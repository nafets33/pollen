
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
from chess_piece.app_hive import create_wave_chart_all, create_slope_chart, create_wave_chart_single, create_wave_chart, create_guage_chart, create_main_macd_chart, page_session_state__cleanUp, trigger_airflow_dag, send_email, queen__account_keys, progress_bar, queen_order_flow, mark_down_text, click_button_grid, nested_grid, mark_down_text, page_line_seperator, write_flying_bee, hexagon_gif, local_gif, flying_bee_gif, pollen__story
from chess_piece.king import kingdom__grace_to_find_a_Queen, return_QUEENs__symbols_data, hive_master_root, streamlit_config_colors, local__filepaths_misc, print_line_of_error
from chess_piece.queen_hive import init_pollen_dbs, init_qcp, return_alpaca_user_apiKeys, return_queen_controls, return_STORYbee_trigbees, add_key_to_app, refresh_account_info, generate_TradingModel, stars, analyze_waves, KINGME, story_view, return_alpc_portolio, ReadPickleData, pollen_themes, PickleData, return_timestamp_string, init_logging
from ozz.ozz_bee import send_ozz_call
# import random
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

# ###### GLOBAL # ######
ARCHIVE_queenorder = 'archived'
active_order_state_list = ['running', 'running_close', 'submitted', 'error', 'pending', 'completed', 'completed_alpaca', 'running_open', 'archived_bee']
active_queen_order_states = ['submitted', 'accetped', 'pending', 'running', 'running_close', 'running_open']
CLOSED_queenorders = ['running_close', 'completed', 'completed_alpaca']
RUNNING_Orders = ['running', 'running_open']
RUNNING_CLOSE_Orders = ['running_close']

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
queen_png = MISC['queen_png']
knight_png = MISC['knight_png']
mainpage_bee_png = MISC['mainpage_bee_png']
floating_queen_gif = MISC['floating_queen_gif']
chess_board__gif = MISC['chess_board__gif']
bee_power_image = MISC['bee_power_image']
hex_image = MISC['hex_image']
hive_image = MISC['hive_image']
queen_image = MISC['queen_image']
queen_angel_image = MISC['queen_angel_image']
flyingbee_gif_path = MISC['flyingbee_gif_path']
flyingbee_grey_gif_path = MISC['flyingbee_grey_gif_path']
bitcoin_gif = MISC['bitcoin_gif']
power_gif = MISC['power_gif']
uparrow_gif = MISC['uparrow_gif']
learningwalk_bee = MISC['learningwalk_bee']
queen_flair_gif = MISC['queen_flair_gif']
chess_piece_queen = MISC['chess_piece_queen']
runaway_bee_gif = MISC['runaway_bee_gif']
queen_crown_url = MISC['queen_crown_url']
pawn_png_url = MISC['pawn_png_url']

# hexagon_loop = MISC['hexagon_loop']
# purple_heartbeat_gif = MISC['purple_heartbeat_gif'] MISC.get('puprple')

moving_ticker_gif = MISC['moving_ticker_gif']
# heart_bee_gif = MISC['heart_bee_gif']

learningwalk_bee = Image.open(learningwalk_bee)
page_icon = Image.open(bee_image)

##### STREAMLIT ###
k_colors = streamlit_config_colors()
default_text_color = k_colors['default_text_color'] # = '#59490A'
default_font = k_colors['default_font'] # = "sans serif"
default_yellow_color = k_colors['default_yellow_color'] # = '#C5B743'

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

def queens_conscience():
    with st.spinner("Welcome to the QueensMind"):

        # signin_main(page='QueensConscience')
        
        # progress_bar(value=89)  ## show user completion of user flow interaction

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
        
        cols = st.columns((4,8,4))
        if prod:
            with cols[1]:
                # st.warning("LIVE ENVIORMENT The RealWorld")
                mark_down_text(text='LIVE', fontsize='23', align='left', color="Green", sidebar=True)
                flying_bee_gif(sidebar=True)

        else:
            with cols[1]:
                # st.info("SandBox")
                mark_down_text(text='SandBox', fontsize='23', align='left', color="Red", sidebar=True)
                local_gif(gif_path=flyingbee_grey_gif_path, sidebar=True)
        
        PB_QUEEN_Pickle = st.session_state['PB_QUEEN_Pickle'] 
        PB_App_Pickle = st.session_state['PB_App_Pickle'] 
        PB_Orders_Pickle = st.session_state['PB_Orders_Pickle'] 
        PB_queen_Archives_Pickle = st.session_state['PB_queen_Archives_Pickle']
        PB_QUEENsHeart_PICKLE = st.session_state['PB_QUEENsHeart_PICKLE']


        QUEEN_KING = ReadPickleData(pickle_file=PB_App_Pickle)    
        # def run_main_page():
        KING = KINGME()
        pollen_theme = pollen_themes(KING=KING)
        # QUEEN Databases
        QUEEN_KING = ReadPickleData(pickle_file=PB_App_Pickle)
        QUEEN_KING['source'] = PB_App_Pickle
        QUEEN = ReadPickleData(PB_QUEEN_Pickle)
        ORDERS = ReadPickleData(PB_Orders_Pickle)
        QUEENsHeart = ReadPickleData(PB_QUEENsHeart_PICKLE)


        if st.session_state['authorized_user']:
            APP_req = add_key_to_app(QUEEN_KING)
            QUEEN_KING = APP_req['QUEEN_KING']
            if APP_req['update']:
                PickleData(PB_App_Pickle, QUEEN_KING)


        if st.session_state['authorized_user'] == False and sneak_peak == False:
            cols = st.columns(2)
            with cols[0]:
                st.info("You Don't have a QueenTraderBot yet! Need authorization, Please contact pollenq.queen@gmail.com or click the button below to send a Request")
            with cols[1]:
                st.info("Below is a Preview")
            client_user_wants_a_queen = st.button("Yes I want a Queen!")
            if client_user_wants_a_queen:
                st.session_state['init_queen_request'] = True
                if 'init_queen_request' in st.session_state:
                    QUEEN_KING['init_queen_request'] = {'timestamp_est': datetime.datetime.now(est)}
                    PickleData(PB_App_Pickle, QUEEN_KING)
                    send_email(recipient=os.environ('pollenq_gmail'), subject="RequestingQueen", body=f'{st.session_state["username"]} Asking for a Queen')
                    st.success("Hive Master Notified and You should receive contact soon")



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


        def queen_QueenOrders():
            if admin == False:
                st.write("You Do Not Have Access")
                return False
            # Update run order
            all_orders = QUEEN['queen_orders']
            active_orders = all_orders[all_orders['queen_order_state'].isin(active_order_state_list)].copy()
            show_errors_option = st.selectbox('show last error', ['no', 'yes'], index=['no'].index('no'))
            c_order_input_list = st.multiselect("active client_order_id", active_orders['client_order_id'].to_list(), default=active_orders.iloc[-1]['client_order_id'])
            
            c_order_input = [c_order_input_list[0] if len(c_order_input_list) > 0 else all_orders.iloc[-1]['client_order_id'] ][0]

            # if show_errors_option == 'yes':
            if show_errors_option == 'yes':
                latest_queen_order = all_orders[all_orders['queen_order_state'] == 'error'].copy()
            else:                
                latest_queen_order = all_orders[all_orders['client_order_id'] == c_order_input].copy()

            
            df = latest_queen_order
            df = df.T.reset_index()
            df = df.astype(str)
            df = df.rename(columns={df.columns[1]: 'main'})
            
            grid_response = build_AGgrid_df(data=df, reload_data=False, update_cols=['update_column'], height=933)
            data = grid_response['data']
            # st.write(data)
            ttframe = data[data['index'] == 'ticker_time_frame'].copy()
            ttframe = ttframe.iloc[0]['main']
            # st.write(ttframe.iloc[0]['main'])
            selected = grid_response['selected_rows'] 
            df_sel = pd.DataFrame(selected)

            if len(df_sel) > 0:
                df_sel = df_sel.astype(str)
                st.write(df_sel)
                up_values = dict(zip(df_sel['index'], df_sel['update_column_update']))
                up_values = {k: v for (k,v) in up_values.items() if len(v) > 0}
                update_dict = {latest_queen_order.iloc[0]["client_order_id"]: up_values}
                st.session_state['update'] = update_dict
                st.session_state['ttframe_update'] = ttframe

            save_button_runorder = st.button("Save RunOrderUpdate")
            if save_button_runorder:
                # st.write(st.session_state['update'])
                update_sstate = st.session_state['update']
                update_ttframe = st.session_state['ttframe_update']
                order_dict = {'system': 'app',
                'queen_order_update_package': update_sstate,
                'app_requests_id' : f'{save_signals}{"_app-request_id_"}{return_timestamp_string()}{datetime.datetime.now().microsecond}',
                'ticker_time_frame': update_ttframe,
                }
                # st.write(order_dict)
                data = ReadPickleData(pickle_file=PB_App_Pickle)
                data['update_queen_order'].append(order_dict)
                PickleData(pickle_file=PB_App_Pickle, data_to_store=data)
                data = ReadPickleData(pickle_file=PB_App_Pickle)
                st.write(data['update_queen_order'])


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

        
        def return_total_profits(ORDERS):
            try:
                df = ORDERS['queen_orders']
                ORDERS = df[(df['queen_order_state']== 'completed') & (df['side'] == 'sell')].copy()
                return_dict = {}
                if len(ORDERS) > 0:
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

        
        def check_API__send_user_to_pollenq__with_message(api_failed, msg, errmsg=False):
            if api_failed:
                if errmsg:
                    st.error(errmsg)
                
                st.write("Taking you back to pollenq")
                time.sleep(5)

                st.session_state['QueenConscience_msg'] = msg
                switch_page("pollenq")
            
            return True

        
        def return_buying_power(api):
            with st.expander("Portfolio",  True):
                check_API__send_user_to_pollenq__with_message(api_failed, msg='You were not allowed there', errmsg="Your API Failed, Please Update in pollenq")

                ac_info = refresh_account_info(api=api)['info_converted']
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


        def stop_queenbee(QUEEN_KING):
            checkbox_val = st.sidebar.button("Stop Queen")
            if checkbox_val:
                QUEEN_KING['stop_queen'] = str(checkbox_val).lower()
                PickleData(pickle_file=PB_App_Pickle, data_to_store=QUEEN_KING)
                local_gif(gif_path=power_gif)
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

        
        def set_chess_pieces_symbols(QUEEN_KING):
            qcp_ticker_index = {}
            all_workers = list(QUEEN_KING['qcp_workerbees'].keys())
            view = []
            for qcp in all_workers:
                if qcp in ['castle', 'bishop', 'knight', 'castle_coin']:
                    view.append(f'{qcp} ({QUEEN_KING["qcp_workerbees"][qcp]["tickers"]} )')
                    for ticker in qcp:
                        qcp_ticker_index[ticker] = qcp
            
            return {'qcp_ticker_index': qcp_ticker_index, 'view': view, 'all_workers': all_workers}


        def update_Workerbees(QUEEN_KING, QUEEN, admin):
            
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


            #### SPEED THIS UP AND CHANGE TO DB CALL FOR ALLOWED ACTIVE TICKERS ###
            all_alpaca_tickers = api.list_assets()
            alpaca_symbols_dict = {}
            for n, v in enumerate(all_alpaca_tickers):
                if all_alpaca_tickers[n].status == 'active':
                    alpaca_symbols_dict[all_alpaca_tickers[n].symbol] = vars(all_alpaca_tickers[n])
            
            view = set_chess_pieces_symbols(QUEEN_KING=QUEEN_KING)['view']
            all_workers = set_chess_pieces_symbols(QUEEN_KING=QUEEN_KING)['all_workers']
            name = str(view).replace("[", "").replace("]", "").replace('"', "")

            with st.expander(f'WorkingBees Sybmols Chess Board: {name}', True):
                with st.form("Update WorkerBees"):

                    cols = st.columns((1,1,1))
                    with cols[0]:
                        st.image(pawn_png_url, width=23)
                        # st.markdown(f'<img src="{image}"', unsafe_allow_html=True)
                    #     image = "https://p7.hiclipart.com/preview/221/313/319/chess-piece-knight-rook-board-game-chess.jpg"
                    #     st.markdown(f'<img src="{image}" style="background-color:transparent">', unsafe_allow_html=True)
                    with cols[1]:
                        st.subheader("Chess Board")
                    cols = st.columns((1,10,3,2,2,2))
                    # all_workers = list(QUEEN_KING['qcp_workerbees'].keys())
                    for qcp in all_workers:
                        # if qcp == '':
                        #     # with cols[0]:
                        #     #     local_gif(gif_path=bitcoin_gif)
                        #     with cols[0]:
                        #         st.write(f'{qcp} {QUEEN_KING["qcp_workerbees"][qcp]["tickers"]}')
                        if qcp == 'castle_coin':
                            with cols[0]:
                                st.image("https://s3.us-east-2.amazonaws.com/nomics-api/static/images/currencies/BSV.png", width=54)
                                # local_gif(gif_path=bitcoin_gif)
                            with cols[1]:
                                QUEEN_KING['qcp_workerbees'][qcp]['tickers'] = st.multiselect(label=f'{qcp} symbols', options=list(alpaca_symbols_dict.keys()) + crypto_symbols__tickers_avail, default=QUEEN_KING['qcp_workerbees'][qcp]['tickers'], help='Castle Should Hold your Highest Valued Symbols')
                            with cols[2]:
                                st.selectbox(label='Model', key=f'{qcp}model', options=['MACD'])
                            with cols[3]:
                                QUEEN_KING['qcp_workerbees'][qcp]['MACD_fast_slow_smooth']['fast'] = st.number_input("fast", min_value=1, max_value=33, value=int(QUEEN_KING['qcp_workerbees'][qcp]['MACD_fast_slow_smooth']['fast']), key=f'{qcp}fast')
                            with cols[4]:
                                QUEEN_KING['qcp_workerbees'][qcp]['MACD_fast_slow_smooth']['slow'] = st.number_input("slow", min_value=1, max_value=33, value=int(QUEEN_KING['qcp_workerbees'][qcp]['MACD_fast_slow_smooth']['slow']), key=f'{qcp}slow')
                            with cols[5]:
                                QUEEN_KING['qcp_workerbees'][qcp]['MACD_fast_slow_smooth']['smooth'] = st.number_input("smooth", min_value=1, max_value=33, value=int(QUEEN_KING['qcp_workerbees'][qcp]['MACD_fast_slow_smooth']['smooth']), key=f'{qcp}smooth')
                        
                        if qcp == 'castle':
                            with cols[0]:
                                st.image(castle_png, width=54)
                            with cols[1]:
                                QUEEN_KING['qcp_workerbees'][qcp]['tickers'] = st.multiselect(label=f'{qcp} symbols', options=list(alpaca_symbols_dict.keys()) + crypto_symbols__tickers_avail, default=QUEEN_KING['qcp_workerbees'][qcp]['tickers'], help='Castle Should Hold your Highest Valued Symbols')
                            with cols[2]:
                                st.selectbox(label='Model', key=f'{qcp}model', options=['MACD'])
                            with cols[3]:
                                QUEEN_KING['qcp_workerbees'][qcp]['MACD_fast_slow_smooth']['fast'] = st.number_input("fast", min_value=1, max_value=33, value=int(QUEEN_KING['qcp_workerbees'][qcp]['MACD_fast_slow_smooth']['fast']), key=f'{qcp}fast')
                            with cols[4]:
                                QUEEN_KING['qcp_workerbees'][qcp]['MACD_fast_slow_smooth']['slow'] = st.number_input("slow", min_value=1, max_value=33, value=int(QUEEN_KING['qcp_workerbees'][qcp]['MACD_fast_slow_smooth']['slow']), key=f'{qcp}slow')
                            with cols[5]:
                                QUEEN_KING['qcp_workerbees'][qcp]['MACD_fast_slow_smooth']['smooth'] = st.number_input("smooth", min_value=1, max_value=33, value=int(QUEEN_KING['qcp_workerbees'][qcp]['MACD_fast_slow_smooth']['smooth']), key=f'{qcp}smooth')

                        if qcp == 'bishop':
                            with cols[0]:
                                st.image(bishop_png, width=74)
                            with cols[1]:
                                QUEEN_KING['qcp_workerbees'][qcp]['tickers'] = st.multiselect(label=f'{qcp} symbols', options=list(alpaca_symbols_dict.keys()) + crypto_symbols__tickers_avail, default=QUEEN_KING['qcp_workerbees'][qcp]['tickers'], help='Castle Should Hold your Highest Valued Symbols')
                            with cols[2]:
                                st.selectbox(label='Model', key=f'{qcp}model', options=['MACD'])
                            with cols[3]:
                                QUEEN_KING['qcp_workerbees'][qcp]['MACD_fast_slow_smooth']['fast'] = st.number_input("fast", min_value=1, max_value=33, value=int(QUEEN_KING['qcp_workerbees'][qcp]['MACD_fast_slow_smooth']['fast']), key=f'{qcp}fast')
                            with cols[4]:
                                QUEEN_KING['qcp_workerbees'][qcp]['MACD_fast_slow_smooth']['slow'] = st.number_input("slow", min_value=1, max_value=33, value=int(QUEEN_KING['qcp_workerbees'][qcp]['MACD_fast_slow_smooth']['slow']), key=f'{qcp}slow')
                            with cols[5]:
                                QUEEN_KING['qcp_workerbees'][qcp]['MACD_fast_slow_smooth']['smooth'] = st.number_input("smooth", min_value=1, max_value=33, value=int(QUEEN_KING['qcp_workerbees'][qcp]['MACD_fast_slow_smooth']['smooth']), key=f'{qcp}smooth')

                        if qcp == 'knight':
                            with cols[0]:
                                st.image(knight_png, width=74)
                            with cols[1]:
                                QUEEN_KING['qcp_workerbees'][qcp]['tickers'] = st.multiselect(label=f'{qcp} symbols', options=list(alpaca_symbols_dict.keys()) + crypto_symbols__tickers_avail, default=QUEEN_KING['qcp_workerbees'][qcp]['tickers'], help='Castle Should Hold your Highest Valued Symbols')
                            with cols[2]:
                                st.selectbox(label='Model', key=f'{qcp}model', options=['MACD'])
                            with cols[3]:
                                QUEEN_KING['qcp_workerbees'][qcp]['MACD_fast_slow_smooth']['fast'] = st.number_input("fast", min_value=1, max_value=33, value=int(QUEEN_KING['qcp_workerbees'][qcp]['MACD_fast_slow_smooth']['fast']), key=f'{qcp}fast')
                            with cols[4]:
                                QUEEN_KING['qcp_workerbees'][qcp]['MACD_fast_slow_smooth']['slow'] = st.number_input("slow", min_value=1, max_value=33, value=int(QUEEN_KING['qcp_workerbees'][qcp]['MACD_fast_slow_smooth']['slow']), key=f'{qcp}slow')
                            with cols[5]:
                                QUEEN_KING['qcp_workerbees'][qcp]['MACD_fast_slow_smooth']['smooth'] = st.number_input("smooth", min_value=1, max_value=33, value=int(QUEEN_KING['qcp_workerbees'][qcp]['MACD_fast_slow_smooth']['smooth']), key=f'{qcp}smooth')
                
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
            

        def update_QueenControls(QUEEN_KING, control_option, theme_list):
            theme_desc = {'nuetral': ' follows basic model wave patterns',
                        'strong_risk': ' defaults to high power trades',
                        'star__storywave': ' follows symbols each day changes and adjusts order rules based on latest data'}
            
            if control_option.lower() == 'theme':
                with st.form("Update Control"):
                    cols = st.columns((1,3))
                    with cols[0]:
                        st.info("Set your Risk Theme")
                    with cols[0]:
                        theme_option = st.selectbox(label='set theme', options=theme_list, index=theme_list.index('nuetral'))
                    with cols[1]:
                        # st.warning(f'Theme: {theme_option}')
                        ep = st.empty()
                    with cols[1]:
                        st.warning(f'Theme: {theme_option}{theme_desc[theme_option]}')

                    save_button = st.form_submit_button("Save")
                    if save_button:
                        QUEEN_KING['theme'] = theme_option
                        QUEEN_KING['last_app_update'] = datetime.datetime.now()
                        PickleData(pickle_file=PB_App_Pickle, data_to_store=QUEEN_KING)
                        return_image_upon_save(title="Theme saved")
                return True

            elif control_option.lower() == 'symbols_stars_tradingmodel':
                # add: ticker_family, short position and macd/hist story 
                # queen__write_active_symbols(QUEEN_KING=QUEEN_KING)
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
                    tickers_avail = list(QUEEN_KING['king_controls_queen'][control_option].keys())
                    ticker_option_qc = st.selectbox("Symbol", tickers_avail, index=tickers_avail.index(["SPY" if "SPY" in tickers_avail else tickers_avail[0]][0]))

                    # QUEEN_KING = add_trading_model(PB_APP_Pickle=PB_App_Pickle, QUEEN_KING=QUEEN_KING, ticker=ticker_option_qc)
                

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
                'take_profit': 'number',
                'sellout': 'number',
                # 'status': 'checkbox',
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

                    # trigbee_update = trading_model__star['trigbees'][trigbee_sel]
                    king_order_rules_update = trading_model__star['trigbees'][trigbee_sel][wave_blocks_option]
                    # # st.write('tic level', QUEEN['queen_controls'][control_option][ticker_option_qc].keys())
                    st.subheader("Settings")
                    with st.expander(f'{ticker_option_qc} Global Settings'):
                        cols = st.columns((1,1,1,1,1))
                        
                        # all ticker settings
                        for kor_option, kor_v in trading_model.items():
                            if kor_option in ticker_model_level_1.keys():
                                item_type = ticker_model_level_1[kor_option]['type']
                                # st.write(kor_option, kor_v, item_type)
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

                    with st.expander(f'{star_option_qc}'):
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
                            
                    with st.expander(f'{wave_blocks_option}'):
                        # mark_down_text(text=f'{trigbee_sel}{" >>> "}{wave_blocks_option}')
                        # st.write(f'{wave_blocks_option} >>> WaveBlocktime KingOrderRules 4')
                        cols = st.columns((1, 1, 2, 3))

                        for kor_option, kor_v in king_order_rules_update.items():
                            if kor_option in kor_option_mapping.keys():
                                st_func = kor_option_mapping[kor_option]
                                if kor_option == 'take_profit_in_vwap_deviation_range':
                                    # with cols[0]:
                                    #     st.write("vwap_deviation_range")
                                    with cols[0]:
                                        low = st.number_input(label=f'{"vwap_deviation_low"}', value=kor_v['low_range'], key=f'{trigbee_sel}{"_"}{wave_blocks_option}{"_"}{"low_range"}', help="take_profit_in_vwap_deviation_range")
                                    with cols[1]:
                                        high = st.number_input(label=f'{"vwap_deviation_high"}', value=kor_v['high_range'], key=f'{trigbee_sel}{"_"}{wave_blocks_option}{"_"}{"high_range"}')
                                        
                                    king_order_rules_update[kor_option] = {'high_range': high, "low_range": low}
                                
                                if kor_option == 'ignore_trigbee_in_vwap_range':
                                    # with cols[0]:
                                    #     st.write("ignore_trigbee_in_vwap_range")
                                    with cols[0]:
                                        low = st.number_input(label=f'{"ignore_vwap_low"}', value=kor_v['low_range'], key=f'{trigbee_sel}{"_"}{wave_blocks_option}{"_"}{"vwap_low_range"}')
                                    with cols[1]:
                                        high = st.number_input(label=f'{"ignore_vwap_high"}', value=kor_v['high_range'], key=f'{trigbee_sel}{"_"}{wave_blocks_option}{"_"}{"vwap_high_range"}')
                                    king_order_rules_update[kor_option] = {'high_range': high, "low_range": low}

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

                    
                    #### TRADING MODEL ####
                    # Ticker Level 1
                    # Star Level 2
                    # trading_model = trading_model
                    
                    # Trigbees Level 3
                    # trading_model['stars_kings_order_rules'][star_option_qc]['trigbees'][trigbee_sel].update(trigbee_update)
                    # trading_model = trading_model
                    
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
                        refresh_to_theme = st.form_submit_button("Refresh Model To Current Theme")           

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
                        QUEEN_KING = refresh_tickers_TradingModels(QUEEN_KING=QUEEN_KING, ticker=ticker_option_qc)
                        PickleData(pickle_file=PB_App_Pickle, data_to_store=QUEEN_KING)
                        return_image_upon_save(title=f'Model Refreshed to Theme: {QUEEN_KING["theme"]}')



                if st.button('show queens trading model'):
                    st.write(QUEEN_KING['king_controls_queen'][control_option][ticker_option_qc])
            else:
                st.write("PENDING WORK")
            

            return True 


        def queen_order_update(latest_queen_order, c_order_input):
            with st.form("my_form"):
                df = pd.DataFrame(latest_queen_order)
                df = df.T.reset_index()
                df = df.astype(str)
                # for col in df.columns:
                #     df[col] = df[col].astype(str)
                df = df.rename(columns={0: 'main'})
                grid_response = build_AGgrid_df(data=df, reload_data=False, update_cols=['update_column'])
                data = grid_response['data']
                # st.write(data)
                ttframe = data[data['index'] == 'ticker_time_frame'].copy()
                ttframe = ttframe.iloc[0]['main']
                # st.write(ttframe.iloc[0]['main'])
                selected = grid_response['selected_rows'] 
                df_sel = pd.DataFrame(selected)
                st.write(df_sel)
                if len(df_sel) > 0:
                    up_values = dict(zip(df_sel['index'], df_sel['update_column_update']))
                    up_values = {k: v for (k,v) in up_values.items() if len(v) > 0}
                    update_dict = {c_order_input: up_values}
                    st.session_state['update'] = update_dict
                    st.session_state['ttframe_update'] = ttframe

                save_button_runorder = st.button("Save RunOrderUpdate")
                if save_button_runorder:
                    # st.write(st.session_state['update'])
                    update_sstate = st.session_state['update']
                    update_ttframe = st.session_state['ttframe_update']
                    order_dict = {'system': 'app',
                    'queen_order_update_package': update_sstate,
                    'app_requests_id' : f'{save_signals}{"_app-request_id_"}{return_timestamp_string()}{datetime.datetime.now().microsecond}',
                    'ticker_time_frame': update_ttframe,
                    }
                    # st.write(order_dict)
                    data = ReadPickleData(pickle_file=PB_App_Pickle)
                    data['update_queen_order'].append(order_dict)
                    PickleData(pickle_file=PB_App_Pickle, data_to_store=data)
                    data = ReadPickleData(pickle_file=PB_App_Pickle)
                    st.write(data['update_queen_order'])


        def create_AppRequest_package(request_name, archive_bucket=None):
            return {
            'app_requests_id': f'{request_name}{"_app-request_id_"}{return_timestamp_string()}{datetime.datetime.now().microsecond}', 
            'request_name': request_name,
            'archive_bucket': archive_bucket,
            'request_timestamp': datetime.datetime.now().astimezone(est),
            }


        def build_AGgrid_df(data, reload_data=False, fit_columns_on_grid_load=True, height=750, update_cols=['Update'], update_mode_value='MANUAL', paginationOn=True, dropdownlst=False, allow_unsafe_jscode=True):
            gb = GridOptionsBuilder.from_dataframe(data, min_column_width=30)
            if paginationOn:
                gb.configure_pagination(paginationAutoPageSize=True) #Add pagination
            gb.configure_side_bar() #Add a sidebar
            gb.configure_selection('multiple', use_checkbox=True, groupSelectsChildren="Group checkbox select children") #Enable multi-row selection
            if update_cols:
                for colName in update_cols:        
                    if dropdownlst:
                        gb.configure_column(f'{colName}{"_update"}', editable=True, cellEditor='agSelectCellEditor', cellEditorParams={'values': dropdownlst })
                    else:
                        gb.configure_column(f'{colName}{"_update"}', header_name=colName, editable=True, groupable=True)

            
            gridOptions = gb.build()

            gridOptions['wrapHeaderText'] = 'true'
            gridOptions['autoHeaderHeight'] = 'true'
            gridOptions['rememberGroupStateWhenNewData'] = 'true'
            gridOptions['enableCellTextSelection'] = 'true'

            grid_response = AgGrid(
                data,
                gridOptions=gridOptions,
                data_return_mode='AS_INPUT', 
                update_mode=update_mode_value, 
                fit_columns_on_grid_load=fit_columns_on_grid_load,
                # theme='blue', #Add theme color to the table
                enable_enterprise_modules=True,
                height=height, 
                # width='100%',
                reload_data=reload_data,
                allow_unsafe_jscode=allow_unsafe_jscode
            )
            return grid_response


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
                    st.write("Verison Missing DB", req_bucket)
                    continue
                for app_req in QUEEN_KING[req_bucket]:
                    if app_req['app_requests_id'] in QUEEN['app_requests__bucket']:
                        print("Quen Processed app req item")
                        archive_bucket = f'{req_bucket}{"_requests"}'
                        QUEEN_KING[req_bucket].remove(app_req)
                        QUEEN_KING[archive_bucket].append(app_req)
                        save = True
            if save:
                PickleData(pickle_file=PB_App_Pickle, data_to_store=QUEEN_KING)


        def queens_subconscious_Thoughts(QUEEN, expand_=False):
            write_sub = []
            for key, bucket in QUEEN['subconscious'].items():
                if len(bucket) > 0:
                    write_sub.append(bucket)
            if expand_ == False:
                expand_ = expand_
            else:
                expand_ = True if len(write_sub) > 0 else False
            
            if len(write_sub) > 0:
                with st.expander('subconscious alert thoughts', expand_):
                    st.write(write_sub)


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
            
            users_allowed_queen_email, users_allowed_queen_emailname, users_allowed_queen_emailname__db = kingdom__grace_to_find_a_Queen()
            now = datetime.datetime.now(est)

            if dag =='run_queenbee':
                if 'trigger_queen' in QUEEN_KING.keys():
                    if (now - QUEEN_KING['trigger_queen'].get('last_trig_date')).total_seconds() < 60:
                        st.write("Waking up your Queen She is a bit lazy today...it may take her up to 60 Seconds to get out of bed")
                        st.image(QUEEN_KING['character_image'], width=100)
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
                                sys.exit()
                            # execute trigger
                            trigger_airflow_dag(dag=dag, client_username=st.session_state['username'], prod=prod)
                            QUEEN_KING['trigger_queen'].update(trigger_queen_vars(dag=dag, client_username=st.session_state['username']))
                            st.write("My Queen")
                            st.image(QUEEN_KING['character_image'], width=100)  ## have this be the client_user character
                            PickleData(pickle_file=PB_App_Pickle, data_to_store=QUEEN_KING)
                            switch_page("QueensConscience")
                    
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

    
        def queen_chart(POLLENSTORY):
            # Main CHART Creation
            with st.expander('chart', expanded=True):
                req = ticker_time_frame__option(tickers_avail_op=tickers_avail_op, req_key='charts')
                tickers = req['tickers']
                ticker_option = req['ticker_option']
                frame_option = req['frame_option']
                ticker_time_frame = f'{ticker_option}{"_"}{frame_option}'
                df = POLLENSTORY[ticker_time_frame].copy()

                st.markdown('<div style="text-align: center;">{}</div>'.format(ticker_option), unsafe_allow_html=True)

                # star__view = its_morphin_time_view(QUEEN=QUEEN, STORY_bee=STORY_bee, ticker=ticker_option, POLLENSTORY=POLLENSTORY)
                
                day_only_option = st.checkbox("Only Today")
                
                if day_only_option:
                    df_day = df['timestamp_est'].iloc[-1]
                    df['date'] = df['timestamp_est'] # test

                    df_today = df[df['timestamp_est'] > (datetime.datetime.now().replace(hour=1, minute=1, second=1)).astimezone(est)].copy()
                    df_prior = df[~(df['timestamp_est'].isin(df_today['timestamp_est'].to_list()))].copy()

                    df = df_today
                fig = create_main_macd_chart(df)
                st.plotly_chart(fig)

                return True

        
        def add_trading_model(PB_APP_Pickle, QUEEN_KING, ticker, model='MACD', status='active', workerbee=False):
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
        
        
        def queen__write_active_symbols(QUEEN_KING):

            active_ticker_models = [{i: v['status']} for i, v in QUEEN_KING['king_controls_queen']['symbols_stars_TradingModel'].items() if v['status'] == 'active']
            chunk_write_dictitems_in_row(active_ticker_models)

            return True


        def show_waves(ticker_storys, ticker_option, frame_option):
            ttframe = f'{ticker_option}{"_"}{frame_option}'
            knowledge = ticker_storys[ttframe]

            mark_down_text(text=ttframe)
            st.write("waves story -- investigate BACKEND functions")
            df = knowledge['waves']['story']
            df = df.astype(str)
            st.dataframe(df)

            st.write("buy cross waves")
            m_sort = knowledge['waves']['buy_cross-0']
            df_m_sort = pd.DataFrame(m_sort).T
            df_m_sort = df_m_sort.astype(str)
            st.dataframe(data=df_m_sort)

            st.write("sell cross waves")
            m_sort = knowledge['waves']['sell_cross-0']
            df_m_sort = pd.DataFrame(m_sort).T
            df_m_sort = df_m_sort.astype(str)
            st.dataframe(data=df_m_sort)

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


        # """ if "__name__" == "__main__": """
        if st.session_state['admin']:
            with st.expander("ozz"):
                query = st.text_input('ozz call')
                if st.button("ozz"):
                    send_ozz_call(query=query)
        
        prod_keys_confirmed = QUEEN_KING['users_secrets']['prod_keys_confirmed']
        sandbox_keys_confirmed = QUEEN_KING['users_secrets']['sandbox_keys_confirmed']

        if st.session_state['authorized_user']:
            clean_out_app_requests(QUEEN=QUEEN, QUEEN_KING=QUEEN_KING, request_buckets=['subconscious'])
        
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

        # use API keys from user
        queenbee_online(QUEENsHeart=QUEENsHeart, admin=admin, dag='run_queenbee', api_failed=api_failed)
        queenbee_online(QUEENsHeart=QUEENsHeart, admin=admin, dag='run_workerbees', api_failed=api_failed)
        queenbee_online(QUEENsHeart=QUEENsHeart, admin=admin, dag='run_workerbees_crypto', api_failed=api_failed)

        portfolio = return_alpc_portolio(api)['portfolio']
        acct_info = refresh_account_info(api=api)

        # # if authorized_user: log type auth and none
        log_dir = os.path.join(db_root, 'logs')
        init_logging(queens_chess_piece=queens_chess_piece, db_root=db_root, prod=st.session_state['production'])

        # db global
        coin_exchange = "CBSE"

        ticker_db = return_QUEENs__symbols_data(QUEEN=QUEEN)
        POLLENSTORY = ticker_db['pollenstory']
        STORY_bee = ticker_db['STORY_bee']
        # Ticker DataBase
        tickers_avail = [set(i.split("_")[0] for i in STORY_bee.keys())][0]
        tickers_avail = tickers_avail if len(tickers_avail) > 0 else 'SPY'

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
        # with cols[2]:
        bee_keeper = st.sidebar.button("Refresh", key='gatekeeper')



    def rename_trigbee_name(tribee_name):
        return tribee_name


    def ticker_time_frame_UI_rename(ticker_time_frame):
        new_ttf = ticker_time_frame
        # group tickers . i.e. if apart of index = index is a character
        stars = stars() # 1Minute_1Day
        rename = {'ticker': {}, 'time': {}, 'stars': {}}
        return new_ttf


    def ticker_time_frame__option(tickers_avail_op, req_key):
        cols = st.columns(2)
        with cols[0]:
            if 'sel_tickers' not in st.session_state:
                st.session_state['sel_tickers'] = tickers_avail_op[0]

            tickers = st.multiselect('Symbols', options=list(tickers_avail_op), default=st.session_state['sel_tickers'], help='View Groups of symbols to Inspect where to send the Bees', key=f'ticker{req_key}')
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



    today_day = datetime.datetime.now(est).day
    current_radio_sel = str(option).lower()
    if str(option).lower() == 'queen':
        
        with st.spinner("Waking Up the Hive"):

                        
            # page_line_seperator('1', color=default_yellow_color)
            if st.session_state['authorized_user'] == True:
                # keys
                # add new trading models if needed
                for workerbee, bees_data in QUEEN_KING['qcp_workerbees'].items():
                    for ticker in bees_data['tickers']:
                        QUEEN_KING = add_trading_model(PB_APP_Pickle=PB_App_Pickle, QUEEN_KING=QUEEN_KING, ticker=ticker, workerbee=workerbee)

            tickers_avail_op = list(tickers_avail)

            # page_line_seperator(height='1')
            cols = st.columns(2)

            # cols = st.columns((1,1))

            queen_tabs = ["Orders", "Chess Board", "Portfolio", "Wave Stories", "Trading Models", "Charts"]
            order_tab, chessboard_tab, Portfolio, wave_stories_tab, trading_models_tab, charts_tab = st.tabs(queen_tabs)

            # with cols[1]:
            return_total_profits(ORDERS=ORDERS)
            # with cols[0]:
            queens_subconscious_Thoughts(QUEEN=QUEEN)

            with Portfolio:
                return_buying_power(api=api)  # sidebar

            with chessboard_tab:
                update_Workerbees(QUEEN_KING=QUEEN_KING, QUEEN=QUEEN, admin=admin)
            
            with wave_stories_tab:
                queen_wavestories(QUEEN=QUEEN)
            
            with order_tab:
                queen_order_flow(ORDERS=ORDERS, active_order_state_list=active_order_state_list)
                queen_beeAction_theflash(False)
                queen_triggerbees()
            
            with charts_tab:
                # queen_chart(POLLENSTORY=POLLENSTORY)
                advanced_charts(tickers_avail=tickers_avail_op, POLLENSTORY=POLLENSTORY)

            with trading_models_tab:
                queen__write_active_symbols(QUEEN_KING=QUEEN_KING)
                st.header("Select Control")
                theme_list = list(pollen_theme.keys())
                contorls = list(QUEEN['queen_controls'].keys())
                control_option = st.selectbox('control', contorls, index=contorls.index('theme'))
                update_QueenControls(QUEEN_KING=QUEEN_KING, control_option=control_option, theme_list=theme_list)


            page_line_seperator(color=default_yellow_color)

    if str(option).lower() == 'controls':

        cols = st.columns((1,3))
        if authorized_user == False:
            st.write("permission denied")
            st.stop()
        else:
            
            stop_queenbee(QUEEN_KING=QUEEN_KING)
            refresh_queenbee_controls(QUEEN_KING=QUEEN_KING)
            
            # page_line_seperator()

            # st.header("Select Control")
            # theme_list = list(pollen_theme.keys())
            # contorls = list(QUEEN['queen_controls'].keys())
            # control_option = st.selectbox('control', contorls, index=contorls.index('theme'))
            # update_QueenControls(QUEEN_KING=QUEEN_KING, control_option=control_option, theme_list=theme_list)

            clear_subconscious_Thought(QUEEN=QUEEN, QUEEN_KING=QUEEN_KING)

            with st.expander('Heartbeat'):
                st.write(QUEEN['heartbeat'])


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
    ##### END ####
if __name__ == '__main__':
    queens_conscience()