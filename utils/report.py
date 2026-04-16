"""
utils/report.py

Now supports:
- OpenAI
- Anthropic
- Groq (NEW)
- Auto fallback if one fails
"""
import streamlit as st
from __future__ import annotations
import os
import textwrap
import pandas as pd
from datetime import datetime


# ─────────────────────────────────────────────────────────────────────────────
# Helpers (unchanged)
# ─────────────────────────────────────────────────────────────────────────────
def get_key(name):
    return st.secrets.get(name) or os.getenv(name)
    
def _format_fundamentals(df: pd.DataFrame) -> str:
    return df.to_markdown() if not df.empty else "*(No fundamental data available)*"


def _format_performance(perf: dict[str, float]) -> str:
    return "\n".join(
        f"• {t}: {'+' if v >= 0 else ''}{v:.2f}%" for t, v in perf.items()
    )


def _format_correlation(corr: pd.DataFrame) -> str:
    return corr.round(4).to_markdown() if corr is not None and not corr.empty else "*(No correlation data)*"


# ─────────────────────────────────────────────────────────────────────────────
# SYSTEM PROMPT (same)
# ─────────────────────────────────────────────────────────────────────────────

_SYSTEM_PROMPT = """You are a professional financial analyst...
(keep your original system prompt here unchanged)
"""


# ─────────────────────────────────────────────────────────────────────────────
# MODEL SELECTION (NEW)
# ─────────────────────────────────────────────────────────────────────────────

# def _choose_provider(provider: str) -> str:
#     """Auto-select provider if needed."""
#     if provider != "auto":
#         return provider

#     if os.getenv("GROQ_API_KEY"):
#         return "groq"
#     if os.getenv("OPENAI_API_KEY"):
#         return "openai"
#     if os.getenv("ANTHROPIC_API_KEY"):
#         return "anthropic"

#     raise EnvironmentError("No API key found in .env")

def _choose_provider(provider: str) -> str:
    if provider != "auto":
        return provider

    if get_key("GROQ_API_KEY"):
        return "groq"
    if get_key("OPENAI_API_KEY"):
        return "openai"
    if get_key("ANTHROPIC_API_KEY"):
        return "anthropic"

    raise EnvironmentError("No API key found")


# ─────────────────────────────────────────────────────────────────────────────
# MAIN FUNCTION
# ─────────────────────────────────────────────────────────────────────────────

def generate_report(
    tickers,
    ticker_names,
    fundamentals,
    performance,
    correlation,
    news_headlines,
    provider="auto",   # 🔥 changed
    model="gpt-4o",
):
    today = datetime.now().strftime("%Y-%m-%d")

    names_block = "\n".join(f"• {t}: {ticker_names.get(t, t)}" for t in tickers)

    headlines_block = ""
    for ticker in tickers:
        headlines = news_headlines.get(ticker, [])
        headlines_block += f"\n### {ticker}\n"
        headlines_block += "\n".join(f"- {h}" for h in headlines[:10]) or "- No news"

    user_prompt = f"""
Today's date: {today}

## Tickers
{names_block}

## Fundamentals
{_format_fundamentals(fundamentals)}

## Performance
{_format_performance(performance)}

## Correlation
{_format_correlation(correlation)}

## News
{headlines_block}
"""

    provider = _choose_provider(provider)

    try:
        if provider == "groq":
            return _call_groq(user_prompt)

        elif provider == "openai":
            return _call_openai(model, user_prompt)

        elif provider == "anthropic":
            return _call_anthropic(model, user_prompt)

    except Exception as e:
        # 🔥 fallback logic
        if provider != "groq" and os.getenv("GROQ_API_KEY"):
            return _call_groq(user_prompt)

        return f"❌ AI call failed: {str(e)}"


# ─────────────────────────────────────────────────────────────────────────────
# GROQ (NEW)
# ─────────────────────────────────────────────────────────────────────────────

def _call_groq(user_prompt: str) -> str:
    #api_key = os.getenv("GROQ_API_KEY")
    api_key = get_key("GROQ_API_KEY")
    if not api_key:
        raise EnvironmentError("Missing GROQ_API_KEY")

    try:
        from groq import Groq
    except ImportError:
        raise ImportError("Install groq: pip install groq")

    client = Groq(api_key=api_key)
    

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.4,
    )

    return response.choices[0].message.content


# ─────────────────────────────────────────────────────────────────────────────
# OPENAI (same but simplified)
# ─────────────────────────────────────────────────────────────────────────────

def _call_openai(model: str, user_prompt: str) -> str:
    from openai import OpenAI

    #client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    client = OpenAI(api_key=get_key("OPENAI_API_KEY"))

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
    )

    return response.choices[0].message.content


# ─────────────────────────────────────────────────────────────────────────────
# ANTHROPIC (same)
# ─────────────────────────────────────────────────────────────────────────────

def _call_anthropic(model: str, user_prompt: str) -> str:
    import anthropic

    #client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    client = anthropic.Anthropic(api_key=get_key("ANTHROPIC_API_KEY"))

    message = client.messages.create(
        model=model,
        system=_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_prompt}],
        max_tokens=4096,
    )

    return message.content[0].text
