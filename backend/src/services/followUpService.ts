import DatabaseManager from '../database';

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
  
  async createFollowUp(customerId: string, stage: string): Promise<void> {
    const days = this.followUpTimes[stage] || 7;
    const scheduledFor = new Date();
    scheduledFor.setDate(scheduledFor.getDate() + days);
    
    const message = this.getFollowUpMessage(stage);
    
    try {
      const db = dbManager.getDb();
      await new Promise((resolve, reject) => {
        db.run(
          `INSERT INTO reminders (customer_id, type, message, scheduled_for, created_at) 
           VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)`,
          [customerId, 'follow_up', message, scheduledFor.toISOString()],
          (err) => {
            if (err) reject(err);
            else resolve(null);
          }
        );
      });
      
      console.log(`Created follow-up for customer ${customerId} at stage ${stage}, scheduled for ${scheduledFor.toISOString()}`);
    } catch (error) {
      console.error('Error creating follow-up:', error);
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
          'SELECT id, status FROM customers WHERE status != "Closed - Won"',
          (err, rows) => {
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
      
      console.log(`Auto-scheduled ${scheduled} follow-ups`);
      return scheduled;
    } catch (error) {
      console.error('Error auto-scheduling follow-ups:', error);
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
           AND r.completed = 0
           ORDER BY r.scheduled_for ASC`,
          [futureDate.toISOString()],
          (err, rows) => {
            if (err) reject(err);
            else resolve(rows || []);
          }
        );
      });
      
      return followUps;
    } catch (error) {
      console.error('Error getting upcoming follow-ups:', error);
      throw error;
    }
  }
}

export const followUpService = new FollowUpService();
