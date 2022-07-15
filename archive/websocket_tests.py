"""
In this example code we wrap the ws connection to make sure we reconnect
in case of ws disconnection.
"""

from asyncore import loop
import logging
import time
import collections
from collections import deque

from pip import main
from alpaca_trade_api.stream import Stream
from alpaca_trade_api.common import URL
from dotenv import load_dotenv
import pandas_ta as ta
import os
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
import pytz
import random
from Hive_Utils import PickleData
# from asyncio import loop

load_dotenv()
logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)

est = pytz.timezone("US/Eastern")

# Load Roots
system = 'windows' #mac, windows
load_dotenv()

if system != 'windows':
    db_root = os.environ.get('db_root_mac')
else:
    db_root = os.environ.get('db_root_winodws')

# KEYS
ALPACA_API_KEY = os.environ.get('APCA_API_KEY_ID')
ALPACA_SECRET_KEY = os.environ.get('APCA_API_SECRET_KEY')

main_dict = {}
dq = deque([], 100)  # fast way to handle running list


def run_connection(conn):
    try:
        conn.run()
    except KeyboardInterrupt:
        print("Interrupted execution by user")
        loop.run_until_complete(conn.stop_ws())
        exit(0)
    except Exception as e:
        print(f'Exception from websocket connection: {e}')
    finally:
        print("Trying to re-establish connection")
        time.sleep(3)
        run_connection(conn)


async def print_quote(q):
    # print('quote', q)
    dq.append(q)
    pickle_file = os.path.join(db_root, 'now_tic.pkl')
    PickleData(pickle_file, data_to_store={'now_tic': dq})


async def quote_callback(q):
    # stream = pd.read_csv(os.path.join(db_root, '_stream.csv'), dtype=str, encoding='utf8', engine='python')
    print('quote', q)


async def on_account_updates(conn, channel, account):
    print('account', account)


async def on_trade_updates(tu):
    print('trade update', tu)


async def print_crypto_trade(t):
    print('crypto trade', t)


# tickers = ['SPY', 'QQQ', 'SPLX', 'SQQQ', 'TQQQ']
# tick selection Logic (top 10, highest beta, top movers from prv day)

tickers = ['AAPL', 'TSLA', 'GOOG', 'FB', 'AMZN']
ticker_tiers = {} # top {N_50} tickers of entire market 
if __name__ == '__main__':
    conn = Stream(ALPACA_API_KEY,
                  ALPACA_SECRET_KEY,
                  base_url=URL('https://api.alpaca.markets'),
                  data_feed='sip')

    # conn.subscribe_bars(print_quote, *tickers)
    # conn.subscribe_quotes(quote_callback, *tickers)
    # conn.subscribe_crypto_trades(print_crypto_trade, 'BTCUSD') # CRYPTO BTC
    conn.subscribe_trades(print_quote, *tickers) # Returns Trades: Exlcude Conditions????
    # conn.subscribe_trades(print_quote, 'SPY') # Returns Trades: Exlcude Conditions????

    conn.subscribe_trade_updates(on_trade_updates)
    run_connection(conn)








###<<<<<<<<END>>>>>>>>>>>>>###
# @conn.on(r'^account_updates$')
# async def on_account_updates(conn, channel, account):
#     print('account', account)

# @conn.on(r'^trade_updates$')
# async def on_trade_updates(conn, channel, trade):
#     print('trade', trade)


# quote Quote({   'ask_exchange': 'P',
#     'ask_price': 426.23,
#     'ask_size': 1,
#     'bid_exchange': 'P',
#     'bid_price': 426.22,
#     'bid_size': 2,
#     'conditions': ['R'],
#     'symbol': 'SPY',
#     'tape': 'B',
#     'timestamp': 1645640562579999744})