import streamlit as st
import sys, os
import google.generativeai as genai
import utils.prompts as pmt  # keeps your augmented prompt
from datetime import datetime
import pathlib
from faster_whisper import WhisperModel

# to allow import of speech_rec
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from speech_rec import application

# ---------------- Gemini defaults ----------------
DEFAULT_MODEL_NAME = "gemini-2.5-flash"
DEFAULT_TEMPERATURE = 0.7
# -------------------------------------------------


def get_client():
    """
    Initialize the Gemini client from Streamlit secrets or environment variable.
    """
    api_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        st.error(
            "❌ No Gemini API key found. Add it to .streamlit/secrets.toml "
            "or set GEMINI_API_KEY in your environment."
        )
        st.stop()
    genai.configure(api_key=api_key)
    return genai


# -------------- UI ------------------ #
st.title("Evaluate your answer")
st.write("Record your answer and listen back to it.")

# Make sure we actually have a question from the first page
if "question" not in st.session_state or not st.session_state.question:
    st.warning(
        "No interview question found in session. "
        "Go back to the first page, get a question, then return here."
    )

audio_file = st.audio_input("🎙️ Click to record your answer")

if audio_file is not None:
    st.success("Recording finished!")
    st.audio(audio_file)

    if st.button("Evaluate answer"):
        # --- Save recording ---
        out_dir = pathlib.Path("recordings")
        out_dir.mkdir(exist_ok=True)

        filename = out_dir / f"answer_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
        filename.write_bytes(audio_file.getbuffer())

        # --- Confidence evaluation ---
        lower, upper = application.initiateIntervals()
        is_confident = application.isConfident(filename, lower, upper)

        # --- Transcribe with faster-whisper ---
        model = WhisperModel("small", device="cpu")  # use "cuda" if you have a GPU
        segments, info = model.transcribe(str(filename), beam_size=5)
        transcription = "".join(segment.text for segment in segments)

        # --- Build evaluation prompt ---
        # st.session_state.question comes from the first (chat) page
        original_question = st.session_state.get("question", "")
        perfected_prompt = (
            pmt.getEvaluationPrompt(is_confident, original_question) + transcription
        )

        # --- Call Gemini: single user message, no history ---
        genai_client = get_client()
        gemini_model = genai_client.GenerativeModel(DEFAULT_MODEL_NAME)

        try:
            response = gemini_model.generate_content(
                [{"role": "user", "parts": [perfected_prompt]}],
                generation_config={"temperature": DEFAULT_TEMPERATURE},
            )
            assistant_reply = response.text or ""
        except Exception as e:
            assistant_reply = f"❗Error calling Gemini API: {e}"

        with st.chat_message("assistant"):
            st.markdown(assistant_reply)
