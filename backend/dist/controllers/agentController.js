"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.AgentController = void 0;
const agentService_1 = __importDefault(require("../services/agentService"));
const logger_1 = __importDefault(require("../utils/logger"));
class AgentController {
    /**
     * Register a new agent
     */
    async registerAgent(req, res) {
        try {
            const { agentName, initialState } = req.body;
            if (!agentName) {
                res.status(400).json({ error: 'agentName is required' });
                return;
            }
            const agent = await agentService_1.default.registerAgent(agentName, initialState || {});
            res.status(201).json(agent);
        }
        catch (error) {
            logger_1.default.error('Error in registerAgent:', error);
            res.status(500).json({ error: error.message });
        }
    }
    /**
     * Get agent state
     */
    async getAgentState(req, res) {
        try {
            const { agentName } = req.params;
            const agent = await agentService_1.default.getAgentState(agentName);
            if (!agent) {
                res.status(404).json({ error: 'Agent not found' });
                return;
            }
            res.json(agent);
        }
        catch (error) {
            logger_1.default.error('Error in getAgentState:', error);
            res.status(500).json({ error: error.message });
        }
    }
    /**
     * Update agent state
     */
    async updateAgentState(req, res) {
        try {
            const { agentName } = req.params;
            const { state } = req.body;
            if (!state) {
                res.status(400).json({ error: 'state is required' });
                return;
            }
            const agent = await agentService_1.default.updateAgentState(agentName, state);
            res.json(agent);
        }
        catch (error) {
            logger_1.default.error('Error in updateAgentState:', error);
            res.status(500).json({ error: error.message });
        }
    }
    /**
     * Get all agents
     */
    async getAllAgents(req, res) {
        try {
            const agents = await agentService_1.default.getAllAgents();
            res.json(agents);
        }
        catch (error) {
            logger_1.default.error('Error in getAllAgents:', error);
            res.status(500).json({ error: error.message });
        }
    }
    /**
     * Create a new job
     */
    async createJob(req, res) {
        try {
            const { targetAgent, payload } = req.body;
            if (!targetAgent || !payload) {
                res.status(400).json({ error: 'targetAgent and payload are required' });
                return;
            }
            const job = await agentService_1.default.createJob(targetAgent, payload);
            res.status(201).json(job);
        }
        catch (error) {
            logger_1.default.error('Error in createJob:', error);
            res.status(500).json({ error: error.message });
        }
    }
    /**
     * Get pending jobs for an agent
     */
    async getPendingJobs(req, res) {
        try {
            const { agentName } = req.params;
            const limit = parseInt(req.query.limit) || 10;
            const jobs = await agentService_1.default.getPendingJobs(agentName, limit);
            res.json(jobs);
        }
        catch (error) {
            logger_1.default.error('Error in getPendingJobs:', error);
            res.status(500).json({ error: error.message });
        }
    }
    /**
     * Get all pending jobs
     */
    async getAllPendingJobs(req, res) {
        try {
            const limit = parseInt(req.query.limit) || 50;
            const jobs = await agentService_1.default.getAllPendingJobs(limit);
            res.json(jobs);
        }
        catch (error) {
            logger_1.default.error('Error in getAllPendingJobs:', error);
            res.status(500).json({ error: error.message });
        }
    }
    /**
     * Update job status
     */
    async updateJobStatus(req, res) {
        try {
            const { jobId } = req.params;
            const { status, incrementAttempts } = req.body;
            if (!status) {
                res.status(400).json({ error: 'status is required' });
                return;
            }
            if (!['pending', 'processing', 'completed', 'failed'].includes(status)) {
                res.status(400).json({ error: 'Invalid status value' });
                return;
            }
            const job = await agentService_1.default.updateJobStatus(parseInt(jobId), status, incrementAttempts || false);
            res.json(job);
        }
        catch (error) {
            logger_1.default.error('Error in updateJobStatus:', error);
            res.status(500).json({ error: error.message });
        }
    }
    /**
     * Store a document
     */
    async storeDocument(req, res) {
        try {
            const { content, metadata, embedding } = req.body;
            if (!content) {
                res.status(400).json({ error: 'content is required' });
                return;
            }
            const doc = await agentService_1.default.storeDocument(content, metadata, embedding);
            res.status(201).json(doc);
        }
        catch (error) {
            logger_1.default.error('Error in storeDocument:', error);
            res.status(500).json({ error: error.message });
        }
    }
    /**
     * Get document by ID
     */
    async getDocument(req, res) {
        try {
            const { id } = req.params;
            const doc = await agentService_1.default.getDocument(parseInt(id));
            if (!doc) {
                res.status(404).json({ error: 'Document not found' });
                return;
            }
            res.json(doc);
        }
        catch (error) {
            logger_1.default.error('Error in getDocument:', error);
            res.status(500).json({ error: error.message });
        }
    }
    /**
     * Search documents
     */
    async searchDocuments(req, res) {
        try {
            const { metadata, limit } = req.query;
            const docs = await agentService_1.default.searchDocuments(metadata ? JSON.parse(metadata) : {}, limit ? parseInt(limit) : 10);
            res.json(docs);
        }
        catch (error) {
            logger_1.default.error('Error in searchDocuments:', error);
            res.status(500).json({ error: error.message });
        }
    }
}
exports.AgentController = AgentController;
exports.default = new AgentController();
//# sourceMappingURL=agentController.js.map