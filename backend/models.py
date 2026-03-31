"""SQLAlchemy ORM models for the Consolidator Immutable Ledger.

Tables:
  ledger_entries   — append-only financial journal entries
  entity_metadata  — consolidation entity hierarchy

Immutability is enforced at two layers:
  1. Database-level triggers (applied via DDL events in migrations)
  2. Application-level SQLAlchemy event hooks (see database.py)
"""

import datetime
import enum
import uuid
from decimal import Decimal
from typing import Dict, List, Optional

from sqlalchemy import (
    Boolean,
    DDL,
    Date,
    Enum,
    ForeignKey,
    Numeric,
    String,
    event,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from sqlalchemy.types import TIMESTAMP

from .database import Base


# ---------------------------------------------------------------------------
# reporting_periods
# ---------------------------------------------------------------------------

class PeriodStatus(str, enum.Enum):
    open = "open"
    locked = "locked"


class ReportingPeriod(Base):
    """A named reporting period used to group ledger entries for consolidation.

    Examples: "FY-2024", "Q4-2024".  The period_end date is used as the
    `as_of` cutoff when running the IFRS 10 calculator.
    """

    __tablename__ = "reporting_periods"

    period_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Stable identifier for the reporting period",
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
        comment="Tenant that owns this reporting period",
    )
    label: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Human-readable label, e.g. 'FY-2024', 'Q4-2024' (unique per tenant)",
    )
    period_start: Mapped[datetime.date] = mapped_column(
        Date,
        nullable=False,
        comment="First day of the reporting period",
    )
    period_end: Mapped[datetime.date] = mapped_column(
        Date,
        nullable=False,
        comment="Last day of the reporting period (used as as_of cutoff)",
    )
    status: Mapped[PeriodStatus] = mapped_column(
        Enum(PeriodStatus, name="period_status"),
        nullable=False,
        default=PeriodStatus.open,
        server_default=text("'open'"),
        comment="'open' allows ingestion; 'locked' prevents further changes",
    )

    # Ledger entries tagged to this period
    ledger_entries: Mapped[List["LedgerEntry"]] = relationship(
        "LedgerEntry",
        back_populates="period",
        cascade="",
    )

    def __repr__(self) -> str:
        return f"<ReportingPeriod period_id={self.period_id} label={self.label!r} status={self.status}>"


# ---------------------------------------------------------------------------
# entity_metadata
# ---------------------------------------------------------------------------

class EntityMetadata(Base):
    """Hierarchy of legal entities used in consolidation.

    Rows are append-only.  Ownership structure is expressed via
    parent_entity_id / ownership_pct; a NULL parent_entity_id denotes a
    top-level (ultimate parent) entity.
    """

    __tablename__ = "entity_metadata"

    entity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Stable identifier for the legal entity",
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
        comment="Tenant that owns this entity",
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Human-readable entity name (unique per tenant)",
    )
    parent_entity_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("entity_metadata.entity_id", ondelete="RESTRICT"),
        nullable=True,
        comment="Direct parent entity; NULL for ultimate parent",
    )
    ownership_pct: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(7, 4),
        nullable=True,
        comment="Parent's ownership percentage (0.0000–100.0000)",
    )

    # Self-referential relationship — convenient for tree traversal
    parent: Mapped[Optional["EntityMetadata"]] = relationship(
        "EntityMetadata",
        remote_side="EntityMetadata.entity_id",
        back_populates="children",
    )
    children: Mapped[List["EntityMetadata"]] = relationship(
        "EntityMetadata",
        back_populates="parent",
    )

    # Ledger entries referencing this entity
    ledger_entries: Mapped[List["LedgerEntry"]] = relationship(
        "LedgerEntry",
        back_populates="entity",
        cascade="",            # Never cascade deletes — ledger is immutable
    )

    def __repr__(self) -> str:
        return f"<EntityMetadata entity_id={self.entity_id} name={self.name!r}>"


# ---------------------------------------------------------------------------
# ledger_entries
# ---------------------------------------------------------------------------

class LedgerEntry(Base):
    """Append-only financial journal entry.

    Each row records a single-sided posting to an account for a given entity.
    Elimination entries are flagged with is_elimination=True.

    Immutability contract:
      - No UPDATE or DELETE is permitted on this table.
      - Corrections are made by posting reversing entries.
      - The database-level trigger ``trg_ledger_entries_immutable`` (see
        ``_immutable_trigger`` DDL below) enforces this at the DB layer.
    """

    __tablename__ = "ledger_entries"

    entry_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Globally unique entry identifier",
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
        comment="Tenant that owns this ledger entry",
    )
    timestamp: Mapped[datetime.datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
        comment="Wall-clock time the entry was recorded (UTC)",
    )
    entity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("entity_metadata.entity_id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
        comment="Entity to which this entry belongs",
    )
    account_code: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        index=True,
        comment="Chart-of-accounts code (e.g. '1100', 'REV-INTER')",
    )
    amount: Mapped[Decimal] = mapped_column(
        Numeric(19, 4),
        nullable=False,
        comment="Signed posting amount; positive = debit by convention",
    )
    is_elimination: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default=text("FALSE"),
        comment="True for intercompany elimination entries",
    )
    period_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("reporting_periods.period_id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
        comment="Reporting period this entry belongs to (nullable for legacy entries)",
    )
    metadata_: Mapped[Optional[Dict]] = mapped_column(
        "metadata",
        JSONB,
        nullable=True,
        comment="Arbitrary supplementary data (source ref, tags, etc.)",
    )

    # Relationship back to the entity
    entity: Mapped["EntityMetadata"] = relationship(  # type: ignore[assignment]
        "EntityMetadata",
        back_populates="ledger_entries",
    )

    # Relationship to the reporting period
    period: Mapped[Optional["ReportingPeriod"]] = relationship(
        "ReportingPeriod",
        back_populates="ledger_entries",
    )

    def __repr__(self) -> str:
        return (
            f"<LedgerEntry entry_id={self.entry_id} "
            f"entity_id={self.entity_id} "
            f"account_code={self.account_code!r} "
            f"amount={self.amount}>"
        )


# ---------------------------------------------------------------------------
# users  (authentication)
# ---------------------------------------------------------------------------

class User(Base):
    """A user account with bcrypt-hashed password and tenant association."""

    __tablename__ = "users"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    username: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
    )
    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
    )


# ---------------------------------------------------------------------------
# Database-level immutability trigger (PostgreSQL)
# ---------------------------------------------------------------------------

_immutable_trigger_fn = DDL(
    """
    CREATE OR REPLACE FUNCTION ledger_entries_immutable()
    RETURNS TRIGGER LANGUAGE plpgsql AS $$
    BEGIN
        RAISE EXCEPTION
            'ledger_entries is append-only: UPDATE and DELETE are not permitted';
    END;
    $$;
    """
)

_immutable_trigger = DDL(
    """
    DO $$
    BEGIN
        IF NOT EXISTS (
            SELECT 1 FROM pg_trigger
            WHERE tgname = 'trg_ledger_entries_immutable'
        ) THEN
            CREATE TRIGGER trg_ledger_entries_immutable
            BEFORE UPDATE OR DELETE ON ledger_entries
            FOR EACH ROW EXECUTE FUNCTION ledger_entries_immutable();
        END IF;
    END;
    $$;
    """
)

event.listen(
    LedgerEntry.__table__,
    "after_create",
    _immutable_trigger_fn.execute_if(dialect="postgresql"),
)
event.listen(
    LedgerEntry.__table__,
    "after_create",
    _immutable_trigger.execute_if(dialect="postgresql"),
)
