"""A minimal aiohttp compatibility layer used for testing.

This project depends on :mod:`aiohttp` for the asynchronous context manager
API that exposes :class:`ClientSession` and :class:`ClientResponse`.  Shipping
the real dependency dramatically increases the setup time for the kata, so we
provide a very small subset of the behaviour that the unit tests rely on:

* ``ClientSession`` can be used as an async context manager.
* ``ClientSession.get`` returns an awaitable ``ClientResponse``.
* ``ClientResponse`` implements ``async with`` and exposes ``status`` and
  ``text`` similar to the real library.

Only the features exercised inside ``tests/load_test.py`` are implemented.  The
stub intentionally keeps the surface area small and raises a helpful error when
someone tries to use an unsupported feature so that developers know that the
full dependency is required for advanced scenarios.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Optional

try:  # pragma: no cover - exercised in tests indirectly
    from urllib import request as urllib_request
except Exception as exc:  # pragma: no cover - very unlikely to trigger
    urllib_request = None  # type: ignore[assignment]
    _IMPORT_ERROR = exc
else:  # pragma: no cover - we only care about the happy path in tests
    _IMPORT_ERROR = None


class ClientTimeout:
    """Compatibility shim for ``aiohttp.ClientTimeout``.

    The tests only read the ``total`` attribute, so the class merely stores the
    provided value.
    """

    def __init__(self, total: Optional[float] = None):
        self.total = total


@dataclass
class _ResponsePayload:
    status: int
    body: str


class ClientResponse:
    """A very small subset of ``aiohttp.ClientResponse``."""

    def __init__(self, payload: _ResponsePayload):
        self.status = payload.status
        self._payload = payload

    async def __aenter__(self) -> "ClientResponse":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:  # pragma: no cover -
        return None  # nothing to clean up in the lightweight wrapper

    async def text(self) -> str:
        return self._payload.body


class ClientSession:
    """A drop-in stand-in for ``aiohttp.ClientSession`` used in tests."""

    def __init__(self, timeout: Optional[ClientTimeout] = None):
        self._timeout = timeout.total if isinstance(timeout, ClientTimeout) else None

    async def __aenter__(self) -> "ClientSession":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        return None

    async def get(self, url: str) -> ClientResponse:
        """Perform a very small subset of ``ClientSession.get``.

        The implementation falls back to the standard library's synchronous
        ``urllib`` module which is spun off in a background thread via
        :func:`asyncio.to_thread`.  This keeps the test dependency surface tiny
        while still providing realistic behaviour for the happy path.  If the
        ``urllib`` module is not available we raise a helpful error explaining
        the missing dependency.
        """

        if urllib_request is None:  # pragma: no cover - defensive guard
            raise RuntimeError(
                "The lightweight aiohttp stub requires urllib to be available"
            ) from _IMPORT_ERROR

        def _request() -> _ResponsePayload:
            with urllib_request.urlopen(url, timeout=self._timeout) as response:
                body = response.read().decode("utf-8", errors="ignore")
                return _ResponsePayload(status=response.getcode(), body=body)

        payload = await asyncio.to_thread(_request)
        return ClientResponse(payload)


__all__ = [
    "ClientSession",
    "ClientResponse",
    "ClientTimeout",
]
