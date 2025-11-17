import logger from './logger';

type LogFn = (message: string, meta?: unknown) => void;

const EMAIL_REGEX = /\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b/g;
const PHONE_REGEX = /\b\d{3}[-.]?\d{3}[-.]?\d{4}\b/g;
const GENERIC_ID_REGEX = /\b(user_id|customer_id|agent_id):\s*\S+/gi;

function redactString(input: string): string {
  return input
    .replace(EMAIL_REGEX, '[REDACTED_EMAIL]')
    .replace(PHONE_REGEX, '[REDACTED_PHONE]')
    .replace(GENERIC_ID_REGEX, '$1: [REDACTED_ID]');
}

function sanitizeValue(value: unknown): unknown {
  if (typeof value === 'string') {
    return redactString(value);
  }
  if (value instanceof Date) {
    return value.toISOString();
  }
  if (Array.isArray(value)) {
    return value.map(sanitizeValue);
  }
  if (value && typeof value === 'object') {
    return Object.entries(value as Record<string, unknown>).reduce<Record<string, unknown>>((acc, [key, entry]) => {
      acc[key] = sanitizeValue(entry);
      return acc;
    }, {});
  }
  return value;
}

function buildLog(level: 'info' | 'warn' | 'error' | 'debug'): LogFn {
  return (message: string, meta?: unknown) => {
    const safeMessage = redactString(message);
    const safeMeta = sanitizeValue(meta);

    if (typeof safeMeta !== 'undefined') {
      logger.log(level, safeMessage as string, safeMeta);
    } else {
      logger.log(level, safeMessage as string);
    }
  };
}

export type SafeLogger = {
  info: LogFn;
  warn: LogFn;
  error: LogFn;
  debug: LogFn;
};

export const safeLogger: SafeLogger = {
  info: buildLog('info'),
  warn: buildLog('warn'),
  error: buildLog('error'),
  debug: buildLog('debug'),
};

export const redactSensitive = sanitizeValue;

