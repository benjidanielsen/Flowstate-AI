import DatabaseManager from '../database';
import logger from '../utils/logger';
import { PoolClient } from 'pg';
import { v4 as uuidv4 } from 'uuid';
import { Reminder } from '../types'; // Assuming Reminder type is defined in types.ts

export interface FollowUp {
  id: string;
  customer_id: string;
  agent_name: string;
  due_date: Date;
  status: 'pending' | 'completed' | 'skipped';
  notes?: string;
  created_at: Date;
  updated_at: Date;
}

export class FollowUpService {
  // Follow-up timing based on Frazer Method stages
  private followUpTimes: Record<string, number> = {
    'new_lead': 1,           // 1 day - Quick response for new leads
    'qualified': 3,          // 3 days - Give them time to think
    'presentation': 7,       // 7 days - Follow up after presentation
    'follow_up': 14,         // 14 days - Longer nurture cycle
    'closed': 30             // 30 days - Check-in with closed customers
  };

  async createFollowUp(customerId: string, stage: string, agentName: string): Promise<FollowUp> {
    const days = this.followUpTimes[stage] || 7;
    const scheduledFor = new Date();
    scheduledFor.setDate(scheduledFor.getDate() + days);
    
    const notes = this.getFollowUpMessage(stage);
    
    let client: PoolClient | null = null;
    try {
      const pool = DatabaseManager.getInstance().getPool();
      client = await pool.connect();
      const id = uuidv4();
      const now = new Date().toISOString();
      const result = await client.query(
        `INSERT INTO follow_ups (id, customer_id, agent_name, due_date, status, notes, created_at, updated_at)
         VALUES ($1, $2, $3, $4, $5, $6, $7, $8) RETURNING *`,
        [
          id,
          customerId,
          agentName,
          scheduledFor.toISOString(),
          'pending',
          notes,
          now,
          now,
        ]
      );
      logger.info(`Created follow-up for customer ${customerId} at stage ${stage}, scheduled for ${scheduledFor.toISOString()}`);
      return result.rows[0];
    } finally {
      if (client) client.release();
    }
  }

  private getFollowUpMessage(stage: string): string {
    const messages: Record<string, string> = {
      'new_lead': 'Follow up with new lead - establish rapport',
      'qualified': 'Check if prospect has questions about opportunity',
      'presentation': 'Follow up on presentation - address concerns',
      'follow_up': 'Continue nurturing relationship',
      'closed': 'Check in on progress and satisfaction'
    };
    
    return messages[stage] || `Follow up on ${stage}`;
  }

  async autoScheduleFollowUps(): Promise<number> {
    let client: PoolClient | null = null;
    try {
      const pool = DatabaseManager.getInstance().getPool();
      client = await pool.connect();
      const customers = await client.query(
        `SELECT id, status FROM customers WHERE status != 'Closed - Won'`
      );
      
      let scheduled = 0;
      for (const customer of customers.rows) {
        // Assuming 'customer.status' directly maps to a stage in followUpTimes
        // And we need an agent_name for the follow-up, using a placeholder for now
        await this.createFollowUp(customer.id, customer.status, 'AutoFollowUpAgent');
        scheduled++;
      }
      
      logger.info(`Auto-scheduled ${scheduled} follow-ups`);
      return scheduled;
    } finally {
      if (client) client.release();
    }
  }

  async getUpcomingFollowUps(days: number = 7): Promise<FollowUp[]> {
    const futureDate = new Date();
    futureDate.setDate(futureDate.getDate() + days);
    
    let client: PoolClient | null = null;
    try {
      const pool = DatabaseManager.getInstance().getPool();
      client = await pool.connect();
      const result = await client.query(
        `SELECT f.*, c.name as customer_name, c.email, c.status
         FROM follow_ups f
         JOIN customers c ON f.customer_id = c.id
         WHERE f.status = 'pending'
         AND f.due_date <= $1
         ORDER BY f.due_date ASC`,
        [futureDate.toISOString()]
      );
      
      return result.rows;
    } finally {
      if (client) client.release();
    }
  }

  async getFollowUpById(id: string): Promise<FollowUp | null> {
    let client: PoolClient | null = null;
    try {
      const pool = DatabaseManager.getInstance().getPool();
      client = await pool.connect();
      const result = await client.query(
        `SELECT * FROM follow_ups WHERE id = $1`,
        [id]
      );
      return result.rows[0] || null;
    } finally {
      if (client) client.release();
    }
  }

  async getFollowUpsByCustomerId(customerId: string): Promise<FollowUp[]> {
    let client: PoolClient | null = null;
    try {
      const pool = DatabaseManager.getInstance().getPool();
      client = await pool.connect();
      const result = await client.query(
        `SELECT * FROM follow_ups WHERE customer_id = $1 ORDER BY due_date ASC`,
        [customerId]
      );
      return result.rows;
    } finally {
      if (client) client.release();
    }
  }

  async updateFollowUpStatus(id: string, status: 'completed' | 'skipped'): Promise<FollowUp | null> {
    let client: PoolClient | null = null;
    try {
      const pool = DatabaseManager.getInstance().getPool();
      client = await pool.connect();
      const now = new Date().toISOString();
      const result = await client.query(
        `UPDATE follow_ups SET status = $1, updated_at = $2 WHERE id = $3 RETURNING *`,
        [status, now, id]
      );
      return result.rows[0] || null;
    } finally {
      if (client) client.release();
    }
  }

  async getPendingFollowUps(): Promise<FollowUp[]> {
    let client: PoolClient | null = null;
    try {
      const pool = DatabaseManager.getInstance().getPool();
      client = await pool.connect();
      const result = await client.query(
        `SELECT * FROM follow_ups WHERE status = 'pending' AND due_date <= NOW() ORDER BY due_date ASC`
      );
      return result.rows;
    } finally {
      if (client) client.release();
    }
  }

  async deleteFollowUp(id: string): Promise<boolean> {
    let client: PoolClient | null = null;
    try {
      const pool = DatabaseManager.getInstance().getPool();
      client = await pool.connect();
      const result = await client.query(
        `DELETE FROM follow_ups WHERE id = $1 RETURNING id`,
        [id]
      );
      return result.rowCount !== null && result.rowCount > 0;
    } finally {
      if (client) client.release();
    }
  }
}

export const followUpService = new FollowUpService();

