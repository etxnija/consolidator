"""FastAPI application for the Ingestion service.

Endpoints:
  POST /ingest/{entity_id}  — Upload a subsidiary Trial Balance CSV.

The endpoint:
  1. Validates entity_id resolves to a known entity in entity_metadata.
  2. Parses the CSV with Pandas.
  3. Maps each account code to GCoA via mapping.py.
  4. Persists mapped entries to ledger_entries via database.py.
  5. Returns an UploadSummary (mapped/unmapped counts).

Optional query parameter:
  period_id — UUID of a reporting period; if provided entries are tagged to that period.
"""

from __future__ import annotations

import pathlib
import uuid
from datetime import datetime, timezone
from typing import Optional

from contextlib import asynccontextmanager

from alembic import command as alembic_command
from alembic.config import Config as AlembicConfig
from fastapi import FastAPI, HTTPException, Query, UploadFile, status

from ..consolidation.router import router as consolidation_router
from ..entities.router import router as entities_router
from ..models import EntityMetadata, LedgerEntry, ReportingPeriod  # noqa: F401 — register ORM models
from ..periods.router import router as periods_router
from .database import commit_entries
from .mapping import map_trial_balance, parse_csv, split_records
from .models import UploadSummary

_ALEMBIC_INI = pathlib.Path(__file__).parent.parent / "alembic.ini"


@asynccontextmanager
async def lifespan(app: FastAPI):
    cfg = AlembicConfig(str(_ALEMBIC_INI))
    alembic_command.upgrade(cfg, "head")
    yield


app = FastAPI(
    lifespan=lifespan,
    title="Consolidator Ingestion Service",
    description="Accepts subsidiary Trial Balance CSVs and maps them to GCoA.",
    version="0.2.0",
)

app.include_router(entities_router)
app.include_router(periods_router)
app.include_router(consolidation_router)


@app.get("/health", status_code=status.HTTP_200_OK)
async def health() -> dict:
    return {"status": "ok"}


@app.post(
    "/ingest/{entity_id}",
    response_model=UploadSummary,
    status_code=status.HTTP_200_OK,
    summary="Upload a Trial Balance CSV for a subsidiary",
)
async def ingest_trial_balance(
    entity_id: str,
    file: UploadFile,
    period_id: Optional[uuid.UUID] = Query(
        None,
        description="Tag these entries to a specific reporting period",
    ),
) -> UploadSummary:
    """Accept a CSV Trial Balance for *entity_id* and commit mapped entries.

    The CSV must have at minimum the columns `account_code` and `amount`.
    An optional `description` column is also recognised.

    Pass `period_id` to associate entries with a reporting period.

    Returns an UploadSummary with mapped/unmapped counts.
    """
    content = await file.read()
    if not content:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Uploaded file is empty",
        )

    try:
        df = parse_csv(content)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    ingestion_ts = datetime.now(timezone.utc)
    records = map_trial_balance(
        entity_id=entity_id,
        df=df,
        ingestion_timestamp=ingestion_ts,
        extra_metadata={"source_filename": file.filename or ""},
    )

    entries, unmapped_codes = split_records(records)

    try:
        committed = commit_entries(entries, entity_name=entity_id, period_id=period_id)
    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail=str(exc),
        ) from exc

    return UploadSummary(
        entity_id=entity_id,
        total_rows=len(records),
        mapped_count=len(entries),
        unmapped_count=len(unmapped_codes),
        unmapped_codes=unmapped_codes,
        entries_committed=committed,
    )
