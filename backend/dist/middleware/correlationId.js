"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.correlationIdMiddleware = correlationIdMiddleware;
const uuid_1 = require("uuid");
const piiRedaction_1 = require("../utils/piiRedaction");
/**
 * Middleware to generate and attach a correlation ID to each request.
 * This ID can be used for end-to-end tracing across services.
 * It also creates a child logger with the correlation ID for request-specific logging.
 */
function correlationIdMiddleware(req, res, next) {
    const correlationId = req.headers["x-correlation-id"] || (0, uuid_1.v4)();
    req.correlationId = correlationId;
    res.setHeader("X-Correlation-ID", correlationId);
    // Create a child logger with the correlationId as default metadata
    req.logger = piiRedaction_1.safeLogger.child({ correlationId });
    next();
}
//# sourceMappingURL=correlationId.js.map