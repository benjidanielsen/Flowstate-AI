"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.StatsService = void 0;
const database_1 = __importDefault(require("../database"));
const types_1 = require("../types");
class StatsService {
    constructor() {
        this.cache = {};
        this.cacheDuration = 5 * 60 * 1000; // 5 minutes in milliseconds
    }
    getCached(key) {
        const entry = this.cache[key];
        if (entry && (Date.now() - entry.timestamp < this.cacheDuration)) {
            return entry.data;
        }
        return null;
    }
    setCache(key, data) {
        this.cache[key] = { data, timestamp: Date.now() };
    }
    async countsByStatus() {
        const cacheKey = 'countsByStatus';
        const cachedData = this.getCached(cacheKey);
        if (cachedData) {
            return cachedData;
        }
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
        this.setCache(cacheKey, result);
        return result;
    }
    dateRange() {
        const now = new Date();
        const start = new Date();
        start.setHours(0, 0, 0, 0);
        const weekStart = new Date(now);
        weekStart.setDate(now.getDate() - 6);
        weekStart.setHours(0, 0, 0, 0);
        return { todayStart: start, weekStart };
    }
    async dmoCounters() {
        const cacheKey = 'dmoCounters';
        const cachedData = this.getCached(cacheKey);
        if (cachedData) {
            return cachedData;
        }
        const db = database_1.default.getInstance().getDb();
        const { todayStart, weekStart } = this.dateRange();
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
        const result = {
            today: { invites: invitesToday, follow_ups: followToday },
            week: { invites: invitesWeek, follow_ups: followWeek },
        };
        this.setCache(cacheKey, result);
        return result;
    }
    async extraCounts() {
        const cacheKey = 'extraCounts';
        const cachedData = this.getCached(cacheKey);
        if (cachedData) {
            return cachedData;
        }
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
        const result = { no_show_count: noShow, video_sent_count: videoSent, overdue_followups: overdueFollowups };
        this.setCache(cacheKey, result);
        return result;
    }
    async getCustomerDemographics() {
        const cacheKey = 'customerDemographics';
        const cachedData = this.getCached(cacheKey);
        if (cachedData) {
            return cachedData;
        }
        const db = database_1.default.getInstance().getDb();
        const [byCountry, byLanguage, bySource] = await Promise.all([
            new Promise((resolve, reject) => {
                db.all('SELECT country, COUNT(*) as count FROM customers WHERE country IS NOT NULL GROUP BY country', (err, rows) => {
                    if (err)
                        return reject(err);
                    resolve(rows.reduce((acc, row) => ({ ...acc, [row.country]: row.count }), {}));
                });
            }),
            new Promise((resolve, reject) => {
                db.all('SELECT language, COUNT(*) as count FROM customers WHERE language IS NOT NULL GROUP BY language', (err, rows) => {
                    if (err)
                        return reject(err);
                    resolve(rows.reduce((acc, row) => ({ ...acc, [row.language]: row.count }), {}));
                });
            }),
            new Promise((resolve, reject) => {
                db.all('SELECT source, COUNT(*) as count FROM customers WHERE source IS NOT NULL GROUP BY source', (err, rows) => {
                    if (err)
                        return reject(err);
                    resolve(rows.reduce((acc, row) => ({ ...acc, [row.source]: row.count }), {}));
                });
            }),
        ]);
        const result = { byCountry, byLanguage, bySource };
        this.setCache(cacheKey, result);
        return result;
    }
    async getInteractionSummary() {
        const cacheKey = 'interactionSummary';
        const cachedData = this.getCached(cacheKey);
        if (cachedData) {
            return cachedData;
        }
        const db = database_1.default.getInstance().getDb();
        const [byType, totalInteractionsResult, totalCustomersResult] = await Promise.all([
            new Promise((resolve, reject) => {
                db.all('SELECT type, COUNT(*) as count FROM interactions GROUP BY type', (err, rows) => {
                    if (err)
                        return reject(err);
                    resolve(rows.reduce((acc, row) => ({ ...acc, [row.type]: row.count }), {}));
                });
            }),
            new Promise((resolve, reject) => {
                db.get('SELECT COUNT(*) as count FROM interactions', (err, row) => {
                    if (err)
                        return reject(err);
                    resolve(row.count || 0);
                });
            }),
            new Promise((resolve, reject) => {
                db.get('SELECT COUNT(*) as count FROM customers', (err, row) => {
                    if (err)
                        return reject(err);
                    resolve(row.count || 0);
                });
            }),
        ]);
        const totalInteractions = totalInteractionsResult;
        const totalCustomers = totalCustomersResult;
        const avgInteractionsPerCustomer = totalCustomers > 0 ? totalInteractions / totalCustomers : 0;
        const result = { byType, totalInteractions, avgInteractionsPerCustomer };
        this.setCache(cacheKey, result);
        return result;
    }
    async getPipelineConversionRates() {
        const cacheKey = 'pipelineConversionRates';
        const cachedData = this.getCached(cacheKey);
        if (cachedData) {
            return cachedData;
        }
        const db = database_1.default.getInstance().getDb();
        const pipelineStatuses = Object.values(types_1.PipelineStatus);
        const conversionRates = {};
        for (let i = 0; i < pipelineStatuses.length - 1; i++) {
            const currentStage = pipelineStatuses[i];
            const nextStage = pipelineStatuses[i + 1];
            const currentStageCount = await new Promise((resolve, reject) => {
                db.get('SELECT COUNT(*) as count FROM customers WHERE status = ?', [currentStage], (err, row) => {
                    if (err)
                        return reject(err);
                    resolve(row.count || 0);
                });
            });
            const nextStageCount = await new Promise((resolve, reject) => {
                db.get('SELECT COUNT(*) as count FROM customers WHERE status = ?', [nextStage], (err, row) => {
                    if (err)
                        return reject(err);
                    resolve(row.count || 0);
                });
            });
            if (currentStageCount > 0) {
                conversionRates[`${currentStage}_to_${nextStage}`] = (nextStageCount / currentStageCount) * 100;
            }
            else {
                conversionRates[`${currentStage}_to_${nextStage}`] = 0;
            }
        }
        this.setCache(cacheKey, conversionRates);
        return conversionRates;
    }
}
exports.StatsService = StatsService;
//# sourceMappingURL=statsService.js.map