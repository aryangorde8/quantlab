"""LRS-Sentinel research run: most CAGR available under a hard drawdown budget.

The flagship configs maximise growth and accept -50% to -67% drawdowns. This
run inverts the objective — cap max drawdown (default: under 10%) and take the
best CAGR that cap allows — then sweeps the risk settings to find the frontier.

    python3 run_lowdd.py                 # Nasdaq Composite, 10% budget
    python3 run_lowdd.py "S&P 500" 0.08  # different index / budget

Read RESULTS WITH THE CASH CAVEAT printed at the end: a portfolio this
de-risked is structurally mostly T-bills, and T-bills paid far more in
1971-2000 than they plausibly will again.
"""

from __future__ import annotations

import sys

import pandas as pd

from quantlab import backtest, bonds, data, gold, leverage, metrics, sentinel, strategies

pd.set_option("display.width", 200)
pd.set_option("display.float_format", lambda x: f"{x:,.2f}")

INDICES = {
    "S&P 500": ("^GSPC", "1950-01-01", 0.029),
    "Nasdaq Comp": ("^IXIC", "1971-01-01", 0.006),
    "Nasdaq 100": ("^NDX", "1985-01-01", 0.006),
}
PAPER_PUBLICATION = "2016-07-01"
DD_LIMIT = 0.10

# Swept risk settings. target_vol and dd_budget are the two real dials;
# cppi_mult sets how hard the governor reacts to a drawdown in progress.
TARGET_VOLS = [0.04, 0.05, 0.06, 0.08, 0.10, 0.12]
DD_BUDGETS = [0.06, 0.08, 0.10, 0.12]
CPPI_MULTS = [2.0, 3.0, 4.0]


def pct(x: float) -> str:
    return f"{x * 100:,.1f}%"


def build_sleeves(label: str) -> tuple[pd.DataFrame, pd.Series]:
    """Three trend sleeves, each defaulting to T-bills when its own trend is off.

    Deliberately kept PURE — the equity sleeve parks in T-bills rather than in
    bonds or gold, because the bond and gold sleeves already hold that exposure
    explicitly. Letting the equity sleeve rotate into gold (as LRS-Fortress
    does) would double-count gold and corrupt the risk-parity weights.
    """
    ticker, start, div = INDICES[label]
    close = data.get_close(ticker, start)
    rf = data.get_daily_rf(close.index)
    idx_ret = close.pct_change().dropna() + div / 252.0

    lev3 = leverage.leveraged_returns(idx_ret, rf, 3.0)
    sig_def = strategies.trend_ladder_vt(close, warn_w=0.5, ext_cap=0.25)
    equity = backtest.run(sig_def, lev3, rf, name="equity3x")

    ust = bonds.bond_momentum_defensive(rf).rename("ust10")
    gld = gold.trend_sleeve(lev=1.0).rename("gold")

    sleeves = pd.concat([equity, ust, gld], axis=1).dropna()
    return sleeves, rf.reindex(sleeves.index).ffill().bfill()


def sweep(sleeves: pd.DataFrame, rf: pd.Series, dd_limit: float) -> pd.DataFrame:
    """Every risk setting, scored on full history."""
    rows = []
    for tv in TARGET_VOLS:
        for bud in DD_BUDGETS:
            for m in CPPI_MULTS:
                ret, diag = sentinel.build(
                    sleeves, rf, target_vol=tv, dd_budget=bud, cppi_mult=m
                )
                rows.append(
                    {
                        "target_vol": tv,
                        "dd_budget": bud,
                        "cppi_mult": m,
                        "CAGR": metrics.cagr(ret),
                        "MaxDD": metrics.max_drawdown(ret),
                        "AnnVol": metrics.ann_vol(ret),
                        "Sharpe": metrics.sharpe(ret, rf),
                        "WorstYear": metrics.worst_year(ret),
                        "AvgExposure": float(diag["exposure"].mean()),
                        "Turnover/yr": sentinel.turnover_per_year(diag),
                    }
                )
    df = pd.DataFrame(rows)
    df["passes"] = df["MaxDD"] > -dd_limit  # MaxDD is negative
    return df


def main() -> None:
    label = sys.argv[1] if len(sys.argv) > 1 else "Nasdaq Comp"
    dd_limit = float(sys.argv[2]) if len(sys.argv) > 2 else DD_LIMIT
    if label not in INDICES:
        raise SystemExit(f"Unknown index {label!r}; choose from {list(INDICES)}")

    print(f"Building sleeves for {label} ...")
    sleeves, rf = build_sleeves(label)
    print(f"  {len(sleeves):,} trading days, "
          f"{sleeves.index[0].date()} -> {sleeves.index[-1].date()}\n")

    print("=" * 110)
    print("SLEEVE INPUTS (each already net of costs, each parks in T-bills when its own trend is off)")
    print("=" * 110)
    for c in sleeves.columns:
        print(f"  {c:10s} CAGR {pct(metrics.cagr(sleeves[c])):>7s}   "
              f"vol {pct(metrics.ann_vol(sleeves[c])):>6s}   "
              f"MaxDD {pct(metrics.max_drawdown(sleeves[c])):>7s}   "
              f"Sharpe {metrics.sharpe(sleeves[c], rf):5.2f}")
    corr = sleeves.corr()
    print("\n  Sleeve correlation (the diversification that pays for the CAGR):")
    print(corr.round(2).to_string().replace("\n", "\n  "))

    df = sweep(sleeves, rf, dd_limit)

    print()
    print("=" * 110)
    print(f"SWEEP — every risk setting, full history. 'passes' = MaxDD stayed inside {pct(dd_limit)}")
    print("=" * 110)
    show = df.sort_values("CAGR", ascending=False).head(20).copy()
    for col in ("CAGR", "MaxDD", "AnnVol", "WorstYear", "AvgExposure"):
        show[col] = show[col].map(pct)
    print(show.to_string(index=False))

    ok = df[df["passes"]]
    if ok.empty:
        print(f"\nNo configuration held MaxDD inside {pct(dd_limit)} on this index.")
        print("Loosen the budget or lower target_vol further.")
        return

    best = ok.sort_values("CAGR", ascending=False).iloc[0]
    print()
    print("=" * 110)
    print(f"BEST CONFIG WITHIN THE {pct(dd_limit)} BUDGET  ->  "
          f"target_vol {best['target_vol']:.0%}, dd_budget {best['dd_budget']:.0%}, "
          f"cppi_mult {best['cppi_mult']:.0f}")
    print("=" * 110)

    ret, diag = sentinel.build(
        sleeves, rf,
        target_vol=float(best["target_vol"]),
        dd_budget=float(best["dd_budget"]),
        cppi_mult=float(best["cppi_mult"]),
    )

    oos = ret.loc[PAPER_PUBLICATION:]
    rows = [
        metrics.summarize(ret, rf, name=f"LRS-Sentinel ({label})"),
        metrics.summarize(oos, rf, name=f"LRS-Sentinel OOS {PAPER_PUBLICATION[:4]}+"),
        metrics.summarize(sleeves["equity3x"], rf, name="LRS-Defense equity sleeve alone"),
        metrics.summarize(rf.reindex(ret.index), rf, name="T-bills alone (the cash floor)"),
    ]
    out = pd.DataFrame(rows).set_index("strategy")
    for col in ("CAGR", "AnnVol", "MaxDD", "WorstYear"):
        out[col] = out[col].map(pct)
    print(out.to_string())

    print()
    print("=" * 110)
    print("DECADE-BY-DECADE CAGR")
    print("=" * 110)
    dec = pd.DataFrame({
        "Sentinel": metrics.by_decade(ret),
        "T-bills": metrics.by_decade(rf.reindex(ret.index)),
        "Equity sleeve": metrics.by_decade(sleeves["equity3x"]),
    })
    print((dec * 100).round(1).to_string())

    print()
    print("=" * 110)
    print("HOW IT BEHAVES")
    print("=" * 110)
    print(f"  average exposure to the risky book : {best['AvgExposure']:.1%}")
    print(f"  round-trip turnover                : {best['Turnover/yr']:.1f}/year")
    print(f"  worst rolling drawdown             : {pct(metrics.max_drawdown(ret))}")
    print(f"  days spent below -5% drawdown      : {(diag['rolling_dd'] < -0.05).mean():.1%}")

    # The caveat that matters most for this particular strategy.
    cash_cagr = metrics.cagr(rf.reindex(ret.index))
    total_cagr = metrics.cagr(ret)
    print()
    print("=" * 110)
    print("READ THIS BEFORE BELIEVING THE CAGR — the cash caveat")
    print("=" * 110)
    print(f"  T-bills alone returned {pct(cash_cagr)}/yr over this window; the strategy")
    print(f"  returned {pct(total_cagr)}/yr, so only ~{pct(total_cagr - cash_cagr)}/yr came from")
    print("  the strategy itself. A portfolio held to a sub-10% drawdown is structurally")
    print("  mostly T-bills, and T-bills paid double digits in the 1980s. Weight the")
    print(f"  {PAPER_PUBLICATION[:4]}+ out-of-sample row far more heavily than the full-history row.")

    df.to_csv("results_lowdd_sweep.csv", index=False)

    from quantlab import report

    chart = report.equity_and_drawdown_chart(
        ret,
        sleeves["equity3x"],
        strat_label=f"LRS-Sentinel — drawdown-budgeted ({best['target_vol']:.0%} vol target, "
                    f"{best['dd_budget']:.0%} budget)",
        bench_label="LRS-Defense equity sleeve (the unconstrained version)",
        subtitle=f"{label}, net of fees, financing, transaction costs; 1-day execution lag. "
                 "Backtest — not a guarantee of future returns.",
        path="chart_sentinel.png",
    )
    print(f"\nSaved: results_lowdd_sweep.csv, {chart}")


if __name__ == "__main__":
    main()
