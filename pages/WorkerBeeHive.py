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
from chess_piece.king import return_QUEENs__symbols_data, master_swarm_QUEENBEE, hive_master_root, print_line_of_error, ReadPickleData, PickleData
from chess_piece.queen_hive import init_qcp_workerbees, init_queenbee, init_swarm_dbs
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

db=init_swarm_dbs(prod)

def refresh_workerbees(QUEENBEE, QUEEN_KING, backtesting=False, macd=None, reset_only=True, run_all_pawns=False):
    
    reset_only = st.checkbox("reset_only", reset_only)
    backtesting = st.checkbox("backtesting", backtesting)
    run_all_pawns = st.checkbox("run_all_pawns", run_all_pawns)
    run_bishop = st.checkbox("run_bishop", False)
    BISHOP = ReadPickleData(db.get('BISHOP'))
    bishop_screens = st.selectbox("Bishop Screens", options=list(BISHOP.keys()))

    if run_bishop:
        qcp_bees_key = 'workerbees'
        QUEENBEE = {qcp_bees_key: {}}
        df = BISHOP.get(bishop_screens)
        for sector in set(df['sector']):
            token = df[df['sector']==sector]
            tickers=token['symbol'].tolist()
            QUEENBEE[qcp_bees_key][sector] = init_qcp_workerbees(ticker_list=tickers)

    qcp_options = list(QUEENBEE['workerbees'].keys())
    default_qcp = [i for i in QUEENBEE['workerbees'] if len(QUEENBEE['workerbees'][i].get('tickers')) > 0]

    with st.form("workerbees refresh"):
        try:
            if st.session_state['admin']:
 
                pieces = st.multiselect('qcp', options=qcp_options, default=default_qcp)
                refresh = st.form_submit_button("Run WorkerBees", use_container_width=True)
                if refresh:
                    with st.status("Running WorkerBees"):
                        s = datetime.now(est)
                        if backtesting:
                            msg=("executing backtesting")
                            st.info(msg)
                            subprocess.run([f"{sys.executable}", os.path.join(hive_master_root(), 'macd_grid_search.py')])
                        else:
                            queen_workerbees(
                                            qcp_s=pieces,
                                            QUEENBEE=QUEENBEE,
                                            prod=QUEEN_KING.get('prod'), 
                                            reset_only=reset_only, 
                                            backtesting=False, 
                                            run_all_pawns=run_all_pawns, 
                                            macd=None,
                                            streamit=True,
                                                )
                        st.success("WorkerBees Completed")
                        e = datetime.now(est)
                        st.write("refresh time ", (e - s).total_seconds())
        except Exception as e:
            print(e, print_line_of_error())

QUEENBEE = ReadPickleData(master_swarm_QUEENBEE(prod=prod))

qb = init_queenbee(client_user=client_user, prod=prod, queen=False, queen_king=True)
QUEEN_KING = qb.get('QUEEN_KING')
QUEEN = qb.get('QUEEN')

if st.session_state['admin']:
    # with st.expander("WorkerBees Tools"):
    refresh_workerbees(QUEENBEE, QUEEN_KING)

# workerbees = QUEENBEE['workerbees']
# symbols = []
# for qcp, va in workerbees.items():
#     tickers = va.get('tickers')
#     if tickers:
#         for tic in tickers:
#             symbols.append(tic)

# ticker_db = return_QUEENs__symbols_data(QUEEN=False, QUEEN_KING=False, symbols=symbols, swarmQueen=True, read_pollenstory=False, read_storybee=True)
# STORY_bee = ticker_db['STORY_bee']
# tickers_avail = set([i.split("_")[0] for i in STORY_bee.keys()])

# ticker_option = st.selectbox("story keys", options=tickers_avail)
