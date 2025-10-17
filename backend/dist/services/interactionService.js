"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.interactionService = void 0;
const uuid_1 = require("uuid");
const database_1 = __importDefault(require("../database"));
exports.interactionService = {
    async create(interaction) {
        const db = database_1.default.getInstance().getDb();
        const id = (0, uuid_1.v4)();
        const now = new Date();
        const interactionDate = interaction.interaction_date || now;
        return new Promise((resolve, reject) => {
            db.run(`INSERT INTO interactions (id, customer_id, type, summary, notes, interaction_date, created_at, updated_at) 
         VALUES (?, ?, ?, ?, ?, ?, ?, ?)`, [
                id,
                interaction.customer_id,
                interaction.type,
                interaction.summary,
                interaction.notes || null,
                interactionDate.toISOString(),
                now.toISOString(),
                now.toISOString()
            ], function (err) {
                if (err)
                    return reject(err);
                resolve({
                    id,
                    ...interaction,
                    interaction_date: interactionDate,
                    created_at: now,
                    updated_at: now
                });
            });
        });
    },
    async getByCustomerId(customerId) {
        const db = database_1.default.getInstance().getDb();
        return new Promise((resolve, reject) => {
            db.all(`SELECT * FROM interactions WHERE customer_id = ? ORDER BY interaction_date DESC`, [customerId], (err, rows) => {
                if (err)
                    return reject(err);
                const interactions = rows.map(row => ({
                    id: row.id,
                    customer_id: row.customer_id,
                    type: row.type,
                    summary: row.summary,
                    notes: row.notes,
                    interaction_date: new Date(row.interaction_date),
                    created_at: new Date(row.created_at),
                    updated_at: new Date(row.updated_at)
                }));
                resolve(interactions);
            });
        });
    },
    async getById(id) {
        const db = database_1.default.getInstance().getDb();
        return new Promise((resolve, reject) => {
            db.get(`SELECT * FROM interactions WHERE id = ?`, [id], (err, row) => {
                if (err)
                    return reject(err);
                if (!row)
                    return resolve(undefined);
                resolve({
                    id: row.id,
                    customer_id: row.customer_id,
                    type: row.type,
                    summary: row.summary,
                    notes: row.notes,
                    interaction_date: new Date(row.interaction_date),
                    created_at: new Date(row.created_at),
                    updated_at: new Date(row.updated_at)
                });
            });
        });
    },
    async update(id, updates) {
        const db = database_1.default.getInstance().getDb();
        const now = new Date().toISOString();
        const fields = [];
        const values = [];
        if (updates.customer_id) {
            fields.push('customer_id = ?');
            values.push(updates.customer_id);
        }
        if (updates.type) {
            fields.push('type = ?');
            values.push(updates.type);
        }
        if (updates.summary) {
            fields.push('summary = ?');
            values.push(updates.summary);
        }
        if (updates.notes !== undefined) {
            fields.push('notes = ?');
            values.push(updates.notes);
        }
        if (updates.interaction_date) {
            fields.push('interaction_date = ?');
            values.push(updates.interaction_date.toISOString());
        }
        fields.push('updated_at = ?');
        values.push(now);
        values.push(id);
        if (fields.length === 1) { // Only updated_at
            return this.getById(id);
        }
        return new Promise((resolve, reject) => {
            db.run(`UPDATE interactions SET ${fields.join(', ')} WHERE id = ?`, values, function (err) {
                if (err)
                    return reject(err);
                if (this.changes === 0)
                    return resolve(undefined);
                db.get(`SELECT * FROM interactions WHERE id = ?`, [id], (err, row) => {
                    if (err)
                        return reject(err);
                    if (!row)
                        return resolve(undefined);
                    resolve({
                        id: row.id,
                        customer_id: row.customer_id,
                        type: row.type,
                        summary: row.summary,
                        notes: row.notes,
                        interaction_date: new Date(row.interaction_date),
                        created_at: new Date(row.created_at),
                        updated_at: new Date(row.updated_at)
                    });
                });
            });
        });
    },
    async delete(id) {
        const db = database_1.default.getInstance().getDb();
        return new Promise((resolve, reject) => {
            db.run(`DELETE FROM interactions WHERE id = ?`, [id], function (err) {
                if (err)
                    return reject(err);
                resolve();
            });
        });
    },
};
//# sourceMappingURL=interactionService.js.map