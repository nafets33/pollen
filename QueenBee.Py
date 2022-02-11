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
from Hive_Utils import return_api_keys, read_csv_db, account_info
import sys
load_dotenv()

logging.basicConfig(
	filename='QueenBee.log',
	level=logging.WARNING,
	format='%(asctime)s:%(levelname)s:%(message)s',
)

# Main Arguments
client_num_LT = sys.argv[1]
client_num_ST = sys.argv[2]

# Customer Setup
num = {1: .15, 2: .25, 3: .40, 4: .60, 5: .8}
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
client_symbols = ['SPY', 'SPDN', 'SPXU', 'SPXL', 'TQQQ', 'SQQQ', 'AAPL', 'GOOG']
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

def StartTheDay():
	db = read_csv_db(db_root=os.path.join((os.getcwd()), 'db'))
	return_bars = # return 1 yr Mac
	# return 5 day Mac
	# return 1 Day Mac
	# return RSI
	# return VIX

def return_bars(api, symbol, timeframe, start_date, end_date):
    # SYMBOL = 'SPY'
    # time = 1
    # timeframe = tradeapi.TimeFrame(1, tradeapi.TimeFrameUnit.Minute) # every second
    
    ticker = api.get_bars(symbol, timeframe, start_date, end_date) # '2022-02-11', '2022-02-11'
    df = ticker.df.reset_index()

    macd = df.ta.macd(close='close', fast=12, slow=26, append=True)
    # print(df.iloc[-1])

    return 