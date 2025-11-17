import DatabaseManager from '../database';
import logger from '../utils/logger';
import { v4 as uuidv4 } from 'uuid';
import { Reminder } from '../types';

const dbManager = DatabaseManager.getInstance();

export class FollowUpService {
  // Follow-up timing based on Frazer Method stages
  private followUpTimes: Record<string, number> = {
    'new_lead': 1,           // 1 day - Quick response for new leads
    'qualified': 3,          // 3 days - Give them time to think
    'presentation': 7,       // 7 days - Follow up after presentation
    'follow_up': 14,         // 14 days - Longer nurture cycle
    'closed': 30             // 30 days - Check-in with closed customers
  };
  
  async createFollowUp(customerId: string, stage: string): Promise<Reminder> {
    const days = this.followUpTimes[stage] || 7;
    const scheduledFor = new Date();
    scheduledFor.setDate(scheduledFor.getDate() + days);
    
    const message = this.getFollowUpMessage(stage);
    
    try {
      const db = dbManager.getDb();
      return new Promise((resolve, reject) => {
        const id = uuidv4();
        db.run(
          `INSERT INTO reminders (id, customer_id, type, message, scheduled_for, created_at) 
           VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)`,
          [id, customerId, 'follow_up', message, scheduledFor.toISOString()],
          function(err: Error | null) {
            if (err) return reject(err);
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
                });
              } else {
                reject(new Error("Failed to retrieve created reminder."));
              }
            });
          }
        );
      });
      
      logger.info(`Created follow-up for customer ${customerId} at stage ${stage}, scheduled for ${scheduledFor.toISOString()}`);
    } catch (error) {
      logger.error("Error creating follow-up:", error);
      throw error;
    }
  }
  
  private getFollowUpMessage(stage: string): string {
    const messages: Record<string, string> = {
      'new_lead': 'Follow up with new lead - establish rapport',
      'qualified': 'Check if prospect has questions about opportunity',
      'presentation': 'Follow up on presentation - address concerns',
      'follow_up': 'Continue nurturing relationship',
      'closed': 'Check in on progress and satisfaction'
    };
    
    return messages[stage] || `Follow up on ${stage}`;
  }
  
  async autoScheduleFollowUps(): Promise<number> {
    try {
      const db = dbManager.getDb();
      const customers: any[] = await new Promise((resolve, reject) => {
        db.all(
          "SELECT id, status FROM customers WHERE status <> 'Closed - Won'",
          (err: Error | null, rows: any[]) => {
            if (err) reject(err);
            else resolve(rows || []);
          }
        );
      });
      
      let scheduled = 0;
      for (const customer of customers) {
        await this.createFollowUp(customer.id, customer.status);
        scheduled++;
      }
      
      logger.info(`Auto-scheduled ${scheduled} follow-ups`);
      return scheduled;
    } catch (error) {
      logger.error("Error auto-scheduling follow-ups:", error);
      throw error;
    }
  }
  
  async getUpcomingFollowUps(days: number = 7): Promise<any[]> {
    const futureDate = new Date();
    futureDate.setDate(futureDate.getDate() + days);
    
    try {
      const db = dbManager.getDb();
      const followUps: any[] = await new Promise((resolve, reject) => {
        db.all(
          `SELECT r.*, c.name as customer_name, c.email, c.status
           FROM reminders r
           JOIN customers c ON r.customer_id = c.id
           WHERE r.type = 'follow_up'
           AND r.scheduled_for <= ?
           AND r.completed = false
           ORDER BY r.scheduled_for ASC`,
          [futureDate.toISOString()],
          (err: Error | null, rows: any[]) => {
            if (err) reject(err);
            else resolve(rows || []);
          }
        );
      });
      
      return followUps;
    } catch (error) {
      logger.error("Error getting upcoming follow-ups:", error);
      throw error;
    }
  }
}

export const followUpService = new FollowUpService();
