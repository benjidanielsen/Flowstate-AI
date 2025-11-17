import express, { Router } from 'express';
import { Database } from 'sqlite';
import { CustomerController } from '../controllers/customerController';
const router = express.Router();

interface Customer {
  id: number;
  name: string;
  stage: string;
  createdAt: string;
}
export function createCustomersRouter(db: Database) {
  const router = express.Router();

  router.get('/', async (_req, res) => {
    const rows = await db.all('SELECT * FROM customers');
    res.json(rows);
  });

  router.post('/', async (req, res) => {
    const body = req.body;
    const stmt = await db.run('INSERT INTO customers (name, stage, createdAt) VALUES (?, ?, ?)', [body.name || 'Unnamed', 'Lead', new Date().toISOString()]);
    const id = stmt.lastID;
    const row = await db.get('SELECT * FROM customers WHERE id = ?', [id]);
    res.status(201).json(row);
  });

  return router;
}

export default createCustomersRouter;
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