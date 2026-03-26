"""Pydantic models for the Ingestion service."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


class LedgerEntry(BaseModel):
    """Immutable ledger entry as stored in ledger_entries table."""

    entry_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    entity_id: str
    account_code: str  # GCoA account code (post-mapping)
    amount: Decimal
    is_elimination: bool = False
    metadata: Dict[str, Any] = Field(default_factory=dict)

    model_config = {"frozen": True}


class TrialBalanceRow(BaseModel):
    """One row from a subsidiary Trial Balance CSV."""

    account_code: str
    amount: Decimal
    description: str = ""
    counterparty_entity_id: Optional[str] = None
    subsidiary_entity_id: Optional[str] = None

    @field_validator("amount", mode="before")
    @classmethod
    def coerce_amount(cls, v: Any) -> Decimal:
        return Decimal(str(v))


class MappingRecord(BaseModel):
    """Resolved mapping: source row + resulting LedgerEntry (or None if unmapped)."""

    row: TrialBalanceRow
    gcoa_code: Optional[str]
    entry: Optional[LedgerEntry]


class UploadSummary(BaseModel):
    """Response returned after a successful upload."""

    entity_id: str
    total_rows: int
    mapped_count: int
    unmapped_count: int
    unmapped_codes: List[str]
    entries_committed: int
