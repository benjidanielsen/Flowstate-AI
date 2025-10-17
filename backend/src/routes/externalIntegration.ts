import { Router } from 'express';
import { createIntegration, getIntegrationsByCustomer, updateIntegration, deleteIntegration } from '../controllers/externalIntegrationController';
import { authenticateToken } from '../middleware/authMiddleware';

const router = Router();

router.post('/', authenticateToken, createIntegration);
router.get('/:customerId', authenticateToken, getIntegrationsByCustomer);
router.put('/:id', authenticateToken, updateIntegration);
router.delete('/:id', authenticateToken, deleteIntegration);

export default router;

