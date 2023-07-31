from fastapi import APIRouter, status, Header, Body
from fastapi.responses import JSONResponse
from chess_piece.fastapi_queen import get_queen_messages_logfile_json, get_queen_messages_json, app_buy_order_request, get_queens_mind, get_queen_orders_json, app_Sellorder_request,  get_ticker_data, get_account_info, queen_wavestories__get_macdwave, app_buy_wave_order_request, app_archive_queen_order
import pandas as pd
import random
import json
import ipdb
import os

router = APIRouter(
    prefix="/api/data",
    tags=["auth"]
)


def grid_row_button_resp(status='success', description='success', message_type='fade', close_modal=True, color_text='red'):
    return {'status': status, # success / error
            'data':{
                'close_modal': close_modal, # T/F
                'color_text': color_text, #? test if it works
                'message_type': message_type # click / fade
            },
            'description': description,
            }

@router.post("/wave_stories", status_code=status.HTTP_200_OK)
def load_wavestories_json(username: str=Body(...), symbols: list=Body(...), prod: bool=Body(...), api_key = Body(...), return_type = Body(...)):
    try:
        if api_key != os.environ.get("fastAPI_key"): # fastapi_pollenq_key
            print("Auth Failed", api_key)
            return "NOTAUTH"
        json_data = queen_wavestories__get_macdwave(username, prod, symbols, return_type=return_type)
        # print(json_data)
        return JSONResponse(content=json_data)
    except Exception as e:
        print(e)

@router.post("/workerbees", status_code=status.HTTP_200_OK)
def load_workebees_json(username: str=Body(...), symbols: list=Body(...), prod: bool=Body(...), api_key = Body(...)):
    if api_key != os.environ.get("fastAPI_key"): # fastapi_pollenq_key
        print("Auth Failed", api_key)
        return "NOTAUTH"
    json_data = queen_wavestories__get_macdwave(username, prod, symbols)
    return JSONResponse(content=json_data)

@router.post("/symbol_graph", status_code=status.HTTP_200_OK)
def load_symbol_graph(symbols: list=Body(...), prod: bool=Body(...), api_key=Body(...)):
    if api_key != os.environ.get("fastAPI_key"): # fastapi_pollenq_key
        print("Auth Failed", api_key)
        return "NOTAUTH"
    json_data = get_ticker_data(symbols, prod)
    return JSONResponse(content=json_data)


@router.post("/queen_messages", status_code=status.HTTP_200_OK)
def load_queen_messages_json(username: str=Body(...), prod: bool=Body(...), api_key = Body(...)):
    if api_key != os.environ.get("fastAPI_key"): # fastapi_pollenq_key
        print("Auth Failed", api_key)
        return "NOTAUTH"
    json_data = get_queen_messages_json(username, prod)
    return JSONResponse(content=json_data)

@router.post("/queen_messages_logfile", status_code=status.HTTP_200_OK)
def load_queen_messages_logfile_json(username: str=Body(...), api_key = Body(...), log_file=Body(...)):
    if api_key != os.environ.get("fastAPI_key"): # fastapi_pollenq_key
        print("Auth Failed", api_key)
        return "NOTAUTH"
    json_data = get_queen_messages_logfile_json(username, log_file)
    return JSONResponse(content=json_data)


@router.post("/queen", status_code=status.HTTP_200_OK)
def load_queen_json(username: str=Body(...), prod: bool=Body(...), api_key = Body(...), toggle_view_selection=Body(...)):
    try:
        print(toggle_view_selection)
        if api_key != os.environ.get("fastAPI_key"): # fastapi_pollenq_key
            print("Auth Failed", api_key)
            return "NOTAUTH"
        json_data = get_queen_orders_json(username, prod, toggle_view_selection)
        return JSONResponse(content=json_data)
    except Exception as e:
        print("router queen error", e)

@router.post("/queen_archive_queen_order", status_code=status.HTTP_200_OK)
def archive_queen_order(username: str=Body(...), prod: bool=Body(...), selected_row=Body(...), default_value=Body(...), api_key=Body(...)):
    try:
        if api_key != os.environ.get("fastAPI_key"): # fastapi_pollenq_key
            print("Auth Failed", api_key)
            return "NOTAUTH"
        json_data = app_archive_queen_order(username, prod, selected_row, default_value)
        return JSONResponse(content=json_data)
    except Exception as e:
        print("router queen error", e)

@router.post("/queen_sell_orders", status_code=status.HTTP_200_OK)
def sell_order(username: str=Body(...), prod: bool=Body(...), selected_row=Body(...), default_value: int=Body(...), api_key=Body(...)):
    try:
        # print("router", username, prod, selected_row, default_value)
        if api_key != os.environ.get("fastAPI_key"): # fastapi_pollenq_key
            print("Auth Failed", api_key)
            return "NOTAUTH"

        
        # app_Sellorder_request(username, prod, selected_row, default_value)
        return JSONResponse(content=grid_row_button_resp())
    except Exception as e:
        print("router err ", e)

@router.post("/queen_buy_wave_orders", status_code=status.HTTP_200_OK)
def buy_order(username: str=Body(...), prod: bool=Body(...), selected_row=Body(...), api_key=Body(...)):
    if api_key != os.environ.get("fastAPI_key"): # fastapi_pollenq_key
        print("Auth Failed", api_key)
        return "NOTAUTH"

    app_buy_wave_order_request(username, prod, selected_row, ready_buy=False)
    return JSONResponse(content=grid_row_button_resp())

@router.post("/queen_buy_wave_orders__ready_buy", status_code=status.HTTP_200_OK)
def buy_order(username: str=Body(...), prod: bool=Body(...), selected_row=Body(...), api_key=Body(...)):
    if api_key != os.environ.get("fastAPI_key"): # fastapi_pollenq_key
        print("Auth Failed", api_key)
        return "NOTAUTH"

    app_buy_wave_order_request(username, prod, selected_row, ready_buy=True)
    return JSONResponse(content=grid_row_button_resp())

@router.post("/queen_buy_orders", status_code=status.HTTP_200_OK)
def buy_order(username: str=Body(...), prod: bool=Body(...), selected_row=Body(...), default_value: int=Body(...), api_key=Body(...)):
    if api_key != os.environ.get("fastAPI_key"): # fastapi_pollenq_key
        print("Auth Failed", api_key)
        return "NOTAUTH"

    app_buy_order_request(username, prod, selected_row, default_value)
    return JSONResponse(content="ssuccess")

@router.post("/update_orders", status_code=status.HTTP_200_OK)
def write_queen_order(username: str= Body(...), prod: bool= Body(...), new_data= Body(...), api_key=Body(...)):
    if api_key != os.environ.get("fastAPI_key"): # fastapi_pollenq_key
        print("Auth Failed", api_key)
        return "NOTAUTH"
    # print(new_data)
    df = pd.DataFrame(new_data).T
    print(df.columns)
    return JSONResponse(content=grid_row_button_resp())



# info = api.get_account()
# alpaca_acct_info = refresh_account_info(api=api)
@router.post("/text", status_code=status.HTTP_200_OK)
def get_text(api_key = Body(...)):
    print(api_key.get("prod"))
    print("/data/text")
    n = random.randrange(100)
    return JSONResponse(content=str(n))

@router.post("/account_info", status_code=status.HTTP_200_OK)
def load_account_info(kwargs=Body(...)):
    # print(kwargs)
    username=kwargs.get('username')
    prod=kwargs.get('prod')
    api_key=kwargs.get('api_key')
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

@router.get("/", status_code=status.HTTP_200_OK)
def check_api():
    print("online")
    return JSONResponse(content="online")