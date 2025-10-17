import { Router } from 'express';
import { sendTask, getStatus } from '../controllers/aiCoordinationController';
import { authenticateToken } from '../middleware/authMiddleware';

const router = Router();

router.post('/ai-task', authenticateToken, sendTask);
router.get('/ai-status', authenticateToken, getStatus);

export default router;

