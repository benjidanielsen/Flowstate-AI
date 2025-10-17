import db from '../database/supabase';
import { documents } from '../database/schema';
import { sql as sqlTemplate } from 'drizzle-orm';
import embeddingService from './embeddingService';
import logger from '../utils/logger';

export interface SearchResult {
  id: number;
  content: string;
  metadata: any;
  similarity: number;
}

export class VectorSearchService {
  /**
   * Perform semantic search on documents
   */
  async semanticSearch(
    query: string,
    options: {
      agentName?: string;
      threshold?: number;
      limit?: number;
    } = {}
  ): Promise<SearchResult[]> {
    try {
      const {
        agentName,
        threshold = 0.7,
        limit = 10,
      } = options;

      logger.info(`Performing semantic search for query: "${query.substring(0, 50)}..."`);

      // Generate embedding for the query
      const queryEmbedding = await embeddingService.generateEmbedding(query);
      const embeddingStr = embeddingService.formatEmbeddingForPostgres(queryEmbedding);

      // Use the match_documents function we created in Supabase
      const results = await db.execute(sqlTemplate.raw(`
        SELECT * FROM match_documents(
          '${embeddingStr}'::vector(1536),
          ${threshold},
          ${limit}
          ${agentName ? `, '${agentName}'` : ', NULL'}
        )
      `));

      logger.info(`Found ${results.rows.length} results for semantic search`);

      return results.rows.map((row: any) => ({
        id: row.id,
        content: row.content,
        metadata: row.metadata,
        similarity: row.similarity,
      }));
    } catch (error: any) {
      logger.error('Error in semantic search:', error);
      throw new Error(`Semantic search failed: ${error.message}`);
    }
  }

  /**
   * Find similar documents to a given document
   */
  async findSimilarDocuments(
    documentId: number,
    options: {
      agentName?: string;
      threshold?: number;
      limit?: number;
    } = {}
  ): Promise<SearchResult[]> {
    try {
      const {
        agentName,
        threshold = 0.7,
        limit = 10,
      } = options;

      logger.info(`Finding similar documents to document ${documentId}`);

      // Get the document's embedding
      const result = await db.execute(sqlTemplate.raw(`
        SELECT embedding FROM documents WHERE id = ${documentId}
      `));

      if (!result.rows || result.rows.length === 0) {
        throw new Error(`Document ${documentId} not found`);
      }

      const embedding = result.rows[0].embedding;

      if (!embedding) {
        throw new Error(`Document ${documentId} has no embedding`);
      }

      // Search for similar documents
      const results = await db.execute(sqlTemplate.raw(`
        SELECT * FROM match_documents(
          '${embedding}'::vector(1536),
          ${threshold},
          ${limit}
          ${agentName ? `, '${agentName}'` : ', NULL'}
        )
        WHERE id != ${documentId}
      `));

      logger.info(`Found ${results.rows.length} similar documents`);

      return results.rows.map((row: any) => ({
        id: row.id,
        content: row.content,
        metadata: row.metadata,
        similarity: row.similarity,
      }));
    } catch (error: any) {
      logger.error('Error finding similar documents:', error);
      throw new Error(`Failed to find similar documents: ${error.message}`);
    }
  }

  /**
   * Search documents by metadata and semantic similarity
   */
  async hybridSearch(
    query: string,
    metadataFilters: any = {},
    options: {
      threshold?: number;
      limit?: number;
    } = {}
  ): Promise<SearchResult[]> {
    try {
      const {
        threshold = 0.7,
        limit = 10,
      } = options;

      logger.info(`Performing hybrid search for query: "${query.substring(0, 50)}..."`);

      // Generate embedding for the query
      const queryEmbedding = await embeddingService.generateEmbedding(query);
      const embeddingStr = embeddingService.formatEmbeddingForPostgres(queryEmbedding);

      // Build metadata filter conditions
      const metadataConditions = Object.entries(metadataFilters)
        .map(([key, value]) => `metadata->>'${key}' = '${value}'`)
        .join(' AND ');

      const whereClause = metadataConditions
        ? `WHERE ${metadataConditions}`
        : '';

      // Perform semantic search with metadata filters
      const results = await db.execute(sqlTemplate.raw(`
        SELECT
          id,
          content,
          metadata,
          1 - (embedding <=> '${embeddingStr}'::vector(1536)) as similarity
        FROM documents
        ${whereClause}
        ${whereClause ? 'AND' : 'WHERE'} 1 - (embedding <=> '${embeddingStr}'::vector(1536)) > ${threshold}
        ORDER BY embedding <=> '${embeddingStr}'::vector(1536)
        LIMIT ${limit}
      `));

      logger.info(`Found ${results.rows.length} results for hybrid search`);

      return results.rows.map((row: any) => ({
        id: row.id,
        content: row.content,
        metadata: row.metadata,
        similarity: row.similarity,
      }));
    } catch (error: any) {
      logger.error('Error in hybrid search:', error);
      throw new Error(`Hybrid search failed: ${error.message}`);
    }
  }

  /**
   * Get recommendations based on multiple document IDs
   */
  async getRecommendations(
    documentIds: number[],
    options: {
      agentName?: string;
      threshold?: number;
      limit?: number;
    } = {}
  ): Promise<SearchResult[]> {
    try {
      const {
        agentName,
        threshold = 0.7,
        limit = 10,
      } = options;

      logger.info(`Getting recommendations based on ${documentIds.length} documents`);

      // Get embeddings for all documents
      const results = await db.execute(sqlTemplate.raw(`
        SELECT embedding FROM documents WHERE id IN (${documentIds.join(',')})
      `));

      if (!results.rows || results.rows.length === 0) {
        throw new Error('No documents found with the given IDs');
      }

      // Calculate average embedding
      const embeddings = results.rows
        .filter((row: any) => row.embedding)
        .map((row: any) => {
          // Parse the embedding if it's a string
          if (typeof row.embedding === 'string') {
            return embeddingService.parseEmbeddingFromPostgres(row.embedding);
          }
          return row.embedding;
        });

      if (embeddings.length === 0) {
        throw new Error('No embeddings found for the given documents');
      }

      // Calculate average embedding
      const avgEmbedding = embeddings[0].map((_: number, i: number) => {
        const sum = embeddings.reduce((acc: number, emb: number[]) => acc + emb[i], 0);
        return sum / embeddings.length;
      });

      const embeddingStr = embeddingService.formatEmbeddingForPostgres(avgEmbedding);

      // Search for similar documents
      const searchResults = await db.execute(sqlTemplate.raw(`
        SELECT * FROM match_documents(
          '${embeddingStr}'::vector(1536),
          ${threshold},
          ${limit}
          ${agentName ? `, '${agentName}'` : ', NULL'}
        )
        WHERE id NOT IN (${documentIds.join(',')})
      `));

      logger.info(`Found ${searchResults.rows.length} recommendations`);

      return searchResults.rows.map((row: any) => ({
        id: row.id,
        content: row.content,
        metadata: row.metadata,
        similarity: row.similarity,
      }));
    } catch (error: any) {
      logger.error('Error getting recommendations:', error);
      throw new Error(`Failed to get recommendations: ${error.message}`);
    }
  }

  /**
   * Cluster documents by similarity
   */
  async clusterDocuments(
    agentName?: string,
    threshold: number = 0.8
  ): Promise<Array<{ clusterId: number; documents: SearchResult[] }>> {
    try {
      logger.info(`Clustering documents for agent: ${agentName || 'all'}`);

      // Get all documents with embeddings
      const whereClause = agentName
        ? `WHERE metadata->>'agentName' = '${agentName}' AND embedding IS NOT NULL`
        : 'WHERE embedding IS NOT NULL';

      const results = await db.execute(sqlTemplate.raw(`
        SELECT id, content, metadata, embedding FROM documents
        ${whereClause}
      `));

      if (!results.rows || results.rows.length === 0) {
        return [];
      }

      // Simple clustering algorithm (can be improved)
      const clusters: Array<{ clusterId: number; documents: SearchResult[] }> = [];
      const processed = new Set<number>();

      for (let i = 0; i < results.rows.length; i++) {
        const doc: any = results.rows[i];

        if (processed.has(doc.id)) {
          continue;
        }

        // Start a new cluster
        const cluster: SearchResult[] = [{
          id: doc.id,
          content: doc.content,
          metadata: doc.metadata,
          similarity: 1.0,
        }];

        processed.add(doc.id);

        // Find similar documents
        const similarDocs = await this.findSimilarDocuments(doc.id, {
          agentName,
          threshold,
          limit: 100,
        });

        for (const similarDoc of similarDocs) {
          if (!processed.has(similarDoc.id)) {
            cluster.push(similarDoc);
            processed.add(similarDoc.id);
          }
        }

        clusters.push({
          clusterId: clusters.length + 1,
          documents: cluster,
        });
      }

      logger.info(`Created ${clusters.length} clusters`);

      return clusters;
    } catch (error: any) {
      logger.error('Error clustering documents:', error);
      throw new Error(`Failed to cluster documents: ${error.message}`);
    }
  }
}

export default new VectorSearchService();

