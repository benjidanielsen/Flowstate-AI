import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import dotenv from 'dotenv';
import DatabaseManager from './database';
import { runMigrations } from './database/migrate';
import routes from './routes';
import http from 'http';

dotenv.config();

const app = express();

let serverRef: http.Server | null = null;
let isShuttingDown = false;
let shutdownPromise: Promise<void> | null = null;

// Middleware
app.use(helmet());
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Routes
app.use('/api', routes);

// Error handling middleware
app.use((err: Error, req: express.Request, res: express.Response, _next: express.NextFunction) => {
  console.error(err.stack);
  res.status(500).json({ error: 'Something broke!' });
});

// 404 handler
app.use((req: express.Request, res: express.Response) => {
  res.status(404).json({ error: 'Route not found' });
});

export function createApp() {
  return app;
}

export async function startServer() {
  try {
    // Initialize database
    console.log('Connecting to database...');
    await DatabaseManager.getInstance().connect();

    // Run migrations
    console.log('Running database migrations...');
    await runMigrations();

    // Start server
    serverRef = app.listen(process.env.PORT || 3001, () => {
      console.log(`Server is running on port ${process.env.PORT || 3001}`);
      console.log(`Environment: ${process.env.NODE_ENV || 'development'}`);
    });
    return serverRef;
  } catch (error) {
    console.error('Failed to start server:', error);
    // Throw instead of process.exit so tests can handle failures
    throw error;
  }
}

// Graceful shutdown
export async function shutdown() {
  console.log('Shutting down gracefully');
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
            console.error('Error closing server:', err);
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
            console.warn('Server close timed out after 5s; continuing with DB close');
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
    console.error('Fatal error starting server:', err);
    process.exit(1);
  });

  process.on('SIGTERM', async () => {
    console.log('SIGTERM received, shutting down gracefully');
    await shutdown();
    process.exit(0);
  });

  process.on('SIGINT', async () => {
    console.log('SIGINT received, shutting down gracefully');
    await shutdown();
    process.exit(0);
  });
}

export default app;

