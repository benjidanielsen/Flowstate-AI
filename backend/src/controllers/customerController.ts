import { Request, Response } from 'express';
import { CustomerService } from '../services/customerService';
import { PipelineStatus } from '../types';
import Joi from 'joi';
import { StatsService } from '../services/statsService';

const SOURCE_ENUM = ['ig','messenger','whatsapp','web','ads','manual','other'];
const customerCreateSchema = Joi.object({
  name: Joi.string().min(1).required(),
  email: Joi.string().email().optional(),
  phone: Joi.string().optional(),
  status: Joi.string().valid(...Object.values(PipelineStatus)).optional(),
  notes: Joi.string().optional(),
  next_action: Joi.string().optional(),
  next_action_date: Joi.date().iso().optional(),
  source: Joi.string().valid(...SOURCE_ENUM).optional(),
  handle_ig: Joi.string().optional(),
  handle_whatsapp: Joi.string().optional(),
  country: Joi.string().optional(),
  language: Joi.string().optional(),
  utm_json: Joi.object({
    source: Joi.string().optional(),
    medium: Joi.string().optional(),
    campaign: Joi.string().optional(),
    content: Joi.string().optional(),
    term: Joi.string().optional(),
  }).unknown(false).optional(),
  consent_json: Joi.object().optional(),
});

const customerUpdateSchema = customerCreateSchema.fork(['name'], (s) => s.optional());

export class CustomerController {
  private customerService: CustomerService;
  private statsService: StatsService;

  constructor() {
    this.customerService = new CustomerService();
    this.statsService = new StatsService();
  }

  getAllCustomers = async (req: Request, res: Response) => {
    try {
      const { status } = req.query;
      
      let customers;
      if (status && Object.values(PipelineStatus).includes(status as PipelineStatus)) {
        customers = await this.customerService.getCustomersByStatus(status as PipelineStatus);
      } else {
        customers = await this.customerService.getAllCustomers();
      }
      
      res.json(customers);
    } catch (error) {
      console.error('Error fetching customers:', error);
      res.status(500).json({ error: 'Internal server error' });
    }
  };

  getCustomerById = async (req: Request, res: Response) => {
    try {
      const { id } = req.params;
      const customer = await this.customerService.getCustomerById(id);
      
      if (!customer) {
        return res.status(404).json({ error: 'Customer not found' });
      }
      
      res.json(customer);
    } catch (error) {
      console.error('Error fetching customer:', error);
      res.status(500).json({ error: 'Internal server error' });
    }
  };

  createCustomer = async (req: Request, res: Response) => {
    try {
      const { error, value } = customerCreateSchema.validate(req.body, { abortEarly: false });
      if (error) {
        return res.status(400).json({ error: 'Invalid payload', details: error.details });
      }
      
      const customer = await this.customerService.createCustomer(value);
      res.status(201).json(customer);
    } catch (error) {
      console.error('Error creating customer:', error);
      res.status(500).json({ error: 'Internal server error' });
    }
  };

  updateCustomer = async (req: Request, res: Response) => {
    try {
      const { id } = req.params;
      const { error, value } = customerUpdateSchema.validate(req.body, { abortEarly: false });
      if (error) {
        return res.status(400).json({ error: 'Invalid payload', details: error.details });
      }
      
      const customer = await this.customerService.updateCustomer(id, value);
      
      if (!customer) {
        return res.status(404).json({ error: 'Customer not found' });
      }
      
      res.json(customer);
    } catch (error) {
      console.error('Error updating customer:', error);
      res.status(500).json({ error: 'Internal server error' });
    }
  };

  deleteCustomer = async (req: Request, res: Response) => {
    try {
      const { id } = req.params;
      const deleted = await this.customerService.deleteCustomer(id);
      
      if (!deleted) {
        return res.status(404).json({ error: 'Customer not found' });
      }
      
      res.status(204).send();
    } catch (error) {
      console.error('Error deleting customer:', error);
      res.status(500).json({ error: 'Internal server error' });
    }
  };

  moveToNextStage = async (req: Request, res: Response) => {
    try {
      const { id } = req.params;
      const customer = await this.customerService.moveCustomerToNextStage(id);
      
      if (!customer) {
        return res.status(404).json({ error: 'Customer not found' });
      }
      
      res.json(customer);
    } catch (error) {
      console.error('Error moving customer to next stage:', error);
      res.status(500).json({ error: 'Internal server error' });
    }
  };

  getPipelineStats = async (req: Request, res: Response) => {
    try {
      const counts_by_status = await this.statsService.countsByStatus();
      const dmo = await this.statsService.dmoCounters();
      const extras = await this.statsService.extraCounts();
      const pipeline = String(req.query.pipeline || '').toLowerCase();
      let counts_by_pipeline: any = undefined;
      if (['frazer','recruiting','sales'].includes(pipeline)) {
        counts_by_pipeline = await this.statsService.countsByPipeline(pipeline as any);
      }
      res.json({ counts_by_status, counts_by_pipeline, dmo_today: dmo.today, dmo_week: dmo.week, ...extras });
    } catch (error) {
      console.error('Error fetching pipeline stats:', error);
      res.status(500).json({ error: 'Internal server error' });
    }
  };
}
