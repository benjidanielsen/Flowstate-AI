import { ExternalIntegration } from '../types';
export declare class ExternalIntegrationService {
    createIntegration(integration: Omit<ExternalIntegration, 'id' | 'created_at' | 'updated_at'>): Promise<ExternalIntegration>;
    getIntegrationsByCustomer(customerId: string): Promise<ExternalIntegration[]>;
    updateIntegration(id: string, updates: Partial<Omit<ExternalIntegration, 'id' | 'customer_id' | 'created_at'>>): Promise<ExternalIntegration>;
    deleteIntegration(id: string): Promise<void>;
}
//# sourceMappingURL=externalIntegrationService.d.ts.map