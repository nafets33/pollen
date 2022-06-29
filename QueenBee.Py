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
from QueenHive import slice_by_time, split_today_vs_prior, read_csv_db, update_csv_db, read_queensmind, read_pollenstory, pickle_chesspiece, speedybee, submit_order, return_timestamp_string, pollen_story, ReadPickleData, PickleData, return_api_keys, return_bars_list, refresh_account_info, return_bars, init_index_ticker, print_line_of_error, return_index_tickers
# from QueenHive import return_macd, return_VWAP, return_RSI, return_sma_slope

# script arguments
queens_chess_piece = sys.argv[1] # 'castle', 'knight' 'queen'

prod = False
pd.options.mode.chained_assignment = None
est = pytz.timezone("US/Eastern")
load_dotenv()
main_root = os.getcwd()
db_root = os.path.join(main_root, 'db')

# init_logging(queens_chess_piece, db_root)
loglog_newfile = False
log_dir = dst = os.path.join(db_root, 'logs')
log_dir_logs = dst = os.path.join(log_dir, 'logs')
if os.path.exists(dst) == False:
    os.mkdir(dst)
log_name = f'{"log_"}{queens_chess_piece}{".log"}'
log_file = os.path.join(os.getcwd(), log_name)
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

# Macd Settings
MACD_12_26_9 = {'fast': 12, 'slow': 26, 'smooth': 9}
QUEEN = { # The Queens Mind
    'command_conscience': {'memory': {'trigger_stopped': [], 'trigger_sell_stopped': [], 'orders_completed': [], 'running_bees': deque([], 89)}, 
                           'orders': { 'requests': [],
                                        'submitted': [],
                                        'running': [],
                                        'running_close': []}
                                        }, 
                            'collective_conscience': {'theme': {}}, # ONLY for the Kings Eyes
        'heartbeat': {}, # ticker info ... change name
        'kings_order_rules': {},
    # Worker Bees
    queens_chess_piece: {
    'conscience': {'STORY_bee': {},'KNIGHTSWORD': {}, 'ANGEL_bee': {}}, # 'command_conscience': {}, 'memory': {}, 'orders': []}, # change knightsword
    'pollenstory': {}, # latest story of dataframes castle and bishop
    'pollencharts': {}, # latest chart rebuild
    'pollencharts_nectar': {}, # latest chart rebuild with indicators
    'pollenstory_info': {}, # Misc Info,
    'client': {},
    # 'heartbeat': {},
    'last_modified' : datetime.datetime.now(),
    }
}

if queens_chess_piece == 'queen':  ## KINGS ORDERS
    kings_order_rules = {'knight_bees': {'buy_cross-0': {'timeduration': 1, 
                                                'take_profit': .005,
                                                'sellout': .01,
                                                'adjustable': True,
                                                'friend_links': [],
                                                    },
                                      'sell_cross-0': {'timeduration': 1, 
                                                'take_profit': .005,
                                                'sellout': .01,
                                                'adjustable': True,
                                                'friend_links': [],
                                                    },
                                      'ready_buy_cross': {'timeduration': 1, 
                                                'take_profit': .005,
                                                'sellout': .01,
                                                'adjustable': True,
                                                'friend_links': [],
                                                    },
                                      'ready_sell_cross': {'timeduration': 1, 
                                                'take_profit': .005,
                                                'sellout': .01,
                                                'adjustable': True,
                                                'friend_links': [],
                                                    },

################## crypto >>> crypto >>> crypto >>> crypto >>> crypto ###################                                        
                                      'crypto_buy_cross-0': {'timeduration': 1, 
                                                'take_profit': .005,
                                                'sellout': .01,
                                                'adjustable': True,
                                                'friend_links': [],
                                                    },
                                      'crypto_sell_cross-0': {'timeduration': 1, 
                                                'take_profit': .005,
                                                'sellout': .01,
                                                'adjustable': True,
                                                'friend_links': [],
                                                    },
                                        }
    }
    QUEEN['kings_order_rules'] = kings_order_rules


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

QUEEN['heartbeat']['main_indexes'] = {
    'SPY': {'long3X': 'SPXL', 'inverse': 'SH', 'inverse2X': 'SDS', 'inverse3X': 'SPXU'},
    'QQQ': {'long3X': 'TQQQ', 'inverse': 'PSQ', 'inverse2X': 'QID', 'inverse3X': 'SQQQ'}
    } 


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


def reconcile_portforlio(api, running_orders):
    # every running order should match up to portfolio HANDLE Gaps
    all_positions = api.list_positions()
    portfolio = {i.symbol: vars(i)["_raw"] for i in all_positions}
    running_orders = QUEEN['command_conscience']['orders']['running']

    # recon symbols and qty
    orders_current_status = [check_order_status(api=api, client_order_id=i['client_order_id']) for i in running_orders]
    running_symbols = {i['symbol']: i['filled_qty'] for i in running_orders}

    if running_close:
        for sy, f_qty in running_close.items():
            int(running_symbols[sy])
    # check if any orders are paritially filled and account for delta



def initialize_orders(api, start_date, end_date, symbols=False):
    if start_date==(datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y-%m-%d"):
        after = start_date
        until = end_date
        if symbols:
            closed_orders = api.list_orders(status='closed', symbols=symbols, after=after, until=until)
            open_orders = api.list_orders(status='open', symbols=symbols, after=after, until=until)
        else:
            closed_orders = api.list_orders(status='closed', after=after, until=until)
            open_orders = api.list_orders(status='open', after=after, until=until)
        
        return {'open': open_orders, 'closed': closed_orders}
    
    else:
        print("TDB chunk the dates and return all orders per day for x days")
        start_date = '2022-06-01'
        # count num of says from start and end
        # for every day return all closed orders
        # end_date = (datetime.datetime.now() - datetime.timedelta(days=1)) 
        # after = start_date
        # until = end_date
        # api_paper.list_orders(status='closed', symbols=symbols, after=after, until=until)
        pass


def create_running_order(order, trig):
    date_mark = datetime.datetime.now()
    if order['side'] == 'buy':
        running_order = {'symbol': order['symbol'], 'order_rules': kings_order_rules['knight_bees'][trig], 
                        'trigname': trig, 'datetime': date_mark, 
                        'status_q': status_q, 
                        'exit_order_links': exit_order_link, 'client_order_id': order['client_order_id'],
                        }
    else: # sell
        running_order = {'symbol': order['symbol'], 'order_rules': kings_order_rules['knight_bees'][trig], 
                        'trigname': trig, 'datetime': date_mark, 
                        'status_q': status_q, 
                        'exit_order_links': exit_order_link, 'client_order_id': order['client_order_id'],
                        }

    return running_order

def process_order_submission(order, trig, prod, tablename, status_q=False, exit_order_link=False):
    date_mark = datetime.datetime.now()
    symbol = order['symbol']
    client_order_id = order['client_order_id']
    alpaca_order_id = order['id']
    df_details = {'trigname': trig, 'client_order_id':client_order_id, 'origin_client_order_id':client_order_id, 'exit_order_link':exit_order_link, 'status_q': status_q, 'alpaca_order_id': alpaca_order_id} 
    df = pd.DataFrame(df_details.items()).T
    new_header = df.iloc[0] #grab the first row for the header
    df = df[1:] #take the data less the header row
    df.columns = new_header #set the header row as the df header
    update_csv_db(df_to_add=df, tablename=tablename, prod=prod, append=True)

    # sending_order = {'symbol': order['symbol'], 'order_rules': kings_order_rules['knight_bees'][trig], 'trigname': trig, 'datetime': date_mark, 'status_q': status_q, 'exit_order_links': exit_order_link, 'client_order_id': order['client_order_id'], 'sellable_qty': order['qty']}                                    
    sending_order = create_running_order(order=order, trig=trig)
    logging.info(kings_order_rules['knight_bees'][trig])
    trig_stop_info = {'symbol': symbol, 'trigname': trig, 'exit_order_link': exit_order_link, 'client_order_id': client_order_id, 'datetime': date_mark}
    
    return {'sending_order': sending_order, 'trig_stop_info': trig_stop_info}


def liquidate_position(api, ticker, side, type, client_order_id):
    client_order_id = f'{ticker}{"_"}{side}{"_"}{datetime.datetime.now().isoformat()}'
    p = api.get_position(ticker)
    p_qty = p.qty
    p_side = p.side
    if type ==  'market':
        order = submit_order(api=api, side=side, symbol=ticker, qty=p_qty, type=type, client_order_id=client_order_id)
    else:
        print("make this a limit order")
    return order


def check_order_status(api, client_order_id):
    order = api.get_order_by_client_order_id(client_order_id=client_order_id)
    order_ = vars(order)['_raw']
    return order_


def generate_client_order_id(ticker, trig):
    main_orders_table = read_csv_db(db_root=db_root, tablename='main_orders', prod=prod)
    main_trigs_df = main_orders_table[(main_orders_table['trigname']==trig) & (main_orders_table['exit_order_link'] != 'False')]
    trig_num = len(main_trigs_df)
    temp_date = datetime.datetime.now().strftime("%y%m%d-%M.%S")
    order_id = f'{ticker}{"-"}{trig}{"--"}{trig_num}--{temp_date}'

    return order_id


def command_conscience(api, ticker, STORY_bee):
    # ticker = 'SPY'
    # api = api_paper

    def king_knights_requests(QUEEN, ticker):
        # answer all questions for order to be placed, compare against the rules
        all_bees = QUEEN['kings_order_rules']['knight_bees'].keys()
        all_bees = ['buy_cross-0', 'sell_cross-0'] # test
        decision = {}

        for bee in all_bees:
            if bee == 'buy_cross-0':
                # Q?confirmation on trigger, should you wait for futher confirmation?

                theme_input = QUEEN['command_conscience']['collective_conscience']['theme']['current_state'] # what is the theme?
                # what is your timeblock?
                # what does your friend_links(bees) say? or have said?
                # 
                # what is the % amount you want to buy?
                # should you override your original order rules?


                pass
        return decision

    # ipdb.set_trace()
    ticker_storys = {k:v for (k, v) in STORY_bee['story'].items() if k.split("_")[0] == ticker} # filter by ticker
    all_current_triggers = {k:v['alltriggers_current_state'] for (k,v) in ticker_storys.items() if len(v['alltriggers_current_state']) > 0}
    # all_current_triggers.update({'SPY_1Minute_1Day': ['buy_cross-0']}) # test

    if all_current_triggers:
        # print("num of current triggers", len(all_current_triggers))
        if f'{ticker}{"_1Minute_1Day"}' in all_current_triggers.keys():
            # cycle through triggers and pass buy first logic for buy
            trigs =  all_current_triggers[f'{ticker}{"_1Minute_1Day"}']
            for trig in trigs:
                if trig == "buy_cross-0":
                    # check if you already placed order or if a workerbee in transit to place order
                    trigname_stopped = [item['trigname'] for item in QUEEN['command_conscience']['memory']['trigger_stopped']]
                    if trig in trigname_stopped:
                        continue # break loop
                    else:
                        print("CheckPoint_WhoAreYou?", trig, " time:", return_timestamp_string())
                        print("trig", trig, " time:", return_timestamp_string())
                        print("Each Buz in a gift")
                        # FUNCTION THAT CHECKS ORDER TO input Qty RETURN Story of other ttframes to influence order
                        r=king_knights_requests(QUEEN=QUEEN, ticker=ticker)
                        
                        # return num of trig for client_order_id
                        order_id = generate_client_order_id(ticker=ticker, trig=trig)
                        
                        order_submit = submit_order(api=api, symbol=ticker, type='market', qty=1, side='buy', client_order_id=order_id) # buy
                        order = vars(order_submit)['_raw']

                        # ensure order went through
                        if route_order_based_on_status(order_status=order['status']):
                            order_process = process_order_submission(trig=trig, order=order, prod=prod, tablename='main_orders')
                            QUEEN['command_conscience']['orders']['submitted'].append(order_process['sending_order'])
                            QUEEN['command_conscience']['memory']['trigger_stopped'].append(order_process['trig_stop_info'])
                            pickle_chesspiece(pickle_file=PB_Story_Pickle, data_to_store=QUEEN)
                            # json.dump(QUEEN['command_conscience'], open(PB_json_queen,"w"))
                        else:
                            msg = ("error order not accepted", order)
                            print(msg)
                            logging.error(msg)
                if trig == "sell_cross-0":
                    # print(trig)
                    if ticker in QUEEN['heartbeat']['main_indexes']: # SPY, QQQ
                        ticker = QUEEN['heartbeat']['main_indexes'][ticker]['inverse'] # SH SQQQ...
                        trigname_stopped = [item['trigname'] for item in QUEEN['command_conscience']['memory']['trigger_stopped']]
                        # check if you already placed order or if a workerbee in transit to place order
                        if trig in trigname_stopped:
                            continue # break loop
                        else:
                            print("trig", trig, return_timestamp_string())
                            print("Each Buz in a gift")
                            # FUNCTION THAT CHECKS ORDER TO input Qty RETURN Story of other ttframes to influence order
                            
                            # return num of trig for client_order_id
                            order_id = generate_client_order_id()
                            
                            order_submit = submit_order(api=api, symbol=ticker, type='market', qty=1, side='buy', client_order_id=order_id) # buy
                            order = vars(order_submit)['_raw']
                            # ensure order went through
                            if route_order_based_on_status(order_status=order['status']):
                                order_process = process_order_submission(trig=trig, order=order, prod=prod, tablename='main_orders')
                                QUEEN['command_conscience']['orders']['submitted'].append(order_process['sending_order'])
                                QUEEN['command_conscience']['memory']['trigger_stopped'].append(order_process['trig_stop_info'])
                                pickle_chesspiece(pickle_file=PB_Story_Pickle, data_to_store=QUEEN)
                                # json.dump(QUEEN['command_conscience'], open(PB_json_queen,"w"))
                            else:
                                msg = ("error order not accepted", order)
                                print(msg)
                                logging.error(msg)


def order_management(api): # Handle ALL submitted orders and place them

    def submitted_orders_main(api):
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
                order_status = check_order_status(api, client_order_id=order_id)
                #               
                # if order has fulfilled place in working orders else tag as partial order fulfilled
                if order_status['filled_qty']:
                    if order_status['side'] == 'buy':
                        if order_status['filled_qty'] == order_status['qty']: # move out of submitted to running
                            print("order filled, and move to memory")
                            # update order with latest infomation
                            fulfilled_qty = order_status['filled_qty']
                            QUEEN['command_conscience']['orders']['submitted'][idx]['filled_qty'] = fulfilled_qty
                            filled_avg_price = order_status['filled_avg_price']
                            QUEEN['command_conscience']['orders']['submitted'][idx]['filled_avg_price'] = filled_avg_price
                            # transistion from Submitted to Running
                            QUEEN['command_conscience']['orders']['running'].append(QUEEN['command_conscience']['orders']['submitted'][idx])
                            QUEEN['command_conscience']['orders']['submitted'].remove(QUEEN['command_conscience']['orders']['submitted'][idx])
    
                        elif int(order_status['filled_qty']) > 0: # move out of submitted to running same as if it was fully fulfilled
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
                        if order_status['filled_qty'] == order_status['qty']:   
                            
                            # update order with latest infomation
                            fulfilled_qty = order_status['filled_qty']
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


                            #### CHECK to see if Origin ORDER has Completed LifeCycle ####
                            exit_order_link = order_sent['exit_order_links']
                            orders_db = read_csv_db(db_root=db_root, tablename='main_orders', ext='.csv', prod=prod, init=False) # return all sellable orders where they have same client_order_id
                            all_linked_orders = orders_db[orders_db['exit_order_link'] == exit_order_link].copy()
                            all_linked_client_order_ids = all_linked_orders['exit_order_link'].to_list()
                            all_linked_filled_qty = 0
                            for c_order_id in all_linked_client_order_ids:
                                token_order = check_order_status(api=api, client_order_id=c_order_id)
                                all_linked_filled_qty += int(token_order['filled_qty'])

                            origin_order = [i for i in QUEEN['command_conscience']['orders']['running'] if i['client_order_id'] == exit_order_link][0]
                            if origin_order['filled_qty'] == all_linked_filled_qty: 
                                # running order has been fully sold out and now we can archive
                                QUEEN['command_conscience']['orders']['running'].remove(origin_order)
                                # remove trigger stops
                                stop = [i for i in QUEEN['command_conscience']['memory']['trigger_stopped'] if i['client_order_id'] == exit_order_link][0]
                                QUEEN['command_conscience']['memory']['trigger_stopped'].remove(stop)
                                # send to memory
                                QUEEN['command_conscience']['memory']['orders_completed'].append(origin_order)
                                # update db on origin order status?
                        
                        elif int(order_status['filled_qty']) > 0:
                            print("Order Partial fulfilled, move to running")
                            # update order with latest infomation
                            fulfilled_qty = order_status['filled_qty']
                            QUEEN['command_conscience']['orders']['submitted'][idx]['filled_qty'] = fulfilled_qty
                            filled_avg_price = order_status['filled_avg_price']
                            QUEEN['command_conscience']['orders']['submitted'][idx]['filled_avg_price'] = filled_avg_price
                            
                            # transistion from Submitted to Running
                            QUEEN['command_conscience']['orders']['running_close'].append(QUEEN['command_conscience']['orders']['submitted'][idx])
                            QUEEN['command_conscience']['orders']['submitted'].remove(QUEEN['command_conscience']['orders']['submitted'][idx])

                else:
                    print(order_status['client_order_id'], "order pending fill stays in submitted")
                    pass
            
            # god save the queen
            pickle_chesspiece(pickle_file=PB_Story_Pickle, data_to_store=QUEEN)
    
    submitted_orders_main(api)
    
    
    # >for every ticker position join in running-positions to account for total position
    # >for each running position determine to exit the position                
    all_positions = api.list_positions()
    portfolio = {i.symbol: vars(i)["_raw"] for i in all_positions}

    def running_orders_main(api):
        return True
    
    def running_close_orders_main(api):
        return True

    def validate_portfolio_with_RUNNING(queen_running, portfolio):
        all_positions = api.list_positions()
        portfolio = {i.symbol: vars(i)["_raw"] for i in all_positions}        
    
        return True

    # if profit has achived send order to take profit
    def re_evaluate_kings_orders(run_order, order_obj, current_profit_loss):
        # all scenarios if run_order should be closed out
        take_profit = run_order['order_rules']['take_profit'] #  {'order_rules': order_rules, 'trigname': trig, 'order': order, 'datetime': date_mark, 'status_q': False, 'exit_order': False}                                    
        sellout = run_order['order_rules']['sellout']
        sell_qty = int(order_obj['filled_qty'])
        
        side = 'sell'
        type ='market'

        if take_profit <= current_profit_loss:
            return {'bee_sell': True, 'type': type, 'side': side, 'sell_qty': sell_qty}
        
        # return client signal to sell
        db_app_dir = os.path.join(db_root, 'app')
        client_signal_json = os.path.join(db_app_dir, 'signals.json')
        client_signals_db = json.load(open(client_signal_json))
        json.dump(client_signals_db, open(client_signal_json,"w"))
        
        def initate_app_clientsignal_json_file(json_file):
            # re-create with 
            if os.path.exists(json_file):
                return json.load(open(json_file))
            else:
                # initiate app json file
                i = {'app': {'orders': {'sell': [], 'buy': []},
                            'themes' : {'main': True},
                            'throttle' : 1 
                                },
                    'self': {}
                    }
                json.dump(i, open(client_signal_json,"w"))
        
        
        return {'bee_sell': False, 'run_order': run_order}


    # if its in RUNNING then its fulfilled or partially fulfilled and now its time to figure out how to close the position
    for idx, run_order in enumerate(QUEEN['command_conscience']['orders']['running']):
        # try to close order
        runorder_client_order_id = run_order['client_order_id']
        ticker = run_order["symbol"]
        trigname = run_order['trigname']

        order_obj = check_order_status(api=api, client_order_id=runorder_client_order_id)

        trigname_stopped = [item['client_order_id'] for item in QUEEN['command_conscience']['memory']['trigger_sell_stopped']]
        # check if you already placed order or if a workerbee in transit to place order
        if runorder_client_order_id in trigname_stopped:
            continue # break loop

        # return trade info
        snap = api.get_snapshot(ticker)
        # current_price = STORY_bee[f'{ticker}{"_1Minute_1Day"}']['last_close_price']
        current_price = snap.latest_trade.price
        currnet_ask = snap.latest_quote.ask_price
        currnet_bid = snap.latest_quote.bid_price
        order_price = float(order_obj['filled_avg_price'])
        current_profit_loss = (current_price - order_price) / order_price
        # current_profit_loss = (currnet_ask - order_price) / order_price
        QUEEN['command_conscience']['orders']['running'][idx]['honey'] = current_profit_loss
        
        re_eval_order = re_evaluate_kings_orders(run_order, order_obj, current_profit_loss)

        if re_eval_order['bee_sell']:
            # close out order variables
            sell_qty = re_eval_order['sell_qty'] # int(order_obj['filled_qty'])
            side = re_eval_order['side'] # 'sell'
            type = re_eval_order['type'] # 'market'

            # check to see if you have enough Qty to Sell, if NOT archive running order and log as error
            all_positions = api.list_positions()
            portfolio = {i.symbol: vars(i)["_raw"] for i in all_positions}
            
            if ticker in portfolio.keys():
                if sell_qty <= portfolio[ticker]['qty']:
                    sell_validation = True
                else:
                    sell_validation = False
                    print("error, do not have enough shares to sell, check reason")
            else:
                sell_validation = False
                print("error TICKER NOT in Portfolio")
            
            ticker_portfolio_qty = portfolio['']

            #
            sell_client_order_id = f'{"close__"}{runorder_client_order_id}'
            send_close_order = submit_order(api=api, side=side, symbol=ticker, qty=sell_qty, type=type, client_order_id=sell_client_order_id) 
            send_close_order = vars(send_close_order)['_raw']
            if route_order_based_on_status(order_status=send_close_order['status']):
                print("Did you bring me some Honey?")
                order_process=process_order_submission(order=send_close_order, trig=trigname, exit_order_link=runorder_client_order_id, prod=prod, tablename='main_orders')
                QUEEN['command_conscience']['orders']['submitted'].append(order_process['sending_order'])
                QUEEN['command_conscience']['memory']['trigger_sell_stopped'].append(order_process['trig_stop_info'])
                pickle_chesspiece(pickle_file=PB_Story_Pickle, data_to_store=QUEEN)

            else:
                msg = ("error order not accepted", run_order)
                print(msg)
                logging.error(msg)


    # handle newly submitted closing orders 
    submitted_orders_main(api)

    # closed_orders_list = api.list_orders(status='closed')
    # open_orders_list = api.list_orders(status='open')

    # # get all orders that have been submitted
    # beeorders = QUEEN[queens_chess_piece]['conscience']['orders']
    
    # get all orders that are open

    if pickle_chesspiece(pickle_file=PB_Story_Pickle, data_to_store=QUEEN):
        pass
    else:
        print("ERROR WITH PICKLE")
        logging.critical("{'type': 'orders', 'errorname': 'ERROR WITH PICKLE'}")

    return True


def route_order_based_on_status(order_status):
    # https://alpaca.markets/docs/trading/orders/#order-lifecycle
    if order_status in ['accepted', 'pending_new', 'accepted_for_bidding', 'filled', 'partially_filled', 'new', 'calculated']:
        return True
    elif order_status in ['canceled', 'expired', 'replaced', 'pending_cancel', 'pending_replace', 'stopped', 'rejected', 'suspended']:
        return False
    else:
        print("unknown error")
        logging.error("unknown error")



###############>>>>
###############>>>>

###############>>>>
###############>>>>
###############>>>>

###############>>>>
###############>>>>

# if '_name_' == '_main_':
# print("Buzz Buzz Where My Honey")
try:
    if queens_chess_piece == 'queen':
        logging.info("My Queen")

    # init files needed
    if prod:
        api = api
        main_orders_file = os.path.join(db_root, 'main_orders.csv')
        PB_Story_Pickle = os.path.join(db_root, f'{queens_chess_piece}{".pkl"}')
        PB_json_queen = os.path.join(db_root, f'{queens_chess_piece}{".json"}')
        print("My Queen Production")
    else:
        api = api_paper
        main_orders_file = os.path.join(db_root, 'main_orders_sandbox.csv')
        PB_Story_Pickle = os.path.join(db_root, f'{queens_chess_piece}{'_sandbox'}{".pkl"}')
        PB_json_queen = os.path.join(db_root, f'{queens_chess_piece}{'_sandbox'}{".json"}')
        print("My Queen Sandbox")
        
        init_api_orders_start_date =(datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        init_api_orders_end_date = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        api_orders = initialize_orders(api, init_api_orders_start_date, init_api_orders_end_date)
        
        available_triggers = ["sell_cross-0", "buy_cross-0"]
        print(available_triggers)

    POLLENSTORY = read_pollenstory()
    def theme_calculator(POLLENSTORY, chart_times):
        # ticker = 'SPY' # test
        # chart_times = {
        #     "1Minute_1Day": 0, "5Minute_5Day": 5, "30Minute_1Month": 18, 
        #     "1Hour_3Month": 48, "2Hour_6Month": 72, 
        #     "1Day_1Year": 250}
        # return all prior 5 days close and compare to current, return angle of the different periods

        theme = {'castle': {},
                'sub_indexes': {},
                'big_players': {}
                    }
        tickers = set([i.split("_")[0] for i in POLLENSTORY.keys()])
        all_tframes = chart_times.keys()
        for ticker in tickers:
            theme[ticker] = {}
            for tframe in all_tframes:
                story={}
                # theme[ticker][] = {}
                theme_df = POLLENSTORY[f'{ticker}{"_"}{tframe}'].copy()

                if tframe == "1Minute_1Day":
                    theme_df = split_today_vs_prior(df=theme_df) # remove prior day
                    theme_today_df = theme_df['df_today']
                    theme_prior_df = theme_df['df_prior']                
                    
                    # we want...last vs currnet close prices, && Height+length of wave

                    # current from open price
                    open_price = theme_today_df.iloc[0]['close']
                    current_price = theme_today_df.iloc[-1]['close']
                    delta_pct = (current_price - open_price) / current_price
                    story['current_from_open'] = delta_pct
                    # current day slope
                    slope, intercept, r_value, p_value, std_err = stats.linregress(theme_today_df.index, theme_today_df['close'])
                    story['slope'] = slope
                    
                    # how did day start
                    last_price = theme_prior_df.iloc[-1]['close']
                    delta_pct = (open_price - last_price) / open_price
                    story['open_start'] = delta_pct
                    
                    
                    
                    theme[ticker][tframe] = story
        
        return theme
    
    trigger_bee_enable = {'VWAP_GRAVITY': {'desc': 'VWAP Gravity Kicks in starting 10:15 - 2 > if up holds'}}
    day_theme = {'strong_open': {'name': 'strong_open',
                                'desc': """SPY/overall up > 1% 
                                            & prior X(5) days decline is Z(-5%)
                                            
                                            """,
                                'formula': theme_calculator(POLLENSTORY, chart_times),
                                'triggerbees_tofind': ['VWAP_GRAVITY']
                                }
                    } # set the course for the day how you want to buy expecting more scalps vs long? this should update and change as new info comes into being


    workerbee_run_times = []
    while True:
        if queens_chess_piece.lower() == 'queen': # Rule On High
            # The story
            POLLENSTORY = read_pollenstory()
            queensmind = read_queensmind(prod) # return {'bishop': bishop, 'castle': castle, 'STORY_bee': STORY_bee, 'knightsword': knightsword}
            # The story behind the story       
            STORY_bee = queensmind['STORY_bee']
            KNIGHTSWORD = queensmind['KNIGHTSWORD']
            ANGEL_bee = queensmind['ANGEL_bee']

            # Should you operate now? I thnik the brain never sleeps ?

            # Populate QUEEN
            queen = queensmind['queen']            
            QUEEN['command_conscience']['memory'] = queen['command_conscience']['memory'] # return memory
            QUEEN['command_conscience']['orders'] = queen['command_conscience']['orders'] # return memory
            # Collective Conscience  
            QUEEN[queens_chess_piece]['conscience']['STORY_bee'] = queensmind['STORY_bee'] # return memory
            QUEEN[queens_chess_piece]['conscience']['KNIGHTSWORD'] = queensmind['KNIGHTSWORD'] # return memory
            QUEEN[queens_chess_piece]['conscience']['ANGEL_bee'] = queensmind['ANGEL_bee'] # return memory          
            
            STORY_bee = queensmind['STORY_bee'] # all ttframes with all immediate info needed

            chart_times = {
                "1Minute_1Day": 0, "5Minute_5Day": 5, "30Minute_1Month": 18, 
                "1Hour_3Month": 48, "2Hour_6Month": 72, 
                "1Day_1Year": 250}

            knight_bees = {}


            current_positions = {}
      
            # submit orders / gather all info first THEN submit order
            queens_requests_to_buy = {}
            story_tickers = set([i.split("_")[0] for i in STORY_bee.keys()])
            for story_ticker in story_tickers:
                if story_ticker == 'SPY':
                    command_conscience(api=api, ticker=story_ticker, STORY_bee=STORY_bee)            
            
            order_management(api=api)
            
            time.sleep(1)
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