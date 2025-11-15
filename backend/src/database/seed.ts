import { v4 as uuidv4 } from 'uuid';
import DatabaseManager from './index';
import { safeLogger } from '../utils/piiRedaction';
import { InteractionType, PipelineStatus } from '../types';

interface SeedCustomer {
  id: string;
  name: string;
  email: string;
  phone: string;
  status: PipelineStatus;
  notes: string;
  next_action: string;
  next_action_date: Date;
  source: string;
  country: string;
  language: string;
  consent_json: Record<string, unknown>;
  utm_json: Record<string, unknown>;
}

const sampleCustomers: SeedCustomer[] = [
  {
    id: uuidv4(),
    name: 'John Smith',
    email: 'john@example.com',
    phone: '+1-555-0123',
    status: PipelineStatus.NEW_LEAD,
    notes: 'Met at networking event. Interested in fitness products.',
    next_action: 'Schedule initial call',
    next_action_date: new Date(Date.now() + 24 * 60 * 60 * 1000),
    source: 'ig',
    country: 'US',
    language: 'en',
    consent_json: { email: true, sms: false },
    utm_json: { source: 'ig', campaign: 'frazer_method_launch' },
  },
  {
    id: uuidv4(),
    name: 'Sarah Johnson',
    email: 'sarah@example.com',
    phone: '+1-555-0124',
    status: PipelineStatus.WARMING_UP,
    notes: 'Building rapport. Has expressed interest in health supplements.',
    next_action: 'Send product information',
    next_action_date: new Date(Date.now() + 2 * 24 * 60 * 60 * 1000),
    source: 'ads',
    country: 'US',
    language: 'en',
    consent_json: { email: true, sms: true },
    utm_json: { source: 'ads', campaign: 'conversion_push' },
  },
  {
    id: uuidv4(),
    name: 'Mike Chen',
    email: 'mike@example.com',
    phone: '+1-555-0125',
    status: PipelineStatus.INVITED,
    notes: 'Invited to product presentation webinar.',
    next_action: 'Follow up on webinar attendance',
    next_action_date: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000),
    source: 'web',
    country: 'SG',
    language: 'en',
    consent_json: { email: true },
    utm_json: { source: 'web', campaign: 'asia_expansion' },
  },
  {
    id: uuidv4(),
    name: 'Lisa Davis',
    email: 'lisa@example.com',
    phone: '+1-555-0126',
    status: PipelineStatus.QUALIFIED,
    notes: 'Highly interested prospect. Budget confirmed.',
    next_action: 'Send presentation materials',
    next_action_date: new Date(Date.now() + 12 * 60 * 60 * 1000),
    source: 'messenger',
    country: 'US',
    language: 'en',
    consent_json: { email: true, sms: true },
    utm_json: { source: 'messenger', campaign: 'referral_program' },
  },
  {
    id: uuidv4(),
    name: 'David Wilson',
    email: 'david@example.com',
    phone: '+1-555-0127',
    status: PipelineStatus.PRESENTATION_SENT,
    notes: 'Presentation sent. Waiting for response.',
    next_action: 'Follow up on presentation feedback',
    next_action_date: new Date(Date.now() + 48 * 60 * 60 * 1000),
    source: 'manual',
    country: 'CA',
    language: 'en',
    consent_json: { email: true },
    utm_json: { source: 'manual', campaign: 'partner_intros' },
  },
];

const sampleProspects = [
  {
    id: uuidv4(),
    name: 'Noah Perez',
    email: 'noah@example.com',
    phone: '+1-555-0130',
    status: 'Discovery',
    interest_level: 'Hot',
    source: 'web',
    owner: 'frazer',
    segmentation: 'Fitness Influencer',
    notes: 'Has a 50k community focused on wellness tips.'
  },
  {
    id: uuidv4(),
    name: 'Emily Clark',
    email: 'emily@example.com',
    phone: '+1-555-0131',
    status: 'Nurture',
    interest_level: 'Warm',
    source: 'podcast',
    owner: 'growth-team',
    segmentation: 'Business Coaching',
    notes: 'Hosts a top podcast, interested in partnership.'
  }
];

const sampleTasks = (customers: SeedCustomer[]) => [
  {
    id: uuidv4(),
    customer_id: customers[0].id,
    prospect_id: null,
    title: 'Share onboarding deck',
    description: 'Send the Frazer Method onboarding deck before kickoff call.',
    due_date: new Date(Date.now() + 6 * 60 * 60 * 1000),
    status: 'open',
    priority: 'high',
    owner: 'success-team',
    metadata: { channel: 'email' }
  },
  {
    id: uuidv4(),
    customer_id: customers[2].id,
    prospect_id: null,
    title: 'Confirm webinar attendance',
    description: 'Send reminder and confirm attendance for Thursday webinar.',
    due_date: new Date(Date.now() + 3 * 60 * 60 * 1000),
    status: 'in_progress',
    priority: 'normal',
    owner: 'sales',
    metadata: { followUp: true }
  },
  {
    id: uuidv4(),
    customer_id: null,
    prospect_id: sampleProspects[0].id,
    title: 'Draft co-marketing plan',
    description: 'Outline potential collaboration for IG Live training.',
    due_date: new Date(Date.now() + 5 * 24 * 60 * 60 * 1000),
    status: 'open',
    priority: 'high',
    owner: 'marketing',
    metadata: { partnerTier: 'gold' }
  }
];

const sampleInteractions = (customers: SeedCustomer[]) => customers.map(customer => ({
  id: uuidv4(),
  customer_id: customer.id,
  type: InteractionType.NOTE,
  summary: `Initial touchpoint with ${customer.name}`,
  notes: customer.notes,
  interaction_date: new Date(),
}));

export async function seedDatabase(): Promise<void> {
  const manager = DatabaseManager.getInstance();
  const pool = await manager.connect();
  const client = await pool.connect();

  safeLogger.info('Starting database seed...');

  try {
    await client.query('BEGIN');
    await client.query('TRUNCATE TABLE tasks, interactions, reminders, event_logs, external_integrations, prospects, customers RESTART IDENTITY CASCADE');

    for (const customer of sampleCustomers) {
      await client.query(
        `INSERT INTO customers (
          id, name, email, phone, status, notes, next_action, next_action_date,
          created_at, updated_at, source, prospect_why, handle_ig, handle_whatsapp,
          country, language, consent_json, utm_json
        ) VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13,$14,$15,$16,$17,$18)`,
        [
          customer.id,
          customer.name,
          customer.email,
          customer.phone,
          customer.status,
          customer.notes,
          customer.next_action,
          customer.next_action_date,
          new Date(),
          new Date(),
          customer.source,
          customer.notes,
          customer.source === 'ig' ? customer.name.replace(/\s+/g, '').toLowerCase() : null,
          customer.source === 'whatsapp' ? customer.phone : null,
          customer.country,
          customer.language,
          customer.consent_json,
          customer.utm_json,
        ]
      );
    }

    for (const prospect of sampleProspects) {
      await client.query(
        `INSERT INTO prospects (id, name, email, phone, status, interest_level, source, owner, segmentation, created_at, updated_at, notes)
         VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,NOW(),NOW(),$10)`,
        [
          prospect.id,
          prospect.name,
          prospect.email,
          prospect.phone,
          prospect.status,
          prospect.interest_level,
          prospect.source,
          prospect.owner,
          prospect.segmentation,
          prospect.notes,
        ]
      );
    }

    for (const interaction of sampleInteractions(sampleCustomers)) {
      await client.query(
        `INSERT INTO interactions (id, customer_id, type, summary, notes, interaction_date, created_at, updated_at)
         VALUES ($1,$2,$3,$4,$5,$6,NOW(),NOW())`,
        [
          interaction.id,
          interaction.customer_id,
          interaction.type,
          interaction.summary,
          interaction.notes,
          interaction.interaction_date,
        ]
      );
    }

    const tasks = sampleTasks(sampleCustomers);
    for (const task of tasks) {
      await client.query(
        `INSERT INTO tasks (id, customer_id, prospect_id, title, description, due_date, status, priority, owner, created_at, updated_at, metadata)
         VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,NOW(),NOW(),$10)`,
        [
          task.id,
          task.customer_id,
          task.prospect_id,
          task.title,
          task.description,
          task.due_date,
          task.status,
          task.priority,
          task.owner,
          task.metadata,
        ]
      );
    }

    safeLogger.info('Database seed completed successfully');
    await client.query('COMMIT');
  } catch (error) {
    await client.query('ROLLBACK');
    safeLogger.error('Seed failed', error);
    throw error;
  } finally {
    client.release();
  }
}

if (require.main === module) {
  seedDatabase()
    .then(() => {
      safeLogger.info('Seed completed');
      process.exit(0);
    })
    .catch((err) => {
      safeLogger.error('Seed failed', err);
      process.exit(1);
    });
}
