import { Request, Response } from 'express';
export declare class EventController {
    private eventLogService;
    private automation;
    constructor();
    createEvent: (req: Request, res: Response) => Promise<Response<any, Record<string, any>> | undefined>;
    getAll: (req: Request, res: Response) => Promise<void>;
    getByCustomer: (req: Request, res: Response) => Promise<void>;
    getByType: (req: Request, res: Response) => Promise<Response<any, Record<string, any>> | undefined>;
}
//# sourceMappingURL=eventController.d.ts.map