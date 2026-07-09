"""Gold as the crisis diversifier: trend sleeve + defensive rotation.

Data: LBMA monthly prices (datahub.io/core/gold-prices, cached in
data_cache/gold_monthly.csv) for the pre-futures era; COMEX front-month
futures (GC=F via Yahoo) daily from 2000.

The trend sleeve follows Faber (2007): gold when above trend, T-bills
otherwise — monthly 10-month-SMA rule pre-2001 with returns spread evenly
within each month (all flagship drawdown episodes lie in the daily era, so
the smoothing never flatters a MaxDD number), daily 200d SMA on futures
after. The 2x sleeve is implementable via UGL (ProShares Ultra Gold, listed
2008) or futures.
"""

from __future__ import annotations

import os

import numpy as np
import pandas as pd

from . import data, leverage
from .bonds import treasury_total_return
from .data import CACHE_DIR

DAILY_CUT = "2001-01-01"  # futures signal needs its 200d warmup first


def monthly_prices() -> pd.Series:
    df = pd.read_csv(os.path.join(CACHE_DIR, "gold_monthly.csv"))
    df["Date"] = pd.to_datetime(df["Date"], format="%Y-%m")
    return df.set_index("Date")["Price"]["1968":]


def daily_prices(index: pd.DatetimeIndex) -> pd.Series:
    """Gold price on `index`: monthly (ffilled) pre-2001, futures after."""
    gm = monthly_prices().resample("D").ffill()
    gc = data.get_close("GC=F", "2000-01-01")
    px = pd.concat([gm[:DAILY_CUT].iloc[:-1], gc[DAILY_CUT:]]).sort_index()
    px = px[~px.index.duplicated()]
    return px.reindex(index).ffill()


def trend_sleeve(lev: float = 1.0) -> pd.Series:
    """Daily returns: long gold when above trend, T-bills otherwise."""
    gc = data.get_close("GC=F", "2000-01-01")
    gm = monthly_prices()
    full_days = pd.bdate_range(gm.index[0], gc.index[-1])
    rf_d = data.get_daily_rf(full_days)

    # pre-2001: Faber monthly rule on LBMA data, spread evenly within month
    tb_m = (1.0 + rf_d).resample("ME").prod() - 1.0
    tb_m.index = tb_m.index.to_period("M").to_timestamp()
    sig_m = (gm > gm.rolling(10).mean()).astype(float).shift(1)
    sleeve_m = (sig_m * gm.pct_change() + (1.0 - sig_m) * tb_m.reindex(gm.index)).dropna()

    bdays = pd.bdate_range(sleeve_m.index[0], DAILY_CUT)
    pre_parts = []
    for dt, r_m in sleeve_m[:DAILY_CUT].items():
        month_days = bdays[(bdays.year == dt.year) & (bdays.month == dt.month)]
        if len(month_days) < 1 or np.isnan(r_m):
            continue
        d = (1.0 + r_m) ** (1.0 / len(month_days)) - 1.0
        pre_parts.append(pd.Series(d, index=month_days))
    pre = pd.concat(pre_parts)

    # 2001+: daily 200d SMA rule on futures
    sig_d = (gc > gc.rolling(200).mean()).astype(float).shift(1).fillna(0.0)
    post = (sig_d * gc.pct_change() + (1.0 - sig_d) * rf_d.reindex(gc.index).ffill()).dropna()

    sleeve = pd.concat([pre[:DAILY_CUT].iloc[:-1], post[DAILY_CUT:]]).sort_index()
    sleeve = sleeve[~sleeve.index.duplicated()]
    sleeve.name = f"gold_trend_{lev:g}x"
    if lev != 1.0:
        rf_full = data.get_daily_rf(sleeve.index)
        sleeve = leverage.leveraged_returns(sleeve, rf_full, lev)
        sleeve.name = f"gold_trend_{lev:g}x"
    return sleeve


def defensive_rotation(index: pd.DatetimeIndex, rf_daily: pd.Series) -> pd.Series:
    """Risk-off asset by 12m momentum: UST10 or gold, else T-bills
    (Antonacci-style absolute/relative momentum on the defensive leg)."""
    ust = treasury_total_return(10.0).reindex(index).fillna(0.0)
    gold_ret = daily_prices(index).pct_change().fillna(0.0)
    rf = rf_daily.reindex(index).ffill()

    def mom12(r: pd.Series) -> pd.Series:
        c = (1.0 + r).cumprod()
        return c / c.shift(252) - 1.0

    m_u, m_g, m_t = mom12(ust), mom12(gold_ret), mom12(rf)
    pick_gold = ((m_g > m_u) & (m_g > m_t)).shift(1).fillna(False)
    pick_ust = ((m_u >= m_g) & (m_u > m_t)).shift(1).fillna(False)
    out = pd.Series(
        np.where(pick_gold, gold_ret, np.where(pick_ust, ust, rf)), index=index
    )
    out.name = "defensive_rotation"
    return out
