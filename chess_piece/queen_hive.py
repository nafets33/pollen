import argparse
import logging
import os
import asyncio
import aiohttp
import smtplib
import ssl
import sys
import time
from collections import defaultdict, deque
import sqlite3
from itertools import islice
from datetime import datetime, timedelta
from email.message import EmailMessage
from typing import Callable
import ipdb
import numpy as np
import pandas as pd
import pytz
import requests
import streamlit as st
import alpaca_trade_api as tradeapi
from alpaca_trade_api.rest import URL
from alpaca_trade_api.rest_async import AsyncRest
from dotenv import load_dotenv
from scipy import stats
from stocksymbol import StockSymbol
from tqdm import tqdm
from logging.handlers import RotatingFileHandler

from chess_piece.app_hive import init_client_user_secrets
from chess_piece.king import return_db_root, PickleData, ReadPickleData, hive_master_root, local__filepaths_misc, kingdom__global_vars

queens_chess_piece = os.path.basename(__file__)
king_G = kingdom__global_vars()
MISC = local__filepaths_misc()
mainpage_bee_png = MISC['mainpage_bee_png']

est = pytz.timezone("America/New_York")
utc = pytz.timezone("UTC")


prod = True

main_root = hive_master_root()  # os.getcwd()
load_dotenv(os.path.join(main_root, ".env"))
db_root = os.path.join(main_root, "db")

"""# Dates """
current_day = datetime.now(est).day
current_month = datetime.now(est).month
current_year = datetime.now(est).year


def init_logging(queens_chess_piece, db_root, prod, loglevel='info', max_log_size=10 * 1024 * 1024, backup_count=5):
    log_dir = os.path.join(db_root, "logs")
    log_dir_logs = os.path.join(log_dir, "logs")

    if not os.path.exists(log_dir):
        os.mkdir(log_dir)
    if not os.path.exists(log_dir_logs):
        os.mkdir(log_dir_logs)

    if prod:
        log_name = f'{"log_"}{queens_chess_piece}{".log"}'
    else:
        log_name = f'{"log_"}{queens_chess_piece}{"_sandbox_"}{".log"}'

    log_file = os.path.join(log_dir, log_name)

    # Set the logging level based on the provided loglevel parameter
    if loglevel.lower() == 'info':
        level = logging.INFO
    elif loglevel.lower() == 'warning':
        level = logging.WARNING
    else:
        level = logging.INFO  # Default to INFO if an invalid log level is provided

    # Create a logger and set the level
    logger = logging.getLogger()
    logger.setLevel(level)

    # Create a formatter
    formatter = logging.Formatter("%(asctime)s:%(name)s:%(levelname)s: %(message)s", datefmt="%m/%d/%Y %I:%M:%S %p")

    # Create a rotating file handler and set the formatter
    file_handler = RotatingFileHandler(log_file, mode="a", maxBytes=max_log_size, backupCount=backup_count)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Create a stream handler (console) and set the formatter
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    return True


init_logging(queens_chess_piece=queens_chess_piece, db_root=db_root, prod=prod)

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
]  # 'U' afterhours

current_date = datetime.now(est).strftime("%Y-%m-%d")

""" Global VARS"""
crypto_currency_symbols = ["BTCUSD", "ETHUSD", "BTC/USD", "ETH/USD"]
macd_tiers = 8


def return_api_keys(base_url, api_key_id, api_secret, prod=True):
    # api_key_id = os.environ.get('APCA_API_KEY_ID')
    # api_secret = os.environ.get('APCA_API_SECRET_KEY')
    # base_url = "https://api.alpaca.markets"
    # base_url_paper = "https://paper-api.alpaca.markets"
    # feed = "sip"  # change to "sip" if you have a paid account

    if prod == False:
        rest = AsyncRest(key_id=api_key_id, secret_key=api_secret)

        api = tradeapi.REST(
            key_id=api_key_id,
            secret_key=api_secret,
            base_url=URL(base_url),
            api_version="v2",
        )
    else:
        rest = AsyncRest(key_id=api_key_id, secret_key=api_secret)

        api = tradeapi.REST(
            key_id=api_key_id,
            secret_key=api_secret,
            base_url=URL(base_url),
            api_version="v2",
        )
    return {"rest": rest, "api": api}


def test_api_keys(user_secrets):
    APCA_API_KEY_ID_PAPER = user_secrets["APCA_API_KEY_ID_PAPER"]
    APCA_API_SECRET_KEY_PAPER = user_secrets["APCA_API_SECRET_KEY_PAPER"]
    APCA_API_KEY_ID = user_secrets["APCA_API_KEY_ID"]
    APCA_API_SECRET_KEY = user_secrets["APCA_API_SECRET_KEY"]
    try:
        base_url = "https://api.alpaca.markets"
        rest = AsyncRest(key_id=APCA_API_KEY_ID, secret_key=APCA_API_SECRET_KEY)

        api = tradeapi.REST(
            key_id=APCA_API_KEY_ID,
            secret_key=APCA_API_SECRET_KEY,
            base_url=URL(base_url),
            api_version="v2",
        )
        api.get_snapshot("SPY")
        prod = True
        prod_er = False
    except Exception as e:
        prod_er = e
        prod = False

    try:
        base_url = "https://paper-api.alpaca.markets"
        rest = AsyncRest(
            key_id=APCA_API_KEY_ID_PAPER, secret_key=APCA_API_SECRET_KEY_PAPER
        )

        api = tradeapi.REST(
            key_id=APCA_API_KEY_ID_PAPER,
            secret_key=APCA_API_SECRET_KEY_PAPER,
            base_url=URL(base_url),
            api_version="v2",
        )
        api.get_snapshot("SPY")
        sandbox = True
        sb_er = False
    except Exception as e:
        sb_er = e
        sandbox = False
    return {
        "prod": prod,
        "sandbox": sandbox,
        "prod_er": str(prod_er),
        "sb_er": str(sb_er),
    }


def return_alpaca_api_keys(prod):
    # """ Keys """ ### NEEDS TO BE FIXED TO PULL USERS API CREDS UNLESS USER IS PART OF MAIN.FUND.Account
    try:
        if prod:
            keys = return_api_keys(
                base_url="https://api.alpaca.markets",
                api_key_id=os.environ.get("APCA_API_KEY_ID"),
                api_secret=os.environ.get("APCA_API_SECRET_KEY"),
                prod=prod,
            )
            rest = keys["rest"]
            api = keys["api"]
        else:
            # Paper
            keys_paper = return_api_keys(
                base_url="https://paper-api.alpaca.markets",
                api_key_id=os.environ.get("APCA_API_KEY_ID_PAPER"),
                api_secret=os.environ.get("APCA_API_SECRET_KEY_PAPER"),
                prod=False,
            )
            rest = keys_paper["rest"]
            api = keys_paper["api"]

    except Exception as e:
        print("Key Return failure default to HivesKeys")
        print(e)

    return {"rest": rest, "api": api}


def return_alpaca_user_apiKeys(QUEEN_KING, authorized_user, prod):
    def return_client_user__alpaca_api_keys(prod, api_key_id, api_secret):

        # """ Keys """ ### NEEDS TO BE FIXED TO PULL USERS API CREDS UNLESS USER IS PART OF MAIN.FUND.Account
        if prod:
            keys = return_api_keys(
                base_url="https://api.alpaca.markets",
                api_key_id=api_key_id,
                api_secret=api_secret,
                prod=prod,
            )
            rest = keys["rest"]
            api = keys["api"]
        else:
            # Paper
            keys_paper = return_api_keys(
                base_url="https://paper-api.alpaca.markets",
                api_key_id=api_key_id,
                api_secret=api_secret,
                prod=False,
            )
            rest = keys_paper["rest"]
            api = keys_paper["api"]

        return {"rest": rest, "api": api}

    prod_keys_confirmed = QUEEN_KING["users_secrets"]["prod_keys_confirmed"]
    sandbox_keys_confirmed = QUEEN_KING["users_secrets"]["sandbox_keys_confirmed"]
    try:
        if authorized_user:
            if prod:
                if prod_keys_confirmed == False:
                    # st.error("You Need to Add you PROD API KEYS")
                    return False
                else:
                    api_key_id = QUEEN_KING["users_secrets"]["APCA_API_KEY_ID"]
                    api_secret = QUEEN_KING["users_secrets"]["APCA_API_SECRET_KEY"]
                    api = return_client_user__alpaca_api_keys(
                        api_key_id=api_key_id, api_secret=api_secret, prod=prod
                    )["api"]
                    return api
            else:
                if sandbox_keys_confirmed == False:
                    # st.error("You Need to Add you SandboxPAPER API KEYS")
                    return False
                else:
                    api_key_id = QUEEN_KING["users_secrets"]["APCA_API_KEY_ID_PAPER"]
                    api_secret = QUEEN_KING["users_secrets"]["APCA_API_SECRET_KEY_PAPER"]
                    api = return_client_user__alpaca_api_keys(
                        api_key_id=api_key_id, api_secret=api_secret, prod=prod
                    )["api"]
                    return api
        else:
            st.warning("USER NOT YET AUTHORIZED AND SHOWING PREVIEW")
            return return_alpaca_api_keys(prod=False)["api"]
    except Exception as e:
        print_line_of_error()
        return False


def hive_dates(api):
    current_date = datetime.now(est).strftime("%Y-%m-%d")
    trading_days = api.get_calendar()
    trading_days_df = pd.DataFrame([day._raw for day in trading_days])
    trading_days_df["date"] = pd.to_datetime(trading_days_df["date"])

    return {"trading_days": trading_days}


def init_queen(queens_chess_piece):

    QUEEN = {  # The Queens Mind
        "version": 2,
        "init_id": f'{"queen"}{"_"}{return_timestamp_string()}',
        "account_info": {},
        "prod": "",
        "source": "na", # local file path
        "source_account_info": 'init',
        "last_modified": datetime.now(est),
        "command_conscience": {}, ## ?
        "crypto_temp": {"trigbees": {}},
        "queen_orders": pd.DataFrame([create_QueenOrderBee(queen_init=True)]).set_index("client_order_id", drop=False),
        "portfolio": {},
        "heartbeat": {
            'need_order_info': [],
            'long': 0,
            'short': 0,
            'wave_blocktime': {},
            "critical": {},
            "available_tickers": [],
            "active_tickers": [],
            "available_triggerbees": [],
        },
        "queens_messages": {},
        "kings_order_rules": {},
        "queen_controls": return_queen_controls(stars),
        "order_status_info": [],

        "workerbees": {
            "castle": {
                "MACD_fast_slow_smooth": {"fast": 12, "slow": 26, "smooth": 9},
                "tickers": ["SPY"],
                "stars": stars(),
            },
            "bishop": {
                "MACD_fast_slow_smooth": {"fast": 12, "slow": 26, "smooth": 9},
                "tickers": ["GOOG", "AAPL", "TSLA"],
                "stars": stars(),
            },
            "knight": {
                "MACD_fast_slow_smooth": {"fast": 12, "slow": 26, "smooth": 9},
                "tickers": ["AMZN", "OXY", "SOFI"],
                "stars": stars(),
            },
            "castle_coin": {
                "MACD_fast_slow_smooth": {"fast": 12, "slow": 26, "smooth": 9},
                "tickers": ["BTCUSD", "ETHUSD"],
                "stars": stars(),
            },
            # "pawns": {
            #     "MACD_fast_slow_smooth": {"fast": 12, "slow": 26, "smooth": 9},
            #     "tickers": main_symbols_full_list[:100],
            #     "stars": stars(),
            # },
        },
        "chess_board": {},
        "revrec": {},
        "errors": {},
        "client_order_ids_qgen": [],
        "app_requests__bucket": [],
        # 'triggerBee_frequency': {}, # hold a star and the running trigger
        "saved_pollenThemes": [],  # bucket of saved star settings to choose from
        "saved_powerRangers": [],  # bucket of saved star settings to choose from
        "subconscious": {"app_info": deque([], 89)},
        "conscience": {"app_info": deque([], 89)},
        "sub_conscience": {"app_info": deque([], 89)},
        # Worker Bees
        queens_chess_piece: {
            "conscience": {"STORY_bee": {}, "KNIGHTSWORD": {}, "ANGEL_bee": {}},
            # 'command_conscience': {}, 'memory': {}, 'orders': []}, # change knightsword
            "pollenstory": {},  # latest story of dataframes castle and bishop
            "pollencharts": {},  # latest chart rebuild
            "pollencharts_nectar": {},  # latest chart rebuild with indicators
            "pollenstory_info": {},  # Misc Info,
            "client": {},
            # 'heartbeat': {},
            "last_modified": datetime.now(est),
        },
    }

    return QUEEN

# WORKERBEE combine init_qcp with any QUEEN even Swarm
def init_qcp(init_macd_vars={"fast": 12, "slow": 26, "smooth": 9}, 
             ticker_list=['SPY'], 
             theme='nuetral', 
             model='MACD', piece_name='king', buying_power=1, borrow_power=0, picture='knight_png', margin_power=0):
    return {
        "picture": picture,
        "piece_name": piece_name,
        "model": model,
        "MACD_fast_slow_smooth": init_macd_vars,
        "tickers": ticker_list,
        "stars": stars(),
        "theme": theme,
        "total_buyng_power_allocation": buying_power,
        "total_borrow_power_allocation": borrow_power,
        "margin_power": margin_power,
    }

def generate_chess_board(init_macd_vars={"fast": 12, "slow": 26, "smooth": 9}, qcp_tickers={'castle': ["SPY"], 'bishop': ["GOOG"], 'knight': ["OXY"], 'castle_coin':["BTCUSD", "ETHUSD"] }, qcp_theme={'castle': "nuetral", 'bishop': "nuetral", 'knight': "nuetral", 'castle_coin':"nuetral" }):
    chess_board = {}
    for qcp, tickers in qcp_tickers.items():
        theme = qcp_theme.get(qcp)
        chess_board[qcp] = init_qcp(init_macd_vars=init_macd_vars, ticker_list=tickers, theme=theme)

    return chess_board

def init_qcp_workerbees(init_macd_vars={"fast": 12, "slow": 26, "smooth": 9}, 
             ticker_list=['SPY'], 
             theme='nuetral', 
             model='MACD', 
             piece_name='king', 
             buying_power=1, 
             borrow_power=0, 
             picture='knight_png', 
             margin_power=0,
             refresh_star='1Minute_1Day'):
    return {
        "picture": picture,
        "piece_name": piece_name,
        "model": model,
        "MACD_fast_slow_smooth": init_macd_vars,
        "tickers": ticker_list,
        "stars": stars(),
        "theme": theme,
        "total_buyng_power_allocation": buying_power,
        "total_borrow_power_allocation": borrow_power,
        "margin_power": margin_power,
        'refresh_star': refresh_star,
    }

def setup_chess_board(QUEEN, qcp_bees_key='workerbees'):
    if qcp_bees_key not in QUEEN.keys():
        QUEEN[qcp_bees_key] = {}
    db = init_swarm_dbs(prod)
    BISHOP = ReadPickleData(db.get('BISHOP'))
    df = BISHOP.get('screen_1')
    for sector in set(df['sector']):
        token = df[df['sector']==sector]
        tickers=token['symbol'].tolist()
        QUEEN[qcp_bees_key][sector] = init_qcp_workerbees(ticker_list=tickers)
    
    return QUEEN


def init_QUEEN_KING():

    app = {
        "version": 3,
        "prod": 'init',
        "api": 'init',
        # 'long': 0,
        # 'short': 0,
        "db__client_user": 'init',
        "pickle_file": 'init',
        "source": "init",
        "theme": "nuetral",
        "queen_tier": "queen_1",
        "king_controls_queen": return_queen_controls(stars),
        "qcp_workerbees": generate_chess_board(),
        "chess_board": generate_chess_board(),
        "revrec": "init",
        "STORY_bee_wave_analysis": 'init',
        "fresh_board_timer" : datetime.now(est),
        "trigger_queen": {
            "dag": "init",
            "last_trig_date": datetime.now(est),
            "client_user": "init",
        },
        "trigger_workerbees": {
            "last_trig_date": datetime.now(est),
            "client_user": "init",
        },
        "saved_trading_models": generate_TradingModel()["MACD"],
        "misc_bucket": [],
        "bee_lounge": [],
        "users_secrets": init_client_user_secrets(),
        "character_image" : mainpage_bee_png,
        "risk_level": 0,
        "age": 0,
        "update_order_rules": [],
        
        "app_order_requests": [], # depr.
        
        "sell_orders": [],
        "sell_orders_requests": [],
        "buy_orders": [],
        "buy_orders_requests": [],

        "queen_processed_orders": [],
        "wave_triggers": [],
        "app_wave_requests": [],
        "trading_models": [],
        "trading_models_requests": [],
        "power_rangers": [],
        "power_rangers_requests": [],
        "power_rangers_lastupdate": datetime.now(est),
        "knight_bees_kings_rules": [],
        "knight_bees_kings_rules_requests": [],
        "queen_controls_reset": False,
        # 'queen_controls': [],
        "queen_controls_requests": [],
        "queen_contorls_lastupdate": False,
        # 'workerbees': [],
        "workerbees_requests": [],
        "subconscious": [],
        "subconscious_requests": [],
        "del_QUEEN_object": [],
        "del_QUEEN_object_requests": [],
        "last_app_update": datetime.now(est),
        "update_queen_order": [],
        "update_queen_order_requests": [],
        # "stop_queen": False,
        "queen_sleep": [],
        "queen_sleep_requests": [],
        "last_modified": {"last_modified": datetime.now(est)},
    }
    return app


def add_key_to_KING(KING):  # returns QUEES
    q_keys = KING.keys()
    latest_init = init_KING()
    update = False
    KING = update_king_users(KING, init=False)
    for k, v in latest_init.items():
        if k not in q_keys:
            KING[k] = v
            update = True
            msg = f'{k}{" : Key Added"}'
            print(msg)
            logging.info(msg)
    return {"KING": KING, "update": update}


def add_key_to_app(QUEEN_KING):  # returns QUEES
    try:
        update = False
        update_msg = {}
        
        q_keys = QUEEN_KING.keys()
        latest_queen = init_QUEEN_KING()
        latest_controls = return_queen_controls()
        latest_qcp = init_qcp()

        for k, v in latest_queen.items():
            if k not in q_keys:
                QUEEN_KING[k] = v
                update = True
                msg = f'{k}{" : Key Added to QUEEN_KING"}'
                print(msg)
                logging.info(msg)
                update_msg[k] = msg
        for k, v in latest_controls.items():
            if k not in QUEEN_KING['king_controls_queen'].keys():
                QUEEN_KING['king_controls_queen'][k] = v
                update = True
                msg = f'{k}{" : Control Key Added to QUEEN_KING"}'
                print(msg)
                logging.info(msg)
                update_msg[k] = msg
        
        for k, v in latest_qcp.items():
            for qcp, qcp_vars in QUEEN_KING['chess_board'].items():
                qcp_keys = qcp_vars.keys()
                if k not in qcp_keys:
                    QUEEN_KING['chess_board'][qcp][k] = latest_qcp.get(k)
                    update = True
                    msg = f'{qcp}: {k} -- {"Key Added to Chess Board"}'
                    print(msg)
                    logging.info(msg)
                    update_msg[k] = msg

        return {"QUEEN_KING": QUEEN_KING, "update": update}
    except Exception as e:
        print_line_of_error(e)

def set_chess_pieces_symbols(QUEEN_KING, qcp_bees_key):
    try:
        all_workers = list(QUEEN_KING[qcp_bees_key].keys())
        # worker_names = [v.get('piece_name') for i, v in QUEEN_KING[qcp_bees_key].items()]
        
        ticker_qcp_index = {}
        view = []
        dups = {}

        for qcp in all_workers:
            view.append(f'{qcp.upper()} ({QUEEN_KING[qcp_bees_key][qcp].get("tickers")} )')
            for ticker in QUEEN_KING[qcp_bees_key][qcp].get("tickers"):
                ticker_qcp_index[ticker] = qcp
                if ticker in dups.keys():
                    dups[ticker] = qcp
        
        return {'ticker_qcp_index': ticker_qcp_index, 'view': view, 'all_workers': all_workers, 'dups': dups}
    except Exception as e:
        print_line_of_error(e)

def return_ticker_qcp_index(QUEEN_KING, qcp_bees_key):
    all_workers = list(QUEEN_KING[qcp_bees_key].keys())
    ticker_qcp_index = {}
    for qcp in all_workers:
        for ticker in QUEEN_KING[qcp_bees_key][qcp].get("tickers"):
            ticker_qcp_index[ticker] = qcp
    
    return ticker_qcp_index


def return_star_from_ttf(x):
    try:
        ticker, tframe, tperiod = x.split("_")
        return f'{tframe}_{tperiod}'
    except Exception as e:
        print(e)
        return x  

def return_symbol_from_ttf(x):
    try:
        return x.split("_")[0]
    except Exception as e:
        print(e, x)
        return x 

def return_trading_model_trigbee(tm_trig, trig_wave_length):
    on_wave_buy = True if trig_wave_length != '0' else False
    if on_wave_buy:
        tm_trig = 'buy_cross-0' if 'buy' in tm_trig else 'sell_cross-0'
    
    return tm_trig


def return_trading_model_mapping(QUEEN_KING, waveview):
    return_main = {}
    for ttf in waveview.index.to_list():
        try:
            ticker = waveview.at[ttf, 'symbol']
            trading_model = QUEEN_KING['king_controls_queen']['symbols_stars_TradingModel'].get(ticker)
            star_time = waveview.at[ttf, 'star_time']
            tm_trig = waveview.at[ttf, 'macd_state']
            trig_wave_length = waveview.at[ttf, 'wave_state']
            # on_wave_buy = True if trig_wave_length != '0' else False
            # if on_wave_buy:
            #     tm_trig = 'buy_cross-0' if 'buy' in tm_trig else 'sell_cross-0'
            tm_trig = return_trading_model_trigbee(tm_trig, trig_wave_length)
            wave_blocktime = waveview.at[ttf, 'wave_blocktime']
            king_order_rules = trading_model['stars_kings_order_rules'][star_time]['trigbees'][tm_trig][wave_blocktime]
            return_main[ttf] = king_order_rules
        except Exception as e:
            print_line_of_error()
            return_main[ttf] = {}
    
    return return_main


def return_queenking_board_symbols(QUEEN_KING, active=True):
    all_workers = list(QUEEN_KING['chess_board'].keys())
    return_qcp_tickers = []
    for qcp in all_workers:
        if QUEEN_KING['chess_board'][qcp].get('buying_power') == 0:
            continue
        # Refresh ChessBoard and RevRec
        qcp_tickers = QUEEN_KING['chess_board'][qcp].get('tickers')
        return_qcp_tickers = return_qcp_tickers + qcp_tickers
    
    return return_qcp_tickers



def reallocate_revrec(revrec, ticker_time_frame, ):
    # return number of shares to sell
    return 0

# check last loss order, if the loss order is > X amount, then set ticker on a 31 day Buying Hold, set this in QUEEN_KING['symbols_buying_hold'] = []

def refresh_chess_board__revrec(acct_info, QUEEN, QUEEN_KING, STORY_bee, active_queen_order_states, 
                                chess_board__revrec={}, revrec__ticker={}, revrec__stars={}, chess_board__revrec_borrow={}, 
                                marginPower={}, save_queenking=False, fresh_board=False):
    # Create/Refresh RevRec from Chess Board
    # WORKERBEE: Add validation only 1 symbol per qcp --- QUEEN not needed only need ORDERS and QUEEN_KING
    rr_starttime = datetime.now()
    def shape_revrec_chesspieces(dic_items, acct_info, chess_board__revrec_borrow, marginPower):
        df_borrow = pd.DataFrame(chess_board__revrec_borrow.items())
        df_borrow = df_borrow.rename(columns={0: 'qcp', 1: 'buying_power_borrow'})
        bpb = sum(df_borrow['buying_power_borrow'])
        df_borrow['borrow_budget'] = (df_borrow['buying_power_borrow'] * acct_info.get('buying_power')) / bpb
        
        df = pd.DataFrame(dic_items.items())
        df = df.rename(columns={0: 'qcp', 1: 'buying_power'})
        bp = sum(df['buying_power'])
        
        df['total_budget'] = (df['buying_power'] * acct_info.get('last_equity')) / bp
        df['equity_budget'] = (df['buying_power'] * acct_info.get('last_equity')) / bp
        df['cash_budget'] = (df['buying_power'] * acct_info.get('cash')) / bp
        
        df = pd.merge(df, df_borrow, how='left', on='qcp')

        df = df.set_index('qcp', drop=False)

        df['margin_power'] = df.index.map(marginPower)
        
        return df

    def shape_revrec_tickers(dic_items, symbol_qcp_dict, df_qcp):
        df = pd.DataFrame(dic_items.items())
        df = df.rename(columns={0: 'qcp_ticker', 1: 'ticker_buying_power'})
        df = df.set_index('qcp_ticker', drop=False)
        df['qcp'] = df['qcp_ticker'].map(symbol_qcp_dict)
        df['margin_power'] = df['qcp'].map(dict(zip(df_qcp['qcp'], df_qcp['margin_power'])))
        
        return df

    def shape_revrec_stars(dic_items, revrec__stars_borrow, symbol_qcp_dict, df_qcp):
        df = pd.DataFrame(dic_items.items())
        df_main = df.rename(columns={0: 'qcp_ticker_star', 1: 'star_buying_power'})

        df = pd.DataFrame(revrec__stars_borrow.items())
        df = df.rename(columns={0: 'qcp_ticker_star', 1: 'star_borrow_buying_power'})

        df_main = df_main.merge(df, how='left', on='qcp_ticker_star')
        df_main = df_main.set_index('qcp_ticker_star', drop=False)
        
        df_main['ticker_time_frame'] = df_main.index
        df_main['ticker'] = df_main['ticker_time_frame'].apply(lambda x: x.split("_")[0])
        df_main['star'] = df_main['ticker_time_frame'].apply(lambda x: return_star_from_ttf(x))
        
        df_main['qcp'] = df_main['ticker'].map(symbol_qcp_dict)

        df_main['margin_power'] = df_main['qcp'].map(dict(zip(df_qcp['qcp'], df_qcp['margin_power'])))

        return df_main


    def return_trading_model(QUEEN_KING, qcp, ticker):
        trading_model = QUEEN_KING['king_controls_queen']['symbols_stars_TradingModel'].get(ticker)
        # Handle missing TM
        if trading_model is None: 
            print(ticker, ' tradingmodel missing handling in revrec to default')
            QUEEN_KING['king_controls_queen']['symbols_stars_TradingModel'].update(generate_TradingModel(ticker=ticker, theme=QUEEN_KING['chess_board'][qcp].get('theme'))["MACD"])
            # save_queenking = True
            trading_model = QUEEN_KING['king_controls_queen']['symbols_stars_TradingModel'].get(ticker)

        return trading_model

    try:
        if fresh_board:
            marginPower={}
            chess_board__revrec_borrow={}
            chess_board__revrec={}
            revrec__ticker={}
            revrec__stars={}
    
        # base line power allocation per qcp
        revrec__stars_borrow = {}
        symbol_qcp_dict = {}

        all_workers = list(QUEEN_KING['chess_board'].keys())

        board_tickers = []
        ticker_TradingModel = {}
        for qcp in all_workers:
            if QUEEN_KING['chess_board'][qcp].get('buying_power') == 0:
                continue
            
            # Refresh ChessBoard and RevRec
            qcp_power = float(QUEEN_KING['chess_board'][qcp]['total_buyng_power_allocation'])
            qcp_borrow = float(QUEEN_KING['chess_board'][qcp]['total_borrow_power_allocation'])
            qcp_marginpower = float(QUEEN_KING['chess_board'][qcp]['margin_power'])
            chess_board__revrec[qcp] = qcp_power
            chess_board__revrec_borrow[qcp] = qcp_borrow
            marginPower[qcp] = qcp_marginpower
            
            qcp_tickers = QUEEN_KING['chess_board'][qcp].get('tickers')
            board_tickers = board_tickers + qcp_tickers

            num_tickers = len(qcp_tickers)
            if num_tickers == 0:
                print("No Tickers in Chess Piece")
                continue
            
            # CONFIRM TRADING MODEL Ticker Budget Allocation
            ticker_mapping = QUEEN_KING['king_controls_queen'].get('ticker_revrec_allocation_mapping')
            ticker_mapping = ticker_mapping if ticker_mapping else {}

            for ticker in qcp_tickers:
                symbol_qcp_dict[ticker] = qcp              
                
                trading_model= return_trading_model(QUEEN_KING, qcp, ticker)
                tm_keys = trading_model['stars_kings_order_rules'].keys()
                ticker_TradingModel[ticker] = trading_model

                ## Ticker Allocation Budget
                if num_tickers == 1:
                    ticker_power = qcp_power
                    revrec__ticker[ticker] = ticker_power
                else:
                    if ticker in ticker_mapping.keys():
                        ticker_power = ticker_mapping[ticker]
                    else:
                        ticker_power = qcp_power / num_tickers # equal number disribution
                    
                    revrec__ticker[ticker] = ticker_power

                # Star Allocation Budget
                for star in tm_keys:
                    revrec__stars[f'{ticker}_{star}'] = trading_model['stars_kings_order_rules'][star].get("buyingpower_allocation_LongTerm")
                    revrec__stars_borrow[f'{ticker}_{star}'] = trading_model['stars_kings_order_rules'][star].get("buyingpower_allocation_ShortTerm")

        # Refresh RevRec Total Budgets
        df_qcp = shape_revrec_chesspieces(chess_board__revrec, acct_info, chess_board__revrec_borrow, marginPower)
        df_ticker = shape_revrec_tickers(revrec__ticker, symbol_qcp_dict, df_qcp)
        df_stars = shape_revrec_stars(revrec__stars, revrec__stars_borrow, symbol_qcp_dict, df_qcp)
        df_stars = df_stars.fillna(0) # tickers without budget move this to upstream in code and fillna only total budget column
        # out of balance
        # ipdb.set_trace()
        for qcp in df_qcp.index:
            tickers_ = df_ticker[df_ticker['qcp'] == qcp]
            if len(tickers_)>0:
                qcp_bp = float(df_qcp.at[qcp, 'buying_power'])
                qcp_tb = float(df_qcp.at[qcp, 'total_budget'])
                deltaa = sum(tickers_['ticker_buying_power']) - qcp_bp
                if abs(deltaa) > .01:
                    msg=(f'{qcp} out of balance by {deltaa} ${round(deltaa * qcp_tb)} Allocation At Risk')
                    st.write(msg)
                    print(msg)

        df_active_orders = pd.DataFrame()
        # print("WORKERS")
        for qcp in all_workers:
            
            piece = QUEEN_KING['chess_board'].get(qcp)
            tickers = list(set(piece.get('tickers')))
            # WORKERBEE query return orders is being called twice, once for ticker and once for star ...
            # ticker_active_orders = {}
            
            for ticker in tickers:
                # TICKER
                df_temp = df_ticker[df_ticker.index.isin(tickers)].copy()
                bp = sum(df_temp['ticker_buying_power'])
                df_temp['total_budget'] = (df_temp['ticker_buying_power'] * df_qcp.at[qcp, 'total_budget']) / bp
                df_temp['equity_budget'] = (df_temp['ticker_buying_power'] * df_qcp.at[qcp, 'equity_budget']) / bp
                df_temp['borrow_budget'] = ((df_temp['ticker_buying_power'] * df_qcp.at[qcp, 'borrow_budget']) / bp) * df_qcp.at[qcp, 'margin_power']
                # budget_remaining, borrowed_budget_remaining = return_ticker_remaining_budgets(cost_basis_current, ticker, df_temp)

                # UPDTAE TICKER
                df_ticker.at[ticker, 'ticker_total_budget'] = df_temp.at[ticker, 'total_budget']
                df_ticker.at[ticker, 'ticker_equity_budget'] = df_temp.at[ticker, 'equity_budget']
                df_ticker.at[ticker, 'ticker_borrow_budget'] = df_temp.at[ticker, 'borrow_budget']
                # df_ticker.at[ticker, 'ticker_remaining_borrow'] = borrowed_budget_remaining

                # UPDATE star time 
                df_temp = df_stars[(df_stars['ticker'].isin([ticker]))].copy()
                bp = sum(df_temp['star_buying_power'])
                bp_borrow = sum(df_temp['star_borrow_buying_power'])
                df_temp['total_budget'] = (df_temp['star_buying_power'] * df_ticker.loc[ticker].get('ticker_total_budget')) / bp
                df_temp['equity_budget'] = (df_temp['star_buying_power'] * df_ticker.loc[ticker].get('ticker_equity_budget')) / bp
                df_temp['borrow_budget'] = (df_temp['star_borrow_buying_power'] * df_ticker.loc[ticker].get('ticker_borrow_budget')) / bp_borrow
                
                current_from_open = 0
                current_from_yesterday = 0
                ticker_remaining_budget = 0
                ticker_remaining_borrow = 0
                ttf_storybeekeys=STORY_bee.keys()
                for star in df_temp['star'].to_list():
                    ticker_time_frame = f'{ticker}_{star}'
                    if '1Minute_1Day' in ticker_time_frame and ticker_time_frame in ttf_storybeekeys:
                        current_from_open = STORY_bee[ticker_time_frame]["story"].get("current_from_open")
                        current_from_yesterday = STORY_bee[ticker_time_frame]["story"].get("current_from_yesterday")
                        df_ticker.at[ticker, 'current_from_open'] = current_from_open
                        df_ticker.at[ticker, 'current_from_yesterday'] = current_from_yesterday
                    
                    df_stars.at[f'{ticker}_{star}', 'star_total_budget'] = df_temp.loc[f'{ticker}_{star}'].get('total_budget')
                    df_stars.at[f'{ticker}_{star}', 'star_equity_budget'] = df_temp.loc[f'{ticker}_{star}'].get('equity_budget')
                    df_stars.at[f'{ticker}_{star}', 'star_borrow_budget'] = df_temp.loc[f'{ticker}_{star}'].get('borrow_budget')
                    star_total_budget = df_stars.at[ticker_time_frame, 'star_total_budget']
                    star_borrow_budget = df_stars.at[ticker_time_frame, 'star_borrow_budget']
                    active_orders, ttf_remaining_budget, remaining_budget_borrow, budget_cost_basis, borrowed_cost_basis, buys_at_play, sells_at_play = return_ttf_remaining_budget(QUEEN=QUEEN, 
                                                                        total_budget=star_total_budget,
                                                                        borrow_budget=star_borrow_budget,
                                                                        ticker_time_frame=ticker_time_frame, 
                                                                        active_queen_order_states=active_queen_order_states)

                    df_stars.at[ticker_time_frame, 'remaining_budget'] = ttf_remaining_budget
                    df_stars.at[ticker_time_frame, 'remaining_budget_borrow'] = remaining_budget_borrow
                    df_stars.at[ticker_time_frame, 'star_at_play'] = budget_cost_basis
                    df_stars.at[ticker_time_frame, 'star_at_play_borrow'] = borrowed_cost_basis
                    df_stars.at[ticker_time_frame, 'star_buys_at_play'] = buys_at_play
                    df_stars.at[ticker_time_frame, 'star_sells_at_play'] = sells_at_play
                    # df_stars.at[ticker_time_frame, 'sell_reccomendation'] =
                    if len(active_orders) > 0: 
                        df_stars.at[ticker_time_frame, 'money'] = sum(active_orders['money'])
                        df_stars.at[ticker_time_frame, 'honey'] = sum(active_orders['honey'])
                        df_active_orders = pd.concat([df_active_orders, active_orders])
                        active_orders_close_today = active_orders[active_orders['side'] == 'buy']
                        if len(active_orders_close_today) > 0:
                            active_orders_close_today = active_orders_close_today[(active_orders_close_today['order_rules'].apply(lambda x: x.get('close_order_today') == True))]
                            active_orders_close_today['long_short'] = np.where(active_orders_close_today['trigname'].str.contains('buy'), 'long', 'short') 
                            buy_orders = active_orders_close_today[active_orders_close_today['long_short'] == 'long']
                            buys_at_play_close_today = sum(buy_orders["cost_basis_current"]) if len(buy_orders) > 0 else 0
                            df_stars.at[ticker_time_frame, 'star_buys_at_play_allocation'] = buys_at_play - buys_at_play_close_today
                        else:
                            df_stars.at[ticker_time_frame, 'star_buys_at_play_allocation'] = buys_at_play
                    else:
                        df_stars.at[ticker_time_frame, 'money'] = 0
                        df_stars.at[ticker_time_frame, 'honey'] = 0
                        df_stars.at[ticker_time_frame, 'star_buys_at_play_allocation'] = buys_at_play
                    
                    ticker_remaining_budget += ttf_remaining_budget
                    ticker_remaining_borrow += remaining_budget_borrow
                
                df_ticker.at[ticker, 'ticker_remaining_budget'] = ticker_remaining_budget
                df_ticker.at[ticker, 'ticker_remaining_borrow'] = ticker_remaining_borrow

        # print("ORDERS")
        if len(df_active_orders) > 0:
            df_active_orders['qty_available'] = pd.to_numeric(df_active_orders['qty_available'], errors='coerce')
            symbols_qty_avail = df_active_orders.groupby("symbol")[['qty_available']].sum().reset_index().set_index('symbol', drop=False)
        else:
            symbols_qty_avail = pd.DataFrame()
        # cost basis at play
        ticker_buys_at_play_dict = df_stars.groupby("ticker")[['star_buys_at_play']].sum().reset_index().set_index('ticker', drop=False)
        ticker_sells_at_play_dict = df_stars.groupby("ticker")[['star_sells_at_play']].sum().reset_index().set_index('ticker', drop=False)

        # order money/honey
        tickers_money = df_stars.groupby("ticker")[['money']].sum().reset_index().set_index('ticker', drop=False)
        tickers_honey = df_stars.groupby("ticker")[['honey']].sum().reset_index().set_index('ticker', drop=False)

        # Wave Analysis 3 triforce view
        # print("WAVES")
        symbols=board_tickers
        symbols = [i for i in symbols if df_ticker.loc[i].get('ticker_buying_power') > 0]

        WAVE_ANALYSIS = ReadPickleData(QUEEN['dbs'].get('PB_Wave_Analysis_Pickle'))

        if 'STORY_bee_wave_analysis' not in WAVE_ANALYSIS.keys():
            print("INIT Board")
            fresh_board = True
        else:
            missing_symbols = [i for i in symbols if i not in WAVE_ANALYSIS['STORY_bee_wave_analysis']['df_storyguage']['symbol'].tolist()]
            if missing_symbols:
                print("MISSING symbols Refresh Wave Analysis: ", missing_symbols)
                fresh_board = True
            if (datetime.now(est) - WAVE_ANALYSIS['fresh_board_timer']).total_seconds() > 1989:
                print("Wave Analysis Refresh Timer")
                fresh_board = True
    
        if fresh_board:
            print("Fresh Board on Wave Analysis")
            resp = wave_analysis__storybee_model(QUEEN_KING, STORY_bee, symbols)
            WAVE_ANALYSIS = {'fresh_board_timer': datetime.now(est), 'STORY_bee_wave_analysis': resp}
            save_queenking = True
        else:
            # print("using Cached Wave Analysis")
            resp = WAVE_ANALYSIS['STORY_bee_wave_analysis']

        storygauge = resp.get('df_storyguage') # wave_gauge
        storygauge = storygauge.set_index('symbol', drop=False)
        waveview = resp.get('df_waveview') # up
        df_storyview = resp.get('df_storyview')
        wave_analysis_down = resp.get('df_storyview_down') # down
        
        # filter out story fails
        waveview['macd_state'] = waveview['macd_state'].fillna('WHO')
        waveview = waveview[~(waveview['macd_state']=='WHO')]

        # for every star ad the stars column to storygauge i.e. trading grid, ... put the kors

        # CURRENLT UNABLE TO HANDLE TICKER IF NOT IN DB : ) WORKERBEE: handle tickers not returned from wave analysis

        star_longs = dict(zip(df_stars.index, df_stars['star_buys_at_play']))
        star_short = dict(zip(df_stars.index, df_stars['star_sells_at_play']))
        star_money = dict(zip(df_stars.index, df_stars['money']))

        waveview['star_buys_at_play'] = waveview.index.map(star_longs)
        waveview['star_sells_at_play'] = waveview.index.map(star_short)
        waveview['star_money'] = waveview.index.map(star_money)
        
        main_indexes = QUEEN['heartbeat']['main_indexes']
        df_broker_portfolio = pd.DataFrame([v for i, v in QUEEN['portfolio'].items()])
        df_broker_portfolio = df_broker_portfolio.set_index('symbol', drop=False)

        
        if len(storygauge) > 0: # should be able to remove this now WORKERBEE
            for symbol in storygauge.index:
                # STORYBEE
                storygauge.at[symbol, 'current_from_open'] = STORY_bee[f'{symbol}_1Minute_1Day']['story'].get('current_from_open')
                
                if symbol in df_ticker.index:
                    storygauge.at[symbol, 'ticker_buying_power'] = df_ticker.at[symbol, 'ticker_buying_power']
                else:
                    storygauge.at[symbol, 'ticker_buying_power'] = 0
                
                if symbol in ticker_buys_at_play_dict.index:
                    storygauge.at[symbol, 'long_at_play'] = ticker_buys_at_play_dict.at[symbol, 'star_buys_at_play']
                else:
                    storygauge.at[symbol, 'long_at_play'] = 0
                if symbol in ticker_sells_at_play_dict.index:
                    storygauge.at[symbol, 'short_at_play'] = ticker_sells_at_play_dict.at[symbol, 'star_sells_at_play']
                else:
                    storygauge.at[symbol, 'short_at_play'] = 0
         
            for symbol in symbols_qty_avail.index:
                if symbol in storygauge.index:
                    storygauge.at[symbol, 'qty_available'] = symbols_qty_avail.at[symbol, 'qty_available']
            for symbol in df_broker_portfolio['symbol'].tolist():
                if symbol in storygauge.index:
                    storygauge.at[symbol, 'broker_qty_available'] = df_broker_portfolio.at[symbol, 'qty_available']
                    storygauge.at[symbol, 'broker_qty_delta'] = float(storygauge.at[symbol, 'qty_available']) - float(df_broker_portfolio.at[symbol, 'qty_available'])
        
        storygauge['broker_qty_delta'] = storygauge['broker_qty_delta'].fillna(0)
        QUEEN['heartbeat']['broker_qty_delta'] = sum(storygauge['broker_qty_delta'])

        current_wave = star_ticker_WaveAnalysis(STORY_bee=STORY_bee, ticker_time_frame="SPY_1Minute_1Day").get('current_wave') # df slice or can be dict
        wave_blocktime = current_wave.get('wave_blocktime')
        
        def revrec_allocation(waveview, df_storyview, wave_analysis_down, wave_blocktime):
            """ WORK ON
            # handle star allocation, conflicts your sellhomes are cancel out the flying
            """
            try:

                """Weights of 3 sets (profit/len, tier_gain, tier_start) to the final allocation table"""


                # Global
                tier_max = 8
                tier_max_universe = tier_max * 2 # 16
                alloc_powerlen_base_weight = .23 #????

                # Weight Tiers of Time and Profit
                allloc_time_weight = 2
                alloc_powerlen_weight = 1
                alloc_currentprofit_weight = 4
                alloc_maxprofit_shot_weight = 1
                revrec_weight_sum = allloc_time_weight + alloc_powerlen_weight + alloc_currentprofit_weight + alloc_maxprofit_shot_weight

                # Weight Tiers of Tier Gain
                macd_weight = 3
                vwap_weight = 2
                rsi_weight = 3
                wavestat_weight_sum = macd_weight + vwap_weight + rsi_weight

                # Weight Tiers of Start Tier
                macd_start_weight = 3
                vwap_start_weight = 2
                rsi_start_weight = 3
                wavestat_start_weight_sum = macd_start_weight + vwap_start_weight + rsi_start_weight

                alloc_trinity_of__len_and_profit = 1
                wave_tiers_allocation = 1
                wave_tier_start = 1
            
                # tier divergence, how many tiers have been gain'd / lost MACD/RSI/VWAP // current profit deviation
                waveview['macd_tier_divergence'] =  waveview['end_tier_macd'] - waveview['start_tier_macd']
                waveview['vwap_tier_divergence'] =  waveview['end_tier_vwap'] - waveview['start_tier_vwap']
                waveview['rsi_tier_divergence'] =  waveview['end_tier_rsi_ema'] - waveview['start_tier_rsi_ema']
                waveview['macd_tier_gain'] =  np.where((waveview['macd_state'].str.contains("buy")) & (waveview['macd_tier_divergence'] > 0), waveview['macd_tier_divergence'], 0)
                waveview['vwap_tier_gain'] =  np.where((waveview['macd_state'].str.contains("buy")) & (waveview['vwap_tier_divergence'] > 0), waveview['vwap_tier_divergence'], 0)
                waveview['rsi_tier_gain'] =  np.where((waveview['macd_state'].str.contains("buy")) & (waveview['rsi_tier_divergence'] > 0), waveview['rsi_tier_divergence'], 0)

                waveview['macd_tier_gain'] =  np.where((waveview['macd_state'].str.contains("sell")) & (waveview['macd_tier_divergence'] < 0), abs(waveview['macd_tier_divergence']), waveview['macd_tier_gain'])
                waveview['vwap_tier_gain'] =  np.where((waveview['macd_state'].str.contains("sell")) & (waveview['vwap_tier_divergence'] < 0), abs(waveview['vwap_tier_divergence']), waveview['vwap_tier_gain'])
                waveview['rsi_tier_gain'] =  np.where((waveview['macd_state'].str.contains("sell")) & (waveview['rsi_tier_divergence'] < 0), abs(waveview['rsi_tier_divergence']), waveview['rsi_tier_gain'])
                waveview['trinity_tier_gain'] =  waveview['macd_tier_gain'] + waveview['vwap_tier_gain'] + waveview['rsi_tier_gain']

                waveview['wave_blocktime'] = wave_blocktime # current_wave.get('wave_blocktime')
                waveview['wave_state'] = waveview['macd_state'].str.split("-").str[-1]

                # waveview['star'] = waveview.index
                waveview['symbol'] = waveview['ticker_time_frame'].apply(lambda x: return_symbol_from_ttf(x))
                waveview['bs_position'] = waveview['macd_state'].apply(lambda x: x.split("_")[0])

                waveview_buy = waveview[waveview['macd_state'].str.contains('buy')]
                waveview_sell = waveview[waveview['macd_state'].str.contains('sell')]

                df_storyview['star'] = df_storyview.index
                wave_analysis_ = df_storyview[['star', 'star_avg_time_to_max_profit']].drop_duplicates().reset_index(drop=True)
                wave_analysis_ = wave_analysis_.set_index('star')
                wave_analysis_length = df_storyview[['star', 'star_avg_length']].drop_duplicates().reset_index(drop=True)
                wave_analysis_length = wave_analysis_length.set_index('star')


                wave_analysis_down['star'] = wave_analysis_down.index
                wave_analysis_sell = wave_analysis_down[['star', 'star_avg_time_to_max_profit']].drop_duplicates().reset_index(drop=True)
                wave_analysis_sell = wave_analysis_sell.set_index('star')
                wave_analysis_length_sell = wave_analysis_down[['star', 'star_avg_length']].drop_duplicates().reset_index(drop=True)
                wave_analysis_length_sell = wave_analysis_length_sell.set_index('star')


                for ttf in waveview.index.to_list():

                    waveview.at[ttf, 'star_time'] = df_stars.at[ttf, 'star']
                    waveview.at[ttf, 'star_total_budget'] = df_stars.at[ttf, 'star_total_budget']
                    waveview.at[ttf, 'star_borrow_budget'] = df_stars.at[ttf, 'star_borrow_budget']
                    waveview.at[ttf, 'remaining_budget'] = df_stars.at[ttf, 'remaining_budget']
                    waveview.at[ttf, 'remaining_budget_borrow'] = df_stars.at[ttf, 'remaining_budget_borrow']
                    waveview.at[ttf, 'star_at_play'] = df_stars.at[ttf, 'star_at_play']
                    waveview.at[ttf, 'star_at_play_borrow'] = df_stars.at[ttf, 'star_at_play_borrow']
                    waveview.at[ttf, 'star_time'] = df_stars.at[ttf, 'star']
                    waveview.at[ttf, 'long_at_play'] = df_stars.at[ttf, 'star_buys_at_play']
                    waveview.at[ttf, 'short_at_play'] = df_stars.at[ttf, 'star_sells_at_play']
                    waveview.at[ttf, 'star_buys_at_play_allocation'] = df_stars.at[ttf, 'star_buys_at_play_allocation']
                    waveview.at[ttf, 'margin_power'] = df_stars.at[ttf, 'margin_power']
                    

                for ttf in waveview_buy.index:
                    waveview.at[ttf, 'star_avg_time_to_max_profit'] = wave_analysis_.loc[ttf].get('star_avg_time_to_max_profit')
                    waveview.at[ttf, 'star_avg_length'] = wave_analysis_length.loc[ttf].get('star_avg_length')

                for ttf in waveview_sell.index:
                    waveview.at[ttf, 'star_avg_time_to_max_profit'] = wave_analysis_sell.loc[ttf].get('star_avg_time_to_max_profit')
                    waveview.at[ttf, 'star_avg_length'] = wave_analysis_length_sell.loc[ttf].get('star_avg_length')

                waveview_map = return_trading_model_mapping(QUEEN_KING, waveview)
                waveview['king_order_rules'] = waveview['ticker_time_frame'].map(waveview_map)

                # start pct
                waveview['macd_start_tier_alloc'] =np.where(waveview['start_tier_macd']==tier_max, 0, waveview['start_tier_macd'] / tier_max)
                waveview['vwap_start_tier_alloc'] =np.where(waveview['start_tier_vwap']==tier_max, 0, waveview['start_tier_vwap'] / tier_max)
                waveview['rsi_start_tier_alloc'] =np.where(waveview['start_tier_rsi_ema']==tier_max, 0, waveview['start_tier_rsi_ema'] / tier_max)

                # max growth
                waveview['macd_tier_max_growth'] = tier_max - waveview['start_tier_macd']
                waveview['vwap_tier_max_growth'] = tier_max - waveview['start_tier_vwap']
                waveview['rsi_tier_max_growth'] = tier_max - waveview['start_tier_rsi_ema']
                # distance to max
                waveview['macd_tier_distance_max_growth'] = np.where(waveview['start_tier_macd']<=0, ((waveview['macd_tier_max_growth'] / tier_max_universe)) * -1, (waveview['macd_tier_max_growth'] / tier_max_universe))
                waveview['vwap_tier_distance_max_growth'] = np.where(waveview['start_tier_vwap']<=0, ((waveview['vwap_tier_max_growth'] / tier_max_universe)) * -1, (waveview['vwap_tier_max_growth'] / tier_max_universe))
                waveview['rsi_tier_distance_max_growth'] = np.where(waveview['start_tier_rsi_ema']<=0, ((waveview['rsi_tier_max_growth'] / tier_max_universe)) * -1, (waveview['rsi_tier_max_growth'] / tier_max_universe))

                waveview['macd_start_tier_alloc'] = np.where(waveview['macd_tier_max_growth']==0, 0, (waveview['macd_start_tier_alloc'] + (waveview['end_tier_macd'] / waveview['macd_tier_max_growth'])))
                waveview['vwap_start_tier_alloc'] = np.where(waveview['vwap_tier_max_growth']==0, 0, (waveview['vwap_start_tier_alloc'] + (waveview['end_tier_vwap'] / waveview['vwap_tier_max_growth'])))
                waveview['rsi_start_tier_alloc'] = np.where(waveview['rsi_tier_max_growth']==0, 0, (waveview['rsi_start_tier_alloc'] + (waveview['end_tier_rsi_ema'] / waveview['rsi_tier_max_growth'])))

                waveview['macd_start_tier_alloc'] = np.where(waveview['macd_start_tier_alloc'] >= 0, 1, waveview['macd_start_tier_alloc'] - 1)
                waveview['vwap_start_tier_alloc'] = np.where(waveview['vwap_start_tier_alloc'] >= 0, 1, waveview['vwap_start_tier_alloc'] - 1)
                waveview['rsi_start_tier_alloc'] = np.where(waveview['rsi_start_tier_alloc'] >= 0, 1, waveview['rsi_start_tier_alloc'] - 1)

                waveview['macd_start_tier_alloc'] = np.where(waveview['macd_start_tier_alloc'] >= 1, 1, waveview['macd_start_tier_alloc'])
                waveview['vwap_start_tier_alloc'] = np.where(waveview['vwap_start_tier_alloc'] >= 1, 1, waveview['vwap_start_tier_alloc'])
                waveview['rsi_start_tier_alloc'] = np.where(waveview['rsi_start_tier_alloc'] >= 1, 1, waveview['rsi_start_tier_alloc'])

                # Tier Gain
                waveview['macd_start_tier_alloc'] = np.where(waveview['macd_start_tier_alloc'] == 0, -.5, waveview['macd_start_tier_alloc'])
                waveview['vwap_start_tier_alloc'] = np.where(waveview['vwap_start_tier_alloc'] == 0, -.5, waveview['vwap_start_tier_alloc'])
                waveview['rsi_start_tier_alloc'] = np.where(waveview['rsi_start_tier_alloc'] == 0, -.5, waveview['rsi_start_tier_alloc'])


                ## base calc variables ##
                # power on current deviation
                waveview['tmp_deivation'] = waveview['time_to_max_profit'] - waveview['star_avg_time_to_max_profit']
                waveview['starmark_len_deivation'] = waveview['length'] / waveview['star_avg_time_to_max_profit']
                # where we are you, tmp - len deviation
                waveview['tmp_length_deivation'] = waveview['time_to_max_profit'] - waveview['length']
                # len - star deviation
                waveview['len__starmark_tmp_deviation'] = waveview['length'] - waveview['star_avg_time_to_max_profit']

                waveview['tmp_deivation_multiplier'] = waveview['tmp_deivation'] / waveview['star_avg_time_to_max_profit']
                waveview['current_tmp_len_multiplier'] = waveview['tmp_length_deivation'] / waveview['star_avg_time_to_max_profit']
                waveview['lev_vs_starmark_tmp_multiplier'] = np.where(waveview['len__starmark_tmp_deviation']>=0, 0, waveview['len__starmark_tmp_deviation'] / waveview['star_avg_time_to_max_profit'])

                waveview['tmp_power'] = waveview['star_total_budget'] * waveview['tmp_deivation_multiplier'] # 
                waveview['tmp_power_len'] = waveview['star_total_budget'] * waveview['current_tmp_len_multiplier'] # 

                # waveview['allocation_power_powerlen'] = np.where((abs(waveview['tmp_power']) - abs(waveview['tmp_power_len'])) < 1, alloc_powerlen_base_weight * waveview['star_total_budget'], waveview['tmp_power'] - waveview['tmp_power_len'])

                """ # TIME to Max Profit Delta from Current Length """
                waveview['alloc_powerlen'] = np.where(waveview['time_to_max_profit'] == 0, 
                                                      -1, 
                                                      ((1- (waveview['length'] - waveview['time_to_max_profit']) / waveview['length']) * -1))
                waveview['alloc_powerlen'] = np.where((waveview['alloc_powerlen'] == -1) & (waveview['length']>1), -.5, waveview['alloc_powerlen']) # check if no mxprofit and length past 1, lose budget

                # OJ allocation time # Allow for Reverse budget outcome
                waveview['allocation'] = waveview['star_total_budget'] * waveview['lev_vs_starmark_tmp_multiplier'] # 
                waveview['allocation_borrow'] = waveview['star_borrow_budget'] * waveview['lev_vs_starmark_tmp_multiplier'] # 

                """# Allocation Profit Deviation # current profit deviation"""
                waveview['current_profit_deviation'] = np.where(
                    (waveview['current_profit'] == waveview['maxprofit']) | 
                    (waveview['current_profit'] == 0) & (waveview['maxprofit'] == 0), 
                    -1, -1 - (waveview['current_profit'] - waveview['maxprofit']) / waveview['maxprofit']
                    )
                waveview['current_profit_deviation'] = np.where(waveview['current_profit']< 0, 0, waveview['current_profit_deviation'] )
                waveview['current_profit_deviation_pct'] = np.where(waveview['current_profit_deviation']== 0, 0, waveview['current_profit_deviation'] )
                waveview['current_profit_deviation_pct'] = np.where(waveview['current_profit_deviation']== -1, -1, waveview['current_profit_deviation'] )

                waveview['maxprofit_shot'] = waveview.index.map(dict(zip(df_storyview.index, df_storyview['ttf_median_maxprofit_median']))) # join from wave analysis
                waveview['maxprofit_shot_weight'] = (waveview['maxprofit'] / waveview['maxprofit_shot'])
                waveview['maxprofit_shot_weight_score'] = np.where(waveview['maxprofit_shot_weight'] == 0, -1, (waveview['maxprofit_shot_weight'] *-1))# np.where(waveview['tmp_mark_deivation'] < 0, waveview['tmp_mark_deivation'] * waveview['remaining_budget'], 0)
                waveview['maxprofit_shot_weight_score'] = np.where(waveview['maxprofit_shot_weight'] >= 1, 0, (waveview['maxprofit_shot_weight_score']))# np.where(waveview['tmp_mark_deivation'] < 0, waveview['tmp_mark_deivation'] * waveview['remaining_budget'], 0)
                # waveview['maxprofit_deviation__shotweight__score'] = ((waveview['current_profit_deviation']) + (waveview['maxprofit_shot_weight_score']) ) / 2

                # Top Level Allocations on Budget - Time, profit deviation, maxprofit shot
                waveview['alloc_time'] = ((waveview['star_total_budget'] * waveview['lev_vs_starmark_tmp_multiplier'])/waveview['star_total_budget']) * allloc_time_weight * (waveview['star_total_budget'] * waveview['lev_vs_starmark_tmp_multiplier'])/revrec_weight_sum
                waveview['alloc_ttmp_length'] = ((waveview['star_total_budget'] * waveview['alloc_powerlen'])/waveview['star_total_budget']) * alloc_powerlen_weight * (waveview['star_total_budget'] * waveview['alloc_powerlen'])/revrec_weight_sum
                waveview['alloc_currentprofit'] = ((waveview['star_total_budget'] * waveview['current_profit_deviation_pct'])/waveview['star_total_budget']) * alloc_currentprofit_weight * (waveview['star_total_budget'] * waveview['current_profit_deviation_pct'])/revrec_weight_sum
                waveview['alloc_maxprofit_shot'] = ((waveview['star_total_budget'] * waveview['maxprofit_shot_weight_score'])/waveview['star_total_budget']) * alloc_maxprofit_shot_weight * (waveview['star_total_budget'] * waveview['maxprofit_shot_weight_score'])/revrec_weight_sum
                waveview['total_allocation_budget'] = waveview['alloc_time'] + waveview['alloc_ttmp_length'] + waveview['alloc_currentprofit'] + waveview['alloc_maxprofit_shot']
                waveview['pct_budget_allocation'] = waveview['total_allocation_budget'] / waveview['star_total_budget']
                waveview['total_allocation_borrow_budget'] = (waveview['pct_budget_allocation'] * waveview['star_borrow_budget'])

                # -Tiers

                #Hold the Line Minimum Allocation with Margin
                # Deploy Allocation Number
                waveview['allocation_deploy'] = np.where((waveview['bs_position']=='buy'), 
                                                         waveview['total_allocation_budget'] - waveview['star_buys_at_play_allocation'], 
                                                         waveview['total_allocation_budget'] - waveview['star_sells_at_play']
                                                         )
                waveview['allocation_deploy'] = np.where(waveview['star_total_budget']<=0,0,waveview['allocation_deploy'])

                waveview['allocation_borrow_deploy'] = np.where((waveview['bs_position']=='buy'), 
                                                                (waveview['total_allocation_borrow_budget'] - waveview['star_buys_at_play_allocation']) , 
                                                                (waveview['total_allocation_borrow_budget'] - waveview['star_sells_at_play']) 
                                                                )
                waveview['allocation_borrow_deploy'] = np.where(waveview['star_borrow_budget']<=0,0,waveview['allocation_borrow_deploy'])
                
                waveview['allocation_long'] = np.where((waveview['bs_position']=='buy'), 
                                                       waveview['total_allocation_budget'] - waveview['star_buys_at_play_allocation'], 
                                                       (waveview['star_total_budget'] - waveview['total_allocation_budget'])
                                                       )
                waveview['allocation_borrow_long'] = np.where((waveview['bs_position']=='buy'), 
                                                       waveview['total_allocation_budget'] - waveview['star_buys_at_play_allocation'], 
                                                       (waveview['star_borrow_budget'] - waveview['total_allocation_budget'])
                                                       )
                # Minimum Allocation // consider when sell, long shold be allocation_long
                waveview['allocation_long_deploy'] = (waveview['allocation_long'] + waveview['allocation_borrow_long'])

            except Exception as e:
                print_line_of_error(e)

            return waveview

        waveview = revrec_allocation(waveview, df_storyview, wave_analysis_down, wave_blocktime)
        
        # print("STORYGAUGE")
        price_info_symbols = QUEEN['price_info_symbols']
        for symbol in storygauge.index:
            token = waveview[waveview['symbol'] == symbol]
            if len(token) > 0:
                storygauge.at[symbol, 'allocation_long'] = sum(token['allocation_long'])
                storygauge.at[symbol, 'allocation_long_deploy'] = sum(token['allocation_long_deploy'])
            if symbol in tickers_money.index:
                storygauge.at[symbol, 'money'] = tickers_money.at[symbol, 'money']
            if symbol in tickers_honey.index:
                storygauge.at[symbol, 'honey'] = tickers_honey.at[symbol, 'honey']
            
            # storybee OR price_info_symbols
            if symbol in price_info_symbols.index:
                storygauge.at[symbol, 'ask'] = price_info_symbols.loc[symbol]['priceinfo'].get('current_ask')
                storygauge.at[symbol, 'bid'] = price_info_symbols.loc[symbol]['priceinfo'].get('current_bid')
                storygauge.at[symbol, 'ask_bid_variance'] = price_info_symbols.loc[symbol]['priceinfo'].get('ask_bid_variance')
                storygauge.at[symbol, 'maker_middle'] = price_info_symbols.loc[symbol]['priceinfo'].get('maker_middle')

            # STORY BEE
            storygauge.at[symbol, 'current_from_open'] = df_ticker.loc[symbol].get('current_from_open')
            storygauge.at[symbol, 'current_from_yesterday'] = df_ticker.loc[symbol].get('current_from_yesterday')
            

        cycle_time = (datetime.now()-rr_starttime).total_seconds()
        if cycle_time > 10:
            msg=("rervec cycle_time > 10 seconds", cycle_time)
            print(msg)
            logging.warning(msg)
        return {'cycle_time': cycle_time, 'df_qcp': df_qcp, 'df_ticker': df_ticker, 'df_stars':df_stars, 
                'df_storyview': df_storyview, 'storygauge': storygauge, 'waveview': waveview, "save_queenking": save_queenking, 'WAVE_ANALYSIS': WAVE_ANALYSIS}
    
    except Exception as e:
        print_line_of_error(f'revrec failed {e}')

### QUEEN UTILS
def star_ticker_WaveAnalysis(STORY_bee, ticker_time_frame, trigbee=False): # buy/sell cross
    """ Waves: Current Wave, answer questions about proir waves """
    
    # index                                                                 0
    # wave_n                                                               37
    # length                                                              8.0
    # wave_blocktime                                            afternoon_2-4
    # wave_start_time                               2022-08-31 15:52:00-04:00
    # wave_end_time                          2022-08-31 16:01:00.146718-04:00
    # trigbee                                                    sell_cross-0
    # maxprofit                                                        0.0041
    # time_to_max_profit                                                  8.0
    # macd_wave_n                                                           0
    # macd_wave_length                                        0 days 00:11:00    

    token_df = pd.DataFrame(STORY_bee[ticker_time_frame]['waves']['buy_cross-0']).T
    current_buywave = token_df.iloc[0]

    token_df = pd.DataFrame(STORY_bee[ticker_time_frame]['waves']['sell_cross-0']).T
    current_sellwave = token_df.iloc[0]

    token_df = pd.DataFrame(STORY_bee[ticker_time_frame]['waves']['ready_buy_cross']).T
    ready_buy_cross = token_df.iloc[0]


    if current_buywave['wave_start_time'] > current_sellwave['wave_start_time']:
        current_wave = current_buywave
    else:
        current_wave = current_sellwave


    d_return = {'buy_cross-0': current_buywave, 'sell_cross-0':current_sellwave, 'ready_buy_cross': ready_buy_cross }



    return {'current_wave': current_wave, 'current_active_waves': d_return}


def find_symbol(main_indexes, ticker, trading_model, trigbee, etf_long_tier=False, etf_inverse_tier=False): # Load Ticker Index ETF Risk Level

    if ticker in main_indexes.keys():
        if 'buy' in trigbee:
            if f'{"long"}{trading_model["index_long_X"]}' in main_indexes[ticker].keys():
                etf_long_tier = f'{"long"}{trading_model["index_long_X"]}'
                ticker = main_indexes[ticker][etf_long_tier]

        if 'sell' in trigbee:
            if f'{"inverse"}{trading_model["index_inverse_X"]}' in  main_indexes[ticker].keys():
                etf_inverse_tier = f'{"inverse"}{trading_model["index_inverse_X"]}'
                ticker = main_indexes[ticker][etf_inverse_tier]


    return {'ticker': ticker, 'etf_long_tier': etf_long_tier, 'etf_inverse_tier': etf_inverse_tier}


def init_charlie_bee(db_root):
    queens_charlie_bee = os.path.join(db_root, 'charlie_bee.pkl')
    if os.path.exists(os.path.join(db_root, 'charlie_bee.pkl')) == False:
        charlie_bee = {'queen_cyle_times': {}}
        PickleData(queens_charlie_bee, charlie_bee)
    else:
        charlie_bee = ReadPickleData(queens_charlie_bee)
    
    return queens_charlie_bee, charlie_bee


def power_amo():
    power_up_amo = 0
    power_rangers_universe = ['mac_ranger', 'hist_ranger']
    power_up_amo = {ranger: 0 for ranger in power_rangers_universe}
    return power_up_amo


def initialize_orders(api, start_date, end_date, symbols=False, limit=500): # TBD
    after = start_date
    until = end_date
    if symbols:
        closed_orders = api.list_orders(status='closed', symbols=symbols, after=after, until=until, limit=limit)
        open_orders = api.list_orders(status='open', symbols=symbols, after=after, until=until, limit=limit)
    else:
        closed_orders = api.list_orders(status='closed', after=after, until=until, limit=limit)
        open_orders = api.list_orders(status='open', after=after, until=until, limit=limit)
    
    return {'open': open_orders, 'closed': closed_orders}


def return_queen_orders__query(QUEEN, queen_order_states, ticker=False, star=False, ticker_time_frame=False, trigbee=False, info='1var able queried at a time'):
    q_orders = QUEEN['queen_orders']
    if len(q_orders) == 1 and q_orders.index[0] == None: # init only
        return ''
    if ticker_time_frame:
        orders = q_orders[q_orders['queen_order_state'].isin(queen_order_states) & (q_orders['ticker_time_frame'].isin([ticker_time_frame]))]
    elif ticker:
        orders = q_orders[q_orders['queen_order_state'].isin(queen_order_states) & (q_orders['ticker'].isin([ticker]))]
    elif star:
        orders = q_orders[q_orders['queen_order_state'].isin(queen_order_states) & (q_orders['star'].isin([star]))] ## needs to be added to orders
    elif trigbee:
        orders = q_orders[q_orders['queen_order_state'].isin(queen_order_states) & (q_orders['trigbee'].isin([trigbee]))] ## needs to be added to orders
    else:
        orders = q_orders[q_orders['queen_order_state'].isin(queen_order_states)] ## needs to be added to orders

    return orders


def return_queen_orders__query(QUEEN, queen_order_states, ticker=False, star=False, ticker_time_frame=False, trigbee=False, info='1var able queried at a time'):
    q_orders = QUEEN['queen_orders']
    if len(q_orders) == 1 and q_orders.index[0] == None: # init only
        return ''
    if ticker_time_frame:
        orders = q_orders[q_orders['queen_order_state'].isin(queen_order_states) & (q_orders['ticker_time_frame'].isin([ticker_time_frame]))]
    elif ticker:
        orders = q_orders[q_orders['queen_order_state'].isin(queen_order_states) & (q_orders['ticker'].isin([ticker]))]
    elif star:
        orders = q_orders[q_orders['queen_order_state'].isin(queen_order_states) & (q_orders['star'].isin([star]))] ## needs to be added to orders
    elif trigbee:
        orders = q_orders[q_orders['queen_order_state'].isin(queen_order_states) & (q_orders['trigbee'].isin([trigbee]))] ## needs to be added to orders
    else:
        orders = q_orders[q_orders['queen_order_state'].isin(queen_order_states)] ## needs to be added to orders

    return orders


def check_length(val):
    if pd.isna(val):
        return False
    elif isinstance(val, dict):
        return len(val) > 0
    elif isinstance(val, str):
        return len(val) > 0
    elif isinstance(val, list):
        return len(val) > 0
    else:
        return False


def return_queen_orders__profit_loss(QUEEN, queen_orders, queen_order_states, ticker): # closed queen orders
    # the check only happens if not currently on a hold QUEEN
    queen_orders = QUEEN['queen_orders']
    if len(queen_orders) == 1 and queen_orders.index[0] == None: # init only
        return ''
    orders = queen_orders[
        queen_orders['queen_order_state'].isin(queen_order_states) & 
        queen_orders['ticker'].isin([ticker]) & 
        queen_orders['sell_reason'].apply(check_length)
    ]
    # filter to last 30 days 
    start_date = datetime.now(est) - timedelta(days=30)
    end_date = datetime.now(est)

    # Filter the rows
    filtered_orders = orders[(orders['datetime'] >= start_date) & (orders['datetime'] <= end_date)]
    if len(filtered_orders) == 0:
        return ''

    return orders


def return_ttf_remaining_budget(QUEEN, total_budget, borrow_budget, active_queen_order_states, ticker_time_frame, cost_basis_ref='cost_basis_current'):
    try:
        # Total In Running, Remaining
        active_orders = return_queen_orders__query(QUEEN, queen_order_states=active_queen_order_states, ticker_time_frame=ticker_time_frame,)
        if len(active_orders) == 0:
            return '', total_budget, borrow_budget, 0, 0, 0, 0
        
        # handle long_short in update WORKERBEE
        active_orders['long_short'] = np.where(active_orders['trigname'].str.contains('buy'), 'long', 'short') 
        buy_orders = active_orders[active_orders['long_short'] == 'long']
        sell_orders = active_orders[active_orders['long_short'] == 'short']
        # get cost basis
        cost_basis_current = sum(active_orders[cost_basis_ref]) if len(active_orders) > 0 else 0
        buys_at_play = sum(buy_orders[cost_basis_ref]) if len(buy_orders) > 0 else 0
        sells_at_play = sum(sell_orders[cost_basis_ref]) if len(sell_orders) > 0 else 0

        # check current cost_basis
        if cost_basis_current == 0:
            budget_cost_basis = 0
            borrowed_cost_basis = 0
            remaining_budget = total_budget
            remaining_budget_borrow = borrow_budget
            return active_orders, remaining_budget, remaining_budget_borrow, budget_cost_basis, borrowed_cost_basis, buys_at_play, sells_at_play
        
        remaining_budget = total_budget - cost_basis_current
        if remaining_budget < 0:
            budget_cost_basis = total_budget
            borrowed_cost_basis = abs(remaining_budget)
            # (ticker_time_frame, "over budget")
            remaining_budget_borrow = borrow_budget - borrowed_cost_basis
            if remaining_budget_borrow < 0:
                # (ticker_time_frame, "WHATT YOU WENT OVER BORROW BUDGET")
                remaining_budget_borrow = 0
        else:
            budget_cost_basis = cost_basis_current
            borrowed_cost_basis = 0
            remaining_budget = remaining_budget
            remaining_budget_borrow = borrow_budget
        
        return active_orders, remaining_budget, remaining_budget_borrow, budget_cost_basis, borrowed_cost_basis, buys_at_play, sells_at_play
    
    except Exception as e:
        print_line_of_error("return_ttf_remaining_budget")


def add_trading_model(status, QUEEN_KING, ticker, model='MACD', theme="nuetral"):
    # tradingmodel1["SPY"]["stars_kings_order_rules"]["1Minute_1Day"]["trigbees" ]["buy_cross-0"]["morning_9-11"].items()
    try:
        if model is None or ticker is None or theme is None:
            print("TM Vars Not Available")
            print(f'{model} {ticker} {theme}')
            return QUEEN_KING
        
        print(ticker, " Updating Trading Model ", model, theme)
        tradingmodel1 = generate_TradingModel(ticker=ticker, status=status, theme=theme)[model]
        if tradingmodel1 is not None:
            QUEEN_KING['king_controls_queen']['symbols_stars_TradingModel'].update(tradingmodel1)
            return QUEEN_KING
        else:
            print("error in tm")
    except Exception as e:
        print_line_of_error("adding trading model error")


def add_key_to_QUEEN(QUEEN, queens_chess_piece):  # returns QUEEN
    update = False
    q_keys = QUEEN.keys()
    latest_queen = init_queen("queen")
    for k, v in latest_queen.items():
        if k not in q_keys:
            QUEEN[k] = v
            update = True
            msg = f'{k}{" : Key Added to "}{queens_chess_piece}'
            print(msg)
            logging.info(msg)

    for k, v in latest_queen["queen_controls"].items():
        if k not in QUEEN["queen_controls"].keys():
            QUEEN["queen_controls"][k] = v
            update = True
            msg = f'{k}{" : queen controls Key Added to "}{queens_chess_piece}'
            print(msg)
            logging.info(msg)

    for k, v in latest_queen["heartbeat"].items():
        if k not in QUEEN["heartbeat"].keys():
            QUEEN["heartbeat"][k] = v
            update = True
            msg = f'{k}{" : queen heartbeat Key Added to "}{queens_chess_piece}'
            print(msg)
            logging.info(msg)

    for k, v in latest_queen["workerbees"].items():
        if k not in QUEEN["workerbees"].keys():
            QUEEN["workerbees"][k] = v
            update = True
            msg = f'{k}{" : queen workerbees Key Added to "}{queens_chess_piece}'
            print(msg)
            logging.info(msg)

    return {"QUEEN": QUEEN, "update": update}


def return_STORYbee_trigbees(QUEEN, STORY_bee, tickers_filter=False):
    now_time = datetime.now(est)
    # all_trigs = {k: i['story']["macd_state"] for (k, i) in STORY_bee.items() if len(i['story']["macd_state"]) > 0 and (now_time - i['story']['time_state']).seconds < 33}
    # active_trigs = {k: i['story']["macd_state"] for (k, i) in STORY_bee.items() if len(i['story']["macd_state"]) > 0 and i['story']["macd_state"] in QUEEN['heartbeat']['available_triggerbees'] and (now_time - i['story']['time_state']).seconds < 33}

    # ticker_storys = {k:v for (k, v) in STORY_bee.items() if k.split("_")[0] == ticker} # filter by ticker
    # ticker_storys["TSLA_1Minute_1Day"].keys() >>> # dict_keys(['story', 'waves', 'KNIGHTSWORD'])
    # all_trigs = {k: v['story']['macd_state'] for (k,v) in STORY_bee.items()}
    all_current_trigs = {}
    active_trigs = {}
    for ttf, story_ in STORY_bee.items():
        ticker = ttf.split("_")[0]
        if tickers_filter:
            if ticker not in tickers_filter:
                continue  # next ttf
        if (story_["story"]["macd_state"] in QUEEN["heartbeat"]["available_triggerbees"] and (now_time - story_["story"]["time_state"]).seconds < 33):
            if ttf not in active_trigs.keys():
                active_trigs[ttf] = []
            active_trigs[ttf].append(story_["story"]["macd_state"])
        elif (now_time - story_["story"]["time_state"]).seconds < 33:
            if ttf not in all_current_trigs.keys():
                all_current_trigs[ttf] = []
            all_current_trigs[ttf].append(story_["story"]["macd_state"])

    return {"active_trigs": active_trigs, "all_current_trigs": all_current_trigs}


""" STORY: I want a dict of every ticker and the chart_time TRADE buy/signal weights """


### Story
# trade closer to ask price .... sellers closer to bid .... measure divergence from bid/ask to give weight
def pollen_story(pollen_nectar):
    # define weights in global and do multiple weights for different scenarios..
    # MACD momentum from past N times/days
    # TIME PAST SINCE LAST HIGH TO LOW to change weight & how much time passed since tier cross last high?
    # how long since last max/min value reached (reset time at +- 2)

    # >/ create ranges for MACD & RSI 4-3, 70-80, or USE Prior MAX&Low ...
    # >/ what current macd tier values in comparison to max/min


    def return_macd_wave_story(df, trigbees, ticker_time_frame, tframe):
        # POLLENSTORY = read_pollenstory()
        # df = POLLENSTORY["SPY_1Minute_1Day"]
        # trigbees = ["buy_cross-0", "sell_cross-0"]
        # length and height of wave
        def wave_series():
            return True
        MACDWAVE_story = {"story": {}}
        MACDWAVE_story.update({trig_name: {} for trig_name in trigbees})

        for trigger in trigbees:
            trig_buy = True if 'buy' in trigger else False
            wave_col_name = f'{trigger}{"__wave"}'
            wave_col_wavenumber = f'{trigger}{"__wave_number"}'

            num_waves = df[wave_col_wavenumber].tolist()
            num_waves_list = list(set(num_waves))
            num_waves_list = [
                str(i) for i in sorted([int(i) for i in num_waves_list], reverse=True)
            ]

            for wave_n in num_waves_list:
                MACDWAVE_story[trigger][wave_n] = {}
                MACDWAVE_story[trigger][wave_n].update({"wave_n": wave_n})
                if wave_n == "0":
                    continue
                df_waveslice = df[
                    ["timestamp_est", wave_col_wavenumber, "story_index", wave_col_name, "macd_tier", "hist_tier", "vwap_tier", "rsi_ema_tier"]
                ].copy()
                df_waveslice = df[
                    df[wave_col_wavenumber] == wave_n
                ]  # slice by trigger event wave start / end

                row_1 = df_waveslice.iloc[0]["story_index"]
                row_2 = df_waveslice.iloc[-1]["story_index"]
                current_profit = (df_waveslice.iloc[-1].get('close') - df_waveslice.iloc[0].get('close')) / df_waveslice.iloc[-1].get('close')
                current_profit = current_profit * -1 if 'sell' in trigger else current_profit

                # we want to know the how long it took to get to low?

                # Assign each waves timeblock
                if "Day" in tframe:
                    wave_blocktime = "Day"
                    wave_starttime = df_waveslice.iloc[0]["timestamp_est"]
                    wave_endtime = df_waveslice.iloc[-1]["timestamp_est"]
                else:
                    wave_starttime = df_waveslice.iloc[0]["timestamp_est"]
                    wave_endtime = df_waveslice.iloc[-1]["timestamp_est"]
                    wave_starttime_token = wave_starttime.replace(tzinfo=None)
                    if wave_starttime_token < wave_starttime_token.replace(hour=11, minute=0):
                        wave_blocktime = "morning_9-11"
                    elif wave_starttime_token >= wave_starttime_token.replace(hour=11, minute=0) and wave_starttime_token < wave_starttime_token.replace(hour=14, minute=0):
                        wave_blocktime = "lunch_11-2"
                    elif wave_starttime_token >= wave_starttime_token.replace(hour=14, minute=0) and wave_starttime_token < wave_starttime_token.replace(hour=16, minute=1):
                        wave_blocktime = "afternoon_2-4"
                    else:
                        wave_blocktime = "afterhours"

                macd_start_tier = df_waveslice.iloc[0].get('macd_tier')
                macd_end_tier = df_waveslice.iloc[-1].get('macd_tier')
                macd_tier_divergence = macd_end_tier - macd_start_tier

                vwap_start_tier=df_waveslice.iloc[0].get('vwap_tier')
                vwap_end_tier=df_waveslice.iloc[-1].get('vwap_tier')
                vwap_tier_divergence = vwap_end_tier - vwap_start_tier

                rsi_start_tier=df_waveslice.iloc[0].get('rsi_ema_tier')
                rsi_end_tier=df_waveslice.iloc[-1].get('rsi_ema_tier')
                rsi_tier_divergence = rsi_end_tier - rsi_start_tier

                
                if trig_buy:
                    macd_tier_gain = macd_tier_divergence if macd_tier_divergence > 0 else 0
                    vwap_tier_gain = vwap_tier_divergence if vwap_tier_divergence > 0 else 0
                    rsi_tier_gain = rsi_tier_divergence if rsi_tier_divergence > 0 else 0
                else: # sell
                    macd_tier_gain = abs(macd_tier_divergence) if macd_tier_divergence < 0 else 0
                    vwap_tier_gain = abs(vwap_tier_divergence) if vwap_tier_divergence < 0 else 0
                    rsi_tier_gain = abs(rsi_tier_divergence) if rsi_tier_divergence < 0 else 0

                trinity_tier_gain =  macd_tier_gain + vwap_tier_gain + rsi_tier_gain
                
                MACDWAVE_story[trigger][wave_n].update(
                    {
                        "ticker_time_frame": ticker_time_frame,
                        "length": row_2 - row_1,
                        "wave_blocktime": wave_blocktime,
                        "wave_start_time": wave_starttime,
                        "wave_end_time": wave_endtime,
                        "trigbee": trigger,
                        "wave_id": f'{trigger}{"_"}{wave_blocktime}{"_"}{wave_starttime}',
                        # macd
                        "start_tier_macd": df_waveslice.iloc[0].get('macd_tier'),
                        "end_tier_macd": df_waveslice.iloc[-1].get('macd_tier'),
                        # vwap
                        "start_tier_vwap": df_waveslice.iloc[0].get('vwap_tier'),
                        "end_tier_vwap": df_waveslice.iloc[-1].get('vwap_tier'),
                        # rsi
                        "start_tier_rsi_ema": df_waveslice.iloc[0].get('rsi_ema_tier'),
                        "end_tier_rsi_ema": df_waveslice.iloc[-1].get('rsi_ema_tier'),
                        # profit
                        "current_profit": current_profit,
                        # tier gains
                        "macd_tier_gain": macd_tier_gain,
                        "vwap_tier_gain": vwap_tier_gain,
                        "rsi_tier_gain": rsi_tier_gain,
                        "trinity_tier_gain": trinity_tier_gain,
                        # WORKERBEE put revrec wave analysis here on wavestory + wave_gauge
                    }
                )

                wave_height_value = max(df_waveslice[wave_col_name].values)

                # how long was it profitable?
                profit_df = df_waveslice[df_waveslice[wave_col_name] > 0].copy()
                profit_length = len(profit_df)

                if profit_length > 0:
                    max_profit_index = profit_df[profit_df[wave_col_name] == wave_height_value].iloc[0]["story_index"]
                    time_to_max_profit = max_profit_index - row_1
                    # mx_profit_deviation = (current_profit - wave_height_value) / wave_height_value
                    
                    MACDWAVE_story[trigger][wave_n].update(
                        {
                            "maxprofit": wave_height_value,
                            "time_to_max_profit": time_to_max_profit,
                            "mxp_macd_tier": df_waveslice.at[max_profit_index, 'macd_tier'],
                            "mxp_vwap_tier": df_waveslice.at[max_profit_index, 'vwap_tier'],
                            "mxp_rsi_ema_tier": df_waveslice.at[max_profit_index, 'rsi_ema_tier'],

                        }
                    )

                else:
                    MACDWAVE_story[trigger][wave_n].update(
                        {"maxprofit": wave_height_value, 
                         "time_to_max_profit": 0,
                        "mxp_macd_tier": None,
                        "mxp_vwap_tier": None,
                        "mxp_rsi_ema_tier": None,
                         }
                    )


        return MACDWAVE_story


    def return_waves_measurements(df, ticker_time_frame, trigbees=["buy_cross-0", "sell_cross-0", "ready_buy_cross"]):
        # POLLENSTORY = read_pollenstory()
        # df = POLLENSTORY["SPY_1Minute_1Day"]
        # trigbees = ["macd_cross"]
        # length and height of wave

        # """ use shift to get row index"""
        # # Create a sample DataFrame
        # df = pd.DataFrame({'col1': [1, 4, 7, 10], 'col2': [10, 20, 30, 40]})
        # # Create a new column 'new_column' that calculates the difference between 'col1' and the previous row's value of 'col1'
        # df['new_column'] = np.where(df['col1'] - df['col1'].shift(1) != 0, df['col1'] - df['col1'].shift(1), 0)

        # df['new_column'] = np.where(df['close'] > 0, ((df['close'] - df['close'].shift(1))/ df['close']), 0)

        ticker, tframe, frame = ticker_time_frame.split("_")

        def profit_loss(df_waves, x):
            if x == 0:
                return 0
            else:
                prior_row = df_waves.iloc[x - 1]
                current_row = df_waves.iloc[x]
                latest_price = current_row["close"]
                origin_trig_price = prior_row["close"]
                profit_loss = (latest_price - origin_trig_price) / latest_price
                if df_waves.iloc[x]["macd_cross"] == "sell_cross-0":
                    profit_loss * -1
                return profit_loss


        def macd_cross_WaveLength(df_waves, x):
            if x == 0:
                return 0
            else:
                latest_prices = df_waves["story_index"].values
                prior_prices = np.roll(latest_prices, 1)  # Shift the array to get previous prices
                length = latest_prices[x] - prior_prices[x]
                return length



        def macd_cross_WaveBlocktime(df_waves, x):
            # Assign each waves timeblock
            # WORKERBEE preset times and turn this func into np.where
            if x == 0:
                return 0
            if "Day" in tframe:
                return "Day"
            else:
                wave_starttime = df_waves.iloc[x]["timestamp_est"]
                # wave_endtime = df_waves.iloc[x]['timestamp_est']
                wave_starttime_token = wave_starttime.replace(tzinfo=None)
                if wave_starttime_token < wave_starttime_token.replace(hour=11, minute=0):
                    return "morning_9-11"
                elif wave_starttime_token >= wave_starttime_token.replace(
                    hour=11, minute=0
                ) and wave_starttime_token < wave_starttime_token.replace(hour=14, minute=0):
                    return "lunch_11-2"
                elif wave_starttime_token >= wave_starttime_token.replace(
                    hour=14, minute=0
                ) and wave_starttime_token < wave_starttime_token.replace(hour=16, minute=1):
                    return "afternoon_2-4"
                else:
                    return "afterhours"

        # set wave num
        df_waves = df[df["macd_cross"].isin(trigbees)].copy().reset_index()

        df_check = df[~df["macd_cross"].isin(trigbees)].copy().reset_index()
        if len(df_check) <= 0:
            print("wtf hive ", df_check)
        df_waves["wave_n"] = df_waves.index
        # df_waves["length"] = df_waves["wave_n"].apply(
        #     lambda x: macd_cross_WaveLength(df_waves, x)
        # )
        df_waves['length'] = [macd_cross_WaveLength(df_waves, x) for x in range(len(df_waves))]

        df_waves["profits"] = df_waves["wave_n"].apply(lambda x: profit_loss(df_waves, x))
        # df_waves['profits'] = profit_loss(df_waves)

        # df_waves['story_index_in_profit'] = np.where(df_waves['profits'] > 0, 1, 0)
        df_waves["active_wave"] = np.where(
            df_waves["wave_n"] == df_waves["wave_n"].iloc[-1], "active", "not_active"
        )
        df_waves["wave_blocktime"] = df_waves["wave_n"].apply(
            lambda x: macd_cross_WaveBlocktime(df_waves, x)
        )

        index_wave_series = dict(zip(df_waves["story_index"], df_waves["wave_n"]))
        df["wave_n"] = df["story_index"].map(index_wave_series).fillna("000")

        index_wave_series = dict(zip(df_waves["story_index"], df_waves["length"]))
        df["length"] = df["story_index"].map(index_wave_series).fillna("000")

        index_wave_series = dict(zip(df_waves["story_index"], df_waves["wave_blocktime"]))
        df["wave_blocktime"] = df["story_index"].map(index_wave_series).fillna("000")

        index_wave_series = dict(zip(df_waves["story_index"], df_waves["profits"]))
        df["profits"] = df["story_index"].map(index_wave_series).fillna("000")

        # index_wave_series = dict(zip(df_waves['story_index'], df_waves['story_index_in_profit']))
        # df['story_index_in_profit'] = df['story_index'].map(index_wave_series).fillna("0")

        index_wave_series = dict(zip(df_waves["story_index"], df_waves["active_wave"]))
        df["active_wave"] = df["story_index"].map(index_wave_series).fillna("000")

        df_waves = df_waves[
            [
                "story_index",
                "wave_blocktime",
                "timestamp_est",
                "macd_cross",
                "wave_n",
                "length",
                "profits",
                "active_wave",
            ]
        ]

        return {"df": df, "df_waves": df_waves}


    def assign_MACD_Tier(df, mac_world, tiers_num):
        # create tier ranges
        # tiers_num = 8

        def create_tier_range(m_high, m_low, tiers_num):
            # m_high = mac_world_ranges[ftime]
            # m_low = mac_world_ranges[ftime] * -1

            tiers_add = m_high / tiers_num
            td_high = {}
            for i in range(tiers_num):
                if i == 0:
                    td_high[i] = (0, tiers_add)
                else:
                    td_high[i] = (td_high[i - 1][1], td_high[i - 1][1] + tiers_add)

            tiers_add = m_low / tiers_num
            td_low = {}
            for i in range(tiers_num):
                if i == 0:
                    td_low[i] = (0, tiers_add)
                else:
                    td_low[i] = (td_low[i - 1][1], td_low[i - 1][1] + tiers_add)

            return {"td_high": td_high, "td_low": td_low}

        def assign_tier_num(num_value, td):
            length_td = len(td)  ## Max Tier
            max_num_value = td[length_td - 1][1]  ## max value of range

            for k, v in td.items():
                num_value = float(num_value)

                if num_value > 0 and num_value > v[0] and num_value < v[1]:
                    # (k, num_value)
                    return k
                elif num_value < 0 and num_value < v[0] and num_value > v[1]:
                    # (k, num_value)
                    return k
                elif num_value > 0 and num_value >= max_num_value:
                    # ("way above")
                    return length_td
                elif num_value < 0 and num_value <= max_num_value:
                    # ("way below")
                    return length_td
                elif num_value == 0:
                    # ('0 really')
                    return 0


        # "MACD"
        if mac_world["macd_high"] == 0:  # no max min exist yet (1day scenario)
            m_high = 1
            m_low = -1
        else:
            m_high = mac_world["macd_high"]
            m_low = mac_world["macd_low"]
        tier_range = create_tier_range(m_high, m_low, tiers_num)
        td_high = tier_range["td_high"]
        td_low = tier_range["td_low"]
        df["macd_tier"] = np.where(
            (df["macd"] > 0),
            df["macd"].apply(lambda x: assign_tier_num(num_value=x, td=td_high)),
            df["macd"].apply(lambda x: assign_tier_num(num_value=x, td=td_low)),
        )

        # df["macd_tier"] = np.where(
        #     df["macd"] > 0,
        #     assign_tier_num_vectorized(df["macd"], td=td_high),
        #     assign_tier_num_vectorized(df["macd"], td=td_low),
        # )

        df["macd_tier"] = np.where(df["macd"] > 0, df["macd_tier"], df["macd_tier"] * -1)


        # "MAC HIST"
        if mac_world["hist_high"] == 0:  # no max min exist yet (1day scenario)
            m_high = 1
            m_low = -1
        else:
            m_high = mac_world["hist_high"]
            m_low = mac_world["hist_low"]
        tier_range = create_tier_range(m_high, m_low, tiers_num)
        td_high = tier_range["td_high"]
        td_low = tier_range["td_low"]
        df["hist_tier"] = np.where(
            (df["hist"] > 0),
            df["hist"].apply(lambda x: assign_tier_num(num_value=x, td=td_high)),
            df["hist"].apply(lambda x: assign_tier_num(num_value=x, td=td_low)),
        )
        df["hist_tier"] = np.where(df["hist"] > 0, df["hist_tier"], df["hist_tier"] * -1)

        # "RSI"
        if mac_world["rsi_ema_high"] == 0:  # no max min exist yet (1day scenario)
            m_high = 1
            m_low = -1
        else:
            m_high = mac_world["rsi_ema_high"]
            m_low = mac_world["rsi_ema_low"]
        tier_range = create_tier_range(m_high, m_low, tiers_num)
        td_high = tier_range["td_high"]
        td_low = tier_range["td_low"]
        df["rsi_ema_tier"] = np.where(
            (df["rsi_ema"] > 0),
            df["rsi_ema"].apply(lambda x: assign_tier_num(num_value=x, td=td_high)),
            df["rsi_ema"].apply(lambda x: assign_tier_num(num_value=x, td=td_low)),
        )
        df["rsi_ema_tier"] = np.where(df["rsi_ema"] > 0, df["rsi_ema_tier"], df["rsi_ema_tier"] * -1)

        # "VWAP"
        if mac_world["vwap_deviation_high"] == 0:  # no max min exist yet (1day scenario)
            m_high = 1
            m_low = -1
        else:
            m_high = mac_world["vwap_deviation_high"]
            m_low = mac_world["vwap_deviation_low"]
        tier_range = create_tier_range(m_high, m_low, tiers_num)
        df["vwap_tier"] = np.where(
            (df["vwap_deviation"] > 0),
            df["vwap_deviation"].apply(lambda x: assign_tier_num(num_value=x, td=tier_range["td_high"])),
            df["vwap_deviation"].apply(lambda x: assign_tier_num(num_value=x, td=tier_range["td_low"])),
        )
        df["vwap_tier"] = np.where(df["vwap_deviation"] > 0, df["vwap_tier"], df["vwap_tier"] * -1)

        return df


    def power_ranger_mapping(
        tier_value,
        colors=[
            "red",
            "blue",
            "pink",
            "yellow",
            "white",
            "green",
            "orange",
            "purple",
            "black",
        ],
    ):
        # When 1M macd tier in range (-7, -5) + 50% : Red // Sell :: 1%
        # When 1M macd tier in range (-5, -3) + 40% : Blue // Sell :: 1%
        # When 1M macd tier in range (-3, -2) + 25% : Pink // Sell :: 1%
        # When 1M macd tier in range (-2, -1) + 10% : Yellow // Sell :: 1%
        # When 1M macd tier in range (-1, 1) + 1% : White // Sell :: 1%
        # When 1M macd tier in range (1, 2) + 1% : Green // Sell :: 1%
        # When 1M macd tier in range (2, 3) + 1% : orange // Sell :: 25%
        # When 1M macd tier in range (3, 5) + 1% : purple // Sell :: 40%
        # When 1M macd tier in range (5, 7) + 1% : Black // Sell :: 50%

        tier_value = float(tier_value)

        if tier_value >= -8 and tier_value <= -7:
            return "red"
        elif tier_value >= -6 and tier_value <= -5:
            return "blue"
        elif tier_value >= -4 and tier_value <= -3:
            return "pink"
        elif tier_value >= -2 and tier_value <= -1:
            return "yellow"
        elif tier_value > -1 and tier_value <= 1:
            return "white"
        elif tier_value >= 2 and tier_value <= 3:
            return "green"
        elif tier_value >= 4 and tier_value <= 5:
            return "purple"
        elif tier_value >= 6 and tier_value >= 7:
            return "black"
        else:
            return "black"


    def power_ranger_mapping_vectorized(tier_values):
        tier_values = np.asarray(tier_values, dtype=float)
        
        conditions = [
            (tier_values >= -8) & (tier_values <= -7),
            (tier_values >= -6) & (tier_values <= -5),
            (tier_values >= -4) & (tier_values <= -3),
            (tier_values >= -2) & (tier_values <= -1),
            (tier_values > -1) & (tier_values <= 1),
            (tier_values >= 2) & (tier_values <= 3),
            (tier_values >= 4) & (tier_values <= 5),
            (tier_values >= 6) & (tier_values <= 7)
        ]
        
        choices = [
            "red", "blue", "pink", "yellow",
            "white", "green", "purple", "black"
        ]
        
        result = np.select(conditions, choices, default="black")
        return result

    try:
        s = datetime.now(est)
        story = {}
        ANGEL_bee = {}  # add to QUEENS mind
        STORY_bee = {}
        betty_bee = {k: {} for k in pollen_nectar.keys()}  # monitor function speeds
        knights_sight_word = {}

        def pollenstory_cycle(ticker_time_frame, df_i):
            try:
                s_ttfame_func_check = datetime.now(est)
                ticker, tframe, frame = ticker_time_frame.split("_")

                trigbees = ["buy_cross-0", "sell_cross-0", "ready_buy_cross"]

                ANGEL_bee[ticker_time_frame] = {}
                STORY_bee[ticker_time_frame] = {"story": {}}

                df = df_i.fillna(0).copy()
                df = df.reset_index(drop=True)
                df["story_index"] = df.index
                df_len = len(df)

                # adjust rsi
                rsi_t = df[~df['rsi_ema'].isin([0,100])]
                
                # macd signal divergence
                df["macd_singal_deviation"] = df["macd"] - df["signal"]
                # devation from vwap
                df["vwap_deviation"] = df["close"] - df["vwap"]
                df["vwap_deviation_pct"] =  df["vwap_deviation"] / df["close"]

                mac_world = {
                    "macd_high": df["macd"].max(),
                    "macd_low": df["macd"].min(),
                    "signal_high": df["signal"].max(),
                    "signal_low": df["signal"].min(),
                    "hist_high": df["hist"].max(),
                    "hist_low": df["hist"].min(),
                    "rsi_ema_high": rsi_t["rsi_ema"].max(),
                    "rsi_ema_low": rsi_t["rsi_ema"].min(),
                    "vwap_deviation_high": df["vwap_deviation"].max(),
                    "vwap_deviation_low": df["vwap_deviation"].min(),
                }

                # Story Bee >>> Wave Info

                STORY_bee[ticker_time_frame]["story"]["macd_singal_deviation"] = df.iloc[-1]["macd_singal_deviation"]
                STORY_bee[ticker_time_frame]["story"]["vwap_deviation"] = df.iloc[-1]["vwap_deviation"]
                STORY_bee[ticker_time_frame]["story"]["vwap_deviation_pct"] = df.iloc[-1]["vwap_deviation_pct"]
                current_ask = df.iloc[-1].get("current_ask")
                current_bid = df.iloc[-1].get("current_bid")
                STORY_bee[ticker_time_frame]["story"]["current_ask"] = current_ask
                STORY_bee[ticker_time_frame]["story"]["current_bid"] = current_bid
                best_limit_price = get_best_limit_price(ask=current_ask, 
                                                        bid=current_bid )
                maker_middle = best_limit_price['maker_middle']
                ask_bid_variance = None if current_ask is None else current_bid / current_ask
                STORY_bee[ticker_time_frame]["story"]["maker_middle"] = maker_middle
                STORY_bee[ticker_time_frame]["story"]["ask_bid_variance"] = ask_bid_variance

                # Measure MACD WAVES
                # change % shifts for each, close, macd, signal, hist....
                s_timetoken = datetime.now(est)
                df = assign_MACD_Tier(df=df, mac_world=mac_world, tiers_num=macd_tiers)
                STORY_bee[ticker_time_frame]["story"]["current_macd_tier"] = df.iloc[-1]["macd_tier"]
                STORY_bee[ticker_time_frame]["story"]["current_hist_tier"] = df.iloc[-1]["hist_tier"]

                # df["mac_ranger"] = df["macd_tier"].apply(lambda x: power_ranger_mapping(x)) ## OLD
                df['mac_ranger'] = power_ranger_mapping_vectorized(df['macd_tier'])
                df['hist_ranger'] = power_ranger_mapping_vectorized(df['hist_tier'])
                df['vwap_ranger'] = power_ranger_mapping_vectorized(df['vwap_tier'])
                df['rsi_ranger'] = power_ranger_mapping_vectorized(df['rsi_ema_tier'])
                df['trinity_tier'] = round(round(((df['macd_tier'] + df['vwap_tier'] + df['rsi_ema_tier']) / 3), 2) / 8 * 100)

                e_timetoken = datetime.now(est)
                betty_bee[ticker_time_frame]["assign_Tier"] = e_timetoken - s_timetoken


                s_timetoken = datetime.now(est)
                # mac cross
                df = mark_macd_signal_cross(df=df)
                resp = knights_triggerbees(df=df)
                df = resp["df"]
                knights_word = resp["bee_triggers"]
                # how long does trigger stay profitable?
                e_timetoken = datetime.now(est)
                betty_bee[ticker_time_frame]["macdcross"] = e_timetoken - s_timetoken

                """for every index(timeframe) calculate profit length, bell curve conclude with how well trigger is doing to then determine when next trigger will do well """
                # MACD WAVE ~~~~~~~~~~~~~~~~~~~~~~~~ WAVES ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ MACD WAVE #
                # Queen to make understanding of trigger-profit waves
                # Q? measure pressure of a wave? if small waves, expect bigger wave>> up the buy

                s_timetoken = datetime.now(est)

                wave = return_knightbee_waves(
                    df=df, trigbees=trigbees, ticker_time_frame=ticker_time_frame
                )
                e_timetoken = datetime.now(est)
                betty_bee[ticker_time_frame]["waves_return_knightbee_waves"] = (
                    e_timetoken - s_timetoken
                )

                s_timetoken = datetime.now(est)
                MACDWAVE_story = return_macd_wave_story(
                    df=df,
                    trigbees=trigbees,
                    ticker_time_frame=ticker_time_frame,
                    tframe=tframe,
                )
                e_timetoken = datetime.now(est)
                betty_bee[ticker_time_frame]["waves_return_macd_wave_story"] = (
                    e_timetoken - s_timetoken
                )

                s_timetoken = datetime.now(est)
                resp = return_waves_measurements(df=df, trigbees=trigbees, ticker_time_frame=ticker_time_frame)
                e_timetoken = datetime.now(est)
                betty_bee[ticker_time_frame]["waves_return_waves_measurements"] = (e_timetoken - s_timetoken)

                df = resp["df"]
                MACDWAVE_story["story"] = resp["df_waves"]

                STORY_bee[ticker_time_frame]["waves"] = MACDWAVE_story

                e_timetoken = datetime.now(est)
                betty_bee[ticker_time_frame]["waves"] = e_timetoken - s_timetoken

                knights_sight_word[ticker_time_frame] = knights_word
                STORY_bee[ticker_time_frame]["KNIGHTSWORD"] = knights_word


                macd_state = df["macd_cross"].iloc[-1]
                macd_state_side = macd_state.split("_")[0]  # buy_cross-num
                middle_crossname = macd_state.split("_")[1].split("-")[0]
                state_count = macd_state.split("-")[1]  # buy/sell_name_number
                STORY_bee[ticker_time_frame]["story"]["macd_state"] = macd_state
                STORY_bee[ticker_time_frame]["story"]["macd_state_side"] = macd_state_side
                STORY_bee[ticker_time_frame]["story"]["time_since_macd_change"] = state_count


                # # # return degree angle 0, 45, 90
                # try:
                #     s_timetoken = datetime.now(est)
                #     var_list = ["macd", "hist", "signal", "close", "rsi_ema"]
                #     var_timeframes = [3, 6, 8, 10, 25, 33]
                #     for var in var_list:
                #         for t in var_timeframes:
                #             # apply rollowing angle
                #             if df_len >= t:
                #                 x = df.iloc[df_len - t : df_len][var].to_list()
                #                 y = [1, 2]
                #                 name = f'{var}{"-"}{"Degree"}{"--"}{str(t)}'
                #                 ANGEL_bee[ticker_time_frame][name] = return_degree_angle(x, y)
                #     e_timetoken = datetime.now().astimezone(est)
                #     betty_bee[ticker_time_frame]["Angel_Bee"] = e_timetoken - s_timetoken
                # except Exception as e:
                #     msg = (
                #         e,
                #         "--",
                #         print_line_of_error(),
                #         "--",
                #         ticker_time_frame,
                #         "--ANGEL_bee",
                #     )
                #     print(msg)

                # # add close price momentum
                # try:
                #     s_timetoken = datetime.now().astimezone(est)
                #     close = df['close']
                #     df['close_mom_3'] = talib.MOM(close, timeperiod=3).fillna(0)
                #     df['close_mom_6'] = talib.MOM(close, timeperiod=6).fillna(0)
                #     e_timetoken = datetime.now().astimezone(est)
                #     betty_bee[ticker_time_frame]['MOM'] = (e_timetoken - s_timetoken)
                # except Exception as e:
                #     msg=(e,"--", print_line_of_error(), "--", ticker_time_frame)
                #     logging.error(msg)

                time_state = df["timestamp_est"].iloc[-1]  # current time
                STORY_bee[ticker_time_frame]["story"][
                    "time_state"
                ] = datetime.now().astimezone(est)


                # last time there was buycross
                if "buy_cross-0" in knights_word.keys():
                    prior_macd_time = knights_word["buy_cross-0"]["last_seen"]
                    STORY_bee[ticker_time_frame]["story"][
                        f'{"last_seen_macd_buy_time"}'
                    ] = prior_macd_time
                    prior_macd_time = knights_word["buy_cross-0"]["prior_seen"]
                    STORY_bee[ticker_time_frame]["story"][
                        f'{"prior_seen_macd_buy_time"}'
                    ] = prior_macd_time
                # last time there was sellcross
                if "sell_cross-0" in knights_word.keys():
                    prior_macd_time = knights_word["sell_cross-0"]["last_seen"]
                    STORY_bee[ticker_time_frame]["story"][
                        f'{"last_seen_macd_sell_time"}'
                    ] = prior_macd_time
                    prior_macd_time = knights_word["sell_cross-0"]["prior_seen"]
                    STORY_bee[ticker_time_frame]["story"][
                        f'{"prior_seen_macd_sell_time"}'
                    ] = prior_macd_time

                # all triggers ? move to top?
                # STORY_bee[ticker_time_frame]['story']['alltriggers_current_state'] = [k for (k,v) in knights_word.items() if v['last_seen'].day == time_state.day and v['last_seen'].hour == time_state.hour and v['last_seen'].minute == time_state.minute]

                # count number of Macd Crosses
                # df['macd_cross_running_count'] = np.where((df['macd_cross'] == 'buy_cross-0') | (df['macd_cross'] == 'sell_cross-0'), 1, 0)
                s_timetoken = datetime.now().astimezone(est)
                today_df = df[
                    df["timestamp_est"]
                    > (datetime.now(est).replace(hour=1, minute=1, second=1)).astimezone(est)
                ].copy()
                # today_df = df[df['timestamp_est'] > (datetime.now().replace(hour=1, minute=1, second=1)).isoformat()].copy()
                STORY_bee[ticker_time_frame]["story"]["macd_cross_count"] = {
                    "buy_cross_total_running_count": sum(
                        np.where(df["macd_cross"] == "buy_cross-0", 1, 0)
                    ),
                    "sell_cross_totalrunning_count": sum(
                        np.where(df["macd_cross"] == "sell_cross-0", 1, 0)
                    ),
                    "buy_cross_todays_running_count": sum(
                        np.where(today_df["macd_cross"] == "buy_cross-0", 1, 0)
                    ),
                    "sell_cross_todays_running_count": sum(
                        np.where(today_df["macd_cross"] == "sell_cross-0", 1, 0)
                    ),
                }
                e_timetoken = datetime.now().astimezone(est)
                betty_bee[ticker_time_frame]["count_cross"] = e_timetoken - s_timetoken

                # latest_close_price
                STORY_bee[ticker_time_frame]["story"]["last_close_price"] = df.iloc[-1]["close"]

                try:
                    if "1Minute_1Day" in ticker_time_frame:
                        theme_df = df.copy()
                        theme_df = split_today_vs_prior(df=theme_df)  # remove prior day
                        theme_today_df = theme_df["df_today"]
                        theme_prior_df = theme_df['df_prior']

                        # we want...last vs currnet close prices, && Height+length of wave
                        yesterday_price = theme_prior_df.iloc[-1]['close']
                        current_price = theme_today_df.iloc[-1]["close"]
                        open_price = theme_today_df.iloc[0]["close"]  # change to timestamp lookup

                        STORY_bee[ticker_time_frame]["story"]["current_from_open"] = (
                            current_price - open_price
                        ) / open_price
                        STORY_bee[ticker_time_frame]["story"]["current_from_yesterday"] = (
                            current_price - yesterday_price
                        ) / yesterday_price

                        # SLOPE NEEDED HERE WORKERBEE?
                        # e_timetoken = datetime.now(est)
                        # slope, intercept, r_value, p_value, std_err = stats.linregress(
                        #     theme_today_df.index, theme_today_df["close"]
                        # )
                        # STORY_bee[ticker_time_frame]["story"]["current_slope"] = slope
                        # e_timetoken = datetime.now(est)
                        # betty_bee[ticker_time_frame]["slope"] = e_timetoken - s_timetoken

                except Exception as e:
                    print(f"PollenStory Error {ticker_time_frame} 1 Mintue {e}")
                    print_line_of_error()



                # how long have you been stuck at vwap ?

                # add to story
                df["chartdate"] = df["timestamp_est"]  # add as new col
                df["name"] = ticker_time_frame
                story[ticker_time_frame] = df
                # ticker, _time, _frame = ticker_time_frame.split("_")

                # latest Pull
                df_lastrow = df.iloc[-1]
                # df_lastrow_remaining = df_lastrow[[i for i in df_lastrow.index.tolist() if i not in STORY_bee[ticker_time_frame]['story'].keys()]].copy
                STORY_bee[ticker_time_frame]["story"]["current_mind"] = df_lastrow

                e_ttfame_func_check = datetime.now().astimezone(est)
                betty_bee[ticker_time_frame]["full_loop"] = (
                    e_ttfame_func_check - s_ttfame_func_check
                )

                # add momentem ( when macd < signal & past 3 macds are > X Value or %)

                # when did macd and signal share same tier?
            except Exception as e:
                print_line_of_error()
                print(e)
                print("PStoryEr", ticker_time_frame)
                return False


        s = datetime.now(est)
        async def main_func(session, ticker_time_frame, df_i):
            async with session:
                try:
                    return_dict = pollenstory_cycle(ticker_time_frame, df_i)
                    return {
                        'return_dict': return_dict
                    }  # return Charts Data based on Queen's Query Params, (stars())
                except Exception as e:
                    print("ps_error", e, ticker_time_frame)

        async def main(pollen_nectar):

            async with aiohttp.ClientSession() as session:
                return_list = []
                tasks = []
                for ticker_time_frame, df_i in pollen_nectar.items():
                    tasks.append(asyncio.ensure_future(main_func(session, ticker_time_frame, df_i)))
                original_pokemon = await asyncio.gather(*tasks)
                for pokemon in original_pokemon:
                    return_list.append(pokemon)
                return return_list

        return_list = asyncio.run(main(pollen_nectar))
        e = datetime.now(est)
        # (f"async pollenstory {df_tickers_data.keys()} --- {(e - s)} seconds ---")


        # for (ticker_time_frame, df_i) in (pollen_nectar.items()):  # CHARLIE_bee: # create ranges for MACD & RSI 4-3, 70-80, or USE Prior MAX&Low ...
        #     pollenstory_cycle(ticker_time_frame, df_i)


        e = datetime.now(est)
        # ("pollen_story", str((e - s)))
        
        
        return {
            "pollen_story": story,
            "conscience": {
                "ANGEL_bee": ANGEL_bee,
                "KNIGHTSWORD": knights_sight_word,
                "STORY_bee": STORY_bee,
            },
            "betty_bee": betty_bee,
        }
    
    except Exception as e:
        print_line_of_error("pollen_story error")
        return False


def knights_triggerbees(df):  # adds all triggers to dataframe
    # ticker_time_frame = df['name'].iloc[-1] #TEST
    # trigger_dict = {ticker_time_frame: {}}  #TEST

    def trig_89(df):
        trig = np.where(
            (df["macd_cross"].str.contains("buy_cross-0") == True), "bee", "nothing"
        )
        return trig

    def trig_98(df):
        trig = np.where(
            (df["macd_cross"].str.contains("sell_cross-0") == True), "bee", "nothing"
        )
        return trig

    def trig_pre_89(df):
        trig = np.where(
            (df["macd_cross"].str.contains("buy") == False)
            & (df["hist_slope-3"] > 5)
            & (df["macd_singal_deviation"] < -0.04)
            & (df["macd_singal_deviation"] > -0.06),
            "bee",
            "nothing",
        )
        return trig

    trigger_dict_info = {
        "buy_cross-0": trig_89,
        "sell_cross-0": trig_98,
        "ready_buy_cross": trig_pre_89,
    }

    trigger_dict = {}
    for trigger, trig_func in trigger_dict_info.items():
        trigger_dict[trigger] = {}
        df[trigger] = trig_func(df=df)
        bee_df = df[df[trigger] == "bee"].copy()
        if len(bee_df) > 0:
            trigger_dict[trigger]["last_seen"] = bee_df["timestamp_est"].iloc[-1]
            if len(bee_df) > 1:
                trigger_dict[trigger]["prior_seen"] = bee_df["timestamp_est"].iloc[-2]
            else:
                trigger_dict[trigger]["prior_seen"] = datetime.now(est).replace(
                    year=1989, month=4, day=11
                )
        else:
            trigger_dict[trigger]["last_seen"] = datetime.now(est).replace(
                year=1989, month=4, day=11
            )
            trigger_dict[trigger]["prior_seen"] = datetime.now(est).replace(
                year=1989, month=4, day=11
            )

    # # Mac is very LOW and we are in buy cross
    # trigger = 'buy_RED_tier-1_macdcross'
    # df[trigger] = np.where(
    #     (df['macd_cross'].str.contains("buy")==True) & # is not in BUY cycle
    #     ((df['macd'] < 0) & (df['macd'] > -.3))
    #     ,"bee", 'nothing')
    # bee_df = df[df[trigger] == 'bee'].copy()
    # if len(bee_df) > 0:
    #     trigger_dict[trigger] = {}
    #     trigger_dict[trigger]['last_seen'] = bee_df['timestamp_est'].iloc[-1]
    #     if len(bee_df) > 1:
    #         trigger_dict[trigger]['prior_seen'] = bee_df['timestamp_est'].iloc[-2]
    #     else:
    #         trigger_dict[trigger]['prior_seen'] = bee_df['timestamp_est'].iloc[-1]

    # trigger = 'buy_RED_tier-2_macdcross'
    # df[trigger] = np.where(
    #     (df['macd_cross'].str.contains("buy")==True) & # is not in BUY cycle
    #     ((df['macd'] < -.3) & (df['macd'] > -.5))
    #     ,"bee", 'nothing')
    # bee_df = df[df[trigger] == 'bee'].copy()
    # if len(bee_df) > 0:
    #     trigger_dict[trigger] = {}
    #     trigger_dict[trigger]['last_seen'] = bee_df['timestamp_est'].iloc[-1]
    #     if len(bee_df) > 1:
    #         trigger_dict[trigger]['prior_seen'] = bee_df['timestamp_est'].iloc[-2]
    #     else:
    #         trigger_dict[trigger]['prior_seen'] = bee_df['timestamp_est'].iloc[-1]

    # trigger = 'buy_RED_tier-3_macdcross'
    # df[trigger] = np.where(
    #     (df['macd_cross'].str.contains("buy")==True) & # is not in BUY cycle
    #     ((df['macd'] < -.5) & (df['macd'] > -.1))
    #     ,"bee", 'nothing')
    # bee_df = df[df[trigger] == 'bee'].copy()
    # if len(bee_df) > 0:
    #     trigger_dict[trigger] = {}
    #     trigger_dict[trigger]['last_seen'] = bee_df['timestamp_est'].iloc[-1]
    #     if len(bee_df) > 1:
    #         trigger_dict[trigger]['prior_seen'] = bee_df['timestamp_est'].iloc[-2]
    #     else:
    #         trigger_dict[trigger]['prior_seen'] = bee_df['timestamp_est'].iloc[-1]

    # trigger = 'buy_RED_tier-4_macdcross'
    # df[trigger] = np.where(
    #     (df['macd_cross'].str.contains("buy")==True) & # is not in BUY cycle
    #     ((df['macd'] < -.1) & (df['macd'] > -.15))
    #     ,"bee", 'nothing')
    # bee_df = df[df[trigger] == 'bee'].copy()
    # if len(bee_df) > 0:
    #     trigger_dict[trigger] = {}
    #     trigger_dict[trigger]['last_seen'] = bee_df['timestamp_est'].iloc[-1]
    #     if len(bee_df) > 1:
    #         trigger_dict[trigger]['prior_seen'] = bee_df['timestamp_est'].iloc[-2]
    #     else:
    #         trigger_dict[trigger]['prior_seen'] = bee_df['timestamp_est'].iloc[-1]

    # trigger = 'buy_RED_tier-5_macdcross'
    # df[trigger] = np.where(
    #     (df['macd_cross'].str.contains("buy")==True) & # is not in BUY cycle
    #     (df['macd'] < -.15)
    #     ,"bee", 'nothing')
    # bee_df = df[df[trigger] == 'bee'].copy()
    # if len(bee_df) > 0:
    #     trigger_dict[trigger] = {}
    #     trigger_dict[trigger]['last_seen'] = bee_df['timestamp_est'].iloc[-1]
    #     if len(bee_df) > 1:
    #         trigger_dict[trigger]['prior_seen'] = bee_df['timestamp_est'].iloc[-2]
    #     else:
    #         trigger_dict[trigger]['prior_seen'] = bee_df['timestamp_est'].iloc[-1]

    # # Mac is very LOW and we are in buy cross
    # trigger = 'buy_high-macdcross'
    # df[trigger] = np.where(
    #     (df['macd_cross'].str.contains("buy")==True) & # is not in BUY cycle
    #     (df['macd'] < -.1)
    #     ,"bee", 'nothing')
    # bee_df = df[df[trigger] == 'bee'].copy()
    # if len(bee_df) > 0:
    #     trigger_dict[trigger] = {}
    #     trigger_dict[trigger]['last_seen'] = bee_df['timestamp_est'].iloc[-1]
    #     if len(bee_df) > 1:
    #         trigger_dict[trigger]['prior_seen'] = bee_df['timestamp_est'].iloc[-2]
    #     else:
    #         trigger_dict[trigger]['prior_seen'] = bee_df['timestamp_est'].iloc[-1]

    # # Mac is very LOW and we are in buy cross
    # trigger = 'buy_high-macdcross'
    # df[trigger] = np.where(
    #     (df['macd_cross'].str.contains("buy")==True) & # is not in BUY cycle
    #     (df['macd'] < -.1)
    #     ,"bee", 'nothing')
    # bee_df = df[df[trigger] == 'bee'].copy()
    # if len(bee_df) > 0:
    #     trigger_dict[trigger] = {}
    #     trigger_dict[trigger]['last_seen'] = bee_df['timestamp_est'].iloc[-1]
    #     if len(bee_df) > 1:
    #         trigger_dict[trigger]['prior_seen'] = bee_df['timestamp_est'].iloc[-2]
    #     else:
    #         trigger_dict[trigger]['prior_seen'] = bee_df['timestamp_est'].iloc[-1]

    # # Mac is very High and we are in a Sell Cross
    # trigger = 'sell_high-macdcross'
    # df[trigger] = np.where(
    #     (df['macd_cross'].str.contains("sell")==True) &
    #     (df['macd'] > 1)
    #     ,"bee", 'nothing')
    # bee_df = df[df[trigger] == 'bee'].copy()
    # if len(bee_df) > 0:
    #     trigger_dict[trigger] = {}
    #     trigger_dict[trigger]['last_seen'] = bee_df['timestamp_est'].iloc[-1]
    #     if len(bee_df) > 1:
    #         trigger_dict[trigger]['prior_seen'] = bee_df['timestamp_est'].iloc[-2]
    #     else:
    #         trigger_dict[trigger]['prior_seen'] = bee_df['timestamp_est'].iloc[-1]

    # # Mac is very High and the prior hist slow was steep and we are not in a Sell CROSS Cycle Yet
    # trigger = 'sell_high-macdcross'
    # df[trigger] = np.where(
    #     (df['macd_cross'].str.contains("sell_hold")==False) & # is not in Sell cycle
    #     (df['macd'] > 1.5) &
    #     (df['macd_slope-3'] < .1) &
    #     ((df['hist_slope-3'] < .33) |(df['hist_slope-6'] < .10))
    #     ,"bee", 'nothing')
    # bee_df = df[df[trigger] == 'bee'].copy()
    # if len(bee_df) > 0:
    #     trigger_dict[trigger] = {}
    #     trigger_dict[trigger]['last_seen'] = bee_df['timestamp_est'].iloc[-1]
    #     if len(bee_df) > 1:
    #         trigger_dict[trigger]['prior_seen'] = bee_df['timestamp_est'].iloc[-2]
    #     else:
    #         trigger_dict[trigger]['prior_seen'] = bee_df['timestamp_est'].iloc[-1]

    return {"df": df, "bee_triggers": trigger_dict}


def mark_macd_signal_cross(df):  # return df: Mark the signal macd crosses
    # running totals
    try:
        m = df["macd"].to_list()
        s = df["signal"].to_list()
        prior_cross = None
        cross_list = []
        c = 0  # count which side of trade you are on (c brings deveations from prior cross)
        buy_c = 0
        sell_c = 0
        # last_buycross_index = 0
        # last_sellcross_index = 0
        # wave_mark_list = []
        for i, macdvalue in enumerate(m):
            if i != 0:
                prior_mac = m[i - 1]
                prior_signal = s[i - 1]
                now_mac = macdvalue
                now_signal = s[i]
                if now_mac > now_signal and prior_mac <= prior_signal:
                    cross_list.append(f'{"buy_cross"}{"-"}{0}')
                    c = 0
                    prior_cross = "buy"
                    buy_c += 1
                    # last_buycross_index = i
                    # wave_mark_list.append(last_buycross_index)
                elif now_mac < now_signal and prior_mac >= prior_signal:
                    cross_list.append(f'{"sell_cross"}{"-"}{0}')
                    c = 0
                    prior_cross = "sell"
                    sell_c += 1
                    # last_sellcross_index = i
                    # wave_mark_list.append(last_sellcross_index)

                else:
                    if prior_cross:
                        if prior_cross == "buy":
                            c += 1
                            cross_list.append(f'{"buy_hold"}{"-"}{c}')
                            # wave_mark_list.append(0)
                        else:
                            c += 1
                            cross_list.append(f'{"sell_hold"}{"-"}{c}')
                            # wave_mark_list.append(0)
                    else:
                        cross_list.append(f'{"init_hold"}{"-"}{0}')
                        # wave_mark_list.append(0)
            else:
                cross_list.append(f'{"init_hold"}{"-"}{0}')
                # wave_mark_list.append(0)
        df2 = pd.DataFrame(cross_list, columns=["macd_cross"])
        # df3 = pd.DataFrame(wave_mark_list, columns=['macd_cross_wavedistance'])
        df_new = pd.concat([df, df2], axis=1)
        return df_new
    except Exception as e:
        msg = (e, "--", print_line_of_error(), "--", "macd_cross")
        logging.critical(msg)


def return_knightbee_waves(df, trigbees, ticker_time_frame):  # adds profit wave based on trigger
    # df = POLLENSTORY['SPY_1Minute_1Day'] # test
    wave = {ticker_time_frame: {"ticker_time_frame": ticker_time_frame}}
    for knight_trigger in trigbees:
        trig_name = knight_trigger  # "buy_cross-0" # test
        wave[ticker_time_frame][trig_name] = {}
        trigger_bee = df[trig_name].tolist()
        close = df["close"].tolist()
        track_bees = {}
        track_bees_profits = {}
        trig_bee_count = 0
        for idx, trig_bee in enumerate(trigger_bee):
            beename = f"{trig_bee_count}"
            if idx == 0:
                continue
            if trig_bee == "bee":

                close_price = close[idx]
                track_bees[beename] = close_price
                # reset only if bee not continous
                if trigger_bee[idx - 1] != "bee":
                    trig_bee_count += 1
                
                beename = f"{trig_bee_count}"
                # (beename, " ", idx)
                if beename in track_bees_profits.keys():
                    track_bees_profits[beename].update({idx: 0})
                else:
                    track_bees_profits[beename] = {idx: 0}
                continue
            if trig_bee_count > 0:
                # beename = f'{trig_name}{trig_bee_count}'
                origin_trig_price = track_bees[str(int(beename) - 1)]
                latest_price = close[idx]
                profit_loss = (latest_price - origin_trig_price) / latest_price

                if ("sell_cross-0" in knight_trigger):  # all triggers with short reverse number to reflect profit
                    profit_loss = profit_loss * -1

                if beename in track_bees_profits.keys():
                    track_bees_profits[beename].update({idx: profit_loss})
                else:
                    track_bees_profits[beename] = {idx: profit_loss}

        wave[ticker_time_frame][trig_name] = track_bees_profits
        # wave[ticker_time_frame]["buy_cross-0"].keys()
        # bees_wave = wave['AAPL_1Minute_1Day']["buy_cross-0"]
        index_perwave = {}
        for k, v in track_bees_profits.items():
            for kn, vn in v.items():
                index_perwave[kn] = k
        index_wave_dict = [v for (k, v) in track_bees_profits.items()]
        index_wave_series = {}
        for di in index_wave_dict:
            for k, v in di.items():
                index_wave_series[k] = v
        df[f'{trig_name}{"__wave"}'] = (
            df["story_index"].map(index_wave_series).fillna("0")
        )
        df[f'{trig_name}{"__wave_number"}'] = (
            df["story_index"].map(index_perwave).fillna("0")
        )
        # bees_wave_df = df[df['story_index'].isin(bees_wave_list)].copy()
        # tag greatest profit
    return wave


def split_today_vs_prior(df, timestamp="timestamp_est"):
    try:
        last_date = df[timestamp].iloc[-1].replace(hour=1, minute=1, second=1)
        df_today = df[df[timestamp] > (last_date).astimezone(est)].copy()
        df_prior = df[~(df[timestamp].isin(df_today[timestamp].to_list()))].copy()
    except Exception as e:
        print("QH error", e, print_line_of_error())
    
    return {"df_today": df_today, "df_prior": df_prior}


def convert_to_float(x):
    try:
        return float(x)
    except:
        return 0


def return_degree_angle(x, y):  #
    # 45 degree angle
    # x = [1, 2, 3]
    # y = [1,2]

    # calculate
    e = np.math.atan2(y[-1] - y[0], x[-1] - x[0])
    degree = np.degrees(e)

    return degree

def chunk(it, size):
    it = iter(it)
    return iter(lambda: tuple(islice(it, size)), ())

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
                start_date = (
                    trading_days_df.query("date < @current_day").tail(ndays).head(1).date
                )

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
        symbol_data["timestamp_est"] = symbol_data["timestamp_est"].apply(
            lambda x: x.astimezone(est)
        )
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
        # (str((e - s)) + ": " + datetime.now().strftime('%Y-%m-%d %H:%M'))

        return {
            "resp": True,
            "df": symbol_data,
            "market_hours_data": market_hours_data,
            "after_hours_data": after_hours_data,
        }
    # handle error
    except Exception as e:
        print("sending email of error", e)
        er_line = print_line_of_error()
        logging_log_message(
            log_type="critical",
            msg="bars failed",
            error=f"error {e}  error line {str(er_line)}",
        )


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
                def chunk_getbars_ticker_list(chunk_list, max_n=2,):
                    # print(chunk_list)
                    num_rr = len(chunk_list) + 1 # + 1 is for chunking so slice ends at last 
                    chunk_num = max_n if num_rr > max_n else num_rr
                    
                    # if num_rr > chunk_num:
                    chunks = list(chunk(range(num_rr), chunk_num))
                    # print(chunks)
                    for i in chunks:
                        if i[0] == 0:
                            slice1 = i[0]
                            slice2 = i[-1] # [0 : 49]
                        else:
                            slice1 = i[0] - 1
                            slice2 = i[-1] # [49 : 87]
                        print("chunk slice", (slice1, slice2))
                        chunk_n = chunk_list[slice1:slice2]
                        print("c", chunk_n)
                        # print(ticker_list)
                        # try:
                        #     symbol_data = api.get_bars(
                        #         chunk_n,
                        #         timeframe=timeframe,
                        #         start=start_date,
                        #         end=end_date,
                        #         adjustment="all",
                        #     ).df
                        #     # print(type(symbol_data))
                        #     # if symbol_data == None:
                        #     #     print("QH_None_getbars")
                        #     #     error_dict[ticker_list] = {"msg": "no data returned", "time": time}
                        #     #     return False
                            
                        #     if len(symbol_data) == 0:
                        #         error_dict[ticker_list] = {"msg": "no data returned", "time": time}
                        #         return False
                        #     # set index to EST time
                        #     symbol_data["timestamp_est"] = symbol_data.index
                        #     symbol_data["timestamp_est"] = symbol_data["timestamp_est"].apply(
                        #         lambda x: x.astimezone(est)
                        #     )
                        #     symbol_data["timeframe"] = timeframe
                        #     symbol_data["bars"] = "bars_list"

                        #     symbol_data = symbol_data.reset_index(drop=True)
                        #     # if ndays == 1:
                        #     #     symbol_data = symbol_data[symbol_data['timestamp_est'] > (datetime.now(est).replace(hour=1, minute=1, second=1))].copy()

                        #     return_dict[charttime] = symbol_data  
                        # except Exception as e:
                        #     print("QH_getbars", print_line_of_error(), e)

                    return True

                # chunk_getbars_ticker_list(chunk_list=ticker_list)
                try:
                    symbol_data = api.get_bars(
                        ticker_list,
                        timeframe=timeframe,
                        start=start_date,
                        end=end_date,
                        adjustment="all",
                    ).df
                    
                    if len(symbol_data) == 0:
                        error_dict[ticker_list] = {"msg": "no data returned", "time": time}
                        return False
                    # set index to EST time
                    symbol_data["timestamp_est"] = symbol_data.index
                    symbol_data["timestamp_est"] = symbol_data["timestamp_est"].apply(
                        lambda x: x.astimezone(est)
                    )
                    symbol_data["timeframe"] = timeframe
                    symbol_data["bars"] = "bars_list"

                    symbol_data = symbol_data.reset_index(drop=True)

                    return_dict[charttime] = symbol_data  
                except Exception as e:
                    print("QH_getbars", print_line_of_error(), e)
                    print(ticker_list)
        e = datetime.now(est)

        return {"resp": True, "return": return_dict, 'error_dict': error_dict}

    except Exception as e:
        print("sending email of error", e)
        er_line = print_line_of_error()
        logging_log_message(
            log_type="critical",
            msg="bars failed",
            error=f"error {e}  error line {str(er_line)}",
        )


def get_best_limit_price(ask, bid):
    if ask is None or bid is None:
        return {"maker_middle": None, "maker_delta": None}
    
    maker_dif = ask - bid
    maker_delta = (maker_dif / ask) * 100
    # check to ensure bid / ask not far
    maker_middle = round(ask - (maker_dif / 2), 2)

    return {"maker_middle": maker_middle, "maker_delta": maker_delta}


def return_snap_priceinfo(api, ticker, crypto, exclude_conditions, coin_exchange):
    ## update to query ticker by last 30 seconds if snapshot not available
    if crypto:
        snap = api.get_crypto_snapshot(ticker, exchange=coin_exchange)
    else:
        snap = api.get_snapshot(ticker)
        conditions = snap.latest_quote.conditions
        c = 0
        while True:
            # print(conditions)
            valid = [j for j in conditions if j in exclude_conditions]
            if len(valid) == 0 or c > 10:
                break
            else:
                snap = api.get_snapshot(ticker)  # return_last_quote from snapshot
                c += 1

    # current_price = STORY_bee[f'{ticker}{"_1Minute_1Day"}']['last_close_price']
    current_price = snap.latest_trade.price
    current_ask = snap.latest_quote.ask_price
    current_bid = snap.latest_quote.bid_price

    # best limit price
    best_limit_price = get_best_limit_price(ask=current_ask, bid=current_bid)
    maker_middle = best_limit_price["maker_middle"]
    ask_bid_variance = current_bid / current_ask

    priceinfo = {
        "snapshot": snap,
        "price": current_price,
        "bid": current_bid,
        "ask": current_ask,
        "maker_middle": maker_middle,
        "ask_bid_variance": ask_bid_variance,
    }

    return priceinfo


def rebuild_timeframe_bars(
    api, ticker_list, build_current_minute=False, min_input=False, sec_input=False
):
    # ticker_list = ['IBM', 'AAPL', 'GOOG', 'TSLA', 'MSFT', 'FB']
    try:
        # First get the current time
        if build_current_minute:
            current_time = datetime.now(est)
            current_sec = current_time.second
            if current_sec < 5:
                time.sleep(1)
                current_time = datetime.now(est)
                sec_input = current_time.second
                min_input = 0
        else:
            sec_input = sec_input
            min_input = min_input

        current_time = datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        previous_time = (
            datetime.now(datetime.timezone.utc)
            - datetime.timedelta(minutes=min_input, seconds=sec_input)
        ).strftime("%Y-%m-%dT%H:%M:%SZ")

        def has_condition(condition_list, condition_check):
            if type(condition_list) is not list:
                # Assume none is a regular trade?
                in_list = False
            else:
                # There are one or more conditions in the list
                in_list = any(
                    condition in condition_list for condition in condition_check
                )

            return in_list

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
        # Fetch trades for the X seconds before the current time
        trades_df = api.get_trades(
            ticker_list, start=previous_time, end=current_time, limit=30000
        ).df
        # convert to market time for easier reading
        trades_df = trades_df.tz_convert("America/New_York")

        # add a column to easily identify the trades to exclude using our function from above
        trades_df["exclude"] = trades_df.conditions.apply(
            has_condition, condition_check=exclude_conditions
        )

        # filter to only look at trades which aren't excluded
        valid_trades = trades_df.query("not exclude")
        # print(len(trades_df), len(valid_trades))
        # x=trades_df['conditions'].to_list()
        # y=[str(i) for i in x]
        # print(set(y))
        if build_current_minute:
            minbars_dict = {}
            for ticker in ticker_list:
                df = valid_trades[valid_trades["symbol"] == ticker].copy()
                # Resample the trades to calculate the OHLCV bars
                agg_functions = {
                    "price": ["first", "max", "min", "last"],
                    "size": ["sum", "count"],
                }
                min_bars = df.resample("1T").agg(agg_functions)
                min_bars = min_bars.droplevel(0, "columns")
                min_bars.columns = [
                    "open",
                    "high",
                    "low",
                    "close",
                    "volume",
                    "trade_count",
                ]
                min_bars = min_bars.reset_index()
                min_bars = min_bars.rename(columns={"timestamp": "timestamp_est"})
                minbars_dict[ticker] = min_bars
                return {"resp": minbars_dict}
        else:
            return {"resp": valid_trades}
    except Exception as e:
        print("rebuild timeframe bars", e)
        return {"resp": False, "msg": [e, current_time, previous_time]}


def return__snapshot__latest_PriceInfo(
    api, ticker_list=["SPY"], crypto=False, coin_exchange=False, min_input=0, sec_input=60
):
    def has_condition(condition_list, condition_check):
        if type(condition_list) is not list:
            # Assume none is a regular trade?
            in_list = False
        else:
            # There are one or more conditions in the list
            in_list = any(condition in condition_list for condition in condition_check)

        return in_list

    try:
        # api = return_alpaca_api_keys(prod=False)['api']
        # ticker_list = ['IBM', 'AAPL', 'GOOG', 'TSLA', 'MSFT', 'FB']
        # sec_input = 30
        # min_input = 0

        current_time = datetime.now(utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        previous_time = (datetime.now(utc) - timedelta(minutes=min_input, seconds=sec_input)).strftime("%Y-%m-%dT%H:%M:%SZ")

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
        # Fetch trades for the X seconds before the current time
        trades_df = api.get_trades(
            ticker_list, start=previous_time, end=current_time, limit=30000
        ).df

        # check if empty to call further away

        # convert to market time for easier reading
        trades_df = trades_df.tz_convert("America/New_York")

        # add a column to easily identify the trades to exclude using our function from above
        trades_df["exclude"] = trades_df.conditions.apply(
            has_condition, condition_check=exclude_conditions
        )

        # filter to only look at trades which aren't excluded
        valid_trades = trades_df.query("not exclude")

    except Exception as e:
        print(e)

        return True


### Orders ###
def return_alpc_portolio(api):
    all_positions = api.list_positions()
    portfolio = {i.symbol: vars(i)["_raw"] for i in all_positions}
    return {"portfolio": portfolio}


def check_order_status(api, client_order_id):  # return raw dict form
    try:
        order = api.get_order_by_client_order_id(client_order_id=client_order_id)
        order_ = vars(order)["_raw"]
        return order_
    except Exception as e:
        print(f"qplcacae {client_order_id} error {e}")
        return {}


def submit_best_limit_order(api, symbol, qty, side, client_order_id=False):
    # side = 'buy'
    # qty = '1'
    # symbol = 'BABA'
    # if api == 'paper':
    #     api = api_paper
    # else:
    #     api = api

    snapshot = api.get_snapshot(symbol)  # return_last_quote from snapshot
    conditions = snapshot.latest_quote.conditions
    c = 0
    while True:
        print(conditions)
        valid = [j for j in conditions if j in exclude_conditions]
        if len(valid) == 0 or c > 10:
            break
        else:
            snapshot = api.get_snapshot(symbol)  # return_last_quote from snapshot
            c += 1

            # print(snapshot)
    last_trade = snapshot.latest_trade.price
    ask = snapshot.latest_quote.ask_price
    bid = snapshot.latest_quote.bid_price
    maker_dif = ask - bid
    maker_delta = (maker_dif / ask) * 100
    # check to ensure bid / ask not far
    set_price = round(ask - (maker_dif / 2), 2)

    if client_order_id:
        order = api.submit_order(
            symbol=symbol,
            qty=qty,
            side=side,  # buy, sell
            time_in_force="gtc",  # 'day'
            type="limit",  # 'market'
            limit_price=set_price,
            client_order_id=client_order_id,
        )  # optional make sure it unique though to call later!

    else:
        order = api.submit_order(
            symbol=symbol,
            qty=qty,
            side=side,  # buy, sell
            time_in_force="gtc",  # 'day'
            type="limit",  # 'market'
            limit_price=set_price,
        )
        # client_order_id='test1') # optional make sure it unique though to call later!
    return order


# order = submit_best_limit_order(symbol='BABA', qty=1, side='buy', client_order_id=False)


def order_filled_completely(api, client_order_id):
    order_status = api.get_order_by_client_order_id(client_order_id=client_order_id)
    filled_qty = order_status.filled_qty
    order_status.status
    order_status.filled_avg_price
    while True:
        if order_status.status == "filled":
            print("order fully filled")
            break
    return True


def submit_order(
    api,
    symbol,
    qty,
    side,
    type,
    limit_price=False,
    client_order_id=False,
    time_in_force="gtc",
    order_class=False,
    stop_loss=False,
    take_profit=False,):


    try:
        if type == "market":
            order = api.submit_order(
                symbol=symbol,
                qty=qty,
                side=side,
                type=type,
                time_in_force=time_in_force,
                client_order_id=client_order_id,
            )
        elif type == "limit":
            order = api.submit_order(
                symbol=symbol,
                qty=qty,
                side=side,
                type=type,
                time_in_force=time_in_force,
                client_order_id=client_order_id,
                limit_price=limit_price,
            )
        else:
            return {'error': 'wtf'}

        return {'order': order}
    except Exception as e:
        print_line_of_error(e)
        print(side, symbol, qty, type, limit_price, time_in_force, client_order_id)
        return {'error': e}

    """stop loss order"""
    # api.submit_order(symbol='TSLA',
    #         qty=1,
    #         side='buy',
    #         time_in_force='gtc', 'day'
    #         type='limit',
    #         limit_price=400.00,
    #         client_order_id=001,
    #         order_class='bracket',
    #         stop_loss=dict(stop_price='360.00'),
    #         take_profit=dict(limit_price='440.00'))


def refresh_account_info(api):
    """
    # Account({   
    'account_blocked': False, 
    'account_number': '603397580', 
    'accrued_fees': '0', 
    'buying_power': '80010',
    'cash': '40005', 
    'created_at': '2022-01-23T22:11:15.978765Z', 
    'crypto_status': 'PAPER_ONLY', 
    'currency': 'USD', 
    'daytrade_count': 0,
    'daytrading_buying_power': '0', 
    'equity': '40005', 
    'id': '2fae9699-b24f-4d06-80ec-d531b61e9458', 
    'initial_margin': '0',
    'last_equity': '40005',
    'last_maintenance_margin': '0',
    'long_market_value': '0',
    'maintenance_margin': '0',
    'multiplier': '2',
    'non_marginable_buying_power': '40005',
    'pattern_day_trader': False,
    'pending_transfer_in': '40000',
    'portfolio_value': '40005',
    'regt_buying_power': '80010',
    'short_market_value': '0',
    'shorting_enabled': True,
    'sma': '40005',
    'status': 'ACTIVE',
    'trade_suspended_by_user': False,
    'trading_blocked': False, 'transfers_blocked': False})
    """
    info = api.get_account()
    info_ = {
        "info": info,
        "info_converted": {
            "accrued_fees": float(info.accrued_fees),
            "buying_power": float(info.buying_power),
            "cash": float(info.cash),
            "daytrade_count": float(info.daytrade_count),
            "last_equity": float(info.last_equity),
            "portfolio_value": float(info.portfolio_value),
            "daytrading_buying_power": float(info.daytrading_buying_power)
        },
    }
    # info_ = {k: v for (k,v) in (vars(info).get('_raw').keys()) if k not in info_}
    return info_


def init_index_ticker(index_list, db_root, init=True):
    # index_list = [
    #     'DJA', 'DJI', 'DJT', 'DJUSCL', 'DJU',
    #     'NDX', 'IXIC', 'IXCO', 'INDS', 'INSR', 'OFIN', 'IXTC', 'TRAN', 'XMI',
    #     'XAU', 'HGX', 'OSX', 'SOX', 'UTY',
    #     'OEX', 'MID', 'SPX',
    #     'SCOND', 'SCONS', 'SPN', 'SPF', 'SHLTH', 'SINDU', 'SINFT', 'SMATR', 'SREAS', 'SUTIL']
    api_key = "b2c87662-0dce-446c-862b-d64f25e93285"
    ss = StockSymbol(api_key)

    "Create DB folder if needed"
    index_ticker_db = os.path.join(db_root, "index_tickers")
    if os.path.exists(index_ticker_db) == False:
        os.mkdir(index_ticker_db)
        print("Ticker Index db Initiated")

    if init:
        us = ss.get_symbol_list(market="US")
        df = pd.DataFrame(us)
        df.to_csv(os.path.join(index_ticker_db, "US.csv"), index=False, encoding="utf8")

        for tic_index in index_list:
            try:
                index = ss.get_symbol_list(index=tic_index)
                df = pd.DataFrame(index)
                df.to_csv(
                    os.path.join(index_ticker_db, tic_index + ".csv"),
                    index=False,
                    encoding="utf8",
                )
            except Exception as e:
                print(tic_index, e, datetime.now(est))

    # examples:
    # symbol_list_us = ss.get_symbol_list(market="US")
    # symbol_only_list = ss.get_symbol_list(market="malaysia", symbols_only=True)
    # # https://stock-symbol.herokuapp.com/market_index_list
    # symbol_list_dow = ss.get_symbol_list(index="DJI")

    # symbol_list_dow = ss.get_symbol_list(index="SPX")
    # ndx = ss.get_symbol_list(index="NDX")
    # ndx_df = pd.DataFrame(ndx)

    # Dow Jones Composite Average (DJA)
    # Dow Jones Industrial Average (DJI)
    # Dow Jones Transportation Average (DJT)
    # Dow Jones U.S. Coal (DJUSCL)
    # Dow Jones Utility Average (DJU)
    # NASDAQ 100 (NDX)
    # NASDAQ COMPOSITE (IXIC)
    # NASDAQ COMPUTER (IXCO)
    # NASDAQ INDUSTRIAL (INDS)
    # NASDAQ INSURANCE (INSR)
    # NASDAQ OTHER FINANCE (OFIN)
    # NASDAQ TELECOMMUNICATIONS (IXTC)
    # NASDAQ TRANSPORTATION (TRAN)
    # NYSE ARCA MAJOR MARKET (XMI)
    # PHLX GOLD AND SILVER SECTOR INDEX (XAU)
    # PHLX HOUSING SECTOR (HGX)
    # PHLX OIL SERVICE SECTOR (OSX)
    # PHLX SEMICONDUCTOR (SOX)
    # PHLX UTILITY SECTOR (UTY)
    # S&P 100 (OEX)
    # S&P 400 (MID)
    # S&P 500 (SPX)
    # S&P 500 Communication Services (S5TELS)
    # S&P 500 Consumer Discretionary (S5COND)
    # S&P 500 Consumer Staples (S5CONS)
    # S&P 500 Energy (SPN)
    # S&P 500 Financials (SPF)
    # S&P 500 Health Care (S5HLTH)
    # S&P 500 Industrials (S5INDU)
    # S&P 500 Information Technology (S5INFT)
    # S&P 500 Materials (S5MATR)
    # S&P 500 Real Estate (S5REAS)
    # S&P 500 Utilities (S5UTIL)"""
    return True


def timestamp_string(format="%m-%d-%Y %I.%M%p", tz=est):
    return datetime.now(tz).strftime(format)


def return_timestamp_string(format="%Y-%m-%d %H-%M-%S %p {}".format(est), tz=est):
    return datetime.now(tz).strftime(format)


def print_line_of_error(e=False, me=False):
    exc_type, exc_obj, exc_tb = sys.exc_info()
    print(e, exc_type, exc_tb.tb_lineno)
    if me:
        print("me trace", me)
    return True
    # return exc_type, exc_tb.tb_lineno


def return_index_tickers(index_dir, ext):
    s = datetime.now(est)
    # ext = '.csv'
    # index_dir = os.path.join(db_root, 'index_tickers')

    index_dict = {}
    full_ticker_list = []
    all_indexs = [i.split(".")[0] for i in os.listdir(index_dir)]
    for i in all_indexs:
        try:
            df = pd.read_csv(
                os.path.join(index_dir, i + ext), dtype=str, encoding="utf8", engine="python"
            )
            df = df.fillna("")
            tics = df["symbol"].tolist()
            for j in tics:
                full_ticker_list.append(j)
            index_dict[i] = df
        except Exception as e:
            print(f'read file error {e} {i}')

    return [index_dict, list(set(full_ticker_list))]


###### >>>>>>>>>>>>>>>> CASTLE BISHOP FUNCTIONS <<<<<<<<<<<<<<<#########
#####                                                            #######
"""TICKER Calculation Functions"""


def return_macd(df_main, fast, slow, smooth):
    price = df_main["close"]
    exp1 = price.ewm(span=fast, adjust=False).mean()
    exp2 = price.ewm(span=slow, adjust=False).mean()
    macd = pd.DataFrame(exp1 - exp2).rename(columns={"close": "macd"})
    signal = pd.DataFrame(macd.ewm(span=smooth, adjust=False).mean()).rename(
        columns={"macd": "signal"}
    )
    hist = pd.DataFrame(macd["macd"] - signal["signal"]).rename(columns={0: "hist"})
    frames = [macd, signal, hist]
    df = pd.concat(frames, join="inner", axis=1)
    df_main = pd.concat([df_main, df], join="inner", axis=1)
    return df_main


def return_VWAP(df):
    if df.iloc[0]["timeframe"] == "1Min":
        d_token = split_today_vs_prior(df=df)
        df_today = d_token["df_today"]
        df_prior = d_token["df_prior"]


        df_split = []
        for df__ in [df_prior, df_today]:
            df__["typical_price"] = (
                df__.high + df__.low + df__.close
            ) / 3  # 1 Calculate the Typical Price for the period. (High + Low + Close)/3)
            df__["price_volume"] = (
                df__.typical_price * df__.volume
            )  # 2 Multiply the Typical Price by the period Volume. (Typical Price x Volume)
            df__[
                "cum_price_volume"
            ] = (
                df__.expanding().price_volume.sum()
            )  # 3 Create a Cumulative Total of Typical Price. Cumulative(Typical Price x Volume)
            df__[
                "cum_volume"
            ] = (
                df__.expanding().volume.sum()
            )  # 4 Create a Cumulative Total of Volume. Cumulative(Volume)
            df__["vwap"] = (
                df__.cum_price_volume / df__.cum_volume
            )  # 5 Divide the Cumulative Totals. VWAP = Cumulative(Typical Price x Volume) / Cumulative(Volume)

            del df__["typical_price"]
            del df__["cum_price_volume"]
            del df__["cum_volume"]
            df_split.append(df__)

        vwap_df = pd.concat(df_split, axis=0, join="outer")
    else:
        vwap_df = df
        # 1 Calculate the Typical Price for the period. (High + Low + Close)/3)
        vwap_df["typical_price"] = (vwap_df.high + vwap_df.low + vwap_df.close) / 3
        # 2 Multiply the Typical Price by the period Volume. (Typical Price x Volume)
        vwap_df["price_volume"] = vwap_df.typical_price * vwap_df.volume
        # 3 Create a Cumulative Total of Typical Price. Cumulative(Typical Price x Volume)
        vwap_df["cum_price_volume"] = vwap_df.expanding().price_volume.sum()
        # 4 Create a Cumulative Total of Volume. Cumulative(Volume)
        vwap_df["cum_volume"] = vwap_df.expanding().volume.sum()
        # 5 Divide the Cumulative Totals. VWAP = Cumulative(Typical Price x Volume) / Cumulative(Volume)
        vwap_df["vwap"] = vwap_df.cum_price_volume / vwap_df.cum_volume

        del vwap_df["typical_price"]
        del vwap_df["cum_price_volume"]
        del vwap_df["cum_volume"]

    return vwap_df


def return_RSI(df, length):
    # Define function to calculate the RSI
    # length = 14 # test
    # df = df.reset_index(drop=True)
    close = df["close"]

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
        rsi.name = "rsi"

        # Assert range
        valid_rsi = rsi.iloc[length - 1 :]
        assert ((0 <= valid_rsi) & (valid_rsi <= 100)).all()
        # Note: rsi[:length - 1] is excluded from above assertion because it is NaN for SMA.
        return rsi

    # Calculate RSI using MA of choice
    # Reminder: Provide ≥ 1 + length extra data points!
    rsi_ema = calc_rsi(close, lambda s: s.ewm(span=length).mean())
    rsi_ema.name = "rsi_ema"
    df = pd.concat((df, rsi_ema), axis=1).fillna(0)

    rsi_sma = calc_rsi(close, lambda s: s.rolling(length).mean())
    rsi_sma.name = "rsi_sma"
    df = pd.concat((df, rsi_sma), axis=1).fillna(0)

    rsi_rma = calc_rsi(
        close, lambda s: s.ewm(alpha=1 / length).mean()
    )  # Approximates TradingView.
    rsi_rma.name = "rsi_rma"
    df = pd.concat((df, rsi_rma), axis=1).fillna(0)

    return df


def return_sma_slope(df, y_list, time_measure_list):
    # df=pollenstory['SPY_1Minute_1Day'].copy()
    # time_measure_list = [3, 23, 33]
    # y_list = ['close', 'macd', 'hist']
    for mtime in time_measure_list:
        for el in y_list:
            sma_name = f'{el}{"_sma-"}{mtime}'
            slope_name = f'{el}{"_slope-"}{mtime}'
            df[sma_name] = df[el].rolling(mtime).mean().fillna(1)
            df[slope_name] = np.degrees(np.arctan(df[sma_name].diff() / mtime))
    return df


# ###### >>>>>>>>>>>>>>>> QUEEN <<<<<<<<<<<<<<<#########


def return_dfshaped_orders(running_orders, portfolio_name="Jq"):
    running_orders_df = pd.DataFrame(running_orders)
    if len(running_orders_df) > 0:
        running_orders_df["filled_qty"] = running_orders_df["filled_qty"].apply(
            lambda x: float(x)
        )
        running_orders_df["req_qty"] = running_orders_df["req_qty"].apply(
            lambda x: float(x)
        )
        running_orders_df = running_orders_df[
            running_orders_df["portfolio_name"] == portfolio_name
        ].copy()
        running_portfolio = (
            running_orders_df.groupby("symbol")[["filled_qty", "req_qty"]]
            .sum()
            .reset_index()
        )
    else:
        running_portfolio = []  # empty

    return running_portfolio


def createParser():
    parser = argparse.ArgumentParser()
    parser.add_argument("-qcp", default="queen")
    parser.add_argument("-prod", default="false")
    return parser


def return_market_hours(trading_days, crypto=False):
    # trading_days = api_cal # api.get_calendar()
    trading_days_df = pd.DataFrame([day._raw for day in trading_days])
    s = datetime.now(est)
    s_iso = s.isoformat()[:10]
    mk_open_today = s_iso in trading_days_df["date"].tolist()
    mk_open = s.replace(hour=9, minute=30, second=1)
    mk_close = s.replace(hour=16, minute=0, second=0)

    if crypto:
        return "open"

    if mk_open_today:
        if s >= mk_open and s <= mk_close:
            return "open"
        else:
            return "closed"
    else:
        return "closed"


def discard_allprior_days(df):
    df_day = df["timestamp_est"].iloc[-1]
    df = df.copy()
    df = df.set_index("timestamp_est", drop=True)  # test
    # df = df[(df.index.day == df_day.day) & (df.index.year == df_day.year) & (df.index.month == df_day.month)].copy() # remove yesterday
    df = df[(df.index.day == df_day.day)].copy()
    df = df.reset_index()
    return df


def slice_by_time(df, between_a, between_b):
    df = df.copy()
    df = df.set_index("timestamp_est", drop=True)  # test
    # df = df.between_time('9:30', '12:00') #test
    df = df.between_time(between_a, between_b)
    df = df.reset_index()
    return df


def init_app(pickle_file):
    if os.path.exists(pickle_file) == False:
        if "_App_" in pickle_file:
            print("init app")
            data = init_QUEEN_KING()
            PickleData(pickle_file=pickle_file, data_to_store=data)
        if "_Orders_" in pickle_file:
            print("init Orders")
            data = {"orders_completed": [], "archived": []}
            PickleData(pickle_file=pickle_file, data_to_store=data)


def stars(chart_times=False, desc="frame_period: period count -- 1Minute_1Day"):
    if chart_times:
        return chart_times
    else:
        chart_times = {
            "1Minute_1Day": 1,
            "5Minute_5Day": 5,
            "30Minute_1Month": 18,
            "1Hour_3Month": 48,
            "2Hour_6Month": 72,
            "1Day_1Year": 250,
        }
        return chart_times


def trigger_bees():
    return {
        'buy_cross-0': {},
        'sell_cross': {},
        'ready_buy_cross': {}
    }


def pollen_themes(
    KING,
    themes=[
        "nuetral",
        "custom",
        "long_star",
        "short_star",
        "day_shark",
        "safe",
        "star__storywave_AI",
    ],
    waves_cycles=["waveup", "wavedown"],
    wave_periods={
        "premarket": 0.01,
        "morning_9-11": 0.01,
        "lunch_11-2": 0.01,
        "afternoon_2-4": 0.01,
        "afterhours": 0.01,
        "Day": 0.01,
    },
):
    ## set the course for the day how you want to buy expecting more scalps vs long? this should update and change as new info comes into being
    # themes = ['nuetral', 'strong']
    # waves_cycles = ['waveup', 'wavedown']
    # wave_periods = {'morning_9-11': .01, 'lunch_11-2': .01, 'afternoon_2-4': .01, 'Day': .01, 'afterhours': .01}

    # star__storywave: auto_adjusting_with_starwave: using story
    star_times = KING["star_times"]
    pollen_themes = {}
    for theme in themes:
        pollen_themes[theme] = {}
        for star in star_times.keys():
            pollen_themes[theme][star] = {}
            for wave_c in waves_cycles:
                pollen_themes[theme][star][wave_c] = {
                    wave_period: n for (wave_period, n) in wave_periods.items()
                }

    return pollen_themes


def update_king_users(KING, init=False, users_allowed_queen_email=["stefanstapinski@gmail.com"]):
    con = sqlite3.connect(os.path.join(hive_master_root(), "db/client_users.db"))
    with con:
        cur = con.cursor()
        users = cur.execute("SELECT * FROM users").fetchall()
        df = pd.DataFrame(users)

    users_allowed_queen_email = [
        "stefanstapinski@gmail.com",
        "ng2654@columbia.edu",
        "mrubin2724@gmail.com",
        # "stevenweaver8@gmail.com",
        # "adivergentthinker@gmail.com",
        # "stapinski89@gmail.com",
        # "jehddie@gmail.com",
        # "conrad.studzinski@yahoo.com",
        # "jamesliess@icloud.com",
        # "pollenq.queen@gmail.com",
    ]

    if init:
        KING['users'] = {
            'client_users_db': df,
            'client_user__allowed_queen_list': users_allowed_queen_email
        }
    else:
        new_users = [i for i in df[0].tolist() if i not in KING['users'].get('client_users_db')[0].tolist()]
        if len(new_users) > 0:
            print("New Users to KING: ", new_users)
            KING['users']['client_users_db'] = df
    
    return KING


def init_KING():
    king = {}
    ticker_universe = return_Ticker_Universe()
    
    trigbees = ["buy_cross-0", "sell_cross-0", "ready_buy_cross"]
    waveBlocktimes = [
        "premarket",
        "morning_9-11",
        "lunch_11-2",
        "afternoon_2-4",
        "afterhours",
        "Day",
    ]

    king["star_times"] = stars()
    king["waveBlocktimes"] = waveBlocktimes
    king["trigbees"] = trigbees
    king = update_king_users(KING=king, init=True)
    king['ticker_universe'] = ticker_universe
    king['active_order_state_list'] = ['running', 'running_close', 'submitted', 'error', 'pending', 'completed', 'completed_alpaca', 'running_open', 'archived_bee']

    return king

def KOR_close_order_today_vars(take_profit=True):
    return {
        'take_profit': take_profit,
        'close_order_today_allowed_timeduration': 60,
    }


def star_names(name=None):
    chart_times = {
        'Flash': "1Minute_1Day",
        'Week': "5Minute_5Day",
        'Month': "30Minute_1Month",
        'Quarter': "1Hour_3Month",
        '2 Quarters': "2Hour_6Month",
        '1 Year': "1Day_1Year",
    }

    if name:
        return chart_times[name]
    else:
        return chart_times

def ttf_grid_names(ttf_name, symbol=True):
    symbol_n = ttf_name.split("_")[0]
    if '1Minute_1Day' in ttf_name:
      ttf_name = "Flash"
    elif '5Minute_5Day' in ttf_name:
      ttf_name = "Week"
    elif '30Minute_1Month' in ttf_name:
      ttf_name = "Month"
    elif '1Hour_3Month' in ttf_name:
      ttf_name = "Quarter"
    elif '2Hour_6Month' in ttf_name:
      ttf_name = "2 Quarters"
    elif '1Day_1Year' in ttf_name:
      ttf_name = "1 Year"
    
    if symbol:
        return f'{symbol_n} {ttf_name}'
    else:
       return ttf_name

def buy_button_dict_items(queen_handles_trade=True, 
                          star='1Minute_1Day',
                          star_list=list(star_names().keys()),
                          wave_amo=1000,
                          trade_using_limits=None,
                          limit_price=False,
                          take_profit=.03,
                          sell_out=-.03,
                          sell_trigbee_trigger=True,
                          sell_trigbee_trigger_timeduration=5,
                          close_order_today=False, 
                          reverse_buy=False, 
                          sell_at_vwap=False, 
                          ):
    column = {
                'queen_handles_trade': queen_handles_trade,
                'star':star,
                'wave_amo': wave_amo,
                # 'trade_using_limits': trade_using_limits,
                'limit_price': limit_price,
                'take_profit': take_profit,
                'sell_out': sell_out,
                'sell_trigbee_trigger': sell_trigbee_trigger,
                'sell_trigbee_trigger_timeduration': sell_trigbee_trigger_timeduration,
                'close_order_today': close_order_today,
                'reverse_buy': reverse_buy,
                'sell_at_vwap': sell_at_vwap,
                'star_list': star_list,
                }
    return {key: value for key, value in column.items() if value is not None}

def sell_button_dict_items(symbol="SPY", sell_qty=89):
    var_s = {
                'symbol': symbol,
                'sell_qty':sell_qty,
                }
    return var_s

def kings_order_rules( # rules created for 1Minute
    KOR_version=2,
    queen_handles_trade=True,
    order_side='buy', # 'sell'
    order_type='market',
    wave_amo=100,
    # Global, Buy, Sell
    theme='nuetral',
    status='active',
    trade_using_limits=False,
    limit_price=False,
    # BUYS
    doubledown_timeduration=60,

    ignore_trigbee_at_power=0.01,
    macd_tier_multiplier = {}, # deprecate
    vwap_tier_multiplier = {},# deprecate
    rsi_tier_multiplier = {},# deprecate

    # SELLS
    take_profit=.01,
    take_profit_scale={.05: {'take_pct': .25, 'take_mark': False}},
    sell_out=-.0089,
    sell_out_scale={.05: {'take_pct': .25, 'take_mark': False}},
    max_profit_Deviation=.5, # how far from max profit
    max_profit_waveDeviation=1, ## Need to figure out expected waveDeivation from a top profit in wave to allow trade to exit (faster from seeking profit?)
    max_profit_waveDeviation_timeduration=5, # Minutes
    timeduration=120, # Minutes ### DEPRECATE WORKERBEE
    sell_date=datetime.now().replace(hour=0, minute=00, second=0) + timedelta(days=366), 
    sell_trigbee_trigger=True,
    sell_trigbee_trigger_timeduration=60, # Minutes
    sell_at_vwap = 1, # Sell pct at vwap
    use_wave_guage=False,
    doubledowns_allowed=2,
    close_order_today=False,
    close_order_today_allowed_timeduration=60, # seconds allowed to be past, sells at 60 seconds left in close
    borrow_qty=0,
    # Not Used
    short_position=False,
    revisit_trade_frequency=60,
    take_profit_in_vwap_deviation_range={"low_range": -0.05, "high_range": 0.05},
    stagger_profits=False,
    scalp_profits=False,
    scalp_profits_timeduration=30,
    stagger_profits_tiers=1,
    limitprice_decay_timeduration=1,
    skip_sell_trigbee_distance_frequency=0,
    skip_buy_trigbee_distance_frequency=0,
    use_margin=False,

):

    return {
        "KOR_version": KOR_version,
        "queen_handles_trade": queen_handles_trade,
        "theme": theme,
        "status": status,
        "trade_using_limits": trade_using_limits,
        "limitprice_decay_timeduration": limitprice_decay_timeduration,
        "doubledown_timeduration": doubledown_timeduration,
        "max_profit_Deviation": max_profit_Deviation,
        "max_profit_waveDeviation": max_profit_waveDeviation,
        "max_profit_waveDeviation_timeduration": max_profit_waveDeviation_timeduration, # Deprecate
        "timeduration": timeduration, # Deprecate
        "take_profit": take_profit,
        "sell_out": sell_out,
        "sell_trigbee_trigger": sell_trigbee_trigger,
        "sell_date": sell_date,
        "sell_at_vwap": sell_at_vwap,
        "stagger_profits": stagger_profits, # Deprecate
        "scalp_profits": scalp_profits, # Deprecate
        "scalp_profits_timeduration": scalp_profits_timeduration,# Deprecate
        "stagger_profits_tiers": stagger_profits_tiers,# Deprecate
        "skip_sell_trigbee_distance_frequency": skip_sell_trigbee_distance_frequency,
        "skip_buy_trigbee_distance_frequency": skip_buy_trigbee_distance_frequency,
        # skip sell signal if frequency of last sell signal was X distance >> timeperiod over value, 1m: if sell was 1 story index ago
        "ignore_trigbee_at_power": ignore_trigbee_at_power, # Deprecate ?
        "take_profit_in_vwap_deviation_range": take_profit_in_vwap_deviation_range, # Deprecate ?
        "short_position": short_position,
        'use_wave_guage': use_wave_guage,
        'doubledowns_allowed': doubledowns_allowed,
        'close_order_today': close_order_today,
        "use_margin": use_margin, # Deprecate
        "revisit_trade_frequency": revisit_trade_frequency, # Deprecate ???
        'close_order_today_allowed_timeduration': close_order_today_allowed_timeduration,

        'macd_tier_multiplier': {}, # Deprecate ?
        'vwap_tier_multiplier': {}, # Deprecate ?
        'rsi_tier_multiplier': {}, # Deprecate ?
        'sell_trigbee_trigger_timeduration': sell_trigbee_trigger_timeduration,
        'borrow_qty': borrow_qty, # Deprecate
        'order_side': order_side,
        'wave_amo': wave_amo,
        'limit_price': limit_price,

    }

def generate_TradingModel(
    theme="nuetral", portfolio_name="Jq", ticker="SPY",
    stars=stars, trigbees=["buy_cross-0", "sell_cross-0", "ready_buy_cross"], 
    trading_model_name="MACD", status="active", portforlio_weight_ask=0.01, init=False,
    ):
    # theme level settings
    themes = [
        "nuetral", # Custom
        "custom", # Custom
        "long_star", # 1yr + 6Mon
        "short_star", # 1min(safe) + 5Min(safe) + 
        "day_shark",
        "safe",
        "star__storywave_AI", # 
    ]

    def theme_king_order_rules(theme, stars=stars):
        # " time duration in minutes" ### DOUBLE CHECK SOME NOT ALIGNED IN SECONDS ###
        # Returns Star KOR for all waveblocktimes
        
        # Default Model Settings return all levels of model
        symbol_theme_vars = {
            "power_rangers": {
                "1Minute_1Day": True,
                "5Minute_5Day" : True,
                "30Minute_1Month": True,
                "1Hour_3Month": True,
                "2Hour_6Month": True,
                "1Day_1Year": True,

            }
        }        
        star_theme_vars = {
                "1Minute_1Day": {
                    'stagger_profits':False, 
                    'buyingpower_allocation_LongTerm': .1,
                    'buyingpower_allocation_ShortTerm': .2,
                    'use_margin': False,
                    },
                "5Minute_5Day" : {
                    'stagger_profits':False, 
                    'buyingpower_allocation_LongTerm': .5,
                    'buyingpower_allocation_ShortTerm': .4,
                    'use_margin': False,
                    },
                "30Minute_1Month": {
                    'stagger_profits':False, 
                    'buyingpower_allocation_LongTerm': .6,
                    'buyingpower_allocation_ShortTerm': .4,
                    'use_margin': False,
                    },
                "1Hour_3Month": {
                    'stagger_profits':False, 
                    'buyingpower_allocation_LongTerm': .8,
                    'buyingpower_allocation_ShortTerm': .5,
                    'use_margin': False,
                    },
                "2Hour_6Month": {
                    'stagger_profits':False, 
                    'buyingpower_allocation_LongTerm': .8,
                    'buyingpower_allocation_ShortTerm': .8,
                    'use_margin': False,
                    },
                "1Day_1Year": {
                    'stagger_profits':False, 
                    'buyingpower_allocation_LongTerm': .8,
                    'buyingpower_allocation_ShortTerm': .8,
                    'use_margin': False,
                    },
        }
        wave_block_theme__kor = {}

        if theme.lower() == 'nuetral':
            symbol_theme_vars = symbol_theme_vars
            star_theme_vars = star_theme_vars
            wave_block_theme__kor = {
                "1Minute_1Day": kings_order_rules(
                                    theme=theme,
                                    status='active',
                                    doubledown_timeduration=60,
                                    trade_using_limits=False,
                                    max_profit_waveDeviation=3,
                                    max_profit_waveDeviation_timeduration=5,
                                    timeduration=360,
                                    take_profit=.01,
                                    sell_out=0,
                                    sell_trigbee_trigger=False,
                                    sell_trigbee_trigger_timeduration=60,#mins
                                    stagger_profits=False,
                                    scalp_profits=False,
                                    scalp_profits_timeduration=30,
                                    stagger_profits_tiers=1,
                                    limitprice_decay_timeduration=1,
                                    skip_sell_trigbee_distance_frequency=1,
                                    ignore_trigbee_at_power=0.01,
                                    # ignore_trigbee_in_vwap_range={"low_range": -0.05, "high_range": 0.05},
                                    take_profit_in_vwap_deviation_range={"low_range": -0.05, "high_range": 0.05},
                                    short_position=False,
                                    use_wave_guage=False,
                                    close_order_today=False,
                                    revisit_trade_frequency=60,
                ),
                "5Minute_5Day": kings_order_rules(
                                    theme=theme,
                                    status='active',
                                    doubledown_timeduration=60,
                                    trade_using_limits=False,
                                    max_profit_waveDeviation=3,
                                    max_profit_waveDeviation_timeduration=10,
                                    timeduration=320,
                                    take_profit=.05,
                                    sell_out=0,
                                    sell_trigbee_trigger=True,
                                    sell_trigbee_trigger_timeduration=60*5,#mins
                                    stagger_profits=False,
                                    scalp_profits=False,
                                    scalp_profits_timeduration=30,
                                    stagger_profits_tiers=3,
                                    limitprice_decay_timeduration=1,
                                    skip_sell_trigbee_distance_frequency=0,
                                    ignore_trigbee_at_power=0.01,
                                    # ignore_trigbee_in_vwap_range={"low_range": -0.05, "high_range": 0.05},
                                    take_profit_in_vwap_deviation_range={"low_range": -0.05, "high_range": 0.05},
                                    short_position=False,
                                    use_wave_guage=False,
                                    close_order_today=False,
                                    revisit_trade_frequency=5 * 3600,
                ),
                "30Minute_1Month": kings_order_rules(
                                    theme=theme,
                                    status='active',
                                    doubledown_timeduration=60,
                                    trade_using_limits=False,
                                    max_profit_waveDeviation=2,
                                    max_profit_waveDeviation_timeduration=30,
                                    timeduration=43800,
                                    take_profit=.05,
                                    sell_out=0,
                                    sell_trigbee_trigger=True,
                                    sell_trigbee_trigger_timeduration=60*30,#mins
                                    stagger_profits=False,
                                    scalp_profits=False,
                                    scalp_profits_timeduration=30,
                                    stagger_profits_tiers=1,
                                    limitprice_decay_timeduration=1,
                                    skip_sell_trigbee_distance_frequency=0,
                                    ignore_trigbee_at_power=0.01,
                                    # ignore_trigbee_in_vwap_range={"low_range": -0.05, "high_range": 0.05},
                                    take_profit_in_vwap_deviation_range={"low_range": -0.05, "high_range": 0.05},
                                    short_position=False,
                                    use_wave_guage=False,
                                    close_order_today=False,
                                    revisit_trade_frequency=10 * 3600,
                ),
                "1Hour_3Month": kings_order_rules(
                                    theme=theme,
                                    status='active',
                                    doubledown_timeduration=60,
                                    trade_using_limits=False,
                                    max_profit_waveDeviation=2,
                                    max_profit_waveDeviation_timeduration=60,
                                    timeduration=43800 * 3,
                                    take_profit=.05,
                                    sell_out=0,
                                    sell_trigbee_trigger=True,
                                    sell_trigbee_trigger_timeduration=60*60,#mins
                                    stagger_profits=False,
                                    scalp_profits=False,
                                    scalp_profits_timeduration=30,
                                    stagger_profits_tiers=1,
                                    limitprice_decay_timeduration=1,
                                    skip_sell_trigbee_distance_frequency=0,
                                    ignore_trigbee_at_power=0.01,
                                    # ignore_trigbee_in_vwap_range={"low_range": -0.05, "high_range": 0.05},
                                    take_profit_in_vwap_deviation_range={"low_range": -0.05, "high_range": 0.05},
                                    short_position=False,
                                    use_wave_guage=False,
                                    close_order_today=False,
                                    revisit_trade_frequency=10 * 3600,
                ),
                "2Hour_6Month": kings_order_rules(
                                    theme='nuetral',
                                    status='active',
                                    doubledown_timeduration=60,
                                    trade_using_limits=False,
                                    max_profit_waveDeviation=2,
                                    max_profit_waveDeviation_timeduration=120,
                                    timeduration=43800 * 6,
                                    take_profit=.07,
                                    sell_out=0,
                                    sell_trigbee_trigger=True,
                                    sell_trigbee_trigger_timeduration=60*120,#mins
                                    stagger_profits=False,
                                    scalp_profits=False,
                                    scalp_profits_timeduration=30,
                                    stagger_profits_tiers=1,
                                    limitprice_decay_timeduration=1,
                                    skip_sell_trigbee_distance_frequency=0,
                                    ignore_trigbee_at_power=0.01,
                                    # ignore_trigbee_in_vwap_range={"low_range": -0.05, "high_range": 0.05},
                                    take_profit_in_vwap_deviation_range={"low_range": -0.05, "high_range": 0.05},
                                    short_position=False,
                                    use_wave_guage=False,
                                    close_order_today=False,
                                    revisit_trade_frequency=10 * 3600,
                ),
                "1Day_1Year": kings_order_rules(
                                    theme=theme,
                                    status='active',
                                    doubledown_timeduration=60,
                                    trade_using_limits=False,
                                    max_profit_waveDeviation=3,
                                    max_profit_waveDeviation_timeduration=60 * 24, 
                                    timeduration=525600,
                                    take_profit=.08,
                                    sell_out=0,
                                    sell_trigbee_trigger=True,
                                    sell_trigbee_trigger_timeduration=60*300,#mins
                                    stagger_profits=False,
                                    scalp_profits=False,
                                    scalp_profits_timeduration=30,
                                    stagger_profits_tiers=1,
                                    limitprice_decay_timeduration=1,
                                    skip_sell_trigbee_distance_frequency=0,
                                    ignore_trigbee_at_power=0.01,
                                    # ignore_trigbee_in_vwap_range={"low_range": -0.05, "high_range": 0.05},
                                    take_profit_in_vwap_deviation_range={"low_range": -0.05, "high_range": 0.05},
                                    short_position=False,
                                    use_wave_guage=False,
                                    close_order_today=False,
                                    revisit_trade_frequency=60 * 3600,
                ),
            }
        elif theme.lower() == 'long_star':
            symbol_theme_vars = symbol_theme_vars
            star_theme_vars = {
                "1Minute_1Day": {
                    'stagger_profits':False, 
                    'buyingpower_allocation_LongTerm': .1,
                    'buyingpower_allocation_ShortTerm': .5,
                    'use_margin': False,
                    },
                "5Minute_5Day" : {
                    'stagger_profits':False, 
                    'buyingpower_allocation_LongTerm': .3,
                    'buyingpower_allocation_ShortTerm': .5,
                    'use_margin': False,
                    },
                "30Minute_1Month": {
                    'stagger_profits':False, 
                    'buyingpower_allocation_LongTerm': .4,
                    'buyingpower_allocation_ShortTerm': .2,
                    'use_margin': False,
                    },
                "1Hour_3Month": {
                    'stagger_profits':False, 
                    'buyingpower_allocation_LongTerm': .5,
                    'buyingpower_allocation_ShortTerm': .2,
                    'use_margin': False,
                    },
                "2Hour_6Month": {
                    'stagger_profits':False, 
                    'buyingpower_allocation_LongTerm': .8,
                    'buyingpower_allocation_ShortTerm': .2,
                    'use_margin': False,
                    },
                "1Day_1Year": {
                    'stagger_profits':False, 
                    'buyingpower_allocation_LongTerm': .99,
                    'buyingpower_allocation_ShortTerm': .2,
                    'use_margin': False,
                    },
        }
            wave_block_theme__kor = {
                "1Minute_1Day": kings_order_rules(
                                    theme=theme,
                                    status='active',
                                    doubledown_timeduration=60,
                                    trade_using_limits=False,
                                    max_profit_waveDeviation=1,
                                    max_profit_waveDeviation_timeduration=5,
                                    timeduration=120,
                                    take_profit=.005,
                                    sell_out=-.089,
                                    sell_trigbee_trigger=True,
                                    stagger_profits=False,
                                    scalp_profits=False,
                                    scalp_profits_timeduration=30,
                                    stagger_profits_tiers=1,
                                    limitprice_decay_timeduration=1,
                                    skip_sell_trigbee_distance_frequency=0,
                                    ignore_trigbee_at_power=0.01,
                                    # ignore_trigbee_in_vwap_range={"low_range": -0.05, "high_range": 0.05},
                                    take_profit_in_vwap_deviation_range={"low_range": -0.05, "high_range": 0.05},
                                    short_position=False,
                                    use_wave_guage=False,
                                    close_order_today=True,
                ),
                "5Minute_5Day": kings_order_rules(
                                    theme=theme,
                                    status='active',
                                    doubledown_timeduration=60,
                                    trade_using_limits=False,
                                    max_profit_waveDeviation=1,
                                    max_profit_waveDeviation_timeduration=5,
                                    timeduration=320,
                                    take_profit=.01,
                                    sell_out=-.0089,
                                    sell_trigbee_trigger=True,
                                    stagger_profits=False,
                                    scalp_profits=False,
                                    scalp_profits_timeduration=30,
                                    stagger_profits_tiers=1,
                                    limitprice_decay_timeduration=1,
                                    skip_sell_trigbee_distance_frequency=0,
                                    ignore_trigbee_at_power=0.01,
                                    # ignore_trigbee_in_vwap_range={"low_range": -0.05, "high_range": 0.05},
                                    take_profit_in_vwap_deviation_range={"low_range": -0.05, "high_range": 0.05},
                                    short_position=False,
                                    use_wave_guage=False,
                                    close_order_today=True,
                ),
                "30Minute_1Month": kings_order_rules(
                                    theme=theme,
                                    status='active',
                                    doubledown_timeduration=60,
                                    trade_using_limits=False,
                                    max_profit_waveDeviation=1,
                                    max_profit_waveDeviation_timeduration=30,
                                    timeduration=43800,
                                    take_profit=.01,
                                    sell_out=-.0089,
                                    sell_trigbee_trigger=True,
                                    stagger_profits=False,
                                    scalp_profits=False,
                                    scalp_profits_timeduration=30,
                                    stagger_profits_tiers=1,
                                    limitprice_decay_timeduration=1,
                                    skip_sell_trigbee_distance_frequency=0,
                                    ignore_trigbee_at_power=0.01,
                                    # ignore_trigbee_in_vwap_range={"low_range": -0.05, "high_range": 0.05},
                                    take_profit_in_vwap_deviation_range={"low_range": -0.05, "high_range": 0.05},
                                    short_position=False,
                                    use_wave_guage=False,
                ),
                "1Hour_3Month": kings_order_rules(
                                    theme=theme,
                                    status='active',
                                    doubledown_timeduration=60,
                                    trade_using_limits=False,
                                    max_profit_waveDeviation=1,
                                    max_profit_waveDeviation_timeduration=60,
                                    timeduration=43800 * 3,
                                    take_profit=.01,
                                    sell_out=-.0089,
                                    sell_trigbee_trigger=True,
                                    stagger_profits=False,
                                    scalp_profits=False,
                                    scalp_profits_timeduration=30,
                                    stagger_profits_tiers=1,
                                    limitprice_decay_timeduration=1,
                                    skip_sell_trigbee_distance_frequency=0,
                                    ignore_trigbee_at_power=0.01,
                                    # ignore_trigbee_in_vwap_range={"low_range": -0.05, "high_range": 0.05},
                                    take_profit_in_vwap_deviation_range={"low_range": -0.05, "high_range": 0.05},
                                    short_position=False,
                                    use_wave_guage=False,
                ),
                "2Hour_6Month": kings_order_rules(
                                    theme='nuetral',
                                    status='active',
                                    doubledown_timeduration=60,
                                    trade_using_limits=False,
                                    max_profit_waveDeviation=1,
                                    max_profit_waveDeviation_timeduration=120,
                                    timeduration=43800 * 6,
                                    take_profit=.01,
                                    sell_out=-.0089,
                                    sell_trigbee_trigger=True,
                                    stagger_profits=False,
                                    scalp_profits=False,
                                    scalp_profits_timeduration=30,
                                    stagger_profits_tiers=1,
                                    limitprice_decay_timeduration=1,
                                    skip_sell_trigbee_distance_frequency=0,
                                    ignore_trigbee_at_power=0.01,
                                    # ignore_trigbee_in_vwap_range={"low_range": -0.05, "high_range": 0.05},
                                    take_profit_in_vwap_deviation_range={"low_range": -0.05, "high_range": 0.05},
                                    short_position=False,
                                    use_wave_guage=False,
                ),
                "1Day_1Year": kings_order_rules(
                                    theme=theme,
                                    status='active',
                                    doubledown_timeduration=60,
                                    trade_using_limits=False,
                                    max_profit_waveDeviation=1,
                                    max_profit_waveDeviation_timeduration=60 * 24, 
                                    timeduration=525600,
                                    take_profit=.05,
                                    sell_out=-.015,
                                    sell_trigbee_trigger=True,
                                    stagger_profits=False,
                                    scalp_profits=False,
                                    scalp_profits_timeduration=30,
                                    stagger_profits_tiers=1,
                                    limitprice_decay_timeduration=1,
                                    skip_sell_trigbee_distance_frequency=0,
                                    ignore_trigbee_at_power=0.01,
                                    # ignore_trigbee_in_vwap_range={"low_range": -0.05, "high_range": 0.05},
                                    take_profit_in_vwap_deviation_range={"low_range": -0.05, "high_range": 0.05},
                                    short_position=False,
                                    use_wave_guage=False,
                ),
            }
        else: # custom catch all ? Random AI
            print("there is no else, get it right")

        return symbol_theme_vars, star_theme_vars,  wave_block_theme__kor
    
    def star_trading_model_vars(star_theme_vars, wave_block_theme__kor, trigbees, stars=stars):

        def star_kings_order_rules_mapping(stars, trigbees, waveBlocktimes, wave_block_theme__kor=wave_block_theme__kor,):
            # symbol_theme_vars, star_theme_vars, wave_block_theme__kor =  theme_king_order_rules(theme=theme, stars=stars)
            # star_kings_order_rules_dict["1Minute_1Day"][trigbee]
            # for theme in themes
            # import copy
            star_kings_order_rules_dict = {} # Master Return
            for star in stars().keys():
                star_kings_order_rules_dict[star] = {}
                for trigbee in trigbees:
                    star_kings_order_rules_dict[star][trigbee] = {}
                    for blocktime in waveBlocktimes:
                        star_kings_order_rules_dict[star][trigbee][blocktime] = wave_block_theme__kor.get(star) # theme=theme

            return star_kings_order_rules_dict

        def star_vars_mapping(star_theme_vars, trigbees, waveBlocktimes, stars=stars,theme=theme,):
            return_dict = {}
            
            trigbees_king_order_rules = star_kings_order_rules_mapping(stars=stars, trigbees=trigbees, waveBlocktimes=waveBlocktimes)
            
            # for star in stars:
            #     return_dict[star] = {
            #     "total_budget": 0,
            #     "trade_using_limits": False,
            #     "buyingpower_allocation_LongTerm": star_theme_vars[star].get('buyingpower_allocation_LongTerm'),
            #     "buyingpower_allocation_ShortTerm": star_theme_vars[star].get('buyingpower_allocation_ShortTerm'),
            #     "stagger_profits": star_theme_vars[star].get('stagger_profits'),
            #     "use_margin": star_theme_vars[star].get('use_margin'),
            #     "power_rangers": {k: 1 for k in stars().keys()},
            #     "trigbees": trigbees_king_order_rules[star],
            #     "short_position": False,
            #     "ticker_family": [ticker],
            #     "theme": theme,
            # }
            
            star = "1Minute_1Day"
            return_dict[star] = {
                "total_budget": 0,
                "trade_using_limits": False,
                "buyingpower_allocation_LongTerm": star_theme_vars[star].get('buyingpower_allocation_LongTerm'),
                "buyingpower_allocation_ShortTerm": star_theme_vars[star].get('buyingpower_allocation_ShortTerm'),
                "stagger_profits": star_theme_vars[star].get('stagger_profits'),
                "use_margin": star_theme_vars[star].get('use_margin'),
                "power_rangers": {k: 1 for k in stars().keys()},
                "trigbees": trigbees_king_order_rules[star],
                "short_position": False,
                "ticker_family": [ticker],
                "theme": theme,
            }
            star = "5Minute_5Day"
            return_dict[star] = {
                "total_budget": 0,
                "trade_using_limits": False,
                "buyingpower_allocation_LongTerm": star_theme_vars[star].get('buyingpower_allocation_LongTerm'),
                "buyingpower_allocation_ShortTerm": star_theme_vars[star].get('buyingpower_allocation_ShortTerm'),
                "stagger_profits": star_theme_vars[star].get('stagger_profits'),
                "use_margin": star_theme_vars[star].get('use_margin'),
                "power_rangers": {k: 1 for k in stars().keys()},
                "trigbees": trigbees_king_order_rules[star],
                "short_position": False,
                "ticker_family": [ticker],
                "theme": theme,
            }
            star = "30Minute_1Month"
            return_dict[star] = {
                "total_budget": 0,
                "trade_using_limits": False,
                "buyingpower_allocation_LongTerm": star_theme_vars[star].get('buyingpower_allocation_LongTerm'),
                "buyingpower_allocation_ShortTerm": star_theme_vars[star].get('buyingpower_allocation_ShortTerm'),
                "stagger_profits": star_theme_vars[star].get('stagger_profits'),
                "use_margin": star_theme_vars[star].get('use_margin'),
                "power_rangers": {k: 1 for k in stars().keys()},
                "trigbees": trigbees_king_order_rules[star],
                "short_position": False,
                "ticker_family": [ticker],
                "theme": theme,
            }
            star = "1Hour_3Month"
            return_dict[star] = {
                "total_budget": 0,
                "trade_using_limits": False,
                "buyingpower_allocation_LongTerm": star_theme_vars[star].get('buyingpower_allocation_LongTerm'),
                "buyingpower_allocation_ShortTerm": star_theme_vars[star].get('buyingpower_allocation_ShortTerm'),
                "stagger_profits": star_theme_vars[star].get('stagger_profits'),
                "use_margin": star_theme_vars[star].get('use_margin'),
                "power_rangers": {k: 1 for k in stars().keys()},
                "trigbees": trigbees_king_order_rules[star],
                "short_position": False,
                "ticker_family": [ticker],
                "theme": theme,
            }
            star = "2Hour_6Month"
            return_dict[star] = {
                "total_budget": 0,
                "trade_using_limits": False,
                "buyingpower_allocation_LongTerm": star_theme_vars[star].get('buyingpower_allocation_LongTerm'),
                "buyingpower_allocation_ShortTerm": star_theme_vars[star].get('buyingpower_allocation_ShortTerm'),
                "stagger_profits": star_theme_vars[star].get('stagger_profits'),
                "use_margin": star_theme_vars[star].get('use_margin'),
                "power_rangers": {k: 1 for k in stars().keys()},
                "trigbees": trigbees_king_order_rules[star],
                "short_position": False,
                "ticker_family": [ticker],
                "theme": theme,
            }
            star = "1Day_1Year"
            return_dict[star] = {
                "total_budget": 0,
                "trade_using_limits": False,
                "buyingpower_allocation_LongTerm": star_theme_vars[star].get('buyingpower_allocation_LongTerm'),
                "buyingpower_allocation_ShortTerm": star_theme_vars[star].get('buyingpower_allocation_ShortTerm'),
                "stagger_profits": star_theme_vars[star].get('stagger_profits'),
                "use_margin": star_theme_vars[star].get('use_margin'),
                "power_rangers": {k: 1 for k in stars().keys()},
                "trigbees": trigbees_king_order_rules[star],
                "short_position": False,
                "ticker_family": [ticker],
                "theme": theme,
            }

            return return_dict

        def star_vars(star, star_vars_mapping):
            return {
                "star": star,
                # 'status': star_vars_mapping[star]['status'],
                "trade_using_limits": star_vars_mapping[star]["trade_using_limits"],
                "total_budget": star_vars_mapping[star]["total_budget"],
                "buyingpower_allocation_LongTerm": star_vars_mapping[star]["buyingpower_allocation_LongTerm"],
                "buyingpower_allocation_ShortTerm": star_vars_mapping[star]["buyingpower_allocation_ShortTerm"],
                "power_rangers": star_vars_mapping[star]["power_rangers"],
                "trigbees": star_vars_mapping[star]["trigbees"],
                "short_position": star_vars_mapping[star]["short_position"],
                "ticker_family": star_vars_mapping[star]["ticker_family"],
            }

        # Get Stars Trigbees and Blocktimes to create kings order rules
        all_stars = stars().keys()
        waveBlocktimes = [
            "premarket",
            "morning_9-11",
            "lunch_11-2",
            "afternoon_2-4",
            "afterhours",
            "Day",
        ]
        star_vars_mapping_dict = star_vars_mapping(
            trigbees=trigbees, waveBlocktimes=waveBlocktimes, stars=stars, theme=theme, star_theme_vars=star_theme_vars
        )

        return_dict = {
            star: star_vars(star=star, star_vars_mapping=star_vars_mapping_dict)
            for star in all_stars
        }

        return return_dict

    def model_vars(trading_model_name, star, stars_vars, stars=stars):
        return {
            # 'status': stars_vars[star]['status'],
            "buyingpower_allocation_LongTerm": stars_vars[star]["buyingpower_allocation_LongTerm"],
            "buyingpower_allocation_ShortTerm": stars_vars[star]["buyingpower_allocation_ShortTerm"],
            "power_rangers": stars_vars[star]["power_rangers"],
            "trade_using_limits": stars_vars[star]["trade_using_limits"],
            "total_budget": stars_vars[star]["total_budget"],
            "trigbees": stars_vars[star]["trigbees"],
            "index_inverse_X": "1X",
            "index_long_X": "1X",
            "trading_model_name": trading_model_name,
        }

    def tradingmodel_vars(
        symbol_theme_vars,
        stars_vars,
        trigbees=trigbees,
        ticker=ticker,
        trading_model_name=trading_model_name,
        status=status,
        portforlio_weight_ask=portforlio_weight_ask,
        stars=stars,
        portfolio_name=portfolio_name,
        theme=theme,):
        
        afterhours = True if ticker in crypto_currency_symbols else False
        afternoon = True if ticker in crypto_currency_symbols else True
        lunch = True if ticker in crypto_currency_symbols else True
        morning = True if ticker in crypto_currency_symbols else True
        premarket = True if ticker in crypto_currency_symbols else False
        Day = True if ticker in crypto_currency_symbols else False

        time_blocks = {
            "premarket": premarket,
            "afterhours": afterhours,
            "morning_9-11": morning,
            "lunch_11-2": lunch,
            "afternoon_2-4": afternoon,
            "afterhours": afterhours,
            "Day": Day,
        }

        allow_for_margin = [False if ticker in crypto_currency_symbols else True][0]
        # etf_X_direction = ["1X", "2X", "3X"]  # Determined by QUEEN

        def init_stars_allocation():
            return {}

        model1 = {
            "theme": theme,
            "QueenBeeTrader": "Jq",
            "status": status,
            "buyingpower_allocation_LongTerm": 0.2,
            "buyingpower_allocation_ShortTerm": 0.8,
            "index_long_X": "1X",
            "index_inverse_X": "1X",
            "portforlio_weight_ask": portforlio_weight_ask,
            "total_budget": 0,
            "max_single_trade_amount": 100000,
            "allow_for_margin": allow_for_margin,
            "buy_ONLY_by_accept_from_QueenBeeTrader": False,
            "trading_model_name": trading_model_name,
            "portfolio_name": portfolio_name,
            "trigbees": {k: True for k in trigbees},
            "time_blocks": time_blocks,
            "power_rangers": {k: True for k in stars().keys()},
            "stars": {k: True for k in stars().keys()},
            "stars_kings_order_rules": {
                star: model_vars(
                    trading_model_name=trading_model_name,
                    star=star,
                    stars_vars=stars_vars,
                )
                for star in stars().keys()
            },
            "short_position": False,  # flip all star allocation to short
            "ticker_family": [ticker],
        }

        star_model = {ticker: model1}

        return star_model

    try:
        # Trading Model Version 1
        symbol_theme_vars, star_theme_vars, wave_block_theme__kor =  theme_king_order_rules(theme=theme, stars=stars)
        stars_vars = star_trading_model_vars(star_theme_vars, wave_block_theme__kor, trigbees)
        # {ticker: model_vars}
        macd_model = tradingmodel_vars(symbol_theme_vars=symbol_theme_vars, stars_vars=stars_vars)

        # if init==False:
        #     print(f'{trading_model_name} {ticker} {theme} Model Generated')

        return {"MACD": macd_model}
    except Exception as e:
        print_line_of_error("generate trading model error")
        return None



#### QUEENBEE ######## QUEENBEE ######## QUEENBEE ######## QUEENBEE ######## QUEENBEE ####
#### QUEENBEE ######## QUEENBEE ######## QUEENBEE ######## QUEENBEE ######## QUEENBEE ####
#### QUEENBEE ######## QUEENBEE ######## QUEENBEE ######## QUEENBEE ######## QUEENBEE ####
#### QUEENBEE ######## QUEENBEE ######## QUEENBEE ######## QUEENBEE ######## QUEENBEE ####
#### QUEENBEE ######## QUEENBEE ######## QUEENBEE ######## QUEENBEE ######## QUEENBEE ####
#### QUEENBEE ######## QUEENBEE ######## QUEENBEE ######## QUEENBEE ######## QUEENBEE ####

def init_queenbee(client_user, prod, queen=False, queen_king=False, orders=False, api=False, init=False, broker=False, queens_chess_piece="queen", broker_info=False, revrec=False, init_pollen_ONLY=False, queen_heart=False):
    db_root = init_clientUser_dbroot(client_username=client_user)

    init_pollen = init_pollen_dbs(db_root=db_root, prod=prod, queens_chess_piece=queens_chess_piece, init=init)
    if init_pollen_ONLY:
        return {'init_pollen': init_pollen}

    QUEEN = ReadPickleData(init_pollen.get('PB_QUEEN_Pickle')) if queen else {}
    QUEENsHeart = ReadPickleData(init_pollen['PB_QUEENsHeart_PICKLE']) if queen or queen_heart else {}
    QUEEN_KING = ReadPickleData(init_pollen.get('PB_App_Pickle')) if queen_king else {}
    ORDERS = ReadPickleData(init_pollen.get('PB_Orders_Pickle')) if orders else {}
    BROKER = ReadPickleData(init_pollen.get('PB_broker_PICKLE')) if broker else {}
    broker_info = ReadPickleData(init_pollen.get('PB_account_info_PICKLE')) if broker_info else {}
    revrec = ReadPickleData(init_pollen.get('PB_RevRec_PICKLE')).get('revrec') if revrec else {}

    if QUEEN_KING:
        QUEEN_KING['dbs'] = init_pollen
        QUEEN_KING['last_modified'] = os.stat(init_pollen.get('PB_App_Pickle')).st_mtime
    if QUEEN:
        QUEEN['dbs'] = init_pollen
        QUEEN['heartbeat']['beat'] = QUEENsHeart
    # if BROKER:

    """ Keys """ 
    api = return_alpaca_user_apiKeys(QUEEN_KING=QUEEN_KING, authorized_user=True, prod=prod) if api else {}
    if api == False:
        if QUEEN_KING:
            print("API Keys Failed, Queen goes back to Sleep")
            QUEEN_KING['api'] = False
            PickleData(pickle_file=init_pollen.get('PB_App_Pickle'), data_to_store=QUEEN_KING)
    
    return {"QUEEN": QUEEN, 
            "QUEEN_KING": QUEEN_KING, 
            "ORDERS": ORDERS, 
            "api": api, 
            'BROKER': BROKER, 
            'QUEENsHeart': QUEENsHeart,
            'broker_info': broker_info,
            "revrec": revrec,}


def process_order_submission(trading_model, order, order_vars, trig, symbol, ticker_time_frame, star, portfolio_name='Jq', status_q=False, exit_order_link=False, priceinfo=False):

    try:
        # Create Running Order
        new_queen_order = create_QueenOrderBee(
        trading_model=trading_model,
        order_vars=order_vars, 
        order=order, 
        symbol=symbol,
        star=star,
        ticker_time_frame=ticker_time_frame, 
        portfolio_name=portfolio_name, 
        status_q=status_q, 
        trig=trig, 
        exit_order_link=exit_order_link, 
        priceinfo=priceinfo
        )
        # Append Order
        new_queen_order_df = pd.DataFrame([new_queen_order]).set_index("client_order_id")
        new_queen_order_df['cost_basis_current'] = new_queen_order_df.get('wave_amo')
        
        return new_queen_order_df

    except Exception as e:
        print_line_of_error()
        body=str(e)
        send_email(recipient='stapinski89@gmail.com', subject="NotAllowedQueen", body=body)


def order_vars__queen_order_items(
    order_side=False,
    trading_model=False,
    king_order_rules=False,
    wave_amo=False,
    maker_middle=False,
    origin_wave=False,
    power_up_rangers=False,
    symbol=False,
    ticker_time_frame_origin=False,
    double_down_trade=False,
    sell_reason={},
    running_close_legs=False,
    wave_at_creation={},
    assigned_wave={},
    sell_qty=False,
    first_sell=False,
    time_intrade=False,
    updated_at=False,
    trigbee=False,
    tm_trig=False,
    borrowed_funds=False,
    ready_buy=False,
    borrow_qty=0,
):
    if order_side:
        order_vars = {}
        if order_side == "sell":
            if maker_middle:
                order_vars["order_type"] = "limit"
                order_vars["limit_price"] = maker_middle  # 10000
                order_vars["order_trig_sell_stop_limit"] = True
            else:
                order_vars["order_type"] = "market"
                order_vars["limit_price"] = False
                order_vars["order_trig_sell_stop_limit"] = False

            order_vars["origin_wave"] = origin_wave
            order_vars["power_up"] = power_up_rangers
            order_vars["wave_amo"] = wave_amo
            order_vars["order_side"] = order_side
            order_vars["ticker_time_frame_origin"] = ticker_time_frame_origin
            order_vars["power_up_rangers"] = power_up_rangers
            order_vars["king_order_rules"] = king_order_rules
            order_vars["trading_model"] = trading_model
            order_vars["double_down_trade"] = double_down_trade
            order_vars["sell_reason"] = sell_reason
            order_vars["running_close_legs"] = running_close_legs
            order_vars["wave_at_creation"] = wave_at_creation
            order_vars["sell_qty"] = sell_qty
            order_vars["first_sell"] = first_sell
            order_vars["time_intrade"] = time_intrade
            order_vars["updated_at"] = updated_at
            order_vars["symbol"] = symbol
            
            
            return order_vars

        elif order_side == "buy":
            if maker_middle:
                order_vars["order_type"] = "limit"
                order_vars["limit_price"] = maker_middle  # 10000
                order_vars["order_trig_sell_stop_limit"] = True
            else:
                order_vars["order_type"] = "market"
                order_vars["limit_price"] = False
                order_vars["order_trig_sell_stop_limit"] = False

            
            order_vars["assigned_wave"] = assigned_wave
            order_vars["origin_wave"] = origin_wave
            order_vars["power_up"] = sum(power_up_rangers.values())
            order_vars["wave_amo"] = wave_amo
            order_vars["order_side"] = order_side
            order_vars["ticker_time_frame_origin"] = ticker_time_frame_origin
            order_vars["power_up_rangers"] = power_up_rangers
            order_vars["king_order_rules"] = king_order_rules
            order_vars["trading_model"] = trading_model
            order_vars["double_down_trade"] = double_down_trade
            order_vars["sell_reason"] = sell_reason
            order_vars["running_close_legs"] = running_close_legs
            order_vars["wave_at_creation"] = wave_at_creation
            order_vars["sell_qty"] = sell_qty
            order_vars["first_sell"] = first_sell
            order_vars["time_intrade"] = time_intrade
            order_vars["updated_at"] = updated_at
            order_vars["symbol"] = symbol
            order_vars["trigbee"] = trigbee
            order_vars["tm_trig"] = tm_trig
            order_vars["borrowed_funds"] = borrowed_funds
            order_vars["ready_buy"] = ready_buy
            order_vars["borrow_qty"] = borrow_qty

            return order_vars

        else:
            print("break in program")
            logging_log_message(
                log_type="error", msg="break in program order vars queen order items"
            )
            return False
    else:
        print("break in program")
        logging_log_message(
            log_type="error", msg="break in program order vars queen order items"
        )
        return False


def create_QueenOrderBee(
    queen_order_version=1,
    trading_model="init",
    ticker_time_frame="SPY_1Minute_1Day",
    symbol="SPY",
    star='1Minute_1Day',
    portfolio_name="Jq",
    status_q="init",
    trig="buy_cross-0",
    exit_order_link="init",
    order_vars={},
    order={},
    priceinfo={},
    queen_init=False,
    long_short="init",
):  # Create Running Order
    def gen_queen_order(
        queen_order_version=queen_order_version,
        trading_model=trading_model,
        double_down_trade=False,
        queen_order_state="submitted",
        side=False,
        order_trig_buy_stop=False,
        order_trig_sell_stop=False,
        order_trig_sell_stop_limit=False,
        limit_price=False,
        running_close_legs=False,
        order_rules=False,
        origin_wave=False,
        wave_at_creation=False,
        assigned_wave=False,
        power_up=False,
        power_up_rangers=False,
        ticker_time_frame_origin=False,
        wave_amo=False,
        trigname=trig,
        ticker_time_frame=ticker_time_frame,
        symbol=symbol,
        star=star,
        status_q=status_q,
        portfolio_name=portfolio_name,
        exit_order_link=exit_order_link,
        client_order_id=False,
        system_recon=False,
        req_qty=False,
        filled_qty=False,
        qty_available=0,
        filled_avg_price=0,
        price_time_of_request=False,
        bid=False,
        ask=False,
        honey_gauge=False,
        macd_gauge=False,
        honey_money=False,
        sell_reason=False,
        honey_time_in_profit=0,
        cost_basis=0,
        cost_basis_current=0,
        market_value=0,
        honey=0,
        money=0,
        order=order,
        order_vars=order_vars,
        priceinfo=priceinfo,
        queen_init=False,
        revisit_trade_datetime=datetime.now(est),
        datetime=datetime.now(est),
        borrowed_funds=False,
        ready_buy=None,
        date_mark = datetime.now(est),
        long_short=long_short,

    ):
        # date_mark = datetime.now(est)
        if queen_init:
            qo = gen_queen_order()
            return {
                name: qo.get(name)
                for name in gen_queen_order.__code__.co_varnames
                if name not in ["order", "order_vars", "priceinfo"]
            }
        else:

            return {
                "queen_order_version": queen_order_version,
                "trading_model": trading_model,
                "queen_order_state": queen_order_state,
                "order_trig_buy_stop": True,
                "order_trig_sell_stop": False,
                "running_close_legs": False,
                "ticker_time_frame": ticker_time_frame,
                "star": star,
                "double_down_trade": order_vars.get("double_down_trade"),
                "order_trig_sell_stop_limit": order_vars.get("order_trig_sell_stop_limit"),
                "req_limit_price": order_vars.get("limit_price"),
                "limit_price": order_vars.get("limit_price"),
                "order_rules": order_vars.get("king_order_rules"),
                "origin_wave": order_vars.get("origin_wave"),
                "wave_at_creation": order_vars.get("wave_at_creation"),
                "power_up": order_vars.get("power_up"),
                "power_up_rangers": order_vars.get("power_up_rangers"),
                "ticker_time_frame_origin": order_vars.get("ticker_time_frame_origin"),
                "wave_amo": order_vars.get("wave_amo"),
                "sell_reason": order_vars.get("sell_reason"),
                "borrowed_funds": order_vars.get('borrowed_funds'),
                "ready_buy": order_vars.get('ready_buy'),
                "qty_order": order_vars.get('qty_order'),
                "assigned_wave": order_vars.get("wave_at_creation"),
                "trigname": trig,
                "datetime": date_mark,
                "status_q": status_q,
                "portfolio_name": portfolio_name,
                "exit_order_link": exit_order_link,
                "system_recon": False,
                "order": "alpaca",
                "client_order_id": order.get("client_order_id"),
                "side": order.get("side"),
                "ticker": order.get("symbol"),
                "symbol": order.get("symbol"),
                "req_qty": order.get("qty"),
                "qty": order.get("qty"),
                "filled_qty": order.get("filled_qty"),
                "qty_available": order.get("filled_qty"),
                "filled_avg_price": order.get("filled_avg_price"),
                "price_time_of_request": priceinfo.get("price"),
                "bid": priceinfo.get("bid"),
                "ask": priceinfo.get("ask"),
                "honey_gauge": deque([], 89),
                "macd_gauge": deque([], 89),
                "money": 0,
                "honey": 0,
                "cost_basis": 0,
                'cost_basis_current': 0,
                'market_value': market_value,
                "honey_time_in_profit": {},
                "profit_loss": 0,
                "revisit_trade_datetime": revisit_trade_datetime,
                "long_short": long_short,
            }

    if queen_init:
        # print("Queen Template Initalized")
        running_order = gen_queen_order(queen_init=True)
    elif order["side"] == "buy" or order["side"] == "sell":
        # print("create buy running order")
        running_order = gen_queen_order()
    

    return running_order


def generate_queen_buying_powers_settings(
    portfolio_name="Jq", total_dayTrade_allocation=0.5, total_longTrade_allocation=0.5
):
    return {
        portfolio_name: {
            "portfolio_name": portfolio_name,
            "total_dayTrade_allocation": total_dayTrade_allocation,
            "total_longTrade_allocation": total_longTrade_allocation,
        }
    }


def generate_queen_ticker_settings(
    ticker="SPY",
    status="active",
    portforlio_name="Jq",
    portforlio_weight=1,
    day_theme_throttle=0.33,
    long_theme_throttle=0.33,
):
    return {
        portforlio_name: {
            "portforlio_name": portforlio_name,
            "ticker": ticker,
            "status": status,
            "portforlio_weight": portforlio_weight,
            "day_theme_throttle": day_theme_throttle,
            "long_theme_throttle": long_theme_throttle,
        }
    }


def createParser_QUEEN():
    parser = argparse.ArgumentParser()
    parser.add_argument("-qcp", default="queen")
    parser.add_argument("-user", default="pollen")

    return parser

def generate_chessboards_trading_models(chessboard):
    tradingmodels = {}
    # chessboard = generate_chess_board()
    for qcp_name, chesspiece in chessboard.items():
        for ticker in chesspiece.get('tickers'):
            tradingmodels[ticker] = generate_TradingModel(ticker=ticker, theme=chesspiece.get('theme'), init=True)["MACD"][ticker]
    return tradingmodels

def star_power(stars):
    star_main = {}
    for star in stars().keys():
        if star == "1Minute_1Day":
            star_main[star] = .5
        elif star == "5Minute_5Day":
            star_main[star] = .5
        elif star == "30Minute_1Month":
            star_main[star] = .5
        elif star == "1Hour_3Month":
            star_main[star] = .5
        elif star == "2Hour_6Month":
            star_main[star] = .5
        elif star == "1Day_1Year":
            star_main[star] = .5 
        else:
            print("no way")
    
    return star_main

def return_queen_controls(stars=stars):
    chessboard = generate_chess_board()
    tradingmodels = generate_chessboards_trading_models(chessboard)
    star_powers = star_power(stars) # deprecate
    x_power = star_power(stars) # deprecate

    queen_controls_dict = {
        "theme": "nuetral",
        "last_read_app": datetime.now(est),
        "stars": stars(),
        "ticker_settings": generate_queen_ticker_settings(),
        "buying_powers": generate_queen_buying_powers_settings(),
        "symbols_stars_TradingModel": tradingmodels, # buy chessboard #
        # "symbols_stars_tradingmodel": tradingmodels,
        "power_rangers": init_PowerRangers(),
        "trigbees": {
            "buy_cross-0": "active",
            "sell_cross-0": "active",
            "ready_buy_cross": "not_active",
        },
        'use_margin': True,
        'use_margin_pct': 0, # deprecate
        
        # ticker_allocation_mapping
        'ticker_revrec_allocation_mapping' : {},

        # working
        'daytrade_risk_takes': {'frame_blocks': {'morning': 1, 'lunch': 1, 'afternoon':1},

                                'budget_type': 'star'},
        'throttle': .5,
        'x_power': x_power, # deprecate
        'star_power': star_powers, # deprecate

    }
    return queen_controls_dict


def refresh_tickers_TradingModels(QUEEN_KING, ticker, theme):
    print("update generate trading model")
    tradingmodel1 = generate_TradingModel(ticker=ticker, status='active', theme=theme)['MACD'][ticker]
    QUEEN_KING['king_controls_queen']['symbols_stars_TradingModel'][ticker] = tradingmodel1
    return QUEEN_KING


def return_Ticker_Universe():  # Return Ticker and Acct Info
    api = return_alpaca_api_keys(prod=False)["api"]
    # Initiate Code File Creation
    index_list = [
        "DJA",
        "DJI",
        "DJT",
        "DJUSCL",
        "DJU",
        "NDX",
        "IXIC",
        "IXCO",
        "INDS",
        "INSR",
        "OFIN",
        "IXTC",
        "TRAN",
        "XMI",
        "XAU",
        "HGX",
        "OSX",
        "SOX",
        "UTY",
        "OEX",
        "MID",
        "SPX",
        "SCOND",
        "SCONS",
        "SPN",
        "SPF",
        "SHLTH",
        "SINDU",
        "SINFT",
        "SMATR",
        "SREAS",
        "SUTIL",
    ]
    # index_ticker_db__dir = os.path.join(db_root, "index_tickers")

    # if os.path.exists(index_ticker_db__dir) == False:
    #     os.mkdir(index_ticker_db__dir)
    #     print("Ticker Index db Initiated")
    #     init_index_ticker(index_list, db_root, init=True)

    """ Return Index Charts & Data for All Tickers Wanted"""
    """ Return Tickers of SP500 & Nasdaq / Other Tickers"""
    # s = datetime.now()
    all_alpaca_tickers = api.list_assets()
    alpaca_symbols_dict = {}
    for n, v in enumerate(all_alpaca_tickers):
        if all_alpaca_tickers[n].status == "active" and all_alpaca_tickers[n].tradable == True and all_alpaca_tickers[n].exchange != 'CRYPTO':
            alpaca_symbols_dict[all_alpaca_tickers[n].symbol] = vars(
                all_alpaca_tickers[n]
            )

    alpaca_symbols = {k: i['_raw'] for k,i in alpaca_symbols_dict.items()}
    alpaca_symbols_df = pd.DataFrame(alpaca_symbols).T


    symbol_shortable_list = []
    t = []
    for ticker, v in alpaca_symbols_dict.items():
        if v["_raw"]["shortable"] == True:
            symbol_shortable_list.append(ticker)
        if v["_raw"]["easy_to_borrow"] == True:
            t.append(ticker)

    market_exchanges_tickers = defaultdict(list)

    for k, v in alpaca_symbols_dict.items():
        market_exchanges_tickers[v["_raw"]["exchange"]].append(k)
    # market_exchanges = ['OTC', 'NASDAQ', 'NYSE', 'ARCA', 'AMEX', 'BATS']

    # index_ticker_db = return_index_tickers(
    #     index_dir=os.path.join(db_root, "index_tickers"), ext=".csv"
    # )

    # main_index_dict = index_ticker_db[0]
    # main_symbols = index_ticker_db[1]
    # not_avail_in_alpaca = [i for i in main_symbols if i not in alpaca_symbols_dict]
    # main_symbols_full_list = [i for i in main_symbols if i in alpaca_symbols_dict]

    """ Return Index Charts & Data for All Tickers Wanted"""
    """ Return Tickers of SP500 & Nasdaq / Other Tickers"""

    return {
        "alpaca_symbols_dict": alpaca_symbols_dict,
        "all_alpaca_tickers": all_alpaca_tickers,
        "alpaca_symbols_df": alpaca_symbols_df,
    }


def get_ticker_statatistics(symbol):
    try:
        url = f"https://finance.yahoo.com/quote/{symbol}/key-statistics?p={symbol}"
        dataframes = pd.read_html(
            requests.get(url, headers={"User-agent": "Mozilla/5.0"}).text
        )
    except Exception as e:
        print(symbol, e)
    return dataframes


def init_ticker_stats__from_yahoo():
    ticker_universe = return_Ticker_Universe()
    # index_ticker_db = ticker_universe["index_ticker_db"]
    # main_index_dict = ticker_universe["main_index_dict"]
    all_alpaca_tickers = ticker_universe.get("alpaca_symbols_dict")
    all_alpaca_tickers = list(all_alpaca_tickers.keys())
    # not_avail_in_alpaca = ticker_universe["not_avail_in_alpaca"]
    s = datetime.now(est)
    db_return = {}
    for symbol in tqdm(all_alpaca_tickers):
        try:
            db_return[symbol] = get_ticker_statatistics(symbol)
        except Exception as e:
            print(symbol, e)
    e = datetime.now(est)
    time_delta = (e-s)
    st.write(f'{time_delta} __ total Seconds: {time_delta.total_seconds()}')

    yahoo_stats_bee = os.path.join(db_root, "yahoo_stats_bee.pkl")

    PickleData(yahoo_stats_bee, db_return)

    return db_return


def logging_log_message(
    log_type="info", msg="default", error="none", origin_func="default", ticker="false"
):
    if log_type == "error":
        return {"msg": msg, "error": error, "origin_func": origin_func, "ticker": ticker}
    if log_type == "critical":
        return {"msg": msg, "error": error, "origin_func": origin_func, "ticker": ticker}


""" WAVE ANALYSIS"""

def return_Best_Waves(df, rankname="maxprofit", top=False):
    if top:
        df = df.sort_values(rankname)
        return df.tail(top)
    else:
        df = df.sort_values(rankname)
        return df


def analyze_waves(STORY_bee, ticker_time_frame=False, top_waves=8):
    def process_trigbee(wave_series):
        try:
            upwave_dict = [wave_data for (k, wave_data) in wave_series.items() if k != "0"]
            df = pd.DataFrame(upwave_dict)
            df["winners_n"] = np.where(df["maxprofit"] > 0, 1, 0)
            df["losers_n"] = np.where(df["maxprofit"] < 0, 1, 0)
            df["winners"] = np.where(df["maxprofit"] > 0, "winner", "loser")
            df_token = df[df['winners']=='winner']
            groups = (
                df.groupby(["ticker_time_frame", "wave_blocktime",]) # "end_tier_macd", "end_tier_vwap", "end_tier_rsi_ema"])
                .agg(
                    {
                        "winners_n": "sum",
                        "losers_n": "sum",
                        "maxprofit": "sum",
                        "length": "mean",
                        "time_to_max_profit": "mean",
                        # "mxp_macd_tier": 'mean',
                        # "mxp_vwap_tier": 'mean',
                        # "mxp_rsi_tier": 'mean',
                        
                    }
                )
                .reset_index("ticker_time_frame")
            )
            
            df_return_waveup = groups.rename(
                columns={
                    "length": "avg_length",
                    "time_to_max_profit": "avg_time_to_max_profit",
                    "maxprofit": "sum_maxprofit",
                }
            )

            all_wave_count = round(len(df) / 3)
            df_bestwaves = return_Best_Waves(df=df, top=all_wave_count)
            # df_token_g = df_bestwaves.groupby(["ticker_time_frame"]).agg({'maxprofit': "median"}).reset_index("ticker_time_frame").iloc[0].get('maxprofit')
            df_return_waveup['ttf_median_maxprofit_median'] = df_bestwaves.groupby(["ticker_time_frame"]).agg({'maxprofit': "median"}).reset_index("ticker_time_frame").iloc[0].get('maxprofit')
            df_return_waveup['ttf_mean_maxprofit_mean'] = df_bestwaves.groupby(["ticker_time_frame"]).agg({'maxprofit': "mean"}).reset_index("ticker_time_frame").iloc[0].get('maxprofit')

            # df_return_waveup['ttf_mean_macdtiergain_mean'] = df_bestwaves.groupby(["ticker_time_frame"]).agg({'mxp_macd_tier': "mean"}).reset_index("ticker_time_frame").iloc[0].get('mxp_macd_tier')
            # df_return_waveup['ttf_mean_vwaptiergain_mean'] = df_bestwaves.groupby(["ticker_time_frame"]).agg({'mxp_vwap_tier': "mean"}).reset_index("ticker_time_frame").iloc[0].get('mxp_vwap_tier')
            # df_return_waveup['ttf_mean_rsitiergain_mean'] = df_bestwaves.groupby(["ticker_time_frame"]).agg({'mxp_rsi_tier': "mean"}).reset_index("ticker_time_frame").iloc[0].get('mxp_rsi_tier')



            df_top3 = return_Best_Waves(df=df, top=3)
            df_return_waveup['ttf_mean_top3_maxprofit'] = df_top3.groupby(["ticker_time_frame"]).agg({'maxprofit': "mean"}).reset_index("ticker_time_frame").iloc[0].get('maxprofit')

            # show today only
            df_today_return = pd.DataFrame()
            df_today = split_today_vs_prior(df=df, timestamp="wave_start_time")["df_today"]
            daywaves_length = len(df_today)
            if daywaves_length > 0:
                if daywaves_length == 1:
                    df_day_bestwaves = return_Best_Waves(df=df_today, top=1)
                else:
                    # daywaves_length_c = sum([i for i in range(daywaves_length)]) / daywaves_length
                    df_day_bestwaves = return_Best_Waves(df=df_today, top=3)

                df_return_waveup['ttf_mean_bestday_maxprofit'] = df_day_bestwaves.groupby(["ticker_time_frame"]).agg({'maxprofit': "mean"}).reset_index("ticker_time_frame").iloc[0].get('maxprofit')
            else:
                df_return_waveup['ttf_mean_bestday_maxprofit'] = 0

            groups = (
                df_today.groupby(["ticker_time_frame", "wave_blocktime"])
                .agg(
                    {
                        "winners_n": "sum",
                        "losers_n": "sum",
                        "maxprofit": "sum",
                        "length": "mean",
                        "time_to_max_profit": "mean",
                    }
                )
                .reset_index("ticker_time_frame")
            )
            df_today_return = groups.rename(
                columns={
                    "length": "avg_length",
                    "time_to_max_profit": "avg_time_to_max_profit",
                    "maxprofit": "sum_maxprofit",
                }
            )

            return df_return_waveup, df_bestwaves, df_today_return
        except Exception as e:
            print_line_of_error(e)

    try:
        # len and profits
        groupby_agg_dict = {
            "winners_n": "sum",
            "losers_n": "sum",
            "maxprofit": "sum",
            "length": "mean",
            "time_to_max_profit": "mean",
        }

        if ticker_time_frame:
            # buy_cross-0
            wave_series = STORY_bee[ticker_time_frame]["waves"]["buy_cross-0"]
            df_return_waveup, df_bestwaves, df_waveup_today = process_trigbee(wave_series)


            # sell_cross-0
            wave_series = STORY_bee[ticker_time_frame]["waves"]["sell_cross-0"]
            df_return_wavedown, df_bestwaves_sell_cross, df_wavedown_today = process_trigbee(wave_series)


            df_best_buy__sell__waves = pd.concat(
                [df_bestwaves, df_bestwaves_sell_cross], axis=0
            )

            return {
                "df_waveup": df_return_waveup,
                "df_wavedown": df_return_wavedown,
                "df_waveup_today": df_waveup_today,
                "df_wavedown_today": df_wavedown_today,
                "df_best_buy__sell__waves": df_best_buy__sell__waves,
            }
        else:
            df_bestwaves = pd.DataFrame()
            d_return = {}  # every star and the data by grouping
            d_agg_view_return = {}  # every star and the data by grouping

            for symbol_star, data in STORY_bee.items():
                try:
                    d_return[symbol_star] = {}
                    d_agg_view_return[symbol_star] = {}

                    waves = data["waves"]
                    for trigbee, wave in waves.items():
                        if trigbee == "story":
                            continue
                        else:
                            d_wave = [
                                wave_data for (k, wave_data) in wave.items() if k != "0"
                            ]
                            df = pd.DataFrame(d_wave)
                            if len(df) > 0:
                                df["winners"] = np.where(
                                    df["maxprofit"] > 0, "winner", "loser"
                                )
                                df["winners"] = np.where(
                                    df["maxprofit"] > 0, "winner", "loser"
                                )
                                df["winners_n"] = np.where(df["maxprofit"] > 0, 1, 0)
                                df["losers_n"] = np.where(df["maxprofit"] < 0, 1, 0)

                                groups = (
                                    df.groupby(["ticker_time_frame", "wave_blocktime"])
                                    .agg(groupby_agg_dict)
                                    .reset_index("ticker_time_frame")
                                )
                                groups = groups.rename(
                                    columns={
                                        "length": "avg_length",
                                        "time_to_max_profit": "avg_time_to_max_profit",
                                        "maxprofit": "sum_maxprofit",
                                    }
                                )
                                d_return[symbol_star][trigbee] = groups

                                groups = (
                                    df.groupby(["trigbee", "wave_blocktime"])
                                    .agg(groupby_agg_dict)
                                    .reset_index()
                                )
                                groups = groups.rename(
                                    columns={
                                        "length": "avg_length",
                                        "time_to_max_profit": "avg_time_to_max_profit",
                                        "maxprofit": "sum_maxprofit",
                                    }
                                )
                                groups["ticker_time_frame"] = symbol_star
                                d_agg_view_return[symbol_star][f"{trigbee}"] = groups

                except Exception as e:
                    print_line_of_error(e)


            df_return_waveup = pd.DataFrame(d_return)
            df_agg_view_return = pd.DataFrame(d_agg_view_return)
            df_agg_view_return = df_agg_view_return.T


            return {
                "df": df_return_waveup,
                "d_agg_view_return": d_agg_view_return,
                "df_agg_view_return": df_agg_view_return,
                "df_bestwaves": df_bestwaves,
            }
    except Exception as e:
        print("universe what am I missing?")
        print_line_of_error(e)


def optimized_analyze_waves(STORY_bee, ticker_time_frame=None):

    def process_trigbee(wave_series):
        upwave_dict = [wave_data for (k, wave_data) in wave_series.items() if k != "0"]
        df = pd.DataFrame(upwave_dict)
        
        df["winners"] = np.where(df["maxprofit"] > 0, "winner", "loser")
        df["winners_n"] = np.where(df["maxprofit"] > 0, 1, 0)
        df["losers_n"] = np.where(df["maxprofit"] < 0, 1, 0)

        groups = df.groupby(["ticker_time_frame", "wave_blocktime"]).agg({
            "winners_n": "sum",
            "losers_n": "sum",
            "maxprofit": "sum",
            "length": "mean",
            "time_to_max_profit": "mean",
        }).reset_index("ticker_time_frame")

        df_return_waveup = groups.rename(columns={
            "length": "avg_length",
            "time_to_max_profit": "avg_time_to_max_profit",
            "maxprofit": "sum_maxprofit",
        })

        df_bestwaves = return_Best_Waves(df=df, top=round(len(df) / 3))
        df_return_waveup['ttf_median_maxprofit_median'] = df_bestwaves.groupby(["ticker_time_frame"]).agg({'maxprofit': "median"}).reset_index("ticker_time_frame").iloc[0].get('maxprofit')
        df_return_waveup['ttf_mean_maxprofit_mean'] = df_bestwaves.groupby(["ticker_time_frame"]).agg({'maxprofit': "mean"}).reset_index("ticker_time_frame").iloc[0].get('maxprofit')

        df_top3 = return_Best_Waves(df=df, top=3)
        df_return_waveup['ttf_mean_top3_maxprofit'] = df_top3.groupby(["ticker_time_frame"]).agg({'maxprofit': "mean"}).reset_index("ticker_time_frame").iloc[0].get('maxprofit')

        df_today = split_today_vs_prior(df=df, timestamp="wave_start_time")["df_today"]
        if len(df_today) > 0:
            df_day_bestwaves = return_Best_Waves(df=df_today, top=1 if len(df_today) == 1 else 3)
            df_return_waveup['ttf_mean_bestday_maxprofit'] = df_day_bestwaves.groupby(["ticker_time_frame"]).agg({'maxprofit': "mean"}).reset_index("ticker_time_frame").iloc[0].get('maxprofit')
        else:
            df_return_waveup['ttf_mean_bestday_maxprofit'] = 0

        return df_return_waveup, df_bestwaves, df_today

    if ticker_time_frame:
        df_return_waveup, df_return_wavedown, df_waveup_today, df_wavedown_today = [], [], [], []

        for trigbee_type in ["buy_cross-0", "sell_cross-0"]:
            wave_series = STORY_bee[ticker_time_frame]["waves"][trigbee_type]
            df_waveup, _, df_waveup_today = process_trigbee(wave_series)
            df_return_waveup.append(df_waveup)

        df_return_waveup, df_return_wavedown = tuple(df_return_waveup)
        return {
            "df_waveup": df_return_waveup,
            "df_wavedown": df_return_wavedown,
            "df_waveup_today": df_waveup_today,
            "df_wavedown_today": df_wavedown_today,
            "df_best_buy__sell__waves": pd.concat([df_return_waveup, df_return_wavedown], axis=0),
        }
    else:
        d_return, d_agg_view_return = {}, {}

        for symbol_star, data in STORY_bee.items():
            d_return[symbol_star], d_agg_view_return[symbol_star] = {}, {}

            for trigbee, wave in data["waves"].items():
                if trigbee == "story":
                    continue

                df_wave = [wave_data for (k, wave_data) in wave.items() if k != "0"]
                df = pd.DataFrame(df_wave)

                if len(df) > 0:
                    df["winners"] = np.where(df["maxprofit"] > 0, "winner", "loser")
                    df["winners_n"] = np.where(df["maxprofit"] > 0, 1, 0)
                    df["losers_n"] = np.where(df["maxprofit"] < 0, 1, 0)

                    groups = df.groupby(["ticker_time_frame", "wave_blocktime"]).agg({
                        "winners_n": "sum",
                        "losers_n": "sum",
                        "maxprofit": "sum",
                        "length": "mean",
                        "time_to_max_profit": "mean",
                    }).reset_index("ticker_time_frame")
                    groups = groups.rename(columns={
                        "length": "avg_length",
                        "time_to_max_profit": "avg_time_to_max_profit",
                        "maxprofit": "sum_maxprofit",
                    })

                    d_return[symbol_star][trigbee] = groups

                    groups = df.groupby(["trigbee", "wave_blocktime"]).agg({
                        "winners_n": "sum",
                        "losers_n": "sum",
                        "maxprofit": "sum",
                        "length": "mean",
                        "time_to_max_profit": "mean",
                    }).reset_index()
                    groups = groups.rename(columns={
                        "length": "avg_length",
                        "time_to_max_profit": "avg_time_to_max_profit",
                        "maxprofit": "sum_maxprofit",
                    })
                    groups["ticker_time_frame"] = symbol_star
                    d_agg_view_return[symbol_star][trigbee] = groups

        df_return_waveup = pd.DataFrame(d_return)
        df_agg_view_return = pd.DataFrame(d_agg_view_return).T

        return {
            "df": df_return_waveup,
            "d_agg_view_return": d_agg_view_return,
            "df_agg_view_return": df_agg_view_return,
            "df_bestwaves": pd.DataFrame(),  # Placeholder for df_bestwaves since it's not available in the non-ticker_time_frame case
        }


def model_wave_results(STORY_bee):
    try:
        return_results = {}
        dict_list_ttf = analyze_waves(STORY_bee, ticker_time_frame=False)['d_agg_view_return']        

        ticker_list = set([i.split("_")[0] for i in dict_list_ttf.keys()])
        for ticker_option in ticker_list:
        
            for trigbee in dict_list_ttf[list(dict_list_ttf.keys())[0]]:
                
                ticker_selection = {k: v for k, v in dict_list_ttf.items() if ticker_option in k}
                buys = [data[trigbee] for k, data in ticker_selection.items()]
                df_trigbee_waves = pd.concat(buys, axis=0)
                col_view = ['ticker_time_frame'] + [i for i in df_trigbee_waves.columns if i not in 'ticker_time_frame']
                df_trigbee_waves = df_trigbee_waves[col_view]
                color = 'Green' if 'buy' in trigbee else 'Red'

                t_winners = sum(df_trigbee_waves['winners_n'])
                t_losers = sum(df_trigbee_waves['losers_n'])
                total_waves = t_winners + t_losers
                win_pct = 100 * round(t_winners / total_waves, 2)

                t_maxprofits = sum(df_trigbee_waves['sum_maxprofit'])

                return_results[f'{ticker_option}{"_bee_"}{trigbee}'] = f'{"~Total Max Profits "}{round(t_maxprofits * 100, 2)}{"%"}{"  ~Win Pct "}{win_pct}{"%"}{": Winners "}{t_winners}{" :: Losers "}{t_losers}'
            # df_bestwaves = analyze_waves(STORY_bee, ttframe_wave_trigbee=df_trigbee_waves['ticker_time_frame'].iloc[-1])['df_bestwaves']

        # df = pd.DataFrame(return_results.items())
        # mark_down_text(color='#C5B743', text=f'{"Trigger Bee Model Results "}')
        # st.write(df) 

        return return_results, dict_list_ttf
    
    except Exception as e:
        print_line_of_error()
        print("model calc error")

""" WAVE ANALYSIS"""



# weight the MACD tier // slice by selected tiers?
def wave_gauge(symbol, df_waves, weight_team, trading_model=False, model_eight_tier=8, wave_guage_list=['current_macd_tier', 'current_hist_tier', 'end_tier_vwap', 'end_tier_rsi_ema'], long_weight=.8, margin_weight=.8):
    try:
        # weight_team = ['w_L', 'w_S', 'w_15', 'w_30', 'w_54']
        weight__short = ['1Minute_1Day', '5Minute_5Day']
        weight__mid = ['30Minute_1Month', '1Hour_3Month']
        weight__long = ['2Hour_6Month', '1Day_1Year']
        # weight__3 = ['1Minute_1Day', '5Minute_5Day', '30Minute_1Month']
        # print(df_waves.columns)
        for ticker_time_frame in df_waves.index:
            ticker, tframe, tperiod = ticker_time_frame.split("_")
            if trading_model:
                long_weight = trading_model['stars_kings_order_rules'][f'{tframe}_{tperiod}'].get("buyingpower_allocation_LongTerm")
                margin_weight = trading_model['stars_kings_order_rules'][f'{tframe}_{tperiod}'].get("buyingpower_allocation_ShortTerm")
                
            df_waves.at[ticker_time_frame, 'w_L'] = long_weight
            df_waves.at[ticker_time_frame, 'w_S'] = margin_weight

            if f'{tframe}_{tperiod}' in weight__short:
                df_waves.at[ticker_time_frame, 'w_15'] = .89 # luck
            elif f'{tframe}_{tperiod}' in weight__mid:
                df_waves.at[ticker_time_frame, 'w_30'] = .89 # luck
            elif f'{tframe}_{tperiod}' in weight__long:
                df_waves.at[ticker_time_frame, 'w_54'] = .89 # luck
            else:
                df_waves.at[ticker_time_frame, 'w_15'] = .11 # luck
                df_waves.at[ticker_time_frame, 'w_30'] = .11 # luck
                df_waves.at[ticker_time_frame, 'w_54'] = .11 # luck

        # ttf_gauge = {}
        guage_return = {}
        df_waves = df_waves.fillna(0)
        for weight_ in weight_team:

            df_waves[f'{weight_}_weight_base'] = df_waves[weight_] * model_eight_tier
            df_waves[f'{weight_}_macd_weight_sum'] = df_waves[weight_] * df_waves['current_macd_tier']
            df_waves[f'{weight_}_hist_weight_sum'] = df_waves[weight_] * df_waves['current_hist_tier']
            df_waves[f'{weight_}_vwap_weight_sum'] = df_waves[weight_] * df_waves['end_tier_vwap'] ## skip out on OLD tickers that haven't been refreshed
            df_waves[f'{weight_}_rsi_weight_sum'] = df_waves[weight_] * df_waves['end_tier_rsi_ema']

            
            # Macd Tier Position 
            guage_return[f'{weight_}_macd_tier_position'] = sum(df_waves[f'{weight_}_macd_weight_sum']) / sum(df_waves[f'{weight_}_weight_base'])
            guage_return[f'{weight_}_hist_tier_position'] = sum(df_waves[f'{weight_}_hist_weight_sum']) / sum(df_waves[f'{weight_}_weight_base'])

            guage_return[f'{weight_}_vwap_tier_position'] = sum(df_waves[f'{weight_}_vwap_weight_sum']) / sum(df_waves[f'{weight_}_weight_base'])
            guage_return[f'{weight_}_rsi_tier_position'] = sum(df_waves[f'{weight_}_rsi_weight_sum']) / sum(df_waves[f'{weight_}_weight_base'])

        guage_return['symbol'] = symbol
        
        return guage_return, df_waves
    
    except Exception as e:
        print_line_of_error(e)
        return None


def wave_analysis_from_storyview(storyviews, trigbee='df_waveup', df_agg='df_agg'):
    df_agg_data = storyviews.get(df_agg)
    wave_analysis_data = []

    for star_n in range(len(df_agg_data)):
        df = df_agg_data.iloc[star_n][trigbee]
        df['star_avg_length'] = df['avg_length'].mean()
        df['star_avg_time_to_max_profit'] = df['avg_time_to_max_profit'].mean()
        wave_analysis_data.append(df)

    wave_analysis_df = pd.concat(wave_analysis_data)
    
    return wave_analysis_df


def story_view(STORY_bee, ticker):
    s_ = datetime.now()
    storyview = [
        "ticker_time_frame", "macd_state", "current_macd_tier", "current_hist_tier", "macd", "hist", "mac_ranger", "hist_ranger",
    ]
    ticker_items = {k: v for k, v in STORY_bee.items() if k.split("_")[0] == ticker}
    return_view = []
    return_agg_view = []

    for ttframe, conscience in ticker_items.items():
        # Perform optimized analysis of waves for the ticker
        trigbee_waves_analyzed = analyze_waves(STORY_bee, ticker_time_frame=ttframe)
        return_agg_view.append(trigbee_waves_analyzed)
        
        queen_return = {"star": ttframe}

        # Extract relevant story and wave information
        story = {k: v for k, v in conscience["story"].items() if k in storyview}
        p_story = {k: v for k, v in conscience["story"]["current_mind"].items() if k in storyview}

        # Extract last buy or sell wave based on MACD state
        last_wave_key = "buy_cross-0" if "buy" in story['macd_state'] else "sell_cross-0"
        last_wave = conscience["waves"][last_wave_key][str(len(conscience["waves"][last_wave_key]) - 1)]

        current_wave_view = {k: v for k, v in last_wave.items()}
        obj_return = {**story, **current_wave_view, **p_story}
        queen_return = {**queen_return, **obj_return}
        return_view.append(queen_return)

    df = pd.DataFrame(return_view)
    df_agg = pd.DataFrame(return_agg_view)
    
    storyviews = {"df": df, "df_agg": df_agg, 'symbol': ticker}

    if len(storyviews.get('df')) == 0:
        print(f"NO STORY FOUND FOR: {ticker}")
        return {}

    storyviews.update({'wave_analysis_up': wave_analysis_from_storyview(storyviews, trigbee='df_waveup')})
    storyviews.update({'wave_analysis_down': wave_analysis_from_storyview(storyviews, trigbee='df_wavedown')})

    return storyviews


def wave_buy__var_items(ticker_time_frame, trigbee, macd_state, ready_buy, x_buy, order_rules):
   trigbee = macd_state
   return {'ticker': ticker_time_frame.split("_")[0],
    'ticker_time_frame': ticker_time_frame,
    'system': 'app',
    # 'wave_trigger': wave_trigger,
    'request_time': datetime.now(est),
    'app_requests_id' : f'wave_buy__app_requests_id__{return_timestamp_string()}{datetime.now().microsecond}',
    'macd_state': trigbee,
    'ready_buy': ready_buy,
    'x_buy': x_buy,
    'order_rules': order_rules,
    }



def async_waveAnalysis(symbols, STORY_bee): # re-initiate for i timeframe 

    async def get_func(session, ticker, STORY_bee):
        async with session:
            try:
                story_views = story_view(STORY_bee=STORY_bee, ticker=ticker)
                # remainder of code to 
                return story_views
            except Exception as e:
                print(e)
                raise e
    
    async def main(symbols, STORY_bee):
        async with aiohttp.ClientSession() as session:
            return_list = []
            tasks = []
            # symbols = [qo['symbol'] for qo in queen_order__s]
            for ticker in set(symbols):

                tasks.append(asyncio.ensure_future(get_func(session, ticker, STORY_bee)))
            original_pokemon = await asyncio.gather(*tasks)
            for pokemon in original_pokemon:
                return_list.append(pokemon)
            
            return return_list

    list_return = asyncio.run(main(symbols, STORY_bee))

    return list_return


def wave_analysis__storybee_model(QUEEN_KING, STORY_bee, symbols):
    s = datetime.now()
    symbols=async_waveAnalysis(symbols, STORY_bee)
    print("waves analysis: ", (datetime.now()-s).total_seconds())

    weight_team = ['w_L', 'w_S', 'w_15', 'w_30', 'w_54'] # WORKERBEE put weight team in revrec or stars in hive?
    df_waveview = pd.DataFrame()
    df_storyview = pd.DataFrame()
    df_storyview_down = pd.DataFrame()
    df_storyguage = pd.DataFrame()
    story_guages_view = []
    s = datetime.now()

    for story_views in symbols:
        # try:
        # story_views = story_view(STORY_bee=STORY_bee, ticker=story_views)
        if story_views:
            symbol = story_views.get('symbol')
            # story views wave analysis
            
            wave_analysis = story_views.get("wave_analysis_up").reset_index()
            waves = wave_analysis.set_index("ticker_time_frame")
            df_storyview = pd.concat([df_storyview, waves])

            wave_analysis = story_views.get("wave_analysis_down").reset_index()
            waves = wave_analysis.set_index("ticker_time_frame")
            df_storyview_down = pd.concat([df_storyview_down, waves])

            # wave_guage__story()
            df = story_views.get('df')
            df = df.set_index('star')
            df.at[f'{symbol}_{"1Minute_1Day"}', 'sort'] = 1
            df.at[f'{symbol}_{"5Minute_5Day"}', 'sort'] = 2
            df.at[f'{symbol}_{"30Minute_1Month"}', 'sort'] = 3
            df.at[f'{symbol}_{"1Hour_3Month"}', 'sort'] = 4
            df.at[f'{symbol}_{"2Hour_6Month"}', 'sort'] = 5
            df.at[f'{symbol}_{"1Day_1Year"}', 'sort'] = 6
            df = df.sort_values('sort')
            df_waveview = pd.concat([df_waveview, df])
            
            
            trading_model = QUEEN_KING['king_controls_queen']['symbols_stars_TradingModel'].get(symbol)
            if trading_model == None:
                # print(f"{symbol} no tm using default")
                trading_model = QUEEN_KING['king_controls_queen']['symbols_stars_TradingModel'].get("SPY")
            story_guages, delme = wave_gauge(symbol=symbol, df_waves=df, trading_model=trading_model, weight_team=weight_team)
            if story_guages:
                story_guages_view.append(story_guages)
                df_storyguage = pd.DataFrame(story_guages_view)

                # Trinity 
                for w_t in weight_team:
                    df_storyguage[f'trinity_{w_t}'] = (df_storyguage[f'{w_t}_macd_tier_position'] + df_storyguage[f'{w_t}_vwap_tier_position'] + df_storyguage[f'{w_t}_rsi_tier_position']) / 3


    # print("waves analysis: ", (datetime.now()-s).total_seconds())

    STORY_bee_wave_analysis = {'df_storyview': df_storyview, 
            'df_storyguage': df_storyguage, 
            'df_waveview': df_waveview, 
            'df_storyview_down': df_storyview_down
    }

    return STORY_bee_wave_analysis


def queen_orders_view(
    QUEEN, queen_order_state, cols_to_view=False, return_all_cols=False, return_str=True
):
    if cols_to_view:
        col_view = col_view
    else:
        col_view = [
            "honey",
            "money",
            "symbol",
            "ticker_time_frame",
            "trigname",
            "datetime",
            "honey_time_in_profit",
            "filled_qty",
            "qty_available",
            "filled_avg_price",
            "limit_price",
            "cost_basis",
            "wave_amo",
            "status_q",
            "client_order_id",
            "origin_wave",
            "wave_at_creation",
            "power_up",
            "sell_reason",
            "exit_order_link",
            "queen_order_state",
            "order_rules",
            "order_trig_sell_stop",
            "side",
        ]
    if len(QUEEN["queen_orders"]) > 0:
        df = QUEEN["queen_orders"]
        df = df[df["queen_order_state"].isin(queen_order_state)].copy()

        if len(df) > 0:
            col_view = [i for i in col_view if i in df.columns]
            df_return = df[col_view].copy()
        else:
            df_return = df

        if return_all_cols and len(df_return) > 0:
            all_cols = col_view + [i for i in df.columns.tolist() if i not in col_view]
            df_return = df[all_cols].copy()

        if return_str:
            df_return = df_return.astype(str)

        return {"df": df_return}
    else:
        return {"df": pd.DataFrame()}


def init_PowerRangers(ranger_dimensions=False):
    # ranger = '1Minute_1Day'
    # stars = ['1Minute_1Day', '5Minute_5Day', '30Minute_1Month', '1Hour_3Month', '2Hour_6Month', '1Day_1Year']
    # trigbees = ['buy_wave', 'sell_wave']
    # theme_list = ['nuetral', 'strong']
    # colors = ['red', 'blue', 'pink', 'yellow', 'white', 'green', 'orange', 'purple', 'black']
    # bee_ranger_tiers = 9

    # BUY_Cross
    # When 1M macd tier in range (-7, -5) + 50% : Red // Sell :: 1%
    # When 1M macd tier in range (-5, -3) + 40% : Blue // Sell :: 1%
    # When 1M macd tier in range (-3, -2) + 25% : Pink // Sell :: 1%
    # When 1M macd tier in range (-2, -1) + 10% : Yellow // Sell :: 1%
    # When 1M macd tier in range (-1, 1) + 1% : White // Sell :: 1%
    # When 1M macd tier in range (1, 2) + 1% : Green // Sell :: 1%
    # When 1M macd tier in range (2, 3) + 1% : orange // Sell :: 25%
    # When 1M macd tier in range (3, 5) + 1% : purple // Sell :: 40%
    # When 1M macd tier in range (5, 7) + 1% : Black // Sell :: 50%

    if ranger_dimensions:
        stars = ranger_dimensions[
            "stars"
        ]  # = ['1Minute_1Day', '5Minute_5Day', '30Minute_1Month', '1Hour_3Month', '2Hour_6Month', '1Day_1Year']
        trigbees = ranger_dimensions["trigbees"]  # = ['buy_wave', 'sell_wave']
        theme_list = ranger_dimensions["theme_list"]  # theme_list = ['nuetral', 'strong']
        colors = ranger_dimensions[
            "colors"
        ]  # colors = ['red', 'blue', 'pink', 'yellow', 'white', 'green', 'orange', 'purple', 'black']
        wave_types = ranger_dimensions["wave_types"]
        # bee_ranger_tiers = 9
        ranger_init = ranger_dimensions["ranger_init"]
    else:
        wave_types = ["mac_ranger", "hist_ranger"]
        stars = [
            "1Minute_1Day",
            "5Minute_5Day",
            "30Minute_1Month",
            "1Hour_3Month",
            "2Hour_6Month",
            "1Day_1Year",
        ]
        trigbees = ["buy_wave", "sell_wave"]
        theme_list = ["nuetral", "strong"]
        colors = [
            "red",
            "blue",
            "pink",
            "yellow",
            "white",
            "green",
            "orange",
            "purple",
            "black",
        ]

        ## FEAT REQUEST: adjust upstream to include universe
        ranger_init = {
            "mac_ranger": {
                "buy_wave": {
                    "nuetral": {
                        "red": 0.05,
                        "blue": 0.04,
                        "pink": 0.025,
                        "yellow": 0.01,
                        "white": 0.01,
                        "green": 0.01,
                        "orange": 0.01,
                        "purple": 0.01,
                        "black": 0.001,
                    },
                    "strong": {
                        "red": 0.05,
                        "blue": 0.04,
                        "pink": 0.025,
                        "yellow": 0.01,
                        "white": 0.01,
                        "green": 0.01,
                        "orange": 0.01,
                        "purple": 0.01,
                        "black": 0.001,
                    },
                },
                "sell_wave": {
                    "nuetral": {
                        "red": 0.001,
                        "blue": 0.001,
                        "pink": 0.01,
                        "yellow": 0.01,
                        "white": 0.03,
                        "green": 0.01,
                        "orange": 0.01,
                        "purple": 0.01,
                        "black": 0.01,
                    },
                    "strong": {
                        "red": 0.05,
                        "blue": 0.04,
                        "pink": 0.025,
                        "yellow": 0.01,
                        "white": 0.01,
                        "green": 0.01,
                        "orange": 0.01,
                        "purple": 0.01,
                        "black": 0.01,
                    },
                },
            },
            "hist_ranger": {
                "buy_wave": {
                    "nuetral": {
                        "red": 0.05,
                        "blue": 0.04,
                        "pink": 0.025,
                        "yellow": 0.01,
                        "white": 0.01,
                        "green": 0.01,
                        "orange": 0.01,
                        "purple": 0.01,
                        "black": 0.001,
                    },
                    "strong": {
                        "red": 0.05,
                        "blue": 0.04,
                        "pink": 0.025,
                        "yellow": 0.01,
                        "white": 0.01,
                        "green": 0.01,
                        "orange": 0.01,
                        "purple": 0.01,
                        "black": 0.001,
                    },
                },
                "sell_wave": {
                    "nuetral": {
                        "red": 0.001,
                        "blue": 0.001,
                        "pink": 0.01,
                        "yellow": 0.01,
                        "white": 0.03,
                        "green": 0.01,
                        "orange": 0.01,
                        "purple": 0.01,
                        "black": 0.01,
                    },
                    "strong": {
                        "red": 0.05,
                        "blue": 0.04,
                        "pink": 0.025,
                        "yellow": 0.01,
                        "white": 0.05,
                        "green": 0.01,
                        "orange": 0.01,
                        "purple": 0.01,
                        "black": 0.01,
                    },
                },
            },
        }

    r_dict = {}
    for star in stars:
        r_dict[star] = {}
        for wave_type in wave_types:
            r_dict[star][wave_type] = {}
            for trigbee in trigbees:
                r_dict[star][wave_type][trigbee] = {}
                for theme in theme_list:
                    r_dict[star][wave_type][trigbee][theme] = {}
                    for color in colors:
                        r_dict[star][wave_type][trigbee][theme][color] = ranger_init[
                            wave_type
                        ][trigbee][theme][color]

    return r_dict

def queens_heart(heart):
    heart.update({"heartbeat_time": datetime.now(est)})
    return heart


def live_sandbox__setup_switch(pq_env, switch_env=False):

    try:
        prod = pq_env.get('env')

        prod_name = (
            "LIVE"
            if prod
            else "Sandbox"
        )
        
        st.session_state["prod_name"] = prod_name
        st.session_state["production"] = prod

        if switch_env:
            if prod:
                prod = False
                st.session_state["production"] = prod
                prod_name = "Sanbox"
                st.session_state["prod_name"] = prod_name
            else:
                prod = True
                st.session_state["production"] = prod
                prod_name = "LIVE"
                st.session_state["prod_name"] = prod_name
            # save
            pq_env.update({'env': prod})
            PickleData(pq_env.get('source'), pq_env)

        return prod
    except Exception as e:
        print_line_of_error("live sb switch")


def init_clientUser_dbroot(client_username, force_db_root=False, queenKING=False):

    if force_db_root:
        db_root = os.path.join(hive_master_root(), "db")
    # elif client_username in ['stefanstapinski@gmail.com']:  ## admin
    #     db_root = os.path.join(hive_master_root(), "db")
    else:
        db_root = return_db_root(client_username=client_username)
        if os.path.exists(db_root) == False:
            os.mkdir(db_root)
            os.mkdir(os.path.join(db_root, "logs"))
    
    if queenKING:
        st.session_state['db_root'] = db_root
        st.session_state["admin"] = True if client_username == "stefanstapinski@gmail.com" else False

    return db_root


def init_swarm_dbs(prod, init=False):
    db_swarm_root=os.path.join(hive_master_root(), 'db')
    envs = '_Sandbox' if prod == False else ''
    dbs = ['KING', 'QUEEN', 'BISHOP', 'KNIGHT']
    db_local_path = {}
    for db_name in dbs:
        pathname = os.path.join(db_swarm_root, f'{db_name}{envs}.pkl')
        if init:
            if os.path.exists(pathname) == False:
                print(db_name)
                if db_name == 'KING':
                    data = init_KING()
                elif db_name == 'QUEEN':
                    data = init_queen('queen')
                else:
                    data = {}
                PickleData(pathname, data, console=True)
        
        db_local_path[db_name] = pathname
    
    return db_local_path
            

def init_pollen_dbs(db_root, prod, queens_chess_piece='queen', queenKING=False, init=False):
    
    def init_queen_orders(pickle_file):
        db = {}
        db["queen_orders"] = pd.DataFrame([create_QueenOrderBee(queen_init=True)])
        PickleData(pickle_file=pickle_file, data_to_store=db)

        return True


    # WORKERBEE don't check if file exists, only check on init
    if prod:
        # print("My Queen Production")
        # main_orders_file = os.path.join(db_root, 'main_orders.csv')
        PB_QUEEN_Pickle = os.path.join(db_root, f'{queens_chess_piece}{".pkl"}')
        PB_KING_Pickle = os.path.join(db_root, f'{"KING"}{".pkl"}')
        PB_App_Pickle = os.path.join(db_root, f'{queens_chess_piece}{"_App_"}{".pkl"}')
        PB_Orders_Pickle = os.path.join(db_root, f'{queens_chess_piece}{"_Orders_"}{".pkl"}')
        PB_queen_Archives_Pickle = os.path.join(db_root, f'{queens_chess_piece}{"_Archives_"}{".pkl"}')
        PB_QUEENsHeart_PICKLE = os.path.join(db_root, f'{queens_chess_piece}{"_QUEENsHeart_"}{".pkl"}')
        PB_RevRec_PICKLE = os.path.join(db_root, f'{queens_chess_piece}{"_revrec"}{".pkl"}')
        PB_account_info_PICKLE = os.path.join(db_root, f'{queens_chess_piece}{"_account_info"}{".pkl"}')
        PB_broker_PICKLE = os.path.join(db_root, f'{queens_chess_piece}{"_broker"}{".pkl"}')
        PB_Orders_FINAL_Pickle = os.path.join(db_root, f'{queens_chess_piece}{"_Orders_FINAL"}{".pkl"}')
        PB_Wave_Analysis_Pickle = os.path.join(db_root, f'{queens_chess_piece}{"_Wave_Analysis"}{".pkl"}')
    else:
        # print("My Queen Sandbox")
        PB_QUEEN_Pickle = os.path.join(db_root, f'{queens_chess_piece}{"_sandbox"}{".pkl"}')
        PB_KING_Pickle = os.path.join(db_root, f'{"KING"}{"_sandbox"}{".pkl"}')
        PB_App_Pickle = os.path.join(db_root, f'{queens_chess_piece}{"_App_"}{"_sandbox"}{".pkl"}')
        PB_Orders_Pickle = os.path.join(db_root, f'{queens_chess_piece}{"_Orders_"}{"_sandbox"}{".pkl"}')
        PB_queen_Archives_Pickle = os.path.join(db_root, f'{queens_chess_piece}{"_Archives_"}{"_sandbox"}{".pkl"}')
        PB_QUEENsHeart_PICKLE = os.path.join(db_root, f'{queens_chess_piece}{"_QUEENsHeart_"}{"_sandbox"}{".pkl"}')
        PB_RevRec_PICKLE = os.path.join(db_root, f'{queens_chess_piece}{"_revrec"}{"_sandbox"}{".pkl"}')
        PB_account_info_PICKLE = os.path.join(db_root, f'{queens_chess_piece}{"_account_info"}{"_sandbox"}{".pkl"}')
        PB_broker_PICKLE = os.path.join(db_root, f'{queens_chess_piece}{"_broker"}{"_sandbox"}{".pkl"}')
        PB_Orders_FINAL_Pickle = os.path.join(db_root, f'{queens_chess_piece}{"_Orders_FINAL"}{"_sandbox"}{".pkl"}')
        PB_Wave_Analysis_Pickle = os.path.join(db_root, f'{queens_chess_piece}{"_Wave_Analysis"}{"_sandbox"}{".pkl"}')

    if init:
        if os.path.exists(PB_Wave_Analysis_Pickle) == False:
            print("Init PB_Wave_Analysis_Pickle")
            PickleData(PB_Wave_Analysis_Pickle, {})

        if os.path.exists(PB_broker_PICKLE) == False:
            print("Init PB_broker_PICKLE")
            PickleData(PB_broker_PICKLE, {'broker_orders': pd.DataFrame()})

        if os.path.exists(PB_account_info_PICKLE) == False:
            print("Init PB_account_info_PICKLE")
            PickleData(PB_account_info_PICKLE, {'account_info': {}})

        if os.path.exists(PB_RevRec_PICKLE) == False:
            print("Init PB_RevRec_PICKLE")
            PickleData(PB_RevRec_PICKLE, {'revrec': {}})

        if os.path.exists(PB_QUEENsHeart_PICKLE) == False:
            print("Init PB_QUEENsHeart_PICKLE")
            heart = {"heartbeat_time": datetime.now(est)}
            PickleData(pickle_file=PB_QUEENsHeart_PICKLE, data_to_store=queens_heart(heart))

        if os.path.exists(PB_queen_Archives_Pickle) == False:
            print("Init queen archives")
            queens_archived = {"queens": [{"queen_id": 0}]}
            PickleData(pickle_file=PB_queen_Archives_Pickle, data_to_store=queens_archived)

        if os.path.exists(PB_QUEEN_Pickle) == False:
            print("You Need a Queen")
            queens_archived = ReadPickleData(pickle_file=PB_queen_Archives_Pickle)
            l = len(queens_archived["queens"])
            QUEEN = init_queen(queens_chess_piece=queens_chess_piece)
            QUEEN["id"] = f'{"V1"}{"__"}{l}'
            queens_archived["queens"].append({"queen_id": QUEEN["id"]})
            PickleData(pickle_file=PB_queen_Archives_Pickle, data_to_store=queens_archived)

            PickleData(pickle_file=PB_QUEEN_Pickle, data_to_store=QUEEN)
            logging.info(("queen created", timestamp_string()))

        if os.path.exists(PB_App_Pickle) == False:
            print("You Need an QueenApp")
            init_app(pickle_file=PB_App_Pickle)

        if os.path.exists(PB_Orders_Pickle) == False:
            print("You Need an QueenOrders")
            init_queen_orders(pickle_file=PB_Orders_Pickle)

        if os.path.exists(PB_Orders_FINAL_Pickle) == False:
            print("You Need an QueenOrders FINAL")
            init_queen_orders(pickle_file=PB_Orders_FINAL_Pickle)

        if os.path.exists(PB_KING_Pickle) == False:
            print("You Need a King")
            KING = init_KING()
            PickleData(pickle_file=PB_KING_Pickle, data_to_store=KING)


    if queenKING:
        st.session_state["PB_QUEEN_Pickle"] = PB_QUEEN_Pickle
        st.session_state["PB_App_Pickle"] = PB_App_Pickle
        st.session_state["PB_Orders_Pickle"] = PB_Orders_Pickle
        st.session_state["PB_queen_Archives_Pickle"] = PB_queen_Archives_Pickle
        st.session_state["PB_QUEENsHeart_PICKLE"] = PB_QUEENsHeart_PICKLE
        st.session_state["PB_KING_Pickle"] = PB_KING_Pickle
        st.session_state["PB_RevRec_PICKLE"] = PB_RevRec_PICKLE
        st.session_state["PB_account_info_PICKLE"] = PB_account_info_PICKLE
        st.session_state["PB_broker_PICKLE"] = PB_broker_PICKLE
        st.session_state["PB_Orders_FINAL_Pickle"] = PB_Orders_FINAL_Pickle


    return {
        "PB_QUEEN_Pickle": PB_QUEEN_Pickle,
        "PB_App_Pickle": PB_App_Pickle,
        "PB_Orders_Pickle": PB_Orders_Pickle,
        "PB_queen_Archives_Pickle": PB_queen_Archives_Pickle,
        "PB_QUEENsHeart_PICKLE": PB_QUEENsHeart_PICKLE,
        "PB_KING_Pickle": PB_KING_Pickle,
        "PB_RevRec_PICKLE": PB_RevRec_PICKLE,
        "PB_account_info_PICKLE": PB_account_info_PICKLE,
        "PB_broker_PICKLE": PB_broker_PICKLE,
        "PB_Orders_FINAL_Pickle": PB_Orders_FINAL_Pickle,
        "PB_Wave_Analysis_Pickle": PB_Wave_Analysis_Pickle,
    }


def setup_instance(client_username, switch_env, force_db_root, queenKING, prod=None, init=False):
    # init_clientUser_dbroot(client_user, client_useremail, admin_permission_list, force_db_root=False)
    try:
        db_root = init_clientUser_dbroot(client_username=client_username, force_db_root=force_db_root, queenKING=queenKING)  # main_root = os.getcwd() // # db_root = os.path.join(main_root, 'db')
        if prod is not None:
            init_pollen_dbs(db_root=db_root, prod=prod, queens_chess_piece='queen', queenKING=queenKING, init=init)
            return prod
        else:
            # Ensure Environment
            PB_env_PICKLE = os.path.join(db_root, f'{"queen_king"}{"_env"}{".pkl"}')
            if os.path.exists(PB_env_PICKLE) == False:
                PickleData(PB_env_PICKLE, {'source': PB_env_PICKLE,'env': False})
            
            pq_env = ReadPickleData(PB_env_PICKLE)
            prod = live_sandbox__setup_switch(pq_env, switch_env)
            
            init_pollen_dbs(db_root=db_root, prod=prod, queens_chess_piece='queen', queenKING=queenKING, init=init)
            
            st.session_state['prod'] = prod
            st.session_state['client_user'] = client_username
            return prod
    except Exception as e:
        print_line_of_error("setup instance")



def send_email(
    recipient="stapinski89@gmail.com",
    subject="you forgot a subject",
    body="you forgot to same something",
):
    # Define email sender and receiver
    pollenq_gmail = os.environ.get("pollenq_gmail")
    pollenq_gmail_app_pw = os.environ.get("pollenq_gmail_app_pw")

    em = EmailMessage()
    em["From"] = pollenq_gmail
    em["To"] = recipient
    em["Subject"] = subject
    em.set_content(body)

    # Add SSL layer of security
    context = ssl.create_default_context()

    # Log in and send the email
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as smtp:
        smtp.login(pollenq_gmail, pollenq_gmail_app_pw)
        smtp.sendmail(pollenq_gmail, recipient, em.as_string())

    return True


##################################################
##################################################
################ NOT IN USE ######################
##################################################



def datestr_UTC_to_EST(date_string, return_string=False):
    # In [94]: date_string
    # Out[94]: '2022-03-11T19:41:50.649448Z'
    # In [101]: date_string[:19]
    # Out[101]: '2022-03-11T19:41:50'
    d = datetime.fromisoformat(date_string[:19])
    j = d.replace(tzinfo=datetime.timezone.utc)
    fmt = "%Y-%m-%dT%H:%M:%S"
    if return_string:
        est_date = j.astimezone(pytz.timezone("US/Eastern")).strftime(fmt)
    else:
        est_date = j.astimezone(pytz.timezone("US/Eastern"))

    return est_date


def convert_nano_utc_timestamp_to_est_datetime(digit_trc_time):
    digit_trc_time = 1644523144856422000
    digit_trc_time = 1656785012.538478
    dt = datetime.utcfromtimestamp(digit_trc_time // 1000000000)  # 9 zeros
    dt = dt.strftime("%Y-%m-%d %H:%M:%S")
    return dt


def read_wiki_index():
    table = pd.read_html("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")
    df = table[0]
    # sp500 = df['Symbol'].tolist()
    # df.to_csv('S&P500-Info.csv')
    # df.to_csv("S&P500-Symbols.csv", columns=['Symbol'])
    return df



"""##################REFERENCEs############################"""
#     """ Return Index Charts & Data for All Tickers Wanted"""
#     """ Return Tickers of SP500 & Nasdaq / Other Tickers"""

#     all_alpaca_tickers = api.list_assets()
#     alpaca_symbols_dict = {}
#     for n, v in enumerate(all_alpaca_tickers):
#         if all_alpaca_tickers[n].status == 'active':
#             alpaca_symbols_dict[all_alpaca_tickers[n].symbol] = vars(all_alpaca_tickers[n])

#     symbol_shortable_list = []
#     easy_to_borrow_list = []
#     for ticker, v in alpaca_symbols_dict.items():
#         if v['_raw']['shortable'] == True:
#             symbol_shortable_list.append(ticker)
#         if v['_raw']['easy_to_borrow'] == True:
#             easy_to_borrow_list.append(ticker)

#     # alpaca_symbols_dict[list(alpaca_symbols_dict.keys())[100]]

#     market_exchanges_tickers = defaultdict(list)
#     for k, v in alpaca_symbols_dict.items():
#         market_exchanges_tickers[v['_raw']['exchange']].append(k)
#     # market_exchanges = ['OTC', 'NASDAQ', 'NYSE', 'ARCA', 'AMEX', 'BATS']


#     main_index_dict = index_ticker_db[0]
#     main_symbols_full_list = index_ticker_db[1]
#     not_avail_in_alpaca =[i for i in main_symbols_full_list if i not in alpaca_symbols_dict]
#     main_symbols_full_list = [i for i in main_symbols_full_list if i in alpaca_symbols_dict]

#     LongTerm_symbols = ['AAPL', 'GOOGL', 'MFST', 'VIT', 'HD', 'WMT', 'MOOD', 'LIT', 'SPXL', 'TQQQ']


#     index_ticker_db = return_index_tickers(index_dir=os.path.join(db_root, 'index_tickers'), ext='.csv')

#     """ Return Index Charts & Data for All Tickers Wanted"""
#     """ Return Tickers of SP500 & Nasdaq / Other Tickers"""
