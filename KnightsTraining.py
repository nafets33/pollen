
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
import mplfinance as mpf

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



prod = True
pd.options.mode.chained_assignment = None
est = pytz.timezone("US/Eastern")
load_dotenv()
# >>> initiate db directories
system = 'windows' #mac, windows
# if system != 'windows':
#     db_root = os.environ.get('db_root_mac')
# else:
#     db_root = os.environ.get('db_root_winodws')

QUEEN = { # The Queens Mind
    'pollenstory': {}, # latest story
    'pollencharts': {}, # latest rebuild
    'pollencharts_nectar': {}, # latest charts with indicators
    'pollenstory_info': {}, # Misc Info,
    'self_last_modified' : datetime.datetime.now(),
    }

main_root = os.getcwd()
db_root = os.path.join(main_root, 'db')
# Client Tickers
src_root, db_dirname = os.path.split(db_root)
client_ticker_file = os.path.join(src_root, 'client_tickers.csv')
df_client = pd.read_csv(client_ticker_file, dtype=str)
client_symbols = df_client.tickers.to_list()


# if queens_chess_piece.lower() == 'knight': # Read Bees Story
# Read chart story data
castle = ReadPickleData(pickle_file=os.path.join(db_root, 'castle.pkl'))
bishop = ReadPickleData(pickle_file=os.path.join(db_root, 'bishop.pkl'))  
if castle == False or bishop == False:
    msg = ("Failed in Reading of Castle of Bishop Pickle File")
    print(msg)
    logging.warning(msg)
    # continue
else:
    pollenstory = {**bishop['bishop']['pollenstory'], **castle['castle']['pollenstory']} # combine daytrade and longterm info
    # make recording of last modified
    lastmod = bishop["last_modified"]["last_modified"]
    if lastmod > QUEEN["self_last_modified"]:
        QUEEN["self_last_modified"] = lastmod
        spy = pollenstory['SPY_1Minute_1Day']
        print(spy[['macd_cross', 'macd_slope-3', 'close_slope-3', 'macd', 'nowdate']].tail(5))
        
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


        prod = 'sandbox'
        # >>> >>>> macd_buy_cross <<< <<<
            # cross = buy
            # hist slope 3 is positive, > .033%
            # close slope 3 is positive > .033%
            # macd slope is positive > .033%
        # macd is low, sum past 2 macds lower then -1 and current 2 > then -1 (past Num(3,6,10) degree angle: V )
        # macd peaked or macd peaked in past 3 (take sum of past 3 and measure middle dveation from -2 vs 0)
        def knight_sight():
            trigger_dict = {}
            symbol = spy
            symbol['macd_buy_cross'] = np.where(
                (symbol['macd_cross'] == 'buy_cross') & 
                (symbol['hist_slope-3'] > .033) | (symbol['hist_slope-6'] > .01) &
                (symbol['close_slope-3'] > .033) &
                (symbol['macd_slope-3'] > .033),
                't', # queens_order_managment(prod), # execute order managment to be considered to place order
                'nothing') # do nothing
            t = symbol[symbol['macd_buy_cross']=='t'].copy()
            if symbol['macd_buy_cross'].iloc[-1] == 't':
                trigger_dict['macd_buy_cross'] = 't'

            # Mac is very LOW and the prior hist slow was steep and we are not in a BUY CROSS Cycle Yet
            symbol['buy_high-deviation'] = np.where(
                (symbol['macd_cross'].str.contains("buy_hold")==False) & # is not in BUY cycle
                (symbol['macd'] < -1.5) &
                (symbol['macd_slope-3'] > .33)&
                (symbol['hist_slope-3'] > .3) |(symbol['hist_slope-6'] > .10) 
                ,"t2", 'nothing'
            )
            if symbol['macd_buy_cross'].iloc[-1] == 't':
                trigger_dict['macd_buy_cross'] = 't'


            np.where(
                (symbol['vwap'] < - 3) # 
                ,"vwap_deivation", 'nothing'
            )
        
            return {"df": df, "bee_triggers": trigger_dict}

def queens_conscience():
    # what time is it? Block of Day? [9-9:30, 10-11, 11-1,1-3,3-4]
    # read triggers
    # validate triggers
    # pass to order function

        
        e = datetime.datetime.now()
        print("knight", str((e - s)) + ": " + datetime.datetime.now().strftime("%A, %d. %B %Y %I:%M:%S%p"))

spy = pollenstory['SPY_1Minute_1Day']



c = spy
c2 = c[:120].copy()
c3=c2[['hist','hist_sma-3','hist_slope-3', 'hist_slope-6']].copy()
c=c2[['hist','hist_slope-3', 'hist_slope-6']].plot(figsize=(14,7))
# c=spy[['slope']].plot(figsize=(14,7))
plt.show()
t['t'] = np.where(t['macd'] > 0, t['macd'][0] + t['macd'][:-1], '')

spy = pollenstory['SPY_5Minute_5Day']

df_apple = spy

x = np.arange(0,len(df_apple))
fig, (ax, ax2) = plt.subplots(2, figsize=(12,8), gridspec_kw={'height_ratios': [4, 1]})
for idx, val in df_apple.iterrows():
    color = '#2CA453'
    if val['open'] > val['close']: color= '#F04730'
    ax.plot([x[idx], x[idx]], [val['low'], val['high']], color=color)
    ax.plot([x[idx], x[idx]-0.1], [val['open'], val['open']], color=color)
    ax.plot([x[idx], x[idx]+0.1], [val['close'], val['close']], color=color)
    
# ticks top plot
ax2.set_xticks(x[::3])
ax2.set_xticklabels(df_apple.timestamp_est.dt.timestamp_est[::3])
ax.set_xticks(x, minor=True)
# labels
ax.set_ylabel('USD')
ax2.set_ylabel('Volume')
# grid
ax.xaxis.grid(color='black', linestyle='dashed', which='both', alpha=0.1)
ax2.set_axisbelow(True)
ax2.yaxis.grid(color='black', linestyle='dashed', which='both', alpha=0.1)
# remove spines
ax.spines['right'].set_visible(False)
ax.spines['left'].set_visible(False)
ax.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)
ax2.spines['left'].set_visible(False)
# plot volume
ax2.bar(x, df_apple['volume'], color='lightgrey')
# get max volume + 10%
mx = df_apple['volume'].max()*1.1
# define tick locations - 0 to max in 4 steps
yticks_ax2 = np.arange(0, mx+1, mx/4)
# create labels for ticks. Replace 1.000.000 by 'mi'
yticks_labels_ax2 = ['{:.2f} mi'.format(i/1000000) for i in yticks_ax2]
ax2.yaxis.tick_right() # Move ticks to the left side
# plot y ticks / skip first and last values (0 and max)
plt.yticks(yticks_ax2[1:-1], yticks_labels_ax2[1:-1])
plt.ylim(0,mx)
 
# title
ax.set_title('Apple Stock Price\n', loc='left', fontsize=20)
# no spacing between the subplots
plt.subplots_adjust(wspace=0, hspace=0)
plt.show()

# worker bee
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





# return change 
df['price_delta'] = df['price'].rolling(window=2).apply(lambda x: x.iloc[1] - x.iloc[0])
df['price_delta_pct'] = df['price'].rolling(window=2).apply(lambda x: (x.iloc[1] - x.iloc[0])/ x.iloc[0])



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
def kalmanfilter():
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


def filterout_priorday(df, timeindex=False):# remove past day from 1 min 
    yesterday = datetime.datetime.now() - timedelta(days=1)
    # datetime.datetime.strptime(yesterday, "%Y-%m-%d")
    # df=df[df['timestamp_est'] > "2022-04-29"]
    df=df[df['timestamp_est'] < yesterday.isoformat()].copy()  # WORKS
    return df

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











### SAVE ###

def bullish_engulfing(data):
     open_p = list(data['open'])
     close_p = list(data['close'])
     tmp = close_p[-10:]
     dec_seq = lds(tmp, len(tmp))
     
     DECREASING_FACTOR = 0.65
     if(dec_seq/len(tmp) >= DECREASING_FACTOR):
          if(open_p[-1] < close_p[-1] and open_p[-2] > close_p[-2] and open_p[-1] < close_p[-2] and close_p[-1] > open_p[-2]):
               return True
          return False
     return False
    


slope, intercept, r_value, p_value, std_err = linregress(x, y)


def pollenstory():
    castle = ReadPickleData(pickle_file=os.path.join(db_root, 'castle.pkl'))
    bishop = ReadPickleData(pickle_file=os.path.join(db_root, 'bishop.pkl'))
    pollenstory = {**bishop['bishop']['pollenstory'], **castle['castle']['pollenstory']} # combine daytrade and longterm info
    return pollenstory


pollenstory = pollenstory()
df = pollenstory['SPY_1Minute_1Day']
df = df.set_index('timestamp_est')
df_t = df.between_time('11:00', '11:12')
df_t = df_t[df_t.index.day == 27]

df_t['prior_slopedelta'] = (df_t['macd_slope-3'] - df_t['macd_slope-3'].shift(1)).fillna(0)

p=plt.figure(figsize=(12,6))
p=plt.plot(df_t[['macd', 'macd_slope-3', 'prior_slopedelta']], lw=1.5)
# plt.show()


# prior slope delta


