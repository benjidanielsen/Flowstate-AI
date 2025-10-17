"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.ExternalIntegrationService = void 0;
const logger_1 = __importDefault(require("../utils/logger"));
const database_1 = __importDefault(require("../database"));
const uuid_1 = require("uuid");
class ExternalIntegrationService {
    async createIntegration(integration) {
        const db = database_1.default.getInstance().getDb();
        const id = (0, uuid_1.v4)();
        const now = new Date().toISOString();
        logger_1.default.info('Creating new external integration', { type: integration.type, customerId: integration.customer_id });
        return new Promise((resolve, reject) => {
            db.run(`INSERT INTO external_integrations (id, customer_id, type, config, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)`, [id, integration.customer_id, integration.type, integration.config, now, now], function (err) {
                if (err)
                    return reject(err);
                resolve({
                    id,
                    ...integration,
                    created_at: new Date(now),
                    updated_at: new Date(now)
                });
            });
        });
    }
    async getIntegrationsByCustomer(customerId) {
        const db = database_1.default.getInstance().getDb();
        logger_1.default.info('Fetching external integrations for customer', { customerId });
        return new Promise((resolve, reject) => {
            db.all(`SELECT * FROM external_integrations WHERE customer_id = ?`, [customerId], (err, rows) => {
                if (err)
                    return reject(err);
                const integrations = rows.map(row => ({
                    id: row.id,
                    customer_id: row.customer_id,
                    type: row.type,
                    config: row.config,
                    created_at: new Date(row.created_at),
                    updated_at: new Date(row.updated_at)
                }));
                resolve(integrations);
            });
        });
    }
    async updateIntegration(id, updates) {
        const db = database_1.default.getInstance().getDb();
        const now = new Date().toISOString();
        logger_1.default.info('Updating external integration', { id });
        const fields = [];
        const values = [];
        if (updates.type) {
            fields.push('type = ?');
            values.push(updates.type);
        }
        if (updates.config) {
            fields.push('config = ?');
            values.push(updates.config);
        }
        fields.push('updated_at = ?');
        values.push(now);
        values.push(id);
        return new Promise((resolve, reject) => {
            db.run(`UPDATE external_integrations SET ${fields.join(', ')} WHERE id = ?`, values, function (err) {
                if (err)
                    return reject(err);
                db.get(`SELECT * FROM external_integrations WHERE id = ?`, [id], (err, row) => {
                    if (err)
                        return reject(err);
                    if (row) {
                        resolve({
                            id: row.id,
                            customer_id: row.customer_id,
                            type: row.type,
                            config: row.config,
                            created_at: new Date(row.created_at),
                            updated_at: new Date(row.updated_at)
                        });
                    }
                    else {
                        reject(new Error('Integration not found after update'));
                    }
                });
            });
        });
    }
    async deleteIntegration(id) {
        const db = database_1.default.getInstance().getDb();
        logger_1.default.info('Deleting external integration', { id });
        return new Promise((resolve, reject) => {
            db.run(`DELETE FROM external_integrations WHERE id = ?`, [id], function (err) {
                if (err)
                    return reject(err);
                resolve();
            });
        });
    }
}
exports.ExternalIntegrationService = ExternalIntegrationService;
//# sourceMappingURL=externalIntegrationService.js.map