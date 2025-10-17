"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.jobQueue = exports.documents = exports.agentStates = void 0;
const pg_core_1 = require("drizzle-orm/pg-core");
exports.agentStates = (0, pg_core_1.pgTable)('agent_states', {
    id: (0, pg_core_1.serial)('id').primaryKey(),
    agentName: (0, pg_core_1.text)('agent_name').notNull(),
    state: (0, pg_core_1.jsonb)('state'),
    createdAt: (0, pg_core_1.timestamp)('created_at').defaultNow(),
    updatedAt: (0, pg_core_1.timestamp)('updated_at').defaultNow(),
});
exports.documents = (0, pg_core_1.pgTable)('documents', {
    id: (0, pg_core_1.serial)('id').primaryKey(),
    content: (0, pg_core_1.text)('content'),
    metadata: (0, pg_core_1.jsonb)('metadata'),
    embedding: (0, pg_core_1.text)('embedding'), // Store as text for now, will be converted to vector type in Supabase
});
exports.jobQueue = (0, pg_core_1.pgTable)('job_queue', {
    id: (0, pg_core_1.serial)('id').primaryKey(),
    payload: (0, pg_core_1.jsonb)('payload').notNull(),
    targetAgent: (0, pg_core_1.text)('target_agent').notNull(),
    status: (0, pg_core_1.text)('status').notNull().default('pending'), // pending, processing, completed, failed
    attempts: (0, pg_core_1.integer)('attempts').notNull().default(0),
    createdAt: (0, pg_core_1.timestamp)('created_at').defaultNow(),
    processedAt: (0, pg_core_1.timestamp)('processed_at'),
});
//# sourceMappingURL=schema.js.map