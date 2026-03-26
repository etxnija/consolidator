"""Database engine and session configuration for the Consolidator backend."""

import os

from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql+psycopg2://consolidator:consolidator@localhost:5432/consolidator",
)

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


class Base(DeclarativeBase):
    pass


def get_db():
    """Yield a database session, closing it when done."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _block_unsafe_ddl(conn, cursor, statement, parameters, context, executemany):
    """Raise if a DDL UPDATE or DELETE targets ledger tables."""
    upper = statement.strip().upper()
    ledger_tables = {"LEDGER_ENTRIES", "ENTITY_METADATA"}
    if upper.startswith(("UPDATE", "DELETE")):
        for table in ledger_tables:
            if table in upper:
                raise RuntimeError(
                    f"Immutability violation: {statement[:80]!r} is not allowed on {table}"
                )


event.listen(engine, "before_cursor_execute", _block_unsafe_ddl)
