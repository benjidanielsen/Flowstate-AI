import DatabaseManager from '../database';
import { EventLog } from '../types';
import { v4 as uuidv4 } from 'uuid';
import { PoolClient } from 'pg';
import analyticsIngestionService from './analyticsIngestionService';
import featureFlagService from './featureFlagService';
import logger from '../utils/logger';

export class EventLogService {
  async logEvent(eventType: string, eventData: any, customerId?: string, userId?: string): Promise<EventLog> {
    let client: PoolClient | null = null;
    try {
      const pool = DatabaseManager.getInstance().getPool();
      client = await pool.connect();
      const id = uuidv4();
      const timestamp = new Date();

      const result = await client.query(
        `INSERT INTO event_logs (id, customer_id, event_type, event_data, timestamp, user_id)
         VALUES ($1, $2, $3, $4, $5, $6) RETURNING *`,
        [
          id,
          customerId || null,
          eventType,
          eventData,
          timestamp.toISOString(),
          userId || null
        ]
      );
      const inserted = result.rows[0];

      featureFlagService
        .shouldServe('analytics_event_ingestion', {
          accountId: (eventData && (eventData.account_id || eventData.accountId)) || undefined,
          customerId,
          userId,
        })
        .then((enabled) => {
          if (!enabled) {
            return;
          }
          analyticsIngestionService
            .recordEvent({
              eventName: eventType,
              eventType,
              customerId,
              accountId: (eventData && (eventData.account_id || eventData.accountId)) || undefined,
              userId,
              source: eventData?.source,
              payload: eventData || undefined,
              metadata: eventData?.metadata || undefined,
              correlationId: eventData?.correlationId,
            })
            .catch((err) => logger.warn('Failed to mirror event into analytics pipeline', err));
        })
        .catch((err) => logger.warn('Failed to evaluate analytics event feature flag', err));

      return inserted;
    } finally {
      if (client) client.release();
    }
  }

  async getEventsByCustomer(customerId: string, limit: number = 50): Promise<EventLog[]> {
    let client: PoolClient | null = null;
    try {
      const pool = DatabaseManager.getInstance().getPool();
      client = await pool.connect();

      const result = await client.query(
        `SELECT * FROM event_logs 
         WHERE customer_id = $1 
         ORDER BY timestamp DESC 
         LIMIT $2`,
        [customerId, limit]
      );
      return result.rows.map(row => ({
        ...row,
        event_data: row.event_data,
        timestamp: new Date(row.timestamp)
      }));
    } finally {
      if (client) client.release();
    }
  }

  async getAllEvents(limit: number = 100): Promise<EventLog[]> {
    let client: PoolClient | null = null;
    try {
      const pool = DatabaseManager.getInstance().getPool();
      client = await pool.connect();

      const result = await client.query(
        `SELECT * FROM event_logs 
         ORDER BY timestamp DESC 
         LIMIT $1`,
        [limit]
      );
      return result.rows.map(row => ({
        ...row,
        event_data: row.event_data,
        timestamp: new Date(row.timestamp)
      }));
    } finally {
      if (client) client.release();
    }
  }

  async getEventsByType(eventType: string, limit: number = 50): Promise<EventLog[]> {
    let client: PoolClient | null = null;
    try {
      const pool = DatabaseManager.getInstance().getPool();
      client = await pool.connect();

      const result = await client.query(
        `SELECT * FROM event_logs 
         WHERE event_type = $1 
         ORDER BY timestamp DESC 
         LIMIT $2`,
        [eventType, limit]
      );
      return result.rows.map(row => ({
        ...row,
        event_data: row.event_data,
        timestamp: new Date(row.timestamp)
      }));
    } finally {
      if (client) client.release();
    }
  }
}

