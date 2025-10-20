import { Router } from 'express';
import analyticsController from '../controllers/analyticsController';

const router: Router = Router();

router.post('/events', analyticsController.ingestEvent);
router.post('/recommendations', analyticsController.ingestRecommendation);
router.get('/summary', analyticsController.getSummary);
router.get('/events', analyticsController.getRecentEvents);

export default router;
