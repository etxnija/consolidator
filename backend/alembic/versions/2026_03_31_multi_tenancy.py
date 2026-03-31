"""Add tenant_id to entity_metadata, reporting_periods, and ledger_entries.

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-03-31 01:00:00.000000
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

# Sentinel tenant UUID used as DEFAULT for rows that pre-date multi-tenancy.
_DEFAULT_TENANT = "00000000-0000-0000-0000-000000000001"


def upgrade() -> None:
    # --- entity_metadata ---------------------------------------------------
    op.add_column(
        "entity_metadata",
        sa.Column(
            "tenant_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
            server_default=_DEFAULT_TENANT,
            comment="Tenant that owns this entity",
        ),
    )
    op.create_index("ix_entity_metadata_tenant_id", "entity_metadata", ["tenant_id"])

    # --- reporting_periods -------------------------------------------------
    op.add_column(
        "reporting_periods",
        sa.Column(
            "tenant_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
            server_default=_DEFAULT_TENANT,
            comment="Tenant that owns this reporting period",
        ),
    )
    op.create_index("ix_reporting_periods_tenant_id", "reporting_periods", ["tenant_id"])

    # --- ledger_entries ----------------------------------------------------
    op.add_column(
        "ledger_entries",
        sa.Column(
            "tenant_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
            server_default=_DEFAULT_TENANT,
            comment="Tenant that owns this ledger entry",
        ),
    )
    op.create_index("ix_ledger_entries_tenant_id", "ledger_entries", ["tenant_id"])


def downgrade() -> None:
    op.drop_index("ix_ledger_entries_tenant_id", table_name="ledger_entries")
    op.drop_column("ledger_entries", "tenant_id")

    op.drop_index("ix_reporting_periods_tenant_id", table_name="reporting_periods")
    op.drop_column("reporting_periods", "tenant_id")

    op.drop_index("ix_entity_metadata_tenant_id", table_name="entity_metadata")
    op.drop_column("entity_metadata", "tenant_id")
