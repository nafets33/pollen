# QueenBee Workers
import argparse
import asyncio
import logging
import os
import sys
import time
from collections import deque
from datetime import datetime
from itertools import islice
import streamlit as st
import aiohttp
import pandas as pd
import pytz
from datetime import datetime
import threading
import ipdb
import requests

from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import os
import threading

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from chess_piece.king import (
    PickleData,
    hive_master_root,
    workerbee_dbs_backtesting_root,
    workerbee_dbs_backtesting_root__STORY_bee,
    workerbee_dbs_root,
    workerbee_dbs_root__STORY_bee,
    return_active_orders,
    main_index_tickers,
    master_swarm_QUEENBEE,
    return_crypto_bars,
    return_crypto_snapshots
    
)
from chess_piece.queen_hive import (
    stars,
    init_logging,
    init_qcp_workerbees,
    pollen_story,
    print_line_of_error,
    return_alpaca_api_keys,
    return_macd,
    return_RSI,
    return_sma_slope,
    return_VWAP,
    return_market_hours,
    init_swarm_dbs,
    ReadPickleData,
    return_Ticker_Universe,
    send_email,
    init_queenbee
    
)

from chess_piece.pollen_db import PollenDatabase

os.environ["no_proxy"] = "*"

est = pytz.timezone("US/Eastern")
crypto_currency_symbols = ['BTC/USD', 'ETH/USD']

CRYPTO_URL = "https://data.alpaca.markets/v1beta3/crypto/us"
CRYPTO_HEADER = {"accept": "application/json"}

upsert_to_main_server = os.getenv("upsert_to_main_server")
pg_migration = os.getenv('pg_migration')
# # WORKEBEE WAS NOT AS EFFIIENT TO KEEP??? check on this
# def ttf__save(table_name, task_results):
#     """
#     Save data to the PostgreSQL database using ThreadPoolExecutor for concurrency.
    
#     :param table_name: Name of the database table.
#     :param task_results: List of (key, data) tuples to be saved.
#     """
#     batch_size = 50  # Adjustable batch size for efficient inserts
#     batches = [task_results[i:i + batch_size] for i in range(0, len(task_results), batch_size)]

#     def process_batch(batch):
#         data_dict = {key: data for key, data in batch}
#         PollenDatabase.upsert_multiple(table_name, data_dict)

#     with ThreadPoolExecutor(max_workers=20) as executor:
#         for batch in batches:
#             executor.submit(process_batch, batch)

pollenstory_tickers = ['SPY', 'QQQ', 'GOOG', 'AAPL', 'TSLA', 'META', 'MSFT', 'NVDA', 'AMZN', 'ADBE'] + crypto_currency_symbols

def write_pollenstory_storybee(pollens_honey, MACD_settings, backtesting=False, backtesting_star=None, pg_migration=False, upsert_to_main_server=upsert_to_main_server):
    s = datetime.now(est)
    table_name = "pollen_store" if not backtesting else "pollen_store_backtesting"

    async def main_func(session, ticker_time_frame, pickle_file, key, data, allow_pg_migration, task_results):
        async with session:
            try:
                ticker, tt, tg = ticker_time_frame.split("_")
                if 'GOLD' == ticker:
                    print("YEEEES")
                if backtesting:
                    allow_pg_migration = False
                if allow_pg_migration:
                    PollenDatabase.upsert_data(table_name, key, data, console=False, main_server=upsert_to_main_server)
                    task = (key, data)
                    task_results.append(task)
                else:
                    PickleData(pickle_file, data, console=False)
                return {"status": "success", "ticker_time_frame": ticker_time_frame}
            except Exception as e:
                print("ps_error", e, ticker_time_frame)
                return {"status": "error", "error": e}

    async def main(symbols_pollenstory_dbs, symbols_STORY_bee_root, pollens_honey, macd_part_fname, allow_pg_migration, task_results):
        async with aiohttp.ClientSession() as session:
            return_list = []
            tasks = []

            for ticker_time_frame in pollens_honey["pollen_story"]:
                key = f"POLLEN_STORY_{ticker_time_frame}{macd_part_fname}"
                ticker, ttime, tframe = ticker_time_frame.split("_")
                if ticker not in pollenstory_tickers:
                    continue
                # print("Saving Pollen Story ", ticker)
                pickle_file = os.path.join(symbols_pollenstory_dbs, f"{ticker_time_frame}{macd_part_fname}.pkl")
                data = {"pollen_story": pollens_honey["pollen_story"][ticker_time_frame]}
                tasks.append(asyncio.ensure_future(main_func(session, ticker_time_frame, pickle_file, key, data, allow_pg_migration, task_results)))

            for ticker_time_frame in pollens_honey["conscience"]["STORY_bee"]:
                key = f"STORY_BEE_{ticker_time_frame}{macd_part_fname}"
                ticker, ttime, tframe = ticker_time_frame.split("_")
                pickle_file = os.path.join(symbols_STORY_bee_root, f"{ticker_time_frame}{macd_part_fname}.pkl")
                data = {"STORY_bee": pollens_honey["conscience"]["STORY_bee"][ticker_time_frame]}
                tasks.append(asyncio.ensure_future(main_func(session, ticker_time_frame, pickle_file, key, data, allow_pg_migration, task_results)))

            results = await asyncio.gather(*tasks)
            return results

    symbols_pollenstory_dbs = workerbee_dbs_backtesting_root() if backtesting else workerbee_dbs_root()
    symbols_STORY_bee_root = workerbee_dbs_backtesting_root__STORY_bee() if backtesting else workerbee_dbs_root__STORY_bee()
    macd_part_fname = "__{}-{}-{}".format(MACD_settings["fast"], MACD_settings["slow"], MACD_settings["smooth"]) if backtesting else ""
    
    task_results = []

    save_all_pollenstory = asyncio.run(
        main(
            symbols_pollenstory_dbs,
            symbols_STORY_bee_root,
            pollens_honey,
            macd_part_fname,
            pg_migration,
            task_results,
        )
    )

    # if pg_migration:
    #     ttf__save(table_name, task_results)

    return True



def update_speed_gauges(pollens_honey, speed_gauges=None):
    # for each star append last macd state
    if not speed_gauges:
        pollens_honey["conscience"]["STORY_bee"][ticker_time_frame]["story"]["macd_gauge"] = []
        pollens_honey["conscience"]["STORY_bee"][ticker_time_frame]["story"]["price_gauge"] = [] 
        return pollens_honey
    
    for ticker_time_frame, i in pollens_honey["conscience"].get("STORY_bee").items():
        speed_gauges[ticker_time_frame]["macd_gauge"].append(i["story"]["macd_state"])
        speed_gauges[ticker_time_frame]["price_gauge"].append(i["story"]["last_close_price"])
        pollens_honey["conscience"]["STORY_bee"][ticker_time_frame]["story"]["macd_gauge"] = speed_gauges[ticker_time_frame]["macd_gauge"]
        pollens_honey["conscience"]["STORY_bee"][ticker_time_frame]["story"]["price_gauge"] = speed_gauges[ticker_time_frame]["price_gauge"]
    
    return pollens_honey


def read_QUEEN(prod, qcp_s=["castle", "bishop", "knight"], pg_migration=False):
    if pg_migration:
        table_name = 'db' if prod else 'db_sandbox'
        QUEENBEE = PollenDatabase.retrieve_data(table_name, key='QUEEN')
    else:
        QUEENBEE = ReadPickleData(master_swarm_QUEENBEE(prod=prod))

    queens_master_tickers = []
    queens_chess_pieces = []
    for qcp, qcp_vars in QUEENBEE["workerbees"].items():
        if qcp in qcp_s:
            for ticker in qcp_vars["tickers"]:
                queens_master_tickers.append(ticker)
                queens_chess_pieces.append(qcp)
    queens_chess_pieces = list(set(queens_chess_pieces))
    queens_master_tickers = list(set(queens_master_tickers))

    return {
        "QUEENBEE": QUEENBEE,
        "queens_chess_pieces": queens_chess_pieces,
        "queens_master_tickers": queens_master_tickers,
    }


### BARS
def return_bars(
    api,
    symbol,
    timeframe,
    ndays,
    trading_days_df,
    sdate_input=False,
    edate_input=False,
    crypto=False,
    exchange=False,
):
    try:
        s = datetime.now(est)
        timeframe = timeframe.replace("ute", '') if 'Minute' in timeframe else timeframe
        error_dict = {}
        # Fetch bars for prior ndays and then add on today
        # s_fetch = datetime.now()
        if edate_input != False:
            end_date = edate_input
        else:
            end_date = datetime.now(est).strftime("%Y-%m-%d")

        if sdate_input != False:
            start_date = sdate_input
        else:
            if ndays == 0:
                start_date = datetime.now(est).strftime("%Y-%m-%d")
            else:
                start_date = (trading_days_df.query("date < @current_day").tail(ndays).head(1).date)

        if exchange:
            symbol_data = api.get_crypto_bars(
                symbol,
                timeframe=timeframe,
                start=start_date,
                end=end_date,
                exchanges=exchange,
            ).df
        else:
            symbol_data = api.get_bars(
                symbol,
                timeframe=timeframe,
                start=start_date,
                end=end_date,
                adjustment="all",
            ).df
        if len(symbol_data) == 0:
            print("No Data Returned for ", timeframe)
            error_dict[symbol] = {"msg": "no data returned", "time": time}
            return [False, error_dict]

        # set index to EST time
        symbol_data["timestamp_est"] = symbol_data.index
        symbol_data["timestamp_est"] = symbol_data["timestamp_est"].apply(lambda x: x.astimezone(est))
        symbol_data = symbol_data.set_index("timestamp_est", drop=False)

        symbol_data["symbol"] = symbol
        symbol_data["timeframe"] = timeframe
        symbol_data["bars"] = "bars"

        # Make two dataframes one with just market hour data the other with after hour data
        if "day" in timeframe:
            market_hours_data = symbol_data  # keeping as copy since main func will want to return markethours
            after_hours_data = None
        else:
            market_hours_data = symbol_data.between_time("9:30", "16:00")
            market_hours_data = market_hours_data.reset_index(drop=True)
            after_hours_data = symbol_data.between_time("16:00", "9:30")
            after_hours_data = after_hours_data.reset_index(drop=True)

        symbol_data = symbol_data.reset_index(drop=True)

        e = datetime.now(est)
        # print("?????", symbol_data.iloc[-1]["timestamp_est"])
        # (str((e - s)) + ": " + datetime.now().strftime('%Y-%m-%d %H:%M'))

        return {
            "resp": True,
            "df": symbol_data,
            "market_hours_data": market_hours_data,
            "after_hours_data": after_hours_data,
        }
    # handle error
    except Exception as e:
       print_line_of_error(e)


def return_bars_list(api, ticker_list, chart_times, trading_days_df, crypto=False, exchange=False, s_date=False, e_date=False):
    try:
        # ticker_list = ['SPY', 'QQQ']
        # chart_times = {
        #     "1Minute_1Day": 1, "5Minute_5Day": 5, "30Minute_1Month": 18,
        #     "1Hour_3Month": 48, "2Hour_6Month": 72,
        #     "1Day_1Year": 250
        #     }
        current_date = datetime.now(est).strftime("%Y-%m-%d")
        trading_days_df_ = trading_days_df[trading_days_df["date"] < current_date]  # less then current date
        s = datetime.now(est)
        return_dict = {}
        error_dict = {}

        for charttime, ndays in chart_times.items():
            try:
                timeframe = charttime.split("_")[0]  # '1Minute_1Day'
                timeframe = timeframe.replace("ute", '') if 'Minute' in timeframe else timeframe
                if s_date and e_date:
                    start_date = s_date
                    end_date = e_date
                else:
                    start_date = trading_days_df_.tail(ndays).head(1).date
                    start_date = start_date.iloc[-1].strftime("%Y-%m-%d")
                    end_date = datetime.now(est).strftime("%Y-%m-%d")

                if exchange:
                    symbol_data = api.get_crypto_bars(
                        ticker_list,
                        timeframe=timeframe,
                        start=start_date,
                        end=end_date,
                        exchanges=exchange,
                    ).df
                else:
                        symbol_data = api.get_bars(
                            ticker_list,
                            timeframe=timeframe,
                            start=start_date,
                            end=end_date,
                            adjustment="all",
                        ).df
                    
                if len(symbol_data) == 0:
                    print(f"{ticker_list} {charttime} NO Bars")
                    error_dict[str(ticker_list)] = {"msg": "no data returned", "time": datetime.now()}
                    return {}
                # set index to EST time
                symbol_data["timestamp_est"] = symbol_data.index
                symbol_data["timestamp_est"] = symbol_data["timestamp_est"].apply(lambda x: x.astimezone(est))
                symbol_data["timeframe"] = timeframe
                symbol_data["bars"] = "bars_list"
                symbol_data = symbol_data.reset_index(drop=True)
                # print("?????", symbol_data.iloc[-1]["timestamp_est"])

                return_dict[charttime] = symbol_data  
            except Exception as e:
                print("QH_getbars", print_line_of_error(), e)
                print(ticker_list)
                return {}
        
        e = datetime.now(est)
        return {"resp": True, "return": return_dict, 'error_dict': error_dict}

    except Exception as e:
        print_line_of_error("beeee worker error")
        logging.error(str(e))



def queen_workerbees(
    qcp_s,  # =["castle", "bishop", "knight"],
    QUEENBEE=None,
    prod=True,
    check_with_queen_frequency=360,
    queens_chess_piece="bees_manager",
    backtesting=False,
    macd=None,
    reset_only=False,
    run_all_pawns=False,
    backtesting_star=False,
    streamit=False,
    pg_migration=True,
    upsert_to_main_server=upsert_to_main_server,
):

    if backtesting:
        assert macd is not None
        reset_only = True
    else:
        assert macd is None

    # script arguments
    if prod:
        print("Production")
    else:
        print("Sandbox")
    
    print(", ".join(f"{key}={value}" for key, value in locals().items()))

    # if windows:
    #     asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy()) # needed to work on Windows
    if queens_chess_piece.lower() not in ["workerbee", "bees_manager"]:
        print("wrong chess move")
        sys.exit()

    pd.options.mode.chained_assignment = None
    est = pytz.timezone("US/Eastern")

    main_root = hive_master_root()  # os.getcwd()
    db_root = os.path.join(main_root, "db")
    init_logging(queens_chess_piece=queens_chess_piece, db_root=db_root, prod=prod)

    # Macd Settings
    # MACD_12_26_9 = {'fast': 12, 'slow': 26, 'smooth': 9}
    def init_QUEENWORKER(queens_chess_piece):

        QUEEN = {  # To Go To The Queens Mind
            # Worker Bees
            queens_chess_piece: {
                "conscience": {"STORY_bee": {}, "KNIGHTSWORD": {}, "ANGEL_bee": {}},
                "pollenstory": {},  # latest story of dataframes castle and bishop
                "pollencharts": {},  # latest chart rebuild
                "pollencharts_nectar": {},  # latest chart rebuild with indicators
                "pollenstory_info": {},  # Misc Info,
                "client": {},
                "heartbeat": {"cycle_time": deque([], 89)},
                "last_modified": datetime.now(est),
                "triggerBee_frequency": {},
            }
        }

        return QUEEN

    """ Keys """
    api = return_alpaca_api_keys(prod=prod)["api"]

    """# Dates """
    current_date = datetime.now(est).strftime("%Y-%m-%d")
    trading_days = api.get_calendar()
    trading_days_df = pd.DataFrame([day._raw for day in trading_days])

    trading_days_df["date"] = pd.to_datetime(trading_days_df["date"])

    if backtesting or reset_only:
        pass
    else:
        mkhrs = return_market_hours(trading_days=trading_days)
        if mkhrs != 'open':
            print("Bee to ZzzzZZzzzZzzz")
            # sys.exit()

    current_day = datetime.now(est).day
    current_month = datetime.now(est).month
    current_year = datetime.now(est).year

    # misc
    exclude_conditions = [
        "B",
        "W",
        "4",
        "7",
        "9",
        "C",
        "G",
        "H",
        "I",
        "M",
        "N",
        "P",
        "Q",
        "R",
        "T",
        "V",
        "Z",
    ]  # 'U'

    """# Main Arguments """

    def close_worker(WORKERBEE_queens, crypto):
        s = datetime.now(est)
        date = datetime.now(est)
        if crypto:
            turn_off_time = date.replace(hour=22, minute=0, second=0)
            if s > turn_off_time:
                print("CRYPTO: Great Job! See you Tomorrow")
                return True
        else:
            date = date.replace(hour=16, minute=0, second=1)
            if s >= date:
                # logging.info("Happy Bee Day End")
                print("Great Job! See you Tomorrow")
                print("save all workers and their results")
                return True
        
        return False

    def return_getbars_WithIndicators(bars_data, MACD):
        # time = '1Minute' #TEST
        # symbol = 'SPY' #TEST
        # ndays = 1
        # bars_data = return_bars(symbol, time, ndays, trading_days_df=trading_days_df)

        try:
            # s = datetime.datetime.now(est) #TEST
            bars_data["vwap_original"] = bars_data["vwap"]

            bars_data = return_VWAP(bars_data)
            # df_vwap = vwap(bars_data)

            bars_data = return_RSI(df=bars_data, length=14)

            bars_data = return_macd(
                df_main=bars_data,
                fast=MACD["fast"],
                slow=MACD["slow"],
                smooth=MACD["smooth"],
            )
            # df_vwap_rsi_macd_smaslope = return_sma_slope(
            #     df=df_vwap_rsi_macd,
            #     time_measure_list=[3, 6, 23, 33],
            #     y_list=["close", "macd", "hist"],
            # )
            # e = datetime.datetime.now(est)
            # print(str((e - s)) + ": " + datetime.datetime.now().strftime("%A, %d. %B %Y %I:%M%p"))
            # 0:00:00.198920: Monday, 21. March 2022 03:02PM 2 days 1 Minute
            return [True, bars_data]
        except Exception as e:
            print_line_of_error("return_getbars_WithIndicators ERROR")
            return [False]

    def Return_Init_ChartData(ticker_list, chart_times):  # Iniaite Ticker Charts with Indicator Data
        # ticker_list = ['SPY', 'QQQ']
        # chart_times = {
        #     "1Minute_1Day": 0, "5Minute_5Day": 5, "30Minute_1Month": 18,
        #     "1Hour_3Month": 48, "2Hour_6Month": 72,
        #     "1Day_1Year": 250}
        try:
            crypto = True if '/' in ticker_list[0] else False

            error_dict = {}
            s = datetime.now(est)
            dfs_index_tickers = {}
            if crypto:
                # print("returning crypto bars")
                bars = return_crypto_bars(
                    ticker_list=ticker_list,
                    chart_times=chart_times,
                    trading_days_df=trading_days_df,
                )
                # print("len of crypto bars", bars)
            else:
                bars = return_bars_list(
                    api=api,
                    ticker_list=ticker_list,
                    chart_times=chart_times,
                    trading_days_df=trading_days_df,
                )
            # print("bars data\n", bars['return']['1Minute_1Day'])
            if len(bars) == 0:
                # print(f"{ticker_list} NO Bars") # error called out in func
                return {}
            # if bars['return']: # rebuild and split back to ticker_time with market hours only
            #     # bars_dfs = bars['return']
            for timeframe, df in bars["return"].items():
                time_frame = timeframe.split("_")[0]  # '1day_1year'
                if "1day" in time_frame.lower() or crypto:
                    for ticker in ticker_list:
                        df_return = df[df["symbol"] == ticker].copy()
                        dfs_index_tickers[f'{ticker}{"_"}{timeframe}'] = df_return
                else:
                    df = df.set_index("timestamp_est")
                    market_hours_data = df.between_time("9:30", "16:00")
                    market_hours_data = market_hours_data.reset_index()
                    # market_hours_data = df
                    for ticker in ticker_list:
                        df_return = market_hours_data[market_hours_data["symbol"] == ticker].copy()
                        dfs_index_tickers[f'{ticker}{"_"}{timeframe}'] = df_return

            e = datetime.now(est)

            return {"init_charts": dfs_index_tickers, "errors": error_dict}
        except Exception as e:
            print("eeeeeror", e, print_line_of_error())

    def Return_Snapshots_Rebuild(df_tickers_data, init=False):  # from snapshots & consider using day.min.chart to rebuild other timeframes
        def ticker_Snapshots(ticker_list, float_cols, int_cols):
            return_dict = {}
            try:
                for ticker in ticker_list:
                    if '/' in ticker:
                        dl = {
                        "close": snapshots[ticker]['dailyBar']['c'],
                        "high": snapshots[ticker]['dailyBar']['h'],
                        "low": snapshots[ticker]['dailyBar']['l'],
                        "timestamp_est": pd.to_datetime(snapshots[ticker]['dailyBar']['t']).tz_convert('UTC'),
                        "open": snapshots[ticker]['dailyBar']['o'],
                        "volume": snapshots[ticker]['dailyBar']['v'],
                        "trade_count": snapshots[ticker]['dailyBar']['n'],
                        "vwap": snapshots[ticker]['dailyBar']['vw'],
                        "current_ask": snapshots[ticker]['latestQuote']['ap'],
                        "current_bid": snapshots[ticker]['latestQuote']['bp'],
                        }
                        df_daily = pd.Series(dl).to_frame().T  # reshape dataframe
                        for i in float_cols:
                            df_daily[i] = df_daily[i].astype(float)
                        for i in int_cols:
                            df_daily[i] = df_daily[i].astype(int)

                        return_dict[ticker + "_day"] = df_daily

                        d = {
                            "close": snapshots[ticker]['latestTrade']['p'],
                            "high": snapshots[ticker]['latestTrade']['p'],
                            "low": snapshots[ticker]['latestTrade']['p'],
                            "timestamp_est": pd.to_datetime(snapshots[ticker]['latestTrade']['t']).tz_convert('UTC'),
                            "open": snapshots[ticker]['latestTrade']['p'],
                            "volume": snapshots[ticker]['minuteBar']['v'],
                            "trade_count": snapshots[ticker]['minuteBar']['n'],
                            "vwap": snapshots[ticker]['minuteBar']['vw'],
                            # "current_price": snapshots[ticker].latest_trade.price,
                            "current_ask": snapshots[ticker]['latestQuote']['ap'],
                            "current_bid": snapshots[ticker]['latestQuote']['bp'],
                        }
                        df_minute = pd.Series(d).to_frame().T
                        for i in float_cols:
                            df_minute[i] = df_minute[i].astype(float)
                        for i in int_cols:
                            df_minute[i] = df_minute[i].astype(int)

                        return_dict[ticker + "_minute"] = df_minute
                    else:
                        dl = {
                            "close": snapshots[ticker].daily_bar.close,
                            "high": snapshots[ticker].daily_bar.high,
                            "low": snapshots[ticker].daily_bar.low,
                            "timestamp_est": snapshots[ticker].daily_bar.timestamp,
                            "open": snapshots[ticker].daily_bar.open,
                            "volume": snapshots[ticker].daily_bar.volume,
                            "trade_count": snapshots[ticker].daily_bar.trade_count,
                            "vwap": snapshots[ticker].daily_bar.vwap,
                            "current_ask": snapshots[ticker].latest_quote.ask_price,
                            "current_bid": snapshots[ticker].latest_quote.bid_price,
                        }
                        df_daily = pd.Series(dl).to_frame().T  # reshape dataframe
                        for i in float_cols:
                            df_daily[i] = df_daily[i].astype(float)
                        for i in int_cols:
                            df_daily[i] = df_daily[i].astype(int)

                        return_dict[ticker + "_day"] = df_daily

                        d = {
                            "close": snapshots[ticker].latest_trade.price,
                            "high": snapshots[ticker].latest_trade.price,
                            "low": snapshots[ticker].latest_trade.price,
                            "timestamp_est": snapshots[ticker].latest_trade.timestamp,
                            "open": snapshots[ticker].latest_trade.price,
                            "volume": snapshots[ticker].minute_bar.volume,
                            "trade_count": snapshots[ticker].minute_bar.trade_count,
                            "vwap": snapshots[ticker].minute_bar.vwap,
                            # "current_price": snapshots[ticker].latest_trade.price,
                            "current_ask": snapshots[ticker].latest_quote.ask_price,
                            "current_bid": snapshots[ticker].latest_quote.bid_price,
                        }
                        df_minute = pd.Series(d).to_frame().T
                        for i in float_cols:
                            df_minute[i] = df_minute[i].astype(float)
                        for i in int_cols:
                            df_minute[i] = df_minute[i].astype(int)

                        return_dict[ticker + "_minute"] = df_minute
            except Exception as e:
                print("main error")
                print(e)
                print(ticker)
                print_line_of_error()

            return return_dict

        try:
            crypto_snapshots = False
            stock_snapshots = False
            ticker_list = list([set(j.split("_")[0] for j in df_tickers_data.keys())][0])  # > get list of tickers
            crypto_tickers = []
            stock_tickers = []
            for ticker in ticker_list:
                if '/' in ticker:
                    crypto_tickers.append(ticker)
                else:
                    stock_tickers.append(ticker)
            
            if crypto_tickers:
                print("crypto", crypto_tickers)
                crypto_snapshots =  return_crypto_snapshots(crypto_tickers)
            if stock_tickers:
                stock_snapshots = api.get_snapshots(stock_tickers)
            
            snapshots = {}

            if crypto_snapshots:
                for key, value in crypto_snapshots.items():
                    snapshots[key] = value
            if stock_snapshots:
                for key, value in stock_snapshots.items():
                    snapshots[key] = value

            for ticker in snapshots.keys():  # replace snapshot if in exclude_conditions
                if '/' in ticker:
                    continue
                else:
                    c = 0
                    while True:
                        conditions = snapshots[ticker].latest_trade.conditions
                        invalid = [c for c in conditions if c in exclude_conditions]
                        if len(invalid) == 0 or c > 10:
                            break
                        else:
                            print(f"{ticker} invalid trade-condition pull snapshot")
                            snapshot = api.get_snapshot(
                                ticker
                            )  # return_last_quote from snapshot
                            snapshots[ticker] = snapshot
                            c += 1

            float_cols = [
                "close",
                "high",
                "open",
                "low",
                "vwap",
                "current_ask",
                "current_bid",
            ]
            int_cols = ["volume", "trade_count"]
            main_return_dict = {}

            snapshot_ticker_data = ticker_Snapshots(ticker_list, float_cols, int_cols)

            def ttf_snapshot(ticker_time, df):
                symbol_snapshots = {
                    k: v
                    for (k, v) in snapshot_ticker_data.items()
                    if k.split("_")[0] == ticker_time.split("_")[0]
                }
                symbol, timeframe, days = ticker_time.split("_")
                if "day" in timeframe.lower():
                    df_day_snapshot = symbol_snapshots[f'{symbol}{"_day"}']  # stapshot df
                    df_day_snapshot["symbol"] = symbol
                    df = df.head(-1)  # drop last row which has current day / added minute
                    df_rebuild = pd.concat([df, df_day_snapshot], join="outer", axis=0).reset_index(drop=True)  # concat minute
                    main_return_dict[ticker_time] = df_rebuild
                else:
                    df_snapshot = symbol_snapshots[f'{symbol}{"_minute"}']  # stapshot df
                    df_snapshot["symbol"] = symbol
                    # df_snapshot['timestamp_est'] = df_snapshot["timestamp_est"].apply(lambda x: x.astimezone(est))
                    if init:
                        df_rebuild = pd.concat([df, df_snapshot], join="outer", axis=0).reset_index(drop=True)  # concat minute
                        main_return_dict[ticker_time] = df_rebuild
                    else:
                        df = df.head(-1)  # drop last row which has current day
                        df_rebuild = pd.concat([df, df_snapshot], join="outer", axis=0).reset_index(drop=True)  # concat minute
                        main_return_dict[ticker_time] = df_rebuild

            s = datetime.now(est)

            async def main_func(session, ticker_time, df):
                async with session:
                    try:
                        ttf_snapshot(ticker_time=ticker_time, df=df)
                        return {"status": "success", "ttf": ticker_time}
                    except Exception as e:
                        print("erhere: ", e, ticker_time)
                        return {"status": "error", "ttf": ticker_time, "error": e}

            async def main(df_tickers_data):

                async with aiohttp.ClientSession() as session:
                    return_list = []
                    tasks = []
                    for ticker_time, df in df_tickers_data.items():
                        tasks.append(
                            asyncio.ensure_future(main_func(session, ticker_time, df))
                        )
                    original_pokemon = await asyncio.gather(*tasks)
                    for pokemon in original_pokemon:
                        return_list.append(pokemon)
                    return return_list

            return_list = asyncio.run(main(df_tickers_data))
            e = datetime.now(est)
            # print(f"async snapshots {df_tickers_data.keys()} --- {(e - s)} seconds ---")

            return main_return_dict  # df_tickers_data

        except Exception as e:
            print("Error mate", e)
            print(queens_chess_piece)

    def ReInitiate_Charts_Past_Their_Time(df_tickers_data):  # re-initiate for i timeframe
        # IMPROVEMENT: use Return_bars_list for Return_Bars_LatestDayRebuild
        return_dict = {}
        rebuild_confirmation = {}

        def Return_Bars_LatestDayRebuild(ticker_time):  # Iniaite Ticker Charts with Indicator Data
            # IMPROVEMENT: use Return_bars_list for Return Bars_LatestDayRebuild
            # ticker_time = "SPY_1Minute_1Day"
            print("REBUILDING BARS for ", ticker_time)
            ticker, timeframe, days = ticker_time.split("_")
            error_dict = {}
            s = datetime.now(est)
            dfs_index_tickers = {}
            try:
                # return market hours data from bars
                bars_data = return_bars(
                    api=api,
                    symbol=ticker,
                    timeframe=timeframe,
                    ndays=0,
                    trading_days_df=trading_days_df,
                )  # return [True, symbol_data, market_hours_data, after_hours_data]
                df_bars_data = bars_data["market_hours_data"]  # mkhrs if in minutes
                dfs_index_tickers[ticker_time] = df_bars_data
            except Exception as e:
                print("err__", ticker_time, e)

            e = datetime.now(est)
            msg = {
                "function": "Return_Bars_Latest Day Rebuild",
                "func_timeit": str((e - s)),
                "datetime": datetime.now(est).strftime("%Y-%m-%d_%H:%M:%S_%p"),
            }
            # print(msg)
            # dfs_index_tickers['SPY_5Minute']
            return [dfs_index_tickers, error_dict, msg]

        def tag_current_day(timestamp):
            if (
                timestamp.day == current_day
                and timestamp.month == current_month
                and timestamp.year == current_year
            ):
                return "tag"
            else:
                return "0"

        def rebuild_ticker_time_frame(ticker_time_frame, df):
            ticker, timeframe, days = ticker_time_frame.split("_")
            last = df["timestamp_est"].iloc[-2]
            now = datetime.now(est)
            timedelta_minutes = (now - last).seconds / 60
            now_day = now.day
            last_day = last.day
            if now_day != last_day:
                print(f"NOT Rebuilding {ticker_time_frame} as day has changed")
                return_dict[ticker_time_frame] = df
                return return_dict, rebuild_confirmation

            dfn = Return_Bars_LatestDayRebuild(ticker_time_frame)

            def apply_swap_out_row(df):
                if len(dfn[1]) == 0:
                    df_latest = dfn[0][ticker_time_frame]
                    df["timetag"] = df["timestamp_est"].apply(lambda x: tag_current_day(x))
                    df_replace = df[df["timetag"] != "tag"].copy()
                    del df_replace["timetag"]
                    df_return = pd.concat([df_replace, df_latest], join="outer", axis=0).reset_index(drop=True)
                    df_return_me = pd.concat([df_return, df_return.tail(1)], join="outer", axis=0).reset_index(drop=True)  # add dup last row to act as snapshot
                    return_dict[ticker_time_frame] = df_return_me
                    rebuild_confirmation[ticker_time_frame] = "rebuild"
                
                return df
    
            if "1minute" == timeframe.lower():
                if timedelta_minutes > 2:
                    apply_swap_out_row(df)
                else:
                    return_dict[ticker_time_frame] = df
            elif "5minute" == timeframe.lower():
                if timedelta_minutes > 6:
                    apply_swap_out_row(df)
                else:
                    return_dict[ticker_time_frame] = df
            elif "30minute" == timeframe.lower():
                if timedelta_minutes > 31:
                    apply_swap_out_row(df)
                else:
                    return_dict[ticker_time_frame] = df
            elif "1hour" == timeframe.lower():
                if timedelta_minutes > 61:
                    apply_swap_out_row(df)
                else:
                    return_dict[ticker_time_frame] = df
            elif "2hour" == timeframe.lower():
                if timedelta_minutes > 121:
                    apply_swap_out_row(df)
                else:
                    return_dict[ticker_time_frame] = df
            else:
                return_dict[ticker_time_frame] = df

            return return_dict, rebuild_confirmation

        s = datetime.now(est)

        async def get_changelog(session, ticker_time, df):
            async with session:
                try:
                    return_dict = rebuild_ticker_time_frame(
                        ticker_time_frame=ticker_time, df=df
                    )
                    return {
                        "return_dict": return_dict
                    }  # return Charts Data based on Queen's Query Params, (stars())
                except Exception as e:
                    print("erhere_2: ", e, ticker_time)

        async def main(df_tickers_data):

            async with aiohttp.ClientSession() as session:
                return_list = []
                tasks = []
                for ticker_time, df in df_tickers_data.items():
                    # return_dict = rebuild_ticker_time_frame(ticker_time_frame=ticker_time, df=df)
                    tasks.append(
                        asyncio.ensure_future(get_changelog(session, ticker_time, df))
                    )
                original_pokemon = await asyncio.gather(*tasks)
                for pokemon in original_pokemon:
                    return_list.append(pokemon)
                return return_list

        return_list = asyncio.run(main(df_tickers_data))
        e = datetime.now(est)
        # print(f"async ReInitiate Past Times {df_tickers_data.keys()} --- {(e - s)} seconds ---")

        # add back in snapshot init
        return {
            "df_tickers_data": return_dict,  # df_tickers_data
            "rebuild_confirmation": rebuild_confirmation,
        }

    def pollen_hunt(df_tickers_data, MACD={"fast": 13,"slow": 28,"smooth": 9}, MACD_WAVES=None, reset_only=reset_only, backtesting=backtesting):
        try:
        # Check to see if any charts need to be Recreate as times lapsed
            if reset_only == False:
                print("POLLEN HUNT")
                res = ReInitiate_Charts_Past_Their_Time(df_tickers_data)
                df_tickers_data = res.get("df_tickers_data")
                df_tickers_data = Return_Snapshots_Rebuild(df_tickers_data=df_tickers_data)

            main_rebuild_dict = {}  ##> only override current dict if memory becomes issues!
            chart_rebuild_dict = {}
            ttf_MACD = {ttf: MACD for ttf in df_tickers_data.keys()}
            # print(f"Running, {MACD}, for {len(df_tickers_data)}")
            
            if backtesting:
                pass
            else:
                if isinstance(MACD_WAVES, pd.DataFrame):
                    MACD_WAVES_ttfs = MACD_WAVES.index.tolist()
                    for ttf, macd_var in ttf_MACD.items():
                        if ttf in MACD_WAVES_ttfs:
                            story_AI_MACD = MACD_WAVES.loc[ttf].get("avg_ratio")
                            m_fast, m_slow, m_smooth = story_AI_MACD.split("_")
                            macd_var = {
                                "fast": int(m_fast),
                                "slow": int(m_slow),
                                "smooth": int(m_smooth),
                            }
                            ttf_MACD[ttf] = macd_var

            def add_techincals_indicator(ticker_time, df, MACD):
                chart_rebuild_dict[ticker_time] = df
                df_data_new = return_getbars_WithIndicators(bars_data=df, MACD=MACD)
                if df_data_new[0] == True:
                    main_rebuild_dict[ticker_time] = df_data_new[1]
                else:
                    print("error", ticker_time)

            s = datetime.now(est)

            async def main_func(session, ticker_time, df, MACD):
                async with session:
                    try:
                        return_dict = add_techincals_indicator(ticker_time, df, MACD)
                        return {
                            "return_dict": return_dict
                        }  # return Charts Data based on Queen's Query Params, (stars())
                    except Exception as e:
                        print("erhere_3", e, ticker_time)

            async def main(df_tickers_data):

                async with aiohttp.ClientSession() as session:
                    return_list = []
                    tasks = []
                    for ticker_time, df in df_tickers_data.items():
                        if len(df) == 0:
                            print("errrrr", ticker_time)
                        #     ipdb.set_trace()
                        #     continue
                        MACD = ttf_MACD.get(ticker_time)  # get MAC from KING
                        tasks.append(
                            asyncio.ensure_future(main_func(session, ticker_time, df, MACD))
                        )
                    original_pokemon = await asyncio.gather(*tasks)
                    for pokemon in original_pokemon:
                        return_list.append(pokemon)
                    return return_list

            return_list = asyncio.run(main(df_tickers_data))
            e = datetime.now(est)
            # print(f"async Techincals Join {df_tickers_data.keys()} --- {(e - s)} seconds ---")

            # for ticker_time, df in df_tickers_data.items():
            #     add_techincals_indicator(ticker_time, df, MACD)

            return {
                "pollencharts_nectar": main_rebuild_dict,
                "pollencharts": chart_rebuild_dict,
            }
        except Exception as e:
            print_line_of_error("del me")

    """ Initiate your Charts with Indicators """

    def initiate_ttframe_charts(master_tickers, star_times, MACD_settings, MACD_WAVES, speed_gauges=None, reset_only=reset_only, pg_migration=pg_migration):
        try:
            s_mainbeetime = datetime.now(est)
            # WORKERBEE if backetesting no need to recall chart data
            df_all = {}
            
            for ticker in master_tickers:
                res = Return_Init_ChartData(ticker_list=[ticker], chart_times=star_times)
                df_tickers_data = res["init_charts"]
                df_all.update(df_tickers_data)

            df_tickers_data = df_all

            """ add snapshot to initial chartdata -1 """
            if reset_only == False:
                df_tickers_data = Return_Snapshots_Rebuild(df_tickers_data=df_tickers_data, init=True)

            """ give it all to the QUEEN put directkly in function """
            pollen = pollen_hunt(df_tickers_data=df_tickers_data, MACD=MACD_settings, MACD_WAVES=MACD_WAVES)
            if reset_only: # run pollen story and save then quit
                pollens_honey = pollen_story(pollen_nectar=pollen.get("pollencharts_nectar"))
                pollens_honey = update_speed_gauges(pollens_honey, speed_gauges)
                # s = datetime.now()
                write_pollenstory_storybee(pollens_honey, MACD_settings, backtesting, backtesting_star, pg_migration=pg_migration, upsert_to_main_server=upsert_to_main_server)
                

            """# mark final times and return values"""
            e_mainbeetime = datetime.now(est)
                # print((datetime.now() - s).total_seconds())

            return pollen
        except Exception as e:
            print_line_of_error(f"BEES IINIT FAILED {e} ")
            raise e

    def chunk(it, size):
        it = iter(it)
        return iter(lambda: tuple(islice(it, size)), ())

    def ticker_star_hunter_bee(WORKERBEE, QUEENBEE, queens_chess_piece, speed_gauges, MACD_WAVES, macd=macd):
        # QUEEN = WORKERBEE_queens[queens_chess_piece]  # castle [spy, qqq], knight,
        start_time = datetime.now(est)

        if backtesting:
            MACD_settings = macd
        else:
            MACD_settings = QUEENBEE["workerbees"][queens_chess_piece]["MACD_fast_slow_smooth"]

        # main
        s = datetime.now()
        pollen = pollen_hunt(
            df_tickers_data=WORKERBEE[queens_chess_piece]["pollencharts"],
            MACD=MACD_settings,
            MACD_WAVES=MACD_WAVES,
        )
        hunt_time =  (datetime.now() - s).total_seconds()
        # print(pollen["pollencharts"]['BTC/USD_1Minute_1Day'].tail(1)[['symbol', 'timestamp_est', 'close']])
        WORKERBEE[queens_chess_piece]["pollencharts"] = pollen["pollencharts"]
        WORKERBEE[queens_chess_piece]["pollencharts_nectar"] = pollen["pollencharts_nectar"]  # bars and techicnals
        s = datetime.now()
        pollens_honey = pollen_story(pollen_nectar=pollen.get("pollencharts_nectar"))
        story_time = (datetime.now() - s).total_seconds()
        # print(pollen["pollencharts"]['BTC/USD_1Minute_1Day'].tail(1)[['symbol', 'timestamp_est', 'close']])
        # print(pollens_honey["conscience"]["STORY_bee"]['BTC/USD_1Minute_1Day']['story'])

        betty_bee = pollens_honey["betty_bee"]

        pollens_honey = update_speed_gauges(pollens_honey, speed_gauges)
        s = datetime.now()
        write_pollenstory_storybee(pollens_honey, MACD_settings, backtesting, backtesting_star, pg_migration=pg_migration, upsert_to_main_server=upsert_to_main_server)
        write_time = (datetime.now() - s).total_seconds()
        
        print(f'{queens_chess_piece}: hunt {hunt_time} : story {story_time} : write {write_time}')
        
        qcp_hunt = (datetime.now(est) - start_time).total_seconds()

        betty_bee[f"{queens_chess_piece}_cycle_time.pkl"] = qcp_hunt
        # WORKERBEE add deque([], 89)
        if f"{queens_chess_piece}_avg_cycle_time.pkl" not in betty_bee.keys():
           betty_bee[f"{queens_chess_piece}_avg_cycle_time"] = deque([], 1500)
        else:
            betty_bee[f"{queens_chess_piece}_avg_cycle_time"].append(qcp_hunt)

        # PickleData(
        #     pickle_file=os.path.join(db_root, f"{queens_chess_piece}_betty_bee.pkl"),
        #     data_to_store=betty_bee,
        # )

        return True

    def init_QueenWorkersBees(QUEENBEE, queens_chess_pieces, MACD_WAVES, queens_master_tickers, reset_only=reset_only, backtesting=backtesting):
        try:
            speed_gauges = {}

            WORKERBEE_queens = {i: init_QUEENWORKER(i) for i in queens_chess_pieces}

            for qcp_worker in WORKERBEE_queens.keys():
            # for qcp_worker in WORKERBEE_queens.keys():
                if backtesting:
                    MACD_settings = macd
                else:
                    MACD_settings = QUEENBEE["workerbees"][qcp_worker]["MACD_fast_slow_smooth"]
                
                qcp = QUEENBEE["workerbees"].get(qcp_worker)
                if not qcp:
                    print("QCP", qcp_worker)
                    continue
                master_tickers = qcp.get('tickers')
                master_tickers = [i for i in master_tickers if i in queens_master_tickers]
                if not master_tickers:
                    print("not tics available in master")
                    return None
                # master_tickers = ['SPY', 'BTC/USD', 'ETH/USD', 'LTC/USD']

                star_times = stars() # QUEENBEE["workerbees"][qcp_worker]["stars"]
                if backtesting_star:
                    QUEENBEE["workerbees"][qcp_worker]["stars"] = {backtesting_star: 1}  # "1Minute_1Day"
                    # star_times = QUEENBEE["workerbees"][qcp_worker]["stars"]
                
                speed_gauges.update(
                    {
                        f'{tic}{"_"}{star_}': {
                            # "speen_gauge": deque([], 89), # maybe to track each qcp
                            "macd_gauge": deque([], 89),
                            "price_gauge": deque([], 89),
                        }
                        for tic in master_tickers
                        for star_ in star_times.keys()
                    }
                )

                WORKERBEE_QUEEN = WORKERBEE_queens[qcp_worker]
                pollen = initiate_ttframe_charts(
                    master_tickers=master_tickers,
                    star_times=star_times,
                    MACD_settings=MACD_settings,
                    MACD_WAVES=MACD_WAVES,
                    speed_gauges=speed_gauges,
                    reset_only=reset_only,
                )
                WORKERBEE_QUEEN[qcp_worker]["pollencharts"] = pollen["pollencharts"]
                WORKERBEE_QUEEN[qcp_worker]["pollencharts_nectar"] = pollen["pollencharts_nectar"]
                WORKERBEE_queens[qcp_worker] = WORKERBEE_QUEEN
                

            return {"WORKERBEE_queens": WORKERBEE_queens, "speed_gauges": speed_gauges}
        except Exception as e:
            print_line_of_error(e)
    
    
    def queens_court__WorkerBees(QUEENBEE, prod, qcp_s, run_all_pawns=False, streamit=False, reset_only=reset_only):

        if type(qcp_s) == str:
            qcp_s = [qcp_s]
        queens_chess_pieces = qcp_s # pq.get("queens_chess_pieces")

        def confirm_tickers_available(alpaca_symbols_dict, symbols):
            queens_master_tickers = []
            errors = []
            alpaca_symbols_dict['BTC/USD'] = {}
            alpaca_symbols_dict['ETH/USD'] = {}
            for i in symbols:
                if i in alpaca_symbols_dict.keys():
                    queens_master_tickers.append(i)
                else:
                    msg=(i, "Ticker NOT in Alpaca Ticker DB")
                    errors.append(msg)
            if errors:
                msg = str(errors)
                # send_email(subject="Tickers Not Longer Active", body=msg)
                print("MISSING TICKER NOT IN ALPACA", msg)
                if streamit:
                    st.error(f'tickers NOT in Alpaca TICKER DB {errors}')
            
            return queens_master_tickers


        alpaca_symbols_dict = return_Ticker_Universe().get('alpaca_symbols_dict')

        MACD_WAVES = pd.read_csv(os.path.join(hive_master_root(), "backtesting/macd_backtest_analysis.txt"))
        MACD_WAVES = MACD_WAVES.set_index("ttf")
        
        # swarm_db = init_swarm_dbs(prod)
        
        if QUEENBEE is not None:
            list_of_lists = [i.get('tickers') for qcp, i in QUEENBEE['workerbees'].items() if qcp in queens_chess_pieces]
            symbols = [item for sublist in list_of_lists for item in sublist]
            queens_master_tickers = confirm_tickers_available(alpaca_symbols_dict, symbols)
        else:
            print("READING MASTER QUEEN")
            if pg_migration:
                table_name = 'db' if prod else 'db_sandbox'
                QUEENBEE = PollenDatabase.retrieve_data(table_name, key='QUEEN')
            else:
                QUEENBEE = ReadPickleData(master_swarm_QUEENBEE(prod=prod))
            
            list_of_lists = [i.get('tickers') for qcp, i in QUEENBEE['workerbees'].items() if qcp in queens_chess_pieces]
            symbols = [item for sublist in list_of_lists for item in sublist]
            queens_master_tickers = confirm_tickers_available(alpaca_symbols_dict, symbols)

        if not queens_master_tickers:
            print(queens_chess_pieces, " No Tickers to Find EXITING", queens_master_tickers)
            sys.exit()
        
        def handle_qcp_pawns(QUEENBEE, tickers, queens_chess_pieces=queens_chess_pieces, queens_master_tickers=queens_master_tickers):
            CHUNK_SIZE = 20

            if len(tickers) < CHUNK_SIZE:
                print("< 20 catch call pawn")
                pawn = 'catch_all_bucket'
                pawn_qcp = init_qcp_workerbees(
                    init_macd_vars={"fast": 12, "slow": 26, "smooth": 9},
                    ticker_list=tickers,
                    theme=None,
                    model=None,
                    piece_name=pawn,
                    buying_power=None,
                    borrow_power=None,
                    picture="knight_png",
                )
                QUEENBEE["workerbees"].update({pawn: pawn_qcp})
                queens_chess_pieces.append(pawn)
                queens_master_tickers += tickers

            else:
                print("> 20 catch call pawns")
                for i in range(0, len(tickers), CHUNK_SIZE):
                    chunk = tickers[i:i + CHUNK_SIZE]
                    pawn = f'{str(chunk)}'
                    pawn_qcp = init_qcp_workerbees(
                        init_macd_vars={"fast": 12, "slow": 26, "smooth": 9},
                        ticker_list=chunk,
                        theme=None,
                        model=None,
                        piece_name=pawn,
                        buying_power=None,
                        borrow_power=None,
                        picture="knight_png",
                    )
                    QUEENBEE["workerbees"].update({pawn: pawn_qcp})
                    queens_chess_pieces.append(pawn)
                    queens_master_tickers += chunk

            return QUEENBEE, queens_chess_pieces, queens_master_tickers


        # def check for new symbols
        if 'castle' in queens_chess_pieces:
            list_of_lists = [i.get('tickers') for qcp, i in QUEENBEE['workerbees'].items()]
            all_symbols = [item for sublist in list_of_lists for item in sublist]
            # ipdb.set_trace()
            df_tickers = init_queenbee(client_user='stefanstapinski@gmail.com', prod=True, revrec=True, pg_migration=True)['revrec'].get('df_ticker')
            tickers_to_add = []
            for ticker in df_tickers.index:
                if ticker not in all_symbols and df_tickers.loc[ticker, 'ticker_buying_power'] > 0:
                    # print(ticker, "NOT IN QUEENBEE adding to Castle")
                    tickers_to_add.append(ticker)

            new_symbols = [i for i in tickers_to_add if i not in all_symbols] # and i not in all_values
            for i in new_symbols:
                if i not in alpaca_symbols_dict.keys():
                    print(i, "NOT IN ALPACA DB")
                    new_symbols.remove(i)

            if len(new_symbols)> 0 and reset_only == False:
                print("NEW SYMBOLS NEEDED FROM OPEN ORDERS", new_symbols)
                QUEENBEE, queens_chess_pieces, queens_master_tickers =  handle_qcp_pawns(QUEENBEE, new_symbols)
        
        if run_all_pawns:
            p_num = 0
            QUEENBEE, queens_chess_pieces, queens_master_tickers =  handle_qcp_pawns(QUEENBEE, new_symbols)
            p_num += 1


        msg=f" Master Tickers {len(queens_master_tickers)} {queens_master_tickers}"
        print(msg)
        crypto = True if [i for i in queens_master_tickers if i in crypto_currency_symbols] else False
        print("CRYPTO:", crypto)

        try:

            if streamit:
                st.write(msg)

            # def chunk_queenbee(queens_master_tickers):
            
            if len(queens_master_tickers) > 89:
                print("chunking queens")
                from tqdm import tqdm
                for ticker in tqdm(queens_master_tickers):
                    queen_workers = init_QueenWorkersBees(
                        QUEENBEE=QUEENBEE,
                        queens_chess_pieces=queens_chess_pieces,
                        MACD_WAVES=MACD_WAVES,
                        queens_master_tickers=[ticker],
                        reset_only=reset_only,
                    )
            else:
                queen_workers = init_QueenWorkersBees(
                    QUEENBEE=QUEENBEE,
                    queens_chess_pieces=queens_chess_pieces,
                    MACD_WAVES=MACD_WAVES,
                    queens_master_tickers=queens_master_tickers,
                    reset_only=reset_only,
                )
            if reset_only:
                msg=("EXITING RESET ONLY")
                print(msg)
                if streamit:
                    st.write(msg)
                return True
            
            WORKERBEE_queens = queen_workers["WORKERBEE_queens"]
            speed_gauges = queen_workers["speed_gauges"]
            now_time = datetime.now(est)
            time.sleep(1)
            last_queen_call = {"last_call": datetime.now(est)}

            chart_times_refresh = {
                "1Minute_1Day": 3,
                "5Minute_5Day": 5*60,
                "30Minute_1Month": 30*60,
                "1Hour_3Month": 60*60,
                "2Hour_6Month": 120*60,
                "1Day_1Year": 360*60,
            }

            print("Here We go Mario")
            while True:
                # if check_with_queen_frequency
                if reset_only == False and run_all_pawns == False: # I.E. not Current Day
                    now_time = datetime.now(est)
                    if (now_time - last_queen_call.get("last_call")).total_seconds() > check_with_queen_frequency:
                        print("Check Queen for New Tickers")
                        pq = read_QUEEN(prod, qcp_s=qcp_s, pg_migration=pg_migration)
                        QUEENBEE = pq["QUEENBEE"]
                        last_queen_call = {"last_call": now_time}
                        latest__queens_chess_pieces = pq["queens_chess_pieces"]
                        latest__queens_master_tickers = pq["queens_master_tickers"]
                        if latest__queens_master_tickers != queens_master_tickers:
                            print("Revised Ticker List ReInitiate")
                            queen_workers = init_QueenWorkersBees(
                                QUEENBEE=QUEENBEE,
                                queens_chess_pieces=latest__queens_chess_pieces,
                                MACD_WAVES=MACD_WAVES,
                                queens_master_tickers=queens_master_tickers,
                            )
                            WORKERBEE_queens = queen_workers["WORKERBEE_queens"]
                            speed_gauges = queen_workers["speed_gauges"]

                try:                    
                    for qcp in WORKERBEE_queens.keys():
                        s = datetime.now(est)
                        WORKERBEE = WORKERBEE_queens[qcp]
                        # check to see if last call
                        last_modified = WORKERBEE[qcp].get('last_modified')
                        if isinstance(last_modified, datetime):
                            pass
                        else:
                            WORKERBEE[qcp]['last_modified'] = now_time
                        refresh_star = QUEENBEE['workerbees'][qcp].get('refresh_star')
                        if refresh_star:
                            star_frequency = chart_times_refresh[refresh_star]
                        else:
                            star_frequency = 1
                        
                        if (now_time - last_modified).total_seconds() < star_frequency:
                            # print(qcp, "workbee too fast")
                            continue
                        WORKERBEE[qcp]['last_modified'] = now_time
                        ticker_star_hunter_bee(
                            WORKERBEE=WORKERBEE,
                            QUEENBEE=QUEENBEE,
                            queens_chess_piece=qcp,
                            speed_gauges=speed_gauges,
                            MACD_WAVES=MACD_WAVES,
                        )
                        e = datetime.now(est)
                        print(f"Worker Refreshed {qcp} : {(e - s)} seconds : {QUEENBEE['workerbees'][qcp].get('tickers')}")
                        # else:
                        #     print("star Frequency not Met")

                except Exception as e:
                    print("qtf", e, print_line_of_error())

                if backtesting or reset_only:
                    break
                if close_worker(WORKERBEE_queens, crypto=False): #WORKERBEE HC UNTIL CRYPTO WORKING
                    break

        except Exception as errbuz:
            print(errbuz)
            erline = print_line_of_error()
            log_msg = {"type": "ProgramCrash", "lineerror": erline}
            print(log_msg)
            logging.critical(log_msg)

    # if queens_chess_piece == 'castle':
    print(f"Queens Court, {queens_chess_piece} I beseech you")
    queens_court = queens_court__WorkerBees(QUEENBEE, prod, qcp_s, run_all_pawns, streamit)

    print("EXIT BEE ")
    return True



if __name__ == "__main__":

    def createParser_workerbees():
        parser = argparse.ArgumentParser()
        parser.add_argument("-prod", default=True)
        parser.add_argument("-qcp_s", default="castle")
        parser.add_argument("-reset_only", default=False)
        parser.add_argument("-pg_migration", default=True)
        # parser.add_argument("-queens_chess_piece", default="bees_manager")
        # parser.add_argument("-backtesting", default=True)
        # parser.add_argument("-macd", default=None)

        return parser

    # script arguments
    parser = createParser_workerbees()
    namespace = parser.parse_args()
    qcp_s = namespace.qcp_s  # 'castle', 'knight' 'queen'
    reset_only = namespace.reset_only  # 'castle', 'knight' 'queen'
    pg_migration = True if str(namespace.pg_migration).lower() == "true" else False
    prod = True if str(namespace.prod).lower() == "true" else False


    # if not reset_only:
    #     while True:
    #         seconds_to_market_open = (
    #             datetime.now(est).replace(hour=9, minute=30, second=0) - datetime.now(est)
    #         ).total_seconds()
    #         if seconds_to_market_open > 0:
    #             print(seconds_to_market_open, " ZZzzzZZ")
    #             time.sleep(3)
    #         else:
    #             break
            

    print("printing qcp_s:\n", qcp_s)
    queen_workerbees(qcp_s=qcp_s, prod=prod, reset_only=reset_only, pg_migration=pg_migration)

#### >>>>>>>>>>>>>>>>>>> END <<<<<<<<<<<<<<<<<<###