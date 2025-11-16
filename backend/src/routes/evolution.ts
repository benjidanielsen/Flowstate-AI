import express, { Request, Response } from 'express';
import logger from '../utils/logger';
import { authenticateToken } from '../middleware/authMiddleware';
import { AICoordinationService } from '../services/aiCoordinationService';

const router = express.Router();
const aiCoordinationService = new AICoordinationService();

// All evolution routes require authentication
router.use(authenticateToken);

/**
 * GET /api/evolution/metrics
 * Get overall evolution framework metrics
 */
router.get('/metrics', async (req: Request, res: Response) => {
  try {
    // In production, this would fetch from the Evolution Manager
    // For now, returning mock data
    const metrics = {
      total_events: 42,
      pending_improvements: 3,
      applied_improvements: 39,
      success_rate: 0.93,
      average_confidence: 0.85,
      safe_mode_active: false,
      last_evolution: new Date().toISOString()
    };

    res.json(metrics);
  } catch (error) {
    logger.error("Error fetching evolution metrics:", error);
    res.status(500).json({ error: 'Failed to fetch evolution metrics' });
  }
});

/**
 * GET /api/evolution/anomalies
 * Get detected anomalies
 */
router.get('/anomalies', async (req: Request, res: Response) => {
  try {
    // In production, this would fetch from the Anomaly Detector
    const anomalies: any[] = [];

    res.json(anomalies);
  } catch (error) {
    logger.error("Error fetching anomalies:", error);
    res.status(500).json({ error: 'Failed to fetch anomalies' });
  }
});

/**
 * GET /api/evolution/performance
 * Get system performance metrics
 */
router.get('/performance', async (req: Request, res: Response) => {
  try {
    // In production, this would fetch from the Metrics Collector
    const performance = {
      nba_success_rate: 0.87,
      reminder_success_rate: 0.92,
      avg_response_time: 245
    };

    res.json(performance);
  } catch (error) {
    logger.error("Error fetching performance metrics:", error);
    res.status(500).json({ error: 'Failed to fetch performance metrics' });
  }
});

/**
 * GET /api/evolution/events
 * Get recent evolution events
 */
router.get('/events', async (req: Request, res: Response) => {
  try {
    const limit = parseInt(req.query.limit as string) || 10;

    // In production, this would fetch from the database
    const events = [
      {
        id: '1',
        type: 'nba_optimization',
        description: 'Improved confidence threshold for customer segment A',
        status: 'applied',
        confidence: 0.85,
        created_at: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
        applied_at: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString()
      },
      {
        id: '2',
        type: 'reminder_optimization',
        description: 'Adjusted preferred hours based on response patterns',
        status: 'applied',
        confidence: 0.78,
        created_at: new Date(Date.now() - 5 * 60 * 60 * 1000).toISOString(),
        applied_at: new Date(Date.now() - 5 * 60 * 60 * 1000).toISOString()
      },
      {
        id: '3',
        type: 'code_improvement',
        description: 'Pending review: Refactored NBA decision engine',
        status: 'pending',
        confidence: 0.72,
        created_at: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(),
        applied_at: null
      }
    ];

    res.json(events.slice(0, limit));
  } catch (error) {
    logger.error("Error fetching evolution events:", error);
    res.status(500).json({ error: 'Failed to fetch evolution events' });
  }
});

/**
 * POST /api/evolution/safe-mode
 * Toggle safe mode
 */
router.post('/safe-mode', async (req: Request, res: Response) => {
  try {
    const { active, reason } = req.body;

    // In production, this would call the Evolution Governor
    logger.info(`Safe mode ${active ? 'activated' : 'deactivated'}: ${reason || 'manual'}`);

    res.json({
      safe_mode_active: active,
      reason: reason || 'manual',
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    logger.error("Error toggling safe mode:", error);
    res.status(500).json({ error: 'Failed to toggle safe mode' });
  }
});

/**
 * POST /api/evolution/improvements/:id/approve
 * Approve a pending improvement
 */
router.post('/improvements/:id/approve', async (req: Request, res: Response) => {
  try {
    const { id } = req.params;
    const operatorEmail = (req as any)?.user?.email || 'operator';
    const { rationale = 'Approved via API', decision_maker = operatorEmail } = req.body || {};

    logger.info(`Approving improvement: ${id}`);
    const decisionPayload = {
      decision: 'approve' as const,
      rationale,
      decision_maker: decision_maker
    };

    await aiCoordinationService.submitApprovalDecision(id, decisionPayload);

    res.json({
      id,
      status: 'approved',
      timestamp: new Date().toISOString(),
      recorded_by: decision_maker
    });
  } catch (error) {
    logger.error('Error approving improvement:', error);
    res.status(500).json({ error: 'Failed to approve improvement' });
  }
});

/**
 * POST /api/evolution/improvements/:id/reject
 * Reject a pending improvement
 */
router.post('/improvements/:id/reject', async (req: Request, res: Response) => {
  try {
    const { id } = req.params;
    const { reason } = req.body;

    logger.info(`Rejecting improvement: ${id}, reason: ${reason}`);
    await aiCoordinationService.submitApprovalDecision(id, {
      decision: 'reject',
      rationale: reason || 'Rejected via API',
      decision_maker: (req as any)?.user?.email || 'operator'
    });

    res.json({
      id,
      status: 'rejected',
      reason,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    logger.error("Error rejecting improvement:", error);
    res.status(500).json({ error: 'Failed to reject improvement' });
  }
});

/**
 * GET /api/evolution/knowledge
 * Search knowledge base
 */
router.get('/knowledge', async (req: Request, res: Response) => {
  try {
    // const { query, category, limit } = req.query; // query, category, limit are not used in mock implementation

    // In production, this would call the Knowledge Manager
    const results: any[] = [];

    res.json(results);
  } catch (error) {
    logger.error("Error searching knowledge base:", error);
    res.status(500).json({ error: 'Failed to search knowledge base' });
  }
});

/**
 * GET /api/evolution/governance/status
 * Get governance status
 */
router.get('/governance/status', async (req: Request, res: Response) => {
  try {
    // In production, this would fetch from the Evolution Governor
    const status = {
      safe_mode_active: false,
      safe_mode_reason: null,
      recent_violations: 0,
      total_violations: 0,
      allowed_modifications: [
        'nba_rules',
        'reminder_timing',
        'code_quality'
      ],
      human_oversight_required: [
        'database_schema',
        'security_policies'
      ]
    };

    res.json(status);
  } catch (error) {
    logger.error('Error fetching governance status:', error);
    res.status(500).json({ error: 'Failed to fetch governance status' });
  }
});

/**
 * GET /api/evolution/agents
 * Surface multi-agent coordinator state
 */
router.get('/agents', async (_req: Request, res: Response) => {
  try {
    const agents = await aiCoordinationService.getAgentStatuses();
    res.json(agents);
  } catch (error: any) {
    logger.error('Error fetching agent status from worker', error);
    res.status(502).json({ error: error.message || 'Failed to fetch agent status' });
  }
});

/**
 * GET /api/evolution/approvals
 * Surface pending human approvals
 */
router.get('/approvals', async (_req: Request, res: Response) => {
  try {
    const approvals = await aiCoordinationService.getApprovalQueue();
    res.json(approvals);
  } catch (error: any) {
    logger.error('Error fetching approvals from worker', error);
    res.status(502).json({ error: error.message || 'Failed to fetch approval queue' });
  }
});

/**
 * POST /api/evolution/signals
 * Forward KPI/CRM signals to the worker for agent coordination
 */
router.post('/signals', async (req: Request, res: Response) => {
  try {
    const result = await aiCoordinationService.sendEvolutionSignal(req.body);
    res.json(result);
  } catch (error: any) {
    logger.error('Error sending evolution signal to worker', error);
    res.status(502).json({ error: error.message || 'Failed to route evolution signal' });
  }
});

export default router;

