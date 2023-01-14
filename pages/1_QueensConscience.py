
import pandas as pd
# import logging
import os
import pandas as pd
import numpy as np
import datetime
import pytz
# from typing import Callable
import random
from tqdm import tqdm
from collections import defaultdict
import ipdb
import matplotlib.pyplot as plt
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from itertools import islice
from PIL import Image
from dotenv import load_dotenv
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode, JsCode
from streamlit_extras.stoggle import stoggle
from streamlit_extras.switch_page_button import switch_page
import time
import _locale
import os
# from random import randint
import sqlite3
import streamlit as st
from appHive import init_client_user_secrets, live_sandbox__setup_switch, progress_bar, queen_order_flow, grid_height, mark_down_text, click_button_grid, nested_grid, mark_down_text, page_line_seperator, write_flying_bee, hexagon_gif, local_gif, flying_bee_gif, pollen__story
from app_auth import signin_main
import base64
import time
# from streamlit_extras.stoggle import stoggle
from King import hive_master_root, streamlit_config_colors, local__filepaths_misc
from QueenBeeDagger import run__trigger_dag

est = pytz.timezone("US/Eastern")

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
# purple_heartbeat_gif = MISC['purple_heartbeat_gif'] MISC.get('puprple')

# moving_ticker_gif = MISC['moving_ticker_gif']
# heart_bee_gif = MISC['heart_bee_gif']

learningwalk_bee = Image.open(learningwalk_bee)
page_icon = Image.open(bee_image)

##### STREAMLIT ###
k_colors = streamlit_config_colors()
default_text_color = k_colors['default_text_color'] # = '#59490A'
default_font = k_colors['default_font'] # = "sans serif"
default_yellow_color = k_colors['default_yellow_color'] # = '#C5B743'

if 'sidebar_hide' in st.session_state:
    sidebar_hide = 'collapsed'
else:
    sidebar_hide = 'expanded'

st.set_page_config(
     page_title="pollenq",
     page_icon=page_icon,
     layout="wide",
     initial_sidebar_state=sidebar_hide,
    #  menu_items={
    #      'Get Help': 'https://www.extremelycoolapp.com/help',
    #      'Report a bug': "https://www.extremelycoolapp.com/bug",
    #      'About': "# This is a header. This is an *extremely* cool app!"
    #  }
 )

# local_gif(gif_path=purple_heartbeat_gif, height='33', width='1000')

def set_prod_env(prod):
    st.session_state['production'] = prod
    st.sidebar.image(chess_piece_queen, width=23)

# if st.button("sw"):
#     switch_page("QueensConscience#no-ones-flying")

## anchors
# st.header("Section 1")
# st.markdown("[Section 1](#section-1)")

# if st.button("Go to page 1", url_param='playground'):
#     pass

with st.spinner("Buzz Buzz Where is my Honey"):
    # st.write( st.session_state['username'], st.session_state['authorized_user'])

    if 'username' not in st.session_state:
        signin_main()
    
    # return page last visited 
    
    if 'sneak_peak' in st.session_state and st.session_state['sneak_peak'] == True:
        sneak_peak = True
        st.session_state['production'] = True
        st.session_state['username'] = 'stefanstapinski@gmail.com'
        st.session_state['authorized_user'] = False
        st.session_state['db_root'] = os.path.join(main_root, 'db')
        st.info("Welcome and Watch A QueenBot in Action")
    
    elif st.session_state['authentication_status'] != True:
        st.write(st.session_state['authentication_status'])
        sneak_peak = False
        st.error("You Need to Log In to pollenq")
        switch_page("pollenq")
        st.stop()
    

    # if st.session_state['authentication_status']
    db_root = st.session_state['db_root']
    # st.write(st.session_state['db_root'])

    st.sidebar.write(f'Welcome {st.session_state["name"]}')
    client_user = st.session_state['username']
    authorized_user = st.session_state['authorized_user']
    db_client_user_name = st.session_state['username'].split("@")[0]

    prod, admin, prod_name = live_sandbox__setup_switch()
    
    if st.session_state['production']:
        from QueenHive import return_alpaca_user_apiKeys, test_api_keys, return_queen_controls, return_STORYbee_trigbees, return_alpaca_api_keys, add_key_to_app, read_pollenstory, init_clientUser_dbroot, init_pollen_dbs, refresh_account_info, generate_TradingModel, stars, analyze_waves, KINGME, queen_orders_view, story_view, return_alpc_portolio, return_dfshaped_orders, ReadPickleData, pollen_themes, PickleData, return_timestamp_string, return_api_keys, read_queensmind, split_today_vs_prior, init_logging
        load_dotenv(os.path.join(os.getcwd(), '.env_jq'))
    else:
        from QueenHive_sandbox import return_alpaca_user_apiKeys, test_api_keys, return_queen_controls, return_STORYbee_trigbees, return_alpaca_api_keys, add_key_to_app, read_pollenstory, init_clientUser_dbroot, init_pollen_dbs, refresh_account_info, generate_TradingModel, stars, analyze_waves, KINGME, queen_orders_view, story_view, return_alpc_portolio, return_dfshaped_orders, ReadPickleData, pollen_themes, PickleData, return_timestamp_string, return_api_keys, read_queensmind, split_today_vs_prior, init_logging
        load_dotenv(os.path.join(os.getcwd(), '.env'))


    init_pollen = init_pollen_dbs(db_root=db_root, prod=st.session_state['production'], queens_chess_piece='queen')
    PB_QUEEN_Pickle = init_pollen['PB_QUEEN_Pickle']
    PB_App_Pickle = init_pollen['PB_App_Pickle']
    PB_Orders_Pickle = init_pollen['PB_Orders_Pickle']

    QUEEN_KING = ReadPickleData(pickle_file=PB_App_Pickle)    
    # def run_main_page():
    KING = KINGME()
    pollen_theme = pollen_themes(KING=KING)
    # QUEEN Databases
    QUEEN_KING = ReadPickleData(pickle_file=PB_App_Pickle)
    QUEEN_KING['source'] = PB_App_Pickle
    QUEEN = ReadPickleData(PB_QUEEN_Pickle)
    ORDERS = ReadPickleData(PB_Orders_Pickle)
    # st.write("using ", PB_App_Pickle)
    if st.session_state['authorized_user']:
        APP_req = add_key_to_app(QUEEN_KING)
        QUEEN_KING = APP_req['QUEEN_KING']
        if APP_req['update']:
            PickleData(PB_App_Pickle, QUEEN_KING)


    def grid_height(len_of_rows):
        if len_of_rows > 10:
            grid_height = 333
        else:
            grid_height = round(len_of_rows * 33, 0)
        
        return grid_height

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
            list_of_dicts_ = [{k:v} for (k,v) in list_of_dicts.items()]

            chunk_write_dictitems_in_row(chunk_list=list_of_dicts_, title="Active Bees", write_type="info")
            # g = {write_flying_bee() for i in range(len(df))}
        else:
            st.subheader("No ones flying")
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

    def create_guage_chart(title, value=.01):

        fig = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = value,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': title, 'font': {'size': 25}},
            delta = {'reference':.4 , 'increasing': {'color': "RebeccaPurple"}},
            gauge = {
                'axis': {'range': [1, -1], 'tickwidth': 1, 'tickcolor': "darkblue"},
                'bar': {'color': '#ffe680'},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "gray",
                'steps': [
                    {'range': [-1, -.5], 'color': 'red'},
                    {'range': [1, .6], 'color': 'royalblue'}],
                'threshold': {
                    'line': {'color': "red", 'width': 3},
                    'thickness': 0.60,
                    'value': 1}}))

        # fig.update_layout(paper_bgcolor = "lavender", font = {'color': "darkblue", 'family': "Arial"})
        fig.update_layout(height=289, width=350)

        return fig

    def create_todays_profit_header_information():
        fig = go.Figure()

        fig.add_trace(go.Indicator(
            mode = "number+delta",
            value = 200,
            domain = {'x': [0, 0.5], 'y': [0, 0.5]},
            delta = {'reference': 400, 'relative': True, 'position' : "top"}))

        # fig.add_trace(go.Indicator(
        #     mode = "number+delta",
        #     value = 350,
        #     delta = {'reference': 400, 'relative': True},
        #     domain = {'x': [0, 0.5], 'y': [0.5, 1]}))

        # fig.add_trace(go.Indicator(
        #     mode = "number+delta",
        #     value = 450,
        #     title = {"text": "Accounts<br><span style='font-size:0.8em;color:gray'>Subtitle</span><br><span style='font-size:0.8em;color:gray'>Subsubtitle</span>"},
        #     delta = {'reference': 400, 'relative': True},
        #     domain = {'x': [0.6, 1], 'y': [0, 1]}))

        # fig.show()
        fig.update_layout(height=300, width=333)
        st.plotly_chart(fig)
    
    def create_main_macd_chart(df):
        title = df.iloc[-1]['name']
        # st.markdown('<div style="text-align: center;">{}</div>'.format(title), unsafe_allow_html=True)
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.1999, row_heights=[0.7, 0.3])
        # df.set_index('timestamp_est')
        # df['chartdate'] = f'{df["chartdate"].day}{df["chartdate"].hour}{df["chartdate"].minute}'
        df=df.copy()
        df['chartdate'] = df['chartdate'].apply(lambda x: f'{x.month}{"-"}{x.day}{"_"}{x.hour}{":"}{x.minute}')
        fig.add_ohlc(x=df['chartdate'], close=df['close'], open=df['open'], low=df['low'], high=df['high'], name='price')
        # fig.add_scatter(x=df['chartdate'], y=df['close'], mode="lines", row=1, col=1)
        # if '1Minute_1Day' in df.iloc[0]['name']:
        fig.add_scatter(x=df['chartdate'], y=df['vwap'], mode="lines", row=1, col=1, name='vwap')

        fig.add_scatter(x=df['chartdate'], y=df['macd'], mode="lines", row=2, col=1, name='mac')
        fig.add_scatter(x=df['chartdate'], y=df['signal'], mode="lines", row=2, col=1, name='signal')
        fig.add_bar(x=df['chartdate'], y=df['hist'], row=2, col=1, name='hist')
        fig.update_layout(title_text=title)
        df['cross'] = np.where(df['macd_cross'].str.contains('cross'), df['macd'], 0)
        fig.add_scatter(x=df['chartdate'], y=df['cross'], mode='lines', row=2, col=1, name='cross',) # line_color='#00CC96')
        # fig.add_scatter(x=df['chartdate'], y=df['cross'], mode='markers', row=1, col=1, name='cross',) # line_color='#00CC96')
        fig.update_xaxes(showgrid=False)
        fig.update_yaxes(showgrid=False)
        # fig.update_layout(sliders=False)
        return fig


    def create_slope_chart(df):
        title = df.iloc[-1]['name']
        # st.markdown('<div style="text-align: center;">{}</div>'.format(title), unsafe_allow_html=True)
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.01)
        # df.set_index('timestamp_est')
        # df['chartdate'] = f'{df["chartdate"].day}{df["chartdate"].hour}{df["chartdate"].minute}'
        df = df.copy()
        df['chartdate'] = df['chartdate'].apply(lambda x: f'{x.month}{"-"}{x.day}{"_"}{x.hour}{":"}{x.minute}')
        slope_cols = [i for i in df.columns if 'slope' in i]
        for col in slope_cols:
            df[col] = pd.to_numeric(df[col])
            df[col] = np.where(abs(df[col])>5, 0, df[col])
        fig.add_scatter(x=df['chartdate'], y=df['hist_slope-3'], mode="lines", row=1, col=1, name='hist_slope-3')
        fig.add_scatter(x=df['chartdate'], y=df['hist_slope-6'], mode="lines", row=1, col=1, name='hist_slope-6')
        # fig.add_scatter(x=df['chartdate'], y=df['hist_slope-23'], mode="lines", row=1, col=1, name='hist_slope-23')
        fig.add_scatter(x=df['chartdate'], y=df['macd_slope-3'], mode="lines", row=2, col=1, name='macd_slope-3')
        fig.add_scatter(x=df['chartdate'], y=df['macd_slope-6'], mode="lines", row=2, col=1, name='macd_slope-6')
        # fig.add_scatter(x=df['chartdate'], y=df['macd_slope-23'], mode="lines", row=2, col=1, name='macd_slope-23')
        fig.update_layout(height=600, width=900, title_text=title)
        return fig


    def create_wave_chart(df):
        title = f'buy+sell cross __waves {df.iloc[-1]["name"]}'
        # st.markdown('<div style="text-align: center;">{}</div>'.format(title), unsafe_allow_html=True)
        fig = make_subplots(rows=1, cols=1, shared_xaxes=True, vertical_spacing=0.01)
        # df.set_index('timestamp_est')
        # df['chartdate'] = f'{df["chartdate"].day}{df["chartdate"].hour}{df["chartdate"].minute}'
        df = df.copy()
        df['chartdate'] = df['chartdate'].apply(lambda x: f'{x.month}{"-"}{x.day}{"_"}{x.hour}{":"}{x.minute}')

        fig.add_bar(x=df['chartdate'], y=df['buy_cross-0__wave'],  row=1, col=1, name='buycross wave')
        fig.add_bar(x=df['chartdate'], y=df['sell_cross-0__wave'],  row=1, col=1, name='sellcross wave')
        fig.update_layout(height=600, width=900, title_text=title)
        return fig


    def create_wave_chart_single(df, wave_col):
        title = df.iloc[-1]['name']
        # st.markdown('<div style="text-align: center;">{}</div>'.format(title), unsafe_allow_html=True)
        fig = make_subplots(rows=1, cols=1, shared_xaxes=True, vertical_spacing=0.01)
        # df.set_index('timestamp_est')
        # df['chartdate'] = f'{df["chartdate"].day}{df["chartdate"].hour}{df["chartdate"].minute}'
        df = df.copy()
        df['chartdate'] = df['chartdate'].apply(lambda x: f'{x.month}{"-"}{x.day}{"_"}{x.hour}{":"}{x.minute}')

        fig.add_bar(x=df['chartdate'], y=df[wave_col],  row=1, col=1, name=wave_col)
        fig.update_layout(height=600, width=900, title_text=title)
        return fig


    def create_wave_chart_all(df, wave_col):
        title = df.iloc[-1]['name']
        # st.markdown('<div style="text-align: center;">{}</div>'.format(title), unsafe_allow_html=True)
        fig = make_subplots(rows=1, cols=1, shared_xaxes=True, vertical_spacing=0.01)
        # df.set_index('timestamp_est')
        # df['chartdate'] = f'{df["chartdate"].day}{df["chartdate"].hour}{df["chartdate"].minute}'
        df = df.copy()
        # df['chartdate'] = df['chartdate'].apply(lambda x: f'{x.month}{"-"}{x.day}{"_"}{x.hour}{":"}{x.minute}')
        # df[f'{wave_col}{"_number"}'] = df[f'{wave_col}{"_number"}'].astype(str)
        # dft = df[df[f'{wave_col}{"_number"}'] == '1'].copy()
        fig.add_bar(x=df[f'{wave_col}{"_number"}'], y=df[wave_col].values,  row=1, col=1, name=wave_col)
        fig.update_layout(height=600, width=900, title_text=title)
        return fig


    def return_total_profits(ORDERS):
        
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
            # ipdb.set_trace()
            if len(orders_today) > 0:
                today_pl_df = orders_today.groupby(group_by_value)[['profit_loss', 'honey']].sum().reset_index()
                total_dolla = round(sum(orders_today['profit_loss']), 2)
                total_honey = round((sum(orders_today['honey']) * 100), 2)
            else:
                today_pl_df = 0
                total_dolla = 0
                total_honey = 0
            
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
                # submitted = st.form_submit_button("Save")
        # else:
        #     st.write("Waiting for your First Trade")
        return return_dict


    def return_buying_power(api):
        with st.expander("Portfolio",  True):
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
                    st.image("https://cdn.pixabay.com/photo/2012/04/18/00/42/chess-36311_960_720.png", width=23)
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

            # wrkerbees_list = list(QUEEN_KING['qcp_workerbees'].keys())
            # # for workerbee in wrkerbees_list:
            # #     for ticker in workerbee['tickers']:
            # #         QUEEN_KING = add_trading_model(PB_APP_Pickle=PB_App_Pickle, QUEEN_KING=QUEEN_KING, ticker=ticker)
            
            # c1, c2, c3 = st.columns((1,5,1))
            # with c1:
            #     workerbee = st.selectbox('select worker', wrkerbees_list, index=wrkerbees_list.index('castle'))
            # with c2:
            #     QUEEN_KING['qcp_workerbees'][workerbee]['tickers'] = st.multiselect(label='workers', options=list(alpaca_symbols_dict.keys()) + crypto_symbols__tickers_avail, default=QUEEN_KING['qcp_workerbees'][workerbee]['tickers'])
            # with c3:
            #     flying_bee_gif()

            # with st.form("Update WorkerBees"):
                
            #     st.write("MACD Model Settings")
            #     c1, c2, c3 = st.columns(3)
            #     with c1:
            #         QUEEN_KING['qcp_workerbees'][workerbee]['MACD_fast_slow_smooth']['fast'] = st.slider("fast", min_value=1, max_value=33, value=int(QUEEN_KING['qcp_workerbees'][workerbee]['MACD_fast_slow_smooth']['fast']))
            #     with c2:
            #         QUEEN_KING['qcp_workerbees'][workerbee]['MACD_fast_slow_smooth']['slow'] = st.slider("slow", min_value=1, max_value=33, value=int(QUEEN_KING['qcp_workerbees'][workerbee]['MACD_fast_slow_smooth']['slow']))
            #     with c3:
            #         QUEEN_KING['qcp_workerbees'][workerbee]['MACD_fast_slow_smooth']['smooth'] = st.slider("smooth", min_value=1, max_value=33, value=int(QUEEN_KING['qcp_workerbees'][workerbee]['MACD_fast_slow_smooth']['smooth']))



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
            
            # ipdb.set_trace()
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
            req = ticker_time_frame__option(req_key='wavestories')
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
                    st.plotly_chart(create_guage_chart(title=f'{ticker_option} Wave Gauge', value=float(star__view["macd_tier_guage_value"])))
                with cols[1]:
                    mark_down_text(fontsize=25, text=f'{ticker_option} {"MACD Gauge "}{star__view["macd_tier_guage"]}{" Hist Gauge "}{star__view["hist_tier_guage"]}')

                    st.dataframe(df_style)

        # with cols[1]:


        
        # page_line_seperator()

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


    def queen_online(QUEEN):
        # from airflow.dags.dag_queenbee_prod import run_trigger_dag
        now = datetime.datetime.now(est)
        if (now - QUEEN['pq_last_modified']['pq_last_modified']).total_seconds() > 60:
            # st.write("YOUR QUEEN if OFFLINE")
            cols = st.columns((1,1,5))
            with cols[0]:
                st.error("Your Queen Is Asleep")
                with cols[1]:
                    wake_up_queen_button = st.button("Wake Her Up")
                    if wake_up_queen_button:
                        if st.session_state['authorized_user'] and st.session_state['admin']:
                            dag_queen__run_id = f'dag_queen__run_id___{datetime.datetime.now(est)}___pq'
                            # st.write(run__trigger_dag())
                            run__trigger_dag(dag_id='run_queenbee_prod', run_id=dag_queen__run_id, client_user=db_client_user_name, prod=prod) # stefanstapinski  @gmail.com
                            QUEEN_KING['trigger_queen'] = {'last_trig_date': datetime.datetime.now(est), 'client_user': client_user}
                            st.snow()
                        else:
                            st.warning("Your Account not Yet authorized")
            with cols[1]:
                local_gif(gif_path=flyingbee_grey_gif_path)
            return False
        else:
            return True

    def workerbees_online(QUEEN):
        # from airflow.dags.dag_queenbee_prod import run_trigger_dag
        now = datetime.datetime.now() # no est
        CASTLE = os.path.join(main_root, 'db')
        CASTLE = os.path.join(CASTLE, 'castle.pkl')
        CASTLE_lastmod = datetime.datetime.fromtimestamp(os.path.getmtime(CASTLE))
        if (now - CASTLE_lastmod).total_seconds() > 60:
            # st.write("YOUR QUEEN if OFFLINE")
            cols = st.columns((1,1,5))
            with cols[0]:
                st.error("Your Castle Is Falling")
                with cols[1]:
                    wake_up_queen_button = st.button("Wake up Castle workerbees")
                    if wake_up_queen_button:
                        if st.session_state['authorized_user']:
                            dag_queen__run_id = f'dag_queen__run_id___{datetime.datetime.now(est)}___pq'
                            # st.write(run__trigger_dag())
                            # run__trigger_dag(dag_id='run_queenbee_prod', run_id=dag_queen__run_id, client_user=db_client_user_name) # stefanstapinski  @gmail.com
                            # QUEEN_KING['trigger_workerbees'] = {'last_trig_date': datetime.datetime.now(est), 'client_user': client_user}
                            # create file in folder
                            pollen_dir = os.path.dirname(main_root)
                            client_db = os.path.join(pollen_dir, 'client_user_dbs')
                            client_db_path = os.path.join(client_db, f'db__{client_user}')
                            file_path = os.path.join(client_db_path, f'{client_user}__workerbee.txt')
                            if os.path.exists(file_path) == True:
                                pass
                            else:
                                with open(file_path, 'w'):
                                    pass
                                st.snow()
                        else:
                            st.warning("Your Account not Yet authorized")
            with cols[1]:
                local_gif(gif_path=flyingbee_grey_gif_path)
            return False
        else:
            return True

    def queen_chart(POLLENSTORY):
        # Main CHART Creation
        with st.expander('chart', expanded=True):
            req = ticker_time_frame__option(req_key='charts')
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

    
    def chunk_write_dictitems_in_row(chunk_list, max_n=10, write_type='checkbox', title="Active Models", groupby_qcp=False):
        # qcp_ticker_index = set_chess_pieces_symbols(QUEEN_KING=QUEEN_KING)['qcp_ticker_index']
        # if groupby_qcp:
        #     for qcp in set(qcp_ticker_index.values()):
        #         st.warning()

        # chunk_list = chunk_list
        num_rr = len(chunk_list) + 1 # + 1 is for chunking so slice ends at last 
        chunk_num = max_n
        if num_rr > chunk_num:
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
                                st.info(f'{ticker} {v}')
                                local_gif(gif_path=uparrow_gif, height='23', width='23')
                                flying_bee_gif(width='43', height='40')

        else:
            cols = st.columns(len(chunk_list) + 1)
            with cols[0]:
                if write_type == 'info':
                    flying_bee_gif(width='53', height='53')
                else:
                    st.write(title)
            for idx, package in enumerate(chunk_list):
                for ticker, v in package.items():
                # ticker, value = package.items()
                    with cols[idx + 1]:
                        if write_type == 'checkbox':
                            st.checkbox(ticker, v, key=f'{ticker}{v}')  ## add as quick save to turn off and on Model
                        if write_type == 'info':
                            st.info(f'{ticker} {v}')
                            flying_bee_gif(width='38', height='42')
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


    def queen__account_keys(QUEEN_KING, authorized_user, show_form=False):
        if authorized_user == False:
            return False
        view_account_button = st.sidebar.button("Update API Keys", key='sidebar_key')
        cols = st.columns((4,1,4))
        # check if keys exist
        # st.write(QUEEN_KING['users_secrets'])
        prod_keys_confirmed = QUEEN_KING['users_secrets']['prod_keys_confirmed']
        sandbox_keys_confirmed = QUEEN_KING['users_secrets']['sandbox_keys_confirmed']

        view_account_keys = False
        if sandbox_keys_confirmed == False:
            with cols[0]:
                st.error(f'Enter Your Sandbox API Keys To Activate Paper.QueenTraderBot')
            with cols[1]:
                # view_account_button = st.button("Update API Keys", key='main_key')
                view_account_keys = True
            # with cols[2]:
                local_gif(gif_path=runaway_bee_gif, height=33, width=33)
        
        if prod_keys_confirmed == False:
            with cols[2]:
                st.warning("Enter Your Production API Keys To Activate LIVE.QueenTraderBot...Begin Your Queens Journey")


        if view_account_keys or view_account_button or show_form:
            # with cols[0]:
            with st.expander("Add API Account Keys", authorized_user):
                # with cols[0]:
                local_gif(gif_path=runaway_bee_gif, height=33, width=33)
                st.session_state['account_keys'] = True
                
                with st.form("account keys"):
                    # if prod_keys_confirmed == False:
                    #     st.warning("You Need to Add you LIVE API KEYS")
                    # if sandbox_keys_confirmed == False:
                    #     st.warning("You Need to Add your Sandbox-PAPER API KEYS")

                    # st.write(st.session_state['username']) @ stefanstapinski@gmail.com
                    st.write("SandBox Paper")
                    APCA_API_KEY_ID_PAPER = st.text_input(label=f'APCA_API_KEY_ID_PAPER', value=QUEEN_KING['users_secrets']['APCA_API_KEY_ID_PAPER'], key=f'APCA_API_KEY_ID_PAPER')
                    APCA_API_SECRET_KEY_PAPER = st.text_input(label=f'APCA_API_SECRET_KEY_PAPER', value=QUEEN_KING['users_secrets']['APCA_API_SECRET_KEY_PAPER'], key=f'APCA_API_SECRET_KEY_PAPER')
                    
                    st.write("LIVE")
                    APCA_API_KEY_ID = st.text_input(label=f'APCA_API_KEY_ID', value=QUEEN_KING['users_secrets']['APCA_API_KEY_ID'], key=f'APCA_API_KEY_ID')
                    APCA_API_SECRET_KEY = st.text_input(label=f'APCA_API_SECRET_KEY', value=QUEEN_KING['users_secrets']['APCA_API_SECRET_KEY'], key=f'APCA_API_SECRET_KEY')

                    if st.form_submit_button("Save API Keys"):
                        
                        user_secrets = init_client_user_secrets(prod_keys_confirmed=False, sandbox_keys_confirmed=False, client_user=st.session_state['username'], APCA_API_KEY_ID_PAPER=APCA_API_KEY_ID_PAPER, APCA_API_SECRET_KEY_PAPER=APCA_API_SECRET_KEY_PAPER, APCA_API_KEY_ID=APCA_API_KEY_ID, APCA_API_SECRET_KEY=APCA_API_SECRET_KEY)

                        # test keys
                        test_keys = test_api_keys(user_secrets=user_secrets)

                        if test_keys['prod'] == False:
                            st.error("Production Keys Not Valid")
                            st.info(test_keys['prod_er'])
                        else:
                            st.success("Production Keys Added")
                            user_secrets['prod_keys_confirmed'] = True

                        if test_keys['sandbox'] == False:
                            st.error("Sandbox Keys Not Valid")
                            st.info(test_keys['sb_er'])
                        else:
                            st.success("Sandbox Keys Added")
                            user_secrets['sandbox_keys_confirmed'] = True
                
                        QUEEN_KING['users_secrets'] = user_secrets
                        PickleData(PB_App_Pickle, QUEEN_KING)

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

    
    
    def advanced_charts(POLLENSTORY):
        
        stars_radio_dict = {'1Min':"1Minute_1Day", '5Min':"5Minute_5Day", '30m':"30Minute_1Month", '1hr':"1Hour_3Month", 
        '2hr':"2Hour_6Month", '1Yr':"1Day_1Year", 'all':"all",}
        charts__view, waves__view, slopes__view = st.tabs(['charts', 'waves', 'slopes'])


        tickers_avail = list([set(i.split("_")[0] for i in POLLENSTORY.keys())][0])
        ttframe_list = list(set([i.split("_")[1] + "_" + i.split("_")[2] for i in POLLENSTORY.keys()]))
        ttframe_list.append(["short_star", "mid_star", "long_star", "retire_star"])

        cols = st.columns((1,10,1,1))
        # fullstory_option = st.selectbox('POLLENSTORY', ['no', 'yes'], index=['yes'].index('yes'))
        with cols[0]:
            ticker_option = st.selectbox("Tickers", tickers_avail, index=tickers_avail.index(["SPY" if "SPY" in tickers_avail else tickers_avail[0]][0]))
            ticker = ticker_option
        
        with charts__view:
            
            with cols[0]:
                option__ = st.radio(
                                        "",
                    list(stars_radio_dict.keys()),
                    key="signal_radio",
                    label_visibility='visible',
                    # disabled=st.session_state.disabled,
                    horizontal=True,
                    # label=bee_image
                )
            # with cols[1]:
                # frame_option = st.selectbox("ttframes", ttframe_list, index=ttframe_list.index(["1Minute_1Day" if "1Minute_1Day" in ttframe_list else ttframe_list[0]][0]))
            with cols[0]:
                day_only_option = st.selectbox('Show Today Only', ['no', 'yes'], index=['no'].index('no'))
            # with cols[2]:
                # wave_option = st.sidebar.selectbox('Show Waves', ['no', 'yes'], index=['no'].index('no'))
                # slope_option = st.sidebar.selectbox('Show Slopes', ['no', 'yes'], index=['no'].index('no'))
            

            # selections = [i for i in POLLENSTORY.keys() if i.split("_")[0] in ticker_option and i.split("_")[1] in frame_option]
            # ticker_time_frame = selections[0]
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
            
            dft = split_today_vs_prior(df=df)
            dft = dft['df_today']

            fig=create_wave_chart_all(df=dft, wave_col='buy_cross-0__wave')
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
        
        return True


    
    # """ Keys """ ### NEEDS TO BE FIXED TO PULL USERS API CREDS UNLESS USER IS PART OF MAIN.FUND.Account
    # @st.cache(allow_output_mutation=True, max_entries=1)



    ########################################################
    ########################################################
    #############The Infinite Loop of Time #################
    ########################################################
    ########################################################
    ########################################################


    # """ if "__name__" == "__main__": """

    # st.image(chess_piece_queen, width=23)

    ## answer the question what to show to a User when they first Sign On OR whats a Preview to Show? I.E. if User Not allowed then show Sandbox Data?

    # use API keys from user
    queen_online(QUEEN=QUEEN)
    
    prod_keys_confirmed = QUEEN_KING['users_secrets']['prod_keys_confirmed']
    sandbox_keys_confirmed = QUEEN_KING['users_secrets']['sandbox_keys_confirmed']

    if st.session_state['authorized_user']:
        clean_out_app_requests(QUEEN=QUEEN, QUEEN_KING=QUEEN_KING, request_buckets=['subconscious'])
    # ipdb.set_trace()
    api = return_alpaca_user_apiKeys(QUEEN_KING=QUEEN_KING, authorized_user=authorized_user, prod=st.session_state['production'])
    
    try:
        snapshot = api.get_snapshot("SPY") # return_last_quote from snapshot
    except Exception as e:
        # requests.exceptions.HTTPError: 403 Client Error: Forbidden for url: https://data.alpaca.markets/v2/stocks/SPY/snapshot
        st.write("your api failed you need to update your api keys from alpaca.broker... taking you there")
        # time.sleep(5)
        queen__account_keys(PB_App_Pickle=PB_App_Pickle, QUEEN_KING=QUEEN_KING, authorized_user=authorized_user, show_form=True) #EDRXZ Maever65teo
        st.stop()

    
    portfolio = return_alpc_portolio(api)['portfolio']
    acct_info = refresh_account_info(api=api)

    # # if authorized_user: log type auth and none
    log_dir = os.path.join(db_root, 'logs')
    init_logging(queens_chess_piece=queens_chess_piece, db_root=db_root, prod=st.session_state['production'])

    # db global
    coin_exchange = "CBSE"

    # Ticker DataBase
    ticker_db = read_pollenstory(db_root=os.path.join(os.getcwd(), 'db'), dbs=['castle.pkl', 'bishop.pkl', 'castle_coin.pkl', 'knight.pkl'])
    POLLENSTORY = ticker_db['pollenstory']
    STORY_bee = ticker_db['STORY_bee']
    tickers_avail = [set(i.split("_")[0] for i in STORY_bee.keys())][0]

    # cols = st.columns((3,10,1,1))
    # with cols[1]:
    if authorized_user:
        option = st.sidebar.radio(
                    label="",
            options=["queen", "controls", "model_results", "pollen_engine"],
            key="main_radio",
            label_visibility='visible',
            # disabled=st.session_state.disabled,
            horizontal=False,
        )
    else:
        option = st.sidebar.radio(
                    label="",
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


def ticker_time_frame__option(req_key):
    cols = st.columns(2)
    with cols[0]:
        if 'sel_tickers' not in st.session_state:
            st.session_state['sel_tickers'] = 'SPY'
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

# req = ticker_time_frame__option()
# tickers = req['tickers']
# ticker_option = req['ticker_option']
# frame_option = req['frame_option']

# ticker_storys = {k:v for (k,v) in STORY_bee.items() if k.split("_")[0] in tickers}

# ticker_time_frame = f'{ticker_option}{"_"}{frame_option}'

# star__view = its_morphin_time_view(QUEEN=QUEEN, STORY_bee=STORY_bee, ticker=ticker_option, POLLENSTORY=POLLENSTORY)

today_day = datetime.datetime.now(est).day
current_radio_sel = str(option).lower()
if str(option).lower() == 'queen':
    if st.session_state['authorized_user'] == False:
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
                st.success("Hive Master Notified and You should receive contact soon")
    
    with st.spinner("Waking Up the Hive"):

        progress_bar(value=100)
                    
        # page_line_seperator('1', color=default_yellow_color)
        if st.session_state['authorized_user'] == True:
            # keys
            queen__account_keys(QUEEN_KING=QUEEN_KING, authorized_user=authorized_user, show_form=False)
            # add new trading models if needed
            for workerbee, bees_data in QUEEN_KING['qcp_workerbees'].items():
                for ticker in bees_data['tickers']:
                    QUEEN_KING = add_trading_model(PB_APP_Pickle=PB_App_Pickle, QUEEN_KING=QUEEN_KING, ticker=ticker, workerbee=workerbee)

        tickers_avail_op = list(tickers_avail)

        # page_line_seperator(height='1')
        cols = st.columns(2)

        # cols = st.columns((1,1))

        queen_tabs = ["Orders", "Portforlio", "Wave Stories", "Chess Board", "Trading Models", "Charts"]
        order_tab, Portforlio, wave_stories_tab, chessboard_tab, trading_models_tab, charts_tab = st.tabs(queen_tabs)


        with cols[1]:
            return_total_profits(ORDERS=ORDERS)
        with cols[0]:
            queens_subconscious_Thoughts(QUEEN=QUEEN)

        with Portforlio:
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
            advanced_charts(POLLENSTORY=POLLENSTORY)

        with trading_models_tab:
            queen__write_active_symbols(QUEEN_KING=QUEEN_KING)
            st.header("Select Control")
            theme_list = list(pollen_theme.keys())
            contorls = list(QUEEN['queen_controls'].keys())
            control_option = st.selectbox('control', contorls, index=contorls.index('theme'))
            update_QueenControls(QUEEN_KING=QUEEN_KING, control_option=control_option, theme_list=theme_list)
        
        
        
        
        page_line_seperator(color=default_yellow_color)

        st.sidebar.image(learningwalk_bee, width=54)


if str(option).lower() == 'controls':

    cols = st.columns((1,3))
    if admin == False:
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
    # tickers_avail = [set(i.split("_")[0] for i in STORY_bee.keys())][0]
    # tickers_avail.update({"all"})
    cols = st.columns(2)
    tickers_avail_op = list(tickers_avail)
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
    cols = st.columns(3)
    # with cols[1]:
    #     local_gif(gif_path=queen_flair_gif, height=350, width=400)
    
    page_tab_permission_denied(admin, st_stop=True)
    
    with st.expander("alpaca account info"):
        st.write(acct_info['info'])

    with st.expander('betty_bee'):
        betty_bee = ReadPickleData(os.path.join(db_root, 'betty_bee.pkl'))
        df_betty = pd.DataFrame(betty_bee)
        df_betty = df_betty.astype(str)
        st.write(df_betty)

    with st.expander('charlie_bee'):

        queens_charlie_bee = ReadPickleData(os.path.join(db_root, 'charlie_bee.pkl'))
        df_charlie = pd.DataFrame(queens_charlie_bee)
        df_charlie = df_charlie.astype(str)
        st.write(df_charlie)
    
    if admin == False:
        st.warning("End of the Line")
        st.stop()
    with st.expander('queen logs'):
        logs = os.listdir(log_dir)
        logs = [i for i in logs if i.endswith(".log")]
        log_file = st.selectbox('log files', list(logs))
        with open(os.path.join(log_dir, log_file), 'r') as f:
            content = f.readlines()
            st.write(content)
    with st.expander('users db'):
        con = sqlite3.connect("db/users.db")
        cur = con.cursor()

        users = cur.execute("SELECT * FROM users").fetchall()
        st.dataframe(pd.DataFrame(users))
    

st.session_state['option_sel'] = False
st.session_state['sneak_peak'] = False
##### END ####