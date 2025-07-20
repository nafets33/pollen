from fastapi import APIRouter, status, Header, Body, Query, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse, FileResponse
import pandas as pd
import os
import random
from dotenv import load_dotenv
from chess_piece.fastapi_queen import *
from master_ozz.utils import init_constants
from fastapi import Request
import asyncio


# WORKERBEE FIX TO AVOID WARNING STREAMLIT ERROR..WARNING streamlit.runtime.scriptrunner_utils.script_run_context
from master_ozz.ozz_query import ozz_query
# from master_ozz.utils import ozz_master_root, init_constants

router = APIRouter(
    prefix="/api/data",
    tags=["auth"]
)

# A set to store active WebSocket connections
active_connections = set()

async def notify_websockets():
    for connection in active_connections:
        await connection.send_text("dataUpdated")

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.add(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        active_connections.remove(websocket)


def check_authKey(api_key):
    if api_key != os.environ.get("fastAPI_key"): # fastapi_pollenq_key
        print("Auth Failed", api_key)
        return False
    else:
        return True

@router.get("/local/{file_name}")
def get_file(file_name: str):
    print("GET FILE", file_name)
    constants = init_constants()
    OZZ_db_audio = constants.get('OZZ_db_audio')
    OZZ_db_images = constants.get('OZZ_db_images')
    file_path = os.path.join(OZZ_db_audio, file_name)
    
    # Determine the media type based on the file extension
    media_type = "application/octet-stream"
    if file_name.lower().endswith(".mp3"):
        media_type = "audio/mp3"
        file_path = os.path.join(OZZ_db_audio, file_name)
    elif file_name.lower().endswith(".png"):
        media_type = "image/png"
        file_path = os.path.join(OZZ_db_images, file_name)
    elif file_name.lower().endswith(".gif"):
        media_type = "image/gif"
        file_path = os.path.join(OZZ_db_images, file_name)

    return FileResponse(file_path, media_type=media_type)

@router.get("/test", status_code=status.HTTP_200_OK)
def load_ozz_voice():
    json_data = {'msg': 'test'}
    return JSONResponse(content=json_data)

@router.get("/lastmod_key", status_code=status.HTTP_200_OK)
def get_revrec_lastmod(client_user: str = Query(...), prod: bool = Query(...), api_key: str = Query(...), api_lastmod_key: str = Query(...)):
    if check_authKey(api_key):
        json_data = get_revrec_lastmod_time(client_user, prod, api_lastmod_key)
        return JSONResponse(content=json_data)
    else:
        return "NOAUTH"


@router.post("/voiceGPT", status_code=status.HTTP_200_OK)
def load_ozz_voice(api_key=Body(...), text=Body(...), self_image=Body(...), refresh_ask=Body(...), face_data=Body(...), client_user=Body(...), force_db_root=Body(...), session_listen=Body(...), before_trigger_vars=Body(...), tigger_type=Body(...)):
    # print(f'face data {face_data}')
    print(f'trig TYPE: {tigger_type}')
    
    if api_key != os.environ.get("ozz_key"): # fastapi_pollenq_key
        print("Auth Failed", api_key)
        # Log the trader WORKERBEE
        return "NOTAUTH"

    json_data = ozz_query(text, self_image, refresh_ask, client_user, force_db_root, session_listen, before_trigger_vars)
    return JSONResponse(content=json_data)

@router.post("/wave_stories", status_code=status.HTTP_200_OK)
def load_wavestories_json(client_user: str=Body(...), symbols: list=Body(...), toggle_view_selection: str=Body(...), prod: bool=Body(...), api_key = Body(...), return_type = Body(...)):
    try:
        if api_key != os.environ.get("fastAPI_key"): # fastapi_pollenq_key
            print("Auth Failed", api_key)
            return "NOTAUTH"
        json_data = queen_wavestories__get_macdwave(client_user, prod, symbols, toggle_view_selection, return_type=return_type)
        # print(json_data)
        return JSONResponse(content=json_data)
    except Exception as e:
        print(e)


@router.post("/story", status_code=status.HTTP_200_OK)
def load_story_json(client_user: str=Body(...), toggle_view_selection: str=Body(...), symbols: list=Body(...), prod: bool=Body(...), api_key = Body(...)):
    try:
        if api_key != os.environ.get("fastAPI_key"): # fastapi_pollenq_key
            print("Auth Failed", api_key)
            return "NOTAUTH"
        json_data = queen_wavestories__get_macdwave(client_user, prod, symbols, toggle_view_selection, return_type='story')
        # print(json_data)
        return JSONResponse(content=json_data)
    except Exception as e:
        print(e)

@router.post("/chessboard", status_code=status.HTTP_200_OK)
def load_chessboard_view_json(client_user: str=Body(...), toggle_view_selection: str=Body(...), symbols: list=Body(...), prod: bool=Body(...), api_key = Body(...)):
    try:
        if api_key != os.environ.get("fastAPI_key"): # fastapi_pollenq_key
            print("Auth Failed", api_key)
            return "NOTAUTH"
        json_data = chessboard_view(client_user, prod, symbols, toggle_view_selection,)
        return JSONResponse(content=json_data)
    except Exception as e:
        print(e)

@router.post("/account_header", status_code=status.HTTP_200_OK)
def load_account_header(client_user: str=Body(...),prod: bool=Body(...), api_key = Body(...)):
    if check_authKey(api_key):
        json_data = header_account(client_user, prod)
        return JSONResponse(content=json_data)
    else:
        return "NOAUTH"



@router.post("/ticker_time_frame", status_code=status.HTTP_200_OK)
def load_trinity_graph(api_key=Body(...), symbols=Body(...), toggles_selection=Body(...)):
    
    if api_key != os.environ.get("fastAPI_key"): # fastapi_pollenq_key
        print("Auth Failed", api_key)
        return "NOTAUTH"
    json_data = get_ticker_time_frame(symbols, toggles_selection)
    return JSONResponse(content=json_data)

@router.post("/symbol_graph", status_code=status.HTTP_200_OK)
def load_symbol_graph(symbols: list=Body(...), prod: bool=Body(...), api_key=Body(...), toggles_selection=Body(...)):
    if api_key != os.environ.get("fastAPI_key"): # fastapi_pollenq_key
        print("Auth Failed", api_key)
        return "NOTAUTH"
    json_data = get_ticker_data(symbols, toggles_selection)
    return JSONResponse(content=json_data)


# @router.post("/symbol_graph_candle_stick", status_code=status.HTTP_200_OK)
# def load_symbol_graph(selectedOption: list=Body(...), prod: bool=Body(...), api_key=Body(...)):
#     if api_key != os.environ.get("fastAPI_key"): # fastapi_pollenq_key
#         print("Auth Failed", api_key)
#         return "NOTAUTH"
#     json_data = get_ticker_data_candle_stick(selectedOption)
#     return JSONResponse(content=json_data)



@router.post("/queen_messages_logfile", status_code=status.HTTP_200_OK)
def load_queen_messages_logfile_json(username: str=Body(...), api_key = Body(...), log_file=Body(...)):
    if api_key != os.environ.get("fastAPI_key"): # fastapi_pollenq_key
        print("Auth Failed", api_key)
        return "NOTAUTH"
    json_data = get_queen_messages_logfile_json(username, log_file)
    return JSONResponse(content=json_data)


@router.post("/queen", status_code=status.HTTP_200_OK)
def load_queen_json(client_user: str=Body(...), username: str=Body(...), prod: bool=Body(...), api_key = Body(...), toggle_view_selection=Body(...)):
    try:
        if api_key != os.environ.get("fastAPI_key"): # fastapi_pollenq_key
            print("Auth Failed", api_key)
            return "NOTAUTH"
        json_data = get_queen_orders_json(client_user, username, prod, toggle_view_selection)
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
        return JSONResponse(content=grid_row_button_resp())
    except Exception as e:
        print("router queen error", e)
        return JSONResponse(content=grid_row_button_resp(status='error'))

@router.post("/update_queen_order_kors", status_code=status.HTTP_200_OK)
def archive_queen_order(client_user: str=Body(...), username: str=Body(...), prod: bool=Body(...), selected_row=Body(...), default_value=Body(...), api_key=Body(...)):
    try:
        if check_authKey(api_key) == False:
            return "NOTAUTH"

        req = app_queen_order_update_order_rules(client_user, username, prod, selected_row, default_value)
        if req.get('status'):
            return JSONResponse(content=grid_row_button_resp(description=req.get('description')))
        else:
            return JSONResponse(content=grid_row_button_resp(status='error', description=req.get('description')))
        # json_data = app_archive_queen_order(username, prod, selected_row, default_value)
        # app_queen_order_update_order_rules(username, prod, selected_row, default_value)
    except Exception as e:
        print("router queen error", e)

@router.post("/queen_sell_orders", status_code=status.HTTP_200_OK)
async def sell_order(request: Request, client_user: str=Body(...), username: str=Body(...), prod: bool=Body(...), selected_row=Body(...), default_value=Body(...), api_key=Body(...),):
    try:
        if request is not None and isinstance(request, Request):
            data = await request.json()
            df = data['default_value'].get('active_orders_with_qty', [])
            df = pd.DataFrame(df)
            if len(df) > 0:
                df['sell_qty'] = pd.to_numeric(df['sell_qty'], errors='coerce')
                df = df[df['sell_qty'] > 0]
                if len(df) > 0:
                    order_ids = df['client_order_id'].tolist()
                    print("selected ORDER IDs to sell", order_ids)
            # print("Request body as dict:", data.keys())
            # print(data['buttons']) # remove the parts fo the body not needed ? promptText WORKERBEE
            # print(data['default_value']['active_orders_with_qty']) # it has the orders --- selling can be done then with either OR not BOTH

        if not check_authKey(api_key):
            return "NOTAUTH"

        rep = app_Sellorder_request(client_user, username, prod, selected_row, default_value)
        # rep = grid_row_button_resp() # TESING 
        return JSONResponse(content=rep)

    except Exception as e:
        print("router err ", e)
        return str(e)


@router.post("/ttf_buy_orders", status_code=status.HTTP_200_OK)
def buy_order(client_user: str=Body(...), username: str=Body(...), prod: bool=Body(...), selected_row=Body(...), default_value=Body(...), api_key=Body(...), return_type=Body(...)):
    if not check_authKey(api_key):
        return "NOTAUTH"
    story = True
    kors = default_value
    req = app_buy_order_request(client_user, prod, selected_row, kors, story=story)
    if req.get('status'):
        return JSONResponse(content=grid_row_button_resp(description=req.get('msg')))
    else:
        return JSONResponse(content=grid_row_button_resp(status="ERROR", description=req.get('msg')))


@router.post("/queen_buy_orders", status_code=status.HTTP_200_OK)
def buy_order(client_user: str=Body(...), username: str=Body(...), prod: bool=Body(...), selected_row=Body(...), default_value=Body(...), api_key=Body(...)):
    if not check_authKey(api_key): # fastapi_pollenq_key
        return "NOTAUTH"
    story = False
    kors = default_value
    req = app_buy_order_request(client_user, prod, selected_row, kors, story=story)
    if req.get('status'):
        return JSONResponse(content=grid_row_button_resp(description=req.get('msg')))
    else:
        return JSONResponse(content=grid_row_button_resp(status="ERROR", description=req.get('msg')))



@router.post("/update_orders", status_code=status.HTTP_200_OK)
def write_queen_order(username: str= Body(...), prod: bool= Body(...), new_data= Body(...), api_key=Body(...)):
    if not check_authKey(api_key): # fastapi_pollenq_key
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


@router.get("/", status_code=status.HTTP_200_OK)
def check_api():
    print("online")
    return JSONResponse(content="online")

@router.post("/update_queenking_chessboard", status_code=status.HTTP_200_OK)
async def update_qk_chessboard(client_user: str= Body(...), prod: bool=Body(...), api_key=Body(...), selected_row=Body(...), default_value=Body(...)): # new_data for update entire row
    if api_key != os.environ.get("fastAPI_key"): # fastapi_pollenq_key
        print("Auth Failed", api_key)
        return "NOTAUTH"
    
    # print("/data/queen", username, prod, kwargs)
    json_data = update_queenking_chessboard(client_user, prod, selected_row, default_value)
    # await notify_websockets()
    return JSONResponse(content=json_data)


@router.post("/update_buy_autopilot", status_code=status.HTTP_200_OK)
async def buy_autopilot(client_user: str= Body(...), prod: bool=Body(...), api_key=Body(...), selected_row=Body(...), default_value=Body(...)): # new_data for update entire row
    if not check_authKey(api_key): # fastapi_pollenq_key
        return "NOTAUTH"
    
    json_data = update_buy_autopilot(client_user, prod, selected_row, default_value)
    # await notify_websockets()
    return JSONResponse(content=json_data)

@router.post("/update_sell_autopilot", status_code=status.HTTP_200_OK)
def sell_autopilot(client_user: str= Body(...), prod: bool=Body(...), api_key=Body(...), selected_row=Body(...), default_value=Body(...)): # new_data for update entire row
    if not check_authKey(api_key): # fastapi_pollenq_key
        return "NOTAUTH"
    json_data = update_sell_autopilot(client_user, prod, selected_row, default_value)
    return JSONResponse(content=json_data)

@router.post("/voiceGPT", status_code=status.HTTP_200_OK)
async def load_ozz_voice(request: Request, api_key=Body(...), text=Body(...), self_image=Body(...), refresh_ask=Body(...), face_data=Body(...), client_user=Body(...), force_db_root=Body(...), session_listen=Body(...), before_trigger_vars=Body(...), tigger_type=Body(...)):
    # Print the entire body of the POST request
    body = await request.json()
    print("Full Request Body:", body)
    selected_actions = body.get('selected_actions', [])
    use_embeddings = body.get('use_embeddings', [])

    print(f'trig TYPE: {tigger_type} {before_trigger_vars}')
    
    if api_key != os.environ.get("ozz_key"): # fastapi_pollenq_key
        print("Auth Failed", api_key)
        return "NOTAUTH"

    # json_data = ozz_query(text, self_image, refresh_ask, client_user, force_db_root, session_listen, before_trigger_vars, selected_actions, use_embeddings)
    return JSONResponse(content=json_data)


@router.post("/update_queenking_symbol", status_code=status.HTTP_200_OK)
def sell_autopilot(client_user: str= Body(...), prod: bool=Body(...), api_key=Body(...), selected_row=Body(...), default_value=Body(...)): # new_data for update entire row
    if not check_authKey(api_key): # fastapi_pollenq_key
        return "NOTAUTH"
    json_data = queenking_symbol(client_user, prod, selected_row, default_value)
    return JSONResponse(content=json_data)


#### WORKERBEE
@router.post("/queen_buy_wave_orders", status_code=status.HTTP_200_OK)
def buy_order(client_user: str=Body(...), prod: bool=Body(...), selected_row=Body(...), default_value=Body(...), api_key=Body(...)):
    if api_key != os.environ.get("fastAPI_key"): # fastapi_pollenq_key
        print("Auth Failed", api_key)
        return "NOTAUTH"

    if app_buy_wave_order_request(client_user, prod, selected_row, default_value=default_value, ready_buy=False):
        return JSONResponse(content=grid_row_button_resp())
    else:
        return JSONResponse(content=grid_row_button_resp(status='error', message_type='click'))