import { Request, Response, NextFunction } from 'express';
import logger from '../utils/logger';

const performanceMiddleware = (req: Request, res: Response, next: NextFunction) => {
  const start = process.hrtime.bigint();

  res.on('finish', () => {
    const end = process.hrtime.bigint();
    const duration = Number(end - start) / 1_000_000; // convert to milliseconds
    logger.info(`Request to ${req.originalUrl} took ${duration.toFixed(2)} ms`);
  });

  next();
};

export default performanceMiddleware;

