# example streamlit app
```python
# This is a simple Python program
import streamlit as st
from custom_text import custom_text

st.title("Testing Streamlit custom components")

# Add Streamlit widgets to define the parameters for the CustomSlider
label = st.sidebar.text_input('Label', 'Hello world')
min_value, max_value = st.sidebar.slider("Range slider", 0, 100, (0, 50))

# Pass the parameters inside the wrapper function
v1 = custom_text(api="http://localhost:8000/get-text/1")
st.write(v1)
v2 = custom_text(api="http://localhost:8000/get-text/2", text_size = 17, refresh_sec =2,refresh_cutoff_sec =10)
st.write(v2)
```
# example fastAPI server
```python
from fastapi import FastAPI
import pandas as pd
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/get-text/1")
async def read_data():
    return JSONResponse(content="Text from fastAPI-1")

@app.get("/get-text/2")
async def read_data():
    return JSONResponse(content="Text from fastAPI-2")
# uvicorn server:app --reload
```