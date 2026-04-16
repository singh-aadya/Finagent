"""
utils/indicators.py
───────────────────
Technical indicator calculations used by the dashboard charts.

Implements
──────────
• normalize_prices()  – percentage-return normalization (base = 100)
• calculate_rsi()     – Relative Strength Index with configurable window

Why these indicators?
─────────────────────
Normalised prices let us compare stocks at very different price levels on a
single chart – each series starts at 100 and moves according to % returns.

RSI (Wilder, 1978) measures momentum on a 0-100 scale.  Values above 70 are
conventionally considered "overbought"; values below 30 "oversold".  A 14-day
window is the most widely used setting and the one we default to here.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


# ─────────────────────────────────────────────────────────────────────────────
# Normalization
# ─────────────────────────────────────────────────────────────────────────────

def normalize_prices(price_series: pd.Series) -> pd.Series:
    """
    Convert an absolute price series into a percentage-return index.

    Formula
    ───────
        norm_t = (price_t / price_0) × 100

    The first non-NaN value is used as the base (= 100).

    Parameters
    ----------
    price_series : pd.Series
        Raw closing prices indexed by date.

    Returns
    -------
    pd.Series
        Normalised series starting at 100.0 on the first trading day.

    Raises
    ------
    ValueError
        If the series is empty or entirely NaN.
    """
    clean = price_series.dropna()
    if clean.empty:
        raise ValueError("Cannot normalise an empty or all-NaN price series.")

    base = clean.iloc[0]
    if base == 0:
        raise ValueError("Base price is zero – cannot normalise.")

    return (price_series / base) * 100.0


# ─────────────────────────────────────────────────────────────────────────────
# RSI
# ─────────────────────────────────────────────────────────────────────────────

def calculate_rsi(price_series: pd.Series, window: int = 14) -> pd.Series:
    """
    Compute the Relative Strength Index (RSI) using Wilder's smoothing method.

    Algorithm
    ─────────
    1.  Compute daily price change: Δ = price_t − price_{t-1}
    2.  Separate gains (Δ > 0) and losses (|Δ| where Δ < 0).
    3.  Compute the initial average gain / loss over the first *window* bars
        using a simple mean (Wilder's recommended seed).
    4.  For subsequent bars, apply the exponential smoothing factor
            avg_gain_t = (avg_gain_{t-1} × (window−1) + gain_t) / window
    5.  RS  = avg_gain / avg_loss
        RSI = 100 − 100 / (1 + RS)

    Parameters
    ----------
    price_series : pd.Series
        Closing prices indexed by date.
    window : int
        Look-back period (default 14 – Wilder's original recommendation).

    Returns
    -------
    pd.Series
        RSI values in [0, 100]; NaN for the first *window* bars where
        insufficient history is available.

    Why 14 days?
    ────────────
    Wilder (1978) chose 14 days as a balance between responsiveness and noise.
    Shorter windows react faster but generate more false signals; longer ones
    are smoother but lag meaningful reversals.
    """
    if price_series.empty or len(price_series) < window + 1:
        return pd.Series(dtype=float, index=price_series.index)

    delta = price_series.diff()

    gain = delta.clip(lower=0)    # Δ > 0 → gain; else 0
    loss = (-delta).clip(lower=0) # Δ < 0 → loss (positive); else 0

    # Wilder smoothing – equivalent to EWM with com = window - 1
    avg_gain = gain.ewm(com=window - 1, min_periods=window).mean()
    avg_loss = loss.ewm(com=window - 1, min_periods=window).mean()

    rs = avg_gain / avg_loss.replace(0, np.nan)   # avoid division by zero
    rsi = 100.0 - (100.0 / (1.0 + rs))

    return rsi