"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = require("express");
const customers_1 = __importDefault(require("./customers"));
const interaction_1 = __importDefault(require("./interaction"));
const events_1 = __importDefault(require("./events"));
const webhooks_1 = __importDefault(require("./webhooks"));
const nba_1 = __importDefault(require("./nba"));
const auth_1 = __importDefault(require("./auth"));
const reminder_1 = __importDefault(require("./reminder"));
const externalIntegration_1 = __importDefault(require("./externalIntegration"));
const stats_1 = __importDefault(require("./stats"));
const aiCoordination_1 = __importDefault(require("./aiCoordination"));
const evolution_1 = __importDefault(require("./evolution"));
const kpis_1 = __importDefault(require("./kpis")); // Import KPI routes
const agents_1 = __importDefault(require("./agents")); // Import agent routes
const authMiddleware_1 = require("../middleware/authMiddleware");
const router = (0, express_1.Router)();
router.use('/auth', auth_1.default);
// Apply authentication middleware to all other routes
router.use('/customers', authMiddleware_1.authenticateToken, customers_1.default);
router.use("/interactions", authMiddleware_1.authenticateToken, interaction_1.default);
router.use("/stats", authMiddleware_1.authenticateToken, stats_1.default);
router.use('/events', authMiddleware_1.authenticateToken, events_1.default);
router.use('/hooks', authMiddleware_1.authenticateToken, webhooks_1.default);
router.use('/nba', authMiddleware_1.authenticateToken, nba_1.default);
router.use("/reminders", authMiddleware_1.authenticateToken, reminder_1.default);
router.use("/integrations", authMiddleware_1.authenticateToken, externalIntegration_1.default);
router.use("/ai", authMiddleware_1.authenticateToken, aiCoordination_1.default);
router.use("/evolution", authMiddleware_1.authenticateToken, evolution_1.default);
router.use("/kpis", authMiddleware_1.authenticateToken, kpis_1.default); // Use KPI routes
router.use("/api", authMiddleware_1.authenticateToken, agents_1.default); // Use agent routes
// Health check
router.get('/health', (req, res) => {
    res.json({ status: 'OK', timestamp: new Date().toISOString() });
});
exports.default = router;
//# sourceMappingURL=index.js.map