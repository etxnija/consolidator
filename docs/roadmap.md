# North Star Consolidator — Investor Demo Roadmap

_Date: 2026-03-26_

---

## 1. Current State Assessment

### What Works (Backend — Solid)

The backend is functionally complete for the demo story:

| Capability | Status |
|---|---|
| Entity management (create / tree / PATCH ownership) | ✅ Done |
| Reporting periods (create / list / lock) | ✅ Done |
| CSV ingestion with GCoA mapping | ✅ Done |
| IFRS 10 engine — 4 elimination steps | ✅ Done |
| Intercompany receivable/payable elimination | ✅ Done |
| Equity elimination with NCI split | ✅ Done |
| Dividend elimination | ✅ Done |
| Interco revenue/COGS elimination | ✅ Done |
| Consolidated report endpoint (BS + P&L + eliminations) | ✅ Done |
| Immutable ledger (PG trigger) | ✅ Done |
| Period locking | ✅ Done |
| Docker / Podman compose stack | ✅ Done |

### What's Missing (Demo-Blockers)

| Gap | Severity | Notes |
|---|---|---|
| Frontend uses hardcoded `SUBS_01`–`SUBS_10` IDs; ignores entity API | 🔴 CRITICAL | CFO can't use the UI end-to-end |
| No entity / period management in frontend | 🔴 CRITICAL | Can't drive the demo story from UI |
| No report display in frontend (P&L, BS, NCI) | 🔴 CRITICAL | "Sees" step of demo story not reachable |
| No seed data script or sample CSVs | 🔴 CRITICAL | Demo requires live data already loaded |
| No one-click demo launcher | 🟠 HIGH | Curl commands are not investor-friendly |
| No export (PDF / Excel) | 🟠 HIGH | CFOs expect to download a report |
| Goodwill residual is implicit (not posted to GOODWILL account) | 🟡 LOW | Visible mismatch confuses finance audience |
| No frontend entity ownership-tree visualisation | 🟡 LOW | Nice visual for the "group structure" step |

---

## 2. Demo Story

> **"A CFO onboards 3 subsidiaries (one 75%-owned) and consolidates to a clean
> P&L and Balance Sheet showing NCI — in under 60 seconds, from a browser."**

### Scene-by-Scene

| # | Scene | Actor | System action |
|---|---|---|---|
| 1 | Open dashboard, see green health | CFO | Streamlit loads, backend/engine healthy |
| 2 | Create group: ParentCo + SubA (100%) + SubB (75%) | CFO (UI form) | `POST /entities` ×3 |
| 3 | Create period "FY-2024" | CFO (UI form) | `POST /periods` |
| 4 | Upload 3 pre-built CSVs (one per entity) | CFO (file picker) | `POST /ingest/{entity_name}?period_id=…` ×3 |
| 5 | Click "Consolidate" | CFO (button) | `POST /consolidate/{period_id}` → engine runs eliminations |
| 6 | See P&L and Balance Sheet with NCI callout | CFO (report panel) | `GET /report/{period_id}` displayed as formatted tables |
| 7 | Click "Export to Excel" | CFO (button) | Download `.xlsx` |
| 8 | Lock the period | CFO (button) | `POST /periods/{period_id}/lock` |

Target elapsed time: **< 60 seconds** (data is pre-staged in CSVs; steps 2-8 are UI clicks).

---

## 3. Prioritised Backlog

Beads to file, in execution order. Dependencies shown with `←`.

---

### P0 — Demo-Blockers (must be done before any investor demo)

#### `co-ui-entities` — Entity & period management UI
**Type:** feature
**Effort:** M
Rewrite the Streamlit sidebar/main to use the entity API:
- Form: create entity (name, parent dropdown, ownership %)
- Display ownership tree (nested list from `/entities/tree`)
- Form: create reporting period (label, start/end dates)
- Period selector for all subsequent operations

#### `co-ui-ingest` — Ingestion UI linked to real entity IDs  ← `co-ui-entities`
**Type:** feature
**Effort:** S
Replace hardcoded `SUBS_01`–`SUBS_10` dropdown with a live entity list pulled from `/entities`. Pass the resolved `entity_name` (or UUID) and selected `period_id` to the ingest endpoint.

#### `co-ui-report` — Consolidated report display ← `co-ui-ingest`
**Type:** feature
**Effort:** M
After consolidation, display:
- Balance Sheet table (assets / liabilities / equity with NCI_EQUITY highlighted)
- Income Statement table (revenue / COGS / opex)
- Eliminations summary (collapsible)
- Warnings panel (entities with no submissions)
- "Consolidate" button that calls `POST /consolidate/{period_id}`
- "Lock Period" button

#### `co-seed-data` — Sample data: 3-entity group + realistic CSVs
**Type:** task
**Effort:** S
Produce under `demo/`:
- `demo/parent.csv`, `demo/sub_a.csv`, `demo/sub_b.csv` — realistic trial balances with interco balances, equity accounts, and a dividend from Sub B
- `demo/seed.sh` — curl script that creates the group, period, ingests all 3 CSVs, runs consolidation, and prints the report URL (should complete in < 30 s)

---

### P1 — High Value (should be done for a strong demo)

#### `co-export-excel` — Excel export of consolidated report ← `co-ui-report`
**Type:** feature
**Effort:** M
Add a backend endpoint `GET /report/{period_id}/export?format=xlsx` that returns an `.xlsx` file with:
- Sheet 1: Balance Sheet
- Sheet 2: Income Statement
- Sheet 3: Eliminations detail
Hook a download button in the Streamlit frontend (`st.download_button`).

#### `co-demo-launcher` — One-click demo script ← `co-seed-data`
**Type:** task
**Effort:** S
Add `Makefile` targets:
```
make demo-up     # docker compose up --build + wait for healthy
make demo-seed   # run demo/seed.sh
make demo-open   # open http://localhost:8501 in browser
make demo        # all three in sequence
```
Target: `make demo` completes first-run setup and opens the dashboard in < 90 s on a modern laptop.

---

### P2 — Nice-to-Have (polish for repeated demos / follow-up)

#### `co-goodwill-posting` — Explicit goodwill account
**Type:** feature
**Effort:** S
In `engine/calculator.py` `_eliminate_equity`, when `invest_amount ≠ parent_share`, post the residual to a `GOODWILL` account (positive = goodwill asset; negative = bargain purchase). Update `_BS_ASSET_PREFIXES` in the consolidation router to classify `GOODWILL`.

#### `co-ui-entity-tree-viz` — Visual ownership tree in dashboard
**Type:** feature
**Effort:** S
Render a simple indented-tree widget (or Graphviz/mermaid via `st.graphviz_chart`) from `/entities/tree`. Shows group structure at a glance without reading JSON.

#### `co-ui-period-lock-guard` — UI feedback when period is locked
**Type:** feature
**Effort:** XS
When a locked period is selected, disable the Upload and Consolidate buttons and show a banner: "Period FY-2024 is locked. Create a new period to restate."

---

## 4. Implementation Order

```
co-seed-data
  └─ co-demo-launcher

co-ui-entities
  └─ co-ui-ingest
       └─ co-ui-report
            └─ co-export-excel

(parallel) co-goodwill-posting
(parallel) co-ui-entity-tree-viz
(parallel) co-ui-period-lock-guard
```

The P0 beads are two parallel tracks (seed data + UI). Both must be complete before a live investor demo is possible.

---

## 5. Definition of "Demo-Ready"

A session is demo-ready when ALL of the following are true:

- [ ] `make demo` completes without error on a fresh clone (no pre-existing Docker volumes)
- [ ] CFO can run the full scene-by-scene demo from the Streamlit UI without touching a terminal
- [ ] The report displays NCI_EQUITY as a distinct line item with the correct 25% minority share
- [ ] Excel export downloads a readable multi-sheet workbook
- [ ] Total elapsed time (scenes 2–8) is under 60 seconds on a prepared demo machine

---

## 6. Out of Scope for Demo

- Multi-currency / FX translation (post-seed roadmap item)
- User authentication / multi-tenant
- Historical restatements / reversing entry UI
- Goodwill amortisation / impairment testing
- XBRL / iXBRL output
