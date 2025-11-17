import express, { Router } from 'express';
import { CustomerController } from '../controllers/customerController';
const router = express.Router();

interface Customer {
  id: number;
  name: string;
  stage: string;
  createdAt: string;
}

const customers: Customer[] = [];
let nextId = 1;

router.get('/', (_req, res) => {
  res.json(customers);
});

router.post('/', (req, res) => {
  const body = req.body;
  const c: Customer = { id: nextId++, name: body.name || 'Unnamed', stage: 'Lead', createdAt: new Date().toISOString() };
  customers.push(c);
  res.status(201).json(c);
});

export default router;

const router = Router();
const customerController = new CustomerController();

router.get('/', customerController.getAllCustomers);
router.get('/stats', customerController.getPipelineStats);
router.get('/:id', customerController.getCustomerById);
router.post('/', customerController.createCustomer);
router.put('/:id', customerController.updateCustomer);
router.delete('/:id', customerController.deleteCustomer);
router.post('/:id/next-stage', customerController.moveToNextStage);

export default router;