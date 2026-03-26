"""FastAPI application for the Ingestion service.

Endpoints:
  POST /ingest/{entity_id}  — Upload a subsidiary Trial Balance CSV.

The endpoint:
  1. Validates entity_id is a known subsidiary.
  2. Parses the CSV with Pandas.
  3. Maps each account code to GCoA via mapping.py.
  4. Persists mapped entries to ledger_entries via database.py.
  5. Returns an UploadSummary (mapped/unmapped counts).
"""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException, UploadFile, status

from .database import commit_entries
from .mapping import map_trial_balance, parse_csv, split_records
from .models import UploadSummary

# The 10 supported subsidiaries.
KNOWN_SUBSIDIARIES = {
    "SUBS_01",
    "SUBS_02",
    "SUBS_03",
    "SUBS_04",
    "SUBS_05",
    "SUBS_06",
    "SUBS_07",
    "SUBS_08",
    "SUBS_09",
    "SUBS_10",
}

app = FastAPI(
    title="Consolidator Ingestion Service",
    description="Accepts subsidiary Trial Balance CSVs and maps them to GCoA.",
    version="0.1.0",
)


@app.post(
    "/ingest/{entity_id}",
    response_model=UploadSummary,
    status_code=status.HTTP_200_OK,
    summary="Upload a Trial Balance CSV for a subsidiary",
)
async def ingest_trial_balance(
    entity_id: str,
    file: UploadFile,
) -> UploadSummary:
    """Accept a CSV Trial Balance for *entity_id* and commit mapped entries.

    The CSV must have at minimum the columns `account_code` and `amount`.
    An optional `description` column is also recognised.

    Returns an UploadSummary with mapped/unmapped counts.
    """
    if entity_id not in KNOWN_SUBSIDIARIES:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Unknown subsidiary: {entity_id!r}. "
                   f"Valid values: {sorted(KNOWN_SUBSIDIARIES)}",
        )

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
        committed = commit_entries(entries, entity_name=entity_id)
    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
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
