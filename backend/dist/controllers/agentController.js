"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.AgentController = void 0;
const agentService_1 = require("../services/agentService");
const logger_1 = __importDefault(require("../utils/logger"));
class AgentController {
    /**
     * Register a new agent
     */
    async registerAgent(req, res) {
        try {
            const { name, status, metadata } = req.body;
            if (!name || !status) {
                res.status(400).json({ error: 'Agent name and status are required' });
                return;
            }
            const newAgent = {
                name,
                status,
                last_heartbeat: new Date(),
                metadata: metadata || {},
            };
            const agent = await agentService_1.agentService.registerAgent(newAgent);
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
            const agent = await agentService_1.agentService.getAgentState(agentName);
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
            const { status, metadata } = req.body;
            if (!status) {
                res.status(400).json({ error: 'status is required' });
                return;
            }
            const agent = await agentService_1.agentService.updateAgentState(agentName, status, metadata || {});
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
            const agents = await agentService_1.agentService.getAllAgents();
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
            const { agent_name, task_type, payload, priority, correlation_id } = req.body;
            if (!agent_name || !task_type || !payload) {
                res.status(400).json({ error: 'agent_name, task_type, and payload are required' });
                return;
            }
            const newJob = {
                agent_name,
                task_type,
                payload,
                priority: priority || 0,
                correlation_id: correlation_id || 'default',
            };
            const job = await agentService_1.agentService.createJob(newJob);
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
            const jobs = await agentService_1.agentService.getPendingJobs(agentName);
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
            const jobs = await agentService_1.agentService.getAllPendingJobs();
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
            const { status, resultPayload } = req.body;
            if (!status) {
                res.status(400).json({ error: 'status is required' });
                return;
            }
            const job = await agentService_1.agentService.updateJobStatus(jobId, status, resultPayload);
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
            const { agent_name, type, content, metadata, tags, importance } = req.body;
            if (!agent_name || !content) {
                res.status(400).json({ error: 'agent_name and content are required' });
                return;
            }
            const newDocument = {
                agent_name,
                type: type || 'general',
                content,
                metadata: metadata || {},
                tags: tags || [],
                importance: importance || 5,
            };
            const doc = await agentService_1.agentService.storeDocument(newDocument);
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
            const doc = await agentService_1.agentService.getDocument(id);
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
            const { query, agentName, type, tags } = req.query;
            const docs = await agentService_1.agentService.searchDocuments(query || '', agentName, type, tags ? tags.split(',') : undefined);
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