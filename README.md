# AI Financial Analysis Dashboard

> A production-ready Streamlit application that fetches live stock data,
> renders technical charts, and generates AI-powered financial reports — all
> without hard-coded secrets or notebook boilerplate.

---

## Abstract

This project converts a Jupyter notebook prototype (AutoGen + GPT-4o multi-
agent financial reporter) into a clean, modular Streamlit application.
It preserves all analytical logic — price normalisation, RSI, volume moving
averages, fundamental ratios, correlation analysis — while adding a polished
interactive UI, proper error handling, and a separation-of-concerns
architecture suitable for production deployment or cloud hosting.

---

## Introduction

Modern quantitative finance tools increasingly rely on AI to interpret raw
market data.  This dashboard bridges the gap between raw Yahoo Finance data
and human-readable insight by combining:

* **Real-time market data** via `yfinance` (no API key needed for prices)
* **Technical analysis** — RSI, price normalisation, volume moving average
* **Fundamental analysis** — P/E, Forward P/E, P/B, D/E, ROE
* **AI report generation** — structured prompt to OpenAI or Anthropic
  that encodes Legal, Consistency, Text-Alignment and Completion review
  criteria from the original AutoGen agent pipeline

---

## Problem Statement

The original notebook:

1. Required manual execution cell-by-cell
2. Embedded a live API key directly in source code (security risk)
3. Used AutoGen's non-deterministic agent loops that could get stuck
4. Had no user interface for non-technical users
5. Was impossible to deploy as a shareable web application

---

## Objectives

| # | Objective |
|---|-----------|
| 1 | Convert notebook to a deployable Streamlit app |
| 2 | Preserve ALL analysis logic (prices, indicators, fundamentals, AI report) |
| 3 | Eliminate hard-coded secrets — use `.env` pattern |
| 4 | Modular architecture with single-responsibility modules |
| 5 | Robust error handling for bad tickers, network failures, missing keys |
| 6 | Wide-layout, polished UI with interactive Plotly charts |

---

## Block Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     app.py  (Streamlit UI)                  │
│                                                             │
│  Sidebar inputs:                                            │
│  • Tickers (text)  • Date range  • AI settings  • Run btn  │
└────────────┬───────────────┬──────────────────┬────────────┘
             │               │                  │
             ▼               ▼                  ▼
     utils/data.py   utils/indicators.py  utils/plots.py
     ─────────────   ──────────────────   ──────────────
     fetch_data()    normalize_prices()   plot_normalised_prices()
     fetch_          calculate_rsi()      plot_rsi()
       fundamentals()                     plot_volume()
     get_ticker_name()
             │
             ▼
     utils/report.py
     ───────────────
     generate_report()
          │
     ┌────┴────┐
     ▼         ▼
  OpenAI    Anthropic
  API       API
```

**Data flow:**
1. User enters tickers + date range → `fetch_data()` downloads OHLCV from Yahoo Finance
2. `fetch_fundamentals()` fetches P/E, ROE, etc. per ticker
3. `normalize_prices()` creates the 100-based index for comparison
4. `calculate_rsi()` computes 14-day Wilder RSI for each ticker
5. Plotly charts are assembled and rendered in Streamlit
6. If AI report is requested, all context is serialised into a structured
   prompt and sent to OpenAI / Anthropic; the Markdown response is displayed

---

## Methodology

### Price Normalisation
Each stock's closing price series is divided by its first value and
multiplied by 100, creating a common index starting at 100.  This removes
the effect of absolute price levels and lets investors compare performance
across stocks at very different price points.

### RSI (Relative Strength Index)
Wilder's 14-day RSI is calculated using exponential smoothing:

```
avg_gain_t = (avg_gain_{t-1} × 13 + gain_t) / 14
avg_loss_t = (avg_loss_{t-1} × 13 + loss_t) / 14
RS  = avg_gain / avg_loss
RSI = 100 - (100 / (1 + RS))
```

Values above 70 signal potential overbought conditions; below 30 = oversold.

### Volume Moving Average
A 20-day Simple Moving Average (SMA) of daily trading volume smooths noise
and reveals the underlying trend in market participation.

### AI Report Generation
A structured system prompt encoding four review roles (Legal, Text-Alignment,
Consistency, Completion) is sent along with all fetched data as user context.
The model returns a self-reviewed Markdown report in one deterministic call,
replacing the non-deterministic multi-agent AutoGen loops in the notebook.

---

## Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| UI | Streamlit 1.35+ | Web app framework |
| Data | yfinance 0.2+ | Yahoo Finance API wrapper |
| Analysis | pandas, numpy | DataFrames & numerical ops |
| Charts | Plotly 5+ | Interactive visualisations |
| AI | openai / anthropic | Report generation |
| Config | python-dotenv | Secret management |

---

## Implementation

### Project Structure

```
financial-dashboard/
├── app.py                  ← Streamlit entry point + UI logic
├── requirements.txt        ← Python dependencies
├── .env.example            ← Secret template (copy → .env)
├── .gitignore
├── README.md
└── utils/
    ├── __init__.py
    ├── data.py             ← fetch_data(), fetch_fundamentals(), get_ticker_name()
    ├── indicators.py       ← normalize_prices(), calculate_rsi()
    ├── plots.py            ← plot_normalised_prices(), plot_rsi(), plot_volume()
    └── report.py           ← generate_report() → OpenAI / Anthropic
```

### Key Design Decisions

**`fetch_data`** uses `yf.download()` in a per-ticker loop (rather than
batch download) so each ticker's success/failure is handled independently —
a bad ticker won't block the others.

**`calculate_rsi`** uses `ewm(com=window-1)` which exactly reproduces
Wilder's smoothing factor of `1/window` per bar.

**`generate_report`** bakes all four reviewer roles into the system prompt
instead of running sequential agent chats, giving deterministic, fast results.

---

## Results

After running the analysis on AMD and NVDA over a 6-month window:

| Metric | AMD | NVDA |
|--------|-----|------|
| 6-month return | −18.6% | +35.5% |
| P/E Ratio | 181.3 | 55.9 |
| Forward P/E | 28.0 | 29.6 |
| Price to Book | 4.4 | 50.3 |
| Debt / Equity | 3.97 | 17.2 |
| ROE | 2.4% | 123.8% |
| Correlation | −0.077 (near zero) | |

*(Values from a September 2024 sample run; live values will differ.)*

---

## Evaluation Metrics

| Metric | Target | Notes |
|--------|--------|-------|
| Data freshness | ≤ 1 trading day | yfinance pulls real-time data |
| Chart render time | < 3 s | Plotly is client-side |
| AI report latency | 20–60 s | Depends on model and context length |
| Error coverage | All major failure modes | Bad ticker, empty data, missing key |

---

## Limitations

* Yahoo Finance data quality varies — some tickers return incomplete fundamentals
* News headlines must be pasted manually (no live news API integration)
* AI reports cost money per call (OpenAI / Anthropic usage fees apply)
* The RSI/volume charts are informational; no backtesting or signal generation

---

## Future Scope

| Feature | Description |
|---------|-------------|
| Live news API | Integrate NewsAPI or Bing News to auto-fetch headlines |
| Portfolio mode | Accept weights + compute portfolio-level metrics |
| Backtesting | Add a simple SMA/RSI strategy backtester tab |
| Cloud deploy | One-click deploy to Streamlit Cloud or GCP Cloud Run |
| Alerts | Email / Slack notifications when RSI crosses 70 / 30 |
| PDF export | Render the AI report as a styled PDF with charts embedded |

---

## References

1. Wilder, J. W. (1978). *New Concepts in Technical Trading Systems*. Trend Research.
2. yfinance documentation: https://pypi.org/project/yfinance/
3. Streamlit documentation: https://docs.streamlit.io
4. Plotly Python documentation: https://plotly.com/python/
5. OpenAI API reference: https://platform.openai.com/docs/api-reference
6. Anthropic API reference: https://docs.anthropic.com/en/api

---

## How to Run

### Windows 11 (Command Prompt / PowerShell)

```bat
REM 1. Clone or unzip the project
cd financial-dashboard

REM 2. Create & activate virtual environment
python -m venv .venv
.venv\Scripts\activate

REM 3. Install dependencies
pip install -r requirements.txt

REM 4. Create your .env file with API keys
copy .env.example .env
REM  → edit .env and add your OPENAI_API_KEY or ANTHROPIC_API_KEY

REM 5. Launch the app
streamlit run app.py
```

### macOS / Linux

```bash
# 1. Navigate to the project folder
cd financial-dashboard

# 2. Create & activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Add API keys
cp .env.example .env
# Edit .env and add your keys

# 5. Run
streamlit run app.py
```

The dashboard will open automatically at **http://localhost:8501**.

---

## VS Code Setup

1. Install the **Python** extension (ms-python.python)
2. Install the **Pylance** extension for autocomplete
3. Open the project folder: `File → Open Folder`
4. Select interpreter: `Ctrl+Shift+P` → *Python: Select Interpreter* → choose `.venv`
5. Install the **Streamlit** snippets extension (optional but helpful)
6. Run/debug: open a terminal (`Ctrl+\``) and run `streamlit run app.py`

---

## GitHub Setup

```bash
# Inside the project folder (after activating venv):
git init
git add .
git commit -m "Initial commit: AI Financial Analysis Dashboard"

# Create a new repo on GitHub (https://github.com/new), then:
git remote add origin https://github.com/YOUR_USERNAME/financial-dashboard.git
git branch -M main
git push -u origin main
```

> **Important:** `.gitignore` already excludes `.env` so your API keys are
> never pushed to GitHub.

---

*This project is for educational and informational purposes only.
It does not constitute financial advice.*