"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = require("express");
const nbaController_1 = require("../controllers/nbaController");
const router = (0, express_1.Router)();
const controller = new nbaController_1.NBAController();
router.get('/', controller.getRecommendations);
router.post('/analyze', controller.analyze);
exports.default = router;
//# sourceMappingURL=nba.js.map