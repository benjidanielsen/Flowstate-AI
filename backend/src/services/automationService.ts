import { ReminderService } from './reminderService';

export class AutomationService {
  private reminderService = new ReminderService();

  async handleEvent(event: { event_name: string; customer_id?: string }) {
    const name = event.event_name;
    const customerId = event.customer_id;
    if (!customerId) return; // cannot attach reminders without customer
    const now = new Date();
    const inHours = (h: number) => new Date(now.getTime() + h * 3600 * 1000);
    const inDays = (d: number) => new Date(now.getTime() + d * 24 * 3600 * 1000);

    switch (name) {
      case 'VIDEO_SENT':
        await this.reminderService.createReminder({ customer_id: customerId, type: 'follow_up_24h', scheduled_for: inHours(24) });
        await this.reminderService.createReminder({ customer_id: customerId, type: 'follow_up_48h', scheduled_for: inHours(48) });
        break;
      case 'NO_SHOW':
        await this.reminderService.createReminder({ customer_id: customerId, type: 'follow_up_2h', scheduled_for: inHours(2) });
        await this.reminderService.createReminder({ customer_id: customerId, type: 'follow_up_1d', scheduled_for: inDays(1) });
        break;
      default:
        break;
    }
  }

  async processInactivity(days: number = 7) {
    const db = DatabaseManager.getInstance().getDb();
    const threshold = new Date(Date.now() - days * 24 * 3600 * 1000).toISOString();

    const rows: any[] = await new Promise((resolve, reject) => {
      db.all(
        `SELECT c.id as customer_id,
                MAX(i.created_at) as last_interaction,
                c.updated_at as cust_updated
         FROM customers c
         LEFT JOIN interactions i ON i.customer_id = c.id
         GROUP BY c.id`,
        (err, rows) => (err ? reject(err) : resolve(rows))
      );
    });

    for (const r of rows) {
      const last = r.last_interaction || r.cust_updated;
      if (!last) continue;
      if (last < threshold) {
        const existing: any = await new Promise((resolve, reject) => {
          db.get(
            `SELECT COUNT(*) as c FROM reminders WHERE customer_id = ? AND type = 'follow_up_7d' AND completed = 0`,
            [r.customer_id],
            (err, row: any) => (err ? reject(err) : resolve(row))
          );
        });
        if ((existing?.c || 0) === 0) {
          await this.reminderService.createReminder({
            customer_id: r.customer_id,
            type: 'follow_up_7d',
            scheduled_for: new Date(),
          });
        }
      }
    }
    return { processed: true, checked: rows.length };
  }
}
