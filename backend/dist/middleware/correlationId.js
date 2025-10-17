"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.correlationIdMiddleware = correlationIdMiddleware;
const uuid_1 = require("uuid");
const piiRedaction_1 = require("../utils/piiRedaction");
/**
 * Middleware to generate and attach a correlation ID to each request.
 * This ID can be used for end-to-end tracing across services.
 */
function correlationIdMiddleware(req, res, next) {
    const correlationId = req.headers['x-correlation-id'] || (0, uuid_1.v4)();
    req.correlationId = correlationId;
    res.setHeader('X-Correlation-ID', correlationId);
    // Enhance logger to include correlationId in every log message for this request
    const originalInfo = piiRedaction_1.safeLogger.info;
    const originalWarn = piiRedaction_1.safeLogger.warn;
    const originalError = piiRedaction_1.safeLogger.error;
    const originalDebug = piiRedaction_1.safeLogger.debug;
    piiRedaction_1.safeLogger.info = (message, meta) => {
        originalInfo(message, { correlationId, ...meta });
    };
    piiRedaction_1.safeLogger.warn = (message, meta) => {
        originalWarn(message, { correlationId, ...meta });
    };
    piiRedaction_1.safeLogger.error = (message, meta) => {
        originalError(message, { correlationId, ...meta });
    };
    piiRedaction_1.safeLogger.debug = (message, meta) => {
        originalDebug(message, { correlationId, ...meta });
    };
    // Reset logger functions after the request is processed
    res.on('finish', () => {
        piiRedaction_1.safeLogger.info = originalInfo;
        piiRedaction_1.safeLogger.warn = originalWarn;
        piiRedaction_1.safeLogger.error = originalError;
        piiRedaction_1.safeLogger.debug = originalDebug;
    });
    next();
}
//# sourceMappingURL=correlationId.js.map