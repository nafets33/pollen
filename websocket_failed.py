import logging
from enum import Enum
import time
import alpaca_trade_api as tradeapi
import asyncio
import os
import pandas as pd
import sys
from alpaca_trade_api.rest import TimeFrame, URL
from alpaca_trade_api.rest_async import gather_with_concurrency, AsyncRest
from dotenv import load_dotenv
import threading
import pandas_ta as ta

load_dotenv()

logging.basicConfig(
	filename='errlog.log',
	level=logging.WARNING,
	format='%(asctime)s:%(levelname)s:%(message)s',
)

api_key_id = os.environ.get('APCA_API_KEY_ID')
api_secret = os.environ.get('APCA_API_SECRET_KEY')
base_url = "https://api.alpaca.markets"
feed = "sip"  # change to "sip" if you have a paid account vs "iex"

rest = AsyncRest(key_id=api_key_id,
                    secret_key=api_secret)

api = tradeapi.REST(key_id=api_key_id,
                    secret_key=api_secret,
                    base_url=URL(base_url), api_version='v2')


# # List of all Available stocks to trade
# active_assets = api.list_assets(status='active')
# aapl_asset = api.get_asset('AAPL') # if security avail to trade


# for The last price a stock traded at, curent quote, last 1 min bar
# conn = tradeapi.stream2.StreamConn(api_key_id, api_secret, base_url)

def time_to_market_close():
	clock = api.get_clock()
	return (clock.next_close - clock.timestamp).total_seconds()


def wait_for_market_open():
	clock = api.get_clock()
	if not clock.is_open:
		time_to_open = (clock.next_open - clock.timestamp).total_seconds()
		time.sleep(round(time_to_open))


def set_trade_params(df):  # use to return High / Low of set of Bars
	return {
		'high': df.high.tail(10).max(),
		'low': df.low.tail(10).min(),
		'trade_taken': False,
	}


# Don't Trade Unless there X time left in Market 
# if time_to_market_close() > 120:
#     print(f'sent {direction} trade')

# To Stream prices
ws_url = 'wss://data.alpaca.markets'
conn = tradeapi.stream2.StreamConn(
    api_key_id, api_secret, base_url=base_url, data_url=ws_url, data_stream='alpacadatav1'
)

print("Bees Hunt")
@conn.on(r'^account_updates$')
async def on_account_updates(conn, channel, account):
    print('account', account)

@conn.on(r'^trade_updates$')
async def on_trade_updates(conn, channel, trade):
    print('trade', trade)

# updates for every trade / at what price
@conn.on(r'^T.AAPL$') # updates for every trade / at what price
async def trade_info(conn, channel, bar):
    print('bars', bar)
    print(bar._raw)

# return bid/ask
@conn.on(r'^Q.AAPL$')
async def quote_info(conn, channel, bar):
    print('bars', bar)

# 1 min bar
@conn.on(r'^AM.AAPL$')
async def on_minute_bars(conn, channel, bar):
    print('bars', bar)

def ws_start():
	conn.run(['account_updates', 'trade_updates'])

#start WebSocket in a thread
ws_thread = threading.Thread(target=ws_start, daemon=True)
ws_thread.start()






