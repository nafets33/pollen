
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
import math
import matplotlib.pyplot as plt



prod = True
pd.options.mode.chained_assignment = None
est = pytz.timezone("US/Eastern")
load_dotenv()
# >>> initiate db directories
system = 'windows' #mac, windows
if system != 'windows':
    db_root = os.environ.get('db_root_mac')
else:
    db_root = os.environ.get('db_root_winodws')

QUEEN = { # The Queens Mind
    'pollenstory': {}, # latest story
    'pollencharts': {}, # latest rebuild
    'pollencharts_nectar': {}, # latest charts with indicators
    'pollenstory_info': {}, # Misc Info,
    'self_last_modified' : datetime.datetime.now(),
    }

db_root = os.environ.get('db_root_winodws')

# read bishop daya
queens_chess_piece = 'bishop'
PB_Story_Pickle = os.path.join(db_root, f'{queens_chess_piece}{".pkl"}')
r = ReadPickleData(pickle_file=PB_Story_Pickle)
pollenstory = r['pollenstory']

p = pollen_story(pollen_nectar=pollenstory, QUEEN=QUEEN)


spy = p['pollen_story']['SPY_1Minute_1Day']
# spy['f'] = spy['timestamp_est'].apply(lambda x: x.day==29)==True
# spy = spy[spy['f']==True]

# remove past day from 1 min 
yesterday = datetime.datetime.now() - timedelta(days=1)
datetime.datetime.strptime(yesterday, "%Y-%m-%d")
spy=spy[spy['timestamp_est'] > "2022-04-29"]
spy=spy[spy['timestamp_est'] < yesterday.isoformat()].copy()  # WORKS

# t = spy[["macd", "seq_macd", "running_macd", "tier_macd"]]
def linear_regression(pollenstory, x_list, y_list, regression_times, init=False):
    s = datetime.datetime.now()
    # if init=True then run ALL Linear Regression Timeframes and variables 
        # ELSE run select

    x_value = 'timestamp_est'
    y_list = ['macd', 'close', 'signal', 'hist'] # do we care for signal?
    # y_list = ['hist'] # do we care for signal?
    regression_times = [4, 5, 10, 20, 33, 63]
    # df['index'] = df.index # set index as column
    # df_len = len(df)
    regression_times.append('token')
    init = True
    regression_return = {}
    # if init:
    #     regression_times = reg
    for ticker_time, df in pollenstory.items():
        df['x_values'] = df['timestamp_est'].apply(lambda x: str(x))
        df_len = len(df)
        df['index'] = df.index # set index as column
        regression_times = regression_times[:-1]# drop token
        regression_times.append(df_len) # add full df

        regression_return[ticker_time] = {}
        for time in regression_times:
            for main_value in y_list:
                if time == df_len:
                    name = f'{"0"}{"_"}{main_value}'
                else:
                    name = f'{time}{"_"}{main_value}'
                # ipdb.set_trace()
                # x = df[x_value].to_list()[df_len-time:df_len-1]
                x = [i for i in range(time)]
                # x = df['x_values'].to_list()[df_len-time:df_len]
                y = df[main_value].to_list()[df_len-time:df_len]
                # regression_results = linregress(x, y)
                # 

                # regression_return[name] = regression_results
                # slope, intercept, r_value, p_value, std_err = linregress(x, y)
                slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)

                regression_results = {'slope': slope, 'intercept': intercept, 
                'r_value': r_value, 'p_value':p_value, 'std_err':std_err}
                add_results = {name: regression_results}
                regression_return[ticker_time].update(add_results)

    kme = regression_return['SPY_1Minute_1Day']
    print({k: v['slope'] for k,v in kme.items() if 'hist' in k})
    print({k: v['slope'] for k,v in kme.items() if 'close' in k})
    e = datetime.datetime.now()
    msg = {'function':'linear_regression',  'func_timeit': str((e - s)), 'datetime': datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S_%p')}
    print([i for i in msg])
    return regression_return
    # return regression
    # cannot exceed current length of chart
r=linear_regression(pollenstory=pollenstory, x_list=None, y_list=['macd', 'hist'], regression_times=[3, 5, 10, 20, 33, 63], init=False)
sp = r['SPY_5Minute_5Day']
# ORRR filter directly with index, use ... depends if its faster?



spy = pollenstory['SPY_1Minute_1Day']
btc = spy
btc['sma20'] = btc.rolling(20).mean()['close']
btc['slope'] = np.degrees(np.arctan(btc['sma20'].diff()/20))
btc = btc[['close','sma20','slope']].copy()
c=btc[['close','sma20']].plot(figsize=(14,7))
c=btc[['slope']].plot(figsize=(14,7))
plt.show()


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

# read bishop daya
queens_chess_piece = 'bishop'
PB_Story_Pickle = os.path.join(db_root, f'{queens_chess_piece}{".pkl"}')
r = ReadPickleData(pickle_file=PB_Story_Pickle)
pollenstory = r['pollenstory']
spy = pollenstory['SPY_1Minute_1Day']
btc = spy
btc['sma20'] = btc.rolling(3).mean()['hist']
btc['slope'] = np.degrees(np.arctan(btc['sma20'].diff()/3))
btc = btc[['timestamp_est', 'close', 'hist','sma20','slope']].copy()
btc.tail(10)
t = btc.set_index('timestamp_est')
t = t.between_time('13:00', '13:12')
t
btc[['close','sma20']].plot(figsize=(14,7))
btc[['slope']].plot(figsize=(14,7))
plt.show()

# return by prior times
spy = spy.set_index('timestamp_est')
last_time = spy.iloc[-1].name # current datetime value since time is index
min_input = 5
sec_input = 0
previous_time = (last_time - datetime.timedelta(minutes=min_input, seconds=sec_input)).strftime('%Y-%m-%dT%H:%M:%SZ')
t = spy.between_time('9:30', '10:30')
t = spy.between_time('9:50', '9:56')

t = t.reset_index()
x = t["index"].to_list()
y = t["hist"].to_list()


a=linregress(x, y)
# a=linregress(y, x) # hello flip me Buzzzt.?

slope, intercept, r_value, p_value, std_err = linregress(x, y)


# from QueenBishop import QUEEN


# r["pollencharts"][ticker_time].tail(3).timestamp_est
# r["pollencharts"]['SPY_5Minute_5Day'].tail(3).timestamp_est

# c= 0
# while True:
#     PB_Story_Pickle
#     r = ReadPickleData(pickle_file=PB_Story_Pickle)
#     if r == False:
#         time.sleep(1)
#         r = ReadPickleData(pickle_file=PB_Story_Pickle)
#     print("<<<<<<<<<<--------------------------->>>>>>>>>>")

    # print(">>>1Min")
    # one = r["pollencharts"]['SPY_1Minute_1Day']
    # print(one[['close', 'timestamp_est']].tail(3))

#     one_n = r["pollenstory"]['SPY_1Minute_1Day']
#     t = one_n.tail(5)
#     print(one_n[['macd_cross', 'tier_macd', 'tier_signal', 'tier_hist', 'timestamp_est']].tail(2))
#     print("----")
#     print(one_n[['macd', 'signal', 'hist']].tail(2))

#     # print(">>>5Min")
#     # five = r["pollencharts"]['SPY_5Minute_5Day']
#     # print(five[['close', 'timestamp_est']].tail(3))
    

#     # print(">>>30Min1Month")
#     # one = r["pollencharts"]['SPY_30Minute_1Month']
#     # print(one[['close', 'timestamp_est']].tail(3))


#     c+=1
#     time.sleep(1)


# Index(['open', 'high', 'low', 'close', 'volume', 'trade_count', 'vwap',
#        'symbol', 'timestamp_est', 'vwap_original', 'rsi_ema', 'rsi_sma',
#        'rsi_rma', 'macd', 'signal', 'hist', 'story_index', 'tier_macd',
#        'tier_macd_range-high', 'tier_macd_range-low', 'tier_signal',
#        'tier_signal_range-high', 'tier_signal_range-low', 'tier_hist',
#        'tier_hist_range-high', 'tier_hist_range-low', 'seq_macd',
#        'running_macd', 'seq_signal', 'running_signal', 'seq_hist',
#        'running_hist', 'macd_cross', 'name'],
#       dtype='object')

#       # Assuming that dataframes df1 and df2 are already defined:
# print "Dataframe 1:"
# display(spy)
# print "Dataframe 2:"
# display(HTML(spy.to_html()))
