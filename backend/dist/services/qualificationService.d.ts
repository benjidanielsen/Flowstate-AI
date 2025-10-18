import { Qualification, QualificationAnswer } from '../types';
export declare class QualificationService {
    createQualification(data: {
        customer_id: string;
        question: string;
        expected_answer: string;
        status: 'pending' | 'completed' | 'failed';
        agent_name?: string;
    }): Promise<Qualification>;
    getQualificationById(id: string): Promise<Qualification | null>;
    updateQualificationStatus(id: string, status: 'pending' | 'completed' | 'failed'): Promise<Qualification | null>;
    recordQualificationAnswer(data: {
        qualification_id: string;
        answer: string;
        is_correct: boolean;
        agent_name?: string;
    }): Promise<QualificationAnswer>;
    getAnswersForQualification(qualificationId: string): Promise<QualificationAnswer[]>;
    getQualificationsByCustomerId(customerId: string): Promise<Qualification[]>;
    getPendingQualifications(): Promise<Qualification[]>;
    deleteQualification(id: string): Promise<boolean>;
    deleteQualificationAnswer(id: string): Promise<boolean>;
    getCustomerQualificationSummary(): Promise<any[]>;
    canMoveToStage(customerId: string, targetStage: string): Promise<{
        allowed: boolean;
        reason?: string;
    }>;
    checkQualification(customerId: string): Promise<{
        is_qualified: boolean;
        qualification_score: number;
        reason?: string;
    }>;
}
export declare const qualificationService: QualificationService;
//# sourceMappingURL=qualificationService.d.ts.map