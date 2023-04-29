# QueenBee
import logging
# from multiprocessing.pool import RUN
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
from chess_piece.king import kingdom__global_vars, print_line_of_error, master_swarm_KING, return_QUEENs__symbols_data, kingdom__grace_to_find_a_Queen, master_swarm_QUEENBEE, ReadPickleData, PickleData
from chess_piece.queen_hive import initialize_orders, refresh_account_info, refresh_chess_board__revrec, return_ttf_remaining_budget, init_clientUser_dbroot, queens_heart, get_best_limit_price, hive_dates, return_alpaca_user_apiKeys, send_email, return_STORYbee_trigbees, init_logging, convert_to_float, order_vars__queen_order_items, create_QueenOrderBee, init_pollen_dbs, story_view, logging_log_message, return_alpc_portolio, return_market_hours,  add_key_to_app, pollen_themes, check_order_status,  timestamp_string, submit_order, return_timestamp_string, add_key_to_QUEEN


""" ideas 
if prior day abs(change) > 1 ignore ticker for the day!
"""

def queenbee(client_user, prod, queens_chess_piece='queen'):
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
    RUNNING_CLOSE_Orders = king_G.get('RUNNING_CLOSE_Orders') # = ['running_close']

    # crypto
    crypto_currency_symbols = ['BTCUSD', 'ETHUSD', 'BTC/USD', 'ETH/USD']
    coin_exchange = "CBSE"
    # misc
    exclude_conditions = [
        'B','W','4','7','9','C','G','H','I','M','N',
        'P','Q','R','T','V','Z'
    ] # 'U'
    

    prod = True if str(prod).lower() == 'true' else False

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
                df_ = df[df['client_order_id'] == c_order_id].copy()
                order_idx = df_.iloc[-1].name
                for field_, new_value in package.items():
                    try:
                        QUEEN['queen_orders'].at[order_idx, field_] = new_value
                        save = True
                    except Exception as e:
                        print(e, 'failed to update QueenOrder')
                        logging.critical({'msg': 'failed to update queen orders', 'error': e, 'other': (field_, new_value)})
                        QUEEN['queens_messages'].update({c_order_id: {'date': return_timestamp_string(), 'error': e, 'updates': (field_, new_value)}})
            if save:
                PickleData(pickle_file=PB_QUEEN_Pickle, data_to_store=QUEEN, write_temp=False)
        except Exception as e:
            print(e, print_line_of_error())
            logging.CRITICAL({'error': e, 'msg': 'update queen order', 'update_package': update_package})
            QUEEN['queens_messages'].update({'CRITICAL_QueenOrdersUpdates': {'date': return_timestamp_string(), 'error': e, 'update_package': update_package}})
        return True


    def submit_order_validation(ticker, qty, side, portfolio, run_order_idx=False):
        try:
            if side == 'buy':
                # if crypto check avail cash to buy
                # check against buying power validate not buying too much of total portfolio
                if qty < 1:
                    print("Qty Value Not Valid (less then 1) setting to 1")
                    qty = 1.0
                return {'qty_correction': qty}
            elif side == 'sell': # sel == sell
                # print("check portfolio has enough shares to sell")
                if ticker not in portfolio.keys():
                    msg = {"submit order validation()": {'msg': "MISSING_TICKER", 'ticker': ticker}}
                    logging.error(msg)
                    print(msg)
                    QUEEN['queen_orders'].at[run_order_idx, 'queen_order_state'] = 'completed_alpaca'
                    return {'stop_order': 'MISSING_TICKER'}
                position = float(portfolio[ticker]['qty_available'])
                if position > 0 and position < qty: # long
                    msg = {"submit order validation()": {'#of shares avail': position,  'msg': "not enough shares avail to sell, updating sell qty", 'ticker': ticker}}
                    logging.error(msg)
                    print(msg)
                    # QUEEN["errors"].update({f'{symbol}{"_portfolio!=queen"}': {'msg': msg}})
                    
                    qty_correction = position
                    if run_order_idx:
                        # update run_order
                        print('Correcting Run Order Qty with avail qty: ', qty_correction)
                        QUEEN['queen_orders'].at[run_order_idx, 'validation_correction'] = 'true'
                
                    return {'qty_correction': qty_correction}
                else:
                    return {'qty_correction': qty}
            else:
                return {'stop_order': 'MISSING_SIDE'}
        except Exception as e:
            print(e)

    
    def generate_client_order_id(QUEEN, ticker, trig, sellside_client_order_id=False): # generate using main_order table and trig count
        main_orders_table = QUEEN['queen_orders']
        temp_date = datetime.now(est).strftime("%y-%m-%d %M.%S")
        
        if sellside_client_order_id:
            main_trigs_df = main_orders_table[main_orders_table['client_order_id'] == sellside_client_order_id].copy()
            trig_num = len(main_trigs_df) + 1
            order_id = f'{"close__"}{trig_num}-{sellside_client_order_id}-{temp_date}'
        else:
            main_trigs_df = main_orders_table[(main_orders_table['trigname']==trig) & (main_orders_table['exit_order_link'] != 'False')].copy()
            
            trig_num = len(main_trigs_df) + 1
            order_id = f'{"run__"}{ticker}-{trig}-{trig_num}-{temp_date}'

        if order_id in QUEEN['client_order_ids_qgen']:
            msg = {"generate client_order_id()": "client order id already exists change"}
            print(msg)
            logging.error(msg)
            # q_l = len(QUEEN['client_order_ids_qgen'])
            mill_s = datetime.now(est).microsecond
            order_id = f'{order_id}{"_qgen_"}{mill_s}'

        # append created id to QUEEN
        QUEEN['client_order_ids_qgen'].append(order_id)
        PickleData(pickle_file=PB_QUEEN_Pickle, data_to_store=QUEEN)
        
        return order_id





    def process_order_submission(trading_model, order, order_vars, trig, symbol, ticker_time_frame, star, portfolio_name='Jq', status_q=False, exit_order_link=False, priceinfo=False):

        try:
            # Create Running Order
            new_queen_order = create_QueenOrderBee(
            trading_model=trading_model,
            KING=KING, 
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

            QUEEN['queen_orders'] = pd.concat([QUEEN['queen_orders'], new_queen_order_df], axis=0) # , ignore_index=True
            QUEEN['queen_orders']['client_order_id'] = QUEEN['queen_orders'].index
            

            logging.info("Order Bee Created")
            
            return True
        except Exception as e:
            print(e, print_line_of_error())

    
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

                        QUEEN['app_requests__bucket'].append(app_request['app_requests_id'])
                        PickleData(pickle_file=PB_QUEEN_Pickle, data_to_store=QUEEN, write_temp=False)
                        return {'app_flag': True, 'sell_order': True, 'sell_qty': sell_qty, 'type': o_type, 'side': side}
                else:
                    pass
 
        return {'app_flag': False}

    
    def process_app_requests(QUEEN, QUEEN_KING, request_name, archive_bucket=None):
        app_requests__bucket = 'app_requests__bucket'
        try:
            if request_name == "buy_orders": # test
                # archive_bucket = 'buy_orders_requests'
                app_order_base = [i for i in QUEEN_KING[request_name]]
                if app_order_base:
                    for app_request in app_order_base:
                        if app_request['app_requests_id'] in QUEEN[app_requests__bucket]:
                            # print("buy trigger request Id already received")

                            return {'app_flag': False,}
                        else:
                            print("app buy order gather")
                            wave_amo = app_request['wave_amo']
                            r_type = app_request['type']
                            r_side = app_request['side']
                        
                            king_resp = {'side': r_side, 'type': r_type, 'wave_amo': wave_amo }
                            ticker_time_frame = f'{app_request["ticker"]}{"_app_bee"}'
                            
                            return {'king_resp': king_resp, 'app_flag': True, 'app_request': app_request, 'ticker_time_frame': ticker_time_frame,} 
                else:
                    return {'app_flag': False}
            
            elif request_name == "wave_triggers": # test
                app_order_base = [i for i in QUEEN_KING[request_name]]
                if app_order_base:
                    for app_request in app_order_base:
                        if app_request['app_requests_id'] in QUEEN[app_requests__bucket]:
                            # print("wave trigger request Id already received") # waiting for user to refresh client side
                            continue
                            # return {'app_flag': False}
                        else:
                            print("app wave trigger gather", app_request['wave_trigger'], " : ", app_request['ticker_time_frame'])
                            QUEEN[app_requests__bucket].append(app_request['app_requests_id'])
                                
                            return {'app_flag': True, 'app_request': app_request, 'ticker_time_frame': app_request['ticker_time_frame']}
                else:
                    return {'app_flag': False}
            
            elif request_name == "update_queen_order": # test
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

            elif request_name == "knight_bees_kings_rules": ## Order Update to KINGs ORDER RULES
                return False
                archive_bucket = "knight_bees_kings_rules_requests"
                all_items = [i for i in QUEEN_KING[request_name]]
                if all_items:
                    for app_request in all_items:
                        if app_request['app_requests_id'] in QUEEN['app_requests__bucket']:
                            print("Knight Bees request Id already received")
                            QUEEN_KING[archive_bucket].append(app_request)
                            QUEEN_KING[request_name].remove(app_request)
                            PickleData(pickle_file=PB_App_Pickle, data_to_store=QUEEN_KING)
                            return {'app_flag': False}
                        else:
                            print("Knight Bees Change")
                            QUEEN['app_requests__bucket'].append(app_request['app_requests_id'])
                            QUEEN_KING[archive_bucket].append(app_request)
                            QUEEN_KING[request_name].remove(app_request)
                            PickleData(pickle_file=PB_App_Pickle, data_to_store=QUEEN_KING)
                            
                            return {'app_flag': True, 'app_request': app_request}
                else:
                    return {'app_flag': False}

            elif request_name == "queen_sleep": # redo Don't save App
                app_order_base = [i for i in QUEEN_KING[request_name]]
                if app_order_base:
                    for app_request in app_order_base:
                        if app_request['app_requests_id'] in QUEEN['app_requests__bucket']:
                            return {'app_flag': False}
                        else:
                            print("exiting QUEEN stopping queen")
                            QUEEN['app_requests__bucket'].append(app_request['app_requests_id'])
                            PickleData(PB_QUEEN_Pickle, QUEEN)
                            sys.exit()
                            
                            return {'app_flag': True}
                else:
                    return {'app_flag': False}

            elif request_name == "subconscious": # update
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

                            PickleData(PB_QUEEN_Pickle, QUEEN)
                            return {'app_flag': True, 'app_request': app_request}
                else:
                    return {'app_flag': False}

            
            return {'app_flag': False}
        
        except Exception as e:
            print(e, print_line_of_error())

    
    def trig_In_Action_cc(active_orders, trig, ticker_time_frame):
        
        if len(active_orders) > 0:
            # print('trig_action ',  len(active_orders))
            active_orders['order_exits'] = np.where(
                (active_orders['trigname'] == trig) &
                (active_orders['ticker_time_frame_origin'] == ticker_time_frame), 1, 0)
            trigbee_orders = active_orders[active_orders['order_exits'] == 1].copy()
            if len(trigbee_orders) > 0:
                # print('trig in action ',  len(trigbee_orders))
                return trigbee_orders
            else:
                return ''
        else:
            return ''

    def ticker_trig_In_Action_cc(active_orders, trig, ticker):
        
        if len(active_orders) > 0:
            active_orders['order_exits'] = np.where(
                (active_orders['trigname'] == trig) &
                (active_orders['symbol'] == ticker), 1, 0)
            trigbee_orders = active_orders[active_orders['order_exits'] == 1].copy()
            if len(trigbee_orders) > 0:
                # print('trig in action ',  len(trigbee_orders))
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


    def update_origin_order_qty_available(QUEEN, run_order_idx, RUNNING_CLOSE_Orders, RUNNING_Orders):
        try:
            # Return QueenOrder
            queen_order = QUEEN['queen_orders'].loc[run_order_idx].to_dict()
            if queen_order['queen_order_state'] in RUNNING_Orders:
                closing_dfs = return_closing_orders_df(QUEEN=QUEEN, exit_order_link=queen_order['client_order_id'])
                if len(closing_dfs) > 0:
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
                print('Update Origin wtf are you?', queen_order['client_order_id'])
            
            return QUEEN['queen_orders'].loc[run_order_idx].to_dict()
        except Exception as e:
            print(e, print_line_of_error())


        return True


    def execute_order(QUEEN, king_resp, king_eval_order, ticker, ticker_time_frame, trig, portfolio, run_order_idx=False, crypto=False):
        try:
            tic, tframe, tperiod = ticker_time_frame.split("_")
            star = f'{tframe}_{tperiod}'
            
            logging.info({'ex_order()': ticker_time_frame})
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

            portfolio = return_alpc_portolio(api)['portfolio']
            
            # priceinfo = return_snap_priceinfo__pollenData(ticker=ticker)
            if crypto:
                snap = api.get_crypto_snapshot(ticker, exchange=coin_exchange)
            else:
                snap = api.get_snapshot(ticker)

            # get latest pricing
            priceinfo_order = {'price': snap.latest_trade.price, 'bid': snap.latest_quote.bid_price, 'ask': snap.latest_quote.ask_price}
            # priceinfo_order = {'price': priceinfo['current_price'], 'bid': priceinfo['current_bid'], 'ask': priceinfo['current_ask']}
            if king_resp:
                side = 'buy'
                # if app order get order vars its way
                if 'order_vars' not in king_resp.keys():
                    # up pack order vars
                    side = king_resp['side']
                    order_type = king_resp['type']
                    wave_amo = king_resp['wave_amo']
                    limit_price = False
                    trading_model = king_resp['order_vars']
                else:
                    # up pack order vars
                    side = king_resp['order_vars']['order_side']
                    order_type = king_resp['order_vars']['order_type']
                    wave_amo = king_resp['order_vars']['wave_amo']
                    limit_price = king_resp['order_vars']['limit_price']
                    trading_model = king_resp['order_vars']['trading_model']

                if side == 'buy':
                    order_vars = king_resp['order_vars']
                    limit_price = [limit_price if limit_price != False else False][0]
                    print(f'{wave_amo}')
                    limit_price, qty_order = update__validate__qty(crypto=crypto, current_price=priceinfo_order['price'], limit_price=limit_price, wave_amo=wave_amo)
                    print(f'{qty_order}')

                    client_order_id__gen = generate_client_order_id(QUEEN=QUEEN, ticker=ticker, trig=trig)

                    send_order_val = submit_order_validation(ticker=ticker, qty=qty_order, side=side, portfolio=portfolio, run_order_idx=run_order_idx)                    
                    qty_order = send_order_val['qty_correction'] # same return unless more validation done here
                    print(f'{qty_order}')

                    print(f'{side} {order_type} {qty_order}  {client_order_id__gen}')
                    
                    order_submit = submit_order(api=api, symbol=ticker, type=order_type, qty=qty_order, side=side, client_order_id=client_order_id__gen, limit_price=limit_price) # buy
                    if order_submit == False:
                        print(f'{ticker_time_frame} Order Failed log in Hive, Log so you can make this only a warning')

                    logging.info("order submit")
                    order = vars(order_submit)['_raw']

                    if 'borrowed_funds' not in order_vars.keys():
                        order_vars['borrowed_funds'] = None

                    process_order_submission(trading_model=trading_model, 
                    order=order, 
                    order_vars=order_vars,
                    trig=trig,
                    symbol=ticker,
                    ticker_time_frame=ticker_time_frame,
                    star=star,
                    priceinfo=priceinfo_order)

                    PickleData(pickle_file=PB_QUEEN_Pickle, data_to_store=QUEEN)
                    logging.info({'ex__order__confirmed': ticker_time_frame})

                    msg = {'execute order()': {'msg': f'{"order submitted"}{" : at : "}{return_timestamp_string()}', 'ticker': ticker, 'ticker_time_frame': ticker_time_frame, 'trig': trig, 'crypto': crypto, 'wave_amo': wave_amo}}
                    logging.info(msg)
                    print(msg)
                    return{'executed': True, 'msg': msg}
                else:
                    msg = ("error order not accepted", order)
                    print(msg)
                    logging.error(msg)
                    return{'executed': False, 'msg': msg}
            elif king_eval_order:
                side = 'sell'
                if side == 'sell':
                    print("bee_sell")
                    run_order_client_order_id = QUEEN['queen_orders'].at[run_order_idx, 'client_order_id']
                    order_vars = king_eval_order['order_vars']

                    # close out order variables
                    sell_qty = float(king_eval_order['order_vars']['sell_qty']) # float(order_obj['filled_qty'])
                    q_side = king_eval_order['order_vars']['order_side'] # 'sell' Unless it short then it will be a 'buy'
                    q_type = king_eval_order['order_vars']['order_type'] # 'market'
                    sell_reason = king_eval_order['order_vars']['sell_reason']
                    limit_price = king_eval_order['order_vars']['limit_price']

                    # Generate Client Order Id
                    client_order_id__gen = generate_client_order_id(QUEEN=QUEEN, ticker=ticker, trig=trig, sellside_client_order_id=run_order_client_order_id)

                    limit_price, sell_qty = update__sell_qty(crypto, limit_price, sell_qty)

                    # Validate Order
                    send_order_val = submit_order_validation(ticker=ticker, qty=sell_qty, side=q_side, portfolio=portfolio, run_order_idx=run_order_idx)
                    sell_qty = send_order_val.get('qty_correction')
                    if 'stop_order' in send_order_val.keys():
                        print("Order Did not pass to execute")
                        msg = ("Order Did not pass to execute")
                        logging.error(msg)
                        return{'executed': False, 'msg': msg}
                    
                    
                    send_close_order = submit_order(api=api, side=q_side, symbol=ticker, qty=sell_qty, type=q_type, client_order_id=client_order_id__gen, limit_price=limit_price) 
                    send_close_order = vars(send_close_order)['_raw']
                                        
                    if limit_price:
                        print("seeking Honey?")
                    else:
                        print("honey pots")
                    
                    if 'borrowed_funds' not in order_vars.keys():
                        order_vars['borrowed_funds'] = None
                    
                    # Order Vars 
                    process_order_submission(trading_model=False,
                    order=send_close_order, 
                    order_vars=order_vars, 
                    trig=trig, 
                    exit_order_link=run_order_client_order_id,
                    symbol=ticker,
                    ticker_time_frame=ticker_time_frame,
                    star=star,
                    priceinfo=priceinfo_order)

                    QUEEN['queen_orders'].at[run_order_idx, 'order_trig_sell_stop'] = True
                    # QUEEN['queen_orders'].at[run_order_idx, 'sell_reason'].update({client_order_id__gen: {'sell_reason': sell_reason}})
                    QUEEN['queen_orders'].at[run_order_idx, 'sell_reason'] = {client_order_id__gen: {'sell_reason': sell_reason}}
                    update_origin_order_qty_available(QUEEN=QUEEN, run_order_idx=run_order_idx, RUNNING_CLOSE_Orders=RUNNING_CLOSE_Orders, RUNNING_Orders=RUNNING_Orders)

                    PickleData(pickle_file=PB_QUEEN_Pickle, data_to_store=QUEEN)
            else:
                print('Error Ex Order..good luck')
                sys.exit()
        
        except Exception as e:
            print("Error Ex Order..Full Failure" , e, print_line_of_error())
            print(ticker_time_frame)


    def buying_Power_cc(QUEEN_KING, api, client_args="TBD", daytrade=True):
        info = api.get_account()
        argu_validate = ['portfolio', 'daytrade_pct', 'longtrade_pct', 'waveup_pct', 'wavedown_pct']
        
        total_buying_power = info.buying_power # what is the % amount you want to buy?
        cBoard = {}
        qcp_ticker_index = {}
        for qcp, piece in QUEEN_KING['chess_board'].items():
            for ticker in piece.get("tickers"):
                qcp_ticker_index[ticker] = qcp
                

        app_portfolio_day_trade_allowed = .8
        app_portfolio_long_trade_allowed = .2
        if app_portfolio_day_trade_allowed + app_portfolio_long_trade_allowed != 1:
            print("Critical Error Fix buying power numbers")
            sys.exit()
        
        # # wave power allowance
        # app_portfolio_waveup_buying_power = .6
        # app_portfolio_wavedown_buying_power = .4
        # if app_portfolio_waveup_buying_power + app_portfolio_wavedown_buying_power != 1:
        #     print("Critical Error Fix buying power numbers")
        #     sys.exit()
        
        client_total_DAY_trade_amt_allowed = float(app_portfolio_day_trade_allowed) * float(total_buying_power)
        client_total_LONG_trade_amt_allowed = float(app_portfolio_long_trade_allowed) * float(total_buying_power)
        
        return {
            'total_buying_power': total_buying_power,
            'client_total_DAY_trade_amt_allowed': client_total_DAY_trade_amt_allowed, 
            'app_portfolio_day_trade_allowed': app_portfolio_day_trade_allowed,
            'client_total_LONG_trade_amt_allowed': client_total_LONG_trade_amt_allowed,
        }


    def star_ticker_WaveAnalysis(STORY_bee, ticker_time_frame, trigbee=False): # buy/sell cross
        """ Waves: Current Wave, answer questions about proir waves """
        # df_waves_story = STORY_bee[ticker_time_frame]['waves']['story']  # df
        # current_wave = df_waves_story.iloc[-1]

        # ttf_waves = STORY_bee[ticker_time_frame]['waves']

        # ticker, star, frame = ticker_time_frame.split("_")
        
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
        # trigbees = set(df_waves_story['macd_cross'])

        # d_return = {}
        # for trigbee in trigbees:
        #     if trigbee in available_triggerbees:
        #         df_token = df_waves_story[df_waves_story['macd_cross'] == trigbee].copy()
        #         d_return[trigbee] = df_token.iloc[-1]
        
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
        

        # wave slices
        # l_wave_blocktime = [i for i in STORY_bee[ticker_time_frame]['waves'].keys() if 'story' not in i]
        # wave_blocktime_slices ={i: '' for i in l_wave_blocktime}
        # total_waves = len(df_waves_story.keys())
        # morning_waves = {k:v for (k,v) in waves.items() if v['wave_blocktime'] == "morning_9-11"}
        # lunch_waves = {k:v for (k,v) in waves.items() if v['wave_blocktime'] == "lunch_11-2"}
        # afternoon_waves = {k:v for (k,v) in waves.items() if v['wave_blocktime'] == "afternoon_2-4"}
        # afterhours_waves = {k:v for (k,v) in waves.items() if v['wave_blocktime'] == "afterhours"}
        # wave_blocktime_slices[] = morning_waves


        return {'current_wave': current_wave, 'current_active_waves': d_return}


    def king_knights_requests(QUEEN, STORY_bee, revrec, trigbee, ticker_time_frame, trading_model, trig_action, crypto=False):
        # answer all questions for order to be placed, compare against the rules
        # measure len of trigbee how long has trigger been there?
        # Std Deivation from last X trade prices
        # Jump on wave if NOT on Wave?
        # collective BUY only when story MACD tier aligns to certian power NEW THEME
        # Sell on MACD Tier distance (how many tiers have we crossed increment to sell at)  NEW THEME
        # collective MACD triggers? Family Triggers, weights on where trigger is
        # accept trigbee tier when deviation from vwap?
        # did your Previous Trigger make money? 
        # Or did the previous wave go from + to - or vice versa, OR what was the wave frequency? 

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

        def kings_blessing_checks():
            if trigbee not in trading_model['trigbees']: 
                print("Error New Trig not in Queens Mind: ", trigbee )
                return True
            elif "ignore_trigbee_in_macdstory_tier" in king_order_rules.keys():
                if macd_tier in king_order_rules.get("ignore_trigbee_in_macdstory_tier"):
                    # print(f'{ticker_time_frame} Ignore Trigger macd_tier: , {macd_tier}')
                    return True
            else:
                return False

        def find_symbol(ticker): # Load Ticker Index ETF Risk Level

            if ticker in QUEEN['heartbeat']['main_indexes'].keys():
                if 'buy' in trigbee:
                    if f'{"long"}{trading_model["index_long_X"]}' in QUEEN['heartbeat']['main_indexes'][ticker].keys():
                        etf_long_tier = f'{"long"}{trading_model["index_long_X"]}'
                        ticker = QUEEN['heartbeat']['main_indexes'][ticker][etf_long_tier]
                    else:
                        etf_long_tier = False
                if 'sell' in trigbee:
                    if f'{"inverse"}{trading_model["index_inverse_X"]}' in  QUEEN['heartbeat']['main_indexes'][ticker].keys():
                        etf_inverse_tier = f'{"inverse"}{trading_model["index_inverse_X"]}'
                        ticker = QUEEN['heartbeat']['main_indexes'][ticker][etf_inverse_tier]
                    else:
                        etf_inverse_tier = False
            
            return ticker

        def trig_in_action_waterfall(kings_blessing, order_vars, trig_action_num, time_delta, borrowed_funds=False, info="returns kings_blessing, order_vars"):
            if borrowed_funds:
                kings_blessing = True
                order_vars = order_vars__queen_order_items(trading_model=trading_model_theme, king_order_rules=king_order_rules, order_side='buy', wave_amo=wave_amo, maker_middle=maker_middle, origin_wave=current_wave, power_up_rangers=power_up_amo, ticker_time_frame_origin=ticker_time_frame, double_down_trade=True, wave_at_creation=current_macd_cross__wave)
            if trig_action_num > 0:
                if time_delta > timedelta(minutes=king_order_rules['doubledown_timeduration']):
                    print("Trig In Action Double Down Trade")
                    kings_blessing = True
                    order_vars = order_vars__queen_order_items(trading_model=trading_model_theme, king_order_rules=king_order_rules, order_side='buy', wave_amo=wave_amo, maker_middle=maker_middle, origin_wave=current_wave, power_up_rangers=power_up_amo, ticker_time_frame_origin=ticker_time_frame, double_down_trade=True, wave_at_creation=current_macd_cross__wave)
                else:
                    kings_blessing = False
                    order_vars = None
            
            return kings_blessing, order_vars
        
        # def last_time_tr
        try:
            if crypto: # crypto currently not supported
                return {'kings_blessing': False}
            
            if 'chess_board__revrec' not in QUEEN_KING.keys():
                print("QUEEN Not Enabled ChessBoard")
                logging.error((" queen not auth "))
                return {'kings_blessing': False}
            
            # vars
            ticker, tframe, tperiod = ticker_time_frame.split("_")
            star_time = f'{tframe}{"_"}{tperiod}'
            ticker_priceinfo = return_snap_priceinfo(api=api, ticker=ticker, crypto=crypto, exclude_conditions=exclude_conditions)
            trigbee_wave_direction = ['waveup' if 'buy' in trigbee else 'wavedown'][0]

            # RevRec # Allocation Star allowed df_qcp, df_ticker, df_stars
            # qcp_total_budget = revrec['df_qcp'].loc[qcp].get("qcp_total_budget")
            ticker_total_budget = revrec['df_ticker'].loc[ticker].get("ticker_total_budget")
            ticker_borrow_budget = revrec['df_ticker'].loc[ticker].get("ticker_borrow_budget")
            star_total_budget = revrec['df_stars'].loc[ticker_time_frame].get("star_total_budget")
            star_total_borrow = revrec['df_stars'].loc[ticker_time_frame].get("star_borrow_budget")
            star_total_budget_remaining = revrec['df_stars'].loc[ticker_time_frame].get("remaining_budget")
            star_total_borrow_remaining = revrec['df_stars'].loc[ticker_time_frame].get("remaining_budget_borrow")

            # Total In Running, Remaining
            # ticker_remaining_budget = return_ttf_remaining_budget(QUEEN=QUEEN, total_budget=ticker_total_budget, active_queen_order_states=active_queen_order_states, ticker=ticker, star=False, ticker_time_frame=False,)
            # star_remaining_budget = return_ttf_remaining_budget(QUEEN=QUEEN, total_budget=star_total_budget, active_queen_order_states=active_queen_order_states, ticker=False, star=False, ticker_time_frame=ticker_time_frame,)
            
            kings_blessing = False

            # how many trades have we completed today? whats our total profit loss with wave trades
            # should you override your original order rules?

            if star_total_budget_remaining == 0:
                # print(f'{ticker_time_frame} all budget used up')
                if ticker_time_frame not in QUEEN['queens_messages'].keys():
                    QUEEN['queens_messages'][ticker_time_frame] = {'remaining_budget': f'{ticker_time_frame} all budget used up'}
                else:
                    QUEEN['queens_messages'][ticker_time_frame].update({'remaining_budget': f'{ticker_time_frame} all budget used up'})
                return {'kings_blessing': False}

            if star_total_budget_remaining == 0 and star_total_borrow_remaining == 0:
                return {'kings_blessing': False}
            
            # trade scenarios / power ups / 
            trig_action_num = len(trig_action) # get trading model amount allowed?
            now_time = datetime.now(est)
            if trig_action_num != 0:
                trig_action.iloc[-1]['datetime']
                time_delta = now_time - trig_action.iloc[-1]['datetime']
            else:
                time_delta = now_time - datetime.now(est)

            # remaining_budget_wave = ticker_remaining_budget * .89
            remaining_budget_wave = star_total_budget_remaining
            remaining_budget_wave_Short = star_total_borrow_remaining
            # how much are you allowed of the total budget
            
            # Total buying power allowed  
            wave_amo = remaining_budget_wave
            wave_amo = wave_amo * .89  # Never Allow Full Budget

            borrowed_funds = True if star_total_budget_remaining == 0 else False

            power_up_amo = 0
            power_rangers_universe = ['mac_ranger', 'hist_ranger']
            power_up_amo = {ranger: 0 for ranger in power_rangers_universe}

            # Theme
            theme = QUEEN_KING['king_controls_queen']['theme'] # what is the theme?
            trading_model_theme = trading_model.get('theme')
            trading_model_star = trading_model['stars_kings_order_rules'].get(f'{tframe}_{tperiod}')

            """Stars Forever Be in Heaven"""
            # Story View, Wave Analysis
            story_view_ = story_view(STORY_bee=STORY_bee, ticker=ticker)
            stars_df = story_view_['df']
            stars_df = stars_df.set_index("star")
            macd_tier = stars_df.loc[ticker_time_frame].get('current_macd_tier')
            current_macd_cross__wave = star_ticker_WaveAnalysis(STORY_bee=STORY_bee, ticker_time_frame=ticker_time_frame)['current_wave']
            current_wave = star_ticker_WaveAnalysis(STORY_bee=STORY_bee, ticker_time_frame=ticker_time_frame)['current_active_waves'][trigbee]
            current_wave_blocktime = current_wave['wave_blocktime']
            # current_wave_amo = pollen_theme_dict[theme][star_time][trigbee_wave_direction][current_wave_blocktime]
            
            # Trading Model Vars
            # Global switch to user power rangers at ticker or portfolio level 
            tmodel_power_rangers = trading_model['stars_kings_order_rules'][star_time].get('power_rangers')
            if trading_model_theme == 'story__AI':
                print('story ai update KORs with lastest from story_view()')
            king_order_rules = trading_model['stars_kings_order_rules'][star_time]['trigbees'][trigbee][current_wave_blocktime]
            maker_middle = ticker_priceinfo['maker_middle'] if str(trading_model_star.get('trade_using_limits')) == 'true' else False

            # power_up_amo = its_morphin_time(QUEEN_KING=QUEEN_KING, QUEEN=QUEEN, trigbee=trigbee, theme=theme, tmodel_power_rangers=tmodel_power_rangers, ticker=ticker, stars_df=stars_df)
            # print("POWERUP !!!!! ", power_up_amo)
            # wave_amo = theme_amo + power_up_amo['mac_ranger'] + power_up_amo['hist_ranger']

            if kings_blessing_checks():
                return {'kings_blessing': False}

            ticker = find_symbol(ticker)

            # def waterfall_knight_buy_chain(trigbees, trading_model):
            #     return False
            
            if trigbee == 'buy_cross-0':
                if crypto:
                    kings_blessing = True
                    order_vars = order_vars__queen_order_items(trading_model=trading_model_theme, king_order_rules=king_order_rules, order_side='buy', wave_amo=wave_amo, maker_middle=maker_middle, origin_wave=current_wave, power_up_rangers=power_up_amo, ticker_time_frame_origin=ticker_time_frame, wave_at_creation=current_macd_cross__wave)
                else:
                    kings_blessing = True
                    order_vars = order_vars__queen_order_items(trading_model=trading_model_theme, king_order_rules=king_order_rules, order_side='buy', wave_amo=wave_amo, maker_middle=maker_middle, origin_wave=current_wave, power_up_rangers=power_up_amo, ticker_time_frame_origin=ticker_time_frame, wave_at_creation=current_macd_cross__wave)

                kings_blessing, order_vars = trig_in_action_waterfall(kings_blessing, order_vars, trig_action_num, time_delta, borrowed_funds) # if time_delta.seconds > king_order_rules['doubledown_timeduration']
            
            elif trigbee == 'sell_cross-0':
                ## create process of shorting when regular tickers
                if crypto:
                    return {'kings_blessing': False}
                else:
                    kings_blessing = True
                    order_vars = order_vars__queen_order_items(trading_model=trading_model, king_order_rules=king_order_rules, order_side='buy', wave_amo=wave_amo, maker_middle=maker_middle, origin_wave=current_wave, power_up_rangers=power_up_amo, ticker_time_frame_origin=ticker_time_frame, wave_at_creation=current_macd_cross__wave)

                kings_blessing, order_vars = trig_in_action_waterfall(kings_blessing, order_vars, trig_action_num, time_delta, borrowed_funds) # if time_delta.seconds > king_order_rules['doubledown_timeduration']

            elif trigbee == 'ready_buy_cross':
                if crypto:
                    kings_blessing = True
                    order_vars = order_vars__queen_order_items(trading_model=trading_model_theme,king_order_rules=king_order_rules, order_side='buy', wave_amo=wave_amo, maker_middle=maker_middle, origin_wave=current_wave, power_up_rangers=power_up_amo, ticker_time_frame_origin=ticker_time_frame, wave_at_creation=current_macd_cross__wave)
                else:
                    kings_blessing = True
                    order_vars = order_vars__queen_order_items(trading_model=trading_model_theme, king_order_rules=king_order_rules, order_side='buy', wave_amo=wave_amo, maker_middle=maker_middle, origin_wave=current_wave, power_up_rangers=power_up_amo, ticker_time_frame_origin=ticker_time_frame, wave_at_creation=current_macd_cross__wave)

                kings_blessing, order_vars = trig_in_action_waterfall(kings_blessing, order_vars, trig_action_num, time_delta, borrowed_funds) # if time_delta.seconds > king_order_rules['doubledown_timeduration']

            else:
                print("Error New Trig not in Queens Mind: ", trigbee )
                return {'kings_blessing': False}


            if kings_blessing:
                if not isinstance(order_vars.get('wave_amo'), float) or order_vars.get('wave_amo') <=0:
                    send_email(subject="error check go check kings blessing")
                    ipdb.set_trace()
                    return {'kings_blessing': False}

            if kings_blessing:
                return {'kings_blessing': kings_blessing, 'ticker': ticker, 'order_vars': order_vars}
            else:
                return {'kings_blessing': False}
            
        except Exception as e:
            print(e, print_line_of_error(), ticker_time_frame)
            print("logme")


    def command_conscience(api, QUEEN, STORY_bee, QUEEN_KING):

        try:


            def short():
                return True

            s_time_fullloop = datetime.now(est)

            active_tickers = QUEEN['heartbeat']['active_tickers']

            portfolio = return_alpc_portolio(api)['portfolio']

            all_orders = QUEEN['queen_orders']
            active_orders = all_orders[all_orders['queen_order_state'].isin(active_queen_order_states)].copy()
            app_wave_trig_req = process_app_requests(QUEEN=QUEEN, QUEEN_KING=QUEEN_KING, request_name='wave_triggers', archive_bucket='app_wave_requests')

            mkhrs = return_market_hours(trading_days=trading_days)
            # cycle through stories  # The Golden Ticket
            s_time = datetime.now(est)
            for ticker in active_tickers:
                # Ensure Trading Model
                if ticker not in QUEEN_KING['king_controls_queen']['symbols_stars_TradingModel'].keys():
                    QUEEN['queens_messages'].update({'model_does_not_exist': f'{ticker}'})
                    continue 
                crypto = True if ticker in crypto_currency_symbols else False
                
                # Check Mrk Hours
                if mkhrs != 'open':
                    continue

                """ the hunt """
                s_time = datetime.now(est)
                req = return_STORYbee_trigbees(QUEEN=QUEEN, STORY_bee=STORY_bee, tickers_filter=[ticker])
                active_trigs = req.get('active_trigs')   
                all_current_trigs = req.get('all_current_trigs')
                if app_wave_trig_req.get('app_flag'):
                    active_trigs = add_app_wave_trigger(active_trigs=active_trigs, ticker=ticker, app_wave_trig_req=app_wave_trig_req)      
                charlie_bee['queen_cyle_times']['thehunt__cc'] = (datetime.now(est) - s_time).total_seconds()
                # Return Scenario based trades
                
                # def global level allow trade to be considered
                # 1 stop Level of tier trading only allowed x number of trades a day until you receive day trade margin
                acct_info = refresh_account_info(api=api)['info_converted']
                revrec = refresh_chess_board__revrec(acct_info, QUEEN, QUEEN_KING, active_queen_order_states=RUNNING_Orders, chess_board__revrec={}, revrec__ticker={}, revrec__stars={}) ## Setup Board

                try:
                    s_time = datetime.now(est)
                    for ticker_time_frame, avail_trigs in active_trigs.items():
                        if len(avail_trigs) == 0:
                            continue
                        
                        ticker, tframe, frame = ticker_time_frame.split("_")
                        frame_block = f'{tframe}{"_"}{frame}' # frame_block = "1Minute_1Day"

                        if ticker not in revrec.get('df_ticker').index.tolist():
                            continue
                        if revrec.get('df_ticker').loc[ticker, 'ticker_buying_power'] == 0:
                            continue

                        trading_model = QUEEN_KING['king_controls_queen']['symbols_stars_TradingModel'][ticker]
                        
                        # check global ticker level
                        if str(trading_model['status']) not in ['active', 'true']:
                            # print(str(trading_model['status']), "model not active", ticker_time_frame, " availtrigs: ", avail_trigs)
                            QUEEN['queens_messages'].update({'model_not_active': f'{ticker_time_frame}'})
                            continue
                        if str(trading_model['power_rangers'].get(frame_block)).lower() not in ['active', 'true']:
                            # global 1Minute_1Day is not active
                            continue
                        # cycle through triggers and pass buy first logic for buy
                        # trigs =  all_current_triggers[f'{ticker}{"_1Minute_1Day"}']
                        for trig in avail_trigs:
                            if trig == 'sell_cross-0' and ticker not in QUEEN['heartbeat']['main_indexes'].keys():
                                # print("Wants to Short Stock Scenario")
                                continue
                            if trig not in QUEEN['heartbeat']['available_triggerbees']: # buy_cross-0 <<< OLD >>> this is handled in return_STORYbee_trigbees()
                                continue
                            if trig in trading_model['trigbees'].keys():
                                if str(trading_model['trigbees'][trig]).lower() not in ['active', 'true']:
                                    # print("trig bee model not active", ticker_time_frame, " availtrigs: ", avail_trigs)
                                    QUEEN['queens_messages'].update({'trigbee_not_active': f'{ticker_time_frame}__trig-{trig}'})
                                    continue

                                # check if you already placed order or if a workerbee in transit to place order
                                ticker_trig_action = ticker_trig_In_Action_cc(active_orders=active_orders, trig=trig, ticker=ticker)
                                trig_action = trig_In_Action_cc(active_orders=active_orders, trig=trig, ticker_time_frame=ticker_time_frame)
                                
                                if len(ticker_trig_action) > 0 and trading_model.get('short_position') == True:
                                    print("Only 1 Trigger Allowed in ticker Shorting")
                                    continue

                                if crypto:
                                    # check if ticker_time_frame is in temp, if yes then check last time it was put there, if it has been over X time per timeframe rules then send email to buy
                                    QUEEN['crypto_temp']['trigbees'].update({ticker_time_frame: {'king_resp': king_resp, 'datetime': datetime.now(est)}})

                                """ HAIL TRIGGER, WHAT SAY YOU? ~forgive me but I bring a gift for the king and queen"""
                                s_time = datetime.now(est)
                                king_resp = king_knights_requests(QUEEN=QUEEN, STORY_bee=STORY_bee, revrec=revrec, trigbee=trig, ticker_time_frame=ticker_time_frame, trading_model=trading_model, trig_action=trig_action, crypto=crypto)
                                if king_resp.get('kings_blessing'):
                                    execute_order(QUEEN=QUEEN, king_resp=king_resp, king_eval_order=False, ticker=king_resp['ticker'], ticker_time_frame=ticker_time_frame, trig=trig, portfolio=portfolio, crypto=crypto)

                                charlie_bee['queen_cyle_times']['knights_request__cc'] = (datetime.now(est) - s_time).total_seconds()
                    
                except Exception as e:
                    msg = (ticker_time_frame, e, print_line_of_error())
                    print(msg)
                    QUEEN['queens_messages'].update({'commandconscience__failed': {'ticker_time_frame': f'{ticker_time_frame}', 'error': e, 'line_error': print_line_of_error()}})
                    send_email(subject="Knight Error", body=f'{msg}')
                    ipdb.set_trace()
                    sys.exit()

            
            # # App Buy Order Requests
            # s_time = datetime.now(est)
            # app_resp = process_app_requests(QUEEN=QUEEN, QUEEN_KING=QUEEN_KING, request_name='buy_orders')
            # charlie_bee['queen_cyle_times']['app_req_loop__cc'] = (datetime.now(est) - s_time).total_seconds()
            # if app_resp['app_flag']:
            #     msg = {'process_app_buy_requests()': 'queen processed app request'}
            #     print(msg)
            #     # queen process
            #     logging.info(msg)
            #     QUEEN_KING['queen_processed_orders'].append(app_resp['app_request']['app_requests_id'])
            #     QUEEN['app_requests__bucket'].append(app_resp['app_request']['app_requests_id'])

            #     crypto = [True if app_resp['app_request']['ticker'] in crypto_currency_symbols else False][0]
                
            #     # execute order
            #     bzzz = execute_order(QUEEN=QUEEN, 
            #     trig=app_resp['app_request']['trig'], 
            #     king_resp=app_resp['king_resp'],
            #     king_eval_order=False,
            #     ticker=app_resp['app_request']['ticker'], 
            #     ticker_time_frame=app_resp['ticker_time_frame'],
            #     portfolio=portfolio,
            #     crypto=crypto)


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
                return (order_time_delta.seconds / 60) - duration_rule

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


    def return_closing_orders_df(QUEEN, exit_order_link): # returns linking order
        df = QUEEN['queen_orders']
        origin_closing_orders = df[(df['exit_order_link'] == exit_order_link) & (df['queen_order_state'].isin(CLOSED_queenorders)) & (df['client_order_id'].str.startswith("close__"))].copy()
        if len(origin_closing_orders) > 0:
            return origin_closing_orders
        else:
            return ''


    def update_latest_queen_order_status(order_status, queen_order_idx): # updates qty and cost basis from Alpaca
        for order_key, order_value in order_status.items():
            QUEEN['queen_orders'].at[queen_order_idx, order_key] = order_value

        if order_status['filled_qty'] is not None:
            QUEEN['queen_orders'].at[queen_order_idx, 'filled_qty'] = float(order_status['filled_qty'])
        if order_status['filled_avg_price'] is not None:
            QUEEN['queen_orders'].at[queen_order_idx, 'filled_avg_price'] = float(order_status['filled_avg_price'])
            QUEEN['queen_orders'].at[queen_order_idx, 'cost_basis'] = float(order_status['filled_qty']) * float(order_status['filled_avg_price'])

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
        origin_order_cost_basis__qorder = float(queen_order['filled_qty']) * float(origin_order['filled_avg_price'])
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

            profit_loss = queen_order_cost_basis__to_origin_order
            closing_filled = sum(origin_closing_orders_df['filled_qty'])

            # validate qty
            if sum(origin_closing_orders_df['filled_qty']) > float(queen_order['qty']):
                print("There must be a limit order thats needs to be adjusted/cancelled")
                pass

            QUEEN['queen_orders'].at[origin_order_idx, 'profit_loss'] = profit_loss
                    
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


    def return_snap_priceinfo(api, ticker, crypto, exclude_conditions):
        if crypto:
            snap = api.get_crypto_snapshot(ticker, exchange=coin_exchange)
        else:
            snap = api.get_snapshot(ticker)
            conditions = snap.latest_quote.conditions
            c=0
            while True:
                # print(conditions)
                valid = [j for j in conditions if j in exclude_conditions]
                if len(valid) == 0 or c > 10:
                    break
                else:
                    snap = api.get_snapshot(ticker) # return_last_quote from snapshot
                    c+=1 

        # current_price = STORY_bee[f'{ticker}{"_1Minute_1Day"}']['last_close_price']
        current_price = snap.latest_trade.price
        current_ask = snap.latest_quote.ask_price
        current_bid = snap.latest_quote.bid_price

        # best limit price
        best_limit_price = get_best_limit_price(ask=current_ask, bid=current_bid)
        maker_middle = best_limit_price['maker_middle']
        ask_bid_variance = current_bid / current_ask
        
        priceinfo = {'snapshot': snap, 'current_price': current_price, 'current_bid': current_bid, 'current_ask': current_ask, 'maker_middle': maker_middle, 'ask_bid_variance': ask_bid_variance}
        
        return priceinfo


    def return_snap_priceinfo__pollenData(STORY_bee, ticker):
        # read check if ticker is active...if it is return into from db ELSE if user data Pa
        # ttf = f'{ticker}{"_1Minute_1Day"}'
        # if ttf not in STORY_bee.keys():
        #     snap = api.get_snapshot(ticker)
        #     conditions = snap.latest_quote.conditions
        #     c=0
        #     while True:
        #         # print(conditions)
        #         valid = [j for j in conditions if j in exclude_conditions]
        #         if len(valid) == 0 or c > 5:
        #             break
        #         else:
        #             snap = api.get_snapshot(ticker) # return_last_quote from snapshot
        #             c+=1 
            
        #     current_price = snap.latest_trade.price
        #     current_ask = snap.latest_quote.ask_price
        #     current_bid = snap.latest_quote.bid_price
        
        # else:
        #     current_price = STORY_bee[ttf]['story']['last_close_price']
        #     current_ask = current_price + (current_price * .01)
        #     current_bid = current_price - (current_price * .01)

        snap = api.get_snapshot(ticker)
        conditions = snap.latest_quote.conditions
        c=0
        while True:
            # print(conditions)
            valid = [j for j in conditions if j in exclude_conditions]
            if len(valid) == 0 or c > 5:
                break
            else:
                snap = api.get_snapshot(ticker) # return_last_quote from snapshot
                c+=1 
        
        current_price = snap.latest_trade.price
        current_ask = snap.latest_quote.ask_price
        current_bid = snap.latest_quote.bid_price


        # best limit price
        best_limit_price = get_best_limit_price(ask=current_ask, bid=current_bid)
        maker_middle = best_limit_price['maker_middle']
        ask_bid_variance = current_bid / current_ask
        
        priceinfo = {'current_price': current_price, 'current_bid': current_bid, 'current_ask': current_ask, 'maker_middle': maker_middle, 'ask_bid_variance': ask_bid_variance}
        
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
            
            # priceinfo = {'price': current_price, 'bid': current_bid, 'ask': current_ask}
            order_price = float(queen_order['filled_avg_price'])
            if order_price > 0:
                current_profit_loss = (current_price - order_price) / order_price
                QUEEN['queen_orders'].at[queen_order_idx, 'honey'] = current_profit_loss
                QUEEN['queen_orders'].at[queen_order_idx, '$honey'] = (current_price * float(queen_order['filled_qty'])) - ( float(queen_order['filled_avg_price']) * float(queen_order['filled_qty']) )
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
                QUEEN['queen_orders'].at[queen_order_idx, '$honey'] = 0
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
                    d_return[trigbee] = {}
                    for num in number_ranges:
                        d_return[trigbee][num] = {}
                        if gauge_len > num:
                            last_n = [gauge[(gauge_len - n) *-1] for n in range(1,num)]
                            avg = sum([1 for i in last_n if i == trigbee]) / len(last_n)
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
        QUEEN['queen_orders'].at[queen_order_idx, '$honey'] = profit_loss_value
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


    def subconscious_update(root_name, dict_to_add, list_len=89):
        # store message
        if root_name not in QUEEN['subconscious'].keys():
            if dict_to_add not in QUEEN['subconscious'][root_name]:
                QUEEN['subconscious'][root_name].append(dict_to_add)
        else:
            if dict_to_add not in QUEEN['subconscious'][root_name]:
                QUEEN['subconscious'][root_name].append(dict_to_add)

        return True

    def conscience_update(root_name, dict_to_add, list_len=89):
        # store message
        try:
            if root_name not in QUEEN['conscience'].keys():
                QUEEN['conscience'][root_name] = deque([], list_len)
            else:
                if dict_to_add not in QUEEN['conscience'][root_name]:
                    QUEEN['conscience'][root_name].append(dict_to_add)

            return True
        except Exception as e:
            print(e, print_line_of_error())

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


    def king_bishops_QueenOrder(STORY_bee, run_order, priceinfo):
        """if you made it here you are running somewhere, I hope you find your way, I'll always bee here to help"""
        try:
            # # """ all scenarios if run_order should be closed out """
            
            # if run_order['client_order_id'] == 'run__TSLA-buy_cross-0-127-22-10-31 17.14':
            #     ipdb.

            # Stars in Heaven
            # stars_df = story_view(STORY_bee=STORY_bee, ticker=ticker)['df'] ## story view is slow needs improvement before implementation

            s_time = datetime.now(est)
            # gather run_order Vars
            trigname = run_order['trigname']
            order_rules = run_order.get('order_rules')
            client_order_id = run_order['client_order_id']
            take_profit = order_rules['take_profit']
            sellout = order_rules['sellout']
            sell_qty = float(run_order['filled_qty'])
            qty_available = float(run_order['qty_available'])
            ticker_time_frame = run_order['ticker_time_frame']
            ticker_time_frame_origin = run_order['ticker_time_frame_origin']
            entered_trade_time = run_order['datetime'].astimezone(est)
            origin_wave = run_order['origin_wave']
            # trading_model = run_order['trading_model'] # in Future Turn this to TradingModel_Id
            time_in_trade = datetime.now(est) - entered_trade_time
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

            # verison control until better way found
            if 'max_profit_waveDeviation_timeduration' in order_rules.keys():
                max_profit_waveDeviation_timeduration = order_rules['max_profit_waveDeviation_timeduration']
            else:
                max_profit_waveDeviation_timeduration = 500 # Minutes

            # Only if there are available shares

            sell_order = False # #### >>> convince me to sell  $$

            macd_gauge = macdGauge_metric(STORY_bee=STORY_bee, ticker_time_frame=ticker_time_frame, trigbees=['buy_cross-0', 'sell_cross-0'], number_ranges=[5, 11, 16, 24, 33])
            honey_gauge = honeyGauge_metric(run_order)
            # print(macd_gauge)
            # conscience_update(root_name='macd_gauge', dict_to_add={macd_gauge}, list_len=1)
            # conscience_update(root_name='honey_gauge', dict_to_add={honey_gauge}, list_len=1)

            charlie_bee['queen_cyle_times']['bishop_block1_queenorder__om'] = (datetime.now(est) - s_time).total_seconds()
            s_time = datetime.now(est)

            """ Bishop Knight Waves """
            df_waves_story = STORY_bee[ticker_time_frame]['waves']['story']
            current_story_wave = df_waves_story.iloc[-1].to_dict()
            
            trigbees_wave_id_list = []
            trigbees = ['buy_cross-0', 'sell_cross-0', 'read_buy_cross']
            for trigbee in trigbees:
                if trigbee in STORY_bee[ticker_time_frame]['waves'].keys():
                    for wave, v, in STORY_bee[ticker_time_frame]['waves'][trigbee].items():
                        if wave == '0':
                            continue
                        else:
                            trigbees_wave_id_list.append(v['wave_id'])
            
            last_buy_wave = STORY_bee[ticker_time_frame]['waves']['buy_cross-0']['1']
            last_sell_wave = STORY_bee[ticker_time_frame]['waves']['sell_cross-0']['1']
            current_wave = last_buy_wave if last_buy_wave["wave_start_time"] > last_sell_wave["wave_start_time"] else last_sell_wave

            # handle not in Story default to SPY
            if ticker_time_frame_origin not in STORY_bee.keys():
                ticker_time_frame_origin = "SPY_1Minute_1Day"
            ticker, tframe, tperiod = ticker_time_frame_origin.split("_")
            star = f'{tframe}{"_"}{tperiod}'

            # POLLEN STORY
            ttframe_story = STORY_bee[ticker_time_frame_origin]['story']
            current_macd = ttframe_story['macd_state']
            current_macd_time = int(current_macd.split("-")[-1])
            
            # current_macd_cross__wave = star_ticker_WaveAnalysis(STORY_bee=STORY_bee, ticker_time_frame=ticker_time_frame)['current_wave'].to_dict()
            # current_wave = star_ticker_WaveAnalysis(STORY_bee=STORY_bee, ticker_time_frame=ticker_time_frame)['current_active_waves'][trigname].to_dict()

            """ Trading Models Kings Order Rules """ 
            # Trading Model Sell Vars
            # use maxprofit deviation here and add to order
            current_wave_maxprofit_stat = current_wave['length'] - current_wave['time_to_max_profit']
            run_order_wave_changed = True if run_order['origin_wave']['wave_id'] in trigbees_wave_id_list else False

            # trade is past excepted duration time 
            past_trade_duration = order_past_duration(queen_order=run_order)

            # Wave distance to Max Profit
            ttframe_take_max_profit = order_rules['max_profit_waveDeviation']
            wave_past_max_profit = float(ttframe_take_max_profit) >= current_wave_maxprofit_stat # max profits exceed setting

            # Gather main sell reason groups
            sell_trigbee_trigger = True if str(order_rules['sell_trigbee_trigger']).lower() == 'true' else False
            stagger_profits = True if str(order_rules['stagger_profits']).lower() == 'true' else False
            scalp_profits = True if str(order_rules['scalp_profits']).lower() == 'true' else False
            macd_tier = current_macd_time
            
            charlie_bee['queen_cyle_times']['bishop_block2_queenorder__om'] = (datetime.now(est) - s_time).total_seconds()
            s_time = datetime.now(est)

            """ WaterFall sellout chain """

            now_time = s_time
            def waterfall_sellout_chain(client_order_id, macd_tier, trading_model, sell_order, run_order, order_type, limit_price, sell_trigbee_trigger, stagger_profits, scalp_profits, run_order_wave_changed, sell_qty, QUEEN=QUEEN):
                try:
                    # client_order_id = run_order.get('client_order_id')
                    sell_reasons = []
                    
                    if scalp_profits:
                        scalp_profits = order_rules['scalp_profits_timeduration']
                        if time_in_trade.total_seconds() > float(scalp_profits):
                            if honey_gauge['last_30_avg']:
                                # store message and compare trading model against distance from breakeven
                                if honey_gauge['last_30_avg'] < 0:
                                    profit_seek = qorder_honey__distance_from_breakeven_tiers(run_order=run_order)
                                    profit_stars = ['high_above_breakeven', 'low_above_breakeven', 'breakeven', 'below_breakeven', 'immediate']
                                    # if profit_seek = 'high_above_breakeven'
                                    # set limit price based on profit_seek
                                    print("selling out due Scalp Exit last_30_avg ")
                                    sell_reason = 'scalp_exit__last_30_avg'
                                    sell_reasons.append(sell_reason)
                                    sell_order = True
                                    order_side = 'sell'
                                    profit_seek_value = priceinfo['maker_middle'] + abs(float(honey) * float(run_order['filled_avg_price']))
                                    profit_seek_value = profit_seek_value + (priceinfo['maker_middle'] * .00033)
                                    if crypto:
                                        limit_price = round(profit_seek_value, 1) # current price + (current price * profit seek)
                                    else:
                                        limit_price = round(profit_seek_value, 2) # current price + (current price * profit seek)


                                    # # store message
                                    # if 'queen_orders' in QUEEN['subconscious'].keys():
                                    #     QUEEN['subconscious']['queen_orders'].update({run_order['client_order_id']: {'client_order_id': run_order['client_order_id'],  'waterfall_sellout_msg': f'{"last_30_avg"}{" find exit price"}' }})
                                    # else:
                                    #     QUEEN['subconscious']['queen_orders'] = {run_order['client_order_id']: {'client_order_id': run_order['client_order_id'],  'waterfall_sellout_msg': f'{"last_30_avg"}{" find exit price"}' }}
                                    
                                    return {'sell_order': True, 'sell_reason': sell_reason, 'order_side': order_side, 'order_type': order_type, 'sell_qty': sell_qty, 'limit_price': limit_price}    

                    
                    # Water Fall
                    if order_rules['take_profit'] <= honey:
                        print("selling out due PROFIT ACHIVED")
                        sell_reason = 'order_rules__take_profit'
                        sell_reasons.append(sell_reason)
                        sell_order = True
                        
                        order_side = 'sell'
                        limit_price = priceinfo['maker_middle'] if order_type == 'limit' else False

                    elif honey <= order_rules['sellout']:
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

                    elif time_in_trade > timedelta(minutes=max_profit_waveDeviation_timeduration) and wave_past_max_profit:
                        print("Selling Out from max_profit_waveDeviation: deviation>> ", current_wave_maxprofit_stat)
                        sell_reason = 'order_rules__max_profit_waveDeviation'
                        sell_reasons.append(sell_reason)
                        sell_order = True

                        order_side = 'sell'
                        limit_price = priceinfo['maker_middle'] if order_type == 'limit' else False
                    
                    # how to consider new triggers?
                    if sell_trigbee_trigger:
                        if run_order['trigname'] == "buy_cross-0" and "sell" in current_macd and time_in_trade.seconds > 500: 
                            # if 'use_wave_guage' in order_rules.keys():

                            if macd_gauge['metrics']['sell_cross-0'][5]['avg'] > .5:
                                print("SELL ORDER change from buy to sell", current_macd, current_macd_time)
                                sell_reason = 'order_rules__macd_cross_buytosell'
                                sell_reasons.append(sell_reason)
                                sell_order = True
                                order_side = 'sell'
                                limit_price = priceinfo['maker_middle'] if order_type == 'limit' else False

                        elif run_order['trigname'] == "sell_cross-0" and "buy" in current_macd and time_in_trade.seconds > 500:
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
                                # upddate run order
                                run_order['order_rules']['revisit_trade_datetime'] = now_time
                            # are we in profit?
                            # how old is our trade compared to our goal?
                            # what does the family say?
                            # are you closing out today?
                    
                    #     close_order_today = order_rules.get('close_order_today')
                    #     time_to_bell_close = (now_time.replace(hour=16, minute=00, second=0) - now_time).total_seconds()
                    #     last_call_time = now_time.replace(hour=15, minute=58, second=0)
                    #     last_10min_time = now_time.replace(hour=15, minute=50, second=0)
                    #     last_30min_time = now_time.replace(hour=15, minute=30, second=0)
                    #     last_30hr_time = now_time.replace(hour=15, minute=0, second=0)

                    #     if order_rules.get('KOR_version') > 0:
                    #         if close_order_today and order_rules.get('close_order_today_allowed_timeduration') >= time_to_bell_close and time_in_trade > timedelta(seconds=33):
                                
                    #             print("Selling Out, Trade Not Allowed to go past day")
                    #             sell_reason = 'close_order_today'
                    #             sell_order = True

                    #             order_side = 'sell'
                    #             limit_price = priceinfo['maker_middle'] if order_type == 'limit' else False

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
                        print("Bishop SELL ORDER:", ticker_time_frame, sell_reasons, current_macd, current_macd_time)
                        # conscience_update(root_name='bishop_sell_order', dict_to_add={'ticker_time_frame': ticker_time_frame, 'sell_reasons': sell_reasons}, list_len=33)
                        return {'sell_order': True, 
                        'sell_reason': sell_reason, 
                        'order_side': order_side, 
                        'order_type': order_type, 
                        'sell_qty': sell_qty, 
                        'limit_price': limit_price, 
                        'app_request': app_request,}    
                    else:
                        return {'sell_order': False}
                
                except Exception as e:
                    print('waterfall error', e, " er line>>", print_line_of_error())

            king_bishop = waterfall_sellout_chain(client_order_id, macd_tier, trading_model, sell_order, run_order, order_type, limit_price, sell_trigbee_trigger, stagger_profits, scalp_profits, run_order_wave_changed, sell_qty)
        
            charlie_bee['queen_cyle_times']['bishop_block3_queenorder__om'] = (datetime.now(est) - s_time).total_seconds()

            # elif the 3 wisemen pointing to sell or re-chunk profits

            # check if position is neg, if so, switch side to sell and sell_qty to buy  # if portfolio[run_order['ticker']]['side'] == 'short':

            if king_bishop['sell_order']:
                # conscience_update(root_name='bishop_sell_order', dict_to_add={king_bishop})
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
                time_intrade=time_in_trade)
                return {'bee_sell': True, 'order_vars': order_vars, 'app_request': king_bishop['app_request'], 'bishop_keys':bishop_keys}
            else:
                return {'bee_sell': False, 'run_order': run_order}
        
        except Exception as e:
            print(e, print_line_of_error())
            log_error_dict = logging_log_message(log_type='error', msg=f'{client_order_id}{": unable to process kings read on queen order"}', error=str(e), origin_func='king Evaluate QueenOrder')
            logging.error(log_error_dict)


    def stop_queen_order_from_kingbishop(run_order):
        if run_order == False:
            return True
        # Stop Queen Order from going to the Kings Court
        if str(run_order['order_trig_sell_stop']).lower() == 'true': ### consider remaining qty
            return True
        
        if float(run_order['qty_available']) <= 0:
            return True
        else:
            return False


    def queen_orders_main(QUEEN, ORDERS, STORY_bee, portfolio, QUEEN_KING):
        ### TO DO ###
        try:
            s_loop = datetime.now(est)

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
                                QUEEN['queen_orders'].at[queen_order_idx, 'queen_order_state'] = 'running_close'

                        # Handle Filled Orders #
                        elif alp_order_status in filled:
                            # route by order type buy sell
                            if order_status['side'] == 'buy':
                                if QUEEN['queen_orders'].at[queen_order_idx, 'queen_order_state'] in CLOSED_queenorders:
                                    print("but why?")
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
                                    update_origin_order_qty_available(QUEEN=QUEEN, run_order_idx=queen_order_idx, RUNNING_CLOSE_Orders=RUNNING_CLOSE_Orders, RUNNING_Orders=RUNNING_Orders)
                                    update_queen_order_profits(ticker=queen_order['ticker'], queen_order=queen_order, queen_order_idx=queen_order_idx, priceinfo=priceinfo)

                            elif order_status['side'] == 'sell':

                                # closing order, update origin order profits attempt to close out order
                                origin_order = return_origin_order(df_queenorders=QUEEN['queen_orders'], exit_order_link=queen_order['exit_order_link'])
                                origin_order_idx = origin_order.get('origin_idx')
                                origin_order = origin_order.get('origin_order')
                                # confirm profits
                                profit_loss_value = update_runCLOSE__queen_order_honey(queen_order=queen_order, origin_order=origin_order, queen_order_idx=queen_order_idx)['profit_loss_value']
                                QUEEN['queen_orders'].at[queen_order_idx, 'queen_order_state'] = 'completed'

                                #### CHECK to see if Origin ORDER has Completed LifeCycle ###
                                res = update_origin_orders_profits(queen_order=queen_order, origin_order=origin_order, origin_order_idx=origin_order_idx)
                                closing_filled = res['closing_filled']
                                profit_loss = res['profit_loss']
                                print('closing filled: ', profit_loss_value, 'profit_loss: ', profit_loss)
                                
                                update_origin_order_qty_available(QUEEN=QUEEN, run_order_idx=origin_order_idx, RUNNING_CLOSE_Orders=RUNNING_CLOSE_Orders, RUNNING_Orders=RUNNING_Orders)

                                # Check to complete Queen Order
                                check_origin_order_status(QUEEN=QUEEN, origin_order=origin_order, origin_idx=origin_order_idx, closing_filled=closing_filled)

                                
                        elif alp_order_status in partially_filled:            
                            if order_status['side'] == 'buy':
                                QUEEN['queen_orders'].at[queen_order_idx, 'queen_order_state'] = "running_open"
                                
                                update_queen_order_profits(ticker=ticker, queen_order=queen_order, queen_order_idx=queen_order_idx, priceinfo=priceinfo)
                                
                                update_origin_order_qty_available(QUEEN=QUEEN, run_order_idx=queen_order_idx, RUNNING_CLOSE_Orders=RUNNING_CLOSE_Orders, RUNNING_Orders=RUNNING_Orders)

                                return {'resp': "running_open"}
                            elif order_status['side'] == 'sell':
                                # closing order, update origin order profits attempt to close out order
                                origin_order = return_origin_order(df_queenorders=QUEEN['queen_orders'], exit_order_link=queen_order['exit_order_link'])
                                origin_order_idx = origin_order.get('origin_idx')
                                origin_order = origin_order.get('origin_order')
                                
                                # update profits keep in running 
                                update_runCLOSE__queen_order_honey(queen_order=queen_order, origin_order=origin_order, queen_order_idx=queen_order_idx)
                                QUEEN['queen_orders'].at[queen_order_idx, 'queen_order_state'] = 'running_close'
                                
                                update_origin_orders_profits(queen_order=queen_order, origin_order=origin_order, origin_order_idx=origin_order_idx)
                                update_queen_order_profits(ticker=ticker, queen_order=queen_order, queen_order_idx=queen_order_idx, priceinfo=priceinfo)
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

                    ticker = queen_order['ticker']
                    order_id = queen_order['client_order_id']
                    current_updated_at = [queen_order['updated_at'] if 'updated_at' in queen_order.keys() else False][0]
                    # 1 check if order fulfilled
                    # order_status = check_order_status(api=api, client_order_id=order_id, queen_order=queen_order)
                    # 2 update filled qty & $
                    queen_order = update_latest_queen_order_status(order_status=order_status, queen_order_idx=queen_order_idx)
                    # 3 Process Queen Order State
                    queen_order = alpaca_queen_order_state(QUEEN=QUEEN, order_status=order_status, queen_order=queen_order, queen_order_idx=queen_order_idx, priceinfo=priceinfo)
                    # validate RUNNING # check if run_order needs to be arhived?

                    QUEEN['queen_orders'].at[queen_order_idx, 'updated_at'] = order_status['updated_at']
                    
                    if current_updated_at != order_status['updated_at']:
                        print("Queen Order Updated")

                    return QUEEN['queen_orders'].loc[queen_order_idx].to_dict()

                except Exception as e:
                    print(e, print_line_of_error())
                    print("Unable to Route Queen Order")
                    logging.error({'queen order client id': queen_order['client_order_id'], 'msg': 'unable to route queen order', 'error': str(e)})


            def async_api_alpaca__queenOrders(queen_order__s, mkhrs): # re-initiate for i timeframe 

                async def get_queen_order_status(session, client_order_id, queen_order, ticker):
                    async with session:
                        try:
                            order_status = check_order_status(api=api, client_order_id=client_order_id)
                            return {'client_order_id': client_order_id, 'order_status': order_status, 'ticker': ticker}
                        except Exception as e:
                            print(e, client_order_id)
                            logging.error((str(client_order_id), str(e)))
                            return {'client_order_id': client_order_id, 'order_status': 'failed', 'ticker': ticker}
                
                async def main_get_order_status(queen_order__s):
                    async with aiohttp.ClientSession() as session:
                        return_list = []
                        tasks = []
                        for queen_order in queen_order__s:
                            client_order_id = queen_order['client_order_id']
                            ticker = queen_order['ticker']
                            qo_crypto = True if ticker in crypto_currency_symbols else False
                            if mkhrs != 'open':
                                continue # markets are not open for you
                            tasks.append(asyncio.ensure_future(get_queen_order_status(session, client_order_id, queen_order, ticker)))
                        original_pokemon = await asyncio.gather(*tasks)
                        for pokemon in original_pokemon:
                            return_list.append(pokemon)
                        
                        return return_list

                list_of_status = asyncio.run(main_get_order_status(queen_order__s))
                
                return list_of_status

            
            def async_api_alpaca__snapshots_priceinfo(queen_order__s, mkhrs): # re-initiate for i timeframe 

                async def get_changelog(session, client_order_id, queen_order, ticker, crypto):
                    async with session:
                        try:
                            priceinfo = return_snap_priceinfo(api=api, ticker=queen_order['ticker'], crypto=crypto, exclude_conditions=exclude_conditions)
                            return {'client_order_id': client_order_id, 'priceinfo': priceinfo, 'ticker': ticker}
                        except Exception as e:
                            print(e, client_order_id)
                            logging.error((str(client_order_id), str(e)))
                            raise e
                
                async def main(queen_order__s):
                    async with aiohttp.ClientSession() as session:
                        return_list = []
                        tasks = []
                        for queen_order in queen_order__s:
                            client_order_id = queen_order['client_order_id']
                            ticker = queen_order['ticker']
                            crypto = True if ticker in crypto_currency_symbols else False
                            # Continue Only if Market Open
                            if mkhrs != 'open':
                                continue # markets are not open for you
                            tasks.append(asyncio.ensure_future(get_changelog(session, client_order_id, queen_order, ticker, crypto)))
                        original_pokemon = await asyncio.gather(*tasks)
                        for pokemon in original_pokemon:
                            return_list.append(pokemon)
                        
                        return return_list

                list_of_status = asyncio.run(main(queen_order__s))
                return list_of_status
            

            def async_send_queen_orders__to__kingsBishop_court(queen_orders__dict): 

                async def get_kingsBishop(session, run_order, priceinfo):
                    async with session:
                        try:
                            king_eval_order = king_bishops_QueenOrder(STORY_bee=STORY_bee, run_order=run_order, priceinfo=priceinfo)
                            return king_eval_order  # dictionary
                        except Exception as e:
                            print("kb error ", e, run_order['client_order_id'])
                            logging.error((str(run_order['client_order_id']), str(e)))
                            raise e
                
                async def main_kingsBishop(queen_orders__dict):
                    async with aiohttp.ClientSession() as session:
                        return_list = []
                        tasks = []
                        for c_or_id, queen_order_package in queen_orders__dict.items():
                            run_order = queen_order_package['run_order']
                            priceinfo = queen_order_package['priceinfo']
                            tasks.append(asyncio.ensure_future(get_kingsBishop(session, run_order=run_order, priceinfo=priceinfo)))
                        original_pokemon = await asyncio.gather(*tasks)
                        for pokemon in original_pokemon:
                            return_list.append(pokemon)
                        
                        return return_list

                list_of_kingbishop_evals = asyncio.run(main_kingsBishop(queen_orders__dict))
                return list_of_kingbishop_evals

            charlie_bee['queen_cyle_times']['read_funcs__QUEENORDERS_om'] = (datetime.now(est) - s_loop).total_seconds()

            mkhrs = return_market_hours(trading_days=trading_days)

            try: # App Requests
                s_app = datetime.now(est)
                process_app_requests(QUEEN=QUEEN, QUEEN_KING=QUEEN_KING, request_name='update_queen_order')
                charlie_bee['queen_cyle_times']['app_req_om'] = (datetime.now(est) - s_app).total_seconds()
            except Exception as e:
                print('APP: Queen Order Main FAILED PROCESSING ORDER', e, print_line_of_error())
                log_error_dict = logging_log_message(log_type='error', msg='APP: Queen Order Main FAILED PROCESSING ORDER', error=str(e), origin_func='Quen Main Orders')
                logging.error(log_error_dict)

            """ ALL Active SUBMITTED & RUNNING & RUNNING_CLOSE SWITCH TO ASYNC to call all snapshots and orders"""
            s_loop = datetime.now(est)
            df = QUEEN['queen_orders']
            if len(df) == 1:
                # print("First Order")
                QUEEN['queen_orders']['client_order_id'] = QUEEN['queen_orders'].index
                df = QUEEN['queen_orders']

            df['index'] = df.index
            queen_orders__index_dic = dict(zip(df['client_order_id'], df['index']))
            df_active = df[df['queen_order_state'].isin(active_queen_order_states)].copy()
            charlie_bee['queen_cyle_times']['app_filter_QUEENORDERS_om'] = (datetime.now(est) - s_loop).total_seconds()

            s_time = datetime.now(est)
            queen_order__s = [] 
            for idx in df_active['index'].to_list():
                run_order = QUEEN['queen_orders'].loc[idx].to_dict()
                fix_crypto_ticker(QUEEN=QUEEN, ticker=run_order['ticker'], idx=idx)
                queen_order__s.append(QUEEN['queen_orders'].loc[idx].to_dict())
            charlie_bee['queen_cyle_times']['fix_ticker_crypto_QUEENORDERS_om'] = (datetime.now(est) - s_time).total_seconds()

            s_time_qOrders = datetime.now(est)
            if len(queen_order__s) > 0:
                order_status_info = async_api_alpaca__queenOrders(queen_order__s, mkhrs)  ## Returns Status Info IF Market is Open For Ticker
            charlie_bee['queen_cyle_times']['async api alpaca__queenOrders__om'] = (datetime.now(est) - s_time_qOrders).total_seconds()
            
            # s_time = datetime.now(est)
            # priceinfo_info = async_api_alpaca__snapshots_priceinfo(queen_order__s=queen_order__s)
            # charlie_bee['queen_cyle_times']['api_priceinfo_QUEENORDERS_om'] = (datetime.now(est) - s_time).total_seconds()

            s_time = datetime.now(est)
            queen_orders__dict = {}

            for idx in df_active['index'].to_list():
                run_order = QUEEN['queen_orders'].loc[idx].to_dict()
                # Queen Order Local Vars
                runorder_client_order_id = run_order['client_order_id']
                ticker = run_order['ticker_time_frame'].split("_")[0]
                crypto = True if ticker in crypto_currency_symbols else False

                try:

                    if mkhrs != 'open':
                        continue # markets are not open for you

                    priceinfo = return_snap_priceinfo__pollenData(STORY_bee=STORY_bee, ticker=run_order['ticker'])
                    order_status = [ord_stat for ord_stat in order_status_info if ord_stat['client_order_id'] == runorder_client_order_id]
                    # Process Queen Order States
                    if len(order_status) > 0:
                    
                        if order_status[0]['order_status'] == 'failed':
                            print("Order Failed To Turn From Alpaca, Archving Order to Error")
                            QUEEN['queen_orders'].at[idx, 'queen_order_state'] = "failed"
                            continue

                        s_time = datetime.now(est)
                        run_order = route_queen_order(QUEEN=QUEEN, queen_order=run_order, queen_order_idx=idx, order_status=order_status[0]['order_status'], priceinfo=priceinfo) ## send in order_status
                        charlie_bee['queen_cyle_times']['route_queenorder__om'] = (datetime.now(est) - s_time).total_seconds()
                    else: ## this can be removed ### 
                        print(f'order status not returned c_order_id:{runorder_client_order_id}')
                        continue

                    if run_order['queen_order_state'] in ["error", "completed"]:
                        continue
                    
                    if run_order['queen_order_state'] in RUNNING_Orders:
                        # run_order = validate_portfolio_with_RUNNING(ticker=ticker, run_index=idx, run_order=run_order, portfolio=portfolio)
                        if run_order['queen_order_state'] == "error":
                            continue

                        if stop_queen_order_from_kingbishop(run_order):
                            continue

                        ## subconsicous here ###
                        if run_order['ticker_time_frame'] not in STORY_bee.keys():
                            # Handle Order if Ticker Stream Turned off I.E. Not in STORY_bee
                            subconscious_update(root_name='app_info', dict_to_add={'ticker_time_frame': run_order['ticker_time_frame'], 'msg': f'{run_order["symbol"]} open order and ticker not active Handle Order Manually'})                    
                        else:
                            subconscious_mind(root_name='app_info')
                            queen_orders__dict[runorder_client_order_id] = {'run_order': run_order, 'priceinfo': priceinfo}
                                
                except Exception as e:
                    print('Queen Order Main FAILED PROCESSING ORDER', e, print_line_of_error())
                    log_error_dict = logging_log_message(log_type='error', msg='Queen Order Main FAILED PROCESSING ORDER', error=str(e), origin_func='Quen Main Orders')
                    logging.error(log_error_dict)
                    # archive order?
                    QUEEN['queen_orders'].at[idx, 'queen_order_state'] = 'error'

            charlie_bee['queen_cyle_times']['loop_queen_orders__om'] = (datetime.now(est) - s_time_qOrders).total_seconds()

            if len(queen_orders__dict) > 0 :
                s_time_qOrders = datetime.now(est)
                king_bishop_queen_order__EvalOrder = async_send_queen_orders__to__kingsBishop_court(queen_orders__dict=queen_orders__dict)
                charlie_bee['queen_cyle_times']['async_kingsBishop__queenOrders__om'] = (datetime.now(est) - s_time_qOrders).total_seconds()

                for king_eval_order in king_bishop_queen_order__EvalOrder:
                    if king_eval_order['bee_sell']:
                        execute_order(QUEEN=QUEEN, 
                        king_resp=False, 
                        king_eval_order=king_eval_order, 
                        ticker=king_eval_order['bishop_keys']['ticker'], 
                        ticker_time_frame=king_eval_order['bishop_keys']['ticker_time_frame'],
                        trig=king_eval_order['bishop_keys']['trigname'], 
                        portfolio=portfolio, 
                        run_order_idx=queen_orders__index_dic[king_eval_order['bishop_keys']['client_order_id']], 
                        crypto=king_eval_order['bishop_keys']['qo_crypto'])
            
            charlie_bee['queen_cyle_times']['full_loop_queenorderS__om'] = (datetime.now(est) - s_loop).total_seconds()
            
            return True
        
        except Exception as e:
            print(e)
            print_line_of_error()


    def order_management(STORY_bee, QUEEN, QUEEN_KING, ORDERS, portfolio, QUEENsHeart): 

        #### MAIN ####
        # >for every ticker position join in running-positions to account for total position
        # >for each running position determine to exit the position                
        try:
            # Submitted Orders First
            s_loop = datetime.now(est)
            queen_orders_main(QUEEN=QUEEN, ORDERS=ORDERS, STORY_bee=STORY_bee, portfolio=portfolio, QUEEN_KING=QUEEN_KING)
            charlie_bee['queen_cyle_times']['queen_orders___main'] = (datetime.now(est) - s_loop).total_seconds()

            # Reconcile QUEENs portfolio
            # reconcile_portfolio()

            # God Save the Queen
            s_loop = datetime.now(est)
            PickleData(pickle_file=PB_QUEEN_Pickle, data_to_store=QUEEN)
            charlie_bee['queen_cyle_times']['God_Save_The_Queen__main'] = (datetime.now(est) - s_loop).total_seconds()
            
            # Save Heart to avoid saving Queen to improve speed
            QUEENsHeart['charlie_bee'] = charlie_bee
            QUEENsHeart = queens_heart(heart=QUEENsHeart)
            PickleData(pickle_file=PB_QUEENsHeart_PICKLE, data_to_store=QUEENsHeart, write_temp=False)

        except Exception as e:
            print(e)
            print_line_of_error()
            raise e
        return True


    def refresh_QUEEN_starTickers(QUEEN, STORY_bee, ticker_allowed, story_heartrate=54):
        try:

            now_time = datetime.now().astimezone(est)

            original_state = QUEEN['heartbeat']['available_tickers']
            
            QUEEN['heartbeat']['available_tickers'] = [i for (i, v) in STORY_bee.items() if (now_time - v['story']['time_state']).seconds < story_heartrate]
            ticker_set = set([i.split("_")[0] for i in QUEEN['heartbeat']['available_tickers']])
            # ticker_set = []
            # for ttf in QUEEN['heartbeat']['available_tickers']:
            #     ticker_set.append(ttf.split("_")[0])

            QUEEN['heartbeat']['active_tickers'] = [i for i in ticker_set if i in ticker_allowed]

            new_active = QUEEN['heartbeat']['available_tickers']
            if original_state != new_active:
                print('added dropped / updated tickers')
                added_list = []
                for ttframe in new_active:
                    if ttframe not in original_state:
                        added_list.append({ttframe: return_timestamp_string()})
                        # print("dropped", ttframe, return_timestamp_string())
                if len(added_list) > 0:
                    print("Added ", added_list)
                
                dropped_list = []
                for ttframe in original_state:
                    if ttframe not in new_active:
                        dropped_list.append({ttframe: return_timestamp_string()})
                        # print("dropped", ttframe, return_timestamp_string())
                if len(dropped_list) > 0:
                    print("dropped ", dropped_list)

                QUEEN['heartbeat']['added_list'] = added_list
                QUEEN['heartbeat']['dropped_list'] = dropped_list
                PickleData(PB_QUEEN_Pickle, QUEEN)

            return QUEEN
        except Exception as e:
            print("ERROR", print_line_of_error())
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

        init_logging(queens_chess_piece=queens_chess_piece, db_root=db_root, prod=prod)

        # init files needed
        init_pollen = init_pollen_dbs(db_root=db_root, prod=prod, queens_chess_piece=queens_chess_piece)
        PB_QUEEN_Pickle = init_pollen['PB_QUEEN_Pickle']
        PB_App_Pickle = init_pollen['PB_App_Pickle']
        PB_Orders_Pickle = init_pollen['PB_Orders_Pickle']
        PB_QUEENsHeart_PICKLE = init_pollen['PB_QUEENsHeart_PICKLE']

        # KING = ReadPickleData(master_swarm_KING(prod=prod))
        # QUEENBEE = ReadPickleData(master_swarm_QUEENBEE(prod=prod))
        # QUEEN Databases
        QUEEN_KING = ReadPickleData(pickle_file=PB_App_Pickle)
        QUEEN = ReadPickleData(PB_QUEEN_Pickle)
        QUEEN_KING['king_controls_queen'] = QUEEN_KING['king_controls_queen']
        ORDERS = ReadPickleData(PB_Orders_Pickle)
        
        """ Keys """ 
        api = return_alpaca_user_apiKeys(QUEEN_KING=QUEEN_KING, authorized_user=True, prod=prod)
        if api == False:
            print("API Keys Failed, Queen goes back to Sleep")
            QUEEN['queens_messages'].update({"api_status": 'failed'})
            PickleData(pickle_file=PB_QUEEN_Pickle, data_to_store=QUEEN)
            sys.exit()

        trading_days = hive_dates(api=api)['trading_days']
        init_api_orders_start_date =(datetime.now() - timedelta(days=100)).strftime("%Y-%m-%d")
        init_api_orders_end_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        api_orders = initialize_orders(api, init_api_orders_start_date, init_api_orders_end_date)

        queen_orders_open = api_orders.get('open')
        queen_orders_closed = api_orders.get('closed')
        num__queen_orders_today = len(queen_orders_open) + len(queen_orders_closed)

        portfolio = return_alpc_portolio(api)['portfolio']
        ## !! Reconcile all orders processed in alpaca vs queen_order !! ##

        # Ticker database of pollenstory ## Need to seperate out into tables 
        ticker_db = return_QUEENs__symbols_data(QUEEN=QUEEN, QUEEN_KING=QUEEN_KING, read_storybee=True, read_pollenstory=False) ## async'd func
        # POLLENSTORY = ticker_db['pollenstory']
        STORY_bee = ticker_db['STORY_bee']
        QUEEN['heartbeat']['ticker_db'] =  {'errors': ticker_db.get('errors')}
        
        
        # add new keys
        QUEEN_req = add_key_to_QUEEN(QUEEN=QUEEN, queens_chess_piece=queens_chess_piece)
        if QUEEN_req['update']:
            QUEEN = QUEEN_req['QUEEN']
            PickleData(PB_QUEEN_Pickle, QUEEN)


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
        
        # ticker_allowed = ['SPY', 'ETHUSD', 'BTCUSD', 'META', 'GOOG', 'AAPL', 'TSLA', 'SOFI']
        ticker_allowed = list(KING['ticker_universe'].get('alpaca_symbols_dict').keys())

        QUEEN = refresh_QUEEN_starTickers(QUEEN, STORY_bee, ticker_allowed)

        available_triggerbees = ["sell_cross-0", "buy_cross-0"]

        QUEEN['heartbeat']['available_triggerbees'] = available_triggerbees
        
        print("active trigs", available_triggerbees)
        print("active tickers", QUEEN['heartbeat']['active_tickers'])


        PickleData(pickle_file=PB_QUEEN_Pickle, data_to_store=QUEEN)
        print(f'ProdEnv {prod} Here we go Mario')
        
        pollen_theme_dict = pollen_themes(KING=KING)
        workerbee_run_times = []


        ########################################################
        ########################################################
        #############The Infinite Loop of Time #################
        ########################################################
        ########################################################
        ########################################################

        def init_charlie_bee():
            queens_charlie_bee = os.path.join(db_root, 'charlie_bee.pkl')
            if os.path.exists(os.path.join(db_root, 'charlie_bee.pkl')) == False:
                charlie_bee = {'queen_cyle_times': {}}
                PickleData(queens_charlie_bee, charlie_bee)
            else:
                charlie_bee = ReadPickleData(queens_charlie_bee)
            
            return queens_charlie_bee, charlie_bee
        
        queens_charlie_bee, charlie_bee = init_charlie_bee() # monitors queen order cycles, also seen in heart

        while True:
            s = datetime.now(est)
            # Should you operate now? I thnik the brain never sleeps ?

            if queens_chess_piece.lower() == 'queen': # Rule On High
                
                """ The Story of every Knight and their Quest """
                s = datetime.now(est)
                # refresh db
                s_time = datetime.now(est)
                # QUEEN Databases
                KING = ReadPickleData(master_swarm_KING(prod=prod))
                # QUEENBEE = ReadPickleData(master_swarm_QUEENBEE(prod=prod))
                QUEEN_KING = ReadPickleData(PB_App_Pickle)
                QUEEN['chess_board'] = QUEEN_KING['chess_board']
                QUEENsHeart = ReadPickleData(PB_QUEENsHeart_PICKLE)
                
                portfolio = return_alpc_portolio(api)['portfolio']

                # symbol ticker data >>> 1 all current pieces on chess board && all current running orders
                ticker_db = return_QUEENs__symbols_data(QUEEN=QUEEN, QUEEN_KING=QUEEN_KING, read_storybee=True, read_pollenstory=False) ## async'd func
                # POLLENSTORY = ticker_db['pollenstory']
                STORY_bee = ticker_db['STORY_bee']

                QUEEN = refresh_QUEEN_starTickers(QUEEN=QUEEN, STORY_bee=STORY_bee, ticker_allowed=ticker_allowed)
                charlie_bee['queen_cyle_times']['db_refresh'] = (datetime.now(est) - s_time).total_seconds()

                # Read client App Reqquests
                s_time = datetime.now(est)
                process_app_requests(QUEEN=QUEEN, QUEEN_KING=QUEEN_KING, request_name='queen_sleep', archive_bucket=False)
                process_app_requests(QUEEN=QUEEN, QUEEN_KING=QUEEN_KING, request_name='subconscious', archive_bucket='subconscious_requests')
                charlie_bee['queen_cyle_times']['app'] = (datetime.now(est) - s_time).total_seconds()

                # Process All Orders
                s_time = datetime.now(est)
                order_management(STORY_bee=STORY_bee, QUEEN=QUEEN, QUEEN_KING=QUEEN_KING, ORDERS=ORDERS, portfolio=portfolio, QUEENsHeart=QUEENsHeart)
                charlie_bee['queen_cyle_times']['order management'] = (datetime.now(est) - s_time).total_seconds()

                # Hunt for Triggers
                s_time = datetime.now(est)
                command_conscience(api=api, QUEEN=QUEEN, STORY_bee=STORY_bee, QUEEN_KING=QUEEN_KING) #####>   
                charlie_bee['queen_cyle_times']['command conscience'] = (datetime.now(est) - s_time).total_seconds()
                e = datetime.now(est)
                PickleData(queens_charlie_bee, charlie_bee)
                
            e = datetime.now(est)
            if (e - s).seconds > 20:
                logging.info((queens_chess_piece, ": cycle time > 20 seconds:  SLOW cycle: ", (e - s).seconds ))
                print(queens_chess_piece, str((e - s).seconds),  "sec: ", datetime.now().strftime("%A,%d. %I:%M:%S%p"))
    except Exception as errbuz:
        print(errbuz)
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
        parser.add_argument ('-prod', default='false')
        parser.add_argument ('-client_user', default='stefanstapinski@gmail.com')
        return parser
    
    parser = createParser()
    namespace = parser.parse_args()
    client_user = namespace.client_user
    prod = namespace.prod
    queenbee(client_user, prod, queens_chess_piece='queen')

"""
The Journey is Hard,
Believe in you,
Believe in God,
Believe
"""