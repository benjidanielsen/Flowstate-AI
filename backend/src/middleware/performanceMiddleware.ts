import { Request, Response, NextFunction } from 'express';
import { httpRequestDurationHistogram, requestCounter } from '../utils/metrics';
import { safeLogger } from '../utils/piiRedaction';
import { tracer } from '../utils/tracer';

const performanceMiddleware = (req: Request, res: Response, next: NextFunction) => {
  const start = process.hrtime.bigint();
  const span = tracer.startSpan('http_request', {
    attributes: {
      'http.method': req.method,
      'http.route': req.route?.path || req.originalUrl,
    },
  });
  let spanEnded = false;

  res.on('finish', () => {
    const end = process.hrtime.bigint();
    const durationMs = Number(end - start) / 1_000_000;
    const routeLabel = req.route?.path || req.originalUrl;
    const labels = { method: req.method, route: routeLabel, status_code: res.statusCode.toString() };
    requestCounter.inc(labels);
    httpRequestDurationHistogram.observe(labels, durationMs / 1000);
    span.setAttribute('http.status_code', res.statusCode);
    span.setAttribute('http.duration_ms', durationMs);
    span.end();
    spanEnded = true;
    safeLogger.info(`Request to ${routeLabel} took ${durationMs.toFixed(2)} ms`, { statusCode: res.statusCode });
  });

  res.on('close', () => {
    if (!spanEnded) {
      span.end();
    }
  });

  next();
};

export default performanceMiddleware;

