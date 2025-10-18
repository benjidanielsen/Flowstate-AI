"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.qualificationService = exports.QualificationService = void 0;
const database_1 = __importDefault(require("../database"));
const uuid_1 = require("uuid");
class QualificationService {
    async createQualification(data) {
        let client = null;
        try {
            const pool = database_1.default.getInstance().getPool();
            client = await pool.connect();
            const id = (0, uuid_1.v4)();
            const now = new Date().toISOString();
            const result = await client.query(`INSERT INTO qualifications (id, customer_id, question, expected_answer, status, agent_name, created_at, updated_at)
         VALUES ($1, $2, $3, $4, $5, $6, $7, $8) RETURNING *`, [
                id,
                data.customer_id,
                data.question,
                data.expected_answer,
                data.status,
                data.agent_name || null,
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
    async getQualificationById(id) {
        let client = null;
        try {
            const pool = database_1.default.getInstance().getPool();
            client = await pool.connect();
            const result = await client.query(`SELECT * FROM qualifications WHERE id = $1`, [id]);
            return result.rows[0] || null;
        }
        finally {
            if (client)
                client.release();
        }
    }
    async updateQualificationStatus(id, status) {
        let client = null;
        try {
            const pool = database_1.default.getInstance().getPool();
            client = await pool.connect();
            const now = new Date().toISOString();
            const result = await client.query(`UPDATE qualifications SET status = $1, updated_at = $2 WHERE id = $3 RETURNING *`, [status, now, id]);
            return result.rows[0] || null;
        }
        finally {
            if (client)
                client.release();
        }
    }
    async recordQualificationAnswer(data) {
        let client = null;
        try {
            const pool = database_1.default.getInstance().getPool();
            client = await pool.connect();
            const id = (0, uuid_1.v4)();
            const now = new Date().toISOString();
            const result = await client.query(`INSERT INTO qualification_answers (id, qualification_id, answer, is_correct, agent_name, created_at, updated_at)
         VALUES ($1, $2, $3, $4, $5, $6, $7) RETURNING *`, [
                id,
                data.qualification_id,
                data.answer,
                data.is_correct,
                data.agent_name || null,
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
    async getAnswersForQualification(qualificationId) {
        let client = null;
        try {
            const pool = database_1.default.getInstance().getPool();
            client = await pool.connect();
            const result = await client.query(`SELECT * FROM qualification_answers WHERE qualification_id = $1 ORDER BY created_at DESC`, [qualificationId]);
            return result.rows;
        }
        finally {
            if (client)
                client.release();
        }
    }
    async getQualificationsByCustomerId(customerId) {
        let client = null;
        try {
            const pool = database_1.default.getInstance().getPool();
            client = await pool.connect();
            const result = await client.query(`SELECT * FROM qualifications WHERE customer_id = $1 ORDER BY created_at DESC`, [customerId]);
            return result.rows;
        }
        finally {
            if (client)
                client.release();
        }
    }
    async getPendingQualifications() {
        let client = null;
        try {
            const pool = database_1.default.getInstance().getPool();
            client = await pool.connect();
            const result = await client.query(`SELECT * FROM qualifications WHERE status = 'pending' ORDER BY created_at ASC`);
            return result.rows;
        }
        finally {
            if (client)
                client.release();
        }
    }
    async deleteQualification(id) {
        let client = null;
        try {
            const pool = database_1.default.getInstance().getPool();
            client = await pool.connect();
            const result = await client.query(`DELETE FROM qualifications WHERE id = $1 RETURNING id`, [id]);
            return result.rowCount !== null && result.rowCount > 0;
        }
        finally {
            if (client)
                client.release();
        }
    }
    async deleteQualificationAnswer(id) {
        let client = null;
        try {
            const pool = database_1.default.getInstance().getPool();
            client = await pool.connect();
            const result = await client.query(`DELETE FROM qualification_answers WHERE id = $1 RETURNING id`, [id]);
            return result.rowCount !== null && result.rowCount > 0;
        }
        finally {
            if (client)
                client.release();
        }
    }
    async getCustomerQualificationSummary() {
        let client = null;
        try {
            const pool = database_1.default.getInstance().getPool();
            client = await pool.connect();
            const result = await client.query(`SELECT
          c.id AS customer_id,
          c.name AS customer_name,
          COUNT(q.id) AS total_qualifications,
          SUM(CASE WHEN q.status = 'completed' THEN 1 ELSE 0 END) AS completed_qualifications,
          SUM(CASE WHEN q.status = 'failed' THEN 1 ELSE 0 END) AS failed_qualifications,
          SUM(CASE WHEN qa.is_correct = TRUE THEN 1 ELSE 0 END) AS correct_answers,
          SUM(CASE WHEN qa.is_correct = FALSE THEN 1 ELSE 0 END) AS incorrect_answers
         FROM customers c
         LEFT JOIN qualifications q ON c.id = q.customer_id
         LEFT JOIN qualification_answers qa ON q.id = qa.qualification_id
         GROUP BY c.id, c.name
         ORDER BY c.name`);
            return result.rows;
        }
        finally {
            if (client)
                client.release();
        }
    }
    async canMoveToStage(customerId, targetStage) {
        // Placeholder logic: A customer can move to a stage if they have at least one completed qualification
        // and no failed qualifications. This is a simplified example.
        const qualifications = await this.getQualificationsByCustomerId(customerId);
        const hasCompletedQualification = qualifications.some(q => q.status === 'completed');
        const hasFailedQualification = qualifications.some(q => q.status === 'failed');
        if (hasFailedQualification) {
            return { allowed: false, reason: 'Customer has failed qualifications.' };
        }
        if (!hasCompletedQualification) {
            return { allowed: false, reason: 'Customer has no completed qualifications.' };
        }
        // Further logic can be added here based on specific targetStage requirements
        return { allowed: true };
    }
    async checkQualification(customerId) {
        const qualifications = await this.getQualificationsByCustomerId(customerId);
        let totalScore = 0;
        let passedCount = 0;
        let failedCount = 0;
        for (const q of qualifications) {
            if (q.status === 'completed') {
                passedCount++;
                // Example scoring: 10 points for each completed qualification
                totalScore += 10;
            }
            else if (q.status === 'failed') {
                failedCount++;
            }
        }
        const is_qualified = passedCount > 0 && failedCount === 0;
        const qualification_score = totalScore;
        let reason;
        if (!is_qualified) {
            if (failedCount > 0) {
                reason = 'Customer failed one or more qualifications.';
            }
            else if (passedCount === 0) {
                reason = 'Customer has not completed any qualifications.';
            }
        }
        return { is_qualified, qualification_score, reason };
    }
}
exports.QualificationService = QualificationService;
exports.qualificationService = new QualificationService();
//# sourceMappingURL=qualificationService.js.map