import DatabaseManager from '../database';
import { v4 as uuidv4 } from 'uuid';
import { PaginatedResult, Reminder, ReminderType } from '../types';

interface ReminderListOptions {
  page?: number;
  pageSize?: number;
  onlyOpen?: boolean;
}

export class ReminderService {
  async createReminder(data: {
    customer_id: string;
    type: ReminderType;
    message: string;
    scheduled_for: Date;
    repeat_interval?: string;
  }): Promise<Reminder> {
    const db = DatabaseManager.getInstance().getDb();
    const id = uuidv4();
    const now = new Date();
    return new Promise((resolve, reject) => {
      const stmt = db.prepare(`
        INSERT INTO reminders (id, customer_id, type, message, scheduled_for, created_at, updated_at, repeat_interval)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
      `);
      stmt.run([
        id,
        data.customer_id,
        data.type,
        data.message,
        data.scheduled_for.toISOString(),
        now.toISOString(),
        now.toISOString(),
        data.repeat_interval || null
      ], (err) => {
        if (err) return reject(err);
        resolve({
          id,
          customer_id: data.customer_id,
          type: data.type,
          message: data.message,
          scheduled_for: data.scheduled_for,
          completed: false,
          created_at: now,
          updated_at: now,
          repeat_interval: data.repeat_interval || null,
        } as Reminder);
      });
      stmt.finalize();
    });
  }

  async getDueReminders(options: { dueInMinutes?: number } & ReminderListOptions = {}): Promise<PaginatedResult<Reminder>> {
    const manager = DatabaseManager.getInstance();
    const pool = await manager.connect();
    const dueInMinutes = options.dueInMinutes ?? 1440; // default 24h
    const cutoff = new Date(Date.now() + dueInMinutes * 60 * 1000);
    const page = Math.max(options.page || 1, 1);
    const rawPageSize = options.pageSize || 25;
    const pageSize = Math.min(Math.max(rawPageSize, 1), 100);
    const offset = (page - 1) * pageSize;

    const totalResult = await pool.query<{ count: number }>(
      'SELECT COUNT(*)::BIGINT AS count FROM reminders WHERE completed = false AND scheduled_for <= $1',
      [cutoff.toISOString()]
    );
    const total = Number(totalResult.rows[0]?.count || 0);
    const dataResult = await pool.query(
      'SELECT * FROM reminders WHERE completed = false AND scheduled_for <= $1 ORDER BY scheduled_for ASC LIMIT $2 OFFSET $3',
      [cutoff.toISOString(), pageSize, offset]
    );

    const reminders = dataResult.rows.map(row => this.mapReminderRow(row));
    return {
      data: reminders,
      meta: {
        page,
        pageSize,
        total,
        hasMore: offset + reminders.length < total,
      },
    };
  }

  async markReminderCompleted(id: string): Promise<Reminder | null> {
    const db = DatabaseManager.getInstance().getDb();
    const now = new Date().toISOString();
    const mapReminder = this.mapReminderRow.bind(this);
    return new Promise((resolve, reject) => {
      db.run('UPDATE reminders SET completed = true, updated_at = ? WHERE id = ?', [now, id], function(err) {
        if (err) return reject(err);
        if (this.changes > 0) {
          db.get('SELECT * FROM reminders WHERE id = ?', [id], (err, row: any) => {
            if (err) return reject(err);
            if (row) {
              resolve(mapReminder(row));
            } else {
              resolve(null);
            }
          });
        } else {
          resolve(null);
        }
      });
    });
  }

  async getRemindersByCustomerId(customerId: string, options: ReminderListOptions = {}): Promise<PaginatedResult<Reminder>> {
    const manager = DatabaseManager.getInstance();
    const pool = await manager.connect();
    const clauses = ['customer_id = $1'];
    const params: any[] = [customerId];
    if (options.onlyOpen) {
      clauses.push(`completed = false`);
    }
    const whereClause = `WHERE ${clauses.join(' AND ')}`;

    const page = Math.max(options.page || 1, 1);
    const rawPageSize = options.pageSize || 25;
    const pageSize = Math.min(Math.max(rawPageSize, 1), 100);
    const offset = (page - 1) * pageSize;

    const totalResult = await pool.query<{ count: number }>(
      `SELECT COUNT(*)::BIGINT AS count FROM reminders ${whereClause}`,
      params
    );
    const total = Number(totalResult.rows[0]?.count || 0);
    const limitIndex = params.length + 1;
    const dataResult = await pool.query(
      `SELECT * FROM reminders ${whereClause} ORDER BY scheduled_for ASC LIMIT $${limitIndex} OFFSET $${limitIndex + 1}`,
      [...params, pageSize, offset]
    );
    const reminders = dataResult.rows.map(row => this.mapReminderRow(row));
    return {
      data: reminders,
      meta: {
        page,
        pageSize,
        total,
        hasMore: offset + reminders.length < total,
      },
    };
  }

  async getAllReminders(): Promise<Reminder[]> {
    const db = DatabaseManager.getInstance().getDb();
    return new Promise((resolve, reject) => {
      db.all(
        'SELECT * FROM reminders ORDER BY scheduled_for ASC',
        (err, rows: any[]) => {
          if (err) return reject(err);
          resolve(rows.map(row => this.mapReminderRow(row)));
        }
      );
    });
  }

  async updateReminder(id: string, data: {
    type?: ReminderType;
    message?: string;
    scheduled_for?: Date;
    completed?: boolean;
    repeat_interval?: string;
  }): Promise<Reminder | null> {
    const db = DatabaseManager.getInstance().getDb();
    const now = new Date().toISOString();
    const fields: string[] = [];
    const values: any[] = [];

    if (data.type) { fields.push('type = ?'); values.push(data.type); }
    if (data.message) { fields.push('message = ?'); values.push(data.message); }
    if (data.scheduled_for) { fields.push('scheduled_for = ?'); values.push(data.scheduled_for.toISOString()); }
    if (data.completed !== undefined) { fields.push('completed = ?'); values.push(data.completed); }
    if (data.repeat_interval !== undefined) { fields.push('repeat_interval = ?'); values.push(data.repeat_interval); }

    if (fields.length === 0) return this.getReminderById(id);

    fields.push('updated_at = ?');
    values.push(now);
    values.push(id);

    return new Promise((resolve, reject) => {
      db.run(`UPDATE reminders SET ${fields.join(', ')} WHERE id = ?`, values, (err) => {
        if (err) return reject(err);
        this.getReminderById(id)
          .then(reminder => resolve(reminder))
          .catch(reject);
      });
    });
  }

  async deleteReminder(id: string): Promise<boolean> {
    const db = DatabaseManager.getInstance().getDb();
    return new Promise((resolve, reject) => {
      db.run('DELETE FROM reminders WHERE id = ?', [id], function(err) {
        if (err) return reject(err);
        resolve(this.changes > 0);
      });
    });
  }

  async getReminderById(id: string): Promise<Reminder | null> {
    const db = DatabaseManager.getInstance().getDb();
    return new Promise((resolve, reject) => {
      db.get('SELECT * FROM reminders WHERE id = ?', [id], (err, row: any) => {
        if (err) return reject(err);
        if (row) {
          resolve(this.mapReminderRow(row));
        } else {
          resolve(null);
        }
      });
    });
  }

  private mapReminderRow(row: any): Reminder {
    return {
      id: row.id,
      customer_id: row.customer_id,
      type: row.type,
      message: row.message,
      scheduled_for: new Date(row.scheduled_for),
      completed: Boolean(row.completed),
      created_at: new Date(row.created_at),
      updated_at: new Date(row.updated_at),
      repeat_interval: row.repeat_interval,
    };
  }
}
