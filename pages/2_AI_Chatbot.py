from openai import OpenAI
import streamlit as st
import os
from utils.chatbot import explain_stock_concept

if st.button("🗑️ Clear Chat"):
    st.session_state.chat_history = []
    st.rerun()

st.set_page_config(page_title="AI Chatbot", layout="wide")

st.title("🤖 AI Stock Assistant")
st.markdown("Ask anything about stocks in simple language.")

# ✅ Persistent chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
    
audio_file = st.file_uploader("🎤 Upload voice (wav/mp3)", type=["wav", "mp3"])

def speech_to_text(audio_file):
    client = OpenAI(api_key=st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY"))

    with open("temp_audio.wav", "wb") as f:
        f.write(audio_file.read())

    with open("temp_audio.wav", "rb") as f:
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=f
        )

if audio_file:
    text = speech_to_text(audio_file)
    st.write("📝 You said:", text)

    response = explain_stock_concept(text)

    st.write("🤖 AI:", response)

    return transcript.text
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
