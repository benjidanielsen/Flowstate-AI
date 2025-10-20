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
import { authorizeRoles, Roles } from '../middleware/rbacMiddleware';
import { metricsRegister } from '../utils/metrics';
import DatabaseManager from '../database';

const router: Router = Router();

router.use('/auth', authRoutes);

// Apply authentication middleware to all other routes
router.use('/customers', authenticateToken, authorizeRoles(Roles.ADMIN, Roles.MANAGER, Roles.AGENT), customerRoutes);
router.use("/interactions", authenticateToken, authorizeRoles(Roles.ADMIN, Roles.MANAGER, Roles.AGENT), interactionRoutes);
router.use("/stats", authenticateToken, authorizeRoles(Roles.ADMIN, Roles.MANAGER, Roles.ANALYST), statsRoutes);
router.use('/events', authenticateToken, authorizeRoles(Roles.ADMIN, Roles.MANAGER, Roles.ANALYST), eventRoutes);
router.use('/hooks', authenticateToken, authorizeRoles(Roles.ADMIN, Roles.SERVICE, Roles.INTEGRATION), webhookRoutes);
router.use('/nba', authenticateToken, authorizeRoles(Roles.ADMIN, Roles.MANAGER, Roles.AGENT, Roles.ANALYST), nbaRoutes);
router.use("/reminders", authenticateToken, authorizeRoles(Roles.ADMIN, Roles.MANAGER, Roles.AGENT), reminderRoutes);
router.use("/integrations", authenticateToken, authorizeRoles(Roles.ADMIN, Roles.MANAGER, Roles.INTEGRATION), externalIntegrationRoutes);
router.use("/ai", authenticateToken, authorizeRoles(Roles.ADMIN, Roles.MANAGER, Roles.ANALYST), aiCoordinationRoutes);
router.use("/evolution", authenticateToken, authorizeRoles(Roles.ADMIN, Roles.ANALYST), evolutionRoutes);
router.use("/kpis", authenticateToken, authorizeRoles(Roles.ADMIN, Roles.MANAGER, Roles.ANALYST), kpiRoutes); // Use KPI routes
router.use("/api", authenticateToken, authorizeRoles(Roles.ADMIN, Roles.MANAGER, Roles.AGENT, Roles.ANALYST), agentRoutes); // Use agent routes
router.use("/api", authenticateToken, authorizeRoles(Roles.ADMIN, Roles.MANAGER, Roles.AGENT, Roles.ANALYST), vectorSearchRoutes); // Use vector search routes

// Health check
router.get('/health', (req, res) => {
  res.json({ status: 'OK', timestamp: new Date().toISOString() });
});

// Readiness check - validates database connectivity
router.get('/ready', async (_req, res) => {
  try {
    const pool = DatabaseManager.getInstance().getPool();
    await pool.query('SELECT 1');
    res.json({ status: 'READY', timestamp: new Date().toISOString() });
  } catch (error: any) {
    res.status(503).json({
      status: 'UNAVAILABLE',
      error: error.message,
      timestamp: new Date().toISOString(),
    });
  }
});

// Prometheus metrics endpoint
router.get('/metrics', async (_req, res) => {
  res.set('Content-Type', metricsRegister.contentType);
  res.send(await metricsRegister.metrics());
});

export default router;

