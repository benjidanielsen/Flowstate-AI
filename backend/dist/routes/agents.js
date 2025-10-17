"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = require("express");
const agentController_1 = __importDefault(require("../controllers/agentController"));
const router = (0, express_1.Router)();
// Agent management routes
router.post('/agents/register', agentController_1.default.registerAgent.bind(agentController_1.default));
router.get('/agents', agentController_1.default.getAllAgents.bind(agentController_1.default));
router.get('/agents/:agentName', agentController_1.default.getAgentState.bind(agentController_1.default));
router.put('/agents/:agentName', agentController_1.default.updateAgentState.bind(agentController_1.default));
// Job queue routes
router.post('/jobs', agentController_1.default.createJob.bind(agentController_1.default));
router.get('/jobs/pending', agentController_1.default.getAllPendingJobs.bind(agentController_1.default));
router.get('/jobs/agent/:agentName', agentController_1.default.getPendingJobs.bind(agentController_1.default));
router.put('/jobs/:jobId/status', agentController_1.default.updateJobStatus.bind(agentController_1.default));
// Document routes
router.post('/documents', agentController_1.default.storeDocument.bind(agentController_1.default));
router.get('/documents/:id', agentController_1.default.getDocument.bind(agentController_1.default));
router.get('/documents/search', agentController_1.default.searchDocuments.bind(agentController_1.default));
exports.default = router;
//# sourceMappingURL=agents.js.map