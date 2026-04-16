import streamlit as st

st.set_page_config(page_title="Learn Stocks", layout="wide")

st.title("📘 Learn Stocks (Simple Guide)")

st.markdown("""
### 💡 What is a Stock?
A stock means you own a small part of a company.

Example:
If you buy a stock of Apple, you own a tiny piece of Apple.

---

### 📈 What is Price?
Price = current value of the stock.

If price goes up → you profit  
If price goes down → you lose  

---

### 📊 What is RSI?
RSI tells if stock is:
- Overbought (too expensive) → may fall  
- Oversold (cheap) → may rise  

Simple:
- RSI > 70 → risky  
- RSI < 30 → good buying chance  

---

### 📦 What is Volume?
Volume = number of shares traded  

High volume = strong movement  
Low volume = weak signal  

---

### 🔄 What is Trend?
- Uptrend → price going up 📈  
- Downtrend → price going down 📉  

---

### 🧠 Simple Rule (for beginners)

- Price rising + volume high → good  
- RSI low → good buying chance  
- RSI high → be careful  

---

### ⚠️ Important

This app helps you understand  
👉 Always do your own thinking before investing
""")
