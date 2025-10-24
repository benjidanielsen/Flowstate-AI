import { Request, Response } from 'express';
import { interactionService } from '../services/interactionService';

export const interactionController = {
  async createInteraction(req: Request, res: Response) {
    try {
      const { customer_id, type, content, notes, scheduled_for, completed } = req.body;
      const newInteraction = await interactionService.createInteraction({
        customer_id,
        type,
        content,
        notes,
        scheduled_for: scheduled_for ? new Date(scheduled_for) : undefined,
        completed,
      });
      res.status(201).json(newInteraction);
    } catch (error) {
      console.error("Error creating interaction:", error);
      res.status(500).json({ message: "Error creating interaction" });
    }
  },

  async getInteractionsByCustomerId(req: Request, res: Response) {
    try {
      const { customerId } = req.params;
      const interactions = await interactionService.getInteractionsByCustomer(customerId);
      res.status(200).json(interactions);
    } catch (error) {
      console.error("Error fetching interactions:", error);
      res.status(500).json({ message: "Error fetching interactions" });
    }
  },

  async getInteractionById(req: Request, res: Response) {
    try {
      const { id } = req.params;
      const interaction = await interactionService.getInteractionById(id);
      if (interaction) {
        res.status(200).json(interaction);
      } else {
        res.status(404).json({ message: "Interaction not found" });
      }
    } catch (error) {
      console.error("Error fetching interaction:", error);
      res.status(500).json({ message: "Error fetching interaction" });
    }
  },

  async updateInteraction(req: Request, res: Response) {
    try {
      const { id } = req.params;
      const { type, content, notes, scheduled_for, completed } = req.body;
      const updatedInteraction = await interactionService.updateInteraction(id, {
        type,
        content,
        notes,
        scheduled_for: scheduled_for ? new Date(scheduled_for) : undefined,
        completed,
      });
      if (updatedInteraction) {
        res.status(200).json(updatedInteraction);
      } else {
        res.status(404).json({ message: "Interaction not found" });
      }
    } catch (error) {
      console.error("Error updating interaction:", error);
      res.status(500).json({ message: "Error updating interaction" });
    }
  },

  async deleteInteraction(req: Request, res: Response) {
    try {
      const { id } = req.params;
      await interactionService.deleteInteraction(id);
      res.status(204).send();
    } catch (error) {
      console.error("Error deleting interaction:", error);
      res.status(500).json({ message: "Error deleting interaction" });
    }
  },
};
