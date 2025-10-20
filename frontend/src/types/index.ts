export interface Customer {
  id: string;
  name: string;
  email?: string;
  phone?: string;
  status: PipelineStatus;
  created_at: Date | string;
  updated_at: Date | string;
  notes?: string;
  next_action?: string;
  next_action_date?: Date | string;
  prospect_why?: string;
  country?: string;
  language?: string;
  source?: string;
}

export enum PipelineStatus {
  LEAD = 'Lead',
  RELATIONSHIP = 'Relationship', 
  INVITED = 'Invited',
  QUALIFIED = 'Qualified',
  PRESENTATION_SENT = 'Presentation Sent',
  FOLLOW_UP = 'Follow-up',
  SIGNED_UP = 'SIGNED-UP'
}

export interface Interaction {
  id: string;
  customer_id: string;
  type: InteractionType;
  content: string;
  created_at: Date | string;
  scheduled_for?: Date | string;
  completed: boolean;
  summary?: string;
  notes?: string;
  interaction_date?: Date | string;
}

export enum InteractionType {
  NOTE = 'note',
  CALL = 'call',
  EMAIL = 'email',
  MEETING = 'meeting',
  REMINDER = 'reminder'
}

export interface PipelineStats {
  [key: string]: number;
}

export interface Stats {
  countsByStatus: Record<string, number>;
  dmoCounters: {
    today: { invites: number; follow_ups: number; };
    week: { invites: number; follow_ups: number; };
  };
  extraCounts: {
    no_show_count: number;
    video_sent_count: number;
    overdue_followups: number;
  };
  customerDemographics: {
    byCountry: Record<string, number>;
    byLanguage: Record<string, number>;
    bySource: Record<string, number>;
  };
  interactionSummary: {
    byType: Record<string, number>;
    totalInteractions: number;
    avgInteractionsPerCustomer: number;
  };
  pipelineConversionRates: Record<string, number>;
}

export interface Reminder {
  id: string;
  customer_id: string;
  title?: string;
  description?: string;
  message?: string;
  type?: ReminderType | string;
  due_date?: Date | string;
  scheduled_for?: Date | string;
  completed: boolean;
  created_at: Date | string;
  updated_at: Date | string;
  repeat_interval?: string;
}

export interface EventLog {
  id: string;
  event_type: string;
  description: string;
  metadata?: Record<string, any>;
  created_at: Date | string;
  user_id?: string;
  customer_id?: string;
}



export interface AIDecisionLog {
  id: number;
  decision_type: string;
  input_data: Record<string, any>;
  output_decision: Record<string, any>;
  confidence_score: number;
  status: string;
  human_reviewer?: string;
  created_at: Date | string;
  updated_at: Date | string;
  agent_name?: string;
  agent_id?: string;
  decision_description?: string;
  action_taken?: string;
  metadata?: Record<string, any>;
}



export enum ReminderType {
  FOLLOW_UP = 'follow_up',
  CALL = 'call',
  EMAIL = 'email',
  MEETING = 'meeting',
  TASK = 'task',
  OTHER = 'other'
}

export interface AnalyticsEventRecord {
  id: string;
  event_name: string;
  event_type: string;
  occurred_at: string;
  ingested_at: string;
  customer_id?: string;
  source?: string;
}

export interface AnalyticsSummary {
  events: {
    total: number;
    byType: { eventType: string; count: number }[];
    trend: { date: string; count: number }[];
  };
  recommendations: {
    total: number;
    byAgent: { agentName: string; count: number }[];
    topTypes: { recommendationType: string; count: number; averagePriority: number | null }[];
    averageScoreByAgent: { agentName: string; averageScore: number | null }[];
  };
  pipeline: {
    byStatus: { status: string; count: number }[];
  };
}

export interface FeatureFlagEvaluation {
  flag: {
    key: string;
    description?: string;
    enabled: boolean;
    rollout_phase?: string;
    rollout_percentage?: number;
  };
  enabledForContext: boolean;
}

