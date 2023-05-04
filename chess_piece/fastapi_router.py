from fastapi import APIRouter, status, Header, Body
from fastapi.responses import JSONResponse
from chess_piece.fastapi_queen import get_queen_orders_json, app_Sellorder_request
# from database.schemas import UsernameSchema
import random
import json 

router = APIRouter(
    prefix="/api/data",
    tags=["auth"]
)


@router.get("/text", status_code=status.HTTP_200_OK)
def get_text():
    print("/data/text")
    n = random.randrange(100)
    return JSONResponse(content=str(n))


@router.post("/queen", status_code=status.HTTP_200_OK)
def load_queen_json(username: str=Body(...), prod: bool=Body(...), kwargs = Body(...)):
    # print("/data/queen", username, prod, kwargs)
    json_data = get_queen_orders_json(username, prod, kwargs)
    return JSONResponse(content=json_data)

@router.post("/queen_app_Sellorder_request", status_code=status.HTTP_200_OK)
def sell_order(username: str=Body(...), prod: bool=Body(...), client_order_id: str=Body(...), number_shares: int=Body(...), kwargs=Body(...)):
    # print(client_order_id, username, prod, kwargs)
    app_Sellorder_request(username, prod, client_order_id, number_shares)
    return JSONResponse(content="success")

@router.post("/update_orders", status_code=status.HTTP_200_OK)
def write_queen_order(username: str= Body(...), prod: bool= Body(...), new_data= Body(...), kwargs=Body(...)):
    # print("/update_orders", username, prod, len(new_data), kwargs)
    # print("/update_orders", kwargs["api_key"])
    ret = {"status":True, "data":{"rows_updated":len(new_data)}}
    return JSONResponse(content=str(ret))

