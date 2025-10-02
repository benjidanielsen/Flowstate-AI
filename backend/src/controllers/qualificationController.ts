import { Request, Response } from 'express';
import { db } from '../database';

export class QualificationController {
  saveQualification = async (req: Request, res: Response) => {
    const { customer_id, prospect_why, qualification_data } = req.body;
    
    if (!customer_id) {
      return res.status(400).json({ error: 'customer_id is required' });
    }
    
    try {
      await db.run(
        'UPDATE customers SET prospect_why = ?, qualification_data = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
        [prospect_why || '', JSON.stringify(qualification_data || {}), customer_id]
      );
      
      res.json({ success: true, message: 'Qualification saved successfully' });
    } catch (error) {
      console.error('Error saving qualification:', error);
      res.status(500).json({ error: 'Failed to save qualification' });
    }
  };
  
  getQualification = async (req: Request, res: Response) => {
    const { id } = req.params;
    
    try {
      const customer = await db.get(
        'SELECT id, name, prospect_why, qualification_data FROM customers WHERE id = ?',
        [id]
      );
      
      if (!customer) {
        return res.status(404).json({ error: 'Customer not found' });
      }
      
      // Parse qualification_data if it's a string
      if (customer.qualification_data && typeof customer.qualification_data === 'string') {
        try {
          customer.qualification_data = JSON.parse(customer.qualification_data);
        } catch (e) {
          customer.qualification_data = {};
        }
      }
      
      res.json(customer);
    } catch (error) {
      console.error('Error getting qualification:', error);
      res.status(500).json({ error: 'Failed to get qualification' });
    }
  };
}
