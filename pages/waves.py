
import streamlit as st
from streamlit_extras.switch_page_button import switch_page
from chess_piece.app_hive import set_streamlit_page_config_once, standard_AGgrid
from chess_piece.king import master_swarm_QUEENBEE
from chess_piece.queen_hive import setup_chess_board
from dotenv import load_dotenv
from pq_auth import signin_main

set_streamlit_page_config_once()

if 'authentication_status' not in st.session_state:
    authenticator = signin_main(page="pollenq")

if 'authentication_status' not in st.session_state or st.session_state['authentication_status'] != True:
    switch_page('pollen')


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

from chess_piece.king import master_swarm_KING, ReadPickleData, kingdom__global_vars, return_QUEENs__symbols_data, print_line_of_error
from chess_piece.queen_hive import generate_chess_board, init_queenbee, hive_master_root, refresh_chess_board__revrec, refresh_account_info
from chess_piece.app_hive import show_waves, pollenq_button_source, move_columns_to_front
from custom_button import cust_Button
from custom_grid import st_custom_grid, GridOptionsBuilder
from custom_graph_v1 import st_custom_graph
import hydralit_components as hc



# from ...pollen.pq_auth import signin_main
# auth = signin_main("waves")
# ImportError: attempted relative import with no known parent package


main_root = hive_master_root()  # os.getcwd()
load_dotenv(os.path.join(main_root, ".env"))


import ipdb


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

all_portfolios = ['Queen', 'King', 'Bishop', "RevRec Refresh"]

optoins = []
for op in all_portfolios:
    icon = "fas fa-chess-pawn"
    optoins.append({'id': op, 'icon': "fas fa-chess-pawn", 'label':op})
hc_source_option = hc.option_bar(option_definition=optoins,title='Source', key='waves_revrec_source', horizontal_orientation=True) #,override_theme=over_theme,font_styling=font_fmt,horizontal_orientation=True)

KING = ReadPickleData(master_swarm_KING(st.session_state['prod']))
king_G = kingdom__global_vars()
active_order_state_list = king_G.get('active_order_state_list') # = ['running', 'running_close', 'submitted', 'error', 'pending', 'completed', 'completed_alpaca', 'running_open', 'archived_bee']
active_queen_order_states = king_G.get('active_queen_order_states')

client_user=st.session_state['client_user']
prod=st.session_state['prod']

qb = init_queenbee(client_user, prod, queen=True, queen_king=True, api=True)
QUEEN = qb.get('QUEEN')
QUEEN_KING = qb.get('QUEEN_KING')
api = qb.get('api')

st.info(QUEEN.keys())
if st.toggle("broker portoflio"):
    df = pd.DataFrame([v for i, v in QUEEN['portfolio'].items()])
    st.write(df)


coin_exchange = "CBSE"


all_portfolios_selection = st.selectbox("Portfolio", options=all_portfolios)

acct_info = QUEEN.get('account_info')

if hc_source_option == 'Queen':
    revrec = QUEEN.get('revrec')
elif hc_source_option == 'King':
    revrec = QUEEN_KING.get('revrec')
elif hc_source_option == 'Bishop':
    QUEENBEE = ReadPickleData(master_swarm_QUEENBEE(prod))
    QUEENBEE = setup_chess_board(QUEEN=QUEENBEE)
    QUEEN_KING['chess_board'] = QUEENBEE['workerbees']
    STORY_bee = return_QUEENs__symbols_data(QUEEN=QUEEN, QUEEN_KING=QUEEN_KING, swarmQueen=False, read_pollenstory=False).get('STORY_bee')
    revrec = refresh_chess_board__revrec(acct_info, QUEEN, QUEEN_KING, STORY_bee, active_queen_order_states, chess_board__revrec={}, revrec__ticker={}, revrec__stars={}) ## Setup Board
else:
    STORY_bee = return_QUEENs__symbols_data(QUEEN=QUEEN, QUEEN_KING=QUEEN_KING, swarmQueen=False, read_pollenstory=False).get('STORY_bee')
    revrec = refresh_chess_board__revrec(acct_info, QUEEN, QUEEN_KING, STORY_bee, active_queen_order_states, chess_board__revrec={}, revrec__ticker={}, revrec__stars={}) ## Setup Board

cols = st.columns(3)
tabs = st.tabs([key for key in revrec.keys()])
tab = 0
wave_view_input_cols = ['ticker_time_frame', 'macd_state', 'allocation_long', 'pct_budget_allocation', 'total_allocation_budget', 'star_total_budget', 'star_buys_at_play', 'star_sells_at_play',  'total_allocation_borrow_budget', 'star_borrow_budget', 'allocation_deploy', 'allocation_borrow_deploy', 'star_avg_time_to_max_profit', 'length', 'current_profit', 'time_to_max_profit', 'maxprofit', 'maxprofit_shot', 'end_tier_macd', 'end_tier_vwap', 'end_tier_rsi_ema', 'start_tier_macd', 'start_tier_vwap', 'start_tier_rsi_ema','macd_tier_gain', 'vwap_tier_gain', 'rsi_tier_gain' ] # 'allocation', 'allocation_trinity', 'allocation_trinity_amt'
for revrec_key in revrec.keys():
    with tabs[tab]:
        st.write(revrec_key)
        df = revrec.get(revrec_key)
        if revrec_key == 'waveview':
            all_ = df.copy()
            buys = df[df['bs_position']=='buy']
            sells = df[df['bs_position']!='buy']
            market = df[df['symbol'].isin(['SPY', 'QQQ'])]
            marketsells = market[market['bs_position']!='buy']
            with cols[0]:
                st.write(f"""Deploy Long ${round(sum(all_["allocation_long_deploy"]),0)}$""")
            with cols[0]:
                st.write(f"""Allocation long ${round(sum(all_["allocation_long"]),0)}$""")
            with cols[0]:
                st.write(f"""buys ${round(sum(buys["total_allocation_budget"]),0)}$""")
            with cols[1]:
                st.write(f"""sells ${round(sum(sells["total_allocation_budget"]))}$""")
                st.write(f"""marketsells ${round(sum(marketsells["total_allocation_budget"]))}$""")

            df = move_columns_to_front(df, wave_view_input_cols)
            hide_cols = [i for i in df.columns.tolist() if i not in wave_view_input_cols]
            df = df.rename(columns={i: i.replace('_', ' ') for i in df.columns.tolist()})
            standard_AGgrid(df, hide_cols=hide_cols)
        elif isinstance(df, pd.DataFrame):
            st.dataframe(df)
        else:
            st.write(df)
    
    tab+=1

st.write("RevRec Check")
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

def king_knights_of_the_round_table(revrec):
    waveview = revrec.get('waveview')
    def func(x):
        try:
            return x.split("_")[0]
        except Exception as e:
            print(e)
            return x
    waveview['star'] = waveview.index
    waveview['symbol'] = waveview['star'].apply(lambda x: func(x))

    waveview['symbol_filter'] = np.where((waveview['macd_state'].str.contains('buy')), True, False)
    waveview_buys = waveview[waveview['symbol_filter'] == True]
    buys = waveview_buys.groupby(['symbol']).agg({'allocation_deploy': 'sum'}).reset_index()
    st.dataframe(buys)

    waveview['symbol_filter'] = np.where((waveview['macd_state'].str.contains('sell')), True, False)
    waveview_sells = waveview[waveview['symbol_filter'] == True]
    sells = waveview_sells.groupby(['symbol']).agg({'allocation': 'sum'}).reset_index()
    
    return True

king_knights_of_the_round_table(revrec)


st.write(QUEEN['price_info_symbols'])