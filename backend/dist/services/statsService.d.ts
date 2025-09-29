export declare class StatsService {
    countsByStatus(): Promise<Record<string, number>>;
    private dateRange;
    dmoCounters(): Promise<{
        today: {
            invites: number;
            follow_ups: number;
        };
        week: {
            invites: number;
            follow_ups: number;
        };
    }>;
    extraCounts(): Promise<{
        no_show_count: number;
        video_sent_count: number;
        overdue_followups: number;
    }>;
}
//# sourceMappingURL=statsService.d.ts.map