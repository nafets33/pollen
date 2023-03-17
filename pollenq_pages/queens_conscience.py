
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
from chess_piece.queen_hive import add_trading_model, set_chess_pieces_symbols, init_pollen_dbs, init_qcp, return_alpaca_user_apiKeys, return_queen_controls, return_STORYbee_trigbees, add_key_to_app, add_key_to_QUEEN, refresh_account_info, generate_TradingModel, stars, analyze_waves, story_view, return_alpc_portolio, ReadPickleData, pollen_themes, PickleData, return_timestamp_string, init_logging
from ozz.ozz_bee import send_ozz_call
# from chat_bot import ozz_bot
# from tqdm import tqdm
# from collections import defaultdict
import ipdb
# import matplotlib.pyplot as plt
# import base64


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

def queens_conscience(KING, QUEEN_KING):
    # from random import randint
    main_root = hive_master_root() # os.getcwd()  # hive root
    load_dotenv(os.path.join(main_root, ".env"))
    est = pytz.timezone("US/Eastern")
    utc = pytz.timezone('UTC')
    # ###### GLOBAL # ######
    active_order_state_list = ['running', 'running_close', 'submitted', 'error', 'pending', 'completed', 'completed_alpaca', 'running_open', 'archived_bee']

    # crypto
    crypto_currency_symbols = ['BTCUSD', 'ETHUSD', 'BTC/USD', 'ETH/USD']
    crypto_symbols__tickers_avail = ['BTCUSD', 'ETHUSD']


    # images
    MISC = local__filepaths_misc()
    flyingbee_grey_gif_path = MISC['flyingbee_grey_gif_path']
    power_gif = MISC['power_gif']
    uparrow_gif = MISC['uparrow_gif']
    learningwalk_bee = MISC['learningwalk_bee']
    runaway_bee_gif = MISC['runaway_bee_gif']

    learningwalk_bee = Image.open(learningwalk_bee)

    ##### STREAMLIT ###
    k_colors = streamlit_config_colors()
    default_text_color = k_colors['default_text_color'] # = '#59490A'
    default_font = k_colors['default_font'] # = "sans serif"
    default_yellow_color = k_colors['default_yellow_color'] # = '#C5B743'
    
    with st.spinner("Welcome to the QueensMind"):


        def chunk(it, size):
            it = iter(it)
            return iter(lambda: tuple(islice(it, size)), ())

        
        def queen_triggerbees():
            # cols = st.columns((1,5))
            now_time = datetime.datetime.now(est)
            req = return_STORYbee_trigbees(QUEEN=QUEEN, STORY_bee=STORY_bee, tickers_filter=False)
            active_trigs = req['active_trigs']
            all_current_trigs = req['all_current_trigs']
        
            # with cols[0]:
            if len(active_trigs) > 0:
                st.subheader("Active Bees")
                df = pd.DataFrame(active_trigs.items())
                df = df.rename(columns={0: 'ttf', 1: 'trig'})
                df = df.sort_values('ttf')
                # st.write(df)
                list_of_dicts = dict(zip(df['ttf'], df['trig']))
                list_of_dicts_ = [{k:v} for (k,v) in list_of_dicts.items() if 'buy_cross-0' in v]
                list_of_dicts_sell = [{k:v} for (k,v) in list_of_dicts.items() if 'sell_cross-0' in v]
                st.write("Active Buy Bees")
                chunk_write_dictitems_in_row(chunk_list=list_of_dicts_, title="Active Buy Bees", write_type="info", info_type='buy')
                st.write("Active Sell Bees")
                chunk_write_dictitems_in_row(chunk_list=list_of_dicts_sell, title="Active Sell Bees", write_type="info", info_type='sell')
                # g = {write_flying_bee() for i in range(len(df))}
            else:
                st.subheader("No one's flying")
                # mark_down_text(fontsize=12, color=default_text_color, text="No Active TriggerBees")
                local_gif(gif_path=flyingbee_grey_gif_path)     
                


            cq1, cq2, cq3, cq4 = st.columns((4,1,1,4))

            with cq4:
                if len(all_current_trigs) > 0:
                    with st.expander('All Available TriggerBees'):
                        mark_down_text(fontsize=15, color=default_text_color, text="All Available TriggerBees")
                        df = pd.DataFrame(all_current_trigs.items())
                        df = df.rename(columns={0: 'ttf', 1: 'trig'})
                        df = df.sort_values('ttf')
                        st.write(df)


        def queen_beeAction_theflash(Falseexpand=True):
    
            with st.expander("The Flash", False):
                cols = st.columns((1,1,1,2,1,1))
                with cols[5]:
                    local_gif(power_gif)

                with cols[0]:
                    quick_buy_long = st.button("FLASH BUY TQQQ")
                    quick_sell_long = st.button("FLASH SELL TQQQ")
                with cols[1]:   
                    quick_buy_short = st.button("FLASH BUY SQQQ")
                    quick_sell_short = st.button("FLASH SELL SQQQ")

                with cols[2]:
                    quick_buy_BTC = st.button("FLASH BUY BTC")
                    quick_sell_BTC = st.button("FLASH SELL BTC")
                with cols[3]:   
                    quick_buy_amt = st.selectbox("FLASH BUY $", [5000, 10000, 20000, 30000], index=[10000].index(10000))
                with cols[4]:
                    type_option = st.selectbox('type', ['market'], index=['market'].index('market'))                

                if quick_buy_short or quick_buy_long or quick_buy_BTC:
                    page_tab_permission_denied(admin=admin, st_stop=True)
                    
                    if quick_buy_short:
                        ticker = "SQQQ"
                    elif quick_buy_long:
                        ticker = "TQQQ"
                    elif quick_buy_BTC:
                        ticker = "BTCUSD"
                    
                    # get price convert to amount
                    if ticker in crypto_currency_symbols:
                        crypto = True
                        snap = api.get_crypto_snapshot(ticker, exchange=coin_exchange)
                        current_price = snap.latest_trade.price
                    else:
                        crypto = False
                        snap = api.get_snapshot(ticker)
                        current_price = snap.latest_trade.price
                    
                    info = api.get_account()
                    total_buying_power = info.buying_power # what is the % amount you want to buy?


                    validation = True # not > 50% of buying power COIN later
                    
                    if validation:
                        print("qty validated")
                        # process order signal                
                        order_dict = {'ticker': ticker,
                        'system': 'app',
                        'trig': 'app',
                        'request_time': datetime.datetime.now(est),
                        'wave_amo': quick_buy_amt,
                        'app_seen_price': current_price,
                        'side': 'buy',
                        'type': type_option,
                        'app_requests_id' : f'{"flashbuy"}{"_app-request_id_"}{return_timestamp_string()}{datetime.datetime.now().microsecond}'
                        }

                        app_req = create_AppRequest_package(request_name='buy_orders')

                        data = ReadPickleData(pickle_file=PB_App_Pickle)
                        data['buy_orders'].append(order_dict)
                        PickleData(pickle_file=PB_App_Pickle, data_to_store=data)


                        with cols[4]:
                            return_image_upon_save(title="Flash Request Delivered to the Queen", gif=runaway_bee_gif)
                
                page_line_seperator('1')

                # with cols[1]:
                ticker_time_frame = QUEEN['heartbeat']['available_tickers']
                if len(ticker_time_frame) == 0:
                    ticker_time_frame = list(set(i for i in STORY_bee.keys()))
                cols = st.columns((1,1,4, 1))
                with cols[0]:
                    initiate_waveup = st.button("Send Wave")
                with cols[1]:
                    ticker_wave_option = st.selectbox("Tickers", ticker_time_frame, index=ticker_time_frame.index(["SPY_1Minute_1Day" if "SPY_1Minute_1Day" in ticker_time_frame else ticker_time_frame[0]][0]))
                with cols[2]:
                    wave_button_sel = st.selectbox("Waves", ["buy_cross-0", "sell_cross-0"])
                with cols[3]:
                    local_gif(power_gif)


                if initiate_waveup:
                    wave_trigger = {ticker_wave_option: [wave_button_sel]}
                    order_dict = {'ticker': ticker_wave_option.split("_")[0],
                    'ticker_time_frame': ticker_wave_option,
                    'system': 'app',
                    'wave_trigger': wave_trigger,
                    'request_time': datetime.datetime.now(),
                    'app_requests_id' : f'{"theflash"}{"_"}{"waveup"}{"_app-request_id_"}{return_timestamp_string()}{datetime.datetime.now().microsecond}'
                    }

                    QUEEN_KING['wave_triggers'].append(order_dict)
                    PickleData(pickle_file=PB_App_Pickle, data_to_store=QUEEN_KING)
                    with cols[3]:
                        return_image_upon_save(title="Wave Request Delivered to the Queen")

        
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


        def return_buying_power(acct_info):
            with st.expander("Portfolio",  True):

                ac_info = acct_info['info_converted']
                num_text = "Total Buying Power: " + '${:,.2f}'.format(ac_info['buying_power'])
                mark_down_text(fontsize='18', text=num_text)
                # st.write(":heavy_minus_sign:" * 34)

                num_text = "last_equity: " + '${:,.2f}'.format(ac_info['last_equity'])
                mark_down_text(fontsize='15', text=num_text)

                num_text = "portfolio_value: " + '${:,.2f}'.format(ac_info['portfolio_value'])
                mark_down_text(fontsize='15', text=num_text)

                num_text = "Cash: " + '${:,.2f}'.format(ac_info['cash'])
                mark_down_text(fontsize='15', text=num_text)
                
                num_text = "Total Fees: " + '${:,.2f}'.format(ac_info['accrued_fees'])
                mark_down_text(fontsize='12', text=num_text)

        def portfolio_header__QC(ac_info):
                cols = st.columns((1,1,1,1,1,4,4,4))

                with cols[6]:
                    num_text = (ac_info['portfolio_value'] - ac_info['last_equity']) / ac_info['portfolio_value']
                    num_text = "Honey: " + '%{:,.4f}'.format(num_text)
                    mark_down_text(fontsize='18', text=num_text)
                with cols[7]:
                    num_text = ac_info['portfolio_value'] - ac_info['last_equity']
                    num_text = "Money: " + '${:,.2f}'.format(num_text)
                    mark_down_text(fontsize='18', text=num_text)
        
        def stop_queenbee(QUEEN_KING):
            checkbox_val = st.sidebar.button("Stop Queen", use_container_width=True)
            if checkbox_val:
                stop_queen = create_AppRequest_package(request_name='queen_sleep')

                QUEEN_KING['queen_sleep'].append(stop_queen)
                PickleData(PB_App_Pickle, QUEEN_KING)
                st.success("Queen Sleeps")
            
            return True





        def return_image_upon_save(title="Saved", width=33, gif=power_gif):
            local_gif(gif_path=gif)
            st.success(title)

        

        def clean_out_app_requests(QUEEN, QUEEN_KING, request_buckets):
            save = False
            for req_bucket in request_buckets:
                if req_bucket not in QUEEN_KING.keys():
                    st.write("Verison Missing DB: ", req_bucket)
                    continue
                for app_req in QUEEN_KING[req_bucket]:
                    if app_req['app_requests_id'] in QUEEN['app_requests__bucket']:
                        print(f'{app_req["client_order_id"]}__{req_bucket}__QUEEN Processed app Request__{app_req["app_requests_id"]}')
                        st.info(f'{app_req["client_order_id"]}__{req_bucket}__QUEEN Processed app Request__{app_req["app_requests_id"]}')
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
            
            users_allowed_queen_email = KING['users'].get('client_user__allowed_queen_list')
            now = datetime.datetime.now(est)

            if dag =='run_queenbee':
                if (now - QUEEN_KING['trigger_queen'].get('last_trig_date')).total_seconds() < 60:
                    st.write("Waking up your Queen She is a bit lazy today...it may take her up to 60 Seconds to get out of bed")
                    st.image(QUEEN_KING['character_image'], width=100)
                    return False
                # if (now - QUEEN_KING['trigger_queen'].get('last_trig_date')).total_seconds() < 86400:
                #     st.sidebar.write("Awaiting Queen")
                #     return False
                
                if api_failed:
                    st.write("you need to setup your Broker Queens to Turn on your Queen See Account Keys Below")
                    return False

                # if (now - QUEEN['pq_last_modified']['pq_last_modified']).total_seconds() > 60:
                if 'heartbeat_time' not in QUEENsHeart.keys():
                    st.write("You Need a Queen")
                    return False
                
                if (now - QUEENsHeart['heartbeat_time']).total_seconds() > 60:
                    # st.write("YOUR QUEEN if OFFLINE")
                    cols = st.columns((3,1,1,1,1))
                    with cols[2]:
                        st.error("Your Queen Is Asleep Wake Her UP!")
                    with cols[3]:
                        wake_up_queen_button = st.button("Wake Her Up")
                        # wake_up_queen_button = cust_Button(file_path_url="misc/sleeping_queen_gif.gif", height='50px', key='b')
                        if wake_up_queen_button and st.session_state['authorized_user']:
                            # check to ensure queen is offline before proceeding 
                            if (now - QUEENsHeart['heartbeat_time']).total_seconds() < 60:
                                return False
                            
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

                    with cols[4]:
                        local_gif(gif_path=flyingbee_grey_gif_path)


                    return False
                else:
                    return True
            elif dag =='run_workerbees':
                if admin:
                    if st.sidebar.button("Flying Bees", use_container_width=True):
                        trigger_airflow_dag(dag=dag, client_username=st.session_state['username'], prod=prod)
                        st.write("Bees Fly")
                return True
            elif dag =='run_workerbees_crypto':
                if admin:
                    if st.sidebar.button("Flying Crypto Bees", use_container_width=True):
                        trigger_airflow_dag(dag=dag, client_username=st.session_state['username'], prod=prod)
                        st.write("Crypto Bees Fly")
                return True
            else:
                return False

        
        def chunk_write_dictitems_in_row(chunk_list, max_n=10, write_type='checkbox', title="Active Models", groupby_qcp=False, info_type='buy'):

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
        
       
        def page_tab_permission_denied(admin, st_stop=True):
            if admin == False:
                st.warning("permission denied you need a Queen to access")
                if st_stop:
                    st.info("Page Stopped")
                    st.stop()
            
        def add_new_qcp__to_Queens_workerbees(qcp_bees_key):
            with st.form('add new qcp'):
                avail_qcp = ['pawn1', 'pawn2', 'pawn3', 'pawn4']
                avail_tickers = ['QQQ']
                # tickers_to_add = st.multiselect(label=f'Add Symbols', options=avail_tickers, help=f'Try not to Max out number of piecesm, only ~10 allowed')
                cols = st.columns((1,2,10,3,2,2))
                with cols[1]:                
                    qcp = st.selectbox(label='qcp', key=f'qcp_new', options=avail_qcp)
                    QUEEN_KING[qcp_bees_key][qcp] = init_qcp(init_macd_vars={'fast': 12, 'slow': 26, 'smooth': 9}, ticker_list=[])
                with cols[0]:
                    st.image(MISC.get('queen_crown_url'), width=64)
                with cols[2]:
                    QUEEN_KING[qcp_bees_key][qcp]['tickers'] = st.multiselect(label=f'{qcp} symbols', options=avail_tickers, default=None, help='Try not to Max out number of piecesm, only ~10 allowed')
                with cols[3]:
                    QUEEN_KING[qcp_bees_key][qcp]['MACD_fast_slow_smooth']['fast'] = st.number_input("fast", min_value=1, max_value=33, value=int(QUEEN_KING[qcp_bees_key][qcp]['MACD_fast_slow_smooth']['fast']), key=f'{qcp}fast')
                with cols[4]:
                    QUEEN_KING[qcp_bees_key][qcp]['MACD_fast_slow_smooth']['slow'] = st.number_input("slow", min_value=1, max_value=33, value=int(QUEEN_KING[qcp_bees_key][qcp]['MACD_fast_slow_smooth']['slow']), key=f'{qcp}slow')
                with cols[5]:
                    QUEEN_KING[qcp_bees_key][qcp]['MACD_fast_slow_smooth']['smooth'] = st.number_input("smooth", min_value=1, max_value=33, value=int(QUEEN_KING[qcp_bees_key][qcp]['MACD_fast_slow_smooth']['smooth']), key=f'{qcp}smooth')            

                if st.form_submit_button('Save New qcp'):
                    PickleData(PB_App_Pickle, QUEEN_KING)


        def on_click_ss_value_bool(name):
            st.session_state[name] = True


        def chessboard(QUEEN_KING, admin=False):
            ticker_allowed = list(KING['ticker_universe'].get('alpaca_symbols_dict').keys()) + crypto_symbols__tickers_avail
            
            current_setup = QUEEN_KING['chess_board']
            chess_pieces = set_chess_pieces_symbols(QUEEN_KING=QUEEN_KING)
            view = chess_pieces.get('view')
            all_workers = chess_pieces.get('all_workers')
            qcp_ticker_index = chess_pieces.get('qcp_ticker_index')
            current_tickers = qcp_ticker_index.keys()
            # st.write(current_tickers)
            
            name = 'Workerbees_Admin' if admin else 'Chess Board'
            qcp_bees_key = 'qcp_workerbees' if admin else 'chess_board'

            with st.expander(name, True):
                with st.form(f'Update WorkerBees{admin}'):
                    
                    ticker_search = st.text_input("Find Symbol") ####### WORKERBEE

                    cols = st.columns((1,1,1))
                    # with cols[0]:
                    #     if cust_Button("https://p7.hiclipart.com/preview/221/313/319/chess-piece-knight-rook-board-game-chess.jpg", height='34px', key='k12', hoverText="Game of Chess, Allocate your portoflio, Each Theme is the Overall Trading Stratergy"):
                    #         st.info("Game of Chess, Allocate your portoflio, Each Theme is the Overall Trading Stratergy")
                        # if cust_Button(MISC.get('pawn_png_url'), height='34px', key='k11'):
                        # st.write(st.session_state['chess_board'])
                        # if st.session_state['chess_board'] == True:
                            # st.info("Game of Chess, Allocate your portoflio, Each Theme is the Overall Trading Stratergy")
                        ## generate info messages with click ok to exit message
                        # st.markdown(f'<img src="{image}"', unsafe_allow_html=True)
                    #     image = "https://p7.hiclipart.com/preview/221/313/319/chess-piece-knight-rook-board-game-chess.jpg"
                    #     st.markdown(f'<img src="{image}" style="background-color:transparent">', unsafe_allow_html=True)
                    themes = list(pollen_themes(KING).keys())
                    with cols[1]:
                        st.subheader(name)
                    cols = st.columns((1,4,2,2,1,1,1,1))
                    for qcp in all_workers:
                        if qcp == 'castle_coin':
                            with cols[0]:
                                st.image("https://s3.us-east-2.amazonaws.com/nomics-api/static/images/currencies/BSV.png", width=54)
                                
                            with cols[1]:
                                QUEEN_KING[qcp_bees_key][qcp]['tickers'] = st.multiselect(label=f'symbols', options=ticker_allowed + crypto_symbols__tickers_avail, default=QUEEN_KING[qcp_bees_key][qcp]['tickers'], help='Castle Should Hold your Highest Valued Symbols', key=f'{qcp}tickers{admin}')
                            with cols[2]:
                                st.selectbox(label='Model', options=['MACD'], key=f'{qcp}model{admin}')
                            with cols[3]:
                                QUEEN_KING[qcp_bees_key][qcp]['theme'] = st.selectbox(label=f'theme', options=themes, index=themes.index(QUEEN_KING[qcp_bees_key][qcp].get('theme')), help='Trading Star Strategy, You May Customize Trading Models', key=f'{qcp}theme{admin}')
                            with cols[4]:
                                QUEEN_KING[qcp_bees_key][qcp]['MACD_fast_slow_smooth']['fast'] = st.number_input("fast", min_value=1, max_value=88, value=int(QUEEN_KING[qcp_bees_key][qcp]['MACD_fast_slow_smooth']['fast']), key=f'{qcp}fast{admin}')
                            with cols[5]:
                                QUEEN_KING[qcp_bees_key][qcp]['MACD_fast_slow_smooth']['slow'] = st.number_input("slow", min_value=1, max_value=88, value=int(QUEEN_KING[qcp_bees_key][qcp]['MACD_fast_slow_smooth']['slow']), key=f'{qcp}slow{admin}')
                            with cols[6]:
                                QUEEN_KING[qcp_bees_key][qcp]['MACD_fast_slow_smooth']['smooth'] = st.number_input("smooth", min_value=1, max_value=88, value=int(QUEEN_KING[qcp_bees_key][qcp]['MACD_fast_slow_smooth']['smooth']), key=f'{qcp}smooth{admin}')
                                
                        if qcp == 'castle':
                            with cols[0]:
                                st.image(MISC.get('castle_png'), width=54)

                            with cols[1]:
                                QUEEN_KING[qcp_bees_key][qcp]['tickers'] = st.multiselect(label=f'symbols', options=ticker_allowed + crypto_symbols__tickers_avail, default=QUEEN_KING[qcp_bees_key][qcp]['tickers'], help='Castle Should Hold your Highest Valued Symbols', key=f'{qcp}tickers{admin}')
                            with cols[2]:
                                st.selectbox(label='Model', options=['MACD'], key=f'{qcp}model{admin}')
                            with cols[3]:
                                QUEEN_KING[qcp_bees_key][qcp]['theme'] = st.selectbox(label=f'theme', options=themes, index=themes.index(QUEEN_KING[qcp_bees_key][qcp].get('theme')), help='Trading Star Strategy, You May Customize Trading Models', key=f'{qcp}theme{admin}')
                            with cols[4]:
                                QUEEN_KING[qcp_bees_key][qcp]['MACD_fast_slow_smooth']['fast'] = st.number_input("fast", min_value=1, max_value=88, value=int(QUEEN_KING[qcp_bees_key][qcp]['MACD_fast_slow_smooth']['fast']), key=f'{qcp}fast{admin}')
                            with cols[5]:
                                QUEEN_KING[qcp_bees_key][qcp]['MACD_fast_slow_smooth']['slow'] = st.number_input("slow", min_value=1, max_value=88, value=int(QUEEN_KING[qcp_bees_key][qcp]['MACD_fast_slow_smooth']['slow']), key=f'{qcp}slow{admin}')
                            with cols[6]:
                                QUEEN_KING[qcp_bees_key][qcp]['MACD_fast_slow_smooth']['smooth'] = st.number_input("smooth", min_value=1, max_value=88, value=int(QUEEN_KING[qcp_bees_key][qcp]['MACD_fast_slow_smooth']['smooth']), key=f'{qcp}smooth{admin}')


                        if qcp == 'bishop':
                            with cols[0]:
                                st.image(MISC.get('bishop_png'), width=74)

                            with cols[1]:
                                QUEEN_KING[qcp_bees_key][qcp]['tickers'] = st.multiselect(label=f'symbols', options=ticker_allowed + crypto_symbols__tickers_avail, default=QUEEN_KING[qcp_bees_key][qcp]['tickers'], help='Castle Should Hold your Highest Valued Symbols', key=f'{qcp}tickers{admin}')
                            with cols[2]:
                                st.selectbox(label='Model', options=['MACD'], key=f'{qcp}model{admin}')
                            with cols[3]:
                                QUEEN_KING[qcp_bees_key][qcp]['theme'] = st.selectbox(label=f'theme', options=themes, index=themes.index(QUEEN_KING[qcp_bees_key][qcp].get('theme')), help='Trading Star Strategy, You May Customize Trading Models', key=f'{qcp}theme{admin}')
                            with cols[4]:
                                QUEEN_KING[qcp_bees_key][qcp]['MACD_fast_slow_smooth']['fast'] = st.number_input("fast", min_value=1, max_value=88, value=int(QUEEN_KING[qcp_bees_key][qcp]['MACD_fast_slow_smooth']['fast']), key=f'{qcp}fast{admin}')
                            with cols[5]:
                                QUEEN_KING[qcp_bees_key][qcp]['MACD_fast_slow_smooth']['slow'] = st.number_input("slow", min_value=1, max_value=88, value=int(QUEEN_KING[qcp_bees_key][qcp]['MACD_fast_slow_smooth']['slow']), key=f'{qcp}slow{admin}')
                            with cols[6]:
                                QUEEN_KING[qcp_bees_key][qcp]['MACD_fast_slow_smooth']['smooth'] = st.number_input("smooth", min_value=1, max_value=88, value=int(QUEEN_KING[qcp_bees_key][qcp]['MACD_fast_slow_smooth']['smooth']), key=f'{qcp}smooth{admin}')


                        if qcp == 'knight':
                            with cols[0]:
                                st.image(MISC.get('knight_png'), width=74)
                            
                            with cols[1]:
                                QUEEN_KING[qcp_bees_key][qcp]['tickers'] = st.multiselect(label=f'symbols', options=ticker_allowed + crypto_symbols__tickers_avail, default=QUEEN_KING[qcp_bees_key][qcp]['tickers'], help='Castle Should Hold your Highest Valued Symbols', key=f'{qcp}tickers{admin}')
                            with cols[2]:
                                st.selectbox(label='Model', options=['MACD'], key=f'{qcp}model{admin}')
                            with cols[3]:
                                QUEEN_KING[qcp_bees_key][qcp]['theme'] = st.selectbox(label=f'theme', options=themes, index=themes.index(QUEEN_KING[qcp_bees_key][qcp].get('theme')), help='Trading Star Strategy, You May Customize Trading Models', key=f'{qcp}theme{admin}')
                            with cols[4]:
                                QUEEN_KING[qcp_bees_key][qcp]['MACD_fast_slow_smooth']['fast'] = st.number_input("fast", min_value=1, max_value=88, value=int(QUEEN_KING[qcp_bees_key][qcp]['MACD_fast_slow_smooth']['fast']), key=f'{qcp}fast{admin}')
                            with cols[5]:
                                QUEEN_KING[qcp_bees_key][qcp]['MACD_fast_slow_smooth']['slow'] = st.number_input("slow", min_value=1, max_value=88, value=int(QUEEN_KING[qcp_bees_key][qcp]['MACD_fast_slow_smooth']['slow']), key=f'{qcp}slow{admin}')
                            with cols[6]:
                                QUEEN_KING[qcp_bees_key][qcp]['MACD_fast_slow_smooth']['smooth'] = st.number_input("smooth", min_value=1, max_value=88, value=int(QUEEN_KING[qcp_bees_key][qcp]['MACD_fast_slow_smooth']['smooth']), key=f'{qcp}smooth{admin}')
                


                    if st.form_submit_button('Save Workers'):
                        if authorized_user == False:
                            st.warning("You Need your Queen First! Please contact pollenq.queen@gmail.com")
                            return False
                    if st.form_submit_button('Reset ChessBoards Trading Models With Theme', on_click=on_click_ss_value_bool('reset_chessboard_theme')):
                        if authorized_user == False:
                            st.warning("You Need your Queen First! Please contact pollenq.queen@gmail.com")
                            return False


                        def handle__new_tickers__AdjustTradingModels(QUEEN_KING, reset_theme=False):
                            # add new trading models if needed
                            # Castle 
                            for workerbee, bees_data in QUEEN_KING[qcp_bees_key].items():
                                for ticker in bees_data.get('tickers'):
                                    print("UPDATE MODELS")
                                    theme = bees_data.get('theme')
                                    QUEEN_KING = add_trading_model(status='active', PB_APP_Pickle=PB_App_Pickle, QUEEN_KING=QUEEN_KING, ticker=ticker, workerbee=workerbee, theme=theme, reset_theme=reset_theme)
                            
                            return QUEEN_KING
                        

                        reset_theme = True if 'reset_chessboard_theme' in st.session_state and st.session_state['reset_chessboard_theme'] else False
                        print(reset_theme)
                        QUEEN_KING = handle__new_tickers__AdjustTradingModels(QUEEN_KING=QUEEN_KING, reset_theme=reset_theme)
                        
                        app_req = create_AppRequest_package(request_name='workerbees')
                        QUEEN_KING['workerbees_requests'].append(app_req)
                        PickleData(pickle_file=PB_App_Pickle, data_to_store=QUEEN_KING)
                        st.success("New Move Saved")
                        
                        return True


        def chess_board__workerbees(QUEEN_KING, admin=True):

            try:

                ticker_allowed = list(KING['ticker_universe'].get('alpaca_symbols_dict').keys()) + crypto_symbols__tickers_avail
                
                current_setup = QUEEN_KING['chess_board']
                chess_pieces = set_chess_pieces_symbols(QUEEN_KING=QUEEN_KING)
                view = chess_pieces.get('view')
                all_workers = chess_pieces.get('all_workers')
                qcp_ticker_index = chess_pieces.get('qcp_ticker_index')
                current_tickers = qcp_ticker_index.keys()
                # st.write(current_tickers)
                
                name = 'Workerbees_Admin' if admin else 'Chess Board'
                qcp_bees_key = 'qcp_workerbees' if admin else 'chess_board'
                
                add_new_qcp__to_Queens_workerbees(qcp_bees_key)

                with st.expander(name, True):

                    with st.form(f'Update WorkerBees{admin}'):
                        
                        ticker_search = st.text_input("Find Symbol") ####### WORKERBEE

                        cols = st.columns((1,1,1))
                        # with cols[0]:
                        #     if cust_Button("https://p7.hiclipart.com/preview/221/313/319/chess-piece-knight-rook-board-game-chess.jpg", height='34px', key='k12', hoverText="Game of Chess, Allocate your portoflio, Each Theme is the Overall Trading Stratergy"):
                        #         st.info("Game of Chess, Allocate your portoflio, Each Theme is the Overall Trading Stratergy")
                            # if cust_Button(MISC.get('pawn_png_url'), height='34px', key='k11'):
                            # st.write(st.session_state['chess_board'])
                            # if st.session_state['chess_board'] == True:
                                # st.info("Game of Chess, Allocate your portoflio, Each Theme is the Overall Trading Stratergy")
                            ## generate info messages with click ok to exit message
                            # st.markdown(f'<img src="{image}"', unsafe_allow_html=True)
                        #     image = "https://p7.hiclipart.com/preview/221/313/319/chess-piece-knight-rook-board-game-chess.jpg"
                        #     st.markdown(f'<img src="{image}" style="background-color:transparent">', unsafe_allow_html=True)
                        themes = list(pollen_themes(KING).keys())
                        with cols[1]:
                            st.subheader(name)
                        cols = st.columns((1,4,2,2,1,1,1,1))
                        for qcp in all_workers:
                            if qcp == 'castle_coin':
                                with cols[0]:
                                    st.image("https://s3.us-east-2.amazonaws.com/nomics-api/static/images/currencies/BSV.png", width=54)
                                    
                                with cols[1]:
                                    QUEEN_KING[qcp_bees_key][qcp]['tickers'] = st.multiselect(label=f'symbols', options=ticker_allowed + crypto_symbols__tickers_avail, default=QUEEN_KING[qcp_bees_key][qcp]['tickers'], help='Castle Should Hold your Highest Valued Symbols', key=f'{qcp}tickers{admin}')
                                with cols[2]:
                                    st.selectbox(label='Model', options=['MACD'], key=f'{qcp}model{admin}')
                                with cols[3]:
                                    QUEEN_KING[qcp_bees_key][qcp]['theme'] = st.selectbox(label=f'theme', options=themes, index=themes.index(QUEEN_KING[qcp_bees_key][qcp].get('theme')), help='Trading Star Strategy, You May Customize Trading Models', key=f'{qcp}theme{admin}')
                                with cols[4]:
                                    QUEEN_KING[qcp_bees_key][qcp]['MACD_fast_slow_smooth']['fast'] = st.number_input("fast", min_value=1, max_value=88, value=int(QUEEN_KING[qcp_bees_key][qcp]['MACD_fast_slow_smooth']['fast']), key=f'{qcp}fast{admin}')
                                with cols[5]:
                                    QUEEN_KING[qcp_bees_key][qcp]['MACD_fast_slow_smooth']['slow'] = st.number_input("slow", min_value=1, max_value=88, value=int(QUEEN_KING[qcp_bees_key][qcp]['MACD_fast_slow_smooth']['slow']), key=f'{qcp}slow{admin}')
                                with cols[6]:
                                    QUEEN_KING[qcp_bees_key][qcp]['MACD_fast_slow_smooth']['smooth'] = st.number_input("smooth", min_value=1, max_value=88, value=int(QUEEN_KING[qcp_bees_key][qcp]['MACD_fast_slow_smooth']['smooth']), key=f'{qcp}smooth{admin}')
                                    
                            if qcp == 'castle':
                                with cols[0]:
                                    st.image(MISC.get('castle_png'), width=54)

                                with cols[1]:
                                    QUEEN_KING[qcp_bees_key][qcp]['tickers'] = st.multiselect(label=f'symbols', options=ticker_allowed + crypto_symbols__tickers_avail, default=QUEEN_KING[qcp_bees_key][qcp]['tickers'], help='Castle Should Hold your Highest Valued Symbols', key=f'{qcp}tickers{admin}')
                                with cols[2]:
                                    st.selectbox(label='Model', options=['MACD'], key=f'{qcp}model{admin}')
                                with cols[3]:
                                    QUEEN_KING[qcp_bees_key][qcp]['theme'] = st.selectbox(label=f'theme', options=themes, index=themes.index(QUEEN_KING[qcp_bees_key][qcp].get('theme')), help='Trading Star Strategy, You May Customize Trading Models', key=f'{qcp}theme{admin}')
                                with cols[4]:
                                    QUEEN_KING[qcp_bees_key][qcp]['MACD_fast_slow_smooth']['fast'] = st.number_input("fast", min_value=1, max_value=88, value=int(QUEEN_KING[qcp_bees_key][qcp]['MACD_fast_slow_smooth']['fast']), key=f'{qcp}fast{admin}')
                                with cols[5]:
                                    QUEEN_KING[qcp_bees_key][qcp]['MACD_fast_slow_smooth']['slow'] = st.number_input("slow", min_value=1, max_value=88, value=int(QUEEN_KING[qcp_bees_key][qcp]['MACD_fast_slow_smooth']['slow']), key=f'{qcp}slow{admin}')
                                with cols[6]:
                                    QUEEN_KING[qcp_bees_key][qcp]['MACD_fast_slow_smooth']['smooth'] = st.number_input("smooth", min_value=1, max_value=88, value=int(QUEEN_KING[qcp_bees_key][qcp]['MACD_fast_slow_smooth']['smooth']), key=f'{qcp}smooth{admin}')


                            if qcp == 'bishop':
                                with cols[0]:
                                    st.image(MISC.get('bishop_png'), width=74)

                                with cols[1]:
                                    QUEEN_KING[qcp_bees_key][qcp]['tickers'] = st.multiselect(label=f'symbols', options=ticker_allowed + crypto_symbols__tickers_avail, default=QUEEN_KING[qcp_bees_key][qcp]['tickers'], help='Castle Should Hold your Highest Valued Symbols', key=f'{qcp}tickers{admin}')
                                with cols[2]:
                                    st.selectbox(label='Model', options=['MACD'], key=f'{qcp}model{admin}')
                                with cols[3]:
                                    QUEEN_KING[qcp_bees_key][qcp]['theme'] = st.selectbox(label=f'theme', options=themes, index=themes.index(QUEEN_KING[qcp_bees_key][qcp].get('theme')), help='Trading Star Strategy, You May Customize Trading Models', key=f'{qcp}theme{admin}')
                                with cols[4]:
                                    QUEEN_KING[qcp_bees_key][qcp]['MACD_fast_slow_smooth']['fast'] = st.number_input("fast", min_value=1, max_value=88, value=int(QUEEN_KING[qcp_bees_key][qcp]['MACD_fast_slow_smooth']['fast']), key=f'{qcp}fast{admin}')
                                with cols[5]:
                                    QUEEN_KING[qcp_bees_key][qcp]['MACD_fast_slow_smooth']['slow'] = st.number_input("slow", min_value=1, max_value=88, value=int(QUEEN_KING[qcp_bees_key][qcp]['MACD_fast_slow_smooth']['slow']), key=f'{qcp}slow{admin}')
                                with cols[6]:
                                    QUEEN_KING[qcp_bees_key][qcp]['MACD_fast_slow_smooth']['smooth'] = st.number_input("smooth", min_value=1, max_value=88, value=int(QUEEN_KING[qcp_bees_key][qcp]['MACD_fast_slow_smooth']['smooth']), key=f'{qcp}smooth{admin}')


                            if qcp == 'knight':
                                with cols[0]:
                                    st.image(MISC.get('knight_png'), width=74)
                                
                                with cols[1]:
                                    QUEEN_KING[qcp_bees_key][qcp]['tickers'] = st.multiselect(label=f'symbols', options=ticker_allowed + crypto_symbols__tickers_avail, default=QUEEN_KING[qcp_bees_key][qcp]['tickers'], help='Castle Should Hold your Highest Valued Symbols', key=f'{qcp}tickers{admin}')
                                with cols[2]:
                                    st.selectbox(label='Model', options=['MACD'], key=f'{qcp}model{admin}')
                                with cols[3]:
                                    QUEEN_KING[qcp_bees_key][qcp]['theme'] = st.selectbox(label=f'theme', options=themes, index=themes.index(QUEEN_KING[qcp_bees_key][qcp].get('theme')), help='Trading Star Strategy, You May Customize Trading Models', key=f'{qcp}theme{admin}')
                                with cols[4]:
                                    QUEEN_KING[qcp_bees_key][qcp]['MACD_fast_slow_smooth']['fast'] = st.number_input("fast", min_value=1, max_value=88, value=int(QUEEN_KING[qcp_bees_key][qcp]['MACD_fast_slow_smooth']['fast']), key=f'{qcp}fast{admin}')
                                with cols[5]:
                                    QUEEN_KING[qcp_bees_key][qcp]['MACD_fast_slow_smooth']['slow'] = st.number_input("slow", min_value=1, max_value=88, value=int(QUEEN_KING[qcp_bees_key][qcp]['MACD_fast_slow_smooth']['slow']), key=f'{qcp}slow{admin}')
                                with cols[6]:
                                    QUEEN_KING[qcp_bees_key][qcp]['MACD_fast_slow_smooth']['smooth'] = st.number_input("smooth", min_value=1, max_value=88, value=int(QUEEN_KING[qcp_bees_key][qcp]['MACD_fast_slow_smooth']['smooth']), key=f'{qcp}smooth{admin}')
                    
                        if st.form_submit_button('Save Workers'):
                            if authorized_user == False:
                                st.warning("You Need your Queen First! Please contact pollenq.queen@gmail.com")
                                return False
                        if st.form_submit_button('Reset ChessBoards Trading Models With Theme', on_click=on_click_ss_value_bool('reset_chessboard_theme')):
                            if authorized_user == False:
                                st.warning("You Need your Queen First! Please contact pollenq.queen@gmail.com")
                                return False


                            def handle__new_tickers__AdjustTradingModels(QUEEN_KING, reset_theme=False):
                                # add new trading models if needed
                                # Castle 
                                for workerbee, bees_data in QUEEN_KING[qcp_bees_key].items():
                                    for ticker in bees_data.get('tickers'):
                                        print("UPDATE MODELS")
                                        theme = bees_data.get('theme')
                                        QUEEN_KING = add_trading_model(status='active', PB_APP_Pickle=PB_App_Pickle, QUEEN_KING=QUEEN_KING, ticker=ticker, workerbee=workerbee, theme=theme, reset_theme=reset_theme)
                                
                                return QUEEN_KING
                            

                            reset_theme = True if 'reset_chessboard_theme' in st.session_state and st.session_state['reset_chessboard_theme'] else False
                            print(reset_theme)
                            QUEEN_KING = handle__new_tickers__AdjustTradingModels(QUEEN_KING=QUEEN_KING, reset_theme=reset_theme)
                            
                            app_req = create_AppRequest_package(request_name='workerbees')
                            QUEEN_KING['workerbees_requests'].append(app_req)
                            PickleData(pickle_file=PB_App_Pickle, data_to_store=QUEEN_KING)
                            st.success("New Move Saved")
                            
                            return True


                return True
            except Exception as e:
                print(e, print_line_of_error())

        
        def refresh_tickers_TradingModels(QUEEN_KING, ticker, theme):
            print("update generate trading model")
            tradingmodel1 = generate_TradingModel(ticker=ticker, status='active', theme=theme)['MACD'][ticker]
            # QUEEN_KING['king_controls_queen']['symbols_stars_TradingModel'].update(tradingmodel1)
            QUEEN_KING['king_controls_queen']['symbols_stars_TradingModel'][ticker] = tradingmodel1
            return QUEEN_KING




        
        def update_trading_models(QUEEN_KING, pollen_themes_selections):
        # elif control_option.lower() == 'symbols_stars_tradingmodel':
            # add: ticker_family, short position and macd/hist story 
            # queen__write_active_symbols(QUEEN_KING=QUEEN_KING)
            try:
                control_option = 'symbols_stars_TradingModel'
                cols = st.columns((1,4))
                with cols[0]:
                    saved_avail = list(QUEEN_KING['saved_trading_models'].keys()) + ['select']
                    saved_model_ticker = st.selectbox("View Saved Model", options=saved_avail, index=saved_avail.index('select'), help="This will display Saved Model")
                page_line_seperator(height='1')

                # mark_down_text(color='Black', text='Ticker Model')
                if saved_model_ticker != 'select':
                    title = f'{"Viewing a Saved Not active Ticker Model"}'
                else:
                    title = "Current Ticker Model"
                
                st.header(title)

                cols = st.columns(4)
                with cols[0]:
                    models_avail = list(QUEEN_KING['king_controls_queen'][control_option].keys())
                    ticker_option_qc = st.selectbox("Symbol", models_avail, index=models_avail.index(["SPY" if "SPY" in models_avail else models_avail[0]][0]))                

                if saved_model_ticker != 'select':
                    st.info("You Are Viewing Saved Model")
                    trading_model = QUEEN_KING['saved_trading_models'][saved_model_ticker]
                else:
                    trading_model = QUEEN_KING['king_controls_queen'][control_option][ticker_option_qc]

                star_avail = list(trading_model['stars_kings_order_rules'].keys())
                trigbees_avail = list(trading_model['trigbees'].keys())
                blocktime_avail = list(trading_model['time_blocks'].keys())
                
                with cols[1]:
                    star_option_qc = st.selectbox("Star", star_avail, index=star_avail.index(["1Minute_1Day" if "1Minute_1Day" in star_avail else star_avail[0]][0]))
                with cols[2]:
                    trigbee_sel = st.selectbox("Trigbee", trigbees_avail, index=trigbees_avail.index(["buy_cross-0" if "buy_cross-0" in trigbees_avail else trigbees_avail[0]][0]))
                with cols[3]:
                    # wave_blocks_option = st.selectbox("Block Time", KING['waveBlocktimes'])
                    wave_blocks_option = st.selectbox("BlockTime", blocktime_avail, index=blocktime_avail.index(["morning_9-11" if "morning_9-11" in blocktime_avail else blocktime_avail[0]][0]))
                    
                trading_model__star = trading_model['stars_kings_order_rules'][star_option_qc]

                ticker_model_level_1 = {
                        'portforlio_weight_ask': {'type': 'portforlio_weight_ask'},
                        'QueenBeeTrader': {'type': None}, # not allowed to change
                        'status': {'type': 'status', 'list': ['active', 'not_active']},
                        'buyingpower_allocation_LongTerm': {'type': 'numberslider', 'min': 0, 'max': 1},
                        'buyingpower_allocation_ShortTerm': {'type': None}, # returns opposite of LongTerm
                        'index_long_X': {'type': 'index_long_X', 'list': ['1X', '2X', '3X']},
                        'index_inverse_X': {'type': 'index_inverse_X', 'list': ['1X', '2X', '3X']},
                        'total_budget': {'type': 'total_budget'},
                        'max_single_trade_amount': {'type': 'number'},
                        'allow_for_margin': {'type': 'allow_for_margin'}, 
                        'buy_ONLY_by_accept_from_QueenBeeTrader': {'type': 'buy_ONLY_by_accept_from_QueenBeeTrader'},
                        'trading_model_name': {'type': None}, # not allowed to change
                        'portfolio_name': {'type': None}, # not allowed to change
                        'trigbees': {'type': 'trigbees', 'list': ['active', 'not_active']},
                        'time_blocks': {'type': 'time_blocks', 'list': ['active', 'not_active']},
                        'power_rangers': {'type': 'power_rangers', 'list': ['active', 'not_active']},
                        # 'power_rangers_power': {'type': 'power_rangers_power'},
                        'kings_order_rules': {'type': 'PENDING'},
                        'stars_kings_order_rules': {'type': 'stars_kings_order_rules'},
                }

                star_level_2 = {
                    # 'stars': ["1Minute_1Day", "5Minute_5Day", "30Minute_1Month", "1Hour_3Month", "2Hour_6Month", "1Day_1Year"], 
                    'trade_using_limits': {'name': 'trade_using_limits', 'type':'bool', 'var': None},
                    'stagger_profits': {'name': 'stagger_profits', 'type':'number', 'var': None},
                    'total_budget': {'name': 'total_budget', 'type':'number', 'var': None},
                    'buyingpower_allocation_LongTerm': {'name': 'buyingpower_allocation_LongTerm', 'type':'number', 'var': None},
                    'buyingpower_allocation_ShortTerm': {'name': 'buyingpower_allocation_ShortTerm', 'type':'number', 'var': None},
                    'power_rangers': ["1Minute_1Day", "5Minute_5Day", "30Minute_1Month", "1Hour_3Month", "2Hour_6Month", "1Day_1Year"],
                    'trigbees': None,
            }

                star_trigbee_mapping = {
                    'status': 'checkbox',
                }
                    
                kor_option_mapping = {
                'theme': 'theme',
                'take_profit': 'number',
                'sellout': 'number',
                'status': 'checkbox',
                'trade_using_limits': 'checkbox',
                'doubledown_timeduration': 'number',
                'max_profit_waveDeviation': 'number',
                'max_profit_waveDeviation_timeduration': 'number',
                'timeduration': 'number',
                'sell_trigbee_trigger': 'checkbox',
                'stagger_profits': 'checkbox',
                'scalp_profits': 'checkbox',
                'scalp_profits_timeduration': 'number',
                'stagger_profits_tiers': 'number',
                'limitprice_decay_timeduration': 'number',
                'take_profit_in_vwap_deviation_range': 'take_profit_in_vwap_deviation_range',
                'skip_sell_trigbee_distance_frequency': 'skip_sell_trigbee_distance_frequency', # skip sell signal if frequency of last sell signal was X distance >> timeperiod over value, 1m: if sell was 1 story index ago
                'ignore_trigbee_at_power': 'ignore_trigbee_at_power',
                'ignore_trigbee_in_vwap_range': 'ignore_trigbee_in_vwap_range',
                'ignore_trigbee_in_macdstory_tier': 'ignore_trigbee_in_macdstory_tier',
                'ignore_trigbee_in_histstory_tier': 'ignore_trigbee_in_histstory_tier',
                }
                # take_profit_in_vwap_deviation_range={'low_range': -.05, 'high_range': .05}



                with st.form('trading model form'):
                    st.subheader("Settings")
                    #### TRADING MODEL ####
                    # Ticker Level 1
                    # Star Level 2
                    # Trigbees Level 3
                    
                    theme = st.selectbox(label=f'theme_reset', options=pollen_themes_selections, index=pollen_themes_selections.index(trading_model.get('theme')), key=f'theme_reset')
                    king_order_rules_update = trading_model__star['trigbees'][trigbee_sel][wave_blocks_option]

                    
                    with st.expander(f'{ticker_option_qc} Global Settings'):
                        cols = st.columns((1,1,1,1,1))
                        
                        # all ticker settings
                        for kor_option, kor_v in trading_model.items():
                            if kor_option in ticker_model_level_1.keys():
                                item_type = ticker_model_level_1[kor_option]['type']
                                if kor_option == 'theme':
                                    trading_model[kor_option] = st.selectbox(label=f'{ticker_option_qc}{"_"}{kor_option}', options=item_val, index=item_val.index(kor_v), key=f'{ticker_option_qc}{"_"}{kor_option}')

                                if item_type == None:
                                    continue # not allowed edit

                                elif kor_option == 'status':
                                    with cols[0]:
                                        item_val = ticker_model_level_1[kor_option]['list']
                                        trading_model[kor_option] = st.selectbox(label=f'{ticker_option_qc}{"_"}{kor_option}', options=item_val, index=item_val.index(kor_v), key=f'{ticker_option_qc}{"_"}{kor_option}')
                            
                                elif kor_option == 'total_budget':
                                    with cols[1]:
                                        trading_model[kor_option] = st.number_input(label=f'{ticker_option_qc}{"_"}{kor_option}', value=kor_v, key=f'{ticker_option_qc}{"_"}{kor_option}')

                                elif kor_option == 'max_single_trade_amount':
                                    with cols[1]:
                                        trading_model[kor_option] = st.number_input(label=f'{ticker_option_qc}{"_"}{kor_option}', value=kor_v, key=f'{ticker_option_qc}{"_"}{kor_option}')

                                elif kor_option == 'allow_for_margin':
                                    with cols[0]:
                                        trading_model[kor_option] = st.checkbox(label=f'{ticker_option_qc}{"_"}{kor_option}', value=kor_v, key=f'{ticker_option_qc}{"_"}{kor_option}')
                                
                                elif kor_option == 'buy_ONLY_by_accept_from_QueenBeeTrader':
                                    with cols[1]:
                                        trading_model[kor_option] = st.checkbox(label=f'{ticker_option_qc}{"_"}{kor_option}', value=kor_v, key=f'{ticker_option_qc}{"_"}{kor_option}')

                                elif kor_option == 'index_long_X':
                                    with cols[0]:
                                        item_val = ticker_model_level_1[kor_option]['list']
                                        trading_model[kor_option] = st.selectbox(label=f'{ticker_option_qc}{"_"}{kor_option}', options=item_val, index=item_val.index(kor_v), key=f'{ticker_option_qc}{"_"}{kor_option}')
                                elif kor_option == 'index_inverse_X':
                                    with cols[0]:
                                        item_val = ticker_model_level_1[kor_option]['list']
                                        trading_model[kor_option] = st.selectbox(label=f'{ticker_option_qc}{"_"}{kor_option}', options=item_val, index=item_val.index(kor_v), key=f'{ticker_option_qc}{"_"}{kor_option}')
                                
                                elif kor_option == 'portforlio_weight_ask':
                                    with cols[0]:
                                        trading_model[kor_option] = st.slider(label=f'{"portforlio_weight_ask"}', key='portforlio_weight_ask', min_value=float(0.0), max_value=float(1.0), value=float(kor_v), help="Allocation to Strategy by portfolio")

                                elif kor_option == 'trigbees':
                                    with cols[4]:
                                        st.write("Activate Trigbees")
                                        item_val = ticker_model_level_1[kor_option]['list']
                                        for trigbee, trigactive in trading_model['trigbees'].items():
                                            trading_model[kor_option][trigbee] = st.checkbox(label=f'{trigbee}', value=trigactive, key=f'{ticker_option_qc}{"_"}{kor_option}{trigbee}')

                                elif kor_option == 'time_blocks':
                                    with cols[2]:
                                        st.write("Trade Following Time Blocks")
                                        for wave_block, waveactive in trading_model['time_blocks'].items():
                                            trading_model[kor_option][wave_block] = st.checkbox(label=f'{wave_block}', value=waveactive, key=f'{ticker_option_qc}{"_"}{kor_option}{wave_block}')
                                
                                elif kor_option == 'power_rangers':
                                    with cols[3]:
                                        st.write('Trade Following Time Frames')
                                        for power_ranger, pr_active in trading_model['power_rangers'].items():
                                            trading_model[kor_option][power_ranger] = st.checkbox(label=f'{power_ranger}', value=pr_active, key=f'{ticker_option_qc}{"_"}{kor_option}{power_ranger}')
                                
                                elif kor_option == 'buyingpower_allocation_LongTerm':
                                    with cols[0]:
                                        long = st.slider(label=f'{"Long Term Allocation"}', key='tic_long', min_value=float(0.0), max_value=float(1.0), value=float(trading_model['buyingpower_allocation_LongTerm']), help="Set the Length of the trades, lower number means short trade times")
                                        short = st.slider(label=f'{"Short Term Allocation"}', key='tic_short', min_value=float(0.0), max_value=float(1.0), value=float(trading_model['buyingpower_allocation_ShortTerm']), help="Set the Length of the trades, lower number means short trade times")

                                        if long > short:
                                            long = long
                                        else:
                                            short = 1 - long
                                        
                                        trading_model['buyingpower_allocation_ShortTerm'] = short
                                        trading_model["buyingpower_allocation_LongTerm"] = long
                                else:
                                    st.write("not accounted ", kor_option)
                            else:
                                # trading_model[kor_option] = kor_v
                                st.write("missing ", kor_option)

                    with st.expander(f'{star_option_qc} Time Frame'):
                        # st.write([i for i in star_level_2.keys() if i ])
                        st.info("Set the Stars Gravity; allocation of power on the set of stars your Symbol's choice")
                        cols = st.columns(3)
                        
                        for item_control, itc_vars in star_level_2.items():
                            if item_control not in QUEEN_KING['king_controls_queen'][control_option][ticker_option_qc]['stars_kings_order_rules'][star_option_qc].keys():
                                st.write(f'{item_control} not in scope')
                                continue
                        

                        with cols[0]: # total_budget
                            trading_model['stars_kings_order_rules'][star_option_qc]['total_budget'] = st.number_input(label='$Budget', value=float(trading_model['stars_kings_order_rules'][star_option_qc]['total_budget']))

                        with cols[0]: # Allocation
                            long = st.slider(label=f'{"Long Term Allocation"}', key='trigbee_long', min_value=float(0.0), max_value=float(1.0), value=float(trading_model__star['buyingpower_allocation_LongTerm']), help="Set the Length of the trades, lower number means shorter trade times")
                            short = st.slider(label=f'{"Short Term Allocation"}', key='trigbee_short', min_value=float(0.0), max_value=float(1.0), value=float(trading_model__star['buyingpower_allocation_ShortTerm']), help="Set the Length of the trades, lower number means shorter trade times")

                            if long > short:
                                long = long
                            else:
                                short = 1 - long
                            
                            trading_model['stars_kings_order_rules'][star_option_qc]['buyingpower_allocation_ShortTerm'] = short
                            trading_model['stars_kings_order_rules'][star_option_qc]["buyingpower_allocation_LongTerm"] = long
                        
                        with cols[1]: # index_long_X
                            trading_model['stars_kings_order_rules'][star_option_qc]['index_long_X'] = st.selectbox("Long X Weight", options=['1X', '2X', '3X'], index=['1X', '2X', '3X'].index(f'{trading_model["stars_kings_order_rules"][star_option_qc]["index_long_X"]}'))

                        with cols[1]: # index_inverse_X
                            trading_model['stars_kings_order_rules'][star_option_qc]['index_inverse_X'] = st.selectbox("Short X Weight", options=['1X', '2X', '3X'], index=['1X', '2X', '3X'].index(f'{trading_model["stars_kings_order_rules"][star_option_qc]["index_inverse_X"]}'))                    
                        
                        with cols[2]: # trade_using_limits
                            trading_model['stars_kings_order_rules'][star_option_qc]['trade_using_limits'] = st.checkbox("trade_using_limits", value=trading_model['stars_kings_order_rules'][star_option_qc]['trade_using_limits'])
                        
                        page_line_seperator(height='1')
                        cols = st.columns((1,3,1))
                        with cols[1]:
                            st.write('Star Allocation Power')
                        
                        # with cols[2]:
                        #     st.write('Gravity')
                        
                        for power_ranger, pr_active in trading_model['stars_kings_order_rules'][star_option_qc]['power_rangers'].items():
                            # st.write(power_ranger, pr_active)
                            with cols[1]:
                                trading_model['stars_kings_order_rules'][star_option_qc]['power_rangers'][power_ranger] = st.slider(label=f'{power_ranger}', min_value=float(0.0), max_value=float(1.0), value=float(pr_active), key=f'{star_option_qc}{power_ranger}')
                            
                    with st.expander(f'{wave_blocks_option} Time Block KOR'):
                        # mark_down_text(text=f'{trigbee_sel}{" >>> "}{wave_blocks_option}')
                        # st.write(f'{wave_blocks_option} >>> WaveBlocktime KingOrderRules 4')
                        cols = st.columns((1, 1, 2, 3))

                        for kor_option, kor_v in king_order_rules_update.items():
                            if kor_option in kor_option_mapping.keys():
                                st_func = kor_option_mapping[kor_option]
                                with cols[0]:
                                    if kor_option == 'status':
                                        st.write(kor_v)
                                    if kor_option == 'theme':
                                        st.write(kor_v)
                                    if kor_option == 'take_profit_in_vwap_deviation_range':
                                        # with cols[0]:
                                        #     st.write("vwap_deviation_range")
                                            low = st.number_input(label=f'{"vwap_deviation_low"}', value=kor_v['low_range'], key=f'{trigbee_sel}{"_"}{wave_blocks_option}{"_"}{"low_range"}', help="take_profit_in_vwap_deviation_range")
                                            high = st.number_input(label=f'{"vwap_deviation_high"}', value=kor_v['high_range'], key=f'{trigbee_sel}{"_"}{wave_blocks_option}{"_"}{"high_range"}')
                                            king_order_rules_update[kor_option] = {'high_range': high, "low_range": low}

                                
                                with cols[1]:
                                    if kor_option == 'ignore_trigbee_in_vwap_range':
                                        low = st.number_input(label=f'{"ignore_vwap_low"}', value=kor_v['low_range'], key=f'{trigbee_sel}{"_"}{wave_blocks_option}{"_"}{"vwap_low_range"}')
                                        high = st.number_input(label=f'{"ignore_vwap_high"}', value=kor_v['high_range'], key=f'{trigbee_sel}{"_"}{wave_blocks_option}{"_"}{"vwap_high_range"}')
                                        king_order_rules_update[kor_option] = {'high_range': high, "low_range": low}
                                        # with cols[0]:
                                        #     st.write("ignore_trigbee_in_vwap_range")

                                if kor_option == 'skip_sell_trigbee_distance_frequency':
                                    with cols[3]:
                                        king_order_rules_update[kor_option] = st.slider(label=f'{kor_option}', key=f'{trigbee_sel}{"_"}{wave_blocks_option}{"_"}{kor_option}', min_value=float(0.0), max_value=float(3.0), value=float(kor_v), help="Skip a sellcross trigger frequency")
                                
                                if kor_option == 'ignore_trigbee_at_power':
                                    with cols[3]:
                                        king_order_rules_update[kor_option] = st.slider(label=f'{kor_option}', key=f'{trigbee_sel}{"_"}{wave_blocks_option}{"_"}{kor_option}', min_value=float(0.0), max_value=float(3.0), value=float(kor_v), help="Trade Needs to be Powerful Enough as defined by the model allocation story")

                                if st_func == 'checckbox':
                                    king_order_rules_update[kor_option] = st.checkbox(label=f'{kor_option}', value=kor_v, key=f'{trigbee_sel}{"_"}{wave_blocks_option}{"_"}{kor_option}')
                                elif st_func == 'number':
                                    king_order_rules_update[kor_option] = st.number_input(label=f'{kor_option}', value=kor_v, key=f'{trigbee_sel}{"_"}{wave_blocks_option}{"_"}{kor_option}')
                                elif st_func == 'text':
                                    king_order_rules_update[kor_option] = st.text_input(label=f'{kor_option}', value=kor_v, key=f'{trigbee_sel}{"_"}{wave_blocks_option}{"_"}{kor_option}')
                            
                            else:
                                # print('missing')
                                st.write("missing ", kor_option)
                                king_order_rules_update[kor_option] = kor_v

                    # WaveBlock Time Levle 4 ## using all selections to change KingsOrderRules
                    trading_model['stars_kings_order_rules'][star_option_qc]['trigbees'][trigbee_sel][wave_blocks_option] = king_order_rules_update

                    cols = st.columns((1,1,1,1,3))
                    with cols[0]:
                        save_button_addranger = st.form_submit_button("Save Trading Model Settings")
                    with cols[1]:
                        savecopy_button_addranger = st.form_submit_button("Save Copy of Trading Model Settings")
                    with cols[2]:
                        replace_model_with_saved_selection = st.form_submit_button("replace model with saved selection")
                    with cols[3]:
                        refresh_to_theme = st.form_submit_button("Refresh Model To Selected Theme")           

                    if save_button_addranger:
                        app_req = create_AppRequest_package(request_name='trading_models_requests')
                        app_req['trading_model'] = trading_model
                        QUEEN_KING['trading_models_requests'].append(app_req)
                        QUEEN_KING['king_controls_queen'][control_option][ticker_option_qc] = trading_model
                        
                        PickleData(pickle_file=PB_App_Pickle, data_to_store=QUEEN_KING)
                        return_image_upon_save(title="Model Saved")
                    
                    elif savecopy_button_addranger:                        
                        QUEEN_KING['saved_trading_models'].update(trading_model)
                        PickleData(pickle_file=PB_App_Pickle, data_to_store=QUEEN_KING)
                        return_image_upon_save(title="Model Cpoy Saved")

                    elif replace_model_with_saved_selection:                        
                        app_req = create_AppRequest_package(request_name='trading_models_requests')
                        app_req['trading_model'] = trading_model
                        QUEEN_KING['trading_models_requests'].append(app_req)
                        QUEEN_KING['king_controls_queen'][control_option][ticker_option_qc] = trading_model
                        
                        PickleData(pickle_file=PB_App_Pickle, data_to_store=QUEEN_KING)
                        return_image_upon_save(title="Model Replaced With Saved Version")
                    elif refresh_to_theme:
                        QUEEN_KING = refresh_tickers_TradingModels(QUEEN_KING=QUEEN_KING, ticker=ticker_option_qc, theme=theme)
                        PickleData(pickle_file=PB_App_Pickle, data_to_store=QUEEN_KING)
                        return_image_upon_save(title=f'Model Reset to Original Theme Settings')



                if st.button('show queens trading model'):
                    st.write(QUEEN_KING['king_controls_queen'][control_option][ticker_option_qc])
            except Exception as e:
                print(e)
                print_line_of_error()




        ########################################################
        ########################################################
        #############The Infinite Loop of Time #################
        ########################################################
        ########################################################
        ########################################################

    try:
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
        # PB_KING_Pickle = st.session_state['PB_KING_Pickle']


        # QUEEN_KING = ReadPickleData(pickle_file=PB_App_Pickle)    
        # KING = ReadPickleData(pickle_file=PB_KING_Pickle)
        # QUEEN Databases
        # QUEEN = ReadPickleData(st.session_state['PB_QUEEN_Pickle'])
        
        @st.cache_data()
        def return_QUEEN():
            st.info("Cache QUEEN")
            return ReadPickleData(st.session_state['PB_QUEEN_Pickle'])

        if 'edit_orders' in st.session_state and st.session_state['edit_orders'] == True:
            QUEEN = return_QUEEN()
            order_buttons = True
        else:
            st.cache_data.clear()
            order_buttons = False
            QUEEN = ReadPickleData(st.session_state['PB_QUEEN_Pickle'])
    
        QUEENsHeart = ReadPickleData(PB_QUEENsHeart_PICKLE)

        pollen_themes_selections = list(pollen_themes(KING).keys())        
        prod_keys_confirmed = QUEEN_KING['users_secrets']['prod_keys_confirmed']
        sandbox_keys_confirmed = QUEEN_KING['users_secrets']['sandbox_keys_confirmed']

        api = return_alpaca_user_apiKeys(QUEEN_KING=QUEEN_KING, authorized_user=authorized_user, prod=st.session_state['production'])
        
        # try:
        #     api_failed = False
        #     snapshot = api.get_snapshot("SPY") # return_last_quote from snapshot
        # except Exception as e:
        #     # requests.exceptions.HTTPError: 403 Client Error: Forbidden for url: https://data.alpaca.markets/v2/stocks/SPY/snapshot
        #     st.write("API Keys failed! You need to update, Please Go to your Alpaca Broker Account to Generate API Keys")
        #     # time.sleep(5)
        #     queen__account_keys(PB_App_Pickle=PB_App_Pickle, QUEEN_KING=QUEEN_KING, authorized_user=authorized_user, show_form=True) #EDRXZ Maever65teo
        #     api_failed = True

        if st.session_state['authorized_user']: ## MOVE THIS INTO pollenq?
            clean_out_app_requests(QUEEN=QUEEN, QUEEN_KING=QUEEN_KING, request_buckets=['subconscious', 'sell_orders', 'queen_sleep', 'update_queen_order'])
        
            # # use API keys from user
            # queenbee_online(QUEENsHeart=QUEENsHeart, admin=admin, dag='run_queenbee', api_failed=api_failed)
            # queenbee_online(QUEENsHeart=QUEENsHeart, admin=admin, dag='run_workerbees', api_failed=api_failed)
            # queenbee_online(QUEENsHeart=QUEENsHeart, admin=admin, dag='run_workerbees_crypto', api_failed=api_failed)

        portfolio = return_alpc_portolio(api)['portfolio']
        acct_info = refresh_account_info(api=api)
        ac_info = refresh_account_info(api=api)['info_converted']

        # # if authorized_user: log type auth and none
        log_dir = os.path.join(db_root, 'logs')
        init_logging(queens_chess_piece=queens_chess_piece, db_root=db_root, prod=st.session_state['production'])

        # db global
        # Ticker DataBase
        coin_exchange = "CBSE"
        ticker_db = return_QUEENs__symbols_data(QUEEN=QUEEN, QUEEN_KING=QUEEN_KING)
        POLLENSTORY = ticker_db['pollenstory']
        STORY_bee = ticker_db['STORY_bee']
        tickers_avail = [list(set(i.split("_")[0] for i in STORY_bee.keys()))][0]
        st.write(ticker_db.get('errors'))


        with st.spinner("Waking Up the Hive"):

            # if cust_Button(MISC.get('pawn_png_url'), height='34px', key='chess'):
            if st.session_state['chess_board'] == True:
                if 'admin_workerbees' in st.session_state and st.session_state['admin_workerbees'] == "admin_workerbees":
                    chess_board__workerbees(QUEEN_KING=QUEEN_KING, admin=admin)
                else:
                    # chess_board__workerbees(QUEEN_KING=QUEEN_KING, admin=False)
                    chessboard(QUEEN_KING=QUEEN_KING, admin=False)
            
            if st.session_state['queens_mind']:
                update_trading_models(QUEEN_KING=QUEEN_KING, pollen_themes_selections=pollen_themes_selections)

            portfolio_header__QC(ac_info=ac_info)
            cols = st.columns(2)

            queen_tabs = ["Orders", "Heart", "Portfolio"]
            order_tab, heart_tab, Portfolio = st.tabs(queen_tabs)

            if authorized_user:
                return_total_profits(QUEEN=QUEEN)
                stop_queenbee(QUEEN_KING=QUEEN_KING)
                # refresh_queenbee_controls(QUEEN_KING=QUEEN_KING)
                clear_subconscious_Thought(QUEEN=QUEEN, QUEEN_KING=QUEEN_KING)
            
            with order_tab:
                ordertables__agrid = queen_order_flow(QUEEN=QUEEN, active_order_state_list=active_order_state_list, order_buttons=order_buttons)
                # ipdb.set_trace()
                if authorized_user:
                    if ordertables__agrid.selected_rows:
                        # st.write(queen_order[0]['client_order_id'])
                        queen_order = ordertables__agrid.selected_rows[0]
                        client_order_id = queen_order.get('client_order_id')

                        try: # OrderState
                            df = ordertables__agrid["data"][ordertables__agrid["data"].orderstate == "clicked"]
                            if len(df) > 0:
                                current_requests = [i for i in QUEEN_KING['update_queen_order'] if client_order_id in i.keys()]
                                if len(current_requests) > 0:
                                    st.write("You Already Requested Queen To Change Order State, Refresh Orders to View latest Status")
                                else:
                                    order_update_package = create_AppRequest_package(request_name='update_queen_order', client_order_id=client_order_id)
                                    order_update_package['queen_order_updates'] = {client_order_id: {'queen_order_state': queen_order.get('queen_order_state')}}
                                    QUEEN_KING['update_queen_order'].append(order_update_package)
                                    PickleData(PB_App_Pickle, QUEEN_KING)
                                    st.success(f'{client_order_id} Changing QueenOrderState Please wait for Queen to process, Refresh Table')
                        except:
                            st.write("OrderState nothing was clicked")
                        
                        # validate to continue with selection
                        try: ## SELL
                            df = ordertables__agrid["data"][ordertables__agrid["data"].sell == "clicked"]
                            if len(df) > 0:
                                current_requests = [i for i in QUEEN_KING['sell_orders'] if client_order_id in i.keys()]
                                if len(current_requests) > 0:
                                    st.write("You Already Requested Queen To Sell order, Refresh Orders to View latest Status")
                                else:
                                    sell_package = create_AppRequest_package(request_name='sell_orders', client_order_id=client_order_id)
                                    sell_package['sell_qty'] = float(queen_order.get('qty_available'))
                                    sell_package['side'] = 'sell'
                                    sell_package['type'] = 'market'
                                    QUEEN_KING['sell_orders'].append(sell_package)
                                    PickleData(PB_App_Pickle, QUEEN_KING)
                                    st.success(f'{client_order_id} : Selling Order Sent to Queen Please wait for Queen to process, Refresh Table')
                            else:
                                st.write("Nothing Sell clicked")

                        except:
                            er_line = print_line_of_error()
                            st.write("Error in Sell ", er_line)
                        try: ## KOR
                            df = ordertables__agrid["data"][ordertables__agrid["data"].orderrules == "clicked"]
                            if len(df) > 0:
                                st.write("KOR: ", client_order_id)
                                # kings_order_rules__forum(order_rules)
                            else:
                                st.write("Nothing KOR clicked")
                        except:
                            st.write("KOR PENDING WORK")

                    download_df_as_CSV(df=ordertables__agrid["data"], file_name="orders.csv")
                    queen_beeAction_theflash(False)
                
                queen_triggerbees()
            
            with heart_tab:
                cols = st.columns(3)
                with cols[0]:
                    if st.button("clear all sell orders"):
                        QUEEN_KING['sell_orders'] = []
                        PickleData(PB_App_Pickle, QUEEN_KING)
                    st.write("sell_orders")
                    st.write(QUEEN_KING['sell_orders'])
                    
                    st.write("Heart")
                    st.write(QUEEN['heartbeat'])
                
                with cols[1]:
                    st.write("queen_sleep")
                    st.write(QUEEN_KING['queen_sleep'])
                    st.write("queen_messages")
                    st.write(QUEEN['queens_messages'])
                with cols[2]:
                    st.write("update_queen_order")
                    st.write(QUEEN_KING['update_queen_order'])

            with Portfolio:
                return_buying_power(acct_info=acct_info)  # sidebar


            page_line_seperator(color=default_yellow_color)

            
        page_session_state__cleanUp(page=page)

        if authorized_user:            
            st.session_state['last_page'] = 'queen'
            PickleData(PB_App_Pickle, QUEEN_KING)
            print(return_timestamp_string())
        ##### END ####
    except Exception as e:
        print(e, print_line_of_error(), return_timestamp_string())

if __name__ == '__main__':
    queens_conscience(False, False)