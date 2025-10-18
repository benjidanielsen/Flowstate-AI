"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.customerService = exports.CustomerService = void 0;
const database_1 = __importDefault(require("../database"));
const uuid_1 = require("uuid");
const types_1 = require("../types");
const eventLogService_1 = require("./eventLogService");
const pipelineValidationService_1 = require("./pipelineValidationService");
class CustomerService {
    constructor() {
        this.eventLogService = new eventLogService_1.EventLogService();
        this.pipelineValidationService = new pipelineValidationService_1.PipelineValidationService();
    }
    async getAllCustomers(filters = {}) {
        let client = null;
        try {
            const pool = database_1.default.getInstance().getPool();
            client = await pool.connect();
            let query = 'SELECT * FROM customers WHERE 1=1';
            const params = [];
            let paramIndex = 1;
            if (filters.status) {
                query += ` AND status = $${paramIndex++}`;
                params.push(filters.status);
            }
            if (filters.source) {
                query += ` AND source = $${paramIndex++}`;
                params.push(filters.source);
            }
            if (filters.country) {
                query += ` AND country = $${paramIndex++}`;
                params.push(filters.country);
            }
            if (filters.language) {
                query += ` AND language = $${paramIndex++}`;
                params.push(filters.language);
            }
            if (filters.next_action) {
                query += ` AND next_action = $${paramIndex++}`;
                params.push(filters.next_action);
            }
            if (filters.search) {
                const searchTerm = `%${filters.search}%`;
                query += ` AND (name ILIKE $${paramIndex++} OR email ILIKE $${paramIndex++} OR phone ILIKE $${paramIndex++} OR notes ILIKE $${paramIndex++})`;
                params.push(searchTerm, searchTerm, searchTerm, searchTerm);
            }
            const sortBy = filters.sortBy || 'updated_at';
            const sortOrder = filters.sortOrder || 'DESC';
            query += ` ORDER BY ${sortBy} ${sortOrder}`;
            const result = await client.query(query, params);
            return result.rows.map(row => ({
                ...row,
                created_at: new Date(row.created_at),
                updated_at: new Date(row.updated_at),
                next_action_date: row.next_action_date ? new Date(row.next_action_date) : undefined,
                consent_json: row.consent_json,
                utm_json: row.utm_json
            }));
        }
        finally {
            if (client)
                client.release();
        }
    }
    async getCustomerById(id) {
        let client = null;
        try {
            const pool = database_1.default.getInstance().getPool();
            client = await pool.connect();
            const result = await client.query(`SELECT * FROM customers WHERE id = $1`, [id]);
            const row = result.rows[0];
            if (!row)
                return null;
            return {
                ...row,
                created_at: new Date(row.created_at),
                updated_at: new Date(row.updated_at),
                next_action_date: row.next_action_date ? new Date(row.next_action_date) : undefined,
                consent_json: row.consent_json,
                utm_json: row.utm_json
            };
        }
        finally {
            if (client)
                client.release();
        }
    }
    async createCustomer(customerData) {
        let client = null;
        try {
            const pool = database_1.default.getInstance().getPool();
            client = await pool.connect();
            const id = (0, uuid_1.v4)();
            const now = new Date().toISOString();
            const customer = {
                id,
                ...customerData,
                status: customerData.status || types_1.PipelineStatus.NEW_LEAD,
                created_at: new Date(now),
                updated_at: new Date(now)
            };
            const result = await client.query(`INSERT INTO customers (
          id, name, email, phone, status, notes, next_action, next_action_date,
          created_at, updated_at, source, handle_ig, handle_whatsapp, country, language,
          consent_json, utm_json
        )
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17)
        RETURNING *`, [
                customer.id,
                customer.name,
                customer.email || null,
                customer.phone || null,
                customer.status,
                customer.notes || null,
                customer.next_action || null,
                customer.next_action_date?.toISOString() || null,
                customer.created_at.toISOString(),
                customer.updated_at.toISOString(),
                customerData.source || null,
                customerData.handle_ig || null,
                customerData.handle_whatsapp || null,
                customerData.country || null,
                customerData.language || null,
                customerData.consent_json || null,
                customerData.utm_json || null
            ]);
            const createdCustomer = result.rows[0];
            // Log event
            this.eventLogService.logEvent('customer_created', {
                customer_id: createdCustomer.id,
                name: createdCustomer.name,
                status: createdCustomer.status
            }, createdCustomer.id);
            return {
                ...createdCustomer,
                created_at: new Date(createdCustomer.created_at),
                updated_at: new Date(createdCustomer.updated_at),
                next_action_date: createdCustomer.next_action_date ? new Date(createdCustomer.next_action_date) : undefined,
            };
        }
        finally {
            if (client)
                client.release();
        }
    }
    async updateCustomer(id, updates) {
        let client = null;
        try {
            const pool = database_1.default.getInstance().getPool();
            client = await pool.connect();
            const existingCustomer = await this.getCustomerById(id);
            if (!existingCustomer) {
                return null;
            }
            const now = new Date().toISOString();
            const updateKeys = Object.keys(updates).filter(key => key !== 'id' && key !== 'created_at' && key !== 'updated_at');
            const updateValues = updateKeys.map(key => {
                const value = updates[key];
                // Handle JSON fields
                if (key === 'consent_json' || key === 'utm_json') {
                    return value;
                }
                return value !== undefined ? value : existingCustomer[key];
            });
            if (updateKeys.length === 0 && !updates.status) {
                return existingCustomer; // No actual updates
            }
            const setClauses = updateKeys.map((key, index) => `
        ${key} = $${index + 2}
      `).join(', ');
            const query = `UPDATE customers SET ${setClauses}, updated_at = $${updateValues.length + 2} WHERE id = $1 RETURNING *`;
            const result = await client.query(query, [id, ...updateValues, now]);
            const updatedCustomer = result.rows[0];
            // Log event if status changed
            if (updates.status && updates.status !== existingCustomer.status) {
                this.eventLogService.logEvent('status_changed', {
                    customer_id: id,
                    old_status: existingCustomer.status,
                    new_status: updates.status
                }, id);
            }
            if (!updatedCustomer)
                return null; // Should not happen if RETURNING * is used
            return {
                ...updatedCustomer,
                created_at: new Date(updatedCustomer.created_at),
                updated_at: new Date(updatedCustomer.updated_at),
                next_action_date: updatedCustomer.next_action_date ? new Date(updatedCustomer.next_action_date) : undefined,
            };
        }
        finally {
            if (client)
                client.release();
        }
    }
    async deleteCustomer(id) {
        let client = null;
        try {
            const pool = database_1.default.getInstance().getPool();
            client = await pool.connect();
            const result = await client.query(`DELETE FROM customers WHERE id = $1 RETURNING id`, [id]);
            return result.rowCount !== null && result.rowCount > 0;
        }
        finally {
            if (client)
                client.release();
        }
    }
    async getCustomersByStatus(status) {
        let client = null;
        try {
            const pool = database_1.default.getInstance().getPool();
            client = await pool.connect();
            const result = await client.query(`SELECT * FROM customers WHERE status = $1 ORDER BY created_at DESC`, [status]);
            return result.rows.map(row => ({
                ...row,
                created_at: new Date(row.created_at),
                updated_at: new Date(row.updated_at),
                next_action_date: row.next_action_date ? new Date(row.next_action_date) : undefined,
            }));
        }
        finally {
            if (client)
                client.release();
        }
    }
    async moveCustomerToNextStage(id) {
        const customer = await this.getCustomerById(id);
        if (!customer) {
            return null;
        }
        const nextValidStages = this.pipelineValidationService.getNextValidStages(customer.status);
        if (nextValidStages.length === 0) {
            return customer; // Already at final stage or no valid next stages
        }
        // Get the first valid next stage (main pipeline progression)
        const nextStatus = nextValidStages[0];
        // Validate the transition
        const validationResult = await this.pipelineValidationService.validateStageTransition(id, customer.status, nextStatus);
        if (!validationResult.allowed) {
            throw new Error(validationResult.reason || 'Stage transition not allowed');
        }
        // Log the transition
        await this.pipelineValidationService.logStageTransition(id, customer.status, nextStatus);
        return this.updateCustomer(id, { status: nextStatus });
    }
    /**
     * Move customer to a specific stage with validation
     */
    async moveCustomerToStage(id, targetStage) {
        const customer = await this.getCustomerById(id);
        if (!customer) {
            return null;
        }
        // Validate the transition
        const validationResult = await this.pipelineValidationService.validateStageTransition(id, customer.status, targetStage);
        if (!validationResult.allowed) {
            throw new Error(validationResult.reason || 'Stage transition not allowed');
        }
        // Log the transition
        await this.pipelineValidationService.logStageTransition(id, customer.status, targetStage);
        return this.updateCustomer(id, { status: targetStage });
    }
    /**
     * Get stage recommendations for a customer
     */
    async getStageRecommendations(id) {
        const customer = await this.getCustomerById(id);
        if (!customer) {
            return null;
        }
        return this.pipelineValidationService.getStageRecommendations(id, customer.status);
    }
}
exports.CustomerService = CustomerService;
exports.customerService = new CustomerService();
//# sourceMappingURL=customerService.js.map