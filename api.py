import asyncio
import uvicorn
from fastapi import FastAPI, status, Request
from fastapi.middleware.cors import CORSMiddleware
# from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
# from starlette.responses import RedirectResponse
# from starlette.requests import Request
import argparse
from dotenv import load_dotenv

from chess_piece import fastapi_router
from chess_piece.king import get_ip_address
from chess_piece.queen_hive import read_swarm_db

load_dotenv()
prod = True
class CacheManager:
    def __init__(self):
        self.data = {}

    async def load(self):
        # Simulate data loading
        BISHOP = "WORKERBEE" #read_swarm_db(prod=prod)
        self.data = {"BISHOP": BISHOP, "key2": "value2"}
        print("Cache initialized!")

    def get_data(self):
        return self.data


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
        "message": "Pollen Welcomes"
    }

cache_manager = CacheManager()

@app.on_event("startup")
async def startup_event():
    await cache_manager.load()
    asyncio.create_task(fastapi_router.poll_table_and_notify())


@app.get("/cachedata")
async def get_data(request: Request):
    headers = request.headers
    print(headers)  # Prints headers
    return cache_manager.get_data()

@app.get("/cachedata/{key}")
async def get_key(key: str):
    return cache_manager.get_data().get(key, "Key not found")

if __name__ == '__main__':
    def ozzapi_script_Parser():
        parser = argparse.ArgumentParser()
        parser.add_argument ('-ip', default='127.0.0.1')
        parser.add_argument ('-port', default='8000')
        return parser

    parser = ozzapi_script_Parser()
    namespace = parser.parse_args()
    ip_address = namespace.ip
    port=int(namespace.port)

    uvicorn.run(app, host=ip_address, port=port) # '10.3.144.157'






# from starlette.responses import Response

# from fastapi_cache import FastAPICache
# from fastapi_cache.backends.redis import RedisBackend
# from fastapi_cache.decorator import cache

# from redis import asyncio as aioredis

# app = FastAPI()


# @cache()
# async def get_cache():
#     return 1


# @app.get("/")
# @cache(expire=60)
# async def index():
#     return dict(hello="world")


# @app.on_event("startup")
# async def startup():
#     redis = aioredis.from_url("redis://localhost", encoding="utf8", decode_responses=True)
#     FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")