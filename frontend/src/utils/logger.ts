export type Logger = {
  info: (message: string, ...args: unknown[]) => void;
  warn: (message: string, ...args: unknown[]) => void;
  error: (message: string, ...args: unknown[]) => void;
  debug: (message: string, ...args: unknown[]) => void;
};

const formatMessage = (namespace: string, message: string) => `[${namespace}] ${message}`;

const createLogger = (namespace = 'FlowstateFrontend'): Logger => ({
  info: (message, ...args) => console.info(formatMessage(namespace, message), ...args),
  warn: (message, ...args) => console.warn(formatMessage(namespace, message), ...args),
  error: (message, ...args) => console.error(formatMessage(namespace, message), ...args),
  debug: (message, ...args) => console.debug(formatMessage(namespace, message), ...args),
});

const logger = createLogger();

export default logger;
export { createLogger };
