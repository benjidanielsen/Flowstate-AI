import { Request, Response, NextFunction } from 'express';
import { v4 as uuidv4 } from 'uuid';
import { safeLogger } from '../utils/piiRedaction';

/* eslint-disable @typescript-eslint/no-namespace */
declare global {
  namespace Express {
    interface Request {
      correlationId?: string;
    }
  }
}
/* eslint-enable @typescript-eslint/no-namespace */

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

  safeLogger.info = (message: string, meta?: unknown) => {
    originalInfo(message, { correlationId, ...meta });
  };
  safeLogger.warn = (message: string, meta?: unknown) => {
    originalWarn(message, { correlationId, ...meta });
  };
  safeLogger.error = (message: string, meta?: unknown) => {
    originalError(message, { correlationId, ...meta });
  };
  safeLogger.debug = (message: string, meta?: unknown) => {
    originalDebug(message, { correlationId, ...meta });
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

