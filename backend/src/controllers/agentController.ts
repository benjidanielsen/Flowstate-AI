import { Request, Response } from 'express';
import agentService from '../services/agentService';
import logger from '../utils/logger';

export class AgentController {
  /**
   * Register a new agent
   */
  async registerAgent(req: Request, res: Response): Promise<void> {
    try {
      const { agentName, initialState } = req.body;

      if (!agentName) {
        res.status(400).json({ error: 'agentName is required' });
        return;
      }

      const agent = await agentService.registerAgent(agentName, initialState || {});
      res.status(201).json(agent);
    } catch (error: any) {
      logger.error('Error in registerAgent:', error);
      res.status(500).json({ error: error.message });
    }
  }

  /**
   * Get agent state
   */
  async getAgentState(req: Request, res: Response): Promise<void> {
    try {
      const { agentName } = req.params;

      const agent = await agentService.getAgentState(agentName);
      
      if (!agent) {
        res.status(404).json({ error: 'Agent not found' });
        return;
      }

      res.json(agent);
    } catch (error: any) {
      logger.error('Error in getAgentState:', error);
      res.status(500).json({ error: error.message });
    }
  }

  /**
   * Update agent state
   */
  async updateAgentState(req: Request, res: Response): Promise<void> {
    try {
      const { agentName } = req.params;
      const { state } = req.body;

      if (!state) {
        res.status(400).json({ error: 'state is required' });
        return;
      }

      const agent = await agentService.updateAgentState(agentName, state);
      res.json(agent);
    } catch (error: any) {
      logger.error('Error in updateAgentState:', error);
      res.status(500).json({ error: error.message });
    }
  }

  /**
   * Get all agents
   */
  async getAllAgents(req: Request, res: Response): Promise<void> {
    try {
      const agents = await agentService.getAllAgents();
      res.json(agents);
    } catch (error: any) {
      logger.error('Error in getAllAgents:', error);
      res.status(500).json({ error: error.message });
    }
  }

  /**
   * Create a new job
   */
  async createJob(req: Request, res: Response): Promise<void> {
    try {
      const { targetAgent, payload } = req.body;

      if (!targetAgent || !payload) {
        res.status(400).json({ error: 'targetAgent and payload are required' });
        return;
      }

      const job = await agentService.createJob(targetAgent, payload);
      res.status(201).json(job);
    } catch (error: any) {
      logger.error('Error in createJob:', error);
      res.status(500).json({ error: error.message });
    }
  }

  /**
   * Get pending jobs for an agent
   */
  async getPendingJobs(req: Request, res: Response): Promise<void> {
    try {
      const { agentName } = req.params;
      const limit = parseInt(req.query.limit as string) || 10;

      const jobs = await agentService.getPendingJobs(agentName, limit);
      res.json(jobs);
    } catch (error: any) {
      logger.error('Error in getPendingJobs:', error);
      res.status(500).json({ error: error.message });
    }
  }

  /**
   * Get all pending jobs
   */
  async getAllPendingJobs(req: Request, res: Response): Promise<void> {
    try {
      const limit = parseInt(req.query.limit as string) || 50;

      const jobs = await agentService.getAllPendingJobs(limit);
      res.json(jobs);
    } catch (error: any) {
      logger.error('Error in getAllPendingJobs:', error);
      res.status(500).json({ error: error.message });
    }
  }

  /**
   * Update job status
   */
  async updateJobStatus(req: Request, res: Response): Promise<void> {
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

      const job = await agentService.updateJobStatus(
        parseInt(jobId),
        status,
        incrementAttempts || false
      );
      res.json(job);
    } catch (error: any) {
      logger.error('Error in updateJobStatus:', error);
      res.status(500).json({ error: error.message });
    }
  }

  /**
   * Store a document
   */
  async storeDocument(req: Request, res: Response): Promise<void> {
    try {
      const { content, metadata, embedding } = req.body;

      if (!content) {
        res.status(400).json({ error: 'content is required' });
        return;
      }

      const doc = await agentService.storeDocument(content, metadata, embedding);
      res.status(201).json(doc);
    } catch (error: any) {
      logger.error('Error in storeDocument:', error);
      res.status(500).json({ error: error.message });
    }
  }

  /**
   * Get document by ID
   */
  async getDocument(req: Request, res: Response): Promise<void> {
    try {
      const { id } = req.params;

      const doc = await agentService.getDocument(parseInt(id));
      
      if (!doc) {
        res.status(404).json({ error: 'Document not found' });
        return;
      }

      res.json(doc);
    } catch (error: any) {
      logger.error('Error in getDocument:', error);
      res.status(500).json({ error: error.message });
    }
  }

  /**
   * Search documents
   */
  async searchDocuments(req: Request, res: Response): Promise<void> {
    try {
      const { metadata, limit } = req.query;

      const docs = await agentService.searchDocuments(
        metadata ? JSON.parse(metadata as string) : {},
        limit ? parseInt(limit as string) : 10
      );
      res.json(docs);
    } catch (error: any) {
      logger.error('Error in searchDocuments:', error);
      res.status(500).json({ error: error.message });
    }
  }
}

export default new AgentController();

