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
from streamlit_extras.switch_page_button import switch_page
import argparse
from streamlit_extras.stoggle import stoggle
from chess_piece.app_hive import send_email, flying_bee_gif, display_for_unAuth_client_user, queen__account_keys, local_gif, mark_down_text, update_queencontrol_theme, progress_bar, page_line_seperator, return_runningbee_gif__save
from chess_piece.king import print_line_of_error, master_swarm_KING, menu_bar_selection, kingdom__grace_to_find_a_Queen, streamlit_config_colors, local__filepaths_misc, ReadPickleData, PickleData, client_dbs_root
from chess_piece.queen_hive import kings_order_rules, return_timestamp_string, return_alpaca_user_apiKeys, refresh_account_info, init_KING, add_key_to_KING, setup_instance, add_key_to_app, init_pollen_dbs, pollen_themes
from custom_button import cust_Button
# import hydralit_components as hc
from pollenq_pages.playground import PlayGround
from pollenq_pages.queens_conscience import queens_conscience
from pollenq_pages.queen import queen
from pollenq_pages.account import account
from pollenq_pages.trading_models import trading_models
from pollenq_pages.pollen_engine import pollen_engine

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


def pollenq(admin_pq):
    try:

        def return_custom_button_nav(hoverText, key, file_path_url="misc/floating-queen-unscreen.gif", height='334'):
            cBq = cust_Button(file_path_url=file_path_url, height=f'{height}px', hoverText=hoverText, key=key)
            if cBq:
                if key in ['queens_conscience', 'qc2']:
                    # queens_conscience() # not Working
                    st.write("Go To QueensConscience")
                    pass
            
            return True

        def setup_page():
            cols = st.columns((3,3))
            with cols[0]:
                st.title("Automate Your Portfolio With a AI.BeeBot")
            with cols[1]:
                # cust_Button(file_path_url='misc/queen_flair.gif', height='50px', hoverText='')
                return_custom_button_nav(file_path_url='misc/chess_board_king.gif', height='150', hoverText='Queens Conscience', key='qc2')

            hive_setup, settings_queen, BrokerAPIKeys, YourPublicCharacter, help_me = st.tabs(["Setup Steps:gear:", "Risk Parameters:comet:", "BrokerAPIKeys:old_key:", "Choose A Queen:crown:", "Help:dizzy:"])

            with hive_setup:
                # st.subheader("Steps to get your QueenTraderBot")
                cols = st.columns((1,1,1))
                                
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
                # with cols[3]:
                #     stoggle("4. Command",
                #     """
                #     Select a Queen.TradingModel 
                #     Trade alongside, make changes, talk with you Queen, Change strategy and Implement! 
                #     Sit Back and watch your Queen Make You Money $$$
                #     """
                #     )

                cols = st.columns((1,1,1))

                with cols[0]:
                    page_line_seperator('.5')
                    st.image(mainpage_bee_png, width=100)
                with cols[1]:
                    page_line_seperator('.5')
                    st.image(mainpage_bee_png, width=100)
                with cols[2]:
                    page_line_seperator('.5')
                    st.image(mainpage_bee_png, width=100)
                # with cols[3]:
                #     page_line_seperator('.5')
                #     # st.write(":honeybee:")
                    # cust_Button(file_path_url='misc/chess_board.gif', hoverText=None, key=None)
                    # return_custom_button_nav(file_path_url='misc/chess_board_king.gif', height='200', hoverText='Queens Conscience', key='qc2')
            
            with BrokerAPIKeys:
                queen__account_keys(PB_App_Pickle=st.session_state['PB_App_Pickle'], QUEEN_KING=QUEEN_KING, authorized_user=authorized_user, show_form=True)
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
                            PickleData(pickle_file=st.session_state['PB_App_Pickle'], data_to_store=QUEEN_KING)
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

        def add_new_trading_models_settings(QUEEN_KING):
            all_models = QUEEN_KING['king_controls_queen']['symbols_stars_TradingModel']
            latest_kors = kings_order_rules()
            latest_rules = latest_kors.keys()
            save = False
            new_rules_confirmation = {}
            for ticker, t_model in all_models.items():
                missing_rules = [i for i in latest_rules if i not in t_model.keys()]
                if len(missing_rules) > 0:
                    save = True
                    new_rules_confirmation[ticker] = []
                    for new_rule in missing_rules:
                        QUEEN_KING['king_controls_queen']['symbols_stars_TradingModel'][ticker].update({new_rule: latest_kors.get(new_rule)})
                        new_rules_confirmation[ticker].append(new_rule)
                        # print("New Rule Added: ", new_rule)
                        # st.write("New Rule Added: ", new_rule)

            if save:
                st.write(new_rules_confirmation)
                PickleData(st.session_state["PB_App_Pickle"], QUEEN_KING)
            
            return QUEEN_KING
        
        est = pytz.timezone("US/Eastern")

        # images
        MISC = local__filepaths_misc()
        bee_image = MISC['bee_image']
        mainpage_bee_png = MISC['mainpage_bee_png']
        flyingbee_grey_gif_path = MISC['flyingbee_grey_gif_path']
        
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


        ##### STREAMLIT ###
        k_colors = streamlit_config_colors()
        default_text_color = k_colors['default_text_color'] # = '#59490A'
        default_font = k_colors['default_font'] # = "sans serif"
        default_yellow_color = k_colors['default_yellow_color'] # = '#C5B743'


        with st.spinner("Verifying Your Scent, Hang Tight"):
            signin_main(page="pollenq")
        
        if st.session_state['authentication_status'] != True: ## None or False
            # menu_id = menu_bar_selection(prod_name_oppiste=False, prod_name=False, prod=False, menu='unAuth', ac_info=False)
            display_for_unAuth_client_user()
            st.stop()

        with st.spinner("Hello Welcome To pollenq a Kings Queen"):

            prod_name = "LIVE" if st.session_state['production'] else "Sandbox"    
            prod_name_oppiste = "Sandbox" if st.session_state['production']  else "LIVE"        

            live_sb_button = st.sidebar.button(f'Switch to {prod_name_oppiste}', key='pollenq')
            if live_sb_button:
                st.session_state['production'] = setup_instance(client_username=st.session_state["username"], switch_env=True, force_db_root=False, queenKING=True)
                st.experimental_rerun()

            prod = st.session_state['production']
            authorized_user = st.session_state['authorized_user']            
            
            PB_KING_Pickle = master_swarm_KING(prod=prod)
            KING = ReadPickleData(PB_KING_Pickle)
            
            if admin_pq:
                admin = True
                st.session_state['admin'] = True
            if st.session_state['admin'] == True:
                users_allowed_queen_email, users_allowed_queen_emailname__db = kingdom__grace_to_find_a_Queen()
                admin_client_user = st.sidebar.selectbox('admin client_users', options=users_allowed_queen_email, index=users_allowed_queen_email.index(st.session_state['username']))
                if st.sidebar.button('admin change user'):
                    st.session_state['admin__client_user'] = admin_client_user
                    st.session_state["production"] = False
                    st.session_state['production'] = setup_instance(client_username=admin_client_user, switch_env=False, force_db_root=False, queenKING=True)

            # if st.session_state['admin']:
            #     with st.sidebar:
            #         if st.button('Re-Init KING'):
            #             print("init KING")
            #             KING = init_KING()
            #             PickleData(PB_KING_Pickle, KING)


            QUEENsHeart = ReadPickleData(pickle_file=st.session_state['PB_QUEENsHeart_PICKLE'])
            QUEEN_KING = ReadPickleData(pickle_file=st.session_state['PB_App_Pickle'])

            try:
                api = return_alpaca_user_apiKeys(QUEEN_KING=QUEEN_KING, authorized_user=authorized_user, prod=st.session_state['production'])
                ac_info = refresh_account_info(api=api)['info_converted']
            except Exception as e:
                st.error(e)
                ac_info = False
            
            hide_streamlit_markers = False if st.sidebar.button('show dev-ham') else True
            menu_id = menu_bar_selection(prod_name_oppiste=prod_name_oppiste, prod_name=prod_name, prod=st.session_state['production'], menu='main', ac_info=ac_info, hide_streamlit_markers=hide_streamlit_markers) 
            if st.session_state["admin"]:
                st.write('admin:', st.session_state["admin"])
            
            ## add new keys
            QUEEN_KING = add_new_trading_models_settings(QUEEN_KING)

            APP_req = add_key_to_app(QUEEN_KING)
            QUEEN_KING = APP_req['QUEEN_KING']
            if APP_req['update']:
                PickleData(st.session_state['PB_App_Pickle'], QUEEN_KING)
            
            QUEEN_KING['source'] = st.session_state['PB_App_Pickle']
            pollen_theme = pollen_themes(KING=KING)
            
            # add new keys
            if st.session_state['admin'] == True:
                KING_req = add_key_to_KING(KING=KING)
                if KING_req.get('update'):
                    KING = KING_req['KING']
                    PickleData(PB_KING_Pickle, KING)
            
            pollen_theme = pollen_themes(KING=KING)
            theme_list = list(pollen_theme.keys())

            if 'init_queen_request' in st.session_state:
                QUEEN_KING['init_queen_request'] = {'timestamp_est': datetime.datetime.now(est)}
                st.success("Hive Master Notified and You should receive contact soon")

        # cols = st.columns((4,8,4))
        if prod:
            mark_down_text(text='LIVE', fontsize='23', align='left', color="Green", sidebar=True)
            flying_bee_gif(sidebar=True)

        else:
            mark_down_text(text='SandBox', fontsize='23', align='left', color="Red", sidebar=True)
            local_gif(gif_path=flyingbee_grey_gif_path, sidebar=True)

        if authorized_user and 'pollenq' in menu_id: 
            queens_conscience()
            st.stop()
        if menu_id == 'QC':
            queen()
            st.stop()
        if menu_id == 'TradingModels':
            trading_models()
            st.stop()
        if menu_id == 'PlayGround':
            PlayGround()
            st.stop()  
        if menu_id == 'Account':
            account(st=st)
            setup_page()
            st.stop()
        if menu_id == 'pollen_engine':
            acct_info = refresh_account_info(api=api)
            log_dir = os.path.join(st.session_state['db_root'], 'logs')
            pollen_engine(st=st, pd=pd, acct_info=acct_info, log_dir=log_dir)
            st.stop()
        # else:
        #     setup_page()

        page_line_seperator('5')
    except Exception as e:
        print(e, print_line_of_error(), return_timestamp_string())

if __name__ == '__main__':
    def createParser():
        parser = argparse.ArgumentParser()
        parser.add_argument ('-admin', default=False)
        # parser.add_argument ('-instance', default=False)
        return parser
    parser = createParser()
    namespace = parser.parse_args()
    admin_pq = namespace.admin
    # instance_pq = namespace.instance
    try:
        pollenq(admin_pq)
    except Exception as e:
        print(e)