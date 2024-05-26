
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
from dotenv import load_dotenv
import random
import streamlit as st
import os
import copy

from pq_auth import signin_main
from chess_piece.king import kingdom__grace_to_find_a_Queen, master_swarm_QUEENBEE, print_line_of_error, ReadPickleData, PickleData, local__filepaths_misc
from chess_piece.queen_hive import setup_chess_board, init_qcp_workerbees, init_swarm_dbs, stars, add_key_to_KING, init_queenbee, set_chess_pieces_symbols, return_timestamp_string
from chess_piece.app_hive import display_for_unAuth_client_user, admin_queens_active
from custom_button import cust_Button

import ipdb

MISC = local__filepaths_misc()

def ensure_swarm_queen_workerbees(QUEENBEE, qcp_bees_key):
    workerbee_vars = init_qcp_workerbees()
    qcp_pieces = QUEENBEE[qcp_bees_key].keys()
    for k, var_default in workerbee_vars.items():
        for qcp in qcp_pieces:
            if k not in QUEENBEE[qcp_bees_key][qcp].keys():
                print(f'Key Missing {k} -- from qcp {qcp}')
                QUEENBEE[qcp_bees_key][qcp][k] = var_default
    return QUEENBEE




def add_new_qcp__to_Queens_workerbees(QUEENBEE, qcp_bees_key, ticker_allowed):
    try:
        old_tickers = []
        for qcp in QUEENBEE[qcp_bees_key].keys():
            tickers=QUEENBEE[qcp_bees_key][qcp].get('tickers')
            if tickers:
                old_tickers = old_tickers + tickers
        
        models = ['MACD', 'story__AI']
        qcp_pieces = QUEENBEE[qcp_bees_key].keys()
        qcp = st.text_input(label='piece name', value=f'pawn_{len(qcp_pieces)}', help="Theme your names to match your strategy")
        if qcp in qcp_pieces:
            st.error("Chess Piece Name must be Unique")
            st.stop()
        
        cols = st.columns(2)

        QUEENBEE[qcp_bees_key][qcp] = init_qcp_workerbees()
           
        with cols[0]:
            QUEENBEE[qcp_bees_key][qcp]['tickers'] = st.multiselect(label=f'{qcp} symbols', options=ticker_allowed, default=None, help='Try not to Max out number of piecesm, only ~10 allowed', key='swarm_tickers_selected')
        with cols[1]:
            QUEENBEE[qcp_bees_key][qcp]['model'] = st.selectbox(label='-', options=models, index=models.index(QUEENBEE[qcp_bees_key][qcp].get('model')), key=f'{qcp}model')

        dup_tickers = [i for i in st.session_state['swarm_tickers_selected'] if i in old_tickers]
        if dup_tickers:
            st.error(f"  duplicate tickers {dup_tickers}")

        star_options = list(stars().keys())
        with st.form('add new qcp'):
            m_fast = int(QUEENBEE[qcp_bees_key][qcp]['MACD_fast_slow_smooth']['fast'])
            m_slow = int(QUEENBEE[qcp_bees_key][qcp]['MACD_fast_slow_smooth']['slow'])
            m_smooth = int(QUEENBEE[qcp_bees_key][qcp]['MACD_fast_slow_smooth']['smooth'])
            refresh_star = QUEENBEE[qcp_bees_key][qcp]['refresh_star']
            cols = st.columns((1,6,2,2,2,2,2))
            with cols[0]:
                st.image(MISC.get('queen_crown_url'), width=64)
            
            # if QUEENBEE[qcp_bees_key][qcp]['model'] == 'story__AI':
            #     # first_symbol = QUEENBEE[qcp_bees_key][qcp]['tickers'][0]
            #     # ttf_macd_wave_ratios = ReadPickleData(os.path.join(hive_master_root(), 'backtesting/macd_backtest_analysis.csv'))
            #     st.write("Lets Let AI Wave Analysis Handle Wave")
            # else:

                with cols[3]:
                    QUEENBEE[qcp_bees_key][qcp]['MACD_fast_slow_smooth']['fast'] = st.number_input("fast", min_value=1, max_value=33, value=m_fast, key=f'{qcp}fast')
                with cols[4]:
                    QUEENBEE[qcp_bees_key][qcp]['MACD_fast_slow_smooth']['slow'] = st.number_input("slow", min_value=1, max_value=33, value=m_slow, key=f'{qcp}slow')
                with cols[5]:
                    QUEENBEE[qcp_bees_key][qcp]['MACD_fast_slow_smooth']['smooth'] = st.number_input("smooth", min_value=1, max_value=33, value=m_smooth, key=f'{qcp}smooth')            
                with cols[6]:
                    QUEENBEE[qcp_bees_key][qcp]['refresh_star'] = st.selectbox("refresh_star", options=star_options, index=star_options.index(refresh_star), key=f'{qcp}refresh_star') 

            if st.form_submit_button('Save New qcp'):
                PickleData(QUEENBEE.get('source'), QUEENBEE)
    except Exception as e:
        print_line_of_error()



def QB_workerbees(KING, QUEENBEE, qcp_bees_key='workerbees', admin=True, ):
    try:
        # QUEENBEE read queen bee and update based on QUEENBEE
        name = 'Workerbees_Admin'
        
        ticker_allowed = list(KING['ticker_universe'].get('alpaca_symbols_dict').keys())
        
        run_bishop = st.checkbox("run_bishop", False)

        if run_bishop:
            QUEENBEE = setup_chess_board(QUEEN=QUEENBEE, qcp_bees_key='bishop')

        chess_pieces = set_chess_pieces_symbols(QUEEN_KING=QUEENBEE, qcp_bees_key=qcp_bees_key)
        st.write(chess_pieces.get('dups'))
        view = chess_pieces.get('view')
        all_workers = chess_pieces.get('all_workers')
        qcp_ticker_index = chess_pieces.get('ticker_qcp_index')
        current_tickers = qcp_ticker_index.keys()
        star_options = list(stars().keys())

        QUEENBEE = ensure_swarm_queen_workerbees(QUEENBEE, qcp_bees_key)

        with st.expander("New Workerbee"):
            add_new_qcp__to_Queens_workerbees(QUEENBEE=QUEENBEE, qcp_bees_key=qcp_bees_key, ticker_allowed=ticker_allowed)
        
        with st.expander(name, True):
            with st.form(f'Update WorkerBees{admin}'):
                ticker_search = st.text_input("Find Symbol") ####### WORKERBEE
                
                cols = st.columns((1,1,1))
                with cols[1]:
                    st.subheader(name)
                
                cols = st.columns(3)
                col_n = 0
                for qcp in all_workers:
                    try:
                        # if qcp == 'castle_coin':
                        #     with cols[col_n]:
                        #         st.image(MISC.get('castle_png'), width=74)
                        # elif qcp == 'castle':
                        #     with cols[col_n]:
                        #         st.image(MISC.get('castle_png'), width=74)
                        # elif qcp == 'bishop':
                        #     with cols[col_n]:
                        #         st.image(MISC.get('bishop_png'), width=74)
                        # elif qcp == 'knight':
                        #     with cols[col_n]:
                        #         st.image(MISC.get('knight_png'), width=74)
                        # else:
                        #     with cols[col_n]:
                        #         st.image(MISC.get('knight_png'), width=74)
                        
                        ticker_list = QUEENBEE[qcp_bees_key][qcp]['tickers']
                        all_tickers = ticker_allowed # + crypto_symbols__tickers_avail
                        refresh_star = QUEENBEE[qcp_bees_key][qcp]['refresh_star']
                        QUEENBEE[qcp_bees_key][qcp]['tickers'] = [i for i in ticker_list if i in all_tickers]

                        with cols[col_n]:
                            QUEENBEE[qcp_bees_key][qcp]['tickers'] = st.multiselect(label=f'{qcp}', options=ticker_allowed, default=QUEENBEE[qcp_bees_key][qcp]['tickers'], help='Castle Should Hold your Highest Valued Symbols', key=f'{qcp}tickers{admin}')
                        # with cols[col_n]:
                        #     st.selectbox(label='Model', options=['MACD'], key=f'{qcp}model{admin}')
                        # with cols[col_n]:
                        #     QUEENBEE[qcp_bees_key][qcp]['MACD_fast_slow_smooth']['fast'] = st.number_input(f'fast', min_value=1, max_value=88, value=int(QUEENBEE[qcp_bees_key][qcp]['MACD_fast_slow_smooth']['fast']), key=f'{qcp}fast{admin}')
                        # with cols[col_n]:
                        #     QUEENBEE[qcp_bees_key][qcp]['MACD_fast_slow_smooth']['slow'] = st.number_input(f'slow', min_value=1, max_value=88, value=int(QUEENBEE[qcp_bees_key][qcp]['MACD_fast_slow_smooth']['slow']), key=f'{qcp}slow{admin}')
                        # with cols[col_n]:
                        #     QUEENBEE[qcp_bees_key][qcp]['MACD_fast_slow_smooth']['smooth'] = st.number_input(f'slow', min_value=1, max_value=88, value=int(QUEENBEE[qcp_bees_key][qcp]['MACD_fast_slow_smooth']['smooth']), key=f'{qcp}smooth{admin}')
                        with cols[col_n]:
                            QUEENBEE[qcp_bees_key][qcp]['refresh_star'] = st.selectbox("refresh_star", options=star_options, index=star_options.index(refresh_star), key=f'{qcp}refresh_star{admin}') 
                        col_n+=1
                        if col_n>2:
                            col_n=0
                    except Exception as e:
                        print(e, qcp)
                        st.write(qcp, " ", e)
                        st.write(QUEENBEE[qcp_bees_key][qcp])

                if st.form_submit_button('Save ChessBoard'):
                    PickleData(pickle_file=QUEENBEE.get('source'), data_to_store=QUEENBEE)
                    st.success("Swarm QueenBee Saved")
                    
                    return True

                from collections import Counter

                def find_duplicates(lst):
                    # Count occurrences of each item in the list
                    counts = Counter(lst)
                    
                    # Filter out items with count > 1
                    duplicates = [item for item, count in counts.items() if count > 1]
                    
                    return duplicates

                # Example usage
                my_list = QUEENBEE[qcp_bees_key].keys()
                my_tic_list = []
                for qn, q in QUEENBEE[qcp_bees_key].items():
                    if q.get('tickers'):
                        my_tic_list = my_tic_list + q.get('tickers')
                duplicates = find_duplicates(my_list)
                duplicates_tickers = find_duplicates(my_tic_list)
                st.write(duplicates)
                st.write(duplicates_tickers)


        return True
    except Exception as e:
        print(e, print_line_of_error())

authenticator = signin_main(page="pollenq")
prod = st.session_state['production']
authorized_user = st.session_state['authorized_user']
client_user = st.session_state["username"]

st.session_state['sneak_name'] = ' ' if 'sneak_name' not in st.session_state else st.session_state['sneak_name']
print(st.session_state['sneak_name'], st.session_state['username'], return_timestamp_string())

if st.session_state['authentication_status'] != True: ## None or False
    
    display_for_unAuth_client_user()
    st.stop()


if st.session_state['admin'] != True:
    st.error("No Soup for you")
    st.stop()


prod = st.session_state['production']
prod = False if 'sneak_peak' in st.session_state and st.session_state['sneak_peak'] else prod
QUEENBEE = ReadPickleData(master_swarm_QUEENBEE(prod))
KING, users_allowed_queen_email, users_allowed_queen_emailname__db = kingdom__grace_to_find_a_Queen()
qb = init_queenbee(client_user=client_user, prod=prod, queen=True, queen_king=True, api=True, init=True)
QUEEN = qb.get('QUEEN')
QUEEN_KING = qb.get('QUEEN_KING')
api = qb.get('api')

chess_pieces = set_chess_pieces_symbols(QUEEN_KING=QUEEN_KING, qcp_bees_key='chess_board')
tt = chess_pieces.get('ticker_qcp_index')

chess_pieces = set_chess_pieces_symbols(QUEEN_KING=QUEENBEE, qcp_bees_key='workerbees')
qq = chess_pieces.get('ticker_qcp_index')


# df = pd.DataFrame(QUEEN_KING['chess_board'].items())
def flatten_data(data):
    flattened_data = []

    for piece, attributes in data.items():
        tickers = attributes.pop('tickers')
        
        for ticker in tickers:
            flat_attributes = {'ticker': ticker, 'piece': piece}
            flat_attributes.update(attributes)
            # Flatten nested dictionaries
            for key, value in attributes.items():
                # if isinstance(value, dict):
                #     for sub_key, sub_value in value.items():
                #         flat_attributes[f"{key}_{sub_key}"] = sub_value
                # else:
                flat_attributes[key] = value
            flattened_data.append(flat_attributes)
    
    return flattened_data

cols = st.columns(2)

flattened_data = flatten_data(data=copy.deepcopy(QUEENBEE['workerbees']))
df = pd.DataFrame(flattened_data)
df.set_index('ticker', inplace=True)
with cols[0]:
    st.data_editor(df)


flattened_data = flatten_data(data=copy.deepcopy(QUEEN_KING['chess_board']))
df = pd.DataFrame(flattened_data)
df.set_index('ticker', inplace=True)
with cols[1]:
    st.data_editor(df)

st.sidebar.write('admin:', st.session_state["admin"])
# add new keys
KING_req = add_key_to_KING(KING=KING)
if KING_req.get('update'):
    KING = KING_req['KING']
    PickleData(KING.get('source'), KING)

with st.sidebar:
    with st.expander("admin"):
        cust_Button("misc/bee.jpg", hoverText='admin users', key='admin_users', height='34px')
        cust_Button("misc/bee.jpg", hoverText='send queen', key='admin_queens', height='34px')


# if st.session_state.get('admin_queens'):
#     admin_send_queen_airflow(KING)
if st.session_state.get('admin_users'):
    admin_queens_active(KING.get('source'), KING)

QB_workerbees(KING, QUEENBEE, admin=True)

with st.sidebar:
    st.write(pd.DataFrame([i for i in qq if i not in tt]))