"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.AgentService = void 0;
const drizzle_orm_1 = require("drizzle-orm");
const supabase_1 = __importDefault(require("../database/supabase"));
const schema_1 = require("../database/schema");
const logger_1 = __importDefault(require("../utils/logger"));
class AgentService {
    /**
     * Register or update an agent's state
     */
    async registerAgent(agentName, initialState = {}) {
        try {
            logger_1.default.info(`Registering agent: ${agentName}`);
            // Check if agent already exists
            const existingAgent = await supabase_1.default
                .select()
                .from(schema_1.agentStates)
                .where((0, drizzle_orm_1.eq)(schema_1.agentStates.agentName, agentName))
                .limit(1);
            if (existingAgent.length > 0) {
                // Update existing agent
                const [updated] = await supabase_1.default
                    .update(schema_1.agentStates)
                    .set({
                    state: initialState,
                    updatedAt: new Date(),
                })
                    .where((0, drizzle_orm_1.eq)(schema_1.agentStates.agentName, agentName))
                    .returning();
                logger_1.default.info(`Agent ${agentName} updated successfully`);
                return updated;
            }
            else {
                // Create new agent
                const [created] = await supabase_1.default
                    .insert(schema_1.agentStates)
                    .values({
                    agentName,
                    state: initialState,
                })
                    .returning();
                logger_1.default.info(`Agent ${agentName} registered successfully`);
                return created;
            }
        }
        catch (error) {
            logger_1.default.error(`Error registering agent ${agentName}:`, error);
            throw error;
        }
    }
    /**
     * Get agent state by name
     */
    async getAgentState(agentName) {
        try {
            const [agent] = await supabase_1.default
                .select()
                .from(schema_1.agentStates)
                .where((0, drizzle_orm_1.eq)(schema_1.agentStates.agentName, agentName))
                .limit(1);
            return agent || null;
        }
        catch (error) {
            logger_1.default.error(`Error getting agent state for ${agentName}:`, error);
            throw error;
        }
    }
    /**
     * Update agent state
     */
    async updateAgentState(agentName, newState) {
        try {
            const [updated] = await supabase_1.default
                .update(schema_1.agentStates)
                .set({
                state: newState,
                updatedAt: new Date(),
            })
                .where((0, drizzle_orm_1.eq)(schema_1.agentStates.agentName, agentName))
                .returning();
            if (!updated) {
                throw new Error(`Agent ${agentName} not found`);
            }
            logger_1.default.info(`Agent ${agentName} state updated`);
            return updated;
        }
        catch (error) {
            logger_1.default.error(`Error updating agent state for ${agentName}:`, error);
            throw error;
        }
    }
    /**
     * Get all registered agents
     */
    async getAllAgents() {
        try {
            const agents = await supabase_1.default
                .select()
                .from(schema_1.agentStates)
                .orderBy((0, drizzle_orm_1.desc)(schema_1.agentStates.updatedAt));
            return agents;
        }
        catch (error) {
            logger_1.default.error('Error getting all agents:', error);
            throw error;
        }
    }
    /**
     * Create a new job in the queue
     */
    async createJob(targetAgent, payload) {
        try {
            logger_1.default.info(`Creating job for agent: ${targetAgent}`);
            const [job] = await supabase_1.default
                .insert(schema_1.jobQueue)
                .values({
                targetAgent,
                payload,
                status: 'pending',
                attempts: 0,
            })
                .returning();
            logger_1.default.info(`Job created with ID: ${job.id}`);
            return job;
        }
        catch (error) {
            logger_1.default.error(`Error creating job for ${targetAgent}:`, error);
            throw error;
        }
    }
    /**
     * Get pending jobs for a specific agent
     */
    async getPendingJobs(targetAgent, limit = 10) {
        try {
            const jobs = await supabase_1.default
                .select()
                .from(schema_1.jobQueue)
                .where((0, drizzle_orm_1.and)((0, drizzle_orm_1.eq)(schema_1.jobQueue.targetAgent, targetAgent), (0, drizzle_orm_1.eq)(schema_1.jobQueue.status, 'pending')))
                .orderBy(schema_1.jobQueue.createdAt)
                .limit(limit);
            return jobs;
        }
        catch (error) {
            logger_1.default.error(`Error getting pending jobs for ${targetAgent}:`, error);
            throw error;
        }
    }
    /**
     * Get all pending jobs
     */
    async getAllPendingJobs(limit = 50) {
        try {
            const jobs = await supabase_1.default
                .select()
                .from(schema_1.jobQueue)
                .where((0, drizzle_orm_1.eq)(schema_1.jobQueue.status, 'pending'))
                .orderBy(schema_1.jobQueue.createdAt)
                .limit(limit);
            return jobs;
        }
        catch (error) {
            logger_1.default.error('Error getting all pending jobs:', error);
            throw error;
        }
    }
    /**
     * Update job status
     */
    async updateJobStatus(jobId, status, incrementAttempts = false) {
        try {
            const updateData = {
                status,
            };
            if (status === 'completed' || status === 'failed') {
                updateData.processedAt = new Date();
            }
            if (incrementAttempts) {
                // Get current attempts count
                const [currentJob] = await supabase_1.default
                    .select()
                    .from(schema_1.jobQueue)
                    .where((0, drizzle_orm_1.eq)(schema_1.jobQueue.id, jobId))
                    .limit(1);
                if (currentJob) {
                    updateData.attempts = (currentJob.attempts || 0) + 1;
                }
            }
            const [updated] = await supabase_1.default
                .update(schema_1.jobQueue)
                .set(updateData)
                .where((0, drizzle_orm_1.eq)(schema_1.jobQueue.id, jobId))
                .returning();
            if (!updated) {
                throw new Error(`Job ${jobId} not found`);
            }
            logger_1.default.info(`Job ${jobId} status updated to ${status}`);
            return updated;
        }
        catch (error) {
            logger_1.default.error(`Error updating job ${jobId}:`, error);
            throw error;
        }
    }
    /**
     * Store a document in the documents table
     */
    async storeDocument(content, metadata = {}, embedding) {
        try {
            const [doc] = await supabase_1.default
                .insert(schema_1.documents)
                .values({
                content,
                metadata,
                embedding,
            })
                .returning();
            logger_1.default.info(`Document stored with ID: ${doc.id}`);
            return doc;
        }
        catch (error) {
            logger_1.default.error('Error storing document:', error);
            throw error;
        }
    }
    /**
     * Search documents by metadata
     */
    async searchDocuments(metadataFilter, limit = 10) {
        try {
            // For now, we'll get all documents and filter in memory
            // In production, you'd want to use Supabase's JSONB query capabilities
            const allDocs = await supabase_1.default
                .select()
                .from(schema_1.documents)
                .limit(limit);
            return allDocs;
        }
        catch (error) {
            logger_1.default.error('Error searching documents:', error);
            throw error;
        }
    }
    /**
     * Get document by ID
     */
    async getDocument(id) {
        try {
            const [doc] = await supabase_1.default
                .select()
                .from(schema_1.documents)
                .where((0, drizzle_orm_1.eq)(schema_1.documents.id, id))
                .limit(1);
            return doc || null;
        }
        catch (error) {
            logger_1.default.error(`Error getting document ${id}:`, error);
            throw error;
        }
    }
    /**
     * Delete old completed jobs (cleanup)
     */
    async cleanupCompletedJobs(olderThanDays = 7) {
        try {
            const cutoffDate = new Date();
            cutoffDate.setDate(cutoffDate.getDate() - olderThanDays);
            // Note: This is a simplified version. In production, you'd want to use
            // a proper date comparison with Drizzle ORM
            logger_1.default.info(`Cleaning up jobs older than ${olderThanDays} days`);
            // For now, just log the intent
            // Actual implementation would require proper date filtering
            return 0;
        }
        catch (error) {
            logger_1.default.error('Error cleaning up jobs:', error);
            throw error;
        }
    }
}
exports.AgentService = AgentService;
exports.default = new AgentService();
//# sourceMappingURL=agentService.js.map