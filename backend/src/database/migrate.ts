import DatabaseManager from './index';

const migrations = [
  {
    version: 1,
    up: `
      CREATE TABLE IF NOT EXISTS customers (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT,
        phone TEXT,
        status TEXT NOT NULL DEFAULT 'Lead',
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
        content TEXT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        scheduled_for DATETIME,
        completed BOOLEAN DEFAULT 0,
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
          console.log('No pending migrations');
          resolve();
          return;
        }

        // Run pending migrations
        let completed = 0;
        pendingMigrations.forEach(migration => {
          db.exec(migration.up, (err) => {
            if (err) {
              console.error(`Migration ${migration.version} failed:`, err);
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
              console.log(`Migration ${migration.version} completed`);
              
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
      console.log('All migrations completed');
      process.exit(0);
    })
    .catch((err) => {
      console.error('Migration failed:', err);
      process.exit(1);
    });
}
