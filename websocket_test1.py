"""
In this example code we wrap the ws connection to make sure we reconnect
in case of ws disconnection.
"""

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
# from asyncio import loop



load_dotenv()
logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)

ALPACA_API_KEY = os.environ.get('APCA_API_KEY_ID')
ALPACA_SECRET_KEY = os.environ.get('APCA_API_SECRET_KEY')
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
    print('quote', q)


if __name__ == '__main__':
    conn = Stream(ALPACA_API_KEY,
                  ALPACA_SECRET_KEY,
                  base_url=URL('https://api.alpaca.markets'),
                  data_feed='sip')

    conn.subscribe_quotes(print_quote, 'SPY')
    # conn.subscribe_quotes(print_quote, 'AAPL')

    run_connection(conn)
