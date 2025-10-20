import { Request, Response } from 'express';
import vectorSearchService from '../services/vectorSearchService';
import logger from '../utils/logger';

export class VectorSearchController {
  /**
   * Perform semantic search
   */
  async semanticSearch(req: Request, res: Response): Promise<void> {
    try {
      const { query, agentName, threshold, limit } = req.body;

      if (!query) {
        res.status(400).json({ error: 'query is required' });
        return;
      }

      const results = await vectorSearchService.semanticSearch(query, {
        agentName,
        threshold: threshold ? parseFloat(threshold) : undefined,
        limit: limit ? parseInt(limit) : undefined,
      });

      res.json({
        query,
        results,
        count: results.length,
      });
    } catch (error: any) {
      logger.error('Error in semanticSearch:', error);
      res.status(500).json({ error: error.message });
    }
  }

  /**
   * Find similar documents
   */
  async findSimilar(req: Request, res: Response): Promise<void> {
    try {
      const { documentId } = req.params;
      const { agentName, threshold, limit } = req.query;

      const results = await vectorSearchService.findSimilarDocuments(
        parseInt(documentId),
        {
          agentName: agentName as string,
          threshold: threshold ? parseFloat(threshold as string) : undefined,
          limit: limit ? parseInt(limit as string) : undefined,
        }
      );

      res.json({
        documentId: parseInt(documentId),
        results,
        count: results.length,
      });
    } catch (error: any) {
      logger.error('Error in findSimilar:', error);
      res.status(500).json({ error: error.message });
    }
  }

  /**
   * Perform hybrid search (metadata + semantic)
   */
  async hybridSearch(req: Request, res: Response): Promise<void> {
    try {
      const { query, metadata, threshold, limit } = req.body;

      if (!query) {
        res.status(400).json({ error: 'query is required' });
        return;
      }

      const results = await vectorSearchService.hybridSearch(
        query,
        metadata || {},
        {
          threshold: threshold ? parseFloat(threshold) : undefined,
          limit: limit ? parseInt(limit) : undefined,
        }
      );

      res.json({
        query,
        metadata,
        results,
        count: results.length,
      });
    } catch (error: any) {
      logger.error('Error in hybridSearch:', error);
      res.status(500).json({ error: error.message });
    }
  }

  /**
   * Get recommendations based on document IDs
   */
  async getRecommendations(req: Request, res: Response): Promise<void> {
    try {
      const { documentIds, agentName, threshold, limit } = req.body;

      if (!documentIds || !Array.isArray(documentIds) || documentIds.length === 0) {
        res.status(400).json({ error: 'documentIds array is required' });
        return;
      }

      const results = await vectorSearchService.getRecommendations(
        documentIds.map((id: any) => parseInt(id)),
        {
          agentName,
          threshold: threshold ? parseFloat(threshold) : undefined,
          limit: limit ? parseInt(limit) : undefined,
        }
      );

      res.json({
        basedOn: documentIds,
        results,
        count: results.length,
      });
    } catch (error: any) {
      logger.error('Error in getRecommendations:', error);
      res.status(500).json({ error: error.message });
    }
  }

  /**
   * Cluster documents by similarity
   */
  async clusterDocuments(req: Request, res: Response): Promise<void> {
    try {
      const { agentName, threshold } = req.query;

      const clusters = await vectorSearchService.clusterDocuments(
        agentName as string,
        threshold ? parseFloat(threshold as string) : undefined
      );

      res.json({
        clusters,
        count: clusters.length,
        totalDocuments: clusters.reduce((sum, cluster) => sum + cluster.documents.length, 0),
      });
    } catch (error: any) {
      logger.error('Error in clusterDocuments:', error);
      res.status(500).json({ error: error.message });
    }
  }
}

export default new VectorSearchController();

