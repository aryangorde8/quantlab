"""Constant-maturity Treasury total-return series constructed from yields.

Uses the standard fixed-income approximation for a par bond rolled daily
(see e.g. Swinkels 2019, "Simulating historical bond returns"):

    TR_t ~= y_{t-1}/252  +  D_mod * (y_{t-1} - y_t)  +  0.5 * C * (y_{t-1} - y_t)^2

where D_mod and C are the modified duration and convexity of a par bond at
yield y. Validated against the IEF ETF (7-10y Treasuries) over 2002-present.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from . import data

TRADING_DAYS = 252


def _par_duration_convexity(y: pd.Series, maturity: float) -> tuple[pd.Series, pd.Series]:
    k = 2.0  # semiannual coupons
    y = y.clip(lower=1e-4)
    n = k * maturity
    disc = (1.0 + y / k) ** (-n)
    dur = (1.0 - disc) / y  # modified duration of a par bond
    conv = (2.0 / y**2) * (1.0 - disc) - (2.0 * maturity) / (y * (1.0 + y / k) ** (n + 1.0))
    return dur, conv


def treasury_total_return(maturity: float = 10.0, start: str = "1962-01-01") -> pd.Series:
    """Daily total returns of a constant-maturity Treasury position.

    Built from ^TNX (10y CMT yield, available since 1962) for maturity=10.
    """
    ticker = {10.0: "^TNX", 5.0: "^FVX", 30.0: "^TYX"}.get(maturity, "^TNX")
    y = data.get_close(ticker, start) / 100.0
    y = y.dropna()

    y_prev = y.shift(1)
    dur, conv = _par_duration_convexity(y_prev, maturity)
    dy = y - y_prev
    tr = y_prev / TRADING_DAYS + dur * (-dy) + 0.5 * conv * dy**2
    tr.name = f"UST{maturity:g}y_TR"
    return tr.dropna()


def bond_momentum_defensive(
    rf_daily: pd.Series, maturity: float = 10.0, lookback: int = 252
) -> pd.Series:
    """Defensive leg with absolute momentum (Antonacci 2014): hold the
    `maturity`-year Treasury while its trailing 12m total return beats
    T-bills, else T-bills. Sidesteps 2022-style regimes where bonds fall
    together with stocks."""
    tr = treasury_total_return(maturity)
    rf = rf_daily.reindex(tr.index).ffill().bfill()
    cum_tr = (1.0 + tr).cumprod()
    cum_rf = (1.0 + rf).cumprod()
    better = (cum_tr / cum_tr.shift(lookback)) > (cum_rf / cum_rf.shift(lookback))
    out = pd.Series(
        np.where(better.shift(1).fillna(False), tr, rf), index=tr.index
    )
    out.name = f"UST{maturity:g}y_mom_mix"
    return out
