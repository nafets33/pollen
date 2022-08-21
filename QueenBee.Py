# QueenBee
import logging
from enum import Enum
from operator import sub
from signal import signal
from symtable import Symbol
import time
import alpaca_trade_api as tradeapi
import asyncio
import os
import pandas as pd
import numpy as np
import pandas_ta as ta
import sys
# from alpaca_trade_api.rest import TimeFrame, URL
# from alpaca_trade_api.rest_async import gather_with_concurrency, AsyncRest
from dotenv import load_dotenv
import threading
import sys
import datetime
from datetime import date, timedelta
import pytz
from typing import Callable
import random
import collections
import pickle
from tqdm import tqdm
from stocksymbol import StockSymbol
import requests
from collections import defaultdict
import ipdb
import tempfile
import shutil
# from scipy.stats import linregress
from scipy import stats
import hashlib
import json
from collections import deque
import argparse
from QueenHive import KING, logging_log_message, createParser, return_index_tickers, return_alpc_portolio, return_market_hours, return_dfshaped_orders, add_key_to_app, init_QUEEN, pollen_themes, init_app, check_order_status, slice_by_time, split_today_vs_prior, read_csv_db, update_csv_db, read_queensmind, read_pollenstory, pickle_chesspiece, speedybee, submit_order, return_timestamp_string, pollen_story, ReadPickleData, PickleData, return_api_keys, return_bars_list, refresh_account_info, return_bars, init_index_ticker, print_line_of_error, add_key_to_QUEEN
# from QueenHive import return_macd, return_VWAP, return_RSI, return_sma_slope

# if prior day abs(change) > 1 ignore ticker for the day! 
 
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

# Macd Settings
# MACD_12_26_9 = {'fast': 12, 'slow': 26, 'smooth': 9}

active_order_state_list = ['running', 'running_close', 'submitted']

# Client Tickers
src_root, db_dirname = os.path.split(db_root)
client_ticker_file = os.path.join(src_root, 'client_tickers.csv')
df_client = pd.read_csv(client_ticker_file, dtype=str)
df_client_f = df_client[df_client['status']=='active'].copy()
client_symbols = df_client_f.tickers.to_list()
client_symbols_castle = ['SPY', 'QQQ']
client_symbols_bishop = ['AAPL', 'GOOG']
client_market_movers = ['AAPL', 'TSLA', 'GOOG', 'META']
crypto_currency_symbols = ['BTCUSD', 'ETHUSD', 'BTC/USD', 'ETH/USD']
coin_exchange = "CBSE"



""" Keys """
api_key_id = os.environ.get('APCA_API_KEY_ID')
api_secret = os.environ.get('APCA_API_SECRET_KEY')
base_url = "https://api.alpaca.markets"
keys = return_api_keys(base_url, api_key_id, api_secret)
rest = keys[0]['rest']
api = keys[0]['api']

# Paper
api_key_id_paper = os.environ.get('APCA_API_KEY_ID_PAPER')
api_secret_paper = os.environ.get('APCA_API_SECRET_KEY_PAPER')
base_url_paper = "https://paper-api.alpaca.markets"
keys_paper = return_api_keys(base_url=base_url_paper, 
    api_key_id=api_key_id_paper, 
    api_secret=api_secret_paper,
    prod=False)
rest_paper = keys_paper[0]['rest']
api_paper = keys_paper[0]['api']

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
    'P','Q','R','T','U','V','Z'
]

"""# Main Arguments """
num = {1: .15, 2: .25, 3: .40, 4: .60, 5: .8}
client_num_LT = 1
client_num_ST = 3
client_days1yrmac_input = 233 # Tier 1
client_daysT2Mac_input = 5 # Tier 2
client_daysT3Mac_input = 233 # Tier 3

"""# Customer Setup """
Long_Term_Client_Input = num[client_num_LT]
MidDayLag_Alloc = num[client_num_ST]
DayRiskAlloc = 1 - (Long_Term_Client_Input + MidDayLag_Alloc)


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
"""
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


def generate_client_order_id(QUEEN, ticker, trig, db_root=db_root, sellside_client_order_id=False): # generate using main_order table and trig count
    main_orders_table = read_csv_db(db_root=db_root, tablename='main_orders', prod=prod)
    temp_date = datetime.datetime.now().strftime("%y%m%d-%M.%S")
    
    if sellside_client_order_id:
        main_trigs_df = main_orders_table[main_orders_table['client_order_id'] == sellside_client_order_id].copy()
        trig_num = len(main_trigs_df)
        order_id = f'{"close__"}{trig_num}-{sellside_client_order_id}'
    else:
        main_trigs_df = main_orders_table[(main_orders_table['trigname']==trig) & (main_orders_table['exit_order_link'] != 'False')].copy()
        
        trig_num = len(main_trigs_df)
        order_id = f'{"run__"}{ticker}-{trig}-{trig_num}-{temp_date}'

    if order_id in QUEEN['client_order_ids_qgen']:
        msg = {"generate_client_order_id()": "client order id already exists change"}
        print(msg)
        logging.error(msg)
        # q_l = len(QUEEN['client_order_ids_qgen'])
        mill_s = datetime.datetime.now().microsecond
        order_id = f'{order_id}{"_qgen_"}{mill_s}'

    # append created id to QUEEN
    QUEEN['client_order_ids_qgen'].append(order_id)
    PickleData(pickle_file=PB_Story_Pickle, data_to_store=QUEEN)
    
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


def process_order_submission(order, trig, prod, tablename, ticker_time_frame, portfolio_name='Jq', status_q=False, exit_order_link=False, bulkorder_origin__client_order_id=False, system_recon=False, priceinfo=False):

    try:
        def create_QueenOrderBee(): # Create Running Order
            date_mark = datetime.datetime.now()
            # allowed_col = ["queen_order_state", ]
            if system_recon:
                print("create recon order")
                running_order = {'queen_order_state': 'submitted',
                                'side': system_recon['side'],
                                'order_trig_buy_stop': True,
                                'order_trig_sell_stop': 'false',
                                'symbol': order['symbol'], 'order_rules': QUEEN["kings_order_rules"]["knight_bees"][trig], 
                                'trigname': trig, 'datetime': date_mark,
                                'ticker_time_frame': ticker_time_frame,
                                'ticker_time_frame_origin': ticker_time_frame,
                                'status_q': status_q,
                                'portfolio_name': portfolio_name,
                                'exit_order_link': exit_order_link, 'client_order_id': order['client_order_id'],
                                'system_recon': True,
                                'req_qty': system_recon['req_qty'],
                                'filled_qty': system_recon['filled_qty'],
                                'qty_available': system_recon['filled_qty'],
                                'filled_avg_price': system_recon['filled_avg_price'],
                                'price_time_of_request': 'na',
                                'bid': 'na',
                                'ask': 'na',
                                'honey_gauge': deque([], 89),
                                } 
            elif order['side'] == 'buy':
                # print("create buy running order")
                running_order = {'queen_order_state': 'submitted',
                                'side': order['side'],
                                'order_trig_buy_stop': True,
                                'order_trig_sell_stop': 'false',
                                'symbol': order['symbol'], 'order_rules': QUEEN["kings_order_rules"]["knight_bees"][trig], 
                                'trigname': trig, 'datetime': date_mark,
                                'ticker_time_frame': ticker_time_frame,
                                'ticker_time_frame_origin': ticker_time_frame, 
                                'status_q': status_q,
                                'portfolio_name': portfolio_name,
                                'exit_order_link': exit_order_link, 'client_order_id': order['client_order_id'],
                                'system_recon': False,
                                'req_qty': order['qty'],
                                'filled_qty': order['filled_qty'],
                                'qty_available': order['filled_qty'],
                                'filled_avg_price': order['filled_avg_price'],
                                'price_time_of_request': priceinfo['price'],
                                'bid': priceinfo['bid'],
                                'ask': priceinfo['ask'],
                                'honey_gauge': deque([], 89),
                                }
            elif order['side'] == 'sell':
                # print("create sell order")
                running_order = {'queen_order_state': 'submitted',
                                'side': order['side'],
                                'order_trig_buy_stop': True,
                                'order_trig_sell_stop': 'true',
                                'symbol': order['symbol'], 'order_rules': QUEEN["kings_order_rules"]["knight_bees"][trig], 
                                'trigname': trig, 'datetime': date_mark,
                                'ticker_time_frame': ticker_time_frame,
                                'ticker_time_frame_origin': ticker_time_frame, 
                                'status_q': status_q,
                                'portfolio_name': portfolio_name,
                                'exit_order_link': exit_order_link, 'client_order_id': order['client_order_id'],
                                'system_recon': False,
                                'req_qty': order['qty'],
                                'filled_qty': order['filled_qty'],
                                'qty_available': order['filled_qty'],
                                'filled_avg_price': order['filled_avg_price'],
                                'price_time_of_request': priceinfo['price'],
                                'bid': priceinfo['bid'],
                                'ask': priceinfo['ask'],
                                'honey_gauge': deque([], 89),
                                }

            return running_order

        # update db
        date_mark = datetime.datetime.now()
        symbol = order['symbol']
        client_order_id = order['client_order_id']
        alpaca_order_id = order['id']
        df_details = {'trigname': trig, 'client_order_id':client_order_id, 'origin_client_order_id':client_order_id, 
        'exit_order_link':exit_order_link, 'ticker_time_frame': ticker_time_frame, 'status_q': status_q, 'alpaca_order_id': alpaca_order_id,
        'bulkorder_origin__client_order_id': bulkorder_origin__client_order_id, 'portfolio_name': portfolio_name, 'system_recon': system_recon} 
        df = pd.DataFrame(df_details.items()).T
        new_header = df.iloc[0] #grab the first row for the header
        df = df[1:] #take the data less the header row
        df.columns = new_header #set the header row as the df header
        update_csv_db(df_to_add=df, tablename=tablename, prod=prod, append=True)

        # Create Running Order
        sending_order = create_QueenOrderBee()

        QUEEN['queen_orders'].append(sending_order)

        logging.info(QUEEN["kings_order_rules"]["knight_bees"][trig])
        
        # trig_stop_info = {'symbol': symbol, 'trigname': trig, 'ticker_time_frame': ticker_time_frame, 
        # 'exit_order_link': exit_order_link, 
        # 'client_order_id': client_order_id, 'datetime': date_mark}
        
        return {'sending_order': sending_order}
    except Exception as e:
        print(e, print_line_of_error())


def route_order_based_on_status(order_status):
    # https://alpaca.markets/docs/trading/orders/#order-lifecycle
    if order_status in ['accepted', 'pending_new', 'accepted_for_bidding', 'filled', 'partially_filled', 'new', 'calculated']:
        return True
    elif order_status in ['canceled', 'expired', 'replaced', 'pending_cancel', 'pending_replace', 'stopped', 'rejected', 'suspended']:
        return False
    else:
        msg={order_status: ": unknown error"}
        print(msg)
        logging.error(msg)


def process_app_requests(APP_requests, request_name):
    # APP_requests = ReadPickleData(pickle_file=PB_App_Pickle)
    
    if request_name == "buy_orders":
        # request_name = "buy_orders" # buy_orders
        # theme, sell, buy
        app_order_base = [i for i in APP_requests[request_name]]
        if app_order_base:
            for app_request in app_order_base:
                if app_request['app_requests_id'] in QUEEN['queen_controls']['app_order_requests']:
                    print("buy trigger request Id already received")
                    APP_requests['app_order_requests'].append(app_request)
                    APP_requests[request_name].remove(app_request)
                    PickleData(pickle_file=PB_App_Pickle, data_to_store=APP_requests)
                    return {'order_flag': False}
                else:
                    print("app buy order gather")
                    wave_amo = app_request['wave_amo']
                    r_type = app_request['type']
                    r_side = app_request['side']
                
                    king_resp = {'side': r_side, 'type': r_type, 'wave_amo': wave_amo }
                    ticker_time_frame = f'{app_request["ticker"]}{"_app_bee"}'

                    # remove request
                    APP_requests['app_order_requests'].append(app_request)
                    APP_requests[request_name].remove(app_request)
                    PickleData(pickle_file=PB_App_Pickle, data_to_store=APP_requests)
                    
                    return {'king_resp': king_resp, 'order_flag': True, 'app_request': app_request, 'ticker_time_frame': ticker_time_frame}  
        else:
            return {'order_flag': False}
    
    if request_name == "wave_triggers":
        # theme, sell, buy
        app_order_base = [i for i in APP_requests[request_name]]
        if app_order_base:
            for app_request in app_order_base:
                if app_request['app_requests_id'] in QUEEN['queen_controls']['app_order_requests']:
                    print("wave trigger request Id already received")
                    APP_requests['app_wave_requests'].append(app_request)
                    APP_requests[request_name].remove(app_request)
                    PickleData(pickle_file=PB_App_Pickle, data_to_store=APP_requests)
                    return {'app_flag': False}
                else:
                    print("app wave trigger gather", app_request['wave_trigger'], " : ", app_request['ticker_time_frame'])
                    QUEEN['queen_controls']['app_order_requests'].append(app_request['app_requests_id'])
                    APP_requests['app_wave_requests'].append(app_request)
                    APP_requests[request_name].remove(app_request)
                    PickleData(pickle_file=PB_App_Pickle, data_to_store=APP_requests)
                    
                    return {'app_flag': True, 'app_request': app_request, 'ticker_time_frame': app_request['ticker_time_frame']}
        else:
            return {'app_flag': False}
    
    if request_name == "update_queen_order":
        app_order_base = [i for i in APP_requests[request_name]]
        if app_order_base:
            for app_request in app_order_base:
                if app_request['app_requests_id'] in QUEEN['queen_controls']['app_order_requests']:
                    print("queen update order trigger request Id already received")
                    APP_requests['update_queen_order_requests'].append(app_request)
                    APP_requests[request_name].remove(app_request)
                    PickleData(pickle_file=PB_App_Pickle, data_to_store=APP_requests)
                    return {'app_flag': False}
                else:
                    print("queen update order trigger gather", app_request['queen_order_update_package'], " : ", app_request['ticker_time_frame'])
                    QUEEN['queen_controls']['app_order_requests'].append(app_request['app_requests_id'])
                    APP_requests['update_queen_order_requests'].append(app_request)
                    APP_requests[request_name].remove(app_request)
                    PickleData(pickle_file=PB_App_Pickle, data_to_store=APP_requests)
                    
                    return {'app_flag': True, 'app_request': app_request, 'ticker_time_frame': app_request['ticker_time_frame']}
        else:
            return {'app_flag': False}    


"""  >>>><<<< MAIN <<<<>>>> """
def trig_In_Action_cc(active_orders, trig, ticker):
    # all_orders = pd.DataFrame(QUEEN['queen_orders'])
    # active_orders = all_orders[all_orders['queen_order_state'].isin(QUEEN['heartbeat']['active_order_state_list'])].copy()
    if queens_first_go == 0:
        return False
    
    order_exits = np.where(
        (active_orders['trigname'] == trig) &
        (active_orders['symbol'] == ticker)
    )

    if sum(order_exits[0]) > 0:
        return True
    else:
        return False


def add_app_wave_trigger(all_current_triggers, ticker, app_wave_trig_req):
    # ipdb.()
    if app_wave_trig_req['app_flag'] == False:
        return all_current_triggers
    else:
        if ticker == app_wave_trig_req['app_request']['ticker']:
            all_current_triggers.update(app_wave_trig_req['app_request']['wave_trigger']) # test
            msg = {'add_app_wave_trigger()': 'added wave drone'}
            print(msg)
            # queen process
            logging.info(msg)
            # APP_requests['queen_processed_orders'].append(app_wave_trig_req['app_request']['app_requests_id'])
            # QUEEN['queen_controls']['app_order_requests'].append(app_wave_trig_req['app_request']['app_requests_id'])
            return all_current_triggers
        else:
            return all_current_triggers


def buying_Power_cc(api, client_args="TBD", daytrade=True):
    info = api.get_account()
    total_buying_power = info.buying_power # what is the % amount you want to buy?
    app_portfolio_day_trade_allowed = .8
    app_portfolio_long_trade_allowed = .2
    if app_portfolio_day_trade_allowed + app_portfolio_long_trade_allowed != 1:
        print("Critical Error Fix buying power numbers")
        sys.exit()
    
    # wave power allowance
    app_portfolio_waveup_buying_power = .6
    app_portfolio_wavedown_buying_power = .4
    if app_portfolio_waveup_buying_power + app_portfolio_wavedown_buying_power != 1:
        print("Critical Error Fix buying power numbers")
        sys.exit()
    
    client_totalday_trade_amt_allowed = app_portfolio_day_trade_allowed * float(total_buying_power)
    
    return {'client_totalday_trade_amt_allowed': client_totalday_trade_amt_allowed, 'app_portfolio_day_trade_allowed': app_portfolio_day_trade_allowed, 'total_buying_power': total_buying_power}


def execute_order(QUEEN, king_resp, ticker, ticker_time_frame, trig, portfolio, run_order_idx=False):
    try:
        # print(ticker_time_frame)
        logging.info({'ex_order()': ticker_time_frame})
        # trig made it into the kingdom
        # print("Journy to the kingdom of heaven")
        side = king_resp['side']
        type = king_resp['type']
        wave_amo = king_resp['wave_amo']
        
        # flag crypto
        if ticker in crypto_currency_symbols:
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
        
        if crypto:
            qty_order = float(round(wave_amo / current_price, 4))
        else:
            qty_order = float(round(wave_amo / current_price, 0))


        # validate app order
        def validate_app_order():
            pass
        
        
        # return num of trig for client_order_id
        order_id = generate_client_order_id(QUEEN=QUEEN, ticker=ticker, trig=trig)

        send_order_val = submit_order_validation(ticker=ticker, qty=qty_order, side=side, portfolio=portfolio, run_order_idx=run_order_idx)
        qty_order = send_order_val['qty_correction'] # same return unless more validation done here

        # ONLY allows Market
        if type == 'market':
            order_submit = submit_order(api=api, symbol=ticker, type=type, qty=qty_order, side=side, client_order_id=order_id) # buy
        else:
            order_submit = submit_order(api=api, symbol=ticker, type=type, qty=qty_order, side=side, client_order_id=order_id) # buy
        logging.info("order submit")
        order = vars(order_submit)['_raw']
        # Confirm order went through, end process and write results
        if route_order_based_on_status(order_status=order['status']):
            # print(ticker_time_frame)
            
            order_process = process_order_submission(trig=trig, order=order, prod=prod, tablename='main_orders', ticker_time_frame=ticker_time_frame, priceinfo=priceinfo)

            pickle_chesspiece(pickle_file=PB_Story_Pickle, data_to_store=QUEEN)
            
            msg = {'execute order()': {'msg': f'{"order submitted"}{" : at : "}{return_timestamp_string()}', 'ticker_time_frame': ticker_time_frame, 'trig': trig, 'crypto': crypto}}
            logging.info(msg)
            print(msg)
            queens_first_go = 1
            return{'executed': True, 'msg': msg}
        else:
            msg = ("error order not accepted", order)
            print(msg)
            logging.error(msg)
            return{'executed': False, 'msg': msg}
    except Exception as e:
        print(e, print_line_of_error())
        print(ticker_time_frame)
        log_error_dict = logging_log_message(type='error', msg='Failed to Execute Order', error=str(e), origin_func='Execute Order', ticker=ticker)
        logging.error(log_error_dict)
        sys.exit()


def king_knights_requests(trigbee, ticker_time_frame, trig_action=False, crypto=False):
    # answer all questions for order to be placed, compare against the rules
    
    def knight_request_recon_portfolio():
        # debate if we should place a new order based on current portfolio trades
        pass
    
    
    def eval_trig_action():
        # evaluate if the current trade needs more love$
        pass

    
    def trade_Scenarios(trigbee):
        # Create buying power upgrades depending on the STARS waves
        return True
    

    def tickers_story(ticker_time_frame):
        # state of every wave per timeframe, buy/sell, len, weight to add on
        # ticker_influence = {} #change value return or multiplier
        # rules = {}
        # weight = {
        #     '1M':{1: {'5D': 0, '5D_1M': 0, '5D_1M_3M': 0, '5D_1M_3M_6M': 0 },
        #           2 : {},
        #           3: {},  
        #         },
        #     '5D':,
        #     '1M':,
        #     '3M':,
        # }
        
        return True
    
    def trade_Allowance():
        # trade is not allowed x% level, if so kill/reduce trade
        return True

    
    def current_wave():
        # attach self to latest wave
        return True
    
    def proir_waves():
        # return fequency of prior waves and statement conclusions
        return True


    try:
        ticker, tframe, frame = ticker_time_frame.split("_")            

        """ Waves: Current Wave, answer questions about proir waves """
        waves = QUEEN[queens_chess_piece]['conscience']['STORY_bee'][ticker_time_frame]['waves'][trigbee]
        if "0" in waves.keys():
            waves.pop("0")
        
        # wave slices
        total_waves = len(waves.keys())
        morning_waves = {k:v for (k,v) in waves.items() if v['wave_blocktime'] == "morning_9-11"}
        lunch_waves = {k:v for (k,v) in waves.items() if v['wave_blocktime'] == "lunch_11-2"}
        afternoon_waves = {k:v for (k,v) in waves.items() if v['wave_blocktime'] == "afternoon_2-4"}
        afterhours_waves = {k:v for (k,v) in waves.items() if v['wave_blocktime'] == "afterhours"}

        # Total buying power allowed
        bpower_resp = buying_Power_cc(api=api, client_args="TBD", daytrade=True)
        client_totalday_trade_amt_allowed = bpower_resp['client_totalday_trade_amt_allowed']
        app_portfolio_day_trade_allowed = bpower_resp['app_portfolio_day_trade_allowed']
        total_buying_power = bpower_resp['total_buying_power']
        
        # Theme
        theme = QUEEN['queen_controls']['theme'] # what is the theme?

        # for bee in all_bees:
        if trigbee == 'buy_cross-0':
            # Q?confirmation on trigger, should you wait for futher confirmation?

            if crypto:
                order_type = "market"
                order_side = "buy"
                wave_amo = 10000
                kings_blessing = True
            else:
                theme_buyingpower = {
                'morning_9-11' : pollen_theme_dict[theme]['waveup']['morning_9-11'],
                'lunch_11-2' : pollen_theme_dict[theme]['waveup']['lunch_11-2'],
                'afternoon_2-4' : pollen_theme_dict[theme]['waveup']['afternoon_2-4'],
                }

                # what is your timeblock?
                
                # what does your friend_links(bees) say? or have said?
                
                # current wave
                current_wave_index = list(waves.keys())[len(waves)-1]
                current_wave = waves[current_wave_index]
                current_wave_blocktime = current_wave['wave_blocktime']
                current_wave_amo = theme_buyingpower[current_wave['wave_blocktime']]
                
                # total budget
                client_totalday_trade_amt_allowed = app_portfolio_day_trade_allowed * float(total_buying_power)

                order_type = "market"
                order_side = "buy"
                wave_amo = current_wave_amo * client_totalday_trade_amt_allowed
                
                # how many trades have we completed today? whats our total profit loss with wave trades
                
                # should you override your original order rules?

                kings_blessing = True
            
            if trig_action:
                # print("evalatue if there is another trade to make on top of current wave")
                kings_blessing = False

            return {'kings_blessing': kings_blessing, 'wave_amo': wave_amo, 'type': order_type, 'side': order_side}

        if trigbee == 'sell_cross-0':
            # Q?confirmation on trigger, should you wait for futher confirmation?

            if crypto:
                kings_blessing = False
            else:
                theme_buyingpower = {
                'morning_9-11' : pollen_theme_dict[theme]['wavedown']['morning_9-11'],
                'lunch_11-2' : pollen_theme_dict[theme]['wavedown']['lunch_11-2'],
                'afternoon_2-4' : pollen_theme_dict[theme]['wavedown']['afternoon_2-4'],
                }
                
                # current wave
                current_wave_index = list(waves.keys())[len(waves)-1]
                current_wave = waves[current_wave_index]
                current_wave_blocktime = current_wave['wave_blocktime']
                current_wave_amo = theme_buyingpower[current_wave['wave_blocktime']]

                order_type = "market"
                order_side = "buy"
                wave_amo = current_wave_amo * client_totalday_trade_amt_allowed
                # how many trades have we completed today? whats our total profit loss with wave trades
                # should you override your original order rules?
                kings_blessing = True

            if trig_action:
                # print("evalatue if there is another trade to make on top of current wave")
                kings_blessing = False
            if crypto:
                kings_blessing = False

            return {'kings_blessing': kings_blessing, 'wave_amo': wave_amo, 'type': order_type, 'side': order_side}
        
        else:
            print("Error New Trig not in Queens Mind: ", trigbee )

    except Exception as e:
        print(e, print_line_of_error(), ticker_time_frame)


def command_conscience(api, QUEEN, active_tickers):

    STORY_bee = QUEEN['queen']['conscience']['STORY_bee']

    story_tickers = set([i.split("_")[0] for i in list(STORY_bee.keys())])
    portfolio = return_alpc_portolio(api)['portfolio']
       
    # def app_request_triggerbees():
    app_wave_trig_req = process_app_requests(APP_requests=APP_requests, request_name='wave_triggers')

    all_orders = pd.DataFrame(QUEEN['queen_orders'])
    if queens_first_go == 0: 
        active_orders = []
    else:
        active_orders = all_orders[all_orders['queen_order_state'].isin(active_order_state_list)].copy()

    # cycle through stories  # The Golden Ticket
    for ticker in story_tickers:
        # Accept Ticker
        if ticker not in active_tickers:
            continue # break loop
        
        # crypto
        if ticker in crypto_currency_symbols:
            crypto = True
        else:
            crypto = False

        # if market closed do NOT Sell
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
                frame_block = "_1Minute_1Day"
                if f'{ticker}{frame_block}' in all_current_triggers.keys():
                    ticker_time_frame = f'{ticker}{"_1Minute_1Day"}'
                    # cycle through triggers and pass buy first logic for buy
                    trigs =  all_current_triggers[f'{ticker}{"_1Minute_1Day"}']
                    for trig in trigs:
                        # ipdb.()
                        if trig == "buy_cross-0":                                                        
                            # check if you already placed order or if a workerbee in transit to place order
                            if trig_In_Action_cc(active_orders=active_orders, trig=trig, ticker=ticker):
                                trig_action = True
                            else:
                                trig_action = False

                            
                            """ HAIL TRIGGER, WHAT SAY YOU?
                            ~forgive me but I bring a gift for the king and queen
                            """
                            king_resp = king_knights_requests(trigbee=trig, ticker_time_frame=ticker_time_frame, trig_action=trig_action, crypto=crypto)

                            if king_resp['kings_blessing']:
                                print("CheckPoint_WhoAreYou?", trig, " time:", return_timestamp_string())
                                # print("Each Buz in a gift")

                                execute_order(QUEEN=QUEEN, king_resp=king_resp, ticker=ticker, ticker_time_frame=ticker_time_frame, trig=trig, portfolio=portfolio)
                        
                        if trig == "sell_cross-0":
                            # print(trig)
                            # if ticker in QUEEN['heartbeat']['main_indexes']: # SPY, QQQ
                            if ticker in crypto_currency_symbols:
                                continue # break loop
                            
                            ticker = QUEEN['heartbeat']['main_indexes'][ticker]['inverse'] # SH SQQQ...

                            # check if you already placed order or if a workerbee in transit to place order
                            if trig_In_Action_cc(active_orders=active_orders, trig=trig, ticker=ticker):
                                trig_action = True
                            else:
                                trig_action = False
                            
                            king_resp = king_knights_requests(trigbee=trig, ticker_time_frame=ticker_time_frame, trig_action=trig_action, crypto=crypto)

                            if king_resp['kings_blessing']:
                                print("CheckPoint_WhoAreYou?", trig, " time:", return_timestamp_string())
                                print("Each Buz in a gift")
                                
                                execute_order(QUEEN=QUEEN, king_resp=king_resp, ticker=ticker, ticker_time_frame=ticker_time_frame, trig=trig, portfolio=portfolio)

            except Exception as e:
                print(e, print_line_of_error())
                print(ticker_time_frame)
    
    # App Buy Order Requests
    app_resp = process_app_requests(APP_requests, 'buy_orders')
    if app_resp['order_flag']:
        msg = {'process_app_buy_requests()': 'queen processed app request'}
        print(msg)
        # queen process
        logging.info(msg)
        APP_requests['queen_processed_orders'].append(app_resp['app_request']['app_requests_id'])
        QUEEN['queen_controls']['app_order_requests'].append(app_resp['app_request']['app_requests_id'])
        PickleData(PB_App_Pickle, APP_requests)
        
        # execute order
        bzzz = execute_order(QUEEN=QUEEN, 
        trig=app_resp['app_request']['trig'], 
        king_resp=app_resp['king_resp'], 
        ticker=app_resp['app_request']['ticker'], 
        ticker_time_frame=app_resp['ticker_time_frame'],
        portfolio=portfolio)


    return True



""">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> order management <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< """

def order_past_duration(queen_order):
    nowtime = datetime.datetime.now()
    qorder_time = queen_order['datetime']
    duration_rule = queen_order['order_rules']['timeduration']
    order_time_delta = nowtime - qorder_time
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
            if app_request['app_requests_id'] in QUEEN['queen_controls']['app_order_requests']:
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

                QUEEN['queen_controls']['app_order_requests'].append(app_request['app_requests_id'])
                pickle_chesspiece(pickle_file=PB_Story_Pickle, data_to_store=QUEEN)
                APP_requests['sell_orders'].remove(app_request)
                PickleData(pickle_file=PB_App_Pickle, data_to_store=APP_requests)
                                
                return {'sell_order': True, 'sell_qty': sell_qty, 'type': type, 'side': side}
    else:
        return {'sell_order': False}


def confirm_Theme(QUEEN, APP_requests): # King 
    if APP_requests['last_app_update'] > QUEEN['queen_controls']['last_read_app']:
        print("app request, checking theme")
        print(APP_requests['theme'])
        # always set Theme
        if QUEEN['queen_controls']['theme'] != APP_requests['theme'] and APP_requests['theme'] in pollen_theme_dict.keys():
            print("setting new theme", APP_requests['theme'])
            logging.info({'new_theme': APP_requests['theme'] })
            QUEEN['queen_controls']['theme'] = APP_requests['theme']
            QUEEN['queen_controls']['last_read_app'] = APP_requests['last_app_update']
    return True 


def update_origin_order_qty_available(): # TBD
    # return all closed orders & running close
    # reduce qty filled by qty filled in close orders
    return True


def fix_crypto_ticker(QUEEN, ticker): # order manage
    # fix symbol for crypto
    if ticker == 'BTC/USD':
        print("correcting symbol for ", ticker)
        QUEEN['queen_orders'][idx]['symbol'] = 'BTCUSD'
        ticker = "BTCUSD"
    if ticker == 'ETH/USD':
        print("correcting symbol for ", ticker)
        QUEEN['queen_orders'][idx]['symbol'] = 'ETHUSD'
        ticker = "ETHUSD"
    
    return ticker


def check_origin_order_status(QUEEN, origin_order, origin_idx, closing_filled):
    # queen_order = QUEEN['queen_orders'][queen_order_idx]
    if float(origin_order["filled_qty"]) == closing_filled: 
        print("# running order has been fully sold out and now we can archive")
        QUEEN['queen_orders'][origin_idx]['queen_order_state'] = 'completed'

    else:
        print("origin order still has shares to sell")
        QUEEN['queen_orders'][origin_idx]['order_trig_sell_stop'] = 'false'


def update_origin_orders_profits(queen_order, origin_order, origin_order_idx):
    origin_order_cost_basis = float(origin_order['filled_qty']) * float(origin_order['filled_avg_price'])
    
    # closing_orders_cost_basis
    origin_closing_orders_df = return_closing_orders_df(exit_order_link=queen_order['exit_order_link'])
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


def validate_portfolio_with_RUNNING(ticker, run_index, run_order, portfolio):        
    # check if there are enough shares in portfolio IF NOT Archive RUNNING ORDER AS IT WAS SOLD ALREADY
    # if ticker in crypto_currency_symbols:
    #     return {"run_order_valid":True}
    if ticker in portfolio.keys():
        # ipdb.()
        qty_avail = float(portfolio[ticker]['qty'])
        qty_run = float(run_order["qty_available"])
        # ipdb.()
        if qty_avail < 0 and qty_run < qty_avail: # short and run < avail (-10, -5)
            print("CRITICAL ERROR SHORT POSITION PORTFOLIO DOES NOT HAVE QTY AVAIL TO SELL adjust to remaining")
            logging.critical({"msg": "run order qty > then avail in portfolio, adjust to remaining"})
            QUEEN['queen_orders'][run_index]["filled_qty"] = qty_avail
            # QUEEN['queen_orders'][run_index]["status_q"] = True
            return QUEEN['queen_orders'][run_index]
        
        elif qty_avail > 0 and qty_run > qty_avail: # long and run > avail (10, 5)
            print("CRITICAL ERROR LONG POSITION PORTFOLIO DOES NOT HAVE QTY AVAIL TO SELL adjust to remaining")
            logging.critical({"msg": "run order qty > then avail in portfolio, adjust to remaining"})
            QUEEN['queen_orders'][run_index]["filled_qty"] = qty_avail
            # QUEEN['queen_orders'][run_index]["status_q"] = True
            return QUEEN['queen_orders'][run_index]
        
        else:
            return QUEEN['queen_orders'][run_index]
    
    else:
        print(ticker, "CRITICAL ERROR PORTFOLIO DOES NOT HAVE TICKER ARCHVIE RUNNING ORDER")
        logging.critical({'msg': f'{ticker}{" :Ticker not in Portfolio"}'})

        order_status = check_order_status(api=api, client_order_id=run_order['client_order_id'], queen_order=run_order)
        queen_order = update_latest_queen_order_status(order_status=order_status, queen_order_idx=run_index)
        # closing_filled = update_origin_orders_profits(queen_order, origin_order, origin_order_idx)

        # REMOVE running order
        QUEEN['queen_orders'][run_index]['queen_order_state'] = "error"        
        return QUEEN['queen_orders'][run_index]


def return_closing_orders_df(exit_order_link):
    closing_orders = [i for i in QUEEN['queen_orders'] if i['client_order_id'].startswith("close__")]
    closing_orders_df = pd.DataFrame(closing_orders)
    origin_closing_orders = closing_orders_df[closing_orders_df['exit_order_link'] == exit_order_link].copy()
    return origin_closing_orders


def update_latest_queen_order_status(order_status, queen_order_idx): # returns queen_order
    # if order_status['filled_qty']:
    # if order_status['filled_avg_price']:
    QUEEN['queen_orders'][queen_order_idx]['filled_qty'] = float(order_status['filled_qty'])
    QUEEN['queen_orders'][queen_order_idx]['filled_avg_price'] = float(order_status['filled_avg_price'])
    QUEEN['queen_orders'][queen_order_idx]['cost_basis'] = float(order_status['filled_qty']) * float(order_status['filled_avg_price'])
    
    return QUEEN['queen_orders'][queen_order_idx]


def return_origin_order(exit_order_link):
    # exit_order_link = queen_order['exit_order_link']
    origin_order_q = {idx: i for idx, i in enumerate(QUEEN['queen_orders']) if i['client_order_id'] == exit_order_link}
    origin_idx = list(origin_order_q.keys())[0]
    origin_order = origin_order_q[list(origin_order_q.keys())[0]]
    return {'origin_order': origin_order, 'origin_idx': origin_idx}


def return_snap_priceinfo(ticker):
    if ticker in crypto_currency_symbols:
        snap = api.get_crypto_snapshot(ticker, exchange=coin_exchange)
    else:
        snap = api.get_snapshot(ticker)
    # current_price = STORY_bee[f'{ticker}{"_1Minute_1Day"}']['last_close_price']
    current_price = snap.latest_trade.price
    current_ask = snap.latest_quote.ask_price
    current_bid = snap.latest_quote.bid_price
    priceinfo = {'price': current_price, 'bid': current_bid, 'ask': current_ask}
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


def route_queen_order(QUEEN, queen_order, queen_order_idx):
    try:
        idx = queen_order_idx
        ticker = queen_order['symbol']
        order_id = queen_order['client_order_id']
        # ipdb
        # check if order fulfilled
        order_status = check_order_status(api=api, client_order_id=order_id, queen_order=queen_order)
        # update filled qty & $
        queen_order = update_latest_queen_order_status(order_status=order_status, queen_order_idx=idx)

        # if order has fulfilled place in working orders else tag as partial order fulfilled
        if float(order_status["filled_qty"]) > 0:
            if order_status['side'] == 'buy':
                if QUEEN['queen_orders'][idx]['status_q'] == "filled":
                    return {'resp': 'running'}
                elif float(order_status['filled_qty']) == float(queen_order['req_qty']):                        
                    # Transistion state to Running
                    QUEEN['queen_orders'][idx]['queen_order_state'] = 'running'
                    QUEEN['queen_orders'][idx]['qty_available'] = float(order_status['filled_qty'])
                    QUEEN['queen_orders'][idx]['status_q'] = "filled"
                    return {'resp': "running"}

                elif float(order_status['filled_qty']) > 0: # move out of submitted to running same as if it was fully fulfilled
                    # Transistion state to Running
                    if QUEEN['queen_orders'][idx]['status_q'] != float(order_status['filled_qty']):
                        QUEEN['queen_orders'][idx]['queen_order_state'] = 'running'
                        QUEEN['queen_orders'][idx]['qty_available'] = float(order_status['filled_qty'])
                        QUEEN['queen_orders'][idx]['status_q'] = float(order_status['filled_qty'])
                        return {'resp': "running"}
                    else:
                        return {'resp': "running"}
                else:
                    print("UNKNOWN SHORT?")
                    return {'resp': "pending"}


            if order_status['side'] == 'sell':
                # closing order, update origin order profits attempt to close out order
                origin_order = return_origin_order(exit_order_link=queen_order['exit_order_link'])
                origin_order_idx = origin_order['origin_idx']
                origin_order = origin_order['origin_order']
                
                # if float(order_status['filled_qty']) == float(queen_order['req_qty']):
                if order_status['status'] == 'filled':
                    # confirm profits
                    sold_price = float(queen_order['filled_avg_price'])
                    origin_price = float(origin_order['filled_avg_price'])
                    honey = (sold_price - origin_price) / origin_price
                    cost_basis = sold_price * float(queen_order['filled_qty'])
                    profit_loss_value = honey * cost_basis
                    QUEEN['queen_orders'][idx]['honey'] = honey
                    QUEEN['queen_orders'][idx]['$honey'] = profit_loss_value
                    QUEEN['queen_orders'][idx]['profit_loss'] = profit_loss_value

                    # transistion from Submitted to Running
                    QUEEN['queen_orders'][idx]['queen_order_state'] = 'completed'

                    print("Sell Order Fuly Filled: Honey>> ", profit_loss_value)

                    #### CHECK to see if Origin ORDER has Completed LifeCycle ###
                    closing_filled = update_origin_orders_profits(queen_order=queen_order, origin_order=origin_order, origin_order_idx=origin_order_idx)['closing_filled']
                    check_origin_order_status(QUEEN=QUEEN, origin_order=origin_order, origin_idx=origin_order_idx, closing_filled=closing_filled)
                    
                    return {'resp': "completed"}
                
                elif float(order_status['filled_qty']) > 0:
                    print("order still has remaining Qty To Sell Keep in Running Close")
                    sold_price = float(queen_order['filled_avg_price'])
                    origin_price = float(origin_order['filled_avg_price'])
                    honey = (sold_price - origin_price) / origin_price
                    cost_basis = sold_price * float(queen_order['filled_qty'])
                    QUEEN['queen_orders'][idx]['honey'] = honey
                    QUEEN['queen_orders'][idx]['$honey'] = honey * cost_basis
                    QUEEN['queen_orders'][idx]['profit_loss'] = honey * cost_basis
                    
                    # transistion from Submitted to Running
                    QUEEN['queen_orders'][idx]['queen_order_state'] = 'running_close'

                    # update origin 
                    closing_filled = update_origin_orders_profits(queen_order=queen_order, origin_order=origin_order, origin_order_idx=origin_order_idx)['closing_filled']

                    return {'resp': "running_close"}
                
                else:
                    print("order pending fill")
                    return {'resp': "pending"}


        else:
            print(order_status['client_order_id'], "order pending fill stays in submitted")
            return {'resp': "pending"}
    except Exception as e:
        print(e, print_line_of_error())
        print("Unable to Route Queen Order")
        logging.error({'queen order client id': queen_order['client_order_id'], 'msg': 'unable to route queen order', 'error': str(e)})
        # sys.exit()


def king_Evaluate_QueenOrder(run_order, current_profit_loss, portfolio):
    try:
        # all scenarios if run_order should be closed out
        sell_order = False # convince me to sell

        rn_order_symbol = run_order['symbol']
        runorder_client_order_id = run_order['client_order_id']
        take_profit = run_order['order_rules']['take_profit'] #  {'order_rules': order_rules, 'trigname': trig, 'order': order, 'datetime': date_mark, 'status_q': False, 'exit_order': False}                                    
        sellout = run_order['order_rules']['sellout']
        sell_qty = float(run_order['filled_qty'])
        ticker_time_frame = run_order['ticker_time_frame']
        ticker_time_frame_origin = run_order['ticker_time_frame_origin']
        
        if ticker_time_frame_origin not in QUEEN[queens_chess_piece]['conscience']['STORY_bee'].keys():
            ticker_time_frame_origin = "SPY_1Minute_1Day"
        
        # POLLEN-STORY
        ttframe_story = QUEEN[queens_chess_piece]['conscience']['STORY_bee'][ticker_time_frame_origin]['story']
        current_macd = ttframe_story['macd_state']
        current_macd_time = int(current_macd.split("-")[-1])
        
        # trade is past excepted duration time 
        past_trade_duration = order_past_duration(queen_order=run_order)

        # if market closed do NOT Sell
        if rn_order_symbol in crypto_currency_symbols:
            crypto = True
        else:
            crypto = False
        
        mkhrs = return_market_hours(api_cal=trading_days, crypto=crypto)
        
        if mkhrs == 'open':
            sell_order = sell_order
        else:
            return {'bee_sell': False, 'run_order': run_order}

        if str(run_order['order_trig_sell_stop']).lower() == 'true': ### consider remaining qty
            logging.info({"sell in progress": rn_order_symbol})
            print("sell in progress")
            return {'bee_sell': False}
        
        side = 'sell'
        type ='market'
        app_req = process_app_sell_signal(QUEEN=QUEEN, PB_App_Pickle=PB_App_Pickle, runorder_client_order_id=runorder_client_order_id)
        if app_req['sell_order']:
            print("process app sell order")
            sell_order = True
            app_request = True
            
            sell_qty = app_req['sell_qty']
            type = app_req['type']
            side = app_req['side']
        else:
            app_request = False

        if take_profit <= current_profit_loss:
            print("selling out due PROFIT ACHIVED")
            sell_order = True
        
        elif current_profit_loss <= sellout:
            print("selling out due STOP LOSS")
            sell_order = True
        
        elif past_trade_duration:
            print("selling out due to TIME DURATION")
            sell_order = True

        # where are we at in relation to Max Profit
        
        # time in trade

        # elif run_order['trigname'] == "buy_cross-0" and "sell" in current_macd and current_macd_time > 0:
        #     print("SELL ORDER change from buy to sell", current_macd, current_macd_time)
        #     sell_order = True

        # elif run_order['trigname'] == "sell_cross-0" and "buy" in current_macd and current_macd_time > 0:
        #     print("SELL ORDER change from Sell to Buy", current_macd, current_macd_time)
        #     sell_order = True
        
        # elif the 3 wisemen pointing to sell or re-chunk profits
        

        # check if position is neg, if so, switch side to sell and sell_qty to buy
        if portfolio[rn_order_symbol]['side'] == 'short':
            sell_qty = abs(sell_qty)
            side = 'buy'
        


        if sell_order:
            return {'bee_sell': True, 'type': type, 'side': side, 'sell_qty': sell_qty, 'app_request': app_request}
        else:
            return {'bee_sell': False, 'run_order': run_order}
    except Exception as e:
        print(e, print_line_of_error())
        log_error_dict = logging_log_message(type='error', msg='unable to process kings read on queen order', error=str(e), origin_func='king Evaluate QueenOrder')
        logging.error(log_error_dict)


def queen_orders_main(portfolio):
    
    try:
        app_req = process_app_requests(APP_requests=APP_requests, request_name='update_queen_order')
        if app_req['app_flag']:
            update_queen_order(QUEEN=QUEEN, update_package=app_req['app_request']['queen_order_update_package'])

        # active orders
        if queens_first_go == 0:
            return False
        
        QUEEN['command_conscience']['orders']['active'] = [i for i in QUEEN['queen_orders'] if i['queen_order_state'] in active_order_state_list]
        QUEEN['command_conscience']['orders']['submitted'] = [i for i in QUEEN['queen_orders'] if i['queen_order_state'] == 'submitted']
        QUEEN['command_conscience']['orders']['running'] = [i for i in QUEEN['queen_orders'] if i['queen_order_state'] == 'running']
        QUEEN['command_conscience']['orders']['running_close'] = [i for i in QUEEN['queen_orders'] if i['queen_order_state'] == 'running_close']

        active_orders = {idx: i for idx, i in enumerate(QUEEN['queen_orders']) if i['queen_order_state'] in ['submitted', 'running', 'running_close']}

        for idx, run_order in active_orders.items():
            try:
                # ipdb.()
                # Queen Order Local Vars
                ticker_time_frame = run_order['ticker_time_frame']
                runorder_client_order_id = run_order['client_order_id']
                ticker = run_order["symbol"]
                trigname = run_order['trigname']

                if ticker in crypto_currency_symbols:
                    qo_crypto = 'true'
                else:
                    qo_crypto = 'false'

                ticker = fix_crypto_ticker(QUEEN=QUEEN, ticker=ticker)

                mkhrs = return_market_hours(api_cal=trading_days, crypto=qo_crypto)
                if mkhrs != 'open':
                    continue # markets are not open for you
                
                if run_order['queen_order_state'] == 'completed':
                    continue
                
                if run_order['queen_order_state'] == 'submitted':
                    order_state = route_queen_order(QUEEN=QUEEN, queen_order=run_order, queen_order_idx=idx)                          
                    run_order = QUEEN['queen_orders'][idx] # refresh run_order
                
                if run_order['queen_order_state'] == 'running':
                    order_state = route_queen_order(QUEEN=QUEEN, queen_order=run_order, queen_order_idx=idx)
                    run_order = QUEEN['queen_orders'][idx] # refresh run_order
                    if order_state['resp'] == 'completed':
                        print("order completed")
                        continue
                # ipdb.()
                if str(run_order['order_trig_sell_stop']).lower() == 'true': ### consider remaining qty
                    continue
                # this should be for ONLY Running Orders and Running Close
                if "run" not in run_order['queen_order_state']:
                    continue
            

                # try to close order
                run_order = QUEEN['queen_orders'][idx]

                resp = update_queen_order_profits(ticker=ticker, queen_order=run_order, queen_order_idx=idx)
                current_profit_loss = resp['current_profit_loss']
                re_eval_order = king_Evaluate_QueenOrder(run_order=run_order, current_profit_loss=current_profit_loss, portfolio=portfolio)
                if re_eval_order['bee_sell']:
                    # VALIDATE BEE ORDER check if there are enough shares in portfolio IF NOT Archive RUNNING ORDER AS IT WAS SOLD ALREADY
                    run_order = validate_portfolio_with_RUNNING(ticker=ticker, run_index=idx, run_order=run_order, portfolio=portfolio)
                    if run_order['queen_order_state'] == "error":
                        continue
                    
                    print("bee_sell")
                    # close out order variables
                    priceinfo = return_snap_priceinfo(ticker)
                    sell_qty = float(re_eval_order['sell_qty']) # float(order_obj['filled_qty'])
                    q_side = re_eval_order['side'] # 'sell' Unless it short then it will be a 'buy'
                    q_type = re_eval_order['type'] # 'market'

                    sell_client_order_id = generate_client_order_id(QUEEN=QUEEN, ticker=ticker, trig=trigname, db_root=db_root, sellside_client_order_id=runorder_client_order_id)
                    
                    send_order_val = submit_order_validation(ticker=ticker, qty=sell_qty, side=q_side, portfolio=portfolio, run_order_idx=idx)
                    
                    sell_qty = send_order_val['qty_correction']
                    send_close_order = submit_order(api=api, side=q_side, symbol=ticker, qty=sell_qty, type=q_type, client_order_id=sell_client_order_id) 
                    send_close_order = vars(send_close_order)['_raw']
                    if route_order_based_on_status(order_status=send_close_order['status']):
                        print("Did you bring me some Honey?")
                        order_process = process_order_submission(order=send_close_order, trig=trigname, exit_order_link=runorder_client_order_id, prod=prod, tablename='main_orders', ticker_time_frame=ticker_time_frame, priceinfo=priceinfo)
                        QUEEN['queen_orders'][idx]['order_trig_sell_stop'] = 'true'

                        PickleData(pickle_file=PB_Story_Pickle, data_to_store=QUEEN)

                    else:
                        msg = {"order_management()" : ("runorder_client_order_id", run_order['client_order_id'])}
                        print(msg)
                        logging.error(msg)
            except Exception as e:
                print('Queen Order Main FAILED PROCESSING ORDER', e, print_line_of_error())
                log_error_dict = logging_log_message(type='error', msg='Queen Order Main FAILED PROCESSING ORDER', error=str(e), origin_func='Quen Main Orders')
                logging.error(log_error_dict)
                # archive order?
                QUEEN['queen_orders'][idx]['queen_order_state'] = 'error'
    
    except Exception as e:
        print('Queen Order Main FAILED', e, print_line_of_error())
        log_error_dict = logging_log_message(type='critical', msg='Queen Main Orders Failed', error=str(e), origin_func='Quen Main Orders')
        logging.critical(log_error_dict)
        sys.exit()


def order_management(api, QUEEN): 

    #### MAIN ####
    # >for every ticker position join in running-positions to account for total position
    # >for each running position determine to exit the position                

    portfolio = return_alpc_portolio(api)['portfolio']

    # return Theme from App    
    confirm_Theme(QUEEN=QUEEN, APP_requests=APP_requests)

    # Submitted Orders First
    queen_orders_main(portfolio=portfolio)

    # Reconcile QUEENs portfolio
    # reconcile_portfolio()

    # God Save the Queen
    PickleData(pickle_file=PB_Story_Pickle, data_to_store=QUEEN)

    return True


# if '_name_' == '_main_':
try:
    # namespace.q_1
    chart_times = {
        "1Minute_1Day": 0, "5Minute_5Day": 5, "30Minute_1Month": 18, 
        "1Hour_3Month": 48, "2Hour_6Month": 72, 
        "1Day_1Year": 250}
    # init files needed
    if prod:
        api = api
        main_orders_file = os.path.join(db_root, 'main_orders.csv')
        PB_Story_Pickle = os.path.join(db_root, f'{queens_chess_piece}{".pkl"}')
        if os.path.exists(PB_Story_Pickle) == False:
            # QUEEN = init_QUEEN()
            print("You Need a Queen")
            sys.exit()
        PB_App_Pickle = os.path.join(db_root, f'{queens_chess_piece}{"_App_"}{".pkl"}')
        if os.path.exists(PB_App_Pickle) == False:
            init_app(pickle_file=PB_App_Pickle)
        PB_Orders_Pickle = os.path.join(db_root, f'{queens_chess_piece}{"_Orders_"}{".pkl"}')
        if os.path.exists(PB_Orders_Pickle) == False:
            init_app(pickle_file=PB_Orders_Pickle)
        print("My Queen Production")
    else:
        api = api_paper
        main_orders_file = os.path.join(db_root, 'main_orders_sandbox.csv')
        PB_Story_Pickle = os.path.join(db_root, f'{queens_chess_piece}{"_sandbox"}{".pkl"}')
        if os.path.exists(PB_Story_Pickle) == False:
            # QUEEN = init_QUEEN()
            print("You Need a Queen__sandbox")
            sys.exit()
        PB_App_Pickle = os.path.join(db_root, f'{queens_chess_piece}{"_App_"}{"_sandbox"}{".pkl"}')
        if os.path.exists(PB_App_Pickle) == False:
            init_app(pickle_file=PB_App_Pickle)
        PB_Orders_Pickle = os.path.join(db_root, f'{queens_chess_piece}{"_Orders_"}{"_sandbox"}{".pkl"}')
        if os.path.exists(PB_Orders_Pickle) == False:
            init_app(pickle_file=PB_Orders_Pickle)
        print("My Queen Sandbox")
        
    init_api_orders_start_date =(datetime.datetime.now() - datetime.timedelta(days=100)).strftime("%Y-%m-%d")
    init_api_orders_end_date = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    api_orders = initialize_orders(api, init_api_orders_start_date, init_api_orders_end_date)
    
    # Pollen QUEEN
    pollen = read_queensmind(prod)
    QUEEN = pollen['queen']
    STORY_bee = pollen['STORY_bee']
    POLLENSTORY = read_pollenstory()

    QUEEN_req = add_key_to_QUEEN(QUEEN=QUEEN, queens_chess_piece=queens_chess_piece)
    if QUEEN_req['update']:
        QUEEN = QUEEN_req['QUEEN']
        PickleData(PB_Story_Pickle, QUEEN)

    APP_requests = ReadPickleData(pickle_file=PB_App_Pickle)
    APP_req = add_key_to_app(APP_requests)
    APP_requests = APP_req['APP_requests']
    if APP_req['update']:
        PickleData(PB_App_Pickle, APP_requests)

    logging.info("My Queen")

    
    # Extra Queen Info
    kingme = KING()
    # ipdb.set_trace()
    QUEEN['kings_order_rules'] = kingme['kings_order_rules']
    QUEEN['heartbeat']['main_indexes'] = {
        'SPY': {'long3X': 'SPXL', 'inverse': 'SH', 'inverse2X': 'SDS', 'inverse3X': 'SPXU'},
        'QQQ': {'long3X': 'TQQQ', 'inverse': 'PSQ', 'inverse2X': 'QID', 'inverse3X': 'SQQQ'}
        }
    # active_order_state_list = ['running', 'running_close', 'submitted']
    QUEEN['heartbeat']['active_order_state_list'] = active_order_state_list
    QUEEN['heartbeat']['active_tickers'] = ["SPY", "ETHUSD"]
    PickleData(pickle_file=PB_Story_Pickle, data_to_store=QUEEN)
    
    available_triggers = ["sell_cross-0", "buy_cross-0"]
    print("active trigs", available_triggers)
    print("active tickers", QUEEN['heartbeat']['active_tickers'])
    
    print("Here we go Mario")
    pollen_theme_dict = pollen_themes()
    workerbee_run_times = []
    queens_first_go = len(QUEEN['queen_orders'])

    while True:
        s = datetime.datetime.now()
        # Should you operate now? I thnik the brain never sleeps ?

        if queens_chess_piece.lower() == 'queen': # Rule On High
            """ The Story of every Knight and their Quest """

            pollen = read_queensmind(prod)
            QUEEN = pollen['queen']
            POLLENSTORY = read_pollenstory()


            # Read App Reqquests
            APP_requests = ReadPickleData(pickle_file=PB_App_Pickle)

            # Process All Orders
            order_management(api=api, QUEEN=QUEEN)  ### <>
                                                    ####>
            # Hunt for Triggers
            command_conscience(api=api, QUEEN=QUEEN, active_tickers=QUEEN['heartbeat']['active_tickers']) #####>   
                                                    ####>
            # order_management(api=api, QUEEN=QUEEN) ### <>
            

            time.sleep(1)
            e = datetime.datetime.now()
            # print(queens_chess_piece, str((e - s).seconds),  "sec: ", datetime.datetime.now().strftime("%A,%d. %I:%M:%S%p"))


            """
                > lets do this!!!!
                love: anchor on the 1 min macd crosses or better yet just return all triggers and base everything off the trigger
            """

    # >>> Buy Sell Weights 

    # >>> NEED TO FIX the return for each time interval, rebuild 5 Min, 1 hr...etc....Put rebuild charts into new dict where they get maintained...add logic for each interval...i.e. on 5Min Mark rebuild with Initiate OR replace last 5 Minutes....?
except Exception as errbuz:
    print(errbuz)
    erline = print_line_of_error()
    log_msg = {'type': 'ProgramCrash', 'lineerror': erline}
    print(log_msg)
    logging.critical(log_msg)
#### >>>>>>>>>>>>>>>>>>> END <<<<<<<<<<<<<<<<<<###