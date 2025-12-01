import { Request, Response, NextFunction } from 'express';
import { OutgoingHttpHeaders } from 'http';
import { safeLogger } from '../utils/piiRedaction';

const IDEMPOTENCY_KEY_PREFIX = 'idempotency:';
const IDEMPOTENCY_KEY_TTL = 60 * 60; // 1 hour

type CachedResponse = {
  statusCode: number;
  headers: Record<string, number | string | string[]>;
  body: any;
  expiresAt: number;
};

// Lightweight in-memory cache to avoid redis dependency in test environments
const idempotencyCache = new Map<string, CachedResponse>();

const getCachedResponse = (key: string): CachedResponse | undefined => {
  const cached = idempotencyCache.get(key);
  if (!cached) return undefined;
  if (cached.expiresAt < Date.now()) {
    idempotencyCache.delete(key);
    return undefined;
  }
  return cached;
};

const setCachedResponse = (key: string, response: CachedResponse) => {
  idempotencyCache.set(key, response);
};

const sanitizeHeaders = (headers: OutgoingHttpHeaders): Record<string, string | number | string[]> => {
  return Object.entries(headers).reduce<Record<string, string | number | string[]>>((acc, [key, value]) => {
    if (value !== undefined) {
      acc[key] = value as string | number | string[];
    }
    return acc;
  }, {});
};

/**
 * Middleware to ensure idempotency for API requests.
 * Prevents duplicate processing of requests with the same idempotency key.
 */
export async function idempotencyMiddleware(req: Request, res: Response, next: NextFunction): Promise<void> {
  const idempotencyKey = req.headers['x-idempotency-key'] as string;

  if (!idempotencyKey) {
    return next(); // No idempotency key provided, proceed as normal
  }

  const cacheKey = IDEMPOTENCY_KEY_PREFIX + idempotencyKey;

  try {
    const cachedResponse = getCachedResponse(cacheKey);

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
        headers: sanitizeHeaders(res.getHeaders()),
        body: body,
        expiresAt: Date.now() + IDEMPOTENCY_KEY_TTL * 1000,
      };
      try {
        setCachedResponse(cacheKey, responseToCache);
      } catch (err) {
        safeLogger.error(`Idempotency: Failed to cache response for key ${idempotencyKey}`, err as Error);
      }
      return originalSend.apply(res, [body]);
    };

    next();

  } catch (error) {
    safeLogger.error(`Idempotency: Error processing key ${idempotencyKey}`, error);
    next(error); // Continue to error handler
  }
}

