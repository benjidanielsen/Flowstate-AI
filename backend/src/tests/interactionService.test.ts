import { InteractionService } from '../services/interactionService';
import { CustomerService } from '../services/customerService';
import { InteractionType, PipelineStatus } from '../types';
import DatabaseManager from '../database';
import { runMigrations } from '../database/migrate';

describe('InteractionService', () => {
  let interactionService: InteractionService;
  let customerService: CustomerService;
  let testCustomerId: number;

  beforeAll(async () => {
    await DatabaseManager.getInstance().connect();
    await runMigrations();
    interactionService = new InteractionService();
    customerService = new CustomerService();

    // Create a test customer for interactions
    const customerData = {
      name: 'Interaction Test Customer',
      email: 'interaction@example.com',
      status: PipelineStatus.NEW_LEAD,
    };
    const customer = await customerService.createCustomer(customerData);
    testCustomerId = customer.id;
  });

  describe('createInteraction', () => {
    it('should create a new interaction', async () => {
      const interactionData = {
        customerId: testCustomerId,
        type: InteractionType.CALL,
        notes: 'Called to follow up',
        scheduledAt: new Date().toISOString(),
      };

      const interaction = await interactionService.createInteraction(interactionData);

      expect(interaction).toBeDefined();
      expect(interaction.customerId).toBe(interactionData.customerId);
      expect(interaction.type).toBe(interactionData.type);
      expect(interaction.notes).toBe(interactionData.notes);
      expect(interaction.id).toBeDefined();
    });
  });

  describe('getInteractionsByCustomerId', () => {
    it('should return all interactions for a given customer', async () => {
      const interactions = await interactionService.getInteractionsByCustomerId(testCustomerId);
      expect(Array.isArray(interactions)).toBe(true);
      expect(interactions.length).toBeGreaterThan(0);
      expect(interactions[0].customerId).toBe(testCustomerId);
    });
  });

  describe('updateInteraction', () => {
    it('should update an existing interaction', async () => {
      const interactionData = {
        customerId: testCustomerId,
        type: InteractionType.EMAIL,
        notes: 'Initial email sent',
        scheduledAt: new Date().toISOString(),
      };
      const createdInteraction = await interactionService.createInteraction(interactionData);

      const updatedNotes = 'Follow-up email sent';
      const updatedInteraction = await interactionService.updateInteraction(createdInteraction.id, { notes: updatedNotes });

      expect(updatedInteraction).toBeDefined();
      expect(updatedInteraction?.notes).toBe(updatedNotes);
      expect(updatedInteraction?.id).toBe(createdInteraction.id);
    });
  });

  describe('deleteInteraction', () => {
    it('should delete an interaction', async () => {
      const interactionData = {
        customerId: testCustomerId,
        type: InteractionType.MEETING,
        notes: 'Meeting scheduled',
        scheduledAt: new Date().toISOString(),
      };
      const createdInteraction = await interactionService.createInteraction(interactionData);

      await interactionService.deleteInteraction(createdInteraction.id);

      const deletedInteraction = await interactionService.getInteractionById(createdInteraction.id);
      expect(deletedInteraction).toBeUndefined();
    });
  });
});

