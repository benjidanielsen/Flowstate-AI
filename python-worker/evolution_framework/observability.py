"""Observability helpers for the evolution framework."""

import logging
import os
from typing import Dict, Any, Optional

from logging_loki import LokiHandler
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

_SERVICE_NAME = os.getenv("PY_SERVICE_NAME", "flowstate-ai-python-worker")
_LOKI_URL = os.getenv("LOKI_URL")
_OTEL_ENDPOINT = os.getenv("OTEL_COLLECTOR_ENDPOINT", "http://localhost:4318/v1/traces")
_tracer_provider: Optional[TracerProvider] = None


def _configure_logging() -> None:
    root_logger = logging.getLogger()
    if _LOKI_URL and not any(isinstance(handler, LokiHandler) for handler in root_logger.handlers):
        handler = LokiHandler(
            url=f"{_LOKI_URL.rstrip('/')}/loki/api/v1/push",
            tags={"service": _SERVICE_NAME, "environment": os.getenv("ENVIRONMENT", "development")},
            version="1",
        )
        root_logger.addHandler(handler)


def _configure_tracer() -> None:
    global _tracer_provider
    if _tracer_provider:
        return
    resource = Resource.create({"service.name": _SERVICE_NAME})
    _tracer_provider = TracerProvider(resource=resource)
    exporter = OTLPSpanExporter(endpoint=_OTEL_ENDPOINT)
    _tracer_provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(_tracer_provider)


def init_observability() -> trace.Tracer:
    logging.basicConfig(level=os.getenv("PY_LOG_LEVEL", "INFO"))
    _configure_logging()
    _configure_tracer()
    return trace.get_tracer(_SERVICE_NAME)


def record_agent_action(action: str, correlation_id: Optional[str] = None, payload: Optional[Dict[str, Any]] = None) -> str:
    tracer = init_observability()
    with tracer.start_as_current_span(action) as span:
        if correlation_id:
            span.set_attribute("correlation.id", correlation_id)
        for key, value in (payload or {}).items():
            span.set_attribute(f"action.{key}", value)
        logging.getLogger("agent_actions").info(
            "Agent action recorded",
            extra={"correlation_id": correlation_id, "action": action, "payload": payload or {}},
        )
        return format(span.get_span_context().trace_id, "032x")
