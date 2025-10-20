import { Request, Response } from 'express';
import { ReminderService } from '../services/reminderService';
import Joi from 'joi';
import { ReminderType } from '../types';

const createSchema = Joi.object({
  customer_id: Joi.string().required(),
  type: Joi.string().valid(...Object.values(ReminderType)).required(),
  message: Joi.string().allow('').optional(),
  scheduled_for: Joi.date().iso().required(),
  repeat_interval: Joi.string().allow(null, '').optional(),
});

const updateSchema = Joi.object({
  type: Joi.string().valid(...Object.values(ReminderType)).optional(),
  message: Joi.string().allow('').optional(),
  scheduled_for: Joi.date().iso().optional(),
  completed: Joi.boolean().optional(),
  repeat_interval: Joi.string().allow(null, '').optional(),
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
        scheduled_for: new Date(value.scheduled_for),
        repeat_interval: value.repeat_interval,
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

  getRemindersByCustomerId = async (req: Request, res: Response) => {
    try {
      const { customerId } = req.params;
      const reminders = await this.reminderService.getRemindersByCustomerId(customerId);
      res.json(reminders);
    } catch (err) {
      console.error('Error getting reminders by customer ID:', err);
      res.status(500).json({ error: 'Internal server error' });
    }
  };

  update = async (req: Request, res: Response) => {
    try {
      const { id } = req.params;
      const { error, value } = updateSchema.validate(req.body, { abortEarly: false });
      if (error) return res.status(400).json({ error: 'Invalid payload', details: error.details });

      const updatedReminder = await this.reminderService.updateReminder(id, value);
      if (!updatedReminder) return res.status(404).json({ error: 'Reminder not found' });
      res.status(200).json(updatedReminder);
    } catch (err) {
      console.error('Error updating reminder:', err);
      res.status(500).json({ error: 'Internal server error' });
    }
  };

  delete = async (req: Request, res: Response) => {
    try {
      const { id } = req.params;
      const deleted = await this.reminderService.deleteReminder(id);
      if (!deleted) return res.status(404).json({ error: 'Reminder not found' });
      res.status(204).send(); // No content for successful deletion
    } catch (err) {
      console.error('Error deleting reminder:', err);
      res.status(500).json({ error: 'Internal server error' });
    }
  };
}

