# Consolidation Logic — IFRS 10 Elimination

This document explains the financial logic behind the `IfrsCalculator` in
`engine/calculator.py`.

---

## What is IFRS 10 Consolidation?

When a parent company owns subsidiaries, the group must publish a single set of
**consolidated financial statements** that represent the group as one economic
entity. IFRS 10 is the international accounting standard that governs this.

The core challenge: subsidiaries record transactions with each other and with the
parent. If you simply add all their Trial Balances together, you double-count:

- A loan from the parent appears as an asset on the parent's books **and** a
  liability on the subsidiary's books.
- The parent's ownership stake appears as an asset on the parent's books **and**
  as equity on the subsidiary's books.

**Elimination entries** remove this double-counting so the consolidated statement
reflects only transactions with third parties outside the group.

---

## The Immutable Ledger Pattern

All financial postings — including eliminations — are stored as immutable events
in `ledger_entries`. The calculator **never writes to the database**. It:

1. Receives an in-memory snapshot of all ledger entries up to an `as_of` timestamp.
2. Computes elimination entries as pure Python objects (`EliminationEntry`).
3. Returns them to the caller, who may choose to persist them.

This means:
- You can re-run the calculator at any past timestamp and get the same result.
- The audit trail is never modified — only extended.
- Corrections are made by posting new reversing entries, never by editing existing ones.

---

## Elimination Step 1: Intercompany Balances

### Why

Suppose Subsidiary A lends €100k to Subsidiary B:
- Subsidiary A records: `INTERCO_REC (counterparty=B) +100,000` (asset)
- Subsidiary B records: `INTERCO_PAY (counterparty=A) -100,000` (liability)

When consolidated, these two entries cancel out. The loan is internal to the
group and has no economic substance to an outside observer.

### How the calculator does it

Account codes prefixed with `INTERCO_REC` or `INTERCO_PAY` are treated as
intercompany accounts. Each entry's `metadata.counterparty_entity_id` identifies
the other entity in the transaction.

For each (Entity A, Entity B) pair, the calculator:

1. Sums Entity A's `INTERCO_REC` entries where counterparty = B → `rec_amount`
2. Sums Entity B's `INTERCO_PAY` entries where counterparty = A → `pay_amount`
3. Emits an elimination entry on Entity A: `INTERCO_REC, amount = -rec_amount`
4. Emits an elimination entry on Entity B: `INTERCO_PAY, amount = -pay_amount`

If `rec_amount ≠ |pay_amount|` (a mismatch), **both sides are still eliminated
at their book values**. The residual imbalance surfaces in the consolidated trial
balance, signalling a data quality issue for human review rather than being
silently suppressed.

### Account code convention

| Prefix | Side | Sign |
|--------|------|------|
| `INTERCO_REC` | Receivable (asset) | Positive (debit) |
| `INTERCO_PAY` | Payable (liability) | Negative (credit) |

---

## Elimination Step 2: Equity Elimination

### Why

When a parent acquires a subsidiary, it records the investment:
- Parent records: `INVEST_SUB (subsidiary=B) +500,000` (asset — cost of investment)
- Subsidiary B records its net assets as equity: `EQUITY_SHARE_CAP +500,000`, etc.

From a consolidated perspective, the parent's investment and the subsidiary's
equity both represent the same net assets. Showing both would inflate the group's
balance sheet. The investment and equity are therefore eliminated against each other.

### How the calculator does it

Account codes prefixed with `INVEST_SUB` on the parent side and `EQUITY_` on the
subsidiary side are the targets.

For each parent → child relationship in `entity_metadata`:

1. Sum the parent's `INVEST_SUB` entries where `metadata.subsidiary_entity_id = child` → `invest_amount`
2. Sum the child's `EQUITY_*` entries → `equity_amount`
3. Emit an elimination entry on the parent: `INVEST_SUB, amount = -invest_amount`
4. Emit an elimination entry on the child: `EQUITY, amount = -equity_amount`

### Goodwill residual

If `invest_amount ≠ equity_amount`, the difference is **goodwill** (or a
bargain-purchase gain if negative). The current implementation eliminates both
sides at book value and leaves the residual implicit in the trial balance.
A future enhancement would explicitly post the residual to a `GOODWILL` account.

### Account code convention

| Prefix | Entity | Notes |
|--------|--------|-------|
| `INVEST_SUB` | Parent | Asset — cost of investment in subsidiary |
| `EQUITY_*` | Subsidiary | All equity accounts (share capital, retained earnings, etc.) |

---

## Worked Example

### Group structure

```
Parent Co  (100% owns)
  └── Sub A  (100% owns)
        └── Sub B
```

### Ledger entries before elimination

| Entity | Account | Amount | Notes |
|--------|---------|--------|-------|
| Parent | `INVEST_SUB` (sub=A) | +800,000 | Investment in Sub A |
| Sub A | `EQUITY_SHARE_CAP` | +800,000 | Sub A's equity |
| Sub A | `INVEST_SUB` (sub=B) | +200,000 | Investment in Sub B |
| Sub B | `EQUITY_SHARE_CAP` | +200,000 | Sub B's equity |
| Sub A | `INTERCO_REC` (cp=B) | +50,000 | Loan to Sub B |
| Sub B | `INTERCO_PAY` (cp=A) | -50,000 | Loan from Sub A |

### Elimination entries produced

| Entity | Account | Amount | Type |
|--------|---------|--------|------|
| Parent | `INVEST_SUB` | -800,000 | equity_investment |
| Sub A | `EQUITY` | -800,000 | equity_subsidiary |
| Sub A | `INVEST_SUB` | -200,000 | equity_investment |
| Sub B | `EQUITY` | -200,000 | equity_subsidiary |
| Sub A | `INTERCO_REC` | -50,000 | intercompany_receivable |
| Sub B | `INTERCO_PAY` | +50,000 | intercompany_payable |

After adding these eliminations to the trial balance, the consolidated statement
shows only the group's third-party assets, liabilities, and equity — with no
double-counting.

---

## Calling the Calculator

```python
from engine import IfrsCalculator, LedgerEntrySnapshot, EntityNode
from datetime import datetime, timezone

entries: list[LedgerEntrySnapshot] = [...]   # from ledger DB
entities: list[EntityNode] = [...]           # from entity_metadata DB
as_of = datetime(2024, 12, 31, tzinfo=timezone.utc)

eliminations = IfrsCalculator.eliminate(entries, entities, as_of=as_of)

# eliminations is a list[EliminationEntry] — persist as needed
```

The calculator is **pure**: no I/O, no global state, fully unit-testable without
a database. See `engine/tests/test_calculator.py` for comprehensive examples.

---

## Phase 2 Additions

The following elimination steps were added in Phase 2:

### Step 3: Dividend Elimination (IFRS 10.B86(b))

Intercompany dividends are eliminated so that a subsidiary paying a dividend to
its parent does not inflate group income.

For each parent → child pair:
- Sum `DIVIDEND_PAID` on the child where `metadata.counterparty_entity_id = parent`
- Sum `DIVIDEND_REC` on the parent where `metadata.counterparty_entity_id = child`
- Emit offsetting elimination entries on both sides

### Step 4: Intragroup Revenue / COGS Elimination (IFRS 10.B86(c))

When one group entity sells goods to another, the revenue on the seller and the
cost on the buyer are both eliminated so that internal sales do not inflate
consolidated revenue or cost of sales.

For each (seller, buyer) pair:
- Sum `INTERCO_REV` on the seller where `metadata.counterparty_entity_id = buyer`
- Sum `INTERCO_COGS` on the buyer where `metadata.counterparty_entity_id = seller`
- Emit offsetting elimination entries on both sides

### NCI Split in Equity Elimination (IFRS 10.22)

When `ownership_pct < 100`, the subsidiary's equity is split before elimination:

- **Parent's share** = `equity × (ownership_pct / 100)` → eliminated against `INVEST_SUB`
- **NCI share** = `equity × (1 − ownership_pct / 100)` → posted to `NCI_EQUITY`

`NCI_EQUITY` is **not** eliminated — it remains on the consolidated balance sheet
as the non-controlling interest's claim on the group's net assets.

---

## Known Limitations

- **Goodwill** — when `invest_amount ≠ equity_amount` the residual is implicit
  in the trial balance. A future enhancement would explicitly post to a `GOODWILL`
  account (IFRS 3 / IFRS 10.B86(d)).
- **Multi-currency** — all amounts are assumed to be in a single reporting currency.
  No IAS 21 FX translation step is performed.
- **Control assessment** — `ownership_pct` is used as a proxy for control.
  The full IFRS 10.7 power / returns test is out of scope.
- **Uniform accounting policies** — no enforcement that all entities use the
  same accounting policies before consolidation.
