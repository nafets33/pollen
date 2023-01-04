
import logging
from enum import Enum
from operator import sub
from signal import signal
from symtable import Symbol
import time
import asyncio
import os
import pandas as pd
import numpy as np
import pandas_ta as ta
import sys
from dotenv import load_dotenv
import sys
import datetime
from datetime import date, timedelta
import pytz
from typing import Callable
from tqdm import tqdm
from collections import defaultdict
from collections import deque
# from QueenHive import return_Ticker_Universe, init_logging, return_macd, return_VWAP, return_RSI, return_sma_slope, init_pollen_dbs, pollen_story, ReadPickleData, PickleData,  return_bars_list, return_bars, init_index_ticker, print_line_of_error, return_index_tickers
import argparse
import aiohttp
import asyncio
from itertools import islice
import ipdb
from QueenHive_sandbox import return_alpaca_api_keys, return_VWAP, return_RSI, return_macd, return_sma_slope, pollen_story
est = pytz.timezone("US/Eastern")

load_dotenv(os.path.join(os.getcwd(), '.env'))

trading_days = api.get_calendar()
trading_days_df = pd.DataFrame([day._raw for day in trading_days])
trading_days_df['date'] = pd.to_datetime(trading_days_df['date'])

api = return_alpaca_api_keys(prod=False)['api']

def init_QUEENWORKER(queens_chess_piece='castle'):

    QUEEN = { # To Go To The Queens Mind

        # Worker Bees
        queens_chess_piece: {
        'conscience': {'STORY_bee': {},'KNIGHTSWORD': {}, 'ANGEL_bee': {}},
        'pollenstory': {}, # latest story of dataframes castle and bishop
        'pollencharts': {}, # latest chart rebuild
        'pollencharts_nectar': {}, # latest chart rebuild with indicators
        'pollenstory_info': {}, # Misc Info,
        'client': {},
        'heartbeat': {'cycle_time': deque([], 89)},
        'last_modified' : datetime.datetime.now(est),
        'triggerBee_frequency' : {},
        }
    }

    return QUEEN


def return_bars_list(ticker_list, chart_times, crypto=False, exchange=False):
    try:
        s = datetime.datetime.now(est)
        # ticker_list = ['SPY', 'QQQ']
        # chart_times = {
        #     "1Minute_1Day": 0, "5Minute_5Day": 5, "30Minute_1Month": 18, 
        #     "1Hour_3Month": 48, "2Hour_6Month": 72, 
        #     "1Day_1Year": 250
        #     }
        return_dict = {}
        error_dict = {}

        for charttime, ndays in chart_times.items():
            timeframe = charttime.split("_")[0] # '1Minute_1Day'

            trading_days_df_ = trading_days_df[trading_days_df['date'] < current_date] # less then current date
            start_date = trading_days_df_.tail(ndays).head(1).date
            start_date = start_date.iloc[-1].strftime("%Y-%m-%d")
            end_date = datetime.datetime.now(est).strftime("%Y-%m-%d")

            if exchange:
                symbol_data = api.get_crypto_bars(ticker_list, timeframe=timeframe,
                                            start=start_date,
                                            end=end_date,
                                            exchanges=exchange).df
            else:
                symbol_data = api.get_bars(ticker_list, timeframe=timeframe,
                                        start=start_date,
                                        end=end_date, 
                                        adjustment='all').df
            
            # set index to EST time
            symbol_data['timestamp_est'] = symbol_data.index
            symbol_data['timestamp_est'] = symbol_data['timestamp_est'].apply(lambda x: x.astimezone(est))
            symbol_data['timeframe'] = timeframe
            symbol_data['bars'] = 'bars_list'
            
            symbol_data = symbol_data.reset_index(drop=True)
            # if ndays == 1:
            #     symbol_data = symbol_data[symbol_data['timestamp_est'] > (datetime.datetime.now(est).replace(hour=1, minute=1, second=1))].copy()

            return_dict[charttime] = symbol_data


            if len(symbol_data) == 0:
                error_dict[ticker_list] = {'msg': 'no data returned', 'time': time}
                return False


        e = datetime.datetime.now(est)

        return {'resp': True, 'return': return_dict}

    except Exception as e:
        print("sending email of error", e)
        er_line = print_line_of_error()
        logging_log_message(log_type='critical', msg='bars failed', error=f'error {e}  error line {str(er_line)}')


def return_getbars_WithIndicators(bars_data, MACD):

    # time = '1Minute' #TEST
    # symbol = 'SPY' #TEST
    # ndays = 1
    # bars_data = return_bars(symbol, time, ndays, trading_days_df=trading_days_df)

    try:
        # s = datetime.datetime.now(est) #TEST
        bars_data['vwap_original'] = bars_data['vwap']
        # del mk_hrs_data['vwap']
        df_vwap = return_VWAP(bars_data)
        # df_vwap = vwap(bars_data)

        df_vwap_rsi = return_RSI(df=df_vwap, length=14)
        # append_MACD(df_vwap_rsi_macd, fast=MACD['fast'], slow=MACD['slow'])
        df_vwap_rsi_macd = return_macd(df_main=df_vwap_rsi, fast=MACD['fast'], slow=MACD['slow'], smooth=MACD['smooth'])
        df_vwap_rsi_macd_smaslope = return_sma_slope(df=df_vwap_rsi_macd, time_measure_list=[3, 6, 23, 33], y_list=['close', 'macd', 'hist'])
        # e = datetime.datetime.now(est)
        # print(str((e - s)) + ": " + datetime.datetime.now().strftime("%A, %d. %B %Y %I:%M%p"))
        # 0:00:00.198920: Monday, 21. March 2022 03:02PM 2 days 1 Minute
        return [True, df_vwap_rsi_macd_smaslope]
    except Exception as e:
        # print("log error", print_line_of_error())
        # return [False, e, print_line_of_error()]
        print(e)


# QUEEN[queens_chess_piece]['pollencharts_nectar'] = bars_data__WithIndicators
# {SPY_1Minute_1Day: }
# SPY_5Minute_5Day

pollen_story(pollen_nectar=QUEEN[queens_chess_piece]['pollencharts_nectar'])

# 1
# return bars into a new DB (pickle file db) for the past week
# pkl['1/3/2022'] = {SPY: bars_data, ticker1: bars_data}

# step 2
# retuns indicators & pollen_story

# final output 

###
# 3
# basic grid search of the params