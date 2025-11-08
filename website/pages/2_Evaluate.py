import streamlit as st
import sys, os
import google.generativeai as genai
import utils.prompts as pmt
from datetime import datetime
import pathlib
from faster_whisper import WhisperModel
from gtts import gTTS
from io import BytesIO
import re


# to allow import of speech_rec
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from speech_rec import application

# ---------------- Gemini defaults ----------------
DEFAULT_MODEL_NAME = "gemini-2.5-flash"
DEFAULT_TEMPERATURE = 0.7
# -------------------------------------------------

def clean_for_tts(text: str) -> str:
    """Strip Markdown/formatting so TTS only reads the meaningful content."""

    # 1) Remove fenced code blocks ```...```
    text = re.sub(r"```.*?```", " ", text, flags=re.DOTALL)

    # 2) Remove inline code backticks `like this`
    text = text.replace("`", "")

    # 3) Remove Markdown headings: "# Title", "## Subtitle", etc.
    text = re.sub(r"^\s*#{1,6}\s*", "", text, flags=re.MULTILINE)

    # 4) Remove blockquote markers "> "
    text = re.sub(r"^\s*>\s*", "", text, flags=re.MULTILINE)

    # 5) Remove list markers ("- ", "* ", "+ ", "1. ", "2) ", etc.) at line start
    text = re.sub(r"^\s*[-*+]\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\s*\d+[\.\)]\s+", "", text, flags=re.MULTILINE)

    # 6) Unwrap **bold** and __bold__
    text = re.sub(r"(\*\*|__)(.+?)\1", r"\2", text)

    # 7) Unwrap *italic* and _italic_
    text = re.sub(r"(\*|_)([^*_]+?)\1", r"\2", text)

    # 8) Normalize fancy quotes to normal ones (optional but helps TTS)
    text = text.replace("“", '"').replace("”", '"').replace("’", "'").replace("‘", "'")

    # 9) Collapse extra blank lines / spaces
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]{2,}", " ", text)

    return text.strip()


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

        # with st.chat_message("assistant"):
        #     st.markdown(assistant_reply)  # full Markdown, for display

        if assistant_reply:
            spoken_text = clean_for_tts(assistant_reply)
            if spoken_text:
                tts = gTTS(spoken_text, lang="en")  # or "pt", "pt-pt", etc.
                audio_bytes = BytesIO()
                tts.write_to_fp(audio_bytes)
                audio_bytes.seek(0)
                st.audio(audio_bytes, format="audio/mp3")
