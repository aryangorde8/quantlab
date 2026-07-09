"""NSE index cross-sectional research run.

    python run_nifty500.py [nifty500|niftymidcap150]     (default: nifty500)

For every constituent: buy & hold vs the 200-day SMA trend filter (1x,
long-only — no leveraged funds exist for individual Indian stocks), idle cash
earning the Indian T-bill yield. Results are ranked, saved to CSV, and a local
Ollama 7B model (qwen2.5:7b) writes the research commentary.
"""

from __future__ import annotations

import sys

import pandas as pd

from quantlab import backtest, india, metrics, ollama_analyst, strategies

MIN_YEARS = 5.0
TOP_N_NOTES = 10


def evaluate_stock(close: pd.Series, rf: pd.Series) -> dict | None:
    close = close.dropna()
    years = (close.index[-1] - close.index[0]).days / 365.25
    if years < MIN_YEARS or len(close) < 300:
        return None
    ret = close.pct_change().dropna()

    bh = backtest.run(strategies.buy_and_hold(close), ret, rf, name="bh")
    sma = backtest.run(strategies.sma_regime(close), ret, rf, name="sma")

    return {
        "years": years,
        "bh_cagr": metrics.cagr(bh),
        "bh_sharpe": metrics.sharpe(bh, rf),
        "bh_maxdd": metrics.max_drawdown(bh),
        "sma_cagr": metrics.cagr(sma),
        "sma_sharpe": metrics.sharpe(sma, rf),
        "sma_maxdd": metrics.max_drawdown(sma),
    }


def main() -> None:
    name = sys.argv[1] if len(sys.argv) > 1 else "nifty500"
    label = india.UNIVERSES[name][1]
    uni = india.universe(name).set_index("yahoo")
    print(f"Universe: {label}, {len(uni)} stocks. Downloading prices (cached after first run)...")
    closes = india.download_closes(name)
    print(f"Got usable price history for {closes.shape[1]} stocks, "
          f"{closes.index[0].date()} to {closes.index[-1].date()}")

    rf = india.rf_daily_india(closes.index)
    rows = []
    for ticker in closes.columns:
        if ticker not in uni.index:
            continue
        res = evaluate_stock(closes[ticker], rf)
        if res is None:
            continue
        res.update(uni.loc[ticker][["Company Name", "Industry", "Symbol"]].to_dict())
        rows.append(res)

    df = pd.DataFrame(rows).set_index("Symbol")
    df = df.sort_values("sma_sharpe", ascending=False)
    results_csv = f"results_{name}.csv"
    df.to_csv(results_csv)
    print(f"\nBacktested {len(df)} stocks (>= {MIN_YEARS:.0f}y history). "
          f"Saved {results_csv}")

    agg = {
        "stocks tested": len(df),
        "median B&H CAGR": f"{df.bh_cagr.median():.1%}",
        "median SMA200 CAGR": f"{df.sma_cagr.median():.1%}",
        "median B&H max drawdown": f"{df.bh_maxdd.median():.1%}",
        "median SMA200 max drawdown": f"{df.sma_maxdd.median():.1%}",
        "% stocks where SMA200 improved Sharpe": f"{(df.sma_sharpe > df.bh_sharpe).mean():.0%}",
        "% stocks where SMA200 cut drawdown": f"{(df.sma_maxdd > df.bh_maxdd).mean():.0%}",
        "% stocks with SMA200 CAGR >= 24%": f"{(df.sma_cagr >= 0.24).mean():.0%}",
        "stocks with SMA200 CAGR >= 24%": int((df.sma_cagr >= 0.24).sum()),
    }
    agg_text = "\n".join(f"- {k}: {v}" for k, v in agg.items())
    print("\nAGGREGATE\n" + agg_text)

    show = ["Company Name", "Industry", "years", "sma_cagr", "sma_sharpe",
            "sma_maxdd", "bh_cagr", "bh_sharpe", "bh_maxdd"]
    top = df.head(TOP_N_NOTES)
    print(f"\nTOP {TOP_N_NOTES} BY STRATEGY SHARPE")
    with pd.option_context("display.float_format", lambda x: f"{x:.2f}"):
        print(top[show].to_string())

    print(f"\nGenerating commentary with local Ollama ({ollama_analyst.MODEL})...")
    summary = ollama_analyst.market_summary(f"Universe: {label}\n{agg_text}")
    notes = []
    for sym, row in top.iterrows():
        note = ollama_analyst.stock_note({**row.to_dict(), "Symbol": sym})
        notes.append((sym, row["Company Name"], note))
        print(f"  note written: {sym}")

    report_md = f"{name.upper()}_REPORT.md"
    with open(report_md, "w") as f:
        f.write(f"# {label} — systematic trend-filter research\n\n")
        f.write(f"*Universe: NSE {label} constituents; {len(df)} stocks with "
                f">= {MIN_YEARS:.0f} years of history backtested. Strategy: long "
                "when price > 200-day SMA, else cash at 6.5%. 10 bps costs, "
                "1-day execution lag. Data: Yahoo Finance, dividend-adjusted.*\n\n")
        f.write("## Aggregate results\n\n" + agg_text + "\n\n")
        f.write("## Market summary (AI-generated, qwen2.5:7b via Ollama)\n\n")
        f.write(summary + "\n\n")
        f.write(f"## Top {TOP_N_NOTES} stocks by strategy Sharpe "
                "(notes AI-generated, qwen2.5:7b)\n\n")
        for sym, name, note in notes:
            r = top.loc[sym]
            f.write(f"### {name} ({sym})\n\n")
            f.write(f"SMA200: CAGR {r.sma_cagr:.1%}, Sharpe {r.sma_sharpe:.2f}, "
                    f"MaxDD {r.sma_maxdd:.1%} | B&H: CAGR {r.bh_cagr:.1%}, "
                    f"Sharpe {r.bh_sharpe:.2f}, MaxDD {r.bh_maxdd:.1%}\n\n")
            f.write(note + "\n\n")
        f.write("---\n\n*Caveats: survivorship bias (today's constituents), "
                "no taxes, INR cash yield approximated at a constant 6.5%. "
                "Backtests do not guarantee future returns. Not investment "
                "advice.*\n")
    print(f"\nSaved {report_md}")


if __name__ == "__main__":
    main()
