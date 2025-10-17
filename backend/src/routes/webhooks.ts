import { Router } from 'express';
import { WebhookController } from '../controllers/webhookController';

const router = Router();
const controller = new WebhookController();

router.post('/dm', controller.dm);
router.post('/capi/lead', controller.capiLead);

export default router;

