export interface AgentState {
  name: string;
  status: string;
  last_heartbeat: Date;
  metadata: any;
}

export enum JobStatus {
  PENDING = 'pending',
  PROCESSING = 'processing',
  COMPLETED = 'completed',
  FAILED = 'failed',
}

export interface Job {
  id: string;
  agent_name: string;
  task_type: string;
  payload: any;
  status: JobStatus;
  priority: number;
  correlation_id: string;
  created_at: Date;
  updated_at: Date;
  result?: any;
}

export interface Document {
  id: string;
  agent_name: string;
  type: string;
  content: string;
  metadata: any;
  tags: string[];
  importance: number;
  embedding?: number[]; // Vector embedding for semantic search
  created_at: Date;
  updated_at: Date;
}

export interface Qualification {
  id: string;
  customer_id: string;
  question: string;
  expected_answer: string;
  status: 'pending' | 'completed' | 'failed';
  agent_name?: string;
  created_at: Date;
  updated_at: Date;
}

export interface QualificationAnswer {
  id: string;
  qualification_id: string;
  answer: string;
  is_correct: boolean;
  agent_name?: string;
  created_at: Date;
  updated_at: Date;
}

export interface Customer {
  id: string;
  name: string;
  email?: string;
  phone?: string;
  status: PipelineStatus;
  created_at: Date;
  updated_at: Date;
  notes?: string;
  next_action?: string;
  next_action_date?: Date;
  source?: string;
  prospect_why?: string; // Frazer Method: Mandatory for Qualified stage
  handle_ig?: string;
  handle_whatsapp?: string;
  country?: string;
  language?: string;
  consent_json?: any;
  utm_json?: any;
}

export enum PipelineStatus {
  NEW_LEAD = 'New Lead',
  WARMING_UP = 'Warming Up',
  INVITED = 'Invited',
  QUALIFIED = 'Qualified',
  PRESENTATION_SENT = 'Presentation Sent',
  FOLLOW_UP = 'Follow-up',
  CLOSED_WON = 'Closed - Won',
  NOT_NOW = 'Not Now',
  LONG_TERM_NURTURE = 'Long-term Nurture'
}

export interface Interaction {
  id: string;
  customer_id: string;
  type: InteractionType;
  summary: string;
  notes?: string;
  interaction_date: Date;
  created_at: Date;
  updated_at: Date;
}

export enum InteractionType {
  NOTE = 'note',
  CALL = 'call',
  EMAIL = 'email',
  MEETING = 'meeting',
  REMINDER = 'reminder'
}

export interface Reminder {
  id: string;
  customer_id: string;
  type: ReminderType;
  message: string;
  scheduled_for: Date;
  completed: boolean;
  created_at: Date;
  updated_at: Date;
  repeat_interval?: string; // e.g., "daily", "weekly", "monthly"
}

export enum ReminderType {
  FOLLOW_UP_24H = 'follow_up_24h',
  FOLLOW_UP_48H = 'follow_up_48h',
  FOLLOW_UP_2H = 'follow_up_2h',
  FOLLOW_UP_1D = 'follow_up_1d',
  FOLLOW_UP_7D = 'follow_up_7d',
  FOLLOW_UP = 'follow_up'
}

export interface EventLog {
  id: string;
  customer_id?: string;
  event_type: string;
  event_data: any;
  timestamp: Date;
  user_id?: string;
}

export interface User {
  id: string;
  username: string;
  created_at: Date;
  updated_at: Date;
}

export interface ExternalIntegration {
  id: string;
  customer_id: string;
  type: string; // e.g., "google_calendar", "outlook_calendar", "slack"
  config: any; // JSON object for integration-specific configuration
  created_at: Date;
  updated_at: Date;
}

export interface KPI {
  name: string;
  value: number;
  unit: string;
  change: number;
  changeType: 'increase' | 'decrease' | 'neutral';
  description: string;
  status: 'success' | 'warning' | 'danger';
  category: string;
}

export interface Database {
  customers: Customer;
  interactions: Interaction;
  reminders: Reminder;
  event_logs: EventLog;
  analytics_events: AnalyticsEvent;
  recommendation_logs: RecommendationLog;
  feature_flags: FeatureFlag;
  users: User;
  external_integrations: ExternalIntegration;
  kpis: KPI;
}

export interface AnalyticsEvent {
  id: string;
  event_name: string;
  event_type: string;
  customer_id?: string | null;
  account_id?: string | null;
  user_id?: string | null;
  source?: string | null;
  payload?: Record<string, any> | null;
  metadata?: Record<string, any> | null;
  occurred_at: Date;
  ingested_at: Date;
  correlation_id?: string | null;
  recommendation_id?: string | null;
}

export interface RecommendationLog {
  id: string;
  recommendation_id: string;
  agent_name?: string | null;
  customer_id?: string | null;
  account_id?: string | null;
  recommendation_type?: string | null;
  priority?: number | null;
  score?: number | null;
  context?: Record<string, any> | null;
  metadata?: Record<string, any> | null;
  generated_at: Date;
  accepted?: boolean | null;
  action_taken_at?: Date | null;
  outcome?: string | null;
  feedback?: Record<string, any> | null;
}

export interface FeatureFlag {
  key: string;
  description?: string | null;
  rollout_phase?: string | null;
  enabled: boolean;
  rollout_percentage?: number | null;
  metadata?: Record<string, any> | null;
  created_at: Date;
  updated_at: Date;
}

