# QueenBee Workers
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
from King import init_symbol_dbs__pollenstory, hive_master_root, read_QUEEN

# import tempfile
# import shutil
# from scipy.stats import linregress
# from scipy import stats
# import hashlib
# import json
# from stocksymbol import StockSymbol
# import requests
# import random
# import collections
# import pickle
# import threading
# from alpaca_trade_api.rest import TimeFrame, URL
# from alpaca_trade_api.rest_async import gather_with_concurrency, AsyncRest
# import alpaca_trade_api as tradeapi


# FEAT List
# rebuild minute bar with high and lows, store current minute bar in QUEEN, reproduce every minute
def queen_workerbees(prod, bee_scheduler=False, queens_chess_piece='bees_manager'):

    # script arguments
    if bee_scheduler:
        prod = prod
        queens_chess_piece = queens_chess_piece
    else:
        def createParser_workerbees():
            parser = argparse.ArgumentParser()
            parser.add_argument ('-qcp', default="workerbee")
            parser.add_argument ('-prod', default=True)
            # parser.add_argument ('-windows', default=False)

            return parser

        # script arguments
        parser = createParser_workerbees()
        namespace = parser.parse_args()
        queens_chess_piece = namespace.qcp # 'castle', 'knight' 'queen'
        prod = True if namespace.prod.lower() == 'true' else False

    if prod:
        print("Production")
        from QueenHive import return_alpaca_api_keys, return_Ticker_Universe, init_logging, return_macd, return_VWAP, return_RSI, return_sma_slope, init_pollen_dbs, pollen_story, ReadPickleData, PickleData,  return_bars_list, return_bars, init_index_ticker, print_line_of_error, return_index_tickers
        load_dotenv(os.path.join(os.getcwd(), '.env_jq'))
    else:
        print("Sandbox")
        from QueenHive_sandbox import return_alpaca_api_keys, return_Ticker_Universe, init_logging, return_macd, return_VWAP, return_RSI, return_sma_slope, init_pollen_dbs, pollen_story, ReadPickleData, PickleData,  return_bars_list, return_bars, init_index_ticker, print_line_of_error, return_index_tickers
        load_dotenv(os.path.join(os.getcwd(), '.env'))

    # if windows:
    #     asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy()) # needed to work on Windows
    if queens_chess_piece.lower() not in ['workerbee', 'bees_manager']:
        print("wrong chess move")
        sys.exit()

    pd.options.mode.chained_assignment = None
    est = pytz.timezone("US/Eastern")

    
    main_root = hive_master_root() #os.getcwd()
    db_root = os.path.join(main_root, 'db')

    init_logging(queens_chess_piece=queens_chess_piece, db_root=db_root, prod=prod)


    # Macd Settings
    # MACD_12_26_9 = {'fast': 12, 'slow': 26, 'smooth': 9}
    def init_QUEENWORKER(queens_chess_piece):

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



    """ Keys """
    api = return_alpaca_api_keys(prod=prod)['api']

    """# Dates """
    # current_day = api.get_clock().timestamp.date().isoformat()
    # trading_days = api.get_calendar()
    # trading_days_df = pd.DataFrame([day._raw for day in trading_days])

    current_date = datetime.datetime.now(est).strftime("%Y-%m-%d")
    trading_days = api.get_calendar()
    trading_days_df = pd.DataFrame([day._raw for day in trading_days])
    trading_days_df['date'] = pd.to_datetime(trading_days_df['date'])


    current_day = datetime.datetime.now(est).day
    current_month = datetime.datetime.now(est).month
    current_year = datetime.datetime.now(est).year

    # misc
    exclude_conditions = [
        'B','W','4','7','9','C','G','H','I','M','N',
        'P','Q','R','T','V','Z'
    ] # 'U'

    """# Main Arguments """

    def close_worker():
        s = datetime.datetime.now(est)
        date = datetime.datetime.now(est)
        date = date.replace(hour=16, minute=1)
        if s >= date:
            logging.info("Happy Bee Day End")
            print("Great Job! See you Tomorrow")
            return True
        else:
            return False


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
            print("log error", print_line_of_error())
            return [False, e, print_line_of_error()]


    def Return_Init_ChartData(ticker_list, chart_times): #Iniaite Ticker Charts with Indicator Data
        # ticker_list = ['SPY', 'QQQ']
        # chart_times = {
        #     "1Minute_1Day": 0, "5Minute_5Day": 5, "30Minute_1Month": 18, 
        #     "1Hour_3Month": 48, "2Hour_6Month": 72, 
        #     "1Day_1Year": 250}
        try:
            msg = (ticker_list, chart_times)
            # logging.info(msg)
            # print(msg)

            error_dict = {}
            s = datetime.datetime.now(est)
            dfs_index_tickers = {}
            bars = return_bars_list(ticker_list=ticker_list, chart_times=chart_times, trading_days_df=trading_days_df)      
            # if bars['return']: # rebuild and split back to ticker_time with market hours only
            #     # bars_dfs = bars['return']
            for timeframe, df in bars['return'].items():
                time_frame=timeframe.split("_")[0] # '1day_1year'
                if '1day' in time_frame.lower():
                    for ticker in ticker_list:
                        df_return = df[df['symbol']==ticker].copy()
                        dfs_index_tickers[f'{ticker}{"_"}{timeframe}'] = df_return
                else:
                    df = df.set_index('timestamp_est')
                    market_hours_data = df.between_time('9:30', '16:00')
                    market_hours_data = market_hours_data.reset_index()
                    # market_hours_data = df
                    for ticker in ticker_list:
                        df_return = market_hours_data[market_hours_data['symbol']==ticker].copy()
                        dfs_index_tickers[f'{ticker}{"_"}{timeframe}'] = df_return
            
            e = datetime.datetime.now(est)
            msg = {'function':'Return Init ChartData',  'func_timeit': str((e - s)), 'datetime': datetime.datetime.now(est).strftime('%Y-%m-%d_%H:%M:%S_%p')}
            print(msg)
            # dfs_index_tickers['SPY_5Minute']
            return {'init_charts': dfs_index_tickers, 'errors': error_dict}
        except Exception as e:
            print("eeeeeror", e, print_line_of_error())
            ipdb.set_trace()


    def Return_Bars_LatestDayRebuild(ticker_time): #Iniaite Ticker Charts with Indicator Data
        # IMPROVEMENT: use Return_bars_list for Return Bars_LatestDayRebuild
        # ticker_time = "SPY_1Minute_1Day"

        ticker, timeframe, days = ticker_time.split("_")
        error_dict = {}
        s = datetime.datetime.now(est)
        dfs_index_tickers = {}
        try:
            # return market hours data from bars
            bars_data = return_bars(symbol=ticker, timeframe=timeframe, ndays=0, trading_days_df=trading_days_df) # return [True, symbol_data, market_hours_data, after_hours_data]
            df_bars_data = bars_data['market_hours_data'] # mkhrs if in minutes
            dfs_index_tickers[ticker_time] = df_bars_data
        except Exception as e:
            print(ticker_time, e)
        
        e = datetime.datetime.now(est)
        msg = {'function':'Return_Bars_Latest Day Rebuild',  'func_timeit': str((e - s)), 'datetime': datetime.datetime.now(est).strftime('%Y-%m-%d_%H:%M:%S_%p')}
        # print(msg)
        # dfs_index_tickers['SPY_5Minute']
        return [dfs_index_tickers, error_dict, msg]


    def Return_Snapshots_Rebuild(df_tickers_data, init=False): # from snapshots & consider using day.min.chart to rebuild other timeframes
        
        def ticker_Snapshots(ticker_list, float_cols, int_cols):
            return_dict = {}
            try:
                for ticker in ticker_list:
                    dl = {
                    'close': snapshots[ticker].daily_bar.close,
                    'high': snapshots[ticker].daily_bar.high,
                    'low': snapshots[ticker].daily_bar.low,
                    'timestamp_est': snapshots[ticker].daily_bar.timestamp,
                    'open': snapshots[ticker].daily_bar.open,
                    'volume': snapshots[ticker].daily_bar.volume,
                    'trade_count': snapshots[ticker].daily_bar.trade_count,
                    'vwap': snapshots[ticker].daily_bar.vwap
                    }
                    df_daily = pd.Series(dl).to_frame().T  # reshape dataframe
                    for i in float_cols:
                        # df_daily[i] = df_daily[i].apply(lambda x: float(x))
                        df_daily[i] = df_daily[i].astype(float)
                    for i in int_cols:
                        # df_daily[i] = df_daily[i].apply(lambda x: int(x))
                        df_daily[i] = df_daily[i].astype(int)
                    # df_daily = df_daily.rename(columns={'timestamp': 'timestamp_est'})
                    
                    return_dict[ticker + "_day"] = df_daily

                    d = {
                        'close': snapshots[ticker].latest_trade.price,
                        'high': snapshots[ticker].latest_trade.price,
                        'low': snapshots[ticker].latest_trade.price,
                        'timestamp_est': snapshots[ticker].latest_trade.timestamp,
                        'open': snapshots[ticker].latest_trade.price,
                        'volume': snapshots[ticker].minute_bar.volume,
                        'trade_count': snapshots[ticker].minute_bar.trade_count,
                        'vwap': snapshots[ticker].minute_bar.vwap
                        }
                    df_minute = pd.Series(d).to_frame().T
                    for i in float_cols:
                        # df_minute[i] = df_minute[i].apply(lambda x: float(x))
                        df_minute[i] = df_minute[i].astype(float)
                    for i in int_cols:
                        # df_minute[i] = df_minute[i].apply(lambda x: int(x))
                        df_minute[i] = df_minute[i].astype(int)

                    return_dict[ticker + "_minute"] = df_minute
            except Exception as e:
                print(e)
                print(ticker)
                ipdb.set_trace()
            
            return return_dict
        
        try:
            ticker_list = list([set(j.split("_")[0] for j in df_tickers_data.keys())][0]) #> get list of tickers
            snapshots = api.get_snapshots(ticker_list)

            for ticker in snapshots.keys(): # replace snapshot if in exclude_conditions
                c = 0
                while True:
                    conditions = snapshots[ticker].latest_trade.conditions
                    # print(conditions)
                    invalid = [c for c in conditions if c in exclude_conditions]
                    if len(invalid) == 0 or c > 10:
                        break
                    else:
                        print("invalid trade-condition pull snapshot")
                        snapshot = api.get_snapshot(ticker) # return_last_quote from snapshot
                        snapshots[ticker] = snapshot
                        c+=1

            float_cols = ['close', 'high', 'open', 'low', 'vwap']
            int_cols = ['volume', 'trade_count']
            main_return_dict = {}
            
            # min_bars_dict = rebuild_timeframe_bars(ticker_list)
            # if min_bars_dict['resp'] == False:
            #     print("Min Bars Error", min_bars_dict)
            #     min_bars_dict = {k:{} for k in ticker_list}
            # else:
            #     min_bars_dict = min_bars_dict['resp']
            # min_bars_dict = {k:{} for k in ticker_list} # REBUILDING MIN BARS NEEDS IMPROVEMENT BEFORE SOME MAY FAIL TO RETURN

            snapshot_ticker_data = ticker_Snapshots(ticker_list, float_cols, int_cols)
            
            for ticker_time, df in df_tickers_data.items():
                symbol_snapshots = {k:v for (k,v) in snapshot_ticker_data.items() if k.split("_")[0] == ticker_time.split("_")[0]}
                symbol, timeframe, days = ticker_time.split("_")
                if "day" in timeframe.lower():
                    df_day_snapshot = symbol_snapshots[f'{symbol}{"_day"}'] # stapshot df
                    df_day_snapshot['symbol'] = symbol
                    df = df.head(-1) # drop last row which has current day / added minute
                    df_rebuild = pd.concat([df, df_day_snapshot], join='outer', axis=0).reset_index(drop=True) # concat minute
                    main_return_dict[ticker_time] = df_rebuild
                else:
                    df_snapshot = symbol_snapshots[f'{symbol}{"_minute"}'] # stapshot df
                    df_snapshot['symbol'] = symbol
                    if init:
                        df_rebuild = pd.concat([df, df_snapshot], join='outer', axis=0).reset_index(drop=True) # concat minute
                        main_return_dict[ticker_time] = df_rebuild
                    else:
                        df = df.head(-1) # drop last row which has current day
                        df_rebuild = pd.concat([df, df_snapshot], join='outer', axis=0).reset_index(drop=True) # concat minute
                        main_return_dict[ticker_time] = df_rebuild
        except Exception as e:
            print(e)
            print(queens_chess_piece)
            ipdb.set_trace()
        
        return main_return_dict


    def ReInitiate_Charts_Past_Their_Time(df_tickers_data): # re-initiate for i timeframe 
        # IMPROVEMENT: use Return_bars_list for Return_Bars_LatestDayRebuild
        return_dict = {}
        rebuild_confirmation = {}

        def tag_current_day(timestamp):
            if timestamp.day == current_day and timestamp.month == current_month and timestamp.year == current_year:
                return 'tag'
            else:
                return '0'

        for ticker_time, df in df_tickers_data.items():
            ticker, timeframe, days = ticker_time.split("_")
            last = df['timestamp_est'].iloc[-2]
            now = datetime.datetime.now(est)
            timedelta_minutes = (now - last).seconds / 60
            now_day = now.day
            last_day = last.day
            if now_day != last_day:
                return_dict[ticker_time] = df
                continue
            
            dfn = Return_Bars_LatestDayRebuild(ticker_time)

            if "1minute" == timeframe.lower():
                if timedelta_minutes > 2:
                    if len(dfn[1]) == 0:
                        df_latest = dfn[0][ticker_time]
                        df['timetag'] = df['timestamp_est'].apply(lambda x: tag_current_day(x))
                        df_replace = df[df['timetag']!= 'tag'].copy()
                        del df_replace['timetag']
                        df_return = pd.concat([df_replace, df_latest], join='outer', axis=0).reset_index(drop=True)
                        df_return_me = pd.concat([df_return, df_return.tail(1)], join='outer', axis=0).reset_index(drop=True) # add dup last row to act as snapshot
                        return_dict[ticker_time] = df_return_me
                        rebuild_confirmation[ticker_time] = "rebuild"
                else:
                    return_dict[ticker_time] = df

            elif "5minute" == timeframe.lower():
                if timedelta_minutes > 6:
                    if len(dfn[1]) == 0:
                        df_latest = dfn[0][ticker_time]
                        df['timetag'] = df['timestamp_est'].apply(lambda x: tag_current_day(x))
                        df_replace = df[df['timetag']!= 'tag'].copy()
                        del df_replace['timetag']
                        df_return = pd.concat([df_replace, df_latest], join='outer', axis=0).reset_index(drop=True)
                        df_return_me = pd.concat([df_return, df_return.tail(1)], join='outer', axis=0).reset_index(drop=True) # add dup last row to act as snapshot
                        return_dict[ticker_time] = df_return_me
                        rebuild_confirmation[ticker_time] = "rebuild"
                else:
                    return_dict[ticker_time] = df
            
            elif "30minute" == timeframe.lower():
                if timedelta_minutes > 31:
                    if len(dfn[1]) == 0:
                        df_latest = dfn[0][ticker_time]

                        df['timetag'] = df['timestamp_est'].apply(lambda x: tag_current_day(x))
                        df_replace = df[df['timetag']!= 'tag'].copy()
                        del df_replace['timetag']
                        df_return = pd.concat([df_replace, df_latest], join='outer', axis=0).reset_index(drop=True)
                        df_return_me = pd.concat([df_return, df_return.tail(1)], join='outer', axis=0).reset_index(drop=True) # add dup last row to act as snapshot
                        return_dict[ticker_time] = df_return_me
                        rebuild_confirmation[ticker_time] = "rebuild"
                else:
                    return_dict[ticker_time] = df

            elif "1hour" == timeframe.lower():
                if timedelta_minutes > 61:
                    if len(dfn[1]) == 0:
                        df_latest = dfn[0][ticker_time]
                        df['timetag'] = df['timestamp_est'].apply(lambda x: tag_current_day(x))
                        df_replace = df[df['timetag']!= 'tag'].copy()
                        del df_replace['timetag']
                        df_return = pd.concat([df_replace, df_latest], join='outer', axis=0).reset_index(drop=True)
                        df_return_me = pd.concat([df_return, df_return.tail(1)], join='outer', axis=0).reset_index(drop=True) # add dup last row to act as snapshot
                        return_dict[ticker_time] = df_return_me
                        rebuild_confirmation[ticker_time] = "rebuild"
                else:
                    return_dict[ticker_time] = df

            elif "2hour" == timeframe.lower():
                if timedelta_minutes > 121:
                    if len(dfn[1]) == 0:
                        df_latest = dfn[0][ticker_time]
                        df['timetag'] = df['timestamp_est'].apply(lambda x: tag_current_day(x))
                        df_replace = df[df['timetag']!= 'tag'].copy()
                        del df_replace['timetag']
                        df_return = pd.concat([df_replace, df_latest], join='outer', axis=0).reset_index(drop=True)
                        df_return_me = pd.concat([df_return, df_return.tail(1)], join='outer', axis=0).reset_index(drop=True) # add dup last row to act as snapshot
                        return_dict[ticker_time] = df_return_me
                        rebuild_confirmation[ticker_time] = "rebuild"
                else:
                    return_dict[ticker_time] = df

            else:
                return_dict[ticker_time] = df
        
        # add back in snapshot init
        return {"ticker_time": return_dict, "rebuild_confirmation": rebuild_confirmation}


    def pollen_hunt(df_tickers_data, MACD):
        # Check to see if any charts need to be Recreate as times lapsed
        df_tickers_data_rebuilt = ReInitiate_Charts_Past_Their_Time(df_tickers_data)
        if len(df_tickers_data_rebuilt['rebuild_confirmation'].keys()) > 0:
            print(df_tickers_data_rebuilt['rebuild_confirmation'].keys())
            print(datetime.datetime.now(est).strftime("%H:%M-%S"))
        
        # re-add snapshot
        # ipdb.set_trace()
        df_tickers_data_rebuilt = Return_Snapshots_Rebuild(df_tickers_data=df_tickers_data_rebuilt['ticker_time'])
        
        main_rebuild_dict = {} ##> only override current dict if memory becomes issues!
        chart_rebuild_dict = {}
        for ticker_time, bars_data in df_tickers_data_rebuilt.items():
            chart_rebuild_dict[ticker_time] = bars_data
            df_data_new = return_getbars_WithIndicators(bars_data=bars_data, MACD=MACD)
            if df_data_new[0] == True:
                main_rebuild_dict[ticker_time] = df_data_new[1]
            else:
                print("error", ticker_time)

        return {'pollencharts_nectar': main_rebuild_dict, 'pollencharts': chart_rebuild_dict}


    """ Initiate your Charts with Indicators """
    def initiate_ttframe_charts(QUEEN, queens_chess_piece, master_tickers, star_times, MACD_settings):
        s_mainbeetime = datetime.datetime.now(est)
        res = Return_Init_ChartData(ticker_list=master_tickers, chart_times=star_times)
        errors = res['errors']
        if errors:
            msg = ("Return_Init_ChartData Failed", "--", errors)
            print(msg)
            logging.critical(msg)
            sys.exit()
        df_tickers_data_init = res['init_charts']
        
        """ add snapshot to initial chartdata -1 """
        df_tickers_data = Return_Snapshots_Rebuild(df_tickers_data=df_tickers_data_init, init=True)
        
        """ give it all to the QUEEN put directkly in function """
        pollen = pollen_hunt(df_tickers_data=df_tickers_data, MACD=MACD_settings)
        QUEEN[queens_chess_piece]['pollencharts'] = pollen['pollencharts']
        QUEEN[queens_chess_piece]['pollencharts_nectar'] = pollen['pollencharts_nectar']

        """# mark final times and return values"""
        e_mainbeetime = datetime.datetime.now(est)
        msg = {queens_chess_piece:'initiate ttframe charts',  'block_timeit': str((e_mainbeetime - s_mainbeetime)), 'datetime': datetime.datetime.now(est).strftime('%Y-%m-%d_%H:%M:%S_%p')}
        logging.info(msg)
        print(msg)    
        return QUEEN


    def chunk(it, size):
        it = iter(it)
        return iter(lambda: tuple(islice(it, size)), ())


    def ticker_star_hunter_bee(WORKERBEE_queens, QUEENBEE, queens_chess_piece, speed_gauges):
        s = datetime.datetime.now(est)
        
        QUEEN = WORKERBEE_queens[queens_chess_piece] # castle [spy, qqq], knight,
        # QUEEN = qcp_QUEEN
        PB_Story_Pickle = os.path.join(db_root, f'{queens_chess_piece}{".pkl"}')
        # MACD_12_26_9 = QUEENBEE['queen_controls']['MACD_fast_slow_smooth']
        # master_tickers = QUEENBEE['workerbees'][queens_chess_piece]['tickers']
        MACD_settings = QUEENBEE['workerbees'][queens_chess_piece]['MACD_fast_slow_smooth']
        # star_times = QUEENBEE['workerbees'][queens_chess_piece]['stars']

        # change the script to pull for each ticker, inifinite pawns pw1: [10] ... write out the pollenstory to the local db pickle file
        # aysnc needs to happen here as well: change from async full chess piece to group of tickers and async the pollen_hunt & pollen_story
        # multiprocess the workbees # SPY_1Minute_1Day

        # main 
        pollen = pollen_hunt(df_tickers_data=QUEEN[queens_chess_piece]['pollencharts'], MACD=MACD_settings)
        QUEEN[queens_chess_piece]['pollencharts'] = pollen['pollencharts']
        QUEEN[queens_chess_piece]['pollencharts_nectar'] = pollen['pollencharts_nectar']
        
        pollens_honey = pollen_story(pollen_nectar=QUEEN[queens_chess_piece]['pollencharts_nectar'], WORKER_QUEEN=QUEENBEE)
        ANGEL_bee = pollens_honey['conscience']['ANGEL_bee']
        knights_sight_word = pollens_honey['conscience']['KNIGHTSWORD']
        STORY_bee = pollens_honey['conscience']['STORY_bee']
        betty_bee = pollens_honey['betty_bee']
        PickleData(pickle_file=os.path.join(db_root, 'betty_bee.pkl'), data_to_store=betty_bee)

        # for each star append last macd state
        for ticker_time_frame, i in STORY_bee.items():
            speed_gauges[ticker_time_frame]['macd_gauge'].append(i['story']['macd_state'])
            speed_gauges[ticker_time_frame]['price_gauge'].append(i['story']['last_close_price'])
            STORY_bee[ticker_time_frame]['story']['macd_gauge'] = speed_gauges[ticker_time_frame]['macd_gauge']
            STORY_bee[ticker_time_frame]['story']['price_gauge'] = speed_gauges[ticker_time_frame]['price_gauge']

        
        SPEEDY_bee = speed_gauges

        # add all charts
        QUEEN[queens_chess_piece]['pollenstory'] = pollens_honey['pollen_story']

        # populate conscience
        QUEEN[queens_chess_piece]['conscience']['ANGEL_bee'] = ANGEL_bee
        QUEEN[queens_chess_piece]['conscience']['KNIGHTSWORD'] = knights_sight_word
        QUEEN[queens_chess_piece]['conscience']['STORY_bee'] = STORY_bee
        QUEEN[queens_chess_piece]['conscience']['SPEEDY_bee'] = SPEEDY_bee

        
        PickleData(pickle_file=PB_Story_Pickle, data_to_store=QUEEN)

        return True


    def qcp_QUEENWorker__pollenstory(qcp_s, QUEENBEE, WORKERBEE_queens, speed_gauges):
        try:
            s = datetime.datetime.now(est)
            async def get_changelog(session, qcp):
                async with session:
                    try:
                        ticker_star_hunter_bee(WORKERBEE_queens=WORKERBEE_queens, QUEENBEE=QUEENBEE, queens_chess_piece=qcp, speed_gauges=speed_gauges)
                        return {qcp: ''} # return Charts Data based on Queen's Query Params, (stars())
                    except Exception as e:
                        print(e, qcp)
                        logging.error((str(qcp), str(e)))
                        return {qcp: e}
                        
            async def main(qcp_s):

                async with aiohttp.ClientSession() as session:
                    return_list = []
                    tasks = []
                    for qcp in qcp_s: # castle: [spy], bishop: [goog], knight: [META] ..... pawn1: [xmy, skx], pawn2: [....]
                        # print(qcp)
                        tasks.append(asyncio.ensure_future(get_changelog(session, qcp)))
                    original_pokemon = await asyncio.gather(*tasks)
                    for pokemon in original_pokemon:
                        return_list.append(pokemon)
                    return return_list

            x = asyncio.run(main(qcp_s))
            e = datetime.datetime.now(est)
            print(f'All Workers Refreshed {qcp_s} --- {(e - s)} seconds ---')
            return x
        except Exception as e:
            print("qtf", e, print_line_of_error())


    # def read_QUEEN(queen_db, qcp_s=['castle', 'bishop', 'knight']):
    #     QUEENBEE = ReadPickleData(queen_db)
    #     queens_master_tickers = []
    #     queens_chess_pieces = [] 
    #     for qcp, qcp_vars in QUEENBEE['workerbees'].items():
    #         for ticker in qcp_vars['tickers']:
    #             if qcp in qcp_s:
    #             # if qcp in ['knight']:
    #                 queens_master_tickers.append(ticker)
    #                 queens_chess_pieces.append(qcp)
    #     queens_chess_pieces = list(set(queens_chess_pieces))

    #     return {'QUEENBEE': QUEENBEE, 'queens_chess_pieces': queens_chess_pieces, 'queens_master_tickers':queens_master_tickers}
    
    
    def init_QueenWorkersBees(QUEENBEE, queens_chess_pieces):

        speed_gauges = {}

        WORKERBEE_queens = {i: init_QUEENWORKER(i) for i in queens_chess_pieces}
        for qcp_worker in WORKERBEE_queens.keys():
            MACD_settings = QUEENBEE['workerbees'][qcp_worker]['MACD_fast_slow_smooth']
            master_tickers = QUEENBEE['workerbees'][qcp_worker]['tickers']
            star_times = QUEENBEE['workerbees'][qcp_worker]['stars']
            WORKERBEE_queens[qcp_worker] = initiate_ttframe_charts(QUEEN=WORKERBEE_queens[qcp_worker], queens_chess_piece=qcp_worker, master_tickers=master_tickers, star_times=star_times, MACD_settings=MACD_settings)
            speed_gauges.update({f'{tic}{"_"}{star_}': {'macd_gauge': deque([], 89), 'price_gauge': deque([], 89)} for tic in master_tickers for star_ in star_times.keys()})
        
        return {'WORKERBEE_queens': WORKERBEE_queens, 'speed_gauges': speed_gauges}

    
    print(
    """
    We all shall prosper through the depths of our connected hearts,
    Not all will share my world,
    So I put forth my best mind of virtue and goodness, 
    Always Bee Better
    """
    )


    # init_pollen = init_pollen_dbs(db_root=db_root, prod=prod, queens_chess_piece=queens_chess_piece)
    # PB_QUEEN_Pickle = init_pollen['PB_QUEEN_Pickle']
    # ipdb.set_trace()
    # if os.path.exists(PB_QUEEN_Pickle) == False:
    #     print("WorkerBee Needs a Queen")
    #     sys.exit()

    # Pollen QUEEN
    
    if prod:
        queen_db = os.path.join(db_root, 'queen.pkl')
        # QUEENBEE = ReadPickleData(pickle_file=os.path.join(db_root, 'queen.pkl'))
    else:
        queen_db = os.path.join(db_root, 'queen_sandbox.pkl')
        # QUEENBEE = ReadPickleData(pickle_file=os.path.join(db_root, 'queen_sandbox.pkl'))


    ticker_universe = return_Ticker_Universe()
    main_index_dict = ticker_universe['main_index_dict']
    index_ticker_db = ticker_universe['index_ticker_db']
    main_symbols_full_list = ticker_universe['main_symbols_full_list']
    not_avail_in_alpaca = ticker_universe['not_avail_in_alpaca']

    
    def queens_court__WorkerBees():
        try:
            pq = read_QUEEN(queen_db=queen_db) # castle, bishop
            QUEENBEE = pq['QUEENBEE']
            queens_chess_pieces = pq['queens_chess_pieces']
            queens_master_tickers = pq['queens_master_tickers']
            # for every ticker async init return inital chart data 
            # res = Return_Init_ChartData(ticker_list=master_tickers, chart_times=star_times)
            # for every qcp (chess peiece) 
            # 1. async pollen_hunt # pulling api close data create the initial setting
            # 2. async pollen story 
            # 3. async write

            queen_workers = init_QueenWorkersBees(QUEENBEE=QUEENBEE, queens_chess_pieces=queens_chess_pieces)
            WORKERBEE_queens = queen_workers['WORKERBEE_queens']
            speed_gauges = queen_workers['speed_gauges']
            
            while True:
                pq = read_QUEEN(queen_db=queen_db)
                QUEENBEE = pq['QUEENBEE']
                latest__queens_chess_pieces = pq['queens_chess_pieces']
                latest__queens_master_tickers = pq['queens_master_tickers']
                if latest__queens_master_tickers != queens_master_tickers:
                    print("Revised Ticker List ReInitiate")
                    queen_workers = init_QueenWorkersBees(QUEENBEE=QUEENBEE, queens_chess_pieces=latest__queens_chess_pieces)
                    WORKERBEE_queens = queen_workers['WORKERBEE_queens']
                    speed_gauges = queen_workers['speed_gauges']
                
                qcp_QUEENWorker__pollenstory(qcp_s=WORKERBEE_queens.keys(), QUEENBEE=QUEENBEE, WORKERBEE_queens=WORKERBEE_queens, speed_gauges=speed_gauges)

                if close_worker():
                    break

        except Exception as errbuz:
            print(errbuz)
            erline = print_line_of_error()
            log_msg = {'type': 'ProgramCrash', 'lineerror': erline}
            print(log_msg)
            logging.critical(log_msg)
            ipdb.set_trace()


    # if queens_chess_piece == 'castle':
    print(f'Queens Court, {queens_chess_piece} I beseech you')
    queens_court__WorkerBees()
    # elif queens_chess_piece == 'indexes':
    #     print("pending")
if __name__ == '__main__':
    queen_workerbees(prod=True)

#### >>>>>>>>>>>>>>>>>>> END <<<<<<<<<<<<<<<<<<###
