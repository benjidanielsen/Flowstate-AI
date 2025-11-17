import logger from './logger';

/**
 * safeLogger wraps the shared logger that already applies PII redaction.
 * Re-exporting it here maintains compatibility with existing imports.
 */
export const safeLogger = logger;

export default safeLogger;
