"use strict";
/**
 * Session Management Utility
 * Handles Redis-based session storage and management
 */
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.sessionManager = exports.SessionManager = void 0;
const ioredis_1 = __importDefault(require("ioredis"));
const logger_1 = __importDefault(require("./logger"));
class SessionManager {
    constructor(redisUrl) {
        this.SESSION_PREFIX = 'session:';
        this.SESSION_TTL = 7 * 24 * 60 * 60; // 7 days in seconds
        this.ACTIVITY_UPDATE_INTERVAL = 5 * 60; // 5 minutes
        this.redis = new ioredis_1.default(redisUrl || process.env.REDIS_URL || 'redis://localhost:6379', {
            retryStrategy: (times) => {
                const delay = Math.min(times * 50, 2000);
                return delay;
            },
            maxRetriesPerRequest: 3,
            enableReadyCheck: true,
            lazyConnect: false,
        });
        this.redis.on('error', (err) => {
            logger_1.default.error("Redis Session Manager Error:", err);
        });
        this.redis.on('connect', () => {
            logger_1.default.info("Session Manager connected to Redis");
        });
    }
    /**
     * Create a new session
     */
    async createSession(sessionId, data) {
        const sessionData = {
            ...data,
            createdAt: Date.now(),
            lastActivity: Date.now(),
        };
        const key = this.getSessionKey(sessionId);
        await this.redis.setex(key, this.SESSION_TTL, JSON.stringify(sessionData));
    }
    /**
     * Get session data
     */
    async getSession(sessionId) {
        const key = this.getSessionKey(sessionId);
        const data = await this.redis.get(key);
        if (!data) {
            return null;
        }
        const sessionData = JSON.parse(data);
        // Update last activity if enough time has passed
        const timeSinceLastActivity = Date.now() - sessionData.lastActivity;
        if (timeSinceLastActivity > this.ACTIVITY_UPDATE_INTERVAL * 1000) {
            await this.updateActivity(sessionId);
            sessionData.lastActivity = Date.now();
        }
        return sessionData;
    }
    /**
     * Update session data
     */
    async updateSession(sessionId, updates) {
        const existing = await this.getSession(sessionId);
        if (!existing) {
            throw new Error('Session not found');
        }
        const updated = {
            ...existing,
            ...updates,
            lastActivity: Date.now(),
        };
        const key = this.getSessionKey(sessionId);
        await this.redis.setex(key, this.SESSION_TTL, JSON.stringify(updated));
    }
    /**
     * Update last activity timestamp
     */
    async updateActivity(sessionId) {
        const existing = await this.getSession(sessionId);
        if (existing) {
            existing.lastActivity = Date.now();
            const key = this.getSessionKey(sessionId);
            await this.redis.setex(key, this.SESSION_TTL, JSON.stringify(existing));
        }
    }
    /**
     * Delete a session
     */
    async deleteSession(sessionId) {
        const key = this.getSessionKey(sessionId);
        await this.redis.del(key);
    }
    /**
     * Get all sessions for a user
     */
    async getUserSessions(userId) {
        const pattern = `${this.SESSION_PREFIX}*`;
        const keys = await this.redis.keys(pattern);
        const sessions = [];
        for (const key of keys) {
            const data = await this.redis.get(key);
            if (data) {
                const sessionData = JSON.parse(data);
                if (sessionData.userId === userId) {
                    sessions.push({
                        sessionId: key.replace(this.SESSION_PREFIX, ''),
                        data: sessionData,
                    });
                }
            }
        }
        return sessions;
    }
    /**
     * Delete all sessions for a user
     */
    async deleteUserSessions(userId) {
        const sessions = await this.getUserSessions(userId);
        const keys = sessions.map(s => this.getSessionKey(s.sessionId));
        if (keys.length === 0) {
            return 0;
        }
        return await this.redis.del(...keys);
    }
    /**
     * Check if a session exists and is valid
     */
    async isSessionValid(sessionId) {
        const session = await this.getSession(sessionId);
        return session !== null;
    }
    /**
     * Get session TTL in seconds
     */
    async getSessionTTL(sessionId) {
        const key = this.getSessionKey(sessionId);
        return await this.redis.ttl(key);
    }
    /**
     * Refresh session TTL
     */
    async refreshSession(sessionId) {
        const key = this.getSessionKey(sessionId);
        await this.redis.expire(key, this.SESSION_TTL);
    }
    /**
     * Get active session count
     */
    async getActiveSessionCount() {
        const pattern = `${this.SESSION_PREFIX}*`;
        const keys = await this.redis.keys(pattern);
        return keys.length;
    }
    /**
     * Cleanup expired sessions (Redis handles this automatically, but this can be used for manual cleanup)
     */
    async cleanupExpiredSessions() {
        const pattern = `${this.SESSION_PREFIX}*`;
        const keys = await this.redis.keys(pattern);
        let deletedCount = 0;
        for (const key of keys) {
            const ttl = await this.redis.ttl(key);
            if (ttl === -2) {
                // Key doesn't exist
                deletedCount++;
            }
        }
        return deletedCount;
    }
    /**
     * Close Redis connection
     */
    async close() {
        await this.redis.quit();
    }
    /**
     * Get the full Redis key for a session
     */
    getSessionKey(sessionId) {
        return `${this.SESSION_PREFIX}${sessionId}`;
    }
}
exports.SessionManager = SessionManager;
// Export singleton instance
exports.sessionManager = new SessionManager();
//# sourceMappingURL=sessionManager.js.map