import { Request, Response } from 'express';
export declare class ReminderController {
    private reminderService;
    listDue: (_req: Request, res: Response) => Promise<void>;
    create: (req: Request, res: Response) => Promise<Response<any, Record<string, any>> | undefined>;
    complete: (req: Request, res: Response) => Promise<Response<any, Record<string, any>> | undefined>;
}
//# sourceMappingURL=reminderController.d.ts.map