# Forge
Our project wants to help people prepare to their high stakes conversations: job interviews, project discussions, and everything where what you say is not only what matters, but also HOW you say it.  
You ask our agent to give you a question, and then you answer it. The tone of your voice is then evaluated by our algorithm, and you receive feedback on the content of your answer, as well as the tone.



## activation of the environment
### Windows
python -m venv forge
.\forge\Scripts\activate
### Mac/Linux
python -m venv forge
source forge/bin/activate

## installation
pip install fastapi
pip install uvicorn
pip install streamlit
pip install librosa
pip install matplotlib
pip install numpy
pip install audiorecorder
pip install whisper
pip install faster-whisper soundfile
pip install gTTS


------
## Run API
uvicorn api:app --reload

## Run website
streamlit run website/app.py
# give me a question help in my job interview


------
## new
pip install -r requirements.txt
