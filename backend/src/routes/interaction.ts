import { Router } from 'express';
import { interactionController } from '../controllers/interactionController';
import { authenticateToken } from '../middleware/authMiddleware';

const router: Router = Router();

router.post(
  '/',
  authenticateToken,
  interactionController.createInteraction
);
router.get(
  '/customer/:customerId',
  authenticateToken,
  interactionController.getInteractionsByCustomerId
);
router.get(
  '/:id',
  authenticateToken,
  interactionController.getInteractionById
);
router.put(
  '/:id',
  authenticateToken,
  interactionController.updateInteraction
);
router.delete(
  '/:id',
  authenticateToken,
  interactionController.deleteInteraction
);

export default router;
