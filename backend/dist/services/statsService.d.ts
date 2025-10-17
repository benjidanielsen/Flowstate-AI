export declare class StatsService {
    private cache;
    private cacheDuration;
    private getCached;
    private setCache;
    countsByStatus(): Promise<Record<string, number>>;
    private dateRange;
    dmoCounters(): Promise<any>;
    extraCounts(): Promise<any>;
    getCustomerDemographics(): Promise<{
        byCountry: Record<string, number>;
        byLanguage: Record<string, number>;
        bySource: Record<string, number>;
    }>;
    getInteractionSummary(): Promise<{
        byType: Record<string, number>;
        totalInteractions: number;
        avgInteractionsPerCustomer: number;
    }>;
    getPipelineConversionRates(): Promise<Record<string, number>>;
}
//# sourceMappingURL=statsService.d.ts.map