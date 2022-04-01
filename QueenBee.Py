# QueenBee
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
from Hive_Utils import return_api_keys, read_csv_db, refresh_account_info, return_bars, return_snapshots, init_index_ticker, convert_Todatetime_return_est_stringtime
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


index_list = [
    'DJA', 'DJI', 'DJT', 'DJUSCL', 'DJU',
    'NDX', 'IXIC', 'IXCO', 'INDS', 'INSR', 'OFIN', 'IXTC', 'TRAN', 'XMI', 
    'XAU', 'HGX', 'OSX', 'SOX', 'UTY',
    'OEX', 'MID', 'SPX',
    'SCOND', 'SCONS', 'SPN', 'SPF', 'SHLTH', 'SINDU', 'SINFT', 'SMATR', 'SREAS', 'SUTIL']


get_bars_cols = ['timestamp', 'open', 'high', 'low', 'close', 'volume', 'trade_count', 'vwap', 'index_timestamp', 'timestamp_est_timestamp']


# Create DB folder if needed
index_ticker_db = os.path.join(db_root, "index_tickers")
if os.path.exists(index_ticker_db) == False:
    os.mkdir(index_ticker_db)
    print("Ticker Index db Initiated")
    init_index_ticker(index_list, db_root, init=True)


def return_timestamp_string():
    return datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S %p')


def return_index_tickers(db_root, ext):
    s = datetime.datetime.now()
    ext = '.csv'

    index_dict = {}
    index_dir = os.path.join(db_root, 'index_tickers')
    full_ticker_list = []
    all_indexs = [i.split(".")[0] for i in os.listdir(index_dir)]
    for i in all_indexs:
        df = pd.read_csv(os.path.join(index_dir, i+ext), dtype=str, encoding='utf8', engine='python')
        df = df.fillna('')
        tics = df['symbol'].tolist()
        for j in tics:
            full_ticker_list.append(j)
        index_dict[i] = df
    
    return [index_dict, list(set(full_ticker_list))]
# index_ticker_db = return_index_tickers(db_root, ext='.csv')

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
        ).groupby(df['timestamp_est']).cumsum().eval('wgtd / volume')
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
        df_vwap_rsi_macd = return_RSI(df=df_vwap, length=14)
        append_MACD(df_vwap_rsi_macd, fast=MACD['fast'], slow=MACD['slow'])
        e = datetime.datetime.now()
        # print(str((e - s)) + ": " + datetime.datetime.now().strftime("%A, %d. %B %Y %I:%M%p"))
        # 0:00:00.198920: Monday, 21. March 2022 03:02PM 2 days 1 Minute
        return [True, df_vwap_rsi_macd]
    except Exception as e:
        # print("log error")
            return [False, e]
# bee = return_getbars_WithIndicators(bars_data=)


def Return_Init_ChartData(ticker_list, chart_times): #Iniaite Ticker Charts with Indicator Data
    # ticker_list = ['SPY', 'QQQ']
    # chart_times = {"1Minute": 1, "5Minute": 5, "30Minute": 18, "1Hour": 48, "2Hour": 72, "1Day": 233}
    # MACD={'fast': 16, 'slow': 29} 
   
    error_dict = {}
    s = datetime.datetime.now()
    dfs_index_tickers = {}
    for ticker in tqdm(ticker_list):
        for time_frames, ndays in chart_times.items(): # 1day: 250, 1minute: 0
            try:
                bars_data = return_bars(symbol=ticker, time=time_frames, ndays=ndays, trading_days_df=trading_days_df) # return [True, symbol_data, market_hours_data, after_hours_data]
                df_bars_data = bars_data[2] # mkhrs if in minutes
                df_bars_data = df_bars_data.reset_index()
                if bars_data[0] == False:
                    error_dict["NoData"] = bars_data[1] # symbol already included in value
                else:
                    name = ticker + "_" + time_frames
                    dfs_index_tickers[name] = df_bars_data
            except Exception as e:
                print(e)
                print(ticker, time_frames, ndays)
    
    e = datetime.datetime.now()
    msg = {'function':'init_ticker_charts_data',  'func_timeit': str((e - s)), 'datetime': datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S_%p')}
    print(msg)
    # dfs_index_tickers['SPY_5Minute']
    return [dfs_index_tickers, error_dict]
# Return_Init_ChartData = init_ticker_charts_data(ticker_list=ticker_list, chart_times=chart_times)


def Return_Snapshots_Rebuild(df_tickers_data):
    ticker_list = list([set(j.split("_")[0] for j in df_tickers_data.keys())][0]) #> get list of tickers
    
    snapshots = api.get_snapshots(ticker_list)

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
            'vwap': snapshots[ticker].daily_bar.vwap
            }
            df_daily = pd.Series(dl).to_frame().T  # reshape dataframe
            for i in float_cols:
                df_daily[i] = df_daily[i].apply(lambda x: float(x))
            for i in int_cols:
                df_daily[i] = df_daily[i].apply(lambda x: int(x))
            df_daily = df_daily.rename(columns={'timestamp': 'timestamp_est'})
            
            return_dict[ticker + "_day"] = df_daily

            d = {'close': snapshots[ticker].minute_bar.close,
            'high': snapshots[ticker].minute_bar.high,
            'low': snapshots[ticker].minute_bar.low,
            'timestamp': snapshots[ticker].minute_bar.timestamp,
            'open': snapshots[ticker].minute_bar.open,
            'volume': snapshots[ticker].minute_bar.volume,
            'trade_count': snapshots[ticker].minute_bar.trade_count,
            'vwap': snapshots[ticker].minute_bar.vwap
            }
            df_minute = pd.Series(d).to_frame().T
            for i in float_cols:
                df_minute[i] = df_minute[i].apply(lambda x: float(x))
            for i in int_cols:
                df_minute[i] = df_minute[i].apply(lambda x: int(x))
            df_minute = df_minute.rename(columns={'timestamp': 'timestamp_est'})

            return_dict[ticker + "_minute"] = df_minute
        
        return return_dict
    snapshot_ticker_data = response_returned(ticker_list)

    for ticker, chartdata in df_tickers_data.items():
        # ticker = "SPY_5Minute"
        symbol_snapshots = {k:v for (k,v) in snapshot_ticker_data.items() if k.split("_")[0] == ticker.split("_")[0]}
        symbol, timeframe = ticker.split("_")
        if "Day" in timeframe:
            df_day_snapshot = symbol_snapshots[f'{symbol}{"_day"}'] # stapshot df
            df_rebuild = pd.concat([chartdata, df_day_snapshot]).reset_index() # concat minute
            df_rebuild = df_rebuild.reset_index()
            main_return_dict[ticker] = df_rebuild
        if "Minute" in timeframe:
            # chartdata = df_tickers_data["SPY_5Minute"]
            df_minute_snapshot = symbol_snapshots[f'{symbol}{"_minute"}'] # stapshot df
            df_rebuild = pd.concat([chartdata, df_minute_snapshot]).reset_index() # concat minute
            main_return_dict[ticker] = df_rebuild
            # assert ensure df is solid (dtypes are correct)

    return main_return_dict
# beer = Return_Snapshots_Rebuild(df_tickers_data)

    
def Return_ChartData_Rebuild(df_tickers_data, chart_times):
    df_tickers_data_rebuilt = Return_Snapshots_Rebuild(df_tickers_data=df_tickers_data)
    main_rebuild_dict = {} ##> only override current dict if memory becomes issues!
    for ticker_time, df_data in df_tickers_data_rebuilt.items():
        df_data_new = return_getbars_WithIndicators(bars_data=df_data, MACD={'fast': 12, 'slow': 26})
        if df_data_new[0] == True:
            main_rebuild_dict[ticker_time] = df_data_new[1]
    return main_rebuild_dict
# PollenBee_Charts = Return_ChartData_Rebuild(ticker_list=main_index_tickers, chart_times=chart_times)


"""
We All Shall prosper through the depths of our connected hearts,
Not all will share my world,
So I put forth my best mind of virtue and good 
Always bee better
"""
if '_name_' == '_main_':
    print("Buzz Buzz Where My Honey")
    QUEEN = {} # The Queens Mind

    s_mainbeetime = datetime.datetime.now()
    #LongTerm_symbols = ?Weight Each Symbol? or just you assests and filter on Market Cap & VOL SECTOR, EBITDA, Free Cash Flow
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
    for n, v in tqdm(enumerate(all_alpaca_tickers)):
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

    index_ticker_db = return_index_tickers(db_root, ext='.csv')
    
    main_index_dict = index_ticker_db[0]
    main_symbols_full_list = index_ticker_db[1]
    not_avail_in_alpaca =[i for i in main_symbols_full_list if i not in alpaca_symbols_dict]
    main_symbols_full_list = [i for i in main_symbols_full_list if i in alpaca_symbols_dict]

    client_symbols = ['SPY', 'SPDN', 'SPXU', 'SPXL', 'TQQQ', 'SQQQ', 'AAPL', 'GOOG', 'VIX'] # Should be from CSV file OR UI List from app
    LongTerm_symbols = ['AAPL', 'GOOGL', 'MFST', 'VIT', 'HD', 'WMT', 'MOOD', 'LIT', 'SPXL', 'TQQQ']
    BeeHunter = {
        'LongX3': {'TQQQ': 'TQQQ', 'SPXL': 'SPXL'},
        'ShortX3': {'SQQQ':'SQQQ', 'SPXU': 'SPXU'},
        'Long':  {'SPY': 'SPY', 'QQQQ': 'QQQQ'}
    }
    main_index_tickers = ['SPY', 'QQQ']
    """ Return Index Charts & Data for All Tickers Wanted"""
    """ Return Tickers of SP500 & Nasdaq / Other Tickers"""    
    
    """ Create Chart Data  BUZZ BUZZ """
    chart_times = {
        "1Minute": 1, "5Minute": 5, "30Minute": 18, 
        "1Hour": 48, "2Hour": 72, 
        "1Day": 250}
    
    
    """ Tell Story of Main Tickers #  # Return Readable Information about Tickers and Indicators """
    # >>> Initiate your Charts
    df_tickers_data = Return_Init_ChartData(ticker_list=main_index_tickers, chart_times=chart_times)
    errors = df_tickers_data[1]
    if errors:
        print("logme")
    df_tickers_data = df_tickers_data[0]
    # Initiate your Charts <<<
    PollenBee_Charts = Return_ChartData_Rebuild(df_tickers_data=df_tickers_data, chart_times=chart_times)
    """ >>># STORY: I want a dict of every ticker and the chart_time TRADE buy/signal weights """
    
    # >>> Continue to Rebuild ChartData
    # >>> Buy Sell Weights 
    
    e_mainbeetime = datetime.datetime.now()
    msg = {'Main':'Queen',  'block_timeit': str((e_mainbeetime - s_mainbeetime)), 'datetime': datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S_%p')}
    print(msg)


    # # >>> all tickers  # this should run as a night job and pickle the data to read for the morning?

    # s= datetime.datetime.now()
    # df = init_ticker_charts_data(ticker_list=main_symbols_full_list, chart_times={"1Day": 30}, MACD={'fast': 16, 'slow': 29})
    # errs = df[1]
    # main_ticker_chart_data = df[0]
    # e=datetime.datetime.now()
    # msg = {'function':'NA',  'func_timeit': str((e - s)), 'datetime': datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S_%p')}
    # print(msg)  # 8-10mins to return 7700 tickers for 1Day 233 days -  5Min, 5days 

    """# mark final times and return values"""
    e_mainbeetime = datetime.datetime.now()
    msg = {'Main':'Queen',  'block_timeit': str((e_mainbeetime - s_mainbeetime)), 'datetime': datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S_%p')}
    print(msg)

sys.exit()
def open_orders_beeManager(orders):
    
    def order_pulse(time_in_trade):
        decision = {}
        time_in_trade = 4 # 3 Mins
        return decision

    # order is open manage when trade will be closed
    time_trade_horizion = # guage on when to trade out (i.e. critical mass for profits)
    profit_take_block1 = .03 # % to sell
    profit_take_block2 = .05 # % to sell
    profit_take_ALL = # Full Position
    exit_trade_block1 = .02 # % to sell
    exit_trade_block2 = .02 # % to sell
    exit_trade_ALL = # Full Position
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

a = 0
while True:
    def Rebuild_bar_with_latest(ticker_list, chart_times):
        snapshots = api.get_snapshots(main_index_tickers)
        # ['daily_bar', 'latest_quote', 'latest_trade', 'minute_bar', 'prev_daily_bar']
        for tic in ticker_list:
            main_tic = 
            return_last_trade_price = snapshots[tic].latest_trade.price

    if last_trade_price_min - ticker_last_trade_price_min > 2:
        refresh(ticker_data)
    
    re_build_charts(last_trade_price) # return all new objects (allowed obj based on how many pr may return wihtin the minute)

    order_managment(ticker_obj_list)


each historgram bump by N:Value increases BUY (when Critial Mass of Weights agree to buy, you buy an allocation per chart and each has its own timeframe)


# return VIX





# def return_db(csv_name, symbol):
#     symbol = True
#     csv_name = "SPY_bars.csv"
#     symbol, filename = csv_name.split("_")
#     type='bars'
#     db = read_csv_db(db_root=(os.path.join((os.getcwd()), 'db')), type=type, symbol=symbol)
#     # symbol = 'SPY'
#     perMin = tradeapi.TimeFrame(1, tradeapi.TimeFrameUnit.Minute) # every second
#     FiveperMin = tradeapi.TimeFrame(5, tradeapi.TimeFrameUnit.Minute) # every second
#     tday = tradeapi.TimeFrame(1, tradeapi.TimeFrameUnit.Day) # every day





# check before executing final Trade [distance between bid/ask, momentum value of ticker, momentum of market] 


#### >>>>>>>>>>>>>>>>>>> END <<<<<<<<<<<<<<<<<<###