import { diag, DiagConsoleLogger, DiagLogLevel, trace } from '@opentelemetry/api';
import { Resource } from '@opentelemetry/resources';
import { SemanticResourceAttributes } from '@opentelemetry/semantic-conventions';
import { NodeSDK } from '@opentelemetry/sdk-node';
import { OTLPTraceExporter } from '@opentelemetry/exporter-trace-otlp-http';
import logger from './logger';
import { safeLogger } from './piiRedaction';

// Configure diagnostic logger
const logLevel = (process.env.OTEL_LOG_LEVEL || 'info').toUpperCase() as keyof typeof DiagLogLevel;
const resolvedLevel = DiagLogLevel[logLevel] ?? DiagLogLevel.INFO;
diag.setLogger(new DiagConsoleLogger(), resolvedLevel);

const serviceName = process.env.OTEL_SERVICE_NAME || 'flowstate-ai-backend';
const collectorEndpoint = process.env.OTEL_EXPORTER_OTLP_ENDPOINT || process.env.OTEL_COLLECTOR_ENDPOINT || 'http://localhost:4318/v1/traces';
const otelEnabled = (process.env.OTEL_ENABLED || 'true').toLowerCase() !== 'false';

let sdk: NodeSDK | null = null;

if (otelEnabled) {
  try {
    const traceExporter = new OTLPTraceExporter({
      url: collectorEndpoint,
    });

    sdk = new NodeSDK({
      resource: new Resource({
        [SemanticResourceAttributes.SERVICE_NAME]: serviceName,
        [SemanticResourceAttributes.DEPLOYMENT_ENVIRONMENT]: process.env.NODE_ENV || 'development',
      }),
      traceExporter,
    });

    sdk.start().then(() => {
      safeLogger.info(`OpenTelemetry SDK initialized for service: ${serviceName}`);
    });

    process.once('beforeExit', async () => {
      try {
        await sdk?.shutdown();
      } catch (error) {
        logger.warn('Error shutting down OpenTelemetry SDK', error as Error);
      }
    });
  } catch (error) {
    safeLogger.error('Error initializing OpenTelemetry SDK', error);
  }
} else {
  safeLogger.info('OpenTelemetry tracing is disabled via OTEL_ENABLED flag.');
}

export const tracer = trace.getTracer(serviceName);
