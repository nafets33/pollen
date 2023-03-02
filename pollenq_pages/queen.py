
import pandas as pd
import os
import sys
import pandas as pd
import numpy as np
import datetime
import pytz
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from itertools import islice
from PIL import Image
from dotenv import load_dotenv

import streamlit as st
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode, JsCode
from streamlit_extras.stoggle import stoggle
from streamlit_extras.switch_page_button import switch_page
import time
import os
import sqlite3
import time
from custom_button import cust_Button

from polleq_app_auth import signin_main
# import requests
# from requests.auth import HTTPBasicAuth
from chess_piece.app_hive import download_df_as_CSV, create_AppRequest_package, standard_AGgrid, create_wave_chart_all, create_slope_chart, create_wave_chart_single, create_wave_chart, create_guage_chart, create_main_macd_chart, page_session_state__cleanUp, trigger_airflow_dag, send_email, queen__account_keys, progress_bar, queen_order_flow, mark_down_text, click_button_grid, nested_grid, mark_down_text, page_line_seperator, write_flying_bee, hexagon_gif, local_gif, flying_bee_gif, pollen__story
from chess_piece.king import menu_bar_selection, return_all_client_users__db, kingdom__grace_to_find_a_Queen, return_QUEENs__symbols_data, hive_master_root, streamlit_config_colors, local__filepaths_misc, print_line_of_error
from chess_piece.queen_hive import init_pollen_dbs, init_qcp, return_alpaca_user_apiKeys, return_queen_controls, return_STORYbee_trigbees, add_key_to_app, add_key_to_QUEEN, refresh_account_info, generate_TradingModel, stars, analyze_waves, story_view, return_alpc_portolio, ReadPickleData, pollen_themes, PickleData, return_timestamp_string, init_logging
from ozz.ozz_bee import send_ozz_call
# from chat_bot import ozz_bot
# from tqdm import tqdm
# from collections import defaultdict
import ipdb
# import matplotlib.pyplot as plt
# import base64
# from random import randint
load_dotenv()
est = pytz.timezone("US/Eastern")
utc = pytz.timezone('UTC')


# import streamlit_authenticator as stauth
# import smtplib
# import ssl
# from email.message import EmailMessage
# from streamlit.web.server.websocket_headers import _get_websocket_headers

# headers = _get_websocket_headers()

# https://blog.streamlit.io/a-new-streamlit-theme-for-altair-and-plotly/
# https://discuss.streamlit.io/t/how-to-animate-a-line-chart/164/6 ## animiate the Bees Images : )
# https://blog.streamlit.io/introducing-theming/  # change theme colors
# https://extras.streamlit.app
# https://www.freeformatter.com/cron-expression-generator-quartz.html

pd.options.mode.chained_assignment = None

scriptname = os.path.basename(__file__)
queens_chess_piece = os.path.basename(__file__)



# if 'sidebar_hide' in st.session_state:
#     sidebar_hide = 'collapsed'
# else:
#     sidebar_hide = 'expanded'

# st.set_page_config(
#      page_title="pollenq",
#      page_icon=page_icon,
#      layout="wide",
#      initial_sidebar_state=sidebar_hide,
#     #  menu_items={
#     #      'Get Help': 'https://www.extremelycoolapp.com/help',
#     #      'Report a bug': "https://www.extremelycoolapp.com/bug",
#     #      'About': "# This is a header. This is an *extremely* cool app!"
#     #  }
#  )
page = 'QueensConscience'

# if st.button("sw"):
#     switch_page("QueensConscience#no-ones-flying")

## anchors
# st.header("Section 1")
# st.markdown("[Section 1](#section-1)")

def queen():
    # ###### GLOBAL # ######
    active_order_state_list = ['running', 'running_close', 'submitted', 'error', 'pending', 'completed', 'completed_alpaca', 'running_open', 'archived_bee']

    # crypto
    crypto_currency_symbols = ['BTCUSD', 'ETHUSD', 'BTC/USD', 'ETH/USD']
    crypto_symbols__tickers_avail = ['BTCUSD', 'ETHUSD']

    main_root = hive_master_root() # os.getcwd()  # hive root

    # images
    MISC = local__filepaths_misc()
    jpg_root = MISC['jpg_root']
    bee_image = MISC['bee_image']
    castle_png = MISC['castle_png']
    bishop_png = MISC['bishop_png']
    knight_png = MISC['knight_png']
    flyingbee_grey_gif_path = MISC['flyingbee_grey_gif_path']
    power_gif = MISC['power_gif']
    uparrow_gif = MISC['uparrow_gif']
    learningwalk_bee = MISC['learningwalk_bee']
    runaway_bee_gif = MISC['runaway_bee_gif']
    queen_crown_url = MISC['queen_crown_url']
    pawn_png_url = MISC['pawn_png_url']

    learningwalk_bee = Image.open(learningwalk_bee)

    ##### STREAMLIT ###
    k_colors = streamlit_config_colors()
    default_text_color = k_colors['default_text_color'] # = '#59490A'
    default_font = k_colors['default_font'] # = "sans serif"
    default_yellow_color = k_colors['default_yellow_color'] # = '#C5B743'
    
    with st.spinner("Welcome to the QueensMind"):

        # return page last visited 
        sneak_peak = False
        if 'sneak_peak' in st.session_state and st.session_state['sneak_peak'] == True:
            sneak_peak = True
            st.session_state['production'] = True
            st.session_state['username'] = 'stefanstapinski@gmail.com'
            st.session_state['authorized_user'] = False
            st.session_state['db_root'] = os.path.join(main_root, 'db')
            st.info("Welcome and Watch A QueenBot in Action")
                    
            init_pollen_dbs(db_root=st.session_state['db_root'], prod=True, queens_chess_piece='queen', queenKING=True)

        
        elif st.session_state['authentication_status'] != True:
            st.write(st.session_state['authentication_status'])
            st.error("You Need to Log In to pollenq")
            # switch_page("pollenq")
            sneak_peak = False
            st.session_state['sneak_peak'] == False
            st.stop()
        
        elif st.session_state['authentication_status']:
            sneak_peak = False
            pass
        else:
            st.error("Stopping page")
            st.stop()

        db_root = st.session_state['db_root']
        prod, admin, prod_name = st.session_state['production'], st.session_state['admin'], st.session_state['prod_name']

        authorized_user = st.session_state['authorized_user']
        client_user = st.session_state["username"]
        # st.write("*", client_user)
        
        PB_QUEEN_Pickle = st.session_state['PB_QUEEN_Pickle'] 
        PB_App_Pickle = st.session_state['PB_App_Pickle'] 
        PB_Orders_Pickle = st.session_state['PB_Orders_Pickle'] 
        PB_queen_Archives_Pickle = st.session_state['PB_queen_Archives_Pickle']
        PB_QUEENsHeart_PICKLE = st.session_state['PB_QUEENsHeart_PICKLE']
        PB_KING_Pickle = st.session_state['PB_KING_Pickle']


        QUEEN_KING = ReadPickleData(pickle_file=PB_App_Pickle)    
        KING = ReadPickleData(pickle_file=PB_KING_Pickle)
        # QUEEN Databases
        QUEEN_KING['source'] = PB_App_Pickle
        QUEEN = ReadPickleData(st.session_state['PB_QUEEN_Pickle'])
       
        QUEENsHeart = ReadPickleData(PB_QUEENsHeart_PICKLE)

        if st.session_state['authorized_user']:
            APP_req = add_key_to_app(QUEEN_KING)
            QUEEN_KING = APP_req['QUEEN_KING']
            if APP_req['update']:
                PickleData(PB_App_Pickle, QUEEN_KING)


        def chunk(it, size):
            it = iter(it)
            return iter(lambda: tuple(islice(it, size)), ())
      
        def return_total_profits(QUEEN):
            try:
                df = QUEEN['queen_orders']
                QUEEN = df[(df['queen_order_state']== 'completed') & (df['side'] == 'sell')].copy()
                return_dict = {}
                if len(QUEEN) > 0:
                    now_ = datetime.datetime.now(est)
                    orders_today = df[df['datetime'] > now_.replace(hour=1, minute=1, second=1)].copy()
                    
                    by_ticker = True if 'by_ticker' in st.session_state else False
                    group_by_value = ['symbol'] if by_ticker == True else ['symbol', 'ticker_time_frame']
                    tic_group_df = df.groupby(group_by_value)[['profit_loss', 'honey']].sum().reset_index()

                    return_dict['TotalProfitLoss'] = tic_group_df
                    
                    pct_profits = df.groupby(group_by_value)[['profit_loss', 'honey']].sum().reset_index()
                    # total_dolla = round(sum(pct_profits['profit_loss']), 2)
                    # total_honey = round(sum(pct_profits['honey']), 2)
                    if len(orders_today) > 0:
                        today_pl_df = orders_today.groupby(group_by_value)[['profit_loss', 'honey']].sum().reset_index()
                        total_dolla = round(sum(orders_today['profit_loss']), 2)
                        total_honey = "" # round((sum(orders_today['honey']) * 100), 2) # this needs to be avg % per trade?
                    else:
                        today_pl_df = 0
                        total_dolla = 0
                        total_honey = ""
                    
                    # st.write(sum(pct_profits['profit_loss']))
                    
                    if len(orders_today) > 0:
                        title = f'P/L Todays Money {"$"} {total_dolla}, Honey {total_honey} %'
                    else:
                        title = f'P/L Todays Money {"$"} {total_dolla}, Honey {total_honey} %'
                    with st.expander(title):
                        by_ticker = st.checkbox('Group by Ticker', key='by_ticker')

                        if len(orders_today) > 0:
                            # df = orders_today
                            # today_pl_df = df.groupby(group_by_value)[['profit_loss']].sum().reset_index()
                            mark_down_text(fontsize='25', text="Today Profit Loss")
                            st.write(today_pl_df)
                            mark_down_text(fontsize='25', text="Total Profit Loss")
                            st.write(tic_group_df)
                        else:
                            mark_down_text(fontsize='25', text="Total Profit Loss")

                            st.write(tic_group_df)
                            chunk_list = dict(zip(tic_group_df['symbol'], tic_group_df['honey']))
                            chunk_list = [{k:round(v,2)} for (k,v) in chunk_list.items() if k != 'init']
                            chunk_write_dictitems_in_row(chunk_list=chunk_list, max_n=10, write_type='pl_profits', title="PL", groupby_qcp=False, info_type=False)
            except Exception as e:
                print(e, print_line_of_error())          # submitted = st.form_submit_button("Save")
                # else:
                #     st.write("Waiting for your First Trade")
            return return_dict

        
        def stop_queenbee(QUEEN_KING):
            checkbox_val = st.sidebar.button("Stop Queen")
            if checkbox_val:
                stop_queen = create_AppRequest_package(request_name='queen_sleep')

                QUEEN_KING['queen_sleep'].append(stop_queen)
                PickleData(PB_App_Pickle, QUEEN_KING)
                st.success("Queen Sleeps")
            
            return True


        def refresh_queenbee_controls(QUEEN_KING):
            refresh = st.sidebar.button("Reset QUEEN controls")

            if refresh:
                QUEEN_KING['king_controls_queen'] = return_queen_controls(stars)
                
                PickleData(pickle_file=PB_App_Pickle, data_to_store=QUEEN_KING)
                local_gif(gif_path=power_gif)
                st.success("All Queen Controls Reset")
                    
            return True


        def return_image_upon_save(title="Saved", width=33, gif=power_gif):
            local_gif(gif_path=gif)
            st.success(title)

        
        def set_chess_pieces_symbols(QUEEN_KING, admin=False):
            if admin:
                all_workers = list(QUEEN_KING['chess_board'].keys())
            else:
                all_workers = list(QUEEN_KING['qcp_workerbees'].keys())
            
            qcp_ticker_index = {}
            view = []
            for qcp in all_workers:
                if qcp in ['castle', 'bishop', 'knight', 'castle_coin']:
                    view.append(f'{qcp.upper()} ({QUEEN_KING["qcp_workerbees"][qcp]["tickers"]} )')
                    for ticker in QUEEN_KING["qcp_workerbees"][qcp]["tickers"]:
                        qcp_ticker_index[ticker] = qcp
            
            return {'qcp_ticker_index': qcp_ticker_index, 'view': view, 'all_workers': all_workers}


        def update_Workerbees(QUEEN_KING, admin):
            
            def add_new_qcp__to_Queens_workerbees():
                with st.form('add new qcp'):
                    avail_qcp = ['pawn1', 'pawn2', 'pawn3', 'pawn4']
                    avail_tickers = ['QQQ']
                    # tickers_to_add = st.multiselect(label=f'Add Symbols', options=avail_tickers, help=f'Try not to Max out number of piecesm, only ~10 allowed')
                    cols = st.columns((1,2,10,3,2,2))
                    with cols[1]:                
                        qcp = st.selectbox(label='qcp', key=f'qcp_new', options=avail_qcp)
                        QUEEN_KING['qcp_workerbees'][qcp] = init_qcp(init_macd_vars={'fast': 12, 'slow': 26, 'smooth': 9}, ticker_list=[])
                    with cols[0]:
                        st.image(queen_crown_url, width=64)
                    with cols[2]:
                        QUEEN_KING['qcp_workerbees'][qcp]['tickers'] = st.multiselect(label=f'{qcp} symbols', options=avail_tickers, default=None, help='Try not to Max out number of piecesm, only ~10 allowed')
                    with cols[3]:
                        QUEEN_KING['qcp_workerbees'][qcp]['MACD_fast_slow_smooth']['fast'] = st.number_input("fast", min_value=1, max_value=33, value=int(QUEEN_KING['qcp_workerbees'][qcp]['MACD_fast_slow_smooth']['fast']), key=f'{qcp}fast')
                    with cols[4]:
                        QUEEN_KING['qcp_workerbees'][qcp]['MACD_fast_slow_smooth']['slow'] = st.number_input("slow", min_value=1, max_value=33, value=int(QUEEN_KING['qcp_workerbees'][qcp]['MACD_fast_slow_smooth']['slow']), key=f'{qcp}slow')
                    with cols[5]:
                        QUEEN_KING['qcp_workerbees'][qcp]['MACD_fast_slow_smooth']['smooth'] = st.number_input("smooth", min_value=1, max_value=33, value=int(QUEEN_KING['qcp_workerbees'][qcp]['MACD_fast_slow_smooth']['smooth']), key=f'{qcp}smooth')            

                    if st.form_submit_button('Save New qcp'):
                        PickleData(PB_App_Pickle, QUEEN_KING)


            try:
                #### SPEED THIS UP AND CHANGE TO DB CALL FOR ALLOWED ACTIVE TICKERS ###
                # all_alpaca_tickers = api.list_assets()
                # alpaca_symbols_dict = {}
                # for n, v in enumerate(all_alpaca_tickers):
                #     if all_alpaca_tickers[n].status == 'active':
                #         alpaca_symbols_dict[all_alpaca_tickers[n].symbol] = vars(all_alpaca_tickers[n])
                # ipdb.set_trace()
                ticker_allowed = list(KING['ticker_universe'].get('alpaca_symbols_dict').keys()) + crypto_symbols__tickers_avail
                
                current_setup = QUEEN_KING['qcp_workerbees']
                chess_pieces = set_chess_pieces_symbols(QUEEN_KING=QUEEN_KING)
                view = chess_pieces.get('view')
                all_workers = chess_pieces.get('all_workers')
                qcp_ticker_index = chess_pieces.get('qcp_ticker_index')
                current_tickers = qcp_ticker_index.keys()
                # st.write(current_tickers)
                
                name = 'Workerbees_Admin' if admin else 'Chess Board'

                with st.expander(name, True):
                    with st.form(f'Update WorkerBees{admin}'):

                        cols = st.columns((1,1,1))
                        with cols[0]:
                            st.image(pawn_png_url, width=23) ## generate info messages with click ok to exit message
                            # st.markdown(f'<img src="{image}"', unsafe_allow_html=True)
                        #     image = "https://p7.hiclipart.com/preview/221/313/319/chess-piece-knight-rook-board-game-chess.jpg"
                        #     st.markdown(f'<img src="{image}" style="background-color:transparent">', unsafe_allow_html=True)
                        with cols[1]:
                            st.subheader(name)
                        cols = st.columns((1,10,3,2,2,2))
                        # all_workers = list(QUEEN_KING['qcp_workerbees'].keys())
                        for qcp in all_workers:
                            if qcp == 'castle_coin':
                                with cols[0]:
                                    st.image("https://s3.us-east-2.amazonaws.com/nomics-api/static/images/currencies/BSV.png", width=54)
                                    # local_gif(gif_path=bitcoin_gif)
                                with cols[1]:
                                    QUEEN_KING['qcp_workerbees'][qcp]['tickers'] = st.multiselect(label=f'{qcp} symbols', options=ticker_allowed + crypto_symbols__tickers_avail, default=QUEEN_KING['qcp_workerbees'][qcp]['tickers'], help='Castle Should Hold your Highest Valued Symbols', key=f'{qcp}tickers{admin}')
                                with cols[2]:
                                    st.selectbox(label='Model', options=['MACD'], key=f'{qcp}model{admin}')
                                with cols[3]:
                                    QUEEN_KING['qcp_workerbees'][qcp]['MACD_fast_slow_smooth']['fast'] = st.number_input("fast", min_value=1, max_value=33, value=int(QUEEN_KING['qcp_workerbees'][qcp]['MACD_fast_slow_smooth']['fast']), key=f'{qcp}fast{admin}')
                                with cols[4]:
                                    QUEEN_KING['qcp_workerbees'][qcp]['MACD_fast_slow_smooth']['slow'] = st.number_input("slow", min_value=1, max_value=33, value=int(QUEEN_KING['qcp_workerbees'][qcp]['MACD_fast_slow_smooth']['slow']), key=f'{qcp}slow{admin}')
                                with cols[5]:
                                    QUEEN_KING['qcp_workerbees'][qcp]['MACD_fast_slow_smooth']['smooth'] = st.number_input("smooth", min_value=1, max_value=33, value=int(QUEEN_KING['qcp_workerbees'][qcp]['MACD_fast_slow_smooth']['smooth']), key=f'{qcp}smooth{admin}')
                            
                            if qcp == 'castle':
                                with cols[0]:
                                    st.image(castle_png, width=54)
                                with cols[1]:
                                    QUEEN_KING['qcp_workerbees'][qcp]['tickers'] = st.multiselect(label=f'{qcp} symbols', options=ticker_allowed + crypto_symbols__tickers_avail, default=QUEEN_KING['qcp_workerbees'][qcp]['tickers'], help='Castle Should Hold your Highest Valued Symbols', key=f'{qcp}tickers{admin}')
                                with cols[2]:
                                    st.selectbox(label='Model', options=['MACD'], key=f'{qcp}model{admin}')
                                with cols[3]:
                                    QUEEN_KING['qcp_workerbees'][qcp]['MACD_fast_slow_smooth']['fast'] = st.number_input("fast", min_value=1, max_value=33, value=int(QUEEN_KING['qcp_workerbees'][qcp]['MACD_fast_slow_smooth']['fast']), key=f'{qcp}fast{admin}')
                                with cols[4]:
                                    QUEEN_KING['qcp_workerbees'][qcp]['MACD_fast_slow_smooth']['slow'] = st.number_input("slow", min_value=1, max_value=33, value=int(QUEEN_KING['qcp_workerbees'][qcp]['MACD_fast_slow_smooth']['slow']), key=f'{qcp}slow{admin}')
                                with cols[5]:
                                    QUEEN_KING['qcp_workerbees'][qcp]['MACD_fast_slow_smooth']['smooth'] = st.number_input("smooth", min_value=1, max_value=33, value=int(QUEEN_KING['qcp_workerbees'][qcp]['MACD_fast_slow_smooth']['smooth']), key=f'{qcp}smooth{admin}')

                            if qcp == 'bishop':
                                with cols[0]:
                                    st.image(bishop_png, width=74)
                                with cols[1]:
                                    QUEEN_KING['qcp_workerbees'][qcp]['tickers'] = st.multiselect(label=f'{qcp} symbols', options=ticker_allowed + crypto_symbols__tickers_avail, default=QUEEN_KING['qcp_workerbees'][qcp]['tickers'], help='Castle Should Hold your Highest Valued Symbols', key=f'{qcp}tickers{admin}')
                                with cols[2]:
                                    st.selectbox(label='Model', options=['MACD'], key=f'{qcp}model{admin}')
                                with cols[3]:
                                    QUEEN_KING['qcp_workerbees'][qcp]['MACD_fast_slow_smooth']['fast'] = st.number_input("fast", min_value=1, max_value=33, value=int(QUEEN_KING['qcp_workerbees'][qcp]['MACD_fast_slow_smooth']['fast']), key=f'{qcp}fast{admin}')
                                with cols[4]:
                                    QUEEN_KING['qcp_workerbees'][qcp]['MACD_fast_slow_smooth']['slow'] = st.number_input("slow", min_value=1, max_value=33, value=int(QUEEN_KING['qcp_workerbees'][qcp]['MACD_fast_slow_smooth']['slow']), key=f'{qcp}slow{admin}')
                                with cols[5]:
                                    QUEEN_KING['qcp_workerbees'][qcp]['MACD_fast_slow_smooth']['smooth'] = st.number_input("smooth", min_value=1, max_value=33, value=int(QUEEN_KING['qcp_workerbees'][qcp]['MACD_fast_slow_smooth']['smooth']), key=f'{qcp}smooth{admin}')

                            if qcp == 'knight':
                                with cols[0]:
                                    st.image(knight_png, width=74)
                                with cols[1]:
                                    QUEEN_KING['qcp_workerbees'][qcp]['tickers'] = st.multiselect(label=f'{qcp} symbols', options=ticker_allowed + crypto_symbols__tickers_avail, default=QUEEN_KING['qcp_workerbees'][qcp]['tickers'], help='Castle Should Hold your Highest Valued Symbols', key=f'{qcp}tickers{admin}')
                                with cols[2]:
                                    st.selectbox(label='Model', options=['MACD'], key=f'{qcp}model{admin}')
                                with cols[3]:
                                    QUEEN_KING['qcp_workerbees'][qcp]['MACD_fast_slow_smooth']['fast'] = st.number_input("fast", min_value=1, max_value=33, value=int(QUEEN_KING['qcp_workerbees'][qcp]['MACD_fast_slow_smooth']['fast']), key=f'{qcp}fast{admin}')
                                with cols[4]:
                                    QUEEN_KING['qcp_workerbees'][qcp]['MACD_fast_slow_smooth']['slow'] = st.number_input("slow", min_value=1, max_value=33, value=int(QUEEN_KING['qcp_workerbees'][qcp]['MACD_fast_slow_smooth']['slow']), key=f'{qcp}slow{admin}')
                                with cols[5]:
                                    QUEEN_KING['qcp_workerbees'][qcp]['MACD_fast_slow_smooth']['smooth'] = st.number_input("smooth", min_value=1, max_value=33, value=int(QUEEN_KING['qcp_workerbees'][qcp]['MACD_fast_slow_smooth']['smooth']), key=f'{qcp}smooth{admin}')
                    
                            # elif qcp == 'pawns':
                            #     if len(QUEEN_KING["qcp_workerbees"][qcp]["tickers"]) > 20:
                            #         show = QUEEN_KING["qcp_workerbees"][qcp]["tickers"][:20]
                            #         show = f'{show} ....'
                            #     else:
                            #         show = QUEEN_KING["qcp_workerbees"][qcp]["tickers"]
                            #     st.write(f'{qcp} {show}')



                        if st.form_submit_button('Save Workers'):
                            if authorized_user == False:
                                st.warning("You Need your Queen First! Please contact pollenq.queen@gmail.com")
                                return False


                            else:
                                def handle__new_tickers__AdjustTradingModels(QUEEN_KING):
                                    # add new trading models if needed
                                    # Castle 
                                    for workerbee, bees_data in QUEEN_KING['qcp_workerbees'].items():
                                        for ticker in bees_data['tickers']:
                                            QUEEN_KING = add_trading_model(PB_APP_Pickle=PB_App_Pickle, QUEEN_KING=QUEEN_KING, ticker=ticker, workerbee=workerbee, status='active')

                                    return QUEEN_KING
                                
                                QUEEN_KING = handle__new_tickers__AdjustTradingModels(QUEEN_KING=QUEEN_KING)
                                
                                app_req = create_AppRequest_package(request_name='workerbees')
                                QUEEN_KING['workerbees_requests'].append(app_req)
                                # QUEEN_KING['qcp_workerbees'].update(QUEEN['workerbees'][workerbee])
                                PickleData(pickle_file=PB_App_Pickle, data_to_store=QUEEN_KING)
                                return_image_upon_save(title="Workers Saved")
                                return True

                    if admin:
                        if st.button('add new qcp'):
                            add_new_qcp__to_Queens_workerbees()
                return True
            except Exception as e:
                print(e, print_line_of_error())
            

        def its_morphin_time_view(QUEEN, STORY_bee, ticker, POLLENSTORY, combine_story=False):

            now_time = datetime.datetime.now(est)
            active_ttf = QUEEN['heartbeat']['available_tickers'] = [i for (i, v) in STORY_bee.items() if (now_time - v['story']['time_state']).seconds < 86400]
            
            all_df = []
            total_current_macd_tier = 0
            total_current_hist_tier = 0
            for ttf in active_ttf :
                if ttf in POLLENSTORY.keys() and ticker in ttf.split("_")[0]:
                    df = POLLENSTORY[ttf]
                    df = df[['timestamp_est', 'chartdate', 'name', 'macd_tier', 'hist_tier', 'profits']].copy()
                    total_current_macd_tier += df.iloc[-1]['macd_tier']
                    total_current_hist_tier += df.iloc[-1]['hist_tier']
                    
                    all_df.append(df)
            


            t = '{:,.2%}'.format(total_current_macd_tier/ 64)
            h = '{:,.2%}'.format(total_current_hist_tier / 64)


            return {'macd_tier_guage': t, 'hist_tier_guage': h, 'macd_tier_guage_value': (total_current_macd_tier/ 64),
            'hist_tier_guage_value': (total_current_hist_tier/ 64)
            }


        def queen_wavestories(QUEEN):
            
            try:
                with st.expander("Wave Stories", True):
                    req = ticker_time_frame__option(tickers_avail_op=tickers_avail_op, req_key='wavestories')
                    tickers = req['tickers']
                    ticker_option = req['ticker_option']
                    frame_option = req['frame_option']

                    if len(tickers) > 8:
                        st.warning("Total MACD GUAGE Number reflects all tickers BUT you may only view 8 tickers")
                    cols = st.columns((1, 2))
                    # st.write("why")
                    for symbol in tickers:
                        star__view = its_morphin_time_view(QUEEN=QUEEN, STORY_bee=STORY_bee, ticker=symbol, POLLENSTORY=POLLENSTORY) ## RETURN FASTER maybe cache?
                        df = story_view(STORY_bee=STORY_bee, ticker=ticker_option)['df']
                        df_style = df.style.background_gradient(cmap="RdYlGn", gmap=df['current_macd_tier'], axis=0, vmin=-8, vmax=8)
                        with cols[0]:
                            st.plotly_chart(create_guage_chart(title=f'{symbol} Wave Gauge', value=float(star__view["macd_tier_guage_value"])))
                        with cols[1]:
                            mark_down_text(fontsize=25, text=f'{symbol} {"MACD Gauge "}{star__view["macd_tier_guage"]}{" Hist Gauge "}{star__view["hist_tier_guage"]}')

                            st.dataframe(df_style)


                return True
            except Exception as e:
                print(e, print_line_of_error()) ## error should stop when you have data of bees?
                return False
            

        def model_wave_results(STORY_bee):
            with st.expander('model results of queens court'):
                return_results = {}
                dict_list_ttf = analyze_waves(STORY_bee, ttframe_wave_trigbee=False)['d_agg_view_return']        

                ticker_list = set([i.split("_")[0] for i in dict_list_ttf.keys()])
                for ticker_option in ticker_list:
                
                    for trigbee in dict_list_ttf[list(dict_list_ttf.keys())[0]]:
                        
                        ticker_selection = {k: v for k, v in dict_list_ttf.items() if ticker_option in k}
                        buys = [data[trigbee] for k, data in ticker_selection.items()]
                        df_trigbee_waves = pd.concat(buys, axis=0)
                        col_view = ['ticker_time_frame'] + [i for i in df_trigbee_waves.columns if i not in 'ticker_time_frame']
                        df_trigbee_waves = df_trigbee_waves[col_view]
                        color = 'Green' if 'buy' in trigbee else 'Red'

                        t_winners = sum(df_trigbee_waves['winners_n'])
                        t_losers = sum(df_trigbee_waves['losers_n'])
                        total_waves = t_winners + t_losers
                        win_pct = 100 * round(t_winners / total_waves, 2)

                        t_maxprofits = sum(df_trigbee_waves['sum_maxprofit'])

                        return_results[f'{ticker_option}{"_bee_"}{trigbee}'] = f'{"~Total Max Profits "}{round(t_maxprofits * 100, 2)}{"%"}{"  ~Win Pct "}{win_pct}{"%"}{": Winners "}{t_winners}{" :: Losers "}{t_losers}'
                    # df_bestwaves = analyze_waves(STORY_bee, ttframe_wave_trigbee=df_trigbee_waves['ticker_time_frame'].iloc[-1])['df_bestwaves']

                df = pd.DataFrame(return_results.items())
                mark_down_text(color='#C5B743', text=f'{"Trigger Bee Model Results "}')
                st.write(df) 

                return True


        def clean_out_app_requests(QUEEN, QUEEN_KING, request_buckets):
            save = False
            for req_bucket in request_buckets:
                if req_bucket not in QUEEN_KING.keys():
                    st.write("Verison Missing DB: ", req_bucket)
                    continue
                for app_req in QUEEN_KING[req_bucket]:
                    if app_req['app_requests_id'] in QUEEN['app_requests__bucket']:
                        print(f'{req_bucket} QUEEN Processed app Request {app_req["app_requests_id"]}')
                        st.info(f'{req_bucket} QUEEN Processed app Request {app_req["app_requests_id"]}')
                        archive_bucket = f'{req_bucket}{"_requests"}'
                        QUEEN_KING[req_bucket].remove(app_req)
                        QUEEN_KING[archive_bucket].append(app_req)
                        save = True
            if save:
                PickleData(pickle_file=PB_App_Pickle, data_to_store=QUEEN_KING)
            
            return True


        def clear_subconscious_Thought(QUEEN, QUEEN_KING):
            with st.sidebar.expander("clear subconscious thought"):
                with st.form('clear subconscious'):
                    thoughts = QUEEN['subconscious'].keys()
                    clear_thought = st.selectbox('clear subconscious thought', list(thoughts))
                    
                    if st.form_submit_button("Save"):
                        app_req = create_AppRequest_package(request_name='subconscious', archive_bucket='subconscious_requests')
                        app_req['subconscious_thought_to_clear'] = clear_thought
                        app_req['subconscious_thought_new_value'] = []
                        QUEEN_KING['subconscious'].append(app_req)
                        return_image_upon_save(title="subconscious thought cleared")
                        PickleData(pickle_file=PB_App_Pickle, data_to_store=QUEEN_KING)

                        return True


        def trigger_queen_vars(dag, client_username, last_trig_date=datetime.datetime.now(est)):
            return {'dag': dag, 'last_trig_date': last_trig_date, 'client_user': client_username}
        
        
        def queenbee_online(QUEENsHeart, admin, dag, api_failed):
            # from airflow.dags.dag_queenbee_prod import run_trigger_dag
            
            # users_allowed_queen_email, users_allowed_queen_emailname, users_allowed_queen_emailname__db = kingdom__grace_to_find_a_Queen()
            users_allowed_queen_email = KING['users'].get('client_user__allowed_queen_list')
            now = datetime.datetime.now(est)

            if dag =='run_queenbee':
                if (now - QUEEN_KING['trigger_queen'].get('last_trig_date')).total_seconds() < 60:
                    st.write("Waking up your Queen She is a bit lazy today...it may take her up to 60 Seconds to get out of bed")
                    st.image(QUEEN_KING['character_image'], width=100)
                    return False
                if (now - QUEEN_KING['trigger_queen'].get('last_trig_date')).total_seconds() < 86400:
                    st.sidebar.write("Awaiting Queen")
                    return False
                
                if api_failed:
                    st.write("you need to setup your Broker Queens to Turn on your Queen See Account Keys Below")
                    return False

                # if (now - QUEEN['pq_last_modified']['pq_last_modified']).total_seconds() > 60:
                if 'heartbeat_time' not in QUEENsHeart.keys():
                    st.write("You Need a Queen")
                    return False
                
                if (now - QUEENsHeart['heartbeat_time']).total_seconds() > 60:
                    # st.write("YOUR QUEEN if OFFLINE")
                    cols = st.columns((3,3,1,1,1,1,1,1))
                    with cols[0]:
                        st.error("Your Queen Is Asleep Wake Her UP!")
                    with cols[1]:
                        wake_up_queen_button = st.button("Wake Her Up")
                        # wake_up_queen_button = cust_Button(file_path_url="misc/sleeping_queen_gif.gif", height='50px', key='b')
                        if wake_up_queen_button and st.session_state['authorized_user']:
                            if st.session_state['username'] not in users_allowed_queen_email: ## this db name for client_user # stefanstapinski
                                print("failsafe away from user running function")
                                send_email(recipient='stapinski89@gmail.com', subject="NotAllowedQueen", body=f'{st.session_state["username"]} you forgot to say something')
                                st.error("Your Account not Yet authorized")
                                return False
                            # execute trigger
                            trigger_airflow_dag(dag=dag, client_username=st.session_state['username'], prod=prod)
                            QUEEN_KING['trigger_queen'].update(trigger_queen_vars(dag=dag, client_username=st.session_state['username']))
                            st.write("My Queen")
                            st.image(QUEEN_KING['character_image'], width=100)  ## have this be the client_user character
                            PickleData(pickle_file=PB_App_Pickle, data_to_store=QUEEN_KING)
                            switch_page("pollenq")

                    
                    with cols[2]:
                        local_gif(gif_path=flyingbee_grey_gif_path)

                    with cols[3]:
                        local_gif(gif_path=flyingbee_grey_gif_path)
                    with cols[4]:
                        local_gif(gif_path=flyingbee_grey_gif_path)
                    with cols[5]:
                        local_gif(gif_path=flyingbee_grey_gif_path)
                    with cols[6]:
                        local_gif(gif_path=flyingbee_grey_gif_path)


                    return False
                else:
                    return True
            elif dag =='run_workerbees':
                if admin:
                    if st.sidebar.button("Flying Bees"):
                        trigger_airflow_dag(dag=dag, client_username=st.session_state['username'], prod=prod)
                        st.write("Bees Fly")
                return True
            elif dag =='run_workerbees_crypto':
                if admin:
                    if st.sidebar.button("Flying Crypto Bees"):
                        trigger_airflow_dag(dag=dag, client_username=st.session_state['username'], prod=prod)
                        st.write("Crypto Bees Fly")
                return True
            else:
                return False

        
        def add_trading_model(PB_APP_Pickle, QUEEN_KING, ticker, model='MACD', status='not_active', workerbee=False):
            trading_models = QUEEN_KING['king_controls_queen']['symbols_stars_TradingModel']
            confirmed_qcp = ['castle', 'bishop', 'knight', 'castle_coin']
            if ticker not in trading_models.keys():
                if workerbee in confirmed_qcp:
                    print(ticker, " Ticker Missing Trading Model Adding Default ", model)
                    # logging_log_message(msg=f'{ticker}{": added trading model: "}{model}')
                    # logging.info()
                    tradingmodel1 = generate_TradingModel(ticker=ticker, status=status)[model]
                    QUEEN_KING['king_controls_queen']['symbols_stars_TradingModel'].update(tradingmodel1)
                    PickleData(pickle_file=PB_APP_Pickle, data_to_store=QUEEN_KING)
                else:
                    tradingmodel1 = generate_TradingModel(ticker=ticker, status='not_active')[model]
                    QUEEN_KING['king_controls_queen']['symbols_stars_TradingModel'].update(tradingmodel1)
                    PickleData(pickle_file=PB_APP_Pickle, data_to_store=QUEEN_KING)

                return QUEEN_KING
            else:
                return QUEEN_KING

        
        def chunk_write_dictitems_in_row(chunk_list, max_n=10, write_type='checkbox', title="Active Models", groupby_qcp=False, info_type='buy'):
            # qcp_ticker_index = set_chess_pieces_symbols(QUEEN_KING=QUEEN_KING)['qcp_ticker_index']
            # if groupby_qcp:
            #     for qcp in set(qcp_ticker_index.values()):
            #         st.warning()
            try:
                # chunk_list = chunk_list
                num_rr = len(chunk_list) + 1 # + 1 is for chunking so slice ends at last 
                chunk_num = max_n if num_rr > max_n else num_rr
                
                # if num_rr > chunk_num:
                chunks = list(chunk(range(num_rr), chunk_num))
                for i in chunks:
                    if i[0] == 0:
                        slice1 = i[0]
                        slice2 = i[-1] # [0 : 49]
                    else:
                        slice1 = i[0] - 1
                        slice2 = i[-1] # [49 : 87]
                    # print("chunk slice", (slice1, slice2))
                    chunk_n = chunk_list[slice1:slice2]
                    cols = st.columns(len(chunk_n) + 1)
                    with cols[0]:
                        if write_type == 'info':
                            flying_bee_gif(width='53', height='53')
                        else:
                            st.write(title)
                        # bees = [write_flying_bee(width='3') for i in chunk_n]
                    for idx, package in enumerate(chunk_n):
                        for ticker, v in package.items():
                        # ticker, value = package.items()
                            with cols[idx + 1]:
                                if write_type == 'checkbox':
                                    st.checkbox(ticker, v, key=f'{ticker}')  ## add as quick save to turn off and on Model
                                if write_type == 'info':
                                    if info_type == 'buy':
                                        st.warning(f'{ticker} {v}')
                                        local_gif(gif_path=uparrow_gif, height='23', width='23')
                                    else:
                                        st.info(f'{ticker} {v}')
                                    flying_bee_gif(width='43', height='40')
                                if write_type == 'pl_profits':
                                    st.write(ticker, v)
            except Exception as e:
                print(e, print_line_of_error())
            # else:
            #     cols = st.columns(len(chunk_list) + 1)
            #     with cols[0]:
            #         if write_type == 'info':
            #             flying_bee_gif(width='53', height='53')
            #         else:
            #             st.write(title)
            #     for idx, package in enumerate(chunk_list):
            #         for ticker, v in package.items():
            #         # ticker, value = package.items()
            #             with cols[idx + 1]:
            #                 if write_type == 'checkbox':
            #                     st.checkbox(ticker, v, key=f'{ticker}{v}')  ## add as quick save to turn off and on Model
            #                 if write_type == 'info':
            #                     if info_type == 'buy':
            #                         st.warning(f'{ticker} {v}')
            #                         local_gif(gif_path=uparrow_gif, height='23', width='23')
            #                     else:
            #                         st.info(f'{ticker} {v}')
            #                         flying_bee_gif(width='38', height='42')
            return True 
        

        def refresh_tickers_TradingModels(QUEEN_KING, ticker):
            tradingmodel1 = generate_TradingModel(ticker=ticker, status='active')['MACD']
            QUEEN_KING['king_controls_queen']['symbols_stars_TradingModel'].update(tradingmodel1)
            return QUEEN_KING

        
        def page_tab_permission_denied(admin, st_stop=True):
            if admin == False:
                st.warning("permission denied you need a Queen to access")
                if st_stop:
                    st.info("Page Stopped")
                    st.stop()


        def advanced_charts(tickers_avail, POLLENSTORY):
            try:
                stars_radio_dict = {'1Min':"1Minute_1Day", '5Min':"5Minute_5Day", '30m':"30Minute_1Month", '1hr':"1Hour_3Month", 
                '2hr':"2Hour_6Month", '1Yr':"1Day_1Year", 'all':"all",}
                charts__view, waves__view, slopes__view = st.tabs(['charts', 'waves', 'slopes'])

                cols = st.columns((1,10,1,1))
                # fullstory_option = st.selectbox('POLLENSTORY', ['no', 'yes'], index=['yes'].index('yes'))
                with cols[0]:
                    ticker_option = st.selectbox("Tickers", tickers_avail, index=tickers_avail.index(["SPY" if "SPY" in tickers_avail else tickers_avail[0]][0]))
                    ticker = ticker_option
                
                with charts__view:
                    try:
                        with cols[0]:
                            option__ = st.radio(
                                label="stars_radio",
                                options=list(stars_radio_dict.keys()),
                                key="signal_radio",
                                label_visibility='visible',
                                # disabled=st.session_state.disabled,
                                horizontal=True,
                            )
                        with cols[0]:
                            day_only_option = st.selectbox('Show Today Only', ['no', 'yes'], index=['no'].index('no'))
    
                        ticker_time_frame = f'{ticker}_{stars_radio_dict[option__]}'
                        df = POLLENSTORY[ticker_time_frame].copy()
                        st.markdown('<div style="text-align: center;">{}</div>'.format(ticker_option), unsafe_allow_html=True)

                        # star__view = its_morphin_time_view(QUEEN=QUEEN, STORY_bee=STORY_bee, ticker=ticker_option, POLLENSTORY=POLLENSTORY)

                        if day_only_option == 'yes':
                            df_day = df['timestamp_est'].iloc[-1]
                            df['date'] = df['timestamp_est'] # test

                            df_today = df[df['timestamp_est'] > (datetime.datetime.now().replace(hour=1, minute=1, second=1)).astimezone(est)].copy()
                            df_prior = df[~(df['timestamp_est'].isin(df_today['timestamp_est'].to_list()))].copy()

                            df = df_today

                        min_1 = POLLENSTORY[f'{ticker_option}{"_"}{"1Minute_1Day"}'].copy()
                        min_5 = POLLENSTORY[f'{ticker_option}{"_"}{"5Minute_5Day"}'].copy()
                        min_30m = POLLENSTORY[f'{ticker_option}{"_"}{"30Minute_1Month"}'].copy()
                        min_1hr = POLLENSTORY[f'{ticker_option}{"_"}{"1Hour_3Month"}'].copy()
                        min_2hr = POLLENSTORY[f'{ticker_option}{"_"}{"2Hour_6Month"}'].copy()
                        min_1yr = POLLENSTORY[f'{ticker_option}{"_"}{"1Day_1Year"}'].copy()


                    
                        if option__.lower() == 'all':
                            c1, c2 = st.columns(2)
                            with c1:
                                st.plotly_chart(create_main_macd_chart(min_1))
                            with c2:
                                st.plotly_chart(create_main_macd_chart(min_5))
                            c1, c2 = st.columns(2)
                            with c1:
                                st.plotly_chart(create_main_macd_chart(min_30m))
                            with c2:
                                st.plotly_chart(create_main_macd_chart(min_1hr))
                            c1, c2 = st.columns(2)
                            with c1:
                                st.plotly_chart(create_main_macd_chart(min_2hr))
                            with c2:
                                st.plotly_chart(create_main_macd_chart(min_1yr))
                        else:
                            # Main CHART Creation
                            radio_b_dict = {'1Min': '1Minute_1Day', 
                            '5Min': '5Minute_5Day', '30m': '30Minute_1Month', 
                            '1hr': '1Hour_3Month' , '2hr': '2Hour_6Month', '1Yr': '1Day_1Year'}
                            ticker_time_frame = f'{ticker}_{radio_b_dict[option__]}'
                            with cols[1]:
                                st.write(create_main_macd_chart(POLLENSTORY[ticker_time_frame].copy()))
                    except Exception as e:
                        print(e)
                        print_line_of_error()

                # if slope_option == 'yes':
                with slopes__view:
                    slope_cols = [i for i in df.columns if "slope" in i]
                    slope_cols.append("close")
                    slope_cols.append("timestamp_est")
                    slopes_df = df[['timestamp_est', 'hist_slope-3', 'hist_slope-6', 'macd_slope-3']]
                    fig = create_slope_chart(df=df)
                    st.plotly_chart(fig)
                    st.dataframe(slopes_df)
                    
                # if wave_option == "yes":
                with waves__view:
                    fig = create_wave_chart(df=df)
                    st.plotly_chart(fig)
                    
                    # dft = split_today_vs_prior(df=df)
                    # dft = dft['df_today']
                    fig=create_wave_chart_all(df=df, wave_col='buy_cross-0__wave')
                    st.plotly_chart(fig)

                    st.write("current wave")
                    current_buy_wave = df['buy_cross-0__wave_number'].tolist()
                    current_buy_wave = [int(i) for i in current_buy_wave]
                    current_buy_wave = max(current_buy_wave)
                    st.write("current wave number")
                    st.write(current_buy_wave)
                    dft = df[df['buy_cross-0__wave_number'] == str(current_buy_wave)].copy()
                    st.write({'current wave': [dft.iloc[0][['timestamp_est', 'close', 'macd']].values]})
                    fig=create_wave_chart_single(df=dft, wave_col='buy_cross-0__wave')
                    st.plotly_chart(fig)
            
            
                st.session_state['last_page'] = 'queen'
            
            
            except Exception as e:
                print(e)
                print_line_of_error()
            
            return True



        ########################################################
        ########################################################
        #############The Infinite Loop of Time #################
        ########################################################
        ########################################################
        ########################################################

        
        prod_keys_confirmed = QUEEN_KING['users_secrets']['prod_keys_confirmed']
        sandbox_keys_confirmed = QUEEN_KING['users_secrets']['sandbox_keys_confirmed']

        api = return_alpaca_user_apiKeys(QUEEN_KING=QUEEN_KING, authorized_user=authorized_user, prod=st.session_state['production'])
        
        try:
            api_failed = False
            snapshot = api.get_snapshot("SPY") # return_last_quote from snapshot
        except Exception as e:
            # requests.exceptions.HTTPError: 403 Client Error: Forbidden for url: https://data.alpaca.markets/v2/stocks/SPY/snapshot
            st.write("API Keys failed! You need to update, Please Go to your Alpaca Broker Account to Generate API Keys")
            # time.sleep(5)
            queen__account_keys(PB_App_Pickle=PB_App_Pickle, QUEEN_KING=QUEEN_KING, authorized_user=authorized_user, show_form=True) #EDRXZ Maever65teo
            api_failed = True

        if st.session_state['authorized_user']: ## MOVE THIS INTO pollenq?
            clean_out_app_requests(QUEEN=QUEEN, QUEEN_KING=QUEEN_KING, request_buckets=['subconscious', 'sell_orders', 'queen_sleep', 'update_queen_order'])
        
            # use API keys from user
            queenbee_online(QUEENsHeart=QUEENsHeart, admin=admin, dag='run_queenbee', api_failed=api_failed)
            queenbee_online(QUEENsHeart=QUEENsHeart, admin=admin, dag='run_workerbees', api_failed=api_failed)
            queenbee_online(QUEENsHeart=QUEENsHeart, admin=admin, dag='run_workerbees_crypto', api_failed=api_failed)

        # portfolio = return_alpc_portolio(api)['portfolio']
        acct_info = refresh_account_info(api=api)
        # ac_info = refresh_account_info(api=api)['info_converted']

        # # if authorized_user: log type auth and none
        log_dir = os.path.join(db_root, 'logs')
        init_logging(queens_chess_piece=queens_chess_piece, db_root=db_root, prod=st.session_state['production'])

        # db global
        # Ticker DataBase
        coin_exchange = "CBSE"
        ticker_db = return_QUEENs__symbols_data(QUEEN=QUEEN)
        POLLENSTORY = ticker_db['pollenstory']
        STORY_bee = ticker_db['STORY_bee']
        tickers_avail = [set(i.split("_")[0] for i in STORY_bee.keys())][0]
        # __ = tickers_avail if len(tickers_avail) > 0 else 'SPY'

        if authorized_user:
            option = st.sidebar.radio(
                label="main_radio",
                options=["queen", "controls", "model_results", "pollen_engine"],
                key="main_radio",
                label_visibility='visible',
                # disabled=st.session_state.disabled,
                horizontal=False,
            )
        else:
            option = st.sidebar.radio(
                label="PendingAuth",
                options=["queen", "controls", "charts", "model_results"],
                key="main_radio",
                label_visibility='visible',
                # disabled=st.session_state.disabled,
                horizontal=False,
                ) 



    def ticker_time_frame__option(tickers_avail_op, req_key):
        cols = st.columns(2)
        with cols[0]:
            if 'sel_tickers' not in st.session_state:
                st.session_state['sel_tickers'] = tickers_avail_op[0]

            tickers = st.multiselect('Symbols', options=list(tickers_avail_op), default=tickers_avail_op[0], help='View Groups of symbols to Inspect where to send the Bees', key=f'ticker{req_key}')
            if len(tickers) == 0:
                ticker_option = 'SPY'
            else:
                ticker_option = tickers[0]
        with cols[1]:
            if 'sel_stars' not in st.session_state:
                st.session_state['sel_stars'] = [i for i in stars().keys()]
            
            ttframe_list = list(set([i.split("_")[1] + "_" + i.split("_")[2] for i in POLLENSTORY.keys()]))
            frames = st.multiselect('Stars', options=list(ttframe_list), default=st.session_state['sel_stars'], help='View Groups of Stars to Allocate Bees on where to go', key=f'frame{req_key}')
            frame_option = frames[0]
        # frame_option = st.selectbox("Ticker_Stars", ttframe_list, index=ttframe_list.index(["1Minute_1Day" if "1Minute_1Day" in ttframe_list else ttframe_list[0]][0]))
        return {'tickers': tickers, 'ticker_option': ticker_option, 'frame_option': frame_option}


    try:

        if str(option).lower() == 'queen':
            
            with st.spinner("Waking Up the Hive"):

                tickers_avail_op = list(tickers_avail)

                cols = st.columns(2)

                queen_tabs = ["Chess Board","Wave Stories", "Charts"]
                chessboard_tab, wave_stories_tab, charts_tab = st.tabs(queen_tabs)

                if authorized_user:
                    return_total_profits(QUEEN=QUEEN)
                    # queens_subconscious_Thoughts(QUEEN=QUEEN)
                    stop_queenbee(QUEEN_KING=QUEEN_KING)
                    refresh_queenbee_controls(QUEEN_KING=QUEEN_KING)
                    clear_subconscious_Thought(QUEEN=QUEEN, QUEEN_KING=QUEEN_KING)
                

                with chessboard_tab:
                    update_Workerbees(QUEEN_KING=QUEEN_KING, admin=False)
                    if admin:
                        update_Workerbees(QUEEN_KING=QUEEN_KING, admin=admin)
                        with st.expander("admin QUEENS_ACTIVE"):
                            df = return_all_client_users__db()
                            # df = pd.DataFrame(KING['users'].get('client_users_db'))
                            # ipdb.set_trace()
                            allowed_list = KING['users']['client_user__allowed_queen_list']
                            df_map = pd.DataFrame(allowed_list)
                            df_map['queen_authorized'] = 'active'
                            df_map = df_map.rename(columns={0: 'email'})
                            
                            df = pd.merge(df, df_map, how='outer', on='email').fillna('')
                            grid = standard_AGgrid(data=df, use_checkbox=False, update_mode_value="MANUAL", grid_type='king_users')
                            grid_df = grid['data']

                            allowed_list_new = grid_df[grid_df['queen_authorized'] == 'active']
                            allowed_list_new = allowed_list_new['email'].tolist()

                            if allowed_list != allowed_list_new:
                                KING['users']['client_user__allowed_queen_list'] = allowed_list_new
                                PickleData(PB_KING_Pickle, KING, write_temp=False)
                                st.success("Auth Queen Users Updated")
                
                with wave_stories_tab:
                    queen_wavestories(QUEEN=QUEEN)
               
                with charts_tab:
                    # queen_chart(POLLENSTORY=POLLENSTORY)
                    advanced_charts(tickers_avail=tickers_avail_op, POLLENSTORY=POLLENSTORY)


                page_line_seperator(color=default_yellow_color)


        if str(option).lower() == 'model_results':
            model_wave_results(STORY_bee)

            cols = st.columns(2)

            with cols[0]:
                if 'sel_tickers' not in st.session_state:
                    st.session_state['sel_tickers'] = 'SPY'
                tickers = st.multiselect('Symbols', options=list(tickers_avail_op), default=st.session_state['sel_tickers'], help='View Groups of symbols to Inspect where to send the Bees')
                if len(tickers) == 0:
                    ticker_option = 'SPY'
                else:
                    ticker_option = tickers[0]
            with cols[1]:
                if 'sel_stars' not in st.session_state:
                    st.session_state['sel_stars'] = '1Minute_1Day'
                
                ttframe_list = list(set([i.split("_")[1] + "_" + i.split("_")[2] for i in POLLENSTORY.keys()]))
                frames = st.multiselect('Stars', options=list(ttframe_list), default=st.session_state['sel_stars'], help='View Groups of Stars to Allocate Bees on where to go')
                frame_option = frames[0]
                # frame_option = st.selectbox("Ticker_Stars", ttframe_list, index=ttframe_list.index(["1Minute_1Day" if "1Minute_1Day" in ttframe_list else ttframe_list[0]][0]))
            

            dict_list_ttf = analyze_waves(STORY_bee, ttframe_wave_trigbee=False)['d_agg_view_return']        
            for trigbee in dict_list_ttf[list(dict_list_ttf.keys())[0]]:
                
                ticker_selection = {k: v for k, v in dict_list_ttf.items() if ticker_option in k}
                buys = [data[trigbee] for k, data in ticker_selection.items()]
                df_trigbee_waves = pd.concat(buys, axis=0)
                col_view = ['ticker_time_frame'] + [i for i in df_trigbee_waves.columns if i not in 'ticker_time_frame']
                df_trigbee_waves = df_trigbee_waves[col_view]
                color = 'Green' if 'buy' in trigbee else 'Red'
                df_bestwaves = analyze_waves(STORY_bee, ttframe_wave_trigbee=df_trigbee_waves['ticker_time_frame'].iloc[-1])['df_bestwaves']

                t_winners = sum(df_trigbee_waves['winners_n'])
                t_losers = sum(df_trigbee_waves['losers_n'])
                total_waves = t_winners + t_losers
                win_pct = 100 * round(t_winners / total_waves, 2)

                t_maxprofits = sum(df_trigbee_waves['sum_maxprofit'])
                
                # Top Winners Header
                df_bestwaves = df_bestwaves[[col for col in df_bestwaves.columns if col not in ['wave_id', 'winners_n', 'loser_n']]]
                df_bestwaves = df_bestwaves[['maxprofit'] + [col for col in df_bestwaves.columns if col not in ['maxprofit']]]
                
                c1, c2, c3, c4 = st.columns((1,3,3,3))
                with c1:
                    flying_bee_gif()
                with c2:
                    mark_down_text(align='left', color=color, fontsize='15', text=f'{"Trigger Bee "}{trigbee}')
                with c3:
                    # write_flying_bee(25,25)
                    mark_down_text(align='left', color='Green', fontsize='15', text=f'{"~Total Max Profits "}{round(t_maxprofits * 100, 2)}{"%"}')
                with c4:
                    # write_flying_bee(28,28)
                    mark_down_text(align='left', color='Green', fontsize='15', text=f'{"~Win Pct "}{win_pct}{"%"}{": Winners "}{t_winners}{" :: Losers "}{t_losers}')

                # with st.expander(f'{"Todays Best Waves: "}{len(df_bestwaves)}', expanded=False):
                #     st.dataframe(df_bestwaves)
                # c1, c2, c3 = st.columns(3)
                # with c1:
                    # mark_down_text(color='Purple', align='center', text=f'{"All Ticker Bee Waves"}')
                with st.expander(f'{"Top "}{len(df_bestwaves)}{" Waves"}', expanded=False):
                    st.dataframe(df_bestwaves)
                # with c2:
                #     with st.expander(f'{"Top "}{len(df_bestwaves)}{" Waves"}', expanded=False):
                #         st.dataframe(df_bestwaves)

                with st.expander(f'{"All Ticker Bee Waves"}', expanded=False):
                    st.dataframe(df_trigbee_waves)
            page_line_seperator(color=default_yellow_color, height='3')


        if str(option).lower() == 'pollen_engine':
            # db_root = os.path.join(hive_master_root(), 'db')
            cols = st.columns(3)
            # with cols[1]:
            #     local_gif(gif_path=queen_flair_gif, height=350, width=400)
            
            page_tab_permission_denied(admin, st_stop=True)
            
            with st.expander("alpaca account info"):
                st.write(acct_info['info'])

            if admin:
                with st.expander('betty_bee'):
                    betty_bee = ReadPickleData(os.path.join(os.path.join(hive_master_root(), 'db'), 'betty_bee.pkl'))
                    df_betty = pd.DataFrame(betty_bee)
                    df_betty = df_betty.astype(str)
                    st.write(df_betty)
                
                with st.expander('users db'):
                    con = sqlite3.connect("db/client_users.db")
                    cur = con.cursor()

                    users = cur.execute("SELECT * FROM users").fetchall()
                    st.dataframe(pd.DataFrame(users))

            with st.expander('charlie_bee'):

                queens_charlie_bee = ReadPickleData(os.path.join(db_root, 'charlie_bee.pkl'))
                df_charlie = pd.DataFrame(queens_charlie_bee)
                df_charlie = df_charlie.astype(str)
                st.write(df_charlie)
            
            with st.expander('queen logs'):
                logs = os.listdir(log_dir)
                logs = [i for i in logs if i.endswith(".log")]
                log_file = st.selectbox('log files', list(logs))
                with open(os.path.join(log_dir, log_file), 'r') as f:
                    content = f.readlines()
                    st.write(content)
            
            
        page_session_state__cleanUp(page=page)

        if authorized_user:            
            st.session_state['last_page'] = 'queen'
            PickleData(PB_App_Pickle, QUEEN_KING)

        ##### END ####
    except Exception as e:
        print(e, print_line_of_error(), return_timestamp_string())
        # switch_page('pollenq')
if __name__ == '__main__':
    queen()