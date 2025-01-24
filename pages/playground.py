import streamlit as st
from streamlit_extras.stoggle import stoggle
from PIL import Image
import subprocess
from custom_grid import st_custom_grid
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
from streamlit_extras.switch_page_button import switch_page
import yfinance as yf
import requests
import copy

from plotly.subplots import make_subplots
import plotly.graph_objects as go

from chess_piece.pollen_db import PollenDatabase
from chess_piece.queen_bee import init_BROKER, append_queen_order, god_save_the_queen

from tqdm import tqdm

pg_migration = os.getenv('pg_migration')

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


def sync_current_broker_account(client_user, prod, symbols=[]):
    # Find combinations of orders where the total `filled_qty` matches the target
 
    # WORKERBEE HANDLE WHEN NOT ENOUGH ORDERS AVAILABLE 
    ## Sync current broker account
    qb = init_queenbee(client_user=client_user, prod=prod, broker=True, queen=True, queen_king=True, api=True, revrec=True, queen_heart=True, pg_migration=pg_migration)
    api = qb.get('api')
    QUEEN_KING = qb.get('QUEEN_KING')
    QUEEN = qb.get('QUEEN')
    BROKER = qb.get('BROKER')
    BROKER = init_BROKER(api, BROKER)
    revrec = qb.get('revrec') # qb.get('queen_revrec')

    queen_orders = QUEEN['queen_orders']
    queen_order_ids = queen_orders.index.tolist()
    broker_orders = BROKER['broker_orders']
    storygauge = revrec['storygauge'].copy()
    df = storygauge[storygauge['broker_qty_delta'] < 0].copy()
    if len(df) == 0:
        st.write("There is NO Delta returning out")
        # return False

    god_save = False
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
            st.write(symbol, "No Orders Available go GET MORE ORDERS")
            continue

        # for all Available Orders return orders to match Qty
                # Find matches
        avail_orders['filled_qty'] = avail_orders['filled_qty'].astype(float)
        # find order to match to Qty
        found_orders, total_qty = find_orders_to_meet_delta(avail_orders, broker_qty_delta)
        print(symbol, total_qty)
        # st.write(symbol, total_qty)
        reduce_adjustment_qty = broker_qty_delta - total_qty if broker_qty_delta >= total_qty else total_qty - broker_qty_delta
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
            
            new_queen_order_df = process_order_submission(
                trading_model=trading_model, 
                order=order, 
                order_vars=order_vars,
                trig=trigbee,
                symbol=symbol,
                ticker_time_frame=ticker_time_frame,
                star=star,
                priceinfo=priceinfo_order
            )

            # logging.info(f"SUCCESS on BUY for {ticker}")
            # msg = (f'Ex BUY Order {trigbee} {ticker_time_frame} {round(wave_amo,2):,}')
            append_queen_order(QUEEN, new_queen_order_df)
            god_save = True

    if god_save:
        god_save_the_queen(QUEEN, save_q=True, save_qo=True)

    return True


def sync_current_broker_delta(client_user, prod, symbols=[], god_save=False):
    # Find combinations of orders where the total `filled_qty` matches the target


    # WORKERBEE HANDLE WHEN NOT ENOUGH ORDERS AVAILABLE 
    ## Sync current broker account
    qb = init_queenbee(client_user=client_user, prod=prod, queen=True, revrec=True, pg_migration=pg_migration)
    QUEEN = qb.get('QUEEN')
    revrec = qb.get('revrec') # qb.get('queen_revrec')

    # check broker_qty_delta >> if <0 then find orders, create order link, determine which star to use based on budget, if not budget use 1 year
    # for every broker order, if Order is not in QUEEN then create QUEEN order, seperate by BUY and SELL, run__ vs close__
    
    queen_orders = QUEEN['queen_orders']

    storygauge = revrec['storygauge'].copy()
    df = storygauge[storygauge['broker_qty_delta'] < 0].copy()
    if len(df) == 0:
        st.write("There is NO Delta returning out")
        # return False

    # reduce orders
    df = storygauge[storygauge['broker_qty_delta'] > 0].copy()
    # find orders to reduce
    for symbol in df.index.tolist():
        if symbols:
            if symbol not in symbols:
                continue
        selected_row = df.loc[symbol]
        broker_qty_delta = selected_row.get('broker_qty_delta')
        avail_orders = return_active_orders(QUEEN)
        if len(avail_orders) == 0:
            st.write(symbol, "No Orders Available go GET MORE ORDERS")
            continue
        avail_orders['qty_available'] = avail_orders['qty_available'].astype(float)
        # find order to match to Qty
        found_orders, total_qty = find_orders_to_meet_delta(avail_orders, broker_qty_delta, qty_field='qty_available')
        st.write(symbol, len(found_orders), total_qty)
        # for the found orders you need to match up the qty to the broker_qty_delta
        # fake sell the order and match it an order in broker ..... else create a fake order to store and pull from 
        # OR ARCHIVE

        # Route QUEEN Orders to Close
        for client_order_id in found_orders.index.tolist():
            QUEEN['queen_orders'].at[client_order_id, 'queen_order_state'] = 'completed_pollen'
        
        # if god_save:
        #     god_save_the_queen(QUEEN, save_q=True, save_qo=True)
        

    return True


def init_account_info(client_user, prod):
    broker_info = init_queenbee(client_user=client_user, prod=prod, broker_info=True, pg_migration=pg_migration).get('broker_info') ## WORKERBEE, account_info is in heartbeat already, no need to read this file
    if not broker_info.get('account_info'):
        print("No Account Info")
        return False


def PlayGround():

    prod = st.session_state['prod']
    client_user=st.session_state['client_user']

    if st.button("Sync Current Broker Account -"):
        sync_current_broker_account(client_user, prod)
    if st.button("Sync With Broker Delta +"):
        sync_current_broker_delta(client_user, prod)
    
    print("PLAYGROUND", st.session_state['client_user'])
    king_G = kingdom__global_vars()
    ARCHIVE_queenorder = king_G.get('ARCHIVE_queenorder') # ;'archived'
    active_order_state_list = king_G.get('active_order_state_list') # = ['running', 'running_close', 'submitted', 'error', 'pending', 'completed', 'completed_alpaca', 'running_open', 'archived_bee']
    active_queen_order_states = king_G.get('active_queen_order_states') # = ['submitted', 'accetped', 'pending', 'running', 'running_close', 'running_open']
    CLOSED_queenorders = king_G.get('CLOSED_queenorders') # = ['completed', 'completed_alpaca']
    
    
    db = init_swarm_dbs(prod, pg_migration=True)
    BISHOP = read_swarm_db()

    # delete_dict_keys(BISHOP)

    broker_info = init_queenbee(client_user=client_user, prod=prod, broker_info=True, pg_migration=True).get('broker_info') ## WORKERBEE, account_info is in heartbeat already, no need to read this file
    st.write(broker_info)

    # if True:
    table_name = 'db' if prod else 'db_sandbox'
    QUEENBEE = PollenDatabase.retrieve_data(table_name, key='QUEEN')
    print(QUEENBEE.keys())

    # init files needed
    qb = init_queenbee(client_user=client_user, prod=prod, queen=True, queen_king=True, api=True, broker=True, init=True, pg_migration=True, charlie_bee=True, revrec=True)
    QUEEN = qb.get('QUEEN')
    print(qb.get('QUEEN').get('revrec').keys())
    QUEEN_KING = qb.get('QUEEN_KING')
    api = qb.get('api')
    QUEENsHeart = qb.get('QUEENsHeart')
    BROKER = qb.get('BROKER')
    print(qb.get('CHARLIE_BEE'))
    revrec = qb.get('revrec')

    st.write(pd.DataFrame(QUEENsHeart['heartbeat'].get('portfolio')).T)




    api = qb.get('api')
    if prod:
        BASE_URL = "https://api.alpaca.markets"  # Paper trading URL
    else:
        BASE_URL = "https://paper-api.alpaca.markets"  # Paper trading URL

    def fetch_portfolio_history(api):
        try:
            # Fetch portfolio history
            portfolio_history = api.get_portfolio_history(
                period='3M',  # Options: '1D', '7D', '1M', '3M', '6M', '1A' -> for year
                timeframe='1D',  # Options: '1Min', '5Min', '15Min', '1H', '1D'
            )

            # Convert response to dictionary for better readability
            history = portfolio_history._raw
            df = pd.DataFrame(history)
            # df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
            st.write(df)
            df['profit_loss'] = pd.to_numeric(df['profit_loss'])
            print(sum(df['profit_loss']))
            print(sum(df['profit_loss_pct']))
            print((df.iloc[-1]['equity'] - df.iloc[0]['equity']) / df.iloc[0]['equity'])

            # # Print summary
            # print("Portfolio Equity: ", history['equity'])
            # print("Timestamps: ", history['timestamp'])
            # print("Profit/Loss: ", history['profit_loss'])
            # print("Keys", history.keys())
        # Keys dict_keys(['timestamp', 'equity', 'profit_loss', 'profit_loss_pct', 'base_value', 'base_value_asof', 'timeframe'])
            return history
        except Exception as e:
            print("Error fetching portfolio history:", e)

    # Call the function
    portfolio_history = fetch_portfolio_history(api)
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
    
        KING, users_allowed_queen_email, users_allowed_queen_emailname__db = kingdom__grace_to_find_a_Queen()
        
        # QUEEN = ReadPickleData(st.session_state['PB_QUEEN_Pickle'])
        
        # PB_App_Pickle = st.session_state['PB_App_Pickle']
        # QUEEN_KING = ReadPickleData(pickle_file=PB_App_Pickle)
        # ticker_db = return_QUEENs__symbols_data(QUEEN=QUEEN, QUEEN_KING=QUEEN_KING)
        # POLLENSTORY = ticker_db['pollenstory']
        # STORY_bee = ticker_db['STORY_bee']

        symbols = return_QUEEN_KING_symbols(QUEEN_KING, QUEEN)
        STORY_bee = PollenDatabase.retrieve_all_story_bee_data(symbols).get('STORY_bee')
        POLLENSTORY = PollenDatabase.retrieve_all_pollenstory_data(symbols).get('pollenstory')

        tickers_avail = [set(i.split("_")[0] for i in STORY_bee.keys())][0]

        # ticker_universe = return_Ticker_Universe()
        # alpaca_symbols_dict = ticker_universe.get('alpaca_symbols_dict')
        # alpaca_symbols = {k: i['_raw'] for k,i in alpaca_symbols_dict.items()}
        # df = pd.DataFrame(alpaca_symbols).T
        alpaca_symbols_dict = KING.get('alpaca_symbols_dict')
        # print(alpaca_symbols_dict['SPY']['_raw'].get('exchange'))
        # st.write(alpaca_symbols_dict)
        df = KING.get('alpaca_symbols_df')
        st.write("all symbols")
        with st.expander("all symbols"):
            standard_AGgrid(df)


        st.markdown("[![Click me](app/static/cat.png)](https://pollenq.com)",unsafe_allow_html=True)
        cols = st.columns(2)
        # with cols[0]:
        #     with st.expander('nested columns'):
        #         cols_2 = st.columns(2)
        #         with cols_2[1]:
        #             st.markdown("[![Click me](app/static/cat.png)](https://pollenq.com)",unsafe_allow_html=True)
        
        # with st.expander("button on grid"):
        #     click_button_grid()
        # if st.toggle("nested grid"):
        #     with st.expander("nested grid"):
        #         nested_grid()

        # if st.toggle("pollenstory"):
        with st.expander("pollenstory"):
            ttf = st.selectbox('ttf', list(STORY_bee.keys())) # index=['no'].index('no'))
            data=POLLENSTORY[ttf]
            data['trinity_avg_tier'] = sum(data['trinity_tier']) / len(data)
            default_cols = ['timestamp_est', 'open', 'close', 'high', 'low', 'buy_cross-0', 'buy_cross-0__wave_number', 'trinity_tier', 'trinity_avg_tier']
            cols = st.multiselect('qcp', options=data.columns.tolist(), default=default_cols)
            view=data[cols].copy()
            view = data.reset_index()
            grid = standard_AGgrid(data=view, configure_side_bar=True)

            def create_wave_chart(df):
                title = f'i know'
                fig = make_subplots(rows=1, cols=1, shared_xaxes=True, vertical_spacing=0.01)
                df = df.copy()
                # df['timestamp_est'] = df['timestamp_est'].apply(lambda x: f'{x.month}{"-"}{x.day}{"_"}{x.hour}{":"}{x.minute}')

                fig.add_bar(x=df['timestamp_est'], y=df['trinity_tier'],  row=1, col=1, name='trinity')
                fig.add_bar(x=df['timestamp_est'], y=df['trinity_avg_tier'],  row=1, col=1, name='sellcross wave')
                fig.update_layout(height=600, width=900, title_text=title)
                return fig
            create_wave_chart(data)

        # if st.toggle("wave stories"):
        with st.expander("wave stories"):
            ticker_option = st.selectbox("ticker", options=tickers_avail)
            frame_option = st.selectbox("frame", options=KING['star_times'])
            show_waves(STORY_bee=STORY_bee, ticker_option=ticker_option, frame_option=frame_option)


        if st.toggle("yahoo", True):
            db_qb_root = os.path.join(hive_master_root(), "db")
            yahoo_stats_bee = os.path.join(db_qb_root, "yahoo_stats_bee.pkl")
            db = ReadPickleData(yahoo_stats_bee)
            # st.write(db['AAPL'])
            

            if st.button("Refresh ALL yahoo ticker info from BISHOP"):
                ticker_universe = KING['alpaca_symbols_df']
                main_symbols_full_list = ticker_universe['symbol'].tolist()

                df_info = refresh_yfinance_ticker_info(main_symbols_full_list)
                if type(df_info) == pd.core.frame.DataFrame:
                    BISHOP['ticker_info'] = df_info
                    if pg_migration:
                        PollenDatabase.upsert_data(BISHOP.get('table_name'), key=BISHOP.get('key'), data=BISHOP)
                    else:
                        PickleData(BISHOP.get('source'), BISHOP, console=True)
        
        if st.button("Sync Queen King Symbol Yahoo Stats"):
            symbols = [item for sublist in [v.get('tickers') for v in QUEEN_KING['chess_board'].values()] for item in sublist]
            df_info = refresh_yfinance_ticker_info(symbols)
            if type(df_info) == pd.core.frame.DataFrame:
                BISHOP['queen_story_symbol_stats'] = df_info
                if pg_migration:
                    PollenDatabase.upsert_data(BISHOP.get('table_name'), key=BISHOP.get('key'), data=BISHOP)
                else:
                    PickleData(BISHOP.get('source'), BISHOP, console=True)        
        if 'queen_story_symbol_stats' in BISHOP.keys():
            st.header("QK Yahoo Stats")
            standard_AGgrid(BISHOP['queen_story_symbol_stats'])
        
        if 'ticker_info' in BISHOP.keys():
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
                        PollenDatabase.upsert_data(BISHOP.get('table_name'), key=BISHOP.get('key'), data=BISHOP)
                    else:
                        PickleData(BISHOP.get('source'), BISHOP, console=True)

            st.header(screen_name)
            standard_AGgrid(df_filter, hide_cols=hide_cols)


    except Exception as e:
        print("playground error: ", e,  print_line_of_error())


if __name__ == '__main__':
    signin_main()
    PlayGround()