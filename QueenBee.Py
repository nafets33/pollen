import logging
from enum import Enum
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
from Hive_Utils import return_api_keys, read_csv_db, refresh_account_info, return_bars, return_snapshots, init_index_ticker
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

# trade closer to ask price .... sellers closer to bid .... measure divergence from bid/ask to give weight


pd.options.mode.chained_assignment = None

est = pytz.timezone("US/Eastern")

system = 'windows' #mac, windows
load_dotenv()

if system != 'windows':
    db_root = os.environ.get('db_root_mac')
else:
    db_root = os.environ.get('db_root_winodws')

# logging.basicConfig(
# 	filename='QueenBee.log',
# 	level=logging.WARNING,
# 	format='%(asctime)s:%(levelname)s:%(message)s',
# )

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
current_day = api.get_clock().timestamp.date().isoformat()
trading_days = api.get_calendar()
trading_days_df = pd.DataFrame([day._raw for day in trading_days])

start_date = datetime.datetime.now().strftime('%Y-%m-%d')
end_date = datetime.datetime.now().strftime('%Y-%m-%d')

"""# Main Arguments """
num = {1: .15, 2: .25, 3: .40, 4: .60, 5: .8}
client_num_LT = 1
client_num_ST = 3
client_days1yrmac_input = 233 # Tier 1
client_daysT2Mac_input = 5 # Tier 2
client_daysT3Mac_input = 233 # Tier 3

# client_num_LT = sys.argv[1]
# client_num_ST = sys.argv[2]
# client_days1yrmac_input = sys.argv[3]

"""# Customer Setup """
Long_Term_Client_Input = num[client_num_LT]
MidDayLag_Alloc = num[client_num_ST]
DayRiskAlloc = 1 - (Long_Term_Client_Input + MidDayLag_Alloc)


""" Return Tickers of SP500 & Nasdaq / Other Tickers"""

client_symbols = ['SPY', 'SPDN', 'SPXU', 'SPXL', 'TQQQ', 'SQQQ', 'AAPL', 'GOOG', 'VIX']
LongTerm_symbols = ['AAPL', 'GOOGL', 'MFST', 'VIT', 'HD', 'WMT', 'MOOD', 'LIT', 'SPXL', 'TQQQ']
BeeHunter = {
    'LongX3': {'TQQQ': 'TQQQ', 'SPXL': 'SPXL'},
    'ShortX3': {'SQQQ':'SQQQ', 'SPXU': 'SPXU'},
    'Long':  {'SPY': 'SPY', 'QQQQ': 'QQQQ'}
}

index_list = [
    'DJA', 'DJI', 'DJT', 'DJUSCL', 'DJU',
    'NDX', 'IXIC', 'IXCO', 'INDS', 'INSR', 'OFIN', 'IXTC', 'TRAN', 'XMI', 
    'XAU', 'HGX', 'OSX', 'SOX', 'UTY',
    'OEX', 'MID', 'SPX',
    'SCOND', 'SCONS', 'SPN', 'SPF', 'SHLTH', 'SINDU', 'SINFT', 'SMATR', 'SREAS', 'SUTIL']


# Create DB folder if needed
index_ticker_db = os.path.join(db_root, "index_tickers")
if os.path.exists(index_ticker_db) == False:
    os.mkdir(index_ticker_db)
    print("Ticker Index db Initiated")
    init_index_ticker(index_list, db_root, init=True)


#LongTerm_symbols = ?Weight Each Symbol? or just you assests and filter on Market Cap & VOL SECTOR, EBITDA, Free Cash Flow

"""Account Infomation """
acc_info = 	refresh_account_info(api)

# Main Alloc
portvalue_LT_iniate = acc_info[1]['portfolio_value'] * Long_Term_Client_Input
portvalue_MID_iniate = acc_info[1]['portfolio_value'] * MidDayLag_Alloc
portvalue_BeeHunter_iniate = acc_info[1]['portfolio_value'] * DayRiskAlloc


# check alloc correct
if round(portvalue_BeeHunter_iniate + portvalue_MID_iniate + portvalue_LT_iniate - acc_info[1]['portfolio_value'],4) > 1:
    print("break in Rev Alloc")
    sys.exit()



"""TICKER Calculation Functions"""
def append_MACD(df, fast, slow):
    # fast=12
    # slow=26
    macd = df.ta.macd(close='close', fast=fast, slow=slow, append=True) 
    return macd


def return_VWAP(df):
    # VWAP
    df = df.assign(
        vwap=df.eval(
            'wgtd = close * volume', inplace=False
        ).groupby(df['timestamp']).cumsum().eval('wgtd / volume')
    )
    return df


def return_RSI(df, length):
    # Define function to calculate the RSI
    length = 14 # test

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
    # Reminder: Provide ≥ `1 + length` extra data points!
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


"""TICKER ChartData Functions"""
def return_getbars_WithIndicators(symbol, time, ndays, trading_days_df=trading_days_df):
    # time = '1Minute' #TEST
    # symbol = 'SPY' #TEST

    s = datetime.datetime.now() #TEST
    m = return_bars(symbol=symbol, time=time, ndays=ndays, trading_days_df=trading_days_df)
    mk_hrs_data = m[1] # market hours data frame only (0 = all, 1=mk hours, 3=afterhours)
    mk_hrs_data['vwap_original'] = mk_hrs_data['vwap']
    # del mk_hrs_data['vwap']
    df_vwap = return_VWAP(mk_hrs_data)
    df_vwap_rsi_macd = return_RSI(df=df_vwap, length=14)
    append_MACD(df_vwap_rsi_macd, fast=12, slow=16)
    e = datetime.datetime.now()
    # print(str((e - s)) + ": " + datetime.datetime.now().strftime("%A, %d. %B %Y %I:%M%p"))
    # 0:00:00.198920: Monday, 21. March 2022 03:02PM 2 days 1 Minute
    return df_vwap_rsi_macd
# bee = return_getbars_WithIndicators(symbol="SPY", time="1Minute", ndays=1)


def Rebuild_bar_with_latest(symbols, df):
    snapshot = return_snapshots(ticker_list=symbols)


def open_orders_bee_manager(orders):
    # order is open manage when trade will be closed
    return True


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



"""Iniaite Ticker Charts with Indicators"""
s = datetime.datetime.now()
dfs_index_tickers = {}
main_index_tickers = ['SPY', 'QQQ']
chart_times = {"1Minute": 1, "5Minute": 5, "30Minute": 18, "1Hour": 48, "2Hour": 72, "1Day": 233}
for ticker in main_index_tickers:
    for time_frames, times in chart_times.items():
        try:
            bee = return_getbars_WithIndicators(symbol=ticker, time=time_frames, ndays=times)
            name = ticker + "_" + time_frames
            dfs_index_tickers[name] = bee
        except Exception as e:
            print(e)
            print(ticker, time_frames, times)
e = datetime.datetime.now()
print(str((e - s)) + ": " + datetime.datetime.now().strftime('%Y-%m-%d %H:%M'))

# Rebuild Current Bar for Each timeframe 1Min, 5Min, 30min, 1hr, 2hr, 1day
spy_1min = dfs_index_tickers['SPY_5Minute']

a = 0
while True:
    return_last_trade_price
    if last_trade_price_min - ticker_last_trade_price_min > 2:
        refresh(ticker_data)
    
    re_build_charts(last_trade_price) # return all new objects (allowed obj based on how many pr may return wihtin the minute)

    order_managment(ticker_obj_list)


# return VIX


def return_db(csv_name, symbol):
    symbol = True
    csv_name = "SPY_bars.csv"
    symbol, filename = csv_name.split("_")
    type='bars'
    db = read_csv_db(db_root=(os.path.join((os.getcwd()), 'db')), type=type, symbol=symbol)
    # symbol = 'SPY'
    perMin = tradeapi.TimeFrame(1, tradeapi.TimeFrameUnit.Minute) # every second
    FiveperMin = tradeapi.TimeFrame(5, tradeapi.TimeFrameUnit.Minute) # every second
    tday = tradeapi.TimeFrame(1, tradeapi.TimeFrameUnit.Day) # every day





# check before executing final Trade [distance between bid/ask, momentum value of ticker, momentum of market] 


#### >>>>>>>>>>>>>>>>>>> END <<<<<<<<<<<<<<<<<<###