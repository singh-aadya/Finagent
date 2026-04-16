"""
app.py – AI Financial Analysis Dashboard
─────────────────────────────────────────
A production-ready Streamlit application that:

  1. Accepts stock tickers and date range in the sidebar
  2. Downloads price & fundamental data via Yahoo Finance (no API key needed)
  3. Renders three interactive Plotly charts:
       • Normalised price comparison (% return)
       • RSI (14-day) with overbought / oversold bands
       • Volume bars + 20-day moving average
  4. Optionally generates an AI-powered financial report via OpenAI / Anthropic

Run with:
    streamlit run app.py
"""

from __future__ import annotations

import os
import re
from datetime import date, timedelta

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

# ── load .env (API keys etc.) before anything else ───────────────────────────
load_dotenv()

# ── local utils ──────────────────────────────────────────────────────────────
from utils.data import fetch_data, fetch_fundamentals, get_ticker_name
from utils.indicators import normalize_prices, calculate_rsi
from utils.plots import plot_normalised_prices, plot_rsi, plot_volume
from utils.report import generate_report
from utils.chatbot import explain_stock_concept   

# ─────────────────────────────────────────────────────────────────────────────
# Page config  (MUST be the first Streamlit call)
# ─────────────────────────────────────────────────────────────────────────────
# st.set_page_config(
#     page_title="AI Financial Analysis Dashboard",
#     #page_icon="📈",
#     layout="wide",
#     initial_sidebar_state="expanded",
# )

st.set_page_config(
    page_title="FinAgent",
    page_icon="📊",
    layout="wide"
)

st.sidebar.markdown(
    "<h2 style='color:#4C8BF5;'>📊 FinAgent</h2>",
    unsafe_allow_html=True
)

# ─────────────────────────────────────────────────────────────────────────────
# Minimal custom CSS – keeps styling clean without overriding Streamlit's theme
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    /* Tighten the default padding */
    .block-container { padding-top: 1.5rem; padding-bottom: 2rem; }
    /* Section headers */
    .section-header {
        font-size: 1.1rem;
        font-weight: 600;
        margin-bottom: 0.25rem;
        color: #4C8BF5;
    }
    /* Metric card label */
    .metric-label { font-size: 0.78rem; color: #999; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────────────────────────────────────
# Sidebar – user inputs
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    # st.image(
    #     "https://img.icons8.com/fluency/96/stock-market.png",
    #     width=60,
    # )
    # st.title("Settings")
    st.divider()

    # Ticker input
    st.markdown("**Stock Tickers**")
    raw_tickers = st.text_input(
        label="Enter tickers (comma-separated)",
        value="AMD, NVDA",
        help="Yahoo Finance symbols, e.g. AAPL, MSFT, TSLA",
        label_visibility="collapsed",
    )

    # Date range
    st.markdown("**Date Range**")
    col_s, col_e = st.columns(2)
    default_start = date.today() - timedelta(days=180)
    default_end   = date.today()

    start_date = col_s.date_input("Start", value=default_start, key="start")
    end_date   = col_e.date_input("End",   value=default_end,   key="end")

    # AI Report section
    st.divider()
    st.markdown("**AI Report Settings**")
    generate_ai = st.checkbox("Generate AI Report", value=False)

    ai_provider = st.selectbox(
        "Provider",
        options=["openai", "anthropic", "groq"],
        disabled=not generate_ai,
    )
    ai_model_map = {
        "openai":    ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo"],
        "anthropic": ["claude-opus-4-6", "claude-sonnet-4-6", "claude-haiku-4-5-20251001"],
        "groq": ["llama-3.3-70b-versatile"] 
    }
    ai_model = st.selectbox(
        "Model",
        options=ai_model_map[ai_provider],
        disabled=not generate_ai,
    )

    # News headlines text area (simulates Research Agent output)
    if generate_ai:
        st.markdown("**News Headlines** *(optional)*")
        st.caption("Paste headlines – one per line – to include in the AI report.")
        headlines_raw = st.text_area(
            "Headlines",
            height=120,
            label_visibility="collapsed",
            placeholder="AMD Q2 earnings beat expectations...\nNVIDIA faces DOJ antitrust inquiry...",
        )
    else:
        headlines_raw = ""

    st.divider()
    run_btn = st.button("🚀  Run Analysis", type="primary", use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
# Main area – title + placeholder
# ─────────────────────────────────────────────────────────────────────────────
st.title("📈 AI Financial Analysis Dashboard")

if not run_btn:
    st.info(
        "👈  Configure your tickers and date range in the sidebar, "
        "then press **Run Analysis**.",
        icon="ℹ️",
    )
    st.stop()

# ─────────────────────────────────────────────────────────────────────────────
# Parse & validate inputs
# ─────────────────────────────────────────────────────────────────────────────
tickers: list[str] = [
    t.strip().upper()
    for t in re.split(r"[,\s]+", raw_tickers)
    if t.strip()
]

if not tickers:
    st.error("Please enter at least one ticker symbol.")
    st.stop()

if start_date >= end_date:
    st.error("Start date must be before end date.")
    st.stop()

from datetime import datetime
start_dt = datetime.combine(start_date, datetime.min.time())
end_dt   = datetime.combine(end_date,   datetime.min.time())

# ─────────────────────────────────────────────────────────────────────────────
# Fetch data
# ─────────────────────────────────────────────────────────────────────────────
with st.spinner("Downloading price data from Yahoo Finance…"):
    try:
        price_data = fetch_data(tickers, start_dt, end_dt)
    except ValueError as exc:
        st.error(f"❌ {exc}")
        st.stop()

# Warn about tickers that returned no data
missing = [t for t in tickers if t not in price_data]
if missing:
    st.warning(
        f"No data returned for: **{', '.join(missing)}**.  "
        "These tickers have been excluded from the analysis."
    )

valid_tickers = list(price_data.keys())
if not valid_tickers:
    st.error("None of the requested tickers returned usable data.")
    st.stop()

# Fetch full company names
with st.spinner("Fetching company names…"):
    ticker_names = {t: get_ticker_name(t) for t in valid_tickers}

# Fetch fundamentals
with st.spinner("Fetching fundamental metrics…"):
    try:
        fundamentals = fetch_fundamentals(valid_tickers)
    except Exception as exc:
        st.warning(f"Could not fetch fundamental metrics: {exc}")
        fundamentals = pd.DataFrame()

# ─────────────────────────────────────────────────────────────────────────────
# Compute indicators
# ─────────────────────────────────────────────────────────────────────────────
# st.markdown("### 📊 Technical Indicators")

# Normalised prices
normalised: dict[str, pd.Series] = {}
for ticker, df in price_data.items():
    try:
        normalised[ticker] = normalize_prices(df["Close"])
    except (ValueError, KeyError):
        pass

# RSI
rsi_dict: dict[str, pd.Series] = {}
for ticker, df in price_data.items():
    try:
        rsi_dict[ticker] = calculate_rsi(df["Close"], window=14)
    except (ValueError, KeyError):
        pass

# 6-month % performance
performance: dict[str, float] = {}
for ticker, df in price_data.items():
    close = df["Close"].dropna()
    if len(close) >= 2:
        performance[ticker] = (close.iloc[-1] / close.iloc[0] - 1) * 100.0

# Correlation matrix
close_df = pd.DataFrame(
    {t: price_data[t]["Close"] for t in valid_tickers}
).dropna()
correlation = close_df.corr() if len(valid_tickers) > 1 else None

# ─────────────────────────────────────────────────────────────────────────────
# Layout – metrics row
# ─────────────────────────────────────────────────────────────────────────────
st.divider()
st.subheader("Overview")

cols = st.columns(len(valid_tickers))
for col, ticker in zip(cols, valid_tickers):
    pct = performance.get(ticker)
    close = price_data[ticker]["Close"].dropna()
    latest_price = close.iloc[-1] if not close.empty else None

    with col:
        st.markdown(f"<div class='section-header'>{ticker}</div>", unsafe_allow_html=True)
        st.caption(ticker_names.get(ticker, ticker))
        if latest_price is not None:
            st.metric(
                label="Latest Close",
                value=f"${latest_price:,.2f}",
                delta=f"{pct:+.2f}% (period)" if pct is not None else None,
            )

# ─────────────────────────────────────────────────────────────────────────────
# Fundamentals table
# ─────────────────────────────────────────────────────────────────────────────
if not fundamentals.empty:
    st.divider()
    with st.expander("📊 Fundamental Metrics", expanded=True):
        st.dataframe(
            fundamentals,
            use_container_width=True,
        )
        st.caption(
            "P/E = Price-to-Earnings | Forward P/E = consensus forward estimate | "
            "P/B = Price-to-Book | D/E = Debt-to-Equity | ROE = Return on Equity"
        )

# ─────────────────────────────────────────────────────────────────────────────
# Correlation matrix
# ─────────────────────────────────────────────────────────────────────────────
if correlation is not None:
    with st.expander("🔗 Price Correlation Matrix", expanded=False):
        st.dataframe(correlation.round(4), use_container_width=True)
        st.caption(
            "Pearson correlation of daily closing prices over the selected period. "
            "Values near +1 = highly correlated; near -1 = inverse; near 0 = uncorrelated."
        )

# ─────────────────────────────────────────────────────────────────────────────
# Charts
# ─────────────────────────────────────────────────────────────────────────────
st.divider()
st.subheader("Charts")
# st.markdown("### 📈 Stock Performance")

# Chart 1 – Normalised prices
if normalised:
    st.markdown("#### 1 – Normalised Price Comparison")
    st.caption(
        "All series rebased to 100 at period start.  "
        "Moves reflect percentage returns, not absolute prices."
    )
    st.plotly_chart(
        plot_normalised_prices(normalised),
        use_container_width=True,
    )
else:
    st.warning("Could not compute normalised prices.")

# Chart 2 – RSI
if rsi_dict:
    st.markdown("#### 2 – RSI (14-Day)")
    st.caption(
        "RSI > 70 → potentially overbought  |  RSI < 30 → potentially oversold  |  "
        "RSI ≈ 50 → neutral momentum"
    )
    st.plotly_chart(
        plot_rsi(rsi_dict),
        use_container_width=True,
    )
else:
    st.warning("Could not compute RSI.")

# Chart 3 – Volume
st.markdown("#### 3 – Volume & 20-Day Moving Average")
st.caption(
    "Bars = daily trading volume.  Line = 20-day simple moving average.  "
    "Volume spikes above the MA often confirm significant price moves."
)
st.plotly_chart(
    plot_volume(price_data, ma_window=20),
    use_container_width=True,
)

# ─────────────────────────────────────────────────────────────────────────────
# AI Report
# ─────────────────────────────────────────────────────────────────────────────

# st.markdown("### 🤖 AI Report")

if generate_ai:
    st.divider()
    st.subheader("🤖 AI Generated Financial Report")

    # Parse headlines from the text area
    news_headlines: dict[str, list[str]] = {t: [] for t in valid_tickers}
    if headlines_raw.strip():
        # Distribute headlines equally across tickers if no prefix is given
        raw_lines = [l.strip() for l in headlines_raw.splitlines() if l.strip()]
        # Try to detect "TICKER: headline" pattern
        for line in raw_lines:
            matched = False
            for ticker in valid_tickers:
                if line.upper().startswith(ticker + ":") or line.upper().startswith(ticker + " "):
                    news_headlines[ticker].append(line)
                    matched = True
                    break
            if not matched:
                # Assign to all tickers as a general market headline
                for ticker in valid_tickers:
                    news_headlines[ticker].append(line)

    with st.spinner(f"Calling {ai_provider} ({ai_model}) to generate report…  This may take 30–60 s."):
        try:
            report_md = generate_report(
                tickers=valid_tickers,
                ticker_names=ticker_names,
                fundamentals=fundamentals,
                performance=performance,
                correlation=correlation,
                news_headlines=news_headlines,
                provider=ai_provider,
                model=ai_model,
            )
            st.markdown(report_md, unsafe_allow_html=False)

            # Download button
            st.download_button(
                label="⬇️  Download Report (.md)",
                data=report_md,
                file_name="financial_report.md",
                mime="text/markdown",
            )

        except EnvironmentError as exc:
            st.error(f"🔑 API key error: {exc}")
        except ImportError as exc:
            st.error(f"📦 Missing package: {exc}")
        except RuntimeError as exc:
            st.error(f"🌐 API call failed: {exc}")
        except Exception as exc:
            st.error(f"Unexpected error: {exc}")

st.markdown("---")
st.subheader("💬 Ask AI (Learn Stocks Easily)")

# Initialize chat
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Input box
user_input = st.chat_input("Ask anything about stocks...")

if user_input:
    # Store user message
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.markdown(user_input)

    # Generate response
    response = explain_stock_concept(user_input)

    # Store bot response
    st.session_state.messages.append({"role": "assistant", "content": response})

    with st.chat_message("assistant"):
        st.markdown(response)

# ─────────────────────────────────────────────────────────────────────────────
# Footer
# ─────────────────────────────────────────────────────────────────────────────
st.divider()
st.caption(
    "Data sourced from Yahoo Finance via yfinance.  "
    "This dashboard is for informational purposes only and does not constitute "
    "financial advice.  Always consult a qualified financial advisor before making "
    "investment decisions."
)
