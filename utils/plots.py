"""
utils/plots.py
──────────────
Plotly chart factories for the AI Financial Analysis Dashboard.

Each function returns a go.Figure / px.Figure that Streamlit can render
with  st.plotly_chart(fig, use_container_width=True).

Charts implemented
──────────────────
1.  plot_normalised_prices()  – % return comparison (all tickers on one axis)
2.  plot_rsi()                – RSI panel with overbought / oversold bands
3.  plot_volume()             – Volume bars + 20-day moving-average line
"""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Consistent colour palette – one colour per position in the ticker list
# _PALETTE = [
#     "#4C8BF5",  # blue
#     "#F5A623",  # amber
#     "#2ECC71",  # green
#     "#E74C3C",  # red
#     "#9B59B6",  # purple
#     "#1ABC9C",  # teal
#     "#F39C12",  # orange
#     "#3498DB",  # sky-blue
# ]

_PALETTE = [
    "#00E5FF",  # neon cyan
    "#FFD54F",  # soft yellow
    "#00FFA3",  # neon green
    "#FF4C4C",  # red
    "#B388FF",  # purple
]


def _ticker_colour(idx: int) -> str:
    """Return a colour from the palette, wrapping around if needed."""
    return _PALETTE[idx % len(_PALETTE)]


# ─────────────────────────────────────────────────────────────────────────────
# 1. Normalised price comparison
# ─────────────────────────────────────────────────────────────────────────────

def plot_normalised_prices(
    normalised: dict[str, pd.Series],
) -> go.Figure:
    """
    Overlay normalised price curves (base = 100) for all tickers.

    Why normalise?
    ──────────────
    Stocks trade at vastly different price levels – NVDA at $1 000 and a
    $10 small-cap can't share a raw-price Y-axis meaningfully.  Normalising
    to a common 100 base lets every series be compared purely on % return.

    Parameters
    ----------
    normalised : dict[str, pd.Series]
        Mapping  ticker → normalised price series (from indicators.normalize_prices).

    Returns
    -------
    go.Figure
    """
    fig = go.Figure()

    for idx, (ticker, series) in enumerate(normalised.items()):
        series = series.dropna()
        pct_change = series.iloc[-1] - 100.0 if not series.empty else 0.0
        sign = "+" if pct_change >= 0 else ""
        label = f"{ticker} ({sign}{pct_change:.1f}%)"

        fig.add_trace(
            go.Scatter(
                x=series.index,
                y=series.values,
                mode="lines",
                name=label,
                line=dict(color=_ticker_colour(idx), width=2),
                hovertemplate=(
                    f"<b>{ticker}</b><br>"
                    "Date: %{x|%Y-%m-%d}<br>"
                    "Index: %{y:.2f}<extra></extra>"
                ),
            )
        )

    # Horizontal baseline at 100
    fig.add_hline(
        y=100,
        line_dash="dot",
        line_color="rgba(180,180,180,0.6)",
        annotation_text="Base (100)",
        annotation_position="right",
    )

    fig.update_layout(
        title="Normalised Price Comparison (Base = 100)",
        xaxis_title="Date",
        yaxis_title="Normalised Price Index",
        hovermode="x unified",
        # legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            bgcolor="rgba(0,0,0,0)",
            font=dict(size=12)
        )
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(size=13),
        margin=dict(t=60, b=40, l=60, r=20),
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=True, gridcolor="rgba(180,180,180,0.15)")

    return fig


# ─────────────────────────────────────────────────────────────────────────────
# 2. RSI
# ─────────────────────────────────────────────────────────────────────────────

def plot_rsi(
    rsi_dict: dict[str, pd.Series],
    overbought: float = 70.0,
    oversold: float = 30.0,
) -> go.Figure:
    """
    Draw RSI lines for each ticker with overbought / oversold reference bands.

    RSI interpretation
    ──────────────────
    • RSI > 70 → potentially overbought (price may reverse downward)
    • RSI < 30 → potentially oversold  (price may reverse upward)
    • RSI ≈ 50 → momentum is neutral

    Parameters
    ----------
    rsi_dict     : dict[str, pd.Series]   ticker → RSI series
    overbought   : float  reference line (default 70)
    oversold     : float  reference line (default 30)

    Returns
    -------
    go.Figure
    """
    fig = go.Figure()

    for idx, (ticker, rsi) in enumerate(rsi_dict.items()):
        rsi = rsi.dropna()
        if rsi.empty:
            continue

        fig.add_trace(
            go.Scatter(
                x=rsi.index,
                y=rsi.values,
                mode="lines",
                name=ticker,
                line=dict(color=_ticker_colour(idx), width=2),
                hovertemplate=(
                    f"<b>{ticker}</b><br>"
                    "Date: %{x|%Y-%m-%d}<br>"
                    "RSI(14): %{y:.1f}<extra></extra>"
                ),
            )
        )

    # Overbought / oversold bands
    fig.add_hrect(
        y0=overbought, y1=100,
        fillcolor="rgba(231,76,60,0.08)",
        line_width=0,
        annotation_text="Overbought",
        annotation_position="right",
    )
    fig.add_hrect(
        y0=0, y1=oversold,
        fillcolor="rgba(46,204,113,0.08)",
        line_width=0,
        annotation_text="Oversold",
        annotation_position="right",
    )
    fig.add_hline(y=overbought, line_dash="dash", line_color="rgba(231,76,60,0.5)", line_width=1)
    fig.add_hline(y=oversold,   line_dash="dash", line_color="rgba(46,204,113,0.5)",  line_width=1)
    fig.add_hline(y=50,         line_dash="dot",  line_color="rgba(180,180,180,0.4)", line_width=1)
    fig.update_traces(line=dict(width=2, shape="spline"))
    fig.update_layout(
        title="RSI (14-Day Relative Strength Index)",
        xaxis_title="Date",
        yaxis_title="RSI",
        yaxis=dict(range=[0, 100]),
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(size=13),
        margin=dict(t=60, b=40, l=60, r=20),
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=True, gridcolor="rgba(255,255,255,0.05)"")

    return fig


# ─────────────────────────────────────────────────────────────────────────────
# 3. Volume + 20-day MA
# ─────────────────────────────────────────────────────────────────────────────

def plot_volume(
    price_data: dict[str, pd.DataFrame],
    ma_window: int = 20,
) -> go.Figure:
    """
    Render volume bars alongside their 20-day simple moving average.

    Why a volume MA?
    ────────────────
    Raw volume is very noisy.  A 20-day SMA (Simple Moving Average) smooths
    out day-to-day variation and reveals the underlying trend in trading
    activity.  A spike of volume far above the MA typically confirms a
    significant price move; low volume during a rally may signal weakness.

    Parameters
    ----------
    price_data : dict[str, pd.DataFrame]
        Mapping  ticker → DataFrame with at least a "Volume" column.
    ma_window  : int
        Moving-average period (default 20 trading days ≈ one calendar month).

    Returns
    -------
    go.Figure
        One row per ticker in a vertically stacked subplot layout.
    """
    tickers = [t for t, df in price_data.items() if "Volume" in df.columns]
    if not tickers:
        fig = go.Figure()
        fig.update_layout(title="No volume data available.")
        return fig

    n = len(tickers)
    fig = make_subplots(
        rows=n, cols=1,
        shared_xaxes=True,
        subplot_titles=[f"{t} – Volume" for t in tickers],
        vertical_spacing=0.06,
    )

    for row_idx, ticker in enumerate(tickers, start=1):
        df = price_data[ticker]
        vol = df["Volume"].dropna()
        ma  = vol.rolling(window=ma_window, min_periods=1).mean()
        colour = _ticker_colour(row_idx - 1)

        # Volume bars
        # fig.add_trace(
        #     go.Bar(
        #         x=vol.index,
        #         y=vol.values,
        #         name=f"{ticker} Volume",
        #         marker_color=colour,
        #         opacity=0.4,
        #         showlegend=(row_idx == 1),
        #         hovertemplate=(
        #             f"<b>{ticker}</b><br>"
        #             "Date: %{x|%Y-%m-%d}<br>"
        #             "Volume: %{y:,.0f}<extra></extra>"
        #         ),
        #     ),
        #     row=row_idx, col=1,
        # )

        # glow layer
        fig.add_trace(
            go.Scatter(
                x=series.index,
                y=series.values,
                mode="lines",
                line=dict(color=_ticker_colour(idx), width=6),
                opacity=0.25,
                showlegend=False
            )
        )

        # 20-day MA line
        fig.add_trace(
            go.Scatter(
                x=ma.index,
                y=ma.values,
                mode="lines",
                name=f"{ticker} MA({ma_window})",
                # line=dict(color=colour, width=2, dash="solid"),
                line=dict(
                    color=_ticker_colour(idx),
                    width=2,
                    shape="spline"   # smooth curve
                )
                hovertemplate=(
                    f"<b>{ticker}</b> MA({ma_window})<br>"
                    "Date: %{x|%Y-%m-%d}<br>"
                    "Avg Vol: %{y:,.0f}<extra></extra>"
                ),
            ),
            row=row_idx, col=1,
        )

    fig.update_layout(
        title=f"Trading Volume & {ma_window}-Day Moving Average",
        hovermode="x unified",
        # plot_bgcolor="rgba(0,0,0,0)",
        # paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#0E1117",
        paper_bgcolor="#0E1117",
        font=dict(size=13),
        height=250 * n + 80,
        margin=dict(t=60, b=40, l=70, r=20),
        bargap=0.1,
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=True, gridcolor="rgba(255,255,255,0.05)"")

    return fig
