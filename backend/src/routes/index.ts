import { Router } from 'express';
import customerRoutes from './customers';
import interactionRoutes from './interaction';

import eventRoutes from './events';
import webhookRoutes from './webhooks';
import nbaRoutes from './nba';
import authRoutes from './auth';
import reminderRoutes from './reminders';
import { authenticateToken } from '../middleware/authMiddleware';

const router = Router();

router.use('/auth', authRoutes);

// Apply authentication middleware to all other routes
router.use('/customers', authenticateToken, customerRoutes);
router.use("/interactions", authenticateToken, interactionRoutes);
router.use('/events', authenticateToken, eventRoutes);
router.use('/hooks', authenticateToken, webhookRoutes);
router.use('/nba', authenticateToken, nbaRoutes);
router.use('/reminders', authenticateToken, reminderRoutes);

// Health check
router.get('/health', (req, res) => {
  res.json({ status: 'OK', timestamp: new Date().toISOString() });
});

export default router;
