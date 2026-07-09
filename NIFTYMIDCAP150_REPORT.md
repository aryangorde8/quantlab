# Nifty Midcap 150 — systematic trend-filter research

*Universe: NSE Nifty Midcap 150 constituents; 124 stocks with >= 5 years of history backtested. Strategy: long when price > 200-day SMA, else cash at 6.5%. 10 bps costs, 1-day execution lag. Data: Yahoo Finance, dividend-adjusted.*

## Aggregate results

- stocks tested: 124
- median B&H CAGR: 19.7%
- median SMA200 CAGR: 16.2%
- median B&H max drawdown: -74.0%
- median SMA200 max drawdown: -52.9%
- % stocks where SMA200 improved Sharpe: 42%
- % stocks where SMA200 cut drawdown: 89%
- % stocks with SMA200 CAGR >= 24%: 26%
- stocks with SMA200 CAGR >= 24%: 32

## Market summary (AI-generated, qwen2.5:7b via Ollama)

The backtest compared a buy-and-hold (B&H) strategy to a 200-day Simple Moving Average (SMA) trend filter on the Nifty Midcap 150 universe, which consists of 124 stocks. Over the period, the median compound annual growth rate (CAGR) for the B&H strategy was 19.7%, while the SMA200 approach yielded a lower CAGR of 16.2%. Notably, the SMA200 strategy significantly reduced maximum drawdowns, with only 52.9% compared to the B&H's -74.0%. Approximately 42% of stocks showed an improved Sharpe ratio under the SMA200 strategy, and 89% experienced a reduction in their maximum drawdowns. Additionally, 32 out of the 124 stocks (26%) achieved a CAGR of at least 24% using the SMA200 filter. It is important to note that survivorship bias might affect today's constituent list, as only those stocks that survived the market test are included in the current Nifty Midcap 150 index.

## Top 10 stocks by strategy Sharpe (notes AI-generated, qwen2.5:7b)

### BSE Ltd. (BSE)

SMA200: CAGR 56.3%, Sharpe 1.24, MaxDD -40.5% | B&H: CAGR 47.6%, Sharpe 1.00, MaxDD -71.9%

BSE Ltd. (BSE) has shown strong performance in a backtest comparing a buy-and-hold strategy to a 200-day Simple Moving Average (SMA) trend-following approach, net of a 6.5% INR cash yield when out of the market. The buy-and-hold strategy yielded a Compound Annual Growth Rate (CAGR) of 47.6% with a Sharpe ratio of 1.00 and a maximum drawdown of -71.9%. In contrast, the SMA200 trend-following strategy produced a higher CAGR of 56.3%, a Sharpe ratio of 1.24, and a reduced maximum drawdown to -40.5%, indicating potentially lower risk during market downturns.

### Dixon Technologies (India) Ltd. (DIXON)

SMA200: CAGR 45.8%, Sharpe 1.20, MaxDD -33.1% | B&H: CAGR 42.4%, Sharpe 0.94, MaxDD -57.3%

Over an 8.8-year period, Dixon Technologies (India) Ltd. (DIXON) exhibited superior performance under the 200-day SMA trend-following strategy compared to a buy-and-hold approach. The SMA200 strategy generated a CAGR of 45.8% with a Sharpe ratio of 1.20, outperforming the buy-and-hold's CAGR of 42.4% and Sharpe ratio of 0.94. Additionally, this strategy mitigated maximum drawdown risk more effectively, reducing it from -57.3% for buy-and-hold to -33.1%. However, investors must consider the net-of-6.5% INR cash yield when out of market. Past performance is not indicative of future results.

### Kalyan Jewellers India Ltd. (KALYANKJIL)

SMA200: CAGR 48.7%, Sharpe 1.20, MaxDD -38.7% | B&H: CAGR 35.8%, Sharpe 0.78, MaxDD -57.9%

Over the past 5.3 years, Kalyan Jewellers India Ltd. (KALYANKJIL) has shown promising backtest results with a 1x long-only strategy using a 200-day Simple Moving Average (SMA) trend filter outperforming buy & hold. The SMA200 strategy delivered a Compound Annual Growth Rate (CAGR) of 48.7% and a Sharpe ratio of 1.20, compared to a CAGR of 35.8% and a Sharpe ratio of 0.78 for buy & hold. Notably, the SMA200 strategy also exhibited lower maximum drawdown at -38.7%, as opposed to -57.9% for buy & hold, while netting a 6.5% INR cash yield when out of market. Backtests do not guarantee future performance.

### Hitachi Energy India Ltd. (POWERINDIA)

SMA200: CAGR 53.6%, Sharpe 1.14, MaxDD -40.5% | B&H: CAGR 83.3%, Sharpe 1.47, MaxDD -40.3%

The backtest results for Hitachi Energy India Ltd. (POWERINDIA) over a 6.3-year period show that while the buy-and-hold strategy yielded a CAGR of 83.3% and a Sharpe ratio of 1.47, the 200-day SMA trend-following strategy provided a lower but more stable return profile with a CAGR of 53.6% and a Sharpe ratio of 1.14. Both strategies experienced significant drawdowns, reaching a maximum of -40.3% for buy-and-hold and -40.5% for the SMA200 strategy. Notably, the SMA200 strategy net of a 6.5% INR cash yield when out of market slightly underperformed the buy-and-hold approach but offered reduced volatility.

### Adani Total Gas Ltd. (ATGL)

SMA200: CAGR 52.8%, Sharpe 1.10, MaxDD -50.3% | B&H: CAGR 33.7%, Sharpe 0.69, MaxDD -88.0%

Adani Total Gas Ltd. (ATGL) has shown compelling backtest results over its 7.7-year history, with a 1x long-only SMA200 trend-following strategy outperforming buy & hold significantly. The SMA200 strategy delivered a Compound Annual Growth Rate (CAGR) of 52.8% and a Sharpe ratio of 1.10 compared to the buy & hold CAGR of 33.7% and Sharpe ratio of 0.69. Notably, while the maximum drawdown for the SMA200 strategy was -50.3%, it still outperformed the more severe -88.0% drawdown experienced by a simple buy & hold approach. However, investors should note that past performance is not indicative of future results and backtests do not guarantee future returns.

### KPIT Technologies Ltd. (KPITTECH)

SMA200: CAGR 44.5%, Sharpe 1.08, MaxDD -47.2% | B&H: CAGR 27.0%, Sharpe 0.63, MaxDD -70.0%

KPIT Technologies Ltd. (KPITTECH) has shown compelling backtest results with a 200-day Simple Moving Average (SMA) trend filter strategy outperforming the buy-and-hold approach over its 7.2-year history. The SMA200 strategy achieved a Compound Annual Growth Rate (CAGR) of 44.5% and a Sharpe ratio of 1.08, compared to a CAGR of 27.0% and a Sharpe ratio of 0.63 for buy-and-hold. However, the SMA200 strategy experienced a maximum drawdown of -47.2%, slightly higher than the -70.0% seen with the buy-and-hold approach, net of a 6.5% INR cash yield when out of the market.

### Rail Vikas Nigam Ltd. (RVNL)

SMA200: CAGR 48.9%, Sharpe 1.05, MaxDD -44.8% | B&H: CAGR 44.4%, Sharpe 0.86, MaxDD -64.3%

Over the past 7.2 years, Rail Vikas Nigam Ltd. (RVNL) has shown promising backtest results with both a buy-and-hold strategy and a 200-day SMA trend-following approach. The buy-and-hold strategy yielded a CAGR of 44.4% and a Sharpe ratio of 0.86, but experienced a maximum drawdown of -64.3%. In contrast, the 200-day SMA trend filter generated a higher CAGR of 48.9% with a Sharpe ratio of 1.05, though it had a slightly lower maximum drawdown of -44.8%, indicating potentially smoother returns during market downturns.

### Laurus Labs Ltd. (LAURUSLABS)

SMA200: CAGR 35.6%, Sharpe 1.04, MaxDD -36.1% | B&H: CAGR 33.6%, Sharpe 0.84, MaxDD -58.9%

Over the past 9.5 years, Laurus Labs Ltd. (LAURUSLABS) has shown promising backtest results with a 1x long-only strategy using a 200-day Simple Moving Average (SMA) trend filter outperforming buy & hold. The SMA200 strategy delivered a Compound Annual Growth Rate (CAGR) of 35.6% and a Sharpe ratio of 1.04, compared to 33.6% CAGR and 0.84 Sharpe for buy & hold. Additionally, the SMA200 strategy reduced maximum drawdown from -58.9% in buy & hold to -36.1%, while netting a 6.5% Indian Rupee (INR) cash yield when out of market.

### Persistent Systems Ltd. (PERSISTENT)

SMA200: CAGR 28.3%, Sharpe 0.86, MaxDD -41.3% | B&H: CAGR 28.3%, Sharpe 0.74, MaxDD -46.4%

Persistent Systems Ltd. (PERSISTENT) has shown similar long-term performance between a buy & hold strategy and a 200-day SMA trend filter approach over the past 16.3 years, with both strategies delivering a CAGR of 28.3%. While the Sharpe ratio for the SMA200 strategy is marginally higher at 0.86 compared to 0.74 for buy & hold, both exhibit significant drawdowns, with maximum drawdowns of -46.4% and -41.3%, respectively. Notably, netting out a 6.5% INR cash yield when out of the market does not significantly alter these backtest results.

### K.P.R. Mill Ltd. (KPRMILL)

SMA200: CAGR 32.4%, Sharpe 0.85, MaxDD -38.9% | B&H: CAGR 27.1%, Sharpe 0.63, MaxDD -88.9%

K.P.R. Mill Ltd. (KPRMILL) has shown improved performance with the 1x long-only strategy using a 200-day Simple Moving Average (SMA) trend filter compared to buy & hold over an 18.9-year history, with a Compound Annual Growth Rate (CAGR) of 32.4% versus 27.1%. The SMA200 strategy also demonstrated better risk-adjusted returns, achieving a Sharpe ratio of 0.85 against 0.63 for buy & hold. However, the maximum drawdown was lower at -38.9% with the SMA200 strategy compared to -88.9% under buy & hold, indicating reduced volatility during market downturns.

---

*Caveats: survivorship bias (today's constituents), no taxes, INR cash yield approximated at a constant 6.5%. Backtests do not guarantee future returns. Not investment advice.*
