import { AutomationService } from '../services/automationService';
import { CustomerService } from '../services/customerService';
import { PipelineStatus, Reminder } from '../types';
import DatabaseManager from '../database';
import { runMigrations } from '../database/migrate';
import { ReminderService } from '../services/reminderService';

describe('AutomationService', () => {
  let automationService: AutomationService;
  let customerService: CustomerService;
  let reminderService: ReminderService;
  let testCustomerId: string;

  beforeEach(async () => {
    await DatabaseManager.getInstance().connect();
    const db = DatabaseManager.getInstance().getDb();
    await new Promise<void>((resolve, reject) => {
      db.exec("DROP TABLE IF EXISTS customers; DROP TABLE IF EXISTS interactions; DROP TABLE IF EXISTS reminders; DROP TABLE IF EXISTS event_logs;", (err) => {
        if (err) reject(err);
        else resolve();
      });
    });
    await runMigrations();
    automationService = new AutomationService();
    customerService = new CustomerService();
    reminderService = new ReminderService();

    // Create a test customer for automation
    const customerData = {
      name: 'Automation Test Customer',
      email: 'automation@example.com',
      status: PipelineStatus.NEW_LEAD,
    };
    const customer = await customerService.createCustomer(customerData);
    testCustomerId = customer.id;
  });

  afterEach(async () => {
    await DatabaseManager.getInstance().close();
  });

  describe('handleEvent', () => {
    it('should create reminders for VIDEO_SENT event', async () => {
      const initialReminders: Reminder[] = await reminderService.getAllReminders();
      expect(initialReminders.length).toBe(0);

      await automationService.handleEvent({ event_name: 'VIDEO_SENT', customer_id: testCustomerId });

      const newReminders: Reminder[] = await reminderService.getAllReminders();
      expect(newReminders.length).toBe(2); // Expecting 2 reminders for VIDEO_SENT
      expect(newReminders.some(r => r.type === 'follow_up_24h')).toBe(true);
      expect(newReminders.some(r => r.type === 'follow_up_48h')).toBe(true);
    });

    it('should create reminders for NO_SHOW event', async () => {
      const initialReminders: Reminder[] = await reminderService.getAllReminders();
      expect(initialReminders.length).toBe(0);

      await automationService.handleEvent({ event_name: 'NO_SHOW', customer_id: testCustomerId });

      const newReminders: Reminder[] = await reminderService.getAllReminders();
      expect(newReminders.length).toBe(2); // Expecting 2 reminders for NO_SHOW
      expect(newReminders.some(r => r.type === 'follow_up_2h')).toBe(true);
      expect(newReminders.some(r => r.type === 'follow_up_1d')).toBe(true);
    });

    it('should not create reminders for unknown events', async () => {
      const initialReminders: Reminder[] = await reminderService.getAllReminders();
      expect(initialReminders.length).toBe(0);

      await automationService.handleEvent({ event_name: 'UNKNOWN_EVENT', customer_id: testCustomerId });

      const newReminders: Reminder[] = await reminderService.getAllReminders();
      expect(newReminders.length).toBe(0);
    });

    it('should not create reminders if customer_id is missing', async () => {
      const initialReminders: Reminder[] = await reminderService.getAllReminders();
      expect(initialReminders.length).toBe(0);

      await automationService.handleEvent({ event_name: 'VIDEO_SENT' });

      const newReminders: Reminder[] = await reminderService.getAllReminders();
      expect(newReminders.length).toBe(0);
    });

    it('chains reminders when multiple automation events fire in sequence', async () => {
      await automationService.handleEvent({ event_name: 'VIDEO_SENT', customer_id: testCustomerId });
      await automationService.handleEvent({ event_name: 'NO_SHOW', customer_id: testCustomerId });

      const reminders: Reminder[] = await reminderService.getAllReminders();
      expect(reminders.length).toBe(4);
      const types = reminders.map(r => r.type).sort();
      expect(types).toEqual(['follow_up_1d', 'follow_up_24h', 'follow_up_2h', 'follow_up_48h'].sort());
      const scheduledDates = reminders.map(r => new Date(r.scheduled_for));
      const now = Date.now();
      scheduledDates.forEach(date => expect(date.getTime()).toBeGreaterThan(now));
    });
  });
});

