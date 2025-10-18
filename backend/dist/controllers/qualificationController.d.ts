import { Request, Response } from 'express';
export declare class QualificationController {
    createQualification(req: Request, res: Response): Promise<void>;
    getQualificationById(req: Request, res: Response): Promise<void>;
    updateQualificationStatus(req: Request, res: Response): Promise<void>;
    recordQualificationAnswer(req: Request, res: Response): Promise<void>;
    getAnswersForQualification(req: Request, res: Response): Promise<void>;
    getQualificationsByCustomerId(req: Request, res: Response): Promise<void>;
    getPendingQualifications(req: Request, res: Response): Promise<void>;
    deleteQualification(req: Request, res: Response): Promise<void>;
    deleteQualificationAnswer(req: Request, res: Response): Promise<void>;
    getCustomerQualificationSummary(req: Request, res: Response): Promise<void>;
}
declare const _default: QualificationController;
export default _default;
//# sourceMappingURL=qualificationController.d.ts.map