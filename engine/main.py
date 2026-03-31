"""Engine service — exposes the IFRS 10 calculator via HTTP."""

import os
import uuid
from datetime import datetime, timezone
from typing import List

import structlog
from fastapi import FastAPI, Request
from pydantic import BaseModel
from starlette.middleware.base import BaseHTTPMiddleware

structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ],
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=True,
)

log = structlog.get_logger(__name__)


class _RequestIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(request_id=request_id)
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response

from .calculator import IfrsCalculator
from .models import EliminationEntry, EntityNode, LedgerEntrySnapshot

_prod = os.getenv("APP_ENV") == "production" or os.getenv("DISABLE_DOCS", "").lower() == "true"

app = FastAPI(
    title="Consolidator Engine",
    description="IFRS 10 stateless consolidation calculator.",
    version="0.1.0",
    docs_url=None if _prod else "/docs",
    redoc_url=None if _prod else "/redoc",
    openapi_url=None if _prod else "/openapi.json",
)

app.add_middleware(_RequestIdMiddleware)


class ConsolidationRequest(BaseModel):
    entries: List[LedgerEntrySnapshot]
    entities: List[EntityNode]
    as_of: datetime = None


class ConsolidationResponse(BaseModel):
    eliminations: List[EliminationEntry]
    count: int


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/consolidate", response_model=ConsolidationResponse)
async def consolidate(req: ConsolidationRequest) -> ConsolidationResponse:
    """Run IFRS 10 elimination logic on the provided ledger snapshot."""
    as_of = req.as_of or datetime.now(timezone.utc)
    log.info("consolidation_started", entries=len(req.entries), entities=len(req.entities))
    eliminations = IfrsCalculator.eliminate(req.entries, req.entities, as_of=as_of)
    log.info("consolidation_complete", eliminations=len(eliminations))
    return ConsolidationResponse(eliminations=eliminations, count=len(eliminations))
