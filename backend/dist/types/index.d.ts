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
    handle_ig?: string;
    handle_whatsapp?: string;
    country?: string;
    language?: string;
    consent_json?: any;
    utm_json?: any;
}
export declare enum PipelineStatus {
    LEAD = "Lead",
    RELATIONSHIP = "Relationship",
    INVITED = "Invited",
    QUALIFIED = "Qualified",
    PRESENTATION_SENT = "Presentation Sent",
    FOLLOW_UP = "Follow-up",
    SIGNED_UP = "SIGNED-UP"
}
export interface Interaction {
    id: string;
    customer_id: string;
    type: InteractionType;
    content: string;
    created_at: Date;
    scheduled_for?: Date;
    completed: boolean;
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
}
export declare enum ReminderType {
    FOLLOW_UP_24H = "follow_up_24h",
    FOLLOW_UP_48H = "follow_up_48h",
    FOLLOW_UP_2H = "follow_up_2h",
    FOLLOW_UP_1D = "follow_up_1d",
    FOLLOW_UP_7D = "follow_up_7d"
}
export interface EventLog {
    id: string;
    customer_id?: string;
    event_type: string;
    event_data: any;
    timestamp: Date;
    user_id?: string;
}
//# sourceMappingURL=index.d.ts.map