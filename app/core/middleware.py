import uuid
import structlog
from structlog.contextvars import clear_contextvars, bind_contextvars
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        clear_contextvars()
        request_id = str(uuid.uuid4())
        bind_contextvars(request_id=request_id, path=request.url.path)

        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response