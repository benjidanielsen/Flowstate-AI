import DatabaseManager from './index';
import logger from '../utils/logger';

const migrations = [
  {
    version: 1,
    up: `
      CREATE TABLE IF NOT EXISTS customers (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT,
        phone TEXT,
        status TEXT NOT NULL DEFAULT 'New Lead',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        notes TEXT,
        next_action TEXT,
        next_action_date DATETIME
      );

      CREATE TABLE IF NOT EXISTS interactions (
        id TEXT PRIMARY KEY,
        customer_id TEXT NOT NULL,
        type TEXT NOT NULL,
        summary TEXT NOT NULL,
        notes TEXT,
        interaction_date DATETIME DEFAULT CURRENT_TIMESTAMP,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (customer_id) REFERENCES customers (id)
      );

      CREATE TABLE IF NOT EXISTS reminders (
        id TEXT PRIMARY KEY,
        customer_id TEXT NOT NULL,
        type TEXT NOT NULL,
        message TEXT NOT NULL,
        scheduled_for DATETIME NOT NULL,
        completed BOOLEAN DEFAULT 0,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        repeat_interval TEXT,
        FOREIGN KEY (customer_id) REFERENCES customers (id)
      );

      CREATE TABLE IF NOT EXISTS event_logs (
        id TEXT PRIMARY KEY,
        customer_id TEXT,
        event_type TEXT NOT NULL,
        event_data TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        user_id TEXT
      );

      CREATE INDEX IF NOT EXISTS idx_customers_status ON customers(status);
      CREATE INDEX IF NOT EXISTS idx_customers_updated_at ON customers(updated_at);
      CREATE INDEX IF NOT EXISTS idx_interactions_customer_id ON interactions(customer_id);
      CREATE INDEX IF NOT EXISTS idx_reminders_customer_id ON reminders(customer_id);
      CREATE INDEX IF NOT EXISTS idx_reminders_scheduled_for ON reminders(scheduled_for);
      CREATE INDEX IF NOT EXISTS idx_event_logs_customer_id ON event_logs(customer_id);
      CREATE INDEX IF NOT EXISTS idx_event_logs_timestamp ON event_logs(timestamp);
    `
  }
  ,
  {
    version: 2,
    up: `
      -- Extend customers with metadata for consent/utm/source/handles per docs
      ALTER TABLE customers ADD COLUMN source TEXT;
      ALTER TABLE customers ADD COLUMN handle_ig TEXT;
      ALTER TABLE customers ADD COLUMN handle_whatsapp TEXT;
      ALTER TABLE customers ADD COLUMN country TEXT;
      ALTER TABLE customers ADD COLUMN language TEXT;
      ALTER TABLE customers ADD COLUMN consent_json TEXT;
      ALTER TABLE customers ADD COLUMN utm_json TEXT;

      CREATE INDEX IF NOT EXISTS idx_customers_source ON customers(source);
    `
  },
  {
    version: 3,
    up: `
      -- Add prospect_why field for Frazer Method requirement
      ALTER TABLE customers ADD COLUMN prospect_why TEXT;
      
      -- Update existing customers with old status values to new Frazer Method stages
      UPDATE customers SET status = 'New Lead' WHERE status = 'Lead';
      UPDATE customers SET status = 'Warming Up' WHERE status = 'Relationship';
      UPDATE customers SET status = 'Closed - Won' WHERE status = 'SIGNED-UP';
      
      CREATE INDEX IF NOT EXISTS idx_customers_prospect_why ON customers(prospect_why);
    `
  },
  {
    version: 4,
    up: `
      CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
      );
      CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
      CREATE INDEX IF NOT EXISTS idx_customers_email ON customers(email);
      CREATE INDEX IF NOT EXISTS idx_customers_phone ON customers(phone);
      CREATE INDEX IF NOT EXISTS idx_customers_country ON customers(country);
      CREATE INDEX IF NOT EXISTS idx_customers_language ON customers(language);
      CREATE INDEX IF NOT EXISTS idx_interactions_interaction_date ON interactions(interaction_date);
      CREATE INDEX IF NOT EXISTS idx_reminders_completed ON reminders(completed);
      CREATE INDEX IF NOT EXISTS idx_event_logs_event_type ON event_logs(event_type);
    `
  },
  {
    version: 5,
    up: `
      CREATE TABLE IF NOT EXISTS external_integrations (
        id TEXT PRIMARY KEY,
        customer_id TEXT NOT NULL,
        type TEXT NOT NULL,
        config TEXT NOT NULL, -- Storing as JSON string
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (customer_id) REFERENCES customers (id)
      );
      CREATE INDEX IF NOT EXISTS idx_external_integrations_customer_id ON external_integrations(customer_id);
    `
  },
  {
    version: 6,
    up: `
      ALTER TABLE interactions ADD COLUMN content TEXT;
      ALTER TABLE interactions ADD COLUMN scheduled_for DATETIME;
      ALTER TABLE interactions ADD COLUMN completed BOOLEAN DEFAULT 0;
      UPDATE interactions SET content = summary WHERE content IS NULL;
      UPDATE interactions SET scheduled_for = interaction_date WHERE scheduled_for IS NULL;
      UPDATE interactions SET completed = COALESCE(completed, 0);
      CREATE INDEX IF NOT EXISTS idx_interactions_completed ON interactions(completed);
      CREATE INDEX IF NOT EXISTS idx_interactions_scheduled_for ON interactions(scheduled_for);
    `
  }
];

export async function runMigrations(): Promise<void> {
  const dbManager = DatabaseManager.getInstance();
  const db = await dbManager.connect();

  return new Promise((resolve, reject) => {
    // Create migrations table
    db.run(`
      CREATE TABLE IF NOT EXISTS migrations (
        version INTEGER PRIMARY KEY,
        applied_at DATETIME DEFAULT CURRENT_TIMESTAMP
      )
    `, (err) => {
      if (err) {
        reject(err);
        return;
      }

      // Get current version
      db.get('SELECT MAX(version) as version FROM migrations', (err, row: any) => {
        if (err) {
          reject(err);
          return;
        }

        const currentVersion = row?.version || 0;
        const pendingMigrations = migrations.filter(m => m.version > currentVersion);

        if (pendingMigrations.length === 0) {
          logger.info("No pending migrations");
          resolve();
          return;
        }

        // Run pending migrations
        let completed = 0;
        pendingMigrations.forEach(migration => {
          db.exec(migration.up, (err) => {
            if (err) {
              logger.error(`Migration ${migration.version} failed:`, err);
              reject(err);
              return;
            }

            // Record migration
            db.run('INSERT INTO migrations (version) VALUES (?)', [migration.version], (err) => {
              if (err) {
                reject(err);
                return;
              }

              completed++;
              logger.info(`Migration ${migration.version} completed`);
              
              if (completed === pendingMigrations.length) {
                resolve();
              }
            });
          });
        });
      });
    });
  });
}

if (require.main === module) {
  runMigrations()
    .then(() => {
      logger.info("All migrations completed");
      process.exit(0);
    })
    .catch((err) => {
      console.error('Migration failed:', err);
      process.exit(1);
    });
}
