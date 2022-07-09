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
from QueenHive import init_QUEEN, pollen_themes, init_app, check_order_status, slice_by_time, split_today_vs_prior, read_csv_db, update_csv_db, read_queensmind, read_pollenstory, pickle_chesspiece, speedybee, submit_order, return_timestamp_string, pollen_story, ReadPickleData, PickleData, return_api_keys, return_bars_list, refresh_account_info, return_bars, init_index_ticker, print_line_of_error, add_key_to_chesspiecePICKLE_if_key_does_not_exist
# from QueenHive import return_macd, return_VWAP, return_RSI, return_sma_slope

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
                                    # CRYPTO
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


def reconcile_portforlio(api, running_orders):  # TBD
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


def liquidate_position(api, ticker, side, type, client_order_id): # TBD
    client_order_id = f'{ticker}{"_"}{side}{"_"}{datetime.datetime.now().isoformat()}'
    p = api.get_position(ticker)
    p_qty = p.qty
    p_side = p.side
    if type ==  'market':
        order = submit_order(api=api, side=side, symbol=ticker, qty=p_qty, type=type, client_order_id=client_order_id)
    else:
        print("make this a limit order")
    return order


def generate_client_order_id(ticker, trig, db_root=db_root, sellside_client_order_id=False): # generate using main_order table and trig count
    main_orders_table = read_csv_db(db_root=db_root, tablename='main_orders', prod=prod)
    temp_date = datetime.datetime.now().strftime("%y%m%d-%M.%S")
    
    if sellside_client_order_id:
        main_trigs_df = main_orders_table[main_orders_table['exit_order_link'] == sellside_client_order_id].copy()
        trig_num = len(main_trigs_df)
        order_id = f'{"close__"}{trig_num}-{sellside_client_order_id}'
    else:
        main_trigs_df = main_orders_table[(main_orders_table['trigname']==trig) & (main_orders_table['exit_order_link'] != 'False')].copy()
        
        trig_num = len(main_trigs_df)
        order_id = f'{"run__"}{ticker}-{trig}-{trig_num}-{temp_date}'

    return order_id


def initialize_orders(api, start_date, end_date, symbols=False): # TBD
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



def process_order_submission(order, trig, prod, tablename, ticker_time_frame, status_q=False, exit_order_link=False, bulkorder_origin__client_order_id=False):

    def create_running_order():
        date_mark = datetime.datetime.now()
        if order['side'] == 'buy':
            running_order = {'symbol': order['symbol'], 'order_rules': kings_order_rules['knight_bees'][trig], 
                            'trigname': trig, 'datetime': date_mark,
                            'ticker_time_frame': ticker_time_frame, 
                            'status_q': status_q, 
                            'exit_order_links': exit_order_link, 'client_order_id': order['client_order_id'],
                            }
        else: # sell
            running_order = {'symbol': order['symbol'], 'order_rules': kings_order_rules['knight_bees'][trig], 
                            'trigname': trig, 'datetime': date_mark,
                            'ticker_time_frame': ticker_time_frame, 
                            'status_q': status_q, 
                            'exit_order_links': exit_order_link, 'client_order_id': order['client_order_id'],
                            }

        return running_order

    
    date_mark = datetime.datetime.now()
    symbol = order['symbol']
    client_order_id = order['client_order_id']
    alpaca_order_id = order['id']
    df_details = {'trigname': trig, 'client_order_id':client_order_id, 'origin_client_order_id':client_order_id, 
    'exit_order_link':exit_order_link, 'ticker_time_frame': ticker_time_frame, 'status_q': status_q, 'alpaca_order_id': alpaca_order_id,
    'bulkorder_origin__client_order_id': bulkorder_origin__client_order_id} 
    df = pd.DataFrame(df_details.items()).T
    new_header = df.iloc[0] #grab the first row for the header
    df = df[1:] #take the data less the header row
    df.columns = new_header #set the header row as the df header
    update_csv_db(df_to_add=df, tablename=tablename, prod=prod, append=True)

    # Create Running Order
    sending_order = create_running_order()

    logging.info(kings_order_rules['knight_bees'][trig])
    trig_stop_info = {'symbol': symbol, 'trigname': trig, 'ticker_time_frame': ticker_time_frame, 'exit_order_link': exit_order_link, 
    'client_order_id': client_order_id, 'datetime': date_mark}
    
    return {'sending_order': sending_order, 'trig_stop_info': trig_stop_info}


def route_order_based_on_status(order_status):
    # https://alpaca.markets/docs/trading/orders/#order-lifecycle
    if order_status in ['accepted', 'pending_new', 'accepted_for_bidding', 'filled', 'partially_filled', 'new', 'calculated']:
        return True
    elif order_status in ['canceled', 'expired', 'replaced', 'pending_cancel', 'pending_replace', 'stopped', 'rejected', 'suspended']:
        return False
    else:
        print("unknown error")
        logging.error("unknown error")


"""  >>>><<<< MAIN <<<<>>>> """

def command_conscience(api, ticker_time_frame, pollen):
    ticker, tframe, frame = ticker_time_frame.split("_")
    # api = api_paper

    if "SPY" != ticker: # only allowing SPY
        return False

    def king_knights_requests(trigbee, ticker_time_frame):
        # answer all questions for order to be placed, compare against the rules
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

        # for bee in all_bees:
        if trigbee == 'buy_cross-0':
            # Q?confirmation on trigger, should you wait for futher confirmation?

            theme = QUEEN['queen_controls']['theme'] # what is the theme?
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
            
            client_totalday_trade_amt_allowed = app_portfolio_day_trade_allowed * float(total_buying_power)

            order_type = "market"
            wave_amo = current_wave_amo * client_totalday_trade_amt_allowed
            # how many trades have we completed today? whats our total profit loss with wave trades
            # should you override your original order rules?

        if trigbee == 'sell_cross-0':
            # Q?confirmation on trigger, should you wait for futher confirmation?

            theme = QUEEN['queen_controls']['theme'] # what is the theme?
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

        decision[trigbee] = {'wave_amo': wave_amo, 'type': order_type}
        return decision

    ticker_storys = {k:v for (k, v) in pollen.STORY_bee.items() if k.split("_")[0] == ticker} # filter by ticker
    all_current_triggers = {k:v['story']['alltriggers_current_state'] for (k,v) in ticker_storys.items() if len(v['story']['alltriggers_current_state']) > 0}
    # all_current_triggers.update({'SPY_1Minute_1Day': ['buy_cross-0']}) # test

    if all_current_triggers:
        if f'{ticker}{"_1Minute_1Day"}' in all_current_triggers.keys():
            ticker_time_frame = f'{ticker}{"_1Minute_1Day"}'
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
                        king_resp = king_knights_requests(trigbee=trig, ticker_time_frame=ticker_time_frame)
                        if trig in king_resp.keys():
                            type_order = king_resp[trig]['type']
                            wave_amo = king_resp[trig]['wave_amo']
                            snap = api.get_snapshot(ticker)
                            current_price = snap.latest_trade.price
                            qty_order = int(round(wave_amo / current_price, 0))

                            # return num of trig for client_order_id
                            order_id = generate_client_order_id(ticker=ticker, trig=trig)
                            
                            if type_order == 'market':
                                order_submit = submit_order(api=api, symbol=ticker, type='market', qty=qty_order, side='buy', client_order_id=order_id) # buy
                            else:
                                order_submit = submit_order(api=api, symbol=ticker, type='market', qty=qty_order, side='buy', client_order_id=order_id) # buy
                            order = vars(order_submit)['_raw']

                            # ensure order went through
                            if route_order_based_on_status(order_status=order['status']):
                                order_process = process_order_submission(trig=trig, order=order, prod=prod, tablename='main_orders', ticker_time_frame=ticker_time_frame)
                                QUEEN['command_conscience']['orders']['submitted'].append(order_process['sending_order'])
                                QUEEN['command_conscience']['memory']['trigger_stopped'].append(order_process['trig_stop_info'])
                                pickle_chesspiece(pickle_file=PB_Story_Pickle, data_to_store=QUEEN)
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
                            king_resp = king_knights_requests(trigbee=trig, ticker_time_frame=ticker_time_frame)
                            if trig in king_resp.keys():
                                type_order = king_resp[trig]['type']
                                wave_amo = king_resp[trig]['wave_amo']
                                snap = api.get_snapshot(ticker)
                                current_price = snap.latest_trade.price
                                qty_order = int(round(wave_amo / current_price, 0))                            

                                order_id = generate_client_order_id(ticker=ticker, trig=trig)
                                
                                if type_order == 'market':
                                    order_submit = submit_order(api=api, symbol=ticker, type=type_order, qty=qty_order, side='buy', client_order_id=order_id) # buy
                                else:
                                    order_submit = submit_order(api=api, symbol=ticker, type=type_order, qty=qty_order, side='buy', client_order_id=order_id) # buy

                                order = vars(order_submit)['_raw']
                                # ensure order went through
                                if route_order_based_on_status(order_status=order['status']):
                                    order_process = process_order_submission(trig=trig, order=order, prod=prod, tablename='main_orders', ticker_time_frame=ticker_time_frame)
                                    QUEEN['command_conscience']['orders']['submitted'].append(order_process['sending_order'])
                                    QUEEN['command_conscience']['memory']['trigger_stopped'].append(order_process['trig_stop_info'])
                                    pickle_chesspiece(pickle_file=PB_Story_Pickle, data_to_store=QUEEN)
                                else:
                                    msg = ("error order not accepted", order)
                                    print(msg)
                                    logging.error(msg)
    
    return True


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
        
        return True

    submitted_orders_main(api)

    # Confirm Theme
    if len(app_theme_base) > 0:
        if len(app_theme_base) != 1:
            app_request = app_theme_base[len(app_theme_base)-1]
            print("dup theme requests, removing dups processing last")
            logging.info("dup theme requests, removing dups processing last")
            for i in range(len(app_theme_base) - 1):
                idx_order = APP_requests['theme'][i]
                APP_requests['theme'].remove(idx_order)
                PickleData(pickle_file=PB_App_Pickle, data_to_store=APP_requests)
        else:
            app_request = app_theme_base[0]
            
        if app_request['app_requests_id'] in QUEEN['queen_controls']['app_order_requests']:
            print("remove from theme section as already processed")
            APP_requests['queen_processed'].append(app_request)
            APP_requests['theme'].remove(app_request)
            PickleData(pickle_file=PB_App_Pickle, data_to_store=APP_requests)
        else:
            # print("Processing App Request")
            QUEEN['queen_controls']['theme'] = app_request['theme']
            QUEEN['queen_controls']['app_order_requests'].append(app_request['app_requests_id'])
            pickle_chesspiece(pickle_file=PB_Story_Pickle, data_to_store=QUEEN)

            APP_requests['queen_processed'].append(app_request)
            APP_requests['theme'].remove(app_request)
            PickleData(pickle_file=PB_App_Pickle, data_to_store=APP_requests)
            print("App Request Processed")
            logging.info("App Theme Request Processed")

    # >for every ticker position join in running-positions to account for total position
    # >for each running position determine to exit the position                
    all_positions = api.list_positions()
    portfolio = {i.symbol: vars(i)["_raw"] for i in all_positions}

    def running_orders_main(api):
        return True
    
    def running_close_orders_main(api):
        return True

    def validate_portfolio_with_RUNNING(ticker, run_index, run_order, portfolio):        
    
        # check if there are enough shares in portforlio IF NOT Archive RUNNING ORDER AS IT WAS SOLD ALREADY
        if ticker in portfolio.keys():
            qty_avail = int(portfolio[ticker]['qty'])
            if int(run_order["filled_qty"]) > qty_avail:
                print("CRITICAL ERROR PORTFOLIO DOES NOT HAVE QTY AVAIL TO SELL ARCHVIE RUNNING ORDER")
                logging.critical({"msg": "run order qty > then avail in portfolio, adjust to remaining"})
                QUEEN['command_conscience']['orders']['running'][run_index]["filled_qty"] = qty_avail - int(run_order["filled_qty"])
                QUEEN['command_conscience']['orders']['running'][run_index]["status_q"] = True

                # QUEEN['command_conscience']['memory']['orders_completed'].append(run_order)
                # QUEEN['command_conscience']['orders']['running'].remove(run_order)
                # trigname_stop = [item for item in QUEEN['command_conscience']['memory']['trigger_stopped'] if item['client_order_id'] == runorder_client_order_id ]
                # QUEEN['command_conscience']['memory']['trigger_stopped'].remove(trigname_stop[0])
                # PickleData(pickle_file=PB_Story_Pickle, data_to_store=QUEEN)
        else:
            print(ticker, "CRITICAL ERROR PORTFOLIO DOES NOT HAVE TICKER ARCHVIE RUNNING ORDER")
            logging.critical({'msg': f'{Ticker}{" Ticker not in Portfolio"}'})

            QUEEN['command_conscience']['memory']['orders_completed'].append(run_order)
            QUEEN['command_conscience']['orders']['running'].remove(run_order) 
            trigname_stop = [item for item in QUEEN['command_conscience']['memory']['trigger_stopped'] if item['client_order_id'] == runorder_client_order_id ]
            QUEEN['command_conscience']['memory']['trigger_stopped'].remove(trigname_stop[0])
            PickleData(pickle_file=PB_Story_Pickle, data_to_store=QUEEN)

        return True

    # if profit has achived send order to take profit
    def kning_queens_order_evaluation(run_order, order_obj, current_profit_loss):
        # all scenarios if run_order should be closed out
        runorder_client_order_id = run_order['client_order_id']
        take_profit = run_order['order_rules']['take_profit'] #  {'order_rules': order_rules, 'trigname': trig, 'order': order, 'datetime': date_mark, 'status_q': False, 'exit_order': False}                                    
        sellout = run_order['order_rules']['sellout']
        sell_qty = int(order_obj['filled_qty'])
        
        side = 'sell'
        type ='market'

        """Read App Controls and update if anything new"""
        # app_request = QUEEN['queen_controls']['orders']
        app_order_base = [i for i in APP_requests['orders']]
        c_order_ids = {idx: i for idx, i in enumerate(app_order_base) if i['client_order_id'] == runorder_client_order_id}
        if c_order_ids: # App Requests to sell client_order_id
            print("App Request Order")
            logging.info("App Request Order")
            if len(c_order_ids) != 1:
                print("error duplicate client_order_id requests, taking latest")
                logging.info("error duplicate client_order_id requests, taking latest")
                app_request = c_order_ids[len(c_order_ids)-1]
                for i in range(len(c_order_ids) - 1):
                    APP_requests['orders'].remove(i)
                    PickleData(pickle_file=PB_App_Pickle, data_to_store=APP_requests)
            else:
                app_request = c_order_ids[0]
                if app_request['app_requests_id'] in QUEEN['queen_controls']['app_order_requests']:
                    print("remove from theme section as already processed")
                    APP_requests['queen_processed'].append(app_request)
                    APP_requests['theme'].remove(app_request)
                    PickleData(pickle_file=PB_App_Pickle, data_to_store=APP_requests)
                else:
                    sell_qty = app_request['sellable_qty']
                    type = app_request['type']
                    side = app_request['side']

                    QUEEN['queen_controls']['app_order_requests'].append(app_request['app_requests_id'])
                    pickle_chesspiece(pickle_file=PB_Story_Pickle, data_to_store=QUEEN)

                    APP_requests['queen_processed'].append(app_request)
                    APP_requests['orders'].remove(app_request)
                    PickleData(pickle_file=PB_App_Pickle, data_to_store=APP_requests)
                    
                    sell_order = True

        elif take_profit <= current_profit_loss:
            sell_order = True
        
        elif abs(current_profit_loss) <= sellout:
            sell_order = True
        
        # elif the 3 wisemen pointing to sell or re-chunk profits
        
        else:
            sell_order = False
        
        if sell_order:
            return {'bee_sell': True, 'type': type, 'side': side, 'sell_qty': sell_qty}
        else:
            return {'bee_sell': False, 'run_order': run_order}


    # if its in RUNNING then its fulfilled or partially fulfilled and now its time to figure out how to close the position
    for idx, run_order in enumerate(QUEEN['command_conscience']['orders']['running']):
        cur_runorders = QUEEN['command_conscience']['orders']['running']
        all_symbol_runorders = [i for i in cur_runorders if i['symbol'] == run_order['sumbol']]
        QUEEN['command_conscience']['portfolios']
        # give to Queen portfolio status
        
        # try to close order
        runorder_ticker_time_frame = run_order['ticker_time_frame']
        runorder_client_order_id = run_order['client_order_id']
        ticker = run_order["symbol"]
        trigname = run_order['trigname']

        order_obj = check_order_status(api=api, client_order_id=runorder_client_order_id)

        # VALIDATE BEE ORDER check if there are enough shares in portforlio IF NOT Archive RUNNING ORDER AS IT WAS SOLD ALREADY
        all_positions = api.list_positions()
        portfolio = {i.symbol: vars(i)["_raw"] for i in all_positions}
        validate_portfolio_with_RUNNING(ticker=ticker, run_index=idx, run_order=run_order, portfolio=portfolio)


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
        QUEEN['command_conscience']['orders']['running'][idx]['$honey'] = float(order_obj['filled_avg_price']) * float(order_obj['filled_qty']) - current_price * float(order_obj['filled_qty'])
        
        re_eval_order = kning_queens_order_evaluation(run_order, order_obj, current_profit_loss)

        if re_eval_order['bee_sell']:
            # close out order variables
            sell_qty = re_eval_order['sell_qty'] # int(order_obj['filled_qty'])
            side = re_eval_order['side'] # 'sell'
            type = re_eval_order['type'] # 'market'

            # check to see if you have enough Qty to Sell, if NOT archive running order and log as error
            all_positions = api.list_positions()
            portfolio = {i.symbol: vars(i)["_raw"] for i in all_positions}
            
            if ticker in portfolio.keys():
                if sell_qty <= int(portfolio[ticker]['qty']):
                    sell_validation = True
                else:
                    sell_validation = False
                    print("error, do not have enough shares to sell, check reason")
            else:
                sell_validation = False
                print("error TICKER NOT in Portfolio")

            sell_client_order_id = generate_client_order_id(ticker=ticker, trig=trigname, db_root=db_root, sellside_client_order_id=True)
            send_close_order = submit_order(api=api, side=side, symbol=ticker, qty=sell_qty, type=type, client_order_id=sell_client_order_id) 
            send_close_order = vars(send_close_order)['_raw']
            if route_order_based_on_status(order_status=send_close_order['status']):
                print("Did you bring me some Honey?")
                order_process=process_order_submission(order=send_close_order, trig=trigname, exit_order_link=runorder_client_order_id, prod=prod, tablename='main_orders', ticker_time_frame=runorder_ticker_time_frame)
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



###############>>>>
###############>>>>

###############>>>>
###############>>>>
###############>>>>

###############>>>>
###############>>>>
        
# QUEEN['command_conscience']['portfolios'] = {'Jq': {'total_investment': 0, 'currnet_value': 0}}


# if '_name_' == '_main_':
# print("Buzz Buzz Where My Honey")
try:
    pollen = return_pollen()
    QUEEN = pollen.QUEEN
    QUEEN = add_key_to_chesspiecePICKLE_if_key_does_not_exist(QUEEN=QUEEN, queens_chess_piece=queens_chess_piece)

    
    if queens_chess_piece == 'queen':
        logging.info("My Queen")

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
        
        init_api_orders_start_date =(datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        init_api_orders_end_date = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        api_orders = initialize_orders(api, init_api_orders_start_date, init_api_orders_end_date)
        
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
        if queens_chess_piece.lower() == 'queen': # Rule On High
            # The story
            pollen = return_pollen()
            QUEEN = pollen.QUEEN
            # Should you operate now? I thnik the brain never sleeps ?
            
            APP_requests = ReadPickleData(pickle_file=PB_App_Pickle)
            app_order_base = [i for i in APP_requests['orders']]
            app_theme_base = [i for i in APP_requests['theme']]
            # app_processed = [i for i in APP_requests['queen_processed']]

            chart_times = {
                "1Minute_1Day": 0, "5Minute_5Day": 5, "30Minute_1Month": 18, 
                "1Hour_3Month": 48, "2Hour_6Month": 72, 
                "1Day_1Year": 250}
                        
            for ttframe_story in pollen.STORY_bee.keys():
                command_conscience(api=api, ticker_time_frame=ttframe_story, pollen=pollen)        
            
            order_management(api=api)
            
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
    pickle_chesspiece(pickle_file=PB_Story_Pickle, data_to_store=pollen.QUEEN)

#### >>>>>>>>>>>>>>>>>>> END <<<<<<<<<<<<<<<<<<###