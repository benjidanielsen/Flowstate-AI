import { Router } from 'express';
import { QualificationController } from '../controllers/qualificationController';

const router = Router();
const controller = new QualificationController();

router.post('/', controller.saveQualification);
router.get('/:id', controller.getQualification);

export default router;
