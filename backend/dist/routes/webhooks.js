"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = require("express");
const webhookController_1 = require("../controllers/webhookController");
const router = (0, express_1.Router)();
const controller = new webhookController_1.WebhookController();
router.post('/dm', controller.dm);
router.post('/capi/lead', controller.capiLead);
exports.default = router;
//# sourceMappingURL=webhooks.js.map