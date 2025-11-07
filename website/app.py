import os
import streamlit as st
import google.generativeai as genai
from typing import List, Dict

import utils.prompts as pmt  # keeps your augmented prompt
# Initialize keys if not already in session_state
if "question" not in st.session_state:
    st.session_state.question = ""

# -------------------- Defaults (since no settings sidebar) --------------------
DEFAULT_SYSTEM_PROMPT = "You are a helpful assistant."
DEFAULT_MODEL_NAME = "gemini-2.5-flash"
DEFAULT_TEMPERATURE = 0.7
# -----------------------------------------------------------------------------

# ---- Helpers -----------------------------------------------------------------

def get_client():
    """
    Initialize the Gemini client from Streamlit secrets or environment variable.
    """
    api_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        st.error("❌ No Gemini API key found. Add it to .streamlit/secrets.toml or environment.")
        st.stop()
    genai.configure(api_key=api_key)
    return genai


def init_state():
    # lock in defaults since we removed the sidebar controls
    if "system_prompt" not in st.session_state:
        st.session_state.system_prompt = DEFAULT_SYSTEM_PROMPT
    if "model_name" not in st.session_state:
        st.session_state.model_name = DEFAULT_MODEL_NAME
    if "temperature" not in st.session_state:
        st.session_state.temperature = DEFAULT_TEMPERATURE

    if "messages" not in st.session_state:
        st.session_state.messages: List[Dict[str, str]] = [
            {"role": "system", "content": st.session_state.system_prompt}
        ]
    # ensure system prompt is always first
    if st.session_state.messages and st.session_state.messages[0]["role"] != "system":
        st.session_state.messages.insert(0, {"role": "system", "content": st.session_state.system_prompt})


def send_to_gemini(
    genai,
    model_name: str,
    messages: List[Dict[str, str]],
    temperature: float = DEFAULT_TEMPERATURE,
) -> str:
    """
    Send messages to Gemini and return the assistant's reply.
    """
    history = [
        {"role": msg["role"], "parts": [msg["content"]]}
        for msg in messages
        if msg["role"] in ["user", "assistant"]
    ]

    try:
        model = genai.GenerativeModel(model_name)
        chat = model.start_chat(history=history)
        response = chat.send_message(messages[-1]["content"], generation_config={"temperature": temperature})
        reply = response.text or ""
    except Exception as e:
        reply = f"❗Error calling Gemini API: {e}"

    return reply


# ---- UI ----------------------------------------------------------------------

st.set_page_config(page_title="Streamlit + Gemini Chatbot", page_icon="💬", layout="centered")

st.title("💬 Streamlit Chatbot (Gemini)")

# Initialize session state
init_state()

# Render chat history (skip system message)
for msg in st.session_state.messages:
    if msg["role"] == "system":
        continue
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input
user_input = st.chat_input("Type your message…")

if user_input:
    # Prepend your augmented prompt
    perfected_prompt = pmt.AUGMENTED_PROMPT + user_input
    st.session_state.messages.append({"role": "user", "content": perfected_prompt})
    with st.chat_message("user"):
        st.markdown(user_input)

    genai = get_client()
    assistant_reply = send_to_gemini(
        genai=genai,
        model_name=st.session_state.model_name,
        messages=st.session_state.messages,
        temperature=st.session_state.temperature,
    )

    with st.chat_message("assistant"):
        st.markdown(assistant_reply)

    if assistant_reply:
        st.session_state.question = assistant_reply
        st.session_state.messages.append({"role": "assistant", "content": assistant_reply})
