import DatabaseManager from '../database';
import { EventLog } from '../types';
import { v4 as uuidv4 } from 'uuid';

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

  async getEventsByCustomer(customerId: string, limit: number = 50): Promise<EventLog[]> {
    const db = DatabaseManager.getInstance().getDb();
    
    return new Promise((resolve, reject) => {
      db.all(`
        SELECT * FROM event_logs 
        WHERE customer_id = ? 
        ORDER BY timestamp DESC 
        LIMIT ?
      `, [customerId, limit], (err, rows: any[]) => {
        if (err) {
          reject(err);
        } else {
          const events = rows.map(row => ({
            ...row,
            event_data: JSON.parse(row.event_data),
            timestamp: new Date(row.timestamp)
          }));
          resolve(events);
        }
      });
    });
  }

  async getAllEvents(limit: number = 100): Promise<EventLog[]> {
    const db = DatabaseManager.getInstance().getDb();
    
    return new Promise((resolve, reject) => {
      db.all(`
        SELECT * FROM event_logs 
        ORDER BY timestamp DESC 
        LIMIT ?
      `, [limit], (err, rows: any[]) => {
        if (err) {
          reject(err);
        } else {
          const events = rows.map(row => ({
            ...row,
            event_data: JSON.parse(row.event_data),
            timestamp: new Date(row.timestamp)
          }));
          resolve(events);
        }
      });
    });
  }

  async getEventsByType(eventType: string, limit: number = 50): Promise<EventLog[]> {
    const db = DatabaseManager.getInstance().getDb();
    
    return new Promise((resolve, reject) => {
      db.all(`
        SELECT * FROM event_logs 
        WHERE event_type = ? 
        ORDER BY timestamp DESC 
        LIMIT ?
      `, [eventType, limit], (err, rows: any[]) => {
        if (err) {
          reject(err);
        } else {
          const events = rows.map(row => ({
            ...row,
            event_data: JSON.parse(row.event_data),
            timestamp: new Date(row.timestamp)
          }));
          resolve(events);
        }
      });
    });
  }
}