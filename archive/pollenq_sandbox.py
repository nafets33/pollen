import pandas as pd
import logging
import os
import pandas as pd
import datetime
import pytz
import ipdb
import matplotlib.pyplot as plt
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from itertools import islice
from PIL import Image
from dotenv import load_dotenv
import os
# from random import randint
import streamlit as st
from polleq_app_auth import signin_main
import time
from streamlit_extras.switch_page_button import switch_page
from appHive import createParser_App, local_gif, mark_down_text, update_queencontrol_theme, progress_bar
# from streamlit_extras.stoggle import stoggle


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
# https://www.freeformatter.com/cron-expression-generator-quartz.html
# http://34.162.236.105:8080/home # dags

pd.options.mode.chained_assignment = None

scriptname = os.path.basename(__file__)
queens_chess_piece = os.path.basename(__file__)

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
chess_piece_queen = "https://cdn.pixabay.com/photo/2012/04/18/00/42/chess-36311_960_720.png"

queen_flair_gif = os.path.join(jpg_root, 'queen_flair.gif')

runaway_bee_gif = os.path.join(jpg_root, 'runaway_bee_gif.gif')

page_icon = Image.open(bee_image)

##### STREAMLIT ###
default_text_color = '#59490A'
default_font = "sans serif"
default_yellow_color = '#C5B743'

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
# st.write(st.session_state)
with st.spinner("Hello Welcome To pollenq"):
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
        
        # hive_setup, QueenInfo, pollenq_account, = st.tabs(["Setup Your Hive", "QueenInfo", "MyAccount"])
        st.title("Create Yourself The QueenTrader")
        st.text("Set Trader Settings, Setting will preset AI Trading Patterns and Behaviors. Trade based on how you feel")

        with st.expander("Set Trader Settings"):
            # stoggle("Create Your Alpaca Account Steps",
            # mark_down_text(align='left', color=default_text_color, fontsize='33', text='Create Alpaca Account', font=default_font, hyperlink="https://app.alpaca.markets/brokerage/new-account")
            # )
            cols = st.columns((3,4, 8))
            with cols[0]:
                st.error("1 Create Alpaca Account")
            with cols[1]:
                mark_down_text(align='left', color=default_text_color, fontsize='33', text='Create Alpaca Account', font=default_font, hyperlink="https://app.alpaca.markets/brokerage/new-account")
            
            st.info("2 Request a queen and enter in Aplaca API credentials")
            st.info("3 Create Risk Settings")
            st.success("4 Start Trading")

            # with st.expander("Risk Levels"):
            with st.form("Set How You Wish your Queen to Trade"):
                cols = st.columns((2,3))
                with cols[0]:
                    st.subheader("Set Your Risk Level")
                # st.write(QUEEN_KING.keys())
                with cols[1]:
                    st.slider("Risk Level", min_value=1, max_value=10, value=int(QUEEN_KING['risk_level']))            
                    st.slider("Age..How you Feel to Risk", min_value=1, max_value=100, value=int(QUEEN_KING['age']))     
                
                if st.form_submit_button('Save Risk Settings'):
                    PickleData(pickle_file=PB_App_Pickle, data_to_store=QUEEN_KING)
            
            update_queencontrol_theme(QUEEN_KING, theme_list)


    
        # QueenInfo, macc, infohelp = st.tabs(["To The Hive", "MyAccount", "Info Help Doc"])
        option = st.radio(
                    label="",
            options=["to_the_hive", "help"],
            key="main_radio",
            label_visibility='visible',
            # disabled=st.session_state.disabled,
            horizontal=True,
        )
        if option == 'to_the_hive':
            cols = st.columns((2,4,2))
            with cols[0]:
                welcome = st.button("Take me to the Hive, Inside the QueensConscience")
                # st.write("The Hive QueensConscience")
                pass
            with cols[1]:
                local_gif(gif_path=flyingbee_gif_path, height=23, width=23)

            local_gif(gif_path=queen_flair_gif, height=450, width=500)
                # st.button("Show", key=1)
            # with cols[1]:
            #     local_gif(gif_path=queen_flair_gif, height=450, width=500)
            
            if welcome:
                switch_page("QueensConscience")
    else:
        st.session_state['authorized_user'] = False
        st.session_state['admin'] = False
        st.session_state['prod'] = False
        st.error("Create an Account! QUICK only a limited number of Queens Available!! Please contact pollenq.queen@gmail.com for any questions")
        progress_bar(value=33, text=f'{100-33} Queens Remaining')

        if st.button("Take a sneak peak and watch a Queen Trade in Real Time"):
            switch_page("QueensConscience")