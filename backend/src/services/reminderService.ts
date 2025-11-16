import DatabaseManager from '../database';
import { v4 as uuidv4 } from 'uuid';
import { PipelineStatus, Reminder, ReminderType } from '../types';
import { getStageDefinition } from './frazerStageConfig';

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
        INSERT INTO reminders (id, customer_id, type, message, scheduled_for, completed, created_at, updated_at, repeat_interval)
        VALUES (?, ?, ?, ?, ?, 0, ?, ?, ?)
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

  async getDueReminders(): Promise<Reminder[]> {
    const db = DatabaseManager.getInstance().getDb();
    const now = new Date().toISOString();
    return new Promise((resolve, reject) => {
      db.all(
        `SELECT * FROM reminders WHERE completed = 0 AND scheduled_for <= ? ORDER BY scheduled_for ASC`,
        [now],
        (err, rows: any[]) => {
          if (err) return reject(err);
          const reminders = rows.map(r => ({
            id: r.id,
            customer_id: r.customer_id,
            type: r.type,
            message: r.message,
            scheduled_for: new Date(r.scheduled_for),
            completed: Boolean(r.completed),
            created_at: new Date(r.created_at),
            updated_at: new Date(r.updated_at),
            repeat_interval: r.repeat_interval,
          }));
          resolve(reminders);
        }
      );
    });
  }

  async markReminderCompleted(id: string): Promise<Reminder | null> {
    const db = DatabaseManager.getInstance().getDb();
    const now = new Date().toISOString();
    return new Promise((resolve, reject) => {
      db.run(`UPDATE reminders SET completed = 1, updated_at = ? WHERE id = ?`, [now, id], function(err) {
        if (err) return reject(err);
        if (this.changes > 0) {
          db.get(`SELECT * FROM reminders WHERE id = ?`, [id], (err, row: any) => {
            if (err) return reject(err);
            if (row) {
              resolve({
                id: row.id,
                customer_id: row.customer_id,
                type: row.type,
                message: row.message,
                scheduled_for: new Date(row.scheduled_for),
                completed: true,
                created_at: new Date(row.created_at),
                updated_at: new Date(row.updated_at),
                repeat_interval: row.repeat_interval,
              });
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

  async getRemindersByCustomerId(customerId: string): Promise<Reminder[]> {
    const db = DatabaseManager.getInstance().getDb();
    return new Promise((resolve, reject) => {
      db.all(
        `SELECT * FROM reminders WHERE customer_id = ? ORDER BY scheduled_for ASC`,
        [customerId],
        (err, rows: any[]) => {
          if (err) return reject(err);
          const reminders = rows.map(r => ({
            id: r.id,
            customer_id: r.customer_id,
            type: r.type,
            message: r.message,
            scheduled_for: new Date(r.scheduled_for),
            completed: Boolean(r.completed),
            created_at: new Date(r.created_at),
            updated_at: new Date(r.updated_at),
            repeat_interval: r.repeat_interval,
          }));
          resolve(reminders);
        }
      );
    });
  }

  async getAllReminders(): Promise<Reminder[]> {
    const db = DatabaseManager.getInstance().getDb();
    return new Promise((resolve, reject) => {
      db.all(
        `SELECT * FROM reminders ORDER BY scheduled_for ASC`,
        (err, rows: any[]) => {
          if (err) return reject(err);
          const reminders = rows.map(r => ({
            id: r.id,
            customer_id: r.customer_id,
            type: r.type,
            message: r.message,
            scheduled_for: new Date(r.scheduled_for),
            completed: Boolean(r.completed),
            created_at: new Date(r.created_at),
            updated_at: new Date(r.updated_at),
            repeat_interval: r.repeat_interval,
          }));
          resolve(reminders);
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
    if (data.completed !== undefined) { fields.push('completed = ?'); values.push(data.completed ? 1 : 0); }
    if (data.repeat_interval !== undefined) { fields.push('repeat_interval = ?'); values.push(data.repeat_interval); }

    if (fields.length === 0) return this.getReminderById(id); // No fields to update

    fields.push('updated_at = ?');
    values.push(now);
    values.push(id);

    return new Promise((resolve, reject) => {
      db.run(`UPDATE reminders SET ${fields.join(', ')} WHERE id = ?`, values, (err) => {
        if (err) return reject(err);
        // Note: changes count not available with arrow function, fetch to verify
        this.getReminderById(id)
          .then(reminder => {
            resolve(reminder);
          })
          .catch(reject);
      });
    });
  }

  async deleteReminder(id: string): Promise<boolean> {
    const db = DatabaseManager.getInstance().getDb();
    return new Promise((resolve, reject) => {
      db.run(`DELETE FROM reminders WHERE id = ?`, [id], function(err) {
        if (err) return reject(err);
        resolve(this.changes > 0);
      });
    });
  }

  async getReminderById(id: string): Promise<Reminder | null> {
    const db = DatabaseManager.getInstance().getDb();
    return new Promise((resolve, reject) => {
      db.get(`SELECT * FROM reminders WHERE id = ?`, [id], (err, row: any) => {
        if (err) return reject(err);
        if (row) {
          resolve({
            id: row.id,
            customer_id: row.customer_id,
            type: row.type,
            message: row.message,
            scheduled_for: new Date(row.scheduled_for),
            completed: Boolean(row.completed),
            created_at: new Date(row.created_at),
            updated_at: new Date(row.updated_at),
            repeat_interval: row.repeat_interval,
          });
        } else {
          resolve(null);
        }
      });
    });
  }

  async scheduleStageReminder(
    customerId: string,
    stage: PipelineStatus,
    options: {
      cadenceHours?: number;
      context?: string;
      skipIfExists?: boolean;
      reminderTypeOverride?: ReminderType;
    } = {}
  ): Promise<Reminder | null> {
    const stageDefinition = getStageDefinition(stage);
    const cadenceHours = options.cadenceHours ?? stageDefinition.cadenceHours;
    const reminderType = options.reminderTypeOverride ?? stageDefinition.reminderType;
    const scheduledFor = new Date(Date.now() + cadenceHours * 60 * 60 * 1000);
    const message = options.context
      ? `${stageDefinition.frazerStep}: ${options.context}`
      : `${stageDefinition.frazerStep} → ${stageDefinition.touchpoint.summary}`;

    if (options.skipIfExists) {
      const existing = await this.findActiveReminder(customerId, reminderType);
      if (existing) {
        return existing;
      }
    }

    return this.createReminder({
      customer_id: customerId,
      type: reminderType,
      message,
      scheduled_for: scheduledFor
    });
  }

  private async findActiveReminder(customerId: string, reminderType: ReminderType): Promise<Reminder | null> {
    const db = DatabaseManager.getInstance().getDb();
    return new Promise((resolve, reject) => {
      db.get(
        `SELECT * FROM reminders
         WHERE customer_id = ? AND type = ? AND completed = 0
         ORDER BY scheduled_for ASC LIMIT 1`,
        [customerId, reminderType],
        (err, row: any) => {
          if (err) return reject(err);
          if (!row) return resolve(null);
          resolve({
            id: row.id,
            customer_id: row.customer_id,
            type: row.type,
            message: row.message,
            scheduled_for: new Date(row.scheduled_for),
            completed: Boolean(row.completed),
            created_at: new Date(row.created_at),
            updated_at: new Date(row.updated_at),
            repeat_interval: row.repeat_interval,
          });
        }
      );
    });
  }
}

