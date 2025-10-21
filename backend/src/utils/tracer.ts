import { safeLogger } from './piiRedaction';

const serviceName = process.env.OTEL_SERVICE_NAME || 'flowstate-ai-backend';
const collectorEndpoint = process.env.OTEL_COLLECTOR_ENDPOINT || 'http://localhost:4318/v1/traces';

let tracer: unknown = null;

try {
  // Dynamically require OpenTelemetry dependencies so the backend can run without them in local/test environments
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
  safeLogger.info(`OpenTelemetry Tracer initialized for service: ${serviceName}, exporting to: ${collectorEndpoint}`);
} catch (error) {
  tracer = null;
  safeLogger.warn('OpenTelemetry dependencies unavailable; tracing disabled.', error);
}

export { tracer };

