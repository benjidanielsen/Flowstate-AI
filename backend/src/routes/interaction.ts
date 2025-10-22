import { Router } from 'express';
import { interactionController } from '../controllers/interactionController';

const router = Router();

router.get('/upcoming', interactionController.getUpcomingInteractions);
router.post('/:id/complete', interactionController.completeInteraction);
router.post('/', interactionController.createInteraction);
router.get('/customer/:customerId', interactionController.getInteractionsByCustomerId);
router.get('/:id', interactionController.getInteractionById);
router.put('/:id', interactionController.updateInteraction);
router.delete('/:id', interactionController.deleteInteraction);

export default router;
