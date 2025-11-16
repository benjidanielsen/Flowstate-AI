import { Request, Response, NextFunction } from 'express';
import { v4 as uuidv4 } from 'uuid';
import { safeLogger } from '../utils/piiRedaction';

declare global {
  namespace Express {
    interface Request {
      correlationId?: string;
    }
  }
}

/**
 * Middleware to generate and attach a correlation ID to each request.
 * This ID can be used for end-to-end tracing across services.
 */
export function correlationIdMiddleware(req: Request, res: Response, next: NextFunction): void {
  const correlationId = req.headers['x-correlation-id'] as string || uuidv4();
  req.correlationId = correlationId;
  res.setHeader('X-Correlation-ID', correlationId);

  // Enhance logger to include correlationId in every log message for this request
  const originalInfo = safeLogger.info;
  const originalWarn = safeLogger.warn;
  const originalError = safeLogger.error;
  const originalDebug = safeLogger.debug;

  const mergeMeta = (meta?: unknown) => {
    if (meta && typeof meta === 'object' && !Array.isArray(meta)) {
      return { correlationId, ...(meta as Record<string, unknown>) };
    }
    if (meta === undefined) {
      return { correlationId };
    }
    return { correlationId, detail: meta };
  };

  safeLogger.info = (message: string, meta?: unknown) => {
    originalInfo(message, mergeMeta(meta));
  };
  safeLogger.warn = (message: string, meta?: unknown) => {
    originalWarn(message, mergeMeta(meta));
  };
  safeLogger.error = (message: string, meta?: unknown) => {
    originalError(message, mergeMeta(meta));
  };
  safeLogger.debug = (message: string, meta?: unknown) => {
    originalDebug(message, mergeMeta(meta));
  };

  // Reset logger functions after the request is processed
  res.on('finish', () => {
    safeLogger.info = originalInfo;
    safeLogger.warn = originalWarn;
    safeLogger.error = originalError;
    safeLogger.debug = originalDebug;
  });

  next();
}

