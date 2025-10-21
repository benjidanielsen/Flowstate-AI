import express, { Request, Response, NextFunction } from 'express';
import bodyParser from 'body-parser';
import dotenv from 'dotenv';
import cors from 'cors';
import helmet from 'helmet';
import http from 'http';
import path from 'path';
import fs from 'fs';
import swaggerUi from 'swagger-ui-express';
import YAML from 'yamljs';

import routes from './routes';
import performanceMiddleware from './middleware/performanceMiddleware';
import { correlationIdMiddleware } from './middleware/correlationId'; // Import correlationId middleware
import { idempotencyMiddleware } from './middleware/idempotency'; // Import idempotency middleware
import DatabaseManager from './database';
import { runMigrations } from './database/migrate';
import { safeLogger } from './utils/piiRedaction'; // Use safeLogger
import './utils/tracer'; // Initialize OpenTelemetry tracer

const swaggerPath = path.resolve(__dirname, '../../openapi.yaml');
const swaggerDocument = fs.existsSync(swaggerPath) ? YAML.load(swaggerPath) : null;

dotenv.config();

const app = express();

let serverRef: http.Server | null = null;
let isShuttingDown = false;
let shutdownPromise: Promise<void> | null = null;

// Middleware
app.use(helmet());
app.use(cors());
app.use(correlationIdMiddleware); // Add correlation ID middleware early
app.use(bodyParser.json());
app.use(express.urlencoded({ extended: true }));
app.use(idempotencyMiddleware); // Add idempotency middleware after body parser
app.use(performanceMiddleware);

// Routes
app.use("/api", routes);
if (swaggerDocument) {
  app.use("/api-docs", swaggerUi.serve, swaggerUi.setup(swaggerDocument));
} else {
  safeLogger.warn('openapi.yaml not found; skipping Swagger UI mounting.');
}

// Global Error Handling Middleware
app.use((err: Error, req: Request, res: Response, _next: NextFunction) => { // eslint-disable-line @typescript-eslint/no-unused-vars
  safeLogger.error(`Unhandled error: ${err.message}`, { stack: err.stack, path: req.path, method: req.method, correlationId: req.correlationId });
  res.status(500).json({ message: 'Internal Server Error', error: err.message });
});

// 404 handler
app.use((req: Request, res: Response) => {
  safeLogger.warn(`Route not found: ${req.method} ${req.path}`, { correlationId: req.correlationId });
  res.status(404).json({ error: 'Route not found' });
});

export function createApp() {
  return app;
}

export async function startServer() {
  try {
    // Initialize database
    safeLogger.info('Connecting to database...');
    await DatabaseManager.getInstance().connect();

    // Run migrations
    safeLogger.info('Running database migrations...');
    await runMigrations();

    // Start server
    serverRef = app.listen(process.env.PORT || 3001, () => {
      safeLogger.info(`Server is running on port ${process.env.PORT || 3001}`);
      safeLogger.info(`Environment: ${process.env.NODE_ENV || 'development'}`);
    });
    return serverRef;
  } catch (error) {
    safeLogger.error('Failed to start server:', error);
    // Throw instead of process.exit so tests can handle failures
    throw error;
  }
}

// Graceful shutdown
export async function shutdown() {
  safeLogger.info('Shutting down gracefully');
  if (isShuttingDown && shutdownPromise) {
    return shutdownPromise;
  }

  isShuttingDown = true;
  shutdownPromise = (async () => {
    // Close HTTP server if running
    if (serverRef) {
      await new Promise<void>((resolve, reject) => {
        let closeTimeout: NodeJS.Timeout | null = null;

        const onClose = (err?: Error) => {
          if (closeTimeout) {
            clearTimeout(closeTimeout);
            closeTimeout = null;
          }
          if (err) {
            safeLogger.error('Error closing server:', err);
            reject(err);
            return;
          }
          serverRef = null;
          resolve();
        };

        serverRef!.close(onClose);

        // Safety: force resolve if close hangs (5s)
        closeTimeout = setTimeout(() => {
          try {
            /* istanbul ignore next */
            safeLogger.warn('Server close timed out after 5s; continuing with DB close');
          } catch (e) {
            // swallow any logging errors
          }
          serverRef = null;
          resolve();
        }, 5000);
      });
    }

    await DatabaseManager.getInstance().close();
    isShuttingDown = false; // Reset after successful shutdown
    shutdownPromise = null; // Reset after successful shutdown
  })();

  return shutdownPromise;
}

if (require.main === module) {
  // When run directly, start the server and attach signal handlers that exit the process
  startServer().catch((err) => {
    safeLogger.error('Fatal error starting server:', err);
    process.exit(1);
  });

  process.on('SIGTERM', async () => {
    safeLogger.info('SIGTERM received, shutting down gracefully');
    await shutdown();
    process.exit(0);
  });

  process.on('SIGINT', async () => {
    safeLogger.info('SIGINT received, shutting down gracefully');
    await shutdown();
    process.exit(0);
  });
}

export default app;

