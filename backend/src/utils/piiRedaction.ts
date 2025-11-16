import logger from './logger';

// `logger` already applies basic PII redaction via its formatter. This module
// exposes a `safeLogger` helper so other parts of the application can import a
// consistent sanitized logger without depending directly on the logger
// implementation.
export const safeLogger = logger;

export default safeLogger;
