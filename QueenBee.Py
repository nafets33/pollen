# QueenBee
import logging
from enum import Enum
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
from QueenHive import init_logging, pickle_chesspiece, speedybee, submit_order, return_timestamp_string, pollen_story, ReadPickleData, PickleData, return_api_keys, return_bars_list, refresh_account_info, return_bars, rebuild_timeframe_bars, init_index_ticker, print_line_of_error, return_index_tickers

# script arguments
queens_chess_piece = sys.argv[1] # 'castle', 'knight' 'queen'

main_root = os.getcwd()
db_root = os.path.join(main_root, 'db')

init_logging(queens_chess_piece, db_root)

# Macd Settings
MACD_12_26_9 = {'fast': 12, 'slow': 26, 'smooth': 9}
QUEEN = { # The Queens Mind
    queens_chess_piece: {
    'conscience': {'pollenstory': {},'knightsword': {}, 'command_conscience': {}, 'memory': {}, 'orders': []}, # change knightsword
    'pollenstory': {}, # latest story of dataframes
    'pollencharts': {}, # latest chart rebuild
    'pollencharts_nectar': {}, # latest chart rebuild with indicators
    'pollenstory_info': {}, # Misc Info,
    'client': {},
    'heartbeat': {},
    'last_modified' : datetime.datetime.now(),
    }
}

prod = True
pd.options.mode.chained_assignment = None
est = pytz.timezone("US/Eastern")
load_dotenv()

if queens_chess_piece.lower() not in ['queen', 'castle', 'knight', 'bishop', 'workerbee']:
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

QUEEN[queens_chess_piece]['heartbeat']['main_indexes'] = {
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

    # client_symbols = ['SPY', 'SPDN', 'SPXU', 'SPXL', 'TQQQ', 'SQQQ', 'AAPL', 'GOOG', 'VIX'] # Should be from CSV file OR UI List from app
    LongTerm_symbols = ['AAPL', 'GOOGL', 'MFST', 'VIT', 'HD', 'WMT', 'MOOD', 'LIT', 'SPXL', 'TQQQ']
    # BeeHunter = {
    #     'LongX3': {'TQQQ': 'TQQQ', 'SPXL': 'SPXL'},
    #     'ShortX3': {'SQQQ':'SQQQ', 'SPXU': 'SPXU'},
    #     'Long':  {'SPY': 'SPY', 'QQQQ': 'QQQQ'}
    # }
    # main_index_tickers = ['SPY', 'QQQ']

    index_ticker_db = return_index_tickers(index_dir=os.path.join(db_root, 'index_tickers'), ext='.csv')

    """ Return Index Charts & Data for All Tickers Wanted"""
    """ Return Tickers of SP500 & Nasdaq / Other Tickers"""    

####<>///<>///<>///<>///<>/// ALL FUNCTIONS NECTOR ####<>///<>///<>///<>///<>///


"""TICKER Calculation Functions"""

def return_macd(df_main, fast, slow, smooth):
    price = df_main['close']
    exp1 = price.ewm(span = fast, adjust = False).mean()
    exp2 = price.ewm(span = slow, adjust = False).mean()
    macd = pd.DataFrame(exp1 - exp2).rename(columns = {'close':'macd'})
    signal = pd.DataFrame(macd.ewm(span = smooth, adjust = False).mean()).rename(columns = {'macd':'signal'})
    hist = pd.DataFrame(macd['macd'] - signal['signal']).rename(columns = {0:'hist'})
    frames =  [macd, signal, hist]
    df = pd.concat(frames, join='inner', axis=1)
    df_main = pd.concat([df_main, df], join='inner', axis=1)
    return df_main


def return_VWAP(df):
    # VWAP
    df = df.assign(
        vwap=df.eval(
            'wgtd = close * volume', inplace=False
        ).groupby(df['timestamp_est']).cumsum().eval('wgtd / volume')
    )
    return df


def vwap(df):
    q = df.volume.values
    p = df.close.values
    df.assign(vwap=(p * q).cumsum() / q.cumsum())
    df = df.groupby(df['timestamp_est'], group_keys=False).apply(vwap).fillna(0)
    return df


def return_RSI(df, length):
    # Define function to calculate the RSI
    # length = 14 # test
    # df = df.reset_index(drop=True)
    close = df['close']
    def calc_rsi(over: pd.Series, fn_roll: Callable) -> pd.Series:
        # Get the difference in price from previous step
        delta = over.diff()
        # Get rid of the first row, which is NaN since it did not have a previous row to calculate the differences
        delta = delta[1:] 

        # Make the positive gains (up) and negative gains (down) Series
        up, down = delta.clip(lower=0), delta.clip(upper=0).abs()

        roll_up, roll_down = fn_roll(up), fn_roll(down)
        rs = roll_up / roll_down
        rsi = 100.0 - (100.0 / (1.0 + rs))

        # Avoid division-by-zero if `roll_down` is zero
        # This prevents inf and/or nan values.
        rsi[:] = np.select([roll_down == 0, roll_up == 0, True], [100, 0, rsi])
        rsi.name = 'rsi'

        # Assert range
        valid_rsi = rsi[length - 1:]
        assert ((0 <= valid_rsi) & (valid_rsi <= 100)).all()
        # Note: rsi[:length - 1] is excluded from above assertion because it is NaN for SMA.
        return rsi

    # Calculate RSI using MA of choice
    # Reminder: Provide ≥ 1 + length extra data points!
    rsi_ema = calc_rsi(close, lambda s: s.ewm(span=length).mean())
    rsi_ema.name = 'rsi_ema'
    df = pd.concat((df, rsi_ema), axis=1).fillna(0)
    
    rsi_sma = calc_rsi(close, lambda s: s.rolling(length).mean())
    rsi_sma.name = 'rsi_sma'
    df = pd.concat((df, rsi_sma), axis=1).fillna(0)

    rsi_rma = calc_rsi(close, lambda s: s.ewm(alpha=1 / length).mean())  # Approximates TradingView.
    rsi_rma.name = 'rsi_rma'
    df = pd.concat((df, rsi_rma), axis=1).fillna(0)

    return df


def return_sma_slope(df, y_list, time_measure_list):
        # df=pollenstory['SPY_1Minute_1Day'].copy()
        # time_measure_list = [3, 23, 33]
        # y_list = ['close', 'macd', 'hist']
        for mtime in time_measure_list:
            for el in y_list:
                sma_name = f'{el}{"_sma-"}{mtime}'
                slope_name = f'{el}{"_slope-"}{mtime}'
                df[sma_name] = df[el].rolling(mtime).mean().fillna(1)
                df[slope_name] = np.degrees(np.arctan(df[sma_name].diff()/mtime))
        return df


"""TICKER ChartData Functions"""

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
    # ticker_list = ['SPY', 'QQQ']
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
    bars = return_bars_list(ticker_list, chart_times)
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
        bars_data = return_bars(symbol=ticker, timeframe=timeframe, ndays=0, trading_days_df=trading_days_df) # return [True, symbol_data, market_hours_data, after_hours_data]
        df_bars_data = bars_data[2] # mkhrs if in minutes
        # df_bars_data = df_bars_data.reset_index()
        if bars_data[0] == False:
            error_dict["NoData"] = bars_data[1] # symbol already included in value
        else:
            dfs_index_tickers[ticker_time] = df_bars_data
    except Exception as e:
        print(ticker_time, e)
    
    e = datetime.datetime.now()
    msg = {'function':'Return_Bars_LatestDayRebuild',  'func_timeit': str((e - s)), 'datetime': datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S_%p')}
    # print(msg)
    # dfs_index_tickers['SPY_5Minute']
    return [dfs_index_tickers, error_dict, msg]


def Return_Snapshots_Rebuild(df_tickers_data, init=False): # from snapshots & consider using day.min.chart to rebuild other timeframes
    ticker_list = list([set(j.split("_")[0] for j in df_tickers_data.keys())][0]) #> get list of tickers

    snapshots = api.get_snapshots(ticker_list)
    # snapshots['SPY'].latest_trade
    # snapshots['SPY'].latest_trade.conditions

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
    min_bars_dict = {k:{} for k in ticker_list} # REBUILDING MIN BARS NEEDS IMPROVEMENT BEFORE SOME MAY FAIL TO RETURN

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
            
            # if len(min_bars_dict[ticker]) != 0:
            #     # "THIS IS NOT being used"
            #     d = {'close': min_bars_dict[ticker].close.iloc[-1],
            #     'high': min_bars_dict[ticker].high.iloc[-1],
            #     'low': min_bars_dict[ticker].low.iloc[-1],
            #     'timestamp_est': min_bars_dict[ticker].timestamp_est.iloc[-1],
            #     'open': min_bars_dict[ticker].open.iloc[-1],
            #     'volume': min_bars_dict[ticker].volume.iloc[-1],
            #     'trade_count': min_bars_dict[ticker].trade_count.iloc[-1],
            #     'vwap': min_bars_dict[ticker].vwap.iloc[-1]
            #     }
            # else:
            #     d = {
            #     'close': snapshots[ticker].latest_trade.price,
            #     'high': 0, # snapshots[ticker].minute_bar.high,
            #     'low': 0, # snapshots[ticker].minute_bar.low,
            #     'timestamp_est': snapshots[ticker].latest_trade.timestamp,
            #     'open': 0, # snapshots[ticker].minute_bar.open,
            #     'volume': 0, # snapshots[ticker].minute_bar.volume,
            #     'trade_count': 0, # snapshots[ticker].minute_bar.trade_count,
            #     'vwap': snapshots[ticker].minute_bar.vwap
            #     }
            d = {
                'close': snapshots[ticker].latest_trade.price,
                'high': 0, # snapshots[ticker].minute_bar.high,
                'low': 0, # snapshots[ticker].minute_bar.low,
                'timestamp_est': snapshots[ticker].latest_trade.timestamp,
                'open': 0, # snapshots[ticker].minute_bar.open,
                'volume': 0, # snapshots[ticker].minute_bar.volume,
                'trade_count': 0, # snapshots[ticker].minute_bar.trade_count,
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
        last = df['timestamp_est'].iloc[-2].replace(tzinfo=None)
        now = datetime.datetime.now()
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
        print(datetime.datetime.now().strftime("%H:%M-%S"))
    
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
    
    # QUEEN['pollencharts'] = chart_rebuild_dict
    # QUEEN['pollencharts_nectar'] = main_rebuild_dict
    return {'pollencharts_nectar': main_rebuild_dict, 'pollencharts': chart_rebuild_dict}


def read_pollenstory(): # return combined dataframes
    castle = ReadPickleData(pickle_file=os.path.join(db_root, 'castle.pkl'))
    bishop = ReadPickleData(pickle_file=os.path.join(db_root, 'bishop.pkl'))
    pollenstory = {**bishop['bishop']['pollenstory'], **castle['castle']['pollenstory']} # combine daytrade and longterm info
    return pollenstory


def read_queensmind(): # return active story workers
    castle = ReadPickleData(pickle_file=os.path.join(db_root, 'castle.pkl'))['castle']
    bishop = ReadPickleData(pickle_file=os.path.join(db_root, 'bishop.pkl'))['bishop']
    # knight = ReadPickleData(pickle_file=os.path.join(db_root, 'knight.pkl'))
    collective_pollenstory = {**bishop['conscience']['pollenstory'], **castle['conscience']['pollenstory']}
    knightsword = {**bishop['conscience']['knightsword'], **castle['conscience']['knightsword']}
    
    return {'bishop': bishop, 'castle': castle, 'collective_pollenstory': collective_pollenstory, 'knightsword': knightsword}

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

# Account Info
# Check System
# All Symbols and Tickers
# Intiaite Main tickers
# Order Manage Loop

# init files needed
PB_Story_Pickle = os.path.join(db_root, f'{queens_chess_piece}{".pkl"}')
if queens_chess_piece == 'castle':
    if os.path.exists(PB_Story_Pickle):
        os.remove(PB_Story_Pickle)
    chart_times_castle = {
            "1Minute_1Day": 1, "5Minute_5Day": 5,
            "30Minute_1Month": 18, 
            "1Hour_3Month": 48, "2Hour_6Month": 72, 
            "1Day_1Year": 250}

if queens_chess_piece == 'bishop':
    if os.path.exists(PB_Story_Pickle):
        os.remove(PB_Story_Pickle)
    chart_times_bishop = {
            "1Minute_1Day": 1, "5Minute_5Day": 5,
            "30Minute_1Month": 18, 
            "1Hour_3Month": 48, "2Hour_6Month": 72, 
            "1Day_1Year": 250}

if queens_chess_piece == 'workerbee':
    if os.path.exists(PB_Story_Pickle):
        os.remove(PB_Story_Pickle)

if queens_chess_piece == 'queen':
    print("My Queen")

s_mainbeetime = datetime.datetime.now()


""" Initiate your Charts with Indicators """
def initiate_ttframe_charts(queens_chess_piece):
    if queens_chess_piece.lower() == 'castle':    # >>> Initiate your Charts
        res = Return_Init_ChartData(ticker_list=client_symbols_castle, chart_times=chart_times_castle)
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
        pollen = pollen_hunt(df_tickers_data=df_tickers_data, MACD=MACD_12_26_9)
        QUEEN[queens_chess_piece]['pollencharts'] = pollen['pollencharts']
        QUEEN[queens_chess_piece]['pollencharts_nectar'] = pollen['pollencharts_nectar']
    
        """# mark final times and return values"""
        e_mainbeetime = datetime.datetime.now()
        msg = {'Main':'Queen',  'block_timeit': str((e_mainbeetime - s_mainbeetime)), 'datetime': datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S_%p')}
        logging.info(msg)
        print(msg)

    if queens_chess_piece.lower() == 'bishop':
        # >>> Initiate your Charts
        res = Return_Init_ChartData(ticker_list=client_symbols_bishop, chart_times=chart_times_bishop)
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
        pollen = pollen_hunt(df_tickers_data=df_tickers_data, MACD=MACD_12_26_9)
        QUEEN[queens_chess_piece]['pollencharts'] = pollen['pollencharts']
        QUEEN[queens_chess_piece]['pollencharts_nectar'] = pollen['pollencharts_nectar']
    
        """# mark final times and return values"""
        e_mainbeetime = datetime.datetime.now()
        msg = {'Main':'Queen',  'block_timeit': str((e_mainbeetime - s_mainbeetime)), 'datetime': datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S_%p')}
        logging.info(msg)
        print(msg)


# >>> Continue to Rebuild ChartData and Story
try:
    initiate_ttframe_charts(queens_chess_piece)
    while True:
        if queens_chess_piece.lower() in ['castle', 'bishop']:
            s = datetime.datetime.now()
            if s > datetime.datetime(s.year, s.month, s.day, 16):
                logging.info("Happy Bee Day End")
                print("Great Job! See you Tomorrow")
                break
            pollen = pollen_hunt(df_tickers_data=QUEEN[queens_chess_piece]['pollencharts'], MACD=MACD_12_26_9)
            QUEEN[queens_chess_piece]['pollencharts'] = pollen['pollencharts']
            QUEEN[queens_chess_piece]['pollencharts_nectar'] = pollen['pollencharts_nectar']
            pollens_honey = pollen_story(pollen_nectar=QUEEN[queens_chess_piece]['pollencharts_nectar'], QUEEN=QUEEN, queens_chess_piece=queens_chess_piece)
            QUEEN[queens_chess_piece]['pollenstory'] = pollens_honey['pollen_story']
            if PickleData(pickle_file=PB_Story_Pickle, data_to_store=QUEEN) == False:
                msg=("Pickle Data Failed")
                print(msg)
                logging.critical(msg)
                continue
            if queens_chess_piece == 'castle':
                speedybee(QUEEN, queens_chess_piece, ticker_list=client_market_movers)
            e = datetime.datetime.now()
            print(queens_chess_piece, str((e - s).seconds),  "sec: ", datetime.datetime.now().strftime("%A,%d. %I:%M:%S%p"))

        if queens_chess_piece.lower() == 'workerbee': # return tics
            s = datetime.datetime.now()
            if s > datetime.datetime(s.year, s.month, s.day, 16):
                logging.info("Happy Bee Day End")
                print("Great Job! See you Tomorrow")
                break
            tic_tickers = ['AAPL', 'TSLA', 'GOOG', 'FB']
            r = rebuild_timeframe_bars(ticker_list=tic_tickers, build_current_minute=False, min_input=0, sec_input=30) # return all tics
            resp = r['resp'] # return slope of collective tics
            slope_dict = {}
            for symbol in set(resp['symbol'].to_list()):
                df = resp[resp['symbol']==symbol].copy()
                df = df.reset_index()
                df_len = len(df)
                if df_len > 2:
                    slope, intercept, r_value, p_value, std_err = stats.linregress(df.index, df['price'])
                    slope_dict[df.iloc[0].symbol] = slope

            print(sum([v for k,v in slope_dict.items()]))
            # for k, i in slope_dict.items():
            #     print(k, i)
            
            if PickleData(pickle_file=PB_Story_Pickle, data_to_store=QUEEN) == False:
                msg=("Pickle Data Failed")
                print(msg)
                logging.critical(msg)
                continue
            e = datetime.datetime.now()
            print(queens_chess_piece, str((e - s).seconds),  "sec: ", datetime.datetime.now().strftime("%A,%d. %I:%M:%S%p"))

        if queens_chess_piece.lower() == 'knight': # TBD
            s = datetime.datetime.now()
            if s > datetime.datetime(s.year, s.month, s.day, 16):
                logging.info("Happy Bee Day End")
                print("Great Job! See you Tomorrow")
                break

            # Read chart story data
            castle = ReadPickleData(pickle_file=os.path.join(db_root, 'castle.pkl'))
            bishop = ReadPickleData(pickle_file=os.path.join(db_root, 'bishop.pkl'))
            if castle == False or bishop == False:
                msg = ("Failed in Reading of Castle of Bishop Pickle File")
                print(msg)
                logging.warning(msg)
                continue
            else:
                pollenstory = {**bishop['bishop']['pollenstory'], **castle['castle']['pollenstory']} # combine daytrade and longterm info
                # make recording of last modified
                lastmod = bishop["last_modified"]["last_modified"]
                
                if lastmod > QUEEN[queens_chess_piece]["last_modified"]:
                    QUEEN[queens_chess_piece]["last_modified"] = lastmod
                    
                    if prod:
                        def bid_ask_devation(symbol):
                            devation = .01  #(bid - ask) / ask
                            return devation


                        def generate_order_id():
                            var_1 = 'buy'
                            var_2 = 'type'  # create category types based on framework of scenarios
                            now = return_timestamp_string()
                            x = now
                            # id = str(int(hashlib.md5(x.encode('utf8')).hexdigest(), 16))
                            id = now + "_" + str(var_1) + "_" + str(var_2)
                            return id # OR just return the string iteslf? that is better no?
                        

                        def queens_order_managment(prod, spy, symbols):
                            prod = 'sandbox'
                            symbols = {'sting': ['spy']}  # sting: fast day trade
                            symbols_argu = {'qty': 1, 'side': 'buy', 'type': 'market'}
                            symbol = spy
                            qty = 1
                            side = 'buy'
                            type = 'market'  #'limit', 'market'
                            time_in_force = 'gtc'
                            client_order_id = generate_order_id()

                            # Buy in Prod or Sandbox
                            if prod:
                                api =api
                            else:
                                api = api_paper



                        if PickleData(pickle_file=PB_Story_Pickle, data_to_store=QUEEN) == False:
                            msg=("Pickle Data Failed")
                            print(msg)
                            logging.critical(msg)
                            continue
                    
                        spy = pollenstory['SPY_1Minute_1Day']
                        print(spy[['macd_cross', 'close_mom_3', 'nowdate']].tail(5))

                    
                    e = datetime.datetime.now()
                    print("knight", str((e - s).seconds) + ": " + datetime.datetime.now().strftime("%A, %d. %B %Y %I:%M:%S%p"))

        if queens_chess_piece.lower() == 'queen': # Read Bees Story 
            pollenstory = read_pollenstory()
            QUEEN[queens_chess_piece]['pollenstory'] = pollenstory
            queensmind = read_queensmind()
            mindseye = queensmind['collective_pollenstory'] # all ttframes with all immediate info needed
            qm_knightsword = queensmind['knightsword'] # all ttframes with all triggers their lastmod times
            
            knight_bees = {}
            day_theme = {} # set the course for the day how you want to buy expecting more scalps vs long? this should update and change as new info comes into being
            current_positions = {}

            
            # working with SPY TO START ONLY
            def command_conscience(api, ticker):
                ticker = 'SPY'

                king = {k:v for (k, v) in mindseye.items() if k.split("_")[0] == ticker} # filter by ticker
                all_current_triggers = {k:v['alltriggers_current_state'] for (k,v) in king.items() if len(v['alltriggers_current_state']) > 0}
                memory = {k.split("_")[0]: [] for (k,v) in king.items()} # memory should be initialized
                if all_current_triggers:
                    if f'{ticker}{"_1Minute_1Day"}' in all_current_triggers.keys():
                        # cycle through triggers and pass buy first logic for buy
                        trigs =  all_current_triggers[f'{ticker}{"_1Minute_1Day"}']
                        for trig in trigs:
                            if trig == "buy_cross-0":
                                print("trig", trig, return_timestamp_string())
                                # check if you already placed order or if a workerbee in transit to place order
                                all_position = api.list_positions() # return current position # check current position of order
                                open_orders_list = api.list_orders(status='open') # check if open order exists
                                if ticker in [i.symbol for i in all_position]:
                                    memory_trig_stopped = memory[ticker]['trigger_stopped']
                                    for trig_info in memory_trig_stopped:
                                        if trig_info['trigname'] == trig:
                                            print("trig already stopped moving on")
                                    print("position already taken send info to Queen")
                                    memory[ticker]['trigger_stopped'].append({'trigname': trig, 'datetime': datetime.datetime.now().isoformat()})
                                else:
                                    print("Always Bee Better > Each Buz in a gift")
                                    # FUNCTION THAT CHECKS ORDER TO input Qty
                                    order = submit_order(api=api, symbol=ticker, type='market', qty=1, side='buy', client_order_id=trig) # buy
                                    QUEEN[queens_chess_piece]['conscience']['orders'].append({'ticker': ticker, 'order': order, 'datetime': datetime.datetime.now().isoformat()})
                                    pickle_chesspiece(pickle_file=PB_Story_Pickle, data_to_story=QUEEN)
                            
                            if ticker in QUEEN[queens_chess_piece]['heartbeat']['main_indexes']: # SPY, QQQ
                                if trig == "sell_cross-0":
                                    print("trig", trig, return_timestamp_string())
                                    # check if you already placed order or if a workerbee in transit to place order
                                    all_position = api.list_positions() # return current position # check current position of order
                                    open_orders_list = api.list_orders(status='open') # check if open order exists
                                    if ticker in [i.symbol for i in all_position]:
                                        memory_trig_stopped = memory[ticker]['trigger_stopped']
                                        for trig_info in memory_trig_stopped:
                                            if trig_info['trigname'] == trig:
                                                print("trig already stopped moving on")
                                        print("position already taken send info to Queen")
                                        memory[ticker]['trigger_stopped'].append({'trigname': trig, 'datetime': datetime.datetime.now().isoformat()})
                                    else:
                                        print("Always Bee Better > Each Buz in a gift")
                                        # FUNCTION THAT CHECKS ORDER TO input Qty
                                        order = submit_order(api=api, symbol=QUEEN[queens_chess_piece]['heartbeat']['main_indexes'][ticker]['inverse'], type='market', qty=1, side='buy', client_order_id=trig) # buy
                                        QUEEN[queens_chess_piece]['conscience']['orders'].append({'ticker': ticker, 'order': order, 'datetime': datetime.datetime.now().isoformat()})
                                        if pickle_chesspiece(pickle_file=PB_Story_Pickle, data_to_store=QUEEN):
                                            pass
                                        else:
                                            print("ERROR WITH PICKLE")
                                            logging.critical("{'type': 'orders', 'errorname': 'ERROR WITH PICKLE'}")
            
            for ttframe, mind in mindseye.items():
                ticker, time, frame = ttframe.split("_")
                command_conscience(api=api_paper, ticker=ticker)
            

            # manager orders
            def order_management():
                # you need a better name for the function : )
                closed_orders_list = api.list_orders(status='closed')
                open_orders_list = api.list_orders(status='open')

                # get all orders that have been submitted
                beeorders = QUEEN[queens_chess_piece]['conscience']['orders']
                
                # get all orders that are open


                return True

            # QUEEN[queens_chess_piece]['conscience']['pollenstory'] = mindseye
            # QUEEN[queens_chess_piece]['conscience']['knightsword'] = qm_knightsword
            
            # print(queens_chess_piece, str((e - s).seconds),  "sec: ", datetime.datetime.now().strftime("%A,%d. %I:%M:%S%p"))


            """
                > lets do this!!!!
                love: anchor on the 1 min macd crosses or better yet just return all triggers and base everything off the trigger
            """

    # >>> Buy Sell Weights 

    # >>> NEED TO FIX the return for each time interval, rebuild 5 Min, 1 hr...etc....Put rebuild charts into new dict where they get maintained...add logic for each interval...i.e. on 5Min Mark rebuild with Initiate OR replace last 5 Minutes....?
except Exception as errbuz:
    print(errbuz)
    log_msg = {'type': 'ProgramCrash'}
    logging.critical(log_msg)
    pickle_chesspiece(pickle_file=PB_Story_Pickle, data_to_store=QUEEN)

#### >>>>>>>>>>>>>>>>>>> END <<<<<<<<<<<<<<<<<<###