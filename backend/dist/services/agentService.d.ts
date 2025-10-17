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
export declare class AgentService {
    /**
     * Register or update an agent's state
     */
    registerAgent(agentName: string, initialState?: any): Promise<AgentState>;
    /**
     * Get agent state by name
     */
    getAgentState(agentName: string): Promise<AgentState | null>;
    /**
     * Update agent state
     */
    updateAgentState(agentName: string, newState: any): Promise<AgentState>;
    /**
     * Get all registered agents
     */
    getAllAgents(): Promise<AgentState[]>;
    /**
     * Create a new job in the queue
     */
    createJob(targetAgent: string, payload: any): Promise<Job>;
    /**
     * Get pending jobs for a specific agent
     */
    getPendingJobs(targetAgent: string, limit?: number): Promise<Job[]>;
    /**
     * Get all pending jobs
     */
    getAllPendingJobs(limit?: number): Promise<Job[]>;
    /**
     * Update job status
     */
    updateJobStatus(jobId: number, status: 'pending' | 'processing' | 'completed' | 'failed', incrementAttempts?: boolean): Promise<Job>;
    /**
     * Store a document in the documents table
     */
    storeDocument(content: string, metadata?: any, embedding?: string): Promise<Document>;
    /**
     * Search documents by metadata
     */
    searchDocuments(metadataFilter: any, limit?: number): Promise<Document[]>;
    /**
     * Get document by ID
     */
    getDocument(id: number): Promise<Document | null>;
    /**
     * Delete old completed jobs (cleanup)
     */
    cleanupCompletedJobs(olderThanDays?: number): Promise<number>;
}
declare const _default: AgentService;
export default _default;
//# sourceMappingURL=agentService.d.ts.map