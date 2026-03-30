"""Alembic environment configuration for the Consolidator backend.

Reads DATABASE_URL from the environment (same variable used by the app).
Imports Base from backend.database so autogenerate can detect model changes.
"""

from __future__ import annotations

import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

from alembic import context

# Import all ORM models so their tables are registered with Base.metadata.
import backend.models  # noqa: F401

from backend.database import Base

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def _get_url() -> str:
    return os.environ.get(
        "DATABASE_URL",
        "postgresql+psycopg2://consolidator:consolidator@localhost:5432/consolidator",
    )


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode (no live DB connection, emit SQL)."""
    context.configure(
        url=_get_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode (connect to DB and execute)."""
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = _get_url()
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
