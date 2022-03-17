import logging
from enum import Enum
from symtable import Symbol
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
from Hive_Utils import return_api_keys, read_csv_db, refresh_account_info, return_trade_bars, return_bars
import sys
import datetime
from datetime import timedelta
import pytz

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


# SYMBOLS>>>Tickers
client_symbols = ['SPY', 'SPDN', 'SPXU', 'SPXL', 'TQQQ', 'SQQQ', 'AAPL', 'GOOG', 'VIX']
LongTerm_symbols = ['AAPL', 'GOOGL', 'MFST', 'VIT', 'HD', 'WMT', 'MOOD', 'LIT', 'SPXL', 'TQQQ']
BeeHunter = {
	'LongX3': {'TQQQ': 'TQQQ', 'SPXL': 'SPXL'},
	'ShortX3': {'SQQQ':'SQQQ', 'SPXU': 'SPXU'},
	'Long':  {'SPY': 'SPY', 'QQQQ': 'QQQQ'}
}
#LongTerm_symbols = ?Weight Each Symbol? or just you assests and filter on Market Cap & VOL SECTOR, EBITDA, Free Cash Flow

"""Account Infomation """
acc_info = 	refresh_account_info(api)

# Main Alloc
portvalue_LT_iniate = acc_info[1]['portfolio_value'] * Long_Term_Client_Input
portvalue_MID_iniate = acc_info[1]['portfolio_value'] * MidDayLag_Alloc
portvalue_BeeHunter_iniate = acc_info[1]['portfolio_value'] * DayRiskAlloc


# check alloc correct
if round(portvalue_BeeHunter_iniate + portvalue_MID_iniate + portvalue_LT_iniate - acc_info[1]['portfolio_value'],4) > 1:
	print("break in Rev Alloc")
	sys.exit()

# MAX Intra-Day (4x)

def return_MACD(df, fast, slow):
	# fast=12
	# slow=26
	macd = df.ta.macd(close='close', fast=fast, slow=slow, append=True) 
	return macd

def return_VWAP(df):
	# VWAP
	df = df.assign(
		vwap=df.eval(
			'wgtd = close * volume', inplace=False
		).groupby(df['timestamp']).cumsum().eval('wgtd / volume')
	)
	return df

def relative_strength_index(frame):
    delta = frame['close'].diff()
    up = delta.clip(lower=0)
    down = -1 * delta.clip(upper=0)
    ema_up = up.ewm(com=13, adjust=False).mean()
    ema_down = down.ewm(com=3, adjust=False).mean()
    rsi = ema_up/ema_down
    frame['rsi'] = rsi

    return frame

def return_RSI(df):
	window_length = 14
	df['diff'] = df.diff(1)
	df['gain'] = df['diff'].clip(lower=0).round(2)
	df['loss'] = df['diff'].clip(upper=0).abs().round(2)
	# Get initial Averages
	df['avg_gain'] = df['gain'].rolling(window=window_length, min_periods=window_length).mean()[:window_length+1]
	df['avg_loss'] = df['loss'].rolling(window=window_length, min_periods=window_length).mean()[:window_length+1]
	# Get WMS averages
	# Average Gains
	for i, row in enumerate(df['avg_gain'].iloc[window_length+1:]):
		df['avg_gain'].iloc[i + window_length + 1] =\
			(df['avg_gain'].iloc[i + window_length] *
			(window_length - 1) +
			df['gain'].iloc[i + window_length + 1])\
			/ window_length
	# Average Losses
	for i, row in enumerate(df['avg_loss'].iloc[window_length+1:]):
		df['avg_loss'].iloc[i + window_length + 1] =\
			(df['avg_loss'].iloc[i + window_length] *
			(window_length - 1) +
			df['loss'].iloc[i + window_length + 1])\
			/ window_length

	# Calculate RS Values
	df['rs'] = df['avg_gain'] / df['avg_loss']
	# Calculate RSI
	df['rsi'] = 100 - (100 / (1.0 + df['rs']))


def return_RSI(df):
	# Define function to calculate the RSI
from typing import Callable
close = df['close']
length = 14
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
rsi_sma = calc_rsi(close, lambda s: s.rolling(length).mean())
rsi_rma = calc_rsi(close, lambda s: s.ewm(alpha=1 / length).mean())  # Approximates TradingView.


def return_ticker_min(symbol, time, ndays, trading_days_df=trading_days_df):
	
	time = '1Min'
	symbol = 'SPY'
	m = return_bars(symbol=symbol, time=time, ndays=ndays, trading_days_df=trading_days_df)
	mk_hrs_data = m[1] # market hours data frame only (0 = all, 1=mk hours, 3=afterhours)
	mk_hrs_data['vwap_original'] = mk_hrs_data['vwap']
	# del mk_hrs_data['vwap']
	df_vwap = return_VWAP(mk_hrs_data)
	df_vwap_rsi = relative_strength_index(df_vwap)
	df_vwap_rsi_macd = return_MACD(df_vwap_rsi, fast=12, slow=16)


def return_ticker_5day(symbol, timetype, ndays):
	timetype = '1Min'
	symbol = 'SPY'
	spy_5day = return_bars(symbol=symbol, timetype=timetype, ndays=ndays, trading_days_df=trading_days_df)


def return_ticker_1yr(symbol, time):
	time = tradeapi.TimeFrame(1, tradeapi.TimeFrameUnit.Day) # every day
	start_date1yr = (datetime.datetime.now() - datetime.timedelta(days=client_days1yrmac_input)).strftime('%Y-%m-%d')
	end_date1yr = start_date
	# spy_1yr = return_bars(api=api, symbol='SPY', timeframe=perMin, start_date=start_date, end_date=end_date) # return 1 yr Mac
	spy_1yr = return_bars(api=api, symbol=symbol, timeframe=time, start_date=start_date1yr, end_date=end_date1yr) # return 1 yr Mac


# return VIX


def return_db(csv_name, symbol):
	symbol = True
	csv_name = "SPY_bars.csv"
	symbol, filename = csv_name.split("_")
	type='bars'
	db = read_csv_db(db_root=(os.path.join((os.getcwd()), 'db')), type=type, symbol=symbol)
	# symbol = 'SPY'
	perMin = tradeapi.TimeFrame(1, tradeapi.TimeFrameUnit.Minute) # every second
	FiveperMin = tradeapi.TimeFrame(5, tradeapi.TimeFrameUnit.Minute) # every second
	tday = tradeapi.TimeFrame(1, tradeapi.TimeFrameUnit.Day) # every day



# check before executing final Trade [distance between bid/ask, momentum value of ticker, momentum of market] 


#### >>>>>>>>>>>>>>>>>>> END <<<<<<<<<<<<<<<<<<###

# Day Trading Margin Requirements
# dtbp = 4 x prev_eod_excess_margin
# prev_eod_excess_margin = prev_equity - prev_maintenance_margin
# dtbp = 4 x (prev_equity - prev_maintenance_margin)


""" not using

def return_ticker_min(symbol, time, sec_n):
	# how should 1 day 1 min be built? start to now every time? 
	# or store in dict and return increment? WINNER
		# first call returns up until now & then second returns stored main_df

	now = datetime.datetime.now()
	main_time = pd.DataFrame()

	symbol = 'SPY'
	sec_n = 10000 # 1 day: 27000, 5min: 330
	min = sec_n / 60
	time = tradeapi.TimeFrame(1, tradeapi.TimeFrameUnit.Minute) # every second

	start_date_iso = datetime.datetime.now().strftime('%Y-%m-%d') + ' 19:00'
	a = datetime.datetime.strptime(start_date_iso, '%Y-%m-%d %H:%M')
	# a = datetime.datetime.now()
	b = a + datetime.timedelta(0, sec_n) # days, seconds, then other fields.
	end_date_iso = str(b)[:16]
	
	now = datetime.datetime.now()

	# spy_1min = return_bars(api=api, symbol='SPY', timeframe=time, start_date=start_date, end_date=end_date) # return 1 Day Mac
	spy_1min = return_trade_bars(symbol, start_date_iso, end_date_iso, limit=None)
	spy_1min = spy_1min.reset_index()
	df_calc = return_VWAP(spy_1min)
	df_calc = return_MACD(spy_1min, fast=12, slow=16)

"""