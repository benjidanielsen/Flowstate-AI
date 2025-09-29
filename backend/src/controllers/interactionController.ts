import { Request, Response } from 'express';
import { InteractionService } from '../services/interactionService';

export class InteractionController {
  private readonly interactionService: InteractionService;

  constructor() {
    this.interactionService = new InteractionService();
  }

  getInteractionsByCustomer = async (req: Request, res: Response) => {
    try {
      const { customerId } = req.params;
      const interactions = await this.interactionService.getInteractionsByCustomer(customerId);
      res.json(interactions);
    } catch (error) {
      console.error('Error fetching interactions:', error);
      res.status(500).json({ error: 'Internal server error' });
    }
  };

  createInteraction = async (req: Request, res: Response) => {
    try {
      const interactionData = req.body;
      
      if (!interactionData.customer_id || !interactionData.type || !interactionData.content) {
        return res.status(400).json({ error: 'customer_id, type, and content are required' });
      }
      
      const interaction = await this.interactionService.createInteraction(interactionData);
      res.status(201).json(interaction);
    } catch (error) {
      console.error('Error creating interaction:', error);
      res.status(500).json({ error: 'Internal server error' });
    }
  };

  updateInteraction = async (req: Request, res: Response) => {
    try {
      const { id } = req.params;
      const updates = req.body;
      
      const interaction = await this.interactionService.updateInteraction(id, updates);
      
      if (!interaction) {
        return res.status(404).json({ error: 'Interaction not found' });
      }
      
      res.json(interaction);
    } catch (error) {
      console.error('Error updating interaction:', error);
      res.status(500).json({ error: 'Internal server error' });
    }
  };

  deleteInteraction = async (req: Request, res: Response) => {
    try {
      const { id } = req.params;
      const deleted = await this.interactionService.deleteInteraction(id);
      
      if (!deleted) {
        return res.status(404).json({ error: 'Interaction not found' });
      }
      
      res.status(204).send();
    } catch (error) {
      console.error('Error deleting interaction:', error);
      res.status(500).json({ error: 'Internal server error' });
    }
  };

  completeInteraction = async (req: Request, res: Response) => {
    try {
      const { id } = req.params;
      const interaction = await this.interactionService.updateInteraction(id, { completed: true });

      if (!interaction) {
        return res.status(404).json({ error: 'Interaction not found' });
      }

      // Optionally log event via eventLogService (already triggered by service.create/update)
      res.json(interaction);
    } catch (error) {
      console.error('Error completing interaction:', error);
      res.status(500).json({ error: 'Internal server error' });
    }
  };

  getUpcomingInteractions = async (req: Request, res: Response) => {
    try {
      const limit = parseInt(req.query.limit as string) || 20;
      const interactions = await this.interactionService.getUpcomingInteractions(limit);
      res.json(interactions);
    } catch (error) {
      console.error('Error fetching upcoming interactions:', error);
      res.status(500).json({ error: 'Internal server error' });
    }
  };
}