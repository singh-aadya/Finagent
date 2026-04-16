"""
utils/plots.py

Clean + Styled Plotly charts for AI Financial Dashboard
"""

from future import annotations

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# 🎨 Neon palette (clean + modern)

_PALETTE = [
"#00E5FF",  # cyan
"#FFD54F",  # yellow
"#00FFA3",  # green
"#FF4C4C",  # red
"#B388FF",  # purple
]

def _ticker_colour(idx: int) -> str:
return _PALETTE[idx % len(_PALETTE)]

# ─────────────────────────────────────────────

# 1. Normalised Prices

# ─────────────────────────────────────────────

def plot_normalised_prices(normalised: dict[str, pd.Series]) -> go.Figure:
fig = go.Figure()

```
for idx, (ticker, series) in enumerate(normalised.items()):
    series = series.dropna()
    if series.empty:
        continue

    pct_change = series.iloc[-1] - 100.0
    sign = "+" if pct_change >= 0 else ""
    label = f"{ticker} ({sign}{pct_change:.1f}%)"

    # glow
    fig.add_trace(go.Scatter(
        x=series.index,
        y=series.values,
        mode="lines",
        line=dict(color=_ticker_colour(idx), width=6),
        opacity=0.15,
        showlegend=False
    ))

    # main line
    fig.add_trace(go.Scatter(
        x=series.index,
        y=series.values,
        mode="lines",
        name=label,
        line=dict(color=_ticker_colour(idx), width=2, shape="spline"),
    ))

fig.add_hline(
    y=100,
    line_dash="dot",
    line_color="rgba(255,255,255,0.2)"
)

fig.update_layout(
    title="Normalised Price Comparison",
    plot_bgcolor="#0E1117",
    paper_bgcolor="#0E1117",
    font=dict(color="white"),
    hovermode="x unified",
    legend=dict(
        orientation="h",
        y=1.02,
        x=1,
        xanchor="right",
        bgcolor="rgba(0,0,0,0)"
    ),
    margin=dict(t=40, b=20, l=40, r=20),
)

fig.update_yaxes(gridcolor="rgba(255,255,255,0.05)")
fig.update_xaxes(showgrid=False)

return fig
```

# ─────────────────────────────────────────────

# 2. RSI

# ─────────────────────────────────────────────

def plot_rsi(rsi_dict: dict[str, pd.Series]) -> go.Figure:
fig = go.Figure()

```
for idx, (ticker, rsi) in enumerate(rsi_dict.items()):
    rsi = rsi.dropna()
    if rsi.empty:
        continue

    fig.add_trace(go.Scatter(
        x=rsi.index,
        y=rsi.values,
        mode="lines",
        name=ticker,
        line=dict(color=_ticker_colour(idx), width=2, shape="spline"),
    ))

fig.add_hline(y=70, line_dash="dash", line_color="red")
fig.add_hline(y=30, line_dash="dash", line_color="green")

fig.update_layout(
    title="RSI (14)",
    plot_bgcolor="#0E1117",
    paper_bgcolor="#0E1117",
    font=dict(color="white"),
    hovermode="x unified",
    margin=dict(t=40, b=20, l=40, r=20),
)

fig.update_yaxes(range=[0, 100], gridcolor="rgba(255,255,255,0.05)")
fig.update_xaxes(showgrid=False)

return fig
```

# ─────────────────────────────────────────────

# 3. Volume

# ─────────────────────────────────────────────

def plot_volume(price_data: dict[str, pd.DataFrame]) -> go.Figure:
tickers = [t for t, df in price_data.items() if "Volume" in df.columns]

```
fig = make_subplots(
    rows=len(tickers),
    cols=1,
    shared_xaxes=True,
    subplot_titles=tickers,
)

for row_idx, ticker in enumerate(tickers, start=1):
    df = price_data[ticker]
    vol = df["Volume"].dropna()
    ma = vol.rolling(20).mean()
    colour = _ticker_colour(row_idx - 1)

    fig.add_trace(
        go.Bar(
            x=vol.index,
            y=vol.values,
            marker_color=colour,
            opacity=0.25,
            name=ticker,
        ),
        row=row_idx, col=1
    )

    fig.add_trace(
        go.Scatter(
            x=ma.index,
            y=ma.values,
            mode="lines",
            line=dict(color=colour, width=2, shape="spline"),
            name=f"{ticker} MA",
        ),
        row=row_idx, col=1
    )

fig.update_layout(
    title="Volume + Moving Average",
    plot_bgcolor="#0E1117",
    paper_bgcolor="#0E1117",
    font=dict(color="white"),
    height=250 * len(tickers),
    margin=dict(t=40, b=20, l=40, r=20),
)

fig.update_yaxes(gridcolor="rgba(255,255,255,0.05)")
fig.update_xaxes(showgrid=False)

return fig
```
