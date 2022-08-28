from asyncore import poll
from turtle import width
import pandas as pd  # pip install pandas openpyxl
import plotly.express as px  # pip install plotly-express
import streamlit as st  # pip install streamlit
# QueenBee
import logging
from enum import Enum
from signal import signal
from symtable import Symbol
import time
# import alpaca_trade_api as tradeapi
import asyncio
import os
import pandas as pd
import numpy as np
import pandas_ta as ta
import sys
# from alpaca_trade_api.rest import TimeFrame, URL
# from alpaca_trade_api.rest_async import gather_with_concurrency, AsyncRest
from dotenv import load_dotenv
import threading
import sys
import datetime
from datetime import date, timedelta
import pytz
from typing import Callable
import random
import collections
import pickle
from tqdm import tqdm
from stocksymbol import StockSymbol
import requests
from collections import defaultdict
import ipdb
import tempfile
import shutil
from scipy.stats import linregress
from scipy import stats
import math
import matplotlib.pyplot as plt
from plotly.subplots import make_subplots
from PIL import Image
import mplfinance as mpf
import plotly.graph_objects as go
import base64
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode
from QueenHive import KINGME, queen_orders_view, story_view, return_alpc_portolio, return_dfshaped_orders, ReadPickleData, pollen_themes, PickleData, return_timestamp_string, return_api_keys, read_pollenstory, read_queensmind, read_csv_db, split_today_vs_prior, check_order_status
import json
import argparse

scriptname = os.path.basename(__file__)
if 'sandbox' in scriptname:
    prod = False
else:
    prod = True

main_root = os.getcwd()
db_root = os.path.join(main_root, 'db')
db_app_root = os.path.join(db_root, 'app')

bee_image = os.path.join(db_root, 'bee.jpg')
image = Image.open(bee_image)
st.set_page_config(
     page_title="pollenq",
     page_icon=image,
     layout="wide",
     initial_sidebar_state="expanded",
     menu_items={
         'Get Help': 'https://www.extremelycoolapp.com/help',
         'Report a bug': "https://www.extremelycoolapp.com/bug",
         'About': "# This is a header. This is an *extremely* cool app!"
     }
 )
col1, col2, col3, col4 = st.columns(4)
# col1_sb, col2_sb = st.sidebar.columns(2)
# with col1_sb:
st.sidebar.button("ReRun")
# with col2_sb:
st.sidebar.image(image, caption='pollenq', width=89)

bee_power_image = os.path.join(db_root, 'power.jpg')
# with col4:
#     st.image(Image.open(bee_image), width=89)

queens_chess_piece = os.path.basename(__file__)
log_dir = dst = os.path.join(db_root, 'logs')


def init_logging(queens_chess_piece, db_root):
    loglog_newfile = False
    log_dir = dst = os.path.join(db_root, 'logs')
    log_dir_logs = dst = os.path.join(log_dir, 'logs')
    if os.path.exists(dst) == False:
        os.mkdir(dst)
    if prod:
        log_name = f'{"log_"}{queens_chess_piece}{".log"}'
    else:
        log_name = f'{"log_"}{queens_chess_piece}{"_sandbox_"}{".log"}'

    log_file = os.path.join(log_dir, log_name)
    if loglog_newfile:
        # copy log file to log dir & del current log file
        datet = datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S_%p')
        dst_path = os.path.join(log_dir_logs, f'{log_name}{"_"}{datet}{".log"}')
        shutil.copy(log_file, dst_path) # only when you want to log your log files
        os.remove(log_file)
    else:
        # print("logging",log_file)
        logging.basicConfig(filename=log_file,
                            filemode='a',
                            format='%(asctime)s:%(name)s:%(levelname)s: %(message)s',
                            datefmt='%m/%d/%Y %I:%M:%S %p',
                            level=logging.INFO,
                            force=True)
    
    return True

init_logging(queens_chess_piece=queens_chess_piece, db_root=db_root)


# prod = True
pd.options.mode.chained_assignment = None
est = pytz.timezone("US/Eastern")
load_dotenv()
# >>> initiate db directories
system = 'windows' #mac, windows

# """ Keys """
api_key_id = os.environ.get('APCA_API_KEY_ID')
api_secret = os.environ.get('APCA_API_SECRET_KEY')
base_url = "https://api.alpaca.markets"
keys = return_api_keys(base_url, api_key_id, api_secret)
rest = keys[0]['rest']
api = keys[0]['api']

# Paper
api_key_id_paper = os.environ.get('APCA_API_KEY_ID_PAPER')
api_secret_paper = os.environ.get('APCA_API_SECRET_KEY_PAPER')
base_url_paper = "https://paper-api.alpaca.markets"
keys_paper = return_api_keys(base_url=base_url_paper, 
    api_key_id=api_key_id_paper, 
    api_secret=api_secret_paper,
    prod=False)
rest_paper = keys_paper[0]['rest']
api_paper = keys_paper[0]['api']


# Client Tickers
src_root, db_dirname = os.path.split(db_root)
client_ticker_file = os.path.join(src_root, 'client_tickers.csv')
df_client = pd.read_csv(client_ticker_file, dtype=str)
client_symbols = df_client.tickers.to_list()
crypto_currency_symbols = ['BTCUSD', 'ETHUSD']
coin_exchange = "CBSE"


today_day = datetime.datetime.now().day


def subPlot():
    st.header("Sub Plots")
    # st.balloons()
    fig = plt.figure(figsize = (10, 5))

    #Plot 1
    data = {'C':15, 'C++':20, 'JavaScript': 30, 'Python':35}
    Courses = list(data.keys())
    values = list(data.values())
    
    plt.xlabel("Programming Environment")
    plt.ylabel("Number of Students")

    plt.subplot(1, 2, 1)
    plt.bar(Courses, values)

    #Plot 2
    x = np.array([35, 25, 25, 15])
    mylabels = ["Python", "JavaScript", "C++", "C"]

    plt.subplot(1, 2, 2)
    plt.pie(x, labels = mylabels)

    st.pyplot(fig)



def df_plotchart(title, df, y, x=False, figsize=(14,7), formatme=False):
    st.markdown('<div style="text-align: center;">{}</div>'.format(title), unsafe_allow_html=True)
    if x == False:
        return df.plot(y=y,figsize=figsize)
    else:
        if formatme:
            df['chartdate'] = df['chartdate'].apply(lambda x: f'{x.month}{"-"}{x.day}{"_"}{x.hour}{":"}{x.minute}')
            return df.plot(x='chartdate', y=y,figsize=figsize)
        else:
            return df.plot(x=x, y=y,figsize=figsize)
  
def build_AGgrid_df(data, reload_data=False, fit_columns_on_grid_load=True):
    gb = GridOptionsBuilder.from_dataframe(data)
    gb.configure_pagination(paginationAutoPageSize=True) #Add pagination
    gb.configure_side_bar() #Add a sidebar
    gb.configure_selection('multiple', use_checkbox=True, groupSelectsChildren="Group checkbox select children") #Enable multi-row selection
    gb.configure_column("update_column", header_name="Update", editable=True, groupable=True)


    gridOptions = gb.build()
    gridOptions['rememberGroupStateWhenNewData'] = 'true'


    grid_response = AgGrid(
        data,
        gridOptions=gridOptions,
        data_return_mode='AS_INPUT', 
        update_mode='MODEL_CHANGED', 
        fit_columns_on_grid_load=fit_columns_on_grid_load,
        theme='blue', #Add theme color to the table
        enable_enterprise_modules=True,
        height=750, 
        # width='100%',
        reload_data=reload_data
    )
    return grid_response

def create_main_macd_chart(df):
    title = df.iloc[-1]['name']
    # st.markdown('<div style="text-align: center;">{}</div>'.format(title), unsafe_allow_html=True)
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.1999, row_heights=[0.7, 0.3])
    # df.set_index('timestamp_est')
    # df['chartdate'] = f'{df["chartdate"].day}{df["chartdate"].hour}{df["chartdate"].minute}'
    df=df.copy()
    df['chartdate'] = df['chartdate'].apply(lambda x: f'{x.month}{"-"}{x.day}{"_"}{x.hour}{":"}{x.minute}')
    fig.add_ohlc(x=df['chartdate'], close=df['close'], open=df['open'], low=df['low'], high=df['high'])
    # fig.add_scatter(x=df['chartdate'], y=df['close'], mode="lines", row=1, col=1)
    fig.add_scatter(x=df['chartdate'], y=df['macd'], mode="lines", row=2, col=1)
    fig.add_scatter(x=df['chartdate'], y=df['signal'], mode="lines", row=2, col=1)
    fig.add_bar(x=df['chartdate'], y=df['hist'], row=2, col=1)
    fig.update_layout(height=600, width=900, title_text=title)
    return fig

def create_slope_chart(df):
    title = df.iloc[-1]['name']
    # st.markdown('<div style="text-align: center;">{}</div>'.format(title), unsafe_allow_html=True)
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.01)
    # df.set_index('timestamp_est')
    # df['chartdate'] = f'{df["chartdate"].day}{df["chartdate"].hour}{df["chartdate"].minute}'
    df = df.copy()
    df['chartdate'] = df['chartdate'].apply(lambda x: f'{x.month}{"-"}{x.day}{"_"}{x.hour}{":"}{x.minute}')
    slope_cols = [i for i in df.columns if 'slope' in i]
    for col in slope_cols:
        df[col] = pd.to_numeric(df[col])
        df[col] = np.where(abs(df[col])>5, 0, df[col])
    fig.add_scatter(x=df['chartdate'], y=df['hist_slope-3'], mode="lines", row=1, col=1, name='hist_slope-3')
    fig.add_scatter(x=df['chartdate'], y=df['hist_slope-6'], mode="lines", row=1, col=1, name='hist_slope-6')
    # fig.add_scatter(x=df['chartdate'], y=df['hist_slope-23'], mode="lines", row=1, col=1, name='hist_slope-23')
    fig.add_scatter(x=df['chartdate'], y=df['macd_slope-3'], mode="lines", row=2, col=1, name='macd_slope-3')
    fig.add_scatter(x=df['chartdate'], y=df['macd_slope-6'], mode="lines", row=2, col=1, name='macd_slope-6')
    # fig.add_scatter(x=df['chartdate'], y=df['macd_slope-23'], mode="lines", row=2, col=1, name='macd_slope-23')
    fig.update_layout(height=600, width=900, title_text=title)
    return fig

def create_wave_chart(df):
    title = f'buy+sell cross __waves {df.iloc[-1]["name"]}'
    # st.markdown('<div style="text-align: center;">{}</div>'.format(title), unsafe_allow_html=True)
    fig = make_subplots(rows=1, cols=1, shared_xaxes=True, vertical_spacing=0.01)
    # df.set_index('timestamp_est')
    # df['chartdate'] = f'{df["chartdate"].day}{df["chartdate"].hour}{df["chartdate"].minute}'
    df = df.copy()
    df['chartdate'] = df['chartdate'].apply(lambda x: f'{x.month}{"-"}{x.day}{"_"}{x.hour}{":"}{x.minute}')

    fig.add_bar(x=df['chartdate'], y=df['buy_cross-0__wave'],  row=1, col=1, name='buycross wave')
    fig.add_bar(x=df['chartdate'], y=df['sell_cross-0__wave'],  row=1, col=1, name='sellcross wave')
    fig.update_layout(height=600, width=900, title_text=title)
    return fig

def create_wave_chart_single(df, wave_col):
    title = df.iloc[-1]['name']
    # st.markdown('<div style="text-align: center;">{}</div>'.format(title), unsafe_allow_html=True)
    fig = make_subplots(rows=1, cols=1, shared_xaxes=True, vertical_spacing=0.01)
    # df.set_index('timestamp_est')
    # df['chartdate'] = f'{df["chartdate"].day}{df["chartdate"].hour}{df["chartdate"].minute}'
    df = df.copy()
    df['chartdate'] = df['chartdate'].apply(lambda x: f'{x.month}{"-"}{x.day}{"_"}{x.hour}{":"}{x.minute}')

    fig.add_bar(x=df['chartdate'], y=df[wave_col],  row=1, col=1, name=wave_col)
    fig.update_layout(height=600, width=900, title_text=title)
    return fig

def create_wave_chart_all(df, wave_col):
    title = df.iloc[-1]['name']
    # st.markdown('<div style="text-align: center;">{}</div>'.format(title), unsafe_allow_html=True)
    fig = make_subplots(rows=1, cols=1, shared_xaxes=True, vertical_spacing=0.01)
    # df.set_index('timestamp_est')
    # df['chartdate'] = f'{df["chartdate"].day}{df["chartdate"].hour}{df["chartdate"].minute}'
    df = df.copy()
    # df['chartdate'] = df['chartdate'].apply(lambda x: f'{x.month}{"-"}{x.day}{"_"}{x.hour}{":"}{x.minute}')
    # df[f'{wave_col}{"_number"}'] = df[f'{wave_col}{"_number"}'].astype(str)
    # dft = df[df[f'{wave_col}{"_number"}'] == '1'].copy()
    fig.add_bar(x=df[f'{wave_col}{"_number"}'], y=df[wave_col].values,  row=1, col=1, name=wave_col)
    fig.update_layout(height=600, width=900, title_text=title)
    return fig


def return_total_profits(QUEEN):
    
    ORDERS = [i for i in QUEEN['queen_orders'] if i['queen_order_state'] == 'completed' and i['side'] == 'sell']
    c_1, c_2 = st.columns(2)
    
    if ORDERS:
        df = pd.DataFrame(ORDERS)
        tic_group_df = df.groupby(['symbol'])[['profit_loss']].sum().reset_index()
        
        with c_1:
            st.write("Total Profit Loss")
            st.write(tic_group_df)


        now_ = datetime.datetime.now()
        orders_today = [i for i in ORDERS if i['datetime'].day == now_.day and i['datetime'].month == now_.month and i['datetime'].year == now_.year]
        if orders_today:
            df = pd.DataFrame(orders_today)
            tic_group_df = df.groupby(['symbol'])[['profit_loss']].sum().reset_index()
            with c_2:
                st.write("Today Profit Loss")
                st.write(tic_group_df)


class return_pollen:
    POLLENSTORY = read_pollenstory()
    QUEENSMIND = read_queensmind(prod) # return {'bishop': bishop, 'castle': castle, 'STORY_bee': STORY_bee, 'knightsword': knightsword}
    QUEEN = QUEENSMIND['queen']
    # The story behind the story       
    STORY_bee = QUEEN['queen']['conscience']['STORY_bee']
    KNIGHTSWORD = QUEEN['queen']['conscience']['KNIGHTSWORD']
    ANGEL_bee = QUEEN['queen']['conscience']['ANGEL_bee']

# pollen = return_pollen()

st.sidebar.write("Production: ", prod)
# st.write(prod)
if prod:
    api = api
    PB_App_Pickle = os.path.join(db_root, f'{"queen"}{"_App_"}{".pkl"}')
    st.sidebar.write("""My Queen Production""")
else:
    api = api_paper
    PB_App_Pickle = os.path.join(db_root, f'{"queen"}{"_App_"}{"_sandbox"}{".pkl"}')
    st.sidebar.write("""My Queen Sandbox""")


pollen_theme = pollen_themes()
KING = KINGME()
stars = KING['stars']

QUEEN = read_queensmind(prod)['queen']
POLLENSTORY = read_pollenstory()
APP_requests = ReadPickleData(pickle_file=PB_App_Pickle)
STORY_bee = QUEEN['queen']['conscience']['STORY_bee']
KNIGHTSWORD = QUEEN['queen']['conscience']['KNIGHTSWORD']
ANGEL_bee = QUEEN['queen']['conscience']['ANGEL_bee']


option3 = st.sidebar.selectbox("Always RUN", ('No', 'Yes'))
option = st.sidebar.selectbox("Dashboards", ('queen', 'charts', 'signal'))
st.sidebar.write("<<<('')>>>")
# st.header(option)


# """ if "__name__" == "__main__": """

# full view of all stories 
# # macd_state, Macd Tier, Macd, Hist Tier, Hist, Signal Tier, Signal, & Current Wave dimensions (length, profit)story


if option == 'charts':
    # pollen = return_pollen()
    
    tickers_avail = list([set(i.split("_")[0] for i in POLLENSTORY.keys())][0])
    # tickers_avail.update({"all"})
    ticker_option = st.sidebar.selectbox("Tickers", tickers_avail, index=tickers_avail.index(["SPY" if "SPY" in tickers_avail else tickers_avail[0]][0]))
    st.markdown('<div style="text-align: center;">{}</div>'.format(ticker_option), unsafe_allow_html=True)

    ttframe_list = list(set([i.split("_")[1] + "_" + i.split("_")[2] for i in POLLENSTORY.keys()]))
    # ttframe_list.append("all")
    frame_option = st.sidebar.selectbox("ttframes", ttframe_list, index=ttframe_list.index(["1Minute_1Day" if "1Minute_1Day" in ttframe_list else ttframe_list[0]][0]))
    day_only_option = st.sidebar.selectbox('Show Today Only', ['no', 'yes'], index=['no'].index('no'))
    slope_option = st.sidebar.selectbox('Show Slopes', ['no', 'yes'], index=['no'].index('no'))
    wave_option = st.sidebar.selectbox('Show Waves', ['no', 'yes'], index=['no'].index('no'))
    
    if frame_option == 'all':
        st.write("TDB")

    else:
        selections = [i for i in POLLENSTORY.keys() if i.split("_")[0] in ticker_option and i.split("_")[1] in frame_option]
        st.write(selections[0])
        ticker_time_frame = selections[0]
        df = POLLENSTORY[ticker_time_frame].copy()
        # if df.iloc[-1]['open'] == 0:
        #     df = df.head(-1)
        if day_only_option == 'yes':
            df_day = df['timestamp_est'].iloc[-1]
            df['date'] = df['timestamp_est'] # test
            df = df.set_index('timestamp_est', drop=False) # test
            # between certian times
            # df_t = df.between_time('9:30', '12:00')
            df = df[df.index.day == df_day.day].copy() # remove yesterday       
        

        
        fig = create_main_macd_chart(df)
        st.write(fig)

        if slope_option == 'yes':
            slope_cols = [i for i in df.columns if "slope" in i]
            slope_cols.append("close")
            slope_cols.append("timestamp_est")
            slopes_df = df[['timestamp_est', 'hist_slope-3', 'hist_slope-6', 'macd_slope-3']]
            fig = create_slope_chart(df=df)
            st.write(fig)
            st.dataframe(slopes_df)
        
        if wave_option == "yes":
            fig = create_wave_chart(df=df)
            st.write(fig)
            
            dft = split_today_vs_prior(df=df)
            dft = dft['df_today']

            fig=create_wave_chart_all(df=dft, wave_col='buy_cross-0__wave')
            st.write(fig)

            st.write("current wave")
            current_buy_wave = df['buy_cross-0__wave_number'].tolist()
            current_buy_wave = [int(i) for i in current_buy_wave]
            current_buy_wave = max(current_buy_wave)
            st.write("current wave number")
            st.write(current_buy_wave)
            dft = df[df['buy_cross-0__wave_number'] == str(current_buy_wave)].copy()
            st.write({'current wave': [dft.iloc[0][['timestamp_est', 'close', 'macd']].values]})
            fig=create_wave_chart_single(df=dft, wave_col='buy_cross-0__wave')
            st.write(fig)

            # st.write("waves")
            # waves = STORY_bee[ticker_time_frame]['waves']
            # st.write(waves)
        
        if "BTCUSD" in ticker_time_frame:
            df = POLLENSTORY[ticker_time_frame].copy()
            df_output = df[['timestamp_est', 'story_index', 'close']].copy()
            df_output = df_output.sort_values(by='story_index', ascending=False)

            st.write(df_output)
        
        if option3 == "Yes":
            time.sleep(10)
            st.experimental_rerun()

if option == 'queen':
    # pollen = return_pollen()
    tickers_avail = [set(i.split("_")[0] for i in STORY_bee.keys())][0]
    tickers_avail.update({"all"})
    tickers_avail_op = list(tickers_avail)
    ticker_option = st.sidebar.selectbox("Tickers", tickers_avail_op, index=tickers_avail_op.index('SPY'))
    st.markdown('<div style="text-align: center;">{}</div>'.format(ticker_option), unsafe_allow_html=True)

    option_showaves = st.sidebar.selectbox("Show Waves", ('no', 'yes'), index=["no"].index("no"))

    return_total_profits(QUEEN=QUEEN)

    command_conscience_option = st.sidebar.selectbox("command conscience", ('yes', 'no'), index=["yes"].index("yes"))
    orders_table = st.sidebar.selectbox("orders_table", ('no', 'yes'), index=["no"].index("no"))
    today_day = datetime.datetime.now().day
    col11, col22 = st.columns(2)
    with col22:
        st.write("current errors")
    with col22:
        st.write(QUEEN["errors"])

    if command_conscience_option == 'yes':
        # all_trigs = []
        all_trigs = {k: i['story']["alltriggers_current_state"] for (k, i) in STORY_bee.items() if len(i['story']["alltriggers_current_state"]) > 0}
        # df = pd.DataFrame(all_trigs)
        df = pd.DataFrame(all_trigs.items())
        df = df.rename(columns={0: 'ttf', 1: 'trig'})
        df = df.sort_values('ttf')

        # df_1 = df[df['ttf'].lower().contians('spys')]
        st.write("<<all trigger bees>>")
        st.write(df)

        col1_a, col2_b, = st.columns(2)
        
        st.selectbox("memory timeframe", ['today', 'all'], index=['today'].index('today'))

        # QUEEN['command_conscience']['orders']['active'] = [i for i in QUEEN['queen_orders'] if i['queen_order_state'] in ['submitted', 'running', 'running_close']]
        # QUEEN['command_conscience']['orders']['submitted'] = [i for i in QUEEN['queen_orders'] if i['queen_order_state'] == 'submitted']
        # QUEEN['command_conscience']['orders']['running'] = [i for i in QUEEN['queen_orders'] if i['queen_order_state'] == 'running']

        
        ORDERS = QUEEN['queen_orders']
        ORDERS = [i for i in ORDERS if i['queen_order_state'] == 'completed']
        # queen shows only today orders
        now_ = datetime.datetime.now()
        orders_today = [i for i in ORDERS if i['datetime'].day == now_.day and i['datetime'].month == now_.month and i['datetime'].year == now_.year]
        orders_today = pd.DataFrame(orders_today)
        orders_today = orders_today.astype(str)
        st.write(orders_today)
        st.write('orders')

        new_title = '<p style="font-family:sans-serif; color:Black; font-size: 25px;">ERRORS</p>'
        st.markdown(new_title, unsafe_allow_html=True)
        error_orders = queen_orders_view(QUEEN=QUEEN, queen_order_state='error', return_all_cols=True)['df']
        st.dataframe(error_orders)

        new_title = '<p style="font-family:sans-serif; color:Black; font-size: 25px;">SUBMITTED</p>'
        st.markdown(new_title, unsafe_allow_html=True)
        submitted_orders = queen_orders_view(QUEEN=QUEEN, queen_order_state='submitted')['df']
        st.dataframe(submitted_orders)
        
        new_title = '<p style="font-family:sans-serif; color:Green; font-size: 25px;">RUNNING</p>'
        st.markdown(new_title, unsafe_allow_html=True)
        run_orders = queen_orders_view(QUEEN=QUEEN, queen_order_state='running')['df']
        st.dataframe(run_orders)

        new_title = '<p style="font-family:sans-serif; color:Green; font-size: 25px;">RUNNING CLOSE</p>'
        st.markdown(new_title, unsafe_allow_html=True)
        runclose_orders = queen_orders_view(QUEEN=QUEEN, queen_order_state='running_close')['df']
        st.dataframe(runclose_orders)

 
        with col2_b:
            new_title = '<p style="font-family:sans-serif; color:Black; font-size: 33px;">memory</p>'
            st.markdown(new_title, unsafe_allow_html=True)
        


    if orders_table == 'yes':
        main_orders_table = read_csv_db(db_root=db_root, tablename='main_orders', prod=prod)
        st.dataframe(main_orders_table)

    st.write("QUEENS Collective CONSCIENCE")
    if ticker_option != 'all':
        # q = QUEEN["queen"]["conscience"]["STORY_bee"]["SPY_1Minute_1Day"]

        # View Stars
        new_title = '<p style="font-family:sans-serif; color:Black; font-size: 33px;">Stars In Heaven</p>'
        st.markdown(new_title, unsafe_allow_html=True)        
        st.dataframe(data=story_view(STORY_bee=STORY_bee, ticker=ticker_option)['df'], width=2000) 


        # View Star and Waves
        m = {k:v for (k,v) in STORY_bee.items() if k.split("_")[0] == ticker_option}
        # m2 = {k:v for (k,v) in KNIGHTSWORD.items() if k.split("_")[0] == ticker_option}
        
        for ttframe, knowledge in m.items():
            
            st.write(ttframe)
            story_sort = knowledge['story']
            st.write(story_sort)
            
            if option_showaves.lower() == 'yes':
                st.write("buy cross waves")
                m_sort = knowledge['waves']['buy_cross-0']
                df_m_sort = pd.DataFrame(m_sort).T
                df_m_sort = df_m_sort.astype(str)
                st.dataframe(data=df_m_sort)

                st.write("sell cross waves")
                m_sort = knowledge['waves']['sell_cross-0']
                df_m_sort = pd.DataFrame(m_sort).T
                df_m_sort = df_m_sort.astype(str)
                st.dataframe(data=df_m_sort)

            # st.write("KNIGHTSWORDS")
            # st.write(m2[ttframe])
        
        # st.write(m)
        # st.write(m2)
        # df = pollenstory_resp[f'{ticker_option}{"_1Day_1Year"}']
        # df = df.tail(5)
        # st.dataframe(df)
    else:
        # st.write(STORY_bee)
        print("groups not allowed yet")
    # if ticker_option == 'all':
    #     st.write(mainstate)
    
    if option3 == "Yes":
        time.sleep(10)
        st.experimental_rerun()


if option == 'signal':
    # pollen = return_pollen()
    # PB_App_Pickle = os.path.join(db_app_root, 'queen_controls.pkl')
    save_signals = st.sidebar.selectbox('Send to Queen', ['beeaction', 'orders', 'controls'], index=['controls'].index('controls'))


    ## SHOW CURRENT THEME
    with st.sidebar:
        # with st.echo():
            # st.write("theme>>>", QUEEN['collective_conscience']['theme']['current_state'])
        st.write("theme>>>", QUEEN['queen_controls']['theme'])


    if save_signals == 'controls':
        
        # CHANGE Theme_list or any selections has to come from QUEEN
        theme_list = list(pollen_theme.keys())
        theme_option = st.selectbox('theme', theme_list, index=theme_list.index('nuetral'))
        
        save_button = st.button("Save Theme")
        if save_button:
            # updates = {'theme': theme_option,
            #            'request_time': datetime.datetime.now(),
            #            'app_requests_id' : f'{save_signals}{"_app-request_id_"}{return_timestamp_string()}{"__"}{datetime.datetime.now().microsecond}'
            # }
            
            # Set Theme
            # APP_requests = ReadPickleData(pickle_file=PB_App_Pickle)
            APP_requests['theme'] = theme_option
            APP_requests['last_app_update'] = datetime.datetime.now()
            PickleData(pickle_file=PB_App_Pickle, data_to_store=APP_requests)
            
            st.write("Controls Saved", return_timestamp_string())
            st.image(Image.open(bee_power_image), width=89)


        # Update run order
        show_errors_option = st.selectbox('show last error', ['no', 'yes'], index=['no'].index('no'))
        if show_errors_option == 'no':
            if len(QUEEN['queen_orders']) == 0:
                latest_queen_order = pd.DataFrame()
                orders_present = False
            else:
                latest_queen_order = [QUEEN['queen_orders'][-1]] # latest
                orders_present = True
        else:
            if len(QUEEN['queen_orders']) == 0:
                latest_queen_order = pd.DataFrame()
                orders_present = False
            else:
                latest_queen_order = [i for i in QUEEN['queen_orders'] if i['queen_order_state']=='error'] # latest
                latest_queen_order = [latest_queen_order[-1]]
                orders_present = True
        if orders_present:
            c_order_input = st.text_input("client_order_id", latest_queen_order[0]['client_order_id'])
            q_order = {k: i for k, i in enumerate(QUEEN['queen_orders']) if i['client_order_id'] == c_order_input}
            idx = list(q_order.keys())[0]
            latest_queen_order = [QUEEN['queen_orders'][idx]] # latest
            
            # q_order = [i for i in QUEEN['queen_orders'] if i['client_order_id'] == c_order_input]
            st.write("current queen order requests")
            data = ReadPickleData(pickle_file=PB_App_Pickle)
            st.write(data['update_queen_order'])
            
            df = pd.DataFrame(latest_queen_order)
            df = df.T.reset_index()
            df = df.astype(str)
            # for col in df.columns:
            #     df[col] = df[col].astype(str)
            df = df.rename(columns={0: 'main'})
            grid_response = build_AGgrid_df(data=df, reload_data=False)
            data = grid_response['data']
            # st.write(data)
            ttframe = data[data['index'] == 'ticker_time_frame'].copy()
            ttframe = ttframe.iloc[0]['main']
            # st.write(ttframe.iloc[0]['main'])
            selected = grid_response['selected_rows'] 
            df_sel = pd.DataFrame(selected)
            st.write(df_sel)
            if len(df_sel) > 0:
                up_values = dict(zip(df_sel['index'], df_sel['update_column']))
                up_values = {k: v for (k,v) in up_values.items() if len(v) > 0}
                update_dict = {c_order_input: up_values}
                st.session_state['update'] = update_dict
                st.session_state['ttframe_update'] = ttframe

            save_button_runorder = st.button("Save RunOrderUpdate")
            if save_button_runorder:
                # st.write(st.session_state['update'])
                update_sstate = st.session_state['update']
                update_ttframe = st.session_state['ttframe_update']
                order_dict = {'system': 'app',
                'queen_order_update_package': update_sstate,
                'app_requests_id' : f'{save_signals}{"_app-request_id_"}{return_timestamp_string()}{datetime.datetime.now().microsecond}',
                'ticker_time_frame': update_ttframe,
                }
                # st.write(order_dict)
                data = ReadPickleData(pickle_file=PB_App_Pickle)
                data['update_queen_order'].append(order_dict)
                PickleData(pickle_file=PB_App_Pickle, data_to_store=data)
                data = ReadPickleData(pickle_file=PB_App_Pickle)
                st.write(data['update_queen_order'])
                


    
    if save_signals == 'orders':
        show_app_req = st.selectbox('show app requests', ['yes', 'no'], index=['yes'].index('yes'))
        if show_app_req == 'yes':
            data = ReadPickleData(pickle_file=PB_App_Pickle)
            st.write("sell orders", data['sell_orders'])
            st.write("buy orders", data['buy_orders'])
        current_orders = QUEEN['command_conscience']['orders']
        running_orders = current_orders['running']
        
        running_portfolio = return_dfshaped_orders(running_orders)
        
        portfolio = return_alpc_portolio(api)['portfolio']
        p_view = {k: [v['qty'], v['qty_available']] for (k,v) in portfolio.items()}
        st.write(p_view)
        st.write(running_portfolio)

        position_orders = [i for i in running_orders if not i['client_order_id'].startswith("close__") ]
        closing_orders = [i for i in running_orders if i['client_order_id'].startswith("close__") ]
        c_order_ids = [i['client_order_id'] for i in position_orders]
        c_order_iddict = {i['client_order_id']: idx for idx, i in enumerate(position_orders)}
        c_order_ids.append("Select")
        c_order_id_option = st.selectbox('client_order_id', c_order_ids, index=c_order_ids.index('Select'))
        if c_order_id_option != 'Select':
            run_order = position_orders[c_order_iddict[c_order_id_option]]
            run_order_alpaca = check_order_status(api=api, client_order_id=c_order_id_option, queen_order=run_order, prod=prod)
            st.write(("pollen matches alpaca", float(run_order_alpaca['filled_qty']) == float(run_order['filled_qty']))) ## VALIDATION FOR RUN ORDERS
            st.write(run_order_alpaca)
            st.write(run_order['filled_qty'])
            sell_qty_option = st.number_input(label="Sell Qty", max_value=float(run_order['filled_qty']), value=float(run_order['filled_qty']), step=1e-4, format="%.4f")
            # sell_qty_option = st.selectbox('sell_qty', [run_order['filled_qty']])
            type_option = st.selectbox('type', ['market'], index=['market'].index('market'))                

            sell_command = st.button("Sell Order")
            if sell_command:
                st.write("yes")
                # val qty
                if sell_qty_option > 0 and sell_qty_option <= float(run_order['filled_qty']):
                    print("qty validated")
                    # process order signal
                    client_order_id = c_order_id_option
                    sellable_qty = sell_qty_option
                    
                    order_dict = {'system': 'app',
                    'request_time': datetime.datetime.now(),
                    'client_order_id': client_order_id, 'sellable_qty': sellable_qty,
                    'side': 'sell',
                    'type': type_option,
                    'app_requests_id' : f'{save_signals}{"_app-request_id_"}{return_timestamp_string()}{datetime.datetime.now().microsecond}'

                    }
                    data = ReadPickleData(pickle_file=PB_App_Pickle)
                    data['sell_orders'].append(order_dict)
                    PickleData(pickle_file=PB_App_Pickle, data_to_store=data)
                    data = ReadPickleData(pickle_file=PB_App_Pickle)
                    st.write(data['sell_orders'])
                
                if sell_qty_option < 0 and sell_qty_option >= float(run_order['filled_qty']):
                    print("qty validated")
                    # process order signal
                    client_order_id = c_order_id_option
                    sellable_qty = sell_qty_option
                    
                    order_dict = {'system': 'app',
                    'request_time': datetime.datetime.now(),
                    'client_order_id': client_order_id, 'sellable_qty': sellable_qty,
                    'side': 'sell',
                    'type': type_option,
                    'app_requests_id' : f'{save_signals}{"_app-request_id_"}{return_timestamp_string()}{datetime.datetime.now().microsecond}'

                    }
                    data = ReadPickleData(pickle_file=PB_App_Pickle)
                    data['sell_orders'].append(order_dict)
                    PickleData(pickle_file=PB_App_Pickle, data_to_store=data)
                    data = ReadPickleData(pickle_file=PB_App_Pickle)
                    st.write(data['sell_orders'])

    
    if save_signals == 'beeaction':
        st.write("beeaction")

        wave_button_sel = st.selectbox("Waves", ["buy_cross-0", "sell_cross-0"])
        initiate_waveup = st.button("Send Wave")
        # pollen = return_pollen()
        ticker_time_frame = [set(i for i in STORY_bee.keys())][0]
        ticker_time_frame = [i for i in ticker_time_frame]
        ticker_time_frame.sort()
        ticker_wave_option = st.sidebar.selectbox("Tickers", ticker_time_frame, index=ticker_time_frame.index(["SPY_1Minute_1Day" if "SPY_1Minute_1Day" in ticker_time_frame else ticker_time_frame[0]][0]))

        wave_trigger = {ticker_wave_option: [wave_button_sel]}
        data = ReadPickleData(pickle_file=PB_App_Pickle)
        st.write(data['wave_triggers'])  

        def create_app_request(var_dict):
            valid_cols = ['app_requests_id', 'ticker', 'ticker_time_frame', 'wave_trigger']
            for k,v in var_dict.items():
                if k not in v:
                    print("invalid key")
                else:
                    var_dict

        if initiate_waveup:
            order_dict = {'ticker': ticker_wave_option.split("_")[0],
            'ticker_time_frame': ticker_wave_option,
            'system': 'app',
            'wave_trigger': wave_trigger,
            'request_time': datetime.datetime.now(),
            'app_requests_id' : f'{save_signals}{"_"}{"waveup"}{"_app-request_id_"}{return_timestamp_string()}{datetime.datetime.now().microsecond}'
            }

            data = ReadPickleData(pickle_file=PB_App_Pickle)
            # st.write(data.keys())
            data['wave_triggers'].append(order_dict)
            PickleData(pickle_file=PB_App_Pickle, data_to_store=data)
            data = ReadPickleData(pickle_file=PB_App_Pickle)
            st.write(data['wave_triggers'])            


        new_title = '<p style="font-family:sans-serif; color:Black; font-size: 33px;">BUY BUY Honey to be Made</p>'
        st.markdown(new_title, unsafe_allow_html=True)
        
        quick_buy_short = st.button("FLASH BUY SQQQ")
        quick_buy_long = st.button("FLASH BUY TQQQ")
        quick_buy_BTC = st.button("FLASH BUY BTC")
        quick_buy_amt = st.selectbox("FLASH BUY $", [5000, 10000, 20000, 30000], index=[10000].index(10000))
        
        type_option = st.selectbox('type', ['market'], index=['market'].index('market'))                

        if quick_buy_short or quick_buy_long or quick_buy_BTC:
            
            if quick_buy_short:
                ticker = "SQQQ"
            elif quick_buy_long:
                ticker = "TQQQ"
            elif quick_buy_BTC:
                ticker = "BTCUSD"
            
            print("buy buy meee, sending app request")
            # get price convert to amount
            if ticker in crypto_currency_symbols:
                crypto = True
                snap = api.get_crypto_snapshot(ticker, exchange=coin_exchange)
                current_price = snap.latest_trade.price
            else:
                crypto = False
                snap = api.get_snapshot(ticker)
                current_price = snap.latest_trade.price
            
            info = api.get_account()
            total_buying_power = info.buying_power # what is the % amount you want to buy?


            validation = True # not > 50% of buying power COIN later
            
            if validation:
                print("qty validated")
                # process order signal                
                order_dict = {'ticker': ticker,
                'system': 'app',
                'trig': 'app',
                'request_time': datetime.datetime.now(),
                'wave_amo': quick_buy_amt,
                'app_seen_price': current_price,
                'side': 'buy',
                'type': type_option,
                'app_requests_id' : f'{save_signals}{"_app-request_id_"}{return_timestamp_string()}{datetime.datetime.now().microsecond}'
                }

                data = ReadPickleData(pickle_file=PB_App_Pickle)
                data['buy_orders'].append(order_dict)
                PickleData(pickle_file=PB_App_Pickle, data_to_store=data)
                data = ReadPickleData(pickle_file=PB_App_Pickle)
                st.write(data['buy_orders'])


##### END ####