import { Router } from 'express';
import { QualificationController } from '../controllers/qualificationController';

const router: Router = Router();
const controller = new QualificationController();

router.post('/', controller.createQualification);
router.get('/:id', controller.getQualificationById);

export default router;
