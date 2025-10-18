import { Router } from 'express';
import customerRoutes from './customers';
import interactionRoutes from './interaction';

import eventRoutes from './events';
import webhookRoutes from './webhooks';
import nbaRoutes from './nba';
import authRoutes from './auth';
import reminderRoutes from './reminder';
import externalIntegrationRoutes from './externalIntegration';
import statsRoutes from './stats';
import aiCoordinationRoutes from './aiCoordination';
import evolutionRoutes from './evolution';
import kpiRoutes from './kpis'; // Import KPI routes
import agentRoutes from './agents'; // Import agent routes
import vectorSearchRoutes from './vectorSearch'; // Import vector search routes
import { authenticateToken } from '../middleware/authMiddleware';

const router: Router = Router();

router.use('/auth', authRoutes);

// Apply authentication middleware to all other routes
router.use('/customers', authenticateToken, customerRoutes);
router.use("/interactions", authenticateToken, interactionRoutes);
router.use("/stats", authenticateToken, statsRoutes);
router.use('/events', authenticateToken, eventRoutes);
router.use('/hooks', authenticateToken, webhookRoutes);
router.use('/nba', authenticateToken, nbaRoutes);
router.use("/reminders", authenticateToken, reminderRoutes);
router.use("/integrations", authenticateToken, externalIntegrationRoutes);
router.use("/ai", authenticateToken, aiCoordinationRoutes);
router.use("/evolution", authenticateToken, evolutionRoutes);
router.use("/kpis", authenticateToken, kpiRoutes); // Use KPI routes
router.use("/api", authenticateToken, agentRoutes); // Use agent routes
router.use("/api", authenticateToken, vectorSearchRoutes); // Use vector search routes

// Health check
router.get('/health', (req, res) => {
  res.json({ status: 'OK', timestamp: new Date().toISOString() });
});

export default router;

