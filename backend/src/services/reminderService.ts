import DatabaseManager from '../database';
import { v4 as uuidv4 } from 'uuid';

export class ReminderService {
  async createReminder(data: { customer_id: string; type: string; message?: string; scheduled_for: Date }) {
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
        resolve({ id, ...data, completed: false, created_at });
      });
      stmt.finalize();
    });
  }

  async getDueReminders() {
    const db = DatabaseManager.getInstance().getDb();
    const now = new Date().toISOString();
    return new Promise((resolve, reject) => {
      db.all(
        `SELECT * FROM reminders WHERE completed = 0 AND scheduled_for <= ? ORDER BY scheduled_for ASC`,
        [now],
        (err, rows: any[]) => {
          if (err) return reject(err);
          const reminders = rows.map(r => ({ ...r }));
          resolve(reminders);
        }
      );
    });
  }

  async markReminderCompleted(id: string): Promise<any> {
    const db = DatabaseManager.getInstance().getDb();
    return new Promise((resolve, reject) => {
      db.run(`UPDATE reminders SET completed = 1 WHERE id = ?`, [id], function(err) {
        if (err) return reject(err);
        if (this.changes > 0) {
          db.get(`SELECT * FROM reminders WHERE id = ?`, [id], (err, row) => {
            if (err) reject(err);
            else resolve(row);
          });
        } else {
          resolve(null);
        }
      });
    });
  }

  async getRemindersByCustomerId(customerId: string): Promise<any[]> {
    const db = DatabaseManager.getInstance().getDb();
    return new Promise((resolve, reject) => {
      db.all(
        `SELECT * FROM reminders WHERE customer_id = ? ORDER BY scheduled_for ASC`,
        [customerId],
        (err, rows: any[]) => {
          if (err) return reject(err);
          const reminders = rows.map(r => ({ ...r, scheduled_for: new Date(r.scheduled_for), created_at: new Date(r.created_at) }));
          resolve(reminders);
        }
      );
    });
  }

  async getAllReminders(): Promise<any[]> {
    const db = DatabaseManager.getInstance().getDb();
    return new Promise((resolve, reject) => {
      db.all(
        `SELECT * FROM reminders ORDER BY scheduled_for ASC`,
        (err, rows: any[]) => {
          if (err) return reject(err);
          const reminders = rows.map(r => ({ ...r, scheduled_for: new Date(r.scheduled_for), created_at: new Date(r.created_at) }));
          resolve(reminders);
        }
      );
    });
  }
}

