# QueenBee
import logging
from enum import Enum
from operator import sub
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
# from alpaca_trade_api.rest import TimeFrame, URL
# from alpaca_trade_api.rest_async import gather_with_concurrency, AsyncRest
from dotenv import load_dotenv
import threading
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
# from scipy.stats import linregress
from scipy import stats
import hashlib
import json
from collections import deque
import argparse
from QueenHive import KING, init_logging, story_view, logging_log_message, createParser, return_index_tickers, return_alpc_portolio, return_market_hours, return_dfshaped_orders, add_key_to_app, init_QUEEN, pollen_themes, init_app, check_order_status, slice_by_time, split_today_vs_prior, read_csv_db, update_csv_db, read_queensmind, read_pollenstory, pickle_chesspiece, speedybee, submit_order, return_timestamp_string, pollen_story, ReadPickleData, PickleData, return_api_keys, return_bars_list, refresh_account_info, return_bars, init_index_ticker, print_line_of_error, add_key_to_QUEEN
# from QueenHive import return_macd, return_VWAP, return_RSI, return_sma_slope



from pymongo import MongoClient; import pymongo
import certifi
import pprint
import pytz


est = pytz.timezone("US/Eastern")

# script arguments
parser = createParser()
namespace = parser.parse_args()
queens_chess_piece = namespace.qcp # 'castle', 'knight' 'queen'
# queens_chess_piece = 'queen'
# prod = False
if queens_chess_piece.lower() not in ['mongo']:
    print("wrong chess move")
    sys.exit()
if namespace.prod.lower() == "true":
    prod = True
else:
    prod = False

load_dotenv()
main_root = os.getcwd()
db_root = os.path.join(main_root, 'db')
db_app_root = os.path.join(db_root, 'app')

init_logging(queens_chess_piece=queens_chess_piece, db_root=db_root)

# client = pymongo.MongoClient("mongodb+srv://stefanstapinski:<Family33!>@cluster0.99putso.mongodb.net/?retryWrites=true&w=majority")
#connection
mongo_conn = MongoClient('mongodb+srv://cluster0.99putso.mongodb.net/test?retryWrites=true', username='stefanstapinski', password='Family33!', authSource='admin', authMechanism='SCRAM-SHA-1', tlsCAFile=certifi.where())

# databases
QUEEN_db = mongo_conn['QUEEN']

db = mongo_conn['pollen_app']
# db func
# db.create_collection('test2')
db.list_collection_names()

# Collections
APP_c = db['test2']


pprint.pprint(APP_c.find_one())

post = {'a': 1, 'b': 2}
post_id = APP_c.insert_one(post).inserted_id
pprint.pprint(APP_c.find_one())

new_posts = [{'a': 1, 'b': 2}, {'a': 1, 'b': datetime.datetime.now().astimezone(est)}]
result = APP_c.insert_many(new_posts)

mylist= []
for d in db['test2'].find():
    mylist.append(d)

def mongo_QUEEN(db, collection, payload):
    result = APP_c.insert_many(new_posts)
    return True


def init_mongoQUEEN(queens_chess_piece):
    QUEEN = { # The Queens Mind
        'queen_chess_piece': {queens_chess_piece},
        'prod': {""},
        'last_modified': {datetime.datetime.now().astimezone(est)},
        'command_conscience': { 'orders': { 'requests': [],
                                        'submitted': [],
                                        'running': [],
                                        'running_close': []}
                                            },
        'queen_orders': {},
        'portfolios': {'Jq': {'total_investment': 0, 'currnet_value': 0}},
        'heartbeat': {}, # ticker info ... change name
        'kings_order_rules': {},
        'queen_controls': { 'theme': 'nuetral',
                            'app_order_requests': [],
                            'orders': [],
                            'last_read_app': datetime.datetime.now().astimezone(est),},
        'errors': {},
        'client_order_ids_qgen': {},
        'power_rangers': 'Create Rangers that hold Points to each Tier',#  get done else where init_PowerRangers(),
        'triggerBee_frequency': {}, # hold a star and the running trigger
        'STORY_bee': {},
    }

    # QUEEN_collections = db.list_collection_names()
    # QUEEN = {k: QUEEN[k] for k in QUEEN.keys()}
    return QUEEN


def add_key_to_mongoQUEEN(db, QUEEN, queens_chess_piece): # returns QUEEN
    update = False
    q_keys = QUEEN.keys()
    q_keys_mongo = db.list_collection_names()
    latest_queen = init_mongoQUEEN(queens_chess_piece=queens_chess_piece)
    for k, v in latest_queen.items():
        if k not in q_keys:
            QUEEN[k] = v
            db.create_collection(k)
            update=True
            msg = f'{k}{" : Key Added to "}{queens_chess_piece}'
            print(msg)
            print(db.list_collection_names())
            logging.info(msg)
        if k not in q_keys_mongo:
            db.create_collection(k)
            update=True
            msg = f'{k}{" : Key Added to "}{queens_chess_piece}'
            print(msg)
            print(db.list_collection_names())
            logging.info(msg)

    return {'QUEEN': QUEEN, 'update': update}


# Pollen QUEEN
pollen = read_queensmind(prod)
QUEEN = pollen['queen']
STORY_bee = pollen['STORY_bee']
POLLENSTORY = read_pollenstory()

mongoQUEEN = init_mongoQUEEN(queens_chess_piece='mongoQUEEN')
mongoQUEEN_ = add_key_to_mongoQUEEN(db=db, QUEEN=mongoQUEEN, queens_chess_piece='mongoQUEEN')