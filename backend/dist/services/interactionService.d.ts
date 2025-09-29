import { Interaction } from '../types';
export declare class InteractionService {
    private eventLogService;
    constructor();
    getInteractionsByCustomer(customerId: string): Promise<Interaction[]>;
    createInteraction(interactionData: Omit<Interaction, 'id' | 'created_at'>): Promise<Interaction>;
    updateInteraction(id: string, updates: Partial<Interaction>): Promise<Interaction | null>;
    getInteractionById(id: string): Promise<Interaction | null>;
    deleteInteraction(id: string): Promise<boolean>;
    getUpcomingInteractions(limit?: number): Promise<Interaction[]>;
}
//# sourceMappingURL=interactionService.d.ts.map