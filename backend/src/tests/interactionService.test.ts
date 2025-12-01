import { interactionService } from '../services/interactionService';
import { CustomerService } from '../services/customerService';
import { InteractionType, PipelineStatus } from '../types';
import DatabaseManager from '../database';
import { runMigrations } from '../database/migrate';

describe('InteractionService', () => {
  let customerService: CustomerService;
  let testCustomerId: string;

  beforeEach(async () => {
    await DatabaseManager.getInstance().connect();
    await runMigrations();
    customerService = new CustomerService();

    // Create a test customer for interactions
    const customerData = {
      name: 'Interaction Test Customer',
      email: 'interaction@example.com',
      status: PipelineStatus.LEAD,
    };
    const customer = await customerService.createCustomer(customerData);
    testCustomerId = customer.id;
  });

  afterEach(async () => {
    await DatabaseManager.getInstance().close();
  });

  describe('createInteraction', () => {
    it('should create a new interaction', async () => {
      const interactionData = {
        customer_id: testCustomerId,
        type: InteractionType.CALL,
        summary: 'Called to follow up',
        notes: 'Discussed next steps',
        interaction_date: new Date(),
      };

      const interaction = await interactionService.create(interactionData);

      expect(interaction).toBeDefined();
      expect(interaction.customer_id).toBe(interactionData.customer_id); // Corrected to customer_id
      expect(interaction.type).toBe(interactionData.type);
      expect(interaction.summary).toBe(interactionData.summary);
      expect(interaction.id).toBeDefined();
    });
  });

  describe('getInteractionsByCustomer', () => {
    it('should return all interactions for a given customer', async () => {
      // Log an interaction first to ensure there's something to retrieve
      await interactionService.create({
        customer_id: testCustomerId,
        type: InteractionType.NOTE,
        summary: 'Test note for retrieval',
        notes: 'ensure retrieval works',
        interaction_date: new Date(),
      });

      const interactions = await interactionService.getByCustomerId(testCustomerId);
      expect(Array.isArray(interactions)).toBe(true);
      expect(interactions.length).toBeGreaterThan(0);
      expect(interactions[0].customer_id).toBe(testCustomerId);
    });
  });

  describe('updateInteraction', () => {
    it('should update an existing interaction', async () => {
      const interactionData = {
        customer_id: testCustomerId,
        type: InteractionType.EMAIL,
        summary: 'Initial email sent',
        notes: 'first touch',
        interaction_date: new Date(),
      };
      const createdInteraction = await interactionService.create(interactionData);

      const updatedSummary = 'Follow-up email sent';
      const updatedInteraction = await interactionService.update(createdInteraction.id, { summary: updatedSummary });

      expect(updatedInteraction).toBeDefined();
      expect(updatedInteraction?.summary).toBe(updatedSummary);
      expect(updatedInteraction?.id).toBe(createdInteraction.id);
    });
  });

  describe('deleteInteraction', () => {
    it('should delete an interaction', async () => {
      const interactionData = {
        customer_id: testCustomerId,
        type: InteractionType.MEETING,
        summary: 'Meeting scheduled',
        notes: 'confirm availability',
        interaction_date: new Date(),
      };
      const createdInteraction = await interactionService.create(interactionData);

      await interactionService.delete(createdInteraction.id);

      const deletedInteraction = await interactionService.getById(createdInteraction.id);
      expect(deletedInteraction).toBeUndefined();
    });
  });
});

