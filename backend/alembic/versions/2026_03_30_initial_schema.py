"""Initial schema — reporting_periods, entity_metadata, ledger_entries.

Revision ID: a1b2c3d4e5f6
Revises:
Create Date: 2026-03-30 00:00:00.000000
"""
from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- ENUM type ---------------------------------------------------------
    period_status = postgresql.ENUM("open", "locked", name="period_status")
    period_status.create(op.get_bind(), checkfirst=True)

    # --- reporting_periods -------------------------------------------------
    op.create_table(
        "reporting_periods",
        sa.Column(
            "period_id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            comment="Stable identifier for the reporting period",
        ),
        sa.Column(
            "label",
            sa.String(50),
            nullable=False,
            comment="Human-readable label, e.g. 'FY-2024', 'Q4-2024'",
        ),
        sa.Column(
            "period_start",
            sa.Date(),
            nullable=False,
            comment="First day of the reporting period",
        ),
        sa.Column(
            "period_end",
            sa.Date(),
            nullable=False,
            comment="Last day of the reporting period (used as as_of cutoff)",
        ),
        sa.Column(
            "status",
            sa.Enum("open", "locked", name="period_status", create_type=False),
            nullable=False,
            server_default="open",
            comment="'open' allows ingestion; 'locked' prevents further changes",
        ),
        sa.UniqueConstraint("label", name="uq_reporting_periods_label"),
    )

    # --- entity_metadata ---------------------------------------------------
    op.create_table(
        "entity_metadata",
        sa.Column(
            "entity_id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            comment="Stable identifier for the legal entity",
        ),
        sa.Column(
            "name",
            sa.String(255),
            nullable=False,
            comment="Human-readable entity name",
        ),
        sa.Column(
            "parent_entity_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("entity_metadata.entity_id", ondelete="RESTRICT"),
            nullable=True,
            comment="Direct parent entity; NULL for ultimate parent",
        ),
        sa.Column(
            "ownership_pct",
            sa.Numeric(7, 4),
            nullable=True,
            comment="Parent's ownership percentage (0.0000–100.0000)",
        ),
    )

    # --- ledger_entries ----------------------------------------------------
    op.create_table(
        "ledger_entries",
        sa.Column(
            "entry_id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            comment="Globally unique entry identifier",
        ),
        sa.Column(
            "timestamp",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
            comment="Wall-clock time the entry was recorded (UTC)",
        ),
        sa.Column(
            "entity_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("entity_metadata.entity_id", ondelete="RESTRICT"),
            nullable=False,
            comment="Entity to which this entry belongs",
        ),
        sa.Column(
            "account_code",
            sa.String(64),
            nullable=False,
            comment="Chart-of-accounts code (e.g. '1100', 'REV-INTER')",
        ),
        sa.Column(
            "amount",
            sa.Numeric(19, 4),
            nullable=False,
            comment="Signed posting amount; positive = debit by convention",
        ),
        sa.Column(
            "is_elimination",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("FALSE"),
            comment="True for intercompany elimination entries",
        ),
        sa.Column(
            "period_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("reporting_periods.period_id", ondelete="RESTRICT"),
            nullable=True,
            comment="Reporting period this entry belongs to (nullable for legacy entries)",
        ),
        sa.Column(
            "metadata",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
            comment="Arbitrary supplementary data (source ref, tags, etc.)",
        ),
    )

    # Indexes on frequently filtered columns
    op.create_index("ix_ledger_entries_entity_id", "ledger_entries", ["entity_id"])
    op.create_index("ix_ledger_entries_account_code", "ledger_entries", ["account_code"])
    op.create_index("ix_ledger_entries_period_id", "ledger_entries", ["period_id"])

    # --- Immutability trigger on ledger_entries ----------------------------
    op.execute(
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
    op.execute(
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


def downgrade() -> None:
    op.execute(
        """
        DROP TRIGGER IF EXISTS trg_ledger_entries_immutable ON ledger_entries;
        """
    )
    op.execute("DROP FUNCTION IF EXISTS ledger_entries_immutable();")

    op.drop_index("ix_ledger_entries_period_id", table_name="ledger_entries")
    op.drop_index("ix_ledger_entries_account_code", table_name="ledger_entries")
    op.drop_index("ix_ledger_entries_entity_id", table_name="ledger_entries")

    op.drop_table("ledger_entries")
    op.drop_table("entity_metadata")
    op.drop_table("reporting_periods")

    op.execute("DROP TYPE IF EXISTS period_status;")
