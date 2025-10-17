import { Router } from 'express';
import agentController from '../controllers/agentController';

const router = Router();

// Agent management routes
router.post('/agents/register', agentController.registerAgent.bind(agentController));
router.get('/agents', agentController.getAllAgents.bind(agentController));
router.get('/agents/:agentName', agentController.getAgentState.bind(agentController));
router.put('/agents/:agentName', agentController.updateAgentState.bind(agentController));

// Job queue routes
router.post('/jobs', agentController.createJob.bind(agentController));
router.get('/jobs/pending', agentController.getAllPendingJobs.bind(agentController));
router.get('/jobs/agent/:agentName', agentController.getPendingJobs.bind(agentController));
router.put('/jobs/:jobId/status', agentController.updateJobStatus.bind(agentController));

// Document routes
router.post('/documents', agentController.storeDocument.bind(agentController));
router.get('/documents/:id', agentController.getDocument.bind(agentController));
router.get('/documents/search', agentController.searchDocuments.bind(agentController));

export default router;

