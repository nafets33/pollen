# QueenTics
import logging
from enum import Enum
from signal import signal
from symtable import Symbol
import time
import alpaca_trade_api as tradeapi
import asyncio
import os
import pandas as pd
import numpy as np
import pandas_ta as ta
import sys
from alpaca_trade_api.rest import TimeFrame, URL
from alpaca_trade_api.rest_async import gather_with_concurrency, AsyncRest
from dotenv import load_dotenv
import threading
from QueenHive import ReadPickleData, PickleData, return_api_keys, return_bars_list, refresh_account_info, return_bars, rebuild_timeframe_bars, init_index_ticker, print_line_of_error, return_index_tickers
import sys
import datetime
from datetime import date, timedelta
import pytz
from typing import Callable
import random
import collections
import pickle
from tqdm import tqdm
from stocksymbol import StockSymbol
import requests
from collections import defaultdict
import ipdb
import tempfile
import shutil

prod = True
pd.options.mode.chained_assignment = None
est = pytz.timezone("US/Eastern")
load_dotenv()
# >>> initiate db directories
system = 'windows' #mac, windows
if system != 'windows':
    db_root = os.environ.get('db_root_mac')
else:
    db_root = os.environ.get('db_root_winodws')

queens_chess_piece = sys.argv[1] # 'castle', 'knight', 'workerbee'
if queens_chess_piece.lower() not in ['castle', 'knight', 'bishop', 'workerbee']:
    print("wrong chess move")
    sys.exit()


scriptname = os.path.basename(__file__)
log_dir = dst = os.path.join(db_root, 'logs')
if os.path.exists(dst) == False:
    os.mkdir(dst)
log_name = f'{"log_"}{queens_chess_piece}{".log"}'
log_file = os.path.join(os.getcwd(), log_name)
if os.path.exists(log_file) == False:
    logging.basicConfig(filename=f'{"log_"}{queens_chess_piece}{".log"}',
                        filemode='a',
                        format='%(asctime)s:%(name)s:%(levelname)s: %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p',
                        level=logging.INFO)
else:
    # copy log file to log dir & del current log file
    datet = datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S_%p')
    dst_path = os.path.join(log_dir, f'{log_name}{"_"}{datet}{".log"}')
    shutil.copy(log_file, dst_path)
    os.remove(log_file)
    logging.basicConfig(filename=f'{"log_"}{queens_chess_piece}{".log"}',
                        filemode='a',
                        format='%(asctime)s:%(name)s:%(levelname)s: %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p',
                        level=logging.INFO)

# Client Tickers
src_root, db_dirname = os.path.split(db_root)
client_ticker_file = os.path.join(src_root, 'client_tickers.csv')
df_client = pd.read_csv(client_ticker_file, dtype=str)
client_symbols = df_client.tickers.to_list()


""" Keys """
api_key_id = os.environ.get('APCA_API_KEY_ID')
api_secret = os.environ.get('APCA_API_SECRET_KEY')
base_url = "https://api.alpaca.markets"
keys = return_api_keys(base_url, api_key_id, api_secret)
rest = keys[0]['rest']
api = keys[0]['api']

# Paper
api_key_id_paper = os.environ.get('APCA_API_KEY_ID_PAPER')
api_secret_paper = os.environ.get('APCA_API_SECRET_KEY_PAPER')
base_url_paper = "https://paper-api.alpaca.markets"
keys_paper = return_api_keys(base_url=base_url_paper, 
    api_key_id=api_key_id_paper, 
    api_secret=api_secret_paper,
    prod=False)
rest_paper = keys_paper[0]['rest']
api_paper = keys_paper[0]['api']

"""# Dates """
# current_day = api.get_clock().timestamp.date().isoformat()
trading_days = api.get_calendar()
trading_days_df = pd.DataFrame([day._raw for day in trading_days])

current_day = datetime.datetime.now().day
current_month = datetime.datetime.now().month
current_year = datetime.datetime.now().year

PB_Story_Pickle = os.path.join(db_root, f'{queens_chess_piece}{".pkl"}')
if queens_chess_piece == 'workerbee':
    if os.path.exists(PB_Story_Pickle):
        os.remove(PB_Story_Pickle)

def return_sma_slope(df, y_list, time_measure_list):
        # df=pollenstory['SPY_1Minute_1Day'].copy()
        # time_measure_list = [3, 23, 33]
        # y_list = ['close', 'macd', 'hist']
        for mtime in time_measure_list:
            for el in y_list:
                sma_name = f'{el}{"_sma-"}{mtime}'
                slope_name = f'{el}{"_slope-"}{mtime}'
                df[sma_name] = df[el].rolling(mtime).mean().fillna(0)
                df[slope_name] = np.degrees(np.arctan(df[sma_name].diff()/mtime))
        return df

while True:
        if queens_chess_piece.lower() == 'workerbee': # return tics
            s = datetime.datetime.now()
            r = rebuild_timeframe_bars(ticker_list=client_symbols, build_current_minute=False, min_input=0, sec_input=30) # return all tics
            resp = r['resp'] # return slope of collective tics
            for symbol in set(resp['symbol'].to_list()):
                df = resp[resp['symbol']==symbol].copy()
                df = df.reset_index()
                df_len = len(df)
                rolling_times = [round(df_len / 4), round(df_len / 2)]
                df = return_sma_slope(df=df, y_list=['price'], time_measure_list=rolling_times)

            e = datetime.datetime.now()
            print(queens_chess_piece, str((e - s)) + ": " + datetime.datetime.now().strftime("%A, %d. %B %Y %I:%M:%S%p"))