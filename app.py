import pandas as pd  # pip install pandas openpyxl
import plotly.express as px  # pip install plotly-express
import streamlit as st  # pip install streamlit
# QueenBee
import logging
from enum import Enum
from signal import signal
from symtable import Symbol
import time
import alpaca_trade_api as tradeapi
import asyncio
import os
import pandas as pd
import numpy as np
import pandas_ta as ta
import sys
from alpaca_trade_api.rest import TimeFrame, URL
from alpaca_trade_api.rest_async import gather_with_concurrency, AsyncRest
from dotenv import load_dotenv
import threading
from QueenHive import ReadPickleData
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

QUEEN = { # The Queens Mind
    'pollenstory': {}, # latest story
    'pollencharts': {}, # latest rebuild
    'pollencharts_nectar': {}, # latest charts with indicators
    'pollenstory_info': {}, # Misc Info,
    'self_last_modified' : datetime.datetime.now(),
    }

main_root = os.getcwd()
db_root = os.path.join(main_root, 'db')
# Client Tickers
src_root, db_dirname = os.path.split(db_root)
client_ticker_file = os.path.join(src_root, 'client_tickers.csv')
df_client = pd.read_csv(client_ticker_file, dtype=str)
client_symbols = df_client.tickers.to_list()

main_root = os.getcwd() 
db_root = os.path.join(main_root, 'db') 
# if queens_chess_piece.lower() == 'knight': # Read Bees Story
# Read chart story dat
st.header('QueenBee')
st.sidebar.write("WelcomeSide")
# option1 = st.selectbox("Dashboards", ('knight', 'Bishop', 'Castle'))
option = st.sidebar.selectbox("Dashboards", ('knight', 'bishop', 'castle'))
st.header(option)

if option == 'knight':
    symbol = st.sidebar.text_input("Jq_Name", value='SPY_1Minute_1Day', max_chars=33)
    image = Image.open(r'C:\Users\sstapinski\pollen\pollen\db\me.jpg')
    st.image(image, caption='Jq')
    castle = ReadPickleData(pickle_file=os.path.join(db_root, 'castle.pkl'))
    bishop = ReadPickleData(pickle_file=os.path.join(db_root, 'bishop.pkl'))  
    pollenstory = {**bishop['pollenstory'], **castle['pollenstory']} # combine daytrade and longterm info
    spy = pollenstory['SPY_1Minute_1Day']
    spy = pollenstory[symbol]

    hist_slope = spy[['symbol', 'nowdate', 'hist', 'hist_slope-3', 'hist_slope-6']].copy()
    df = hist_slope.tail(10)
    # my_df = my_df.sort_values(by=['col1','col2','col3'], ascending=[False, False, True])
    df = df.sort_values(by=['nowdate'], ascending=[False])
    st.subheader("Hists")
    st.dataframe(df)



# c = spy
# c2 = c[:120].copy()
# c3=c2[['hist','hist_sma-3','hist_slope-3', 'hist_slope-6']].copy()
# c=c2[['hist','hist_slope-3', 'hist_slope-6']].plot(figsize=(14,7))
# st.pyplot(c)

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