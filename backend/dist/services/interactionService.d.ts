import { Interaction } from '../types';
export declare const interactionService: {
    create(interaction: Omit<Interaction, "id" | "created_at" | "updated_at">): Promise<Interaction>;
    getByCustomerId(customerId: string): Promise<Interaction[]>;
    getById(id: string): Promise<Interaction | undefined>;
    update(id: string, updates: Partial<Omit<Interaction, "id" | "created_at">>): Promise<Interaction | undefined>;
    delete(id: string): Promise<void>;
};
//# sourceMappingURL=interactionService.d.ts.map