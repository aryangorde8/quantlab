"""Portfolio projection: 40 years, milestone crossings, 5-year snapshots."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np

START_USD = 10_000
CAGR = 0.19          # post-tax USD (LRS-VT2 estimate)
DEP = 0.03           # INR depreciation per year
USDINR = 83.0
GROWTH = 0.08        # contribution growth per year
YEARS = 40
Y0 = 2026

def path(monthly0):
    wealth, monthly = START_USD, monthly0
    out = [START_USD * USDINR / 1e7]
    for yr in range(1, YEARS + 1):
        wealth = wealth * (1 + CAGR) + monthly * 12
        monthly *= (1 + GROWTH)
        out.append(wealth * USDINR * (1 + DEP) ** yr / 1e7)
    return np.array(out)

SURFACE, INK, INK2, MUTED = "#fcfcfb", "#0b0b0b", "#52514e", "#898781"
GRID, BASELINE = "#e1e0d9", "#c3c2b7"
SERIES = ["#2a78d6", "#1baf7a", "#eda100", "#008300"]
LEVELS = [500, 1000, 1500, 2000]
MILESTONES = [1, 5, 10, 20, 50, 100]

years = np.arange(Y0, Y0 + YEARS + 1)
paths = {lvl: path(lvl) for lvl in LEVELS}

def fmt_cr(v):
    if v < 1:
        return f"{v*100:.0f}L"
    if v < 100:
        return f"{v:,.1f}cr"
    return f"{v:,.0f}cr"

fig = plt.figure(figsize=(11.5, 11.5), facecolor=SURFACE, constrained_layout=True)
gs = fig.add_gridspec(3, 1, height_ratios=[2.6, 1.0, 1.0])
ax = fig.add_subplot(gs[0])
axA = fig.add_subplot(gs[1]); axA.axis("off")
axB = fig.add_subplot(gs[2]); axB.axis("off")

ax.set_facecolor(SURFACE)
for side in ("top", "right"):
    ax.spines[side].set_visible(False)
for side in ("left", "bottom"):
    ax.spines[side].set_color(BASELINE)
ax.tick_params(colors=MUTED, labelsize=9)
ax.set_axisbelow(True)

for m in MILESTONES:
    ax.axhline(m, color=GRID if m < 100 else MUTED, linewidth=0.75,
               linestyle="-" if m < 100 else (0, (4, 4)))
ax.annotate("₹100 crore goal", xy=(years[1], 100), xytext=(0, 5),
            textcoords="offset points", color=MUTED, fontsize=9)

for lvl, color in zip(LEVELS, SERIES):
    w = paths[lvl]
    ax.plot(years, w, color=color, linewidth=2, label=f"${lvl:,}/mo")
    ax.annotate(f"₹{w[-1]:,.0f}cr", xy=(years[-1], w[-1]), xytext=(6, 0),
                textcoords="offset points", color=color, fontsize=10,
                fontweight="bold", va="center")
    cross = np.argmax(w >= 100)
    ax.plot(years[cross], w[cross], "o", color=color, markersize=6,
            markeredgecolor=SURFACE, markeredgewidth=1.5)

ax.set_yscale("log")
ax.set_yticks([0.1, 1, 5, 10, 20, 50, 100, 500, 2000, 10000])
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: "₹" + fmt_cr(v)))
ax.yaxis.set_minor_locator(mticker.NullLocator())
ax.set_title("Your portfolio: 40-year projection by monthly contribution",
             color=INK, fontsize=14, fontweight="bold", loc="left", pad=16)
ax.text(0, 1.012, "Start $10k · 19% post-tax USD CAGR (LRS-VT2 estimate) · contributions +8%/yr · "
        "+3%/yr INR depreciation · dots mark ₹100cr — projection, not a promise",
        transform=ax.transAxes, color=INK2, fontsize=9)
ax.legend(loc="upper left", frameon=False, fontsize=9.5, labelcolor=INK2)

def styled_table(axx, title, col_labels, rows):
    axx.set_title(title, color=INK, fontsize=11, fontweight="bold", loc="left", y=0.92)
    tbl = axx.table(cellText=[r[1] for r in rows],
                    rowLabels=[r[0] for r in rows],
                    colLabels=col_labels,
                    cellLoc="center", rowLoc="center", loc="center",
                    bbox=[0.06, 0.0, 0.94, 0.78])
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(9.5)
    for (r, c), cell in tbl.get_celld().items():
        cell.set_edgecolor(GRID)
        cell.set_text_props(color=INK if r > 0 else INK2)
        cell.set_facecolor(SURFACE)
        if r == 0:
            cell.set_text_props(fontweight="bold", color=INK2)
        if c == -1 and r > 0:
            cell.set_facecolor(SERIES[r - 1] + "26")  # light tint of series hue
            cell.set_text_props(color=INK, fontweight="bold")
    return tbl

# Table A: milestone crossing years
rowsA = []
for lvl in LEVELS:
    w = paths[lvl]
    vals = []
    for m in MILESTONES:
        i = np.argmax(w >= m)
        vals.append(str(years[i]) if w[i] >= m else "—")
    rowsA.append((f"${lvl:,}/mo", vals))
styled_table(axA, "Year each milestone is reached",
             [f"₹{m}cr" for m in MILESTONES], rowsA)

# Table B: value every 5 years
marks = list(range(5, YEARS + 1, 5))
rowsB = []
for lvl in LEVELS:
    w = paths[lvl]
    rowsB.append((f"${lvl:,}/mo", ["₹" + fmt_cr(w[m]) for m in marks]))
styled_table(axB, "Portfolio value every 5 years",
             [f"{m}y ({Y0+m})" for m in marks], rowsB)

fig.savefig("portfolio_projection.png", dpi=160, facecolor=SURFACE)
print("saved")
