"""IFRS 10 Elimination Calculator — stateless, pure projection.

Usage::

    from engine import IfrsCalculator, LedgerEntrySnapshot, EntityNode

    eliminations = IfrsCalculator.eliminate(entries, entities, as_of=cutoff_dt)

The calculator never reads from or writes to any database.  It takes an
in-memory snapshot and returns a list of EliminationEntry objects that
the caller may choose to persist (or not).

Two elimination steps are performed in order:

1. **Intercompany elimination** — matches INTERCO_REC and INTERCO_PAY
   accounts across entity pairs and produces offsetting entries so that
   the intercompany balances net to zero on consolidation.

2. **Equity elimination** — for each parent→child relationship in the
   entity hierarchy, eliminates the parent's INVEST_SUB account against
   the child's EQUITY_* accounts so that the consolidated statement does
   not double-count the subsidiary's net assets.

Account-code conventions and the signed-amount convention are documented
in engine/models.py.
"""

from __future__ import annotations

import uuid
from collections import defaultdict
from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional, Set, Tuple

from .models import EliminationEntry, EntityNode, LedgerEntrySnapshot

# ---------------------------------------------------------------------------
# Account-code sentinels
# ---------------------------------------------------------------------------

_INTERCO_REC_PREFIX = "INTERCO_REC"
_INTERCO_PAY_PREFIX = "INTERCO_PAY"
_INVEST_SUB_PREFIX = "INVEST_SUB"
_EQUITY_PREFIX = "EQUITY_"
_NCI_EQUITY_CODE = "NCI_EQUITY"
_DIVIDEND_PAID_PREFIX = "DIVIDEND_PAID"
_DIVIDEND_REC_PREFIX = "DIVIDEND_REC"
_INTERCO_REV_PREFIX = "INTERCO_REV"
_INTERCO_COGS_PREFIX = "INTERCO_COGS"


def _is_interco_rec(entry: LedgerEntrySnapshot) -> bool:
    return entry.account_code.startswith(_INTERCO_REC_PREFIX)


def _is_interco_pay(entry: LedgerEntrySnapshot) -> bool:
    return entry.account_code.startswith(_INTERCO_PAY_PREFIX)


def _is_invest_sub(entry: LedgerEntrySnapshot) -> bool:
    return entry.account_code.startswith(_INVEST_SUB_PREFIX)


def _is_equity(entry: LedgerEntrySnapshot) -> bool:
    return entry.account_code.startswith(_EQUITY_PREFIX)


def _is_dividend_paid(entry: LedgerEntrySnapshot) -> bool:
    return entry.account_code.startswith(_DIVIDEND_PAID_PREFIX)


def _is_dividend_rec(entry: LedgerEntrySnapshot) -> bool:
    return entry.account_code.startswith(_DIVIDEND_REC_PREFIX)


def _is_interco_rev(entry: LedgerEntrySnapshot) -> bool:
    return entry.account_code.startswith(_INTERCO_REV_PREFIX)


def _is_interco_cogs(entry: LedgerEntrySnapshot) -> bool:
    return entry.account_code.startswith(_INTERCO_COGS_PREFIX)


def _counterparty(entry: LedgerEntrySnapshot) -> Optional[uuid.UUID]:
    """Return the counterparty entity UUID from entry metadata, or None."""
    if not entry.metadata:
        return None
    raw = entry.metadata.get("counterparty_entity_id")
    if raw is None:
        return None
    try:
        return uuid.UUID(str(raw))
    except ValueError:
        return None


def _subsidiary_id(entry: LedgerEntrySnapshot) -> Optional[uuid.UUID]:
    """Return the subsidiary entity UUID from entry metadata, or None."""
    if not entry.metadata:
        return None
    raw = entry.metadata.get("subsidiary_entity_id")
    if raw is None:
        return None
    try:
        return uuid.UUID(str(raw))
    except ValueError:
        return None


# ---------------------------------------------------------------------------
# Entity hierarchy helpers
# ---------------------------------------------------------------------------

def _build_entity_set(entities: List[EntityNode]) -> Set[uuid.UUID]:
    """Return the full set of entity IDs in the consolidation group."""
    return {e.entity_id for e in entities}


def _parent_child_pairs(entities: List[EntityNode]) -> List[Tuple[uuid.UUID, uuid.UUID]]:
    """Return (parent_entity_id, child_entity_id) for every parent→child edge."""
    return [
        (e.parent_entity_id, e.entity_id)
        for e in entities
        if e.parent_entity_id is not None
    ]


# ---------------------------------------------------------------------------
# Main calculator
# ---------------------------------------------------------------------------

class IfrsCalculator:
    """Stateless IFRS 10 consolidation calculator.

    All methods are class-level so callers need not instantiate anything.
    """

    @classmethod
    def eliminate(
        cls,
        entries: List[LedgerEntrySnapshot],
        entities: List[EntityNode],
        as_of: datetime,
    ) -> List[EliminationEntry]:
        """Compute IFRS 10 elimination entries for a ledger snapshot.

        Args:
            entries:  All ledger entries for the consolidation group.
                      Entries after *as_of* and already-eliminated entries
                      are silently ignored.
            entities: The entity hierarchy.  Must include every entity
                      referenced in *entries*.
            as_of:    Cut-off timestamp (inclusive).

        Returns:
            A list of EliminationEntry objects (is_elimination=True).
            The list may be empty if there is nothing to eliminate.
            The caller is responsible for any persistence.
        """
        entity_ids = _build_entity_set(entities)

        # Filter to eligible entries: within the cut-off, not already
        # elimination entries, and belonging to entities in scope.
        eligible = [
            e for e in entries
            if e.timestamp <= as_of
            and not e.is_elimination
            and e.entity_id in entity_ids
        ]

        step1 = cls._eliminate_intercompany(eligible, entity_ids, as_of)
        step2 = cls._eliminate_equity(eligible, entities, entity_ids, as_of)
        step3 = cls._eliminate_dividends(eligible, entities, entity_ids, as_of)
        step4 = cls._eliminate_interco_revenue(eligible, entity_ids, as_of)

        return step1 + step2 + step3 + step4

    # ------------------------------------------------------------------
    # Step 1: Intercompany elimination
    # ------------------------------------------------------------------

    @classmethod
    def _eliminate_intercompany(
        cls,
        entries: List[LedgerEntrySnapshot],
        entity_ids: Set[uuid.UUID],
        as_of: datetime,
    ) -> List[EliminationEntry]:
        """Zero out matched intercompany receivable / payable pairs.

        For each (entity_A, entity_B) pair we sum:
          - entity_A's INTERCO_REC entries where counterparty == entity_B
          - entity_B's INTERCO_PAY entries where counterparty == entity_A

        Both should sum to the same absolute value (one positive, one
        negative).  We create offsetting elimination entries for each
        side regardless of whether the pair perfectly balances — this
        surfaces mismatches in the resulting trial balance for human
        review rather than silently masking them.
        """
        eliminations: List[EliminationEntry] = []

        # rec_totals[(holder_id, counterparty_id)] = net receivable amount
        rec_totals: Dict[Tuple[uuid.UUID, uuid.UUID], Decimal] = defaultdict(Decimal)
        # pay_totals[(holder_id, counterparty_id)] = net payable amount
        pay_totals: Dict[Tuple[uuid.UUID, uuid.UUID], Decimal] = defaultdict(Decimal)

        for entry in entries:
            cp = _counterparty(entry)
            if cp is None or cp not in entity_ids:
                continue
            if _is_interco_rec(entry):
                rec_totals[(entry.entity_id, cp)] += entry.amount
            elif _is_interco_pay(entry):
                pay_totals[(entry.entity_id, cp)] += entry.amount

        # Produce one elimination entry per side of each matched pair.
        # We deduplicate pairs so (A→B) and (B→A) are handled together.
        seen_pairs: Set[Tuple[uuid.UUID, uuid.UUID]] = set()

        for (holder, counterparty), rec_amount in rec_totals.items():
            if (counterparty, holder) in seen_pairs:
                continue
            seen_pairs.add((holder, counterparty))

            # Eliminate the receivable side (negate: credit the asset)
            if rec_amount != Decimal("0"):
                eliminations.append(
                    EliminationEntry(
                        entry_id=uuid.uuid4(),
                        timestamp=as_of,
                        entity_id=holder,
                        account_code=_INTERCO_REC_PREFIX,
                        amount=-rec_amount,
                        is_elimination=True,
                        metadata={
                            "elimination_type": "intercompany_receivable",
                            "counterparty_entity_id": str(counterparty),
                        },
                    )
                )

            # Eliminate the payable side (negate: debit the liability)
            pay_amount = pay_totals.get((counterparty, holder), Decimal("0"))
            if pay_amount != Decimal("0"):
                eliminations.append(
                    EliminationEntry(
                        entry_id=uuid.uuid4(),
                        timestamp=as_of,
                        entity_id=counterparty,
                        account_code=_INTERCO_PAY_PREFIX,
                        amount=-pay_amount,
                        is_elimination=True,
                        metadata={
                            "elimination_type": "intercompany_payable",
                            "counterparty_entity_id": str(holder),
                        },
                    )
                )

        # Handle any payable-only entries (no matching receivable was recorded)
        for (holder, counterparty), pay_amount in pay_totals.items():
            pair = (counterparty, holder)
            if pair in seen_pairs or (holder, counterparty) in seen_pairs:
                continue
            seen_pairs.add((holder, counterparty))
            if pay_amount != Decimal("0"):
                eliminations.append(
                    EliminationEntry(
                        entry_id=uuid.uuid4(),
                        timestamp=as_of,
                        entity_id=holder,
                        account_code=_INTERCO_PAY_PREFIX,
                        amount=-pay_amount,
                        is_elimination=True,
                        metadata={
                            "elimination_type": "intercompany_payable",
                            "counterparty_entity_id": str(counterparty),
                        },
                    )
                )

        return eliminations

    # ------------------------------------------------------------------
    # Step 2: Equity elimination
    # ------------------------------------------------------------------

    @classmethod
    def _eliminate_equity(
        cls,
        entries: List[LedgerEntrySnapshot],
        entities: List[EntityNode],
        entity_ids: Set[uuid.UUID],
        as_of: datetime,
    ) -> List[EliminationEntry]:
        """Eliminate parent's investment account against subsidiary equity.

        For each parent→child pair:
          1. Sum all INVEST_SUB entries on the parent where
             metadata.subsidiary_entity_id == child's entity_id.
          2. Sum all EQUITY_* entries on the child.
          3. Split equity into parent share and NCI share based on ownership_pct.
          4. Eliminate parent's share and investment; post NCI share to NCI_EQUITY.

        If the investment and equity totals differ, both sides are still
        eliminated at their respective book values, leaving an implicit
        goodwill or bargain-purchase residual visible in the trial balance.
        """
        eliminations: List[EliminationEntry] = []

        # Build ownership_pct lookup: entity_id -> ownership_pct (0-100)
        ownership: Dict[uuid.UUID, Decimal] = {
            e.entity_id: (e.ownership_pct if e.ownership_pct is not None else Decimal("100"))
            for e in entities
        }

        # Pre-compute per-entity investment and equity totals
        # invest_totals[parent_id][subsidiary_id] = total investment amount
        invest_totals: Dict[uuid.UUID, Dict[uuid.UUID, Decimal]] = defaultdict(
            lambda: defaultdict(Decimal)
        )
        # equity_totals[child_id] = total equity amount
        equity_totals: Dict[uuid.UUID, Decimal] = defaultdict(Decimal)

        for entry in entries:
            if _is_invest_sub(entry):
                sub_id = _subsidiary_id(entry)
                if sub_id is not None and sub_id in entity_ids:
                    invest_totals[entry.entity_id][sub_id] += entry.amount
            elif _is_equity(entry):
                equity_totals[entry.entity_id] += entry.amount

        for parent_id, child_id in _parent_child_pairs(entities):
            invest_amount = invest_totals[parent_id].get(child_id, Decimal("0"))
            equity_amount = equity_totals.get(child_id, Decimal("0"))
            pct = ownership.get(child_id, Decimal("100"))

            parent_share = (equity_amount * pct / Decimal("100")).quantize(Decimal("0.0001"))
            nci_share = equity_amount - parent_share

            # Eliminate parent's investment (credit: negate debit balance)
            if invest_amount != Decimal("0"):
                eliminations.append(
                    EliminationEntry(
                        entry_id=uuid.uuid4(),
                        timestamp=as_of,
                        entity_id=parent_id,
                        account_code=_INVEST_SUB_PREFIX,
                        amount=-invest_amount,
                        is_elimination=True,
                        metadata={
                            "elimination_type": "equity_investment",
                            "subsidiary_entity_id": str(child_id),
                        },
                    )
                )

            # Eliminate parent's share of subsidiary equity
            if parent_share != Decimal("0"):
                eliminations.append(
                    EliminationEntry(
                        entry_id=uuid.uuid4(),
                        timestamp=as_of,
                        entity_id=child_id,
                        account_code=_EQUITY_PREFIX.rstrip("_"),
                        amount=-parent_share,
                        is_elimination=True,
                        metadata={
                            "elimination_type": "equity_subsidiary",
                            "parent_entity_id": str(parent_id),
                            "ownership_pct": str(pct),
                        },
                    )
                )

            # Post NCI share to NCI_EQUITY (not eliminated — stays on BS)
            if nci_share != Decimal("0"):
                eliminations.append(
                    EliminationEntry(
                        entry_id=uuid.uuid4(),
                        timestamp=as_of,
                        entity_id=child_id,
                        account_code=_NCI_EQUITY_CODE,
                        amount=-nci_share,
                        is_elimination=True,
                        metadata={
                            "elimination_type": "nci_equity",
                            "parent_entity_id": str(parent_id),
                            "nci_pct": str(Decimal("100") - pct),
                        },
                    )
                )

        return eliminations

    # ------------------------------------------------------------------
    # Step 3: Dividend elimination
    # ------------------------------------------------------------------

    @classmethod
    def _eliminate_dividends(
        cls,
        entries: List[LedgerEntrySnapshot],
        entities: List[EntityNode],
        entity_ids: Set[uuid.UUID],
        as_of: datetime,
    ) -> List[EliminationEntry]:
        """Eliminate intragroup dividends (IFRS 10.B86(b)).

        For each parent→child pair, sum:
          - DIVIDEND_PAID on child (debit reduces equity, counterparty = parent)
          - DIVIDEND_REC on parent (credit income, counterparty = child)

        Both sides are negated to eliminate the intercompany dividend flow.
        """
        eliminations: List[EliminationEntry] = []

        # div_paid_totals[child_id][parent_id] = total paid
        div_paid: Dict[uuid.UUID, Dict[uuid.UUID, Decimal]] = defaultdict(
            lambda: defaultdict(Decimal)
        )
        # div_rec_totals[parent_id][child_id] = total received
        div_rec: Dict[uuid.UUID, Dict[uuid.UUID, Decimal]] = defaultdict(
            lambda: defaultdict(Decimal)
        )

        for entry in entries:
            cp = _counterparty(entry)
            if cp is None or cp not in entity_ids:
                continue
            if _is_dividend_paid(entry):
                div_paid[entry.entity_id][cp] += entry.amount
            elif _is_dividend_rec(entry):
                div_rec[entry.entity_id][cp] += entry.amount

        for parent_id, child_id in _parent_child_pairs(entities):
            paid_amount = div_paid[child_id].get(parent_id, Decimal("0"))
            rec_amount = div_rec[parent_id].get(child_id, Decimal("0"))

            if paid_amount != Decimal("0"):
                eliminations.append(
                    EliminationEntry(
                        entry_id=uuid.uuid4(),
                        timestamp=as_of,
                        entity_id=child_id,
                        account_code=_DIVIDEND_PAID_PREFIX,
                        amount=-paid_amount,
                        is_elimination=True,
                        metadata={
                            "elimination_type": "dividend_paid",
                            "counterparty_entity_id": str(parent_id),
                        },
                    )
                )

            if rec_amount != Decimal("0"):
                eliminations.append(
                    EliminationEntry(
                        entry_id=uuid.uuid4(),
                        timestamp=as_of,
                        entity_id=parent_id,
                        account_code=_DIVIDEND_REC_PREFIX,
                        amount=-rec_amount,
                        is_elimination=True,
                        metadata={
                            "elimination_type": "dividend_received",
                            "counterparty_entity_id": str(child_id),
                        },
                    )
                )

        return eliminations

    # ------------------------------------------------------------------
    # Step 4: Intragroup revenue / COGS elimination
    # ------------------------------------------------------------------

    @classmethod
    def _eliminate_interco_revenue(
        cls,
        entries: List[LedgerEntrySnapshot],
        entity_ids: Set[uuid.UUID],
        as_of: datetime,
    ) -> List[EliminationEntry]:
        """Eliminate intragroup revenue/COGS pairs (IFRS 10.B86(c)).

        For each (seller, buyer) pair:
          - Negate INTERCO_REV on seller
          - Negate INTERCO_COGS on buyer
        """
        eliminations: List[EliminationEntry] = []

        # rev_totals[(seller_id, buyer_id)] = total revenue
        rev_totals: Dict[Tuple[uuid.UUID, uuid.UUID], Decimal] = defaultdict(Decimal)
        # cogs_totals[(buyer_id, seller_id)] = total COGS
        cogs_totals: Dict[Tuple[uuid.UUID, uuid.UUID], Decimal] = defaultdict(Decimal)

        for entry in entries:
            cp = _counterparty(entry)
            if cp is None or cp not in entity_ids:
                continue
            if _is_interco_rev(entry):
                rev_totals[(entry.entity_id, cp)] += entry.amount
            elif _is_interco_cogs(entry):
                cogs_totals[(entry.entity_id, cp)] += entry.amount

        seen_pairs: Set[Tuple[uuid.UUID, uuid.UUID]] = set()

        for (seller, buyer), rev_amount in rev_totals.items():
            if (buyer, seller) in seen_pairs:
                continue
            seen_pairs.add((seller, buyer))

            if rev_amount != Decimal("0"):
                eliminations.append(
                    EliminationEntry(
                        entry_id=uuid.uuid4(),
                        timestamp=as_of,
                        entity_id=seller,
                        account_code=_INTERCO_REV_PREFIX,
                        amount=-rev_amount,
                        is_elimination=True,
                        metadata={
                            "elimination_type": "interco_revenue",
                            "counterparty_entity_id": str(buyer),
                        },
                    )
                )

            cogs_amount = cogs_totals.get((buyer, seller), Decimal("0"))
            if cogs_amount != Decimal("0"):
                eliminations.append(
                    EliminationEntry(
                        entry_id=uuid.uuid4(),
                        timestamp=as_of,
                        entity_id=buyer,
                        account_code=_INTERCO_COGS_PREFIX,
                        amount=-cogs_amount,
                        is_elimination=True,
                        metadata={
                            "elimination_type": "interco_cogs",
                            "counterparty_entity_id": str(seller),
                        },
                    )
                )

        # Handle COGS-only entries
        for (buyer, seller), cogs_amount in cogs_totals.items():
            pair = (seller, buyer)
            if pair in seen_pairs or (buyer, seller) in seen_pairs:
                continue
            seen_pairs.add((buyer, seller))
            if cogs_amount != Decimal("0"):
                eliminations.append(
                    EliminationEntry(
                        entry_id=uuid.uuid4(),
                        timestamp=as_of,
                        entity_id=buyer,
                        account_code=_INTERCO_COGS_PREFIX,
                        amount=-cogs_amount,
                        is_elimination=True,
                        metadata={
                            "elimination_type": "interco_cogs",
                            "counterparty_entity_id": str(seller),
                        },
                    )
                )

        return eliminations
