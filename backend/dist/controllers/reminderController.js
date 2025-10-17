"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.ReminderController = void 0;
const reminderService_1 = require("../services/reminderService");
const joi_1 = __importDefault(require("joi"));
const types_1 = require("../types");
const createSchema = joi_1.default.object({
    customer_id: joi_1.default.string().required(),
    type: joi_1.default.string().valid(...Object.values(types_1.ReminderType)).required(),
    message: joi_1.default.string().allow('').optional(),
    scheduled_for: joi_1.default.date().iso().required(),
    repeat_interval: joi_1.default.string().allow(null, '').optional(),
});
const updateSchema = joi_1.default.object({
    type: joi_1.default.string().valid(...Object.values(types_1.ReminderType)).optional(),
    message: joi_1.default.string().allow('').optional(),
    scheduled_for: joi_1.default.date().iso().optional(),
    completed: joi_1.default.boolean().optional(),
    repeat_interval: joi_1.default.string().allow(null, '').optional(),
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
                    scheduled_for: new Date(value.scheduled_for),
                    repeat_interval: value.repeat_interval,
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
                const reminder = await this.reminderService.markReminderCompleted(req.params.id);
                if (!reminder)
                    return res.status(404).json({ error: 'Reminder not found' });
                res.status(200).json(reminder);
            }
            catch (err) {
                console.error('Error completing reminder:', err);
                res.status(500).json({ error: 'Internal server error' });
            }
        };
        this.getRemindersByCustomerId = async (req, res) => {
            try {
                const { customerId } = req.params;
                const reminders = await this.reminderService.getRemindersByCustomerId(customerId);
                res.json(reminders);
            }
            catch (err) {
                console.error('Error getting reminders by customer ID:', err);
                res.status(500).json({ error: 'Internal server error' });
            }
        };
        this.update = async (req, res) => {
            try {
                const { id } = req.params;
                const { error, value } = updateSchema.validate(req.body, { abortEarly: false });
                if (error)
                    return res.status(400).json({ error: 'Invalid payload', details: error.details });
                const updatedReminder = await this.reminderService.updateReminder(id, value);
                if (!updatedReminder)
                    return res.status(404).json({ error: 'Reminder not found' });
                res.status(200).json(updatedReminder);
            }
            catch (err) {
                console.error('Error updating reminder:', err);
                res.status(500).json({ error: 'Internal server error' });
            }
        };
        this.delete = async (req, res) => {
            try {
                const { id } = req.params;
                const deleted = await this.reminderService.deleteReminder(id);
                if (!deleted)
                    return res.status(404).json({ error: 'Reminder not found' });
                res.status(204).send(); // No content for successful deletion
            }
            catch (err) {
                console.error('Error deleting reminder:', err);
                res.status(500).json({ error: 'Internal server error' });
            }
        };
    }
}
exports.ReminderController = ReminderController;
//# sourceMappingURL=reminderController.js.map