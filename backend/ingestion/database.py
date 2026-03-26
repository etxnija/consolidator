"""Database persistence layer for the Ingestion service.

Integrates with the SQLAlchemy ORM defined in backend/models.py and the
session factory in backend/database.py.

Commits LedgerEntry (Pydantic) objects by converting them to the ORM
LedgerEntry model and inserting via a session.  Only INSERTs are ever
issued — the ledger is append-only.

Entity resolution:
  The ingestion API accepts a human-readable subsidiary code (e.g. "SUBS_01").
  entity_metadata rows must already exist with matching `name` values.
  If no matching entity is found, a LookupError is raised.
"""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy.orm import Session

from ..database import get_db
from ..models import EntityMetadata, PeriodStatus, ReportingPeriod
from ..models import LedgerEntry as OrmLedgerEntry

if TYPE_CHECKING:
    from .models import LedgerEntry as PydanticLedgerEntry


def _resolve_entity_uuid(session: Session, entity_name: str):
    """Return the UUID for an entity by its name, or raise LookupError."""
    row = (
        session.query(EntityMetadata)
        .filter(EntityMetadata.name == entity_name)
        .one_or_none()
    )
    if row is None:
        raise LookupError(
            f"Entity {entity_name!r} not found in entity_metadata. "
            "Ensure the entity has been registered before ingestion."
        )
    return row.entity_id


def _resolve_period(session: Session, period_id: uuid.UUID) -> ReportingPeriod:
    """Return the period row, or raise LookupError / ValueError."""
    period = session.get(ReportingPeriod, period_id)
    if period is None:
        raise LookupError(f"Reporting period {period_id} not found.")
    if period.status == PeriodStatus.locked:
        raise ValueError(f"Reporting period {period.label!r} is locked; ingestion is not allowed.")
    return period


def commit_entries(
    entries: "List[PydanticLedgerEntry]",
    entity_name: str,
    period_id: Optional[uuid.UUID] = None,
) -> int:
    """Insert Pydantic LedgerEntry records into ledger_entries via ORM.

    Args:
        entries: Validated Pydantic LedgerEntry objects from mapping.py.
        entity_name: Human-readable subsidiary name (e.g. "SUBS_01") used
            to resolve the entity UUID from entity_metadata.
        period_id: Optional UUID of a reporting period to tag entries to.

    Returns:
        Number of rows inserted.

    Raises:
        LookupError: If no entity_metadata row exists for entity_name, or period not found.
        ValueError: If the period is locked.
    """
    if not entries:
        return 0

    # get_db() is a generator — consume it manually here.
    session: Session = next(get_db())
    try:
        entity_uuid = _resolve_entity_uuid(session, entity_name)

        if period_id is not None:
            _resolve_period(session, period_id)

        orm_rows = [
            OrmLedgerEntry(
                entry_id=entry.entry_id,
                timestamp=entry.timestamp,
                entity_id=entity_uuid,
                account_code=entry.account_code,
                amount=entry.amount,
                is_elimination=entry.is_elimination,
                period_id=period_id,
                metadata_=entry.metadata,
            )
            for entry in entries
        ]

        session.add_all(orm_rows)
        session.commit()
        return len(orm_rows)
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
