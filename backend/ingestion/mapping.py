"""CSV-to-GCoA mapping logic for the Ingestion service.

Responsibilities:
  1. Parse a Trial Balance CSV (via Pandas).
  2. Map each local account code to a GCoA account code.
  3. Build validated LedgerEntry objects for mapped rows.
  4. Return a list of MappingRecord objects (mapped + unmapped).

Expected CSV columns (case-insensitive, whitespace-stripped):
  account_code  — subsidiary-local account code
  amount        — monetary amount (positive = debit, negative = credit)
  description   — optional human-readable label

Example:
  account_code,amount,description
  1000,50000.00,Cash
  2000,-15000.00,Accounts Payable
  9999,1000.00,Unknown local account
"""

from __future__ import annotations

import io
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
from pydantic import ValidationError

from .gcoa_map import lookup
from .models import LedgerEntry, MappingRecord, TrialBalanceRow

# Columns we recognise in an uploaded CSV.
_REQUIRED_COLUMNS = {"account_code", "amount"}
_OPTIONAL_COLUMNS = {"description", "counterparty_entity_id", "subsidiary_entity_id"}
_ALL_COLUMNS = _REQUIRED_COLUMNS | _OPTIONAL_COLUMNS


def _normalise_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Lower-case and strip column names; raise if required columns are missing."""
    df.columns = [c.strip().lower() for c in df.columns]
    missing = _REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"CSV is missing required columns: {sorted(missing)}")
    # Add optional columns with defaults if absent.
    for col in _OPTIONAL_COLUMNS:
        if col not in df.columns:
            df[col] = ""
    return df


def parse_csv(content: bytes | str) -> pd.DataFrame:
    """Read and validate a Trial Balance CSV, returning a normalised DataFrame."""
    if isinstance(content, bytes):
        buf = io.BytesIO(content)
    else:
        buf = io.StringIO(content)

    try:
        df = pd.read_csv(buf, dtype=str)
    except Exception as exc:
        raise ValueError(f"Failed to parse CSV: {exc}") from exc

    if df.empty:
        raise ValueError("CSV contains no data rows")

    return _normalise_columns(df)


def _parse_row(row: pd.Series) -> Optional[TrialBalanceRow]:
    """Coerce a DataFrame row into a TrialBalanceRow; return None if invalid."""
    try:
        def _opt_str(key: str) -> Optional[str]:
            val = str(row.get(key, "")).strip()
            return val if val else None

        return TrialBalanceRow(
            account_code=str(row["account_code"]).strip(),
            amount=Decimal(str(row["amount"]).strip()),
            description=str(row.get("description", "")).strip(),
            counterparty_entity_id=_opt_str("counterparty_entity_id"),
            subsidiary_entity_id=_opt_str("subsidiary_entity_id"),
        )
    except (ValidationError, InvalidOperation):
        return None


def map_trial_balance(
    entity_id: str,
    df: pd.DataFrame,
    ingestion_timestamp: Optional[datetime] = None,
    extra_metadata: Optional[Dict[str, Any]] = None,
) -> List[MappingRecord]:
    """Map all rows of a Trial Balance DataFrame to GCoA codes.

    Args:
        entity_id: Subsidiary identifier (e.g. "SUBS_01").
        df: Normalised Trial Balance DataFrame from parse_csv().
        ingestion_timestamp: Timestamp to stamp on all LedgerEntry records.
            Defaults to UTC now.
        extra_metadata: Optional dict merged into each LedgerEntry.metadata.

    Returns:
        List of MappingRecord — one per valid CSV row.
        Rows with parse errors are skipped (not included in results).
        Rows that fail GCoA lookup have gcoa_code=None and entry=None.
    """
    ts = ingestion_timestamp or datetime.now(timezone.utc)
    base_meta: dict[str, Any] = {"entity_id": entity_id, **(extra_metadata or {})}

    records: list[MappingRecord] = []

    for _, raw_row in df.iterrows():
        tb_row = _parse_row(raw_row)
        if tb_row is None:
            # Skip rows that cannot be parsed at all.
            continue

        gcoa_code = lookup(entity_id, tb_row.account_code)

        if gcoa_code is None:
            records.append(MappingRecord(row=tb_row, gcoa_code=None, entry=None))
            continue

        extra: dict[str, Any] = {}
        if tb_row.counterparty_entity_id:
            extra["counterparty_entity_id"] = tb_row.counterparty_entity_id
        if tb_row.subsidiary_entity_id:
            extra["subsidiary_entity_id"] = tb_row.subsidiary_entity_id

        entry = LedgerEntry(
            timestamp=ts,
            entity_id=entity_id,
            account_code=gcoa_code,
            amount=tb_row.amount,
            is_elimination=False,
            metadata={
                **base_meta,
                "local_account_code": tb_row.account_code,
                "description": tb_row.description,
                **extra,
            },
        )
        records.append(MappingRecord(row=tb_row, gcoa_code=gcoa_code, entry=entry))

    return records


def split_records(
    records: List[MappingRecord],
) -> Tuple[List[LedgerEntry], List[str]]:
    """Partition mapping results into (committed entries, unmapped codes).

    Returns:
        entries: LedgerEntry objects ready to persist.
        unmapped_codes: Deduplicated list of local account codes with no GCoA match.
    """
    entries: list[LedgerEntry] = []
    unmapped_codes: list[str] = []
    seen_unmapped: set[str] = set()

    for rec in records:
        if rec.entry is not None:
            entries.append(rec.entry)
        else:
            code = rec.row.account_code
            if code not in seen_unmapped:
                unmapped_codes.append(code)
                seen_unmapped.add(code)

    return entries, unmapped_codes
