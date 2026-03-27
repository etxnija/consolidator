# North Star Consolidator — Product Research

_Date: 2026-03-27_

---

## 1. Customer Segments

### Persona A — Mid-Market CFO

**Profile:** Owner-operated or founder-led business with 2–8 legal entities. Revenue typically £10m–£150m. Finance team of 2–5 people including the CFO. Common in professional services, manufacturing, retail roll-ups, and tech.

**Typical entity count:** 3–8

**Current consolidation tool:** Excel is the dominant approach — a manually maintained workbook stitching together exported trial balances from Xero, QuickBooks, or Sage. The CFO or a part-time controller owns the file. No systematic intercompany elimination; goodwill is tracked in a side sheet.

**Biggest pain point:** Month-end close extends 15–30 days because the Excel consolidation must be rebuilt or manually updated after every subsidiary's books are closed. Intercompany mismatches surface late. When the external auditor arrives, there is no audit trail for eliminations — the CFO must reconstruct the logic from the spreadsheet, wasting days. IFRS 10 compliance is assumed rather than enforced.

**Willingness-to-pay signal:** This persona will pay to eliminate consultant-accountant fees at year-end (typically £5k–£20k per engagement for Excel cleanup and audit support). SaaS tools priced at £500–£1,500/month for the full group are in range if the savings and audit confidence are clear. Per-entity pricing is attractive because the entity count is predictable. The purchase decision is made by the CFO alone or with the board.

---

### Persona B — Listed-Company Group Controller

**Profile:** Mid-cap listed company on a secondary exchange (AIM, Euronext Growth, ASX, TSX-V). 6–20 legal entities, often across 2–4 jurisdictions. Dedicated group finance team of 3–8 people. Subject to external audit by a mid-tier firm (BDO, Grant Thornton, RSM) or, for larger listings, a Big 4 firm.

**Typical entity count:** 8–20

**Current consolidation tool:** A legacy EPM tool (Prophix, Tagetik at the lower tier, or a heavily customised Excel-based consolidation pack) or a managed consolidation service from an outsourced finance provider. Some use NetSuite's built-in multi-entity consolidation module when the group standardised on NetSuite.

**Biggest pain point:** Three compounding problems. First, the consolidation system does not produce statutory-quality audit evidence — the group controller must manually prepare an "audit pack" from the system's output. Second, multi-currency (IAS 21 translation and OCI posting for the CTA) is either absent or requires manual journal overrides. Third, changes requested by the auditor after the first draft require a full restatement cycle that the system makes time-consuming and error-prone.

**Willingness-to-pay signal:** Budgets exist and are benchmarked against the cost of the current system plus the consultant/auditor time cost. Tools like Lucanet charge £2,000–£6,000/month at this tier. A statutory-ready tool that cuts audit preparation time by 50% justifies £1,500–£3,000/month. Procurement involves CFO plus IT sign-off; 3–6 month sales cycle.

---

### Persona C — PE-Backed Portfolio CFO

**Profile:** CFO installed by a private equity sponsor into a platform company or recently acquired add-on. The sponsor typically requires monthly management accounts and a quarterly consolidated pack. Group structure is dynamic — add-on acquisitions happen quarterly or annually. Entities may span multiple countries. Finance infrastructure is often immature at acquisition.

**Typical entity count:** 3–15, growing through the hold period

**Current consolidation tool:** The PE operating team may mandate a specific tool (NetSuite for ERP, with manual Excel consolidation for statutory; or a lightweight tool like Joiin or Syft for management accounts). Statutory consolidation often lands back in Excel or with an outsourced accounting firm. SAP Business One appears in larger buyouts.

**Biggest pain point:** The consolidation model must accommodate new entities quickly after acquisitions. Goodwill from each acquisition must be tracked separately (purchase price allocation, IFRS 3 fair value step-up, annual IAS 36 impairment test). Intercompany complexity rises rapidly as the group grows. The sponsor wants to see NCI correctly stated for minority positions in add-ons. The biggest operational risk is not having a defensible audit trail for Year 1 statutory accounts after each acquisition — auditors scrutinise NCI, goodwill, and intercompany eliminations intensely.

**Willingness-to-pay signal:** The PE sponsor is cost-conscious but the CFO has a clear mandate to close faster and cleaner. Tools that save a week of month-end work per month justify £1,000–£2,500/month. The sponsor's operating partner may influence the procurement decision. A tool that integrates with the mandated ERP (NetSuite or SAP) has a significant advantage — removing the CSV-upload friction point is often the decisive factor.

---

## 2. Competitive Landscape

### CCH Tagetik (Wolters Kluwer)

**Strengths:** Statutory and management consolidation in one platform. Deep IFRS and multi-GAAP support. Strong audit trail. Trusted by finance teams at listed companies. Regulatory reporting (ESEF/XBRL) built in. PwC and Deloitte use it in outsourced consolidation engagements.

**Weaknesses:** Implementation is a project, not a product. System integrators (element61, Hayne, Bluebird) are required. Minimum viable implementation is 3–6 months for a simple group; 9–18 months for complex structures. Pricing is enterprise — modular, negotiated, typically £50k–£200k/year all-in including implementation. Requires dedicated admin.

**Pricing tier:** £50k–£200k/year. Custom.

**Implementation time:** 3–18 months depending on scope.

**Failure mode for 2–20 entities:** Massively over-engineered. A 5-entity group will spend 80% of the implementation budget on configuration it will never use. The ongoing cost is disproportionate to the problem size. The system rewards the sophistication of a Big 4 implementation partner, not the CFO's own team.

---

### OneStream

**Strengths:** Unified EPM platform — consolidation, planning, reporting, and analytics in one data model. Recognised as a Gartner Magic Quadrant Leader (2025). Eliminations, currency, and NCI are all first-class. AI-assisted features (dynamic report creation, anomaly detection) are being added. Strong for groups over £300m revenue.

**Weaknesses:** Average annual contract value is approximately $178,000; complex implementations can exceed $1m. Requires certified implementation partners. Ideal customer profile is $300m–$10bn revenue. Not designed for a 5-entity group. Training investment is significant.

**Pricing tier:** $150k–$1m+/year. Custom only.

**Implementation time:** 6–18 months.

**Failure mode for 2–20 entities:** Price and complexity create an impenetrable barrier. A mid-market CFO who receives a OneStream quote typically reverts to Excel. The product experience assumes a dedicated EPM team, which does not exist at target segment scale.

---

### Lucanet

**Strengths:** The closest existing competitor to North Star's target segment. Purpose-built financial consolidation with IFRS, US GAAP, and local GAAP support. Sweet spot is £50m–£500m revenue, 5–50 entities. 300+ ERP integrations. Implementation is faster than Tagetik or OneStream — 8–16 weeks for simple groups. Excel-friendly output. Embedded Power BI. Well regarded in DACH and increasingly UK/Benelux markets.

**Weaknesses:** Per-user pricing starts around $1,200/year per user, scaling to ~$50k/year for 100 users. Implementation still requires a Lucanet partner and project management overhead. Multi-currency support exists but requires configuration. Not self-serve — onboarding involves consultants.

**Pricing tier:** £10k–£80k/year for a 5–20 entity group, depending on user count and modules.

**Implementation time:** 8–24 weeks.

**Failure mode for 2–20 entities:** Still requires an implementation project and consultant. A 3-entity startup group cannot afford or justify a Lucanet engagement. The UI is functional rather than modern. Lucanet's lower bound is still above where North Star starts.

---

### Excel + Accountant

**Strengths:** Zero upfront cost. Infinitely flexible. The CFO and auditor both understand it. Every subsidiary can export to CSV or Excel. Widely used — this is the current state for the majority of the target segment.

**Weaknesses:** No enforced elimination logic; errors are silent. No audit trail beyond file version history. Month-end close is manual, slow, and error-prone. Intercompany mismatches are discovered late. Multi-currency requires manual rate lookups. NCI calculation is a formula in a cell, not a governed process. Scaling from 3 to 8 entities typically forces a painful rebuild of the model. Auditors accept it but add procedures (and cost) to compensate for the lack of controls.

**Pricing tier:** £0 tool cost, but £5k–£30k/year in accountant time for consolidation support and audit prep.

**Failure mode for 2–20 entities:** Does not fail abruptly — it degrades gradually. The pain compounds as the group grows. The switch moment typically comes after an audit finding, a restatement, or a new CFO arriving who has used a proper system before.

---

### Market Wedge for North Star

The gap is clearly defined: **below Lucanet's floor, above Excel's ceiling.** For groups of 2–10 entities, no tool currently delivers:

1. IFRS 10-correct, auditable eliminations with a timestamped immutable ledger
2. Self-serve onboarding in hours, not weeks
3. Pricing under £1,000/month with no implementation project required
4. A modern UI that a CFO can use without training

Lucanet is the nearest competitor but requires a partner-led project. Tagetik and OneStream are three price tiers above the segment. Excel has 100% market share by default, not by design. The wedge is **"statutory-ready, self-serve consolidation for the group that has outgrown Excel but cannot justify Lucanet."**

---

## 3. IFRS 10 Correctness and Audit Scope

### What an External Auditor Checks

A statutory audit of consolidated financial statements under IFRS 10 involves the following procedures, conducted by the group audit team (often coordinating with component auditors for significant subsidiaries):

**Scope and control assessment (IFRS 10.7):** The auditor verifies that every entity the parent claims to control actually meets the three-element control definition: power over the investee, exposure to variable returns, and ability to use power to affect returns. Entities omitted from consolidation are a significant audit risk. North Star currently uses `ownership_pct` as a proxy for control — this is pragmatic for the target segment (simple majority-owned subsidiaries) but is an assumption the auditor will scrutinise for any entity below 50% or with complex governance.

**Elimination completeness and accuracy (IFRS 10.B86):** The auditor traces every material intercompany balance and transaction through the elimination schedule. They reconcile intercompany receivables against payables across entity pairs, test that intercompany revenue is matched by intercompany cost of sales, confirm dividends paid to the parent have been eliminated from group income, and verify the investment-in-subsidiary account is eliminated against subsidiary equity. North Star's four-step engine covers all four of these. The immutable ledger and `is_elimination=True` flag provide the traceability the auditor needs.

**Non-controlling interests (IFRS 10.22):** Auditors verify that NCI is calculated on the full net assets of the subsidiary (not just share capital), that the split between controlling and non-controlling interest is arithmetically correct, and that NCI equity is presented separately within group equity. North Star's NCI split in Step 2 is correct in principle; the auditor will want to see it calculated on total `EQUITY_*` balances, which the current implementation does.

**Goodwill and IFRS 3 (IFRS 10.B86(d)):** This is the most complex area. Goodwill arises when the cost of the investment (`INVEST_SUB`) exceeds the fair value of the net assets acquired. The auditor will check: (a) that goodwill has been explicitly recognised and disclosed (not left as a residual imbalance), (b) that goodwill is allocated to cash-generating units (IAS 36), and (c) that an annual impairment test has been performed and documented. This is a significant gap in the current implementation — the residual is implicit in the trial balance and there is no `GOODWILL` account.

**Multi-currency / IAS 21:** For groups with foreign subsidiaries, the auditor checks that each subsidiary's functional currency is correctly identified, that balance sheet items are translated at the closing rate, that P&L items are translated at transaction rates (or an average where this approximates transaction rates), and that the resulting Cumulative Translation Adjustment (CTA) is posted to OCI and presented as a separate equity reserve. The CTA must also be split between controlling interest and NCI. The current implementation has no IAS 21 support — all amounts are assumed to be in a single currency. For any group with a foreign subsidiary, the consolidated statements will be technically non-compliant.

**Uniform accounting policies (IFRS 10.B87):** The auditor checks that all subsidiaries have applied consistent policies before consolidation, or that adjustments have been made. North Star has no mechanism to enforce or document this.

---

### Gap Analysis: Current Implementation vs. Big 4 Audit Pass

| Area | Current State | Audit Gap | Risk Level |
|---|---|---|---|
| Interco balance elimination | Implemented (Step 1) | Mismatch residuals surface in TB — need human review process documented | Low |
| Equity elimination with NCI | Implemented (Steps 2 + NCI split) | Passes for simple structures; NCI must be on total equity, not share capital only | Low |
| Dividend elimination | Implemented (Step 3) | Adequate | Low |
| Interco revenue/COGS elimination | Implemented (Step 4) | Unrealised profit in inventory not eliminated — gap for goods-trading groups | Medium |
| Goodwill explicit posting | Not implemented — residual is implicit | Auditor will require explicit `GOODWILL` account, CGU allocation disclosure, IAS 36 impairment test | High |
| Multi-currency (IAS 21) | Not implemented | Any group with a non-domestic subsidiary cannot produce IFRS-compliant consolidated statements | Critical |
| Control assessment (IFRS 10.7) | Ownership % proxy only | Adequate for simple majority-owned structures; fails for SPVs, joint arrangements, de facto control | Medium |
| Unrealised profit in inventory | Not implemented | Gap for manufacturing/trading groups | Medium |
| Uniform accounting policy adjustments | Not implemented | No tooling; CFO must manually adjust before upload | Low (process) |
| Immutable ledger and audit trail | Implemented (PG trigger + app layer) | Strong — exceeds what most tools provide at this tier | None |
| Period locking | Implemented | Strong | None |

---

### Legal Risk Areas

**Goodwill:** If a group uses the platform for statutory IFRS accounts and goodwill is not explicitly recognised and subject to an IAS 36 impairment test, the statutory accounts are materially misstated. This creates legal exposure for the directors and — if the platform is positioned as producing auditable output — potential liability for the vendor. The fix (explicit `GOODWILL` posting) is in the roadmap; it is a prerequisite before the platform can credibly claim statutory use.

**Multi-currency:** Any group with a foreign subsidiary that relies on the current platform for consolidated statements will produce accounts that violate IAS 21. This is not a minor disclosure gap — it affects the total values reported for assets, liabilities, and equity. Do not market the platform to multi-currency groups until IAS 21 is implemented.

**NCI on full fair value vs. proportionate:** IFRS 3 permits two methods for measuring NCI at acquisition: full fair value (which creates more goodwill) or proportionate share of identifiable net assets. The current implementation uses the proportionate approach (NCI = `equity × NCI%`). This is permitted but the platform does not surface the choice as a policy election — auditors will ask.

---

## 4. UX Requirements for Corporate Finance

### Why Streamlit Is Insufficient for Production Use

Streamlit is an appropriate prototyping and demo tool, but a CFO using a consolidation platform for statutory accounts needs capabilities that Streamlit's interaction model does not naturally support:

---

### Approval and Sign-Off Workflows

A statutory consolidation is not a single-user action. The typical workflow involves: (1) subsidiary controllers submitting their trial balances, (2) a group controller reviewing submissions and flagging queries, (3) the CFO approving the consolidated output, and (4) the auditor receiving a locked, signed-off package. Each step requires a clear record of who approved what and when.

Current gap: North Star has period locking but no user identity, no approval states, and no sign-off record. The CFO cannot demonstrate to the auditor that the correct person approved the final figures.

Required: Multi-user roles (subsidiary submitter, group controller, CFO approver), an approval workflow with email notifications, and an immutable sign-off log attached to the locked period.

---

### Drill-Down from Consolidated Figure to Source Entry

When an auditor or the CFO questions a line in the consolidated P&L or balance sheet, they need to be able to click on the figure and trace it through: consolidated account → entity breakdown → individual ledger entries → source CSV row. This is the standard expectation of any consolidation tool used in an audit context.

Current gap: The report endpoint (`GET /report/{period_id}`) returns aggregated sums with no drill path. The `ledger_entries` table supports this — every elimination entry carries `metadata.elimination_type` and every source entry carries the source file reference. The data is there; the UI path is not.

Required: Clickable consolidated figures that expand to entity-level detail, then to individual ledger entries, with the source file and row reference visible. Exportable to a workbook for the audit pack.

---

### Period Comparison and Movement Analysis

CFOs and group controllers routinely need to compare the current period against the prior period (or prior year) to explain movements. Auditors will ask for this as part of analytical procedures. A single-period view is inadequate for any real-world use.

Required: Side-by-side reporting for two periods (e.g., H1-2025 vs. H1-2024), with variances calculated and highlighted. Movement on key balance sheet lines (goodwill, NCI, intercompany balances eliminated) should be surfaced automatically.

---

### Export to Audit Package

The consolidated output must be exportable in a form the auditor can work with. The roadmap already includes Excel export. For a full audit package the requirement extends to:

- A multi-sheet Excel workbook: consolidated P&L, consolidated Balance Sheet, elimination schedule (each elimination with date, counterparty, amount, and type), entity-level trial balances before and after eliminations, NCI calculation, and a period-lock event log.
- PDF rendering of the same for filing and board packs.
- A machine-readable format (CSV or JSON) for the auditor's own reconciliation work.

---

### Additional Corporate Finance UX Requirements

**Intercompany mismatch alerting:** When INTERCO_REC on Entity A does not match INTERCO_PAY on Entity B, this should surface as a named alert (e.g., "Mismatch £12,500 between SubA and SubB — INTERCO loan") before consolidation is run, not as a silent residual in the trial balance.

**Entity submission status dashboard:** A traffic-light view showing which entities have submitted for the current period, which are pending, and which have zero entries. This currently exists as a "warnings" field but should be a prominent pre-consolidation checklist.

**Restatement workflow:** When an error is found after period lock, there needs to be a governed restatement path: open a restatement period, post reversing entries, re-run eliminations, produce a comparison of original vs. restated figures. The immutable ledger supports this architecturally; the workflow needs to be surfaced.

---

## 5. Trust and Transparency for AI-Generated Financials

### The CFO Trust Problem

Corporate finance operates as a system of accountability. Every number that appears in a statutory filing must be defensible — traceable to a source transaction, computed by a known and documented method, and approved by an identified person. CFOs are personally liable for statutory accounts in most jurisdictions. The moment a CFO is uncertain whether a number is correct, or cannot explain how it was produced, it becomes a liability rather than an asset.

The market in 2025–2026 shows strong CFO scepticism toward AI-generated financial outputs, despite widespread interest in AI productivity tools. The concern is not about automation per se — month-end journals and depreciation calculations have always been automated — but about explainability and auditability of the automation. When an AI model produces a financial estimate (reserves, impairment, revenue), the CFO must justify it through a clear, defensible audit trail. If the method is opaque, the CFO cannot sign off.

---

### How Comparable Fintech Products Handle This

The most trusted fintech finance tools share four common assurance mechanisms:

1. **Deterministic rules, not probabilistic models.** Revenue recognition tools (Recurly, Maxio) and lease accounting tools (LeaseQuery) emphasise that their calculations follow a defined rulebook — the same inputs always produce the same output, and the rulebook is auditable. They contrast this explicitly with "AI" approaches to differentiate on trust.

2. **Full source-to-output traceability.** Every computed figure links back to its input transactions. Auditors can, and do, test this linkage. Tools that cannot provide it are replaced before the first statutory audit.

3. **Human sign-off gates.** The tool computes; a qualified human approves. This division of labour is the assurance framework that regulators, auditors, and CFOs are comfortable with. No trusted fintech tool removes the sign-off step.

4. **Third-party validation.** Audit-ready tools are often promoted alongside a Big 4 or mid-tier firm endorsement ("EY uses this in its client engagements") or a published accounting methodology document that an auditor can reference.

---

### Positioning North Star's Rules-Based Engine

North Star's engine has a significant but under-exploited trust advantage: **it is a deterministic, rules-based calculator, not an ML model.** The dual-implementation cross-validator (imperative Python vs. Pandas vectorised implementation) is a genuine differentiator — no comparable tool at this tier can demonstrate that two independent implementations of the elimination logic produce the same results to four decimal places.

The positioning opportunity is to lean into this explicitly:

- **Do not call it "AI."** The engine is a codified accounting rulebook. Describe it as "rules-based elimination engine, independently validated" not "AI-powered consolidation."
- **Expose the invariant check as a user-visible assertion.** When the consolidated trial balance nets to zero, surface this as a visible confirmation ("Consolidation balanced: assets + liabilities + equity = £0.00") on the report screen. This is the mathematical proof that the elimination was correct.
- **Publish the elimination methodology as a public document.** The consolidation-logic.md document already exists internally. A version of this should be available to customers and their auditors as the reference specification for how the engine works. Deloitte's "Clearly IFRS" series does exactly this — it makes the methodology the trust asset.
- **The dual-validator should be marketed, not hidden.** "Every consolidation run is cross-checked by an independent second implementation" is a claim no competitor at this tier can make. It directly addresses the auditor's concern about systematic errors.
- **Audit trail as a first-class UI element.** The immutable ledger and `is_elimination=True` flag are architectural trust assets. They should be surfaced explicitly in the UI and audit export, not buried in a database column.

---

### What a CFO Would Require Before Relying on This for a Statutory Filing

Based on the trust framework above, a CFO would require:

1. A complete elimination schedule — every entry, with type, counterparty, and amount — exportable for the auditor. (Partially met — the data exists, the export needs building.)
2. Proof that the consolidated trial balance nets to zero. (Architecturally met; not yet surfaced in UI.)
3. A human sign-off record attached to the locked period. (Not yet implemented — approval workflow required.)
4. A methodology document they can give to their auditor. (Exists internally; needs to be customer-facing.)
5. Confidence that goodwill and multi-currency are handled — or, if not, a clear statement of scope limitations. (Currently not handled — this must be documented explicitly until the gaps are closed.)

---

## 6. Technical Gap Prioritisation

The following gaps are ranked by impact on the three customer segments, with reference to the competitive and compliance analysis above.

---

### Rank 1: Multi-Currency / IAS 21 — Critical

**Customer impact:** Blocks all three personas for any group with a non-domestic subsidiary. Even a UK parent with one Irish or US subsidiary cannot produce IFRS-compliant consolidated accounts without this. The PE-backed CFO and listed-company controller segments are almost entirely unusable without it. The mid-market CFO segment is partially addressable for single-currency groups, but this limits the addressable market severely.

**Competitive impact:** Lucanet, Tagetik, and NetSuite all include multi-currency. Absence puts North Star below even the "Excel + accountant" benchmark for international groups — an accountant would at least manually translate and adjust.

**What is required:** IAS 21 closing rate method for balance sheet items; average rate or transaction rate for P&L; OCI posting of CTA; CTA split between controlling interest and NCI; goodwill retranslation at closing rate. This is a significant engine change that also requires a `functional_currency` field on `entity_metadata` and exchange rate inputs per period.

**Suggested priority: P1** — implement before claiming IFRS compliance for any international group.

---

### Rank 2: Goodwill Explicit Posting — High

**Customer impact:** Any group that has acquired a subsidiary at above book value will have an implicit goodwill balance sitting as an unexplained residual in the consolidated trial balance. The roadmap already acknowledges this as a P2 item (`co-goodwill-posting`). For the purposes of statutory accounts, this is a legal risk — directors are signing accounts with a material item misclassified. The PE-backed CFO persona is particularly exposed because every acquisition creates new goodwill.

**Competitive impact:** Lucanet and Tagetik handle goodwill explicitly. This is an expected feature of any consolidation tool used in an audit context.

**What is required:** When `invest_amount ≠ parent_share_of_equity`, post the residual to a `GOODWILL` account. Classify `GOODWILL` as a non-current asset in the balance sheet. Provide a per-subsidiary goodwill schedule (acquisition date, cost, net assets at acquisition, goodwill recognised, carrying amount). The IAS 36 impairment test itself is out of scope for the engine — but the platform should capture impairment journal entries when the CFO uploads them.

**Suggested priority: P1** — elevate from roadmap P2. This is a legal risk item, not a polish item.

---

### Rank 3: ERP Integrations (SAP / NetSuite / Oracle) — High for PE and Listed Segments

**Customer impact:** The current CSV upload model is acceptable for the investor demo and early adopters, but it is a friction point for ongoing production use. For the PE-backed portfolio CFO whose entities run on NetSuite, a direct API pull would eliminate the manual export step and the GCoA mapping problem (NetSuite has a standardised chart of accounts). For listed companies on SAP, an SAP Financial Consolidation connector is expected.

**Competitive impact:** Lucanet has 300+ ERP integrations as a selling point. This is a moat that North Star will need to chip away at incrementally. A NetSuite connector targets the PE segment directly (NetSuite is the dominant ERP in PE-backed portfolio companies). A QuickBooks/Xero connector targets the mid-market CFO segment.

**Sequencing:** NetSuite API → Xero API → QuickBooks API → SAP BAPI. This is the order that maps to the three personas by segment size and acquisition likelihood.

**Suggested priority: P2** — defer until multi-currency and goodwill are closed. ERP integration without correct eliminations is a demo feature, not a product.

---

### Rank 4: Performance and Load Testing — Medium

**Customer impact:** A 20-entity group submitting quarterly trial balances generates a ledger of roughly 20,000–100,000 entries per period. The current stack (FastAPI + PostgreSQL, single-instance) should handle this comfortably at small scale, but there are no benchmarks. The engine's stateless design and the append-only ledger are good architectural choices for scale, but the consolidation step (load all non-elimination entries for a period, pass to engine, insert eliminations) has not been tested above the demo data scale (~200 entries).

**Risk:** A production customer with a 15-entity group and 3 years of history could trigger a slow consolidation run that times out the HTTP request. This is a support and trust problem, not a functional one.

**Suggested priority: P3** — add load tests with synthetic 10k/50k/200k entry datasets before launch. Define SLA targets (consolidation run < 5 seconds for up to 50k entries).

---

### Rank 5: Playwright UI Tests — Medium-Low

**Customer impact:** Indirect. UI regressions in a CFO-facing product erode trust quickly. A broken "Lock Period" button or a report that renders incorrect totals after a backend change will create immediate escalation.

**Competitive context:** Not a differentiator — customers do not know or care about the test suite. But UI test coverage is the baseline engineering hygiene that prevents the trust failures described in Section 5.

**Suggested priority: P3** — implement a smoke test suite (create entity, ingest CSV, run consolidation, view report, export Excel) after the UI reaches feature parity per the roadmap P0 items. Do not invest before the UI is stable.

---

## Backlog Recommendations

The following items are grouped into three tracks with suggested priorities. These are not filed beads — they are recommendations for the next planning session.

---

### Track: `product`

| Priority | Bead Name | Description |
|---|---|---|
| P1 | `co-ias21-translation` | Implement IAS 21 multi-currency: closing rate BS, average rate P&L, CTA to OCI, CTA split for NCI. Requires `functional_currency` on entity and exchange rate inputs per period. |
| P1 | `co-goodwill-explicit` | Elevate goodwill posting from P2 to P1: explicit `GOODWILL` account, per-subsidiary goodwill schedule, balance sheet classification. Legal risk item. |
| P2 | `co-interco-mismatch-alert` | Pre-consolidation warning UI: named alerts for each unmatched INTERCO pair with entity names and residual amount before the user clicks Consolidate. |
| P2 | `co-unrealised-profit` | Eliminate unrealised profit in intercompany inventory transfers — required for manufacturing and trading groups (IFRS 10.B86(c) full application). |
| P2 | `co-netsuite-connector` | NetSuite API connector: pull trial balance by period and entity directly, auto-map to GCoA using NetSuite standard account types. |
| P3 | `co-xero-connector` | Xero API connector for mid-market single-currency groups. |
| P3 | `co-period-comparison` | Side-by-side prior period comparison in the report view with variance column. |
| P3 | `co-load-tests` | Synthetic load tests: 10k/50k/200k entry datasets against consolidation endpoint; define and enforce <5s SLA. |

---

### Track: `trust/compliance`

| Priority | Bead Name | Description |
|---|---|---|
| P1 | `co-trial-balance-zero-ui` | Surface the "consolidated TB nets to zero" invariant as a visible confirmation on the report screen, including the exact net figure and a pass/fail indicator. |
| P1 | `co-methodology-doc` | Publish the elimination methodology as a customer-facing document (derived from consolidation-logic.md) that can be handed to an external auditor as the engine's reference specification. |
| P1 | `co-audit-package-export` | Full audit package export: multi-sheet Excel with consolidated P&L, consolidated BS, elimination schedule (typed, counterparty, amount), entity-level TBs pre/post elimination, NCI calculation, period-lock log. |
| P2 | `co-approval-workflow` | Multi-user roles (submitter, controller, CFO approver) with approval states per period, email notifications, and an immutable sign-off log attached to the locked period record. |
| P2 | `co-control-assessment-doc` | Add a `control_basis` field to entity_metadata (e.g., majority ownership, contractual, de facto) and surface it in the ownership tree so auditors can see the basis for inclusion of each entity in scope. |
| P2 | `co-restatement-workflow` | Governed restatement path: open a restatement sub-period, post reversing entries, re-run eliminations, produce a restated vs. original comparison report. |
| P3 | `co-ifrs18-readiness` | Assess impact of IFRS 18 (mandatory FY2027) on account classification categories (Operating / Investing / Financing) and flag any GCoA mapping changes required. |

---

### Track: `ux`

| Priority | Bead Name | Description |
|---|---|---|
| P1 | `co-drill-down` | Clickable drill-down from consolidated figure → entity breakdown → individual ledger entries → source file reference. Exportable at each level. |
| P1 | `co-submission-dashboard` | Pre-consolidation entity submission status dashboard: traffic-light view of which entities have submitted, which are pending, and any zero-entry warnings for the selected period. |
| P2 | `co-interco-reconciliation-view` | Intercompany matrix view: for each entity pair, show the INTERCO_REC, INTERCO_PAY, and any mismatch. Allows the group controller to chase subsidiaries before running consolidation. |
| P2 | `co-period-lock-guard` | Already in roadmap — disable Upload and Consolidate buttons on locked period, show clear banner. |
| P2 | `co-entity-tree-viz` | Already in roadmap — ownership tree visualisation with ownership percentages and NCI labels. |
| P3 | `co-pdf-report` | PDF rendering of the consolidated report for board pack and statutory filing use. |
| P3 | `co-playwright-smoke` | Playwright smoke test suite covering the end-to-end demo story: entity creation, CSV upload, consolidation run, report view, Excel export. |
