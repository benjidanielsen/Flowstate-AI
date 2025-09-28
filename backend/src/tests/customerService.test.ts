import { CustomerService } from '../services/customerService';
import { PipelineStatus } from '../types';
import DatabaseManager from '../database';
import { runMigrations } from '../database/migrate';

describe('CustomerService', () => {
  let customerService: CustomerService;

  beforeAll(async () => {
    await DatabaseManager.getInstance().connect();
    await runMigrations();
    customerService = new CustomerService();
  });

  describe('createCustomer', () => {
    it('should create a new customer', async () => {
      const customerData = {
        name: 'Test Customer',
        email: 'test@example.com',
        status: PipelineStatus.LEAD
      };

      const customer = await customerService.createCustomer(customerData);

      expect(customer).toBeDefined();
      expect(customer.name).toBe(customerData.name);
      expect(customer.email).toBe(customerData.email);
      expect(customer.status).toBe(customerData.status);
      expect(customer.id).toBeDefined();
    });
  });

  describe('getAllCustomers', () => {
    it('should return all customers', async () => {
      const customers = await customerService.getAllCustomers();
      expect(Array.isArray(customers)).toBe(true);
    });
  });

  describe('moveCustomerToNextStage', () => {
    it('should move customer to next pipeline stage', async () => {
      const customerData = {
        name: 'Pipeline Test Customer',
        email: 'pipeline@example.com',
        status: PipelineStatus.LEAD
      };

      const customer = await customerService.createCustomer(customerData);
      const updatedCustomer = await customerService.moveCustomerToNextStage(customer.id);

      expect(updatedCustomer).toBeDefined();
      expect(updatedCustomer?.status).toBe(PipelineStatus.RELATIONSHIP);
    });
  });
});