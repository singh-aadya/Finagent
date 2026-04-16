import streamlit as st

st.set_page_config(page_title="Learn Stocks", layout="wide")

st.title("📘 Learn Stocks (Simple Guide)")
st.markdown("Understand stock market in the easiest way possible.")

# -------------------------------
# Helper function for clean UI
# -------------------------------
def show_term(title, meaning, example, tip):
    with st.expander(f"📌 {title}"):
        st.markdown(f"**What it means:** {meaning}")
        st.markdown(f"**Example:** {example}")
        st.markdown(f"**Simple tip:** {tip}")

# -------------------------------
# TERMS
# -------------------------------

show_term(
    "Stock",
    "A small ownership in a company.",
    "Buying Apple stock means you own a tiny part of Apple.",
    "Good companies grow → your money grows."
)

show_term(
    "Price",
    "Current value of the stock.",
    "If a stock is ₹100 today and ₹120 tomorrow → profit.",
    "Buy low, sell high."
)

show_term(
    "P/E Ratio",
    "Tells if a stock is expensive or cheap.",
    "P/E = 30 means people are paying 30x the company earnings.",
    "High P/E → expensive, Low P/E → cheaper (but check quality)."
)

show_term(
    "RSI (Relative Strength Index)",
    "Shows if stock is overbought or oversold.",
    "RSI > 70 → too high, RSI < 30 → cheap",
    "Buy when low, be careful when high."
)

show_term(
    "Volume",
    "Number of shares traded.",
    "High volume = strong movement.",
    "Big moves with high volume are more reliable."
)

show_term(
    "Trend",
    "Direction of stock price.",
    "Uptrend → going up 📈, Downtrend → going down 📉",
    "Follow the trend, don’t fight it."
)

show_term(
    "Bullish",
    "Market going up.",
    "People are buying more → price rising.",
    "Good time to invest carefully."
)

show_term(
    "Bearish",
    "Market going down.",
    "People are selling → price falling.",
    "Better to wait or be cautious."
)

show_term(
    "Market Cap",
    "Size of the company.",
    "Big companies = safer, small companies = risky but high growth.",
    "Beginners should prefer large companies."
)

show_term(
    "Moving Average",
    "Average price over time.",
    "Smooths out price noise.",
    "Helps identify trend direction."
)

# -------------------------------
# FINAL SIMPLE RULES
# -------------------------------

st.markdown("---")
st.subheader("🧠 Simple Rules for Beginners")

st.markdown("""
- Don’t invest blindly  
- Understand before buying  
- Start small  
- Avoid emotional decisions  
- Long-term is safer  

👉 Always remember: This is for learning, not financial advice.
""")
