import { agentService } from './agentService';
import logger from '../utils/logger';
import axios from 'axios';
import { JobStatus, Job } from '../types';

export interface JobProcessorConfig {
  pythonWorkerUrl: string;
  pollInterval: number; // in milliseconds
  maxRetries: number;
}

export class JobProcessorService {
  private config: JobProcessorConfig;
  private isRunning: boolean = false;
  private intervalId: NodeJS.Timeout | null = null;

  constructor(config?: Partial<JobProcessorConfig>) {
    this.config = {
      pythonWorkerUrl: process.env.PYTHON_WORKER_URL || 'http://localhost:8000',
      pollInterval: parseInt(process.env.JOB_POLL_INTERVAL || '5000'),
      maxRetries: parseInt(process.env.JOB_MAX_RETRIES || '3'),
      ...config,
    };
  }

  /**
   * Start the job processor
   */
  start(): void {
    if (this.isRunning) {
      logger.warn('Job processor is already running');
      return;
    }

    logger.info('Starting job processor', {
      pollInterval: this.config.pollInterval,
      maxRetries: this.config.maxRetries,
    });

    this.isRunning = true;
    this.intervalId = setInterval(() => {
      this.processJobs().catch((error) => {
        logger.error('Error in job processing cycle:', error);
      });
    }, this.config.pollInterval);
  }

  /**
   * Stop the job processor
   */
  stop(): void {
    if (!this.isRunning) {
      logger.warn('Job processor is not running');
      return;
    }

    logger.info('Stopping job processor');
    this.isRunning = false;
    
    if (this.intervalId) {
      clearInterval(this.intervalId);
      this.intervalId = null;
    }
  }

  /**
   * Process pending jobs
   */
  private async processJobs(): Promise<void> {
    try {
      // Get all pending jobs
      const jobs = await agentService.getAllPendingJobs();

      if (jobs.length === 0) {
        logger.debug('No pending jobs to process');
        return;
      }

      logger.info(`Processing ${jobs.length} pending jobs`);

      // Process each job
      for (const job of jobs) {
        try {
          await this.processJob(job);
        } catch (error) {
          logger.error(`Error processing job ${job.id}:`, error);
        }
      }
    } catch (error) {
      logger.error('Error fetching pending jobs:', error);
    }
  }

  /**
   * Process a single job
   */
  private async processJob(job: Job): Promise<void> {
    const jobId = job.id;
    const targetAgent = job.agent_name;
    const payload = job.payload;
    const attempts = job.payload?.attempts || 0; // Assuming attempts is part of payload

    logger.info(`Processing job ${jobId} for agent ${targetAgent}`, { attempts });

    // Check if max retries exceeded
    if (attempts >= this.config.maxRetries) {
      logger.error(`Job ${jobId} exceeded max retries (${this.config.maxRetries})`);
      await agentService.updateJobStatus(jobId, JobStatus.FAILED);
      return;
    }

    try {
      // Mark job as processing
      await agentService.updateJobStatus(jobId, JobStatus.PROCESSING, { ...job.payload, attempts: attempts + 1 });

      // Execute the job based on the target agent
      const result = await this.executeJob(targetAgent, payload);

      // Mark job as completed
      await agentService.updateJobStatus(jobId, JobStatus.COMPLETED, result);

      logger.info(`Job ${jobId} completed successfully`, { result });
    } catch (error: any) {
      logger.error(`Job ${jobId} failed:`, error);

      // If we haven't exceeded max retries, mark as pending for retry
      if (attempts + 1 < this.config.maxRetries) {
        await agentService.updateJobStatus(jobId, JobStatus.PENDING, { ...job.payload, attempts: attempts + 1 });
        logger.info(`Job ${jobId} will be retried (attempt ${attempts + 1}/${this.config.maxRetries})`);
      } else {
        await agentService.updateJobStatus(jobId, JobStatus.FAILED, { ...job.payload, attempts: attempts + 1, error: error.message });
        logger.error(`Job ${jobId} failed permanently after ${attempts + 1} attempts`);
      }
    }
  }

  /**
   * Execute a job by delegating to the appropriate agent
   */
  private async executeJob(targetAgent: string, payload: any): Promise<any> {
    logger.info(`Executing job for agent ${targetAgent}`, { payload });

    // Get the agent's current state
    const agentState = await agentService.getAgentState(targetAgent);

    if (!agentState) {
      throw new Error(`Agent ${targetAgent} not found`);
    }

    // Determine the job type from the payload
    const jobType = payload.type || 'generic';

    // Route the job to the appropriate handler
    switch (jobType) {
      case 'ai_task':
        return await this.executeAITask(targetAgent, payload);
      
      case 'data_processing':
        return await this.executeDataProcessing(targetAgent, payload);
      
      case 'inter_agent_message':
        return await this.handleInterAgentMessage(targetAgent, payload);
      
      default:
        logger.warn(`Unknown job type: ${jobType}, executing as generic task`);
        return await this.executeGenericTask(targetAgent, payload);
    }
  }

  /**
   * Execute an AI task via the Python worker
   */
  private async executeAITask(targetAgent: string, payload: any): Promise<any> {
    try {
      const response = await axios.post(
        `${this.config.pythonWorkerUrl}/ai-task/${payload.taskType || 'generic'}`,
        {
          agent: targetAgent,
          ...payload.data,
        }
      );

      return response.data;
    } catch (error: any) {
      logger.error(`Error executing AI task for ${targetAgent}:`, error);
      throw new Error(`AI task execution failed: ${error.message}`);
    }
  }

  /**
   * Execute a data processing task
   */
  private async executeDataProcessing(targetAgent: string, payload: any): Promise<any> {
    logger.info(`Executing data processing task for ${targetAgent}`, { payload });

    // Update agent state to reflect processing
    const currentState = await agentService.getAgentState(targetAgent);
    await agentService.updateAgentState(targetAgent, 'active', {
      ...currentState?.metadata,
      lastProcessedJob: payload,
      lastProcessedAt: new Date().toISOString(),
    });

    return { status: 'processed', agent: targetAgent };
  }

  /**
   * Handle inter-agent message
   */
  private async handleInterAgentMessage(targetAgent: string, payload: any): Promise<any> {
    logger.info(`Handling inter-agent message for ${targetAgent}`, { payload });

    const { fromAgent, message, messageType } = payload;

    // Store the message in the agent's state
    const currentState = await agentService.getAgentState(targetAgent);
    const messages = currentState?.metadata?.messages || [];
    
    messages.push({
      from: fromAgent,
      message,
      type: messageType,
      timestamp: new Date().toISOString(),
    });

    await agentService.updateAgentState(targetAgent, 'active', {
      ...currentState?.metadata,
      messages,
      lastMessageAt: new Date().toISOString(),
    });

    // If the message requires a response, create a job for the sending agent
    if (payload.requiresResponse) {
      const newJob: Omit<Job, 'id' | 'created_at' | 'updated_at' | 'status'> = {
        agent_name: fromAgent,
        task_type: 'inter_agent_message',
        payload: {
          fromAgent: targetAgent,
          message: `Response to: ${message}`,
          messageType: 'response',
          requiresResponse: false,
        },
        priority: 0,
        correlation_id: payload.correlation_id || 'default',
      };
      await agentService.createJob(newJob);
    }

    return { status: 'message_received', agent: targetAgent };
  }

  /**
   * Execute a generic task
   */
  private async executeGenericTask(targetAgent: string, payload: any): Promise<any> {
    logger.info(`Executing generic task for ${targetAgent}`, { payload });

    // Update agent state
    const currentState = await agentService.getAgentState(targetAgent);
    await agentService.updateAgentState(targetAgent, 'active', {
      ...currentState?.metadata,
      lastGenericTask: payload,
      lastTaskAt: new Date().toISOString(),
    });

    return { status: 'completed', agent: targetAgent };
  }

  /**
   * Send a message from one agent to another
   */
  async sendInterAgentMessage(
    fromAgent: string,
    toAgent: string,
    message: string,
    messageType: string = 'info',
    requiresResponse: boolean = false
  ): Promise<any> {
    logger.info(`Sending message from ${fromAgent} to ${toAgent}`);

    const newJob: Omit<Job, 'id' | 'created_at' | 'updated_at' | 'status'> = {
      agent_name: toAgent,
      task_type: 'inter_agent_message',
      payload: {
        fromAgent,
        message,
        messageType,
        requiresResponse,
      },
      priority: 0,
      correlation_id: 'default', // Or generate a new one
    };

    return await agentService.createJob(newJob);
  }

  /**
   * Get job processor status
   */
  getStatus(): { isRunning: boolean; config: JobProcessorConfig } {
    return {
      isRunning: this.isRunning,
      config: this.config,
    };
  }
}

export default new JobProcessorService();

