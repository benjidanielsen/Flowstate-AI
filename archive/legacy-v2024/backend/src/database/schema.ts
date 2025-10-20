import { pgTable, serial, text, jsonb, timestamp, integer } from 'drizzle-orm/pg-core';

export const agentStates = pgTable('agent_states', {
  id: serial('id').primaryKey(),
  agentName: text('agent_name').notNull(),
  state: jsonb('state'),
  createdAt: timestamp('created_at').defaultNow(),
  updatedAt: timestamp('updated_at').defaultNow(),
});

export const documents = pgTable('documents', {
  id: serial('id').primaryKey(),
  content: text('content'),
  metadata: jsonb('metadata'),
  embedding: text('embedding'), // Store as text for now, will be converted to vector type in Supabase
});

export const jobQueue = pgTable('job_queue', {
  id: serial('id').primaryKey(),
  payload: jsonb('payload').notNull(),
  targetAgent: text('target_agent').notNull(),
  status: text('status').notNull().default('pending'), // pending, processing, completed, failed
  attempts: integer('attempts').notNull().default(0),
  createdAt: timestamp('created_at').defaultNow(),
  processedAt: timestamp('processed_at'),
});

