# Hack Day Story: Building a Financial Consolidation Platform with an AI Agent Team

_Gas Town Hack Day — 2026-03-26_

---

## The Starting Point

At 10:29 on a Thursday morning, we set out to answer a question that most software teams would dismiss as a week-long project: **can a small human–AI team build a production-grade IFRS 10 financial consolidation platform in a single day?**

IFRS 10 is the international accounting standard that governs how multinational companies publish consolidated financial statements. When a parent company owns subsidiaries, they record transactions with each other — loans, dividends, sales of goods. Simply adding all their accounts together double-counts those internal flows. The standard requires **elimination entries** to remove the double-counting so the consolidated view reflects only transactions with the outside world.

This is non-trivial software. It requires:
- A reliable, auditable financial ledger
- A configurable entity hierarchy with ownership percentages
- A stateless, testable calculation engine
- REST APIs, a database, a UI
- Documentation and tests that a CFO or auditor could trust

We had a few hours.

---

## Gas Town: The Multi-Agent Workspace

The secret ingredient was **Gas Town** — a multi-agent coordination system built on top of Claude Code. In Gas Town, the workspace is called a **rig**, and work is tracked as **beads** (lightweight issues). Workers are called **polecats** — AI agents with persistent identities but ephemeral sessions. They spin up for a specific task, commit their work, and disappear. The human plays the role of **Mayor**: setting direction, reviewing output, and unblocking agents when they get stuck.

The coordination model looks like this:

```
Mayor (human + Claude Code)
  ├── PM polecat       → Roadmap, backlog, bead filing
  ├── Dev polecats     → Feature implementation (parallel)
  └── QA polecat       → Test suite, validation, bug reports
```

Work flows as beads. The Mayor dispatches beads to polecats. Polecats push branches, which go through a merge queue (the **Refinery**). When merged, the bead closes.

---

## Phase 1: The Foundation (10:29–11:00)

Before any multi-agent work, we needed a foundation. The Mayor (with Claude Code in plan mode) designed the full architecture:

- **PostgreSQL** as an append-only ledger — financial data is never modified, only extended
- **FastAPI engine** (`port 8001`) — a stateless micro-service wrapping the IFRS 10 calculator, no database connection, pure Python input → output
- **FastAPI backend** (`port 8000`) — orchestration, persistence, all REST endpoints
- **Streamlit frontend** (`port 8501`) — a CFO-facing UI
- **Podman** (rootless containers) for orchestration

The core design insight: **the calculator never touches the database**. It receives an in-memory snapshot of ledger entries and entity relationships, computes elimination entries as pure Python objects, and returns them. This makes it independently testable, replaceable, and auditable.

Three polecats worked in parallel on the foundation:
- One built the SQLAlchemy data models and immutable ledger
- One built the IFRS 10 calculator engine (Step 1: interco balances, Step 2: equity elimination)
- One built the Docker/Podman container setup

By 10:41, the core engine was running.

---

## Phase 2: Making It Useful (11:00–14:00)

A working engine is not a usable product. Phase 2 addressed three gaps:

**1. Entity management** — There was no way to register legal entities or set ownership. The backend had a `entity_metadata` table but no API. A dev polecat built full CRUD: create, list, tree view, patch, delete (with a 409 guard if the entity has ledger entries).

**2. Reporting periods** — All ledger entries shared a raw timestamp. There was no concept of "FY-2024" or "Q3-2025". A dev polecat added a `reporting_periods` table with open/locked states and wired it into the ingestion endpoint so CSV uploads tag entries to a period.

**3. Consolidation orchestration** — The engine and backend were islands. A dev polecat built `POST /consolidate/{period_id}`: load entries from the DB, call the engine via HTTP, persist the returned elimination entries back as `is_elimination=True` rows.

Simultaneously, two more steps were added to the IFRS 10 calculator:
- **Step 3: Dividend elimination** (IFRS 10.B86(b)) — `DIVIDEND_PAID` on subsidiary ↔ `DIVIDEND_REC` on parent
- **Step 4: Interco revenue/COGS elimination** (IFRS 10.B86(c)) — `INTERCO_REV` on seller ↔ `INTERCO_COGS` on buyer

And the equity elimination (Step 2) was upgraded to handle **NCI (Non-Controlling Interests)**: when a subsidiary is less than 100% owned, the equity splits into the parent's share (eliminated) and the NCI share (posted to `NCI_EQUITY` and kept on the consolidated balance sheet).

---

## The PM → Dev → QA Governance Cycle

Midway through the day, we established a formal governance cycle:

1. A **PM polecat** read the codebase, assessed what was missing against IFRS 10 requirements, and filed **9 prioritised beads** covering entity management, the Streamlit UI, demo data, QA testing, and documentation.

2. **Dev polecats** picked up P1 beads in parallel. Because each polecat works in its own git worktree (branch), there are no merge conflicts during development.

3. A **QA polecat** ran an independent validation pass after all P1 beads were merged — filing a full API regression suite (35 tests) using FastAPI's `TestClient` against a real SQLite database.

4. The Mayor reviewed the QA output, fixed bugs found during the process, and closed the cycle.

This cycle happened in a compressed form — one iteration in a few hours rather than a sprint. The key insight is that **the governance structure doesn't change; only the clock speed does**.

---

## Bugs Found and Fixed

Real software has real bugs. Here is what surfaced:

| Bug | Root cause | Fix |
|-----|-----------|-----|
| `ModuleNotFoundError: httpx` | Missing from `requirements.txt` | Added `httpx>=0.27.0` |
| Engine "Connection refused" | Backend used `localhost:8001` inside Docker | Set `ENGINE_URL=http://engine:8001` in `docker-compose.yml` |
| 500 on locked period ingestion | `ValueError` not caught in endpoint | Added `except ValueError` → 422/423 |
| 500 on duplicate entity name | `one_or_none()` blew up on multiple rows | Switched to `all()` + explicit 404 with clear message |
| DELETE entity 500 | Immutability guard blocked `entity_metadata` | Removed `ENTITY_METADATA` from the protected set — only `ledger_entries` is append-only |

Every bug was caught either by the QA polecat's test suite or by the human testing the live stack. None reached production undetected.

---

## Three Independent QA Layers

One of the more interesting design decisions was the **three-layer QA strategy**:

**Layer 1 — Unit tests** (`engine/tests/test_calculator.py`)
27 tests covering every elimination step in isolation. No database, no HTTP — pure Python. Catches logic bugs in the calculator.

**Layer 2 — Independent cross-validator** (`engine/validator.py`)
A completely separate implementation of the same IFRS 10 logic, written in Pandas (groupby, pivot, merge) rather than imperative Python loops. Both implementations receive the same inputs. The test harness asserts they produce the same net elimination for every `(entity, account)` pair. This catches systematic errors where the implementation and its unit tests share the same wrong assumption.

It also asserts the fundamental accounting invariant:
> `sum(all_entries + eliminations) == 0`

A balanced source ledger must produce a consolidated trial balance that nets to zero. If it doesn't, either the source data has an error or the elimination logic introduced an imbalance.

**Layer 3 — API regression tests** (`engine/tests/test_api_regression.py`)
35 tests covering the full HTTP surface end-to-end: entity CRUD, period lifecycle, ingestion error cases, consolidation orchestration, report structure.

Total: **83 tests, 0 failures**.

---

## What Was Built

By 15:52 — about 5.5 hours after the first commit — the repository contained:

| Component | Lines | Description |
|-----------|-------|-------------|
| `engine/calculator.py` | ~250 | IFRS 10 calculator, 4 elimination steps, NCI split |
| `engine/validator.py` | ~180 | Independent Pandas-based cross-validator |
| `engine/audit.py` | ~100 | Standalone CLI audit script |
| `backend/` | ~600 | FastAPI backend — 4 routers, models, ingestion |
| `frontend/app.py` | ~400 | Streamlit UI — entity tree, periods, report |
| `engine/tests/` | ~800 | 83 tests across 3 test files |
| `docs/` | ~700 | Architecture, IFRS logic, QA strategy, demo |

**33 commits. 5 distinct polecats. 1 Mayor. 1 human. 5.5 hours.**

---

## What We Learned

**1. Decomposition is the skill.**
The Mayor's most important job was not writing code — it was breaking the problem into well-defined, independently-deliverable beads. A bead with a clear acceptance criterion is something an AI agent can run with autonomously. A vague bead creates rework.

**2. Domain precision matters.**
IFRS 10 is a legal standard. Getting the NCI split wrong, or the sign convention for `INTERCO_PAY`, produces financial statements that fail an audit. We had to be precise about accounting rules in the design phase — "roughly correct" was not acceptable.

**3. Independent validation catches what unit tests can't.**
The cross-validator (`PandasValidator`) was the most valuable single investment of the day. Unit tests verify that code is consistent with itself. An independent second implementation verifies that the code is consistent with the specification.

**4. Governance cycles scale down.**
PM → Dev → QA is a pattern that works at sprint length (two weeks) and at hack-day length (two hours). The artifact format (beads, branches, merge queue) stays the same; only the cadence changes.

**5. Bugs are cheaper when caught early.**
Every bug in the table above was caught within minutes of the code being merged — either by the test suite or by live testing. The cost of fixing a `requirements.txt` omission is trivial. The cost of that same omission reaching a CFO demo is not.

---

## The Stack

```
Browser (CFO)
     │
     ▼
Streamlit UI  :8501
     │
     ▼
FastAPI Backend  :8000  ──────►  Engine Service  :8001
     │                           (IfrsCalculator — pure Python)
     ▼
PostgreSQL 16
(append-only ledger)
```

All four services run as Podman containers. The engine has no database connection — it is a pure function from ledger snapshot to elimination entries. The backend owns all persistence and orchestration.

---

## Conclusion

A few hours. One accounting standard. Thirty-three commits. Eighty-three passing tests. A working multi-entity IFRS 10 consolidation platform with a full UI, audit trail, and documentation.

The platform is not finished — goodwill, multi-currency translation, and Playwright UI tests are all on the backlog. But it is **real**: it runs, it consolidates, it produces a balance sheet and income statement that net to zero after elimination.

Gas Town made this possible by turning coordination overhead into a system: beads replace verbal task assignments, polecats replace "let me look at that later", and the merge queue replaces the ad-hoc PR review scramble. The human's job shifted from doing to directing — and the output reflected that shift.
