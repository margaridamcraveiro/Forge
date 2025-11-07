import streamlit as st

st.title("Evaluate your answer")

st.write("Record your answer and listen back to it.")

audio_file = st.audio_input("🎙️ Click to record your answer")

if audio_file is not None:
    st.success("Recording finished!")
    st.audio(audio_file)
    if st.button("Evaluate answer"):
        from datetime import datetime
        import pathlib

        out_dir = pathlib.Path("recordings")
        out_dir.mkdir(exist_ok=True)

        filename = out_dir / f"answer_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
        filename.write_bytes(audio_file.getbuffer())
        st.info(f"Saved as: {filename}")
