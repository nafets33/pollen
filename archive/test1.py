from datetime import datetime
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
q = api.get_latest_quote("SPY")
d = vars(q)
d["_raw"]

api.get_latest_trade("SPY")
Out[55]: 
TradeV2({   'c': [' ', 'F'],
    'i': 52983610165572,
    'p': 423.93,
    's': 100,
    't': '2022-03-11T17:55:17.593651968Z',
    'x': 'P',
    'z': 'B'})

# check for submitted orders WEB Socket will return orders then get executed
position = api.get_position('SPY') 
spdn = api.get_position('BABA')
open_orders_list = api.list_orders(status='closed')
open_orders_list = api.list_orders(status='open')
# REFERENCE FOR ALL FIELDS https://alpaca.markets/docs/api-references/trading-api/orders/



order1 = api.submit_order(symbol='SPY', 
        qty=1, 
        side='buy', # buy, sell 
        time_in_force='gtc', # 'day'
        type='market', # 'market'
        ) # optional make sure it unique though to call later!
order2 = api.submit_order(symbol='SPY', 
        qty=1, 
        side='sell', # buy, sell 
        time_in_force='gtc', # 'day'
        type='market', # 'market'
        ) # optional make sure it unique though to call later!


api.get_order_by_client_order_id(client_order_id=client_order_id)

replace = api.replace_order(qty=1, time_in_force='gtc', limit_price='14.71', order_id='98d15a9f-0f1e-4f0f-80c6-1b34719957ec')

    def list_orders(self,
                    status: str = None,
                    limit: int = None,
                    after: str = None,
                    until: str = None,
                    direction: str = None,
                    params=None,
                    nested: bool = None,
                    symbols: List[str] = None
                    )

api_paper.list_orders(status, symbols, after, until, direction,  limit=500)

def initiate_orders(api, symbols=False, start_date=(datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y-%m-%d"), end_date=(datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%Y-%m-%d")):

    if start_date==(datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y-%m-%d"):
        after = start_date
        until = end_date
        if symbols:
            closed_orders = api.list_orders(status='closed', symbols=symbols, after=after, until=until)
            open_orders = api.list_orders(status='open', symbols=symbols, after=after, until=until)
        else:
            closed_orders = api.list_orders(status='closed', after=after, until=until)
            open_orders = api.list_orders(status='open', after=after, until=until)
        
        return {'open': open_orders, 'closed': closed_orders}
    
    else:
        print("TDB chunk the dates and return all orders per day for x days")
        start_date = '2022-06-01'
        # count num of says from start and end
        # for every day return all closed orders
        # end_date = (datetime.datetime.now() - datetime.timedelta(days=1)) 
        # after = start_date
        # until = end_date
        # api_paper.list_orders(status='closed', symbols=symbols, after=after, until=until)
        pass

    # after = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    # api_paper.list_orders(status='closed', symbols=['SPY'], after=after)

def handle_order_submission(trig_side):
    trig_side = 'sell' # 'buy'
    order = submit_order(api=api, symbol=QUEEN['heartbeat']['main_indexes'][ticker]['inverse'], type='market', qty=1, side='buy', client_order_id=trig) # buy
    QUEEN['command_conscience']['orders'].append({'ticker': ticker, 'order': order, 'datetime': datetime.datetime.now()})


trigger_dict = {'triggers': {'buy_cross-0': {'timeduration': 1, 
                                              'profit_take': .001,
                                              'sellout': .01,
                                              'adjustable': True,
                                                },
                            'sell_cross-0': {'timeduration': 1, 
                                              'profit_take': .001,
                                              'sellout': .01,
                                              'adjustable': True,
                                                },}
}

# for every trigger adjust order based on the story of other ttframes                               

def convert_nano_timestamp_to_datetime(t):
    return datetime.datetime.utcfromtimestamp(t // 1000000000)

def convert_todatetime_string(date_string):
    # In [94]: date_string
    # Out[94]: '2022-03-11T19:41:50.649448Z'
    # In [101]: date_string[:19]
    # Out[101]: '2022-03-11T19:41:50'
    return datetime.datetime.fromisoformat(date_string[:19])


df1 = df.assign(
    vwap=df.eval(
        'wgtd = close * volume', inplace=False
    ).groupby(df['timestamp']).cumsum().eval('wgtd / volume')
)
df


ts = pd.Timestamp('2022-02-17 09:30:00', tz='EST')




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
s = datetime.datetime.now()
start_time = pd.to_datetime('2022-02-18 19:00', utc=True)
end_time = pd.to_datetime('2022-02-18 20:00', utc=True)
symbol = 'SPY'

trades_df = api.get_trades(symbol=symbol, start=start_time.isoformat(), end=end_time.isoformat(), limit=None).df

# convert to market time for easier reading
trades_df = trades_df.tz_convert('America/New_York')

# add a column to easily identify the trades to exclude using our function from above
trades_df['exclude'] = trades_df.conditions.apply(has_condition, condition_check=exclude_conditions)

# filter to only look at trades which aren't excluded
valid_trades = trades_df.query('not exclude')

# Resample the valid trades to calculate the OHLCV bars
agg_functions = {'price': ['first', 'max', 'min', 'last'], 'size': 'sum'}
min_bars = valid_trades.resample('1T').agg(agg_functions)
e = datetime.datetime.now()
print(e-s)

# VWAP
df1 = df.assign(
    vwap=df.eval(
        'wgtd = close * volume', inplace=False
    ).groupby(df['timestamp']).cumsum().eval('wgtd / volume')
)
df

# timezome est
ts = pd.Timestamp('2022-02-17 09:30:00', tz='EST')

s = datetime.datetime.now()
x = return_trade_bars(symbol, start_date_iso, end_date_iso, limit=None)
e = datetime.datetime.now()
print(e-s)



import logging
logging.basicConfig(level=logging.INFO)

def hypotenuse(a, b):
    """Compute the hypotenuse"""
    return (a**2 + b**2)**0.5

kwargs = {'a':3, 'b':4, 'c':hypotenuse(3, 4)}

logging.debug("a = {a}, b = {b}".format(**kwargs))
logging.info("Hypotenuse of {a}, {b} is {c}".format(**kwargs))
logging.warning("a={a} and b={b} are equal".format(**kwargs))
logging.error("a={a} and b={b} cannot be negative".format(**kwargs))
logging.critical("Hypotenuse of {a}, {b} is {c}".format(**kwargs))


# Assumes api and api_data are instantiated REST objects for the trading account and the data account respectively.
# These can be the same but I separate them to be able to use data in several accounts

import pandas as pd

def return_bars(symbol, timetype, ndays):
    try:
        # ndays = 10
        # timetype = "1Day" # "1Min"
        # symbol = 'SPY'
        
        # First get the current day and all trading days
        current_day = api.get_clock().timestamp.date().isoformat()
        trading_days = api.get_calendar()

        # Convert trading days to a Dataframe for easier manipulation
        # Select the 10 days before the current day
        trading_days_df = pd.DataFrame([day._raw for day in trading_days])
        symbol_n_days = trading_days_df.query('date < @current_day').tail(ndays)

        # Fetch bars for those days
        symbol_data = api.get_bars(symbol, timetype,
                                    start=symbol_n_days.head(1).date,
                                    end=symbol_n_days.tail(1).date, 
                                    adjustment='all').df.reset_index()
        est = pytz.timezone("US/Eastern")
        symbol_data['timestamp_est'] = symbol_data['timestamp'].apply(lambda x: x.astimezone(est))
        return symbol_data
    # handle error
    except Exception as e:
        print("sending email of error", e)


THANKYOU_DAN_THEMAN = return_bars(symbol='SPY', timetype='1Min', ndays=10)