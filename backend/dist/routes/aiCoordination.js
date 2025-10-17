"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = require("express");
const aiCoordinationController_1 = require("../controllers/aiCoordinationController");
const authMiddleware_1 = require("../middleware/authMiddleware");
const router = (0, express_1.Router)();
router.post('/ai-task', authMiddleware_1.authenticateToken, aiCoordinationController_1.sendTask);
router.get('/ai-status', authMiddleware_1.authenticateToken, aiCoordinationController_1.getStatus);
exports.default = router;
//# sourceMappingURL=aiCoordination.js.map