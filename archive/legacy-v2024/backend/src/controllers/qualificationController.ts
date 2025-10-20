import { Request, Response } from 'express';
import { QualificationService } from '../services/qualificationService';
import logger from '../utils/logger';

const qualificationService = new QualificationService();

export class QualificationController {
  async createQualification(req: Request, res: Response): Promise<void> {
    try {
      const { customer_id, question, expected_answer, status, agent_name } = req.body;

      if (!customer_id || !question || !expected_answer || !status) {
        res.status(400).json({ error: 'customer_id, question, expected_answer, and status are required' });
        return;
      }

      const qualification = await qualificationService.createQualification({
        customer_id,
        question,
        expected_answer,
        status,
        agent_name,
      });
      res.status(201).json(qualification);
    } catch (error: any) {
      logger.error('Error creating qualification:', error);
      res.status(500).json({ error: 'Failed to create qualification' });
    }
  }

  async getQualificationById(req: Request, res: Response): Promise<void> {
    try {
      const { id } = req.params;
      const qualification = await qualificationService.getQualificationById(id);

      if (!qualification) {
        res.status(404).json({ error: 'Qualification not found' });
        return;
      }
      res.json(qualification);
    } catch (error: any) {
      logger.error('Error getting qualification by ID:', error);
      res.status(500).json({ error: 'Failed to get qualification' });
    }
  }

  async updateQualificationStatus(req: Request, res: Response): Promise<void> {
    try {
      const { id } = req.params;
      const { status } = req.body;

      if (!status) {
        res.status(400).json({ error: 'status is required' });
        return;
      }

      const updatedQualification = await qualificationService.updateQualificationStatus(id, status);
      if (!updatedQualification) {
        res.status(404).json({ error: 'Qualification not found' });
        return;
      }
      res.json(updatedQualification);
    } catch (error: any) {
      logger.error('Error updating qualification status:', error);
      res.status(500).json({ error: 'Failed to update qualification status' });
    }
  }

  async recordQualificationAnswer(req: Request, res: Response): Promise<void> {
    try {
      const { qualification_id, answer, is_correct, agent_name } = req.body;

      if (!qualification_id || !answer || typeof is_correct !== 'boolean') {
        res.status(400).json({ error: 'qualification_id, answer, and is_correct are required' });
        return;
      }

      const qualificationAnswer = await qualificationService.recordQualificationAnswer({
        qualification_id,
        answer,
        is_correct,
        agent_name,
      });
      res.status(201).json(qualificationAnswer);
    } catch (error: any) {
      logger.error('Error recording qualification answer:', error);
      res.status(500).json({ error: 'Failed to record qualification answer' });
    }
  }

  async getAnswersForQualification(req: Request, res: Response): Promise<void> {
    try {
      const { qualificationId } = req.params;
      const answers = await qualificationService.getAnswersForQualification(qualificationId);
      res.json(answers);
    } catch (error: any) {
      logger.error('Error getting answers for qualification:', error);
      res.status(500).json({ error: 'Failed to get answers for qualification' });
    }
  }

  async getQualificationsByCustomerId(req: Request, res: Response): Promise<void> {
    try {
      const { customerId } = req.params;
      const qualifications = await qualificationService.getQualificationsByCustomerId(customerId);
      res.json(qualifications);
    } catch (error: any) {
      logger.error('Error getting qualifications by customer ID:', error);
      res.status(500).json({ error: 'Failed to get qualifications by customer ID' });
    }
  }

  async getPendingQualifications(req: Request, res: Response): Promise<void> {
    try {
      const qualifications = await qualificationService.getPendingQualifications();
      res.json(qualifications);
    } catch (error: any) {
      logger.error('Error getting pending qualifications:', error);
      res.status(500).json({ error: 'Failed to get pending qualifications' });
    }
  }

  async deleteQualification(req: Request, res: Response): Promise<void> {
    try {
      const { id } = req.params;
      const success = await qualificationService.deleteQualification(id);
      if (!success) {
        res.status(404).json({ error: 'Qualification not found' });
        return;
      }
      res.status(204).send(); // No Content
    } catch (error: any) {
      logger.error('Error deleting qualification:', error);
      res.status(500).json({ error: 'Failed to delete qualification' });
    }
  }

  async deleteQualificationAnswer(req: Request, res: Response): Promise<void> {
    try {
      const { id } = req.params;
      const success = await qualificationService.deleteQualificationAnswer(id);
      if (!success) {
        res.status(404).json({ error: 'Qualification answer not found' });
        return;
      }
      res.status(204).send(); // No Content
    } catch (error: any) {
      logger.error('Error deleting qualification answer:', error);
      res.status(500).json({ error: 'Failed to delete qualification answer' });
    }
  }

  async getCustomerQualificationSummary(req: Request, res: Response): Promise<void> {
    try {
      const summary = await qualificationService.getCustomerQualificationSummary();
      res.json(summary);
    } catch (error: any) {
      logger.error('Error getting customer qualification summary:', error);
      res.status(500).json({ error: 'Failed to get customer qualification summary' });
    }
  }
}

export default new QualificationController();

