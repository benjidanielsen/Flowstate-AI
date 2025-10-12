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
  title: string;
  description?: string;
  due_date: Date | string;
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

