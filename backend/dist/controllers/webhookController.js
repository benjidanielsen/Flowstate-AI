"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.WebhookController = void 0;
const eventLogService_1 = require("../services/eventLogService");
class WebhookController {
    constructor() {
        this.eventLogService = new eventLogService_1.EventLogService();
        // Example: DM webhook from social platforms -> log event
        this.dm = async (req, res) => {
            try {
                const payload = req.body || {};
                const customerId = payload.customer_id || payload.contact_id || undefined;
                const source = payload.source || payload.platform || undefined; // ig|messenger|whatsapp|...
                const event = await this.eventLogService.logEvent('DM_STARTED', { payload, source }, customerId, payload.user_id);
                res.status(202).json({ ok: true, event_id: event.id });
            }
            catch (err) {
                console.error('Webhook DM error:', err);
                res.status(500).json({ error: 'Internal server error' });
            }
        };
        // Stub for Meta CAPI lead capture (logs event only here)
        this.capiLead = async (req, res) => {
            try {
                const payload = req.body || {};
                const customerId = payload.customer_id || undefined;
                const event = await this.eventLogService.logEvent('LEAD_QUALIFIED', { payload, source: 'ads' }, customerId, payload.user_id);
                res.status(202).json({ ok: true, event_id: event.id });
            }
            catch (err) {
                console.error('CAPI lead error:', err);
                res.status(500).json({ error: 'Internal server error' });
            }
        };
    }
}
exports.WebhookController = WebhookController;
//# sourceMappingURL=webhookController.js.map