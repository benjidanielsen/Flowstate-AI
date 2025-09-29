"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.ReminderService = void 0;
const database_1 = __importDefault(require("../database"));
const uuid_1 = require("uuid");
class ReminderService {
    async createReminder(data) {
        const db = database_1.default.getInstance().getDb();
        const id = (0, uuid_1.v4)();
        const created_at = new Date();
        return new Promise((resolve, reject) => {
            const stmt = db.prepare(`
        INSERT INTO reminders (id, customer_id, type, message, scheduled_for, completed, created_at)
        VALUES (?, ?, ?, ?, ?, 0, ?)
      `);
            stmt.run([
                id,
                data.customer_id,
                data.type,
                data.message || null,
                data.scheduled_for.toISOString(),
                created_at.toISOString()
            ], (err) => {
                if (err)
                    return reject(err);
                resolve({ id, ...data, completed: false, created_at });
            });
            stmt.finalize();
        });
    }
    async getDueReminders() {
        const db = database_1.default.getInstance().getDb();
        const now = new Date().toISOString();
        return new Promise((resolve, reject) => {
            db.all(`SELECT * FROM reminders WHERE completed = 0 AND scheduled_for <= ? ORDER BY scheduled_for ASC`, [now], (err, rows) => {
                if (err)
                    return reject(err);
                const reminders = rows.map(r => ({ ...r }));
                resolve(reminders);
            });
        });
    }
    async completeReminder(id) {
        const db = database_1.default.getInstance().getDb();
        return new Promise((resolve, reject) => {
            db.run(`UPDATE reminders SET completed = 1 WHERE id = ?`, [id], function (err) {
                if (err)
                    return reject(err);
                resolve(this.changes > 0);
            });
        });
    }
}
exports.ReminderService = ReminderService;
//# sourceMappingURL=reminderService.js.map