import { Reminder } from '../types';
export declare class FollowUpService {
    private followUpTimes;
    createFollowUp(customerId: string, stage: string): Promise<Reminder>;
    private getFollowUpMessage;
    autoScheduleFollowUps(): Promise<number>;
    getUpcomingFollowUps(days?: number): Promise<any[]>;
}
export declare const followUpService: FollowUpService;
//# sourceMappingURL=followUpService.d.ts.map