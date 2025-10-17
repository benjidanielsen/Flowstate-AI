"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.MemoryService = void 0;
const agentService_1 = __importDefault(require("./agentService"));
const logger_1 = __importDefault(require("../utils/logger"));
class MemoryService {
    /**
     * Store a memory for an agent
     */
    async storeMemory(agentName, content, type = 'general', tags = [], importance = 5, additionalMetadata = {}) {
        try {
            logger_1.default.info(`Storing memory for agent ${agentName}`, { type, tags });
            const metadata = {
                agentName,
                type,
                timestamp: new Date().toISOString(),
                tags,
                importance,
                ...additionalMetadata,
            };
            const document = await agentService_1.default.storeDocument(content, metadata);
            // Update agent state to track memory count
            const agentState = await agentService_1.default.getAgentState(agentName);
            const memoryCount = (agentState?.state?.memoryCount || 0) + 1;
            await agentService_1.default.updateAgentState(agentName, {
                ...agentState?.state,
                memoryCount,
                lastMemoryAt: new Date().toISOString(),
            });
            logger_1.default.info(`Memory stored for agent ${agentName}`, { documentId: document.id });
            return document;
        }
        catch (error) {
            logger_1.default.error(`Error storing memory for ${agentName}:`, error);
            throw error;
        }
    }
    /**
     * Retrieve memories for an agent
     */
    async getMemories(agentName, type, tags, limit = 10) {
        try {
            logger_1.default.info(`Retrieving memories for agent ${agentName}`, { type, tags, limit });
            // Get all documents (in production, you'd filter by metadata)
            const documents = await agentService_1.default.searchDocuments({ agentName }, limit * 2);
            // Filter by agent name and optionally by type and tags
            let filtered = documents.filter((doc) => doc.metadata?.agentName === agentName);
            if (type) {
                filtered = filtered.filter((doc) => doc.metadata?.type === type);
            }
            if (tags && tags.length > 0) {
                filtered = filtered.filter((doc) => {
                    const docTags = doc.metadata?.tags || [];
                    return tags.some((tag) => docTags.includes(tag));
                });
            }
            // Sort by importance and timestamp
            filtered.sort((a, b) => {
                const importanceA = a.metadata?.importance || 0;
                const importanceB = b.metadata?.importance || 0;
                if (importanceA !== importanceB) {
                    return importanceB - importanceA; // Higher importance first
                }
                const timeA = new Date(a.metadata?.timestamp || 0).getTime();
                const timeB = new Date(b.metadata?.timestamp || 0).getTime();
                return timeB - timeA; // More recent first
            });
            // Limit results
            const results = filtered.slice(0, limit);
            logger_1.default.info(`Retrieved ${results.length} memories for agent ${agentName}`);
            return results;
        }
        catch (error) {
            logger_1.default.error(`Error retrieving memories for ${agentName}:`, error);
            throw error;
        }
    }
    /**
     * Store a conversation turn
     */
    async storeConversation(agentName, userMessage, agentResponse, conversationId) {
        const content = `User: ${userMessage}\nAgent: ${agentResponse}`;
        return await this.storeMemory(agentName, content, 'conversation', ['conversation'], 7, // Higher importance for conversations
        { conversationId, userMessage, agentResponse });
    }
    /**
     * Store a task execution result
     */
    async storeTaskResult(agentName, taskDescription, result, success) {
        const content = `Task: ${taskDescription}\nResult: ${JSON.stringify(result)}\nSuccess: ${success}`;
        return await this.storeMemory(agentName, content, 'task_result', ['task', success ? 'success' : 'failure'], success ? 6 : 8, // Higher importance for failures to learn from
        { taskDescription, result, success });
    }
    /**
     * Store a learning or insight
     */
    async storeLearning(agentName, learning, category = 'general', importance = 9) {
        return await this.storeMemory(agentName, learning, 'learning', ['learning', category], importance, { category });
    }
    /**
     * Get recent memories for an agent
     */
    async getRecentMemories(agentName, limit = 10) {
        try {
            const memories = await this.getMemories(agentName, undefined, undefined, limit);
            return memories;
        }
        catch (error) {
            logger_1.default.error(`Error getting recent memories for ${agentName}:`, error);
            throw error;
        }
    }
    /**
     * Get important memories for an agent
     */
    async getImportantMemories(agentName, minImportance = 7, limit = 10) {
        try {
            const allMemories = await this.getMemories(agentName, undefined, undefined, limit * 2);
            const important = allMemories.filter((memory) => (memory.metadata?.importance || 0) >= minImportance);
            return important.slice(0, limit);
        }
        catch (error) {
            logger_1.default.error(`Error getting important memories for ${agentName}:`, error);
            throw error;
        }
    }
    /**
     * Get conversation history for an agent
     */
    async getConversationHistory(agentName, conversationId, limit = 10) {
        try {
            const memories = await this.getMemories(agentName, 'conversation', undefined, limit * 2);
            let filtered = memories;
            if (conversationId) {
                filtered = memories.filter((memory) => memory.metadata?.conversationId === conversationId);
            }
            return filtered.slice(0, limit);
        }
        catch (error) {
            logger_1.default.error(`Error getting conversation history for ${agentName}:`, error);
            throw error;
        }
    }
    /**
     * Get task history for an agent
     */
    async getTaskHistory(agentName, successOnly = false, limit = 10) {
        try {
            const tags = successOnly ? ['task', 'success'] : ['task'];
            const memories = await this.getMemories(agentName, 'task_result', tags, limit);
            return memories;
        }
        catch (error) {
            logger_1.default.error(`Error getting task history for ${agentName}:`, error);
            throw error;
        }
    }
    /**
     * Get learnings for an agent
     */
    async getLearnings(agentName, category, limit = 10) {
        try {
            const tags = category ? ['learning', category] : ['learning'];
            const memories = await this.getMemories(agentName, 'learning', tags, limit);
            return memories;
        }
        catch (error) {
            logger_1.default.error(`Error getting learnings for ${agentName}:`, error);
            throw error;
        }
    }
    /**
     * Clear all memories for an agent (use with caution)
     */
    async clearMemories(agentName) {
        try {
            logger_1.default.warn(`Clearing all memories for agent ${agentName}`);
            // Update agent state to reset memory count
            const agentState = await agentService_1.default.getAgentState(agentName);
            await agentService_1.default.updateAgentState(agentName, {
                ...agentState?.state,
                memoryCount: 0,
                lastMemoryAt: null,
            });
            // Note: In production, you'd want to actually delete the documents
            // For now, we just update the agent state
            logger_1.default.info(`Memories cleared for agent ${agentName}`);
        }
        catch (error) {
            logger_1.default.error(`Error clearing memories for ${agentName}:`, error);
            throw error;
        }
    }
    /**
     * Get memory statistics for an agent
     */
    async getMemoryStats(agentName) {
        try {
            const allMemories = await this.getMemories(agentName, undefined, undefined, 1000);
            const stats = {
                totalMemories: allMemories.length,
                byType: {},
                byImportance: {},
                averageImportance: 0,
            };
            let totalImportance = 0;
            allMemories.forEach((memory) => {
                const type = memory.metadata?.type || 'unknown';
                const importance = memory.metadata?.importance || 0;
                stats.byType[type] = (stats.byType[type] || 0) + 1;
                stats.byImportance[importance] = (stats.byImportance[importance] || 0) + 1;
                totalImportance += importance;
            });
            stats.averageImportance = allMemories.length > 0
                ? totalImportance / allMemories.length
                : 0;
            return stats;
        }
        catch (error) {
            logger_1.default.error(`Error getting memory stats for ${agentName}:`, error);
            throw error;
        }
    }
}
exports.MemoryService = MemoryService;
exports.default = new MemoryService();
//# sourceMappingURL=memoryService.js.map