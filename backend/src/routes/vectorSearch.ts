import { Router } from 'express';
import vectorSearchController from '../controllers/vectorSearchController';

const router = Router();

// Semantic search routes
router.post('/search/semantic', vectorSearchController.semanticSearch.bind(vectorSearchController));
router.get('/search/similar/:documentId', vectorSearchController.findSimilar.bind(vectorSearchController));
router.post('/search/hybrid', vectorSearchController.hybridSearch.bind(vectorSearchController));
router.post('/search/recommendations', vectorSearchController.getRecommendations.bind(vectorSearchController));
router.get('/search/clusters', vectorSearchController.clusterDocuments.bind(vectorSearchController));

export default router;

