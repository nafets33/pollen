
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

# Client Tickers
src_root, db_dirname = os.path.split(db_root)
client_ticker_file = os.path.join(src_root, 'client_tickers.csv')
df_client = pd.read_csv(client_ticker_file, dtype=str)
client_symbols = df_client.tickers.to_list()

main_root = os.getcwd()
db_root = os.path.join(main_root, 'db')
castle = ReadPickleData(pickle_file=os.path.join(db_root, 'castle.pkl'))
bishop = ReadPickleData(pickle_file=os.path.join(db_root, 'bishop.pkl'))  
if castle == False or bishop == False:
    print("Failed in Reading of Castle of Bishop Pickle File")
else:
    pollenstory = {**bishop['pollenstory'], **castle['pollenstory']} # combine daytrade and longterm info
# p = pollen_story(pollen_nectar=pollenstory, QUEEN=QUEEN) # re run story

spy = pollenstory['SPY_1Minute_1Day']

r = rebuild_timeframe_bars(ticker_list=client_symbols, build_current_minute=False, min_input=0, sec_input=30) # return all tics
resp = r['resp'] # return slope of collective tics
df = resp[resp['symbol']=='GOOG'].copy()
df = df.reset_index()
df_len = len(df)
if df_len > 2:
    df['price_delta'] = df['price'].rolling(window=2).apply(lambda x: x.iloc[1] - x.iloc[0]).fillna(0)
    slope, intercept, r_value, p_value, std_err = stats.linregress(df.index, df['price'])
    # slope1, intercept, r_value, p_value, std_err = stats.linregress(df.index, df['price_delta'])
else:
    print(df)
print(slope)
# print(slope1)
print(sum(df['price_delta'].tail(int(round(df_len/2,0)))))



r = rebuild_timeframe_bars(ticker_list=client_symbols, build_current_minute=False, min_input=0, sec_input=30) # return all tics
resp = r['resp'] # return slope of collective tics
for symbol in set(resp['symbol'].to_list()):
    df = resp[resp['symbol']==symbol].copy()
    df = df.reset_index()
    df_len = len(df)
    rolling_times = [round(df_len / 4), round(df_len / 2)]
    df = return_sma_slope(df=df, y_list=['price'], time_measure_list=rolling_times)
# add weight to index each new index greater weight
index_max = df_len
df['index_weight'] = df

# return change 
df['price_delta'] = df['price'].rolling(window=2).apply(lambda x: x.iloc[1] - x.iloc[0])
df['price_delta_pct'] = df['price'].rolling(window=2).apply(lambda x: (x.iloc[1] - x.iloc[0])/ x.iloc[0])


def return_degree_angle(x, y):
    # 45 degree angle
    # x = [1, 2, 3]
    # y = [1, 2, 3]

    #calculate
    degree = np.math.atan2(y[-1] - y[0], x[-1] - x[0])
    degree = np.degrees(degree)

    return degree


def return_ema_slope(df, y_list, time_measure_list):
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

# Momementem 2 ways, 2 way is much faster
# 1.
df['momentum'] = np.where(df['price_delta'] > 0, 1, -1)
df['3_day_momentum'] = df.momentum.rolling(3).mean()

# 2.
from scipy.ndimage import uniform_filter1d
def rolling_mean(ar, W=3):
    hW = (W-1)//2
    out = uniform_filter1d(momentum.astype(float), size=W, origin=hW)
    out[:W-1] = np.nan
    return out

momentum = 2*(df['price_delta'] > 0) - 1
df['out'] = rolling_mean(momentum, W=3)

# this works but not sure how it compares???
alpha = 0.1    # This is my smoothing parameter
window = 24
weights = list(reversed([(1-alpha)**n for n in range(window)]))
def f(w):
    def g(x):
        return sum(w*x) / sum(w)
    return g
T_ = pd.DataFrame()
T_ = df['price'].rolling(window=24).apply(f(weights))
T_ = T_.dropna()

def pct_delta(price_list):
    # return pct change from prior value
    # l = [1,1.2,1,2,2.5,3,1,1.2,1.3,1.4,1.6,1.8,1.4,1.5,2,2,3,1]
    l = price_list
    final = []
    for i, value in enumerate(l):
        if i < 1:
            final.append(0)
        else:
            prior_value = l[i-1]
            if prior_value==0 or value==0:
                final.append(0)
            else:
                pct_change_from_prior = round((value - prior_value) / value, 10)
                final.append(pct_change_from_prior)
    return final
pct_change = pct_delta(df['price'].values)


# df['pct_change'] = df['price'].apply(lambda x: pct_delta(x))

distribution = df['price']
weights = df['size']
def weighted_average_m1(distribution, weights):
  
    numerator = sum([distribution[i]*weights[i] for i in range(len(distribution))])
    denominator = sum(weights)
    
    return round(numerator/denominator,2)

weighted_average_m1(distribution, weights)


from pykalman import KalmanFilter

spy = pollenstory['SPY_1Day_1Year']
kf = KalmanFilter(transition_matrices = [1],
                  observation_matrices = [1],
                  initial_state_mean = 0,
                  initial_state_covariance = 1,
                  observation_covariance = 1,
                  transition_covariance = 0.0001)
mean, cov = kf.filter(spy['close'].values)
mean, std = mean.squeeze(), np.std(cov.squeeze())
plt.figure(figsize=(12,6))
plt.plot(spy['close'].values - mean, 'red', lw=1.5)
plt.show()


# df = from above last 30 seconds pull
kf = KalmanFilter(transition_matrices = [1],
                  observation_matrices = [1],
                  initial_state_mean = 0,
                  initial_state_covariance = 1,
                  observation_covariance = 1,
                  transition_covariance = 0.0001)
mean, cov = kf.filter(df['price'].values)
mean, std = mean.squeeze(), np.std(cov.squeeze())
plt.figure(figsize=(12,6))
plt.plot(df['price'].values - mean, 'red', lw=1.5)
plt.show()

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


def rebuild_timeframe_bars(ticker_list, build_current_minute=False, min_input=False, sec_input=False):
    # ticker_list = ['IBM', 'AAPL', 'GOOG', 'TSLA', 'MSFT', 'FB']
    try:
        # First get the current time
        if build_current_minute:
            current_time = datetime.datetime.now()
            current_sec = current_time.second
            if current_sec < 5:
                time.sleep(1)
                current_time = datetime.datetime.now()
                sec_input = current_time.second
                min_input = 0
        else:
            sec_input = sec_input
            min_input = min_input

        current_time = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
        previous_time = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(minutes=min_input, seconds=sec_input)).strftime('%Y-%m-%dT%H:%M:%SZ')

        def has_condition(condition_list, condition_check):
            if type(condition_list) is not list: 
                # Assume none is a regular trade?
                in_list = False
            else:
                # There are one or more conditions in the list
                in_list = any(condition in condition_list for condition in condition_check)

            return in_list

        exclude_conditions = [
        'B','W','4','7','9','C','G','H',
        'I','M','N','P','Q','R','T', 'U', 'V', 'Z'
        ]
        # Fetch trades for the X seconds before the current time
        trades_df = api.get_trades(ticker_list,
                                    start=previous_time,
                                    end=current_time, 
                                    limit=30000).df
        # convert to market time for easier reading
        trades_df = trades_df.tz_convert('America/New_York')

        # add a column to easily identify the trades to exclude using our function from above
        trades_df['exclude'] = trades_df.conditions.apply(has_condition, condition_check=exclude_conditions)

        # filter to only look at trades which aren't excluded
        valid_trades = trades_df.query('not exclude')
        # print(len(trades_df), len(valid_trades))
        # x=trades_df['conditions'].to_list()
        # y=[str(i) for i in x]
        # print(set(y))
        if build_current_minute:
            minbars_dict = {}
            for ticker in ticker_list:
                df = valid_trades[valid_trades['symbol']==ticker].copy()
                # Resample the trades to calculate the OHLCV bars
                agg_functions = {'price': ['first', 'max', 'min', 'last'], 'size': ['sum', 'count']}
                min_bars = df.resample('1T').agg(agg_functions)
                min_bars = min_bars.droplevel(0, 'columns')
                min_bars.columns=['open', 'high', 'low' , 'close', 'volume', 'trade_count']
                min_bars = min_bars.reset_index()
                min_bars = min_bars.rename(columns={'timestamp': 'timestamp_est'})
                minbars_dict[ticker] = min_bars
                return {'resp': minbars_dict}
        else:
            return {'resp': valid_trades}
    except Exception as e:
        print("rebuild_timeframe_bars", e)
        return {'resp': False, 'msg': [e, current_time, previous_time]}
# r = rebuild_timeframe_bars(ticker_list, sec_input=30)


def QueenBee(): # Order Management
    acc_info = 	refresh_account_info(api)
    open_orders = 
    num_of_trades = 
    day_profitloss = 
    max_num_of_trades = 10
    happy_ending = .02 #2%
    bee_ticks = # current tick momentum
    bee_1min = # current momentum (use combination of RSI, MACD to Determine weight of BUY/SELL)
    bee_5min = # current momentum (use combination of RSI, MACD to Determine weight of BUY/SELL)
    bee_1month = # current momentum (use combination of RSI, MACD to Determine weight of BUY/SELL)
    bee_3month = # current momentum (use combination of RSI, MACD to Determine weight of BUY/SELL)
    bee_6month = # current momentum (use combination of RSI, MACD to Determine weight of BUY/SELL)
    bee_1yr = # current momentum (use combination of RSI, MACD to Determine weight of BUY/SELL)

    if open_orders: # based on indicators decide whether to close position
        open_orders_bee_manager(orders)