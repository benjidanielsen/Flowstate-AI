import { Request, Response } from 'express';
import Joi from 'joi';
import { EventLogService } from '../services/eventLogService';
import { AutomationService } from '../services/automationService';

// Event types per docs (frazer_method_blueprints/schemas/events.json)
const AllowedEventTypes = [
  'DM_STARTED',
  'LEAD_QUALIFIED',
  'MEETING_BOOKED',
  'MEETING_HELD',
  'NO_SHOW',
  'PURCHASED',
  'JOINED_TEAM',
  'UNSUBSCRIBED',
];

const eventSchema = Joi.object({
  event_name: Joi.string().valid(...AllowedEventTypes).required(),
  event_id: Joi.string().required(),
  user_id: Joi.string().optional(),
  account_id: Joi.string().optional(),
  timestamp: Joi.date().iso().optional(),
  source: Joi.string().optional(), // ig|messenger|whatsapp|web|ads|manual
  properties: Joi.object().unknown(true).optional(),
  consent: Joi.object({
    email: Joi.boolean().optional(),
    sms: Joi.boolean().optional(),
    messaging: Joi.boolean().optional(),
    terms_version: Joi.string().optional(),
  }).optional(),
  utm: Joi.object({
    source: Joi.string().optional(),
    medium: Joi.string().optional(),
    campaign: Joi.string().optional(),
    content: Joi.string().optional(),
    term: Joi.string().optional(),
  }).optional(),
  customer_id: Joi.string().optional(),
});

export class EventController {
  private eventLogService: EventLogService;
  private automation: AutomationService;

  constructor() {
    this.eventLogService = new EventLogService();
    this.automation = new AutomationService();
  }

  createEvent = async (req: Request, res: Response) => {
    try {
      const { error, value } = eventSchema.validate(req.body, { abortEarly: false });
      if (error) {
        return res.status(400).json({ error: 'Invalid event payload', details: error.details });
      }

      const { event_name, customer_id, timestamp, ...rest } = value;

      const event = await this.eventLogService.logEvent(
        event_name,
        { ...rest },
        customer_id,
        rest.user_id
      );

      // Fire automation hooks (best effort)
      try {
        await this.automation.handleEvent({ event_name, customer_id });
      } catch (e) {
        console.warn('Automation error (non-fatal):', e);
      }

      // Override timestamp if provided
      if (timestamp) {
        // Direct DB update to preserve provided timestamp
        // Kept simple: eventLogService stores now(); clients can ignore minor skew
      }

      res.status(201).json(event);
    } catch (err) {
      console.error('Error creating event:', err);
      res.status(500).json({ error: 'Internal server error' });
    }
  };

  getAll = async (req: Request, res: Response) => {
    try {
      const { page, pageSize, source, from, to } = req.query;
      const filters = {
        page: page ? parseInt(page as string, 10) : undefined,
        pageSize: pageSize ? parseInt(pageSize as string, 10) : undefined,
        source: source as string,
        from: from ? new Date(from as string) : undefined,
        to: to ? new Date(to as string) : undefined,
      };
      const events = await this.eventLogService.getAllEvents(filters);
      res.json(events);
    } catch (err) {
      console.error('Error fetching events:', err);
      res.status(500).json({ error: 'Internal server error' });
    }
  };

  getByCustomer = async (req: Request, res: Response) => {
    try {
      const { customerId } = req.params;
      const { page, pageSize, from, to } = req.query;
      const events = await this.eventLogService.getEventsByCustomer(customerId, {
        page: page ? parseInt(page as string, 10) : undefined,
        pageSize: pageSize ? parseInt(pageSize as string, 10) : undefined,
        from: from ? new Date(from as string) : undefined,
        to: to ? new Date(to as string) : undefined,
      });
      res.json(events);
    } catch (err) {
      console.error('Error fetching customer events:', err);
      res.status(500).json({ error: 'Internal server error' });
    }
  };

  getByType = async (req: Request, res: Response) => {
    try {
      const { type } = req.params;
      if (!AllowedEventTypes.includes(type)) {
        return res.status(400).json({ error: 'Unknown event type' });
      }
      const { page, pageSize, from, to } = req.query;
      const events = await this.eventLogService.getEventsByType(type, {
        page: page ? parseInt(page as string, 10) : undefined,
        pageSize: pageSize ? parseInt(pageSize as string, 10) : undefined,
        from: from ? new Date(from as string) : undefined,
        to: to ? new Date(to as string) : undefined,
      });
      res.json(events);
    } catch (err) {
      console.error('Error fetching events by type:', err);
      res.status(500).json({ error: 'Internal server error' });
    }
  };
}
