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

est = pytz.timezone("US/Eastern")

system = 'windows' #mac, windows
load_dotenv()

if system != 'windows':
    db_root = os.environ.get('db_root_mac')
else:
    db_root = os.environ.get('db_root_winodws')

# logging.basicConfig(
#     filename='hive_utils.log',
#     level=logging.INFO,
#     format='%(asctime)s:%(levelname)s:%(message)s',
# )

api_key_id = os.environ.get('APCA_API_KEY_ID')
api_secret = os.environ.get('APCA_API_SECRET_KEY')
base_url = "https://api.alpaca.markets"


def return_api_keys(base_url, api_key_id, api_secret):

    # api_key_id = os.environ.get('APCA_API_KEY_ID')
    # api_secret = os.environ.get('APCA_API_SECRET_KEY')
    # base_url = "https://api.alpaca.markets"
    # feed = "sip"  # change to "sip" if you have a paid account

    rest = AsyncRest(key_id=api_key_id,
                        secret_key=api_secret)

    api = tradeapi.REST(key_id=api_key_id,
                        secret_key=api_secret,
                        base_url=URL(base_url), api_version='v2')
    return [{'rest': rest, 'api': api}]

keys = return_api_keys(base_url, api_key_id, api_secret)

rest = keys[0]['rest']
api = keys[0]['api']

"""# Dates """
current_day = api.get_clock().timestamp.date().isoformat()
trading_days = api.get_calendar()
trading_days_df = pd.DataFrame([day._raw for day in trading_days])

start_date = datetime.datetime.now().strftime('%Y-%m-%d')
end_date = datetime.datetime.now().strftime('%Y-%m-%d')

""" VAR >>>>>>>>>>VAR >>>>>>>>>>VAR >>>>>>>>>>VAR >>>>>>>>>>VAR >>>>>>>>>>VAR >>>>>>>>>>"""
def return_bars(symbol, time, ndays, trading_days_df):
    try:
        # ndays = 1
        # time = "1Min" #"1Day" # "1Min"
        # symbol = 'SPY'
        
        # # First get the current day and all trading days
        # current_day = api.get_clock().timestamp.date().isoformat()
        # trading_days = api.get_calendar()

        # # Convert trading days to a Dataframe for easier manipulation
        # # Select the 10 days before the current day
        # ADDED Above as Global var
        symbol_n_days = trading_days_df.query('date < @current_day').tail(ndays)

        # Fetch bars for those days
        symbol_data = api.get_bars(symbol, time,
                                    start=symbol_n_days.head(1).date,
                                    end=symbol_n_days.tail(1).date, 
                                    adjustment='all').df.reset_index()
        # est = pytz.timezone("US/Eastern") # GlovalVar
        symbol_data['timestamp_est'] = symbol_data['timestamp'].apply(lambda x: x.astimezone(est))
        symbol_data['timestamp_est_timestamp'] = symbol_data['timestamp_est'].apply(lambda x: datetime.datetime.fromtimestamp(x.timestamp()))
    
        day = symbol_data["timestamp_est"].iloc[0].day
        month = symbol_data["timestamp_est"].iloc[0].month
        year = symbol_data["timestamp_est"].iloc[0].year
        
        formater = "%Y-%m-%d %H:%M:%S"
        str_timestamp = "{}-{}-{} 09:30:00".format(year, month, day)
        market_reg_open = datetime.datetime.strptime(str_timestamp, formater)
        str_timestamp = "{}-{}-{} 16:00:00".format(year, month, day)
        market_reg_close = datetime.datetime.strptime(str_timestamp, formater)

        symbol_data['after_hours_tag'] = np.where((symbol_data['timestamp_est_timestamp']>=market_reg_open) & (symbol_data['timestamp_est_timestamp']<=market_reg_close), "MarketHours", "AfterHours")
        market_hours_data = symbol_data[symbol_data['after_hours_tag']=='MarketHours'].copy()
        after_hours_data = symbol_data[symbol_data['after_hours_tag']=='AfterHours'].copy()

        return [symbol_data, market_hours_data, after_hours_data]
    # handle error
    except Exception as e:
        print("sending email of error", e)
# r = return_bars(symbol='SPY', time='1Min', ndays=10, trading_days_df=trading_days_df)


def init_log(root, dirname, name, update_df=False, update_type=False, update_write=False, cols=False):
    # dirname = 'db'
    # root_token=os.path.join(root, dirname)
    # name='hive_utils_log.csv'
    # cols = ['type', 'log_note']
    # update_df = pd.DataFrame(list(zip(['info'], ['text'])), columns = ['type', 'log_note'])
    # update_write=True
    
    root_token=os.path.join(root, dirname)
    
    if os.path.exists(os.path.join(root_token, name)) == False:
        with open(os.path.join(root_token, name), 'w') as f:
            df = pd.DataFrame()
            for i in cols:
                df[i] = ''
            df.to_csv(os.path.join(root_token, name), index=False, encoding='utf8')
            print(name, "created")
            return df
    else:
        df = pd.read_csv(os.path.join(root_token, name), dtype=str, encoding='utf8')
        if update_type == 'append':
            # df = df.append(update_df, ignore_index=True, sort=False)
            df = pd.concat([df, update_df], ignore_index=True)
            if update_write:
                df.to_csv(os.path.join(root_token, name), index=False, encoding='utf8')
                return df
            else:
                return df
        else:
            return df
# # TESTS
# log_file = init_log(root=os.getcwd(), dirname='db', name='hive_utils_log.csv', cols=False)
# log_file = init_log(root=os.getcwd(), dirname='db', name='hive_utils_log.csv', update_df=update_df, update_type='append', update_write=True, cols=False)

# trade closer to ask price .... sellers closer to bid .... measure divergence from bid/ask to give weight

def return_snapshots(ticker_list):
    # ticker_list = ['SPY', 'AAPL'] # TEST
    """ The Following will convert get_snapshots into a dict"""
    snapshots = api.get_snapshots(ticker_list)
    # snapshots['AAPL'].latest_trade.price # FYI This also avhices same goal
    
    return_dict = {}
    for ticker in snapshots:
        di = {ticker: {}}
        token_dict = vars(snapshots[ticker])
        for i in token_dict:
            unpack_dict = vars(token_dict[i])
            data = unpack_dict["_raw"] # raw data
            dataname = unpack_dict["_reversed_mapping"] # data names
            temp_dict = {i : {}} # revised dict with datanames
            for k, v in dataname.items():
                if v in data.keys():
                    t = {}
                    t[str(k)] = data[v]
                    temp_dict[i].update(t)
                    if v == 't':
                        temp_dict[i]['timestamp_covert'] = convert_todatetime_string(data[v])
                        # temp_dict[i]['timestamp_covert_est'] =  temp_dict[i]['timestamp_covert'].astimezone(est)
                        # temp_dict[i]['timestamp_covert_est'] = data[v].astimezone(est)
                di[ticker].update(temp_dict)
        
        return_dict.update(di)        
    return return_dict
# data = return_snapshots(ticker_list=['SPY', 'AAPL'])

def submit_order(symbol, qty, side, type, limit_price, client_order_id, time_in_force, order_class=False, stop_loss=False, take_profit=False):
    
    # order = api.submit_order(symbol='SPY', 
    #         qty=1, 
    #         side='buy', # buy, sell 
    #         time_in_force='gtc', # 'day'
    #         type='limit', # 'market'
    #         limit_price=425.15, 
    #         client_order_id='006') # optional make sure it unique though to call later!
    # order = api.submit_order(symbol='AAPL', 
    #         qty=1, 
    #         side='buy', # buy, sell 
    #         time_in_force='gtc', # 'day'
    #         type='market', # 'market'
    #         # limit_price=425.15, 
    #         client_order_id='008') # optional make sure it unique though to call later!

    if type == 'market':
        order = api.submit_order(symbol=symbol,
        qty=qty,
        side=side,
        type=type,
        time_in_force=time_in_force)
    return order

    """stop loss order""" 
    # api.submit_order(symbol='TSLA', 
    #         qty=1, 
    #         side='buy', 
    #         time_in_force='gtc', 'day'
    #         type='limit', 
    #         limit_price=400.00, 
    #         client_order_id=001, 
    #         order_class='bracket', 
    #         stop_loss=dict(stop_price='360.00'), 
	#         take_profit=dict(limit_price='440.00'))



    if 'name' == 'main':
        submit_order()


def refresh_account_info(api):
            """
            # Account({   'account_blocked': False, 'account_number': '603397580', 'accrued_fees': '0', 'buying_power': '80010',
            #     'cash': '40005', 'created_at': '2022-01-23T22:11:15.978765Z', 'crypto_status': 'PAPER_ONLY', 'currency': 'USD', 'daytrade_count': 0,
            #     'daytrading_buying_power': '0', 'equity': '40005', 'id': '2fae9699-b24f-4d06-80ec-d531b61e9458', 'initial_margin': '0',
            #     'last_equity': '40005','last_maintenance_margin': '0','long_market_value': '0','maintenance_margin': '0',
            #     'multiplier': '2','non_marginable_buying_power': '40005','pattern_day_trader': False,'pending_transfer_in': '40000',
            #     'portfolio_value': '40005','regt_buying_power': '80010',
            #     'short_market_value': '0','shorting_enabled': True,'sma': '40005','status': 'ACTIVE','trade_suspended_by_user': False,
            #     'trading_blocked': False, 'transfers_blocked': False})
            """
            info = api.get_account()
            return [info, 
                {'account_number': info.account_number,
                'accrued_fees': float(info.accrued_fees),
                'buying_power': float(info.buying_power),
                'cash': float(info.cash),
                'daytrade_count': float(info.daytrade_count),
                'last_equity': float(info.last_equity),
                'portfolio_value': float(info.portfolio_value)
                }
                ]


def return_trade_bars(symbol, start_date_iso, end_date_iso, limit=None):
    # symbol = 'SPY'
    # start_date_iso = '2022-03-10 19:00' # 2 PM EST start_date_iso = '2022-03-10 14:30'
	# end_date_iso = '2022-03-10 19:15' # end_date_iso = '2022-03-10 20:00'
	# Function to check if trade has one of inputted conditions
	def has_condition(condition_list, condition_check):
		if type(condition_list) is not list: 
			# Assume none is a regular trade?
			in_list = False
		else:
			# There are one or more conditions in the list
			in_list = any(condition in condition_list for condition in condition_check)

		return in_list

	exclude_conditions = [
	'B',
	'W',
	'4',
	'7',
	'9',
	'C',
	'G',
	'H',
	'I',
	'M',
	'N',
	'P',
	'Q',
	'R',
	'T',
	'U',
	'V',
	'Z'
	]

	# fetch trades over whatever timeframe you need
	start_time = pd.to_datetime(start_date_iso, utc=True)
	end_time = pd.to_datetime(end_date_iso, utc=True)

	trades_df = api.get_trades(symbol=symbol, start=start_time.isoformat(), end=end_time.isoformat(), limit=limit).df

	# convert to market time for easier reading
	trades_df = trades_df.tz_convert('America/New_York')

	# add a column to easily identify the trades to exclude using our function from above
	trades_df['exclude'] = trades_df.conditions.apply(has_condition, condition_check=exclude_conditions)

	# filter to only look at trades which aren't excluded
	valid_trades = trades_df.query('not exclude')

	# # Resample the valid trades to calculate the OHLCV bars
	# agg_functions = {'price': ['first', 'max', 'min', 'last'], 'size': 'sum'}
	# min_bars = valid_trades.resample('1T').agg(agg_functions)

	# Resample the trades to calculate the OHLCV bars
	agg_functions = {'price': ['first', 'max', 'min', 'last'], 'size': ['sum', 'count']}

	valid_trades = trades_df.query('not exclude')
	min_bars = valid_trades.resample('1T').agg(agg_functions)

	min_bars = min_bars.droplevel(0, 'columns')
	min_bars.columns=['open', 'high', 'low' , 'close', 'volume', 'trade_count']

	return min_bars


def log_script(log_file, loginfo_dict):
    loginfo_dict = {'type': 'info', 'lognote': 'someones note'}
    df = pd.read_csv(log_file, dtype=str, encoding='utf8')
    for k,v in  loginfo_dict.items():
        df[k] = v.fillna(df[k])


def read_csv_db(db_root, type, symbol=False):
    # spy_stream
    # spy_barset
    stream = False
    bars = False
    orders = False

    tables = ['main_orders.csv', '_stream.csv', '_bars.csv']
    for t in tables:
        if os.path.exists(os.path.join(db_root, t)):
            pass
        else:
            with open(os.path.join(db_root, t), 'w') as f:
                print(t, "created")
                print(f)

    if symbol:
        if type == 'stream':
            if os.path.exists(os.path.join(db_root, symbol + '_{}.csv'.format(type))) == False:
                with open(os.path.join(db_root, symbol + '_{}.csv'.format(type)), 'w') as f:
                    df = pd.DataFrame()
                    cols = ['timestamp', 'open', 'high', 'low', 'close', 'volume', 'trade_count']
                    for i in cols:
                        df[i] = ''
                    df.to_csv(os.path.join(db_root, symbol + '_{}.csv'.format(type)), index=False, encoding='utf8')
                    print(t, "created")
                    now = datetime.datetime.now()
                    stream = df
            else:
                stream = pd.read_csv(os.path.join(db_root, symbol + '_{}.csv'.format(type)), dtype=str, encoding='utf8', engine='python')

        # bars = pd.read_csv(os.path.join(db_root, symbol + '_bars.csv'),  dtype=str, encoding='utf8', engine='python')
        elif type == 'bars':
            if os.path.exists(os.path.join(db_root, symbol + '_{}.csv'.format(type))) == False:
                with open(os.path.join(db_root, symbol + '_{}.csv'.format(type)), 'w') as f:
                    df = pd.DataFrame()
                    cols = ['timestamp', 'open', 'high', 'low', 'close', 'volume', 'trade_count']
                    for i in cols:
                        df[i] = ''
                    df.to_csv(os.path.join(db_root, symbol + '_{}.csv'.format(type)), index=False, encoding='utf8')
                    print(t, "created")
                    bars = df
            else:
                bars = pd.read_csv(os.path.join(db_root, symbol + '_{}.csv'.format(type)), dtype=str, encoding='utf8', engine='python')

        # orders = pd.read_csv(os.path.join(db_root, 'main_orders.csv'),  dtype=str, encoding='utf8', engine='python')
        orders = 'TBD'
        return [stream, bars, orders]


def convert_todatetime_string(date_string):
    # In [94]: date_string
    # Out[94]: '2022-03-11T19:41:50.649448Z'
    # In [101]: date_string[:19]
    # Out[101]: '2022-03-11T19:41:50'
    return datetime.datetime.fromisoformat(date_string[:19])


def convert_nano_utc_timestamp_to_est_datetime(digit_trc_time):
    time = 1644523144856422000
    dt = datetime.datetime.utcfromtimestamp(digit_trc_time // 1000000000) # 9 zeros
    dt = dt.strftime('%Y-%m-%d %H:%M:%S')
    return dt

def convert_datetime_toEST(datetimeobject):
    out = datetime.datetime.fromisoformat(d).replace(tzinfo=timezone.utc).astimezone(ZoneInfo("America/New_York"))

def wait_for_market_open():
	clock = api.get_clock()
	if not clock.is_open:
		time_to_open = (clock.next_open - clock.timestamp).total_seconds()
		time.sleep(round(time_to_open))


def time_to_market_close():
	clock = api.get_clock()
	return (clock.next_close - clock.timestamp).total_seconds()


""" XXXXXXXXXXX depricated functions XXXXXXXXXX"""

def old_return_bars(api, symbol, timeframe, start_date, end_date):
    # symbol = 'SPY'
    # time = 1
    # timeframe = tradeapi.TimeFrame(1, tradeapi.TimeFrameUnit.Minute) # every second
    # start_date = '2022-02-15'
	# end_date = '2022-02-15'
	start_date = pd.to_datetime('2022-02-17 19:00', utc=True)
	end_date = pd.to_datetime('2022-02-17 19:15', utc=True)
	ticker = api.get_bars(symbol, timeframe, start_date.isoformat(), end_date.isoformat())
	df = ticker.df.reset_index()
	df['timestamp_est'] = df['timestamp'].apply(lambda x: x.astimezone(est))

    # macd = df.ta.macd(close='close', fast=12, slow=26, append=True)
    # print(df.iloc[-1])

	return df


def old_return_latest_trade(api, symbol):
    resp = api.get_latest_trade(symbol)
    di = {}
    d = vars(resp)
    data = d["_raw"] # raw data
    dataname = d["_reversed_mapping"] # data names
    for k,v in dataname.items():
        if v in data.keys():
            di[str(k)] = data[v]
    data['time_est'] = convert_todatetime_string(data['t']) # add est
    # QuoteV2({   'ap': 448.27,
    #     'as': 3,
    #     'ax': 'X',
    #     'bp': 448.25,
    #     'bs': 4,
    #     'bx': 'T',
    #     'c': ['R'],
    #     't': '2022-02-11T16:19:51.467033352Z',    
    #     'z': 'B'})
    return data


def old_return_latest_quote(api, symbol, tradeconditions=True):
    resp = api.get_latest_quote(symbol)
    di = {}
    d = vars(resp)
    data = d["_raw"] # raw data
    dataname = d["_reversed_mapping"] # data names
    for k,v in dataname.items():
        if v in data.keys():
            di[str(k)] = data[v]
    data['time_est'] = convert_todatetime_string(data['t']) # add est
    # QuoteV2({   'ap': 448.27,
    #     'as': 3,
    #     'ax': 'X',
    #     'bp': 448.25,
    #     'bs': 4,
    #     'bx': 'T',
    #     'c': ['R'],
    #     't': '2022-02-11T16:19:51.467033352Z',    
    #     'z': 'B'})
    return data
# # Return order Status
# def clientId_order_status(api, client_id_order):
#     open_orders_list = api.list_orders(status='open')
#     if client_id_order:
#         order_token = api.get_order_by_client_order_id(client_id_order)
#     else:
#         order_token = False
#     return [True, spdn_order, open_orders_list]






""" entity_v2.py Alpaca symbol matching"""
# trade_mapping_v2 = {
#     "i": "id",
#     "S": "symbol",
#     "c": "conditions",
#     "x": "exchange",
#     "p": "price",
#     "s": "size",
#     "t": "timestamp",
#     "z": "tape",  # stocks only
#     "tks": "takerside"  # crypto only
# }

# quote_mapping_v2 = {
#     "S":  "symbol",
#     "x": "exchange",  # crypto only
#     "ax": "ask_exchange",
#     "ap": "ask_price",
#     "as": "ask_size",
#     "bx": "bid_exchange",
#     "bp": "bid_price",
#     "bs": "bid_size",
#     "c":  "conditions",  # stocks only
#     "t":  "timestamp",
#     "z":  "tape"  # stocks only
# }

# bar_mapping_v2 = {
#     "S":  "symbol",
#     "x": "exchange",  # crypto only
#     "o":  "open",
#     "h":  "high",
#     "l":  "low",
#     "c":  "close",
#     "v":  "volume",
#     "t":  "timestamp",
#     "n":  "trade_count",
#     "vw": "vwap"
# }

# status_mapping_v2 = {
#     "S":  "symbol",
#     "sc": "status_code",
#     "sm": "status_message",
#     "rc": "reason_code",
#     "rm": "reason_message",
#     "t":  "timestamp",
#     "z":  "tape"
# }

# luld_mapping_v2 = {
#     "S": "symbol",
#     "u": "limit_up_price",
#     "d": "limit_down_price",
#     "i": "indicator",
#     "t": "timestamp",
#     "z": "tape"
# }

# cancel_error_mapping_v2 = {
#     "S": "symbol",
#     "i": "id",
#     "x": "exchange",
#     "p": "price",
#     "s": "size",
#     "a": "cancel_error_action",
#     "z": "tape",
#     "t": "timestamp",
# }

# correction_mapping_v2 = {
#     "S": "symbol",
#     "x": "exchange",
#     "oi": "original_id",
#     "op": "original_price",
#     "os": "original_size",
#     "oc": "original_conditions",
#     "ci": "corrected_id",
#     "cp": "corrected_price",
#     "cs": "corrected_size",
#     "cc": "corrected_conditions",
#     "z": "tape",
#     "t": "timestamp",
# }

""" snapshot"""
# snapshots = api.get_snapshots(['AAPL', 'IBM'])
# snapshots['AAPL'].latest_trade.price

# In [34]: vars(api.get_snapshot("SPY"))
# Out[34]: 
# {'latest_trade': TradeV2({   'c': [' ', 'M'],
#      'i': 52983677401155,
#      'p': 420.07,
#      's': 2018694,
#      't': '2022-03-12T01:00:00.00258816Z',
#      'x': 'P',
#      'z': 'B'}),
#  'latest_quote': QuoteV2({   'ap': 419.95,
#      'as': 245,
#      'ax': 'P',
#      'bp': 419.94,
#      'bs': 19,
#      'bx': 'P',
#      'l': 419.91,
#      'n': 56,
#      'o': 419.92,
#      't': '2022-03-12T00:59:00Z',
#      'v': 2397,
#      'vw': 419.929908}),
#  'daily_bar': BarV2({   'c': 420.07,
#      'h': 428.77,
#      'l': 419.53,
#      'n': 809145,
#      'o': 428.18,
#      't': '2022-03-11T05:00:00Z',
#      'v': 90803923,
#      'vw': 424.040193}),
#  'prev_daily_bar': BarV2({   'c': 425.48,
#      'h': 426.43,
#      'l': 420.44,
#      'n': 891241,
#      'o': 422.73,
#      't': '2022-03-10T05:00:00Z',
#      'v': 91933914,
#      'vw': 423.871044})}



"""Order Return ref"""
# Out[14]: 
# Order({   'asset_class': 'us_equity',
#     'asset_id': 'b28f4066-5c6d-479b-a2af-85dc1a8f16fb',
#     'canceled_at': None,
#     'client_order_id': '001',
#     'created_at': '2022-02-08T16:20:07.813040847Z',
#     'expired_at': None,
#     'extended_hours': False,
#     'failed_at': None,
#     'filled_at': None,
#     'filled_avg_price': None,
#     'filled_qty': '0',
#     'hwm': None,
#     'id': '5dbcb543-956b-4eec-b9b8-fc768d517da9',
#     'legs': None,
#     'limit_price': '449.2',
#     'notional': None,
#     'order_class': '',
#     'order_type': 'limit',
#     'qty': '1',
#     'replaced_at': None,
#     'replaced_by': None,
#     'replaces': None,
#     'side': 'buy',
#     'status': 'accepted',
#     'stop_price': None,
#     'submitted_at': '2022-02-08T16:20:07.812422547Z',
#     'symbol': 'SPY',
#     'time_in_force': 'gtc',
#     'trail_percent': None,
#     'trail_price': None,
#     'type': 'limit',
#     'updated_at': '2022-02-08T16:20:07.813040847Z'})