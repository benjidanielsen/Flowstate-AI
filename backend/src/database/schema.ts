import { pgTable, serial, text, jsonb, timestamp, integer, boolean, doublePrecision } from 'drizzle-orm/pg-core';

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

export const analyticsEvents = pgTable('analytics_events', {
  id: text('id').primaryKey(),
  eventName: text('event_name').notNull(),
  eventType: text('event_type').notNull(),
  customerId: text('customer_id'),
  accountId: text('account_id'),
  userId: text('user_id'),
  source: text('source'),
  payload: jsonb('payload'),
  metadata: jsonb('metadata'),
  occurredAt: timestamp('occurred_at', { withTimezone: true }).defaultNow(),
  ingestedAt: timestamp('ingested_at', { withTimezone: true }).defaultNow(),
  correlationId: text('correlation_id'),
  recommendationId: text('recommendation_id'),
});

export const recommendationLogs = pgTable('recommendation_logs', {
  id: text('id').primaryKey(),
  recommendationId: text('recommendation_id').notNull(),
  agentName: text('agent_name'),
  customerId: text('customer_id'),
  accountId: text('account_id'),
  recommendationType: text('recommendation_type'),
  priority: integer('priority'),
  score: doublePrecision('score'),
  context: jsonb('context'),
  metadata: jsonb('metadata'),
  generatedAt: timestamp('generated_at', { withTimezone: true }).defaultNow(),
  accepted: boolean('accepted').default(false),
  actionTakenAt: timestamp('action_taken_at', { withTimezone: true }),
  outcome: text('outcome'),
  feedback: jsonb('feedback'),
});

export const featureFlags = pgTable('feature_flags', {
  key: text('key').primaryKey(),
  description: text('description'),
  rolloutPhase: text('rollout_phase').default('beta'),
  enabled: boolean('enabled').default(false).notNull(),
  rolloutPercentage: integer('rollout_percentage').default(0),
  metadata: jsonb('metadata'),
  createdAt: timestamp('created_at', { withTimezone: true }).defaultNow(),
  updatedAt: timestamp('updated_at', { withTimezone: true }).defaultNow(),
});

