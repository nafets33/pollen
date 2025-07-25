# pollen
import pandas as pd
import logging
import os
import numpy as np
from datetime import datetime, timedelta, date
import pytz
import subprocess
import sys
from tqdm import tqdm
from collections import deque
from dotenv import load_dotenv
import os
import requests

import streamlit as st
from pq_auth import signin_main
import time
import argparse

#pages
# from pages.orders import order_grid, config_orders_cols
from pages.conscience import queens_conscience
# from pages.chessboard import chessboard

# main chess piece
# from chess_piece.workerbees import queen_workerbees
# from chess_piece.workerbees_manager import workerbees_multiprocess_pool
from chess_piece.app_hive import mark_down_text, sac_menu_buttons, set_streamlit_page_config_once, admin_queens_active, stop_queenbee, pollenq_button_source, trigger_airflow_dag, queen__account_keys, page_line_seperator
from chess_piece.king import hive_master_root_db, kingdom__global_vars, hive_master_root, ReadPickleData, return_QUEENs__symbols_data, PickleData, return_app_ip
from chess_piece.queen_hive import return_all_client_users__db, init_swarm_dbs, kingdom__grace_to_find_a_Queen, return_queen_controls, stars, return_timestamp_string, refresh_account_info, add_key_to_KING, setup_instance, add_key_to_app, init_queenbee, hive_dates, return_market_hours, return_Ticker_Universe, init_charlie_bee
from chess_piece.queen_mind import kings_order_rules
from pages.conscience import account_header_grid
# componenets
# import streamlit_antd_components as sac
# from streamlit_extras.switch_page_button import switch_page
# from streamlit_extras.stoggle import stoggle
# import hydralit_components as hc
from custom_button import cust_Button
from chess_piece.pollen_db import PollenDatabase
# from pages.PortfolioManager import ozz 


import ipdb

pg_migration = os.getenv('pg_migration')


pd.options.mode.chained_assignment = None
est = pytz.timezone("US/Eastern")


bishop_symbol_cols = [
    'phone',
'website',
'industry',
'industryKey',
'industryDisp',
'sector',
'sectorKey',
'sectorDisp',
'longBusinessSummary',
'fullTimeEmployees',
'companyOfficers',
'auditRisk',
'boardRisk',
'compensationRisk',
'shareHolderRightsRisk',
'overallRisk',
'governanceEpochDate',
'compensationAsOfEpochDate',
'maxAge',
'priceHint',
'previousClose',
'open',
'dayLow',
'dayHigh',
'regularMarketPreviousClose',
'regularMarketOpen',
'regularMarketDayLow',
'regularMarketDayHigh',
'dividendRate',
'dividendYield',
'exDividendDate',
'payoutRatio',
'fiveYearAvgDividendYield',
'beta',
'trailingPE',
'forwardPE',
'volume',
'regularMarketVolume',
'averageVolume',
'averageVolume10days',
'averageDailyVolume10Day',
'bid',
'ask',
'bidSize',
'askSize',
'marketCap',
'fiftyTwoWeekLow',
'fiftyTwoWeekHigh',
'priceToSalesTrailing12Months',
'fiftyDayAverage',
'twoHundredDayAverage',
'trailingAnnualDividendRate',
'trailingAnnualDividendYield',
'currency',
'enterpriseValue',
'profitMargins',
'floatShares',
'sharesOutstanding',
'sharesShort',
'sharesShortPriorMonth',
'sharesShortPreviousMonthDate',
'dateShortInterest',
'sharesPercentSharesOut',
'heldPercentInsiders',
'heldPercentInstitutions',
'shortRatio',
'shortPercentOfFloat',
'impliedSharesOutstanding',
'bookValue',
'priceToBook',
'lastFiscalYearEnd',
'nextFiscalYearEnd',
'mostRecentQuarter',
'earningsQuarterlyGrowth',
'netIncomeToCommon',
'trailingEps',
'forwardEps',
'pegRatio',
'lastSplitFactor',
'lastSplitDate',
'enterpriseToRevenue',
'enterpriseToEbitda',
'52WeekChange',
'SandP52WeekChange',
'lastDividendValue',
'lastDividendDate',
'exchange',
'quoteType',
'symbol',
'underlyingSymbol',
'shortName',
'longName',
'firstTradeDateEpochUtc',
'timeZoneFullName',
'timeZoneShortName',
'uuid',
'messageBoardId',
'gmtOffSetMilliseconds',
'currentPrice',
'targetHighPrice',
'targetLowPrice',
'targetMeanPrice',
'targetMedianPrice',
'recommendationMean',
'recommendationKey',
'numberOfAnalystOpinions',
'totalCash',
'totalCashPerShare',
'ebitda',
'totalDebt',
'quickRatio',
'currentRatio',
'totalRevenue',
'debtToEquity',
'revenuePerShare',
'returnOnAssets',
'returnOnEquity',
'freeCashflow',
'operatingCashflow',
'earningsGrowth',
'grossMargins',
'ebitdaMargins',
'operatingMargins',
'financialCurrency',
'trailingPegRatio',
'address2',
'fax',
'irWebsite',
'revenueGrowth',
'totalAssets',
'navPrice',
'category',
'ytdReturn',
'beta3Year',
'fundFamily',
'fundInceptionDate',
'legalType',
'threeYearAverageReturn',
'fiveYearAverageReturn',
'grossProfits',
'yield',
'industrySymbol',
]

bishop_symbols_keep = [
    'sector',
'longBusinessSummary',
'fullTimeEmployees',
'dividendRate',
'trailingPE',
'forwardPE',
'fiftyTwoWeekLow',
'fiftyTwoWeekHigh',
'shortRatio',
'shortName',
'longName',
'debtToEquity',
'freeCashflow',
'grossMargins',
]


def save_king_queen(QUEEN_KING):
    QUEEN_KING['king_controls_queen']['buying_powers']['Jq']['total_longTrade_allocation'] = st.session_state['cash_slider']
    PollenDatabase.upsert_data(QUEEN_KING.get('table_name'), QUEEN_KING.get('key'), QUEEN_KING)

def cash_slider(QUEEN_KING, key='cash_slider'):
    cash = QUEEN_KING['king_controls_queen']['buying_powers']['Jq']['total_longTrade_allocation']
    cash = max(min(cash, 1), -1)
    return st.slider("Cash %", min_value=-1.0, max_value=1.0, value=cash, on_change=lambda: save_king_queen(QUEEN_KING), key=key)

def sneak_peak_form():
    # if st.session_state['SneakQueen']:
    # if cust_Button("misc/bee.png", hoverText='SneakPeak', key='SneakQueen', default=False, height=f'53px'): # "https://cdn.onlinewebfonts.com/svg/img_562964.png"
    with st.form("Sneak Peak Access"):
        st.session_state["sneak_peak"] = True
        # sneak_name = st.text_input("Your Name", key='sneak_name')
        # sneak_pw = st.text_input("Sneak Key", key='sneak_key')
        if st.form_submit_button("Watch a Live Bot", use_container_width=True):
            # if len(sneak_name) == 0:
            #     st.error("Enter Your Name To Get In")
            #     st.stop()
            # if sneak_pw.lower() != os.environ.get("quantqueen_pw"):
            #     st.error("Incorrect Password")
            #     st.stop()
            st.session_state['sneak_pw'] = os.environ.get("quantqueen_pw")
            # switch_page("LiveBot")
            st.switch_page("pages/LiveBot.py")
            
            return True
    
    return False


def display_for_unAuth_client_user(pct_queens_taken=89):
    # newuser = st.button("New User")
    # signin_button = st.button("SignIn")

    
    cols = st.columns((6, 7, 2))
    # with cols[0]:
    #     st.subheader("Create an Account To Get a QueenTraderBot")
    # with cols[1]:
    #     progress_bar(
    #         value=pct_queens_taken, text=f"{100-pct_queens_taken} Trading Bots Available"
    #     )
    # with cols[2]:
    sneak_peak_form()

                    

    page_line_seperator("25")
    # sneak_peak = st.button("Watch a QueenBot Trade Live")
    # if sneak_peak:
        # switch_page("LiveBot")
    # st.error(
    #     "ONLY a limited number of Queens Available!! Please contact pollenq.queen@gmail.com for any questions"
    # )

    page_line_seperator("1")



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
                            new_rules_confirmation[ticker].append(new_rule)

    if save:
        st.write(new_rules_confirmation)
        if pg_migration:
            PollenDatabase.upsert_data(QUEEN_KING.get('table_name'), QUEEN_KING.get('key'), QUEEN_KING)
        else:
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

def admin_check(admin_pq, users_allowed_queen_email):
    if admin_pq:
        admin = True
        st.session_state['admin'] = True
    if st.session_state['admin'] == True:
        with st.sidebar:
            with st.expander("admin user"):
                admin_client_user = st.selectbox('admin client_users', options=users_allowed_queen_email, index=users_allowed_queen_email.index(st.session_state['username']))
                if st.button('admin change user', use_container_width=True):
                    st.session_state['admin__client_user'] = admin_client_user
                    st.session_state["prod"] = False
                    st.session_state['prod'], st.session_state['db_root'] = setup_instance(client_username=admin_client_user, switch_env=False, force_db_root=False, queenKING=True)
                    st.rerun()

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

    script_path = os.path.join(hive_master_root(), 'api.py')

    try:
        # Use sys.executable to get the path to the Python interpreter
        python_executable = sys.executable
        subprocess.run([python_executable, script_path, '-i'])
    except FileNotFoundError:
        print(f"Error: Python interpreter not found. Make sure Python is installed.")
    except Exception as e:
        print(f"Error: {e}")

def clean_out_app_requests(QUEEN, QUEEN_KING, request_buckets, prod):
    save = False
    for req_bucket in request_buckets:
        if req_bucket not in QUEEN_KING.keys():
            st.write("Verison Missing DB: ", req_bucket)
            continue
        for app_req in QUEEN_KING[req_bucket]:
            if app_req['app_requests_id'] in QUEEN['app_requests__bucket']:
                print(app_req)
                archive_bucket = f'{req_bucket}{"_requests"}'
                QUEEN_KING[req_bucket].remove(app_req)
                QUEEN_KING[archive_bucket].append(app_req)
                save = True
    if save:
        if pg_migration:
            table_name = 'client_user_store' if prod else "client_user_store_sandbox"
            PollenDatabase.upsert_data(table_name, QUEEN_KING.get('key'), QUEEN_KING)
        else:
            PickleData(pickle_file=QUEEN_KING.get('source'), data_to_store=QUEEN_KING, console="Cleared APP Requests")
            st.success(f"Cleared App Request from {request_buckets}")
    
    return True

@st.cache_data(ttl=timedelta(days=1))
def fetch_portfolio_history(_api, period='3M', timeframe='1D'):
    try:
        # Fetch portfolio history
        portfolio_history = _api.get_portfolio_history(
            period=period,  # Options: '1D', '7D', '1M', '3M', '6M', '1A' -> for year
            timeframe=timeframe,  # Options: '1Min', '5Min', '15Min', '1H', '1D'
        )

        # Convert response to dictionary for better readability
        history = portfolio_history._raw
        df = pd.DataFrame(history)

        df = df[df['profit_loss'] != 0]
        print(len(df), "rows in portfolio history for period:", period)

        return df
    except Exception as e:
        print("Error fetching portfolio history:", e)

def pollenq(sandbox=False, demo=False):
    # st.write("pollenq", demo, sandbox)
    # print("pollenq", demo, sandbox)
    pollen = 'pollen' if not demo else 'demo'
    # check if page is sandbox and prod, if so go to pollen.py

    main_page_start = datetime.now()
    king_G = kingdom__global_vars()
    main_root = hive_master_root()
    load_dotenv(os.path.join(main_root, ".env"))
    set_streamlit_page_config_once()

    # st.write(st.query_params)

    ##### QuantQueen #####
    print(f'>>>> pollen START >>>> {return_timestamp_string()}' )


    pq_buttons = pollenq_button_source()
    s = datetime.now(est)

    ##### STREAMLIT #####
    # st.session_state['orders'] = True
    if 'refresh_times' not in st.session_state:
        st.session_state['refresh_times'] = 0
        pq_buttons['chess_board'] = True


    with st.spinner("Verifying Your Scent, Hang Tight"):
        # print(st.session_state)
        if demo:
            admin_pq = False
            st.session_state['admin_pq'] = admin_pq
            client_user = 'stapinskistefan@gmail.com'
            prod = False
            KING = kingdom__grace_to_find_a_Queen()
            st.session_state['sneak_peak'] = True
            st.info("Welcome, feel free to place trades, every trade is handled and management by the AI using TimeSeries Weighted Averages...TimeValueMoney")
            st.session_state['sneak_peak'] = False
            st.session_state["ip_address"] = return_app_ip()
            st.session_state["username"] = client_user
            st.session_state['db_root'] = 'db__stapinskistefan_99757341'
            st.session_state['authorized_user'] = True
            st.session_state['authentication_status'] = True
            st.session_state['prod'] = False
            qb = init_queenbee(client_user=client_user, prod=prod, orders_v2=True, 
                            queen_king=True, api=True, init=True, 
                            revrec=True, 
                            demo=True)
            QUEEN_KING = qb.get('QUEEN_KING')
            api = qb.get('api')
            revrec = qb.get('revrec')
        else:
            authenticator = signin_main(page="pollenq")
    
    admin_pq = st.session_state.get('admin', False)
    if st.session_state['authentication_status'] != True: ## None or False
        st.warning("Sign In")
        display_for_unAuth_client_user()
        st.stop()
    prod = st.session_state['prod']
    
    if not demo:
        if sandbox and prod:
            st.switch_page('pollen.py')
        if not sandbox and not prod:
            st.switch_page('pages/sandbox.py')
    
    # check if main
    authorized_user = st.session_state['authorized_user']
    client_user = st.session_state["username"]
    
    if authorized_user != True:
        st.error("Your Account is Not Yet Authorized by a pollenq admin")
        authenticator.logout("Logout", location='sidebar')
        if sneak_peak_form():
            pass
        else:
            st.stop()

    ip_address = st.session_state['ip_address'] # return_app_ip()
    # db_root = st.session_state['db_root']

    st.session_state['sneak_name'] = ' ' if 'sneak_name' not in st.session_state else st.session_state['sneak_name']
    # print("SNEAKPEAK", st.session_state['sneak_name'], st.session_state['username'], return_timestamp_string())

    # HEADER
    cols = st.columns((1,2,2,4))
    with cols[0]:
        header_text = st.empty()
        height=50
        prod_name = "Switch to Sandbox" if prod else "Switch to Live"
        image__ = "misc/power.png" if prod else "misc/bitcoin_spinning.gif"
        prod_switch = cust_Button(image__, hoverText=f'{prod_name}', key=f'switch_env', default=False, height=f'{height}px') # "https://cdn.onlinewebfonts.com/svg/img_562964.png"
    with cols[1]:
        header_text_1 = st.empty()

    with header_text_1.container():
        if not prod:
            mark_down_text("SandBox Account", fontsize="28", color="#a8b702", align="left")
        else:
            mark_down_text("Live Account", fontsize="28", color="#03457C", align="left")

        # if show_acct:
        with cols[3]:
        # Show all portfolio history periods in columns
            periods = ["title", '7D', '1M', '3M', '6M', '1A']
            perf_cols = st.columns(len(periods))
            perf_containers = [col.container() for col in perf_cols]


    table_name = 'db' if prod else 'db_sandbox'
    if not demo:
        KING = kingdom__grace_to_find_a_Queen()
        users, all_users = return_all_client_users__db()
        admin_check(admin_pq, all_users['email'].tolist())
        if 'admin__client_user' in st.session_state:
            client_user = st.session_state['admin__client_user']

        if st.session_state['admin']:
            if st.sidebar.button("Refresh Ticker Universe to KING"):
                ticker_universe = return_Ticker_Universe()
                KING['alpaca_symbols_dict'] = ticker_universe.get('alpaca_symbols_dict')
                KING['alpaca_symbols_df'] = ticker_universe.get('alpaca_symbols_df')
                if pg_migration:
                    PollenDatabase.upsert_data(table_name, KING.get('key'), KING)
                else:
                    PickleData(KING.get('source'), KING)
                    st.success("KING Saved")

    menu_id = sac_menu_buttons(pollen)
    # with cols[0]:
    with st.sidebar:
        st.write(f'menu selection {menu_id}')
    if menu_id == 'PlayGround':
        from pages.playground import PlayGround

        print(menu_id)
        print("PLAYGROUND")
        PlayGround()
        st.stop()
    
    # if menu_id == 'Account':
        # switch_page('account')

    if menu_id == 'Orders':
        # switch_page('orders')
        # queen_orders = pd.DataFrame([create_QueenOrderBee(queen_init=True)])

        # active_order_state_list = king_G.get('active_order_state_list')
        # config_cols = config_orders_cols(active_order_state_list)
        # missing_cols = [i for i in queen_orders.iloc[-1].index.tolist() if i not in config_cols.keys()]
        # order_grid(client_user, config_cols, KING, missing_cols, ip_address, seconds_to_market_close)

        st.stop()

    if menu_id == 'Trading Models':
        st.switch_page('pages/trading_models.py')

    if menu_id == 'Portfolio Allocations':
        st.switch_page('pages/chessboard.py')

    print("WORKING")
    with st.spinner("Trade Carefully And Trust the Queens Trades"):

        ####### Welcome to Pollen ##########

        # use API keys from user            
        prod = False if 'sneak_peak' in st.session_state and st.session_state['sneak_peak'] else prod
        sneak_peak = True if 'sneak_peak' in st.session_state and st.session_state['sneak_peak'] else False
        sneak_peak = True if client_user == 'stefanstapinski@yahoo.com' else False
        if not demo:
            qb = init_queenbee(client_user=client_user, prod=prod, queen_king=True, api=True, init=True, revrec=True, pg_migration=pg_migration)
            api = qb.get('api')
            revrec = qb.get('revrec')
            # QUEEN = qb.get('QUEEN')
            QUEEN_KING = qb.get('QUEEN_KING')

        with cols[1]:
            cash = QUEEN_KING['king_controls_queen']['buying_powers']['Jq']['total_longTrade_allocation']
            cash = max(min(cash, 1), -1)
            QUEEN_KING['king_controls_queen']['buying_powers']['Jq']['total_longTrade_allocation'] = cash_slider(QUEEN_KING)


        if st.sidebar.button("Clear App Requests"):
            QUEEN = init_queenbee(client_user=client_user, prod=prod, queen=True).get('QUEEN')
            clean_out_app_requests(QUEEN=QUEEN, QUEEN_KING=QUEEN_KING, request_buckets=['subconscious', 'sell_orders', 'queen_sleep', 'update_queen_order'], prod=prod)

        with st.sidebar:
            # with st.expander("admin"):
            cust_Button("misc/bee.jpg", hoverText='admin users', key='admin_users', height='34px')
            cust_Button("misc/bee.jpg", hoverText='send queen', key='admin_queens', height='34px')

        # if st.session_state.get('admin_queens'):
        #     admin_send_queen_airflow(KING)
        if st.session_state.get('admin_users'):
            admin_queens_active(KING, all_users)
        

        if sneak_peak:
            st.info("Preview")
            pass
        else:
            switch_env = f'{"Switch to Sandbox" if prod else "Switch to Prod"}'
            live_sb_button = st.sidebar.button(switch_env, key='pollenq', use_container_width=True)
            if live_sb_button or prod_switch:
                st.session_state['prod'], st.session_state['db_root'] = setup_instance(client_username=st.session_state["username"], switch_env=True, force_db_root=False, queenKING=True)
                prod = st.session_state['prod']
                st.session_state['env'] = prod
                if not prod:
                    st.switch_page('pages/sandbox.py')
                else:
                    st.switch_page('pollen.py')
        


        table_name = "client_user_store" if prod else 'client_user_store_sandbox'
        
        if not demo:
            stop_queenbee(QUEEN_KING, sidebar=True, pg_migration=pg_migration, table_name=table_name)

        init_swarm_dbs(prod, init=True)


        ## add new keys add new keys should come from KING timestamp or this becomes a airflow job
        if st.sidebar.button("Check for new KORs"):
            QUEEN_KING = add_new_trading_models_settings(QUEEN_KING) ## fix to add new keys at global level, star level, trigbee/waveBlock level
        
        
        APP_req = add_key_to_app(QUEEN_KING)
        QUEEN_KING = APP_req['QUEEN_KING']
        if APP_req['update']:
            print("Updating QK db")
            if pg_migration:
                PollenDatabase.upsert_data(QUEEN_KING.get('table_name'), QUEEN_KING.get('key'), QUEEN_KING)
            else:
                PickleData(QUEEN_KING.get('source'), QUEEN_KING, console=True)

        if st.sidebar.button('show_keys'):
            queen__account_keys(QUEEN_KING=QUEEN_KING, authorized_user=authorized_user, show_form=True) #EDRXZ Maever65teo

        try:
            if not api:
                queen__account_keys(QUEEN_KING=QUEEN_KING, authorized_user=authorized_user, show_form=True) #EDRXZ Maever65teo
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
            acct_info = alpaca_acct_info.get('info_converted')
            acct_info_raw = alpaca_acct_info.get('info')

        except Exception as e:
            st.error(e)
            acct_info = False
            queen__account_keys(QUEEN_KING=QUEEN_KING, authorized_user=authorized_user, show_form=True) #EDRXZ Maever65teo
            st.stop()

        ### TOP OF PAGE
        if st.session_state['admin']:
            if check_fastapi_status(ip_address) == False:
                st.error("api")
                if st.button('API'):
                    run_pq_fastapi_server()

        if 'chess_board__revrec' not in QUEEN_KING.keys():
            print("SETUP QUEEN KING")
            st.session_state['chessboard_setup'] = True
            # switch_page('chessboard')
            st.switch_page('pages/chessboard.py')

        # QUEENsHeart = init_queenbee(client_user=client_user, prod=prod, queen=True, queen_heart=True, pg_migration=False).get('QUEENsHeart')
        # st.write(QUEENsHeart)
        # if 'storygauge' not in revrec.keys(): # NOT NEEDED?



        trading_days = hive_dates(api=api)['trading_days']
        # st.write(trading_days) # STORE IN KING and only call once
        mkhrs = return_market_hours(trading_days=trading_days)
        seconds_to_market_close = (datetime.now(est).replace(hour=16, minute=0, second=0) - datetime.now(est)).total_seconds()

        
        seconds_to_market_close = abs(seconds_to_market_close) if seconds_to_market_close > 0 else 8
        if mkhrs != 'open':
            seconds_to_market_close = 1
        st.session_state['mkhrs'] = mkhrs
        st.session_state['seconds_to_market_close'] = seconds_to_market_close

        if menu_id == 'Engine':
            from pages.pollen_engine import pollen_engine
            pollen_engine(acct_info_raw)

        # Show all portfolio history periods in columns
    for i, period in enumerate(periods):
        if i == 0:
            with perf_containers[i]:
                # mark_down_text('Portfolio', fontsize='23')
                cust_Button("misc/dollar-symbol-unscreen.gif", hoverText='Portfolio', key='portfolio_ahe', )
        else:
            df = fetch_portfolio_history(api, period=period)
            
            if df is not None and not df.empty:
                portfolio_perf = round((df.iloc[-1]['equity'] - df.iloc[0]['equity']) / df.iloc[0]['equity'] * 100, 2)
                with perf_containers[i]:
                    color = "#1d982b" if portfolio_perf > 0 else "#ff4136"
                    mark_down_text(f'{period}', fontsize='18', color="#888", align="center")
                    mark_down_text(f'{portfolio_perf}%', fontsize='23', color=color, align="center")


    if 'pollen' in menu_id:
        refresh_sec = 8 if seconds_to_market_close > 0 and mkhrs == 'open' else 63000
        # account_header_grid(client_user, prod, refresh_sec, ip_address, seconds_to_market_close)
        queens_conscience(prod, revrec, KING, QUEEN_KING, api)

    st.session_state['refresh_times'] += 1
    page_line_seperator('5')
    table_name = 'client_user_store' if prod else 'client_user_store_sandbox'
    if st.button("Reset Queen Controls"):
        king_controls_queen=return_queen_controls(stars)
        QUEEN_KING['king_controls_queen'] = king_controls_queen
        if st.session_state.get('pg_migration'):
            PollenDatabase.upsert_data(table_name=table_name, key=QUEEN_KING.get('key'), value=QUEEN_KING)
        else:
            PickleData(QUEEN_KING.get('source'), QUEEN_KING, console="QUEEN CONTROLS RESET")

    print(f'>>>> pollen END >>>> {(datetime.now() - main_page_start).total_seconds()}' )


if __name__ == '__main__':
    # def createParser():
    #     parser = argparse.ArgumentParser()
    #     parser.add_argument ('-admin', default=False)
    #     # parser.add_argument ('-instance', default=False)
    #     return parser
    # parser = createParser()
    # namespace = parser.parse_args()
    # admin_pq = namespace.admin

    pollenq()
    # st.write(st.session_state.items())
