export interface AgentState {
    name: string;
    status: string;
    last_heartbeat: Date;
    metadata: any;
}
export declare enum JobStatus {
    PENDING = "pending",
    PROCESSING = "processing",
    COMPLETED = "completed",
    FAILED = "failed"
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
    embedding?: number[];
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
    prospect_why?: string;
    handle_ig?: string;
    handle_whatsapp?: string;
    country?: string;
    language?: string;
    consent_json?: any;
    utm_json?: any;
}
export declare enum PipelineStatus {
    NEW_LEAD = "New Lead",
    WARMING_UP = "Warming Up",
    INVITED = "Invited",
    QUALIFIED = "Qualified",
    PRESENTATION_SENT = "Presentation Sent",
    FOLLOW_UP = "Follow-up",
    CLOSED_WON = "Closed - Won",
    NOT_NOW = "Not Now",
    LONG_TERM_NURTURE = "Long-term Nurture"
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
export declare enum InteractionType {
    NOTE = "note",
    CALL = "call",
    EMAIL = "email",
    MEETING = "meeting",
    REMINDER = "reminder"
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
    repeat_interval?: string;
}
export declare enum ReminderType {
    FOLLOW_UP_24H = "follow_up_24h",
    FOLLOW_UP_48H = "follow_up_48h",
    FOLLOW_UP_2H = "follow_up_2h",
    FOLLOW_UP_1D = "follow_up_1d",
    FOLLOW_UP_7D = "follow_up_7d",
    FOLLOW_UP = "follow_up"
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
    type: string;
    config: any;
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
    users: User;
    external_integrations: ExternalIntegration;
    kpis: KPI;
}
//# sourceMappingURL=index.d.ts.map