"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = require("express");
const statsController_1 = require("../controllers/statsController");
const authMiddleware_1 = require("../middleware/authMiddleware");
const router = (0, express_1.Router)();
const statsController = new statsController_1.StatsController();
router.use(authMiddleware_1.authenticateToken); // All stats routes require authentication
router.get('/', statsController.getPipelineStats);
exports.default = router;
//# sourceMappingURL=stats.js.map