import { Request, Response, NextFunction } from 'express';
import { v4 as uuidv4 } from 'uuid';
import { safeLogger } from '../utils/piiRedaction';
import { Logger } from 'winston';

declare global {
  namespace Express {
    interface Request {
      correlationId?: string;
      logger?: Logger; // Add a logger property to the Request object
    }
  }
}

/**
 * Middleware to generate and attach a correlation ID to each request.
 * This ID can be used for end-to-end tracing across services.
 * It also creates a child logger with the correlation ID for request-specific logging.
 */
export function correlationIdMiddleware(req: Request, res: Response, next: NextFunction): void {
  const correlationId = req.headers["x-correlation-id"] as string || uuidv4();
  req.correlationId = correlationId;
  res.setHeader("X-Correlation-ID", correlationId);

  // Create a child logger with the correlationId as default metadata
  req.logger = safeLogger.child({ correlationId });

  next();
}

