import { agentService } from './agentService';
import logger from '../utils/logger';

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

export class MemoryService {
  /**
   * Store a memory for an agent
   */
  async storeMemory(
    agentName: string,
    content: string,
    type: string = 'general',
    tags: string[] = [],
    importance: number = 5,
    additionalMetadata: any = {}
  ): Promise<any> {
    try {
      logger.info(`Storing memory for agent ${agentName}`, { type, tags });

      const metadata = {
        agentName,
        type,
        timestamp: new Date().toISOString(),
        tags,
        importance,
        ...additionalMetadata,
      };

      const document = await agentService.storeDocument({ agent_name: agentName, type, content, metadata, tags, importance });

      // Update agent state to track memory count
      const agentState = await agentService.getAgentState(agentName);
      const memoryCount = (agentState?.metadata?.memoryCount || 0) + 1;

      await agentService.updateAgentState(agentName, "active", {
        ...agentState?.metadata,
        memoryCount,
        lastMemoryAt: new Date().toISOString(),
      });

      logger.info(`Memory stored for agent ${agentName}`, { documentId: document.id });
      return document;
    } catch (error) {
      logger.error(`Error storing memory for ${agentName}:`, error);
      throw error;
    }
  }

  /**
   * Retrieve memories for an agent
   */
  async getMemories(
    agentName: string,
    type?: string,
    tags?: string[],
    limit: number = 10
  ): Promise<any[]> {
    try {
      logger.info(`Retrieving memories for agent ${agentName}`, { type, tags, limit });

      // Get all documents (in production, you'd filter by metadata)
      const documents = await agentService.searchDocuments('', agentName, type, tags);

      // Filter by agent name and optionally by type and tags
      let filtered = documents.filter(
        (doc: any) => doc.metadata?.agentName === agentName
      );

      if (type) {
        filtered = filtered.filter((doc: any) => doc.metadata?.type === type);
      }

      if (tags && tags.length > 0) {
        filtered = filtered.filter((doc: any) => {
          const docTags = doc.metadata?.tags || [];
          return tags.some((tag) => docTags.includes(tag));
        });
      }

      // Sort by importance and timestamp
      filtered.sort((a: any, b: any) => {
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

      logger.info(`Retrieved ${results.length} memories for agent ${agentName}`);
      return results;
    } catch (error) {
      logger.error(`Error retrieving memories for ${agentName}:`, error);
      throw error;
    }
  }

  /**
   * Store a conversation turn
   */
  async storeConversation(
    agentName: string,
    userMessage: string,
    agentResponse: string,
    conversationId?: string
  ): Promise<any> {
    const content = `User: ${userMessage}\nAgent: ${agentResponse}`;
    
    return await this.storeMemory(
      agentName,
      content,
      'conversation',
      ['conversation'],
      7, // Higher importance for conversations
      { conversationId, userMessage, agentResponse }
    );
  }

  /**
   * Store a task execution result
   */
  async storeTaskResult(
    agentName: string,
    taskDescription: string,
    result: any,
    success: boolean
  ): Promise<any> {
    const content = `Task: ${taskDescription}\nResult: ${JSON.stringify(result)}\nSuccess: ${success}`;
    
    return await this.storeMemory(
      agentName,
      content,
      'task_result',
      ['task', success ? 'success' : 'failure'],
      success ? 6 : 8, // Higher importance for failures to learn from
      { taskDescription, result, success }
    );
  }

  /**
   * Store a learning or insight
   */
  async storeLearning(
    agentName: string,
    learning: string,
    category: string = 'general',
    importance: number = 9
  ): Promise<any> {
    return await this.storeMemory(
      agentName,
      learning,
      'learning',
      ['learning', category],
      importance,
      { category }
    );
  }

  /**
   * Get recent memories for an agent
   */
  async getRecentMemories(agentName: string, limit: number = 10): Promise<any[]> {
    try {
      const memories = await this.getMemories(agentName, undefined, undefined, limit);
      return memories;
    } catch (error) {
      logger.error(`Error getting recent memories for ${agentName}:`, error);
      throw error;
    }
  }

  /**
   * Get important memories for an agent
   */
  async getImportantMemories(
    agentName: string,
    minImportance: number = 7,
    limit: number = 10
  ): Promise<any[]> {
    try {
      const allMemories = await this.getMemories(agentName, undefined, undefined, limit * 2);
      
      const important = allMemories.filter(
        (memory: any) => (memory.metadata?.importance || 0) >= minImportance
      );

      return important.slice(0, limit);
    } catch (error) {
      logger.error(`Error getting important memories for ${agentName}:`, error);
      throw error;
    }
  }

  /**
   * Get conversation history for an agent
   */
  async getConversationHistory(
    agentName: string,
    conversationId?: string,
    limit: number = 10
  ): Promise<any[]> {
    try {
      const memories = await this.getMemories(agentName, 'conversation', undefined, limit * 2);
      
      let filtered = memories;
      if (conversationId) {
        filtered = memories.filter(
          (memory: any) => memory.metadata?.conversationId === conversationId
        );
      }

      return filtered.slice(0, limit);
    } catch (error) {
      logger.error(`Error getting conversation history for ${agentName}:`, error);
      throw error;
    }
  }

  /**
   * Get task history for an agent
   */
  async getTaskHistory(
    agentName: string,
    successOnly: boolean = false,
    limit: number = 10
  ): Promise<any[]> {
    try {
      const tags = successOnly ? ['task', 'success'] : ['task'];
      const memories = await this.getMemories(agentName, 'task_result', tags, limit);
      return memories;
    } catch (error) {
      logger.error(`Error getting task history for ${agentName}:`, error);
      throw error;
    }
  }

  /**
   * Get learnings for an agent
   */
  async getLearnings(
    agentName: string,
    category?: string,
    limit: number = 10
  ): Promise<any[]> {
    try {
      const tags = category ? ['learning', category] : ['learning'];
      const memories = await this.getMemories(agentName, 'learning', tags, limit);
      return memories;
    } catch (error) {
      logger.error(`Error getting learnings for ${agentName}:`, error);
      throw error;
    }
  }

  /**
   * Clear all memories for an agent (use with caution)
   */
  async clearMemories(agentName: string): Promise<void> {
    try {
      logger.warn(`Clearing all memories for agent ${agentName}`);
      
      // Update agent state to reset memory count
      const agentState = await agentService.getAgentState(agentName);
      await agentService.updateAgentState(agentName, "active", {
        ...agentState?.metadata,
        memoryCount: 0,
        lastMemoryAt: null,
      });

      // Note: In production, you'd want to actually delete the documents
      // For now, we just update the agent state
      logger.info(`Memories cleared for agent ${agentName}`);
    } catch (error) {
      logger.error(`Error clearing memories for ${agentName}:`, error);
      throw error;
    }
  }

  /**
   * Get memory statistics for an agent
   */
  async getMemoryStats(agentName: string): Promise<any> {
    try {
      const allMemories = await this.getMemories(agentName, undefined, undefined, 1000);
      
      const stats = {
        totalMemories: allMemories.length,
        byType: {} as any,
        byImportance: {} as any,
        averageImportance: 0,
      };

      let totalImportance = 0;

      allMemories.forEach((memory: any) => {
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
    } catch (error) {
      logger.error(`Error getting memory stats for ${agentName}:`, error);
      throw error;
    }
  }
}

export default new MemoryService();

