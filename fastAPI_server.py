from chess_piece import fastapi_router
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import uvicorn
from chess_piece.king import get_ip_address

load_dotenv()


origins = []

app = FastAPI()

app.include_router(fastapi_router.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", status_code=status.HTTP_200_OK, tags=["API Check"])
def check():
    return {
        "message": "Hello World!"
    }


if __name__ == '__main__':
    ip_address = get_ip_address()
    print("IP Address:", ip_address)
    uvicorn.run(app, host=ip_address, port=8000) # '10.3.144.157'