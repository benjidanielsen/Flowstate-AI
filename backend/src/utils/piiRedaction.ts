import logger from './logger';

type LogMeta = Record<string, unknown> | undefined;

const redactMeta = (meta?: unknown): LogMeta => {
  if (!meta || typeof meta !== 'object' || Array.isArray(meta)) {
    return meta as LogMeta;
  }

  const clone: Record<string, unknown> = { ...(meta as Record<string, unknown>) };

  if ('password' in clone) {
    clone.password = '[REDACTED]';
  }
  if ('token' in clone) {
    clone.token = '[REDACTED]';
  }
  if ('authorization' in clone) {
    clone.authorization = '[REDACTED]';
  }
  return clone;
};

export const safeLogger = {
  info: (message: string, meta?: unknown) => logger.info(message, redactMeta(meta)),
  warn: (message: string, meta?: unknown) => logger.warn(message, redactMeta(meta)),
  error: (message: string, meta?: unknown) => logger.error(message, redactMeta(meta)),
  debug: (message: string, meta?: unknown) => logger.debug(message, redactMeta(meta)),
};

export default safeLogger;
