"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.ReminderController = void 0;
const reminderService_1 = require("../services/reminderService");
const joi_1 = __importDefault(require("joi"));
const createSchema = joi_1.default.object({
    customer_id: joi_1.default.string().required(),
    type: joi_1.default.string().required(),
    message: joi_1.default.string().allow('').optional(),
    scheduled_for: joi_1.default.date().iso().required()
});
class ReminderController {
    constructor() {
        this.reminderService = new reminderService_1.ReminderService();
        this.listDue = async (_req, res) => {
            try {
                const due = await this.reminderService.getDueReminders();
                res.json(due);
            }
            catch (err) {
                console.error('Error listing due reminders:', err);
                res.status(500).json({ error: 'Internal server error' });
            }
        };
        this.create = async (req, res) => {
            try {
                const { error, value } = createSchema.validate(req.body, { abortEarly: false });
                if (error)
                    return res.status(400).json({ error: 'Invalid payload', details: error.details });
                const created = await this.reminderService.createReminder({
                    customer_id: value.customer_id,
                    type: value.type,
                    message: value.message,
                    scheduled_for: new Date(value.scheduled_for)
                });
                res.status(201).json(created);
            }
            catch (err) {
                console.error('Error creating reminder:', err);
                res.status(500).json({ error: 'Internal server error' });
            }
        };
        this.complete = async (req, res) => {
            try {
                const ok = await this.reminderService.completeReminder(req.params.id);
                if (!ok)
                    return res.status(404).json({ error: 'Reminder not found' });
                res.status(200).json({ ok: true });
            }
            catch (err) {
                console.error('Error completing reminder:', err);
                res.status(500).json({ error: 'Internal server error' });
            }
        };
    }
}
exports.ReminderController = ReminderController;
//# sourceMappingURL=reminderController.js.map