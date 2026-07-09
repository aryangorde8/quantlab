"""Market data loading with a local CSV cache.

All prices are dividend/split adjusted (yfinance auto_adjust=True).
The risk-free rate comes from ^IRX (13-week T-bill annualized yield, %).
"""

from __future__ import annotations

import os

import pandas as pd
import yfinance as yf

CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data_cache")


def _flatten(df: pd.DataFrame) -> pd.DataFrame:
    if isinstance(df.columns, pd.MultiIndex):
        df = df.copy()
        df.columns = df.columns.get_level_values(0)
    return df


def get_prices(ticker: str, start: str = "1950-01-01", refresh: bool = False) -> pd.DataFrame:
    """Daily OHLCV for `ticker`, cached on disk so research runs are reproducible."""
    os.makedirs(CACHE_DIR, exist_ok=True)
    path = os.path.join(CACHE_DIR, f"{ticker.replace('^', '_')}.csv")
    if os.path.exists(path) and not refresh:
        df = pd.read_csv(path, index_col=0, parse_dates=True)
    else:
        df = yf.download(ticker, start=start, progress=False, auto_adjust=True)
        df = _flatten(df)
        if df.empty:
            raise RuntimeError(f"No data returned for {ticker}")
        df.to_csv(path)
    df.index = pd.to_datetime(df.index)
    return df.sort_index()


def get_close(ticker: str, start: str = "1950-01-01") -> pd.Series:
    s = get_prices(ticker, start)["Close"].dropna()
    s.name = ticker
    return s


def get_daily_rf(index: pd.DatetimeIndex) -> pd.Series:
    """Daily risk-free rate aligned to `index`.

    ^IRX starts in 1960; earlier dates (and gaps) are forward/back-filled.
    """
    irx = get_close("^IRX", "1954-01-01")
    ann = irx.reindex(index).ffill().bfill() / 100.0
    daily = (1.0 + ann) ** (1.0 / 252.0) - 1.0
    daily.name = "rf_daily"
    return daily
