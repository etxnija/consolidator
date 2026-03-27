# CPO Feedback: Product Research Review
## North Star Consolidator — Nordic Market Assessment

**To:** Product Manager
**From:** CPO
**Date:** 2026-03-27
**Re:** Product Research Document — Nordic Gaps and Re-prioritisation

---

## Upfront Summary

The research document is a solid first pass for a pan-European or UK-centric product. The IFRS 10 gap analysis is technically competent, the competitive wedge is correctly identified, and the trust/transparency framing is genuinely good strategic thinking. But if we are building a consolidation product for the Nordic market — which is where our near-term GTM focus should be — this document is missing the market. Almost every section defaults to a UK/global frame. The personas assume Xero and QuickBooks. The competitors named are the London consulting scene's reference list. The regulatory section treats IFRS 10 as universal when it is not, in this region, for the segment we are targeting.

I have gone through each section below. Some of the feedback is blunt. That is because the gaps are material, not cosmetic.

---

## 1. Nordic Market Sizing and Segments

### The PM's personas are geographically unanchored

The three personas (Mid-Market CFO, Listed-Company Group Controller, PE-Backed Portfolio CFO) are structurally sound but they float in an unspecified market. There is no Nordic lens. The revenue ranges are in GBP. The ERP references are Xero, QuickBooks, and Sage — none of which are dominant in the Nordics at the SME tier.

### What the actual addressable market looks like

Sweden accounts for approximately 41% of Nordic enterprises by count, followed by Finland and Norway at roughly 20% each and Denmark at 15%. The Nordic combined ERP market is approximately $1.3 billion in 2025, with Sweden the largest single market at around $470 million. The Nordics are highly digitalised — cloud adoption among SMEs is high, but that cuts both ways: it means buyers are ERP-native and expect integrations, not CSV uploads.

The addressable segment for a 2–20 entity consolidation tool in the Nordics is real but not enormous. A conservative estimate: there are perhaps 8,000–15,000 parent companies in Sweden, Norway, Denmark, and Finland with 2–20 subsidiaries in the relevant revenue band (SEK 50m–1.5bn, roughly €5m–€140m). The challenge is that a significant portion of these already have a solution — either Excel with an external accountant, or AARO (now Pacera), or Visma's built-in consolidation features, or Cognos Controller for larger listed entities. The genuinely underserved pocket is the lower end: groups of 2–6 entities that have outgrown Excel but are below the minimum viable scale for AARO or Lucanet.

### Which country first?

Sweden. Here is why:

- Sweden has the largest Nordic enterprise base (41% of Nordic companies).
- Fortnox dominates Swedish SME accounting with 612,000+ customers and approximately 60% cloud accounting market share — and Fortnox does not have a native group consolidation product. This is a partnership and integration opportunity that does not exist in the same form in Denmark (e-conomic) or Norway (Visma/Tripletex). Critically, there is already a third-party connector (Otisco) specifically linking Fortnox to AARO — which confirms the demand signal.
- AARO (now Pacera, backed by Accel-KKR) is the incumbent in Swedish consolidation but targets listed companies and larger mid-market groups. It is not self-serve. There is a genuine gap below it.
- Stockholm has the deepest PE and VC finance ecosystem in the Nordics, which feeds Persona C (PE-Backed Portfolio CFO) directly.
- Sweden's K3 standard (see regulatory section below) is well-understood by local accountants and creates local GAAP consolidation work that the current research ignores.

Norway second. Denmark third (e-conomic's dominance creates a natural integration wedge). Finland fourth — more SAP-heavy at mid-market, harder to penetrate without Finnish-language support.

### WTP numbers in the Nordic context

The document's WTP ranges (£500–£1,500/month for Persona A; £1,500–£3,000/month for Persona B) are plausible in GBP terms and directionally correct for the Nordics. Nordic CFOs pay for quality software — the region is not price-sensitive in the same way as southern Europe. However, a few calibrations:

- Swedish and Norwegian companies will want pricing in local currency (SEK/NOK), not GBP or EUR. This sounds trivial but it matters for procurement and optics.
- The Persona A WTP should be expressed against the local accountant cost benchmark. In Sweden, an external consolidation engagement with a Big 4 or mid-tier firm for a 4-entity group runs SEK 80,000–250,000 per year (roughly £6,000–£18,000). A SaaS tool at SEK 8,000–15,000/month (£600–£1,100/month) that eliminates most of that engagement is a credible save.
- AARO/Pacera's pricing (not publicly disclosed, but knowable from market conversations) is in the SEK 150,000–600,000/year range for a mid-market group. This is the ceiling above which North Star does not need to compete.

---

## 2. Nordic ERP Landscape

### The PM has the wrong ERP list

The document mentions SAP, NetSuite, and Oracle as the primary ERP integrations to build. For the Nordic SME and lower mid-market segment — which is our target — this is almost entirely wrong. The actual ERP landscape by segment:

**Sweden:**
- Fortnox: 612,000+ customers, dominant in micro and small companies. No native group consolidation. The connector gap is real and exploitable.
- Visma Net / Business NXT: Strong in mid-market (€10m–€200m revenue). Has some built-in consolidation features (basic group accounts) but they are not statutory-quality.
- Microsoft Dynamics 365 Business Central: Growing fast in mid-market, good local payroll and tax modules, no strong native consolidation story.
- SAP Business One / S/4HANA: Present at the upper mid-market and large end. Worth integrating eventually, but not the beachhead.

**Norway:**
- Tripletex: Dominant in small Norwegian companies. Owned by Visma.
- Visma Business / Visma.net: Mid-market staple.
- 24SevenOffice: Growing cloud ERP challenger.

**Denmark:**
- e-conomic (Visma): ~250,000 customers in Denmark and beyond. The Danish equivalent of Fortnox. No group consolidation native capability.
- Dynamics 365: Strong in larger Danish mid-market.

**Finland:**
- Procountor / Netvisor (Visma): Dominant in Finnish SME accounting.
- SAP has higher penetration in Finnish mid-market than elsewhere in the Nordics.

### What this means for integration strategy

The document recommends: NetSuite API → Xero API → QuickBooks API → SAP BAPI.

For the Nordic market this sequence should be: **Fortnox API → e-conomic (Visma) API → Visma Net API → Dynamics 365 BC API → SAP Business One**.

NetSuite is present in PE-backed Nordic portfolio companies (Persona C) and is worth building, but it is not the entry point for the Swedish SME segment. Xero and QuickBooks have negligible share in the Nordics. Building a Xero connector first is building for the UK market, not this one.

### What Nordic CFOs actually export for consolidation today

This is missing from the research document entirely. The current practice for a 4-entity Swedish group running on Fortnox is: each entity's controller exports a trial balance as an Excel or CSV file from Fortnox (SIE format is also common — the Swedish standard interchange format for accounting data). These are emailed to the group controller, who manually pastes them into a master Excel consolidation model. SIE (Standard Import Export) is the Swedish accounting data interchange format mandated by BAS (the Swedish accounting standards body). Any consolidation tool targeting Sweden should natively import SIE4-format files. This is not mentioned anywhere in the research document and it is a material gap — a CFO who sees "upload CSV" when they are used to SIE export will assume the tool does not understand Swedish accounting.

---

## 3. Nordic Competitors

### The competitive map is incomplete and misleading for this region

The document names Tagetik, OneStream, Lucanet, and Excel. This is correct for a global or UK framing. In the Nordics, the competitive map is materially different.

**AARO (now Pacera) — the competitor the PM missed entirely**

This is the most significant gap in the competitive section. AARO is a Swedish consolidation software company, founded in 1989, that now holds approximately 30% of Nasdaq Stockholm Large Cap listed companies as customers. In January 2026, AARO merged with Aico (financial close automation) and Mercur (FP&A) to form Pacera, backed by Accel-KKR. The combined entity supports 700+ organisations across Europe.

AARO is the dominant brand in Swedish consolidation. Any Swedish CFO evaluating a consolidation tool will have AARO in the evaluation set. Not mentioning it in the research document is a significant blind spot.

What AARO covers: full IFRS consolidation, Swedish K3 support, IFRS and local GAAP, Fortnox and Visma integrations (via Otisco connector), listed company compliance. Its target is mid-market to large enterprise — typically groups with SEK 500m+ revenue. Its pricing and implementation model mean it is not self-serve.

North Star's positioning against AARO: same as against Lucanet — below its floor, self-serve, no implementation project. But you need to know AARO exists before you can position against it.

**Visma Consolidation — built-in but limited**

Visma Software Nordic offers basic group consolidation within its ERP products (Visma Net, Business NXT). This covers simple group accounts for Norwegian and Swedish parent companies. It is not statutory-quality IFRS consolidation — it handles basic elimination but does not produce audit-ready output, does not handle complex NCI, and has limited goodwill support. However, for a simple 3-entity group all running on Visma, the CFO may see the built-in feature as "good enough." This is a competitive threat at the bottom of the market that the research does not acknowledge.

**IBM Cognos Controller — entrenched in larger Nordic listed companies**

Sweden accounts for roughly 14% of Cognos Controller's global customer base — the highest country concentration outside North America. This is a legacy installed base at listed Nordic companies. Cognos Controller users are typically groups with 10–50 entities on SAP or similar large ERP. They are not our near-term target, but they matter because: (a) their CFOs have experience with proper consolidation tools and will have high expectations, and (b) when these companies downsize or spin off divisions, the spun-off entity may be our Persona B target with strong product expectations from day one.

**Lucanet — present but no Nordic office**

Lucanet has no office in Stockholm or any Nordic city. Nordic customers are served through continental European operations (Netherlands, UK). This is a distribution weakness — Nordic CFOs tend to prefer vendors with local presence, local language support, and understanding of local GAAP (K3, NRS). Lucanet's gap here is genuine and exploitable. However, Lucanet's DACH success and growing UK presence means it will eventually turn Nordic attention. If North Star is not established before that happens, the window closes.

**The Excel + external accountant competitive reality**

The document correctly identifies this as the dominant incumbent. In the Nordic context, add specificity: the "external accountant" for a mid-sized Swedish group consolidation is typically one of the Big 4 (PwC, Deloitte, EY, KPMG — all have strong Swedish practices) or a mid-tier firm like BDO or Grant Thornton. These firms perform the year-end consolidation as a managed service. They have a financial interest in the status quo. Winning against Excel means not just selling software — it means either (a) co-selling through those firms (they white-label or recommend the tool) or (b) winning the CFO directly and displacing the firm's consolidation engagement. Option (a) is slower to close but stickier and referral-driven. Option (b) is faster but creates firm antagonism. The research says nothing about this.

---

## 4. Nordic Regulatory Context

### The IFRS 10 assumption does not hold for the target segment

This is the most consequential gap in the research document. The document assumes IFRS 10 is the relevant consolidation standard throughout. For listed companies on Nasdaq Nordic (Stockholm, Copenhagen, Helsinki, Oslo), this is correct — IFRS is mandatory for consolidated accounts. But listed companies are not our initial target. Our target is Personas A and C: unlisted owner-operated groups and PE-backed portfolio companies. For these companies, the regulatory picture is materially different.

**Sweden — K3**

Unlisted Swedish parent companies preparing consolidated accounts must use K3 (BFNAR 2012:1), developed by the Swedish Accounting Standards Board (BFN). K3 is based on IFRS for SMEs but with significant modifications for Swedish law and tax practice. Key consolidation differences from full IFRS 10:

- K3 uses the **full goodwill method** (goodwill is recognised on the full fair value of the subsidiary, not just the parent's share). This is the same as IFRS 3 under one of the two permitted methods, but it means the goodwill calculation is standardised and cannot use the proportionate NCI method the document describes as the platform's current approach.
- K3 has specific rules for **intercompany profit elimination in inventory** that differ from IFRS 10 in the treatment of deferred tax on eliminated profits.
- K3 consolidation disclosures are different from IFRS 10 — the note structure for NCI, goodwill, and related-party transactions follows Swedish BAS chart of accounts conventions, not IFRS presentation.
- **An unlisted Swedish group that uses the North Star platform and produces IFRS 10-compliant consolidated accounts may not be producing K3-compliant accounts.** If their statutory filings must be under K3, there is a compliance gap the platform currently cannot address. This is a legal risk, not a product preference.

**Norway — NRS**

Unlisted Norwegian companies use Norwegian GAAP (NRS — Norsk RegnskapsStandard). Key points:

- Listed Norwegian companies must use IFRS for consolidated accounts. Unlisted companies may choose between full IFRS, a simplified IFRS variant, or Norwegian GAAP.
- Norwegian GAAP has its own consolidation standard (NRS 17 — Virksomhetssammenslutninger and NRS consolidated accounts guidance) which differs from IFRS 10 in several respects, including goodwill amortisation (NRS still permits amortisation over useful life, whereas IFRS 10/IAS 36 requires impairment testing only).
- Goodwill amortisation under NRS is a significant difference: a Norwegian unlisted group using North Star would need the platform to support periodic goodwill amortisation entries, not just annual impairment testing.

**Denmark — Årsregnskabsloven (ÅRL)**

Danish companies use the Danish Financial Statements Act (Årsregnskabsloven). Class C companies (roughly equivalent to mid-market) must prepare consolidated accounts but may use Danish GAAP or IFRS. The Danish rules for consolidation are broadly IFRS-aligned but have local characteristics in disclosure and presentation.

**Finland — Finnish Accounting Act**

Finnish unlisted groups use the Finnish Accounting Act (Kirjanpitolaki) with FAS standards. Similar story — IFRS-aligned in substance for consolidation but with local presentation differences.

### The risk of building purely for IFRS 10

If North Star positions as an "IFRS 10-correct" consolidation tool and targets unlisted Nordic groups, a significant portion of those groups' statutory accounts will need K3 (Sweden) or NRS (Norway) compliance, not IFRS 10. The platform as designed will produce accounts that are incorrect under local GAAP for those companies. This is not a minor note disclosure issue — it affects goodwill measurement, intercompany profit elimination, and possibly minority interest calculation.

The immediate implication is: **scope the platform clearly as IFRS 10 only, and document explicitly that unlisted Swedish and Norwegian companies should confirm with their auditor whether IFRS 10 is applicable to their consolidated accounts before using it.** Do not let this become a silent compliance gap. The longer-term implication is that a K3 module would dramatically expand the addressable market in Sweden. It is non-trivial to build but worth scoping.

---

## 5. Trust and Adoption in the Nordics

### The trust section is accurate but generic

The PM's trust section correctly identifies the core problem (CFO personal liability, need for audit trail, rules-based vs. AI positioning). This framing holds up in the Nordics. But the Nordic context adds specific nuances:

**Data sovereignty and EU hosting**

Nordic CFOs, particularly in Sweden and Finland (both EU members), have strong preferences for EU-hosted data. Norway (not EU) has its own sovereignty concerns. Denmark's public sector has notably retreated from US-cloud arrangements. The research document says nothing about where data is hosted.

A Nordic CFO evaluating a new SaaS finance tool will ask: where is the data hosted? Is it in the EU? Which data centre? Who has access? For statutory consolidated accounts — which contain entity-level P&L and balance sheet data that may be commercially sensitive — this is not a checkbox question. It is a procurement gate.

The practical implication: North Star needs to be hosted in an EU data centre (AWS eu-north-1 Stockholm, or Azure Sweden Central, or equivalent) and needs to be able to state this clearly in procurement conversations. If it is on US infrastructure, a meaningful proportion of Nordic enterprise buyers will not proceed without a Data Processing Agreement and legal review — adding 2–3 months to the sales cycle.

**Auditor attitudes in the Nordics**

PwC, Deloitte, EY, and KPMG all have significant Swedish and Nordic practices. PwC is the largest auditor in Norway by market share. In Sweden, PwC and KPMG are dominant in listed company audit; BDO and Grant Thornton are the main mid-tier players.

Nordic audit culture is conservative and technically rigorous. Swedish auditors (Auktoriserad revisor / Godkänd revisor under the accountant body FAR) are thorough on consolidation methodology. Key points:

- Nordic auditors will scrutinise methodology documentation. The PM's recommendation to publish a public methodology document is exactly right for this market. It is not optional — it is what a Swedish Big 4 team will request before accepting a client who uses the platform.
- The "dual-validator" differentiator (two independent implementations cross-checked) is genuinely compelling to a Nordic technical auditor. This should be in the methodology document explicitly.
- Nordic auditors are conservative about new software. A tool without a track record of being accepted in an audit will face resistance. The path to auditor acceptance is: (a) methodology document, (b) a few reference customers who have completed audits using the platform, and (c) ideally a formal dialogue with one of the Big 4 Nordic audit practices before we go to market.

**GDPR enforcement in the Nordics**

All four Nordic EU states (Sweden, Finland, Denmark) have active GDPR supervisory authorities with enforcement records. The Schrems II implications and related transfer restrictions are taken seriously by Nordic legal and compliance teams. Finance data is sensitive data. Any North Star marketing that promises "your data stays in the EU" needs to be architecturally true and contractually documented, not just a marketing claim.

---

## 6. Go-to-Market

### How consolidation tools are actually sold in the Nordics

The research document says nothing about GTM. This is a significant gap.

In the Nordic market, consolidation tools are sold through three main channels, in roughly descending order of current importance for the target segment:

**1. Accounting and advisory firms (ERP-agnostic)**

The most common initial evaluation trigger is an audit observation, a new CFO, or an M&A event (acquisition adds entity count). When this happens, the CFO typically calls their external accountant or advisor first. That advisor — often a BDO, Grant Thornton, PwC, or EY mid-market team — recommends or runs a tool selection. If North Star is not in the consideration set of those advisors, it is invisible to most buyers.

The implication: prioritise relationships with mid-tier Nordic accounting firms (BDO Sweden, Grant Thornton Sweden, Azets Scandinavia) over Big 4. Mid-tier firms have more mid-market clients in the 2–8 entity range. Big 4 will want reference clients before engaging.

**2. ERP vendor channel (especially Fortnox ecosystem)**

In Sweden, there is an established ecosystem of Fortnox partners who provide add-on services (payroll, invoicing, reporting) to Fortnox customers. A native Fortnox integration with a published app in the Fortnox partner marketplace would drive inbound for Persona A (Swedish SME CFO) without requiring a direct sales team. This is the single highest-leverage GTM action for the Swedish market and it is not in the research document at all.

**3. Direct / inbound**

Nordic CFOs are digitally literate and will search. A Swedish-language landing page with a Fortnox integration, a clear K3/IFRS framing, and a free trial would generate inbound from the target segment. The product must be self-serve to convert this — which aligns with the PM's existing positioning.

### Sales cycle for the target pricing tier

For a tool at SEK 6,000–18,000/month (£500–£1,500/month) targeting Persona A, the realistic sales cycle is 4–12 weeks. The CFO is the buyer and the decision-maker. There is no IT sign-off at this size. The main friction is:

1. Auditor acceptance (can the CFO show their auditor the methodology document and get a green light?)
2. ERP integration (does it connect to Fortnox or Visma — if yes, friction drops significantly)
3. Local GAAP question (is this IFRS 10 only, or does it support K3?)

For Persona B (listed company group controller), the cycle is 3–6 months. IT will be involved. The audit committee or CFO will want to see references. Legal will want a DPA and data residency confirmation.

---

## 7. What the PM Got Right

To be direct about what holds up:

**The market wedge is correctly identified.** "Below Lucanet's floor, above Excel's ceiling" is accurate and compelling. This is the right strategic frame.

**The IFRS 10 gap analysis is technically strong.** The multi-currency gap (IAS 21), the goodwill explicit posting gap, and the unrealised profit in inventory gap are all correctly identified and correctly prioritised. Elevating goodwill to P1 is the right call.

**The trust and transparency framing is genuinely good.** The "rules-based, not AI" positioning is differentiated and credible. The recommendation to publish the methodology document publicly is exactly right for a Nordic auditor-literate buyer. The dual-validator as a marketing claim rather than an internal implementation detail is smart.

**The personas are structurally sound.** The three personas (Mid-Market CFO, Listed Group Controller, PE-Backed Portfolio CFO) map to real buyer profiles in the Nordics, even if the details need Nordic calibration.

**The UX requirements are correct.** Drill-down from consolidated figure to source entry, submission status dashboard, approval workflow — these are genuine CFO requirements that are not over-specified.

**The audit package export requirement is right.** A Nordic auditor will expect a multi-sheet Excel workbook matching the structure described. The elimination schedule with typed entries and counterparties is exactly what a FAR-accredited Swedish auditor will look for.

---

## 8. Revised Backlog Priorities

Given Nordic market realities, here is my re-prioritisation of the 22 backlog items, plus what is missing.

### Re-prioritise: move these up

**`co-ias21-translation` (P1) — correct, keep at P1**
No change needed. Multi-currency is already a P1 and that is right. A Swedish parent with a Norwegian or Finnish subsidiary is multi-currency by definition (SEK/NOK/EUR).

**`co-goodwill-explicit` (elevate to P1) — correct, keep**
Already recommended as P1. This is correct for both IFRS 10 and K3. Under K3's full goodwill method, explicit goodwill posting is if anything more important than under IFRS 10.

**`co-audit-package-export` (P1) — correct**
Keep at P1. Nordic auditors will not accept a tool that cannot produce a structured audit package.

**`co-methodology-doc` (P1) — correct and urgent for Nordic GTM**
This is not just a product item — it is a prerequisite for auditor acceptance in Sweden. Without a public methodology document, Nordic audit teams will not bless client use of the platform. This must be customer-facing before any Nordic launch.

### Demote or defer

**`co-netsuite-connector` (P2) — defer for Nordic launch, do not drop**
NetSuite is not the Nordic entry point. For the Swedish SME segment (Persona A), Fortnox is. Defer NetSuite until Phase 2 (PE-backed portfolio companies, Persona C). Do not drop — it matters for that persona.

**`co-xero-connector` (P3) — very low priority for Nordics**
Xero has negligible Nordic market share. This is a UK/ANZ integration. Deprioritise entirely for the Nordic launch; it can be built later for any UK-facing expansion.

### Missing from the backlog entirely

**`co-sie-import` — P1 for Nordic launch**
SIE (Standard Import Export) is the Swedish accounting data interchange format. Every Fortnox, Visma, and Björn Lundén customer can export SIE4 files. If North Star cannot ingest SIE4, Swedish accountants will see it as not understanding Swedish accounting. This is the Nordic equivalent of not supporting CSV — it is a table-stakes compatibility requirement. It is not in the backlog at all. Add it as P1 for Swedish launch.

**`co-fortnox-connector` — P1 for Swedish market, replaces `co-xero-connector`**
A direct Fortnox API integration, or at minimum a published Fortnox partner marketplace listing, is the single most leveraged GTM action for Sweden. Fortnox has 612,000 customers. A native connector that replaces the manual CSV export step is the unlock for Persona A in Sweden. This belongs at P1 for the Swedish launch, not absent from the backlog.

**`co-k3-mode` — P2, scoped for Swedish unlisted groups**
A K3 compliance mode — covering full goodwill method, K3 note disclosure templates, and BAS chart of accounts mapping — would materially expand the addressable market in Sweden beyond IFRS-reporting entities. It is non-trivial but it should be scoped and placed in the backlog. Unlisted Swedish groups (the majority of Persona A) may not be able to use an IFRS 10-only tool for their statutory accounts.

**`co-eu-data-residency` — P1 before any Nordic enterprise sale**
Confirm and document EU data residency (ideally Sweden or EU North). Produce a standard DPA template. Make the hosting location visible on the product website and in contract documentation. This is a procurement gate for any Nordic Persona B or C buyer and for any Swedish public-sector adjacent company.

**`co-nordic-language-support` — P2, Swedish first**
The platform will need to function in Swedish for accountants who are not fully English-language fluent. This does not mean full localisation on day one, but the UI should be navigable in English by Nordic users (this is generally fine — Nordic professionals are strong English speakers). However, the help documentation, methodology document, and support channels need a Swedish-language option before enterprise-scale Nordic adoption.

**`co-bas-chart-of-accounts` — P2 for Sweden**
BAS (Baskontoplan) is the standard Swedish chart of accounts used by virtually every Swedish company. A pre-built BAS-to-GCoA mapping would eliminate the most common onboarding friction for Swedish Persona A customers. This is the Swedish equivalent of a QuickBooks or Xero chart of accounts template. It is not in the backlog.

---

## Summary: The Three Things to Fix First

1. **Add AARO/Pacera to the competitive section.** It is the dominant Nordic consolidation vendor, present in 30% of Nasdaq Stockholm Large Cap companies, and was just reorganised with PE backing. We cannot have a Nordic product strategy that does not account for it.

2. **Reframe the regulatory section.** Add K3 (Sweden) and NRS (Norway) as parallel standards to IFRS 10. Document clearly which companies must use which standard. Add `co-k3-mode` and `co-sie-import` to the backlog. Until this is done, the platform has a compliance gap for the majority of its target customers in Sweden.

3. **Rewrite the ERP integration roadmap for Nordic reality.** Replace `co-xero-connector` (negligible Nordic relevance) with `co-fortnox-connector` and `co-sie-import`. Move `co-netsuite-connector` from P2 to Phase 2. Add e-conomic (Visma) and Visma Net as Phase 2 integrations. The current integration roadmap optimises for the UK/US market, not Sweden.

---

*This feedback is intended to redirect the next research revision, not to replace it. The PM should revisit the document with Nordic CFO and auditor interviews — specifically at least two interviews with Swedish Auktoriserad revisors at mid-tier firms (BDO, Grant Thornton, Azets) before the next planning session.*
