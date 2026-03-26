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

from typing import TYPE_CHECKING, List

from sqlalchemy.orm import Session

from ..database import get_db
from ..models import EntityMetadata
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


def commit_entries(
    entries: "List[PydanticLedgerEntry]",
    entity_name: str,
) -> int:
    """Insert Pydantic LedgerEntry records into ledger_entries via ORM.

    Args:
        entries: Validated Pydantic LedgerEntry objects from mapping.py.
        entity_name: Human-readable subsidiary name (e.g. "SUBS_01") used
            to resolve the entity UUID from entity_metadata.

    Returns:
        Number of rows inserted.

    Raises:
        LookupError: If no entity_metadata row exists for entity_name.
    """
    if not entries:
        return 0

    # get_db() is a generator — consume it manually here.
    session: Session = next(get_db())
    try:
        entity_uuid = _resolve_entity_uuid(session, entity_name)

        orm_rows = [
            OrmLedgerEntry(
                entry_id=entry.entry_id,
                timestamp=entry.timestamp,
                entity_id=entity_uuid,
                account_code=entry.account_code,
                amount=entry.amount,
                is_elimination=entry.is_elimination,
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
