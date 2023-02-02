import argparse
import logging
import os
import pickle
import smtplib
import ssl
import sys
import time
from collections import defaultdict, deque

# import datetime
from datetime import datetime, timedelta
from email.message import EmailMessage
from typing import Callable

import alpaca_trade_api as tradeapi
import ipdb
import numpy as np
import pandas as pd
import pytz
import requests
import streamlit as st
from alpaca_trade_api.rest import URL
from alpaca_trade_api.rest_async import AsyncRest
from dotenv import load_dotenv
from scipy import stats
from stocksymbol import StockSymbol
from tqdm import tqdm

from chess_piece.app_hive import init_client_user_secrets
from chess_piece.king import PickleData, ReadPickleData, hive_master_root, local__filepaths_misc
load_dotenv(os.path.join(hive_master_root(), ".env"))

MISC = local__filepaths_misc()
mainpage_bee_png = MISC['mainpage_bee_png']


# _locale._getdefaultlocale = (lambda *args: ['en_US', 'UTF-8'])

est = pytz.timezone("America/New_York")
utc = pytz.timezone("UTC")

queens_chess_piece = os.path.basename(__file__)

scriptname = os.path.basename(__file__)
prod = False if "sandbox" in scriptname else True

main_root = hive_master_root()  # os.getcwd()
db_root = os.path.join(main_root, "db")

"""# Dates """
current_day = datetime.now(est).day
current_month = datetime.now(est).month
current_year = datetime.now(est).year


def init_logging(queens_chess_piece, db_root, prod):
    log_dir = os.path.join(db_root, "logs")
    log_dir_logs = os.path.join(log_dir, "logs")

    if os.path.exists(log_dir) == False:
        os.mkdir(log_dir)
    if os.path.exists(log_dir_logs) == False:
        os.mkdir(log_dir_logs)

    if prod:
        log_name = f'{"log_"}{queens_chess_piece}{".log"}'
    else:
        log_name = f'{"log_"}{queens_chess_piece}{"_sandbox_"}{".log"}'

    log_file = os.path.join(log_dir, log_name)
    # print("logging",log_file)
    logging.basicConfig(
        filename=log_file,
        filemode="a",
        format="%(asctime)s:%(name)s:%(levelname)s: %(message)s",
        datefmt="%m/%d/%Y %I:%M:%S %p",
        level=logging.INFO,
        force=True,
    )

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
MACD_WORLDS = {
    "crypto": {
        "macd": {
            "1Minute": 10,
            "5Minute": 10,
            "30Minute": 20,
            "1Hour": 50,
            "2Hour": 50,
            "1Day": 50,
        },
        "hist": {
            "1Minute": 1,
            "5Minute": 1,
            "30Minute": 5,
            "1Hour": 5,
            "2Hour": 10,
            "1Day": 10,
        },
    },
    "default": {
        "macd": {
            "1Minute": 1,
            "5Minute": 1,
            "30Minute": 2,
            "1Hour": 5,
            "2Hour": 5,
            "1Day": 5,
        },
        "hist": {
            "1Minute": 1,
            "5Minute": 1,
            "30Minute": 2,
            "1Hour": 5,
            "2Hour": 5,
            "1Day": 5,
        },
    },
}


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
    # ipdb.set_trace()
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

    # ipdb.set_trace()
    prod_keys_confirmed = QUEEN_KING["users_secrets"]["prod_keys_confirmed"]
    sandbox_keys_confirmed = QUEEN_KING["users_secrets"]["sandbox_keys_confirmed"]
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
        return return_alpaca_api_keys(prod=False)["api"]


def hive_dates(api):
    current_date = datetime.now(est).strftime("%Y-%m-%d")
    trading_days = api.get_calendar()
    trading_days_df = pd.DataFrame([day._raw for day in trading_days])
    trading_days_df["date"] = pd.to_datetime(trading_days_df["date"])

    return {"trading_days": trading_days}


# def read_pollenstory(
#     db_root, dbs=["castle.pkl", "bishop.pkl", "castle_coin.pkl", "knight.pkl"]
# ):  # return combined dataframes
#     # return beeworkers data

#     pollenstory = {}
#     STORY_bee = {}
#     # KNIGHTSWORD = {}
#     # ANGEL_bee = {}
#     # db_names = []
#     for db in dbs:
#         if os.path.exists(os.path.join(db_root, db)):
#             db_name = db.split(".pkl")[0]
#             chess_piece = ReadPickleData(pickle_file=os.path.join(db_root, db))[db_name]
#             pollenstory = {**pollenstory, **chess_piece["pollenstory"]}
#             STORY_bee = {**STORY_bee, **chess_piece["conscience"]["STORY_bee"]}
#             # KNIGHTSWORD = {**KNIGHTSWORD, **chess_piece['conscience']['KNIGHTSWORD']}
#             # ANGEL_bee = {**ANGEL_bee, **chess_piece['conscience']['ANGEL_bee']}
#             # dbs_[db_name] = chess_piece
#             # db_names.append(chess_piece)

#     return {"pollenstory": pollenstory, "STORY_bee": STORY_bee}


def read_queensmind(prod, db_root):  # return active story workers
    if prod:
        QUEEN = ReadPickleData(pickle_file=os.path.join(db_root, "queen.pkl"))
        ORDERS = ReadPickleData(pickle_file=os.path.join(db_root, "queen_Orders_.pkl"))
    else:
        QUEEN = ReadPickleData(pickle_file=os.path.join(db_root, "queen_sandbox.pkl"))
        ORDERS = ReadPickleData(
            pickle_file=os.path.join(db_root, "queen_Orders__sandbox.pkl")
        )

    return {"queen": QUEEN, "orders": ORDERS}


def init_symbols_db():
    ticker_universe = return_Ticker_Universe()
    index_ticker_db = ticker_universe["index_ticker_db"]
    main_index_dict = ticker_universe["main_index_dict"]
    main_symbols_full_list = ticker_universe["main_symbols_full_list"]
    not_avail_in_alpaca = ticker_universe["not_avail_in_alpaca"]
    main_tale = pd.DataFrame(main_symbols_full_list)
    symbols_db = {"main_table": main_tale, "ticker_universe": ticker_universe}

    return symbols_db


def init_QUEEN(queens_chess_piece, swarmQUEEN=False):
    ticker_universe = return_Ticker_Universe()
    index_ticker_db = ticker_universe["index_ticker_db"]
    main_index_dict = ticker_universe["main_index_dict"]
    main_symbols_full_list = ticker_universe["main_symbols_full_list"]
    not_avail_in_alpaca = ticker_universe["not_avail_in_alpaca"]
    if swarmQUEEN:
        QUEEN = {  # The Queens Mind
            "init_id": f'{"queen"}{"_"}{return_timestamp_string()}',
            "prod": "",
            "source": "na",
            "last_modified": datetime.now(est),
            "command_conscience": {},
            "queen_orders": pd.DataFrame([create_QueenOrderBee(queen_init=True)]),
            "portfolios": {"Jq": {"total_investment": 0, "currnet_value": 0}},
            "heartbeat": {
                "active_tickerStars": {},
                "available_tickers": [],
                "active_tickers": [],
                "available_triggerbees": [],
            },
            "queens_messages": {},
            "kings_order_rules": {},
            "queen_controls": return_queen_controls(stars),
            "symbol_universe": {
                "index_ticker_db": index_ticker_db,
                "main_index_dict": main_index_dict,
                "main_symbols_full_list": main_symbols_full_list,
                "not_avail_in_alpaca": not_avail_in_alpaca,
            },
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
                "pawns": {
                    "MACD_fast_slow_smooth": {"fast": 12, "slow": 26, "smooth": 9},
                    "tickers": main_symbols_full_list[:100],
                    "stars": stars(),
                },
            },
            # 'auth_users': {'stefanstapinski@gmail.com': {}, 'stevenweaver8@gmail.com': {}},
            "errors": {},
            "client_order_ids_qgen": [],
            "app_requests__bucket": [],
            # 'triggerBee_frequency': {}, # hold a star and the running trigger
            "saved_pollenThemes": [],  # bucket of saved star settings to choose from
            "saved_powerRangers": [],  # bucket of saved star settings to choose from
            "subconscious": {"app_info": []},
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

    else:
        QUEEN = {  # The Queens Mind
            "init_id": f'{"queen"}{"_"}{return_timestamp_string()}',
            "prod": "",
            "source": "na",
            "last_modified": datetime.now(est),
            "command_conscience": {},
            "queen_orders": pd.DataFrame([create_QueenOrderBee(queen_init=True)]),
            "portfolios": {"Jq": {"total_investment": 0, "currnet_value": 0}},
            "heartbeat": {
                "active_tickerStars": {},
                "available_tickers": [],
                "active_tickers": [],
                "available_triggerbees": [],
            },
            "queens_messages": {},
            "kings_order_rules": {},
            "queen_controls": return_queen_controls(stars),
            "symbol_universe": {
                "index_ticker_db": index_ticker_db,
                "main_index_dict": main_index_dict,
                "main_symbols_full_list": main_symbols_full_list,
                "not_avail_in_alpaca": not_avail_in_alpaca,
            },
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
                "pawns": {
                    "MACD_fast_slow_smooth": {"fast": 12, "slow": 26, "smooth": 9},
                    "tickers": main_symbols_full_list[:100],
                    "stars": stars(),
                },
            },
            # 'auth_users': {'stefanstapinski@gmail.com': {}, 'stevenweaver8@gmail.com': {}},
            "errors": {},
            "client_order_ids_qgen": [],
            "app_requests__bucket": [],
            # 'triggerBee_frequency': {}, # hold a star and the running trigger
            "saved_pollenThemes": [],  # bucket of saved star settings to choose from
            "saved_powerRangers": [],  # bucket of saved star settings to choose from
            "subconscious": {"app_info": []},
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


def init_qcp(init_macd_vars, ticker_list):
    return {
        "MACD_fast_slow_smooth": init_macd_vars,
        "tickers": ticker_list,
        "stars": stars(),
    }


def generate_chess_board(chess_pieces, init_macd_vars = {"fast": 12, "slow": 26, "smooth": 9}):

    chess_board = {
        "castle": init_qcp(init_macd_vars=init_macd_vars, ticker_list=["SPY"]),
        "bishop": init_qcp(
            init_macd_vars=init_macd_vars, ticker_list=["GOOG", "AAPL", "TSLA"]
        ),
        "knight": init_qcp(
            init_macd_vars=init_macd_vars, ticker_list=["AMZN", "OXY", "SOFI"]
        ),
        "castle_coin": init_qcp(
            init_macd_vars=init_macd_vars, ticker_list=["BTCUSD", "ETHUSD"]
        ),
    }


    return chess_board

def init_QUEEN_App():
    ticker_universe = return_Ticker_Universe()
    index_ticker_db = ticker_universe["index_ticker_db"]
    main_index_dict = ticker_universe["main_index_dict"]
    main_symbols_full_list = ticker_universe["main_symbols_full_list"]
    not_avail_in_alpaca = ticker_universe["not_avail_in_alpaca"]
    init_macd_vars = {"fast": 12, "slow": 26, "smooth": 9}



    app = {
        "prod": 'init',
        "db__client_user": 'init',
        "theme": "nuetral",
        "king_controls_queen": return_queen_controls(stars),
        "qcp_workerbees": {
            "castle": init_qcp(init_macd_vars=init_macd_vars, ticker_list=["SPY"]),
            "bishop": init_qcp(
                init_macd_vars=init_macd_vars, ticker_list=["GOOG", "AAPL", "TSLA"]
            ),
            "knight": init_qcp(
                init_macd_vars=init_macd_vars, ticker_list=["AMZN", "OXY", "SOFI"]
            ),
            "castle_coin": init_qcp(
                init_macd_vars=init_macd_vars, ticker_list=["BTCUSD", "ETHUSD"]
            ),
            "pawns": init_qcp(
                init_macd_vars=init_macd_vars, ticker_list=main_symbols_full_list[88:89]
            ),
        },
        
        "chess_board": {
            "castle": init_qcp(init_macd_vars=init_macd_vars, ticker_list=["SPY"]),
            "bishop": init_qcp(
                init_macd_vars=init_macd_vars, ticker_list=["GOOG", "AAPL", "TSLA"]
            ),
            "knight": init_qcp(
                init_macd_vars=init_macd_vars, ticker_list=["AMZN", "OXY", "SOFI"]
            ),
            "castle_coin": init_qcp(
                init_macd_vars=init_macd_vars, ticker_list=["BTCUSD", "ETHUSD"]
            ),
            "pawns": init_qcp(
                init_macd_vars=init_macd_vars, ticker_list=main_symbols_full_list[88:89]
            ),
        },


        "trigger_queen": {
            "dag": "init",
            "last_trig_date": datetime.now(est),
            "client_user": "init",
        },
        "trigger_workerbees": {
            "last_trig_date": datetime.now(est),
            "client_user": "init",
        },
        "bee_lounge": [],
        "users_secrets": init_client_user_secrets(),
        "character_image" : mainpage_bee_png,
        "risk_level": 0,
        "age": 0,
        "app_order_requests": [],
        "sell_orders": [],
        "buy_orders": [],
        "last_modified": {"last_modified": datetime.now(est)},
        "queen_processed_orders": [],
        "wave_triggers": [],
        "app_wave_requests": [],
        "trading_models": [],
        "trading_models_requests": [],
        "power_rangers": [],
        "power_rangers_requests": [],
        "power_rangers_lastupdate": datetime.now().astimezone(est),
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
        ## Update Time Zone... Low Priority
        "update_queen_order": [],
        "update_queen_order_requests": [],
        "saved_trading_models": generate_TradingModel()["MACD"],
        "misc_bucket": [],
        "source": "na",
        "stop_queen": False,
    }
    return app


def add_key_to_app(APP_requests):  # returns QUEES
    q_keys = APP_requests.keys()
    latest_queen = init_QUEEN_App()
    update = False
    for k, v in latest_queen.items():
        if k not in q_keys:
            APP_requests[k] = v
            update = True
            msg = f'{k}{" : Key Added"}'
            print(msg)
            logging.info(msg)
    return {"QUEEN_KING": APP_requests, "update": update}


def add_key_to_QUEEN(QUEEN, queens_chess_piece):  # returns QUEEN
    update = False
    q_keys = QUEEN.keys()
    latest_queen = init_QUEEN("queen")
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
        if (
            story_["story"]["macd_state"] in QUEEN["heartbeat"]["available_triggerbees"]
            and (now_time - story_["story"]["time_state"]).seconds < 33
        ):
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
def pollen_story(pollen_nectar, WORKER_QUEEN=False):
    # define weights in global and do multiple weights for different scenarios..
    # MACD momentum from past N times/days
    # TIME PAST SINCE LAST HIGH TO LOW to change weight & how much time passed since tier cross last high?
    # how long since last max/min value reached (reset time at +- 2)

    # >/ create ranges for MACD & RSI 4-3, 70-80, or USE Prior MAX&Low ...
    # >/ what current macd tier values in comparison to max/min
    try:
        s = datetime.now(est)
        story = {}
        ANGEL_bee = {}  # add to QUEENS mind
        STORY_bee = {}
        # CHARLIE_bee = {}  # holds all ranges for ticker and passes info into df
        betty_bee = {k: {} for k in pollen_nectar.keys()}  # monitor function speeds
        knights_sight_word = {}
        # knight_sight_df = {}

        for (
            ticker_time_frame,
            df_i,
        ) in (
            pollen_nectar.items()
        ):  # CHARLIE_bee: # create ranges for MACD & RSI 4-3, 70-80, or USE Prior MAX&Low ...
            s_ttfame_func_check = datetime.now(est).astimezone(est)
            ticker, tframe, frame = ticker_time_frame.split("_")

            trigbees = ["buy_cross-0", "sell_cross-0", "ready_buy_cross"]

            ANGEL_bee[ticker_time_frame] = {}
            STORY_bee[ticker_time_frame] = {"story": {}}

            df = df_i.fillna(0).copy()
            df = df.reset_index(drop=True)
            df["story_index"] = df.index
            df_len = len(df)
            mac_world = {
                "macd_high": df["macd"].max(),
                "macd_low": df["macd"].min(),
                "signal_high": df["signal"].max(),
                "signal_low": df["signal"].min(),
                "hist_high": df["hist"].max(),
                "hist_low": df["hist"].min(),
            }
            # macd signal divergence
            df["macd_singal_deviation"] = df["macd"] - df["signal"]
            STORY_bee[ticker_time_frame]["story"]["macd_singal_deviation"] = df.iloc[-1][
                "macd_singal_deviation"
            ]

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
            resp = return_waves_measurements(
                df=df, trigbees=trigbees, ticker_time_frame=ticker_time_frame
            )
            e_timetoken = datetime.now(est)
            betty_bee[ticker_time_frame]["waves_return_waves_measurements"] = (
                e_timetoken - s_timetoken
            )

            df = resp["df"]
            MACDWAVE_story["story"] = resp["df_waves"]

            STORY_bee[ticker_time_frame]["waves"] = MACDWAVE_story

            e_timetoken = datetime.now(est)
            betty_bee[ticker_time_frame]["waves"] = e_timetoken - s_timetoken

            knights_sight_word[ticker_time_frame] = knights_word
            STORY_bee[ticker_time_frame]["KNIGHTSWORD"] = knights_word

            # # return degree angle 0, 45, 90
            try:
                s_timetoken = datetime.now(est)
                var_list = ["macd", "hist", "signal", "close", "rsi_ema"]
                var_timeframes = [3, 6, 8, 10, 25, 33]
                for var in var_list:
                    for t in var_timeframes:
                        # apply rollowing angle
                        if df_len >= t:
                            x = df.iloc[df_len - t : df_len][var].to_list()
                            y = [1, 2]
                            name = f'{var}{"-"}{"Degree"}{"--"}{str(t)}'
                            ANGEL_bee[ticker_time_frame][name] = return_degree_angle(x, y)
                e_timetoken = datetime.now().astimezone(est)
                betty_bee[ticker_time_frame]["Angel_Bee"] = e_timetoken - s_timetoken
            except Exception as e:
                msg = (
                    e,
                    "--",
                    print_line_of_error(),
                    "--",
                    ticker_time_frame,
                    "--ANGEL_bee",
                )
                logging.error(msg)

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

            # devation from vwap
            df["vwap_deviation"] = df["close"] - df["vwap"]
            df["vwap_deviation_pct"] = df["close"] / df["vwap_deviation"]
            STORY_bee[ticker_time_frame]["story"]["vwap_deviation"] = df.iloc[-1][
                "vwap_deviation"
            ]
            STORY_bee[ticker_time_frame]["story"]["vwap_deviation_pct"] = df.iloc[-1][
                "vwap_deviation"
            ]

            # ipdb.set_trace()
            # MACD WAVE
            macd_state = df["macd_cross"].iloc[-1]
            macd_state_side = macd_state.split("_")[0]  # buy_cross-num
            middle_crossname = macd_state.split("_")[1].split("-")[0]
            state_count = macd_state.split("-")[1]  # buy/sell_name_number
            STORY_bee[ticker_time_frame]["story"]["macd_state"] = macd_state
            STORY_bee[ticker_time_frame]["story"]["macd_state_side"] = macd_state_side
            STORY_bee[ticker_time_frame]["story"]["time_since_macd_change"] = state_count

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
            STORY_bee[ticker_time_frame]["story"]["last_close_price"] = df.iloc[-1][
                "close"
            ]

            if "1Minute_1Day" in ticker_time_frame:
                theme_df = df.copy()
                theme_df = split_today_vs_prior(df=theme_df)  # remove prior day
                theme_today_df = theme_df["df_today"]
                # theme_prior_df = theme_df['df_prior']

                # we want...last vs currnet close prices, && Height+length of wave
                current_price = theme_today_df.iloc[-1]["close"]
                open_price = theme_today_df.iloc[0]["close"]  # change to timestamp lookup
                # yesterday_close = theme_prior_df.iloc[-1]['close'] # change to timestamp lookup

                STORY_bee[ticker_time_frame]["story"]["current_from_open"] = (
                    current_price - open_price
                ) / current_price

                # # Current from Yesterdays Close
                # STORY_bee[ticker_time_frame]['story']['current_from_yesterday_close'] = (current_price - yesterday_close) / current_price

                # # how did day start ## this could be moved to queen and calculated once only
                # STORY_bee[ticker_time_frame]['story']['open_start_pct'] = (open_price - yesterday_close) / open_price

                e_timetoken = datetime.now().astimezone(est)
                slope, intercept, r_value, p_value, std_err = stats.linregress(
                    theme_today_df.index, theme_today_df["close"]
                )
                STORY_bee[ticker_time_frame]["story"]["current_slope"] = slope
                e_timetoken = datetime.now().astimezone(est)
                betty_bee[ticker_time_frame]["slope"] = e_timetoken - s_timetoken

            # Measure MACD WAVES
            # change % shifts for each, close, macd, signal, hist....
            df = assign_MACD_Tier(
                df=df,
                mac_world=mac_world,
                tiers_num=macd_tiers,
                ticker_time_frame=ticker_time_frame,
            )
            STORY_bee[ticker_time_frame]["story"]["current_macd_tier"] = df.iloc[-1][
                "macd_tier"
            ]
            STORY_bee[ticker_time_frame]["story"]["current_hist_tier"] = df.iloc[-1][
                "hist_tier"
            ]

            df["mac_ranger"] = df["macd_tier"].apply(lambda x: power_ranger_mapping(x))
            df["hist_ranger"] = df["hist_tier"].apply(lambda x: power_ranger_mapping(x))

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

        e = datetime.now(est)
        print("pollen_story", str((e - s)))
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
        print("pollen_story error ", e)
        print_line_of_error()
        print(ticker_time_frame)
        ipdb.set_trace()


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


def assign_MACD_Tier(df, mac_world, tiers_num, ticker_time_frame):
    # create tier ranges
    # tiers_num = 8

    def create_tier_range(m_high, m_low):
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
                # print(k, num_value)
                return k
            elif num_value < 0 and num_value < v[0] and num_value > v[1]:
                # print(k, num_value)
                return k
            elif num_value > 0 and num_value >= max_num_value:
                # print("way above")
                return length_td
            elif num_value < 0 and num_value <= max_num_value:
                # print("way below")
                return length_td
            elif num_value == 0:
                # print('0 really')
                return 0

    # select mac_world &  # apply tiers

    # "MAC"
    if mac_world["macd_high"] == 0:  # no max min exist yet (1day scenario)
        m_high = 1
        m_low = -1
    else:
        m_high = mac_world["macd_high"]
        m_low = mac_world["macd_low"]

    tier_range = create_tier_range(m_high, m_low)
    td_high = tier_range["td_high"]
    td_low = tier_range["td_low"]

    df["macd_tier"] = np.where(
        (df["macd"] > 0),
        df["macd"].apply(lambda x: assign_tier_num(num_value=x, td=td_high)),
        df["macd"].apply(lambda x: assign_tier_num(num_value=x, td=td_low)),
    )

    df["macd_tier"] = np.where(df["macd"] > 0, df["macd_tier"], df["macd_tier"] * -1)

    # if ticker_time_frame == 'SPY_30Minute_1Month':
    #     ipdb.set_trace()

    # "MAC"
    if mac_world["hist_high"] == 0:  # no max min exist yet (1day scenario)
        m_high = 1
        m_low = -1
    else:
        m_high = mac_world["hist_high"]
        m_low = mac_world["hist_low"]

    tier_range = create_tier_range(m_high, m_low)
    td_high = tier_range["td_high"]
    td_low = tier_range["td_low"]
    df["hist_tier"] = np.where(
        (df["hist"] > 0),
        df["hist"].apply(lambda x: assign_tier_num(num_value=x, td=td_high)),
        df["hist"].apply(lambda x: assign_tier_num(num_value=x, td=td_low)),
    )
    df["hist_tier"] = np.where(df["hist"] > 0, df["hist_tier"], df["hist_tier"] * -1)

    return df


def return_knightbee_waves(
    df, trigbees, ticker_time_frame
):  # adds profit wave based on trigger
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
                # trig_bee_count+=1
                # beename = f'{trig_name}{trig_bee_count}'
                close_price = close[idx]
                track_bees[beename] = close_price
                # reset only if bee not continous
                if trigger_bee[idx - 1] != "bee":
                    trig_bee_count += 1
                continue
            if trig_bee_count > 0:
                # beename = f'{trig_name}{trig_bee_count}'
                origin_trig_price = track_bees[str(int(beename) - 1)]
                latest_price = close[idx]
                profit_loss = (latest_price - origin_trig_price) / latest_price

                if (
                    "sell_cross-0" in knight_trigger
                ):  # all triggers with short reverse number to reflect profit
                    profit_loss = profit_loss * -1

                if beename in track_bees_profits.keys():
                    track_bees_profits[beename].update({idx: profit_loss})
                else:
                    track_bees_profits[beename] = {idx: profit_loss}
        # trigbees[trig_name]['wave'] = track_bees_profits
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


def return_macd_wave_story(df, trigbees, ticker_time_frame, tframe):
    # POLLENSTORY = read_pollenstory()
    # df = POLLENSTORY["SPY_1Minute_1Day"]
    # trigbees = ["buy_cross-0", "sell_cross-0"]
    # length and height of wave
    MACDWAVE_story = {"story": {}}
    MACDWAVE_story.update({trig_name: {} for trig_name in trigbees})

    for trigger in trigbees:
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
                ["timestamp_est", wave_col_wavenumber, "story_index", wave_col_name]
            ].copy()
            df_waveslice = df[
                df[wave_col_wavenumber] == wave_n
            ]  # slice by trigger event wave start / end

            row_1 = df_waveslice.iloc[0]["story_index"]
            row_2 = df_waveslice.iloc[-1]["story_index"]

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
                elif wave_starttime_token > wave_starttime_token.replace(
                    hour=11, minute=0
                ) and wave_starttime_token < wave_starttime_token.replace(
                    hour=14, minute=0
                ):
                    wave_blocktime = "lunch_11-2"
                elif wave_starttime_token > wave_starttime_token.replace(
                    hour=14, minute=0
                ) and wave_starttime_token < wave_starttime_token.replace(
                    hour=16, minute=1
                ):
                    wave_blocktime = "afternoon_2-4"
                else:
                    wave_blocktime = "afterhours"

            MACDWAVE_story[trigger][wave_n].update(
                {
                    "ticker_time_frame": ticker_time_frame,
                    "length": row_2 - row_1,
                    "wave_blocktime": wave_blocktime,
                    "wave_start_time": wave_starttime,
                    "wave_end_time": wave_endtime,
                    "trigbee": trigger,
                    "wave_id": f'{trigger}{"_"}{wave_blocktime}{"_"}{wave_starttime}',
                }
            )

            wave_height_value = max(df_waveslice[wave_col_name].values)
            # how long was it profitable?
            profit_df = df_waveslice[df_waveslice[wave_col_name] > 0].copy()
            profit_length = len(profit_df)
            if profit_length > 0:
                max_profit_index = profit_df[
                    profit_df[wave_col_name] == wave_height_value
                ].iloc[0]["story_index"]
                time_to_max_profit = max_profit_index - row_1
                MACDWAVE_story[trigger][wave_n].update(
                    {
                        "maxprofit": wave_height_value,
                        "time_to_max_profit": time_to_max_profit,
                    }
                )

            else:
                MACDWAVE_story[trigger][wave_n].update(
                    {"maxprofit": wave_height_value, "time_to_max_profit": 0}
                )

    # all_waves = []
    # all_waves_temp = []
    # for trig_name in trigbees:
    #     l_waves = list(MACDWAVE_story[trig_name].values())
    #     l_waves = [i for i in l_waves if i['wave_n'] != '0']
    #     all_waves_temp.append(l_waves)
    # for el_list in range(len(all_waves_temp)):
    #     all_waves = all_waves + all_waves_temp[el_list - 1]
    # df_waves = pd.DataFrame(all_waves)
    # # df_waves = df_waves.fillna("NULL")
    # # df_waves = df_waves
    # df_waves = df_waves.sort_values(by=['wave_start_time'], ascending=True).reset_index()
    # df_waves['macd_wave_n'] = df_waves.index
    # df_waves = macd_wave_length_story(df_waves) # df_waves['macd_wave_length']

    # MACDWAVE_story['story'] = df_waves
    # df_t = df_waves[[i for i in df_waves.columns if 'macd' in i or i in ['wave_start_time', 'trigbee', 'wave_blocktime']]].copy()

    return MACDWAVE_story


def return_waves_measurements(
    df, ticker_time_frame, trigbees=["buy_cross-0", "sell_cross-0", "ready_buy_cross"]
):
    # POLLENSTORY = read_pollenstory()
    # df = POLLENSTORY["SPY_1Minute_1Day"]
    # trigbees = ["macd_cross"]
    # length and height of wave

    # """ use shift to get row index"""
    # # Create a sample DataFrame
    # df = pd.DataFrame({'col1': [1, 4, 7, 10], 'col2': [10, 20, 30, 40]})
    # # Create a new column 'new_column' that calculates the difference between 'col1' and the previous row's value of 'col1'
    # df['new_column'] = np.where(df['col1'] - df['col1'].shift(1) != 0, df['col1'] - df['col1'].shift(1), 0)

    # ipdb.set_trace()
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
            prior_row = df_waves.iloc[x - 1]
            current_row = df_waves.iloc[x]
            latest_price = current_row["story_index"]
            origin_trig_price = prior_row["story_index"]
            length = latest_price - origin_trig_price
            return length

    def macd_cross_WaveBlocktime(df_waves, x):
        # Assign each waves timeblock
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

    ### Needs a little extra Love >> index max profit, count length, add to df_waves and df >> ensure max profit is correct as 2 rows could share same value
    def macd_cross_TimeToMaxProfit(df, df_waves, x):
        # Assign each waves timeblock
        for x in df_waves["wave_n"].tolist():
            if x == 0:
                return 0
            else:
                prior_row = df_waves.iloc[x - 1]["story_index"]
                current_row = df_waves.iloc[x]["story_index"]

                df_waveslice = df[
                    (df.index >= int(prior_row)) & (df.index < int(current_row))
                ].copy()
                origin_trig_price = df_waves.iloc[x - 1]["close"]
                df_waveslice["macd_cross__maxprofit"] = (
                    df_waveslice["close"] - origin_trig_price
                ) / df_waveslice["close"]

                index_wave_series = dict(
                    zip(
                        df_waveslice["story_index"], df_waveslice["macd_cross__maxprofit"]
                    )
                )
                # df['macd_cross__maxprofit'] = df['story_index'].map(index_wave_series).fillna("0")
                # return index_wave_series
                # return df
                wave_col_name = "macd_cross__maxprofit"
                wave_height_value = max(df_waveslice[wave_col_name].values)
                # how long was it profitable?
                profit_df = df_waveslice[df_waveslice[wave_col_name] > 0].copy()
                profit_length = len(profit_df)
                if profit_length > 0:
                    max_profit_index = profit_df[
                        profit_df[wave_col_name] == wave_height_value
                    ].iloc[0]["story_index"]
                    time_to_max_profit = max_profit_index - prior_row
                    # MACDWAVE_story[trigger][wave_n].update({'maxprofit': wave_height_value, 'time_to_max_profit': time_to_max_profit})

                else:
                    time_to_max_profit = 0
                    # MACDWAVE_story[trigger][wave_n].update({'maxprofit': wave_height_value, 'time_to_max_profit': 0})

    # set wave num
    df_waves = df[df["macd_cross"].isin(trigbees)].copy().reset_index()
    df_waves["wave_n"] = df_waves.index
    df_waves["length"] = df_waves["wave_n"].apply(
        lambda x: macd_cross_WaveLength(df_waves, x)
    )
    df_waves["profits"] = df_waves["wave_n"].apply(lambda x: profit_loss(df_waves, x))
    # df_waves['story_index_in_profit'] = np.where(df_waves['profits'] > 0, 1, 0)
    df_waves["active_wave"] = np.where(
        df_waves["wave_n"] == df_waves["wave_n"].iloc[-1], "active", "not_active"
    )
    df_waves["wave_blocktime"] = df_waves["wave_n"].apply(
        lambda x: macd_cross_WaveBlocktime(df_waves, x)
    )

    index_wave_series = dict(zip(df_waves["story_index"], df_waves["wave_n"]))
    df["wave_n"] = df["story_index"].map(index_wave_series).fillna("0")

    index_wave_series = dict(zip(df_waves["story_index"], df_waves["length"]))
    df["length"] = df["story_index"].map(index_wave_series).fillna("0")

    index_wave_series = dict(zip(df_waves["story_index"], df_waves["wave_blocktime"]))
    df["wave_blocktime"] = df["story_index"].map(index_wave_series).fillna("0")

    index_wave_series = dict(zip(df_waves["story_index"], df_waves["profits"]))
    df["profits"] = df["story_index"].map(index_wave_series).fillna("0")

    # index_wave_series = dict(zip(df_waves['story_index'], df_waves['story_index_in_profit']))
    # df['story_index_in_profit'] = df['story_index'].map(index_wave_series).fillna("0")

    index_wave_series = dict(zip(df_waves["story_index"], df_waves["active_wave"]))
    df["active_wave"] = df["story_index"].map(index_wave_series).fillna("0")

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


def split_today_vs_prior(df, timestamp="timestamp_est"):
    # df[timestamp] = pd.to_datetime(df[timestamp], errors='coerce').fillna('err')
    # err = df[df[timestamp] == 'err']
    # if len(err) > 0:
    #     print('datetime conv failed')

    # df = df[df[timestamp] != 'err'].copy()

    df_today = df[
        df[timestamp]
        > (datetime.now(est).replace(hour=1, minute=1, second=1)).astimezone(est)
    ].copy()
    df_prior = df[~(df[timestamp].isin(df_today[timestamp].to_list()))].copy()

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
        # print(str((e - s)) + ": " + datetime.now().strftime('%Y-%m-%d %H:%M'))

        # if ndays == 1:
        #     market_hours_data = market_hours_data[market_hours_data['timestamp_est'] > (datetime.now(est).replace(hour=1, minute=1, second=1))].copy()

        # if symbol_data.iloc[-1]["timestamp_est"] == 0:
        #     ipdb.set_trace()

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
        # ipdb.set_trace()


def return_bars_list(
    api, ticker_list, chart_times, trading_days_df, crypto=False, exchange=False
):
    try:
        s = datetime.now(est)
        # ticker_list = ['SPY', 'QQQ']
        # chart_times = {
        #     "1Minute_1Day": 0, "5Minute_5Day": 5, "30Minute_1Month": 18,
        #     "1Hour_3Month": 48, "2Hour_6Month": 72,
        #     "1Day_1Year": 250
        #     }
        return_dict = {}
        error_dict = {}

        for charttime, ndays in chart_times.items():
            timeframe = charttime.split("_")[0]  # '1Minute_1Day'

            trading_days_df_ = trading_days_df[
                trading_days_df["date"] < current_date
            ]  # less then current date
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

            # set index to EST time
            symbol_data["timestamp_est"] = symbol_data.index
            symbol_data["timestamp_est"] = symbol_data["timestamp_est"].apply(
                lambda x: x.astimezone(est)
            )
            symbol_data["timeframe"] = timeframe
            symbol_data["bars"] = "bars_list"

            symbol_data = symbol_data.reset_index(drop=True)
            # if ndays == 1:
            #     symbol_data = symbol_data[symbol_data['timestamp_est'] > (datetime.now(est).replace(hour=1, minute=1, second=1))].copy()

            return_dict[charttime] = symbol_data

            if len(symbol_data) == 0:
                error_dict[ticker_list] = {"msg": "no data returned", "time": time}
                return False

        e = datetime.now(est)

        return {"resp": True, "return": return_dict}

    except Exception as e:
        print("sending email of error", e)
        er_line = print_line_of_error()
        logging_log_message(
            log_type="critical",
            msg="bars failed",
            error=f"error {e}  error line {str(er_line)}",
        )
        # ipdb.set_trace()


def get_best_limit_price(ask, bid):
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
    api, ticker_list, crypto=False, coin_exchange=False, min_input=0, sec_input=30
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
        previous_time = (
            datetime.now(utc) - timedelta(minutes=min_input, seconds=sec_input)
        ).strftime("%Y-%m-%dT%H:%M:%SZ")

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


def check_order_status(
    api, client_order_id, queen_order=False, prod=True
):  # return raw dict form
    if queen_order:
        if "queen_gen" in queen_order["client_order_id"]:
            return queen_order
        else:
            order = api.get_order_by_client_order_id(client_order_id=client_order_id)
            order_ = vars(order)["_raw"]
            return order_


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


def order_filled_completely(client_order_id):
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
    take_profit=False,
):
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
        return False

    return order

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
    # Account({   'account_blocked': False, 'account_number': '603397580', 'accrued_fees': '0', 'buying_power': '80010',
    #     'cash': '40005', 'created_at': '2022-01-23T22:11:15.978765Z', 'crypto_status': 'PAPER_ONLY', 'currency': 'USD', 'daytrade_count': 0,
    #     'daytrading_buying_power': '0', 'equity': '40005', 'id': '2fae9699-b24f-4d06-80ec-d531b61e9458', 'initial_margin': '0',
    #     'last_equity': '40005','last_maintenance_margin': '0','long_market_value': '0','maintenance_margin': '0',
    #     'multiplier': '2','non_marginable_buying_power': '40005','pattern_day_trader': False,'pending_transfer_in': '40000',
    #     'portfolio_value': '40005','regt_buying_power': '80010',
    #     'short_market_value': '0','shorting_enabled': True,'sma': '40005','status': 'ACTIVE','trade_suspended_by_user': False,
    #     'trading_blocked': False, 'transfers_blocked': False})
    """
    info = api.get_account()
    return {
        "info": info,
        "info_converted": {
            "accrued_fees": float(info.accrued_fees),
            "buying_power": float(info.buying_power),
            "cash": float(info.cash),
            "daytrade_count": float(info.daytrade_count),
            "last_equity": float(info.last_equity),
            "portfolio_value": float(info.portfolio_value),
        },
    }


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


def PickleData(pickle_file, data_to_store):
    p_timestamp = {"pq_last_modified": datetime.now(est)}
    root, name = os.path.split(pickle_file)
    pickle_file_temp = os.path.join(root, ("temp" + name))
    with open(pickle_file_temp, "wb+") as dbfile:
        db = data_to_store
        db["pq_last_modified"] = p_timestamp
        pickle.dump(db, dbfile)

    with open(pickle_file, "wb+") as dbfile:
        db = data_to_store
        db["pq_last_modified"] = p_timestamp
        pickle.dump(db, dbfile)

    return True


def ReadPickleData(pickle_file):
    # Check the file's size and modification time
    prev_size = os.stat(pickle_file).st_size
    prev_mtime = os.stat(pickle_file).st_mtime
    while True:
        stop = 0
        # Get the current size and modification time of the file
        curr_size = os.stat(pickle_file).st_size
        curr_mtime = os.stat(pickle_file).st_mtime

        # Check if the size or modification time has changed
        if curr_size != prev_size or curr_mtime != prev_mtime:
            print(f"{pickle_file} is currently being written to")
            logging.info(f"{pickle_file} is currently being written to")
        else:
            if stop > 3:
                print("pickle error")
                logging.critical(f"{e} error is pickle load")
                send_email(subject="CRITICAL Read Pickle Break")
                break
            try:
                with open(pickle_file, "rb") as f:
                    return pickle.load(f)
            except Exception as e:
                print(e)
                logging.error(f"{e} error is pickle load")
                stop += 1
                time.sleep(0.033)

        # Update the previous size and modification time
        prev_size = curr_size
        prev_mtime = curr_mtime

        # Wait a short amount of time before checking again
        time.sleep(0.033)


def timestamp_string(format="%m-%d-%Y %I.%M%p", tz=est):
    return datetime.now(tz).strftime(format)


def return_timestamp_string(format="%Y-%m-%d %H-%M-%S %p {}".format(est), tz=est):
    return datetime.now(tz).strftime(format)


def print_line_of_error():
    exc_type, exc_obj, exc_tb = sys.exc_info()
    print(exc_type, exc_tb.tb_lineno)


def return_index_tickers(index_dir, ext):
    s = datetime.now(est)
    # ext = '.csv'
    # index_dir = os.path.join(db_root, 'index_tickers')

    index_dict = {}
    full_ticker_list = []
    all_indexs = [i.split(".")[0] for i in os.listdir(index_dir)]
    for i in all_indexs:
        df = pd.read_csv(
            os.path.join(index_dir, i + ext), dtype=str, encoding="utf8", engine="python"
        )
        df = df.fillna("")
        tics = df["symbol"].tolist()
        for j in tics:
            full_ticker_list.append(j)
        index_dict[i] = df

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
    if df.iloc[0]["timeframe"] == "1Minute":
        d_token = split_today_vs_prior(df=df)
        df_today = d_token["df_today"]
        df_prior = d_token["df_prior"]

        # if df_today.iloc[-1]["timestamp_est"] == 0 or df_prior.iloc[-1]["timestamp_est"] == 0:
        #     ipdb.set_trace()

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


def return_market_hours(trading_days, crypto):
    # trading_days = api_cal # api.get_calendar()
    trading_days_df = pd.DataFrame([day._raw for day in trading_days])
    s = datetime.now(est)
    s_iso = s.isoformat()[:10]
    mk_open_today = s_iso in trading_days_df["date"].tolist()
    mk_open = s.replace(hour=1, minute=1, second=1)
    mk_close = s.replace(hour=16, minute=0, second=0)

    if str(crypto).lower() == "true":
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
            data = init_QUEEN_App()
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


def return_star_alloc(star_settings, stars=stars):
    if star_settings:
        star_settings = star_settings
    else:
        star_settings = {
            "1Minute_1Day": 1,
            "5Minute_5Day": 1,
            "30Minute_1Month": 1,
            "1Hour_3Month": 1,
            "2Hour_6Month": 1,
            "1Day_1Year": 1,
        }

    total_settings = sum(star_settings.values())
    star_alloc = {k: i / total_settings for (k, i) in star_settings.items()}

    default = {star: star_alloc[star] for star in stars().keys()}

    return {"default": default}


def return_portfolio_ticker_allocation():
    pass


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


def init_KING(pickle_file):
    king = {
        "kingme": KINGME(),
    }

    PickleData(pickle_file=pickle_file, data_to_store=king)

    return True


def KINGME(trigbees=False, waveBlocktimes=False, stars=stars):
    return_dict = {}

    trigbees = ["buy_cross-0", "sell_cross-0", "ready_buy_cross"]
    waveBlocktimes = [
        "premarket",
        "morning_9-11",
        "lunch_11-2",
        "afternoon_2-4",
        "afterhours",
        "Day",
    ]

    # add order rules
    return_dict["star_times"] = stars()
    return_dict["waveBlocktimes"] = waveBlocktimes
    return_dict["trigbees"] = trigbees

    return return_dict


def generate_TradingModel(
    theme="custom",
    portfolio_name="Jq",
    ticker="SPY",
    stars=stars,
    trigbees=["buy_cross-0", "sell_cross-0", "ready_buy_cross"],
    trading_model_name="MACD",
    status="active",
    portforlio_weight_ask=0.01,
):
    # theme level settings
    themes = [
        "nuetral",
        "custom",
        "long_star",
        "short_star",
        "day_shark",
        "safe",
        "star__storywave_AI",
    ]
    star__storywave_AI = "star__storywave_AI"

    def kings_order_rules(
        status,
        doubledown_timeduration,
        trade_using_limits,
        max_profit_waveDeviation,
        max_profit_waveDeviation_timeduration,
        timeduration,
        take_profit,
        sellout,
        sell_trigbee_trigger,
        stagger_profits,
        scalp_profits,
        scalp_profits_timeduration,
        stagger_profits_tiers,
        limitprice_decay_timeduration=1,
        skip_sell_trigbee_distance_frequency=0,
        ignore_trigbee_at_power=0.01,
        ignore_trigbee_in_macdstory_tier=[],
        ignore_trigbee_in_histstory_tier=[],
        ignore_trigbee_in_vwap_range={"low_range": -0.05, "high_range": 0.05},
        take_profit_in_vwap_deviation_range={"low_range": -0.05, "high_range": 0.05},
        short_position=False,
    ):
        return {
            # 1 trade if exists, double allows for 1 more trade to occur while in existance
            "theme": theme,
            "status": status,
            "trade_using_limits": trade_using_limits,
            "limitprice_decay_timeduration": limitprice_decay_timeduration,
            # TimeHorizion: i.e. the further along time how to sell out of profit
            "doubledown_timeduration": doubledown_timeduration,
            "max_profit_waveDeviation": max_profit_waveDeviation,
            "max_profit_waveDeviation_timeduration": max_profit_waveDeviation_timeduration,
            "timeduration": timeduration,
            "take_profit": take_profit,
            "sellout": sellout,
            "sell_trigbee_trigger": sell_trigbee_trigger,
            "stagger_profits": stagger_profits,
            "scalp_profits": scalp_profits,
            "scalp_profits_timeduration": scalp_profits_timeduration,
            "stagger_profits_tiers": stagger_profits_tiers,
            "skip_sell_trigbee_distance_frequency": skip_sell_trigbee_distance_frequency,
            # skip sell signal if frequency of last sell signal was X distance >> timeperiod over value, 1m: if sell was 1 story index ago
            "ignore_trigbee_at_power": ignore_trigbee_at_power,
            "ignore_trigbee_in_macdstory_tier": ignore_trigbee_in_macdstory_tier,
            "ignore_trigbee_in_histstory_tier": ignore_trigbee_in_histstory_tier,
            "ignore_trigbee_in_vwap_range": ignore_trigbee_in_vwap_range,
            "take_profit_in_vwap_deviation_range": take_profit_in_vwap_deviation_range,
            "short_position": short_position,
        }

    def star_trading_model_vars(stars=stars):
        def star__DEFAULT_kings_order_rules_mapping(stars=stars):
            return {
                "1Minute_1Day": kings_order_rules(
                    status="active",
                    trade_using_limits=True,
                    doubledown_timeduration=60,
                    max_profit_waveDeviation=1,
                    max_profit_waveDeviation_timeduration=5,
                    timeduration=120,
                    take_profit=0.01,
                    sellout=-0.0089,
                    sell_trigbee_trigger=True,
                    stagger_profits=False,
                    scalp_profits=True,
                    scalp_profits_timeduration=30,
                    stagger_profits_tiers=1,
                ),
                "5Minute_5Day": kings_order_rules(
                    status="active",
                    trade_using_limits=False,
                    doubledown_timeduration=60,
                    max_profit_waveDeviation=1,
                    max_profit_waveDeviation_timeduration=5,
                    timeduration=320,
                    take_profit=0.01,
                    sellout=-0.0089,
                    sell_trigbee_trigger=True,
                    stagger_profits=False,
                    scalp_profits=False,
                    scalp_profits_timeduration=30,
                    stagger_profits_tiers=1,
                ),
                "30Minute_1Month": kings_order_rules(
                    status="active",
                    trade_using_limits=False,
                    doubledown_timeduration=60,
                    max_profit_waveDeviation=1,
                    max_profit_waveDeviation_timeduration=30,
                    timeduration=43800,
                    take_profit=0.05,
                    sellout=-0.02,
                    sell_trigbee_trigger=True,
                    stagger_profits=False,
                    scalp_profits=False,
                    scalp_profits_timeduration=30,
                    stagger_profits_tiers=1,
                ),
                "1Hour_3Month": kings_order_rules(
                    status="active",
                    trade_using_limits=False,
                    doubledown_timeduration=60,
                    max_profit_waveDeviation=1,
                    max_profit_waveDeviation_timeduration=60,
                    timeduration=43800 * 3,
                    take_profit=0.05,
                    sellout=-0.02,
                    sell_trigbee_trigger=True,
                    stagger_profits=False,
                    scalp_profits=False,
                    scalp_profits_timeduration=30,
                    stagger_profits_tiers=1,
                ),
                "2Hour_6Month": kings_order_rules(
                    status="active",
                    trade_using_limits=False,
                    doubledown_timeduration=60,
                    max_profit_waveDeviation=1,
                    max_profit_waveDeviation_timeduration=120,
                    timeduration=43800 * 6,
                    take_profit=0.05,
                    sellout=-0.02,
                    sell_trigbee_trigger=True,
                    stagger_profits=False,
                    scalp_profits=False,
                    scalp_profits_timeduration=30,
                    stagger_profits_tiers=1,
                ),
                "1Day_1Year": kings_order_rules(
                    status="active",
                    trade_using_limits=False,
                    doubledown_timeduration=60,
                    max_profit_waveDeviation=1,
                    max_profit_waveDeviation_timeduration=60 * 24,
                    timeduration=525600,
                    take_profit=0.1,
                    sellout=-0.05,
                    sell_trigbee_trigger=True,
                    stagger_profits=False,
                    scalp_profits=False,
                    scalp_profits_timeduration=30,
                    stagger_profits_tiers=1,
                ),
            }

        def trigbees__DEFAULT_keys():
            return {
                "buy_cross-0": {},
                "sell_cross-0": {},
                "ready_buy_cross": {},
            }

        def star_kings_order_rules_mapping(
            stars,
            trigbees,
            waveBlocktimes,
            star__DEFAULT_kings_order_rules_mapping=star__DEFAULT_kings_order_rules_mapping,
            trigbees__DEFAULT_keys=trigbees__DEFAULT_keys,
        ):  # --> returns star_trigbee_king_order_rules
            star_kings_order_rules_dict = {}
            star_default_rules = star__DEFAULT_kings_order_rules_mapping()
            trigbee__default_settings = trigbees__DEFAULT_keys()
            # theme
            # for theme in themes
            for star in stars().keys():
                star_kings_order_rules_dict[star] = {}
                for trigbee in trigbees:
                    star_kings_order_rules_dict[star][
                        trigbee
                    ] = trigbee__default_settings[trigbee]
                    for blocktime in waveBlocktimes:
                        star_kings_order_rules_dict[star][trigbee][
                            blocktime
                        ] = star_default_rules[star]

            return star_kings_order_rules_dict

        def star_vars_mapping(
            trigbees,
            waveBlocktimes,
            stars=stars,
            star_kings_order_rules_mapping=star_kings_order_rules_mapping,
        ):
            return_dict = {}
            trigbees_king_order_rules = star_kings_order_rules_mapping(
                stars=stars, trigbees=trigbees, waveBlocktimes=waveBlocktimes
            )
            star_default_rules = star__DEFAULT_kings_order_rules_mapping()

            star = "1Minute_1Day"
            return_dict[star] = {
                # 'status': 'active',
                "trade_using_limits": False,
                "stagger_profits": star_default_rules[star]["stagger_profits"],
                "total_budget": 100,
                "buyingpower_allocation_LongTerm": 0.2,
                "buyingpower_allocation_ShortTerm": 0.8,
                "power_rangers": {k: 1 for k in stars().keys()},
                "trigbees": trigbees_king_order_rules[star],
                "short_position": False,
                "ticker_family": [ticker],
            }
            star = "5Minute_5Day"
            return_dict[star] = {
                "trade_using_limits": False,
                "stagger_profits": star_default_rules[star]["stagger_profits"],
                "total_budget": 100,
                "buyingpower_allocation_LongTerm": 0.2,
                "buyingpower_allocation_ShortTerm": 0.8,
                "power_rangers": {k: 1 for k in stars().keys()},
                "trigbees": trigbees_king_order_rules[star],
                "short_position": False,
                "ticker_family": [ticker],
            }

            star = "30Minute_1Month"
            return_dict[star] = {
                "trade_using_limits": False,
                "stagger_profits": star_default_rules[star]["stagger_profits"],
                "total_budget": 100,
                "buyingpower_allocation_LongTerm": 0.2,
                "buyingpower_allocation_ShortTerm": 0.8,
                "power_rangers": {k: 1 for k in stars().keys()},
                "trigbees": trigbees_king_order_rules[star],
                "short_position": False,
                "ticker_family": [ticker],
            }

            star = "1Hour_3Month"
            return_dict[star] = {
                "trade_using_limits": False,
                "stagger_profits": star_default_rules[star]["stagger_profits"],
                "total_budget": 100,
                "buyingpower_allocation_LongTerm": 0.2,
                "buyingpower_allocation_ShortTerm": 0.8,
                "power_rangers": {k: 1 for k in stars().keys()},
                "trigbees": trigbees_king_order_rules[star],
                "short_position": False,
                "ticker_family": [ticker],
            }
            star = "2Hour_6Month"
            return_dict[star] = {
                "trade_using_limits": False,
                "stagger_profits": star_default_rules[star]["stagger_profits"],
                "total_budget": 100,
                "buyingpower_allocation_LongTerm": 0.2,
                "buyingpower_allocation_ShortTerm": 0.8,
                "power_rangers": {k: 1 for k in stars().keys()},
                "trigbees": trigbees_king_order_rules[star],
                "short_position": False,
                "ticker_family": [ticker],
            }
            star = "1Day_1Year"
            return_dict[star] = {
                "trade_using_limits": False,
                "stagger_profits": star_default_rules[star]["stagger_profits"],
                "total_budget": 100,
                "buyingpower_allocation_LongTerm": 0.2,
                "buyingpower_allocation_ShortTerm": 0.8,
                "power_rangers": {k: 1 for k in stars().keys()},
                "trigbees": trigbees_king_order_rules[star],
                "short_position": False,
                "ticker_family": [ticker],
            }

            return return_dict

        def star_vars(star, star_vars_mapping):
            return {
                "star": star,
                # 'status': star_vars_mapping[star]['status'],
                "trade_using_limits": star_vars_mapping[star]["trade_using_limits"],
                "total_budget": star_vars_mapping[star]["total_budget"],
                "buyingpower_allocation_LongTerm": star_vars_mapping[star][
                    "buyingpower_allocation_LongTerm"
                ],
                "buyingpower_allocation_ShortTerm": star_vars_mapping[star][
                    "buyingpower_allocation_ShortTerm"
                ],
                "power_rangers": star_vars_mapping[star]["power_rangers"],
                "trigbees": star_vars_mapping[star]["trigbees"],
                "short_position": star_vars_mapping[star]["short_position"],
                "ticker_family": star_vars_mapping[star]["ticker_family"],
            }

        # Get Stars Trigbees and Blocktimes to create kings order rules
        all_stars = stars().keys()
        trigbees = ["buy_cross-0", "sell_cross-0", "ready_buy_cross"]
        waveBlocktimes = [
            "premarket",
            "morning_9-11",
            "lunch_11-2",
            "afternoon_2-4",
            "afterhours",
            "Day",
        ]
        star_vars_mapping_dict = star_vars_mapping(
            trigbees=trigbees, waveBlocktimes=waveBlocktimes, stars=stars
        )

        return_dict = {
            star: star_vars(star=star, star_vars_mapping=star_vars_mapping_dict)
            for star in all_stars
        }

        return return_dict

    def model_vars(trading_model_name, star, stars_vars):
        return {
            # 'status': stars_vars[star]['status'],
            "buyingpower_allocation_LongTerm": stars_vars[star][
                "buyingpower_allocation_LongTerm"
            ],
            "buyingpower_allocation_ShortTerm": stars_vars[star][
                "buyingpower_allocation_ShortTerm"
            ],
            "power_rangers": stars_vars[star]["power_rangers"],
            "trade_using_limits": stars_vars[star]["trade_using_limits"],
            "total_budget": stars_vars[star]["total_budget"],
            "trigbees": stars_vars[star]["trigbees"],
            "index_inverse_X": "1X",
            "index_long_X": "1X",
            "trading_model_name": trading_model_name,
        }

    def tradingmodel_vars(
        stars_vars,
        trigbees=trigbees,
        ticker=ticker,
        trading_model_name=trading_model_name,
        status=status,
        portforlio_weight_ask=portforlio_weight_ask,
        stars=stars,
        portfolio_name=portfolio_name,
        kings_order_rules=kings_order_rules,
    ):
        afterhours = [True if ticker in crypto_currency_symbols else False][0]
        afternoon = [True if ticker in crypto_currency_symbols else True][0]
        lunch = [True if ticker in crypto_currency_symbols else True][0]
        morning = [True if ticker in crypto_currency_symbols else True][0]
        premarket = [True if ticker in crypto_currency_symbols else False][0]
        Day = [True if ticker in crypto_currency_symbols else False][0]

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
        etf_X_direction = ["1X", "2X", "3X"]  # Determined by QUEEN
        # trigbees_list = ['buy_cross-0', 'sell_cross-0', 'ready_buy_cross']

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
            "kings_order_rules": kings_order_rules(
                status="not_active",
                trade_using_limits=False,
                doubledown_timeduration=60,
                max_profit_waveDeviation=1,
                max_profit_waveDeviation_timeduration=60 * 24,
                timeduration=33,
                take_profit=0.005,
                sellout=-0.0089,
                sell_trigbee_trigger=True,
                stagger_profits=False,
                scalp_profits=True,
                scalp_profits_timeduration=30,
                stagger_profits_tiers=1,
            ),
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

    # Trading Model Version 1
    stars_vars = star_trading_model_vars()
    macd_model = tradingmodel_vars(stars_vars=stars_vars)

    return {"MACD": macd_model}


#### QUEENBEE ####


def order_vars__queen_order_items(
    order_side=False,
    trading_model=False,
    king_order_rules=False,
    wave_amo=False,
    maker_middle=False,
    origin_wave=False,
    power_up_rangers=False,
    ticker_time_frame_origin=False,
    double_down_trade=False,
    sell_reason={},
    running_close_legs=False,
    wave_at_creation={},
    sell_qty=False,
    first_sell=False,
    time_intrade=False,
    updated_at=False,
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
    trading_model="init",
    KING="init",
    ticker_time_frame="init",
    portfolio_name="init",
    status_q="init",
    trig="init",
    exit_order_link="init",
    order_vars={},
    order={},
    priceinfo={},
    queen_init=False,
):  # Create Running Order
    def gen_queen_order(
        trading_model=trading_model,
        double_down_trade=False,
        queen_order_state=False,
        side=False,
        order_trig_buy_stop=False,
        order_trig_sell_stop=False,
        order_trig_sell_stop_limit=False,
        limit_price=False,
        running_close_legs=False,
        symbol=False,
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
        status_q=status_q,
        portfolio_name=portfolio_name,
        exit_order_link=exit_order_link,
        client_order_id=False,
        system_recon=False,
        req_qty=False,
        filled_qty=False,
        qty_available=0,
        filled_avg_price=False,
        price_time_of_request=False,
        bid=False,
        ask=False,
        honey_gauge=False,
        macd_gauge=False,
        honey_money=False,
        sell_reason=False,
        honey_time_in_profit=0,
        order=order,
        order_vars=order_vars,
        priceinfo=priceinfo,
        queen_init=False,
    ):
        date_mark = datetime.now().astimezone(est)
        if queen_init:
            return {
                name: "init"
                for name in gen_queen_order.__code__.co_varnames
                if name not in ["order", "order_vars", "priceinfo"]
            }
        else:
            return {
                "trading_model": trading_model,
                "double_down_trade": order_vars["double_down_trade"],
                "queen_order_state": "submitted",
                "side": order["side"],
                "order_trig_buy_stop": True,
                "order_trig_sell_stop": False,
                "order_trig_sell_stop_limit": order_vars["order_trig_sell_stop_limit"],
                "req_limit_price": order_vars["limit_price"],
                "limit_price": order_vars["limit_price"],
                "running_close_legs": False,
                "ticker": order["symbol"],
                "symbol": order["symbol"],
                "order_rules": order_vars["king_order_rules"],
                "origin_wave": order_vars["origin_wave"],
                "wave_at_creation": order_vars["wave_at_creation"],
                "assigned_wave": {},
                "power_up": order_vars["power_up"],
                "power_up_rangers": order_vars["power_up_rangers"],
                "ticker_time_frame_origin": order_vars["ticker_time_frame_origin"],
                "wave_amo": order_vars["wave_amo"],
                "trigname": trig,
                "datetime": date_mark,
                "ticker_time_frame": ticker_time_frame,
                "status_q": status_q,
                "portfolio_name": portfolio_name,
                "exit_order_link": exit_order_link,
                "client_order_id": order["client_order_id"],
                "system_recon": False,
                "order": "alpaca",
                "req_qty": order["qty"],
                "qty": order["qty"],
                "filled_qty": order["filled_qty"],
                "qty_available": order["filled_qty"],
                "filled_avg_price": order["filled_avg_price"],
                "price_time_of_request": priceinfo["price"],
                "bid": priceinfo["bid"],
                "ask": priceinfo["ask"],
                "honey_gauge": deque([], 89),
                "macd_gauge": deque([], 89),
                "$honey": 0,
                "sell_reason": order_vars["sell_reason"],
                "honey_time_in_profit": {},
                "profit_loss": 0,
            }

    if queen_init:
        # print("Queen Template Initalized")
        logging_log_message(msg="QueenHive Queen Template Initalized")
        running_order = gen_queen_order(queen_init=True)
    elif order["side"] == "buy" or order["side"] == "sell":
        # print("create buy running order")
        running_order = gen_queen_order()

    return running_order


def heartbeat_portfolio_revrec_template(QUEEN, portforlio_name="Jq"):
    # buying_powers
    # buying power item

    # adjust ticker weight with current QueenRevRec
    # df = pd.DataFrame(QUEEN['queen_controls']['symbols_stars_TradingModel'])
    # for ticker in df['ticker'].to_list():
    #     if ticker not in QUEEN['queen_controls']['ticker_settings'].keys():
    #         add_ticker_settings = generate_queen_ticker_settings(portforlio_name='Jq', ticker=ticker, portforlio_weight=.1, day_theme_throttle=.75, long_theme_throttle=.55)
    #         reduce_tickers = add_ticker_settings['portforlio_weight'] / sum(np.where(df['status'] == 'active',1 ,0))
    #         df['new_weight'] = df['portforlio_weight'] - reduce_tickers
    # df = pd.DataFrame(QUEEN['queen_controls']['ticker_settings'].items())
    # df = df.T
    # headers = df.iloc[0].values
    # df.columns = headers
    # df.drop(index=0, axis=0, inplace=True)
    # for ticker, tradingmodel in QUEEN['queen_controls']['symbols_stars_TradingModel'].items():
    #     if ticker not in df['ticker'].tolist():
    #         add_ticker_settings = generate_queen_ticker_settings(portforlio_name='Jq', status='active', ticker=ticker, portforlio_weight=.1, day_theme_throttle=.75, long_theme_throttle=.55)
    #         reduce_tickers = add_ticker_settings['portforlio_weight'] / sum(np.where(df['status'] == 'active',1 ,0))
    #         df['portforlio_weight'] = df['portforlio_weight'] - reduce_tickers
    #         QUEEN['queen_controls']['ticker_settings'] = df.T.to_dict()[0]
    #         QUEEN['queen_controls']['ticker_settings'].update(add_ticker_settings)

    # for ticker, tradingmodel in QUEEN['queen_controls']['symbols_stars_TradingModel'].items():
    #     if ticker not in QUEEN['queen_controls']['ticker_settings'].keys():
    #         add_ticker_settings = generate_queen_ticker_settings(portforlio_name='Jq', status='active', ticker=ticker, portforlio_weight=.1, day_theme_throttle=.75, long_theme_throttle=.55)
    #         reduce_tickers = add_ticker_settings['portforlio_weight'] / len([i for k, i in QUEEN['queen_controls']['ticker_settings'].items() if i['status']=='active'])
    #         for ticker2 in QUEEN['queen_controls']['ticker_settings'].keys()
    #             if QUEEN['queen_controls']['ticker_settings'][ticker2]['portforlio_weight'] > reduce_tickers:
    #                 QUEEN['queen_controls']['ticker_settings'][ticker2]['portforlio_weight'] = QUEEN['queen_controls']['ticker_settings'][ticker2]['portforlio_weight'] - reduce_tickers

    #         QUEEN['queen_controls']['ticker_settings'] = {df.T.to_dict()[0]}
    #         QUEEN['queen_controls']['ticker_settings'].update(add_ticker_settings)

    # rebalance based on total budget???

    # for ticker in settings check for new models and if they are active, ReAllocate weight and return star powers

    return True


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


def return_queen_controls(stars=stars):
    # num_of_stars = len(stars())
    queen_controls_dict = {
        "theme": "nuetral",
        "last_read_app": datetime.now(est),
        "stars": stars(),
        "ticker_settings": generate_queen_ticker_settings(),
        "buying_powers": generate_queen_buying_powers_settings(),
        "symbols_stars_TradingModel": generate_TradingModel()["MACD"],
        "power_rangers": init_PowerRangers(),
        "trigbees": {
            "buy_cross-0": "active",
            "sell_cross-0": "active",
            "ready_buy_cross": "not_active",
        },
    }
    return queen_controls_dict


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
    index_ticker_db__dir = os.path.join(db_root, "index_tickers")

    if os.path.exists(index_ticker_db__dir) == False:
        os.mkdir(index_ticker_db__dir)
        print("Ticker Index db Initiated")
        init_index_ticker(index_list, db_root, init=True)

    """ Return Index Charts & Data for All Tickers Wanted"""
    """ Return Tickers of SP500 & Nasdaq / Other Tickers"""
    # s = datetime.now()
    all_alpaca_tickers = api.list_assets()
    alpaca_symbols_dict = {}
    for n, v in enumerate(all_alpaca_tickers):
        if all_alpaca_tickers[n].status == "active":
            alpaca_symbols_dict[all_alpaca_tickers[n].symbol] = vars(
                all_alpaca_tickers[n]
            )

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

    index_ticker_db = return_index_tickers(
        index_dir=os.path.join(db_root, "index_tickers"), ext=".csv"
    )

    main_index_dict = index_ticker_db[0]
    main_symbols = index_ticker_db[1]
    not_avail_in_alpaca = [i for i in main_symbols if i not in alpaca_symbols_dict]
    main_symbols_full_list = [i for i in main_symbols if i in alpaca_symbols_dict]

    """ Return Index Charts & Data for All Tickers Wanted"""
    """ Return Tickers of SP500 & Nasdaq / Other Tickers"""

    return {
        "index_ticker_db": index_ticker_db,
        "main_index_dict": main_index_dict,
        "main_symbols_full_list": main_symbols_full_list,
        "not_avail_in_alpaca": not_avail_in_alpaca,
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
    index_ticker_db = ticker_universe["index_ticker_db"]
    main_index_dict = ticker_universe["main_index_dict"]
    main_symbols_full_list = ticker_universe["main_symbols_full_list"]
    not_avail_in_alpaca = ticker_universe["not_avail_in_alpaca"]

    db_return = {}
    for symbol in tqdm(main_symbols_full_list):
        try:
            db_return[symbol] = get_ticker_statatistics(symbol)
        except Exception as e:
            print(symbol, e)

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


def return_Best_Waves(df, rankname="maxprofit", top=False):
    if top:
        df = df.sort_values(rankname)
        return df.tail(top)
    else:
        df = df.sort_values(rankname)
        return df


def analyze_waves(STORY_bee, ttframe_wave_trigbee=False):
    # len and profits
    groupby_agg_dict = {
        "winners_n": "sum",
        "losers_n": "sum",
        "maxprofit": "sum",
        "length": "mean",
        "time_to_max_profit": "mean",
    }
    # groupby_agg_dict = {'maxprofit': 'sum', 'length': 'mean', 'time_to_max_profit': 'mean'}

    if ttframe_wave_trigbee:
        # buy_cross-0
        wave_series = STORY_bee[ttframe_wave_trigbee]["waves"]["buy_cross-0"]
        upwave_dict = [wave_data for (k, wave_data) in wave_series.items() if k != "0"]
        df = pd.DataFrame(upwave_dict)
        df["winners"] = np.where(df["maxprofit"] > 0, "winner", "loser")
        df["winners_n"] = np.where(df["maxprofit"] > 0, 1, 0)
        df["losers_n"] = np.where(df["maxprofit"] < 0, 1, 0)
        df["winners"] = np.where(df["maxprofit"] > 0, "winner", "loser")
        groups = (
            df.groupby(["wave_blocktime"])
            .agg({"maxprofit": "sum", "length": "mean", "time_to_max_profit": "mean"})
            .reset_index()
        )
        df_return = groups.rename(
            columns={
                "length": "avg_length",
                "time_to_max_profit": "avg_time_to_max_profit",
                "maxprofit": "sum_maxprofit",
            }
        )

        df_bestwaves = return_Best_Waves(df=df, top=3)

        # show today only
        df_today_return = pd.DataFrame()
        df_today = split_today_vs_prior(df=df, timestamp="wave_start_time")["df_today"]
        df_day_bestwaves = return_Best_Waves(df=df_today, top=3)
        groups = (
            df_today.groupby(["wave_blocktime"])
            .agg({"maxprofit": "sum", "length": "mean", "time_to_max_profit": "mean"})
            .reset_index()
        )
        df_today_return = groups.rename(
            columns={
                "length": "avg_length",
                "time_to_max_profit": "avg_time_to_max_profit",
                "maxprofit": "sum_maxprofit",
            }
        )

        # sell_cross-0
        wave_series = STORY_bee[ttframe_wave_trigbee]["waves"]["sell_cross-0"]
        upwave_dict = [wave_data for (k, wave_data) in wave_series.items() if k != "0"]
        df = pd.DataFrame(upwave_dict)
        df["winners"] = np.where(df["maxprofit"] > 0, "winner", "loser")
        df["winners_n"] = np.where(df["maxprofit"] > 0, 1, 0)
        df["losers_n"] = np.where(df["maxprofit"] < 0, 1, 0)
        groups = (
            df.groupby(["wave_blocktime"])
            .agg(
                {
                    "winners_n": "sum",
                    "losers_n": "sum",
                    "maxprofit": "sum",
                    "length": "mean",
                    "time_to_max_profit": "mean",
                }
            )
            .reset_index()
        )
        df_return_wavedown = groups.rename(
            columns={
                "length": "avg_length",
                "time_to_max_profit": "avg_time_to_max_profit",
                "maxprofit": "sum_maxprofit",
            }
        )

        df_bestwaves_sell_cross = return_Best_Waves(df=df, top=3)

        df_best_buy__sell__waves = pd.concat(
            [df_bestwaves, df_bestwaves_sell_cross], axis=0
        )

        return {
            "df": df_return,
            "df_wavedown": df_return_wavedown,
            "df_today": df_today_return,
            "df_bestwaves": df_bestwaves,
            "df_bestwaves_sell_cross": df_bestwaves_sell_cross,
            "df_day_bestwaves": df_day_bestwaves,
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
                                df.groupby(["wave_blocktime"])
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
                print(e)

        #

        df_return = pd.DataFrame(d_return)
        df_agg_view_return = pd.DataFrame(d_agg_view_return)
        df_agg_view_return = df_agg_view_return.T

    # d_return2 = {} # every star and the data by grouping
    # for symbol_star, data in STORY_bee.items():
    #     d_return[symbol_star] = {}
    #     waves = data['waves']['story']
    #     df = pd.DataFrame(waves)
    #     # df = df[~df['macd_wave_length'] == 'NULL'].copy()
    #     if len(df) > 0:
    #         df['winners'] = np.where(df['maxprofit'] > 0, 'winner', 'loser')
    #         groups = df.groupby(['wave_blocktime']).agg({'maxprofit': 'sum', 'length': 'mean', 'time_to_max_profit': 'mean'}).reset_index()
    #         groups = groups.rename(columns={'length': 'avg_length'})
    #         d_return[symbol_star][trigbee] = groups

    return {
        "df": d_return,
        "d_agg_view_return": d_agg_view_return,
        "df_agg_view_return": df_agg_view_return,
        "df_bestwaves": df_bestwaves,
    }


def story_view(STORY_bee, ticker):  # --> returns dataframe
    storyview = [
        "ticker_time_frame",
        "macd_state",
        "current_macd_tier",
        "current_hist_tier",
        "macd",
        "hist",
        "mac_ranger",
        "hist_ranger",
    ]
    wave_view = ["length", "maxprofit", "time_to_max_profit", "wave_n"]
    ttframe__items = {k: v for (k, v) in STORY_bee.items() if k.split("_")[0] == ticker}
    return_view = []  # queenmemory objects in conscience {}
    return_agg_view = []
    for ttframe, conscience in ttframe__items.items():
        queen_return = {"star": ttframe}
        ttf_waves = {}

        # trigbees = ['buy_cross-0', 'sell_cross-0', 'ready_buy_cross']
        # for trig in trigbees:
        #     if trig in conscience['waves'].keys():
        #         last_buy_wave = [v for (k,v) in conscience['waves'][trig].items() if str((len(conscience['waves'][trig].keys()) - 1)) == str(k)][0]
        #         ttf_waves[trig] = last_buy_wave

        story = {k: v for (k, v) in conscience["story"].items() if k in storyview}
        p_story = {
            k: v
            for (k, v) in conscience["story"]["current_mind"].items()
            if k in storyview
        }

        last_buy_wave = [
            v
            for (k, v) in conscience["waves"]["buy_cross-0"].items()
            if str((len(conscience["waves"]["buy_cross-0"].keys()) - 1)) == str(k)
        ][0]
        last_sell_wave = [
            v
            for (k, v) in conscience["waves"]["sell_cross-0"].items()
            if str((len(conscience["waves"]["sell_cross-0"].keys()) - 1)) == str(k)
        ][0]
        # last_ready_buy_wave = [v for (k,v) in conscience['waves']['ready_buy_cross'].items() if str((len(conscience['waves']['ready_buy_cross'].keys()) - 1)) == str(k)][0]

        # all_buys = [v for (k,v) in conscience['waves']['buy_cross-0'].items()]
        # all_sells = [v for (k,v) in conscience['waves']['sell_cross-0'].items()]

        # ALL waves groups
        trigbee_waves_analzyed = analyze_waves(STORY_bee, ttframe_wave_trigbee=ttframe)
        return_agg_view.append(trigbee_waves_analzyed)

        # Current Wave View
        if "buy" in story["macd_state"]:
            current_wave = last_buy_wave
        else:
            current_wave = last_sell_wave

        wave_times = {k: i["wave_start_time"] for k, i in ttf_waves.items()}

        current_wave_view = {k: v for (k, v) in current_wave.items() if k in wave_view}
        obj_return = {**story, **current_wave_view}
        obj_return_ = {**obj_return, **p_story}
        queen_return = {**queen_return, **obj_return_}
        """append view"""
        return_view.append(queen_return)

    df = pd.DataFrame(return_view)
    df_agg = pd.DataFrame(return_agg_view)

    return {"df": df, "df_agg": df_agg, "current_wave": current_wave}


def story_view_combined(STORY_bee, ticker_list):  # --> returns dataframe
    storyview = [
        "ticker_time_frame",
        "macd_state",
        "current_macd_tier",
        "current_hist_tier",
        "macd",
        "hist",
        "mac_ranger",
        "hist_ranger",
    ]
    wave_view = ["length", "maxprofit", "time_to_max_profit", "wave_n"]
    ttframe__items = {
        k: v for (k, v) in STORY_bee.items() if k.split("_")[0] in ticker_list
    }
    return_view = []  # queenmemory objects in conscience {}
    return_agg_view = []
    for ttframe, conscience in ttframe__items.items():
        ticker, ttime, tframe = ttframe.split("_")
        queen_return = {"star": f'{ttime}"_"{tframe}'}
        ttf_waves = {}

        # trigbees = ['buy_cross-0', 'sell_cross-0', 'ready_buy_cross']
        # for trig in trigbees:
        #     if trig in conscience['waves'].keys():
        #         last_buy_wave = [v for (k,v) in conscience['waves'][trig].items() if str((len(conscience['waves'][trig].keys()) - 1)) == str(k)][0]
        #         ttf_waves[trig] = last_buy_wave

        story = {k: v for (k, v) in conscience["story"].items() if k in storyview}
        p_story = {
            k: v
            for (k, v) in conscience["story"]["current_mind"].items()
            if k in storyview
        }

        last_buy_wave = [
            v
            for (k, v) in conscience["waves"]["buy_cross-0"].items()
            if str((len(conscience["waves"]["buy_cross-0"].keys()) - 1)) == str(k)
        ][0]
        last_sell_wave = [
            v
            for (k, v) in conscience["waves"]["sell_cross-0"].items()
            if str((len(conscience["waves"]["sell_cross-0"].keys()) - 1)) == str(k)
        ][0]
        # last_ready_buy_wave = [v for (k,v) in conscience['waves']['ready_buy_cross'].items() if str((len(conscience['waves']['ready_buy_cross'].keys()) - 1)) == str(k)][0]

        # all_buys = [v for (k,v) in conscience['waves']['buy_cross-0'].items()]
        # all_sells = [v for (k,v) in conscience['waves']['sell_cross-0'].items()]

        # ALL waves groups
        trigbee_waves_analzyed = analyze_waves(STORY_bee, ttframe_wave_trigbee=ttframe)
        return_agg_view.append(trigbee_waves_analzyed)

        # Current Wave View
        if "buy" in story["macd_state"]:
            current_wave = last_buy_wave
        else:
            current_wave = last_sell_wave

        wave_times = {k: i["wave_start_time"] for k, i in ttf_waves.items()}

        current_wave_view = {k: v for (k, v) in current_wave.items() if k in wave_view}
        obj_return = {**story, **current_wave_view}
        obj_return_ = {**obj_return, **p_story}
        queen_return = {**queen_return, **obj_return_}
        """append view"""
        return_view.append(queen_return)

    df = pd.DataFrame(return_view)
    df_agg = pd.DataFrame(return_agg_view)

    return {"df": df, "df_agg": df_agg, "current_wave": current_wave}


def queen_orders_view(
    QUEEN, queen_order_state, cols_to_view=False, return_all_cols=False, return_str=True
):
    if cols_to_view:
        col_view = col_view
    else:
        col_view = [
            "honey",
            "$honey",
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
            # if 'running' in queen_order_state:
            #     df = df[col_view]
            # if 'profit_loss' in df.columns:
            #     df["profit_loss"] = df['profit_loss'].map("{:.2f}".format)
            # if "honey" in df.columns:
            #     df["honey"] = df['honey'].map("{:.2%}".format)
            # if "cost_basis" in df.columns:
            #     df["cost_basis"] = df['cost_basis'].map("{:.2f}".format)

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

def init_pollen_dbs(db_root, prod, queens_chess_piece='queen', queenKING=False):
    def init_queen_orders(pickle_file):
        db = {}
        db["queen_orders"] = pd.DataFrame([create_QueenOrderBee(queen_init=True)])
        PickleData(pickle_file=pickle_file, data_to_store=db)
        print("Order init")
        logging_log_message(msg="Orders init")

    if prod:
        # print("My Queen Production")
        # main_orders_file = os.path.join(db_root, 'main_orders.csv')
        PB_QUEEN_Pickle = os.path.join(db_root, f'{queens_chess_piece}{".pkl"}')
        PB_KING_Pickle = os.path.join(db_root, f'{"KING"}{".pkl"}')
        PB_App_Pickle = os.path.join(db_root, f'{queens_chess_piece}{"_App_"}{".pkl"}')
        PB_Orders_Pickle = os.path.join(db_root, f'{queens_chess_piece}{"_Orders_"}{".pkl"}')
        PB_queen_Archives_Pickle = os.path.join(db_root, f'{queens_chess_piece}{"_Archives_"}{".pkl"}')
        PB_QUEENsHeart_PICKLE = os.path.join(db_root, f'{queens_chess_piece}{"_QUEENsHeart_"}{".pkl"}')
    else:
        # print("My Queen Sandbox")
        PB_QUEEN_Pickle = os.path.join(db_root, f'{queens_chess_piece}{"_sandbox"}{".pkl"}')
        PB_KING_Pickle = os.path.join(db_root, f'{"KING"}{"_sandbox"}{".pkl"}')
        PB_App_Pickle = os.path.join(db_root, f'{queens_chess_piece}{"_App_"}{"_sandbox"}{".pkl"}')
        PB_Orders_Pickle = os.path.join(db_root, f'{queens_chess_piece}{"_Orders_"}{"_sandbox"}{".pkl"}')
        PB_queen_Archives_Pickle = os.path.join(db_root, f'{queens_chess_piece}{"_Archives_"}{"_sandbox"}{".pkl"}')
        PB_QUEENsHeart_PICKLE = os.path.join(db_root, f'{queens_chess_piece}{"_QUEENsHeart_"}{"_sandbox"}{".pkl"}')

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
        QUEEN = init_QUEEN(queens_chess_piece=queens_chess_piece)
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

    if os.path.exists(PB_KING_Pickle) == False:
        print("You Need a King")
        init_KING(pickle_file=PB_KING_Pickle)

    if queenKING:
        # st.write("prod", prod)
        st.session_state["PB_QUEEN_Pickle"] = PB_QUEEN_Pickle
        st.session_state["PB_App_Pickle"] = PB_App_Pickle
        st.session_state["PB_Orders_Pickle"] = PB_Orders_Pickle
        st.session_state["PB_queen_Archives_Pickle"] = PB_queen_Archives_Pickle
        st.session_state["PB_QUEENsHeart_PICKLE"] = PB_QUEENsHeart_PICKLE


    return {
        "PB_QUEEN_Pickle": PB_QUEEN_Pickle,
        "PB_App_Pickle": PB_App_Pickle,
        "PB_Orders_Pickle": PB_Orders_Pickle,
        "PB_queen_Archives_Pickle": PB_queen_Archives_Pickle,
        'PB_QUEENsHeart_PICKLE': PB_QUEENsHeart_PICKLE,
    }


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


# ### NEEDS TO BE WORKED ON TO ADD TO WORKERBEE
# def speedybee(QUEEN, queens_chess_piece, ticker_list): # if queens_chess_piece.lower() == 'workerbee': # return tics
#     ticker_list = ['AAPL', 'TSLA', 'GOOG', 'META']

#     s = datetime.now(est)
#     r = rebuild_timeframe_bars(ticker_list=ticker_list, build_current_minute=False, min_input=0, sec_input=30) # return all tics
#     resp = r['resp'] # return slope of collective tics
#     speedybee_dict = {}
#     slope_dict = {}
#     for symbol in set(resp['symbol'].to_list()):
#         df = resp[resp['symbol']==symbol].copy()
#         df = df.reset_index()
#         df_len = len(df)
#         if df_len > 2:
#             slope, intercept, r_value, p_value, std_err = stats.linregress(df.index, df['price'])
#             slope_dict[df.iloc[0].symbol] = slope
#     speedybee_dict['slope'] = slope_dict

#     # QUEEN[queens_chess_piece]['pollenstory_info']['speedybee'] = speedybee_dict

#     print("cum.slope", sum([v for k,v in slope_dict.items()]))
#     return {'speedybee': speedybee_dict}


# def return_snapshots(ticker_list):
#     # ticker_list = ['SPY', 'AAPL'] # TEST
#     """ The Following will convert get_snapshots into a dict"""
#     snapshots = api.get_snapshots(ticker_list)
#     # snapshots['AAPL'].latest_trade.price # FYI This also avhices same goal
#     return_dict = {}

#     # handle errors
#     error_dict = {}
#     for i in snapshots:
#         if snapshots[i] == None:
#             error_dict[i] = None

#     try:
#         for ticker in snapshots:
#             if ticker not in error_dict.keys():
#                     di = {ticker: {}}
#                     token_dict = vars(snapshots[ticker])
#                     temp_dict = {}
#                     # for k, v in token_dict.items():
#                     #     snapshots[ticker]


#                     for i in token_dict:
#                         unpack_dict = vars(token_dict[i])
#                         data = unpack_dict["_raw"] # raw data
#                         dataname = unpack_dict["_reversed_mapping"] # data names
#                         temp_dict = {i : {}} # revised dict with datanames
#                         for k, v in dataname.items():
#                             if v in data.keys():
#                                 t = {}
#                                 t[str(k)] = data[v]
#                                 temp_dict[i].update(t)
#                                 # if v == 't':
#                                 #     temp_dict[i]['timestamp_covert'] = convert_todatetime_string(data[v])
#                                 #     # temp_dict[i]['timestamp_covert_est'] =  temp_dict[i]['timestamp_covert'].astimezone(est)
#                                 #     # temp_dict[i]['timestamp_covert_est'] = data[v].astimezone(est)
#                             di[ticker].update(temp_dict)
#                     return_dict.update(di)

#     except Exception as e:
#         print("logme", ticker, e)
#         error_dict[ticker] = "Failed To Unpack"

#     return [return_dict, error_dict]
# # data = return_snapshots(ticker_list=['SPY', 'AAPL'])


def log_script(log_file, loginfo_dict):
    loginfo_dict = {"type": "info", "lognote": "someones note"}
    df = pd.read_csv(log_file, dtype=str, encoding="utf8")
    for k, v in loginfo_dict.items():
        df[k] = v.fillna(df[k])


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
