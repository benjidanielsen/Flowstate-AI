import crypto from 'crypto';
import CacheClient from './cacheClient';
import { SearchResult } from '../services/vectorSearchService';

const VECTOR_CACHE_PREFIX = 'vector-search:';
const DEFAULT_TTL = parseInt(process.env.VECTOR_CACHE_TTL || '120', 10);

const cacheClient = CacheClient.getInstance();

function createKey(parts: Record<string, unknown>): string {
  const serialized = JSON.stringify(parts, Object.keys(parts).sort());
  const hash = crypto.createHash('sha256').update(serialized).digest('hex');
  return `${VECTOR_CACHE_PREFIX}${hash}`;
}

export async function getCachedResults(keyParts: Record<string, unknown>): Promise<SearchResult[] | null> {
  const key = createKey(keyParts);
  return cacheClient.get<SearchResult[]>(key);
}

export async function setCachedResults(
  keyParts: Record<string, unknown>,
  results: SearchResult[],
  ttlSeconds: number = DEFAULT_TTL
): Promise<void> {
  const key = createKey(keyParts);
  await cacheClient.set(key, results, { ttlSeconds });
}

export async function invalidateVectorCache(): Promise<void> {
  await cacheClient.invalidate(`${VECTOR_CACHE_PREFIX}*`);
}
