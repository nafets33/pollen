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
from Hive_Utils import return_api_keys, read_csv_db, account_info
import sys
import datetime
from datetime import timedelta
load_dotenv()

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
# def init_main_portfolio_account():
info = api.get_account()
account_number = info.account_number
accrued_fees = float(info.accrued_fees)
buying_power = float(info.buying_power)
cash = float(info.cash)
daytrade_count = info.daytrade_count
last_equity = float(info.last_equity)
portfolio_value = float(info.portfolio_value)
sma = info.sma
# return True

# Main Alloc
portvalue_LT_iniate = float(portfolio_value) * Long_Term_Client_Input
portvalue_MID_iniate = float(portfolio_value) * MidDayLag_Alloc
portvalue_BeeHunter_iniate = float(portfolio_value) * DayRiskAlloc
BeeHunter_Max_Intra_day = 3.9 * cash

# check alloc correct
if round(portvalue_BeeHunter_iniate + portvalue_MID_iniate + portvalue_LT_iniate - float(portfolio_value),4) > 1:
	print("break in Rev Alloc")
	sys.exit()

# MAX Intra-Day (4x)

def return_bars(api, symbol, timeframe, start_date, end_date):
    # SYMBOL = 'SPY'
    # time = 1
    # timeframe = tradeapi.TimeFrame(1, tradeapi.TimeFrameUnit.Minute) # every second
    
    ticker = api.get_bars(symbol, timeframe, start_date, end_date) # '2022-02-11', '2022-02-11'
    df = ticker.df.reset_index()

    # macd = df.ta.macd(close='close', fast=12, slow=26, append=True)
    # print(df.iloc[-1])

    return df


def FamilyNest(df):
	macd = df.ta.macd(close='close', fast=12, slow=26, append=True)

def StartTheDay():
	db = read_csv_db(db_root=os.path.join((os.getcwd()), 'db'))
	# symbol = 'SPY'
	perMin = tradeapi.TimeFrame(1, tradeapi.TimeFrameUnit.Minute) # every second
	FiveperMin = tradeapi.TimeFrame(5, tradeapi.TimeFrameUnit.Minute) # every second
	tday = tradeapi.TimeFrame(1, tradeapi.TimeFrameUnit.Day) # every day

	start_date1yr = (datetime.datetime.now() - datetime.timedelta(days=client_days1yrmac_input)).strftime('%Y-%m-%d')
	end_date1yr = start_date
	# spy_1yr = return_bars(api=api, symbol='SPY', timeframe=perMin, start_date=start_date, end_date=end_date) # return 1 yr Mac
	spy_1yr = return_bars(api=api, symbol='SPY', timeframe=tday, start_date=start_date1yr, end_date=end_date1yr) # return 1 yr Mac
	
	start_day_5day = (datetime.datetime.now() - datetime.timedelta(days=client_daysT2Mac_input)).strftime('%Y-%m-%d')
	end_date_5day = start_date
	spy_5day = return_bars(api=api, symbol='SPY', timeframe=FiveperMin, start_date=start_day_5day, end_date=end_date_5day) # return 5 day Mac
	
	spy_1min = return_bars(api=api, symbol='SPY', timeframe=perMin, start_date=start_date, end_date=end_date) # return 1 Day Mac
	
	# return RSI
	# return VIX

