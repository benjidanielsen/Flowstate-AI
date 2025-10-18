"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.tracer = void 0;
const api_1 = require("@opentelemetry/api");
const piiRedaction_1 = require("./piiRedaction");
// For troubleshooting, set the log level to DiagLogLevel.DEBUG
api_1.diag.setLogger(new api_1.DiagConsoleLogger(), api_1.DiagLogLevel.INFO);
const serviceName = process.env.OTEL_SERVICE_NAME || 'flowstate-ai-backend';
// const collectorEndpoint = process.env.OTEL_COLLECTOR_ENDPOINT || 'http://localhost:4318/v1/traces';
// Temporarily commenting out OpenTelemetry initialization due to persistent TypeScript errors.
// We will revisit this integration once the core backend is stable.
// import { NodeSDK } from '@opentelemetry/sdk-node';
// import { OTLPTraceExporter } from '@opentelemetry/exporter-trace-otlp-http';
// import { Resource } from '@opentelemetry/resources';
// import { SemanticResourceAttributes } from '@opentelemetry/semantic-conventions';
// const sdk = new NodeSDK({
//   resource: new Resource({
//     [SemanticResourceAttributes.SERVICE_NAME]: serviceName,
//   }),
//   traceExporter: new OTLPTraceExporter({
//     url: collectorEndpoint,
//   }),
//   // instrumentations: [getNodeAutoInstrumentations()], // Enable auto-instrumentations if needed
// });
// // Initialize the SDK and register it
// try {
//   sdk.start();
//   safeLogger.info(`OpenTelemetry SDK initialized for service: ${serviceName}, exporting to: ${collectorEndpoint}`);
// } catch (error) {
//   safeLogger.error('Error initializing OpenTelemetry SDK', error);
// }
// Export a dummy tracer for now
exports.tracer = api_1.trace.getTracer(serviceName);
piiRedaction_1.safeLogger.warn('OpenTelemetry initialization is temporarily disabled. Tracing will not be active.');
//# sourceMappingURL=tracer.js.map