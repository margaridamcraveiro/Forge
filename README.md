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


------
## Run
one terminal (the server):
uvicorn main:app