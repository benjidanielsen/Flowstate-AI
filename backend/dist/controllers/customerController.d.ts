import { Request, Response } from 'express';
export declare class CustomerController {
    private customerService;
    private statsService;
    constructor();
    getAllCustomers: (req: Request, res: Response) => Promise<void>;
    getCustomerById: (req: Request, res: Response) => Promise<Response<any, Record<string, any>> | undefined>;
    createCustomer: (req: Request, res: Response) => Promise<Response<any, Record<string, any>> | undefined>;
    updateCustomer: (req: Request, res: Response) => Promise<Response<any, Record<string, any>> | undefined>;
    deleteCustomer: (req: Request, res: Response) => Promise<Response<any, Record<string, any>> | undefined>;
    moveToNextStage: (req: Request, res: Response) => Promise<Response<any, Record<string, any>> | undefined>;
    getPipelineStats: (req: Request, res: Response) => Promise<void>;
}
//# sourceMappingURL=customerController.d.ts.map