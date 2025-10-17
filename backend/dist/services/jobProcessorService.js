"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.JobProcessorService = void 0;
const agentService_1 = __importDefault(require("./agentService"));
const logger_1 = __importDefault(require("../utils/logger"));
const axios_1 = __importDefault(require("axios"));
class JobProcessorService {
    constructor(config) {
        this.isRunning = false;
        this.intervalId = null;
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
    start() {
        if (this.isRunning) {
            logger_1.default.warn('Job processor is already running');
            return;
        }
        logger_1.default.info('Starting job processor', {
            pollInterval: this.config.pollInterval,
            maxRetries: this.config.maxRetries,
        });
        this.isRunning = true;
        this.intervalId = setInterval(() => {
            this.processJobs().catch((error) => {
                logger_1.default.error('Error in job processing cycle:', error);
            });
        }, this.config.pollInterval);
    }
    /**
     * Stop the job processor
     */
    stop() {
        if (!this.isRunning) {
            logger_1.default.warn('Job processor is not running');
            return;
        }
        logger_1.default.info('Stopping job processor');
        this.isRunning = false;
        if (this.intervalId) {
            clearInterval(this.intervalId);
            this.intervalId = null;
        }
    }
    /**
     * Process pending jobs
     */
    async processJobs() {
        try {
            // Get all pending jobs
            const jobs = await agentService_1.default.getAllPendingJobs(10);
            if (jobs.length === 0) {
                logger_1.default.debug('No pending jobs to process');
                return;
            }
            logger_1.default.info(`Processing ${jobs.length} pending jobs`);
            // Process each job
            for (const job of jobs) {
                try {
                    await this.processJob(job);
                }
                catch (error) {
                    logger_1.default.error(`Error processing job ${job.id}:`, error);
                }
            }
        }
        catch (error) {
            logger_1.default.error('Error fetching pending jobs:', error);
        }
    }
    /**
     * Process a single job
     */
    async processJob(job) {
        const jobId = job.id;
        const targetAgent = job.targetAgent;
        const payload = job.payload;
        const attempts = job.attempts || 0;
        logger_1.default.info(`Processing job ${jobId} for agent ${targetAgent}`, { attempts });
        // Check if max retries exceeded
        if (attempts >= this.config.maxRetries) {
            logger_1.default.error(`Job ${jobId} exceeded max retries (${this.config.maxRetries})`);
            await agentService_1.default.updateJobStatus(jobId, 'failed');
            return;
        }
        try {
            // Mark job as processing
            await agentService_1.default.updateJobStatus(jobId, 'processing', true);
            // Execute the job based on the target agent
            const result = await this.executeJob(targetAgent, payload);
            // Mark job as completed
            await agentService_1.default.updateJobStatus(jobId, 'completed');
            logger_1.default.info(`Job ${jobId} completed successfully`, { result });
        }
        catch (error) {
            logger_1.default.error(`Job ${jobId} failed:`, error);
            // If we haven't exceeded max retries, mark as pending for retry
            if (attempts + 1 < this.config.maxRetries) {
                await agentService_1.default.updateJobStatus(jobId, 'pending');
                logger_1.default.info(`Job ${jobId} will be retried (attempt ${attempts + 1}/${this.config.maxRetries})`);
            }
            else {
                await agentService_1.default.updateJobStatus(jobId, 'failed');
                logger_1.default.error(`Job ${jobId} failed permanently after ${attempts + 1} attempts`);
            }
        }
    }
    /**
     * Execute a job by delegating to the appropriate agent
     */
    async executeJob(targetAgent, payload) {
        logger_1.default.info(`Executing job for agent ${targetAgent}`, { payload });
        // Get the agent's current state
        const agentState = await agentService_1.default.getAgentState(targetAgent);
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
                logger_1.default.warn(`Unknown job type: ${jobType}, executing as generic task`);
                return await this.executeGenericTask(targetAgent, payload);
        }
    }
    /**
     * Execute an AI task via the Python worker
     */
    async executeAITask(targetAgent, payload) {
        try {
            const response = await axios_1.default.post(`${this.config.pythonWorkerUrl}/ai-task/${payload.taskType || 'generic'}`, {
                agent: targetAgent,
                ...payload.data,
            });
            return response.data;
        }
        catch (error) {
            logger_1.default.error(`Error executing AI task for ${targetAgent}:`, error);
            throw new Error(`AI task execution failed: ${error.message}`);
        }
    }
    /**
     * Execute a data processing task
     */
    async executeDataProcessing(targetAgent, payload) {
        logger_1.default.info(`Executing data processing task for ${targetAgent}`, { payload });
        // Update agent state to reflect processing
        const currentState = await agentService_1.default.getAgentState(targetAgent);
        await agentService_1.default.updateAgentState(targetAgent, {
            ...currentState?.state,
            lastProcessedJob: payload,
            lastProcessedAt: new Date().toISOString(),
        });
        return { status: 'processed', agent: targetAgent };
    }
    /**
     * Handle inter-agent message
     */
    async handleInterAgentMessage(targetAgent, payload) {
        logger_1.default.info(`Handling inter-agent message for ${targetAgent}`, { payload });
        const { fromAgent, message, messageType } = payload;
        // Store the message in the agent's state
        const currentState = await agentService_1.default.getAgentState(targetAgent);
        const messages = currentState?.state?.messages || [];
        messages.push({
            from: fromAgent,
            message,
            type: messageType,
            timestamp: new Date().toISOString(),
        });
        await agentService_1.default.updateAgentState(targetAgent, {
            ...currentState?.state,
            messages,
            lastMessageAt: new Date().toISOString(),
        });
        // If the message requires a response, create a job for the sending agent
        if (payload.requiresResponse) {
            await agentService_1.default.createJob(fromAgent, {
                type: 'inter_agent_message',
                fromAgent: targetAgent,
                message: `Response to: ${message}`,
                messageType: 'response',
                requiresResponse: false,
            });
        }
        return { status: 'message_received', agent: targetAgent };
    }
    /**
     * Execute a generic task
     */
    async executeGenericTask(targetAgent, payload) {
        logger_1.default.info(`Executing generic task for ${targetAgent}`, { payload });
        // Update agent state
        const currentState = await agentService_1.default.getAgentState(targetAgent);
        await agentService_1.default.updateAgentState(targetAgent, {
            ...currentState?.state,
            lastGenericTask: payload,
            lastTaskAt: new Date().toISOString(),
        });
        return { status: 'completed', agent: targetAgent };
    }
    /**
     * Send a message from one agent to another
     */
    async sendInterAgentMessage(fromAgent, toAgent, message, messageType = 'info', requiresResponse = false) {
        logger_1.default.info(`Sending message from ${fromAgent} to ${toAgent}`);
        return await agentService_1.default.createJob(toAgent, {
            type: 'inter_agent_message',
            fromAgent,
            message,
            messageType,
            requiresResponse,
        });
    }
    /**
     * Get job processor status
     */
    getStatus() {
        return {
            isRunning: this.isRunning,
            config: this.config,
        };
    }
}
exports.JobProcessorService = JobProcessorService;
exports.default = new JobProcessorService();
//# sourceMappingURL=jobProcessorService.js.map