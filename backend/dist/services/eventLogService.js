"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.EventLogService = void 0;
const database_1 = __importDefault(require("../database"));
const uuid_1 = require("uuid");
class EventLogService {
    async logEvent(eventType, eventData, customerId, userId) {
        const db = database_1.default.getInstance().getDb();
        const id = (0, uuid_1.v4)();
        const timestamp = new Date();
        const eventLog = {
            id,
            customer_id: customerId,
            event_type: eventType,
            event_data: eventData,
            timestamp,
            user_id: userId
        };
        return new Promise((resolve, reject) => {
            const stmt = db.prepare(`
        INSERT INTO event_logs (id, customer_id, event_type, event_data, timestamp, user_id)
        VALUES (?, ?, ?, ?, ?, ?)
      `);
            stmt.run([
                eventLog.id,
                eventLog.customer_id,
                eventLog.event_type,
                JSON.stringify(eventLog.event_data),
                eventLog.timestamp.toISOString(),
                eventLog.user_id
            ], function (err) {
                if (err) {
                    reject(err);
                }
                else {
                    resolve(eventLog);
                }
            });
            stmt.finalize();
        });
    }
    async getEventsByCustomer(customerId, limit = 50) {
        const db = database_1.default.getInstance().getDb();
        return new Promise((resolve, reject) => {
            db.all(`
        SELECT * FROM event_logs 
        WHERE customer_id = ? 
        ORDER BY timestamp DESC 
        LIMIT ?
      `, [customerId, limit], (err, rows) => {
                if (err) {
                    reject(err);
                }
                else {
                    const events = rows.map(row => ({
                        ...row,
                        event_data: JSON.parse(row.event_data),
                        timestamp: new Date(row.timestamp)
                    }));
                    resolve(events);
                }
            });
        });
    }
    async getAllEvents(limit = 100) {
        const db = database_1.default.getInstance().getDb();
        return new Promise((resolve, reject) => {
            db.all(`
        SELECT * FROM event_logs 
        ORDER BY timestamp DESC 
        LIMIT ?
      `, [limit], (err, rows) => {
                if (err) {
                    reject(err);
                }
                else {
                    const events = rows.map(row => ({
                        ...row,
                        event_data: JSON.parse(row.event_data),
                        timestamp: new Date(row.timestamp)
                    }));
                    resolve(events);
                }
            });
        });
    }
    async getEventsByType(eventType, limit = 50) {
        const db = database_1.default.getInstance().getDb();
        return new Promise((resolve, reject) => {
            db.all(`
        SELECT * FROM event_logs 
        WHERE event_type = ? 
        ORDER BY timestamp DESC 
        LIMIT ?
      `, [eventType, limit], (err, rows) => {
                if (err) {
                    reject(err);
                }
                else {
                    const events = rows.map(row => ({
                        ...row,
                        event_data: JSON.parse(row.event_data),
                        timestamp: new Date(row.timestamp)
                    }));
                    resolve(events);
                }
            });
        });
    }
}
exports.EventLogService = EventLogService;
//# sourceMappingURL=eventLogService.js.map