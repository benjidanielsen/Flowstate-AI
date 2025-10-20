from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.status import HTTP_429_TOO_MANY_REQUESTS
import time
import asyncio

class RateLimiterMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_requests: int = 100, window_seconds: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        # Store data in the form {client_ip: [timestamps]}
        self.requests = {}
        self.lock = asyncio.Lock()

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        now = time.monotonic()

        async with self.lock:
            if client_ip not in self.requests:
                self.requests[client_ip] = []

            # Remove timestamps outside the window
            window_start = now - self.window_seconds
            self.requests[client_ip] = [ts for ts in self.requests[client_ip] if ts > window_start]

            if len(self.requests[client_ip]) >= self.max_requests:
                retry_after = self.requests[client_ip][0] + self.window_seconds - now
                headers = {"Retry-After": str(int(retry_after))}
                raise HTTPException(
                    status_code=HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Rate limit exceeded. Try again in {int(retry_after)} seconds.",
                    headers=headers
                )

            self.requests[client_ip].append(now)

        response = await call_next(request)
        return response
