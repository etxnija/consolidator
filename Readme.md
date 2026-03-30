# North Star Consolidator

A containerised SaaS for **IFRS 10 group consolidation**. The system transforms
Trial Balance CSVs from up to 10 subsidiaries into a single, audited consolidated
financial statement using an **Immutable Ledger** and **Stateless Calculator** pattern.

---

## Architecture

```
┌─────────────┐   CSV upload   ┌──────────────────┐   ledger entries   ┌──────────┐
│  Streamlit  │ ─────────────► │  FastAPI Backend  │ ─────────────────► │ Postgres │
│  Frontend   │                │  (Ingestion)      │                    │  Ledger  │
└─────────────┘                └──────────────────┘                     └────┬─────┘
       ▲                                                                       │
       │  consolidated report                                                  │ snapshot
       │                                                                       ▼
       └───────────────────────────────── Engine (IFRS 10 Calculator) ◄───────┘
```

| Service | Technology | Port |
|---------|-----------|------|
| `postgres` | PostgreSQL 16 | internal |
| `backend` | FastAPI + SQLAlchemy | 8000 |
| `engine` | Pure Python (Pydantic) | internal |
| `frontend` | Streamlit | 8501 |

### Design Principles

- **Immutable Ledger** — `ledger_entries` is append-only. No UPDATE or DELETE is
  ever issued. Corrections are posted as reversing entries. A PostgreSQL trigger
  enforces this at the database layer.
- **Stateless Calculator** — the consolidation engine takes an in-memory snapshot
  of the ledger and returns elimination entries. It has no database connection and
  no side effects.
- **Auditability** — every consolidation result is a deterministic projection of
  the ledger state at a specific `as_of` timestamp. Re-running at the same
  timestamp always produces the same result.

---

## Quick Start

### Prerequisites

- [Podman](https://podman.io/) (rootless) and `podman-compose`, **or** Docker + docker-compose
- Python 3.12+ (for running tests locally)

### Run with Podman

```bash
git clone git@github.com:etxnija/consolidator.git
cd consolidator
cp .env.example .env          # edit credentials if needed
podman-compose up --build
```

Services will be available at:
- **Streamlit dashboard**: http://localhost:8501
- **FastAPI / Swagger UI**: http://localhost:8000/docs

### Run with Docker

```bash
docker compose up --build
```

---

## Ingesting a Trial Balance

Upload a subsidiary CSV via the API:

```bash
curl -X POST http://localhost:8000/ingest/SUBS_01 \
  -F "file=@trial_balance_subs01.csv"
```

**CSV format** — minimum required columns:

```csv
account_code,amount
1100,50000.00
2000,-30000.00
REV-SALES,120000.00
```

An optional `description` column is also accepted.

Supported subsidiary IDs: `SUBS_01` through `SUBS_10`.

The endpoint returns an `UploadSummary`:

```json
{
  "entity_id": "SUBS_01",
  "total_rows": 42,
  "mapped_count": 40,
  "unmapped_count": 2,
  "unmapped_codes": ["LEGACY_CODE_X", "OLD_ACCT_99"],
  "entries_committed": 40
}
```

---

## Data Model

### `ledger_entries` (append-only)

| Column | Type | Notes |
|--------|------|-------|
| `entry_id` | UUID PK | Auto-generated |
| `timestamp` | TIMESTAMPTZ | UTC, server default |
| `entity_id` | UUID FK | References `entity_metadata` |
| `account_code` | VARCHAR(64) | Global Chart of Accounts code |
| `amount` | NUMERIC(19,4) | Positive = debit by convention |
| `is_elimination` | BOOLEAN | True for IFRS 10 elimination entries |
| `metadata` | JSONB | Source reference, tags, counterparty IDs |

### `entity_metadata`

| Column | Type | Notes |
|--------|------|-------|
| `entity_id` | UUID PK | Stable identifier |
| `name` | VARCHAR(255) | Human-readable name |
| `parent_entity_id` | UUID FK | NULL = ultimate parent |
| `ownership_pct` | NUMERIC(7,4) | Parent's ownership % |

---

## Running Tests

```bash
# Engine tests (no database needed)
cd engine
pip install -r requirements.txt
python -m pytest tests/ -v

# Ingestion / backend tests
cd backend
pip install -r requirements.txt
python -m pytest tests/ -v
```

---

## Project Structure

```
consolidator/
├── backend/
│   ├── ingestion/
│   │   ├── app.py          # FastAPI endpoints
│   │   ├── mapping.py      # CSV → GCoA mapping logic
│   │   ├── gcoa_map.py     # Global Chart of Accounts definitions
│   │   ├── database.py     # Ledger commit helpers
│   │   └── models.py       # Pydantic request/response models
│   ├── models.py           # SQLAlchemy ORM (LedgerEntry, EntityMetadata)
│   ├── database.py         # DB engine, session factory
│   └── requirements.txt
├── engine/
│   ├── calculator.py       # IFRS 10 IfrsCalculator (stateless)
│   ├── models.py           # Pydantic snapshots / elimination models
│   └── requirements.txt
├── frontend/
│   └── Dockerfile
├── infra/
├── docker-compose.yml
├── .env.example
└── docs/
    └── consolidation-logic.md
```

---

## Schema Migrations (Alembic)

Database schema is managed via [Alembic](https://alembic.sqlalchemy.org/).
The backend applies `alembic upgrade head` automatically on startup, so a fresh
`podman compose up` creates all tables without any manual steps.

### Adding a schema change

1. Edit the SQLAlchemy models in `backend/models.py`.
2. Generate a migration:
   ```bash
   cd backend
   DATABASE_URL=postgresql+psycopg2://consolidator:consolidator@localhost:5432/consolidator \
     alembic revision --autogenerate -m "describe your change"
   ```
3. Review the generated file in `backend/alembic/versions/` and adjust if needed.
4. Apply it locally:
   ```bash
   alembic upgrade head
   ```

### Migration history and rollback

```bash
# Show migration history
alembic history

# Downgrade one step
alembic downgrade -1

# Re-apply
alembic upgrade head
```

---

## Further Reading

- [Consolidation Logic](docs/consolidation-logic.md) — detailed explanation of
  the IFRS 10 elimination steps implemented in the engine.
