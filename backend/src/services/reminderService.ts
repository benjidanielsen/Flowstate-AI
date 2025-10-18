import DatabaseManager from '../database';
import { v4 as uuidv4 } from 'uuid';
import { Reminder, ReminderType } from '../types';
import { PoolClient } from 'pg';

export class ReminderService {
  async createReminder(data: {
    customer_id: string;
    type: ReminderType;
    message: string;
    scheduled_for: Date;
    repeat_interval?: string;
  }): Promise<Reminder> {
    let client: PoolClient | null = null;
    try {
      const pool = DatabaseManager.getInstance().getPool();
      client = await pool.connect();
      const id = uuidv4();
      const now = new Date();
      const result = await client.query(
        `INSERT INTO reminders (id, customer_id, type, message, scheduled_for, completed, created_at, updated_at, repeat_interval)
         VALUES ($1, $2, $3, $4, $5, FALSE, $6, $7, $8) RETURNING *`,
        [
          id,
          data.customer_id,
          data.type,
          data.message,
          data.scheduled_for.toISOString(),
          now.toISOString(),
          now.toISOString(),
          data.repeat_interval || null
        ]
      );
      return result.rows[0];
    } finally {
      if (client) client.release();
    }
  }

  async getDueReminders(): Promise<Reminder[]> {
    let client: PoolClient | null = null;
    try {
      const pool = DatabaseManager.getInstance().getPool();
      client = await pool.connect();
      const now = new Date().toISOString();
      const result = await client.query(
        `SELECT * FROM reminders WHERE completed = FALSE AND scheduled_for <= $1 ORDER BY scheduled_for ASC`,
        [now]
      );
      return result.rows.map(r => ({
        id: r.id,
        customer_id: r.customer_id,
        type: r.type,
        message: r.message,
        scheduled_for: new Date(r.scheduled_for),
        completed: r.completed,
        created_at: new Date(r.created_at),
        updated_at: new Date(r.updated_at),
        repeat_interval: r.repeat_interval,
      }));
    } finally {
      if (client) client.release();
    }
  }

  async markReminderCompleted(id: string): Promise<Reminder | null> {
    let client: PoolClient | null = null;
    try {
      const pool = DatabaseManager.getInstance().getPool();
      client = await pool.connect();
      const now = new Date().toISOString();
      const result = await client.query(
        `UPDATE reminders SET completed = TRUE, updated_at = $1 WHERE id = $2 RETURNING *`,
        [now, id]
      );
      return result.rows[0] || null;
    } finally {
      if (client) client.release();
    }
  }

  async getRemindersByCustomerId(customerId: string): Promise<Reminder[]> {
    let client: PoolClient | null = null;
    try {
      const pool = DatabaseManager.getInstance().getPool();
      client = await pool.connect();
      const result = await client.query(
        `SELECT * FROM reminders WHERE customer_id = $1 ORDER BY scheduled_for ASC`,
        [customerId]
      );
      return result.rows.map(r => ({
        id: r.id,
        customer_id: r.customer_id,
        type: r.type,
        message: r.message,
        scheduled_for: new Date(r.scheduled_for),
        completed: r.completed,
        created_at: new Date(r.created_at),
        updated_at: new Date(r.updated_at),
        repeat_interval: r.repeat_interval,
      }));
    } finally {
      if (client) client.release();
    }
  }

  async getAllReminders(): Promise<Reminder[]> {
    let client: PoolClient | null = null;
    try {
      const pool = DatabaseManager.getInstance().getPool();
      client = await pool.connect();
      const result = await client.query(
        `SELECT * FROM reminders ORDER BY scheduled_for ASC`
      );
      return result.rows.map(r => ({
        id: r.id,
        customer_id: r.customer_id,
        type: r.type,
        message: r.message,
        scheduled_for: new Date(r.scheduled_for),
        completed: r.completed,
        created_at: new Date(r.created_at),
        updated_at: new Date(r.updated_at),
        repeat_interval: r.repeat_interval,
      }));
    } finally {
      if (client) client.release();
    }
  }

  async updateReminder(id: string, data: {
    type?: ReminderType;
    message?: string;
    scheduled_for?: Date;
    completed?: boolean;
    repeat_interval?: string;
  }): Promise<Reminder | null> {
    let client: PoolClient | null = null;
    try {
      const pool = DatabaseManager.getInstance().getPool();
      client = await pool.connect();
      const now = new Date().toISOString();
      const fields: string[] = [];
      const values: any[] = [];

      if (data.type) { fields.push('type = $'+(fields.length+1)); values.push(data.type); }
      if (data.message) { fields.push('message = $'+(fields.length+1)); values.push(data.message); }
      if (data.scheduled_for) { fields.push('scheduled_for = $'+(fields.length+1)); values.push(data.scheduled_for.toISOString()); }
      if (data.completed !== undefined) { fields.push('completed = $'+(fields.length+1)); values.push(data.completed); }
      if (data.repeat_interval !== undefined) { fields.push('repeat_interval = $'+(fields.length+1)); values.push(data.repeat_interval); }

      if (fields.length === 0) return this.getReminderById(id); // No fields to update

      fields.push('updated_at = $'+(fields.length+1));
      values.push(now);
      values.push(id);

      const result = await client.query(
        `UPDATE reminders SET ${fields.join(', ')} WHERE id = $${values.length} RETURNING *`,
        values
      );
      return result.rows[0] || null;
    } finally {
      if (client) client.release();
    }
  }

  async deleteReminder(id: string): Promise<boolean> {
    let client: PoolClient | null = null;
    try {
      const pool = DatabaseManager.getInstance().getPool();
      client = await pool.connect();
      const result = await client.query(
        `DELETE FROM reminders WHERE id = $1 RETURNING id`,
        [id]
      );
      return result.rowCount !== null && result.rowCount > 0;
    } finally {
      if (client) client.release();
    }
  }

  async getReminderById(id: string): Promise<Reminder | null> {
    let client: PoolClient | null = null;
    try {
      const pool = DatabaseManager.getInstance().getPool();
      client = await pool.connect();
      const result = await client.query(
        `SELECT * FROM reminders WHERE id = $1`,
        [id]
      );
      const row = result.rows[0];
      if (row) {
        return {
          id: row.id,
          customer_id: row.customer_id,
          type: row.type,
          message: row.message,
          scheduled_for: new Date(row.scheduled_for),
          completed: row.completed,
          created_at: new Date(row.created_at),
          updated_at: new Date(row.updated_at),
          repeat_interval: row.repeat_interval,
        };
      } else {
        return null;
      }
    } finally {
      if (client) client.release();
    }
  }
}

