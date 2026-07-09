"""Backtest engine: position series -> net strategy returns.

Realism features:
- positions are pre-lagged by the strategy layer (no look-ahead),
- transaction costs charged on every position change (default 10 bps per
  full switch — conservative for major ETFs whose spreads are ~1-3 bps),
- idle capital earns the T-bill rate.
"""

from __future__ import annotations

import pandas as pd

COST_PER_SWITCH = 0.0010  # 10 bps of traded notional


def run(
    position: pd.Series,
    risky_ret: pd.Series,
    rf_daily: pd.Series,
    cost_per_switch: float = COST_PER_SWITCH,
    name: str = "strategy",
    safe_ret: pd.Series | None = None,
) -> pd.Series:
    """Net daily returns of holding `risky_ret` when position==1, else the
    defensive asset (`safe_ret`, e.g. Treasuries; defaults to T-bills)."""
    idx = risky_ret.dropna().index
    pos = position.reindex(idx).fillna(0.0)
    rf = rf_daily.reindex(idx).ffill()
    safe = rf if safe_ret is None else safe_ret.reindex(idx).fillna(rf)

    gross = pos * risky_ret.loc[idx] + (1.0 - pos) * safe
    turnover = pos.diff().abs().fillna(0.0)
    net = gross - turnover * cost_per_switch
    net.name = name
    return net.dropna()


def trades_per_year(position: pd.Series) -> float:
    switches = position.diff().abs().fillna(0.0)
    years = (position.index[-1] - position.index[0]).days / 365.25
    return float(switches.sum() / years)
