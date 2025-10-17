import { Request, Response } from 'express';
export declare class WebhookController {
    private eventLogService;
    dm: (req: Request, res: Response) => Promise<void>;
    capiLead: (req: Request, res: Response) => Promise<void>;
}
//# sourceMappingURL=webhookController.d.ts.map