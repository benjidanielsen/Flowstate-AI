import logger from './logger';

const SENSITIVE_KEYS = ['email', 'phone', 'token', 'password'];

function sanitizeMeta(meta: unknown): Record<string, unknown> {
  if (!meta) {
    return {};
  }

  if (meta instanceof Error) {
    return sanitizeMeta({ message: meta.message, stack: meta.stack });
  }

  if (typeof meta !== 'object') {
    return {};
  }

  const cleanMeta: Record<string, unknown> = {};
  for (const [key, value] of Object.entries(meta as Record<string, unknown>)) {
    if (SENSITIVE_KEYS.includes(key.toLowerCase())) {
      cleanMeta[key] = '[redacted]';
    } else if (typeof value === 'object' && value !== null) {
      cleanMeta[key] = sanitizeMeta(value);
    } else {
      cleanMeta[key] = value;
    }
  }
  return cleanMeta;
}

function logWithSanitization(level: 'info' | 'error' | 'warn' | 'debug', message: string, meta?: unknown) {
  const cleaned = sanitizeMeta(meta);
  logger.log(level, message, cleaned);
}

export const safeLogger = {
  info: (message: string, meta?: unknown) => logWithSanitization('info', message, meta),
  error: (message: string, meta?: unknown) => logWithSanitization('error', message, meta),
  warn: (message: string, meta?: unknown) => logWithSanitization('warn', message, meta),
  debug: (message: string, meta?: unknown) => logWithSanitization('debug', message, meta),
};
