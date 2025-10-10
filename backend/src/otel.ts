import { NodeSDK } from '@opentelemetry/sdk-node';
import { getNodeAutoInstrumentations } from '@opentelemetry/auto-instrumentations-node';
import { OTLPTraceExporter } from '@opentelemetry/exporter-trace-otlp-grpc';
import { Resource } from '@opentelemetry/resources';
import { SemanticResourceAttributes } from '@opentelemetry/semantic-conventions';

const exporter = new OTLPTraceExporter({
  url: process.env.OTEL_EXPORTER_OTLP_ENDPOINT || 'http://otel-collector:4317',
});

const sdk = new NodeSDK({
  resource: new Resource({
    [SemanticResourceAttributes.SERVICE_NAME]: 'flowstate-backend',
  }),
  traceExporter: exporter,
  instrumentations: [getNodeAutoInstrumentations()],
});

let started = false;

export async function startOtel() {
  if (started) {
    return;
  }
  try {
    await sdk.start();
    started = true;
  } catch (error) {
    console.error('OTEL start failed', error);
  }

  const shutdown = async () => {
    try {
      await sdk.shutdown();
    } catch (error) {
      console.error('OTEL shutdown failed', error);
    }
  };

  process.once('SIGTERM', shutdown);
  process.once('SIGINT', shutdown);
}
