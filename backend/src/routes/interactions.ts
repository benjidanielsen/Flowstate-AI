import { Router, Request, Response } from 'express';

const router = Router();

const interactionController = {
  getUpcomingInteractions: (req: Request, res: Response) => {
	res.status(200).json({ message: 'getUpcomingInteractions not implemented' });
  },
  getInteractionsByCustomer: (req: Request, res: Response) => {
	res.status(200).json({ message: 'getInteractionsByCustomer not implemented' });
  },
  createInteraction: (req: Request, res: Response) => {
	res.status(201).json({ message: 'createInteraction not implemented' });
  },
  updateInteraction: (req: Request, res: Response) => {
	res.status(200).json({ message: 'updateInteraction not implemented' });
  },
  completeInteraction: (req: Request, res: Response) => {
	res.status(200).json({ message: 'completeInteraction not implemented' });
  },
  deleteInteraction: (req: Request, res: Response) => {
	res.status(204).send();
  },
};

router.get('/upcoming', interactionController.getUpcomingInteractions);
router.get('/customer/:customerId', interactionController.getInteractionsByCustomer);
router.post('/', interactionController.createInteraction);
router.put('/:id', interactionController.updateInteraction);
router.post('/:id/complete', interactionController.completeInteraction);
router.delete('/:id', interactionController.deleteInteraction);

export default router;