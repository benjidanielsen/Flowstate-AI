import { InteractionService } from '../services/interactionService';
import { CustomerService } from '../services/customerService';
import { InteractionType, PipelineStatus } from '../types';
import DatabaseManager from '../database';
import { runMigrations } from '../database/migrate';

describe('InteractionService', () => {
  let interactionService: InteractionService;
  let customerService: CustomerService;
  let testCustomerId: string;

  beforeEach(async () => {
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

  afterEach(async () => {
    await DatabaseManager.getInstance().close();
  });

  describe('createInteraction', () => {
    it('should create a new interaction', async () => {
      const interactionData = {
        customer_id: testCustomerId, // Corrected to customer_id
        type: InteractionType.CALL,
        content: 'Called to follow up', // Corrected to content
        scheduled_for: new Date(), // Corrected to scheduled_for and Date object
        completed: false, // Added completed field
      };

      const interaction = await interactionService.createInteraction(interactionData);

      expect(interaction).toBeDefined();
      expect(interaction.customer_id).toBe(interactionData.customer_id); // Corrected to customer_id
      expect(interaction.type).toBe(interactionData.type);
      expect(interaction.content).toBe(interactionData.content); // Corrected to content
      expect(interaction.id).toBeDefined();
    });
  });

  describe('getInteractionsByCustomer', () => {
    it('should return all interactions for a given customer', async () => {
      // Log an interaction first to ensure there's something to retrieve
      await interactionService.createInteraction({
        customer_id: testCustomerId,
        type: InteractionType.NOTE,
        content: 'Test note for retrieval',
        scheduled_for: new Date(),
        completed: false,
      });

      const interactions = await interactionService.getInteractionsByCustomer(testCustomerId); // Correct method name
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
        content: 'Initial email sent',
        scheduled_for: new Date(),
        completed: false,
      };
      const createdInteraction = await interactionService.createInteraction(interactionData);

      const updatedContent = 'Follow-up email sent';
      const updatedInteraction = await interactionService.updateInteraction(createdInteraction.id, { content: updatedContent }); // Corrected to content

      expect(updatedInteraction).toBeDefined();
      expect(updatedInteraction?.content).toBe(updatedContent); // Corrected to content
      expect(updatedInteraction?.id).toBe(createdInteraction.id);
    });
  });

  describe('deleteInteraction', () => {
    it('should delete an interaction', async () => {
      const interactionData = {
        customer_id: testCustomerId,
        type: InteractionType.MEETING,
        content: 'Meeting scheduled',
        scheduled_for: new Date(),
        completed: false,
      };
      const createdInteraction = await interactionService.createInteraction(interactionData);

      await interactionService.deleteInteraction(createdInteraction.id);

      const deletedInteraction = await interactionService.getInteractionById(createdInteraction.id);
      expect(deletedInteraction).toBeNull(); // Expect null for not found
    });
  });
});

