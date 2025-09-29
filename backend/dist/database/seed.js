"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.seedDatabase = seedDatabase;
const index_1 = __importDefault(require("./index"));
const uuid_1 = require("uuid");
const types_1 = require("../types");
const sampleCustomers = [
    {
        id: (0, uuid_1.v4)(),
        name: 'John Smith',
        email: 'john@example.com',
        phone: '+1-555-0123',
        status: types_1.PipelineStatus.LEAD,
        notes: 'Met at networking event. Interested in fitness products.',
        next_action: 'Schedule initial call',
        next_action_date: new Date(Date.now() + 24 * 60 * 60 * 1000) // Tomorrow
    },
    {
        id: (0, uuid_1.v4)(),
        name: 'Sarah Johnson',
        email: 'sarah@example.com',
        phone: '+1-555-0124',
        status: types_1.PipelineStatus.RELATIONSHIP,
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
    const dbManager = index_1.default.getInstance();
    const db = await dbManager.connect();
    console.log('Starting database seed...');
    return new Promise((resolve, reject) => {
        // Clear existing data
        db.run('DELETE FROM interactions', (err) => {
            if (err) {
                reject(err);
                return;
            }
            db.run('DELETE FROM reminders', (err) => {
                if (err) {
                    reject(err);
                    return;
                }
                db.run('DELETE FROM event_logs', (err) => {
                    if (err) {
                        reject(err);
                        return;
                    }
                    db.run('DELETE FROM customers', (err) => {
                        if (err) {
                            reject(err);
                            return;
                        }
                        // Insert sample customers
                        let completed = 0;
                        sampleCustomers.forEach(customer => {
                            const stmt = db.prepare(`
                INSERT INTO customers (id, name, email, phone, status, notes, next_action, next_action_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
              `);
                            stmt.run([
                                customer.id,
                                customer.name,
                                customer.email,
                                customer.phone,
                                customer.status,
                                customer.notes,
                                customer.next_action,
                                customer.next_action_date.toISOString()
                            ], (err) => {
                                if (err) {
                                    reject(err);
                                    return;
                                }
                                // Add sample interactions
                                const interactionStmt = db.prepare(`
                  INSERT INTO interactions (id, customer_id, type, content, created_at)
                  VALUES (?, ?, ?, ?, ?)
                `);
                                interactionStmt.run([
                                    (0, uuid_1.v4)(),
                                    customer.id,
                                    types_1.InteractionType.NOTE,
                                    `Initial contact with ${customer.name}`,
                                    new Date().toISOString()
                                ], (err) => {
                                    if (err) {
                                        reject(err);
                                        return;
                                    }
                                    // Add sample event log
                                    const eventStmt = db.prepare(`
                    INSERT INTO event_logs (id, customer_id, event_type, event_data, timestamp)
                    VALUES (?, ?, ?, ?, ?)
                  `);
                                    eventStmt.run([
                                        (0, uuid_1.v4)(),
                                        customer.id,
                                        'customer_created',
                                        JSON.stringify({ name: customer.name, status: customer.status }),
                                        new Date().toISOString()
                                    ], (err) => {
                                        if (err) {
                                            reject(err);
                                            return;
                                        }
                                        completed++;
                                        if (completed === sampleCustomers.length) {
                                            console.log('Database seed completed successfully');
                                            resolve();
                                        }
                                    });
                                    eventStmt.finalize();
                                });
                                interactionStmt.finalize();
                            });
                            stmt.finalize();
                        });
                    });
                });
            });
        });
    });
}
if (require.main === module) {
    seedDatabase()
        .then(() => {
        console.log('Seed completed');
        process.exit(0);
    })
        .catch((err) => {
        console.error('Seed failed:', err);
        process.exit(1);
    });
}
//# sourceMappingURL=seed.js.map