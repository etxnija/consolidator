# QA Strategy — North Star Consolidator

_Last updated: 2026-03-26_

---

## Overview

The consolidator uses three independent layers of automated testing. Each layer
targets a different failure mode and can be run without the others.

```
Layer 1 — Unit tests          engine/tests/test_calculator.py
Layer 2 — Cross-validation    engine/tests/test_validator.py  +  engine/validator.py
Layer 3 — API regression      backend/tests/test_api_regression.py
           (+ standalone)      python -m engine.audit
```

---

## Layer 1 — Unit Tests (`engine/tests/test_calculator.py`)

### What it tests

The `IfrsCalculator` in `engine/calculator.py` in complete isolation — no
database, no HTTP, no external dependencies.

27 tests across 5 test classes:

| Class | Scope |
|-------|-------|
| `TestIntercompanyElimination` | Step 1: INTERCO_REC / INTERCO_PAY matching |
| `TestEquityElimination` | Step 2: INVEST_SUB vs EQUITY_* with NCI |
| `TestCombinedElimination` | All steps together, edge cases (empty ledger, empty entities) |
| `TestEliminationMetadata` | Metadata fields on elimination entries |
| `TestNciElimination` | NCI split at 75% ownership |
| `TestDividendElimination` | Step 3: DIVIDEND_PAID / DIVIDEND_REC |
| `TestIntercoRevenueElimination` | Step 4: INTERCO_REV / INTERCO_COGS |

### How to run

```bash
cd engine
python3 -m pytest tests/test_calculator.py -v
```

### What a failure means

A bug in the core elimination logic — wrong amounts, wrong entity, wrong sign,
or a step silently not running.

---

## Layer 2 — Independent Cross-Validator (`engine/validator.py`)

### The problem it solves

Unit tests only verify that `IfrsCalculator` is consistent with itself. They
cannot detect a systematic error where both the test and the implementation
share the same wrong assumption.

The cross-validator solves this by providing a **completely independent second
implementation** of the IFRS 10 elimination logic.

### Two implementations, one truth

| Implementation | File | Approach |
|----------------|------|----------|
| `IfrsCalculator` | `engine/calculator.py` | Imperative Python — loops, dicts, defaultdict |
| `PandasValidator` | `engine/validator.py` | Vectorised Pandas — groupby, pivot, merge |

Both receive identical inputs (`List[LedgerEntrySnapshot]`, `List[EntityNode]`,
`as_of` datetime) and independently compute elimination entries. The test
harness (`engine/tests/test_validator.py`) asserts that the net elimination
amount for every `(entity_id, account_code)` pair is the same in both outputs,
within a tolerance of 0.0001.

### The mathematical invariant

Beyond comparing the two implementations, the validator asserts a fundamental
accounting property:

> **The consolidated trial balance must net to zero.**
> `sum(all_entries + eliminations) == 0`

This holds whenever the source ledger is balanced (every debit has a matching
credit). If it does not hold, either the source data has an error or the
elimination logic has introduced an imbalance.

This check is implemented in `engine/validator.py` as `assert_trial_balance_zero()`.

### Test scenarios covered

| Class | Scenario |
|-------|----------|
| `TestIntercompanyComparison` | Matched pair, multiple transactions, sibling interco |
| `TestEquityComparison` | 100% ownership, 75% NCI, multiple subsidiaries |
| `TestDividendComparison` | Matched dividend pair, one-sided |
| `TestIntercoRevenueComparison` | Matched REV/COGS pair |
| `TestTrialBalanceInvariant` | Balanced BS nets to zero after eliminations |
| `TestAuditScript` | `audit.py` demo data runs without errors |

### How to run

```bash
cd engine
python3 -m pytest tests/test_validator.py -v
```

### Standalone audit script

`engine/audit.py` runs both implementations against the same data and prints a
side-by-side comparison. Can be used as a post-consolidation sanity check:

```bash
# Built-in demo data
python3 -m engine.audit

# Custom CSV data
python3 -m engine.audit ledger.csv entities.csv 2024-12-31
```

Exit code 0 = all checks passed. Exit code 1 = mismatch or imbalance detected.

CSV input formats:

**ledger.csv:**
```
entry_id, timestamp, entity_id, account_code, amount,
is_elimination, counterparty_entity_id, subsidiary_entity_id
```

**entities.csv:**
```
entity_id, name, parent_entity_id, ownership_pct
```

---

## Layer 3 — API Regression Tests (`backend/tests/test_api_regression.py`)

### What it tests

The full HTTP API surface end-to-end using FastAPI's `TestClient` against a
real test database. Tests the complete request → response cycle including
validation, error handling, and database state.

Coverage:

| Area | Tests |
|------|-------|
| Entity CRUD | Create, list, tree, patch, delete |
| Duplicate entity name | Returns 404 with clear message (not 500) |
| Delete blocked by ledger entries | Returns 409 |
| Period lifecycle | Create, list, lock |
| Locked period enforcement | Ingestion returns 422/423 on locked period |
| Ingestion happy path | CSV uploaded, entries committed, summary returned |
| Ingestion — unknown entity | Returns 404 |
| Consolidation | `eliminations_created > 0` after ingesting data |
| Report structure | Balance sheet, income statement, eliminations present |

### How to run

```bash
cd backend
python3 -m pytest tests/ -v
```

---

## What QA Does NOT Cover (current gaps)

| Gap | Risk |
|-----|------|
| Multi-currency (IAS 21) | Out of scope for this phase |
| Goodwill explicit posting | Residual is implicit — no test asserts GOODWILL account |
| Docker/Podman networking | `ENGINE_URL` misconfiguration (e.g. `localhost` vs service name) is not caught by any automated test |
| Frontend UI behaviour | No Selenium/Playwright tests — UI is tested manually |
| Performance / load | No volume tests against large ledgers |

---

## Running All Tests

```bash
# From repo root
cd engine && python3 -m pytest tests/ -v
cd ../backend && python3 -m pytest tests/ -v

# Standalone audit (demo data)
cd ../engine && python3 -m engine.audit
```

All three should pass before any PR is merged.

---

## Relationship to Architecture

See [architecture.md](architecture.md) §7 for how these three layers fit into
the overall validation architecture, and [consolidation-logic.md](consolidation-logic.md)
for the IFRS 10 rules that the tests verify.
