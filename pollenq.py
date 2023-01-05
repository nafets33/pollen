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
from app_auth import signin_main
import time
from streamlit_extras.switch_page_button import switch_page
from appHive import createParser_App, local_gif, mark_down_text, update_queencontrol_theme, progress_bar, page_line_seperator, return_runningbee_gif__save
from King import hive_master_root, streamlit_config_colors
import argparse
from streamlit_extras.stoggle import stoggle

def pollenq():
    # prod = True if prod.lower() == 'true' else False

    # if prod:
    #     from QueenHive import  init_clientUser_dbroot, init_pollen_dbs, KINGME, ReadPickleData, pollen_themes, PickleData, add_key_to_app
    #     load_dotenv(os.path.join(os.getcwd(), '.env_jq'))
    # else:
    #     from QueenHive_sandbox import init_clientUser_dbroot, init_pollen_dbs, KINGME, ReadPickleData, pollen_themes, PickleData, add_key_to_app
    #     load_dotenv(os.path.join(os.getcwd(), '.env'))
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

    main_root = hive_master_root() # os.getcwd()  # hive root

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
    castle_png = "https://images.vexels.com/media/users/3/255175/isolated/lists/3c6de0f0c883416d9b6bd981a4471092-rook-chess-piece-line-art.png"
    bishop_png = "https://images.vexels.com/media/users/3/255170/isolated/lists/efeb124323c55a60510564779c9e1d38-bishop-chess-piece-line-art.png"
    knight_png = "https://cdn2.iconfinder.com/data/icons/chess-set-pieces/100/Chess_Set_04-White-Classic-Knight-512.png"
    queen_png = "https://cdn.shopify.com/s/files/1/0925/9070/products/160103_queen_chess_piece_wood_shape_600x.png?v=1461105893"
    queen_flair_gif = os.path.join(jpg_root, 'queen_flair.gif')
    mainpage_bee_png = "https://i.pinimg.com/originals/a8/95/e8/a895e8e96c08357bfeb92d3920cd7da0.png"
    runaway_bee_gif = os.path.join(jpg_root, 'runaway_bee_gif.gif')
    floating_queen_gif = os.path.join(jpg_root, "floating-queen-unscreen.gif")

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
    # st.write(st.session_state)
    with st.spinner("Hello Welcome To pollenq"):
        signin_main()
        
        if st.session_state['authentication_status'] != None:
            if st.session_state['authorized_user'] == False:
                st.info("Your Need to have your account authorized before receiving a QueenTraderBot, Please contact pollenq.queen@gmail.com or click the button below to send a Request")
                client_user_wants_a_queen = st.button("Yes I want a Queen!")
                if client_user_wants_a_queen:
                    st.session_state['init_queen_request'] = True
        
        # parser = createParser_App()
        # namespace = parser.parse_args()


        if st.session_state['authentication_status']:
            # if 'username' not in st.session_state:
            #     signin_auth = signin_main()
            
            st.sidebar.write(f'Welcome {st.session_state["name"]}')
            st.sidebar.write(f'{st.session_state["username"]}')
            client_user = st.session_state['username']
            authorized_user = st.session_state['authorized_user']
            db_client_user_name = st.session_state['username'].split("@")[0]

            prod = True if 'production' in st.session_state and st.session_state['production'] == True else False
            admin = True if st.session_state['username'] == 'stefanstapinski@gmail.com' else False
            st.session_state['admin'] = True if admin else False

            prod_option = st.sidebar.selectbox('LIVE/Sandbox', ['LIVE', 'Sandbox'])#, on_change=save_change())
            st.session_state['production'] = True if prod_option == 'LIVE' else False
            prod = st.session_state['production']

            
            if st.session_state['production']:
                from QueenHive import return_alpaca_user_apiKeys, init_client_user_secrets, test_api_keys, return_queen_controls, return_STORYbee_trigbees, return_alpaca_api_keys, add_key_to_app, read_pollenstory, init_clientUser_dbroot, init_pollen_dbs, refresh_account_info, generate_TradingModel, stars, analyze_waves, KINGME, queen_orders_view, story_view, return_alpc_portolio, return_dfshaped_orders, ReadPickleData, pollen_themes, PickleData, return_timestamp_string, return_api_keys, read_queensmind, split_today_vs_prior, init_logging
                load_dotenv(os.path.join(os.getcwd(), '.env_jq'))
            else:
                from QueenHive_sandbox import return_alpaca_user_apiKeys, init_client_user_secrets, test_api_keys, return_queen_controls, return_STORYbee_trigbees, return_alpaca_api_keys, add_key_to_app, read_pollenstory, init_clientUser_dbroot, init_pollen_dbs, refresh_account_info, generate_TradingModel, stars, analyze_waves, KINGME, queen_orders_view, story_view, return_alpc_portolio, return_dfshaped_orders, ReadPickleData, pollen_themes, PickleData, return_timestamp_string, return_api_keys, read_queensmind, split_today_vs_prior, init_logging
                load_dotenv(os.path.join(os.getcwd(), '.env'))

            # if db__name exists use db__name else use db
            db_root = st.session_state['db_root']

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
            # Return True

            if 'init_queen_request' in st.session_state:
                QUEEN_KING['init_queen_request'] = {'timestamp_est': datetime.datetime.now(est)}
                PickleData(PB_App_Pickle, QUEEN_KING)
                st.success("Hive Master Notified and You should receive contact soon")

            # hive_setup, QueenInfo, pollenq_account, = st.tabs(["Setup Your Hive", "QueenInfo", "MyAccount"])
            cols = st.columns((3,1,5,1,1,1,1))
            st.title("Create Yourself The QueenTrader")
            with cols[0]:
                st.text("Customize QueenTraderBot Settings!\nTrade based on how you feel&think" )
            with cols[1]:
                st.image(mainpage_bee_png, width=89)
            with cols[2]:
                st.text("Set an investment theme and watch your QueenTraderBot\nhandle everyone of your trades, trade along side her")
            with cols[3]:
                st.image(castle_png, width=133)
            with cols[4]:
                st.image(mainpage_bee_png, width=133)
            
            cols = st.columns((5,3,3,2,2,2))
            with cols[0]:
                st.subheader("Steps to get your QueenTraderBot")
                stoggle("1. Select your Broker",
                "Alpaca is only current supported broker (Alpaca is a free no-fee trading broker, they are FDIC 250k insured) create a FREE account at https://app.alpaca.markets/brokerage/new-account"
                )
            with cols[0]:
                stoggle("2. Enter in your API Keys ",
                """
                (this allows the QueenTraderBot to place trades) Its going to change the way you trade forever...everyone needs an AI :bot:
                """
                )
            with cols[0]:
                stoggle("3. Set your Risk Parameters",
                """
                Go Start Building your QueenTradingBot! There is too much to dicuss now...we'll talk later
                """
                )
            with cols[1]:
                st.image(queen_png, width=250)

            with cols[3]:
                # local_gif(gif_path=queen_flair_gif, height=254, width=450)
                st.image(bishop_png, width=223)

            with cols[2]:
                # local_gif(gif_path=queen_flair_gif, height=254, width=450)
                st.image(mainpage_bee_png, width=133)
            # with cols[4]:
            #     # local_gif(gif_path=queen_flair_gif, height=254, width=450)
            #     st.image(knight_png, width=133)    
            
            page_line_seperator('1')
            st.subheader("QueenTraderBot Settings")
            with st.expander("QueenTraderBot Settings"):
                mark_down_text(align='left', color=default_text_color, fontsize='23', text='Ensure to Complete Step 1 and an Create Alpaca Account', font=default_font, hyperlink="https://app.alpaca.markets/brokerage/new-account")
                cols = st.columns((3,4,1))
                # with cols[0]:
                #     st.error("1 Create Alpaca Account")
                # with cols[1]:

                # st.info("2 Request a queen and enter in Aplaca API credentials")
                # st.info("3 Create Risk Settings")
                # st.success("4 Start Trading")
                def update_age():
                    return True
                # with st.expander("Risk Levels"):
                with cols[0]:
                    with st.form("Set How You Wish your Queen to Trade"):
                        st.subheader("Set Your Risk Level")
                    # st.write(QUEEN_KING.keys())
                        st.text("How Old are you?")
                        birthday = st.date_input("Enter your birthday: YYYY/MM/DD")
                        yrs_old = datetime.datetime.now().year - birthday.year
                        if QUEEN_KING['age'] == 0:
                            QUEEN_KING['age'] = yrs_old
                        
                        QUEEN_KING['risk_level'] = st.slider("Risk Level", min_value=1, max_value=10, value=int(QUEEN_KING['risk_level']), help="Shoot for the Moon or Steady as she goes")            
                        QUEEN_KING['age'] = st.slider("Age..How you Feel to Risk", min_value=1, max_value=100, value=int(QUEEN_KING['age']))     
                        QUEEN_KING['QueenTraders_Bithday'] = birthday
                        if st.form_submit_button('Save Risk Settings'):
                            PickleData(pickle_file=PB_App_Pickle, data_to_store=QUEEN_KING)
                            return_runningbee_gif__save(title='Risk Saved')
                            
                with cols[1]:
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
                    welcome = st.button("QueensConscience")
                    # st.write("The Hive QueensConscience")
                    pass
                with cols[1]:
                    local_gif(gif_path=flyingbee_gif_path, height=23, width=23)

                # local_gif(gif_path=queen_flair_gif, height=450, width=500)
                    # st.button("Show", key=1)
                # with cols[1]:
                #     local_gif(gif_path=queen_flair_gif, height=450, width=500)
                
                if welcome:
                    switch_page("QueensConscience")

            if option == 'help':
                mark_down_text(fontsize='22', text="No Soup for you! Go figure it out..Set a theme and let it handle your entire portfolio....it will beat you ;) ")
        
        else:
            st.session_state['authorized_user'] = False
            st.session_state['admin'] = False
            st.session_state['prod'] = False
            st.error("Create an Account! QUICK only a limited number of Queens Available!! Please contact pollenq.queen@gmail.com for any questions")
            progress_bar(value=33, text=f'{100-33} Queens Remaining')

            cols = st.columns((3,2,5))
            with cols[0]:
                sneak_peak = st.button("Take a sneak peak and watch a Queen Trade in Real Time")
                if sneak_peak:
                    st.session_state['sneak_peak'] = True
                    switch_page("QueensConscience")
                else:
                    st.session_state['sneak_peak'] = False
            with cols[1]:
                local_gif(floating_queen_gif, '100', '123')
            
if __name__ == '__main__':
    # def createParser():
    #     parser = argparse.ArgumentParser()
    #     parser.add_argument ('--qcp', default="queen")
    #     parser.add_argument ('--prod', default='false')
    #     return parser
    # parser = createParser()
    # namespace = parser.parse_args()
    # prod = namespace.prod
    pollenq()