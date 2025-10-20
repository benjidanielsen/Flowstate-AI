import { PoolClient } from 'pg';
import { createHash } from 'crypto';
import DatabaseManager from '../database';
import logger from '../utils/logger';
import { FeatureFlag } from '../types';

interface EvaluationContext {
  accountId?: string;
  userId?: string;
  customerId?: string;
  fallbackId?: string;
}

interface UpsertOptions {
  description?: string;
  rolloutPhase?: string;
  enabled?: boolean;
  rolloutPercentage?: number;
  metadata?: Record<string, any> | null;
}

class FeatureFlagService {
  private static instance: FeatureFlagService;
  private cache: Map<string, { flag: FeatureFlag; fetchedAt: number }> = new Map();
  private cacheTtlMs = 60_000; // 60 seconds

  static getInstance(): FeatureFlagService {
    if (!FeatureFlagService.instance) {
      FeatureFlagService.instance = new FeatureFlagService();
    }
    return FeatureFlagService.instance;
  }

  async listFlags(): Promise<FeatureFlag[]> {
    const pool = DatabaseManager.getInstance().getPool();
    let client: PoolClient | null = null;

    try {
      client = await pool.connect();
      const result = await client.query('SELECT * FROM feature_flags ORDER BY key ASC');
      return result.rows.map(this.mapRowToFlag);
    } finally {
      if (client) client.release();
    }
  }

  async getFlag(key: string): Promise<FeatureFlag | null> {
    const cached = this.cache.get(key);
    if (cached && Date.now() - cached.fetchedAt < this.cacheTtlMs) {
      return cached.flag;
    }

    const pool = DatabaseManager.getInstance().getPool();
    let client: PoolClient | null = null;

    try {
      client = await pool.connect();
      const result = await client.query('SELECT * FROM feature_flags WHERE key = $1', [key]);
      if (result.rows.length === 0) {
        return null;
      }

      const flag = this.mapRowToFlag(result.rows[0]);
      this.cache.set(key, { flag, fetchedAt: Date.now() });
      return flag;
    } finally {
      if (client) client.release();
    }
  }

  async upsertFlag(key: string, options: UpsertOptions): Promise<FeatureFlag> {
    const pool = DatabaseManager.getInstance().getPool();
    let client: PoolClient | null = null;

    try {
      client = await pool.connect();
      const result = await client.query(
        `INSERT INTO feature_flags (key, description, rollout_phase, enabled, rollout_percentage, metadata, updated_at)
         VALUES ($1, $2, $3, $4, $5, $6, CURRENT_TIMESTAMP)
         ON CONFLICT (key) DO UPDATE SET
           description = EXCLUDED.description,
           rollout_phase = EXCLUDED.rollout_phase,
           enabled = EXCLUDED.enabled,
           rollout_percentage = EXCLUDED.rollout_percentage,
           metadata = EXCLUDED.metadata,
           updated_at = CURRENT_TIMESTAMP
         RETURNING *`,
        [
          key,
          options.description ?? null,
          options.rolloutPhase ?? null,
          options.enabled ?? false,
          options.rolloutPercentage ?? 0,
          options.metadata ?? null,
        ]
      );

      const flag = this.mapRowToFlag(result.rows[0]);
      this.cache.set(key, { flag, fetchedAt: Date.now() });
      logger.info(`Feature flag ${key} updated (enabled=${flag.enabled}, rollout=${flag.rollout_percentage ?? 0}%)`);
      return flag;
    } finally {
      if (client) client.release();
    }
  }

  async shouldServe(key: string, context: EvaluationContext = {}): Promise<boolean> {
    const flag = await this.getFlag(key);
    if (!flag) {
      logger.debug(`Feature flag ${key} not found; defaulting to disabled.`);
      return false;
    }

    if (!flag.enabled) {
      return false;
    }

    const rolloutPercentage = flag.rollout_percentage ?? 100;
    if (rolloutPercentage >= 100) {
      return true;
    }

    if (rolloutPercentage <= 0) {
      return false;
    }

    const identifier = context.accountId || context.userId || context.customerId || context.fallbackId;
    if (!identifier) {
      // Without an identifier we can't deterministically roll out partially.
      return false;
    }

    const hash = createHash('sha256')
      .update(`${key}:${identifier}`)
      .digest('hex')
      .slice(0, 8);
    const numeric = parseInt(hash, 16) % 100;
    return numeric < rolloutPercentage;
  }

  async getActiveFlags(): Promise<Record<string, FeatureFlag>> {
    const flags = await this.listFlags();
    return flags
      .filter((flag) => flag.enabled)
      .reduce((acc, flag) => {
        acc[flag.key] = flag;
        return acc;
      }, {} as Record<string, FeatureFlag>);
  }

  private mapRowToFlag(row: any): FeatureFlag {
    return {
      key: row.key,
      description: row.description ?? undefined,
      rollout_phase: row.rollout_phase ?? undefined,
      enabled: row.enabled,
      rollout_percentage: row.rollout_percentage ?? undefined,
      metadata: row.metadata ?? undefined,
      created_at: row.created_at,
      updated_at: row.updated_at,
    };
  }
}

export default FeatureFlagService.getInstance();
