import { Request, Response, NextFunction } from 'express';
/**
 * Middleware to ensure idempotency for API requests.
 * Prevents duplicate processing of requests with the same idempotency key.
 */
export declare function idempotencyMiddleware(req: Request, res: Response, next: NextFunction): Promise<void>;
//# sourceMappingURL=idempotency.d.ts.map