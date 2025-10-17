"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const logger_1 = __importDefault(require("../utils/logger"));
const performanceMiddleware = (req, res, next) => {
    const start = process.hrtime.bigint();
    res.on('finish', () => {
        const end = process.hrtime.bigint();
        const duration = Number(end - start) / 1000000; // convert to milliseconds
        logger_1.default.info(`Request to ${req.originalUrl} took ${duration.toFixed(2)} ms`);
    });
    next();
};
exports.default = performanceMiddleware;
//# sourceMappingURL=performanceMiddleware.js.map