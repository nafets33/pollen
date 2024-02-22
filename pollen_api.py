from chess_piece import fastapi_router
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import uvicorn
from chess_piece.king import get_ip_address
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from starlette.responses import RedirectResponse
from starlette.requests import Request


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
# app.add_middleware(HTTPSRedirectMiddleware) # returned 307 temporary redirect but did not work

# @app.route('/{_:path}')
# async def https_redirect(request: Request):
#     return RedirectResponse(request.url.replace(scheme='https'))

@app.get("/", status_code=status.HTTP_200_OK, tags=["API Check"])
def check():
    return {
        "message": "Hello World!"
    }

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


if __name__ == '__main__':
    # ip_address = get_ip_address()
    # print("IP Address:", ip_address)
    ip_address = "127.0.0.1"
    uvicorn.run(app, host=ip_address, port=8000) # '10.3.144.157'