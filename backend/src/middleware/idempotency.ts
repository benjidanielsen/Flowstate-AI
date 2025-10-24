import { Request, Response, NextFunction } from 'express';
import { safeLogger } from '../utils/piiRedaction';
import { cacheManager } from '../utils/cacheManager';

const IDEMPOTENCY_KEY_PREFIX = 'idempotency:';
const IDEMPOTENCY_KEY_TTL = 60 * 60; // 1 hour

/**
 * Middleware to ensure idempotency for API requests.
 * Prevents duplicate processing of requests with the same idempotency key.
 */
export async function idempotencyMiddleware(req: Request, res: Response, next: NextFunction): Promise<void> {
  const idempotencyKey = req.headers['x-idempotency-key'] as string;

  if (!idempotencyKey) {
    return next(); // No idempotency key provided, proceed as normal
  }

  const cacheNamespace = { prefix: IDEMPOTENCY_KEY_PREFIX };

  try {
    const cachedResponse = await cacheManager.get<{
      statusCode: number;
      headers: Record<string, unknown>;
      body: unknown;
    }>(idempotencyKey, cacheNamespace);

    if (cachedResponse) {
      safeLogger.info(`Idempotency: Returning cached response for key: ${idempotencyKey}`);
      const { statusCode, headers, body } = cachedResponse;
      res.status(statusCode).set(headers).send(body);
      return;
    }

    // Store original send method to cache response before sending
    const originalSend = res.send;
    res.send = (body?: any) => {
      const responseToCache = {
        statusCode: res.statusCode,
        headers: res.getHeaders(),
        body: body,
      };
      cacheManager.set(idempotencyKey, responseToCache, { ...cacheNamespace, ttl: IDEMPOTENCY_KEY_TTL })
        .catch((err: unknown) => safeLogger.error(`Idempotency: Failed to cache response for key ${idempotencyKey}`, err));
      return originalSend.apply(res, [body]);
    };

    next();

  } catch (error) {
    safeLogger.error(`Idempotency: Error processing key ${idempotencyKey}`, error);
    next(error); // Continue to error handler
  }
}

