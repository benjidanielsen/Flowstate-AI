import { Interaction, InteractionType } from '../types';
export declare class InteractionService {
    private eventLogService;
    constructor();
    create(interaction: Omit<Interaction, 'id' | 'created_at' | 'updated_at'>): Promise<Interaction>;
    getByCustomerId(customerId: string): Promise<Interaction[]>;
    getById(id: string): Promise<Interaction | undefined>;
    update(id: string, updates: Partial<Omit<Interaction, 'id' | 'created_at'>>): Promise<Interaction | undefined>;
    delete(id: string): Promise<boolean>;
    getAllInteractions(): Promise<Interaction[]>;
    getInteractionSummaryByType(): Promise<Record<InteractionType, number>>;
}
export declare const interactionService: InteractionService;
//# sourceMappingURL=interactionService.d.ts.map