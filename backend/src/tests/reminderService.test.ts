import { ReminderService } from '../services/reminderService';
import { CustomerService } from '../services/customerService';
import { PipelineStatus } from '../types';
import DatabaseManager from '../database';
import { runMigrations } from '../database/migrate';

describe('ReminderService', () => {
  let reminderService: ReminderService;
  let customerService: CustomerService;
  let testCustomerId: number;

  beforeEach(async () => {
    await DatabaseManager.getInstance().connect();
    await runMigrations();
    reminderService = new ReminderService();
    customerService = new CustomerService();

    // Create a test customer for reminders
    const customerData = {
      name: 'Reminder Test Customer',
      email: 'reminder@example.com',
      status: PipelineStatus.NEW_LEAD,
    };
    const customer = await customerService.createCustomer(customerData);
    testCustomerId = customer.id;
  });

  afterEach(async () => {
    await DatabaseManager.getInstance().close();
  });

  describe('createReminder', () => {
    it('should create a new reminder for a customer', async () => {
      const reminderData = {
        customerId: testCustomerId,
        message: 'Follow up with customer',
        scheduledAt: new Date().toISOString(),
      };

      const reminder = await reminderService.createReminder(reminderData);

      expect(reminder).toBeDefined();
      expect(reminder.customerId).toBe(reminderData.customerId);
      expect(reminder.message).toBe(reminderData.message);
      expect(reminder.id).toBeDefined();
    });
  });

  describe('getDueReminders', () => {
    it('should return reminders that are due', async () => {
      // Schedule a reminder that is due now
      const pastDate = new Date();
      pastDate.setMinutes(pastDate.getMinutes() - 5); // 5 minutes ago
      await reminderService.createReminder({
        customerId: testCustomerId,
        message: 'Due reminder',
        scheduledAt: pastDate.toISOString(),
      });

      const dueReminders = await reminderService.getDueReminders();
      expect(Array.isArray(dueReminders)).toBe(true);
      expect(dueReminders.length).toBeGreaterThan(0);
      expect(dueReminders.some(r => r.customerId === testCustomerId && r.message === 'Due reminder')).toBe(true);
    });
  });

  describe('markReminderCompleted', () => {
    it('should mark a reminder as completed', async () => {
      const reminderData = {
        customerId: testCustomerId,
        message: 'Reminder to complete',
        scheduledAt: new Date().toISOString(),
      };
      const createdReminder = await reminderService.createReminder(reminderData);

      const completedReminder = await reminderService.markReminderCompleted(createdReminder.id);

      expect(completedReminder).toBeDefined();
      expect(completedReminder?.completed).toBe(true);
    });
  });
});

