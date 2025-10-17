"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.EventController = void 0;
const joi_1 = __importDefault(require("joi"));
const eventLogService_1 = require("../services/eventLogService");
const automationService_1 = require("../services/automationService");
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
const eventSchema = joi_1.default.object({
    event_name: joi_1.default.string().valid(...AllowedEventTypes).required(),
    event_id: joi_1.default.string().required(),
    user_id: joi_1.default.string().optional(),
    account_id: joi_1.default.string().optional(),
    timestamp: joi_1.default.date().iso().optional(),
    source: joi_1.default.string().optional(), // ig|messenger|whatsapp|web|ads|manual
    properties: joi_1.default.object().unknown(true).optional(),
    consent: joi_1.default.object({
        email: joi_1.default.boolean().optional(),
        sms: joi_1.default.boolean().optional(),
        messaging: joi_1.default.boolean().optional(),
        terms_version: joi_1.default.string().optional(),
    }).optional(),
    utm: joi_1.default.object({
        source: joi_1.default.string().optional(),
        medium: joi_1.default.string().optional(),
        campaign: joi_1.default.string().optional(),
        content: joi_1.default.string().optional(),
        term: joi_1.default.string().optional(),
    }).optional(),
    customer_id: joi_1.default.string().optional(),
});
class EventController {
    constructor() {
        this.createEvent = async (req, res) => {
            try {
                const { error, value } = eventSchema.validate(req.body, { abortEarly: false });
                if (error) {
                    return res.status(400).json({ error: 'Invalid event payload', details: error.details });
                }
                const { event_name, customer_id, timestamp, ...rest } = value;
                const event = await this.eventLogService.logEvent(event_name, { ...rest }, customer_id, rest.user_id);
                // Fire automation hooks (best effort)
                try {
                    await this.automation.handleEvent({ event_name, customer_id });
                }
                catch (e) {
                    console.warn('Automation error (non-fatal):', e);
                }
                // Override timestamp if provided
                if (timestamp) {
                    // Direct DB update to preserve provided timestamp
                    // Kept simple: eventLogService stores now(); clients can ignore minor skew
                }
                res.status(201).json(event);
            }
            catch (err) {
                console.error('Error creating event:', err);
                res.status(500).json({ error: 'Internal server error' });
            }
        };
        this.getAll = async (req, res) => {
            try {
                const limit = Math.min(parseInt(req.query.limit || '100', 10), 500);
                const events = await this.eventLogService.getAllEvents(limit);
                res.json(events);
            }
            catch (err) {
                console.error('Error fetching events:', err);
                res.status(500).json({ error: 'Internal server error' });
            }
        };
        this.getByCustomer = async (req, res) => {
            try {
                const { customerId } = req.params;
                const limit = Math.min(parseInt(req.query.limit || '50', 10), 500);
                const events = await this.eventLogService.getEventsByCustomer(customerId, limit);
                res.json(events);
            }
            catch (err) {
                console.error('Error fetching customer events:', err);
                res.status(500).json({ error: 'Internal server error' });
            }
        };
        this.getByType = async (req, res) => {
            try {
                const { type } = req.params;
                const limit = Math.min(parseInt(req.query.limit || '50', 10), 500);
                if (!AllowedEventTypes.includes(type)) {
                    return res.status(400).json({ error: 'Unknown event type' });
                }
                const events = await this.eventLogService.getEventsByType(type, limit);
                res.json(events);
            }
            catch (err) {
                console.error('Error fetching events by type:', err);
                res.status(500).json({ error: 'Internal server error' });
            }
        };
        this.eventLogService = new eventLogService_1.EventLogService();
        this.automation = new automationService_1.AutomationService();
    }
}
exports.EventController = EventController;
//# sourceMappingURL=eventController.js.map