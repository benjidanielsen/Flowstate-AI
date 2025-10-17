"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = require("express");
const externalIntegrationController_1 = require("../controllers/externalIntegrationController");
const authMiddleware_1 = require("../middleware/authMiddleware");
const router = (0, express_1.Router)();
router.post('/', authMiddleware_1.authenticateToken, externalIntegrationController_1.createIntegration);
router.get('/:customerId', authMiddleware_1.authenticateToken, externalIntegrationController_1.getIntegrationsByCustomer);
router.put('/:id', authMiddleware_1.authenticateToken, externalIntegrationController_1.updateIntegration);
router.delete('/:id', authMiddleware_1.authenticateToken, externalIntegrationController_1.deleteIntegration);
exports.default = router;
//# sourceMappingURL=externalIntegration.js.map