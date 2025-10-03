"""Shared error-handling utilities for the autonomous Project Manager AI.

This module provides small, dependency-free helpers to ensure that
exceptional paths are logged consistently and, when appropriate, retried
using a configurable backoff policy.  The implementation is intentionally
lightweight so it can be reused across the various MANUS coordination
components without introducing new runtime dependencies.
"""

from __future__ import annotations

import logging
import time
from typing import Any, Callable, Dict, Optional, Tuple, TypeVar

T = TypeVar("T")


def _coerce_context(context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Return a shallow copy of the supplied context dictionary."""

    if context is None:
        return {}
    return {**context}


def log_exception(
    logger: logging.Logger,
    error: BaseException,
    *,
    context: Optional[Dict[str, Any]] = None,
    message: Optional[str] = None,
    level: int = logging.ERROR,
) -> Dict[str, Any]:
    """Log an exception with structured metadata and return the payload."""

    payload: Dict[str, Any] = {
        "event": "exception",
        "error_type": type(error).__name__,
        "error_message": str(error),
    }

    if message:
        payload["message"] = message

    payload.update(_coerce_context(context))

    if logger.isEnabledFor(level):
        logger.log(level, payload, exc_info=True)

    return payload


def log_and_raise(
    logger: logging.Logger,
    error: BaseException,
    *,
    context: Optional[Dict[str, Any]] = None,
    message: Optional[str] = None,
) -> None:
    """Log the provided exception and re-raise it."""

    log_exception(logger, error, context=context, message=message)
    raise error


def retry(
    operation: Callable[[], T],
    *,
    retries: int = 3,
    initial_delay: float = 0.5,
    backoff_factor: float = 2.0,
    retry_exceptions: Tuple[type[BaseException], ...] = (Exception,),
    logger: Optional[logging.Logger] = None,
    context: Optional[Dict[str, Any]] = None,
) -> T:
    """Execute ``operation`` and retry on failure with exponential backoff."""

    attempt = 0
    attempt_context = _coerce_context(context)

    while True:
        try:
            return operation()
        except retry_exceptions as exc:  # pragma: no cover - thin wrapper
            attempt += 1
            attempt_context.update({"attempt": attempt})

            if attempt > retries:
                if logger is not None:
                    log_exception(
                        logger,
                        exc,
                        context=attempt_context,
                        message="Max retries exceeded",
                    )
                raise

            delay = initial_delay * (backoff_factor ** (attempt - 1))

            if logger is not None:
                logger.warning(
                    {
                        "event": "retry",
                        "message": "Retrying operation after failure",
                        "delay_seconds": round(delay, 2),
                        **attempt_context,
                    }
                )

            time.sleep(delay)


def guard(
    logger: logging.Logger,
    *,
    context: Optional[Dict[str, Any]] = None,
    reraise: bool = False,
) -> Callable[[Callable[..., T]], Callable[..., Optional[T]]]:
    """Decorator to wrap a function and capture any raised exceptions."""

    def decorator(func: Callable[..., T]) -> Callable[..., Optional[T]]:
        def wrapper(*args: Any, **kwargs: Any) -> Optional[T]:
            try:
                return func(*args, **kwargs)
            except Exception as exc:  # pragma: no cover - passthrough wrapper
                log_exception(
                    logger,
                    exc,
                    context={"guarded_function": func.__name__, **_coerce_context(context)},
                )
                if reraise:
                    raise
                return None

        return wrapper

    return decorator


__all__ = ["guard", "log_and_raise", "log_exception", "retry"]
