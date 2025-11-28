from fastapi import APIRouter, status, Header, Body, Query, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse, FileResponse
from dotenv import load_dotenv
from fastapi import Request

import asyncio
from typing import Dict, Set, Optional
import os
import random
import pandas as pd

from master_ozz.utils import init_constants
from master_ozz.ozz_query import ozz_query
from chess_piece.fastapi_queen import *
from chess_utils.websocket_manager import manager
from chess_utils.websocket_updates import send_story_grid_update

router = APIRouter(
    prefix="/api/data",
    tags=["auth"]
)

@router.get("/debug/active_connections")
async def debug_active_connections():
    """Debug: Show raw active connections data."""
    connections_debug = []
    
    async with manager.lock:
        for ws, info in manager.active_connections.items():
            connections_debug.append({
                'websocket_id': id(ws),
                'websocket_state': str(ws.client_state) if hasattr(ws, 'client_state') else 'unknown',
                'stored_data': info,
                'keys_in_data': list(info.keys()),
            })
    
    return {
        "total_connections": len(manager.active_connections),
        "raw_connections": connections_debug,
        "timestamp": datetime.now(est).isoformat()
    }

### NEW WEBSOCKET CODE FOR EVENT-DRIVEN UPDATES ###
# ✅ Store active WebSocket connections by username
active_connections: Dict[str, Set[WebSocket]] = {}

@router.websocket("/ws_story")
async def websocket_story_endpoint(websocket: WebSocket):
    client_user = None
    toggle_view = None
    
    try:
        await websocket.accept()
        logging.info(f"✅ WebSocket accepted")
        
        # Receive handshake
        data = await websocket.receive_text()
        handshake = json.loads(data)
        logging.info(f"📦 Handshake: {handshake}")
        
        client_user = handshake.get('username')
        toggle_view = handshake.get('toggle_view_selection', 'queen')
        api_key = handshake.get('api_key')
        
        # Validate
        if not client_user:
            logging.error("❌ No username in handshake")
            await websocket.send_text(json.dumps({
                'type': 'error',
                'message': 'username required'
            }))
            await websocket.close()
            return
        
        if api_key != os.getenv('fastAPI_key'):
            logging.error(f"❌ Invalid API key")
            await websocket.send_text(json.dumps({
                'type': 'error',
                'message': 'Invalid API key'
            }))
            await websocket.close()
            return
        
        # Register connection
        await manager.connect(websocket, {
            'username': client_user,
            'toggle_view_selection': toggle_view,
            'connected_at': str(datetime.now())
        })
        
        logging.info(f"✅ Registered {client_user} in manager")
        logging.info(f"📊 Total connections: {len(manager.active_connections)}")
        
        # Send confirmation
        await websocket.send_text(json.dumps({
            'type': 'connection_established',
            'message': f'Connected as {client_user}',
            'username': client_user
        }))
        
        # ✅ Keep alive loop - handle ping/pong
        while True:
            try:
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # ✅ Handle ping from client
                if message.get('type') == 'ping':
                    logging.debug(f"💓 Received ping from {client_user}")
                    await websocket.send_text(json.dumps({
                        'type': 'pong',
                        'timestamp': datetime.now(est).isoformat()
                    }))
                else:
                    # Handle other message types if needed
                    logging.debug(f"📨 Message from {client_user}: {str(message)[:100]}")
                    
            except WebSocketDisconnect:
                logging.info(f"🔌 {client_user} disconnected normally")
                break
            except json.JSONDecodeError as e:
                logging.warning(f"⚠️  Invalid JSON from {client_user}: {e}")
            except Exception as e:
                logging.error(f"❌ Error in message loop for {client_user}: {e}")
                break
                
    except WebSocketDisconnect:
        logging.info(f"🔌 WebSocket disconnected: {client_user}")
    except Exception as e:
        logging.error(f"❌ WebSocket error for {client_user}: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await manager.disconnect(websocket)
        logging.info(f"🗑️ Cleaned up {client_user}")


@router.post("/trigger_story_grid_update")
async def trigger_story_grid_update(request: Request):
    """
    Trigger story grid update via WebSocket.
    Called by Queen Bee after calculating revrec.
    """
    try:
        # Get payload
        body = await request.body()
        from chess_piece.pollen_db import PollenJsonDecoder
        payload = json.loads(body, cls=PollenJsonDecoder)
        
        client_user = payload.get('client_user')
        api_key = payload.get('api_key')
        # QUEEN_KING = payload.get('QUEEN_KING')
        revrec = payload.get('revrec')
        toggle_view_selection = payload.get('toggle_view_selection', 'queen')
        # qk_chessboard = payload.get('qk_chessboard')
        
        # ✅ Validate API key
        if api_key != os.getenv('fastAPI_key'):
            return {"status": "error", "message": "Invalid API key"}
        
        # ✅ Check if user is connected
        if not manager.is_connected(client_user):
            logging.warning(f"⚠️  User {client_user} not connected via WebSocket")
            return {
                "status": "warning",
                "message": f"User {client_user} not connected",
                "connected_users": manager.get_active_users()
            }
        
        # ✅ Send update
        success = await send_story_grid_update(
            client_user=client_user,
            # QUEEN_KING=QUEEN_KING,
            revrec=revrec,
            toggle_view_selection=toggle_view_selection,
            # qk_chessboard=qk_chessboard
        )
        
        if success:
            return {
                "status": "success",
                "message": f"Story grid update sent to {client_user}"
            }
        else:
            return {
                "status": "error",
                "message": f"Failed to send update to {client_user}"
            }
            
    except Exception as e:
        logging.error(f"❌ Error in trigger_story_grid_update: {e}")
        import traceback
        traceback.print_exc()
        return {
            "status": "error",
            "message": str(e)
        }

@router.get("/ws_status/{client_user}")
async def get_websocket_status(client_user: str):
    """Check if user has active WebSocket connection."""
    try:
        # ✅ Safely iterate over connections
        user_connections = []
        all_users = set()
        
        async with manager.lock:
            for ws, info in list(manager.active_connections.items()):
                client_user = info.get('username')
                if client_user:
                    all_users.add(client_user)
                    if client_user == client_user:
                        user_connections.append(ws)
        
        return {
            "client_user": client_user,
            "connected": len(user_connections) > 0,
            "connection_count": len(user_connections),
            "all_connected_users": sorted(list(all_users)),
            "total_connections": len(manager.active_connections),
            "timestamp": datetime.now(est).isoformat()
        }
    except Exception as e:
        logging.error(f"❌ Error in ws_status: {e}")
        import traceback
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )


@router.get("/ws_status")
async def get_all_websocket_status():
    """Get all active WebSocket connections."""
    try:
        users_dict = {}
        
        async with manager.lock:
            for ws, info in list(manager.active_connections.items()):
                client_user = info.get('username')
                if client_user:
                    users_dict[client_user] = users_dict.get(client_user, 0) + 1
        
        return {
            "total_users": len(users_dict),
            "total_connections": len(manager.active_connections),
            "users": users_dict,
            "timestamp": datetime.now(est).isoformat()
        }
    except Exception as e:
        logging.error(f"❌ Error in ws_status: {e}")
        import traceback
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )
### NEW WEBSOCKET CODE FOR EVENT-DRIVEN UPDATES ###


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
        json_data = get_storygauge_waveview_json(client_user, prod, symbols, toggle_view_selection, return_type=return_type)
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
        json_data = get_storygauge_waveview_json(client_user, prod, symbols, toggle_view_selection, return_type='story')
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
async def buy_order(request: Request, client_user: str=Body(...), prod: bool=Body(...), selected_row=Body(...), default_value=Body(...), api_key=Body(...)):
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
async def func_update_queenking_symbol(request: Request, client_user: str= Body(...), prod: bool=Body(...), api_key=Body(...), selected_row=Body(...), default_value=Body(...)): # new_data for update entire row
    if not check_authKey(api_key): # fastapi_pollenq_key
        return "NOTAUTH"
    if request is not None and isinstance(request, Request):
        data = await request.json()
    triggers = data.get('editable_orders', [])
    
    json_data = queenking_symbol(client_user, prod, selected_row, default_value, triggers)
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
