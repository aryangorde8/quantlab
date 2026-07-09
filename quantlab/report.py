"""Chart generation: equity curve (log scale) + drawdown, saved as PNG."""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas as pd

from . import metrics

# Reference dataviz palette (light mode, pre-validated)
SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK_2 = "#52514e"
MUTED = "#898781"
GRID = "#e1e0d9"
BASELINE = "#c3c2b7"
SERIES_1 = "#2a78d6"  # flagship: categorical slot 1 (blue)
BENCH = "#898781"     # benchmark: neutral context, not a competing series


def _style_axis(ax) -> None:
    ax.set_facecolor(SURFACE)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(BASELINE)
    ax.tick_params(colors=MUTED, labelsize=9)
    ax.grid(True, axis="y", color=GRID, linewidth=0.75)
    ax.set_axisbelow(True)


def equity_and_drawdown_chart(
    strat_ret: pd.Series,
    bench_ret: pd.Series,
    strat_label: str,
    bench_label: str,
    path: str = "chart_flagship.png",
    title: str = "Growth of $1 (log scale)",
    subtitle: str = "",
) -> str:
    strat_curve = metrics.equity_curve(strat_ret)
    bench_curve = metrics.equity_curve(bench_ret.reindex(strat_ret.index).dropna())
    strat_dd = strat_curve / strat_curve.cummax() - 1.0
    bench_dd = bench_curve / bench_curve.cummax() - 1.0

    fig, (ax1, ax2) = plt.subplots(
        2, 1, figsize=(11, 7.5), height_ratios=[2.4, 1],
        sharex=True, facecolor=SURFACE, constrained_layout=True,
    )

    ax1.plot(strat_curve.index, strat_curve, color=SERIES_1, linewidth=2, label=strat_label)
    ax1.plot(bench_curve.index, bench_curve, color=BENCH, linewidth=2, label=bench_label)
    ax1.set_yscale("log")
    _style_axis(ax1)
    ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"${v:,.0f}"))

    for curve, color in [(strat_curve, SERIES_1), (bench_curve, BENCH)]:
        ax1.annotate(
            f"${curve.iloc[-1]:,.0f}", xy=(curve.index[-1], curve.iloc[-1]),
            xytext=(6, 0), textcoords="offset points",
            color=color, fontsize=10, fontweight="bold", va="center",
        )

    ax1.set_title(title, color=INK, fontsize=14, fontweight="bold", loc="left", pad=14)
    if subtitle:
        ax1.text(0, 1.01, subtitle, transform=ax1.transAxes, color=INK_2, fontsize=9.5)
    ax1.legend(loc="upper left", frameon=False, fontsize=9.5, labelcolor=INK_2)

    ax2.fill_between(strat_dd.index, strat_dd, 0, color=SERIES_1, alpha=0.25, linewidth=0)
    ax2.plot(strat_dd.index, strat_dd, color=SERIES_1, linewidth=1.25)
    ax2.plot(bench_dd.index, bench_dd, color=BENCH, linewidth=1.25)
    _style_axis(ax2)
    ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v * 100:.0f}%"))
    ax2.set_title("Drawdown from peak", color=INK_2, fontsize=10.5, loc="left")

    fig.savefig(path, dpi=160, facecolor=SURFACE)
    plt.close(fig)
    return path
