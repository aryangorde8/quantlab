# Commands Reference

Every command in this project, what it does, and how to read its output.
Run all of them from the project folder: `cd ~/fable_project`

---

## One-time setup

```bash
pip install -r requirements.txt
```
Installs the four Python libraries the engine needs: `pandas`/`numpy` (data
math), `yfinance` (free market data from Yahoo), `matplotlib` (charts).
On Debian/Ubuntu Python you may need `pip install --user --break-system-packages -r requirements.txt`.

---

## 1. The US research engine

```bash
python3 run_research.py
```
**What it does:** downloads/loads S&P 500 (1950+), Nasdaq Composite (1971+),
Nasdaq 100 (1985+), T-bill rates, Treasury yields and gold, then backtests
every strategy combination — buy & hold, SMA200, TSMOM at 1x/2x/3x, plus the
four flagships: LRS-VT (v1), LRS-VT2, LRS-Defense, 60/40 blend, and
**LRS-Fortress 70/30** (the recommended config).

**Outputs:**
- Terminal tables — FULL HISTORY (net of all costs), OUT-OF-SAMPLE (2016+,
  the honest window), decade-by-decade CAGR, trading activity.
- `results_full_history.csv`, `results_out_of_sample.csv` — same tables for
  a spreadsheet.
- `chart_flagship.png` — flagship equity curve vs buy & hold, with drawdowns.

**How to read it:** find the `LRS-Fortress 70/30` rows. CAGR = growth rate,
MaxDD = worst peak-to-trough loss (your pain budget), Sharpe = return per
unit of risk (higher is better; 0.9+ is excellent), `Growth of $1` = what
compounding did. Compare any strategy against its same-index `1x B&H` row.

**First run** downloads everything (needs internet, ~1-2 min); afterwards
prices are cached in `data_cache/` and it runs offline.

---

## 2. The India engine

```bash
python3 run_nifty500.py                  # all Nifty 500 stocks
python3 run_nifty500.py niftymidcap150   # just the Midcap 150
```
**What it does:** backtests every constituent stock — buy & hold vs the
200-day SMA filter (1x, cash earns 6.5% when out) — ranks all stocks, then
has your **local Ollama qwen2.5:7b** write research commentary (needs
`ollama serve` running and the model pulled; the LLM only narrates numbers
the engine computed).

**Outputs:** `results_<universe>.csv` (every stock's metrics, sorted by
strategy Sharpe) and `<UNIVERSE>_REPORT.md` (aggregates + AI notes on the
top 10). The AI part takes a few minutes on CPU.

**Check Ollama first:** `ollama list` (is qwen2.5:7b there?) and
`curl -s localhost:11434/api/version` (is the server up?).

---

## 3. The low-drawdown engine (LRS-Sentinel)

```bash
python3 run_lowdd.py                 # Nasdaq Composite, 10% drawdown budget
python3 run_lowdd.py "S&P 500" 0.08  # different index / tighter budget
```
**What it does:** the opposite trade-off from `run_research.py`. Instead of
maximising growth and accepting a -50%+ drawdown, it caps max drawdown at a
budget you set and finds the most CAGR that fits inside it. Builds three
trend sleeves (3x equity on the Defense signal, UST10 momentum, gold trend),
weights them inverse-vol, then sizes the whole book with a volatility target,
a CPPI drawdown governor and an overnight-gap stress cap. It sweeps the risk
settings and reports the frontier.

**Outputs:** `results_lowdd_sweep.csv` (every setting scored), a best-config
table with the 2016+ out-of-sample row, a decade breakdown, and
`chart_sentinel.png`.

**How to read it:** the `passes` column says whether that setting held inside
the budget; the best config is the highest-CAGR row among those. Then read
the **cash caveat** the run prints at the end — a portfolio this de-risked is
structurally mostly T-bills, so a lot of the full-history CAGR is just 1980s
interest rates. Trust the out-of-sample row more.

---

## 4. Your wealth projection chart

```bash
python3 make_projection.py
```
Regenerates `portfolio_projection.png` — the 40-year compounding chart for
$500/1000/1500/2000-per-month contributions, with milestone years (₹1cr →
₹100cr) and 5-year snapshots. Edit the assumptions at the top of the file
(START_USD, CAGR, GROWTH, monthly levels) and rerun to explore scenarios.

---

## 5. Best & worst years

```bash
python3 best_worst_years.py
```
For each market's winning strategy (Defense on TQQQ, classic SMA200 on gold,
Defense on Nifty 50): the 10 best and 10 worst calendar years, with buy &
hold beside each and the `edge %` column showing who won that year. Read the
edge column in the worst-years table to see what the crash protection is
worth — and in the best-years table to see what it costs.

## 6. Refreshing market data

Prices are cached forever in `data_cache/`. To pull fresh data, delete the
price caches (NOT the source files) and rerun:

```bash
# refresh US index/ETF/bond/gold-futures prices:
rm data_cache/_GSPC.csv data_cache/_IXIC.csv data_cache/_NDX.csv \
   data_cache/_IRX.csv data_cache/_TNX.csv data_cache/GC=F.csv \
   data_cache/IEF.csv 2>/dev/null
python3 run_research.py

# refresh Indian stock prices:
rm data_cache/nifty500_close.csv data_cache/niftymidcap150_close.csv
python3 run_nifty500.py
```

**Never delete** `data_cache/gold_monthly.csv` (LBMA history — source data,
not a cache) or `data_cache/ind_*list.csv` (NSE constituent lists). To
update the constituent lists:

```bash
curl -s -A "Mozilla/5.0" "https://archives.nseindia.com/content/indices/ind_nifty500list.csv" \
     -o data_cache/ind_nifty500list.csv
curl -s -A "Mozilla/5.0" "https://archives.nseindia.com/content/indices/ind_niftymidcap150list.csv" \
     -o data_cache/ind_niftymidcap150list.csv
```

---

## 7. TradingView setup (not a command — a checklist)

**US (the 70% sleeve):**
1. Open a **daily** chart of `NASDAQ:TQQQ`.
2. Pine Editor → paste `tradingview/LRS_VT.pine` → Add to chart.
3. Defaults are already the **LRS-Defense** config (warning weight 0.5,
   extension cap 0.25). Only change: rebalance band → 15 if trading on
   Dhan. (For plain v2: warnW = 1.0, extCap = 0.)
4. Create alerts on "LRS-VT2: RISK-ON", "RISK-OFF", "rebalance" →
   Once Per Bar Close.

**Gold (the 30% sleeve):** daily `AMEX:UGL` chart → paste
`tradingview/LRS_Gold.pine` → set its two alerts. It computes the signal on
spot gold (TVC:GOLD) automatically; the panel says whether to hold UGL or
SGOV right now.

**India:** daily chart of the NSE stock or ETF → paste
`tradingview/LRS_India.pine`. For ETFs enable "signal on a separate index
symbol" and pick the underlying index. Set both alerts.

**Execution rule for every alert:** trade at the next market open, then
stop looking.

---

## 8. Project map

```
PLAYBOOK.md            what/when/how to invest (read this first)
README.md              the research evidence and every disclosed assumption
COMMANDS.md            this file
run_research.py        US engine        -> results_*.csv, chart_flagship.png
run_nifty500.py        India engine     -> results_<universe>.csv, report
run_lowdd.py           low-DD engine    -> results_lowdd_sweep.csv, chart_sentinel.png
make_projection.py     wealth chart     -> portfolio_projection.png
quantlab/              the engine library (data, leverage, bonds, gold,
                       strategies, backtest, metrics, report, india, ollama,
                       sentinel)
tradingview/           LRS_VT.pine (US), LRS_India.pine (NSE)
data_cache/            cached prices + source data (gold, NSE lists)
```
