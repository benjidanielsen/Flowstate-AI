import Redis from 'ioredis';
import logger from '../utils/logger';

export interface CacheOptions {
  ttlSeconds?: number;
}

class CacheClient {
  private static instance: CacheClient;

  private readonly client: Redis;

  private readonly defaultTtl = 60;

  private constructor() {
    const redisUrl = process.env.REDIS_CACHE_URL || process.env.REDIS_URL || 'redis://localhost:6379';
    this.client = new Redis(redisUrl, {
      lazyConnect: true,
      maxRetriesPerRequest: 2,
      retryStrategy: (times: number) => Math.min(times * 50, 2000),
    });

    this.client.on('error', (err) => {
      logger.error('Redis cache error', err);
    });

    this.client.on('connect', () => {
      logger.info('Connected to Redis cache');
    });
  }

  static getInstance(): CacheClient {
    if (!CacheClient.instance) {
      CacheClient.instance = new CacheClient();
    }

    return CacheClient.instance;
  }

  async get<T>(key: string): Promise<T | null> {
    try {
      const value = await this.client.get(key);
      if (!value) {
        return null;
      }

      return JSON.parse(value) as T;
    } catch (error: any) {
      logger.warn(`Failed to read cache key ${key}: ${error.message}`);
      return null;
    }
  }

  async set<T>(key: string, value: T, options: CacheOptions = {}): Promise<void> {
    const ttl = options.ttlSeconds ?? this.defaultTtl;
    try {
      await this.client.set(key, JSON.stringify(value), 'EX', ttl);
    } catch (error: any) {
      logger.warn(`Failed to set cache key ${key}: ${error.message}`);
    }
  }

  async invalidate(pattern: string): Promise<void> {
    try {
      const keys = await this.client.keys(pattern);
      if (keys.length > 0) {
        await this.client.del(keys);
      }
    } catch (error: any) {
      logger.warn(`Failed to invalidate cache for pattern ${pattern}: ${error.message}`);
    }
  }
}

export default CacheClient;
