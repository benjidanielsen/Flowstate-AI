"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const winston_1 = __importDefault(require("winston"));
// Function to redact PII from log messages
const redactPII = winston_1.default.format((info) => {
    const message = info.message;
    // Simple regex for common PII patterns (email, phone numbers, basic IDs)
    // This is a basic example and should be expanded for production use
    info.message = message
        .replace(/\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b/g, '[REDACTED_EMAIL]')
        .replace(/\b\d{3}[-.]?\d{3}[-.]?\d{4}\b/g, '[REDACTED_PHONE]')
        .replace(/\b(user_id|customer_id|agent_id):\s*\S+/gi, '$1: [REDACTED_ID]');
    return info;
});
const logger = winston_1.default.createLogger({
    level: process.env.NODE_ENV === 'production' ? 'info' : 'debug',
    format: winston_1.default.format.combine(redactPII(), // Apply PII redaction
    winston_1.default.format.colorize(), winston_1.default.format.timestamp(), winston_1.default.format.printf(({ timestamp, level, message }) => {
        return `[${timestamp}] ${level}: ${message}`;
    })),
    transports: [
        new winston_1.default.transports.Console(),
        new winston_1.default.transports.File({ filename: 'error.log', level: 'error' }),
        new winston_1.default.transports.File({ filename: 'combined.log' }),
    ],
});
// Data retention policies (e.g., log rotation, archival, deletion) should be implemented in a production environment.
// Consider using dedicated log management solutions (e.g., ELK stack, Splunk) or a log rotation library like 'winston-daily-rotate-file' for Node.js.
// Ensure sensitive logs are retained only for necessary periods and then purged according to compliance requirements.
exports.default = logger;
//# sourceMappingURL=logger.js.map