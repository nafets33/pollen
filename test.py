from alpaca_trade_api.stream import Stream
from asyncore import loop
import logging
import time
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
import threading

load_dotenv()
logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)

api_key = os.environ.get('APCA_API_KEY_ID')
api_secret = os.environ.get('APCA_API_SECRET_KEY')
base_url = 'https://api.alpaca.markets'

# conn = tradeapi.stream2.StreamConn(ALPACA_API_KEY, 
# ALPACA_SECRET_KEY, 'https://api.alpaca.markets')

ws_url = 'wss://data.alpaca.markets/v2'

conn = tradeapi.stream2.StreamConn(
    api_key, api_secret, base_url=base_url, data_url=ws_url, data_stream='alpacadatav1'
)

@conn.on(r'^account_updates$')
async def on_account_updates(conn, channel, account):
    print('account', account)

@conn.on(r'^trade_updates$')
async def on_trade_updates(conn, channel, trade):
    print('trade', trade)

@conn.on(r'^T.AAPL$')
async def trade_info(conn, channel, bar):
    print('bars', bar)
    print(bar._raw)

@conn.on(r'^AM.AAPL$')
async def on_minute_bars(conn, channel, bar):
    print('bars', bar)

def ws_start():
    conn.run(['account_updates', 'trade_updates', 'AM.AAPL'])

# #start WebSocket in a thread
# ws_thread = threading.Thread(target=ws_start, daemon=True)
# ws_thread.start()

async def trade_callback(t):
    print('trade', t)


async def quote_callback(q):
    print('quote', q)
# Initiate Class Instance
stream = Stream(api_key,
                api_secret,
                base_url=URL('https://api.alpaca.markets'),
                data_feed='SIP')  # <- replace to SIP if you have PRO subscription

# subscribing to event``
stream.subscribe_trades(trade_callback, 'AAPL')
stream.subscribe_quotes(quote_callback, 'IBM')

stream.run()