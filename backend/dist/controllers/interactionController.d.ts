import { Request, Response } from 'express';
export declare class InteractionController {
    private interactionService;
    constructor();
    getInteractionsByCustomer: (req: Request, res: Response) => Promise<void>;
    createInteraction: (req: Request, res: Response) => Promise<Response<any, Record<string, any>> | undefined>;
    updateInteraction: (req: Request, res: Response) => Promise<Response<any, Record<string, any>> | undefined>;
    deleteInteraction: (req: Request, res: Response) => Promise<Response<any, Record<string, any>> | undefined>;
    getUpcomingInteractions: (req: Request, res: Response) => Promise<void>;
}
//# sourceMappingURL=interactionController.d.ts.map