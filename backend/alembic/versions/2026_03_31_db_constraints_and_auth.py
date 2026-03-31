"""Add missing DB constraints and users table for JWT auth.

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-03-31 00:00:00.000000
"""
from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "b2c3d4e5f6a7"
down_revision: Union[str, None] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- co-9h9: Missing DB constraints ------------------------------------

    # Unique constraint on entity_metadata.name
    op.create_unique_constraint(
        "uq_entity_metadata_name",
        "entity_metadata",
        ["name"],
    )

    # CHECK constraint: ownership_pct must be between 0 and 100
    op.create_check_constraint(
        "ck_entity_metadata_ownership_pct",
        "entity_metadata",
        "ownership_pct IS NULL OR (ownership_pct >= 0 AND ownership_pct <= 100)",
    )

    # CHECK constraint: period_end must be after period_start
    op.create_check_constraint(
        "ck_reporting_periods_dates",
        "reporting_periods",
        "period_end > period_start",
    )

    # --- co-ntq: Users table for JWT authentication ------------------------

    op.create_table(
        "users",
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            comment="Stable user identifier",
        ),
        sa.Column(
            "username",
            sa.String(255),
            nullable=False,
            comment="Unique login name",
        ),
        sa.Column(
            "hashed_password",
            sa.String(255),
            nullable=False,
            comment="bcrypt hash of the user's password",
        ),
        sa.Column(
            "tenant_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
            comment="Tenant this user belongs to",
        ),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
            comment="Account creation timestamp",
        ),
        sa.UniqueConstraint("username", name="uq_users_username"),
    )

    op.create_index("ix_users_tenant_id", "users", ["tenant_id"])


def downgrade() -> None:
    op.drop_index("ix_users_tenant_id", table_name="users")
    op.drop_table("users")

    op.drop_constraint("ck_reporting_periods_dates", "reporting_periods", type_="check")
    op.drop_constraint("ck_entity_metadata_ownership_pct", "entity_metadata", type_="check")
    op.drop_constraint("uq_entity_metadata_name", "entity_metadata", type_="unique")
