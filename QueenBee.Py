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
from Hive_Utils import *
load_dotenv()

logging.basicConfig(
	filename='QueenBee.log',
	level=logging.WARNING,
	format='%(asctime)s:%(levelname)s:%(message)s',
)

keys = return_api_keys()
rest = keys['rest']
api = keys['api']

client_symbols = ['SPY', 'SPDN', 'SPXU', 'SPXL', 'TQQQ', 'SQQQ', 'AAPL', 'GOOG']