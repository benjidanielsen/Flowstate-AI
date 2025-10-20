import client from 'prom-client';

const register = new client.Registry();

register.setDefaultLabels({
  service: process.env.OTEL_SERVICE_NAME || 'flowstate-ai-backend',
});

client.collectDefaultMetrics({ register });

export const httpRequestDuration = new client.Histogram({
  name: 'http_request_duration_seconds',
  help: 'Duration of HTTP requests in seconds',
  labelNames: ['method', 'route', 'status_code'],
  buckets: [0.005, 0.01, 0.05, 0.1, 0.25, 0.5, 1, 2, 5],
  registers: [register],
});

export const httpRequestActive = new client.Gauge({
  name: 'http_requests_active',
  help: 'Number of active HTTP requests',
  labelNames: ['method', 'route'],
  registers: [register],
});

export const httpRequestErrors = new client.Counter({
  name: 'http_requests_errors_total',
  help: 'Total number of failed HTTP requests',
  labelNames: ['method', 'route', 'status_code'],
  registers: [register],
});

export const metricsRegister = register;
