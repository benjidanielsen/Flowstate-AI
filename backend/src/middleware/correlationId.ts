import { Request, Response, NextFunction } from 'express';
import { v4 as uuidv4 } from 'uuid';
import { safeLogger } from '../utils/piiRedaction';
import { correlationContext } from '../utils/correlationContext';

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
  const correlationId = (req.headers['x-correlation-id'] as string) || uuidv4();
  req.correlationId = correlationId;
  res.setHeader('X-Correlation-ID', correlationId);

  correlationContext.runWithCorrelation(correlationId, () => {
    safeLogger.debug('Correlation ID assigned to request', {
      path: req.path,
      method: req.method,
    });
    next();
  });
}

