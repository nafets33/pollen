# QueenBee
import logging
import time
import os
import pandas as pd
import numpy as np
import sys
from dotenv import load_dotenv
import sys
from datetime import datetime, timedelta, date
import pytz
import asyncio
import aiohttp
from collections import defaultdict, deque
import argparse
import ast ## WORKERBEE TEMP FIX UNTIL LATER FIX PRICEINFO STORAGE
from decimal import Decimal, ROUND_DOWN
import uuid
import requests
import json
import ipdb



sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from chess_piece.king import main_index_tickers, hash_string, kingdom__global_vars, print_line_of_error, return_QUEENs__symbols_data, PickleData, return_QUEEN_KING_symbols, return_crypto_snapshots
from chess_piece.queen_hive import (kingdom__grace_to_find_a_Queen,
                                    init_charlie_bee, 
                                    init_queenbee, 
                                    power_amo, 
                                    return_queenking_board_symbols,
                                    star_ticker_WaveAnalysis, 
                                    return_queen_orders__query, 
                                    initialize_orders, 
                                    init_clientUser_dbroot, 
                                    process_order_submission, 
                                    get_best_limit_price, 
                                    hive_dates, 
                                    send_email, 
                                    init_logging, 
                                    convert_to_float, 
                                    order_vars__queen_order_items, 
                                    return_market_hours, 
                                    check_order_status, stars,  
                                    timestamp_string, 
                                    submit_order, 
                                    add_key_to_QUEEN, 
                                    update_sell_date,
                                    return_Ticker_Universe,
                                    refresh_broker_account_portolfio
                                    )
from chess_utils.trigrule_utils import check_trigrule_conditions, get_existing_trigrule_orders, flip_queen_trigger_rule_status
from chess_piece.queen_mind import refresh_chess_board__revrec, weight_team_keys, kings_order_rules, return_long_short
from chess_piece.pollen_db import PollenDatabase, PollenJsonEncoder, PollenJsonDecoder
from chess_piece.workerbees_snap import process_priceinfo_snapshot
from chess_utils.robinhood_crypto_utils import CryptoAPITrading
from chess_utils.conscience_utils import story_return
# from chess_utils.websocket_manager import manager

import copy
from tqdm import tqdm

# Load environment variables
load_dotenv()

pg_migration = os.getenv('pg_migration')
upsert_to_main_server = os.getenv('upsert_to_main_server')
server = os.getenv('server')

pd.options.mode.chained_assignment = None
est = pytz.timezone("US/Eastern")
# utc = pytz.timezone('UTC')

notification_list = deque([], 500)

# ###### GLOBAL # ######
KING = kingdom__grace_to_find_a_Queen()
king_G = kingdom__global_vars()
ARCHIVE_queenorder = king_G.get('ARCHIVE_queenorder') # ;'archived'
active_order_state_list = king_G.get('active_order_state_list') # = ['running', 'running_close', 'submitted', 'error', 'pending', 'completed', 'completed_alpaca', 'running_open', 'archived_bee']
active_queen_order_states = king_G.get('active_queen_order_states') # = ['submitted', 'accetped', 'pending', 'running', 'running_close', 'running_open']
CLOSED_queenorders = king_G.get('CLOSED_queenorders') # = ['completed', 'completed_alpaca']
RUNNING_Orders = king_G.get('RUNNING_Orders') # = ['running', 'running_open']
RUNNING_OPEN = king_G.get('RUNNING_OPEN') # ['running_open']
RUNNING_CLOSE_Orders = king_G.get('RUNNING_CLOSE_Orders') # = ['running_close']
WT = weight_team_keys()
TRINITY_ = "trinity_"
reverse_indexes = ['SH', 'PSQ']
API_KEY = os.getenv('fastAPI_key')
API_URL = os.getenv('fastAPI_url')
wash_sale_rule = []

# crypto
crypto_currency_symbols = ['BTCUSD', 'ETHUSD', 'BTC/USD', 'ETH/USD']
# crypto_symbols__tickers_avail = ['BTC/USD', 'ETH/USD']
def symbol_is_crypto(symbol, crypto_currency_symbols=crypto_currency_symbols):
    if symbol in crypto_currency_symbols:
        return True
    else:
        return False

coin_exchange = "CBSE"
# ACTIVE_SYMBOLS = list(return_Ticker_Universe().get('alpaca_symbols_dict')) + crypto_currency_symbols
alpaca_symbols_dict = return_Ticker_Universe().get('alpaca_symbols_dict')
ACTIVE_SYMBOLS = list(alpaca_symbols_dict.keys()) + crypto_currency_symbols

# misc
exclude_conditions = [
    'B','W','4','7','9','C','G','H','I','M','N',
    'P','Q','R','T','V','Z'
] # 'U'

def check_user_websocket_status(client_user, prod, API_URL, upsert_to_main_server=upsert_to_main_server):
    """
    Check if a specific user has an active WebSocket connection.
    
    Args:
        client_user: Username to check
        prod: Boolean indicating production (True) or sandbox (False) environment
        API_URL: Base URL for the API
        upsert_to_main_server: Whether to use main server URL
    
    Returns:
        bool: True if user is connected in specified environment, False otherwise
    """
    if upsert_to_main_server:
        API_URL = os.getenv('main_fastAPI_url')
    
    # ✅ Add prod parameter to query string
    endpoint = f"{API_URL}/api/data/ws_status/{client_user}?prod={'true' if prod else 'false'}"
    
    try:
        response = requests.get(endpoint, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            
            environment = "PROD" if prod else "SANDBOX"
            is_connected = data.get('connected', False)
            connection_count = data.get('connection_count', 0)
            
            # ✅ Show environment-specific status
            status = '✅ YES' if is_connected else '❌ NO'
            logging.info(f"🔌 {data.get('client_user')} [{environment}] Connected: {status} ({connection_count} connections)")
            
            # ✅ Log connection details if connected
            if is_connected and connection_count > 0:
                connections = data.get('connections', [])
                for conn in connections:
                    conn_env = conn.get('environment', 'unknown')
                    logging.info(f"   └─ Connection: {conn_env}")

            return is_connected
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"❌ CONNECTION ERROR: Could not connect to {API_URL}")
        print(f"💡 Make sure FastAPI server is running!")
        return False
    except requests.exceptions.Timeout:
        print(f"⏱️  TIMEOUT: Request took longer than 5 seconds")
        return False
    except Exception as e:
        print(f"❌ Error checking status: {e}")
        import traceback
        traceback.print_exc()
        return False

def story_grid_update(prod, QUEEN_KING, revrec, client_user, API_KEY, API_URL, upsert_to_main_server=upsert_to_main_server):
    if upsert_to_main_server:
        API_URL = os.getenv('main_fastAPI_url')
    endpoint = f"{API_URL}/api/data/trigger_story_grid_update"
    revrec_copy = copy.deepcopy(revrec)
    QUEEN_KING_copy = copy.deepcopy(QUEEN_KING)
    df_story = story_return(QUEEN_KING_copy, revrec_copy)
    
    revrec_for_ws = {'storygauge': df_story.to_dict('records')}
    
    # Prepare payload
    payload = {
        'client_user': client_user,
        'api_key': API_KEY,
        'prod': prod,
        'revrec': revrec_for_ws,
        'toggle_view_selection': 'queen',
    }

    try:
        # Send HTTP POST with PollenJsonEncoder
        response = requests.post(
            endpoint,
            data=json.dumps(payload, cls=PollenJsonEncoder),
            headers={'Content-Type': 'application/json'},
            timeout=15
        )
        
        # print(f"\n📥 Response Status: {response.status_code}")
        
        if response.status_code == 404:
            print(f"❌ 404 NOT FOUND")
            print(f"💡 The endpoint might not exist. Check your fastapi_router.py")
            
            # Try to get OpenAPI docs tehehee
            try:
                docs_response = requests.get(f"{API_URL}/docs")
                if docs_response.status_code == 200:
                    print(f"✅ FastAPI docs available at: {API_URL}/docs")
                    print(f"   Check there for available endpoints")
            except:
                pass
            
            return False
        
        if response.status_code == 200:
            result = response.json()
            # print(f"✅ Status: {result.get('status')}")
            # print(f"💬 Message: {result.get('message')}")
            if result.get('status') == 'success':
                logging.info(f"\n🎉 SUCCESS! {client_user} Story grid update sent via WebSocket")
                return True
            elif result.get('status') == 'warning':
                logging.warning(f"\n⚠️  WARNING: {result.get('message')}")
                print(f"💡 Connected users: {result.get('connected_users', [])}")
                return False
            else:
                logging.error(f"\n❌ ERROR: {result.get('message')}")
                return False
        else:
            logging.error(f"❌ HTTP Error: {response.status_code}")
            logging.error(f"Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        logging.error(f"\n⏱️  TIMEOUT: Request took longer than 15 seconds")
        return False
    except requests.exceptions.ConnectionError:
        logging.error(f"\n❌ CONNECTION ERROR: Could not connect to {API_URL}")
        logging.error(f"💡 Make sure FastAPI server is running!")
        return False
    except Exception as e:
        logging.error(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def init_broker_orders(api, BROKER, start_date=None, end_date=None):
    # Start and end dates for the last 100 days
    if not start_date:
        end_date = datetime.now() + timedelta(days=1)
        start_date = datetime.now() - timedelta(days=365)

    # Initialize an empty DataFrame for broker orders
    broker_orders = BROKER.get('broker_orders', pd.DataFrame())
    if not isinstance(broker_orders, pd.DataFrame):
        broker_orders = pd.DataFrame()

    # Iterate over 5-day intervals
    current_date = start_date
    while current_date < end_date:
        next_date = min(current_date + timedelta(days=5), end_date)
        
        # Format dates for the API call
        start_date_str = current_date.strftime("%Y-%m-%d")
        end_date_str = next_date.strftime("%Y-%m-%d")
        
        # Fetch API orders for the 5-day interval
        api_orders = initialize_orders(api, start_date_str, end_date_str, symbols=False, limit=500)
        
        # Process closed and open orders
        queen_orders_closed = api_orders.get('closed', [])
        queen_orders_open = api_orders.get('open', [])
        
        c_order_ids_dict_closed = [vars(order)['_raw'] for order in queen_orders_closed]
        c_order_ids_dict_open = [vars(order)['_raw'] for order in queen_orders_open]
        
        # Combine orders into a single list
        interval_orders = c_order_ids_dict_closed + c_order_ids_dict_open

        # If orders exist, append them to the broker_orders DataFrame
        if interval_orders:
            interval_df = pd.DataFrame(interval_orders)
            if not interval_df.empty:
                interval_df.set_index('client_order_id', drop=False, inplace=True)
                interval_df = interval_df[~(interval_df.index.isin(broker_orders.index))]
                if len(interval_df) > 0:
                    print("new orders to add num: ", len(interval_df))
                    broker_orders = pd.concat([broker_orders, interval_df])
        
        # Move to the next 5-day interval
        current_date = next_date

    # Save the broker orders to the BROKER dictionary
    BROKER['broker_orders'] = broker_orders

    return BROKER


def update_broker_order_status(BROKER, order_status):
    try:
        broker_orders = BROKER['broker_orders']
        client_order_id = order_status.get('client_order_id')
        
        # Check if order exists and compare dictionaries
        if client_order_id in broker_orders.index:
            existing_order = broker_orders.loc[client_order_id].to_dict()
            
            # Find and print differences
            differences = {}
            for key in set(list(existing_order.keys()) + list(order_status.keys())):
                existing_value = existing_order.get(key)
                new_value = order_status.get(key)
                
                if existing_value != new_value:
                    differences[key] = {
                        'old': existing_value,
                        'new': new_value
                    }
            
            # If no differences, return False
            if not differences:
                # print("no changes detected for order:", client_order_id)
                return False
            
            # Print the differences
            print(f"\n{'='*60}")
            print(f"Broker Order Update Detected: {client_order_id}")
            print(f"{'='*60}")
            for key, values in differences.items():
                print(f"  {key}:")
                print(f"    OLD: {values['old']}")
                print(f"    NEW: {values['new']}")
            print(f"{'='*60}\n")
        
        # Create new order DataFrame
        df_token = pd.DataFrame([order_status]).set_index('client_order_id', drop=False)
        
        # Remove old order if it exists
        if client_order_id in broker_orders.index:
            broker_orders = broker_orders[broker_orders['client_order_id'] != client_order_id]
        
        # Add updated order
        broker_orders = pd.concat([broker_orders, df_token])
        BROKER['broker_orders'] = broker_orders
        
        logging.info(f"Broker order updated: {client_order_id}")
        return True
        
    except Exception as e:
        print_line_of_error("broker update failed")
        return False


def generate_client_order_id(ticker_time_frame, trig, sellside_client_order_id=False): # generate using main_order table and trig count
    # WORKERBEE THIS NEED TO BE MORE UNIQUE
    random_suffix = str(uuid.uuid4())[:8]
    temp_date = datetime.now().strftime("%y-%m-%d %M.%S.%f")
    order_string = f'{ticker_time_frame}-{trig}-{temp_date}-{random_suffix}'
    order_id = hash_string(order_string)
    
    if sellside_client_order_id:
        order_id = f'{"close__"}{order_id}'
    else:        
        order_id = f'{"run__"}{order_id}'
    
    return order_id


def submit_order_validation(ticker, qty, side, portfolio, run_order_idx=False, crypto=False):
    def func_return(qty=False, queen_order_state=False, stop_order=False, qty_correction=False, log_msg=('msg'), log=False):
        return {
            'qty': qty,
            'queen_order_state': queen_order_state,
            'stop_order': stop_order,
            'qty_correction': qty_correction,
            'log_msg': log_msg,
            'log': log,
        }
    try:
        ticker = ticker.replace('/', '') if crypto else ticker
        # print("START of submit order validation  crypto: ", crypto, ticker, qty, side)
        position = int(float(portfolio[ticker]['qty_available'])) if portfolio.get(ticker) else 0

        if side == 'buy':
            # if crypto check avail cash to buy
            # check against buying power validate not buying too much of total portfolio
            if position < 0:
                print("you are short, buying to cover")
                if qty  > abs(position):
                    print("you are short, buying to cover ADJUST NEEDED")
                    msg = (f' {ticker} buying too much you need to cover first, adjusting qty cover to {abs(position)}')
                    return func_return(qty=abs(position), qty_correction=True, log=True, log_msg=msg)
            elif qty < 1:
                if not crypto:
                    msg = (f'{ticker} Qty Value Not Valid (less then 1) setting to 1')
                    qty = 1.0
                    qty_correction = True
                    logging.warning("CORRECTION on BUY Quanity, Qty < 1 setting to 1")
                    return func_return(qty, qty_correction=qty_correction, log=True, log_msg=msg)
                else:
                    msg = ('Buy Order Validated')
                    return func_return()
            else:
                msg = ('Buy Order Validated')
                return func_return()
        elif side == 'sell': # sel == sell
            # print("check portfolio has enough shares to sell")
            if ticker not in portfolio.keys() or position == 0:
                msg = f'submit order validation({ticker}), MISSING_TICKER ARCHVING ORDER <<<<< >POSITION: {position}'
                return func_return(queen_order_state='archived', stop_order=True, log_msg=msg, log=True)
            elif position < 0:
                msg = (f"ARCHVING ORDER, SHORTING, Scenario Not Added {run_order_idx}")
                return func_return(qty, queen_order_state='archived', stop_order=True, log_msg=msg, log=True)
            elif position > 0 and position < qty: # long
                msg = (f'submit order validation() {ticker} #of shares avail: {position} >>> NOT enough shares avail to sell, updating sell qty')            
                return func_return(qty=position, qty_correction=True, log_msg=msg, log=True)
            elif position > 0 and (position - qty) < 0:
                msg = (f'submit order validation() {ticker} #of shares avail: {position} >>> NOT enough shares avail to sell, updating sell qty')            
                return func_return(qty=position, qty_correction=True, log_msg=msg, log=True)
            else:
                msg = ("Sell Order Validated")
                return func_return()

    except Exception as e:
        print("order validaiton", e)
        print_line_of_error()
        sys.exit()


def return_closing_orders_df(QUEEN, exit_order_link): # returns linking order
    df = QUEEN['queen_orders']
    origin_closing_orders = df[(df['exit_order_link'] == exit_order_link)].copy()
    
    if len(origin_closing_orders) > 0:
        return origin_closing_orders
    else:
        return ''


def return_multiple_closing_orders(queen_orders, exit_order_links): # returns linking order

    origin_closing_orders = queen_orders[(queen_orders['exit_order_link'].isin(exit_order_links))].copy()
    
    if len(origin_closing_orders) > 0:
        return origin_closing_orders
    else:
        return ''


def get_priceinfo_snapshot(api, ticker, crypto):
    try:
        snap = api.get_snapshot(ticker) if crypto == False else return_crypto_snapshots(ticker)
        if crypto:
            snap = snap[ticker]
            priceinfo_order = {'price': snap['latestQuote']['ap'], 'bid': snap['latestQuote']['bp'], 
                            'ask': snap['latestQuote']['ap'], 
                            'bid_ask_var': snap['latestQuote']['bp']/snap['latestQuote']['ap']}
        else:
            ask = snap.latest_quote.ask_price
            price = snap.latest_trade.price
            if ask == 0 or price == 0:
                print("ERROR Price OR Ask is 0 Ignore: ", ticker, snap)
                return {}
            
            priceinfo_order = {
                            'price': snap.latest_trade.price, 
                            'bid': snap.latest_quote.bid_price, 
                            'ask': snap.latest_quote.ask_price, 
                            'bid_ask_var': snap.latest_quote.bid_price/snap.latest_quote.ask_price
                            }
        
        priceinfo_order['ticker'] = ticker
        
        return priceinfo_order
    except Exception as e:
        print("SNAP CALL ERROR", e, ticker)
        # WORKERBEE handle error get priceinfo from YAHOO
        return {}


def handle_broker(broker):

    if isinstance(broker, list):
        print("broker is a list, selecting first broker", broker)
        broker = broker[0]  # WORKERBEE handle multiple brokers later
    if broker == 'queens_choice':
        print("WORKERBEE fix REMOVE queens_choice broker")
        broker = 'alpaca'  # WORKERBEE fix REMOVE queens_choice broker
    elif broker == 'alpaca':
        pass
    else:
        print("broker NOT FOUND, using alpaca", broker)
        broker = 'alpaca'  # WORKERBEE fix REMOVE queens_choice broker
    
    return broker


def execute_buy_order(broker, order_key, prod, api, blessing, ticker, ticker_time_frame, trig, wave_amo, order_type='market', side='buy', crypto=False, limit_price=False, portfolio=None, trading_model=False, ACTIVE_SYMBOLS=ACTIVE_SYMBOLS, trigger_buy=False):
    try:
        def update__validate__qty(crypto, current_price, limit_price, wave_amo):
            if crypto:
                limit_price = round(limit_price) if limit_price else limit_price
                qty_order = float(round(wave_amo / current_price, 8))
            else:
                limit_price = round(limit_price, 2) if limit_price else limit_price
                qty_order = float(round(wave_amo / current_price, 0))

            return limit_price, qty_order
        
        # WORKERBEE handle active symbols allowed to buy. / put in error checker for them instead
        # if ticker not in ACTIVE_SYMBOLS:
        #     logging.error(f"{ticker} No Longer Active symbol")
        #     return {'executed': False}

        broker = handle_broker(broker)

        if not crypto:
            # check again
            crypto = True if ticker in crypto_currency_symbols else False
        
        tic, tframe, tperiod = ticker_time_frame.split("_")
        star = f'{tframe}_{tperiod}'
        robinhood_crypto_ticker = tic.replace('/', '-') if ticker in crypto_currency_symbols else None

        # get latest pricing
        priceinfo_order = get_priceinfo_snapshot(api, ticker, crypto)
        if not priceinfo_order:
            print(f"ERROR on GETTING PRICE INFO for {ticker}")
            return {'executed': False}

        order_vars = blessing
        limit_price = limit_price if limit_price != False else False
        limit_price, qty_order = update__validate__qty(crypto=crypto, current_price=priceinfo_order['price'], limit_price=limit_price, wave_amo=wave_amo)
        if limit_price:
            order_type = 'limit'
        
        # Client Order Id
        client_order_id__gen = generate_client_order_id(ticker_time_frame=ticker_time_frame, trig=trig)
        
        # BROKER HANDLE HERE WORKERBEE (send in a combined total portfolio? how to handle this split)
        if portfolio is not None:
            order_val = submit_order_validation(ticker=ticker, qty=qty_order, side=side, portfolio=portfolio, crypto=crypto)                    
            if order_val.get('log'):
                logging.warning(order_val.get('log_msg'))
            if order_val.get('qty_correction'):
                logging.warning(order_val.get('log_msg'))
                # QUEEN['queen_orders'].at[run_order_idx, 'validation_correction'] = 'true' # WORKERBEE handle later
                qty_order = order_val.get('qty')
       # BROKER HANDLE HERE WORKERBEE
        if broker == 'queens_choice' or broker == 'alpaca':
            # Submit Order
            order_submit = submit_order(api=api, 
                                        symbol=ticker, 
                                        type=order_type, 
                                        qty=qty_order, 
                                        side=side, 
                                        client_order_id=client_order_id__gen, 
                                        limit_price=limit_price) # buy
            if 'error' in order_submit.keys():
                print(f'{ticker_time_frame} Order Failed log in Hive, Log so you can make this only a warning')
                logging.error(f"{ticker} ERROR on Submiting Order")
                return {'executed': False}
        elif broker == 'robinhood':
            if crypto:
                api_rh = CryptoAPITrading()
                order = api_rh.place_order(
                        client_order_id=client_order_id__gen,
                        side=side,
                        order_type=order_type,
                        symbol=robinhood_crypto_ticker, #"BTC-USD",
                        order_config={"asset_quantity": str(qty_order)}#{"asset_quantity": "0.0001"}
        )
            else:
                print("Robinhood Order Not Implemented")
                return {'executed': False}


        # logging.info("order submit")
        order = vars(order_submit.get('order'))['_raw']
        # print("SUBMIT ORDER", client_order_id__gen, order.get('client_order_id'))

        if 'borrowed_funds' not in order_vars.keys():
            order_vars['borrowed_funds'] = False
        order_vars['qty_order'] = qty_order
        
        new_queen_order = process_order_submission(
            broker=broker,
            trading_model=trading_model, 
            order=order, 
            order_vars=order_vars,
            trig=trig,
            symbol=ticker,
            ticker_time_frame=ticker_time_frame,
            star=star,
            priceinfo=priceinfo_order
        )

        # logging.info(f"SUCCESS on BUY for {ticker}")
        msg = (f'EXECUTE BUY ORDER {ticker} {trig} {ticker_time_frame} {round(wave_amo,2):,}')

        return {'executed': True, 'msg': msg, 'new_queen_order': new_queen_order, 'priceinfo_order': priceinfo_order, 'trigger_buy': trigger_buy}

    except Exception as e:
        print_line_of_error(f"ERROR Ex BUY Order..Full Failure {ticker_time_frame} ERROR is {e}")
        return {'executed': False}


def execute_sell_order(broker, prod, api, QUEEN, king_eval_order, ticker, ticker_time_frame, trig, run_order_idx, crypto=False, limit_price=False, portfolio=None, order_type='market', side='sell', ACTIVE_SYMBOLS=ACTIVE_SYMBOLS):
    try:
        if ticker not in ACTIVE_SYMBOLS:
            print(f"{ticker} No Longer Active symbol")
            return {'executed': False}

        tic, tframe, tperiod = ticker_time_frame.split("_")
        star = f'{tframe}_{tperiod}'
        
        def update__sell_qty(crypto, limit_price, sell_qty):
            # flag crypto
            if crypto:
                if limit_price:
                    limit_price = round(limit_price)
                    sell_qty = round(sell_qty)
            else:
                if limit_price:
                    limit_price = round(limit_price, 2)                    
            
            return limit_price, sell_qty

        # portfolio = return_alpc_portolio(api)['portfolio']
        QUEEN = refresh_broker_account_portolfio(api, QUEEN)
        portfolio = QUEEN['portfolio']
        
        # get latest pricing
        priceinfo_order = get_priceinfo_snapshot(api, ticker, crypto)
        if not priceinfo_order:
            print(f"ERROR on GETTING PRICE INFO for {ticker}")
            return {'executed': False}

        run_order_client_order_id = QUEEN['queen_orders'].at[run_order_idx, 'client_order_id']
        order_vars = king_eval_order['order_vars']

        # close out order variables
        sell_qty = float(king_eval_order['order_vars']['sell_qty']) # float(order_obj['filled_qty'])


        limit_price, sell_qty = update__sell_qty(crypto, limit_price, sell_qty)

        # Validate Order
        order_val = submit_order_validation(ticker=ticker, qty=sell_qty, side=side, 
                                            portfolio=portfolio, run_order_idx=run_order_idx,
                                            crypto=crypto,
                                            )

        if order_val.get('log'):
            logging.error(order_val.get('log_msg'))
        if order_val.get('stop_order'):
            QUEEN['queen_orders'].at[run_order_idx, 'queen_order_state'] = 'completed_alpaca'
            QUEEN['queen_orders'].at[run_order_idx, 'order_trig_sell_stop'] = True
            QUEEN['queen_orders'].at[run_order_idx, 'qty_available'] = 0
            return {'executed': False, 'refresh': True}
        if order_val.get('qty_correction'):
            logging.warning(order_val.get('log_msg'))
            QUEEN['queen_orders'].at[run_order_idx, 'validation_correction'] = 'true'
            sell_qty = order_val.get('qty')

        # Generate Client Order Id
        client_order_id__gen = generate_client_order_id(ticker_time_frame=ticker_time_frame, trig=trig, sellside_client_order_id=run_order_client_order_id)
        send_close_order = submit_order(api=api, 
                                        side=side, 
                                        symbol=ticker, 
                                        qty=sell_qty, 
                                        type=order_type, 
                                        client_order_id=client_order_id__gen, 
                                        limit_price=limit_price) 

        if 'error' in send_close_order.keys():
            print(f'{ticker_time_frame} Order Failed log in Hive, Log so you can make this only a warning')
            return {'executed': False}


        send_close_order = vars(send_close_order['order'])['_raw']
                            
        if limit_price:
            print("seeking Honey?")
        
        if 'borrowed_funds' not in order_vars.keys():
            order_vars['borrowed_funds'] = False
        
        # Order Vars 
        new_queen_order = process_order_submission(
            broker=broker,
            trading_model=False,
            order=send_close_order, 
            order_vars=order_vars, 
            trig=trig, 
            exit_order_link=run_order_client_order_id,
            symbol=ticker,
            ticker_time_frame=ticker_time_frame,
            star=star,
            priceinfo=priceinfo_order
        )

        msg = (f'ExOrder SELL {trig} {ticker_time_frame}')
        print(msg)

        return{'executed': True, 'msg': msg, 'new_queen_order': new_queen_order, 'priceinfo_order': priceinfo_order}

    except Exception as e:
        print("Error Ex Order..Full Failure" , ticker_time_frame, e, print_line_of_error())


def return_origin_order(df_queenorders, exit_order_link):
    origin_order_q = df_queenorders[df_queenorders['client_order_id'] == exit_order_link].copy()
    if len(origin_order_q) > 0:
        origin_idx = origin_order_q.iloc[-1].name
        origin_order = origin_order_q.iloc[-1].to_dict()
        return {'origin_order': origin_order, 'origin_idx': origin_idx}
    else:
        return {'origin_order': ''}


def fix_crypto_ticker(QUEEN, ticker, idx): # order manage
    if ticker not in crypto_currency_symbols:
        return ticker
    
    # fix symbol for crypto
    if ticker == 'BTC/USD':
        print("correcting symbol for ", ticker)
        QUEEN['queen_orders'].at[idx, 'ticker'] = 'BTCUSD'
        ticker = "BTCUSD"
    if ticker == 'ETH/USD':
        print("correcting symbol for ", ticker)
        QUEEN['queen_orders'].at[idx, 'ticker'] = 'ETHUSD'
        ticker = "ETHUSD"
        
    return ticker


def update_origin_order_cost_basis_current(QUEEN, queen_order_idx, priceinfo, instance=1):
    qty_avail = float(QUEEN['queen_orders'].at[queen_order_idx, 'qty_available'])
    # current_ask = float(QUEEN['queen_orders'].at[queen_order_idx, 'filled_avg_price'])
    current_bid = float(priceinfo['current_bid'])
    if qty_avail > 0:
        QUEEN['queen_orders'].at[queen_order_idx, 'cost_basis_current'] = qty_avail * current_bid
    else:
        QUEEN['queen_orders'].at[queen_order_idx, 'cost_basis_current'] = 0
        print(f"{instance} update_origin_order_cost_basis_current qty_avail <= 0 {priceinfo} orderId: {queen_order_idx}, Qty Avail: {qty_avail}")
    
    return QUEEN['queen_orders'].loc[queen_order_idx].to_dict()

def update_latest_queen_order_status(QUEEN, queen_order_idx, order_status, save_order): # updates qty and cost basis from Alpaca

    def str_value_check(val1, val2, field_name=None):
        """Compare values with field-specific handling"""
        # Handle numeric fields specifically
        numeric_fields = {'filled_qty'}
        
        if field_name in numeric_fields:
            try:
                return float(val1) == float(val2)
            except (ValueError, TypeError):
                pass
        
        # Handle timestamp comparison
        str1, str2 = str(val1), str(val2)
        if 'T' in str1 and 'T' in str2 and str1.endswith('Z') and str2.endswith('Z'):
            return str1[:23] == str2[:23]
        
        return str1 == str2

    queen_order_keys = QUEEN['queen_orders'].loc[queen_order_idx].to_dict().keys()
    for order_key, order_value in order_status.items():
        if order_key in ['source']:
            continue
        if order_key in queen_order_keys:
            current_value = QUEEN['queen_orders'].at[queen_order_idx, order_key]
            
            # Handle NaN/None comparison
            if pd.isna(current_value) and pd.isna(order_value):
                pass  # Both are NaN/None, no change
            elif str_value_check(current_value, order_value, order_key):
                pass  # Values are equal
            else:
                # print("TESTING: updating queen order key:", order_key, "from:", current_value, "to:", order_value)
                QUEEN['queen_orders'].at[queen_order_idx, order_key] = order_value
                save_order = True
        else:
            QUEEN['queen_orders'].at[queen_order_idx, order_key] = order_value
            save_order = True
   
    return QUEEN['queen_orders'].loc[queen_order_idx].to_dict(), save_order

def update_queen_order_cost_basis(QUEEN, queen_order_idx, order_status):
    if order_status['filled_qty'] is not None:
        QUEEN['queen_orders'].at[queen_order_idx, 'filled_qty'] = float(order_status['filled_qty'])
    if order_status['filled_avg_price'] is not None:
        QUEEN['queen_orders'].at[queen_order_idx, 'filled_avg_price'] = float(order_status['filled_avg_price'])
        QUEEN['queen_orders'].at[queen_order_idx, 'cost_basis'] = float(order_status['filled_qty']) * float(order_status['filled_avg_price'])
    
    return QUEEN['queen_orders'].loc[queen_order_idx].to_dict()


def check_origin_order_status(QUEEN, origin_order, origin_idx, closing_filled):
    if float(origin_order["filled_qty"]) == closing_filled: 
        print("# FINAL CYCLE of QUEEN ORDER: running order has been fully sold out and now we can archive", origin_idx)
        QUEEN['queen_orders'].at[origin_idx, 'queen_order_state'] = 'final'
        return True
    else:
        return False


def update_runCLOSE__queen_order_honey(QUEEN, queen_order, origin_order, queen_order_idx):
    sold_price = float(queen_order['filled_avg_price'])
    origin_price = float(origin_order['filled_avg_price'])
    honey = (sold_price - origin_price) / origin_price
    cost_basis = origin_price * float(queen_order['filled_qty'])
    
    profit_loss_value = honey * cost_basis
    
    QUEEN['queen_orders'].at[queen_order_idx, 'honey'] = honey
    QUEEN['queen_orders'].at[queen_order_idx, 'money'] = profit_loss_value
    QUEEN['queen_orders'].at[queen_order_idx, 'profit_loss'] = profit_loss_value
    
    return {'profit_loss_value': profit_loss_value}


def update_origin_orders_profits(QUEEN, queen_order, origin_order, origin_order_idx): # updated origin Trade orders profits
    # origin order
    origin_order_cost_basis__qorder = origin_order.get('cost_basis')

    # closing_orders_cost_basis
    origin_closing_orders_df = return_closing_orders_df(QUEEN=QUEEN, exit_order_link=queen_order['exit_order_link'])
    
    if len(origin_closing_orders_df) > 0:        

        # Origin qty, price, costbasis
        origin_closing_orders_df['filled_qty'] = origin_closing_orders_df['filled_qty'].apply(lambda x: convert_to_float(x))
        origin_closing_orders_df['filled_avg_price'] = origin_closing_orders_df['filled_avg_price'].apply(lambda x: convert_to_float(x))
        origin_closing_orders_df['cost_basis'] = origin_closing_orders_df['filled_qty'] * origin_closing_orders_df['filled_avg_price']

        closing_orders_cost_basis = sum(origin_closing_orders_df['cost_basis'])

        profit_loss = closing_orders_cost_basis - origin_order_cost_basis__qorder
        closing_filled = sum(origin_closing_orders_df['filled_qty'])

        QUEEN['queen_orders'].at[origin_order_idx, 'profit_loss'] = profit_loss
        QUEEN['queen_orders'].at[origin_order_idx, 'closing_orders_cost_basis'] = closing_orders_cost_basis

        return {'closing_filled': closing_filled, 'profit_loss': profit_loss}
    else:
        return {'closing_filled': 0, 'profit_loss': 0, 'symbol': queen_order.get('symbol')}


def update_queen_order_profits(QUEEN, ticker, queen_order, queen_order_idx, priceinfo):
    try:
        current_price = float(priceinfo['current_price'])
        current_ask = float(priceinfo['current_ask'])
        current_bid = float(priceinfo['current_bid'])
        
        # priceinfo = {'price': current_price, 'bid': current_bid, 'ask': current_ask}
        order_price = float(queen_order['filled_avg_price'])
        if isinstance(order_price, float) and isinstance(current_price, float):
            current_profit_loss = (current_price - order_price) / order_price
            QUEEN['queen_orders'].at[queen_order_idx, 'honey'] = current_profit_loss
            QUEEN['queen_orders'].at[queen_order_idx, 'money'] = (current_price * float(queen_order['qty_available'])) - ( float(queen_order['filled_avg_price']) * float(queen_order['qty_available']) )
            QUEEN['queen_orders'].at[queen_order_idx, 'current_ask'] = current_ask
            QUEEN['queen_orders'].at[queen_order_idx, 'current_bid'] = current_bid
            if QUEEN['queen_orders'].at[queen_order_idx, 'honey'] > 0:
                if type(QUEEN['queen_orders'].at[queen_order_idx, 'honey_time_in_profit']) == dict:
                    QUEEN['queen_orders'].at[queen_order_idx, 'honey_time_in_profit'] = 1
                elif QUEEN['queen_orders'].at[queen_order_idx, 'honey_time_in_profit'] > 0:
                    current_iter_num = QUEEN['queen_orders'].at[queen_order_idx, 'honey_time_in_profit']
                    QUEEN['queen_orders'].at[queen_order_idx, 'honey_time_in_profit'] = 1 + current_iter_num
                else:
                    QUEEN['queen_orders'].at[queen_order_idx, 'honey_time_in_profit'] = 1
        else:
            print("ERROR calculating current profit loss, setting to 0", ticker, queen_order_idx, order_price, current_price)
            current_profit_loss = 0
            QUEEN['queen_orders'].at[queen_order_idx, 'honey'] = 0
            QUEEN['queen_orders'].at[queen_order_idx, 'money'] = 0
            QUEEN['queen_orders'].at[queen_order_idx, 'current_ask'] = current_ask
            QUEEN['queen_orders'].at[queen_order_idx, 'current_bid'] = current_bid
        
        return {'current_profit_loss': current_profit_loss}
    except Exception as e:
        print(ticker, " pl error", e, print_line_of_error())


def god_save_the_queen(QUEEN, QUEENsHeart=False, charlie_bee=False, save_q=False, save_acct=False, save_rr=False, save_qo=False, active_queen_order_states=active_queen_order_states, console=False, upsert_to_main_server=upsert_to_main_server, API_URL=API_URL):
    
    try:
        # print("upsert_to_main_server", upsert_to_main_server)
        # Save Heart to avoid saving Queen to improve speed
        # if charlie_bee:
        #     QUEENsHeart.update({"charlie_bee": charlie_bee})
        if QUEENsHeart:
            QUEENsHeart['heartbeat'] = QUEEN['heartbeat']
            QUEENsHeart.update({"heartbeat_time": datetime.now(est)})
            if pg_migration:
                PollenDatabase.upsert_data(QUEENsHeart.get('table_name'), QUEENsHeart.get('key'), QUEENsHeart, main_server=upsert_to_main_server, console=console)
            else:
                PickleData(QUEEN['dbs'].get('PB_QUEENsHeart_PICKLE'), QUEENsHeart, console=console)
        if save_q:
            # del QUEEN['queen_orders']
            if pg_migration:
                queen_to_save = copy.deepcopy(QUEEN)
                if QUEEN.get('orders_v2'):
                    queen_to_save['queen_orders'] = pd.DataFrame()
                PollenDatabase.upsert_data(QUEEN.get('table_name'), QUEEN.get('key'), queen_to_save, main_server=upsert_to_main_server, console=console)
                del queen_to_save
            else:
                PickleData(QUEEN['dbs'].get('PB_QUEEN_Pickle'), QUEEN, console=console)
        if save_qo:
            df = QUEEN.get('queen_orders')
            df = df[df['queen_order_state'].isin(active_queen_order_states)]
            ORDERS = {'queen_orders': df}
            if pg_migration:
                if not QUEEN.get('orders_v2'):
                    key = f'{QUEEN.get("key").split("-")[0]}-ORDERS'
                    PollenDatabase.upsert_data(QUEEN.get('table_name'), key=key, value=ORDERS, main_server=upsert_to_main_server, console=console)
            else:
                PickleData(QUEEN['dbs'].get('PB_Orders_Pickle'), {'queen_orders': df}, console=console)
        if save_acct:
            if pg_migration:
                key = f'{QUEEN.get("key").split("-")[0]}-ACCOUNT_INFO'
                ACCOUNT_INFO = QUEEN.get('account_info')
                PollenDatabase.upsert_data(QUEEN.get('table_name'), key=key, value=ACCOUNT_INFO, main_server=upsert_to_main_server, console=console)
            else:
                PickleData(QUEEN['dbs'].get('PB_account_info_PICKLE'), {'account_info': QUEEN.get('account_info')}, console=console)
        if save_rr:
            if pg_migration:
                key = f'{QUEEN.get("key").split("-")[0]}-REVREC'
                revrec = QUEEN.get('revrec')
                PollenDatabase.upsert_data(QUEEN.get('table_name'), key=key, value=revrec, main_server=upsert_to_main_server, console=console)
            else:
                PickleData(QUEEN['dbs'].get('PB_RevRec_PICKLE'), {'revrec': QUEEN.get('revrec')}, console=console)
        
        return True
    except Exception as e:
        print_line_of_error(e)
        sys.exit()


def save_queen_order(QUEEN, prod, client_order_id, upsert_to_main_server):
    try:
        # logging.info(f"saving queen order: {client_order_id} server={upsert_to_main_server}")
        table_name = 'queen_orders' if prod else 'queen_orders_sandbox'
        key = f"{QUEEN['db_root']}___{client_order_id}"
        PollenDatabase.upsert_data(table_name=table_name, key=key, value=QUEEN['queen_orders'].loc[client_order_id].to_dict(), console=True, main_server=upsert_to_main_server)
        return True  
    except Exception as e:
        logging.error(f"Error saving queen order: {e}")
        return False

def print_queen_cycle_times(charlie_bee):
    print("Queen Cycle Times:")
    total_time = 0
    for k, v in charlie_bee['queen_cycle_times'].items():
        print(f" - {k}: {v:.2f} seconds")
        total_time += v
    print(f"Total Cycle Time: {total_time:.2f} seconds")
    # print("OM:", charlie_bee['queen_cyle_times']['order management']) # 80%
    # print("CC:", charlie_bee['queen_cyle_times']['command conscience']) # 20%
    # print(f"Charlie: Cycle Times", {k: v for k, v in charlie_bee['queen_cyle_times'].items() if k.startswith('om_')})

    # charlie_bee['queen_cyle_times']['beat_times'].append({'datetime': datetime.now(est).strftime("%Y-%m-%d %H:%M:%S"), 'beat': beat})
    # charlie_bee['queen_cyle_times']['QUEEN_avg_cycle'].append(beat)
    # charlie_bee['queen_cyle_times']['QUEEN_avg_cycletime'] = sum(charlie_bee['queen_cyle_times']['QUEEN_avg_cycle'])/len(charlie_bee['queen_cyle_times']['QUEEN_avg_cycle'])


def normalize_timestamp(timestamp_str):
    """Normalize timestamp to microsecond precision for comparison"""
    if isinstance(timestamp_str, str) and 'T' in timestamp_str and timestamp_str.endswith('Z'):
        # Find the decimal point in the timestamp
        if '.' in timestamp_str:
            parts = timestamp_str.split('.')
            if len(parts) == 2:
                # Truncate to 6 decimal places (microseconds)
                fractional = parts[1][:-1]  # Remove the 'Z'
                fractional = fractional[:3]  # Keep only first 3 digits
                return f"{parts[0]}.{fractional}Z"
    return timestamp_str

def queenbee_get_priceinfo(QUEEN, active_queen_order_states, info="assumes revrec"):
    symbols = []
    if len(QUEEN['queen_orders']) > 0:
        active_order_symbols =  QUEEN['queen_orders'][QUEEN['queen_orders']['queen_order_state'].isin(active_queen_order_states)]['symbol'].unique().tolist()
        symbols.extend(active_order_symbols)
    
    story_symbols = QUEEN['revrec']['storygauge'].index.tolist()
    if story_symbols:
        symbols.extend(story_symbols)

    read_symbols = list(set(symbols))
    price_info_symbols = PollenDatabase.read_priceinfo_table(tickers=read_symbols)
    price_info_symbols_df = pd.DataFrame(price_info_symbols).set_index('ticker', drop=False)

    return price_info_symbols_df


def queenbee(client_user, prod, queens_chess_piece='queen', server=server, loglevel='warning', 
             server_storybee=False # ONLY USED SINCE DB QUEENS ARE LOCAL NOW... Jan 2026
             ):
    table_name = 'client_user_store' if prod else 'client_user_store_sandbox'
    if client_user in ['stapinskistefan@gmail.com'] and not prod: #'stefanstapinski@gmail.com', 
        print("TESTING LOCAL SANDBOX SAVE DATA TO SERVER")
        upsert_to_main_server = True
        server = True
        API_URL = os.getenv("main_fastAPI_url")
    else:
        upsert_to_main_server = False
        API_URL = os.getenv("fastAPI_url")

    def refresh_price_info_from_storybee(QUEEN, STORY_bee, symbols):
        """
        Refresh price_info_symbols with latest data from STORY_bee
        Falls back to API calls for missing tickers
        """
        try:
            price_data_list = []
            symbols_need_api_call = []
            
            for symbol in symbols:
                if symbol not in QUEEN['price_info_symbols']:
                    if symbol in STORY_bee.index:
                        story_data = STORY_bee.loc[symbol]
                        price_data = {
                            'ticker': symbol,
                            'current_price': story_data.get('current_price'),
                            'current_bid': story_data.get('current_bid'),
                            'current_ask': story_data.get('current_ask'),
                            'bid_ask_var': story_data.get('bid_ask_var')
                        }
                        price_data_list.append(price_data)
                    else:
                        symbols_need_api_call.append(symbol)
            
            # Handle symbols not in STORY_bee with API calls
            if symbols_need_api_call:
                print(f"Symbols missing from STORY_bee, calling API: {symbols_need_api_call}")
                api_price_data = async_api_alpaca__snapshots_priceinfo(
                    symbols_need_api_call, STORY_bee, api, QUEEN
                )
                price_data_list.extend(api_price_data)
            
            # Update QUEEN['price_info_symbols']
            if price_data_list:
                df_priceinfo_symbols = pd.DataFrame(price_data_list)
                df_priceinfo_symbols = df_priceinfo_symbols.set_index('ticker', drop=False)
                update_queens_priceinfo_symbols(QUEEN, df_priceinfo_symbols)
                
            return True
            
        except Exception as e:
            print(f"Error refreshing price info from STORY_bee: {e}")
            return False

    def route_queen_order(QUEEN, queen_order, queen_order_idx, order_status, priceinfo, save_order=False):

        def alpaca_queen_order_state(QUEEN, order_status, queen_order, queen_order_idx, priceinfo, save_order):
            try:
                origin_order_idx = False
                """ Alpcaca Order States """
                cancel_expired = ['canceled', 'expired']
                pending = ['pending_cancel', 'pending_replace']
                failed = ['stopped', 'rejected', 'suspended']
                accetped = ['accepted', 'pending_new', 'accepted_for_bidding', 'new', 'calculated']
                filled = ['filled']
                partially_filled = ['partially_filled']
                alp_order_status = order_status['status']
            
                # handle updates. cancels updates
                if alp_order_status in cancel_expired:
                    QUEEN['queen_orders'].at[queen_order_idx, 'queen_order_state'] = "cancel_expired"
                elif alp_order_status in pending:
                    QUEEN['queen_orders'].at[queen_order_idx, 'queen_order_state'] = "pending"
                elif alp_order_status in failed:
                    # Send Info Back to Not Trade Again?
                    QUEEN['queen_orders'].at[queen_order_idx, 'queen_order_state'] = "failed"
                elif alp_order_status in accetped:
                    if order_status['side'] == 'buy':
                        QUEEN['queen_orders'].at[queen_order_idx, 'queen_order_state'] = 'running_open'
                    else:
                        #WORKERBEE IF SHORTING THIS WON"T WORK NEED TO FIX. CHECK IF SHORITNG
                        QUEEN['queen_orders'].at[queen_order_idx, 'queen_order_state'] = 'running_close'

                # Handle Filled Orders #
                elif alp_order_status in filled:
                    # route by order type buy sell
                    if order_status['side'] == 'buy':
                        QUEEN['queen_orders'].at[queen_order_idx, 'queen_order_state'] = 'running'
                        update_origin_order_qty_available(QUEEN=QUEEN, run_order_idx=queen_order_idx, RUNNING_CLOSE_Orders=RUNNING_CLOSE_Orders, RUNNING_Orders=RUNNING_Orders)                        
                        run_order, save_order = update_latest_queen_order_status(QUEEN=QUEEN, queen_order_idx=queen_order_idx, order_status=order_status, save_order=save_order)
                        update_origin_order_cost_basis_current(QUEEN, queen_order_idx, priceinfo, instance=1)
                        update_queen_order_profits(QUEEN=QUEEN, ticker=queen_order.get('ticker'), queen_order=queen_order, queen_order_idx=queen_order_idx, priceinfo=priceinfo)
                        if QUEEN['queen_orders'].at[queen_order_idx, 'status_q'] != 'filled':
                            update_queen_order_cost_basis(QUEEN, queen_order_idx, order_status)
                            save_order = True
                        QUEEN['queen_orders'].at[queen_order_idx, 'status_q'] = 'filled'
                    
                    elif order_status['side'] == 'sell':
                        # closing order, update origin order profits attempt to close out order
                        origin_order = return_origin_order(df_queenorders=QUEEN['queen_orders'], exit_order_link=queen_order['exit_order_link'])
                        origin_order_idx = origin_order.get('origin_idx')
                        if origin_order_idx:
                            origin_order = origin_order.get('origin_order')
                            # confirm profits
                            profit_loss_value = update_runCLOSE__queen_order_honey(QUEEN=QUEEN, queen_order=queen_order, origin_order=origin_order, queen_order_idx=queen_order_idx)['profit_loss_value']
                            QUEEN['queen_orders'].at[queen_order_idx, 'queen_order_state'] = 'completed'
                            msg=(f'{queen_order_idx} {origin_order.get("symbol")} closing filled: {profit_loss_value}')
                            logging.info(msg)

                            #### CHECK to see if Origin ORDER has Completed LifeCycle ###
                            res = update_origin_orders_profits(QUEEN=QUEEN, queen_order=queen_order, origin_order=origin_order, origin_order_idx=origin_order_idx)
                            closing_filled = res['closing_filled']
                            profit_loss = res['profit_loss']
                            update_queen_order_profits(QUEEN=QUEEN, ticker=queen_order.get('ticker'), queen_order=queen_order, queen_order_idx=queen_order_idx, priceinfo=priceinfo)
                            
                            update_origin_order_qty_available(QUEEN=QUEEN, run_order_idx=origin_order_idx, RUNNING_CLOSE_Orders=RUNNING_CLOSE_Orders, RUNNING_Orders=RUNNING_Orders)
                            update_origin_order_cost_basis_current(QUEEN=QUEEN, queen_order_idx=origin_order_idx, priceinfo=priceinfo, instance=2)
                            check_origin_order_status(QUEEN=QUEEN, origin_order=origin_order, origin_idx=origin_order_idx, closing_filled=closing_filled)
                        
                elif alp_order_status in partially_filled:            
                    if order_status['side'] == 'buy':
                        QUEEN['queen_orders'].at[queen_order_idx, 'queen_order_state'] = "running_open"

                        update_origin_order_qty_available(QUEEN=QUEEN, run_order_idx=queen_order_idx, RUNNING_CLOSE_Orders=RUNNING_CLOSE_Orders, RUNNING_Orders=RUNNING_Orders)
                        run_order, save_order = update_latest_queen_order_status(QUEEN=QUEEN, queen_order_idx=queen_order_idx, order_status=order_status, save_order=save_order)
                        update_origin_order_cost_basis_current(QUEEN, queen_order_idx, priceinfo, instance=2)
                        update_queen_order_profits(QUEEN=QUEEN, ticker=queen_order.get('ticker'), queen_order=queen_order, queen_order_idx=queen_order_idx, priceinfo=priceinfo)
                        update_queen_order_cost_basis(QUEEN, queen_order_idx, order_status)
                    
                    elif order_status['side'] == 'sell':
                        # closing order, update origin order profits attempt to close out order
                        origin_order = return_origin_order(df_queenorders=QUEEN['queen_orders'], exit_order_link=queen_order['exit_order_link'])
                        origin_order_idx = origin_order.get('origin_idx')
                        origin_order = origin_order.get('origin_order')
                        
                        if origin_order_idx:
                            # update profits keep in running 
                            update_runCLOSE__queen_order_honey(QUEEN=QUEEN, queen_order=queen_order, origin_order=origin_order, queen_order_idx=queen_order_idx)
                            QUEEN['queen_orders'].at[queen_order_idx, 'queen_order_state'] = 'running_close'

                            update_origin_orders_profits(QUEEN=QUEEN, queen_order=queen_order, origin_order=origin_order, origin_order_idx=origin_order_idx)
                            update_queen_order_profits(QUEEN=QUEEN, ticker=queen_order.get('ticker'), queen_order=queen_order, queen_order_idx=queen_order_idx, priceinfo=priceinfo)
                            update_origin_order_qty_available(QUEEN=QUEEN, run_order_idx=origin_order_idx, RUNNING_CLOSE_Orders=RUNNING_CLOSE_Orders, RUNNING_Orders=RUNNING_Orders)
                            update_origin_order_cost_basis_current(QUEEN=QUEEN, queen_order_idx=origin_order_idx, priceinfo=priceinfo, instance=3)

                    else:
                        print("Critical Error New Order Side")
                else:
                    print("critical errror new order type received")
                    logging.error(f"WTF Route me {queen_order_idx}")
            
                
                return queen_order_idx, origin_order_idx, save_order

            except Exception as e:
                print('queen router failed', e, print_line_of_error())
        

        queen_order_idx, origin_order_idx, save_order = alpaca_queen_order_state(QUEEN=QUEEN, 
                                                                                 order_status=order_status, 
                                                                                 queen_order=queen_order, 
                                                                                 queen_order_idx=queen_order_idx, 
                                                                                 priceinfo=priceinfo,
                                                                                 save_order=save_order
                                                                                 )
        if save_order:
            print("ROUTE ORDER SAVE QUEEN ORDER SAVE REASON?", queen_order_idx, origin_order_idx)
            save_queen_order(QUEEN, prod=QUEEN['prod'], client_order_id=queen_order_idx, upsert_to_main_server=upsert_to_main_server)
            if origin_order_idx:
                print("ROUTE ORDER SAVE ORIGIN QUEEN ORDER", queen_order_idx, "ORIGIN ORDER: ", origin_order_idx)
                save_queen_order(QUEEN, prod=QUEEN['prod'], client_order_id=origin_order_idx, upsert_to_main_server=upsert_to_main_server)


        return QUEEN['queen_orders'].loc[queen_order_idx].to_dict(), save_order

    def append_queen_order(QUEEN, new_queen_order_df, upsert_to_main_server=upsert_to_main_server):
        client_order_id = new_queen_order_df.iloc[0]['client_order_id']
        if client_order_id not in QUEEN['queen_orders']['client_order_id'].to_list():
            QUEEN['queen_orders'] = pd.concat([QUEEN['queen_orders'], new_queen_order_df], axis=0) # , ignore_index=True
            QUEEN['queen_orders']['client_order_id'] = QUEEN['queen_orders'].index
            save_queen_order(QUEEN, prod=QUEEN['prod'], client_order_id=client_order_id, upsert_to_main_server=upsert_to_main_server)
        else:
            print("QUEEN ORDER ALREADY EXISTS", client_order_id)
            return False
        return True

    def adhoc_handle_queen_order_broker_failure(order_status, QUEEN, c_order_id, upsert_to_main_server=upsert_to_main_server):
        if not order_status:
            print("BROKER ORDER NOT UPDATED", c_order_id, "BROKER ORDERS", "Archive ORDER")
            QUEEN['queen_orders'].at[c_order_id, 'queen_order_state'] = 'archived'
            QUEEN['queen_orders'].at[c_order_id, 'status_q'] = 'ERROR NO BROKER'
            save_queen_order(QUEEN, prod=QUEEN['prod'], client_order_id=c_order_id, upsert_to_main_server=upsert_to_main_server)

    def update_origin_order_qty_available(QUEEN, run_order_idx, RUNNING_CLOSE_Orders, RUNNING_Orders, save=False):
        try:
            # Retrieve Queen Order details
            queen_order = QUEEN['queen_orders'].loc[run_order_idx].to_dict()
            symbol = queen_order['symbol']

            if queen_order['queen_order_state'] in RUNNING_Orders:
                closing_dfs = return_closing_orders_df(QUEEN, queen_order['client_order_id'])

                if len(closing_dfs) > 0:  # WORKERBEE num convert NOT necessary REMOVE
                    closing_dfs['qty'] = closing_dfs['qty'].apply(convert_to_float)
                    closing_dfs['filled_qty'] = closing_dfs['filled_qty'].apply(convert_to_float)
                    closing_dfs['filled_avg_price'] = closing_dfs['filled_avg_price'].apply(convert_to_float)

                    # Validate qty
                    closing_filled = sum(closing_dfs['filled_qty'])

                    if closing_filled < 0:
                        wash_sale_rule.append({
                            'symbol': symbol,
                            'loss': closing_filled,
                            'wash_sale_next_buy_date': (datetime.now(est) + timedelta(days=31)).strftime("%m/%d/%Y")
                        })

                    order_qty = float(queen_order['filled_qty'])

                    # Handle case where filled qty exceeds original order
                    if closing_filled > order_qty:
                        excess_qty = closing_filled - order_qty
                        msg = (f"⚠️ Excess filled! Order {queen_order['client_order_id']} filled {closing_filled} "
                            f"but original qty was {order_qty}. Excess: {excess_qty}, Symbol: {symbol}")
                        print(msg)
                        logging.warning(msg)
                    
                    # Ensure no negative values in available quantities
                    qty_available = max(0, order_qty - closing_filled)
                    qty_available_pending = max(0, order_qty - closing_filled)

                    # Update QUEEN order
                    QUEEN['queen_orders'].at[run_order_idx, 'qty_available'] = qty_available
                    QUEEN['queen_orders'].at[run_order_idx, 'qty_available_pending'] = qty_available_pending
                
                else:
                    QUEEN['queen_orders'].at[run_order_idx, 'qty_available'] = float(queen_order['filled_qty'])

            elif queen_order['queen_order_state'] in RUNNING_CLOSE_Orders:
                qty_available = max(0, float(queen_order['qty']) - float(queen_order['filled_qty']))
                QUEEN['queen_orders'].at[run_order_idx, 'qty_available'] = qty_available

            elif queen_order['queen_order_state'] in CLOSED_queenorders:
                msg = f"{run_order_idx} Order Closed. Consider handling closure here?"
                print(msg)
                logging.error(msg)
            elif queen_order['queen_order_state'] in ['submitted']:
                QUEEN['queen_orders'].at[run_order_idx, 'qty_available'] = float(queen_order['filled_qty'])

            else:
                print(f"⚠️ Unknown state for order {queen_order['client_order_id']}: {queen_order['queen_order_state']}")

            if save:
                save_queen_order(QUEEN, prod=QUEEN['prod'], client_order_id=queen_order['client_order_id'], upsert_to_main_server=upsert_to_main_server)

            return True

        except Exception as e:
            print_line_of_error(e)
            return False

    def init_BROKER(api, BROKER):
        if len(BROKER['broker_orders']) == 0:
            print("INIT Broker ORDERS")
            BROKER = init_broker_orders(api, BROKER)
            if pg_migration:
                print(f"--- INIT UPSERT BROKER ORDERS TO Server= {server} ")
                logging.warning(f"--- INIT UPSERT BROKER ORDERS TO Server= {server} ")
                PollenDatabase.upsert_data(BROKER.get('table_name'), BROKER.get('key'), BROKER, main_server=server)
            else:
                PickleData(BROKER.get('source'), BROKER, console=False)
        return BROKER

    def reconcile_broker_orders_with_queen_orders(BROKER, api, QUEEN, active_queen_order_states, b_order_init=False):
        
        # if len(BROKER['broker_orders']) == 0:
        #     print("INIT Broker ORDERS")
        #     b_order_init = True
        #     BROKER = init_broker_orders(api, BROKER)

        BROKER = init_BROKER(api, BROKER)

        # check for any missing orders
        save_b = False
        df = QUEEN.get('queen_orders')
        df['status_q'] = df['status_q'].fillna('')
        df_active = df[df['queen_order_state'].isin(active_queen_order_states)].copy()
        if len(df_active) > 0 and len(BROKER['broker_orders']) > 0:
            # ("Update QUEEN with Broker Orders")
            df_active['client_order_id'] = df_active['client_order_id'].fillna('init')
            qo_active_index = df_active['client_order_id'].to_list()
            broker_corder_ids = BROKER['broker_orders']['client_order_id'].tolist()
            for client_order_id in qo_active_index:
                if client_order_id not in broker_corder_ids and client_order_id != 'init':
                    print(f"ALERT NEW CLIENT ORDER ID {client_order_id}")
                    time.sleep(1)
                    order_status = check_order_status(broker='alpaca', api=api, client_order_id=client_order_id)
                    if not order_status:
                        adhoc_handle_queen_order_broker_failure(order_status, QUEEN, client_order_id, upsert_to_main_server=upsert_to_main_server)
                        continue
                    if order_status:
                        save_b = True
                        update_broker_order_status(BROKER, order_status)
                    if b_order_init:
                        if df_active.at[client_order_id, 'status'] == 'filled':
                            QUEEN['queen_orders'].at[client_order_id, 'status_q'] = 'filled'
                        else:
                            QUEEN['queen_orders'].at[client_order_id, 'status_q'] = 'pending'

        return save_b, BROKER, QUEEN

    def update_queen_order(QUEEN, update_package, upsert_to_main_server=upsert_to_main_server):
        # update_package client_order id and field updates {client_order_id: {'queen_order_status': 'running'}}
        try:
            for c_order_id, package in update_package['queen_order_updates'].items():
                save = False
                for field_, new_value in package.items():
                    try:
                        QUEEN['queen_orders'].at[c_order_id, field_] = new_value
                        save = True
                    except Exception as e:
                        print(e, 'failed to update QueenOrder')
                        logging.critical({'msg': 'failed to update queen orders', 'error': e, 'other': (field_, new_value)})
                if save:
                    save_queen_order(QUEEN, prod=QUEEN['prod'], client_order_id=c_order_id, upsert_to_main_server=upsert_to_main_server)

        except Exception as e:
            print_line_of_error()
            logging.critical({'error': e, 'msg': 'update queen order', 'update_package': update_package})
        return True

    def update_queen_order_order_rules(QUEEN, update_package, upsert_to_main_server=upsert_to_main_server):
        try:
            latest_kors = kings_order_rules()
            for c_order_id, package in update_package['update_order_rules'].items():
                save = False
                for field_, new_value in package.items():
                    try:
                        if field_ in latest_kors:
                            QUEEN['queen_orders'].at[c_order_id, 'order_rules'].update({field_: new_value})
                            save = True
                        elif field_ in QUEEN['queen_orders'].loc[c_order_id]:
                            QUEEN['queen_orders'].at[c_order_id, field_] = new_value
                            save = True
                        else:
                            print(f"Field {field_} not found in order_rules or queen_orders for {c_order_id}")
                            logging.warning(f"Field {field_} not found in order_rules or queen_orders for {c_order_id}")
                        # logging.info((f'{field_} updated to {new_value}'))
                    except Exception as e:
                        print(e, 'failed to update QueenOrder')
                        logging.critical({'msg': 'failed to update queen orders', 'error': e, 'other': (field_, new_value)})
                        
                if save:
                    save_queen_order(QUEEN, prod=QUEEN['prod'], client_order_id=c_order_id, upsert_to_main_server=upsert_to_main_server)
            # if save:
            #     god_save_the_queen(QUEEN, save_q=True, save_qo=True, upsert_to_main_server=upsert_to_main_server)
        except Exception as e:
            print_line_of_error()
            logging.critical({'error': e, 'msg': 'update queen order', 'update_package': update_package})
        return True

    def process_sell_app_request(QUEEN, QUEEN_KING, run_order, request_name='sell_orders', app_requests__bucket='app_requests__bucket', check_only=False):
        client_order_id = run_order.get('client_order_id')
        order_state = run_order.get('queen_order_state')  # currenting func in waterfall so it will always be running order
        app_order_base = [i for i in QUEEN_KING[request_name]]
        
        if len(app_order_base) > 0:
            for app_request in app_order_base:
                # if app_request['app_requests_id'] == "sell_orders_run__9409982_app-request_id_2025-06-17 21-40-03 PM US/Eastern118077":
                #     print("App Request ID already processed")
                if app_request['app_requests_id'] in QUEEN[app_requests__bucket]:
                    # if app_request['app_requests_id'] == "sell_orders_run__9409982_app-request_id_2025-06-17 21-40-03 PM US/Eastern118077":
                    #     print("App Request ID already processed @@@@@2")
                    continue
                elif app_request['client_order_id'] == client_order_id:
                    if order_state in CLOSED_queenorders:
                        print(f"{client_order_id} ORDER ALREADY CLOSED")
                        QUEEN['app_requests__bucket'].append(app_request['app_requests_id'])
                    else:
                        if check_only:
                            print("App Req TO SELL ORDER ORDER FOUND")
                            return {'app_flag': True}
                        
                        print("App Req Sell Order")
                        sell_qty = app_request.get('sell_qty')
                        o_type = app_request.get('type')
                        side = app_request.get('side')
                        limit = app_request.get('limit')

                        QUEEN['app_requests__bucket'].append(app_request['app_requests_id'])
                        # god_save_the_queen(QUEEN, save_q=True, save_qo=True, upsert_to_main_server=upsert_to_main_server)
                        return {'app_flag': True, 'sell_order': True, 'sell_qty': sell_qty, 'type': o_type, 'side': side, 'limit': limit}
                else:
                    pass

        return {'app_flag': False}

    def process_app_requests(QUEEN, QUEEN_KING, request_name):
        app_flag = False
        app_requests__bucket = 'app_requests__bucket'
        try:
            if request_name == "buy_orders": # ok
                app_order_base = [i for i in QUEEN_KING[request_name]]
                if app_order_base:
                    for app_request in app_order_base:
                        if app_request['app_requests_id'] in QUEEN[app_requests__bucket]:
                            # print("buy trigger request Id already received")
                            continue
                        else:
                            
                            QUEEN[app_requests__bucket].append(app_request['app_requests_id'])
                            if isinstance(app_request.get('new_queen_order'), dict):
                                msg = ("APP BUY order gather", app_request['new_queen_order']['ticker_time_frame'])
                                new_queen_order_df = pd.DataFrame([app_request['new_queen_order']]).set_index("client_order_id", drop=False)
                                append_queen_order(QUEEN, new_queen_order_df)
                            else:
                                msg = ("new queen order not dict error")
                            print(msg)
                            logging.info(msg)

                            return {'app_flag': True}
                else:
                    return {'app_flag': False}
            
            elif request_name == "wave_triggers": # ok
                app_order_base = [i for i in QUEEN_KING[request_name]]
                if app_order_base:
                    for app_request in app_order_base:
                        if app_request['app_requests_id'] in QUEEN[app_requests__bucket]:
                            # print("wave trigger request Id already received") # waiting for user to refresh client side
                            continue
                            # return {'app_flag': False}
                        else:
                            msg = ("app wave trigger gather", app_request['wave_trigger'], " : ", app_request['ticker_time_frame'])
                            QUEEN[app_requests__bucket].append(app_request['app_requests_id'])
                            print(msg)
                            logging.info(msg)
                                
                            return {'app_flag': True, 'app_request': app_request, 'ticker_time_frame': app_request['ticker_time_frame']}
                else:
                    return {'app_flag': False}

            elif request_name == "queen_sleep": # redo Don't save App
                app_order_base = [i for i in QUEEN_KING[request_name]]
                if len(app_order_base) == 0:
                    return {'app_flag': False}
                queensleep = False
                for app_request in app_order_base: # if len(app_order_base) > 1:
                    if app_request['app_requests_id'] in QUEEN['app_requests__bucket']:
                        # return {'app_flag': False}
                        continue
                    else:
                        queensleep = True
                        QUEEN['app_requests__bucket'].append(app_request['app_requests_id'])                
                if queensleep:
                    print("WAIT for QUEEN to STOP")
                    god_save_the_queen(QUEEN, save_rr=True, save_q=True, upsert_to_main_server=upsert_to_main_server)
                    print("QUEEN STOPPED")
                    sys.exit()

            elif request_name == "update_queen_order": # ok
                app_order_base = [i for i in QUEEN_KING[request_name]]
                if app_order_base:
                    for app_request in app_order_base:
                        if app_request['app_requests_id'] in QUEEN['app_requests__bucket']:
                            continue
                        else:
                            QUEEN['app_requests__bucket'].append(app_request['app_requests_id'])
                            print("queen update order trigger gather", app_request['queen_order_updates'])
                            update_queen_order(QUEEN=QUEEN, update_package=app_request)
                            app_flag = True
                            
                    return {'app_flag': app_flag}
                else:
                    return {'app_flag': False}

            elif request_name == 'update_order_rules':
                app_order_base = [i for i in QUEEN_KING[request_name]]
                if app_order_base:
                    for app_request in app_order_base:
                        if app_request['app_requests_id'] in QUEEN['app_requests__bucket']:
                            continue
                            # return {'app_flag': False}
                        else:
                            QUEEN['app_requests__bucket'].append(app_request['app_requests_id'])
                            print("queen update order trigger gather", app_request['update_order_rules'])
                            update_queen_order_order_rules(QUEEN=QUEEN, update_package=app_request)
                            app_flag = True
                            
                    return {'app_flag': app_flag}
                else:
                    return {'app_flag': False}
            elif request_name == "subconscious": # ?
                app_order_base = [i for i in QUEEN_KING[request_name]]
                if app_order_base:
                    for app_request in app_order_base:
                        if app_request['app_requests_id'] in QUEEN['app_requests__bucket']:
                            # print("queen update order trigger request Id already received")
                            return {'app_flag': False}
                        else:
                            print("queen control gather", app_request['request_name'],)
                            QUEEN['app_requests__bucket'].append(app_request['app_requests_id'])
                            # update control
                            path_key = app_request['subconscious_thought_to_clear']
                            QUEEN[request_name][path_key] = app_request['subconscious_thought_new_value']
                            msg = (f'{path_key} Subconscious thought cleared:: {path_key}')
                            print(msg)
                            logging.info(msg)
                            if pg_migration:
                                PollenDatabase.upsert_data(QUEEN.get('table_name'), key=QUEEN.get('key'), value=QUEEN)
                            else:
                                PickleData(QUEEN['dbs'].get('PB_QUEEN_Pickle'), QUEEN)
                            return {'app_flag': True, 'app_request': app_request}
                else:
                    return {'app_flag': False}

            
            return {'app_flag': False}
        
        except Exception as e:
            print_line_of_error(e)

    def process_app_requests__order_updates(QUEEN, QUEEN_KING, upsert_to_main_server):
        try: # App Requests
            s_app = datetime.now(est)
            req = process_app_requests(QUEEN=QUEEN, QUEEN_KING=QUEEN_KING, request_name='update_queen_order')
            if req.get('app_flag'):
                print("APP: Queen Order Main PROCESSING ORDER")
                god_save_the_queen(QUEEN, save_q=True, upsert_to_main_server=upsert_to_main_server)
            req =  process_app_requests(QUEEN=QUEEN, QUEEN_KING=QUEEN_KING, request_name='update_order_rules')
            if req.get('app_flag'):
                print("APP: Queen Order Order Rules Updated SAVE")
                god_save_the_queen(QUEEN, save_q=True, upsert_to_main_server=upsert_to_main_server)
        except Exception as e:
            msg=('APP: Queen Order Main FAILED PROCESSING ORDER', print_line_of_error(e))
            logging.error(msg)

    def trig_In_Action_cc(active_orders, trig, ticker_time_frame):
        
        if len(active_orders) > 0:
            active_orders['order_exits'] = np.where(
                (active_orders['trigname'] == trig) &
                (active_orders['ticker_time_frame_origin'] == ticker_time_frame), 1, 0)
            trigbee_orders = active_orders[active_orders['order_exits'] == 1].copy()
            if len(trigbee_orders) > 0:
                return trigbee_orders
            else:
                return ''
        else:
            return ''

    def ticker_trig_In_Action_cc(active_orders, trig, ticker):
        
        if len(active_orders) > 0:
            active_orders['ticker_trig_active'] = np.where(
                (active_orders['trigname'] == trig) &
                (active_orders['symbol'] == ticker), 1, 0)
            trigbee_orders = active_orders[active_orders['ticker_trig_active'] == 1].copy()
            if len(trigbee_orders) > 0:
                return trigbee_orders
            else:
                return ''
        else:
            return ''

    def king_knights_requests(QUEEN, STORY_bee, revrec, tm_trig, trigbee, ticker, ticker_time_frame, trading_model, trig_action, app_trig, trigger_model={}, crypto=False, WT=WT, order_type='buy'):
        s_ = datetime.now(est)

        """Confirming King's Blessing"""


        ####### Allow Stars to borrow power if cash available ###### its_morphin_time
        
        def kings_blessing_checks(ticker_time_frame, acct_info, wave_amo, king_order_rules, trig_action_num, time_delta, macd_tier, trigbee, crypto):
            # print(acct_info)
            # ACCOUNT amo greater then available account
            if wave_amo > acct_info.get('buying_power'): # daytrading_buying_power
                print("day trade buying power exceeded")
                wave_amo = acct_info.get('buying_power') - wave_amo
                if wave_amo <= 0:
                    print(f"{ticker_time_frame} budget buying power is depleted for BUYING POWER")
                    return True
            # Ignore Tiering, this looks like dup WORKERBEE
            if "ignore_trigbee_in_macdstory_tier" in king_order_rules.keys():
                if macd_tier in king_order_rules.get("ignore_trigbee_in_macdstory_tier"):
                    print(f'{ticker_time_frame} Ignore Trigger macd_tier: , {macd_tier}')
                    return True #(f'{ticker_time_frame} Ignore Trigger macd_tier: , {macd_tier}')
            elif trig_action_num > 0: ## already happens in Water Fall
                if time_delta < timedelta(minutes=king_order_rules['doubledown_timeduration']):
                    msg = (f"{ticker_time_frame} TRIG In Action, DoubleDown Time Delta Not Met wave amo {wave_amo}")
                    print(msg)
                    # logging.info(msg)
                    return True
            # elif 'sell' in trigbee: # == 'sell_cross-0':
            #     if crypto:
            #         print(f'sell is in TRIG {ticker_time_frame} crypto not allowed')
            #         return True
            else:
                return False

        def calculate_margin_buy(trinity, waveguage_meter, order_type, smooth=2):
            if isinstance(trinity, float) and isinstance(waveguage_meter, float):
                if order_type == 'buy':
                    trinity = 1 - trinity
                    waveguage_meter = 1 - waveguage_meter
                else: # sell
                    trinity = trinity * -1
                    trinity = 1 - trinity

                    waveguage_meter = waveguage_meter * -1
                    waveguage_meter = 1 - waveguage_meter
                
                trinity = (waveguage_meter + trinity) / smooth
                return trinity
            else:
                return None
        

        # vars
        ticker, tframe, tperiod = ticker_time_frame.split("_")
        symbol = ticker
        star_time = f'{tframe}{"_"}{tperiod}'

        waveview = revrec.get('waveview')
        storygauge = revrec.get('storygauge')

        trinity = storygauge.loc[ticker].get(f'{TRINITY_}w_L')
        waveguage_meter = storygauge.loc[ticker].get(f'{TRINITY_}{WT[star_time]}')

        try:
            borrowed_funds = False
            kings_blessing = False
            alloc_deploy = waveview.at[ticker_time_frame, 'allocation_deploy']
            alloc_deploy_margin = waveview.at[ticker_time_frame, 'allocation_long_deploy'] - alloc_deploy
            wave_amo = alloc_deploy
            if trigger_model:
                wave_amo = float(trigger_model.get('wave_amo', wave_amo))

            if symbol not in QUEEN['price_info_symbols'].index:
                msg = f'KNIGHT: {symbol} NOT in QUEENs price_info_symbols'
                print(msg)
                return {'kings_blessing': False, 'msg': 'missing price info'}
            
            ticker_priceinfo = QUEEN['price_info_symbols'].loc[symbol].to_dict()

            star_total_budget_remaining = waveview.loc[ticker_time_frame].get("remaining_budget")
            star_total_borrow_remaining = waveview.loc[ticker_time_frame].get("remaining_budget_borrow")

            # trade scenarios / power ups / 
            trig_action_num = len(trig_action) # get trading model amount allowed?
            now_time = datetime.now(est)
            if trig_action_num != 0:
                trig_action.iloc[-1]['datetime']
                time_delta = now_time - trig_action.iloc[-1]['datetime']
            else:
                time_delta = now_time - datetime.now(est)

            acct_info = QUEEN['account_info']

            # Theme ???????/ WORKERBEE
            theme = QUEEN_KING['king_controls_queen']['theme'] # what is the theme?
            trading_model_theme = trading_model.get('theme')
            trading_model_star = trading_model['stars_kings_order_rules'].get(f'{tframe}_{tperiod}')

            """Stars Forever Be in Heaven"""
            macd_tier = waveview.loc[ticker_time_frame].get('end_tier_macd')

            s_ = datetime.now(est)
            current_macd_cross__wave = star_ticker_WaveAnalysis(STORY_bee=STORY_bee, ticker_time_frame=ticker_time_frame)['current_wave']
            current_wave = star_ticker_WaveAnalysis(STORY_bee=STORY_bee, ticker_time_frame=ticker_time_frame)['current_active_waves'][tm_trig]
            current_wave_blocktime = current_wave['wave_blocktime']

            # Trading Model Vars
            # Global switch to user power rangers at ticker or portfolio level 
            if trading_model_theme == 'story__AI':
                print('story ai update KORs with lastest from story view()')
            king_order_rules = trading_model['stars_kings_order_rules'][star_time]['trigbees'][tm_trig][current_wave_blocktime]
            maker_middle = ticker_priceinfo['maker_middle'] if str(trading_model_star.get('trade_using_limits')) == 'true' else False
            king_order_rules['sell_trigbee_date'] = update_sell_date(star_time)

            if trigger_model:
                app_trig['trig'] = True
                # Update KORS
                king_order_rules['ignore_allocation_budget'] = True
                king_order_rules['trigger_id'] = trigger_model['trigger_id']
                king_order_rules['take_profit'] = trigger_model['take_profit']
                king_order_rules['sell_out'] = trigger_model['sell_out']
                king_order_rules['sell_trigbee_date'] = trigger_model['sell_trigbee_date']


            power_up_amo = power_amo() # deprecated WORKERBEE
            if kings_blessing_checks(ticker_time_frame, acct_info, wave_amo, king_order_rules, trig_action_num, time_delta, macd_tier, trigbee, crypto):
                return {'kings_blessing': False}

            overrule_power = king_order_rules.get('overrule_power')
            overrule_power = 0 if king_order_rules.get('overrule_power') is None else overrule_power

            blessings = {'kings_blessing': kings_blessing, 'blessings': []}

            # if star_total_budget_remaining > 0: # STAR

            if not trigger_model:
                if wave_amo > star_total_budget_remaining:
                    borrowed_funds = True
                    if wave_amo < star_total_borrow_remaining:
                        msg = (f"KNIGHT {ticker_time_frame} Wave Amo > then star budget using borrowed funds {round(wave_amo)}")
                        # logging.warning(msg)
                        print(msg)
                    else:
                        msg = (f"KNIGHT {ticker_time_frame} Wave Amo > then star BORROW Budget using Remaining borrowed funds {round(wave_amo)}")
                        # logging.warning(msg)
                        print(msg)
                        wave_amo = star_total_borrow_remaining

            ticker_current_ask = ticker_priceinfo['current_ask']
            if not ticker_current_ask:
                pass
                ticker_current_ask = 89
            else:
                ticker_current_ask = float(ticker_current_ask)
            # if wave_amo > # ticker price
            if not crypto:
                if wave_amo < ticker_current_ask:
                    msg = (f'KNIGHT EXIT wave amo LESS then current ask {ticker_time_frame} current ask: {ticker_current_ask} wave amo: {round(wave_amo)}')
                    # logging.warning(msg)
                    # print(msg)
                    return {'kings_blessing': False, 'msg': msg}
            
            kings_blessing = True
            double_down_trade = False
            
            if trig_action_num > 0: ## move this to before KNIGHT
                if time_delta > timedelta(minutes=king_order_rules['doubledown_timeduration']) or app_trig.get('trig') == True:
                    # logging.info(f"Double Down Wave {ticker_time_frame} trigbee {trigbee}")
                    print(f"Double Down Wave {ticker_time_frame} trigbee {trigbee}")
                    kings_blessing = True
                    double_down_trade = True
                else:
                    print(ticker_time_frame, " Double Down delta HAULT")
                    kings_blessing = False
                    order_vars = None
            
            # gamble(monring,noon,afternoon) order based on trinity, if existing ttf no thank you?, prior(n) wave high,
            if not isinstance(wave_amo, float) or wave_amo <=0:
                msg=(f"KNIGHT: Deploy for {ticker_time_frame} LESS then 0, reduce by wave amo {wave_amo}")
                logging.error(msg)
                return {'kings_blessing': False}
            
            if wave_amo and kings_blessing:
                blessings.update({'kings_blessing': kings_blessing})
                order_vars = order_vars__queen_order_items(trading_model=trading_model_theme, 
                                                            king_order_rules=king_order_rules, 
                                                            order_side='buy', 
                                                            wave_amo=wave_amo, 
                                                            maker_middle=maker_middle, 
                                                            origin_wave=current_wave, 
                                                            power_up_rangers=power_up_amo, 
                                                            ticker_time_frame_origin=ticker_time_frame, 
                                                            double_down_trade=double_down_trade, 
                                                            wave_at_creation=current_macd_cross__wave,
                                                            symbol=symbol,
                                                            trigbee=trigbee,
                                                            tm_trig=tm_trig,
                                                            borrowed_funds=borrowed_funds,
                                                            assigned_wave=current_macd_cross__wave,
                                                            borrow_qty=0,
                                                            trigger_model=trigger_model,
                                                            )                
                blessings['blessings'].append(order_vars)

                ## MARGIN BUY consider another buy based on trinity
                wave_len = str(revrec['waveview'].at[ticker_time_frame, 'length'])
                if borrowed_funds == False and star_total_borrow_remaining > 0 and wave_len == '0' and alloc_deploy_margin > ticker_current_ask: # order did not have to dip into margin
                    print("Lets Buy on MARGIN !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                    # # handle trinity
                    trinity = calculate_margin_buy(trinity, waveguage_meter, order_type, smooth=4)
                    if trinity:
                        wave_amo = star_total_borrow_remaining * trinity
                        print("Margin Buy", wave_amo)
                        ## update KORS on based on trinity, ticker_time_frame

                        order_vars = order_vars__queen_order_items(trading_model=trading_model_theme, 
                                                                    king_order_rules=king_order_rules, 
                                                                    order_side='buy', 
                                                                    wave_amo=wave_amo, 
                                                                    maker_middle=maker_middle, 
                                                                    origin_wave=current_wave, 
                                                                    power_up_rangers=power_up_amo, 
                                                                    ticker_time_frame_origin=ticker_time_frame, 
                                                                    double_down_trade=double_down_trade, 
                                                                    wave_at_creation=current_macd_cross__wave,
                                                                    symbol=symbol,
                                                                    trigbee=trigbee,
                                                                    tm_trig=tm_trig,
                                                                    borrowed_funds=True,
                                                                    assigned_wave=current_macd_cross__wave,
                                                                    borrow_qty=0,
                                                                    trigger_model=trigger_model,
                                                                    )
                        blessings['blessings'].append(order_vars)
                
                charlie_bee['queen_cyle_times']['cc_knight'] = (datetime.now(est) - s_).total_seconds()

                return blessings
            else:
                msg = (f'KNIGHT EXIT NO WAVE AMO {ticker_time_frame} {ticker_current_ask} {round(wave_amo)}')
                # logging.warning(msg)
                print(msg)
                return {'kings_blessing': False}


            
        except Exception as e:
            print_line_of_error()

    def command_conscience(QUEEN, STORY_bee, QUEEN_KING, api, mkhrs):

        def repeat_purchase_delay(wave, ticker_time_frame, QUEEN):
            if ticker_time_frame in QUEEN['stars'].keys():
                if (datetime.now(est) - QUEEN['stars'].get(ticker_time_frame).get('last_buy')) < timedelta(seconds=60):
                    buy_msg = QUEEN['stars'].get(ticker_time_frame).get('msg')
                    msg = ("STOP BEE", 'Just Bought, Deploying Is Still', wave.at[ticker_time_frame, 'allocation_deploy'], " StarAtPlay: ", wave.at[ticker_time_frame, 'star_at_play'], " Ask Price", wave.at[ticker_time_frame, 'current_ask'], "REFRENCE:>>>", buy_msg, )
                    print(msg)
                    return True
            return False

        def autopilot_check(QUEEN_KING, symbol):

            try:
                # Get ticker_autopilot as list of dicts
                ticker_autopilot = QUEEN_KING['king_controls_queen'].get('ticker_autopilot', [])
                
                # Ensure it's a list
                if not isinstance(ticker_autopilot, list):
                    return True  # If not configured, allow buying
                
                # Find the symbol in the list
                symbol_autopilot = next((item for item in ticker_autopilot if item.get('symbol') == symbol), None)
                
                # If symbol not found in autopilot list, allow buying
                if not symbol_autopilot:
                    return True
                
                # Check if buy_autopilot is enabled
                if symbol_autopilot.get('buy_autopilot') != True:
                    # print(symbol, ": buy_autopilot FALSE")
                    return True
                
                # buy_autopilot is True, do not block
                return False
                
            except Exception as e:
                print(f"Error checking autopilot for {symbol}: {e}")
                return True  # Allow buying on error


        def stop_ticker(storygauge, ticker, QUEEN_KING):
            # Ensure Trading Model
            if ticker not in QUEEN_KING['king_controls_queen']['symbols_stars_TradingModel'].keys():
                msg = (f'TRADING model_does_not_exist {ticker}')
                print(msg)
                return True 

            if storygauge.loc[ticker, 'ticker_buying_power'] <= 0:
                msg = (f'{ticker} Conscience NO ticker_buying_power')
                print(msg)
                return True
            
            return False
        
        
        try:
            s_time = datetime.now(est)
            # def global level allow trade to be considered
            # 1 stop Level of tier trading only allowed x number of trades a day until you receive day trade margin
            client_user = QUEEN['client_user']
            prod = QUEEN['prod']
            revrec = QUEEN['revrec']
            waveview = revrec.get('waveview')
            storygauge = revrec['storygauge'].copy()
            if 'wash_sale_next_buy_date' in storygauge.columns:
                storygauge['wash_sale_next_buy_date'] = pd.to_datetime(storygauge['wash_sale_next_buy_date'], errors='coerce')
            else:
                storygauge['wash_sale_next_buy_date'] = None

            symbols = revrec['storygauge'][revrec['storygauge']['ticker_total_budget'] > 0]
            symbols = symbols.index.tolist()
            if len(symbols) == 0:
                symbols = ['SPY']
            
            if 'stars' not in QUEEN.keys():
                QUEEN['stars'] = {ttf: {'last_buy': datetime.now(est).replace(year=1989)} for ttf in symbols}           
            
            all_orders = QUEEN['queen_orders']
            active_orders = all_orders[all_orders['queen_order_state'].isin(active_queen_order_states)].copy()
            
            if type(QUEEN.get('price_info_symbols')) is not pd.core.frame.DataFrame:
                print("OLD QUEEN")
                return False

            req = process_app_requests(QUEEN, QUEEN_KING, request_name='buy_orders')
            if req.get('app_flag'):
                acct_info = QUEEN['account_info']
                revrec = refresh_chess_board__revrec(acct_info, QUEEN, QUEEN_KING, STORY_bee) ## Setup Board
                waveview = revrec.get('waveview')
                QUEEN['revrec'] = revrec
                god_save_the_queen(QUEEN, save_rr=True, save_q=True, save_qo=True, upsert_to_main_server=upsert_to_main_server)

            # refresh_price_info_from_storybee(QUEEN, STORY_bee, symbols)
        
            df = QUEEN.get('price_info_symbols')
            if df is not None and len(df) > 0:
                # df['priceinfo_ast'] = df['priceinfo'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)
                # df['current_ask'] = df['priceinfo_ast'].apply(lambda d: d.get('current_ask') if isinstance(d, dict) else None)
                dict_join = dict(zip(df.index, df['current_ask']))
                missing = set([i for i in waveview['symbol'].tolist() if i not in dict_join.keys()])
                if len(missing) > 0:
                    logging.info(f"MISSING current_ask in WAVEVIEW {missing}")
                
                waveview['current_ask'] = waveview['symbol'].map(dict_join).fillna(8989)
            else:
                logging.warning("WARNING: Price INFO SYMBOLS is empty or None")
                return False
            

            s_time = datetime.now(est)
            price_info_missing = [s for s in symbols if s not in QUEEN['price_info_symbols'].index]
            broker = 'alpaca' # WORKERBEE HOW TO DECIDE Which BROKER? Need Manual switch (per ticker?)-- brokers joined linked orders... :()

            existing_orders_df = get_existing_trigrule_orders(symbols, active_orders) # these symbols only checking on Symbols with Budget

            triggers = {}
            trigger_symbols = []
            for symbol in storygauge.index.tolist(): ## Handling Triggers
                if symbol not in ACTIVE_SYMBOLS:
                    logging.info(f'SKIP INACTIVE SYMBOL {symbol}')
                    continue

                trigger_model = check_trigrule_conditions(symbol, storygauge, QUEEN_KING, existing_orders_df)
                if trigger_model:
                    if trigger_model.get('ttf') in stars().keys():
                        ttf = f'{symbol}_{trigger_model.get("ttf")}'
                    else:
                        ttf = f'{symbol}_{"1Minute_1Day"}' # default
                    
                    triggers[ttf] = trigger_model
                    trigger_symbols.append(symbol)

            storygauge = storygauge[(storygauge['allocation_deploy'] > 89) | (storygauge.index.isin(trigger_symbols))].copy()
            # lll = {symbol: storygauge.at[symbol, 'allocation_deploy'] for symbol in storygauge.index.tolist()}
            # print(f"Symbols and their deploy amounts after filter {lll}")
            
            app_trig = False
            for symbol in storygauge.index.tolist(): ## Handling Buys
                # if symbol == 'QQQ':
                #     ipdb.set_trace()
                if symbol not in ACTIVE_SYMBOLS:
                    logging.info(f'SKIP INACTIVE SYMBOL {symbol}')
                    continue
                trigger_id = False
                if symbol in triggers.keys():
                    logging.info(f'TRIGRULE Triggered for {symbol} : {triggers[symbol]}')
                    trigger_id = triggers[symbol]
                
                crypto = True if symbol in crypto_currency_symbols else False
                if stop_ticker(storygauge, symbol, QUEEN_KING):
                    continue

                wave = waveview[waveview['symbol']==symbol]
                if not crypto:
                    wave = wave[(wave['allocation_deploy'] > 89) & (wave['allocation_deploy'] > wave['current_ask']) | (wave.index.isin(triggers.keys()))].copy()
                else:
                    wave = wave[(wave['allocation_deploy'] > 89) | (wave.index.isin(triggers.keys()))].copy()
                
                if len(wave) == 0:
                    continue

                wave = wave.sort_values('allocation_deploy', ascending=False)

                if not trigger_id:
                    not_enough = wave[(wave['allocation_deploy'] < wave['current_ask']) & (wave['allocation_deploy'] > 0)].copy()
                    if len(not_enough) > 0:
                        wave_amo_for_next_wave = not_enough['allocation_deploy'].sum()
                        logging.info(f"{wave_amo_for_next_wave} {symbol} NOT ENOUGH WAVE AMO FOR NEXT WAVE")

                # if crypto and QUEEN['prod']: # TEMP UNTIL CRYPTO handled in QUEEN CONTROLS WORKERBEE
                #     print("PRODUCTION OF CRYPTO ACCOUNT")
                #     broker = 'robinhood'
                """ the hunt """
                s_time = datetime.now(est)

                # queen_orders = QUEEN['queen_orders']
                for ticker_time_frame in wave.index.tolist():
                    s_time = datetime.now(est)
                    trigger_model = triggers.get(ticker_time_frame, False)

                    if not crypto and mkhrs != 'open':
                        continue
                    # if refresh_star_check(QUEEN_KING, queen_orders, symbol, ticker_time_frame):
                    #     continue
                    if repeat_purchase_delay(wave, ticker_time_frame, QUEEN): # WORKERBEE deprecate?
                        continue
                    if autopilot_check(QUEEN_KING, symbol) and not trigger_model:
                        continue
                    """# wash sale rule check"""
                    # now_time = datetime.now()
                    # if ticker in storygauge.index:
                    #     wash_sale_rule_buy_date = storygauge.at[ticker, 'wash_sale_next_buy_date']
                    #     if isinstance(wash_sale_rule_buy_date, datetime):
                    #         if now_time < wash_sale_rule_buy_date:
                    #             print("WASH SALE RULE NO BUYING ALLOWED")
                    #             continue

                    """# STORY_bee"""
                    # # check for missing tickers in price_info
                    if symbol in price_info_missing:
                        logging.info(f"MISSING PRICE INFO FOR {symbol}")

                        priceinfo_snap = process_priceinfo_snapshot(api=api, ticker=symbol, crypto=crypto)
                        df_priceinfo_symbols = pd.DataFrame([priceinfo_snap]).set_index('ticker', drop=False)
                        update_queens_priceinfo_symbols(QUEEN, df_priceinfo_symbols)

                        if symbol not in QUEEN['price_info_symbols'].index:
                            logging.info(f"STILL MISSING PRICE INFO FOR {symbol} SKIPPING")
                            continue

                    # trading model
                    trading_model = QUEEN_KING['king_controls_queen']['symbols_stars_TradingModel'].get(symbol)

                    # trigbee
                    trig = wave.at[ticker_time_frame, 'macd_state']
                    tm_trig = 'buy_cross-0' #trig # point to only 1
                    # buying threshold if in SELL wave
                    trig_wave_length = waveview.at[ticker_time_frame, 'length']
                    trig_wave_length_num = int(trig_wave_length)
  
                    if not trigger_model:
                        """ THE NEXT 2 CHECKS NOT NEEDED due to allocation_deploy > 0 ? WORKERBEE"""
                        # CHECK STAR TOTAL BUDGETS 
                        star_total_budgets = wave.loc[ticker_time_frame].get("remaining_budget", 0) + wave.loc[ticker_time_frame].get("remaining_budget_borrow", 0)
                        if star_total_budgets <= 0:
                            msg=(f'{ticker_time_frame} remaining budget used up', star_total_budgets)
                            # print(msg)
                            continue
                        # CHECK SYMBOL TOTAL BUDGETS
                        symbol_total_budgets = storygauge.loc[symbol].get("ticker_remaining_budget", 0) + storygauge.loc[symbol].get("ticker_remaining_borrow", 0)
                        if symbol_total_budgets <= 0:
                            msg=(f'{symbol} remaining budget used up', symbol_total_budgets)
                            # print(msg)
                            continue

                        elif 'sell' in trig and trig_wave_length_num < 3: # WORKERBEE This needs to be in king_controls_queen[{'1_Minute_1Day: 3}...] ?? different for each star!!
                            # print("Not Buying until Wave is longer then 22")
                            continue

                    # try: # """ Trigger Bees"""                         
                    s_ = datetime.now(est)
                    # ticker_in_action = True if ticker in active_orders['symbol'].to_list() else False
                    ticker_trig_action = ticker_trig_In_Action_cc(active_orders=active_orders, trig=tm_trig, ticker=symbol)
                    trig_action = trig_In_Action_cc(active_orders=active_orders, trig=tm_trig, ticker_time_frame=ticker_time_frame)
                    charlie_bee['queen_cyle_times']['cc_trig_in_action'] = (datetime.now(est) - s_).total_seconds()
                    # Protect the Knight # WORKERBEE this is only meant if you're trying to buy and trying to short
                    if len(ticker_trig_action) > 0 and trading_model.get('short_position') == True: # shorting allowed
                        msg=("Only 1 Trigger Allowed in ticker Shorting")
                        logging.warning(msg)
                        continue

                    """ HAIL TRIGGER, WHAT SAY YOU? ~forgive me but I bring a gift for the king and queen"""
                    s_time = datetime.now(est)
                    print(f"KNIGHT PROCESSING {ticker_time_frame} TRIG: {trig} TRADING MODEL: {trading_model.get('trading_model_name')}")
                    king_resp = king_knights_requests(
                        QUEEN=QUEEN, 
                        STORY_bee=STORY_bee, 
                        revrec=revrec, 
                        tm_trig=tm_trig, 
                        trigbee=trig,
                        ticker=symbol,
                        ticker_time_frame=ticker_time_frame, 
                        trading_model=trading_model, 
                        trig_action=trig_action, 
                        crypto=crypto, 
                        app_trig=app_trig,
                        trigger_model=trigger_model,
                    )
                    charlie_bee['queen_cyle_times']['cc_knights_request__cc'] = (datetime.now(est) - s_time).total_seconds()
                    if king_resp.get('kings_blessing'):
                        for blessing in king_resp.get('blessings'):
                            if blessing:
                                # WORKERBEE Handle Logic if order needs to be user Manual? or put in king knights request?
                                trigger_id = blessing['king_order_rules'].get('trigger_id', False)
                                if trigger_id:
                                    print("Trigger Model Order Placed", trigger_id, blessing.get('ticker_time_frame_origin'), " $", blessing.get('wave_amo'))
                                    flip_queen_trigger_rule_status(API_URL, trigger_id, client_user, prod, status='trig_running')
    
                                exx =  execute_buy_order(
                                                      broker=broker,
                                                      order_key=QUEEN['db_root'],
                                                      prod=prod,
                                                      api=api, 
                                                      blessing=blessing, 
                                                      trading_model=blessing.get('trading_model'), 
                                                      ticker=blessing.get('symbol'), 
                                                      ticker_time_frame=blessing.get('ticker_time_frame_origin'), 
                                                      trig=blessing.get('trigbee'), 
                                                      wave_amo=blessing.get('wave_amo'), 
                                                    #   order_type='market',
                                                    #   side='buy', 
                                                      crypto=crypto, 
                                                    #   limit_price=False, 
                                                      portfolio=QUEEN['portfolio']
                                                      )
                                if exx.get('executed'):
                                    new_queen_order_df = pd.DataFrame([exx['new_queen_order']]).set_index("client_order_id", drop=False)
                                    append_queen_order(QUEEN, new_queen_order_df)
                                    # logging.info(exx.get('msg'))
                                    msg = (exx.get('msg'))
                                    print(msg)
                                    # check if places by trigger model to flip switch of ID in QUEEN_KING

                                    if 'stars' not in QUEEN.keys():
                                        QUEEN['stars'] = {ticker_time_frame: {'last_buy': datetime.now(est), 'msg': msg}}
                                    else:
                                        QUEEN['stars'].update({ticker_time_frame: {'last_buy': datetime.now(est), 'msg': msg}})
                                    if exx.get('trigger_buy'):
                                        # WORKERBEE Save Queen KING and turn off Trigger OR Just let Max Orders Handle? I think turn off
                                        pass
                        QUEEN = refresh_broker_account_portolfio(api, QUEEN)
                        acct_info = QUEEN['account_info']
                        """Rev Rec"""
                        revrec = refresh_chess_board__revrec(acct_info, QUEEN, QUEEN_KING, STORY_bee) ## Setup Board
                        QUEEN['revrec'] = revrec
                        god_save_the_queen(QUEEN, save_q=True, save_rr=True, save_qo=True, console=True, upsert_to_main_server=upsert_to_main_server)

                
                charlie_bee['queen_cyle_times']['cc_thehunt__cc'] = (datetime.now(est) - s_time).total_seconds()

            return True
        except Exception as e:
            print_line_of_error(f'KNIGHT ERROR {e}')


    """>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> ORDER MANAGEMENT <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< """
    """>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> ORDER MANAGEMENT <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< """
    """>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> ORDER MANAGEMENT <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< """




    def return_snap_priceinfo__pollenData(QUEEN, STORY_bee, ticker, api, crypto):
        # read check if ticker is active...if it is return into from db ELSE return broker data 
        try:
            call_snap = False
            ttf = f'{ticker}{"_1Minute_1Day"}'
            tic_missing = []
            if ttf not in QUEEN['heartbeat']['available_tickers']:
                # print(f"{ttf} NOT in Workerbees")
                ticker, ttime, tframe = ttf.split("_")
                if ticker not in tic_missing:
                    tic_missing.append(ticker)
                call_snap = True
            
            error_msg = []
            if tic_missing:
                error_msg.append(f"{tic_missing}")
            # if error_msg:
            #     print(f'snapshotCALL: Missing Tickers in STORYBEE {tic_missing}')
            
            
            if call_snap:
                logging.info(f"SNAPSHOT PRICEINFO CALL FOR {ticker} in QUEEN")

                # get latest pricing
                temp = get_priceinfo_snapshot(api, ticker, crypto)
                if not temp:
                    logging.info(f"{ticker} ERROR in Get priceinfo SNAPSHOT")
                    return {}

                current_price = temp['price']
                current_ask = temp['ask']
                current_bid = temp['bid']

                # best limit price
                best_limit_price = get_best_limit_price(ask=current_ask, bid=current_bid)
                maker_middle = best_limit_price['maker_middle']
                ask_bid_variance = current_bid / current_ask
            else:
                current_price = STORY_bee[f'{ticker}_1Minute_1Day']['story']['current_mind'].get('close') #STORY_bee[f'{ticker}_1Minute_1Day']['story'].get('current_price')
                current_ask = STORY_bee[f'{ticker}_1Minute_1Day']['story'].get('current_ask')
                current_bid = STORY_bee[f'{ticker}_1Minute_1Day']['story'].get('current_bid')
                maker_middle = STORY_bee[f'{ticker}_1Minute_1Day']['story'].get('maker_middle')
                ask_bid_variance = STORY_bee[f'{ticker}_1Minute_1Day']['story'].get('ask_bid_variance')
            
            priceinfo = {'ticker': ticker, 'current_price': current_price, 'current_bid': current_bid, 'current_ask': current_ask, 'maker_middle': maker_middle, 'ask_bid_variance': ask_bid_variance}
            
            return priceinfo
        except Exception as e:
            print_line_of_error(f'priceinfo queenbee {e}')
            return {}


    def honeyGauge_metric(run_order):
        # measure latest profits to determine to sell out / not
        
        gauge = run_order['honey_gauge']
        gauge_len = len(gauge)
        
        if gauge_len > 5:
            last_3 = [gauge[(gauge_len - n) *-1] for n in range(1,4)] # roughly ~5seconds
            last_3_avg = sum(last_3) / len(last_3)
        else:
            last_3_avg = False
        if gauge_len > 11:
            last_9 = [gauge[(gauge_len - n) *-1] for n in range(1,10)] # roughly ~13seconds
            last_9_avg = sum(last_9) / len(last_9)
        else:
            last_9_avg = False
        if gauge_len > 11:
            last_15 = [gauge[(gauge_len - n) *-1] for n in range(1,16)] # roughly ~10seconds
            last_15_avg = sum(last_15) / len(last_15)
        else:
            last_15_avg = False
        if gauge_len > 30:
            last_30 = [gauge[(gauge_len - n) *-1] for n in range(1,29)] # roughly ~35seconds
            last_30_avg = sum(last_30) / len(last_30)
        else:
            last_30_avg = False
        
        
        return {'last_3_avg': last_3_avg, 'last_9_avg': last_9_avg, 'last_15_avg': last_15_avg, 'last_30_avg': last_30_avg}


    def macdGauge_metric(STORY_bee, ticker_time_frame, trigbees=['buy_cross-0', 'sell_cross-0'], number_ranges=[5]): # , 11, 16, 24, 33
        # measure trigger bee strength
        try:
            if ticker_time_frame not in STORY_bee.keys():
                return {'metrics': {'sell_cross-0': {5: {'avg': 1}}}}
            if len(STORY_bee[ticker_time_frame]['story']['macd_gauge']) > 0:
                gauge = STORY_bee[ticker_time_frame]['story']['macd_gauge']
                gauge_len = len(gauge)
                
                d_return = {}
                for trigbee in trigbees:
                    buy_sell = trigbee.split("-")[0]
                    d_return[trigbee] = {}
                    for num in number_ranges:
                        d_return[trigbee][num] = {}
                        if gauge_len > num:
                            last_n = [gauge[(gauge_len - n) *-1] for n in range(1,num)]
                            avg = sum([1 for i in last_n if buy_sell in trigbee]) / len(last_n)
                            d_return[trigbee][num].update({'avg': avg})
                        else:
                            d_return[trigbee][num].update({'avg': 0})
                
                return {'metrics': d_return}
            else:
                return {'metrics': {'sell_cross-0': {5: {'avg': 1}}}}
        except Exception as e:
            print(e, print_line_of_error())


    def release_trig_sell_stop(QUEEN, ticker, client_order_id):
        # does as it says
        try:
            qo_states = RUNNING_CLOSE_Orders + RUNNING_OPEN
            running_close = return_queen_orders__query(QUEEN=QUEEN, queen_order_states=qo_states, ticker=ticker)
            if len(running_close) > 0:
                in_running_close = True if client_order_id in running_close['exit_order_link'].tolist() else False
                if in_running_close == False:
                    msg=("Releaseing Order back to Bishop be Sold: ", client_order_id)
                    logging.info(msg)
                    QUEEN['queen_orders'].at[client_order_id, 'order_trig_sell_stop'] = False
                    return True
            else:
                print("release order back to Bishop no linked orders active")
                logging.info(("Releaseing Order back to Bishop be Sold: ", client_order_id))
                QUEEN['queen_orders'].at[client_order_id, 'order_trig_sell_stop'] = False
                return True 

            return False                
        except Exception as e:
            print(e)

            # do you have any active running_close against you?

    
    def async_api_alpaca__snapshots_priceinfo(symbols, STORY_bee, api, QUEEN, mkhrs='open'): # re-initiate for i timeframe 

        async def get_priceinfo(session, ticker, api, STORY_bee, QUEEN, crypto):
            async with session:
                try:
                    priceinfo = return_snap_priceinfo__pollenData(QUEEN=QUEEN, STORY_bee=STORY_bee, ticker=ticker, api=api, crypto=crypto)
                    if not priceinfo:
                        return {}
                    return {'priceinfo': priceinfo, 'ticker': ticker}
                except Exception as e:
                    print(e)
                    raise e
        
        async def main(symbols, STORY_bee, api, QUEEN):
            async with aiohttp.ClientSession() as session:
                return_list = []
                tasks = []
                # symbols = [qo['symbol'] for qo in queen_order__s]
                for ticker in set(symbols):
                    crypto = True if ticker in crypto_currency_symbols else False
                    # Continue Only if Market Open
                    if not crypto and mkhrs != 'open':
                        continue # markets are not open for you
                    if ticker not in ACTIVE_SYMBOLS:
                        print(f'SKIP INACTIVE SYMBOL {ticker}')
                        continue
                    tasks.append(asyncio.ensure_future(get_priceinfo(session, ticker, api, STORY_bee, QUEEN, crypto)))
                original_pokemon = await asyncio.gather(*tasks)
                for pokemon in original_pokemon:
                    return_list.append(pokemon)
                
                return return_list

        list_return = asyncio.run(main(symbols, STORY_bee, api, QUEEN))

        return list_return

    
    def update_queens_priceinfo_symbols(QUEEN, df):
        df_main = QUEEN['price_info_symbols']
        # fitler out incoming symbols
        df_main = df_main[~df_main.index.isin(df.index)]
        # join in new data
        df_main = pd.concat([df_main, df])
        # set data back to QUEEN
        QUEEN['price_info_symbols'] = df_main
        
        return QUEEN


    def king_bishops_QueenOrder(QUEEN_KING, STORY_bee, run_order, priceinfo, revrec):

        def check_revrec(
                        client_order_id,
                        sell_qty, 
                        revrec, 
                        crypto, 
                        ticker_time_frame, 
                        makers_middle_price, 
                        close_order_today, 
                        app_request,
                        min_allocation_field='ticker_total_budget',
                        current_long_value='star_buys_at_play_allocation',
                         ):
            try:
                symbol = ticker_time_frame.split("_")[0]
                # if client_order_id == 'run__12935399':
                #     ipdb.set_trace()

                if close_order_today or app_request:
                    logging.info(f"{ticker_time_frame} CLOSE Order TODAY")
                    return sell_qty
                
                if symbol not in revrec['storygauge'].index:
                    logging.info(f"BISHOP check revrec: {ticker_time_frame} MISSING in RevRec")
                    return sell_qty

                min_allocation = revrec['storygauge'].loc[symbol].get(min_allocation_field, 0)
                if min_allocation == 0:
                    logging.info(f'BISHOP check revrec: {ticker_time_frame} no Min Allocation Sell ALL')
                    return sell_qty

                current_long = revrec['storygauge'].loc[symbol].get(current_long_value, 0)

                pending_sells = QUEEN['queen_orders'][
                    (QUEEN['queen_orders']['symbol'] == symbol) &
                    (QUEEN['queen_orders']['queen_order_state'].isin(['submitted', 'running_close'])) &
                    (QUEEN['queen_orders']['side'] == 'sell')
                ]

                # Calculate total value of pending sells
                pending_sell_value = 0
                if len(pending_sells) > 0:
                    for idx, sell_order in pending_sells.iterrows():
                        sell_qty = float(sell_order['qty'])
                        sell_price = sell_order.get('limit_price', makers_middle_price)
                        if not sell_price:
                            # print("NO LIMIT PRICE using maker middle")
                            sell_price = float(makers_middle_price)
                        if not isinstance(sell_price, (int, float)):
                            sell_price = float(makers_middle_price)
                        pending_sell_value += (sell_qty * sell_price)
                    
                    logging.info(f"{ticker_time_frame} PENDING SELLS DETECTED: {len(pending_sells)} orders, Total Value: ${round(pending_sell_value)}")

                # Adjust current_long to account for pending sells
                # sellable = max(0, current_long - min_allocation)
                adjusted_current_long = current_long - pending_sell_value
                sellable = max(0, adjusted_current_long - min_allocation)

                if sellable <= 0:
                    logging.info(f"{ticker_time_frame} NOT Allowed to SELL Min Allocation LONG: {round(current_long)} MIN: {round(min_allocation)} SELLABLE:{sellable}")
                    return 0

                if not crypto:
                    # Equities: integer shares, never oversell
                    raw_qty = sellable / makers_middle_price
                    sellable_qty = int(raw_qty)
                    # Cap by requested sell_qty
                    adjust_qty = min(sellable_qty, int(sell_qty))
                    # Final check: do not sell more than sellable
                    if adjust_qty * makers_middle_price > sellable:
                        adjust_qty = int(sellable // makers_middle_price)
                else:
                    # Crypto: use Decimal for precision, round down
                    raw_qty = Decimal(str(sellable)) / Decimal(str(makers_middle_price))
                    sellable_qty = raw_qty.quantize(Decimal('0.000000'), rounding=ROUND_DOWN)
                    # Cap by requested sell_qty
                    adjust_qty = min(sellable_qty, Decimal(str(sell_qty)))
                    # Final check: do not sell more than sellable
                    if adjust_qty * Decimal(str(makers_middle_price)) > Decimal(str(sellable)):
                        adjust_qty = (Decimal(str(sellable)) / Decimal(str(makers_middle_price))).quantize(Decimal('0.000000'), rounding=ROUND_DOWN)

                # Defensive: never negative
                if adjust_qty != sell_qty:
                    logging.info(f"SELL QTY ADJUSTMENT {ticker_time_frame} adjusted sell qty: {adjust_qty} sell qty: {sell_qty}")
                if adjust_qty <= 0:
                    logging.info(f"{ticker_time_frame} NOT Allowed to SELL Adjusted QTY == {adjust_qty} : Sell Qty == {sell_qty}")
                    return 0

                return float(adjust_qty)

                
            except Exception as e:
                print_line_of_error(f'QUEEN: {ticker_time_frame} :: REVREC CHECK ERROR {e}')
                return 0
        
        """if you made it here you are running somewhere, I hope you find your way, I'll always bee here to help"""
        try:
            # # # Stars in Heaven

            s_time = datetime.now(est)
            # gather run_order Vars
            symbol = run_order['symbol']

            trigname = run_order['trigname']
            order_rules = run_order.get('order_rules')
            client_order_id = run_order['client_order_id']
            take_profit = float(order_rules['take_profit'])
            sell_out = float(order_rules.get('sell_out', 0.0))
            sell_out = 0.0 if not sell_out else sell_out
            sell_out = sell_out *-1 if sell_out > 0 else sell_out
            sell_qty = float(run_order['qty_available'])
            ticker_time_frame = run_order['ticker_time_frame']
            ticker_time_frame_origin = run_order['ticker_time_frame_origin']
            entered_trade_time = run_order['datetime'].astimezone(est)
            time_in_trade_datetime = datetime.now(est) - entered_trade_time
            close_order_today = order_rules.get('close_order_today', None)

            honey = run_order['honey']

            # Return Latest Model Vars in QUEEN
            ticker, tframe, tperiod = ticker_time_frame_origin.split("_")
            model_ticker = 'SPY' if run_order['symbol'] not in QUEEN_KING['king_controls_queen']['symbols_stars_TradingModel'].keys() else run_order['symbol']
            trading_model = QUEEN_KING['king_controls_queen']['symbols_stars_TradingModel'].get(model_ticker)
            trading_model_star = trading_model['stars_kings_order_rules'].get(f'{tframe}_{tperiod}')

            bishop_keys_list = ['ticker', 'ticker_time_frame', 'trigname', 'client_order_id']
            bishop_keys = {i: run_order[i] for i in bishop_keys_list}
            crypto = True if run_order['ticker'] in crypto_currency_symbols else False
            bishop_keys['qo_crypto'] = crypto
            # print("BISHOP KEYS", bishop_keys)
            
            origin_closing_orders_df = return_closing_orders_df(QUEEN=QUEEN, exit_order_link=client_order_id)
            first_sell = True if len(origin_closing_orders_df) > 0 else False
            
            # this occurs when selling is chunked
            running_close_legs = False

            # global limit type order type
            if str(trading_model_star.get('trade_using_limits')).lower() == 'true':
                order_type = 'limit'
                limit_price = priceinfo['maker_middle']
            elif str(order_rules['trade_using_limits']).lower() == 'true':
                order_type = 'limit'
                limit_price = priceinfo['maker_middle']
            else:
                order_type = 'market'
                limit_price = False
            
            bishop_keys['order_type'] = order_type
            bishop_keys['limit_price'] = limit_price

            # Only if there are available shares

            sell_order = False # #### >>> convince me to sell  $$

            # WORKERBEE this can be replaced with a deque list
            macd_gauge = macdGauge_metric(STORY_bee=STORY_bee, ticker_time_frame=ticker_time_frame, trigbees=['buy_cross-0', 'sell_cross-0'], number_ranges=[5, 11, 16, 24, 33])
            # honey_gauge = honeyGauge_metric(run_order)

            charlie_bee['queen_cyle_times']['om_bishop_block1_queenorder__om'] = (datetime.now(est) - s_time).total_seconds()
            s_time = datetime.now(est)

            """ Bishop Knight Waves """
            # df_waves_story = STORY_bee[ticker_time_frame]['waves']['story']
            # current_story_wave = df_waves_story.iloc[-1].to_dict()

            # handle not in Story default to SPY
            if ticker_time_frame_origin not in STORY_bee.keys():
                ticker_time_frame_origin = "SPY_1Minute_1Day"
            ticker, tframe, tperiod = ticker_time_frame_origin.split("_")
            star = f'{tframe}{"_"}{tperiod}'

            # POLLEN STORY
            ttframe_story = STORY_bee[ticker_time_frame_origin]['story']
            current_macd = ttframe_story['macd_state']
            current_macd_time = int(current_macd.split("-")[-1])
            QUEEN['queen_orders'].at[client_order_id, 'current_macd'] = current_macd
            
            # Gather main sell reason groups
            sell_trigbee_trigger = True if str(order_rules['sell_trigbee_trigger']).lower() == 'true' else False
            stagger_profits = True if str(order_rules['stagger_profits']).lower() == 'true' else False
            scalp_profits = True if str(order_rules['scalp_profits']).lower() == 'true' else False
            # macd_tier = current_macd_time
            
            charlie_bee['queen_cyle_times']['om_bishop_block2_queenorder__om'] = (datetime.now(est) - s_time).total_seconds()
            s_time = datetime.now(est)

            """ WaterFall sell chain """
            def waterfall_sellout_chain(client_order_id, 
                                        run_order, 
                                        order_type, 
                                        limit_price, 
                                        sell_trigbee_trigger, 
                                        sell_qty, 
                                        sell_out,
                                        order_rules=order_rules, 
                                        QUEEN=QUEEN):
                save_order=False
                sell_reasons = []
                now_time = datetime.now(est)
                close_order_today = order_rules.get('close_order_today')
                makers_middle_price = priceinfo.get('maker_middle')
                if 'sell_reason' not in run_order.keys():
                    run_order['sell_reason'] = []
                if 'queen_wants_to_sell_qty' not in run_order.keys():
                    run_order['queen_wants_to_sell_qty'] = 0

                try:
                    sell_trigbee_datetime = order_rules.get('sell_trigbee_date')
                    if sell_trigbee_datetime:
                        dt = pd.to_datetime(order_rules.get('sell_trigbee_date'))
                        sell_trigbee_datetime = dt.tz_localize(est, ambiguous='NaT', nonexistent='NaT')
                    else:
                        sell_trigbee_datetime = now_time
                except Exception as e:
                    print("SELL TRIG DATE ERROR", e)
                    sell_trigbee_datetime = now_time
                
                wave_cross_switched__buytosell = True if "sell" in current_macd and symbol not in reverse_indexes else False
                # wave_cross_switched__selltobuy = True if "buy" in current_macd and symbol in reverse_indexes else False

                time_to_bell_close = (now_time.replace(hour=16, minute=00, second=0) - now_time).total_seconds()

                try:
                    """ Take Profit """
                    if honey >= take_profit:
                        # print(f"{ticker_time_frame} selling out due PROFIT ACHIVED order profit: {take_profit}")
                        sell_reasons.append('order_rules__take_profit')
                        limit_price = priceinfo['maker_middle'] if order_type == 'limit' else False

                    """ Stop Loss """
                    if sell_out: # can be None or 0==None
                        if honey <= sell_out:
                            # print(f"{ticker_time_frame} selling out due STOP LOSS {client_order_id}")
                            sell_reasons.append('order_rules__sellout')
                            limit_price = priceinfo['maker_middle'] if order_type == 'limit' else False

                    """ Wave Cross """
                    # if sell_trigbee_trigger:
                    if wave_cross_switched__buytosell and sell_trigbee_datetime <= now_time and time_in_trade_datetime.seconds > 60:
                        # print("SELL ORDER change from Buy to Sell", current_macd, current_macd_time)
                        if macd_gauge['metrics']['sell_cross-0'][5]['avg'] > .5:
                            sell_reasons.append('order_rules__macd_cross_buytosell')
                            limit_price = priceinfo['maker_middle'] if order_type == 'limit' else False

                    """ Close Order Today """
                    if close_order_today: # WORKERBEE Change this to sell_date instead to check the datetime and if its past sell
                        if order_rules.get('close_order_today_allowed_timeduration', 60) >= time_to_bell_close and time_in_trade_datetime > timedelta(seconds=60):
                            if time_to_bell_close < 133:
                                print("Selling Out, Trade Not Allowed to go past day")
                                sell_reasons.append('close_order_today')
                                limit_price = priceinfo['maker_middle'] if order_type == 'limit' else False
                            
                    """ APP REQUESTS"""
                    app_request = False
                    app_req = process_sell_app_request(QUEEN=QUEEN, QUEEN_KING=QUEEN_KING, run_order=run_order)
                    if app_req['app_flag']:       
                        print("QUEEN processing app sell order")
                        sell_reasons.append('app_request')
                        app_request = True
                        sell_qty = float(app_req['sell_qty'])
                        order_type = app_req['type']
                        order_side = app_req['side']
                        limit_price = False

                    """ Check RevRec for Sell Qty Allowed Will return 0 if not allowed to Sell """
                    sell_qty = check_revrec(
                                            client_order_id=client_order_id,
                                            sell_qty=sell_qty, 
                                            revrec=revrec, 
                                            crypto=crypto, 
                                            ticker_time_frame=ticker_time_frame, 
                                            makers_middle_price=makers_middle_price, 
                                            close_order_today=close_order_today,
                                            app_request=app_request,
                                            min_allocation_field='ticker_total_budget',
                                            )

                    # ALWAYS update queen_wants_to_sell_qty and sell_reason (even if not selling)
                    current_sell_reasons = QUEEN['queen_orders'].at[client_order_id, 'sell_reason']
                    current_sell_qty = QUEEN['queen_orders'].at[client_order_id, 'queen_wants_to_sell_qty']
                    
                    # Track if changes occurred
                    reasons_changed = str(current_sell_reasons) != str(sell_reasons)
                    qty_changed = current_sell_qty != sell_qty
                    
                    # Only update if there are sell_reasons OR if queen changed her mind
                    if sell_reasons:                        
                        if reasons_changed:
                            QUEEN['queen_orders'].at[client_order_id, 'sell_reason'] = sell_reasons
                            logging.info(f"{ticker_time_frame}: Sell Reason Changed from {current_sell_reasons} to {sell_reasons}")
                        
                        # Update queen_wants_to_sell_qty if changed (and sell_qty > 0)
                        if qty_changed and sell_qty > 0:
                            QUEEN['queen_orders'].at[client_order_id, 'queen_wants_to_sell_qty'] = sell_qty
                            logging.info(f"{ticker_time_frame}: QUEEN wants to sell QTY changed from {current_sell_qty} to {sell_qty}")
                        elif sell_qty == 0:
                            # Queen wants to sell but can't (allocation blocking)
                            logging.info(f"{ticker_time_frame}: QUEEN wants to sell but allocation prevents it. Reasons: {sell_reasons}")
                            # Keep previous queen_wants_to_sell_qty for reference
                            
                    else:
                        # Queen does NOT want to sell (no reasons) # Clear sell_reason if it had reasons before
                        if current_sell_reasons:
                            QUEEN['queen_orders'].at[client_order_id, 'sell_reason'] = []
                            logging.info(f"{ticker_time_frame}: Sell reasons cleared (was: {current_sell_reasons})")
                        
                        # Reset queen_wants_to_sell_qty if it was set before
                        if current_sell_qty > 0:
                            QUEEN['queen_orders'].at[client_order_id, 'queen_wants_to_sell_qty'] = 0
                            logging.info(f"{ticker_time_frame}: QUEEN no longer wants to sell (was: {current_sell_qty})")

                        
                    if not close_order_today and not app_request: # based on user input, profit, sellout,  and sell_trigbee_trigger...
                        """ AUTO PILOT """
                        ticker_autopilot = QUEEN_KING['king_controls_queen'].get('ticker_autopilot', [])
                        if not isinstance(ticker_autopilot, list):
                            return {'sell_order': False, 'save_order': save_order}
                        symbol_autopilot = next((item for item in ticker_autopilot if item.get('symbol') == symbol), None)
                        
                        if symbol_autopilot:
                            if symbol_autopilot.get('sell_autopilot') != True:
                                # print(symbol, ": sell_autopilot FALSE", " -- Sell Reasons", sell_reasons)
                                return {'sell_order': False, 'save_order': save_order}
                        else:
                            # Symbol not in autopilot list, block selling
                            return {'sell_order': False, 'save_order': save_order}

                    order_side = 'sell'
                    mm_cost = priceinfo.get('maker_middle') * sell_qty
                    if sell_qty > 0 and sell_reasons:
                        msg = ("Bishop SAYs SELL:", symbol, ticker_time_frame, sell_reasons, current_macd, sell_qty, mm_cost)
                        print(msg)
                        # logging.info(msg)

                        return {
                        'sell_order': True, 
                        'sell_reason': sell_reasons, 
                        'order_side': order_side, 
                        'order_type': order_type, 
                        'sell_qty': sell_qty, 
                        'limit_price': limit_price, 
                        'app_request': app_request,
                        'maker_middle_cost': mm_cost,
                        'save_order': True,
                        }
                    else:
                        # print("Bishop DONOT SELL Min.Allocation Stop", ticker_time_frame)
                        return {'sell_order': False, 'save_order': save_order}

                
                except Exception as e:
                    print('waterfall error', e, " er line>>", print_line_of_error())

            king_bishop = waterfall_sellout_chain(client_order_id, 
                                                  run_order, 
                                                  order_type, 
                                                  limit_price, 
                                                  sell_trigbee_trigger, 
                                                  sell_qty, 
                                                  sell_out,
                                                  order_rules=order_rules, 
                                                  QUEEN=QUEEN)

            charlie_bee['queen_cyle_times']['om_bishop_block3__om'] = (datetime.now(est) - s_time).total_seconds()

            save_order = True if king_bishop.get('save_order') else False

            if king_bishop['sell_order']:
                order_vars = order_vars__queen_order_items(order_side='sell',  
                maker_middle=king_bishop['limit_price'],
                sell_reason=king_bishop['sell_reason'], 
                sell_qty=king_bishop['sell_qty'], 
                running_close_legs=running_close_legs,
                ticker_time_frame_origin=ticker_time_frame,
                first_sell=first_sell, 
                time_intrade=time_in_trade_datetime)
                return {
                        'bee_sell': True, 
                        'order_vars': order_vars, 
                        'app_request': king_bishop['app_request'], 
                        'bishop_keys':bishop_keys, 
                        'save_order': True
                    }
            else:
                return {
                    'bee_sell': False, 
                    'run_order': run_order, 
                    'save_order': save_order
                }

        except Exception as e:
            print_line_of_error("Bishop Selling Error")
            logging.error("Bishop Selling Error")


    def order_management(BROKER, STORY_bee, QUEEN, QUEEN_KING, api, QUEENsHeart, charlie_bee, mkhrs='closed'): 

        def stop_queen_order_from_kingbishop(run_order):
            # Stop Queen Order from going to the Kings Court -- order_trig_sell_stop, qty_avilable, autopilot'
            
            ttf = run_order.get('ticker_time_frame')
            
            if str(run_order['order_trig_sell_stop']).lower() == 'true': ### consider remaining qty
                return True
            elif run_order['queen_order_state'] not in RUNNING_Orders:
                print(ttf, run_order['client_order_id'], ": QUEEN ORDER STATE NOT RUNNING")
                return True
            elif run_order['status_q'] != 'filled':
                print(ttf, run_order['client_order_id'], ": QUEEN ORDER STATUS NOT FILLED")
                return True
            elif float(run_order['qty_available']) == 0:
                print(ttf, run_order['client_order_id'], ": QUEEN ORDER QTY AVAILABLE IS ZERO 0")
                return True
            else:
                return False


        # WORKERBEE FIND RETURN BROKER DELTA AND FIX WITH QTY_AVAILABLE
        def queen_orders_main(BROKER, QUEEN, STORY_bee, QUEEN_KING, charlie_bee, mkhrs):
                    
            
            try: # Order Loop
                s_loop = datetime.now(est)
                df_active = QUEEN['queen_orders']
                df_active = df_active[df_active['queen_order_state'].isin(active_queen_order_states)]
                qo_active_index = df_active['client_order_id'].to_list()
                symbols = list(set(df_active['symbol'].to_list()))
                if not symbols:
                    print("No Orders Yet")
                    return True

                long, short, cost_basis_current = return_long_short(active_orders=df_active)
                QUEEN['heartbeat']['long'] = round(long)
                QUEEN['heartbeat']['short'] = round(short)
                
                s_time = datetime.now(est)

                price_info_missing = [s for s in symbols if s not in QUEEN['price_info_symbols'].index]
                
                s_time_qOrders = datetime.now(est)

                # api # refresh all broker orders which are still pending # Confirm Sync with Broker 
                after_hours = True if mkhrs == 'closed' else False
                save_b = False 
                for idx, c_order_id in enumerate(qo_active_index): # Confirm Sync with Broker 
                    if not c_order_id.startswith("run") and not c_order_id.startswith("close"):
                        print("CLIENT ORDER ID is not a run or close order: index: ", idx, "c_order_id: ", c_order_id)
                        continue
                    if pd.isna(c_order_id):
                        print("CLIENT ORDER ID is NAN: index: ", idx)
                        continue

                    symbol = QUEEN['queen_orders'].loc[c_order_id].get('symbol')
                    crypto = True if symbol in crypto_currency_symbols else False
                    if not crypto and after_hours:
                        continue
                    if symbol not in ACTIVE_SYMBOLS:
                        print(f'SKIP INACTIVE SYMBOL {symbol}')
                        continue   
                    # Confirm Sync with Broker 
                    pull_order_status = df_active.at[c_order_id, 'status_q']
                    broker = df_active.at[c_order_id, 'broker']
                    broker = handle_broker(broker)
                    if c_order_id not in BROKER['broker_orders'].index or str(pull_order_status) != 'filled':
                        # print("checking order status for", c_order_id)
                        order_status = check_order_status(broker=broker, api=api, client_order_id=c_order_id)
                        if not order_status:
                            adhoc_handle_queen_order_broker_failure(order_status, QUEEN, c_order_id)
                            continue
                        
                        if update_broker_order_status(BROKER, order_status):
                            save_b = True

                if save_b:
                    if pg_migration:
                        PollenDatabase.upsert_data(BROKER.get('table_name'), BROKER.get('key'), BROKER, main_server=server)
                    else:
                        PickleData(BROKER.get('source'), BROKER, console=False)
                broker_time = (datetime.now(est) - s_time_qOrders).total_seconds()
                # print("broker time: ", price_info_symbol_time)
                charlie_bee['queen_cyle_times']['om_order_status_api'] = broker_time


                s_time = datetime.now(est)
                queen_orders__dict = {}
                save = False
                save_broker_order = False
                save_revrec = False
                for idex, idx in enumerate(qo_active_index):
                    save_order = False
                    if pd.isna(idx):
                        # print("CLIENT ORDER ID is NAN: index: ", idex)
                        continue
                    if idx not in BROKER['broker_orders'].index:
                        # print("CLIENT ORDER ID not in BROKER orders: index: ", idex, "idx: ", idx)
                        continue
                    
                    run_order = QUEEN['queen_orders'].loc[idx].to_dict()
                    symbol = run_order.get('symbol')
                    crypto = True if symbol in crypto_currency_symbols else False

                    if symbol not in ACTIVE_SYMBOLS:
                        logging.info(f'OM: SKIP INACTIVE SYMBOL {symbol}')
                        continue
                    if symbol not in QUEEN['price_info_symbols'].index:
                        logging.info(f"PriceINFO Missing for symbol in QUEEN price_info_symbols: {symbol}")
                        # get priceinfo here to try to continue
                        priceinfo_snap = process_priceinfo_snapshot(api=api, ticker=symbol, crypto=crypto)
                        if priceinfo_snap:
                            df_priceinfo = pd.DataFrame([priceinfo_snap]).set_index('ticker', drop=True)
                            update_queens_priceinfo_symbols(QUEEN, df_priceinfo)
                            print("Updated QUEEN price_info_symbols with snapshot for ", symbol)
                        else:
                            logging.info(f"ERROR!! : Could not retrieve priceinfo snapshot for {symbol}")
                            continue

                    # Queen Order Local Vars
                    broker = run_order['broker']
                    
                    # broker = handle_broker(broker)
                    if broker != 'alpaca':
                        print(f'BROKER {broker} NOT supported for Queen Orders UPDATING to alpaca for {idx}')
                        save_order = True
                        broker = 'alpaca'
                        QUEEN['queen_orders'].at[idx, 'broker'] = broker
                        save_queen_order(QUEEN, prod=QUEEN['prod'], client_order_id=idx, upsert_to_main_server=upsert_to_main_server)
                    
                    app_req = process_sell_app_request(QUEEN=QUEEN, QUEEN_KING=QUEEN_KING, run_order=run_order, check_only=True).get('app_flag')
                    
                    
                    try: 
                        # snapshot prices bar                        
                        # priceinfo = QUEEN['price_info_symbols'].at[symbol, 'priceinfo']
                        priceinfo = QUEEN['price_info_symbols'].loc[symbol]
                        
                        order_status = BROKER['broker_orders'].loc[idx].to_dict()

                        # Updates Broker Order if changed
                        queen_order_lastmod = normalize_timestamp(str(run_order.get('updated_at')))
                        broker_order_lastmod = normalize_timestamp(str(order_status.get('updated_at')))

                        if queen_order_lastmod != broker_order_lastmod:
                            logging.info(f"{symbol} ORDER {idx} : Broker Order Updated {broker_order_lastmod} vs {queen_order_lastmod}")
                            order_status = check_order_status(broker=broker, api=api, client_order_id=idx)
                            if not order_status:
                                adhoc_handle_queen_order_broker_failure(order_status, QUEEN, idx)
                                continue                     
                            run_order, save_order = update_latest_queen_order_status(QUEEN=QUEEN, queen_order_idx=idx, order_status=order_status, save_order=save_order)
                            save_order = True
                            save_broker_order = True
                            update_broker_order_status(BROKER, order_status)


                        # Process Queen Order States
                        run_order, save_order = route_queen_order(
                                                            QUEEN=QUEEN, 
                                                            queen_order=run_order, 
                                                            queen_order_idx=idx, 
                                                            order_status=order_status, 
                                                            priceinfo=priceinfo,
                                                            save_order=save_order,
                                                      ) ## send in order_status
                        if save_order and not save_revrec:
                            save_revrec = True

                        if float(run_order.get('qty_available')) > 0 and run_order.get('order_trig_sell_stop') == True:
                            if release_trig_sell_stop(QUEEN=QUEEN, ticker=symbol, client_order_id=idx):
                                print("RELEASE TRIG SELL STOP", symbol, idx)
                                save_queen_order(QUEEN, prod=QUEEN['prod'], client_order_id=idx, upsert_to_main_server=upsert_to_main_server)


                        """MARKET HOURS"""

                        if not app_req:
                            if stop_queen_order_from_kingbishop(run_order): # false, order_trig_sell_stop or qty_avilable
                                continue

                        if not crypto and mkhrs != 'open':
                            # print(f"{symbol} QUEEN ORDER MARKET HOURS CLOSED")
                            continue

                        ## subconsicous here ###
                        ro_ttf = run_order['ticker_time_frame']
                        if run_order['ticker_time_frame'] not in STORY_bee.keys():
                            # Handle Order if Ticker Stream Turned off I.E. Not in STORY_bee
                            logging.info(f"{ro_ttf} Missing from STORY_bee")

                        king_eval_order = king_bishops_QueenOrder(QUEEN_KING=QUEEN_KING, STORY_bee=STORY_bee, run_order=run_order, priceinfo=priceinfo, revrec=QUEEN['revrec'])
                        
                        if king_eval_order['bee_sell']:
                            exx = execute_sell_order(
                                    broker=broker,
                                    prod=QUEEN['prod'],
                                    api=api, 
                                    QUEEN=QUEEN,
                                    king_eval_order=king_eval_order,
                                    ticker=king_eval_order['bishop_keys']['ticker'], 
                                    ticker_time_frame=king_eval_order['bishop_keys'].get('ticker_time_frame'),
                                    trig=king_eval_order['bishop_keys']['trigname'], 
                                    run_order_idx=king_eval_order['bishop_keys']['client_order_id'], 
                                    order_type=king_eval_order['bishop_keys']['order_type'],
                                    crypto=king_eval_order['bishop_keys']['qo_crypto'],
                                )
                            if exx.get('executed'):
                                save = True
                                new_queen_order_df = pd.DataFrame([exx['new_queen_order']]).set_index("client_order_id", drop=False)
                                append_queen_order(QUEEN, new_queen_order_df)
                                queen_order_idx = new_queen_order_df.index[0]

                                QUEEN = refresh_broker_account_portolfio(api, QUEEN) #heartbeat
                                
                                # IMMEDIATE UPDATE QUEEN ORDER STATUS
                                order_status = check_order_status(broker=broker, api=api, client_order_id=queen_order_idx)
                                run_order_closed = QUEEN['queen_orders'].loc[queen_order_idx].to_dict()
                                run_order_closed, save_order = route_queen_order(QUEEN=QUEEN, 
                                                            queen_order=run_order_closed, 
                                                            queen_order_idx=queen_order_idx, 
                                                            order_status=order_status, 
                                                            priceinfo=priceinfo,
                                                            save_order=True,
                                                            )

                                """ Hold ORDER from being SOLD again until Release Validation """
                                origin_order_idx = new_queen_order_df.at[queen_order_idx, 'exit_order_link']
                                run_order = QUEEN['queen_orders'].loc[origin_order_idx].to_dict() # shouldn't be necessary since we haven't redefined but doing this as a safe check
                                QUEEN['queen_orders'].at[origin_order_idx, 'order_trig_sell_stop'] = True
                                update_origin_order_qty_available(QUEEN=QUEEN, 
                                                                  run_order_idx=origin_order_idx, 
                                                                  RUNNING_CLOSE_Orders=RUNNING_CLOSE_Orders, RUNNING_Orders=RUNNING_Orders, 
                                                                  save=True)
                                update_origin_order_cost_basis_current(QUEEN=QUEEN, 
                                                                       queen_order_idx=origin_order_idx, 
                                                                       priceinfo=priceinfo,
                                                                       instance=4)
                                if float(run_order.get('qty_available')) > 0 and run_order.get('order_trig_sell_stop') == True:
                                    if release_trig_sell_stop(QUEEN=QUEEN, ticker=symbol, client_order_id=origin_order_idx):
                                        print("RELEASE TRIG SELL STOP", symbol, origin_order_idx)
                                        save_queen_order(QUEEN, prod=QUEEN['prod'], client_order_id=origin_order_idx, upsert_to_main_server=upsert_to_main_server)

                                QUEEN['revrec'] = refresh_chess_board__revrec(QUEEN['account_info'], QUEEN, QUEEN_KING, STORY_bee) ## Setup Board

                        elif king_eval_order.get('save_order'):
                            save_queen_order(QUEEN, prod=QUEEN['prod'], client_order_id=idx, upsert_to_main_server=upsert_to_main_server)
                            QUEEN['revrec'] = refresh_chess_board__revrec(QUEEN['account_info'], QUEEN, QUEEN_KING, STORY_bee) ## Setup Board



                    except Exception as e:
                        print_line_of_error(f'ORDER FAILED {e}')
                        send_email(subject="Order Failed", body=str(e))
                        time.sleep(33)


                if save_revrec:
                    QUEEN['revrec'] = refresh_chess_board__revrec(QUEEN['account_info'], QUEEN, QUEEN_KING, STORY_bee) ## Setup Board

                if save_broker_order:
                    if pg_migration:
                        PollenDatabase.upsert_data(BROKER.get('table_name'), BROKER.get('key'), BROKER, main_server=server)
                    else:
                        PickleData(BROKER.get('source'), BROKER, console=False)

                if save: # this is for executed Orders ONLY, maybe this can be deprecated ? #WORKERBEE
                    god_save_the_queen(QUEENsHeart=QUEENsHeart, QUEEN=QUEEN, charlie_bee=charlie_bee,
                                    save_q=True,
                                    save_rr=True,
                                    save_qo=True,
                                    console=True,
                                    upsert_to_main_server=upsert_to_main_server)
                charlie_bee['queen_cyle_times']['om_loop_queen_orders__om'] = (datetime.now(est) - s_time).total_seconds()

                if len(queen_orders__dict) > 0 :
                    pass
                else:
                    return False

                charlie_bee['queen_cyle_times']['full_loop_queenorderS__om'] = (datetime.now(est) - s_loop).total_seconds()
                
                return True
            
            except Exception as e:
                print_line_of_error(f"QUEEN ORDERS MAIN ERROR {e}")
                return False


        #### MAIN ####
        # >for every ticker position join in running-positions to account for total position
        # >for each running position determine to exit the position   

        process_app_requests__order_updates(QUEEN=QUEEN, QUEEN_KING=QUEEN_KING, upsert_to_main_server=upsert_to_main_server)

        try:
            # Submitted Orders First
            s_loop = datetime.now(est)
            queen_orders_main(BROKER, QUEEN, STORY_bee, QUEEN_KING, charlie_bee, mkhrs=mkhrs)
            charlie_bee['queen_cyle_times']['om_queen_orders___main'] = (datetime.now(est) - s_loop).total_seconds()
        
        except Exception as e:
            print_line_of_error()
            raise e
        return True


    def refresh_QUEEN_starTickers(QUEEN, STORY_bee, ticker_allowed, story_heartrate=172800):
        try:

            now_time = datetime.now(est)

            original_state = QUEEN['heartbeat']['available_tickers']
            avail_tics = []
            tics_missing = []
            for i, v in STORY_bee.items():
                time_delta = (now_time - v['story']['time_state']).total_seconds()
                if time_delta < story_heartrate:
                    avail_tics.append(i)
                else:
                    # print(i, "time delta", time_delta)
                    ticker, ttime, tframe = i.split("_")
                    if ticker not in tics_missing:
                        # print(f'ticker missing {ticker} time delta story {time_delta} seconds')
                        tics_missing.append(ticker)
            
            # if tics_missing:
            #     print("Missing Tickers in STORYBEE", tics_missing)
        
            QUEEN['heartbeat']['available_tickers'] = avail_tics #[i for (i, v) in STORY_bee.items() if (now_time - v['story']['time_state']).total_seconds() < story_heartrate]
            ticker_set = set([i.split("_")[0] for i in QUEEN['heartbeat']['available_tickers']])

            QUEEN['heartbeat']['active_tickers'] = [i for i in ticker_set if i in ticker_allowed]
            # current_wave = star_ticker_WaveAnalysis(STORY_bee=STORY_bee, ticker_time_frame='SPY_1Minute_1Day').get('current_wave')
            # QUEEN['heartbeat']['current_wave'] = current_wave ## REMOVE?
            
            for old_item in ['added_list', 'active_tickerStars', 'dropped_list']:
                if old_item in QUEEN['heartbeat'].keys():
                    print('clean heart')
                    QUEEN['heartbeat'].pop(old_item)

            return QUEEN
        except Exception as e:
            print_line_of_error(e)
    
    
        
    ### Close the Day ###

    def close_day__queen(QUEEN, BROKER, ORDERS_FINAL=False): # clean all FINAL orders bucket 
        def archive_queen(QUEEN):
            # archive_queen_copy
            if pg_migration:
                PollenDatabase.upsert_data(QUEEN.get('table_name'), key=f'previousDAY_{QUEEN.get("key")}', value=QUEEN, main_server=server)
                return True
            else:
                root, name = os.path.split(QUEEN.get('source'))
                archive_ = os.path.join(root, f'{"previousDAY"}__{name}')
                PickleData(archive_, QUEEN, console=True)
        
        # Save Copy of Current day Queen
        # archive_queen(QUEEN)
        if not pg_migration:
            ORDERS_FINAL = init_queenbee(client_user=client_user, prod=prod, orders_final=True, main_server=server).get('ORDERS_FINAL')
        
        ## Clean ORders WORKERBE
        def archive_order(QUEEN, ORDERS_FINAL=ORDERS_FINAL):
            try:
                db_root = QUEEN.get('db_root')
                now_time_hash = hash_string(datetime.now(est).strftime("%y-%m-%d %M.%S.%f"))
                final_batch_name = f'{db_root}_{now_time_hash}_final_orders' 
                
                queen_orders = copy.deepcopy(QUEEN['queen_orders'])
                ARCHIVE_queenorder = kingdom__global_vars().get('ARCHIVE_queenorder') # ['final', 'archived']
                final_orders = queen_orders[queen_orders['queen_order_state'].isin(ARCHIVE_queenorder)].copy()
                if len(final_orders) > 0:
                    dump_final_orders = []
                    
                    for final_origin_order in final_orders.index:
                        dump_final_orders.append(final_origin_order)

                    if dump_final_orders:  
                        linked_orders = return_multiple_closing_orders(queen_orders, dump_final_orders)
                        if len(linked_orders) > 0:
                            for order_idx in linked_orders.index:
                                dump_final_orders.append(order_idx)

                        msg=(f"Removing Final/Completed Orders from QUEEN {dump_final_orders}")
                        print(msg)
                        logging.info(msg)

                        # archived orders
                        dump_orders = queen_orders[queen_orders.index.isin(dump_final_orders)].copy()
                        
                        # refreshed Queen Orders
                        qo_new = queen_orders[~queen_orders.index.isin(dump_final_orders)].copy()
                        QUEEN['queen_orders'] = qo_new
                        
                        if pg_migration:
                            PollenDatabase.upsert_data(table_name='final_orders', key=final_batch_name, value=dump_orders, main_server=server)
                        
                        if ORDERS_FINAL:
                            qo_final = copy.deepcopy(ORDERS_FINAL['queen_orders'])
                            qo_final = pd.concat([qo_final, dump_orders])
                            ORDERS_FINAL['queen_orders'] = qo_final

                        return True
    
            except Exception as e:
                print(e)
                return False

        if archive_order(QUEEN, ORDERS_FINAL):
            if pg_migration:
                pass
            else:
                PickleData(ORDERS_FINAL.get('source'), ORDERS_FINAL)
        

        # reduce Broker Orders to QUEENs
        broker_orders = BROKER['broker_orders']
        broker_orders = broker_orders[broker_orders['client_order_id'].isin(QUEEN['queen_orders']['client_order_id'])].copy()
        BROKER['broker_orders'] = broker_orders # remove all QUEEN orders from broker orders
        if pg_migration:
            PollenDatabase.upsert_data(BROKER.get('table_name'), key=BROKER.get('key'), value=BROKER, main_server=server)
        else:
            PickleData(BROKER.get('source'), BROKER)

        return True    

    ################################################################# pollen
    #################################################################
    ################################################################# 
    #################################################################
    ######################QUEENBEE###################################
    #################################################################
    ################################################################# 
    #################################################################
    ################################################################# pollen


    # if '__name__' == '__main__':
    try:
        # s_time = datetime.now().astimezone(est)

        db_root = init_clientUser_dbroot(client_username=client_user)

        print(
        """
        pollenq:
        We all shall prosper through the depths of our connected hearts,
        Not all will share my world,
        So I put forth my best mind of virtue and goodness, 
        Always Bee Better
        """, timestamp_string()
        )
        if loglevel == 'info':
            print("Logging Level: INFO CONSOLE ONLY")
            console_only = True
        else:
            console_only = False
        init_logging(queens_chess_piece=queens_chess_piece, db_root=db_root, prod=prod, loglevel=loglevel, console_only=console_only)

        # init files needed
        qb = init_queenbee(client_user, prod, queen=True, orders=False, orders_v2=True, queen_king=True, api=True, broker=True, init=True, pg_migration=pg_migration, main_server=server)
        QUEEN = qb.get('QUEEN')
        QUEEN['prod'] = prod
        QUEEN_KING = qb.get('QUEEN_KING')
        api = qb.get('api')
        QUEENsHeart = qb.get('QUEENsHeart')
        BROKER = qb.get('BROKER')


        ## """Rev Rec"""
        if 'chess_board__revrec' not in QUEEN_KING.keys():
            print("QUEEN Not Enabled ChessBoard")
            logging.error((" queen not auth "))
            send_email(subject=f'{client_user} running queen without Board', body=f'{client_user} running queen without Board')
            sys.exit()

        if api == False:
            print("API Keys Failed, Queen goes back to Sleep")
            QUEEN['queens_messages'].update({"api_status": 'failed'})
            if pg_migration:
                PollenDatabase.upsert_data(QUEEN.get('table_name'), key=QUEEN.get('key'), value=QUEEN, main_server=server)
            else:
                PickleData(QUEEN['dbs'].get('PB_QUEEN_Pickle'), QUEEN)
            sys.exit()

        trading_days = hive_dates(api=api)['trading_days']
        
        save_b, BROKER, QUEEN = reconcile_broker_orders_with_queen_orders(BROKER, api, QUEEN, active_queen_order_states)
        if save_b:
            if pg_migration:
                PollenDatabase.upsert_data(BROKER.get('table_name'), key=BROKER.get('key'), value=BROKER, main_server=server)
            else:
                PickleData(BROKER.get('source'), BROKER, console=False)

        if pg_migration:
            symbols = return_QUEEN_KING_symbols(QUEEN_KING, QUEEN)
            STORY_bee = PollenDatabase.retrieve_all_story_bee_data(symbols, server=server_storybee).get('STORY_bee') # WORKERBEE let server call?
            # Ticker database of pollenstory ## Need to seperate out into tables 
        else:
            STORY_bee = return_QUEENs__symbols_data(QUEEN=QUEEN, QUEEN_KING=QUEEN_KING, read_storybee=True, read_pollenstory=False).get('STORY_bee') ## async'd func

        # add new keys
        QUEEN_req = add_key_to_QUEEN(QUEEN=QUEEN, queens_chess_piece=queens_chess_piece)
        if QUEEN_req['update']:
            QUEEN = QUEEN_req['QUEEN']
            if pg_migration:
                PollenDatabase.upsert_data(QUEEN.get('table_name'), key=QUEEN.get('key'), value=QUEEN, main_server=server)
            else:
                PickleData(QUEEN['dbs'].get('PB_QUEEN_Pickle'), QUEEN)
        
        print("My Queen")

        QUEEN['heartbeat']['main_indexes'] = main_index_tickers()
        QUEEN['heartbeat']['active_order_state_list'] = active_order_state_list
        
        ticker_allowed = list(KING['alpaca_symbols_dict'].keys())
        QUEEN = refresh_QUEEN_starTickers(QUEEN, STORY_bee, ticker_allowed)

        available_triggerbees = ["sell_cross-0", "buy_cross-0"]
        QUEEN['heartbeat']['available_triggerbees'] = available_triggerbees

        # if 'price_info_symbols' not in QUEEN.keys():
        QUEEN['price_info_symbols'] = queenbee_get_priceinfo(QUEEN, active_queen_order_states)

        print(f'ProdEnv {prod} Here we go Mario')

        # handle App updates
        process_app_requests__order_updates(QUEEN=QUEEN, QUEEN_KING=QUEEN_KING, upsert_to_main_server=upsert_to_main_server)
        
        if pg_migration:
            charlie_bee = qb.get('CHARLIE_BEE')
            queens_charlie_bee, charlie_bee = init_charlie_bee(db_root, pg_migration=pg_migration, charlie_bee=charlie_bee)
        else:
            queens_charlie_bee, charlie_bee = init_charlie_bee(db_root) # monitors queen order cycles, also seen in heart
        charlie_bee['queen_cycle_count'] = 0
        
        # WORKERBEE UPDATE WITH KEYS BY USER !! NOT ALL KEYS
        db_keys_df = (pd.DataFrame(PollenDatabase.get_all_keys_with_timestamps(table_name, server=server))).rename(columns={0:'key', 1:'timestamp'})
        db_keys_df['key_name'] = db_keys_df['key'].apply(lambda x: x.split("-")[-1])
        db_keys_df = db_keys_df.set_index('key_name')
        pq_qk_lastmod = db_keys_df.at['QUEEN_KING', 'timestamp']

        ########################################################
        ########################################################
        #############The Infinite Loop of Time #################
        ########################################################
        ########################################################
        ########################################################
        heartbeat_cyle = deque([], 3000)
        cycle_time = datetime.now(est)
        while True:
            s = datetime.now(est)
            mkhrs = return_market_hours(trading_days=trading_days)
            # seconds_to_market_close = (datetime.now(est).replace(hour=16, minute=0, second=0) - datetime.now(est)).total_seconds()

            db_keys_df = (pd.DataFrame(PollenDatabase.get_all_keys_with_timestamps(table_name, server=server))).rename(columns={0:'key', 1:'timestamp'})
            db_keys_df['key_name'] = db_keys_df['key'].apply(lambda x: x.split("-")[-1])
            db_keys_df = db_keys_df.set_index('key_name')
            """ The Story of every Knight and their Quest """
            s = datetime.now(est)
            # refresh db
            s_time = datetime.now(est)
            if pg_migration:
                qk_lastmod = db_keys_df.at['QUEEN_KING', 'timestamp']
                if str(qk_lastmod) != str(pq_qk_lastmod):
                    # send_revrec_update = True
                    pq_qk_lastmod = qk_lastmod
                    print("PGM: QUEENKING Updated Read New Data")
                    QUEEN_KING = init_queenbee(client_user=client_user, prod=prod, queen_king=True, pg_migration=pg_migration, main_server=server).get('QUEEN_KING')
                    QUEEN['chess_board'] = QUEEN_KING['chess_board']
            else:
                if str(os.stat(QUEEN['dbs'].get('PB_App_Pickle')).st_mtime) != QUEEN_KING['last_modified']:
                    print("QUEENKING Updated Read New Data")
                    QUEEN_KING = init_queenbee(client_user=client_user, prod=prod, queen_king=True, main_server=server).get('QUEEN_KING')
                    QUEEN['chess_board'] = QUEEN_KING['chess_board']

            # symbol ticker data >>> 1 all current pieces on chess board && all current running orders
            if pg_migration:
                symbols = return_QUEEN_KING_symbols(QUEEN_KING, QUEEN)
                STORY_bee = PollenDatabase.retrieve_all_story_bee_data(symbols, server=server_storybee).get('STORY_bee')
                # Ticker database of pollenstory ## Need to seperate out into tables 
            else:
                STORY_bee = return_QUEENs__symbols_data(QUEEN=QUEEN, QUEEN_KING=QUEEN_KING, read_storybee=True, read_pollenstory=False).get('STORY_bee') ## async'd func

            QUEEN = refresh_QUEEN_starTickers(QUEEN=QUEEN, STORY_bee=STORY_bee, ticker_allowed=ticker_allowed)
            charlie_bee['queen_cyle_times']['db_refresh'] = (datetime.now(est) - s_time).total_seconds()

            """Account Info"""
            QUEEN = refresh_broker_account_portolfio(api, QUEEN)
            acct_info = QUEEN['account_info']
            # portfolio = QUEEN['portfolio']

            # Save Account WORKERBEE unessecary SAVING only save whats needed ! Handle via conscience_utils / websockets
            god_save_the_queen(QUEEN, save_acct=True, console=False, upsert_to_main_server=upsert_to_main_server)

            charlie_bee['queen_cyle_times']['cc_block1_account'] = (datetime.now(est) - s_time).total_seconds()

            # Read client App Reqquests
            s_time = datetime.now(est)
            req = process_app_requests(QUEEN=QUEEN, QUEEN_KING=QUEEN_KING, request_name='queen_sleep')
            if req.get('app_flag'):
                print("APP: Queen Sleeps SAVE")
                god_save_the_queen(QUEEN, save_q=True, upsert_to_main_server=upsert_to_main_server)
            # process_app_requests(QUEEN=QUEEN, QUEEN_KING=QUEEN_KING, request_name='subconscious')
            charlie_bee['queen_cyle_times']['app'] = (datetime.now(est) - s_time).total_seconds()

            ############ PRICE INFO SYMBOLS ###########
            QUEEN['price_info_symbols'] = queenbee_get_priceinfo(QUEEN, active_queen_order_states)
            
            ############# Refresh Board ############
            QUEEN['revrec'] = refresh_chess_board__revrec(acct_info, QUEEN, QUEEN_KING, STORY_bee, wash_sale_rule=wash_sale_rule) ## Setup Board

            charlie_bee['queen_cyle_times']['cc_revrec'] = QUEEN['revrec'].get('cycle_time')

            # # # Save Revrec WORKERBEE unessecary SAVING only save whats needed ! Handle via conscience_utils / websockets SO need to refresh REVREC in API on first load
            # god_save_the_queen(QUEEN, save_rr=True, console=True, upsert_to_main_server=upsert_to_main_server) # WORKERBEE unessecary SAVING only save whats needed

            # WORKERBEE ONLY SEND NECESSARY DATA (Priceinfo, total budget, remaining balance...????)
            if check_user_websocket_status(client_user, prod, API_URL=API_URL, upsert_to_main_server=upsert_to_main_server):
                story_grid_update(prod, QUEEN_KING, QUEEN['revrec'], client_user, API_KEY=API_KEY, API_URL=API_URL, upsert_to_main_server=upsert_to_main_server)

            # Process All Orders
            s_time = datetime.now(est)
            # print("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<ORDER MANAGEMENT>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
            order_management(BROKER, STORY_bee, QUEEN, QUEEN_KING, api, QUEENsHeart, charlie_bee, mkhrs)
            charlie_bee['queen_cyle_times']['order management'] = (datetime.now(est) - s_time).total_seconds()

            s_time = datetime.now(est)
            # print("<<<<<<<<<<<<<<<<<<<<<<<COMMAND CONSCIENCE>>>>>>>>>>>>>>>>>>>>>>>>>>")
            command_conscience(QUEEN, STORY_bee, QUEEN_KING, api, mkhrs) ##### >   
            charlie_bee['queen_cyle_times']['command conscience'] = (datetime.now(est) - s_time).total_seconds()
            
            beat = (datetime.now(est) - s).total_seconds()

            # print_queen_cycle_times(charlie_bee)
            # if pg_migration:
            #     PollenDatabase.upsert_data(table_name, key=charlie_bee.get('key'), value=charlie_bee)
            # else:
            #     PickleData(queens_charlie_bee, charlie_bee, console=False)
            heartbeat_cyle.append(beat)
            
            charlie_bee['queen_cycle_count'] += 1
            if datetime.now(est) - cycle_time > timedelta(seconds=60) or charlie_bee['queen_cycle_count'] == 1:
                cycle_time = datetime.now(est)
                print("HeartBeat", beat, datetime.now(est).strftime('%y-%m-%d:%H:%M'))
                avg_beat = sum(heartbeat_cyle) / len(heartbeat_cyle)
                QUEENsHeart.update({"heartbeat_beat": round(beat)})
                QUEENsHeart.update({"heartbeat_avg_beat": round(avg_beat)})
                god_save_the_queen(QUEEN, QUEENsHeart, console=True, upsert_to_main_server=upsert_to_main_server)
                # god_save_the_queen(QUEEN, save_rr=True, console=True, upsert_to_main_server=upsert_to_main_server) # WORKERBEE unessecary SAVING only save whats needed

            
            if beat > 23:
                logging.warning((queens_chess_piece, ": SLOW cycle Heart Beat: ", beat, "use price gauge"))

            # Should you operate now? I thnik the brain never sleeps ?
            if 'crypto' not in queens_chess_piece:
                if datetime.now(est) > datetime.now(est).replace(hour=16, minute=00):
                    # close_day__queen(QUEEN, BROKER) # cleaning orders to confirm WORKERBEE            
                    god_save_the_queen(QUEENsHeart=QUEENsHeart, QUEEN=QUEEN, charlie_bee=charlie_bee,
                                    save_q=True,
                                    save_rr=True,
                                    save_qo=True,
                                    save_acct=True,
                                    console=True,
                                    upsert_to_main_server=upsert_to_main_server)
                    # hanlde_missing_broker_orders_with_queen_orders(BROKER, QUEEN)
                    print("Queen to ZzzzZZzzzZzzz see you tomorrow")
                    sys.exit()
            if datetime.now(est) > datetime.now(est).replace(hour=22, minute=30):
                print("Everyone Needs to Sleep")
                sys.exit()

    except Exception as errbuz:
        print("eeerbuz", errbuz)
        er, erline = print_line_of_error()
        log_msg = {'type': 'ProgramCrash', 'errbuz': errbuz, 'er': er, 'lineerror': erline}
        print(log_msg)
        logging.critical(log_msg)
        send_email(subject="queen crashed", body=log_msg)
    
    #### >>>>>>>>>>>>>>>>>>> END <<<<<<<<<<<<<<<<<<###


if __name__ == '__main__':
    # read
    def createParser():
        parser = argparse.ArgumentParser()
        parser.add_argument ('-prod', default='true')
        parser.add_argument ('-crypto', default='false')
        parser.add_argument ('-client_user', default=os.environ.get('admin_user'))
        parser.add_argument ('-loglevel', default='warning')
        return parser
    
    parser = createParser()
    namespace = parser.parse_args()
    client_user = namespace.client_user
    prod = namespace.prod
    prod = True if str(prod).lower() == 'true' else False
    crypto = 'crypto' if str(namespace.crypto).lower() == 'true' else ''
    loglevel = namespace.loglevel

        
    queenbee(client_user, prod, queens_chess_piece=f'queen{crypto}', server=server, loglevel=loglevel)

"""
The Journey is Hard,
Believe in you,
Believe in God,
Believe
"""
