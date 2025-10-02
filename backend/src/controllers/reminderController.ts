import { Request, Response } from 'express';
import { ReminderService } from '../services/reminderService';
import Joi from 'joi';

const createSchema = Joi.object({
  customer_id: Joi.string().required(),
  type: Joi.string().required(),
  message: Joi.string().allow('').optional(),
  scheduled_for: Joi.date().iso().required()
});

export class ReminderController {
  private reminderService = new ReminderService();

  listDue = async (_req: Request, res: Response) => {
    try {
      const due = await this.reminderService.getDueReminders();
      res.json(due);
    } catch (err) {
      console.error('Error listing due reminders:', err);
      res.status(500).json({ error: 'Internal server error' });
    }
  };

  create = async (req: Request, res: Response) => {
    try {
      const { error, value } = createSchema.validate(req.body, { abortEarly: false });
      if (error) return res.status(400).json({ error: 'Invalid payload', details: error.details });
      const created = await this.reminderService.createReminder({
        customer_id: value.customer_id,
        type: value.type,
        message: value.message,
        scheduled_for: new Date(value.scheduled_for)
      });
      res.status(201).json(created);
    } catch (err) {
      console.error('Error creating reminder:', err);
      res.status(500).json({ error: 'Internal server error' });
    }
  };

  complete = async (req: Request, res: Response) => {
    try {
      const reminder = await this.reminderService.markReminderCompleted(req.params.id);
      if (!reminder) return res.status(404).json({ error: 'Reminder not found' });
      res.status(200).json(reminder);
    } catch (err) {
      console.error('Error completing reminder:', err);
      res.status(500).json({ error: 'Internal server error' });
    }
  };
}

