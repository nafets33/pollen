
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

        if st.session_state['authorized_user']:
            APP_req = add_key_to_app(QUEEN_KING)
            QUEEN_KING = APP_req['QUEEN_KING']
            if APP_req['update']:
                PickleData(PB_App_Pickle, QUEEN_KING)


        # if st.session_state['authorized_user'] == False and sneak_peak == False:
        #     cols = st.columns(2)
        #     with cols[0]:
        #         st.info("You Don't have a QueenTraderBot yet! Need authorization, Please contact pollenq.queen@gmail.com or click the button below to send a Request")
        #     with cols[1]:
        #         st.info("Below is a Preview")
        #     client_user_wants_a_queen = st.button("Yes I want a Queen!")
        #     if client_user_wants_a_queen:
        #         st.session_state['init_queen_request'] = True
        #         if 'init_queen_request' in st.session_state:
        #             QUEEN_KING['init_queen_request'] = {'timestamp_est': datetime.datetime.now(est)}
        #             PickleData(PB_App_Pickle, QUEEN_KING)
        #             send_email(recipient=os.environ.get('pollenq_gmail'), subject="RequestingQueen", body=f'{st.session_state["username"]} Asking for a Queen')
        #             st.success("Hive Master Notified and You should receive contact soon")



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

        portfolio = return_alpc_portolio(api)['portfolio']
        acct_info = refresh_account_info(api=api)
        ac_info = refresh_account_info(api=api)['info_converted']

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

        
        with st.spinner("Waking Up the Hive"):

            tickers_avail_op = list(tickers_avail)

            portfolio_header__QC(ac_info=ac_info)
            cols = st.columns(2)

            queen_tabs = ["Orders", "Heart", "Portfolio"]
            order_tab, heart_tab, Portfolio = st.tabs(queen_tabs)

            if authorized_user:
                return_total_profits(QUEEN=QUEEN)
                stop_queenbee(QUEEN_KING=QUEEN_KING)
                refresh_queenbee_controls(QUEEN_KING=QUEEN_KING)
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

        ##### END ####
    except Exception as e:
        print(e, print_line_of_error(), return_timestamp_string())

