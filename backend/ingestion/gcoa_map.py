"""Global Chart of Accounts mapping table.

Maps (subsidiary_code, local_account_code) -> gcoa_account_code.

Structure:
  - Keys are (entity_id, local_code) tuples.
  - Values are GCoA account codes from the standard chart.

GCoA account number ranges:
  1xxx  Assets
  2xxx  Liabilities
  3xxx  Equity
  4xxx  Revenue
  5xxx  Cost of Sales
  6xxx  Operating Expenses
  7xxx  Other Income/Expense

Each subsidiary may use its own local numbering; this table normalises them.
"""

from __future__ import annotations

from typing import Dict, Optional, Tuple

# ---------------------------------------------------------------------------
# Seed mapping — 10 subsidiaries × representative accounts
# ---------------------------------------------------------------------------
# Format: { (entity_id, local_account_code): gcoa_account_code }

GCOA_MAPPING: Dict[Tuple[str, str], str] = {}

# Helper to register a subsidiary's chart in bulk.
def _register(entity_id: str, local_to_gcoa: Dict[str, str]) -> None:
    for local, gcoa in local_to_gcoa.items():
        GCOA_MAPPING[(entity_id, local)] = gcoa


# Subsidiary SUBS_01 — US Operations
_register("SUBS_01", {
    "1000": "1100",  # Cash → Cash & Cash Equivalents
    "1100": "1200",  # Accounts Receivable → Trade Receivables
    "1200": "1300",  # Inventory → Inventories
    "1500": "1500",  # PP&E → Property, Plant & Equipment
    "2000": "2100",  # Accounts Payable → Trade Payables
    "2100": "2200",  # Accrued Liabilities → Accrued Liabilities
    "2500": "2500",  # Long-Term Debt → Long-Term Borrowings
    "3000": "3100",  # Common Stock → Share Capital
    "3100": "3200",  # Retained Earnings → Retained Earnings
    "4000": "4100",  # Sales Revenue → Revenue from Contracts
    "5000": "5100",  # COGS → Cost of Sales
    "6000": "6100",  # Salaries → Employee Benefits Expense
    "6100": "6200",  # Rent → Occupancy Expense
    "6200": "6300",  # Depreciation → Depreciation & Amortisation
    "7000": "7100",  # Interest Expense → Finance Costs
    "7100": "7200",  # Interest Income → Finance Income
})

# Subsidiary SUBS_02 — UK Operations
_register("SUBS_02", {
    "1001": "1100",
    "1101": "1200",
    "1201": "1300",
    "1501": "1500",
    "2001": "2100",
    "2101": "2200",
    "2501": "2500",
    "3001": "3100",
    "3101": "3200",
    "4001": "4100",
    "5001": "5100",
    "6001": "6100",
    "6101": "6200",
    "6201": "6300",
    "7001": "7100",
    "7101": "7200",
})

# Subsidiary SUBS_03 — Germany Operations
_register("SUBS_03", {
    "1002": "1100",
    "1102": "1200",
    "1202": "1300",
    "1502": "1500",
    "2002": "2100",
    "2102": "2200",
    "2502": "2500",
    "3002": "3100",
    "3102": "3200",
    "4002": "4100",
    "5002": "5100",
    "6002": "6100",
    "6102": "6200",
    "6202": "6300",
    "7002": "7100",
    "7102": "7200",
})

# Subsidiary SUBS_04 — France Operations
_register("SUBS_04", {
    "1003": "1100",
    "1103": "1200",
    "1203": "1300",
    "1503": "1500",
    "2003": "2100",
    "2103": "2200",
    "2503": "2500",
    "3003": "3100",
    "3103": "3200",
    "4003": "4100",
    "5003": "5100",
    "6003": "6100",
    "6103": "6200",
    "6203": "6300",
    "7003": "7100",
    "7103": "7200",
})

# Subsidiary SUBS_05 — Singapore Operations
_register("SUBS_05", {
    "1004": "1100",
    "1104": "1200",
    "1204": "1300",
    "1504": "1500",
    "2004": "2100",
    "2104": "2200",
    "2504": "2500",
    "3004": "3100",
    "3104": "3200",
    "4004": "4100",
    "5004": "5100",
    "6004": "6100",
    "6104": "6200",
    "6204": "6300",
    "7004": "7100",
    "7104": "7200",
})

# Subsidiary SUBS_06 — Japan Operations
_register("SUBS_06", {
    "1005": "1100",
    "1105": "1200",
    "1205": "1300",
    "1505": "1500",
    "2005": "2100",
    "2105": "2200",
    "2505": "2500",
    "3005": "3100",
    "3105": "3200",
    "4005": "4100",
    "5005": "5100",
    "6005": "6100",
    "6105": "6200",
    "6205": "6300",
    "7005": "7100",
    "7105": "7200",
})

# Subsidiary SUBS_07 — Australia Operations
_register("SUBS_07", {
    "1006": "1100",
    "1106": "1200",
    "1206": "1300",
    "1506": "1500",
    "2006": "2100",
    "2106": "2200",
    "2506": "2500",
    "3006": "3100",
    "3106": "3200",
    "4006": "4100",
    "5006": "5100",
    "6006": "6100",
    "6106": "6200",
    "6206": "6300",
    "7006": "7100",
    "7106": "7200",
})

# Subsidiary SUBS_08 — Canada Operations
_register("SUBS_08", {
    "1007": "1100",
    "1107": "1200",
    "1207": "1300",
    "1507": "1500",
    "2007": "2100",
    "2107": "2200",
    "2507": "2500",
    "3007": "3100",
    "3107": "3200",
    "4007": "4100",
    "5007": "5100",
    "6007": "6100",
    "6107": "6200",
    "6207": "6300",
    "7007": "7100",
    "7107": "7200",
})

# Subsidiary SUBS_09 — Brazil Operations
_register("SUBS_09", {
    "1008": "1100",
    "1108": "1200",
    "1208": "1300",
    "1508": "1500",
    "2008": "2100",
    "2108": "2200",
    "2508": "2500",
    "3008": "3100",
    "3108": "3200",
    "4008": "4100",
    "5008": "5100",
    "6008": "6100",
    "6108": "6200",
    "6208": "6300",
    "7008": "7100",
    "7108": "7200",
})

# Subsidiary SUBS_10 — India Operations
_register("SUBS_10", {
    "1009": "1100",
    "1109": "1200",
    "1209": "1300",
    "1509": "1500",
    "2009": "2100",
    "2109": "2200",
    "2509": "2500",
    "3009": "3100",
    "3109": "3200",
    "4009": "4100",
    "5009": "5100",
    "6009": "6100",
    "6109": "6200",
    "6209": "6300",
    "7009": "7100",
    "7109": "7200",
})


# ---------------------------------------------------------------------------
# Demo entities — ParentCo / SubA / SubB (3-entity consolidation group)
# ---------------------------------------------------------------------------

_register("ParentCo", {
    "CASH":            "1100",
    "PPE":             "1500",
    "INVEST_SUB_A":    "INVEST_SUB",
    "INVEST_SUB_B":    "INVEST_SUB",
    "INTERCO_REC_A":   "INTERCO_REC",
    "DIVIDEND_REC_B":  "DIVIDEND_REC",
    "AP":              "2100",
    "LTD":             "2500",
    "EQUITY_SHARE_CAP": "EQUITY_SHARE_CAP",
    "RETAINED":        "3200",
})

_register("SubA", {
    "CASH":            "1100",
    "AR":              "1200",
    "INV":             "1300",
    "PPE":             "1500",
    "INTERCO_PAY_P":   "INTERCO_PAY",
    "AP":              "2100",
    "EQUITY_SHARE_CAP": "EQUITY_SHARE_CAP",
    "RETAINED":        "3200",
    "REV":             "4100",
    "INTERCO_REV_B":   "INTERCO_REV",
    "COGS":            "5100",
})

_register("SubB", {
    "CASH":            "1100",
    "AR":              "1200",
    "INV":             "1300",
    "PPE":             "1500",
    "AP":              "2100",
    "LTD":             "2500",
    "EQUITY_SHARE_CAP": "EQUITY_SHARE_CAP",
    "RETAINED":        "3200",
    "DIVIDEND_PAID_P": "DIVIDEND_PAID",
    "REV":             "4100",
    "INTERCO_COGS_A":  "INTERCO_COGS",
    "COGS":            "5100",
})


def lookup(entity_id: str, local_code: str) -> Optional[str]:
    """Return the GCoA account code for a given subsidiary + local code, or None."""
    return GCOA_MAPPING.get((entity_id, local_code.strip()))
