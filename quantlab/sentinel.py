"""LRS-Sentinel: a drawdown-targeted portfolio (design budget: MaxDD < 10%).

The flagship configs maximise growth and accept -50% to -67% drawdowns. This
module inverts the objective: hold drawdown under a hard budget and take the
most CAGR that budget allows.

Why the signal-level fixes in README.md cannot get there
--------------------------------------------------------
A 3x fund fell ~61% on 1987-10-19 alone. Entering that day at zero drawdown,
a 10% budget is already spent at a 16% weight in the fund — and no daily
signal can react to an overnight gap. Tightening the trend rule therefore
cannot buy a 10% budget; only *sizing* can.

The three mechanisms, all published
-----------------------------------
1. Risk parity across trend sleeves (Faber 2007 GTAA; Asness, Frazzini &
   Pedersen 2012). Equity, Treasuries and gold each carry their own trend
   filter and default to T-bills, so each sleeve is individually de-risked.
   Inverse-volatility weighting stops the 3x equity sleeve from owning all
   the risk. Diversification is what keeps CAGR from collapsing when the
   budget is tightened — it raises the book's Sharpe, and under a drawdown
   constraint CAGR is (risk-free rate + exposure x Sharpe x vol).
2. Portfolio-level volatility targeting (Moreira & Muir 2017). Scale the
   whole book to a low target vol; the remainder sits in T-bills. Drawdown
   scales roughly linearly with volatility, so this does most of the work.
3. A drawdown governor (CPPI: Black & Perold 1992; the max-drawdown
   constraint of Grossman & Zhou 1993 and Cvitanic & Karatzas 1995). This is
   the hard constraint — exposure is cut in proportion to the cushion
   remaining above the floor.

4. A stress (gap) cap. The governor reacts to *realised* drawdown, so it
   cannot price a loss that arrives overnight in a single print. Exposure is
   additionally capped so that a stress scenario — a worst-case one-day move
   per sleeve, defaulting to the 1987 experience for leveraged equity — still
   fits inside the drawdown budget that is left. This is an ordinary stress
   limit, and it is the only one of the four mechanisms that binds on gap
   risk; without it the budget is unenforceable at leverage.

The governor's known failure mode — and the fix
-----------------------------------------------
README.md records that equity-curve governors "halve DD but collapse CAGR to
12-18% by staying de-levered through recoveries". That is cash-lock: against
an all-time high-water mark the floor never moves, so once you are pinned you
miss the rebound. Two standard repairs are applied here:

- a ROLLING high-water mark (`hwm_window`), so an old peak ages out and the
  floor decays — the time-decay idea behind Estep & Kritzman's (1988) TIPP;
- a minimum exposure (`min_mult`), so the book is never fully cash-locked.

Realism
-------
Multipliers move every day, which would imply untradeable turnover. Exposure
is therefore rebalanced through a band (`band`): trade only when effective
weights drift beyond it, and pay `cost` on the notional actually traded. All
sizing inputs are lagged one day, so nothing is decided on information that
did not exist yet.
"""

from __future__ import annotations

from collections import deque

import numpy as np
import pandas as pd

COST = 0.0010  # 10 bps on traded notional, matching backtest.py
TRADING_DAYS = 252

# Worst-case one-day loss per sleeve, used by the stress cap. Equity is the
# 1987-10-19 print (-20.5% on the index) passed through fund leverage; the
# defensive sleeves get their own historical worst days, rounded up.
DEFAULT_STRESS_GAP = {
    "equity1x": 0.21,
    "equity2x": 0.41,
    "equity3x": 0.61,
    "ust10": 0.05,
    "gold": 0.12,
    "gold2x": 0.24,
}
GENERIC_STRESS_GAP = 0.25


def inverse_vol_weights(
    sleeves: pd.DataFrame, lookback: int = 60, cap: float = 0.60
) -> pd.DataFrame:
    """Risk-parity sleeve weights: proportional to 1/vol, lagged, renormalised.

    `cap` bounds any single sleeve's share so a quiet sleeve cannot take over
    the book. Weights sum to 1 and are shifted one day (decided at the prior
    close).
    """
    vol = sleeves.rolling(lookback).std() * np.sqrt(TRADING_DAYS)
    inv = 1.0 / vol.replace(0.0, np.nan)
    w = inv.div(inv.sum(axis=1), axis=0)

    # Apply the cap, then redistribute the excess over the uncapped sleeves.
    for _ in range(len(sleeves.columns)):
        over = w > cap
        if not over.to_numpy().any():
            break
        excess = (w[over] - cap).sum(axis=1).fillna(0.0)
        w = w.where(~over, cap)
        room = w.where(~over, 0.0)
        share = room.div(room.sum(axis=1).replace(0.0, np.nan), axis=0).fillna(0.0)
        w = w + share.mul(excess, axis=0)

    return w.shift(1).fillna(0.0)


def build(
    sleeves: pd.DataFrame,
    rf_daily: pd.Series,
    target_vol: float = 0.06,
    dd_budget: float = 0.10,
    cppi_mult: float = 3.0,
    hwm_window: int = 252,
    min_mult: float = 0.15,
    max_exposure: float = 1.0,
    stress_gap: dict[str, float] | None = None,
    vol_lookback: int = 60,
    weight_lookback: int = 60,
    weight_cap: float = 0.60,
    band: float = 0.10,
    cost: float = COST,
    name: str = "LRS-Sentinel",
) -> tuple[pd.Series, pd.DataFrame]:
    """Net daily returns of the drawdown-targeted book, plus diagnostics.

    `sleeves` holds one net daily return series per trend sleeve (each already
    defaulting to T-bills when its own trend is off). Returns
    ``(net_returns, diagnostics)`` where diagnostics carries the realised
    exposure, drawdown and sleeve weights for inspection.
    """
    idx = sleeves.dropna(how="all").index
    sl = sleeves.reindex(idx).fillna(0.0)
    rf = rf_daily.reindex(idx).ffill().bfill().to_numpy()

    w = inverse_vol_weights(sl, weight_lookback, weight_cap).reindex(idx).fillna(0.0)
    book = (sl * w).sum(axis=1)

    # Volatility target, from trailing book vol known at the prior close.
    book_vol = book.rolling(vol_lookback).std() * np.sqrt(TRADING_DAYS)
    vol_mult = (target_vol / book_vol.replace(0.0, np.nan)).shift(1)
    vol_mult = vol_mult.clip(upper=max_exposure).fillna(0.0).to_numpy()

    sl_arr = sl.to_numpy()
    w_arr = w.to_numpy()
    n, k = sl_arr.shape

    # Worst-case one-day loss assumed for each sleeve. The leveraged-equity
    # default is the 1987-10-19 experience (index -20.5%, so ~-61% on a 3x
    # fund); unnamed sleeves get a conservative generic gap.
    gaps = dict(DEFAULT_STRESS_GAP if stress_gap is None else stress_gap)
    stress = np.array([gaps.get(c, GENERIC_STRESS_GAP) for c in sl.columns])
    book_stress = w_arr @ stress  # stress loss of the book at unit exposure

    wealth = np.empty(n)
    exposure = np.empty(n)
    dd_series = np.empty(n)
    held = np.zeros(k)  # effective weights actually held (post-band)

    W = 1.0
    hist = np.empty(n)  # wealth history for the rolling high-water mark
    dq: deque[int] = deque()  # monotonic deque -> O(n) trailing max
    floor_dd = 0.0

    for i in range(n):
        # --- size from information through i-1 -------------------------------
        room = max(0.0, dd_budget + floor_dd)  # budget left before the floor
        cushion = room / dd_budget if dd_budget > 0 else 1.0
        dd_mult = float(np.clip(cppi_mult * cushion, min_mult, 1.0))

        # Stress cap: an overnight gap of `book_stress` must still fit in the
        # remaining budget. This binds where the governor cannot.
        gap_cap = room / book_stress[i] if book_stress[i] > 0 else max_exposure

        target_e = float(
            np.clip(min(vol_mult[i] * dd_mult, gap_cap), 0.0, max_exposure)
        )

        want = target_e * w_arr[i]
        traded = np.abs(want - held).sum()
        if traded > band:  # band rebalance keeps turnover investable
            held = want
        else:
            traded = 0.0

        e = held.sum()
        r = float(held @ sl_arr[i]) + (1.0 - e) * rf[i] - traded * cost

        # --- realise the day -------------------------------------------------
        W *= 1.0 + r
        hist[i] = W
        while dq and hist[dq[-1]] <= W:
            dq.pop()
        dq.append(i)
        if dq[0] <= i - hwm_window:
            dq.popleft()
        hwm = hist[dq[0]]
        floor_dd = W / hwm - 1.0  # <= 0; feeds the NEXT day's sizing

        wealth[i] = W
        exposure[i] = e
        dd_series[i] = floor_dd

    ret = pd.Series(wealth, index=idx).pct_change()
    ret.iloc[0] = wealth[0] - 1.0
    ret.name = name

    diag = pd.DataFrame(
        {"exposure": exposure, "rolling_dd": dd_series, "book": book.to_numpy()},
        index=idx,
    ).join(w.add_prefix("w_"))
    return ret, diag


def turnover_per_year(diag: pd.DataFrame) -> float:
    """Round-trip turnover implied by the realised exposure path."""
    ex = diag["exposure"]
    years = (ex.index[-1] - ex.index[0]).days / 365.25
    return float(ex.diff().abs().sum() / years)
