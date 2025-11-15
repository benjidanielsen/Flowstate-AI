import DatabaseManager from './index';
import { safeLogger } from '../utils/piiRedaction';

interface Migration {
  version: number;
  description: string;
  up: string;
}

const migrations: Migration[] = [
  {
    version: 1,
    description: 'Initial CRM core tables',
    up: `
      CREATE TABLE IF NOT EXISTS customers (
        id UUID PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT,
        phone TEXT,
        status TEXT NOT NULL DEFAULT 'New Lead',
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        notes TEXT,
        next_action TEXT,
        next_action_date TIMESTAMPTZ,
        source TEXT,
        prospect_why TEXT,
        handle_ig TEXT,
        handle_whatsapp TEXT,
        country TEXT,
        language TEXT,
        consent_json JSONB,
        utm_json JSONB
      );

      CREATE TABLE IF NOT EXISTS interactions (
        id UUID PRIMARY KEY,
        customer_id UUID REFERENCES customers(id) ON DELETE CASCADE,
        type TEXT NOT NULL,
        summary TEXT NOT NULL,
        notes TEXT,
        interaction_date TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
      );

      CREATE TABLE IF NOT EXISTS reminders (
        id UUID PRIMARY KEY,
        customer_id UUID REFERENCES customers(id) ON DELETE CASCADE,
        type TEXT NOT NULL,
        message TEXT NOT NULL,
        scheduled_for TIMESTAMPTZ NOT NULL,
        completed BOOLEAN NOT NULL DEFAULT FALSE,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        repeat_interval TEXT
      );

      CREATE TABLE IF NOT EXISTS event_logs (
        id UUID PRIMARY KEY,
        customer_id UUID REFERENCES customers(id) ON DELETE SET NULL,
        event_type TEXT NOT NULL,
        event_data JSONB NOT NULL,
        timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        user_id TEXT
      );

      CREATE TABLE IF NOT EXISTS users (
        id UUID PRIMARY KEY,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'agent',
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
      );

      CREATE TABLE IF NOT EXISTS external_integrations (
        id UUID PRIMARY KEY,
        customer_id UUID REFERENCES customers(id) ON DELETE CASCADE,
        type TEXT NOT NULL,
        config JSONB NOT NULL,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
      );

      CREATE INDEX IF NOT EXISTS idx_customers_status ON customers(status);
      CREATE INDEX IF NOT EXISTS idx_customers_updated_at ON customers(updated_at);
      CREATE INDEX IF NOT EXISTS idx_customers_source ON customers(source);
      CREATE INDEX IF NOT EXISTS idx_customers_country ON customers(country);
      CREATE INDEX IF NOT EXISTS idx_customers_language ON customers(language);
      CREATE INDEX IF NOT EXISTS idx_customers_email ON customers(email);
      CREATE INDEX IF NOT EXISTS idx_customers_phone ON customers(phone);
      CREATE INDEX IF NOT EXISTS idx_customers_prospect_why ON customers(prospect_why);
      CREATE INDEX IF NOT EXISTS idx_interactions_customer_id ON interactions(customer_id);
      CREATE INDEX IF NOT EXISTS idx_interactions_type ON interactions(type);
      CREATE INDEX IF NOT EXISTS idx_interactions_interaction_date ON interactions(interaction_date);
      CREATE INDEX IF NOT EXISTS idx_reminders_customer_id ON reminders(customer_id);
      CREATE INDEX IF NOT EXISTS idx_reminders_scheduled_for ON reminders(scheduled_for);
      CREATE INDEX IF NOT EXISTS idx_reminders_completed ON reminders(completed);
      CREATE INDEX IF NOT EXISTS idx_event_logs_customer_id ON event_logs(customer_id);
      CREATE INDEX IF NOT EXISTS idx_event_logs_event_type ON event_logs(event_type);
      CREATE INDEX IF NOT EXISTS idx_event_logs_timestamp ON event_logs(timestamp);
      CREATE INDEX IF NOT EXISTS idx_external_integrations_customer_id ON external_integrations(customer_id);
    `,
  },
  {
    version: 2,
    description: 'Prospects and task management tables',
    up: `
      CREATE TABLE IF NOT EXISTS prospects (
        id UUID PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT,
        phone TEXT,
        status TEXT NOT NULL DEFAULT 'New Lead',
        interest_level TEXT,
        source TEXT,
        owner TEXT,
        segmentation TEXT,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        notes TEXT
      );

      CREATE TABLE IF NOT EXISTS tasks (
        id UUID PRIMARY KEY,
        customer_id UUID REFERENCES customers(id) ON DELETE CASCADE,
        prospect_id UUID REFERENCES prospects(id) ON DELETE SET NULL,
        title TEXT NOT NULL,
        description TEXT,
        due_date TIMESTAMPTZ,
        status TEXT NOT NULL DEFAULT 'open',
        priority TEXT NOT NULL DEFAULT 'normal',
        owner TEXT,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        metadata JSONB
      );

      ALTER TABLE interactions ADD COLUMN IF NOT EXISTS prospect_id UUID REFERENCES prospects(id) ON DELETE SET NULL;

      CREATE INDEX IF NOT EXISTS idx_prospects_status ON prospects(status);
      CREATE INDEX IF NOT EXISTS idx_prospects_owner ON prospects(owner);
      CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
      CREATE INDEX IF NOT EXISTS idx_tasks_due_date ON tasks(due_date);
      CREATE INDEX IF NOT EXISTS idx_tasks_customer_id ON tasks(customer_id);
      CREATE INDEX IF NOT EXISTS idx_tasks_prospect_id ON tasks(prospect_id);
    `,
  },
];

function splitStatements(sql: string): string[] {
  return sql
    .split(';')
    .map(stmt => stmt.trim())
    .filter(stmt => stmt.length > 0);
}

export async function runMigrations(): Promise<void> {
  const manager = DatabaseManager.getInstance();
  const pool = await manager.connect();

  await pool.query(`
    CREATE TABLE IF NOT EXISTS migrations (
      version INTEGER PRIMARY KEY,
      applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    )
  `);

  const currentVersionResult = await pool.query<{ version: number }>(
    'SELECT version FROM migrations ORDER BY version DESC LIMIT 1'
  );
  const currentVersion = currentVersionResult.rows[0]?.version || 0;
  const pending = migrations.filter(m => m.version > currentVersion).sort((a, b) => a.version - b.version);

  if (!pending.length) {
    safeLogger.info('No pending migrations');
    return;
  }

  for (const migration of pending) {
    const client = await pool.connect();
    safeLogger.info(`Running migration v${migration.version}: ${migration.description}`);
    try {
      await client.query('BEGIN');
      for (const statement of splitStatements(migration.up)) {
        await client.query(statement);
      }
      await client.query('INSERT INTO migrations (version) VALUES ($1)', [migration.version]);
      await client.query('COMMIT');
      safeLogger.info(`Migration v${migration.version} completed`);
    } catch (error) {
      await client.query('ROLLBACK');
      safeLogger.error(`Migration v${migration.version} failed`, error);
      throw error;
    } finally {
      client.release();
    }
  }
}

if (require.main === module) {
  runMigrations()
    .then(() => {
      safeLogger.info('All migrations completed');
      process.exit(0);
    })
    .catch((err) => {
      safeLogger.error('Migration failed', err);
      process.exit(1);
    });
}
