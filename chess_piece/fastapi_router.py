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
active_connections = {}

async def notify_websockets(data):
    to_remove = set()
    for connection in active_connections:
        try:
            await connection.send_json(data)
        except Exception as e:
            print(f"WebSocket send error: {e}")
            to_remove.add(connection)
    for connection in to_remove:
        active_connections.remove(connection)

@router.websocket("/ws_story")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    initial_data = await websocket.receive_json()  # Receive initial data from frontend
    active_connections[websocket] = initial_data
    try:
        while True:
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        active_connections.pop(websocket, None)


async def poll_table_and_notify():
    while True:
        to_remove = set()
        # Print polling info only every 120 seconds
        if not hasattr(poll_table_and_notify, "last_print_time"):
            poll_table_and_notify.last_print_time = 0
        now = asyncio.get_event_loop().time()
        if now - poll_table_and_notify.last_print_time > 120:
            print(f"Polling active WebSocket connections... {len(active_connections)}")
            poll_table_and_notify.last_print_time = now
        for connection, initial_data in active_connections.items():
            try:
                # Customize the data you send based on initial_data
                # Example: send updates for the symbol requested by the client
                client_user = initial_data.get("username")
                print(f"Sending data to {client_user}")
                data = initial_data.get("grid", {})
                symbol = "SPY" # initial_data.get("symbol", "SPY")
                json_data = {
                    'row_id': symbol,
                    'updates': {
                        'symbol': symbol,
                        'current_ask': random.uniform(100, 200),
                        'broker_qty_delta': random.uniform(100, 200)
                    }
                }
                await connection.send_json(json_data)
            except Exception as e:
                print(f"WebSocket send error: {e}")
                to_remove.add(connection)
        for connection in to_remove:
            active_connections.pop(connection, None)
        await asyncio.sleep(3)  # Poll every 3 seconds (adjust as needed)


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


@router.post("/trig_rules", status_code=status.HTTP_200_OK)
def return_trig_rules(client_user: str=Body(...),  prod: bool=Body(...), selected_row=Body(...), default_value=Body(...), api_key=Body(...)):
    try:
        if check_authKey(api_key) == False:
            return "NOTAUTH"

        # req = app_queen_order_update_order_rules(client_user, prod, selected_row, default_value)
        req = {'status': 'success', 'description': 'No changes made', 'error': ''}
        return JSONResponse(content=grid_row_button_resp(status=req.get('status'), description=req.get('description')))
    
    except Exception as e:
        print("router queen error", e)


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
def queen_order_kors(client_user: str=Body(...), username: str=Body(...), prod: bool=Body(...), selected_row=Body(...), default_value=Body(...), api_key=Body(...)):
    try:
        if check_authKey(api_key) == False:
            return "NOTAUTH"

        req = app_queen_order_update_order_rules(client_user, prod, selected_row, default_value)
        return JSONResponse(content=grid_row_button_resp(status=req.get('status'), description=req.get('description')))
    
    except Exception as e:
        print("router queen error", e)

@router.post("/queen_sell_orders", status_code=status.HTTP_200_OK)
async def sell_order(request: Request, client_user: str=Body(...), username: str=Body(...), prod: bool=Body(...), selected_row=Body(...), default_value=Body(...), api_key=Body(...),):
    try:
        if not check_authKey(api_key):
            return "NOTAUTH"
        if request is not None and isinstance(request, Request):
            data = await request.json()
            if not data:
                return JSONResponse(content=grid_row_button_resp(status="ERROR", description="No data received"))
            # dict_keys(['username', 'prod', 'selected_row', 'default_value', 'editable_orders', 'client_user', 'return_type', 'api_lastmod_key', 'prompt_message', 'prompt_field', 'api_key', 'symbols', 'grid_height', 'toggle_views', 'allow_unsafe_jscode', 'columnOrder', 'refresh_success', 'total_col', 'subtotal_cols', 'filter_apply', 'filter_button', 'show_clear_all_filters', 'column_sets', 'show_cell_content', 'buttons'])
            client_order_id = selected_row.get('client_order_id', None)
            df = data['editable_orders']
            df_order_kors = selected_row.get('active_orders', [])
            df_order_kors = pd.DataFrame(df_order_kors)
            df = pd.DataFrame(df)
            if len(df) > 0:
                df['sell_qty'] = pd.to_numeric(df['sell_qty'], errors='coerce').fillna(0)
                df['sell_amount'] = pd.to_numeric(df['sell_amount'], errors='coerce').fillna(0)
                df_sells = df[(df['sell_qty'] > 0) | (df['sell_amount'] > 0) & (df['confirm_sell'] == True)]
                df_kors =  df[df['confirm_sell'] == True]

                if len(df_sells) > 0:
                    order_ids = df_sells['client_order_id'].tolist()
                    print("SELL", order_ids)
                elif len(df_kors) > 0:
                    df_kors['ignore_allocation_budget'] = df_kors['ignore_allocation_budget'].replace({'': False})
                    order_ids = df_kors['client_order_id'].tolist()
                    print("KORS", order_ids)
                    kors_to_compare = ['queen_order_state', 'take_profit', 'sell_out', 'close_order_today', 'sell_trigbee_date', 'ignore_allocation_budget']
                    update = False
                    default_value = {} # kors
                    reps = grid_row_button_resp(status='success', description='')
                    for idx, row in df_kors.iterrows():
                        for col in kors_to_compare:
                            if col not in df_order_kors.columns:
                                update = True
                                default_value[col] = row[col]
                                print("KORS MISMATCH Missing COL", col)
                            else: 
                                if row[col] != df_order_kors[col].iloc[idx]:
                                    update = True
                                    default_value[col] = row[col]
                                    print("KORS MISMATCH", col, row[col], df_order_kors[col].iloc[idx])
                        
                        if update:
                            print("KORS UPDATE NEEDED")
                            selected_row = {'client_order_id': row['client_order_id']} # queen_order - order_rules
                            req = app_queen_order_update_order_rules(client_user, prod, selected_row, default_value)
                            # 'status': status, # success
                            # 'description': description,
                            # 'error': error,
                            for col in ['description', 'error']:
                                if col in reps:
                                    reps[col] = f'{reps[col]} - {req.get(col)}'
                                else:
                                    reps[col] = req.get(col, '')
                    if update:
                        return JSONResponse(content=reps)
                        


            if client_order_id:
                process_type = 'specific'
            elif len(df_sells) > 0:
                process_type = 'batch'
            else:
                process_type = 'single'
            print("PROCESS TYPE", process_type)
    # Index(['ticker_time_frame', 'wave_amo', 'cost_basis_current', 'filled_qty',
    #        'qty_available', 'money', 'honey', 'queen_order_state', 'status',
    #        'macd_state', 'trigname', 'client_order_id', 'created_at', 'side',
    #        'queen_wants_to_sell_qty', 'qty', 'sell_trigbee_date', 'sell_out',
    #        'take_profit', 'close_order_today', 'sell_qty', 'sell_amount',
    #        'ignore_allocation_budget', 'confirm_sell'],
    #       dtype='object')


        # return JSONResponse(content=grid_row_button_resp())

        rep = app_Sellorder_request(client_user, prod, process_type, selected_row, default_value, df_sells)
        return JSONResponse(content=rep)

    except Exception as e:
        print("router err ", e)
        return str(e)


@router.post("/ttf_buy_orders", status_code=status.HTTP_200_OK)
async def buy_order(request: Request, client_user: str=Body(...), username: str=Body(...), prod: bool=Body(...), selected_row=Body(...), default_value=Body(...), api_key=Body(...), return_type=Body(...)):
    if not check_authKey(api_key):
        return "NOTAUTH"

    if request is not None and isinstance(request, Request):
        data = await request.json()

    print(data['default_value'].keys())
    # print(data['default_value'].keys())
    story = True
    kors = default_value
    req = app_buy_order_request(client_user, prod, selected_row, kors, story=story)
    if req.get('status'):
        return JSONResponse(content=grid_row_button_resp(description=req.get('msg')))
    else:
        return JSONResponse(content=grid_row_button_resp(status="ERROR", description=req.get('msg')))


@router.post("/queen_buy_orders", status_code=status.HTTP_200_OK)
async def buy_order(request: Request, client_user: str=Body(...), username: str=Body(...), prod: bool=Body(...), selected_row=Body(...), default_value=Body(...), api_key=Body(...)):
    if not check_authKey(api_key): # fastapi_pollenq_key
        return "NOTAUTH"

    if request is not None and isinstance(request, Request):
        data = await request.json()

    # print(data.keys())
    wave_buy_orders = data.get('editable_orders', [])

    # return JSONResponse(content=grid_row_button_resp(status="testing", description="ok"))
    story = False
    wave_buys = True
    kors = default_value
    req = app_buy_order_request(client_user, prod, selected_row, kors, story=story, wave_buy_orders=wave_buy_orders, wave_buys=wave_buys)
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

    json_data = ozz_query(text, self_image, refresh_ask, client_user, force_db_root, session_listen, before_trigger_vars, selected_actions, use_embeddings)
    return JSONResponse(content=json_data)


@router.post("/update_queenking_symbol", status_code=status.HTTP_200_OK)
def func_update_queenking_symbol(client_user: str= Body(...), prod: bool=Body(...), api_key=Body(...), selected_row=Body(...), default_value=Body(...)): # new_data for update entire row
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