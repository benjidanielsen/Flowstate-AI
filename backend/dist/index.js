"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.createApp = createApp;
exports.startServer = startServer;
exports.shutdown = shutdown;
const express_1 = __importDefault(require("express"));
const body_parser_1 = __importDefault(require("body-parser"));
const dotenv_1 = __importDefault(require("dotenv"));
const cors_1 = __importDefault(require("cors"));
const helmet_1 = __importDefault(require("helmet"));
const path_1 = __importDefault(require("path"));
const swagger_ui_express_1 = __importDefault(require("swagger-ui-express"));
const yamljs_1 = __importDefault(require("yamljs"));
const routes_1 = __importDefault(require("./routes"));
const performanceMiddleware_1 = __importDefault(require("./middleware/performanceMiddleware"));
const correlationId_1 = require("./middleware/correlationId"); // Import correlationId middleware
const idempotency_1 = require("./middleware/idempotency"); // Import idempotency middleware
const database_1 = __importDefault(require("./database"));
const supabase_1 = require("./database/supabase"); // Import test connection from supabase.ts
const migrate_1 = require("./database/migrate");
const piiRedaction_1 = require("./utils/piiRedaction"); // Use safeLogger
require("./utils/tracer"); // Initialize OpenTelemetry tracer
const swaggerDocument = yamljs_1.default.load(path_1.default.resolve(__dirname, '../../openapi.yaml'));
dotenv_1.default.config();
const app = (0, express_1.default)();
let serverRef = null;
let isShuttingDown = false;
let shutdownPromise = null;
// Ensure the database connection is established early for Drizzle to initialize properly
// This is a workaround to ensure `db` is initialized before any services try to use it.
// In a real application, you might want a more controlled initialization flow.
const initializeDatabaseAndDrizzle = async () => {
    try {
        piiRedaction_1.safeLogger.info('Initializing database and running migrations...');
        await database_1.default.getInstance().connect();
        await (0, supabase_1.testConnection)(); // Test Supabase connection
        await (0, migrate_1.runMigrations)(); // Run custom migrations for initial schema setup
    }
    catch (error) {
        piiRedaction_1.safeLogger.error('Failed to initialize database and Drizzle:', error);
        process.exit(1); // Exit if database initialization fails
    }
};
// Middleware
app.use((0, helmet_1.default)());
app.use((0, cors_1.default)());
app.use(correlationId_1.correlationIdMiddleware); // Add correlation ID middleware early
app.use(body_parser_1.default.json());
app.use(express_1.default.urlencoded({ extended: true }));
app.use(idempotency_1.idempotencyMiddleware); // Add idempotency middleware after body parser
app.use(performanceMiddleware_1.default);
// Routes
app.use("/api", routes_1.default);
app.use("/api-docs", swagger_ui_express_1.default.serve, swagger_ui_express_1.default.setup(swaggerDocument));
// Global Error Handling Middleware
app.use((err, req, res, _next) => {
    piiRedaction_1.safeLogger.error(`Unhandled error: ${err.message}`, { stack: err.stack, path: req.path, method: req.method, correlationId: req.correlationId });
    res.status(500).json({ message: 'Internal Server Error', error: err.message });
});
// 404 handler
app.use((req, res) => {
    piiRedaction_1.safeLogger.warn(`Route not found: ${req.method} ${req.path}`, { correlationId: req.correlationId });
    res.status(404).json({ error: 'Route not found' });
});
function createApp() {
    return app;
}
async function startServer() {
    try {
        // The database initialization and migration are now handled by initializeDatabaseAndDrizzle() call above
        // This ensures they run before the server attempts to start and use the database
        // Start server
        serverRef = app.listen(process.env.PORT || 3001, () => {
            piiRedaction_1.safeLogger.info(`Server is running on port ${process.env.PORT || 3001}`);
            piiRedaction_1.safeLogger.info(`Environment: ${process.env.NODE_ENV || 'development'}`);
        });
        return serverRef;
    }
    catch (error) {
        piiRedaction_1.safeLogger.error('Failed to start server:', error);
        throw error;
    }
}
// Graceful shutdown
async function shutdown() {
    piiRedaction_1.safeLogger.info('Shutting down gracefully');
    if (isShuttingDown && shutdownPromise) {
        return shutdownPromise;
    }
    isShuttingDown = true;
    shutdownPromise = (async () => {
        // Close HTTP server if running
        if (serverRef) {
            await new Promise((resolve, reject) => {
                let closeTimeout = null;
                const onClose = (err) => {
                    if (closeTimeout) {
                        clearTimeout(closeTimeout);
                        closeTimeout = null;
                    }
                    if (err) {
                        piiRedaction_1.safeLogger.error('Error closing server:', err);
                        reject(err);
                        return;
                    }
                    serverRef = null;
                    resolve();
                };
                serverRef.close(onClose);
                // Safety: force resolve if close hangs (5s)
                closeTimeout = setTimeout(() => {
                    try {
                        /* istanbul ignore next */
                        piiRedaction_1.safeLogger.warn('Server close timed out after 5s; continuing with DB close');
                    }
                    catch (e) {
                        // swallow any logging errors
                    }
                    serverRef = null;
                    resolve();
                }, 5000);
            });
        }
        await database_1.default.getInstance().close();
        isShuttingDown = false; // Reset after successful shutdown
        shutdownPromise = null; // Reset after successful shutdown
    })();
    return shutdownPromise;
}
if (require.main === module) {
    // When run directly, initialize database, start the server and attach signal handlers that exit the process
    initializeDatabaseAndDrizzle()
        .then(() => startServer())
        .catch((err) => {
        piiRedaction_1.safeLogger.error("Fatal error starting server:", err);
        process.exit(1);
    });
    process.on('SIGTERM', async () => {
        piiRedaction_1.safeLogger.info('SIGTERM received, shutting down gracefully');
        await shutdown();
        process.exit(0);
    });
    process.on('SIGINT', async () => {
        piiRedaction_1.safeLogger.info('SIGINT received, shutting down gracefully');
        await shutdown();
        process.exit(0);
    });
}
exports.default = app;
//# sourceMappingURL=index.js.map