# example streamlit app
```python
import streamlit as st
from streamlit_custom_grid import st_custom_grid

st.title("Testing Streamlit custom components")

v = st_custom_grid("http://localhost:8000/grid-data", 2,0,"")
st.write(v)
```

# example fastAPI server
```python
from fastapi import FastAPI
import pandas as pd
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import random
from constant import json_data

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/grid-data")
async def read_data():
    json_data['honey']= random.randrange(10)
    return json_data
# uvicorn server:app --reload
```