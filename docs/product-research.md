# North Star Consolidator — Product Research

> **Revised following CPO review — Nordic market focus.**

_Date: 2026-03-27_

---

## 1. Customer Segments

_Reframed for Nordic market. Revenue figures in SEK with EUR/GBP approximate equivalents. ERP references updated to Nordic reality. WTP benchmarked against Nordic accountant costs and Nordic competitor pricing._

### Persona A — Mid-Market Nordic CFO

**Profile:** Owner-operated or founder-led business with 2–8 legal entities. Revenue typically SEK 50m–1.5bn (roughly €5m–€140m / £4m–£120m). Finance team of 2–5 people including the CFO. Common in professional services, manufacturing, retail roll-ups, and tech. Domiciled primarily in Sweden (K3 filer), with Norwegian (NRS filer) as the second-largest cohort. Most entities will run on Fortnox (Sweden) or Tripletex/Visma (Norway).

**Typical entity count:** 3–8

**Applicable consolidation standard:** Unlisted Swedish parent companies use **K3** (BFNAR 2012:1) for statutory consolidated accounts. Unlisted Norwegian parent companies use **NRS** (Norwegian GAAP). IFRS 10 is relevant only if the group voluntarily elects IFRS — which is uncommon at this size.

**Current consolidation tool:** Excel is the dominant approach — a manually maintained workbook stitching together exported trial balances from Fortnox, Visma, or Björn Lundén (sometimes as SIE4 files, sometimes as CSV). The CFO or a part-time controller owns the file. No systematic intercompany elimination; goodwill is tracked in a side sheet. The external consolidation engagement with a Big 4 or mid-tier firm typically runs SEK 80,000–250,000 per year (roughly €7,500–€23,000 / £6,000–£18,000) for a 4-entity group.

**Biggest pain point:** Month-end close extends 15–30 days because the Excel consolidation must be rebuilt or manually updated after every subsidiary's books are closed. Intercompany mismatches surface late. When the external auditor arrives, there is no audit trail for eliminations — the CFO must reconstruct the logic from the spreadsheet, wasting days. K3/NRS compliance is assumed rather than enforced.

**Willingness-to-pay signal:** This persona will pay to eliminate the annual accountant consolidation engagement (SEK 80,000–250,000/year). A SaaS tool at SEK 6,000–15,000/month (roughly £500–£1,100/month) that eliminates most of that engagement is a credible save. Per-entity pricing is attractive because the entity count is predictable. The purchase decision is made by the CFO alone or with the board. Local currency pricing (SEK/NOK) matters for procurement — GBP or EUR pricing creates psychological friction.

---

### Persona B — Listed-Company Group Controller (Nasdaq Nordic)

**Profile:** Mid-cap listed company on Nasdaq Stockholm, Nasdaq Copenhagen, Oslo Børs, or Nasdaq Helsinki. 6–20 legal entities, often across 2–4 jurisdictions. Dedicated group finance team of 3–8 people. Subject to external audit by a Big 4 firm (PwC, Deloitte, KPMG, EY — all with strong Nordic practices) or a mid-tier firm (BDO, Grant Thornton, Azets).

**Typical entity count:** 8–20

**Applicable consolidation standard:** **IFRS 10** is mandatory for listed Nordic companies preparing consolidated accounts. Multi-currency (IAS 21) is almost always in scope: a Swedish-listed parent with Finnish or Norwegian subsidiaries is multi-currency by definition (SEK/EUR/NOK).

**Current consolidation tool:** AARO (now part of Pacera), IBM Cognos Controller, or a heavily customised Excel consolidation pack. Larger listings use a managed consolidation service from an outsourced finance provider. AARO holds approximately 30% of Nasdaq Stockholm Large Cap listed companies as customers, making it the dominant Nordic incumbent for this persona.

**Biggest pain point:** Three compounding problems. First, the consolidation system does not produce statutory-quality audit evidence — the group controller must manually prepare an "audit pack" from the system's output. Second, multi-currency (IAS 21 translation and OCI posting for the CTA) is either absent or requires manual journal overrides. Third, changes requested by the auditor after the first draft require a full restatement cycle that the system makes time-consuming and error-prone.

**Willingness-to-pay signal:** Benchmarked against Pacera/AARO pricing, which is in the SEK 150,000–600,000/year range for a mid-market group. A statutory-ready tool that cuts audit preparation time by 50% justifies SEK 15,000–30,000/month (£1,200–£2,500/month). Procurement involves CFO plus IT sign-off plus a Data Processing Agreement review (EU data residency); 3–6 month sales cycle.

---

### Persona C — PE-Backed Portfolio CFO (Nordic)

**Profile:** CFO installed by a Nordic private equity sponsor (e.g., EQT, Altor, Triton, Nordic Capital, Verdane) into a platform company or recently acquired add-on. Stockholm has the deepest PE ecosystem in the Nordics, feeding this persona directly. The sponsor typically requires monthly management accounts and a quarterly consolidated pack. Group structure is dynamic — add-on acquisitions happen quarterly or annually. Entities may span multiple Nordic countries. Finance infrastructure is often immature at acquisition.

**Typical entity count:** 3–15, growing through the hold period

**Applicable consolidation standard:** Many PE-backed Nordic groups elect IFRS for investor reporting even if not listed, to satisfy LP reporting requirements and facilitate future IPO. Some use K3 (if Swedish, unlisted). The sponsor operating partner will dictate the standard. This persona is the most likely to be genuinely IFRS 10 applicable.

**Current consolidation tool:** The PE operating team may mandate a specific tool (NetSuite for ERP at larger portfolio companies, or a lightweight tool for management accounts). Statutory consolidation often lands back in Excel or with an outsourced accounting firm. At acquisition, the CFO inherits whatever the previous owners used — which is frequently Fortnox (small Swedish add-ons) or Visma Business.

**Biggest pain point:** The consolidation model must accommodate new entities quickly after acquisitions. Goodwill from each acquisition must be tracked separately (purchase price allocation, IFRS 3 fair value step-up, annual IAS 36 impairment test or NRS amortisation schedule). Intercompany complexity rises rapidly as the group grows. The sponsor wants to see NCI correctly stated for minority positions. The biggest operational risk is not having a defensible audit trail for Year 1 statutory accounts after each acquisition.

**Willingness-to-pay signal:** The PE sponsor is cost-conscious but the CFO has a clear mandate to close faster and cleaner. Tools that save a week of month-end work per month justify SEK 10,000–25,000/month (£800–£2,000/month). The sponsor's operating partner may influence the procurement decision. A tool that integrates with Fortnox or Visma (the most common ERP in Swedish add-ons) removes the CSV-upload friction that is often the decisive barrier.

---

## 2. Competitive Landscape

_Updated for Nordic market reality. AARO/Pacera added. Cognos Controller Nordic presence added. Lucanet assessment corrected (no Nordic office). Tagetik and OneStream retained but reframed as out-of-segment for initial target._

### Pacera / AARO — The Nordic Incumbent

**Background:** AARO is a Swedish consolidation software company founded in 1989 in Stockholm, with approximately 30% of Nasdaq Stockholm Large Cap listed companies as customers. In January 2026, AARO merged with Aico (financial close automation) and Mercur (FP&A and budgeting) to form Pacera, backed by Accel-KKR. The combined entity supports 700+ organisations across Europe. Pacera positions itself as a unified platform for financial close, consolidation, and FP&A.

**Strengths:** Deep IFRS and K3 support. Established in the Swedish listed-company market. Known to Big 4 and mid-tier Swedish auditors. Fortnox and Visma integrations via the Otisco connector confirm the Nordic ERP integration demand. PE backing provides runway for product development and expansion. Nordic-native, Swedish-language support.

**Weaknesses:** Not self-serve. Implementation is a partner-led project. Pricing (SEK 150,000–600,000/year for mid-market) puts it out of reach for Persona A (2–6 entity groups). Target is listed companies and larger mid-market groups (SEK 500m+ revenue). Does not serve the sub-Pacera gap that is North Star's wedge.

**Pricing tier:** SEK 150,000–600,000/year. Custom, negotiated.

**Implementation time:** Consultant-led project; typically 8–20 weeks.

**North Star positioning against Pacera/AARO:** Below its floor, self-serve, no implementation project. Pacera is the reference point for "what a proper consolidation tool looks like" in the Swedish market — positioning North Star as "self-serve Pacera for groups of 2–6 entities" is a credible frame for a Swedish CFO audience.

---

### Visma Consolidation — Built-In but Limited

**Background:** Visma Software Nordic offers basic group consolidation within its ERP products (Visma Net, Business NXT, and related products). The Visma group has a very large Nordic customer base — Tripletex (Norwegian SME accounting, owned by Visma) has over 65,000 customers; e-conomic (Danish accounting) has approximately 250,000 customers across Denmark and the Nordics.

**Strengths:** For groups where all entities already run on Visma products, the built-in consolidation feature removes the integration step. Zero incremental cost. Familiar UI.

**Weaknesses:** Not statutory-quality IFRS or K3 consolidation. Handles basic elimination but does not produce audit-ready output. Limited goodwill support. NCI calculation is basic. No immutable audit trail. The CFO who needs to produce a statutory consolidated filing will still need an external accountant or a proper tool.

**Competitive threat level:** High at the bottom of Persona A (simple 3-entity groups all on Visma). Lower as entity count or complexity increases. For any group with mixed ERPs or more than 4–5 entities, Visma's built-in feature is insufficient.

---

### IBM Cognos Controller (IBM)

**Background:** IBM Cognos Controller (rebranded IBM Controller) is an enterprise financial consolidation platform. It has an entrenched installed base at larger Nordic listed companies — Sweden accounts for a disproportionate share of its European customer base (Länsförsäkringar AB is a named Nordic reference customer). It meets "virtually all global and local consolidation and reporting requirements" per IBM.

**Strengths:** Full IFRS and multi-GAAP support. Deep audit trail. Handles large, complex group structures. Well understood by Nordic Big 4 audit teams who have clients on it.

**Weaknesses:** Enterprise pricing. SAP/Oracle ERP dependency typical. Implementation requires specialist consultants. Not designed for 2–20 entity groups. UI is legacy. Not self-serve.

**Pricing tier:** Enterprise; similar range to Tagetik/OneStream. Custom.

**Relevance to North Star:** IBM Controller users are not our near-term target. However: (a) their CFOs have high expectations of consolidation tooling, and (b) when these companies spin off divisions or add-ons, the spun-off entity may become our Persona B or C target with strong prior-experience expectations.

---

### Lucanet — DACH-Centric, No Nordic Office

**Strengths:** The closest existing competitor to North Star's target segment outside the Nordics. Purpose-built financial consolidation with IFRS, US GAAP, and local GAAP support. Sweet spot is €50m–€500m revenue, 5–50 entities. 300+ ERP integrations. Implementation is faster than Tagetik or OneStream — 8–16 weeks for simple groups. Well regarded in DACH and increasingly UK/Benelux markets.

**Weaknesses:** **No office in Stockholm or any Nordic city.** Nordic customers are served through continental European operations (Netherlands, UK). This is a significant distribution weakness in a market where local presence, local language support, and understanding of K3/NRS genuinely matters to CFO buyers. Lucanet has no established relationships with Nordic mid-tier accounting firms. Still requires an implementation partner and project management overhead. Not self-serve.

**Pricing tier:** SEK 100,000–800,000/year (£10k–£80k/year) for a 5–20 entity group, depending on user count and modules.

**Implementation time:** 8–24 weeks.

**Window for North Star:** Lucanet's DACH success and growing UK presence will eventually draw Nordic attention. If North Star is not established in the Swedish market before Lucanet builds local presence, the window closes. The Nordic gap is real today; it will not remain open indefinitely.

---

### CCH Tagetik (Wolters Kluwer) — Out of Segment for Initial Target

**Strengths:** Statutory and management consolidation in one platform. Deep IFRS and multi-GAAP support. Strong audit trail. Regulatory reporting (ESEF/XBRL) built in. Used by larger Nordic listed companies.

**Weaknesses:** Implementation is a project, not a product. System integrators required. Minimum viable implementation 3–6 months. Pricing is enterprise — typically £50k–£200k/year all-in. Not for 2–20 entity groups.

**Pricing tier:** £50k–£200k/year. Custom.

**Failure mode for target segment:** Massively over-engineered. Out of segment for Persona A and most of Persona C. Relevant only for the upper end of Persona B. Not a near-term competitive threat in North Star's wedge.

---

### OneStream — Out of Segment for Initial Target

**Strengths:** Unified EPM platform — consolidation, planning, reporting, and analytics. Gartner Magic Quadrant Leader. Strong for groups over £300m revenue.

**Weaknesses:** Average annual contract value approximately $178,000; complex implementations can exceed $1m. Ideal customer profile is $300m–$10bn revenue. Not designed for a 5-entity group.

**Pricing tier:** $150k–$1m+/year. Custom only.

**Failure mode for target segment:** Price and complexity create an impenetrable barrier. Out of segment. Not a near-term competitive threat.

---

### Excel + External Accountant — The True Incumbent

**Strengths:** Zero upfront cost. Infinitely flexible. Every subsidiary can export to CSV, Excel, or SIE4 (in Sweden). Widely used — this is the current state for the majority of the target segment.

**Weaknesses:** No enforced elimination logic; errors are silent. No audit trail. Month-end close is manual and slow. Multi-currency requires manual rate lookups. Scaling from 3 to 8 entities typically forces a painful rebuild of the model.

**Nordic-specific competitive reality:** The "external accountant" for a mid-sized Swedish group consolidation is typically a Big 4 Nordic practice (PwC Sweden, Deloitte Sweden, KPMG Sweden, EY Sweden) or a mid-tier firm (BDO Sweden, Grant Thornton Sweden, Azets Scandinavia). These firms perform the year-end consolidation as a managed service and have a financial interest in the status quo.

Winning against Excel means either: (a) co-selling through those firms — they recommend or white-label the tool, slower to close but stickier and referral-driven; or (b) winning the CFO directly and displacing the firm's consolidation engagement — faster but creates firm antagonism. GTM strategy must address this tension explicitly (see Section 7).

**Pricing tier:** SEK 0 tool cost, but SEK 80,000–250,000/year in accountant time for a 4-entity group.

---

### Market Wedge for North Star

The gap is clearly defined: **below Pacera/AARO's floor, above Excel's ceiling, in the Swedish and Nordic market.** For groups of 2–8 entities, no tool currently delivers:

1. K3-correct (or IFRS 10-correct) auditable eliminations with a timestamped immutable ledger
2. SIE4 file import for Swedish accountants
3. Self-serve onboarding in hours, not weeks
4. Pricing under SEK 15,000/month (£1,000/month) with no implementation project
5. A modern UI that a Nordic CFO can use without training

Pacera/AARO is the Nordic incumbent but requires a partner-led project and targets larger groups. Lucanet has no Nordic office or local GAAP support. Tagetik and OneStream are three price tiers above the segment. Visma's built-in feature covers only simple all-Visma groups. The wedge is **"statutory-ready, self-serve consolidation for the Nordic group that has outgrown Excel but cannot justify Pacera."**

---

## 3. IFRS 10 Correctness, K3 (Sweden), and NRS (Norway) — Audit Scope

_This section has been expanded to address the CPO's feedback: IFRS 10 is not the universal applicable standard for the target segment. K3 (Sweden) and NRS (Norway) are the primary local GAAP standards for unlisted Nordic groups._

### Which Standard Applies to Which Company?

| Company type | Sweden | Norway | Denmark | Finland |
|---|---|---|---|---|
| Listed (Nasdaq Nordic, Oslo Børs) | IFRS 10 (mandatory) | IFRS 10 (mandatory) | IFRS 10 (mandatory) | IFRS 10 (mandatory) |
| Unlisted, larger mid-market | K3 (BFNAR 2012:1) | NRS (Norwegian GAAP) | Danish ÅRL (Class C) | Finnish Accounting Act |
| Unlisted, smaller groups | K3 or K2 (no consolid. req.) | NRS or simplified IFRS | Danish ÅRL | Finnish Accounting Act |
| PE-backed, IFRS elected | IFRS 10 (voluntary election) | IFRS 10 (voluntary election) | IFRS 10 (voluntary) | IFRS 10 (voluntary) |

**Important:** North Star currently implements IFRS 10 logic. For a significant portion of Persona A (unlisted Swedish and Norwegian groups), the platform's output may not satisfy their statutory obligation. **Before using North Star for statutory consolidated accounts, unlisted Swedish and Norwegian CFOs must confirm with their auditor whether their obligation is IFRS 10, K3, or NRS.**

---

### K3 — Swedish GAAP for Unlisted Groups (BFNAR 2012:1)

K3 is the Swedish Accounting Standards Board's (BFN) comprehensive accounting standard for larger unlisted companies. It is based on IFRS for SMEs but with significant modifications. Virtually all unlisted Swedish parent companies above the K2 threshold must use K3 for their statutory consolidated accounts.

**Key differences from IFRS 10 relevant to consolidation:**

**Goodwill method — K3 mandates full goodwill method.** Under K3, goodwill must be recognised on the full fair value of the subsidiary at acquisition, not just the parent's proportionate share. This means:
- The proportionate NCI method (NCI = equity × NCI%) that North Star currently uses produces the wrong goodwill figure under K3.
- Under K3, NCI at acquisition must be measured at fair value (full goodwill method), which generates a higher goodwill balance than the proportionate approach.
- This is a material compliance gap: a Swedish K3 filer using North Star in its current form will understate goodwill and misstate NCI at acquisition.

**Goodwill amortisation — K3 requires systematic amortisation, not impairment-only.** Under IFRS (IAS 36), goodwill is not amortised — it is subject to annual impairment testing. Under K3, goodwill must be amortised over its useful life (typically 5–10 years; maximum 10 years under K3 rules). A Swedish unlisted group on K3 will therefore post a goodwill amortisation charge each year. North Star's current engine has no mechanism for systematic goodwill amortisation.

**Intercompany profit elimination — deferred tax treatment differs.** K3 requires that deferred tax be recognised on intercompany profit eliminated in inventory, following the purchasing entity's tax rate. The IFRS 10 treatment of this deferred tax is slightly different. For most simple groups this is a disclosure difference rather than a measurement difference, but the notes will differ.

**BAS chart of accounts.** K3 consolidation note disclosures follow BAS (Baskontoplan) conventions — the standard Swedish chart of accounts. North Star's GCoA mapping must accommodate BAS account codes for Swedish users.

**Platform position until K3 module is built:** The platform should not be marketed to Swedish unlisted groups as K3-compliant. It can be used for management consolidation and IFRS-elected groups. A K3 compliance module (`co-k3-mode`) is in the backlog as P2.

---

### NRS — Norwegian GAAP for Unlisted Groups

Unlisted Norwegian companies use NRS (Norsk RegnskapsStandard). Listed Norwegian companies use IFRS. Key consolidation differences:

**Goodwill amortisation under NRS.** Norwegian GAAP still requires goodwill amortisation over useful life (unlike IFRS 10/IAS 36). The amortisation period must be justified; in practice many Norwegian groups use 5–20 years. This means a Norwegian unlisted group needs periodic goodwill amortisation entries in the consolidation — the platform must support this journal type, even before a full NRS module is built.

**Simplified IFRS option.** Norwegian unlisted companies may elect simplified IFRS (a Norwegian variant), which is closer to full IFRS but with some practical expedients. This option reduces the compliance gap for groups that prefer IFRS-style reporting.

**Platform position until NRS module is built:** Same as K3 — do not market as NRS-compliant for statutory accounts. Norwegian unlisted groups should use the platform for management consolidation or confirm IFRS election with their auditor. An NRS compliance module (`co-nrs-mode`) should be scoped after K3 work.

---

### What an External Auditor Checks (IFRS 10)

A statutory audit of consolidated financial statements under IFRS 10 involves the following procedures:

**Scope and control assessment (IFRS 10.7):** The auditor verifies that every entity the parent claims to control actually meets the three-element control definition: power over the investee, exposure to variable returns, and ability to use power to affect returns. North Star currently uses `ownership_pct` as a proxy for control — pragmatic for simple majority-owned subsidiaries but scrutinised for entities below 50% or with complex governance.

**Elimination completeness and accuracy (IFRS 10.B86):** The auditor traces every material intercompany balance and transaction through the elimination schedule. North Star's four-step engine covers the main categories. The immutable ledger and `is_elimination=True` flag provide the traceability the auditor needs.

**Non-controlling interests (IFRS 10.22):** Auditors verify NCI is calculated on the full net assets of the subsidiary (not just share capital) and that NCI equity is presented separately. North Star's NCI split is correct in principle for IFRS; it is incorrect for K3's full goodwill method.

**Goodwill and IFRS 3 (IFRS 10.B86(d)):** The auditor checks explicit goodwill recognition, CGU allocation, and annual impairment test documentation. The goodwill residual being implicit in the current implementation is a significant audit gap — explicit `GOODWILL` posting is a P1 item.

**Multi-currency / IAS 21:** For groups with foreign subsidiaries, the auditor checks closing rate translation for balance sheet, average rate for P&L, and CTA posting to OCI. Multi-currency support is absent in the current platform — any group with a non-domestic subsidiary cannot produce IFRS-compliant accounts. P1 item.

**Uniform accounting policies (IFRS 10.B87):** The auditor checks consistent policies across subsidiaries before consolidation. No mechanism in North Star today.

---

### Gap Analysis: Current Implementation vs. Audit Pass

| Area | Current State | Audit Gap | Risk Level |
|---|---|---|---|
| Interco balance elimination | Implemented (Step 1) | Mismatch residuals surface in TB — need human review process documented | Low |
| Equity elimination with NCI (IFRS) | Implemented (Steps 2 + NCI split) | Passes for IFRS simple structures; NCI on total equity, not share capital only | Low |
| Dividend elimination | Implemented (Step 3) | Adequate | Low |
| Interco revenue/COGS elimination | Implemented (Step 4) | Unrealised profit in inventory not eliminated — gap for goods-trading groups | Medium |
| Goodwill explicit posting | Not implemented — residual implicit | Auditor requires explicit GOODWILL account, CGU allocation, IAS 36 impairment test | High |
| Multi-currency (IAS 21) | Not implemented | Any group with non-domestic subsidiary cannot produce IFRS-compliant statements | Critical |
| K3 full goodwill method | Not implemented | Swedish K3 filers: wrong goodwill and NCI at acquisition | Critical for K3 |
| K3 goodwill amortisation | Not implemented | Swedish K3 filers: missing annual amortisation charge | Critical for K3 |
| NRS goodwill amortisation | Not implemented | Norwegian NRS filers: missing annual amortisation charge | Critical for NRS |
| Control assessment (IFRS 10.7) | Ownership % proxy only | Adequate for simple majority-owned structures; fails for SPVs, joint arrangements | Medium |
| Unrealised profit in inventory | Not implemented | Gap for manufacturing/trading groups | Medium |
| Uniform accounting policy adjustments | Not implemented | No tooling; CFO must manually adjust before upload | Low (process) |
| Immutable ledger and audit trail | Implemented (PG trigger + app layer) | Strong — exceeds what most tools provide at this tier | None |
| Period locking | Implemented | Strong | None |

---

### Platform Scope Statement (What the Platform Can and Cannot Be Used for Today)

**Can be used today:**
- Management consolidation for any group (for internal reporting, not statutory filing)
- Statutory consolidated accounts under IFRS 10 for single-currency groups where goodwill does not arise (or where goodwill is tracked externally)
- Statutory accounts for IFRS-elected groups with all-domestic subsidiaries (no IAS 21 required)
- Audit pack preparation support — elimination schedules, intercompany reconciliation, entity-level trial balances

**Cannot be used today for statutory statutory filing:**
- Any group with a foreign currency subsidiary (IAS 21 not implemented — Critical gap)
- Any group where goodwill arises at acquisition (goodwill posting not explicit — High gap)
- Unlisted Swedish groups with K3 statutory obligation (K3 goodwill method and amortisation not implemented)
- Unlisted Norwegian groups with NRS statutory obligation (NRS goodwill amortisation not implemented)
- Any group with unrealised profit in intercompany inventory transfers (manufacturing/trading)

---

## 4. UX Requirements for Corporate Finance

_Existing content retained. SIE4 file format import added as P1 requirement._

### Why Streamlit Is Insufficient for Production Use

Streamlit is an appropriate prototyping and demo tool, but a CFO using a consolidation platform for statutory accounts needs capabilities that Streamlit's interaction model does not naturally support.

---

### SIE4 File Format Import (P1 — Nordic Launch Prerequisite)

SIE (Standard Import Export) is the Swedish accounting data interchange format, standardised by BAS (the Swedish accounting standards body). SIE4 is the transaction-level export format that includes all ledger entries for a period. Every major Swedish accounting system — Fortnox, Visma, Björn Lundén, Hogia, PE Accounting — supports SIE4 export.

**Why this is P1 for the Nordic launch:** A Swedish accountant working on a consolidation for a 4-entity group will export SIE4 files from Fortnox, one per entity. If North Star requires CSV instead, the accountant must either (a) manually convert SIE4 to CSV — which is additional work and a source of errors — or (b) conclude that North Star does not understand Swedish accounting. The latter is the more common reaction. Not supporting SIE4 is the Nordic equivalent of not supporting CSV — it is a table-stakes compatibility requirement.

**What is required:** Parse SIE4 format files (`.si` extension). Extract period, account code (BAS account number), and debit/credit amounts. Map BAS account numbers to North Star GCoA. Handle the SIE4 header metadata (company name, organisation number, financial year). Provide a BAS-to-GCoA pre-built mapping as a default.

---

### Approval and Sign-Off Workflows

A statutory consolidation is not a single-user action. The typical workflow involves: (1) subsidiary controllers submitting their trial balances, (2) a group controller reviewing submissions and flagging queries, (3) the CFO approving the consolidated output, and (4) the auditor receiving a locked, signed-off package. Each step requires a clear record of who approved what and when.

Current gap: North Star has period locking but no user identity, no approval states, and no sign-off record. The CFO cannot demonstrate to the auditor that the correct person approved the final figures.

Required: Multi-user roles (subsidiary submitter, group controller, CFO approver), an approval workflow with email notifications, and an immutable sign-off log attached to the locked period.

---

### Drill-Down from Consolidated Figure to Source Entry

When an auditor or the CFO questions a line in the consolidated P&L or balance sheet, they need to be able to click on the figure and trace it through: consolidated account → entity breakdown → individual ledger entries → source file reference (CSV row or SIE4 transaction). This is the standard expectation of any consolidation tool used in an audit context.

Current gap: The report endpoint returns aggregated sums with no drill path. The `ledger_entries` table supports this — every elimination entry carries `metadata.elimination_type` and every source entry carries the source file reference. The data is there; the UI path is not.

Required: Clickable consolidated figures that expand to entity-level detail, then to individual ledger entries, with the source file and row reference visible. Exportable to a workbook for the audit pack.

---

### Period Comparison and Movement Analysis

CFOs and group controllers routinely need to compare the current period against the prior period (or prior year) to explain movements. Auditors will ask for this as part of analytical procedures.

Required: Side-by-side reporting for two periods (e.g., H1-2025 vs. H1-2024), with variances calculated and highlighted. Movement on key balance sheet lines (goodwill, NCI, intercompany balances eliminated) should be surfaced automatically.

---

### Export to Audit Package

The consolidated output must be exportable in a form the auditor can work with. For a Nordic Big 4 or mid-tier firm audit team (FAR-accredited Swedish auditors), the expected package is:

- A multi-sheet Excel workbook: consolidated P&L, consolidated Balance Sheet, elimination schedule (each elimination with date, counterparty, amount, and type), entity-level trial balances before and after eliminations, NCI calculation, and a period-lock event log.
- PDF rendering of the same for filing and board packs.
- A machine-readable format (CSV or JSON) for the auditor's own reconciliation work.

---

### Additional Corporate Finance UX Requirements

**Intercompany mismatch alerting:** When INTERCO_REC on Entity A does not match INTERCO_PAY on Entity B, this should surface as a named alert before consolidation is run, not as a silent residual in the trial balance.

**Entity submission status dashboard:** A traffic-light view showing which entities have submitted for the current period, which are pending, and which have zero entries.

**Restatement workflow:** When an error is found after period lock, there needs to be a governed restatement path: open a restatement period, post reversing entries, re-run eliminations, produce a comparison of original vs. restated figures.

---

## 5. Trust and Transparency for AI-Generated Financials

_Existing content retained. EU data residency added as a procurement gate. Big 4 Nordic practices named._

### The CFO Trust Problem

Corporate finance operates as a system of accountability. Every number that appears in a statutory filing must be defensible — traceable to a source transaction, computed by a known and documented method, and approved by an identified person. CFOs are personally liable for statutory accounts in most jurisdictions. The moment a CFO is uncertain whether a number is correct, or cannot explain how it was produced, it becomes a liability rather than an asset.

The market in 2025–2026 shows strong CFO scepticism toward AI-generated financial outputs, despite widespread interest in AI productivity tools. The concern is not about automation per se — but about explainability and auditability of the automation.

---

### EU Data Residency — A Nordic Procurement Gate

**This is not optional for enterprise Nordic sales.** Nordic CFOs, particularly in Sweden and Finland (EU members), have strong preferences for EU-hosted data. Norway (not EU) has its own sovereignty concerns. Denmark's public sector has noticeably retreated from US-cloud arrangements in recent years.

A Nordic CFO evaluating a new SaaS finance tool will ask: where is data hosted? Is it in the EU? Which data centre? Who has access? For statutory consolidated accounts — which contain entity-level P&L and balance sheet data that may be commercially sensitive — this is a procurement gate, not a checkbox.

**Practical requirements:**
- North Star must be hosted in an EU data centre. Preferred options: AWS eu-north-1 (Stockholm), Azure Sweden Central, or GCP europe-north1 (Finland). Stockholm hosting is a positive signal for Swedish enterprise buyers.
- A standard Data Processing Agreement (DPA) template must be available before any Persona B or Persona C sale.
- The hosting location must be stated clearly on the product website and in contract documentation. A marketing claim of "EU data residency" must be architecturally true and contractually documented, not aspirational.
- If the platform is on US infrastructure today, a meaningful proportion of Nordic enterprise buyers will not proceed without a DPA and legal review — adding 2–3 months to the sales cycle.

**GDPR enforcement context:** Sweden, Finland, and Denmark all have active GDPR supervisory authorities with enforcement records. Finance data is sensitive. Any "EU data residency" promise must be backed by architecture, not just policy.

---

### Auditor Attitudes in the Nordics

The Nordic Big 4 practices all have significant Nordic operations:

- **PwC Sweden** — largest auditor in Sweden by listed company count; strong K3 and IFRS expertise
- **KPMG Sweden** — co-dominant with PwC in Stockholm listed company audit
- **Deloitte Sweden** — strong in technology-sector clients and PE-backed groups
- **EY Sweden** — significant mid-market and listed practice
- **PwC Norway** — largest auditor in Norway by market share
- **BDO Sweden / BDO Norway** — leading mid-tier; most relevant for Persona A and B
- **Grant Thornton Sweden** — strong mid-market presence; key target for partner channel
- **Azets Scandinavia** — accounting and advisory firm with Sweden, Norway, Denmark practices; particularly relevant for Persona A

Nordic auditors are conservative and technically rigorous. Swedish auditors (Auktoriserad revisor / Godkänd revisor, accredited by FAR) will scrutinise consolidation methodology. Key implications:

- A public methodology document is not optional for the Nordic market — it is what a Swedish Big 4 team will request before accepting a client using the platform.
- The "dual-validator" differentiator (two independent implementations cross-checked) is genuinely compelling to a Nordic technical auditor. Include it in the methodology document explicitly.
- Nordic auditors are conservative about new software. A tool without a track record will face resistance. The path to acceptance: (a) methodology document, (b) reference customers who have completed audits using the platform, (c) ideally a formal dialogue with one Nordic Big 4 or mid-tier audit practice before go-to-market.

---

### How Comparable Fintech Products Handle Trust

The most trusted fintech finance tools share four common assurance mechanisms:

1. **Deterministic rules, not probabilistic models.** Revenue recognition and lease accounting tools emphasise that their calculations follow a defined rulebook — the same inputs always produce the same output. They contrast this explicitly with "AI" approaches to differentiate on trust.
2. **Full source-to-output traceability.** Every computed figure links back to its input transactions.
3. **Human sign-off gates.** The tool computes; a qualified human approves.
4. **Third-party validation.** Audit-ready tools are promoted alongside a Big 4 or mid-tier firm endorsement or a published accounting methodology document.

---

### Positioning North Star's Rules-Based Engine

North Star's engine has a significant but under-exploited trust advantage: **it is a deterministic, rules-based calculator, not an ML model.**

- **Do not call it "AI."** Describe it as "rules-based elimination engine, independently validated."
- **Expose the invariant check as a user-visible assertion.** Surface "Consolidation balanced: assets + liabilities + equity = £0.00" (or SEK equivalent) on the report screen.
- **Publish the elimination methodology as a public document** that customers and their auditors can reference.
- **Market the dual-validator.** "Every consolidation run is cross-checked by an independent second implementation" is a claim no competitor at this tier can make.
- **Audit trail as a first-class UI element.** The immutable ledger and `is_elimination=True` flag should be surfaced explicitly, not buried in a database column.

---

### What a CFO Would Require Before Relying on This for a Statutory Filing

1. A complete elimination schedule — every entry, with type, counterparty, and amount — exportable for the auditor.
2. Proof that the consolidated trial balance nets to zero.
3. A human sign-off record attached to the locked period.
4. A methodology document they can give to their auditor.
5. Confidence that goodwill and multi-currency are handled — or a clear statement of scope limitations.
6. EU data residency confirmation and a signed DPA.
7. Confirmation that the applicable local GAAP standard (K3 for unlisted Swedish groups, NRS for unlisted Norwegian groups) is either supported or explicitly out of scope.

---

## 6. Technical Gap Prioritisation

_ERP integration roadmap updated for Nordic market: Fortnox, e-conomic, Visma replace Xero/QuickBooks/NetSuite as the primary priorities. SIE4 import added as P1. NetSuite retained for Phase 2 (PE segment)._

---

### Rank 1: Multi-Currency / IAS 21 — Critical

**Customer impact:** Blocks all three personas for any group with a non-domestic subsidiary. A Swedish parent with a Norwegian (SEK/NOK) or Finnish (SEK/EUR) subsidiary cannot produce IFRS-compliant consolidated accounts without this. The PE-backed CFO and listed-company controller segments are almost entirely unusable without it.

**Competitive impact:** Pacera/AARO, Lucanet, Tagetik, and IBM Controller all include multi-currency. Absence puts North Star below even the "Excel + accountant" benchmark for international groups.

**What is required:** IAS 21 closing rate method for balance sheet items; average rate or transaction rate for P&L; OCI posting of CTA; CTA split between controlling interest and NCI; goodwill retranslation at closing rate. Requires a `functional_currency` field on `entity_metadata` and exchange rate inputs per period (SEK/NOK/EUR/DKK are the priority currency pairs for the Nordic market).

**Suggested priority: P1** — implement before claiming IFRS compliance for any international group.

---

### Rank 2: Goodwill Explicit Posting — High (Legal Risk)

**Customer impact:** Any group that has acquired a subsidiary at above book value will have an implicit goodwill balance. For the PE-backed CFO persona, every acquisition creates new goodwill. Statutory accounts with implicit goodwill are materially misstated. Note: under K3, this gap is compounded by the full goodwill method requirement.

**Competitive impact:** Pacera/AARO, Lucanet, and IBM Controller handle goodwill explicitly.

**What is required:** When `invest_amount ≠ parent_share_of_equity`, post the residual to a `GOODWILL` account. Classify `GOODWILL` as a non-current asset. Provide a per-subsidiary goodwill schedule (acquisition date, cost, net assets at acquisition, goodwill recognised, carrying amount). The IAS 36 impairment test itself is out of scope for the engine — but the platform should capture impairment journal entries when the CFO uploads them.

**Suggested priority: P1** — legal risk item. Elevate from roadmap P2.

---

### Rank 3: SIE4 Import — P1 for Nordic Launch

**Customer impact:** For Swedish Persona A customers running on Fortnox, Visma, or Björn Lundén, SIE4 is the native export format. Requiring CSV is an unnecessary friction point that signals unfamiliarity with Swedish accounting practice. Any Fortnox-ecosystem customer will expect SIE4 support.

**What is required:** Parse SIE4 format files. Extract account codes (BAS), period, and amounts. Map BAS codes to GCoA using a pre-built mapping. This is parseable in a few hundred lines of Python; the BAS chart of accounts is publicly available.

**Suggested priority: P1** — table-stakes for Swedish market entry.

---

### Rank 4: ERP Integrations — Fortnox First, Then Visma/e-conomic

**Nordic ERP priority sequence (replaces original Xero/QuickBooks/NetSuite sequencing):**

1. **Fortnox API (P1/P2 for Swedish launch):** Fortnox has 500,000+ Swedish customers and no native group consolidation. A direct API connector that pulls trial balance by period and entity is the highest-leverage integration for Persona A in Sweden. Fortnox operates an open API (OAuth 2.0). A published integration in the Fortnox partner marketplace would drive inbound without requiring a direct sales team.

2. **e-conomic API (P2 — Denmark):** e-conomic (owned by Visma) has approximately 250,000 customers in Denmark and broader Nordics. It is the Fortnox equivalent for Danish SMEs. An e-conomic integration is the key unlock for Persona A in Denmark.

3. **Visma Net / Business NXT API (P2 — Norway/Sweden mid-market):** Visma has the broadest Nordic ERP footprint — Norway (Tripletex, Visma Business), Sweden (Visma Net), Denmark (e-conomic). Visma provides developer APIs across its product range. A Visma integration covers the Norwegian Persona A mid-market cohort.

4. **Dynamics 365 Business Central (P3):** Growing fast in Nordic mid-market. Worth building after the core Nordic stack is covered.

5. **NetSuite (P3 — Phase 2, PE segment):** NetSuite is present in PE-backed Nordic portfolio companies (Persona C) and worth building, but it is not the Swedish SME entry point. Defer until the Phase 1 Nordic launch integrations are complete.

6. **SAP Business One / S/4HANA (P3):** Present at the upper mid-market in Sweden and Finland. Build after core Nordic stack.

**Deprecated for Nordic launch:**
- Xero: negligible Nordic market share. Relevant for any future UK-facing expansion. Do not build for the Nordic launch.
- QuickBooks: essentially absent from the Nordics. Remove from the integration roadmap for this market.

---

### Rank 5: Performance and Load Testing — Medium

**Customer impact:** A 20-entity group submitting quarterly trial balances generates a ledger of roughly 20,000–100,000 entries per period. The consolidation step has not been tested above demo data scale.

**Suggested priority: P3** — add load tests with synthetic 10k/50k/200k entry datasets before launch. Define SLA targets (consolidation run < 5 seconds for up to 50k entries).

---

### Rank 6: Playwright UI Tests — Medium-Low

**Suggested priority: P3** — implement a smoke test suite after the UI reaches feature parity per P0 roadmap items.

---

## 7. Go-to-Market (Nordic)

_New section, addressing the CPO's feedback that the original document said nothing about GTM._

### Channel Overview

Consolidation tools in the Nordic market are sold through three main channels. For North Star's target segment, these are in roughly descending order of importance for initial traction:

---

### Channel 1 — Accounting and Advisory Firms (Recommended Priority: High)

**Mechanics:** The most common evaluation trigger for a new consolidation tool is an audit observation, a new CFO hire, or an M&A event (acquisition adds entity count). When this happens, the CFO typically calls their external accountant or advisor first. That advisor recommends or runs a tool selection.

**Key targets — mid-tier Nordic firms first:**
- BDO Sweden and BDO Norway — strong mid-market practice, most clients in the 2–8 entity range
- Grant Thornton Sweden — mid-market presence, significant for Persona A
- Azets Scandinavia — accounting and advisory across Sweden, Norway, Denmark; directly relevant for Persona A
- PwC, Deloitte, KPMG, EY — approach after reference clients exist; Big 4 Nordic practices will want references and methodology documentation before recommending to clients

**Why mid-tier first, Big 4 second:** Mid-tier firms have more clients in the 2–8 entity range (Persona A). Big 4 will be more cautious about recommending an unproven tool. The sequence is: build reference clients via mid-tier, then approach Big 4 with evidence.

**Programme structure:**
- Refer-and-recommend tier: accounting firm recommends North Star to clients; receives a referral fee per conversion
- White-label tier: accounting firm embeds North Star in a managed consolidation service; firm is the customer, not the end group
- Certified adviser tier: firm staff trained on the platform; listed as a "certified North Star partner" with inbound leads shared

**Risk:** These firms perform year-end consolidations as a managed service today. A tool that eliminates manual consolidation work reduces their billable hours. Win against Excel without displacing the firm's advisory relationship — position North Star as enabling the firm to do more advisory work per hour, not replacing the engagement.

---

### Channel 2 — ERP Partner Channel (Fortnox Ecosystem, Recommended Priority: High for Sweden)

**Mechanics:** Fortnox operates a partner marketplace with 500+ integrations. A published integration with a dedicated listing in the Fortnox marketplace is the single highest-leverage GTM action for the Swedish Persona A market. Fortnox has 500,000+ customers. Even a modest conversion rate on relevant multi-entity groups produces significant pipeline.

**Actions required:**
1. Build Fortnox API connector (see technical roadmap, Rank 4)
2. Publish to Fortnox partner marketplace
3. Register as a Fortnox integration partner
4. Build equivalent Visma partner relationship for Norway/Denmark

**Fortnox partner ecosystem specifics:** The Otisco connector (which links Fortnox to AARO/Pacera) confirms that demand for Fortnox-to-consolidation-tool connectivity exists and that Fortnox customers are willing to pay for it. North Star can compete directly in this connector position, targeting the sub-AARO/sub-Pacera segment.

---

### Channel 3 — Direct / Inbound for PE-Backed Segment

**Mechanics:** Nordic PE CFOs (Persona C) are digitally literate and will search. A Swedish-language landing page with a Fortnox/Visma integration, a clear K3/IFRS framing, and a free trial would generate inbound. The product must be self-serve to convert this channel.

**PE operating partner network:** Stockholm's PE ecosystem (EQT, Altor, Triton, Nordic Capital, Verdane, Summa) uses a relatively small community of operating partners who influence finance tool decisions across portfolio companies. Reaching 10–15 key operating partners in Stockholm is a high-leverage action for Persona C. This is a direct/relationship channel, not a digital channel.

---

### Typical Sales Cycle and Deal Mechanics

| Persona | Typical cycle | Decision maker | Key friction points |
|---|---|---|---|
| A — Mid-Market Nordic CFO | 4–12 weeks | CFO alone or + board | Auditor acceptance, ERP integration, local GAAP question |
| B — Listed Group Controller | 3–6 months | CFO + IT + audit committee | DPA/data residency, references, auditor acceptance |
| C — PE-Backed Portfolio CFO | 6–12 weeks | CFO + PE operating partner | ERP integration, IFRS vs. K3, multi-entity onboarding speed |

**Persona A deal mechanics:** Self-serve trial → product-led conversion → email onboarding. Price: SEK 6,000–15,000/month. No IT sign-off. The main friction is whether the auditor will accept the platform — which is resolved by the public methodology document and a reference customer who has completed an audit.

**Persona B deal mechanics:** Demo → proof-of-concept period → security/DPA review → contract. Price: SEK 15,000–30,000/month. Legal review of DPA required (add 4–8 weeks). Reference customers are critical. Auditor dialogue (ideally pre-sales, arranged through the accounting firm channel) materially shortens the cycle.

**Persona C deal mechanics:** Introduction via PE operating partner or accounting firm → demo → proof-of-concept → conversion. Price: SEK 10,000–25,000/month. Speed of multi-entity onboarding is the key evaluation criterion — the CFO will test this explicitly.

---

### Pre-Launch GTM Prerequisites

Before any Nordic market launch, the following must be in place:
1. EU data residency confirmed and documented (see Section 5)
2. Public methodology document published (see Section 5)
3. SIE4 import working (see Section 6)
4. Fortnox API connector live or in beta
5. At least one reference customer who has completed a financial year-end using the platform
6. Swedish-language product marketing page

---

## 8. Backlog Recommendations

_All 22 original items revised in light of CPO feedback. New items added: SIE4 import, K3 compliance research, NRS compliance research, EU data residency, Pacera/AARO competitive monitoring, GTM partner programme. Xero and QuickBooks connectors deprioritised for Nordic launch. ERP sequencing updated._

---

### Track: `product`

| Priority | Bead Name | Description |
|---|---|---|
| P1 | `co-ias21-translation` | Implement IAS 21 multi-currency: closing rate BS, average rate P&L, CTA to OCI, CTA split for NCI. Requires `functional_currency` on entity and exchange rate inputs per period. Nordic priority currency pairs: SEK/NOK/EUR/DKK. |
| P1 | `co-goodwill-explicit` | Explicit GOODWILL account posting, per-subsidiary goodwill schedule, balance sheet classification. Legal risk item. Prerequisite for any statutory use claim. Note: K3 full goodwill method requires additional work beyond this item. |
| P1 | `co-sie-import` | SIE4 format file import. Parse `.si` files, extract BAS account codes and period amounts, map to GCoA using pre-built BAS mapping. Table-stakes for Swedish market entry. |
| P1 | `co-fortnox-connector` | Fortnox API connector: pull trial balance by period and entity directly via Fortnox open API (OAuth 2.0). Publish to Fortnox partner marketplace. Replaces `co-xero-connector` as the P1 ERP integration for Nordic launch. |
| P2 | `co-bas-chart-of-accounts` | Pre-built BAS (Baskontoplan)-to-GCoA mapping as a default template for Swedish onboarding. BAS account codes are publicly available. Eliminates the most common onboarding friction for Swedish Persona A customers. |
| P2 | `co-economic-connector` | e-conomic (Visma) API connector for Danish SME market. Approximately 250,000 customers in Denmark and broader Nordics. Phase 2 integration after Fortnox. |
| P2 | `co-visma-connector` | Visma Net / Business NXT API connector for Norwegian and Swedish mid-market. Covers Tripletex (Norway) and Visma Business equivalents. Phase 2 integration after Fortnox. |
| P2 | `co-k3-mode` | K3 compliance mode for unlisted Swedish groups: full goodwill method (NCI at fair value at acquisition), goodwill systematic amortisation, K3 note disclosure templates, BAS-aligned presentation. Non-trivial but materially expands Swedish addressable market. |
| P2 | `co-nrs-research` | Scoping study for NRS (Norwegian GAAP) compliance: document all consolidation differences from IFRS 10, estimate build effort for NRS module, define go/no-go criteria. Precedes `co-nrs-mode`. |
| P2 | `co-interco-mismatch-alert` | Pre-consolidation warning UI: named alerts for each unmatched INTERCO pair with entity names and residual amount before the user clicks Consolidate. |
| P2 | `co-unrealised-profit` | Eliminate unrealised profit in intercompany inventory transfers — required for manufacturing and trading groups. |
| P3 | `co-netsuite-connector` | NetSuite API connector for PE-backed portfolio companies (Persona C, Phase 2). Defer until Fortnox and Visma connectors are live. |
| P3 | `co-dynamics365-connector` | Microsoft Dynamics 365 Business Central connector. Growing in Nordic mid-market. Phase 3. |
| P3 | `co-xero-connector` | Xero API connector. Very low priority for Nordic launch — negligible Nordic market share. Relevant only for future UK/ANZ expansion. |
| P3 | `co-period-comparison` | Side-by-side prior period comparison in the report view with variance column. |
| P3 | `co-load-tests` | Synthetic load tests: 10k/50k/200k entry datasets against consolidation endpoint; define and enforce <5s SLA. |

---

### Track: `trust/compliance`

| Priority | Bead Name | Description |
|---|---|---|
| P1 | `co-eu-data-residency` | Confirm and document EU data residency (AWS eu-north-1 Stockholm preferred, or Azure Sweden Central). Produce standard DPA template. State hosting location on product website and in contract. Procurement gate for any Nordic Persona B or C buyer. |
| P1 | `co-trial-balance-zero-ui` | Surface the "consolidated TB nets to zero" invariant as a visible confirmation on the report screen, including the exact net figure and a pass/fail indicator. |
| P1 | `co-methodology-doc` | Publish the elimination methodology as a customer-facing document (derived from consolidation-logic.md) that can be handed to an external auditor as the engine's reference specification. Include the dual-validator description explicitly. Required before any Nordic enterprise or Big 4 advisory channel engagement. |
| P1 | `co-audit-package-export` | Full audit package export: multi-sheet Excel with consolidated P&L, consolidated BS, elimination schedule (typed, counterparty, amount), entity-level TBs pre/post elimination, NCI calculation, period-lock log. Nordic auditors (FAR-accredited) will expect this format. |
| P1 | `co-k3-compliance-research` | Detailed K3 consolidation requirements study: document all K3 differences from IFRS 10 (full goodwill method, goodwill amortisation, deferred tax on eliminated profits, BAS disclosure requirements). Commission or conduct with a K3-qualified Swedish accountant. Precedes `co-k3-mode`. |
| P2 | `co-approval-workflow` | Multi-user roles (submitter, controller, CFO approver) with approval states per period, email notifications, and an immutable sign-off log attached to the locked period record. |
| P2 | `co-control-assessment-doc` | Add a `control_basis` field to entity_metadata (majority ownership, contractual, de facto) and surface it in the ownership tree so auditors can see the basis for inclusion of each entity. |
| P2 | `co-restatement-workflow` | Governed restatement path: open a restatement sub-period, post reversing entries, re-run eliminations, produce a restated vs. original comparison report. |
| P2 | `co-pacera-competitive-monitoring` | Ongoing competitive intelligence: track Pacera (AARO + Aico + Mercur) product releases, pricing signals, and GTM moves. Subscribe to Pacera/AARO customer references and monitor Accel-KKR portfolio announcements. Review quarterly. |
| P3 | `co-ifrs18-readiness` | Assess impact of IFRS 18 (mandatory FY2027) on account classification categories (Operating / Investing / Financing) and flag any GCoA mapping changes required. |

---

### Track: `ux`

| Priority | Bead Name | Description |
|---|---|---|
| P1 | `co-drill-down` | Clickable drill-down from consolidated figure → entity breakdown → individual ledger entries → source file reference (CSV row or SIE4 transaction). Exportable at each level. |
| P1 | `co-submission-dashboard` | Pre-consolidation entity submission status dashboard: traffic-light view of which entities have submitted, which are pending, and any zero-entry warnings for the selected period. |
| P2 | `co-interco-reconciliation-view` | Intercompany matrix view: for each entity pair, show the INTERCO_REC, INTERCO_PAY, and any mismatch. Allows the group controller to chase subsidiaries before running consolidation. |
| P2 | `co-period-lock-guard` | Already in roadmap — disable Upload and Consolidate buttons on locked period, show clear banner. |
| P2 | `co-entity-tree-viz` | Already in roadmap — ownership tree visualisation with ownership percentages and NCI labels. |
| P3 | `co-pdf-report` | PDF rendering of the consolidated report for board pack and statutory filing use. |
| P3 | `co-playwright-smoke` | Playwright smoke test suite covering the end-to-end demo story: entity creation, SIE4 or CSV upload, consolidation run, report view, Excel export. |

---

### Track: `gtm`

| Priority | Bead Name | Description |
|---|---|---|
| P1 | `co-gtm-fortnox-partnership` | Establish Fortnox integration partner relationship. Publish app to Fortnox marketplace. Agree co-marketing terms. This is the single highest-leverage GTM action for Swedish Persona A. |
| P1 | `co-gtm-partner-programme` | Design and launch accounting firm partner programme: refer-and-recommend tier, white-label tier, certified adviser tier. Initial targets: BDO Sweden, Grant Thornton Sweden, Azets Scandinavia. Document referral fee structure, training programme, and co-marketing materials. |
| P2 | `co-gtm-nordic-landing-page` | Swedish-language product marketing page: Fortnox integration badge, K3/IFRS framing, free trial CTA, data residency statement, reference customer quotes. |
| P2 | `co-gtm-visma-partnership` | Establish Visma partner relationship for Norway/Denmark. Parallel to Fortnox for Norwegian Persona A. |
| P3 | `co-gtm-pe-operating-partners` | Map Nordic PE operating partner community (EQT, Altor, Triton, Nordic Capital, Verdane, Summa). Identify 10–15 key contacts. Build outreach programme for Persona C pipeline. |

---

_Research document prepared by Product Manager. Revised following CPO review, 2026-03-27. Further recommended: at least two interviews with Swedish Auktoriserad revisors at mid-tier firms (BDO, Grant Thornton, Azets) before the next planning session._
