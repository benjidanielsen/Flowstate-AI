import { Router } from 'express';
import customerRoutes from './customers';
import interactionRoutes from './interactions';
import eventRoutes from './events';
import webhookRoutes from './webhooks';
import nbaRoutes from './nba';
import reminderRoutes from './reminders';

const router = Router();

router.use('/customers', customerRoutes);
router.use('/interactions', interactionRoutes);
router.use('/events', eventRoutes);
router.use('/hooks', webhookRoutes);
router.use('/nba', nbaRoutes);
router.use('/reminders', reminderRoutes);

// Health check
router.get('/health', (req, res) => {
  res.json({ status: 'OK', timestamp: new Date().toISOString() });
});

export default router;
