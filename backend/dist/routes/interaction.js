"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = require("express");
const interactionController_1 = require("../controllers/interactionController");
const authMiddleware_1 = require("../middleware/authMiddleware");
const router = (0, express_1.Router)();
router.post('/', authMiddleware_1.authenticateToken, interactionController_1.interactionController.createInteraction);
router.get('/customer/:customerId', authMiddleware_1.authenticateToken, interactionController_1.interactionController.getInteractionsByCustomerId);
router.get('/:id', authMiddleware_1.authenticateToken, interactionController_1.interactionController.getInteractionById);
router.put('/:id', authMiddleware_1.authenticateToken, interactionController_1.interactionController.updateInteraction);
router.delete('/:id', authMiddleware_1.authenticateToken, interactionController_1.interactionController.deleteInteraction);
exports.default = router;
//# sourceMappingURL=interaction.js.map