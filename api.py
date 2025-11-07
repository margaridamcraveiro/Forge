from fastapi import FastAPI

app = FastAPI()

URL = "http://localhost:8000"

@app.get("/")
def root():
    return {"response": "Hello World!"}  

@app.get("/test")
def test():
    return {"response": "received test!"}