from fastapi import APIRouter, status, Header, Body
from fastapi.responses import JSONResponse
import pandas as pd
import random
import json
import ipdb
import os
from chess_piece.fastapi_queen import (get_queen_messages_logfile_json, get_queen_messages_json, app_buy_order_request, get_queens_mind, get_queen_orders_json, app_Sellorder_request,  get_ticker_data, get_account_info, queen_wavestories__get_macdwave, app_buy_wave_order_request, 
                                       app_archive_queen_order,
                                       app_queen_order_update_order_rules,
                                       get_revrec_trinity,
                                       get_ticker_time_frame,
                                       get_heart,)

router = APIRouter(
    prefix="/api/data",
    tags=["auth"]
)

def confirm_auth_keys(api_key):
    if api_key != os.environ.get("fastAPI_key"): # fastapi_pollenq_key
        print("Auth Failed", api_key)
        return False
    else:
        return True

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
def load_wavestories_json(username: str=Body(...), symbols: list=Body(...), toggle_view_selection: str=Body(...), prod: bool=Body(...), api_key = Body(...), return_type = Body(...)):
    try:
        if api_key != os.environ.get("fastAPI_key"): # fastapi_pollenq_key
            print("Auth Failed", api_key)
            return "NOTAUTH"
        json_data = queen_wavestories__get_macdwave(username, prod, symbols, toggle_view_selection, return_type=return_type)
        # print(json_data)
        return JSONResponse(content=json_data)
    except Exception as e:
        print(e)


@router.post("/story", status_code=status.HTTP_200_OK)
def load_story_json(client_user: str=Body(...), username: str=Body(...), toggle_view_selection: str=Body(...), symbols: list=Body(...), prod: bool=Body(...), api_key = Body(...), return_type = Body(...)):
    try:
        if api_key != os.environ.get("fastAPI_key"): # fastapi_pollenq_key
            print("Auth Failed", api_key)
            return "NOTAUTH"
        json_data = queen_wavestories__get_macdwave(username, prod, symbols, toggle_view_selection, return_type='story')
        # print(json_data)
        return JSONResponse(content=json_data)
    except Exception as e:
        print(e)


@router.post("/trinity_graph", status_code=status.HTTP_200_OK)
def load_trinity_graph(username=Body(...), prod=Body(...), api_key=Body(...), trinity_weight=Body(...)):
    
    print("trying trinitty")
    if api_key != os.environ.get("fastAPI_key"): # fastapi_pollenq_key
        print("Auth Failed", api_key)
        return "NOTAUTH"
    json_data = get_revrec_trinity(username, prod, trinity_weight=trinity_weight) #'w_15')
    return JSONResponse(content=json_data)

@router.post("/ticker_time_frame", status_code=status.HTTP_200_OK)
def load_trinity_graph(username=Body(...), prod=Body(...), api_key=Body(...), symbols=Body(...)):
    
    if api_key != os.environ.get("fastAPI_key"): # fastapi_pollenq_key
        print("Auth Failed", api_key)
        return "NOTAUTH"
    json_data = get_ticker_time_frame(symbols) #'w_15')
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
def sell_order(username: str=Body(...), prod: bool=Body(...), selected_row=Body(...), default_value: int=Body(...), api_key=Body(...)):
    try:
        # print("router", username, prod, selected_row, default_value)
        if api_key != os.environ.get("fastAPI_key"): # fastapi_pollenq_key
            print("Auth Failed", api_key)
            return "NOTAUTH"

        
        rep = app_Sellorder_request(username, prod, selected_row, default_value)
        if rep.get('status') == 'success':
            return JSONResponse(content=grid_row_button_resp())
        else:
            return JSONResponse(content=grid_row_button_resp(status='error'))
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
def buy_order(client_user: str=Body(...), username: str=Body(...), prod: bool=Body(...), selected_row=Body(...), default_value=Body(...), api_key=Body(...)):
    if api_key != os.environ.get("fastAPI_key"): # fastapi_pollenq_key
        print("Auth Failed", api_key)
        return "NOTAUTH"

    req = app_buy_order_request(client_user, username, prod, selected_row, default_value)
    if req.get('status'):
        return JSONResponse(content=grid_row_button_resp())
    else:
        return JSONResponse(content=grid_row_button_resp(status='error'))

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
    client_user=kwargs.get('client_user')
    if api_key != os.environ.get("fastAPI_key"): # fastapi_pollenq_key
        print("Auth Failed", api_key)
        return "NOTAUTH"
    json_data = get_account_info(client_user, username, prod)
    return JSONResponse(content=json_data)

@router.post("/heart", status_code=status.HTTP_200_OK)
def load_heart(kwargs=Body(...)):
    # print(kwargs)
    username=kwargs.get('username')
    prod=kwargs.get('prod')
    api_key=kwargs.get('api_key')
    client_user=kwargs.get('client_user')
    if api_key != os.environ.get("fastAPI_key"): # fastapi_pollenq_key
        print("Auth Failed", api_key)
        return "NOTAUTH"
    json_data = get_heart(client_user, username, prod)
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
    
    json_data = {'text': text, 'audio_path': audio_file, 'page_direct': page_direct, 'self_image': self_image, 'listen_after_reply': True}


    return JSONResponse(content=json_data)