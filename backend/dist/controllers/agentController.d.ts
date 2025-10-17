import { Request, Response } from 'express';
export declare class AgentController {
    /**
     * Register a new agent
     */
    registerAgent(req: Request, res: Response): Promise<void>;
    /**
     * Get agent state
     */
    getAgentState(req: Request, res: Response): Promise<void>;
    /**
     * Update agent state
     */
    updateAgentState(req: Request, res: Response): Promise<void>;
    /**
     * Get all agents
     */
    getAllAgents(req: Request, res: Response): Promise<void>;
    /**
     * Create a new job
     */
    createJob(req: Request, res: Response): Promise<void>;
    /**
     * Get pending jobs for an agent
     */
    getPendingJobs(req: Request, res: Response): Promise<void>;
    /**
     * Get all pending jobs
     */
    getAllPendingJobs(req: Request, res: Response): Promise<void>;
    /**
     * Update job status
     */
    updateJobStatus(req: Request, res: Response): Promise<void>;
    /**
     * Store a document
     */
    storeDocument(req: Request, res: Response): Promise<void>;
    /**
     * Get document by ID
     */
    getDocument(req: Request, res: Response): Promise<void>;
    /**
     * Search documents
     */
    searchDocuments(req: Request, res: Response): Promise<void>;
}
declare const _default: AgentController;
export default _default;
//# sourceMappingURL=agentController.d.ts.map