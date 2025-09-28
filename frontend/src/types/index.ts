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