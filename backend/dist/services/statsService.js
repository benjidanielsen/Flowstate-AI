"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.StatsService = void 0;
const database_1 = __importDefault(require("../database"));
const types_1 = require("../types");
class StatsService {
    async countsByStatus() {
        const db = database_1.default.getInstance().getDb();
        const statuses = Object.values(types_1.PipelineStatus);
        const result = {};
        await Promise.all(statuses.map(s => new Promise((resolve, reject) => {
            db.get('SELECT COUNT(*) as c FROM customers WHERE status = ?', [s], (err, row) => {
                if (err)
                    return reject(err);
                result[s] = row.c || 0;
                resolve();
            });
        })));
        return result;
    }
    dateRange(_daySpan) {
        const now = new Date();
        const start = new Date();
        start.setHours(0, 0, 0, 0);
        const weekStart = new Date(now);
        weekStart.setDate(now.getDate() - 6);
        weekStart.setHours(0, 0, 0, 0);
        return { todayStart: start, weekStart };
    }
    async dmoCounters() {
        const db = database_1.default.getInstance().getDb();
        const { todayStart, weekStart } = this.dateRange(7);
        function countEvent(name, from) {
            return new Promise((resolve, reject) => {
                db.get('SELECT COUNT(*) as c FROM event_logs WHERE event_type = ? AND timestamp >= ?', [name, from.toISOString()], (err, row) => err ? reject(err) : resolve(row.c || 0));
            });
        }
        const [invitesToday, invitesWeek, followToday, followWeek] = await Promise.all([
            countEvent('INVITE_SENT', todayStart),
            countEvent('INVITE_SENT', weekStart),
            countEvent('FOLLOW_UP_DONE', todayStart),
            countEvent('FOLLOW_UP_DONE', weekStart),
        ]);
        return {
            today: { invites: invitesToday, follow_ups: followToday },
            week: { invites: invitesWeek, follow_ups: followWeek },
        };
    }
    async extraCounts() {
        const db = database_1.default.getInstance().getDb();
        const nowIso = new Date().toISOString();
        const noShow = await new Promise((resolve, reject) => {
            db.get('SELECT COUNT(*) as c FROM event_logs WHERE event_type = ?', ['NO_SHOW'], (e, r) => e ? reject(e) : resolve(r.c || 0));
        });
        const videoSent = await new Promise((resolve, reject) => {
            db.get('SELECT COUNT(*) as c FROM event_logs WHERE event_type = ?', ['VIDEO_SENT'], (e, r) => e ? reject(e) : resolve(r.c || 0));
        });
        const overdueFollowups = await new Promise((resolve, reject) => {
            db.get('SELECT COUNT(*) as c FROM reminders WHERE completed = 0 AND scheduled_for < ?', [nowIso], (e, r) => e ? reject(e) : resolve(r.c || 0));
        });
        return { no_show_count: noShow, video_sent_count: videoSent, overdue_followups: overdueFollowups };
    }
}
exports.StatsService = StatsService;
//# sourceMappingURL=statsService.js.map