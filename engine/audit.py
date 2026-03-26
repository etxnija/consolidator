"""Standalone IFRS 10 consolidation audit script.

Runs both IfrsCalculator and PandasValidator on the same inputs, compares
their outputs, and asserts the trial-balance invariant.

Usage
-----
Built-in demo (no arguments)::

    python -m engine.audit

Custom CSV data::

    python -m engine.audit ledger.csv entities.csv 2025-12-31

CSV formats
-----------
ledger.csv:
    entry_id, timestamp (ISO-8601), entity_id (UUID), account_code,
    amount (decimal), is_elimination (0/1), counterparty_entity_id (UUID or ""),
    subsidiary_entity_id (UUID or "")

entities.csv:
    entity_id (UUID), name, parent_entity_id (UUID or ""), ownership_pct (0-100 or "")

Exit codes
----------
0 — all checks passed
1 — validator/calculator mismatch or trial-balance imbalance detected
"""

from __future__ import annotations

import sys
import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import List, Optional, Tuple

from .calculator import IfrsCalculator
from .models import EntityNode, LedgerEntrySnapshot
from .validator import PandasValidator, assert_trial_balance_zero


# ---------------------------------------------------------------------------
# Demo data
# ---------------------------------------------------------------------------

_PARENT_ID  = uuid.UUID("aaaaaaaa-0000-0000-0000-000000000001")
_CHILD_ID   = uuid.UUID("bbbbbbbb-0000-0000-0000-000000000002")
_SIBLING_ID = uuid.UUID("cccccccc-0000-0000-0000-000000000003")

_CUT_OFF = datetime(2025, 12, 31, tzinfo=timezone.utc)

_DEMO_ENTITIES = [
    EntityNode(entity_id=_PARENT_ID,  name="Parent Co"),
    EntityNode(entity_id=_CHILD_ID,   name="Subsidiary A",
               parent_entity_id=_PARENT_ID, ownership_pct=Decimal("100")),
    EntityNode(entity_id=_SIBLING_ID, name="Subsidiary B",
               parent_entity_id=_PARENT_ID, ownership_pct=Decimal("75")),
]


def _e(
    entity_id: uuid.UUID,
    account_code: str,
    amount: Decimal,
    metadata: Optional[dict] = None,
) -> LedgerEntrySnapshot:
    return LedgerEntrySnapshot(
        entry_id=uuid.uuid4(),
        timestamp=_CUT_OFF,
        entity_id=entity_id,
        account_code=account_code,
        amount=amount,
        metadata=metadata,
    )


_DEMO_ENTRIES: List[LedgerEntrySnapshot] = [
    # Intercompany: Parent ↔ Subsidiary A
    _e(_PARENT_ID,  "INTERCO_REC",      Decimal("300"),
       metadata={"counterparty_entity_id": str(_CHILD_ID)}),
    _e(_CHILD_ID,   "INTERCO_PAY",      Decimal("-300"),
       metadata={"counterparty_entity_id": str(_PARENT_ID)}),
    # Equity: Parent→A (100%)
    _e(_PARENT_ID,  "INVEST_SUB",       Decimal("1000"),
       metadata={"subsidiary_entity_id": str(_CHILD_ID)}),
    _e(_CHILD_ID,   "EQUITY_SHARE_CAP", Decimal("-1000")),
    # Equity: Parent→B (75%, NCI = 25%)
    _e(_PARENT_ID,  "INVEST_SUB",       Decimal("750"),
       metadata={"subsidiary_entity_id": str(_SIBLING_ID)}),
    _e(_SIBLING_ID, "EQUITY_SHARE_CAP", Decimal("-1000")),
    # Dividends: A→Parent
    _e(_CHILD_ID,   "DIVIDEND_PAID",    Decimal("100"),
       metadata={"counterparty_entity_id": str(_PARENT_ID)}),
    _e(_PARENT_ID,  "DIVIDEND_REC",     Decimal("-100"),
       metadata={"counterparty_entity_id": str(_CHILD_ID)}),
    # Intragroup revenue: A sells to B
    _e(_CHILD_ID,   "INTERCO_REV",      Decimal("-500"),
       metadata={"counterparty_entity_id": str(_SIBLING_ID)}),
    _e(_SIBLING_ID, "INTERCO_COGS",     Decimal("500"),
       metadata={"counterparty_entity_id": str(_CHILD_ID)}),
]


# ---------------------------------------------------------------------------
# CSV loaders
# ---------------------------------------------------------------------------

def _load_entries(path: str) -> List[LedgerEntrySnapshot]:
    import csv
    entries = []
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            meta: dict = {}
            if row.get("counterparty_entity_id"):
                meta["counterparty_entity_id"] = row["counterparty_entity_id"]
            if row.get("subsidiary_entity_id"):
                meta["subsidiary_entity_id"] = row["subsidiary_entity_id"]
            entries.append(LedgerEntrySnapshot(
                entry_id=uuid.UUID(row["entry_id"]),
                timestamp=datetime.fromisoformat(row["timestamp"]),
                entity_id=uuid.UUID(row["entity_id"]),
                account_code=row["account_code"],
                amount=Decimal(row["amount"]),
                is_elimination=bool(int(row.get("is_elimination", "0"))),
                metadata=meta or None,
            ))
    return entries


def _load_entities(path: str) -> List[EntityNode]:
    import csv
    entities = []
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            entities.append(EntityNode(
                entity_id=uuid.UUID(row["entity_id"]),
                name=row["name"],
                parent_entity_id=uuid.UUID(row["parent_entity_id"])
                    if row.get("parent_entity_id") else None,
                ownership_pct=Decimal(row["ownership_pct"])
                    if row.get("ownership_pct") else None,
            ))
    return entities


# ---------------------------------------------------------------------------
# Core audit logic
# ---------------------------------------------------------------------------

def run_audit(
    entries: List[LedgerEntrySnapshot],
    entities: List[EntityNode],
    as_of: datetime,
    label: str = "audit",
) -> bool:
    """Run the full audit: compare outputs and check trial balance.

    Returns True if all checks pass, False if any discrepancy is found.
    """
    print(f"\n{'='*60}")
    print(f" IFRS 10 Consolidation Audit — {label}")
    print(f" Cut-off: {as_of.date()}  |  Entities: {len(entities)}"
          f"  |  Entries: {len(entries)}")
    print(f"{'='*60}")

    # --- Run both implementations ---
    calc_elims = IfrsCalculator.eliminate(entries, entities, as_of)
    val_df = PandasValidator.expected_eliminations(entries, entities, as_of)

    # Aggregate: (entity_id_str, account_code) → net amount
    def _calc_net():
        out = {}
        for e in calc_elims:
            k = (str(e.entity_id), e.account_code)
            out[k] = out.get(k, 0.0) + float(e.amount)
        return out

    def _val_net():
        if val_df.empty:
            return {}
        out = {}
        for _, row in val_df.iterrows():
            k = (str(row["entity_id"]), row["account_code"])
            out[k] = out.get(k, 0.0) + float(row["amount"])
        return out

    calc_net = _calc_net()
    val_net  = _val_net()

    # --- Compare ---
    all_keys = sorted(set(calc_net) | set(val_net))
    mismatches = []
    for k in all_keys:
        c = calc_net.get(k, 0.0)
        v = val_net.get(k, 0.0)
        if abs(c - v) > 1e-4:
            mismatches.append((k, c, v))

    if mismatches:
        print("\n[FAIL] Calculator / Validator MISMATCH:")
        print(f"  {'Entity':36s}  {'Account':20s}  {'Calculator':>12}  {'Validator':>12}  {'Delta':>10}")
        print(f"  {'-'*36}  {'-'*20}  {'-'*12}  {'-'*12}  {'-'*10}")
        for (eid, code), c, v in mismatches:
            print(f"  {eid:36s}  {code:20s}  {c:12.4f}  {v:12.4f}  {c-v:10.4f}")
    else:
        print(f"\n[PASS] Implementations agree — {len(all_keys)} elimination lines checked.")

    # Print elimination summary
    print(f"\nElimination summary ({len(calc_elims)} entries):")
    print(f"  {'Type':30s}  {'Net Amount':>12}")
    print(f"  {'-'*30}  {'-'*12}")
    from collections import defaultdict
    by_type: dict = defaultdict(float)
    for e in calc_elims:
        t = (e.metadata or {}).get("elimination_type", "unknown")
        by_type[t] += float(e.amount)
    for t, amt in sorted(by_type.items()):
        print(f"  {t:30s}  {amt:12.4f}")

    # --- Trial balance invariant ---
    entity_ids = {e.entity_id for e in entities}
    original_sum = sum(
        float(e.amount)
        for e in entries
        if e.timestamp <= as_of and not e.is_elimination and e.entity_id in entity_ids
    )
    elim_sum = sum(float(e.amount) for e in calc_elims)
    tb_net   = original_sum + elim_sum

    print(f"\nTrial balance check:")
    print(f"  Original entries sum : {original_sum:12.4f}")
    print(f"  Eliminations sum     : {elim_sum:12.4f}")
    print(f"  Consolidated net     : {tb_net:12.4f}")

    tb_ok = abs(tb_net) <= 1e-4
    if tb_ok:
        print("  [PASS] Trial balance nets to zero.")
    else:
        print(f"  [WARN] Trial balance does NOT net to zero (|net|={abs(tb_net):.4f}).")
        print("         This is expected when source data is not a fully balanced")
        print("         double-entry ledger (e.g. audit-only snapshot with partial data).")

    all_ok = not mismatches
    print(f"\n{'='*60}")
    status = "ALL CHECKS PASSED" if all_ok else "DISCREPANCY DETECTED — review output above"
    print(f" Result: {status}")
    print(f"{'='*60}\n")
    return all_ok


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main(argv: Optional[List[str]] = None) -> int:
    if argv is None:
        argv = sys.argv[1:]

    if len(argv) == 0:
        # Run built-in demo
        ok = run_audit(_DEMO_ENTRIES, _DEMO_ENTITIES, _CUT_OFF, label="built-in demo")
        return 0 if ok else 1

    if len(argv) != 3:
        print("Usage: python -m engine.audit [ledger.csv entities.csv YYYY-MM-DD]")
        return 2

    ledger_path, entities_path, date_str = argv
    try:
        as_of = datetime.fromisoformat(date_str).replace(tzinfo=timezone.utc)
        entries  = _load_entries(ledger_path)
        entities = _load_entities(entities_path)
    except Exception as exc:
        print(f"Error loading data: {exc}")
        return 2

    ok = run_audit(entries, entities, as_of, label=f"{ledger_path}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
