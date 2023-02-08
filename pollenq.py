# pollenq
import pandas as pd
import logging
import os
import pandas as pd
import datetime
import pytz
import ipdb
# import matplotlib.pyplot as plt
# from plotly.subplots import make_subplots
# import plotly.graph_objects as go
# from itertools import islice
from PIL import Image
from dotenv import load_dotenv
import os
# from random import randint
import streamlit as st
from polleq_app_auth import signin_main
import time
# from streamlit_extras.switch_page_button import switch_page
import argparse
from streamlit_extras.stoggle import stoggle
from chess_piece.app_hive import display_for_unAuth_client_user, queen__account_keys, local_gif, mark_down_text, update_queencontrol_theme, progress_bar, page_line_seperator, return_runningbee_gif__save
from chess_piece.king import master_swarm_KING, menu_bar_selection, kingdom__grace_to_find_a_Queen, streamlit_config_colors, local__filepaths_misc, ReadPickleData, PickleData, client_dbs_root
from chess_piece.queen_hive import add_key_to_KING, setup_instance, add_key_to_app, init_pollen_dbs, KINGME, pollen_themes
from custom_button import cust_Button
# import hydralit_components as hc
from pollenq_pages.playground import PlayGround
from pollenq_pages.queens_conscience import queens_conscience
from pollenq_pages.account import account
from ozz.ozz_bee import send_ozz_call
# import sys, importlib
# importlib.reload(sys.modules['pollenq_pages.'])

pd.options.mode.chained_assignment = None
# https://blog.streamlit.io/a-new-streamlit-theme-for-altair-and-plotly/
# https://discuss.streamlit.io/t/how-to-animate-a-line-chart/164/6 ## animiate the Bees Images : )
# https://blog.streamlit.io/introducing-theming/  # change theme colors
# https://extras.streamlit.app
# https://www.freeformatter.com/cron-expression-generator-quartz.html
# http://34.162.236.105:8080/home # dags
# https://docs.google.com/spreadsheets/d/1ddqj-EkO1MluAjDg-U-DyCzJvtFjRN-9SfEYXkB8eNo/edit#gid=0 # track hours
# https://unicode.org/emoji/charts/full-emoji-list.html#1fae0

# scriptname = os.path.basename(__file__)
# queens_chess_piece = os.path.basename(__file__)


def pollenq(instance_pq, admin_pq):
    
    def return_custom_button_nav(hoverText, key, file_path_url="misc/floating-queen-unscreen.gif", height='334'):
        cBq = cust_Button(file_path_url=file_path_url, height=f'{height}px', hoverText=hoverText, key=key)
        if cBq:
            if key in ['queens_conscience', 'qc2']:
                # queens_conscience() # not Working
                st.write("Go To QueensConscience")
                pass
        
        return True

    def setup_page():
        hive_setup, settings_queen, BrokerAPIKeys, YourPublicCharacter, help_me = st.tabs(["Setup Steps:gear:", "Risk Parameters:comet:", "BrokerAPIKeys:old_key:", "Choose A Queen:crown:", "Help:dizzy:"])

        with hive_setup:
            st.title("Create Yourself The QueenTrader")
            # st.subheader("Steps to get your QueenTraderBot")
            cols = st.columns((3,3,3,3))
                            
            # cols = st.columns((5,3,3,2,2,2))
            with cols[0]:
                stoggle("1. Select your Broker",
                "Alpaca is only current supported broker, Create your FREE account at https://app.alpaca.markets/brokerage/new-account"
                )
            with cols[1]:
                stoggle("2. Add your Broker API keys",
                """
                This allows the Queen to place Trades for your portfolio. 
                This will change the way you trade forever...everyone needs an AI
                """
                )
            with cols[2]:
                stoggle("3. Select A Queen",
                """
                Each Queen Offers different trading trading strategies with different levels of customization  
                """
                )
            with cols[3]:
                stoggle("4. Command",
                """
                Select a Queen.TradingModel 
                Trade alongside, make changes, talk with you Queen, Change strategy and Implement! 
                Sit Back and watch your Queen Make You Money $$$
                """
                )

            cols = st.columns((2,2,2,3))

            with cols[0]:
                page_line_seperator('.5')
                st.image(mainpage_bee_png, width=100)
            with cols[1]:
                page_line_seperator('.5')
                st.image(mainpage_bee_png, width=100)
            with cols[2]:
                page_line_seperator('.5')
                st.image(mainpage_bee_png, width=100)
            with cols[3]:
                page_line_seperator('.5')
                # st.write(":honeybee:")
                # cust_Button(file_path_url='misc/chess_board.gif', hoverText=None, key=None)
                return_custom_button_nav(file_path_url='misc/chess_board_king.gif', height='200', hoverText='Queens Conscience', key='qc2')
        
        with BrokerAPIKeys:
            queen__account_keys(PB_App_Pickle=PB_App_Pickle, QUEEN_KING=QUEEN_KING, authorized_user=authorized_user, show_form=True)
            # st.error("Account Needs to be Authoirzed First, Add Keys in QueensConscience")
            pass
        
        with settings_queen:
            st.subheader("QueenTraderBot Settings")
            with st.expander("QueenTraderBot Settings", True):
                mark_down_text(align='left', color=default_text_color, fontsize='23', text='Ensure to Complete Step 1 and an Create Alpaca Account', font=default_font, hyperlink="https://app.alpaca.markets/brokerage/new-account")
                
                # queen_controls__tabs = [""]
                
                cols = st.columns((3,4,1))

                # with st.expander("Risk Levels"):
                with cols[0]:
                    # with st.form("Set How You Wish your Queen to Trade"):
                    st.subheader("Set Your Risk Level")
                # st.write(QUEEN_KING.keys())
                    st.text("How Old are you?")
                    if 'QueenTraders_Bithday' in QUEEN_KING.keys():
                        birthday = st.date_input("Enter your birthday: YYYY/MM/DD")
                    else:
                        birthday = st.date_input("Enter your birthday: YYYY/MM/DD", datetime.date(year=1989, month=4, day=11))
                    
                    yrs_old = datetime.datetime.now().year - birthday.year
                    if QUEEN_KING['age'] == 0:
                        QUEEN_KING['age'] = yrs_old
                    with cols[1]:
                        QUEEN_KING['risk_level'] = st.slider("Risk Level", min_value=1, max_value=10, value=int(QUEEN_KING['risk_level']), help="Shoot for the Moon or Steady as she goes")            
                    with cols[1]:
                        QUEEN_KING['age'] = st.slider("Age..How you Feel to Risk", min_value=1, max_value=100, value=int(QUEEN_KING['age']))     
                    QUEEN_KING['QueenTraders_Bithday'] = birthday
                    
                    
                    # if st.form_submit_button('Save Risk Settings'):
                    if st.button('Save Risk Settings'):
                        PickleData(pickle_file=PB_App_Pickle, data_to_store=QUEEN_KING)
                        return_runningbee_gif__save(title='Risk Saved')
                            
            # with cols[1]:
            with st.expander("Select a Theme, a Personality"):
                update_queencontrol_theme(QUEEN_KING, theme_list)

        with YourPublicCharacter:      
            cols = st.columns((1,1,1))
            with cols[0]:
                # return_custom_button_nav(file_path_url="misc/pawn.png", height='123', hoverText="QUEEN1", key='queen_1')
                set_button = True if QUEEN_KING['queen_tier'] == 'queen_1' else False
                cBq = cust_Button(file_path_url="misc/pawn.png", height=f'100px', hoverText="Tier1 QUEEN", key="queen_1", default=set_button)
                if cBq:
                    QUEEN_KING['queen_tier'] = 'queen_1'
            with cols[1]:
                return_custom_button_nav(file_path_url="misc/knight.png", height='153', hoverText="QUEEN2", key='queen_2')
            with cols[2]:
                return_custom_button_nav(file_path_url="misc/queen_king.png", height='159', hoverText="QUEEN_KING3", key='queen_3')

        with help_me:
            st.write("No Soup for You")
            local_gif(gif_path=flyingbee_grey_gif_path)

    est = pytz.timezone("US/Eastern")

    # images
    MISC = local__filepaths_misc()
    bee_image = MISC['bee_image']
    castle_png = MISC['castle_png']
    bishop_png = MISC['bishop_png']
    queen_png = MISC['queen_png']
    mainpage_bee_png = MISC['mainpage_bee_png']
    floating_queen_gif = MISC['floating_queen_gif']
    chess_board__gif = MISC['chess_board__gif']
    knight_png = MISC['knight_png']
    bishop_unscreen = MISC['bishop_unscreen']
    flyingbee_grey_gif_path = MISC['flyingbee_grey_gif_path']
    alpaca_portfolio_keys_png = MISC['alpaca_portfolio_keys_png']
    
    page_icon = Image.open(bee_image)

    st.set_page_config(
        page_title="pollenq",
        page_icon=page_icon,
        layout="wide",
        initial_sidebar_state='collapsed',
        #  menu_items={
        #      'Get Help': 'https://www.extremelycoolapp.com/help',
        #      'Report a bug': "https://www.extremelycoolapp.com/bug",
        #      'About': "# This is a header. This is an *extremely* cool app!"
        #  }
    )

    # if menu_id == 'pollenq':
    #     pollenq_page()
    #     st.stop()

    # st.write(menu_id)

    ##### STREAMLIT ###
    k_colors = streamlit_config_colors()
    default_text_color = k_colors['default_text_color'] # = '#59490A'
    default_font = k_colors['default_font'] # = "sans serif"
    default_yellow_color = k_colors['default_yellow_color'] # = '#C5B743'


        
    if 'name' in st.session_state and st.session_state['name'] != None:
        auth = True
    else:
        with st.spinner("Verifying Your Scent, Hang Tight"):
            auth = signin_main(page="pollenq")

    with st.spinner("Hello Welcome To pollenq a Kings Queen"):
        prod_name = "LIVE" if st.session_state['production'] else "Sandbox"    
        prod_name_oppiste = "Sandbox" if st.session_state['production']  else "LIVE"        

        switch_env = True if 'menu_id' in st.session_state and st.session_state['menu_id'] == 'sb_liv_switch' else False
        
        live_sb_button = st.sidebar.button(f'Switch to {prod_name_oppiste}', key='pollenq')
        if live_sb_button or switch_env:
            # print(st.session_state['menu_id'])
            st.session_state['production'] = setup_instance(client_username=st.session_state["username"], switch_env=True, force_db_root=False, queenKING=True)
            prod_name = "LIVE" if st.session_state['production'] else "Sandbox"    
            prod_name_oppiste = "Sandbox" if st.session_state['production']  else "LIVE"
            # print('s', prod_name_oppiste)
        
        if st.session_state['authentication_status'] == False:
            menu_id = menu_bar_selection(prod_name_oppiste=False, prod_name=False, prod=False, menu='unAuth')
            display_for_unAuth_client_user()
            st.stop()
  
        if st.session_state['authentication_status'] == True:
            menu_id = menu_bar_selection(prod_name_oppiste=prod_name_oppiste, prod_name=prod_name, prod=st.session_state['production'], menu='main') 
            # print('m', prod_name_oppiste)

            # warning
            if st.session_state['authorized_user'] == False:
                st.info("Your Need to have your account authorized before receiving a QueenTraderBot, Please contact pollenq.queen@gmail.com or click the button below to send a Request")
                client_user_wants_a_queen = st.button("Yes I want a Queen!")
                if client_user_wants_a_queen:
                    st.session_state['init_queen_request'] = True
            

            prod = st.session_state['production']
            authorized_user = st.session_state['authorized_user']            
            
            if admin_pq:
                admin = True
                st.session_state['admin'] = True
            if st.session_state['admin'] == True:
                users_allowed_queen_email, users_allowed_queen_emailname__db = kingdom__grace_to_find_a_Queen()
                admin_client_user = st.sidebar.selectbox('admin client_users', options=users_allowed_queen_email, index=users_allowed_queen_email.index(st.session_state['username']))
                if st.sidebar.button('admin change user'):
                    st.session_state['admin__client_user'] = admin_client_user

    ## Menu Without chess_pieces

    if menu_id == 'Account':
        account(admin_pq=st.session_state['admin'])
        st.stop()

    PB_KING_Pickle = master_swarm_KING(prod=prod)
    KING = ReadPickleData(PB_KING_Pickle)
    
    ## chess_pieces
    db_root = st.session_state['db_root']
    init_pollen = init_pollen_dbs(db_root=db_root, prod=st.session_state['production'], queens_chess_piece='queen')
    PB_QUEEN_Pickle = init_pollen['PB_QUEEN_Pickle']
    PB_App_Pickle = init_pollen['PB_App_Pickle']
    PB_Orders_Pickle = init_pollen['PB_Orders_Pickle']
    PB_QUEENsHeart_PICKLE = init_pollen['PB_QUEENsHeart_PICKLE']
    # PB_KING_Pickle = init_pollen['PB_KING_Pickle']

    QUEENsHeart = ReadPickleData(PB_QUEENsHeart_PICKLE)
    QUEEN_KING = ReadPickleData(pickle_file=PB_App_Pickle)    
    QUEEN_KING = ReadPickleData(pickle_file=PB_App_Pickle)
    QUEEN = ReadPickleData(PB_QUEEN_Pickle)
    # ORDERS = ReadPickleData(PB_Orders_Pickle)
    
    ## add new keys
    APP_req = add_key_to_app(QUEEN_KING)
    QUEEN_KING = APP_req['QUEEN_KING']
    if APP_req['update']:
        PickleData(PB_App_Pickle, QUEEN_KING)
    
    QUEEN_KING['source'] = PB_App_Pickle
    pollen_theme = pollen_themes(KING=KING)
    
    # add new keys
    if st.session_state['admin'] == True:
        KING_req = add_key_to_KING(KING=KING)
        if KING_req.get('update'):
            KING = KING_req['KING']
            PickleData(PB_KING_Pickle, KING)
    
    pollen_theme = pollen_themes(KING=KING)
    theme_list = list(pollen_theme.keys())

    if menu_id == 'QC':
        KING['instance_pq'] = instance_pq
        queens_conscience(QUEEN_KING=QUEEN_KING, QUEEN=QUEEN, KING=KING)
        st.stop()
    if menu_id == 'PlayGround':
        PlayGround(QUEEN=QUEEN)
        st.stop()  

    ## Setup Page
    # if menu_id == 'setup':
    if 'init_queen_request' in st.session_state:
        QUEEN_KING['init_queen_request'] = {'timestamp_est': datetime.datetime.now(est)}
        PickleData(PB_App_Pickle, QUEEN_KING)
        st.success("Hive Master Notified and You should receive contact soon")

    setup_page()

    page_line_seperator('5')


if __name__ == '__main__':
    def createParser():
        parser = argparse.ArgumentParser()
        parser.add_argument ('-admin', default=False)
        parser.add_argument ('-instance', default=False)
        return parser
    parser = createParser()
    namespace = parser.parse_args()
    admin_pq = namespace.admin
    instance_pq = namespace.instance
    try:
        pollenq(instance_pq, admin_pq)
    except Exception as e:
        print(e)