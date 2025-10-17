export interface QualificationData {
    prospect_why?: string;
    pain_points?: string[];
    desired_outcome?: string;
    timeline?: string;
    budget_range?: string;
    decision_maker?: boolean;
    decision_process?: string;
    current_solution?: string;
    objections?: string[];
    notes?: string;
}
export interface QualificationResult {
    is_qualified: boolean;
    qualification_score: number;
    missing_fields: string[];
    qualification_data: QualificationData;
}
export declare class QualificationService {
    private eventLogService;
    private requiredFields;
    constructor();
    /**
     * Save qualification data for a customer
     */
    saveQualification(customerId: string, qualificationData: QualificationData): Promise<void>;
    /**
     * Get qualification data for a customer
     */
    getQualification(customerId: string): Promise<QualificationData | null>;
    /**
     * Check if a customer is qualified based on Frazer Method requirements
     */
    checkQualification(customerId: string): Promise<QualificationResult>;
    /**
     * Validate if a customer can move to a specific pipeline stage
     */
    canMoveToStage(customerId: string, targetStage: string): Promise<{
        allowed: boolean;
        reason?: string;
    }>;
    /**
     * Get qualification statistics for all customers
     */
    getQualificationStats(): Promise<{
        total_customers: number;
        qualified_customers: number;
        average_qualification_score: number;
        qualification_rate: number;
    }>;
}
//# sourceMappingURL=qualificationService.d.ts.map