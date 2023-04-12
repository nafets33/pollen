# fast_api_server

from fastapi import FastAPI
import pandas as pd
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import random

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
    n = random.randrange(10)
    return JSONResponse(content=str(n))

@app.get("/get-text/2")
async def read_data():
    n = random.randrange(100)
    return JSONResponse(content=str(n))