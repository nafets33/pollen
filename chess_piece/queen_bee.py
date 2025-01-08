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
from chess_piece.king import main_index_tickers, hash_string, kingdom__global_vars, print_line_of_error, return_QUEENs__symbols_data, PickleData, return_QUEEN_KING_symbols
from chess_piece.queen_hive import (kingdom__grace_to_find_a_Queen,
                                    init_charlie_bee, 
                                    init_queenbee, 
                                    power_amo, 
                                    return_queenking_board_symbols,
                                    find_symbol, 
                                    star_ticker_WaveAnalysis, 
                                    return_queen_orders__query, 
                                    initialize_orders, 
                                    refresh_account_info, 
                                    init_clientUser_dbroot, 
                                    process_order_submission, 
                                    get_best_limit_price, 
                                    hive_dates, 
                                    send_email, 
                                    return_STORYbee_trigbees, 
                                    init_logging, 
                                    convert_to_float, 
                                    order_vars__queen_order_items, 
                                    logging_log_message, 
                                    return_alpc_portolio, 
                                    return_market_hours, 
                                    check_order_status,  
                                    timestamp_string, 
                                    submit_order, 
                                    return_timestamp_string, 
                                    add_key_to_QUEEN, 
                                    update_sell_date,
                                    return_Ticker_Universe
                                    )
from chess_piece.queen_mind import refresh_chess_board__revrec, weight_team_keys
from chess_piece.pollen_db import PollenDatabase, PollenJsonEncoder, PollenJsonDecoder
import copy
from tqdm import tqdm


pg_migration = os.getenv('pg_migration')

pd.options.mode.chained_assignment = None
est = pytz.timezone("US/Eastern")
# utc = pytz.timezone('UTC')

notification_list = deque([], 500)

# ###### GLOBAL # ######
KING, users_allowed_queen_email, users_allowed_queen_emailname__db = kingdom__grace_to_find_a_Queen()
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

ACTIVE_SYMBOLS = return_Ticker_Universe().get('alpaca_symbols_dict')

# crypto
crypto_currency_symbols = ['BTCUSD', 'ETHUSD', 'BTC/USD', 'ETH/USD']
coin_exchange = "CBSE"
# misc
exclude_conditions = [
    'B','W','4','7','9','C','G','H','I','M','N',
    'P','Q','R','T','V','Z'
] # 'U'



def generate_client_order_id(ticker, trig, sellside_client_order_id=False): # generate using main_order table and trig count

    temp_date = datetime.now(est).strftime("%y-%m-%d %M.%S.%f")
    order_string = f'{ticker}-{trig}-{temp_date}'
    order_id = hash_string(order_string)
    
    if sellside_client_order_id:
        order_id = f'{"close__"}{order_id}'
    else:        
        order_id = f'{"run__"}{order_id}'
    
    return order_id


def submit_order_validation(ticker, qty, side, portfolio, run_order_idx=False):
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
                msg = (f'{ticker} Qty Value Not Valid (less then 1) setting to 1')
                qty = 1.0
                qty_correction = True
                logging.warning("CORRECTION on BUY Quanity, Qty < 1 setting to 1")
                return func_return(qty, qty_correction=qty_correction, log=True, log_msg=msg)
            else:
                msg = ('Buy Order Validated')
                return func_return()
        elif side == 'sell': # sel == sell
            # print("check portfolio has enough shares to sell")
            if ticker not in portfolio.keys():
                msg = f'submit order validation({ticker}), MISSING_TICKER ARCHVING ORDER'
                return func_return(queen_order_state='completed_alpaca', stop_order=True, log_msg=msg, log=True)
            elif position > 0 and position < qty: # long
                msg = (f'submit order validation() {ticker} #of shares avail: {position} >>> NOT enough shares avail to sell, updating sell qty')            
                return func_return(qty=position, qty_correction=True, log_msg=msg, log=True)
            elif position < 0 or (position - qty) < 0:
                msg = (f"ARCHVING ORDER, SHORTING, Scenario Not Added {run_order_idx}")
                return func_return(qty, queen_order_state='completed_alpaca', stop_order=True, log_msg=msg, log=True)
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

def update_origin_order_qty_available(QUEEN, run_order_idx, RUNNING_CLOSE_Orders, RUNNING_Orders):
    try:
        # Return QueenOrder
        queen_order = QUEEN['queen_orders'].loc[run_order_idx].to_dict()
        if queen_order['queen_order_state'] in RUNNING_Orders:
            closing_dfs = return_closing_orders_df(QUEEN, queen_order['client_order_id'])
            if len(closing_dfs) > 0: # WORKERBEE num convert NOT necesary REMOVE
                closing_dfs['qty'] = closing_dfs['qty'].apply(lambda x: convert_to_float(x))
                closing_dfs['filled_qty'] = closing_dfs['filled_qty'].apply(lambda x: convert_to_float(x))
                closing_dfs['filled_avg_price'] = closing_dfs['filled_avg_price'].apply(lambda x: convert_to_float(x))

                # validate qty
                closing_filled = sum(closing_dfs['filled_qty'])
                order_qty = float(queen_order['qty'])
                if closing_filled > order_qty:
                    msg=(f"wtf closing > origin order Linked Orders filled {closing_filled} Order has {order_qty}", queen_order['client_order_id'], queen_order['symbol'])
                    print(msg)
                    # logging.error(msg)
                    pass

                # update queen order
                QUEEN['queen_orders'].at[run_order_idx, 'qty_available'] = float(queen_order['filled_qty']) - sum(closing_dfs['filled_qty'])
                QUEEN['queen_orders'].at[run_order_idx, 'qty_available_pending'] = float(queen_order['filled_qty']) - sum(closing_dfs['filled_qty'])
            else:
                QUEEN['queen_orders'].at[run_order_idx, 'qty_available'] = float(queen_order['filled_qty'])
        elif queen_order['queen_order_state'] in RUNNING_CLOSE_Orders:
            QUEEN['queen_orders'][run_order_idx]['qty_available'] = float(queen_order['qty']) - float(queen_order['filled_qty'])
        elif queen_order['queen_order_state'] in CLOSED_queenorders:
            msg=(f"{run_order_idx} Order Closed and will Complete in later function Consider Closing HERE????")
            print(msg)
            logging.error(msg)
        else:
            print('Update Origin wtf are you?', queen_order['client_order_id'], queen_order['queen_order_state'])
        
        return True
    except Exception as e:
        print_line_of_error(e)
        return False


def append_queen_order(QUEEN, new_queen_order_df):
    QUEEN['queen_orders'] = pd.concat([QUEEN['queen_orders'], new_queen_order_df], axis=0) # , ignore_index=True
    QUEEN['queen_orders']['client_order_id'] = QUEEN['queen_orders'].index
    return True


def execute_buy_order(api, blessing, ticker, ticker_time_frame, trig, wave_amo, order_type='market', side='buy', crypto=False, limit_price=False, portfolio=None, trading_model=False, ACTIVE_SYMBOLS=ACTIVE_SYMBOLS):
    try:
        if ticker not in ACTIVE_SYMBOLS:
            logging.error(f"{ticker} No Longer Active symbol")
            return {'executed': False}
        
        tic, tframe, tperiod = ticker_time_frame.split("_")
        star = f'{tframe}_{tperiod}'

        def update__validate__qty(crypto, current_price, limit_price, wave_amo):
            if crypto:
                limit_price = round(limit_price) if limit_price else limit_price
                qty_order = float(round(wave_amo / current_price, 8))
            else:
                limit_price = round(limit_price, 2) if limit_price else limit_price
                qty_order = float(round(wave_amo / current_price, 0))

            return limit_price, qty_order

        # get latest pricing
        snap = api.get_snapshot(ticker) if crypto == False else api.get_crypto_snapshot(ticker, exchange=coin_exchange)
        priceinfo_order = {'price': snap.latest_trade.price, 'bid': snap.latest_quote.bid_price, 'ask': snap.latest_quote.ask_price, 'bid_ask_var': snap.latest_quote.bid_price/snap.latest_quote.ask_price}
        # priceinfo_order = {'price': priceinfo['current_price'], 'bid': priceinfo['current_bid'], 'ask': priceinfo['current_ask']}
        
        # logging.info(f"ATTEMPTING TO BUY {ticker}")
        # if app order get order vars its way

        order_vars = blessing
        limit_price = limit_price if limit_price != False else False
        limit_price, qty_order = update__validate__qty(crypto=crypto, current_price=priceinfo_order['price'], limit_price=limit_price, wave_amo=wave_amo)
        if limit_price:
            order_type = 'limit'
        # Client Order Id
        client_order_id__gen = generate_client_order_id(ticker=ticker, trig=trig)
        
        if portfolio is not None:
            order_val = submit_order_validation(ticker=ticker, qty=qty_order, side=side, portfolio=portfolio)                    
            if order_val.get('log'):
                logging.warning(order_val.get('log_msg'))
            if order_val.get('qty_correction'):
                logging.warning(order_val.get('log_msg'))
                # QUEEN['queen_orders'].at[run_order_idx, 'validation_correction'] = 'true' # WORKERBEE handle later
                qty_order = order_val.get('qty')

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

        # logging.info("order submit")
        order = vars(order_submit.get('order'))['_raw']

        if 'borrowed_funds' not in order_vars.keys():
            order_vars['borrowed_funds'] = False
        order_vars['qty_order'] = qty_order
        
        new_queen_order_df = process_order_submission(
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
        msg = (f'Ex BUY Order {trig} {ticker_time_frame} {round(wave_amo,2):,}')

        return {'executed': True, 'msg': msg, 'new_queen_order_df': new_queen_order_df, 'priceinfo_order': priceinfo_order}

    except Exception as e:
        print_line_of_error(f"ERROR Ex BUY Order..Full Failure {ticker_time_frame} ERROR is {e}")
        return {'executed': False}


def execute_sell_order(api, QUEEN, king_eval_order, ticker, ticker_time_frame, trig, run_order_idx, crypto=False, limit_price=False, portfolio=None, order_type='market', side='sell', ACTIVE_SYMBOLS=ACTIVE_SYMBOLS):
    try:
        if ticker not in ACTIVE_SYMBOLS:
            logging.error(f"{ticker} No Longer Active symbol")
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
        portfolio = QUEEN.get('portfolio')
        
        snap = api.get_snapshot(ticker) if crypto == False else api.get_crypto_snapshot(ticker, exchange=coin_exchange)

        # get latest pricing
        priceinfo_order = {'price': snap.latest_trade.price, 'bid': snap.latest_quote.bid_price, 'ask': snap.latest_quote.ask_price, 'bid_ask_var': snap.latest_quote.bid_price/snap.latest_quote.ask_price}

        run_order_client_order_id = QUEEN['queen_orders'].at[run_order_idx, 'client_order_id']
        order_vars = king_eval_order['order_vars']

        # close out order variables
        sell_qty = float(king_eval_order['order_vars']['sell_qty']) # float(order_obj['filled_qty'])

        # Generate Client Order Id
        client_order_id__gen = generate_client_order_id(ticker=ticker, trig=trig, sellside_client_order_id=run_order_client_order_id)

        limit_price, sell_qty = update__sell_qty(crypto, limit_price, sell_qty)

        # Validate Order
        order_val = submit_order_validation(ticker=ticker, qty=sell_qty, side=side, portfolio=portfolio, run_order_idx=run_order_idx)

        if order_val.get('log'):
            logging.error(order_val.get('log_msg'))
        if order_val.get('stop_order'):
            QUEEN['queen_orders'].at[run_order_idx, 'queen_order_state'] = 'completed_alpaca'
            return order_val
        if order_val.get('qty_correction'):
            logging.warning(order_val.get('log_msg'))
            QUEEN['queen_orders'].at[run_order_idx, 'validation_correction'] = 'true'
            sell_qty = order_val.get('qty')

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

        return{'executed': True, 'msg': msg, 'new_queen_order_df': new_queen_order_df, 'priceinfo_order': priceinfo_order}

    except Exception as e:
        print("Error Ex Order..Full Failure" , ticker_time_frame, e, print_line_of_error())


def refresh_broker_account_portolfio(api, QUEEN, account=False, portfolio=False):
    if portfolio:
        portfolio = return_alpc_portolio(api)['portfolio']
        QUEEN['portfolio'] = portfolio
        QUEEN['heartbeat']['portfolio'] = portfolio
    if account:
        acct_info = refresh_account_info(api=api)['info_converted']
        QUEEN['account_info'] = acct_info
        QUEEN['heartbeat']['account_info'] = acct_info





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

def update_latest_queen_order_status(QUEEN, order_status, queen_order_idx): # updates qty and cost basis from Alpaca
    for order_key, order_value in order_status.items():
        QUEEN['queen_orders'].at[queen_order_idx, order_key] = order_value

    if order_status['filled_qty'] is not None:
        QUEEN['queen_orders'].at[queen_order_idx, 'filled_qty'] = float(order_status['filled_qty'])
    if order_status['filled_avg_price'] is not None:
        QUEEN['queen_orders'].at[queen_order_idx, 'filled_avg_price'] = float(order_status['filled_avg_price'])
        QUEEN['queen_orders'].at[queen_order_idx, 'cost_basis'] = float(order_status['filled_qty']) * float(order_status['filled_avg_price'])
        av_qty = float(QUEEN['queen_orders'].at[queen_order_idx, 'qty_available'])
        avg_price_fill = float(QUEEN['queen_orders'].at[queen_order_idx, 'filled_avg_price'])          
        if av_qty > 0:
            QUEEN['queen_orders'].at[queen_order_idx, 'cost_basis_current'] = av_qty * avg_price_fill
            
    return QUEEN['queen_orders'].loc[queen_order_idx].to_dict()

def check_origin_order_status(QUEEN, origin_order, origin_idx, closing_filled):
    if float(origin_order["filled_qty"]) == closing_filled: 
        # print("# running order has been fully sold out and now we can archive")
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
    # origin_order_cost_basis__qorder = float(queen_order['filled_qty']) * float(origin_order['filled_avg_price'])
    origin_order_cost_basis__qorder = origin_order.get('cost_basis')
    origin_filled_qty = float(queen_order['filled_qty'])
    queen_order_cost_basis = origin_filled_qty * float(queen_order['filled_avg_price'])
    # queen_order_cost_basis__to_origin_order = queen_order_cost_basis - origin_order_cost_basis__qorder
    
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
        if queen_order.get('client_order_id') == 'run__SH-sell_cross-0-16-23-08-04 35.54.':
            print(ticker, current_ask, current_bid, current_price)
        
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
            if 'honey_gauge' in queen_order.keys():
                QUEEN['queen_orders'].at[queen_order_idx, 'honey_gauge'].append(current_profit_loss)
        else:
            current_profit_loss = 0
            QUEEN['queen_orders'].at[queen_order_idx, 'honey'] = 0
            QUEEN['queen_orders'].at[queen_order_idx, 'money'] = 0
            QUEEN['queen_orders'].at[queen_order_idx, 'current_ask'] = current_ask
            QUEEN['queen_orders'].at[queen_order_idx, 'current_bid'] = current_bid
        
        return {'current_profit_loss': current_profit_loss}
    except Exception as e:
        print(ticker, " pl error", e, print_line_of_error())


def route_queen_order(QUEEN, queen_order, queen_order_idx, order_status, priceinfo):

    def alpaca_queen_order_state(QUEEN, order_status, queen_order, queen_order_idx, priceinfo):
        try:
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
                    origin_order = origin_order.get('origin_order')
                    if origin_order_idx:
                        # confirm profits
                        profit_loss_value = update_runCLOSE__queen_order_honey(QUEEN=QUEEN, queen_order=queen_order, origin_order=origin_order, queen_order_idx=queen_order_idx)['profit_loss_value']
                        QUEEN['queen_orders'].at[queen_order_idx, 'queen_order_state'] = 'completed'
                        msg=(f'{queen_order_idx} {origin_order.get("symbol")} closing filled: {profit_loss_value}')
                        logging.info(msg)

                    #### CHECK to see if Origin ORDER has Completed LifeCycle ###
                        res = update_origin_orders_profits(QUEEN=QUEEN, queen_order=queen_order, origin_order=origin_order, origin_order_idx=origin_order_idx)
                        closing_filled = res['closing_filled']
                        profit_loss = res['profit_loss']
                        # Qty Available
                        update_origin_order_qty_available(QUEEN=QUEEN, run_order_idx=origin_order_idx, RUNNING_CLOSE_Orders=RUNNING_CLOSE_Orders, RUNNING_Orders=RUNNING_Orders)
                        # Check to complete Queen Order
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

                else:
                    print("Critical Error New Order Side")
                    logging_log_message(log_type='error', msg='Critical Error New Order Side')
            else:
                print("critical errror new order type received")
                logging.error(f"WTF Route me {queen_order_idx}")
        
            
            return QUEEN['queen_orders'].loc[queen_order_idx].to_dict()

        except Exception as e:
            print('queen router failed', e, print_line_of_error())
    

    queen_order = update_latest_queen_order_status(QUEEN=QUEEN, order_status=order_status, queen_order_idx=queen_order_idx)
    queen_order = alpaca_queen_order_state(QUEEN=QUEEN, order_status=order_status, queen_order=queen_order, queen_order_idx=queen_order_idx, priceinfo=priceinfo)

    return QUEEN['queen_orders'].loc[queen_order_idx].to_dict()


def god_save_the_queen(QUEEN, QUEENsHeart=False, charlie_bee=False, save_q=False, save_acct=False, save_rr=False, save_qo=False, active_queen_order_states=active_queen_order_states, console=True):
    
    try:
        # Save Heart to avoid saving Queen to improve speed
        # if charlie_bee:
        #     QUEENsHeart.update({"charlie_bee": charlie_bee})
        if QUEENsHeart:
            QUEENsHeart['heartbeat'] = QUEEN['heartbeat']
            QUEENsHeart.update({"heartbeat_time": datetime.now(est)})
            if pg_migration:
                PollenDatabase.upsert_data(QUEENsHeart.get('table_name'), QUEENsHeart.get('key'), QUEENsHeart)
            else:
                PickleData(QUEEN['dbs'].get('PB_QUEENsHeart_PICKLE'), QUEENsHeart, console=console)
        if save_q:
            if pg_migration:
                PollenDatabase.upsert_data(QUEEN.get('table_name'), QUEEN.get('key'), QUEEN)
            else:
                PickleData(QUEEN['dbs'].get('PB_QUEEN_Pickle'), QUEEN, console=console)
        if save_qo:
            df = QUEEN.get('queen_orders')
            df = df[df['queen_order_state'].isin(active_queen_order_states)]
            ORDERS = {'queen_orders': df}
            if pg_migration:
                key = f'{QUEEN.get("key").split("-")[0]}-ORDERS'
                PollenDatabase.upsert_data(QUEEN.get('table_name'), key=key, value=ORDERS)
            else:
                PickleData(QUEEN['dbs'].get('PB_Orders_Pickle'), {'queen_orders': df}, console=console)
        if save_acct:
            if pg_migration:
                key = f'{QUEEN.get("key").split("-")[0]}-ACCOUNT_INFO'
                ACCOUNT_INFO = QUEEN.get('account_info')
                PollenDatabase.upsert_data(QUEEN.get('table_name'), key=key, value=ACCOUNT_INFO)
            else:
                PickleData(QUEEN['dbs'].get('PB_account_info_PICKLE'), {'account_info': QUEEN.get('account_info')}, console=console)
        if save_rr:
            if pg_migration:
                key = f'{QUEEN.get("key").split("-")[0]}-REVREC'
                revrec = QUEEN.get('revrec')
                PollenDatabase.upsert_data(QUEEN.get('table_name'), key=key, value=revrec)
            else:
                PickleData(QUEEN['dbs'].get('PB_RevRec_PICKLE'), {'revrec': QUEEN.get('revrec')}, console=console)
        
        return True
    except Exception as e:
        print_line_of_error(e)
        sys.exit()


def queenbee(client_user, prod, queens_chess_piece='queen'):
    table_name = 'client_user_store' if prod else 'client_user_store_sandbox'

    def update_queen_order(QUEEN, update_package):
        # update_package client_order id and field updates {client_order_id: {'queen_order_status': 'running'}}
        try:
            save = False
            for c_order_id, package in update_package['queen_order_updates'].items():
                for field_, new_value in package.items():
                    try:
                        QUEEN['queen_orders'].at[c_order_id, field_] = new_value
                        save = True
                    except Exception as e:
                        print(e, 'failed to update QueenOrder')
                        logging.critical({'msg': 'failed to update queen orders', 'error': e, 'other': (field_, new_value)})
            if save:
                god_save_the_queen(QUEEN, save_q=True, save_qo=True)
        except Exception as e:
            print_line_of_error()
            logging.critical({'error': e, 'msg': 'update queen order', 'update_package': update_package})
        return True

    def update_queen_order_order_rules(QUEEN, update_package):
        try:
            save = False
            for c_order_id, package in update_package['update_order_rules'].items():
                for field_, new_value in package.items():
                    try:
                        QUEEN['queen_orders'].at[c_order_id, 'order_rules'].update({field_: new_value})
                        save = True
                        logging.info((f'{field_} updated to {new_value}'))
                    except Exception as e:
                        print(e, 'failed to update QueenOrder')
                        logging.critical({'msg': 'failed to update queen orders', 'error': e, 'other': (field_, new_value)})
            if save:
                god_save_the_queen(QUEEN, save_q=True, save_qo=True)
        except Exception as e:
            print_line_of_error()
            logging.critical({'error': e, 'msg': 'update queen order', 'update_package': update_package})
        return True

    def process_sell_app_request(QUEEN, QUEEN_KING, run_order, request_name='sell_orders', app_requests__bucket='app_requests__bucket'):
        client_order_id = run_order.get('client_order_id')
        order_state = run_order.get('queen_order_state')  # currenting func in waterfall so it will always be running order
        app_order_base = [i for i in QUEEN_KING[request_name]]
        
        if len(app_order_base) > 0:
            for app_request in app_order_base:
                if app_request['app_requests_id'] in QUEEN[app_requests__bucket]:
                    continue
                elif app_request['client_order_id'] == client_order_id:
                    print(f"{client_order_id} ORDER ALREADY CLOSED")
                    if order_state in CLOSED_queenorders:
                        msg = f'Queen Already Processing Sell Order'
                        if client_order_id in QUEEN['queens_messages'].keys():
                            QUEEN['queens_messages'][client_order_id].update({'msg': msg})
                        else:
                            QUEEN['queens_messages'][client_order_id] = {'msg': msg}
                        QUEEN['app_requests__bucket'].append(app_request['app_requests_id'])
                    else:
                        print("App Req Sell Order")
                        sell_qty = app_request.get('sell_qty')
                        o_type = app_request.get('type')
                        side = app_request.get('side')
                        limit = app_request.get('limit')

                        QUEEN['app_requests__bucket'].append(app_request['app_requests_id'])
                        god_save_the_queen(QUEEN, save_q=True, save_qo=True)
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
                            msg = ("APP BUY order gather")
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
                    if pg_migration:
                        PollenDatabase.upsert_data(QUEEN.get('table_name'), key=QUEEN.get('key'), value=QUEEN)
                    else:
                        PickleData(QUEEN['dbs'].get('PB_QUEEN_Pickle'), QUEEN)
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
            print(e, print_line_of_error())

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

    def add_app_wave_trigger(active_trigs, ticker, app_wave_trig_req):
        if app_wave_trig_req['app_flag'] == False:
            return active_trigs
        else:
            if ticker == app_wave_trig_req['app_request']['ticker']:
                active_trigs.update(app_wave_trig_req['app_request']['wave_trigger']) # test
                msg = {'added app_wave_trigger()': 'added wave drone'}
                print(msg)
                # queen process
                logging.info(msg)
                return active_trigs
            else:
                return active_trigs

    def king_knights_requests(QUEEN, STORY_bee, revrec, tm_trig, trigbee, ticker, ticker_time_frame, trading_model, trig_action, app_trig, crypto=False, WT=WT):
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
            
            # ACCOUNT amo greater then available account
            if wave_amo > acct_info.get('daytrading_buying_power'):
                print("day trade buying power exceeded")
                wave_amo = acct_info.get('daytrading_buying_power') - wave_amo
                if wave_amo <= 0:
                    print(f"{ticker_time_frame} budget buying power is depleted for daytrading_buying_power")
                    return True
            # Ignore Tiering, this looks like dup WORKERBEE
            elif "ignore_trigbee_in_macdstory_tier" in king_order_rules.keys():
                if macd_tier in king_order_rules.get("ignore_trigbee_in_macdstory_tier"):
                    # print(f'{ticker_time_frame} Ignore Trigger macd_tier: , {macd_tier}')
                    return True #(f'{ticker_time_frame} Ignore Trigger macd_tier: , {macd_tier}')
            elif trig_action_num > 0: ## already happens in Water Fall
                if time_delta < timedelta(minutes=king_order_rules['doubledown_timeduration']):
                    msg = (f"{ticker_time_frame} TRIG In Action, DoubleDown Time Delta Not Met wave amo {wave_amo}")
                    # print(msg)
                    # logging.info(msg)
                    return True
            elif 'sell' in trigbee: # == 'sell_cross-0':
                if crypto:
                    print(f'crypto not allowed')
                    return True
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
        main_indexes = QUEEN['heartbeat']['main_indexes']
        ticker, tframe, tperiod = ticker_time_frame.split("_")
        symbol = find_symbol(main_indexes, ticker, trading_model, trigbee).get('ticker') # for SPY & QQQ to get inverse X of trading model
        star_time = f'{tframe}{"_"}{tperiod}'

        order_type = 'buy' if 'buy' in tm_trig else 'sell'
        waveview = revrec.get('waveview')
        storygauge = revrec.get('storygauge')
        # storygauge = storygauge.set_index('symbol') # not necessary?

        trinity = storygauge.loc[ticker].get(f'{TRINITY_}w_L')
        waveguage_meter = storygauge.loc[ticker].get(f'{TRINITY_}{WT[star_time]}')

        try:
            alloc_deploy = waveview.at[ticker_time_frame, 'allocation_deploy']
            wave_amo=alloc_deploy
            if symbol not in QUEEN['price_info_symbols'].index:
                msg = f'{symbol} NOT in QUEENs price_info_symbols'
                return {'kings_blessing': False}
            
            ticker_priceinfo = QUEEN['price_info_symbols'].at[symbol, 'priceinfo']
            star_total_budget_remaining = revrec['df_stars'].loc[ticker_time_frame].get("remaining_budget")
            star_total_borrow_remaining = revrec['df_stars'].loc[ticker_time_frame].get("remaining_budget_borrow")

            kings_blessing = False

            # how many trades have we completed today? whats our total profit loss with wave trades
            # should you override your original order rules? ### Handled in Allocation ###### 

            # trade scenarios / power ups / 
            trig_action_num = len(trig_action) # get trading model amount allowed?
            now_time = datetime.now(est)
            if trig_action_num != 0:
                trig_action.iloc[-1]['datetime']
                time_delta = now_time - trig_action.iloc[-1]['datetime']
            else:
                time_delta = now_time - datetime.now(est)

            acct_info = QUEEN['account_info']

            # Theme
            theme = QUEEN_KING['king_controls_queen']['theme'] # what is the theme?
            trading_model_theme = trading_model.get('theme')
            trading_model_star = trading_model['stars_kings_order_rules'].get(f'{tframe}_{tperiod}')

            """Stars Forever Be in Heaven"""
            macd_tier = waveview.loc[ticker_time_frame].get('end_tier_macd')

            s_ = datetime.now(est)
            current_macd_cross__wave = star_ticker_WaveAnalysis(STORY_bee=STORY_bee, ticker_time_frame=ticker_time_frame)['current_wave']
            current_wave = star_ticker_WaveAnalysis(STORY_bee=STORY_bee, ticker_time_frame=ticker_time_frame)['current_active_waves'][tm_trig]
            current_wave_blocktime = current_wave['wave_blocktime']
            charlie_bee['queen_cyle_times']['cc_symbol_waveAnalysis'] = (datetime.now(est) - s_).total_seconds()

            # Trading Model Vars
            # Global switch to user power rangers at ticker or portfolio level 
            if trading_model_theme == 'story__AI':
                print('story ai update KORs with lastest from story view()')
            king_order_rules = trading_model['stars_kings_order_rules'][star_time]['trigbees'][tm_trig][current_wave_blocktime]
            maker_middle = ticker_priceinfo['maker_middle'] if str(trading_model_star.get('trade_using_limits')) == 'true' else False
            king_order_rules['sell_trigbee_date'] = update_sell_date(star_time)

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
            
            ready_buy = True if app_trig.get('ready_buy') else False
            if app_trig.get('ready_buy'):
                print("KNIGHT ready buy")
                king_order_rules.update({'ready_buy': True, 'sell_trigbee_trigger_timeduration':ready_buy_star_timeduration_delay(star_time)})
            
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
                    logging.warning(msg)
                else:
                    msg = (f"KNIGHT {ticker_time_frame} Wave Amo > then star BORROW Budget using Remaining borrowed funds {round(wave_amo)}")
                    logging.warning(msg)
                    wave_amo = star_total_borrow_remaining
            ticker_current_ask = float(STORY_bee[ticker_time_frame]['story'].get('current_ask'))
            # if wave_amo > # ticker price
            if wave_amo < ticker_current_ask:
                msg = (f'KNIGHT EXIT wave amo LESS then current ask {ticker_time_frame} current ask: {ticker_current_ask} wave amo: {round(wave_amo)}')
                logging.warning(msg)
                return {'kings_blessing': False}
            
            kings_blessing = True
            double_down_trade=False
            
            if trig_action_num > 0: ## move this to before KNIGHT
                if time_delta > timedelta(minutes=king_order_rules['doubledown_timeduration']) or app_trig.get('trig') == True:
                    print("Trig In Action Double Down Trade")
                    logging.info(f"Double Down Wave {ticker_time_frame} trigbee {trigbee}")
                    kings_blessing = True
                    double_down_trade = True
                else:
                    # print(ticker_time_frame, "double down delta HAULT")
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
                                                            ready_buy=ready_buy,
                                                            assigned_wave=current_macd_cross__wave,
                                                            borrow_qty=0,
                                                            )                
                blessings['blessings'].append(order_vars)

                ## MARGIN BUY consider another buy based on trinity
                wave_len = str(revrec['waveview'].at[ticker_time_frame, 'length'])
                if borrowed_funds == False and star_total_borrow_remaining > 0 and wave_len == '0': # order did not have to dip into margin
                    print("Lets Buy on MARGIN")
                    # # handle trinity
                    trinity = calculate_margin_buy(trinity, waveguage_meter, order_type, smooth=4)
                    if trinity:            
                        wave_amo = star_total_borrow_remaining * trinity
                        print("Margin Buy", wave_amo)
                        ## update KORS on based on trinity, ticker_time_frame
                        # king_order_rules.update('take_profit': ) 
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
                                                                    ready_buy=ready_buy,
                                                                    assigned_wave=current_macd_cross__wave,
                                                                    borrow_qty=0,
                                                                    )
                        blessings['blessings'].append(order_vars)
                
                charlie_bee['queen_cyle_times']['cc_knight'] = (datetime.now(est) - s_).total_seconds()

                return blessings
            else:
                msg = (f'KNIGHT EXIT NO WAVE AMO {ticker_time_frame} {ticker_current_ask} {round(wave_amo)}')
                logging.warning(msg)
                return {'kings_blessing': False}


            
        except Exception as e:
            print_line_of_error()

    def command_conscience(QUEEN, STORY_bee, QUEEN_KING, api):

        def star_messages(last_buy=None, msg=None):
            # Your function logic here (if any)
            
            # Return the local variables
            return locals()
        try:
                

            s_time = datetime.now(est)
            # def global level allow trade to be considered
            # 1 stop Level of tier trading only allowed x number of trades a day until you receive day trade margin
            revrec = QUEEN['revrec']
            waveview = revrec.get('waveview')
            active_tickers = QUEEN['heartbeat']['active_tickers'] # ttf

            # check for missing tickers in price_info
            symbols = active_tickers
            price_info_missing = [s for s in symbols if s not in QUEEN['price_info_symbols'].index]
            if price_info_missing:
                msg = (f"Symbols MISSING PriceInfo Adding In {price_info_missing}")
                logging.info(msg)
                print(msg)
                snapshot_price_symbols = async_api_alpaca__snapshots_priceinfo(symbols, STORY_bee, api, QUEEN)
                df_priceinfo_symbols = pd.DataFrame(snapshot_price_symbols)
                df_priceinfo_symbols = df_priceinfo_symbols.set_index('ticker', drop=False)
                update_queens_priceinfo_symbols(QUEEN, df_priceinfo_symbols)

            if 'stars' not in QUEEN.keys():
                QUEEN['stars'] = {ttf: {'last_buy': datetime.now(est).replace(year=1989)} for ttf in active_tickers}           
            
            all_orders = QUEEN['queen_orders']
            active_orders = all_orders[all_orders['queen_order_state'].isin(active_queen_order_states)].copy()
            app_wave_trig_req = process_app_requests(QUEEN=QUEEN, QUEEN_KING=QUEEN_KING, request_name='wave_triggers')
            app_trig = {'trig': False}
            ready_buy = False
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
                god_save_the_queen(QUEEN, save_rr=True, save_q=True, save_qo=True)
            
            # cycle through stories  # The Golden Ticket
            s_time = datetime.now(est)
            for ticker in active_tickers:
                # Ensure Trading Model
                if ticker not in QUEEN_KING['king_controls_queen']['symbols_stars_TradingModel'].keys():
                    msg = (f'model_does_not_exist {ticker}')
                    # print(msg)
                    # logging.error(msg)
                    continue 
                crypto = True if ticker in crypto_currency_symbols else False

                if crypto: # crypto currently not supported
                    continue

                """ the hunt """
                s_time = datetime.now(est)
                req = return_STORYbee_trigbees(QUEEN=QUEEN, STORY_bee=STORY_bee, tickers_filter=[ticker])
                active_trigs = req.get('active_trigs') # {ttf: [waves]}

                # waveview current ask
                df = QUEEN.get('price_info_symbols')
                df['current_ask'] = df['priceinfo'].apply(lambda x: x.get('current_ask'))
                dict_join = dict(zip(df.index, df['current_ask']))
                waveview['current_ask'] = waveview['symbol'].map(dict_join).fillna(8989)
            
                bees_fly = waveview[(waveview['symbol'] == ticker) &
                                    (waveview['allocation_deploy'] > 0) &
                                    ((waveview['allocation_deploy']) > waveview['current_ask'])
                                    ].copy()
                # conflicts your sellhomes are cancel out the flying

                def repeat_purchase_delay(ticker_time_frame, QUEEN):
                    if ticker_time_frame in QUEEN['stars'].keys():
                        if (datetime.now(est) - QUEEN['stars'].get(ticker_time_frame).get('last_buy')) < timedelta(seconds=60):
                            buy_msg = QUEEN['stars'].get(ticker_time_frame).get('msg')
                            msg = (buy_msg, 'Just Bought, Deploying Is Still', bees_fly.at[ticker_time_frame, 'allocation_deploy'], " StarAtPlay: ", bees_fly.at[ticker_time_frame, 'star_at_play'], " Ask Price", bees_fly.at[ticker_time_frame, 'current_ask'])
                            print(msg)
                            return True
                    return False

                def autopilot_check(QUEEN_KING, symbol):
                    if symbol in QUEEN_KING['king_controls_queen']['ticker_autopilot'].index:
                        if QUEEN_KING['king_controls_queen']['ticker_autopilot'].at[symbol, 'buy_autopilot'] == False:
                            print(symbol, ": buy_autopilot FALSE")
                            return True

                    return False
        
                for ticker_time_frame in bees_fly.index.tolist():
                    s_time = datetime.now(est)
                    
                    if repeat_purchase_delay(ticker_time_frame, QUEEN):
                        continue

                    # path to Knight
                    ticker, tframe, frame = ticker_time_frame.split("_")
                    
                    if autopilot_check(QUEEN_KING, symbol=ticker):
                        continue

                    frame_block = f'{tframe}{"_"}{frame}' # frame_block = "1Minute_1Day"
                    # trading model
                    trading_model = QUEEN_KING['king_controls_queen']['symbols_stars_TradingModel'].get(ticker)
                    
                    # trigbee
                    trig = bees_fly.at[ticker_time_frame, 'macd_state']
                    tm_trig = trig
                    trig_wave_length = waveview.at[ticker_time_frame, 'length']
                    on_wave_buy = True if trig_wave_length != '0' else False
                    if on_wave_buy:
                        tm_trig = 'buy_cross-0' if 'buy' in trig else 'sell_cross-0'
                    
                    trig_type = 'buy' if 'buy' in tm_trig else 'sell'

                    # check global ticker level
                    if frame_block in ['1Minute_1Day']:
                        if trig_type == 'buy' and revrec['storygauge'].loc[ticker].get('trinity_w_15') > .33:
                            msg=(ticker, "trinity short 1min buy > 0 not buying")
                            # logging.info(msg)
                            continue
                        elif trig_type == 'sell' and revrec['storygauge'].loc[ticker].get('trinity_w_15') < -.33:
                            msg=("shorting when trinity in negative")
                            # logging.info(msg)
                            continue
                    
                    if revrec.get('df_ticker').loc[ticker, 'ticker_buying_power'] == 0:
                        msg = (f'{ticker} Conscience NO ticker_buying_power')
                        print(msg)
                        logging.warning(msg)
                        continue
                    
                    if str(trading_model['status']) not in ['active', 'true']:
                        QUEEN['queens_messages'].update({'model_not_active': f'{ticker_time_frame}'})
                        print("model status not active")
                        continue

                    # Stop Symbols from shorting unless you are main_index ("Wants to Short Stock Scenario")
                    if 'sell' in trig and ticker not in QUEEN['heartbeat']['main_indexes'].keys():
                        # print("ticker not avail to short > short gauge >")
                        continue

                    # try: # """ Trigger Bees"""                         
                    # check if you already placed order or if a workerbee in transit to place order
                    s_ = datetime.now(est)
                    # ticker_in_action = True if ticker in active_orders['symbol'].to_list() else False
                    ticker_trig_action = ticker_trig_In_Action_cc(active_orders=active_orders, trig=tm_trig, ticker=ticker)
                    trig_action = trig_In_Action_cc(active_orders=active_orders, trig=tm_trig, ticker_time_frame=ticker_time_frame)
                    charlie_bee['queen_cyle_times']['cc_trig_in_action'] = (datetime.now(est) - s_).total_seconds()
                    # Protect the Knight
                    if len(ticker_trig_action) > 0 and trading_model.get('short_position') == True: # shorting allowed
                        msg=("Only 1 Trigger Allowed in ticker Shorting")
                        logging.warning(msg)
                        continue
                    timestamp_str = return_timestamp_string()
                    if revrec['df_stars'].loc[ticker_time_frame].get("remaining_budget") <= 0 and revrec['df_stars'].loc[ticker_time_frame].get("remaining_budget_borrow") <= 0:
                        msg=(f'{ticker_time_frame} remaining budget used up')
                        if msg in notification_list:
                            continue
                        logging.warning(msg)
                        notification_list.append(msg)
                        # print(f'{ticker_time_frame} all budget used up') # WORKER BEE only LOG message if timestamp has elasped say X seconds 
                        # if ticker_time_frame not in QUEEN['queens_messages'].keys():
                        #     QUEEN['queens_messages'][ticker_time_frame] = {'remaining_budget': f'{ticker_time_frame} all budget used up {timestamp_str}'}
                        # else:
                        #     QUEEN['queens_messages'][ticker_time_frame].update({'remaining_budget': f'{ticker_time_frame} all budget used up {timestamp_str}'})
                        continue

                    # if crypto: # Not currently supported
                    #     # check if ticker_time_frame is in temp, if yes then check last time it was put there, if it has been over X time per timeframe rules then send email to buy
                    #     QUEEN['crypto_temp']['trigbees'].update({ticker_time_frame: {'king_resp': king_resp, 'datetime': datetime.now(est)}})

                    """ HAIL TRIGGER, WHAT SAY YOU? ~forgive me but I bring a gift for the king and queen"""
                    s_time = datetime.now(est)
                    # print("To The Knight", ticker_time_frame)
                    king_resp = king_knights_requests(
                        QUEEN=QUEEN, 
                        STORY_bee=STORY_bee, 
                        revrec=revrec, 
                        tm_trig=tm_trig, 
                        trigbee=trig,
                        ticker=ticker,
                        ticker_time_frame=ticker_time_frame, 
                        trading_model=trading_model, 
                        trig_action=trig_action, 
                        crypto=crypto, 
                        app_trig=app_trig)
                    charlie_bee['queen_cyle_times']['cc_knights_request__cc'] = (datetime.now(est) - s_time).total_seconds()
                    
                    if king_resp.get('kings_blessing'):
                        for blessing in king_resp.get('blessings'):
                            if blessing:
                                exx =  execute_buy_order(
                                                      api=api, 
                                                      blessing=blessing, 
                                                      trading_model=blessing.get('trading_model'), 
                                                      ticker=blessing.get('symbol'), 
                                                      ticker_time_frame=blessing.get('ticker_time_frame_origin'), 
                                                      trig=blessing.get('trigbee'), 
                                                      wave_amo=blessing.get('wave_amo'), 
                                                    #   order_type='market',
                                                    #   side='buy', 
                                                    #   crypto=False, 
                                                    #   limit_price=False, 
                                                      portfolio=QUEEN.get('portfolio')
                                                      )
                                if exx.get('executed'):
                                    append_queen_order(QUEEN, exx.get('new_queen_order_df'))
                                    logging.info(exx.get('msg'))
                                    msg = (exx.get('msg'))
                                    print(msg)

                                    if 'stars' not in QUEEN.keys():
                                        QUEEN['stars'] = {ticker_time_frame: {'last_buy': datetime.now(est), 'msg': msg}}
                                    else:
                                        QUEEN['stars'].update({ticker_time_frame: {'last_buy': datetime.now(est), 'msg': msg}})

                        acct_info = QUEEN['account_info']
                        """Rev Rec"""
                        revrec = refresh_chess_board__revrec(acct_info, QUEEN, QUEEN_KING, STORY_bee, active_queen_order_states=active_queen_order_states) ## Setup Board
                        QUEEN['revrec'] = revrec
                        god_save_the_queen(QUEEN, save_q=True, save_rr=True, save_qo=True, console=False)

                if app_wave_trig_req.get('app_flag') == True and ticker == app_wave_trig_req['app_request']['ticker']:
                    active_trigs = add_app_wave_trigger(active_trigs=active_trigs, ticker=ticker, app_wave_trig_req=app_wave_trig_req)
                
                charlie_bee['queen_cyle_times']['cc_thehunt__cc'] = (datetime.now(est) - s_time).total_seconds()

            return True
        except Exception as e:
            print_line_of_error()


    """>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> ORDER MANAGEMENT <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< """
    """>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> ORDER MANAGEMENT <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< """
    """>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> ORDER MANAGEMENT <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< """




    def return_snap_priceinfo__pollenData(QUEEN, STORY_bee, ticker, api):
        # read check if ticker is active...if it is return into from db ELSE return broker data 
        call_snap = False
        ttf = f'{ticker}{"_1Minute_1Day"}'
        if ttf not in QUEEN['heartbeat']['available_tickers']:
            print(f"{ttf} NOT in Workerbees")
            call_snap = True
        
        def api_alpaca__request_call(ticker, api, call_type='snapshot'):

            if call_type == 'snapshot':
                try:
                    snap = api.get_snapshot(ticker)
                except Exception as e:
                    print("snap error", e)
                    time.sleep(1)
                    snap = api.get_snapshot(ticker)
                
                return snap
        
        if call_snap:
            snap = api_alpaca__request_call(ticker, api)
            
            c=0
            while True:
                conditions = snap.latest_quote.conditions
                valid = [j for j in conditions if j in exclude_conditions]
                if len(valid) == 0 or c > 5:
                    break
                else:
                    snap = api_alpaca__request_call(ticker, api)
                    c+=1 
            
            current_price = snap.latest_trade.price
            current_ask = snap.latest_quote.ask_price
            current_bid = snap.latest_quote.bid_price

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
            else:
                # print("release order back to Bishop no linked orders active")
                logging.info(("Releaseing Order back to Bishop be Sold: ", client_order_id))
                QUEEN['queen_orders'].at[client_order_id, 'order_trig_sell_stop'] = False    
            
            
            
            return True                
        except Exception as e:
            print(e)

            # do you have any active running_close against you?

    def stop_queen_order_from_kingbishop(QUEEN_KING, run_order):
        # Stop Queen Order from going to the Kings Court -- order_trig_sell_stop, qty_avilable, autopilot'
        
        symbol = run_order.get('symbol')
        ttf = run_order.get('ticker_time_frame')
        # revrec = QUEEN_KING['chess_board']
        # refresh_star = QUEEN_KING['king_controls_queen']
        if symbol in QUEEN_KING['king_controls_queen']['ticker_autopilot'].index:
            if QUEEN_KING['king_controls_queen']['ticker_autopilot'].at[symbol, 'sell_autopilot'] == False:
                print(symbol, ttf, ": sell_autopilot FALSE")
                return True
        
        if run_order == False:
            return True
        elif str(run_order['order_trig_sell_stop']).lower() == 'true': ### consider remaining qty
            return True
        elif run_order['queen_order_state'] not in RUNNING_Orders:
            return True
        elif float(run_order['qty_available']) <= 0:
            return True
        else:
            return False


    def async_api_alpaca__snapshots_priceinfo(symbols, STORY_bee, api, QUEEN, mkhrs='open'): # re-initiate for i timeframe 

        async def get_priceinfo(session, ticker, api, STORY_bee, QUEEN):
            async with session:
                try:
                    priceinfo = return_snap_priceinfo__pollenData(QUEEN=QUEEN, STORY_bee=STORY_bee, ticker=ticker, api=api)
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
                    if mkhrs != 'open':
                        continue # markets are not open for you
                    tasks.append(asyncio.ensure_future(get_priceinfo(session, ticker, api, STORY_bee, QUEEN)))
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


    def king_bishops_QueenOrder(STORY_bee, run_order, priceinfo, revrec):

        def check_revrec(sell_qty, revrec, trigname, current_macd, mm_cost, ticker_time_frame, makers_middle_price, close_order_today=False):
            try:
                # at symbol level, the sell amount cannot exceed the min allocation
                # wave
                macd_state_ = trigname.split("_")[0]
                # current_macd_ = current_macd.split("_")[0]
                if close_order_today:
                    logging.info(f"{ticker_time_frame} CLOSE Order TODAY")
                    return sell_qty
                symbol = ticker_time_frame.split("_")[0]
                if symbol in revrec['storygauge'].index and 'buy' == macd_state_:
                    min_allocation = revrec['storygauge'].loc[symbol].get('allocation_long')
                    if min_allocation is None:
                        print(f'{ticker_time_frame} no Min Allocation Sell ALL')
                        return sell_qty
                    
                    current_long = revrec['storygauge'].loc[symbol].get('star_buys_at_play')
                    current_long = 0 if current_long is None else current_long

                    sellable = current_long - min_allocation
                    not_allowed_to_sell_msg = (f"{ticker_time_frame} NOT Allowed to SELL Min Allocation SELLABLE:{sellable}")
                    if sellable <= 0:
                        print(not_allowed_to_sell_msg)
                        return 0
                    else:
                        adjust_qty = min(round(sellable / makers_middle_price), sell_qty)
                        adjust_qty = 0 if adjust_qty < 1 else adjust_qty
                        if adjust_qty != sell_qty:
                            msg = ("SELL QTY ADJUSTMENT", ticker_time_frame, " sell qty: ", sell_qty, " adjusted sell qty: ", adjust_qty)
                            logging.info(msg)
                        if adjust_qty == 0:
                            msg = ("NOT Allowed to SELL Min Allocation")
                        return adjust_qty
                else:
                    if macd_state_ == 'sell':
                        logging.info(f"{ticker_time_frame} No Min Alloc for SHORTS, Inverse Index")
                        pass
                    else:
                        logging.warning(f"{ticker_time_frame} MISSING in RevRec")
                    return sell_qty
                
            except Exception as e:
                print_line_of_error(f'QUEEN: {ticker_time_frame} :: REVREC CHECK ERROR {e}')
                return 0
        
        """if you made it here you are running somewhere, I hope you find your way, I'll always bee here to help"""
        try:
            # # # Stars in Heaven

            s_time = datetime.now(est)
            # gather run_order Vars
            trigname = run_order['trigname']
            order_rules = run_order.get('order_rules')
            client_order_id = run_order['client_order_id']
            take_profit = order_rules['take_profit']
            sell_out = order_rules.get('sell_out')
            sell_qty = float(run_order['qty_available'])
            ticker_time_frame = run_order['ticker_time_frame']
            ticker_time_frame_origin = run_order['ticker_time_frame_origin']
            entered_trade_time = run_order['datetime'].astimezone(est)
            time_in_trade_datetime = datetime.now(est) - entered_trade_time
            
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
            honey_gauge = honeyGauge_metric(run_order)

            charlie_bee['queen_cyle_times']['om_bishop_block1_queenorder__om'] = (datetime.now(est) - s_time).total_seconds()
            s_time = datetime.now(est)

            """ Bishop Knight Waves """
            df_waves_story = STORY_bee[ticker_time_frame]['waves']['story']
            current_story_wave = df_waves_story.iloc[-1].to_dict()

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
            
            # Wave Analysis
            current_wave = star_ticker_WaveAnalysis(STORY_bee=STORY_bee, ticker_time_frame=ticker_time_frame_origin).get('current_wave') # df slice or can be dict
            if len(QUEEN['queen_orders'].at[client_order_id, 'assigned_wave']) == 0:
                print(client_order_id, " assign wave first pass do this at order creation?", QUEEN['queen_orders'].at[client_order_id, 'assigned_wave'])
                QUEEN['queen_orders'].at[client_order_id, 'assigned_wave'] = current_wave
            
            assigned_wave = QUEEN['queen_orders'].at[client_order_id, 'assigned_wave']
            # compare current wave against it stats How Far away are you from max profit?

            """ Trading Models Kings Order Rules """ 
            # Trading Model Sell Vars
            # use maxprofit deviation here and add to order
            wave_length = current_wave['length'] - assigned_wave.get('length') ## current_wave['length'] - trigname_count
            wave_time_tomaxprofit  = current_wave['time_to_max_profit'] - assigned_wave.get('time_to_max_profit')
            current_wave_maxprofit_stat = wave_length - wave_time_tomaxprofit
            
            run_order_wave_changed = True if run_order['assigned_wave'].get('wave_id') != current_wave.get("wave_id") else False

            # Gather main sell reason groups
            sell_trigbee_trigger = True if str(order_rules['sell_trigbee_trigger']).lower() == 'true' else False
            stagger_profits = True if str(order_rules['stagger_profits']).lower() == 'true' else False
            scalp_profits = True if str(order_rules['scalp_profits']).lower() == 'true' else False
            macd_tier = current_macd_time
            
            charlie_bee['queen_cyle_times']['om_bishop_block2_queenorder__om'] = (datetime.now(est) - s_time).total_seconds()
            s_time = datetime.now(est)

            """ WaterFall sell chain """
            def waterfall_sellout_chain(client_order_id, run_order, order_type, limit_price, sell_trigbee_trigger, stagger_profits, scalp_profits, sell_qty, order_rules=order_rules, QUEEN=QUEEN):
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
                    print(e)
                    sell_trigbee_datetime = now_time
                    
                wave_cross_switched__buytosell = True if "buy" in run_order['trigname'] and "sell" in current_macd else False
                wave_cross_switched__selltobuy = True if "sell" in run_order['trigname'] and "buy" in current_macd else False

                time_to_bell_close = (now_time.replace(hour=16, minute=00, second=0) - now_time).total_seconds()
                # last_call_time = now_time.replace(hour=15, minute=58, second=0)

                try:
                    if scalp_profits:
                        scalp_profits = order_rules['scalp_profits_timeduration']
                        if time_in_trade_datetime.total_seconds() > float(scalp_profits):
                            if honey_gauge['last_30_avg']:
                                # store message and compare trading model against distance from breakeven
                                if honey_gauge['last_30_avg'] < 0:
                                    profit_seek = qorder_honey__distance_from_breakeven_tiers(run_order=run_order)
                                    profit_stars = ['high_above_breakeven', 'low_above_breakeven', 'breakeven', 'below_breakeven', 'immediate']
                                    # if profit_seek = 'high_above_breakeven'
                                    # set limit price based on profit_seek
                                    # print("selling out due Scalp Exit last_30_avg ")
                                    sell_reason = 'scalp_exit__last_30_avg'
                                    # sell_reasons.append(sell_reason)
                                    # sell_order = True
                                    # order_side = 'sell'
                                    # limit_price = False
                                    profit_seek_value = priceinfo['maker_middle'] + abs(float(honey) * float(run_order['filled_avg_price']))
                                    profit_seek_value = profit_seek_value + (priceinfo['maker_middle'] * .00033)
                                    # print(f'{run_order.get("filled_avg_price")}, {profit_seek_value}')
                                    # if crypto:
                                    #     limit_price = round(profit_seek_value, 1) # current price + (current price * profit seek)
                                    # else:
                                    #     limit_price = round(profit_seek_value, 2) # current price + (current price * profit seek)

                                    # # store message
                                    # if 'queen_orders' in QUEEN['subconscious'].keys():
                                    #     QUEEN['subconscious']['queen_orders'].update({run_order['client_order_id']: {'client_order_id': run_order['client_order_id'],  'waterfall_sellout_msg': f'{"last_30_avg"}{" find exit price"}' }})
                                    # else:
                                    #     QUEEN['subconscious']['queen_orders'] = {run_order['client_order_id']: {'client_order_id': run_order['client_order_id'],  'waterfall_sellout_msg': f'{"last_30_avg"}{" find exit price"}' }}

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
                        if wave_cross_switched__selltobuy and sell_trigbee_datetime <= now_time and time_in_trade_datetime.seconds > 60:
                            # print("SELL ORDER change from Sell to Buy", current_macd, current_macd_time)
                            if macd_gauge['metrics']['buy_cross-0'][5]['avg'] > .5:
                                sell_reason = 'order_rules__macd_cross_selltobuy'
                                sell_reasons.append(sell_reason)
                                sell_order = True
                                order_side = 'sell'
                                limit_price = priceinfo['maker_middle'] if order_type == 'limit' else False
                        
                    """ Close Order Today """
                    if order_rules.get('close_order_today'):
                        if order_rules.get('close_order_today_allowed_timeduration') >= time_to_bell_close and time_in_trade_datetime > timedelta(seconds=60):
                            print("Selling Out, Trade Not Allowed to go past day")
                            sell_reason = 'close_order_today'
                            sell_order = True
                            order_side = 'sell'
                            limit_price = priceinfo['maker_middle'] if order_type == 'limit' else False
                            
                            if time_to_bell_close < 133:
                                print("Selling Out, Trade Not Allowed to go past day")
                                sell_reason = 'close_order_today'
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
                    
                    if sell_reasons:
                        save_order = True
                        QUEEN['queen_orders'].at[client_order_id, 'sell_reason'] = sell_reason
                    
                    if sell_order:

                        makers_middle_price = priceinfo.get('maker_middle')
                        mm_cost = priceinfo.get('maker_middle') * sell_qty
                        order_side = 'sell'
                        sell_qty = check_revrec(sell_qty, revrec, trigname, current_macd, mm_cost, ticker_time_frame, makers_middle_price, close_order_today)
                        
                        if 'queen_wants_to_sell_qty' in run_order.keys():
                            QUEEN['queen_orders'].at[client_order_id, 'queen_wants_to_sell_qty'] = sell_qty
                        
                        if sell_qty > 0:
                            msg = ("Bishop Trying to SELL:", ticker_time_frame, sell_reasons, current_macd, sell_qty, mm_cost)
                            print(msg)
                            logging.info(msg)

                            return {'sell_order': True, 
                            'sell_reason': sell_reason, 
                            'order_side': order_side, 
                            'order_type': order_type, 
                            'sell_qty': sell_qty, 
                            'limit_price': limit_price, 
                            'app_request': app_request,
                            'maker_middle_cost': mm_cost,
                            'save_order': save_order,
                            }
                        else:
                            # print("Bishop DONOT SELL Min.Allocation Stop", ticker_time_frame)
                            return {'sell_order': False}
                    else:
                        return {'sell_order': False}
                
                except Exception as e:
                    print('waterfall error', e, " er line>>", print_line_of_error())

            king_bishop = waterfall_sellout_chain(client_order_id, run_order, order_type, limit_price, sell_trigbee_trigger, stagger_profits, scalp_profits, sell_qty, order_rules=order_rules, QUEEN=QUEEN)
        
            charlie_bee['queen_cyle_times']['om_bishop_block3__om'] = (datetime.now(est) - s_time).total_seconds()

            save_order = True if king_bishop.get('save_order') else False
            if king_bishop['sell_order']:
                if str(king_bishop['sell_qty']) == 'nan':
                    send_email(subject='error checker go see whats up')
                    ipdb.set_trace()

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
                return {'bee_sell': False, 'run_order': run_order}
        
        except Exception as e:
            print_line_of_error("Bishop Selling Error")
            logging.error("Bishop Selling Error")


    def order_management(BROKER, STORY_bee, QUEEN, QUEEN_KING, api, QUEENsHeart, charlie_bee): 

        def async_send_queen_orders__to__kingsBishop_court(queen_orders__dict, revrec): 

            async def get_kingsBishop(session, run_order, priceinfo, revrec):
                async with session:
                    try:
                        king_eval_order = king_bishops_QueenOrder(STORY_bee=STORY_bee, run_order=run_order, priceinfo=priceinfo, revrec=revrec)
                        return king_eval_order  # dictionary
                    except Exception as e:
                        print("kb error ", e, run_order['client_order_id'])
                        logging.error((str(run_order['client_order_id']), str(e)))
                        raise e
            
            async def main_kingsBishop(queen_orders__dict, revrec):
                async with aiohttp.ClientSession() as session:
                    return_list = []
                    tasks = []
                    for c_or_id, queen_order_package in queen_orders__dict.items():
                        run_order = queen_order_package['run_order']
                        priceinfo = queen_order_package['priceinfo']
                        tasks.append(asyncio.ensure_future(get_kingsBishop(session, run_order=run_order, priceinfo=priceinfo, revrec=revrec)))
                    original_pokemon = await asyncio.gather(*tasks)
                    for pokemon in original_pokemon:
                        return_list.append(pokemon)
                    
                    return return_list

            list_of_kingbishop_evals = asyncio.run(main_kingsBishop(queen_orders__dict, revrec))
            return list_of_kingbishop_evals

        def queen_orders_main(BROKER, QUEEN, STORY_bee, QUEEN_KING, charlie_bee):
            # WORKERBEE move info just api?
            def long_short_queenorders(df_active, QUEEN, col_metric='cost_basis_current'):
                long = sum(df_active[df_active['trigname'].str.contains('buy')].get(col_metric))
                short = sum(df_active[~df_active['trigname'].str.contains('buy')].get(col_metric))
                QUEEN['heartbeat']['long'] = round(long)
                QUEEN['heartbeat']['short'] = round(short)

                return True            
            
            try: # App Requests
                s_app = datetime.now(est)
                process_app_requests(QUEEN=QUEEN, QUEEN_KING=QUEEN_KING, request_name='update_queen_order')
                process_app_requests(QUEEN=QUEEN, QUEEN_KING=QUEEN_KING, request_name='update_order_rules')
                charlie_bee['queen_cyle_times']['om_app_req_om'] = (datetime.now(est) - s_app).total_seconds()
            except Exception as e:
                msg=('APP: Queen Order Main FAILED PROCESSING ORDER', print_line_of_error(e))
                logging.error(msg)
            
            try: # Order Loop
                s_loop = datetime.now(est)
                df = QUEEN['queen_orders']
                df['index'] = df.index
                queen_orders__index_dic = dict(zip(df['client_order_id'], df['index']))
                df_active = df[df['queen_order_state'].isin(active_queen_order_states)].copy()
                qo_active_index = df_active['index'].to_list()
                symbols = list(set(df_active['symbol'].to_list()))
                if not symbols:
                    print("No Orders Yet")
                    return True

                long_short_queenorders(df_active, QUEEN, col_metric='cost_basis_current')
                
                s_time = datetime.now(est)
                
                # Price Info Symbols
                snapshot_price_symbols = async_api_alpaca__snapshots_priceinfo(symbols, STORY_bee, api, QUEEN)
                df_priceinfo_symbols = pd.DataFrame(snapshot_price_symbols)
                df_priceinfo_symbols = df_priceinfo_symbols.set_index('ticker', drop=False)
                update_queens_priceinfo_symbols(QUEEN, df_priceinfo_symbols)
                price_info_symbol_time = (datetime.now(est) - s_time).total_seconds()
                print("get priceinfo symbol time: ", price_info_symbol_time)
                
                charlie_bee['queen_cyle_times']['om_priceinfo_api'] = price_info_symbol_time

                s_time_qOrders = datetime.now(est)

                # api # refresh all broker orders which are still pending
                save_b = False 
                for c_order_id in tqdm(qo_active_index):
                    pull_order_status = df_active.at[c_order_id, 'status_q']
                    if c_order_id not in BROKER['broker_orders'].index or pull_order_status != 'filled':
                        order_status = check_order_status(api=api, client_order_id=c_order_id)
                        if order_status:
                            save_b = True
                            update_broker_order_status(BROKER, order_status)
                if save_b:
                    if pg_migration:
                        PollenDatabase.upsert_data(BROKER.get('table_name'), key=BROKER.get('key'), value=BROKER)
                    else:
                        PickleData(BROKER.get('source'), BROKER, console=False)
                broker_time = (datetime.now(est) - s_time_qOrders).total_seconds()
                print("broker time: ", price_info_symbol_time)
                charlie_bee['queen_cyle_times']['om_order_status_api'] = broker_time

                s_time = datetime.now(est)
                queen_orders__dict = {}

                save = False
                for idx in tqdm(qo_active_index):
                    # Queen Order Local Vars
                    run_order = QUEEN['queen_orders'].loc[idx].to_dict()
                    symbol = run_order.get('symbol')
                    crypto = True if symbol in crypto_currency_symbols else False
                    
                    try: 
                        # snapshot prices bar
                        priceinfo = QUEEN['price_info_symbols'].at[symbol, 'priceinfo']
                        
                        order_status = BROKER['broker_orders'].loc[idx].to_dict()

                        # Process Queen Order States
                        run_order = route_queen_order(QUEEN=QUEEN, 
                                                      queen_order=run_order, 
                                                      queen_order_idx=idx, 
                                                      order_status=order_status, 
                                                      priceinfo=priceinfo,
                                                      ) ## send in order_status

                        if float(run_order.get('qty_available')) > 0 and run_order.get('order_trig_sell_stop') == True:
                            release_trig_sell_stop(QUEEN=QUEEN, ticker=symbol, client_order_id=run_order.get('client_order_id'))

                        if stop_queen_order_from_kingbishop(QUEEN_KING, run_order): # false, order_trig_sell_stop or qty_avilable
                            continue

                        ## subconsicous here ###
                        ro_ttf = run_order['ticker_time_frame']
                        if run_order['ticker_time_frame'] not in STORY_bee.keys():
                            # Handle Order if Ticker Stream Turned off I.E. Not in STORY_bee
                            print(f"{ro_ttf} Missing from STORY_bee")

                        king_eval_order = king_bishops_QueenOrder(STORY_bee=STORY_bee, run_order=run_order, priceinfo=priceinfo, revrec=QUEEN['revrec'])
                        
                        if king_eval_order['bee_sell']:
                            exx = execute_sell_order(
                                    api=api, 
                                    QUEEN=QUEEN,
                                    king_eval_order=king_eval_order,
                                    ticker=king_eval_order['bishop_keys']['ticker'], 
                                    ticker_time_frame=king_eval_order['bishop_keys'].get('ticker_time_frame'),
                                    trig=king_eval_order['bishop_keys']['trigname'], 
                                    run_order_idx=queen_orders__index_dic[king_eval_order['bishop_keys']['client_order_id']], 
                                    order_type=king_eval_order['bishop_keys']['order_type'],
                                    crypto=king_eval_order['bishop_keys']['qo_crypto'],
                                )
                            if exx.get('executed'):
                                save = True
                                logging.info(exx.get('msg'))
                                append_queen_order(QUEEN, exx.get('new_queen_order_df'))
                                queen_order_idx = exx.get('new_queen_order_df').index[0]
                                queen_order = QUEEN['queen_orders'].loc[queen_order_idx].to_dict()

                                refresh_broker_account_portolfio(api, QUEEN, account=True, portfolio=True)
                                
                                """ Hold ORDER from being SOLD again until Release Validation """
                                origin_order_idx = exx.get('new_queen_order_df').at[queen_order_idx, 'exit_order_link']
                                QUEEN['queen_orders'].at[origin_order_idx, 'order_trig_sell_stop'] = True
                                update_origin_order_qty_available(QUEEN=QUEEN, run_order_idx=origin_order_idx, RUNNING_CLOSE_Orders=RUNNING_CLOSE_Orders, RUNNING_Orders=RUNNING_Orders)

                                QUEEN['revrec'] = refresh_chess_board__revrec(QUEEN['account_info'], QUEEN, QUEEN_KING, STORY_bee, active_queen_order_states=active_queen_order_states) ## Setup Board

                                god_save_the_queen(QUEENsHeart=QUEENsHeart, QUEEN=QUEEN, charlie_bee=charlie_bee,
                                                save_q=True,
                                                save_rr=True,
                                                save_qo=True,
                                                console=False)
                        elif king_eval_order.get('save_order'):
                            print("Save Order as sell reason exists")
                            god_save_the_queen(QUEENsHeart=QUEENsHeart, QUEEN=QUEEN, charlie_bee=charlie_bee,
                                            save_q=True,
                                            save_qo=True,
                                            console=False)
                    except Exception as e:
                        print('Queen Order Main FAILED PROCESSING ORDER', e, print_line_of_error())
                        send_email(subject="Order Failed", body=str(e))
                        ipdb.set_trace()

                charlie_bee['queen_cyle_times']['om_loop_queen_orders__om'] = (datetime.now(est) - s_time).total_seconds()

                if len(queen_orders__dict) > 0 :
                    pass
                else:
                    return False

                charlie_bee['queen_cyle_times']['full_loop_queenorderS__om'] = (datetime.now(est) - s_loop).total_seconds()
                
                return True
            
            except Exception as e:
                print_line_of_error()
                return False


        #### MAIN ####
        # >for every ticker position join in running-positions to account for total position
        # >for each running position determine to exit the position                
        try:
            # Submitted Orders First
            s_loop = datetime.now(est)
            queen_orders_main(BROKER, QUEEN, STORY_bee, QUEEN_KING, charlie_bee)
            charlie_bee['queen_cyle_times']['om_queen_orders___main'] = (datetime.now(est) - s_loop).total_seconds()
        
        except Exception as e:
            print_line_of_error()
            raise e
        return True


    def refresh_QUEEN_starTickers(QUEEN, STORY_bee, ticker_allowed, story_heartrate=120):
        try:

            now_time = datetime.now(est)

            original_state = QUEEN['heartbeat']['available_tickers']
            avail_tics = []
            for i, v in STORY_bee.items():
                time_delta = (now_time - v['story']['time_state']).total_seconds()
                if time_delta < story_heartrate:
                    avail_tics.append(i)
                else:
                    print(i, "time delta", time_delta)
        
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
    
    
    def hanlde_missing_broker_orders_with_queen_orders(BROKER, QUEEN):

        def add_missing_broker_order_to_queen_orders(QUEEN, broker_order):
            # WORKERBEE append missing broker order new order to queen orders
            return True
        ORDERS_FINAL = init_queenbee(client_user=client_user, prod=prod, orders_final=True).get('ORDERS_FINAL')

        send_em=False
        missing = []
        broker_corder_ids = BROKER['broker_orders'].index # only reconcile latest DAYs orders
        queen_orders = QUEEN['queen_orders'].index.tolist() + ORDERS_FINAL['queen_orders'].index.tolist()
        BROKER['broker_orders']['created_at'] = pd.to_datetime(BROKER['broker_orders']['created_at'], errors='coerce')
        date_ = pd.Timestamp('2024-06-13', tz='America/New_York')
        for c_order_id in broker_corder_ids:
            if c_order_id not in queen_orders:
                # print(c_order_id, " order in broker missing from queen orders add order to queen orders")
                if BROKER['broker_orders'].loc[c_order_id].get('created_at') > date_:
                    missing.append(c_order_id)
                    # print(c_order_id, " order in broker missing from queen orders add order to queen orders")
                    # logging.error(f"{c_order_id} MISSING CLIENT ORDER ID")
                    send_em = True
        # if send_em:
        #     send_email(subject="missing client orders to figure it out", body=str(missing))
        return True


    # BROKER
    def init_broker_orders(api, BROKER):

        init_api_orders_start_date =(datetime.now() - timedelta(days=100)).strftime("%Y-%m-%d")
        init_api_orders_end_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        api_orders = initialize_orders(api, init_api_orders_start_date, init_api_orders_end_date, symbols=False, limit=500)
        queen_orders_closed = api_orders.get('closed')
        queen_orders_open = api_orders.get('open')
        c_order_ids_dict_closed = [vars(queen_orders_closed[n])['_raw'] for n in range(len(queen_orders_closed))]
        c_order_ids_dict_open = [vars(queen_orders_open[n])['_raw'] for n in range(len(queen_orders_open))]
        broker_orders = c_order_ids_dict_closed + c_order_ids_dict_open
        if broker_orders:
            broker_orders = pd.DataFrame(broker_orders).set_index('client_order_id', drop=False)
        else:
            broker_orders = pd.DataFrame()

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

    def reconcile_broker_orders_with_queen_orders(BROKER, api, QUEEN, active_queen_order_states, b_order_init=False):
        
        if len(BROKER['broker_orders']) == 0:
            print("INIT Broker ORDERS")
            b_order_init = True
            BROKER = init_broker_orders(api, BROKER)

        # check for any missing orders
        save_b = False
        df = QUEEN.get('queen_orders')
        df['status_q'] = df['status_q'].fillna('')
        df_active = df[df['queen_order_state'].isin(active_queen_order_states)].copy()
        if len(df_active) > 0 and len(BROKER['broker_orders']) > 0:
            df_active['client_order_id'] = df_active['client_order_id'].fillna('init')
            qo_active_index = df_active['index'].to_list()
            broker_corder_ids = BROKER['broker_orders']['client_order_id'].tolist()
            for client_order_id in qo_active_index:
                if client_order_id not in broker_corder_ids and client_order_id != 'init':
                    print(f"ALERT NEW CLIENT ORDER ID {client_order_id}")
                    order_status = check_order_status(api=api, client_order_id=client_order_id)
                    if order_status:
                        save_b = True
                        update_broker_order_status(BROKER, order_status)
                    if b_order_init:
                        if df_active.at[client_order_id, 'status'] == 'filled':
                            QUEEN['queen_orders'].at[client_order_id, 'status_q'] = 'filled'
                        else:
                            QUEEN['queen_orders'].at[client_order_id, 'status_q'] = 'pending'
        if save_b:
            if pg_migration:
                PollenDatabase.upsert_data(BROKER.get('table_name'), key=BROKER.get('key'), value=BROKER)
            else:
                PickleData(BROKER.get('source'), BROKER, console=False)

        return True
        
        
    ### Close the Day ###

    def close_day__queen(QUEEN, ORDERS_FINAL=False): # clean all FINAL orders bucket 
        def archive_queen(QUEEN):
            # archive_queen_copy
            if pg_migration:
                PollenDatabase.upsert_data(QUEEN.get('table_name'), key=f'previousDAY_{QUEEN.get("key")}', value=QUEEN)
                return True
            else:
                root, name = os.path.split(QUEEN.get('source'))
                archive_ = os.path.join(root, f'{"previousDAY"}__{name}')
                PickleData(archive_, QUEEN, console=True)
        
        # Save Copy of Current day Queen
        archive_queen(QUEEN)
        if not pg_migration:
            ORDERS_FINAL = init_queenbee(client_user=client_user, prod=prod, orders_final=True).get('ORDERS_FINAL')
        
        ## Clean ORders WORKERBE
        def archive_order(QUEEN, ORDERS_FINAL=ORDERS_FINAL):
            try:
                now_time_hash = hash_string(datetime.now(est).strftime("%y-%m-%d %M.%S.%f"))
                
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
                            PollenDatabase.upsert_data(table_name='final_orders', key=f'{now_time_hash}_final_orders', value=dump_orders)
                        
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

        return QUEEN


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
        init_logging(queens_chess_piece=queens_chess_piece, db_root=db_root, prod=prod, loglevel='info')

        # init files needed
        qb = init_queenbee(client_user=client_user, prod=prod, queen=True, queen_king=True, api=True, broker=True, init=True, pg_migration=pg_migration)
        QUEEN = qb.get('QUEEN')
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
                PollenDatabase.upsert_data(QUEEN.get('table_name'), key=QUEEN.get('key'), value=QUEEN)
            else:
                PickleData(QUEEN['dbs'].get('PB_QUEEN_Pickle'), QUEEN)
            sys.exit()

        trading_days = hive_dates(api=api)['trading_days']
        
        reconcile_broker_orders_with_queen_orders(BROKER, api, QUEEN, active_queen_order_states)

        if pg_migration:
            symbols = return_QUEEN_KING_symbols(QUEEN_KING, QUEEN)
            STORY_bee = PollenDatabase.retrieve_all_story_bee_data(symbols).get('STORY_bee')
            # Ticker database of pollenstory ## Need to seperate out into tables 
        else:
            STORY_bee = return_QUEENs__symbols_data(QUEEN=QUEEN, QUEEN_KING=QUEEN_KING, read_storybee=True, read_pollenstory=False).get('STORY_bee') ## async'd func

        # add new keys
        QUEEN_req = add_key_to_QUEEN(QUEEN=QUEEN, queens_chess_piece=queens_chess_piece)
        if QUEEN_req['update']:
            QUEEN = QUEEN_req['QUEEN']
            if pg_migration:
                PollenDatabase.upsert_data(QUEEN.get('table_name'), key=QUEEN.get('key'), value=QUEEN)
            else:
                PickleData(QUEEN['dbs'].get('PB_QUEEN_Pickle'), QUEEN)
        logging.info("My Queen")

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

        ########################################################
        ########################################################
        #############The Infinite Loop of Time #################
        ########################################################
        ########################################################
        ########################################################

        # handle App updates
        process_app_requests(QUEEN, QUEEN_KING, request_name='update_queen_order')
        process_app_requests(QUEEN, QUEEN_KING, request_name='update_order_rules')
        
        if pg_migration:
            charlie_bee = qb.get('CHARLIE_BEE')
            queens_charlie_bee, charlie_bee = init_charlie_bee(db_root, pg_migration=pg_migration, charlie_bee=charlie_bee)
        else:
            queens_charlie_bee, charlie_bee = init_charlie_bee(db_root) # monitors queen order cycles, also seen in heart
        charlie_bee['queen_cycle_count'] = 0
        
        db_keys_df = (pd.DataFrame(PollenDatabase.get_all_keys_with_timestamps(table_name))).rename(columns={0:'key', 1:'timestamp'})
        db_keys_df['key_name'] = db_keys_df['key'].apply(lambda x: x.split("-")[-1])
        db_keys_df = db_keys_df.set_index('key_name')
        pq_qk_lastmod = db_keys_df.at['QUEEN_KING', 'timestamp']


        while True:

            db_keys_df = (pd.DataFrame(PollenDatabase.get_all_keys_with_timestamps(table_name))).rename(columns={0:'key', 1:'timestamp'})
            db_keys_df['key_name'] = db_keys_df['key'].apply(lambda x: x.split("-")[-1])
            db_keys_df = db_keys_df.set_index('key_name')


            s = datetime.now(est)
            # Should you operate now? I thnik the brain never sleeps ?
            mkhrs = return_market_hours(trading_days=trading_days)
            if mkhrs != 'open':
                
                QUEEN = close_day__queen(QUEEN) # cleaning orders to confirm WORKERBEE
                
                
                god_save_the_queen(QUEENsHeart=QUEENsHeart, QUEEN=QUEEN, charlie_bee=charlie_bee,
                                save_q=True,
                                save_rr=True,
                                save_qo=True,
                                save_acct=True,
                                console=True)
                hanlde_missing_broker_orders_with_queen_orders(BROKER, QUEEN)
                print("Queen to ZzzzZZzzzZzzz see you tomorrow")
                break
            
            # if queens_chess_piece.lower() == 'queen': # Rule On High
            seconds_to_market_close = (datetime.now(est).replace(hour=16, minute=0, second=0) - datetime.now(est)).total_seconds()
            
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
                    QUEEN_KING = init_queenbee(client_user=client_user, prod=prod, queen_king=True, pg_migration=pg_migration).get('QUEEN_KING')
                    QUEEN['chess_board'] = QUEEN_KING['chess_board']
            else:
                if str(os.stat(QUEEN['dbs'].get('PB_App_Pickle')).st_mtime) != QUEEN_KING['last_modified']:
                    print("QUEENKING Updated Read New Data")
                    QUEEN_KING = init_queenbee(client_user=client_user, prod=prod, queen_king=True).get('QUEEN_KING')
                    QUEEN['chess_board'] = QUEEN_KING['chess_board']

            # symbol ticker data >>> 1 all current pieces on chess board && all current running orders
            if pg_migration:
                symbols = return_QUEEN_KING_symbols(QUEEN_KING, QUEEN)
                STORY_bee = PollenDatabase.retrieve_all_story_bee_data(symbols).get('STORY_bee')
                # Ticker database of pollenstory ## Need to seperate out into tables 
            else:
                STORY_bee = return_QUEENs__symbols_data(QUEEN=QUEEN, QUEEN_KING=QUEEN_KING, read_storybee=True, read_pollenstory=False).get('STORY_bee') ## async'd func

            QUEEN = refresh_QUEEN_starTickers(QUEEN=QUEEN, STORY_bee=STORY_bee, ticker_allowed=ticker_allowed)
            charlie_bee['queen_cyle_times']['db_refresh'] = (datetime.now(est) - s_time).total_seconds()

            """Account Info"""
            refresh_broker_account_portolfio(api, QUEEN, account=True, portfolio=True)
            acct_info = QUEEN['account_info']
            portfolio = QUEEN['portfolio']

            god_save_the_queen(QUEEN, save_acct=True, console=False)

            charlie_bee['queen_cyle_times']['cc_block1_account'] = (datetime.now(est) - s_time).total_seconds()

            # Read client App Reqquests
            s_time = datetime.now(est)
            process_app_requests(QUEEN=QUEEN, QUEEN_KING=QUEEN_KING, request_name='queen_sleep')
            process_app_requests(QUEEN=QUEEN, QUEEN_KING=QUEEN_KING, request_name='subconscious')
            charlie_bee['queen_cyle_times']['app'] = (datetime.now(est) - s_time).total_seconds()

            # Refresh Board
            revrec = refresh_chess_board__revrec(acct_info, QUEEN, QUEEN_KING, STORY_bee, active_queen_order_states=active_queen_order_states) ## Setup Board

            charlie_bee['queen_cyle_times']['cc_revrec'] = revrec.get('cycle_time')
            QUEEN['revrec'] = revrec
            
            god_save_the_queen(QUEEN, save_rr=True, console=False) # WORKERBEE unessecary SAVING only save whats needed

            # Process All Orders
            s_time = datetime.now(est)
            order_management(BROKER, STORY_bee, QUEEN, QUEEN_KING, api, QUEENsHeart, charlie_bee)
            charlie_bee['queen_cyle_times']['order management'] = (datetime.now(est) - s_time).total_seconds()
            
            god_save_the_queen(QUEEN, QUEENsHeart, charlie_bee, save_qo=True, console=False)

            # Hunt for Triggers
            if seconds_to_market_close > 30:
                s_time = datetime.now(est)
                command_conscience(QUEEN, STORY_bee, QUEEN_KING, api) ##### >   
                charlie_bee['queen_cyle_times']['command conscience'] = (datetime.now(est) - s_time).total_seconds()
            
            beat = (datetime.now(est) - s).total_seconds()

            # charlie_bee['queen_cyle_times']['beat_times'].append({'datetime': datetime.now(est).strftime("%Y-%m-%d %H:%M:%S"), 'beat': beat})
            # charlie_bee['queen_cyle_times']['QUEEN_avg_cycle'].append(beat)
            # charlie_bee['queen_cyle_times']['QUEEN_avg_cycletime'] = sum(charlie_bee['queen_cyle_times']['QUEEN_avg_cycle'])/len(charlie_bee['queen_cyle_times']['QUEEN_avg_cycle'])
            # if pg_migration:
            #     PollenDatabase.upsert_data(table_name, key=charlie_bee.get('key'), value=charlie_bee)
            # else:
            #     PickleData(queens_charlie_bee, charlie_bee, console=False)
            
            charlie_bee['queen_cycle_count'] += 1
            print("Beat", beat, charlie_bee['queen_cycle_count'])
            
            if beat > 23:
                logging.warning((queens_chess_piece, ": SLOW cycle Heart Beat: ", beat, "use price gauge"))
                # print('use price gauge') # (STORY_bee["SPY_1Minute_1Day"]["story"]["price_gauge"])
    
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
        parser.add_argument ('-client_user', default=os.environ.get('admin_user'))
        return parser
    
    parser = createParser()
    namespace = parser.parse_args()
    client_user = namespace.client_user
    prod = namespace.prod
    prod = True if str(prod).lower() == 'true' else False


    while True:
        seconds_to_market_open = (
            datetime.now(est).replace(hour=9, minute=32, second=0) - datetime.now(est)
        ).total_seconds()
        if seconds_to_market_open > 0:
            print(seconds_to_market_open, " ZZzzzZZ")
            time.sleep(3)
        else:
            break


    queenbee(client_user, prod, queens_chess_piece='queen')

"""
The Journey is Hard,
Believe in you,
Believe in God,
Believe
"""
