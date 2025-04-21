from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
from src.core.metrics import request_counts

class RequestCounterMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        if response.status_code == 200:
            request_counts["requests_success"] += 1
        elif 400 <= response.status_code < 500:
            request_counts["requests_malformed"] += 1
        elif 500 <= response.status_code < 600:
            request_counts["requests_bad"] += 1
        return response