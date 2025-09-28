import { Router } from 'express';
import customerRoutes from './customers';
import interactionRoutes from './interactions';

const router = Router();

router.use('/customers', customerRoutes);
router.use('/interactions', interactionRoutes);

// Health check
router.get('/health', (req, res) => {
  res.json({ status: 'OK', timestamp: new Date().toISOString() });
});

export default router;