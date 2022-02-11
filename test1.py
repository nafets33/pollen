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
import pandas_ta as ta

load_dotenv()

NY = 'America/New_York'


class DataType(str, Enum):
    Bars = "Bars"
    Trades = "Trades"
    Quotes = "Quotes"


def get_data_method(data_type: DataType):
    if data_type == DataType.Bars:
        return rest.get_bars_async
    elif data_type == DataType.Trades:
        return rest.get_trades_async
    elif data_type == DataType.Quotes:
        return rest.get_quotes_async
    else:
        raise Exception(f"Unsupoported data type: {data_type}")


async def get_historic_data_base(symbols, data_type: DataType, start, end,
                                 timeframe: TimeFrame = None):
    """
    base function to use with all
    :param symbols:
    :param start:
    :param end:
    :param timeframe:
    :return:
    """
    major = sys.version_info.major
    minor = sys.version_info.minor
    if major < 3 or minor < 6:
        raise Exception('asyncio is not support in your python version')
    msg = f"Getting {data_type} data for {len(symbols)} symbols"
    msg += f", timeframe: {timeframe}" if timeframe else ""
    msg += f" between dates: start={start}, end={end}"
    print(msg)
    step_size = 1000
    results = []
    for i in range(0, len(symbols), step_size):
        tasks = []
        for symbol in symbols[i:i+step_size]:
            args = [symbol, start, end, timeframe.value] if timeframe else \
                [symbol, start, end]
            tasks.append(get_data_method(data_type)(*args))

        if minor >= 8:
            results.extend(await asyncio.gather(*tasks, return_exceptions=True))
        else:
            results.extend(await gather_with_concurrency(500, *tasks))

    bad_requests = 0
    for response in results:
        if isinstance(response, Exception):
            print(f"Got an error: {response}")
        elif not len(response[1]):
            bad_requests += 1

    print(f"Total of {len(results)} {data_type}, and {bad_requests} "
          f"empty responses.")


async def get_historic_bars(symbols, start, end, timeframe: TimeFrame):
    await get_historic_data_base(symbols, DataType.Bars, start, end, timeframe)


async def get_historic_trades(symbols, start, end, timeframe: TimeFrame):
    await get_historic_data_base(symbols, DataType.Trades, start, end)


async def get_historic_quotes(symbols, start, end, timeframe: TimeFrame):
    await get_historic_data_base(symbols, DataType.Quotes, start, end)


async def main(symbols):
    start = pd.Timestamp('2021-05-01', tz=NY).date().isoformat()
    end = pd.Timestamp('2021-08-30', tz=NY).date().isoformat()
    timeframe: TimeFrame = TimeFrame.Day
    await get_historic_bars(symbols, start, end, timeframe)
    await get_historic_trades(symbols, start, end, timeframe)
    await get_historic_quotes(symbols, start, end, timeframe)



api_key_id = os.environ.get('APCA_API_KEY_ID')
api_secret = os.environ.get('APCA_API_SECRET_KEY')
base_url = "https://api.alpaca.markets"
feed = "iex"  # change to "sip" if you have a paid account

rest = AsyncRest(key_id=api_key_id,
                    secret_key=api_secret)

api = tradeapi.REST(key_id=api_key_id,
                    secret_key=api_secret,
                    base_url=URL(base_url), api_version='v2')

start_time = time.time()
loop = asyncio.get_event_loop()
symbols = [el.symbol for el in api.list_assets(status='active')]
symbols = symbols[:200]
loop.run_until_complete(main(symbols))
print(f"took {time.time() - start_time} sec")

# return Data
spy = api.get_quotes("TSLA", "2022-02-10", "2022-02-10", limit=500).df
    # Index(['ask_exchange', 'ask_price', 'ask_size', 'bid_exchange', 'bid_price',
    #        'bid_size', 'conditions', 'tape'],
    #       dtype='object')


isOpen = api.get_clock().is_open

SYMBOL = 'SPY'
timeframe = tradeapi.TimeFrame(1, tradeapi.TimeFrameUnit.Minute)
ticker = api.get_bars('{}'.format(SYMBOL), timeframe, '2022-02-11', '2022-02-11') # return as df (time, open, high, low, close)
df = ticker.df.reset_index()

ticker_data = df['{}'.format(SYMBOL)].reset_index()
macd = ticker_data.ta.macd(close='close', fast=12, slow=26, append=True)
print(ticker_data.iloc[499])

# get latest_quote
api.get_latest_quote("SPY")

# check for submitted orders WEB Socket will return orders then get executed
position = api.get_position('SPY') 
spdn = api.get_position('SPDN')
open_orders_list = api.list_orders(status='open')
https://alpaca.markets/docs/api-references/trading-api/orders/

spdn_order = api.get_order_by_client_order_id('247b28e6-c5b0-4486-b919-2c310a8f1434')

x = api.replace_order(qty=1, time_in_force='gtc', limit_price='15', order_id='45876739-4d8f-4796-9096-b60fcf12a800')

# x returns new client_order_id seen below
spdn_order = api.get_order_by_client_order_id('7c335d05-3873-4c90-b393-f5ffd60d50e8')

after, until (timestamps), direction (desc, asc), nested?, symbols

# use Id for replace
replace = api.replace_order(qty=1, time_in_force='gtc', limit_price='14.71', order_id='98d15a9f-0f1e-4f0f-80c6-1b34719957ec')
# id 98d15a9f-0f1e-4f0f-80c6-1b34719957ec
r = api.get_order_by_client_order_id('98d15a9f-0f1e-4f0f-80c6-1b34719957ec')

Position({   'asset_class': 'us_equity',
    'asset_id': 'b28f4066-5c6d-479b-a2af-85dc1a8f16fb',
    'asset_marginable': False,
    'avg_entry_price': '449.2',
    'change_today': '0.0033090372490274',
    'cost_basis': '449.2',
    'current_price': '448.74',
    'exchange': 'ARCA',
    'lastday_price': '447.26',
    'market_value': '448.74',
    'qty': '1',
    'side': 'long',
    'symbol': 'SPY',
    'unrealized_intraday_pl': '-0.46',
    'unrealized_intraday_plpc': '-0.0010240427426536',
    'unrealized_pl': '-0.46',
    'unrealized_plpc': '-0.0010240427426536'})


""" submit order return """
In [14]: api.submit_order(
    ...:     symbol="SPY",
    ...:     qty=1,
    ...:     side="buy",
    ...:     time_in_force="gtc",
    ...:     type="limit",  # market
    ...:     limit_price=449.20,
    ...:     client_order_id="001",
    ...: )
Out[14]: 
Order({   'asset_class': 'us_equity',
    'asset_id': 'b28f4066-5c6d-479b-a2af-85dc1a8f16fb',
    'canceled_at': None,
    'client_order_id': '001',
    'created_at': '2022-02-08T16:20:07.813040847Z',
    'expired_at': None,
    'extended_hours': False,
    'failed_at': None,
    'filled_at': None,
    'filled_avg_price': None,
    'filled_qty': '0',
    'hwm': None,
    'id': '5dbcb543-956b-4eec-b9b8-fc768d517da9',
    'legs': None,
    'limit_price': '449.2',
    'notional': None,
    'order_class': '',
    'order_type': 'limit',
    'qty': '1',
    'replaced_at': None,
    'replaced_by': None,
    'replaces': None,
    'side': 'buy',
    'status': 'accepted',
    'stop_price': None,
    'submitted_at': '2022-02-08T16:20:07.812422547Z',
    'symbol': 'SPY',
    'time_in_force': 'gtc',
    'trail_percent': None,
    'trail_price': None,
    'type': 'limit',
    'updated_at': '2022-02-08T16:20:07.813040847Z'})

api.get_assapi.get_order_by_client_order_id(client_order_id="001")


In [50]: api.get_order_by_client_order_id(client_order_id="004")
Out[50]: 
Order({   'asset_class': 'us_equity',
    'asset_id': '7c7fa08a-c321-46fa-a907-cc7080548f92',
    'canceled_at': None,
    'client_order_id': '004',
    'created_at': '2022-02-08T17:34:15.733439312Z',
    'expired_at': None,
    'extended_hours': False,
    'failed_at': None,
    'filled_at': None,
    'filled_avg_price': None,
    'filled_qty': '0',
    'hwm': None,
    'id': '45876739-4d8f-4796-9096-b60fcf12a800',
    'legs': None,
    'limit_price': '14.9',
    'notional': None,
    'order_class': '',
    'order_type': 'limit',
    'qty': '1',
    'replaced_at': None,
    'replaced_by': None,
    'replaces': None,
    'side': 'sell',
    'status': 'new',
    'stop_price': None,
    'submitted_at': '2022-02-08T17:34:15.732848252Z',
    'symbol': 'SPDN',
    'time_in_force': 'gtc',
    'trail_percent': None,
    'trail_price': None,
    'type': 'limit',
    'updated_at': '2022-02-08T17:34:15.758800321Z'})


sell_x_c = api.submit_order(symbol='SPDN', 
        qty=1, 
        side='sell', 
        time_in_force='gtc', 
        type='limit', # market
        limit_price=14.80, 
        client_order_id='004') # optional make sure it unique though to call later!



def convert_nano_timestamp_to_datetime(t):
    return datetime.datetime.utcfromtimestamp(t // 1000000000)