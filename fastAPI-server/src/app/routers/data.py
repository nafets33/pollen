from fastapi import APIRouter, status, Header
from fastapi.responses import JSONResponse
from database.queen.queries import get_queen_orders_json
from database.schemas import UsernameSchema
import random

router = APIRouter(
    prefix="/api/data",
    tags=["auth"]
)


@router.get("/text", status_code=status.HTTP_200_OK)
def get_text():
    print("/data/text")
    n = random.randrange(100)
    return JSONResponse(content=str(n))


@router.get("/queen", status_code=status.HTTP_200_OK)
def load_queen_jons(username: str):
    print("/data/queen",username)
    json_data = get_queen_orders_json(username)
    return JSONResponse(content=json_data)
