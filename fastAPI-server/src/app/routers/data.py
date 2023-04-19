from fastapi import APIRouter, status, Header, Body
from fastapi.responses import JSONResponse
from database.queen.queries import get_queen_orders_json, app_Sellorder_request
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
def load_queen_json(username: str, prod: bool):
    print("/data/queen", username, prod)
    json_data = get_queen_orders_json(username, prod)
    return JSONResponse(content=json_data)

@router.post("/queen", status_code=status.HTTP_200_OK)
def write_queen_order(username: str= Body(...), prod: bool= Body(...), id= Body(...)):
    print("/data/queen", username, prod, id)
    return JSONResponse(content="success")

@router.get("/queen_app_Sellorder_request", status_code=status.HTTP_200_OK)
def sell_order(username: str, prod: bool, client_order_id: str, number_shares: int):
    print(client_order_id, username, prod)
    app_Sellorder_request(username, prod, client_order_id, number_shares)
    return JSONResponse(content="success")

