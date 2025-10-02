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
      const initialReminders: Reminder[] = await reminderService.getRemindersByCustomerId(testCustomerId);
      expect(initialReminders.length).toBe(0);

      await automationService.handleEvent({ event_name: 'VIDEO_SENT', customer_id: testCustomerId });

      const newReminders: Reminder[] = await reminderService.getRemindersByCustomerId(testCustomerId);
      expect(newReminders.length).toBe(2); // Expecting 2 reminders for VIDEO_SENT
      expect(newReminders.some(r => r.type === 'follow_up_24h')).toBe(true);
      expect(newReminders.some(r => r.type === 'follow_up_48h')).toBe(true);
    });

    it('should create reminders for NO_SHOW event', async () => {
      const initialReminders: Reminder[] = await reminderService.getRemindersByCustomerId(testCustomerId);
      expect(initialReminders.length).toBe(0);

      await automationService.handleEvent({ event_name: 'NO_SHOW', customer_id: testCustomerId });

      const newReminders: Reminder[] = await reminderService.getRemindersByCustomerId(testCustomerId);
      expect(newReminders.length).toBe(2); // Expecting 2 reminders for NO_SHOW
      expect(newReminders.some(r => r.type === 'follow_up_2h')).toBe(true);
      expect(newReminders.some(r => r.type === 'follow_up_1d')).toBe(true);
    });

    it('should not create reminders for unknown events', async () => {
      const initialReminders: Reminder[] = await reminderService.getRemindersByCustomerId(testCustomerId);
      expect(initialReminders.length).toBe(0);

      await automationService.handleEvent({ event_name: 'UNKNOWN_EVENT', customer_id: testCustomerId });

      const newReminders: Reminder[] = await reminderService.getRemindersByCustomerId(testCustomerId);
      expect(newReminders.length).toBe(0);
    });

    it('should not create reminders if customer_id is missing', async () => {
      const initialReminders: Reminder[] = await reminderService.getRemindersByCustomerId(testCustomerId);
      expect(initialReminders.length).toBe(0);

      await automationService.handleEvent({ event_name: 'VIDEO_SENT' });

      const newReminders: Reminder[] = await reminderService.getRemindersByCustomerId(testCustomerId);
      expect(newReminders.length).toBe(0);
    });
  });
});

