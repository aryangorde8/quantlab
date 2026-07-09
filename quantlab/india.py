"""Nifty 500 universe: constituent list + bulk price download.

Universe file: NSE's official ind_nifty500list.csv (cached in data_cache/).
Yahoo Finance symbols are the NSE symbol + ".NS".

Known limitation, disclosed in the report: using TODAY'S constituent list for
a historical backtest introduces survivorship bias — stocks that fell out of
the index are missing, so aggregate historical numbers are flattered.
"""

from __future__ import annotations

import os
import time

import pandas as pd
import yfinance as yf

from .data import CACHE_DIR

# NSE index name -> (constituent file, human label)
UNIVERSES = {
    "nifty500": ("ind_nifty500list.csv", "Nifty 500"),
    "niftymidcap150": ("ind_niftymidcap150list.csv", "Nifty Midcap 150"),
}
INDIA_RF = 0.065  # long-run average Indian 91-day T-bill yield (~6.5%)


def universe(name: str = "nifty500") -> pd.DataFrame:
    df = pd.read_csv(os.path.join(CACHE_DIR, UNIVERSES[name][0]))
    df["yahoo"] = df["Symbol"].str.strip() + ".NS"
    return df[["Company Name", "Industry", "Symbol", "yahoo"]]


def download_closes(
    name: str = "nifty500",
    start: str = "2000-01-01",
    chunk: int = 100,
    refresh: bool = False,
) -> pd.DataFrame:
    """Adjusted daily closes for the whole universe, one column per stock."""
    closes_file = os.path.join(CACHE_DIR, f"{name}_close.csv")
    if os.path.exists(closes_file) and not refresh:
        return pd.read_csv(closes_file, index_col=0, parse_dates=True)

    tickers = universe(name)["yahoo"].tolist()
    frames = []

    # Reuse anything already cached for the broad Nifty 500 universe
    # (Midcap 150 is a subset of Nifty 500 by construction).
    broad_file = os.path.join(CACHE_DIR, "nifty500_close.csv")
    if name != "nifty500" and os.path.exists(broad_file):
        broad = pd.read_csv(broad_file, index_col=0, parse_dates=True)
        have = [t for t in tickers if t in broad.columns]
        if have:
            frames.append(broad[have])
            print(f"  reused {len(have)}/{len(tickers)} from Nifty 500 cache")
        tickers = [t for t in tickers if t not in broad.columns]

    for i in range(0, len(tickers), chunk):
        batch = tickers[i : i + chunk]
        px = yf.download(batch, start=start, progress=False, auto_adjust=True)["Close"]
        if isinstance(px, pd.Series):
            px = px.to_frame(batch[0])
        frames.append(px)
        print(f"  downloaded {min(i + chunk, len(tickers))}/{len(tickers)}")
        time.sleep(1.0)

    closes = pd.concat(frames, axis=1).sort_index()
    closes = closes.dropna(axis=1, how="all")
    closes.to_csv(closes_file)
    return closes


def rf_daily_india(index: pd.DatetimeIndex) -> pd.Series:
    daily = (1.0 + INDIA_RF) ** (1.0 / 252.0) - 1.0
    return pd.Series(daily, index=index, name="rf_daily_inr")
