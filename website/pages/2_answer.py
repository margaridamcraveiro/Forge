import streamlit as st
import sys, os
import google.generativeai as genai
import website.utils.prompts as pmt  # keeps your augmented prompt
from speech_rec import application
import whisper
from datetime import datetime
import pathlib

# to allow import
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

#--------- gemini ----------#

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




st.title("Evaluate your answer")

st.write("Record your answer and listen back to it.")

audio_file = st.audio_input("🎙️ Click to record your answer")

if audio_file is not None:
    st.success("Recording finished!")
    st.audio(audio_file)
    if st.button("Evaluate answer"):
        out_dir = pathlib.Path("recordings")
        out_dir.mkdir(exist_ok=True)

        filename = out_dir / f"answer_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
        filename.write_bytes(audio_file.getbuffer())

        # get confidence evaluation
        # initialize confidence intervals
        lower, upper = application.initiateIntervals()
        is_confident = application.isConfident(filename, lower, upper)

        # get text transcription of the answer 
        model = whisper.load_model("small")
        transcription = model.transcribe(filename)
        
        # prepare your augmented prompt
        perfected_prompt = pmt.getEvaluationPrompt(is_confident, st.session_state.question) \
                    + transcription
        
        genai = get_client()
        assistant_reply = send_to_gemini(
            genai=genai,
            model_name=st.session_state.model_name,
            messages=st.session_state.messages,
            temperature=st.session_state.temperature,
        )

        with st.chat_message("assistant"):
            st.markdown(assistant_reply)