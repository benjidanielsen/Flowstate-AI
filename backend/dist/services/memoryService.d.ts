export interface MemoryEntry {
    content: string;
    metadata: {
        agentName: string;
        type: string;
        timestamp: string;
        tags?: string[];
        importance?: number;
        [key: string]: any;
    };
    embedding?: string;
}
export declare class MemoryService {
    /**
     * Store a memory for an agent
     */
    storeMemory(agentName: string, content: string, type?: string, tags?: string[], importance?: number, additionalMetadata?: any): Promise<any>;
    /**
     * Retrieve memories for an agent
     */
    getMemories(agentName: string, type?: string, tags?: string[], limit?: number): Promise<any[]>;
    /**
     * Store a conversation turn
     */
    storeConversation(agentName: string, userMessage: string, agentResponse: string, conversationId?: string): Promise<any>;
    /**
     * Store a task execution result
     */
    storeTaskResult(agentName: string, taskDescription: string, result: any, success: boolean): Promise<any>;
    /**
     * Store a learning or insight
     */
    storeLearning(agentName: string, learning: string, category?: string, importance?: number): Promise<any>;
    /**
     * Get recent memories for an agent
     */
    getRecentMemories(agentName: string, limit?: number): Promise<any[]>;
    /**
     * Get important memories for an agent
     */
    getImportantMemories(agentName: string, minImportance?: number, limit?: number): Promise<any[]>;
    /**
     * Get conversation history for an agent
     */
    getConversationHistory(agentName: string, conversationId?: string, limit?: number): Promise<any[]>;
    /**
     * Get task history for an agent
     */
    getTaskHistory(agentName: string, successOnly?: boolean, limit?: number): Promise<any[]>;
    /**
     * Get learnings for an agent
     */
    getLearnings(agentName: string, category?: string, limit?: number): Promise<any[]>;
    /**
     * Clear all memories for an agent (use with caution)
     */
    clearMemories(agentName: string): Promise<void>;
    /**
     * Get memory statistics for an agent
     */
    getMemoryStats(agentName: string): Promise<any>;
}
declare const _default: MemoryService;
export default _default;
//# sourceMappingURL=memoryService.d.ts.map