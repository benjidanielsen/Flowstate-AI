"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.followUpService = exports.FollowUpService = void 0;
const database_1 = __importDefault(require("../database"));
const logger_1 = __importDefault(require("../utils/logger"));
const uuid_1 = require("uuid");
class FollowUpService {
    constructor() {
        // Follow-up timing based on Frazer Method stages
        this.followUpTimes = {
            'new_lead': 1, // 1 day - Quick response for new leads
            'qualified': 3, // 3 days - Give them time to think
            'presentation': 7, // 7 days - Follow up after presentation
            'follow_up': 14, // 14 days - Longer nurture cycle
            'closed': 30 // 30 days - Check-in with closed customers
        };
    }
    async createFollowUp(customerId, stage, agentName) {
        const days = this.followUpTimes[stage] || 7;
        const scheduledFor = new Date();
        scheduledFor.setDate(scheduledFor.getDate() + days);
        const notes = this.getFollowUpMessage(stage);
        let client = null;
        try {
            const pool = database_1.default.getInstance().getPool();
            client = await pool.connect();
            const id = (0, uuid_1.v4)();
            const now = new Date().toISOString();
            const result = await client.query(`INSERT INTO follow_ups (id, customer_id, agent_name, due_date, status, notes, created_at, updated_at)
         VALUES ($1, $2, $3, $4, $5, $6, $7, $8) RETURNING *`, [
                id,
                customerId,
                agentName,
                scheduledFor.toISOString(),
                'pending',
                notes,
                now,
                now,
            ]);
            logger_1.default.info(`Created follow-up for customer ${customerId} at stage ${stage}, scheduled for ${scheduledFor.toISOString()}`);
            return result.rows[0];
        }
        finally {
            if (client)
                client.release();
        }
    }
    getFollowUpMessage(stage) {
        const messages = {
            'new_lead': 'Follow up with new lead - establish rapport',
            'qualified': 'Check if prospect has questions about opportunity',
            'presentation': 'Follow up on presentation - address concerns',
            'follow_up': 'Continue nurturing relationship',
            'closed': 'Check in on progress and satisfaction'
        };
        return messages[stage] || `Follow up on ${stage}`;
    }
    async autoScheduleFollowUps() {
        let client = null;
        try {
            const pool = database_1.default.getInstance().getPool();
            client = await pool.connect();
            const customers = await client.query(`SELECT id, status FROM customers WHERE status != 'Closed - Won'`);
            let scheduled = 0;
            for (const customer of customers.rows) {
                // Assuming 'customer.status' directly maps to a stage in followUpTimes
                // And we need an agent_name for the follow-up, using a placeholder for now
                await this.createFollowUp(customer.id, customer.status, 'AutoFollowUpAgent');
                scheduled++;
            }
            logger_1.default.info(`Auto-scheduled ${scheduled} follow-ups`);
            return scheduled;
        }
        finally {
            if (client)
                client.release();
        }
    }
    async getUpcomingFollowUps(days = 7) {
        const futureDate = new Date();
        futureDate.setDate(futureDate.getDate() + days);
        let client = null;
        try {
            const pool = database_1.default.getInstance().getPool();
            client = await pool.connect();
            const result = await client.query(`SELECT f.*, c.name as customer_name, c.email, c.status
         FROM follow_ups f
         JOIN customers c ON f.customer_id = c.id
         WHERE f.status = 'pending'
         AND f.due_date <= $1
         ORDER BY f.due_date ASC`, [futureDate.toISOString()]);
            return result.rows;
        }
        finally {
            if (client)
                client.release();
        }
    }
    async getFollowUpById(id) {
        let client = null;
        try {
            const pool = database_1.default.getInstance().getPool();
            client = await pool.connect();
            const result = await client.query(`SELECT * FROM follow_ups WHERE id = $1`, [id]);
            return result.rows[0] || null;
        }
        finally {
            if (client)
                client.release();
        }
    }
    async getFollowUpsByCustomerId(customerId) {
        let client = null;
        try {
            const pool = database_1.default.getInstance().getPool();
            client = await pool.connect();
            const result = await client.query(`SELECT * FROM follow_ups WHERE customer_id = $1 ORDER BY due_date ASC`, [customerId]);
            return result.rows;
        }
        finally {
            if (client)
                client.release();
        }
    }
    async updateFollowUpStatus(id, status) {
        let client = null;
        try {
            const pool = database_1.default.getInstance().getPool();
            client = await pool.connect();
            const now = new Date().toISOString();
            const result = await client.query(`UPDATE follow_ups SET status = $1, updated_at = $2 WHERE id = $3 RETURNING *`, [status, now, id]);
            return result.rows[0] || null;
        }
        finally {
            if (client)
                client.release();
        }
    }
    async getPendingFollowUps() {
        let client = null;
        try {
            const pool = database_1.default.getInstance().getPool();
            client = await pool.connect();
            const result = await client.query(`SELECT * FROM follow_ups WHERE status = 'pending' AND due_date <= NOW() ORDER BY due_date ASC`);
            return result.rows;
        }
        finally {
            if (client)
                client.release();
        }
    }
    async deleteFollowUp(id) {
        let client = null;
        try {
            const pool = database_1.default.getInstance().getPool();
            client = await pool.connect();
            const result = await client.query(`DELETE FROM follow_ups WHERE id = $1 RETURNING id`, [id]);
            return result.rowCount !== null && result.rowCount > 0;
        }
        finally {
            if (client)
                client.release();
        }
    }
}
exports.FollowUpService = FollowUpService;
exports.followUpService = new FollowUpService();
//# sourceMappingURL=followUpService.js.map