"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = require("express");
const eventController_1 = require("../controllers/eventController");
const router = (0, express_1.Router)();
const controller = new eventController_1.EventController();
router.get('/', controller.getAll);
router.post('/', controller.createEvent);
router.get('/customer/:customerId', controller.getByCustomer);
router.get('/type/:type', controller.getByType);
exports.default = router;
//# sourceMappingURL=events.js.map