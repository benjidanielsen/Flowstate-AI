"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.AutomationService = void 0;
const reminderService_1 = require("./reminderService");
const types_1 = require("../types");
class AutomationService {
    constructor() {
        this.reminderService = new reminderService_1.ReminderService();
    }
    async handleEvent(event) {
        const name = event.event_name;
        const customerId = event.customer_id;
        if (!customerId)
            return; // cannot attach reminders without customer
        const now = new Date();
        const inHours = (h) => new Date(now.getTime() + h * 3600 * 1000);
        const inDays = (d) => new Date(now.getTime() + d * 24 * 3600 * 1000);
        switch (name) {
            case 'VIDEO_SENT':
                await this.reminderService.createReminder({ customer_id: customerId, type: types_1.ReminderType.FOLLOW_UP_24H, message: 'Follow up after video sent (24h)', scheduled_for: inHours(24) });
                await this.reminderService.createReminder({ customer_id: customerId, type: types_1.ReminderType.FOLLOW_UP_48H, message: 'Follow up after video sent (48h)', scheduled_for: inHours(48) });
                break;
            case 'NO_SHOW':
                await this.reminderService.createReminder({ customer_id: customerId, type: types_1.ReminderType.FOLLOW_UP_2H, message: 'Follow up after no-show (2h)', scheduled_for: inHours(2) });
                await this.reminderService.createReminder({ customer_id: customerId, type: types_1.ReminderType.FOLLOW_UP_1D, message: 'Follow up after no-show (1d)', scheduled_for: inDays(1) });
                break;
            default:
                break;
        }
    }
}
exports.AutomationService = AutomationService;
//# sourceMappingURL=automationService.js.map