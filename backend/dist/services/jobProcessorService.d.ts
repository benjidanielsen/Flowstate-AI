export interface JobProcessorConfig {
    pythonWorkerUrl: string;
    pollInterval: number;
    maxRetries: number;
}
export declare class JobProcessorService {
    private config;
    private isRunning;
    private intervalId;
    constructor(config?: Partial<JobProcessorConfig>);
    /**
     * Start the job processor
     */
    start(): void;
    /**
     * Stop the job processor
     */
    stop(): void;
    /**
     * Process pending jobs
     */
    private processJobs;
    /**
     * Process a single job
     */
    private processJob;
    /**
     * Execute a job by delegating to the appropriate agent
     */
    private executeJob;
    /**
     * Execute an AI task via the Python worker
     */
    private executeAITask;
    /**
     * Execute a data processing task
     */
    private executeDataProcessing;
    /**
     * Handle inter-agent message
     */
    private handleInterAgentMessage;
    /**
     * Execute a generic task
     */
    private executeGenericTask;
    /**
     * Send a message from one agent to another
     */
    sendInterAgentMessage(fromAgent: string, toAgent: string, message: string, messageType?: string, requiresResponse?: boolean): Promise<any>;
    /**
     * Get job processor status
     */
    getStatus(): {
        isRunning: boolean;
        config: JobProcessorConfig;
    };
}
declare const _default: JobProcessorService;
export default _default;
//# sourceMappingURL=jobProcessorService.d.ts.map