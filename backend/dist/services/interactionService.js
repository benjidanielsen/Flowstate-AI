"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.InteractionService = void 0;
const database_1 = __importDefault(require("../database"));
const uuid_1 = require("uuid");
const eventLogService_1 = require("./eventLogService");
class InteractionService {
    constructor() {
        this.eventLogService = new eventLogService_1.EventLogService();
    }
    async getInteractionsByCustomer(customerId) {
        const db = database_1.default.getInstance().getDb();
        return new Promise((resolve, reject) => {
            db.all(`
        SELECT * FROM interactions 
        WHERE customer_id = ? 
        ORDER BY created_at DESC
      `, [customerId], (err, rows) => {
                if (err) {
                    reject(err);
                }
                else {
                    const interactions = rows.map(row => ({
                        ...row,
                        created_at: new Date(row.created_at),
                        scheduled_for: row.scheduled_for ? new Date(row.scheduled_for) : undefined,
                        completed: Boolean(row.completed)
                    }));
                    resolve(interactions);
                }
            });
        });
    }
    async createInteraction(interactionData) {
        const db = database_1.default.getInstance().getDb();
        const id = (0, uuid_1.v4)();
        const now = new Date();
        const interaction = {
            id,
            ...interactionData,
            created_at: now
        };
        return new Promise((resolve, reject) => {
            const stmt = db.prepare(`
        INSERT INTO interactions (id, customer_id, type, content, created_at, scheduled_for, completed)
        VALUES (?, ?, ?, ?, ?, ?, ?)
      `);
            stmt.run([
                interaction.id,
                interaction.customer_id,
                interaction.type,
                interaction.content,
                interaction.created_at.toISOString(),
                interaction.scheduled_for?.toISOString(),
                interaction.completed ? 1 : 0
            ], (err) => {
                if (err) {
                    reject(err);
                }
                else {
                    // Log event
                    this.eventLogService.logEvent('interaction_created', {
                        interaction_id: interaction.id,
                        customer_id: interaction.customer_id,
                        type: interaction.type
                    }, interaction.customer_id);
                    resolve(interaction);
                }
            });
            stmt.finalize();
        });
    }
    async updateInteraction(id, updates) {
        const db = database_1.default.getInstance().getDb();
        // First get the existing interaction
        const existing = await this.getInteractionById(id);
        if (!existing) {
            return null;
        }
        const updated = { ...existing, ...updates };
        return new Promise((resolve, reject) => {
            const stmt = db.prepare(`
        UPDATE interactions 
        SET type = ?, content = ?, scheduled_for = ?, completed = ?
        WHERE id = ?
      `);
            stmt.run([
                updated.type,
                updated.content,
                updated.scheduled_for?.toISOString(),
                updated.completed ? 1 : 0,
                id
            ], function (err) {
                if (err) {
                    reject(err);
                }
                else {
                    resolve(updated);
                }
            });
            stmt.finalize();
        });
    }
    async getInteractionById(id) {
        const db = database_1.default.getInstance().getDb();
        return new Promise((resolve, reject) => {
            db.get('SELECT * FROM interactions WHERE id = ?', [id], (err, row) => {
                if (err) {
                    reject(err);
                }
                else if (!row) {
                    resolve(null);
                }
                else {
                    const interaction = {
                        ...row,
                        created_at: new Date(row.created_at),
                        scheduled_for: row.scheduled_for ? new Date(row.scheduled_for) : undefined,
                        completed: Boolean(row.completed)
                    };
                    resolve(interaction);
                }
            });
        });
    }
    async deleteInteraction(id) {
        const db = database_1.default.getInstance().getDb();
        return new Promise((resolve, reject) => {
            db.run('DELETE FROM interactions WHERE id = ?', [id], function (err) {
                if (err) {
                    reject(err);
                }
                else {
                    resolve(this.changes > 0);
                }
            });
        });
    }
    async getUpcomingInteractions(limit = 20) {
        const db = database_1.default.getInstance().getDb();
        const now = new Date().toISOString();
        return new Promise((resolve, reject) => {
            db.all(`
        SELECT * FROM interactions 
        WHERE scheduled_for > ? AND completed = 0
        ORDER BY scheduled_for ASC 
        LIMIT ?
      `, [now, limit], (err, rows) => {
                if (err) {
                    reject(err);
                }
                else {
                    const interactions = rows.map(row => ({
                        ...row,
                        created_at: new Date(row.created_at),
                        scheduled_for: row.scheduled_for ? new Date(row.scheduled_for) : undefined,
                        completed: Boolean(row.completed)
                    }));
                    resolve(interactions);
                }
            });
        });
    }
}
exports.InteractionService = InteractionService;
//# sourceMappingURL=interactionService.js.map