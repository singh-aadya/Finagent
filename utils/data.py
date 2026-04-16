"""
utils/data.py
─────────────
Data fetching utilities for the AI Financial Analysis Dashboard.

Responsibilities:
  - Fetch historical OHLCV price data from Yahoo Finance via yfinance
  - Fetch fundamental ratios (P/E, Forward P/E, Dividends, P/B, D/E, ROE)
  - Validate ticker symbols and handle missing / malformed data gracefully
  - Return clean pandas DataFrames ready for downstream processing

No API keys required – all data comes from Yahoo Finance's public endpoints.
"""

from __future__ import annotations

import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta


# ─────────────────────────────────────────────────────────────────────────────
# Public helpers
# ─────────────────────────────────────────────────────────────────────────────

def fetch_data(
    tickers: list[str],
    start: datetime,
    end: datetime,
) -> dict[str, pd.DataFrame]:
    """
    Download daily Close / Volume history for every ticker in *tickers*.

    Parameters
    ----------
    tickers : list[str]
        List of valid Yahoo Finance ticker symbols, e.g. ["AAPL", "MSFT"].
    start   : datetime  –  first calendar date (inclusive)
    end     : datetime  –  last  calendar date (inclusive)

    Returns
    -------
    dict[str, pd.DataFrame]
        Mapping  ticker → DataFrame with columns ["Close", "Volume"].
        Tickers that return empty or all-NaN data are silently excluded.

    Raises
    ------
    ValueError
        If *tickers* is empty or none of the requested tickers returned data.
    """
    if not tickers:
        raise ValueError("No tickers provided.")

    result: dict[str, pd.DataFrame] = {}

    for ticker in tickers:
        ticker = ticker.strip().upper()
        try:
            raw = yf.download(
                ticker,
                start=start.strftime("%Y-%m-%d"),
                end=(end + timedelta(days=1)).strftime("%Y-%m-%d"),
                progress=False,
                auto_adjust=True,
            )
        except Exception as exc:  # network / parse error
            continue

        if raw.empty:
            continue

        # Flatten multi-level columns that yfinance sometimes returns
        if isinstance(raw.columns, pd.MultiIndex):
            raw.columns = raw.columns.get_level_values(0)

        # Keep only the columns we need
        keep = [c for c in ("Close", "Volume") if c in raw.columns]
        if not keep:
            continue

        df = raw[keep].dropna(how="all")
        if df.empty:
            continue

        result[ticker] = df

    if not result:
        raise ValueError(
            "None of the requested tickers returned usable price data. "
            "Please check your ticker symbols."
        )

    return result


def fetch_fundamentals(tickers: list[str]) -> pd.DataFrame:
    """
    Retrieve fundamental financial ratios for each ticker.

    Metrics fetched
    ───────────────
    • P/E Ratio        – trailing twelve months price-to-earnings
    • Forward P/E      – consensus forward price-to-earnings
    • Dividends        – trailing annual dividend yield (%)
    • Price to Book    – market price divided by book value per share
    • Debt / Equity    – total debt divided by shareholders' equity
    • ROE              – return on equity (net income / avg equity)

    Parameters
    ----------
    tickers : list[str]

    Returns
    -------
    pd.DataFrame
        One column per ticker, one row per metric.
        Missing values appear as "N/A" strings for clean display.
    """
    metric_keys = {
        "P/E Ratio":     "trailingPE",
        "Forward P/E":   "forwardPE",
        "Dividends (%)": "dividendYield",
        "Price to Book": "priceToBook",
        "Debt / Equity": "debtToEquity",
        "ROE":           "returnOnEquity",
    }

    records: dict[str, dict] = {}

    for ticker in tickers:
        ticker = ticker.strip().upper()
        info: dict = {}
        try:
            info = yf.Ticker(ticker).info or {}
        except Exception:
            pass

        row: dict = {}
        for label, key in metric_keys.items():
            raw_val = info.get(key)
            if raw_val is None or raw_val != raw_val:          # None or NaN
                row[label] = "N/A"
            elif label == "Dividends (%)":
                row[label] = f"{raw_val * 100:.4f}%"           # e.g. 0.031 → "3.1000%"
            elif label == "ROE":
                row[label] = f"{raw_val:.4f}"
            else:
                row[label] = round(raw_val, 2)

        records[ticker] = row

    df = pd.DataFrame(records)
    df.index.name = "Metric"
    return df


def get_ticker_name(ticker: str) -> str:
    """
    Return the long name for *ticker* (e.g. "Advanced Micro Devices, Inc.")
    or fall back to the ticker symbol if the info is unavailable.
    """
    try:
        info = yf.Ticker(ticker.strip().upper()).info or {}
        return info.get("longName") or info.get("shortName") or ticker.upper()
    except Exception:
        return ticker.upper()