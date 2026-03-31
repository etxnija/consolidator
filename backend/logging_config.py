"""Structured logging configuration using structlog.

Every log line carries a request_id correlation ID injected by the
RequestIdMiddleware. Use `get_logger()` in any module to get a
pre-configured logger that includes the request_id automatically.

Usage:
    from backend.logging_config import get_logger
    log = get_logger(__name__)
    log.info("entity_created", entity_id=str(entity_id), name=name)
"""
from __future__ import annotations

import logging
import sys
import uuid

import structlog
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

# ---------------------------------------------------------------------------
# structlog configuration
# ---------------------------------------------------------------------------

structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(file=sys.stdout),
    cache_logger_on_first_use=True,
)


def get_logger(name: str = __name__) -> structlog.BoundLogger:
    """Return a structlog logger bound to *name*."""
    return structlog.get_logger(name)


# ---------------------------------------------------------------------------
# Request ID middleware
# ---------------------------------------------------------------------------

class RequestIdMiddleware(BaseHTTPMiddleware):
    """Inject a unique request_id into structlog context for every request.

    The request_id is:
    - Generated as a UUID4 if not present in the incoming X-Request-ID header
    - Bound into structlog's context vars so every log line in the request
      automatically includes it
    - Returned in the X-Request-ID response header for client-side correlation
    """

    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(
            request_id=request_id,
            method=request.method,
            path=request.url.path,
        )
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response
