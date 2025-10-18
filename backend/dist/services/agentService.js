"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.agentService = exports.AgentService = void 0;
const database_1 = __importDefault(require("../database"));
const piiRedaction_1 = require("../utils/piiRedaction");
const types_1 = require("../types");
const embeddingService_1 = require("./embeddingService");
class AgentService {
    constructor() {
        this.dbManager = database_1.default.getInstance();
        this.embeddingService = new embeddingService_1.EmbeddingService();
    }
    async registerAgent(agent) {
        let client = null;
        try {
            const pool = this.dbManager.getPool();
            client = await pool.connect();
            const result = await client.query('INSERT INTO agent_states(name, status, last_heartbeat, metadata) VALUES($1, $2, $3, $4) RETURNING *', [agent.name, agent.status, agent.last_heartbeat, agent.metadata]);
            piiRedaction_1.safeLogger.info(`Agent ${agent.name} registered successfully.`);
            return result.rows[0];
        }
        catch (error) {
            piiRedaction_1.safeLogger.error(`Error registering agent ${agent.name}:`, error);
            throw error;
        }
        finally {
            if (client)
                client.release();
        }
    }
    async getAgentState(agentName) {
        let client = null;
        try {
            const pool = this.dbManager.getPool();
            client = await pool.connect();
            const result = await client.query('SELECT * FROM agent_states WHERE name = $1', [agentName]);
            return result.rows[0] || null;
        }
        catch (error) {
            piiRedaction_1.safeLogger.error(`Error fetching agent state for ${agentName}:`, error);
            throw error;
        }
        finally {
            if (client)
                client.release();
        }
    }
    async getAllAgents() {
        let client = null;
        try {
            const pool = this.dbManager.getPool();
            client = await pool.connect();
            const result = await client.query('SELECT * FROM agent_states');
            return result.rows;
        }
        catch (error) {
            piiRedaction_1.safeLogger.error('Error fetching all agents:', error);
            throw error;
        }
        finally {
            if (client)
                client.release();
        }
    }
    async updateAgentState(agentName, status, metadata) {
        let client = null;
        try {
            const pool = this.dbManager.getPool();
            client = await pool.connect();
            const result = await client.query('UPDATE agent_states SET status = $1, last_heartbeat = NOW(), metadata = $2 WHERE name = $3 RETURNING *', [status, metadata, agentName]);
            piiRedaction_1.safeLogger.info(`Agent ${agentName} state updated to ${status}.`);
            return result.rows[0] || null;
        }
        catch (error) {
            piiRedaction_1.safeLogger.error(`Error updating agent state for ${agentName}:`, error);
            throw error;
        }
        finally {
            if (client)
                client.release();
        }
    }
    async createJob(job) {
        let client = null;
        try {
            const pool = this.dbManager.getPool();
            client = await pool.connect();
            const result = await client.query('INSERT INTO job_queue(agent_name, task_type, payload, priority, correlation_id, status) VALUES($1, $2, $3, $4, $5, $6) RETURNING *', [job.agent_name, job.task_type, job.payload, job.priority || 0, job.correlation_id, types_1.JobStatus.PENDING]);
            piiRedaction_1.safeLogger.info(`Job created for agent ${job.agent_name} with task type ${job.task_type}.`);
            return result.rows[0];
        }
        catch (error) {
            piiRedaction_1.safeLogger.error(`Error creating job for agent ${job.agent_name}:`, error);
            throw error;
        }
        finally {
            if (client)
                client.release();
        }
    }
    async getPendingJobs(agentName) {
        let client = null;
        try {
            const pool = this.dbManager.getPool();
            client = await pool.connect();
            const result = await client.query('SELECT * FROM job_queue WHERE agent_name = $1 AND status = $2 ORDER BY priority DESC, created_at ASC', [agentName, types_1.JobStatus.PENDING]);
            return result.rows;
        }
        catch (error) {
            piiRedaction_1.safeLogger.error(`Error fetching pending jobs for ${agentName}:`, error);
            throw error;
        }
        finally {
            if (client)
                client.release();
        }
    }
    async getAllPendingJobs() {
        let client = null;
        try {
            const pool = this.dbManager.getPool();
            client = await pool.connect();
            const result = await client.query('SELECT * FROM job_queue WHERE status = $1 ORDER BY priority DESC, created_at ASC', [types_1.JobStatus.PENDING]);
            return result.rows;
        }
        catch (error) {
            piiRedaction_1.safeLogger.error('Error fetching all pending jobs:', error);
            throw error;
        }
        finally {
            if (client)
                client.release();
        }
    }
    async updateJobStatus(jobId, status, resultPayload) {
        let client = null;
        try {
            const pool = this.dbManager.getPool();
            client = await pool.connect();
            const result = await client.query('UPDATE job_queue SET status = $1, result = $2, updated_at = NOW() WHERE id = $3 RETURNING *', [status, resultPayload, jobId]);
            piiRedaction_1.safeLogger.info(`Job ${jobId} status updated to ${status}.`);
            return result.rows[0] || null;
        }
        catch (error) {
            piiRedaction_1.safeLogger.error(`Error updating job ${jobId} status:`, error);
            throw error;
        }
        finally {
            if (client)
                client.release();
        }
    }
    async storeDocument(document) {
        let client = null;
        try {
            const pool = this.dbManager.getPool();
            client = await pool.connect();
            const embedding = await this.embeddingService.generateEmbedding(document.content);
            const result = await client.query('INSERT INTO documents(agent_name, type, content, metadata, tags, importance, embedding) VALUES($1, $2, $3, $4, $5, $6, $7) RETURNING *', [document.agent_name, document.type, document.content, document.metadata, document.tags, document.importance, embedding]);
            piiRedaction_1.safeLogger.info(`Document stored for agent ${document.agent_name} with type ${document.type}.`);
            return result.rows[0];
        }
        catch (error) {
            piiRedaction_1.safeLogger.error(`Error storing document for agent ${document.agent_name}:`, error);
            throw error;
        }
        finally {
            if (client)
                client.release();
        }
    }
    async getDocument(documentId) {
        let client = null;
        try {
            const pool = this.dbManager.getPool();
            client = await pool.connect();
            const result = await client.query('SELECT * FROM documents WHERE id = $1', [documentId]);
            return result.rows[0] || null;
        }
        catch (error) {
            piiRedaction_1.safeLogger.error(`Error fetching document ${documentId}:`, error);
            throw error;
        }
        finally {
            if (client)
                client.release();
        }
    }
    async searchDocuments(query, agentName, type, tags) {
        let client = null;
        try {
            const pool = this.dbManager.getPool();
            client = await pool.connect();
            let baseQuery = 'SELECT * FROM documents WHERE 1=1';
            const params = [];
            let paramIndex = 1;
            if (agentName) {
                baseQuery += ` AND agent_name = $${paramIndex++}`;
                params.push(agentName);
            }
            if (type) {
                baseQuery += ` AND type = $${paramIndex++}`;
                params.push(type);
            }
            if (tags && tags.length > 0) {
                baseQuery += ` AND tags && $${paramIndex++}::text[]`; // Using '&&' operator for array overlap
                params.push(tags);
            }
            if (query) {
                baseQuery += ` AND content ILIKE $${paramIndex++}`; // Case-insensitive search
                params.push(`%${query}%`);
            }
            const result = await client.query(baseQuery, params);
            return result.rows;
        }
        catch (error) {
            piiRedaction_1.safeLogger.error(`Error searching documents with query '${query}' for agent ${agentName}:`, error);
            throw error;
        }
        finally {
            if (client)
                client.release();
        }
    }
    async deleteDocument(documentId) {
        let client = null;
        try {
            const pool = this.dbManager.getPool();
            client = await pool.connect();
            const result = await client.query('DELETE FROM documents WHERE id = $1 RETURNING id', [documentId]);
            piiRedaction_1.safeLogger.info(`Document ${documentId} deleted.`);
            return result.rowCount !== null && result.rowCount > 0;
        }
        finally {
            if (client)
                client.release();
        }
    }
}
exports.AgentService = AgentService;
exports.agentService = new AgentService();
//# sourceMappingURL=agentService.js.map