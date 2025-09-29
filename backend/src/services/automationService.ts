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
}

