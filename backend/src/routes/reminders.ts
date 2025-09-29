import { Router } from 'express';
import { ReminderController } from '../controllers/reminderController';

const router = Router();
const controller = new ReminderController();

router.get('/due', controller.listDue);
router.post('/', controller.create);
router.post('/:id/complete', controller.complete);

export default router;

