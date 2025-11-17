import winston from 'winston';

// eslint-disable-next-line @typescript-eslint/no-var-requires
const LokiTransport = require('winston-loki');

const serviceName = process.env.OTEL_SERVICE_NAME || 'flowstate-ai-backend';
const environment = process.env.NODE_ENV || 'development';

const redactPII = winston.format((info) => {
  const message = typeof info.message === 'string' ? info.message : JSON.stringify(info.message);
  info.message = message
    .replace(/\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b/g, '[REDACTED_EMAIL]')
    .replace(/\b\d{3}[-.]?\d{3}[-.]?\d{4}\b/g, '[REDACTED_PHONE]')
    .replace(/\b(?:customer|user|agent|deal)_id\s*[:=]\s*[^,\s]+/gi, '[REDACTED_ID]');
  return info;
});

const transports: winston.transport[] = [
  new winston.transports.Console({
    handleExceptions: true,
  }),
];

if (process.env.LOKI_URL) {
  transports.push(new LokiTransport({
    host: process.env.LOKI_URL,
    labels: { service: serviceName, environment },
    json: true,
    batching: true,
    timeout: 2000,
  }));
}

const safeLogger = winston.createLogger({
  level: process.env.LOG_LEVEL || (environment === 'production' ? 'info' : 'debug'),
  defaultMeta: { service: serviceName, environment },
  format: winston.format.combine(
    redactPII(),
    winston.format.timestamp(),
    winston.format.errors({ stack: true }),
    winston.format.json(),
  ),
  transports,
});

export { safeLogger };
export default safeLogger;
