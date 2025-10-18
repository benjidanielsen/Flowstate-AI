import { Router } from 'express';
import { interactionController } from '../controllers/interactionController';

const router: Router = Router();

router.get('/customer/:customerId', interactionController.getInteractionsByCustomerId);
router.post('/', interactionController.createInteraction);
router.put('/:id', interactionController.updateInteraction);
router.delete('/:id', interactionController.deleteInteraction);

export default router;