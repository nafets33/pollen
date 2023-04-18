
import pandas as pd
import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import pytz
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from itertools import islice
from PIL import Image
from dotenv import load_dotenv

# import streamlit as st
# from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode, JsCode
# from streamlit_extras.stoggle import stoggle
# from streamlit_extras.switch_page_button import switch_page
import time
import os
import sqlite3
import time
import aiohttp
import asyncio
# import requests
# from requests.auth import HTTPBasicAuth
from chess_piece.app_hive import admin_queens_active, send_email, pollenq_button_source, standard_AGgrid, create_AppRequest_package, create_wave_chart_all, create_slope_chart, create_wave_chart_single, create_wave_chart, create_guage_chart, create_main_macd_chart, page_session_state__cleanUp, queen_order_flow, mark_down_text, mark_down_text, page_line_seperator, local_gif, flying_bee_gif, pollen__story
from chess_piece.king import workerbee_dbs_backtesting_root, workerbee_dbs_backtesting_root__STORY_bee, return_all_client_users__db, kingdom__global_vars, return_QUEENs__symbols_data, hive_master_root, streamlit_config_colors, local__filepaths_misc, print_line_of_error, ReadPickleData, PickleData
from chess_piece.queen_hive import init_ticker_stats__from_yahoo, refresh_chess_board__revrec, return_ttf_remaining_budget, return_queen_orders__query, add_trading_model, set_chess_pieces_symbols, init_pollen_dbs, init_qcp, return_alpaca_user_apiKeys, wave_guage, return_STORYbee_trigbees, refresh_account_info, generate_TradingModel, stars, analyze_waves, story_view, return_alpc_portolio, pollen_themes,  return_timestamp_string, init_logging

from custom_button import cust_Button
from custom_grid import st_custom_grid

from ozz.ozz_bee import send_ozz_call
# from chat_bot import ozz_bot


# from tqdm import tqdm

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


page = 'QueensConscience'

# if st.button("sw"):
#     switch_page("QueensConscience#no-ones-flying")

## anchors
# st.header("Section 1")
# st.markdown("[Section 1](#section-1)")

def queens_conscience(st, hc, KING, QUEEN, QUEEN_KING, tabs):

    # from random import randint
    main_root = hive_master_root() # os.getcwd()  # hive root
    load_dotenv(os.path.join(main_root, ".env"))
    est = pytz.timezone("US/Eastern")
    utc = pytz.timezone('UTC')
    # ###### GLOBAL # ######
    king_G = kingdom__global_vars()
    active_order_state_list = king_G.get('active_order_state_list') # = ['running', 'running_close', 'submitted', 'error', 'pending', 'completed', 'completed_alpaca', 'running_open', 'archived_bee']
    active_queen_order_states = king_G.get('active_queen_order_states') # = ['submitted', 'accetped', 'pending', 'running', 'running_close', 'running_open']
    # CLOSED_queenorders = king_G.get('CLOSED_queenorders') # = ['running_close', 'completed', 'completed_alpaca']
    RUNNING_Orders = king_G.get('RUNNING_Orders') # = ['running', 'running_open']
    # RUNNING_CLOSE_Orders = king_G.get('RUNNING_CLOSE_Orders') # = ['running_close']
    
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

        # print("QC Start")
        def advanced_charts():
            try:
                tickers_avail = [list(set(i.split("_")[0] for i in STORY_bee.keys()))][0]
                cols = st.columns((1,5,1,1))
                # fullstory_option = st.selectbox('POLLENSTORY', ['no', 'yes'], index=['yes'].index('yes'))
                stars_radio_dict = {'1Min':"1Minute_1Day", '5Min':"5Minute_5Day", '30m':"30Minute_1Month", '1hr':"1Hour_3Month", 
                '2hr':"2Hour_6Month", '1Yr':"1Day_1Year", 'all':"all",}
                with cols[0]:
                    ticker_option = st.selectbox("Tickers", tickers_avail, index=tickers_avail.index(["SPY" if "SPY" in tickers_avail else tickers_avail[0]][0]))
                    ticker = ticker_option
                with cols[1]:
                    option__ = st.radio(
                        label="stars_radio",
                        options=list(stars_radio_dict.keys()),
                        key="signal_radio",
                        label_visibility='visible',
                        # disabled=st.session_state.disabled,
                        horizontal=True,
                    )
                
                with cols[2]:
                    # day_only_option = st.selectbox('Show Today Only', ['no', 'yes'], index=['no'].index('no'))
                    hc.option_bar(option_definition=pq_buttons.get('charts_day_option_data'),title='Show Today Only', key='day_only_option', horizontal_orientation=True) #,override_theme=over_theme,font_styling=font_fmt,horizontal_orientation=True)

                
                if option__ != 'all':
                    ticker_time_frame = f'{ticker}_{stars_radio_dict[option__]}'
                else:
                    ticker_time_frame = f'{ticker}_{"1Minute_1Day"}'

                df = POLLENSTORY[ticker_time_frame].copy()

                charts__view, waves__view, slopes__view = st.tabs(['charts', 'waves', 'slopes'])
                
                with charts__view:
                    try:
    
                        st.markdown('<div style="text-align: center;">{}</div>'.format(ticker_option), unsafe_allow_html=True)

                        if option__.lower() == 'all':
                            min_1 = POLLENSTORY[f'{ticker_option}{"_"}{"1Minute_1Day"}'].copy()
                            min_5 = POLLENSTORY[f'{ticker_option}{"_"}{"5Minute_5Day"}'].copy()
                            min_30m = POLLENSTORY[f'{ticker_option}{"_"}{"30Minute_1Month"}'].copy()
                            _1hr = POLLENSTORY[f'{ticker_option}{"_"}{"1Hour_3Month"}'].copy()
                            _2hr = POLLENSTORY[f'{ticker_option}{"_"}{"2Hour_6Month"}'].copy()
                            _1yr = POLLENSTORY[f'{ticker_option}{"_"}{"1Day_1Year"}'].copy()

                            c1, c2 = st.columns(2)
                            with c1:
                                st.plotly_chart(create_main_macd_chart(min_1))
                            with c2:
                                st.plotly_chart(create_main_macd_chart(min_5))
                            c1, c2 = st.columns(2)
                            with c1:
                                st.plotly_chart(create_main_macd_chart(min_30m))
                            with c2:
                                st.plotly_chart(create_main_macd_chart(_1hr))
                            c1, c2 = st.columns(2)
                            with c1:
                                st.plotly_chart(create_main_macd_chart(_2hr))
                            with c2:
                                st.plotly_chart(create_main_macd_chart(_1yr))
                        else:
                            # if day_only_option == 'yes':
                            if st.session_state['day_only_option'] == 'charts_dayonly_yes':
                                df_day = df['timestamp_est'].iloc[-1]
                                df['date'] = df['timestamp_est'] # test

                                df_today = df[df['timestamp_est'] > (datetime.now().replace(hour=1, minute=1, second=1)).astimezone(est)].copy()
                                df_prior = df[~(df['timestamp_est'].isin(df_today['timestamp_est'].to_list()))].copy()

                                df = df_today
                            
                            st.plotly_chart(create_main_macd_chart(df=df, width=1500, height=550))
                    
                    except Exception as e:
                        print(e)
                        print_line_of_error()

                # if slope_option == 'yes':
                with slopes__view:
                    # df = POLLENSTORY[ticker_time_frame].copy()
                    slope_cols = [i for i in df.columns if "slope" in i]
                    slope_cols.append("close")
                    slope_cols.append("timestamp_est")
                    slopes_df = df[['timestamp_est', 'hist_slope-3', 'hist_slope-6', 'macd_slope-3']]
                    fig = create_slope_chart(df=df)
                    st.plotly_chart(fig)
                    st.dataframe(slopes_df)
                    
                # if wave_option == "yes":
                with waves__view:
                    # df = POLLENSTORY[ticker_time_frame].copy()
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


        def chunk(it, size):
            it = iter(it)
            return iter(lambda: tuple(islice(it, size)), ())

        
        def queen_triggerbees():
            # cols = st.columns((1,5))
            now_time = datetime.now(est)
            req = return_STORYbee_trigbees(QUEEN=QUEEN, STORY_bee=STORY_bee, tickers_filter=False)
            active_trigs = req['active_trigs']
            all_current_trigs = req['all_current_trigs']
            if len(all_current_trigs) > 0:
                df = pd.DataFrame(all_current_trigs.items())
                df = df.rename(columns={0: 'ttf', 1: 'trig'})
                df_all_active = df.sort_values('ttf')
            else:
                with st.expander("No Bees Flying"):
                    st.subheader("No one's flying")
                    mark_down_text(align='left', fontsize=15, text="All Available TriggerBees")
                    local_gif(gif_path=flyingbee_grey_gif_path) 
            
            if len(active_trigs) > 0:
                st.subheader("Bees Triggers Active")
                with st.expander("Bees Flying", True):
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
                    mark_down_text(align='left', fontsize=15, text="All Available TriggerBees")
                    st.write(df_all_active)
    

            return True


        def queen_beeAction_theflash():
    
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
                    'request_time': datetime.now(est),
                    'wave_amo': quick_buy_amt,
                    'app_seen_price': current_price,
                    'side': 'buy',
                    'type': type_option,
                    'app_requests_id' : f'{"flashbuy"}{"_app-request_id_"}{return_timestamp_string()}{datetime.now().microsecond}'
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
                'request_time': datetime.now(),
                'app_requests_id' : f'{"theflash"}{"_"}{"waveup"}{"_app-request_id_"}{return_timestamp_string()}{datetime.now().microsecond}'
                }

                QUEEN_KING['wave_triggers'].append(order_dict)
                PickleData(pickle_file=PB_App_Pickle, data_to_store=QUEEN_KING)
                with cols[3]:
                    return_image_upon_save(title="Wave Request Delivered to the Queen")
            
            return True



        def return_total_profits(QUEEN):
            try:
                df = QUEEN['queen_orders']
                QUEEN = df[(df['queen_order_state']== 'completed') & (df['side'] == 'sell')].copy()
                return_dict = {}
                if len(QUEEN) > 0:
                    now_ = datetime.now(est)
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


        def trigger_queen_vars(dag, client_username, last_trig_date=datetime.now(est)):
            return {'dag': dag, 'last_trig_date': last_trig_date, 'client_user': client_username}
        
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
                                        st.info(f'{ticker} {v}')
                                        # local_gif(gif_path=uparrow_gif, height='23', width='23')
                                    else:
                                        st.error(f'{ticker} {v}')
                                    # flying_bee_gif(width='43', height='40')
                                if write_type == 'pl_profits':
                                    st.write(ticker, v)
            except Exception as e:
                print(e, print_line_of_error())

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
                ticker_allowed = ['QQQ']
                # tickers_to_add = st.multiselect(label=f'Add Symbols', options=ticker_allowed, help=f'Try not to Max out number of piecesm, only ~10 allowed')
                cols = st.columns((1,2,10,3,2,2))
                with cols[1]:                
                    qcp = st.selectbox(label='qcp', key=f'qcp_new', options=avail_qcp)
                    QUEEN_KING[qcp_bees_key][qcp] = init_qcp(init_macd_vars={'fast': 12, 'slow': 26, 'smooth': 9}, ticker_list=[])
                with cols[0]:
                    st.image(MISC.get('queen_crown_url'), width=64)
                with cols[2]:
                    QUEEN_KING[qcp_bees_key][qcp]['tickers'] = st.multiselect(label=f'{qcp} symbols', options=ticker_allowed, default=None, help='Try not to Max out number of piecesm, only ~10 allowed')
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

        def add_new_qcp__to_chessboard(cols, QUEEN_KING, qcp_bees_key, ticker_allowed, themes):
            with st.form('new qcp'):
                cols = st.columns((1,5,2,2,2,2,2,3,2,2))
                qcp_pieces = QUEEN_KING[qcp_bees_key].keys()
                qcp = st.text_input(label='piece name', value=f'pawn_{len(qcp_pieces)}', help="Theme your names to match your strategy")
                if qcp in qcp_pieces:
                    st.error("Chess Piece Name must be Unique")
                qcp = setup_qcp_on_board(cols, QUEEN_KING, qcp_bees_key, qcp=None, new_piece=qcp, ticker_allowed=ticker_allowed, themes=themes, headers=0)
                if st.form_submit_button('Add New Piece'):
                    QUEEN_KING[qcp_bees_key][qcp.get('piece_name')] = qcp
                    PickleData(st.session_state['PB_App_Pickle'], QUEEN_KING)
                    st.success("New Piece Added Refresh")
                    
        def setup_qcp_on_board(cols, QUEEN_KING, qcp_bees_key, qcp, ticker_allowed, themes, new_piece=False, headers=0):
            def return_active_image(qcp):
                try:
                    with cols[0]:
                        if qcp == 'castle':
                            hc.option_bar(option_definition=pq_buttons.get('castle_option_data'),title='', key='castle_qcp', horizontal_orientation=False)
                        elif qcp == 'bishop':
                            hc.option_bar(option_definition=pq_buttons.get('bishop_option_data'),title='', key='bishop_qcp', horizontal_orientation=False)                                
                        elif qcp == 'knight':
                            hc.option_bar(option_definition=pq_buttons.get('knight_option_data'),title='', key='knight_qcp', horizontal_orientation=False)                                
                        elif qcp == 'castle_coin':
                            st.image("https://s3.us-east-2.amazonaws.com/nomics-api/static/images/currencies/BSV.png", width=54)
                        else:
                            st.image(MISC.get('knight_png'), width=74)
                    return True
                except Exception as e:
                    print(e)
                    print_line_of_error()
            
            # qcp_ex = init_qcp()
            # new_keys = [k for k in qcp_ex.keys() if k not in QUEEN_KING[qcp_bees_key][qcp].keys()]
            # if len(new_keys) > 0:
            #     print("qcp missing keys, adding them")
            #     for missing_key in new_keys:
            #         QUEEN_KING[qcp_bees_key][qcp][missing_key] = qcp_ex.get(missing_key)
            
            try:
                if headers == 0:
                    # Headers
                    c=0
                    chess_board_names = list(QUEEN_KING[qcp_bees_key]['castle'].keys())
                    chess_board_names = ["pq", 'symbols', 'Model', 'theme', 'BuyingP.Alloc', 'BorrowP.Alloc', 'Total Budget', 'Cash']
                    for qcpvar in chess_board_names:
                        try:
                            with cols[c]:
                                st.write(qcpvar)
                                c+=1
                        except Exception as e:
                            print(qcpvar, e)

                if new_piece:
                    return_active_image(new_piece)
                else:
                    return_active_image(qcp)

                if new_piece:
                    qcp = new_piece
                    if qcp not in QUEEN_KING[qcp_bees_key].keys():
                        qcp_vars = init_qcp(buying_power=0, piece_name=qcp)
                        # QUEEN_KING[qcp_bees_key][qcp] = qcp_vars
                        models = ['MACD']
                        # chess board vars
                        with cols[1]:
                            qcp_vars['tickers'] = st.multiselect(label="", options=ticker_allowed + crypto_symbols__tickers_avail, default=qcp_vars['tickers'], help='Castle Should Hold your Highest Valued Symbols', key=f'{qcp}tickers{admin}')
                        with cols[2]:
                            st.selectbox(label='', options=models, index=models.index(qcp_vars.get('model')), key=f'{qcp}model{admin}')
                        with cols[3]:
                            qcp_vars['theme'] = st.selectbox(label=f'', options=themes, index=themes.index(qcp_vars.get('theme')), help='Trading Star Strategy, You May Customize Trading Models', key=f'{qcp}theme{admin}')
                        with cols[4]:
                            qcp_vars['total_buyng_power_allocation'] = st.number_input(label=f'', min_value=float(0.0), max_value=float(1.0), value=float(qcp_vars['total_buyng_power_allocation']), key=f'{qcp}_buying_power_allocation{admin}', label_visibility='hidden')
                        with cols[5]:
                            qcp_vars['total_borrow_power_allocation'] = st.number_input(label=f'', min_value=float(0.0), max_value=float(1.0), value=float(qcp_vars['total_borrow_power_allocation']), key=f'{qcp}_borrow_power_allocation{admin}', label_visibility='hidden')
                            # QUEEN_KING[qcp_bees_key][qcp]['total_borrow_power_allocation'] = 
                    return qcp_vars
                
                else:   
                    models = ['MACD']
                    # chess board vars
                    with cols[1]:
                        QUEEN_KING[qcp_bees_key][qcp]['tickers'] = st.multiselect(label="", options=ticker_allowed + crypto_symbols__tickers_avail, default=QUEEN_KING[qcp_bees_key][qcp]['tickers'], help='Castle Should Hold your Highest Valued Symbols', key=f'{qcp}tickers{admin}')
                    with cols[2]:
                        st.selectbox(label='', options=models, index=models.index(QUEEN_KING[qcp_bees_key][qcp].get('model')), key=f'{qcp}model{admin}')
                    with cols[3]:
                        QUEEN_KING[qcp_bees_key][qcp]['theme'] = st.selectbox(label=f'', options=themes, index=themes.index(QUEEN_KING[qcp_bees_key][qcp].get('theme')), help='Trading Star Strategy, You May Customize Trading Models', key=f'{qcp}theme{admin}')
                    with cols[4]:
                        QUEEN_KING[qcp_bees_key][qcp]['total_buyng_power_allocation'] = st.number_input(label=f'', min_value=float(0.0), max_value=float(1.0), value=float(QUEEN_KING[qcp_bees_key][qcp]['total_buyng_power_allocation']), key=f'{qcp}_buying_power_allocation{admin}', label_visibility='hidden')
                    with cols[5]:
                        QUEEN_KING[qcp_bees_key][qcp]['total_borrow_power_allocation'] = st.number_input(label=f'', min_value=float(0.0), max_value=float(1.0), value=float(QUEEN_KING[qcp_bees_key][qcp]['total_borrow_power_allocation']), key=f'{qcp}_borrow_power_allocation{admin}', label_visibility='hidden')
                return True
            
            except Exception as e:
                er, er_line = print_line_of_error()
                st.write(f'{qcp_bees_key} {qcp} failed {er_line}')
        
        def chessboard(acct_info, QUEEN_KING, ticker_allowed, themes, admin=False):
            try:
                
                def handle__new_tickers__AdjustTradingModels(QUEEN_KING, reset_theme=False):
                    # add new trading models if needed
                    # Castle 
                    trading_models = QUEEN_KING['king_controls_queen']['symbols_stars_TradingModel']
                    for qcp, bees_data in QUEEN_KING[qcp_bees_key].items():
                        for ticker in bees_data.get('tickers'):
                            try:
                                if reset_theme:
                                    QUEEN_KING = add_trading_model(status='active', QUEEN_KING=QUEEN_KING, ticker=ticker, model=bees_data.get('model'), theme=bees_data.get('theme'))
                                else:
                                    if ticker not in trading_models.keys():
                                        QUEEN_KING = add_trading_model(status='active', QUEEN_KING=QUEEN_KING, ticker=ticker, model=bees_data.get('model'), theme=bees_data.get('theme'))
                            except Exception as e:
                                print('wtferr', e)
                    return QUEEN_KING

                name = 'Chess Board'
                qcp_bees_key = 'chess_board'

                current_setup = QUEEN_KING['chess_board']
                chess_pieces = set_chess_pieces_symbols(QUEEN_KING=QUEEN_KING, qcp_bees_key=qcp_bees_key)
                view = chess_pieces.get('view')
                all_workers = chess_pieces.get('all_workers')
                qcp_ticker_index = chess_pieces.get('ticker_qcp_index')
                current_tickers = qcp_ticker_index.keys()

                with st.expander(name, True): # ChessBoard
                    allow_queen_to_update_chessboard = st.checkbox("Allow QUEEN to update chessboard for all themes", True)
                    with st.form(f'ChessBoard_form{admin}'):
                        try:
                            cols = st.columns((1,5))

                            with cols[0]:
                                hc.option_bar(option_definition=pq_buttons.get('chess_option_data'),title='', key='chess_search', horizontal_orientation=True)                                
                            with cols[1]:
                                ticker_search = st.text_input("Find Symbol") ####### WORKERBEE

                            with cols[1]:
                                st.subheader(name)
                            
                            cols = st.columns((1,5,2,2,2,2,2,3,2,2))
                            

                            headers = 0
                            for qcp in all_workers:
                                setup_qcp_on_board(cols, QUEEN_KING, qcp_bees_key, qcp, ticker_allowed=ticker_allowed, themes=themes, headers=headers)
                                headers+=1
                            # RevRec
                            revrec = refresh_chess_board__revrec(acct_info, QUEEN, QUEEN_KING, active_queen_order_states, chess_board__revrec={}, revrec__ticker={}, revrec__stars={}) ## Setup Board

                            QUEEN_KING['chess_board__revrec'] = revrec
                            df_qcp = revrec.get('df_qcp')
                            df_ticker = revrec.get('df_ticker')
                            df_stars = revrec.get('df_stars')

                            # for ticker_time_frame in df_stars.index.to_list():
                            #     star_total_budget = df_stars.loc[ticker_time_frame].get('star_total_budget')
                            #     ttf_remaining_budget = return_ttf_remaining_budget(QUEEN, star_total_budget, ticker_time_frame, active_queen_order_states)
                            #     df_stars.at[ticker_time_frame, 'remaining_budget'] = ttf_remaining_budget

                            for qcp in all_workers:
                                # if qcp not in ['castle', 'castle_coin', 'bishop', 'knight']:
                                #     continue
                                
                                total_ticker_budget = 0
                                tickers_cost_basis = 0
                                qcp_tickers = [i for i in qcp_ticker_index.keys() if qcp_ticker_index[i] == qcp]
                                for ticker in qcp_tickers:

                                    total_budget = df_ticker.loc[ticker].get('ticker_total_budget')
                                    total_ticker_budget+=total_budget
                                    q_orders = return_queen_orders__query(QUEEN=QUEEN, queen_order_states=RUNNING_Orders , ticker=ticker)
                                    if len(q_orders) > 0:
                                        current_running_cost_b = sum(q_orders['cost_basis'])
                                        tickers_cost_basis+=current_running_cost_b
                                
                                remaing_qcp_budget = total_ticker_budget - tickers_cost_basis

                                with cols[6]:
                                    QUEEN_KING[qcp_bees_key][qcp]['total_budget'] = st.number_input(label=f'', key=f'{qcp}_total_budget', value=float(df_qcp.loc[qcp].get('total_budget')), help="Allocate Total.$.portfolio to share amongst tickers")
    
                                with cols[7]:
                                    QUEEN_KING[qcp_bees_key][qcp]['remaining_budget'] = st.number_input(label=f'', key=f'{qcp}_remaining_budget', value=remaing_qcp_budget, help="Remaining Total Budget on Margin")
                        

                        except Exception as e:
                            er, er_line = print_line_of_error()
                            print(qcp, ticker)
                                                
                        cols = st.columns((2,3,1))
                        with cols[0]:
                            # edit_df_qcp = st.experimental_data_editor(df_qcp)
                            st.dataframe(df_qcp)
                        with cols[0]:
                            # edit_df_ticker = st.experimental_data_editor(df_ticker, key='df_ticker')
                            st.dataframe(df_ticker)
                        with cols[1]:
                            # edit_df_stars = st.experimental_data_editor(df_stars, key='df_stars')
                            st.dataframe(df_stars)
                        
                        QUEEN_KING['chess_board__revrec'] = {'df_qcp': df_qcp, 'df_ticker': df_ticker, 'df_stars':df_stars,}


                        if st.form_submit_button('Save Board'):
                            if authorized_user == False:
                                st.warning("You Need your Queen First! Please contact pollenq.queen@gmail.com")
                                return False
                            
                            QUEEN_KING = handle__new_tickers__AdjustTradingModels(QUEEN_KING=QUEEN_KING)
                            PickleData(pickle_file=PB_App_Pickle, data_to_store=QUEEN_KING)
                            st.success("New Move Saved")
                            st.experimental_rerun()
                            
                        if st.form_submit_button('Reset ChessBoards Trading Models With Theme', on_click=on_click_ss_value_bool('reset_chessboard_theme')):
                            if authorized_user == False:
                                st.warning("You Need your Queen First! Please contact pollenq.queen@gmail.com")
                                return False

                            reset_theme = True if 'reset_chessboard_theme' in st.session_state and st.session_state['reset_chessboard_theme'] else False
                            print(reset_theme)
                            QUEEN_KING = handle__new_tickers__AdjustTradingModels(QUEEN_KING, reset_theme)
                            PickleData(pickle_file=PB_App_Pickle, data_to_store=QUEEN_KING)
                            st.success("All Trading Models Reset to Theme")
                            st.experimental_rerun()
                            
                            
                            return True
            

            
            except Exception as e:
                print('chessboard ', e, print_line_of_error())

        def chess_board__workerbees(QUEEN_KING, admin=True):

            try:
                
                name = 'Workerbees_Admin'
                qcp_bees_key = 'qcp_workerbees'

                ticker_allowed = list(KING['ticker_universe'].get('alpaca_symbols_dict').keys()) + crypto_symbols__tickers_avail
                
                current_setup = QUEEN_KING['chess_board']
                chess_pieces = set_chess_pieces_symbols(QUEEN_KING=QUEEN_KING, qcp_bees_key=qcp_bees_key)
                view = chess_pieces.get('view')
                all_workers = chess_pieces.get('all_workers')
                qcp_ticker_index = chess_pieces.get('ticker_qcp_index')
                current_tickers = qcp_ticker_index.keys()

                add_new_qcp__to_Queens_workerbees(qcp_bees_key)

                # with st.expander("Workerbee Controls", True):
                #     refresh_workerbees(QUEEN_KING)

                with st.expander(name, True):

                    with st.form(f'Update WorkerBees{admin}'):
                        
                        ticker_search = st.text_input("Find Symbol") ####### WORKERBEE

                        cols = st.columns((1,1,1))

                        with cols[1]:
                            st.subheader(name)
                        cols = st.columns((1,3,2,2,2,2))
                        for qcp in all_workers:
                            try:
                                if qcp == 'castle_coin':
                                    with cols[0]:
                                        st.image("https://s3.us-east-2.amazonaws.com/nomics-api/static/images/currencies/BSV.png", width=54)
                                elif qcp == 'castle':
                                    with cols[0]:
                                        st.image(MISC.get('castle_png'), width=54)
                                elif qcp == 'bishop':
                                    with cols[0]:
                                        st.image(MISC.get('bishop_png'), width=74)
                                elif qcp == 'knight':
                                    with cols[0]:
                                        st.image(MISC.get('knight_png'), width=74)
                                else:
                                    st.image(MISC.get('knight_png'), width=74)
                                
                                ticker_list = QUEEN_KING[qcp_bees_key][qcp]['tickers']
                                all_tickers = ticker_allowed + crypto_symbols__tickers_avail
                                # st.write([i for i in ticker_list if i not in all_tickers])
                                QUEEN_KING[qcp_bees_key][qcp]['tickers'] = [i for i in ticker_list if i in all_tickers]

                                with cols[1]:
                                    QUEEN_KING[qcp_bees_key][qcp]['tickers'] = st.multiselect(label=f'symbols', options=ticker_allowed + crypto_symbols__tickers_avail, default=QUEEN_KING[qcp_bees_key][qcp]['tickers'], help='Castle Should Hold your Highest Valued Symbols', key=f'{qcp}tickers{admin}')
                                with cols[2]:
                                    st.selectbox(label='Model', options=['MACD'], key=f'{qcp}model{admin}')
                                with cols[3]:
                                    QUEEN_KING[qcp_bees_key][qcp]['MACD_fast_slow_smooth']['fast'] = st.number_input(f'fast', min_value=1, max_value=88, value=int(QUEEN_KING[qcp_bees_key][qcp]['MACD_fast_slow_smooth']['fast']), key=f'{qcp}fast{admin}')
                                with cols[4]:
                                    QUEEN_KING[qcp_bees_key][qcp]['MACD_fast_slow_smooth']['slow'] = st.number_input(f'slow', min_value=1, max_value=88, value=int(QUEEN_KING[qcp_bees_key][qcp]['MACD_fast_slow_smooth']['slow']), key=f'{qcp}slow{admin}')
                                with cols[5]:
                                    QUEEN_KING[qcp_bees_key][qcp]['MACD_fast_slow_smooth']['smooth'] = st.number_input(f'slow', min_value=1, max_value=88, value=int(QUEEN_KING[qcp_bees_key][qcp]['MACD_fast_slow_smooth']['smooth']), key=f'{qcp}smooth{admin}')
                            except Exception as e:
                                print(e, qcp)
                                st.write(qcp, " ", e)
                                st.write(QUEEN_KING[qcp_bees_key][qcp])

                        if st.form_submit_button('Save ChessBoard'):
                            if authorized_user == False:
                                st.warning("You Need your Queen First! Please contact pollenq.queen@gmail.com")
                                return False
                            
                            app_req = create_AppRequest_package(request_name='workerbees')
                            QUEEN_KING['workerbees_requests'].append(app_req)
                            PickleData(pickle_file=PB_App_Pickle, data_to_store=QUEEN_KING)
                            st.success("New Move")
                            
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

        
        def update_trading_models(QUEEN_KING):
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
                    title = "Trading Models"
                
                st.title(title)

                cols = st.columns(4)
                with cols[0]:
                    models_avail = list(QUEEN_KING['king_controls_queen'][control_option].keys())
                    ticker_option_qc = st.selectbox("Symbol", models_avail, index=models_avail.index(["SPY" if "SPY" in models_avail else models_avail[0]][0]))                

                ## Trading Model
                if saved_model_ticker != 'select':
                    st.info("You Are Viewing Saved Model")
                    trading_model = QUEEN_KING['saved_trading_models'][saved_model_ticker]
                else:
                    trading_model = QUEEN_KING['king_controls_queen'][control_option][ticker_option_qc]

                # Trading Global Model Levels
                star_avail = list(trading_model['stars_kings_order_rules'].keys())
                trigbees_avail = list(trading_model['trigbees'].keys())
                blocktime_avail = list(trading_model['time_blocks'].keys())
                
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
                        'short_position': {'type': None},
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
                'KOR_version': 'KOR_version',
                }
                # take_profit_in_vwap_deviation_range={'low_range': -.05, 'high_range': .05}

                trading_model_revrec = {} #
                trading_model_revrec_s = {}
                with st.form("star_revrec"):
                    st.header("Reallocate Star Buying Power")
                    cols = st.columns((1,1,1,1,1,1,1))
                    c = 0
                    for star, star_vars in trading_model.get('stars_kings_order_rules').items():
                        trading_model_revrec[star] = star_vars.get("buyingpower_allocation_LongTerm")
                        trading_model_revrec_s[star] = star_vars.get("buyingpower_allocation_ShortTerm")
                        with cols[c]:
                            trading_model['stars_kings_order_rules'][star]["buyingpower_allocation_LongTerm"] = st.slider(label=f'L {star}', value=star_vars.get('buyingpower_allocation_LongTerm'), key=f'{star}{"_"}{"buying_power"}')
                            trading_model['stars_kings_order_rules'][star]["buyingpower_allocation_ShortTerm"] = st.slider(label=f'S {star}', value=star_vars.get('buyingpower_allocation_ShortTerm'), key=f'{star}{"_"}{"buying_power_s"}')
                        c+=1
                        # with cols[0]:
                        #     mark_down_text(align='left', text=star)

                    df_revrec = pd.DataFrame(trading_model_revrec.items())
                    df_revrec_s = pd.DataFrame(trading_model_revrec_s.items())
                    df = story_view(STORY_bee=STORY_bee, ticker=ticker_option_qc)['df']
                    # df_write = pd.concat([df], axis=1) ## Need to fix
                    df_style = df.style.background_gradient(cmap="RdYlGn", gmap=df['current_macd_tier'], axis=0, vmin=-8, vmax=8)
                    # with cols[1]:
                    st.write(df_style)
                    # edited_df = st.experimental_data_editor(df_write)
                    
                    if st.form_submit_button("Reallocate Star Power"):
                        QUEEN_KING['saved_trading_models'].update(trading_model)
                        PickleData(pickle_file=PB_App_Pickle, data_to_store=QUEEN_KING)
                        return_image_upon_save(title="Saved")
                        st.experimental_rerun()
                
                with st.form('trading model form'):
                    st.subheader("Kings Order Rules Settings")
                    #### TRADING MODEL ####
                    # Ticker Level 1
                    # Star Level 2
                    # Trigbees Level 3
                    cols = st.columns(3)

                    with cols[0]:
                        star_option_qc = st.selectbox("Star", star_avail, index=star_avail.index(["1Minute_1Day" if "1Minute_1Day" in star_avail else star_avail[0]][0]))
                    with cols[1]:
                        trigbee_sel = st.selectbox("Trigbee", trigbees_avail, index=trigbees_avail.index(["buy_cross-0" if "buy_cross-0" in trigbees_avail else trigbees_avail[0]][0]))
                    with cols[2]:
                        # wave_blocks_option = st.selectbox("Block Time", KING['waveBlocktimes'])
                        wave_blocks_option = st.selectbox("BlockTime", blocktime_avail, index=blocktime_avail.index(["morning_9-11" if "morning_9-11" in blocktime_avail else blocktime_avail[0]][0]))

                    trading_model__star = trading_model['stars_kings_order_rules'][star_option_qc]
                    theme = st.selectbox(label=f'Theme', options=pollen_themes_selections, index=pollen_themes_selections.index(trading_model.get('theme')), key=f'theme_reset')
                    king_order_rules_update = trading_model__star['trigbees'][trigbee_sel][wave_blocks_option]
                    
                    # with st.expander(f'{ticker_option_qc} Global Settings'):
                    st.subheader(f'{ticker_option_qc} Global Settings')
                    cols = st.columns((1,1,1,1,1))
                    
                    # all ticker settings
                    for kor_option, kor_v in trading_model.items():
                        # if kor_option in ticker_model_level_1.keys():
                        #     item_type = ticker_model_level_1[kor_option]['type']
                        #     if kor_option == 'theme':
                        #         trading_model[kor_option] = st.selectbox(label=f'{ticker_option_qc}{"_"}{kor_option}', options=item_val, index=item_val.index(kor_v), key=f'{ticker_option_qc}{"_"}{kor_option}')

                        #     if item_type == None:
                        #         continue # not allowed edit
                        if kor_option == 'stars_kings_order_rules':
                            continue

                        if kor_option == 'status':
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

                        elif kor_option == 'short_position':
                            with cols[1]:
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
                                trading_model["buyingpower_allocation_LongTerm"] = st.slider(label=f'{"Long Term Allocation"}', key='tic_long', min_value=float(0.0), max_value=float(1.0), value=float(trading_model['buyingpower_allocation_LongTerm']), help="Set the Length of the trades, lower number means short trade times")

                        elif kor_option == 'buyingpower_allocation_ShortTerm':
                            with cols[0]:
                                trading_model['buyingpower_allocation_ShortTerm'] = st.slider(label=f'{"Short Term Allocation"}', key='tic_short', min_value=float(0.0), max_value=float(1.0), value=float(trading_model['buyingpower_allocation_ShortTerm']), help="Set the Length of the trades, lower number means short trade times")

                                # if long > short:
                                #     long = long
                                # else:
                                #     short = 1 - long
                                
                                # trading_model['buyingpower_allocation_ShortTerm'] = short
                                # trading_model["buyingpower_allocation_LongTerm"] = long
                        else:
                            st.write("not accounted ", f'{kor_option} {trading_model.get(kor_option)}')

                    # with st.expander(f'{star_option_qc} Time Frame'):
                    st.subheader(f'Time Frame: {star_option_qc}')
                    # st.write([i for i in star_level_2.keys() if i ])
                    st.info("Set the Stars Gravity; allocation of power on the set of stars your Symbol's choice")
                    cols = st.columns((1,1,1))
                    
                    for item_control, itc_vars in star_level_2.items():
                        if item_control not in QUEEN_KING['king_controls_queen'][control_option][ticker_option_qc]['stars_kings_order_rules'][star_option_qc].keys():
                            st.write(f'{item_control} not in scope')
                            continue
                    

                    with cols[0]: # total_budget
                        trading_model['stars_kings_order_rules'][star_option_qc]['total_budget'] = st.number_input(label='$Budget', value=float(trading_model['stars_kings_order_rules'][star_option_qc]['total_budget']))

                        st.write("L power ", trading_model['stars_kings_order_rules'][star_option_qc]['buyingpower_allocation_LongTerm'])
                        st.write("S power ", trading_model['stars_kings_order_rules'][star_option_qc]['buyingpower_allocation_ShortTerm'])
                    
                    with cols[1]: # index_long_X
                        trading_model['stars_kings_order_rules'][star_option_qc]['index_long_X'] = st.selectbox("Long X Weight", options=['1X', '2X', '3X'], index=['1X', '2X', '3X'].index(f'{trading_model["stars_kings_order_rules"][star_option_qc]["index_long_X"]}'))

                    with cols[1]: # index_inverse_X
                        trading_model['stars_kings_order_rules'][star_option_qc]['index_inverse_X'] = st.selectbox("Short X Weight", options=['1X', '2X', '3X'], index=['1X', '2X', '3X'].index(f'{trading_model["stars_kings_order_rules"][star_option_qc]["index_inverse_X"]}'))                    
                    
                    with cols[2]: # trade_using_limits
                        trading_model['stars_kings_order_rules'][star_option_qc]['trade_using_limits'] = st.checkbox("trade_using_limits", value=trading_model['stars_kings_order_rules'][star_option_qc]['trade_using_limits'])
                    
                    page_line_seperator(height='3')
                    
                    with cols[1]:
                        st.write('Star Allocation Power')
                    page_line_seperator(height='1')

                    cols = st.columns((1,1,1,1,1,1,6))
                    
                    c = 0
                    for power_ranger, pr_active in trading_model['stars_kings_order_rules'][star_option_qc]['power_rangers'].items():
                        # st.write(power_ranger, pr_active)
                        c = 0 if c > 5 else c
                        with cols[c]:
                            trading_model['stars_kings_order_rules'][star_option_qc]['power_rangers'][power_ranger] = st.slider(label=f'{power_ranger}', min_value=float(0.0), max_value=float(1.0), value=float(pr_active), key=f'{star_option_qc}{power_ranger}')
                        c+=1
                    
                    # with st.expander(f'{wave_blocks_option} Time Block KOR'):
                    st.subheader(f' Time Block KOR: {wave_blocks_option}')
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

        
        def show_heartbeat():
            cols = st.columns(4)
            with cols[0]:
                if st.button("clear all sell orders", key=f'button_a'):
                    QUEEN_KING['sell_orders'] = []
                    PickleData(PB_App_Pickle, QUEEN_KING)
                st.write("sell_orders")
                st.write(QUEEN_KING['sell_orders'])
                
                st.write("Heart")
                st.write(QUEEN['heartbeat'])
            
            with cols[1]:
                if st.button("clear all queen_sleep", key=f'button_b'):
                    QUEEN_KING['queen_sleep'] = []
                    PickleData(PB_App_Pickle, QUEEN_KING)
                st.write("queen_sleep")
                st.write(QUEEN_KING['queen_sleep'])
                st.write("queen_messages")
                st.write(QUEEN['queens_messages'])
            with cols[2]:
                if st.button("clear all update_queen_order", key=f'button_c'):
                    QUEEN_KING['update_queen_order'] = []
                    PickleData(PB_App_Pickle, QUEEN_KING)
                st.write("update_queen_order")
                st.write(QUEEN_KING['update_queen_order'])
            with cols[3]:
                if st.button("clear all wave_triggers", key=f'button_d'):
                    QUEEN_KING['wave_triggers'] = []
                    PickleData(PB_App_Pickle, QUEEN_KING)
                st.write(QUEEN_KING.get('wave_triggers'))


        def queen_wavestories(QUEEN, STORY_bee, POLLENSTORY, tickers_avail):
            # cust_Button("misc/waves.png", hoverText='', key='waves_icon', height=f'23px')
            # st.image((os.path.join(hive_master_root(), "/custom_button/frontend/build/misc/waves.png")), width=33)

            def its_morphin_time_view(QUEEN, STORY_bee, ticker, POLLENSTORY, combine_story=False):

                now_time = datetime.now(est)
                active_ttf = QUEEN['heartbeat']['available_tickers'] = [i for (i, v) in STORY_bee.items() if (now_time - v['story']['time_state']).seconds < 86400]
                eight_tier_maxbase = 8 * 8 
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

                t = '{:,.2%}'.format(total_current_macd_tier/ eight_tier_maxbase)
                h = '{:,.2%}'.format(total_current_hist_tier / eight_tier_maxbase)


                return {'macd_tier_guage': t, 'hist_tier_guage': h, 'macd_tier_guage_value': (total_current_macd_tier/ eight_tier_maxbase),
                'hist_tier_guage_value': (total_current_hist_tier/ eight_tier_maxbase)
                }

            def ticker_time_frame__option(tickers_avail, req_key):
                cols = st.columns(2)
                with cols[0]:
                    if 'sel_tickers' not in st.session_state:
                        st.session_state['sel_tickers'] = tickers_avail[0]

                    tickers = st.multiselect('Symbols', options=list(tickers_avail), default=tickers_avail[0], help='View Groups of symbols to Inspect where to send the Bees', key=f'ticker{req_key}')
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
                req = ticker_time_frame__option(tickers_avail=tickers_avail, req_key='wavestories')
                tickers = req.get('tickers')
                ticker_option = req.get('ticker_option')
                frame_option = req.get('frame_option')

                if len(tickers) > 8:
                    st.warning("Total MACD GUAGE Number reflects all tickers BUT you may only view 8 tickers")
                cols = st.columns((1, 3))

                for symbol in tickers:
                    # star__view = its_morphin_time_view(QUEEN=QUEEN, STORY_bee=STORY_bee, ticker=symbol, POLLENSTORY=POLLENSTORY) ## RETURN FASTER maybe cache?
                    story_views = story_view(STORY_bee=STORY_bee, ticker=symbol)
                    # st.write(story_views.get('df_agg'))
                    df = story_views.get('df')
                    df = df.set_index('star')
                    trading_model = QUEEN_KING['king_controls_queen']['symbols_stars_TradingModel'].get(symbol)
                    story_guages = wave_guage(df, trading_model=trading_model)
                    df_style = df.style.background_gradient(cmap="RdYlGn", gmap=df['current_macd_tier'], axis=0, vmin=-8, vmax=8)
                    with cols[0]:
                        st.plotly_chart(create_guage_chart(title=f'{symbol} Wave Gauge', value=float(story_guages.get(f'{"weight_L"}_macd_tier_guage'))))
                    with cols[1]:
                        for weight_ in ['weight_L', 'weight_S']:
                            macd_ = story_guages.get(f'{weight_}_macd_tier_guage')
                            hist_ = story_guages.get(f'{weight_}_hist_tier_guage')
                            mark_down_text(fontsize=25, 
                                           text=f'{symbol} {f"{weight_} MACD Gauge "}{"{:,.2%}".format(macd_)}{" Hist Gauge "}{"{:,.2%}".format(hist_)}')

                        st.dataframe(df_style)


                return True
            except Exception as e:
                print(e, print_line_of_error()) ## error should stop when you have data of bees?
                return False
            

        def orders_agrid():
            ordertables__agrid = queen_order_flow(QUEEN=QUEEN, active_order_state_list=active_order_state_list, order_buttons=st.session_state.get('order_buttons'))
            if authorized_user:
                if ordertables__agrid == False:
                    return True
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


        ########################################################
        ########################################################
        #############The Infinite Loop of Time #################
        ########################################################
        ########################################################
        ########################################################

    try:
        # print("QC Start")

        pq_buttons = pollenq_button_source()

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
            
    
        QUEENsHeart = ReadPickleData(PB_QUEENsHeart_PICKLE)

        pollen_themes_selections = list(pollen_themes(KING).keys())        
        prod_keys_confirmed = QUEEN_KING['users_secrets']['prod_keys_confirmed']
        sandbox_keys_confirmed = QUEEN_KING['users_secrets']['sandbox_keys_confirmed']

        api = return_alpaca_user_apiKeys(QUEEN_KING=QUEEN_KING, authorized_user=authorized_user, prod=st.session_state['production'])
        acct_info = refresh_account_info(api=api)['info_converted']
        if st.session_state['authorized_user']: ## MOVE THIS INTO pollenq?
            clean_out_app_requests(QUEEN=QUEEN, QUEEN_KING=QUEEN_KING, request_buckets=['subconscious', 'sell_orders', 'queen_sleep', 'update_queen_order'])
        

        # # if authorized_user: log type auth and none
        log_dir = os.path.join(db_root, 'logs')
        init_logging(queens_chess_piece=queens_chess_piece, db_root=db_root, prod=st.session_state['production'])

        # db global
        # Ticker DataBase
        call_all_ticker_data = st.sidebar.button("swarmQueen Symbols", True)

        coin_exchange = "CBSE"
        ticker_db = return_QUEENs__symbols_data(QUEEN=QUEEN, QUEEN_KING=QUEEN_KING, swarmQueen=call_all_ticker_data)
        POLLENSTORY = ticker_db['pollenstory']
        STORY_bee = ticker_db['STORY_bee']
        # tic_need_TM = [i.split("_")[0] for i in STORY_bee.keys()]
        tickers_avail = [list(set(i.split("_")[0] for i in STORY_bee.keys()))][0]
        
        # def cache_tradingModelsNotGenerated() IMPROVEMENT TO SPEED UP CACHE cache function
        tic_need_TM = [i for i in tickers_avail if i not in QUEEN_KING['king_controls_queen'].get('symbols_stars_TradingModel')]
        if len(tic_need_TM) > 0:
            print("Adding Trading Model")
            for ticker in tic_need_TM:
                tradingmodel1 = generate_TradingModel(ticker=ticker, status='active', theme="long_star")['MACD'][ticker]
                QUEEN_KING['king_controls_queen']['symbols_stars_TradingModel'][ticker] = tradingmodel1
        
        ticker_db_errors = ticker_db.get('errors')
        if len(ticker_db_errors) > 0:
            st.error("symbol errors")
            st.write(ticker_db_errors)

        # return__snapshot__latest_PriceInfo()
        with st.spinner("Refreshing"): # ozzbot

            if authorized_user:
                
                def run_function__async(func_list):
                    try:
                        s = datetime.now(est)

                        async def read_pkl_file(session, qcp):
                            async with session:
                                try:
                                    qcp()
                                except Exception as e:
                                    print(e, qcp)
                                    return {qcp: e}

                        async def main(func_list):

                            async with aiohttp.ClientSession() as session:
                                return_list = []
                                tasks = []
                                for qcp in (func_list):  # castle: [spy], bishop: [goog], knight: [META] ..... pawn1: [xmy, skx], pawn2: [....]
                                    # print(qcp)
                                    tasks.append(asyncio.ensure_future(read_pkl_file(session, qcp)))
                                original_pokemon = await asyncio.gather(*tasks)
                                for pokemon in original_pokemon:
                                    return_list.append(pokemon)
                                return return_list

                        x = asyncio.run(main(func_list))
                        e = datetime.now(est)
                        print(f"--- All Workers Refreshed {(e - s)} seconds ---")
                        return x
                    except Exception as e:
                        print("qtf", e, print_line_of_error())

                def readgroup_pklfiles__async(qcp_s):
                    try:
                        s = datetime.now(est)

                        async def read_pkl_file(session, qcp):
                            async with session:
                                try:
                                    return ReadPickleData(qcp)
                                except Exception as e:
                                    print(e, qcp)
                                    return False

                        async def main(qcp_s):

                            async with aiohttp.ClientSession() as session:
                                return_list = []
                                tasks = []
                                for qcp in (qcp_s):  # castle: [spy], bishop: [goog], knight: [META] ..... pawn1: [xmy, skx], pawn2: [....]
                                    # print(qcp)
                                    tasks.append(asyncio.ensure_future(read_pkl_file(session, qcp)))
                                original_pokemon = await asyncio.gather(*tasks)
                                for pokemon in original_pokemon:
                                    return_list.append(pokemon)
                                return return_list

                        x = asyncio.run(main(qcp_s))
                        e = datetime.now(est)
                        print(f"All Workers Refreshed {qcp_s} --- {(e - s)} seconds ---")
                        return x
                    except Exception as e:
                        print("qtf", e, print_line_of_error())



                if st.session_state['show_queenheart']:
                    with st.expander('heartbeat', True):
                        show_heartbeat()

                if st.session_state['total_profits']:
                    return_total_profits(QUEEN=QUEEN)
        
                # print("WAVES")
                if st.session_state['orders']:
                    hc.option_bar(option_definition=pq_buttons.get('option_data_orders'),title='P.Orders', key='orders_main', horizontal_orientation=True) #,override_theme=over_theme,font_styling=font_fmt,horizontal_orientation=True)
                    orders_agrid()
                    if st.session_state['username'] in ["stefanstapinski@gmail.com"]:
                        st_custom_grid("stefanstapinski", "http://127.0.0.1:8000/api/data/queen", 2, 500, prod=st.session_state['production'])
                    # QUEEN['queen_orders'].iloc[3]
                    # st_custom_grid(api:str, refresh_sec:int, refresh_cutoff:int,gridoption_build)
                        
                if st.session_state['waves'] == True:
                    with st.expander('waves', True):
                        hc.option_bar(option_definition=pq_buttons.get('charts_option_data'),title='Waves', key='waves_toggle', horizontal_orientation=True) #,override_theme=over_theme,font_styling=font_fmt,horizontal_orientation=True)
                        queen_wavestories(QUEEN, STORY_bee, POLLENSTORY, tickers_avail)
                    with st.expander('STORY_bee'):
                        st.write(STORY_bee['SPY_1Minute_1Day']['story'])
            
                if st.session_state['workerbees'] == True:
                    hc.option_bar(option_definition=pq_buttons.get('workerbees_option_data'),title='WorkerBees', key='workerbees_option_data', horizontal_orientation=True) #,override_theme=over_theme,font_styling=font_fmt,horizontal_orientation=True)   
                    queen_triggerbees()
                    if st.session_state['admin']:
                        if st.button("Yahoo Return Fin.Data Job"):
                            with st.spinner("running yahoo.Fin.Data job"):
                                init_ticker_stats__from_yahoo()
                    with st.expander("yahoo stats", False):
                        db = ReadPickleData(os.path.join(hive_master_root(), 'db/yahoo_stats_bee.pkl'))
                        # st.write(db.keys())
                        avail_ticker_list = list(db.keys())
                        ticker_option = st.selectbox("ticker", options=avail_ticker_list)
                        if ticker_option is not None:
                            df_i = len(db.get(ticker_option))
                            for n in  range(df_i):
                                st.write(db.get(ticker_option)[n])
            
                if st.session_state['the_flash'] == True:
                    with st.expander("The Flash", True):
                        queen_beeAction_theflash()
            
                if st.session_state['charts'] == True:
                    hc.option_bar(option_definition=pq_buttons.get('charts_option_data'),title='Charts', key='charts_toggle', horizontal_orientation=True) #,override_theme=over_theme,font_styling=font_fmt,horizontal_orientation=True)

                    with st.expander("charts", True):
                        advanced_charts()
            
                if st.session_state['chess_board'] == True:
                    hc.option_bar(option_definition=pq_buttons.get('option_data'),title='C.Board', key='admin_workerbees', horizontal_orientation=True) #,override_theme=over_theme,font_styling=font_fmt,horizontal_orientation=True)
                    ticker_allowed = list(KING['ticker_universe'].get('alpaca_symbols_dict').keys()) + crypto_symbols__tickers_avail
                    themes = list(pollen_themes(KING).keys())

                    if 'admin_workerbees' in st.session_state and st.session_state['admin_workerbees'] == "admin_workerbees":
                        chess_board__workerbees(QUEEN_KING=QUEEN_KING, admin=admin)
                    else:
                        chessboard(acct_info=acct_info, QUEEN_KING=QUEEN_KING, ticker_allowed=ticker_allowed, themes=themes, admin=False)
                    add_new_qcp__to_chessboard(cols=False, QUEEN_KING=QUEEN_KING, qcp_bees_key='chess_board', ticker_allowed=ticker_allowed, themes=themes)
            
                if st.session_state['queens_mind']:
                    hc.option_bar(option_definition=pq_buttons.get('option_data_qm'),title='T.Models', key='queens_mind_toggle', horizontal_orientation=True) #,override_theme=over_theme,font_styling=font_fmt,horizontal_orientation=True)
                    with st.expander("Trading Models"):
                        update_trading_models(QUEEN_KING)                            
            




                func_list = ['queens_mind', 'chess_board', 'orders', 'waves', 'workerbees', 'charts', 'the_flash']
                func_list = [i for i in func_list if st.session_state[i]]
                # if len(func_list) == 0:
                #     st.info("I would Suggest Checking our Your ChessBoard This Morning")
                # else:
                #     tabs = st.tabs(func_list)
                c = 0
                for tab_name in func_list:
                    with tabs[c]:
                        # st.write(tab_name)
                        c+=1
                        if tab_name == 'waves':
                            if st.session_state['waves'] == True:

                                st.write("waves")
                                # with st.expander('waves', True):
                                #     hc.option_bar(option_definition=pq_buttons.get('charts_option_data'),title='Waves', key='waves_toggle', horizontal_orientation=True) #,override_theme=over_theme,font_styling=font_fmt,horizontal_orientation=True)
                                #     queen_wavestories(QUEEN, STORY_bee, POLLENSTORY, tickers_avail)
                                # with st.expander('STORY_bee'):
                                #     st.write(STORY_bee['SPY_1Minute_1Day']['story'])
                        if tab_name == 'workerbees':
                            if st.session_state['workerbees'] == True:
                                st.write("waves")
                                # hc.option_bar(option_definition=pq_buttons.get('workerbees_option_data'),title='WorkerBees', key='workerbees_option_data', horizontal_orientation=True) #,override_theme=over_theme,font_styling=font_fmt,horizontal_orientation=True)   
                                # queen_triggerbees()
                                # if st.session_state['admin']:
                                #     if st.button("Yahoo Return Fin.Data Job"):
                                #         with st.spinner("running yahoo.Fin.Data job"):
                                #             init_ticker_stats__from_yahoo()
                                # with st.expander("yahoo stats", False):
                                #     db = ReadPickleData(os.path.join(hive_master_root(), 'db/yahoo_stats_bee.pkl'))
                                #     # st.write(db.keys())
                                #     avail_ticker_list = list(db.keys())
                                #     ticker_option = st.selectbox("ticker", options=avail_ticker_list)
                                #     if ticker_option is not None:
                                #         df_i = len(db.get(ticker_option))
                                #         for n in  range(df_i):
                                #             st.write(db.get(ticker_option)[n])
                        if tab_name == 'the_flash':
                            st.write("waves")
                            # if st.session_state['the_flash'] == True:
                            #     with st.expander("The Flash", True):
                            #         queen_beeAction_theflash()
                        if tab_name == 'charts':
                            st.write("waves")
                            # if st.session_state['charts'] == True:
                            #     hc.option_bar(option_definition=pq_buttons.get('charts_option_data'),title='Charts', key='charts_toggle', horizontal_orientation=True) #,override_theme=over_theme,font_styling=font_fmt,horizontal_orientation=True)

                            #     with st.expander("charts", True):
                            #         advanced_charts()
                        if tab_name == 'chess_board':
                            if st.session_state['chess_board'] == True:
                                st.write("waves")
                                # hc.option_bar(option_definition=pq_buttons.get('option_data'),title='C.Board', key='admin_workerbees', horizontal_orientation=True) #,override_theme=over_theme,font_styling=font_fmt,horizontal_orientation=True)
                                # ticker_allowed = list(KING['ticker_universe'].get('alpaca_symbols_dict').keys()) + crypto_symbols__tickers_avail
                                # themes = list(pollen_themes(KING).keys())

                                # if 'admin_workerbees' in st.session_state and st.session_state['admin_workerbees'] == "admin_workerbees":
                                #     chess_board__workerbees(QUEEN_KING=QUEEN_KING, admin=admin)
                                # else:
                                #     chessboard(acct_info=acct_info, QUEEN_KING=QUEEN_KING, ticker_allowed=ticker_allowed, themes=themes, admin=False)
                                # add_new_qcp__to_chessboard(cols=False, QUEEN_KING=QUEEN_KING, qcp_bees_key='chess_board', ticker_allowed=ticker_allowed, themes=themes)
                        if tab_name == 'queens_mind':
                            st.write("waves")
                            # if st.session_state['queens_mind']:
                            #     hc.option_bar(option_definition=pq_buttons.get('option_data_qm'),title='T.Models', key='queens_mind_toggle', horizontal_orientation=True) #,override_theme=over_theme,font_styling=font_fmt,horizontal_orientation=True)
                            #     with st.expander("Trading Models"):
                            #         update_trading_models(QUEEN_KING)                            
                        if tab_name == 'orders':
                            st.write("waves")
                            # if st.session_state['orders']:
                            #     hc.option_bar(option_definition=pq_buttons.get('option_data_orders'),title='P.Orders', key='orders_main', horizontal_orientation=True) #,override_theme=over_theme,font_styling=font_fmt,horizontal_orientation=True)
                            #     orders_agrid()
                            #     if st.session_state['username'] in ["stefanstapinski@gmail.com"]:
                            #         st_custom_grid("stefanstapinski", "http://127.0.0.1:8000/api/data/queen", 2, 500, prod=st.session_state['production'])
                            #     # QUEEN['queen_orders'].iloc[3]
                            #     # st_custom_grid(api:str, refresh_sec:int, refresh_cutoff:int,gridoption_build)
                                
                            # print("STOP QUEEN")

                stop_queenbee(QUEEN_KING)
                clear_subconscious_Thought(QUEEN, QUEEN_KING)                    
                page_session_state__cleanUp(page=page)

                def all_button_keys():
                    return {
                        'orders': st.session_state['orders'],
                        'chess_board': st.session_state['chess_board'],
                    'queens_mind': update_trading_models,
                    'charts_toggle': advanced_charts,
                    }
                
                # active_tabs = [i for i in all_button_keys.keys() if st.session_state[i]]
                # t = st.tabs(active_tabs)
                # for n in len(active_tabs):
                #     with t[n]:
                #         all_button_keys[]
                # for key, func in all_button_keys.items():

                # st.session_state['last_page'] = 'queen'
                # QUEEN_KING['last_page_objects'] = {
                #     'orders': st.session_state['orders'],
                #     'chess_board': st.session_state['chess_board'],
                #     'queens_mind': update_trading_models,
                #     'charts_toggle': advanced_charts,

                # }
                # PickleData(PB_App_Pickle, QUEEN_KING)
                # print("QC", return_timestamp_string())
        ##### END ####
    except Exception as e:
        print('queensconscience', e, print_line_of_error(), return_timestamp_string())

if __name__ == '__main__':
    queens_conscience(False, False, False, False, False)