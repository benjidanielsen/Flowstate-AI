import DatabaseManager from './index';
import logger from '../utils/logger';
import { v4 as uuidv4 } from 'uuid';
import { PipelineStatus, InteractionType } from '../types';
import { PoolClient } from 'pg';

const sampleCustomers = [
  {
    id: uuidv4(),
    name: 'John Smith',
    email: 'john@example.com',
    phone: '+1-555-0123',
    status: PipelineStatus.NEW_LEAD,
    notes: 'Met at networking event. Interested in fitness products.',
    next_action: 'Schedule initial call',
    next_action_date: new Date(Date.now() + 24 * 60 * 60 * 1000) // Tomorrow
  },
  {
    id: uuidv4(),
    name: 'Sarah Johnson',
    email: 'sarah@example.com',
    phone: '+1-555-0124', 
    status: PipelineStatus.WARMING_UP,
    notes: 'Building rapport. Has expressed interest in health supplements.',
    next_action: 'Send product information',
    next_action_date: new Date(Date.now() + 2 * 24 * 60 * 60 * 1000) // 2 days
  },
  {
    id: uuidv4(),
    name: 'Mike Chen',
    email: 'mike@example.com',
    phone: '+1-555-0125',
    status: PipelineStatus.INVITED,
    notes: 'Invited to product presentation webinar.',
    next_action: 'Follow up on webinar attendance',
    next_action_date: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000) // 1 week
  },
  {
    id: uuidv4(),
    name: 'Lisa Davis',
    email: 'lisa@example.com', 
    phone: '+1-555-0126',
    status: PipelineStatus.QUALIFIED,
    notes: 'Highly interested prospect. Budget confirmed.',
    next_action: 'Send presentation materials',
    next_action_date: new Date(Date.now() + 12 * 60 * 60 * 1000) // 12 hours
  },
  {
    id: uuidv4(),
    name: 'David Wilson',
    email: 'david@example.com',
    phone: '+1-555-0127',
    status: PipelineStatus.PRESENTATION_SENT,
    notes: 'Presentation sent. Waiting for response.',
    next_action: 'Follow up on presentation feedback',
    next_action_date: new Date(Date.now() + 48 * 60 * 60 * 1000) // 48 hours
  }
];

export async function seedDatabase(): Promise<void> {
  let client: PoolClient | null = null;
  try {
    const pool = DatabaseManager.getInstance().getPool();
    client = await pool.connect();
    logger.info("Starting database seed...");

    // Clear existing data
    await client.query('DELETE FROM interactions');
    await client.query('DELETE FROM reminders');
    await client.query('DELETE FROM event_logs');
    await client.query('DELETE FROM customers');
    logger.info("Cleared existing data.");

    // Insert sample customers
    for (const customer of sampleCustomers) {
      await client.query(
        `INSERT INTO customers (
          id, name, email, phone, status, notes, next_action, next_action_date,
          created_at, updated_at
        )
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)`,
        [
          customer.id,
          customer.name, 
          customer.email,
          customer.phone,
          customer.status,
          customer.notes,
          customer.next_action,
          customer.next_action_date.toISOString(),
          new Date().toISOString(),
          new Date().toISOString()
        ]
      );
      logger.info(`Inserted customer: ${customer.name}`);

      // Add sample interactions
      await client.query(
        `INSERT INTO interactions (id, customer_id, type, summary, interaction_date, created_at, updated_at)
         VALUES ($1, $2, $3, $4, $5, $6, $7)`,
        [
          uuidv4(),
          customer.id,
          InteractionType.NOTE,
          `Initial contact with ${customer.name}`,
          new Date().toISOString(),
          new Date().toISOString(),
          new Date().toISOString()
        ]
      );

      // Add sample event log
      await client.query(
        `INSERT INTO event_logs (id, customer_id, event_type, event_data, timestamp)
         VALUES ($1, $2, $3, $4, $5)`,
        [
          uuidv4(),
          customer.id,
          'customer_created',
          JSON.stringify({ name: customer.name, status: customer.status }),
          new Date().toISOString()
        ]
      );
    }
    logger.info("Database seed completed successfully.");
  } catch (error) {
    logger.error('Seed failed:', error);
    throw error;
  } finally {
    if (client) client.release();
  }
}

if (require.main === module) {
  seedDatabase()
    .then(() => {
      logger.info("Seed completed");
      process.exit(0);
    })
    .catch((err) => {
      console.error('Seed failed:', err);
      process.exit(1);
    });
}

