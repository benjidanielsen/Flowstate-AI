import { PoolClient } from 'pg';
import { v4 as uuidv4 } from 'uuid';
import DatabaseManager from '../database';
import logger from '../utils/logger';

export interface AnalyticsEventInput {
  eventName: string;
  eventType: string;
  customerId?: string;
  accountId?: string;
  userId?: string;
  source?: string;
  payload?: Record<string, any> | null;
  metadata?: Record<string, any> | null;
  occurredAt?: Date | string;
  correlationId?: string;
  recommendationId?: string;
}

export interface RecommendationLogInput {
  recommendationId: string;
  agentName?: string;
  customerId?: string;
  accountId?: string;
  recommendationType?: string;
  priority?: number;
  score?: number;
  context?: Record<string, any> | null;
  metadata?: Record<string, any> | null;
  generatedAt?: Date | string;
  accepted?: boolean;
  outcome?: string;
  feedback?: Record<string, any> | null;
}

class AnalyticsIngestionService {
  async recordEvent(input: AnalyticsEventInput) {
    const pool = DatabaseManager.getInstance().getPool();
    let client: PoolClient | null = null;

    try {
      client = await pool.connect();
      const eventId = uuidv4();
      const occurredAt = input.occurredAt ? new Date(input.occurredAt) : new Date();

      const result = await client.query(
        `INSERT INTO analytics_events (
          id, event_name, event_type, customer_id, account_id, user_id,
          source, payload, metadata, occurred_at, correlation_id, recommendation_id
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
        RETURNING *`,
        [
          eventId,
          input.eventName,
          input.eventType,
          input.customerId ?? null,
          input.accountId ?? null,
          input.userId ?? null,
          input.source ?? null,
          input.payload ?? null,
          input.metadata ?? null,
          occurredAt.toISOString(),
          input.correlationId ?? null,
          input.recommendationId ?? null,
        ]
      );

      logger.debug(`Recorded analytics event ${input.eventType} (${eventId})`);
      return result.rows[0];
    } finally {
      if (client) client.release();
    }
  }

  async recordRecommendation(input: RecommendationLogInput) {
    const pool = DatabaseManager.getInstance().getPool();
    let client: PoolClient | null = null;

    try {
      client = await pool.connect();
      const id = uuidv4();
      const generatedAt = input.generatedAt ? new Date(input.generatedAt) : new Date();

      const result = await client.query(
        `INSERT INTO recommendation_logs (
          id, recommendation_id, agent_name, customer_id, account_id,
          recommendation_type, priority, score, context, metadata,
          generated_at, accepted, outcome, feedback
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14)
        RETURNING *`,
        [
          id,
          input.recommendationId,
          input.agentName ?? null,
          input.customerId ?? null,
          input.accountId ?? null,
          input.recommendationType ?? null,
          input.priority ?? null,
          input.score ?? null,
          input.context ?? null,
          input.metadata ?? null,
          generatedAt.toISOString(),
          input.accepted ?? false,
          input.outcome ?? null,
          input.feedback ?? null,
        ]
      );

      logger.debug(`Recorded recommendation ${input.recommendationId}`);
      return result.rows[0];
    } finally {
      if (client) client.release();
    }
  }

  async getRecentEvents(limit = 25, filters: { customerId?: string; eventType?: string } = {}) {
    const pool = DatabaseManager.getInstance().getPool();
    let client: PoolClient | null = null;

    try {
      client = await pool.connect();
      const conditions: string[] = [];
      const values: any[] = [];

      if (filters.customerId) {
        values.push(filters.customerId);
        conditions.push(`customer_id = $${values.length}`);
      }

      if (filters.eventType) {
        values.push(filters.eventType);
        conditions.push(`event_type = $${values.length}`);
      }

      values.push(limit);
      const whereClause = conditions.length > 0 ? `WHERE ${conditions.join(' AND ')}` : '';
      const query = `SELECT * FROM analytics_events ${whereClause} ORDER BY occurred_at DESC LIMIT $${values.length}`;

      const result = await client.query(query, values);
      return result.rows;
    } finally {
      if (client) client.release();
    }
  }

  async getSummary() {
    const pool = DatabaseManager.getInstance().getPool();
    let client: PoolClient | null = null;

    try {
      client = await pool.connect();

      const [eventsByType, eventTrend, recByAgent, recTopTypes, recScores, pipelineByStatus] = await Promise.all([
        client.query(`
          SELECT event_type, COUNT(*) AS count
          FROM analytics_events
          WHERE occurred_at >= NOW() - INTERVAL '30 days'
          GROUP BY event_type
          ORDER BY count DESC
        `),
        client.query(`
          SELECT date_trunc('day', occurred_at) AS bucket, COUNT(*) AS count
          FROM analytics_events
          WHERE occurred_at >= NOW() - INTERVAL '14 days'
          GROUP BY bucket
          ORDER BY bucket ASC
        `),
        client.query(`
          SELECT agent_name, COUNT(*) AS count
          FROM recommendation_logs
          WHERE generated_at >= NOW() - INTERVAL '30 days'
          GROUP BY agent_name
          ORDER BY count DESC
        `),
        client.query(`
          SELECT recommendation_type, COUNT(*) AS count, AVG(priority) AS avg_priority
          FROM recommendation_logs
          WHERE generated_at >= NOW() - INTERVAL '30 days'
          GROUP BY recommendation_type
          ORDER BY count DESC
          LIMIT 10
        `),
        client.query(`
          SELECT agent_name, AVG(score) AS avg_score
          FROM recommendation_logs
          WHERE score IS NOT NULL
          GROUP BY agent_name
        `),
        client.query(`
          SELECT status, COUNT(*) AS count
          FROM customers
          GROUP BY status
        `),
      ]);

      const totalEvents = eventsByType.rows.reduce((acc, row) => acc + Number(row.count), 0);
      const totalRecs = recByAgent.rows.reduce((acc, row) => acc + Number(row.count), 0);

      return {
        events: {
          total: totalEvents,
          byType: eventsByType.rows.map((row) => ({
            eventType: row.event_type,
            count: Number(row.count),
          })),
          trend: eventTrend.rows.map((row) => ({
            date: (row.bucket as Date).toISOString(),
            count: Number(row.count),
          })),
        },
        recommendations: {
          total: totalRecs,
          byAgent: recByAgent.rows.map((row) => ({
            agentName: row.agent_name ?? 'unknown',
            count: Number(row.count),
          })),
          topTypes: recTopTypes.rows.map((row) => ({
            recommendationType: row.recommendation_type ?? 'unspecified',
            count: Number(row.count),
            averagePriority: row.avg_priority ? Number(row.avg_priority) : null,
          })),
          averageScoreByAgent: recScores.rows.map((row) => ({
            agentName: row.agent_name ?? 'unknown',
            averageScore: row.avg_score ? Number(row.avg_score) : null,
          })),
        },
        pipeline: {
          byStatus: pipelineByStatus.rows.map((row) => ({
            status: row.status ?? 'Unknown',
            count: Number(row.count),
          })),
        },
      };
    } finally {
      if (client) client.release();
    }
  }
}

export default new AnalyticsIngestionService();
