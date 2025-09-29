export declare class ReminderService {
    createReminder(data: {
        customer_id: string;
        type: string;
        message?: string;
        scheduled_for: Date;
    }): Promise<unknown>;
    getDueReminders(): Promise<unknown>;
    completeReminder(id: string): Promise<unknown>;
}
//# sourceMappingURL=reminderService.d.ts.map