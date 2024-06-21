# pollen
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

# main chess piece
from chess_piece.workerbees import queen_workerbees
from chess_piece.workerbees_manager import workerbees_multiprocess_pool
from chess_piece.app_hive import account_header_grid, sneak_peak_form, custom_fastapi_text, sac_menu_buttons, cust_graph, setup_page, set_streamlit_page_config_once, queen_messages_grid__apphive, admin_queens_active, stop_queenbee, read_QUEEN, pollenq_button_source, trigger_airflow_dag, send_email, flying_bee_gif, display_for_unAuth_client_user, queen__account_keys, local_gif, mark_down_text, update_queencontrol_theme, progress_bar, page_line_seperator, return_runningbee_gif__save
from chess_piece.king import get_ip_address, master_swarm_QUEENBEE, kingdom__global_vars, hive_master_root, print_line_of_error, return_app_ip, kingdom__grace_to_find_a_Queen, streamlit_config_colors, local__filepaths_misc, ReadPickleData, PickleData
from chess_piece.queen_hive import initialize_orders, create_QueenOrderBee, generate_chessboards_trading_models, stars, return_queen_controls, generate_chess_board, kings_order_rules, return_timestamp_string, return_alpaca_user_apiKeys, refresh_account_info, init_KING, add_key_to_KING, setup_instance, add_key_to_app, init_queenbee, pollen_themes, hive_dates, return_market_hours

# componenets
# import streamlit_antd_components as sac
from streamlit_extras.switch_page_button import switch_page
# from streamlit_extras.stoggle import stoggle
# import hydralit_components as hc
from custom_button import cust_Button
# from custom_text import custom_text, TextOptionsBuilder


# ozz
# from ozz.ozz_bee import send_ozz_call

import ipdb


pd.options.mode.chained_assignment = None
est = pytz.timezone("US/Eastern")


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
                            # (missing_rules)
                            if len(missing_rules) > 0:
                                save = True
                                new_rules_confirmation[ticker] = []
                                for new_rule in missing_rules:
                                    QUEEN_KING['king_controls_queen']['symbols_stars_TradingModel'][ticker]['stars_kings_order_rules'][ticker_star]['trigbees'][trigbee][blocktime].update({new_rule: latest_kors.get(new_rule)})
                                    msg = f'New Rule Added: , {ticker}{ticker_star}{trigbee}{blocktime}{new_rule}'
                                    new_rules_confirmation[ticker].append(new_rule)
                                    # (f'New Rule Added: , {ticker}{new_rule}')
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
                print_line_of_error()

        def check_fastapi_status(ip_address):
            try:

                req = requests.get(f"{ip_address}/api/data/", timeout=2) # http://127.0.0.1:8000/api/data/

                return True
            # except ConnectionError as e:
            except Exception as e:
                print(e)
                return False



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


        def update_queen_orders(QUEEN): # for revrec # WORKERBEE WORKING
            
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

        ip_address = return_app_ip()

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

        # k_colors = streamlit_config_colors()

        authenticator = signin_main(page="pollenq")
        with st.spinner("Verifying Your Scent, Hang Tight"):
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

            # with cols[1]:
            menu_id = sac_menu_buttons("Queen")
            # cols = st.columns((3,4))
            if menu_id == 'Board':
                switch_page('chessboard')
            # menu_id = menu_bar_selection(prod_name_oppiste=prod_name_oppiste, prod_name=prod_name, prod=st.session_state['production'], menu='main', hide_streamlit_markers=hide_streamlit_markers) 
            if menu_id == 'Waves':
                switch_page('waves')

            if menu_id == 'PlayGround':
                print(menu_id)
                print("PLAYGROUND")
                PlayGround()
                st.stop()
            
            if menu_id == 'Account':
                switch_page('account')

            if menu_id == 'Orders':
                switch_page('orders')

            if menu_id == 'TradingModels':
                switch_page('trading_models')

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
            
            # PROD vs SANDBOX #
            
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
            
            st.session_state['mkhrs'] = mkhrs
            st.session_state['seconds_to_market_close'] = seconds_to_market_close

            if menu_id == 'Engine':
                from pages.pollen_engine import pollen_engine
                pollen_engine(acct_info=acct_info_raw, log_dir=log_dir)
                logs = os.listdir(log_dir)
                logs = [i for i in logs if i.endswith(".log")]
                log_file = 'log_queen.log' if 'log_queen.log' in logs else logs[0]
                log_file = st.sidebar.selectbox("Log Files", list(logs), index=list(logs).index(log_file))
                log_file = os.path.join(log_dir, log_file) # single until allow for multiple
                queen_messages_grid__apphive(KING, log_file=log_file, grid_key='queen_logfile', f_api=f'{ip_address}/api/data/queen_messages_logfile', varss={'seconds_to_market_close': seconds_to_market_close, 'refresh_sec': False})

                st.stop()


            # with cols[0]:
            refresh_sec = 8 if seconds_to_market_close > 0 and mkhrs == 'open' else 63000
            account_header_grid(client_user, refresh_sec, ip_address, seconds_to_market_close)

            with st.sidebar:
                height=50
                cust_Button("misc/power.png", hoverText='WorkerBees', key='workerbees', default=False, height=f'{height}px') # "https://cdn.onlinewebfonts.com/svg/img_562964.png"

        
        if authorized_user and 'pollen' in menu_id: 
            queens_conscience(QUEENBEE, KING, QUEEN, QUEEN_KING, api, api_vars)

        st.session_state['refresh_times'] += 1
        page_line_seperator('5')
        
        print(f'pollen END >>>> {(datetime.now() - main_page_start).total_seconds()}' )

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
    pollenq(admin_pq)
