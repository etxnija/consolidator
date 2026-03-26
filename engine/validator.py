"""Independent IFRS 10 consolidation validator — Pandas-based spreadsheet arithmetic.

Completely separate implementation from engine.calculator.  Uses vectorized
DataFrame operations (pivot/groupby) rather than imperative loops and dicts.

Purpose
-------
1. Cross-check that IfrsCalculator produces correct eliminations.
2. Assert the hard mathematical invariant: consolidated trial balance nets to
   zero when the source ledger is balanced (each debit has a matching credit).

CLI usage (standalone audit)::

    python -m engine.audit

or for custom data::

    python -m engine.audit ledger.csv entities.csv 2025-12-31

Input CSV formats
-----------------
ledger.csv columns:
    entry_id, timestamp, entity_id, account_code, amount,
    is_elimination, counterparty_entity_id, subsidiary_entity_id

entities.csv columns:
    entity_id, name, parent_entity_id, ownership_pct

Signed-amount convention matches engine.models (positive = debit, negative = credit).
"""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

import pandas as pd

from .models import EntityNode, LedgerEntrySnapshot


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _entries_to_df(
    entries: List[LedgerEntrySnapshot],
    entity_ids: set,
    as_of: datetime,
) -> pd.DataFrame:
    """Convert eligible LedgerEntrySnapshot list to a flat DataFrame.

    Filters: timestamp ≤ as_of, not already an elimination, entity in scope.
    """
    rows = []
    for e in entries:
        if e.timestamp > as_of or e.is_elimination or e.entity_id not in entity_ids:
            continue
        meta = e.metadata or {}
        rows.append({
            "entity_id": str(e.entity_id),
            "account_code": e.account_code,
            "amount": float(e.amount),
            "counterparty_id": meta.get("counterparty_entity_id"),
            "subsidiary_id": meta.get("subsidiary_entity_id"),
        })
    if not rows:
        return pd.DataFrame(
            columns=["entity_id", "account_code", "amount", "counterparty_id", "subsidiary_id"]
        )
    return pd.DataFrame(rows)


def _empty_result() -> pd.DataFrame:
    return pd.DataFrame(
        columns=["entity_id", "account_code", "amount", "elimination_type"]
    )


# ---------------------------------------------------------------------------
# PandasValidator
# ---------------------------------------------------------------------------

class PandasValidator:
    """Pandas-based IFRS 10 elimination validator — independent of IfrsCalculator.

    All methods are class-level (stateless).  Call ``expected_eliminations``
    to get a DataFrame of elimination rows, then compare against the
    IfrsCalculator output in the test harness.
    """

    @classmethod
    def expected_eliminations(
        cls,
        entries: List[LedgerEntrySnapshot],
        entities: List[EntityNode],
        as_of: datetime,
    ) -> pd.DataFrame:
        """Compute expected elimination entries using Pandas operations.

        Returns a DataFrame with columns:
            entity_id (str), account_code (str), amount (float),
            elimination_type (str)

        The rows represent the *same logical eliminations* as
        IfrsCalculator.eliminate(), computed via an independent code path.
        """
        entity_ids = {e.entity_id for e in entities}
        entity_strs = {str(eid) for eid in entity_ids}

        df = _entries_to_df(entries, entity_ids, as_of)

        parts = [
            cls._interco(df, entity_strs),
            cls._equity(df, entities, entity_strs),
            cls._dividends(df, entities, entity_strs),
            cls._interco_revenue(df, entity_strs),
        ]
        non_empty = [p for p in parts if not p.empty]
        if not non_empty:
            return _empty_result()
        return pd.concat(non_empty, ignore_index=True)

    # ------------------------------------------------------------------
    # Step 1: Intercompany receivable / payable
    # ------------------------------------------------------------------

    @classmethod
    def _interco(cls, df: pd.DataFrame, entity_strs: set) -> pd.DataFrame:
        """Vectorised intercompany REC / PAY elimination."""
        rows = []

        rec = df[
            df["account_code"].str.startswith("INTERCO_REC")
            & df["counterparty_id"].isin(entity_strs)
        ]
        pay = df[
            df["account_code"].str.startswith("INTERCO_PAY")
            & df["counterparty_id"].isin(entity_strs)
        ]

        # Sum each (holder, counterparty) pair
        rec_sums = (
            rec.groupby(["entity_id", "counterparty_id"])["amount"].sum()
            if not rec.empty
            else pd.Series(dtype=float)
        )
        pay_sums = (
            pay.groupby(["entity_id", "counterparty_id"])["amount"].sum()
            if not pay.empty
            else pd.Series(dtype=float)
        )

        seen: set = set()

        for (holder, cp), rec_total in rec_sums.items():
            if (cp, holder) in seen:
                continue
            seen.add((holder, cp))
            if rec_total != 0:
                rows.append(
                    {
                        "entity_id": holder,
                        "account_code": "INTERCO_REC",
                        "amount": -rec_total,
                        "elimination_type": "intercompany_receivable",
                    }
                )
            # Matching payable on the other entity
            pay_total = pay_sums.get((cp, holder), 0.0)
            if pay_total != 0:
                rows.append(
                    {
                        "entity_id": cp,
                        "account_code": "INTERCO_PAY",
                        "amount": -pay_total,
                        "elimination_type": "intercompany_payable",
                    }
                )

        # Payable-only pairs (no matching receivable was found)
        for (holder, cp), pay_total in pay_sums.items():
            if (cp, holder) in seen or (holder, cp) in seen:
                continue
            seen.add((holder, cp))
            if pay_total != 0:
                rows.append(
                    {
                        "entity_id": holder,
                        "account_code": "INTERCO_PAY",
                        "amount": -pay_total,
                        "elimination_type": "intercompany_payable",
                    }
                )

        return pd.DataFrame(rows) if rows else _empty_result()

    # ------------------------------------------------------------------
    # Step 2: Equity / investment elimination
    # ------------------------------------------------------------------

    @classmethod
    def _equity(
        cls,
        df: pd.DataFrame,
        entities: List[EntityNode],
        entity_strs: set,
    ) -> pd.DataFrame:
        """Vectorised equity + NCI elimination."""
        rows = []

        invest = df[
            df["account_code"].str.startswith("INVEST_SUB")
            & df["subsidiary_id"].isin(entity_strs)
        ]
        equity = df[df["account_code"].str.startswith("EQUITY_")]

        invest_sums = (
            invest.groupby(["entity_id", "subsidiary_id"])["amount"].sum()
            if not invest.empty
            else pd.Series(dtype=float)
        )
        equity_sums = (
            equity.groupby("entity_id")["amount"].sum()
            if not equity.empty
            else pd.Series(dtype=float)
        )

        ownership = {
            str(e.entity_id): float(
                e.ownership_pct if e.ownership_pct is not None else 100
            )
            for e in entities
        }

        for e in entities:
            if e.parent_entity_id is None:
                continue
            parent_str = str(e.parent_entity_id)
            child_str = str(e.entity_id)
            pct = ownership.get(child_str, 100.0)

            invest_amount = invest_sums.get((parent_str, child_str), 0.0)
            equity_amount = equity_sums.get(child_str, 0.0)

            # Mirror the Decimal.quantize(0.0001) used in IfrsCalculator
            parent_share = round(equity_amount * pct / 100, 4)
            nci_share = equity_amount - parent_share

            if invest_amount != 0:
                rows.append(
                    {
                        "entity_id": parent_str,
                        "account_code": "INVEST_SUB",
                        "amount": -invest_amount,
                        "elimination_type": "equity_investment",
                    }
                )
            if parent_share != 0:
                rows.append(
                    {
                        "entity_id": child_str,
                        "account_code": "EQUITY",
                        "amount": -parent_share,
                        "elimination_type": "equity_subsidiary",
                    }
                )
            if nci_share != 0:
                rows.append(
                    {
                        "entity_id": child_str,
                        "account_code": "NCI_EQUITY",
                        "amount": -nci_share,
                        "elimination_type": "nci_equity",
                    }
                )

        return pd.DataFrame(rows) if rows else _empty_result()

    # ------------------------------------------------------------------
    # Step 3: Dividend elimination
    # ------------------------------------------------------------------

    @classmethod
    def _dividends(
        cls,
        df: pd.DataFrame,
        entities: List[EntityNode],
        entity_strs: set,
    ) -> pd.DataFrame:
        """Vectorised dividend elimination."""
        rows = []

        paid = df[
            df["account_code"].str.startswith("DIVIDEND_PAID")
            & df["counterparty_id"].isin(entity_strs)
        ]
        rec = df[
            df["account_code"].str.startswith("DIVIDEND_REC")
            & df["counterparty_id"].isin(entity_strs)
        ]

        paid_sums = (
            paid.groupby(["entity_id", "counterparty_id"])["amount"].sum()
            if not paid.empty
            else pd.Series(dtype=float)
        )
        rec_sums = (
            rec.groupby(["entity_id", "counterparty_id"])["amount"].sum()
            if not rec.empty
            else pd.Series(dtype=float)
        )

        for ent in entities:
            if ent.parent_entity_id is None:
                continue
            parent_str = str(ent.parent_entity_id)
            child_str = str(ent.entity_id)

            paid_amount = paid_sums.get((child_str, parent_str), 0.0)
            rec_amount = rec_sums.get((parent_str, child_str), 0.0)

            if paid_amount != 0:
                rows.append(
                    {
                        "entity_id": child_str,
                        "account_code": "DIVIDEND_PAID",
                        "amount": -paid_amount,
                        "elimination_type": "dividend_paid",
                    }
                )
            if rec_amount != 0:
                rows.append(
                    {
                        "entity_id": parent_str,
                        "account_code": "DIVIDEND_REC",
                        "amount": -rec_amount,
                        "elimination_type": "dividend_received",
                    }
                )

        return pd.DataFrame(rows) if rows else _empty_result()

    # ------------------------------------------------------------------
    # Step 4: Intragroup revenue / COGS
    # ------------------------------------------------------------------

    @classmethod
    def _interco_revenue(cls, df: pd.DataFrame, entity_strs: set) -> pd.DataFrame:
        """Vectorised intragroup revenue / COGS elimination."""
        rows = []

        rev = df[
            df["account_code"].str.startswith("INTERCO_REV")
            & df["counterparty_id"].isin(entity_strs)
        ]
        cogs = df[
            df["account_code"].str.startswith("INTERCO_COGS")
            & df["counterparty_id"].isin(entity_strs)
        ]

        rev_sums = (
            rev.groupby(["entity_id", "counterparty_id"])["amount"].sum()
            if not rev.empty
            else pd.Series(dtype=float)
        )
        cogs_sums = (
            cogs.groupby(["entity_id", "counterparty_id"])["amount"].sum()
            if not cogs.empty
            else pd.Series(dtype=float)
        )

        seen: set = set()

        for (seller, buyer), rev_total in rev_sums.items():
            if (buyer, seller) in seen:
                continue
            seen.add((seller, buyer))
            if rev_total != 0:
                rows.append(
                    {
                        "entity_id": seller,
                        "account_code": "INTERCO_REV",
                        "amount": -rev_total,
                        "elimination_type": "interco_revenue",
                    }
                )
            cogs_total = cogs_sums.get((buyer, seller), 0.0)
            if cogs_total != 0:
                rows.append(
                    {
                        "entity_id": buyer,
                        "account_code": "INTERCO_COGS",
                        "amount": -cogs_total,
                        "elimination_type": "interco_cogs",
                    }
                )

        # COGS-only pairs
        for (buyer, seller), cogs_total in cogs_sums.items():
            if (seller, buyer) in seen or (buyer, seller) in seen:
                continue
            seen.add((buyer, seller))
            if cogs_total != 0:
                rows.append(
                    {
                        "entity_id": buyer,
                        "account_code": "INTERCO_COGS",
                        "amount": -cogs_total,
                        "elimination_type": "interco_cogs",
                    }
                )

        return pd.DataFrame(rows) if rows else _empty_result()


# ---------------------------------------------------------------------------
# Trial balance invariant
# ---------------------------------------------------------------------------

def assert_trial_balance_zero(
    entries: List[LedgerEntrySnapshot],
    entities: List[EntityNode],
    as_of: datetime,
    tolerance: float = 1e-4,
) -> float:
    """Assert that the consolidated trial balance sums to zero.

    Computes::

        sum(original in-scope entries) + sum(elimination entries) ≈ 0

    This invariant holds whenever the source ledger is balanced (every debit
    has a matching credit) AND the eliminations are balanced (each elimination
    is a double-entry pair).  A non-zero result reveals a data imbalance or
    an elimination logic error.

    Args:
        entries:   All ledger entries (original + any pre-existing eliminations).
        entities:  Entity hierarchy.
        as_of:     Cut-off date.
        tolerance: Absolute tolerance for the zero check (default 0.0001).

    Returns:
        The net sum (should be 0.0 ± tolerance).

    Raises:
        AssertionError: if |net| > tolerance.
    """
    from .calculator import IfrsCalculator
    from decimal import Decimal

    entity_ids = {e.entity_id for e in entities}

    original_sum = sum(
        float(e.amount)
        for e in entries
        if e.timestamp <= as_of and not e.is_elimination and e.entity_id in entity_ids
    )

    eliminations = IfrsCalculator.eliminate(entries, entities, as_of)
    elim_sum = sum(float(e.amount) for e in eliminations)

    net = original_sum + elim_sum
    assert abs(net) <= tolerance, (
        f"Consolidated trial balance does not net to zero: "
        f"original_sum={original_sum:.4f}, elim_sum={elim_sum:.4f}, net={net:.4f}"
    )
    return net
