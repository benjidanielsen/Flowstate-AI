import DatabaseManager from '../database';
import { PipelineStatus } from '../types';
import { aggregateCountsByVocabulary, PipelineVocabulary } from './pipelineMapping';

export class StatsService {
  async countsByStatus(): Promise<Record<string, number>> {
    const db = DatabaseManager.getInstance().getDb();
    const statuses = Object.values(PipelineStatus);
    const result: Record<string, number> = {};
    await Promise.all(statuses.map(s => new Promise<void>((resolve, reject) => {
      db.get('SELECT COUNT(*) as c FROM customers WHERE status = ?', [s], (err, row: any) => {
        if (err) return reject(err);
        result[s] = row.c || 0;
        resolve();
      });
    })));
    return result;
  }

  async countsByPipeline(vocab: PipelineVocabulary) {
    const canonical = await this.countsByStatus();
    return aggregateCountsByVocabulary(canonical, vocab);
  }

  private dateRange(_daySpan: number) {
    const now = new Date();
    const start = new Date();
    start.setHours(0,0,0,0);
    const weekStart = new Date(now);
    weekStart.setDate(now.getDate() - 6);
    weekStart.setHours(0,0,0,0);
    return { todayStart: start, weekStart };
  }

  async dmoCounters() {
    const db = DatabaseManager.getInstance().getDb();
    const { todayStart, weekStart } = this.dateRange(7);
    function countEvent(name: string, from: Date): Promise<number> {
      return new Promise((resolve, reject) => {
        db.get(
          'SELECT COUNT(*) as c FROM event_logs WHERE event_type = ? AND timestamp >= ?',
          [name, from.toISOString()],
          (err, row: any) => err ? reject(err) : resolve(row.c || 0)
        );
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
    const db = DatabaseManager.getInstance().getDb();
    const nowIso = new Date().toISOString();
    const noShow = await new Promise<number>((resolve, reject) => {
      db.get('SELECT COUNT(*) as c FROM event_logs WHERE event_type = ?', ['NO_SHOW'], (e, r: any) => e?reject(e):resolve(r.c||0));
    });
    const videoSent = await new Promise<number>((resolve, reject) => {
      db.get('SELECT COUNT(*) as c FROM event_logs WHERE event_type = ?', ['VIDEO_SENT'], (e, r: any) => e?reject(e):resolve(r.c||0));
    });
    const overdueFollowups = await new Promise<number>((resolve, reject) => {
      db.get('SELECT COUNT(*) as c FROM reminders WHERE completed = 0 AND scheduled_for < ?', [nowIso], (e, r: any) => e?reject(e):resolve(r.c||0));
    });
    return { no_show_count: noShow, video_sent_count: videoSent, overdue_followups: overdueFollowups };
  }
}
