import DatabaseManager from '../database';
import { v4 as uuidv4 } from 'uuid';
import { Reminder } from '../types';

export class ReminderService {
  async createReminder(data: { customer_id: string; type: string; message?: string; scheduled_for: Date }): Promise<Reminder> {
    const db = DatabaseManager.getInstance().getDb();
    const id = uuidv4();
    const created_at = new Date();
    return new Promise((resolve, reject) => {
      const stmt = db.prepare(`
        INSERT INTO reminders (id, customer_id, type, message, scheduled_for, completed, created_at)
        VALUES (?, ?, ?, ?, ?, 0, ?)
      `);
      stmt.run([
        id,
        data.customer_id,
        data.type,
        data.message || null,
        data.scheduled_for.toISOString(),
        created_at.toISOString()
      ], (err) => {
        if (err) return reject(err);
        resolve({
          id,
          customer_id: data.customer_id,
          type: data.type,
          message: data.message || null,
          scheduled_for: data.scheduled_for,
          completed: false,
          created_at,
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
          }));
          resolve(  async markReminderCompleted(id: string): Promise<Reminder | null> {
    const db = DatabaseManager.getInstance().getDb();
    return new Promise((resolve, reject) => {
      db.run(`UPDATE reminders SET completed = 1 WHERE id = ?`, [id], (err) => {
        if (err) return reject(err);
        // After attempting to update, always try to retrieve the reminder to get its current state
        db.get(`SELECT * FROM reminders WHERE id = ?`, [id], (err, row: any) => {
          if (err) return reject(err);
          if (row) {
            resolve({
              id: row.id,
              customer_id: row.customer_id,
              type: row.type,
              message: row.message,
              scheduled_for: new Date(row.scheduled_for),
              completed: Boolean(row.completed), // Convert DB integer to boolean
              created_at: new Date(row.created_at),
            });
          } else {
            resolve(null);
          }
        });
      });
    });
  }d: string): Promise<Reminder[]> {
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
          }));
          resolve(reminders);
        }
      );
    });
  }
}

