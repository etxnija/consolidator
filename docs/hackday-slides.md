---
marp: true
theme: default
paginate: true
backgroundColor: '#0f1117'
color: '#e8eaf0'
style: |
  section {
    font-family: 'JetBrains Mono', 'Fira Code', monospace;
  }
  h1 { color: #7dd3fc; border-bottom: 2px solid #7dd3fc; padding-bottom: 0.3em; }
  h2 { color: #a5f3fc; }
  h3 { color: #67e8f9; }
  strong { color: #fbbf24; }
  code { background: #1e293b; color: #7dd3fc; padding: 0.1em 0.3em; border-radius: 3px; }
  pre { background: #1e293b; border-left: 4px solid #7dd3fc; }
  table { border-collapse: collapse; width: 100%; }
  th { background: #1e293b; color: #7dd3fc; padding: 0.4em 0.8em; }
  td { padding: 0.3em 0.8em; border-bottom: 1px solid #334155; }
  blockquote { border-left: 4px solid #fbbf24; color: #fbbf24; background: #1e2a14; padding: 0.5em 1em; }
---

# Building a Financial Platform in a Day

## Gas Town Hack Day — 2026-03-26

_An AI agent team, one accounting standard, 5.5 hours_

---

## The Challenge

> "Can we build a production-grade IFRS 10 consolidation platform in a single hack day?"

**IFRS 10** is the international standard for consolidated financial statements.

When a parent owns subsidiaries, internal transactions must be **eliminated** before publishing group accounts.

- A loan from parent appears as an asset **and** a liability → double-counted
- The investment in a subsidiary appears on parent **and** as equity on sub → double-counted

**The calculator must remove all of this without losing the audit trail.**

---

## What We Were Building

```
ParentCo  (100% owns)
  └── SubA  (100% owns)
        └── SubB  (75% owned — NCI!)

Each entity submits a Trial Balance CSV.
The platform produces one consolidated Balance Sheet + Income Statement.
```

Four IFRS 10 elimination steps required:

| Step | What is eliminated |
|------|--------------------|
| 1 | Interco receivables ↔ payables |
| 2 | Parent investment ↔ subsidiary equity (+ NCI split) |
| 3 | Dividends paid ↔ dividends received |
| 4 | Intragroup revenue ↔ cost of goods sold |

---

## Gas Town: The Coordination System

**Gas Town** is a multi-agent workspace built on Claude Code.

```
Mayor (human + Claude)        ← sets direction, reviews, unblocks
  ├── PM polecat              ← roadmap, backlog, bead filing
  ├── Dev polecats × N        ← feature implementation (parallel)
  └── QA polecat              ← tests, validation, bug reports
```

**Beads** = lightweight issues (co-b26, co-f10, co-68z…)
**Polecats** = AI agents — persistent identity, ephemeral sessions
**Refinery** = merge queue — validates and lands branches

_Each polecat works in its own git worktree. No merge conflicts._

---

## The Architecture

```
Browser (CFO)
     │
     ▼
Streamlit UI  :8501
     │ REST
     ▼
FastAPI Backend  :8000  ──── HTTP ────►  Engine  :8001
     │                                   IfrsCalculator
     │ SQLAlchemy                        (pure Python, no DB)
     ▼
PostgreSQL 16
(append-only ledger)
```

**Key design principle:** The calculator is a **pure function**.
Input: ledger snapshot + entity list.
Output: elimination entries.
No I/O. No state. Fully testable without a database.

---

## Phase 1: The Foundation (10:29 – 10:41)

Three polecats working in parallel:

| Polecat | Task |
|---------|------|
| rust | SQLAlchemy models — immutable `ledger_entries` table |
| chrome | IFRS 10 calculator — Steps 1 & 2 |
| ? | Podman container setup |

**First commit:** `10:29:03`
**Engine running:** `10:40:22`

The immutable ledger: two layers of protection.
1. SQLAlchemy event listener blocks `UPDATE`/`DELETE` at the application layer
2. PostgreSQL trigger blocks it at the database layer

_Financial data is never modified. Only extended._

---

## Phase 2: Making It Useful (11:00 – 14:00)

The engine existed. But three things were missing:

**Entity management** — no API to register subsidiaries or set ownership %

**Reporting periods** — no concept of "FY-2024"; just raw timestamps

**Consolidation orchestration** — the engine and backend were islands

Each became a bead. Each bead got a polecat.
All three ran **simultaneously**.

---

## Phase 2: What the Code Added

```python
# Step 2 — Before (100% ownership only)
elim_equity = -equity_amount

# Step 2 — After (NCI split)
parent_share = equity_amount * (ownership_pct / 100)
nci_share    = equity_amount * (1 - ownership_pct / 100)

# → parent_share eliminated against INVEST_SUB
# → nci_share posted to NCI_EQUITY (stays on consolidated BS)
```

Also added:
- **Step 3:** `DIVIDEND_PAID` ↔ `DIVIDEND_REC`
- **Step 4:** `INTERCO_REV` ↔ `INTERCO_COGS`

_4 IFRS 10 elimination steps. Fully implemented._

---

## The PM → Dev → QA Cycle

```
PM polecat reads codebase
    │
    └── Files 9 prioritised beads
            │
    ┌───────┼───────┐
    ▼       ▼       ▼
  Dev     Dev     Dev    (parallel, separate worktrees)
    │       │       │
    └───────┴───────┘
            │
        Merge queue (Refinery)
            │
        QA polecat validates
            │
        Mayor reviews findings
            │
        PM signs off
```

This is a sprint — compressed to a few hours.

---

## Bugs Found and Fixed

| Bug | What happened | Fix |
|-----|--------------|-----|
| `httpx` missing | `ModuleNotFoundError` on first consolidate | Added to `requirements.txt` |
| Engine 503 | Backend called `localhost:8001` inside Docker | `ENGINE_URL=http://engine:8001` |
| 500 on locked period | `ValueError` not caught | `except ValueError` → 423 |
| 500 on duplicate entity | `one_or_none()` exploded | `all()` + explicit 404 |
| 500 on entity delete | Immutability guard blocked `entity_metadata` | Only `ledger_entries` is append-only |

**Every bug was caught within minutes — by tests or live stack testing.**

None reached the demo undetected.

---

## Three Independent QA Layers

**Layer 1 — Unit tests** (27 tests)
The IFRS 10 calculator in isolation. No database, no HTTP.

**Layer 2 — Independent cross-validator** (21 tests)
A completely separate Pandas-based implementation.
Both get the same input. Results must match within 0.0001.

Also asserts the **accounting invariant:**
> `sum(all_entries + eliminations) == 0`
> _A balanced ledger must stay balanced after elimination._

**Layer 3 — API regression** (35 tests)
Full HTTP surface via FastAPI `TestClient`. Real SQLite database.

**Total: 83 tests. 0 failures.**

---

## The Cross-Validator Was the Smartest Investment

```
Unit tests prove:  implementation is consistent with itself
Cross-validator proves:  implementation is consistent with the spec
```

Two different implementations, written independently:

| | `IfrsCalculator` | `PandasValidator` |
|-|-----------------|-------------------|
| Style | Imperative Python — loops, dicts | Pandas — groupby, pivot, merge |
| File | `engine/calculator.py` | `engine/validator.py` |

If they agree → high confidence.
If they disagree → one is wrong, and the test tells you which.

_This catches systematic errors that unit tests cannot._

---

## What We Delivered

| | |
|-|-|
| **Commits** | 33 |
| **Time** | 5h 23m (10:29 → 15:52) |
| **Tests** | 83 passing |
| **Elimination steps** | 4 (full IFRS 10 coverage) |
| **API endpoints** | ~15 |
| **Polecats deployed** | 5 distinct agents |
| **Documents** | 4 (architecture, IFRS logic, QA strategy, demo) |

A working multi-entity IFRS 10 consolidation platform.
Balance sheet and income statement that **net to zero** after elimination.
Full audit trail. CFO-facing UI. Podman-ready.

---

## What We Learned

**1. Decomposition is the skill.**
A well-defined bead with clear acceptance criteria is something an AI can run with. A vague task creates rework.

**2. Domain precision matters.**
"Roughly correct" fails an audit. The NCI split, the sign conventions, the ledger immutability — all had to be exact.

**3. Independent validation > more unit tests.**
The PandasValidator caught what unit tests structurally cannot.

**4. Governance scales down.**
PM → Dev → QA works at sprint length and at hack-day length. The artifact format stays the same; only the clock speed changes.

**5. The human's job shifted.**
From _doing_ to _directing_. Architecture, domain precision, unblocking agents, reviewing output. The code largely wrote itself.

---

## The Numbers That Matter

```
10:29  First commit
10:41  Engine running — IFRS 10 calculator eliminates interco balances
11:00  Phase 2 begins — PM files 9 beads, dev polecats spawn
13:00  Entity API, periods, consolidation endpoint all merged
14:00  Streamlit UI rebuilt — ownership tree, report, period controls
14:30  QA regression suite: 35 tests, all green
15:52  Final bug fixed, PM signs off
```

**5 hours 23 minutes.**
One accounting standard. One human. One Mayor. Five polecats.
A product that works.

---

## Try It

```bash
git clone git@github.com:etxnija/consolidator.git
cd consolidator
cp .env.example .env
podman compose up --build
```

| Service | URL |
|---------|-----|
| Streamlit UI | http://localhost:8501 |
| API + Swagger | http://localhost:8000/docs |
| Engine | http://localhost:8001/docs |

```bash
# Run the full test suite
cd engine && python3 -m pytest tests/ -v
cd ../backend && python3 -m pytest tests/ -v
```

---

# Thank You

_Gas Town Hack Day — 2026-03-26_

**Mayor** (coordinator) · **PM** (roadmap) · **rust × 3** (dev) · **rust** (QA)

```
33 commits  ·  83 tests  ·  5.5 hours  ·  0 audit findings
```

> The platform is not finished.
> But it is **real**.
