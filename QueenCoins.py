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
from collections import defaultdict, deque
import ipdb
import tempfile
import shutil
# from scipy.stats import linregress
from scipy import stats
import hashlib
import json
from QueenHiveCoin import speedybee,  return_bars_list, return_bars
from QueenHive import pollen_story, init_pollen_dbs, ReadPickleData, return_api_keys, PickleData, return_macd, return_VWAP, return_RSI, return_sma_slope, print_line_of_error

client_symbols_castle = ['BTCUSD', 'ETHUSD']

# script arguments
# queens_chess_piece = sys.argv[1] # 'castle', 'knight' 'queen'
queens_chess_piece = 'castle_coin'
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


# Macd Settings
MACD_12_26_9 = {'fast': 12, 'slow': 26, 'smooth': 9}
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

if queens_chess_piece.lower() not in ['castle_coin']:
    print("wrong chess move")
    sys.exit()


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
current_day = datetime.datetime.now().day
current_month = datetime.datetime.now().month
current_year = datetime.datetime.now().year


####<>///<>///<>///<>///<>/// ALL FUNCTIONS NECTOR ####<>///<>///<>///<>///<>///
### BARS
def return_bars(symbol, timeframe, ndays, exchange, sdate_input=False, edate_input=False):
    try:
        s = datetime.datetime.now()
        error_dict = {}
        # ndays = 0 # today 1=yesterday...  # TEST
        # timeframe = "1Minute" #"1Day" # "1Min"  "5Minute" # TEST
        # symbol = 'BTCUSD'  # TEST

        try:
            # Fetch bars for prior ndays and then add on today
            # s_fetch = datetime.datetime.now()
            if edate_input != False:
                end_date = edate_input
            else:
                end_date = datetime.datetime.now().strftime("%Y-%m-%d")
            
            if sdate_input != False:
                start_date = sdate_input
            else:
                if ndays == 0:
                    start_date = datetime.datetime.now().strftime("%Y-%m-%d")
                else:
                    start_date = (datetime.datetime.now() - datetime.timedelta(days=ndays)).strftime("%Y-%m-%d") # get yesterdays trades as well

            # start_date = (datetime.datetime.now() - datetime.timedelta(days=ndays)).strftime("%Y-%m-%d") # get yesterdays trades as well
            symbol_data = api.get_crypto_bars(symbol, timeframe=timeframe,
                                        start=start_date,
                                        end=end_date, 
                                        exchanges=exchange).df

            # e_fetch = datetime.datetime.now()
            # print('symbol fetch', str((e_fetch - s_fetch)) + ": " + datetime.datetime.now().strftime('%Y-%m-%d %H:%M'))
            if len(symbol_data) == 0:
                error_dict[symbol] = {'msg': 'no data returned', 'time': time}
                return [False, error_dict]
        except Exception as e:
            # print(" log info")
            error_dict[symbol] = e   

        # set index to EST time
        symbol_data['index_timestamp'] = symbol_data.index
        symbol_data['timestamp_est'] = symbol_data['index_timestamp'].apply(lambda x: x.astimezone(est))
        del symbol_data['index_timestamp']
        symbol_data = symbol_data.reset_index()
        symbol_data['symbol'] = symbol       

        e = datetime.datetime.now()
        # print(str((e - s)) + ": " + datetime.datetime.now().strftime('%Y-%m-%d %H:%M'))
        # 0:00:00.310582: 2022-03-21 14:44 to return day 0
        # 0:00:00.497821: 2022-03-21 14:46 to return 5 days
        return {'resp': True, "df": symbol_data}
    # handle error
    except Exception as e:
        print("sending email of error", e)
# r = return_bars(symbol='BTCUSD', timeframe='1Minute', ndays=0, exchange="CBSE")

def return_bars_list(ticker_list, chart_times, exchange):
    try:
        s = datetime.datetime.now()
        # ticker_list = ['BTCUSD', 'ETHUSD']
        # chart_times = {
        #     "1Minute_1Day": 0, "5Minute_5Day": 5, "30Minute_1Month": 18, 
        #     "1Hour_3Month": 48, "2Hour_6Month": 72, 
        #     "1Day_1Year": 250
        #     }
        return_dict = {}
        error_dict = {}

        try:
            for charttime, ndays in chart_times.items():
                timeframe=charttime.split("_")[0] # '1Minute_1Day'
                # if timeframe.lower() == '1minute':
                    # start_date = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y-%m-%d") # get yesterdays trades as well
                # else:
                #     start_date = datetime.datetime.now().strftime("%Y-%m-%d")
                # start_date = trading_days_df.query('date < @current_day').tail(ndays).head(1).date
                start_date = (datetime.datetime.now() - datetime.timedelta(days=ndays)).strftime("%Y-%m-%d") # get yesterdays trades as well

                end_date = datetime.datetime.now().strftime("%Y-%m-%d")
                symbol_data = api.get_crypto_bars(ticker_list, timeframe=timeframe,
                                            start=start_date,
                                            end=end_date,
                                            exchanges=exchange).df
                
                # set index to EST time
                symbol_data['index_timestamp'] = symbol_data.index
                symbol_data['timestamp_est'] = symbol_data['index_timestamp'].apply(lambda x: x.astimezone(est))
                del symbol_data['index_timestamp']
                # symbol_data['timestamp'] = symbol_data['timestamp_est']
                symbol_data = symbol_data.reset_index(drop=True)
                # symbol_data = symbol_data.set_index('timestamp')
                # del symbol_data['timestamp']
                # symbol_data['timestamp_est'] = symbol_data.index
                return_dict[charttime] = symbol_data

            # e_fetch = datetime.datetime.now()
            # print('symbol fetch', str((e_fetch - s_fetch)) + ": " + datetime.datetime.now().strftime('%Y-%m-%d %H:%M'))
            if len(symbol_data) == 0:
                error_dict[ticker_list] = {'msg': 'no data returned', 'time': time}
                return [False, error_dict]
        except Exception as e:
            # print(" log info")
            error_dict[ticker_list] = e      

        e = datetime.datetime.now()
        # print(str((e - s)) + ": " + datetime.datetime.now().strftime('%Y-%m-%d %H:%M'))
        # 0:00:00.310582: 2022-03-21 14:44 to return day 0
        # 0:00:00.497821: 2022-03-21 14:46 to return 5 days
        return {'resp': True, 'return': return_dict}
    # handle error
    except Exception as e:
        print("sending email of error", e)
        return [False, e]
# r = return_bars_list(ticker_list, chart_times)


def return_getbars_WithIndicators(bars_data, MACD):
    # time = '1Minute' #TEST
    # symbol = 'SPY' #TEST
    # ndays = 1
    # bars_data = return_bars(symbol, time, ndays, trading_days_df=trading_days_df)

    try:
        s = datetime.datetime.now() #TEST
        bars_data['vwap_original'] = bars_data['vwap']
        # del mk_hrs_data['vwap']
        df_vwap = return_VWAP(bars_data)
        # df_vwap = vwap(bars_data)

        df_vwap_rsi = return_RSI(df=df_vwap, length=14)
        # append_MACD(df_vwap_rsi_macd, fast=MACD['fast'], slow=MACD['slow'])
        df_vwap_rsi_macd = return_macd(df_main=df_vwap_rsi, fast=MACD['fast'], slow=MACD['slow'], smooth=MACD['smooth'])
        df_vwap_rsi_macd_smaslope = return_sma_slope(df=df_vwap_rsi_macd, time_measure_list=[3, 6, 23, 33], y_list=['close', 'macd', 'hist'])
        e = datetime.datetime.now()
        # print(str((e - s)) + ": " + datetime.datetime.now().strftime("%A, %d. %B %Y %I:%M%p"))
        # 0:00:00.198920: Monday, 21. March 2022 03:02PM 2 days 1 Minute
        return [True, df_vwap_rsi_macd_smaslope]
    except Exception as e:
        print("log error", print_line_of_error())
        return [False, e, print_line_of_error()]


def Return_Init_ChartData(ticker_list, chart_times): #Iniaite Ticker Charts with Indicator Data
    # ticker_list = ['BTCUSD', 'ETHUSD']
    # chart_times = {
    #     "1Minute_1Day": 0, "5Minute_5Day": 5, "30Minute_1Month": 18, 
    #     "1Hour_3Month": 48, "2Hour_6Month": 72, 
    #     "1Day_1Year": 250}
    msg = (ticker_list, chart_times)
    logging.info(msg)
    print(msg)

    error_dict = {}
    s = datetime.datetime.now()
    dfs_index_tickers = {}
    bars = return_bars_list(ticker_list, chart_times, exchange='CBSE')
    if bars['resp']: # rebuild and split back to ticker_time with market hours only
        bars_dfs = bars['return']
        for timeframe, df in bars_dfs.items():
            time_frame=timeframe.split("_")[0] # '1day_1year'
            if '1day' in time_frame.lower():
                for ticker in ticker_list:
                    df_return = df[df['symbol']==ticker].copy()
                    dfs_index_tickers[f'{ticker}{"_"}{timeframe}'] = df_return
            else:
                # df = df.set_index('timestamp_est')
                # market_hours_data = df.between_time('9:30', '16:00')
                # market_hours_data = market_hours_data.reset_index()
                market_hours_data = df
                # print(time_frame, df.iloc[-1][['timestamp_est']])
                for ticker in ticker_list:
                    df_return = market_hours_data[market_hours_data['symbol']==ticker].copy()
                    dfs_index_tickers[f'{ticker}{"_"}{timeframe}'] = df_return
    
    e = datetime.datetime.now()
    msg = {'function':'Return_Init_ChartData',  'func_timeit': str((e - s)), 'datetime': datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S_%p')}
    print(msg)
    # dfs_index_tickers['SPY_5Minute']
    return {'init_charts': dfs_index_tickers, 'errors': error_dict}


def Return_Bars_LatestDayRebuild(ticker_time): #Iniaite Ticker Charts with Indicator Data
    # IMPROVEMENT: use Return_bars_list for Return_Bars_LatestDayRebuild
    # ticker_time = "SPY_1Minute_1Day"

    ticker, timeframe, days = ticker_time.split("_")
    error_dict = {}
    s = datetime.datetime.now()
    dfs_index_tickers = {}
    try:
        # return market hours data from bars
        bars_data = return_bars(symbol=ticker, timeframe=timeframe, ndays=0, exchange='CBSE') # return [True, symbol_data, market_hours_data, after_hours_data]
        df_bars_data = bars_data['df'] # mkhrs if in minutes
        # df_bars_data = df_bars_data.reset_index()
        if bars_data['resp'] == False:
            error_dict["NoData"] = bars_data['df'] # symbol already included in value
        else:
            dfs_index_tickers[ticker_time] = df_bars_data
    except Exception as e:
        print(ticker_time, e)
        print_line_of_error()
    
    e = datetime.datetime.now()
    msg = {'function':'Return_Bars_LatestDayRebuild',  'func_timeit': str((e - s)), 'datetime': datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S_%p')}
    # print(msg)
    # dfs_index_tickers['SPY_5Minute']
    return [dfs_index_tickers, error_dict, msg]


def Return_Snapshots_Rebuild(df_tickers_data, init=False): # from snapshots & consider using day.min.chart to rebuild other timeframes
    ticker_list = list([set(j.split("_")[0] for j in df_tickers_data.keys())][0]) #> get list of tickers

    # snapshots = {tic: api.get_crypto_snapshot(tic, exchange='CBSE') for tic in ticker_list}
    snapshots = {}
    for tic in ticker_list:
        snapshot = api.get_crypto_snapshot(tic, exchange='CBSE')
        snapshots[tic] = snapshot

        float_cols = ['close', 'high', 'open', 'low', 'vwap']
        int_cols = ['volume', 'trade_count']
        main_return_dict = {}


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
            'vwap': snapshots[ticker].daily_bar.vwap,
            'exchange': snapshots[ticker].daily_bar.exchange,
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
                'vwap': snapshots[ticker].minute_bar.vwap,
                'exchange': snapshots[ticker].minute_bar.exchange,
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
                # ipdb.set_trace()
                # print(df[['name', 'timestamp_est']].tail(2))
                df = df.head(-1) # drop last row which has current day
                df_rebuild = pd.concat([df, df_snapshot], join='outer', axis=0).reset_index(drop=True) # concat minute
                main_return_dict[ticker_time] = df_rebuild

    return main_return_dict


def ReInitiate_Charts_Past_Their_Time(df_tickers_data): # re-initiate for i timeframe 
    # IMPROVEMENT: use Return_bars_list for Return_Bars_LatestDayRebuild
    try:
        return_dict = {}
        rebuild_confirmation = {}

        def tag_current_day(timestamp):
            if timestamp.day == current_day and timestamp.month == current_month and timestamp.year == current_year:
                return 'tag'
            else:
                return '0'

        for ticker_time, df in df_tickers_data.items():
            ticker, timeframe, days = ticker_time.split("_")
            last = df['timestamp_est'].iloc[-2].replace(tzinfo=None)
            now = datetime.datetime.now()
            timedelta_minutes = (now - last).seconds / 60
            now_day = now.day
            last_day = last.day
            # ipdb.set_trace()
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
    except Exception as e:
        print(e)
        print_line_of_error()


def pollen_hunt(df_tickers_data, MACD):
    # Check to see if any charts need to be Recreate as times lapsed
    df_tickers_data_rebuilt = ReInitiate_Charts_Past_Their_Time(df_tickers_data)
    if len(df_tickers_data_rebuilt['rebuild_confirmation'].keys()) > 0:
        print(df_tickers_data_rebuilt['rebuild_confirmation'].keys())
        print(datetime.datetime.now().strftime("%H:%M-%S"))
    
    # re-add snapshot
    df_tickers_data_rebuilt = Return_Snapshots_Rebuild(df_tickers_data=df_tickers_data_rebuilt['ticker_time'])
    now = datetime.datetime.now()
    # print(now)
    # t = df_tickers_data_rebuilt['BTCUSD_5Minute_5Day']
    # print(t[['timestamp_est', 'close']].tail(2))
    # ipdb.set_trace()
    main_rebuild_dict = {} ##> only override current dict if memory becomes issues!
    chart_rebuild_dict = {}
    for ticker_time, bars_data in df_tickers_data_rebuilt.items():
        bars_data = bars_data[bars_data['exchange']=='CBSE']
        chart_rebuild_dict[ticker_time] = bars_data
        df_data_new = return_getbars_WithIndicators(bars_data=bars_data, MACD=MACD)
        if df_data_new[0] == True:
            main_rebuild_dict[ticker_time] = df_data_new[1]
        else:
            print("error", ticker_time)

    return {'pollencharts_nectar': main_rebuild_dict, 'pollencharts': chart_rebuild_dict}


print(
"""
We all shall prosper through the depths of our connected hearts,
Not all will share my world,
So I put forth my best mind of virtue and goodness, 
Always Bee Better
"""
)

# if '__name__' == '__main__':
#     print("Buzz Buzz Where My Honey")
#     logging.info("Buzz Buzz Where My Honey")

# init files needed
PB_Story_Pickle = os.path.join(db_root, f'{queens_chess_piece}{".pkl"}')
if queens_chess_piece == 'castle_coin':
    # if os.path.exists(PB_Story_Pickle):
    #     os.remove(PB_Story_Pickle)
    chart_times_castle = {
            "1Minute_1Day": 1, "5Minute_5Day": 5,
            "30Minute_1Month": 18, 
            "1Hour_3Month": 48, "2Hour_6Month": 72, 
            "1Day_1Year": 250}


""" Initiate your Charts with Indicators """
def initiate_ttframe_charts(queens_chess_piece, master_tickers, star_times, MACD_settings):
    s_mainbeetime = datetime.datetime.now()
    if queens_chess_piece.lower() == 'castle_coin':    # >>> Initiate your Charts
        res = Return_Init_ChartData(ticker_list=master_tickers, chart_times=star_times)
        errors = res['errors']
        if errors:
            msg = ("Return_Init_ChartData Failed", "--", errors)
            print(msg)
            logging.critical(msg)
            sys.exit()
        df_tickers_data_init = res['init_charts']
        # add snapshot to initial chartdata -1
        df_tickers_data = Return_Snapshots_Rebuild(df_tickers_data=df_tickers_data_init, init=True)
        # give it all to the QUEEN put directkly in function
        pollen = pollen_hunt(df_tickers_data=df_tickers_data, MACD=MACD_settings)
        QUEEN[queens_chess_piece]['pollencharts'] = pollen['pollencharts']
        QUEEN[queens_chess_piece]['pollencharts_nectar'] = pollen['pollencharts_nectar']
    
        """# mark final times and return values"""
        e_mainbeetime = datetime.datetime.now()
        msg = {queens_chess_piece:'initiate_ttframe_charts',  'block_timeit': str((e_mainbeetime - s_mainbeetime)), 'datetime': datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S_%p')}
        logging.info(msg)
        print(msg)


init_pollen = init_pollen_dbs(db_root=db_root, api=api, prod=prod, queens_chess_piece=queens_chess_piece)
PB_QUEEN_Pickle = init_pollen['PB_QUEEN_Pickle']
# PB_App_Pickle = init_pollen['PB_App_Pickle']

if os.path.exists(PB_QUEEN_Pickle) == False:
    print("WorkerBee Needs a Queen")
    # sys.exit()
    PickleData(PB_QUEEN_Pickle, data_to_store=False)
# Pollen QUEEN
if prod:
    WORKER_QUEEN = ReadPickleData(pickle_file=os.path.join(db_root, 'queen.pkl'))
else:
    WORKER_QUEEN = ReadPickleData(pickle_file=os.path.join(db_root, 'queen_sandbox.pkl'))
WORKER_QUEEN['source'] = PB_QUEEN_Pickle
MACD_12_26_9 = WORKER_QUEEN['queen_controls']['MACD_fast_slow_smooth']
master_tickers = WORKER_QUEEN['workerbees'][queens_chess_piece]['tickers']
MACD_settings = WORKER_QUEEN['workerbees'][queens_chess_piece]['MACD_fast_slow_smooth']
star_times = WORKER_QUEEN['workerbees'][queens_chess_piece]['stars']


try:
    initiate_ttframe_charts(queens_chess_piece=queens_chess_piece, master_tickers=master_tickers, star_times=star_times, MACD_settings=MACD_settings)
    workerbee_run_times = []
    speed_gauges = {
        f'{tic}{"_"}{star_}': {'macd_gauge': deque([], 89), 'price_gauge': deque([], 89)}
        for tic in master_tickers for star_ in star_times.keys()}

    while True:
        if queens_chess_piece.lower() in ['castle_coin']: # create the story
            s = datetime.datetime.now()
            if s > datetime.datetime(s.year, s.month, s.day, 23):
                logging.info("Happy Bee Crypto Day End")
                print("Great Job! See you Tomorrow")
                break
            
            # main 
            pollen = pollen_hunt(df_tickers_data=QUEEN[queens_chess_piece]['pollencharts'], MACD=MACD_settings)
            QUEEN[queens_chess_piece]['pollencharts'] = pollen['pollencharts']
            QUEEN[queens_chess_piece]['pollencharts_nectar'] = pollen['pollencharts_nectar']
            
            pollens_honey = pollen_story(pollen_nectar=QUEEN[queens_chess_piece]['pollencharts_nectar'], QUEEN=QUEEN, queens_chess_piece=queens_chess_piece)
            ANGEL_bee = pollens_honey['conscience']['ANGEL_bee']
            knights_sight_word = pollens_honey['conscience']['KNIGHTSWORD']
            STORY_bee = pollens_honey['conscience']['STORY_bee']

            # add all charts
            QUEEN[queens_chess_piece]['pollenstory'] = pollens_honey['pollen_story']


            # for each star append last macd state
            for ticker_time_frame, i in STORY_bee.items():
                speed_gauges[ticker_time_frame]['macd_gauge'].append(i['story']['macd_state'])
                speed_gauges[ticker_time_frame]['price_gauge'].append(i['story']['last_close_price'])
                STORY_bee[ticker_time_frame]['story']['macd_gauge'] = speed_gauges[ticker_time_frame]['macd_gauge']
                STORY_bee[ticker_time_frame]['story']['price_gauge'] = speed_gauges[ticker_time_frame]['price_gauge']
            SPEEDY_bee = speed_gauges

            # populate conscience
            QUEEN[queens_chess_piece]['conscience']['ANGEL_bee'] = ANGEL_bee
            QUEEN[queens_chess_piece]['conscience']['KNIGHTSWORD'] = knights_sight_word
            QUEEN[queens_chess_piece]['conscience']['STORY_bee'] = STORY_bee

            

            
            # God Save The QUEEN
            if PickleData(pickle_file=PB_Story_Pickle, data_to_store=QUEEN) == False:
                msg=("Pickle Data Failed")
                print(msg)
                logging.critical(msg)
                continue

            e = datetime.datetime.now()
            cycle_run_time = (e-s)
            if cycle_run_time.seconds > 15:
                print("CYCLE TIME SLLLLLLOOOoooooOOOOOO????")
                logging.info({"cycle_time > 15 seconds": str(cycle_run_time.seconds)})
            workerbee_run_times.append(cycle_run_time)
            avg_time = round(sum([i.seconds for i in workerbee_run_times]) / len(workerbee_run_times),2)
            print(queens_chess_piece, " avg cycle:", avg_time, ": ", cycle_run_time,  "sec: ", datetime.datetime.now().strftime("%A,%d. %I:%M:%S%p"))

except Exception as errbuz:
    print(errbuz)
    erline = print_line_of_error()
    log_msg = {'type': 'ProgramCrash', 'lineerror': erline}
    print(log_msg)
    logging.critical(log_msg)

#### >>>>>>>>>>>>>>>>>>> END <<<<<<<<<<<<<<<<<<###