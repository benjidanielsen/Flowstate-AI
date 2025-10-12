/**
 * Session Management Utility
 * Handles Redis-based session storage and management
 */

import Redis from 'ioredis';
import logger from './logger';

export interface SessionData {
  userId: string;
  email: string;
  role: string;
  createdAt: number;
  lastActivity: number;
  metadata?: Record<string, any>;
}

export class SessionManager {
  private redis: Redis;
  private readonly SESSION_PREFIX = 'session:';
  private readonly SESSION_TTL = 7 * 24 * 60 * 60; // 7 days in seconds
  private readonly ACTIVITY_UPDATE_INTERVAL = 5 * 60; // 5 minutes

  constructor(redisUrl?: string) {
    this.redis = new Redis(redisUrl || process.env.REDIS_URL || 'redis://localhost:6379', {
      retryStrategy: (times: number) => {
        const delay = Math.min(times * 50, 2000);
        return delay;
      },
      maxRetriesPerRequest: 3,
      enableReadyCheck: true,
      lazyConnect: false,
    });

    this.redis.on('error', (err: Error) => {
      logger.error("Redis Session Manager Error:", err);
    });

    this.redis.on('connect', () => {
      logger.info("Session Manager connected to Redis");
    });
  }

  /**
   * Create a new session
   */
  async createSession(sessionId: string, data: Omit<SessionData, 'createdAt' | 'lastActivity'>): Promise<void> {
    const sessionData: SessionData = {
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
  async getSession(sessionId: string): Promise<SessionData | null> {
    const key = this.getSessionKey(sessionId);
    const data = await this.redis.get(key);

    if (!data) {
      return null;
    }

    const sessionData: SessionData = JSON.parse(data);

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
  async updateSession(sessionId: string, updates: Partial<SessionData>): Promise<void> {
    const existing = await this.getSession(sessionId);
    if (!existing) {
      throw new Error('Session not found');
    }

    const updated: SessionData = {
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
  async updateActivity(sessionId: string): Promise<void> {
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
  async deleteSession(sessionId: string): Promise<void> {
    const key = this.getSessionKey(sessionId);
    await this.redis.del(key);
  }

  /**
   * Get all sessions for a user
   */
  async getUserSessions(userId: string): Promise<Array<{ sessionId: string; data: SessionData }>> {
    const pattern = `${this.SESSION_PREFIX}*`;
    const keys = await this.redis.keys(pattern);
    const sessions: Array<{ sessionId: string; data: SessionData }> = [];

    for (const key of keys) {
      const data = await this.redis.get(key);
      if (data) {
        const sessionData: SessionData = JSON.parse(data);
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
  async deleteUserSessions(userId: string): Promise<number> {
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
  async isSessionValid(sessionId: string): Promise<boolean> {
    const session = await this.getSession(sessionId);
    return session !== null;
  }

  /**
   * Get session TTL in seconds
   */
  async getSessionTTL(sessionId: string): Promise<number> {
    const key = this.getSessionKey(sessionId);
    return await this.redis.ttl(key);
  }

  /**
   * Refresh session TTL
   */
  async refreshSession(sessionId: string): Promise<void> {
    const key = this.getSessionKey(sessionId);
    await this.redis.expire(key, this.SESSION_TTL);
  }

  /**
   * Get active session count
   */
  async getActiveSessionCount(): Promise<number> {
    const pattern = `${this.SESSION_PREFIX}*`;
    const keys = await this.redis.keys(pattern);
    return keys.length;
  }

  /**
   * Cleanup expired sessions (Redis handles this automatically, but this can be used for manual cleanup)
   */
  async cleanupExpiredSessions(): Promise<number> {
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
  async close(): Promise<void> {
    await this.redis.quit();
  }

  /**
   * Get the full Redis key for a session
   */
  private getSessionKey(sessionId: string): string {
    return `${this.SESSION_PREFIX}${sessionId}`;
  }
}

// Export singleton instance
export const sessionManager = new SessionManager();

