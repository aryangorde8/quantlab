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
TARGET_VOLS = [0.05, 0.07, 0.09, 0.12]
DD_BUDGETS = [0.08, 0.10, 0.15, 0.20, 0.25]
CPPI_MULTS = [3.0]

# Fund leverage on the equity sleeve. This is the single biggest dial and the
# reason a first pass looked like a fixed deposit: leverage does NOT raise
# Sharpe (financing, fees and volatility decay subtract it) but it multiplies
# gap risk, and the stress cap prices gap risk. Under a drawdown budget you
# want the highest-Sharpe sleeve and then scale it — so 3x, correct for the
# growth flagship, is the wrong instrument here. Swept so the data decides.
EQUITY_LEVS = [1.0, 2.0, 3.0]

# None = assume the historical worst gap every day (safe, very costly).
# 8.0  = an 8-sigma move on trailing vol, ceilinged by that worst gap.
STRESS_SIGMAS = [8.0, None]


def pct(x: float) -> str:
    return f"{x * 100:,.1f}%"


def build_sleeves(label: str, equity_lev: float = 1.0) -> tuple[pd.DataFrame, pd.Series]:
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

    lev = leverage.leveraged_returns(idx_ret, rf, equity_lev)
    sig_def = strategies.trend_ladder_vt(close, warn_w=0.5, ext_cap=0.25)
    equity = backtest.run(sig_def, lev, rf, name=f"equity{equity_lev:g}x")

    ust = bonds.bond_momentum_defensive(rf).rename("ust10")
    gld = gold.trend_sleeve(lev=1.0).rename("gold")

    sleeves = pd.concat([equity, ust, gld], axis=1).dropna()
    return sleeves, rf.reindex(sleeves.index).ffill().bfill()


def sweep(label: str, dd_limit: float) -> tuple[pd.DataFrame, dict]:
    """Every risk setting across every equity leverage, scored on full history."""
    rows = []
    books = {}
    for lev in EQUITY_LEVS:
        sleeves, rf = build_sleeves(label, equity_lev=lev)
        books[lev] = (sleeves, rf)
        cash = metrics.cagr(rf.reindex(sleeves.index))
        for tv in TARGET_VOLS:
            for bud in DD_BUDGETS:
                for m in CPPI_MULTS:
                    for sg in STRESS_SIGMAS:
                        ret, diag = sentinel.build(
                            sleeves, rf, target_vol=tv, dd_budget=bud,
                            cppi_mult=m, stress_sigma=sg,
                        )
                        c = metrics.cagr(ret)
                        rows.append({
                            "eq_lev": lev,
                            "target_vol": tv,
                            "dd_budget": bud,
                            "stress": "8sig" if sg else "worst",
                            "CAGR": c,
                            # The only honest measure of edge: everything
                            # above the T-bill rate you could have had for free.
                            "ExcessOverCash": c - cash,
                            "MaxDD": metrics.max_drawdown(ret),
                            "AnnVol": metrics.ann_vol(ret),
                            "Sharpe": metrics.sharpe(ret, rf),
                            "WorstYear": metrics.worst_year(ret),
                            "AvgExposure": float(diag["exposure"].mean()),
                            "Turnover/yr": sentinel.turnover_per_year(diag),
                        })
    df = pd.DataFrame(rows)
    df["passes"] = df["MaxDD"] > -dd_limit  # MaxDD is negative
    return df, books


def frontier(df: pd.DataFrame) -> pd.DataFrame:
    """Best achievable CAGR at each drawdown level — the actual decision table.

    Buckets on REALISED drawdown rather than the requested budget, because
    the budget is an input and the realised number is what you have to live
    through.
    """
    edges = [0.05, 0.10, 0.15, 0.20, 0.25, 0.35, 0.50, 1.01]
    rows = []
    for lo, hi in zip([0.0] + edges[:-1], edges):
        band = df[(-df["MaxDD"] > lo) & (-df["MaxDD"] <= hi)]
        if band.empty:
            continue
        best = band.sort_values("CAGR", ascending=False).iloc[0]
        rows.append({
            "MaxDD band": f"{lo*100:.0f}-{hi*100:.0f}%",
            "best CAGR": best["CAGR"],
            "over cash": best["ExcessOverCash"],
            "realised MaxDD": best["MaxDD"],
            "Sharpe": best["Sharpe"],
            "eq_lev": f"{best['eq_lev']:g}x",
            "vol tgt": f"{best['target_vol']:.0%}",
            "budget": f"{best['dd_budget']:.0%}",
            "stress": best["stress"],
        })
    return pd.DataFrame(rows)


def naive_frontier(books: dict) -> pd.DataFrame:
    """The dumb alternative: x% in the equity sleeve, (1-x)% in T-bills. Rebalanced never.

    This is the benchmark that decides whether Sentinel is worth existing. Any
    point on a risk/return line can be reached by diluting ONE high-Sharpe
    asset with cash, so all of Sentinel's machinery — risk parity, vol target,
    CPPI governor, stress cap — only earns its keep if it beats this. If the
    static blend wins at the same drawdown, the machinery is lowering the
    book's Sharpe and should be dropped rather than tuned.
    """
    rows = []
    for lev, (sleeves, rf) in books.items():
        eq = sleeves[f"equity{lev:g}x"]
        cash = rf.reindex(eq.index).ffill()
        cash_cagr = metrics.cagr(cash)
        for w in (0.10, 0.15, 0.20, 0.25, 0.30, 0.40, 0.50, 0.70, 1.00):
            blend = w * eq + (1.0 - w) * cash
            c = metrics.cagr(blend)
            rows.append({
                "eq_lev": f"{lev:g}x",
                "equity weight": f"{w:.0%}",
                "CAGR": c,
                "over cash": c - cash_cagr,
                "MaxDD": metrics.max_drawdown(blend),
                "Sharpe": metrics.sharpe(blend, rf),
            })
    return pd.DataFrame(rows)


def main() -> None:
    label = sys.argv[1] if len(sys.argv) > 1 else "Nasdaq Comp"
    dd_limit = float(sys.argv[2]) if len(sys.argv) > 2 else DD_LIMIT
    if label not in INDICES:
        raise SystemExit(f"Unknown index {label!r}; choose from {list(INDICES)}")

    print(f"Building sleeves for {label} across {len(EQUITY_LEVS)} leverage "
          f"settings — this takes a few minutes ...")
    df, books = sweep(label, dd_limit)
    sleeves, rf = books[EQUITY_LEVS[0]]
    print(f"  {len(sleeves):,} trading days, "
          f"{sleeves.index[0].date()} -> {sleeves.index[-1].date()}\n")

    print("=" * 110)
    print("THE FRONTIER — the best CAGR available at each level of pain")
    print("=" * 110)
    print("'over cash' is the only real measure of edge: everything above the")
    print("T-bill rate you could have earned for free. If it is near zero, the")
    print("config is an expensive way to hold cash.\n")
    fr = frontier(df)
    show_fr = fr.copy()
    for col in ("best CAGR", "over cash", "realised MaxDD"):
        show_fr[col] = show_fr[col].map(pct)
    print(show_fr.to_string(index=False))
    print()

    print("=" * 110)
    print("THE VERDICT — Sentinel vs just diluting the equity sleeve with cash")
    print("=" * 110)
    print("Any risk level is reachable by mixing ONE high-Sharpe asset with cash.")
    print("Sentinel is only worth its complexity if it beats this at equal drawdown.\n")
    nf = naive_frontier(books)
    show_nf = nf.copy()
    for col in ("CAGR", "over cash", "MaxDD"):
        show_nf[col] = show_nf[col].map(pct)
    print(show_nf.to_string(index=False))

    # Head-to-head at matched drawdown: does the machinery actually add return?
    print("\n  Head-to-head at matched drawdown (best of each):")
    print(f"  {'MaxDD band':<12} {'Sentinel CAGR':>14} {'blend CAGR':>12} {'winner':>10}")
    for lo, hi in [(0.0, 0.10), (0.10, 0.20), (0.20, 0.35), (0.35, 0.60)]:
        s = df[(-df["MaxDD"] > lo) & (-df["MaxDD"] <= hi)]
        b = nf[(-nf["MaxDD"] > lo) & (-nf["MaxDD"] <= hi)]
        if s.empty or b.empty:
            continue
        sc, bc = s["CAGR"].max(), b["CAGR"].max()
        print(f"  {f'{lo*100:.0f}-{hi*100:.0f}%':<12} {pct(sc):>14} {pct(bc):>12} "
              f"{('Sentinel' if sc > bc else 'plain blend'):>10}")

    print()
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

    print("=" * 110)
    print(f"SWEEP — top settings by CAGR. 'passes' = MaxDD stayed inside {pct(dd_limit)}")
    print("=" * 110)
    show = df.sort_values("CAGR", ascending=False).head(20).copy()
    for col in ("CAGR", "ExcessOverCash", "MaxDD", "AnnVol", "WorstYear", "AvgExposure"):
        show[col] = show[col].map(pct)
    print(show.to_string(index=False))

    print()
    print("=" * 110)
    print("DOES LEVERAGE HELP? Best config at each equity leverage, inside the budget")
    print("=" * 110)
    for lev in EQUITY_LEVS:
        sub = df[(df["eq_lev"] == lev) & df["passes"]]
        if sub.empty:
            print(f"  {lev:g}x equity: nothing held inside {pct(dd_limit)}")
            continue
        b = sub.sort_values("CAGR", ascending=False).iloc[0]
        print(f"  {lev:g}x equity: CAGR {pct(b['CAGR'])}  "
              f"over cash {pct(b['ExcessOverCash'])}  MaxDD {pct(b['MaxDD'])}  "
              f"Sharpe {b['Sharpe']:.2f}  avg exposure {pct(b['AvgExposure'])}")

    ok = df[df["passes"]]
    if ok.empty:
        print(f"\nNo configuration held MaxDD inside {pct(dd_limit)} on this index.")
        print("Loosen the budget or lower target_vol further.")
        return

    best = ok.sort_values("CAGR", ascending=False).iloc[0]
    best_lev = float(best["eq_lev"])
    sleeves, rf = books[best_lev]
    eq_col = f"equity{best_lev:g}x"
    print()
    print("=" * 110)
    print(f"BEST CONFIG WITHIN THE {pct(dd_limit)} BUDGET  ->  "
          f"{best_lev:g}x equity, target_vol {best['target_vol']:.0%}, "
          f"dd_budget {best['dd_budget']:.0%}, stress {best['stress']}")
    print("=" * 110)

    ret, diag = sentinel.build(
        sleeves, rf,
        target_vol=float(best["target_vol"]),
        dd_budget=float(best["dd_budget"]),
        cppi_mult=CPPI_MULTS[0],
        stress_sigma=8.0 if best["stress"] == "8sig" else None,
    )

    oos = ret.loc[PAPER_PUBLICATION:]
    rows = [
        metrics.summarize(ret, rf, name=f"LRS-Sentinel ({label})"),
        metrics.summarize(oos, rf, name=f"LRS-Sentinel OOS {PAPER_PUBLICATION[:4]}+"),
        metrics.summarize(sleeves[eq_col], rf, name=f"Equity sleeve alone ({best_lev:g}x)"),
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
        "Equity sleeve": metrics.by_decade(sleeves[eq_col]),
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
        sleeves[eq_col],
        strat_label=f"LRS-Sentinel — drawdown-budgeted ({best['target_vol']:.0%} vol target, "
                    f"{best['dd_budget']:.0%} budget)",
        bench_label=f"Equity sleeve alone, {best_lev:g}x (the unconstrained version)",
        subtitle=f"{label}, net of fees, financing, transaction costs; 1-day execution lag. "
                 "Backtest — not a guarantee of future returns.",
        path="chart_sentinel.png",
    )
    print(f"\nSaved: results_lowdd_sweep.csv, {chart}")


if __name__ == "__main__":
    main()
