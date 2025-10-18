import { Request, Response, NextFunction } from 'express';
import { v4 as uuidv4 } from 'uuid';
import { cacheManager } from '../utils/cacheManager';
import { safeLogger } from '../utils/piiRedaction';

const IDEMPOTENCY_KEY_HEADER = 'X-Idempotency-Key';
const IDEMPOTENCY_EXPIRATION_SECONDS = 60 * 60; // 1 hour

export async function idempotencyMiddleware(req: Request, res: Response, next: NextFunction): Promise<void> {
  if (req.method !== 'POST' && req.method !== 'PUT' && req.method !== 'PATCH') {
    return next();
  }

  const idempotencyKey = req.headers[IDEMPOTENCY_KEY_HEADER.toLowerCase()] as string;

  if (!idempotencyKey) {
    return next();
  }

  const cacheKey = `idempotency:${idempotencyKey}`;

  try {
    const cachedResponse = await cacheManager.get<{ status: number; headers: Record<string, string>; body: any }>(cacheKey);

    if (cachedResponse) {
      safeLogger.info(`Idempotent request for key ${idempotencyKey} served from cache.`);
      res.status(cachedResponse.status).set(cachedResponse.headers).json(cachedResponse.body);
      return;
    }

    // Store original send/json methods
    const originalJson = res.json;
    const originalSend = res.send;
    const originalStatus = res.status;

    let responseBody: any;
    let responseStatus: number;
    const responseHeaders: Record<string, string> = {};

    // Intercept response data
    res.json = (body: any): Response => {
      responseBody = body;
      return originalJson.call(res, body);
    };

    res.send = (body: any): Response => {
      responseBody = body;
      return originalSend.call(res, body);
    };

    res.status = (status: number): Response => {
      responseStatus = status;
      return originalStatus.call(res, status);
    };

    // Intercept headers
    const originalSetHeader = res.setHeader;
    res.setHeader = (name: string, value: string | number | readonly string[]): Response => {
      responseHeaders[name.toLowerCase()] = value.toString();
      return originalSetHeader.call(res, name, value);
    };

    res.on('finish', async () => {
      if (responseStatus && responseBody) {
        const responseToCache = {
          status: responseStatus,
          headers: responseHeaders,
          body: responseBody,
        };
        await cacheManager.set(cacheKey, responseToCache, { ttl: IDEMPOTENCY_EXPIRATION_SECONDS })
          .catch((err: Error) => safeLogger.error(`Idempotency: Failed to cache response for key ${idempotencyKey}`, err));
      }
    });

    next();
  } catch (error: any) {
    safeLogger.error(`Idempotency middleware error for key ${idempotencyKey}:`, error);
    next(error); // Pass error to next middleware
  }
}

