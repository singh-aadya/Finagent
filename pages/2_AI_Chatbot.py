import streamlit as st
from utils.chatbot import explain_stock_concept

st.set_page_config(page_title="AI Chatbot", layout="wide")

st.title("🤖 AI Stock Assistant")
st.markdown("Ask anything about stocks in simple language.")

# ✅ Persistent chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Show chat history
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Input
user_input = st.chat_input("Ask about stocks...")

if user_input:
    # Store user message
    st.session_state.chat_history.append({
        "role": "user",
        "content": user_input
    })

    with st.chat_message("user"):
        st.markdown(user_input)

    # AI response
    response = explain_stock_concept(user_input)

    # Store AI response
    st.session_state.chat_history.append({
        "role": "assistant",
        "content": response
    })

    with st.chat_message("assistant"):
        st.markdown(response)
