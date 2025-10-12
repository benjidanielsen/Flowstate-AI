import winston from 'winston';

// Function to redact PII from log messages
const redactPII = winston.format((info) => {
  const message = info.message as string;
  // Simple regex for common PII patterns (email, phone numbers, basic IDs)
  // This is a basic example and should be expanded for production use
  info.message = message
    .replace(/\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b/g, '[REDACTED_EMAIL]')
    .replace(/\b\d{3}[-.]?\d{3}[-.]?\d{4}\b/g, '[REDACTED_PHONE]')
    .replace(/\b(user_id|customer_id|agent_id):\s*\S+/gi, '$1: [REDACTED_ID]');
  return info;
});

const logger = winston.createLogger({
  level: process.env.NODE_ENV === 'production' ? 'info' : 'debug',
  format: winston.format.combine(
    redactPII(), // Apply PII redaction
    winston.format.colorize(),
    winston.format.timestamp(),
    winston.format.printf(({ timestamp, level, message }) => {
      return `[${timestamp}] ${level}: ${message}`;
    })
  ),
  transports: [
    new winston.transports.Console(),
    new winston.transports.File({ filename: 'error.log', level: 'error' }),
    new winston.transports.File({ filename: 'combined.log' }),
  ],
});

// Data retention policies (e.g., log rotation, archival, deletion) should be implemented in a production environment.
// Consider using dedicated log management solutions (e.g., ELK stack, Splunk) or a log rotation library like 'winston-daily-rotate-file' for Node.js.
// Ensure sensitive logs are retained only for necessary periods and then purged according to compliance requirements.

export default logger;

