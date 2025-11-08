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
import ipdb
import asyncio
import aiohttp
from collections import defaultdict, deque
import argparse
import ast ## WORKERBEE TEMP FIX UNTIL LATER FIX PRICEINFO STORAGE
from decimal import Decimal, ROUND_DOWN


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from chess_piece.king import main_index_tickers, hash_string, kingdom__global_vars, print_line_of_error, return_QUEENs__symbols_data, PickleData, return_QUEEN_KING_symbols, return_crypto_snapshots
from chess_piece.queen_hive import (kingdom__grace_to_find_a_Queen,
                                    init_charlie_bee, 
                                    init_queenbee, 
                                    power_amo, 
                                    return_queenking_board_symbols,
                                    broker_orders_fields, 
                                    star_refresh_star_seconds, 
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
                                    logging_log_message, 
                                    return_market_hours, 
                                    check_order_status,  
                                    timestamp_string, 
                                    submit_order, 
                                    add_key_to_QUEEN, 
                                    update_sell_date,
                                    return_Ticker_Universe,
                                    refresh_broker_account_portolfio,
                                    create_TrigRule,
                                    )
from chess_piece.queen_mind import refresh_chess_board__revrec, weight_team_keys, kings_order_rules
from chess_piece.pollen_db import PollenDatabase, PollenJsonEncoder, PollenJsonDecoder
from chess_utils.robinhood_crypto_utils import CryptoAPITrading

import copy
from tqdm import tqdm

import os, psutil
print("Memory usage (MB):", psutil.Process(os.getpid()).memory_info().rss / 1024 ** 2)

def print_object_memory(label, obj):
    if isinstance(obj, pd.DataFrame):
        print(f"{label} DataFrame mem (MB):", obj.memory_usage(deep=True).sum() / 1024 ** 2)
    elif isinstance(obj, dict):
        total = sys.getsizeof(obj)
        for k, v in obj.items():
            if isinstance(v, pd.DataFrame):
                total += v.memory_usage(deep=True).sum()
            elif isinstance(v, dict):
                total += sys.getsizeof(v)
            elif isinstance(v, list):
                total += sys.getsizeof(v)
            else:
                try:
                    total += sys.getsizeof(v)
                except:
                    pass
        print(f"{label} dict mem (approx MB):", total / 1024 ** 2)
    else:
        print(f"{label} object mem (MB):", sys.getsizeof(obj) / 1024 ** 2)


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

wash_sale_rule = []

# crypto
crypto_currency_symbols = ['BTCUSD', 'ETHUSD', 'BTC/USD', 'ETH/USD']
def symbol_is_crypto(symbol, crypto_currency_symbols=crypto_currency_symbols):
    if symbol in crypto_currency_symbols:
        return True
    else:
        return False

coin_exchange = "CBSE"
ACTIVE_SYMBOLS = list(return_Ticker_Universe().get('alpaca_symbols_dict')) + crypto_currency_symbols
# misc
exclude_conditions = [
    'B','W','4','7','9','C','G','H','I','M','N',
    'P','Q','R','T','V','Z'
] # 'U'


def init_broker_orders(api, BROKER, start_date=None, end_date=None):
    # Start and end dates for the last 100 days
    if not start_date:
        end_date = datetime.now() + timedelta(days=1)
        start_date = datetime.now() - timedelta(days=100)

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
        df_token = pd.DataFrame([order_status]).set_index('client_order_id', drop=False)
        if df_token.index[0] in broker_orders.index:
            broker_orders = broker_orders[broker_orders['client_order_id'] != df_token.index[0]]
        
        broker_orders = pd.concat([broker_orders, df_token])
        BROKER['broker_orders'] = broker_orders
        
        return True
    except Exception as e:
        print_line_of_error("broker update failed")
        return False


def generate_client_order_id(ticker, trig, sellside_client_order_id=False): # generate using main_order table and trig count

    temp_date = datetime.now(est).strftime("%y-%m-%d %M.%S.%f")
    order_string = f'{ticker}-{trig}-{temp_date}'
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
        print("START of submit order validation  crypto: ", crypto, ticker, qty, side)
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
                print("ERROR Price OR Ask is 0 Ignore: ", ticker)
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


def execute_buy_order(broker, order_key, prod, api, blessing, ticker, ticker_time_frame, trig, wave_amo, order_type='market', side='buy', crypto=False, limit_price=False, portfolio=None, trading_model=False, ACTIVE_SYMBOLS=ACTIVE_SYMBOLS):
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
        client_order_id__gen = generate_client_order_id(ticker=ticker, trig=trig)
        
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
        print("SUBMIT ORDER", client_order_id__gen, order.get('client_order_id'))

        if 'borrowed_funds' not in order_vars.keys():
            order_vars['borrowed_funds'] = False
        order_vars['qty_order'] = qty_order
        
        new_queen_order_df = process_order_submission(
            order_key=order_key,
            prod=prod,
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

        return {'executed': True, 'msg': msg, 'new_queen_order_df': new_queen_order_df, 'priceinfo_order': priceinfo_order}

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
        client_order_id__gen = generate_client_order_id(ticker=ticker, trig=trig, sellside_client_order_id=run_order_client_order_id)
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
        new_queen_order_df = process_order_submission(
            order_key=QUEEN['db_root'],
            prod=prod,
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

        return{'executed': True, 'msg': msg, 'new_queen_order_df': new_queen_order_df, 'priceinfo_order': priceinfo_order}

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


def update_origin_order_cost_basis_current(QUEEN, queen_order_idx):
    av_qty = float(QUEEN['queen_orders'].at[queen_order_idx, 'qty_available'])
    avg_price_fill = float(QUEEN['queen_orders'].at[queen_order_idx, 'filled_avg_price'])          
    if av_qty > 0:
        QUEEN['queen_orders'].at[queen_order_idx, 'cost_basis_current'] = av_qty * avg_price_fill
    
    return QUEEN['queen_orders'].loc[queen_order_idx].to_dict()

def update_latest_queen_order_status(QUEEN, order_status, queen_order_idx): # updates qty and cost basis from Alpaca
    # WORKERBEE fix what if any columns neseccary to bring in? Maybe use run_order columns from createQueenBeeOrder? & handle Robinhood/others?
   
    for order_key, order_value in order_status.items():
        QUEEN['queen_orders'].at[queen_order_idx, order_key] = order_value
        # if order_key in broker_cols:

    if order_status['filled_qty'] is not None:
        QUEEN['queen_orders'].at[queen_order_idx, 'filled_qty'] = float(order_status['filled_qty'])
    if order_status['filled_avg_price'] is not None:
        QUEEN['queen_orders'].at[queen_order_idx, 'filled_avg_price'] = float(order_status['filled_avg_price'])
        QUEEN['queen_orders'].at[queen_order_idx, 'cost_basis'] = float(order_status['filled_qty']) * float(order_status['filled_avg_price'])
        update_origin_order_cost_basis_current(QUEEN, queen_order_idx)

    return QUEEN['queen_orders'].loc[queen_order_idx].to_dict()


def check_origin_order_status(QUEEN, origin_order, origin_idx, closing_filled):
    if float(origin_order["filled_qty"]) == closing_filled: 
        print("# running order has been fully sold out and now we can archive", origin_idx)
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
        current_price = priceinfo['current_price']
        current_ask = priceinfo['current_ask']
        current_bid = priceinfo['current_bid']
        
        # priceinfo = {'price': current_price, 'bid': current_bid, 'ask': current_ask}
        order_price = float(queen_order['filled_avg_price'])
        if order_price > 0:
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
            # if 'honey_gauge' in queen_order.keys():
            #     QUEEN['queen_orders'].at[queen_order_idx, 'honey_gauge'].append(current_profit_loss)
        else:
            current_profit_loss = 0
            QUEEN['queen_orders'].at[queen_order_idx, 'honey'] = 0
            QUEEN['queen_orders'].at[queen_order_idx, 'money'] = 0
            QUEEN['queen_orders'].at[queen_order_idx, 'current_ask'] = current_ask
            QUEEN['queen_orders'].at[queen_order_idx, 'current_bid'] = current_bid
        
        return {'current_profit_loss': current_profit_loss}
    except Exception as e:
        print(ticker, " pl error", e, print_line_of_error())


def god_save_the_queen(QUEEN, QUEENsHeart=False, charlie_bee=False, save_q=False, save_acct=False, save_rr=False, save_qo=False, active_queen_order_states=active_queen_order_states, console=False, upsert_to_main_server=upsert_to_main_server):
    
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




def queenbee(client_user, prod, queens_chess_piece='queen', server=server, loglevel='info'):
    table_name = 'client_user_store' if prod else 'client_user_store_sandbox'
    if client_user in ['stapinskistefan@gmail.com'] and not prod: #'stefanstapinski@gmail.com', 
        print("TESTING LOCAL SANDBOX SAVE DATA TO SERVER")
        upsert_to_main_server = True
        server = True
    else:
        upsert_to_main_server = False

    def save_queen_order(QUEEN, prod, client_order_id, upsert_to_main_server=upsert_to_main_server):
        try:
            # logging.info(f"saving queen order: {client_order_id} server={upsert_to_main_server}")
            table_name = 'queen_orders' if prod else 'queen_orders_sandbox'
            key = f"{QUEEN['db_root']}___{client_order_id}"
            PollenDatabase.upsert_data(table_name=table_name, key=key, value=QUEEN['queen_orders'].loc[client_order_id].to_dict(), console=True, main_server=upsert_to_main_server)
            return True  
        except Exception as e:
            logging.error(f"Error saving queen order: {e}")
            return False

    def route_queen_order(QUEEN, queen_order, queen_order_idx, order_status, priceinfo, save_order=False):

        def alpaca_queen_order_state(QUEEN, order_status, queen_order, queen_order_idx, priceinfo):
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
                        if QUEEN['queen_orders'].at[queen_order_idx, 'queen_order_state'] in CLOSED_queenorders:
                            print("but why? THIS SHOULD NOT HAPPEN")
                            send_email(recipient='stapinski89@gmail.com', subject="Order Index Failed", body=f'{queen_order_idx} order index failed')
                            QUEEN['queen_orders'].at[queen_order_idx, 'queen_order_state'] = 'completed'
                            
                            #### CHECK to see if Origin ORDER has Completed LifeCycle ###
                            origin_order = return_origin_order(df_queenorders=QUEEN['queen_orders'], exit_order_link=queen_order['exit_order_link'])
                            if len(origin_order) > 0:
                                origin_order_idx = origin_order['origin_idx']
                                origin_order = origin_order['origin_order']
                                # Check to complete Queen Order 
                                origin_closed = check_origin_order_status(QUEEN=QUEEN, origin_order=origin_order, origin_idx=origin_order_idx, closing_filled=closing_filled)
                                if origin_closed:
                                    print("but why? >> Sell Order Fuly Filled: Honey>> ", profit_loss_value, " :: ", profit_loss)
                                    QUEEN['queen_orders'].at[queen_order_idx, 'queen_order_state'] = 'completed'
                        else:
                            QUEEN['queen_orders'].at[queen_order_idx, 'queen_order_state'] = "running"
                            update_latest_queen_order_status(QUEEN=QUEEN, order_status=order_status, queen_order_idx=queen_order_idx)
                            update_origin_order_qty_available(QUEEN=QUEEN, run_order_idx=queen_order_idx, RUNNING_CLOSE_Orders=RUNNING_CLOSE_Orders, RUNNING_Orders=RUNNING_Orders)
                            update_queen_order_profits(QUEEN=QUEEN, ticker=queen_order.get('ticker'), queen_order=queen_order, queen_order_idx=queen_order_idx, priceinfo=priceinfo)
                            QUEEN['queen_orders'].at[queen_order_idx, 'status_q'] = "filled"
                    
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
                            update_origin_order_cost_basis_current(QUEEN=QUEEN, queen_order_idx=origin_order_idx)
                            check_origin_order_status(QUEEN=QUEEN, origin_order=origin_order, origin_idx=origin_order_idx, closing_filled=closing_filled)
                        
                elif alp_order_status in partially_filled:            
                    if order_status['side'] == 'buy':
                        QUEEN['queen_orders'].at[queen_order_idx, 'queen_order_state'] = "running_open"

                        update_latest_queen_order_status(QUEEN=QUEEN, order_status=order_status, queen_order_idx=queen_order_idx)
                        update_queen_order_profits(QUEEN=QUEEN, ticker=queen_order.get('ticker'), queen_order=queen_order, queen_order_idx=queen_order_idx, priceinfo=priceinfo)
                        update_origin_order_qty_available(QUEEN=QUEEN, run_order_idx=queen_order_idx, RUNNING_CLOSE_Orders=RUNNING_CLOSE_Orders, RUNNING_Orders=RUNNING_Orders)

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
                            update_origin_order_cost_basis_current(QUEEN=QUEEN, queen_order_idx=origin_order_idx)

                    else:
                        print("Critical Error New Order Side")
                        logging_log_message(log_type='error', msg='Critical Error New Order Side')
                else:
                    print("critical errror new order type received")
                    logging.error(f"WTF Route me {queen_order_idx}")
            
                
                return queen_order_idx, origin_order_idx

            except Exception as e:
                print('queen router failed', e, print_line_of_error())
        

        queen_order_idx, origin_order_idx = alpaca_queen_order_state(QUEEN=QUEEN, order_status=order_status, queen_order=queen_order, queen_order_idx=queen_order_idx, priceinfo=priceinfo)
        if save_order:
            print("ROUTE ORDER SAVE QUEEN ORDER", queen_order_idx, origin_order_idx)
            save_queen_order(QUEEN, prod=QUEEN['prod'], client_order_id=queen_order_idx, upsert_to_main_server=upsert_to_main_server)
            if origin_order_idx:
                print("ROUTE ORDER SAVE ORIGIN QUEEN ORDER", queen_order_idx, "ORIGIN ORDER: ", origin_order_idx)
                save_queen_order(QUEEN, prod=QUEEN['prod'], client_order_id=origin_order_idx, upsert_to_main_server=upsert_to_main_server)


        return QUEEN['queen_orders'].loc[queen_order_idx].to_dict()

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
            # if save: # Obsolete with move to save per order
            #     god_save_the_queen(QUEEN, save_q=True, save_qo=True, upsert_to_main_server=upsert_to_main_server, console=True)
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
                            msg = ("APP BUY order gather", app_request['new_queen_order_df']['ticker_time_frame'])
                            QUEEN[app_requests__bucket].append(app_request['app_requests_id'])

                            print(msg)
                            logging.info(msg)
                            append_queen_order(QUEEN, new_queen_order_df=app_request.get('new_queen_order_df'))
                                                        
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

    def check_trigrule_conditions(symbol, storygauge, storygauge_original, QUEEN_KING, active_orders, active_queen_order_states):
        """
        Check if TrigRule conditions are met for a symbol.
        Returns first passing TrigRule dict with trigger_id, or None if none pass.
        """
        try:
            print(f"[TRIGRULE DEBUG] check_trigrule_conditions called for symbol: {symbol}")
            # TEST: Create test TrigRule for this symbol (only once)
            ticker_trigrules = QUEEN_KING['king_controls_queen'].get('ticker_trigrules', [])
            if isinstance(ticker_trigrules, pd.DataFrame):
                ticker_trigrules = ticker_trigrules.to_dict('records')
            
            # Create test rule for current symbol
            if not any(r.get('symbol') == symbol and r.get('marker_value') == -0.2 for r in ticker_trigrules if isinstance(r, dict)):
                ticker_trigrules.append(create_TrigRule(symbol=symbol, trigrule_type='wave_trinity', 
                                                       trigrule_status='active', marker_value=-0.2,
                                                       expire_date=(datetime.now() + timedelta(days=30)).strftime('%m/%d/%YT%H:%M')))
                QUEEN_KING['king_controls_queen']['ticker_trigrules'] = ticker_trigrules
                print(f"[TEST] Created test TrigRule for {symbol}")
            
            # Also create test rules for crypto testing
            for crypto_sym in crypto_currency_symbols:
                if crypto_sym in storygauge_original.index and not any(r.get('symbol') == crypto_sym and r.get('marker_value') == 0.4 for r in ticker_trigrules if isinstance(r, dict)):
                    # Use positive marker_value (0.4) since crypto often has positive trinity_w_L
                    ticker_trigrules.append(create_TrigRule(symbol=crypto_sym, trigrule_type='wave_trinity', 
                                                           trigrule_status='active', marker_value=0.4,
                                                           expire_date=(datetime.now() + timedelta(days=30)).strftime('%m/%d/%YT%H:%M')))
                    QUEEN_KING['king_controls_queen']['ticker_trigrules'] = ticker_trigrules
                    print(f"[TEST] Created test TrigRule for {crypto_sym} (marker_value=0.4 for crypto testing)")
            
            if not ticker_trigrules:
                return None
            
            df_trigrules = pd.DataFrame(ticker_trigrules) if isinstance(ticker_trigrules, list) else ticker_trigrules
            if len(df_trigrules) == 0:
                return None
            
            # Filter for active rules for this symbol
            symbol_rules = df_trigrules[
                (df_trigrules['symbol'] == symbol) & 
                (df_trigrules['trigrule_status'] == 'active')
            ].copy()
            
            if len(symbol_rules) == 0:
                return None
            
            # Get trinity_w_L for the symbol
            if symbol not in storygauge.index:
                return None
            
            ticker_trinity_w_L = storygauge.loc[symbol].get('trinity_w_L')
            if pd.isna(ticker_trinity_w_L):
                print(f"[TRIGRULE DEBUG] Symbol {symbol} has no trinity_w_L value in storygauge")
                return None
            
            print(f"[TRIGRULE DEBUG] Symbol {symbol} trinity_w_L: {ticker_trinity_w_L}")
            
            # Check each rule - return first one that passes
            for idx, rule in symbol_rules.iterrows():
                trigrule_type = rule.get('trigrule_type')
                marker_value = rule.get('marker_value')
                
                print(f"[TRIGRULE DEBUG] Checking rule {idx}: type={trigrule_type}, marker_value={marker_value}")
                
                if pd.isna(marker_value):
                    print(f"[TRIGRULE DEBUG] Rule {idx} skipped: marker_value is NaN")
                    continue
                
                # Check if this trigger_id already has an order (max_order_nums = 1)
                trigger_id = f"{symbol}_{rule.get('trigrule_type')}_{idx}"
                existing_orders = active_orders[
                    (active_orders['queen_order_state'].isin(active_queen_order_states)) &
                    (active_orders['symbol'] == symbol)
                ].copy()
                
                # Check if any existing order has this trigger_id
                has_existing_order = False
                if len(existing_orders) > 0:
                    for _, order in existing_orders.iterrows():
                        order_vars = order.get('order_vars', {})
                        # Handle case where order_vars might be stored as string (JSON)
                        if isinstance(order_vars, str):
                            try:
                                order_vars = ast.literal_eval(order_vars)
                            except:
                                continue
                        
                        if isinstance(order_vars, dict):
                            king_order_rules = order_vars.get('king_order_rules', {})
                            # Handle case where king_order_rules might be stored as string
                            if isinstance(king_order_rules, str):
                                try:
                                    king_order_rules = ast.literal_eval(king_order_rules)
                                except:
                                    continue
                            
                            if isinstance(king_order_rules, dict):
                                if king_order_rules.get('trigger_id') == trigger_id:
                                    has_existing_order = True
                                    break
                
                if has_existing_order:
                    print(f"[TRIGRULE DEBUG] Rule {idx} skipped: existing order found with trigger_id: {trigger_id}")
                    continue  # Skip this rule, already has an order
                
                # Check wave_trinity type
                if trigrule_type == 'wave_trinity':
                    # Compare trinity_w_L against marker_value
                    if marker_value is not None:
                        # Trigger when trinity_w_L meets the marker_value threshold
                        # If marker_value is negative, trigger when trinity_w_L <= marker_value (more negative)
                        # If marker_value is positive, trigger when trinity_w_L >= marker_value (more positive)
                        if marker_value < 0:
                            condition_met = ticker_trinity_w_L <= marker_value
                            print(f"[TRIGRULE DEBUG] wave_trinity check: {ticker_trinity_w_L} <= {marker_value} = {condition_met}")
                        else:
                            condition_met = ticker_trinity_w_L >= marker_value
                            print(f"[TRIGRULE DEBUG] wave_trinity check: {ticker_trinity_w_L} >= {marker_value} = {condition_met}")
                        
                        if condition_met:
                            print(f"[TRIGRULE DEBUG] TrigRule PASSED for {symbol}! trigger_id: {trigger_id}")
                            rule_dict = rule.to_dict()
                            rule_dict['trigger_id'] = trigger_id
                            return rule_dict
                        else:
                            print(f"[TRIGRULE DEBUG] TrigRule NOT PASSED for {symbol} (condition not met)")
                
                # Check trading_pairs type
                elif trigrule_type == 'trading_pairs':
                    deviation_symbols = rule.get('deviation_symbols', [])
                    if not deviation_symbols or len(deviation_symbols) == 0:
                        continue
                    
                    # Calculate deviation for each deviation symbol
                    for dev_symbol in deviation_symbols:
                        if dev_symbol not in storygauge.index:
                            continue
                        
                        dev_symbol_trinity_w_L = storygauge.loc[dev_symbol].get('trinity_w_L')
                        if pd.isna(dev_symbol_trinity_w_L) or dev_symbol_trinity_w_L == 0:
                            continue
                        
                        # Calculate deviation: (ticker_trinity_w_L - deviation_symbol_trinity_w_L) / deviation_symbol_trinity_w_L
                        deviation = (ticker_trinity_w_L - dev_symbol_trinity_w_L) / dev_symbol_trinity_w_L
                        
                        # Compare deviation against marker_value
                        if marker_value is not None:
                            # Trigger when deviation meets or exceeds the marker_value threshold
                            # If marker_value is negative, trigger when deviation <= marker_value (ticker is lower)
                            # If marker_value is positive, trigger when deviation >= marker_value (ticker is higher)
                            if marker_value < 0:
                                condition_met = deviation <= marker_value
                            else:
                                condition_met = deviation >= marker_value
                            
                            if condition_met:
                                rule_dict = rule.to_dict()
                                rule_dict['trigger_id'] = trigger_id
                                return rule_dict
                                break
            
            return None
            
        except Exception as e:
            print(f"Error checking TrigRule conditions for {symbol}: {e}")
            print_line_of_error()
            return None

    def king_knights_requests(QUEEN, STORY_bee, revrec, tm_trig, trigbee, ticker, ticker_time_frame, trading_model, trig_action, app_trig, crypto=False, WT=WT, order_type='buy', trigger_id=None):
        s_ = datetime.now(est)

        """answer all questions for order to be placed, compare against the rules"""
        # measure len of trigbee how long has trigger been there?
        # Std Deivation from last X trade prices
        # Jump on wave if NOT on Wave?
        # collective BUY only when story MACD tier aligns to certian power NEW THEME
        # how many vwap crosses have their been and whats been the frequency
        # take chances buys and sells, allowed default 3, 1 for each blocktime

        # Scenario: buys: :afternoon: if morning > x% then load up vs load down
        # Scenario: sells: :afternoon: if morning > x% & lunch > x% then load up vs load down (look for a quick heavy pull)
        # Scenarios: buys: morning: has push been made? which direction, from vwap

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
        # # Ensure STORYBee
        # if ticker_time_frame not in STORY_bee.keys():
        #     print("TICKER TIME FRAME NOT IN STORY_bee")
        #     STORY_bee[ticker_time_frame] = STORY_bee[f'SPY_{tframe}_{tperiod}'].copy()

         # if 'buy' in tm_trig else 'sell' # always buy until shorting allowed WORKERBEE
        waveview = revrec.get('waveview')
        storygauge = revrec.get('storygauge')

        trinity = storygauge.loc[ticker].get(f'{TRINITY_}w_L')
        waveguage_meter = storygauge.loc[ticker].get(f'{TRINITY_}{WT[star_time]}')

            # how many trades have we completed today? whats our total profit loss with wave trades
            # should you override your original order rules? ### Handled in Allocation ###### 
        try:
            alloc_deploy = waveview.at[ticker_time_frame, 'allocation_deploy']
            alloc_deploy_margin = waveview.at[ticker_time_frame, 'allocation_long_deploy'] - alloc_deploy
            wave_amo=alloc_deploy
            if symbol not in QUEEN['price_info_symbols'].index:
                msg = f'{symbol} NOT in QUEENs price_info_symbols'
                return {'kings_blessing': False, 'msg': 'missing price info'}
            
            ticker_priceinfo = QUEEN['price_info_symbols'].at[symbol, 'priceinfo']
            star_total_budget_remaining = revrec['df_stars'].loc[ticker_time_frame].get("remaining_budget")
            star_total_borrow_remaining = revrec['df_stars'].loc[ticker_time_frame].get("remaining_budget_borrow")

            kings_blessing = False

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
            
            # Store trigger_id in king_order_rules if provided
            if trigger_id:
                king_order_rules['trigger_id'] = trigger_id

            power_up_amo = power_amo()

            if kings_blessing_checks(ticker_time_frame, acct_info, wave_amo, king_order_rules, trig_action_num, time_delta, macd_tier, trigbee, crypto):
                return {'kings_blessing': False}

            def ready_buy_star_timeduration_delay(star_time):
                if star_time == '1Minute_1Day':
                    return 5
                elif star_time == '5Minute_5Day':
                    return 10
                elif star_time == '30Minute_1Month':
                    return 30
                elif star_time == '1Hour_3Month':
                    return 60
                elif star_time == '2Hour_6Month':
                    return 120
                elif star_time == '1Day_1Year':
                    return 360 # fix to days
                else:
                    print("star_time not defined", star_time)
                    return 500
            

            overrule_power = king_order_rules.get('overrule_power')
            overrule_power = 0 if king_order_rules.get('overrule_power') is None else overrule_power

            blessings = {'kings_blessing': kings_blessing, 'blessings': []}



            # if star_total_budget_remaining > 0: # STAR
            borrowed_funds = False
            wave_amo = alloc_deploy
            order_side = 'buy'
            
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
                pass # snapshot always called on execute
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
                        # king_order_rules.update('take_profit': ) 

                        ## WORKERBEE Add TrigRule to king_order_rules
                        trigRule = None
                        # use trigRule Id (concat of symbol, trigrule_type,) How to establish unique ID?
                        if trigRule:
                            king_order_rules.update({'trigRule': trigRule})


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
            auto_pilot_buy = QUEEN_KING['king_controls_queen']['ticker_autopilot']
            if symbol not in auto_pilot_buy.index:
                return True
            if symbol in auto_pilot_buy.index:
                if auto_pilot_buy.at[symbol, 'buy_autopilot'] != True:
                    # print(symbol, ": buy_autopilot FALSE")
                    return True

            return False

        def refresh_star_check(QUEEN_KING, queen_orders, symbol, ttf):
            # if 'ticker_refresh_star' in QUEEN_KING['king_controls_queen'].keys():
            #     refresh_star = QUEEN_KING['king_controls_queen']['ticker_refresh_star'].get(symbol, '1Day_1Year')
            #     last_buy_datetime = queen_orders[(queen_orders['symbol'] == symbol) & (queen_orders['side']=='buy')]
            #     if len(last_buy_datetime) > 0:
            #         last_buy_datetime = last_buy_datetime.iloc[-1]['datetime']
            #     else:
            #         last_buy_datetime = datetime.now(est).replace(year=1989) # no last buy ~ buy away
            #     seconds_needed = star_refresh_star_seconds(refresh_star)
            #     time_in_trade_datetime = datetime.now(est) - last_buy_datetime
                # if seconds_needed > time_in_trade_datetime.total_seconds():
                #     print(symbol, ttf, ": STAR REFRESH TIME IN TRADE", time_in_trade_datetime.total_seconds(), "SECONDS NEEDED", seconds_needed)
                    # return True
            
            return False

        def star_messages(last_buy=None, msg=None):
            # Your function logic here (if any)
            
            # Return the local variables
            return locals()

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
            # active_tickers = QUEEN['heartbeat']['active_tickers'] # ttf

            # # check for missing tickers in price_info
            # try:
            #     price_info_missing = [s for s in symbols if s not in QUEEN['price_info_symbols'].index]
            #     if price_info_missing:
            #         msg = (f"Symbols MISSING PriceInfo Adding In {price_info_missing}")
            #         # logging.info(msg)
            #         print(msg)
            #         snapshot_price_symbols = async_api_alpaca__snapshots_priceinfo(symbols, STORY_bee, api, QUEEN)
            #         df_priceinfo_symbols = pd.DataFrame(snapshot_price_symbols)
            #         df_priceinfo_symbols = df_priceinfo_symbols.set_index('ticker', drop=False)
            #         update_queens_priceinfo_symbols(QUEEN, df_priceinfo_symbols)
            # except Exception as e:
            #     print_line_of_error(f'whaaaa {e}')
            
            if 'stars' not in QUEEN.keys():
                QUEEN['stars'] = {ttf: {'last_buy': datetime.now(est).replace(year=1989)} for ttf in symbols}           
            
            all_orders = QUEEN['queen_orders']
            active_orders = all_orders[all_orders['queen_order_state'].isin(active_queen_order_states)].copy()
            app_wave_trig_req = process_app_requests(QUEEN=QUEEN, QUEEN_KING=QUEEN_KING, request_name='wave_triggers')
            app_trig = {'trig': False}
            app_trig_ttf = False
            if app_wave_trig_req.get('app_flag'):
                print('app flag', app_wave_trig_req.get('ticker_time_frame'))
                # app_wave_trig_req = wave_buy__var_items(ticker_time_frame=app_wave_trig_req.get('ticker_time_frame'), 
                #                                         trigbee=app_wave_trig_req.get('trigbee'), 
                #                                         macd_state=app_wave_trig_req.get('macd_state'), 
                #                                         ready_buy=app_wave_trig_req.get('ready_buy'), 
                #                                         x_buy=app_wave_trig_req.get('x_buy'), 
                #                                         order_rules=app_wave_trig_req.get('order_rules'))
                # buy current wave -- reallocate?

            
            if type(QUEEN.get('price_info_symbols')) is not pd.core.frame.DataFrame:
                print("OLD QUEEN")
                return False

            req = process_app_requests(QUEEN, QUEEN_KING, request_name='buy_orders')
            if req.get('app_flag'):
                acct_info = QUEEN['account_info']
                """Rev Rec"""
                revrec = refresh_chess_board__revrec(acct_info, QUEEN, QUEEN_KING, STORY_bee, active_queen_order_states=active_queen_order_states) ## Setup Board
                waveview = revrec.get('waveview')
                QUEEN['revrec'] = revrec
                god_save_the_queen(QUEEN, save_rr=True, save_q=True, save_qo=True, upsert_to_main_server=upsert_to_main_server)

        
            df = QUEEN.get('price_info_symbols')
            
            df['priceinfo_ast'] = df['priceinfo'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)
            df['current_ask'] = df['priceinfo_ast'].apply(lambda d: d.get('current_ask') if isinstance(d, dict) else None)
            # df['current_ask'] = df['priceinfo'].apply(lambda x: get_priceinfo_ask(x))
            dict_join = dict(zip(df.index, df['current_ask']))
            waveview['current_ask'] = waveview['symbol'].map(dict_join).fillna(8989)


            s_time = datetime.now(est)
            price_info_missing = [s for s in symbols if s not in QUEEN['price_info_symbols'].index]
            broker = 'alpaca' # WORKERBEE HOW TO DECIDE Which BROKER? Need Manual switch (per ticker?)-- brokers joined linked orders... :()
            # Save original storygauge before filtering (needed for crypto test rule creation)
            storygauge_original = storygauge.copy()
            storygauge = storygauge[(storygauge['allocation_deploy'] > 89)].copy()
            
            # Add crypto symbols to processing list if they exist in original storygauge (for TrigRule testing)
            for crypto_sym in crypto_currency_symbols:
                if crypto_sym in storygauge_original.index and crypto_sym not in storygauge.index:
                    storygauge = pd.concat([storygauge, storygauge_original.loc[[crypto_sym]]])
                    print(f"[TRIGRULE DEBUG] Added {crypto_sym} to processing list for TrigRule check")
            
            ### WORKERBEE ###
            # check for trigRule
            # return a dict set of symbol and its list of trigRule

            for symbol in storygauge.index.tolist():
                # If trigRule Calculate trigger info 
                # check trigRule active & not expired
                # check if TrigRule exists inside QUEEN['queen_orders']. iterate over active orders using qo_states check queen_order_state field, then check if TrigRule in order['king_order_rules'] (this also needs to be added on execute order  in order_vars__queen_order_items)
                qo_states = RUNNING_CLOSE_Orders + RUNNING_OPEN
                
                crypto = True if symbol in crypto_currency_symbols else False
                print(f"[TRIGRULE DEBUG] Processing symbol: {symbol}, crypto: {crypto}")
                if stop_ticker(storygauge, symbol, QUEEN_KING):
                    continue

                wave = waveview[waveview['symbol']==symbol]
                if not crypto:
                    wave = wave[(wave['allocation_deploy'] > 89) & (wave['allocation_deploy'] > wave['current_ask'])]
                else:
                    wave = wave[(wave['allocation_deploy'] > 89)]
                
                if len(wave) == 0:
                    continue

                print(f"[TRIGRULE DEBUG] Symbol {symbol} has {len(wave)} waves, proceeding")
                wave = wave.sort_values('allocation_deploy', ascending=False)

                not_enough = wave[(wave['allocation_deploy'] < wave['current_ask']) & (wave['allocation_deploy'] > 0)].copy()
                if len(not_enough) > 0:
                    wave_amo_for_next_wave = not_enough['allocation_deploy'].sum()
                    print(wave_amo_for_next_wave, symbol, "NOT ENOUGH WAVE AMO FOR NEXT WAVE")

                # Check TrigRule conditions at symbol level (before ticker_time_frame loop)
                # This allows testing even when markets are closed
                print(f"[TRIGRULE DEBUG] About to check TrigRule conditions for {symbol} (symbol level)")
                trigrule_result = check_trigrule_conditions(
                    symbol=symbol,
                    storygauge=storygauge,
                    storygauge_original=storygauge_original,
                    QUEEN_KING=QUEEN_KING,
                    active_orders=active_orders,
                    active_queen_order_states=active_queen_order_states
                )
                print(f"[TRIGRULE DEBUG] trigrule_result for {symbol} (symbol level): {trigrule_result}")
                
                # Extract trigger_id if TrigRule passed (will be used later in ticker_time_frame loop)
                trigger_id = trigrule_result.get('trigger_id') if trigrule_result else None
                
                # If symbol has active TrigRules but none passed, skip this symbol entirely
                ticker_trigrules = QUEEN_KING['king_controls_queen'].get('ticker_trigrules')
                if ticker_trigrules:
                    if isinstance(ticker_trigrules, list) and len(ticker_trigrules) > 0:
                        df_check = pd.DataFrame(ticker_trigrules)
                    elif isinstance(ticker_trigrules, pd.DataFrame) and len(ticker_trigrules) > 0:
                        df_check = ticker_trigrules
                    else:
                        df_check = pd.DataFrame()
                    
                    if len(df_check) > 0:
                        symbol_has_rules = len(df_check[
                            (df_check['symbol'] == symbol) & 
                            (df_check['trigrule_status'] == 'active')
                        ]) > 0
                        
                        if symbol_has_rules and not trigrule_result:
                            print(f"[TRIGRULE DEBUG] Symbol {symbol} has active TrigRules but none passed - skipping symbol")
                            continue

                # if crypto and QUEEN['prod']: # TEMP UNTIL CRYPTO handled in QUEEN CONTROLS WORKERBEE
                #     print("PRODUCTION OF CRYPTO ACCOUNT")
                #     broker = 'robinhood'
                """ the hunt """
                s_time = datetime.now(est)

                queen_orders = QUEEN['queen_orders']
                for ticker_time_frame in wave.index.tolist():
                    s_time = datetime.now(est)
                    # path to Knight
                    # ticker, tframe, frame = ticker_time_frame.split("_")
                    # frame_block = f'{tframe}{"_"}{frame}' # frame_block = "1Minute_1Day"
                    
                    """# STORY_bee"""
                    # ensure_story# what happens if no story available?

                    if not crypto and mkhrs != 'open':
                        continue
                    if refresh_star_check(QUEEN_KING, queen_orders, symbol, ticker_time_frame):
                        continue
                    if repeat_purchase_delay(wave, ticker_time_frame, QUEEN):
                        continue
                    if autopilot_check(QUEEN_KING, symbol):
                        continue
                    """# wash sale rule check"""
                    # now_time = datetime.now()
                    # if ticker in storygauge.index:
                    #     wash_sale_rule_buy_date = storygauge.at[ticker, 'wash_sale_next_buy_date']
                    #     if isinstance(wash_sale_rule_buy_date, datetime):
                    #         if now_time < wash_sale_rule_buy_date:
                    #             print("WASH SALE RULE NO BUYING ALLOWED")
                    #             continue

                    # check for missing tickers in price_info
                    if symbol in price_info_missing:
                        msg = (f" {symbol} Symbols MISSING PriceInfo Adding In {price_info_missing}")
                        logging.info(msg)
                        snapshot_price_symbols = async_api_alpaca__snapshots_priceinfo(symbols, STORY_bee, api, QUEEN)
                        df_priceinfo_symbols = pd.DataFrame(snapshot_price_symbols)
                        df_priceinfo_symbols = df_priceinfo_symbols.set_index('ticker', drop=False)
                        update_queens_priceinfo_symbols(QUEEN, df_priceinfo_symbols)


                    # trading model
                    trading_model = QUEEN_KING['king_controls_queen']['symbols_stars_TradingModel'].get(symbol)
                    # trigbee
                    trig = wave.at[ticker_time_frame, 'macd_state']
                    tm_trig = 'buy_cross-0' #trig # point to only 1
                    # buying threshold if in SELL wave
                    trig_wave_length = waveview.at[ticker_time_frame, 'length']
                    trig_wave_length_num = int(trig_wave_length)
  

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
                    # check if you already placed order or if a workerbee in transit to place order
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
                    # print("To The Knight", ticker_time_frame)
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
                        trigger_id=trigger_id)
                    charlie_bee['queen_cyle_times']['cc_knights_request__cc'] = (datetime.now(est) - s_time).total_seconds()
                    if king_resp.get('kings_blessing'):
                        for blessing in king_resp.get('blessings'):
                            if blessing:
                                exx =  execute_buy_order(
                                                      broker=broker,
                                                      order_key=QUEEN['db_root'],
                                                      prod=QUEEN['prod'],
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
                                    append_queen_order(QUEEN, exx.get('new_queen_order_df'))
                                    # logging.info(exx.get('msg'))
                                    msg = (exx.get('msg'))
                                    print(msg)

                                    if 'stars' not in QUEEN.keys():
                                        QUEEN['stars'] = {ticker_time_frame: {'last_buy': datetime.now(est), 'msg': msg}}
                                    else:
                                        QUEEN['stars'].update({ticker_time_frame: {'last_buy': datetime.now(est), 'msg': msg}})

                        QUEEN = refresh_broker_account_portolfio(api, QUEEN)
                        acct_info = QUEEN['account_info']
                        """Rev Rec"""
                        revrec = refresh_chess_board__revrec(acct_info, QUEEN, QUEEN_KING, STORY_bee, active_queen_order_states=active_queen_order_states) ## Setup Board
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
                # snap = api_alpaca__request_call(ticker, api)

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


    def macdGauge_metric(STORY_bee, ticker_time_frame, trigbees=['buy_cross-0', 'sell_cross-0'], number_ranges=[5, 11, 16, 24, 33]):
        # measure trigger bee strength
        try:
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
                return {'metrics': {}}
        except Exception as e:
            print(e, print_line_of_error())


    def qorder_honey__distance_from_breakeven_tiers(run_order):
        # how far away from honey? trading model risk level for each profit stars
        profit_stars = ['high_above_breakeven', 'low_above_breakeven', 'breakeven', 'below_breakeven', 'immediate']
        if run_order['honey'] < 0:
            if run_order['honey'] < -.0033 and run_order['honey'] < -.0055:
                profit_seeking_star = 'high_above_breakeven' # shoot for above breakeven
            elif run_order['honey'] < -.0056 and run_order['honey'] < -.0089:
                profit_seeking_star = 'low_above_breakeven' # shoot for above breakeven
            elif run_order['honey'] < -.009 and run_order['honey'] < -.0013:
                profit_seeking_star = 'breakeven' # shoot for above breakeven
            elif run_order['honey'] < -.0013 and run_order['honey'] < -.0018:
                profit_seeking_star = 'below_breakeven'
            else:
                profit_seeking_star = 'immediate'
            
            return profit_seeking_star
    

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
                    tasks.append(asyncio.ensure_future(get_priceinfo(session, ticker, api, STORY_bee, QUEEN, crypto)))
                original_pokemon = await asyncio.gather(*tasks)
                for pokemon in original_pokemon:
                    return_list.append(pokemon)
                
                return return_list

        list_return = asyncio.run(main(symbols, STORY_bee, api, QUEEN))

        return list_return

    def update_queens_priceinfo_symbols(QUEEN, df):
        if type(QUEEN.get('price_info_symbols')) is not pd.core.frame.DataFrame:
            QUEEN['price_info_symbols'] = df
        else:
            df_main = QUEEN['price_info_symbols']
            # fitler out incoming symbols
            df_main = df_main[~df_main.index.isin(df.index)]
            # join in new data
            df_main = pd.concat([df_main, df])
            # set data back to QUEEN
            QUEEN['price_info_symbols'] = df_main
        
        return True


    def king_bishops_QueenOrder(QUEEN_KING, STORY_bee, run_order, priceinfo, revrec):

        def check_revrec(
                        order_rules,
                        sell_qty, 
                        revrec, 
                        crypto, 
                        ticker_time_frame, 
                        makers_middle_price, 
                        close_order_today, 
                        app_request,
                        min_allocation_field='ticker_total_budget'
                         ):
            try:
                symbol = ticker_time_frame.split("_")[0]

                # WORKERBEE Need a higher defensive check on selling below total budget // issue I think is when multiple sells happen at once
                ignore_allocation_budget = order_rules.get('ignore_allocation_budget', False)
                current_long_value = 'star_buys_at_play' if ignore_allocation_budget else 'star_buys_at_play_allocation'

                if close_order_today or app_request:
                    logging.info(f"{ticker_time_frame} CLOSE Order TODAY")
                    return sell_qty
                
                if symbol not in revrec['storygauge'].index:
                    print(f"{ticker_time_frame} MISSING in RevRec")
                    return sell_qty

                min_allocation = revrec['storygauge'].loc[symbol].get(min_allocation_field, 0)
                if min_allocation == 0:
                    print(f'{ticker_time_frame} no Min Allocation Sell ALL')
                    return sell_qty

                current_long = revrec['storygauge'].loc[symbol].get(current_long_value, 0)
                current_long = revrec['storygauge'].loc[symbol].get('star_buys_at_play', 0) if current_long == 0 else current_long # safeguard
                sellable = max(0, current_long - min_allocation)
                if sellable <= 0:
                    # print(f"{ticker_time_frame} NOT Allowed to SELL Min Allocation LONG: {round(current_long)} MIN: {round(min_allocation)} SELLABLE:{sellable}")
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
                    print("SELL QTY ADJUSTMENT", ticker_time_frame, " adjusted sell qty: ", adjust_qty, " sell qty: ", sell_qty)
                if adjust_qty <= 0:
                    print(ticker_time_frame, "NOT Allowed to SELL Adjusted QTY == ", adjust_qty, " : Sell Qty ==", sell_qty)
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
                                        stagger_profits, 
                                        scalp_profits, 
                                        sell_qty, 
                                        sell_out,
                                        order_rules=order_rules, 
                                        QUEEN=QUEEN):
                sell_order = False
                save_order=False
                now_time = datetime.now(est)
                sell_reasons = []
                close_order_today = order_rules.get('close_order_today')
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
                # last_call_time = now_time.replace(hour=15, minute=58, second=0)

                try:
                    # if scalp_profits:
                    #     scalp_profits = order_rules['scalp_profits_timeduration']
                    #     if time_in_trade_datetime.total_seconds() > float(scalp_profits):
                    #         if honey_gauge['last_30_avg']:
                    #             # store message and compare trading model against distance from breakeven
                    #             if honey_gauge['last_30_avg'] < 0:
                    #                 profit_seek = qorder_honey__distance_from_breakeven_tiers(run_order=run_order)
                    #                 profit_stars = ['high_above_breakeven', 'low_above_breakeven', 'breakeven', 'below_breakeven', 'immediate']
                    #                 # if profit_seek = 'high_above_breakeven'
                    #                 # set limit price based on profit_seek
                    #                 # print("selling out due Scalp Exit last_30_avg ")
                    #                 sell_reason = 'scalp_exit__last_30_avg'
                    #                 # sell_reasons.append(sell_reason)
                    #                 # sell_order = True
                    #                 # order_side = 'sell'
                    #                 # limit_price = False
                    #                 profit_seek_value = priceinfo['maker_middle'] + abs(float(honey) * float(run_order['filled_avg_price']))
                    #                 profit_seek_value = profit_seek_value + (priceinfo['maker_middle'] * .00033)
                    #                 # print(f'{run_order.get("filled_avg_price")}, {profit_seek_value}')
                    #                 # if crypto:
                    #                 #     limit_price = round(profit_seek_value, 1) # current price + (current price * profit seek)
                    #                 # else:
                    #                 #     limit_price = round(profit_seek_value, 2) # current price + (current price * profit seek)

                    #                 # # store message
                    #                 # if 'queen_orders' in QUEEN['subconscious'].keys():
                    #                 #     QUEEN['subconscious']['queen_orders'].update({run_order['client_order_id']: {'client_order_id': run_order['client_order_id'],  'waterfall_sellout_msg': f'{"last_30_avg"}{" find exit price"}' }})
                    #                 # else:
                    #                 #     QUEEN['subconscious']['queen_orders'] = {run_order['client_order_id']: {'client_order_id': run_order['client_order_id'],  'waterfall_sellout_msg': f'{"last_30_avg"}{" find exit price"}' }}

                    """ Take Profit """
                    if honey >= take_profit:
                        # print(f"{ticker_time_frame} selling out due PROFIT ACHIVED order profit: {take_profit}")
                        sell_reason = 'order_rules__take_profit'
                        sell_reasons.append(sell_reason)
                        sell_order = True
                        
                        order_side = 'sell'
                        limit_price = priceinfo['maker_middle'] if order_type == 'limit' else False

                    """ Stop Loss """
                    if sell_out: # can be None or 0==None
                        if honey <= sell_out:
                            # print(f"{ticker_time_frame} selling out due STOP LOSS {client_order_id}")
                            sell_reason = 'order_rules__sellout'
                            sell_reasons.append(sell_reason)
                            sell_order = True

                            order_side = 'sell'
                            limit_price = priceinfo['maker_middle'] if order_type == 'limit' else False

                    """ Wave Cross """
                    if sell_trigbee_trigger:
                        if wave_cross_switched__buytosell and sell_trigbee_datetime <= now_time and time_in_trade_datetime.seconds > 60:
                            # print("SELL ORDER change from Buy to Sell", current_macd, current_macd_time)
                            if macd_gauge['metrics']['sell_cross-0'][5]['avg'] > .5:
                                sell_reason = 'order_rules__macd_cross_buytosell'
                                sell_reasons.append(sell_reason)
                                sell_order = True
                                order_side = 'sell'
                                limit_price = priceinfo['maker_middle'] if order_type == 'limit' else False


                    """ Close Order Today """
                    if close_order_today: # WORKERBEE Change this to sell_date instead to check the datetime and if its past sell
                        if order_rules.get('close_order_today_allowed_timeduration', 60) >= time_to_bell_close and time_in_trade_datetime > timedelta(seconds=60):
                            if time_to_bell_close < 133:
                                print("Selling Out, Trade Not Allowed to go past day")
                                sell_reason = 'close_order_today'
                                sell_reasons.append(sell_reason)
                                sell_order = True
                                order_side = 'sell'
                                limit_price = priceinfo['maker_middle'] if order_type == 'limit' else False
                            
                    """ APP REQUESTS"""
                    app_request = False
                    app_req = process_sell_app_request(QUEEN=QUEEN, QUEEN_KING=QUEEN_KING, run_order=run_order)
                    if app_req['app_flag']:       
                        print("QUEEN processing app sell order")
                        sell_order = True
                        sell_reason = 'app_request'
                        sell_reasons.append(sell_reason)
                        app_request = True
                        
                        sell_qty = float(app_req['sell_qty'])
                        order_type = app_req['type']
                        order_side = app_req['side']
                        limit_price = False
                    

                    if sell_order and sell_reasons:
                        if 'sell_reason' in run_order.keys():
                            current_reasons = QUEEN['queen_orders'].at[client_order_id, 'sell_reason']
                            if str(current_reasons) != str(sell_reasons):
                                # print(ticker_time_frame,  ": Sell Reason Changed", current_reasons, "to", sell_reasons)
                                QUEEN['queen_orders'].at[client_order_id, 'sell_reason'] = sell_reasons
                                # save_order = True
                        if 'queen_wants_to_sell_qty' in run_order.keys():
                            current_sell_qty = QUEEN['queen_orders'].at[client_order_id, 'queen_wants_to_sell_qty']
                            if sell_qty != current_sell_qty:
                                # print(ticker_time_frame, "QUEEN WANTS TO SELL QTY CHANGED: from ", current_sell_qty, "TO NOW SELL", sell_qty)
                                QUEEN['queen_orders'].at[client_order_id, 'queen_wants_to_sell_qty'] = sell_qty
                                # save_order = True
                        
                        if not close_order_today and not app_request: # based on user input, profit, sellout,  and sell_trigbee_trigger...
                            """ AUTO PILOT """
                            auto_pilot_df = QUEEN_KING['king_controls_queen']['ticker_autopilot']
                            if symbol in auto_pilot_df.index:
                                if auto_pilot_df.at[symbol, 'sell_autopilot'] != True:
                                    # print(symbol, ": sell_autopilot FALSE", " -- Sell Reasons", sell_reasons)
                                    return {'sell_order': False, 'save_order': save_order}
                            else:
                                return {'sell_order': False, 'save_order': save_order}


                        makers_middle_price = priceinfo.get('maker_middle')
                        mm_cost = priceinfo.get('maker_middle') * sell_qty
                        order_side = 'sell'
                        sell_qty = check_revrec(order_rules=order_rules,
                                                sell_qty=sell_qty, 
                                                revrec=revrec, 
                                                crypto=crypto, 
                                                ticker_time_frame=ticker_time_frame, 
                                                makers_middle_price=makers_middle_price, 
                                                close_order_today=close_order_today,
                                                app_request=app_request,
                                                min_allocation_field='ticker_total_budget',
                                                )
                        
                        if sell_qty > 0:
                            msg = ("Bishop SAYs SELL:", symbol, ticker_time_frame, sell_reasons, current_macd, sell_qty, mm_cost)
                            print(msg)
                            # logging.info(msg)

                            return {
                            'sell_order': True, 
                            'sell_reason': sell_reason, 
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
                    else:
                        pass
                        if 'sell_reason' in run_order.keys():
                            current_reasons = QUEEN['queen_orders'].at[client_order_id, 'sell_reason']
                            if str(current_reasons) != str([]):
                                # print(ticker_time_frame,  ": Sell Reason Changed", current_reasons, "to", sell_reasons)
                                QUEEN['queen_orders'].at[client_order_id, 'sell_reason'] = sell_reasons
                                # save_order = True
                        if 'queen_wants_to_sell_qty' in run_order.keys():
                            current_sell_qty = QUEEN['queen_orders'].at[client_order_id, 'queen_wants_to_sell_qty']
                            if current_sell_qty != 0:
                                # print(ticker_time_frame, "No Sell Reasons Reset Sell Qty to 0 from: ", current_sell_qty)
                                QUEEN['queen_orders'].at[client_order_id, 'queen_wants_to_sell_qty'] = 0
                                # save_order = True
                        return {'sell_order': False, 'save_order': save_order}
                
                except Exception as e:
                    print('waterfall error', e, " er line>>", print_line_of_error())

            king_bishop = waterfall_sellout_chain(client_order_id, 
                                                  run_order, 
                                                  order_type, 
                                                  limit_price, 
                                                  sell_trigbee_trigger, 
                                                  stagger_profits, 
                                                  scalp_profits, 
                                                  sell_qty, 
                                                  sell_out,
                                                  order_rules=order_rules, 
                                                  QUEEN=QUEEN)
            # if client_order_id == 'run__31359334':
            #     print("RUN ORDER", king_bishop)
            charlie_bee['queen_cyle_times']['om_bishop_block3__om'] = (datetime.now(est) - s_time).total_seconds()

            save_order = True if king_bishop.get('save_order') else False
            if king_bishop['sell_order']:
                if str(king_bishop['sell_qty']) == 'nan':
                    send_email(subject='error checker go see whats up')

                order_vars = order_vars__queen_order_items(order_side='sell',  
                maker_middle=king_bishop['limit_price'],
                sell_reason=king_bishop['sell_reason'], 
                sell_qty=king_bishop['sell_qty'], 
                running_close_legs=running_close_legs,
                ticker_time_frame_origin=ticker_time_frame,
                first_sell=first_sell, 
                time_intrade=time_in_trade_datetime)
                return {'bee_sell': True, 'order_vars': order_vars, 'app_request': king_bishop['app_request'], 'bishop_keys':bishop_keys, 'save_order': save_order}
            else:
                return {'bee_sell': False, 'run_order': run_order, 'save_order': save_order}
        
        except Exception as e:
            print_line_of_error("Bishop Selling Error")
            logging.error("Bishop Selling Error")


    def order_management(BROKER, STORY_bee, QUEEN, QUEEN_KING, api, QUEENsHeart, charlie_bee, mkhrs='closed'): 

        def stop_queen_order_from_kingbishop(QUEEN, QUEEN_KING, run_order):
            # Stop Queen Order from going to the Kings Court -- order_trig_sell_stop, qty_avilable, autopilot'
            
            symbol = run_order.get('symbol')
            ttf = run_order.get('ticker_time_frame')
            client_order_id = run_order.get('client_order_id')
            # refresh_star = QUEEN_KING['king_controls_queen'] #### WORKERBEE
            entered_trade_time = run_order['datetime'].astimezone(est)
            # if 'ticker_refresh_star' in QUEEN_KING['king_controls_queen'].keys():
            #     refresh_star = QUEEN_KING['king_controls_queen']['ticker_refresh_star'].get(symbol, '1Day_1Year')
            #     seconds_needed = star_refresh_star_seconds(refresh_star)
            #     time_in_trade_datetime = datetime.now(est) - entered_trade_time
                # if seconds_needed > time_in_trade_datetime.total_seconds():
                #     print(symbol, ttf, ": STAR REFRESH TIME IN TRADE", time_in_trade_datetime.total_seconds(), "SECONDS NEEDED", seconds_needed)
                    # return True
            # measure times for all ticker_refresh_star
            
            if str(run_order['order_trig_sell_stop']).lower() == 'true': ### consider remaining qty
                return True
            elif run_order['queen_order_state'] not in RUNNING_Orders:
                print(ttf, run_order['client_order_id'], ": QUEEN ORDER STATE NOT RUNNING")
                return True
            elif float(run_order['qty_available']) == 0:
                print(ttf, run_order['client_order_id'], ": QUEEN ORDER QTY AVAILABLE IS ZERO 0")
                QUEEN['queen_orders'].at[client_order_id, 'queen_order_state'] = 'completed'
                save_queen_order(QUEEN, prod=QUEEN['prod'], client_order_id=client_order_id, upsert_to_main_server=upsert_to_main_server)
                return True
            else:
                return False


        # WORKERBEE FIND RETURN BROKER DELTA AND FIX WITH QTY_AVAILABLE
        def queen_orders_main(BROKER, QUEEN, STORY_bee, QUEEN_KING, charlie_bee, mkhrs):
            # WORKERBEE move info just api?
            def long_short_queenorders(df_active, QUEEN, col_metric='cost_basis_current'):
                # WORKERBEE Need to Exclude Long Shorts (SH, PSQ...) so use new column ? long_short
                mask = df_active['symbol'].isin(reverse_indexes)
                long = df_active.loc[~mask, col_metric].fillna(0).sum()
                short = df_active.loc[mask, col_metric].fillna(0).sum()
                QUEEN['heartbeat']['long'] = round(long)
                QUEEN['heartbeat']['short'] = round(short)
                # WORKERBEE crypto
                return True            
            
            try: # App Requests
                s_app = datetime.now(est)
                process_app_requests(QUEEN=QUEEN, QUEEN_KING=QUEEN_KING, request_name='update_queen_order')
                process_app_requests(QUEEN=QUEEN, QUEEN_KING=QUEEN_KING, request_name='update_order_rules')
                # charlie_bee['queen_cyle_times']['om_app_req_om'] = (datetime.now(est) - s_app).total_seconds()
            except Exception as e:
                msg=('APP: Queen Order Main FAILED PROCESSING ORDER', print_line_of_error(e))
                logging.error(msg)
            
            try: # Order Loop
                s_loop = datetime.now(est)
                df_active = QUEEN['queen_orders']
                df_active = df_active[df_active['queen_order_state'].isin(active_queen_order_states)]
                qo_active_index = df_active['client_order_id'].to_list()
                symbols = list(set(df_active['symbol'].to_list()))
                if not symbols:
                    print("No Orders Yet")
                    return True

                long_short_queenorders(df_active, QUEEN, col_metric='cost_basis_current')
                
                s_time = datetime.now(est)
                
                # Price Info Symbols # WORKERBEE priceinfo symbols should come fome main db not QUEEN, WORKERBEE move to new table maybe? symbols_priceinfo
                snapshot_price_symbols = async_api_alpaca__snapshots_priceinfo(symbols, STORY_bee, api, QUEEN)
                df_priceinfo_symbols = pd.DataFrame(snapshot_price_symbols)
                df_priceinfo_symbols = df_priceinfo_symbols.set_index('ticker', drop=False)
                update_queens_priceinfo_symbols(QUEEN, df_priceinfo_symbols)


                s_time_qOrders = datetime.now(est)

                # api # refresh all broker orders which are still pending
                after_hours = True if mkhrs == 'closed' else False
                save_b = False 
                for idx, c_order_id in enumerate(qo_active_index):
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
                        
                        save_b = True
                        update_broker_order_status(BROKER, order_status)


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
                for idex, idx in enumerate(qo_active_index):
                    # time.sleep(2)
                    save_order = False
                    if pd.isna(idx):
                        print("CLIENT ORDER ID is NAN: index: ", idex)
                        continue
                    if idx not in BROKER['broker_orders'].index:
                        print("CLIENT ORDER ID not in BROKER orders: index: ", idex, "idx: ", idx)
                        continue

                    # Queen Order Local Vars
                    run_order = QUEEN['queen_orders'].loc[idx].to_dict()
                    broker = run_order['broker']
                    
                    # broker = handle_broker(broker)
                    if broker != 'alpaca':
                        print(f'BROKER {broker} NOT supported for Queen Orders UPDATING to alpaca for {idx}')
                        save_order = True
                        broker = 'alpaca'
                        QUEEN['queen_orders'].at[idx, 'broker'] = broker
                        save_queen_order(QUEEN, prod=QUEEN['prod'], client_order_id=idx, upsert_to_main_server=upsert_to_main_server)
                    
                    app_req = process_sell_app_request(QUEEN=QUEEN, QUEEN_KING=QUEEN_KING, run_order=run_order, check_only=True).get('app_flag')
                    
                    symbol = run_order.get('symbol')
                    crypto = True if symbol in crypto_currency_symbols else False
                    
                    try: 
                        # snapshot prices bar
                        priceinfo = QUEEN['price_info_symbols'].at[symbol, 'priceinfo']
                        
                        order_status = BROKER['broker_orders'].loc[idx].to_dict()

                        # Updates Broker Order if changed
                        queen_order_lastmod = str(run_order.get('updated_at'))
                        broker_order_lastmod = str(order_status.get('updated_at'))

                        if queen_order_lastmod != broker_order_lastmod:
                            print(f"{symbol} ORDER {idx} : Broker Order Updated {broker_order_lastmod}")
                            order_status = check_order_status(broker=broker, api=api, client_order_id=idx)
                            if not order_status:
                                adhoc_handle_queen_order_broker_failure(order_status, QUEEN, idx)
                                continue                     
                            run_order = update_latest_queen_order_status(QUEEN=QUEEN, order_status=order_status, queen_order_idx=idx)
                            save_order = True
                            save_broker_order = True
                            update_broker_order_status(BROKER, order_status)


                        # Process Queen Order States
                        run_order = route_queen_order(QUEEN=QUEEN, 
                                                      queen_order=run_order, 
                                                      queen_order_idx=idx, 
                                                      order_status=order_status, 
                                                      priceinfo=priceinfo,
                                                      save_order=save_order,
                                                      ) ## send in order_status

                        if float(run_order.get('qty_available')) > 0 and run_order.get('order_trig_sell_stop') == True:
                            if release_trig_sell_stop(QUEEN=QUEEN, ticker=symbol, client_order_id=idx):
                                print("RELEASE TRIG SELL STOP", symbol, idx)
                                save_queen_order(QUEEN, prod=QUEEN['prod'], client_order_id=idx, upsert_to_main_server=upsert_to_main_server)


                        """MARKET HOURS"""

                        if not app_req:
                            if stop_queen_order_from_kingbishop(QUEEN, QUEEN_KING, run_order): # false, order_trig_sell_stop or qty_avilable
                                continue

                        if not crypto and mkhrs != 'open':
                            # print("equity market is closed")
                            continue

                        ## subconsicous here ###
                        ro_ttf = run_order['ticker_time_frame']
                        if run_order['ticker_time_frame'] not in STORY_bee.keys():
                            # Handle Order if Ticker Stream Turned off I.E. Not in STORY_bee
                            print(f"{ro_ttf} Missing from STORY_bee")

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
                                # logging.info(exx.get('msg'))
                                append_queen_order(QUEEN, exx.get('new_queen_order_df'))
                                queen_order_idx = exx.get('new_queen_order_df').index[0]

                                QUEEN = refresh_broker_account_portolfio(api, QUEEN) #heartbeat
                                
                                """ Hold ORDER from being SOLD again until Release Validation """
                                origin_order_idx = exx.get('new_queen_order_df').at[queen_order_idx, 'exit_order_link']
                                QUEEN['queen_orders'].at[origin_order_idx, 'order_trig_sell_stop'] = True
                                update_origin_order_qty_available(QUEEN=QUEEN, run_order_idx=origin_order_idx, RUNNING_CLOSE_Orders=RUNNING_CLOSE_Orders, RUNNING_Orders=RUNNING_Orders, save=save)

                                QUEEN['revrec'] = refresh_chess_board__revrec(QUEEN['account_info'], QUEEN, QUEEN_KING, STORY_bee, active_queen_order_states=active_queen_order_states) ## Setup Board

                        elif king_eval_order.get('save_order'):
                            save_queen_order(QUEEN, prod=QUEEN['prod'], client_order_id=idx, upsert_to_main_server=upsert_to_main_server)
                            QUEEN['revrec'] = refresh_chess_board__revrec(QUEEN['account_info'], QUEEN, QUEEN_KING, STORY_bee, active_queen_order_states=active_queen_order_states) ## Setup Board



                    except Exception as e:
                        print_line_of_error(f'ORDER FAILED {e}')
                        send_email(subject="Order Failed", body=str(e))
                        time.sleep(33)


                if save_broker_order:
                    if pg_migration:
                        PollenDatabase.upsert_data(BROKER.get('table_name'), BROKER.get('key'), BROKER, main_server=server)
                    else:
                        PickleData(BROKER.get('source'), BROKER, console=False)

                if save:
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
        init_logging(queens_chess_piece=queens_chess_piece, db_root=db_root, prod=prod, loglevel=loglevel)

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
            STORY_bee = PollenDatabase.retrieve_all_story_bee_data(symbols).get('STORY_bee') # WORKERBEE let server call?
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

        if 'price_info_symbols' not in QUEEN.keys():
            print("init price info for QUEEN")
            # Price Info Symbols
            symbols = return_queenking_board_symbols(QUEEN_KING)
            snapshot_price_symbols = async_api_alpaca__snapshots_priceinfo(symbols, STORY_bee, api, QUEEN)
            df_priceinfo_symbols = pd.DataFrame(snapshot_price_symbols)
            df_priceinfo_symbols = df_priceinfo_symbols.set_index('ticker', drop=False)
            update_queens_priceinfo_symbols(QUEEN, df_priceinfo_symbols)
        
        print(f'ProdEnv {prod} Here we go Mario')


        # handle App updates
        process_app_requests(QUEEN, QUEEN_KING, request_name='update_queen_order')
        process_app_requests(QUEEN, QUEEN_KING, request_name='update_order_rules')
        
        if pg_migration:
            charlie_bee = qb.get('CHARLIE_BEE')
            queens_charlie_bee, charlie_bee = init_charlie_bee(db_root, pg_migration=pg_migration, charlie_bee=charlie_bee)
        else:
            queens_charlie_bee, charlie_bee = init_charlie_bee(db_root) # monitors queen order cycles, also seen in heart
        charlie_bee['queen_cycle_count'] = 0
        
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
        last_order_refresh = datetime.now(est)
        heartbeat_cyle = deque([], 3000)
        cycle_time = datetime.now(est)
        while True:
            mkhrs = return_market_hours(trading_days=trading_days)
            seconds_to_market_close = (datetime.now(est).replace(hour=16, minute=0, second=0) - datetime.now(est)).total_seconds()

            db_keys_df = (pd.DataFrame(PollenDatabase.get_all_keys_with_timestamps(table_name, server=server))).rename(columns={0:'key', 1:'timestamp'})
            db_keys_df['key_name'] = db_keys_df['key'].apply(lambda x: x.split("-")[-1])
            db_keys_df = db_keys_df.set_index('key_name')

            s = datetime.now(est)
            # if queens_chess_piece.lower() == 'queen': # Rule On High
            
            """ The Story of every Knight and their Quest """
            s = datetime.now(est)
            # refresh db
            s_time = datetime.now(est)
            # QUEEN Databases
            if pg_migration:
                qk_lastmod = db_keys_df.at['QUEEN_KING', 'timestamp']
                if str(qk_lastmod) != str(pq_qk_lastmod):
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
                STORY_bee = PollenDatabase.retrieve_all_story_bee_data(symbols, main_server=server).get('STORY_bee')
                # Ticker database of pollenstory ## Need to seperate out into tables 
            else:
                STORY_bee = return_QUEENs__symbols_data(QUEEN=QUEEN, QUEEN_KING=QUEEN_KING, read_storybee=True, read_pollenstory=False).get('STORY_bee') ## async'd func

            QUEEN = refresh_QUEEN_starTickers(QUEEN=QUEEN, STORY_bee=STORY_bee, ticker_allowed=ticker_allowed)
            charlie_bee['queen_cyle_times']['db_refresh'] = (datetime.now(est) - s_time).total_seconds()

            """Account Info"""
            QUEEN = refresh_broker_account_portolfio(api, QUEEN)
            acct_info = QUEEN['account_info']
            # portfolio = QUEEN['portfolio']

            god_save_the_queen(QUEEN, save_acct=True, console=False, upsert_to_main_server=upsert_to_main_server)

            charlie_bee['queen_cyle_times']['cc_block1_account'] = (datetime.now(est) - s_time).total_seconds()

            # Read client App Reqquests
            s_time = datetime.now(est)
            process_app_requests(QUEEN=QUEEN, QUEEN_KING=QUEEN_KING, request_name='queen_sleep')
            process_app_requests(QUEEN=QUEEN, QUEEN_KING=QUEEN_KING, request_name='subconscious')
            charlie_bee['queen_cyle_times']['app'] = (datetime.now(est) - s_time).total_seconds()

            # Refresh Board
            revrec = refresh_chess_board__revrec(acct_info, QUEEN, QUEEN_KING, STORY_bee, active_queen_order_states=active_queen_order_states, wash_sale_rule=wash_sale_rule) ## Setup Board

            charlie_bee['queen_cyle_times']['cc_revrec'] = revrec.get('cycle_time')
            QUEEN['revrec'] = revrec
            
            god_save_the_queen(QUEEN, save_rr=True, console=False, upsert_to_main_server=upsert_to_main_server) # WORKERBEE unessecary SAVING only save whats needed

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
            # if beat < 8:
            #     print("Zz ZzZzZ zZz")
            #     time.sleep(8)

            # charlie_bee['queen_cyle_times']['beat_times'].append({'datetime': datetime.now(est).strftime("%Y-%m-%d %H:%M:%S"), 'beat': beat})
            # charlie_bee['queen_cyle_times']['QUEEN_avg_cycle'].append(beat)
            # charlie_bee['queen_cyle_times']['QUEEN_avg_cycletime'] = sum(charlie_bee['queen_cyle_times']['QUEEN_avg_cycle'])/len(charlie_bee['queen_cyle_times']['QUEEN_avg_cycle'])
            # if pg_migration:
            #     PollenDatabase.upsert_data(table_name, key=charlie_bee.get('key'), value=charlie_bee)
            # else:
            #     PickleData(queens_charlie_bee, charlie_bee, console=False)
            heartbeat_cyle.append(beat)
            
            charlie_bee['queen_cycle_count'] += 1
            if datetime.now(est) - cycle_time > timedelta(seconds=60):
                cycle_time = datetime.now(est)
                print("Beat", beat, datetime.now(est).strftime('%y-%m-%d:%H:%M'))
                avg_beat = sum(heartbeat_cyle) / len(heartbeat_cyle)
                QUEENsHeart.update({"heartbeat_beat": round(beat)})
                QUEENsHeart.update({"heartbeat_avg_beat": round(avg_beat)})
                god_save_the_queen(QUEEN, QUEENsHeart, upsert_to_main_server=upsert_to_main_server)
            
            if beat > 23:
                logging.warning((queens_chess_piece, ": SLOW cycle Heart Beat: ", beat, "use price gauge"))
                # print('use price gauge') # (STORY_bee["SPY_1Minute_1Day"]["story"]["price_gauge"])

            # Should you operate now? I thnik the brain never sleeps ?
            if 'crypto' not in queens_chess_piece:
                if datetime.now(est) > datetime.now(est).replace(hour=16, minute=00):
                # if mkhrs != 'open':
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
                    break
            if datetime.now(est) > datetime.now(est).replace(hour=3, minute=00) and datetime.now(est) < datetime.now(est).replace(hour=4, minute=00):
                print("Eeveryone Needs to Sleep")
                break

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
        parser.add_argument ('-loglevel', default='error')
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
