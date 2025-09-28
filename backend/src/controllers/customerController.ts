import { Request, Response } from 'express';
import { CustomerService } from '../services/customerService';
import { PipelineStatus } from '../types';

export class CustomerController {
  private customerService: CustomerService;

  constructor() {
    this.customerService = new CustomerService();
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
      const customerData = req.body;
      
      // Basic validation
      if (!customerData.name) {
        return res.status(400).json({ error: 'Name is required' });
      }
      
      const customer = await this.customerService.createCustomer(customerData);
      res.status(201).json(customer);
    } catch (error) {
      console.error('Error creating customer:', error);
      res.status(500).json({ error: 'Internal server error' });
    }
  };

  updateCustomer = async (req: Request, res: Response) => {
    try {
      const { id } = req.params;
      const updates = req.body;
      
      const customer = await this.customerService.updateCustomer(id, updates);
      
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
      const stats: { [key: string]: number } = {};
      
      for (const status of Object.values(PipelineStatus)) {
        const customers = await this.customerService.getCustomersByStatus(status);
        stats[status] = customers.length;
      }
      
      res.json(stats);
    } catch (error) {
      console.error('Error fetching pipeline stats:', error);
      res.status(500).json({ error: 'Internal server error' });
    }
  };
}