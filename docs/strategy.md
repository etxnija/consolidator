# North Star Consolidator — Company Strategy
## Leadership Session Output, 2026-03-27

_Participants: CEO, CPO, CTO, CRO_
_Based on: PM product research (Nordic-revised), CPO feedback memo, SA technical review, investor demo roadmap_

---

## 1. Company Purpose

North Star Consolidator is statutory-grade group consolidation software for Nordic CFOs who have outgrown Excel but cannot justify the implementation project, price, or complexity of Pacera/AARO, Lucanet, or IBM Cognos Controller. We serve owner-operated and PE-backed companies with 2–20 legal entities across Sweden and the broader Nordics — groups whose year-end close is currently a manual, error-prone spreadsheet exercise that costs them SEK 80,000–250,000 in external accountant time and produces no audit trail. We replace that with a self-serve, rules-based consolidation engine that produces immutable, auditable elimination entries under IFRS 10, and — once the K3 module is built — under the Swedish local GAAP standard that the majority of our target customers are actually required to use. We do not claim to be AI. We are a deterministic calculator with a published methodology, independently cross-validated, and designed to produce outputs that a Swedish FAR-accredited auditor will accept.

---

## 2. The 18-Month Ambition

**By September 2027: 30 paying Nordic customers, SEK 4.5m ARR, three completed statutory audits accepted by Big 4 or mid-tier audit firms using North Star as the consolidation record, and a signed accounting-firm partnership with at least one of BDO Sweden, Grant Thornton Sweden, or Azets Scandinavia.**

The audit acceptance milestone is non-negotiable. ARR without audit-accepted reference customers is a fragile commercial position in this market. The accounting firm partnership is the proof point that the channel strategy is working. These three outcomes together — customers, ARR, and audit credibility — define what "established in the Nordic market" means for North Star.

---

## 3. Target Segment — The Beachhead

### The Tension

The CPO and CRO entered this session with different preferred starting points. The CPO argued for Persona C (PE-backed portfolio CFOs) on the grounds that they have genuine IFRS 10 obligations, move quickly, pay well, and the Stockholm PE ecosystem is a concentrated, reachable network. The CRO argued for Persona A (unlisted Swedish mid-market CFOs) on the grounds that the volume is larger, the sales cycle is shorter, and the Fortnox ecosystem creates a scalable inbound channel that does not require a direct sales team at this stage.

The CTO added a complicating constraint: until the K3 module is built, the platform has a compliance gap for unlisted Swedish groups whose statutory obligation is K3, not IFRS 10. Selling Persona A as a statutory tool before K3 is ready exposes the company to legal risk and reputational damage.

The CEO resolved this tension as follows.

### The Decision

**The beachhead is Persona C — PE-backed Nordic CFOs with genuine IFRS 10 obligations — for the first 12 months, while the K3 module is built in parallel.**

The reasoning:

1. Persona C (PE-backed) is the only segment for which the platform's current IFRS 10 scope is the correct statutory standard. These groups elect IFRS to satisfy LP reporting requirements and IPO optionality. Selling to them does not require the K3 module and does not create a compliance gap.

2. PE-backed groups have a clear acute pain: a new acquisition adds entities immediately, goodwill must be tracked, and the sponsor wants consolidated management accounts monthly. The urgency is real and funded.

3. The Stockholm PE ecosystem (EQT, Altor, Triton, Nordic Capital, Verdane, Summa) is a concentrated network of 10–15 operating partners who make or influence finance tool decisions across dozens of portfolio companies. Landing one operating partner relationship is worth five direct Persona A deals in terms of pipeline leverage.

4. Persona C deals (SEK 10,000–25,000/month) are economically meaningful at the ARR targets above. Persona A deals at SEK 6,000–15,000/month require more volume to reach the same ARR.

**From month 12 onward:** Once the K3 module is in production and at least one Persona C audit has been completed, open Persona A (Swedish unlisted mid-market) via the accounting firm and Fortnox channels. The K3 module plus SIE4 import plus Fortnox connector is the unlock for this segment. Running these in parallel as a product investment, not a GTM investment, is the right sequencing.

**Persona B (listed companies) is not the initial target.** The sales cycle is 3–6 months, requires a DPA/data residency review, and the incumbent (Pacera/AARO) has 30% of Nasdaq Stockholm Large Cap. We cannot win this segment without reference customers, and we will not have relevant reference customers from a PE-focused early motion. Revisit after 18 months.

### What This Means for Positioning

North Star's initial positioning is: **"Self-serve IFRS 10 consolidation for PE-backed Nordic portfolio companies — no implementation project, live in a day, audit-ready from the first period."**

The "self-serve Pacera for sub-SEK 500m groups" frame is reserved for the Persona A expansion. Until K3 is ready, using that frame with unlisted Swedish companies creates a compliance misrepresentation.

---

## 4. What We Are NOT Doing in the Next 18 Months

These are explicit scope exclusions, not aspirations deferred. They are commitments that allow the team to say no.

**K3 statutory compliance for external customers — not until month 12–15.** The K3 module (`co-k3-mode`) will be built, but it will not be offered to external customers until it has been reviewed by a K3-qualified Swedish accountant and tested against at least one real statutory consolidation. Selling unlisted Swedish groups on statutory K3 compliance before this is done is a legal risk the company cannot take.

**Listed company segment (Persona B) — not in 18 months.** AARO/Pacera's installed base, the 3–6 month sales cycle, and the IT/legal procurement overhead make this segment uneconomical to pursue before we have audit-accepted references and a DPA framework in place.

**UK or non-Nordic markets — not in 18 months.** The Xero and QuickBooks connectors are explicitly deferred. The product, the GTM, and the compliance scope are Nordic-only for this period. Building for two markets simultaneously at this stage divides focus without proportionate reward.

**Multi-currency (IAS 21) for K3 groups — separate decision.** IAS 21 will be built as a P1 technical item (it is required for IFRS 10 completeness), but the intersection of IAS 21 and K3 multi-currency creates a distinct set of Nordic GAAP edge cases. We will not market K3 + multi-currency as production-ready until both modules have been tested together.

**Enterprise segment (50+ entities, SAP ERP) — not in 18 months.** IBM Cognos Controller and Tagetik own this segment and our product is not architected for it. SAP BAPI connectors and large-group performance tuning are out of scope.

**XBRL / iXBRL regulatory reporting — not in 18 months.** This is the domain of Tagetik and the listed-company tier. Do not scope it.

**Full FP&A / budgeting module — not in 18 months.** Pacera now bundles Mercur (FP&A) post-merger. We will not chase that. Consolidation is the product. Adding planning features at this stage fragments the product and the team.

---

## 5. Technical Strategy — The Path to Customer One

_CTO leads this section._

The SA technical review is unambiguous: the core financial logic is the strongest asset in the codebase, implemented to a higher standard than the surrounding infrastructure deserves. The elimination calculator is correct, the dual-validator is a genuine differentiator, and the append-only ledger is well-designed. None of that saves us if the system has no authentication. The path to customer one is infrastructure, not features.

### Phase 1 — Minimum Viable Security and Tenancy (Weeks 1–6)

These are the items the CTO will not negotiate. No customer touches the system before Phase 1 is complete.

**Authentication (BLOCKER — Week 1–2).** Add JWT-based authentication to the backend API. Remove the engine port (8001) from the host port mapping in production configuration — the engine must only be reachable from within the container network. Remove or randomise the hardcoded database credential fallback in `database.py`. Disable Swagger UI in production (`docs_url=None`). Add a file size cap to the ingestion endpoint. This is 2–5 days of work. It is week one.

**Alembic migration framework (BLOCKER — Week 1–2).** Replace `Base.metadata.create_all()` with Alembic-managed migrations. Every schema change that follows — and there are many — requires this. The CTO will not allow schema changes without a migration trail. This is 1–2 days of work.

**Missing database constraints (BLOCKER — Week 2).** Add `unique=True` on `entity_metadata.name`. Add `CHECK (ownership_pct BETWEEN 0 AND 100)` at the database level. Add `period_end > period_start` constraint. These are one-line DDL additions that prevent silent data corruption. They are not optional.

**Multi-tenancy design and implementation (REQUIRED — Weeks 3–6).** Add `tenant_id UUID NOT NULL` to `entity_metadata`, `reporting_periods`, and `ledger_entries`. Add tenant extraction to the authentication middleware. Filter every query by tenant. Plan the schema-per-tenant migration — recommended approach for North Star's expected customer count (tens to low hundreds). This is 1–2 sprints and is the most significant structural change. It must begin immediately after authentication is in place. A second customer cannot exist without it.

**Structured logging with request correlation IDs (REQUIRED — Week 4).** Every log line across backend and engine must carry a request ID. Without this, diagnosing a production problem requires guesswork. Use `structlog` or equivalent. This is 1–2 days.

**Health endpoint with database connectivity check (REQUIRED — Week 4).** The current `/health` returns 200 even when the database is unreachable. Fix it.

**Tested backup and restore procedure (REQUIRED — before customer one).** Managed PostgreSQL (RDS or equivalent) with PITR enabled. Automated daily snapshots, 30-day retention. A tested restore to a clean instance before the first customer is onboarded. The append-only ledger design makes PITR particularly powerful — document this as a product strength.

**Timeline:** Phase 1 complete in 6 weeks. No customer engagement before then.

### Phase 2 — First Customer Hardening (Weeks 7–16)

Once a customer is engaged for an early-access proof of concept, the following become live requirements:

**IAS 21 multi-currency (P1 product feature).** Any PE-backed Nordic group with subsidiaries in different countries is blocked without this. Swedish parent with Norwegian or Finnish subsidiary is multi-currency by definition (SEK/NOK, SEK/EUR). This is a significant domain complexity addition — treat it as a separate product increment. The CTO estimates 3–5 weeks including testing against real Nordic currency pairs.

**Explicit goodwill posting (P1 product feature).** When `invest_amount ≠ equity_amount`, the residual must be posted to an explicit GOODWILL account with a per-subsidiary schedule. This is a legal risk item: statutory accounts with implicit goodwill are materially misstated. The CTO estimates 1–2 weeks.

**Composite index on `(period_id, is_elimination)`** on `ledger_entries`. The two most-used queries both filter on these columns. Without this index, consolidation run time degrades as the ledger grows.

**GIN index on the `metadata` JSONB column.** The engine relies on `metadata.counterparty_entity_id` for elimination matching. Currently resolved in Python after a full-table load. At production data volumes this will become a bottleneck.

**Replace Streamlit with a proper frontend.** Streamlit cannot support multi-tenant, multi-user, authenticated production use. The clean FastAPI backend makes this a frontend-only replacement. React or Vue against the existing API. The CTO estimates 4–6 weeks for feature parity. Begin planning in Phase 1; execute in Phase 2. This is also the point at which the entity-name-as-UUID UI problem (flagged in the SA review) gets fixed properly.

**Engine as shared library (STRATEGIC — Phase 2).** Move `IfrsCalculator` from an HTTP micro-service to a directly imported library. This eliminates the 60-second timeout risk, the serialisation overhead, the network failure mode, and the second deployed service. The test suite already imports the engine as a library — this change does not require test rewrites. The HTTP service wrapper can be reintroduced when horizontal scaling of the calculation layer is a real requirement. It is not a real requirement today.

**EU data residency confirmation.** Deploy on AWS eu-north-1 (Stockholm) or Azure Sweden Central. Document the hosting location. Produce a standard DPA template. This is a procurement gate for every Persona C deal and every Persona B conversation.

### Phase 3 — Scale (Months 5–18)

**PostgreSQL Row-Level Security as defence-in-depth.** Once application-layer tenant filtering is in place, add RLS as a second layer. A misconfigured query that forgets the tenant filter must not be able to see another customer's data.

**Schema-per-tenant migration.** For North Star's customer count and customer profile (statutory financial data, hard regulatory obligation), schema-per-tenant is the right isolation model. Execute this migration before customer count reaches a point where it becomes operationally difficult.

**K3 mode.** This is a Phase 3 technical investment with Phase 2 research prerequisites (see product strategy). The CTO estimates 4–6 weeks of engine work once the K3 specification is complete.

**Load testing.** 10k/50k/200k entry synthetic datasets against the consolidation endpoint. Define and enforce a <5-second SLA. Required before Persona A volume onboarding.

**Observability stack.** Prometheus instrumentation, alerting on consolidation failure and immutability violations, and OpenTelemetry tracing across the backend. Required before the team stops being able to monitor production manually.

### The CTO's Red Line

The CRO asked whether a very controlled, single-customer pilot could start before Phase 1 is complete — given that a PE-backed CFO in a controlled environment is not the same risk profile as a public SaaS deployment. The CTO's answer is no. A system with no authentication that can be accessed by any HTTP client that reaches the port is not a "controlled" environment — it is an uncontrolled environment that has not been exploited yet. The legal and reputational exposure of a data incident involving statutory financial data, at this stage of the company's life, is not a risk the CTO will accept. Phase 1 is a six-week job. It will not be shortcut.

---

## 6. Product Strategy — Nordic First

_CPO leads this section._

### Compliance Scope — The IFRS 10-Only Decision (for Now)

The product launches with IFRS 10 as its only statutory compliance scope. This is an honest constraint, not a positioning weakness — PE-backed Nordic groups that elect IFRS are a real, fundable segment, and their statutory obligation is IFRS 10. The platform will clearly state, on the product website and in onboarding, that unlisted Swedish groups with a K3 statutory obligation must confirm with their auditor before using the platform for statutory accounts.

The K3 module (`co-k3-mode`) is a formal product commitment for month 12–15. It requires:
1. A scoping study (`co-k3-compliance-research`) to document all K3 differences from IFRS 10 — this must be commissioned with a K3-qualified Swedish accountant, not derived from secondary sources alone.
2. Engine changes: full goodwill method (NCI at fair value at acquisition), systematic goodwill amortisation, deferred tax on eliminated intercompany profits per K3 rules.
3. BAS (Baskontoplan) chart of accounts mapping as a default template.
4. K3 note disclosure templates aligned with BAS presentation conventions.
5. At least one real statutory consolidation tested before any marketing claim of K3 compliance.

The K3 investment decision — whether to build in-house or commission a K3-specialist accounting technology consultant — is a founder decision (see Section 9). It is non-trivial but it is the unlock for the majority of the Swedish Persona A addressable market.

The NRS (Norwegian GAAP) module is scoped for research (`co-nrs-research`) within 18 months but not built. Norway is the second-largest Nordic market and NRS goodwill amortisation differs meaningfully from IFRS 10. The research scoping study will define the build effort and go/no-go criteria for a future NRS module.

### Feature Sequence for Beachhead

The product must clear the following milestones in order before Persona C deals can close.

**Before any customer engagement:** Authentication and multi-tenancy (Phase 1 technical), EU data residency documentation, public methodology document (`co-methodology-doc`), period locking and audit package export (`co-audit-package-export`).

**For first customer (Persona C, IFRS 10, PE-backed):**
- Explicit goodwill posting (`co-goodwill-explicit`) — legal risk item; any PE deal involves acquisition goodwill
- IAS 21 multi-currency (`co-ias21-translation`) — PE-backed Swedish parent with Finnish or Norwegian add-on is the standard pattern
- Submission status dashboard (`co-submission-dashboard`) — CFO needs to know which entities have and have not submitted before running consolidation
- Drill-down from consolidated figure to source entry (`co-drill-down`) — auditors and PE operating partners will ask for this on day one
- Balanced trial balance confirmation on the report screen (`co-trial-balance-zero-ui`)

**For Persona A (Swedish unlisted, month 12+ unlock):**
- SIE4 import (`co-sie-import`) — table-stakes for Swedish market entry; without this, Swedish accountants conclude the tool does not understand Swedish accounting
- Fortnox API connector (`co-fortnox-connector`) — the single highest-leverage GTM action for Sweden; the Otisco connector (Fortnox to AARO/Pacera) confirms this demand signal is real
- K3 compliance mode (`co-k3-mode`) — statutory unlock for the majority of Swedish unlisted groups
- BAS chart of accounts default mapping (`co-bas-chart-of-accounts`)

**Deferred but scoped:**
- Approval and sign-off workflow (`co-approval-workflow`) — required before Persona B (listed companies) but not a blocker for Persona C
- Period comparison / prior-year view (`co-period-comparison`) — auditor asks for this in analytical procedures; not a deal-stopper for early deals
- Intercompany profit in inventory (`co-unrealised-profit`) — material for manufacturing/trading groups; not the first Persona C profile

### The Dual-Validator as a Product Differentiator

The CPO's strongest conviction from the session: the dual-validator (independent `IfrsCalculator` and `PandasValidator` cross-checking every consolidation run) is a genuine product differentiation that no competitor at this tier can match. It must be surfaced explicitly in the methodology document, in the product UI, and in the sales narrative. "Every consolidation run is cross-checked by an independent second implementation" is a specific, verifiable claim — not a marketing abstraction. Nordic auditors will respond to this. It should be in the methodology document as a named architectural commitment, not buried in the codebase.

### SIE4 and the Swedish Market Signal

The CPO's most important insight from the competitive analysis: the Otisco connector (a third-party product specifically linking Fortnox to AARO/Pacera) is a confirmed demand signal for exactly the gap North Star is targeting. Fortnox customers want group consolidation. The connector exists because Fortnox does not provide it natively. North Star's Fortnox integration is not a feature — it is a distribution channel. Building and publishing to the Fortnox partner marketplace is a GTM decision as much as a product decision, and it should be resourced accordingly.

---

## 7. GTM Strategy

_CRO leads this section._

### Channel Sequence

**Months 1–12: Direct to PE operating partner network.**
The Stockholm PE ecosystem is small and reachable. EQT, Altor, Triton, Nordic Capital, Verdane, Summa, and a handful of other firms collectively have 10–15 operating partners who influence finance infrastructure decisions across their portfolio companies. Each operating partner manages multiple portfolio companies. A single operating partner relationship is a multi-deal pipeline. This is a relationship sales motion, not a digital acquisition motion. It requires a founder or senior hire who can walk into Stureplan and be taken seriously in a PE conversation.

The first three deals will come from this channel. The CRO's playbook for the first three deals is below.

**Months 6–12: Mid-tier accounting firm partnerships (BDO Sweden, Grant Thornton Sweden, Azets Scandinavia).**
These firms serve the exact Persona A profile that K3 will unlock. The accounting firm partnership has two functions: (1) it generates referral pipeline, and (2) it provides auditor acceptance — a firm that has recommended North Star and seen a client's audit pass is a reference for future deals. The CRO will begin this relationship-building in month 6, not at launch, so that the first firm partnership is signed before the K3 module goes live.

**Why mid-tier before Big 4:** Mid-tier firms (BDO, Grant Thornton, Azets) have more clients in the 2–8 entity Persona A range. Big 4 Nordic practices (PwC Sweden, KPMG Sweden, Deloitte Sweden, EY Sweden) will require reference customers and methodology documentation before recommending to clients. The sequence is: build reference clients via mid-tier, approach Big 4 with evidence.

**Risk — accounting firm conflict of interest:** Nordic accounting firms perform year-end consolidation as a managed service today and have a financial interest in the status quo. The CRO will position North Star as enabling the firm to deliver more advisory value per hour, not replacing the consolidation engagement. The white-label tier (firm is the customer, group companies are end users) is the structural resolution of this conflict — the firm retains the client relationship and margin; the tool eliminates the manual work.

**Month 12+: Fortnox ecosystem (inbound/product-led).**
Once SIE4, Fortnox connector, and K3 are live, publish to the Fortnox partner marketplace. This is an inbound channel — it does not require a direct sales motion. Conversion from Fortnox marketplace listing to trial requires the product to be self-serve. Conversion from trial to paid requires the pricing and onboarding flow to work without a sales call.

**PE direct channel stays open throughout.** Persona C (PE-backed) remains a direct sales motion even as the other channels develop. The operating partner network is not saturated in 12 months.

### First Three Deals Playbook

The CRO's model for closing the first three paying customers, all from Persona C:

**Target profile:** PE-backed Swedish group, 3–8 entities, IFRS-elected, at least one acquisition in the last 24 months (i.e., goodwill exists), 1–3 non-Swedish subsidiaries (i.e., multi-currency applies). This profile exactly matches the technical capabilities that Phase 2 will deliver.

**Entry point:** Operating partner or CFO introduction via founder network. Not inbound. Not marketing. These deals require a person who can credibly represent statutory consolidation expertise in a PE finance conversation.

**Demo:** Live system demo using a realistic PE-backed group scenario — ParentCo with two add-ons, one foreign, acquisition goodwill on one, NCI on one partial acquisition. Run the consolidation in the session. Show the audit package. Show the methodology document. Do not describe the system as AI under any framing.

**Proof of concept:** Offer a 60-day proof-of-concept period at no charge, with one period's real data loaded. The CFO gets to run their actual consolidation and compare to their current Excel model. This is the sales cycle for the first three deals. It is long (8–12 weeks total including PoC) but the conversion rate on PoC-to-paid should be high if the product works.

**What "closed" means:** Signed SaaS subscription agreement with a 12-month minimum term, DPA executed, EU data residency confirmed in writing. No annual commitment without a DPA. No deal where the CFO's auditor has not at minimum seen the methodology document and not raised an objection.

**Pricing:** Per-entity-per-month pricing, invoiced annually in SEK. Base tier: SEK 2,500/entity/month (6 entities = SEK 15,000/month = SEK 180,000/year). This puts a 6-entity group at SEK 15,000/month — in the range where it is a meaningful saving vs. the external accountant consolidation engagement (SEK 80,000–250,000/year) and well below AARO/Pacera (SEK 150,000–600,000/year). Annual invoicing improves cash flow and signals commitment.

**The CRO's constraint on the CTO:** The CRO will not start selling before Phase 1 (security and multi-tenancy) is complete. The CRO's pipeline activity in weeks 1–6 is relationship-building and methodology document preparation only. No live demos of the unprotected system to external parties. No "we'll have it ready soon" PoC commitments. The CRO accepted this constraint.

### Pricing Model Summary

| Tier | Target | Pricing | Notes |
|---|---|---|---|
| Persona C early-access | PE-backed, 4–8 entities | SEK 2,500/entity/month, annual | First three deals; may include PoC period |
| Persona A standard | Swedish unlisted, 2–6 entities | SEK 2,000/entity/month, annual | Post-K3 launch; Fortnox channel |
| Persona B enterprise | Listed, 8–20 entities | Custom, minimum SEK 250,000/year | Not in 18-month scope |

---

## 8. The Critical Path

The four voices converge here. This is the dependency map. If any item is late, the items downstream are late.

```
Week 1–2:   Authentication + Alembic + missing DB constraints
                └── [CTO gate: no customer engagement before here]

Week 3–6:   Multi-tenancy (tenant_id on all tables, query filtering, schema plan)
            EU data residency deployment + DPA template
            Methodology document drafting
                └── [CTO + CPO gate: no customer PoC before here]

Week 4–6:   Structured logging, health endpoint fix, backup procedure
                └── [CTO gate: minimum production readiness]

Week 6–8:   Goodwill explicit posting (legal risk item — blocks any PE deal)
            IAS 21 multi-currency (blocks any cross-border group)
            Submission dashboard + trial balance zero UI
                └── [CPO gate: product must pass here before first Persona C demo]

Week 6–8:   CRO: PE operating partner outreach begins (relationship only, no demos)
            CRO: Methodology document review with a Swedish accountant
                └── [CRO gate: methodology doc approved before any demo]

Week 8–10:  Replace Streamlit with production frontend (React/Vue)
            Audit package export (multi-sheet Excel)
            Drill-down from consolidated figure to source entry
                └── [CPO gate: product must pass here before first PoC]

Week 10–12: First Persona C PoC begins
            CRO: Mid-tier accounting firm outreach begins (BDO Sweden, Grant Thornton Sweden)
                └── [CRO: first deal target — close by month 5–6]

Month 5–6:  First paying Persona C customer
            K3 compliance research commissioned (K3-qualified Swedish accountant)
                └── [CPO gate: K3 scope decision crystallised — see Section 9]

Month 6–9:  Engine as shared library (remove HTTP micro-service overhead)
            PostgreSQL RLS as defence-in-depth
            Load testing at 50k entry scale

Month 9–12: K3 mode engine development (full goodwill method, amortisation, BAS mapping)
            SIE4 import
            Fortnox API connector
            BAS chart of accounts default mapping
                └── [CPO gate: K3 + SIE4 + Fortnox all required before Persona A GTM]

Month 10–12: First audit completed using North Star as the consolidation record
            Accounting firm partner agreement signed (BDO or GT Sweden)
                └── [CEO/CRO gate: audit acceptance is the 18-month strategy proof point]

Month 12–15: Fortnox partner marketplace listing live
             Persona A GTM via accounting firm channel and Fortnox inbound
             K3 module in production (tested, accountant-reviewed)
```

### The Key Dependencies

**If security (Phase 1) is not done, the CRO cannot demo.** The CRO's week 1–6 activity is relationship and methodology work only. This is not a delay — it is the right sequencing. Demoing an unauthenticated system to a PE CFO and having them ask "so who else can see my data?" is a deal-killer that cannot be recovered.

**If the K3 scope decision is not made, the CPO cannot set the Persona A launch date.** K3 is a major product investment. Without a founder decision on whether to build it in-house or commission it externally, the month 12 Persona A unlock has no fixed date. This is listed as an open question in Section 9.

**If the methodology document is not published and auditor-reviewed, the CRO cannot close.** Nordic CFOs will show the methodology document to their auditor before signing. A CFO who cannot get their auditor's provisional acceptance of the platform's approach will not proceed. The methodology document is not a marketing deliverable — it is a sales prerequisite.

**If goodwill posting and IAS 21 are not in production, no PE deal can proceed to statutory use.** Every PE-backed group has acquisition goodwill. Most have at least one non-domestic entity. These are not nice-to-have features for Persona C — they are table-stakes for a statutory product in this segment.

**If audit acceptance (three completed audits) does not happen, the 18-month strategy fails.** Revenue without audit acceptance is a fragile commercial position. Nordic CFOs will not renew a consolidation tool if their auditor objects to the output. The audit acceptance milestone — three completed audits accepted by Big 4 or mid-tier firms — is the validation that the product works for its stated purpose.

---

## 9. Open Questions Requiring Founder Decision

These are not questions the leadership team can resolve in a strategy session. They require a founder or board decision, typically because they involve capital allocation, strategic risk, or external commitments.

### 9.1 K3 Investment Decision

**Question:** Does North Star build the K3 compliance module in-house, or commission it with a specialist K3 accounting technology consultant?

**Context:** K3 mode requires full goodwill method, systematic goodwill amortisation, BAS chart of accounts mapping, and K3 note disclosure templates. It is non-trivial. The CPO estimates 4–6 weeks of engine work once the specification is complete, plus the specification work itself (which requires a K3-qualified Swedish accountant). The alternative is to outsource the specification and possibly the engine implementation to a firm with Swedish GAAP expertise.

**Why it is a founder decision:** The make-vs-commission decision has implications for the technical team's capacity (a 4–6 week engine project competes directly with infrastructure work in Phase 2), the quality risk (building K3 mode without qualified K3 accountant review is a compliance risk), and the cost (commissioning K3 specification work is a meaningful expense at this stage).

**What the leadership team agrees:** K3 mode must be in production by month 12–15. The K3 compliance research (`co-k3-compliance-research`) must be commissioned with a K3-qualified accountant regardless of the build/commission decision. The founder must decide the build approach before month 5.

### 9.2 Hire Sequence — First Three Hires

**Question:** In what sequence does North Star make its first three external hires, and what is the funding assumption that makes that sequence possible?

**Context:** The current team can execute Phase 1 (security and tenancy hardening) and the core product work through the first PoC. But the operating model for 30 customers at SEK 4.5m ARR requires more capacity than the founding team. The three roles most discussed in the session were: (a) a Sweden-based sales person who can execute the PE operating partner channel and the accounting firm outreach — not a generic SaaS AE, but someone with credibility in Nordic PE finance; (b) a frontend engineer to build the production React/Vue frontend; and (c) a Nordic accounting domain specialist to own the K3 compliance work and the methodology document and to be the face to Nordic audit firms.

**Why it is a founder decision:** The hire sequence depends on the funding plan. If raising a seed round, the sequence may be: accounting domain specialist first (enables K3 and auditor relationships), then sales, then frontend. If bootstrapping, the sequence is different and slower.

**What the leadership team agrees:** The accounting domain specialist hire is the one the team is most aligned on as the first priority. A person with K3 consolidation expertise and Nordic audit firm relationships is a prerequisite for both the K3 module quality and the accounting firm channel credibility. This hire is harder to replace with contractors than the frontend work is.

### 9.3 Fundraising Timing and Amount

**Question:** Is North Star raising external capital for the 18-month plan, and if so, when and how much?

**Context:** The 18-month plan (30 customers, SEK 4.5m ARR, three audit acceptances, one firm partnership) is achievable with a small team if the product and GTM execution is tight. But the K3 module investment, the frontend rebuild, the Nordic sales hire, and the accounting domain specialist hire collectively require more than bootstrapped capital is likely to provide.

**Why it is a founder decision:** Capital structure, dilution, and the timing of an institutional raise are founder decisions. The leadership team has noted that the first three Persona C deals — if closed at SEK 180,000/year each — represent SEK 540,000/year ARR. This is the seed traction that a Nordic deep-tech or fintech seed fund would want to see before writing a meaningful cheque. The founder must decide whether to raise pre-traction (to accelerate Phase 2) or post-traction (to raise on better terms). Both paths are viable; they are not equivalent.

**What the leadership team agrees:** The 18-month plan should be modelled in two scenarios — bootstrapped and seed-funded — with explicit assumptions about hire timing and the K3 decision in each. The founder should make the fundraising decision before month 3, not after the first deal closes.

### 9.4 Accounting Firm Partner Exclusivity

**Question:** Should North Star offer any form of exclusivity to the first Nordic accounting firm partner?

**Context:** A firm like BDO Sweden or Azets Scandinavia will be more motivated to build a referral programme if they have some exclusive benefit — access to beta features, co-marketing rights, or a period of exclusivity in their client segment. However, exclusivity limits the speed at which North Star can build the channel.

**Why it is a founder decision:** Exclusivity agreements in early-stage SaaS partnerships are commercial decisions with legal implications. The CPO and CRO disagree on this point: the CPO prefers non-exclusive partnerships to maintain optionality; the CRO is willing to offer limited exclusivity to close the first firm partnership faster. The founder must decide the acceptable parameters before the first firm negotiation begins.

---

## Appendix — Working Agreements from the Session

**On the IFRS 10 / K3 messaging:** Until the K3 module is in production and tested, all external communications will describe the platform as "IFRS 10 consolidation software." Any reference to K3 will be framed as "in development" or "coming in 2027." No customer will be allowed to use the platform for K3 statutory accounts until the module is production-ready and accountant-reviewed. The CPO owns this messaging gate.

**On competitor references:** Sales materials will name Pacera/AARO by name as the Nordic incumbent. The positioning is "self-serve consolidation below Pacera's floor" for internal use, but external materials should not name competitors directly until we have audit-accepted reference customers. The CRO owns this decision.

**On the Streamlit question:** Streamlit will be maintained for investor demos only. It will not be given to any paying customer. The CTO will resource the React/Vue frontend rebuild in Phase 2, beginning planning in Phase 1. If any external party (investor, potential customer) is shown the system before the production frontend is live, they will be explicitly told it is a demo interface, not the production product.

**On audit acceptance as a hard milestone:** All four executives agreed that "three completed statutory audits accepted by Big 4 or mid-tier audit firms using North Star as the consolidation record" is a non-negotiable milestone, not a stretch goal. If this milestone is at risk, it takes priority over ARR targets. A product that has not passed a statutory audit is not what North Star claims to be.

---

_End of strategy document. Version 1.0. Review at month 6._
