"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = require("express");
const interactionController_1 = require("../controllers/interactionController");
const router = (0, express_1.Router)();
router.get('/customer/:customerId', interactionController_1.interactionController.getInteractionsByCustomerId);
router.post('/', interactionController_1.interactionController.createInteraction);
router.put('/:id', interactionController_1.interactionController.updateInteraction);
router.delete('/:id', interactionController_1.interactionController.deleteInteraction);
exports.default = router;
//# sourceMappingURL=interactions.js.map