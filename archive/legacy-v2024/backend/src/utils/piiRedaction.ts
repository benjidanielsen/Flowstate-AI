import winston from 'winston';

// Custom format for PII redaction
const piiRedactionFormat = winston.format((info) => {
  // Implement your PII redaction logic here
  // For example, redact email addresses, phone numbers, etc.
  // For now, we'll just pass it through
  return info;
});

// Create a logger instance
const safeLogger = winston.createLogger({
  level: process.env.LOG_LEVEL || 'info',
  format: winston.format.combine(
    piiRedactionFormat(),
    winston.format.timestamp(),
    winston.format.json()
  ),
  transports: [
    new winston.transports.Console({
      format: winston.format.combine(
        winston.format.colorize(),
        winston.format.simple()
      )
    }),
  ],
});

export { safeLogger };

