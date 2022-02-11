from cgitb import reset
from datetime import datetime
import logging
from enum import Enum
import time
import alpaca_trade_api as tradeapi
import asyncio
import os
import pandas as pd
import pandas_ta as ta
import sys
from alpaca_trade_api.rest import TimeFrame, URL
from alpaca_trade_api.rest_async import gather_with_concurrency, AsyncRest
from dotenv import load_dotenv
import threading
import datetime
system = 'windows' #mac, windows
load_dotenv()

if system != 'windows':
    db_root = os.environ.get('db_root_mac')
else:
    db_root = os.environ.get('db_root_winodws')


logging.basicConfig(
    filename='hive_utils.log',
    level=logging.WARNING,
    format='%(asctime)s:%(levelname)s:%(message)s',
)

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

def wait_for_market_open():
	clock = api.get_clock()
	if not clock.is_open:
		time_to_open = (clock.next_open - clock.timestamp).total_seconds()
		time.sleep(round(time_to_open))


def time_to_market_close():
	clock = api.get_clock()
	return (clock.next_close - clock.timestamp).total_seconds()


# submit order
def submit_order(symbol, qty, side, type, limit_price, client_order_id, time_in_force, order_class=False, stop_loss=False, take_profit=False):
    
    # sell_x = api.submit_order(symbol='SPDN', 
    #         qty=1, 
    #         side='sell', 
    #         time_in_force='gtc', 
    #         type='limit', # market
    #         limit_price=14.90, 
    #         client_order_id='004') # optional make sure it unique though to call later!

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
    #         time_in_force='gtc', 
    #         type='limit', 
    #         limit_price=400.00, 
    #         client_order_id=001, 
    #         order_class='bracket', 
    #         stop_loss=dict(stop_price='360.00'), 
	#         take_profit=dict(limit_price='440.00'))
    """Order Return"""
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


    if 'name' == 'main':
        submit_order()


def account_info(api):
    info = api.get_account()
            # Account({   'account_blocked': False,
            #     'account_number': '603397580',
            #     'accrued_fees': '0',
            #     'buying_power': '80010',
            #     'cash': '40005',
            #     'created_at': '2022-01-23T22:11:15.978765Z',
            #     'crypto_status': 'PAPER_ONLY',
            #     'currency': 'USD',
            #     'daytrade_count': 0,
            #     'daytrading_buying_power': '0',
            #     'equity': '40005',
            #     'id': '2fae9699-b24f-4d06-80ec-d531b61e9458',
            #     'initial_margin': '0',
            #     'last_equity': '40005',
            #     'last_maintenance_margin': '0',
            #     'long_market_value': '0',
            #     'maintenance_margin': '0',
            #     'multiplier': '2',
            #     'non_marginable_buying_power': '40005',
            #     'pattern_day_trader': False,
            #     'pending_transfer_in': '40000',
            #     'portfolio_value': '40005',
            #     'regt_buying_power': '80010',
            #     'short_market_value': '0',
            #     'shorting_enabled': True,
            #     'sma': '40005',
            #     'status': 'ACTIVE',
            #     'trade_suspended_by_user': False,
            #     'trading_blocked': False,
            #     'transfers_blocked': False})
    return {'account_number': info.account_number,
            'accrued_fees': info.accrued_fees,
            'buying_power': info.buying_power,
            'cash': info.cash,
            'daytrade_count': info.daytrade_count,
            'last_equity': info.last_equity,
            'portfolio_value': info.portfolio_value,
            'sma': info.sma}


def return_bars(api, symbol, timeframe, start_date, end_date):
    # SYMBOL = 'SPY'
    # time = 1
    # timeframe = tradeapi.TimeFrame(1, tradeapi.TimeFrameUnit.Minute) # every second
    
    ticker = api.get_bars(symbol, timeframe, start_date, end_date) # '2022-02-11', '2022-02-11'
    df = ticker.df.reset_index()

    macd = df.ta.macd(close='close', fast=12, slow=26, append=True)
    # print(df.iloc[-1])

    return 


def return_latest_quote(api, symbol):
    quote_dict = api.get_latest_quote(symbol)
    # QuoteV2({   'ap': 448.27,
    #     'as': 3,
    #     'ax': 'X',
    #     'bp': 448.25,
    #     'bs': 4,
    #     'bx': 'T',
    #     'c': ['R'],
    #     't': '2022-02-11T16:19:51.467033352Z',    
    #     'z': 'B'})


# # Return order Status
# def clientId_order_status(api, client_id_order):
#     open_orders_list = api.list_orders(status='open')
#     if client_id_order:
#         order_token = api.get_order_by_client_order_id(client_id_order)
#     else:
#         order_token = False
#     return [True, spdn_order, open_orders_list]



def convert_nano_utc_timestamp_to_est_datetime(digit_trc_time):
    time = 1644523144856422000
    dt = datetime.datetime.utcfromtimestamp(digit_trc_time // 1000000000) # 9 zeros
    dt = dt.strftime('%Y-%m-%d %H:%M:%S')
    return dt


def read_csv_db(db_root, symbol=False):
    # spy_stream
    # spy_barset
    tables = ['main_orders.csv', '_stream.csv', '_bars.csv']
    for t in tables:
        if os.path.exists(os.path.join(db_root, t)):
            pass
        else:
            with open(os.path.join(db_root, t), 'w') as f:
                print(t, "created")
                print(f)

    if symbol:
        stream = pd.read_csv(os.path.join(db_root, symbol + '_stream.csv'), dtype=str, encoding='utf8', engine='python')
        bars = pd.read_csv(os.path.join(db_root, symbol + '_bars.csv'),  dtype=str, encoding='utf8', engine='python')
        orders = pd.read_csv(os.path.join(db_root, 'main_orders.csv'),  dtype=str, encoding='utf8', engine='python')
    return [stream, bars, orders]






































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