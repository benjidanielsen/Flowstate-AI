"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = require("express");
const reminderController_1 = require("../controllers/reminderController");
const router = (0, express_1.Router)();
const controller = new reminderController_1.ReminderController();
router.get('/due', controller.listDue);
router.post('/', controller.create);
router.post('/:id/complete', controller.complete);
exports.default = router;
//# sourceMappingURL=reminders.js.map