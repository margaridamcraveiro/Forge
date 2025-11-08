# Forge

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


------
## Run API
uvicorn api:app --reload

## Run website
streamlit run website/app.py
# give me a question help in my job interview


------
## new
pip install -r requirements.txt
