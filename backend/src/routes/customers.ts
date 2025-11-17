import { Router } from 'express';
import { CustomerController } from '../controllers/customerController';
import { interactionController } from '../controllers/interactionController';
import { ReminderController } from '../controllers/reminderController';
import { EventController } from '../controllers/eventController';

const router = Router();
const customerController = new CustomerController();
const reminderController = new ReminderController();
const eventController = new EventController();

router.get('/', customerController.getAllCustomers);
router.get('/stats', customerController.getPipelineStats);
router.get('/:id', customerController.getCustomerById);
router.post('/', customerController.createCustomer);
router.put('/:id', customerController.updateCustomer);
router.delete('/:id', customerController.deleteCustomer);
router.post('/:id/next-stage', customerController.moveToNextStage);
router.post('/:id/move-next-stage', customerController.moveToNextStage);

// Nested interaction routes for customer-scoped operations
router.get('/:id/interactions', interactionController.getInteractionsByCustomerId);
router.post('/:id/interactions', interactionController.createInteractionForCustomer);
router.put('/:id/interactions/:interactionId', interactionController.updateInteractionForCustomer);
router.delete('/:id/interactions/:interactionId', interactionController.deleteInteractionForCustomer);

// Nested reminder routes
router.get('/:id/reminders', reminderController.getRemindersByCustomerId);
router.post('/:id/reminders', reminderController.createForCustomer);
router.put('/:id/reminders/:reminderId', reminderController.updateForCustomer);
router.delete('/:id/reminders/:reminderId', reminderController.deleteForCustomer);

// Nested event log route
router.get('/:id/event-logs', eventController.getByCustomer);

export default router;