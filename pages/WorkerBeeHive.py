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
from chess_piece.king import hive_master_root_db, master_swarm_QUEENBEE, hive_master_root, print_line_of_error, ReadPickleData, read_QUEENs__pollenstory
from chess_piece.queen_hive import init_qcp_workerbees, init_queenbee, init_swarm_dbs, read_swarm_db, return_Ticker_Universe
from chess_piece.app_hive import trigger_py_script, standard_AGgrid
# componenets
from streamlit_extras.switch_page_button import switch_page
from streamlit_extras.stoggle import stoggle
import hydralit_components as hc
from custom_button import cust_Button
from custom_text import custom_text, TextOptionsBuilder

from chess_piece.pollen_db import PollenDatabase


import ipdb

load_dotenv(".env")

pg_migration = os.environ.get('pg_migration')

pd.options.mode.chained_assignment = None
est = pytz.timezone("US/Eastern")

def create_workerbee_queen(QUEENBEE, df=None, bishop_screens=None): # sector symbol
    qcp_bees_key = 'workerbees'
    QUEENBEE = {qcp_bees_key: {}}

    if bishop_screens:
        df = BISHOP.get(bishop_screens)

    sector_tickers = {}
    for sector in set(df['sector']):
        token = df[df['sector']==sector]
        tickers=token['symbol'].tolist()
        QUEENBEE[qcp_bees_key][sector] = init_qcp_workerbees(ticker_list=tickers)
        sector_tickers[sector] = len(tickers)
    
    st.write(sector_tickers)

    return QUEENBEE
# create workerbee queen



def refresh_workerbees(QUEENBEE, BISHOP, backtesting=False, macd=None, reset_only=True, run_all_pawns=False):
    
    
    reset_only = st.checkbox("reset_only", reset_only)
    backtesting = st.checkbox("backtesting", backtesting)
    run_all_pawns = st.checkbox("run_all_pawns", run_all_pawns)
    hedge_funds = st.checkbox("hedge_funds", False)
    run_bishop = st.checkbox("run_bishop", False)
    upsert_to_main_server = st.checkbox("Main Server")
    
    bishop_screens = st.selectbox("Bishop Screens", options=list(BISHOP.keys()))

    if run_bishop:

        qcp_bees_key = 'workerbees'
        QUEENBEE = {qcp_bees_key: {}}
        df = BISHOP.get(bishop_screens)
        sector_tickers = {}
        for sector in set(df['sector']):
            token = df[df['sector']==sector]
            tickers=token['symbol'].tolist()
            QUEENBEE[qcp_bees_key][sector] = init_qcp_workerbees(ticker_list=tickers)
            sector_tickers[sector] = len(tickers)
        
        st.write(sector_tickers)

    if hedge_funds:
        # read_hedge_funds and compare with whats avail in alpaca
        from pages.hedgefunds import read_infotable
        df = read_infotable()
        df = df.dropna(subset=['NAMEOFISSUER'])
        df['VALUE'] = pd.to_numeric(df['VALUE'], errors='coerce').fillna(0).astype(int)
        cusip_mapping = pd.read_csv(os.path.join(hive_master_root_db(), 'cusip_tickers.csv'))
        cusip_mapping = dict(zip(cusip_mapping['CUSIP'], cusip_mapping['Ticker']))
        df['symbol'] = df['CUSIP'].map(cusip_mapping).fillna("MISSING")
        df = df[df['symbol'] != "MISSING"]
        alpaca_symbols_dict = return_Ticker_Universe().get('alpaca_symbols_dict')
        df = df.groupby(['symbol']).agg({'VALUE': 'sum'}).reset_index()
        df = df.sort_values('VALUE', ascending=False)
        df['alpaca'] = df['symbol'].isin(list(alpaca_symbols_dict.keys()))
        df = df[df['alpaca']==True]
        df['sector'] = 'hedgefunds'
        df = df.head(1000)
        st.write(df)
        
        QUEENBEE = create_workerbee_queen(QUEENBEE, df)
        qcp_options = list(QUEENBEE['workerbees'].keys())
        default_qcp = [i for i in QUEENBEE['workerbees'] if len(QUEENBEE['workerbees'][i].get('tickers')) > 0]
        pass

    qcp_options = list(QUEENBEE['workerbees'].keys())
    default_qcp = [i for i in QUEENBEE['workerbees'] if len(QUEENBEE['workerbees'][i].get('tickers')) > 0]
    prod = st.session_state['prod']

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
                            # script_path = os.path.join(hive_master_root(), 'macd_grid_search.py')
                            # trigger_py_script(script_path)
                            with st.spinner("Running Backtesting"):
                                from macd_grid_search import run_backtesting_pollenstory
                                run_backtesting_pollenstory(QUEENBEE, True, pieces)
                        else:
                            queen_workerbees(
                                            qcp_s=pieces,
                                            QUEENBEE=QUEENBEE,
                                            prod=prod, 
                                            reset_only=reset_only, 
                                            backtesting=False, 
                                            run_all_pawns=run_all_pawns, 
                                            macd=macd,
                                            streamit=True,
                                            pg_migration=pg_migration,
                                            upsert_to_main_server=upsert_to_main_server,
                                                )
                        st.success("WorkerBees Completed")
                        e = datetime.now(est)
                        st.write("refresh time ", (e - s).total_seconds())
        except Exception as e:
            print_line_of_error(f'WBHIVE {e}')


if __name__ == '__main__':

    if 'authorized_user' not in st.session_state:
        signin_main("workerbees")

    if st.session_state["authorized_user"] != True:
        st.error("you do not have permissions young fellow")
        st.stop()

    client_user = st.session_state['username']
    prod = st.session_state['prod']


    db=init_swarm_dbs(prod)

    if pg_migration:
        table_name = 'db' if prod else 'db_sandbox'
        QUEENBEE = PollenDatabase.retrieve_data(table_name=table_name, key='QUEEN')
        BISHOP = read_swarm_db(prod, 'BISHOP')
    else:
        QUEENBEE = ReadPickleData(master_swarm_QUEENBEE(prod=prod))
        BISHOP = ReadPickleData(db.get('BISHOP'))

    # qb = init_queenbee(client_user=client_user, prod=prod, queen=False, queen_king=True)
    tabs = st.tabs(['Workerbees'])
    if st.session_state['admin']:
        st.write("ADMIN")
        with tabs[0]:
            refresh_workerbees(QUEENBEE, BISHOP)


    MACD_WAVES = pd.read_csv(os.path.join(hive_master_root(), "backtesting/macd_backtest_analysis.txt"))
    standard_AGgrid(MACD_WAVES)

    MACD_WAVES = pd.read_csv(os.path.join(hive_master_root(), "backtesting/macd_grid_search_blocktime.txt"))
    standard_AGgrid(MACD_WAVES)