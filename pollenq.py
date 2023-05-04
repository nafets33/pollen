# pollenq
import pandas as pd
import logging
import os
import pandas as pd
from datetime import datetime, timedelta, date
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
from chess_piece.workerbees import queen_workerbees
from chess_piece.workerbees_manager import workerbees_multiprocess_pool
from chess_piece.app_hive import admin_queens_active, standard_AGgrid, read_QUEEN, pollenq_button_source, trigger_airflow_dag, send_email, flying_bee_gif, display_for_unAuth_client_user, queen__account_keys, local_gif, mark_down_text, update_queencontrol_theme, progress_bar, page_line_seperator, return_runningbee_gif__save
from chess_piece.king import master_swarm_QUEENBEE, kingdom__global_vars, hive_master_root, print_line_of_error, master_swarm_KING, menu_bar_selection, kingdom__grace_to_find_a_Queen, streamlit_config_colors, local__filepaths_misc, ReadPickleData, PickleData, client_dbs_root
from chess_piece.queen_hive import initialize_orders, create_QueenOrderBee, generate_chessboards_trading_models, generate_TradingModel, stars, return_queen_controls, generate_chess_board, kings_order_rules, return_timestamp_string, return_alpaca_user_apiKeys, refresh_account_info, init_KING, add_key_to_KING, setup_instance, add_key_to_app, init_pollen_dbs, pollen_themes
from custom_button import cust_Button
from custom_text import custom_text, TextOptionsBuilder

# import hydralit_components as hc
from pollenq_pages.playground import PlayGround
from pollenq_pages.queens_conscience import queens_conscience
from pollenq_pages.queen import queen
from pollenq_pages.account import account
from pollenq_pages.trading_models import trading_models
from pollenq_pages.pollen_engine import pollen_engine
import hydralit_components as hc

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
# C:\Users\sstapinski\AppData\Roaming\Code\User\settings.json
# scriptname = os.path.basename(__file__)
# queens_chess_piece = os.path.basename(__file__)


def pollenq(admin_pq):
    try:
        king_G = kingdom__global_vars()
        import subprocess
        import sys
        def refresh_workerbees(QUEENBEE, QUEEN_KING, backtesting=False, macd=None, reset_only=True, run_all_pawns=False):
            
            with st.form("workerbees refresh"):
                try:
                    if st.session_state['admin']:
                        reset_only = st.checkbox("reset_only", reset_only)
                        backtesting = st.checkbox("backtesting", backtesting)
                        run_all_pawns = st.checkbox("run_all_pawns", run_all_pawns)
                        qcp_options = list(QUEENBEE['workerbees'].keys())
                        pieces = st.multiselect('qcp', options=qcp_options, default=['castle'])

                        refresh = st.form_submit_button("Run WorkerBees", use_container_width=True)
                        if refresh:
                            with st.spinner("Running WorkerBees"):
                                s = datetime.now(est)
                                if backtesting:
                                    subprocess.run([f"{sys.executable}", os.path.join(hive_master_root(), 'macd_grid_search.py')])
                                else:
                                    queen_workerbees(qcp_s=pieces, 
                                                        prod=QUEEN_KING.get('prod'), 
                                                        reset_only=reset_only, 
                                                        backtesting=False, 
                                                        run_all_pawns=run_all_pawns, 
                                                        macd=None)
                                st.success("WorkerBees Completed")
                                e = datetime.now(est)
                                st.write("refresh time ", (e - s).total_seconds())
                except Exception as e:
                    print(e, print_line_of_error())

        def refresh_workerbees_manager(QUEEN_KING, backtesting=False, macd=None, reset_only=True, run_all_pawns=False):
            with st.form("workerbees refresh"):
                if st.session_state['admin']:
                    reset_only = st.checkbox("reset_only", reset_only)
                    backtesting = st.checkbox("backtesting", backtesting)
                    run_all_pawns = st.checkbox("run_all_pawns", run_all_pawns)

                    refresh = st.form_submit_button("Run WorkerBees", use_container_width=True)
                    if refresh:
                        with st.spinner("Running WorkerBees"):
                            s = datetime.now(est)
                            workerbees_multiprocess_pool(qcp_s=['castle', 'knight', 'bishop'], 
                                                prod=QUEEN_KING.get('prod'), 
                                                reset_only=reset_only, )
                            st.success("WorkerBees Completed")
                            e = datetime.now(est)
                            st.write("refresh time ", (e - s).total_seconds())
        
        def return_custom_button_nav(hoverText, key, file_path_url="misc/floating-queen-unscreen.gif", height='334'):
            cBq = cust_Button(file_path_url=file_path_url, height=f'{height}px', hoverText=hoverText, key=key)
            if cBq:
                if key in ['queens_conscience', 'qc2']:
                    # queens_conscience() # not Working
                    st.write("Go To QueensConscience")
                    pass
            
            return True

        def setup_page():
            try:
                cols = st.columns((3,3))
                with cols[0]:
                    st.title("Automate Your Portfolio With a AI.BeeBot")
                with cols[1]:
                    cust_Button(file_path_url='misc/chess_board_king.gif', height='150px', hoverText='')
                    # return_custom_button_nav(file_path_url='misc/chess_board_king.gif', height='150', hoverText='Queens Conscience', key='qc2')

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
                                birthday = st.date_input("Enter your birthday: YYYY/MM/DD", date(year=1989, month=4, day=11))
                            
                            yrs_old = datetime.now().year - birthday.year
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
                        set_button = True if QUEEN_KING['queen_tier'] == 'queen_1' else False
                        cBq = cust_Button(file_path_url="misc/pawn.png", height=f'100px', hoverText="Tier1 QUEEN", key="queen_1", default=set_button)
                        if cBq:
                            QUEEN_KING['queen_tier'] = 'queen_1'

                with help_me:
                    st.write("No Soup for You")
                    local_gif(gif_path=flyingbee_grey_gif_path)
            except Exception as e:
                print('setup', e, print_line_of_error())

        def add_new_trading_models_settings(QUEEN_KING, active_orders=False):
            # try:
            save = False
            all_models = QUEEN_KING['king_controls_queen']['symbols_stars_TradingModel']
            lastest_ticker_key = []
            lastest_tframe_keys = []
            latest_kors = kings_order_rules()
            latest_rules = latest_kors.keys()
            new_rules_confirmation = {}
            # ipdb.set_trace()
            for ticker, t_model in all_models.items():
                # 3 level check, ticker, tframe, blocktime
                # ipdb.set_trace()
                for ticker_star, star_model in t_model['stars_kings_order_rules'].items(): #['trigbees'].items():
                    # add new keys
                    for trigbee, trigbee_model in star_model['trigbees'].items():
                        # add new keys
                        for blocktime, waveblock_kor in trigbee_model.items():
                            missing_rules = [i for i in latest_rules if i not in waveblock_kor.keys()]                
                            # print(missing_rules)
                            if len(missing_rules) > 0:
                                save = True
                                new_rules_confirmation[ticker] = []
                                for new_rule in missing_rules:
                                    QUEEN_KING['king_controls_queen']['symbols_stars_TradingModel'][ticker]['stars_kings_order_rules'][ticker_star]['trigbees'][trigbee][blocktime].update({new_rule: latest_kors.get(new_rule)})
                                    msg = f'New Rule Added: , {ticker}{ticker_star}{trigbee}{blocktime}{new_rule}'
                                    new_rules_confirmation[ticker].append(new_rule)
                                    # print(f'New Rule Added: , {ticker}{new_rule}')
                                    # st.write(f'New Rule Added: , {ticker}{new_rule}')

            if save:
                st.write(new_rules_confirmation)
                PickleData(st.session_state["PB_App_Pickle"], QUEEN_KING)
            
            return QUEEN_KING

        def add_new_kor__to_active_orders(QUEEN, QUEEN_KING):
            # try:
            save = False
            all_orders = QUEEN['queen_orders']
            active_orders = all_orders[all_orders['queen_order_state'].isin(king_G.get('active_queen_order_states'))].copy()
            
            all_models = QUEEN_KING['king_controls_queen']['symbols_stars_TradingModel']
            lastest_ticker_key = []
            lastest_tframe_keys = []
            latest_kors = kings_order_rules()
            latest_rules = latest_kors.keys()
            new_rules_confirmation = {}
            # ipdb.set_trace()
            for q_order in active_orders:
                korules = q_order.get('order_rules')
                missing_rules = [i for i in latest_rules if i not in korules.keys()]    
                ticker = korules.get("symbol")
                client_order_id = korules.get('client_order_id')
                if len(missing_rules) > 0:
                    save = True
                    new_rules_confirmation[ticker] = []
                    for new_rule in missing_rules:
                        QUEEN['queen_orders'].at[client_order_id, 'order_rules'].update({new_rule: latest_kors.get(new_rule)})
                        new_rules_confirmation[ticker].append(new_rule)
                        print(f'New Rule Added: , {ticker}{new_rule}')
                        st.write(f'New Rule Added: , {ticker}{new_rule}')

            # if save:
            #     st.write(new_rules_confirmation)
            #     PickleData(st.session_state["PB_App_Pickle"], QUEEN_KING)
            
            return QUEEN
            
        def refresh_chess_board__button(QUEEN_KING):
            refresh = st.button("Reset Chess Board",  use_container_width=True)

            if refresh:
                QUEEN_KING['chess_board'] = generate_chess_board()
                PickleData(pickle_file=st.session_state['PB_App_Pickle'], data_to_store=QUEEN_KING)
                st.success("Generated Default Chess Board")
                time.sleep(1)
                st.experimental_rerun()
                    
            return True

        def refresh_queen_controls_button(QUEEN_KING):
            refresh = st.button("Reset ALL QUEEN controls", use_container_width=True)

            if refresh:
                QUEEN_KING['king_controls_queen'] = return_queen_controls(stars)
                
                PickleData(pickle_file=st.session_state['PB_App_Pickle'], data_to_store=QUEEN_KING)
                st.success("All Queen Controls Reset")
                st.experimental_rerun()
                    
            return True

        def refresh_trading_models_button(QUEEN_KING):
            refresh = st.button("Reset All Trading Models", use_container_width=True)

            if refresh:
                chessboard = QUEEN_KING['chess_board']
                tradingmodels = generate_chessboards_trading_models(chessboard)
                QUEEN_KING['king_controls_queen']['symbols_stars_TradingModel'] = tradingmodels
                
                PickleData(pickle_file=st.session_state['PB_App_Pickle'], data_to_store=QUEEN_KING)
                st.success("All Queen.TradingModels Reset")
                st.experimental_rerun()
                    
            return True

        def refresh_swarmqueen_workerbees(QUEEN_KING):
            refresh = st.button("Reset All Swarm QUEEN Workerbees to New chessboard", use_container_width=True)

            if refresh:
                chessboard = generate_chess_board()
                QUEEN_KING['qcp_workerbees'] = chessboard
                
                PickleData(pickle_file=st.session_state['PB_App_Pickle'], data_to_store=QUEEN_KING)
                with st.spinner("Saving Changes"):
                    st.success("Swarm Workerbees Reset, Refreshing Page One Moment...")
                    time.sleep(3)
                    st.experimental_rerun()
        
        def refresh_swarmqueen_qcp_workerbees(QUEEN, QUEEN_KING):
            refresh = st.button("Save curernt QUEENKING workers to QUEEN", use_container_width=True)

            if refresh:
                # check to make sure QUEEN is asleep before making change!!!!
                QUEEN['workerbees'] = QUEEN_KING['qcp_workerbees']
                
                PickleData(pickle_file=st.session_state['PB_Queen_Pickle'], data_to_store=QUEEN)
                with st.spinner("Saving Changes"):
                    st.success("Refreshed. Refreshing Page One Moment...")
                    time.sleep(2)
                    st.experimental_rerun()
        
        def refresh_queen_orders(QUEEN):
            refresh = st.button("Reset All Queen Orders", use_container_width=True)

            if refresh:
                QUEEN['queen_orders'] = pd.DataFrame([create_QueenOrderBee(queen_init=True)]).set_index("client_order_id")
                PickleData(pickle_file=st.session_state['PB_QUEEN_Pickle'], data_to_store=QUEEN)
                st.success("Orders Reset")
                st.experimental_rerun()

        def stash_queen(QUEEN):
            refresh = st.button("Stash All Queen Orders", use_container_width=True)

            if refresh:
                queen_logs = os.path.join(st.session_state['db_root'], '/logs/logs/queens')
                queen_log_filename = len(os.listdir(queen_logs))
                queen_log_filename = f'{len(os.listdir(queen_logs)) + 1}_queen.pkl'
                queen_logs = os.path.join(st.session_state['db_root'], queen_log_filename)
                PickleData(pickle_file=st.session_state['PB_App_Pickle'], data_to_store=QUEEN)
                st.success("Queen Stashed")

        def queenbee_online(cols, QUEENsHeart, admin, dag, api_failed, prod):
            # from airflow.dags.dag_queenbee_prod import run_trigger_dag

            def trigger_queen_vars(dag, client_username, last_trig_date=datetime.now(est)):
                return {'dag': dag, 'last_trig_date': last_trig_date, 'client_user': client_username}
            try:
                users_allowed_queen_email = KING['users'].get('client_user__allowed_queen_list')
                now = datetime.now(est)

                if dag =='run_queenbee':
                    def queen_checks():
                        if 'chess_board__revrec' not in QUEEN_KING.keys():
                            st.warning("You Need to Save your Chess Board before Proceeding")
                            return False
                        if (now - QUEEN_KING['trigger_queen'].get('last_trig_date')).total_seconds() < 60:
                            st.write("Waking up your Queen")
                            st.image(QUEEN_KING['character_image'], width=100)
                            return False
                
                        if api_failed:
                            st.error("you need to setup your Broker Queens to Turn on your Queen See Account Keys Below")
                            return False

                        if 'heartbeat_time' not in QUEENsHeart.keys():
                            st.error("You Need a Queen")
                            return False
                        
                        return True
                    
                    if queen_checks() == False:
                        return False

                    
                    if (now - QUEENsHeart['heartbeat_time']).total_seconds() > 60:
                        # st.write("YOUR QUEEN if OFFLINE")
                        # st.error("Your Queen Is Asleep Wake Her UP!")
                        with cols[1]:
                            local_gif(gif_path=flyingbee_grey_gif_path)
                            wake_up_queen_button = st.button("Your Queen Is Asleep Wake Her UP!")
                        # wake_up_queen_button = cust_Button(file_path_url="misc/sleeping_queen_gif.gif", height='50px', key='b')
                        if wake_up_queen_button and st.session_state['authorized_user']:
                            # check to ensure queen is offline before proceeding 
                            if (now - QUEENsHeart['heartbeat_time']).total_seconds() < 60:
                                return False
                            
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
                            PickleData(pickle_file=st.session_state['PB_App_Pickle'], data_to_store=QUEEN_KING)
                            # switch_page("pollenq")
                            st.experimental_rerun()
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
            except Exception as e:
                print(e, print_line_of_error())

        def portfolio_header__QC(acct_info):
            try:
           
                with st.expander("Portfolio Value: " + '${:,.2f}'.format(acct_info['portfolio_value']),  False):
                    cols = st.columns((3,2))
                    # st.write(":heavy_minus_sign:" * 34)

                    mark_down_text(fontsize='18', text="Total Buying Power: " + '${:,.2f}'.format(acct_info['buying_power']))

                    mark_down_text(fontsize='15', text="last_equity: " + '${:,.2f}'.format(acct_info['last_equity']))

                    mark_down_text(fontsize='15', text="portfolio_value: " + '${:,.2f}'.format(acct_info['portfolio_value']))

                    mark_down_text(fontsize='15', text="Cash: " + '${:,.2f}'.format(acct_info['cash']))

                    cols = st.columns((1,2,1))
                    with cols[1]:
                        mark_down_text(fontsize='12', text="Total Fees: " + '${:,.2f}'.format(acct_info['accrued_fees']))


                return True
            except Exception as e:
                er, erline=print_line_of_error()
                print(erline)

        def admin_check(admin_pq):
            if admin_pq:
                admin = True
                st.session_state['admin'] = True
            if st.session_state['admin'] == True:
                with st.sidebar:
                    with st.expander("admin user"):
                        admin_client_user = st.selectbox('admin client_users', options=users_allowed_queen_email, index=users_allowed_queen_email.index(st.session_state['username']))
                        if st.button('admin change user', use_container_width=True):
                            st.session_state['admin__client_user'] = admin_client_user
                            st.session_state["production"] = False
                            st.session_state['production'] = setup_instance(client_username=admin_client_user, switch_env=False, force_db_root=False, queenKING=True)
                            st.experimental_rerun()

            return True

        def admin_send_queen_airflow(KING):
            if st.session_state['admin']:
                with st.form('admin queens'):
                    prod_queen = st.checkbox('prod', False)
                    client_user_queen = st.selectbox('client_user_queen', list(KING['users'].get('client_user__allowed_queen_list')))
                    if st.form_submit_button("Send Queen"):
                        trigger_airflow_dag(dag='run_queenbee', client_username=client_user_queen, prod=prod_queen)

            return True
        
        
        ##### QuantQueen #####

        est = pytz.timezone("US/Eastern")
        # cust_Button(file_path_url='misc/chess_board.gif', hoverText=None, key=None)

        pq_buttons = pollenq_button_source()
        s = datetime.now(est)

        # images
        MISC = local__filepaths_misc()
        MISC_cb = local__filepaths_misc(jpg_root=os.path.join(hive_master_root(), '/custom_button/frontend/build/misc' ))
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


        ##### STREAMLIT #####

        if 'refresh_times' not in st.session_state:
            st.session_state['refresh_times'] = 0
            pq_buttons['chess_board'] = True

        k_colors = streamlit_config_colors()
        default_text_color = k_colors['default_text_color'] # = '#59490A'
        default_font = k_colors['default_font'] # = "sans serif"
        default_yellow_color = k_colors['default_yellow_color'] # = '#C5B743'


        with st.spinner("Verifying Your Scent, Hang Tight"):
            signin_main(page="pollenq")
        
        if st.session_state['authentication_status'] != True: ## None or False
            display_for_unAuth_client_user()
            st.stop()

        with st.spinner("Hello Welcome To pollenq a Kings Queen"):

            prod = st.session_state['production']
            authorized_user = st.session_state['authorized_user']
            prod_name = "LIVE" if st.session_state['production'] else "Sandbox"    
            prod_name_oppiste = "Sandbox" if st.session_state['production']  else "LIVE"        

            live_sb_button = st.sidebar.button(f'Switch to {prod_name_oppiste}', key='pollenq', use_container_width=True)
            if live_sb_button:
                st.session_state['production'] = setup_instance(client_username=st.session_state["username"], switch_env=True, force_db_root=False, queenKING=True)
                st.experimental_rerun()



            ####### Welcome to Pollen ##########
            # use API keys from user
            
            print("KingBee & QueenBee")
            PB_QUEENBEE_Pickle = master_swarm_QUEENBEE(prod=prod)
            QUEENBEE = ReadPickleData(PB_QUEENBEE_Pickle)
            QUEENBEE['source'] = PB_QUEENBEE_Pickle
            KING, users_allowed_queen_email, users_allowed_queen_emailname__db = kingdom__grace_to_find_a_Queen()
            admin_check(admin_pq)
            # PB_KING_Pickle = master_swarm_KING(prod=prod)
            # KING = ReadPickleData(PB_KING_Pickle)
            # KING['source'] = PB_KING_Pickle
            
            # with st.sidebar:
            #     st.write("testing fastpi")
            # to_builder = TextOptionsBuilder.create()
            # to_builder.configure_background_color("green")
            # to_builder.configure_text_color("#0d233a")
            # to_builder.configure_font_style("italic")
            # to = to_builder.build()
            # custom_text(api="http://localhost:8000/api/data/text", text_size = 17, refresh_sec =2,refresh_cutoff_sec =20,text_option=to)

            hey = st.info("Sandbox Paper Money Account") if st.session_state['production'] == False else ""
            # cols = st.columns((1,10,1)) # 6
            # with cols[0]:
            with st.sidebar:
                cust_Button("misc/bee.jpg", hoverText='admin users', key='admin_users', height='34px')
                hide_streamlit_markers = False if st.button('show_dev-ham', use_container_width=True) else True
                cust_Button("misc/bee.jpg", hoverText='send queen', key='admin_queens', height='34px')
            
            # with cols[1]:
            menu_id = menu_bar_selection(prod_name_oppiste=prod_name_oppiste, prod_name=prod_name, prod=st.session_state['production'], menu='main', hide_streamlit_markers=hide_streamlit_markers) 
            # with cols[2]:

            if st.session_state['admin_queens']:
                admin_send_queen_airflow(KING)
            if st.session_state['admin_users']:
                admin_queens_active(KING.get('source'), KING)

            cols = st.columns((2,2,2,2,2,2))
            # print("QUEEN_KING")
            if authorized_user:
                QUEEN_KING = ReadPickleData(pickle_file=st.session_state['PB_App_Pickle'])
                QUEEN_KING['prod'] = st.session_state['production']          
                QUEEN = read_QUEEN()

            if menu_id == 'PlayGround':
                print("PLAYGROUND")
                PlayGround()
                st.stop()


            # print("API")
            if st.sidebar.button('show_keys'):
                queen__account_keys(PB_App_Pickle=st.session_state['PB_App_Pickle'], QUEEN_KING=QUEEN_KING, authorized_user=authorized_user, show_form=True) #EDRXZ Maever65teo

            try:
                api = return_alpaca_user_apiKeys(QUEEN_KING=QUEEN_KING, authorized_user=authorized_user, prod=st.session_state['production'])
                if api == False:
                    queen__account_keys(PB_App_Pickle=st.session_state['PB_App_Pickle'], QUEEN_KING=QUEEN_KING, authorized_user=authorized_user, show_form=True) #EDRXZ Maever65teo
                    api_failed = True
                    st.stop()
                else:
                    try:
                        api_failed = False
                        snapshot = api.get_snapshot("SPY") # return_last_quote from snapshot
                    except Exception as e:
                        # requests.exceptions.HTTPError: 403 Client Error: Forbidden for url: https://data.alpaca.markets/v2/stocks/SPY/snapshot
                        st.error("API Keys failed! You need to update, Please Go to your Alpaca Broker Account to Generate API Keys")
                        queen__account_keys(PB_App_Pickle=st.session_state['PB_App_Pickle'], QUEEN_KING=QUEEN_KING, authorized_user=authorized_user, show_form=True) #EDRXZ Maever65teo
                        api_failed = True

                alpaca_acct_info = refresh_account_info(api=api)
                acct_info = alpaca_acct_info.get('info_converted')
                acct_info_raw = alpaca_acct_info.get('info')
                init_api_orders_start_date =(datetime.now() - timedelta(days=100)).strftime("%Y-%m-%d")
                init_api_orders_end_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
                api_orders = initialize_orders(api, init_api_orders_start_date, init_api_orders_end_date)
                queen_orders_open = api_orders.get('open')
                queen_orders_closed = api_orders.get('closed')
                api_vars = {'acct_info': acct_info, 'api_orders': api_orders}
            except Exception as e:
                st.error(e)
                acct_info = False
                st.session_state['production'] = False
                queen__account_keys(PB_App_Pickle=st.session_state['PB_App_Pickle'], QUEEN_KING=QUEEN_KING, authorized_user=authorized_user, show_form=True) #EDRXZ Maever65teo
                st.stop()

            # print("MENU Buttons")
            def menu_buttons():
                # sb = st.sidebar
                off_size = 54
                on_size = 54
                # with sb:
                cols = st.columns(7)
                with cols[0]:
                    wb = hc.option_bar(option_definition=pq_buttons.get('workerbees_option_data'),title='WorkerBees', key='workerbees_m', horizontal_orientation=True) #,override_theme=over_theme,font_styling=font_fmt,horizontal_orientation=True)   
                    st.session_state['workerbees'] = True if st.session_state['workerbees_m'] == 'workerbees' else False
                    # height = on_size if 'workerbees' in st.session_state and st.session_state['workerbees'] == True else off_size
                    # cust_Button("misc/power.png", hoverText='WorkerBees', key='workerbees', default=False, height=f'{height}px') # "https://cdn.onlinewebfonts.com/svg/img_562964.png"
                    # st.write(wb)
                    # st.write(st.session_state)
                    #     # if st.session_state['admin']:
                    #     with st.expander("WorkerBees Tools"):
                    #         refresh_workerbees(QUEEN_KING)
                    #     with cols[0]:
                with cols[1]:
                    hc.option_bar(option_definition=pq_buttons.get('option_data_orders'),title='Orders', key='orders_m', horizontal_orientation=True) #,override_theme=over_theme,font_styling=font_fmt,horizontal_orientation=True)
                    st.session_state['orders'] = True if st.session_state['orders_m'] == 'orders' else False
                    # height = on_size if 'orders' in st.session_state and st.session_state['orders'] == True else off_size
                    # cust_Button("misc/knight_pawn.png", hoverText='Orders', key='orders', default=False, height=f'{height}px') # "https://cdn.onlinewebfonts.com/svg/img_562964.png"
                with cols[2]:
                    hc.option_bar(option_definition=pq_buttons.get('board_option_data'),title='Board', key='chess_board_m', horizontal_orientation=True) #,override_theme=over_theme,font_styling=font_fmt,horizontal_orientation=True)
                    st.session_state['chess_board'] = True if st.session_state['chess_board_m'] in ['admin_workerbees', 'chess_board'] else False
                    
                    # height = on_size if 'chess_board' in st.session_state and st.session_state['chess_board'] == True else off_size
                    # cust_Button("https://cdn.onlinewebfonts.com/svg/img_562964.png", hoverText='Chess Board', key='chess_board', height=f'{height}px', default=False)
                    # if st.session_state['chess_board']:
                    #     hc.option_bar(option_definition=pq_buttons.get('option_data'),title='Board', key='admin_workerbees', horizontal_orientation=True) #,override_theme=over_theme,font_styling=font_fmt,horizontal_orientation=True)
                with cols[3]:
                    height = on_size if 'queens_mind' in st.session_state and st.session_state['queens_mind'] == True else off_size
                    cust_Button("https://www.pngall.com/wp-content/uploads/2016/03/Chess-Free-PNG-Image.png", hoverText='Trading Models', key='queens_mind', height=f'{height}px')
                    # if st.session_state['queens_mind']:
                    #     hc.option_bar(option_definition=pq_buttons.get('option_data_qm'),title='Models', key='queens_mind_toggle', horizontal_orientation=True) #,override_theme=over_theme,font_styling=font_fmt,horizontal_orientation=True)

                with cols[4]:
                    # hc.option_bar(option_definition=pq_buttons.get('charts_option_data'),title='Board', key='charts_m', horizontal_orientation=True) #,override_theme=over_theme,font_styling=font_fmt,horizontal_orientation=True)
                    # st.session_state['charts'] = True if st.session_state['charts_m'] in ['charts_id'] else False
                    
                    height = on_size if 'charts' in st.session_state and st.session_state['charts'] == True else off_size
                    cust_Button("misc/charts.png", hoverText='Charts', key='charts', height=f'{height}px', default=False)
                    # if st.session_state['charts']:
                    #     hc.option_bar(option_definition=pq_buttons.get('charts_option_data'),title='Charts', key='charts_toggle', horizontal_orientation=True) #,override_theme=over_theme,font_styling=font_fmt,horizontal_orientation=True)

                with cols[5]:
                    height = on_size if 'the_flash' in st.session_state and st.session_state['the_flash'] == True else off_size
                    cust_Button("misc/power_gif.gif", hoverText='The Flash', key='the_flash', height=f'{height}px')
                
                with cols[6]:               
                    height = on_size if 'waves' in st.session_state and st.session_state['waves'] == True else off_size
                    cust_Button("misc/waves.png", hoverText='Waves', key='waves', height=f'{height}px')
                    # if st.session_state['waves']:
                    #     hc.option_bar(option_definition=pq_buttons.get('charts_option_data'),title='Waves', key='waves_toggle', horizontal_orientation=True) #,override_theme=over_theme,font_styling=font_fmt,horizontal_orientation=True)

            with cols[0]:
                cust_Button("misc/dollar-symbol-unscreen.gif", hoverText=f'P/L', key='total_profits', height=f'23px')
            with cols[1]:
                portfolio_header__QC(acct_info)
            
            honey_text = "Honey: " + '%{:,.4f}'.format(((acct_info['portfolio_value'] - acct_info['last_equity']) / acct_info['portfolio_value']) *100)
            money_text = "Money: " + '${:,.2f}'.format(acct_info['portfolio_value'] - acct_info['last_equity'])
            with cols[2]:
                mark_down_text(fontsize='18', text=f'{honey_text}')
            with cols[3]:
                mark_down_text(fontsize='18', text=f'{money_text}')
            cols = st.columns((6,2,1))
            with cols[0]:
                with st.expander('Master Controls', True):
                    menu_buttons()

            with cols[1]:
                with st.expander("control buttons"):
                    refresh_chess_board__button(QUEEN_KING)
                    refresh_queen_controls_button(QUEEN_KING)
                    refresh_trading_models_button(QUEEN_KING)
                    refresh_queen_orders(QUEEN)
                    stash_queen(QUEEN)
                    if st.session_state['admin']:
                        refresh_swarmqueen_workerbees(QUEEN_KING)
                        # refresh_workerbees(QUEEN_KING)
                        refresh_swarmqueen_qcp_workerbees(QUEEN, QUEEN_KING)


            if st.session_state['admin'] == True:
                st.sidebar.write('admin:', st.session_state["admin"])
                # add new keys
                KING_req = add_key_to_KING(KING=KING)
                if KING_req.get('update'):
                    KING = KING_req['KING']
                    PickleData(KING.get('source'), KING)

            ## add new keys add new keys should come from KING timestamp or this becomes a airflow job
            QUEEN_KING = add_new_trading_models_settings(QUEEN_KING) ## fix to add new keys at global level, star level, trigbee/waveBlock level
            # print("QUEEN_KING")
            APP_req = add_key_to_app(QUEEN_KING)
            QUEEN_KING = APP_req['QUEEN_KING']
            if APP_req['update']:
                print("Updating KING QUEEN db")
                PickleData(st.session_state['PB_App_Pickle'], QUEEN_KING)
            QUEEN_KING['source'] = st.session_state['PB_App_Pickle']
            
            QUEENsHeart = ReadPickleData(st.session_state['PB_QUEENsHeart_PICKLE'])
            queen_offline = False
            print("HERE")
            if queenbee_online(cols, QUEENsHeart=QUEENsHeart, admin=st.session_state['admin'], dag='run_queenbee', api_failed=api_failed, prod=prod) == False:
                queen_offline = True

            with cols[2]:
                # queensheart
                now = datetime.now(est)
                beat = round((now - QUEENsHeart.get('heartbeat_time')).total_seconds())
                beat_size = 66 if beat > 100 else beat
                beat_size = 45 if beat_size < 10 else beat_size
                cust_Button("misc/heart_beat.gif", hoverText=f'rate {beat}', key='show_queenheart', height=f'{beat_size}px', default=False)
                # if st.session_state['show_queenheart']:
                #     hc.option_bar(option_definition=pq_buttons.get('option_heart'),title='', key='option_heartbeat', horizontal_orientation=True) #,override_theme=over_theme,font_styling=font_fmt,horizontal_orientation=True)


            queenbee_online(cols=cols, QUEENsHeart=QUEENsHeart, admin=st.session_state['admin'], dag='run_workerbees', api_failed=api_failed, prod=prod)
            queenbee_online(cols=cols, QUEENsHeart=QUEENsHeart, admin=st.session_state['admin'], dag='run_workerbees_crypto', api_failed=api_failed, prod=prod)

            print("POLLENTHEMES")
            pollen_theme = pollen_themes(KING=KING)
            theme_list = list(pollen_theme.keys())

            if 'init_queen_request' in st.session_state:
                QUEEN_KING['init_queen_request'] = {'timestamp_est': datetime.now(est)}
                st.success("Hive Master Notified and You should receive contact soon")

            def return_page_tabs():
                func_list = ['orders', 'queens_mind', 'chess_board', 'waves', 'workerbees', 'charts', 'the_flash']
                func_list = [i for i in func_list if st.session_state[i]]
                if len(func_list) == 0:
                    st.info("I would Suggest Checking our Your ChessBoard This Morning")
                    tabs = False
                else:
                    tabs = st.tabs(func_list)
                
                return tabs, func_list


        if authorized_user and 'pollenq' in menu_id: 
            print("QueensConscience")
            # with cols[0]:
            tabs, func_list = return_page_tabs()

            if st.session_state['admin'] and st.session_state['workerbees']:
                with st.expander("WorkerBees Tools"):
                    refresh_workerbees(QUEENBEE, QUEEN_KING)
            
            queens_conscience(st, hc, QUEENBEE, KING, QUEEN, QUEEN_KING, tabs, api, api_vars)
        if menu_id == 'QC':
            print("QUEEN")
            queen()
        # if menu_id == 'TradingModels':
        #     print("TRADINGMODELS")
        #     trading_models()
        if menu_id == 'PlayGround':
            print("PLAYGROUND")
            PlayGround()
        if menu_id == 'Account':
            account(st=st)
            setup_page()
        if menu_id == 'pollen_engine':
            log_dir = os.path.join(st.session_state['db_root'], 'logs')
            pollen_engine(st=st, pd=pd, acct_info=acct_info_raw, log_dir=log_dir)
        


        st.session_state['refresh_times'] += 1
        page_line_seperator('5')
        print(f'pollenq {return_timestamp_string()}' )
        # hide = """
        # <style>
        # ul.streamlit-expander {
        #     border: 0 !important;
        # </style>
        # """
        # st.markdown(hide, unsafe_allow_html=True)
        
        # st.markdown(
        #     """
        #     <style>
        #     [data-testid="stSidebar"][aria-expanded="true"] > div:first-child {
        #         width: 150px;
        #     }
        #     [data-testid="stSidebar"][aria-expanded="false"] > div:first-child {
        #         width: 150px;
        #         margin-left: -150px;
        #     }
        #     </style>
        #     """,
        #     unsafe_allow_html=True,
        # )
        st.stop()
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