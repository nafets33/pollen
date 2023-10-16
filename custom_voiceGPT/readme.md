# example streamlit app

```python
# This is a simple Python program
import streamlit as st
from custom_text import custom_text, TextOptionsBuilder

st.title("Testing Streamlit custom components")

# Add Streamlit widgets to define the parameters for the CustomSlider
to_builder = TextOptionsBuilder.create()
to_builder.configure_background_color("yellow")
to_builder.configure_text_color("#0d233a")
to_builder.configure_font_style("italic")
to = to_builder.build()
custom_text(api="http://localhost:8000/api/data/text",
                     text_size=17, refresh_sec=2, refresh_cutoff_sec=10, text_option=to)
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
