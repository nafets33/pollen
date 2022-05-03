
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

spy['index'] = spy.index 
# ORRR filter directly with index, use ... depends if its faster?

x = spy["index"].to_list()[:100]
y = spy["hist"].to_list()[:100]

# 

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
