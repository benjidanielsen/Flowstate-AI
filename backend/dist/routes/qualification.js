"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = require("express");
const qualificationController_1 = require("../controllers/qualificationController");
const router = (0, express_1.Router)();
const controller = new qualificationController_1.QualificationController();
router.post('/', controller.createQualification);
router.get('/:id', controller.getQualificationById);
exports.default = router;
//# sourceMappingURL=qualification.js.map