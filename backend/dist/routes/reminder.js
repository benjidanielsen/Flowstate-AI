"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = require("express");
const reminderController_1 = require("../controllers/reminderController");
const authMiddleware_1 = require("../middleware/authMiddleware");
const router = (0, express_1.Router)();
const reminderController = new reminderController_1.ReminderController();
router.use(authMiddleware_1.authenticateToken); // All reminder routes require authentication
router.get('/due', reminderController.listDue);
router.post('/', reminderController.create);
router.put('/:id/complete', reminderController.complete);
router.get('/customer/:customerId', reminderController.getRemindersByCustomerId);
router.put('/:id', reminderController.update);
router.delete('/:id', reminderController.delete);
exports.default = router;
//# sourceMappingURL=reminder.js.map