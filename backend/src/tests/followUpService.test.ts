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
      expect(initialReminders.length).toBe(0);

      await followUpService.createFollowUp(testCustomerId, PipelineStatus.PRESENTATION_SENT);

      const newReminders = await reminderService.getRemindersByCustomerId(testCustomerId);
      expect(newReminders.length).toBe(1);
      expect(newReminders[0].customer_id).toBe(testCustomerId);
      expect(newReminders[0].type).toBe(ReminderType.FOLLOW_UP);
      expect(newReminders[0].message).toBeDefined();
      expect(newReminders[0].scheduled_for).toBeDefined();
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
      expect(followUpReminder?.completed).toBe(false);

      const completedReminder = await reminderService.markReminderCompleted(followUpReminder!.id);

      expect(completedReminder).toBeDefined();
      expect(completedReminder?.completed).toBe(true);
    });
  });
});

