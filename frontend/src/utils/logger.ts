const isDev = typeof import.meta !== 'undefined' ? !!import.meta.env?.DEV : true;
const prefix = '[Flowstate-AI]';

type LogArgs = [message?: any, ...optionalParams: any[]];

type Logger = {
  debug: (...args: LogArgs) => void;
  info: (...args: LogArgs) => void;
  warn: (...args: LogArgs) => void;
  error: (...args: LogArgs) => void;
};

const createLogger = (): Logger => {
  const log = (level: 'debug' | 'info' | 'warn' | 'error', ...args: LogArgs) => {
    if (level === 'debug' && !isDev) return;

    const consoleMethod = console[level] ?? console.log;
    consoleMethod(prefix, ...args);
  };

  return {
    debug: (...args) => log('debug', ...args),
    info: (...args) => log('info', ...args),
    warn: (...args) => log('warn', ...args),
    error: (...args) => log('error', ...args),
  };
};

const logger = createLogger();

export default logger;
