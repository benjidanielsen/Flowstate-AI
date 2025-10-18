"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.runMigrations = runMigrations;
const index_1 = __importDefault(require("./index"));
const logger_1 = __importDefault(require("../utils/logger"));
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
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        notes TEXT,
        next_action TEXT,
        next_action_date TIMESTAMP WITH TIME ZONE
      );

      CREATE TABLE IF NOT EXISTS interactions (
        id TEXT PRIMARY KEY,
        customer_id TEXT NOT NULL,
        type TEXT NOT NULL,
        summary TEXT NOT NULL,
        notes TEXT,
        interaction_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (customer_id) REFERENCES customers (id)
      );

      CREATE TABLE IF NOT EXISTS reminders (
        id TEXT PRIMARY KEY,
        customer_id TEXT NOT NULL,
        type TEXT NOT NULL,
        message TEXT NOT NULL,
        scheduled_for TIMESTAMP WITH TIME ZONE NOT NULL,
        completed BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        repeat_interval TEXT,
        FOREIGN KEY (customer_id) REFERENCES customers (id)
      );

      CREATE TABLE IF NOT EXISTS event_logs (
        id TEXT PRIMARY KEY,
        customer_id TEXT,
        event_type TEXT NOT NULL,
        event_data JSONB NOT NULL,
        timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
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
    },
    {
        version: 2,
        up: `
      ALTER TABLE customers ADD COLUMN source TEXT;
      ALTER TABLE customers ADD COLUMN handle_ig TEXT;
      ALTER TABLE customers ADD COLUMN handle_whatsapp TEXT;
      ALTER TABLE customers ADD COLUMN country TEXT;
      ALTER TABLE customers ADD COLUMN language TEXT;
      ALTER TABLE customers ADD COLUMN consent_json JSONB;
      ALTER TABLE customers ADD COLUMN utm_json JSONB;

      CREATE INDEX IF NOT EXISTS idx_customers_source ON customers(source);
    `
    },
    {
        version: 3,
        up: `
      ALTER TABLE customers ADD COLUMN prospect_why TEXT;
      
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
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
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
        config JSONB NOT NULL, -- Storing as JSONB for PostgreSQL
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (customer_id) REFERENCES customers (id)
      );
      CREATE INDEX IF NOT EXISTS idx_external_integrations_customer_id ON external_integrations(customer_id);
    `
    },
    {
        version: 6,
        up: `
      CREATE TABLE IF NOT EXISTS pipelines (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL UNIQUE,
        description TEXT,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
      );

      CREATE TABLE IF NOT EXISTS pipeline_stages (
        id TEXT PRIMARY KEY,
        pipeline_id TEXT NOT NULL,
        name TEXT NOT NULL,
        order_index INTEGER NOT NULL,
        description TEXT,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (pipeline_id) REFERENCES pipelines (id)
      );

      CREATE TABLE IF NOT EXISTS customer_pipeline_status (
        customer_id TEXT PRIMARY KEY,
        pipeline_id TEXT NOT NULL,
        current_stage_id TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'Active', -- e.g., Active, Completed, Dropped
        started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        last_updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (customer_id) REFERENCES customers (id),
        FOREIGN KEY (pipeline_id) REFERENCES pipelines (id),
        FOREIGN KEY (current_stage_id) REFERENCES pipeline_stages (id)
      );

      CREATE INDEX IF NOT EXISTS idx_pipelines_name ON pipelines(name);
      CREATE INDEX IF NOT EXISTS idx_pipeline_stages_pipeline_id ON pipeline_stages(pipeline_id);
      CREATE INDEX IF NOT EXISTS idx_customer_pipeline_status_customer_id ON customer_pipeline_status(customer_id);
      CREATE INDEX IF NOT EXISTS idx_customer_pipeline_status_pipeline_id ON customer_pipeline_status(pipeline_id);
    `
    }
];
async function runMigrations() {
    const dbManager = index_1.default.getInstance();
    const pool = dbManager.getPool();
    let client = null;
    try {
        client = await pool.connect();
        await client.query(`
      CREATE TABLE IF NOT EXISTS migrations (
        version INTEGER PRIMARY KEY,
        applied_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
      );
    `);
        const result = await client.query('SELECT MAX(version) as version FROM migrations');
        const currentVersion = result.rows[0]?.version || 0;
        logger_1.default.info(`Current database version: ${currentVersion}`);
        const pendingMigrations = migrations.filter(m => m.version > currentVersion);
        if (pendingMigrations.length === 0) {
            logger_1.default.info('No pending migrations');
            return;
        }
        logger_1.default.info(`Applying ${pendingMigrations.length} pending migrations...`);
        for (const migration of pendingMigrations) {
            await client.query(migration.up);
            await client.query('INSERT INTO migrations (version) VALUES ($1)', [migration.version]);
            logger_1.default.info(`Migration ${migration.version} completed`);
        }
        logger_1.default.info('All migrations completed successfully');
    }
    catch (error) {
        logger_1.default.error('Failed to run migrations:', error);
        throw error; // Re-throw to indicate migration failure
    }
    finally {
        if (client) {
            client.release();
        }
    }
}
if (require.main === module) {
    // Ensure the database connection is established before running migrations
    index_1.default.getInstance().connect()
        .then(() => runMigrations())
        .then(() => {
        logger_1.default.info('Migration process finished.');
        process.exit(0);
    })
        .catch((err) => {
        logger_1.default.error('Fatal error during migration process:', err);
        process.exit(1);
    });
}
//# sourceMappingURL=migrate.js.map