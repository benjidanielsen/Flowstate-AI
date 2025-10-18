import DatabaseManager from '../database';
import { PipelineStatus } from '../types';
import { PoolClient } from 'pg';

interface CacheEntry<T> {
  data: T;
  timestamp: number;
}

export class StatsService {
  private cache: { [key: string]: CacheEntry<any> } = {};
  private cacheDuration = 5 * 60 * 1000; // 5 minutes in milliseconds

  private getCached<T>(key: string): T | null {
    const entry = this.cache[key];
    if (entry && (Date.now() - entry.timestamp < this.cacheDuration)) {
      return entry.data;
    }
    return null;
  }

  private setCache<T>(key: string, data: T): void {
    this.cache[key] = { data, timestamp: Date.now() };
  }

  async countsByStatus(): Promise<Record<string, number>> {
    const cacheKey = 'countsByStatus';
    const cachedData = this.getCached<Record<string, number>>(cacheKey);
    if (cachedData) {
      return cachedData;
    }

    let client: PoolClient | null = null;
    const result: Record<string, number> = {};

    try {
      const pool = DatabaseManager.getInstance().getPool();
      client = await pool.connect();

      const statuses = Object.values(PipelineStatus);
      await Promise.all(statuses.map(async s => {
        const queryResult = await client!.query('SELECT COUNT(*) as count FROM customers WHERE status = $1', [s]);
        result[s] = parseInt(queryResult.rows[0].count, 10) || 0;
      }));

      this.setCache(cacheKey, result);
      return result;
    } finally {
      if (client) {
        client.release();
      }
    }
  }

  private dateRange() {
    const now = new Date();
    const start = new Date();
    start.setHours(0, 0, 0, 0);
    const weekStart = new Date(now);
    weekStart.setDate(now.getDate() - 6);
    weekStart.setHours(0, 0, 0, 0);
    return { todayStart: start, weekStart };
  }

  async dmoCounters() {
    const cacheKey = 'dmoCounters';
    const cachedData = this.getCached<any>(cacheKey);
    if (cachedData) {
      return cachedData;
    }

    let client: PoolClient | null = null;

    try {
      const pool = DatabaseManager.getInstance().getPool();
      client = await pool.connect();

      async function countEvent(name: string, from: Date): Promise<number> {
        const queryResult = await client!.query('SELECT COUNT(*) as count FROM event_logs WHERE event_type = $1 AND timestamp >= $2', [name, from.toISOString()]);
        return parseInt(queryResult.rows[0].count, 10) || 0;
      }

      const [invitesToday, invitesWeek, followToday, followWeek] = await Promise.all([
        countEvent('INVITE_SENT', this.dateRange().todayStart),
        countEvent('INVITE_SENT', this.dateRange().weekStart),
        countEvent('FOLLOW_UP_DONE', this.dateRange().todayStart),
        countEvent('FOLLOW_UP_DONE', this.dateRange().weekStart),
      ]);

      const result = {
        today: { invites: invitesToday, follow_ups: followToday },
        week: { invites: invitesWeek, follow_ups: followWeek },
      };
      this.setCache(cacheKey, result);
      return result;
    } finally {
      if (client) {
        client.release();
      }
    }
  }

  async extraCounts() {
    const cacheKey = 'extraCounts';
    const cachedData = this.getCached<any>(cacheKey);
    if (cachedData) {
      return cachedData;
    }

    let client: PoolClient | null = null;

    try {
      const pool = DatabaseManager.getInstance().getPool();
      client = await pool.connect();

      const nowIso = new Date().toISOString();

      const noShowResult = await client!.query('SELECT COUNT(*) as count FROM event_logs WHERE event_type = $1', ['NO_SHOW']);
      const noShow = parseInt(noShowResult.rows[0].count, 10) || 0;

      const videoSentResult = await client!.query('SELECT COUNT(*) as count FROM event_logs WHERE event_type = $1', ['VIDEO_SENT']);
      const videoSent = parseInt(videoSentResult.rows[0].count, 10) || 0;

      const overdueFollowupsResult = await client!.query('SELECT COUNT(*) as count FROM reminders WHERE completed = FALSE AND scheduled_for < $1', [nowIso]);
      const overdueFollowups = parseInt(overdueFollowupsResult.rows[0].count, 10) || 0;

      const result = { no_show_count: noShow, video_sent_count: videoSent, overdue_followups: overdueFollowups };
      this.setCache(cacheKey, result);
      return result;
    } finally {
      if (client) {
        client.release();
      }
    }
  }

  async getCustomerDemographics(): Promise<{
    byCountry: Record<string, number>;
    byLanguage: Record<string, number>;
    bySource: Record<string, number>;
  }> {
    const cacheKey = 'customerDemographics';
    const cachedData = this.getCached<any>(cacheKey);
    if (cachedData) {
      return cachedData;
    }

    let client: PoolClient | null = null;

    try {
      const pool = DatabaseManager.getInstance().getPool();
      client = await pool.connect();

      const [byCountryResult, byLanguageResult, bySourceResult] = await Promise.all([
        client!.query('SELECT country, COUNT(*) as count FROM customers WHERE country IS NOT NULL GROUP BY country'),
        client!.query('SELECT language, COUNT(*) as count FROM customers WHERE language IS NOT NULL GROUP BY language'),
        client!.query('SELECT source, COUNT(*) as count FROM customers WHERE source IS NOT NULL GROUP BY source'),
      ]);

      const byCountry = byCountryResult.rows.reduce((acc, row) => ({ ...acc, [row.country]: parseInt(row.count, 10) }), {});
      const byLanguage = byLanguageResult.rows.reduce((acc, row) => ({ ...acc, [row.language]: parseInt(row.count, 10) }), {});
      const bySource = bySourceResult.rows.reduce((acc, row) => ({ ...acc, [row.source]: parseInt(row.count, 10) }), {});

      const result = { byCountry, byLanguage, bySource };
      this.setCache(cacheKey, result);
      return result;
    } finally {
      if (client) {
        client.release();
      }
    }
  }

  async getInteractionSummary(): Promise<{
    byType: Record<string, number>;
    totalInteractions: number;
    avgInteractionsPerCustomer: number;
  }> {
    const cacheKey = 'interactionSummary';
    const cachedData = this.getCached<any>(cacheKey);
    if (cachedData) {
      return cachedData;
    }

    let client: PoolClient | null = null;

    try {
      const pool = DatabaseManager.getInstance().getPool();
      client = await pool.connect();

      const [byTypeResult, totalInteractionsResult, totalCustomersResult] = await Promise.all([
        client!.query('SELECT type, COUNT(*) as count FROM interactions GROUP BY type'),
        client!.query('SELECT COUNT(*) as count FROM interactions'),
        client!.query('SELECT COUNT(*) as count FROM customers'),
      ]);

      const byType = byTypeResult.rows.reduce((acc, row) => ({ ...acc, [row.type]: parseInt(row.count, 10) }), {});
      const totalInteractions = parseInt(totalInteractionsResult.rows[0].count, 10);
      const totalCustomers = parseInt(totalCustomersResult.rows[0].count, 10);
      const avgInteractionsPerCustomer = totalCustomers > 0 ? totalInteractions / totalCustomers : 0;

      const result = { byType, totalInteractions, avgInteractionsPerCustomer };
      this.setCache(cacheKey, result);
      return result;
    } finally {
      if (client) {
        client.release();
      }
    }
  }

  async getPipelineConversionRates(): Promise<Record<string, number>> {
    const cacheKey = 'pipelineConversionRates';
    const cachedData = this.getCached<any>(cacheKey);
    if (cachedData) {
      return cachedData;
    }

    let client: PoolClient | null = null;

    try {
      const pool = DatabaseManager.getInstance().getPool();
      client = await pool.connect();

      const pipelineStatuses = Object.values(PipelineStatus);
      const conversionRates: Record<string, number> = {};

      for (let i = 0; i < pipelineStatuses.length - 1; i++) {
        const currentStage = pipelineStatuses[i];
        const nextStage = pipelineStatuses[i + 1];

        const currentStageCountResult = await client!.query('SELECT COUNT(*) as count FROM customers WHERE status = $1', [currentStage]);
        const currentStageCount = parseInt(currentStageCountResult.rows[0].count, 10);

        const nextStageCountResult = await client!.query('SELECT COUNT(*) as count FROM customers WHERE status = $1', [nextStage]);
        const nextStageCount = parseInt(nextStageCountResult.rows[0].count, 10);

        if (currentStageCount > 0) {
          conversionRates[`${currentStage}_to_${nextStage}`] = (nextStageCount / currentStageCount) * 100;
        } else {
          conversionRates[`${currentStage}_to_${nextStage}`] = 0;
        }
      }
      this.setCache(cacheKey, conversionRates);
      return conversionRates;
    } finally {
      if (client) {
        client.release();
      }
    }
  }
}

