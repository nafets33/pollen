from asyncio import streams
from cgitb import reset
from datetime import datetime
import logging
from enum import Enum
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
import datetime
import pytz
from typing import Callable
import pickle
import random
from tqdm import tqdm
from stocksymbol import StockSymbol
import requests
from collections import defaultdict
import talib
from scipy import stats
import shutil

queens_chess_piece = os.path.basename(__file__)

main_root = os.getcwd()
db_root = os.path.join(main_root, 'db')


def init_logging(queens_chess_piece, db_root, loglog_newfile=False):
    log_dir = dst = os.path.join(db_root, 'logs')
    if os.path.exists(dst) == False:
        os.mkdir(dst)
    log_name = f'{"log_"}{queens_chess_piece}{".log"}'
    log_file = os.path.join(os.getcwd(), log_name)
    if os.path.exists(log_file) == False:
        logging.basicConfig(filename=f'{"log_"}{queens_chess_piece}{".log"}',
                            filemode='a',
                            format='%(asctime)s:%(name)s:%(levelname)s: %(message)s',
                            datefmt='%m/%d/%Y %I:%M:%S %p',
                            level=logging.INFO)
    else:
        if loglog_newfile:
            # copy log file to log dir & del current log file
            datet = datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S_%p')
            dst_path = os.path.join(log_dir, f'{log_name}{"_"}{datet}{".log"}')
            shutil.copy(log_file, dst_path) # only when you want to log your log files
            os.remove(log_file)
        else:
            logging.basicConfig(filename=f'{"log_"}{queens_chess_piece}{".log"}',
                                filemode='a',
                                format='%(asctime)s:%(name)s:%(levelname)s: %(message)s',
                                datefmt='%m/%d/%Y %I:%M:%S %p',
                                level=logging.INFO)
        return True

init_logging(queens_chess_piece, db_root)


# log_dir = dst = os.path.join(db_root, 'logs')
# if os.path.exists(dst) == False:
#     os.mkdir(dst)
# log_name = f'{"log_"}{queens_chess_piece}{".log"}'
# log_file = os.path.join(os.getcwd(), log_name)
# if os.path.exists(log_file) == False:
#     logging.basicConfig(filename=f'{"log_"}{queens_chess_piece}{".log"}',
#                         filemode='a',
#                         format='%(asctime)s:%(name)s:%(levelname)s: %(message)s',
#                         datefmt='%m/%d/%Y %I:%M:%S %p',
#                         level=logging.INFO)
# else:
#     # copy log file to log dir & del current log file
#     datet = datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S_%p')
#     dst_path = os.path.join(log_dir, f'{log_name}{"_"}{datet}{".log"}')
#     # shutil.copy(log_file, dst_path) # only when you want to log your log files
#     # os.remove(log_file)
#     logging.basicConfig(filename=f'{"log_"}{queens_chess_piece}{".log"}',
#                         filemode='a',
#                         format='%(asctime)s:%(name)s:%(levelname)s: %(message)s',
#                         datefmt='%m/%d/%Y %I:%M:%S %p',
#                         level=logging.INFO)

est = pytz.timezone("America/New_York")

system = 'windows' #mac, windows
load_dotenv()


exclude_conditions = [
    'B','W','4','7','9','C','G','H','I','M','N',
    'P','Q','R','T','U','V','Z'
]

# keys
api_key_id = os.environ.get('APCA_API_KEY_ID')
api_secret = os.environ.get('APCA_API_SECRET_KEY')
base_url = "https://api.alpaca.markets"


def return_api_keys(base_url, api_key_id, api_secret, prod=True):

    # api_key_id = os.environ.get('APCA_API_KEY_ID')
    # api_secret = os.environ.get('APCA_API_SECRET_KEY')
    # base_url = "https://api.alpaca.markets"
    # base_url_paper = "https://paper-api.alpaca.markets"
    # feed = "sip"  # change to "sip" if you have a paid account
    
    if prod == False:
        rest = AsyncRest(key_id=api_key_id,
                    secret_key=api_secret)

        api = tradeapi.REST(key_id=api_key_id,
                    secret_key=api_secret,
                    base_url=URL(base_url), api_version='v2')
    else:
        rest = AsyncRest(key_id=api_key_id,
                            secret_key=api_secret)

        api = tradeapi.REST(key_id=api_key_id,
                            secret_key=api_secret,
                            base_url=URL(base_url), api_version='v2')
    return [{'rest': rest, 'api': api}]

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

"""# Dates """
current_day = api.get_clock().timestamp.date().isoformat()
trading_days = api.get_calendar()
trading_days_df = pd.DataFrame([day._raw for day in trading_days])

start_date = datetime.datetime.now().strftime('%Y-%m-%d')
end_date = datetime.datetime.now().strftime('%Y-%m-%d')

""" VAR >>>>>>>>>>VAR >>>>>>>>>>VAR >>>>>>>>>>VAR >>>>>>>>>>VAR >>>>>>>>>>VAR >>>>>>>>>>"""
def read_pollenstory(): # return combined dataframes
    castle = ReadPickleData(pickle_file=os.path.join(db_root, 'castle.pkl'))
    bishop = ReadPickleData(pickle_file=os.path.join(db_root, 'bishop.pkl'))
    pollenstory = {**bishop['bishop']['pollenstory'], **castle['castle']['pollenstory']} # combine daytrade and longterm info
    return pollenstory


def read_queensmind(): # return active story workers
    queen = ReadPickleData(pickle_file=os.path.join(db_root, 'queen.pkl'))
    castle = ReadPickleData(pickle_file=os.path.join(db_root, 'castle.pkl'))['castle']
    bishop = ReadPickleData(pickle_file=os.path.join(db_root, 'bishop.pkl'))['bishop']
    # knight = ReadPickleData(pickle_file=os.path.join(db_root, 'knight.pkl'))
    STORY_bee = {**bishop['conscience']['STORY_bee'], **castle['conscience']['STORY_bee']}
    knightsword = {**bishop['conscience']['knightsword'], **castle['conscience']['knightsword']}
    
    return {'queen': queen, 'bishop': bishop, 'castle': castle, 'STORY_bee': STORY_bee, 'knightsword': knightsword}

""" STORY: I want a dict of every ticker and the chart_time TRADE buy/signal weights """
### Story
# trade closer to ask price .... sellers closer to bid .... measure divergence from bid/ask to give weight
def pollen_story(pollen_nectar, QUEEN, queens_chess_piece):
    # where is max and depending on which time consider different weights of buy...
    # define weights in global and do multiple weights for different scenarios..
    # 1. 1 Month Leads + 3 + 6 month lead the 1 & 5 day...
    # long term uses 1ry and reverse leading 6 + 3 + 1

    # MACD momentum from past N times/days
    # TIME PAST SINCE LAST HIGH TO LOW to change weight & how much time passed since tier cross last high?   
    # how long since last max/min value reached (reset time at +- 2)    

    # >/ create ranges for MACD & RSI 4-3, 70-80, or USE Prior MAX&Low ...
    # >/ what current macd tier values in comparison to max/min
    s = datetime.datetime.now()
    story = {}
    ANGEl_bee = {} # add to QUEENS mind
    STORY_bee = {} 
    # CHARLIE_bee = {}  # holds all ranges for ticker and passes info into df
    betty_bee = {}  
    macd_tier_range = 33
    knights_sight_word = {}
    # knight_sight_df = {}

    for ticker_time_frame, df_i in pollen_nectar.items(): # CHARLIE_bee: # create ranges for MACD & RSI 4-3, 70-80, or USE Prior MAX&Low ...
        # CHARLIE_bee[ticker_time_frame] = {}
        ANGEl_bee[ticker_time_frame] = {}
        STORY_bee[ticker_time_frame] = {}
        
        df = df_i.fillna(0).copy()
        df = df.reset_index(drop=True)
        df['story_index'] = df.index
        df_len = len(df)
        df['nowdate'] = df['timestamp_est'].apply(lambda x: f'{x.hour}{":"}{x.minute}{":"}{x.second}')
        mac_world = {
        'macd_high': df['macd'].max(),
        'macd_low': df['macd'].min(),
        'signal_high': df['signal'].max(),
        'signal_low': df['signal'].min(),
        'hist_high': df['hist'].max(),
        'hist_low': df['hist'].min(),
        }

        # mac cross
        df = mark_macd_signal_cross(df=df)

        resp = knight_sight(df=df)
        df = resp['df']
        knights_word = resp['bee_triggers']
        knights_sight_word[ticker_time_frame] = knights_word
        # knight_sight_df[ticker_time_frame] = df_knight
        
        # # return degree angle 0, 45, 90
        try:
            var_list = ['macd', 'hist', 'signal', 'close', 'rsi_ema']
            var_timeframes = [3, 6, 8, 10, 25, 33]
            for var in var_list:
                for t in var_timeframes:
                    # apply rollowing angle
                    if df_len >= t:
                        x = df.iloc[df_len - t:df_len][var].to_list()
                        y = [1, 2]
                        name = f'{var}{"-"}{"Degree"}{"--"}{str(t)}'
                        ANGEl_bee[ticker_time_frame][name] = return_degree_angle(x, y)
        except Exception as e:
            msg=(e,"--", print_line_of_error(), "--", ticker_time_frame, "--ANGEL_bee")
            logging.error(msg)

        # add close price momentum
        try:
            close = df['close']
            df['close_mom_3'] = talib.MOM(close, timeperiod=3).fillna(0)
            df['close_mom_6'] = talib.MOM(close, timeperiod=6).fillna(0)
        except Exception as e:
            msg=(e,"--", print_line_of_error(), "--", ticker_time_frame)
            logging.error(msg)
        
        # devation from vwap
        df['vwap_deviation'] = df['close'] - df['vwap_original']

        
        # knights_word = knights_word[ticker_time_frame]
        # get all current knowledge to consider trade
        
        time_state = df['timestamp_est'].iloc[-1] # current time
        STORY_bee[ticker_time_frame]['time_state'] = time_state
        
        macd_state = df['macd_cross'].iloc[-1]
        STORY_bee[ticker_time_frame]['macd_state'] = macd_state
        
        macd_state_side = STORY_bee[ticker_time_frame]['macd_state'].split("_")[0] # buy/sell
        STORY_bee[ticker_time_frame]['macd_state_side'] = macd_state_side
        
        prior_macd_df = df[~df['macd_cross'].str.contains(macd_state_side)].copy()
        prior_macd_state_time = prior_macd_df['timestamp_est'].iloc[-1] # filter not current state
        STORY_bee[ticker_time_frame]['prior_macd_state_time'] = prior_macd_state_time

        time_since_macd_change = (df['story_index'].iloc[-1] - prior_macd_df['story_index'].iloc[-1]) -1
        STORY_bee[ticker_time_frame]['time_since_macd_change'] = time_since_macd_change
        
        STORY_bee[ticker_time_frame]['alltriggers_current_state'] = [k for (k,v) in knights_word.items() if v['lastmodified'].day == time_state.day and v['lastmodified'].hour == time_state.hour and v['lastmodified'].minute == time_state.minute]

        # count number of Macd Crosses
        # df['macd_cross_running_count'] = np.where((df['macd_cross'] == 'buy_cross-0') | (df['macd_cross'] == 'sell_cross-0'), 1, 0)
        today_df = df[df['timestamp_est'] > (datetime.datetime.now().replace(hour=1, minute=1, second=1)).isoformat()].copy()
        STORY_bee[ticker_time_frame]['macd_cross_count'] = {
            'buy_cross_total_running_count': sum(np.where(df['macd_cross'] == 'buy_cross-0',1,0)),
            'sell_cross_totalrunning_count' : sum(np.where(df['macd_cross'] == 'sell_cross-0',1,0)),
            'buy_cross_todays_running_count': sum(np.where(today_df['macd_cross'] == 'buy_cross-0',1,0)),
            'sell_cross_todays_running_count' : sum(np.where(today_df['macd_cross'] == 'sell_cross-0',1,0))
        }
        # # add timeblocks [9:30 - 10, 10-12, 12-1, 1-3, 3-4]:: NOT SURE ABOUT TIMEBLOCK YET?
        # def add_timeblock(dt):
        #     if dt.hour > 9 and dt.hour < 10:
        #         return 1
        #     elif dt.hour == 10 and dt.hour < 12:
        #         return 2
        #     elif dt.hour == 12 and dt.hour < 1 
        # df['timeblock'] = 

        # add to story
        df['chartdate'] = df['timestamp_est'] # add as new col
        df['name'] = ticker_time_frame
        story[ticker_time_frame] = df
        # ticker, _time, _frame = ticker_time_frame.split("_")

        
        # add momentem ( when macd < signal & past 3 macds are > X Value or %)
        
        # when did macd and signal share same tier?
    
    # Give to the Queen
    # QUEEN[queens_chess_piece]['conscience']['ANGEl_bee'] = ANGEl_bee
    # QUEEN[queens_chess_piece]['conscience']['knightsword'] = knights_sight_word
    # QUEEN[queens_chess_piece]['conscience']['pollenstory'] = STORY_bee

    e = datetime.datetime.now()
    print("pollen_story", str((e - s)) + ": " + datetime.datetime.now().strftime("%A, %d. %B %Y %I:%M:%S%p"))
    return {'pollen_story': story, 'conscience': {'ANGEl_bee': ANGEl_bee, 'knightsword': knights_sight_word, 'STORY_bee': STORY_bee  } }


def knight_sight(df): # adds all triggers to dataframe
    # ticker_time_frame = df['name'].iloc[-1]
    # trigger_dict = {ticker_time_frame: {}}
    trigger_dict_info = {}
    trigger_dict = {}
    
    # >>> ready for cross trigger: 
    # current macd = sell, & 
    # macd signal deviation "very close" &
    # hist slope is up

    # Mac crosses
    trigger = 'buy_cross-0'
    df[trigger] = np.where(
        (df['macd_cross'].str.contains("buy_cross-0")==True)
        ,"bee", 'nothing')
    bee_df = df[df[trigger] == 'bee'].copy()
    if len(bee_df) > 0:
        trigger_dict[trigger] = {}
        trigger_dict[trigger]['lastmodified'] = bee_df['timestamp_est'].iloc[-1]
    trigger = 'sell_cross-0'
    df[trigger] = np.where(
        (df['macd_cross'].str.contains("sell_cross-0")==True)
        ,"bee", 'nothing')
    bee_df = df[df[trigger] == 'bee'].copy()
    if len(bee_df) > 0:
        trigger_dict[trigger] = {}
        trigger_dict[trigger]['lastmodified'] = bee_df['timestamp_est'].iloc[-1]
    
    # Mac is very LOW and we are in buy cross
    trigger = 'buy_RED_tier-1_macdcross'
    df[trigger] = np.where(
        (df['macd_cross'].str.contains("buy")==True) & # is not in BUY cycle
        ((df['macd'] < 0) & (df['macd'] > -.3))
        ,"bee", 'nothing')
    bee_df = df[df[trigger] == 'bee'].copy()
    if len(bee_df) > 0:
        trigger_dict[trigger] = {}
        trigger_dict[trigger]['lastmodified'] = bee_df['timestamp_est'].iloc[-1]

    trigger = 'buy_RED_tier-2_macdcross'
    df[trigger] = np.where(
        (df['macd_cross'].str.contains("buy")==True) & # is not in BUY cycle
        ((df['macd'] < -.3) & (df['macd'] > -.5))
        ,"bee", 'nothing')
    bee_df = df[df[trigger] == 'bee'].copy()
    if len(bee_df) > 0:
        trigger_dict[trigger] = {}
        trigger_dict[trigger]['lastmodified'] = bee_df['timestamp_est'].iloc[-1]

    trigger = 'buy_RED_tier-3_macdcross'
    df[trigger] = np.where(
        (df['macd_cross'].str.contains("buy")==True) & # is not in BUY cycle
        ((df['macd'] < -.5) & (df['macd'] > -.1))
        ,"bee", 'nothing')
    bee_df = df[df[trigger] == 'bee'].copy()
    if len(bee_df) > 0:
        trigger_dict[trigger] = {}
        trigger_dict[trigger]['lastmodified'] = bee_df['timestamp_est'].iloc[-1]

    trigger = 'buy_RED_tier-4_macdcross'
    df[trigger] = np.where(
        (df['macd_cross'].str.contains("buy")==True) & # is not in BUY cycle
        ((df['macd'] < -.1) & (df['macd'] > -.15))
        ,"bee", 'nothing')
    bee_df = df[df[trigger] == 'bee'].copy()
    if len(bee_df) > 0:
        trigger_dict[trigger] = {}
        trigger_dict[trigger]['lastmodified'] = bee_df['timestamp_est'].iloc[-1]

    trigger = 'buy_RED_tier-5_macdcross'
    df[trigger] = np.where(
        (df['macd_cross'].str.contains("buy")==True) & # is not in BUY cycle
        (df['macd'] < -.15)
        ,"bee", 'nothing')
    bee_df = df[df[trigger] == 'bee'].copy()
    if len(bee_df) > 0:
        trigger_dict[trigger] = {}
        trigger_dict[trigger]['lastmodified'] = bee_df['timestamp_est'].iloc[-1]

    # Mac is very LOW and we are in buy cross
    trigger = 'buy_high-macdcross'
    df[trigger] = np.where(
        (df['macd_cross'].str.contains("buy")==True) & # is not in BUY cycle
        (df['macd'] < -.1)
        ,"bee", 'nothing')
    bee_df = df[df[trigger] == 'bee'].copy()
    if len(bee_df) > 0:
        trigger_dict[trigger] = {}
        trigger_dict[trigger]['lastmodified'] = bee_df['timestamp_est'].iloc[-1]

    # Mac is very LOW and we are in buy cross
    trigger = 'buy_high-macdcross'
    df[trigger] = np.where(
        (df['macd_cross'].str.contains("buy")==True) & # is not in BUY cycle
        (df['macd'] < -.1)
        ,"bee", 'nothing')
    bee_df = df[df[trigger] == 'bee'].copy()
    if len(bee_df) > 0:
        trigger_dict[trigger] = {}
        trigger_dict[trigger]['lastmodified'] = bee_df['timestamp_est'].iloc[-1]
    
    # Mac is very High and we are in a Sell Cross
    trigger = 'sell_high-macdcross'
    df[trigger] = np.where(
        (df['macd_cross'].str.contains("sell")==True) &
        (df['macd'] > 1)
        ,"bee", 'nothing')
    bee_df = df[df[trigger] == 'bee'].copy()
    if len(bee_df) > 0:
        trigger_dict[trigger] = {}
        trigger_dict[trigger]['lastmodified'] = bee_df['timestamp_est'].iloc[-1]

    # Mac is very High and the prior hist slow was steep and we are not in a Sell CROSS Cycle Yet
    trigger = 'sell_high-macdcross'
    df[trigger] = np.where(
        (df['macd_cross'].str.contains("sell_hold")==False) & # is not in Sell cycle
        (df['macd'] > 1.5) &
        (df['macd_slope-3'] < .1) &
        ((df['hist_slope-3'] < .33) |(df['hist_slope-6'] < .10))
        ,"bee", 'nothing')
    bee_df = df[df[trigger] == 'bee'].copy()
    if len(bee_df) > 0:
        trigger_dict[trigger] = {}
        trigger_dict[trigger]['lastmodified'] = bee_df['timestamp_est'].iloc[-1]


    return {"df": df, "bee_triggers": trigger_dict}


def mark_macd_signal_cross(df):  #return df: Mark the signal macd crosses 
    
    # running totals 
    try:
        m=df['macd'].to_list()
        s=df['signal'].to_list()
        prior_cross = None
        cross_list=[]
        c = 0  # count which side of trade you are on (c brings deveations from prior cross)
        buy_c = 0
        sell_c = 0
        for i, macdvalue in enumerate(m):
            if i != 0:
                prior_mac = m[i-1]
                prior_signal = s[i-1]
                now_mac = macdvalue
                now_signal = s[i]
                if now_mac > now_signal and prior_mac <= prior_signal:
                    cross_list.append(f'{"buy_cross"}{"-"}{0}')
                    c = 0
                    prior_cross = 'buy'
                    buy_c += 1
                elif now_mac < now_signal and prior_mac >= prior_signal:
                    cross_list.append(f'{"sell_cross"}{"-"}{0}')
                    c = 0
                    prior_cross = 'sell'
                    sell_c += 1
                else:
                    if prior_cross:
                        if prior_cross == 'buy':
                            c+=1
                            cross_list.append(f'{"buy_hold"}{"-"}{c}')
                        else:
                            c+=1
                            cross_list.append(f'{"sell_hold"}{"-"}{c}')
                    else:
                        cross_list.append(f'{"hold"}{"-"}{0}')
            else:
                cross_list.append(f'{"hold"}{"-"}{0}')
        df2 = pd.DataFrame(cross_list, columns=['macd_cross'])
        df_new = pd.concat([df, df2], axis=1)
        return df_new
    except Exception as e:
        msg=(e,"--", print_line_of_error(), "--", 'macd_cross')
        logging.critical(msg)     


def return_degree_angle(x, y): #
    # 45 degree angle
    # x = [1, 2, 3]
    # y = [1,2]

    #calculate
    e = np.math.atan2(y[-1] - y[0], x[-1] - x[0])
    degree = np.degrees(e)

    return degree

### BARS
def return_bars(symbol, timeframe, ndays, trading_days_df, sdate_input=False, edate_input=False):
    try:
        s = datetime.datetime.now()
        error_dict = {}
        # ndays = 0 # today 1=yesterday...  # TEST
        # timeframe = "1Minute" #"1Day" # "1Min"  "5Minute" # TEST
        # symbol = 'SPY'  # TEST
        # current_day = api.get_clock().timestamp.date().isoformat()  # TEST MOVED TO GLOBAL
        # trading_days = api.get_calendar()  # TEST MOVED TO GLOBAL
        # trading_days_df = pd.DataFrame([day._raw for day in trading_days])  # TEST MOVED TO GLOBAL
        # est = pytz.timezone("US/Eastern") # GlovalVar

        try:
            # Fetch bars for prior ndays and then add on today
            # s_fetch = datetime.datetime.now()
            if edate_input != False:
                end_date = edate_input
            else:
                end_date = datetime.datetime.now().strftime("%Y-%m-%d")
            
            if sdate_input != False:
                start_date = sdate_input
            else:
                if ndays == 0:
                    start_date = datetime.datetime.now().strftime("%Y-%m-%d")
                else:
                    start_date = trading_days_df.query('date < @current_day').tail(ndays).head(1).date

            # symbol_n_days = trading_days_df.query('date < @current_day').tail(ndays).tail(1)
            symbol_data = api.get_bars(symbol, timeframe=timeframe,
                                        start=start_date,
                                        end=end_date, 
                                        adjustment='all').df

            # e_fetch = datetime.datetime.now()
            # print('symbol fetch', str((e_fetch - s_fetch)) + ": " + datetime.datetime.now().strftime('%Y-%m-%d %H:%M'))
            if len(symbol_data) == 0:
                error_dict[symbol] = {'msg': 'no data returned', 'time': time}
                return [False, error_dict]
        except Exception as e:
            # print(" log info")
            error_dict[symbol] = e   

        # set index to EST time
        symbol_data['index_timestamp'] = symbol_data.index
        symbol_data['timestamp_est'] = symbol_data['index_timestamp'].apply(lambda x: x.astimezone(est))
        del symbol_data['index_timestamp']
        # symbol_data['timestamp'] = symbol_data['timestamp_est']
        # symbol_data = symbol_data.reset_index()
        symbol_data = symbol_data.set_index('timestamp_est')
        # del symbol_data['timestamp']
        # symbol_data['timestamp_est'] = symbol_data.index
        symbol_data['symbol'] = symbol

        # Make two dataframes one with just market hour data the other with after hour data
        if "day" in timeframe:
            market_hours_data = symbol_data  # keeping as copy since main func will want to return markethours
            after_hours_data =  None
        else:
            market_hours_data = symbol_data.between_time('9:30', '16:00')
            market_hours_data = market_hours_data.reset_index()
            after_hours_data =  symbol_data.between_time('16:00', '9:30')
            after_hours_data = after_hours_data.reset_index()          

        e = datetime.datetime.now()
        # print(str((e - s)) + ": " + datetime.datetime.now().strftime('%Y-%m-%d %H:%M'))
        # 0:00:00.310582: 2022-03-21 14:44 to return day 0
        # 0:00:00.497821: 2022-03-21 14:46 to return 5 days
        return [True, symbol_data, market_hours_data, after_hours_data]
    # handle error
    except Exception as e:
        print("sending email of error", e)
# r = return_bars(symbol='SPY', timeframe='1Minute', ndays=0, trading_days_df=trading_days_df)

def return_bars_list(ticker_list, chart_times):
    try:
        s = datetime.datetime.now()
        # ticker_list = ['SPY', 'QQQ']
        # chart_times = {
        #     "1Minute_1Day": 0, "5Minute_5Day": 5, "30Minute_1Month": 18, 
        #     "1Hour_3Month": 48, "2Hour_6Month": 72, 
        #     "1Day_1Year": 250
        #     }
        return_dict = {}
        error_dict = {}

        try:
            for charttime, ndays in chart_times.items():
                timeframe=charttime.split("_")[0] # '1Minute_1Day'
                # if timeframe.lower() == '1minute':
                #     start_date = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y-%m-%d") # get yesterdays trades as well
                # else:
                #     start_date = datetime.datetime.now().strftime("%Y-%m-%d")
                start_date = trading_days_df.query('date < @current_day').tail(ndays).head(1).date
                end_date = datetime.datetime.now().strftime("%Y-%m-%d")
                symbol_data = api.get_bars(ticker_list, timeframe=timeframe,
                                            start=start_date,
                                            end=end_date,
                                            adjustment='all').df
                
                # set index to EST time
                symbol_data['index_timestamp'] = symbol_data.index
                symbol_data['timestamp_est'] = symbol_data['index_timestamp'].apply(lambda x: x.astimezone(est))
                del symbol_data['index_timestamp']
                # symbol_data['timestamp'] = symbol_data['timestamp_est']
                symbol_data = symbol_data.reset_index(drop=True)
                # symbol_data = symbol_data.set_index('timestamp')
                # del symbol_data['timestamp']
                # symbol_data['timestamp_est'] = symbol_data.index
                return_dict[charttime] = symbol_data

            # e_fetch = datetime.datetime.now()
            # print('symbol fetch', str((e_fetch - s_fetch)) + ": " + datetime.datetime.now().strftime('%Y-%m-%d %H:%M'))
            if len(symbol_data) == 0:
                error_dict[ticker_list] = {'msg': 'no data returned', 'time': time}
                return [False, error_dict]
        except Exception as e:
            # print(" log info")
            error_dict[ticker_list] = e      

        e = datetime.datetime.now()
        # print(str((e - s)) + ": " + datetime.datetime.now().strftime('%Y-%m-%d %H:%M'))
        # 0:00:00.310582: 2022-03-21 14:44 to return day 0
        # 0:00:00.497821: 2022-03-21 14:46 to return 5 days
        return [True, return_dict]
    # handle error
    except Exception as e:
        print("sending email of error", e)
        return [False, e]
# r = return_bars_list(ticker_list, chart_times)

def rebuild_timeframe_bars(ticker_list, build_current_minute=False, min_input=False, sec_input=False):
    # ticker_list = ['IBM', 'AAPL', 'GOOG', 'TSLA', 'MSFT', 'FB']
    try:
        # First get the current time
        if build_current_minute:
            current_time = datetime.datetime.now()
            current_sec = current_time.second
            if current_sec < 5:
                time.sleep(1)
                current_time = datetime.datetime.now()
                sec_input = current_time.second
                min_input = 0
        else:
            sec_input = sec_input
            min_input = min_input

        current_time = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
        previous_time = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(minutes=min_input, seconds=sec_input)).strftime('%Y-%m-%dT%H:%M:%SZ')

        def has_condition(condition_list, condition_check):
            if type(condition_list) is not list: 
                # Assume none is a regular trade?
                in_list = False
            else:
                # There are one or more conditions in the list
                in_list = any(condition in condition_list for condition in condition_check)

            return in_list

        exclude_conditions = [
        'B','W','4','7','9','C','G','H',
        'I','M','N','P','Q','R','T', 'U', 'V', 'Z'
        ]
        # Fetch trades for the X seconds before the current time
        trades_df = api.get_trades(ticker_list,
                                    start=previous_time,
                                    end=current_time, 
                                    limit=30000).df
        # convert to market time for easier reading
        trades_df = trades_df.tz_convert('America/New_York')

        # add a column to easily identify the trades to exclude using our function from above
        trades_df['exclude'] = trades_df.conditions.apply(has_condition, condition_check=exclude_conditions)

        # filter to only look at trades which aren't excluded
        valid_trades = trades_df.query('not exclude')
        # print(len(trades_df), len(valid_trades))
        # x=trades_df['conditions'].to_list()
        # y=[str(i) for i in x]
        # print(set(y))
        if build_current_minute:
            minbars_dict = {}
            for ticker in ticker_list:
                df = valid_trades[valid_trades['symbol']==ticker].copy()
                # Resample the trades to calculate the OHLCV bars
                agg_functions = {'price': ['first', 'max', 'min', 'last'], 'size': ['sum', 'count']}
                min_bars = df.resample('1T').agg(agg_functions)
                min_bars = min_bars.droplevel(0, 'columns')
                min_bars.columns=['open', 'high', 'low' , 'close', 'volume', 'trade_count']
                min_bars = min_bars.reset_index()
                min_bars = min_bars.rename(columns={'timestamp': 'timestamp_est'})
                minbars_dict[ticker] = min_bars
                return {'resp': minbars_dict}
        else:
            return {'resp': valid_trades}
    except Exception as e:
        print("rebuild_timeframe_bars", e)
        return {'resp': False, 'msg': [e, current_time, previous_time]}
# r = rebuild_timeframe_bars(ticker_list, sec_input=30)


### Orders ###
def submit_best_limit_order(api, symbol, qty, side, client_order_id=False):
    # side = 'buy'
    # qty = '1'
    # symbol = 'BABA'
    if api == 'paper':
        api = api_paper
    else:
        api = api

    snapshot = api.get_snapshot(symbol) # return_last_quote from snapshot
    conditions = snapshot.latest_quote.conditions
    c=0
    while True:
        print(conditions)
        valid = [j for j in conditions if j in exclude_conditions]
        if len(valid) == 0 or c > 10:
            break
        else:
            snapshot = api.get_snapshot(symbol) # return_last_quote from snapshot
            c+=1   
    
    # print(snapshot) 
    last_trade = snapshot.latest_trade.price
    ask = snapshot.latest_quote.ask_price
    bid = snapshot.latest_quote.bid_price
    maker_dif =  ask - bid
    maker_delta = (maker_dif / ask) * 100
    # check to ensure bid / ask not far
    set_price = round(ask - (maker_dif / 2), 2)

    if client_order_id:
        order = api.submit_order(symbol=symbol, 
                qty=qty, 
                side=side, # buy, sell 
                time_in_force='gtc', # 'day'
                type='limit', # 'market'
                limit_price=set_price,
                client_order_id=client_order_id) # optional make sure it unique though to call later! 

    else:
        order = api.submit_order(symbol=symbol, 
            qty=qty, 
            side=side, # buy, sell 
            time_in_force='gtc', # 'day'
            type='limit', # 'market'
            limit_price=set_price,)
            # client_order_id='test1') # optional make sure it unique though to call later!
    return order
# order = submit_best_limit_order(symbol='BABA', qty=1, side='buy', client_order_id=False)

def order_filled_completely(client_order_id):
    order_status = api.get_order_by_client_order_id(client_order_id=client_order_id)
    filled_qty = order_status.filled_qty
    order_status.status
    order_status.filled_avg_price
    while True:
        if order_status.status == 'filled':
            print("order fully filled")
            break
    return True


def submit_order(api, symbol, qty, side, type, limit_price=False, client_order_id=False, time_in_force='gtc', order_class=False, stop_loss=False, take_profit=False):

    if type == 'market':
        order = api.submit_order(
            symbol=symbol,
            qty=qty,
            side=side,
            type=type,
            time_in_force=time_in_force,
            client_order_id=client_order_id
            )
    
    return order

    """stop loss order""" 
    # api.submit_order(symbol='TSLA', 
    #         qty=1, 
    #         side='buy', 
    #         time_in_force='gtc', 'day'
    #         type='limit', 
    #         limit_price=400.00, 
    #         client_order_id=001, 
    #         order_class='bracket', 
    #         stop_loss=dict(stop_price='360.00'), 
    #         take_profit=dict(limit_price='440.00'))

def refresh_account_info(api):
            """
            # Account({   'account_blocked': False, 'account_number': '603397580', 'accrued_fees': '0', 'buying_power': '80010',
            #     'cash': '40005', 'created_at': '2022-01-23T22:11:15.978765Z', 'crypto_status': 'PAPER_ONLY', 'currency': 'USD', 'daytrade_count': 0,
            #     'daytrading_buying_power': '0', 'equity': '40005', 'id': '2fae9699-b24f-4d06-80ec-d531b61e9458', 'initial_margin': '0',
            #     'last_equity': '40005','last_maintenance_margin': '0','long_market_value': '0','maintenance_margin': '0',
            #     'multiplier': '2','non_marginable_buying_power': '40005','pattern_day_trader': False,'pending_transfer_in': '40000',
            #     'portfolio_value': '40005','regt_buying_power': '80010',
            #     'short_market_value': '0','shorting_enabled': True,'sma': '40005','status': 'ACTIVE','trade_suspended_by_user': False,
            #     'trading_blocked': False, 'transfers_blocked': False})
            """
            info = api.get_account()
            return [info, 
                {'account_number': info.account_number,
                'accrued_fees': float(info.accrued_fees),
                'buying_power': float(info.buying_power),
                'cash': float(info.cash),
                'daytrade_count': float(info.daytrade_count),
                'last_equity': float(info.last_equity),
                'portfolio_value': float(info.portfolio_value)
                }
                ]


def init_index_ticker(index_list, db_root, init=True):
    # index_list = [
    #     'DJA', 'DJI', 'DJT', 'DJUSCL', 'DJU',
    #     'NDX', 'IXIC', 'IXCO', 'INDS', 'INSR', 'OFIN', 'IXTC', 'TRAN', 'XMI', 
    #     'XAU', 'HGX', 'OSX', 'SOX', 'UTY',
    #     'OEX', 'MID', 'SPX',
    #     'SCOND', 'SCONS', 'SPN', 'SPF', 'SHLTH', 'SINDU', 'SINFT', 'SMATR', 'SREAS', 'SUTIL']
    api_key = 'b2c87662-0dce-446c-862b-d64f25e93285'
    ss = StockSymbol(api_key)
    
    "Create DB folder if needed"
    index_ticker_db = os.path.join(db_root, "index_tickers")
    if os.path.exists(index_ticker_db) == False:
        os.mkdir(index_ticker_db)
        print("Ticker Index db Initiated")

    if init:
        us = ss.get_symbol_list(market="US")
        df = pd.DataFrame(us)
        df.to_csv(os.path.join(index_ticker_db, 'US.csv'), index=False, encoding='utf8')

        for tic_index in index_list: 
            try:
                index = ss.get_symbol_list(index=tic_index)
                df = pd.DataFrame(index)
                df.to_csv(os.path.join(index_ticker_db, tic_index + '.csv'), index=False, encoding='utf8')
            except Exception as e:
                print(tic_index, e, datetime.datetime.now())

    # examples:
    # symbol_list_us = ss.get_symbol_list(market="US")
    # symbol_only_list = ss.get_symbol_list(market="malaysia", symbols_only=True)
    # # https://stock-symbol.herokuapp.com/market_index_list
    # symbol_list_dow = ss.get_symbol_list(index="DJI")

    # symbol_list_dow = ss.get_symbol_list(index="SPX")
    # ndx = ss.get_symbol_list(index="NDX")
    # ndx_df = pd.DataFrame(ndx)
    
    # Dow Jones Composite Average (DJA)
    # Dow Jones Industrial Average (DJI)
    # Dow Jones Transportation Average (DJT)
    # Dow Jones U.S. Coal (DJUSCL)
    # Dow Jones Utility Average (DJU)
    # NASDAQ 100 (NDX)
    # NASDAQ COMPOSITE (IXIC)
    # NASDAQ COMPUTER (IXCO)
    # NASDAQ INDUSTRIAL (INDS)
    # NASDAQ INSURANCE (INSR)
    # NASDAQ OTHER FINANCE (OFIN)
    # NASDAQ TELECOMMUNICATIONS (IXTC)
    # NASDAQ TRANSPORTATION (TRAN)
    # NYSE ARCA MAJOR MARKET (XMI)
    # PHLX GOLD AND SILVER SECTOR INDEX (XAU)
    # PHLX HOUSING SECTOR (HGX)
    # PHLX OIL SERVICE SECTOR (OSX)
    # PHLX SEMICONDUCTOR (SOX)
    # PHLX UTILITY SECTOR (UTY)
    # S&P 100 (OEX)
    # S&P 400 (MID)
    # S&P 500 (SPX)
    # S&P 500 Communication Services (S5TELS)
    # S&P 500 Consumer Discretionary (S5COND)
    # S&P 500 Consumer Staples (S5CONS)
    # S&P 500 Energy (SPN)
    # S&P 500 Financials (SPF)
    # S&P 500 Health Care (S5HLTH)
    # S&P 500 Industrials (S5INDU)
    # S&P 500 Information Technology (S5INFT)
    # S&P 500 Materials (S5MATR)
    # S&P 500 Real Estate (S5REAS)
    # S&P 500 Utilities (S5UTIL)"""
    return True


def speedybee(QUEEN, queens_chess_piece, ticker_list): # if queens_chess_piece.lower() == 'workerbee': # return tics
    ticker_list = ['AAPL', 'TSLA', 'GOOG', 'FB']

    s = datetime.datetime.now()
    r = rebuild_timeframe_bars(ticker_list=ticker_list, build_current_minute=False, min_input=0, sec_input=30) # return all tics
    resp = r['resp'] # return slope of collective tics
    speedybee_dict = {}
    slope_dict = {}
    for symbol in set(resp['symbol'].to_list()):
        df = resp[resp['symbol']==symbol].copy()
        df = df.reset_index()
        df_len = len(df)
        if df_len > 2:
            slope, intercept, r_value, p_value, std_err = stats.linregress(df.index, df['price'])
            slope_dict[df.iloc[0].symbol] = slope
    speedybee_dict['slope'] = slope_dict
    
    # QUEEN[queens_chess_piece]['pollenstory_info']['speedybee'] = speedybee_dict

    print(sum([v for k,v in slope_dict.items()]))
    return {'speedybee': speedybee_dict}


def pickle_chesspiece(pickle_file, data_to_store):
    if PickleData(pickle_file=pickle_file, data_to_store=data_to_store) == False:
        msg=("Pickle Data Failed")
        print(msg)
        logging.critical(msg)
        return False
    else:
        return True


def PickleData(pickle_file, data_to_store): 
    # initializing data to be stored in db
    try:
        p_timestamp = {'file_creation': datetime.datetime.now()} 
        
        if os.path.exists(pickle_file) == False:
            print("init", pickle_file)
            db = {} 
            db['jp_timestamp'] = p_timestamp 
            dbfile = open(pickle_file, 'ab') 
            pickle.dump(db, dbfile)                   
            dbfile.close() 

        if data_to_store:
            p_timestamp = {'last_modified': datetime.datetime.now()}
            dbfile = open(pickle_file, 'rb+')      
            db = pickle.load(dbfile)
            dbfile.seek(0)
            dbfile.truncate()
            for k, v in data_to_store.items(): 
                db[k] = v
            db['last_modified'] = p_timestamp 
            # print(db)
            pickle.dump(db, dbfile)                   
            dbfile.close()
        
        return True
    except Exception as e:
        print("logme", e)
        return False


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


def get_ticker_statatistics(symbol):
    try:
        url = f"https://finance.yahoo.com/quote/{symbol}/key-statistics?p={symbol}"
        dataframes = pd.read_html(requests.get(url, headers={'User-agent': 'Mozilla/5.0'}).text)
    except Exception as e:
        print(symbol, e)
    return dataframes


def timestamp_string(format="%m-%d-%Y %I.%M%p"):
    return datetime.datetime.now().strftime(format)


def return_timestamp_string(format='%Y-%m-%d %H-%M-%S %p'):
    return datetime.datetime.now().strftime(format)


def print_line_of_error():
    exc_type, exc_obj, exc_tb = sys.exc_info()
    print(exc_type, exc_tb.tb_lineno)


def return_index_tickers(index_dir, ext):
    s = datetime.datetime.now()
    # ext = '.csv'
    # index_dir = os.path.join(db_root, 'index_tickers')

    index_dict = {}
    full_ticker_list = []
    all_indexs = [i.split(".")[0] for i in os.listdir(index_dir)]
    for i in all_indexs:
        df = pd.read_csv(os.path.join(index_dir, i+ext), dtype=str, encoding='utf8', engine='python')
        df = df.fillna('')
        tics = df['symbol'].tolist()
        for j in tics:
            full_ticker_list.append(j)
        index_dict[i] = df
    
    return [index_dict, list(set(full_ticker_list))]





##################################################
##################################################
################ NOT IN USE ######################
##################################################

def return_snapshots(ticker_list):
    # ticker_list = ['SPY', 'AAPL'] # TEST
    """ The Following will convert get_snapshots into a dict"""
    snapshots = api.get_snapshots(ticker_list)
    # snapshots['AAPL'].latest_trade.price # FYI This also avhices same goal
    return_dict = {}

    # handle errors
    error_dict = {}
    for i in snapshots:
        if snapshots[i] == None:
            error_dict[i] = None

    try:    
        for ticker in snapshots:
            if ticker not in error_dict.keys():
                    di = {ticker: {}}
                    token_dict = vars(snapshots[ticker])
                    temp_dict = {}
                    # for k, v in token_dict.items():
                    #     snapshots[ticker]


                    for i in token_dict:
                        unpack_dict = vars(token_dict[i])
                        data = unpack_dict["_raw"] # raw data
                        dataname = unpack_dict["_reversed_mapping"] # data names
                        temp_dict = {i : {}} # revised dict with datanames
                        for k, v in dataname.items():
                            if v in data.keys():
                                t = {}
                                t[str(k)] = data[v]
                                temp_dict[i].update(t)
                                # if v == 't':
                                #     temp_dict[i]['timestamp_covert'] = convert_todatetime_string(data[v])
                                #     # temp_dict[i]['timestamp_covert_est'] =  temp_dict[i]['timestamp_covert'].astimezone(est)
                                #     # temp_dict[i]['timestamp_covert_est'] = data[v].astimezone(est)
                            di[ticker].update(temp_dict)                       
                    return_dict.update(di)

    except Exception as e:
        print("logme", ticker, e)
        error_dict[ticker] = "Failed To Unpack"

    return [return_dict, error_dict]
# data = return_snapshots(ticker_list=['SPY', 'AAPL'])


def log_script(log_file, loginfo_dict):
    loginfo_dict = {'type': 'info', 'lognote': 'someones note'}
    df = pd.read_csv(log_file, dtype=str, encoding='utf8')
    for k,v in  loginfo_dict.items():
        df[k] = v.fillna(df[k])


def read_csv_db(db_root, type, symbol=False):
    # spy_stream
    # spy_barset
    stream = False
    bars = False
    orders = False

    tables = ['main_orders.csv', '_stream.csv', '_bars.csv']
    for t in tables:
        if os.path.exists(os.path.join(db_root, t)):
            pass
        else:
            with open(os.path.join(db_root, t), 'w') as f:
                print(t, "created")
                print(f)

    if symbol:
        if type == 'stream':
            if os.path.exists(os.path.join(db_root, symbol + '_{}.csv'.format(type))) == False:
                with open(os.path.join(db_root, symbol + '_{}.csv'.format(type)), 'w') as f:
                    df = pd.DataFrame()
                    cols = ['timestamp', 'open', 'high', 'low', 'close', 'volume', 'trade_count']
                    for i in cols:
                        df[i] = ''
                    df.to_csv(os.path.join(db_root, symbol + '_{}.csv'.format(type)), index=False, encoding='utf8')
                    print(t, "created")
                    now = datetime.datetime.now()
                    stream = df
            else:
                stream = pd.read_csv(os.path.join(db_root, symbol + '_{}.csv'.format(type)), dtype=str, encoding='utf8', engine='python')

        # bars = pd.read_csv(os.path.join(db_root, symbol + '_bars.csv'),  dtype=str, encoding='utf8', engine='python')
        elif type == 'bars':
            if os.path.exists(os.path.join(db_root, symbol + '_{}.csv'.format(type))) == False:
                with open(os.path.join(db_root, symbol + '_{}.csv'.format(type)), 'w') as f:
                    df = pd.DataFrame()
                    cols = ['timestamp', 'open', 'high', 'low', 'close', 'volume', 'trade_count']
                    for i in cols:
                        df[i] = ''
                    df.to_csv(os.path.join(db_root, symbol + '_{}.csv'.format(type)), index=False, encoding='utf8')
                    print(t, "created")
                    bars = df
            else:
                bars = pd.read_csv(os.path.join(db_root, symbol + '_{}.csv'.format(type)), dtype=str, encoding='utf8', engine='python')

        # orders = pd.read_csv(os.path.join(db_root, 'main_orders.csv'),  dtype=str, encoding='utf8', engine='python')
        orders = 'TBD'
        return [stream, bars, orders]


def convert_todatetime_string(date_string):
    # In [94]: date_string
    # Out[94]: '2022-03-11T19:41:50.649448Z'
    # In [101]: date_string[:19]
    # Out[101]: '2022-03-11T19:41:50'
    return datetime.datetime.fromisoformat(date_string[:19])


def convert_Todatetime_return_est_stringtime(date_string):
    # In [94]: date_string
    # Out[94]: '2022-03-11T19:41:50.649448Z'
    # In [101]: date_string[:19]
    # Out[101]: '2022-03-11T19:41:50'
    d = datetime.datetime.fromisoformat(date_string[:19])
    d = datetime.datetime.fromisoformat(v[:19])
    j = d.replace(tzinfo=datetime.timezone.utc)
    fmt = '%Y-%m-%dT%H:%M:%S'
    est_date = j.astimezone(pytz.timezone('US/Eastern')).strftime(fmt)
    return est_date


def convert_nano_utc_timestamp_to_est_datetime(digit_trc_time):
    digit_trc_time = 1644523144856422000
    dt = datetime.datetime.utcfromtimestamp(digit_trc_time // 1000000000) # 9 zeros
    dt = dt.strftime('%Y-%m-%d %H:%M:%S')
    return dt


def wait_for_market_open():
    clock = api.get_clock()
    if not clock.is_open:
        time_to_open = (clock.next_open - clock.timestamp).total_seconds()
        time.sleep(round(time_to_open))


def time_to_market_close():
    clock = api.get_clock()
    return (clock.next_close - clock.timestamp).total_seconds()


def read_wiki_index():
    table=pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
    df = table[0]
    # sp500 = df['Symbol'].tolist()
    # df.to_csv('S&P500-Info.csv')
    # df.to_csv("S&P500-Symbols.csv", columns=['Symbol'])
    return df


def append_MACD(df, fast, slow):
    # fast=12
    # slow=26
    macd = df.ta.macd(close='close', fast=fast, slow=slow, append=True) 
    return macd