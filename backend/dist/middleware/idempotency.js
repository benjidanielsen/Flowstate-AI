"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.idempotencyMiddleware = idempotencyMiddleware;
const cacheManager_1 = require("../utils/cacheManager");
const piiRedaction_1 = require("../utils/piiRedaction");
const IDEMPOTENCY_KEY_HEADER = 'X-Idempotency-Key';
const IDEMPOTENCY_EXPIRATION_SECONDS = 60 * 60; // 1 hour
async function idempotencyMiddleware(req, res, next) {
    if (req.method !== 'POST' && req.method !== 'PUT' && req.method !== 'PATCH') {
        return next();
    }
    const idempotencyKey = req.headers[IDEMPOTENCY_KEY_HEADER.toLowerCase()];
    if (!idempotencyKey) {
        return next();
    }
    const cacheKey = `idempotency:${idempotencyKey}`;
    try {
        const cachedResponse = await cacheManager_1.cacheManager.get(cacheKey);
        if (cachedResponse) {
            piiRedaction_1.safeLogger.info(`Idempotent request for key ${idempotencyKey} served from cache.`);
            res.status(cachedResponse.status).set(cachedResponse.headers).json(cachedResponse.body);
            return;
        }
        // Store original send/json methods
        const originalJson = res.json;
        const originalSend = res.send;
        const originalStatus = res.status;
        let responseBody;
        let responseStatus;
        const responseHeaders = {};
        // Intercept response data
        res.json = (body) => {
            responseBody = body;
            return originalJson.call(res, body);
        };
        res.send = (body) => {
            responseBody = body;
            return originalSend.call(res, body);
        };
        res.status = (status) => {
            responseStatus = status;
            return originalStatus.call(res, status);
        };
        // Intercept headers
        const originalSetHeader = res.setHeader;
        res.setHeader = (name, value) => {
            responseHeaders[name.toLowerCase()] = value.toString();
            return originalSetHeader.call(res, name, value);
        };
        res.on('finish', async () => {
            if (responseStatus && responseBody) {
                const responseToCache = {
                    status: responseStatus,
                    headers: responseHeaders,
                    body: responseBody,
                };
                await cacheManager_1.cacheManager.set(cacheKey, responseToCache, { ttl: IDEMPOTENCY_EXPIRATION_SECONDS })
                    .catch((err) => piiRedaction_1.safeLogger.error(`Idempotency: Failed to cache response for key ${idempotencyKey}`, err));
            }
        });
        next();
    }
    catch (error) {
        piiRedaction_1.safeLogger.error(`Idempotency middleware error for key ${idempotencyKey}:`, error);
        next(error); // Pass error to next middleware
    }
}
//# sourceMappingURL=idempotency.js.map