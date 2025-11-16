import { NodeTracerProvider } from '@opentelemetry/sdk-trace-node';
import { SimpleSpanProcessor } from '@opentelemetry/sdk-trace-base';
import { OTLPTraceExporter } from '@opentelemetry/exporter-trace-otlp-http';
import { resourceFromAttributes } from '@opentelemetry/resources';
import { SemanticResourceAttributes } from '@opentelemetry/semantic-conventions';
import { safeLogger } from './piiRedaction';

const serviceName = process.env.OTEL_SERVICE_NAME || 'flowstate-ai-backend';
const collectorEndpoint = process.env.OTEL_COLLECTOR_ENDPOINT || 'http://localhost:4318/v1/traces';

const provider = new NodeTracerProvider({
  resource: resourceFromAttributes({
    [SemanticResourceAttributes.SERVICE_NAME]: serviceName,
  }),
});

const exporter = new OTLPTraceExporter({
  url: collectorEndpoint,
});

const typedProvider = provider as unknown as { addSpanProcessor?: (processor: SimpleSpanProcessor) => void };
if (typeof typedProvider.addSpanProcessor === 'function') {
  typedProvider.addSpanProcessor(new SimpleSpanProcessor(exporter));
} else {
  safeLogger.warn('OpenTelemetry span processor not available; traces will not be exported.');
}
provider.register();

safeLogger.info(`OpenTelemetry Tracer initialized for service: ${serviceName}, exporting to: ${collectorEndpoint}`);

export const tracer = provider.getTracer(serviceName);

