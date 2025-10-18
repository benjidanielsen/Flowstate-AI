"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.externalIntegrationService = exports.ExternalIntegrationService = void 0;
const database_1 = __importDefault(require("../database"));
const logger_1 = __importDefault(require("../utils/logger"));
const uuid_1 = require("uuid");
class ExternalIntegrationService {
    async createIntegration(integration) {
        let client = null;
        try {
            const pool = database_1.default.getInstance().getPool();
            client = await pool.connect();
            const id = (0, uuid_1.v4)();
            const now = new Date().toISOString();
            logger_1.default.info('Creating new external integration', { type: integration.type, customerId: integration.customer_id });
            const result = await client.query(`INSERT INTO external_integrations (id, customer_id, type, config, created_at, updated_at) VALUES ($1, $2, $3, $4, $5, $6) RETURNING *`, [
                id,
                integration.customer_id,
                integration.type,
                integration.config,
                now,
                now,
            ]);
            return result.rows[0];
        }
        finally {
            if (client)
                client.release();
        }
    }
    async getIntegrationsByCustomer(customerId) {
        let client = null;
        try {
            const pool = database_1.default.getInstance().getPool();
            client = await pool.connect();
            logger_1.default.info('Fetching external integrations for customer', { customerId });
            const result = await client.query(`SELECT * FROM external_integrations WHERE customer_id = $1 ORDER BY created_at DESC`, [customerId]);
            return result.rows.map(row => ({
                ...row,
                created_at: new Date(row.created_at),
                updated_at: new Date(row.updated_at)
            }));
        }
        finally {
            if (client)
                client.release();
        }
    }
    async updateIntegration(id, updates) {
        let client = null;
        try {
            const pool = database_1.default.getInstance().getPool();
            client = await pool.connect();
            const now = new Date().toISOString();
            logger_1.default.info('Updating external integration', { id });
            const fields = [];
            const values = [];
            let paramIndex = 1;
            if (updates.type) {
                fields.push(`type = $${paramIndex++}`);
                values.push(updates.type);
            }
            if (updates.config) {
                fields.push(`config = $${paramIndex++}`);
                values.push(updates.config);
            }
            if (fields.length === 0) {
                // No fields to update, return existing integration
                const existing = await client.query(`SELECT * FROM external_integrations WHERE id = $1`, [id]);
                return existing.rows[0] || null;
            }
            fields.push(`updated_at = $${paramIndex++}`);
            values.push(now);
            values.push(id); // ID is the last parameter for WHERE clause
            const result = await client.query(`UPDATE external_integrations SET ${fields.join(', ')} WHERE id = $${paramIndex} RETURNING *`, values);
            return result.rows[0] || null;
        }
        finally {
            if (client)
                client.release();
        }
    }
    async deleteIntegration(id) {
        let client = null;
        try {
            const pool = database_1.default.getInstance().getPool();
            client = await pool.connect();
            logger_1.default.info('Deleting external integration', { id });
            const result = await client.query(`DELETE FROM external_integrations WHERE id = $1 RETURNING id`, [id]);
            return result.rowCount !== null && result.rowCount > 0;
        }
        finally {
            if (client)
                client.release();
        }
    }
    async getIntegrationById(id) {
        let client = null;
        try {
            const pool = database_1.default.getInstance().getPool();
            client = await pool.connect();
            const result = await client.query(`SELECT * FROM external_integrations WHERE id = $1`, [id]);
            return result.rows[0] || null;
        }
        finally {
            if (client)
                client.release();
        }
    }
}
exports.ExternalIntegrationService = ExternalIntegrationService;
exports.externalIntegrationService = new ExternalIntegrationService();
//# sourceMappingURL=externalIntegrationService.js.map