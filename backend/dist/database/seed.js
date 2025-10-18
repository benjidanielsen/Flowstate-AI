"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.seedDatabase = seedDatabase;
const index_1 = __importDefault(require("./index"));
const logger_1 = __importDefault(require("../utils/logger"));
const uuid_1 = require("uuid");
const types_1 = require("../types");
const sampleCustomers = [
    {
        id: (0, uuid_1.v4)(),
        name: 'John Smith',
        email: 'john@example.com',
        phone: '+1-555-0123',
        status: types_1.PipelineStatus.NEW_LEAD,
        notes: 'Met at networking event. Interested in fitness products.',
        next_action: 'Schedule initial call',
        next_action_date: new Date(Date.now() + 24 * 60 * 60 * 1000) // Tomorrow
    },
    {
        id: (0, uuid_1.v4)(),
        name: 'Sarah Johnson',
        email: 'sarah@example.com',
        phone: '+1-555-0124',
        status: types_1.PipelineStatus.WARMING_UP,
        notes: 'Building rapport. Has expressed interest in health supplements.',
        next_action: 'Send product information',
        next_action_date: new Date(Date.now() + 2 * 24 * 60 * 60 * 1000) // 2 days
    },
    {
        id: (0, uuid_1.v4)(),
        name: 'Mike Chen',
        email: 'mike@example.com',
        phone: '+1-555-0125',
        status: types_1.PipelineStatus.INVITED,
        notes: 'Invited to product presentation webinar.',
        next_action: 'Follow up on webinar attendance',
        next_action_date: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000) // 1 week
    },
    {
        id: (0, uuid_1.v4)(),
        name: 'Lisa Davis',
        email: 'lisa@example.com',
        phone: '+1-555-0126',
        status: types_1.PipelineStatus.QUALIFIED,
        notes: 'Highly interested prospect. Budget confirmed.',
        next_action: 'Send presentation materials',
        next_action_date: new Date(Date.now() + 12 * 60 * 60 * 1000) // 12 hours
    },
    {
        id: (0, uuid_1.v4)(),
        name: 'David Wilson',
        email: 'david@example.com',
        phone: '+1-555-0127',
        status: types_1.PipelineStatus.PRESENTATION_SENT,
        notes: 'Presentation sent. Waiting for response.',
        next_action: 'Follow up on presentation feedback',
        next_action_date: new Date(Date.now() + 48 * 60 * 60 * 1000) // 48 hours
    }
];
async function seedDatabase() {
    let client = null;
    try {
        const pool = index_1.default.getInstance().getPool();
        client = await pool.connect();
        logger_1.default.info("Starting database seed...");
        // Clear existing data
        await client.query('DELETE FROM interactions');
        await client.query('DELETE FROM reminders');
        await client.query('DELETE FROM event_logs');
        await client.query('DELETE FROM customers');
        logger_1.default.info("Cleared existing data.");
        // Insert sample customers
        for (const customer of sampleCustomers) {
            await client.query(`INSERT INTO customers (
          id, name, email, phone, status, notes, next_action, next_action_date,
          created_at, updated_at
        )
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)`, [
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
            ]);
            logger_1.default.info(`Inserted customer: ${customer.name}`);
            // Add sample interactions
            await client.query(`INSERT INTO interactions (id, customer_id, type, summary, interaction_date, created_at, updated_at)
         VALUES ($1, $2, $3, $4, $5, $6, $7)`, [
                (0, uuid_1.v4)(),
                customer.id,
                types_1.InteractionType.NOTE,
                `Initial contact with ${customer.name}`,
                new Date().toISOString(),
                new Date().toISOString(),
                new Date().toISOString()
            ]);
            // Add sample event log
            await client.query(`INSERT INTO event_logs (id, customer_id, event_type, event_data, timestamp)
         VALUES ($1, $2, $3, $4, $5)`, [
                (0, uuid_1.v4)(),
                customer.id,
                'customer_created',
                JSON.stringify({ name: customer.name, status: customer.status }),
                new Date().toISOString()
            ]);
        }
        logger_1.default.info("Database seed completed successfully.");
    }
    catch (error) {
        logger_1.default.error('Seed failed:', error);
        throw error;
    }
    finally {
        if (client)
            client.release();
    }
}
if (require.main === module) {
    seedDatabase()
        .then(() => {
        logger_1.default.info("Seed completed");
        process.exit(0);
    })
        .catch((err) => {
        console.error('Seed failed:', err);
        process.exit(1);
    });
}
//# sourceMappingURL=seed.js.map