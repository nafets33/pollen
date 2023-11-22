# QueenBee
import logging
import time
import os
import pandas as pd
import numpy as np
import sys
from dotenv import load_dotenv
import sys
from datetime import datetime, timedelta
import pytz
import ipdb
import asyncio
import aiohttp
from collections import defaultdict, deque
import argparse
from chess_piece.king import kingdom__global_vars, print_line_of_error, master_swarm_KING, return_QUEENs__symbols_data, kingdom__grace_to_find_a_Queen, ReadPickleData, PickleData
from chess_piece.queen_hive import init_charlie_bee, init_queenbee, power_amo, find_symbol, star_ticker_WaveAnalysis, return_queen_orders__query, initialize_orders, refresh_account_info, refresh_chess_board__revrec, init_clientUser_dbroot, process_order_submission, get_best_limit_price, hive_dates, return_alpaca_user_apiKeys, send_email, return_STORYbee_trigbees, init_logging, convert_to_float, order_vars__queen_order_items, init_pollen_dbs, story_view, logging_log_message, return_alpc_portolio, return_market_hours, pollen_themes, check_order_status,  timestamp_string, submit_order, return_timestamp_string, add_key_to_QUEEN


""" ideas 
if prior day abs(change) > 1 ignore ticker for the day!
"""

pd.options.mode.chained_assignment = None
est = pytz.timezone("US/Eastern")
utc = pytz.timezone('UTC')

# ###### GLOBAL # ######
KING, users_allowed_queen_email, users_allowed_queen_emailname__db = kingdom__grace_to_find_a_Queen()
king_G = kingdom__global_vars()
ARCHIVE_queenorder = king_G.get('ARCHIVE_queenorder') # ;'archived'
active_order_state_list = king_G.get('active_order_state_list') # = ['running', 'running_close', 'submitted', 'error', 'pending', 'completed', 'completed_alpaca', 'running_open', 'archived_bee']
active_queen_order_states = king_G.get('active_queen_order_states') # = ['submitted', 'accetped', 'pending', 'running', 'running_close', 'running_open']
CLOSED_queenorders = king_G.get('CLOSED_queenorders') # = ['running_close', 'completed', 'completed_alpaca']
RUNNING_Orders = king_G.get('RUNNING_Orders') # = ['running', 'running_open']
RUNNING_OPEN = [RUNNING_Orders[-1]]
RUNNING_CLOSE_Orders = king_G.get('RUNNING_CLOSE_Orders') # = ['running_close']

# crypto
crypto_currency_symbols = ['BTCUSD', 'ETHUSD', 'BTC/USD', 'ETH/USD']
coin_exchange = "CBSE"
# misc
exclude_conditions = [
    'B','W','4','7','9','C','G','H','I','M','N',
    'P','Q','R','T','V','Z'
] # 'U'



def generate_client_order_id(QUEEN, ticker, trig, sellside_client_order_id=False): # generate using main_order table and trig count
    main_orders_table = QUEEN['queen_orders']
    temp_date = datetime.now(est).strftime("%y-%m-%d %M.%S.")
    
    if sellside_client_order_id:
        main_trigs_df = main_orders_table[main_orders_table['client_order_id'] == sellside_client_order_id].copy()
        trig_num = len(main_trigs_df) + 1
        order_id = f'{"close__"}{trig_num}-{sellside_client_order_id}-{temp_date}'
    else:
        main_trigs_df = main_orders_table[(main_orders_table['trigname']==trig) & (main_orders_table['exit_order_link'] != 'False')].copy()
        
        trig_num = len(main_trigs_df) + 1
        order_id = f'{"run__"}{ticker}-{trig}-{trig_num}-{temp_date}'

    if order_id in QUEEN['client_order_ids_qgen']: # WORKERBEE check if also in api order client order ID
        msg = {"generate client_order_id()": "client order id already exists change"}
        print(msg)
        logging.error(msg)
        # q_l = len(QUEEN['client_order_ids_qgen'])
        mill_s = datetime.now(est).microsecond
        order_id = f'{order_id}{"_qgen_"}{mill_s}'
    
    return order_id


def submit_order_validation(QUEEN, ticker, qty, side, portfolio, run_order_idx=False):
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
        
        position = float(portfolio[ticker]['qty_available']) if portfolio.get(ticker) else 0

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
                return func_return(qty, qty_correction=qty_correction, log=True, log_msg=msg)
            else:
                msg = ('Buy Order Validated')
                return func_return(log=True, log_msg=msg)
        elif side == 'sell': # sel == sell
            # print("check portfolio has enough shares to sell")
            if ticker not in portfolio.keys():
                msg = f'submit order validation({ticker}), MISSING_TICKER ARCHVING ORDER'
                return func_return(queen_order_state='completed_alpaca', stop_order=True, log_msg=msg, log=True)
            elif position > 0 and position < qty: # long
                msg = (f'submit order validation() {ticker} #of shares avail: {position} >>> NOT enough shares avail to sell, updating sell qty')            
                return func_return(qty=position, qty_correction=True, log_msg=msg, log=True)
            elif position < 0 or (position - qty) < 0:
                msg = ("ARCHVING ORDER, SHORTING, Scenario Not Added", QUEEN['queen_orders'].at[run_order_idx, 'ticker_time_frame'])
                return func_return(qty, queen_order_state='completed_alpaca', stop_order=True, log_msg=msg, log=True)
            else:
                msg = ("Sell Order Validated")
                return func_return(log_msg=msg, log=True)

    except Exception as e:
        print("order validaiton", e)
        print_line_of_error()
        sys.exit()


def return_closing_orders_df(QUEEN, exit_order_link): # returns linking order
    df = QUEEN['queen_orders']
    origin_closing_orders = df[
        (df['exit_order_link'] == exit_order_link) 
                               & 
        (df['queen_order_state'].isin(CLOSED_queenorders))].copy()
    
    if len(origin_closing_orders) > 0:
        return origin_closing_orders
    else:
        return ''


def update_origin_order_qty_available(QUEEN, run_order_idx, RUNNING_CLOSE_Orders, RUNNING_Orders):
    try:
        # Return QueenOrder
        queen_order = QUEEN['queen_orders'].loc[run_order_idx].to_dict()
        if queen_order['queen_order_state'] in RUNNING_Orders:
            closing_dfs = return_closing_orders_df(QUEEN=QUEEN, exit_order_link=queen_order['client_order_id'])
            if len(closing_dfs) > 0: # WORKERBEE num convert NOT necesary REMOVE
                closing_dfs['qty'] = closing_dfs['qty'].apply(lambda x: convert_to_float(x))
                closing_dfs['filled_qty'] = closing_dfs['filled_qty'].apply(lambda x: convert_to_float(x))
                closing_dfs['filled_avg_price'] = closing_dfs['filled_avg_price'].apply(lambda x: convert_to_float(x))

                # validate qty
                if sum(closing_dfs['filled_qty']) > float(queen_order['qty']):
                    print("wtf closing > origin order", queen_order['client_order_id'])
                    pass

                # update queen order
                QUEEN['queen_orders'].at[run_order_idx, 'qty_available'] = float(queen_order['filled_qty']) - sum(closing_dfs['qty'])
                QUEEN['queen_orders'].at[run_order_idx, 'qty_available_pending'] = float(queen_order['filled_qty']) - sum(closing_dfs['filled_qty'])
            else:
                QUEEN['queen_orders'].at[run_order_idx, 'qty_available'] = float(queen_order['filled_qty'])
        elif queen_order['queen_order_state'] in RUNNING_CLOSE_Orders:
            QUEEN['queen_orders'][run_order_idx]['qty_available'] = float(queen_order['qty']) - float(queen_order['filled_qty'])
        elif queen_order['queen_order_state'] in CLOSED_queenorders:
            print("Order Closed and will Complete in later function Consider Closing HERE????")
        else:
            print('Update Origin wtf are you?', queen_order['client_order_id'], queen_order['queen_order_state'])
        
        return True
    except Exception as e:
        print(e, print_line_of_error())
        return False


def append_queen_order(QUEEN, new_queen_order_df):
    QUEEN['queen_orders'] = pd.concat([QUEEN['queen_orders'], new_queen_order_df], axis=0) # , ignore_index=True
    QUEEN['queen_orders']['client_order_id'] = QUEEN['queen_orders'].index
    return True


def execute_order(api, QUEEN, blessing, king_resp, king_eval_order, side, order_type, trading_model, ticker, ticker_time_frame, trig, run_order_idx=False, crypto=False, app_request=False, wave_amo=False, limit_price=False):
    try:
        tic, tframe, tperiod = ticker_time_frame.split("_")
        star = f'{tframe}_{tperiod}'
        
        # logging.info({'ex_order()': ticker_time_frame})
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

        def update__validate__qty(crypto, current_price, limit_price, wave_amo):
            if crypto:
                limit_price = round(limit_price) if limit_price else limit_price
                qty_order = float(round(wave_amo / current_price, 8))
            else:
                limit_price = round(limit_price, 2) if limit_price else limit_price
                qty_order = float(round(wave_amo / current_price, 0))

                if not isinstance(qty_order, float):
                    ipdb.set_trace()

            return limit_price, qty_order

        def validate_wave_amo(wave_amo):
            if type(wave_amo) == float:
                return True
            else:
                print("wtf wave")
    
        # portfolio = return_alpc_portolio(api)['portfolio']
        portfolio = QUEEN.get('portfolio')
        
        # priceinfo = return_snap_priceinfo__pollenData(ticker=ticker)
        snap = api.get_snapshot(ticker) if crypto == False else api.get_crypto_snapshot(ticker, exchange=coin_exchange)

        # get latest pricing
        priceinfo_order = {'price': snap.latest_trade.price, 'bid': snap.latest_quote.bid_price, 'ask': snap.latest_quote.ask_price, 'bid_ask_var': snap.latest_quote.bid_price/snap.latest_quote.ask_price}
        # priceinfo_order = {'price': priceinfo['current_price'], 'bid': priceinfo['current_bid'], 'ask': priceinfo['current_ask']}
        if king_resp:
            side = 'buy'
            # if app order get order vars its way
            if app_request:
                # up pack order vars
                side = king_resp['side']
                order_type = king_resp['type']
                wave_amo = king_resp['wave_amo']
                limit_price = False
                trading_model = king_resp['order_vars']

            order_vars = blessing
            limit_price = limit_price if limit_price != False else False
            limit_price, qty_order = update__validate__qty(crypto=crypto, current_price=priceinfo_order['price'], limit_price=limit_price, wave_amo=wave_amo)
            if limit_price:
                order_type = 'limit'
            # Client Order Id
            client_order_id__gen = generate_client_order_id(QUEEN=QUEEN, ticker=ticker, trig=trig)
            
            # Submit Order
            order_val = submit_order_validation(QUEEN=QUEEN, ticker=ticker, qty=qty_order, side=side, portfolio=portfolio, run_order_idx=run_order_idx)                    

            if order_val.get('log'):
                logging.warning(order_val.get('log_msg'))

            if order_val.get('qty_correction'):
                logging.warning(order_val.get('log_msg'))
                # QUEEN['queen_orders'].at[run_order_idx, 'validation_correction'] = 'true' # WORKERBEE handle later
                qty_order = order_val.get('qty')

            order_submit = submit_order(api=api, 
                                        symbol=ticker, 
                                        type=order_type, 
                                        qty=qty_order, 
                                        side=side, 
                                        client_order_id=client_order_id__gen, 
                                        limit_price=limit_price) # buy
            if 'error' in order_submit.keys():
                print(f'{ticker_time_frame} Order Failed log in Hive, Log so you can make this only a warning')
                # QUEEN['heartbeat']['critical'] = QUEEN['heartbeat']['critical'].update({ticker_time_frame: 'execute order failed'})
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
            
            msg = (f'ExOrder {trig} {ticker_time_frame} {round(wave_amo,2):,}')

            return{'executed': True, 'msg': msg, 'new_queen_order_df': new_queen_order_df, 'priceinfo_order': priceinfo_order}
        
        elif king_eval_order:
            side = 'sell'
            # print("bee_sell")
            run_order_client_order_id = QUEEN['queen_orders'].at[run_order_idx, 'client_order_id']
            order_vars = king_eval_order['order_vars']

            # close out order variables
            sell_qty = float(king_eval_order['order_vars']['sell_qty']) # float(order_obj['filled_qty'])
            # q_side = king_eval_order['order_vars']['order_side'] # 'sell' Unless it short then it will be a 'buy'
            # q_type = king_eval_order['order_vars']['order_type'] # 'market'
            # sell_reason = king_eval_order['order_vars']['sell_reason']
            # limit_price = king_eval_order['order_vars']['limit_price']

            # Generate Client Order Id
            client_order_id__gen = generate_client_order_id(QUEEN=QUEEN, ticker=ticker, trig=trig, sellside_client_order_id=run_order_client_order_id)

            limit_price, sell_qty = update__sell_qty(crypto, limit_price, sell_qty)

            # Validate Order
            order_val = submit_order_validation(QUEEN=QUEEN, ticker=ticker, qty=sell_qty, side=side, portfolio=portfolio, run_order_idx=run_order_idx)

            if order_val.get('log'):
                logging.error(order_val.get('log_msg'))
            if order_val.get('stop_order'):
                QUEEN['queen_orders'].at[run_order_idx, 'queen_order_state'] = 'completed_alpaca'
                return {}
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
                QUEEN['heartbeat']['critical'] = QUEEN['heartbeat']['critical'].update({ticker_time_frame: 'execute order failed'})
                return {'executed': False}


            send_close_order = vars(send_close_order['order'])['_raw']
                                
            if limit_price:
                print("seeking Honey?")
            
            if 'borrowed_funds' not in order_vars.keys():
                order_vars['borrowed_funds'] = False
            
            # Order Vars 
            new_queen_order_df = process_order_submission(trading_model=False,
            order=send_close_order, 
            order_vars=order_vars, 
            trig=trig, 
            exit_order_link=run_order_client_order_id,
            symbol=ticker,
            ticker_time_frame=ticker_time_frame,
            star=star,
            priceinfo=priceinfo_order)

            msg = (f'ExOrder SELL {trig} {ticker_time_frame}')

            return{'executed': True, 'msg': msg, 'new_queen_order_df': new_queen_order_df, 'priceinfo_order': priceinfo_order}

    except Exception as e:
        print("Error Ex Order..Full Failure" , ticker_time_frame, e, print_line_of_error())
        if 'critical' not in QUEEN['heartbeat'].keys():
            QUEEN['heartbeat']['critical'] = {ticker_time_frame: 'execute order failed'}
        else:
            QUEEN['heartbeat']['critical'].update({ticker_time_frame: 'execute order failed'})
        # sys.exit()


#### QUEENS ORDERS ### OrderMangement ####
def sell_order__var_items(sell_order, sell_reason, order_side, limit_price):
    return {
        'sell_order': sell_order,
        'sell_reason': sell_reason,
        'order_side': order_side,
        'limit_price': limit_price,
    }

### STAR UTILS

def queenbee(client_user, prod, queens_chess_piece='queen'):


    # prod = True if str(prod).lower() == 'true' else False

    if client_user not in users_allowed_queen_email: ## this db name for client_user # stefanstapinski
        print("failsafe away from user running function")
        send_email(recipient='stapinski89@gmail.com', subject="NotAllowedQueen", body=f'{client_user} you forgot to same something')
        sys.exit()


    def update_queen_order(QUEEN, update_package):
        # update_package client_order id and field updates {client_order_id: {'queen_order_status': 'running'}}
        try:
            save = False
            df = QUEEN['queen_orders']
            for c_order_id, package in update_package['queen_order_updates'].items():
                # df_ = df[df['client_order_id'] == c_order_id].copy()
                # order_idx = df_.iloc[-1].name
                for field_, new_value in package.items():
                    try:
                        QUEEN['queen_orders'].at[c_order_id, field_] = new_value
                        save = True
                    except Exception as e:
                        print(e, 'failed to update QueenOrder')
                        logging.critical({'msg': 'failed to update queen orders', 'error': e, 'other': (field_, new_value)})
                        QUEEN['queens_messages'].update({c_order_id: {'date': return_timestamp_string(), 'error': e, 'updates': (field_, new_value)}})
            if save:
                PickleData(QUEEN['dbs'].get('PB_QUEEN_Pickle'), QUEEN)
        except Exception as e:
            print(e, print_line_of_error())
            logging.CRITICAL({'error': e, 'msg': 'update queen order', 'update_package': update_package})
            QUEEN['queens_messages'].update({'CRITICAL_QueenOrdersUpdates': {'date': return_timestamp_string(), 'error': e, 'update_package': update_package}})
        return True

    def update_queen_order_order_rules(QUEEN, update_package):
        try:
            save = False
            for c_order_id, package in update_package['queen_order_updates'].items():
                for field_, new_value in package.items():
                    try:
                        # if field_ in QUEEN['queen_orders'].at[c_order_id, 'order_rules'].keys():
                        QUEEN['queen_orders'].at[c_order_id, 'order_rules'].update({field_: new_value})
                        save = True
                        logging.info((f'{field_} updated to {new_value}'))
                    except Exception as e:
                        print(e, 'failed to update QueenOrder')
                        logging.critical({'msg': 'failed to update queen orders', 'error': e, 'other': (field_, new_value)})
            if save:
                PickleData(QUEEN['dbs'].get('PB_QUEEN_Pickle'), QUEEN)
        except Exception as e:
            print(e, print_line_of_error())
            logging.CRITICAL({'error': e, 'msg': 'update queen order', 'update_package': update_package})
            QUEEN['queens_messages'].update({'CRITICAL_QueenOrdersUpdates': {'date': return_timestamp_string(), 'error': e, 'update_package': update_package}})
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
                        # PickleData(QUEEN['dbs'].get('PB_QUEEN_Pickle'), QUEEN)
                        god_save_the_queen(QUEEN, save_q=True, save_qo=True)
                        return {'app_flag': True, 'sell_order': True, 'sell_qty': sell_qty, 'type': o_type, 'side': side, 'limit': limit}
                else:
                    pass

        return {'app_flag': False}

    def process_app_requests(QUEEN, QUEEN_KING, request_name, archive_bucket=None):
        app_requests__bucket = 'app_requests__bucket'
        try:
            if request_name == "buy_orders": # ok
                # archive_bucket = 'buy_orders_requests'
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
            
            elif request_name == "update_queen_order": # ok
                app_order_base = [i for i in QUEEN_KING[request_name]]
                if app_order_base:
                    for app_request in app_order_base:
                        if app_request['app_requests_id'] in QUEEN['app_requests__bucket']:
                            continue
                            # return {'app_flag': False}
                        else:
                            QUEEN['app_requests__bucket'].append(app_request['app_requests_id'])
                            print("queen update order trigger gather", app_request['queen_order_updates'])
                            update_queen_order(QUEEN=QUEEN, update_package=app_request)
                            
                            return {'app_flag': True}
                else:
                    return {'app_flag': False}

            elif request_name == "queen_sleep": # redo Don't save App
                app_order_base = [i for i in QUEEN_KING[request_name]]
                if len(app_order_base) == 0:
                    return {'app_flag': False}
                queensleep = False
                for app_request in app_order_base: # if len(app_order_base) > 1:
                    if app_request['app_requests_id'] in QUEEN['app_requests__bucket']:
                        return {'app_flag': False}
                    queensleep = True
                    QUEEN['app_requests__bucket'].append(app_request['app_requests_id'])                
                if queensleep:
                    print("exiting QUEEN stopping queen")
                    PickleData(QUEEN['dbs'].get('PB_QUEEN_Pickle'), QUEEN)
                    sys.exit()

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
                            
                            return {'app_flag': True}
            elif request_name == "subconscious": # ?
                # archive_bucket = 'queen_controls_requests'
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


    def king_knights_requests(QUEEN, STORY_bee, revrec, tm_trig, trigbee, ticker_time_frame, trading_model, trig_action, app_trig, crypto=False):
        s_ = datetime.now(est)
        """answer all questions for order to be placed, compare against the rules"""
        # measure len of trigbee how long has trigger been there?
        # Std Deivation from last X trade prices
        # Jump on wave if NOT on Wave?
        # collective BUY only when story MACD tier aligns to certian power NEW THEME
        # Sell on MACD Tier distance (how many tiers have we crossed increment to sell at)  NEW THEME
        # collective MACD triggers? Family Triggers, weights on where trigger is
        # accept trigbee tier when deviation from vwap?
        # did your Previous Trigger make money? 
        # Or did the previous wave go from + to - or vice versa, OR what was the wave frequency? 
        

        """ buy is in range wave_n history, i.e. when buy is in range wave_n blocktime"""
        # wave_frequency_profits = profits grouped by blocktime
        # wave_frequency_profits_today
        # wave_frequency_wave_n = profits grouped by star wave_n
        # how many vwap crosses have their been and whats been the frequency
        # take chances buys and sells, allowed default 3, 1 for each blocktime

        # Scenario: buys: :afternoon: if morning > x% then load up vs load down
        # Scenario: sells: :afternoon: if morning > x% & lunch > x% then load up vs load down (look for a quick heavy pull)
        # Scenarios: buys: morning: has push been made? which direction, from vwap

        ####### Allow Stars to borrow power if cash available ###### its_morphin_time
        # borrow_cashed needs to be sold within timeframe OR it can keep it based on confidence
        
        def knight_request_recon_portfolio():
            # debate if we should place a new order based on current portfolio trades
            pass
        def trade_Scenarios(trigbee, wave_amo):
            # Create buying power upgrades depending on the STARS waves
            
            # Current Star Power? the Incremate of macd_tier, macd_state for a given Star

            # if "buy_cross-0" == trigbee:
            #     pass

            return True
        def proir_waves():
            # return fequency of prior waves and statement conclusions
            return True
        def its_morphin_time(QUEEN_KING, QUEEN, trigbee, theme, tmodel_power_rangers, ticker, stars_df):
            try:
                # Map in the color on storyview
                power_rangers_universe = ['mac_ranger', 'hist_ranger']
                stars_colors_d = {ranger: dict(zip(stars_df['star'], stars_df[ranger])) for ranger in power_rangers_universe}
                # ticker = 'SPY' # default
                ticker_token = f'{ticker}{"_"}'
                
                # color = .5 # for every star we want both mac and hist power_rangers_universe  
                if 'buy' in trigbee:
                    wave_type = 'buy_wave'
                else:
                    wave_type = 'sell_wave'
                
                """ Power Up """ # for every models stars, return stars value by its tier color
                power_up = {ranger: 0 for ranger in power_rangers_universe}
                for star, v in tmodel_power_rangers.items(): # 1m 5m, 3M
                    if v == 'active' or v == True:
                        for ranger in power_rangers_universe:
                            PowerRangerColor = stars_colors_d[ranger][f'{ticker_token}{star}'] # COLOR
                            power_up[ranger] += float(QUEEN_KING['king_controls_queen']['power_rangers'][star][ranger][wave_type][theme][PowerRangerColor]) # star-buywave-theme

                return power_up
            except Exception as e:
                print("power up failed ", e, print_line_of_error())
                return {ranger: 0 for ranger in power_rangers_universe}

        
        def kings_blessing_checks(king_order_rules, trig_action_num, time_delta, macd_tier, trigbee, crypto):

            if "ignore_trigbee_in_macdstory_tier" in king_order_rules.keys():
                if macd_tier in king_order_rules.get("ignore_trigbee_in_macdstory_tier"):
                    # print(f'{ticker_time_frame} Ignore Trigger macd_tier: , {macd_tier}')
                    return False #(f'{ticker_time_frame} Ignore Trigger macd_tier: , {macd_tier}')
            elif trig_action_num > 0:
                if time_delta < timedelta(minutes=king_order_rules['doubledown_timeduration']):
                    # print("Trig In Action time delta not Met for Double Down")
                    return ("Trig In Action time delta not Met for Double Down")
            elif 'sell' in trigbee: # == 'sell_cross-0':
                if crypto:
                    return (f'crypto not allowed')
            else:
                return False

        def blessing_check(acct_info, wave_amo, QUEEN_KING):
            if wave_amo > acct_info.get('daytrading_buying_power'):
                print("day trade buying power exceeded")
                wave_amo = acct_info.get('daytrading_buying_power') - wave_amo
                if wave_amo <= 0:
                    print("buying power is depleted")
                    conscience_update(QUEEN, thought_dict={'msg': 'buying power is depleted'})

                    return False

            return True


        def trig_in_action_waterfall(ticker_time_frame, tm_trig, trigbee, symbol, trig_action_num, time_delta, trading_model_theme, 
                                     king_order_rules, wave_amo, maker_middle, order_side='buy', borrow_qty=0, borrowed_funds=False, 
                                     kings_blessing=True, 
                                     app_trig={'trig': False, 'ready_buy': False, 'x_buy': False}, 
                                     info="returns kings_blessing, order_vars"):
            ready_buy = True if app_trig.get('ready_buy') == True else False

            if trig_action_num > 0:
                if time_delta > timedelta(minutes=king_order_rules['doubledown_timeduration']) or app_trig.get('trig') == True:
                    print("Trig In Action Double Down Trade")
                    kings_blessing = True
                    order_vars = order_vars__queen_order_items(trading_model=trading_model_theme, 
                                                                king_order_rules=king_order_rules, 
                                                                order_side='buy', 
                                                                wave_amo=wave_amo, 
                                                                maker_middle=maker_middle, 
                                                                origin_wave=current_wave, 
                                                                power_up_rangers=power_up_amo, 
                                                                ticker_time_frame_origin=ticker_time_frame, 
                                                                double_down_trade=True, 
                                                                wave_at_creation=current_macd_cross__wave,
                                                                symbol=symbol,
                                                                trigbee=trigbee,
                                                                tm_trig=tm_trig,
                                                                borrowed_funds=borrowed_funds,
                                                                ready_buy=ready_buy,
                                                                assigned_wave=current_macd_cross__wave,
                                                                borrow_qty=borrow_qty,
                                                                )
                else:
                    # print(ticker_time_frame, "double down delta HAULT")
                    kings_blessing = False
                    order_vars = None
            else:
                kings_blessing = True
                order_vars = order_vars__queen_order_items(trading_model=trading_model_theme, 
                                                            king_order_rules=king_order_rules, 
                                                            order_side='buy', 
                                                            wave_amo=wave_amo, 
                                                            maker_middle=maker_middle, 
                                                            origin_wave=current_wave, 
                                                            power_up_rangers=power_up_amo, 
                                                            ticker_time_frame_origin=ticker_time_frame, 
                                                            double_down_trade=False, 
                                                            wave_at_creation=current_macd_cross__wave,
                                                            symbol=symbol,
                                                            trigbee=trigbee,
                                                            tm_trig=tm_trig,
                                                            borrowed_funds=borrowed_funds,
                                                            ready_buy=ready_buy,
                                                            assigned_wave=current_macd_cross__wave,
                                                            borrow_qty=borrow_qty,
                                                            )
            if kings_blessing:
                print("Sending Blessing")

            return kings_blessing, order_vars
        
        waveview = revrec.get('waveview')
        # def last_time_tr
        try:

            # vars
            ticker, tframe, tperiod = ticker_time_frame.split("_")
            star_time = f'{tframe}{"_"}{tperiod}'
            
            ticker_priceinfo = QUEEN['price_info_symbols'].at[ticker, 'priceinfo']
            # RevRec # Allocation Star allowed df_qcp, df_ticker, df_stars
            # qcp_total_budget = revrec['df_qcp'].loc[qcp].get("qcp_total_budget")
            ticker_total_budget = revrec['df_ticker'].loc[ticker].get("ticker_total_budget")
            ticker_borrow_budget = revrec['df_ticker'].loc[ticker].get("ticker_borrow_budget")
            star_total_budget = revrec['df_stars'].loc[ticker_time_frame].get("star_total_budget")
            star_total_borrow = revrec['df_stars'].loc[ticker_time_frame].get("star_borrow_budget")
            star_total_budget_remaining = revrec['df_stars'].loc[ticker_time_frame].get("remaining_budget")
            star_total_borrow_remaining = revrec['df_stars'].loc[ticker_time_frame].get("remaining_budget_borrow")
            symbol_total_budget_remaining = revrec['df_ticker'].loc[ticker].get("ticker_remaining_budget")
            symbol_total_borrow_remaining = revrec['df_ticker'].loc[ticker].get("ticker_remaining_borrow")

            kings_blessing = False

            # how many trades have we completed today? whats our total profit loss with wave trades
            # should you override your original order rules?

            # if star_total_budget_remaining == 0:
            #     # print(f'{ticker_time_frame} all budget used up')
            #     if ticker_time_frame not in QUEEN['queens_messages'].keys():
            #         QUEEN['queens_messages'][ticker_time_frame] = {'remaining_budget': f'{ticker_time_frame} all budget used up'}
            #     else:
            #         QUEEN['queens_messages'][ticker_time_frame].update({'remaining_budget': f'{ticker_time_frame} all budget used up'})
            #     return {'kings_blessing': False}

            # if star_total_budget_remaining == 0 and star_total_borrow_remaining == 0:
            #     return {'kings_blessing': False}
            
            # trade scenarios / power ups / 
            trig_action_num = len(trig_action) # get trading model amount allowed?
            now_time = datetime.now(est)
            if trig_action_num != 0:
                trig_action.iloc[-1]['datetime']
                time_delta = now_time - trig_action.iloc[-1]['datetime']
            else:
                time_delta = now_time - datetime.now(est)

            def knights_wave_amo(trigbee, wave_amo, revrec, ticker_time_frame, king_order_rules, star_total_budget_remaining, symbol_total_budget_remaining):
                alloc_deploy = (revrec['waveview'].at[ticker_time_frame, 'allocation'] *-1)
                if 'buy' in trigbee: # == 'buy_cross-0':

                    macd_rate = macd_tier / 8
                    if macd_rate <0: 
                        macd_rate = (macd_tier * -1)
                    
                    if macd_tier <=-2:
                        # print("powerup ", ticker_time_frame)
                        # logging.info(("powerup ", ticker_time_frame, "", macd_tier))
                        wave_amo = star_total_budget_remaining * .3
                    if macd_tier <=-3:
                        # print("powerup ", ticker_time_frame)
                        # logging.info(("powerup ", ticker_time_frame, "", macd_tier))
                        wave_amo = star_total_budget_remaining * .5
                    if macd_tier <=-5:
                        # print("powerup ", ticker_time_frame)
                        # logging.info(("powerup ", ticker_time_frame, "", macd_tier))
                        wave_amo = star_total_budget_remaining * .8
                    
                    if macd_tier <=-6:
                        # print("powerup ", ticker_time_frame)
                        # logging.info(("powerup ", ticker_time_frame, "", macd_tier))
                        wave_amo = wave_amo + symbol_total_budget_remaining * .3
                        king_order_rules.update({'close_order_today': True, 'stagger_profits_tiers':2})


                elif 'sell' in trigbee: # == 'sell_cross-0':
                    if crypto:
                        return {'kings_blessing': False}
                    if macd_tier >=2:
                        # print("powerup ", ticker_time_frame)
                        logging.info(("powerup ", ticker_time_frame, "", macd_tier))
                        wave_amo = star_total_budget_remaining * .3
                    if macd_tier >=5:
                        # print("powerup ", ticker_time_frame)
                        logging.info(("powerup ", ticker_time_frame, "", macd_tier))
                        wave_amo = wave_amo + symbol_total_budget_remaining * .3

                if wave_amo < alloc_deploy:
                    print(f'Wave Amo < then Allocation, Overwriding to Allocation Amount  {alloc_deploy}')
                    # logging.warning((f'Wave Amo < then Allocation, Overwriding to Allocation Amount  {(revrec["waveview"].at[ticker_time_frame, "allocation"] *-1)}'))
                    wave_amo = alloc_deploy


                return wave_amo, king_order_rules

            # not used  (how to allocate the trigger trade?): distance to vwamp, power of shortterm, power of mid term, power of long term
            # distance_to_vwap = STORY_bee[ticker_time_frame].get("vwap_deviation_pct")
            # distance_to_rsi = STORY_bee[ticker_time_frame].get("rsi_deviation_pct")
            # macd_tier (color) + distance_to_vwap + distance_to_rsi
            # long term wave %, mid term wave %, shoert term wave %
            # power up modes (colors together black and black, black and white)

            # macd_signal_wave_deviation


            # Theme
            theme = QUEEN_KING['king_controls_queen']['theme'] # what is the theme?
            trading_model_theme = trading_model.get('theme')
            trading_model_star = trading_model['stars_kings_order_rules'].get(f'{tframe}_{tperiod}')

            """Stars Forever Be in Heaven"""
            # Story View, Wave Analysis
            story_views = story_view(STORY_bee=STORY_bee, ticker=ticker)
            charlie_bee['queen_cyle_times']['cc_symbol_storyview'] = story_views.get('cycle_time')
            
            stars_df = story_views['df']
            stars_df = stars_df.set_index("star")
            macd_tier = stars_df.loc[ticker_time_frame].get('current_macd_tier')

            s_ = datetime.now(est)
            current_macd_cross__wave = star_ticker_WaveAnalysis(STORY_bee=STORY_bee, ticker_time_frame=ticker_time_frame)['current_wave']
            current_wave = star_ticker_WaveAnalysis(STORY_bee=STORY_bee, ticker_time_frame=ticker_time_frame)['current_active_waves'][tm_trig]
            current_wave_blocktime = current_wave['wave_blocktime']
            charlie_bee['queen_cyle_times']['cc_symbol_waveAnalysis'] = (datetime.now(est) - s_).total_seconds()

            # Trading Model Vars
            # Global switch to user power rangers at ticker or portfolio level 
            tmodel_power_rangers = trading_model['stars_kings_order_rules'][star_time].get('power_rangers')
            if trading_model_theme == 'story__AI':
                print('story ai update KORs with lastest from story_view()')
            king_order_rules = trading_model['stars_kings_order_rules'][star_time]['trigbees'][tm_trig][current_wave_blocktime]
            maker_middle = ticker_priceinfo['maker_middle'] if str(trading_model_star.get('trade_using_limits')) == 'true' else False

            # update revisit trade at intervals "revisit_trade_frequency"
            # king_order_rules.update({"revisit_trade_frequency": expected_maxprofit})

            # power_up_amo = its_morphin_time(QUEEN_KING=QUEEN_KING, QUEEN=QUEEN, trigbee=trigbee, theme=theme, tmodel_power_rangers=tmodel_power_rangers, ticker=ticker, stars_df=stars_df)
            # print("POWERUP !!!!! ", power_up_amo)
            # wave_amo = theme_amo + power_up_amo['mac_ranger'] + power_up_amo['hist_ranger']
            power_up_amo = power_amo()

            king_check = kings_blessing_checks(king_order_rules, trig_action_num, time_delta, macd_tier, trigbee, crypto)
            if king_check:
                print(king_check)
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
            
            if app_trig.get('ready_buy'):
                print("KNIGHT ready buy")
                king_order_rules.update({'ready_buy': True, 'sell_trigbee_trigger_timeduration':ready_buy_star_timeduration_delay(star_time)})
            ready_buy = True if app_trig.get('ready_buy') else False
            overrule_power = king_order_rules.get('overrule_power')
            overrule_power = 0 if king_order_rules.get('overrule_power') is None else overrule_power

            symbol = find_symbol(QUEEN, ticker, trading_model, trigbee).get('ticker')
            # index_X_tier = True if etf_long_tier == False or etf_inverse_tier == False else False
            ticker, tframe, tperiod = ticker_time_frame.split("_")

            # def waterfall_knight_buy_chain(trigbees, trading_model):
            #     return False
            blessings = {'kings_blessing': kings_blessing, 'blessings': []}
            
            rate = .1
            def pillar_rates(macd_tier):
                macd_rate = macd_tier / 8
                if macd_rate <0: 
                    macd_rate = (macd_tier * -1)
                
                return macd_rate

            storygauge = revrec.get('storygauge')
            storygauge = storygauge.set_index('symbol')
            # x = storygauge.at[ticker, 'weight_L_15_macd_tier_position']
            # print("storyg", ticker, x)

            # # symbol family discord (model based allocation of budget compoletely)
            # if storygauge.at[ticker, 'weight_L_macd_tier_position'] < -.3:
            #     storygauge.at[ticker, 'weight_L_macd_tier_position']
            #     starfox_alloc = star_total_budget_remaining * storygauge.at[ticker, 'weight_L_macd_tier_position']
            #     # if starfox_alloc 

            # if star_total_budget_remaining > 0: # STAR
            wave_amo_borrow = 0
            borrowed_funds = False
            wave_amo = ticker_total_budget * rate
            # wave amo tiering
            wave_amo, king_order_rules = knights_wave_amo(trigbee, wave_amo, revrec, ticker_time_frame, king_order_rules, star_total_budget_remaining, symbol_total_budget_remaining)
            order_side = 'buy'
            # print(order_side, wave_amo)
            if wave_amo > star_total_budget_remaining:
                msg = (f"KN EXIT {ticker} Amo > then star budget {round(wave_amo)} {round(star_total_budget_remaining)} {round(wave_amo_borrow)}")
                logging.warning(msg)
                print(msg)
                wave_amo = star_total_budget_remaining
                wave_amo_borrow = wave_amo - star_total_budget_remaining
            
            acct_info = QUEEN['account_info']
            
            if blessing_check(acct_info, wave_amo, QUEEN_KING) == False:
                return {'kings_blessing': False}

            # if wave_amo > # ticker price
            if wave_amo > 0:
                if wave_amo < float(STORY_bee[ticker_time_frame]['story'].get('current_ask')):
                    msg = (f'KNIGHT EXIT wave amo LESS then current ask {ticker_time_frame} {float(STORY_bee[ticker_time_frame]["story"].get("current_ask"))} {wave_amo}')
                    logging.warning(msg)
                    print(msg)
                    return {'kings_blessing': False}
            if wave_amo_borrow > 0:
                if wave_amo_borrow < float(STORY_bee[ticker_time_frame]['story'].get('current_ask')):
                    msg = (f'KNIGHT EXIT wave amo BORROW less then current ask {ticker_time_frame} {float(STORY_bee[ticker_time_frame]["story"].get("current_ask"))} {wave_amo}')
                    logging.warning(msg)
                    print(msg)
                    return {'kings_blessing': False}

            kings_blessing = True
            
            if wave_amo:
                kings_blessing, order_vars = trig_in_action_waterfall(ticker_time_frame, 
                                                                    tm_trig, 
                                                                    trigbee, 
                                                                    symbol, 
                                                                    trig_action_num, 
                                                                    time_delta, 
                                                                    trading_model_theme, 
                                                                    king_order_rules, 
                                                                    wave_amo, 
                                                                    maker_middle, 
                                                                    order_side=order_side, 
                                                                    borrowed_funds=False, 
                                                                    app_trig=app_trig)
                blessings['blessings'].append(order_vars)
            
            if wave_amo_borrow:
                msg = (f"KNIGHT wave_amo exceeds stars budget, split into 2 blessings {ticker_time_frame} {wave_amo} __ {wave_amo_borrow}")
                logging.info(msg)
                if wave_amo_borrow > star_total_borrow_remaining:
                    wave_amo_borrow = star_total_borrow_remaining
                    msg = (f"KNIGHT wave_amo exceeds stars BORROW budget, reducing wave amo {ticker_time_frame} wave_amo: {wave_amo_borrow} star_borrow_budget: {star_total_borrow_remaining}")
                    print(msg)
                    logging.warning(msg)
                if star_total_borrow_remaining == 0:
                    print("KNIGHT how did you get here no budget?")
                    send_email(subject=f"STAR has no more budget how did you get to this line of code{ticker_time_frame}")
                else:
                    borrowed_funds = True
                    kings_blessing = True
                    king_order_rules.update({'take_profit': .0034, 'scalp_profits': True, 'close_order_today': True})
                    kings_blessing, order_vars = trig_in_action_waterfall(ticker_time_frame, tm_trig, trigbee, symbol, trig_action_num, 
                                                                        time_delta, trading_model_theme, king_order_rules, 
                                                                        wave_amo=wave_amo_borrow, maker_middle=maker_middle, 
                                                                        order_side='buy', borrowed_funds=True, 
                                                                        app_trig=app_trig)
                    blessings['blessings'].append(order_vars)

            # else:
            #     kings_blessing = False
            #     print("Error New Trig not in Queens Mind: ", trigbee )
            #     return {'kings_blessing': False}


            # try: # long term allocation
            #     if 'revrec' in QUEEN.keys():
            #         LT_orders = return_queen_orders__query(QUEEN, queen_order_states=['long_term'], ticker=ticker, star=False, ticker_time_frame=False)       # total budget calc
            #         if len(LT_orders) >= 0:
            #             portforlio_weight_ask = trading_model.get("portforlio_weight_ask") # weight to stay in ticker regardless of trade
            #             # weight of total position
            #             LT_cost_basis_remaining = sum(LT_orders['cost_basis'])  # closing_orders_cost_basis
            #             ticker_total_budget = QUEEN['revrec']['df_ticker'].loc[ticker].get("ticker_total_budget")
            #             LT_invested = ticker_total_budget * portforlio_weight_ask
                            
            #             if LT_cost_basis_remaining < LT_invested:
            #                 print("Send InvestMent")

            #                 wave_amo = LT_cost_basis_remaining - LT_invested
            #                 if wave_amo > STORY_bee[ticker_time_frame].get('last_close_price'):
            #                     # if number of trades today allowed ## !! 
            #                     trigbee = 'long_term'
            #                     kings_blessing = True
            #                     king_order_rules.update({'take_profit': .24, 'sell_out': .23, 'close_order_today': True})
            #                     kings_blessing, order_vars = trig_in_action_waterfall(tm_trig, trigbee, symbol, trig_action_num, time_delta, trading_model_theme, king_order_rules, wave_amo, maker_middle,ticker_time_frame, order_side='buy', borrowed_funds=borrowed_funds, info="returns kings_blessing, order_vars")
            #                     blessings['blessings'].append(order_vars)
                            
            # except Exception as e:
            #     print("testing", e)
            #     print_line_of_error()
            #     ipdb.set_trace()

            ## Handle App Buys

            if kings_blessing:
                blessings.update({'kings_blessing': kings_blessing})
                if not isinstance(order_vars.get('wave_amo'), float) or order_vars.get('wave_amo') <=0:
                    send_email(subject="error check go check kings blessing")
                    ipdb.set_trace()
                    return {'kings_blessing': False}
            
            charlie_bee['queen_cyle_times']['cc_knight'] = (datetime.now(est) - s_).total_seconds()

            return blessings
            
            # if kings_blessing:
            #     blessings = {{'kings_blessing': kings_blessing, 'ticker': ticker, 'order_vars': order_vars}}
            #     return {'kings_blessing': kings_blessing, 'ticker': ticker, 'order_vars': order_vars}
            # else:
            #     return blessings
            
        except Exception as e:
            print(e, print_line_of_error(), ticker_time_frame)
            print("logme")


    def king_knights_of_the_round_table(QUEEN):
        revrec = QUEEN.get('revrec')
        waveview = revrec.get('waveview')
        def func(x):
            try:
                return x.split("_")[0]
            except Exception as e:
                print(e)
                return x
        # ipdb.set_trace()
        waveview['star'] = waveview.index
        waveview['symbol'] = waveview['star'].apply(lambda x: func(x))

        waveview['symbol_filter'] = np.where((waveview['macd_state'].str.contains('buy')), True, False)
        waveview_buys = waveview[waveview['symbol_filter'] == True]
        buys = waveview_buys.groupby(['symbol']).agg({'allocation': 'sum'}).reset_index()

        waveview['symbol_filter'] = np.where((waveview['macd_state'].str.contains('sell')), True, False)
        waveview_sells = waveview[waveview['symbol_filter'] == True]
        sells = waveview_sells.groupby(['symbol']).agg({'allocation': 'sum'}).reset_index()
        
        return True


    def command_conscience(QUEENsHeart, QUEEN, STORY_bee, QUEEN_KING, api):

        try:

            def revrec_alloc__find_missing_waves(active_trigs, waveview, ticker, margin=False):
                try:# revrec allocation wave decision ... Missing a Swell??
                    # log understanding of why
                    tic_waveview = waveview[(waveview['symbol'] == ticker) & (waveview['allocation_deploy'] < 0)]
                    if len(tic_waveview) > 0:
                        ttf_buys = tic_waveview[tic_waveview['bs_position'] == 'buy']
                        ttf_sells = tic_waveview[tic_waveview['bs_position'] == 'sell']
                        
                        buy_waves_index = ttf_buys.index.tolist()
                        sell_waves_index = ttf_sells.index.tolist()
                        
                        buy_waves = {ttf: [ttf_buys.at[ttf, 'macd_state']] for ttf in buy_waves_index 
                                            if ttf not in active_trigs.keys()}
                        sell_waves = {ttf: [ttf_sells.at[ttf, 'macd_state']] for ttf in sell_waves_index 
                                                if ttf not in active_trigs.keys()}
                        buy_alloc_waves = {ttf: [ttf_buys.at[ttf, 'macd_state']] for ttf in buy_waves_index 
                                                    if ttf_buys.at[ttf, 'allocation_deploy'] < 0}
                        sell_alloc_waves = {ttf: [ttf_sells.at[ttf, 'macd_state']] for ttf in sell_waves_index 
                                                    if ttf_sells.at[ttf, 'allocation_deploy'] < 0}
                        buy_alloc_waves_borrow = {ttf: [ttf_buys.at[ttf, 'macd_state']] for ttf in buy_waves_index 
                                                if ttf_buys.at[ttf, 'allocation_borrow_deploy'] < 0}
                        sell_alloc_waves_borrow = {ttf: [ttf_sells.at[ttf, 'macd_state']] for ttf in sell_waves_index 
                                                    if ttf_sells.at[ttf, 'allocation_borrow_deploy'] < 0}

                        # for ttf in buy_waves_index:
                        #     if ttf_buys.at[ttf, 'allocation_deploy'] < 0:
                        #         active_trigs = {**active_trigs, **{ttf: [ttf_buys.get('macd_state')]}}
                        
                        # for ttf in sell_waves_index:
                        #     if ttf_sells.at[ttf, 'allocation_deploy'] < 0:
                        #         active_trigs = {**active_trigs, **{ttf: [ttf_sells.get('macd_state')]}}

                        # print('buys', buy_waves.items())
                        # print('sells', sell_waves.items())
                        active_trigs = {**active_trigs, **buy_waves}
                        active_trigs = {**active_trigs, **sell_waves}
                        active_trigs = {**active_trigs, **buy_alloc_waves}
                        active_trigs = {**active_trigs, **sell_alloc_waves}
                        if margin:
                            active_trigs = {**active_trigs, **buy_alloc_waves_borrow}
                            active_trigs = {**active_trigs, **sell_alloc_waves_borrow}
                        
                        return active_trigs

                except Exception as e:
                    print("add wave failed", e)


            def short():
                return True

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
            app_wave_trig_req = process_app_requests(QUEEN=QUEEN, QUEEN_KING=QUEEN_KING, request_name='wave_triggers', archive_bucket='app_wave_requests')
            app_trig = {'trig': False}
            ready_buy = False
            app_trig_ttf = False
            if app_wave_trig_req.get('app_flag'):
                print('app flag', app_wave_trig_req.get('ticker_time_frame'))
                app_trig_ttf = app_wave_trig_req.get('ticker_time_frame')
                ready_buy = app_wave_trig_req.get('ready_buy')
                x_buy = app_wave_trig_req.get('x_buy')

            if type(QUEEN.get('price_info_symbols')) is not pd.core.frame.DataFrame:
                print("OLD QUEEN")
                return False
            
            req = process_app_requests(QUEEN, QUEEN_KING, request_name='buy_orders')
            if req.get('app_flag'):
                acct_info = QUEEN['account_info']
                """Rev Rec"""
                revrec = refresh_chess_board__revrec(acct_info, QUEEN, QUEEN_KING, STORY_bee, active_queen_order_states=active_queen_order_states, chess_board__revrec={}, revrec__ticker={}, revrec__stars={}) ## Setup Board
                QUEEN['revrec'] = revrec
                god_save_the_queen(QUEEN, save_rr=True, save_q=True, save_qo=True)
            
            # cycle through stories  # The Golden Ticket
            s_time = datetime.now(est)
            for ticker in active_tickers:
                # Ensure Trading Model
                if ticker not in QUEEN_KING['king_controls_queen']['symbols_stars_TradingModel'].keys():
                    # QUEEN['queens_messages'].update({'model_does_not_exist': f'{ticker}'})
                    msg = (f'model_does_not_exist {ticker}')
                    print(msg)
                    logging.error(msg)
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
                                    (waveview['allocation_deploy'] < 0) &
                                    ((waveview['allocation_deploy'] * -1) > waveview['current_ask'])
                                    ].copy()
                bees_fly_borrow = waveview[
                                    (waveview['allocation_borrow_deploy'] < 0) &
                                    ((waveview['allocation_borrow_deploy'] * -1) > waveview['current_ask'])
                                    ].copy()
                bees_fly_home = waveview[
                                    (waveview['allocation_deploy'] > 0) &
                                    ((waveview['allocation_deploy']) > waveview['current_ask'])
                                    ].copy()
                bees_fly_home_borrow = waveview[
                                    (waveview['allocation_borrow_deploy'] > 0) &
                                    ((waveview['allocation_borrow_deploy']) > waveview['current_ask'])
                                    ].copy()
                # conflicts your sellhomes are cancel out the flying

                # create single buy package with borrow?

                for ticker_time_frame in bees_fly.index.tolist():
                    # print(bees_fly)
                    if ticker_time_frame in QUEEN['stars'].keys():
                        if (datetime.now(est) - QUEEN['stars'].get(ticker_time_frame).get('last_buy')) < timedelta(seconds=60):
                            msg = (ticker_time_frame, 'Just Bought, Deploying Is Still', bees_fly.at[ticker_time_frame, 'allocation_deploy'], " StarAtPlay: ", bees_fly.at[ticker_time_frame, 'star_at_play'], " Ask Price", bees_fly.at[ticker_time_frame, 'current_ask'])
                            print(msg)
                            logging.warning(msg)
                            continue
                    # if ticker not in ['SPY', 'GOOG']:
                    #     continue
                    # print(ticker_time_frame)
                    s_time = datetime.now(est)
                    # path to Knight
                    ticker, tframe, frame = ticker_time_frame.split("_")
                    # trading model
                    trading_model = QUEEN_KING['king_controls_queen']['symbols_stars_TradingModel'].get(ticker)
                    
                    frame_block = f'{tframe}{"_"}{frame}' # frame_block = "1Minute_1Day"
                    
                    # trigbee
                    trig = bees_fly.at[ticker_time_frame, 'macd_state']
                    tm_trig = trig
                    trig_wave_length = waveview.at[ticker_time_frame, 'wave_state']
                    on_wave_buy = True if trig_wave_length != '0' else False
                    if on_wave_buy:
                        tm_trig = 'buy_cross-0' if 'buy' in trig else 'sell_cross-0'
                    
                    trig_type = 'buy' if 'buy' in tm_trig else 'sell'

                    # check global ticker level
                    if frame_block in ['1Minute_1Day']:
                        if trig_type == 'buy' and revrec['storygauge'].loc[ticker].get('trinity_w_15') > 0:
                            # print(ticker, "trinity short 1min buy > 0 not buying")
                            continue
                        elif trig_type == 'sell' and revrec['storygauge'].loc[ticker].get('trinity_w_15') < 0:
                            # print("shorting when trinity in negative")
                            continue
                    
                    if revrec.get('df_ticker').loc[ticker, 'ticker_buying_power'] == 0:
                        msg = (f'Conscience NO ticker_buying_power')
                        print(msg)
                        logging.warning(msg)
                        continue
                    
                    if str(trading_model['status']) not in ['active', 'true']:
                        QUEEN['queens_messages'].update({'model_not_active': f'{ticker_time_frame}'})
                        print("model status not active")
                        continue
                    if str(trading_model['power_rangers'].get(frame_block)).lower() not in ['active', 'true']:
                        # global 1Minute_1Day is not active
                        print("not active")
                        continue

                    # Stop Symbols from shorting unless you are main_index ("Wants to Short Stock Scenario")
                    if 'sell' in trig and ticker not in QUEEN['heartbeat']['main_indexes'].keys():
                        # print("ticker not avail to short > short gauge >")
                        continue

                    try: # """ Trigger Bees"""                         
                        # check if you already placed order or if a workerbee in transit to place order
                        s_ = datetime.now(est)
                        ticker_in_action = True if ticker in active_orders['symbol'].to_list() else False
                        ticker_trig_action = ticker_trig_In_Action_cc(active_orders=active_orders, trig=tm_trig, ticker=ticker)
                        trig_action = trig_In_Action_cc(active_orders=active_orders, trig=tm_trig, ticker_time_frame=ticker_time_frame)
                        charlie_bee['queen_cyle_times']['cc_trig_in_action'] = (datetime.now(est) - s_).total_seconds()
                        # Protect the Knight
                        if len(ticker_trig_action) > 0 and trading_model.get('short_position') == True: # shorting allowed
                            print("Only 1 Trigger Allowed in ticker Shorting")
                            continue

                        if revrec['df_stars'].loc[ticker_time_frame].get("remaining_budget") == 0:
                            print(f'{ticker_time_frame} all budget used up')
                            if ticker_time_frame not in QUEEN['queens_messages'].keys():
                                QUEEN['queens_messages'][ticker_time_frame] = {'remaining_budget': f'{ticker_time_frame} all budget used up'}
                            else:
                                QUEEN['queens_messages'][ticker_time_frame].update({'remaining_budget': f'{ticker_time_frame} all budget used up'})
                            continue

                        if revrec['df_stars'].loc[ticker_time_frame].get("remaining_budget") <= 0 and revrec['df_stars'].loc[ticker_time_frame].get("remaining_budget_borrow") <= 0:
                            print("No Budget Remaining")
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
                            ticker_time_frame=ticker_time_frame, 
                            trading_model=trading_model, 
                            trig_action=trig_action, 
                            crypto=crypto, 
                            app_trig=app_trig)
                        charlie_bee['queen_cyle_times']['cc_knights_request__cc'] = (datetime.now(est) - s_time).total_seconds()
                        
                        if king_resp.get('kings_blessing'):
                            for blessing in king_resp.get('blessings'):
                                if blessing:
                                    exx = execute_order(api=api, QUEEN=QUEEN, blessing=blessing,
                                                    side=blessing.get('order_side'),
                                                    wave_amo=blessing.get('wave_amo'),
                                                    order_type=blessing.get('order_type'),
                                                    limit_price=blessing.get('limit_price'),
                                                    trading_model=blessing.get('trading_model'),
                                                    king_resp=True, 
                                                    king_eval_order=False, 
                                                    ticker=blessing.get('symbol'), 
                                                    ticker_time_frame=blessing.get('ticker_time_frame_origin'), 
                                                    trig=blessing.get('trigbee'), 
                                                    crypto=crypto)
                                    if exx.get('executed'):
                                        append_queen_order(QUEEN, exx.get('new_queen_order_df'))
                                        logging.info(exx.get('msg'))
                                        print(exx.get('msg'))

                                        if 'stars' not in QUEEN.keys():
                                            QUEEN['stars'] = {ticker_time_frame: {'last_buy': datetime.now(est)}}
                                        else:
                                            QUEEN['stars'].update({ticker_time_frame: {'last_buy': datetime.now(est)}})

                            acct_info = QUEEN['account_info']
                            """Rev Rec"""
                            revrec = refresh_chess_board__revrec(acct_info, QUEEN, QUEEN_KING, STORY_bee, active_queen_order_states=active_queen_order_states, chess_board__revrec={}, revrec__ticker={}, revrec__stars={}) ## Setup Board
                            QUEEN['revrec'] = revrec
                            god_save_the_queen(QUEEN, save_rr=True, save_qo=True)
                                
                    except Exception as e:
                        msg = (ticker_time_frame, e, print_line_of_error())
                        print(msg)
                        QUEEN['queens_messages'].update({'commandconscience__failed': {'ticker_time_frame': f'{ticker_time_frame}', 'error': e, 'line_error': print_line_of_error()}})
                        send_email(subject="Knight Error", body=f'{msg}')
                        ipdb.set_trace()
                        sys.exit()


                if app_wave_trig_req.get('app_flag') == True and ticker == app_wave_trig_req['app_request']['ticker']:
                    active_trigs = add_app_wave_trigger(active_trigs=active_trigs, ticker=ticker, app_wave_trig_req=app_wave_trig_req)
                
                charlie_bee['queen_cyle_times']['cc_thehunt__cc'] = (datetime.now(est) - s_time).total_seconds()
                # Return Scenario based trades
                # return all allocation deploys and add wave trigger if one not already there
                
                # revrec_alloc__find_missing_waves(active_trigs=active_trigs, waveview=waveview, ticker=ticker)
                

            return True
        except Exception as e:
            print('wtf', e, print_line_of_error())




    """>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> ORDER MANAGEMENT <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< """
    """>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> ORDER MANAGEMENT <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< """
    """>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> ORDER MANAGEMENT <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< """



    def order_past_duration(queen_order):
        nowtime = datetime.now().astimezone(est)
        qorder_time = queen_order['datetime'].astimezone(est)
        duration_rule = queen_order['order_rules']['timeduration']
        order_time_delta = nowtime - qorder_time
        # order_time_delta.total_seconds()
        # duration_divide_time = {'1Minute': 60, "5Minute": }
        if "1Minute" in queen_order['ticker_time_frame']:
            if (order_time_delta.seconds / 60) > duration_rule:
                logging.info(("order past timeduration,", queen_order.get('ticker_time_frame')))
                # return (order_time_delta.seconds / 60) - duration_rule

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

        
    def validate_portfolio_with_RUNNING(ticker, run_index, run_order, portfolio): # check if there are enough shares in portfolio IF NOT Archive RUNNING ORDER AS IT WAS SOLD ALREADY
        # if totals don't match with alpaca
        # df_links = return_all_linked_queen_orders(exit_order_link=run_order['client_order_id'])
        # qos_qty = sum(df_links['qty'])
        # qos_filledqty = sum(df_links['filled_qty'])
        ro_delta = datetime.now(est) - run_order['datetime']
        try:
            if ticker in portfolio.keys():
                qty_avail = float(portfolio[ticker]['qty'])
                qty_run = float(run_order['qty_available'])
                
                # short and run < avail (-10, -5)
                if qty_avail < 0 and qty_run < qty_avail and ro_delta > timedelta(minutes=1):
                    msg = ("run order: qty_avail < 0 and qty_run < qty_avail, adjust to remaining", run_order['queen_order_state'], run_order['client_order_id'])

                    logging_log_message(log_type='critical', msg=msg, ticker=run_order['ticker_time_frame'])
                    print("CRITICAL ERROR SHORT POSITION PORTFOLIO DOES NOT HAVE QTY AVAIL TO SELL adjust to remaining")

                    QUEEN['queen_orders'].at[run_index, 'filled_qty'] = qty_avail
                    QUEEN['queen_orders'].at[run_index, 'qty_available'] = qty_avail
                    QUEEN['queen_orders'].at[run_index, 'qty_validation'] = 'true'
                    return QUEEN['queen_orders'].loc[run_index].to_dict()

                # long and run > avail (10, 5)
                if qty_avail > 0 and qty_run > qty_avail and ro_delta > timedelta(minutes=1):
                    msg = ("run order: qty_avail < 0 and qty_run < qty_avail, adjust to remaining", run_order['queen_order_state'], run_order['client_order_id'])
                    logging_log_message(log_type='critical', msg=msg, ticker=run_order['ticker_time_frame'])
                    print("CRITICAL ERROR LONG POSITION PORTFOLIO DOES NOT HAVE QTY AVAIL TO SELL adjust to remaining")

                    QUEEN['queen_orders'].at[run_index, 'filled_qty'] = qty_avail
                    QUEEN['queen_orders'].at[run_index, 'qty_available'] = qty_avail
                    QUEEN['queen_orders'].at[run_index, 'qty_validation'] = 'true'
                    return QUEEN['queen_orders'].loc[run_index].to_dict()
                else:
                    return QUEEN['queen_orders'].loc[run_index].to_dict()
            
            else:
                if ro_delta > timedelta(minutes=1):
                    print(ticker, "tagging CRITICAL ERROR PORTFOLIO DOES NOT HAVE TICKER ARCHVIE RUNNING ORDER Tagged to be archived")
                    logging.critical({'msg': f'{ticker}{" :Ticker not in Portfolio 1"}'})

                    order_status = check_order_status(api=api, client_order_id=run_order['client_order_id'])
                    queen_order = update_latest_queen_order_status(order_status=order_status, queen_order_idx=run_index)
                    QUEEN['queen_orders'].at[run_index, 'queen_order_state'] = "completed_alpaca"        
                    return QUEEN['queen_orders'].loc[run_index].to_dict()
        
        except Exception as e:
            print(e, print_line_of_error())


    def update_latest_queen_order_status(order_status, queen_order_idx): # updates qty and cost basis from Alpaca
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
            print("# running order has been fully sold out and now we can archive")
            QUEEN['queen_orders'].at[origin_idx, 'queen_order_state'] = 'completed'
            return True
        else:
            return False
    

    def update_origin_orders_profits(queen_order, origin_order, origin_order_idx): # updated origin Trade orders profits
        # origin order
        # origin_order_cost_basis__qorder = float(queen_order['filled_qty']) * float(origin_order['filled_avg_price'])
        origin_order_cost_basis__qorder = origin_order.get('cost_basis')
        queen_order_cost_basis = (float(queen_order['filled_qty']) * float(queen_order['filled_avg_price']))
        queen_order_cost_basis__to_origin_order = queen_order_cost_basis - origin_order_cost_basis__qorder
        
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

            # validate qty
            if sum(origin_closing_orders_df['filled_qty']) > float(queen_order['qty']):
                msg = ("There must be a limit order thats needs to be adjusted/cancelled", origin_order_idx)
                print(msg)
                logging.error(msg)
                pass

            QUEEN['queen_orders'].at[origin_order_idx, 'profit_loss'] = profit_loss
            QUEEN['queen_orders'].at[origin_order_idx, 'closing_orders_cost_basis'] = closing_orders_cost_basis

            return {'closing_filled': closing_filled, 'profit_loss': profit_loss}
        else:
            return {'closing_filled': 0, 'profit_loss': 0 }


    def return_origin_order(df_queenorders, exit_order_link):
        origin_order_q = df_queenorders[df_queenorders['client_order_id'] == exit_order_link].copy()
        if len(origin_order_q) > 0:
            origin_idx = origin_order_q.iloc[-1].name
            origin_order = origin_order_q.iloc[-1].to_dict()
            return {'origin_order': origin_order, 'origin_idx': origin_idx}
        else:
            return {'origin_order': ''}


    def return_snap_priceinfo__pollenData(QUEEN, STORY_bee, ticker, api):
        # read check if ticker is active...if it is return into from db ELSE return broker data 
        call_snap = False
        ttf = f'{ticker}{"_1Minute_1Day"}'
        if ttf not in QUEEN['heartbeat']['available_tickers']: #STORY_bee.keys():
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


    def update_queen_order_profits(ticker, queen_order, queen_order_idx, priceinfo):
        try:            
            # snap = priceinfo['snapshot']

            # # current_price = STORY_bee[f'{ticker}{"_1Minute_1Day"}']['last_close_price']
            # current_price = snap.latest_trade.price
            # current_ask = snap.latest_quote.ask_price
            # current_bid = snap.latest_quote.bid_price

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
                QUEEN['queen_orders'].at[queen_order_idx, 'money'] = (current_price * float(queen_order['filled_qty'])) - ( float(queen_order['filled_avg_price']) * float(queen_order['filled_qty']) )
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


    def update_runCLOSE__queen_order_honey(queen_order, origin_order, queen_order_idx):
        sold_price = float(queen_order['filled_avg_price'])
        origin_price = float(origin_order['filled_avg_price'])
        honey = (sold_price - origin_price) / origin_price
        cost_basis = origin_price * float(queen_order['filled_qty'])
        
        profit_loss_value = honey * cost_basis
        
        QUEEN['queen_orders'].at[queen_order_idx, 'honey'] = honey
        QUEEN['queen_orders'].at[queen_order_idx, 'money'] = profit_loss_value
        QUEEN['queen_orders'].at[queen_order_idx, 'profit_loss'] = profit_loss_value
        
        return {'profit_loss_value': profit_loss_value}


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
    

    def conscience_update(QUEEN, root_name='app_info', thought_dict={}, conscience=True):
        def conscience_thought(QUEEN, thought, conscience):
            try:
                tho_id = len(QUEEN[conscience])
                thought['id'] = tho_id
                thought['timestamp_est'] = datetime.now(est)
                return thought
            except Exception as e:
                print_line_of_error(e)
                return None
        
        conscience = 'conscience' if conscience else 'sub_conscience'
        
        if root_name not in QUEEN[conscience].keys():
            logging.warning(f'new conscience {root_name}')
            return False
        
        # store message
        if thought_dict not in QUEEN[conscience][root_name]:
            thought_dict = conscience_thought(QUEEN, thought_dict, conscience)
            if thought_dict:
                QUEEN[conscience][root_name].append(thought_dict)
        
                QUEEN['heartbeat'][conscience] = QUEEN[conscience]
                print("save message to queen", thought_dict)
                
                # god_save_the_queen(QUEEN, QUEENsHeart=True)

        return True

    def subconscious_mind(root_name):
        # store message
        if root_name not in QUEEN['subconscious']:
            QUEEN['subconscious'][root_name] = []
        if len(QUEEN['subconscious'][root_name]) > 0:
            if root_name == 'app_info':
                try:
                    thoughts_to_pop = []
                    for idx, thought in enumerate(QUEEN['subconscious'][root_name]):
                        if len(thought) > 0 and thought['ticker_time_frame'] in STORY_bee.keys():
                            print('clear subconscious thought, db now streaming ticker')
                            thoughts_to_pop.append(idx)
                    if len(thoughts_to_pop) > 0:
                        QUEEN['subconscious'][root_name] = [i for idx, i in enumerate(QUEEN['subconscious'][root_name]) if idx not in thoughts_to_pop]

                except Exception as e:
                    print(e, print_line_of_error())

        return True

    def release_trig_sell_stop(QUEEN, ticker, client_order_id):
        # does as it says
        try:
            qo_states = RUNNING_CLOSE_Orders + RUNNING_OPEN
            running_close = return_queen_orders__query(QUEEN=QUEEN, queen_order_states=qo_states, ticker=ticker)
            if len(running_close) > 0:
                in_running_close = True if client_order_id in running_close['exit_order_link'].tolist() else False
                if in_running_close == False:
                    print("release order back to Bishop")
                    # logging.info(("Releaseing Order back to Bishop be Sold: ", client_order_id))
                    QUEEN['queen_orders'].at[client_order_id, 'order_trig_sell_stop'] = False
            else:
                print("release order back to Bishop no linked orders active")
                # logging.info(("Releaseing Order back to Bishop be Sold: ", client_order_id))
                QUEEN['queen_orders'].at[client_order_id, 'order_trig_sell_stop'] = False    
            
            
            
            return True                
        except Exception as e:
            print(e)

            # do you have any active running_close against you?

    def king_bishops_QueenOrder(STORY_bee, run_order, priceinfo, revrec):

        def check_revrec(sell_qty, revrec, trigname, current_macd, mm_cost, ticker_time_frame):
            try:
                # wave
                macd_state_ = trigname.split("_")[0]
                current_macd_ = current_macd.split("_")[0]
                
                # alloc
                if ticker_time_frame in revrec['waveview'].index:
                    al = abs(revrec['waveview'].loc[ticker_time_frame].get('allocation'))
                    cb = mm_cost
                    al_sellable = al -  cb
                    
                    
                    # sell qty update
                    if al_sellable < 0 and macd_state_ == current_macd_:
                        original_sell_qty = sell_qty
                        sell_qty_pct = abs(al_sellable / cb)
                        sell_qty = round(sell_qty * sell_qty_pct)
                        if original_sell_qty != sell_qty:
                            msg = ("SELL QTY ADJUSTMENT", ticker_time_frame, original_sell_qty, sell_qty)
                            print(msg)
                            logging.warning(msg)
                else:
                    print(ticker_time_frame, "missing in waveview")
                
                return sell_qty
            except Exception as e:
                print_line_of_error(e)
                return 0
        

        """if you made it here you are running somewhere, I hope you find your way, I'll always bee here to help"""
        try:
            # # # Stars in Heaven

            s_time = datetime.now(est)
            # gather run_order Vars
            trigname = run_order['trigname']
            trigname_wave_time = int(trigname.split("-")[-1])
            order_rules = run_order.get('order_rules')
            client_order_id = run_order['client_order_id']
            take_profit = order_rules['take_profit']
            sell_out = order_rules['sell_out']
            skip_sell_trigbee_distance_frequency = order_rules.get('skip_sell_trigbee_distance_frequency')
            stagger_profits_tiers = order_rules.get('stagger_profits_tiers')
            # filled_qty = float(run_order['filled_qty'])
            sell_qty = float(run_order['qty_available'])
            ticker_time_frame = run_order['ticker_time_frame']
            ticker_time_frame_origin = run_order['ticker_time_frame_origin']
            entered_trade_time = run_order['datetime'].astimezone(est)
            origin_wave = run_order['origin_wave']
            ## if on new wave update origin_wave
            # trading_model = run_order['trading_model'] # in Future Turn this to TradingModel_Id
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

            # verison control until better way found
            # def order_rule(rule, order_rules):
            #     if rule in order_rules.keys():
            #         if rule == 'max_profit_waveDeviation_timeduration':
                    
            #         return order_rules.get(rule)
            # order_rule(rule='max_profit_waveDeviation_timeduration', order_rules=order_rules)
            if 'max_profit_waveDeviation_timeduration' in order_rules.keys():
                max_profit_waveDeviation_timeduration = order_rules['max_profit_waveDeviation_timeduration']
            else:
                max_profit_waveDeviation_timeduration = 500 # Minutes

            # Only if there are available shares

            sell_order = False # #### >>> convince me to sell  $$

            macd_gauge = macdGauge_metric(STORY_bee=STORY_bee, ticker_time_frame=ticker_time_frame, trigbees=['buy_cross-0', 'sell_cross-0'], number_ranges=[5, 11, 16, 24, 33])
            honey_gauge = honeyGauge_metric(run_order)
            # conscience_update(root_name='macd_gauge', dict_to_add={macd_gauge}, list_len=1)
            # conscience_update(root_name='honey_gauge', dict_to_add={honey_gauge}, list_len=1)

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
            current_wave = star_ticker_WaveAnalysis(STORY_bee=STORY_bee, ticker_time_frame=ticker_time_frame).get('current_wave') # df slice or can be dict
            if len(QUEEN['queen_orders'].at[client_order_id, 'assigned_wave']) == 0:
                print(type(QUEEN['queen_orders'].at[client_order_id, 'assigned_wave']))
                print("assign wave first pass do this at order creation?", QUEEN['queen_orders'].at[client_order_id, 'assigned_wave'])
                QUEEN['queen_orders'].at[client_order_id, 'assigned_wave'] = current_wave
                # god_save_the_queen(QUEEN, save_q=True, save_qo=True)
            
            assigned_wave = QUEEN['queen_orders'].at[client_order_id, 'assigned_wave']
            # compare current wave against it stats How Far away are you from max profit?

            """ Trading Models Kings Order Rules """ 
            # Trading Model Sell Vars
            # use maxprofit deviation here and add to order
            trigname_count = int(trigname.split("-")[-1])
            wave_length = current_wave['length'] - assigned_wave.get('length') ## current_wave['length'] - trigname_count
            wave_time_tomaxprofit  = current_wave['time_to_max_profit'] - assigned_wave.get('time_to_max_profit')
            current_wave_maxprofit_stat = wave_length - wave_time_tomaxprofit
            
            run_order_wave_changed = True if run_order['assigned_wave'].get('wave_id') != current_wave.get("wave_id") else False
            # if run_order_wave_changed:
                # print(f"{ticker_time_frame} Run Order On New Wave >> {client_order_id}")
                # print(run_order['assigned_wave'].get('wave_id'))
                # print(current_wave.get("wave_id"))
                # if order_rules.get('ready_buy') != True:
                #     print("Do Not Change Wave keep assigned wave as origin this is a Ready BUY")
                # else:
                # logging.warning((f"{ticker_time_frame} Run Order On New Wave >> {client_order_id}"))
                # QUEEN['queen_orders'].at[client_order_id, 'assigned_wave'] = current_wave
                # god_save_the_queen(QUEEN=QUEEN, save_q=True)
            # ("RUN Order Changed")

            # trade is past excepted duration time 
            past_trade_duration = order_past_duration(queen_order=run_order)

            # Wave distance to Max Profit
            ttframe_take_max_profit = order_rules['max_profit_waveDeviation'] # 5,
            wave_past_max_profit = float(ttframe_take_max_profit) >= current_wave_maxprofit_stat # max profits exceed setting

            # Gather main sell reason groups
            sell_trigbee_trigger = True if str(order_rules['sell_trigbee_trigger']).lower() == 'true' else False
            stagger_profits = True if str(order_rules['stagger_profits']).lower() == 'true' else False
            scalp_profits = True if str(order_rules['scalp_profits']).lower() == 'true' else False
            macd_tier = current_macd_time
            
            charlie_bee['queen_cyle_times']['om_bishop_block2_queenorder__om'] = (datetime.now(est) - s_time).total_seconds()
            s_time = datetime.now(est)

            """ WaterFall sell chain """
            now_time = s_time
            def waterfall_sellout_chain(client_order_id, macd_tier, trading_model, sell_order, run_order, order_type, limit_price, sell_trigbee_trigger, stagger_profits, scalp_profits, run_order_wave_changed, sell_qty, QUEEN=QUEEN):
                # if honey go through sell options (i.e. should we split at honey ?)
                # when honey < , go through re-evalute ?
                
                sell_trigbee_trigger_timeduration = run_order.get('sell_trigbee_trigger_timeduration')
                sell_trigbee_trigger_timeduration = 89 if type(sell_trigbee_trigger_timeduration) != int else sell_trigbee_trigger_timeduration
                time_in_trade_past_selltrigbee = time_in_trade_datetime > timedelta(minutes=sell_trigbee_trigger_timeduration)
                time_in_trade_past_selltrigbee_max_wave_profit = True if time_in_trade_datetime > timedelta(minutes=max_profit_waveDeviation_timeduration) and wave_past_max_profit else False
                # if client_order_id == 'close__2-run__MSFT-buy_cross-0-8531-23-07-03 21.10.-23-07-03 44.10.':
                #     print("here", run_order['trigname'], current_macd, time_in_trade_datetime.seconds)
                
                try:
                    # client_order_id = run_order.get('client_order_id')
                    sell_reasons = []
                    
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

                    
                    # Water Fall
                    try:
                        update_profit_mark_scale = []
                        take_profit_scale = order_rules.get('take_profit_scale')
                        if take_profit_scale is not None:
                            for profit_num, profit_take_vars in take_profit_scale.items():
                                if profit_take_vars.get('take_mark') == False:
                                    if honey >= profit_num:
                                        # profit_take_vars.get("take_pct")
                                        print("selling out: PROFIT Mark ACHIVED")
                                        sell_reason = f'order_rules__take_profit_scale_{profit_num}'
                                        sell_reasons.append(sell_reason)
                                        sell_order = True
                                        
                                        limit_price = priceinfo['maker_middle'] if order_type == 'limit' else False
                                        sell_qty = round(sell_qty * profit_take_vars.get("take_pct"), 0)
                                        update_profit_mark_scale.append(run_order.get('client_order_id'))
                                        QUEEN['queen_orders'].at[run_order.get('client_order_id'), 'take_profit_scale'].update({profit_num: {'take_pct':profit_take_vars.get("take_pct"),'take_mark': True}})

                    except Exception as e:
                        print("scale", e)
                    if order_rules['take_profit'] <= honey:
                        print("selling out due PROFIT ACHIVED")
                        sell_reason = 'order_rules__take_profit'
                        sell_reasons.append(sell_reason)
                        sell_order = True
                        
                        order_side = 'sell'
                        limit_price = priceinfo['maker_middle'] if order_type == 'limit' else False

                    elif honey <= order_rules['sell_out']:
                        print("selling out due STOP LOSS")
                        sell_reason = 'order_rules__sellout'
                        sell_reasons.append(sell_reason)
                        sell_order = True

                        order_side = 'sell'
                        limit_price = priceinfo['maker_middle'] if order_type == 'limit' else False

                    elif past_trade_duration:
                        print("selling out due to TIME DURATION")
                        sell_reason = 'order_rules__timeDuration'
                        sell_reasons.append(sell_reason)
                        sell_order = True

                        order_side = 'sell'
                        limit_price = priceinfo['maker_middle'] if order_type == 'limit' else False

                    elif run_order.get('honey') > .01 and time_in_trade_past_selltrigbee_max_wave_profit:
                        print("Selling Out from max_profit_waveDeviation: deviation>> ", current_wave_maxprofit_stat)
                        sell_reason = 'order_rules__max_profit_waveDeviation'
                        sell_reasons.append(sell_reason)
                        sell_order = True

                        order_side = 'sell'
                        limit_price = priceinfo['maker_middle'] if order_type == 'limit' else False

                    
                    # how to consider new triggers?
                    if sell_trigbee_trigger and time_in_trade_past_selltrigbee: #run_order.get('sell_trigbee_trigger_timeduration')
                        if "buy" in run_order['trigname'] and "sell" in current_macd and time_in_trade_datetime.seconds > 500: 
                            # if 'use_wave_guage' in order_rules.keys():
                            logging.info(("looking to sell BUY-cross", ticker_time_frame, f"""{macd_gauge['metrics']['sell_cross-0'][5]['avg']}"""))
                            if macd_gauge['metrics']['sell_cross-0'][5]['avg'] > .5:
                                print("SELL ORDER change from buy to sell", current_macd, current_macd_time)
                                sell_reason = 'order_rules__macd_cross_buytosell'
                                sell_reasons.append(sell_reason)
                                sell_order = True
                                order_side = 'sell'
                                limit_price = priceinfo['maker_middle'] if order_type == 'limit' else False

                        elif "sell" in run_order['trigname'] and "buy" in current_macd and time_in_trade_datetime.seconds > 500:
                            logging.info(("looking to sell Sell-cross", ticker_time_frame, f"""{macd_gauge['metrics']['buy_cross-0'][5]['avg']}"""))
                            if macd_gauge['metrics']['buy_cross-0'][5]['avg'] > .5:
                                print("SELL ORDER change from Sell to Buy", current_macd, current_macd_time)

                                sell_reason = 'order_rules__macd_cross_selltobuy'
                                sell_reasons.append(sell_reason)
                                sell_order = True
                                order_side = 'sell'
                                limit_price = priceinfo['maker_middle'] if order_type == 'limit' else False

                    if 'KOR_version' in order_rules.keys():
                        # weight_of_total_reconsider_time = decay % time in to time to consider
                        if 'revisit_trade_datetime' in order_rules.keys():
                            if order_rules.get('revisit_trade_frequency') > (now_time - order_rules.get('revisit_trade_datetime')).total_seconds():
                                print("reconsider trade thoughts")
                                # logging.info(("Reconsider Trade Time"))
                                # upddate run order
                                run_order['order_rules']['revisit_trade_datetime'] = now_time
                            # are we in profit?
                            # how old is our trade compared to our goal?
                            # what does the family say?
                            # are you closing out today?

                        close_order_today = order_rules.get('close_order_today')
                        time_to_bell_close = (now_time.replace(hour=16, minute=00, second=0) - now_time).total_seconds()
                        last_call_time = now_time.replace(hour=15, minute=58, second=0)
                    #     last_10min_time = now_time.replace(hour=15, minute=50, second=0)
                    #     last_30min_time = now_time.replace(hour=15, minute=30, second=0)
                    #     last_30hr_time = now_time.replace(hour=15, minute=0, second=0)


                        if order_rules.get('close_order_today'):
                            try:
                                if order_rules.get('close_order_today_allowed_timeduration') >= time_to_bell_close and time_in_trade_datetime > timedelta(seconds=33):
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
                            
                            except Exception as e:
                                print(print_line_of_error())
                    
                    
                    
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
                    
                    
                    if sell_order:
                        mm_cost = priceinfo.get('maker_middle') * sell_qty
                        order_side = 'sell'
                        sell_qty = check_revrec(sell_qty, revrec, trigname, current_macd, mm_cost, ticker_time_frame)
                        if sell_qty > 0:
                            print("Bishop SELL ORDER:", ticker_time_frame, sell_reasons, current_macd, current_macd_time, mm_cost)
                            logging.info(("Bishop SELL ORDER:", ticker_time_frame, sell_reasons, current_macd, current_macd_time, mm_cost))
                            # conscience_update(root_name='bishop_sell_order', dict_to_add={'ticker_time_frame': ticker_time_frame, 'sell_reasons': sell_reasons}, list_len=33)
                            return {'sell_order': True, 
                            'sell_reason': sell_reason, 
                            'order_side': order_side, 
                            'order_type': order_type, 
                            'sell_qty': sell_qty, 
                            'limit_price': limit_price, 
                            'app_request': app_request,
                            'maker_middle_cost': mm_cost
                            }
                        else:
                            print("Bishop DONOT SELL Min.Allocation Stop", ticker_time_frame)
                            return {'sell_order': False}
                    else:
                        return {'sell_order': False}
                
                except Exception as e:
                    print('waterfall error', e, " er line>>", print_line_of_error())

            king_bishop = waterfall_sellout_chain(client_order_id, macd_tier, trading_model, sell_order, run_order, order_type, limit_price, sell_trigbee_trigger, stagger_profits, scalp_profits, run_order_wave_changed, sell_qty)
        
            charlie_bee['queen_cyle_times']['om_bishop_block3__om'] = (datetime.now(est) - s_time).total_seconds()

            # elif the 3 wisemen pointing to sell or re-chunk profits

            # check if position is neg, if so, switch side to sell and sell_qty to buy  # if portfolio[run_order['ticker']]['side'] == 'short':


            def check_on_borrowed_funds(run_order, revrec, king_bishop):
                try:
                    if run_order.get('borrowed_funds') == False:
                        al = revrec['waveview'].loc[ticker_time_frame].get('allocation')
                        cb = (king_bishop.get('maker_middle_cost') * -1)
                        macd_state_ = trigname.split("_")[0]
                        current_macd_ = current_macd.split("_")[0]
                        if al:
                            if al < cb and macd_state_ == current_macd_:
                                sellable = (al - cb) * -1
                                # if (cb *-1) > sellable:
                                #     print("Current price > sellable amount, nothing to sell")
                                # print("Hold Sell Min. Allocation ", sellable, run_order.get('ticker_time_frame'), al, cb)
                                # logging.info(("Hold Sell Min. Allocation ", sellable, run_order.get('ticker_time_frame'), al, cb))
                                return True
                        return False
                    return False
                except Exception as e:
                    print("wwwwave", e)
                    return False
            
            if king_bishop['sell_order']:
                print(king_bishop['app_request'])
                if str(king_bishop['sell_qty']) == 'nan':
                    send_email(subject='error checker go see whats up')
                    ipdb.set_trace()
                
                # if check_on_borrowed_funds(run_order=run_order, revrec=revrec, king_bishop=king_bishop):
                #     print("NOT SELLING DUE TO CBF")
                #     return {'bee_sell': False}  

                order_vars = order_vars__queen_order_items(order_side='sell',  
                maker_middle=king_bishop['limit_price'],
                sell_reason=king_bishop['sell_reason'], 
                sell_qty=king_bishop['sell_qty'], 
                running_close_legs=running_close_legs,
                ticker_time_frame_origin=ticker_time_frame,
                first_sell=first_sell, 
                time_intrade=time_in_trade_datetime)
                return {'bee_sell': True, 'order_vars': order_vars, 'app_request': king_bishop['app_request'], 'bishop_keys':bishop_keys}
            else:
                return {'bee_sell': False, 'run_order': run_order}
        
        except Exception as e:
            print(e, print_line_of_error())
            log_error_dict = logging_log_message(log_type='error', msg=f'{client_order_id}{": unable to process kings read on queen order"}', error=str(e), origin_func='king Evaluate QueenOrder')
            logging.error(log_error_dict)


    def stop_queen_order_from_kingbishop(run_order, info='false, order_trig_sell_stop or qty_avilable'):
        

        if run_order == False:
            return True
        # Stop Queen Order from going to the Kings Court
        if str(run_order['order_trig_sell_stop']).lower() == 'true': ### consider remaining qty
            return True
        
        if float(run_order['qty_available']) <= 0:
            return True
        else:
            return False

    
    def god_save_the_queen(QUEEN, QUEENsHeart=False, charlie_bee=False, save_q=False, save_acct=False, save_rr=False, save_qo=False, active_queen_order_states=active_queen_order_states):
        
        s_loop = datetime.now(est)
        try:
            # Save Heart to avoid saving Queen to improve speed
            if charlie_bee:
                QUEENsHeart.update({"charlie_bee": charlie_bee})
            if QUEENsHeart:
                QUEENsHeart['heartbeat'] = QUEEN['heartbeat']
                QUEENsHeart.update({"heartbeat_time": datetime.now(est)})
                PickleData(QUEEN['dbs'].get('PB_QUEENsHeart_PICKLE'), QUEENsHeart)
            if save_q:
                PickleData(QUEEN['dbs'].get('PB_QUEEN_Pickle'), QUEEN)
            if save_qo:
                df = QUEEN.get('queen_orders')
                df = df[df['queen_order_state'].isin(active_queen_order_states)]
                PickleData(QUEEN['dbs'].get('PB_Orders_Pickle'), {'queen_orders': df})
            if save_acct:
                PickleData(QUEEN['dbs'].get('PB_account_info_PICKLE'), {'account_info': QUEEN.get('account_info')})
            if save_rr:
                PickleData(QUEEN['dbs'].get('PB_RevRec_PICKLE'), {'revrec': QUEEN.get('revrec')})
            
            return True
        except Exception as e:
            print_line_of_error(e)
            sys.exit()
    

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

    def order_management(BROKER, STORY_bee, QUEEN, QUEEN_KING, api, QUEENsHeart, charlie_bee): 


        def queen_orders_main(QUEEN, STORY_bee, QUEEN_KING, charlie_bee):
            ### TO DO ###
            try:
                s_loop = datetime.now(est)
                revrec = QUEEN.get('revrec')
                waveview = revrec.get('waveview')
                # wv_symbols = list(set(waveview['symbol'].to_list()))

                def route_queen_order(QUEEN, queen_order, queen_order_idx, order_status, priceinfo, charlie_bee):
                    s_time = datetime.now(est)

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
                                        QUEEN['queen_orders'].at[queen_order_idx, 'queen_order_state'] = 'completed'
                                        logging_log_message(log_type='critical', msg='but why?')
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
                                        update_latest_queen_order_status(order_status=order_status, queen_order_idx=queen_order_idx)
                                        update_origin_order_qty_available(QUEEN=QUEEN, run_order_idx=queen_order_idx, RUNNING_CLOSE_Orders=RUNNING_CLOSE_Orders, RUNNING_Orders=RUNNING_Orders)
                                        update_queen_order_profits(ticker=queen_order.get('ticker'), queen_order=queen_order, queen_order_idx=queen_order_idx, priceinfo=priceinfo)
                                        QUEEN['queen_orders'].at[queen_order_idx, 'status_q'] = "filled"
                                
                                elif order_status['side'] == 'sell':

                                    # closing order, update origin order profits attempt to close out order
                                    origin_order = return_origin_order(df_queenorders=QUEEN['queen_orders'], exit_order_link=queen_order['exit_order_link'])
                                    origin_order_idx = origin_order.get('origin_idx')
                                    origin_order = origin_order.get('origin_order')
                                    if origin_order_idx:
                                        # confirm profits
                                        profit_loss_value = update_runCLOSE__queen_order_honey(queen_order=queen_order, origin_order=origin_order, queen_order_idx=queen_order_idx)['profit_loss_value']
                                        QUEEN['queen_orders'].at[queen_order_idx, 'queen_order_state'] = 'completed'

                                    #### CHECK to see if Origin ORDER has Completed LifeCycle ###
                                        res = update_origin_orders_profits(queen_order=queen_order, origin_order=origin_order, origin_order_idx=origin_order_idx)
                                        closing_filled = res['closing_filled']
                                        profit_loss = res['profit_loss']
                                        print('closing filled: ', profit_loss_value, 'profit_loss: ', profit_loss)
                                        logging.info(('closing filled: ', profit_loss_value, 'profit_loss: ', profit_loss))
                                        # Qty Available
                                        update_origin_order_qty_available(QUEEN=QUEEN, run_order_idx=origin_order_idx, RUNNING_CLOSE_Orders=RUNNING_CLOSE_Orders, RUNNING_Orders=RUNNING_Orders)
                                        # Check to complete Queen Order
                                        check_origin_order_status(QUEEN=QUEEN, origin_order=origin_order, origin_idx=origin_order_idx, closing_filled=closing_filled)

                                    
                            elif alp_order_status in partially_filled:            
                                if order_status['side'] == 'buy':
                                    QUEEN['queen_orders'].at[queen_order_idx, 'queen_order_state'] = "running_open"

                                    update_latest_queen_order_status(order_status=order_status, queen_order_idx=queen_order_idx)
                                    update_queen_order_profits(ticker=queen_order.get('ticker'), queen_order=queen_order, queen_order_idx=queen_order_idx, priceinfo=priceinfo)
                                    update_origin_order_qty_available(QUEEN=QUEEN, run_order_idx=queen_order_idx, RUNNING_CLOSE_Orders=RUNNING_CLOSE_Orders, RUNNING_Orders=RUNNING_Orders)

                                    return {'resp': "running_open"}
                                elif order_status['side'] == 'sell':
                                    # closing order, update origin order profits attempt to close out order
                                    origin_order = return_origin_order(df_queenorders=QUEEN['queen_orders'], exit_order_link=queen_order['exit_order_link'])
                                    origin_order_idx = origin_order.get('origin_idx')
                                    origin_order = origin_order.get('origin_order')
                                    
                                    if origin_order_idx:
                                        # update profits keep in running 
                                        update_runCLOSE__queen_order_honey(queen_order=queen_order, origin_order=origin_order, queen_order_idx=queen_order_idx)
                                        QUEEN['queen_orders'].at[queen_order_idx, 'queen_order_state'] = 'running_close'
                                        
                                        update_origin_orders_profits(queen_order=queen_order, origin_order=origin_order, origin_order_idx=origin_order_idx)
                                        update_queen_order_profits(ticker=queen_order.get('ticker'), queen_order=queen_order, queen_order_idx=queen_order_idx, priceinfo=priceinfo)
                                        update_origin_order_qty_available(QUEEN=QUEEN, run_order_idx=origin_order_idx, RUNNING_CLOSE_Orders=RUNNING_CLOSE_Orders, RUNNING_Orders=RUNNING_Orders)

                                else:
                                    print("Critical Error New Order Side")
                                    logging_log_message(log_type='error', msg='Critical Error New Order Side')
                            else:
                                print("critical errror new order type received")
                                logging_log_message(log_type='error', msg='critical errror new order type received')
                                return False
                        
                            
                            return QUEEN['queen_orders'].loc[queen_order_idx].to_dict()

                        except Exception as e:
                            print('queen router failed', e, print_line_of_error())
                    
                    """ 
                    1. assign queen order state
                    2. Update Queen Order Info
                    """

                    try:

                        # 1 check if order fulfilled
                        # 2 update filled qty & $
                        # 3 Process Queen Order State
                        # 4 validate RUNNING # check if run_order needs to be arhived?
                        
                        current_updated_at = [queen_order['updated_at'] if 'updated_at' in queen_order.keys() else False][0]
                        
                        if current_updated_at != order_status['updated_at']:
                            print("Queen Order Updated")
                        
                        queen_order = update_latest_queen_order_status(order_status=order_status, queen_order_idx=queen_order_idx)
                        queen_order = alpaca_queen_order_state(QUEEN=QUEEN, order_status=order_status, queen_order=queen_order, queen_order_idx=queen_order_idx, priceinfo=priceinfo)

                        QUEEN['queen_orders'].at[queen_order_idx, 'updated_at'] = order_status['updated_at']
                        

                        charlie_bee['queen_cyle_times']['om_route_queenorder__om'] = (datetime.now(est) - s_time).total_seconds()

                        return QUEEN['queen_orders'].loc[queen_order_idx].to_dict()

                    except Exception as e:
                        print(e, print_line_of_error())
                        print("Unable to Route Queen Order")
                        logging.error({'queen order client id': queen_order['client_order_id'], 'msg': 'unable to route queen order', 'error': str(e)})
                

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


                try: # App Requests
                    s_app = datetime.now(est)
                    process_app_requests(QUEEN=QUEEN, QUEEN_KING=QUEEN_KING, request_name='update_queen_order')
                    charlie_bee['queen_cyle_times']['om_app_req_om'] = (datetime.now(est) - s_app).total_seconds()
                except Exception as e:
                    print('APP: Queen Order Main FAILED PROCESSING ORDER', e, print_line_of_error())
                    log_error_dict = logging_log_message(log_type='error', msg='APP: Queen Order Main FAILED PROCESSING ORDER', error=str(e), origin_func='Quen Main Orders')
                    logging.error(log_error_dict)

                s_loop = datetime.now(est)
                df = QUEEN['queen_orders']
                if len(df) == 1:
                    # print("First Order")
                    QUEEN['queen_orders']['client_order_id'] = QUEEN['queen_orders'].index
                    df = QUEEN['queen_orders']

                df['index'] = df.index
                queen_orders__index_dic = dict(zip(df['client_order_id'], df['index']))
                df_active = df[df['queen_order_state'].isin(active_queen_order_states)].copy()
                qo_active_index = df_active['index'].to_list()
                
                # WORKERBEE move info just api?
                def long_short_queenorders(df_active, QUEEN, col_metric='cost_basis_current'):
                    long = sum(df_active[df_active['trigname'].str.contains('buy')].get(col_metric))
                    short = sum(df_active[~df_active['trigname'].str.contains('buy')].get(col_metric))
                    QUEEN['heartbeat']['long'] = round(long)
                    QUEEN['heartbeat']['short'] = round(short)

                    return True
                long_short_queenorders(df_active, QUEEN, col_metric='cost_basis_current')
                
                def gather_orders_as_dict(qo_active_index):
                    queen_order__s = [] 
                    for idx in qo_active_index:
                        run_order = QUEEN['queen_orders'].loc[idx].to_dict()
                        fix_crypto_ticker(QUEEN=QUEEN, ticker=run_order['ticker'], idx=idx)
                        queen_order__s.append(QUEEN['queen_orders'].loc[idx].to_dict())
                    return queen_order__s
                
                queen_order__s = gather_orders_as_dict(qo_active_index)
                charlie_bee['queen_cyle_times']['gather_orders_as_dict'] = (datetime.now(est) - s_loop).total_seconds()

                s_time = datetime.now(est)
                symbols = list(set(df_active['symbol'].to_list()))
                
                # Price Info Symbols
                snapshot_price_symbols = async_api_alpaca__snapshots_priceinfo(symbols, STORY_bee, api, QUEEN)
                df_priceinfo_symbols = pd.DataFrame(snapshot_price_symbols)
                df_priceinfo_symbols = df_priceinfo_symbols.set_index('ticker', drop=False)
                update_queens_priceinfo_symbols(QUEEN, df_priceinfo_symbols)
                
                charlie_bee['queen_cyle_times']['om_priceinfo_api'] = (datetime.now(est) - s_time).total_seconds()

                s_time_qOrders = datetime.now(est)
                if len(queen_order__s) == 0:
                    print("no orders")
                    return False

                # api # refresh all broker orders which are still pending 
                for c_order_id in qo_active_index:
                    pull_order_status = df_active.at[c_order_id, 'status_q']
                    if c_order_id not in BROKER['broker_orders'].index or pull_order_status == 'pending':
                        try:
                            order_status = check_order_status(api=api, client_order_id=c_order_id)
                            if order_status:
                                update_broker_order_status(BROKER, order_status)
                        except Exception as e:
                            print("reeally", e)
                charlie_bee['queen_cyle_times']['om_order_status_api'] = (datetime.now(est) - s_time_qOrders).total_seconds()

                # QUEEN['order_status_info'] = order_status_info # open key in QUEEN to use

                s_time = datetime.now(est)
                queen_orders__dict = {}
                for idx in qo_active_index:
                    # Queen Order Local Vars
                    run_order = QUEEN['queen_orders'].loc[idx].to_dict()
                    runorder_client_order_id = run_order['client_order_id']
                    symbol = run_order.get('symbol')
                    crypto = True if symbol in crypto_currency_symbols else False
                    
                    try: 
                        # snapshot prices bar
                        priceinfo = QUEEN['price_info_symbols'].at[symbol, 'priceinfo']
                        
                        # order_status = [ord_stat for ord_stat in order_status_info if ord_stat['client_order_id'] == runorder_client_order_id]
                        order_status = BROKER['broker_orders'].loc[idx].to_dict()

                        # Process Queen Order States
                        run_order = route_queen_order(QUEEN=QUEEN, 
                                                      queen_order=run_order, 
                                                      queen_order_idx=idx, 
                                                      order_status=order_status, 
                                                      priceinfo=priceinfo, 
                                                      charlie_bee=charlie_bee) ## send in order_status

                        if float(run_order.get('qty_available')) > 0 and run_order.get('order_trig_sell_stop') == True:
                            # print('run order')
                            release_trig_sell_stop(QUEEN=QUEEN, ticker=symbol, client_order_id=run_order.get('client_order_id'))

                        if run_order['queen_order_state'] in ["error", "completed"]:
                            continue
                        
                        if run_order['queen_order_state'] not in RUNNING_Orders:
                            continue

                        if stop_queen_order_from_kingbishop(run_order): # false, order_trig_sell_stop or qty_avilable
                            continue

                        ## subconsicous here ###
                        if run_order['ticker_time_frame'] not in STORY_bee.keys():
                            # Handle Order if Ticker Stream Turned off I.E. Not in STORY_bee
                            conscience_update(QUEEN, root_name='app_info', thought_dict={'ticker_time_frame': run_order['ticker_time_frame'], 'msg': f'{run_order["symbol"]} open order and ticker not active Handle Order Manually'})                    
                        # else:
                        #     conscience_update(QUEEN, root_name='app_info', conscience=False)
                        
                        queen_orders__dict[runorder_client_order_id] = {'run_order': run_order, 'priceinfo': priceinfo}
                                    
                    except Exception as e:
                        print('Queen Order Main FAILED PROCESSING ORDER', e, print_line_of_error())
                        log_error_dict = logging_log_message(log_type='error', msg='Queen Order Main FAILED PROCESSING ORDER', error=str(e), origin_func='Quen Main Orders')
                        logging.error(log_error_dict)
                        ipdb.set_trace()
                        # archive order?
                        # QUEEN['queen_orders'].at[idx, 'queen_order_state'] = 'error'

                charlie_bee['queen_cyle_times']['om_loop_queen_orders__om'] = (datetime.now(est) - s_time).total_seconds()

                if len(queen_orders__dict) > 0 :
                    pass
                else:
                    return False

                s_time_qOrders = datetime.now(est)
                king_bishop_queen_order__EvalOrder = async_send_queen_orders__to__kingsBishop_court(queen_orders__dict, revrec)
                charlie_bee['queen_cyle_times']['om_async_kingsBishop__queenOrders__om'] = (datetime.now(est) - s_time_qOrders).total_seconds()

                for king_eval_order in king_bishop_queen_order__EvalOrder:
                    if king_eval_order['bee_sell']:
                        exx = execute_order(
                                api=api, 
                                QUEEN=QUEEN,
                                blessing=king_eval_order['bishop_keys'],
                                king_resp=False, 
                                king_eval_order=king_eval_order,
                                side='sell',
                                order_type=king_eval_order['bishop_keys']['order_type'],
                                trading_model=None,
                                ticker=king_eval_order['bishop_keys']['ticker'], 
                                ticker_time_frame=king_eval_order['bishop_keys'].get('ticker_time_frame'),
                                trig=king_eval_order['bishop_keys']['trigname'], 
                                run_order_idx=queen_orders__index_dic[king_eval_order['bishop_keys']['client_order_id']], 
                                crypto=king_eval_order['bishop_keys']['qo_crypto'],
                                app_request=king_eval_order['app_request']
                            )
                        if exx.get('executed'):
                            append_queen_order(QUEEN, exx.get('new_queen_order_df'))
                            logging.info(exx.get('msg'))
                            print("exsell", exx.get('msg'))

                            # Hold ORDER from being SOLD again until Release Validation
                            origin_order_idx = exx.get('new_queen_order_df').at[exx.get('new_queen_order_df').index[0], 'exit_order_link']
                            QUEEN['queen_orders'].at[origin_order_idx, 'order_trig_sell_stop'] = True
                            
                            # if type(QUEEN['queen_orders'].at[exx.get('exit_order_link'), 'sell_reason']) is dict:
                            #     QUEEN['queen_orders'].at[exx.get('exit_order_link'), 'sell_reason'].update({exx.get('client_order_id'): {'sell_reason': king_eval_order['order_vars'].get('sell_reason')}})
                            
                            update_origin_order_qty_available(QUEEN=QUEEN, run_order_idx=origin_order_idx, RUNNING_CLOSE_Orders=RUNNING_CLOSE_Orders, RUNNING_Orders=RUNNING_Orders)
                            
                            # try:
                            #     msg = f'ExOrder {king_eval_order["order_vars"].get("sell_reason")} {king_eval_order["bishop_keys"].get("ticker_time_frame")} {king_eval_order["order_vars"].get("qty")} {round(king_eval_order["order_vars"].get("qty") * king_eval_order["order_vars"].get("priceinfo_order").get("ask"),2):,}' # 
                            #     logging.info(msg)
                            #     print(msg)
                            # except Exception as e:
                            #     print(e)
                        save_queen = True
                        QUEEN['revrec'] = refresh_chess_board__revrec(QUEEN['account_info'], QUEEN, QUEEN_KING, STORY_bee, active_queen_order_states=active_queen_order_states, chess_board__revrec={}, revrec__ticker={}, revrec__stars={}) ## Setup Board

                        god_save_the_queen(QUEENsHeart=QUEENsHeart, QUEEN=QUEEN, charlie_bee=charlie_bee,
                                        save_q=True,
                                        save_rr=True,
                                        save_qo=True)
                
                charlie_bee['queen_cyle_times']['full_loop_queenorderS__om'] = (datetime.now(est) - s_loop).total_seconds()
                
                return True
            
            except Exception as e:
                print(e)
                print_line_of_error()
                return False


        #### MAIN ####
        # >for every ticker position join in running-positions to account for total position
        # >for each running position determine to exit the position                
        try:
            # Submitted Orders First
            s_loop = datetime.now(est)
            qo_main = queen_orders_main(QUEEN=QUEEN, STORY_bee=STORY_bee, QUEEN_KING=QUEEN_KING, charlie_bee=charlie_bee)
            charlie_bee['queen_cyle_times']['om_queen_orders___main'] = (datetime.now(est) - s_loop).total_seconds()

            # # God Save the Queen
            # if qo_main:
            #     acct_info = QUEEN['account_info']
            #     QUEEN['revrec'] = refresh_chess_board__revrec(acct_info, QUEEN, QUEEN_KING, STORY_bee, active_queen_order_states=active_queen_order_states, chess_board__revrec={}, revrec__ticker={}, revrec__stars={}) ## Setup Board

            #     god_save_the_queen(QUEENsHeart=QUEENsHeart, QUEEN=QUEEN, charlie_bee=charlie_bee,
            #                        save_q=True,
            #                        save_rr=True,)
        
        except Exception as e:
            print(e)
            print_line_of_error()
            raise e
        return True


    def refresh_QUEEN_starTickers(QUEEN, STORY_bee, ticker_allowed, story_heartrate=54):
        try:

            now_time = datetime.now(est)

            original_state = QUEEN['heartbeat']['available_tickers']
            
            QUEEN['heartbeat']['available_tickers'] = [i for (i, v) in STORY_bee.items() if (now_time - v['story']['time_state']).total_seconds() < story_heartrate]
            ticker_set = set([i.split("_")[0] for i in QUEEN['heartbeat']['available_tickers']])

            QUEEN['heartbeat']['active_tickers'] = [i for i in ticker_set if i in ticker_allowed]
            current_wave = star_ticker_WaveAnalysis(STORY_bee=STORY_bee, ticker_time_frame='SPY_1Minute_1Day').get('current_wave')
            QUEEN['heartbeat']['current_wave'] = current_wave ## REMOVE?
            
            for old_item in ['added_list', 'active_tickerStars', 'dropped_list']:
                if old_item in QUEEN['heartbeat'].keys():
                    print('clean heart')
                    QUEEN['heartbeat'].pop(old_item)

            # new_active = QUEEN['heartbeat']['available_tickers']

            # # if 'story_lastseen' not in 
            # # QUEEN['heartbeat']['story_lastseen'].update({i: datetime.now(est) for i in QUEEN['heartbeat']['available_tickers'].keys()})
            # if original_state != new_active:
            #     print('added dropped / updated tickers')
            #     added_list = []
            #     for ttframe in new_active:
            #         if ttframe not in original_state:
            #             added_list.append({ttframe: return_timestamp_string()})
            #             # print("dropped", ttframe, return_timestamp_string())
            #     if len(added_list) > 0:
            #         print("Added ", added_list)
                
            #     dropped_list = []
            #     for ttframe in original_state:
            #         if ttframe not in new_active:
            #             dropped_list.append({ttframe: return_timestamp_string()})
            #             # print("dropped", ttframe, return_timestamp_string())
            #     if len(dropped_list) > 0:
            #         print("dropped ", dropped_list)

                # QUEEN['heartbeat']['added_list'] = added_list
                # QUEEN['heartbeat']['dropped_list'] = dropped_list

            return QUEEN
        except Exception as e:
            print("ERROR", print_line_of_error())
    
    
    def hanlde_missing_broker_orders_with_queen_orders(BROKER, QUEEN):

        def add_missing_broker_order_to_queen_orders(QUEEN, broker_order):
            # WORKERBEE append missing broker order new order to queen orders
            return True
        
        broker_corder_ids = BROKER['broker_orders']['client_order_ids'].tolist() # only reconcile latest DAYs orders
        for c_order_id in broker_corder_ids:
            if c_order_id not in QUEEN['queen_orders'].index:
                print("order in broker missing from queen orders add order to queen orders")

    # def catch_up_queen_order_status(BROKER, QUEEN)
    def update_broker_order_status(BROKER, order_status):
        try:
            broker_orders = BROKER['broker_orders']
            df_token = pd.DataFrame([order_status]).set_index('client_order_id', drop=False)
            if df_token.index[0] in broker_orders.index:
                broker_orders = broker_orders[broker_orders['client_order_id'] != df_token.index[0]]
            
            broker_orders = pd.concat([broker_orders, df_token])
            BROKER['broker_orders'] = broker_orders
            
            PickleData(BROKER.get('source'), BROKER)
            return True
        except Exception as e:
            print_line_of_error("broker update failed")


    def reconcile_broker_orders_with_queen_orders(BROKER, api, QUEEN, active_queen_order_states, save_orders=False, b_order_init=False):
        
        if len(BROKER['broker_orders']) == 0:
            print("INIT Broker ORDERS")
            b_order_init = True
            BROKER = init_broker_orders(api, BROKER)

        # check for any missing orders
        df = QUEEN.get('queen_orders')
        df['status_q'] = df['status_q'].fillna('')
        df_active = df[df['queen_order_state'].isin(active_queen_order_states)].copy()
        df_active['client_order_id'] = df_active['client_order_id'].fillna('init')
        qo_active_index = df_active['index'].to_list()
        broker_corder_ids = BROKER['broker_orders']['client_order_id'].tolist()
        for client_order_id in qo_active_index:
            if client_order_id not in broker_corder_ids and client_order_id != 'init':
                save_orders = True
                try:
                    order_status = check_order_status(api=api, client_order_id=client_order_id)
                    if order_status:
                        update_broker_order_status(BROKER, order_status)
                    if b_order_init:
                        if df_active.at[client_order_id, 'status'] == 'filled':
                            QUEEN['queen_orders'].at[client_order_id, 'status_q'] = 'filled'
                        else:
                            QUEEN['queen_orders'].at[client_order_id, 'status_q'] = 'pending'
                except Exception as e:
                    print("weeeee", e)

        if save_orders:
            PickleData(QUEEN['dbs'].get('PB_broker_PICKLE'), BROKER)

        return True
        
        
    
    def init_broker_orders(api, BROKER):

        init_api_orders_start_date =(datetime.now() - timedelta(days=100)).strftime("%Y-%m-%d")
        init_api_orders_end_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        api_orders = initialize_orders(api, init_api_orders_start_date, init_api_orders_end_date, symbols=False, limit=500)
        queen_orders_closed = api_orders.get('closed')
        queen_orders_open = api_orders.get('open')
        c_order_ids_dict_closed = [vars(queen_orders_closed[n])['_raw'] for n in range(len(queen_orders_closed))]
        c_order_ids_dict_open = [vars(queen_orders_open[n])['_raw'] for n in range(len(queen_orders_open))]
        broker_orders = c_order_ids_dict_closed + c_order_ids_dict_open
        broker_orders = pd.DataFrame(broker_orders).set_index('client_order_id', drop=False)

        BROKER['broker_orders'] = broker_orders

        return BROKER


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

        db_root = init_clientUser_dbroot(client_username=client_user) # main_root = os.getcwd() // # db_root = os.path.join(main_root, 'db')

        print(
        """
        pollenq:
        We all shall prosper through the depths of our connected hearts,
        Not all will share my world,
        So I put forth my best mind of virtue and goodness, 
        Always Bee Better
        """, timestamp_string()
        )

        init_logging(queens_chess_piece=queens_chess_piece, db_root=db_root, prod=prod, loglevel='warning')

        KING = ReadPickleData(master_swarm_KING(prod=prod))
        # init files needed
        qb = init_queenbee(client_user=client_user, prod=prod, queen=True, queen_king=True, api=True, broker=True, init=True)
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
            PickleData(pickle_file=QUEEN['dbs'].get('PB_QUEEN_Pickle'), data_to_store=QUEEN)
            sys.exit()

        trading_days = hive_dates(api=api)['trading_days']
        
        reconcile_broker_orders_with_queen_orders(BROKER, api, QUEEN, active_queen_order_states, save_orders=False)

        # portfolio = return_alpc_portolio(api)['portfolio']
        ## !! Reconcile all orders processed in alpaca vs queen_order !! ##

        # Ticker database of pollenstory ## Need to seperate out into tables 
        ticker_db = return_QUEENs__symbols_data(QUEEN=QUEEN, QUEEN_KING=QUEEN_KING, read_storybee=True, read_pollenstory=False) ## async'd func
        # POLLENSTORY = ticker_db.get('pollenstory')
        STORY_bee = ticker_db.get('STORY_bee')
        QUEEN['heartbeat']['ticker_db'] =  {'errors': ticker_db.get('errors')}

        # add new keys
        QUEEN_req = add_key_to_QUEEN(QUEEN=QUEEN, queens_chess_piece=queens_chess_piece)
        if QUEEN_req['update']:
            QUEEN = QUEEN_req['QUEEN']
            PickleData(QUEEN['dbs'].get('PB_QUEEN_Pickle'), QUEEN)


        logging.info("My Queen")

        QUEEN['heartbeat']['main_indexes'] = {
            'SPY': {'long1X': "SPY",
                    'long3X': 'SPXL', 
                    'inverse1X': 'SH', 
                    'inverse2X': 'SDS', 
                    'inverse3X': 'SPXU'},
            'QQQ': {'long3X': 'TQQQ', 
                    'inverse1X': 'PSQ', 
                    'inverse2X': 'QID', 
                    'inverse3X': 'SQQQ'}
            }

        QUEEN['heartbeat']['active_order_state_list'] = active_order_state_list
        
        ticker_allowed = list(KING['ticker_universe'].get('alpaca_symbols_dict').keys())

        QUEEN = refresh_QUEEN_starTickers(QUEEN, STORY_bee, ticker_allowed)

        available_triggerbees = ["sell_cross-0", "buy_cross-0"]

        QUEEN['heartbeat']['available_triggerbees'] = available_triggerbees

        PickleData(QUEEN['dbs'].get('PB_QUEEN_Pickle'), QUEEN)
        print(f'ProdEnv {prod} Here we go Mario')

        ########################################################
        ########################################################
        #############The Infinite Loop of Time #################
        ########################################################
        ########################################################
        ########################################################

        queens_charlie_bee, charlie_bee = init_charlie_bee(db_root) # monitors queen order cycles, also seen in heart

        while True:
            s = datetime.now(est)
            # Should you operate now? I thnik the brain never sleeps ?
            mkhrs = return_market_hours(trading_days=trading_days)
            if mkhrs != 'open':
                print("Queen to ZzzzZZzzzZzzz see you tomorrow")
                break
            
            # if queens_chess_piece.lower() == 'queen': # Rule On High
            seconds_to_market_close = (datetime.now(est).replace(hour=16, minute=0, second=0) - datetime.now(est)).total_seconds()
            
            """ The Story of every Knight and their Quest """
            s = datetime.now(est)
            # refresh db
            s_time = datetime.now(est)
            # QUEEN Databases
            KING = ReadPickleData(master_swarm_KING(prod=prod)) # WORKERBEE only check if KING needs to be reloaded
            # QUEENBEE = ReadPickleData(master_swarm_QUEENBEE(prod=prod))
            QUEEN_KING = ReadPickleData(QUEEN['dbs'].get('PB_App_Pickle')) # WORKERBEE only check if KING needs to be reloaded
            QUEEN['chess_board'] = QUEEN_KING['chess_board']

            # symbol ticker data >>> 1 all current pieces on chess board && all current running orders
            ticker_db = return_QUEENs__symbols_data(QUEEN=QUEEN, QUEEN_KING=QUEEN_KING, read_storybee=True, read_pollenstory=False) ## async'd func
            # POLLENSTORY = ticker_db['pollenstory']
            STORY_bee = ticker_db['STORY_bee']

            QUEEN = refresh_QUEEN_starTickers(QUEEN=QUEEN, STORY_bee=STORY_bee, ticker_allowed=ticker_allowed)
            charlie_bee['queen_cyle_times']['db_refresh'] = (datetime.now(est) - s_time).total_seconds()

            """Account Info"""
            # WORKERBEE WHEN BROKER FAILS TO RETURN how to handle?
            def refresh_broker_account_portolfio(api, QUEEN, account=False, portfolio=False):
                if portfolio:
                    portfolio = return_alpc_portolio(api)['portfolio']
                    QUEEN['portfolio'] = portfolio
                if account:
                    acct_info = refresh_account_info(api=api)['info_converted']
                    QUEEN['account_info'] = acct_info
            
            refresh_broker_account_portolfio(api, QUEEN, account=True, portfolio=True)
            acct_info = QUEEN['account_info']
            portfolio = QUEEN['portfolio']

            PickleData(QUEEN['dbs'].get('PB_account_info_PICKLE'), {'account_info': QUEEN.get('account_info')})

            charlie_bee['queen_cyle_times']['cc_block1_account'] = (datetime.now(est) - s_time).total_seconds()

            # Read client App Reqquests
            s_time = datetime.now(est)
            process_app_requests(QUEEN=QUEEN, QUEEN_KING=QUEEN_KING, request_name='queen_sleep', archive_bucket=False)
            process_app_requests(QUEEN=QUEEN, QUEEN_KING=QUEEN_KING, request_name='subconscious', archive_bucket='subconscious_requests')
            charlie_bee['queen_cyle_times']['app'] = (datetime.now(est) - s_time).total_seconds()

            # Refresh Board
            revrec = refresh_chess_board__revrec(acct_info, QUEEN, QUEEN_KING, STORY_bee, active_queen_order_states=active_queen_order_states, chess_board__revrec={}, revrec__ticker={}, revrec__stars={}) ## Setup Board
            charlie_bee['queen_cyle_times']['cc_revrec'] = revrec.get('cycle_time')
            QUEEN['revrec'] = revrec
            god_save_the_queen(QUEEN=QUEEN, save_rr=True, save_acct=True) # WORKERBEE unessecary SAVING only save whats needed

            # Process All Orders
            s_time = datetime.now(est)
            order_management(BROKER, STORY_bee, QUEEN, QUEEN_KING, api, QUEENsHeart, charlie_bee)
            charlie_bee['queen_cyle_times']['order management'] = (datetime.now(est) - s_time).total_seconds()

            # Hunt for Triggers
            if seconds_to_market_close > 30:
                s_time = datetime.now(est)
                
                command_conscience(QUEENsHeart=QUEENsHeart, QUEEN=QUEEN, STORY_bee=STORY_bee, QUEEN_KING=QUEEN_KING, api=api) ##### >   
                charlie_bee['queen_cyle_times']['command conscience'] = (datetime.now(est) - s_time).total_seconds()
                e = datetime.now(est)
                if 'QUEEN_avg_cycle' not in charlie_bee['queen_cyle_times'].keys():
                    charlie_bee['queen_cyle_times']['QUEEN_avg_cycle'] = deque([], 89)
                charlie_bee['queen_cyle_times']['QUEEN_avg_cycle'].append((datetime.now(est) - s).total_seconds())
                charlie_bee['queen_cyle_times']['QUEEN_avg_cycletime'] = sum(charlie_bee['queen_cyle_times']['QUEEN_avg_cycle'])/len(charlie_bee['queen_cyle_times']['QUEEN_avg_cycle'])
                PickleData(queens_charlie_bee, charlie_bee)
            
            e = datetime.now(est)
            beat = (e - s).seconds
            god_save_the_queen(QUEEN, QUEENsHeart, charlie_bee, save_qo=True)
            # print(queens_chess_piece, str((e - s).seconds),  "sec: ", datetime.now().strftime("%A,%d. %I:%M:%S%p"))
            if beat > 10:
                logging.warning((queens_chess_piece, ": cycle time > 10 seconds:  SLOW cycle: ", (e - s).seconds ))
                print(queens_chess_piece, str(beat),  "sec: ", datetime.now().strftime("%A,%d. %I:%M:%S%p"))
                print('use price gauge') # (STORY_bee["SPY_1Minute_1Day"]["story"]["price_gauge"])
    
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
        parser.add_argument ('-client_user', default='stefanstapinski@gmail.com')
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