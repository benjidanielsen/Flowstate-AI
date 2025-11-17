import client from 'prom-client';
import { Request, Response } from 'express';

const register = new client.Registry();
client.collectDefaultMetrics({ register, prefix: 'flowstate_' });

const httpRequestDurationHistogram = new client.Histogram({
  name: 'flowstate_http_request_duration_seconds',
  help: 'HTTP request latency in seconds',
  labelNames: ['method', 'route', 'status_code'],
  buckets: [0.05, 0.1, 0.25, 0.5, 1, 2, 5],
  registers: [register],
});

const requestCounter = new client.Counter({
  name: 'flowstate_http_requests_total',
  help: 'Total HTTP requests processed',
  labelNames: ['method', 'route', 'status_code'],
  registers: [register],
});

const kpiGauge = new client.Gauge({
  name: 'flowstate_kpi_value',
  help: 'Latest KPI values exposed by the KPI router',
  labelNames: ['category', 'name', 'unit'],
  registers: [register],
});

export const metricsHandler = async (_req: Request, res: Response) => {
  res.set('Content-Type', register.contentType);
  res.send(await register.metrics());
};

export { register, httpRequestDurationHistogram, requestCounter, kpiGauge };
