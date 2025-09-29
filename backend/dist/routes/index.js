"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = require("express");
const customers_1 = __importDefault(require("./customers"));
const interactions_1 = __importDefault(require("./interactions"));
const events_1 = __importDefault(require("./events"));
const webhooks_1 = __importDefault(require("./webhooks"));
const nba_1 = __importDefault(require("./nba"));
const reminders_1 = __importDefault(require("./reminders"));
const router = (0, express_1.Router)();
router.use('/customers', customers_1.default);
router.use('/interactions', interactions_1.default);
router.use('/events', events_1.default);
router.use('/hooks', webhooks_1.default);
router.use('/nba', nba_1.default);
router.use('/reminders', reminders_1.default);
// Health check
router.get('/health', (req, res) => {
    res.json({ status: 'OK', timestamp: new Date().toISOString() });
});
exports.default = router;
//# sourceMappingURL=index.js.map