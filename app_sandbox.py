import random
from asyncore import poll
from cProfile import run
from queue import Queue
from turtle import width
import pandas as pd
# import plotly.express as px  # pip install plotly-express
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
# from scipy.stats import linregress
# from scipy import stats
# import math
import matplotlib.pyplot as plt
from plotly.subplots import make_subplots
from PIL import Image
# import mplfinance as mpf
import plotly.graph_objects as go
import base64
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode, JsCode
import json
import argparse
import _locale

_locale._getdefaultlocale = (lambda *args: ['en_US', 'UTF-8'])


scriptname = os.path.basename(__file__)
if 'sandbox' in scriptname:
    prod = False
else:
    prod = True

# def createParser():
#     parser = argparse.ArgumentParser()
#     parser.add_argument ('-qcp', default="queen")
#     parser.add_argument ('-prod', default='false')
#     return parser

if prod:
    from QueenHive import convert_to_float, createParser_App, refresh_account_info, generate_TradingModel, stars, analyze_waves, KINGME, queen_orders_view, story_view, return_alpc_portolio, return_dfshaped_orders, ReadPickleData, pollen_themes, PickleData, return_timestamp_string, return_api_keys, read_pollenstory, read_queensmind, split_today_vs_prior, check_order_status
else:
    from QueenHive_sandbox import convert_to_float, createParser_App, refresh_account_info, generate_TradingModel, stars, analyze_waves, KINGME, queen_orders_view, story_view, return_alpc_portolio, return_dfshaped_orders, ReadPickleData, pollen_themes, PickleData, return_timestamp_string, return_api_keys, read_pollenstory, read_queensmind, split_today_vs_prior, check_order_status

# ###### GLOBAL # ######
ARCHIVE_queenorder = 'archived_bee'
active_order_state_list = ['running', 'running_close', 'submitted', 'error', 'pending', 'completed', 'running_open']
active_queen_order_states = ['submitted', 'accetped', 'pending', 'running', 'running_close', 'running_open']
closing_queen_orders = ['running_close', 'completed']
RUNNING_Orders = ['running', 'running_close', 'running_open']

# crypto
crypto_currency_symbols = ['BTCUSD', 'ETHUSD', 'BTC/USD', 'ETH/USD']
coin_exchange = "CBSE"

parser = createParser_App(prod)
namespace = parser.parse_args()
admin = [True if namespace.admin == 'true' else False][0]

# /home/stapinski89/pollen/pollen/db

main_root = os.getcwd()
db_root = os.path.join(main_root, 'db')
# db_root = '/home/stapinski89/pollen/pollen/db/' # linix
# db_app_root = os.path.join(db_root, 'app')
jpg_root = os.path.join(main_root, 'misc')

bee_image = os.path.join(jpg_root, 'bee.jpg')
image = Image.open(bee_image)
st.set_page_config(
     page_title="pollenq",
     page_icon=image,
     layout="wide",
     initial_sidebar_state="expanded",
    #  Theme='Light'
    #  menu_items={
    #      'Get Help': 'https://www.extremelycoolapp.com/help',
    #      'Report a bug': "https://www.extremelycoolapp.com/bug",
    #      'About': "# This is a header. This is an *extremely* cool app!"
    #  }
 )
col1, col2, col3, col4 = st.columns(4)
# col1_sb, col2_sb = st.sidebar.columns(2)
# with col1_sb:
st.sidebar.button("ReRun")
# with col2_sb:
# st.sidebar.image(image, caption='pollenq', width=89)
with col4:
    st.image(image, caption='pollenq', width=54)

bee_power_image = os.path.join(jpg_root, 'power.jpg')
# with col4:
#     st.image(Image.open(bee_image), width=89)

queens_chess_piece = os.path.basename(__file__)
log_dir = dst = os.path.join(db_root, 'logs')

# host buttons in dictinory!!!
# d = ['a', 'b', 'c']
# d2 = {i: st.button(i, key=i) for i in d}
# if d2['a']:
#     st.write('kewl')

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
# client_ticker_file = os.path.join(src_root, 'client_tickers.csv')
# df_client = pd.read_csv(client_ticker_file, dtype=str)
# client_symbols = df_client.tickers.to_list()
crypto_currency_symbols = ['BTCUSD', 'ETHUSD']
coin_exchange = "CBSE"


today_day = datetime.datetime.now(est).day

acct_info = refresh_account_info(api=api)
# st.write(acct_info)

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
  

def create_main_macd_chart(df):
    title = df.iloc[-1]['name']
    # st.markdown('<div style="text-align: center;">{}</div>'.format(title), unsafe_allow_html=True)
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.1999, row_heights=[0.7, 0.3])
    # df.set_index('timestamp_est')
    # df['chartdate'] = f'{df["chartdate"].day}{df["chartdate"].hour}{df["chartdate"].minute}'
    df=df.copy()
    df['chartdate'] = df['chartdate'].apply(lambda x: f'{x.month}{"-"}{x.day}{"_"}{x.hour}{":"}{x.minute}')
    fig.add_ohlc(x=df['chartdate'], close=df['close'], open=df['open'], low=df['low'], high=df['high'], name='price')
    # fig.add_scatter(x=df['chartdate'], y=df['close'], mode="lines", row=1, col=1)
    # if '1Minute_1Day' in df.iloc[0]['name']:
    fig.add_scatter(x=df['chartdate'], y=df['vwap'], mode="lines", row=1, col=1, name='vwap')

    fig.add_scatter(x=df['chartdate'], y=df['macd'], mode="lines", row=2, col=1, name='mac')
    fig.add_scatter(x=df['chartdate'], y=df['signal'], mode="lines", row=2, col=1, name='signal')
    fig.add_bar(x=df['chartdate'], y=df['hist'], row=2, col=1, name='hist')
    fig.update_layout(height=600, width=1500, title_text=title)
    df['cross'] = np.where(df['macd_cross'].str.contains('cross'), df['macd'], 0)
    fig.add_scatter(x=df['chartdate'], y=df['cross'], mode='lines', row=2, col=1, name='cross',) # line_color='#00CC96')
    # fig.add_scatter(x=df['chartdate'], y=df['cross'], mode='markers', row=1, col=1, name='cross',) # line_color='#00CC96')

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
    
    df = QUEEN['queen_orders']
    ORDERS = df[(df['queen_order_state']== 'completed') & (df['side'] == 'sell')].copy()
    return_dict = {}
    if len(ORDERS) > 0:

        tic_group_df = df.groupby(['symbol'])[['profit_loss']].sum().reset_index()
        return_dict['TotalProfitLoss'] = tic_group_df
        
        # st.write("Total Profit Loss")
        mark_down_text(fontsize='25', text="Total Profit Loss")
        # page_line_seperator()
        st.write(tic_group_df)


        now_ = datetime.datetime.now(est)
        orders_today = df[df['datetime'] > now_.replace(hour=1, minute=1, second=1)].copy()
        
        if len(orders_today) > 0:
            df = orders_today
            tic_group_df = df.groupby(['symbol'])[['profit_loss']].sum().reset_index()
            st.write("Today Profit Loss")
            st.write(tic_group_df)
            # submitted = st.form_submit_button("Save")
    
    return return_dict


def return_buying_power(api):
    ac_info = refresh_account_info(api=api)['info_converted']
    num_text = "Total Buying Power: " + '${:,.2f}'.format(ac_info['buying_power'])
    mark_down_text(fontsize='18', text=num_text)
    # st.write(":heavy_minus_sign:" * 34)

    num_text = "last_equity: " + '${:,.2f}'.format(ac_info['last_equity'])
    mark_down_text(fontsize='15', text=num_text)

    num_text = "portfolio_value: " + '${:,.2f}'.format(ac_info['portfolio_value'])
    mark_down_text(fontsize='15', text=num_text)

    num_text = "Cash: " + '${:,.2f}'.format(ac_info['cash'])
    mark_down_text(fontsize='15', text=num_text)
    
    num_text = "Total Fees: " + '${:,.2f}'.format(ac_info['accrued_fees'])
    mark_down_text(fontsize='10', text=num_text)
    # with st.expander('acctInfo details'):
    #     st.write(refresh_account_info(api=api)['info_converted'])


def pollenstory_view(POLLENSTORY):
    option_ticker = st.selectbox("ticker", ('queen', 'charts', 'signal', 'pollenstory'))

    return True



def stop_queenbee(APP_requests, key='1'):
    with st.form("stop_queen"):
        checkbox_val = st.checkbox("Stop Queen")

        # Every form must have a submit button.
        submitted = st.form_submit_button("Submit")
        if submitted:
            ("checkbox", checkbox_val)
            APP_requests['stop_queen'] = str(checkbox_val).lower()
            PickleData(pickle_file=PB_App_Pickle, data_to_store=APP_requests)
            
            test = ReadPickleData(PB_App_Pickle)
            st.write(test['stop_queen'])
    return True


def refresh_queenbee_controls(APP_requests):
    with st.form("refresh QUEEN controls"):
        checkbox_val = st.checkbox("refresh QUEEN controls")

        # Every form must have a submit button.
        submitted = st.form_submit_button("Submit")
        if submitted:
            ("checkbox", checkbox_val)
            
            APP_requests['queen_controls_reset'] = str(checkbox_val).lower()
            
            # app_request_package = create_AppRequest_package(request_name='queen_controls_reset', archive_bucket='misc_bucket')
            # app_request_package['control_name'] = control_option
            # control_upate = {'control_update' : dict(zip(df_sel['star'], df_sel['Update_Value_update']))}
            # app_request_package.update(control_upate)
            # Save
            # st.write(app_request_package)
            # APP_requests['queen_controls_reset'].append(app_request_package)
            # APP_requests['queen_controls_lastupdate'] = datetime.datetime.now().astimezone(est)
            # PickleData(pickle_file=PB_App_Pickle, data_to_store=APP_requests)
            
            PickleData(pickle_file=PB_App_Pickle, data_to_store=APP_requests)
            
    return True


def return_image_upon_save():
    st.write("Controls Saved", return_timestamp_string())
    st.image(Image.open(bee_power_image), width=89)


def update_QueenControls(APP_requests, control_option, theme_list):
    if control_option.lower() == 'theme':
        with st.form("Update Control"):

            if control_option.lower() == 'theme':
                theme_option = st.selectbox('Select theme', theme_list, index=theme_list.index('nuetral'))
            
            save_button = st.form_submit_button("Submit")
            if save_button:
                APP_requests['theme'] = theme_option
                APP_requests['last_app_update'] = datetime.datetime.now()
                PickleData(pickle_file=PB_App_Pickle, data_to_store=APP_requests)
                return_image_upon_save()
        return True

    elif control_option.lower() == 'max_profit_wavedeviation':
        st.write("active")
        df = pd.DataFrame(QUEEN['queen_controls']['max_profit_waveDeviation'].items()).astype(str)
        df = df.rename(columns={0: 'star', 1: 'Sell At Devation'})
        grid_response = build_AGgrid_df(data=df, reload_data=False, height=250, update_cols=['Update_Value'], paginationOn=False)
        data = grid_response['data']
        selected = grid_response['selected_rows'] 
        df_sel = pd.DataFrame(selected)
        st.write(df_sel)
        save_waveD = st.button('Save')
        if save_waveD:
            # Create
            app_request_package = create_AppRequest_package(request_name=control_option, archive_bucket='queen_contorls_requests')
            app_request_package['control_name'] = control_option
            control_upate = {'control_update' : dict(zip(df_sel['star'], df_sel['Update_Value_update']))}
            app_request_package.update(control_upate)
            # Save
            st.write(app_request_package)
            APP_requests['queen_controls'].append(app_request_package)
            APP_requests['queen_controls_lastupdate'] = datetime.datetime.now().astimezone(est)
            PickleData(pickle_file=PB_App_Pickle, data_to_store=APP_requests)
            return_image_upon_save()

    elif control_option.lower() == 'power_rangers':
        st.write("active")
        # power rangers
        theme_token = st.selectbox('Power Rangers Theme', theme_list, index=theme_list.index('nuetral'))
        queens_power_rangers = QUEEN['queen_controls']['power_rangers']
        powerRangers = list(queens_power_rangers.keys())
        star = st.selectbox('Power Rangers', powerRangers, index=powerRangers.index(["1Minute_1Day" if "1Minute_1Day" in powerRangers else powerRangers[0]][0]))
        ranger_waves_types = list(queens_power_rangers[star].keys())
        ranger_waves = list(queens_power_rangers[star]['mac'].keys())

        wave_type = st.selectbox('Wave_Type', ranger_waves_types, index=ranger_waves_types.index(["mac" if "mac" in ranger_waves_types else ranger_waves_types[0]][0]))
        wave_ = st.selectbox('Wave', ranger_waves, index=ranger_waves.index(["buy_wave" if "buy_wave" in ranger_waves else ranger_waves[0]][0]))


        st.write(wave_)
        ranger_settings = queens_power_rangers[star][wave_type][wave_][theme_token]
        df_i = pd.DataFrame(ranger_settings.items())
        df = df_i.rename(columns={0: 'PowerRanger', 1: theme_token}) 

        
        grid_response = build_AGgrid_df(data=df, reload_data=False, height=333, update_cols=['UpdateRangerTheme'])
        data = grid_response['data']
        selected = grid_response['selected_rows'] 
        df_sel = pd.DataFrame(selected)
        st.write(df_sel)
        
        save_wavePRanger = st.button('Save')
        if save_wavePRanger:
            # Create
            app_request_package = create_AppRequest_package(request_name=control_option, archive_bucket='queen_contorls_requests')
            app_request_package['star'] = star
            app_request_package['wave_type'] = wave_type
            app_request_package['wave_'] = wave_
            app_request_package['theme_token'] = theme_token
            app_request_package['rangers_values'] = dict(zip(df_sel['PowerRanger'], df_sel['UpdateRangerTheme_update']))

            # ranger_wave_update = {star: {wave_: { theme_token: update_values } }}  ### UPDATER HERE

            # control_upate = {'control_update' : ranger_wave_update}
            # app_request_package.update(control_upate)
     
            # Save
            st.write(app_request_package)
            APP_requests['power_rangers'].append(app_request_package)
            APP_requests['power_rangers_lastupdate'] = datetime.datetime.now().astimezone(est)
            PickleData(pickle_file=PB_App_Pickle, data_to_store=APP_requests)
            return_image_upon_save()

            return True


        return True

    elif control_option.lower() == 'symbols_stars_tradingmodel':
        st.write("Current Model")
        # st.write(QUEEN['queen_controls'][control_option])
        tickers_avail = list(QUEEN['queen_controls'][control_option].keys())
        ticker_option_qc = st.selectbox("Select Tickers", tickers_avail, index=tickers_avail.index(["SPY" if "SPY" in tickers_avail else tickers_avail[0]][0]))
        star_avail = list(QUEEN['queen_controls'][control_option][ticker_option_qc]['stars_kings_order_rules'].keys())
        star_option_qc = st.selectbox("Select Star", star_avail, index=star_avail.index(["1Minute_1Day" if "1Minute_1Day" in star_avail else star_avail[0]][0]))
        # Trading Model
        trading_model = QUEEN['queen_controls'][control_option][ticker_option_qc]
        trigbee_sel = st.selectbox("trigbees", list(trading_model['trigbees'].keys()))
        trading_model__star = trading_model['stars_kings_order_rules'][star_option_qc]
        # Waves change to ref tradin model
        wave_blocks_option = st.selectbox("block time", KING['waveBlocktimes'])

        # st.write('QUEEN Ticker STAR model', trading_model__star.keys())
    
        # st.write('delme', trading_model__star['trigbees'].keys())

        
        tic_options_mapping = {
        # 'QueenBeeTrader', 'trigbees': 'checkbox',
        'status': 'checkbox',
        'total_budget': 'number',
        'buyingpower_allocation_LongTerm':  'number', 'buyingpower_allocation_ShortTerm': 'number',
        'index_long_X': 'text', 'index_inverse_X': 'text', 
        'portforlio_weight_ask':  'number', 
        'max_single_trade_amount':  'number', 'allow_for_margin': 'checkbox', 
        'buy_ONLY_by_accept_from_QueenBeeTrader': 'checkbox', 
        'trading_model_name': 'text', 'portfolio_name': 'text', 
        'premarket': 'checkbox', 'afterhours': 'checkbox', 'morning_9-11': 'checkbox', 'lunch_11-2':'checkbox', 'afternoon_2-4': 'checkbox', 'Day': 'checkbox'}

        star_trigbee_mapping = {
            'status': 'checkbox',
        }
            
        kor_option_mapping = {
        'status': 'checkbox',
        'trade_using_limits': 'checkbox',
        'doubledown_timeduration': 'number',
        'max_profit_waveDeviation': 'number',
        'max_profit_waveDeviation_timeduration': 'number',
        'timeduration': 'number',
        'take_profit': 'number',
        'sellout': 'number',
        'sell_trigbee_trigger': 'checkbox',
        'stagger_profits': 'checkbox',
        'scalp_profits': 'checkbox',
        'scalp_profits_timeduration': 'number',
        'stagger_profits_tiers': 'number',
        'limitprice_decay_timeduration': 'number'}




        
        with st.form('trading model form'):
            ticker_update = {}
            star_settings_upadte = {}
            star__items = {}

            trigbee_update = trading_model__star['trigbees'][trigbee_sel]
            king_order_rules_update = trading_model__star['trigbees'][trigbee_sel][wave_blocks_option]

            with st.expander('Ticker Settings'):
                st.write('tic level', QUEEN['queen_controls'][control_option][ticker_option_qc].keys())

                mark_down_text(text='Ticker Settings')
                # power rangers
                for k,v in trading_model['power_rangers'].items():
                    star__items[k] = st.checkbox(label=k, value=v, key=f'{"tic_level1"}{k}{v}')
                # all ticker settings
                for kor_option, kor_v in trading_model.items():
                    if kor_option in tic_options_mapping.keys():
                        st_func = tic_options_mapping[kor_option]
                        if st_func == 'checkbox':
                            ticker_update[kor_option] = st.checkbox(label=f'{ticker_option_qc}{"_"}{kor_option}', value=kor_v, key=f'{ticker_option_qc}{"_"}{kor_option}')
                        elif st_func == 'number':
                            ticker_update[kor_option] = st.number_input(label=f'{ticker_option_qc}{"_"}{kor_option}', value=kor_v, key=f'{ticker_option_qc}{"_"}{kor_option}')
                        elif st_func == 'text':
                            ticker_update[kor_option] = st.text_input(label=f'{ticker_option_qc}{"_"}{kor_option}', value=kor_v, key=f'{ticker_option_qc}{"_"}{kor_option}')
                    else:
                        st.write("missing ", kor_option)
                        # ticker_update[kor_option] = kor_v
                
            with st.expander('Star Settings'):
                st.write(QUEEN['queen_controls'][control_option][ticker_option_qc]['stars_kings_order_rules'][star_option_qc].keys())

                mark_down_text(text=f'{star_option_qc}{" Star Settings"}') 
                control_status = st.selectbox("Ticker Active", ['active', 'not_active'], index=['active', 'not_active'].index(trading_model__star['status']))
                total_budget = st.number_input(label='total_budget', value=float(trading_model__star['total_budget']))
                trade_using_limits = st.checkbox("trade_using_limits", value=trading_model__star['trade_using_limits'])
                buyingpower_allocation_LongTerm = st.number_input(label='buyingpower_allocation_LongTerm', value=trading_model__star['buyingpower_allocation_LongTerm'])
                buyingpower_allocation_ShortTerm = st.number_input(label='buyingpower_allocation_ShortTerm', value=trading_model__star['buyingpower_allocation_ShortTerm'])

                st.write("active stars")
                active_stars = {}
                for k,v in trading_model__star['power_rangers'].items():
                    active_stars[k] = st.checkbox(label=f'{k}', value=v, key=f'{"star_level2"}{k}{v}')

            with st.expander(f'{"Star Trigbee Settings: "}{trigbee_sel}'):
                
                mark_down_text(text=f'{trigbee_sel}')
                for kor_option, kor_v in trigbee_update.items():
                    if kor_option in star_trigbee_mapping.keys():
                        st_func = star_trigbee_mapping[kor_option]
                        if st_func == 'checckbox':
                            trigbee_update[kor_option] = st.checkbox(label=f'{trigbee_sel}{"_"}{kor_option}', value=kor_v, key=f'{trigbee_sel}{"_"}{kor_option}')
                        elif st_func == 'number':
                            trigbee_update[kor_option] = st.number_input(label=f'{trigbee_sel}{"_"}{kor_option}', value=kor_v, key=f'{trigbee_sel}{"_"}{kor_option}')
                        elif st_func == 'text':
                            trigbee_update[kor_option] = st.text_input(label=f'{trigbee_sel}{"_"}{kor_option}', value=kor_v, key=f'{trigbee_sel}{"_"}{kor_option}')
                    else:
                        print('missing')
                        st.write("missing ", kor_option)
                        # trigbee_update[kor_option] = kor_v

            with st.expander(f'{"StarTrigbee WaveBlocktime KingOrderRules "}{trigbee_sel}{" >>> "}{wave_blocks_option}'):
                mark_down_text(text=f'{trigbee_sel}{" >>> "}{wave_blocks_option}')
                for kor_option, kor_v in king_order_rules_update.items():
                    if kor_option in kor_option_mapping.keys():
                        st_func = kor_option_mapping[kor_option]
                        if st_func == 'checckbox':
                            king_order_rules_update[kor_option] = st.checkbox(label=f'{trigbee_sel}{"_"}{wave_blocks_option}{"_"}{kor_option}', value=kor_v, key=f'{trigbee_sel}{"_"}{wave_blocks_option}{"_"}{kor_option}')
                        elif st_func == 'number':
                            king_order_rules_update[kor_option] = st.number_input(label=f'{trigbee_sel}{"_"}{wave_blocks_option}{"_"}{kor_option}', value=kor_v, key=f'{trigbee_sel}{"_"}{wave_blocks_option}{"_"}{kor_option}')
                        elif st_func == 'text':
                            king_order_rules_update[kor_option] = st.text_input(label=f'{trigbee_sel}{"_"}{wave_blocks_option}{"_"}{kor_option}', value=kor_v, key=f'{trigbee_sel}{"_"}{wave_blocks_option}{"_"}{kor_option}')
                    else:
                        print('missing')
                        st.write("missing ", kor_option)
                        king_order_rules_update[kor_option] = kor_v


            # Create App Package
            save_button_addranger = st.form_submit_button("update active star rangers")
            if save_button_addranger:
                app_req = create_AppRequest_package(request_name='trading_models',  archive_bucket='trading_models_requests')
                # Ticker Level 1
                trading_model.update(ticker_update)

                trading_model['status'] = control_status
                trading_model['trade_using_limits'] = trade_using_limits
                trading_model['buyingpower_allocation_LongTerm'] = buyingpower_allocation_LongTerm
                trading_model['buyingpower_allocation_ShortTerm'] = buyingpower_allocation_ShortTerm
                trading_model['total_budget'] = total_budget
                trading_model['power_rangers'] = {k: v for (k,v) in active_stars.items()}

                # Star Level 2
                trading_model['stars_kings_order_rules'][star_option_qc].update(ticker_update)
                
                # Trigbees Level 3
                trading_model['stars_kings_order_rules'][star_option_qc]['trigbees'][trigbee_sel].update(trigbee_update)
                
                # WaveBlock Time Levle 4
                trading_model['stars_kings_order_rules'][star_option_qc]['trigbees'][trigbee_sel][wave_blocks_option].update(king_order_rules_update)


                # st.write(trading_model__star)
                # app_req['trading_model__star'] = trading_model__star
                # APP_requests['trading_models'].append(app_req)
                # PickleData(pickle_file=PB_App_Pickle, data_to_store=APP_requests)
        
                # # Save
                # st.write(app_request_package)
                # APP_requests['power_rangers'].append(app_request_package)
                # APP_requests['power_rangers_lastupdate'] = datetime.datetime.now().astimezone(est)
                # PickleData(pickle_file=PB_App_Pickle, data_to_store=APP_requests)
                return_image_upon_save()
        
    else:
        st.write("PENDING WORK")
        st.write(QUEEN['queen_controls'][control_option])


def queen_order_update():
    with st.form("my_form"):
        df = pd.DataFrame(latest_queen_order)
        df = df.T.reset_index()
        df = df.astype(str)
        # for col in df.columns:
        #     df[col] = df[col].astype(str)
        df = df.rename(columns={0: 'main'})
        grid_response = build_AGgrid_df(data=df, reload_data=False, update_cols=['update_column'])
        data = grid_response['data']
        # st.write(data)
        ttframe = data[data['index'] == 'ticker_time_frame'].copy()
        ttframe = ttframe.iloc[0]['main']
        # st.write(ttframe.iloc[0]['main'])
        selected = grid_response['selected_rows'] 
        df_sel = pd.DataFrame(selected)
        st.write(df_sel)
        if len(df_sel) > 0:
            up_values = dict(zip(df_sel['index'], df_sel['update_column_update']))
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


def create_AppRequest_package(request_name, archive_bucket):
    return {
    'app_requests_id': f'{request_name}{"_app-request_id_"}{return_timestamp_string()}{datetime.datetime.now().microsecond}', 
    'request_name': request_name,
    'archive_bucket': archive_bucket,
    'request_timestamp': datetime.datetime.now().astimezone(est),
    }


def aggrid_build(df, js_code_cols=False, js_code=False, enable_enterprise_modules=False, fit_columns_on_grid_load=False, update_mode_value=False, return_mode_value=False, grid_height=False, enable_sidebar=False, enable_selection=False, selection_mode='multiple', use_checkbox=False, enable_pagination=False, paginationAutoSize=False, paginationPageSize=False):
    #configures last row to use custom styles based on cell's value, injecting JsCode on components front end
    #Infer basic colDefs from dataframe types
    gb = GridOptionsBuilder.from_dataframe(df)

    #customize gridOptions
    gb.configure_default_column(groupable=True, value=True, enableRowGroup=True, aggFunc='sum', editable=True)
    # gb.configure_column("date_only", type=["dateColumnFilter","customDateTimeFormat"], custom_format_string='yyyy-MM-dd', pivot=True)
    # gb.configure_column("date_tz_aware", type=["dateColumnFilter","customDateTimeFormat"], custom_format_string='yyyy-MM-dd HH:mm zzz', pivot=True)

    # gb.configure_column("apple", type=["numericColumn","numberColumnFilter","customNumericFormat"], precision=2, aggFunc='sum')
    # gb.configure_column("banana", type=["numericColumn", "numberColumnFilter", "customNumericFormat"], precision=1, aggFunc='avg')
    # gb.configure_column("chocolate", type=["numericColumn", "numberColumnFilter", "customCurrencyFormat"], custom_currency_symbol="R$", aggFunc='max')
    if js_code:
        js_code =  """ {'mac_ranger':
        function(params) {
            if (params.value == 'white') {
                return {
                    'color': 'white',
                    'backgroundColor': 'darkred'
                }
            } else {
                return {
                    'color': 'black',
                    'backgroundColor': 'white'
                }
            }
        };
        """
        for col in js_code_cols:
            # cellsytle_jscode = JsCode(js_code[col])
            cellsytle_jscode = JsCode(js_code)
            gb.configure_column(col, cellStyle=cellsytle_jscode)

    if enable_sidebar:
        gb.configure_side_bar()

    if enable_selection:
        st.sidebar.subheader("Selection options")
        # selection_mode = st.sidebar.radio("Selection Mode", ['single','multiple'], index=1)
        
        if use_checkbox:
            groupSelectsChildren = st.sidebar.checkbox("Group checkbox select children", value=True)
            groupSelectsFiltered = st.sidebar.checkbox("Group checkbox includes filtered", value=True)

        if ((selection_mode == 'multiple') & (not use_checkbox)):
            rowMultiSelectWithClick = st.sidebar.checkbox("Multiselect with click (instead of holding CTRL)", value=False)
            if not rowMultiSelectWithClick:
                suppressRowDeselection = st.sidebar.checkbox("Suppress deselection (while holding CTRL)", value=False)
            else:
                suppressRowDeselection=False
        # 
        gb.configure_selection(selection_mode)
        if use_checkbox:
            gb.configure_selection(selection_mode, use_checkbox=True, groupSelectsChildren=groupSelectsChildren, groupSelectsFiltered=groupSelectsFiltered)
        if ((selection_mode == 'multiple') & (not use_checkbox)):
            gb.configure_selection(selection_mode, use_checkbox=False, rowMultiSelectWithClick=rowMultiSelectWithClick, suppressRowDeselection=suppressRowDeselection)

    if enable_pagination:
        if paginationAutoSize:
            gb.configure_pagination(paginationAutoPageSize=True)
        else:
            gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=paginationPageSize)

    gb.configure_grid_options(domLayout='normal')
    gridOptions = gb.build()

    #Display the grid
    st.header("Streamlit Ag-Grid")
    st.markdown("""
        AgGrid can handle many types of columns and will try to render the most human readable way.  
        On editions, grid will fallback to string representation of data, DateTime and TimeDeltas are converted to ISO format.
        Custom display formating may be applied to numeric fields, but returned data will still be numeric.
    """)

    grid_response = AgGrid(
        df, 
        gridOptions=gridOptions,
        height=grid_height, 
        width='100%',
        data_return_mode=return_mode_value, 
        update_mode=update_mode_value,
        fit_columns_on_grid_load=fit_columns_on_grid_load,
        allow_unsafe_jscode=True, #Set it to True to allow jsfunction to be injected
        enable_enterprise_modules=enable_enterprise_modules
        )

    df = grid_response['data']
    selected = grid_response['selected_rows']
    # selected_df = pd.DataFrame(selected).apply(pd.to_numeric, errors='coerce')

    return True

def build_AGgrid_df(data, reload_data=False, fit_columns_on_grid_load=True, height=750, update_cols=['Update'], update_mode_value='MANUAL', paginationOn=True, dropdownlst=False, allow_unsafe_jscode=True):
    gb = GridOptionsBuilder.from_dataframe(data, min_column_width=30)
    if paginationOn:
        gb.configure_pagination(paginationAutoPageSize=True) #Add pagination
    gb.configure_side_bar() #Add a sidebar
    gb.configure_selection('multiple', use_checkbox=True, groupSelectsChildren="Group checkbox select children") #Enable multi-row selection
    if update_cols:
        for colName in update_cols:        
            if dropdownlst:
                gb.configure_column(f'{colName}{"_update"}', editable=True, cellEditor='agSelectCellEditor', cellEditorParams={'values': dropdownlst })
            else:
                gb.configure_column(f'{colName}{"_update"}', header_name=colName, editable=True, groupable=True)

    jscode = JsCode("""
    function(params) {
        if (params.data.state === 'white') {
            return {
                'color': 'white',
                'backgroundColor': 'red'
            }
        }
    };
    """)
    
    gridOptions = gb.build()
    
    gridOptions['getRowStyle'] = jscode
    gridOptions['rememberGroupStateWhenNewData'] = 'true'
    gridOptions['enableCellTextSelection'] = 'true'

    grid_response = AgGrid(
        data,
        gridOptions=gridOptions,
        data_return_mode='AS_INPUT', 
        update_mode=update_mode_value, 
        fit_columns_on_grid_load=fit_columns_on_grid_load,
        # theme='blue', #Add theme color to the table
        enable_enterprise_modules=True,
        height=height, 
        # width='100%',
        reload_data=reload_data,
        allow_unsafe_jscode=allow_unsafe_jscode
    )
    return grid_response


def ag_grid_main_build(df, default=False, add_vars=False, write_selection=True):
    if default:
        vars = {'reload_data': False, 'height': 333, 'update_cols': ['Comment'], 
        'update_mode_value': 'MANUAL', 'paginationOn': True}
    if add_vars:
        for k, v in add_vars.items():
            vars[k] = v

    # if 'mac_ranger' in df.columns:
    #     cellsytle_jscode = JsCode("""
    #     function(params) {
    #         if (params.data.state === 'white') {
    #             return {
    #                 'color': 'white',
    #                 'backgroundColor': 'red'
    #             }
    #         }
    #     };
    #     """)
    #     gb = GridOptionsBuilder.from_dataframe(df)

    #     gb.configure_grid_options(domLayout='normal')
    #     gridOptions = gb.build()
    #     gridOptions['getRowStyle'] = cellsytle_jscode
    #     gridOptions['rememberGroupStateWhenNewData'] = 'true'
    #     gb.configure_column("mac_ranger", cellStyle=cellsytle_jscode)
    
    grid_response = build_AGgrid_df(data=df, 
    reload_data=vars['reload_data'],
    # gridOptions=gridOptions,
     height=vars['height'], update_cols=vars['update_cols'], 
     update_mode_value=vars['update_mode_value'], 
     paginationOn=vars['paginationOn'],
     allow_unsafe_jscode=True)
    
    data = grid_response['data']
    if write_selection:
        selected = grid_response['selected_rows'] 
        df_sel = pd.DataFrame(selected)
        st.write(df_sel)
        return df_sel


def build_AGgrid_df__queenorders(data, reload_data=False, fit_columns_on_grid_load=False, height=200, update_cols=['Update'], update_mode_value='MANUAL', paginationOn=True, dropdownlst=False, allow_unsafe_jscode=True):
    gb = GridOptionsBuilder.from_dataframe(data, min_column_width=30)
    if paginationOn:
        gb.configure_pagination(paginationAutoPageSize=True) #Add pagination
    gb.configure_side_bar() #Add a sidebar
    gb.configure_selection('multiple', use_checkbox=True, groupSelectsChildren="Group checkbox select children") #Enable multi-row selection
    if update_cols:
        for colName in update_cols:        
            if dropdownlst:
                gb.configure_column(f'{colName}{"_update"}', editable=True, cellEditor='agSelectCellEditor', cellEditorParams={'values': dropdownlst })
            else:
                gb.configure_column(f'{colName}{"_update"}', header_name=colName, editable=True, groupable=True)

    jscode = JsCode("""
    function(params) {
        if (params.data.state === 'white') {
            return {
                'color': 'white',
                'backgroundColor': 'red'
            }
        }
    };
    """)
    
    gridOptions = gb.build()
    
    gridOptions['getRowStyle'] = jscode
    gridOptions['rememberGroupStateWhenNewData'] = 'true'
    gridOptions['enableCellTextSelection'] = 'true'

    grid_response = AgGrid(
        data,
        gridOptions=gridOptions,
        data_return_mode='AS_INPUT', 
        update_mode=update_mode_value, 
        fit_columns_on_grid_load=fit_columns_on_grid_load,
        # theme='blue', #Add theme color to the table
        enable_enterprise_modules=True,
        height=height, 
        # width='100%',
        reload_data=reload_data,
        allow_unsafe_jscode=allow_unsafe_jscode
    )
    return grid_response


def add_trading_model(QUEEN, ticker, trading_model_universe):
    trading_models = QUEEN['queen_controls']['symbols_stars_TradingModel']
    if ticker not in trading_models.keys():
        print("Ticker Missing Trading Model Adding Default Model1")
        tradingmodel1 = generate_TradingModel(ticker=ticker)['tradingmodel1']
        st.write(tradingmodel1)
        app_req = create_AppRequest_package(request_name='add_trading_model', archive_bucket='add_trading_model_requests')
        # QUEEN['queen_controls']['symbols_stars_TradingModel'].update(tradingmodel1)


def its_morphin_time_view(QUEEN, STORY_bee, ticker):

    now_time = datetime.datetime.now().astimezone(est)
    POLLENSTORY = read_pollenstory()
    active_ttf = QUEEN['heartbeat']['available_tickers'] = [i for (i, v) in STORY_bee.items() if (now_time - v['story']['time_state']).seconds < 86400]
    
    all_df = []
    total_current_macd_tier = 0
    total_current_hist_tier = 0
    for ttf in active_ttf :
        if ttf in POLLENSTORY.keys() and ticker in ttf.split("_")[0]:
            df = POLLENSTORY[ttf]
            df = df[['timestamp_est', 'chartdate', 'name', 'macd_tier', 'hist_tier', 'profits']].copy()
            total_current_macd_tier += df.iloc[-1]['macd_tier']
            total_current_hist_tier += df.iloc[-1]['hist_tier']
            
            all_df.append(df)
    
    # st.write('macd', total_current_macd_tier, ': ', '{:,.2%}'.format(total_current_macd_tier/ 64))
    # st.write('hist', total_current_hist_tier, ': ', '{:,.2%}'.format(total_current_hist_tier / 64))
    
    # t = 'macd', total_current_macd_tier, " ", '{:,.2%}'.format(total_current_macd_tier/ 64)
    # h = 'hist', total_current_hist_tier, " ", '{:,.2%}'.format(total_current_hist_tier / 64)

    t = '{:,.2%}'.format(total_current_macd_tier/ 64)
    h = '{:,.2%}'.format(total_current_hist_tier / 64)


    return {'macd_tier_guage': t, 'hist_tier_guage': h}



def mark_down_text(align='center', color='Black', fontsize='33', text='Hello There'):
    st.markdown('<p style="text-align: {}; font-family:sans-serif; color:{}; font-size: {}px;">{}</p>'.format(align, color, fontsize, text), unsafe_allow_html=True)
    return True

def page_line_seperator(height='5', border='none', color='#333'):
    return st.markdown("""<hr style="height:{}px;border:{};color:#333;background-color:{};" /> """.format(height, border, color), unsafe_allow_html=True)

def write_flying_bee(width="45", height="45", frameBorder="0"):
    return st.markdown('<iframe src="https://giphy.com/embed/ksE4eFvxZM3oyaFEVo" width={} height={} frameBorder={} class="giphy-embed" allowFullScreen></iframe><p><a href="https://giphy.com/gifs/bee-traveling-flying-into-next-week-like-ksE4eFvxZM3oyaFEVo"></a></p>'.format(width, height, frameBorder), unsafe_allow_html=True)

def buzzz_linebreak(icon=">>>", size=15):
    line_break = str([icon for i in range(size)])
    return st.write(line_break)

def pollen__story_charts(df):
    with st.expander('pollen story'):
        df_write = df.astype(str)
        st.dataframe(df_write)
        pass
        


def color_coding(row):
    if row.mac_ranger == 'white':
        return ['background-color:white'] * len(row)
    elif row.mac_ranger == 'black':
        return ['background-color:black'] * len(row)
    elif row.mac_ranger == 'blue':
        return ['background-color:blue'] * len(row)
    elif row.mac_ranger == 'purple':
        return ['background-color:purple'] * len(row)
    elif row.mac_ranger == 'pink':
        return ['background-color:pink'] * len(row)
    elif row.mac_ranger == 'red':
        return ['background-color:red'] * len(row)
    elif row.mac_ranger == 'green':
        return ['background-color:green'] * len(row)
    elif row.mac_ranger == 'yellow':
        return ['background-color:yellow'] * len(row)

    
    import seaborn as sns
    cm = sns.light_palette("green", as_cmap=True)
    df.style.background_gradient(cmap=cm).set_precision(2)


# # Store the initial value of widgets in session state
# if "visibility" not in st.session_state:
#     st.session_state.visibility = "visible"
#     st.session_state.disabled = False
#     st.session_state.horizontal = False

# col1, col2 = st.columns(2)

# with col1:
#     st.checkbox("Disable radio widget", key="disabled")
#     st.checkbox("Orient radio options horizontally", key="horizontal")

# with col2:
#     st.radio(
#         "Set label visibility 👇",
#         ["visible", "hidden", "collapsed"],
#         key="visibility",
#         label_visibility=st.session_state.visibility,
#         disabled=st.session_state.disabled,
#         horizontal=st.session_state.horizontal,
#     )

# # # Show users table 
# colms = st.columns((1, 2, 2, 1, 1))
# fields = ["№", 'email', 'uid', 'verified', "action"]
# for col, field_name in zip(colms, fields):
#     # header
#     col.write(field_name)

# for x, email in enumerate(user_table['email']):
#     col1, col2, col3, col4, col5 = st.columns((1, 2, 2, 1, 1))
#     col1.write(x)  # index
#     col2.write(user_table['email'][x])  # email
#     col3.write(user_table['uid'][x])  # unique ID
#     col4.write(user_table['verified'][x])   # email status
#     disable_status = user_table['disabled'][x]  # flexible type of button
#     button_type = "Unblock" if disable_status else "Block"
#     button_phold = col5.empty()  # create a placeholder
#     do_action = button_phold.button(button_type, key=x)
#     if do_action:
#             pass # do some action with row's data
#             button_phold.empty()  #  remove button


# """ if "__name__" == "__main__": """
# USERS = [{'username': 'pollen', 'password': 'beebetter'},
# {'username': 'guest', 'password': 'bee'}, {'username': 'queen', 'password': 'bee'} ]

# placeholder = st.empty()
# isclick = placeholder.button('delete this button')
# if isclick:
#     placeholder.empty()

PB_USER_pickle = os.path.join(db_root, 'queen_users.plk')
if os.path.exists(PB_USER_pickle) == False:
    PickleData(PB_USER_pickle, {'users': [{'signin_count': 1, 'username': 'queen', 'password': 'bee', 'date': datetime.datetime.now(est)},
    {'signin_count': 1, 'username': 'pollen', 'password': 'master', 'date': datetime.datetime.now(est)}]})
USERS = ReadPickleData(PB_USER_pickle)

def add_user__vars(username, password, date=datetime.datetime.now(est), signin_count=1):
    return {'signin_count': 1, 'username': username, 'password': password, 'date': date}

def check_password(admin):
    """Returns True if the user had a correct password."""
    # for i, k in st.session_state.items():
    #     print(i, k)
    if admin == True:
        st.sidebar.write('admin', admin)
        st.session_state['password_correct'] = True
        return True

    if 'password_correct' in st.session_state and st.session_state['password_correct']:
        return True
    
    # def proc(un_create):
    #     if un_create in df_users['username'].tolist():
    #         mark_down_text(fontsize=10, color='Red', text='User Name Already Taken')

    # st.text_area('enter text', on_change=proc, key='text_key')
    
    with st.form('signin'):
        df_users = pd.DataFrame(USERS['users'])
        def password_entered():
            """Checks whether a password entered by the user is correct."""
            df = pd.DataFrame(USERS['users'])
            df['index'] = df.index
            un = st.session_state["username"]
            pw = st.session_state["password"]
            
            df_user = df[df['username'] == un].copy()
            if len(df_user) == 0:
                mark_down_text(text="No User Name Exists")
                return False
            correct_pw = df_user.iloc[-1]['password']
            if pw == correct_pw:
                if prod:
                    if un != 'pollen':
                        st.write("Who Are You and no You are not allowed in")
                        return False
                USERS['users'][df_user.iloc[-1]['index']]['signin_count'] += 1
                USERS['users'][df_user.iloc[-1]['index']]['date'] = datetime.datetime.now(est)
                print("pw correct")
                st.write("pw correct")
                write_flying_bee()
                st.session_state["password_correct"] = True
                del st.session_state["password"]  # don't store username + password
                del st.session_state["username"]
                PickleData(PB_USER_pickle, USERS)
                return True
            else:
                st.session_state["password_correct"] = False
                mark_down_text(text="sorry charlie thats not correct")
                return False

        st.text_input("Username", key="username")
        st.text_input("Password", type="password",  key="password")
        signin = st.form_submit_button("SignIn")

        with st.expander('Want your own Trading Bot? >>> Join pollenq'):
            st.write("Not a User? Join the QueensHive")

            st.text_input("Create Username", key="createusername")
            st.text_input("Create Password", type="password",  key="createpassword")
            st.text_input("Email",  key="email")

            create_user = st.form_submit_button("Join pollenq")
            un_create = st.session_state["createusername"]
            pw_create = st.session_state["createpassword"]
            email_ = st.session_state["email"]
            # st.write(un_create)
            if un_create in df_users['username'].tolist():
                mark_down_text(fontsize=10, color='Red', text='User Name Already Taken')
                do_not_create = True
            else:
                do_not_create = False

            if create_user:
                if do_not_create:
                    mark_down_text(fontsize=8, color='Red', text='User Name Already Taken')
                    return False
                else:        
                    USERS['users'].append(add_user__vars(username=un_create, password=pw_create))
                    PickleData(PB_USER_pickle, USERS)

                    del st.session_state["createusername"]
                    del st.session_state["createpassword"]
                    return False

        if signin:
            p = password_entered()

            if p:
                return True
            else:
                return False
        else:
            return False


if check_password(admin=admin):

# st.error("😕 User not known or password incorrect")

    # st.sidebar.write(write_flying_bee())
    st.sidebar.write("Production: ", prod)
    # st.write(prod)
    if prod:
        api = api
        # db_root = '/home/stapinski89/pollen/pollen/db/' # linix
        # db_root = '/Users/stefanstapinski/Jq/pollen' # mac
        PB_App_Pickle = os.path.join(db_root, f'{"queen"}{"_App_"}{".pkl"}')
        st.sidebar.write("""My Queen Production""")
    else:
        api = api_paper
        PB_App_Pickle = os.path.join(db_root, f'{"queen"}{"_App_"}{"_sandbox"}{".pkl"}')
        st.sidebar.write("""My Queen Sandbox""")


    KING = KINGME()
    pollen_theme = pollen_themes(KING=KING)


    QUEEN = read_queensmind(prod)['queen']
    POLLENSTORY = read_pollenstory()
    APP_requests = ReadPickleData(pickle_file=PB_App_Pickle)
    STORY_bee = QUEEN['queen']['conscience']['STORY_bee']
    KNIGHTSWORD = QUEEN['queen']['conscience']['KNIGHTSWORD']
    ANGEL_bee = QUEEN['queen']['conscience']['ANGEL_bee']

    # if "visibility" not in st.session_state:
    #     st.session_state.visibility = "visible"
    #     st.session_state.disabled = False
    #     st.session_state.horizontal = False
    c1,c2,c3,c4,c5, = st.columns(5)
    with c3:
        option = st.radio(
                    "",
            ["queen", "signal", "charts"],
            key="visibility",
            label_visibility='visible',
            # disabled=st.session_state.disabled,
            horizontal=True,
        )
    # option3 = st.sidebar.selectbox("Always RUN", ('No', 'Yes'))
    # option = st.sidebar.selectbox("Dashboards", ('queen', 'charts', 'signal'))
    st.sidebar.write("<<<('bee better')>>>")
    # st.header(option)

    page_line_seperator('3', color='#C5B743')

    colors = QUEEN['queen_controls']['power_rangers']['1Minute_1Day']['mac_ranger']['buy_wave']['nuetral']
    # st.write(colors)


    if option == 'charts':
        tickers_avail = list([set(i.split("_")[0] for i in POLLENSTORY.keys())][0])
        ticker_option = st.sidebar.selectbox("Tickers", tickers_avail, index=tickers_avail.index(["SPY" if "SPY" in tickers_avail else tickers_avail[0]][0]))
        ttframe_list = list(set([i.split("_")[1] + "_" + i.split("_")[2] for i in POLLENSTORY.keys()]))
        ttframe_list.append(["short_star", "mid_star", "long_star", "retire_star"])
        frame_option = st.sidebar.selectbox("ttframes", ttframe_list, index=ttframe_list.index(["1Minute_1Day" if "1Minute_1Day" in ttframe_list else ttframe_list[0]][0]))
        day_only_option = st.sidebar.selectbox('Show Today Only', ['no', 'yes'], index=['no'].index('no'))
        slope_option = st.sidebar.selectbox('Show Slopes', ['no', 'yes'], index=['no'].index('no'))
        wave_option = st.sidebar.selectbox('Show Waves', ['no', 'yes'], index=['no'].index('no'))
        fullstory_option = st.sidebar.selectbox('POLLENSTORY', ['no', 'yes'], index=['yes'].index('yes'))
        selections = [i for i in POLLENSTORY.keys() if i.split("_")[0] in ticker_option and i.split("_")[1] in frame_option]

        ticker_time_frame = selections[0]
        df = POLLENSTORY[ticker_time_frame].copy()



        st.markdown('<div style="text-align: center;">{}</div>'.format(ticker_option), unsafe_allow_html=True)

        star__view = its_morphin_time_view(QUEEN=QUEEN, STORY_bee=STORY_bee, ticker=ticker_option)

        pollen__story_charts(df=df)


        if day_only_option == 'yes':
            df_day = df['timestamp_est'].iloc[-1]
            df['date'] = df['timestamp_est'] # test
            # df = df.set_index('timestamp_est', drop=False) # test
            # between certian times
            # df_t = df.between_time('9:30', '12:00')
            df_today = df[df['timestamp_est'] > (datetime.datetime.now().replace(hour=1, minute=1, second=1)).astimezone(est)].copy()
            df_prior = df[~(df['timestamp_est'].isin(df_today['timestamp_est'].to_list()))].copy()
            # df = df[(df['timestamp_est'].day == df_day.day) & 
            #         (df['timestamp_est'].month == df_day.month) & 
            #         (df['timestamp_est'].year == df_day.year)
            #     ].copy() # remove other days
            df = df_today

        # if fullstory_option == 'yes':
        #     df_write = df.astype(str)
        #     st.dataframe(df_write)
                # ag_grid_main_build(df=df_write, default=True, add_vars={'update_mode_value': 'MODEL_CHANGED'})
            
            
        # Main CHART Creation
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


    if option == 'queen':
        cq1, cq2, cq3 = st.columns(3)
        with cq1:
            update_queen_controls = st.selectbox('Show Symbol Trading Model Controls', ['yes', 'no'], index=['no'].index('no'))
            st.session_state['qc'] = update_queen_controls
            update_queen_controls = st.button("Show Symbol Trading Model Controls")
            controls = st.button("Portfolio Controls")
            
        if controls:
            # st.write("direct to control page")
            mark_down_text(color='Red', text="PENDING DEV WORKING")
        
        # if st.session_state['qc'] == 'yes':
        if update_queen_controls == True:
            theme_list = list(pollen_theme.keys())
            contorls = list(QUEEN['queen_controls'].keys())
            # control_option = st.selectbox('Show Trading Models', contorls, index=contorls.index('theme'))
            update_QueenControls(APP_requests=APP_requests, control_option='symbols_stars_TradingModel', theme_list=theme_list)
        
        # Global Vars
        tickers_avail = [set(i.split("_")[0] for i in STORY_bee.keys())][0]
        tickers_avail.update({"all"})
        tickers_avail_op = list(tickers_avail)
        ticker_option = st.sidebar.selectbox("Tickers", tickers_avail_op, index=tickers_avail_op.index('SPY'))
        ticker = ticker_option
        ticker_storys = {k:v for (k,v) in STORY_bee.items() if k.split("_")[0] == ticker_option}

        
        option_showaves = st.sidebar.selectbox("Show Waves", ('no', 'yes'), index=["no"].index("no"))

        command_conscience_option = st.sidebar.selectbox("command conscience", ['yes', 'no'], index=["yes"].index("yes"))
        orders_table = st.sidebar.selectbox("orders_table", ['no', 'yes'], index=["no"].index("no"))
        today_day = datetime.datetime.now().day
        
        with cq1:
            mark_down_text(align='Left', fontsize='64', text=ticker_option)
            # page_line_seperator(color='Green')
        with cq2:
            return_buying_power(api=api)
            # return_total_profits(QUEEN=QUEEN)
            # page_line_seperator()
        with cq3:
            return_total_profits(QUEEN=QUEEN)
        
        page_line_seperator()

        cq1, cq2, cq3 = st.columns((3,1,1))
        
        if command_conscience_option == 'yes':
            now_time = datetime.datetime.now().astimezone(est)
            all_trigs = {k: i['story']["alltriggers_current_state"] for (k, i) in STORY_bee.items() if len(i['story']["alltriggers_current_state"]) > 0 and (now_time - i['story']['time_state']).seconds < 33}
            
            
            with cq1:
                if len(all_trigs) > 0:
                    mark_down_text(fontsize=25, color='Green', text="All Available TriggerBees")
                    df = pd.DataFrame(all_trigs.items())
                    df = df.rename(columns={0: 'ttf', 1: 'trig'})
                    df = df.sort_values('ttf')
                    st.write(df)
                    g = {write_flying_bee() for i in range(len(df))}
                else:
                    mark_down_text(fontsize=25, color='Red', text="No Available TriggerBees")
                with cq2:
                    write_flying_bee(width=100, height=100)

            page_line_seperator()

            mark_down_text(align='center', color='Black', fontsize='33', text='Order Flow')

            with st.expander('Orders'):
                error_orders = queen_orders_view(QUEEN=QUEEN, queen_order_state=['error'], return_all_cols=True)['df']
                error_orders = error_orders.astype(str)
                if len(error_orders)> 0:
                    new_title = '<p style="font-family:sans-serif; color:Black; font-size: 25px;">ERRORS</p>'
                    st.markdown(new_title, unsafe_allow_html=True)
                    st.dataframe(error_orders)

                for order_state in active_queen_order_states:
                    df = queen_orders_view(QUEEN=QUEEN, queen_order_state=[order_state])['df']
                    if len(df) > 89:
                        grid_height = 654
                    elif len(df) < 10:
                        grid_height = 200
                    else:
                        grid_height = 333
                    
                    if len(df) > 0:
                        if order_state == 'error':
                            continue
                        elif order_state == 'submitted':
                            mark_down_text(align='center', color='Green', fontsize='23', text=order_state)
                            run_orders__agrid_submit = build_AGgrid_df__queenorders(data=df, reload_data=False, update_cols=['comment'], height=grid_height)
                        elif order_state == 'running_open':
                            mark_down_text(align='center', color='Green', fontsize='23', text=order_state)
                            run_orders__agrid_open = build_AGgrid_df__queenorders(data=df, reload_data=False, update_cols=['comment'], height=grid_height)
                        elif order_state == 'running':
                            mark_down_text(align='center', color='Green', fontsize='23', text=order_state)
                            # df['honey'] = 
                            # df['honey'] = pd.to_numeric(df['honey'], errors='coerce').fillna(0)
                            # df['honey'] = df['honey'].apply(lambda x: convert_to_float(x))
                            # df.loc['Total'] = df.sum(numeric_only=True)
                            run_orders__agrid = build_AGgrid_df__queenorders(data=df, reload_data=False, update_cols=['comment'], height=grid_height)
                            # df.iloc[[df.columns.tolist()][0]] = 'Total'
                        elif order_state == 'running_close':
                            mark_down_text(align='center', color='Green', fontsize='23', text=order_state)
                            run_orders__agrid_open = build_AGgrid_df__queenorders(data=df, reload_data=False, update_cols=['comment'], height=grid_height)




        if orders_table == 'yes':
            with st.expander('orders table -- Today', expanded=True):

                df = queen_orders_view(QUEEN=QUEEN, queen_order_state=['completed', 'completed_alpaca'])['df']
                # df_today = split_today_vs_prior(df=df, other_timestamp='datetime')['df_today']
                ordertables__agrid = build_AGgrid_df__queenorders(data=df, reload_data=False, update_cols=['comment'], height=500)

            

        st.write("QUEENS Collective CONSCIENCE")
        if ticker_option != 'all':

            star__view = its_morphin_time_view(QUEEN=QUEEN, STORY_bee=STORY_bee, ticker=ticker_option)
            
            # cq1_1, cq2_2 = st.columns((1, 1))

            # with cq2_2:

            st.markdown('<div style="text-align: center;color:Blue; font-size: 33px;">{}</div>'.format("STARS IN HEAVEN"), unsafe_allow_html=True)

                # return ['background-color:black'] * len(
                #     row) if row.mac_ranger == 'white'  else ['background-color:green'] * len(row)
            with st.expander('Tickers Stars'):
                mark_down_text(fontsize=25, text=f'{"MACD Guage "}{star__view["macd_tier_guage"]}')
                mark_down_text(fontsize=22, text=f'{"Hist Guage "}{star__view["hist_tier_guage"]}')
                df = story_view(STORY_bee=STORY_bee, ticker=ticker_option)['df']
                df = df.style.background_gradient(cmap="RdYlGn", gmap=df['current_macd_tier'], axis=0, vmin=-8, vmax=8)
                # df = df.style.background_gradient(subset=["current_hist_tier"], cmap="RdYlGn", vmin=-8, vmax=8)
                # df['mac_ranger'] = df['mac_ranger'].apply(lambda x: color_coding(x))
                # st.dataframe(df.style.apply(color_coding, axis=1))
                st.dataframe(df)
                # st.markdown('<style>div[title="mac_ranger"] { color: green; } div[title="white"] { color: red; } .data:hover{ background:rgb(243 246 255)}</style>', unsafe_allow_html=True)

            
            # ag_grid_main_build(df=story_view(STORY_bee=STORY_bee, ticker=ticker_option)['df'], 
            # default=True, add_vars={'update_cols': False}, write_selection=False)
            
            
            # View Star and Waves
            # m2 = {k:v for (k,v) in KNIGHTSWORD.items() if k.split("_")[0] == ticker_option}

            # # Analyze Waves
            # st.markdown('<div style="text-align: center;">{}</div>'.format('analzye waves'), unsafe_allow_html=True)
            # df = pd.DataFrame(analyze_waves(STORY_bee, ttframe_wave_trigbee=False)['df']) 
            # df = df.astype(str)
            # st.write(df)

            # # Summary of all ticker_time_frames
            # st.markdown('<div style="text-align: center;color:Purple; font-size: 33px;">{}</div>'.format("SUMMARY ALL WAVES"), unsafe_allow_html=True)
            # st.markdown(new_title, unsafe_allow_html=True)
            # df = pd.DataFrame(analyze_waves(STORY_bee, ttframe_wave_trigbee=False)['df_agg_view_return'])
            # df = df.astype(str)
            # st.write(df)
            
            st.markdown('<div style="text-align: center;color:Purple; font-size: 33px;">{}</div>'.format("TRIGBEE WAVES"), unsafe_allow_html=True)
            dict_list_ttf = analyze_waves(STORY_bee, ttframe_wave_trigbee=False)['d_agg_view_return']        

            for trigbee in dict_list_ttf[list(dict_list_ttf.keys())[0]]:
                ticker_selection = {k: v for k, v in dict_list_ttf.items() if ticker_option in k}
                buys = [data[trigbee] for k, data in ticker_selection.items()]
                df_trigbee_waves = pd.concat(buys, axis=0)
                col_view = ['ticker_time_frame'] + [i for i in df_trigbee_waves.columns if i not in 'ticker_time_frame']
                df_trigbee_waves = df_trigbee_waves[col_view]
                if 'buy' in trigbee:
                    st.markdown("""<hr style="height:5px;border:none;color:#333;background-color:#333;" /> """, unsafe_allow_html=True)
                    st.markdown('<div style="text-align: center;color:Green; font-size: 33px;">{}{}</div>'.format("Trigbee : ", trigbee), unsafe_allow_html=True)

                else:
                    st.markdown("""<hr style="height:5px;border:none;color:#333;background-color:#333;" /> """, unsafe_allow_html=True)
                    st.markdown('<div style="text-align: center;color:Red; font-size: 33px;">{}{}</div>'.format("Trigbee : ", trigbee), unsafe_allow_html=True)

                # df_trigbee_waves["maxprofit"] = df_trigbee_waves['maxprofit'].map("{:.2f}".format)
                # total winners total loser, total maxprofit
                t_winners = sum(df_trigbee_waves['winners_n'].apply(lambda x: int(x)))
                t_losers = sum(df_trigbee_waves['losers_n'].apply(lambda x: int(x)))
                # t_maxprofit = round(sum(df_trigbee_waves['sum_maxprofit'].apply(lambda x: float(x))),2)
                total_waves = t_winners + t_losers
                win_pct = 100 * round(t_winners / total_waves, 2)
                
                title = f'{"Total Winners "}{t_winners}{" ::: Total Losers "}{t_losers}{" ::: won "}{win_pct}{"%"}'
                mark_down_text(align='left', color='Green', fontsize='23', text=title)
                
                # Top Winners Header
                df_bestwaves = analyze_waves(STORY_bee, ttframe_wave_trigbee=df_trigbee_waves['ticker_time_frame'].iloc[-1])['df_bestwaves']
                st.markdown('<div style="text-center: center;color:Purple; font-size: 20px;">{}{}{}</div>'.format("BEST WAVES : ", 'top: ', len(df_bestwaves)), unsafe_allow_html=True)
                st.dataframe(df_bestwaves)
                # Data
                st.dataframe(df_trigbee_waves)



            # ticker_selection = {k: v for k, v in dict_list_ttf.items() if ticker_option in k}
            # buys = [data['buy_cross-0'] for k, data in ticker_selection.items()]
            # df_trigbee_waves = pd.concat(buys, axis=0)

            
            # [st.write(k, v) for k,v in v.items()]
            # df = pd.DataFrame(dict_list_ttf[ticker_option])
            # df = df.astype(str)
            # df = df.T
            # st.write(df)

            # d_agg_view_return[ticker_time_frame]["buy_cross-0"]
            # avail_trigbees = df.columns.to_list()
            # for trigbee in avail_trigbees:
            #     trigbee_wave = df[trigbee]



            for ttframe, knowledge in ticker_storys.items():
                # with st.form(str(ttframe)):
                # WaveUp
                st.markdown('<div style="text-align: left;">{}</div>'.format("WAVE UP"), unsafe_allow_html=True)
                df = pd.DataFrame(analyze_waves(STORY_bee, ttframe_wave_trigbee=ttframe)['df'])
                df = df.astype(str)
                st.write(datetime.datetime.now().astimezone(est), 'EST')
                st.dataframe(df)

                # # Top Winners
                # buzzz_linebreak()
                # df_day_bestwaves = analyze_waves(STORY_bee, ttframe_wave_trigbee=ttframe)['df_day_bestwaves']
                # df_bestwaves = analyze_waves(STORY_bee, ttframe_wave_trigbee=ttframe)['df_bestwaves']
                # df_bestwaves_sell = analyze_waves(STORY_bee, ttframe_wave_trigbee=ttframe)['df_bestwaves_sell_cross']
                # df_best_buy__sell__waves = analyze_waves(STORY_bee, ttframe_wave_trigbee=ttframe)['df_best_buy__sell__waves']
                # st.markdown('<div style="text-align: center;color:Purple; font-size: 20px;">{}{}{}</div>'.format("BEST WAVES (mac) : ", 'top: ', len(df_bestwaves)), unsafe_allow_html=True)
                # st.write('top buy waves', df_bestwaves)
                # st.write('top sell waves', df_bestwaves_sell)
                # st.write('top day buy waves', df_day_bestwaves)
                # st.write('top day buy/sell waves', df_best_buy__sell__waves)
                # buzzz_linebreak()

                # Today df_today
                buzzz_linebreak()
                st.markdown('<div style="text-align: left;">{}</div>'.format("WAVE UP TODAY"), unsafe_allow_html=True)
                df = pd.DataFrame(analyze_waves(STORY_bee, ttframe_wave_trigbee=ttframe)['df_today'])
                df = df.astype(str)
                st.write(datetime.datetime.now().astimezone(est), 'EST')
                st.dataframe(df)
                buzzz_linebreak()

                # # WaveDown
                # st.markdown('<div style="text-align: center;">{}</div>'.format("WAVE DOWN"), unsafe_allow_html=True)
                # df = pd.DataFrame(analyze_waves(STORY_bee, ttframe_wave_trigbee=ttframe)['df_wavedown'])
                # df = df.astype(str)
                # st.write(datetime.datetime.now().astimezone(est), 'EST')
                # st.dataframe(df)
                
                # # view details
                # st.write("VIEW TRANSPOSE")
                # df = df.T
                # st.dataframe(df)
                # agg_view = pd.DataFrame(agg_view)
                # agg_view = agg_view.astype(str)
                # st.dataframe(agg_view)

                # st.write(ttframe)
                # story_sort = knowledge['story']
                # st.write(story_sort)
                
                if option_showaves.lower() == 'yes':
                    st.write("waves story -- investigate BACKEND functions")
                    df = knowledge['waves']['story']
                    df = df.astype(str)
                    st.dataframe(df)

                    st.write("buy cross waves")
                    m_sort = knowledge['waves']['buy_cross-0']
                    df_m_sort = pd.DataFrame(m_sort).T
                    # df_m_sort['wave_times'] = df_m_sort['wave_times'].apply(lambda x: [])
                    df_m_sort = df_m_sort.astype(str)
                    st.dataframe(data=df_m_sort)
                    # grid_response = build_AGgrid_df(data=df_m_sort, reload_data=False, height=333, update_cols=['Note'])
                    # data = grid_response['data']

                    st.write("sell cross waves")
                    m_sort = knowledge['waves']['sell_cross-0']
                    df_m_sort = pd.DataFrame(m_sort).T
                    df_m_sort = df_m_sort.astype(str)
                    st.dataframe(data=df_m_sort)

        else:
            # st.write(STORY_bee)
            print("groups not allowed yet")
        
        st.selectbox("memory timeframe", ['today', 'all'], index=['today'].index('today'))
        df = QUEEN['queen_orders']
        
        # queen shows only today orders
        now_ = datetime.datetime.now(est)
        orders_today = df[df['datetime'] > now_.replace(hour=1, minute=1, second=1)].copy()
        orders_today = orders_today.astype(str)
        st.write(orders_today)


    if option == 'signal':
        betty_bee = ReadPickleData(os.path.join(db_root, 'betty_bee.pkl'))
        df_betty = pd.DataFrame(betty_bee)
        df_betty = df_betty.astype(str)
        c1,c2,c3,c4,c5 = st.columns(5)
        # col_d = {f'{"c"}{n}': for n in [c1,c2,c3,c4,c5,c6,c7,c8]}

        st.write(APP_requests['queen_controls'])

        # save_signals = st.sidebar.selectbox('Send to Queen', ['beeaction', 'orders', 'controls', 'QueenOrders'], index=['controls'].index('controls'))
        # c1,c2,c3,c4, c5 = st.columns(5)
        with c3:
            option__ = st.radio(
                                    "",
                ['beeaction', 'orders', 'controls', 'QueenOrders'],
                key="signal_radio",
                label_visibility='visible',
                # disabled=st.session_state.disabled,
                horizontal=True,
            )

        # with c4:
        #     write_flying_bee()
        # with random.choice(range(1))
        with st.expander('betty_bee'):
            st.write(df_betty)

        
        save_signals = option__
        
        col1, col2 = st.columns(2)

        ## SHOW CURRENT THEME
        with st.sidebar:
            # with st.echo():
                # st.write("theme>>>", QUEEN['collective_conscience']['theme']['current_state'])
            st.write("theme>>>", QUEEN['queen_controls']['theme'])


        if save_signals == 'controls':
            with st.expander('Heartbeat'):
                st.write(QUEEN['heartbeat'])
            
            with col1:
                stop_queenbee(APP_requests=APP_requests)
            with col2:
                refresh_queenbee_controls(APP_requests=APP_requests)

            theme_list = list(pollen_theme.keys())
            contorls = list(QUEEN['queen_controls'].keys())
            control_option = st.selectbox('select control', contorls, index=contorls.index('theme'))

            update_QueenControls(APP_requests=APP_requests, control_option=control_option, theme_list=theme_list)


        if save_signals == 'QueenOrders':

            # Update run order
            all_orders = QUEEN['queen_orders']
            active_orders = all_orders[all_orders['queen_order_state'].isin(active_order_state_list)].copy()
            show_errors_option = st.selectbox('show last error', ['no', 'yes'], index=['no'].index('no'))
            c_order_input_list = st.multiselect("active client_order_id", active_orders['client_order_id'].to_list(), default=active_orders.iloc[-1]['client_order_id'])
            
            c_order_input = [c_order_input_list[0] if len(c_order_input_list) > 0 else all_orders.iloc[-1]['client_order_id'] ][0]

            # if show_errors_option == 'yes':
            if show_errors_option == 'yes':
                latest_queen_order = all_orders[all_orders['queen_order_state'] == 'error'].copy()
            else:                
                latest_queen_order = df[df['client_order_id'] == c_order_input].copy()


            st.write("current queen order requests")
            data = ReadPickleData(pickle_file=PB_App_Pickle)
            st.write(data['update_queen_order'])
            
            df = latest_queen_order
            df = df.T.reset_index()
            df = df.astype(str)
            df = df.rename(columns={0: 'main'})

            # df = latest_queen_order.astype(str)

            
            grid_response = build_AGgrid_df(data=df, reload_data=False, update_cols=['update_column'], height=933)
            data = grid_response['data']
            # st.write(data)
            ttframe = data[data['index'] == 'ticker_time_frame'].copy()
            ttframe = ttframe.iloc[0]['main']
            # st.write(ttframe.iloc[0]['main'])
            selected = grid_response['selected_rows'] 
            df_sel = pd.DataFrame(selected)

            if len(df_sel) > 0:
                df_sel = df_sel.astype(str)
                st.write(df_sel)
                up_values = dict(zip(df_sel['index'], df_sel['update_column_update']))
                up_values = {k: v for (k,v) in up_values.items() if len(v) > 0}
                update_dict = {latest_queen_order[0]["client_order_id"]: up_values}
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
                    
    
        # if save_signals == 'orders':
        #     show_app_req = st.selectbox('show app requests', ['yes', 'no'], index=['yes'].index('yes'))
        #     if show_app_req == 'yes':
        #         data = ReadPickleData(pickle_file=PB_App_Pickle)
        #         st.write("sell orders", data['sell_orders'])
        #         st.write("buy orders", data['buy_orders'])
        #     df = QUEEN['queen_orders']
            
        #     running_orders = df[df['queen_order_state'] == 'running'].copy()
            
        #     # running_portfolio = return_dfshaped_orders(running_orders)
            
        #     # portfolio = return_alpc_portolio(api)['portfolio']
        #     # p_view = {k: [v['qty'], v['qty_available']] for (k,v) in portfolio.items()}
        #     # st.write(p_view)
        #     # st.write(running_portfolio)

        #     position_orders = [i for i in running_orders if not i['client_order_id'].startswith("close__") ]
        #     closing_orders = [i for i in running_orders if i['client_order_id'].startswith("close__") ]
        #     c_order_ids = [i['client_order_id'] for i in position_orders]
        #     c_order_iddict = {i['client_order_id']: idx for idx, i in enumerate(position_orders)}
        #     c_order_ids.append("Select")
        #     c_order_id_option = st.selectbox('client_order_id', c_order_ids, index=c_order_ids.index('Select'))
        #     if c_order_id_option != 'Select':
        #         run_order = position_orders[c_order_iddict[c_order_id_option]]
        #         run_order_alpaca = check_order_status(api=api, client_order_id=c_order_id_option, queen_order=run_order, prod=prod)
        #         st.write(("pollen matches alpaca", float(run_order_alpaca['filled_qty']) == float(run_order['filled_qty']))) ## VALIDATION FOR RUN ORDERS
        #         st.write(run_order_alpaca)
        #         st.write(run_order['filled_qty'])
        #         sell_qty_option = st.number_input(label="Sell Qty", max_value=float(run_order['filled_qty']), value=float(run_order['filled_qty']), step=1e-4, format="%.4f")
        #         # sell_qty_option = st.selectbox('sell_qty', [run_order['filled_qty']])
        #         type_option = st.selectbox('type', ['market'], index=['market'].index('market'))                

        #         sell_command = st.button("Sell Order")
        #         if sell_command:
        #             st.write("yes")
        #             # val qty
        #             if sell_qty_option > 0 and sell_qty_option <= float(run_order['filled_qty']):
        #                 print("qty validated")
        #                 # process order signal
        #                 client_order_id = c_order_id_option
        #                 sellable_qty = sell_qty_option
                        
        #                 order_dict = {'system': 'app',
        #                 'request_time': datetime.datetime.now(),
        #                 'client_order_id': client_order_id, 'sellable_qty': sellable_qty,
        #                 'side': 'sell',
        #                 'type': type_option,
        #                 'app_requests_id' : f'{save_signals}{"_app-request_id_"}{return_timestamp_string()}{datetime.datetime.now().microsecond}'

        #                 }
        #                 data = ReadPickleData(pickle_file=PB_App_Pickle)
        #                 data['sell_orders'].append(order_dict)
        #                 PickleData(pickle_file=PB_App_Pickle, data_to_store=data)
        #                 data = ReadPickleData(pickle_file=PB_App_Pickle)
        #                 st.write(data['sell_orders'])
                    
        #             if sell_qty_option < 0 and sell_qty_option >= float(run_order['filled_qty']):
        #                 print("qty validated")
        #                 # process order signal
        #                 client_order_id = c_order_id_option
        #                 sellable_qty = sell_qty_option
                        
        #                 order_dict = {'system': 'app',
        #                 'request_time': datetime.datetime.now(),
        #                 'client_order_id': client_order_id, 'sellable_qty': sellable_qty,
        #                 'side': 'sell',
        #                 'type': type_option,
        #                 'app_requests_id' : f'{save_signals}{"_app-request_id_"}{return_timestamp_string()}{datetime.datetime.now().microsecond}'

        #                 }
        #                 data = ReadPickleData(pickle_file=PB_App_Pickle)
        #                 data['sell_orders'].append(order_dict)
        #                 PickleData(pickle_file=PB_App_Pickle, data_to_store=data)
        #                 data = ReadPickleData(pickle_file=PB_App_Pickle)
        #                 st.write(data['sell_orders'])

        
        if save_signals == 'beeaction':
            st.write("beeaction")

            wave_button_sel = st.selectbox("Waves", ["buy_cross-0", "sell_cross-0"])
            initiate_waveup = st.button("Send Wave")
            # pollen = return_pollen()
            # ticker_time_frame = [set(i for i in STORY_bee.keys())][0]
            ticker_time_frame = QUEEN['heartbeat']['available_tickers']

            if len(ticker_time_frame) == 0:
                ticker_time_frame = list(set(i for i in STORY_bee.keys()))

            # ticker_time_frame = [i for i in ticker_time_frame]
            # ticker_time_frame.sort()
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


            new_title = '<p style="font-family:sans-serif; color:Black; font-size: 33px;">Flash Buttons</p>'
            st.markdown(new_title, unsafe_allow_html=True)
            
            c1, c2, = st.columns(2)
            with c1:
                quick_buy_short = st.button("FLASH BUY SQQQ")
            with c2:
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
                    'request_time': datetime.datetime.now(est),
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


    # with st.sidebar:
    #     stop_queenbee(APP_requests)
else:
    st.write("user auth")    
    ##### END ####