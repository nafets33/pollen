from fastapi import APIRouter, status, Header, Body
from fastapi.responses import JSONResponse
from chess_piece.fastapi_queen import app_buy_order_request, get_queens_mind, get_queen_orders_json, app_Sellorder_request,  get_ticker_data, get_account_info, queen_wavestories__get_macdwave
# from database.schemas import UsernameSchema
import random
import json
import ipdb
import os

router = APIRouter(
    prefix="/api/data",
    tags=["auth"]
)

@router.post("/workerbees", status_code=status.HTTP_200_OK)
def load_workebees_json(username: str=Body(...), symbols: list=Body(...), prod: bool=Body(...), api_key = Body(...)):
    json_data = queen_wavestories__get_macdwave(username, prod, symbols, api_key)
    return JSONResponse(content=json_data)

@router.post("/queen_buy_orders", status_code=status.HTTP_200_OK)
def buy_order(username: str=Body(...), prod: bool=Body(...), client_order_id: str=Body(...), number_shares: int=Body(...), api_key=Body(...)):
    if api_key != os.environ.get("fastAPI_key"): # fastapi_pollenq_key
        print("Auth Failed", api_key)
        return "NOTAUTH"
    app_buy_order_request(username, prod, client_order_id, number_shares)
    return JSONResponse(content="ssuccess")


@router.get("/text", status_code=status.HTTP_200_OK)
def get_text():
    print("/data/text")
    n = random.randrange(100)
    return JSONResponse(content=str(n))


@router.post("/queen", status_code=status.HTTP_200_OK)
def load_queen_json(username: str=Body(...), prod: bool=Body(...), api_key = Body(...)):
    # print("/data/queen", username, prod, kwargs)
    json_data = get_queen_orders_json(username, prod, api_key)
    return JSONResponse(content=json_data)

@router.post("/queen_app_Sellorder_request", status_code=status.HTTP_200_OK)
def sell_order(username: str=Body(...), prod: bool=Body(...), client_order_id: str=Body(...), number_shares: int=Body(...), api_key=Body(...)):
    if api_key != os.environ.get("fastAPI_key"): # fastapi_pollenq_key
        print("Auth Failed", api_key)
        return "NOTAUTH"
    app_Sellorder_request(username, prod, client_order_id, number_shares)
    return JSONResponse(content="ssuccess")

@router.post("/update_orders", status_code=status.HTTP_200_OK)
def write_queen_order(username: str= Body(...), prod: bool= Body(...), new_data= Body(...), api_key=Body(...)):
    if api_key != os.environ.get("fastAPI_key"): # fastapi_pollenq_key
        print("Auth Failed", api_key)
        return "NOTAUTH"
    ret = {"status":True, "data":{"rows_updated":len(new_data)}}
    return JSONResponse(content=str(ret))

@router.post("/symbol_graph", status_code=status.HTTP_200_OK)
def load_symbol_graph(symbols: list=Body(...), prod: bool=Body(...), api_key=Body(...)):
    if api_key != os.environ.get("fastAPI_key"): # fastapi_pollenq_key
        print("Auth Failed", api_key)
        return "NOTAUTH"
    json_data = get_ticker_data(symbols, prod, api_key)
    return JSONResponse(content=json_data)

# info = api.get_account()
# alpaca_acct_info = refresh_account_info(api=api)
@router.get("/account_info", status_code=status.HTTP_200_OK)
def load_account_info(username: str= Body(...), prod: bool=Body(...), api_key=Body(...)):
    if api_key != os.environ.get("fastAPI_key"): # fastapi_pollenq_key
        print("Auth Failed", api_key)
        return "NOTAUTH"
    json_data = get_account_info(username, prod)
    return JSONResponse(content=json_data)

@router.get("/queens_conscience", status_code=status.HTTP_200_OK)
def load_queens_mind(username: str= Body(...), prod: bool=Body(...), api_key=Body(...)):
    if api_key != os.environ.get("fastAPI_key"): # fastapi_pollenq_key
        print("Auth Failed", api_key)
        return "NOTAUTH"
    
    # print("/data/queen", username, prod, kwargs)
    json_data = get_queens_mind(username, prod)
    return JSONResponse(content=json_data)