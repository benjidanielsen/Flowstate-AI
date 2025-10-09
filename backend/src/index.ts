import express, { Request, Response, NextFunction } from 'express';
import bodyParser from 'body-parser';

import helmet from 'helmet';
import http from 'http';
import routes from './routes';
import performanceMiddleware from './middleware/performanceMiddleware';
import DatabaseManager from './database';
import { runMigrations } from './database/migrate';
import logger from './utils/logger';

dotenv.config();

const app = express();

let serverRef: http.Server | null = null;
let isShuttingDown = false;
let shutdownPromise: Promise<void> | null = null;

// Middleware
app.use(helmet());
app.use(cors());
app.use(bodyParser.json());
app.use(express.urlencoded({ extended: true }));
app.use(performanceMiddleware);

// Routes
app.use('/api', routes);

// Global Error Handling Middleware
app.use((err: Error, req: Request, res: Response, next: NextFunction) => {
  logger.error(`Unhandled error: ${err.message}`, { stack: err.stack, path: req.path, method: req.method });
  res.status(500).json({ message: 'Internal Server Error', error: err.message });
});

// 404 handler
app.use((req: Request, res: Response) => {
  res.status(404).json({ error: 'Route not found' });
});

export function createApp() {
  return app;
}

export async function startServer() {
  try {
    // Initialize database
    logger.info('Connecting to database...');
    await DatabaseManager.getInstance().connect();

    // Run migrations
    logger.info('Running database migrations...');
    await runMigrations();

    // Start server
    serverRef = app.listen(process.env.PORT || 3001, () => {
      logger.info(`Server is running on port ${process.env.PORT || 3001}`);
      logger.info(`Environment: ${process.env.NODE_ENV || 'development'}`);
    });
    return serverRef;
  } catch (error) {
    logger.error('Failed to start server:', error);
    // Throw instead of process.exit so tests can handle failures
    throw error;
  }
}

// Graceful shutdown
export async function shutdown() {
  logger.info('Shutting down gracefully');
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
            logger.error('Error closing server:', err);
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
            logger.warn('Server close timed out after 5s; continuing with DB close');
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
    logger.error('Fatal error starting server:', err);
    process.exit(1);
  });

  process.on('SIGTERM', async () => {
    logger.info('SIGTERM received, shutting down gracefully');
    await shutdown();
    process.exit(0);
  });

  process.on('SIGINT', async () => {
    logger.info('SIGINT received, shutting down gracefully');
    await shutdown();
    process.exit(0);
  });
}

export default app;

