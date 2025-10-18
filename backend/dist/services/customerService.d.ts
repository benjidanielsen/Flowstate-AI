import { Customer, PipelineStatus } from '../types';
export declare class CustomerService {
    private eventLogService;
    private pipelineValidationService;
    constructor();
    getAllCustomers(filters?: {
        status?: PipelineStatus;
        search?: string;
        source?: string;
        country?: string;
        language?: string;
        next_action?: string;
        sortBy?: string;
        sortOrder?: 'ASC' | 'DESC';
    }): Promise<Customer[]>;
    getCustomerById(id: string): Promise<Customer | null>;
    createCustomer(customerData: Omit<Customer, 'id' | 'created_at' | 'updated_at'>): Promise<Customer>;
    updateCustomer(id: string, updates: Partial<Customer>): Promise<Customer | null>;
    deleteCustomer(id: string): Promise<boolean>;
    getCustomersByStatus(status: PipelineStatus): Promise<Customer[]>;
    moveCustomerToNextStage(id: string): Promise<Customer | null>;
    /**
     * Move customer to a specific stage with validation
     */
    moveCustomerToStage(id: string, targetStage: PipelineStatus): Promise<Customer | null>;
    /**
     * Get stage recommendations for a customer
     */
    getStageRecommendations(id: string): Promise<{
        recommended_stage: PipelineStatus;
        confidence: number;
        reasoning: string[];
    } | null>;
}
export declare const customerService: CustomerService;
//# sourceMappingURL=customerService.d.ts.map