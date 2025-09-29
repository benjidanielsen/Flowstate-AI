"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = require("express");
const interactionController_1 = require("../controllers/interactionController");
const router = (0, express_1.Router)();
const interactionController = new interactionController_1.InteractionController();
router.get('/upcoming', interactionController.getUpcomingInteractions);
router.get('/customer/:customerId', interactionController.getInteractionsByCustomer);
router.post('/', interactionController.createInteraction);
router.put('/:id', interactionController.updateInteraction);
router.delete('/:id', interactionController.deleteInteraction);
exports.default = router;
//# sourceMappingURL=interactions.js.map