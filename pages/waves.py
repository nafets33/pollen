
import streamlit as st
from streamlit_extras.switch_page_button import switch_page
from chess_piece.app_hive import set_streamlit_page_config_once, standard_AGgrid
from chess_piece.king import return_QUEEN_KING_symbols
from chess_piece.queen_hive import init_swarm_dbs, init_qcp_workerbees,refresh_broker_account_portolfio
from dotenv import load_dotenv
from pq_auth import signin_main
import ipdb 

import pandas as pd
import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import pytz
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from itertools import islice
from PIL import Image
import random

import os
import time

from chess_piece.king import master_swarm_KING, ReadPickleData, kingdom__global_vars, return_QUEENs__symbols_data, print_line_of_error, streamlit_config_colors
from chess_piece.queen_hive import init_queenbee, hive_master_root, read_swarm_db, bishop_ticker_info
from chess_piece.app_hive import show_waves, pollenq_button_source, move_columns_to_front
import hydralit_components as hc
from chess_piece.queen_mind import refresh_chess_board__revrec
from chess_piece.pollen_db import PollenDatabase
from chess_utils.conscience_utils import story_return


#### MOVE STORY STYLE TO UTILS Generate COLORS
def save_king_queen(QUEEN_KING):
    QUEEN_KING['king_controls_queen']['buying_powers']['Jq']['total_longTrade_allocation'] = st.session_state['cash_slider']
    PollenDatabase.upsert_data(QUEEN_KING.get('table_name'), QUEEN_KING.get('key'), QUEEN_KING)

def cash_slider(QUEEN_KING, key='cash_slider'):
    cash = QUEEN_KING['king_controls_queen']['buying_powers']['Jq']['total_longTrade_allocation']
    cash = max(min(cash, 1), -1)
    return st.number_input("Cash %", min_value=-1.0, max_value=1.0, value=cash, on_change=lambda: save_king_queen(QUEEN_KING), key=key)


def queen_data(client_user, prod):
    qb = init_queenbee(client_user, prod, queen=True, orders_v2=True, queen_king=True, api=True, pg_migration=pg_migration)
    QUEEN = qb.get('QUEEN')
    QUEEN_KING = qb.get('QUEEN_KING')
    api = qb.get('api')
    return QUEEN, QUEEN_KING, api



pg_migration = os.getenv("pg_migration")

def waves():
    main_root = hive_master_root()  # os.getcwd()
    load_dotenv(os.path.join(main_root, ".env"))



    pd.options.mode.chained_assignment = None

    scriptname = os.path.basename(__file__)
    queens_chess_piece = os.path.basename(__file__)

    page = 'waves'
    pq_buttons = pollenq_button_source()
    # with st.sidebar:
    # q_or_qk_toggle = st.toggle("QUEEN King RevRec", False)
    # with st.sidebar:
    # q_or_qk_toggle = st.toggle("QUEEN RevRec", False)
    # hc_source_option = hc.option_bar(option_definition=pq_buttons.get('waves_queen_qk_source_toggle'),title='Source', key='waves_revrec_source', horizontal_orientation=True) #,override_theme=over_theme,font_styling=font_fmt,horizontal_orientation=True)

    all_portfolios = ["RevRec Refresh", 'Queen', 'King', 'Bishop']

    optoins = []
    for op in all_portfolios:
        icon = "fas fa-chess-pawn"
        optoins.append({'id': op, 'icon': "fas fa-chess-pawn", 'label':op})
    hc_source_option = hc.option_bar(option_definition=optoins,title='Source', key='waves_revrec_source', horizontal_orientation=True) #,override_theme=over_theme,font_styling=font_fmt,horizontal_orientation=True)

    client_user=st.session_state['client_user']
    print(client_user, "WAVES")

    prod=st.session_state['prod']
    KING = ReadPickleData(master_swarm_KING(prod))
    king_G = kingdom__global_vars()
    active_order_state_list = king_G.get('active_order_state_list') # = ['running', 'running_close', 'submitted', 'error', 'pending', 'completed', 'completed_alpaca', 'running_open', 'archived_bee']
    active_queen_order_states = king_G.get('active_queen_order_states')


    QUEEN, QUEEN_KING, api = queen_data(client_user, prod)
    cash_slider(QUEEN_KING)
    QUEEN = refresh_broker_account_portolfio(api, QUEEN)
    if pg_migration:
        table_name = 'client_user_store' if prod else 'client_user_store_sandbox'
        db_keys_df = (pd.DataFrame(PollenDatabase.get_all_keys_with_timestamps(table_name))).rename(columns={0:'key', 1:'timestamp'})
        db_keys_df['key_name'] = db_keys_df['key'].apply(lambda x: x.split("-")[-1])
        db_keys_df = db_keys_df.set_index('key_name')
        last_qk_mod = str(db_keys_df.at['QUEEN_KING', 'timestamp'])
    else:
        last_qk_mod = str(os.stat(QUEEN_KING.get('source')).st_mtime)
    
    if 'last_qk_mod' in st.session_state and st.session_state['last_qk_mod'] != last_qk_mod:
        st.write("QK updated Refresh Clear Cache")
        st.cache_data.clear()
        st.success("Cache Cleared")
    
    st.session_state['last_qk_mod'] = last_qk_mod

    if st.sidebar.button("Clear Cache"):
        st.cache_data.clear()
        st.success("Cache Cleared")

    st.info(QUEEN.keys())
    if st.toggle("broker portoflio"):
        df = pd.DataFrame([v for i, v in QUEEN['portfolio'].items()])
        st.write(df)


    coin_exchange = "CBSE"

    acct_info = QUEEN.get('account_info')
    if hc_source_option == 'Queen':
        revrec = QUEEN.get('revrec')
                # Broker Data        
        df_broker_portfolio = pd.DataFrame([v for i, v in QUEEN['portfolio'].items()])
        df_broker_portfolio = df_broker_portfolio.set_index('symbol', drop=False)
        st.write([i for i in df_broker_portfolio.index if i not in revrec['storygauge'].index])
    elif hc_source_option == 'King':
        revrec = QUEEN_KING.get('revrec')
    elif hc_source_option == 'Bishop':
        # QUEENBEE = ReadPickleData(master_swarm_QUEENBEE(prod))
        workerbees = 'workerbees'
        QUEENBEE = {workerbees: {}}
        db = init_swarm_dbs(prod)
                
        if pg_migration:
            BISHOP = read_swarm_db(prod, 'BISHOP')
        else:
            BISHOP = ReadPickleData(db.get('BISHOP'))
        
        screens = [ i for i in BISHOP.keys() if i != 'source']
        screen = st.selectbox("Bishop Screens", options=screens, index=screens.index('400_10M'))
        df = BISHOP.get(screen)
        for sector in set(df['sector']):
            token = df[df['sector']==sector]
            tickers=token['symbol'].tolist()
            QUEENBEE[workerbees][sector] = init_qcp_workerbees(ticker_list=tickers, buying_power=0)
        
        QUEEN_KING['chess_board'] = QUEENBEE['workerbees']
        symbols = [item for sublist in [v.get('tickers') for v in QUEEN_KING['chess_board'].values()] for item in sublist]
        s = datetime.now()
        if pg_migration:
            symbols = return_QUEEN_KING_symbols(QUEEN_KING, QUEEN)
            STORY_bee = PollenDatabase.retrieve_all_story_bee_data(symbols).get('STORY_bee')
        else:
            symbols = [item for sublist in [v.get('tickers') for v in QUEEN_KING['chess_board'].values()] for item in sublist]
            STORY_bee = return_QUEENs__symbols_data(QUEEN=QUEEN, QUEEN_KING=QUEEN_KING, swarmQueen=False, read_pollenstory=False).get('STORY_bee')
        st.header(f'call stymbols {(datetime.now()-s).total_seconds()}')
        s = datetime.now()
        revrec = refresh_chess_board__revrec(acct_info, QUEEN, QUEEN_KING, STORY_bee, active_queen_order_states, wave_blocktime='morning_9-11') ## Setup Board
        st.header(f'revrec {(datetime.now()-s).total_seconds()}')
    else:
        s = datetime.now()
        if pg_migration:
            symbols = return_QUEEN_KING_symbols(QUEEN_KING, QUEEN)
            STORY_bee = PollenDatabase.retrieve_all_story_bee_data(symbols).get('STORY_bee')
        else:
            symbols = [item for sublist in [v.get('tickers') for v in QUEEN_KING['chess_board'].values()] for item in sublist]
            STORY_bee = return_QUEENs__symbols_data(QUEEN=QUEEN, QUEEN_KING=QUEEN_KING, swarmQueen=False, read_pollenstory=False).get('STORY_bee')

        st.header(f'call stymbols {(datetime.now()-s).total_seconds()}')
        s = datetime.now()
        # df_broker_portfolio = pd.DataFrame([v for i, v in QUEEN['portfolio'].items()])
        # df_broker_portfolio = df_broker_portfolio.set_index('symbol', drop=False)
        revrec = refresh_chess_board__revrec(acct_info, QUEEN, QUEEN_KING, STORY_bee, active_queen_order_states) ## Setup Board
        st.header(f'revrec {(datetime.now()-s).total_seconds()}')

    cols = st.columns(3)
    tabs = st.tabs([key for key in revrec.keys()])
    tab = 0
    wave_view_input_cols = ['ticker_time_frame', 'alloc_macd_tier', 'macd_tier_gain_pct', 'start_tier_macd', 'end_tier_macd', 'vwap_tier_gain_pct',  'start_tier_vwap', 'end_tier_vwap', 'rsi_ema_tier_gain_pct', 'start_tier_rsi_ema', 'end_tier_rsi_ema',   'macd_tier_gain', 'vwap_tier_gain', 'rsi_tier_gain', 'macd_state', 'allocation_long', 'pct_budget_allocation', 'total_allocation_budget', 'star_total_budget', 'star_buys_at_play', 'star_sells_at_play',  'total_allocation_borrow_budget', 'star_borrow_budget', 'allocation_deploy', 'allocation_borrow_deploy', 'star_avg_time_to_max_profit', 'length', 'current_profit', 'time_to_max_profit', 'maxprofit', 'maxprofit_shot',  ] # 'allocation', 'allocation_trinity', 'allocation_trinity_amt'
    for revrec_key in revrec.keys():
        with tabs[tab]:
            st.write(f"#RevRec KEY {revrec_key}")
            df = revrec.get(revrec_key)
            if revrec_key == 'waveview':
                all_ = df.copy()
                buys = df[df['bs_position']=='buy']
                sells = df[df['bs_position']!='buy']
                market = df[df['symbol'].isin(['SPY', 'QQQ'])]
                marketsells = market[market['bs_position']!='buy']
                st.write(f"""Star Total Budget ${round(sum(all_["star_total_budget"]),0)}$""")
                st.write(f"""Star Total Budget Allocation ${round(sum(all_["total_allocation_budget"]),0)}$""")
                # with cols[0]:
                #     st.write(f"""Deploy Long ${round(sum(all_["allocation_long_deploy"]),0)}$""")
                # with cols[0]:
                #     st.write(f"""Allocation long ${round(sum(all_["allocation_long"]),0)}$""")
                # with cols[0]:
                #     st.write(f"""buys ${round(sum(buys["total_allocation_budget"]),0)}$""")
                # with cols[1]:
                #     st.write(f"""sells ${round(sum(sells["total_allocation_budget"]))}$""")
                #     st.write(f"""marketsells ${round(sum(marketsells["total_allocation_budget"]))}$""")

                # df.loc['Total', 'star_total_budget'] = df['star_total_budget'].sum()
                df = move_columns_to_front(df, wave_view_input_cols)
                hide_cols = [i for i in df.columns.tolist() if i not in wave_view_input_cols]
                df = df.rename(columns={i: i.replace('_', ' ') for i in df.columns.tolist()})
                standard_AGgrid(df, hide_cols=hide_cols, key=f'grid{revrec_key}')

            elif revrec_key == 'WAVE_ANALYSIS':
                for objj, obj in revrec[revrec_key]['STORY_bee_wave_analysis'].items():
                    for k, data in obj.items():
                        st.write("wave analysis key", k)
                        st.dataframe(data) if isinstance(data, pd.DataFrame) else st.write(data)

            if isinstance(df, pd.DataFrame):
                standard_AGgrid(df, key=f'grid {revrec_key}')
            else:
                st.write(df)
            
            tab+=1

    st.write("# RevRec Check")
    df = revrec['waveview']
    wave_revrec_key_cols = ['ticker_time_frame', 'allocation_long', 'macd_state', 'pct_budget_allocation', 'total_allocation_budget', 'alloc_maxprofit_shot', 'alloc_currentprofit', 'alloc_time', 'alloc_ttmp_length', 'maxprofit_shot_weight_score', 'current_profit_deviation_pct', 'current_profit_deviation', 'alloc_powerlen']
    df = df[wave_revrec_key_cols]
    standard_AGgrid(df)
    
    if st.toggle("wave stories", False):
        try:
            with st.expander("wave stories"):
                tic_avial = list(set([i.split("_")[0] for (i, v) in STORY_bee.items()]))
                ticker_option = st.selectbox("ticker", options=tic_avial)
                frame_option = st.selectbox("frame", options=KING['star_times'])
                show_waves(STORY_bee=STORY_bee, ticker_option=ticker_option, frame_option=frame_option)

                ticker_time_frame = f'{ticker_option}_{frame_option}'

                wave_series = STORY_bee[ticker_time_frame]["waves"]["buy_cross-0"]

                st.dataframe(wave_series)
        except Exception as e:
            print_line_of_error(e)

    if st.toggle("test story fastappi return", True):
        st.write(QUEEN['price_info_symbols'])
        df = story_return(QUEEN_KING, revrec, prod=True)
        st.write(df)
        print("HERE")


if __name__ == '__main__':

    authenticator = signin_main(page="pollenq")

    if 'authentication_status' not in st.session_state or st.session_state['authentication_status'] != True:
        switch_page('pollen')
    
    waves()