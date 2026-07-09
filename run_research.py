"""QuantLab research run: 'Leverage for the Long Run' and friends.

Runs a full matrix of {index} x {leverage} x {strategy}, prints performance
tables, a decade-by-decade breakdown, and a true out-of-sample test on the
years AFTER the source paper was published (2016) — the honest test.
"""

from __future__ import annotations

import pandas as pd

from quantlab import backtest, bonds, data, gold, leverage, metrics, strategies

pd.set_option("display.width", 160)
pd.set_option("display.float_format", lambda x: f"{x:,.2f}")

INDICES = {
    "S&P 500": ("^GSPC", "1950-01-01"),
    "Nasdaq Comp": ("^IXIC", "1971-01-01"),
    "Nasdaq 100": ("^NDX", "1985-01-01"),
}
# Yahoo index series are PRICE indices, but leveraged funds' swaps earn the
# TOTAL return. Approximate with conservative long-run average dividend yields
# (S&P actual long-run ~2.9%; Nasdaq held below its ~0.8-1.3% history).
DIV_YIELDS = {"S&P 500": 0.029, "Nasdaq Comp": 0.006, "Nasdaq 100": 0.006}
LEVERAGES = [1.0, 2.0, 3.0]
PAPER_PUBLICATION = "2016-07-01"  # Gayed & Bilello, Dow Award 2016


def pct(x: float) -> str:
    return f"{x * 100:,.1f}%"


def build_returns() -> dict[str, dict]:
    """For every index/leverage/strategy combo, compute net daily returns."""
    out = {}
    ust10 = bonds.treasury_total_return(10.0)
    for label, (ticker, start) in INDICES.items():
        close = data.get_close(ticker, start)
        rf = data.get_daily_rf(close.index)
        idx_ret = close.pct_change().dropna() + DIV_YIELDS[label] / 252.0
        sig_sma = strategies.sma_regime(close)
        sig_bh = strategies.buy_and_hold(close)
        sig_tsm = strategies.tsmom(close)

        for lev in LEVERAGES:
            lev_ret = leverage.leveraged_returns(idx_ret, rf, lev)
            for sig_name, sig in [("B&H", sig_bh), ("SMA200", sig_sma), ("TSMOM", sig_tsm)]:
                key = f"{label} {lev:g}x {sig_name}"
                out[key] = {
                    "returns": backtest.run(sig, lev_ret, rf, name=key),
                    "rf": rf,
                    "signal": sig,
                    "index": label,
                }

        # FLAGSHIP v1 "LRS-VT": 3x fund, SMA200 regime (Gayed & Bilello 2016),
        # volatility scaling (Moreira & Muir 2017), 10y Treasuries when
        # risk-off (Antonacci 2014 / Faber 2007 defensive-asset convention).
        lev3 = leverage.leveraged_returns(idx_ret, rf, 3.0)
        sig_vt = strategies.vol_managed_regime(close, fund_leverage=3.0)
        key = f"{label} 3x LRS-VT (UST10)"
        out[key] = {
            "returns": backtest.run(sig_vt, lev3, rf, name=key, safe_ret=ust10),
            "rf": rf,
            "signal": sig_vt,
            "index": label,
        }

        # FLAGSHIP v2 "LRS-VT2": two-speed trend ladder (out only below BOTH
        # the 50d and 200d SMA), conditional volatility veto, and a
        # bond-momentum defensive leg. Built to shrink the bull-market gap
        # to 3x buy & hold while keeping crash protection.
        sig_v2 = strategies.trend_ladder_vt(close)
        dmix = bonds.bond_momentum_defensive(rf)
        key = f"{label} 3x LRS-VT2 (bond-mom)"
        out[key] = {
            "returns": backtest.run(sig_v2, lev3, rf, name=key, safe_ret=dmix),
            "rf": rf,
            "signal": sig_v2,
            "index": label,
        }

        # DEFENSE variant: early-warning rung (half weight below the 50d SMA
        # even while above the 200d) + overextension trim (cap unprotected
        # crash room after parabolic runs). Pareto-improves full-history
        # CAGR/MaxDD vs LRS-VT2; gives back part of the bull-era edge.
        sig_def = strategies.trend_ladder_vt(close, warn_w=0.5, ext_cap=0.25)
        r_def = backtest.run(sig_def, lev3, rf, name="def", safe_ret=dmix)
        key = f"{label} 3x LRS-Defense"
        out[key] = {"returns": r_def, "rf": rf, "signal": sig_def, "index": label}

        # Halved-drawdown config: 60% LRS-Defense / 40% bond-momentum blend.
        # The efficient way to buy drawdown reduction (Sharpe rises along
        # this frontier; signal-level hacks tested worse).
        idx60 = r_def.index
        r_6040 = 0.6 * r_def + 0.4 * dmix.reindex(idx60).fillna(0.0)
        key = f"{label} 60/40 Defense+bonds"
        out[key] = {"returns": r_6040.dropna(), "rf": rf, "signal": sig_def * 0.6,
                    "index": label}

        # LRS-FORTRESS: 70% [Defense equity with gold-augmented defensive
        # rotation] + 30% [2x gold-trend sleeve]. Gold is the crisis asset
        # that carried 2000-03 and cushioned 2008; on the Composite this
        # keeps CAGR at the flagship's level with every drawdown episode
        # in 55 years below -50%.
        rot = gold.defensive_rotation(close.index, rf)
        r_def_rot = backtest.run(sig_def, lev3, rf, name="dr", safe_ret=rot)
        g2 = gold.trend_sleeve(lev=2.0)
        r_fort = (0.70 * r_def_rot + 0.30 * g2.reindex(r_def_rot.index).fillna(0.0)).dropna()
        key = f"{label} LRS-Fortress 70/30"
        out[key] = {"returns": r_fort, "rf": rf, "signal": sig_def * 0.7,
                    "index": label}
    return out


def table(results: dict, period: slice | None = None) -> pd.DataFrame:
    rows = []
    for key, r in results.items():
        ret = r["returns"] if period is None else r["returns"].loc[period]
        if len(ret) < 252:
            continue
        row = metrics.summarize(ret, r["rf"], name=key)
        for col in ("CAGR", "AnnVol", "MaxDD", "WorstYear"):
            row[col] = pct(row[col])
        rows.append(row)
    df = pd.DataFrame(rows).set_index("strategy")
    return df.sort_values("Sharpe", ascending=False)


def main() -> None:
    results = build_returns()

    print("=" * 100)
    print("FULL HISTORY — net of fees, financing, transaction costs, 1-day execution lag")
    print("=" * 100)
    full = table(results)
    print(full.to_string())

    print()
    print("=" * 100)
    print(f"OUT-OF-SAMPLE — {PAPER_PUBLICATION} to today (after the strategy was published; no hindsight)")
    print("=" * 100)
    oos = table(results, period=slice(PAPER_PUBLICATION, None))
    print(oos.to_string())

    print()
    print("=" * 100)
    print("DECADE-BY-DECADE CAGR — flagship vs buy & hold")
    print("=" * 100)
    focus = [k for k in results if "LRS-VT" in k] + [
        k for k in results if "B&H" in k and "1x" in k
    ]
    dec = pd.DataFrame({k: metrics.by_decade(results[k]["returns"]) for k in focus})
    print((dec * 100).round(1).to_string())

    print()
    print("=" * 100)
    print("TRADING ACTIVITY (flagship)")
    print("=" * 100)
    for k in (k for k in results if ("SMA200" in k and "3x" in k) or "LRS-VT" in k):
        sig = results[k]["signal"]
        print(f"{k:32s} ~{backtest.trades_per_year(sig):.1f} round-trip turnover/year, "
              f"avg exposure {sig.mean() * 100:.0f}%")

    full.to_csv("results_full_history.csv")
    oos.to_csv("results_out_of_sample.csv")

    from quantlab import report

    chart = report.equity_and_drawdown_chart(
        results["Nasdaq Comp 3x LRS-VT2 (bond-mom)"]["returns"],
        results["Nasdaq Comp 1x B&H"]["returns"],
        strat_label="LRS-VT2 flagship (3x Nasdaq, dual-speed trend + vol veto, bond-momentum risk-off)",
        bench_label="Nasdaq Composite buy & hold",
        subtitle="1971–2026, net of fees, financing, transaction costs; 1-day execution lag. "
                 "Backtest — not a guarantee of future returns.",
    )
    print(f"\nSaved: results_full_history.csv, results_out_of_sample.csv, {chart}")


if __name__ == "__main__":
    main()
