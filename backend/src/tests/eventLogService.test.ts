import { EventLogService } from '../services/eventLogService';
import { CustomerService } from '../services/customerService';
import { PipelineStatus } from '../types';
import DatabaseManager from '../database';
import { runMigrations } from '../database/migrate';

describe('EventLogService', () => {
  let eventLogService: EventLogService;
  let customerService: CustomerService;
  let testCustomerId: string; // Changed to string as customer.id is string

  beforeEach(async () => {
    await DatabaseManager.getInstance().connect();
    await runMigrations();
    eventLogService = new EventLogService();
    customerService = new CustomerService();

    // Create a test customer for event logging
    const customerData = {
      name: 'Event Log Test Customer',
      email: 'eventlog@example.com',
      status: PipelineStatus.LEAD,
    };
    const customer = await customerService.createCustomer(customerData);
    testCustomerId = customer.id;
  });

  afterEach(async () => {
    await DatabaseManager.getInstance().close();
  });

  describe('logEvent', () => {
    it('should log a new event', async () => {
      const eventType = 'CUSTOMER_CREATED'; // Use string for eventType
      const eventData = {
        description: 'New customer created for testing',
        metadata: { source: 'test_script' },
      };

      const event = await eventLogService.logEvent(eventType, eventData, testCustomerId);

      expect(event).toBeDefined();
      expect(event.customer_id).toBe(testCustomerId); // Use customer_id
      expect(event.event_type).toBe(eventType); // Use event_type
      expect(event.event_data).toEqual(eventData); // Use event_data
      expect(event.id).toBeDefined();
    });
  });

  describe('getEventsByCustomerId', () => {
    it('should return all events for a given customer', async () => {
      // Log an event first to ensure there's something to retrieve
      const eventType = 'CUSTOMER_VIEWED';
      const eventData = { viewer: 'admin' };
      await eventLogService.logEvent(eventType, eventData, testCustomerId);

      const events = await eventLogService.getEventsByCustomer(testCustomerId); // Correct method name
      expect(Array.isArray(events)).toBe(true);
      expect(events.length).toBeGreaterThan(0);
      expect(events[0].customer_id).toBe(testCustomerId);
    });
  });

  describe('getAllEvents', () => {
    it('should return all events in the system', async () => {
      const events = await eventLogService.getAllEvents();
      expect(Array.isArray(events)).toBe(true);
      expect(events.length).toBeGreaterThan(0);
    });
  });
});

