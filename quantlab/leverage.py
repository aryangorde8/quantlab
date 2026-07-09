"""Realistic simulation of daily-reset leveraged ETFs from an underlying index.

A leveraged ETF's daily return is modeled as:

    L * r_index - (L - 1) * (rf_daily + borrow_spread/252) - expense_ratio/252

i.e. the fund earns L times the index but pays financing on the borrowed
(L - 1) notional at the T-bill rate plus a spread, and charges its expense
ratio. This reproduces published leveraged-ETF returns closely (e.g. UPRO,
TQQQ since 2009/2010) and captures volatility decay automatically because
compounding happens daily.

Defaults follow real funds: 0.95% expense ratio (UPRO/TQQQ charge 0.86-0.95%),
0.50% financing spread over T-bills (typical for equity swap financing).
"""

from __future__ import annotations

import pandas as pd

EXPENSE_RATIO = 0.0095
BORROW_SPREAD = 0.0050
TRADING_DAYS = 252


def leveraged_returns(
    index_ret: pd.Series,
    rf_daily: pd.Series,
    leverage: float,
    expense_ratio: float = EXPENSE_RATIO,
    borrow_spread: float = BORROW_SPREAD,
) -> pd.Series:
    """Daily returns of a simulated daily-reset leveraged fund."""
    if leverage == 1.0:
        return index_ret
    rf = rf_daily.reindex(index_ret.index).ffill()
    financing = (leverage - 1.0) * (rf + borrow_spread / TRADING_DAYS)
    ret = leverage * index_ret - financing - expense_ratio / TRADING_DAYS
    ret.name = f"{index_ret.name}_{leverage:g}x"
    return ret
