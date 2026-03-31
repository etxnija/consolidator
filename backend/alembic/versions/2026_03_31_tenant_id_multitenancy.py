"""Add tenant_id to data tables for full multi-tenancy.

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-03-31 00:00:00.000000
"""
from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "c3d4e5f6a7b8"
down_revision: Union[str, None] = "b2c3d4e5f6a7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Sentinel UUID for rows that predate tenancy
_SENTINEL_TENANT = "00000000-0000-0000-0000-000000000001"


def upgrade() -> None:
    # --- entity_metadata ---------------------------------------------------
    # Replace global name-unique constraint with per-tenant uniqueness.
    op.drop_constraint("uq_entity_metadata_name", "entity_metadata", type_="unique")

    op.add_column(
        "entity_metadata",
        sa.Column(
            "tenant_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
            server_default=_SENTINEL_TENANT,
            comment="Tenant that owns this entity",
        ),
    )
    # Remove the server_default after backfill so it's truly NOT NULL without default
    op.alter_column("entity_metadata", "tenant_id", server_default=None)

    op.create_index("ix_entity_metadata_tenant_id", "entity_metadata", ["tenant_id"])
    op.create_unique_constraint(
        "uq_entity_metadata_name_tenant",
        "entity_metadata",
        ["name", "tenant_id"],
    )

    # --- reporting_periods -------------------------------------------------
    # Replace global label-unique constraint with per-tenant uniqueness.
    op.drop_constraint("uq_reporting_periods_label", "reporting_periods", type_="unique")

    op.add_column(
        "reporting_periods",
        sa.Column(
            "tenant_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
            server_default=_SENTINEL_TENANT,
            comment="Tenant that owns this reporting period",
        ),
    )
    op.alter_column("reporting_periods", "tenant_id", server_default=None)

    op.create_index("ix_reporting_periods_tenant_id", "reporting_periods", ["tenant_id"])
    op.create_unique_constraint(
        "uq_reporting_periods_label_tenant",
        "reporting_periods",
        ["label", "tenant_id"],
    )

    # --- ledger_entries ----------------------------------------------------
    # The immutability trigger only blocks row UPDATE/DELETE; ADD COLUMN is DDL
    # and is not affected.
    op.add_column(
        "ledger_entries",
        sa.Column(
            "tenant_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
            server_default=_SENTINEL_TENANT,
            comment="Tenant that owns this ledger entry",
        ),
    )
    op.alter_column("ledger_entries", "tenant_id", server_default=None)

    op.create_index("ix_ledger_entries_tenant_id", "ledger_entries", ["tenant_id"])


def downgrade() -> None:
    op.drop_index("ix_ledger_entries_tenant_id", table_name="ledger_entries")
    op.drop_column("ledger_entries", "tenant_id")

    op.drop_unique_constraint("uq_reporting_periods_label_tenant", "reporting_periods")
    op.drop_index("ix_reporting_periods_tenant_id", table_name="reporting_periods")
    op.drop_column("reporting_periods", "tenant_id")
    op.create_unique_constraint("uq_reporting_periods_label", "reporting_periods", ["label"])

    op.drop_unique_constraint("uq_entity_metadata_name_tenant", "entity_metadata")
    op.drop_index("ix_entity_metadata_tenant_id", table_name="entity_metadata")
    op.drop_column("entity_metadata", "tenant_id")
    op.create_unique_constraint("uq_entity_metadata_name", "entity_metadata", ["name"])
