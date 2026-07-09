"""Profit-harvesting overlay: sell some at new highs, reinvest after dips.

Two sleeves: the risky strategy and a defensive asset. Each time total wealth
ratchets `step` above the last harvest point, `frac` of the risky sleeve is
moved to the defensive sleeve ("sell some on the new highs"). When wealth
falls `dip` below its peak, the defensive sleeve is moved back into the
risky sleeve ("reinvest it"). Related literature: rebalancing premium;
Estep & Kritzman (1988) TIPP ratchets.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

COST = 0.0010  # 10 bps on every moved notional


def harvest_overlay(
    risky_ret: pd.Series,
    safe_ret: pd.Series,
    step: float = 0.15,
    frac: float = 0.20,
    dip: float = 0.25,
) -> pd.Series:
    """Daily returns of the harvested portfolio (starts 100% risky)."""
    idx = risky_ret.dropna().index
    r = risky_ret.loc[idx].to_numpy()
    s = safe_ret.reindex(idx).ffill().fillna(0.0).to_numpy()

    R, B = 1.0, 0.0        # risky / defensive sleeve values
    peak = last_harvest = 1.0
    out = np.empty(len(idx))

    for i in range(len(idx)):
        R *= 1.0 + r[i]
        B *= 1.0 + s[i]
        W = R + B

        if W >= last_harvest * (1.0 + step) and R > 0:      # new-high ratchet
            moved = R * frac
            R -= moved
            B += moved * (1.0 - COST)
            last_harvest = W
        elif W <= peak * (1.0 - dip) and B > 0:             # dip: reinvest
            R += B * (1.0 - COST)
            B = 0.0
            peak = W
            last_harvest = W

        peak = max(peak, W)
        out[i] = W

    wealth = pd.Series(out, index=idx)
    ret = wealth.pct_change()
    ret.iloc[0] = wealth.iloc[0] - 1.0
    ret.name = f"harvest_{step:g}_{frac:g}_{dip:g}"
    return ret


def fixed_mix(
    risky_ret: pd.Series,
    safe_ret: pd.Series,
    weight: float = 0.80,
    band: float = 0.10,
) -> pd.Series:
    """Band-rebalanced fixed mix — the classic 'sell high, buy low' discipline."""
    idx = risky_ret.dropna().index
    r = risky_ret.loc[idx].to_numpy()
    s = safe_ret.reindex(idx).ffill().fillna(0.0).to_numpy()

    R, B = weight, 1.0 - weight
    out = np.empty(len(idx))
    for i in range(len(idx)):
        R *= 1.0 + r[i]
        B *= 1.0 + s[i]
        W = R + B
        w_now = R / W
        if abs(w_now - weight) >= band:
            traded = abs(w_now - weight) * W
            R = weight * W
            B = (1.0 - weight) * W - traded * COST
        out[i] = R + B

    wealth = pd.Series(out, index=idx)
    ret = wealth.pct_change()
    ret.iloc[0] = wealth.iloc[0] - 1.0
    ret.name = f"mix_{weight:g}"
    return ret
