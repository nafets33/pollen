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

logging.basicConfig(
	filename='QueenBee.log',
	level=logging.WARNING,
	format='%(asctime)s:%(levelname)s:%(message)s',
)

# Main Arguments
num = {1: .15, 2: .25, 3: .40, 4: .60, 5: .8}
client_num_LT = 1
client_num_ST = 3
client_days1yrmac_input = 233 # Tier 1
client_daysT2Mac_input = 5 # Tier 2
client_daysT3Mac_input = 233 # Tier 3


# client_num_LT = sys.argv[1]
# client_num_ST = sys.argv[2]
# client_days1yrmac_input = sys.argv[3]

start_date = datetime.datetime.now().strftime('%Y-%m-%d')
end_date = datetime.datetime.now().strftime('%Y-%m-%d')

# Customer Setup
Long_Term_Client_Input = num[client_num_LT]
MidDayLag_Alloc = num[client_num_ST]
DayRiskAlloc = 1 - (Long_Term_Client_Input + MidDayLag_Alloc)

# Keys
api_key_id = os.environ.get('APCA_API_KEY_ID')
api_secret = os.environ.get('APCA_API_SECRET_KEY')
base_url = "https://api.alpaca.markets"
keys = return_api_keys(base_url, api_key_id, api_secret)
rest = keys[0]['rest']
api = keys[0]['api']

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


def return_ticker_5day(symbol, time):
	time = tradeapi.TimeFrame(5, tradeapi.TimeFrameUnit.Minute) # every second
	start_day_5day = (datetime.datetime.now() - datetime.timedelta(days=client_daysT2Mac_input)).strftime('%Y-%m-%d')
	end_date_5day = start_date
	spy_5day = return_bars(api=api, symbol=symbol, timeframe=time, start_date=start_day_5day, end_date=end_date_5day) # return 5 day Mac


def return_ticker_1yr(symbol, time):
	time = tradeapi.TimeFrame(1, tradeapi.TimeFrameUnit.Day) # every day
	start_date1yr = (datetime.datetime.now() - datetime.timedelta(days=client_days1yrmac_input)).strftime('%Y-%m-%d')
	end_date1yr = start_date
	# spy_1yr = return_bars(api=api, symbol='SPY', timeframe=perMin, start_date=start_date, end_date=end_date) # return 1 yr Mac
	spy_1yr = return_bars(api=api, symbol=symbol, timeframe=time, start_date=start_date1yr, end_date=end_date1yr) # return 1 yr Mac


# return RSI
# return VIX

# check before executing final Trade [distance between bid/ask, momentum value of ticker, momentum of market] 
start_date_iso = datetime.datetime.now().strftime('%Y-%m-%d') + ' 19:00'
a = datetime.datetime.strptime(start_date_iso, '%Y-%m-%d %H:%M')
now = datetime.datetime.now()
a - now
b = a + datetime.timedelta(0, sec_n) # days, seconds, then other fields.
return_ticker_min(symbol='SPY', time=False, sec_n)
#### >>>>>>>>>>>>>>>>>>> END <<<<<<<<<<<<<<<<<<###

# Day Trading Margin Requirements
# dtbp = 4 x prev_eod_excess_margin
# prev_eod_excess_margin = prev_equity - prev_maintenance_margin
# dtbp = 4 x (prev_equity - prev_maintenance_margin)