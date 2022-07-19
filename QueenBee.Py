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
from alpaca_trade_api.rest import TimeFrame, URL
from alpaca_trade_api.rest_async import gather_with_concurrency, AsyncRest
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
from QueenHive import return_market_hours, return_dfshaped_orders, add_key_to_app, init_QUEEN, pollen_themes, init_app, check_order_status, slice_by_time, split_today_vs_prior, read_csv_db, update_csv_db, read_queensmind, read_pollenstory, pickle_chesspiece, speedybee, submit_order, return_timestamp_string, pollen_story, ReadPickleData, PickleData, return_api_keys, return_bars_list, refresh_account_info, return_bars, init_index_ticker, print_line_of_error, add_key_to_chesspiecePICKLE_if_key_does_not_exist
# from QueenHive import return_macd, return_VWAP, return_RSI, return_sma_slope

# if prior day abs(change) > 1 ignore ticker for the day! 
 
# script arguments
# queens_chess_piece = sys.argv[1] # 'castle', 'knight' 'queen'
queens_chess_piece = 'queen'
prod = False
pd.options.mode.chained_assignment = None
est = pytz.timezone("US/Eastern")
load_dotenv()
main_root = os.getcwd()
db_root = os.path.join(main_root, 'db')
db_app_root = os.path.join(db_root, 'app')

# init_logging(queens_chess_piece, db_root)
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

class return_pollen:
    POLLENSTORY = read_pollenstory()
    QUEENSMIND = read_queensmind(prod) # return {'bishop': bishop, 'castle': castle, 'STORY_bee': STORY_bee, 'knightsword': knightsword}
    QUEEN = QUEENSMIND['queen']
    
    # The story behind the story       
    STORY_bee = QUEEN['queen']['conscience']['STORY_bee']
    KNIGHTSWORD = QUEEN['queen']['conscience']['KNIGHTSWORD']
    ANGEL_bee = QUEEN['queen']['conscience']['ANGEL_bee']

# Macd Settings
# MACD_12_26_9 = {'fast': 12, 'slow': 26, 'smooth': 9}



if queens_chess_piece == 'queen':  ## KINGS ORDERS
    
    kings_order_rules = {'knight_bees': 
                                    {
                                    'queen_gen': {'timeduration': 1, 
                                            'take_profit': .005,
                                            'sellout': -.01,
                                            'adjustable': True,
                                            'friend_links': [],
                                                },
                                    'app': {'timeduration': 1, 
                                            'take_profit': .005,
                                            'sellout': -.01,
                                            'adjustable': True,
                                            'friend_links': [],
                                                },
                                    'buy_cross-0': {'timeduration': 1, 
                                            'take_profit': .005,
                                            'sellout': -.01,
                                            'adjustable': True,
                                            'friend_links': [],
                                                },
                                    'sell_cross-0': {'timeduration': 1, 
                                            'take_profit': .005,
                                            'sellout': -.01,
                                            'adjustable': True,
                                            'friend_links': [],
                                                },
                                    'ready_buy_cross': {'timeduration': 1, 
                                            'take_profit': .005,
                                            'sellout': -.01,
                                            'adjustable': True,
                                            'friend_links': [],
                                                },
                                    'ready_sell_cross': {'timeduration': 1, 
                                            'take_profit': .005,
                                            'sellout': -.01,
                                            'adjustable': True,
                                            'friend_links': [],
                                                },
                                    # CRYPTO
                                    'crypto_buy_cross-0': {'timeduration': 1, 
                                            'take_profit': .005,
                                            'sellout': -.01,
                                            'adjustable': True,
                                            'friend_links': [],
                                                },
                                    'crypto_sell_cross-0': {'timeduration': 1, 
                                            'take_profit': .005,
                                            'sellout': -.01,
                                            'adjustable': True,
                                            'friend_links': [],
                                                },
                                    }
    }



if queens_chess_piece.lower() not in ['queen']:
    print("wrong chess move")
    sys.exit()


# Client Tickers
src_root, db_dirname = os.path.split(db_root)
client_ticker_file = os.path.join(src_root, 'client_tickers.csv')
df_client = pd.read_csv(client_ticker_file, dtype=str)
df_client_f = df_client[df_client['status']=='active'].copy()
client_symbols = df_client_f.tickers.to_list()
client_symbols_castle = ['SPY', 'QQQ']
client_symbols_bishop = ['AAPL', 'GOOG']
client_market_movers = ['AAPL', 'TSLA', 'GOOG', 'META']
crypto_currency_symbols = ['BTCUSD', 'ETHUSD']
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


if prod: # Return Ticker and Acct Info
    # Initiate Code File Creation
    index_ticker_db = os.path.join(db_root, "index_tickers")
    if os.path.exists(index_ticker_db) == False:
        os.mkdir(index_ticker_db)
        print("Ticker Index db Initiated")
        init_index_ticker(index_list, db_root, init=True)
    """Account Infomation """
    acc_info = refresh_account_info(api)
    # Main Alloc
    portvalue_LT_iniate = acc_info[1]['portfolio_value'] * Long_Term_Client_Input
    portvalue_MID_iniate = acc_info[1]['portfolio_value'] * MidDayLag_Alloc
    portvalue_BeeHunter_iniate = acc_info[1]['portfolio_value'] * DayRiskAlloc

    # check alloc correct

    if round(portvalue_BeeHunter_iniate + portvalue_MID_iniate + portvalue_LT_iniate - acc_info[1]['portfolio_value'],4) > 1:
        print("break in Rev Alloc")
        sys.exit()

    """ Return Index Charts & Data for All Tickers Wanted"""
    """ Return Tickers of SP500 & Nasdaq / Other Tickers"""

    all_alpaca_tickers = api.list_assets()
    alpaca_symbols_dict = {}
    for n, v in enumerate(all_alpaca_tickers):
        if all_alpaca_tickers[n].status == 'active':
            alpaca_symbols_dict[all_alpaca_tickers[n].symbol] = vars(all_alpaca_tickers[n])

    symbol_shortable_list = []
    easy_to_borrow_list = []
    for ticker, v in alpaca_symbols_dict.items():
        if v['_raw']['shortable'] == True:
            symbol_shortable_list.append(ticker)
        if v['_raw']['easy_to_borrow'] == True:
            easy_to_borrow_list.append(ticker)

    # alpaca_symbols_dict[list(alpaca_symbols_dict.keys())[100]]

    market_exchanges_tickers = defaultdict(list)
    for k, v in alpaca_symbols_dict.items():
        market_exchanges_tickers[v['_raw']['exchange']].append(k)
    # market_exchanges = ['OTC', 'NASDAQ', 'NYSE', 'ARCA', 'AMEX', 'BATS']


    main_index_dict = index_ticker_db[0]
    main_symbols_full_list = index_ticker_db[1]
    not_avail_in_alpaca =[i for i in main_symbols_full_list if i not in alpaca_symbols_dict]
    main_symbols_full_list = [i for i in main_symbols_full_list if i in alpaca_symbols_dict]

    LongTerm_symbols = ['AAPL', 'GOOGL', 'MFST', 'VIT', 'HD', 'WMT', 'MOOD', 'LIT', 'SPXL', 'TQQQ']


    index_ticker_db = return_index_tickers(index_dir=os.path.join(db_root, 'index_tickers'), ext='.csv')

    """ Return Index Charts & Data for All Tickers Wanted"""
    """ Return Tickers of SP500 & Nasdaq / Other Tickers"""    

####<>///<>///<>///<>///<>/// ALL FUNCTIONS NECTOR ####<>///<>///<>///<>///<>///


print(
"""
We all shall prosper through the depths of our connected hearts,
Not all will share my world,
So I put forth my best mind of virtue and goodness, 
Always Bee Better
"""
)

            
def submit_order_validation(ticker, qty, side, portfolio, run_order_idx=False):
    
    if side == 'buy':
        return {'qty_correction': qty}
    else: # sel == sell
        position = float(portfolio[ticker]['qty_available'])
        if position > 0 and position < qty:
            msg = {"submit_order_validation()": {'p': position,  'msg': "not enough shares avail to sell, updating sell qty", 'ticker': ticker}}
            logging.error(msg)
            QUEEN["errors"].update({f'{symbol}{"_portfolio!=queen"}': {'msg': msg}})
            
            qty_correction = position - qty
            if run_order_idx: # update run_order
                print('Correcting Run Order Qty')
                msg = {"submit_order_validation()": {'p': position,  'msg': "not enough shares avail to sell, updating sell qty & RUN Index", 'ticker': ticker}}
                logging.error(msg)

                QUEEN['command_conscience']['orders']['running'][run_order_idx]['filled_qty'] = qty_correction
                QUEEN['command_conscience']['orders']['running'][run_order_idx]['status_q'] = True
                QUEEN['command_conscience']['orders']['running'][run_order_idx]['original_fulflled_qty'] = qty
            
            return {'qty_correction': qty_correction}
        else:
            return {'qty_correction': qty}



def return_alpc_portolio(api):
    all_positions = api.list_positions()
    portfolio = {i.symbol: vars(i)["_raw"] for i in all_positions}
    return {'portfolio': portfolio}


def reconcile_portfolio(running_orders, portfolio, portfolio_name='Jq'):  # IF MISSING FROM RUNNING ADD
    # If Ticker in portfolio but not in RUNNING !!!!!! Need to consider changing to qty_available from pending close orders
    # portfolio_holdings = {k : v['qty_available'] for (k,v) in portfolio.items()}
    # portfolio_holdings = {k : v['qty'] for (k,v) in portfolio.items()} 

    # return running_orders in df    
    running_portfolio = return_dfshaped_orders(running_orders=running_orders)

    for symbol in portfolio:
        if len(running_portfolio) > 0:
            if symbol not in running_portfolio['symbol'].values:
                msg = {"reconcile_portfolio()": f'{symbol}{": was missing added to RUNNING"}'}
                print(msg)
                logging.error(msg)
                
                # create a system gen. running order with portfolio info
                filled_qty = float(portfolio[symbol]["qty"])
                filled_avg_price = portfolio[symbol]["avg_entry_price"]
                side = portfolio[symbol]["side"]
                req_qty = portfolio[symbol]["qty"]
                system_recon = {'req_qty': req_qty, 'filled_qty': filled_qty, 'filled_avg_price': filled_avg_price, 'side': side}
                ticker_time_frame = f'{"symbol"}{"_queen_gen"}'
                trig = 'queen_gen'
                order = {'symbol': symbol, 'side': False, "id": "pollen_recon", 'client_order_id': generate_client_order_id(QUEEN=QUEEN,ticker=symbol, trig=trig)}
                
                order_process = process_order_submission(prod=prod, order=order, trig=trig, tablename='main_orders', ticker_time_frame=ticker_time_frame, system_recon=system_recon)
                QUEEN['command_conscience']['orders']['running'].append(order_process['sending_order'])
                QUEEN['command_conscience']['memory']['trigger_stopped'].append(order_process['trig_stop_info'])
            else: # symbol is in running check our totals
                total_running_ticker_qty = float(running_portfolio[running_portfolio['symbol']==symbol].iloc[0]['filled_qty'])
                total_portfolio_ticker_qty = float(portfolio[symbol]["qty"])
                # !!! check in running_close to see if you have an open order to match qty !!!
                if total_running_ticker_qty != total_portfolio_ticker_qty:
                    print(symbol, ": qty does not match, adjust running order to fix")
                    QUEEN["errors"].update({symbol: {'msg': "recon portfolio qty does not match!", 'root': "reconcile_portfolio"}})
                    run_order_ = {idx: i for (idx, i) in enumerate(QUEEN["command_conscience"]["orders"]["running"]) if i['symbol']==symbol}
                    if run_order_:
                        QUEEN["command_conscience"]["orders"]["running"][list(run_order_.keys())[0]]['filled_qty'] = total_portfolio_ticker_qty
                        QUEEN["command_conscience"]["orders"]["running"][list(run_order_.keys())[0]]['status_q'] = True
                    
                    # # update any running order
                    # if total_running_ticker_qty > total_portfolio_ticker_qty: # if T_run > portfolio 
                    #     qty_correction = total_portfolio_ticker_qty - (total_running_ticker_qty - total_portfolio_ticker_qty)
                    #     QUEEN["command_conscience"]["orders"]["running"][0]['filled_qty'] = qty_correction
                    #     QUEEN["command_conscience"]["orders"]["running"][0]['status_q'] = True
                    # else:
                    #     if total_portfolio_ticker_qty < 0: # short
                    #         qty_correction = (total_running_ticker_qty-total_portfolio_ticker_qty)
                    #     else:
                    #         qty_correction = total_running_ticker_qty + (total_portfolio_ticker_qty- total_running_ticker_qty)
                        
                    #     QUEEN["command_conscience"]["orders"]["running"][0]['filled_qty'] = qty_correction
                    #     QUEEN["command_conscience"]["orders"]["running"][0]['status_q'] = True

        else:
            msg = {"reconcile_portfolio()": f'{symbol}{": was missing added to RUNNING"}'}
            print(msg)
            logging.error(msg)
            
            # create a system gen. running order with portfolio info
            filled_qty = float(portfolio[symbol]["qty_available"])
            filled_avg_price = float(portfolio[symbol]["avg_entry_price"])
            side = portfolio[symbol]["side"]
            req_qty = float(portfolio[symbol]["qty_available"])
            system_recon = {'req_qty': req_qty, 'filled_qty': filled_qty, 'filled_avg_price': filled_avg_price, 'side': side}
            ticker_time_frame = f'{"symbol"}{"_1Minute_1Day"}'
            trig = 'queen_gen'
            order = {'symbol': symbol, 'side': False, "id": "pollen_recon", 'client_order_id': generate_client_order_id(QUEEN=QUEEN,ticker=symbol, trig=trig)}
            
            order_process = process_order_submission(prod=prod, order=order, trig=trig, tablename='main_orders', ticker_time_frame=False, system_recon=system_recon)
            QUEEN['command_conscience']['orders']['running'].append(order_process['sending_order'])
            QUEEN['command_conscience']['memory']['trigger_stopped'].append(order_process['trig_stop_info'])
            # PickleData(PB_Story_Pickle, QUEEN)
    
    return True



# def all_client_order_ids():
#     date_string = '2022-06-01'
#     start_date_conv = datetime.datetime.fromisoformat(date_string)
#     current_date = datetime.datetime.now()
#     all_orders = []
#     dates_timedetla = current_date - start_date_conv
#     delta_day = dates_timedetla.days
#     range_completed = []
#     for day_ in range(1, delta_day+1):
#         # print(day_)
#         day_start = datetime.datetime.now() - datetime.timedelta(days=day_)
#         s = day_start.strftime("%Y-%m-%d")
#         e = (datetime.datetime.now() + datetime.timedelta(days=day_+1)).strftime("%Y-%m-%d")
#         api_orders = initialize_orders(api, s, e)


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
        q_l = len(QUEEN['client_order_ids_qgen'])
        order_id = f'{order_id}{"_"}{q_l}'

    # append created id to QUEEN
    QUEEN['client_order_ids_qgen'].append(order_id)
    PickleData(pickle_file=PB_Story_Pickle, data_to_store=QUEEN)
    
    return order_id


def initialize_orders(api, start_date, end_date, symbols=False): # TBD
    after = start_date
    until = end_date
    if symbols:
        closed_orders = api.list_orders(status='closed', symbols=symbols, after=after, until=until)
        open_orders = api.list_orders(status='open', symbols=symbols, after=after, until=until)
    else:
        closed_orders = api.list_orders(status='closed', after=after, until=until)
        open_orders = api.list_orders(status='open', after=after, until=until)
    
    return {'open': open_orders, 'closed': closed_orders}


def process_order_submission(order, trig, prod, tablename, ticker_time_frame, portfolio_name='Jq', status_q=False, exit_order_link=False, bulkorder_origin__client_order_id=False, system_recon=False, priceinfo=False):

    def create_running_order(): # Create Running Order
        # ipdb.set_trace()
        date_mark = datetime.datetime.now()
        if system_recon:
            print("recon")
            running_order = {'symbol': order['symbol'], 'order_rules': QUEEN["kings_order_rules"]["knight_bees"][trig], 
                            'trigname': trig, 'datetime': date_mark,
                            'ticker_time_frame': ticker_time_frame, 
                            'status_q': status_q,
                            'portfolio_name': portfolio_name,
                            'exit_order_link': exit_order_link, 'client_order_id': order['client_order_id'],
                            'system_recon': True,
                            'req_qty': system_recon['req_qty'],
                            'filled_qty': system_recon['filled_qty'],
                            'filled_avg_price': system_recon['filled_avg_price'],
                            'side': system_recon['side'],
                            'price_time_of_request': 'na',
                            'bid': 'na',
                            'ask': 'na',
                            } 
        elif order['side'] == 'buy':
            print("buy")
            running_order = {'symbol': order['symbol'], 'order_rules': kings_order_rules['knight_bees'][trig], 
                            'trigname': trig, 'datetime': date_mark,
                            'ticker_time_frame': ticker_time_frame, 
                            'status_q': status_q,
                            'portfolio_name': portfolio_name,
                            'exit_order_link': exit_order_link, 'client_order_id': order['client_order_id'],
                            'system_recon': False,
                            'req_qty': order['qty'],
                            'filled_qty': order['filled_qty'],
                            'filled_avg_price': order['filled_avg_price'],
                            'side': order['side'],
                            'price_time_of_request': priceinfo['price'],
                            'bid': priceinfo['bid'],
                            'ask': priceinfo['ask'],
                            }
        elif order['side'] == 'sell':
            print("sell")
            running_order = {'symbol': order['symbol'], 'order_rules': kings_order_rules['knight_bees'][trig], 
                            'trigname': trig, 'datetime': date_mark,
                            'ticker_time_frame': ticker_time_frame, 
                            'status_q': status_q,
                            'portfolio_name': portfolio_name,
                            'exit_order_link': exit_order_link, 'client_order_id': order['client_order_id'],
                            'system_recon': False,
                            'req_qty': order['qty'],
                            'filled_qty': order['filled_qty'],
                            'filled_avg_price': order['filled_avg_price'],
                            'side': order['side'],
                            'price_time_of_request': priceinfo['price'],
                            'bid': priceinfo['bid'],
                            'ask': priceinfo['ask'],
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
    sending_order = create_running_order()

    logging.info(kings_order_rules['knight_bees'][trig])
    
    trig_stop_info = {'symbol': symbol, 'trigname': trig, 'ticker_time_frame': ticker_time_frame, 
    'exit_order_link': exit_order_link, 
    'client_order_id': client_order_id, 'datetime': date_mark}
    
    return {'sending_order': sending_order, 'trig_stop_info': trig_stop_info}


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


def clean_queens_memory(QUEEN, keyitem): # TBD Adhoc ONLY
    if keyitem == "trigger_stopped":
        QUEEN['command_conscience']['memory']['trigger_stopped'] = []
        PickleData(pickle_file=PB_Story_Pickle, data_to_store=QUEEN)


def recon_running_trigger_stops(QUEEN):
    run_dict = {'running': 'trigger_stopped', 'running_close': 'trigger_sell_stopped'}
    save_queen = False
    for run, runstop in run_dict.items():
        # check if item in other bucket, if NOT its MISSING
        for idx, run_order in enumerate(QUEEN['command_conscience']['orders'][run]):
            stop = [i for i in QUEEN['command_conscience']['memory'][runstop] if i['client_order_id'] == run_order['client_order_id']]
            if len(stop) == 0:
                save_queen = True
                msg = {"recon_running_trigger_stops": {"run_order": run_order['client_order_id']}}
                print(msg)
                logging.error(msg)

                # create trig stop
                trig_stop_info = {'symbol': run_order['symbol'], 'trigname': run_order['trigname'], 
                'ticker_time_frame': run_order['ticker_time_frame'], 'exit_order_link': run_order['exit_order_link'], 
                'client_order_id': run_order['client_order_id'], 'datetime': run_order['datetime']}
                QUEEN['command_conscience']['memory'][runstop].append(trig_stop_info)

        for idx, stop_trig in enumerate(QUEEN['command_conscience']['memory'][runstop]):
            matching_run = [i for i in QUEEN['command_conscience']['orders'][run] if i['client_order_id'] == stop_trig['client_order_id']]
            if len(matching_run) == 0:
                save_queen = True
                msg = {"recon_running_trigger_stops": {"msg": "stop found but no running order exists: REMOVING STOP", "run_order": stop_trig['client_order_id']}}
                print(msg)
                logging.error(msg)

                QUEEN['command_conscience']['memory'][runstop].remove(stop_trig)


    
    # God save the Queen
    if save_queen:
        PickleData(pickle_file=PB_Story_Pickle, data_to_store=QUEEN)
    
    return True


def process_app_requests(APP_requests, buy_sell):
    APP_requests = ReadPickleData(pickle_file=PB_App_Pickle)
    buy_sell = "buy_orders" # buy_orders
    # theme, sell, buy
    app_order_base = [i for i in APP_requests[buy_sell]]
    if app_order_base:
        for app_request in app_order_base:
            if app_request['app_requests_id'] in QUEEN['queen_controls']['app_order_requests']:
                print("request Id already received")
                APP_requests['app_order_requests'].append(app_request)
                APP_requests[buy_sell].remove(app_request)
                PickleData(pickle_file=PB_App_Pickle, data_to_store=APP_requests)
                order_flag = False
            else:
                order_flag = True
                wave_amo = app_request['wave_amo']
                r_type = app_request['type']
                r_side = app_request['side']
            
                king_resp = {app_request['trig']: {'side': r_side, 'type': r_type, 'wave_amo': wave_amo }}
                ticker_time_frame = f'{app_request["ticker"]}{"_app_bee"}'
                
                return {'king_resp': king_resp, 'order_flag': order_flag, 'app_request': app_request, 'ticker_time_frame': ticker_time_frame}
    
    else:
        order_flag = False
    return {'order_flag': order_flag}



"""  >>>><<<< MAIN <<<<>>>> """

def command_conscience(api, pollen):

    
    def execute_order(QUEEN, king_resp, ticker, ticker_time_frame, trig, portfolio):
        try:
            print(ticker_time_frame)
            logging.info(ticker_time_frame)
            # trig made it into the kingdom
            # ipdb.set_trace()
            print("Journy to the kingdom of heaven")
            side = king_resp[trig]['side']
            type = king_resp[trig]['type']
            wave_amo = king_resp[trig]['wave_amo']
            
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
                print(ticker_time_frame)
                
                order_process = process_order_submission(trig=trig, order=order, prod=prod, tablename='main_orders', ticker_time_frame=ticker_time_frame, priceinfo=priceinfo)
                
                QUEEN['command_conscience']['orders']['submitted'].append(order_process['sending_order'])
                QUEEN['command_conscience']['memory']['trigger_stopped'].append(order_process['trig_stop_info'])
                pickle_chesspiece(pickle_file=PB_Story_Pickle, data_to_store=QUEEN)
                msg = {'execute_order()': {'msg': "order submitted w trig stop", 'ticker_time_frame': ticker_time_frame, 'trig': trig, 'crypto': crypto}}
                logging.info(msg)
                print(msg)
                return{'executed': True, 'msg': msg}
            else:
                msg = ("error order not accepted", order)
                print(msg)
                logging.error(msg)
                return{'executed': False, 'msg': msg}
        except Exception as e:
            msg = {"execute_orderbees()": {'killqueen': "YES", 'ttf': ticker_time_frame, "error": e, 'line_er': print_line_of_error()}}
            print(msg)
            logging.error(msg)
            sys.exit()

    
    def king_knights_requests(trigbee, ticker_time_frame, trig_action=False, crypto=False):
        # answer all questions for order to be placed, compare against the rules
        
        def knigh_request_recon_portfolio():
            # debate if we should place a new order based on current portfolio trades
            pass
        
        
        def eval_trig_action():
            # evaluate if the current trade needs more love$
            pass


        ticker, tframe, frame = ticker_time_frame.split("_")
        decision = {}
        # Waves: current wave, answer questions what happen with proir waves
        waves = QUEEN[queens_chess_piece]['conscience']['STORY_bee'][ticker_time_frame]['waves'][trigbee]
        if "0" in waves.keys():
            waves.pop("0")
        total_waves = len(waves.keys())
        morning_waves = {k:v for (k,v) in waves.items() if v['wave_blocktime'] == "morning_9-11"}
        lunch_waves = {k:v for (k,v) in waves.items() if v['wave_blocktime'] == "lunch_11-2"}
        afternoon_waves = {k:v for (k,v) in waves.items() if v['wave_blocktime'] == "afternoon_2-4"}

        # Total Buying Power
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
        
        theme = QUEEN['queen_controls']['theme'] # what is the theme?

        # for bee in all_bees:
        if trigbee == 'buy_cross-0':
            # Q?confirmation on trigger, should you wait for futher confirmation?

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
            wave_amo = current_wave_amo * client_totalday_trade_amt_allowed
            
            # how many trades have we completed today? whats our total profit loss with wave trades
            
            # should you override your original order rules?

            kings_blessing = True

            if trig_action:
                print("evalatue if there is another trade to make on top of current wave")
                kings_blessing = False


        if trigbee == 'sell_cross-0':
            # Q?confirmation on trigger, should you wait for futher confirmation?

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
            wave_amo = current_wave_amo * client_totalday_trade_amt_allowed
            
            # how many trades have we completed today? whats our total profit loss with wave trades
            # should you override your original order rules?

            kings_blessing = True

            if trig_action:
                print("evalatue if there is another trade to make on top of current wave")
                kings_blessing = False

        
        decision[trigbee] = {'kings_blessing': kings_blessing, 'wave_amo': wave_amo, 'type': order_type}
        
        return decision


    # The Golden Ticket
    for ticker_time_frame in pollen.STORY_bee.keys():
        ticker, tframe, frame = ticker_time_frame.split("_")

        if ticker not in ["SPY", "BTCUSD"]: # only allowing SPY
            continue # break loop
        
        # if market closed do NOT Sell
        if rn_order_symbol in crypto_currency_symbols:
            crypto = True
        else:
            crypto = False
        
        mkhrs = return_market_hours(api_cal=trading_days, crypto=crypto)
        
        if mkhrs == 'open':
            val_pass = True
        else:
            continue # break loop
        

        ticker_storys = {k:v for (k, v) in pollen.STORY_bee.items() if k.split("_")[0] == ticker} # filter by ticker
        all_current_triggers = {k:v['story']['alltriggers_current_state'] for (k,v) in ticker_storys.items() if len(v['story']['alltriggers_current_state']) > 0}
        all_current_triggers.update({'BTCUSD_1Minute_1Day': ['buy_cross-0']}) # test

        if all_current_triggers:
            try:
                if f'{ticker}{"_1Minute_1Day"}' in all_current_triggers.keys():
                    ticker_time_frame = f'{ticker}{"_1Minute_1Day"}'
                    # cycle through triggers and pass buy first logic for buy
                    trigs =  all_current_triggers[f'{ticker}{"_1Minute_1Day"}']
                    for trig in trigs:
                        if trig == "buy_cross-0":
                            ipdb.set_trace()
                                                        
                            # check if you already placed order or if a workerbee in transit to place order
                            trigname_stopped = [item['trigname'] for item in QUEEN['command_conscience']['memory']['trigger_stopped']]
                            if trig in trigname_stopped:
                                trig_action = True # trig in a trade
                            else:
                                trig_action = False
                            
                            """ HAIL TRIGGER, WHAT SAY YOU?
                            ~forgive me but I bring a gift for the king and queen
                            """
                            king_resp = king_knights_requests(trigbee=trig, ticker_time_frame=ticker_time_frame, trig_action=trig_action)

                            if king_resp['kings_blessing']:
                                print("CheckPoint_WhoAreYou?", trig, " time:", return_timestamp_string())
                                print("trig", trig, " time:", return_timestamp_string())
                                print("Each Buz in a gift")

                                execute_order(king_resp, ticker_time_frame, trig, portfolio)
           
                        if trig == "sell_cross-0":
                            # print(trig)
                            # if ticker in QUEEN['heartbeat']['main_indexes']: # SPY, QQQ
                            ticker = QUEEN['heartbeat']['main_indexes'][ticker]['inverse'] # SH SQQQ...

                            trigname_stopped = [item['trigname'] for item in QUEEN['command_conscience']['memory']['trigger_stopped']]
                            # check if you already placed order or if a workerbee in transit to place order
                            if trig in trigname_stopped:
                                trig_action = True # trig in a trade
                            else:
                                trig_action = False
                            
                            king_resp = king_knights_requests(trigbee=trig, ticker_time_frame=ticker_time_frame, trig_action=trig_action)

                            if king_resp['kings_blessing']:
                                print("trig", trig, return_timestamp_string())
                                print("Each Buz in a gift")
                                
                                execute_order(QUEEN, king_resp, ticker, ticker_time_frame, trig, portflio)

            except Exception as e:
                print(e, print_line_of_error())
                print(ticker_time_frame)
    
    # App Buy Order Requests
    # app_resp = process_app_buy_requests(APP_requests)
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


def order_management(api): # Handle ALL submitted orders and place them

    def validate_portfolio_with_RUNNING(ticker, run_index, run_order, portfolio):        
        # check if there are enough shares in portfolio IF NOT Archive RUNNING ORDER AS IT WAS SOLD ALREADY
        if ticker in portfolio.keys():
            qty_avail = float(portfolio[ticker]['qty'])
            qty_run = float(run_order["filled_qty"])
            
            if qty_avail < 0 and qty_run < qty_avail: # short and run < avail (-10, -5)
                print("CRITICAL ERROR PORTFOLIO DOES NOT HAVE QTY AVAIL TO SELL ARCHVIE RUNNING ORDER")
                logging.critical({"msg": "run order qty > then avail in portfolio, adjust to remaining"})
                portfolio_validated = True
                QUEEN['command_conscience']['orders']['running'][run_index]["filled_qty"] = qty_avail
                QUEEN['command_conscience']['orders']['running'][run_index]["status_q"] = True
            
            elif qty_avail > 0 and qty_run > qty_avail: # long and run > avail (10, 5)
                    print("CRITICAL ERROR PORTFOLIO DOES NOT HAVE QTY AVAIL TO SELL ARCHVIE RUNNING ORDER")
                    logging.critical({"msg": "run order qty > then avail in portfolio, adjust to remaining"})
                    portfolio_validated = True
                    QUEEN['command_conscience']['orders']['running'][run_index]["filled_qty"] = qty_avail
                    QUEEN['command_conscience']['orders']['running'][run_index]["status_q"] = True
            
            elif qty_run == 0:
                print("Critical Error run qty is ZERO")
                logging.critical({"msg": "run order qty > then avail in portfolio, adjust to remaining"})
                portfolio_validated = True
                QUEEN['command_conscience']['orders']['running'][run_index]["filled_qty"] = qty_avail
                QUEEN['command_conscience']['orders']['running'][run_index]["status_q"] = True
            
            else:
                portfolio_validated = True
        
        else:
            print(ticker, "CRITICAL ERROR PORTFOLIO DOES NOT HAVE TICKER ARCHVIE RUNNING ORDER")
            logging.critical({'msg': f'{ticker}{" :Ticker not in Portfolio"}'})

            # REMOVE running order
            QUEEN['command_conscience']['memory']['orders_completed'].append(run_order)
            QUEEN['command_conscience']['orders']['running'].remove(QUEEN['command_conscience']['orders']['running'][run_index]) 
            # check if client order id in trig stop and REMOVE
            try:
                trigname_stop = [item for item in QUEEN['command_conscience']['memory']['trigger_stopped'] if item['client_order_id'] == runorder_client_order_id ]
                QUEEN['command_conscience']['memory']['trigger_stopped'].remove(trigname_stop[0])
                PickleData(pickle_file=PB_Story_Pickle, data_to_store=QUEEN)
            except Exception as e:
                msg = {"validate_portfolio_with_RUNNING": ("client_order_id NOT in trigger_stopped")}
                print(msg)
                logging.error(msg)
            
            portfolio_validated = False

        if portfolio_validated:
            # print("portfolio_validated")
            return {"run_order_valid":True}
        else:
            print("error in portfolio")
            return {"run_order_valid":False}

    
    def kning_queens_order_evaluation(run_order, current_profit_loss, portfolio):

        def process_app_sell_signal(runorder_client_order_id): # ONLY returns if not empty
            """Read App Controls and update if anything new"""
            # app_request = QUEEN['queen_controls']['orders']
            APP_requests = ReadPickleData(pickle_file=PB_App_Pickle)
            app_order_base = [i for i in APP_requests['sell_orders']]
            c_order_ids = {idx: i for idx, i in enumerate(app_order_base) if i['client_order_id'] == runorder_client_order_id}
            if c_order_ids: # App Requests to sell client_order_id
                print("App Request Order")
                logging.info("App Request Order")
                if len(c_order_ids) != 1:
                    ipdb.set_trace()
                    print("error duplicate client_order_id requests, taking latest")
                    logging.info("error duplicate client_order_id requests, taking latest")
                    app_request = c_order_ids[len(c_order_ids)-1]
                    for i in range(len(c_order_ids) - 1):
                        APP_requests["sell_orders"].remove(APP_requests["sell_orders"][i])
                        PickleData(pickle_file=PB_App_Pickle, data_to_store=APP_requests)
                    return {'sell_order': False}
                else:
                    app_request = c_order_ids[0]
                    if app_request['app_requests_id'] in QUEEN['queen_controls']['app_order_requests']:
                        print("request Id already received")
                        APP_requests['app_order_requests'].append(app_request)
                        APP_requests['sell_orders'].remove(app_request)
                        PickleData(pickle_file=PB_App_Pickle, data_to_store=APP_requests)
                        sell_order = False
                        sell_qty = False
                        type = False
                        side = False
                    else:
                        sell_order = True
                        sell_qty = app_request['sellable_qty']
                        type = app_request['type']
                        side = app_request['side']

                        QUEEN['queen_controls']['app_order_requests'].append(app_request['app_requests_id'])
                        pickle_chesspiece(pickle_file=PB_Story_Pickle, data_to_store=QUEEN)
                        APP_requests['sell_orders'].remove(app_request)
                        PickleData(pickle_file=PB_App_Pickle, data_to_store=APP_requests)
                                        
                        return {'sell_order': sell_order, 'sell_qty': sell_qty, 'type': type, 'side': side}
            else:
                return {'sell_order': False}

        # all scenarios if run_order should be closed out
        sell_order = False # convince me to sell
        
        rn_order_symbol = run_order['symbol']
        runorder_client_order_id = run_order['client_order_id']
        take_profit = run_order['order_rules']['take_profit'] #  {'order_rules': order_rules, 'trigname': trig, 'order': order, 'datetime': date_mark, 'status_q': False, 'exit_order': False}                                    
        sellout = run_order['order_rules']['sellout']
        sell_qty = float(run_order['filled_qty'])
        
        side = 'sell'
        type ='market'

        app_req = process_app_sell_signal(runorder_client_order_id)

        if app_req:
            if app_req['sell_order']:
                sell_order = True
                app_reqest = True
                
                sell_qty = app_req['sell_qty']
                type = app_req['type']
                side = app_req['side']

        elif take_profit <= current_profit_loss:
            sell_order = True
        
        elif current_profit_loss <= sellout:
            sell_order = True

        # elif the 3 wisemen pointing to sell or re-chunk profits
        
        else:
            sell_order = False
        
        
        # recon portolio to validate if sell qty allowed
        if app_req:
            app_reqest = True
        else:
            app_request = False

        # check if position is neg, if so, switch side to sell and sell_qty to buy
        if portfolio[rn_order_symbol]['side'] == 'short':
            sell_qty = abs(sell_qty)
            side = 'buy'
        
        # if market closed do NOT Sell
        if rn_order_symbol in crypto_currency_symbols:
            crypto = True
        else:
            crypto = False
        
        mkhrs = return_market_hours(api_cal=trading_days, crypto=crypto)
        
        if mkhrs == 'open':
            sell_order = sell_order
        else:
            sell_order = False

        if sell_order:
            return {'bee_sell': True, 'type': type, 'side': side, 'sell_qty': sell_qty, 'app_request': app_request}
        else:
            return {'bee_sell': False, 'run_order': run_order}


    def submitted_orders_main():
        # put submit order in memory
        # if orders: read memory and find orders with it info
        # once order received and fulfilled discard from memory or place it in completed
        # what happens when trigs submitted not in orders?
        submitted_trigs = [i for i in QUEEN['command_conscience']['orders']['submitted']]
        if submitted_trigs:
            for idx, order_sent in enumerate(submitted_trigs):
                ticker = order_sent['symbol']
                order_id = order_sent['client_order_id']
                # check if order fulfilled
                order_status = check_order_status(api=api, client_order_id=order_id, queen_order=order_sent)
                ipdb.set_trace()
                # if order has fulfilled place in working orders else tag as partial order fulfilled
                if order_status["filled_qty"]:
                    if order_status['side'] == 'buy':
                        if float(order_status['filled_qty']) == float(order_sent['filled_qty']): # move out of submitted to running
                            print("order filled, and move to memory")
                            # update order with latest infomation
                            fulfilled_qty = order_status['filled_qty']
                            QUEEN['command_conscience']['orders']['submitted'][idx]['filled_qty'] = fulfilled_qty
                            filled_avg_price = order_status['filled_avg_price']
                            QUEEN['command_conscience']['orders']['submitted'][idx]['filled_avg_price'] = filled_avg_price
                            # transistion from Submitted to Running
                            QUEEN['command_conscience']['orders']['running'].append(QUEEN['command_conscience']['orders']['submitted'][idx])
                            QUEEN['command_conscience']['orders']['submitted'].remove(QUEEN['command_conscience']['orders']['submitted'][idx])
    
                        elif float(order_status['filled_qty']) > 0: # move out of submitted to running same as if it was fully fulfilled
                            print("order partially filled, and move to memory")
                            # update order with latest infomation
                            fulfilled_qty = order_status['filled_qty']
                            QUEEN['command_conscience']['orders']['submitted'][idx]['filled_qty'] = fulfilled_qty
                            filled_avg_price = order_status['filled_avg_price']
                            QUEEN['command_conscience']['orders']['submitted'][idx]['filled_avg_price'] = filled_avg_price
                            # transistion from Submitted to Running
                            QUEEN['command_conscience']['orders']['running'].append(QUEEN['command_conscience']['orders']['submitted'][idx])
                            QUEEN['command_conscience']['orders']['submitted'].remove(QUEEN['command_conscience']['orders']['submitted'][idx])
                    
                    if order_status['side'] == 'sell':
                        if float(order_status['filled_qty']) == float(order_sent['filled_qty']):
                            
                            # update order with latest infomation
                            fulfilled_qty = float(order_status['filled_qty'])
                            QUEEN['command_conscience']['orders']['submitted'][idx]['filled_qty'] = fulfilled_qty
                            filled_avg_price = order_status['filled_avg_price']
                            QUEEN['command_conscience']['orders']['submitted'][idx]['filled_avg_price'] = filled_avg_price
                            
                            # remove from submitted and archive as you've done your job
                            stop = [i for i in QUEEN['command_conscience']['memory']['trigger_sell_stopped'] if i['client_order_id'] == order_id][0]
                            QUEEN['command_conscience']['memory']['trigger_sell_stopped'].remove(stop)
                            
                            # archive to memory
                            QUEEN['command_conscience']['memory']['orders_completed'].append(QUEEN['command_conscience']['orders']['submitted'][idx])
                            
                            # remove from submitted
                            QUEEN['command_conscience']['orders']['submitted'].remove(QUEEN['command_conscience']['orders']['submitted'][idx])

                            # def origin_order_complete(exit_order_link):
                            #### CHECK to see if Origin ORDER has Completed LifeCycle ####
                            exit_order_link = order_sent['exit_order_link']
                            orders_db = read_csv_db(db_root=db_root, tablename='main_orders', ext='.csv', prod=prod, init=False) # return all sellable orders where they have same client_order_id
                            all_linked_orders = orders_db[orders_db['exit_order_link'] == exit_order_link].copy()
                            all_linked_client_order_ids = all_linked_orders['exit_order_link'].to_list()
                            all_linked_filled_qty = 0 # set populate 
                            for c_order_id in all_linked_client_order_ids:
                                token_order = check_order_status(api=api, client_order_id=c_order_id, queen_order=order_sent)
                                all_linked_filled_qty += float(token_order['filled_qty'])

                            origin_order = [i for i in QUEEN['command_conscience']['orders']['running'] if i['client_order_id'] == exit_order_link][0]
                            if float(origin_order["filled_qty"]) == all_linked_filled_qty: 
                                # running order has been fully sold out and now we can archive
                                QUEEN['command_conscience']['orders']['running'].remove(origin_order)
                                # remove trigger stops
                                stop = [i for i in QUEEN['command_conscience']['memory']['trigger_stopped'] if i['client_order_id'] == exit_order_link][0]
                                QUEEN['command_conscience']['memory']['trigger_stopped'].remove(stop)
                                # send to memory
                                QUEEN['command_conscience']['memory']['orders_completed'].append(origin_order)
                                # update db on origin order status?
                            else:
                                print("origin order still has shares to sell")
                        
                        elif float(order_status['filled_qty']) > 0:
                            print("Order Partial fulfilled, move to running")
                            # update order with latest infomation
                            fulfilled_qty = float(order_status['filled_qty'])
                            QUEEN['command_conscience']['orders']['submitted'][idx]['filled_qty'] = fulfilled_qty
                            filled_avg_price = float(order_status['filled_avg_price'])
                            QUEEN['command_conscience']['orders']['submitted'][idx]['filled_avg_price'] = filled_avg_price
                            
                            # transistion from Submitted to Running
                            QUEEN['command_conscience']['orders']['running_close'].append(QUEEN['command_conscience']['orders']['submitted'][idx])
                            QUEEN['command_conscience']['orders']['submitted'].remove(QUEEN['command_conscience']['orders']['submitted'][idx])

                else:
                    print(order_status['client_order_id'], "order pending fill stays in submitted")
                    pass
            
            # god save the queen
            pickle_chesspiece(pickle_file=PB_Story_Pickle, data_to_store=QUEEN)
        
        return True


    def running_orders_main():
        # if its in RUNNING then its fulfilled or partially fulfilled and now its time to figure out how to close the position
        for idx, run_order in enumerate(QUEEN['command_conscience']['orders']['running']):
            try:                
                # try to close order
                ticker_time_frame = run_order['ticker_time_frame']
                runorder_client_order_id = run_order['client_order_id']
                ticker = run_order["symbol"]
                trigname = run_order['trigname']
                
                # VALIDATE BEE ORDER check if there are enough shares in portfolio IF NOT Archive RUNNING ORDER AS IT WAS SOLD ALREADY
                val = validate_portfolio_with_RUNNING(ticker=ticker, run_index=idx, run_order=run_order, portfolio=portfolio)
                if val["run_order_valid"] == False:
                    pass
                    ### space ###
                    continue # break loop run order archived
                
                # if not system recon
                order_obj = check_order_status(api=api, client_order_id=runorder_client_order_id, queen_order=run_order)
                
                # a. check if you already placed a SELL Order OR b. if a workerbee in transit to place order
                trigname_stopped = [item['exit_order_link'] for item in QUEEN['command_conscience']['memory']['trigger_sell_stopped']] # a
                if runorder_client_order_id in trigname_stopped:
                    pass
                    ### space ###
                    continue # break loop
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
                order_price = float(order_obj['filled_avg_price'])
                current_profit_loss = (current_price - order_price) / order_price
                # current_profit_loss = (current_ask - order_price) / order_price
                QUEEN['command_conscience']['orders']['running'][idx]['honey'] = current_profit_loss
                QUEEN['command_conscience']['orders']['running'][idx]['$honey'] = float(order_obj['filled_avg_price']) * float(order_obj['filled_qty']) - current_price * float(order_obj['filled_qty'])
                
                re_eval_order = kning_queens_order_evaluation(run_order, current_profit_loss, portfolio)

                if re_eval_order['bee_sell']:
                    # close out order variables
                    sell_qty = float(re_eval_order['sell_qty']) # float(order_obj['filled_qty'])
                    side = re_eval_order['side'] # 'sell' Unless it short then it will be a 'buy'
                    type = re_eval_order['type'] # 'market'
                    # print(ticker_time_frame, " meee")
                    # ipdb.set_trace()
                    sell_client_order_id = generate_client_order_id(QUEEN=QUEEN, ticker=ticker, trig=trigname, db_root=db_root, sellside_client_order_id=runorder_client_order_id)
                    run_order_idx = {'runorder_idx': idx}
                    
                    send_order_val = submit_order_validation(ticker=ticker, qty=sell_qty, side=side, portfolio=portfolio, run_order_idx=run_order_idx)
                    
                    sell_qty = send_order_val['qty_correction']

                    send_close_order = submit_order(api=api, side=side, symbol=ticker, qty=sell_qty, type=type, client_order_id=sell_client_order_id) 
                    send_close_order = vars(send_close_order)['_raw']
                    if route_order_based_on_status(order_status=send_close_order['status']):
                        print("Did you bring me some Honey?")

                        order_process = process_order_submission(order=send_close_order, trig=trigname, exit_order_link=runorder_client_order_id, prod=prod, tablename='main_orders', ticker_time_frame=ticker_time_frame, priceinfo=priceinfo)
                        QUEEN['command_conscience']['orders']['submitted'].append(order_process['sending_order'])
                        QUEEN['command_conscience']['memory']['trigger_sell_stopped'].append(order_process['trig_stop_info'])
                        pickle_chesspiece(pickle_file=PB_Story_Pickle, data_to_store=QUEEN)

                    else:
                        msg = {"order_management()" : ("runorder_client_order_id", run_order['client_order_id'])}
                        print(msg)
                        logging.error(msg)
            except Exception as e:
                msg = {"running_orders_main()": {"killqueen" : "YES", "runorder": ticker, "er_line": print_line_of_error()}}
                print(msg)
                sys.exit()


    #### MAIN ####
    # >for every ticker position join in running-positions to account for total position
    # >for each running position determine to exit the position                

    portfolio = return_alpc_portolio(api)
    portfolio = portfolio['portfolio']

    running_orders = QUEEN['command_conscience']['orders']['running']

    # Confirm Theme
    if APP_requests['last_app_update'] > QUEEN['queen_controls']['last_read_app']:
        print("app request")
        # always set Theme
        if QUEEN['queen_controls']['theme'] != APP_requests['theme']:
            print("setting new theme", APP_requests['theme'])
            logging.info({'new_theme': APP_requests['theme'] })
        QUEEN['queen_controls']['theme'] = APP_requests['theme']
        QUEEN['queen_controls']['last_read_app'] = APP_requests['last_app_update']


    # Submitted Orders First
    submitted_orders_main()

    # running orders
    running_orders_main()

    # handle newly submitted closing orders 
    submitted_orders_main()

    # Reconcile QUEENs portfolio
    reconcile_portfolio(running_orders=running_orders, portfolio=portfolio, portfolio_name="Jq")

    # God Save the Queen
    PickleData(pickle_file=PB_Story_Pickle, data_to_store=QUEEN)

    return True



# if '_name_' == '_main_':
try:
    # init files needed
    if prod:
        api = api
        main_orders_file = os.path.join(db_root, 'main_orders.csv')
        PB_Story_Pickle = os.path.join(db_root, f'{queens_chess_piece}{".pkl"}')
        if os.path.exists(PB_Story_Pickle) == False:
            QUEEN = init_QUEEN()
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
            QUEEN = init_QUEEN()
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
    
    
    pollen = return_pollen()
    QUEEN = pollen.QUEEN
    QUEEN = add_key_to_chesspiecePICKLE_if_key_does_not_exist(QUEEN=QUEEN, queens_chess_piece=queens_chess_piece)

    APP_requests = ReadPickleData(pickle_file=PB_App_Pickle)
    APP_requests = add_key_to_app(APP_requests)
    
    logging.info("My Queen")
    
    available_triggers = ["sell_cross-0", "buy_cross-0"]
    print(available_triggers)

    QUEEN['kings_order_rules'] = kings_order_rules
    QUEEN['heartbeat']['main_indexes'] = {
        'SPY': {'long3X': 'SPXL', 'inverse': 'SH', 'inverse2X': 'SDS', 'inverse3X': 'SPXU'},
        'QQQ': {'long3X': 'TQQQ', 'inverse': 'PSQ', 'inverse2X': 'QID', 'inverse3X': 'SQQQ'}
        } 
    
    pollen_theme_dict = pollen_themes()
    workerbee_run_times = []
    while True:
        s = datetime.datetime.now()
        # Should you operate now? I thnik the brain never sleeps ?

        if queens_chess_piece.lower() == 'queen': # Rule On High
            """ The Story of every Knight and their Quest """
            pollen = return_pollen()
            QUEEN = pollen.QUEEN

            # Read App Reqquests
            APP_requests = ReadPickleData(pickle_file=PB_App_Pickle)            

            chart_times = {
                "1Minute_1Day": 0, "5Minute_5Day": 5, "30Minute_1Month": 18, 
                "1Hour_3Month": 48, "2Hour_6Month": 72, 
                "1Day_1Year": 250}
            
            recon_running_trigger_stops(QUEEN=QUEEN)

            order_management(api=api)  ### <>
                                                    #>
            command_conscience(api=api, pollen=pollen) ###>   
                                                    #>
            order_management(api=api) ### <>
            
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
    pickle_chesspiece(pickle_file=PB_Story_Pickle, data_to_store=QUEEN)

#### >>>>>>>>>>>>>>>>>>> END <<<<<<<<<<<<<<<<<<###