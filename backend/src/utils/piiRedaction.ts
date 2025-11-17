import logger from './logger';

type LogLevel = 'info' | 'warn' | 'error' | 'debug';

type LogMetadata = Record<string, unknown> | undefined;

const SENSITIVE_KEYS = new Set([
  'password',
  'token',
  'authorization',
  'email',
  'phone',
  'customer_id',
  'user_id',
  'stack',
  'details',
]);

function sanitizeValue(value: unknown): unknown {
  if (value == null) {
    return value;
  }

  if (typeof value === 'string') {
    if (value.length === 0) return value;
    return value
      .replace(/\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b/g, '[REDACTED_EMAIL]')
      .replace(/\b\+?\d[\d\s().-]{7,}\b/g, '[REDACTED_PHONE]')
      .replace(/Bearer\s+[A-Za-z0-9._-]+/gi, 'Bearer [REDACTED_TOKEN]');
  }

  if (Array.isArray(value)) {
    return value.map(item => sanitizeValue(item));
  }

  if (typeof value === 'object') {
    const sanitized: Record<string, unknown> = {};
    for (const [key, val] of Object.entries(value as Record<string, unknown>)) {
      sanitized[key] = SENSITIVE_KEYS.has(key.toLowerCase()) ? '[REDACTED]' : sanitizeValue(val);
    }
    return sanitized;
  }

  return value;
}

function normalizeMeta(meta?: unknown): LogMetadata {
  if (meta == null) return undefined;

  if (meta instanceof Error) {
    const { name, message, stack } = meta;
    return sanitizeValue({ name, message, stack }) as Record<string, unknown>;
  }

  if (typeof meta === 'string' || typeof meta === 'number' || typeof meta === 'boolean') {
    return sanitizeValue({ detail: meta }) as Record<string, unknown>;
  }

  if (typeof meta === 'object') {
    return sanitizeValue(meta) as Record<string, unknown>;
  }

  return sanitizeValue({ detail: meta }) as Record<string, unknown>;
}

function log(level: LogLevel, message: string, meta?: unknown) {
  const safeMeta = normalizeMeta(meta);
  logger[level](message, safeMeta);
}

export const safeLogger = {
  info: (message: string, meta?: unknown) => log('info', message, meta),
  warn: (message: string, meta?: unknown) => log('warn', message, meta),
  error: (message: string, meta?: unknown) => log('error', message, meta),
  debug: (message: string, meta?: unknown) => log('debug', message, meta),
};

export default safeLogger;
