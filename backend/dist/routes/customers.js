"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = require("express");
const customerController_1 = require("../controllers/customerController");
const router = (0, express_1.Router)();
const customerController = new customerController_1.CustomerController();
router.get('/', customerController.getAllCustomers);
router.get('/stats', customerController.getPipelineStats);
router.get('/:id', customerController.getCustomerById);
router.post('/', customerController.createCustomer);
router.put('/:id', customerController.updateCustomer);
router.delete('/:id', customerController.deleteCustomer);
router.post('/:id/next-stage', customerController.moveToNextStage);
exports.default = router;
//# sourceMappingURL=customers.js.map