import { Router } from 'express';
import { EventController } from '../controllers/eventController';

const router = Router();
const controller = new EventController();

router.get('/', controller.getAll);
router.post('/', controller.createEvent);
router.get('/customer/:customerId', controller.getByCustomer);
router.get('/type/:type', controller.getByType);

export default router;

