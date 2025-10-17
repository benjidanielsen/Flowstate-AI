import { Reminder, ReminderType } from '../types';
export declare class ReminderService {
    createReminder(data: {
        customer_id: string;
        type: ReminderType;
        message: string;
        scheduled_for: Date;
        repeat_interval?: string;
    }): Promise<Reminder>;
    getDueReminders(): Promise<Reminder[]>;
    markReminderCompleted(id: string): Promise<Reminder | null>;
    getRemindersByCustomerId(customerId: string): Promise<Reminder[]>;
    getAllReminders(): Promise<Reminder[]>;
    updateReminder(id: string, data: {
        type?: ReminderType;
        message?: string;
        scheduled_for?: Date;
        completed?: boolean;
        repeat_interval?: string;
    }): Promise<Reminder | null>;
    deleteReminder(id: string): Promise<boolean>;
    getReminderById(id: string): Promise<Reminder | null>;
}
//# sourceMappingURL=reminderService.d.ts.map