from fastapi import APIRouter, status, Header, Body, Query, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse, FileResponse
from dotenv import load_dotenv
from fastapi import Request
import logging
from pydantic import BaseModel
import asyncio
from typing import Dict, Set, Optional, List, Any
import os
import random
import pandas as pd

# from master_ozz.utils import init_constants
# from master_ozz.ozz_query import ozz_query
from chess_piece.fastapi_queen import *
from chess_utils.websocket_manager import manager
from chess_utils.websocket_updates import send_story_grid_update, send_account_header_update
from chess_piece.pollen_db import PollenJsonDecoder

router = APIRouter(
    prefix="/api/data",
    tags=["auth"]
)

def check_authKey(api_key):
    if api_key != os.environ.get("fastAPI_key"): # fastapi_pollenq_key
        print("Auth Failed", api_key)
        return False
    else:
        return True

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
#  Store active WebSocket connections by username
active_connections: Dict[str, Set[WebSocket]] = {}

@router.websocket("/ws_grid")
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
        prod = handshake.get('prod', None)
        
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
            'prod': prod,
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
        payload = json.loads(body, cls=PollenJsonDecoder)
        
        client_user = payload.get('client_user')
        api_key = payload.get('api_key')
        prod = payload.get('prod')
        revrec = payload.get('revrec')
        toggle_view_selection = payload.get('toggle_view_selection', 'Portfolio')
        
        # ✅ Validate API key
        if api_key != os.getenv('fastAPI_key'):
            return {"status": "error", "message": "Invalid API key"}
        
        # ✅ Check if user is connected
        if not manager.is_connected(client_user, prod):
            # logging.warning(f"⚠️  User {client_user} not connected via WebSocket PROD: {prod}")
            return {
                "status": "warning",
                "message": f"User {client_user} not connected",
                "connected_users": manager.get_active_users()
            }
        
        # ✅ Send update
        success = await send_story_grid_update(
            client_user=client_user,
            prod=prod,
            revrec=revrec,
            toggle_view_selection=toggle_view_selection
        )
        
        if success:
            return {
                "status": "success",
                "message": f"Story grid update sent to {client_user} PROD: {prod}"
            }
        else:
            return {
                "status": "error",
                "message": f"Failed to send update to {client_user} PROD: {prod}"
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
async def get_websocket_status(client_user: str, prod: bool, request: Request = None):
    """Check if user has active WebSocket connection."""

    try:
        user_connections = []
        all_users = []
        
        async with manager.lock:
            for ws, info in list(manager.active_connections.items()):
                username = info.get('username')
                user_prod = info.get('prod')
                # print(f"prod check websocket_status: {user_prod} for user {username}")
                
                if username:
                    all_users.append({
                        'username': username,
                        'prod': user_prod,
                        'environment': "PROD" if user_prod else "SANDBOX"
                    })
                    
                    # Match username and optionally prod
                    if username == client_user:
                        if prod is None or user_prod == prod:
                            user_connections.append({
                                # 'username': username,
                                'prod': user_prod,
                                'environment': "PROD" if user_prod else "SANDBOX"
                            })
        
        return {
            "client_user": client_user,
            "connected": len(user_connections) > 0,
            "connection_count": len(user_connections),
            "connections": user_connections,
            "all_connected_users": all_users,
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

@router.post("/trigger_account_header_update")
async def trigger_account_header_update(request: Request):
    """
    Trigger account header update via WebSocket.
    Called by Queen Bee after account refresh.
    """
    try:
        body = await request.body()
        payload = json.loads(body, cls=PollenJsonDecoder)

        client_user = payload.get('client_user')
        api_key = payload.get('api_key')
        prod = payload.get('prod')
        account_rows = payload.get('account_rows')  # expected list[dict]
        toggle_view_selection = payload.get('toggle_view_selection', 'Acoount')
        row_id_field = payload.get('row_id_field', 'broker')

        # Validate API key
        if api_key != os.getenv('fastAPI_key'):
            return {"status": "error", "message": "Invalid API key"}

        # Optional fast-fail if no ws connection
        if not manager.is_connected(client_user, prod):
            print(f"User {client_user} not connected via WebSocket.")
            return {
                "status": "warning",
                "message": f"User {client_user} not connected",
                "connected_users": manager.get_active_users()
            }

        success = await send_account_header_update(
            client_user=client_user,
            prod=prod,
            account_rows=account_rows,
            toggle_view_selection=toggle_view_selection,
            row_id_field=row_id_field,
        )

        if success:
            return {
                "status": "success",
                "message": f"Account header update sent to {client_user} PROD: {prod}"
            }
        return {
            "status": "error",
            "message": f"Failed to send account header update to {client_user} PROD: {prod}"
        }

    except Exception as e:
        logging.error(f"❌ Error in trigger_account_header_update: {e}")
        print_line_of_error()
        return {
            "status": "error",
            "message": str(e)
        }

### NEW WEBSOCKET CODE FOR EVENT-DRIVEN UPDATES ###


@router.get("/", status_code=status.HTTP_200_OK)
def check_api():
    print("online")
    return JSONResponse(content="online")


# @router.get("/local/{file_name}")
# def get_file(file_name: str):
#     print("GET FILE", file_name)
#     constants = init_constants()
#     OZZ_db_audio = constants.get('OZZ_db_audio')
#     OZZ_db_images = constants.get('OZZ_db_images')
#     file_path = os.path.join(OZZ_db_audio, file_name)
    
#     # Determine the media type based on the file extension
#     media_type = "application/octet-stream"
#     if file_name.lower().endswith(".mp3"):
#         media_type = "audio/mp3"
#         file_path = os.path.join(OZZ_db_audio, file_name)
#     elif file_name.lower().endswith(".png"):
#         media_type = "image/png"
#         file_path = os.path.join(OZZ_db_images, file_name)
#     elif file_name.lower().endswith(".gif"):
#         media_type = "image/gif"
#         file_path = os.path.join(OZZ_db_images, file_name)

#     return FileResponse(file_path, media_type=media_type)

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


@router.post("/get_chessboard", status_code=status.HTTP_200_OK)
def load_chessboard_view_json(client_user: str=Body(...), prod: bool=Body(...), api_key = Body(...)):
    try:
        if api_key != os.environ.get("fastAPI_key"): # fastapi_pollenq_key
            print("Auth Failed", api_key)
            return "NOTAUTH"
        json_data = chessboard_view(client_user, prod)
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

# WORKERBEE RECONFIRM IF WORKING PROPERLY
@router.post("/update_queen_order_kors", status_code=status.HTTP_200_OK) 
def queen_order_kors(client_user: str=Body(...), username: str=Body(...), prod: bool=Body(...), selected_row=Body(...), default_value=Body(...), api_key=Body(...)):
    try:
        if check_authKey(api_key) == False:
            return "NOTAUTH"

        return JSONResponse(content=grid_row_button_resp(status="testing TBD", description="ok")) 

        req = app_queen_order_update_order_rules(client_user, prod, selected_row, default_value)
        return JSONResponse(content=grid_row_button_resp(status=req.get('status'), description=req.get('description')))
    
    except Exception as e:
        print("router queen error", e)



### MAIN 3 BUTTON CALLS ###

@router.post("/update_queenking_symbol", status_code=status.HTTP_200_OK)
async def func_update_queenking_symbol(request: Request, client_user: str= Body(...), prod: bool=Body(...), api_key=Body(...), selected_row=Body(...), default_value=Body(...), selected_data_type=Body(...)): # new_data for update entire row
    if selected_data_type != 'trig_data':
        return JSONResponse(content=grid_row_button_resp(status="ERROR", description=f"Invalid data type: {selected_data_type}"))
    
    if not check_authKey(api_key): # fastapi_pollenq_key
        return "NOTAUTH"
    if request is not None and isinstance(request, Request):
        data = await request.json()
    triggers = data.get('editable_orders', [])
    
    json_data = queenking_symbol(client_user, prod, selected_row, default_value, triggers)
    return JSONResponse(content=json_data)


@router.post("/queen_sell_orders", status_code=status.HTTP_200_OK)
async def sell_order(request: Request, client_user: str=Body(...), username: str=Body(...), prod: bool=Body(...), selected_row=Body(...), default_value=Body(...), api_key=Body(...), selected_data_type=Body(...)):
    try:
        if selected_data_type != 'active_orders':
            return JSONResponse(content=grid_row_button_resp(status="ERROR", description=f"Invalid data type: {selected_data_type}"))

        if not check_authKey(api_key):
            return "NOTAUTH"
        if request is not None and isinstance(request, Request):
            data = await request.json()
            if not data:
                return JSONResponse(content=grid_row_button_resp(status="ERROR", description="No data received"))
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
                    queenorder_fields_compare = ['queen_order_state']
                    kors_to_compare = ['queen_order_state', 'take_profit', 'sell_out', 'close_order_today', 'sell_trigbee_date', 'ignore_allocation_budget']
                    update = False
                    default_value = {} # kors
                    reps = grid_row_button_resp(status='success', description='')
                    for idx, row in df_kors.iterrows():
                        for col in kors_to_compare:
                            if col not in df_order_kors.columns and col in queenorder_fields_compare:
                                print("QUEEN ORDER UPDATE -- updating", col)
                                update = True
                                default_value[col] = row[col]
                            else:
                                if row[col] != df_order_kors[col].iloc[idx]:
                                    print("KORS CHANGED -- updating", col, row[col], df_order_kors[col].iloc[idx])
                                    update = True
                                    default_value[col] = row[col]
                        
                        if update:
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


@router.post("/queen_buy_orders", status_code=status.HTTP_200_OK)
async def buy_order(request: Request, client_user: str=Body(...), prod: bool=Body(...), selected_row=Body(...), default_value=Body(...), api_key=Body(...), selected_data_type=Body(...)):
    if not check_authKey(api_key): # fastapi_pollenq_key
        return "NOTAUTH"
    if request is not None and isinstance(request, Request):
        data = await request.json()
    # print(data.keys())
    if selected_data_type != 'wave_data':
        return JSONResponse(content=grid_row_button_resp(status="ERROR", description=f"Invalid data type: {selected_data_type}"))
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

### MAIN 3 BUTTON CALLS ###

@router.post("/ttf_buy_orders", status_code=status.HTTP_200_OK) # WORKERBEE HANDLE NEW KORS
async def buy_order(request: Request, client_user: str=Body(...), username: str=Body(...), prod: bool=Body(...), selected_row=Body(...), default_value=Body(...), api_key=Body(...)):
    if not check_authKey(api_key):
        return "NOTAUTH"

    if request is not None and isinstance(request, Request):
        data = await request.json()

    print(data['default_value'].keys())

    story = True
    kors = default_value
    req = app_buy_order_request(client_user, prod, selected_row, kors, story=story)
    if req.get('status'):
        return JSONResponse(content=grid_row_button_resp(description=req.get('msg')))
    else:
        return JSONResponse(content=grid_row_button_resp(status="ERROR", description=req.get('msg')))


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


@router.post("/queen_queenking_trigrule_event", status_code=status.HTTP_200_OK)
async def func_queen_queenking_trigger_update(client_user: str= Body(...), prod: bool=Body(...), api_key=Body(...), trigger_id=Body(...), status=Body(...)): # new_data for update entire row
    if not check_authKey(api_key): # fastapi_pollenq_key
        return "NOTAUTH"

    json_data = queen_queenking_trigger_update(client_user, prod, trigger_id, status)
    return JSONResponse(content=json_data)


@router.post("/ozz_api", status_code=status.HTTP_200_OK)
async def load_ozz_call(request: Request):

    body = await request.json()
    
    # Extract the message and any kwargs
    message = body.get('message', '')
    client_user = body.get('client_user', '')
    history = body.get('history', [])  # Message history from frontend
    
    # Process the message (your AI/chat logic here)
    response_text = f"Demo - Response: The AI will analyze your portfolio and help you with your investing strategies and even update your portfolio for you with a paid plan."  # Replace with actual logic
    # Return in role/content format matching VoiceChatModal
    return JSONResponse(content={
        "status": "success",
        "role": "assistant",
        "content": response_text,
        "timestamp": datetime.now(est).isoformat(),
    })
    
    # selected_actions = body.get('selected_actions', [])
    # use_embeddings = body.get('use_embeddings', [])

    # print(f'trig TYPE: {tigger_type} {before_trigger_vars}')
    
    # if api_key != os.environ.get("ozz_key"): # fastapi_pollenq_key
    #     print("Auth Failed", api_key)
    #     return "NOTAUTH"

    # json_data = ozz_query(text, self_image, refresh_ask, client_user, force_db_root, session_listen, before_trigger_vars, selected_actions, use_embeddings)
    # return JSONResponse(content=json_data)

@router.post("/update_cash_position", status_code=status.HTTP_200_OK)
async def update_cash_position(
    client_user: str = Body(...),
    prod: bool = Body(...),
    api_key: str = Body(...),
    cash_position: float = Body(...),
):
    if not check_authKey(api_key):
        return JSONResponse(content=grid_row_button_resp(status="error", description="NOTAUTH"))
    try:
        pq = init_queenbee(client_user, prod, queen_king=True, pg_migration=pg_migration)
        QUEEN_KING = pq['QUEEN_KING']
        QUEEN_KING['king_controls_queen']['buying_powers']['Jq']['total_longTrade_allocation'] = cash_position
        if pg_migration:
            PollenDatabase.upsert_data(QUEEN_KING.get("table_name"), QUEEN_KING.get("key"), QUEEN_KING)
        else:
            from chess_piece.king import PickleData
            PickleData(QUEEN_KING.get("source"), QUEEN_KING)
        return JSONResponse(content=grid_row_button_resp(
            status="success",
            description="Cash position saved",
            cash_position=cash_position,
        ))
    except Exception as e:
        logging.error(f"update_cash_position error: {e}")
        return JSONResponse(content=grid_row_button_resp(status="error", description=str(e)))


@router.post("/update_chess_piece", status_code=status.HTTP_200_OK)
async def update_chess_piece(
    request: Request,
    client_user: str = Body(...),
    prod: bool = Body(...),
    api_key: str = Body(...),
    action: str = Body(...),  # "save" | "delete"
    piece_name: str = Body(...),
    original_piece_name: str = Body(None),
    tickers: list = Body([]),
    ticker_allocations: dict = Body({}),  # {ticker: {buying_power, margin_power}}
    model: str = Body(...),
    theme: str = Body(...),
    buying_power: float = Body(...),
    borrow_power: float = Body(...),
    cash_position: float = Body(...),
    # margin_power: float = Body(0.0),  # If you want group-level margin
):
    """
    Add, update, or delete a chess piece with multiple tickers and per-ticker allocations.
    """

    def get_ticker_buying_powers(QUEEN_KING, symbols=[]):
        """
        Extract buying power for each ticker from trading models.
        Returns dict: {ticker: buying_power_value}
        """
        ticker_buying_powers = {}
        if not symbols:
            symbols = return_queenking_board_symbols(QUEEN_KING)
            
        for symbol in symbols:
            trading_model = QUEEN_KING['king_controls_queen']['symbols_stars_TradingModel'].get(symbol, {})
            # if trading_model:
            buying_power = trading_model.get('buyingpower_allocation_LongTerm', 0)
            margin_power = trading_model.get('buyingpower_allocation_ShortTerm', 0)
            ticker_buying_powers[symbol] = {"buying_power": buying_power, "margin_power": margin_power}

        return ticker_buying_powers

    if not check_authKey(api_key):
        return JSONResponse(content=grid_row_button_resp(status="error", description="NOTAUTH"))
    if action not in ["save", "delete"]:
        return JSONResponse(content=grid_row_button_resp(status="error", description=f"Invalid action: {action}"))
    try:
        # import ipdb
        # lets make sure all key names match
        pq = init_queenbee(client_user, prod, queen_king=True, broker_info=True, pg_migration=pg_migration)
        QUEEN_KING = pq['QUEEN_KING']
        broker_info = pq['broker_info']
        chess_board = QUEEN_KING.get("chess_board", {})



        if action == "delete":
            # Remove the piece
            if piece_name in chess_board:
                del chess_board[piece_name]
                QUEEN_KING["chess_board"] = chess_board
                # Persist
                print(f"Deleted piece '{piece_name}' from chess board.")
                if pg_migration:
                    PollenDatabase.upsert_data(QUEEN_KING.get("table_name"), QUEEN_KING.get("key"), QUEEN_KING)
                else:
                    from chess_piece.king import PickleData
                    PickleData(QUEEN_KING.get("source"), QUEEN_KING)
                return JSONResponse(content=grid_row_button_resp(status="success", description=f"Deleted '{piece_name}'", payload=chess_board))
            else:
                return JSONResponse(content=grid_row_button_resp(status="error", description=f"Piece '{piece_name}' not found"))

        # For "save" (add or update)

        # Set latest cash position
        QUEEN_KING['king_controls_queen']['buying_powers']['Jq']['total_longTrade_allocation'] = cash_position


        # If renaming, remove the old key
        if original_piece_name and original_piece_name != piece_name and original_piece_name in chess_board:
            del chess_board[original_piece_name]

        # Build the piece dict
        piece = init_qcp(
            init_macd_vars={"fast": 12, "slow": 26, "smooth": 9},
            ticker_list=tickers,
            theme=theme,
            model=model,
            piece_name=piece_name,
            buying_power=buying_power,
            borrow_power=borrow_power,
            picture="queen_png",
            # margin_power=margin_power,  # Uncomment if needed
            ticker_allocations=ticker_allocations,
        )

        chess_board[piece_name] = piece

        # Remove Any Keys that share the same tickers (case-insensitive), except for the current piece
        def normalize_ticker(ticker):
            return ticker.strip().lower()

        def tickers_equal(t1, t2):
            return sorted(normalize_ticker(t) for t in t1) == sorted(normalize_ticker(t) for t in t2)

        # Filter out duplicates except for the current piece
        filtered = {
            k: v for k, v in chess_board.items()
            if not tickers_equal(v.get("tickers", []), tickers) or k == piece_name
        }
        # Reorder so piece_name is first
        chess_board = {piece_name: filtered[piece_name], **{k: v for k, v in filtered.items() if k != piece_name}}

        QUEEN_KING["chess_board"] = chess_board
        # Ensure trading models exist for all tickers
        trading_models = QUEEN_KING.get("king_controls_queen", {}).get("symbols_stars_TradingModel", {})
        for qcp, data in chess_board.items():
            for ticker in data.get("tickers", []):
                if ticker not in trading_models:
                    QUEEN_KING = add_trading_model(QUEEN_KING=QUEEN_KING, ticker=ticker, model=model, theme=theme)
                if 'ticker_allocations' not in data:
                    tic_allocations = {}
                else:
                    tic_allocations = data['ticker_allocations']
                
                QUEEN_KING['king_controls_queen']['symbols_stars_TradingModel'][ticker]['buyingpower_allocation_LongTerm'] = tic_allocations.get(ticker, {}).get('buying_power', 0)
                QUEEN_KING['king_controls_queen']['symbols_stars_TradingModel'][ticker]['buyingpower_allocation_ShortTerm'] = tic_allocations.get(ticker, {}).get('margin_power', 0)
                ticker_allocations[ticker] = {
                    "buying_power": tic_allocations.get(ticker, {}).get('buying_power', 0),
                    "margin_power": tic_allocations.get(ticker, {}).get('margin_power', 0)
                }
        ticker_allocations = get_ticker_buying_powers(QUEEN_KING)

        # chessboard, df_qcp, df_ticker, df_stars = refresh_chess_board__revrec(
        # acct_info=broker_info, 
        # QUEEN={}, 
        # QUEEN_KING=QUEEN_KING, 
        # STORY_bee=['dummy'],
        # return_chessboard=True,
        # )

        # Persist
        if pg_migration:
            PollenDatabase.upsert_data(QUEEN_KING.get("table_name"), QUEEN_KING.get("key"), QUEEN_KING)
        else:
            from chess_piece.king import PickleData
            PickleData(QUEEN_KING.get("source"), QUEEN_KING)

        return JSONResponse(
            content=grid_row_button_resp(status=f"success", 
                                         description=f"Piece '{piece_name}' saved", 
                                         payload=chess_board, 
                                         payload_2=ticker_allocations,
                                         cash_position=cash_position,))

    except Exception as e:
        logging.error(f"update_chess_piece error: {e}")
        import traceback
        traceback.print_exc()
        return JSONResponse(content=grid_row_button_resp(status="error", description=str(e)))  


@router.post("/ticker_search_query", status_code=status.HTTP_200_OK)
async def ticker_search_query(
    client_user: str = Body(...),
    query: str = Body(...),
    prod: bool = Body(...),
    api_key: str = Body(...),
):
    """
    Returns a filtered list of tradeable ticker symbols matching `query`.
    Used by the TickerSearchModal autocomplete.
    """
    if not check_authKey(api_key):
        return JSONResponse(content={"tickers": []}, status_code=401)

    try:
        crypto_symbols = ["BTC/USD", "ETH/USD"]
        KING = kingdom__grace_to_find_a_Queen()
        all_symbols = list(KING['alpaca_symbols_dict'].keys()) + crypto_symbols

        # ticker_universe = return_Ticker_Universe()
        # all_symbols: list = list(ticker_universe.get("alpaca_symbols_dict", {}).keys()) + crypto_symbols

        q = query.strip().upper()
        # Prioritise exact prefix matches, then contains
        prefix_matches = [s for s in all_symbols if s.upper().startswith(q)]
        contains_matches = [s for s in all_symbols if q in s.upper() and s not in prefix_matches]
        results = (prefix_matches + contains_matches)[:40]

        return JSONResponse(content={"tickers": results})
    except Exception as e:
        logging.error(f"ticker_search_query error: {e}")
        return JSONResponse(content={"tickers": [], "error": str(e)})

