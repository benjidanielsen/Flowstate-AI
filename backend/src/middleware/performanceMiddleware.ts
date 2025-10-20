import { Request, Response, NextFunction } from 'express';
import logger from '../utils/logger';
import { httpRequestActive, httpRequestDuration, httpRequestErrors } from '../utils/metrics';

const performanceMiddleware = (req: Request, res: Response, next: NextFunction) => {
  const start = process.hrtime.bigint();
  const route = req.route?.path || req.baseUrl || req.path;
  const method = req.method;
  httpRequestActive.inc({ method, route });
  const stopTimer = httpRequestDuration.startTimer({ method, route });

  res.on('finish', () => {
    const end = process.hrtime.bigint();
    const duration = Number(end - start) / 1_000_000; // convert to milliseconds
    const statusCode = res.statusCode.toString();
    stopTimer({ status_code: statusCode });
    httpRequestActive.dec({ method, route });

    if (res.statusCode >= 500) {
      httpRequestErrors.inc({ method, route, status_code: statusCode });
    }

    logger.info(`Request to ${req.originalUrl} took ${duration.toFixed(2)} ms`, {
      statusCode,
      method,
      route,
    });
  });

  next();
};

export default performanceMiddleware;

