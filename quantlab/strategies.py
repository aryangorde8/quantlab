"""Trading signals from published research.

Every signal is computed from information available at the close of day t and
returns a position series already shifted so that position[t] is what you hold
DURING day t (i.e. decided at the prior close). This removes look-ahead bias.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def sma_regime(close: pd.Series, window: int = 200) -> pd.Series:
    """Gayed & Bilello (2016) 'Leverage for the Long Run' regime filter.

    Risk-on (1) when the index closes above its `window`-day simple moving
    average, risk-off (0) otherwise. The paper's key finding: above the
    200-day SMA, volatility is lower and streaks are longer — exactly the
    environment where daily-reset leverage compounds well instead of decaying.
    """
    sma = close.rolling(window).mean()
    signal = (close > sma).astype(float)
    return signal.shift(1).fillna(0.0)


def tsmom(close: pd.Series, lookback_months: int = 12) -> pd.Series:
    """Moskowitz, Ooi & Pedersen (2012) time-series momentum.

    Risk-on when the trailing `lookback_months` total return is positive.
    Evaluated daily on month-end data, applied with a one-day lag.
    """
    monthly = close.resample("ME").last()
    mom = monthly.pct_change(lookback_months) > 0
    signal = mom.astype(float).reindex(close.index, method="ffill")
    return signal.shift(1).fillna(0.0)


def buy_and_hold(close: pd.Series) -> pd.Series:
    return pd.Series(1.0, index=close.index)


def vol_managed_regime(
    close: pd.Series,
    window: int = 200,
    fund_leverage: float = 3.0,
    target_vol: float | None = None,
    vol_lookback: int = 20,
) -> pd.Series:
    """SMA regime filter + volatility targeting (Moreira & Muir 2017, JF).

    Inside a risk-on regime, the weight in the leveraged fund is scaled down
    whenever recent realized volatility exceeds its own long-run level:

        w = min(1, sigma_longrun / sigma_recent)

    with sigma_longrun measured on an expanding window (point-in-time — no
    look-ahead, no fitted parameter). Pass an explicit `target_vol` (fund
    vol, e.g. 0.40) for the fixed-target variant:

        w = min(1, target_vol / (fund_leverage * sigma_recent))

    De-levering into vol spikes is the published mechanism that avoids the
    crashes (1987, 2020) that strike while price is still above its SMA.
    """
    sma = close.rolling(window).mean()
    regime = (close > sma).astype(float)

    idx_ret = close.pct_change()
    realized = idx_ret.rolling(vol_lookback).std() * (252.0 ** 0.5)
    if target_vol is None:
        longrun = idx_ret.expanding(2 * 252).std() * (252.0 ** 0.5)
        weight = (longrun / realized).clip(upper=1.0)
    else:
        weight = (target_vol / (fund_leverage * realized)).clip(upper=1.0)

    return (regime * weight).shift(1).fillna(0.0)


def trend_ladder_vt(
    close: pd.Series,
    fast: int = 50,
    slow: int = 200,
    veto_k: float = 1.25,
    vol_lookback: int = 20,
    warn_w: float = 1.0,
    ext_cap: float | None = None,
) -> pd.Series:
    """LRS-VT2: two-speed trend ladder with a conditional volatility veto.

    Risk-on (full weight) while price is above EITHER the slow (200d) or the
    fast (50d) SMA; risk-off only below both. The fast line restores exposure
    quickly after V-shaped rebounds (2019, 2020, 2023) that a lone 200d line
    re-enters weeks late — at 3x leverage those first weeks dominate the gap
    to buy & hold. Multi-speed trend ensembles are standard in the trend
    literature.

    The volatility veto scales weight by sigma_longrun / sigma_recent, but
    only once recent vol exceeds `veto_k` times its long-run level —
    conditional vol management (cf. Cederburg et al. 2020) that leaves
    ordinary bull-market volatility untrimmed and still de-levers into
    1987/2020-style vol explosions.

    Defense options (both off by default — v2 behavior unchanged):
    - `warn_w`: weight while above the slow SMA but below the fast one — the
      breakdown-warning zone where 1987/2020-style crashes begin. 0.5 exits
      half the position days-to-weeks before the slow line breaks.
    - `ext_cap`: overextension trim, weight *= min(1, ext_cap / extension)
      where extension = close/SMA_slow - 1. After parabolic runs (2000: price
      50%+ above its SMA) the exit line is too far below to protect; this
      caps that unprotected crash room.
    The flagship "LRS-Defense" config is warn_w=0.5, ext_cap=0.25.
    """
    sma_f = close.rolling(fast).mean()
    sma_s = close.rolling(slow).mean()
    above_s = close > sma_s
    above_f = close > sma_f
    regime = pd.Series(
        np.where(above_s, np.where(above_f, 1.0, warn_w),
                 np.where(above_f, 1.0, 0.0)),
        index=close.index,
    )
    regime[sma_s.isna()] = 0.0  # wait for full slow-SMA history

    idx_ret = close.pct_change()
    vol = idx_ret.rolling(vol_lookback).std() * (252.0 ** 0.5)
    longrun = idx_ret.expanding(2 * 252).std() * (252.0 ** 0.5)
    weight = pd.Series(
        np.where(vol <= veto_k * longrun, 1.0, longrun / vol), index=close.index
    ).clip(upper=1.0)

    if ext_cap is not None:
        extension = (close / sma_s - 1.0).clip(lower=1e-9)
        weight = weight * (ext_cap / extension).clip(upper=1.0).fillna(1.0)

    return (regime * weight).shift(1).fillna(0.0)
