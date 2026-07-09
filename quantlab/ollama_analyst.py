"""Research commentary via a local Ollama model — free, private, offline.

The LLM never computes numbers; it only narrates metrics that the backtest
engine produced. Every generated section is labeled as AI-written.
"""

from __future__ import annotations

import json
import urllib.request

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "qwen2.5:7b"

SYSTEM = (
    "You are a buy-side quantitative research analyst. You are given ONLY "
    "backtest statistics; do not invent numbers, news, or fundamentals not "
    "provided. Be concise, specific and neutral. Always note that backtests "
    "do not guarantee future returns. Plain prose, no headers, no bullet lists."
)


def generate(prompt: str, model: str = MODEL, timeout: int = 300) -> str:
    payload = {
        "model": model,
        "system": SYSTEM,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.4, "num_predict": 400},
    }
    req = urllib.request.Request(
        OLLAMA_URL,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read())["response"].strip()


def stock_note(row: dict) -> str:
    prompt = (
        f"Write a 3-4 sentence research note on this Indian stock's backtest "
        f"results (1x long-only, 200-day SMA trend filter vs buy & hold, "
        f"net of 6.5% INR cash yield when out of market).\n\n"
        f"Company: {row['Company Name']} ({row['Symbol']}), "
        f"Industry: {row['Industry']}, History: {row['years']:.1f} years\n"
        f"Buy & hold: CAGR {row['bh_cagr']:.1%}, Sharpe {row['bh_sharpe']:.2f}, "
        f"max drawdown {row['bh_maxdd']:.1%}\n"
        f"SMA200 strategy: CAGR {row['sma_cagr']:.1%}, Sharpe {row['sma_sharpe']:.2f}, "
        f"max drawdown {row['sma_maxdd']:.1%}"
    )
    return generate(prompt)


def market_summary(stats: str) -> str:
    prompt = (
        "Write a 2-paragraph summary of this cross-sectional backtest of the "
        "Nifty 500 universe (200-day SMA trend filter applied to every stock, "
        "vs buy & hold). Mention survivorship bias in today's constituent "
        f"list.\n\nAggregate statistics:\n{stats}"
    )
    return generate(prompt)
