import logger from './logger';

type LogLevel = 'info' | 'warn' | 'error' | 'debug';

const redact = (input: string): string => {
  return input
    .replace(/\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b/g, '[REDACTED_EMAIL]')
    .replace(/\b\+?\d{1,2}[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b/g, '[REDACTED_PHONE]')
    .replace(/\b(customer|user|agent)_?id\b/gi, '$1_id');
};

const serializeMeta = (meta?: unknown): Record<string, unknown> | undefined => {
  if (!meta) {
    return undefined;
  }
  try {
    const asString = typeof meta === 'string' ? meta : JSON.stringify(meta);
    return { metadata: JSON.parse(redact(asString)) };
  } catch {
    return { metadata: redact(String(meta)) };
  }
};

function log(level: LogLevel, message: string, meta?: unknown) {
  const payload = serializeMeta(meta);
  if (payload) {
    (logger as any)[level](message, payload);
  } else {
    (logger as any)[level](message);
  }
}

export const safeLogger = {
  info: (message: string, meta?: unknown) => log('info', message, meta),
  warn: (message: string, meta?: unknown) => log('warn', message, meta),
  error: (message: string, meta?: unknown) => log('error', message, meta),
  debug: (message: string, meta?: unknown) => log('debug', message, meta),
};

export default safeLogger;
