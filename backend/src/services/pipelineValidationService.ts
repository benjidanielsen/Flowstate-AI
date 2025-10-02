import { PipelineStatus } from '../types';
import { QualificationService } from './qualificationService';
import { EventLogService } from './eventLogService';

export interface StageTransitionRule {
  from: PipelineStatus;
  to: PipelineStatus;
  requiresQualification: boolean;
  validationMessage?: string;
}

export interface ValidationResult {
  allowed: boolean;
  reason?: string;
  suggestions?: string[];
}

export class PipelineValidationService {
  private qualificationService: QualificationService;
  private eventLogService: EventLogService;
  
  // Define the Frazer Method pipeline flow
  private stageOrder: PipelineStatus[] = [
    PipelineStatus.NEW_LEAD,
    PipelineStatus.WARMING_UP,
    PipelineStatus.INVITED,
    PipelineStatus.QUALIFIED,
    PipelineStatus.PRESENTATION_SENT,
    PipelineStatus.FOLLOW_UP,
    PipelineStatus.CLOSED_WON
  ];

  // Define alternative paths
  private alternativePaths: { [key: string]: PipelineStatus[] } = {
    [PipelineStatus.NEW_LEAD]: [PipelineStatus.NOT_NOW, PipelineStatus.LONG_TERM_NURTURE],
    [PipelineStatus.WARMING_UP]: [PipelineStatus.NOT_NOW, PipelineStatus.LONG_TERM_NURTURE],
    [PipelineStatus.INVITED]: [PipelineStatus.NOT_NOW, PipelineStatus.LONG_TERM_NURTURE],
    [PipelineStatus.QUALIFIED]: [PipelineStatus.NOT_NOW, PipelineStatus.LONG_TERM_NURTURE],
    [PipelineStatus.PRESENTATION_SENT]: [PipelineStatus.NOT_NOW, PipelineStatus.LONG_TERM_NURTURE],
    [PipelineStatus.FOLLOW_UP]: [PipelineStatus.NOT_NOW, PipelineStatus.LONG_TERM_NURTURE, PipelineStatus.CLOSED_WON],
  };

  constructor() {
    this.qualificationService = new QualificationService();
    this.eventLogService = new EventLogService();
  }

  /**
   * Validate if a customer can transition from one stage to another
   */
  async validateStageTransition(
    customerId: string,
    currentStage: PipelineStatus,
    targetStage: PipelineStatus
  ): Promise<ValidationResult> {
    // Check if it's a valid forward progression
    const currentIndex = this.stageOrder.indexOf(currentStage);
    const targetIndex = this.stageOrder.indexOf(targetStage);

    // Allow moving to alternative paths
    if (this.alternativePaths[currentStage]?.includes(targetStage)) {
      return { allowed: true };
    }

    // Check if it's a forward progression in the main pipeline
    if (targetIndex > currentIndex && targetIndex === currentIndex + 1) {
      // Check if qualification is required for this stage
      if (this.requiresQualification(targetStage)) {
        const qualificationCheck = await this.qualificationService.canMoveToStage(customerId, targetStage);
        
        if (!qualificationCheck.allowed) {
          return {
            allowed: false,
            reason: qualificationCheck.reason,
            suggestions: [
              'Complete the qualification form',
              'Ensure all required fields are filled',
              'Document the prospect\'s WHY'
            ]
          };
        }
      }

      return { allowed: true };
    }

    // Check if it's a backward move (allowed for corrections)
    if (targetIndex < currentIndex) {
      return {
        allowed: true,
        reason: 'Moving backward in the pipeline for correction'
      };
    }

    // Check if it's skipping stages (not allowed in Frazer Method)
    if (targetIndex > currentIndex + 1) {
      return {
        allowed: false,
        reason: `Cannot skip stages. Must progress through: ${this.getRequiredPath(currentStage, targetStage).join(' → ')}`,
        suggestions: [
          `Move to ${this.stageOrder[currentIndex + 1]} first`,
          'Follow the Frazer Method pipeline progression'
        ]
      };
    }

    return {
      allowed: false,
      reason: 'Invalid stage transition',
      suggestions: ['Review the Frazer Method pipeline flow']
    };
  }

  /**
   * Get the required path between two stages
   */
  private getRequiredPath(from: PipelineStatus, to: PipelineStatus): PipelineStatus[] {
    const fromIndex = this.stageOrder.indexOf(from);
    const toIndex = this.stageOrder.indexOf(to);

    if (fromIndex === -1 || toIndex === -1 || toIndex <= fromIndex) {
      return [];
    }

    return this.stageOrder.slice(fromIndex, toIndex + 1);
  }

  /**
   * Check if a stage requires qualification
   */
  private requiresQualification(stage: PipelineStatus): boolean {
    const qualificationRequiredStages = [
      PipelineStatus.QUALIFIED,
      PipelineStatus.PRESENTATION_SENT,
      PipelineStatus.FOLLOW_UP,
      PipelineStatus.CLOSED_WON
    ];

    return qualificationRequiredStages.includes(stage);
  }

  /**
   * Get the next valid stages for a customer
   */
  getNextValidStages(currentStage: PipelineStatus): PipelineStatus[] {
    const currentIndex = this.stageOrder.indexOf(currentStage);
    const nextStages: PipelineStatus[] = [];

    // Add the next stage in the main pipeline
    if (currentIndex !== -1 && currentIndex < this.stageOrder.length - 1) {
      nextStages.push(this.stageOrder[currentIndex + 1]);
    }

    // Add alternative paths
    if (this.alternativePaths[currentStage]) {
      nextStages.push(...this.alternativePaths[currentStage]);
    }

    return nextStages;
  }

  /**
   * Get pipeline stage recommendations based on customer data
   */
  async getStageRecommendations(customerId: string, currentStage: PipelineStatus): Promise<{
    recommended_stage: PipelineStatus;
    confidence: number;
    reasoning: string[];
  }> {
    const qualificationResult = await this.qualificationService.checkQualification(customerId);
    const nextStages = this.getNextValidStages(currentStage);

    let recommendedStage = currentStage;
    let confidence = 0;
    const reasoning: string[] = [];

    // If customer is qualified and in early stages, recommend moving forward
    if (qualificationResult.is_qualified && currentStage === PipelineStatus.INVITED) {
      recommendedStage = PipelineStatus.QUALIFIED;
      confidence = 90;
      reasoning.push('Customer is fully qualified');
      reasoning.push('All required information has been collected');
    } else if (qualificationResult.qualification_score >= 75 && currentStage === PipelineStatus.WARMING_UP) {
      recommendedStage = PipelineStatus.INVITED;
      confidence = 80;
      reasoning.push('Customer shows strong engagement');
      reasoning.push('Most qualification criteria are met');
    } else if (qualificationResult.qualification_score < 50 && 
               [PipelineStatus.NEW_LEAD, PipelineStatus.WARMING_UP].includes(currentStage)) {
      recommendedStage = PipelineStatus.LONG_TERM_NURTURE;
      confidence = 70;
      reasoning.push('Low qualification score indicates need for more nurturing');
      reasoning.push('Consider moving to long-term nurture for gradual engagement');
    } else {
      // Default recommendation: next stage in pipeline
      if (nextStages.length > 0) {
        recommendedStage = nextStages[0];
        confidence = 60;
        reasoning.push('Continue with standard pipeline progression');
      }
    }

    return {
      recommended_stage: recommendedStage,
      confidence,
      reasoning
    };
  }

  /**
   * Log a stage transition event
   */
  async logStageTransition(
    customerId: string,
    fromStage: PipelineStatus,
    toStage: PipelineStatus,
    notes?: string
  ): Promise<void> {
    await this.eventLogService.logEvent('stage_transition', {
      customer_id: customerId,
      from_stage: fromStage,
      to_stage: toStage,
      notes: notes || ''
    }, customerId);
  }
}
