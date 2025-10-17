"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.tracer = void 0;
const sdk_trace_node_1 = require("@opentelemetry/sdk-trace-node");
const sdk_trace_base_1 = require("@opentelemetry/sdk-trace-base");
const exporter_trace_otlp_http_1 = require("@opentelemetry/exporter-trace-otlp-http");
const resources_1 = require("@opentelemetry/resources");
const semantic_conventions_1 = require("@opentelemetry/semantic-conventions");
const piiRedaction_1 = require("./piiRedaction");
const serviceName = process.env.OTEL_SERVICE_NAME || 'flowstate-ai-backend';
const collectorEndpoint = process.env.OTEL_COLLECTOR_ENDPOINT || 'http://localhost:4318/v1/traces';
const provider = new sdk_trace_node_1.NodeTracerProvider({
    resource: new resources_1.Resource({
        [semantic_conventions_1.SemanticResourceAttributes.SERVICE_NAME]: serviceName,
    }),
});
const exporter = new exporter_trace_otlp_http_1.OTLPTraceExporter({
    url: collectorEndpoint,
});
provider.addSpanProcessor(new sdk_trace_base_1.SimpleSpanProcessor(exporter));
provider.register();
piiRedaction_1.safeLogger.info(`OpenTelemetry Tracer initialized for service: ${serviceName}, exporting to: ${collectorEndpoint}`);
exports.tracer = provider.getTracer(serviceName);
//# sourceMappingURL=tracer.js.map