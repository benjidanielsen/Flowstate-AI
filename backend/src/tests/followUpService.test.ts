import { FollowUpService } from '../services/followUpService';
import { CustomerService } from '../services/customerService';
import { ReminderService } from '../services/reminderService'; // Import ReminderService
import { PipelineStatus, ReminderType } from '../types';
import DatabaseManager from '../database';
import { runMigrations } from '../database/migrate';

describe('FollowUpService', () => {
  let followUpService: FollowUpService;
  let customerService: CustomerService;
  let reminderService: ReminderService; // Initialize ReminderService
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
    followUpService = new FollowUpService();
    customerService = new CustomerService();
    reminderService = new ReminderService(); // Instantiate ReminderService

    // Create a test customer for follow-ups
    const customerData = {
      name: 'Follow Up Test Customer',
      email: 'followup@example.com',
      status: PipelineStatus.PRESENTATION_SENT,
    };
    const customer = await customerService.createCustomer(customerData);
    testCustomerId = customer.id;
  });

  afterEach(async () => {
    await DatabaseManager.getInstance().close();
  });

  describe('createFollowUp', () => {
    it('should create a new follow-up for a customer', async () => {
      const initialReminders = await reminderService.getRemindersByCustomerId(testCustomerId);
      const initialFollowUpCount = initialReminders.filter(r => r.type === ReminderType.FOLLOW_UP).length;

      await followUpService.createFollowUp(testCustomerId, PipelineStatus.PRESENTATION_SENT);

      const newReminders = await reminderService.getRemindersByCustomerId(testCustomerId);
      const followUpReminders = newReminders.filter(r => r.type === ReminderType.FOLLOW_UP);
      expect(followUpReminders.length).toBe(initialFollowUpCount + 1);
      expect(followUpReminders[followUpReminders.length - 1].customer_id).toBe(testCustomerId);
      expect(followUpReminders[followUpReminders.length - 1].message).toBeDefined();
      expect(followUpReminders[followUpReminders.length - 1].scheduled_for).toBeDefined();
    });
  });

  describe('autoScheduleFollowUps', () => {
    it('should auto-schedule follow-ups for customers', async () => {
      // Ensure there are customers to schedule for
      await customerService.createCustomer({ name: 'Auto Schedule Test 1', email: 'auto1@example.com', status: PipelineStatus.NEW_LEAD });
      await customerService.createCustomer({ name: 'Auto Schedule Test 2', email: 'auto2@example.com', status: PipelineStatus.QUALIFIED });

      const scheduledCount = await followUpService.autoScheduleFollowUps();
      expect(scheduledCount).toBeGreaterThan(0);

      const allReminders = await reminderService.getAllReminders();
      expect(allReminders.some(r => r.type === ReminderType.FOLLOW_UP)).toBe(true);
    });
  });

  describe('getUpcomingFollowUps', () => {
    it('should return upcoming follow-ups', async () => {
      // Schedule a follow-up for the future
      await followUpService.createFollowUp(testCustomerId, PipelineStatus.FOLLOW_UP);

      const upcomingFollowUps = await followUpService.getUpcomingFollowUps(7); // Get follow-ups for next 7 days
      expect(Array.isArray(upcomingFollowUps)).toBe(true);
      expect(upcomingFollowUps.length).toBeGreaterThan(0);
      expect(upcomingFollowUps.some(fu => fu.customer_id === testCustomerId && fu.type === 'follow_up')).toBe(true);
    });
  });

  describe('markReminderCompleted (via ReminderService)', () => {
    it('should mark a follow-up reminder as complete', async () => {
      await followUpService.createFollowUp(testCustomerId, PipelineStatus.FOLLOW_UP);
      const reminders = await reminderService.getRemindersByCustomerId(testCustomerId);
      const followUpReminder = reminders.find(r => r.type === ReminderType.FOLLOW_UP);

      expect(followUpReminder).toBeDefined();
      if (!followUpReminder) {
        throw new Error("Follow-up reminder not found.");
      }
      expect(followUpReminder.completed).toBe(false);

      // Ensure followUpReminder.id is not null before passing it to markReminderCompleted
      if (followUpReminder.id === null || followUpReminder.id === undefined) {
        throw new Error("Follow-up reminder ID is null or undefined.");
      }

      const completedReminder = await reminderService.markReminderCompleted(followUpReminder.id);

      expect(completedReminder).not.toBeNull();
      if (completedReminder) {
        expect(completedReminder.completed).toBe(true);
      }
    });
  });
});

