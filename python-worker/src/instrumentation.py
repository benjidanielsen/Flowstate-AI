"""Instrumentation utilities for the Python worker service."""

from __future__ import annotations

import os
import time

from fastapi import FastAPI
from prometheus_client import Counter, Histogram
from prometheus_fastapi_instrumentator import Instrumentator
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.semconv.resource import ResourceAttributes

OTEL_ENABLED = os.getenv("OTEL_ENABLED", "true").lower() != "false"
_OTEL_TRACER_INITIALIZED = False
_TRACER_PROVIDER: TracerProvider | None = None

BACKEND_REQUEST_COUNTER = Counter(
    "worker_backend_requests_total",
    "Total backend HTTP requests executed by the worker",
    labelnames=("operation", "status"),
)
BACKEND_REQUEST_DURATION = Histogram(
    "worker_backend_request_duration_seconds",
    "Latency distribution for backend HTTP calls",
    labelnames=("operation", "status"),
    buckets=(0.05, 0.1, 0.25, 0.5, 1.0, 2.0, 5.0),
)
WORKFLOW_COUNTER = Counter(
    "worker_agent_workflows_total",
    "Workflow executions coordinated by specialized agents",
    labelnames=("workflow", "status"),
)


def _setup_tracing() -> TracerProvider | None:
    global _OTEL_TRACER_INITIALIZED, _TRACER_PROVIDER

    if not OTEL_ENABLED or _OTEL_TRACER_INITIALIZED:
        return _TRACER_PROVIDER

    endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4318/v1/traces")
    service_name = os.getenv("OTEL_SERVICE_NAME", "flowstate-ai-worker")

    resource = Resource(
        attributes={
            ResourceAttributes.SERVICE_NAME: service_name,
            ResourceAttributes.DEPLOYMENT_ENVIRONMENT: os.getenv("DEPLOY_ENV", "development"),
        }
    )

    provider = TracerProvider(resource=resource)
    processor = BatchSpanProcessor(OTLPSpanExporter(endpoint=endpoint))
    provider.add_span_processor(processor)
    trace.set_tracer_provider(provider)
    _TRACER_PROVIDER = provider
    _OTEL_TRACER_INITIALIZED = True
    return provider


def setup_observability(app: FastAPI) -> None:
    """Initialize tracing and metrics instrumentation for the FastAPI app."""

    provider = _setup_tracing()
    if provider:
        FastAPIInstrumentor().instrument_app(app, tracer_provider=provider)
    else:
        FastAPIInstrumentor().instrument_app(app)
    Instrumentator().instrument(app).expose(app, include_in_schema=False, should_gzip=True)


def track_backend_call(operation: str, status: str, start_time: float) -> None:
    duration = max(time.perf_counter() - start_time, 0.0)
    BACKEND_REQUEST_COUNTER.labels(operation=operation, status=status).inc()
    BACKEND_REQUEST_DURATION.labels(operation=operation, status=status).observe(duration)


def record_workflow_status(workflow: str, status: str) -> None:
    WORKFLOW_COUNTER.labels(workflow=workflow, status=status).inc()


__all__ = [
    "setup_observability",
    "track_backend_call",
    "record_workflow_status",
    "BACKEND_REQUEST_COUNTER",
    "BACKEND_REQUEST_DURATION",
    "WORKFLOW_COUNTER",
]
