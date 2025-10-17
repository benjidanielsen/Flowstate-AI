import { Request, Response } from 'express';
import { EventLogService } from '../services/eventLogService';

export class WebhookController {
  private eventLogService = new EventLogService();

  // Example: DM webhook from social platforms -> log event
  dm = async (req: Request, res: Response) => {
    try {
      const payload = req.body || {};
      const customerId: string | undefined = payload.customer_id || payload.contact_id || undefined;
      const source: string | undefined = payload.source || payload.platform || undefined; // ig|messenger|whatsapp|...

      const event = await this.eventLogService.logEvent(
        'DM_STARTED',
        { payload, source },
        customerId,
        payload.user_id
      );

      res.status(202).json({ ok: true, event_id: event.id });
    } catch (err) {
      console.error('Webhook DM error:', err);
      res.status(500).json({ error: 'Internal server error' });
    }
  };

  // Stub for Meta CAPI lead capture (logs event only here)
  capiLead = async (req: Request, res: Response) => {
    try {
      const payload = req.body || {};
      const customerId: string | undefined = payload.customer_id || undefined;
      const event = await this.eventLogService.logEvent(
        'LEAD_QUALIFIED',
        { payload, source: 'ads' },
        customerId,
        payload.user_id
      );
      res.status(202).json({ ok: true, event_id: event.id });
    } catch (err) {
      console.error('CAPI lead error:', err);
      res.status(500).json({ error: 'Internal server error' });
    }
  };
}

