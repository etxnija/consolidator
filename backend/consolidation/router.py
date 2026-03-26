"""Consolidation orchestration and reporting endpoints.

Endpoints:
  POST /consolidate/{period_id}   — run IFRS 10 consolidation, persist eliminations
  GET  /report/{period_id}        — return consolidated financial statements
"""

from __future__ import annotations

import os
import uuid
from collections import defaultdict
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Dict, List, Optional

import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import EntityMetadata, LedgerEntry, ReportingPeriod

router = APIRouter(tags=["consolidation"])

ENGINE_URL = os.environ.get("ENGINE_URL", "http://localhost:8001")

# ---------------------------------------------------------------------------
# GCoA classification maps for report formatting
# ---------------------------------------------------------------------------

# Account code prefix → financial statement section
_BS_ASSET_PREFIXES = ("1",)
_BS_LIABILITY_PREFIXES = ("2",)
_BS_EQUITY_PREFIXES = ("3", "EQUITY", "NCI_EQUITY")
_IS_REVENUE_PREFIXES = ("4", "INTERCO_REV")
_IS_COGS_PREFIXES = ("5", "INTERCO_COGS")
_IS_OPEX_PREFIXES = ("6", "7", "8")


def _classify(account_code: str) -> str:
    for prefix in _BS_ASSET_PREFIXES:
        if account_code.startswith(prefix):
            return "assets"
    for prefix in _BS_LIABILITY_PREFIXES:
        if account_code.startswith(prefix):
            return "liabilities"
    for prefix in _BS_EQUITY_PREFIXES:
        if account_code.startswith(prefix):
            return "equity"
    for prefix in _IS_REVENUE_PREFIXES:
        if account_code.startswith(prefix):
            return "revenue"
    for prefix in _IS_COGS_PREFIXES:
        if account_code.startswith(prefix):
            return "cogs"
    for prefix in _IS_OPEX_PREFIXES:
        if account_code.startswith(prefix):
            return "operating_expenses"
    return "other"


# ---------------------------------------------------------------------------
# Pydantic response schemas
# ---------------------------------------------------------------------------

class ConsolidationResult(BaseModel):
    period_id: uuid.UUID
    eliminations_created: int
    warnings: List[str]


class EliminationSummary(BaseModel):
    elimination_type: str
    entity_id: str
    account_code: str
    amount: str


class ConsolidatedReport(BaseModel):
    period: Dict[str, Any]
    balance_sheet: Dict[str, Dict[str, str]]
    income_statement: Dict[str, Dict[str, str]]
    eliminations_summary: List[EliminationSummary]
    warnings: List[str]


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _load_period(db: Session, period_id: uuid.UUID) -> ReportingPeriod:
    period = db.get(ReportingPeriod, period_id)
    if period is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Period not found")
    return period


def _submission_warnings(
    db: Session,
    period_id: uuid.UUID,
    entities: List[EntityMetadata],
) -> List[str]:
    """Return warnings for entities with no ledger entries in the period."""
    warnings: List[str] = []
    for entity in entities:
        count = (
            db.query(LedgerEntry)
            .filter(
                LedgerEntry.entity_id == entity.entity_id,
                LedgerEntry.period_id == period_id,
                LedgerEntry.is_elimination == False,  # noqa: E712
            )
            .count()
        )
        if count == 0:
            warnings.append(f"Entity {entity.name!r} ({entity.entity_id}) has not submitted for this period")
    return warnings


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@router.post(
    "/consolidate/{period_id}",
    response_model=ConsolidationResult,
    status_code=status.HTTP_200_OK,
)
def run_consolidation(period_id: uuid.UUID, db: Session = Depends(get_db)) -> ConsolidationResult:
    """Run IFRS 10 consolidation for a period.

    Steps:
    1. Load all ledger entries for the period.
    2. Load entity hierarchy.
    3. Call engine /consolidate.
    4. Persist returned elimination entries to ledger_entries.
    5. Return summary with any submission warnings.
    """
    period = _load_period(db, period_id)

    # Load entries for this period (non-elimination only — eliminations are idempotently re-created)
    entries = (
        db.query(LedgerEntry)
        .filter(
            LedgerEntry.period_id == period_id,
            LedgerEntry.is_elimination == False,  # noqa: E712
        )
        .all()
    )

    if not entries:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No ledger entries found for this period. Ingest subsidiary data first.",
        )

    entities = db.query(EntityMetadata).all()
    warnings = _submission_warnings(db, period_id, entities)

    # Build engine request payload.
    # Use now() as the as_of cutoff so that all currently-ingested entries for
    # this period are eligible.  The period_end date is the accounting boundary
    # for which transactions belong to the period (enforced via period_id FK);
    # the as_of timestamp controls which ledger entries the engine can see and
    # should always be "now" for a live consolidation run.
    as_of_dt = datetime.now(timezone.utc)

    engine_entries = [
        {
            "entry_id": str(e.entry_id),
            "timestamp": e.timestamp.isoformat(),
            "entity_id": str(e.entity_id),
            "account_code": e.account_code,
            "amount": str(e.amount),
            "is_elimination": e.is_elimination,
            "metadata": e.metadata_,
        }
        for e in entries
    ]

    engine_entities = [
        {
            "entity_id": str(e.entity_id),
            "name": e.name,
            "parent_entity_id": str(e.parent_entity_id) if e.parent_entity_id else None,
            "ownership_pct": str(e.ownership_pct) if e.ownership_pct else None,
        }
        for e in entities
    ]

    try:
        resp = httpx.post(
            f"{ENGINE_URL}/consolidate",
            json={
                "entries": engine_entries,
                "entities": engine_entities,
                "as_of": as_of_dt.isoformat(),
            },
            timeout=60.0,
        )
        resp.raise_for_status()
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Engine call failed: {exc}",
        )

    engine_result = resp.json()
    eliminations = engine_result.get("eliminations", [])

    # Persist elimination entries
    now = datetime.now(timezone.utc)
    orm_rows = []
    for elim in eliminations:
        orm_rows.append(
            LedgerEntry(
                entry_id=uuid.UUID(elim["entry_id"]),
                timestamp=now,
                entity_id=uuid.UUID(elim["entity_id"]),
                account_code=elim["account_code"],
                amount=Decimal(str(elim["amount"])),
                is_elimination=True,
                period_id=period_id,
                metadata_=elim.get("metadata"),
            )
        )

    if orm_rows:
        db.add_all(orm_rows)
        db.commit()

    return ConsolidationResult(
        period_id=period_id,
        eliminations_created=len(orm_rows),
        warnings=warnings,
    )


@router.get(
    "/report/{period_id}",
    response_model=ConsolidatedReport,
    status_code=status.HTTP_200_OK,
)
def get_report(period_id: uuid.UUID, db: Session = Depends(get_db)) -> ConsolidatedReport:
    """Return the consolidated financial statements for a period.

    Loads all ledger entries (including eliminations), sums by account code,
    and classifies into balance sheet / income statement sections.
    """
    period = _load_period(db, period_id)
    entities = db.query(EntityMetadata).all()
    warnings = _submission_warnings(db, period_id, entities)

    all_entries = (
        db.query(LedgerEntry)
        .filter(LedgerEntry.period_id == period_id)
        .all()
    )

    # Aggregate by account_code
    totals: Dict[str, Decimal] = defaultdict(Decimal)
    for entry in all_entries:
        totals[entry.account_code] += entry.amount

    balance_sheet: Dict[str, Dict[str, str]] = {
        "assets": {},
        "liabilities": {},
        "equity": {},
    }
    income_statement: Dict[str, Dict[str, str]] = {
        "revenue": {},
        "cogs": {},
        "operating_expenses": {},
    }
    other: Dict[str, str] = {}

    for code, total in totals.items():
        if total == Decimal("0"):
            continue
        section = _classify(code)
        if section in balance_sheet:
            balance_sheet[section][code] = str(total)
        elif section in income_statement:
            income_statement[section][code] = str(total)
        else:
            other[code] = str(total)

    # Elimination summary
    elim_entries = [e for e in all_entries if e.is_elimination]
    elim_summary = [
        EliminationSummary(
            elimination_type=(e.metadata_ or {}).get("elimination_type", "unknown"),
            entity_id=str(e.entity_id),
            account_code=e.account_code,
            amount=str(e.amount),
        )
        for e in elim_entries
    ]

    period_dict = {
        "period_id": str(period.period_id),
        "label": period.label,
        "period_start": str(period.period_start),
        "period_end": str(period.period_end),
        "status": period.status,
    }

    return ConsolidatedReport(
        period=period_dict,
        balance_sheet=balance_sheet,
        income_statement=income_statement,
        eliminations_summary=elim_summary,
        warnings=warnings,
    )
