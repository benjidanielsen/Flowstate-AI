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
        let client = null;
        try {
            const pool = database_1.default.getInstance().getPool();
            client = await pool.connect();
            const id = (0, uuid_1.v4)();
            const timestamp = new Date();
            const result = await client.query(`INSERT INTO event_logs (id, customer_id, event_type, event_data, timestamp, user_id)
         VALUES ($1, $2, $3, $4, $5, $6) RETURNING *`, [
                id,
                customerId || null,
                eventType,
                eventData,
                timestamp.toISOString(),
                userId || null
            ]);
            return result.rows[0];
        }
        finally {
            if (client)
                client.release();
        }
    }
    async getEventsByCustomer(customerId, limit = 50) {
        let client = null;
        try {
            const pool = database_1.default.getInstance().getPool();
            client = await pool.connect();
            const result = await client.query(`SELECT * FROM event_logs 
         WHERE customer_id = $1 
         ORDER BY timestamp DESC 
         LIMIT $2`, [customerId, limit]);
            return result.rows.map(row => ({
                ...row,
                event_data: row.event_data,
                timestamp: new Date(row.timestamp)
            }));
        }
        finally {
            if (client)
                client.release();
        }
    }
    async getAllEvents(limit = 100) {
        let client = null;
        try {
            const pool = database_1.default.getInstance().getPool();
            client = await pool.connect();
            const result = await client.query(`SELECT * FROM event_logs 
         ORDER BY timestamp DESC 
         LIMIT $1`, [limit]);
            return result.rows.map(row => ({
                ...row,
                event_data: row.event_data,
                timestamp: new Date(row.timestamp)
            }));
        }
        finally {
            if (client)
                client.release();
        }
    }
    async getEventsByType(eventType, limit = 50) {
        let client = null;
        try {
            const pool = database_1.default.getInstance().getPool();
            client = await pool.connect();
            const result = await client.query(`SELECT * FROM event_logs 
         WHERE event_type = $1 
         ORDER BY timestamp DESC 
         LIMIT $2`, [eventType, limit]);
            return result.rows.map(row => ({
                ...row,
                event_data: row.event_data,
                timestamp: new Date(row.timestamp)
            }));
        }
        finally {
            if (client)
                client.release();
        }
    }
}
exports.EventLogService = EventLogService;
//# sourceMappingURL=eventLogService.js.map