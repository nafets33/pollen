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
# from QueenHive import ReadPickleData
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
from PIL import Image
import mplfinance as mpf
import plotly.graph_objects as go


def ReadPickleData(pickle_file): 
    # for reading also binary mode is important try 3 times
    try:
        dbfile = open(pickle_file, 'rb')      
        db = pickle.load(dbfile) 
        dbfile.close()
        return db
    except Exception as e:
        try:
            time.sleep(.33)
            dbfile = open(pickle_file, 'rb')      
            db = pickle.load(dbfile) 
            dbfile.close()
            return db
        except Exception as e:
            try:
                time.sleep(.33)
                dbfile = open(pickle_file, 'rb')      
                db = pickle.load(dbfile) 
                dbfile.close()
                return db
            except Exception as e:
                print("CRITICAL ERROR logme", e)
                return False


prod = True
pd.options.mode.chained_assignment = None
est = pytz.timezone("US/Eastern")
load_dotenv()
# >>> initiate db directories
system = 'windows' #mac, windows
# if system != 'windows':
#     db_root = os.environ.get('db_root_mac')
# else:
#     db_root = os.environ.get('db_root_winodws')

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


def pollenstory():
    castle = ReadPickleData(pickle_file=os.path.join(db_root, 'castle.pkl'))
    bishop = ReadPickleData(pickle_file=os.path.join(db_root, 'bishop.pkl'))
    knight = ReadPickleData(pickle_file=os.path.join(db_root, 'knight.pkl'))
    pollenstory = {**bishop['bishop']['pollenstory'], **castle['castle']['pollenstory']} # combine daytrade and longterm info
    pollenstory = {**pollenstory, **knight}
    return pollenstory



def df_plotchart(title, df, y, figsize=(14,7)):
    st.markdown('<div style="text-align: center;">{}</div>'.format(title), unsafe_allow_html=True)
    df['date'] = df['date'].apply(lambda x: f'{x.month}{"-"}{x.day}{"_"}{x.hour}{":"}{x.minute}')
    return df.plot(x='date', y=y,figsize=figsize)


# if queens_chess_piece.lower() == 'knight': # Read Bees Story
# Read chart story dat
st.header('QueenBee')
st.sidebar.write("WelcomeSide")

st.markdown('<div style="text-align: center;">{}</div>'.format("buzz"), unsafe_allow_html=True)
st.markdown('<div style="text-align: left;">{}</div>'.format("buzzz"), unsafe_allow_html=True)
st.markdown('<div style="text-align: right;">{}</div>'.format("buzzzz"), unsafe_allow_html=True)
# st.markdown('<div style="text-align: justify;">Hello World!</div>', unsafe_allow_html=True)

st.button("ReRun")

bee_image = os.path.join(db_root, 'bee.jpg')
image = Image.open(bee_image)
st.image(image, caption='Jq', width=33)

# option1 = st.selectbox("Dashboards", ('knight', 'Bishop', 'Castle'))
option = st.sidebar.selectbox("Dashboards", ('test', 'knight', 'bishop', 'castle'))
st.header(option)

option2 = st.sidebar.selectbox("Tic", ('SPY', 'QQQ'))
st.markdown('<div style="text-align: center;">{}</div>'.format(option2), unsafe_allow_html=True)

option3 = st.sidebar.selectbox("Always RUN", ('Yes', 'No'))


if option == 'knight':
    # symbol = st.sidebar.text_input("Jq_Name", value='SPY_1Minute_1Day', max_chars=33)
    symbol = option2
    castle = ReadPickleData(pickle_file=os.path.join(db_root, 'castle.pkl'))
    bishop = ReadPickleData(pickle_file=os.path.join(db_root, 'bishop.pkl'))  
    pollenstory_resp = {**bishop['bishop']['pollenstory'], **castle['castle']['pollenstory']} # combine daytrade and longterm info
    # spy = pollenstory['SPY_1Minute_1Day']
    spy = pollenstory_resp[f'{symbol}{"_"}{"1Minute_1Day"}']


    c = spy
    df = spy
    df = df[:-1]  # test as last read doesn't have high & low
    c2 = c.set_index("timestamp_est")
    c3 = c2.tail(120)
    c4=c3[['close']].plot(figsize=(14,7))
    st.pyplot(c4.figure)

    # fig = go.Figure(data=[go.Candlestick(x=df['timestamp_est'],
    #                 open=df['open'],
    #                 high=df['high'],
    #                 low=df['low'],
    #                 close=df['close'])])
    # fig.update_xaxes(type='category')
    # fig.update_layout(height=600)

    # st.plotly_chart(fig, use_container_width=True)

    c4=c3[['macd','macd_slope-3', 'macd_slope-6']].plot(figsize=(10,7))
    st.pyplot(c4.figure)

    c4=c3[['hist','hist_slope-3', 'hist_slope-6']].plot(figsize=(10,7))
    st.pyplot(c4.figure)

    df = spy[['symbol', 'nowdate', 'macd_slope-3', 'macd_slope-6', 'hist', 'hist_slope-3', 'hist_slope-6', 'story_index']].copy()
    df = df.tail(30)
    # my_df = my_df.sort_values(by=['col1','col2','col3'], ascending=[False, False, True])
    df = df.sort_values(by=['story_index'], ascending=[False])
    # df = df.sort_index(axis = 1, ascending=True)
    st.subheader("Hists")
    st.dataframe(df)

    # subPlot() # plot multiple grpahs

    # df_google = df[df['Name'] == 'GOOGL'].copy()
    # spy = pollenstory_resp['SPY_1Day_1Year']
    # df = spy
    # df['date'] = df['timestamp_est']
    # # df = df[df['date'] > pd.to_datetime('2017-12-31')]
    # df = df.set_index('date')
    # title=df['name'].iloc[-1]
    # mpf.plot(df)


    
    full = spy.copy()
    title = full.iloc[-1]['name']
    full['date'] = full['timestamp_est'].apply(lambda x: f'{x.month}{"-"}{x.day}{"_"}{x.hour}{":"}{x.minute}')
    # full['date'] = full['timestamp_est'].astype(str)
    full=full[['close', 'date']].plot(x='date',figsize=(14,7))
    st.subheader(title)
    st.pyplot(full.figure)


    # x, y = mpf.plot(df,type='candle',volume=True, figsize=(15,10), title=title, returnfig=True)
    # # st.pyplot(x.figure)
    # st.pyplot(x)

    if option3 == "Yes":
        time.sleep(3)
        st.experimental_rerun()  ## rerun entire page



if option == 'test':
    pollenstory_resp = pollenstory()
    today_day = datetime.datetime.now().day
    
    df = pollenstory_resp['SPY_1Minute_1Day'] # test
    df['date'] = df['timestamp_est'] # test
    df = df.set_index('timestamp_est') # test

    # between certian times
    df_t = df.between_time('9:30', '12:00')
    df_t = df_t[df_t.index.day == today_day].copy() # remove yesterday
    chart = df_plotchart(title='mom_3', df=df_t, y='close_mom_3')
    st.pyplot(chart.figure)
    
    kn = pollenstory_resp['knight']
    bee_triggers = kn['bee_triggers']
    knights_word = bee_triggers['knights_word']
    knights_df = bee_triggers['knights_df']
    st.dataframe(knights_word)
    # queens conscience
        # {tickers: {},
        # orders: {},
        # conscience: {}}
    """ >what is your current macd state?
        >list all other current triggers
        >determine trade consideration logic
     """
    token = [i for i in knights_word.keys() if "1Minute" in i]  # get all 1 day current trigger state
    QUEENS_CONSCIENCE = {
        'daytrader': {}
    }
    for ticker_time_frame in token:
        # ticker, _time, _frame = ticker_time_frame.split("_")
        QUEENS_CONSCIENCE['daytrader'][ticker_time_frame] = {}
        k_word = knights_word[ticker_time_frame]
        k_df = knights_df[ticker_time_frame]
        # get all current knowledge to consider trade
        
        time_state = k_df['timestamp_est'].iloc[-1] # current time
        QUEENS_CONSCIENCE['daytrader'][ticker_time_frame]['time_state'] = time_state
        
        QUEENS_CONSCIENCE['daytrader'][ticker_time_frame]['macd_state'] = k_df['macd_cross'].iloc[-1]
        
        macd_state_side = QUEENS_CONSCIENCE['daytrader'][ticker_time_frame]['macd_state'].split("_")[0] # buy/sell
        QUEENS_CONSCIENCE['daytrader'][ticker_time_frame]['macd_state_side'] = macd_state_side
        
        prior_macd_df = k_df[~k_df['macd_cross'].str.contains(macd_state_side)].copy()
        QUEENS_CONSCIENCE['daytrader'][ticker_time_frame]['prior_macd_state_time'] = prior_macd_df['timestamp_est'].iloc[-1] # filter not current state

        QUEENS_CONSCIENCE['daytrader'][ticker_time_frame]['time_since_macd_change'] = k_df['story_index'].iloc[-1] - prior_macd_df['story_index'].iloc[-1]
        
        QUEENS_CONSCIENCE['daytrader'][ticker_time_frame]['alltriggers_current_state'] = [k for (k,v) in k_word.items() if v['lastmodified'].day == time_state.day and v['lastmodified'].hour == time_state.hour and v['lastmodified'].minute == time_state.minute]

        """ do you want to buy anything my friend """




    

    df_ = pollenstory_resp['SPY_1Minute_1Day']
    df_['date'] = df_['timestamp_est'] # add as new col
    df_ = df_.set_index('timestamp_est')
    df_ = df_[df_.index.day == today_day].copy() # remove yesterday
    chart = df_plotchart(title='1day', df=df_, y='close')
    st.pyplot(chart.figure)

    df_ = pollenstory_resp['SPY_5Minute_5Day']
    df_['date'] = df_['timestamp_est'] # add as new col
    chart = df_plotchart(title='5day', df=df_, y='close')
    st.pyplot(chart.figure)
    df_ = pollenstory_resp['SPY_5Minute_5Day']
    df_['date'] = df_['timestamp_est'] # add as new col
    chart = df_plotchart(title='5day-macd', df=df_, y=['macd', 'signal', 'hist'])
    st.pyplot(chart.figure)


    # between certian times
    df_t = df.between_time('9:30', '12:00')
    df_t = df_t[df_t.index.day == today_day].copy() # remove yesterday

    df_t['prior_slopedelta'] = (df_t['macd_slope-3'] - df_t['macd_slope-3'].shift(1)).fillna(0)

    p=df_t[['close']].plot(figsize=(14,7))
    st.pyplot(p.figure)
    p=df_t[['macd', 'macd_slope-3', 'prior_slopedelta']].plot(figsize=(14,7))
    st.pyplot(p.figure)

    # test candlestick chart
    df = pollenstory_resp['SPY_1Minute_1Day']
    df['date'] = df['timestamp_est'] # add as new col
    df = df.head(-1) # drop current Min until you fix upstream
    fig = go.Figure(data=[go.Candlestick(x=df['date'],
                    open=df['open'],
                    high=df['high'],
                    low=df['low'],
                    close=df['close'])])
    fig.update_xaxes(type='category')
    fig.update_layout(height=600)
    st.markdown('<div style="text-align: center;">{}</div>'.format(df['name'].iloc[-1]), unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True)

    if option3 == "Yes":
        time.sleep(3)
        st.experimental_rerun()

    # full = spy
    # title = full.iloc[-1]['name']
    # full = full.set_index('story_index')
    # full=full[['close']].plot(figsize=(14,7))
    # st.subheader(title)
    # st.pyplot(full.figure)










# st.text('Fixed width text')
# st.markdown('_Markdown_') # see *
# st.latex(r''' e^{i\pi} + 1 = 0 ''')
# st.write('Most objects') # df, err, func, keras!
# st.write(['st', 'is <', 3]) # see *
# st.title('My title')
# st.code('for i in range(8): foo()')
# st.json({
#      'foo': 'bar',
#      'baz': 'boz',
#      'stuff': [
#          'stuff 1',
#          'stuff 2',
#          'stuff 3',
#          'stuff 5',
#      ],
#  })

# import random
# while True:
#     g = st.subheader('me')
# plot chart
# sales_by_hour = df_selection.groupby(by=["hour"]).sum()[["Total"]]
# fig_hourly_sales = px.bar(
#     sales_by_hour,
#     x=sales_by_hour.index,
#     y="Total",
#     title="<b>Sales by hour</b>",
#     color_discrete_sequence=["#0083B8"] * len(sales_by_hour),
#     template="plotly_white",
# )
#  re