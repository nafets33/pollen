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
import time
import _locale
import os
from random import randint
import sqlite3
import streamlit as st
from appHive import queen_order_flow, grid_height, createParser_App, click_button_grid, nested_grid, mark_down_text, page_line_seperator, write_flying_bee, hexagon_gif, local_gif, flying_bee_gif, pollen__story
from app_auth import signin_main
import base64
import time

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


main_root = os.getcwd()

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
default_text_color = '#59490A'
default_font = "sans serif"
default_yellow_color = '#C5B743'

with st.spinner("QueensOrders pollenq"):
    if 'username' not in st.session_state:
        signin_auth = signin_main()
    
    parser = createParser_App()
    namespace = parser.parse_args()
    admin = True if namespace.admin == 'true' or st.session_state['username'] == 'stefanstapinski@gmail.com' else False
    authorized_user = True if namespace.admin == 'true' or st.session_state['username'] == 'stefanstapinski@gmail.com' else False
    st.session_state['admin'] = True if admin else False


    if st.session_state['authentication_status']:
        # def INIT SETUP
        def set_prod_env(prod):
            st.session_state['production'] = prod
            # st.sidebar.image(chess_piece_queen, width=23)
        
        prod = True if 'production' in st.session_state and st.session_state['production'] == True else False
        prod_name = 'LIVE' if 'production' in st.session_state and st.session_state['production'] == True else 'Sandbox'
        
        if prod:
            from QueenHive import  init_clientUser_dbroot, init_pollen_dbs, KINGME, ReadPickleData, pollen_themes, PickleData, add_key_to_app
            load_dotenv(os.path.join(os.getcwd(), '.env_jq'))
        else:
            from QueenHive_sandbox import init_clientUser_dbroot, init_pollen_dbs, KINGME, ReadPickleData, pollen_themes, PickleData, add_key_to_app
            load_dotenv(os.path.join(os.getcwd(), '.env'))
        
        st.sidebar.write(f'Welcome {st.session_state["name"]}')
        admin = True if st.session_state['username'] == 'stefanstapinski@gmail.com' else False
        st.session_state['admin'] = True if admin else False
        client_user = st.session_state['username']
        authorized_user = True if st.session_state['username'] == 'stefanstapinski@gmail.com' else False
        
        db_root = init_clientUser_dbroot(client_user=client_user) # main_root = os.getcwd() // # db_root = os.path.join(main_root, 'db')
        init_pollen = init_pollen_dbs(db_root=db_root, prod=prod, queens_chess_piece='queen')
        PB_QUEEN_Pickle = init_pollen['PB_QUEEN_Pickle']
        PB_App_Pickle = init_pollen['PB_App_Pickle']
        PB_Orders_Pickle = init_pollen['PB_Orders_Pickle']

        QUEEN = ReadPickleData(PB_QUEEN_Pickle)
        ORDERS = ReadPickleData(PB_Orders_Pickle)

        QUEEN_KING = ReadPickleData(pickle_file=PB_App_Pickle)
        QUEEN_KING['source'] = PB_App_Pickle
        APP_req = add_key_to_app(QUEEN_KING)
        if APP_req['update']:
            QUEEN_KING = APP_req['QUEEN_KING']
            PickleData(pickle_file=PB_App_Pickle, data_to_store=QUEEN_KING)

        KING = KINGME()
        pollen_theme = pollen_themes(KING=KING)
        theme_list = list(pollen_theme.keys())
        # Return True

        st.sidebar.selectbox('LIVE/Sandbox', ['LIVE', 'Sandbox'], index=['LIVE', 'Sandbox'].index(prod_name), on_change=set_prod_env(prod))

        if authorized_user:
            READONLY = False
            if 'admin' in st.session_state.keys() and st.session_state['admin']:
                admin = True
                st.sidebar.write('admin', admin)
            # SETUP USER #
            # Client User DB
            db_root = init_clientUser_dbroot(client_user=client_user) # main_root = os.getcwd() // # db_root = os.path.join(main_root, 'db')
            init_pollen = init_pollen_dbs(db_root=db_root, prod=prod, queens_chess_piece='queen')
            PB_QUEEN_Pickle = init_pollen['PB_QUEEN_Pickle']
            PB_App_Pickle = init_pollen['PB_App_Pickle']
            PB_Orders_Pickle = init_pollen['PB_Orders_Pickle']
            # PB_users_secrets = init_pollen['PB_users_secrets']

        else:

            # Read Only View
            READONLY = True
            db_root = os.path.join(main_root, 'db')  ## Force to Main db and Sandbox API
            prod = False
            load_dotenv(os.path.join(os.getcwd(), '.env'))
            init_pollen = init_pollen_dbs(db_root=db_root, prod=False, queens_chess_piece='queen')
            PB_QUEEN_Pickle = init_pollen['PB_QUEEN_Pickle']
            PB_App_Pickle = init_pollen['PB_App_Pickle']
            PB_Orders_Pickle = init_pollen['PB_Orders_Pickle']
            st.sidebar.write('Read Only')
            if st.session_state['authentication_status']:
                st.error("Request Access for a Queen! QUICK only a limited number of Queens Available!! Please contact pollenq.queen@gmail.com")
            else:
                st.error("You Are In Read OnlyMode...zzzz...You Need to Create an Account to Request Access for a Queen! QUICK only a limited number of Queens Available!! Please contact pollenq.queen@gmail.com for any questions")
            admin = False


        queen_order_flow(QUEEN=QUEEN, active_order_state_list=active_order_state_list)