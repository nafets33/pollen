from asyncio import streams
from cgitb import reset
from datetime import datetime
import logging
from enum import Enum
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
import datetime
import pytz
from typing import Callable
import pickle
import random
from tqdm import tqdm
from stocksymbol import StockSymbol
import requests
from collections import defaultdict
# import talib
from scipy import stats
import shutil

prod = True
queens_chess_piece = os.path.basename(__file__)

main_root = os.getcwd()
db_root = os.path.join(main_root, 'db_local')

current_day = datetime.datetime.now().day
current_month = datetime.datetime.now().month
current_year = datetime.datetime.now().year

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
if os.path.exists(log_file) == False:
    logging.basicConfig(filename=f'{"log_"}{queens_chess_piece}{".log"}',
                        filemode='a',
                        format='%(asctime)s:%(name)s:%(levelname)s: %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p',
                        level=logging.INFO)
else:
    if loglog_newfile:
        # copy log file to log dir & del current log file
        datet = datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S_%p')
        dst_path = os.path.join(log_dir_logs, f'{log_name}{"_"}{datet}{".log"}')
        shutil.copy(log_file, dst_path) # only when you want to log your log files
        os.remove(log_file)
    else:
        logging.basicConfig(filename=f'{"log_"}{queens_chess_piece}{".log"}',
                            filemode='a',
                            format='%(asctime)s:%(name)s:%(levelname)s: %(message)s',
                            datefmt='%m/%d/%Y %I:%M:%S %p',
                            level=logging.INFO)


est = pytz.timezone("America/New_York")

system = 'windows' #mac, windows
load_dotenv()


exclude_conditions = [
    'B','W','4','7','9','C','G','H','I','M','N',
    'P','Q','R','T','U','V','Z'
]

# keys
api_key_id = os.environ.get('APCA_API_KEY_ID')
api_secret = os.environ.get('APCA_API_SECRET_KEY')
base_url = "https://api.alpaca.markets"


def return_api_keys(base_url, api_key_id, api_secret, prod=True):

    # api_key_id = os.environ.get('APCA_API_KEY_ID')
    # api_secret = os.environ.get('APCA_API_SECRET_KEY')
    # base_url = "https://api.alpaca.markets"
    # base_url_paper = "https://paper-api.alpaca.markets"
    # feed = "sip"  # change to "sip" if you have a paid account
    
    if prod == False:
        rest = AsyncRest(key_id=api_key_id,
                    secret_key=api_secret)

        api = tradeapi.REST(key_id=api_key_id,
                    secret_key=api_secret,
                    base_url=URL(base_url), api_version='v2')
    else:
        rest = AsyncRest(key_id=api_key_id,
                            secret_key=api_secret)

        api = tradeapi.REST(key_id=api_key_id,
                            secret_key=api_secret,
                            base_url=URL(base_url), api_version='v2')
    return [{'rest': rest, 'api': api}]

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

""" VAR >>>>>>>>>>VAR >>>>>>>>>>VAR >>>>>>>>>>VAR >>>>>>>>>>VAR >>>>>>>>>>VAR >>>>>>>>>>"""

""" STORY: I want a dict of every ticker and the chart_time TRADE buy/signal weights """
### Story

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


def speedybee(QUEEN, queens_chess_piece, ticker_list): # if queens_chess_piece.lower() == 'workerbee': # return tics
    ticker_list = ['AAPL', 'TSLA', 'GOOG', 'META']

    s = datetime.datetime.now()
    r = rebuild_timeframe_bars(ticker_list=ticker_list, build_current_minute=False, min_input=0, sec_input=30) # return all tics
    resp = r['resp'] # return slope of collective tics
    speedybee_dict = {}
    slope_dict = {}
    for symbol in set(resp['symbol'].to_list()):
        df = resp[resp['symbol']==symbol].copy()
        df = df.reset_index()
        df_len = len(df)
        if df_len > 2:
            slope, intercept, r_value, p_value, std_err = stats.linregress(df.index, df['price'])
            slope_dict[df.iloc[0].symbol] = slope
    speedybee_dict['slope'] = slope_dict
    
    # QUEEN[queens_chess_piece]['pollenstory_info']['speedybee'] = speedybee_dict

    print("cum.slope", sum([v for k,v in slope_dict.items()]))
    return {'speedybee': speedybee_dict}


def pickle_chesspiece(pickle_file, data_to_store):
    if PickleData(pickle_file=pickle_file, data_to_store=data_to_store) == False:
        msg=("Pickle Data Failed")
        print(msg)
        logging.critical(msg)
        return False
    else:
        return True


def PickleData(pickle_file, data_to_store): 
    # initializing data to be stored in db
    try:
        p_timestamp = {'file_creation': datetime.datetime.now()} 
        
        if os.path.exists(pickle_file) == False:
            print("init", pickle_file)
            db = {} 
            db['jp_timestamp'] = p_timestamp 
            dbfile = open(pickle_file, 'ab') 
            pickle.dump(db, dbfile)                   
            dbfile.close() 

        if data_to_store:
            p_timestamp = {'last_modified': datetime.datetime.now()}
            dbfile = open(pickle_file, 'rb+')      
            db = pickle.load(dbfile)
            dbfile.seek(0)
            dbfile.truncate()
            for k, v in data_to_store.items(): 
                db[k] = v
            db['last_modified'] = p_timestamp 
            # print(db)
            pickle.dump(db, dbfile)                   
            dbfile.close()
        
        return True
    except Exception as e:
        print("logme", e)
        return False


def ReadPickleData(pickle_file): 
    # for reading also binary mode is important try 3 times
    try:
        dbfile = open(pickle_file, 'rb')      
        db = pickle.load(dbfile) 
        dbfile.close()
        return db
    except Exception as e:
        try:
            time.sleep(.33)
            dbfile = open(pickle_file, 'rb')      
            db = pickle.load(dbfile) 
            dbfile.close()
            return db
        except Exception as e:
            try:
                time.sleep(.33)
                dbfile = open(pickle_file, 'rb')      
                db = pickle.load(dbfile) 
                dbfile.close()
                return db
            except Exception as e:
                print("CRITICAL ERROR logme", e)
                return False


def timestamp_string(format="%m-%d-%Y %I.%M%p"):
    return datetime.datetime.now().strftime(format)


def return_timestamp_string(format='%Y-%m-%d %H-%M-%S %p'):
    return datetime.datetime.now().strftime(format)


def print_line_of_error():
    exc_type, exc_obj, exc_tb = sys.exc_info()
    print(exc_type, exc_tb.tb_lineno)





##################################################
##################################################
################ NOT IN USE ######################
##################################################




def read_csv_db(db_root, tablename, ext='.csv', prod=True, init=False):
    orders = False
    main_orders_cols = ['trigname', 'client_order_id', 'origin_client_order_id', 'exit_order_link', 'date', 'lastmodified', 'selfnote']

    if init:
        def create_csv_table(cols, db_root, tablename, ext):
            table_path = os.path.join(db_root, tablename)
            if os.path.exists(table_path) == False:
                with open(table_path, 'w') as f:
                    df = pd.DataFrame()
                    for i in cols:
                        df[i] = ''
                    df.to_csv(table_path, index=True, encoding='utf8')
                    print(table_path, "created")
                    return True
            else:
                return True

        tables = ['main_orders.csv', 'main_orders_sandbox.csv']
        for t in tables:
            if os.path.exists(os.path.join(db_root, t)):
                pass
            else:
                create_csv_table(cols=main_orders_cols, db_root=db_root, tablename=t, ext='.csv')

    if tablename:
        if prod:
            return pd.read_csv(os.path.join(db_root, f'{tablename}{ext}'), dtype=str, encoding='utf8', engine='python')
        else:
            return pd.read_csv(os.path.join(db_root, f'{tablename}{"_sandbox"}{ext}'), dtype=str, encoding='utf8', engine='python')


def update_csv_db(df_to_add, tablename, append, update=False, replace=False, ext='.csv', prod=True):
    df_to_add['lastmodified'] = datetime.datetime.now().isoformat()
    if prod:
        table_path = os.path.join(db_root, f'{tablename}{ext}')
    else:
        table_path = os.path.join(db_root, f'{tablename}{"_sandbox"}{ext}')

    if tablename:
        if prod:
            main_df = pd.read_csv(os.path.join(db_root, f'{tablename}{ext}'), dtype=str, encoding='utf8', engine='python')
        else:
            main_df = pd.read_csv(os.path.join(db_root, f'{tablename}{"_sandbox"}{ext}'), dtype=str, encoding='utf8', engine='python')

        if append:
            new_df = pd.concat([main_df, df_to_add], axis=0, ignore_index=True)
            new_df.to_csv(table_path, index=True, encoding='utf8')
        
        if update:
            indx = list(df_to_add.index)
            main_df['index'] = main_df.index
            main_df = main_df[~main_df['index'].isin(indx)]
            new_df = pd.concat([main_df, df_to_add], axis=0)
            new_df.to_csv(table_path, index=True, encoding='utf8')
        
        if replace:
            new_df = df_to_add
            new_df.to_csv(table_path, index=True, encoding='utf8')      


def convert_todatetime_string(date_string):
    # In [94]: date_string
    # Out[94]: '2022-03-11T19:41:50.649448Z'
    # In [101]: date_string[:19]
    # Out[101]: '2022-03-11T19:41:50'
    return datetime.datetime.fromisoformat(date_string[:19])


def convert_Todatetime_return_est_stringtime(date_string):
    # In [94]: date_string
    # Out[94]: '2022-03-11T19:41:50.649448Z'
    # In [101]: date_string[:19]
    # Out[101]: '2022-03-11T19:41:50'
    d = datetime.datetime.fromisoformat(date_string[:19])
    d = datetime.datetime.fromisoformat(v[:19])
    j = d.replace(tzinfo=datetime.timezone.utc)
    fmt = '%Y-%m-%dT%H:%M:%S'
    est_date = j.astimezone(pytz.timezone('US/Eastern')).strftime(fmt)
    return est_date


def convert_nano_utc_timestamp_to_est_datetime(digit_trc_time):
    digit_trc_time = 1644523144856422000
    dt = datetime.datetime.utcfromtimestamp(digit_trc_time // 1000000000) # 9 zeros
    dt = dt.strftime('%Y-%m-%d %H:%M:%S')
    return dt


def wait_for_market_open():
    clock = api.get_clock()
    if not clock.is_open:
        time_to_open = (clock.next_open - clock.timestamp).total_seconds()
        time.sleep(round(time_to_open))


def time_to_market_close():
    clock = api.get_clock()
    return (clock.next_close - clock.timestamp).total_seconds()


def read_wiki_index():
    table=pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
    df = table[0]
    # sp500 = df['Symbol'].tolist()
    # df.to_csv('S&P500-Info.csv')
    # df.to_csv("S&P500-Symbols.csv", columns=['Symbol'])
    return df


###### >>>>>>>>>>>>>>>> CASTLE BISHOP FUNCTIONS <<<<<<<<<<<<<<<#########
#####                                                            #######
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



""" Main Functions"""
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
    bars = return_bars_list(ticker_list, chart_times, exchange='CBSE')
    if bars[1]: # rebuild and split back to ticker_time with market hours only
        bars_dfs = bars[1]
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
        bars_data = return_bars(symbol=ticker, timeframe=timeframe, ndays=0) # return [True, symbol_data, market_hours_data, after_hours_data]
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

    return {'pollencharts_nectar': main_rebuild_dict, 'pollencharts': chart_rebuild_dict}



###### >>>>>>>>>>>>>>>> CASTLE BISHOP FUNCTIONS <<<<<<<<<<<<<<<#########
