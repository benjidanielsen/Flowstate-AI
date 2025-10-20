import { Router } from 'express';
import featureFlagController from '../controllers/featureFlagController';

const router: Router = Router();

router.get('/', featureFlagController.list);
router.get('/active', featureFlagController.getActive);
router.get('/:key', featureFlagController.get);
router.put('/:key', featureFlagController.upsert);

export default router;
