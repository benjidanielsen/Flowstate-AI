import { Router } from 'express';
import { pipelineController } from '../controllers/pipelineController';

const router: Router = Router();

router.get('/', pipelineController.list);
router.post('/', pipelineController.create);
router.get('/:pipelineId', pipelineController.getById);
router.post('/:pipelineId/stages', (req, res) => pipelineController.upsertStage(req, res));
router.put('/:pipelineId/stages/:stageId', pipelineController.upsertStage);
router.post('/customers/:customerId/stage', pipelineController.assignCustomerStage);

export default router;
