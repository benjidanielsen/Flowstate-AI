import { Router } from 'express';
import { CustomerController } from '../controllers/customerController';

const router: Router = Router();
const customerController = new CustomerController();

router.get('/', customerController.getAllCustomers);
router.get('/stats', customerController.getPipelineStats);
router.get('/:id', customerController.getCustomerById);
router.post('/', customerController.createCustomer);
router.put('/:id', customerController.updateCustomer);
router.delete('/:id', customerController.deleteCustomer);
router.post('/:id/next-stage', customerController.moveToNextStage);

export default router;