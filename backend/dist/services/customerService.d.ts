import { Customer, PipelineStatus } from '../types';
export declare class CustomerService {
    private eventLogService;
    constructor();
    getAllCustomers(): Promise<Customer[]>;
    getCustomerById(id: string): Promise<Customer | null>;
    createCustomer(customerData: Omit<Customer, 'id' | 'created_at' | 'updated_at'>): Promise<Customer>;
    updateCustomer(id: string, updates: Partial<Customer>): Promise<Customer | null>;
    deleteCustomer(id: string): Promise<boolean>;
    getCustomersByStatus(status: PipelineStatus): Promise<Customer[]>;
    moveCustomerToNextStage(id: string): Promise<Customer | null>;
}
//# sourceMappingURL=customerService.d.ts.map