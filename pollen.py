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
from pages.orders import order_grid, config_orders_cols
from pages.playground import PlayGround
from pages.conscience import queens_conscience
from pages.chessboard import chessboard

# main chess piece
# from chess_piece.workerbees import queen_workerbees
# from chess_piece.workerbees_manager import workerbees_multiprocess_pool
from chess_piece.app_hive import account_header_grid, sneak_peak_form, sac_menu_buttons, set_streamlit_page_config_once, queen_messages_grid__apphive, admin_queens_active, stop_queenbee, pollenq_button_source, trigger_airflow_dag,  display_for_unAuth_client_user, queen__account_keys, page_line_seperator
from chess_piece.king import get_ip_address, master_swarm_QUEENBEE, kingdom__global_vars, hive_master_root, print_line_of_error, return_app_ip, kingdom__grace_to_find_a_Queen, streamlit_config_colors, local__filepaths_misc, ReadPickleData, PickleData
from chess_piece.queen_hive import initialize_orders, create_QueenOrderBee, kings_order_rules, return_timestamp_string, refresh_account_info, add_key_to_KING, setup_instance, add_key_to_app, init_queenbee, hive_dates, return_market_hours

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
        seconds_to_market_close = (datetime.now(est).replace(hour=16, minute=0, second=0) - datetime.now(est)).total_seconds()


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

        ##### STREAMLIT #####
        # st.session_state['orders'] = True
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

        KING, users_allowed_queen_email, users_allowed_queen_emailname__db = kingdom__grace_to_find_a_Queen()

        menu_id = sac_menu_buttons("Queen")
        
        with st.spinner("Trade Carefully And Trust the Queens Trades"):

            ####### Welcome to Pollen ##########
            # with cols[1]:
            # cols = st.columns((3,4))
            if menu_id == 'Board':
                switch_page("chessboard")
                # wierd error on None Type QUEEN_KING WORKERBEE
                # prod = st.session_state['production']
                # qb = init_queenbee(client_user=client_user, prod=prod, queen=True, queen_king=True, api=True, init=True)
                # QUEEN = qb.get('QUEEN')
                # QUEEN_KING = qb.get('QUEEN_KING')
                # api = qb.get('api')    
                # revrec = QUEEN_KING.get('revrec')

                # alpaca_acct_info = refresh_account_info(api=api)
                # with st.sidebar:
                #     if st.button('acct info'):
                #         st.write(alpaca_acct_info)

                # acct_info = alpaca_acct_info.get('info_converted')

                # QUEENBEE = ReadPickleData(master_swarm_QUEENBEE(prod))

                # swarm_queen_symbols = []
                # for qcp, va in QUEENBEE['workerbees'].items():
                #     tickers = va.get('tickers')
                #     if tickers:
                #         for tic in tickers:
                #             swarm_queen_symbols.append(tic)

                # themes = list(pollen_themes(KING).keys())
                # chessboard(revrec=revrec, QUEEN_KING=QUEEN_KING, ticker_allowed=swarm_queen_symbols, themes=themes, admin=False)
                # st.stop()

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
                # switch_page('orders')
                queen_orders = pd.DataFrame([create_QueenOrderBee(queen_init=True)])

                active_order_state_list = king_G.get('active_order_state_list')
                config_cols = config_orders_cols(active_order_state_list)
                missing_cols = [i for i in queen_orders.iloc[-1].index.tolist() if i not in config_cols.keys()]
                order_grid(client_user, config_cols, KING, missing_cols, ip_address, seconds_to_market_close)

                st.stop()

            if menu_id == 'TradingModels':
                switch_page('trading_models')

            # use API keys from user            
            prod = False if 'sneak_peak' in st.session_state and st.session_state['sneak_peak'] else prod
            sneak_peak = True if 'sneak_peak' in st.session_state and st.session_state['sneak_peak'] else False
            sneak_peak = True if client_user == 'stefanstapinski@yahoo.com' else False
            
            PB_QUEENBEE_Pickle = master_swarm_QUEENBEE(prod=prod)
            QUEENBEE = ReadPickleData(PB_QUEENBEE_Pickle)
            qb = init_queenbee(client_user=client_user, prod=prod, queen=True, queen_king=True, api=True, init=True)
            QUEEN = qb.get('QUEEN')
            QUEEN_KING = qb.get('QUEEN_KING')
            api = qb.get('api')            
            if 'chess_board__revrec' not in QUEEN_KING.keys():
                switch_page('chessboard')

            if st.sidebar.button("update Queen Orders"):
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

            if QUEEN_KING.get('revrec') == 'init':
                st.warning("missing revrec, add revrec to QUEEN")

            ## add new keys add new keys should come from KING timestamp or this becomes a airflow job
            if st.sidebar.button("Check for new KORs"):
                QUEEN_KING = add_new_trading_models_settings(QUEEN_KING) ## fix to add new keys at global level, star level, trigbee/waveBlock level
            APP_req = add_key_to_app(QUEEN_KING)
            QUEEN_KING = APP_req['QUEEN_KING']
            if APP_req['update']:
                print("Updating QK db")

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
            print("QC Page Func")
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
