# North Star Consolidator — Plan v1

_Created: 2026-03-30_
_Owner: Mayor / Gas Town team_

---

## Objective

Build a solid, production-worthy IFRS 10 consolidation platform capable of serving 1–3 PE-backed Nordic customers. Three phases, each ending with a demo to the founder. Each phase gates on the demo passing before the next begins.

**Scope constraints:**
- IFRS 10 only — K3 deferred until a paying customer justifies commissioning the specification
- Nordic market — no UK/non-Nordic features
- Gas Town is the team — no human hires
- Podman for now — cloud migration when first customer onboards
- Multi-currency via manual exchange rates per period (no live FX API)
- Drill-down: one level (consolidated figure → breakdown by entity)

---

## Phase 1 — Solid Foundation

**Goal:** A secure, multi-tenant system that can be handed to a real customer without embarrassment.

**Gate:** Founder can log in, create a tenant, run a consolidation, and confirm no other tenant can see their data. Backup script produces a verified restore.

**Estimated duration:** ~4 weeks

### Beads

| ID | What | Track |
|----|------|-------|
| 1.1 | JWT authentication on all backend endpoints | security |
| 1.2 | Remove engine port from host mapping in production; disable Swagger UI in prod | security |
| 1.3 | Alembic migration framework — replace `Base.metadata.create_all()` | infra |
| 1.4 | Missing DB constraints: unique entity name, `ownership_pct` CHECK, `period_end > period_start` | infra |
| 1.5 | `tenant_id UUID NOT NULL` on all three tables; middleware extraction; filter every query by tenant | tenancy |
| 1.6 | Structured logging with request correlation IDs (`structlog`) | infra |
| 1.7 | Health endpoint with real DB connectivity check | infra |
| 1.8 | Backup script: `pg_dump` based, automated, tested restore procedure documented | infra |
| 1.9 | QA regression suite updated for auth + tenancy | qa |
| 1.10 | Demo script — Phase 1 | pm |

### Dependencies
- 1.1 must complete before 1.5 (tenant extracted from JWT)
- 1.3 must complete before 1.4 and 1.5 (schema changes require migration trail)
- 1.1 + 1.5 must complete before 1.9 (QA validates both together)
- All 1.1–1.8 must complete before 1.9 and 1.10

### Phase 1 Demo Script

1. `podman compose up --build` — stack starts clean
2. `POST /auth/register` — create a user account, receive JWT
3. `POST /auth/login` — authenticate, confirm token works
4. Create three entities: ParentCo, SubA (100% owned), SubB (75% owned)
5. Create reporting period FY-2026
6. Upload demo CSVs for each entity (from `demo/`)
7. `POST /consolidate/{period_id}` — run consolidation
8. `GET /report/{period_id}` — view consolidated report, confirm NCI_EQUITY > 0
9. Register a second user for a second tenant — confirm they see zero entities and zero periods
10. Run backup script — confirm `pg_dump` completes and restore to a clean instance works
11. Confirm health endpoint returns unhealthy when DB is stopped

---

## Phase 2 — Production Frontend

**Goal:** Replace Streamlit with a React + shadcn/ui dashboard that a CFO would trust.

**Gate:** Founder can complete a full consolidation workflow — entities, CSV upload, consolidation run, report — in the React UI without touching Streamlit.

**Estimated duration:** ~4 weeks

### Beads

| ID | What | Track |
|----|------|-------|
| 2.1 | UX wireframes + interaction spec for all screens | ux |
| 2.2 | React app scaffold — auth flow, routing, shadcn/ui + Tailwind setup | frontend |
| 2.3 | Entity management screens — tree view, create, edit, delete | frontend |
| 2.4 | Period management screens — create, view status, lock | frontend |
| 2.5 | CSV upload + ingestion feedback screen (mapped vs unmapped codes) | frontend |
| 2.6 | Consolidation run screen — trigger, progress indicator, result summary | frontend |
| 2.7 | Consolidated report screen — BS + IS + eliminations, drill-down by entity (one level) | frontend |
| 2.8 | Submission status dashboard — which entities have/haven't submitted for the active period | frontend |
| 2.9 | Trial balance nets-to-zero confirmation visible on report screen | frontend |
| 2.10 | QA regression suite updated — Playwright smoke tests for critical paths | qa |
| 2.11 | Demo script — Phase 2 | pm |

### Dependencies
- 2.1 (wireframes) before any 2.2–2.9 frontend work begins
- 2.2 (scaffold) before all other frontend beads
- 2.3–2.9 can run in parallel once 2.2 is done
- 2.10 after 2.3–2.9 are merged
- Streamlit remains available for internal reference until 2.10 passes

### Phase 2 Demo Script

1. Open browser to `http://localhost:3000` (React app)
2. Log in with credentials created in Phase 1
3. View ownership tree — ParentCo → SubA (100%) → SubB (75%)
4. Check submission dashboard — confirm all three entities show "not submitted" for FY-2026
5. Upload CSV for each entity — confirm ingestion feedback shows mapped/unmapped codes
6. Check submission dashboard — confirm all three show "submitted"
7. Run consolidation from the consolidation screen
8. View consolidated report:
   - Balance sheet with NCI_EQUITY line visible
   - Income statement
   - Eliminations summary
   - Click a consolidated figure — confirm entity-level breakdown appears
   - Confirm "Trial balance nets to zero ✓" indicator is present
9. Lock the period — confirm re-ingestion is blocked
10. Confirm Streamlit (`http://localhost:8501`) still works as fallback

---

## Phase 3 — Core Product Features

**Goal:** The product is correct enough for a PE-backed group's statutory IFRS 10 consolidation.

**Gate:** Founder can run a full PE scenario — parent + two subsidiaries, one partial ownership (75%), acquisition goodwill, one foreign currency subsidiary (SEK parent, EUR subsidiary) — and the output is audit-ready.

**Estimated duration:** ~4 weeks

### Beads

| ID | What | Track |
|----|------|-------|
| 3.1 | Explicit goodwill posting — residual `invest_amount − equity_amount` posted to GOODWILL account with per-subsidiary schedule | engine |
| 3.2 | IAS 21 multi-currency — functional → presentation currency translation; exchange rates from `fx_rates` table (manual entry per period, no live API) | engine |
| 3.3 | Audit package export — multi-sheet Excel download: BS, IS, eliminations detail, source entries per entity | backend |
| 3.4 | Period comparison — current vs prior period side-by-side on report screen | frontend |
| 3.5 | Engine as shared library — remove HTTP micro-service overhead; import `IfrsCalculator` directly in backend | infra |
| 3.6 | DB performance — composite index on `(period_id, is_elimination)`; GIN index on `metadata` JSONB | infra |
| 3.7 | PostgreSQL Row-Level Security — tenant isolation as defence-in-depth layer | security |
| 3.8 | Methodology document — public-facing, auditor-readable description of the elimination engine, dual-validator, and immutable ledger | pm + sa |
| 3.9 | FX rate management UI — per-period closing rates and average rates, editable by CFO | frontend |
| 3.10 | QA regression suite — goodwill, multi-currency, audit export, period comparison | qa |
| 3.11 | Demo script — Phase 3 (full PE scenario) | pm |

### Dependencies
- 3.1 (goodwill) and 3.2 (multi-currency) are engine changes — can run in parallel
- 3.5 (engine as library) should follow 3.1 and 3.2 to avoid double migration
- 3.9 (FX rate UI) depends on 3.2 (multi-currency backend)
- 3.3, 3.4 can run in parallel with engine work
- 3.6, 3.7 are independent infra items
- 3.10 after all feature beads merged
- 3.8 (methodology doc) can be drafted in parallel, finalised after 3.1 and 3.2

### Phase 3 Demo Script

**Scenario:** NordicGroup AB (SEK, listed in Stockholm)
- ParentCo — Swedish holding company, SEK functional currency
- SubA — Swedish operating company, 100% owned, SEK, with an INTERCO_REC vs SubB
- SubB — Finnish subsidiary, 75% owned, EUR functional currency, acquired 18 months ago with goodwill

1. Create the group structure and FY-2026 period (or use existing from Phase 1/2)
2. Set FX rates for FY-2026: EUR/SEK closing rate 11.30, average rate 11.15
3. Upload trial balance CSVs for all three entities (SubB in EUR)
4. Run consolidation
5. View consolidated report:
   - Confirm GOODWILL account appears with correct per-subsidiary amount
   - Confirm NCI_EQUITY reflects 25% of SubB's equity
   - Confirm SubB's EUR amounts translated to SEK at closing rate (BS) and average rate (IS)
   - Confirm trial balance nets to zero after all eliminations
   - Drill down on a consolidated revenue figure — see SubA and SubB contributions
6. View period comparison — FY-2026 vs FY-2025 (if prior period data loaded)
7. Download audit package — open Excel, confirm all sheets present
8. Confirm methodology document is accessible at `/methodology` or equivalent URL

---

## Governance

**Each phase:**
1. PM polecat opens the phase — reads this plan, files beads with acceptance criteria
2. Dev polecats implement in parallel where dependencies allow
3. QA polecat validates — runs regression suite, confirms demo script passes end-to-end
4. Mayor reviews QA output and fixes any blockers
5. Founder runs the demo script — confirms gate is met
6. PM signs off — phase closed, next phase begins

**Architecture docs:** Any architectural change in Phase 1–3 must be reflected in `docs/architecture.md` before the phase closes.

**This plan document** is updated at the end of each phase to reflect what actually happened vs. what was planned.

---

## Open Questions (deferred)

- **K3** — deferred until a paying customer justifies commissioning a K3-qualified accountant to write the specification. Engine isolation makes this a clean future addition.
- **Cloud migration** — Podman + `pg_dump` for now. Revisit when first customer onboards.
- **Accounting firm channel / methodology doc review** — the methodology document (3.8) needs a human accountant to validate it before being shown to an auditor. Not a Gas Town task.
- **Live FX rates** — manual rates per period are sufficient for 1–3 customers. API integration (ECB, Riksbanken) is a future enhancement.

---

_Plan v1. Review after each phase gate._
