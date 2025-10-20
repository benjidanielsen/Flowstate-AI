import { Request, Response } from 'express';
import { agentService } from '../services/agentService';
import logger from '../utils/logger';
import { AgentState, Job } from '../types';

export class AgentController {
  /**
   * Register a new agent
   */
  async registerAgent(req: Request, res: Response): Promise<void> {
    try {
      const { name, status, metadata } = req.body;

      if (!name || !status) {
        res.status(400).json({ error: 'Agent name and status are required' });
        return;
      }

      const newAgent: AgentState = {
        name,
        status,
        last_heartbeat: new Date(),
        metadata: metadata || {},
      };

      const agent = await agentService.registerAgent(newAgent);
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
      const { status, metadata } = req.body;

      if (!status) {
        res.status(400).json({ error: 'status is required' });
        return;
      }

      const agent = await agentService.updateAgentState(agentName, status, metadata || {});
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
      const { agent_name, task_type, payload, priority, correlation_id } = req.body;

      if (!agent_name || !task_type || !payload) {
        res.status(400).json({ error: 'agent_name, task_type, and payload are required' });
        return;
      }

      const newJob: Omit<Job, 'id' | 'created_at' | 'updated_at' | 'status'> = {
        agent_name,
        task_type,
        payload,
        priority: priority || 0,
        correlation_id: correlation_id || 'default',
      };

      const job = await agentService.createJob(newJob);
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

      const jobs = await agentService.getPendingJobs(agentName);
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
      const jobs = await agentService.getAllPendingJobs();
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
      const { status, resultPayload } = req.body;

      if (!status) {
        res.status(400).json({ error: 'status is required' });
        return;
      }

      const job = await agentService.updateJobStatus(jobId, status, resultPayload);
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

      const doc = await agentService.storeDocument(newDocument);
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

      const doc = await agentService.getDocument(id);
      
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
      const { query, agentName, type, tags } = req.query;

      const docs = await agentService.searchDocuments(
        query as string || '',
        agentName as string,
        type as string,
        tags ? (tags as string).split(',') : undefined
      );
      res.json(docs);
    } catch (error: any) {
      logger.error('Error in searchDocuments:', error);
      res.status(500).json({ error: error.message });
    }
  }
}

export default new AgentController();

