import pandas as pd
import logging
import os
import pandas as pd
from datetime import datetime, timedelta, date
import pytz
import subprocess
import sys

from PIL import Image
from dotenv import load_dotenv
import os
import requests

import streamlit as st
from pq_auth import signin_main
import time
import argparse


# main chess piece
from chess_piece.workerbees import queen_workerbees
# from chess_piece.workerbees_manager import workerbees_multiprocess_pool
from chess_piece.app_hive import set_streamlit_page_config_once, queen_messages_grid__apphive, admin_queens_active, stop_queenbee, read_QUEEN, pollenq_button_source, trigger_airflow_dag, send_email, flying_bee_gif, display_for_unAuth_client_user, queen__account_keys, local_gif, mark_down_text, update_queencontrol_theme, progress_bar, page_line_seperator, return_runningbee_gif__save
from chess_piece.king import return_QUEENs__symbols_data, master_swarm_QUEENBEE, kingdom__global_vars, hive_master_root, print_line_of_error, master_swarm_KING, menu_bar_selection, kingdom__grace_to_find_a_Queen, streamlit_config_colors, local__filepaths_misc, ReadPickleData, PickleData
from chess_piece.queen_hive import create_QueenOrderBee, generate_chessboards_trading_models, stars, return_queen_controls, generate_chess_board, kings_order_rules, return_timestamp_string, return_alpaca_user_apiKeys, refresh_account_info, init_KING, add_key_to_KING, setup_instance, add_key_to_app, init_queenbee, pollen_themes, hive_dates, return_market_hours

# componenets
from streamlit_extras.switch_page_button import switch_page
from streamlit_extras.stoggle import stoggle
import hydralit_components as hc
from custom_button import cust_Button
from custom_text import custom_text, TextOptionsBuilder

# ozz
# from ozz.ozz_bee import send_ozz_call

import ipdb


pd.options.mode.chained_assignment = None
est = pytz.timezone("US/Eastern")

if 'authorized_user' not in st.session_state:
    signin_main("workerbees")

if st.session_state["authorized_user"] != True:
    st.error("you do not have permissions young fellow")
    st.stop()

client_user = st.session_state['username']
prod = st.session_state['production']


def refresh_workerbees(QUEENBEE, QUEEN_KING, backtesting=False, macd=None, reset_only=True, run_all_pawns=False):
    
    with st.form("workerbees refresh"):
        try:
            if st.session_state['admin']:
                reset_only = st.checkbox("reset_only", reset_only)
                backtesting = st.checkbox("backtesting", backtesting)
                run_all_pawns = st.checkbox("run_all_pawns", run_all_pawns)
                qcp_options = list(QUEENBEE['workerbees'].keys())
                pieces = st.multiselect('qcp', options=qcp_options, default=['castle', 'bishop', 'knight'])

                refresh = st.form_submit_button("Run WorkerBees", use_container_width=True)
                if refresh:
                    with st.spinner("Running WorkerBees"):
                        s = datetime.now(est)
                        if backtesting:
                            msg=("executing backtesting")
                            st.info(msg)
                            subprocess.run([f"{sys.executable}", os.path.join(hive_master_root(), 'macd_grid_search.py')])
                        else:
                            queen_workerbees(qcp_s=pieces, 
                                                prod=QUEEN_KING.get('prod'), 
                                                reset_only=reset_only, 
                                                backtesting=False, 
                                                run_all_pawns=run_all_pawns, 
                                                macd=None)
                        st.success("WorkerBees Completed")
                        e = datetime.now(est)
                        st.write("refresh time ", (e - s).total_seconds())
        except Exception as e:
            print(e, print_line_of_error())

PB_QUEENBEE_Pickle = master_swarm_QUEENBEE(prod=prod)
QUEENBEE = ReadPickleData(PB_QUEENBEE_Pickle)

qb = init_queenbee(client_user=client_user, prod=prod, queen=False, queen_king=True)
QUEEN_KING = qb.get('QUEEN_KING')
QUEEN = qb.get('QUEEN')

if st.session_state['admin']:
    # with st.expander("WorkerBees Tools"):
    refresh_workerbees(QUEENBEE, QUEEN_KING)


ticker_db = return_QUEENs__symbols_data(None, QUEEN_KING, swarmQueen=True, read_pollenstory=False, read_storybee=True)
# POLLENSTORY = ticker_db['pollenstory']
STORY_bee = ticker_db['STORY_bee']

ticker_option = st.selectbox("story keys", options=STORY_bee.get('tickers_avail'))
st.write("Swarm tickers_available ", len(STORY_bee.get('tickers_avail')))