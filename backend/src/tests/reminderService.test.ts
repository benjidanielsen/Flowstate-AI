import { ReminderService } from '../services/reminderService';
import { CustomerService } from '../services/customerService';
import { PipelineStatus, ReminderType, Reminder } from '../types'; // Import ReminderType
import DatabaseManager from '../database';
import { runMigrations } from '../database/migrate';

describe('ReminderService', () => {
  let reminderService: ReminderService;
  let customerService: CustomerService;
  let testCustomerId: string;

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
        customer_id: testCustomerId, // Corrected to customer_id
        type: ReminderType.FOLLOW_UP_24H, // Added type
        message: 'Follow up with customer',
        scheduled_for: new Date(), // Corrected to Date object
      };

      const reminder: Reminder = await reminderService.createReminder(reminderData);

      expect(reminder).toBeDefined();
      expect(reminder.customer_id).toBe(reminderData.customer_id); // Corrected to customer_id
      expect(reminder.type).toBe(reminderData.type); // Added type assertion
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
        customer_id: testCustomerId, // Corrected to customer_id
        type: ReminderType.FOLLOW_UP_2H, // Added type
        message: 'Due reminder',
        scheduled_for: pastDate,
      });

      const dueReminders = await reminderService.getDueReminders();
      expect(Array.isArray(dueReminders)).toBe(true);
      expect(dueReminders.length).toBeGreaterThan(0);
      expect(dueReminders.some((r: any) => r.customer_id === testCustomerId && r.message === 'Due reminder')).toBe(true); // Corrected to customer_id and added type for r
    });
  });

  describe('markReminderCompleted', () => {
    it('should mark a reminder as completed', async () => {
      const reminderData = {
        customer_id: testCustomerId, // Corrected to customer_id
        type: ReminderType.FOLLOW_UP_1D, // Added type
        message: 'Reminder to complete',
        scheduled_for: new Date(),
      };
      const createdReminder: Reminder = await reminderService.createReminder(reminderData);

      const completedReminder = await reminderService.markReminderCompleted(createdReminder.id);

      expect(completedReminder).toBeDefined();
      expect(completedReminder?.completed).toBe(true);
    });
  });
});

