import { EventLog } from '../types';
export declare class EventLogService {
    logEvent(eventType: string, eventData: any, customerId?: string, userId?: string): Promise<EventLog>;
    getEventsByCustomer(customerId: string, limit?: number): Promise<EventLog[]>;
    getAllEvents(limit?: number): Promise<EventLog[]>;
    getEventsByType(eventType: string, limit?: number): Promise<EventLog[]>;
}
//# sourceMappingURL=eventLogService.d.ts.map