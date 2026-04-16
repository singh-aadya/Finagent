# 📊 FinAgent — AI-Powered Financial Analysis Dashboard

FinAgent is a multi-agent AI system that analyzes stocks, generates insights, and presents them through an interactive dashboard. It combines data-driven analysis with AI-generated recommendations to help users make informed decisions.

---

## 🚀 Features

### 🔢 Agent 01 — Data Agent

* Computes technical indicators:

  * RSI (14-day)
  * Moving Averages (20/50/200)
  * Momentum Score (0–100)
  * Volatility (annualized)
  * Volume trends
  * Drawdown from 52-week high

---

### 🤖 Agent 02 — Insight Agent

* Powered by Groq (LLaMA models)
* Generates:

  * BUY / HOLD / SELL recommendation
  * Risk score (1–10)
  * Market sentiment (Bullish / Bearish / Neutral)
  * Key insights (3 per stock)
  * Comparative analysis
  * Better stock pick

---

### 📊 Dashboard

* Multi-panel technical chart:

  * Normalized price comparison
  * RSI analysis
  * Volume + moving average
* Clean dark UI
* KPI metrics and tables
* Downloadable charts (PNG)
* Downloadable report (JSON)

---

### 💬 AI Chatbot

* Explains stock concepts
* Answers user queries
* Gives simplified financial insights

---

### 📘 Learn Stocks Page

* Beginner-friendly explanations of:

  * P/E ratio
  * RSI
  * Volume
  * Market trends
* Designed for non-technical users

---

## 🧠 Architecture

```
User Input
   ↓
Agent 01 (Data Processing)
   ↓
Agent 02 (AI Insights via Groq)
   ↓
Dashboard + Charts + Chatbot
```

---

## 🛠️ Tech Stack

* Frontend: Streamlit
* Data: yFinance
* AI: Groq (LLaMA models)
* Visualization:

  * Plotly (interactive)
  * Matplotlib (dashboard charts)
* Backend: Python

---

## ⚙️ Setup Instructions

### 1. Clone repository

```bash
git clone https://github.com/YOUR_USERNAME/Finagent.git
cd Finagent
```

---

### 2. Create virtual environment

```bash
python -m venv .venv
.venv\Scripts\activate   # Windows
```

---

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

### 4. Add API Key

Create `.env` file:

```env
GROQ_API_KEY=your_api_key_here
```

---

### 5. Run the app

```bash
streamlit run app.py
```

---

## 🌐 Deployment (Streamlit Cloud)

1. Push code to GitHub
2. Go to Streamlit Cloud
3. Deploy your repo
4. Add secret:

```
GROQ_API_KEY = your_api_key
```

---

## 📸 Screenshots

* Dashboard with charts
* AI-generated insights
* Chatbot interface
* Learn Stocks page

(Add screenshots here)

---

## 📊 Example Output

* Recommendation: **BUY**
* Sentiment: **Bullish**
* Risk Score: **6/10**
* Insights:

  * Strong upward trend
  * Healthy volume support
  * RSI approaching overbought zone

---

## ⚠️ Disclaimer

This project is for educational purposes only.
It is NOT financial advice. Always consult a professional before investing.

---

## 👤 Author

Aadya
Engineering Student

---

## ⭐ Future Improvements

* Real-time data streaming
* Portfolio tracking
* Multi-language chatbot
* Advanced technical indicators
* TradingView-style charts

---
