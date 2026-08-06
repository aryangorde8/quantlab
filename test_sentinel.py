"""Mechanical validation of quantlab/sentinel.py on synthetic data.

This validates CODE CORRECTNESS ONLY (no look-ahead, governor binds, vol
target is hit, turnover is investable). It says nothing about whether the
strategy has an edge -- that needs real prices.
"""
import os
import sys
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from quantlab import sentinel, metrics

rng = np.random.default_rng(7)
n = 252 * 55
idx = pd.bdate_range("1971-01-01", periods=n)

def sleeve(vol, drift, crash_days=(), crash_size=-0.6, t_df=4):
    """Fat-tailed daily returns (Student-t) with optional crash days."""
    r = drift / 252 + (vol / np.sqrt(252)) * rng.standard_t(t_df, n) / np.sqrt(t_df / (t_df - 2))
    for d in crash_days:
        r[d] = crash_size
    return r

rf = pd.Series(0.045 / 252, index=idx)
crash = [int(n * 0.30), int(n * 0.62)]           # 1987-style overnight gaps
sleeves = pd.DataFrame({
    "equity3x": sleeve(0.35, 0.18, crash_days=crash, crash_size=-0.61),
    "ust10":    sleeve(0.07, 0.03),
    "gold":     sleeve(0.15, 0.05),
}, index=idx)

print("=" * 78)
print("SYNTHETIC SLEEVE INPUTS (not real data -- mechanics test only)")
print("=" * 78)
for c in sleeves:
    print(f"  {c:10s} vol {sleeves[c].std()*np.sqrt(252)*100:5.1f}%   "
          f"CAGR {metrics.cagr(sleeves[c])*100:6.2f}%   "
          f"MaxDD {metrics.max_drawdown(sleeves[c])*100:7.1f}%")

# ---------------------------------------------------------------- test 1
print("\n[1] LOOK-AHEAD TEST: perturb sleeve returns on one day, check that the")
print("    exposure decided FOR that day is unchanged (it must use data < t).")
ret_a, diag_a = sentinel.build(sleeves, rf, target_vol=0.06, dd_budget=0.10)
t = 5000
pert = sleeves.copy()
pert.iloc[t] += 0.25                    # huge shock on day t only
ret_b, diag_b = sentinel.build(pert, rf, target_vol=0.06, dd_budget=0.10)

same_upto_t = np.allclose(diag_a["exposure"].iloc[: t + 1], diag_b["exposure"].iloc[: t + 1])
differs_after = not np.allclose(diag_a["exposure"].iloc[t + 1 :], diag_b["exposure"].iloc[t + 1 :])
print(f"    exposure identical through day t : {same_upto_t}   <- must be True")
print(f"    exposure reacts only after day t : {differs_after}  <- must be True")
assert same_upto_t, "LOOK-AHEAD: day-t return leaked into day-t sizing"

# ---------------------------------------------------------------- test 2
print("\n[2] VOL TARGET: realised vol should land near the target.")
for tv in (0.04, 0.06, 0.08):
    r, d = sentinel.build(sleeves, rf, target_vol=tv, dd_budget=0.10)
    print(f"    target {tv*100:4.1f}%  ->  realised {metrics.ann_vol(r)*100:5.2f}%   "
          f"avg exposure {d['exposure'].mean()*100:5.1f}%")

# ---------------------------------------------------------------- test 3
print("\n[3] GOVERNOR: does a tighter budget actually cut drawdown?")
print("    (crash days are unhedgeable overnight gaps -- the honest limit)")
for bud in (0.06, 0.10, 0.15, 0.25, 1.00):
    r, d = sentinel.build(sleeves, rf, target_vol=0.06, dd_budget=bud)
    tag = "governor off" if bud >= 1.0 else f"budget {bud*100:4.1f}%"
    print(f"    {tag:14s} -> MaxDD {metrics.max_drawdown(r)*100:6.2f}%   "
          f"CAGR {metrics.cagr(r)*100:5.2f}%   Sharpe {metrics.sharpe(r, rf):4.2f}")

# ---------------------------------------------------------------- test 4
print("\n[4] CASH-LOCK: rolling HWM should keep exposure recovering after a hit.")
r, d = sentinel.build(sleeves, rf, target_vol=0.06, dd_budget=0.10)
c = crash[0]
print(f"    exposure  20d before crash : {d['exposure'].iloc[c-20]*100:5.1f}%")
print(f"    exposure   5d after  crash : {d['exposure'].iloc[c+5]*100:5.1f}%")
print(f"    exposure 500d after  crash : {d['exposure'].iloc[c+500]*100:5.1f}%  <- must recover")

# ---------------------------------------------------------------- test 5
print("\n[5] TURNOVER: must stay investable (band rebalancing).")
for band in (0.02, 0.05, 0.10, 0.20):
    r, d = sentinel.build(sleeves, rf, target_vol=0.06, dd_budget=0.10, band=band)
    print(f"    band {band*100:4.1f}% -> {sentinel.turnover_per_year(d):5.2f} round-trips/yr   "
          f"CAGR {metrics.cagr(r)*100:5.2f}%   MaxDD {metrics.max_drawdown(r)*100:6.2f}%")

print("\nAll mechanical assertions passed.")
