import { AgentState, Job, Document, JobStatus } from '../types';
export declare class AgentService {
    private dbManager;
    private embeddingService;
    constructor();
    registerAgent(agent: AgentState): Promise<AgentState>;
    getAgentState(agentName: string): Promise<AgentState | null>;
    getAllAgents(): Promise<AgentState[]>;
    updateAgentState(agentName: string, status: string, metadata: any): Promise<AgentState | null>;
    createJob(job: Omit<Job, 'id' | 'created_at' | 'updated_at' | 'status'>): Promise<Job>;
    getPendingJobs(agentName: string): Promise<Job[]>;
    getAllPendingJobs(): Promise<Job[]>;
    updateJobStatus(jobId: string, status: JobStatus, resultPayload?: any): Promise<Job | null>;
    storeDocument(document: Omit<Document, 'id' | 'created_at' | 'updated_at' | 'embedding'>): Promise<Document>;
    getDocument(documentId: string): Promise<Document | null>;
    searchDocuments(query: string, agentName?: string, type?: string, tags?: string[]): Promise<Document[]>;
    deleteDocument(documentId: string): Promise<boolean>;
}
export declare const agentService: AgentService;
//# sourceMappingURL=agentService.d.ts.map