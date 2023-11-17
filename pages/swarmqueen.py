
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

from pq_auth import signin_main
from chess_piece.king import kingdom__grace_to_find_a_Queen, master_swarm_QUEENBEE, print_line_of_error, ReadPickleData, PickleData, local__filepaths_misc
from chess_piece.queen_hive import add_key_to_KING, init_queenbee, add_new_qcp__to_Queens_workerbees, buy_button_dict_items, wave_analysis__storybee_model, hive_dates, return_market_hours, init_ticker_stats__from_yahoo, refresh_chess_board__revrec, return_queen_orders__query, add_trading_model, set_chess_pieces_symbols, init_pollen_dbs, init_qcp, wave_gauge, return_STORYbee_trigbees, generate_TradingModel, stars, analyze_waves, story_view, pollen_themes, return_timestamp_string, init_logging
from chess_piece.app_hive import display_for_unAuth_client_user, admin_queens_active, symbols_unique_color, cust_graph, custom_graph_ttf_qcp, create_ag_grid_column, download_df_as_CSV, show_waves, send_email, pollenq_button_source, standard_AGgrid, create_AppRequest_package, create_wave_chart_all, create_slope_chart, create_wave_chart_single, create_wave_chart, create_guage_chart, create_main_macd_chart,  queen_order_flow, mark_down_text, mark_down_text, page_line_seperator, local_gif, flying_bee_gif, pollen__story
# from chess_piece.queen_hive import ttf_grid_names_list, buy_button_dict_items, wave_analysis__storybee_model, hive_dates, return_market_hours, init_ticker_stats__from_yahoo, refresh_chess_board__revrec, return_queen_orders__query, add_trading_model, set_chess_pieces_symbols, init_pollen_dbs, init_qcp, wave_gauge, return_STORYbee_trigbees, generate_TradingModel, stars, analyze_waves, story_view, pollen_themes, return_timestamp_string, init_logging
from custom_button import cust_Button

MISC = local__filepaths_misc()


def QB_workerbees(KING, QUEENBEE, admin=True):
    try:
        # QUEENBEE read queen bee and update based on QUEENBEE
        name = 'Workerbees_Admin'
        qcp_bees_key = 'workerbees'
        ticker_allowed = list(KING['ticker_universe'].get('alpaca_symbols_dict').keys())
        
        chess_pieces = set_chess_pieces_symbols(QUEEN_KING=QUEENBEE, qcp_bees_key=qcp_bees_key)
        view = chess_pieces.get('view')
        all_workers = chess_pieces.get('all_workers')
        qcp_ticker_index = chess_pieces.get('ticker_qcp_index')
        current_tickers = qcp_ticker_index.keys()

        with st.expander("New Workerbee"):
            add_new_qcp__to_Queens_workerbees(QUEENBEE=QUEENBEE, qcp_bees_key=qcp_bees_key, ticker_allowed=ticker_allowed)
        
        with st.expander(name, True):
            with st.form(f'Update WorkerBees{admin}'):
                ticker_search = st.text_input("Find Symbol") ####### WORKERBEE
                
                cols = st.columns((1,1,1))
                with cols[1]:
                    st.subheader(name)
                
                cols = st.columns((1,3,2,2,2,2))
                for qcp in all_workers:
                    try:
                        if qcp == 'castle_coin':
                            with cols[0]:
                                st.image(MISC.get('castle_png'), width=74)
                        elif qcp == 'castle':
                            with cols[0]:
                                st.image(MISC.get('castle_png'), width=74)
                        elif qcp == 'bishop':
                            with cols[0]:
                                st.image(MISC.get('bishop_png'), width=74)
                        elif qcp == 'knight':
                            with cols[0]:
                                st.image(MISC.get('knight_png'), width=74)
                        else:
                            with cols[0]:
                                st.image(MISC.get('knight_png'), width=74)
                        
                        ticker_list = QUEENBEE[qcp_bees_key][qcp]['tickers']
                        all_tickers = ticker_allowed # + crypto_symbols__tickers_avail
                        # st.write([i for i in ticker_list if i not in all_tickers])
                        QUEENBEE[qcp_bees_key][qcp]['tickers'] = [i for i in ticker_list if i in all_tickers]

                        with cols[1]:
                            QUEENBEE[qcp_bees_key][qcp]['tickers'] = st.multiselect(label=f'{qcp}', options=ticker_allowed, default=QUEENBEE[qcp_bees_key][qcp]['tickers'], help='Castle Should Hold your Highest Valued Symbols', key=f'{qcp}tickers{admin}')
                        with cols[2]:
                            st.selectbox(label='Model', options=['MACD'], key=f'{qcp}model{admin}')
                        with cols[3]:
                            QUEENBEE[qcp_bees_key][qcp]['MACD_fast_slow_smooth']['fast'] = st.number_input(f'fast', min_value=1, max_value=88, value=int(QUEENBEE[qcp_bees_key][qcp]['MACD_fast_slow_smooth']['fast']), key=f'{qcp}fast{admin}')
                        with cols[4]:
                            QUEENBEE[qcp_bees_key][qcp]['MACD_fast_slow_smooth']['slow'] = st.number_input(f'slow', min_value=1, max_value=88, value=int(QUEENBEE[qcp_bees_key][qcp]['MACD_fast_slow_smooth']['slow']), key=f'{qcp}slow{admin}')
                        with cols[5]:
                            QUEENBEE[qcp_bees_key][qcp]['MACD_fast_slow_smooth']['smooth'] = st.number_input(f'slow', min_value=1, max_value=88, value=int(QUEENBEE[qcp_bees_key][qcp]['MACD_fast_slow_smooth']['smooth']), key=f'{qcp}smooth{admin}')
                    except Exception as e:
                        print(e, qcp)
                        st.write(qcp, " ", e)
                        st.write(QUEENBEE[qcp_bees_key][qcp])

                if st.form_submit_button('Save ChessBoard'):
                    PickleData(pickle_file=QUEENBEE.get('source'), data_to_store=QUEENBEE)
                    st.success("Swarm QueenBee Saved")
                    
                    return True


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