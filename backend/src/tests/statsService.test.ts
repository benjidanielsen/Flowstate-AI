import { StatsService } from '../services/statsService';
import { CustomerService } from '../services/customerService';
import { PipelineStatus } from '../types';
import DatabaseManager from '../database';
import { runMigrations } from '../database/migrate';

describe('StatsService', () => {
  let statsService: StatsService;
  let customerService: CustomerService;

  beforeEach(async () => {
    await DatabaseManager.getInstance().connect();
    await runMigrations();
    statsService = new StatsService();
    customerService = new CustomerService();

    // Clear existing customers and create fresh ones for consistent stats testing
    // This is a simplification; in a real scenario, you might have a dedicated test database or transaction rollback
    await DatabaseManager.getInstance().getDb().run("DELETE FROM customers");

    await customerService.createCustomer({ name: 'Stats Customer 1', email: 'stats1@example.com', status: PipelineStatus.NEW_LEAD });
    await customerService.createCustomer({ name: 'Stats Customer 2', email: 'stats2@example.com', status: PipelineStatus.WARMING_UP });
    await customerService.createCustomer({ name: 'Stats Customer 3', email: 'stats3@example.com', status: PipelineStatus.WARMING_UP });
    await customerService.createCustomer({ name: 'Stats Customer 4', email: 'stats4@example.com', status: PipelineStatus.INVITED });
  });

  afterEach(async () => {
    await DatabaseManager.getInstance().close();
  });

  describe('getPipelineStats', () => {
    it('should return correct pipeline statistics', async () => {
      const stats = await statsService.getPipelineStats();

      expect(stats).toBeDefined();
      expect(stats.totalCustomers).toBe(4);
      expect(stats.statusCounts[PipelineStatus.NEW_LEAD]).toBe(1);
      expect(stats.statusCounts[PipelineStatus.WARMING_UP]).toBe(2);
      expect(stats.statusCounts[PipelineStatus.INVITED]).toBe(1);
      expect(stats.statusCounts[PipelineStatus.PRESENTATION_SENT]).toBe(0);
      // Add more assertions for other statuses as needed
    });
  });

  // Add more tests for other stats service functionalities as needed
});

