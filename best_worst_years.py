"""Top 10 best and worst years for each market's winning strategy.

For each asset we run the strategy that won the head-to-head comparison
(Defense on 3x Nasdaq-100, classic SMA200 on 2x gold, Defense on Nifty 50),
compute calendar-year returns, and print the 10 best and 10 worst years with
buy & hold alongside — so every number has its context.

    python3 best_worst_years.py
"""

from __future__ import annotations

import pandas as pd

from quantlab import backtest, bonds, data, india, leverage, strategies

pd.set_option("display.float_format", lambda x: f"{x:,.1f}")


def yearly(returns: pd.Series) -> pd.Series:
    y = (1.0 + returns).groupby(returns.index.year).prod() - 1.0
    return y * 100.0


def show(strat: pd.Series, bh: pd.Series, title: str) -> None:
    df = pd.DataFrame({"strategy %": yearly(strat), "buy&hold %": yearly(bh)})
    df["edge %"] = df["strategy %"] - df["buy&hold %"]
    last = strat.index[-1]
    if last.month < 12:
        df = df.rename(index={last.year: f"{last.year}*"})  # partial year

    print(f"\n{'=' * 64}\n{title}\n{'=' * 64}")
    print("\nTOP 10 BEST YEARS (by strategy return)")
    print(df.sort_values("strategy %", ascending=False).head(10).to_string())
    print("\nTOP 10 WORST YEARS (by strategy return)")
    print(df.sort_values("strategy %").head(10).to_string())


def main() -> None:
    # 1. TQQQ (3x Nasdaq-100), Defense signal, bond-momentum parking
    ndx = data.get_close("^NDX", "1985-01-01")
    rf = data.get_daily_rf(ndx.index)
    lev3 = leverage.leveraged_returns(ndx.pct_change().dropna() + 0.006 / 252, rf, 3.0)
    dmix = bonds.bond_momentum_defensive(rf)
    sig = strategies.trend_ladder_vt(ndx, warn_w=0.5, ext_cap=0.25)
    strat = backtest.run(sig, lev3, rf, name="def", safe_ret=dmix)
    bh = backtest.run(strategies.buy_and_hold(ndx), lev3, rf, name="bh")
    show(strat, bh, "TQQQ / 3x Nasdaq-100 — LRS-Defense (1985-2026)")

    # 2. Gold 2x, classic SMA200 signal, T-bill parking
    gc = data.get_close("GC=F", "2000-01-01")
    rf_g = data.get_daily_rf(gc.index)
    g2 = leverage.leveraged_returns(gc.pct_change().dropna(), rf_g, 2.0)
    sig_g = strategies.sma_regime(gc)
    strat_g = backtest.run(sig_g, g2, rf_g, name="sma")
    bh_g = backtest.run(strategies.buy_and_hold(gc), g2, rf_g, name="bh")
    show(strat_g, bh_g, "GOLD 2x (UGL) — classic SMA200 trend (2000-2026)")

    # 3. Nifty 50 (1x), Defense signal, liquid fund parking
    nifty = data.get_close("^NSEI", "2007-09-17")
    rf_in = india.rf_daily_india(nifty.index)
    ret_in = nifty.pct_change().dropna() + 0.012 / 252
    sig_in = strategies.trend_ladder_vt(nifty, warn_w=0.5, ext_cap=0.25)
    strat_in = backtest.run(sig_in, ret_in, rf_in, name="def")
    bh_in = backtest.run(strategies.buy_and_hold(nifty), ret_in, rf_in, name="bh")
    show(strat_in, bh_in, "NIFTY 50 (1x) — LRS-Defense (2007-2026)")

    print("\n* partial year (through the latest data date)")


if __name__ == "__main__":
    main()
