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
from QueenHive import pollen_story, ReadPickleData, PickleData, return_api_keys, return_bars_list, refresh_account_info, return_bars, rebuild_timeframe_bars, init_index_ticker, print_line_of_error, return_index_tickers
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
from scipy.stats import linregress
from scipy import stats

prod = True
pd.options.mode.chained_assignment = None
est = pytz.timezone("US/Eastern")
load_dotenv()
# >>> initiate db directories
# system = 'windows' #mac, windows
# if system != 'windows':
#     db_root = os.environ.get('db_root_mac')
# else:
#     db_root = os.environ.get('db_root_winodws')

queens_chess_piece = sys.argv[1] # 'castle', 'knight'
if queens_chess_piece.lower() not in ['castle', 'knight', 'bishop', 'workerbee']:
    print("wrong chess move")
    sys.exit()

main_root = os.getcwd()
db_root = os.path.join(main_root, 'db')

# scriptname = os.path.basename(__file__)
log_dir = dst = os.path.join(db_root, 'logs')
if os.path.exists(dst) == False:
    os.mkdir(dst)
log_name = f'{"log_"}{queens_chess_piece}{".log"}'
log_file = os.path.join(os.getcwd(), log_name)
if os.path.exists(log_file) == False:
    logging.basicConfig(filename=f'{"log_"}{queens_chess_piece}{".log"}',
                        filemode='a',
                        format='%(asctime)s:%(name)s:%(levelname)s: %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p',
                        level=logging.INFO)
else:
    # copy log file to log dir & del current log file
    datet = datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S_%p')
    dst_path = os.path.join(log_dir, f'{log_name}{"_"}{datet}{".log"}')
    shutil.copy(log_file, dst_path)
    os.remove(log_file)
    logging.basicConfig(filename=f'{"log_"}{queens_chess_piece}{".log"}',
                        filemode='a',
                        format='%(asctime)s:%(name)s:%(levelname)s: %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p',
                        level=logging.INFO)

# Client Tickers
src_root, db_dirname = os.path.split(db_root)
client_ticker_file = os.path.join(src_root, 'client_tickers.csv')
df_client = pd.read_csv(client_ticker_file, dtype=str)
client_symbols = df_client.tickers.to_list()

# client_num_LT = sys.argv[2]
# client_num_ST = sys.argv[3]
# client_days1yrmac_input = sys.argv[4]


# trade closer to ask price .... sellers closer to bid .... measure divergence from bid/ask to give weight


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

# Initiate Code File Creation
index_ticker_db = os.path.join(db_root, "index_tickers")
if os.path.exists(index_ticker_db) == False:
    os.mkdir(index_ticker_db)
    print("Ticker Index db Initiated")
    init_index_ticker(index_list, db_root, init=True)


#### ALL FUNCTIONS NECTOR ####

def return_timestamp_string():
    return datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S %p')


index_ticker_db = return_index_tickers(index_dir=os.path.join(db_root, 'index_tickers'), ext='.csv')



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


def mark_macd_signal_cross(df): # Mark the signal macd crosses 
    m=df['macd'].to_list()
    s=df['signal'].to_list()
    cross_list=[]
    for i, macdvalue in enumerate(m):
        if i != 0:
            prior_mac = m[i-1]
            prior_signal = s[i-1]
            now_mac = macdvalue
            now_signal = s[i]
            if now_mac > now_signal and prior_mac <= prior_signal:
                cross_list.append('buy_cross')
            elif now_mac < now_signal and prior_mac >= prior_signal:
                cross_list.append('sell_cross')
            else:
                cross_list.append('hold')
        else:
            cross_list.append('hold')
    df2 = pd.DataFrame(cross_list, columns=['macd_cross'])
    df_new = pd.concat([df, df2], axis=1)
    return df_new


def return_sma_slope(df, y_list, time_measure_list):
        # df=pollenstory['SPY_1Minute_1Day'].copy()
        # time_measure_list = [3, 23, 33]
        # y_list = ['close', 'macd', 'hist']
        for mtime in time_measure_list:
            for el in y_list:
                sma_name = f'{el}{"_sma-"}{mtime}'
                slope_name = f'{el}{"_slope-"}{mtime}'
                df[sma_name] = df[el].rolling(mtime).mean().fillna(0)
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
# bee = return_getbars_WithIndicators(bars_data=)

def Return_Init_ChartData(ticker_list, chart_times): #Iniaite Ticker Charts with Indicator Data
    # ticker_list = ['SPY', 'QQQ']
    # chart_times = {
    #     "1Minute_1Day": 0, "5Minute_5Day": 5, "30Minute_1Month": 18, 
    #     "1Hour_3Month": 48, "2Hour_6Month": 72, 
    #     "1Day_1Year": 250}
    print(ticker_list, chart_times)
    msg = {'function':'Return_Init_ChartData','datetime': datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S_%p')}
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
# r=Return_Init_ChartData(ticker_list, chart_times)

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
# Return_Bars_LatestDayRebuild(ticker_time)


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
            
            if len(min_bars_dict[ticker]) != 0:
                d = {'close': min_bars_dict[ticker].close.iloc[-1],
                'high': min_bars_dict[ticker].high.iloc[-1],
                'low': min_bars_dict[ticker].low.iloc[-1],
                'timestamp_est': min_bars_dict[ticker].timestamp_est.iloc[-1],
                'open': min_bars_dict[ticker].open.iloc[-1],
                'volume': min_bars_dict[ticker].volume.iloc[-1],
                'trade_count': min_bars_dict[ticker].trade_count.iloc[-1],
                'vwap': 0, #snapshots[ticker].latest_trade.vwap
                }
            else:
                # print("Min Bar Not returned (AFTERHRS)")
                d = {
                'close': snapshots[ticker].latest_trade.price,
                'high': 0, # snapshots[ticker].minute_bar.high,
                'low': 0, # snapshots[ticker].minute_bar.low,
                'timestamp_est': snapshots[ticker].latest_trade.timestamp,
                'open': 0, # snapshots[ticker].minute_bar.open,
                'volume': 0, # snapshots[ticker].minute_bar.volume,
                'trade_count': 0, # snapshots[ticker].minute_bar.trade_count,
                'vwap': 0, # snapshots[ticker].minute_bar.vwap
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
# PollenBee_Charts = pollen_hunt(ticker_list=main_index_tickers)

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
logging.info("Buzz Buzz Where My Honey")
# Account Info
# Check System
# All Symbols and Tickers
# Intiaite Main tickers
# Order Manage Loop
QUEEN = { # The Queens Mind
    'pollenstory': {}, # latest story
    'pollencharts': {}, # latest rebuild
    'pollencharts_nectar': {}, # latest charts with indicators
    'pollenstory_info': {}, # Misc Info,
    'self_last_modified' : datetime.datetime.now(),
    }

# init files needed
PB_Story_Pickle = os.path.join(db_root, f'{queens_chess_piece}{".pkl"}')
if queens_chess_piece == 'castle':
    if os.path.exists(PB_Story_Pickle):
        os.remove(PB_Story_Pickle)
    chart_times = {
            #"1Minute_1Day": 0, "5Minute_5Day": 5,
            "30Minute_1Month": 18, 
            "1Hour_3Month": 48, "2Hour_6Month": 72, 
            "1Day_1Year": 250}

if queens_chess_piece == 'bishop':
    if os.path.exists(PB_Story_Pickle):
        os.remove(PB_Story_Pickle)
    chart_times = {
            "1Minute_1Day": 1, "5Minute_5Day": 5,}

if queens_chess_piece == 'workerbee':
    if os.path.exists(PB_Story_Pickle):
        os.remove(PB_Story_Pickle)

s_mainbeetime = datetime.datetime.now()
#LongTerm_symbols = ?Weight Each Symbol? or just you assests and filter on Market Cap & VOL SECTOR, EBITDA, Free Cash Flow

if prod: # Return Ticker and Acct Info
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
    BeeHunter = {
        'LongX3': {'TQQQ': 'TQQQ', 'SPXL': 'SPXL'},
        'ShortX3': {'SQQQ':'SQQQ', 'SPXU': 'SPXU'},
        'Long':  {'SPY': 'SPY', 'QQQQ': 'QQQQ'}
    }
    main_index_tickers = ['SPY', 'QQQ']
    """ Return Index Charts & Data for All Tickers Wanted"""
    """ Return Tickers of SP500 & Nasdaq / Other Tickers"""    

    # Macd Settings
    MACD_12_26_9 = {'fast': 12, 'slow': 26, 'smooth': 9}

""" Initiate your Charts with Indicators """
if queens_chess_piece.lower() in ['castle', 'bishop']:
    # >>> Initiate your Charts
    res = Return_Init_ChartData(ticker_list=client_symbols, chart_times=chart_times)
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
    QUEEN['pollencharts'] = pollen['pollencharts']
    QUEEN['pollencharts_nectar'] = pollen['pollencharts_nectar']
 
    """# mark final times and return values"""
    e_mainbeetime = datetime.datetime.now()
    msg = {'Main':'Queen',  'block_timeit': str((e_mainbeetime - s_mainbeetime)), 'datetime': datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S_%p')}
    print(msg)
 
    """# mark final times and return values"""
    e_mainbeetime = datetime.datetime.now()
    msg = {'Main':'Queen',  'block_timeit': str((e_mainbeetime - s_mainbeetime)), 'datetime': datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S_%p')}
    print(msg)

# >>> Continue to Rebuild ChartData and Story
while True:
    if queens_chess_piece.lower() in ['castle', 'bishop']:
        s = datetime.datetime.now()
        if s > datetime.datetime(s.year, s.month, s.day, 16):
            logging.info("Happy Bee Day End")
            print("Great Job! See you Tomorrow")
            break
        pollen = pollen_hunt(df_tickers_data=QUEEN['pollencharts'], MACD=MACD_12_26_9)
        QUEEN['pollencharts'] = pollen['pollencharts']
        QUEEN['pollencharts_nectar'] = pollen['pollencharts_nectar']
        pollens_honey = pollen_story(pollen_nectar=QUEEN['pollencharts_nectar'], QUEEN=QUEEN)
        QUEEN['pollenstory'] = pollens_honey['pollen_story']
        if PickleData(pickle_file=PB_Story_Pickle, data_to_store=QUEEN) == False:
            msg=("Pickle Data Failed")
            print(msg)
            logging.critical(msg)
            continue
        e = datetime.datetime.now()
        print(queens_chess_piece, str((e - s)) + ": " + datetime.datetime.now().strftime("%A, %d. %B %Y %I:%M:%S%p"))

    if queens_chess_piece.lower() == 'knight': # Read Bees Story
        s = datetime.datetime.now()
        if s > datetime.datetime(s.year, s.month, s.day, 16):
            logging.info("Happy Bee Day End")
            print("Great Job! See you Tomorrow")
            break

        castle = ReadPickleData(pickle_file=os.path.join(db_root, 'castle.pkl'))
        bishop = ReadPickleData(pickle_file=os.path.join(db_root, 'bishop.pkl'))  
        if castle == False or bishop == False:
            msg = ("Failed in Reading of Castle of Bishop Pickle File")
            print(msg)
            logging.warning(msg)
            continue
        else:
            pollenstory = {**bishop['pollenstory'], **castle['pollenstory']} # combine daytrade and longterm info
            # make recording of last modified
            lastmod = bishop["last_modified"]["last_modified"]
            if lastmod > QUEEN["self_last_modified"]:
                QUEEN["self_last_modified"] = lastmod
                spy = pollenstory['SPY_1Minute_1Day']
                print(spy[['tier_macd', 'macd', 'signal', 'hist', 'rsi_rma', 'nowdate']].tail(5))

                e = datetime.datetime.now()
                print("knight", str((e - s)) + ": " + datetime.datetime.now().strftime("%A, %d. %B %Y %I:%M:%S%p"))
        
    if queens_chess_piece.lower() == 'workerbee': # return tics
        s = datetime.datetime.now()
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
        print(queens_chess_piece, str((e - s)) + ": " + datetime.datetime.now().strftime("%A, %d. %B %Y %I:%M:%S%p"))

# >>> Buy Sell Weights 

# >>> NEED TO FIX the return for each time interval, rebuild 5 Min, 1 hr...etc....Put rebuild charts into new dict where they get maintained...add logic for each interval...i.e. on 5Min Mark rebuild with Initiate OR replace last 5 Minutes....?


#### >>>>>>>>>>>>>>>>>>> END <<<<<<<<<<<<<<<<<<###