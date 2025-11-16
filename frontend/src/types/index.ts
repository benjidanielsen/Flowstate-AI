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

export interface TrendPoint {
  label: string;
  value: number;
}

export interface KPIMetric {
  id: string;
  name: string;
  value: number;
  unit?: string;
  change?: number;
  direction?: 'up' | 'down' | 'flat';
  description?: string;
  target?: number;
  status?: 'success' | 'warning' | 'danger';
}

export interface KpiDashboardPayload {
  category: string;
  metrics: KPIMetric[];
  trend: TrendPoint[];
  summary?: {
    total: number;
    delta: number;
  };
}

export interface EvolutionMetrics {
  totalEvents: number;
  pendingImprovements: number;
  appliedImprovements: number;
  successRate: number;
  averageConfidence: number;
  safeModeActive: boolean;
  lastEvolution: string;
}

export interface EvolutionAnomaly {
  metricName: string;
  latestValue: number;
  mean: number;
  zScore: number;
  severity: 'low' | 'medium' | 'high' | 'critical';
  timestamp: string;
}

export interface EvolutionPerformance {
  nbaSuccessRate: number;
  reminderSuccessRate: number;
  avgResponseTime: number;
}

export interface ActivityLog {
  id: string;
  agentName: string;
  action: string;
  createdAt: string;
  sentiment?: 'positive' | 'neutral' | 'negative';
  details?: string;
}

export interface EvolutionDashboardPayload {
  metrics: EvolutionMetrics;
  anomalies: EvolutionAnomaly[];
  performance: EvolutionPerformance;
  activity: ActivityLog[];
}

export interface AgentProfile {
  id: string;
  name: string;
  role: string;
  status: 'online' | 'offline' | 'busy';
  tasksInFlight: number;
  lastActive: string;
  specialty?: string;
  avatarColor?: string;
}

export interface AdminTask {
  id: string;
  title: string;
  owner: string;
  dueDate: string;
  status: 'todo' | 'in_progress' | 'blocked' | 'done';
  priority: 'low' | 'medium' | 'high';
  relatedCustomer?: string;
}

