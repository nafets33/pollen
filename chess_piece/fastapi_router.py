from fastapi import APIRouter, status, Header, Body
from fastapi.responses import JSONResponse
import pandas as pd
import random
import json
import ipdb
import os
from chess_piece.fastapi_queen import (get_queen_messages_logfile_json, get_queen_messages_json, app_buy_order_request, get_queens_mind, get_queen_orders_json, app_Sellorder_request,  get_ticker_data, queen_wavestories__get_macdwave, app_buy_wave_order_request, 
                                       app_archive_queen_order,
                                       app_queen_order_update_order_rules,
                                       get_ticker_time_frame,
                                       get_ticker_data_candle_stick,
                                       get_ticker_data_v2,
                                       grid_row_button_resp,
                                       update_queenking_chessboard,
                                       header_account,)

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

def confirm_auth_keys(api_key):
    if api_key != os.environ.get("fastAPI_key"): # fastapi_pollenq_key
        print("Auth Failed", api_key)
        return False
    else:
        return True



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

@router.post("/symbol_graph_v2", status_code=status.HTTP_200_OK)
def load_symbol_graph(symbol: list=Body(...), prod: bool=Body(...), api_key=Body(...)):
    if api_key != os.environ.get("fastAPI_key"): # fastapi_pollenq_key
        print("Auth Failed", api_key)
        return "NOTAUTH"
    json_data = get_ticker_data_v2(symbol, prod)
    return JSONResponse(content=json_data)

@router.post("/symbol_graph_candle_stick", status_code=status.HTTP_200_OK)
def load_symbol_graph(selectedOption: list=Body(...), prod: bool=Body(...), api_key=Body(...)):
    if api_key != os.environ.get("fastAPI_key"): # fastapi_pollenq_key
        print("Auth Failed", api_key)
        return "NOTAUTH"
    json_data = get_ticker_data_candle_stick(selectedOption)
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
        if confirm_auth_keys(api_key) == False:
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
def sell_order(client_user: str=Body(...), username: str=Body(...), prod: bool=Body(...), selected_row=Body(...), default_value=Body(...), api_key=Body(...)):
    try:
        if api_key != os.environ.get("fastAPI_key"): # fastapi_pollenq_key
            print("Auth Failed", api_key)
            return "NOTAUTH"

        rep = app_Sellorder_request(client_user, username, prod, selected_row, default_value)
        return JSONResponse(content=rep)

    except Exception as e:
        print("router err ", e)

@router.post("/queen_buy_wave_orders", status_code=status.HTTP_200_OK)
def buy_order(username: str=Body(...), prod: bool=Body(...), selected_row=Body(...), default_value=Body(...), api_key=Body(...)):
    if api_key != os.environ.get("fastAPI_key"): # fastapi_pollenq_key
        print("Auth Failed", api_key)
        return "NOTAUTH"

    if app_buy_wave_order_request(username, prod, selected_row, default_value=default_value, ready_buy=False):
        return JSONResponse(content=grid_row_button_resp())
    else:
        return JSONResponse(content=grid_row_button_resp(status='error', message_type='click'))

@router.post("/queen_buy_wave_orders__ready_buy", status_code=status.HTTP_200_OK)
def buy_order(username: str=Body(...), prod: bool=Body(...), selected_row=Body(...), api_key=Body(...)):
    if api_key != os.environ.get("fastAPI_key"): # fastapi_pollenq_key
        print("Auth Failed", api_key)
        return "NOTAUTH"

    if app_buy_wave_order_request(username, prod, selected_row, ready_buy=True):
        return JSONResponse(content=grid_row_button_resp())
    else:
        return JSONResponse(content=grid_row_button_resp(status='error', message_type='click'))

@router.post("/queen_buy_wave_orders__x_buy", status_code=status.HTTP_200_OK)
def buy_order(username: str=Body(...), prod: bool=Body(...), selected_row=Body(...), default_value=Body(...), api_key=Body(...)):
    if api_key != os.environ.get("fastAPI_key"): # fastapi_pollenq_key
        print("Auth Failed", api_key)
        return "NOTAUTH"

    if app_buy_wave_order_request(username, prod, selected_row, default_value, x_buy=True):
        return JSONResponse(content=grid_row_button_resp())
    else:
        return JSONResponse(content=grid_row_button_resp(status='error', message_type='click'))


@router.post("/queen_buy_orders", status_code=status.HTTP_200_OK)
def buy_order(client_user: str=Body(...), username: str=Body(...), prod: bool=Body(...), selected_row=Body(...), default_value=Body(...), api_key=Body(...), return_type=Body(...)):
    if api_key != os.environ.get("fastAPI_key"): # fastapi_pollenq_key
        print("Auth Failed", api_key)
        return "NOTAUTH"
    story = True if return_type == 'story' else False
    kors = default_value
    req = app_buy_order_request(client_user, prod, selected_row, kors, story=story)
    if req.get('status'):
        return JSONResponse(content=grid_row_button_resp(description=req.get('msg')))
    else:
        return JSONResponse(content=grid_row_button_resp(status="ERROR", description=req.get('msg')))


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

@router.post("/update_queenking_chessboard", status_code=status.HTTP_200_OK)
def update_qk_chessboard(username: str= Body(...), prod: bool=Body(...), api_key=Body(...), selected_row=Body(...)): # new_data for update entire row
    if api_key != os.environ.get("fastAPI_key"): # fastapi_pollenq_key
        print("Auth Failed", api_key)
        return "NOTAUTH"
    
    # print("/data/queen", username, prod, kwargs)
    json_data = update_queenking_chessboard(username, prod, selected_row)
    return JSONResponse(content=json_data)



@router.post("/voiceGPT", status_code=status.HTTP_200_OK)
def load_ozz_voice(api_key=Body(...), text=Body(...), self_image=Body(...)):
    # print(kwargs)
    # text = [{'user': 'hey hootie tell me a story'}]
    # text = [  # future state
    #         {'user': 'hey hootie tell me a story', 'resp': 'what story would you like to hear'}, 
    #         {'user': 'could you make up a story?'}]
    # ipdb.set_trace()
    def handle_response(text):
        text_obj = text[-1]['user']

        # handle text_obj
        # WORK take query/history of current question and attempt to handle reponse back ""
        ## Scenarios 

        call_llm=True # goal is to set it to False and figure action/response

        def Scenarios(db_actions, self_image, current_query, first_ask=True, conv_history=False):
            # is this first ask?
            # saying hello, say hello based on whos talking? hoots or hootie, moody
            # how are you...
            # 
            # if first_ask:
            #     # based on question do we have similar listed type quetsion with response action?
            #     if current_query is in db_actions.get('db_first_asks'):
            #         text = db_actions.get('id')
            #         self_image = db_actions.get('id')
                
            return True

        # get final response
        resp = 'what story would you like to hear?'
        
        # update reponse to self
        text[-1].update({'resp': resp})

        return text

    text = handle_response(text)
    
    def handle_image(text, self_image):
        # based on LLM response handle image if needs to change
        self_image = 'hootsAndHootie.png'

        return self_image

    self_image = handle_image(text, self_image)
    
    # audio_file = 'pollen/db/audio_files/file1.mp4'
    audio_file = 'test_audio.mp3'

    page_direct='http://localhost:8501/heart'
    listen_after_reply = False
    
    json_data = {'text': text, 'audio_path': audio_file, 'page_direct': page_direct, 'self_image': self_image, 'listen_after_reply': listen_after_reply}


    return JSONResponse(content=json_data)