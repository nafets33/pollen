# pollenq
import pandas as pd
import logging
import os
import numpy as np
from datetime import datetime, timedelta, date
import pytz
import subprocess
import sys

from PIL import Image
from dotenv import load_dotenv
import os
import requests

import streamlit as st
from pq_auth import signin_main
import time
import argparse

#pages
from pages.playground import PlayGround
from pages.conscience import queens_conscience
# from pages.account import account
from pages.pollen_engine import pollen_engine

# main chess piece
from chess_piece.workerbees import queen_workerbees
from chess_piece.workerbees_manager import workerbees_multiprocess_pool
from chess_piece.app_hive import sneak_peak_form, custom_fastapi_text, sac_menu_buttons, cust_graph, setup_page, set_streamlit_page_config_once, queen_messages_grid__apphive, admin_queens_active, stop_queenbee, read_QUEEN, pollenq_button_source, trigger_airflow_dag, send_email, flying_bee_gif, display_for_unAuth_client_user, queen__account_keys, local_gif, mark_down_text, update_queencontrol_theme, progress_bar, page_line_seperator, return_runningbee_gif__save
from chess_piece.king import get_ip_address, master_swarm_QUEENBEE, kingdom__global_vars, hive_master_root, print_line_of_error, master_swarm_KING, kingdom__grace_to_find_a_Queen, streamlit_config_colors, local__filepaths_misc, ReadPickleData, PickleData
from chess_piece.queen_hive import analyze_waves, initialize_orders, create_QueenOrderBee, generate_chessboards_trading_models, stars, return_queen_controls, generate_chess_board, kings_order_rules, return_timestamp_string, return_alpaca_user_apiKeys, refresh_account_info, init_KING, add_key_to_KING, setup_instance, add_key_to_app, init_queenbee, pollen_themes, hive_dates, return_market_hours

# componenets
import streamlit_antd_components as sac
from streamlit_extras.switch_page_button import switch_page
from streamlit_extras.stoggle import stoggle
import hydralit_components as hc
from custom_button import cust_Button
# from custom_text import custom_text, TextOptionsBuilder


# ozz
# from ozz.ozz_bee import send_ozz_call

import ipdb


pd.options.mode.chained_assignment = None
est = pytz.timezone("US/Eastern")



def menu_bar_selection(prod_name_oppiste, prod_name, prod, menu,hide_streamlit_markers=True):
    k_colors = streamlit_config_colors()
    default_text_color = k_colors['default_text_color'] # = '#59490A'
    default_font = k_colors['default_font'] # = "sans serif"
    default_yellow_color = k_colors['default_yellow_color'] # = '#C5B743'
    


    if menu == 'main':
        
        menu_data = [
            {'id':'queen','icon':"fa fa-fire",'label':"Queen"},
            {'id':'TradingModels','icon':"fa fa-fire",'label':"Trading Models"},
            {'id':'PlayGround', 'icon': "fa fa-bug", 'label':"PlayGround"},
            {'id':'Account', 'icon': "fa fa-bug", 'label':"Account"},
            {'id':'waves', 'icon': "fas fa-chess-board", 'label':"RevRec"},
            {'icon': "fa fa-fighter-jet",'label':"HiveEngine", 
             'submenu':[{'id':'pollen_engine', 'label':"QUEEN", 'icon': "fa fa-heart"},{'label':"KING", 'icon': "fa fa-meh"}]},

        ]
    elif menu == 'unAuth':
        menu_data = [
            {'id':'unauth','icon':"fa fa-fire",'label':"Welcome to pollenq"},

            # {'id':'Copy','icon':"🐙",'label':"Copy"},
            # {'icon': "fa-solid fa-radar",'label':"Dropdown1", 'submenu':[{'id':' subid11','icon': "fa fa-paperclip", 'label':"Sub-item 1"},{'id':'subid12','icon': "💀", 'label':"Sub-item 2"},{'id':'subid13','icon': "fa fa-database", 'label':"Sub-item 3"}]},
            # {'icon': "far fa-chart-bar", 'label':"Chart"},#no tooltip message
            # {'id':' Crazy return value 💀','icon': "💀", 'label':"Calendar"},
            # {'icon': "fas fa-tachometer-alt", 'label':"Dashboard",'ttip':"I'm the Dashboard tooltip!"}, #can add a tooltip message
            # {'icon': "far fa-copy", 'label':"Right End"},
            # {'icon': "fa-solid fa-radar",'label':"Dropdown2", 'submenu':[{'label':"Sub-item 1", 'icon': "fa fa-meh"},{'label':"Sub-item 2"},{'icon':'🙉','label':"Sub-item 3",}]},
        ]
        prod_name = ""

    if prod:

        menu_id = hc.nav_bar(
            menu_definition=menu_data,
            home_name=f'pollen {prod_name}',
            login_name='Account',
            hide_streamlit_markers=hide_streamlit_markers, #will show the st hamburger as well as the navbar now!
            sticky_nav=True, #at the top or not
            sticky_mode='pinned', #jumpy or not-jumpy, but sticky or pinned
        )
    else:
        over_theme = {'option_active':'#B7C8D6'} # {'txc_inactive': '#FB070A'} #'txc_active':'#59490A','option_active':'#FB6464'} #'menu_background':'black',
        # over_font = {'font-class':'h2','font-size':'100%'}
        # over_theme = {'txc_inactive': "#0D93FB"}
        menu_id = hc.nav_bar(
            menu_definition=menu_data,
            override_theme=over_theme,
            # font_styling=over_font,
            home_name=f'pollen {prod_name}',
            login_name='Account',
            hide_streamlit_markers=hide_streamlit_markers, #will show the st hamburger as well as the navbar now!
            sticky_nav=True, #at the top or not
            sticky_mode='pinned', #jumpy or not-jumpy, but sticky or pinned
        )

    st.session_state['menu_id']= menu_id

    return menu_id

def pollenq(admin_pq):
    try:
        main_page_start = datetime.now()
        king_G = kingdom__global_vars()
        main_root = hive_master_root()
        load_dotenv(os.path.join(main_root, ".env"))

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

                    if (now - QUEENsHeart['heartbeat_time']).total_seconds() > 23:
                        # st.write("YOUR QUEEN if OFFLINE")
                        # st.error("Your Queen Is Asleep Wake Her UP!")
                        with cols[0]:
                            wake_up_queen_button = st.button("Your Queen Trading Bot Is Asleep Wake Her UP!", use_container_width=True)
                            # local_gif(gif_path=flyingbee_grey_gif_path)
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
                            # st.experimental_rerun()
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

        def check_fastapi_status(ip_address):
            try:

                req = requests.get(f"{ip_address}/api/data/", timeout=2) # http://127.0.0.1:8000/api/data/

                return True
            # except ConnectionError as e:
            except Exception as e:
                print(e)
                return False


        def portfolio_header__QC(acct_info):
            try:
           
                with st.expander("Portfolio: " + '${:,.2f}'.format(acct_info['portfolio_value']),  False):
                    # st.write(":heavy_minus_sign:" * 34)
                    mark_down_text(fontsize='18', text="Total Buying Power: " + '${:,.2f}'.format(acct_info['buying_power']))
                    mark_down_text(fontsize='15', text="last_equity: " + '${:,.2f}'.format(acct_info['last_equity']))
                    mark_down_text(fontsize='15', text="portfolio_value: " + '${:,.2f}'.format(acct_info['portfolio_value']))
                    mark_down_text(fontsize='15', text="Cash: " + '${:,.2f}'.format(acct_info['cash']))
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


        def run_pq_fastapi_server():

            script_path = os.path.join(hive_master_root(), 'pq_fastapi_server.py')

            try:
                # Use sys.executable to get the path to the Python interpreter
                python_executable = sys.executable
                subprocess.run([python_executable, script_path, '-i'])
            except FileNotFoundError:
                print(f"Error: Python interpreter not found. Make sure Python is installed.")
            except Exception as e:
                print(f"Error: {e}")

        # print("MENU Buttons")
        def menu_buttons(cols, QUEENsHeart):
            # sb = st.sidebar
            # cust_Button("https://www.pngall.com/wp-content/uploads/2016/03/Chess-Free-PNG-Image.png", hoverText='Trading Models', key='queens_mind', height=f'{height}px', default=False)
            try:
                off_size = 23
                on_size = 54
                # with sb:
                # cols = st.columns(7)
                height = 50
                # with st.expander("Menu Buttons"):

                    # with cols[1]:
                    # print("Heart")
                    # now = datetime.now(est)
                    # beat = round((now - QUEENsHeart.get('heartbeat_time')).total_seconds())
                    # beat_size = 66 if beat > 100 else beat
                    # beat_size = 45 if beat_size < 10 else beat_size
                    # cust_Button("misc/zelda-icons.gif", hoverText=f'{beat}', key='show_queenheart', height=f'{height}px', default=False)
                    # with cols[2]:
                    # height = on_size if 'workerbees' in st.session_state and st.session_state['workerbees'] == True else off_size
                    # cust_Button("misc/power.png", hoverText='WorkerBees', key='workerbees', default=False, height=f'{height}px') # "https://cdn.onlinewebfonts.com/svg/img_562964.png"

                    # with cols[3]:
                    # cb = cust_Button("misc/knight_pawn.png", hoverText='Orders', key='orders_m', default=True, height=f'{height}px') # "https://cdn.onlinewebfonts.com/svg/img_562964.png"
                    # st.session_state['orders'] = True if cb == True or cb == 0 else False
                    
                    # with cols[2]:
                    # height = on_size if 'chess_board' in st.session_state and st.session_state['chess_board'] == True else off_size
                    # cust_Button("https://cdn.onlinewebfonts.com/svg/img_562964.png", hoverText='Chess Board', key='chess_board', height=f'{height}px', default=False)
                    # with cols[4]:
                    # st.session_state['chess_board'] = True if st.session_state['chess_board_m'] in ['admin_workerbees', 'chess_board'] or st.session_state['chess_board_m'] == None else False
                    # cust_Button("https://www.pngall.com/wp-content/uploads/2016/03/Chess-Free-PNG-Image.png", hoverText='Trading Models', key='queens_mind', height=f'{height}px', default=False)
                    # st.session_state['queens_mind'] = True if st.session_state['queens_mind'] in ['queens_mind'] or st.session_state['queens_mind'] == None else False
                    
                    # with cols[5]:
                    # height = on_size if 'charts' in st.session_state and st.session_state['charts'] == True else off_size
                    # cust_Button("misc/charts.png", hoverText='Charts', key='charts', height=f'{height}px', default=False)

                    # with cols[6]:
                    # height = on_size if 'the_flash' in st.session_state and st.session_state['the_flash'] == True else off_size
                    # cust_Button("misc/power_gif.gif", hoverText='The Flash', key='the_flash', height=f'{height}px')
                    
                    # with cols[7]:              
                    # height = on_size if 'waves' in st.session_state and st.session_state['waves'] == True else off_size
                    # cust_Button("misc/waves.png", hoverText='Waves', key='waves', height=f'{height}px', default=False)
                        # st.session_state['waves'] = True if st.session_state['waves_m'] == 'waves' else False
                        # if st.session_state['waves']:
                        #     hc.option_bar(option_definition=pq_buttons.get('charts_option_data'),title='Waves', key='waves_toggle', horizontal_orientation=True) #,override_theme=over_theme,font_styling=font_fmt,horizontal_orientation=True)
            except Exception as e:
                print(e)
                print_line_of_error()


        def update_queen_orders(QUEEN): # for revrec # WORKERBEE WORKING
            
            def refresh_long_short(QUEEN):
                queen_orders = QUEEN['queen_orders']
                queen_orders['long_short'] = np.where(queen_orders['trigname'].str.contains('buy'), 'long', 'short')

                return QUEEN
                # queen_orders = queen_orders.fillna("")
                # # Calculate the length of strings and apply the condition
                # queen_orders['valid_order'] = queen_orders['trigname'].str.len() > 5 ## i.e. does not == "init" or any other value
                # queen_orders['valid_order'] = queen_orders['valid_order'].astype(int)  # Convert boolean values to 0 or 1
                # queen_orders = queen_orders[queen_orders['valid_order'] == 1]
                # ls_missing = queen_orders[queen_orders['long_short'] == 'init']
                # buy_orders = queen_orders[queen_orders['trigname'].str.contains('buy')]
                # sell_orders = queen_orders[queen_orders['trigname'].str.contains('sell')]


            # update queen orders ## IMPROVE / REMOVE ## WORKERBEE
            qo = QUEEN['queen_orders']
            qo_cols = qo.columns.tolist()
            latest_order = pd.DataFrame([create_QueenOrderBee(queen_init=True)])
            missing = [i for i in latest_order.columns.tolist() if i not in qo_cols]
            if missing:
                st.warning("YOU NEED TO REFRESH/SAVE YOUR QUEEN ORDERS BEFORE CONTINUING")
                for col in missing:
                    print("adding new column to queens orders: ", col)
                    QUEEN['queen_orders'][col] = latest_order.iloc[0].get(col)
                

        ##### QuantQueen #####
        print(f'pollenq END >>>> {return_timestamp_string()}' )  

        set_streamlit_page_config_once()

        ip_address = get_ip_address()
        if ip_address == os.environ.get('gcp_ip'):
            ip_address = "https://api.quantqueen.com"
            streamlit_ip = ip_address
        else:
            ip_address = "http://127.0.0.1:8000"
            streamlit_ip = "http://localhost:8502"
        
        st.session_state['ip_address'] = ip_address
        st.session_state['streamlit_ip'] = streamlit_ip

        pq_buttons = pollenq_button_source()
        s = datetime.now(est)

        # images
        # MISC = local__filepaths_misc()
        # MISC_cb = local__filepaths_misc(jpg_root=os.path.join(hive_master_root(), '/custom_button/frontend/build/misc' ))
        # bee_image = MISC['bee_image']
        # mainpage_bee_png = MISC['mainpage_bee_png']
        # flyingbee_grey_gif_path = MISC['flyingbee_grey_gif_path']

        ##### STREAMLIT #####
        st.session_state['orders'] = True
        if 'refresh_times' not in st.session_state:
            st.session_state['refresh_times'] = 0
            pq_buttons['chess_board'] = True

        k_colors = streamlit_config_colors()
        default_text_color = k_colors['default_text_color'] # = '#59490A'
        default_font = k_colors['default_font'] # = "sans serif"
        default_yellow_color = k_colors['default_yellow_color'] # = '#C5B743'
        default_background_color = k_colors.get('default_background_color')
        

        with st.spinner("Verifying Your Scent, Hang Tight"):
            authenticator = signin_main(page="pollenq")
            if st.session_state['authentication_status'] != True: ## None or False
                
                display_for_unAuth_client_user()
                st.stop()

            prod = st.session_state['production']
            authorized_user = st.session_state['authorized_user']
            client_user = st.session_state["username"]
            prod_name = "LIVE" if st.session_state['production'] else "Sandbox"    
            prod_name_oppiste = "Sandbox" if st.session_state['production']  else "LIVE"   
            
            if authorized_user != True:
                st.error("Your Account is Not Yet Authorized by a pollenq admin")
                authenticator.logout("Logout", location='sidebar')
                if sneak_peak_form():
                    pass
                else:
                    st.stop()

        st.session_state['sneak_name'] = ' ' if 'sneak_name' not in st.session_state else st.session_state['sneak_name']
        print(st.session_state['sneak_name'], st.session_state['username'], return_timestamp_string())
        
        log_dir = os.path.join(st.session_state['db_root'], 'logs')

        with st.spinner("Trade Carefully And Trust the Queens Trades"):

            ####### Welcome to Pollen ##########
            # use API keys from user            
            prod = False if 'sneak_peak' in st.session_state and st.session_state['sneak_peak'] else prod
            sneak_peak = True if 'sneak_peak' in st.session_state and st.session_state['sneak_peak'] else False
            sneak_peak = True if client_user == 'stefanstapinski@yahoo.com' else False
            
            PB_QUEENBEE_Pickle = master_swarm_QUEENBEE(prod=prod)
            QUEENBEE = ReadPickleData(PB_QUEENBEE_Pickle)
            KING, users_allowed_queen_email, users_allowed_queen_emailname__db = kingdom__grace_to_find_a_Queen()
            qb = init_queenbee(client_user=client_user, prod=prod, queen=True, queen_king=True, api=True, init=True)
            QUEEN = qb.get('QUEEN')
            QUEEN_KING = qb.get('QUEEN_KING')
            api = qb.get('api')            
            if 'chess_board__revrec' not in QUEEN_KING.keys():
                switch_page('chessboard')

            update_queen_orders(QUEEN)
            
            admin_check(admin_pq)
            with st.sidebar:
                hide_streamlit_markers = False if st.button('show_dev-ham', use_container_width=True) else True
            
            if st.session_state['admin'] == True:
                st.sidebar.write('admin:', st.session_state["admin"])
                # add new keys
                KING_req = add_key_to_KING(KING=KING)
                if KING_req.get('update'):
                    KING = KING_req['KING']
                    PickleData(KING.get('source'), KING)
                
                with st.sidebar:
                    with st.expander("admin"):
                        cust_Button("misc/bee.jpg", hoverText='admin users', key='admin_users', height='34px')
                        cust_Button("misc/bee.jpg", hoverText='send queen', key='admin_queens', height='34px')


            if st.session_state.get('admin_queens'):
                admin_send_queen_airflow(KING)
            if st.session_state.get('admin_users'):
                admin_queens_active(KING.get('source'), KING)
            
            # PROD vs SANDBOX
            
            if sneak_peak:
                pass
            else:
                live_sb_button = st.sidebar.button(f'Switch Enviroment', key='pollenq', use_container_width=True)
                if live_sb_button:
                    st.session_state['production'] = setup_instance(client_username=st.session_state["username"], switch_env=True, force_db_root=False, queenKING=True)
                    prod = st.session_state['production']
                    qb = init_queenbee(client_user=client_user, prod=prod, queen=True, queen_king=True, api=True)
                    QUEEN = qb.get('QUEEN')
                    QUEEN_KING = qb.get('QUEEN_KING')
                    api = qb.get('api')

            if st.session_state['production'] == False:
                st.warning("Sandbox Paper Money Account") 

            stop_queenbee(QUEEN_KING, sidebar=True)

            if QUEEN.get('revrec') == 'init':
                st.warning("missing revrec, add revrec to QUEEN")

            ## add new keys add new keys should come from KING timestamp or this becomes a airflow job
            if st.sidebar.button("Check for new KORs"):
                QUEEN_KING = add_new_trading_models_settings(QUEEN_KING) ## fix to add new keys at global level, star level, trigbee/waveBlock level
            APP_req = add_key_to_app(QUEEN_KING)
            QUEEN_KING = APP_req['QUEEN_KING']
            if APP_req['update']:
                print("Updating KING QUEEN db")
                PickleData(st.session_state['PB_App_Pickle'], QUEEN_KING)
            QUEEN_KING['source'] = st.session_state['PB_App_Pickle']
            QUEENsHeart = ReadPickleData(st.session_state['PB_QUEENsHeart_PICKLE'])   

            if st.sidebar.button('show_keys'):
                queen__account_keys(PB_App_Pickle=st.session_state['PB_App_Pickle'], QUEEN_KING=QUEEN_KING, authorized_user=authorized_user, show_form=True) #EDRXZ Maever65teo

            try:
                if api == False:
                    queen__account_keys(PB_App_Pickle=st.session_state['PB_App_Pickle'], QUEEN_KING=QUEEN_KING, authorized_user=authorized_user, show_form=True) #EDRXZ Maever65teo
                    api_failed = True
                    st.stop()
                else:
                    api_failed = False
                    snapshot = api.get_snapshot("SPY") # return_last_quote from snapshot
                alpaca_acct_info = refresh_account_info(api=api)
                with st.sidebar:
                    if st.button('acct info'):
                        st.write(alpaca_acct_info)
                # ap_info=alpaca_acct_info
                # st.write(float(ap_info['info'].get('daytrading_buying_power')) - 4 * (float(ap_info['info'].get('last_equity')) - float(ap_info['info'].get('last_maintenance_margin'))))
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

            ### TOP OF PAGE
            if st.session_state['admin']:
                if check_fastapi_status(ip_address) == False:
                    st.error("api")
                    if st.button('API'):
                        run_pq_fastapi_server()

            trading_days = hive_dates(api=api)['trading_days']
            mkhrs = return_market_hours(trading_days=trading_days)
            
            seconds_to_market_close = (datetime.now(est).replace(hour=16, minute=0, second=0) - datetime.now(est)).total_seconds()
            seconds_to_market_close = abs(seconds_to_market_close) if seconds_to_market_close > 0 else 8
            if mkhrs != 'open':
                seconds_to_market_close = 1

            cols = st.columns((3,5,2))
            menu = sac_menu_buttons("Queen")
            with cols[2]:
                menu_id = menu_bar_selection(prod_name_oppiste=prod_name_oppiste, prod_name=prod_name, prod=st.session_state['production'], menu='main', hide_streamlit_markers=hide_streamlit_markers) 
                if menu_id == 'waves':
                    switch_page('waves')

                if menu_id == 'PlayGround':
                    print("PLAYGROUND")
                    PlayGround()
                    st.stop()
                
                if menu_id == 'Account':
                    switch_page('account')
                    
                if menu_id == 'pollen_engine':
                    pollen_engine(st=st, pd=pd, acct_info=acct_info_raw, log_dir=log_dir)
                    st.stop()

                if menu_id == 'TradingModels':
                    switch_page('trading_models')

            with cols[0]:
                # with st.expander("Queens Heart :heartbeat:", False):
                custom_fastapi_text(KING=KING, 
                                    client_user=client_user, 
                                    default_background_color=default_background_color, 
                                    default_text_color=default_text_color, 
                                    default_font=default_font,
                                    refresh_sec=8,
                                    refresh_cutoff_sec=seconds_to_market_close, 
                                    prod=prod, 
                                    api=f'{ip_address}/api/data/heart',
                                    key='header1',
                                    text_size=20)
            with cols[1]:
                # with st.expander("Account Summary :heavy_dollar_sign:", False):
                custom_fastapi_text(KING=KING, 
                                    client_user=client_user, 
                                    default_background_color=default_background_color, 
                                    default_text_color=default_text_color, 
                                    default_font=default_font,
                                    refresh_sec=8,
                                    refresh_cutoff_sec=seconds_to_market_close, 
                                    prod=prod, 
                                    api=f'{ip_address}/api/data/account_info',
                                    key='header2',
                                    text_size=20)
            
            
            cols = st.columns((1,1,5))

            with st.sidebar:
                height=50
                cust_Button("misc/power.png", hoverText='WorkerBees', key='workerbees', default=False, height=f'{height}px') # "https://cdn.onlinewebfonts.com/svg/img_562964.png"

        
        if authorized_user and 'pollen' in menu_id: 
            queens_conscience(QUEENBEE, KING, QUEEN, QUEEN_KING, api, api_vars)

        cols = st.columns((2,2,5))

        with cols[0]:
            height = 54
            cust_Button("misc/zelda-icons.gif", hoverText=f'Inside Queens Heart', key='show_queenheart', height=f'{height}px', default=False)

        with cols[1]:
            if st.toggle("Control Settings"):
                with st.expander("control buttons"):
                    refresh_chess_board__button(QUEEN_KING)
                    refresh_queen_controls_button(QUEEN_KING)
                    refresh_trading_models_button(QUEEN_KING)
                    refresh_queen_orders(QUEEN)
                    stash_queen(QUEEN)



        with cols[2]:
            # with st.expander("Hey I'm Ozz Your AI Trading Bot, I'll help your Trades Win! Let Chat"):
            jpg_root = os.path.join(main_root, "misc")
            queenbee_png = os.path.join(jpg_root, "bee.png")
            queen_logs = st.toggle("Queens Mind")
            st.session_state['Queens Mind'] = queen_logs

        if st.session_state['Queens Mind']:
            st.text_input("Ask Ozz", value="", help="Ozz is your AI trading bot that can help you with entire portfolio ask Any Question, what should I buy? what should I sell? can you reallocate to more cash")
            st.image(queenbee_png, width=33)
            logs = os.listdir(log_dir)
            logs = [i for i in logs if i.endswith(".log")]
            log_file = 'log_queen.log' if 'log_queen.log' in logs else logs[0]
            log_file = st.sidebar.selectbox("Log Files", list(logs), index=list(logs).index(log_file))
            log_file = os.path.join(log_dir, log_file) # single until allow for multiple
            queen_messages_grid__apphive(KING, log_file=log_file, grid_key='queen_logfile', f_api=f'{ip_address}/api/data/queen_messages_logfile', varss={'seconds_to_market_close': seconds_to_market_close, 'refresh_sec': 4})
            def return_log_file():
                with open(log_file, 'r') as f:
                    content = f.readlines()

                df = pd.DataFrame(content).reset_index()
                df = df.sort_index(ascending=False)
                df = df.rename(columns={'index': 'idx', 0: 'message'})
                df = df.head(500)
                # st.dataframe(df, width=800)
                return df

        st.session_state['refresh_times'] += 1
        page_line_seperator('5')
        
        print(f'pollenq END >>>> {(datetime.now() - main_page_start).total_seconds()}' )

        # with cols[6]:
        # st.button("Refresh", use_container_width=True)
            # cust_Button(file_path_url='misc/runaway_bee_gif.gif', height='23px', hoverText="Refresh")
        # with cols[7]:


        st.stop()
    except Exception as e:
        print_line_of_error(e)

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