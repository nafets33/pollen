from asyncore import poll
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
from scipy.stats import linregress
from scipy import stats
import math
import matplotlib.pyplot as plt
from plotly.subplots import make_subplots
from PIL import Image
# import mplfinance as mpf
import plotly.graph_objects as go
import base64
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode, JsCode
import json
import argparse

scriptname = os.path.basename(__file__)
if 'sandbox' in scriptname:
    prod = False
else:
    prod = True

def createParser():
    parser = argparse.ArgumentParser()
    parser.add_argument ('-qcp', default="queen")
    parser.add_argument ('-prod', default='false')
    return parser

if prod:
    from QueenHive import refresh_account_info, generate_TradingModel, stars, analyze_waves, KINGME, queen_orders_view, story_view, return_alpc_portolio, return_dfshaped_orders, ReadPickleData, pollen_themes, PickleData, return_timestamp_string, return_api_keys, read_pollenstory, read_queensmind, read_csv_db, split_today_vs_prior, check_order_status
else:
    from QueenHive_sandbox import refresh_account_info, generate_TradingModel, stars, analyze_waves, KINGME, queen_orders_view, story_view, return_alpc_portolio, return_dfshaped_orders, ReadPickleData, pollen_themes, PickleData, return_timestamp_string, return_api_keys, read_pollenstory, read_queensmind, read_csv_db, split_today_vs_prior, check_order_status




main_root = os.getcwd()
db_root = os.path.join(main_root, 'db')
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
st.sidebar.image(image, caption='pollenq', width=89)

bee_power_image = os.path.join(jpg_root, 'power.jpg')
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
    if '1Minute_1Day' in df.iloc[0]['name']:
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


def pollenstory_view(POLLENSTORY):
    option_ticker = st.selectbox("ticker", ('queen', 'charts', 'signal', 'pollenstory'))

    return True

# def run_charts(POLLENSTORY = False):
    # with st.form("my_form"):
    #     # tickers_avail = list([set(i.split("_")[0] for i in POLLENSTORY.keys())][0])
    #     # ticker_option = st.sidebar.selectbox("Tickersme", tickers_avail, index=tickers_avail.index(["SPY" if "SPY" in tickers_avail else tickers_avail[0]][0]))
    #     st.write("Inside the form")
    #     slider_val = st.slider("Form slider")
    #     checkbox_val = st.checkbox("Form checkbox")

    #     # Every form must have a submit button.
    #     submitted = st.form_submit_button("Submit")
    #     if submitted:
    #         st.write("slider", slider_val, "checkbox", checkbox_val)

    # st.write("Outside the form")
    return True


def stop_queenbee(APP_requests):
    with st.form("stop queen"):
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
        st.write(QUEEN['queen_controls'][control_option])
        tickers_avail = list(QUEEN['queen_controls'][control_option].keys())
        ticker_option_qc = st.selectbox("Select Tickers", tickers_avail, index=tickers_avail.index(["SPY" if "SPY" in tickers_avail else tickers_avail[0]][0]))
        star_avail = list(QUEEN['queen_controls'][control_option][ticker_option_qc].keys())
        star_option_qc = st.selectbox("Select Star", star_avail, index=star_avail.index(["1Minute_1Day" if "1Minute_1Day" in star_avail else star_avail[0]][0]))

        with st.form('trading model form'):
            trading_model_dict = QUEEN['queen_controls'][control_option][ticker_option_qc][star_option_qc]
            trigbees = trading_model_dict['trigbees']
            for k, v in QUEEN['queen_controls'][control_option][ticker_option_qc][star_option_qc].items():

                if k == 'status':
                    # st.write(k, v)
                    control_status = st.selectbox("control_status", ['active', 'not_active'], index=['active', 'not_active'].index(v))
                elif k == 'total_budget':
                    st.write(k, v)
                    total_budget = st.number_input(label=k, value=float(v))
                elif k == 'trade_using_limits':
                    # st.write(k, v)
                    trade_using_limits = st.checkbox("trade_using_limits")
                elif k == 'buyingpower_allocation_LongTerm':
                    st.write(k, v)
                    buyingpower_allocation_LongTerm = st.number_input(label=k, value=float(v))
                elif k == 'buyingpower_allocation_ShortTerm':
                    st.write(k, v)
                    buyingpower_allocation_ShortTerm = st.number_input(label=k, value=float(v))
                elif k == 'trigbees':
                    st.write(k, v)
                    if 'buy_cross-0' in v.keys():
                        st.write('buy_cross-0')
                        op_trigbee_bc = st.checkbox('status_bc', value=True)
                        op_trigbee_max_profit_waveDeviation_bc = st.number_input(label='max_profit_waveDeviation_bc', value=int(v['buy_cross-0']['max_profit_waveDeviation']))
                        op_trigbee_timeduration_bc = st.number_input(label='timeduration_bc', value=int(v['buy_cross-0']['timeduration']))
                        op_trigbee_take_profit_bc = st.number_input(label='take_profit_bc', value=float(v['buy_cross-0']['take_profit']))
                        op_trigbee_sellout_bc = st.number_input(label='sellout_bc', value=float(v['buy_cross-0']['sellout']))
                        op_trigbee_sell_trigbee_trigger_bc = st.checkbox('sell_trigbee_trigger_bc', value=v['buy_cross-0']['sell_trigbee_trigger'])
                        op_stagger_profits_bc = st.checkbox('stagger_profits_bc', value=v['buy_cross-0']['stagger_profits'])
                        op_scalp_profits_bc = st.checkbox('scalp_profits_bc', value=v['buy_cross-0']['scalp_profits'])

                    if 'sell_cross-0' in v.keys():
                        st.write('sell_cross-0')
                        op_trigbee_sc = st.checkbox('status_sc', value=True)
                        op_trigbee_max_profit_waveDeviation_sc = st.number_input(label='max_profit_waveDeviation_sc', value=int(v['sell_cross-0']['max_profit_waveDeviation']))
                        op_trigbee_timeduration_sc = st.number_input(label='timeduration_sc', value=float(v['sell_cross-0']['timeduration']))
                        op_trigbee_take_profit_sc = st.number_input(label='take_profit_sc', value=float(v['sell_cross-0']['take_profit']))
                        op_trigbee_sellout_sc = st.number_input(label='sellout_sc', value=float(v['sell_cross-0']['sellout']))
                        op_trigbee_sell_trigbee_trigger_sc = st.checkbox('sell_trigbee_trigger_sc', value=v['sell_cross-0']['sell_trigbee_trigger'])
                        op_stagger_profits_sc = st.checkbox('stagger_profits_sc', value=v['sell_cross-0']['stagger_profits'])
                        op_scalp_profits_sc = st.checkbox('scalp_profits_sc', value=v['sell_cross-0']['scalp_profits'])

                    if 'ready_buy_cross' in v.keys():
                        st.write('ready_buy_cross')
                        op_trigbee_rb = st.checkbox('status_rb', value=True)
                        op_trigbee_max_profit_waveDeviation_rb = st.number_input(label='max_profit_waveDeviation_rb', value=int(v['ready_buy_cross']['max_profit_waveDeviation']))
                        op_trigbee_timeduration_rb = st.number_input(label='timeduration_rb', value=int(v['ready_buy_cross']['timeduration']))
                        op_trigbee_take_profit_rb = st.number_input(label='take_profit_rb', value=float(v['ready_buy_cross']['take_profit']))
                        op_trigbee_sellout_rb = st.number_input(label='sellout_rb', value=float(v['ready_buy_cross']['sellout']))
                        op_trigbee_sell_trigbee_trigger_rb = st.checkbox('sell_trigbee_trigger_rb', value=v['ready_buy_cross']['sell_trigbee_trigger'])
                        op_stagger_profits_rb = st.checkbox('stagger_profits_rb', value=v['ready_buy_cross']['stagger_profits'])
                        op_scalp_profits_rb = st.checkbox('scalp_profits_rb', value=v['ready_buy_cross']['scalp_profits'])

                elif k == 'trigbees_kings_order_rules':
                    st.write(k, v)
                elif k == 'power_rangers':
                    st.write("active stars", k, v)
                    # all_stars = stars()

                    df = pd.DataFrame(v.items())
                    df = df.rename(columns={0: 'star', 1: 'status'})

                    
                    # make into 1
                    # st.write(df)

                    grid_response = build_AGgrid_df(data=df, reload_data=True, update_mode_value='SELECTION_CHANGED', height=333, update_cols=['star_status'], dropdownlst=['active', 'not_active'])
                    data = grid_response['data']
                    selected = grid_response['selected_rows'] 
                    df_sel = pd.DataFrame(selected)
                    st.write(df_sel)
                    # if len(df_sel) > 0:
                    #     star_dict = dict(zip(df_sel['star'], df['star_status_update']))
                    #     trading_model_dict['power_rangers'] = star_dict # 'power_rangers'

            # Create
            
            save_button_addranger = st.form_submit_button("update active star rangers")
            if save_button_addranger:
                app_req = create_AppRequest_package(request_name='trading_models',  archive_bucket='trading_models_requests')
                trading_model_dict['status'] = control_status
                trading_model_dict['trade_using_limits'] = trade_using_limits
                trading_model_dict['buyingpower_allocation_LongTerm'] = buyingpower_allocation_LongTerm
                trading_model_dict['buyingpower_allocation_ShortTerm'] = buyingpower_allocation_ShortTerm
                trading_model_dict['total_budget'] = total_budget

                if 'buy_cross-0' in trading_model_dict['trigbees'].keys():
                    trigbees['buy_cross-0']['status'] = op_trigbee_bc
                    trigbees['buy_cross-0']['max_profit_waveDeviation'] = op_trigbee_max_profit_waveDeviation_bc
                    trigbees['buy_cross-0']['timeduration'] = op_trigbee_timeduration_bc
                    trigbees['buy_cross-0']['take_profit'] = op_trigbee_take_profit_bc
                    trigbees['buy_cross-0']['sellout'] = op_trigbee_sellout_bc
                    trigbees['buy_cross-0']['sell_trigbee_trigger'] = op_trigbee_sell_trigbee_trigger_bc
                    trigbees['buy_cross-0']['stagger_profits'] = op_stagger_profits_bc
                    trigbees['buy_cross-0']['scalp_profits']= op_scalp_profits_bc
                if 'sell_cross-0' in trading_model_dict['trigbees'].keys():
                    trigbees['sell_cross-0']['status'] = op_trigbee_sc
                    trigbees['sell_cross-0']['max_profit_waveDeviation'] = op_trigbee_max_profit_waveDeviation_sc
                    trigbees['sell_cross-0']['timeduration'] = op_trigbee_timeduration_sc
                    trigbees['sell_cross-0']['take_profit'] = op_trigbee_take_profit_sc
                    trigbees['sell_cross-0']['sellout'] = op_trigbee_sellout_sc
                    trigbees['sell_cross-0']['sell_trigbee_trigger'] = op_trigbee_sell_trigbee_trigger_sc
                    trigbees['sell_cross-0']['stagger_profits'] = op_stagger_profits_sc
                    trigbees['sell_cross-0']['scalp_profits']= op_scalp_profits_sc
                if 'ready_buy_cross' in trading_model_dict['trigbees'].keys():
                    trigbees['ready_buy_cross']['status'] = op_trigbee_rb
                    trigbees['ready_buy_cross']['max_profit_waveDeviation'] = op_trigbee_max_profit_waveDeviation_rb
                    trigbees['ready_buy_cross']['timeduration'] = op_trigbee_timeduration_rb
                    trigbees['ready_buy_cross']['take_profit'] = op_trigbee_take_profit_rb
                    trigbees['ready_buy_cross']['sellout'] = op_trigbee_sellout_rb
                    trigbees['ready_buy_cross']['sell_trigbee_trigger'] = op_trigbee_sell_trigbee_trigger_rb
                    trigbees['ready_buy_cross']['stagger_profits'] = op_stagger_profits_rb
                    trigbees['ready_buy_cross']['scalp_profits']= op_scalp_profits_rb
                
                trading_model_dict['trigbees'] = trigbees
                
                if len(df_sel) > 0:
                    star_original_dict = dict(zip(df['star'], df['status']))
                    star_update_dict = dict(zip(df_sel['star'], df_sel['star_status_update']))
                    star_dict = {**star_original_dict, **star_update_dict}
                    trading_model_dict['power_rangers'] = star_dict # 'power_rangers'
                
                st.write(trading_model_dict)
                app_req['trading_model_dict'] = trading_model_dict
                APP_requests['trading_models'].append(app_req)
                PickleData(pickle_file=PB_App_Pickle, data_to_store=APP_requests)
        
                # Save
                st.write(app_request_package)
                APP_requests['power_rangers'].append(app_request_package)
                APP_requests['power_rangers_lastupdate'] = datetime.datetime.now().astimezone(est)
                PickleData(pickle_file=PB_App_Pickle, data_to_store=APP_requests)
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
    
    grid_response = build_AGgrid_df(data=df, 
    reload_data=vars['reload_data'],
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
    
    st.write('macd', total_current_macd_tier, ': ', '{:,.2%}'.format(total_current_macd_tier/ 64))
    st.write('hist', total_current_hist_tier, ': ', '{:,.2%}'.format(total_current_hist_tier / 64))

    # for df_p in all_df:
    #     fig = df_plotchart(title=df_p.iloc[-1]['name'], df=df_p, y='profits', x=False, figsize=(14,7), formatme=False)
    #     st.write(fig)
        # graph
    
    return True







# """ if "__name__" == "__main__": """

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


KING = KINGME()
# stars = KING['stars']
pollen_theme = pollen_themes(KING=KING)


QUEEN = read_queensmind(prod)['queen']
POLLENSTORY = read_pollenstory()
APP_requests = ReadPickleData(pickle_file=PB_App_Pickle)
STORY_bee = QUEEN['queen']['conscience']['STORY_bee']
KNIGHTSWORD = QUEEN['queen']['conscience']['KNIGHTSWORD']
ANGEL_bee = QUEEN['queen']['conscience']['ANGEL_bee']


option3 = st.sidebar.selectbox("Always RUN", ('No', 'Yes'))
option = st.sidebar.selectbox("Dashboards", ('queen', 'charts', 'signal', 'pollenstory', 'app'))
st.sidebar.write("<<<('')>>>")
# st.header(option)


colors = QUEEN['queen_controls']['power_rangers']['1Minute_1Day']['mac_ranger']['buy_wave']['nuetral']
# st.write(colors)


if option == 'charts':
    # pollen = return_pollen()
    # run_charts(POLLENSTORY = POLLENSTORY)

    
    tickers_avail = list([set(i.split("_")[0] for i in POLLENSTORY.keys())][0])
    # tickers_avail.update({"all"})
    ticker_option = st.sidebar.selectbox("Tickers", tickers_avail, index=tickers_avail.index(["SPY" if "SPY" in tickers_avail else tickers_avail[0]][0]))
    st.markdown('<div style="text-align: center;">{}</div>'.format(ticker_option), unsafe_allow_html=True)

    ttframe_list = list(set([i.split("_")[1] + "_" + i.split("_")[2] for i in POLLENSTORY.keys()]))
    ttframe_list.append(["short_star", "mid_star", "long_star", "retire_star"])
    frame_option = st.sidebar.selectbox("ttframes", ttframe_list, index=ttframe_list.index(["1Minute_1Day" if "1Minute_1Day" in ttframe_list else ttframe_list[0]][0]))
    day_only_option = st.sidebar.selectbox('Show Today Only', ['no', 'yes'], index=['no'].index('no'))
    slope_option = st.sidebar.selectbox('Show Slopes', ['no', 'yes'], index=['no'].index('no'))
    wave_option = st.sidebar.selectbox('Show Waves', ['no', 'yes'], index=['no'].index('no'))
    fullstory_option = st.sidebar.selectbox('POLLENSTORY', ['no', 'yes'], index=['yes'].index('yes'))


    if frame_option == 'all':
        st.write("TDB")

    else:
        selections = [i for i in POLLENSTORY.keys() if i.split("_")[0] in ticker_option and i.split("_")[1] in frame_option]
        
        its_morphin_time_view(QUEEN=QUEEN, STORY_bee=STORY_bee, ticker=ticker_option)
        
        # st.write(selections[0])
        ticker_time_frame = selections[0]
        df = POLLENSTORY[ticker_time_frame].copy()
        # if df.iloc[-1]['open'] == 0:
        #     df = df.head(-1)
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

        if fullstory_option == 'yes':
            df_write = df.astype(str)
            st.dataframe(df_write)
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

            # st.write("waves")
            # waves = STORY_bee[ticker_time_frame]['waves']
            # st.write(waves)
        
        if option3 == "Yes":
            time.sleep(10)
            st.experimental_rerun()


if option == 'queen':
    col11, col22 = st.columns(2)
    with col11:
        stop_queenbee(APP_requests)
    tickers_avail = [set(i.split("_")[0] for i in STORY_bee.keys())][0]
    tickers_avail.update({"all"})
    tickers_avail_op = list(tickers_avail)
    ticker_option = st.sidebar.selectbox("Tickers", tickers_avail_op, index=tickers_avail_op.index('SPY'))
    st.markdown('<div style="text-align: center;">{}</div>'.format(ticker_option), unsafe_allow_html=True)
    ticker = ticker_option
    
    option_showaves = st.sidebar.selectbox("Show Waves", ('no', 'yes'), index=["no"].index("no"))

    return_total_profits(QUEEN=QUEEN)

    command_conscience_option = st.sidebar.selectbox("command conscience", ['yes', 'no'], index=["yes"].index("yes"))
    orders_table = st.sidebar.selectbox("orders_table", ['no', 'yes'], index=["no"].index("no"))
    today_day = datetime.datetime.now().day
    # with col22:
    #     st.write("current errors")
    # with col22:
    #     st.write(QUEEN["errors"])
    
    
    if command_conscience_option == 'yes':
        ORDERS = QUEEN['queen_orders']
        now_time = datetime.datetime.now().astimezone(est)
        all_trigs = {k: i['story']["alltriggers_current_state"] for (k, i) in STORY_bee.items() if len(i['story']["alltriggers_current_state"]) > 0 and (now_time - i['story']['time_state']).seconds < 33}

        st.write("<<all trigger bees>>")
        if len(all_trigs) > 0:
            df = pd.DataFrame(all_trigs.items())
            df = df.rename(columns={0: 'ttf', 1: 'trig'})
            df = df.sort_values('ttf')
            st.write(df)

        col1_a, col2_b, = st.columns(2)
        
        st.write('orders')

        new_title = '<p style="font-family:sans-serif; color:Black; font-size: 25px;">ERRORS</p>'
        st.markdown(new_title, unsafe_allow_html=True)
        error_orders = queen_orders_view(QUEEN=QUEEN, queen_order_state='error', return_all_cols=True)['df']
        error_orders = error_orders.astype(str)
        st.dataframe(error_orders)

        new_title = '<p style="font-family:sans-serif; color:Black; font-size: 25px;">SUBMITTED</p>'
        st.markdown(new_title, unsafe_allow_html=True)
        submitted_orders = queen_orders_view(QUEEN=QUEEN, queen_order_state='submitted')['df']
        submitted_orders = submitted_orders.astype(str)
        st.dataframe(submitted_orders)
        
        new_title = '<p style="font-family:sans-serif; color:Green; font-size: 25px;">RUNNING</p>'
        st.markdown(new_title, unsafe_allow_html=True)
        run_orders = queen_orders_view(QUEEN=QUEEN, queen_order_state='running', return_all_cols=True)['df']
        st.dataframe(run_orders)

        new_title = '<p style="font-family:sans-serif; color:Green; font-size: 25px;">RUNNING CLOSE</p>'
        st.markdown(new_title, unsafe_allow_html=True)
        runclose_orders = queen_orders_view(QUEEN=QUEEN, queen_order_state='running_close')['df']
        st.dataframe(runclose_orders)

 
        with col2_b:
            new_title = '<p style="font-family:sans-serif; color:Black; font-size: 33px;">memory</p>'
            st.markdown(new_title, unsafe_allow_html=True)
        

    if orders_table == 'yes':
        # main_orders_table = read_csv_db(db_root=db_root, tablename='main_orders', prod=prod)
        main_orders_table = pd.DataFrame(QUEEN['queen_orders'])
        st.dataframe(main_orders_table)

    st.write("QUEENS Collective CONSCIENCE")
    if ticker_option != 'all':
        # q = QUEEN["queen"]["conscience"]["STORY_bee"]["SPY_1Minute_1Day"]

        # View Stars
        its_morphin_time_view(QUEEN, STORY_bee, ticker)
        st.markdown('<div style="text-align: center;color:Blue; font-size: 33px;">{}</div>'.format("STARS IN HEAVEN"), unsafe_allow_html=True)
        st.dataframe(data=story_view(STORY_bee=STORY_bee, ticker=ticker_option)['df'], width=2000)
        ag_grid_main_build(df=story_view(STORY_bee=STORY_bee, ticker=ticker_option)['df'], 
        default=True, add_vars={'update_cols': False}, write_selection=False)
        # View Star and Waves
        ticker_storys = {k:v for (k,v) in STORY_bee.items() if k.split("_")[0] == ticker_option}
        # m2 = {k:v for (k,v) in KNIGHTSWORD.items() if k.split("_")[0] == ticker_option}

        # Analyze Waves
        st.markdown('<div style="text-align: center;">{}</div>'.format('analzye waves'), unsafe_allow_html=True)
        df = pd.DataFrame(analyze_waves(STORY_bee, ttframe_wave_trigbee=False)['df']) 
        df = df.astype(str)
        st.write(df)

        # Summary of all ticker_time_frames
        st.markdown('<div style="text-align: center;color:Purple; font-size: 33px;">{}</div>'.format("SUMMARY ALL WAVES"), unsafe_allow_html=True)
        st.markdown(new_title, unsafe_allow_html=True)
        df = pd.DataFrame(analyze_waves(STORY_bee, ttframe_wave_trigbee=False)['df_agg_view_return'])
        df = df.astype(str)
        st.write(df)
        
        st.markdown('<div style="text-align: center;color:Purple; font-size: 33px;">{}</div>'.format("TRIGBEE WAVES"), unsafe_allow_html=True)
        dict_list_ttf = analyze_waves(STORY_bee, ttframe_wave_trigbee=False)['d_agg_view_return']        

        for trigbee in dict_list_ttf[list(dict_list_ttf.keys())[0]]:
            ticker_selection = {k: v for k, v in dict_list_ttf.items() if ticker_option in k}
            buys = [data[trigbee] for k, data in ticker_selection.items()]
            df_buys = pd.concat(buys, axis=0)
            col_view = ['ticker_time_frame'] + [i for i in df_buys.columns if i not in 'ticker_time_frame']
            df_buys = df_buys[col_view]
            # st.write(trigbee)
            if 'buy' in trigbee:
                st.markdown('<div style="text-align: center;color:Green; font-size: 23px;">{}{}</div>'.format("trigbee : ", trigbee), unsafe_allow_html=True)
            else:
                st.markdown('<div style="text-align: center;color:Red; font-size: 23px;">{}{}</div>'.format("trigbee : ", trigbee), unsafe_allow_html=True)
            # df_buys["maxprofit"] = df_buys['maxprofit'].map("{:.2f}".format)
            st.dataframe(df_buys)

            # Top Winners 
            df_bestwaves = analyze_waves(STORY_bee, ttframe_wave_trigbee=df_buys['ticker_time_frame'].iloc[-1])['df_bestwaves']
            st.markdown('<div style="text-align: center;color:Purple; font-size: 20px;">{}{}{}</div>'.format("BEST WAVES : ", 'top: ', len(df_bestwaves)), unsafe_allow_html=True)
            st.dataframe(df_bestwaves)

        # ticker_selection = {k: v for k, v in dict_list_ttf.items() if ticker_option in k}
        # buys = [data['buy_cross-0'] for k, data in ticker_selection.items()]
        # df_buys = pd.concat(buys, axis=0)

        
        # [st.write(k, v) for k,v in v.items()]
        # df = pd.DataFrame(dict_list_ttf[ticker_option])
        # df = df.astype(str)
        # df = df.T
        # st.write(df)

        # d_agg_view_return[ticker_time_frame]["buy_cross-0"]
        # avail_trigbees = df.columns.to_list()
        # for trigbee in avail_trigbees:
        #     trigbee_wave = df[trigbee]

        def buzzz_linebreak(icon=">>>", size=15):
            line_break = str([icon for i in range(size)])
            return st.write(line_break)

        for ttframe, knowledge in ticker_storys.items():
            # with st.form(str(ttframe)):
            # WaveUp
            st.markdown('<div style="text-align: center;">{}</div>'.format("WAVE UP"), unsafe_allow_html=True)
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
            st.markdown('<div style="text-align: center;">{}</div>'.format("WAVE UP TODAY"), unsafe_allow_html=True)
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
            
            # view details
            st.write("VIEW TRANSPOSE")
            df = df.T
            st.dataframe(df)
            # agg_view = pd.DataFrame(agg_view)
            # agg_view = agg_view.astype(str)
            # st.dataframe(agg_view)

            st.write(ttframe)
            story_sort = knowledge['story']
            st.write(story_sort)
            
            if option_showaves.lower() == 'yes':
                st.write("waves story")
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
    ORDERS = [i for i in ORDERS if i['queen_order_state'] == 'completed']
    # queen shows only today orders
    now_ = datetime.datetime.now()
    orders_today = [i for i in ORDERS if i['datetime'].day == now_.day and i['datetime'].month == now_.month and i['datetime'].year == now_.year]
    orders_today = pd.DataFrame(orders_today)
    orders_today = orders_today.astype(str)
    st.write(orders_today)

    if option3 == "Yes":
        time.sleep(10)
        st.experimental_rerun()


if option == 'signal':
    betty_bee = ReadPickleData(os.path.join(db_root, 'betty_bee.pkl'))
    df_betty = pd.DataFrame(betty_bee)
    df_betty = df_betty.astype(str)
    st.write('betty_bee', df_betty)

    st.write(APP_requests['queen_controls'])

    save_signals = st.sidebar.selectbox('Send to Queen', ['beeaction', 'orders', 'controls', 'QueenOrders'], index=['controls'].index('controls'))
    col1, col2 = st.columns(2)

    ## SHOW CURRENT THEME
    with st.sidebar:
        # with st.echo():
            # st.write("theme>>>", QUEEN['collective_conscience']['theme']['current_state'])
        st.write("theme>>>", QUEEN['queen_controls']['theme'])


    if save_signals == 'controls':
        theme_list = list(pollen_theme.keys())

        with col1:
            st.write('Queen Controls')
            st.write(QUEEN['queen_controls'])
            stop_queenbee(APP_requests=APP_requests)
        with col2:
            st.write("HeartBeat")
            st.write(QUEEN['heartbeat'])
            refresh_queenbee_controls(APP_requests=APP_requests)

        contorls = list(QUEEN['queen_controls'].keys())
        control_option = st.selectbox('select control', contorls, index=contorls.index('theme'))

        update_QueenControls(APP_requests=APP_requests, control_option=control_option, theme_list=theme_list)


    if save_signals == 'QueenOrders':
        # Update run order
        show_errors_option = st.selectbox('show last error', ['no', 'yes'], index=['no'].index('no'))
        if show_errors_option == 'no':
            if len(QUEEN['queen_orders']) == 0:
                latest_queen_order = pd.DataFrame()
                orders_present = False
            else:
                latest_queen_order = QUEEN['queen_orders'][-1] # latest
                orders_present = True
        else:
            if len(QUEEN['queen_orders']) == 0:
                latest_queen_order = pd.DataFrame()
                orders_present = False
            else:
                # latest_queen_order = [i for i in QUEEN['queen_orders']] # latest
                # latest_queen_order = [latest_queen_order[-1]]
                latest_queen_order = [i for i in QUEEN['queen_orders'] if i['queen_order_state'] == 'error'][0]
                orders_present = True
        if orders_present:
            # latest_queen_order_error = [i for i in QUEEN['queen_orders'] if i['queen_order_status'] == 'error'] # latest
            # if latest_queen_order_error:
                # st.write(pd.DataFrame())
            # last_n_trades = pd.DataFrame([QUEEN['queen_orders'][-1], QUEEN['queen_orders'][-2], QUEEN['queen_orders'][-3]])
            # st.write(last_n_trades)
            all_orders = pd.DataFrame(QUEEN['queen_orders'])
            last3 = all_orders.iloc[-3:].astype(str)
            st.write(last3)
            c_order_input = st.text_input("client_order_id", latest_queen_order['client_order_id'])
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
                
   
    if save_signals == 'orders':
        show_app_req = st.selectbox('show app requests', ['yes', 'no'], index=['yes'].index('yes'))
        if show_app_req == 'yes':
            data = ReadPickleData(pickle_file=PB_App_Pickle)
            st.write("sell orders", data['sell_orders'])
            st.write("buy orders", data['buy_orders'])
        current_orders = QUEEN['queen_orders']
        running_orders = [i for i in current_orders if i['queen_order_state'] == 'running']
        
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
        # ticker_time_frame = [set(i for i in STORY_bee.keys())][0]
        ticker_time_frame = QUEEN['heartbeat']['available_tickers']

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


if option == 'app':
    st.write(APP_requests['queen_controls_reset'])
##### END ####