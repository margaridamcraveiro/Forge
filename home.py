import streamlit as st
import requests

URL = "http://localhost:8000"

st.set_page_config(
    page_title="Hello",
    page_icon="👋",
)

def get_data():
    try:
        response = requests.get(f"{URL}/test")
        return response.json()

    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

st.write("# Welcome to HR Agent!")

if st.button("Call API"):
    result = get_data()
    st.write(result)