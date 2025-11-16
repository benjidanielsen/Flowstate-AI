import { InteractionType, PipelineStatus, ReminderType } from '../types';

export interface FrazerStageDefinition {
  status: PipelineStatus;
  frazerStep: 'Talk' | 'Invite' | 'Show' | 'Keep Talking' | 'Enroll';
  cadenceHours: number;
  reminderType: ReminderType;
  aiSignals: string[];
  touchpoint: {
    type: InteractionType;
    summary: string;
    notesHint: string;
  };
}

const DEFAULT_STAGE_DEFINITION: FrazerStageDefinition = {
  status: PipelineStatus.NEW_LEAD,
  frazerStep: 'Talk',
  cadenceHours: 24,
  reminderType: ReminderType.FOLLOW_UP,
  aiSignals: ['speed_of_follow_up'],
  touchpoint: {
    type: InteractionType.NOTE,
    summary: 'Log first touchpoint',
    notesHint: 'Capture tone + context for first contact'
  }
};

export const FRAZER_STAGE_DEFINITIONS: FrazerStageDefinition[] = [
  {
    status: PipelineStatus.NEW_LEAD,
    frazerStep: 'Talk',
    cadenceHours: 24,
    reminderType: ReminderType.FOLLOW_UP_24H,
    aiSignals: ['speed_of_follow_up', 'lead_source_quality'],
    touchpoint: {
      type: InteractionType.CALL,
      summary: 'Talk → Acknowledge new lead',
      notesHint: 'Confirm how you met, mirror their energy, log objections'
    }
  },
  {
    status: PipelineStatus.WARMING_UP,
    frazerStep: 'Invite',
    cadenceHours: 36,
    reminderType: ReminderType.FOLLOW_UP_2H,
    aiSignals: ['micro_commitments', 'rapport_strength'],
    touchpoint: {
      type: InteractionType.NOTE,
      summary: 'Warming Up → Seed the invitation',
      notesHint: 'Share a quick win, confirm interest, document their WHY'
    }
  },
  {
    status: PipelineStatus.INVITED,
    frazerStep: 'Invite',
    cadenceHours: 48,
    reminderType: ReminderType.FOLLOW_UP_48H,
    aiSignals: ['invite_sent', 'accepted_invite'],
    touchpoint: {
      type: InteractionType.EMAIL,
      summary: 'Invite → Confirm event/video details',
      notesHint: 'Send link, reconfirm time, handle friction proactively'
    }
  },
  {
    status: PipelineStatus.QUALIFIED,
    frazerStep: 'Show',
    cadenceHours: 72,
    reminderType: ReminderType.FOLLOW_UP_1D,
    aiSignals: ['prospect_why', 'qualification_score'],
    touchpoint: {
      type: InteractionType.MEETING,
      summary: 'Qualified → Share proof / presentation invite',
      notesHint: 'Capture their WHY + outcome, confirm attendance'
    }
  },
  {
    status: PipelineStatus.PRESENTATION_SENT,
    frazerStep: 'Show',
    cadenceHours: 72,
    reminderType: ReminderType.FOLLOW_UP_1D,
    aiSignals: ['presentation_sent', 'show_rate'],
    touchpoint: {
      type: InteractionType.EMAIL,
      summary: 'Show → Deliver presentation + action plan',
      notesHint: 'Highlight key wins, answer objections, remind of next step'
    }
  },
  {
    status: PipelineStatus.FOLLOW_UP,
    frazerStep: 'Keep Talking',
    cadenceHours: 96,
    reminderType: ReminderType.FOLLOW_UP_7D,
    aiSignals: ['follow_up_count', 'objection_handling'],
    touchpoint: {
      type: InteractionType.CALL,
      summary: 'Keep Talking → Collect decision / objection',
      notesHint: 'Reiterate value, isolate objections, confirm decision date'
    }
  },
  {
    status: PipelineStatus.CLOSED_WON,
    frazerStep: 'Enroll',
    cadenceHours: 168,
    reminderType: ReminderType.FOLLOW_UP,
    aiSignals: ['enrollment', 'onboarding_speed'],
    touchpoint: {
      type: InteractionType.NOTE,
      summary: 'Enroll → Onboard + celebrate',
      notesHint: 'Capture launch tasks, tag accountability partner'
    }
  },
  {
    status: PipelineStatus.NOT_NOW,
    frazerStep: 'Keep Talking',
    cadenceHours: 240,
    reminderType: ReminderType.FOLLOW_UP_7D,
    aiSignals: ['nurture_needed', 'objection_type'],
    touchpoint: {
      type: InteractionType.NOTE,
      summary: 'Not Now → Drop value + timeline reminder',
      notesHint: 'Log objection, set revisit date, share success story'
    }
  },
  {
    status: PipelineStatus.LONG_TERM_NURTURE,
    frazerStep: 'Keep Talking',
    cadenceHours: 360,
    reminderType: ReminderType.FOLLOW_UP,
    aiSignals: ['nurture_sequence', 'content_engagement'],
    touchpoint: {
      type: InteractionType.EMAIL,
      summary: 'Long-term Nurture → Deliver consistent value',
      notesHint: 'Share proof, highlight wins, invite soft micro-commitment'
    }
  }
];

export function getStageDefinition(status: PipelineStatus): FrazerStageDefinition {
  return FRAZER_STAGE_DEFINITIONS.find(def => def.status === status) || DEFAULT_STAGE_DEFINITION;
}
