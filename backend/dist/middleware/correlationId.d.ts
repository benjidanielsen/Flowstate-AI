import { Request, Response, NextFunction } from 'express';
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
export declare function correlationIdMiddleware(req: Request, res: Response, next: NextFunction): void;
//# sourceMappingURL=correlationId.d.ts.map