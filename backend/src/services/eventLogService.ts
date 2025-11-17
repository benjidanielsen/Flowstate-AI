import DatabaseManager from '../database';
import { EventLog, PaginatedResult } from '../types';
import { v4 as uuidv4 } from 'uuid';

interface EventQueryOptions {
  page?: number;
  pageSize?: number;
  customerId?: string;
  eventType?: string;
  source?: string;
  from?: Date;
  to?: Date;
}

export class EventLogService {
  async logEvent(eventType: string, eventData: any, customerId?: string, userId?: string): Promise<EventLog> {
    const db = DatabaseManager.getInstance().getDb();
    const id = uuidv4();
    const timestamp = new Date();

    const eventLog: EventLog = {
      id,
      customer_id: customerId,
      event_type: eventType,
      event_data: eventData,
      timestamp,
      user_id: userId
    };

    return new Promise((resolve, reject) => {
      const stmt = db.prepare(`
        INSERT INTO event_logs (id, customer_id, event_type, event_data, timestamp, user_id)
        VALUES (?, ?, ?, ?, ?, ?)
      `);

      stmt.run([
        eventLog.id,
        eventLog.customer_id,
        eventLog.event_type,
        JSON.stringify(eventLog.event_data),
        eventLog.timestamp.toISOString(),
        eventLog.user_id
      ], function(err) {
        if (err) {
          reject(err);
        } else {
          resolve(eventLog);
        }
      });

      stmt.finalize();
    });
  }

  async getEvents(options: EventQueryOptions = {}): Promise<PaginatedResult<EventLog>> {
    const manager = DatabaseManager.getInstance();
    const pool = await manager.connect();
    const clauses: string[] = [];
    const params: any[] = [];
    let idx = 1;

    if (options.customerId) {
      clauses.push(`customer_id = $${idx++}`);
      params.push(options.customerId);
    }
    if (options.eventType) {
      clauses.push(`event_type = $${idx++}`);
      params.push(options.eventType);
    }
    if (options.source) {
      clauses.push(`event_data->>'source' = $${idx++}`);
      params.push(options.source);
    }
    if (options.from) {
      clauses.push(`timestamp >= $${idx++}`);
      params.push(options.from.toISOString());
    }
    if (options.to) {
      clauses.push(`timestamp <= $${idx++}`);
      params.push(options.to.toISOString());
    }

    const whereClause = clauses.length ? `WHERE ${clauses.join(' AND ')}` : '';
    const page = Math.max(options.page || 1, 1);
    const rawPageSize = options.pageSize || 50;
    const pageSize = Math.min(Math.max(rawPageSize, 1), 250);
    const offset = (page - 1) * pageSize;

    const totalResult = await pool.query<{ count: number }>(
      `SELECT COUNT(*)::BIGINT AS count FROM event_logs ${whereClause}`,
      params
    );
    const total = Number(totalResult.rows[0]?.count || 0);

    const dataResult = await pool.query(
      `SELECT * FROM event_logs ${whereClause} ORDER BY timestamp DESC LIMIT $${idx} OFFSET $${idx + 1}`,
      [...params, pageSize, offset]
    );
    const events = dataResult.rows.map(row => this.mapEventRow(row));

    return {
      data: events,
      meta: {
        page,
        pageSize,
        total,
        hasMore: offset + events.length < total,
      },
    };
  }

  async getEventsByCustomer(customerId: string, options?: EventQueryOptions): Promise<PaginatedResult<EventLog>> {
    return this.getEvents({ ...options, customerId });
  }

  async getAllEvents(options?: EventQueryOptions): Promise<PaginatedResult<EventLog>> {
    return this.getEvents(options);
  }

  async getEventsByType(eventType: string, options?: EventQueryOptions): Promise<PaginatedResult<EventLog>> {
    return this.getEvents({ ...options, eventType });
  }

  private mapEventRow(row: any): EventLog {
    return {
      ...row,
      event_data: typeof row.event_data === 'string' ? JSON.parse(row.event_data) : row.event_data,
      timestamp: new Date(row.timestamp)
    };
  }
}