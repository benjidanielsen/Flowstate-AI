/**
 * Cache Management Utility
 * Handles Redis-based caching with TTL and invalidation
 */

import Redis from 'ioredis';
import logger from './logger';

export interface CacheOptions {
  ttl?: number; // Time to live in seconds
  prefix?: string;
}

type MemoryEntry = {
  value: string;
  expiresAt: number | null;
};

export class CacheManager {
  private redis?: Redis;
  private readonly useMemoryStore: boolean;
  private readonly memoryStore: Map<string, MemoryEntry>;
  private readonly DEFAULT_TTL = 3600; // 1 hour
  private readonly DEFAULT_PREFIX = 'cache:';

  constructor(redisUrl?: string) {
    this.useMemoryStore = process.env.NODE_ENV === 'test' || process.env.USE_IN_MEMORY_CACHE === 'true';
    this.memoryStore = new Map<string, MemoryEntry>();

    if (!this.useMemoryStore) {
      this.redis = new Redis(redisUrl || process.env.REDIS_URL || 'redis://localhost:6379', {
        retryStrategy: (times: number) => {
          const delay = Math.min(times * 50, 2000);
          return delay;
        },
        maxRetriesPerRequest: 1,
        enableReadyCheck: false,
        lazyConnect: true,
        enableOfflineQueue: false,
      });

      this.redis.on('error', (err: Error) => {
        logger.error('Redis Cache Manager Error:', err);
      });

      this.redis.on('connect', () => {
        logger.info('Cache Manager connected to Redis');
      });
    } else {
      logger.debug('Cache Manager running in in-memory mode for faster tests.');
    }
  }

  /**
   * Get a value from cache
   */
  async get<T>(key: string, options?: CacheOptions): Promise<T | null> {
    const fullKey = this.getFullKey(key, options?.prefix);

    if (this.useMemoryStore || !this.redis) {
      const entry = this.getMemoryEntry(fullKey);
      if (!entry) {
        return null;
      }

      try {
        return JSON.parse(entry.value) as T;
      } catch (error) {
        logger.error('Cache parse error:', error);
        return null;
      }
    }

    const value = await this.redis.get(fullKey);

    if (!value) {
      return null;
    }

    try {
      return JSON.parse(value) as T;
    } catch (error) {
      logger.error('Cache parse error:', error);
      return null;
    }
  }

  /**
   * Set a value in cache
   */
  async set<T>(key: string, value: T, options?: CacheOptions): Promise<void> {
    const fullKey = this.getFullKey(key, options?.prefix);
    const ttl = options?.ttl || this.DEFAULT_TTL;
    const serialized = JSON.stringify(value);

    if (this.useMemoryStore || !this.redis) {
      this.setMemoryEntry(fullKey, serialized, ttl);
      return;
    }

    await this.redis.setex(fullKey, ttl, serialized);
  }

  /**
   * Delete a value from cache
   */
  async del(key: string, options?: CacheOptions): Promise<void> {
    const fullKey = this.getFullKey(key, options?.prefix);

    if (this.useMemoryStore || !this.redis) {
      this.memoryStore.delete(fullKey);
      return;
    }

    await this.redis.del(fullKey);
  }

  /**
   * Check if a key exists in cache
   */
  async exists(key: string, options?: CacheOptions): Promise<boolean> {
    const fullKey = this.getFullKey(key, options?.prefix);

    if (this.useMemoryStore || !this.redis) {
      return this.getMemoryEntry(fullKey) !== null;
    }

    const result = await this.redis.exists(fullKey);
    return result === 1;
  }

  /**
   * Get or set pattern: get from cache, or compute and cache if missing
   */
  async getOrSet<T>(
    key: string,
    factory: () => Promise<T>,
    options?: CacheOptions
  ): Promise<T> {
    const cached = await this.get<T>(key, options);

    if (cached !== null) {
      return cached;
    }

    const value = await factory();
    await this.set(key, value, options);
    return value;
  }

  /**
   * Invalidate all cache keys matching a pattern
   */
  async invalidatePattern(pattern: string, options?: CacheOptions): Promise<number> {
    const prefix = options?.prefix || this.DEFAULT_PREFIX;
    const fullPattern = `${prefix}${pattern}`;

    if (this.useMemoryStore || !this.redis) {
      const regex = this.patternToRegex(fullPattern);
      let count = 0;
      for (const key of Array.from(this.memoryStore.keys())) {
        if (regex.test(key)) {
          this.memoryStore.delete(key);
          count += 1;
        }
      }
      return count;
    }

    const keys = await this.redis.keys(fullPattern);

    if (keys.length === 0) {
      return 0;
    }

    return await this.redis.del(...keys);
  }

  /**
   * Invalidate all cache with a specific prefix
   */
  async invalidatePrefix(prefix: string): Promise<number> {
    const pattern = `${prefix}*`;
    return this.invalidatePattern(pattern, { prefix: '' });
  }

  /**
   * Get TTL for a key
   */
  async getTTL(key: string, options?: CacheOptions): Promise<number> {
    const fullKey = this.getFullKey(key, options?.prefix);

    if (this.useMemoryStore || !this.redis) {
      const entry = this.getMemoryEntry(fullKey);
      if (!entry || entry.expiresAt === null) {
        return -1;
      }
      const remaining = entry.expiresAt - Date.now();
      return remaining > 0 ? Math.ceil(remaining / 1000) : -2;
    }

    return await this.redis.ttl(fullKey);
  }

  /**
   * Refresh TTL for a key
   */
  async refreshTTL(key: string, options?: CacheOptions): Promise<void> {
    const fullKey = this.getFullKey(key, options?.prefix);
    const ttl = options?.ttl || this.DEFAULT_TTL;

    if (this.useMemoryStore || !this.redis) {
      const entry = this.getMemoryEntry(fullKey);
      if (entry) {
        this.setMemoryEntry(fullKey, entry.value, ttl);
      }
      return;
    }

    await this.redis.expire(fullKey, ttl);
  }

  /**
   * Increment a counter in cache
   */
  async increment(key: string, options?: CacheOptions): Promise<number> {
    const fullKey = this.getFullKey(key, options?.prefix);

    if (this.useMemoryStore || !this.redis) {
      const entry = this.getMemoryEntry(fullKey);
      const current = entry ? parseInt(entry.value, 10) : 0;
      const next = current + 1;
      this.setMemoryEntry(fullKey, JSON.stringify(next), options?.ttl || this.DEFAULT_TTL);
      return next;
    }

    const value = await this.redis.incr(fullKey);

    if (value === 1 && options?.ttl) {
      await this.redis.expire(fullKey, options.ttl);
    }

    return value;
  }

  /**
   * Decrement a counter in cache
   */
  async decrement(key: string, options?: CacheOptions): Promise<number> {
    const fullKey = this.getFullKey(key, options?.prefix);

    if (this.useMemoryStore || !this.redis) {
      const entry = this.getMemoryEntry(fullKey);
      const current = entry ? parseInt(entry.value, 10) : 0;
      const next = current - 1;
      this.setMemoryEntry(fullKey, JSON.stringify(next), options?.ttl || this.DEFAULT_TTL);
      return next;
    }

    return await this.redis.decr(fullKey);
  }

  /**
   * Set multiple values at once
   */
  async mset(entries: Array<{ key: string; value: any }>, options?: CacheOptions): Promise<void> {
    const ttl = options?.ttl || this.DEFAULT_TTL;

    if (this.useMemoryStore || !this.redis) {
      for (const entry of entries) {
        const fullKey = this.getFullKey(entry.key, options?.prefix);
        this.setMemoryEntry(fullKey, JSON.stringify(entry.value), ttl);
      }
      return;
    }

    const pipeline = this.redis.pipeline();

    for (const entry of entries) {
      const fullKey = this.getFullKey(entry.key, options?.prefix);
      const serialized = JSON.stringify(entry.value);
      pipeline.setex(fullKey, ttl, serialized);
    }

    await pipeline.exec();
  }

  /**
   * Get multiple values at once
   */
  async mget<T>(keys: string[], options?: CacheOptions): Promise<Array<T | null>> {
    const fullKeys = keys.map(k => this.getFullKey(k, options?.prefix));

    if (this.useMemoryStore || !this.redis) {
      return fullKeys.map(fullKey => {
        const entry = this.getMemoryEntry(fullKey);
        if (!entry) {
          return null;
        }
        try {
          return JSON.parse(entry.value) as T;
        } catch {
          return null;
        }
      });
    }

    const values = await this.redis.mget(...fullKeys);

    return values.map((v: string | null) => {
      if (!v) return null;
      try {
        return JSON.parse(v) as T;
      } catch {
        return null;
      }
    });
  }

  /**
   * Get cache statistics
   */
  async getStats(prefix?: string): Promise<{
    keyCount: number;
    memoryUsed: string;
    hitRate?: number;
  }> {
    const actualPrefix = prefix || this.DEFAULT_PREFIX;

    if (this.useMemoryStore || !this.redis) {
      const now = Date.now();
      let count = 0;
      for (const [key, entry] of this.memoryStore.entries()) {
        if (!entry.expiresAt || entry.expiresAt > now) {
          if (key.startsWith(actualPrefix)) {
            count += 1;
          }
        } else {
          this.memoryStore.delete(key);
        }
      }
      return {
        keyCount: count,
        memoryUsed: `${(count * 256) / 1024} KB (approx)`,
      };
    }

    const pattern = `${actualPrefix}*`;
    const keys = await this.redis.keys(pattern);
    const info = await this.redis.info('memory');

    const memoryMatch = info.match(/used_memory_human:(.+)/);
    const memoryUsed = memoryMatch ? memoryMatch[1].trim() : 'unknown';

    return {
      keyCount: keys.length,
      memoryUsed,
    };
  }

  /**
   * Clear all cache
   */
  async clear(): Promise<void> {
    if (this.useMemoryStore || !this.redis) {
      this.memoryStore.clear();
      return;
    }

    await this.redis.flushdb();
  }

  /**
   * Close Redis connection
   */
  async close(): Promise<void> {
    if (this.useMemoryStore || !this.redis) {
      this.memoryStore.clear();
      return;
    }

    await this.redis.quit();
  }

  /**
   * Get the full Redis key
   */
  private getFullKey(key: string, prefix?: string): string {
    const p = prefix || this.DEFAULT_PREFIX;
    return `${p}${key}`;
  }

  private getMemoryEntry(fullKey: string): MemoryEntry | null {
    const entry = this.memoryStore.get(fullKey);
    if (!entry) {
      return null;
    }

    if (entry.expiresAt !== null && entry.expiresAt <= Date.now()) {
      this.memoryStore.delete(fullKey);
      return null;
    }

    return entry;
  }

  private setMemoryEntry(fullKey: string, value: string, ttl: number): void {
    const expiresAt = ttl > 0 ? Date.now() + ttl * 1000 : null;
    this.memoryStore.set(fullKey, { value, expiresAt });
  }

  private patternToRegex(pattern: string): RegExp {
    const escaped = pattern.replace(/[.+?^${}()|[\]\\]/g, '\\$&');
    const regexString = `^${escaped.replace(/\\\*/g, '.*')}$`;
    return new RegExp(regexString);
  }
}

// Export singleton instance
export const cacheManager = new CacheManager();

