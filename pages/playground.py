from chess_utils.trigrule_utils import *
import streamlit as st
from streamlit_extras.stoggle import stoggle
from PIL import Image
from pq_auth import signin_main
from chess_piece.queen_hive import *
from chess_piece.app_hive import *
from chess_piece.king import *
from custom_button import cust_Button
from streamlit_option_menu import option_menu
from datetime import datetime, timedelta
import hydralit_components as hc
# from ozz.ozz_bee import send_ozz_call
import pytz
import ipdb
import pandas as pd
import numpy as np
from chat_bot import ozz_bot
import os
# from st_on_hover_tabs import on_hover_tabs
# from streamlit_extras.switch_page_button import switch_page
import yfinance as yf
import requests
import copy

from plotly.subplots import make_subplots
import plotly.graph_objects as go

from chess_piece.pollen_db import PollenDatabase
from chess_piece.queen_bee import god_save_the_queen, init_broker_orders, get_priceinfo_snapshot, save_queen_order # append_queen_order, 
from chess_piece.queen_mind import refresh_chess_board__revrec

from chess_piece.fastapi_queen import get_revrec_lastmod_time, get_bishop_cache

from tqdm import tqdm
import sys

pg_migration = os.getenv('pg_migration')

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



def delete_dict_keys(object_dict):
    bishop_screens = st.selectbox("Bishop Screens", options=list(object_dict.keys()))
    if st.button("Delete Screen"):
        object_dict.pop(bishop_screens)
        PickleData(object_dict.get('source'), object_dict)
        st.success(f"{bishop_screens} Deleted")


def refresh_yfinance_ticker_info(main_symbols_full_list):
    s = datetime.now()
    all_info = {}
    sectors = {}

    # Initialize the progress bar outside the loop
    progress_text = "Operation in progress. Please wait. ({percent}%)"
    my_bar = st.progress(0)

    max_tickers = len(main_symbols_full_list)

    for idx, tic in enumerate(main_symbols_full_list):
        try:
            ticker = yf.Ticker(tic)
            all_info[tic] = ticker.info
            sectors[tic] = ticker.info.get('sector')

            # Update the progress bar with the correct progress and percentage
            progress_percent = (idx + 1) / max_tickers * 100
            my_bar.progress((idx + 1) / max_tickers, text=progress_text.format(percent=int(progress_percent)))
        except Exception as e:
            print_line_of_error("ERROR PLAY", tic)

    my_bar.empty()

    df = pd.DataFrame()

    # Reset progress bar for the second loop
    progress_text = "Processing tickers... ({percent}%)"
    my_bar = st.progress(0)

    total_tickers = len(all_info)

    for idx, (tic, data) in enumerate(all_info.items(), start=1):
        progress_percent = idx / total_tickers * 100
        my_bar.progress(idx / total_tickers, text=progress_text.format(percent=int(progress_percent)))

        token = pd.DataFrame(data.items()).T
        headers = token.iloc[0]
        token.columns = headers
        token = token.drop(0)
        token['ticker'] = tic
        df = pd.concat([df, token], ignore_index=True)

    my_bar.empty()  # Clear the progress bar after the loop completes
    st.write("Saved Yahoo Ticker Info")

    print((datetime.now() - s).total_seconds())
    return df


def find_orders_to_meet_delta(orders, broker_qty_delta, qty_field='filled_qty'):
    """
    Find the orders that meet the target delta quantity
    """
    selected_orders = []
    total_qty = 0

    for idx in orders.index:
        order_qty = orders.loc[idx, qty_field]
        if total_qty + order_qty == broker_qty_delta:
            selected_orders.append(idx)
            total_qty += order_qty
            break
        if total_qty + order_qty > broker_qty_delta:
            break
        selected_orders.append(idx)
        total_qty += order_qty

    if selected_orders:
        return orders.loc[selected_orders], total_qty

    return pd.DataFrame(), 0

def append_queen_order(QUEEN, new_queen_order_df, upsert_to_main_server=False):
    client_order_id = new_queen_order_df.iloc[0]['client_order_id']
    if client_order_id not in QUEEN['queen_orders']['client_order_id'].to_list():
        QUEEN['queen_orders'] = pd.concat([QUEEN['queen_orders'], new_queen_order_df], axis=0) # , ignore_index=True
        QUEEN['queen_orders']['client_order_id'] = QUEEN['queen_orders'].index
        save_queen_order(QUEEN, prod=QUEEN['prod'], client_order_id=client_order_id, upsert_to_main_server=upsert_to_main_server)
    else:
        print("QUEEN ORDER ALREADY EXISTS", client_order_id)
        return False
    return True

def sync_current_broker_account(client_user, prod, symbols=[], testing=True): # WORKERBEE NEED TO FIX FOR new_queen_order, dict to df
    # Find combinations of orders where the total `filled_qty` matches the target
 
    # WORKERBEE HANDLE WHEN NOT ENOUGH ORDERS AVAILABLE 
    ## Sync current broker account
    qb = init_queenbee(client_user=client_user, prod=prod, orders_v2=True, broker=True, queen=True, queen_king=True, api=True, revrec=True, queen_heart=True, pg_migration=pg_migration)
    api = qb.get('api')
    QUEEN_KING = qb.get('QUEEN_KING')
    QUEEN = qb.get('QUEEN')
    BROKER = qb.get('BROKER')
    # BROKER = init_BROKER(api, BROKER)
    BROKER = init_broker_orders(api, BROKER)
    # revrec = qb.get('revrec') # qb.get('queen_revrec')

    # REFRESH REVREC
    king_G = kingdom__global_vars()
    if pg_migration:
        symbols = return_QUEEN_KING_symbols(QUEEN_KING, QUEEN)
        STORY_bee = PollenDatabase.retrieve_all_story_bee_data(symbols).get('STORY_bee')
    else:
        STORY_bee = return_QUEENs__symbols_data(QUEEN=QUEEN, QUEEN_KING=QUEEN_KING, read_storybee=True, read_pollenstory=False).get('STORY_bee') ## async'd func
    revrec = refresh_chess_board__revrec(QUEEN['account_info'], QUEEN, QUEEN_KING, STORY_bee, king_G.get('active_queen_order_states')) ## Setup Board

    queen_orders = QUEEN['queen_orders']
    dddd = QUEEN['queen_orders']['datetime'].max()
    st.write("Queen Orders Last Modified:", dddd)
    queen_order_ids = queen_orders.index.tolist()
    broker_orders = BROKER['broker_orders']
    broker_orders['created_at'] = pd.to_datetime(broker_orders['created_at'], errors='coerce')
    broker_orders = broker_orders.sort_values('created_at', ascending=False)
    storygauge = revrec['storygauge'].copy()

    """ HANDLE DELTA > 0"""
    avail_orders = return_active_orders(QUEEN)
    avail_orders['qty_available'] = avail_orders['qty_available'].astype(float)

    # reduce orders
    god_save = False
    df = storygauge[storygauge['broker_qty_delta'] > 0].copy()
    if len(df) > 0:
        # find orders to reduce
        for symbol in df.index.tolist():
            if symbols:
                if symbol not in symbols:
                    continue
            selected_row = df.loc[symbol]
            broker_qty_delta = selected_row.get('broker_qty_delta')
            symbol_orders = avail_orders[avail_orders['symbol']==symbol].copy()
            
            if len(symbol_orders) == 0:
                st.write(symbol, "No Orders Available go GET MORE ORDERS")
                continue
            # find order to match to Qty
            found_orders, total_qty = find_orders_to_meet_delta(symbol_orders, broker_qty_delta, qty_field='qty_available')
            st.write(f'{symbol} Delta is {broker_qty_delta} FOUND: {total_qty} num orders {len(found_orders)}')
            # for the found orders you need to match up the qty to the broker_qty_delta
            # fake sell the order and match it an order in broker ..... else create a fake order to store and pull from 
            # OR ARCHIVE
            # Route QUEEN Orders to Close
            for client_order_id in found_orders.index.tolist():
                QUEEN['queen_orders'].at[client_order_id, 'queen_order_state'] = 'archived'
                god_save = True
            
        # Refresh RevRec
        st.write("WORKER BEE NEEDS FIX TO SAVE JUST ORDERS BEFORE IMPLEMENTING")
        revrec = refresh_chess_board__revrec(QUEEN['account_info'], QUEEN, QUEEN_KING, STORY_bee, king_G.get('active_queen_order_states')) ## Setup Board
        QUEEN['revrec'] = revrec
        if not testing and god_save:
            god_save_the_queen(QUEEN, save_q=True, save_qo=True, save_rr=True)

    
    """ HANDLE DELTA < 0"""
    god_save = False
    df = storygauge[storygauge['broker_qty_delta'] < 0].copy()
    if len(df) > 0:
        st.write("#Handling BUY ORDERS to MATCH DELTA")
        for symbol in df.index.tolist():
            if symbols:
                if symbol not in symbols:
                    continue
            selected_row = df.loc[symbol]
            broker_qty_delta = abs(selected_row.get('broker_qty_delta'))
            avail_orders = broker_orders[(broker_orders['symbol']==symbol) & 
                                            (broker_orders['side']=='buy') &
                                            (broker_orders['status']=='filled') &
                                            ~(broker_orders.index.isin(queen_order_ids)) # not in QUEEN
                                            ].copy()
            if len(avail_orders) == 0:
                st.write(symbol, "#No Orders Available go GET MORE ORDERS")
                continue

            # for all Available Orders return orders to match Qty
                    # Find matches
            avail_orders['filled_qty'] = avail_orders['filled_qty'].astype(float)
            # find order to match to Qty
            found_orders, total_qty = find_orders_to_meet_delta(avail_orders, broker_qty_delta)
            # print(symbol, total_qty)
            st.write(f'{symbol} found Qty: {total_qty}')
            # reduce_adjustment_qty = broker_qty_delta - total_qty if broker_qty_delta >= total_qty else total_qty - broker_qty_delta
            # If Enough, create QUEEN order and attempt to use by remaining balance, if Not Skewed weight to 1 year ONLY if BUY... or BUY onlys skew evenly
            ## create QUEEN orders
            for client_order_id in found_orders.index.tolist():
                order_data = found_orders.loc[client_order_id].to_dict()
                filled_qty = float(order_data['filled_qty'])
                filled_avg_price = float(order_data['filled_avg_price'])
                star_time = '1Day_1Year' #star_names(kors.get('star_list')[0])
                ticker_time_frame = f'{symbol}_{star_time}'
                symbol, tframe, tperiod = ticker_time_frame.split("_")
                star = f'{tframe}_{tperiod}'
                wave_blocktime = 'afternoon_2-4'
                trigbee = 'buy_cross-0'
                tm_trig = 'buy_cross-0'
                trading_model = QUEEN_KING['king_controls_queen']['symbols_stars_TradingModel'].get("SPY")
                king_order_rules = copy.deepcopy(trading_model['stars_kings_order_rules'][star_time]['trigbees'][tm_trig][wave_blocktime])
                wave_amo = filled_qty * filled_avg_price
                king_order_rules['sell_trigbee_trigger'] = False
                king_order_rules['queen_handles_trade'] = False
                
                # Other Misc
                order_vars = order_vars__queen_order_items(trading_model=trading_model.get('theme'), 
                                                            king_order_rules=king_order_rules, 
                                                            order_side='buy', 
                                                            wave_amo=wave_amo, 
                                                            ticker_time_frame_origin=ticker_time_frame, 
                                                            symbol=symbol,
                                                            trigbee=trigbee,
                                                            tm_trig=tm_trig,
                                                            )


                # get latest pricing
                # coin_exchange = "CBSE"
                # snap = api.get_snapshot(symbol) if crypto == False else api.get_crypto_snapshot(symbol, exchange=coin_exchange)
                # priceinfo_order = {'price': snap.latest_trade.price, 'bid': snap.latest_quote.bid_price, 'ask': snap.latest_quote.ask_price, 'bid_ask_var': snap.latest_quote.bid_price/snap.latest_quote.ask_price}
                priceinfo_order = {'price': filled_avg_price, 
                                'bid': filled_avg_price, 'ask': filled_avg_price, 
                                'bid_ask_var': filled_avg_price}

                # Client Order Id
                order = found_orders.loc[client_order_id].to_dict() # vars(order_submit.get('order'))['_raw']
                
                order_vars['qty_order'] = order.get('filled_qty')
                
                new_queen_order = process_order_submission(
                    broker='alpaca',
                    trading_model=trading_model, 
                    order=order, 
                    order_vars=order_vars,
                    trig=trigbee,
                    symbol=symbol,
                    ticker_time_frame=ticker_time_frame,
                    star=star,
                    priceinfo=priceinfo_order
                )
                new_queen_order_df = pd.DataFrame([new_queen_order]).set_index("client_order_id", drop=False)
                queen_order_idx = new_queen_order_df.iloc[0]['client_order_id']

                # logging.info(f"SUCCESS on BUY for {ticker}")
                st.write(f'SYNC BUY Order {ticker_time_frame} {round(wave_amo,2):,}')
                if not testing:
                    append_queen_order(QUEEN, new_queen_order_df)

        # Refresh RevRec
        revrec = refresh_chess_board__revrec(QUEEN['account_info'], QUEEN, QUEEN_KING, STORY_bee, king_G.get('active_queen_order_states')) ## Setup Board
        QUEEN['revrec'] = revrec
        if not testing and god_save:
            god_save_the_queen(QUEEN, save_q=True, save_qo=True, save_rr=True)

    return True


def adhoc_fix_ttf_shorts(client_user, prod):
    qb = init_queenbee(client_user=client_user, prod=prod, broker=True, queen=True, orders=True, pg_migration=pg_migration)
    ORDERS = qb.get('QUEEN_KING')
    QUEEN = qb.get('QUEEN')
    queen_orders = QUEEN['queen_orders']
    symbols_to_fix = ['SH', 'PSQ']
    orders_to_fix = queen_orders[queen_orders['symbol'].isin(symbols_to_fix)]
    for order in orders_to_fix.index:
        symbol = queen_orders.at[order, 'symbol']
        ttf = queen_orders.at[order, 'ticker_time_frame']
        ticker, ttime, tframe, = ttf.split("_")
        queen_orders.at[order, 'ticker_time_frame'] = f'{symbol}_{ttime}_{tframe}'
        queen_orders.at[order, 'ticker_time_frame_origin'] = f'{symbol}_{ttime}_{tframe}'
        print(queen_orders.at[order, 'ticker_time_frame_origin'])
    
    QUEEN['queen_orders'] = queen_orders
    god_save_the_queen(QUEEN, save_q=True, save_qo=True)

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
        print("MISSING TICKER NOT IN ALPACA", msg)
    
    return queens_master_tickers


# def queenbee_get_priceinfo(QUEEN, active_queen_order_states, info="assumes revrec"):
#     active_order_symbols =  QUEEN['queen_orders'][QUEEN['queen_orders']['queen_order_state'].isin(active_queen_order_states)]['symbol'].unique().tolist()
#     story_symbols = QUEEN['revrec']['storygauge'].index.tolist()
#     read_symbols = list(set(active_order_symbols + story_symbols))
#     price_info_symbols = PollenDatabase.read_priceinfo_table(tickers=read_symbols)
#     price_info_symbols = pd.DataFrame(price_info_symbols).set_index('ticker', drop=False).T.to_dict()
#     QUEEN['price_info_symbols'] = price_info_symbols

#     return QUEEN


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


def PlayGround():
    if st.toggle("Bishop Cashe"):
        data = get_bishop_cache()
        if isinstance(data['ticker_info'], str):
            # Parse JSON string to list
            import json
            parsed_data = json.loads(data['ticker_info'])
            df = pd.DataFrame(parsed_data)
        elif isinstance(data['ticker_info'], list):
            df = pd.DataFrame(data['ticker_info'])
        else:
            df = data['ticker_info']
        
        st.write("BISHOP Ticker Info", df.head())
    
    
    prod = st.session_state['prod']
    if not prod:
        st.warning("SANDBOX MODE")


    table_name = 'db' if prod else 'db_sandbox'
    QUEENBEE = PollenDatabase.retrieve_data(table_name, key='QUEEN')
    KING = kingdom__grace_to_find_a_Queen()
    # st.write(pd.DataFrame(KING['alpaca_symbols_dict']))
    ticker_allowed = list(KING['alpaca_symbols_dict'].keys())


    client_user=st.session_state['client_user']
    # st.write("revrec last mod", get_revrec_lastmod_time(client_user, prod))
    # symbols = st.multiselect("Symbols to Sync", options=ticker_allowed, help="Select symbols to sync. Leave empty to sync all.")
    # if st.button("Sync Current Broker Account"):
    #     st.write("WORKERBEE NEED to FIX APPENDING AND SAVING AN OVERALL TESTING")
    #     sync_current_broker_account(client_user, prod, symbols=symbols)
    
    print("PLAYGROUND", st.session_state['client_user'])
    king_G = kingdom__global_vars()
    ARCHIVE_queenorder = king_G.get('ARCHIVE_queenorder') # ;'archived'
    active_order_state_list = king_G.get('active_order_state_list') # = ['running', 'running_close', 'submitted', 'error', 'pending', 'completed', 'completed_alpaca', 'running_open', 'archived_bee']
    active_queen_order_states = king_G.get('active_queen_order_states') # = ['submitted', 'accetped', 'pending', 'running', 'running_close', 'running_open']
    CLOSED_queenorders = king_G.get('CLOSED_queenorders') # = ['completed', 'completed_alpaca']
    
    db = init_swarm_dbs(prod, pg_migration=True)
    BISHOP = read_swarm_db(prod, 'BISHOP')
    
    if st.toggle("Bishop ticker info"):
        st.write(BISHOP.keys())
        ticker_info = BISHOP.get('ticker_info').set_index('ticker')
        st.write(ticker_info.head())
        st.write(ticker_info.columns.tolist())
        # standard_AGgrid(BISHOP.get('MarketCap50000000__Volume1000000__ShortRatio2__ebitdaMargins0.25'))
        st.write(len(BISHOP.get('2025_Screen')))


    # if True:

    # print(QUEENBEE.keys())
    # init files needed
    # prod = False
    # client_user = 'stapinskistefan@gmail.com'
    main_server = True
    qb = init_queenbee(client_user=client_user, prod=prod, queen=True, orders=True, orders_v2=True, queen_king=True, api=True, broker=True, init=True, pg_migration=True, charlie_bee=True, revrec=True, 
                       main_server=main_server, demo=False)
    api = init_queenbee(client_user=client_user, prod=prod, queen_king=True, api=True, init=True, pg_migration=True, main_server=main_server, demo=False).get('api')
    QUEEN_KING = qb.get('QUEEN_KING')
    if st.toggle("QUEEN_KING king_controls_queen keys"):
        st.write("QUEEN_KING king_controls_queen keys", QUEEN_KING.keys())
    if st.toggle("QUEEN_KING buy_orders"):
        st.write(QUEEN_KING['buy_orders'])
    QUEENsHeart = qb.get('QUEENsHeart')
    BROKER = qb.get('BROKER')
    # standard_AGgrid(BROKER['broker_orders'], key='broker_orders_index')
    QUEEN = qb.get('QUEEN')
    # st.write(QUEEN['account_info'])
    table_name = 'client_user_store' if prod else 'client_user_store_sandbox'
    # db_root = qb.get('db_root')
    # master_conversation_history = PollenDatabase.retrieve_data(table_name, f'{db_root}-MASTER_CONVERSATIONAL_HISTORY')
    # conversation_history = PollenDatabase.retrieve_data(table_name, f'{db_root}-CONVERSATIONAL_HISTORY')
    # session_state = PollenDatabase.retrieve_data(table_name, f'{db_root}-SESSION_STATE')
    # st.write(master_conversation_history, conversation_history, session_state)



    alpaca_symbols_dict = return_Ticker_Universe().get('alpaca_symbols_dict')
    print("READING MASTER QUEEN")
    if pg_migration:
        table_name = 'db' if prod else 'db_sandbox'
        QUEENBEE = PollenDatabase.retrieve_data(table_name, key='QUEEN')
    else:
        QUEENBEE = ReadPickleData(master_swarm_QUEENBEE(prod=prod))
    queens_chess_pieces = [k for k,v in QUEENBEE['workerbees'].items()]
    list_of_lists = [i.get('tickers') for qcp, i in QUEENBEE['workerbees'].items() if qcp in queens_chess_pieces]
    symbols = [item for sublist in list_of_lists for item in sublist]
    symbols = confirm_tickers_available(alpaca_symbols_dict, symbols)


    symbols = return_QUEEN_KING_symbols(QUEEN_KING, QUEEN)
    ticker = st.text_input("Ticker to Refresh from STORYBEE")
    if ticker:
        symbols.append(ticker)
    STORY_bee = PollenDatabase.retrieve_all_story_bee_data(symbols).get('STORY_bee')
    if f'{ticker}_1Minute_1Day' in STORY_bee:
        st.write(STORY_bee[f'{ticker}_1Minute_1Day']['story'])
        current_price = STORY_bee[f'{ticker}_1Minute_1Day']['story']['current_mind'].get('close') #STORY_bee[f'{ticker}_1Minute_1Day']['story'].get('current_price')
        current_ask = STORY_bee[f'{ticker}_1Minute_1Day']['story'].get('current_ask')
        current_bid = STORY_bee[f'{ticker}_1Minute_1Day']['story'].get('current_bid')
        maker_middle = STORY_bee[f'{ticker}_1Minute_1Day']['story'].get('maker_middle')
        ask_bid_variance = STORY_bee[f'{ticker}_1Minute_1Day']['story'].get('ask_bid_variance')
        st.write(f"SPY Price Info from STORYBEE: Price {current_price}, Ask {current_ask}, Bid {current_bid}, Maker Middle {maker_middle}, Ask/Bid Variance {ask_bid_variance}")

    # symbols = return_queenking_board_symbols(QUEEN_KING)
    # snapshot_price_symbols = async_api_alpaca__snapshots_priceinfo(symbols, STORY_bee, api, QUEEN)
    # df_priceinfo_symbols = pd.DataFrame(snapshot_price_symbols)
    # df_priceinfo_symbols = df_priceinfo_symbols.set_index('ticker', drop=False)
    # update_queens_priceinfo_symbols(QUEEN, df_priceinfo_symbols)
    # st.write(QUEEN['price_info_symbols']['priceinfo'].to_dict())
    # st.write(QUEEN['price_info_symbols'])
    # st.write(api.get_snapshot("VALU"))
    # alpaca_symbols_dict = return_Ticker_Universe().get('alpaca_symbols_dict')
    # st.write(alpaca_symbols_dict['GSHD'])


    if st.toggle("Set Queen with New Price Info Symbols", False):
        df = PollenDatabase.read_priceinfo_table()
        df = pd.DataFrame(df)
        st.write("Price Info Table", df)
        active_order_symbols =  QUEEN['queen_orders'][QUEEN['queen_orders']['queen_order_state'].isin(active_queen_order_states)]['symbol'].unique().tolist()
        story_symbols = QUEEN['revrec']['storygauge'].index.tolist()
        price_info_symbols = PollenDatabase.read_priceinfo_table(tickers=active_order_symbols + story_symbols)
        # price_info_symbols = pd.DataFrame(price_info_symbols).set_index('ticker', drop=False).T.to_dict()
        st.write("Active Order Symbols Price Info", price_info_symbols)
        # ipdb.set_trace()
        QUEEN['price_info_symbols'] = queenbee_get_priceinfo(QUEEN, active_queen_order_states)
        QUEEN = refresh_broker_account_portolfio(api, QUEEN)
        ############# Refresh Board ############
        QUEEN['revrec'] = refresh_chess_board__revrec(QUEEN['account_info'], QUEEN, QUEEN_KING, STORY_bee) ## Setup Board



    from chess_piece.pollen_db import MigratePostgres

    def copy_pollen_store_by_symbol_to_MAIN_server(pollen_store='pollen_store'):
        try:
            s = datetime.now()
            symbols = return_symbols_list_from_queenbees_story(all_symbols=True)
            # send_email(subject="Pollen Store Server Sync RUNNING")
            retrieve_all_pollenstory_data = PollenDatabase.retrieve_all_pollenstory_data(symbols).get('pollenstory')
            st.write("Pollen Story Data", retrieve_all_pollenstory_data.keys())

            # Extract the nested dict and add proper key prefixes
            bulk_data = {
                f'POLLEN_STORY_{key}': value 
                for key, value in retrieve_all_pollenstory_data.items()
            }
            # Bulk upsert
            MigratePostgres.upsert_multiple('pollen_store', bulk_data, console=True)

            retrieve_all_story_bee_data = PollenDatabase.retrieve_all_story_bee_data(symbols).get('STORY_bee')
            st.write("Story Bee Data", retrieve_all_story_bee_data.keys())
            bulk_data = {
                f'STORY_BEE_{key}': value
                for key, value in retrieve_all_story_bee_data.items()
            }
            MigratePostgres.upsert_multiple('pollen_store', bulk_data, console=True)

            time_delta = (datetime.now() - s).total_seconds()
            send_email(subject=f"Pollen Store Server Sync COMPLETED {round(time_delta)} seconds", body=f"Migrated {len(symbols)} symbols in {round(time_delta)} seconds.")
        except Exception as e:
            print(e)
            send_email(subject=f"Pollen Store Server Sync FAILED", body=str(e))
        
    if st.button("Migrate Pollen Store to MAIN Server"):
        copy_pollen_store_by_symbol_to_MAIN_server()

    trading_model = QUEEN_KING['king_controls_queen']['symbols_stars_TradingModel'].get("SPY")
    st.write("Trading Model SPY", trading_model)



        # st.write("Index", QUEEN['price_info_symbols'].index)
    symbols = ['SPY', 'GSHD']
    symbols_str = ','.join(symbols)
    if st.toggle("Alpaca API Snapshots Comparison"):
        snapshots = api.get_snapshots(symbols)
        cols = st.columns(2)
        with cols[0]:
            st.write("Snapshots from Alpaca API", snapshots)
            st.write(vars(snapshots['GSHD']))

        # url = f"https://data.alpaca.markets/v2/stocks/snapshots?symbols=GSHD&feed=sip"
        url = f"https://data.alpaca.markets/v2/stocks/snapshots?symbols={symbols_str}&feed=sip"
        api_key_id = QUEEN_KING["users_secrets"]["APCA_API_KEY_ID"]
        api_secret = QUEEN_KING["users_secrets"]["APCA_API_SECRET_KEY"]
        def get_alpaca_snapshots_safe(symbols, headers):
            symbols_str = ','.join(symbols)
            url = f"https://data.alpaca.markets/v2/stocks/snapshots?symbols={symbols_str}&feed=sip"
            
            try:
                response = requests.get(url, headers=headers, timeout=10)
                
                # st.write(f"Status Code: {response.status_code}")
                # st.write(f"Response Headers: {dict(response.headers)}")
                
                if response.status_code == 200:
                    if response.text and response.text.strip():
                        return response.json()
                    else:
                        st.warning("Empty response body")
                        return None
                elif response.status_code == 401:
                    st.error("Authentication failed - check API keys")
                    return None
                elif response.status_code == 422:
                    st.error("Invalid symbols or parameters")
                    st.write("Response:", response.text)
                    return None
                else:
                    st.error(f"API Error {response.status_code}")
                    st.write("Response:", response.text)
                    return None
                    
            except Exception as e:
                st.error(f"Request failed: {e}")
                return None

        # Use it:
        symbols = ['SPY', 'GSHD']
        key_id = "APCA_API_KEY_ID" if prod else "APCA_API_KEY_ID_PAPER"
        key_id = QUEEN_KING["users_secrets"][key_id]
        secret_key = "APCA_API_SECRET_KEY" if prod else "APCA_API_SECRET_KEY_PAPER"
        secret_key = QUEEN_KING["users_secrets"][secret_key]
        # st.write("Using Keys:", key_id, secret_key)
        headers = {
            "APCA-API-KEY-ID": key_id,
            "APCA-API-SECRET-KEY": secret_key
        }

        data = get_alpaca_snapshots_safe(symbols, headers)
        with cols[1]:
            st.write(data['GSHD'])
        st.write(f"vars(snapshots['GSHD']) == data['GSHD']: {str(vars(snapshots['GSHD'])) == str(data['GSHD'])}")
        if data:
            st.write("Snapshots from Alpaca API via Requests", data)


    
    if st.toggle("show QUEEN SIZE"):
        st.write(f"QUEEN object size: {sys.getsizeof(QUEEN)} bytes")
    
    df=return_active_orders(QUEEN)
    active_orders = df.copy()
        # for k, v in QUEEN.items():
        #     print(f"{k}: {sys.getsizeof(v)} bytes")
    
    # st.write(queen_orders.columns.tolist())
    ORDERS = qb.get('ORDERS')
    df = ORDERS['queen_orders']
    del df['honey_gauge']
    del df['macd_gauge']
    if st.toggle("Show Queen Orders", False):
        standard_AGgrid(df)
        # st.write(df)
    
    client_order_store = "queen_orders" if prod else 'queen_orders_sandbox'


    symbols = return_QUEEN_KING_symbols(QUEEN_KING, QUEEN)
    STORY_bee = PollenDatabase.retrieve_all_story_bee_data(symbols).get('STORY_bee')


    revrec = qb.get('revrec')
    storygauge = revrec['storygauge']
    symbol = "ETH/USD"
    existing_orders_df = get_existing_trigrule_orders(symbols, active_orders) #checking all symbols
    check_trigrule_conditions(symbol, storygauge, QUEEN_KING, existing_orders_df)

    # waveview = revrec['waveview']
    # revrec = refresh_chess_board__revrec(QUEEN['account_info'], QUEEN, QUEEN_KING, STORY_bee, king_G.get('active_queen_order_states')) ## Setup Board
    # # is MinAllocation < Long?
    # story = story[story['allocation_deploy']> 0]
    # standard_AGgrid(story, key='storygauge_index')
    # for symbol in story.index.tolist():
    #     wave = waveview[waveview['symbol']==symbol]
    #     wave = wave[wave['allocation_deploy'] > 0]
    #     wave = wave.sort_values('allocation_deploy', ascending=False)
    #     wave['margin_buy'] = wave['allocation_long_deploy'] - wave['allocation_deploy']
    #     not_enough = wave[(wave['allocation_deploy'] > 0) & (wave['allocation_deploy'] < story.at[symbol, 'current_ask'])].copy()
    #     st.write("Margin Buy", wave['margin_buy'].sum())
    #     if len(not_enough) > 0:
    #         st.write(f"Not Enough Allocation Long Deploy for", not_enough)
    #         # give budget to next wave
        
    #     standard_AGgrid(wave, key=f'{symbol}_waveview_index', height=250)


    st.write("BROKER Orders", BROKER['broker_orders'].shape)
    if st.toggle("Show Broker Orders", False):
        standard_AGgrid(BROKER['broker_orders'], key='broker_orders_index')

    print(qb.get('CHARLIE_BEE'))
    revrec = qb.get('revrec')
    
    all_alpaca_tickers = api.list_assets()
    alpaca_symbols_dict = {}
    for n, v in enumerate(all_alpaca_tickers):
        if all_alpaca_tickers[n].status == "active": # and all_alpaca_tickers[n].tradable == True and all_alpaca_tickers[n].exchange != 'CRYPTO' and all_alpaca_tickers[n].exchange != 'OTC':
            alpaca_symbols_dict[all_alpaca_tickers[n].symbol] = vars(
                all_alpaca_tickers[n]
            )

    if st.toggle("Show king_controls_queen Type", False):
        st.write("#ticker refresh star")
        st.write(QUEEN_KING['king_controls_queen'].keys())
        for k,v in QUEEN_KING['king_controls_queen'].items():
            print(k, type(v))

    if st.toggle("QUEENsHeart portfolio"):
        st.write(pd.DataFrame(QUEENsHeart['heartbeat'].get('portfolio')).T)


    try:

        # images
        MISC = local__filepaths_misc()
        learningwalk_bee = MISC['learningwalk_bee']
        mainpage_bee_png = MISC['mainpage_bee_png']

        est = pytz.timezone("US/Eastern")
        utc = pytz.timezone('UTC')
        
        
        cols = st.columns(4)
        with cols[0]:
            st.write("# Welcome to Playground! 👋")
        with cols[1]:
            # st.image(MISC.get('mainpage_bee_png'))
            st.write(st.color_picker("colors"))
        with cols[2]:
            cB = cust_Button(file_path_url="misc/learningwalks_bee_jq.png", height='23px', key='b1', hoverText="HelloMate")
            if cB:
                st.write("Thank you Akash")
        with cols[3]:
            st.image(MISC.get('mainpage_bee_png'))
    
        KING = kingdom__grace_to_find_a_Queen()
        


        tickers_avail = [set(i.split("_")[0] for i in STORY_bee.keys())][0]
        # st.write(fetch_dividends(QUEEN_KING['users_secrets'].get('APCA_API_SECRET_KEY'), QUEEN_KING['users_secrets'].get('APCA_API_KEY_ID')))
        # ticker_universe = return_Ticker_Universe()
        # alpaca_symbols_dict = ticker_universe.get('alpaca_symbols_dict')
        # alpaca_symbols = {k: i['_raw'] for k,i in alpaca_symbols_dict.items()}
        # df = pd.DataFrame(alpaca_symbols).T
        alpaca_symbols_dict = KING.get('alpaca_symbols_dict')
        # print(alpaca_symbols_dict['SPY']['_raw'].get('exchange'))
        # st.write(alpaca_symbols_dict)
        df = KING.get('alpaca_symbols_df')
        st.write("all symbols")
        if st.toggle("show all symbols", False):
            standard_AGgrid(df, key='all_symbols')


        st.markdown("[![Click me](app/static/cat.png)](https://pollenq.com)",unsafe_allow_html=True)
        cols = st.columns(2)

        # if st.toggle("wave stories"):
        with st.expander("wave stories"):
            ticker_option = st.selectbox("ticker", options=tickers_avail)
            frame_option = st.selectbox("frame", options=KING['star_times'])
            show_waves(STORY_bee=STORY_bee, ticker_option=ticker_option, frame_option=frame_option)


        if st.toggle("yahoo", False):
            # db_qb_root = os.path.join(hive_master_root(), "db")
            # yahoo_stats_bee = os.path.join(db_qb_root, "yahoo_stats_bee.pkl")
            # db = ReadPickleData(yahoo_stats_bee)
            # st.write(db['AAPL'])
            

            if st.button("Refresh ALL yahoo ticker info from BISHOP"):
                ticker_universe = KING['alpaca_symbols_df']
                main_symbols_full_list = ticker_universe['symbol'].tolist()

                df_info = refresh_yfinance_ticker_info(main_symbols_full_list)
                if type(df_info) == pd.core.frame.DataFrame:
                    BISHOP['ticker_info'] = df_info
                    if pg_migration:
                        PollenDatabase.upsert_data(BISHOP.get('table_name'), BISHOP.get('key'), BISHOP)
                    else:
                        PickleData(BISHOP.get('source'), BISHOP, console=True)
        
        if st.button("Sync Queen King Symbol Yahoo Stats"):
            symbols = [item for sublist in [v.get('tickers') for v in QUEEN_KING['chess_board'].values()] for item in sublist]
            df_info = refresh_yfinance_ticker_info(symbols)
            if type(df_info) == pd.core.frame.DataFrame:
                BISHOP['queen_story_symbol_stats'] = df_info
                if pg_migration:
                    PollenDatabase.upsert_data(BISHOP.get('table_name'), BISHOP.get('key'),BISHOP)
                else:
                    PickleData(BISHOP.get('source'), BISHOP, console=True)        
        
        if st.toggle("Show Queen Story Symbol Yahoo Stats"):
            st.header("QK Yahoo Stats")
            st.write(BISHOP['queen_story_symbol_stats'])
            standard_AGgrid(BISHOP['queen_story_symbol_stats'])
        
        if st.toggle("Bishop Stock Screener"):
            cols = st.columns(3)
            with cols[0]:
                market_cap = st.number_input("marker cap >=", value=50000000)
                volume = st.number_input("volume >=", value=1000000)
            with cols[1]:
                shortRatio = st.number_input("shortRatio <=", value=2)
                ebitdaMargins = st.number_input("ebitdaMargins >=", min_value=-1.0, max_value=1.0, value=.25)
            
            show_all = st.toggle("show all tickers")
            df = BISHOP.get('ticker_info')

            hide_cols = df.columns.tolist()
            
            view_cols = ['symbol', 'sector', 'shortName']
            num_cols = ['dividendRate', 'dividendYield', 'volume', 'averageVolume', 'marketCap', 'shortRatio', 'ebitdaMargins']
            hide_cols = [i for i in hide_cols if i not in view_cols + num_cols]
            
            def clean_ticker_info_df(df):
                df = df.fillna('')
                df = df[df['sector']!='']
                for col in num_cols:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                
                return df
            
            df=clean_ticker_info_df(df)

            avail_symbols = KING['alpaca_symbols_df']['symbol'].tolist()
            df = df[df['symbol'].isin(avail_symbols)]
            # screener
            def stock_screen(df, market_cap=50000000, volume=1000000, shortRatio=2, ebitdaMargins=.25, show_all=False):
                if show_all:
                    return df
                df = df[df['marketCap'] >= market_cap]
                df = df[df['volume'] >= volume]
                df = df[df['shortRatio'] < shortRatio]
                df = df[df['ebitdaMargins'] > ebitdaMargins]
                return df

            df = stock_screen(df, market_cap, volume, shortRatio, ebitdaMargins, show_all)
            df['exchange'] = df['symbol'].apply(lambda x: alpaca_symbols_dict[x]['_raw'].get('exchange'))
            # fitler out exchanges
            df_filter = df[df['exchange']!= 'OTC'].copy()
            if len(df) != len(df_filter):
                st.warning("Check for tickers lost in exchange filter")
            default_name = f'MarketCap{market_cap}__Volume{volume}__ShortRatio{shortRatio}__ebitdaMargins{ebitdaMargins}'
            with st.form("Save Screen"):
                screen_name = st.text_input('Screen Name', value=default_name)
                if st.form_submit_button("Save Screen to Bishop"):
                    BISHOP[screen_name] = df_filter
                    if pg_migration:
                        PollenDatabase.upsert_data(BISHOP.get('table_name'),BISHOP.get('key'), BISHOP)
                    else:
                        PickleData(BISHOP.get('source'), BISHOP, console=True)

            st.header(screen_name)
            standard_AGgrid(df_filter, hide_cols=hide_cols, paginationOn=True)


    except Exception as e:
        print_line_of_error("playground error: , {e}")


if __name__ == '__main__':
    signin_main()
    print(st.session_state['prod'])
    PlayGround()
    # client_user = st.session_state['client_user']
    # qb = init_queenbee(client_user=client_user, prod=prod, broker=True, queen=True, queen_king=True, api=True, revrec=True, queen_heart=True, pg_migration=pg_migration)
    # api = qb.get('api')
    # QUEEN_KING = qb.get('QUEEN_KING')
    # QUEEN = qb.get('QUEEN')

    # st.write(QUEEN.keys())
    # st.write(pd.DataFrame(QUEEN['portfolio']))