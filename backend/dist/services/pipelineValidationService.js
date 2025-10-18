"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.pipelineValidationService = exports.PipelineValidationService = void 0;
const qualificationService_1 = require("./qualificationService");
const logger_1 = __importDefault(require("../utils/logger"));
const types_1 = require("../types");
class PipelineValidationService {
    constructor() {
        // Define the Frazer Method pipeline flow
        this.stageOrder = [
            types_1.PipelineStatus.NEW_LEAD,
            types_1.PipelineStatus.WARMING_UP,
            types_1.PipelineStatus.INVITED,
            types_1.PipelineStatus.QUALIFIED,
            types_1.PipelineStatus.PRESENTATION_SENT,
            types_1.PipelineStatus.FOLLOW_UP,
            types_1.PipelineStatus.CLOSED_WON
        ];
        // Define alternative paths
        this.alternativePaths = {
            [types_1.PipelineStatus.NEW_LEAD]: [types_1.PipelineStatus.NOT_NOW, types_1.PipelineStatus.LONG_TERM_NURTURE],
            [types_1.PipelineStatus.WARMING_UP]: [types_1.PipelineStatus.NOT_NOW, types_1.PipelineStatus.LONG_TERM_NURTURE],
            [types_1.PipelineStatus.INVITED]: [types_1.PipelineStatus.NOT_NOW, types_1.PipelineStatus.LONG_TERM_NURTURE],
            [types_1.PipelineStatus.QUALIFIED]: [types_1.PipelineStatus.NOT_NOW, types_1.PipelineStatus.LONG_TERM_NURTURE],
            [types_1.PipelineStatus.PRESENTATION_SENT]: [types_1.PipelineStatus.NOT_NOW, types_1.PipelineStatus.LONG_TERM_NURTURE],
            [types_1.PipelineStatus.FOLLOW_UP]: [types_1.PipelineStatus.NOT_NOW, types_1.PipelineStatus.LONG_TERM_NURTURE, types_1.PipelineStatus.CLOSED_WON],
        };
    }
    /**
     * Validate if a customer can transition from one stage to another
     */
    async validateStageTransition(customerId, currentStage, targetStage) {
        logger_1.default.info(`Checking if customer ${customerId} can transition from ${currentStage} to ${targetStage}`);
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
                const qualificationCheck = await qualificationService_1.qualificationService.canMoveToStage(customerId, targetStage);
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
    getRequiredPath(from, to) {
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
    requiresQualification(stage) {
        const qualificationRequiredStages = [
            types_1.PipelineStatus.QUALIFIED,
            types_1.PipelineStatus.PRESENTATION_SENT,
            types_1.PipelineStatus.FOLLOW_UP,
            types_1.PipelineStatus.CLOSED_WON
        ];
        return qualificationRequiredStages.includes(stage);
    }
    /**
     * Get the next valid stages for a customer
     */
    getNextValidStages(currentStage) {
        const currentIndex = this.stageOrder.indexOf(currentStage);
        const nextStages = [];
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
    async getStageRecommendations(customerId, currentStage) {
        logger_1.default.info(`Getting stage recommendations for customer ${customerId} at stage ${currentStage}`);
        const qualificationResult = await qualificationService_1.qualificationService.checkQualification(customerId);
        const nextStages = this.getNextValidStages(currentStage);
        let recommendedStage = currentStage;
        let confidence = 0;
        const reasoning = [];
        // If customer is qualified and in early stages, recommend moving forward
        if (qualificationResult.is_qualified && currentStage === types_1.PipelineStatus.INVITED) {
            recommendedStage = types_1.PipelineStatus.QUALIFIED;
            confidence = 90;
            reasoning.push('Customer is fully qualified');
            reasoning.push('All required information has been collected');
        }
        else if (qualificationResult.qualification_score >= 75 && currentStage === types_1.PipelineStatus.WARMING_UP) {
            recommendedStage = types_1.PipelineStatus.INVITED;
            confidence = 80;
            reasoning.push('Customer shows strong engagement');
            reasoning.push('Most qualification criteria are met');
        }
        else if (qualificationResult.qualification_score < 50 &&
            [types_1.PipelineStatus.NEW_LEAD, types_1.PipelineStatus.WARMING_UP].includes(currentStage)) {
            recommendedStage = types_1.PipelineStatus.LONG_TERM_NURTURE;
            confidence = 70;
            reasoning.push('Low qualification score indicates need for more nurturing');
            reasoning.push('Consider moving to long-term nurture for gradual engagement');
        }
        else {
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
    async logStageTransition(customerId, fromStage, toStage, notes) {
        // EventLogService is not imported. Assuming this is handled elsewhere or needs to be added.
        // For now, just log to console.
        logger_1.default.info(`Logging stage transition for customer ${customerId}: ${fromStage} -> ${toStage}`, { notes });
    }
}
exports.PipelineValidationService = PipelineValidationService;
exports.pipelineValidationService = new PipelineValidationService();
//# sourceMappingURL=pipelineValidationService.js.map