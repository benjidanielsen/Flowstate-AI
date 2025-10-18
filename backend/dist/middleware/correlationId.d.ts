import { Request, Response, NextFunction } from 'express';
import { Logger } from 'winston';
declare global {
    namespace Express {
        interface Request {
            correlationId?: string;
            logger?: Logger;
        }
    }
}
/**
 * Middleware to generate and attach a correlation ID to each request.
 * This ID can be used for end-to-end tracing across services.
 * It also creates a child logger with the correlation ID for request-specific logging.
 */
export declare function correlationIdMiddleware(req: Request, res: Response, next: NextFunction): void;
//# sourceMappingURL=correlationId.d.ts.map