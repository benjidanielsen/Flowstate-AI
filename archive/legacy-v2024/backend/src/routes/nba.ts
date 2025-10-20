import { Router } from 'express';
import { NBAController } from '../controllers/nbaController';

const router: Router = Router();
const controller = new NBAController();

router.get('/', controller.getRecommendations);
router.post('/analyze', controller.analyze);

export default router;

