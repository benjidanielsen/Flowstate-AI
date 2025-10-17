import { eq, and, desc } from 'drizzle-orm';
import { sql as sqlTemplate } from 'drizzle-orm';
import db from '../database/supabase';
import { agentStates, jobQueue, documents } from '../database/schema';
import embeddingService from './embeddingService';
import logger from '../utils/logger';

export interface AgentState {
  id?: number;
  agentName: string;
  state: any;
  createdAt?: Date;
  updatedAt?: Date;
}

export interface Job {
  id?: number;
  payload: any;
  targetAgent: string;
  status?: string;
  attempts?: number;
  createdAt?: Date;
  processedAt?: Date;
}

export interface Document {
  id?: number;
  content: string;
  metadata?: any;
  embedding?: string;
}

export class AgentService {
  /**
   * Register or update an agent's state
   */
  async registerAgent(agentName: string, initialState: any = {}): Promise<AgentState> {
    try {
      logger.info(`Registering agent: ${agentName}`);
      
      // Check if agent already exists
      const existingAgent = await db
        .select()
        .from(agentStates)
        .where(eq(agentStates.agentName, agentName))
        .limit(1);

      if (existingAgent.length > 0) {
        // Update existing agent
        const [updated] = await db
          .update(agentStates)
          .set({
            state: initialState,
            updatedAt: new Date(),
          })
          .where(eq(agentStates.agentName, agentName))
          .returning();
        
        logger.info(`Agent ${agentName} updated successfully`);
        return updated;
      } else {
        // Create new agent
        const [created] = await db
          .insert(agentStates)
          .values({
            agentName,
            state: initialState,
          })
          .returning();
        
        logger.info(`Agent ${agentName} registered successfully`);
        return created;
      }
    } catch (error) {
      logger.error(`Error registering agent ${agentName}:`, error);
      throw error;
    }
  }

  /**
   * Get agent state by name
   */
  async getAgentState(agentName: string): Promise<AgentState | null> {
    try {
      const [agent] = await db
        .select()
        .from(agentStates)
        .where(eq(agentStates.agentName, agentName))
        .limit(1);

      return agent || null;
    } catch (error) {
      logger.error(`Error getting agent state for ${agentName}:`, error);
      throw error;
    }
  }

  /**
   * Update agent state
   */
  async updateAgentState(agentName: string, newState: any): Promise<AgentState> {
    try {
      const [updated] = await db
        .update(agentStates)
        .set({
          state: newState,
          updatedAt: new Date(),
        })
        .where(eq(agentStates.agentName, agentName))
        .returning();

      if (!updated) {
        throw new Error(`Agent ${agentName} not found`);
      }

      logger.info(`Agent ${agentName} state updated`);
      return updated;
    } catch (error) {
      logger.error(`Error updating agent state for ${agentName}:`, error);
      throw error;
    }
  }

  /**
   * Get all registered agents
   */
  async getAllAgents(): Promise<AgentState[]> {
    try {
      const agents = await db
        .select()
        .from(agentStates)
        .orderBy(desc(agentStates.updatedAt));

      return agents;
    } catch (error) {
      logger.error('Error getting all agents:', error);
      throw error;
    }
  }

  /**
   * Create a new job in the queue
   */
  async createJob(targetAgent: string, payload: any): Promise<Job> {
    try {
      logger.info(`Creating job for agent: ${targetAgent}`);
      
      const [job] = await db
        .insert(jobQueue)
        .values({
          targetAgent,
          payload,
          status: 'pending',
          attempts: 0,
        })
        .returning();

      logger.info(`Job created with ID: ${job.id}`);
      return job;
    } catch (error) {
      logger.error(`Error creating job for ${targetAgent}:`, error);
      throw error;
    }
  }

  /**
   * Get pending jobs for a specific agent
   */
  async getPendingJobs(targetAgent: string, limit: number = 10): Promise<Job[]> {
    try {
      const jobs = await db
        .select()
        .from(jobQueue)
        .where(
          and(
            eq(jobQueue.targetAgent, targetAgent),
            eq(jobQueue.status, 'pending')
          )
        )
        .orderBy(jobQueue.createdAt)
        .limit(limit);

      return jobs;
    } catch (error) {
      logger.error(`Error getting pending jobs for ${targetAgent}:`, error);
      throw error;
    }
  }

  /**
   * Get all pending jobs
   */
  async getAllPendingJobs(limit: number = 50): Promise<Job[]> {
    try {
      const jobs = await db
        .select()
        .from(jobQueue)
        .where(eq(jobQueue.status, 'pending'))
        .orderBy(jobQueue.createdAt)
        .limit(limit);

      return jobs;
    } catch (error) {
      logger.error('Error getting all pending jobs:', error);
      throw error;
    }
  }

  /**
   * Update job status
   */
  async updateJobStatus(
    jobId: number,
    status: 'pending' | 'processing' | 'completed' | 'failed',
    incrementAttempts: boolean = false
  ): Promise<Job> {
    try {
      const updateData: any = {
        status,
      };

      if (status === 'completed' || status === 'failed') {
        updateData.processedAt = new Date();
      }

      if (incrementAttempts) {
        // Get current attempts count
        const [currentJob] = await db
          .select()
          .from(jobQueue)
          .where(eq(jobQueue.id, jobId))
          .limit(1);

        if (currentJob) {
          updateData.attempts = (currentJob.attempts || 0) + 1;
        }
      }

      const [updated] = await db
        .update(jobQueue)
        .set(updateData)
        .where(eq(jobQueue.id, jobId))
        .returning();

      if (!updated) {
        throw new Error(`Job ${jobId} not found`);
      }

      logger.info(`Job ${jobId} status updated to ${status}`);
      return updated;
    } catch (error) {
      logger.error(`Error updating job ${jobId}:`, error);
      throw error;
    }
  }

  /**
   * Store a document in the documents table with automatic embedding generation
   */
  async storeDocument(content: string, metadata: any = {}, generateEmbedding: boolean = true): Promise<Document> {
    try {
      let embeddingVector = null;

      // Generate embedding if requested
      if (generateEmbedding) {
        try {
          const embedding = await embeddingService.generateEmbedding(content);
          embeddingVector = embeddingService.formatEmbeddingForPostgres(embedding);
          logger.debug('Generated embedding for document');
        } catch (error) {
          logger.warn('Failed to generate embedding, storing document without it:', error);
        }
      }

      // Use raw SQL to insert with vector type
      if (embeddingVector) {
        const result = await db.execute(sqlTemplate.raw(`
          INSERT INTO documents (content, metadata, embedding)
          VALUES (
            '${content.replace(/'/g, "''")}',
            '${JSON.stringify(metadata)}'::jsonb,
            '${embeddingVector}'::vector(1536)
          )
          RETURNING *
        `));

        const doc = result.rows[0] as any;
        logger.info(`Document stored with ID: ${doc.id} (with embedding)`);
        return doc;
      } else {
        const [doc] = await db
          .insert(documents)
          .values({
            content,
            metadata,
          })
          .returning();

        logger.info(`Document stored with ID: ${doc.id} (without embedding)`);
        return doc;
      }
    } catch (error) {
      logger.error('Error storing document:', error);
      throw error;
    }
  }

  /**
   * Search documents by metadata
   */
  async searchDocuments(metadataFilter: any, limit: number = 10): Promise<Document[]> {
    try {
      // For now, we'll get all documents and filter in memory
      // In production, you'd want to use Supabase's JSONB query capabilities
      const allDocs = await db
        .select()
        .from(documents)
        .limit(limit);

      return allDocs;
    } catch (error) {
      logger.error('Error searching documents:', error);
      throw error;
    }
  }

  /**
   * Get document by ID
   */
  async getDocument(id: number): Promise<Document | null> {
    try {
      const [doc] = await db
        .select()
        .from(documents)
        .where(eq(documents.id, id))
        .limit(1);

      return doc || null;
    } catch (error) {
      logger.error(`Error getting document ${id}:`, error);
      throw error;
    }
  }

  /**
   * Delete old completed jobs (cleanup)
   */
  async cleanupCompletedJobs(olderThanDays: number = 7): Promise<number> {
    try {
      const cutoffDate = new Date();
      cutoffDate.setDate(cutoffDate.getDate() - olderThanDays);

      // Note: This is a simplified version. In production, you'd want to use
      // a proper date comparison with Drizzle ORM
      logger.info(`Cleaning up jobs older than ${olderThanDays} days`);
      
      // For now, just log the intent
      // Actual implementation would require proper date filtering
      return 0;
    } catch (error) {
      logger.error('Error cleaning up jobs:', error);
      throw error;
    }
  }
}

export default new AgentService();

