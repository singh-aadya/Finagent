def explain_stock_concept(question):
    from groq import Groq
    import streamlit as st
    import os

    def get_key(name):
        return st.secrets.get(name) or os.getenv(name)

    client = Groq(api_key=get_key("GROQ_API_KEY"))

    prompt = f"""
You are a friendly teacher explaining stock market concepts.

Rules:
- Use VERY simple language
- No jargon
- Explain like teaching a villager
- Give real-life examples
- Keep it short and clear

Question:
{question}
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5,
    )

    return response.choices[0].message.content
