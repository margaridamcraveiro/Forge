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


------
## Run API
uvicorn api:app --reload

## Run website
streamlit run home.py

## make requests
