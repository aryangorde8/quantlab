"""Performance and risk metrics computed from daily return series."""

from __future__ import annotations

import numpy as np
import pandas as pd

TRADING_DAYS = 252


def equity_curve(returns: pd.Series, start_value: float = 1.0) -> pd.Series:
    return start_value * (1.0 + returns).cumprod()


def cagr(returns: pd.Series) -> float:
    curve = equity_curve(returns)
    years = (curve.index[-1] - curve.index[0]).days / 365.25
    if years <= 0:
        return np.nan
    return float(curve.iloc[-1] ** (1.0 / years) - 1.0)


def ann_vol(returns: pd.Series) -> float:
    return float(returns.std() * np.sqrt(TRADING_DAYS))


def sharpe(returns: pd.Series, rf_daily: pd.Series | None = None) -> float:
    excess = returns if rf_daily is None else returns - rf_daily.reindex(returns.index).ffill()
    sd = excess.std()
    if sd == 0:
        return np.nan
    return float(excess.mean() / sd * np.sqrt(TRADING_DAYS))


def sortino(returns: pd.Series, rf_daily: pd.Series | None = None) -> float:
    excess = returns if rf_daily is None else returns - rf_daily.reindex(returns.index).ffill()
    downside = excess[excess < 0].std()
    if downside == 0 or np.isnan(downside):
        return np.nan
    return float(excess.mean() / downside * np.sqrt(TRADING_DAYS))


def max_drawdown(returns: pd.Series) -> float:
    curve = equity_curve(returns)
    return float((curve / curve.cummax() - 1.0).min())


def worst_year(returns: pd.Series) -> float:
    yearly = (1.0 + returns).groupby(returns.index.year).prod() - 1.0
    return float(yearly.min())


def summarize(returns: pd.Series, rf_daily: pd.Series | None = None, name: str = "") -> dict:
    curve = equity_curve(returns)
    return {
        "strategy": name or returns.name,
        "start": returns.index[0].date().isoformat(),
        "end": returns.index[-1].date().isoformat(),
        "CAGR": cagr(returns),
        "AnnVol": ann_vol(returns),
        "Sharpe": sharpe(returns, rf_daily),
        "Sortino": sortino(returns, rf_daily),
        "MaxDD": max_drawdown(returns),
        "WorstYear": worst_year(returns),
        "Growth of $1": float(curve.iloc[-1]),
    }


def by_decade(returns: pd.Series) -> pd.Series:
    """CAGR per decade."""
    decade = (returns.index.year // 10) * 10
    out = {}
    for d, grp in returns.groupby(decade):
        out[f"{d}s"] = cagr(grp)
    return pd.Series(out, name="CAGR")
