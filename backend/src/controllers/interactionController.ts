import { Request, Response } from 'express';
import { interactionService } from '../services/interactionService';

function toDate(value: unknown): Date | undefined {
  if (!value) return undefined;
  const date = new Date(value as string);
  return Number.isNaN(date.getTime()) ? undefined : date;
}

export const interactionController = {
  async createInteraction(req: Request, res: Response) {
    try {
      const customerId = (req.body.customer_id || req.params.customerId || req.params.id) as string | undefined;
      if (!customerId) {
        return res.status(400).json({ message: 'customer_id is required' });
      }

      const { type } = req.body;
      if (!type) {
        return res.status(400).json({ message: 'Interaction type is required' });
      }

      const interaction = await interactionService.create({
        customer_id: customerId,
        type,
        summary: req.body.summary,
        content: req.body.content,
        notes: req.body.notes,
        interaction_date: toDate(req.body.interaction_date) ?? new Date(),
        scheduled_for: toDate(req.body.scheduled_for) ?? null,
        completed: typeof req.body.completed === 'boolean' ? req.body.completed : undefined,
      });

      res.status(201).json(interaction);
    } catch (error) {
      console.error('Error creating interaction:', error);
      res.status(500).json({ message: 'Error creating interaction' });
    }
  },

  async createInteractionForCustomer(req: Request, res: Response) {
    return this.createInteraction(req, res);
  },

  async getInteractionsByCustomerId(req: Request, res: Response) {
    try {
      const customerId = (req.params.customerId || req.params.id) as string | undefined;
      if (!customerId) {
        return res.status(400).json({ message: 'customerId is required' });
      }
      const interactions = await interactionService.getByCustomerId(customerId);
      res.status(200).json(interactions);
    } catch (error) {
      console.error('Error fetching interactions:', error);
      res.status(500).json({ message: 'Error fetching interactions' });
    }
  },

  async getInteractionById(req: Request, res: Response) {
    try {
      const { id } = req.params;
      const interaction = await interactionService.getById(id);
      if (interaction) {
        res.status(200).json(interaction);
      } else {
        res.status(404).json({ message: 'Interaction not found' });
      }
    } catch (error) {
      console.error('Error fetching interaction:', error);
      res.status(500).json({ message: 'Error fetching interaction' });
    }
  },

  async updateInteraction(req: Request, res: Response) {
    try {
      const { id } = req.params;
      const updates = {
        customer_id: req.body.customer_id,
        type: req.body.type,
        summary: req.body.summary,
        content: req.body.content,
        notes: req.body.notes,
        interaction_date: toDate(req.body.interaction_date),
        scheduled_for: req.body.scheduled_for === null ? null : toDate(req.body.scheduled_for),
        completed: typeof req.body.completed === 'boolean' ? req.body.completed : undefined,
      };

      const updatedInteraction = await interactionService.update(id, updates);
      if (updatedInteraction) {
        res.status(200).json(updatedInteraction);
      } else {
        res.status(404).json({ message: 'Interaction not found' });
      }
    } catch (error) {
      console.error('Error updating interaction:', error);
      res.status(500).json({ message: 'Error updating interaction' });
    }
  },

  async updateInteractionForCustomer(req: Request, res: Response) {
    const interactionId = req.params.interactionId as string | undefined;
    if (!interactionId) {
      return res.status(400).json({ message: 'interactionId is required' });
    }
    req.params.id = interactionId;
    return this.updateInteraction(req, res);
  },

  async deleteInteraction(req: Request, res: Response) {
    try {
      const { id } = req.params;
      await interactionService.delete(id);
      res.status(204).send();
    } catch (error) {
      console.error('Error deleting interaction:', error);
      res.status(500).json({ message: 'Error deleting interaction' });
    }
  },

  async deleteInteractionForCustomer(req: Request, res: Response) {
    const interactionId = req.params.interactionId as string | undefined;
    if (!interactionId) {
      return res.status(400).json({ message: 'interactionId is required' });
    }
    req.params.id = interactionId;
    return this.deleteInteraction(req, res);
  },

  async getUpcomingInteractions(req: Request, res: Response) {
    try {
      const limit = req.query.limit ? Math.max(parseInt(req.query.limit as string, 10), 1) : 5;
      const interactions = await interactionService.getUpcoming(limit);
      res.status(200).json(interactions);
    } catch (error) {
      console.error('Error fetching upcoming interactions:', error);
      res.status(500).json({ message: 'Error fetching upcoming interactions' });
    }
  },

  async completeInteraction(req: Request, res: Response) {
    try {
      const { id } = req.params;
      const interaction = await interactionService.markCompleted(id);
      if (!interaction) {
        return res.status(404).json({ message: 'Interaction not found' });
      }
      res.status(200).json(interaction);
    } catch (error) {
      console.error('Error completing interaction:', error);
      res.status(500).json({ message: 'Error completing interaction' });
    }
  },
};
