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

export class CacheManager {
  private redis: Redis | null = null;
  private readonly DEFAULT_TTL = 3600; // 1 hour
  private readonly DEFAULT_PREFIX = 'cache:';
  private readonly useInMemory: boolean;
  private readonly memoryStore = new Map<string, { value: string; expiresAt?: number }>();

  constructor(redisUrl?: string) {
    this.useInMemory = process.env.NODE_ENV === 'test' || process.env.USE_IN_MEMORY_CACHE === 'true';

    if (!this.useInMemory) {
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
        logger.error("Redis Cache Manager Error:", err);
      });

      this.redis.on('connect', () => {
        logger.info('Cache Manager connected to Redis');
      });
    } else {
      logger.info('Cache Manager using in-memory fallback store');
    }
  }

  private ensureRedis(): Redis {
    if (!this.redis) {
      throw new Error('Redis client not initialized');
    }
    return this.redis;
  }

  private getMemoryEntry(fullKey: string) {
    const entry = this.memoryStore.get(fullKey);
    if (!entry) {
      return null;
    }
    if (entry.expiresAt && entry.expiresAt <= Date.now()) {
      this.memoryStore.delete(fullKey);
      return null;
    }
    return entry;
  }

  private getMemoryValue(fullKey: string): string | null {
    const entry = this.getMemoryEntry(fullKey);
    return entry ? entry.value : null;
  }

  private setMemoryValue(fullKey: string, value: string, ttl?: number) {
    const expiresAt = ttl ? Date.now() + ttl * 1000 : undefined;
    this.memoryStore.set(fullKey, { value, expiresAt });
  }

  private patternToRegex(pattern: string): RegExp {
    const escaped = pattern.replace(/[-[\]/{}()*+?.\\^$|]/g, '\\$&').replace(/\*/g, '.*');
    return new RegExp(`^${escaped}$`);
  }

  /**
   * Get a value from cache
   */
  async get<T>(key: string, options?: CacheOptions): Promise<T | null> {
    const fullKey = this.getFullKey(key, options?.prefix);
    const value = this.useInMemory ? this.getMemoryValue(fullKey) : await this.ensureRedis().get(fullKey);

    if (!value) {
      return null;
    }

    try {
      return JSON.parse(value) as T;
    } catch (error) {
      logger.error("Cache parse error:", error);
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

    if (this.useInMemory) {
      this.setMemoryValue(fullKey, serialized, ttl);
      return;
    }

    await this.ensureRedis().setex(fullKey, ttl, serialized);
  }

  /**
   * Delete a value from cache
   */
  async del(key: string, options?: CacheOptions): Promise<void> {
    const fullKey = this.getFullKey(key, options?.prefix);
    if (this.useInMemory) {
      this.memoryStore.delete(fullKey);
      return;
    }
    await this.ensureRedis().del(fullKey);
  }

  /**
   * Check if a key exists in cache
   */
  async exists(key: string, options?: CacheOptions): Promise<boolean> {
    const fullKey = this.getFullKey(key, options?.prefix);
    if (this.useInMemory) {
      return this.getMemoryEntry(fullKey) !== null;
    }
    const result = await this.ensureRedis().exists(fullKey);
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
    if (this.useInMemory) {
      const regex = this.patternToRegex(fullPattern);
      let removed = 0;
      for (const key of Array.from(this.memoryStore.keys())) {
        if (regex.test(key)) {
          this.memoryStore.delete(key);
          removed++;
        }
      }
      return removed;
    }

    const redis = this.ensureRedis();
    const keys = await redis.keys(fullPattern);

    if (keys.length === 0) {
      return 0;
    }

    return await redis.del(...keys);
  }

  /**
   * Invalidate all cache with a specific prefix
   */
  async invalidatePrefix(prefix: string): Promise<number> {
    const pattern = `${prefix}*`;
    if (this.useInMemory) {
      const regex = this.patternToRegex(pattern);
      let removed = 0;
      for (const key of Array.from(this.memoryStore.keys())) {
        if (regex.test(key)) {
          this.memoryStore.delete(key);
          removed++;
        }
      }
      return removed;
    }

    const redis = this.ensureRedis();
    const keys = await redis.keys(pattern);

    if (keys.length === 0) {
      return 0;
    }

    return await redis.del(...keys);
  }

  /**
   * Get TTL for a key
   */
  async getTTL(key: string, options?: CacheOptions): Promise<number> {
    const fullKey = this.getFullKey(key, options?.prefix);
    if (this.useInMemory) {
      const entry = this.getMemoryEntry(fullKey);
      if (!entry || !entry.expiresAt) {
        return -1;
      }
      return Math.max(Math.floor((entry.expiresAt - Date.now()) / 1000), -1);
    }
    return await this.ensureRedis().ttl(fullKey);
  }

  /**
   * Refresh TTL for a key
   */
  async refreshTTL(key: string, options?: CacheOptions): Promise<void> {
    const fullKey = this.getFullKey(key, options?.prefix);
    const ttl = options?.ttl || this.DEFAULT_TTL;
    if (this.useInMemory) {
      const entry = this.getMemoryEntry(fullKey);
      if (entry) {
        entry.expiresAt = Date.now() + ttl * 1000;
        this.memoryStore.set(fullKey, entry);
      }
      return;
    }
    await this.ensureRedis().expire(fullKey, ttl);
  }

  /**
   * Increment a counter in cache
   */
  async increment(key: string, options?: CacheOptions): Promise<number> {
    const fullKey = this.getFullKey(key, options?.prefix);
    if (this.useInMemory) {
      const entry = this.getMemoryEntry(fullKey);
      const current = entry ? Number(JSON.parse(entry.value)) : 0;
      const next = current + 1;
      const expiresAt = entry?.expiresAt ?? (options?.ttl ? Date.now() + options.ttl * 1000 : undefined);
      this.memoryStore.set(fullKey, { value: JSON.stringify(next), expiresAt });
      return next;
    }

    const redis = this.ensureRedis();
    const value = await redis.incr(fullKey);

    if (value === 1 && options?.ttl) {
      await redis.expire(fullKey, options.ttl);
    }

    return value;
  }

  /**
   * Decrement a counter in cache
   */
  async decrement(key: string, options?: CacheOptions): Promise<number> {
    const fullKey = this.getFullKey(key, options?.prefix);
    if (this.useInMemory) {
      const entry = this.getMemoryEntry(fullKey);
      const current = entry ? Number(JSON.parse(entry.value)) : 0;
      const next = current - 1;
      const expiresAt = entry?.expiresAt ?? (options?.ttl ? Date.now() + options.ttl * 1000 : undefined);
      this.memoryStore.set(fullKey, { value: JSON.stringify(next), expiresAt });
      return next;
    }
    return await this.ensureRedis().decr(fullKey);
  }

  /**
   * Set multiple values at once
   */
  async mset(entries: Array<{ key: string; value: any }>, options?: CacheOptions): Promise<void> {
    const ttl = options?.ttl || this.DEFAULT_TTL;

    if (this.useInMemory) {
      for (const entry of entries) {
        const fullKey = this.getFullKey(entry.key, options?.prefix);
        this.setMemoryValue(fullKey, JSON.stringify(entry.value), ttl);
      }
      return;
    }

    const redis = this.ensureRedis();
    const pipeline = redis.pipeline();

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
    if (this.useInMemory) {
      return fullKeys.map((key) => {
        const value = this.getMemoryValue(key);
        if (!value) return null;
        try {
          return JSON.parse(value) as T;
        } catch {
          return null;
        }
      });
    }

    const values = await this.ensureRedis().mget(...fullKeys);

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
    if (this.useInMemory) {
      let count = 0;
      for (const key of Array.from(this.memoryStore.keys())) {
        if (this.getMemoryEntry(key)) {
          count++;
        }
      }
      return {
        keyCount: count,
        memoryUsed: 'in-memory',
      };
    }

    const pattern = `${prefix || this.DEFAULT_PREFIX}*`;
    const redis = this.ensureRedis();
    const keys = await redis.keys(pattern);
    const info = await redis.info('memory');

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
    if (this.useInMemory) {
      this.memoryStore.clear();
      return;
    }
    await this.ensureRedis().flushdb();
  }

  /**
   * Close Redis connection
   */
  async close(): Promise<void> {
    if (this.useInMemory) {
      this.memoryStore.clear();
      return;
    }
    if (this.redis) {
      await this.redis.quit();
      this.redis = null;
    }
  }

  /**
   * Get the full Redis key
   */
  private getFullKey(key: string, prefix?: string): string {
    const p = prefix || this.DEFAULT_PREFIX;
    return `${p}${key}`;
  }
}

// Export singleton instance
export const cacheManager = new CacheManager();

