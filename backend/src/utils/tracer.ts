import { safeLogger } from './piiRedaction';

type TracerLike = {
  startSpan: (...args: unknown[]) => { end: () => void };
  startActiveSpan?: (...args: unknown[]) => unknown;
} | null;

export let tracer: TracerLike = null;

const tracingEnabled = process.env.ENABLE_TRACING === 'true';

if (tracingEnabled) {
  try {
    // eslint-disable-next-line @typescript-eslint/no-var-requires
    const { NodeTracerProvider } = require('@opentelemetry/sdk-trace-node');
    // eslint-disable-next-line @typescript-eslint/no-var-requires
    const { SimpleSpanProcessor } = require('@opentelemetry/sdk-trace-base');
    // eslint-disable-next-line @typescript-eslint/no-var-requires
    const { OTLPTraceExporter } = require('@opentelemetry/exporter-trace-otlp-http');
    // eslint-disable-next-line @typescript-eslint/no-var-requires
    const { Resource } = require('@opentelemetry/resources');
    // eslint-disable-next-line @typescript-eslint/no-var-requires
    const { SemanticResourceAttributes } = require('@opentelemetry/semantic-conventions');

    const serviceName = process.env.OTEL_SERVICE_NAME || 'flowstate-ai-backend';
    const collectorEndpoint = process.env.OTEL_COLLECTOR_ENDPOINT || 'http://localhost:4318/v1/traces';

    const provider = new NodeTracerProvider({
      resource: new Resource({
        [SemanticResourceAttributes.SERVICE_NAME]: serviceName,
      }),
    });

    const exporter = new OTLPTraceExporter({
      url: collectorEndpoint,
    });

    provider.addSpanProcessor(new SimpleSpanProcessor(exporter));
    provider.register();

    tracer = provider.getTracer(serviceName);
    safeLogger.info(`OpenTelemetry tracing enabled for ${serviceName}, exporting to ${collectorEndpoint}`);
  } catch (error) {
    tracer = null;
    safeLogger.warn('OpenTelemetry tracer initialization skipped due to missing dependencies.', error);
  }
} else {
  safeLogger.debug('OpenTelemetry tracing disabled. Set ENABLE_TRACING=true to enable instrumentation.');
}

