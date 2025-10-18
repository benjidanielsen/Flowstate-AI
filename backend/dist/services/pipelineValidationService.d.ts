import { PipelineStatus } from '../types';
export interface ValidationResult {
    allowed: boolean;
    reason?: string;
    suggestions?: string[];
}
export declare class PipelineValidationService {
    private stageOrder;
    private alternativePaths;
    /**
     * Validate if a customer can transition from one stage to another
     */
    validateStageTransition(customerId: string, currentStage: PipelineStatus, targetStage: PipelineStatus): Promise<ValidationResult>;
    /**
     * Get the required path between two stages
     */
    private getRequiredPath;
    /**
     * Check if a stage requires qualification
     */
    private requiresQualification;
    /**
     * Get the next valid stages for a customer
     */
    getNextValidStages(currentStage: PipelineStatus): PipelineStatus[];
    /**
     * Get pipeline stage recommendations based on customer data
     */
    getStageRecommendations(customerId: string, currentStage: PipelineStatus): Promise<{
        recommended_stage: PipelineStatus;
        confidence: number;
        reasoning: string[];
    }>;
    /**
     * Log a stage transition event
     */
    logStageTransition(customerId: string, fromStage: PipelineStatus, toStage: PipelineStatus, notes?: string): Promise<void>;
}
export declare const pipelineValidationService: PipelineValidationService;
//# sourceMappingURL=pipelineValidationService.d.ts.map