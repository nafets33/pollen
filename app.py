from asyncore import poll
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
from QueenHive import ReadPickleData, pollen_themes, PickleData, return_timestamp_string, return_api_keys, read_pollenstory, read_queensmind, read_csv_db, split_today_vs_prior, check_order_status
import json

prod = False

main_root = os.getcwd()
db_root = os.path.join(main_root, 'db')
db_app_root = os.path.join(db_root, 'app')

queens_chess_piece = os.path.basename(__file__)
log_dir = dst = os.path.join(db_root, 'logs')


if os.path.exists(dst) == False:
    os.mkdir(dst)
if prod:
    log_name = f'{"log_"}{queens_chess_piece}{".log"}'
else:
    log_name = f'{"log_"}{queens_chess_piece}{"_sandbox_"}{".log"}'

log_file = os.path.join(log_dir, log_name)
if os.path.exists(log_file) == False:
    logging.basicConfig(filename=f'{"log_"}{queens_chess_piece}{".log"}',
                        filemode='a',
                        format='%(asctime)s:%(name)s:%(levelname)s: %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p',
                        level=logging.INFO)
else:
    # copy log file to log dir & del current log file
    datet = datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S_%p')
    dst_path = os.path.join(log_dir, f'{log_name}{"_"}{datet}{".log"}')
    # shutil.copy(log_file, dst_path) # only when you want to log your log files
    # os.remove(log_file)
    logging.basicConfig(filename=f'{"log_"}{queens_chess_piece}{".log"}',
                        filemode='a',
                        format='%(asctime)s:%(name)s:%(levelname)s: %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p',
                        level=logging.INFO)


# prod = True
pd.options.mode.chained_assignment = None
est = pytz.timezone("US/Eastern")
load_dotenv()
# >>> initiate db directories
system = 'windows' #mac, windows

""" Keys """
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

main_root = os.getcwd()
db_root = os.path.join(main_root, 'db')
# Client Tickers
src_root, db_dirname = os.path.split(db_root)
client_ticker_file = os.path.join(src_root, 'client_tickers.csv')
df_client = pd.read_csv(client_ticker_file, dtype=str)
client_symbols = df_client.tickers.to_list()

main_root = os.getcwd() 
db_root = os.path.join(main_root, 'db') 

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

st.write("Production: ", prod)
# st.write(prod)
if prod:
    api = api
    PB_App_main_Pickle = os.path.join(db_app_root, f'{"queen"}{"_App_"}{".pkl"}')
    """My Queen Production"""
else:
    api = api_paper
    PB_App_main_Pickle = os.path.join(db_app_root, f'{"queen"}{"_App_"}{"_sandbox"}{".pkl"}')
    """My Queen Sandbox"""


pollen_theme = pollen_themes()


st.button("ReRun")
col1, col2, col3, col4 = st.columns(4)
bee_image = os.path.join(db_root, 'bee.jpg')
image = Image.open(bee_image)
with col3:
    st.image(image, caption='Jq', width=33)

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

class return_pollen:
    POLLENSTORY = read_pollenstory()
    QUEENSMIND = read_queensmind(prod) # return {'bishop': bishop, 'castle': castle, 'STORY_bee': STORY_bee, 'knightsword': knightsword}
    QUEEN = QUEENSMIND['queen']
    # The story behind the story       
    STORY_bee = QUEEN['queen']['conscience']['STORY_bee']
    KNIGHTSWORD = QUEEN['queen']['conscience']['KNIGHTSWORD']
    ANGEL_bee = QUEEN['queen']['conscience']['ANGEL_bee']

pollen = return_pollen()

option3 = st.sidebar.selectbox("Always RUN", ('No', 'Yes'))
option = st.sidebar.selectbox("Dashboards", ('queen', 'charts', 'signal'))
# st.header(option)


# """ if "__name__" == "__main__": """

if option == 'charts':
    pollen = return_pollen()
    
    tickers_avail = [set(i.split("_")[0] for i in pollen.POLLENSTORY.keys())][0]
    tickers_avail.update({"all"})
    ticker_option = st.sidebar.selectbox("Tickers", tickers_avail)
    st.markdown('<div style="text-align: center;">{}</div>'.format(ticker_option), unsafe_allow_html=True)

    ttframe_list = list(set([i.split("_")[1] for i in pollen.POLLENSTORY.keys()]))
    ttframe_list.append("all")
    frame_option = st.sidebar.selectbox("ttframes", ttframe_list)
    day_only_option = st.sidebar.selectbox('Show Today Only', ['yes', 'no'])
    slope_option = st.sidebar.selectbox('Show Slopes', ['yes', 'no'])
    wave_option = st.sidebar.selectbox('Show Waves', ['yes', 'no'], index=['yes'].index('yes'))
    
    if frame_option == 'all':
        for ttframe, df in pollen.POLLENSTORY.items():
            selections = [i for i in pollen.POLLENSTORY.keys() if i.split("_")[0] == ticker_option]
            for ticker_time_frame in selections:
                df = pollen.POLLENSTORY[ticker_time_frame]
                # if df.iloc[-1]['open'] == 0:
                #     df = df.head(-1)
                fig = create_main_macd_chart(df)
                
                st.write(fig)


            # df_day = df['timestamp_est'].iloc[-1]
            # df['date'] = df['timestamp_est'] # test
            # df = df.set_index('timestamp_est') # test
            # # between certian times
            # df_t = df.between_time('9:30', '12:00')
            # df_t = df_t[df_t.index.day == df_day.day].copy() # remove yesterday
            # chart = create_main_macd_chart(df=df)
            # st.write(chart)

    else:
        selections = [i for i in pollen.POLLENSTORY.keys() if i.split("_")[0] in ticker_option and i.split("_")[1] in frame_option]
        ticker_time_frame = selections[0]
        df = pollen.POLLENSTORY[ticker_time_frame].copy()
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

            st.write("waves")

            waves = pollen.STORY_bee[ticker_time_frame]['waves']
            st.write(waves)
        
        if "BTCUSD" in ticker_time_frame:
            df = pollen.POLLENSTORY[ticker_time_frame].copy()
            df_output = df[['timestamp_est', 'story_index', 'close']].copy()
            df_output = df_output.sort_values(by='story_index', ascending=False)

            st.write(df_output)
        

if option == 'queen':
    pollen = return_pollen()
    tickers_avail = [set(i.split("_")[0] for i in pollen.STORY_bee.keys())][0]
    tickers_avail.update({"all"})
    ticker_option = st.sidebar.selectbox("Tickers", tickers_avail)
    st.markdown('<div style="text-align: center;">{}</div>'.format(ticker_option), unsafe_allow_html=True)

    command_conscience_option = st.sidebar.selectbox("command conscience", ('No', 'Yes'))
    orders_table = st.sidebar.selectbox("orders_table", ('No', 'Yes'))
    pollen = return_pollen()
    today_day = datetime.datetime.now().day

    if command_conscience_option == 'Yes':
        st.write("memory")
        st.selectbox("memory timeframe", ['today', 'all'], index=['today'].index('today'))
        
        # st.write(pollen.QUEEN['command_conscience']['memory'])
        ORDERS = pollen.QUEEN['command_conscience']['memory']['orders_completed']
        # queen shows only today orders
        now_ = datetime.datetime.now()
        orders_today = [i for i in ORDERS if i['datetime'].day == now_.day and i['datetime'].month == now_.month and i['datetime'].year == now_.year]
        st.write(orders_today)
        st.write('orders')
        st.write(pollen.QUEEN['command_conscience']['orders'])

    if orders_table == 'Yes':
        main_orders_table = read_csv_db(db_root=db_root, tablename='main_orders', prod=prod)
        st.dataframe(main_orders_table)

    st.write("QUEENS Collective CONSCIENCE")
    if ticker_option != 'all':
        m = {k:v for (k,v) in pollen.STORY_bee.items() if k.split("_")[0] == ticker_option}
        m2 = {k:v for (k,v) in pollen.KNIGHTSWORD.items() if k.split("_")[0] == ticker_option}
        st.write(m)
        st.write(m2)
        # df = pollenstory_resp[f'{ticker_option}{"_1Day_1Year"}']
        # df = df.tail(5)
        # st.dataframe(df)
    else:
        st.write(pollen.STORY_bee)
    # if ticker_option == 'all':
    #     st.write(mainstate)
    
    if option3 == "Yes":
        time.sleep(3)
        st.experimental_rerun()


if option == 'signal':
    pollen = return_pollen()
    # PB_App_main_Pickle = os.path.join(db_app_root, 'queen_controls.pkl')
    save_signals = st.selectbox('Send to Queen', ['orders', 'controls'], index=['Select'].index('Select'))


    ## SHOW CURRENT THEME
    with st.sidebar:
        # with st.echo():
            # st.write("theme>>>", QUEEN['collective_conscience']['theme']['current_state'])
        st.write("theme>>>", pollen.QUEEN['queen_controls']['theme'])

    
    if save_signals == 'controls':
        
        # CHANGE Theme_list or any selections has to come from QUEEN
        theme_list = list(pollen_theme.keys())
        theme_option = st.selectbox('theme', theme_list, index=theme_list.index('nuetral'))
        
        sell_command = st.button("Save Controls")
        if sell_command:
            updates = {'theme': theme_option,
                       'request_time': datetime.datetime.now(),
                       'app_requests_id' : f'{save_signals}{"_app-request_id_"}{return_timestamp_string()}{"__"}{datetime.datetime.now().microsecond}'
            }
            
            app_queen = ReadPickleData(pickle_file=PB_App_main_Pickle)
            app_queen['theme'].append(updates)
            PickleData(pickle_file=PB_App_main_Pickle, data_to_store=app_queen)
            
            # update_queen_controls(pickle_file=PB_App_main_Pickle, dict_update=updates, queen=False)
            st.write("Controls Saved", return_timestamp_string())

    if save_signals == 'orders':
        current_orders = pollen.QUEEN['command_conscience']['orders']
        running_orders = current_orders['running']
        
        position_orders = [i for i in running_orders if not i['client_order_id'].startswith("close__") ]
        closing_orders = [i for i in running_orders if i['client_order_id'].startswith("close__") ]
        c_order_ids = [i['client_order_id'] for i in position_orders]
        c_order_iddict = {i['client_order_id']: idx for idx, i in enumerate(position_orders)}
        c_order_ids.append("Select")
        c_order_id_option = st.selectbox('client_order_id', c_order_ids, index=c_order_ids.index('Select'))
        if c_order_id_option != 'Select':
            run_order = position_orders[c_order_iddict[c_order_id_option]]
            run_order_alpaca = check_order_status(api=api, client_order_id=c_order_id_option, prod=False)
            st.write(run_order_alpaca['filled_qty'] == run_order['filled_qty']) ## VALIDATION FOR RUN ORDERS
            st.write(run_order_alpaca)
            sell_qty_option = st.selectbox('sell_qty', list(run_order['filled_qty']))
            type_option = st.selectbox('type', ['market'], index=['market'].index('market'))                

            if save_signals == 'orders':
                sell_command = st.button("Sell Order")
                if sell_command:
                    st.write("yes")
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
                    data = ReadPickleData(pickle_file=PB_App_main_Pickle)
                    data['orders'].append(order_dict)
                    PickleData(pickle_file=PB_App_main_Pickle, data_to_store=data)
                    data = ReadPickleData(pickle_file=PB_App_main_Pickle)
                    st.write(data['orders'])


            
            st.write(" BUY BUY Honey to be Made")
            
            quick_buy_short = st.button("Lightning BUY SQQQ")
            quick_buy_long = st.button("Lightning BUY TQQQ")
            quick_buy_amt = st.selectbox("Lightning BUY $", [5000, 10000, 20000, 30000], index=[10000].index(10000))

            if quick_buy_short:
                print("buy ")

            buy_option = st.selectbox('BUY', ['market', 'limit'], index=['market'].index('market'))
            # quick_buy = st.button("Lightning BUY SQQQ")








