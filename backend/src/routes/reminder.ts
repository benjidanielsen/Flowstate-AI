import { Router } from 'express';
import { ReminderController } from '../controllers/reminderController';
import { authMiddleware } from '../middleware/authMiddleware';

const router = Router();
const reminderController = new ReminderController();

router.use(authMiddleware); // All reminder routes require authentication

router.get('/due', reminderController.listDue);
router.post('/', reminderController.create);
router.put('/:id/complete', reminderController.complete);
router.get('/customer/:customerId', reminderController.getRemindersByCustomerId);
router.put('/:id', reminderController.update);
router.delete('/:id', reminderController.delete);

export default router;
