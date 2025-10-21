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
  private redis: Redis;
  private readonly DEFAULT_TTL = 3600; // 1 hour
  private readonly DEFAULT_PREFIX = 'cache:';

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
      logger.error("Redis Cache Manager Error:", err);
    });

    this.redis.on('connect', () => {
      logger.info('Cache Manager connected to Redis');
    });
  }

  /**
   * Get a value from cache
   */
  async get<T>(key: string, options?: CacheOptions): Promise<T | null> {
    const fullKey = this.getFullKey(key, options?.prefix);
    const value = await this.redis.get(fullKey);

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

    await this.redis.setex(fullKey, ttl, serialized);
  }

  /**
   * Delete a value from cache
   */
  async del(key: string, options?: CacheOptions): Promise<void> {
    const fullKey = this.getFullKey(key, options?.prefix);
    await this.redis.del(fullKey);
  }

  /**
   * Check if a key exists in cache
   */
  async exists(key: string, options?: CacheOptions): Promise<boolean> {
    const fullKey = this.getFullKey(key, options?.prefix);
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
    const keys = await this.redis.keys(pattern);

    if (keys.length === 0) {
      return 0;
    }

    return await this.redis.del(...keys);
  }

  /**
   * Get TTL for a key
   */
  async getTTL(key: string, options?: CacheOptions): Promise<number> {
    const fullKey = this.getFullKey(key, options?.prefix);
    return await this.redis.ttl(fullKey);
  }

  /**
   * Refresh TTL for a key
   */
  async refreshTTL(key: string, options?: CacheOptions): Promise<void> {
    const fullKey = this.getFullKey(key, options?.prefix);
    const ttl = options?.ttl || this.DEFAULT_TTL;
    await this.redis.expire(fullKey, ttl);
  }

  /**
   * Increment a counter in cache
   */
  async increment(key: string, options?: CacheOptions): Promise<number> {
    const fullKey = this.getFullKey(key, options?.prefix);
    const value = await this.redis.incr(fullKey);

    // Set TTL if this is a new key
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
    return await this.redis.decr(fullKey);
  }

  /**
   * Set multiple values at once
   */
  async mset(entries: Array<{ key: string; value: any }>, options?: CacheOptions): Promise<void> {
    const pipeline = this.redis.pipeline();
    const ttl = options?.ttl || this.DEFAULT_TTL;

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
    const pattern = `${prefix || this.DEFAULT_PREFIX}*`;
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
    await this.redis.flushdb();
  }

  /**
   * Close Redis connection
   */
  async close(): Promise<void> {
    await this.redis.quit();
  }

  /**
   * Get the full Redis key
   */
  private getFullKey(key: string, prefix?: string): string {
    const p = prefix || this.DEFAULT_PREFIX;
    return `${p}${key}`;
  }
}

class InMemoryCacheManager {
  private readonly store = new Map<string, { value: string; expiresAt: number | null }>();
  private readonly DEFAULT_TTL = 3600; // 1 hour
  private readonly DEFAULT_PREFIX = 'cache:';

  private buildKey(key: string, prefix?: string): string {
    return `${prefix ?? this.DEFAULT_PREFIX}${key}`;
  }

  private purgeIfExpired(fullKey: string) {
    const entry = this.store.get(fullKey);
    if (entry && entry.expiresAt !== null && entry.expiresAt <= Date.now()) {
      this.store.delete(fullKey);
    }
  }

  async get<T>(key: string, options?: CacheOptions): Promise<T | null> {
    const fullKey = this.buildKey(key, options?.prefix);
    this.purgeIfExpired(fullKey);
    const entry = this.store.get(fullKey);
    if (!entry) {
      return null;
    }

    try {
      return JSON.parse(entry.value) as T;
    } catch (error) {
      logger.error('In-memory cache parse error:', error);
      this.store.delete(fullKey);
      return null;
    }
  }

  async set<T>(key: string, value: T, options?: CacheOptions): Promise<void> {
    const fullKey = this.buildKey(key, options?.prefix);
    const ttlSeconds = options?.ttl ?? this.DEFAULT_TTL;
    const expiresAt = ttlSeconds > 0 ? Date.now() + ttlSeconds * 1000 : null;
    this.store.set(fullKey, { value: JSON.stringify(value), expiresAt });
  }

  async del(key: string, options?: CacheOptions): Promise<void> {
    const fullKey = this.buildKey(key, options?.prefix);
    this.store.delete(fullKey);
  }

  async exists(key: string, options?: CacheOptions): Promise<boolean> {
    const fullKey = this.buildKey(key, options?.prefix);
    this.purgeIfExpired(fullKey);
    return this.store.has(fullKey);
  }

  async getOrSet<T>(key: string, factory: () => Promise<T>, options?: CacheOptions): Promise<T> {
    const cached = await this.get<T>(key, options);
    if (cached !== null) {
      return cached;
    }

    const value = await factory();
    await this.set(key, value, options);
    return value;
  }

  async invalidatePattern(pattern: string, options?: CacheOptions): Promise<number> {
    const prefix = options?.prefix ?? this.DEFAULT_PREFIX;
    const regex = new RegExp(`^${prefix}${pattern.replace(/[*]/g, '.*')}$`);
    let removed = 0;
    for (const key of [...this.store.keys()]) {
      if (regex.test(key)) {
        this.store.delete(key);
        removed += 1;
      }
    }
    return removed;
  }

  async invalidatePrefix(prefix: string): Promise<number> {
    const regex = new RegExp(`^${prefix}`);
    let removed = 0;
    for (const key of [...this.store.keys()]) {
      if (regex.test(key)) {
        this.store.delete(key);
        removed += 1;
      }
    }
    return removed;
  }

  async getTTL(key: string, options?: CacheOptions): Promise<number> {
    const fullKey = this.buildKey(key, options?.prefix);
    this.purgeIfExpired(fullKey);
    const entry = this.store.get(fullKey);
    if (!entry || entry.expiresAt === null) {
      return -1;
    }
    return Math.max(0, Math.floor((entry.expiresAt - Date.now()) / 1000));
  }

  async refreshTTL(key: string, options?: CacheOptions): Promise<void> {
    const fullKey = this.buildKey(key, options?.prefix);
    const entry = this.store.get(fullKey);
    if (!entry) {
      return;
    }
    const ttlSeconds = options?.ttl ?? this.DEFAULT_TTL;
    entry.expiresAt = ttlSeconds > 0 ? Date.now() + ttlSeconds * 1000 : null;
    this.store.set(fullKey, entry);
  }

  async increment(key: string, options?: CacheOptions): Promise<number> {
    const current = await this.get<number>(key, options);
    const next = (current ?? 0) + 1;
    await this.set(key, next, options);
    return next;
  }

  async decrement(key: string, options?: CacheOptions): Promise<number> {
    const current = await this.get<number>(key, options);
    const next = (current ?? 0) - 1;
    await this.set(key, next, options);
    return next;
  }

  async mset(entries: Array<{ key: string; value: any }>, options?: CacheOptions): Promise<void> {
    await Promise.all(entries.map(entry => this.set(entry.key, entry.value, options)));
  }

  async mget<T>(keys: string[], options?: CacheOptions): Promise<Array<T | null>> {
    return Promise.all(keys.map(key => this.get<T>(key, options)));
  }

  async getStats(prefix?: string): Promise<{ keyCount: number; memoryUsed: string }> {
    const regex = prefix ? new RegExp(`^${prefix}`) : null;
    const keys = regex ? [...this.store.keys()].filter(key => regex.test(key)) : this.store.keys();
    const keyCount = regex ? [...keys].length : this.store.size;
    return { keyCount, memoryUsed: 'in-memory' };
  }

  async clear(): Promise<void> {
    this.store.clear();
  }

  async close(): Promise<void> {
    this.store.clear();
  }
}

// Export singleton instance
const redisUrl = process.env.REDIS_URL;
export const cacheManager = redisUrl ? new CacheManager(redisUrl) : new InMemoryCacheManager();

if (!redisUrl) {
  logger.warn('Redis URL not configured; using in-memory cache fallback.');
}

