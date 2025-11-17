import DatabaseManager from "../database";
import { safeLogger } from "./piiRedaction";

export class DbOptimizer {
  private db = DatabaseManager.getInstance().getDb();

  constructor(private dbManager: DatabaseManager = DatabaseManager.getInstance()) {
    this.db = this.dbManager.getDb();
  }

  /**
   * Analyzes database performance and suggests optimizations.
   * This is a simplified example; real-world would involve more complex analysis.
   */
  public async analyzeAndSuggestOptimizations(): Promise<string[]> {
    safeLogger.info("Starting database optimization analysis...");
    const suggestions: string[] = [];

    try {
      const customerCount = await new Promise<number>((resolve, reject) => {
        this.db.get('SELECT COUNT(*) AS count FROM customers', (err, row: any) => {
          if (err) {
            reject(err);
          } else {
            resolve(Number(row?.count || 0));
          }
        });
      });
      if (customerCount > 10000) {
        suggestions.push('Consider adding an index on customers.email for faster lookups.');
      }

      suggestions.push('Monitor long-running queries using pg_stat_statements.');
      suggestions.push('Regularly run VACUUM ANALYZE to optimize database space and performance.');

      safeLogger.info("Database optimization analysis completed.");
    } catch (error) {
      safeLogger.error("Error during database optimization analysis", error);
      suggestions.push("Error during analysis. Please check database connection and permissions.");
    }

    return suggestions;
  }

  /**
   * Executes a specific optimization (e.g., adding an index).
   * This should be used with extreme caution in production.
   */
  public async executeOptimization(sqlCommand: string): Promise<void> {
    safeLogger.warn(`Executing database optimization command: ${sqlCommand}`);
    try {
      await new Promise<void>((resolve, reject) => {
        this.db.run(sqlCommand, (err) => {
          if (err) {
            reject(err);
          } else {
            resolve();
          }
        });
      });
      safeLogger.info("Optimization command executed successfully.");
    } catch (error) {
      safeLogger.error(`Error executing optimization command: ${sqlCommand}`, error);
      throw error;
    }
  }
}
