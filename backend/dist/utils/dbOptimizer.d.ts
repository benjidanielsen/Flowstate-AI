import DatabaseManager from "../database";
export declare class DbOptimizer {
    private dbManager;
    constructor(dbManager: DatabaseManager);
    /**
     * Analyzes database performance and suggests optimizations.
     * This is a simplified example; real-world would involve more complex analysis.
     */
    analyzeAndSuggestOptimizations(): Promise<string[]>;
    /**
     * Executes a specific optimization (e.g., adding an index).
     * This should be used with extreme caution in production.
     */
    executeOptimization(sqlCommand: string): Promise<void>;
}
//# sourceMappingURL=dbOptimizer.d.ts.map