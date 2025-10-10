import { Router } from 'express';
import { StatsController } from '../controllers/statsController';
import { authenticateToken } from '../middleware/authMiddleware';

const router = Router();
const statsController = new StatsController();

router.use(authenticateToken); // All stats routes require authentication

router.get('/', statsController.getPipelineStats);

export default router;
