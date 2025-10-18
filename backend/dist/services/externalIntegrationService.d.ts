import { ExternalIntegration } from '../types';
export declare class ExternalIntegrationService {
    createIntegration(integration: Omit<ExternalIntegration, 'id' | 'created_at' | 'updated_at'>): Promise<ExternalIntegration>;
    getIntegrationsByCustomer(customerId: string): Promise<ExternalIntegration[]>;
    updateIntegration(id: string, updates: Partial<Omit<ExternalIntegration, 'id' | 'customer_id' | 'created_at'>>): Promise<ExternalIntegration | null>;
    deleteIntegration(id: string): Promise<boolean>;
    getIntegrationById(id: string): Promise<ExternalIntegration | null>;
}
export declare const externalIntegrationService: ExternalIntegrationService;
//# sourceMappingURL=externalIntegrationService.d.ts.map