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
        const now = new Date();
        return new Promise((resolve, reject) => {
            const stmt = db.prepare(`
        INSERT INTO reminders (id, customer_id, type, message, scheduled_for, completed, created_at, updated_at, repeat_interval)
        VALUES (?, ?, ?, ?, ?, 0, ?, ?, ?)
      `);
            stmt.run([
                id,
                data.customer_id,
                data.type,
                data.message,
                data.scheduled_for.toISOString(),
                now.toISOString(),
                now.toISOString(),
                data.repeat_interval || null
            ], (err) => {
                if (err)
                    return reject(err);
                resolve({
                    id,
                    customer_id: data.customer_id,
                    type: data.type,
                    message: data.message,
                    scheduled_for: data.scheduled_for,
                    completed: false,
                    created_at: now,
                    updated_at: now,
                    repeat_interval: data.repeat_interval || null,
                });
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
                const reminders = rows.map(r => ({
                    id: r.id,
                    customer_id: r.customer_id,
                    type: r.type,
                    message: r.message,
                    scheduled_for: new Date(r.scheduled_for),
                    completed: Boolean(r.completed),
                    created_at: new Date(r.created_at),
                    updated_at: new Date(r.updated_at),
                    repeat_interval: r.repeat_interval,
                }));
                resolve(reminders);
            });
        });
    }
    async markReminderCompleted(id) {
        const db = database_1.default.getInstance().getDb();
        const now = new Date().toISOString();
        return new Promise((resolve, reject) => {
            db.run(`UPDATE reminders SET completed = 1, updated_at = ? WHERE id = ?`, [now, id], function (err) {
                if (err)
                    return reject(err);
                if (this.changes > 0) {
                    db.get(`SELECT * FROM reminders WHERE id = ?`, [id], (err, row) => {
                        if (err)
                            return reject(err);
                        if (row) {
                            resolve({
                                id: row.id,
                                customer_id: row.customer_id,
                                type: row.type,
                                message: row.message,
                                scheduled_for: new Date(row.scheduled_for),
                                completed: true,
                                created_at: new Date(row.created_at),
                                updated_at: new Date(row.updated_at),
                                repeat_interval: row.repeat_interval,
                            });
                        }
                        else {
                            resolve(null);
                        }
                    });
                }
                else {
                    resolve(null);
                }
            });
        });
    }
    async getRemindersByCustomerId(customerId) {
        const db = database_1.default.getInstance().getDb();
        return new Promise((resolve, reject) => {
            db.all(`SELECT * FROM reminders WHERE customer_id = ? ORDER BY scheduled_for ASC`, [customerId], (err, rows) => {
                if (err)
                    return reject(err);
                const reminders = rows.map(r => ({
                    id: r.id,
                    customer_id: r.customer_id,
                    type: r.type,
                    message: r.message,
                    scheduled_for: new Date(r.scheduled_for),
                    completed: Boolean(r.completed),
                    created_at: new Date(r.created_at),
                    updated_at: new Date(r.updated_at),
                    repeat_interval: r.repeat_interval,
                }));
                resolve(reminders);
            });
        });
    }
    async getAllReminders() {
        const db = database_1.default.getInstance().getDb();
        return new Promise((resolve, reject) => {
            db.all(`SELECT * FROM reminders ORDER BY scheduled_for ASC`, (err, rows) => {
                if (err)
                    return reject(err);
                const reminders = rows.map(r => ({
                    id: r.id,
                    customer_id: r.customer_id,
                    type: r.type,
                    message: r.message,
                    scheduled_for: new Date(r.scheduled_for),
                    completed: Boolean(r.completed),
                    created_at: new Date(r.created_at),
                    updated_at: new Date(r.updated_at),
                    repeat_interval: r.repeat_interval,
                }));
                resolve(reminders);
            });
        });
    }
    async updateReminder(id, data) {
        const db = database_1.default.getInstance().getDb();
        const now = new Date().toISOString();
        const fields = [];
        const values = [];
        if (data.type) {
            fields.push('type = ?');
            values.push(data.type);
        }
        if (data.message) {
            fields.push('message = ?');
            values.push(data.message);
        }
        if (data.scheduled_for) {
            fields.push('scheduled_for = ?');
            values.push(data.scheduled_for.toISOString());
        }
        if (data.completed !== undefined) {
            fields.push('completed = ?');
            values.push(data.completed ? 1 : 0);
        }
        if (data.repeat_interval !== undefined) {
            fields.push('repeat_interval = ?');
            values.push(data.repeat_interval);
        }
        if (fields.length === 0)
            return this.getReminderById(id); // No fields to update
        fields.push('updated_at = ?');
        values.push(now);
        values.push(id);
        return new Promise((resolve, reject) => {
            db.run(`UPDATE reminders SET ${fields.join(', ')} WHERE id = ?`, values, (err) => {
                if (err)
                    return reject(err);
                // Note: changes count not available with arrow function, fetch to verify
                this.getReminderById(id)
                    .then(reminder => {
                    resolve(reminder);
                })
                    .catch(reject);
            });
        });
    }
    async deleteReminder(id) {
        const db = database_1.default.getInstance().getDb();
        return new Promise((resolve, reject) => {
            db.run(`DELETE FROM reminders WHERE id = ?`, [id], function (err) {
                if (err)
                    return reject(err);
                resolve(this.changes > 0);
            });
        });
    }
    async getReminderById(id) {
        const db = database_1.default.getInstance().getDb();
        return new Promise((resolve, reject) => {
            db.get(`SELECT * FROM reminders WHERE id = ?`, [id], (err, row) => {
                if (err)
                    return reject(err);
                if (row) {
                    resolve({
                        id: row.id,
                        customer_id: row.customer_id,
                        type: row.type,
                        message: row.message,
                        scheduled_for: new Date(row.scheduled_for),
                        completed: Boolean(row.completed),
                        created_at: new Date(row.created_at),
                        updated_at: new Date(row.updated_at),
                        repeat_interval: row.repeat_interval,
                    });
                }
                else {
                    resolve(null);
                }
            });
        });
    }
}
exports.ReminderService = ReminderService;
//# sourceMappingURL=reminderService.js.map