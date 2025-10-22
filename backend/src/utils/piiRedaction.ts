import logger from './logger';

type LogMethod = (message: string, meta?: unknown) => void;

type SafeLogger = {
  info: LogMethod;
  warn: LogMethod;
  error: LogMethod;
  debug: LogMethod;
};

const createForwarder = (level: 'info' | 'warn' | 'error' | 'debug'): LogMethod => {
  return (message: string, meta?: unknown) => {
    if (typeof meta !== 'undefined') {
      (logger as any)[level](message, meta);
    } else {
      (logger as any)[level](message);
    }
  };
};

export const safeLogger: SafeLogger = {
  info: createForwarder('info'),
  warn: createForwarder('warn'),
  error: createForwarder('error'),
  debug: createForwarder('debug'),
};

export default safeLogger;
