import pandas as pd
import streamlit as st
import logging
import os
import pandas as pd
import numpy as np
import datetime
import pytz
from typing import Callable
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
from streamlit_extras.switch_page_button import switch_page
import time
import os
from random import randint
import sqlite3
import base64
import time
import streamlit as st
from polleq_app_auth import signin_main
from chess_piece.king import hive_master_root, streamlit_config_colors
from chess_piece.queen_hive import add_key_to_app, init_pollen_dbs, KINGME, ReadPickleData, pollen_themes, PickleData
from chess_piece.app_hive import queen_order_flow, live_sandbox__setup_switch, createParser_App, click_button_grid, nested_grid, mark_down_text, page_line_seperator, write_flying_bee, hexagon_gif, local_gif, flying_bee_gif, pollen__story


est = pytz.timezone("US/Eastern")

# _locale._getdefaultlocale = (lambda *args: ['en_US', 'UTF-8'])

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


main_root = hive_master_root() # os.getcwd()

# images
jpg_root = os.path.join(main_root, 'misc')
chess_pic_1 = os.path.join(jpg_root, 'chess_pic_1.jpg')
bee_image = os.path.join(jpg_root, 'bee.jpg')
bee_power_image = os.path.join(jpg_root, 'power.jpg')
hex_image = os.path.join(jpg_root, 'hex_design.jpg')
hive_image = os.path.join(jpg_root, 'bee_hive.jpg')
queen_image = os.path.join(jpg_root, 'queen.jpg')
queen_angel_image = os.path.join(jpg_root, 'queen_angel.jpg')
flyingbee_gif_path = os.path.join(jpg_root, 'flyingbee_gif_clean.gif')
flyingbee_grey_gif_path = os.path.join(jpg_root, 'flying_bee_clean_grey.gif')
bitcoin_gif = os.path.join(jpg_root, 'bitcoin_spinning.gif')
power_gif = os.path.join(jpg_root, 'power_gif.gif')
uparrow_gif = os.path.join(jpg_root, 'uparrows.gif')

queen_flair_gif = os.path.join(jpg_root, 'queen_flair.gif')
# queen_flair_gif_original = os.path.join(jpg_root, 'queen_flair.gif')

runaway_bee_gif = os.path.join(jpg_root, 'runaway_bee_gif.gif')

page_icon = Image.open(bee_image)

##### STREAMLIT ###

k_colors = streamlit_config_colors()
default_text_color = k_colors['default_text_color'] # = '#59490A'
default_font = k_colors['default_font'] # = "sans serif"
default_yellow_color = k_colors['default_yellow_color'] # = '#C5B743'

page = 'QueensOrders'

with st.spinner("QueensOrders pollenq"):

    signin_main()

    if st.session_state['authentication_status'] != True:
        st.error("You Need to Log In")
        st.stop()

    db_root = st.session_state['db_root']

    st.sidebar.write(f'{st.session_state["name"]} Playgound')
    authorized_user = st.session_state['authorized_user']
    client_user = st.session_state["client_user"]
    st.write("*", client_user)

    prod, admin, prod_name = live_sandbox__setup_switch(client_user=client_user)
    prod_name_oppiste = "Sandbox" if prod  else "LIVE"
    if st.sidebar.button(f'Switch to {prod_name_oppiste}'):
        prod, admin, prod_name = live_sandbox__setup_switch(client_user=st.session_state["client_user"], switch_env=True)
        init_pollen_dbs(db_root=db_root, prod=prod, queens_chess_piece='queen', queenKING=True)
        switch_page('QueensOrders')

    
    # if st.session_state['production']:
    #     from QueenHive import return_alpaca_user_apiKeys, init_client_user_secrets, test_api_keys, return_queen_controls, return_STORYbee_trigbees, return_alpaca_api_keys, add_key_to_app, read_pollenstory, init_clientUser_dbroot, init_pollen_dbs, refresh_account_info, generate_TradingModel, stars, analyze_waves, KINGME, queen_orders_view, story_view, return_alpc_portolio, return_dfshaped_orders, ReadPickleData, pollen_themes, PickleData, return_timestamp_string, return_api_keys, read_queensmind, split_today_vs_prior, init_logging
    #     load_dotenv(os.path.join(os.getcwd(), '.env_jq'))
    # else:
    #     from QueenHive_sandbox import return_alpaca_user_apiKeys, init_client_user_secrets, test_api_keys, return_queen_controls, return_STORYbee_trigbees, return_alpaca_api_keys, add_key_to_app, read_pollenstory, init_clientUser_dbroot, init_pollen_dbs, refresh_account_info, generate_TradingModel, stars, analyze_waves, KINGME, queen_orders_view, story_view, return_alpc_portolio, return_dfshaped_orders, ReadPickleData, pollen_themes, PickleData, return_timestamp_string, return_api_keys, read_queensmind, split_today_vs_prior, init_logging
    #     load_dotenv(os.path.join(os.getcwd(), '.env'))


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

    APP_req = add_key_to_app(QUEEN_KING)
    QUEEN_KING = APP_req['QUEEN_KING']
    if APP_req['update']:
        PickleData(PB_App_Pickle, QUEEN_KING)
        pollen_theme = pollen_themes(KING=KING)
        theme_list = list(pollen_theme.keys())

    queen_order_flow(ORDERS=ORDERS, active_order_state_list=active_order_state_list)


    with st.form("Edit Order Rules"):

        st.write("Orders Form Draft")
        status = st.checkbox("Active")

        limit_cols = st.columns(3)
        trade_using_limits = limit_cols[0].checkbox("Trade Using Limits")
        limitprice_decay_timeduration = limit_cols[1].number_input(
            "Limit Price Decay Time Duration"
        )
        doubledown_timeduration = limit_cols[2].number_input("Double Down Time Duration")

        max_profit_cols = st.columns(2)
        max_profit_waveDeviation = max_profit_cols[0].number_input(
            "Max Profit Wave Deviation"
        )
        max_profit_waveDeviation_timeduration = max_profit_cols[1].number_input(
            "Max Profit Wave Deviation Time Duration"
        )

        profit_cols = st.columns(3)
        timeduration = profit_cols[0].number_input("Time Duration")
        take_profit = profit_cols[1].number_input("Take Profit")
        sellout = profit_cols[2].number_input("Sellout")

        stagger_profit_cols = st.columns([2, 2, 3])
        sell_trigbee_trigger = stagger_profit_cols[0].checkbox("Sell Trigbee Trigger")
        stagger_profits = stagger_profit_cols[1].checkbox("Stagger Profits")
        stagger_profits_tiers = stagger_profit_cols[2].number_input("Stagger Profits Tiers")

        scalp_profits_cols = st.columns([1, 3])
        scalp_profits = scalp_profits_cols[0].checkbox("Scalp Profits")
        scalp_profits_timeduration = scalp_profits_cols[1].number_input(
            "Scalp Profits Time Duration"
        )

        if st.form_submit_button("Send"):
            # return values
            st.success("Order Sent!")


        # {
        #     "status": "active",
        #     "trade_using_limits": False,
        #     "limitprice_decay_timeduration": 1,
        #     "doubledown_timeduration": 60,
        #     "max_profit_waveDeviation": 1,
        #     "max_profit_waveDeviation_timeduration": 1440,
        #     "timeduration": 525600,
        #     "take_profit": 0.1,
        #     "sellout": -0.05,
        #     "sell_trigbee_trigger": True,
        #     "stagger_profits": False,
        #     "stagger_profits_tiers": 1,

        #     "scalp_profits": False,
        #     "scalp_profits_timeduration": 30,
        # }

        # 'theme': theme,
        # 'status': status,
        # 'trade_using_limits': trade_using_limits,
        # 'limitprice_decay_timeduration': limitprice_decay_timeduration, # TimeHorizion: i.e. the further along time how to sell out of profit
        # 'doubledown_timeduration': doubledown_timeduration,
        # 'max_profit_waveDeviation': max_profit_waveDeviation,
        # 'max_profit_waveDeviation_timeduration': max_profit_waveDeviation_timeduration,
        # 'timeduration': timeduration,
        # 'take_profit': take_profit,
        # 'sellout': sellout,
        # 'sell_trigbee_trigger': sell_trigbee_trigger,
        # 'stagger_profits': stagger_profits,
        # 'scalp_profits': scalp_profits,
        # 'scalp_profits_timeduration': scalp_profits_timeduration,
        # 'stagger_profits_tiers': stagger_profits_tiers,
        # 'skip_sell_trigbee_distance_frequency': skip_sell_trigbee_distance_frequency, # skip sell signal if frequency of last sell signal was X distance >> timeperiod over value, 1m: if sell was 1 story index ago
        # 'ignore_trigbee_at_power': ignore_trigbee_at_power,
        # 'ignore_trigbee_in_macdstory_tier': ignore_trigbee_in_macdstory_tier,
        # 'ignore_trigbee_in_histstory_tier': ignore_trigbee_in_histstory_tier,
        # 'ignore_trigbee_in_vwap_range': ignore_trigbee_in_vwap_range,
        # 'take_profit_in_vwap_deviation_range': take_profit_in_vwap_deviation_range,
        # 'short_position': short_position
