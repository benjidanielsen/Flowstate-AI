import { Request, Response } from 'express';
import { interactionService } from '../services/interactionService';

export const interactionController = {
  async createInteraction(req: Request, res: Response) {
    try {
      const { customer_id, type, summary, notes, interaction_date } = req.body;
      const newInteraction = await interactionService.create({
        customer_id,
        type,
        summary,
        notes,
        interaction_date: interaction_date ? new Date(interaction_date) : new Date(),
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
      const interactions = await interactionService.getByCustomerId(customerId);
      res.status(200).json(interactions);
    } catch (error) {
      console.error("Error fetching interactions:", error);
      res.status(500).json({ message: "Error fetching interactions" });
    }
  },

  async getInteractionById(req: Request, res: Response) {
    try {
      const { id } = req.params;
      const interaction = await interactionService.getById(id);
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
      const updates = req.body;
      const updatedInteraction = await interactionService.update(id, updates);
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
      await interactionService.delete(id);
      res.status(204).send();
    } catch (error) {
      console.error("Error deleting interaction:", error);
      res.status(500).json({ message: "Error deleting interaction" });
    }
  },
};
