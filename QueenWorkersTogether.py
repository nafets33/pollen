# QueenBee Workers
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
from QueenHive import init_QUEEN, init_pollen_dbs, read_queensmind, speedybee, return_timestamp_string, pollen_story, ReadPickleData, PickleData, return_api_keys, return_bars_list, refresh_account_info, return_bars, rebuild_timeframe_bars, init_index_ticker, print_line_of_error, return_index_tickers
from QueenHive import return_macd, return_VWAP, return_RSI, return_sma_slope
import argparse
import aiohttp
import asyncio
from itertools import islice

# FEAT List
# rebuild minute bar with high and lows, store current minute bar in QUEEN, reproduce every minute

# script arguments
def createParser():
    parser = argparse.ArgumentParser()
    parser.add_argument ('-qcp', default="castle")
    parser.add_argument ('-prod', default=True)
    parser.add_argument ('-windows', default=False)

    return parser

# script arguments
parser = createParser()
namespace = parser.parse_args()
queens_chess_piece = namespace.qcp # 'castle', 'knight' 'queen'
windows = namespace.windows

pd.options.mode.chained_assignment = None
est = pytz.timezone("US/Eastern")
load_dotenv()
prod = True

main_root = os.getcwd()
db_root = os.path.join(main_root, 'db')

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
# log_name = f'{"log_"}{queens_chess_piece}{".log"}'
log_file = os.path.join(log_dir, log_name)
if loglog_newfile:
    # copy log file to log dir & del current log file
    datet = datetime.datetime.now(est).strftime('%Y-%m-%d %H-%M-%S_%p')
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
    # logging.info("Welcome")

# Macd Settings
# MACD_12_26_9 = {'fast': 12, 'slow': 26, 'smooth': 9}
def init_QUEENWORKER(queens_chess_piece):

    QUEEN = { # The Queens Mind
        'command_conscience': {'memory': {'trigger_stopped': [], 'trigger_sell_stopped': [], 'orders_completed': []}, 
                                'orders': { 'requests': [],
                                            'submitted': [],
                                            'running': [],
                                            'running_close': []}
                                            }, # ONLY for the Kings Eyes
            'heartbeat': {}, # ticker info ... change name
            'kings_order_rules': {},
        # Worker Bees
        queens_chess_piece: {
        'conscience': {'STORY_bee': {},'KNIGHTSWORD': {}, 'ANGEL_bee': {}},
        'pollenstory': {}, # latest story of dataframes castle and bishop
        'pollencharts': {}, # latest chart rebuild
        'pollencharts_nectar': {}, # latest chart rebuild with indicators
        'pollenstory_info': {}, # Misc Info,
        'client': {},
        'heartbeat': {'cycle_time': deque([], 89)},
        'last_modified' : datetime.datetime.now(est),
        'triggerBee_frequency' : {},
        }
    }

    return QUEEN


QUEEN = init_QUEENWORKER(queens_chess_piece)

if queens_chess_piece.lower() not in ['castle', 'knight', 'bishop', 'workerbee']:
    print("wrong chess move")
    sys.exit()



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
# trading_days = api.get_calendar()
# trading_days_df = pd.DataFrame([day._raw for day in trading_days])

current_date = datetime.datetime.now(est).strftime("%Y-%m-%d")
trading_days = api.get_calendar()
trading_days_df = pd.DataFrame([day._raw for day in trading_days])
trading_days_df['date'] = pd.to_datetime(trading_days_df['date'])


current_day = datetime.datetime.now(est).day
current_month = datetime.datetime.now(est).month
current_year = datetime.datetime.now(est).year

# misc
exclude_conditions = [
    'B','W','4','7','9','C','G','H','I','M','N',
    'P','Q','R','T','V','Z'
] # 'U'

"""# Main Arguments """

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

    """ Return Index Charts & Data for All Tickers Wanted"""
    """ Return Tickers of SP500 & Nasdaq / Other Tickers"""
    # s = datetime.datetime.now()
    all_alpaca_tickers = api.list_assets()
    alpaca_symbols_dict = {}
    for n, v in enumerate(all_alpaca_tickers):
        if all_alpaca_tickers[n].status == 'active':
            alpaca_symbols_dict[all_alpaca_tickers[n].symbol] = vars(all_alpaca_tickers[n])

    symbol_shortable_list = []
    t = []
    for ticker, v in alpaca_symbols_dict.items():
        if v['_raw']['shortable'] == True:
            symbol_shortable_list.append(ticker)
        if v['_raw']['easy_to_borrow'] == True:
            t.append(ticker)

    # alpaca_symbols_dict[list(alpaca_symbols_dict.keys())[100]]
    # e = datetime.datetime.now()
    # print(e-s) # 0:00:00.490031

    market_exchanges_tickers = defaultdict(list)

    for k, v in alpaca_symbols_dict.items():
        market_exchanges_tickers[v['_raw']['exchange']].append(k)
    # market_exchanges = ['OTC', 'NASDAQ', 'NYSE', 'ARCA', 'AMEX', 'BATS']


    main_index_dict = index_ticker_db[0]
    main_symbols_full_list = index_ticker_db[1]
    not_avail_in_alpaca =[i for i in main_symbols_full_list if i not in alpaca_symbols_dict]
    main_symbols_full_list = [i for i in main_symbols_full_list if i in alpaca_symbols_dict]

    index_ticker_db = return_index_tickers(index_dir=os.path.join(db_root, 'index_tickers'), ext='.csv')

    """ Return Index Charts & Data for All Tickers Wanted"""
    """ Return Tickers of SP500 & Nasdaq / Other Tickers"""    



def close_worker(queens_chess_piece, s):
    date = datetime.datetime.now(est)
    date = date.replace(hour=16, minute=1)
    if s >= date:
        logging.info("Happy Bee Day End")
        print("Great Job! See you Tomorrow")
        if queens_chess_piece.lower() == 'castle':
            # make os copy
            save_files = ['queen.pkl', 'queen_sandbox.pkl']
            for fname in save_files:
                src = os.path.join(db_root, fname)
                dst = os.path.join(os.path.join(os.path.join(db_root, 'logs'), 'logs'), 'queens')
                dst_ = os.path.join(dst, fname)
                shutil.copy(src, dst_)
            print("Queen Bee Saved")
        
        sys.exit()


def return_getbars_WithIndicators(bars_data, MACD):
    # time = '1Minute' #TEST
    # symbol = 'SPY' #TEST
    # ndays = 1
    # bars_data = return_bars(symbol, time, ndays, trading_days_df=trading_days_df)

    try:
        # s = datetime.datetime.now(est) #TEST
        bars_data['vwap_original'] = bars_data['vwap']
        # del mk_hrs_data['vwap']
        df_vwap = return_VWAP(bars_data)
        # df_vwap = vwap(bars_data)

        df_vwap_rsi = return_RSI(df=df_vwap, length=14)
        # append_MACD(df_vwap_rsi_macd, fast=MACD['fast'], slow=MACD['slow'])
        df_vwap_rsi_macd = return_macd(df_main=df_vwap_rsi, fast=MACD['fast'], slow=MACD['slow'], smooth=MACD['smooth'])
        df_vwap_rsi_macd_smaslope = return_sma_slope(df=df_vwap_rsi_macd, time_measure_list=[3, 6, 23, 33], y_list=['close', 'macd', 'hist'])
        # e = datetime.datetime.now(est)
        # print(str((e - s)) + ": " + datetime.datetime.now().strftime("%A, %d. %B %Y %I:%M%p"))
        # 0:00:00.198920: Monday, 21. March 2022 03:02PM 2 days 1 Minute
        return [True, df_vwap_rsi_macd_smaslope]
    except Exception as e:
        print("log error", print_line_of_error())
        return [False, e, print_line_of_error()]


def Return_Init_ChartData(ticker_list, chart_times): #Iniaite Ticker Charts with Indicator Data
    # ticker_list = ['SPY', 'QQQ']
    # chart_times = {
    #     "1Minute_1Day": 0, "5Minute_5Day": 5, "30Minute_1Month": 18, 
    #     "1Hour_3Month": 48, "2Hour_6Month": 72, 
    #     "1Day_1Year": 250}
    try:
        msg = (ticker_list, chart_times)
        logging.info(msg)
        print(msg)

        error_dict = {}
        s = datetime.datetime.now(est)
        dfs_index_tickers = {}
        bars = return_bars_list(ticker_list, chart_times)
        if bars[0] == False:
            print("kill")        
        if bars[1]: # rebuild and split back to ticker_time with market hours only
            bars_dfs = bars[1]
            for timeframe, df in bars_dfs.items():
                time_frame=timeframe.split("_")[0] # '1day_1year'
                if '1day' in time_frame.lower():
                    for ticker in ticker_list:
                        df_return = df[df['symbol']==ticker].copy()
                        dfs_index_tickers[f'{ticker}{"_"}{timeframe}'] = df_return
                else:
                    df = df.set_index('timestamp_est')
                    market_hours_data = df.between_time('9:30', '16:00')
                    market_hours_data = market_hours_data.reset_index()
                    for ticker in ticker_list:
                        df_return = market_hours_data[market_hours_data['symbol']==ticker].copy()
                        dfs_index_tickers[f'{ticker}{"_"}{timeframe}'] = df_return
        
        e = datetime.datetime.now(est)
        msg = {'function':'Return Init ChartData',  'func_timeit': str((e - s)), 'datetime': datetime.datetime.now(est).strftime('%Y-%m-%d_%H:%M:%S_%p')}
        print(msg)
        # dfs_index_tickers['SPY_5Minute']
        return {'init_charts': dfs_index_tickers, 'errors': error_dict}
    except Exception as e:
        print("eeeeeror", e, print_line_of_error())
        ipdb.set_trace()

def Return_Bars_LatestDayRebuild(ticker_time): #Iniaite Ticker Charts with Indicator Data
    # IMPROVEMENT: use Return_bars_list for Return_Bars_LatestDayRebuild
    # ticker_time = "SPY_1Minute_1Day"

    ticker, timeframe, days = ticker_time.split("_")
    error_dict = {}
    s = datetime.datetime.now(est)
    dfs_index_tickers = {}
    try:
        # return market hours data from bars
        bars_data = return_bars(symbol=ticker, timeframe=timeframe, ndays=0, trading_days_df=trading_days_df) # return [True, symbol_data, market_hours_data, after_hours_data]
        df_bars_data = bars_data[2] # mkhrs if in minutes
        # df_bars_data = df_bars_data.reset_index()
        if bars_data[0] == False:
            error_dict["NoData"] = bars_data[1] # symbol already included in value
        else:
            dfs_index_tickers[ticker_time] = df_bars_data
    except Exception as e:
        print(ticker_time, e)
    
    e = datetime.datetime.now(est)
    msg = {'function':'Return_Bars_LatestDayRebuild',  'func_timeit': str((e - s)), 'datetime': datetime.datetime.now(est).strftime('%Y-%m-%d_%H:%M:%S_%p')}
    # print(msg)
    # dfs_index_tickers['SPY_5Minute']
    return [dfs_index_tickers, error_dict, msg]


def Return_Snapshots_Rebuild(df_tickers_data, init=False): # from snapshots & consider using day.min.chart to rebuild other timeframes
    ticker_list = list([set(j.split("_")[0] for j in df_tickers_data.keys())][0]) #> get list of tickers

    snapshots = api.get_snapshots(ticker_list)

    for ticker in snapshots.keys(): # replace snapshot if in exclude_conditions
        c = 0
        while True:
            conditions = snapshots[ticker].latest_trade.conditions
            # print(conditions)
            invalid = [c for c in conditions if c in exclude_conditions]
            if len(invalid) == 0 or c > 10:
                break
            else:
                print("invalid trade-condition pull snapshot")
                snapshot = api.get_snapshot(ticker) # return_last_quote from snapshot
                snapshots[ticker] = snapshot
                c+=1

    float_cols = ['close', 'high', 'open', 'low', 'vwap']
    int_cols = ['volume', 'trade_count']
    main_return_dict = {}
    
    # min_bars_dict = rebuild_timeframe_bars(ticker_list)
    # if min_bars_dict['resp'] == False:
    #     print("Min Bars Error", min_bars_dict)
    #     min_bars_dict = {k:{} for k in ticker_list}
    # else:
    #     min_bars_dict = min_bars_dict['resp']
    # min_bars_dict = {k:{} for k in ticker_list} # REBUILDING MIN BARS NEEDS IMPROVEMENT BEFORE SOME MAY FAIL TO RETURN

    def response_returned(ticker_list):
        return_dict = {}
        for ticker in ticker_list:
            dl = {
            'close': snapshots[ticker].daily_bar.close,
            'high': snapshots[ticker].daily_bar.high,
            'low': snapshots[ticker].daily_bar.low,
            'timestamp_est': snapshots[ticker].daily_bar.timestamp,
            'open': snapshots[ticker].daily_bar.open,
            'volume': snapshots[ticker].daily_bar.volume,
            'trade_count': snapshots[ticker].daily_bar.trade_count,
            'vwap': snapshots[ticker].daily_bar.vwap
            }
            df_daily = pd.Series(dl).to_frame().T  # reshape dataframe
            for i in float_cols:
                df_daily[i] = df_daily[i].apply(lambda x: float(x))
            for i in int_cols:
                df_daily[i] = df_daily[i].apply(lambda x: int(x))
            # df_daily = df_daily.rename(columns={'timestamp': 'timestamp_est'})
            
            return_dict[ticker + "_day"] = df_daily

            d = {
                'close': snapshots[ticker].latest_trade.price,
                'high': snapshots[ticker].latest_trade.price,
                'low': snapshots[ticker].latest_trade.price,
                'timestamp_est': snapshots[ticker].latest_trade.timestamp,
                'open': snapshots[ticker].latest_trade.price,
                'volume': snapshots[ticker].minute_bar.volume,
                'trade_count': snapshots[ticker].minute_bar.trade_count,
                'vwap': snapshots[ticker].minute_bar.vwap
                }
            df_minute = pd.Series(d).to_frame().T
            for i in float_cols:
                df_minute[i] = df_minute[i].apply(lambda x: float(x))
            for i in int_cols:
                df_minute[i] = df_minute[i].apply(lambda x: int(x))
            # df_minute = df_minute.rename(columns={'timestamp': 'timestamp_est'})

            return_dict[ticker + "_minute"] = df_minute
        
        return return_dict
    
 
    snapshot_ticker_data = response_returned(ticker_list)
    
    for ticker_time, df in df_tickers_data.items():
        symbol_snapshots = {k:v for (k,v) in snapshot_ticker_data.items() if k.split("_")[0] == ticker_time.split("_")[0]}
        symbol, timeframe, days = ticker_time.split("_")
        if "day" in timeframe.lower():
            df_day_snapshot = symbol_snapshots[f'{symbol}{"_day"}'] # stapshot df
            df_day_snapshot['symbol'] = symbol
            df = df.head(-1) # drop last row which has current day / added minute
            df_rebuild = pd.concat([df, df_day_snapshot], join='outer', axis=0).reset_index(drop=True) # concat minute
            main_return_dict[ticker_time] = df_rebuild
        else:
            df_snapshot = symbol_snapshots[f'{symbol}{"_minute"}'] # stapshot df
            df_snapshot['symbol'] = symbol
            if init:
                df_rebuild = pd.concat([df, df_snapshot], join='outer', axis=0).reset_index(drop=True) # concat minute
                main_return_dict[ticker_time] = df_rebuild
            else:
                df = df.head(-1) # drop last row which has current day
                df_rebuild = pd.concat([df, df_snapshot], join='outer', axis=0).reset_index(drop=True) # concat minute
                main_return_dict[ticker_time] = df_rebuild

    return main_return_dict


def ReInitiate_Charts_Past_Their_Time(df_tickers_data): # re-initiate for i timeframe 
    # IMPROVEMENT: use Return_bars_list for Return_Bars_LatestDayRebuild
    return_dict = {}
    rebuild_confirmation = {}

    def tag_current_day(timestamp):
        if timestamp.day == current_day and timestamp.month == current_month and timestamp.year == current_year:
            return 'tag'
        else:
            return '0'

    for ticker_time, df in df_tickers_data.items():
        ticker, timeframe, days = ticker_time.split("_")
        last = df['timestamp_est'].iloc[-2]
        now = datetime.datetime.now(est)
        timedelta_minutes = (now - last).seconds / 60
        now_day = now.day
        last_day = last.day
        if now_day != last_day:
            return_dict[ticker_time] = df
            continue

        if "1minute" == timeframe.lower():
            if timedelta_minutes > 2:
                dfn = Return_Bars_LatestDayRebuild(ticker_time)
                if len(dfn[1]) == 0:
                    df_latest = dfn[0][ticker_time]
                    df['timetag'] = df['timestamp_est'].apply(lambda x: tag_current_day(x))
                    df_replace = df[df['timetag']!= 'tag'].copy()
                    del df_replace['timetag']
                    df_return = pd.concat([df_replace, df_latest], join='outer', axis=0).reset_index(drop=True)
                    df_return_me = pd.concat([df_return, df_return.tail(1)], join='outer', axis=0).reset_index(drop=True) # add dup last row to act as snapshot
                    return_dict[ticker_time] = df_return_me
                    rebuild_confirmation[ticker_time] = "rebuild"
            else:
                return_dict[ticker_time] = df

        elif "5minute" == timeframe.lower():
            if timedelta_minutes > 6:
                dfn = Return_Bars_LatestDayRebuild(ticker_time)
                if len(dfn[1]) == 0:
                    df_latest = dfn[0][ticker_time]
                    df['timetag'] = df['timestamp_est'].apply(lambda x: tag_current_day(x))
                    df_replace = df[df['timetag']!= 'tag'].copy()
                    del df_replace['timetag']
                    df_return = pd.concat([df_replace, df_latest], join='outer', axis=0).reset_index(drop=True)
                    df_return_me = pd.concat([df_return, df_return.tail(1)], join='outer', axis=0).reset_index(drop=True) # add dup last row to act as snapshot
                    return_dict[ticker_time] = df_return_me
                    rebuild_confirmation[ticker_time] = "rebuild"
            else:
                return_dict[ticker_time] = df
        
        elif "30minute" == timeframe.lower():
            if timedelta_minutes > 31:
                dfn = Return_Bars_LatestDayRebuild(ticker_time)
                if len(dfn[1]) == 0:
                    df_latest = dfn[0][ticker_time]

                    df['timetag'] = df['timestamp_est'].apply(lambda x: tag_current_day(x))
                    df_replace = df[df['timetag']!= 'tag'].copy()
                    del df_replace['timetag']
                    df_return = pd.concat([df_replace, df_latest], join='outer', axis=0).reset_index(drop=True)
                    df_return_me = pd.concat([df_return, df_return.tail(1)], join='outer', axis=0).reset_index(drop=True) # add dup last row to act as snapshot
                    return_dict[ticker_time] = df_return_me
                    rebuild_confirmation[ticker_time] = "rebuild"
            else:
                return_dict[ticker_time] = df

        elif "1hour" == timeframe.lower():
            if timedelta_minutes > 61:
                dfn = Return_Bars_LatestDayRebuild(ticker_time)
                if len(dfn[1]) == 0:
                    df_latest = dfn[0][ticker_time]
                    df['timetag'] = df['timestamp_est'].apply(lambda x: tag_current_day(x))
                    df_replace = df[df['timetag']!= 'tag'].copy()
                    del df_replace['timetag']
                    df_return = pd.concat([df_replace, df_latest], join='outer', axis=0).reset_index(drop=True)
                    df_return_me = pd.concat([df_return, df_return.tail(1)], join='outer', axis=0).reset_index(drop=True) # add dup last row to act as snapshot
                    return_dict[ticker_time] = df_return_me
                    rebuild_confirmation[ticker_time] = "rebuild"
            else:
                return_dict[ticker_time] = df

        elif "2hour" == timeframe.lower():
            if timedelta_minutes > 121:
                dfn = Return_Bars_LatestDayRebuild(ticker_time)
                if len(dfn[1]) == 0:
                    df_latest = dfn[0][ticker_time]
                    df['timetag'] = df['timestamp_est'].apply(lambda x: tag_current_day(x))
                    df_replace = df[df['timetag']!= 'tag'].copy()
                    del df_replace['timetag']
                    df_return = pd.concat([df_replace, df_latest], join='outer', axis=0).reset_index(drop=True)
                    df_return_me = pd.concat([df_return, df_return.tail(1)], join='outer', axis=0).reset_index(drop=True) # add dup last row to act as snapshot
                    return_dict[ticker_time] = df_return_me
                    rebuild_confirmation[ticker_time] = "rebuild"
            else:
                return_dict[ticker_time] = df

        else:
            return_dict[ticker_time] = df
    
    # add back in snapshot init
    return {"ticker_time": return_dict, "rebuild_confirmation": rebuild_confirmation}


def pollen_hunt(df_tickers_data, MACD):
    # Check to see if any charts need to be Recreate as times lapsed
    df_tickers_data_rebuilt = ReInitiate_Charts_Past_Their_Time(df_tickers_data)
    if len(df_tickers_data_rebuilt['rebuild_confirmation'].keys()) > 0:
        print(df_tickers_data_rebuilt['rebuild_confirmation'].keys())
        print(datetime.datetime.now(est).strftime("%H:%M-%S"))
    
    # re-add snapshot
    df_tickers_data_rebuilt = Return_Snapshots_Rebuild(df_tickers_data=df_tickers_data_rebuilt['ticker_time'])
    
    main_rebuild_dict = {} ##> only override current dict if memory becomes issues!
    chart_rebuild_dict = {}
    for ticker_time, bars_data in df_tickers_data_rebuilt.items():
        chart_rebuild_dict[ticker_time] = bars_data
        df_data_new = return_getbars_WithIndicators(bars_data=bars_data, MACD=MACD)
        if df_data_new[0] == True:
            main_rebuild_dict[ticker_time] = df_data_new[1]
        else:
            print("error", ticker_time)

    return {'pollencharts_nectar': main_rebuild_dict, 'pollencharts': chart_rebuild_dict}


""" Initiate your Charts with Indicators """
def initiate_ttframe_charts(QUEEN, queens_chess_piece, master_tickers, star_times, MACD_settings):
    s_mainbeetime = datetime.datetime.now(est)
    res = Return_Init_ChartData(ticker_list=master_tickers, chart_times=star_times)
    errors = res['errors']
    if errors:
        msg = ("Return_Init_ChartData Failed", "--", errors)
        print(msg)
        logging.critical(msg)
        sys.exit()
    df_tickers_data_init = res['init_charts']
    
    """ add snapshot to initial chartdata -1 """
    df_tickers_data = Return_Snapshots_Rebuild(df_tickers_data=df_tickers_data_init, init=True)
    
    """ give it all to the QUEEN put directkly in function """
    pollen = pollen_hunt(df_tickers_data=df_tickers_data, MACD=MACD_settings)
    QUEEN[queens_chess_piece]['pollencharts'] = pollen['pollencharts']
    QUEEN[queens_chess_piece]['pollencharts_nectar'] = pollen['pollencharts_nectar']

    """# mark final times and return values"""
    e_mainbeetime = datetime.datetime.now(est)
    msg = {queens_chess_piece:'initiate ttframe charts',  'block_timeit': str((e_mainbeetime - s_mainbeetime)), 'datetime': datetime.datetime.now(est).strftime('%Y-%m-%d_%H:%M:%S_%p')}
    logging.info(msg)
    print(msg)    
    return QUEEN

def chunk(it, size):
    it = iter(it)
    return iter(lambda: tuple(islice(it, size)), ())


print(
"""
We all shall prosper through the depths of our connected hearts,
Not all will share my world,
So I put forth my best mind of virtue and goodness, 
Always Bee Better
"""
)

# if '_name_' == '_main_':
# print("Buzz Buzz Where My Honey")
if queens_chess_piece == 'queen':
    logging.info("My Queen")
else:
    logging.info("Buzz Buzz Where My Honey")

# init files needed
# PB_Story_Pickle = os.path.join(db_root, f'{queens_chess_piece}{".pkl"}')

init_pollen = init_pollen_dbs(db_root=db_root, api=api, prod=prod, queens_chess_piece=queens_chess_piece)
PB_QUEEN_Pickle = init_pollen['PB_QUEEN_Pickle']
# PB_App_Pickle = init_pollen['PB_App_Pickle']

if os.path.exists(PB_QUEEN_Pickle) == False:
    print("WorkerBee Needs a Queen")
    sys.exit()

# Pollen QUEEN
if prod:
    QUEENBEE = ReadPickleData(pickle_file=os.path.join(db_root, 'queen.pkl'))
else:
    QUEENBEE = ReadPickleData(pickle_file=os.path.join(db_root, 'queen_sandbox.pkl'))

QUEENBEE['source'] = PB_QUEEN_Pickle
MACD_12_26_9 = QUEENBEE['queen_controls']['MACD_fast_slow_smooth']
# master_tickers = QUEENBEE['workerbees'][queens_chess_piece]['tickers']
MACD_settings = QUEENBEE['workerbees'][queens_chess_piece]['MACD_fast_slow_smooth']
star_times = QUEENBEE['workerbees'][queens_chess_piece]['stars']

if windows:
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy()) # needed to work on Windows

def ticker_star_hunter_bee(WORKERBEE_queens, QUEENBEE, queens_chess_piece):
    s = datetime.datetime.now(est)
    
    QUEEN = WORKERBEE_queens[queens_chess_piece]
    # QUEEN = qcp_QUEEN
    PB_Story_Pickle = os.path.join(db_root, f'{queens_chess_piece}{".pkl"}')
    MACD_12_26_9 = QUEENBEE['queen_controls']['MACD_fast_slow_smooth']
    master_tickers = QUEENBEE['workerbees'][queens_chess_piece]['tickers']
    # MACD_settings = QUEENBEE['workerbees'][queens_chess_piece]['MACD_fast_slow_smooth']
    # star_times = QUEENBEE['workerbees'][queens_chess_piece]['stars']


    close_worker(queens_chess_piece=queens_chess_piece, s=s)

    # main 
    pollen = pollen_hunt(df_tickers_data=QUEEN[queens_chess_piece]['pollencharts'], MACD=MACD_12_26_9)
    QUEEN[queens_chess_piece]['pollencharts'] = pollen['pollencharts']
    QUEEN[queens_chess_piece]['pollencharts_nectar'] = pollen['pollencharts_nectar']
    
    pollens_honey = pollen_story(pollen_nectar=QUEEN[queens_chess_piece]['pollencharts_nectar'], WORKER_QUEEN=QUEENBEE)
    ANGEL_bee = pollens_honey['conscience']['ANGEL_bee']
    knights_sight_word = pollens_honey['conscience']['KNIGHTSWORD']
    STORY_bee = pollens_honey['conscience']['STORY_bee']
    betty_bee = pollens_honey['betty_bee']
    PickleData(pickle_file=os.path.join(db_root, 'betty_bee.pkl'), data_to_store=betty_bee)

    # for each star append last macd state
    for ticker_time_frame, i in STORY_bee.items():
        speed_gauges[ticker_time_frame]['macd_gauge'].append(i['story']['macd_state'])
        speed_gauges[ticker_time_frame]['price_gauge'].append(i['story']['last_close_price'])
        STORY_bee[ticker_time_frame]['story']['macd_gauge'] = speed_gauges[ticker_time_frame]['macd_gauge']
        STORY_bee[ticker_time_frame]['story']['price_gauge'] = speed_gauges[ticker_time_frame]['price_gauge']

    
    SPEEDY_bee = speed_gauges

    # add all charts
    QUEEN[queens_chess_piece]['pollenstory'] = pollens_honey['pollen_story']

    # populate conscience
    QUEEN[queens_chess_piece]['conscience']['ANGEL_bee'] = ANGEL_bee
    QUEEN[queens_chess_piece]['conscience']['KNIGHTSWORD'] = knights_sight_word
    QUEEN[queens_chess_piece]['conscience']['STORY_bee'] = STORY_bee
    QUEEN[queens_chess_piece]['conscience']['SPEEDY_bee'] = SPEEDY_bee

    
    PickleData(pickle_file=PB_Story_Pickle, data_to_store=QUEEN)

    return True


def qcp_QUEENWorker__pollenstory(qcp_s, QUEENBEE, WORKERBEE_queens):
    try:
        s = datetime.datetime.now(est)
        async def get_changelog(session, qcp):
            async with session:
                try:
                    ticker_star_hunter_bee(WORKERBEE_queens=WORKERBEE_queens, QUEENBEE=QUEENBEE, queens_chess_piece=qcp)
                    return {qcp: ''}
                except Exception as e:
                    print(e, qcp)
                    logging.error((str(qcp), str(e)))
                    return {qcp: e}
                    
        async def main(qcp_s):

            async with aiohttp.ClientSession() as session:
                return_list = []
                tasks = []
                for qcp in qcp_s:
                    print(qcp)
                    tasks.append(asyncio.ensure_future(get_changelog(session, qcp)))
                original_pokemon = await asyncio.gather(*tasks)
                for pokemon in original_pokemon:
                    return_list.append(pokemon)
                return return_list

        x = asyncio.run(main(qcp_s))
        e = datetime.datetime.now(est)
        # print("--- %s seconds ---" % (e - s))
        return x
    except Exception as e:
        print("qtf", e, print_line_of_error())



try:

    master_tickers = []
    queens_chess_pieces = [] 
    for qcp, qcp_vars in QUEENBEE['workerbees'].items():
        for ticker in qcp_vars['tickers']:
            if qcp in 'castle' or qcp in 'bishop':
                master_tickers.append(ticker)
                queens_chess_pieces.append(qcp)
    queens_chess_pieces = list(set(queens_chess_pieces))
    


    # initiate_ttframe_charts(queens_chess_piece=queens_chess_piece, master_tickers=master_tickers, star_times=star_times, MACD_settings=MACD_settings) # only Initiates if Castle or Bishop
    WORKERBEE_queens = {i: init_QUEENWORKER(i) for i in queens_chess_pieces}
    for qcp_worker in WORKERBEE_queens.keys():
        WORKERBEE_queens[qcp_worker] = initiate_ttframe_charts(QUEEN=WORKERBEE_queens[qcp_worker], queens_chess_piece=qcp_worker, master_tickers=master_tickers, star_times=star_times, MACD_settings=MACD_settings) # only Initiates if Castle or Bishop
    
    workerbee_run_times = []
    speed_gauges = {
        f'{tic}{"_"}{star_}': {'macd_gauge': deque([], 89), 'price_gauge': deque([], 89)}
        for tic in master_tickers for star_ in star_times.keys()}

    while True:
        qcp_QUEENWorker__pollenstory(qcp_s=WORKERBEE_queens.keys(), QUEENBEE=QUEENBEE, WORKERBEE_queens=WORKERBEE_queens)

except Exception as errbuz:
    print(errbuz)
    erline = print_line_of_error()
    log_msg = {'type': 'ProgramCrash', 'lineerror': erline}
    print(log_msg)
    logging.critical(log_msg)
    ipdb.set_trace()

#### >>>>>>>>>>>>>>>>>>> END <<<<<<<<<<<<<<<<<<###
