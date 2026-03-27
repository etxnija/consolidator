# North Star Consolidator — Solution Architect Technical Review

_Prepared by: Solution Architect_
_Review date: 2026-03-27_
_Codebase reviewed: `rig/` (backend, engine, frontend, docker-compose)_

---

## Executive Summary

North Star Consolidator has a technically sound conceptual architecture. The append-only ledger design is correct for a financial audit product, the engine boundary is well-drawn, and the test suite demonstrates unusual maturity for a product at this stage. However, the system is missing every security primitive required for a multi-tenant SaaS, the data model has no tenant isolation, and several schema decisions will be painful to migrate once data accumulates. This review documents where the foundations are strong, where they are missing, and the minimum work required before a first paying customer can safely use the product.

---

## 1. Architecture Soundness

**Verdict: Correct in design, incomplete in execution.**

The three-tier decomposition — stateless engine, orchestrating backend, append-only ledger — is the right architecture for a statutory financial SaaS. Each tier has a defensible rationale:

- The engine as a pure function (inputs in, elimination entries out, no I/O) is the correct pattern for calculation logic that must be auditable, replayable, and independently verifiable. This is not over-engineering; it is exactly the separation that audit regulators will ask about.
- The backend as the sole writer to the ledger is the correct place to enforce immutability, validate period state, and gate access. All mutation flows through one service.
- PostgreSQL as the persistence layer with a NUMERIC(19,4) monetary type and a DB-level immutability trigger is the right choice for statutory data.

**The append-only ledger is well-implemented.** The dual enforcement — application-layer hook in `database.py` (`_block_unsafe_ddl`) and a PostgreSQL trigger `trg_ledger_entries_immutable` defined in `models.py` — means that even a developer with direct DB access cannot accidentally mutate financial history. The trigger DDL is idempotent and fires on `after_create`, so it survives schema recreation. This is genuinely good work.

**The separation of concerns in routing is clean.** Each router has a single responsibility. The ingestion router (`ingestion/app.py`) owns CSV parsing and mapping. The consolidation router owns orchestration and reporting. The entity and period routers own their lifecycles. There is no cross-contamination.

**Where the architecture is incomplete:**

- There is no migration framework. `Base.metadata.create_all()` runs on every startup. This is acceptable for dev, but it means any schema change in production requires either a destructive drop-and-recreate, or manual SQL. Alembic is absent and must be introduced before the first schema migration.
- The `entity_metadata` table has no `unique` constraint on `name`. The architecture documentation claims names must be unique per group, but the ORM model does not enforce it at the database level. The `create_entity` endpoint does not check for duplicates. Duplicate entity names will silently corrupt GCoA mapping, because ingestion resolves entity names to UUIDs via an exact name match.
- Period overlap is not enforced. Two reporting periods can share the same date range. Nothing prevents `period_start`/`period_end` from overlapping, which could produce ambiguous report results.
- The `period_id` column on `ledger_entries` is nullable. This means entries can exist outside any reporting period. The ingestion path allows this (period_id is an optional query parameter). Entries with no period are invisible to every consolidation and reporting query. This is likely a data quality risk rather than a design intention.

---

## 2. Scalability and Multi-Tenancy

**Verdict: Absent. This is a blocking issue for any SaaS deployment.**

The system has no concept of a tenant. Every entity, every ledger entry, every reporting period is in a shared database with no tenant discriminator column. The practical consequences:

- Any authenticated user (when authentication is added) can read or modify any other customer's financial data.
- There is no way to onboard a second customer without their data being comingled with the first customer's data at the query level.
- Row counts and query plans will degrade as all customers' data accumulates in the same tables.

**How serious is this?** For a single-tenant pilot with one trusted internal user, it is manageable as a known limitation. For any multi-tenant SaaS deployment, even with two customers, it is an unacceptable data isolation failure. IFRS consolidation data is commercially sensitive and in many jurisdictions subject to data protection obligations. A data leak between tenants would be a material incident.

**The recommended path to multi-tenancy:**

There are two standard approaches and a hybrid.

_Option A: Schema-per-tenant._ Each customer gets their own PostgreSQL schema (not database). Connections switch schema at the session level. Migrations run per schema. This provides strong isolation, simple backup per tenant (pg_dump a schema), and easy offboarding. The downside is operational complexity at scale (hundreds of schemas) and cross-tenant reporting is harder. For a product targeting 2–20 entities per group and an expected customer count in the tens to low hundreds, this is the recommended approach.

_Option B: Row-level security (RLS) with a tenant_id column._ Every table gets a `tenant_id UUID NOT NULL` column. PostgreSQL RLS policies enforce that every query sees only rows for the current tenant. This is SQLAlchemy-compatible via session-level `SET app.tenant_id = '...'`. It scales to thousands of tenants and is simpler operationally. The downside is that a misconfigured RLS policy or a forgotten `SET` call exposes all tenants.

_Recommendation:_ For North Star's target market (small-to-mid CFO teams, statutory filing), schema-per-tenant is the right choice. The customer count is manageable, isolation is clean, and the operational model fits a SaaS with per-customer onboarding. Begin with a `tenant_id` column on all tables as a stepping stone, and migrate to schema-per-tenant before the second customer goes live.

**The migration cost is significant.** Every existing table needs a `tenant_id` column added. Every query in every router needs a tenant filter. The session injection point (API authentication middleware) needs to extract and validate the tenant. The longer this is deferred, the more queries exist without tenant filtering and the more likely a gap is missed. This work must be planned for the first production release.

---

## 3. Security

**Verdict: No security posture exists. No customer should touch this system in its current state.**

The security gap list is complete:

- No authentication on any endpoint. Any HTTP client that can reach port 8000 can read all financial data, create entities, ingest data, run consolidations, and lock periods.
- No authorisation. There are no roles, no permissions, no concept of who can do what.
- No API keys, no JWT validation, no session management.
- The backend exposes a Swagger UI at `/docs` with full API documentation to unauthenticated callers — useful for development, an attack surface in production.
- The engine service (port 8001) is also fully exposed with no authentication. In the docker-compose definition, both ports 8000 and 8001 are mapped to the host. A caller can bypass the backend entirely and call the engine directly.
- No rate limiting. The ingestion endpoint accepts arbitrary file uploads with no size cap beyond what FastAPI's default allows.
- The frontend makes all API calls with the Python `requests` library over plain HTTP within the container network. This is acceptable within a trusted Docker network, but there is no TLS termination layer defined anywhere.
- Database credentials are hardcoded in `database.py` as a fallback: `postgresql+psycopg2://consolidator:consolidator@localhost:5432/consolidator`. If `DATABASE_URL` is not set, the app connects with well-known default credentials.

**Minimum viable security posture before any customer can use this system:**

1. Add API key authentication to the backend. Even a static shared secret in an `Authorization: Bearer` header, validated in FastAPI middleware, closes the unauthenticated access gap. This is a one-day implementation.
2. Remove the engine port mapping from `docker-compose.yml` in production. The engine should only be reachable by the backend on the internal container network. Port 8001 should not be exposed to the host.
3. Enforce `DATABASE_URL` from environment. Remove the hardcoded fallback credentials, or replace them with a value that will obviously fail (empty string), so that a misconfigured deployment fails fast rather than silently connecting with default credentials.
4. Disable Swagger UI (`/docs`) in production. FastAPI makes this a one-line change: `FastAPI(docs_url=None, redoc_url=None)` when `ENV=production`.
5. Add a file size limit to the ingestion endpoint to prevent resource exhaustion via large CSV uploads.
6. TLS termination must be added at the ingestion layer (nginx or a cloud load balancer) before any data leaves the internal network.

For a product handling statutory financial data, items 1–3 above are the non-negotiable minimum. Items 4–6 are required before any network-accessible deployment.

---

## 4. Data Model

**Verdict: The ledger design is sound. Several missing constraints will cause problems at scale.**

**What is correct:**

- NUMERIC(19,4) for `amount` is appropriate. It provides 15 digits before the decimal point and 4 decimal places, covering any realistic monetary amount without floating-point error. The use of Python's `Decimal` type throughout the calculation layer is consistent with this.
- TIMESTAMPTZ for `timestamp` is correct. All times are stored in UTC, avoiding the timezone ambiguity that corrupts historical records when servers move regions.
- UUID primary keys are the right choice for an append-only ledger. Sequential integer PKs would create contention under concurrent ingestion and are not portable across tenants.
- The JSONB `metadata` column is a reasonable escape hatch for counterparty IDs and elimination metadata. It avoids over-normalisation at this stage while preserving queryability. The GIN index that would normally accompany a JSONB column is absent (see below).
- The DB-level immutability trigger is correctly structured and idempotent.
- ONDELETE="RESTRICT" on `entity_metadata.entity_id` and `reporting_periods.period_id` foreign keys is correct — the database will refuse to delete an entity or period if ledger entries reference it.

**Missing constraints and indexes:**

- `entity_metadata.name` has no `unique=True` constraint at the database level. The architecture requires unique names per group, but the ORM model does not declare this. Any SQL INSERT can create duplicate names, and the API endpoint does not check for them. This must be a database-level unique constraint, not just application logic, to be reliable under concurrent inserts.
- There is no composite index on `(period_id, is_elimination)` on `ledger_entries`. The two most frequent queries — "load all source entries for a period" (consolidation) and "load all entries for a period" (reporting) — both filter on these two columns. With a large ledger, full scans on this table will become the primary performance bottleneck. The existing separate indexes on `period_id` and `entity_id` help but do not cover the combined filter pattern.
- There is no GIN index on `metadata` (JSONB). The engine relies on `metadata.counterparty_entity_id` and `metadata.subsidiary_entity_id` for all elimination matching, but the matching is done in Python after loading entries from the DB. If these fields ever need to be queried at the SQL level (e.g. for audit queries, or for a future incremental elimination approach), an unindexed JSONB column will be a full-table scan.
- `ownership_pct` on `entity_metadata` has no CHECK constraint enforcing the range 0–100. The Pydantic schema in `entities/router.py` applies `ge=0, le=100`, but this is only enforced at the API layer. A direct database insert, a future data migration, or a bug in a new endpoint could store an invalid ownership percentage that would silently produce wrong elimination amounts.
- There is no constraint preventing `period_end < period_start`. The `periods/router.py` endpoint checks this at the application layer, but the database does not.

**Schema decisions that will be painful to migrate later:**

- The absence of a `tenant_id` column on all three tables is the most significant future migration. Adding a NOT NULL column with no default to a table with existing data requires a multi-step migration (add nullable, backfill, add constraint). The longer this is deferred, the larger the backfill job.
- The use of `Base.metadata.create_all()` with no migration framework means the first schema change (adding `tenant_id`, adding missing constraints, adding indexes) will require careful manual SQL in production. Alembic should be introduced now, while the schema is still small.
- The ENUM type `period_status` is defined inline in SQLAlchemy. PostgreSQL ENUM types are notoriously awkward to extend — adding a new status value (e.g. `archived`, `in_review`) requires `ALTER TYPE`, which is not transactional in older PostgreSQL versions and requires Alembic-specific handling.

---

## 5. The Engine Micro-Service

**Verdict: The architectural boundary is correct. The HTTP coupling is a weakness at the current scale.**

**What is right:**

The decision to make the engine a stateless, pure-function service is architecturally correct and, importantly, is actually implemented as described. The `IfrsCalculator` class has no database connection, no global state, and no side effects. It takes a JSON snapshot and returns elimination entries. This means:

- The calculation logic is fully unit-testable without a database (Layer 1 tests confirm this).
- A second, independent implementation (`PandasValidator`) can cross-check the primary implementation. This is genuinely valuable for a statutory product — it is the software equivalent of a four-eyes check on the maths.
- The engine can be replaced, rewritten, or run in parallel for A/B validation without touching the backend.
- The audit trail in `metadata.elimination_type` is machine-readable and tied to the clear IFRS reference in the documentation.

**What is a weakness:**

The engine is called via synchronous HTTP from the backend's FastAPI handler (`httpx.post(..., timeout=60.0)`). This is a blocking call in what is declared as a `def` (not `async def`) route handler, which means each consolidation request ties up a Uvicorn worker thread for the duration of the engine call. Under concurrent use, this will exhaust the thread pool quickly.

More fundamentally, wrapping a pure Python function in an HTTP service adds latency, a network failure mode, a serialisation/deserialisation cost, and an operational surface (the engine must be deployed, healthchecked, and version-matched to the backend) for a function that could be called directly as a library import. At the current scale — a few users, a few entities, periods run interactively — this is acceptable. At any meaningful scale, or if the payload (all ledger entries for a period) grows large, the HTTP round-trip becomes both a latency problem and a reliability problem.

The engine's `depends_on: backend: condition: service_healthy` in `docker-compose.yml` is also puzzling. The engine declares a dependency on the backend being healthy, but the engine is a pure calculator — it has no dependency on the backend at runtime. This circular-looking dependency (backend depends on postgres, engine depends on backend) suggests the `depends_on` was added to control startup order rather than to reflect a real runtime dependency.

**At what scale does the boundary become a problem:**

- For groups with hundreds of entities and tens of thousands of ledger entries per period, the JSON serialisation of the entire ledger snapshot in `consolidation/router.py` will produce payloads in the tens of megabytes. This is not a theoretical concern — a group with 15 subsidiaries filing quarterly could have 50,000+ entries per period within two years.
- The 60-second timeout on the engine call is a reasonable ceiling for today's data volumes, but it is a hard wall. If a consolidation run exceeds it, the backend returns a 502 to the user with no way to poll for the result. There is no async job pattern, no progress indicator, and no retry mechanism.

**Recommendation:** Keep the engine boundary conceptually, but implement it as a shared Python library imported directly by the backend in the short term. The HTTP service adds operational complexity without meaningful benefit at this scale. When horizontal scaling of the engine becomes a real need, the library can be wrapped in an HTTP service again. The test suite already treats the engine as a library (Layer 1 and Layer 2 tests import it directly), so this change would not require test rewrites.

---

## 6. Deployment and Operations

**Verdict: Dev-ready. Not production-ready. Key observability, backup, and operational concerns are unaddressed.**

**Deployment model:**

The Podman/Docker Compose setup is well-structured for a single-node development deployment. The healthchecks are correct and use appropriate intervals. The use of named volumes for postgres_data ensures data persists across container restarts. The `.env` file pattern for credentials is the right approach for local development.

A production deployment would require:

- A managed PostgreSQL service (RDS, Cloud SQL, Azure Database for PostgreSQL) rather than a containerised postgres instance. The append-only ledger makes managed PostgreSQL's point-in-time recovery (PITR) particularly valuable — you can restore to any second in history.
- A container orchestration layer (Kubernetes, ECS, Cloud Run) with proper resource limits, pod disruption budgets, and rolling deployments. Compose is not a production orchestrator.
- TLS termination at the load balancer or ingress layer for all external traffic.
- Secrets management (AWS Secrets Manager, HashiCorp Vault, or at minimum Kubernetes Secrets) rather than `.env` files.
- Separate backend and engine deployments if horizontal scaling is needed.

**Observability — what is missing:**

- No structured logging. The backend uses FastAPI's default logging, which produces unstructured text. There is no correlation ID that would let you trace a consolidation run across backend, engine, and database logs. In a multi-tenant system, you cannot identify which customer's request caused an error.
- No application metrics. There is no Prometheus instrumentation, no tracking of consolidation run duration, ingestion entry counts, or error rates. The first sign of a performance problem will be a user complaint, not an alert.
- No distributed tracing (OpenTelemetry). The HTTP boundary between backend and engine is a natural trace span boundary, but neither service emits trace data.
- The health endpoint (`GET /health`) returns `{"status": "ok"}` with no database connectivity check. A backend that cannot reach PostgreSQL will report itself as healthy until the first request fails.
- No alerting on immutability violations. The `_block_unsafe_ddl` hook in `database.py` raises a `RuntimeError`, which will surface as a 500 response. There is no alert on this event. An immutability violation in a production ledger should immediately page an on-call engineer.

**Backup and recovery for the append-only ledger:**

The append-only design is actually a significant advantage for backup and recovery. Because no row is ever modified, any consistent database snapshot is a complete point-in-time view of the ledger. Managed PostgreSQL PITR means you can restore to any second. This is worth documenting explicitly as a product strength.

However:
- There is no documented backup policy, no backup schedule, and no tested restore procedure.
- There is no documented recovery time objective (RTO) or recovery point objective (RPO).
- If the postgres container volume is deleted (e.g. `podman volume rm postgres_data`), all financial data is gone with no recovery path in the current setup.

**Recommended minimum production baseline:**
- Daily automated snapshots of the PostgreSQL volume or managed DB, with 30-day retention.
- PITR enabled on the managed DB.
- Documented restore procedure tested before the first customer goes live.
- Alerting on backup failure.

---

## 7. Technology Choices

**Verdict: Mostly correct. Streamlit is the one choice to revisit before growth.**

**FastAPI** — correct choice. The async-capable, type-annotated Python web framework with OpenAPI generation is well-suited for a financial API. The Pydantic validation layer catches malformed inputs at the boundary. The auto-generated Swagger UI at `/docs` is genuinely useful for developer onboarding and manual testing. Keep it.

**SQLAlchemy** — correct choice. The ORM's relationship handling, cascade control, and event hooks (used for the immutability block) are all being used appropriately. The typed `Mapped` columns (SQLAlchemy 2.x style) are good practice and will make future static analysis tooling useful. Keep it. Add Alembic immediately.

**PostgreSQL 16** — correct choice. NUMERIC types, JSONB with GIN indexing, row-level security (for future multi-tenancy), PITR, mature tooling. For statutory financial data, PostgreSQL is the only sensible choice in the open-source space. Keep it.

**Pandas** — used in two contexts. In the ingestion layer (`parse_csv`, `map_trial_balance`), Pandas is used for CSV parsing and column normalisation. This is reasonable for a data-ingestion use case. In the `PandasValidator`, it provides the independent verification implementation. Both uses are appropriate. The dependency on Pandas in the engine image is a minor concern — it adds ~50MB of dependencies to a service that only needs it for the validator, not the calculator. The validator could be separated into a testing-only dependency. Not a blocker.

**Streamlit** — acceptable for an investor demo and internal proof of concept. It is not the right frontend framework for a production financial SaaS. The limitations are fundamental to Streamlit's design:

- Every user interaction reruns the entire Python script from top to bottom. The `@st.cache_data(ttl=5)` calls help but do not eliminate the problem. A CFO with a large group and many periods will experience noticeable rerender lag.
- Streamlit's session model is not designed for multi-tenant, multi-user access. There is no concept of user identity within the Streamlit app — the session state is per-browser-tab, not per-authenticated-user.
- The frontend has no access control layer. It calls the backend with no credentials (since the backend has none to offer), and it exposes all entities and periods to whoever opens the URL.
- Streamlit's UI customisation ceiling is low. The current entity names shown as raw UUIDs in the elimination detail table (truncated to 8 characters with `"..."`) is an example of a UI limitation that would require the whole frontend to be replaced to fix properly.

**Recommendation:** Keep Streamlit for the investor demo. Begin planning a React or Vue frontend backed by the existing FastAPI API as the production UI. The clean API surface makes this straightforward — the backend does not need to change, only the frontend.

**httpx** — used for the engine HTTP call. Correct choice over the older `requests` library for a FastAPI application. No concerns.

---

## 8. What Is Production-Ready Today

Being direct:

**Production-ready today (for a controlled, single-tenant, internal deployment only):**

- The IFRS 10 elimination logic. The four-step calculator is correctly implemented, the account code conventions are sound, and the test coverage is unusually thorough. The dual-implementation cross-validator (IfrsCalculator vs PandasValidator) is a genuine quality assurance differentiator. The mathematical invariant — consolidated trial balance nets to zero — is automatically asserted. This is the core product, and it works.
- The append-only ledger design. The DB-level trigger + application-layer hook combination is robust. The audit trail (every elimination carries `elimination_type` metadata) is correct. Period locking is correctly enforced.
- The API surface. The REST API is well-structured, the Pydantic schemas validate inputs correctly, and the error handling returns appropriate HTTP status codes (404 for unknown entities, 409 for duplicate periods, 423 for locked-period ingestion attempts). The Swagger UI is accurate.
- The test suite. 27 unit tests, an independent cross-validator, and API regression tests that cover the full HTTP surface. This is more test coverage than most SaaS products have at this stage. It provides meaningful confidence in the core calculation logic.

**Cannot handle a real customer with real statutory accounts today:**

- No security. Any system accessible over a network with no authentication cannot be given to a customer.
- No multi-tenancy. A second customer would see the first customer's entities and ledger entries.
- No migration framework. Any schema change (and there are several needed — tenant_id, indexes, constraints) requires manual SQL in production.
- No observability. There is no way to diagnose a problem in production or know that something has gone wrong before a user reports it.
- No backup procedure. Financial data with no tested recovery process is not production data.
- Missing constraints. The lack of a unique constraint on `entity_metadata.name` means duplicate entity names can be created, corrupting GCoA mapping silently.
- Single-currency only. Any group with cross-border subsidiaries reporting in different currencies cannot use this system — there is no IAS 21 FX translation, and the limitation is correctly documented but is a hard blocker for most real-world IFRS 10 consolidations.
- No goodwill explicit posting. When invest_amount differs from equity_amount at acquisition, the residual is implicit in the trial balance. Real statutory accounts require explicit goodwill recognition under IFRS 3.

---

## 9. Recommended Next Technical Steps

Prioritised. Items marked [BLOCKER] must be resolved before any paying customer. Items marked [REQUIRED] must be done before a production SaaS launch. Items marked [STRATEGIC] are medium-term investments.

**[BLOCKER] 1. Add authentication to the backend API**
Minimum: a static API key in `Authorization: Bearer` header, validated in FastAPI middleware. Real target: JWT-based auth with short-lived tokens and refresh. Estimated effort: 2–5 days for JWT. The engine port (8001) must be removed from the host port mapping in production configuration simultaneously.

**[BLOCKER] 2. Add a unique constraint on `entity_metadata.name`**
One line in `models.py` (`unique=True` on the `name` column) plus a database migration. Without this, the GCoA mapping is fragile. Estimated effort: 1 hour plus migration tooling setup.

**[BLOCKER] 3. Introduce Alembic for schema migrations**
This is a prerequisite for every schema change that follows. The `Base.metadata.create_all()` startup call must be replaced with Alembic-managed migrations. Estimated effort: 1–2 days to set up Alembic with an initial migration representing the current schema.

**[BLOCKER] 4. Add a `CHECK` constraint on `ownership_pct` (0–100) at the database level**
Currently enforced only by the Pydantic schema. A Pydantic validation bypass (direct DB access, future endpoint) would silently produce wrong elimination amounts. One-line DDL addition.

**[REQUIRED] 5. Design and implement multi-tenancy**
Recommended path: add `tenant_id UUID NOT NULL` to `entity_metadata`, `reporting_periods`, and `ledger_entries`. Add tenant extraction to the auth middleware. Filter every query by tenant. Plan schema-per-tenant migration for post-MVP. This is the most significant structural change and should begin immediately after authentication is in place. Estimated effort: 1–2 sprints.

**[REQUIRED] 6. Structured logging with correlation IDs**
Add a request ID header (generated on ingress) and include it in every log line across backend and engine. Use Python's `structlog` or configure `logging` to emit JSON. This is the minimum observability needed to diagnose production issues. Estimated effort: 1–2 days.

**[REQUIRED] 7. Add a composite index on `(period_id, is_elimination)` on `ledger_entries`**
The two most frequent queries (consolidation load, report load) filter on both columns. This index will be the single highest-impact performance change as ledger size grows. One-line addition to the model, one Alembic migration. Estimated effort: 2 hours.

**[REQUIRED] 8. Add a database connectivity check to the `/health` endpoint**
The current health check returns 200 regardless of DB state. A backend that cannot reach PostgreSQL should return a 503. A one-query check (`SELECT 1`) in the health handler is sufficient. Estimated effort: 2 hours.

**[REQUIRED] 9. Document and test a backup and restore procedure**
Define RPO/RTO. Configure automated snapshots on whatever PostgreSQL service is used in production. Run a test restore before the first customer. This is not a code change — it is an operations process — but it is required before financial data is entrusted to the system.

**[REQUIRED] 10. Replace Streamlit with a proper frontend for production**
Streamlit is unsuitable for multi-tenant, multi-user production use. The clean FastAPI backend makes this a frontend-only replacement. React or Vue against the existing API. Estimated effort: 4–6 weeks for feature parity.

**[STRATEGIC] 11. Move the engine from HTTP service to shared library**
Import `IfrsCalculator` directly in the backend. Remove the engine as a separate deployed service. This eliminates the network hop, the serialisation cost, the 60-second timeout risk, and the operational complexity of a second deployed service. The HTTP service wrapper can be reintroduced when horizontal scaling of the calculation layer becomes a real requirement. Estimated effort: 2–3 days.

**[STRATEGIC] 12. IAS 21 multi-currency support**
This is a hard blocker for the majority of real IFRS 10 consolidation use cases. It requires FX rates per period, a translation step before consolidation, and translation differences posted to Other Comprehensive Income. This is a significant domain complexity addition — plan as a separate product increment.

**[STRATEGIC] 13. Explicit goodwill posting**
When `invest_amount != equity_amount`, post the residual to a `GOODWILL` or `BARGAIN_PURCHASE` account explicitly. Currently the residual is implicit and invisible to the CFO unless they sum the trial balance manually. This is required for IFRS 3 compliance and for the consolidated balance sheet to be self-explanatory.

**[STRATEGIC] 14. Row-level security as a complement to application-layer tenant filtering**
Once tenancy is implemented at the application layer, add PostgreSQL RLS as a defence-in-depth measure. This ensures that even a query that misses an application-layer tenant filter cannot see another tenant's data. This is appropriate for a product handling statutory financial data.

---

## Summary Assessment

The core financial logic is the product's strongest asset and is implemented to a higher standard than the surrounding infrastructure warrants. The elimination calculator is correct, testable, and independently verified. The append-only ledger is properly designed and enforced.

The surrounding infrastructure has the gaps you would expect from a product that has prioritised getting the financial logic right first. That is a defensible prioritisation for a proof of concept. The gaps — authentication, multi-tenancy, migration tooling, observability — are all solvable with known patterns and predictable effort. None of them require architectural rethinking; they are additions to a foundation that is structurally sound.

The honest assessment: this system could run as a controlled internal tool for a single group's IFRS 10 consolidation today. It cannot be given to a paying customer in its current state. With items 1–9 from the priority list above resolved, it could support an early-access customer under close supervision. Full SaaS readiness requires items 1–10 and the strategic items are needed for the majority of real-world IFRS 10 use cases.

---

_End of review._
