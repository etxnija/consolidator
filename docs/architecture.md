# North Star Consolidator — Architecture

_Last updated: 2026-03-26_

---

## 1. Purpose

North Star Consolidator is a SaaS platform for **IFRS 10 group consolidation**.
It transforms Trial Balance CSVs from multiple subsidiaries into a single audited
consolidated financial statement — Balance Sheet, Income Statement, and an
elimination audit trail.

Target users: CFOs and group controllers at companies with 2–20 legal entities.

---

## 2. System Overview

```
Browser (CFO)
     │
     ▼
┌─────────────────┐    HTTP (port 8501)
│  Streamlit UI   │  ◄──────────────────────────────────────────┐
│  frontend/      │                                              │
└────────┬────────┘                                              │
         │ HTTP REST                                             │
         ▼                                                       │
┌─────────────────────────────────────────────────────────────┐  │
│                  FastAPI Backend  :8000                      │  │
│                  backend/                                    │  │
│                                                              │  │
│  /entities    — entity CRUD + ownership tree                 │  │
│  /periods     — reporting period lifecycle                   │  │
│  /ingest/{e}  — CSV → GCoA mapping → ledger                  │  │
│  /consolidate — orchestration: load → engine → persist       │  │
│  /report      — consolidated BS + IS + eliminations          │  │
└────────┬──────────────────────────┬──────────────────────────┘
         │ SQLAlchemy ORM            │ HTTP POST /consolidate
         ▼                          ▼
┌─────────────────┐      ┌──────────────────────┐
│  PostgreSQL 16  │      │  Engine Service :8001 │
│  (append-only   │      │  engine/              │
│   ledger)       │      │                       │
│                 │      │  Pure Python           │
│  ledger_entries │      │  IfrsCalculator       │
│  entity_metadata│      │  (stateless)          │
│  reporting_     │      └──────────────────────┘
│  periods        │
└─────────────────┘
```

All four services run as containers defined in `docker-compose.yml`,
compatible with both Docker and **Podman** (rootless).

---

## 3. Services

### 3.1 Frontend (`frontend/`, port 8501)

Streamlit single-page application. All state is held in the backend — the
frontend is stateless and makes REST calls on every interaction.

Key UI sections:
- **Sidebar** — reporting period selector; create entity form; create period
  form; CSV upload (ingestion)
- **Main** — service health; ownership tree; active period summary;
  consolidation controls (Run + Lock); consolidated report (BS + IS +
  eliminations)

### 3.2 Backend (`backend/`, port 8000)

FastAPI application. Owns all persistence and orchestration logic.
Auto-creates the database schema on startup via `Base.metadata.create_all()`.

Routers:

| Router | Prefix | Responsibility |
|--------|--------|----------------|
| `entities/router.py` | `/entities` | Register and manage legal entities |
| `periods/router.py` | `/periods` | Create and lock reporting periods |
| `ingestion/app.py` | `/ingest` | Parse CSV, map to GCoA, commit to ledger |
| `consolidation/router.py` | `/consolidate`, `/report` | Orchestrate engine call; produce report |

### 3.3 Engine (`engine/`, port 8001)

Stateless FastAPI micro-service wrapping the IFRS 10 calculator.
**No database connection.** Accepts a JSON snapshot of ledger entries and
entities, returns elimination entries.

Single endpoint: `POST /consolidate`

The engine is isolated so that:
- The calculation logic can be tested without any database
- The engine can be scaled or replaced independently
- The financial logic has a clear, auditable boundary

### 3.4 PostgreSQL (`postgres`, internal)

Append-only ledger. Two immutability layers:
1. **Application layer** — `database.py` hooks block `UPDATE`/`DELETE` on
   ledger tables before they reach the DB
2. **Database layer** — PostgreSQL trigger `trg_ledger_entries_immutable`
   raises an exception on any `UPDATE` or `DELETE` on `ledger_entries`

---

## 4. Data Model

### `entity_metadata`

Hierarchy of legal entities. Self-referential via `parent_entity_id`.

| Column | Type | Notes |
|--------|------|-------|
| `entity_id` | UUID PK | Stable identifier |
| `name` | VARCHAR(255) | Human-readable name — must be unique per group |
| `parent_entity_id` | UUID FK → self | NULL = ultimate parent |
| `ownership_pct` | NUMERIC(7,4) | Parent's ownership % (0–100) |

### `reporting_periods`

Named time windows for consolidation runs.

| Column | Type | Notes |
|--------|------|-------|
| `period_id` | UUID PK | |
| `label` | VARCHAR(50) | e.g. `FY-2024`, `Q3-2025` — unique |
| `period_start` | DATE | First day of period |
| `period_end` | DATE | Last day — used as accounting boundary |
| `status` | ENUM | `open` (default) or `locked` |

### `ledger_entries`

Append-only financial journal. Every posting — source entries and elimination
entries — lives here.

| Column | Type | Notes |
|--------|------|-------|
| `entry_id` | UUID PK | |
| `timestamp` | TIMESTAMPTZ | UTC wall-clock time of recording |
| `entity_id` | UUID FK → entity_metadata | |
| `account_code` | VARCHAR(64) | Global Chart of Accounts code |
| `amount` | NUMERIC(19,4) | Positive = debit |
| `is_elimination` | BOOLEAN | True for IFRS 10 elimination entries |
| `period_id` | UUID FK → reporting_periods | Nullable — links entry to a period |
| `metadata` | JSONB | Source file, counterparty IDs, description |

---

## 5. Key Flows

### 5.1 Ingestion

```
CSV upload
    │
    ├─ parse_csv()          — Pandas read, normalise column names
    ├─ map_trial_balance()  — lookup (entity_name, local_code) → GCoA code
    │                         via gcoa_map.py
    ├─ split_records()      — separate mapped entries from unmapped codes
    └─ commit_entries()     — INSERT into ledger_entries
                              (resolves entity name → UUID,
                               validates period is open)
```

Unmapped codes are returned in the `UploadSummary` response for human review.
They are not committed to the ledger.

### 5.2 Consolidation

```
POST /consolidate/{period_id}
    │
    ├─ Load non-elimination ledger_entries for period
    ├─ Load all entity_metadata rows
    ├─ Build submission warnings (entities with zero entries)
    ├─ POST engine /consolidate  ← HTTP call to engine service
    │       │
    │       └─ IfrsCalculator.eliminate(entries, entities, as_of)
    │               ├─ Step 1: Interco receivable/payable elimination
    │               ├─ Step 2: Equity elimination + NCI split
    │               ├─ Step 3: Dividend elimination
    │               └─ Step 4: Interco revenue/COGS elimination
    │
    └─ INSERT elimination entries → ledger_entries (is_elimination=True)
```

### 5.3 Report

```
GET /report/{period_id}
    │
    ├─ Load ALL ledger_entries for period (source + eliminations)
    ├─ Sum amounts by account_code
    ├─ Classify accounts into BS sections (assets/liabilities/equity)
    │   and IS sections (revenue/cogs/opex) by account prefix
    └─ Return ConsolidatedReport JSON
           ├─ balance_sheet   — {assets, liabilities, equity}
           ├─ income_statement — {revenue, cogs, operating_expenses}
           ├─ eliminations_summary
           └─ warnings        — entities with no submissions
```

---

## 6. IFRS 10 Elimination Logic

The elimination rules are implemented in `engine/calculator.py` and documented
in detail in **[consolidation-logic.md](consolidation-logic.md)**.

Summary of the four steps:

| Step | IFRS ref | What is eliminated |
|------|----------|--------------------|
| 1. Interco balances | IFRS 10.B86(a) | `INTERCO_REC` ↔ `INTERCO_PAY` between any two group entities |
| 2. Equity + NCI | IFRS 10.22, B86(d) | Parent's `INVEST_SUB` vs subsidiary's `EQUITY_*`; NCI share posted to `NCI_EQUITY` |
| 3. Dividends | IFRS 10.B86(b) | `DIVIDEND_PAID` on subsidiary ↔ `DIVIDEND_REC` on parent |
| 4. Interco revenue | IFRS 10.B86(c) | `INTERCO_REV` on seller ↔ `INTERCO_COGS` on buyer |

### NCI (Non-Controlling Interests)

When a subsidiary is less than 100% owned, the equity elimination splits into:
- **Parent's share** — `equity × (ownership_pct / 100)` — eliminated against `INVEST_SUB`
- **NCI share** — `equity × (1 - ownership_pct / 100)` — posted to `NCI_EQUITY` (remains on the consolidated balance sheet)

### Account Code Conventions

| Code prefix | Normal balance | Meaning |
|-------------|---------------|---------|
| `INTERCO_REC` | Debit (+) | Intercompany receivable |
| `INTERCO_PAY` | Credit (−) | Intercompany payable |
| `INVEST_SUB` | Debit (+) | Parent's investment in subsidiary |
| `EQUITY_*` | Credit (−) | Any equity account of the subsidiary |
| `NCI_EQUITY` | Credit (−) | Non-controlling interest equity |
| `DIVIDEND_PAID` | Debit (+) | Dividend paid by subsidiary to parent |
| `DIVIDEND_REC` | Credit (−) | Dividend received by parent from subsidiary |
| `INTERCO_REV` | Credit (−) | Intragroup revenue (seller entity) |
| `INTERCO_COGS` | Debit (+) | Intragroup cost of goods sold (buyer entity) |

All codes above must include `counterparty_entity_id` or `subsidiary_entity_id`
in the entry's `metadata` JSONB column for the calculator to match pairs correctly.

---

## 7. Validation Architecture

The system has three layers of validation:

### Layer 1 — Unit tests (`engine/tests/test_calculator.py`)

27 pytest tests covering every elimination step in isolation. No database,
no HTTP — pure Python. Run with:

```bash
cd engine && python3 -m pytest tests/test_calculator.py -v
```

### Layer 2 — Independent reference validator (`engine/validator.py`, `engine/audit.py`)

A **completely separate implementation** of the consolidation logic using
Pandas-based spreadsheet arithmetic. Takes the same inputs as `IfrsCalculator`
and independently computes expected eliminations. A test harness
(`engine/tests/test_validator.py`) cross-checks both implementations against
each other and asserts the mathematical invariant:

> **Consolidated trial balance must net to zero: assets + liabilities + equity = 0**

This is the key IFRS integrity check. Any divergence between the engine and the
reference validator, or any non-zero balance sheet sum, is a defect.

### Layer 3 — API regression tests (`backend/tests/test_api_regression.py`)

End-to-end tests using FastAPI's `TestClient` against a real (SQLite or
PostgreSQL) database. Covers the full HTTP surface:
- Entity CRUD including delete and duplicate-name guard
- Period lifecycle including lock enforcement
- Ingestion happy path and error cases
- Consolidation orchestration
- Report structure validation

---

## 8. Global Chart of Accounts (GCoA)

Each subsidiary uses its own local account codes. The ingestion service maps
these to a **Global Chart of Accounts** via `backend/ingestion/gcoa_map.py`.

GCoA number ranges:

| Range | Category |
|-------|----------|
| `1xxx` | Assets |
| `2xxx` | Liabilities |
| `3xxx` | Equity |
| `4xxx` | Revenue |
| `5xxx` | Cost of Sales |
| `6xxx` | Operating Expenses |
| `7xxx` | Other Income / Expense |
| `INTERCO_*`, `INVEST_*`, etc. | Consolidation-specific accounts |

Rows with no GCoA mapping are flagged as `unmapped_codes` in the ingestion
response and excluded from the ledger. They do not cause an error — the CFO
can review and re-map them.

---

## 9. Security and Auditability

- **Append-only ledger** — no financial data is ever modified or deleted.
  The full history of every posting is always available.
- **Period locking** — once a period is locked, no new entries can be ingested.
  Consolidation results become immutable.
- **Deterministic re-runs** — running `POST /consolidate` twice on the same
  period produces the same elimination entries (idempotent by design).
- **Elimination audit trail** — every elimination entry in `ledger_entries`
  carries `is_elimination=True` and `metadata.elimination_type`, making the
  reason for each posting fully traceable.

---

## 10. Local Development

### Prerequisites

- Podman (rootless) + `podman-compose`, **or** Docker + `docker compose`
- Python 3.12+ (for running tests locally)

### Start the stack

```bash
git clone git@github.com:etxnija/consolidator.git
cd consolidator
cp .env.example .env
podman-compose up --build
```

| Service | URL |
|---------|-----|
| Streamlit UI | http://localhost:8501 |
| API + Swagger | http://localhost:8000/docs |
| Engine | http://localhost:8001/docs |

### Run tests

```bash
# Engine unit tests (no database needed)
cd engine && python3 -m pytest tests/ -v

# Backend tests
cd backend && python3 -m pytest tests/ -v
```

### Demo seed data

Pre-built Trial Balance CSVs for a 3-entity group (ParentCo, SubA, SubB) are
in `demo/`. Entity names must match **exactly** (case-sensitive) when creating
entities in the UI, as the GCoA mapping is keyed on entity name.

```
demo/
├── parentco_simple.csv   — ParentCo TB (no interco metadata)
├── suba_simple.csv       — SubA TB
├── subb_simple.csv       — SubB TB (75%-owned)
├── parent.csv            — ParentCo TB with full interco metadata
├── sub_a.csv             — SubA TB with full interco metadata
├── sub_b.csv             — SubB TB with full interco metadata
└── seed.sh               — curl script: creates group + period + ingests all 3
```

---

## 11. Document Index

| Document | Contents |
|----------|----------|
| [consolidation-logic.md](consolidation-logic.md) | Detailed IFRS 10 elimination rules, worked examples, account conventions |
| [roadmap.md](roadmap.md) | Investor demo roadmap, current state assessment, prioritised backlog |
| [demo.md](demo.md) | Step-by-step demo walkthrough (curl + Swagger UI) |
| **architecture.md** _(this file)_ | System design, data model, flows, validation |
