export interface FollowUp {
    id: string;
    customer_id: string;
    agent_name: string;
    due_date: Date;
    status: 'pending' | 'completed' | 'skipped';
    notes?: string;
    created_at: Date;
    updated_at: Date;
}
export declare class FollowUpService {
    private followUpTimes;
    createFollowUp(customerId: string, stage: string, agentName: string): Promise<FollowUp>;
    private getFollowUpMessage;
    autoScheduleFollowUps(): Promise<number>;
    getUpcomingFollowUps(days?: number): Promise<FollowUp[]>;
    getFollowUpById(id: string): Promise<FollowUp | null>;
    getFollowUpsByCustomerId(customerId: string): Promise<FollowUp[]>;
    updateFollowUpStatus(id: string, status: 'completed' | 'skipped'): Promise<FollowUp | null>;
    getPendingFollowUps(): Promise<FollowUp[]>;
    deleteFollowUp(id: string): Promise<boolean>;
}
export declare const followUpService: FollowUpService;
//# sourceMappingURL=followUpService.d.ts.map