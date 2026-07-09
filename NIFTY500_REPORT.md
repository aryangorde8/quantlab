# Nifty 500 — systematic trend-filter research

*Universe: NSE Nifty 500 constituents; 396 stocks with >= 5 years of history backtested. Strategy: long when price > 200-day SMA, else cash at 6.5%. 10 bps costs, 1-day execution lag. Data: Yahoo Finance, dividend-adjusted.*

## Aggregate results

- stocks tested: 396
- median B&H CAGR: 19.6%
- median SMA200 CAGR: 16.6%
- median B&H max drawdown: -79.5%
- median SMA200 max drawdown: -54.3%
- % stocks where SMA200 improved Sharpe: 44%
- % stocks where SMA200 cut drawdown: 88%
- % stocks with SMA200 CAGR >= 24%: 28%
- stocks with SMA200 CAGR >= 24%: 109

## Market summary (AI-generated, qwen2.5:7b via Ollama)

The cross-sectional backtest of the Nifty 500 universe applied a 200-day Simple Moving Average (SMA) trend filter to each stock, comparing its performance against a buy-and-hold strategy. Over the period tested with 396 stocks, the median Compound Annual Growth Rate (CAGR) for the buy-and-hold strategy was 19.6%, while the SMA200 strategy yielded a median CAGR of 16.6%. The backtest also revealed that the buy-and-hold strategy experienced a higher maximum drawdown at -79.5% compared to the SMA200 strategy, which had a lower maximum drawdown of -54.3%. Notably, 44% of stocks showed improved Sharpe ratios with the SMA200 filter, and 88% saw reduced drawdowns. Additionally, 109 out of the 396 stocks achieved a CAGR of at least 24% using the SMA200 strategy. However, it is important to note that survivorship bias may affect today's constituent list, as this backtest does not account for any companies that have been removed from or added to the Nifty 500 index during the period.

## Top 10 stocks by strategy Sharpe (notes AI-generated, qwen2.5:7b)

### Adani Green Energy Ltd. (ADANIGREEN)

SMA200: CAGR 73.8%, Sharpe 1.46, MaxDD -49.3% | B&H: CAGR 61.6%, Sharpe 1.05, MaxDD -84.4%

Adani Green Energy Ltd. (ADANIGREEN) has shown compelling backtest results over an 8.1-year period with a 200-day SMA trend filter compared to a buy & hold strategy. The SMA200 strategy delivered a higher Compound Annual Growth Rate (CAGR) of 73.8% versus 61.6% for buy & hold, along with a Sharpe ratio of 1.46 vs. 1.05. Additionally, the maximum drawdown was lower at -49.3% using the SMA200 filter compared to -84.4% under buy & hold, indicating potentially improved risk-adjusted returns and reduced volatility during downturns. Please note that backtest results do not guarantee future performance.

### BSE Ltd. (BSE)

SMA200: CAGR 56.3%, Sharpe 1.24, MaxDD -40.5% | B&H: CAGR 47.6%, Sharpe 1.00, MaxDD -71.9%

Over the past 9.4 years, BSE Ltd. (BSE) has shown strong performance with a buy & hold strategy yielding a Compound Annual Growth Rate (CAGR) of 47.6%, although it experienced a maximum drawdown of -71.9%. Implementing a 200-day Simple Moving Average (SMA) trend filter improved both the CAGR to 56.3% and Sharpe ratio to 1.24, while reducing the maximum drawdown to -40.5%. Notably, this strategy net of a 6.5% INR cash yield when out of market further enhances risk-adjusted returns.

### Dixon Technologies (India) Ltd. (DIXON)

SMA200: CAGR 45.8%, Sharpe 1.20, MaxDD -33.1% | B&H: CAGR 42.4%, Sharpe 0.94, MaxDD -57.3%

Over the past 8.8 years, Dixon Technologies (India) Ltd. (DIXON) has shown compelling backtest results with a 200-day SMA trend filter strategy outperforming buy & hold. The SMA200 strategy delivered a CAGR of 45.8% and a Sharpe ratio of 1.20, compared to 42.4% and 0.94 for buy & hold, respectively. Additionally, the strategy reduced maximum drawdown from -57.3% to -33.1%, while netting out a 6.5% INR cash yield when out of market.

### Kalyan Jewellers India Ltd. (KALYANKJIL)

SMA200: CAGR 48.7%, Sharpe 1.20, MaxDD -38.7% | B&H: CAGR 35.8%, Sharpe 0.78, MaxDD -57.9%

Over the past 5.3 years, Kalyan Jewellers India Ltd. (KALYANKJIL) has shown compelling backtest results with a 200-day SMA trend filter strategy, delivering a CAGR of 48.7% and a Sharpe ratio of 1.20, compared to a buy & hold approach that yielded a CAGR of 35.8% and a Sharpe ratio of 0.78. The SMA200 strategy also demonstrated lower maximum drawdown at -38.7%, relative to the -57.9% seen in a buy & hold scenario. However, it is important to note that these backtest results do not guarantee future performance and are net of a 6.5% INR cash yield when out of market.

### Mazagoan Dock Shipbuilders Ltd. (MAZDOCK)

SMA200: CAGR 59.7%, Sharpe 1.14, MaxDD -34.7% | B&H: CAGR 82.5%, Sharpe 1.34, MaxDD -44.6%

Over the past 5.7 years, Mazagoan Dock Shipbuilders Ltd. (MAZDOCK) has shown robust performance in both buy-and-hold and SMA200 strategy backtests. The buy-and-hold approach yielded a CAGR of 82.5%, with a Sharpe ratio of 1.34 and a maximum drawdown of -44.6%. In contrast, the SMA200 trend filter strategy provided a lower but still significant CAGR of 59.7%, albeit with slightly reduced risk metrics—showing a Sharpe ratio of 1.14 and a maximum drawdown of -34.7%. Both strategies net of 6.5% INR cash yield when out of market highlight the potential for disciplined trading approaches to enhance returns while managing downside risks.

### Hitachi Energy India Ltd. (POWERINDIA)

SMA200: CAGR 53.6%, Sharpe 1.14, MaxDD -40.5% | B&H: CAGR 83.3%, Sharpe 1.47, MaxDD -40.3%

Over the past 6.3 years, Hitachi Energy India Ltd. (POWERINDIA) has shown a strong performance with a buy & hold strategy yielding a CAGR of 83.3% and a Sharpe ratio of 1.47, though it experienced a maximum drawdown of -40.3%. When applying a 200-day SMA trend filter, the strategy resulted in a lower but still substantial CAGR of 53.6%, with a slightly reduced Sharpe ratio of 1.14 and a similar maximum drawdown of -40.5%. Both strategies net of 6.5% INR cash yield when out of market highlight the potential for significant returns, though investors should note that backtest results do not guarantee future performance.

### Adani Total Gas Ltd. (ATGL)

SMA200: CAGR 52.8%, Sharpe 1.10, MaxDD -50.3% | B&H: CAGR 33.7%, Sharpe 0.69, MaxDD -88.0%

Adani Total Gas Ltd. (ATGL) has shown compelling backtest results with a 200-day SMA trend-following strategy compared to a buy-and-hold approach over its 7.7-year history. The SMA200 strategy delivered a higher Compound Annual Growth Rate (CAGR) of 52.8% and a Sharpe ratio of 1.10, outperforming the buy-and-hold CAGR of 33.7% with a Sharpe ratio of 0.69. Notably, while the SMA200 strategy experienced a maximum drawdown of -50.3%, this was significantly lower than the -88.0% seen in the buy-and-hold approach, net of a 6.5% INR cash yield when out of market.

### KPIT Technologies Ltd. (KPITTECH)

SMA200: CAGR 44.5%, Sharpe 1.08, MaxDD -47.2% | B&H: CAGR 27.0%, Sharpe 0.63, MaxDD -70.0%

KPIT Technologies Ltd. (KPITTECH) has shown compelling backtest results with a 200-day SMA trend filter strategy over its 7.2-year history, achieving a CAGR of 44.5% and a Sharpe ratio of 1.08 compared to a buy & hold approach that yielded a CAGR of 27.0% and a Sharpe ratio of 0.63. The SMA200 strategy also demonstrated lower maximum drawdowns, with -47.2% versus -70.0% for the buy & hold strategy. However, it is important to note that these backtest results do not guarantee future performance and are net of a 6.5% INR cash yield when out of market.

### Indian Railway Finance Corporation Ltd. (IRFC)

SMA200: CAGR 43.9%, Sharpe 1.08, MaxDD -35.2% | B&H: CAGR 30.5%, Sharpe 0.71, MaxDD -58.5%

Over the past 5.4 years, Indian Railway Finance Corporation Ltd. (IRFC) has shown promising backtest results with a SMA200 trend filter strategy outperforming buy & hold. The SMA200 strategy achieved a CAGR of 43.9% and a Sharpe ratio of 1.08, compared to a CAGR of 30.5% and a Sharpe ratio of 0.71 for the buy & hold approach. Additionally, the SMA200 strategy demonstrated better risk management with a maximum drawdown of -35.2%, significantly lower than the -58.5% experienced by the buy & hold strategy.

### Rail Vikas Nigam Ltd. (RVNL)

SMA200: CAGR 48.9%, Sharpe 1.05, MaxDD -44.8% | B&H: CAGR 44.4%, Sharpe 0.86, MaxDD -64.3%

Over the past 7.2 years, Rail Vikas Nigam Ltd. (RVNL) has shown compelling backtest results with a buy-and-hold strategy yielding a CAGR of 44.4% and a Sharpe ratio of 0.86, though it experienced a maximum drawdown of -64.3%. Implementing a 200-day Simple Moving Average (SMA) trend filter improved performance further, achieving a higher CAGR of 48.9% and a Sharpe ratio of 1.05, while reducing the maximum drawdown to -44.8%. Notably, this strategy net of 6.5% INR cash yield when out of market provides an enhanced risk-adjusted return profile.

---

*Caveats: survivorship bias (today's constituents), no taxes, INR cash yield approximated at a constant 6.5%. Backtests do not guarantee future returns. Not investment advice.*
