import { Router } from 'express';
import { InteractionController } from '../controllers/interactionController';

const router = Router();
const interactionController = new InteractionController();

router.get('/upcoming', interactionController.getUpcomingInteractions);
router.get('/customer/:customerId', interactionController.getInteractionsByCustomer);
router.post('/', interactionController.createInteraction);
router.put('/:id', interactionController.updateInteraction);
router.delete('/:id', interactionController.deleteInteraction);

export default router;