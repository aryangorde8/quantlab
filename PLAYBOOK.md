# The Investing Playbook

Everything from the research, condensed into what to do, when, and why.
Read alongside [README.md](README.md) (the evidence) and
[COMMANDS.md](COMMANDS.md) (how to run everything).

---

## 0. What "out-of-sample since 2016: 31.8% at -47.2%" means

A backtest can cheat: rules built in 2026 already "know" what happened in
2008. The honest test is to score the rules only on data **after** the core
research was published (the Gayed & Bilello paper came out mid-2016). On
2016-07 → today, a period the original rules could not have been fitted to,
LRS-Fortress compounded **31.8%/year** and its worst peak-to-trough loss was
**-47.2%**. That's the closest a backtest gets to "what if I had started
then." One honesty note: the Defense/gold refinements were added in 2026, so
2016+ is only *partially* out-of-sample for those pieces — the number is
evidence, not proof.

---

## 1. The portfolio (LRS-Fortress)

| Sleeve | Weight | Instrument | Signal | Trades/yr |
|---|---|---|---|---|
| US equity trend | **70%** | TQQQ | LRS-Defense (Pine: `LRS_VT.pine`, warnW=0.5, extCap=0.25, signal NASDAQ:NDX) | ~5-7 |
| Gold trend | **30%** | UGL (2x gold) | gold above its 200-day SMA → hold; below → SGOV | ~2 |
| Defensive parking | (inside the 70%) | IEF / GLD / SGOV | when equity is risk-off: hold whichever of IEF or GLD has the higher trailing 12-month return; SGOV if neither beats it | ~monthly check |

**Evidence (Nasdaq Composite, 1971–2026, net of costs):** 28.0% CAGR,
-49.3% max drawdown, Sharpe 0.94, worst year -34%. Every drawdown episode in
55 years below -50%.

### Sizing by life stage
- **Small account (first 1-2 years):** 100% LRS-Defense equity sleeve, skip
  the gold sleeve. Higher growth; a deep drawdown on a small base is repaired
  by contributions.
- **Serious money:** full Fortress 70/30. This is the config the numbers
  above describe.
- **Large / can't-afford-to-lose money:** slide toward 60/40
  Defense+bond-momentum (21-22% CAGR, ~-37% MaxDD, Sharpe 0.89).

---

## 2. WHEN to invest — each market

**The system times entries for you. You never decide "is now a good time" —
you read the chart panel and obey.**

### US equity (TQQQ) — the growth engine
- Open the daily TQQQ chart with `LRS_VT.pine`. The panel says RISK-ON or
  RISK-OFF and the target weight.
- **Starting today:** if RISK-ON, buy at the shown weight immediately —
  don't wait for a dip. If RISK-OFF, park the money per the defensive
  rotation and wait for the BUY alert. Historically the system is invested
  ~70% of days.
- **Ongoing:** act on alerts, next market open after each, ~5-7 times/year.
- **Monthly contributions:** buy whatever the current signal says (TQQQ if
  risk-on, the defensive asset if not). Never save up waiting for a signal.

### Gold sleeve (UGL)
- Daily gold chart (TVC:GOLD or GLD) with a 200-day SMA — or run
  `LRS_India.pine` on it with the ladder off.
- Above the line → hold UGL. Below → hold SGOV. ~2 changes a year.

### Defensive parking (when equity is risk-off)
- Once a month, compare 12-month returns of IEF and GLD (any charting site).
- Risk-off cash goes to the stronger one; if neither beat SGOV's return,
  SGOV. This one rule added ~1%/yr and is why 2022 didn't hurt the parking.

### India (NIFTYBEES / MID150BEES) — optional domestic sleeve
- Use `LRS_India.pine` (two-speed ladder). Same mechanics: act on alerts,
  park risk-off money in a liquid fund.
- **Know what it is:** at 1x (no leveraged ETFs in India) this is *drawdown
  protection, not a return enhancer* — median stock drawdown -55% vs -74%
  buy-and-hold, at a ~2-3pp CAGR cost. Use it if you want domestic,
  LRS-free, simpler-tax exposure — not because it competes with TQQQ CAGR.
- Individual NSE stocks: the filter is a seatbelt, not armor — overnight
  gap-downs on news go straight through a daily signal. Prefer the ETFs.

### Rebalancing between sleeves
- Check quarterly. If 70/30 has drifted past 75/25 or 65/35, trade back to
  70/30. In taxable accounts, rebalance with new contributions first.

---

## 3. Execution route (from India)

1. **Dhan GIFT City** (confirmed carrying TQQQ): fund via the RBI's
   Liberalised Remittance Scheme (A2 form; LRS caps remittances per person
   per financial year, and TCS above the statutory threshold is prepaid tax,
   not a cost). Verify UGL/SGOV/IEF are searchable; if UGL isn't, IBKR
   carries everything.
2. Costs: Dhan 0.25%/trade ≈ 1.2 CAGR points at our trade frequency (use
   the 15-point rebalance band in the Pine). IBKR ≈ free — switch when the
   account is large enough to care.
3. **Taxes are the biggest real cost:** ~10 trades/yr = short-term gains at
   slab rate (~28% pre-tax becomes ~19-20% post-tax at the 30% slab).
   Foreign holdings go in Schedule FA of your ITR — non-negotiable. One CA
   session before the first remittance.

---

## 4. Expectations — write these down before starting

- **Planning CAGR: ~19-20% post-tax** (28% research − costs − taxes). Any
  long-horizon plan at this rate depends on *growing* contributions, not on
  the return alone — early contributions dominate the terminal outcome
  (year-1 money compounds on the order of 100x more than year-30 money).
- **A -35% to -50% drawdown WILL happen** — likely several times over 30
  years. It is not the strategy breaking; it's the strategy working as
  measured. 2008 took -49.3% and recovered in 10 months.
- The whole 30-year outcome depends on obeying alerts during exactly those
  moments. Every override is an untested strategy.

## 5. The discipline rules

1. Paper-trade the alerts 2-3 months before real money.
2. Automate contributions; increase them with income (front-load anything
   extra — year-1 money compounds ~185x by year 30).
3. Check the market only when an alert fires, plus one monthly 10-minute
   routine (rotation check, weights, alerts armed).
4. Keep an emergency reserve and a plain index-fund core OUTSIDE this system
   so no life event can force a sale at a bottom.
5. Re-read section 4 during every drawdown.

---

*All numbers are backtests net of modeled costs; none are promises. Not
investment advice. The next crisis is the only exam that counts.*
