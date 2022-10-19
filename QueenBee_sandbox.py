# QueenBee
import logging
import time
import os
import pandas as pd
import numpy as np
import sys
from dotenv import load_dotenv
import sys
import datetime
import pytz
import ipdb
import shutil
import argparse
# import pandas_ta as ta

# import threading
# import alpaca_trade_api as tradeapi
# import asyncio
# from alpaca_trade_api.rest import TimeFrame, URL
# from alpaca_trade_api.rest_async import gather_with_concurrency, AsyncRest
# from enum import Enum
# from operator import sub
# from queue import Queue
# from signal import signal
# from symtable import Symbol
# from scipy.stats import linregress
# from scipy import stats
# import hashlib
# import json
# from collections import deque
# import tempfile
# from typing import Callable
# import random
# import collections
# import pickle
# from tqdm import tqdm
# from stocksymbol import StockSymbol
# import requests
# from collections import defaultdict


# if prior day abs(change) > 1 ignore ticker for the day! 

def createParser():
    parser = argparse.ArgumentParser()
    parser.add_argument ('-qcp', default="queen")
    parser.add_argument ('-prod', default='false')
    return parser
 
# script arguments
parser = createParser()
namespace = parser.parse_args()
queens_chess_piece = namespace.qcp # 'castle', 'knight' 'queen'
# queens_chess_piece = 'queen'
# prod = False
if queens_chess_piece.lower() not in ['queen']:
    print("wrong chess move")
    sys.exit()
if namespace.prod.lower() == "true":
    prod = True
else:
    prod = False

if prod:
    from QueenHive import order_vars__queen_order_items, generate_TradingModel, return_queen_controls, stars, create_QueenOrderBee, init_pollen_dbs, KINGME, story_view, logging_log_message, createParser, return_index_tickers, return_alpc_portolio, return_market_hours, return_dfshaped_orders, add_key_to_app, pollen_themes, init_app, check_order_status, slice_by_time, split_today_vs_prior, read_csv_db, timestamp_string, read_queensmind, read_pollenstory, speedybee, submit_order, return_timestamp_string, pollen_story, ReadPickleData, PickleData, return_api_keys, return_bars_list, refresh_account_info, return_bars, init_index_ticker, print_line_of_error, add_key_to_QUEEN
else:
    from QueenHive_sandbox import order_vars__queen_order_items, generate_TradingModel, return_queen_controls, stars, create_QueenOrderBee, init_pollen_dbs, KINGME, story_view, logging_log_message, createParser, return_index_tickers, return_alpc_portolio, return_market_hours, return_dfshaped_orders, add_key_to_app, pollen_themes, init_app, check_order_status, slice_by_time, split_today_vs_prior, read_csv_db, timestamp_string, read_queensmind, read_pollenstory, speedybee, submit_order, return_timestamp_string, pollen_story, ReadPickleData, PickleData, return_api_keys, return_bars_list, refresh_account_info, return_bars, init_index_ticker, print_line_of_error, add_key_to_QUEEN


# Green Light to Main
pd.options.mode.chained_assignment = None
est = pytz.timezone("US/Eastern")
load_dotenv()
main_root = os.getcwd()
db_root = os.path.join(main_root, 'db')
db_app_root = os.path.join(db_root, 'app')

def init_logging(queens_chess_piece, db_root):
    loglog_newfile = False
    log_dir = dst = os.path.join(db_root, 'logs')
    log_dir_logs = dst = os.path.join(log_dir, 'logs')
    if os.path.exists(dst) == False:
        os.mkdir(dst)
    if prod:
        log_name = f'{"log_"}{queens_chess_piece}{".log"}'
    else:
        log_name = f'{"log_"}{queens_chess_piece}{"_sandbox_"}{".log"}'

    log_file = os.path.join(log_dir, log_name)
    if loglog_newfile:
        # copy log file to log dir & del current log file
        datet = datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S_%p')
        dst_path = os.path.join(log_dir_logs, f'{log_name}{"_"}{datet}{".log"}')
        shutil.copy(log_file, dst_path) # only when you want to log your log files
        os.remove(log_file)
    else:
        # print("logging",log_file)
        logging.basicConfig(filename=log_file,
                            filemode='a',
                            format='%(asctime)s:%(name)s:%(levelname)s: %(message)s',
                            datefmt='%m/%d/%Y %I:%M:%S %p',
                            level=logging.INFO,
                            force=True)
    
    return True

init_logging(queens_chess_piece=queens_chess_piece, db_root=db_root)


# ###### GLOBAL # ######
ARCHIVE_queenorder = 'archived_bee'
active_order_state_list = ['running', 'running_close', 'submitted', 'error', 'pending', 'completed', 'running_open', 'archived_bee']
active_queen_order_states = ['submitted', 'accetped', 'pending', 'running', 'running_close', 'running_open']
closing_queen_orders = ['running_close', 'completed']
RUNNING_Orders = ['running', 'running_close', 'running_open']

# crypto
crypto_currency_symbols = ['BTCUSD', 'ETHUSD', 'BTC/USD', 'ETH/USD']
coin_exchange = "CBSE"


""" Keys """
if prod:
    api_key_id = os.environ.get('APCA_API_KEY_ID')
    api_secret = os.environ.get('APCA_API_SECRET_KEY')
    base_url = "https://api.alpaca.markets"
    keys = return_api_keys(base_url, api_key_id, api_secret, prod=True)
    rest = keys[0]['rest']
    api = keys[0]['api']
else:
    # Paper
    api_key_id_paper = os.environ.get('APCA_API_KEY_ID_PAPER')
    api_secret_paper = os.environ.get('APCA_API_SECRET_KEY_PAPER')
    base_url_paper = "https://paper-api.alpaca.markets"
    keys_paper = return_api_keys(base_url=base_url_paper, 
        api_key_id=api_key_id_paper, 
        api_secret=api_secret_paper,
        prod=False)
    rest = keys_paper[0]['rest']
    api = keys_paper[0]['api']

"""# Dates """
# current_day = api.get_clock().timestamp.date().isoformat()
trading_days = api.get_calendar()
trading_days_df = pd.DataFrame([day._raw for day in trading_days])

current_day = datetime.datetime.now().day
current_month = datetime.datetime.now().month
current_year = datetime.datetime.now().year

# misc
exclude_conditions = [
    'B','W','4','7','9','C','G','H','I','M','N',
    'P','Q','R','T','V','Z'
] # 'U'


index_list = [
    'DJA', 'DJI', 'DJT', 'DJUSCL', 'DJU',
    'NDX', 'IXIC', 'IXCO', 'INDS', 'INSR', 'OFIN', 'IXTC', 'TRAN', 'XMI', 
    'XAU', 'HGX', 'OSX', 'SOX', 'UTY',
    'OEX', 'MID', 'SPX',
    'SCOND', 'SCONS', 'SPN', 'SPF', 'SHLTH', 'SINDU', 'SINFT', 'SMATR', 'SREAS', 'SUTIL']


# if prod: # Return Ticker and Acct Info
#     # Initiate Code File Creation
#     index_ticker_db = os.path.join(db_root, "index_tickers")
#     if os.path.exists(index_ticker_db) == False:
#         os.mkdir(index_ticker_db)
#         print("Ticker Index db Initiated")
#         init_index_ticker(index_list, db_root, init=True)
#     """Account Infomation """
#     acc_info = refresh_account_info(api)
#     # Main Alloc
#     portvalue_LT_iniate = acc_info[1]['portfolio_value'] * Long_Term_Client_Input
#     portvalue_MID_iniate = acc_info[1]['portfolio_value'] * MidDayLag_Alloc
#     portvalue_BeeHunter_iniate = acc_info[1]['portfolio_value'] * DayRiskAlloc

#     # check alloc correct

#     if round(portvalue_BeeHunter_iniate + portvalue_MID_iniate + portvalue_LT_iniate - acc_info[1]['portfolio_value'],4) > 1:
#         print("break in Rev Alloc")
#         sys.exit()

#     """ Return Index Charts & Data for All Tickers Wanted"""
#     """ Return Tickers of SP500 & Nasdaq / Other Tickers"""

#     all_alpaca_tickers = api.list_assets()
#     alpaca_symbols_dict = {}
#     for n, v in enumerate(all_alpaca_tickers):
#         if all_alpaca_tickers[n].status == 'active':
#             alpaca_symbols_dict[all_alpaca_tickers[n].symbol] = vars(all_alpaca_tickers[n])

#     symbol_shortable_list = []
#     easy_to_borrow_list = []
#     for ticker, v in alpaca_symbols_dict.items():
#         if v['_raw']['shortable'] == True:
#             symbol_shortable_list.append(ticker)
#         if v['_raw']['easy_to_borrow'] == True:
#             easy_to_borrow_list.append(ticker)

#     # alpaca_symbols_dict[list(alpaca_symbols_dict.keys())[100]]

#     market_exchanges_tickers = defaultdict(list)
#     for k, v in alpaca_symbols_dict.items():
#         market_exchanges_tickers[v['_raw']['exchange']].append(k)
#     # market_exchanges = ['OTC', 'NASDAQ', 'NYSE', 'ARCA', 'AMEX', 'BATS']


#     main_index_dict = index_ticker_db[0]
#     main_symbols_full_list = index_ticker_db[1]
#     not_avail_in_alpaca =[i for i in main_symbols_full_list if i not in alpaca_symbols_dict]
#     main_symbols_full_list = [i for i in main_symbols_full_list if i in alpaca_symbols_dict]

#     LongTerm_symbols = ['AAPL', 'GOOGL', 'MFST', 'VIT', 'HD', 'WMT', 'MOOD', 'LIT', 'SPXL', 'TQQQ']


#     index_ticker_db = return_index_tickers(index_dir=os.path.join(db_root, 'index_tickers'), ext='.csv')

#     """ Return Index Charts & Data for All Tickers Wanted"""
#     """ Return Tickers of SP500 & Nasdaq / Other Tickers"""    

####<>///<>///<>///<>///<>/// ALL FUNCTIONS NECTOR ####<>///<>///<>///<>///<>///


print(
"""
We all shall prosper through the depths of our connected hearts,
Not all will share my world,
So I put forth my best mind of virtue and goodness, 
Always Bee Better
""", timestamp_string()
)


def update_queen_order(QUEEN, update_package):
    # pollen = read_queensmind(prod)
    # QUEEN = pollen['queen']
    # update_package client_order id and field updates {client_order_id: {'queen_order_status': 'running'}}
    for c_order_id in update_package.keys():
        order_sel = {idx: i for idx, i in enumerate(QUEEN['queen_orders']) if i['client_order_id'] == c_order_id}
        order_idx = list(order_sel.keys())[0]
        for field_, new_value in update_package[c_order_id].items():
            QUEEN['queen_orders'][order_idx][field_] = new_value
    
    return True


def submit_order_validation(ticker, qty, side, portfolio, run_order_idx=False):
    
    if side == 'buy':
        # if crypto check avail cash to buy
        # check against buying power validate not buying too much of total portfolio
        return {'qty_correction': qty}
    else: # sel == sell
        # print("check portfolio has enough shares to sell")
        position = float(portfolio[ticker]['qty_available'])
        if position > 0 and position < qty: # long
            msg = {"submit order validation()": {'#of shares avail': position,  'msg': "not enough shares avail to sell, updating sell qty", 'ticker': ticker}}
            logging.error(msg)
            print(msg)
            # QUEEN["errors"].update({f'{symbol}{"_portfolio!=queen"}': {'msg': msg}})
            
            qty_correction = position
            if run_order_idx:
                # update run_order
                print('Correcting Run Order Qty with avail qty: ', qty_correction)
                QUEEN['queen_orders'][run_order_idx]['qty_available'] = qty_correction
                QUEEN['queen_orders'][run_order_idx]['validation_correction'] = 'true'
        
            return {'qty_correction': qty_correction}
        else:
            return {'qty_correction': qty}


def generate_client_order_id(QUEEN, ticker, trig, sellside_client_order_id=False): # generate using main_order table and trig count
    main_orders_table = pd.DataFrame(QUEEN['queen_orders'])
    temp_date = datetime.datetime.now().strftime("%y%m%d-%M.%S")
    
    if sellside_client_order_id:
        main_trigs_df = main_orders_table[main_orders_table['client_order_id'] == sellside_client_order_id].copy()
        trig_num = len(main_trigs_df)
        order_id = f'{"close__"}{trig_num}-{sellside_client_order_id}-{temp_date}'
    else:
        main_trigs_df = main_orders_table[(main_orders_table['trigname']==trig) & (main_orders_table['exit_order_link'] != 'False')].copy()
        
        trig_num = len(main_trigs_df)
        order_id = f'{"run__"}{ticker}-{trig}-{trig_num}-{temp_date}'

    if order_id in QUEEN['client_order_ids_qgen']:
        msg = {"generate client_order_id()": "client order id already exists change"}
        print(msg)
        logging.error(msg)
        # q_l = len(QUEEN['client_order_ids_qgen'])
        mill_s = datetime.datetime.now().microsecond
        order_id = f'{order_id}{"_qgen_"}{mill_s}'

    # append created id to QUEEN
    QUEEN['client_order_ids_qgen'].append(order_id)
    PickleData(pickle_file=PB_QUEEN_Pickle, data_to_store=QUEEN)
    
    return order_id


def initialize_orders(api, start_date, end_date, symbols=False, limit=500): # TBD
    after = start_date
    until = end_date
    if symbols:
        closed_orders = api.list_orders(status='closed', symbols=symbols, after=after, until=until, limit=limit)
        open_orders = api.list_orders(status='open', symbols=symbols, after=after, until=until, limit=limit)
    else:
        closed_orders = api.list_orders(status='closed', after=after, until=until, limit=limit)
        open_orders = api.list_orders(status='open', after=after, until=until, limit=limit)
    
    return {'open': open_orders, 'closed': closed_orders}


def process_order_submission(trading_model, order, order_vars, trig, ticker_time_frame, portfolio_name='Jq', status_q=False, exit_order_link=False, bulkorder_origin__client_order_id=False, system_recon=False, priceinfo=False):

    try:
        # Create Running Order
        new_queen_order = create_QueenOrderBee(trading_model=trading_model,
        KING=KING, order_vars=order_vars, order=order, ticker_time_frame=ticker_time_frame, 
        portfolio_name=portfolio_name, 
        status_q=status_q, 
        trig=trig, 
        exit_order_link=exit_order_link, 
        priceinfo=priceinfo)

        # Append Order
        QUEEN['queen_orders'].append(new_queen_order)

        logging.info("Order Bee Created")

        
        return {'new_queen_order': new_queen_order}
    except Exception as e:
        print(e, print_line_of_error())


def route_order_based_on_status(order_status):
    # https://alpaca.markets/docs/trading/orders/#order-lifecycle
    accepted_orders = ['accepted', 'pending_new', 'accepted_for_bidding', 'filled', 'partially_filled', 'new', 'calculated']
    failed_orders = ['canceled', 'expired', 'replaced', 'pending_cancel', 'pending_replace', 'stopped', 'rejected', 'suspended']
    if order_status in accepted_orders:
        return True
    elif order_status in failed_orders:
        return False
    else:
        msg={order_status: ": unknown error"}
        print(msg)
        logging.error(msg)


def process_app_requests(QUEEN, APP_requests, request_name, archive_bucket):
    # APP_requests = ReadPickleData(pickle_file=PB_App_Pickle)
    
    if request_name == "buy_orders":
        archive_bucket = 'app_order_requests'
        app_order_base = [i for i in APP_requests[request_name]]
        if app_order_base:
            for app_request in app_order_base:
                if app_request['app_requests_id'] in QUEEN['app_requests__bucket']:
                    print("buy trigger request Id already received")
                    APP_requests[archive_bucket].append(app_request)
                    APP_requests[request_name].remove(app_request)
                    PickleData(pickle_file=PB_App_Pickle, data_to_store=APP_requests)
                    return {'order_flag': False,}
                else:
                    print("app buy order gather")
                    wave_amo = app_request['wave_amo']
                    r_type = app_request['type']
                    r_side = app_request['side']
                
                    king_resp = {'side': r_side, 'type': r_type, 'wave_amo': wave_amo }
                    ticker_time_frame = f'{app_request["ticker"]}{"_app_bee"}'

                    # remove request
                    APP_requests[archive_bucket].append(app_request)
                    APP_requests[request_name].remove(app_request)
                    PickleData(pickle_file=PB_App_Pickle, data_to_store=APP_requests)
                    
                    return {'king_resp': king_resp, 'order_flag': True, 'app_request': app_request, 'ticker_time_frame': ticker_time_frame,} 
        else:
            return {'order_flag': False}
    
    elif request_name == "wave_triggers":
        archive_bucket = 'app_wave_requests'
        app_order_base = [i for i in APP_requests[request_name]]
        if app_order_base:
            for app_request in app_order_base:
                if app_request['app_requests_id'] in QUEEN['app_requests__bucket']:
                    print("wave trigger request Id already received")
                    APP_requests[archive_bucket].append(app_request)
                    APP_requests[request_name].remove(app_request)
                    PickleData(pickle_file=PB_App_Pickle, data_to_store=APP_requests)
                    return {'app_flag': False}
                else:
                    print("app wave trigger gather", app_request['wave_trigger'], " : ", app_request['ticker_time_frame'])
                    QUEEN['app_requests__bucket'].append(app_request['app_requests_id'])
                    APP_requests[archive_bucket].append(app_request)
                    APP_requests[request_name].remove(app_request)
                    PickleData(pickle_file=PB_App_Pickle, data_to_store=APP_requests)
                    
                    return {'app_flag': True, 'app_request': app_request, 'ticker_time_frame': app_request['ticker_time_frame']}
        else:
            return {'app_flag': False}
    
    elif request_name == "update_queen_order": # buz
        archive_bucket = 'update_queen_order_requests'
        app_order_base = [i for i in APP_requests[request_name]]
        if app_order_base:
            for app_request in app_order_base:
                if app_request['app_requests_id'] in QUEEN['app_requests__bucket']:
                    print("queen update order trigger request Id already received")
                    APP_requests[archive_bucket].append(app_request)
                    APP_requests[request_name].remove(app_request)
                    PickleData(pickle_file=PB_App_Pickle, data_to_store=APP_requests)
                    return {'app_flag': False}
                else:
                    print("queen update order trigger gather", app_request['queen_order_update_package'], " : ", app_request['ticker_time_frame'])
                    QUEEN['app_requests__bucket'].append(app_request['app_requests_id'])
                    APP_requests[archive_bucket].append(app_request)
                    APP_requests[request_name].remove(app_request)
                    PickleData(pickle_file=PB_App_Pickle, data_to_store=APP_requests)
                    
                    return {'app_flag': True, 'app_request': app_request, 'ticker_time_frame': app_request['ticker_time_frame']}
        else:
            return {'app_flag': False}    

    elif request_name == "power_rangers": ## buz
        # archive_bucket = "power_rangers_requests"
        # power rangers
        all_items = [i for i in APP_requests[request_name]]
        if all_items:
            for app_request in all_items:
                if app_request['app_requests_id'] in QUEEN['app_requests__bucket']:
                    print("Power Rangers trigger request Id already received")
                    APP_requests[archive_bucket].append(app_request)
                    APP_requests[request_name].remove(app_request)
                    PickleData(pickle_file=PB_App_Pickle, data_to_store=APP_requests)
                    return {'app_flag': False}
                else:
                    print("Power Ranger Change")
                    QUEEN['app_requests__bucket'].append(app_request['app_requests_id'])
                    APP_requests[archive_bucket].append(app_request)
                    APP_requests[request_name].remove(app_request)
                    PickleData(pickle_file=PB_App_Pickle, data_to_store=APP_requests)

                    #Update Rangers
                    # control_name = app_request['control_name']
                    
                    for ranger, update_value in app_request['rangers_values'].items():
                        QUEEN['queen_controls'][request_name][app_request['star']][app_request['wave_type']][app_request['wave_']][app_request['theme_token']][ranger] = update_value
                        logging_log_message(log_type='info', msg=(ranger, " :updated to: ", update_value ), origin_func='process app requests')
                    # msg = ('control updated:: ', control_name)
                    # print(msg)
                    # logging.info(msg)

                    
                    return {'app_flag': True, 'app_request': app_request}
        else:
            return {'app_flag': False}

    elif request_name == "knight_bees_kings_rules": ## PEDNIGN
        return False
        archive_bucket = "knight_bees_kings_rules_requests"
        all_items = [i for i in APP_requests[request_name]]
        if all_items:
            for app_request in all_items:
                if app_request['app_requests_id'] in QUEEN['app_requests__bucket']:
                    print("Knight Bees request Id already received")
                    APP_requests[archive_bucket].append(app_request)
                    APP_requests[request_name].remove(app_request)
                    PickleData(pickle_file=PB_App_Pickle, data_to_store=APP_requests)
                    return {'app_flag': False}
                else:
                    print("Knight Bees Change")
                    QUEEN['app_requests__bucket'].append(app_request['app_requests_id'])
                    APP_requests[archive_bucket].append(app_request)
                    APP_requests[request_name].remove(app_request)
                    PickleData(pickle_file=PB_App_Pickle, data_to_store=APP_requests)
                    
                    return {'app_flag': True, 'app_request': app_request}
        else:
            return {'app_flag': False}

    elif request_name == "del_QUEEN_object": # PENDING
        archive_bucket = "del_QUEEN_object_requests"
        all_items = [i for i in APP_requests[request_name]]
        if all_items:
            for app_request in all_items:
                if app_request['app_requests_id'] in QUEEN['app_requests__bucket']:
                    print("Knight Bees request Id already received")
                    APP_requests[archive_bucket].append(app_request)
                    APP_requests[request_name].remove(app_request)
                    PickleData(pickle_file=PB_App_Pickle, data_to_store=APP_requests)
                    return {'app_flag': False}
                else:
                    print("Del Queen Object")
                    QUEEN['app_requests__bucket'].append(app_request['app_requests_id'])
                    APP_requests[archive_bucket].append(app_request)
                    APP_requests[request_name].remove(app_request)
                    PickleData(pickle_file=PB_App_Pickle, data_to_store=APP_requests)

                    # remove object from QUEEN
                    # key_to_del
                    # QUEEN[]
                    
                    return {'app_flag': True, 'app_request': app_request}
        else:
            return {'app_flag': False}

    elif request_name == "stop_queen": #buz
        if APP_requests[request_name] == 'true':
            logging.info(("app stopping queen"))
            print("exiting QUEEN stopping queen")
            APP_requests[request_name] = 'false'
            PickleData(pickle_file=PB_App_Pickle, data_to_store=APP_requests)
            sys.exit()
        else:
            return {'app_flag': False}
    
    elif request_name == 'queen_controls_reset':
        if APP_requests[request_name] == 'true':
            print("All Queen Controls Reset")
            logging.info(("refreshed queen controls"))
            # save app
            APP_requests[request_name] = 'false'
            PickleData(pickle_file=PB_App_Pickle, data_to_store=APP_requests)
            # save queen
            QUEEN['queen_controls'] = return_queen_controls()
            PickleData(pickle_file=PB_QUEEN_Pickle, data_to_store=QUEEN)
        
    elif request_name == "queen_controls": # buz
        # archive_bucket = 'queen_controls_requests'
        app_order_base = [i for i in APP_requests[request_name]]
        if app_order_base:
            for app_request in app_order_base:
                if app_request['app_requests_id'] in QUEEN['app_requests__bucket']:
                    print("queen update order trigger request Id already received")
                    APP_requests[archive_bucket].append(app_request)
                    APP_requests[request_name].remove(app_request)
                    PickleData(pickle_file=PB_App_Pickle, data_to_store=APP_requests)
                    return {'app_flag': False}
                else:
                    print("queen control gather", app_request['request_name'],)
                    QUEEN['app_requests__bucket'].append(app_request['app_requests_id'])
                    APP_requests[archive_bucket].append(app_request)
                    APP_requests[request_name].remove(app_request)
                    PickleData(pickle_file=PB_App_Pickle, data_to_store=APP_requests)

                    # update control
                    control_name = app_request['control_name']
                    QUEEN[request_name][control_name].update(app_request['control_update'])
                    msg = ('control updated:: ', control_name)
                    print(msg)
                    logging.info(msg)

                    
                    return {'app_flag': True, 'app_request': app_request}
        else:
            return {'app_flag': False}    

    elif request_name == 'trading_models':
        app_order_base = [i for i in APP_requests[request_name]]
        if app_order_base:
            for app_request in app_order_base:
                if app_request['app_requests_id'] in QUEEN['app_requests__bucket']:
                    print("App request Id already received")
                    APP_requests[archive_bucket].append(app_request)
                    APP_requests[request_name].remove(app_request)
                    PickleData(pickle_file=PB_App_Pickle, data_to_store=APP_requests)
                    return {'app_flag': False}
                else:
                    print("queen trading model update", app_request['request_name'],)
                    QUEEN['app_requests__bucket'].append(app_request['app_requests_id'])
                    APP_requests[archive_bucket].append(app_request)
                    APP_requests[request_name].remove(app_request)
                    PickleData(pickle_file=PB_App_Pickle, data_to_store=APP_requests)

                    # update trading model
                    trading_model_update = app_request['trading_model_dict']
                    QUEEN['queen_controls']['symbols_stars_TradingModel'].update(trading_model_update)
                    msg = ('trading model updated:: ', trading_model_update)
                    print(msg)
                    logging.info(msg)

                    
                    return {'app_flag': True, 'app_request': app_request}    
    else:
        return {'app_flag': False}


"""  >>>><<<< MAIN <<<<>>>> """
def trig_In_Action_cc(active_orders, trig, ticker_time_frame):
    all_orders = pd.DataFrame(QUEEN['queen_orders'])
    if len(all_orders) == 0:
        return False
    
    if len(active_orders) > 0:
        # print('trig_action ',  len(active_orders))
        active_orders['order_exits'] = np.where(
            (active_orders['trigname'] == trig) &
            (active_orders['ticker_time_frame_origin'] == ticker_time_frame), 1, 0)
        trigbee_orders =  active_orders[active_orders['order_exits'] == 1].copy()
        if len(trigbee_orders) > 0:
            # print('trig in action ',  len(trigbee_orders))
            return trigbee_orders
        else:
            return False
    else:
        return False


def add_app_wave_trigger(all_current_triggers, ticker, app_wave_trig_req):
    if app_wave_trig_req['app_flag'] == False:
        return all_current_triggers
    else:
        if ticker == app_wave_trig_req['app_request']['ticker']:
            all_current_triggers.update(app_wave_trig_req['app_request']['wave_trigger']) # test
            msg = {'add_app_wave_trigger()': 'added wave drone'}
            print(msg)
            # queen process
            logging.info(msg)
            return all_current_triggers
        else:
            return all_current_triggers

def update_origin_order_qty_available(QUEEN, run_order_idx, new_queen_order_index):
    origin_closing_orders_df = return_all_linked_queen_orders(exit_order_link=QUEEN['queen_orders'][run_order_idx]['client_order_id'])
    # origin_closing_orders_df = return_closing_orders_df(exit_order_link=QUEEN['queen_orders'][run_order_idx]['client_order_id'])
    if origin_closing_orders_df != False:
        origin_closing_orders_df['qty'] = origin_closing_orders_df['qty'].apply(lambda x: convert_to_float(x))
        QUEEN['queen_orders'][run_order_idx]['qty_available'] = QUEEN['queen_orders'][run_order_idx]['qty_available'] - sum(origin_closing_orders_df['qty'])
        return True



def execute_order(QUEEN, king_resp, king_eval_order, ticker, ticker_time_frame, trig, portfolio, run_order_idx=False, crypto=False):
    try:
        logging.info({'ex_order()': ticker_time_frame})

        if king_resp:
            side = 'buy'
            # if app order get order vars its way
            if 'order_vars' not in king_resp.keys():
                # up pack order vars
                side = king_resp['side']
                order_type = king_resp['type']
                wave_amo = king_resp['wave_amo']
                limit_price = False
                trading_model = king_resp['order_vars']
            else:
                # up pack order vars
                side = king_resp['order_vars']['order_side']
                order_type = king_resp['order_vars']['order_type']
                wave_amo = king_resp['order_vars']['wave_amo']
                limit_price = king_resp['order_vars']['limit_price']
                trading_model = king_resp['order_vars']['trading_model']

            if side == 'buy':
                if limit_price:
                    limit_price = limit_price
                else:
                    limit_price = False
                # flag crypto
                if crypto:
                    snap = api.get_crypto_snapshot(ticker, exchange=coin_exchange)
                    crypto = True
                else:
                    snap = api.get_snapshot(ticker)
                    crypto = False
                
                # get latest pricing
                current_price = snap.latest_trade.price
                current_bid = snap.latest_quote.bid_price
                current_ask = snap.latest_quote.ask_price
                priceinfo = {'price': current_price, 'bid': current_bid, 'ask': current_ask}
                
                # Adjust for Crypto
                if crypto:
                    qty_order = float(round(wave_amo / current_price, 4))
                else:
                    qty_order = float(round(wave_amo / current_price, 0))

                # validate app order
                def validate_app_order():
                    pass
                
                
                # return num of trig for client_order_id
                client_order_id__gen = generate_client_order_id(QUEEN=QUEEN, ticker=ticker, trig=trig)

                send_order_val = submit_order_validation(ticker=ticker, qty=qty_order, side=side, portfolio=portfolio, run_order_idx=run_order_idx)
                qty_order = send_order_val['qty_correction'] # same return unless more validation done here

                # ORDER TYPES Enter the Market
                order_submit = submit_order(api=api, symbol=ticker, type=order_type, qty=qty_order, side=side, client_order_id=client_order_id__gen, limit_price=limit_price) # buy
                logging.info("order submit")
                order = vars(order_submit)['_raw']
                # print(order['status'])

                # Confirm order went through, end process and write results
                if route_order_based_on_status(order_status=order['status']):
                    
                    process_order_submission(trading_model=trading_model, 
                    order=order, 
                    order_vars=king_resp['order_vars'], 
                    trig=trig, 
                    ticker_time_frame=ticker_time_frame, 
                    priceinfo=priceinfo)

                    PickleData(pickle_file=PB_QUEEN_Pickle, data_to_store=QUEEN)
                    
                    msg = {'execute order()': {'msg': f'{"order submitted"}{" : at : "}{return_timestamp_string()}', 'ticker': ticker, 'ticker_time_frame': ticker_time_frame, 'trig': trig, 'crypto': crypto, 'wave_amo': wave_amo}}
                    logging.info(msg)
                    print(msg)
                    return{'executed': True, 'msg': msg}
                else:
                    msg = ("error order not accepted", order)
                    print(msg)
                    logging.error(msg)
                    return{'executed': False, 'msg': msg}
        elif king_eval_order:
            side = 'sell'
            if side == 'sell':
                print("bee_sell")
                run_order_client_order_id = QUEEN['queen_orders'][run_order_idx]['client_order_id']
                order_vars = king_eval_order['order_vars']

                # close out order variables
                priceinfo = return_snap_priceinfo(api=api, ticker=ticker, crypto=crypto)
                sell_qty = float(king_eval_order['order_vars']['sell_qty']) # float(order_obj['filled_qty'])
                q_side = king_eval_order['order_vars']['order_side'] # 'sell' Unless it short then it will be a 'buy'
                q_type = king_eval_order['order_vars']['order_type'] # 'market'
                sell_reason = king_eval_order['order_vars']['sell_reason']
                limit_price = king_eval_order['order_vars']['limit_price']

                # Generate Client Order Id
                client_order_id__gen = generate_client_order_id(QUEEN=QUEEN, ticker=ticker, trig=trig, sellside_client_order_id=run_order_client_order_id)
                
                # Validate Order
                send_order_val = submit_order_validation(ticker=ticker, qty=sell_qty, side=q_side, portfolio=portfolio, run_order_idx=run_order_idx)
                
                # order_vars
                sell_qty = send_order_val['qty_correction']
                
                send_close_order = submit_order(api=api, side=q_side, symbol=ticker, qty=sell_qty, type=q_type, client_order_id=client_order_id__gen, limit_price=limit_price) 
                send_close_order = vars(send_close_order)['_raw']
                
                if route_order_based_on_status(order_status=send_close_order['status']):
                    print("Did you bring me some Honey?")
                    # Order Vars 
                    new_queen_order = process_order_submission(trading_model=False,
                    order=send_close_order, 
                    order_vars=order_vars, 
                    trig=trig, 
                    exit_order_link=run_order_client_order_id, 
                    ticker_time_frame=ticker_time_frame, 
                    priceinfo=priceinfo)['new_queen_order']

                    new_queen_order_index = return_queen_order_idx(client_order_id=new_queen_order['client_order_id'])
                    # update Origin RUN Order
                    # Limit Order
                    QUEEN['queen_orders'][run_order_idx]['order_trig_sell_stop'] = True
                    # return all linking orders and update qty available?
                    update_origin_order_qty_available(QUEEN=QUEEN, run_order_idx=run_order_idx, new_queen_order_index=new_queen_order_index)

                    QUEEN['queen_orders'][run_order_idx]['sell_reason'].update({client_order_id__gen: {'sell_reason': sell_reason}})

                    PickleData(pickle_file=PB_QUEEN_Pickle, data_to_store=QUEEN)
        else:
            print('Error Ex Order..good luck')
            sys.exit()
    
    except Exception as e:
        print(e, print_line_of_error())
        print(ticker_time_frame)
        log_error_dict = logging_log_message(log_type='error', msg='Failed to Execute Order', error=str(e), origin_func='Execute Order', ticker=ticker)
        logging.error(log_error_dict)
        sys.exit()


def buying_Power_cc(api, client_args="TBD", daytrade=True):
    info = api.get_account()
    argu_validate = ['portfolio', 'daytrade_pct', 'longtrade_pct', 'waveup_pct', 'wavedown_pct']
    
    total_buying_power = info.buying_power # what is the % amount you want to buy?
    
    # portfolio_name = 'Jq'
    # portfolio_buyingpowers = [i for i in QUEEN['queen_controls']['buying_powers'] if i == portfolio_name][0]
    # app_portfolio_day_trade_allowed = float(portfolio_buyingpowers['total_dayTrade_allocation']) #.8
    # app_portfolio_long_trade_allowed = float(portfolio_buyingpowers['total_longTrade_allocation']) #.2
    app_portfolio_day_trade_allowed = .8
    app_portfolio_long_trade_allowed = .2
    if app_portfolio_day_trade_allowed + app_portfolio_long_trade_allowed != 1:
        print("Critical Error Fix buying power numbers")
        sys.exit()
    
    # # wave power allowance
    # app_portfolio_waveup_buying_power = .6
    # app_portfolio_wavedown_buying_power = .4
    # if app_portfolio_waveup_buying_power + app_portfolio_wavedown_buying_power != 1:
    #     print("Critical Error Fix buying power numbers")
    #     sys.exit()
    
    client_total_DAY_trade_amt_allowed = float(app_portfolio_day_trade_allowed) * float(total_buying_power)
    client_total_LONG_trade_amt_allowed = float(app_portfolio_long_trade_allowed) * float(total_buying_power)
    
    return {
        'total_buying_power': total_buying_power,
        'client_total_DAY_trade_amt_allowed': client_total_DAY_trade_amt_allowed, 
        'app_portfolio_day_trade_allowed': app_portfolio_day_trade_allowed,
        'client_total_LONG_trade_amt_allowed': client_total_LONG_trade_amt_allowed,
    }


def last_2_trades(): # change to pull from alpaca and join in by client_order_id?
    df = pd.DataFrame(QUEEN['queen_orders'])
    print(df.iloc[-1][['trigname', 'ticker_time_frame', 'datetime', 'queen_order_state']])
    # print(df.iloc[-2][['trigname', 'ticker_time_frame', 'datetime', 'queen_order_state']])


def star_ticker_WaveAnalysis(STORY_bee, ticker_time_frame, trigbee=False): # buy/sell cross
    """ Waves: Current Wave, answer questions about proir waves """
    # df_waves_story = STORY_bee[ticker_time_frame]['waves']['story']  # df
    # current_wave = df_waves_story.iloc[-1]
    
    token_df = pd.DataFrame(STORY_bee[ticker_time_frame]['waves']['buy_cross-0']).T
    current_buywave = token_df.iloc[0]

    token_df = pd.DataFrame(STORY_bee[ticker_time_frame]['waves']['sell_cross-0']).T
    current_sellwave = token_df.iloc[0]

    if current_buywave['wave_start_time'] > current_sellwave['wave_start_time']:
        current_wave = current_buywave
    else:
        current_wave = current_sellwave


    d_return = {'buy_cross-0': current_buywave, 'sell_cross-0':current_sellwave }
    # trigbees = set(df_waves_story['macd_cross'])

    # d_return = {}
    # for trigbee in trigbees:
    #     if trigbee in available_triggerbees:
    #         df_token = df_waves_story[df_waves_story['macd_cross'] == trigbee].copy()
    #         d_return[trigbee] = df_token.iloc[-1]
    
    # index                                                                 0
    # wave_n                                                               37
    # length                                                              8.0
    # wave_blocktime                                            afternoon_2-4
    # wave_start_time                               2022-08-31 15:52:00-04:00
    # wave_end_time                          2022-08-31 16:01:00.146718-04:00
    # trigbee                                                    sell_cross-0
    # maxprofit                                                        0.0041
    # time_to_max_profit                                                  8.0
    # macd_wave_n                                                           0
    # macd_wave_length                                        0 days 00:11:00    
    

    # wave slices
    # l_wave_blocktime = [i for i in STORY_bee[ticker_time_frame]['waves'].keys() if 'story' not in i]
    # wave_blocktime_slices ={i: '' for i in l_wave_blocktime}
    # total_waves = len(df_waves_story.keys())
    # morning_waves = {k:v for (k,v) in waves.items() if v['wave_blocktime'] == "morning_9-11"}
    # lunch_waves = {k:v for (k,v) in waves.items() if v['wave_blocktime'] == "lunch_11-2"}
    # afternoon_waves = {k:v for (k,v) in waves.items() if v['wave_blocktime'] == "afternoon_2-4"}
    # afterhours_waves = {k:v for (k,v) in waves.items() if v['wave_blocktime'] == "afterhours"}
    # wave_blocktime_slices[] = morning_waves


    return {'current_wave': current_wave, 'current_active_waves': d_return}



def king_knights_requests(QUEEN, avail_trigs, trigbee, ticker_time_frame, trading_model, trig_action, crypto=False):
    # answer all questions for order to be placed, compare against the rules
    # measure len of trigbee how long has trigger been there?
    # Std Deivation from last X trade prices
    
    def knight_request_recon_portfolio():
        # debate if we should place a new order based on current portfolio trades
        pass
    
    def trade_Scenarios(trigbee, wave_amo):
        # Create buying power upgrades depending on the STARS waves
        
        # Current Star Power? the Incremate of macd_tier, macd_state for a given Star

        # if "buy_cross-0" == trigbee:
        #     pass

        return True


    def trade_Allowance():
        # trade is not allowed x% level, if so kill/reduce trade
        return True

    
    def proir_waves():
        # return fequency of prior waves and statement conclusions
        return True


    def its_morphin_time(QUEEN, trigbee, theme, tmodel_power_rangers, ticker, stars_df):
        try:
            # Map in the color on storyview
            power_rangers_universe = ['mac_ranger', 'hist_ranger']
            # queens_star_rangers = [i for i in QUEEN['queen_controls']['power_rangers'].keys() if i in tmodel_power_rangers]
            stars_colors_d = {ranger: dict(zip(stars_df['star'],stars_df[ranger])) for ranger in power_rangers_universe}
            # ticker = 'SPY' # default
            ticker_token = f'{ticker}{"_"}'
            
            # color = .5 # for every star we want both mac and hist power_rangers_universe  
            if 'buy' in trigbee:
                wave_type = 'buy_wave'
            else:
                wave_type = 'sell_wave'
            
            """ Power Up """ # for every models stars, return stars value by its tier color
            power_up = {ranger: 0 for ranger in power_rangers_universe}
            for star, v in tmodel_power_rangers.items(): # 1m 5m, 3M
                if v == 'active':
                    for ranger in power_rangers_universe:
                        PowerRangerColor = stars_colors_d[ranger][f'{ticker_token}{star}'] # COLOR
                        power_up[ranger] += float(QUEEN['queen_controls']['power_rangers'][star][ranger][wave_type][theme][PowerRangerColor]) # star-buywave-theme

            return power_up
        except Exception as e:
            print("power up failed ", e)
            return 0


    try:
        # # # # vars
        ticker, tframe, frame = ticker_time_frame.split("_")
        star_time = f'{tframe}{"_"}{frame}'
        STORY_bee = QUEEN[queens_chess_piece]['conscience']['STORY_bee']
        ticker_priceinfo = return_snap_priceinfo(api=api, ticker=ticker, crypto=crypto)
        trigbee_wave_direction = ['waveup' if 'buy' in trigbee else 'wavedown' ][0]

        # Theme
        theme = QUEEN['queen_controls']['theme'] # what is the theme?

        """Stars Forever Be in Heaven"""
        # Story View, Wave Analysis
        story_view_ = story_view(STORY_bee=STORY_bee, ticker=ticker)
        stars_df = story_view_['df']
        current_macd_cross__wave = star_ticker_WaveAnalysis(STORY_bee=STORY_bee, ticker_time_frame=ticker_time_frame)['current_wave']
        current_wave = star_ticker_WaveAnalysis(STORY_bee=STORY_bee, ticker_time_frame=ticker_time_frame)['current_active_waves'][trigbee]
        current_wave_blocktime = current_wave['wave_blocktime']
        current_wave_amo = pollen_theme_dict[theme][star_time][trigbee_wave_direction][current_wave_blocktime]
        
        # Trading Model Vars
        tmodel_power_rangers = trading_model['power_rangers'] # stars
        king_order_rules = trading_model['trigbees'][trigbee][current_wave_blocktime] # trigbee kings_order_rules
        maker_middle = [ticker_priceinfo['maker_middle'] if trading_model['trade_using_limits'] == 'true' or trading_model['trade_using_limits'] == True else False][0]

        # Total buying power allowed
        bpower_resp = buying_Power_cc(api=api, client_args="TBD", daytrade=True)
        total_buying_power = bpower_resp['total_buying_power']
        client_total_DAY_trade_amt_allowed = bpower_resp['client_total_DAY_trade_amt_allowed']
        app_portfolio_day_trade_allowed = bpower_resp['app_portfolio_day_trade_allowed']
        client_total_LONG_trade_amt_allowed = bpower_resp['client_total_LONG_trade_amt_allowed']

        # total budget
        client_total_DAY_trade_amt_allowed =  float(total_buying_power) * float(app_portfolio_day_trade_allowed) # (10% * ($500,000 * 3%)
        theme_amo = current_wave_amo * client_total_DAY_trade_amt_allowed
        power_up_amo = its_morphin_time(QUEEN=QUEEN, trigbee=trigbee, theme=theme, tmodel_power_rangers=tmodel_power_rangers, ticker=ticker, stars_df=stars_df)
        # print("POWERUP !!!!! ", power_up_amo)
        wave_amo = theme_amo + power_up_amo['mac_ranger'] + power_up_amo['hist_ranger']

        # Index ETF Risk Level
        if ticker in QUEEN['heartbeat']['main_indexes'].keys():
            if 'buy' in trigbee:
                if f'{"long"}{trading_model["index_long_X"]}' in QUEEN['heartbeat']['main_indexes'][ticker].keys():
                    etf_long_tier = f'{"long"}{trading_model["index_long_X"]}'
                    ticker = QUEEN['heartbeat']['main_indexes'][ticker][etf_long_tier]
                else:
                    etf_long_tier = False
            if 'sell' in trigbee:
                if f'{"inverse"}{trading_model["index_inverse_X"]}' in  QUEEN['heartbeat']['main_indexes'][ticker].keys():
                    etf_inverse_tier = f'{"inverse"}{trading_model["index_inverse_X"]}'
                    ticker = QUEEN['heartbeat']['main_indexes'][ticker][etf_inverse_tier]
                else:
                    etf_inverse_tier = False

        # how many trades have we completed today? whats our total profit loss with wave trades
        # should you override your original order rules?
        
        def waterfall_knight_buy_chain(trigbees, trading_model):
            
            
            return False
        
        if trigbee == 'buy_cross-0':
            if crypto:
                kings_blessing = True
                order_vars = order_vars__queen_order_items(trading_model=trading_model,king_order_rules=king_order_rules, order_side='buy', wave_amo=wave_amo, maker_middle=maker_middle, origin_wave=current_wave, power_up_rangers=power_up_amo, ticker_time_frame_origin=ticker_time_frame, wave_at_creation=current_macd_cross__wave)
            else:
                kings_blessing = True
                order_vars = order_vars__queen_order_items(trading_model=trading_model, king_order_rules=king_order_rules, order_side='buy', wave_amo=wave_amo, maker_middle=maker_middle, origin_wave=current_wave, power_up_rangers=power_up_amo, ticker_time_frame_origin=ticker_time_frame, wave_at_creation=current_macd_cross__wave)

            if type(trig_action) != bool:
                # print("evalatue if there is another trade to make on top of current wave")
                if len(trig_action) >= 2:
                    print("won't allow more then 2 double down trades")
                    return {'kings_blessing': False}
                else:
                    now_time = datetime.datetime.now().astimezone(est)
                    trig_action.iloc[-1]['datetime']
                    
                    time_delta = now_time - trig_action.iloc[-1]['datetime']

                if time_delta.seconds > king_order_rules['doubledown_timeduration']:
                    print("Trig In Action Double Down Trade")
                    kings_blessing = True
                    order_vars = order_vars__queen_order_items(trading_model=trading_model, king_order_rules=king_order_rules, order_side='buy', wave_amo=wave_amo, maker_middle=maker_middle, origin_wave=current_wave, power_up_rangers=power_up_amo, ticker_time_frame_origin=ticker_time_frame, double_down_trade=True, wave_at_creation=current_macd_cross__wave)
                    return  {'kings_blessing': kings_blessing, 'ticker': ticker, 'order_vars': order_vars}
                else: 
                    kings_blessing = False
            
            if kings_blessing:
                return {'kings_blessing': kings_blessing, 'ticker': ticker, 'order_vars': order_vars}
            else:
                return {'kings_blessing': False}

        elif trigbee == 'sell_cross-0':
            ## create process of shorting when regular tickers
            if crypto:
                return {'kings_blessing': False}
            else:
                kings_blessing = True
                order_vars = order_vars__queen_order_items(trading_model=trading_model, king_order_rules=king_order_rules, order_side='buy', wave_amo=wave_amo, maker_middle=maker_middle, origin_wave=current_wave, power_up_rangers=power_up_amo, ticker_time_frame_origin=ticker_time_frame, wave_at_creation=current_macd_cross__wave)

            if type(trig_action) != bool:
                trig_action_trades = trig_action
                if len(trig_action_trades) >= 2:
                    print("won't allow more then 2 double down trades")
                    return {'kings_blessing': False}
                now_time = datetime.datetime.now().astimezone(est)
                trig_action_trades.iloc[-1]['datetime']
                
                time_delta = now_time - trig_action_trades.iloc[-1]['datetime']

                if time_delta.seconds > king_order_rules['doubledown_timeduration']:
                    print("Trig In Action Double Down Trade")
                    kings_blessing = True
                    order_vars = order_vars__queen_order_items(trading_model=trading_model, king_order_rules=king_order_rules, order_side='buy', wave_amo=wave_amo, maker_middle=maker_middle, origin_wave=current_wave, power_up_rangers=power_up_amo, ticker_time_frame_origin=ticker_time_frame, double_down_trade=True, wave_at_creation=current_macd_cross__wave)
                    return  {'kings_blessing': kings_blessing, 'ticker': ticker, 'order_vars': order_vars}
                else: 
                    return {'kings_blessing': False}

            return {'kings_blessing': kings_blessing, 'ticker': ticker, 'order_vars': order_vars}

        
        else:
            print("Error New Trig not in Queens Mind: ", trigbee )
            return {'kings_blessing': False}


        # kings_blessing = kings_Blessing(ticker=ticker, trigbee=trigbee, current_wave=current_wave, trig_action=trig_action, total_buying_power=total_buying_power, app_portfolio_day_trade_allowed=app_portfolio_day_trade_allowed, client_total_LONG_trade_amt_allowed=client_total_LONG_trade_amt_allowed, pollen_theme_dict=pollen_theme_dict)

        # return {'kings_blessing': kings_blessing, 'order_vars': order_vars}

    except Exception as e:
        print(e, print_line_of_error(), ticker_time_frame)
        print("logme")


def add_trading_model(QUEEN, ticker, model='tradingmodel1', status='active'):
    trading_models = QUEEN['queen_controls']['symbols_stars_TradingModel']
    if ticker not in trading_models.keys():
        print("Ticker Missing Trading Model Adding Default Model1")
        logging_log_message(msg=f'{ticker}{": added trading model: "}{model}')
        tradingmodel1 = generate_TradingModel(ticker=ticker, status=status)[model]
        QUEEN['queen_controls']['symbols_stars_TradingModel'].update(tradingmodel1)
        PickleData(pickle_file=PB_QUEEN_Pickle, data_to_store=QUEEN)


def command_conscience(api, QUEEN, APP_requests):

    try:
        STORY_bee = QUEEN['queen']['conscience']['STORY_bee']

        refresh_QUEEN_starTickers(QUEEN=QUEEN, STORY_bee=STORY_bee)

        active_tickers = QUEEN['heartbeat']['active_tickers']

        story_tickers = set([i.split("_")[0] for i in list(STORY_bee.keys())])
        portfolio = return_alpc_portolio(api)['portfolio']
        
        app_wave_trig_req = process_app_requests(QUEEN=QUEEN, APP_requests=APP_requests, request_name='wave_triggers', archive_bucket='app_wave_requests')

        all_orders = pd.DataFrame(QUEEN['queen_orders'])
        active_orders = all_orders[all_orders['queen_order_state'].isin(active_queen_order_states)].copy()

        # cycle through stories  # The Golden Ticket    
        for ticker in active_tickers:
            
            # # """ # Accept Ticker """
            # if ticker not in active_tickers:
            #     continue ##### break loop
            
            add_trading_model(QUEEN=QUEEN, ticker=ticker, model='tradingmodel1')
            
            # crypto
            if ticker in crypto_currency_symbols:
                crypto = True
            else:
                crypto = False

            mkhrs = return_market_hours(api_cal=trading_days, crypto=crypto)
            if mkhrs == 'open':
                val_pass = True
            else:
                continue # break loop

            """ hunt """

            ticker_storys = {k:v for (k, v) in STORY_bee.items() if k.split("_")[0] == ticker} # filter by ticker
            all_current_triggers = {k:v['story']['alltriggers_current_state'] for (k,v) in ticker_storys.items() if len(v['story']['alltriggers_current_state']) > 0}
            all_current_triggers = add_app_wave_trigger(all_current_triggers=all_current_triggers, ticker=ticker, app_wave_trig_req=app_wave_trig_req)        
            # all_current_triggers.update({'SPY_1Minute_1Day': ['buy_cross-0']}) # test
            # Return Scenario based trades

            if all_current_triggers:
                try:

                    # enabled stars
                    # QUEEN['heartbeat']

                    for ticker_time_frame, avail_trigs in all_current_triggers.items(): 
                        # ticker_time_frame = f'{ticker}{"_1Minute_1Day"}'
                        ticker, tframe, frame = ticker_time_frame.split("_")
                        frame_block = f'{tframe}{"_"}{frame}' # frame_block = "1Minute_1Day"
                        
                        # validation trading model
                        if ticker not in QUEEN['queen_controls']['symbols_stars_TradingModel'].keys():
                            print("error defaulting to SPY Model")
                            logging.error(("error TICKER not in trading models ", ticker))
                            trading_model = QUEEN['queen_controls']['symbols_stars_TradingModel']['SPY'][frame_block]
                        elif frame_block not in QUEEN['queen_controls']['symbols_stars_TradingModel'][ticker].keys():
                            print("error defaulting to 1Minute Star Ranger")
                            logging.error(("error STAR not in trading models ", ticker))
                            trading_model = QUEEN['queen_controls']['symbols_stars_TradingModel']['SPY']['1Minute_1Day']
                        else:
                            trading_model = QUEEN['queen_controls']['symbols_stars_TradingModel'][ticker][frame_block]

                        if str(trading_model['status']) not in ['active']:
                            print("model not active", ticker_time_frame, " availtrigs: ", avail_trigs)
                            continue
                        # if frame_block != "1Minute_1Day":
                        #     print("model not active", tframe)
                        #     continue

                        # cycle through triggers and pass buy first logic for buy
                        # trigs =  all_current_triggers[f'{ticker}{"_1Minute_1Day"}']
                        for trig in avail_trigs:
                            if trig in trading_model['trigbees'].keys():
                                if str(trading_model['trigbees'][trig]['status']) != 'active':
                                    print("model not active", ticker_time_frame, " availtrigs: ", avail_trigs)
                                    continue
                                
                                # check if you already placed order or if a workerbee in transit to place order
                                trig_action = trig_In_Action_cc(active_orders=active_orders, trig=trig, ticker_time_frame=ticker_time_frame)

                                """ HAIL TRIGGER, WHAT SAY YOU?
                                ~forgive me but I bring a gift for the king and queen
                                """
                                king_resp = king_knights_requests(QUEEN=QUEEN, avail_trigs=avail_trigs, trigbee=trig, ticker_time_frame=ticker_time_frame, trading_model=trading_model, trig_action=trig_action, crypto=crypto)
                                if king_resp['kings_blessing']:
                                    # last_2_trades()
                                    execute_order(QUEEN=QUEEN, king_resp=king_resp, king_eval_order=False, ticker=king_resp['ticker'], ticker_time_frame=ticker_time_frame, trig=trig, portfolio=portfolio, crypto=crypto)

                    
                except Exception as e:
                    print(e, print_line_of_error())
                    print(ticker_time_frame)
                    sys.exit()

    
        # App Buy Order Requests
        app_resp = process_app_requests(QUEEN=QUEEN, APP_requests=APP_requests, request_name='buy_orders', archive_bucket='app_order_requests')
        if app_resp['order_flag']:
            msg = {'process_app_buy_requests()': 'queen processed app request'}
            print(msg)
            # queen process
            logging.info(msg)
            APP_requests['queen_processed_orders'].append(app_resp['app_request']['app_requests_id'])
            QUEEN['app_requests__bucket'].append(app_resp['app_request']['app_requests_id'])
            PickleData(PB_App_Pickle, APP_requests)

            crypto = [True if app_resp['app_request']['ticker'] in crypto_currency_symbols else False][0]
            
            # execute order
            bzzz = execute_order(QUEEN=QUEEN, 
            trig=app_resp['app_request']['trig'], 
            king_resp=app_resp['king_resp'],
            king_eval_order=False,
            ticker=app_resp['app_request']['ticker'], 
            ticker_time_frame=app_resp['ticker_time_frame'],
            portfolio=portfolio,
            crypto=crypto)


        return True
    except Exception as e:
        print('wtf', e, print_line_of_error())



""">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> ORDER MANAGEMENT <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< """
""">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> ORDER MANAGEMENT <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< """
""">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> ORDER MANAGEMENT <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< """
""">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> ORDER MANAGEMENT <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< """
""">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> ORDER MANAGEMENT <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< """
""">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> ORDER MANAGEMENT <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< """
""">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> ORDER MANAGEMENT <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< """
""">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> ORDER MANAGEMENT <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< """


def order_past_duration(queen_order):
    nowtime = datetime.datetime.now().astimezone(est)
    qorder_time = queen_order['datetime'].astimezone(est)
    duration_rule = queen_order['order_rules']['timeduration']
    order_time_delta = nowtime - qorder_time
    # order_time_delta.total_seconds()
    # duration_divide_time = {'1Minute': 60, "5Minute": }
    if "1Minute" in queen_order['ticker_time_frame']:
        if (order_time_delta.seconds / 60) > duration_rule:
            return (order_time_delta.seconds / 60) - duration_rule


def process_app_sell_signal(QUEEN, PB_App_Pickle, runorder_client_order_id): # ONLY returns if not empty
    """Read App Controls and update if anything new"""
    # app_request = QUEEN['queen_controls']['orders']
    APP_requests = ReadPickleData(pickle_file=PB_App_Pickle)
    app_order_base = [i for i in APP_requests['sell_orders']]
    c_order_ids = {idx: i for idx, i in enumerate(app_order_base) if i['client_order_id'] == runorder_client_order_id}
    if c_order_ids: # App Requests to sell client_order_id
        if len(c_order_ids) != 1:
            print("error duplicate client_order_id requests, taking latest")
            logging.info("error duplicate client_order_id requests, taking latest")
            app_request = c_order_ids[len(c_order_ids)-1]
            for i in range(len(c_order_ids) - 1):
                APP_requests["sell_orders"].remove(APP_requests["sell_orders"][i])
                PickleData(pickle_file=PB_App_Pickle, data_to_store=APP_requests)
            return {'sell_order': False}
        else:
            print("App Request Order")
            logging.info("App Request Order")
            app_request = c_order_ids[list(c_order_ids.keys())[0]]
            if app_request['app_requests_id'] in QUEEN['app_requests__bucket']:
                print("sell order request Id already received")
                APP_requests['app_order_requests'].append(app_request)
                APP_requests['sell_orders'].remove(app_request)
                PickleData(pickle_file=PB_App_Pickle, data_to_store=APP_requests)
                return {'sell_order': False}
            else:
                print("get App Info details")
                sell_order = True
                sell_qty = app_request['sellable_qty']
                type = app_request['type']
                side = app_request['side']

                QUEEN['app_requests__bucket'].append(app_request['app_requests_id'])
                PickleData(pickle_file=PB_QUEEN_Pickle, data_to_store=QUEEN)
                APP_requests['sell_orders'].remove(app_request)
                PickleData(pickle_file=PB_App_Pickle, data_to_store=APP_requests)
                                
                return {'sell_order': True, 'sell_qty': sell_qty, 'type': type, 'side': side}
    else:
        return {'sell_order': False}


def confirm_Theme(QUEEN, APP_requests, savequeen=True): # King 
    if APP_requests['last_app_update'] > QUEEN['queen_controls']['last_read_app']:
        print("app request, checking theme")
        print(APP_requests['theme'])
        QUEEN['queen_controls']['last_read_app'] = APP_requests['last_app_update']
        # always set Theme
        if QUEEN['queen_controls']['theme'] != APP_requests['theme'] and APP_requests['theme'] in pollen_theme_dict.keys():
            print("setting new theme", APP_requests['theme'], timestamp_string())
            logging.info({'new_theme': APP_requests['theme'] })
            QUEEN['queen_controls']['theme'] = APP_requests['theme']
            
            PickleData(pickle_file=PB_QUEEN_Pickle, data_to_store=QUEEN) # Save
        else:
            print("theme not changed")
    return True 


def fix_crypto_ticker(QUEEN, ticker, idx): # order manage
    # fix symbol for crypto
    if ticker == 'BTC/USD':
        print("correcting symbol for ", ticker)
        QUEEN['queen_orders'][idx]['ticker'] = 'BTCUSD'
        ticker = "BTCUSD"
    if ticker == 'ETH/USD':
        print("correcting symbol for ", ticker)
        QUEEN['queen_orders'][idx]['ticker'] = 'ETHUSD'
        ticker = "ETHUSD"
    
    return ticker


def check_origin_order_status(QUEEN, origin_order, origin_idx, closing_filled):
    # queen_order = QUEEN['queen_orders'][queen_order_idx]
    if float(origin_order["filled_qty"]) == closing_filled: 
        print("# running order has been fully sold out and now we can archive")
        QUEEN['queen_orders'][origin_idx]['queen_order_state'] = 'completed'
        


def update_origin_orders_profits(queen_order, origin_order, origin_order_idx): # updated origin Trade orders profits
    origin_order_cost_basis = float(origin_order['filled_qty']) * float(origin_order['filled_avg_price'])
    
    # closing_orders_cost_basis
    origin_closing_orders_df = return_closing_orders_df(exit_order_link=queen_order['exit_order_link'])
    if len(origin_closing_orders_df) > 0:
        origin_closing_orders_df['filled_qty'] = origin_closing_orders_df['filled_qty'].apply(lambda x: float(x))
        origin_closing_orders_df['filled_avg_price'] = origin_closing_orders_df['filled_avg_price'].apply(lambda x: float(x))
        origin_closing_orders_df['cost_basis'] = origin_closing_orders_df['filled_qty'] * origin_closing_orders_df['filled_avg_price']
        closing_orders_cost_basis = sum(origin_closing_orders_df['cost_basis'])

        profit_loss = closing_orders_cost_basis - origin_order_cost_basis

        origin_closing_orders_df['filled_qty'] = origin_closing_orders_df['filled_qty'].apply(lambda x: float(x))
        closing_filled = sum(origin_closing_orders_df['filled_qty'])

        QUEEN['queen_orders'][origin_order_idx]['profit_loss'] = profit_loss
        QUEEN['queen_orders'][origin_order_idx]['qty_available'] = float(origin_order['filled_qty']) - closing_filled

        return {'closing_filled': closing_filled }
    else:
        return {'closing_filled': 0 }


def validate_portfolio_with_RUNNING(ticker, run_index, run_order, portfolio): # check if there are enough shares in portfolio IF NOT Archive RUNNING ORDER AS IT WAS SOLD ALREADY
    if ticker in portfolio.keys():
        qty_avail = float(portfolio[ticker]['qty'])
        qty_run = float(run_order["qty_available"])
        if qty_avail < 0 and qty_run < qty_avail: # short and run < avail (-10, -5)
            print("CRITICAL ERROR SHORT POSITION PORTFOLIO DOES NOT HAVE QTY AVAIL TO SELL adjust to remaining")
            logging.critical({"msg": "run order qty > then avail in portfolio, adjust to remaining"})
            QUEEN['queen_orders'][run_index]["filled_qty"] = qty_avail
            return QUEEN['queen_orders'][run_index]
        elif qty_avail > 0 and qty_run > qty_avail: # long and run > avail (10, 5)
            print("CRITICAL ERROR LONG POSITION PORTFOLIO DOES NOT HAVE QTY AVAIL TO SELL adjust to remaining")
            logging.critical({"msg": "run order qty > then avail in portfolio, adjust to remaining"})
            QUEEN['queen_orders'][run_index]["filled_qty"] = qty_avail
            return QUEEN['queen_orders'][run_index]
        else:
            return QUEEN['queen_orders'][run_index]
    else:
        print(ticker, "CRITICAL ERROR PORTFOLIO DOES NOT HAVE TICKER ARCHVIE RUNNING ORDER")
        logging.critical({'msg': f'{ticker}{" :Ticker not in Portfolio"}'})

        order_status = check_order_status(api=api, client_order_id=run_order['client_order_id'], queen_order=run_order)
        queen_order = update_latest_queen_order_status(order_status=order_status, queen_order_idx=run_index)

        # REMOVE running order
        QUEEN['queen_orders'][run_index]['queen_order_state'] = "error"        
        return QUEEN['queen_orders'][run_index]

def convert_to_float(x):
    try:
        return float(x)
    except:
        return 0

def return_all_linked_queen_orders(exit_order_link):
    df = pd.DataFrame(QUEEN['queen_orders'])
    origin_closing_orders = df[(df['exit_order_link'] == exit_order_link) & (df['queen_order_state'] != ARCHIVE_queenorder)].copy()
    if len(origin_closing_orders) > 0:
        return origin_closing_orders
    else:
        return False

def return_closing_orders_df(exit_order_link): # returns linking order
    df = pd.DataFrame(QUEEN['queen_orders'])
    origin_closing_orders = df[(df['exit_order_link'] == exit_order_link) & 
    (df['queen_order_state'].isin(closing_queen_orders)) & (df['client_order_id'].str.startswith("close__"))].copy()
    if len(origin_closing_orders) > 0:
        return origin_closing_orders
    else:
        return ''


def update_latest_queen_order_status(order_status, queen_order_idx): # updates qty and cost basis from Alpaca
    for order_key, order_value in order_status.items():
        QUEEN['queen_orders'][queen_order_idx][order_key] = order_value
    
    if order_status['filled_qty'] is not None:
        QUEEN['queen_orders'][queen_order_idx]['filled_qty'] = float(order_status['filled_qty'])
    if order_status['filled_avg_price'] is not None:
        QUEEN['queen_orders'][queen_order_idx]['filled_avg_price'] = float(order_status['filled_avg_price'])
        QUEEN['queen_orders'][queen_order_idx]['cost_basis'] = float(order_status['filled_qty']) * float(order_status['filled_avg_price'])

    return QUEEN['queen_orders'][queen_order_idx]


def return_origin_order(exit_order_link): # Improvement: faster by sending in df

    origin_order_q = {idx: i for idx, i in enumerate(QUEEN['queen_orders']) if i['client_order_id'] == exit_order_link}
    origin_idx = list(origin_order_q.keys())[0]
    origin_order = origin_order_q[list(origin_order_q.keys())[0]]
    return {'origin_order': origin_order, 'origin_idx': origin_idx}


def return_queen_order_idx(client_order_id):
    queen_order_index = [idx for idx, i in enumerate(QUEEN['queen_orders']) if i['client_order_id'] == client_order_id]
    if queen_order_index:
        return queen_order_index[0]
    else:
        return False


def get_best_limit_price(ask, bid):
    maker_dif =  ask - bid
    maker_delta = (maker_dif / ask) * 100
    # check to ensure bid / ask not far
    maker_middle = round(ask - (maker_dif / 2), 2)

    return {'maker_middle': maker_middle, 'maker_delta': maker_delta}


def return_snap_priceinfo(api, ticker, crypto, exclude_conditions=exclude_conditions):
    if crypto:
        snap = api.get_crypto_snapshot(ticker, exchange=coin_exchange)
    else:
        snap = api.get_snapshot(ticker)
        conditions = snap.latest_quote.conditions
        c=0
        while True:
            # print(conditions)
            valid = [j for j in conditions if j in exclude_conditions]
            if len(valid) == 0 or c > 10:
                break
            else:
                snap = api.get_snapshot(ticker) # return_last_quote from snapshot
                c+=1 

    # current_price = STORY_bee[f'{ticker}{"_1Minute_1Day"}']['last_close_price']
    current_price = snap.latest_trade.price
    current_ask = snap.latest_quote.ask_price
    current_bid = snap.latest_quote.bid_price

    # best limit price
    best_limit_price = get_best_limit_price(ask=current_ask, bid=current_bid)
    maker_middle = best_limit_price['maker_middle']
    ask_bid_variance = current_bid / current_ask
    
    priceinfo = {'price': current_price, 'bid': current_bid, 'ask': current_ask, 'maker_middle': maker_middle, 'ask_bid_variance': ask_bid_variance}
    
    return priceinfo


def update_queen_order_profits(ticker, queen_order, queen_order_idx):
    try:
        # queen_order = queen_order
        idx = queen_order_idx
        # return trade info
        if ticker in crypto_currency_symbols:
            snap = api.get_crypto_snapshot(ticker, exchange=coin_exchange)
        else:
            snap = api.get_snapshot(ticker)
        # current_price = STORY_bee[f'{ticker}{"_1Minute_1Day"}']['last_close_price']
        current_price = snap.latest_trade.price
        current_ask = snap.latest_quote.ask_price
        current_bid = snap.latest_quote.bid_price
        priceinfo = {'price': current_price, 'bid': current_bid, 'ask': current_ask}
        order_price = float(queen_order['filled_avg_price'])
        current_profit_loss = (current_price - order_price) / order_price
        # current_profit_loss = (current_ask - order_price) / order_price
        QUEEN['queen_orders'][idx]['honey'] = current_profit_loss
        QUEEN['queen_orders'][idx]['$honey'] = (current_price * float(queen_order['filled_qty'])) - ( float(queen_order['filled_avg_price']) * float(queen_order['filled_qty']) )
        
        if 'honey_gauge' in queen_order.keys():
            QUEEN['queen_orders'][idx]['honey_gauge'].append(current_profit_loss)

        return {'current_profit_loss': current_profit_loss}
    except Exception as e:
        print(e, print_line_of_error())


def honeyGauge_metric(run_order):
    # measure latest profits to determine to sell out / not
    
    gauge = run_order['honey_gauge']
    gauge_len = len(gauge)
    
    if gauge_len > 5:
        last_3 = [gauge[(gauge_len - n) *-1] for n in range(1,4)] # roughly ~5seconds
        last_3_avg = sum(last_3) / len(last_3)
    else:
        last_3_avg = False
    if gauge_len > 11:
        last_9 = [gauge[(gauge_len - n) *-1] for n in range(1,10)] # roughly ~13seconds
        last_9_avg = sum(last_9) / len(last_9)
    else:
        last_9_avg = False
    if gauge_len > 11:
        last_15 = [gauge[(gauge_len - n) *-1] for n in range(1,16)] # roughly ~10seconds
        last_15_avg = sum(last_15) / len(last_15)
    else:
        last_15_avg = False
    if gauge_len > 30:
        last_30 = [gauge[(gauge_len - n) *-1] for n in range(1,29)] # roughly ~35seconds
        last_30_avg = sum(last_30) / len(last_30)
    else:
        last_30_avg = False
    
    
    return {'last_3_avg': last_3_avg, 'last_9_avg': last_9_avg, 'last_15_avg': last_15_avg, 'last_30_avg': last_30_avg}


def macdGauge_metric(STORY_bee, ticker_time_frame, trigbees=['buy_cross-0', 'sell_cross-0'], number_ranges=[5, 11, 16, 24, 33]):
    # measure trigger bee strength
    
    if len(STORY_bee[ticker_time_frame]['story']['macd_gauge']) > 0:
        gauge = STORY_bee[ticker_time_frame]['story']['macd_gauge']
        gauge_len = len(gauge)
        
        d_return = {}
        for trigbee in trigbees:
            d_return[trigbee] = {}
            for num in number_ranges:
                d_return[trigbee][num] = {}
                if gauge_len > num:
                    last_n = [gauge[(gauge_len - n) *-1] for n in range(1,num)]
                    avg = sum([1 for i in last_n if i == trigbee]) / len(last_n)
                    d_return[trigbee][num].update({'avg': avg})
                else:
                    d_return[trigbee][num].update({'avg': 0})
        
        return {'metrics': d_return}


def update_queen_order_honey(queen_order, origin_order, queen_order_idx):
    sold_price = float(queen_order['filled_avg_price'])
    origin_price = float(origin_order['filled_avg_price'])
    honey = (sold_price - origin_price) / origin_price
    cost_basis = sold_price * float(queen_order['filled_qty'])
    profit_loss_value = honey * cost_basis
    QUEEN['queen_orders'][queen_order_idx]['honey'] = honey
    QUEEN['queen_orders'][queen_order_idx]['$honey'] = profit_loss_value
    QUEEN['queen_orders'][queen_order_idx]['profit_loss'] = profit_loss_value
    return {'profit_loss_value': profit_loss_value}


def route_queen_order(QUEEN, queen_order, queen_order_idx):
    def process_queen_order_update(order_status, queen_order, queen_order_idx):
        # handle updates. cancels updates
        if qo_status in cancel_expired:
            QUEEN['queen_orders'][queen_order_idx]['queen_order_state'] = "cancel_expired"
        elif qo_status in pending:
            QUEEN['queen_orders'][queen_order_idx]['queen_order_state'] = "pending"
        elif qo_status in failed:
            # Send Info Back to Not Trade Again?
            QUEEN['queen_orders'][queen_order_idx]['queen_order_state'] = "failed"
        elif qo_status in accetped:
            QUEEN['queen_orders'][queen_order_idx]['queen_order_state'] = "accetped"
        # Handle Filled Orders #
        elif qo_status in filled:
            # route by order type buy sell
            if order_status['side'] == 'buy':
                QUEEN['queen_orders'][queen_order_idx]['queen_order_state'] == "running"
                update_queen_order_profits(ticker=queen_order['ticker'], queen_order=queen_order, queen_order_idx=queen_order_idx)
                
                return {'resp': 'running'}
            
            elif order_status['side'] == 'sell':
                # closing order, update origin order profits attempt to close out order
                origin_order = return_origin_order(exit_order_link=queen_order['exit_order_link'])
                origin_order_idx = origin_order['origin_idx']
                origin_order = origin_order['origin_order']
                # confirm profits
                profit_loss_value = update_queen_order_honey(queen_order=queen_order, origin_order=origin_order, queen_order_idx=queen_order_idx)['profit_loss_value']
                QUEEN['queen_orders'][queen_order_idx]['queen_order_state'] = 'completed'

                print("Sell Order Fuly Filled: Honey>> ", profit_loss_value)
                #### CHECK to see if Origin ORDER has Completed LifeCycle ###
                closing_filled = update_origin_orders_profits(queen_order=queen_order, origin_order=origin_order, origin_order_idx=origin_order_idx)['closing_filled']
                
                # Check to complete Queen Order 
                check_origin_order_status(QUEEN=QUEEN, origin_order=origin_order, origin_idx=origin_order_idx, closing_filled=closing_filled)
                
                return {'resp': "completed"}     
        elif qo_status in partially_filled:            
            if order_status['side'] == 'buy':
                QUEEN['queen_orders'][queen_order_idx]['queen_order_state'] = "running_open"
                return {'resp': "running_open"}
            elif order_status['side'] == 'sell':
                # update profits keep in running 
                update_queen_order_honey(queen_order=queen_order, origin_order=origin_order, queen_order_idx=queen_order_idx)
                
                update_origin_orders_profits(queen_order=queen_order, origin_order=origin_order, origin_order_idx=origin_order_idx)

                update_queen_order_profits(ticker=ticker, queen_order=queen_order, queen_order_idx=queen_order_idx)

                QUEEN['queen_orders'][queen_order_idx]['queen_order_state'] = 'running_close'
                return {'resp': "running_close"}
            else:
                print("Critical Error New Order Side")
                logging_log_message(log_type='error', msg='Critical Error New Order Side')
        else:
            print("critical errror new order type received")
            logging_log_message(log_type='error', msg='critical errror new order type received')
    
    try:
        ticker = queen_order['ticker']
        order_id = queen_order['client_order_id']
        # check if order fulfilled
        order_status = check_order_status(api=api, client_order_id=order_id, queen_order=queen_order)
        # update filled qty & $
        queen_order = update_latest_queen_order_status(order_status=order_status, queen_order_idx=queen_order_idx)
        
        qo_status = order_status['status']

        """ Alpcaca Order States """
        cancel_expired = ['canceled', 'expired']
        pending = ['pending_cancel', 'pending_replace']
        failed = ['stopped', 'rejected', 'suspended']
        accetped = ['accepted', 'pending_new', 'accepted_for_bidding', 'new', 'calculated']
        filled = ['filled']
        partially_filled = ['partially_filled']
        current_updated_at = queen_order['updated_at']
        QUEEN['queen_orders'][queen_order_idx]['updated_at'] = order_status['updated_at']
        process_queen_order_update(order_status=order_status, queen_order=queen_order, queen_order_idx=queen_order_idx)

        if current_updated_at != order_status['updated_at']:
            print("Queen Order Updated")

        return queen_order

    except Exception as e:
        print(e, print_line_of_error())
        print("Unable to Route Queen Order")
        logging.error({'queen order client id': queen_order['client_order_id'], 'msg': 'unable to route queen order', 'error': str(e)})

def qorder_honey__distance_from_breakeven_tiers(run_order):
    # how far away from honey? trading model risk level for each profit stars
    profit_stars = ['high_above_breakeven', 'low_above_breakeven', 'breakeven', 'below_breakeven', 'immediate']
    if run_order['honey'] < 0:
        if run_order['honey'] < -.0033 and run_order['honey'] < -.0055:
            profit_seeking_star = 'high_above_breakeven' # shoot for above breakeven
        elif run_order['honey'] < -.0056 and run_order['honey'] < -.0089:
            profit_seeking_star = 'low_above_breakeven' # shoot for above breakeven
        elif run_order['honey'] < -.009 and run_order['honey'] < -.0013:
            profit_seeking_star = 'breakeven' # shoot for above breakeven
        elif run_order['honey'] < -.0013 and run_order['honey'] < -.0018:
            profit_seeking_star = 'below_breakeven'
        else:
            profit_seeking_star = 'immediate'
        
        return profit_seeking_star

def subconscious_update(root_name, dict_to_add):
    # store message
    if root_name in QUEEN['subconscious'].keys():
        QUEEN['subconscious'][root_name].update(dict_to_add)
    else:
        QUEEN['subconscious'][root_name] = dict_to_add

def king_bishops_QueenOrder(run_order, current_profit_loss, portfolio, qo_crypto=False):
    """if you made it here you are running somewhere, I hope you find your way, I'll always bee here to help"""
    try:
        portfolio = return_alpc_portolio(api)['portfolio']

        # """ all scenarios if run_order should be closed out """

        # Crypto
        if qo_crypto:
            crypto = True
        else:
            crypto = False
        # gather run_order Vars
        ticker_runorder = run_order['ticker']
        trigname = run_order['trigname']
        runorder_client_order_id = run_order['client_order_id']
        take_profit = run_order['order_rules']['take_profit']
        sellout = run_order['order_rules']['sellout']
        sell_qty = float(run_order['filled_qty'])
        qty_available = float(run_order['qty_available'])
        ticker_time_frame = run_order['ticker_time_frame']
        ticker_time_frame_origin = run_order['ticker_time_frame_origin']
        entered_trade_time = run_order['datetime'].astimezone(est)
        origin_wave = run_order['origin_wave']
        trading_model = run_order['trading_model']
        time_in_trade = datetime.datetime.now().astimezone(est) - entered_trade_time
        honey = run_order['honey']
        
        origin_closing_orders_df = return_closing_orders_df(exit_order_link=runorder_client_order_id)
        first_sell = [False if len(origin_closing_orders_df) > 0 else True][0]

        # Only if there are available shares

        priceinfo = return_snap_priceinfo(api=api, ticker=ticker_runorder, crypto=crypto)

        sell_order = False # #### >>> convince me to sell  $$
        
        macd_gauge = macdGauge_metric(STORY_bee=STORY_bee, ticker_time_frame=ticker_time_frame, trigbees=['buy_cross-0', 'sell_cross-0'], number_ranges=[5, 11, 16, 24, 33])
        honey_gauge = honeyGauge_metric(run_order)

        run_order_wave_changed = False
        try:
            # does current wave differ from origin wave?
            wave_n = [origin_wave['wave_n'] if len(origin_wave) > 0 else False][0]
            if wave_n:
                storybee_origin_wave = STORY_bee[ticker_time_frame]['waves'][trigname][wave_n]
                if storybee_origin_wave['trigbee'] != trigname:
                    run_order_wave_changed = True
                else:
                    run_order_wave_changed = False
        except Exception as e:
            print(e, print_line_of_error())
        

        # handle not in Story default to SPY
        if ticker_time_frame_origin not in QUEEN[queens_chess_piece]['conscience']['STORY_bee'].keys():
            ticker_time_frame_origin = "SPY_1Minute_1Day"
        ticker, tframe, tperiod = ticker_time_frame_origin.split("_")
        star = f'{tframe}{"_"}{tperiod}'

        # Stars in Heaven
        stars_df = story_view(STORY_bee=STORY_bee, ticker=ticker)['df']

        # POLLEN STORY
        ttframe_story = QUEEN[queens_chess_piece]['conscience']['STORY_bee'][ticker_time_frame_origin]['story']
        current_macd = ttframe_story['macd_state']
        current_macd_time = int(current_macd.split("-")[-1])
        
        # Bishop Waves
        current_macd_cross__wave = star_ticker_WaveAnalysis(STORY_bee=STORY_bee, ticker_time_frame=ticker_time_frame)['current_wave'].to_dict()
        current_wave = star_ticker_WaveAnalysis(STORY_bee=STORY_bee, ticker_time_frame=ticker_time_frame)['current_active_waves'][trigname].to_dict()
        current_wave_maxprofit_stat = current_wave['length'] - current_wave['time_to_max_profit']


        # Market closed do NOT Sell
        mkhrs = return_market_hours(api_cal=trading_days, crypto=crypto)
        
        if mkhrs == 'open':
            sell_order = sell_order
        else:
            return {'bee_sell': False, 'run_order': run_order}

        
        """ Trading Models Kings Order Rules """ 


        # trade is past excepted duration time 
        past_trade_duration = order_past_duration(queen_order=run_order)

        # Wave distance to Max Profit
        ttframe_take_max_profit = run_order['order_rules']['max_profit_waveDeviation']
        ttframe_take_max_profit_global = QUEEN['queen_controls']['max_profit_waveDeviation'][star]
        wave_past_max_profit = float(ttframe_take_max_profit) >= current_wave_maxprofit_stat # max profits exceed setting
        
        # App Requests
        app_req = process_app_sell_signal(QUEEN=QUEEN, PB_App_Pickle=PB_App_Pickle, runorder_client_order_id=run_order['client_order_id'])
        if app_req['sell_order']:
            print("process app sell order")
            sell_order = True
            app_request = True
            
            sell_qty = app_req['sell_qty']
            order_type = app_req['type']
            side = app_req['side']

            sell_reason = 'app'
            order_vars = order_vars__queen_order_items(trading_model=False, 
            king_order_rules=False, order_side='sell', wave_amo=False, maker_middle=False, 
            origin_wave=False, power_up_rangers=False, ticker_time_frame_origin='app_app_app',
            sell_reason='app', running_close_legs=False, sell_qty=app_req['sell_qty'], first_sell=first_sell)
            return {'bee_sell': True, 'order_vars': order_vars, 'app_request': app_request}

        else:
            app_request = False

        # Gather main sell reason groups
        sell_trigbee_trigger = [True if str(run_order['order_rules']['sell_trigbee_trigger']).lower() == 'true' else False][0]
        stagger_profits = [True if str(run_order['order_rules']['stagger_profits']).lower() == 'true' else False][0]
        scalp_profits = [True if str(run_order['order_rules']['scalp_profits']).lower() == 'true' else False][0]
        run_order_wave_changed = run_order_wave_changed
        
        # this occurs when selling is chunked
        running_close_legs = False

        # global limit type order type
        if str(trading_model['trade_using_limits']).lower() == 'true':
            order_type = 'limit'
            limit_price = priceinfo['maker_middle']
        elif str(run_order['order_rules']['trade_using_limits']).lower() == 'true':
            order_type = 'limit'
            limit_price = priceinfo['maker_middle']
        else:
            order_type = 'market'
            limit_price = False

        # verison control until better way found
        if 'max_profit_waveDeviation_timeduration' in run_order['order_rules'].keys():
            max_profit_waveDeviation_timeduration = run_order['order_rules']['max_profit_waveDeviation_timeduration']
        else:
            max_profit_waveDeviation_timeduration = 500 # Minutes


        """ WaterFall sellout chain """
        def waterfall_sellout_chain(sell_order, run_order, order_type, limit_price, sell_trigbee_trigger, stagger_profits, scalp_profits, run_order_wave_changed, sell_qty, QUEEN=QUEEN):
            try:        
                if scalp_profits:

                    
                    scalp_profits = run_order['order_rules']['scalp_profits_timeduration']
                    
                    if time_in_trade.total_seconds() > float(scalp_profits):
                        if honey_gauge['last_30_avg']:
                            # store message and compare trading model against distance from breakeven
                            if honey_gauge['last_30_avg'] < 0:
                                profit_seek = qorder_honey__distance_from_breakeven_tiers(run_order=run_order)
                                # set limit price based on profit_seek
                                print("selling out due Scalp Exit last_30_avg ")
                                sell_reason = 'scalp_exit__last_30_avg'
                                sell_order = True
                                order_side = 'sell'
                                if crypto:
                                    limit_price = round(priceinfo['maker_middle'] + (priceinfo['maker_middle'] * .03),1) # current price + (current price * profit seek)
                                else:
                                    limit_price = round(priceinfo['maker_middle'] + (priceinfo['maker_middle'] * .03),2) # current price + (current price * profit seek)


                                # store message
                                if 'queen_orders' in QUEEN['subconscious'].keys():
                                    QUEEN['subconscious']['queen_orders'].update({run_order['client_order_id']: {'client_order_id': run_order['client_order_id'],  'waterfall_sellout_msg': f'{"last_30_avg"}{" find exit price"}' }})
                                else:
                                    QUEEN['subconscious']['queen_orders'] = {run_order['client_order_id']: {'client_order_id': run_order['client_order_id'],  'waterfall_sellout_msg': f'{"last_30_avg"}{" find exit price"}' }}
                                
                                return {'sell_order': True, 'sell_reason': sell_reason, 'order_side': order_side, 'order_type': order_type, 'sell_qty': sell_qty, 'limit_price': limit_price}    

                
                # Water Fall
                if run_order['order_rules']['take_profit'] <= current_profit_loss:
                    print("selling out due PROFIT ACHIVED")
                    sell_reason = 'order_rules__take_profit'
                    sell_order = True
                    
                    order_side = 'sell'
                    limit_price = [priceinfo['maker_middle'] if order_type == 'limit' else False][0]

                elif current_profit_loss <= run_order['order_rules']['sellout']:
                    print("selling out due STOP LOSS")
                    sell_reason = 'order_rules__sellout'
                    sell_order = True

                    order_side = 'sell'
                    limit_price = [priceinfo['maker_middle'] if order_type == 'limit' else False][0]

                elif past_trade_duration:
                    print("selling out due to TIME DURATION")
                    sell_reason = 'order_rules__timeDuration'
                    sell_order = True


                    order_side = 'sell'
                    limit_price = [priceinfo['maker_middle'] if order_type == 'limit' else False][0]

                elif time_in_trade > datetime.timedelta(minutes=max_profit_waveDeviation_timeduration) and wave_past_max_profit:
                    print("Selling Out from max_profit_waveDeviation: deviation>> ", current_wave_maxprofit_stat)
                    sell_reason = 'order_rules__max_profit_waveDeviation'
                    sell_order = True


                    order_side = 'sell'
                    limit_price = [priceinfo['maker_middle'] if order_type == 'limit' else False][0]

                if sell_trigbee_trigger:
                    if run_order['trigname'] == "buy_cross-0" and "sell" in current_macd and time_in_trade.seconds > 500 and macd_gauge['metrics']['sell_cross-0'][24]['avg'] > .5 and macd_gauge['metrics']['sell_cross-0'][5]['avg'] > .5:
                        print("SELL ORDER change from buy to sell", current_macd, current_macd_time)
                        sell_reason = 'order_rules__macd_cross_buytosell'
                        sell_order = True
                        
                        order_side = 'sell'
                        limit_price = [priceinfo['maker_middle'] if order_type == 'limit' else False][0]

                    elif run_order['trigname'] == "sell_cross-0" and "buy" in current_macd and time_in_trade.seconds > 500 and macd_gauge['metrics']['buy_cross-0'][24]['avg'] > .5 and macd_gauge['metrics']['buy_cross-0'][5]['avg'] > .5:
                        print("SELL ORDER change from Sell to Buy", current_macd, current_macd_time)
                        sell_reason = 'order_rules__macd_cross_selltobuy'
                        sell_order = True

                        order_side = 'sell'
                        limit_price = [priceinfo['maker_middle'] if order_type == 'limit' else False][0]


                if sell_order:
                    return {'sell_order': True, 'sell_reason': sell_reason, 'order_side': order_side, 'order_type': order_type, 'sell_qty': sell_qty, 'limit_price': limit_price}    
                else:
                    return {'sell_order': False}
            except Exception as e:
                print('waterfall error', e, " er line>>", print_line_of_error())

        king_bishop = waterfall_sellout_chain(sell_order, run_order, order_type, limit_price, sell_trigbee_trigger, stagger_profits, scalp_profits, run_order_wave_changed, sell_qty)
    
        # elif the 3 wisemen pointing to sell or re-chunk profits

        # check if position is neg, if so, switch side to sell and sell_qty to buy
        # try:
        #     if portfolio[run_order['ticker']]['side'] == 'short':
        #         sell_qty = abs(sell_qty)
        #         side = 'buy'
        # except Exception as e:
        #     msg = (rn_order_symbol, " not found in portfolio, wait a moment and make second attempt call to portfolio :::: error: ", e)
        #     print(msg)
        #     logging.error(logging_log_message(log_type='error', msg=msg, error=str(e), origin_func='Main Queen orders()', ticker=rn_order_symbol))
        #     time.sleep(1)
        #     portfolio = return_alpc_portolio(api)['portfolio']
        #     if portfolio[run_order['ticker']]['side'] == 'short':
        #         sell_qty = abs(sell_qty)
        #         side = 'buy'

        if king_bishop['sell_order']:
            order_vars = order_vars__queen_order_items(order_side='sell',  
            maker_middle=king_bishop['limit_price'],
            sell_reason=king_bishop['sell_reason'], 
            sell_qty=king_bishop['sell_qty'], 
            running_close_legs=running_close_legs,
            ticker_time_frame_origin=ticker_time_frame,
            first_sell=first_sell, 
            time_intrade=time_in_trade)
            return {'bee_sell': True, 'order_vars': order_vars, 'app_request': app_request}
        else:
            return {'bee_sell': False, 'run_order': run_order}
    except Exception as e:
        print(e, print_line_of_error())
        log_error_dict = logging_log_message(log_type='error', msg='unable to process kings read on queen order', error=str(e), origin_func='king Evaluate QueenOrder')
        logging.error(log_error_dict)


def queen_orders_main(portfolio, APP_requests):

    # process queen_order_states
    def process_queen_order_states(run_order, queen_order_idx):
        if run_order['queen_order_state'] == 'completed':
            return False
        if run_order['queen_order_state'] in active_queen_order_states:
            run_order = route_queen_order(QUEEN=QUEEN, queen_order=run_order, queen_order_idx=queen_order_idx)                          
            
            if run_order['queen_order_state'] == 'completed':
                return False

        return run_order

    try:
        # App Requests
        app_req = process_app_requests(QUEEN=QUEEN, APP_requests=APP_requests, request_name='update_queen_order', archive_bucket='update_queen_order_requests')
        if app_req['app_flag']:
            update_queen_order(QUEEN=QUEEN, update_package=app_req['app_request']['queen_order_update_package'])

        # ALL Active SUBMITTED & RUNNING & RUNNING_CLOSE
        active_orders = {idx: i for idx, i in enumerate(QUEEN['queen_orders']) if i['queen_order_state'] in active_queen_order_states}

        for idx, run_order in active_orders.items():

            try:
                # Queen Order Local Vars
                ticker_time_frame = run_order['ticker_time_frame']
                runorder_client_order_id = run_order['client_order_id']
                ticker = run_order['ticker']
                trig = run_order['trigname']

                if ticker in crypto_currency_symbols:
                    qo_crypto = True
                    ticker = fix_crypto_ticker(QUEEN=QUEEN, ticker=ticker, idx=idx)
                else:
                    qo_crypto = False

                # Continue Only if Market Open
                mkhrs = return_market_hours(api_cal=trading_days, crypto=qo_crypto)
                if mkhrs != 'open':
                    continue # markets are not open for you
                # Process Queen Order States
                run_order = process_queen_order_states(run_order=run_order, queen_order_idx=idx)

                if run_order == False:
                    continue

                # Stop Queen Order from going to the Kings Court
                if str(run_order['order_trig_sell_stop']).lower() == 'true': ### consider remaining qty
                    continue
                if run_order['qty_available'] == 0:
                    continue

                if run_order['queen_order_state'] == 'running':
                    # try to close order
                    run_order = QUEEN['queen_orders'][idx]

                    resp = update_queen_order_profits(ticker=ticker, queen_order=run_order, queen_order_idx=idx)
                    current_profit_loss = resp['current_profit_loss']
                    
                    king_eval_order = king_bishops_QueenOrder(run_order=run_order, current_profit_loss=current_profit_loss, portfolio=portfolio, qo_crypto=qo_crypto)
                    if king_eval_order['bee_sell']:
                        """ 
                        VALIDATE BEE ORDER check if there are enough shares in portfolio 
                        IF NOT Archive RUNNING ORDER AS IT WAS SOLD ALREADY
                        """
                        # update buy order collective sell reason?
                        
                        run_order = validate_portfolio_with_RUNNING(ticker=ticker, run_index=idx, run_order=run_order, portfolio=portfolio)
                        if run_order['queen_order_state'] == "error":
                            continue
                        
                        execute_order(QUEEN=QUEEN, 
                        king_resp=False, 
                        king_eval_order=king_eval_order, 
                        ticker=ticker, 
                        ticker_time_frame=ticker_time_frame, 
                        trig=trig, 
                        portfolio=portfolio, 
                        run_order_idx=idx, 
                        crypto=qo_crypto)

                    else:
                        pass
            
            except Exception as e:
                print('Queen Order Main FAILED PROCESSING ORDER', e, print_line_of_error())
                log_error_dict = logging_log_message(log_type='error', msg='Queen Order Main FAILED PROCESSING ORDER', error=str(e), origin_func='Quen Main Orders')
                logging.error(log_error_dict)
                # archive order?
                QUEEN['queen_orders'][idx]['queen_order_state'] = 'error'
    
    except Exception as e:
        print('Queen Order Main FAILED', e, print_line_of_error())
        log_error_dict = logging_log_message(log_type='critical', msg='Queen Main Orders Failed', error=str(e), origin_func='Quen Main Orders')
        logging.critical(log_error_dict)
        sys.exit()


def order_management(api, QUEEN, APP_requests): 

    #### MAIN ####
    # >for every ticker position join in running-positions to account for total position
    # >for each running position determine to exit the position                

    portfolio = return_alpc_portolio(api)['portfolio']

    # Submitted Orders First
    queen_orders_main(portfolio=portfolio, APP_requests=APP_requests)

    # Reconcile QUEENs portfolio
    # reconcile_portfolio()

    # God Save the Queen
    PickleData(pickle_file=PB_QUEEN_Pickle, data_to_store=QUEEN)

    return True


def refresh_QUEEN_starTickers(QUEEN, STORY_bee):
    ticker_allowed = ['SPY', 'ETHUSD']
    now_time = datetime.datetime.now().astimezone(est)

    original_state = QUEEN['heartbeat']['available_tickers']
    
    QUEEN['heartbeat']['available_tickers'] = [i for (i, v) in STORY_bee.items() if (now_time - v['story']['time_state']).seconds < 33]
    # create dict of allowed long term and short term of a given ticker so ticker as info for trading
    QUEEN['heartbeat']['active_tickerStars'] = {k: {'trade_type': ['long_term', 'short_term']} for k in QUEEN['heartbeat']['available_tickers']}
    ticker_set = set([i.split("_")[0] for i in QUEEN['heartbeat']['active_tickerStars'].keys()])

    QUEEN['heartbeat']['active_tickers'] = [i for i in ticker_set if i in ticker_allowed]

    new_active = QUEEN['heartbeat']['available_tickers']
    if original_state != new_active:
        print('added dropped / updated tickers')
        for ttframe in new_active:
            if ttframe not in original_state:
                print("added", ttframe, return_timestamp_string())
        
        for ttframe in original_state:
            if ttframe not in new_active:
                print("dropped", ttframe, return_timestamp_string())

        PickleData(PB_QUEEN_Pickle, QUEEN)

    return True





# if '_name_' == '_main_':
try:
    # s_time = datetime.datetime.now().astimezone(est)

    # init files needed
    init_pollen = init_pollen_dbs(db_root=db_root, api=api, prod=prod, queens_chess_piece=queens_chess_piece)
    PB_QUEEN_Pickle = init_pollen['PB_QUEEN_Pickle']
    PB_App_Pickle = init_pollen['PB_App_Pickle']
    # init orders
    init_api_orders_start_date =(datetime.datetime.now() - datetime.timedelta(days=100)).strftime("%Y-%m-%d")
    init_api_orders_end_date = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    api_orders = initialize_orders(api, init_api_orders_start_date, init_api_orders_end_date)

    # Macd Settings
    # MACD_12_26_9 = {'fast': 12, 'slow': 26, 'smooth': 9}    

    # Pollen QUEEN
    pollen = read_queensmind(prod)
    QUEEN = pollen['queen']
    QUEEN['source'] = PB_QUEEN_Pickle
    STORY_bee = pollen['STORY_bee']
    POLLENSTORY = read_pollenstory()


    APP_requests = ReadPickleData(pickle_file=PB_App_Pickle)
    APP_requests['source'] = PB_App_Pickle
    APP_req = add_key_to_app(APP_requests)
    APP_requests = APP_req['APP_requests']
    if APP_req['update']:
        PickleData(PB_App_Pickle, APP_requests)

    # process_app_requests(QUEEN=QUEEN, APP_requests=APP_requests, request_name='queen_controls_reset', archive_bucket=False)

    # add new keys
    QUEEN_req = add_key_to_QUEEN(QUEEN=QUEEN, queens_chess_piece=queens_chess_piece)
    if QUEEN_req['update']:
        QUEEN = QUEEN_req['QUEEN']
        PickleData(PB_QUEEN_Pickle, QUEEN)


    logging.info("My Queen")

    KING = KINGME()
    # QUEEN = KING['QUEEN']
    # Extra Queen Info
    
    # QUEEN['queen_controls']['MACD_fast_slow_smooth'] = {'fast': 12, 'slow': 26, 'smooth': 9}
    # QUEEN['kings_order_rules'] = KING['kings_order_rules']
    QUEEN['heartbeat']['main_indexes'] = {
        'SPY': {'long1X': "SPY",
                'long3X': 'SPXL', 
                'inverse1X': 'SH', 
                'inverse2X': 'SDS', 
                'inverse3X': 'SPXU'},
        'QQQ': {'long3X': 'TQQQ', 'inverse': 'PSQ', 'inverse2X': 'QID', 'inverse3X': 'SQQQ'}
        }

    QUEEN['heartbeat']['active_order_state_list'] = active_order_state_list

    refresh_QUEEN_starTickers(QUEEN, STORY_bee)

    available_triggerbees = ["sell_cross-0", "buy_cross-0"]
    QUEEN['heartbeat']['available_triggerbees'] = available_triggerbees
    print("active trigs", available_triggerbees)
    print("active tickers", QUEEN['heartbeat']['active_tickers'])


    PickleData(pickle_file=PB_QUEEN_Pickle, data_to_store=QUEEN)
    

    print("Here we go Mario")
    pollen_theme_dict = pollen_themes(KING=KING)
    workerbee_run_times = []


########################################################
########################################################
#############The Infinite Loop of Time ###################
########################################################
########################################################
########################################################


    while True:
        s = datetime.datetime.now()
        # Should you operate now? I thnik the brain never sleeps ?

        if queens_chess_piece.lower() == 'queen': # Rule On High
            
            """ The Story of every Knight and their Quest """

            # refresh db
            pollen = read_queensmind(prod)
            QUEEN = pollen['queen']
            STORY_bee = pollen['STORY_bee']
            POLLENSTORY = read_pollenstory()

            # Read App Reqquests
            APP_requests = ReadPickleData(pickle_file=PB_App_Pickle)

            # # King ME
            # KING = KINGME()
            
            # Client
            process_app_requests(QUEEN=QUEEN, APP_requests=APP_requests, request_name='stop_queen', archive_bucket=False)
            process_app_requests(QUEEN=QUEEN, APP_requests=APP_requests, request_name='queen_controls', archive_bucket='queen_controls_requests')
            process_app_requests(QUEEN=QUEEN, APP_requests=APP_requests, request_name='power_rangers', archive_bucket='power_rangers_requests')
            process_app_requests(QUEEN=QUEEN, APP_requests=APP_requests, request_name='queen_controls_reset', archive_bucket=False)
            # return Theme from App    
            confirm_Theme(QUEEN=QUEEN, APP_requests=APP_requests)

            # Process All Orders
            order_management(api=api, QUEEN=QUEEN, APP_requests=APP_requests)

            # Hunt for Triggers
            command_conscience(api=api, QUEEN=QUEEN, APP_requests=APP_requests) #####>   


            time.sleep(1)
            e = datetime.datetime.now()
            # print(queens_chess_piece, str((e - s).seconds),  "sec: ", datetime.datetime.now().strftime("%A,%d. %I:%M:%S%p"))

            """
                > lets do this!!!!
                love: anchor on the 1 min macd crosses or better yet just return all triggers and base everything off the trigger
            """

        e = datetime.datetime.now()
        if (e - s).seconds > 10:
            logging.info((queens_chess_piece, ": cycle time > 10 seconds:  SLOW cycle: ", (e - s).seconds ))
            print(queens_chess_piece, str((e - s).seconds),  "sec: ", datetime.datetime.now().strftime("%A,%d. %I:%M:%S%p"))
except Exception as errbuz:
    print(errbuz)
    erline = print_line_of_error()
    log_msg = {'type': 'ProgramCrash', 'lineerror': erline}
    print(log_msg)
    logging.critical(log_msg)
#### >>>>>>>>>>>>>>>>>>> END <<<<<<<<<<<<<<<<<<###