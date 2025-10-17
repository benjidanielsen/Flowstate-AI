/**
 * Cache Management Utility
 * Handles Redis-based caching with TTL and invalidation
 */
export interface CacheOptions {
    ttl?: number;
    prefix?: string;
}
export declare class CacheManager {
    private redis;
    private readonly DEFAULT_TTL;
    private readonly DEFAULT_PREFIX;
    constructor(redisUrl?: string);
    /**
     * Get a value from cache
     */
    get<T>(key: string, options?: CacheOptions): Promise<T | null>;
    /**
     * Set a value in cache
     */
    set<T>(key: string, value: T, options?: CacheOptions): Promise<void>;
    /**
     * Delete a value from cache
     */
    del(key: string, options?: CacheOptions): Promise<void>;
    /**
     * Check if a key exists in cache
     */
    exists(key: string, options?: CacheOptions): Promise<boolean>;
    /**
     * Get or set pattern: get from cache, or compute and cache if missing
     */
    getOrSet<T>(key: string, factory: () => Promise<T>, options?: CacheOptions): Promise<T>;
    /**
     * Invalidate all cache keys matching a pattern
     */
    invalidatePattern(pattern: string, options?: CacheOptions): Promise<number>;
    /**
     * Invalidate all cache with a specific prefix
     */
    invalidatePrefix(prefix: string): Promise<number>;
    /**
     * Get TTL for a key
     */
    getTTL(key: string, options?: CacheOptions): Promise<number>;
    /**
     * Refresh TTL for a key
     */
    refreshTTL(key: string, options?: CacheOptions): Promise<void>;
    /**
     * Increment a counter in cache
     */
    increment(key: string, options?: CacheOptions): Promise<number>;
    /**
     * Decrement a counter in cache
     */
    decrement(key: string, options?: CacheOptions): Promise<number>;
    /**
     * Set multiple values at once
     */
    mset(entries: Array<{
        key: string;
        value: any;
    }>, options?: CacheOptions): Promise<void>;
    /**
     * Get multiple values at once
     */
    mget<T>(keys: string[], options?: CacheOptions): Promise<Array<T | null>>;
    /**
     * Get cache statistics
     */
    getStats(prefix?: string): Promise<{
        keyCount: number;
        memoryUsed: string;
        hitRate?: number;
    }>;
    /**
     * Clear all cache
     */
    clear(): Promise<void>;
    /**
     * Close Redis connection
     */
    close(): Promise<void>;
    /**
     * Get the full Redis key
     */
    private getFullKey;
}
export declare const cacheManager: CacheManager;
//# sourceMappingURL=cacheManager.d.ts.map