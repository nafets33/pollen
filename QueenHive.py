# from asyncio import streams
# from cgitb import reset
from cmath import log
from datetime import datetime
import logging
from enum import Enum
import time
from turtle import rt
import alpaca_trade_api as tradeapi
# import asyncio
import os
import pandas as pd
import numpy as np
import pandas_ta as ta
import sys
from alpaca_trade_api.rest import TimeFrame, URL
from alpaca_trade_api.rest_async import gather_with_concurrency, AsyncRest
from dotenv import load_dotenv
# import threading
import datetime
import pytz
from typing import Callable
import pickle
import random
from tqdm import tqdm
from stocksymbol import StockSymbol
import requests
from collections import defaultdict
# import talib
from scipy import stats
import shutil
import ipdb
import json
import argparse
from collections import deque
import ta as bta

queens_chess_piece = os.path.basename(__file__)

prod=True

main_root = os.getcwd()
db_root = os.path.join(main_root, 'db')
db_app_root = os.path.join(db_root, 'app')

"""# Dates """

current_day = datetime.datetime.now().day
current_month = datetime.datetime.now().month
current_year = datetime.datetime.now().year

# init_logging(queens_chess_piece, db_root)
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
        dst_path = os.path.join(log_dir_logs, f'{log_name}{"_"}{datet}{".log"}')
        shutil.copy(log_file, dst_path) # only when you want to log your log files
        os.remove(log_file)
    else:
        print("logging")
        logging.basicConfig(filename=f'{"log_"}{queens_chess_piece}{".log"}',
                            filemode='a',
                            format='%(asctime)s:%(name)s:%(levelname)s: %(message)s',
                            datefmt='%m/%d/%Y %I:%M:%S %p',
                            level=logging.INFO)


est = pytz.timezone("America/New_York")

system = 'windows' #mac, windows
load_dotenv()


exclude_conditions = [
    'B','W','4','7','9','C','G','H','I','M','N',
    'P','Q','R','T','V','Z'
] # 'U' afterhours

try:
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
    # current_day = api.get_clock().timestamp.date().isoformat()
    # trading_days = api.get_calendar()
    # trading_days_df = pd.DataFrame([day._raw for day in trading_days])

except Exception as e:
    print("offline no connection")


current_date = datetime.datetime.now().strftime("%Y-%m-%d")
trading_days = api.get_calendar()
trading_days_df = pd.DataFrame([day._raw for day in trading_days])
trading_days_df['date'] = pd.to_datetime(trading_days_df['date'])


start_date = datetime.datetime.now().strftime('%Y-%m-%d')
end_date = datetime.datetime.now().strftime('%Y-%m-%d')

""" Global VARS"""
crypto_currency_symbols = ['BTCUSD', 'ETHUSD', 'BTC/USD', 'ETH/USD']
macd_tiers = 8
MACD_WORLDS = {
    'crypto': 
        {'macd': {"1Minute": 10, "5Minute": 10, "30Minute": 20, "1Hour": 50, "2Hour": 50, "1Day": 50},
        'hist': {"1Minute": 1, "5Minute": 1, "30Minute": 5, "1Hour": 5, "2Hour": 10, "1Day": 10}},
    
    'default': 
        {'macd': {"1Minute": 1, "5Minute": 1, "30Minute": 2, "1Hour": 5, "2Hour": 5, "1Day": 5},
        'hist': {"1Minute": 1, "5Minute": 1, "30Minute": 2, "1Hour": 5, "2Hour": 5, "1Day": 5}},
    }

""" VAR >>>>>>>>>>VAR >>>>>>>>>>VAR >>>>>>>>>>VAR >>>>>>>>>>VAR >>>>>>>>>>VAR >>>>>>>>>>"""
def read_pollenstory(): # return combined dataframes
    castle = ReadPickleData(pickle_file=os.path.join(db_root, 'castle.pkl'))
    bishop = ReadPickleData(pickle_file=os.path.join(db_root, 'bishop.pkl'))
    pollenstory = {**bishop['bishop']['pollenstory'], **castle['castle']['pollenstory']} # combine daytrade and longterm info

    if os.path.exists(os.path.join(db_root, 'castle_coin.pkl')):
        castle_coin = ReadPickleData(pickle_file=os.path.join(db_root, 'castle_coin.pkl'))
    else:
        castle_coin = False
    
    pollenstory = {**pollenstory, **castle_coin['castle_coin']['pollenstory']} # combine daytrade and longterm info
    return pollenstory


def read_queensmind(prod): # return active story workers
    
    if prod:
        QUEEN = ReadPickleData(pickle_file=os.path.join(db_root, 'queen.pkl'))
    else:
        QUEEN = ReadPickleData(pickle_file=os.path.join(db_root, 'queen_sandbox.pkl'))

    # return beeworkers data
    dbs = ['castle.pkl', 'bishop.pkl', 'castle_coin.pkl']
    STORY_bee = {}
    KNIGHTSWORD = {}
    ANGEL_bee = {}
    dbs_ = {}
    for db in dbs:
        if os.path.exists(os.path.join(db_root, db)):
            db_name = db.split(".pkl")[0]
            chess_piece = ReadPickleData(pickle_file=os.path.join(db_root, db))[db_name]
            STORY_bee = {**STORY_bee, **chess_piece['conscience']['STORY_bee']}
            KNIGHTSWORD = {**KNIGHTSWORD, **chess_piece['conscience']['KNIGHTSWORD']}
            ANGEL_bee = {**ANGEL_bee, **chess_piece['conscience']['ANGEL_bee']}
            dbs_[db_name] = chess_piece
            db_run = True
        else:
            db_run = False
        
    if db_run:
        QUEEN['queen']['conscience']['STORY_bee'] = STORY_bee
        QUEEN['queen']['conscience']['KNIGHTSWORD'] = KNIGHTSWORD
        QUEEN['queen']['conscience']['ANGEL_bee'] = ANGEL_bee
        return {'queen': QUEEN, 
        'STORY_bee': STORY_bee, 'KNIGHTSWORD': KNIGHTSWORD, 'ANGEL_bee': ANGEL_bee, 
        'dbs_': dbs_}
    elif QUEEN:
        return {'queen': QUEEN}
    else:
        return False

""" STORY: I want a dict of every ticker and the chart_time TRADE buy/signal weights """
### Story
# trade closer to ask price .... sellers closer to bid .... measure divergence from bid/ask to give weight
def pollen_story(pollen_nectar, QUEEN, queens_chess_piece):
    # define weights in global and do multiple weights for different scenarios..
    # MACD momentum from past N times/days
    # TIME PAST SINCE LAST HIGH TO LOW to change weight & how much time passed since tier cross last high?   
    # how long since last max/min value reached (reset time at +- 2)    

    # >/ create ranges for MACD & RSI 4-3, 70-80, or USE Prior MAX&Low ...
    # >/ what current macd tier values in comparison to max/min
    try:
        s = datetime.datetime.now()
        story = {}
        ANGEL_bee = {} # add to QUEENS mind
        STORY_bee = {} 
        # CHARLIE_bee = {}  # holds all ranges for ticker and passes info into df
        betty_bee = {k: {} for k in pollen_nectar.keys()} # monitor function speeds
        macd_tier_range = 33
        knights_sight_word = {}
        # knight_sight_df = {}

        for ticker_time_frame, df_i in pollen_nectar.items(): # CHARLIE_bee: # create ranges for MACD & RSI 4-3, 70-80, or USE Prior MAX&Low ...
            s_ttfame_func_check = datetime.datetime.now().astimezone(est)
            ticker, tframe, frame = ticker_time_frame.split("_")

            # if ticker_time_frame == 'QQQ_1Hour_3Month':
            #     ipdb
                # continue

            ANGEL_bee[ticker_time_frame] = {}
            STORY_bee[ticker_time_frame] = {'story': {}}
            
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
            # macd signal divergence
            df['macd_singal_deviation'] = df['macd'] - df['signal']
            STORY_bee[ticker_time_frame]['story']['macd_singal_deviation'] = df.iloc[-1]['macd_singal_deviation']

            s_timetoken = datetime.datetime.now().astimezone(est)
            # mac cross
            df = mark_macd_signal_cross(df=df)
            resp = knight_sight(df=df)
            df = resp['df']
            knights_word = resp['bee_triggers']
            # how long does trigger stay profitable?
            """for every index(timeframe) calculate profit length, bell curve
                conclude with how well trigger is doing to then determine when next trigger will do well
            """
            e_timetoken = datetime.datetime.now().astimezone(est)
            betty_bee[ticker_time_frame]['macdcross'] = (e_timetoken - s_timetoken)
            
            # MACD WAVE ~~~~~~~~~~~~~~~~~~~~~~~~ WAVES ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ MACD WAVE #
            # Queen to make understanding of trigger-profit waves
            #Q? measure pressure of a wave? if small waves, expect bigger wave>> up the buy

            s_timetoken = datetime.datetime.now().astimezone(est)
            wave = return_knightbee_waves(df=df, knights_word=knights_word, ticker_time_frame=ticker_time_frame)
            # wave_trigger_list = wave[ticker_time_frame].keys()
            wave_trigger_list = ['buy_cross-0', 'sell_cross-0']

            MACDWAVE_story = return_macd_wave_story(df=df, wave_trigger_list=wave_trigger_list, tframe=tframe)

            resp = return_waves_measurements(df=df, trigbees=['buy_cross-0', 'sell_cross-0'], ticker_time_frame=ticker_time_frame)
            df = resp['df']
            MACDWAVE_story['story'] = resp['df_waves']

            STORY_bee[ticker_time_frame]['waves'] = MACDWAVE_story

            e_timetoken = datetime.datetime.now().astimezone(est)
            betty_bee[ticker_time_frame]['waves'] = (e_timetoken - s_timetoken)

            knights_sight_word[ticker_time_frame] = knights_word
            STORY_bee[ticker_time_frame]['KNIGHTSWORD'] = knights_word

            
            # # return degree angle 0, 45, 90
            try:
                s_timetoken = datetime.datetime.now().astimezone(est)
                var_list = ['macd', 'hist', 'signal', 'close', 'rsi_ema']
                var_timeframes = [3, 6, 8, 10, 25, 33]
                for var in var_list:
                    for t in var_timeframes:
                        # apply rollowing angle
                        if df_len >= t:
                            x = df.iloc[df_len - t:df_len][var].to_list()
                            y = [1, 2]
                            name = f'{var}{"-"}{"Degree"}{"--"}{str(t)}'
                            ANGEL_bee[ticker_time_frame][name] = return_degree_angle(x, y)
                e_timetoken = datetime.datetime.now().astimezone(est)
                betty_bee[ticker_time_frame]['Angel_Bee'] = (e_timetoken - s_timetoken)
            except Exception as e:
                msg=(e,"--", print_line_of_error(), "--", ticker_time_frame, "--ANGEL_bee")
                logging.error(msg)

            # # add close price momentum
            # try:
            #     s_timetoken = datetime.datetime.now().astimezone(est)
            #     close = df['close']
            #     df['close_mom_3'] = talib.MOM(close, timeperiod=3).fillna(0)
            #     df['close_mom_6'] = talib.MOM(close, timeperiod=6).fillna(0)
            #     e_timetoken = datetime.datetime.now().astimezone(est)
            #     betty_bee[ticker_time_frame]['MOM'] = (e_timetoken - s_timetoken)
            # except Exception as e:
            #     msg=(e,"--", print_line_of_error(), "--", ticker_time_frame)
            #     logging.error(msg)

            time_state = df['timestamp_est'].iloc[-1] # current time
            STORY_bee[ticker_time_frame]['story']['time_state'] = datetime.datetime.now().astimezone(est)

            # devation from vwap
            df['vwap_deviation'] = df['close'] - df['vwap_original']
            STORY_bee[ticker_time_frame]['story']['vwap_deviation'] = df.iloc[-1]['vwap_deviation']     
            
            # MACD WAVE 
            macd_state = df['macd_cross'].iloc[-1]
            macd_state_side = macd_state.split("_")[0] # buy_cross-num
            middle_crossname = macd_state.split("_")[1].split("-")[0]
            state_count = macd_state.split("-")[1] # buy/sell_name_number
            STORY_bee[ticker_time_frame]['story']['macd_state'] = macd_state
            STORY_bee[ticker_time_frame]['story']['macd_state_side'] = macd_state_side
            STORY_bee[ticker_time_frame]['story']['time_since_macd_change'] = state_count

            # last time there was buycross
            if 'buy_cross-0' in knights_word.keys():
                prior_macd_time = knights_word['buy_cross-0']['last_seen']
                STORY_bee[ticker_time_frame]['story'][f'{"last_seen_macd_buy_time"}'] = prior_macd_time
                prior_macd_time = knights_word['buy_cross-0']['prior_seen']
                STORY_bee[ticker_time_frame]['story'][f'{"prior_seen_macd_buy_time"}'] = prior_macd_time
            # last time there was sellcross
            if 'sell_cross-0' in knights_word.keys():
                prior_macd_time = knights_word['sell_cross-0']['last_seen']
                STORY_bee[ticker_time_frame]['story'][f'{"last_seen_macd_sell_time"}'] = prior_macd_time
                prior_macd_time = knights_word['sell_cross-0']['prior_seen']
                STORY_bee[ticker_time_frame]['story'][f'{"prior_seen_macd_sell_time"}'] = prior_macd_time
            
            # all triggers ? move to top?
            STORY_bee[ticker_time_frame]['story']['alltriggers_current_state'] = [k for (k,v) in knights_word.items() if v['last_seen'].day == time_state.day and v['last_seen'].hour == time_state.hour and v['last_seen'].minute == time_state.minute]

            # count number of Macd Crosses
            # df['macd_cross_running_count'] = np.where((df['macd_cross'] == 'buy_cross-0') | (df['macd_cross'] == 'sell_cross-0'), 1, 0)
            s_timetoken = datetime.datetime.now().astimezone(est)
            today_df = df[df['timestamp_est'] > (datetime.datetime.now().replace(hour=1, minute=1, second=1)).astimezone(est)].copy()
            # today_df = df[df['timestamp_est'] > (datetime.datetime.now().replace(hour=1, minute=1, second=1)).isoformat()].copy()
            STORY_bee[ticker_time_frame]['story']['macd_cross_count'] = {
                'buy_cross_total_running_count': sum(np.where(df['macd_cross'] == 'buy_cross-0',1,0)),
                'sell_cross_totalrunning_count' : sum(np.where(df['macd_cross'] == 'sell_cross-0',1,0)),
                'buy_cross_todays_running_count': sum(np.where(today_df['macd_cross'] == 'buy_cross-0',1,0)),
                'sell_cross_todays_running_count' : sum(np.where(today_df['macd_cross'] == 'sell_cross-0',1,0))
            }
            e_timetoken = datetime.datetime.now().astimezone(est)
            betty_bee[ticker_time_frame]['count_cross'] = (e_timetoken - s_timetoken)
            
            # latest_close_price
            STORY_bee[ticker_time_frame]['story']['last_close_price'] = df.iloc[-1]['close']


            if "1Minute_1Day" in ticker_time_frame:
                theme_df = df.copy()
                theme_df = split_today_vs_prior(df=theme_df) # remove prior day
                theme_today_df = theme_df['df_today']
                theme_prior_df = theme_df['df_prior']
                
                # we want...last vs currnet close prices, && Height+length of wave
                current_price = theme_today_df.iloc[-1]['close']
                open_price = theme_today_df.iloc[0]['close'] # change to timestamp lookup
                yesterday_close = theme_prior_df.iloc[-1]['close'] # change to timestamp lookup
                
                STORY_bee[ticker_time_frame]['story']['current_from_open'] = (current_price - open_price) / current_price

                # Current from Yesterdays Close
                STORY_bee[ticker_time_frame]['story']['current_from_yesterday_close'] = (current_price - yesterday_close) / current_price

                # how did day start ## this could be moved to queen and calculated once only
                STORY_bee[ticker_time_frame]['story']['open_start_pct'] = (open_price - yesterday_close) / open_price

                e_timetoken = datetime.datetime.now().astimezone(est)
                slope, intercept, r_value, p_value, std_err = stats.linregress(theme_today_df.index, theme_today_df['close'])
                STORY_bee[ticker_time_frame]['story']['current_slope'] = slope
                e_timetoken = datetime.datetime.now().astimezone(est)
                betty_bee[ticker_time_frame]['slope'] = (e_timetoken - s_timetoken)

            # Measure MACD WAVES
            # change % shifts for each, close, macd, signal, hist....
            df = assign_MACD_Tier(df=df, mac_world=mac_world, tiers_num=macd_tiers,  ticker_time_frame=ticker_time_frame)
            STORY_bee[ticker_time_frame]['story']['current_macd_tier'] = df.iloc[-1]['macd_tier']
            STORY_bee[ticker_time_frame]['story']['current_hist_tier'] = df.iloc[-1]['hist_tier']

            df['mac_ranger'] = df['macd_tier'].apply(lambda x: power_ranger_mapping(x))
            df['hist_ranger'] = df['hist_tier'].apply(lambda x: power_ranger_mapping(x))
            
            # how long have you been stuck at vwap ?

            # add to story
            df['chartdate'] = df['timestamp_est'] # add as new col
            df['name'] = ticker_time_frame
            story[ticker_time_frame] = df
            # ticker, _time, _frame = ticker_time_frame.split("_")

            # latest Pull
            df_lastrow = df.iloc[-1]
            # df_lastrow_remaining = df_lastrow[[i for i in df_lastrow.index.tolist() if i not in STORY_bee[ticker_time_frame]['story'].keys()]].copy
            STORY_bee[ticker_time_frame]['story']['current_mind'] = df_lastrow

            e_ttfame_func_check = datetime.datetime.now().astimezone(est)
            betty_bee[ticker_time_frame]['full_loop'] = (e_ttfame_func_check - s_ttfame_func_check)
            
            # add momentem ( when macd < signal & past 3 macds are > X Value or %)
            
            # when did macd and signal share same tier?

        e = datetime.datetime.now()
        print("pollen_story", str((e - s)))
        return {'pollen_story': story, 'conscience': {'ANGEL_bee': ANGEL_bee, 'KNIGHTSWORD': knights_sight_word, 'STORY_bee': STORY_bee  } , 'betty_bee': betty_bee}
    except Exception as e:
        print("pollen_story error ", e)
        print_line_of_error()
        print(ticker_time_frame)
        

def knight_sight(df): # adds all triggers to dataframe
    # ticker_time_frame = df['name'].iloc[-1] #TEST
    # trigger_dict = {ticker_time_frame: {}}  #TEST
    
    def trig_89(df): 
        trig = np.where(
            (df['macd_cross'].str.contains("buy_cross-0")==True)
            ,"bee", 'nothing')
        return trig
    
    def trig_98(df): 
        trig = np.where(
            (df['macd_cross'].str.contains("sell_cross-0")==True)
            ,"bee", 'nothing')
        return trig
    
    def trig_pre_89(df):
        trig = np.where(
            (df['macd_cross'].str.contains("buy")==False) &
            (df['hist_slope-3'] > 5) &
            (df['macd_singal_deviation'] < -.04) &
            (df['macd_singal_deviation'] > -.06)

            ,"bee", 'nothing')
        return trig
    
    trigger_dict_info = {"buy_cross-0": trig_89, "sell_cross-0": trig_98, 'ready_buy_cross': trig_pre_89}

    trigger_dict = {}
    for trigger, trig_func in trigger_dict_info.items():
        df[trigger] = trig_func(df=df)
        bee_df = df[df[trigger] == 'bee'].copy()
        if len(bee_df) > 0:
            trigger_dict[trigger] = {}
            trigger_dict[trigger]['last_seen'] = bee_df['timestamp_est'].iloc[-1]
            if len(bee_df) > 1:
                trigger_dict[trigger]['prior_seen'] = bee_df['timestamp_est'].iloc[-2]
    
    # # Mac is very LOW and we are in buy cross
    # trigger = 'buy_RED_tier-1_macdcross'
    # df[trigger] = np.where(
    #     (df['macd_cross'].str.contains("buy")==True) & # is not in BUY cycle
    #     ((df['macd'] < 0) & (df['macd'] > -.3))
    #     ,"bee", 'nothing')
    # bee_df = df[df[trigger] == 'bee'].copy()
    # if len(bee_df) > 0:
    #     trigger_dict[trigger] = {}
    #     trigger_dict[trigger]['last_seen'] = bee_df['timestamp_est'].iloc[-1]
    #     if len(bee_df) > 1:
    #         trigger_dict[trigger]['prior_seen'] = bee_df['timestamp_est'].iloc[-2]
    #     else:
    #         trigger_dict[trigger]['prior_seen'] = bee_df['timestamp_est'].iloc[-1]

    # trigger = 'buy_RED_tier-2_macdcross'
    # df[trigger] = np.where(
    #     (df['macd_cross'].str.contains("buy")==True) & # is not in BUY cycle
    #     ((df['macd'] < -.3) & (df['macd'] > -.5))
    #     ,"bee", 'nothing')
    # bee_df = df[df[trigger] == 'bee'].copy()
    # if len(bee_df) > 0:
    #     trigger_dict[trigger] = {}
    #     trigger_dict[trigger]['last_seen'] = bee_df['timestamp_est'].iloc[-1]
    #     if len(bee_df) > 1:
    #         trigger_dict[trigger]['prior_seen'] = bee_df['timestamp_est'].iloc[-2]
    #     else:
    #         trigger_dict[trigger]['prior_seen'] = bee_df['timestamp_est'].iloc[-1]
    
    # trigger = 'buy_RED_tier-3_macdcross'
    # df[trigger] = np.where(
    #     (df['macd_cross'].str.contains("buy")==True) & # is not in BUY cycle
    #     ((df['macd'] < -.5) & (df['macd'] > -.1))
    #     ,"bee", 'nothing')
    # bee_df = df[df[trigger] == 'bee'].copy()
    # if len(bee_df) > 0:
    #     trigger_dict[trigger] = {}
    #     trigger_dict[trigger]['last_seen'] = bee_df['timestamp_est'].iloc[-1]
    #     if len(bee_df) > 1:
    #         trigger_dict[trigger]['prior_seen'] = bee_df['timestamp_est'].iloc[-2]
    #     else:
    #         trigger_dict[trigger]['prior_seen'] = bee_df['timestamp_est'].iloc[-1]
    
    # trigger = 'buy_RED_tier-4_macdcross'
    # df[trigger] = np.where(
    #     (df['macd_cross'].str.contains("buy")==True) & # is not in BUY cycle
    #     ((df['macd'] < -.1) & (df['macd'] > -.15))
    #     ,"bee", 'nothing')
    # bee_df = df[df[trigger] == 'bee'].copy()
    # if len(bee_df) > 0:
    #     trigger_dict[trigger] = {}
    #     trigger_dict[trigger]['last_seen'] = bee_df['timestamp_est'].iloc[-1]
    #     if len(bee_df) > 1:
    #         trigger_dict[trigger]['prior_seen'] = bee_df['timestamp_est'].iloc[-2]
    #     else:
    #         trigger_dict[trigger]['prior_seen'] = bee_df['timestamp_est'].iloc[-1]
    
    # trigger = 'buy_RED_tier-5_macdcross'
    # df[trigger] = np.where(
    #     (df['macd_cross'].str.contains("buy")==True) & # is not in BUY cycle
    #     (df['macd'] < -.15)
    #     ,"bee", 'nothing')
    # bee_df = df[df[trigger] == 'bee'].copy()
    # if len(bee_df) > 0:
    #     trigger_dict[trigger] = {}
    #     trigger_dict[trigger]['last_seen'] = bee_df['timestamp_est'].iloc[-1]
    #     if len(bee_df) > 1:
    #         trigger_dict[trigger]['prior_seen'] = bee_df['timestamp_est'].iloc[-2]
    #     else:
    #         trigger_dict[trigger]['prior_seen'] = bee_df['timestamp_est'].iloc[-1]
    
    # # Mac is very LOW and we are in buy cross
    # trigger = 'buy_high-macdcross'
    # df[trigger] = np.where(
    #     (df['macd_cross'].str.contains("buy")==True) & # is not in BUY cycle
    #     (df['macd'] < -.1)
    #     ,"bee", 'nothing')
    # bee_df = df[df[trigger] == 'bee'].copy()
    # if len(bee_df) > 0:
    #     trigger_dict[trigger] = {}
    #     trigger_dict[trigger]['last_seen'] = bee_df['timestamp_est'].iloc[-1]
    #     if len(bee_df) > 1:
    #         trigger_dict[trigger]['prior_seen'] = bee_df['timestamp_est'].iloc[-2]
    #     else:
    #         trigger_dict[trigger]['prior_seen'] = bee_df['timestamp_est'].iloc[-1]
    
    # # Mac is very LOW and we are in buy cross
    # trigger = 'buy_high-macdcross'
    # df[trigger] = np.where(
    #     (df['macd_cross'].str.contains("buy")==True) & # is not in BUY cycle
    #     (df['macd'] < -.1)
    #     ,"bee", 'nothing')
    # bee_df = df[df[trigger] == 'bee'].copy()
    # if len(bee_df) > 0:
    #     trigger_dict[trigger] = {}
    #     trigger_dict[trigger]['last_seen'] = bee_df['timestamp_est'].iloc[-1]
    #     if len(bee_df) > 1:
    #         trigger_dict[trigger]['prior_seen'] = bee_df['timestamp_est'].iloc[-2]
    #     else:
    #         trigger_dict[trigger]['prior_seen'] = bee_df['timestamp_est'].iloc[-1]
    
    # # Mac is very High and we are in a Sell Cross
    # trigger = 'sell_high-macdcross'
    # df[trigger] = np.where(
    #     (df['macd_cross'].str.contains("sell")==True) &
    #     (df['macd'] > 1)
    #     ,"bee", 'nothing')
    # bee_df = df[df[trigger] == 'bee'].copy()
    # if len(bee_df) > 0:
    #     trigger_dict[trigger] = {}
    #     trigger_dict[trigger]['last_seen'] = bee_df['timestamp_est'].iloc[-1]
    #     if len(bee_df) > 1:
    #         trigger_dict[trigger]['prior_seen'] = bee_df['timestamp_est'].iloc[-2]
    #     else:
    #         trigger_dict[trigger]['prior_seen'] = bee_df['timestamp_est'].iloc[-1]
    
    # # Mac is very High and the prior hist slow was steep and we are not in a Sell CROSS Cycle Yet
    # trigger = 'sell_high-macdcross'
    # df[trigger] = np.where(
    #     (df['macd_cross'].str.contains("sell_hold")==False) & # is not in Sell cycle
    #     (df['macd'] > 1.5) &
    #     (df['macd_slope-3'] < .1) &
    #     ((df['hist_slope-3'] < .33) |(df['hist_slope-6'] < .10))
    #     ,"bee", 'nothing')
    # bee_df = df[df[trigger] == 'bee'].copy()
    # if len(bee_df) > 0:
    #     trigger_dict[trigger] = {}
    #     trigger_dict[trigger]['last_seen'] = bee_df['timestamp_est'].iloc[-1]
    #     if len(bee_df) > 1:
    #         trigger_dict[trigger]['prior_seen'] = bee_df['timestamp_est'].iloc[-2]
    #     else:
    #         trigger_dict[trigger]['prior_seen'] = bee_df['timestamp_est'].iloc[-1]

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
        # last_buycross_index = 0
        # last_sellcross_index = 0
        # wave_mark_list = []
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
                    # last_buycross_index = i
                    # wave_mark_list.append(last_buycross_index)
                elif now_mac < now_signal and prior_mac >= prior_signal:
                    cross_list.append(f'{"sell_cross"}{"-"}{0}')
                    c = 0
                    prior_cross = 'sell'
                    sell_c += 1
                    # last_sellcross_index = i
                    # wave_mark_list.append(last_sellcross_index)

                else:
                    if prior_cross:
                        if prior_cross == 'buy':
                            c+=1
                            cross_list.append(f'{"buy_hold"}{"-"}{c}')
                            # wave_mark_list.append(0)
                        else:
                            c+=1
                            cross_list.append(f'{"sell_hold"}{"-"}{c}')
                            # wave_mark_list.append(0)
                    else:
                        # ipdb.set_trace()
                        cross_list.append(f'{"init_hold"}{"-"}{0}')
                        # wave_mark_list.append(0)
            else:
                cross_list.append(f'{"init_hold"}{"-"}{0}')
                # wave_mark_list.append(0)
        df2 = pd.DataFrame(cross_list, columns=['macd_cross'])
        # df3 = pd.DataFrame(wave_mark_list, columns=['macd_cross_wavedistance'])
        df_new = pd.concat([df, df2], axis=1)
        return df_new
    except Exception as e:
        msg=(e,"--", print_line_of_error(), "--", 'macd_cross')
        logging.critical(msg)     


def assign_tier_num(num_value,  td):
    length_td = len(td)
    max_num_value = td[length_td-1][1]
    for k, v in td.items():
        # ipdb.set_trace()
        num_value = float(num_value)
        if num_value > 0 and num_value > v[0] and num_value < v[1]:
            # print(k, num_value)
            return k
        elif num_value < 0 and num_value < v[0] and num_value > v[1]:
            # print(k, num_value)
            return k
        elif num_value > 0 and num_value > max_num_value:
            # print("way above")
            return length_td
        elif num_value < 0 and num_value < max_num_value:
            # print("way below")
            return length_td
        elif num_value == 0:
            # print('0 really')
            return 0


def assign_MACD_Tier(df, mac_world, tiers_num, ticker_time_frame):
    # create tier ranges
    # tiers_num = 7
    
    ticker, ftime, frame = ticker_time_frame.split("_")    

    def create_tier_range(mac_world_ranges):
        m_high = mac_world_ranges[ftime]
        m_low = mac_world_ranges[ftime] * -1

        tiers_add = m_high/tiers_num
        td_high = {}
        for i in range(tiers_num):
            if i == 0:
                td_high[i] = (0, tiers_add)
            else:
                td_high[i] = (td_high[i-1][1], td_high[i-1][1] + tiers_add)

        tiers_add = m_low/tiers_num
        td_low = {}
        for i in range(tiers_num):
            if i == 0:
                td_low[i] = (0, tiers_add)
            else:
                td_low[i] = (td_low[i-1][1], td_low[i-1][1] + tiers_add)
        
        return {'td_high': td_high, 'td_low': td_low}

    # select mac_world &  # apply tiers

    # "MAC"
    if ticker in crypto_currency_symbols:
        mac_world_ranges = MACD_WORLDS['crypto']['macd']
    else:
        mac_world_ranges = MACD_WORLDS['default']['macd']
    tier_range = create_tier_range(mac_world_ranges=mac_world_ranges)
    td_high = tier_range['td_high']
    td_low = tier_range['td_low']
    df['macd_tier'] = np.where( (df['macd'] > 0), 
    df['macd'].apply(lambda x: assign_tier_num(num_value=x, td=td_high)), 
    df['macd'].apply(lambda x: assign_tier_num(num_value=x, td=td_low))
    )
    df['macd_tier'] = np.where(df['macd'] > 0, df['macd_tier'], df['macd_tier'] * -1)

    
    # "Hist"
    if ticker in crypto_currency_symbols:
        mac_world_ranges = MACD_WORLDS['crypto']['hist']
    else:
        mac_world_ranges = MACD_WORLDS['default']['hist']
    tier_range = create_tier_range(mac_world_ranges=mac_world_ranges)
    td_high = tier_range['td_high']
    td_low = tier_range['td_low']
    df['hist_tier'] = np.where( (df['hist'] > 0), 
    df['hist'].apply(lambda x: assign_tier_num(num_value=x, td=td_high)), 
    df['hist'].apply(lambda x: assign_tier_num(num_value=x, td=td_low))
    )
    df['hist_tier'] = np.where(df['hist'] > 0, df['hist_tier'], df['hist_tier'] * -1)

    return df


def return_knightbee_waves(df, knights_word, ticker_time_frame):  # adds profit wave based on trigger
    # df = POLLENSTORY['SPY_1Minute_1Day'] # test
    wave = {ticker_time_frame: {}}
    # knights_word = {'ready_buy_cross': 2, 'buy_cross-0':1,}
    for knight_trigger in knights_word.keys():
        trig_name = knight_trigger # "buy_cross-0" # test
        wave[ticker_time_frame][trig_name] = {}
        trigger_bee = df[trig_name].tolist()
        close = df['close'].tolist()
        track_bees = {}
        track_bees_profits = {}
        trig_bee_count = 0
        for idx, trig_bee in enumerate(trigger_bee):
            beename = f'{trig_bee_count}'
            if idx == 0:
                continue
            if trig_bee == 'bee':
                # trig_bee_count+=1
                # beename = f'{trig_name}{trig_bee_count}'
                close_price = close[idx]
                track_bees[beename] = close_price
                # reset only if bee not continous
                if trigger_bee[idx-1] != 'bee':
                    trig_bee_count+=1
                continue
            if trig_bee_count > 0:
                # beename = f'{trig_name}{trig_bee_count}'
                origin_trig_price = track_bees[str(int(beename) - 1)]
                latest_price = close[idx]
                profit_loss = (latest_price - origin_trig_price) / latest_price
                
                if "sell_cross-0" in knight_trigger: # all triggers with short reverse number to reflect profit
                    profit_loss = profit_loss * -1
                
                if beename in track_bees_profits.keys():
                    track_bees_profits[beename].update({idx: profit_loss})
                else:
                    track_bees_profits[beename] = {idx: profit_loss}
        # knights_word[trig_name]['wave'] = track_bees_profits
        wave[ticker_time_frame][trig_name] = track_bees_profits
        # wave[ticker_time_frame]["buy_cross-0"].keys()
        # bees_wave = wave['AAPL_1Minute_1Day']["buy_cross-0"]
        index_perwave = {}
        for k, v in track_bees_profits.items():
            for kn, vn in v.items():
                index_perwave[kn] = k
        index_wave_dict = [v for (k,v) in track_bees_profits.items()]
        index_wave_series = {} 
        for di in index_wave_dict:
            for k,v in di.items():
                index_wave_series[k] = v
        df[f'{trig_name}{"__wave"}'] = df['story_index'].map(index_wave_series).fillna("0")
        df[f'{trig_name}{"__wave_number"}'] = df['story_index'].map(index_perwave).fillna("0")
        # bees_wave_df = df[df['story_index'].isin(bees_wave_list)].copy()
        # tag greatest profit
    return wave


def return_macd_wave_story(df, wave_trigger_list, tframe):
    # POLLENSTORY = read_pollenstory()
    # df = POLLENSTORY["SPY_1Minute_1Day"]
    # wave_trigger_list = ["buy_cross-0", "sell_cross-0"]
    
    # t = split_today_vs_prior(df=df)
    # df = t['df_today']
    
    # df = df

    # length and height of wave
    MACDWAVE_story = {'story': {}}
    MACDWAVE_story.update({trig_name: {} for trig_name in wave_trigger_list})

    for trigger in wave_trigger_list:
        wave_col_name = f'{trigger}{"__wave"}'
        wave_col_wavenumber = f'{trigger}{"__wave_number"}'
    
        num_waves = df[wave_col_wavenumber].tolist()
        num_waves_list = list(set(num_waves))
        num_waves_list = [str(i) for i in sorted([int(i) for i in num_waves_list], reverse=True)]

        for wave_n in num_waves_list:
            MACDWAVE_story[trigger][wave_n] = {}
            MACDWAVE_story[trigger][wave_n].update({'wave_n': wave_n})
            if wave_n == '0':
                continue
            df_waveslice = df[['timestamp_est', wave_col_wavenumber, 'story_index', wave_col_name]].copy()
            df_waveslice = df[df[wave_col_wavenumber] == wave_n] # slice by trigger event wave start / end 
            
            row_1 = df_waveslice.iloc[0]['story_index']
            row_2 = df_waveslice.iloc[-1]['story_index']

            # we want to know the how long it took to get to low? 

            # Assign each waves timeblock
            if "Day" in tframe:
                wave_blocktime = "Day"
                wave_starttime = df_waveslice.iloc[0]['timestamp_est']
                wave_endtime = df_waveslice.iloc[-1]['timestamp_est']
            else:
                wave_starttime = df_waveslice.iloc[0]['timestamp_est']
                wave_endtime = df_waveslice.iloc[-1]['timestamp_est']
                wave_starttime_token = wave_starttime.replace(tzinfo=None)
                if wave_starttime_token < wave_starttime_token.replace(hour=11, minute=0):
                    wave_blocktime = 'morning_9-11'
                elif wave_starttime_token > wave_starttime_token.replace(hour=11, minute=0) and wave_starttime_token < wave_starttime_token.replace(hour=14, minute=0):
                    wave_blocktime = 'lunch_11-2'
                elif wave_starttime_token > wave_starttime_token.replace(hour=14, minute=0) and wave_starttime_token < wave_starttime_token.replace(hour=16, minute=1):
                    wave_blocktime = 'afternoon_2-4'
                else:
                    wave_blocktime = 'afterhours'

            MACDWAVE_story[trigger][wave_n].update({'length': row_2 - row_1, 
            'wave_blocktime' : wave_blocktime,
            'wave_start_time': wave_starttime,
            'wave_end_time': wave_endtime,
            'trigbee': trigger,
            'wave_id': f'{trigger}{wave_blocktime}{wave_starttime}'
            })
            
            wave_height_value = max(df_waveslice[wave_col_name].values)
            # how long was it profitable?
            profit_df = df_waveslice[df_waveslice[wave_col_name] > 0].copy()
            profit_length  = len(profit_df)
            if profit_length > 0:
                max_profit_index = profit_df[profit_df[wave_col_name] == wave_height_value].iloc[0]['story_index']
                time_to_max_profit = max_profit_index - row_1
                MACDWAVE_story[trigger][wave_n].update({'maxprofit': wave_height_value, 'time_to_max_profit': time_to_max_profit})

            else:
                MACDWAVE_story[trigger][wave_n].update({'maxprofit': wave_height_value, 'time_to_max_profit': 0})

    # all_waves = []
    # all_waves_temp = []
    # for trig_name in wave_trigger_list:
    #     l_waves = list(MACDWAVE_story[trig_name].values())
    #     l_waves = [i for i in l_waves if i['wave_n'] != '0']
    #     all_waves_temp.append(l_waves)
    # for el_list in range(len(all_waves_temp)):
    #     all_waves = all_waves + all_waves_temp[el_list - 1]
    # df_waves = pd.DataFrame(all_waves)
    # # df_waves = df_waves.fillna("NULL")
    # # df_waves = df_waves
    # df_waves = df_waves.sort_values(by=['wave_start_time'], ascending=True).reset_index()
    # df_waves['macd_wave_n'] = df_waves.index
    # df_waves = macd_wave_length_story(df_waves) # df_waves['macd_wave_length']

    # MACDWAVE_story['story'] = df_waves
    # df_t = df_waves[[i for i in df_waves.columns if 'macd' in i or i in ['wave_start_time', 'trigbee', 'wave_blocktime']]].copy()

    return MACDWAVE_story


def return_waves_measurements(df, ticker_time_frame, trigbees=['buy_cross-0', 'sell_cross-0', 'ready_buy_cross']):
    # POLLENSTORY = read_pollenstory()
    # df = POLLENSTORY["SPY_1Minute_1Day"]
    # wave_trigger_list = ["macd_cross"]
    # length and height of wave

    ticker, tframe, frame  = ticker_time_frame.split("_")

    def profit_loss(df_waves, x):
        if x == 0:
            return 0
        else:
            prior_row = df_waves.iloc[x-1]
            current_row = df_waves.iloc[x]
            latest_price = current_row['close']
            origin_trig_price = prior_row['close']
            profit_loss = (latest_price - origin_trig_price) / latest_price
            if df_waves.iloc[x]['macd_cross'] == 'sell_cross-0':
                profit_loss * -1
            return profit_loss

    
    def macd_cross_WaveLength(df_waves, x):
        if x == 0:
            return 0
        else:
            prior_row = df_waves.iloc[x-1]
            current_row = df_waves.iloc[x]
            latest_price = current_row['story_index']
            origin_trig_price = prior_row['story_index']
            length = latest_price - origin_trig_price
            return length
    
    
    def macd_cross_WaveBlocktime(df_waves, x):
        # Assign each waves timeblock
        if x == 0:
            return 0
        if "Day" in tframe:
            return "Day"
            # wave_starttime = df_waves.iloc[x]['timestamp_est']
            # wave_endtime = df_waves.iloc[x]['timestamp_est']
        else:
            wave_starttime = df_waves.iloc[x]['timestamp_est']
            # wave_endtime = df_waves.iloc[x]['timestamp_est']
            wave_starttime_token = wave_starttime.replace(tzinfo=None)
            if wave_starttime_token < wave_starttime_token.replace(hour=11, minute=0):
                return 'morning_9-11'
            elif wave_starttime_token >= wave_starttime_token.replace(hour=11, minute=0) and wave_starttime_token < wave_starttime_token.replace(hour=14, minute=0):
                return 'lunch_11-2'
            elif wave_starttime_token >= wave_starttime_token.replace(hour=14, minute=0) and wave_starttime_token < wave_starttime_token.replace(hour=16, minute=1):
                return 'afternoon_2-4'
            else:
                # ipdb.set_trace()
                return 'afterhours'

    ### Needs a little extra Love >> index max profit, count length, add to df_waves and df >> ensure max profit is correct as 2 rows could share same value
    def macd_cross_TimeToMaxProfit(df, df_waves, x):
        # Assign each waves timeblock
        for x in df_waves['wave_n'].tolist():
            if x == 0:
                return 0
            else:
                prior_row = df_waves.iloc[x - 1]['story_index']
                current_row = df_waves.iloc[x]['story_index']
                
                df_waveslice = df[(df.index >= int(prior_row)) & (df.index < int(current_row))].copy()
                origin_trig_price = df_waves.iloc[x - 1]['close']
                df_waveslice['macd_cross__maxprofit'] = (df_waveslice['close'] - origin_trig_price) / df_waveslice['close']
                
                index_wave_series = dict(zip(df_waveslice['story_index'], df_waveslice['macd_cross__maxprofit']))
                # df['macd_cross__maxprofit'] = df['story_index'].map(index_wave_series).fillna("0")
                # return index_wave_series
                # return df
                wave_col_name = 'macd_cross__maxprofit'
                wave_height_value = max(df_waveslice[wave_col_name].values)
                # how long was it profitable?
                profit_df = df_waveslice[df_waveslice[wave_col_name] > 0].copy()
                profit_length  = len(profit_df)
                if profit_length > 0:
                    max_profit_index = profit_df[profit_df[wave_col_name] == wave_height_value].iloc[0]['story_index']
                    time_to_max_profit = max_profit_index - prior_row
                    # MACDWAVE_story[trigger][wave_n].update({'maxprofit': wave_height_value, 'time_to_max_profit': time_to_max_profit})

                else:
                    time_to_max_profit = 0
                    # MACDWAVE_story[trigger][wave_n].update({'maxprofit': wave_height_value, 'time_to_max_profit': 0})

    # set wave num
    df_waves = df[df['macd_cross'].isin(trigbees)].copy().reset_index()
    df_waves['wave_n'] = df_waves.index
    df_waves['length'] = df_waves['wave_n'].apply(lambda x: macd_cross_WaveLength(df_waves, x))
    df_waves['profits'] = df_waves['wave_n'].apply(lambda x: profit_loss(df_waves, x))
    # df_waves['story_index_in_profit'] = np.where(df_waves['profits'] > 0, 1, 0)
    df_waves['active_wave'] = np.where(df_waves['wave_n'] == df_waves['wave_n'].iloc[-1], 'active', 'not_active')
    df_waves['wave_blocktime'] = df_waves['wave_n'].apply(lambda x: macd_cross_WaveBlocktime(df_waves, x))


    index_wave_series = dict(zip(df_waves['story_index'], df_waves['wave_n']))
    df['wave_n'] = df['story_index'].map(index_wave_series).fillna("0")
    
    index_wave_series = dict(zip(df_waves['story_index'], df_waves['length']))
    df['length'] = df['story_index'].map(index_wave_series).fillna("0")

    index_wave_series = dict(zip(df_waves['story_index'], df_waves['wave_blocktime']))
    df['wave_blocktime'] = df['story_index'].map(index_wave_series).fillna("0")

    index_wave_series = dict(zip(df_waves['story_index'], df_waves['profits']))
    df['profits'] = df['story_index'].map(index_wave_series).fillna("0")

    # index_wave_series = dict(zip(df_waves['story_index'], df_waves['story_index_in_profit']))
    # df['story_index_in_profit'] = df['story_index'].map(index_wave_series).fillna("0")

    index_wave_series = dict(zip(df_waves['story_index'], df_waves['active_wave']))
    df['active_wave'] = df['story_index'].map(index_wave_series).fillna("0")

    df_waves = df_waves[['wave_blocktime', 'timestamp_est', 'macd_cross', 'wave_n', 'length', 'profits', 'active_wave',]]
    
    return {'df': df, 'df_waves': df_waves}




def split_today_vs_prior(df, other_timestamp=False):
    if other_timestamp:
        df_day = df[other_timestamp].iloc[-1]
        # df = df.set_index(other_timestamp, drop=False)
        # df_today = df[(df.index.day == df_day.day) & (df.index.month == df_day.month) & (df.index.year == df_day.year)].copy()        
        df_today = df[df['wave_start_time'] > (datetime.datetime.now().replace(hour=1, minute=1, second=1)).astimezone(est)].copy()
        df_prior = df[~(df['wave_start_time'].isin(df_today['wave_start_time'].to_list()))].copy()
        return {'df_today': df_today, 'df_prior': df_prior}
        # df_today = df_today.reset_index()
        # df_prior = df_prior.reset_index()
    else:
        df_day = df['timestamp_est'].iloc[-1]
        # df = df.copy()
        # df = df.set_index('timestamp_est', drop=False)
        df_today = df[df['timestamp_est'] > (datetime.datetime.now().replace(hour=1, minute=1, second=1)).astimezone(est)].copy()
        # df_today = df[(df['timestamp_est'].day == df_day.day) & (df['timestamp_est'].month == df_day.month) & (df['timestamp_est'].year == df_day.year)].copy()
        df_prior = df[~(df['story_index'].isin(df_today['story_index'].to_list()))].copy()
        
        # df_today = df_today.reset_index()
        # df_prior = df_prior.reset_index()
        return {'df_today': df_today, 'df_prior': df_prior}


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
                

                trading_days_df_ = trading_days_df[trading_days_df['date'] < current_date] # less then current date
                start_date = trading_days_df_.tail(ndays).head(1).date
                start_date = start_date.iloc[-1].strftime("%Y-%m-%d")

                # start_date = trading_days_df.query('date < @current_day').tail(ndays).head(1).date
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
        'I','M','N','P','Q','R','T', 'V', 'Z'
        ] # 'U'
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
        print("rebuild timeframe bars", e)
        return {'resp': False, 'msg': [e, current_time, previous_time]}
# r = rebuild_timeframe_bars(ticker_list, sec_input=30)


### Orders ###
def return_alpc_portolio(api):
    all_positions = api.list_positions()
    portfolio = {i.symbol: vars(i)["_raw"] for i in all_positions}
    return {'portfolio': portfolio}


def check_order_status(api, client_order_id, queen_order=False, prod=True): # return raw dict form
    if queen_order:
        if "queen_gen" in queen_order['client_order_id']:
            return queen_order
    if prod:
        order = api.get_order_by_client_order_id(client_order_id=client_order_id)
        order_ = vars(order)['_raw']
    else:
        order = api_paper.get_order_by_client_order_id(client_order_id=client_order_id)
        order_ = vars(order)['_raw']
    return order_


def submit_best_limit_order(api, symbol, qty, side, client_order_id=False):
    # side = 'buy'
    # qty = '1'
    # symbol = 'BABA'
    # if api == 'paper':
    #     api = api_paper
    # else:
    #     api = api

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
    elif type == 'limit':
        order = api.submit_order(
            symbol=symbol,
            qty=qty,
            side=side,
            type=type,
            time_in_force=time_in_force,
            client_order_id=client_order_id,
            limit_price=limit_price,
            )
    else:
        return False
    
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


def PickleData(pickle_file, data_to_store):
    # initializing data to be stored in db
    p_timestamp = {'file_creation': datetime.datetime.now()} 
    if os.path.exists(pickle_file) == False:
        with open(pickle_file, 'wb+') as dbfile:
            print("init", pickle_file)
            db = {} 
            db['jp_timestamp'] = p_timestamp
            pickle.dump(db, dbfile)                   

    if data_to_store:
        p_timestamp = {'last_modified': datetime.datetime.now()}
        db = {}
        root, name = os.path.split(pickle_file)
        pickle_file_temp = os.path.join(root, ("temp" + name))
        with open(pickle_file_temp, 'wb+') as dbfile:
            for k, v in data_to_store.items(): 
                db[k] = v
            db['last_modified'] = p_timestamp
            pickle.dump(db, dbfile)
        
        with open(pickle_file, 'wb+') as dbfile:
            for k, v in data_to_store.items(): 
                db[k] = v
            db['last_modified'] = p_timestamp
            pickle.dump(db, dbfile)

        #remove temp

        # try:
        #     os.rename(pickle_file_temp, pickle_file)
        # except Exception as e:
        #     logging.critical(("Not able to Rename Pickle File Trying again: err: ", e))
        #     for attempt in range(5):
        #         time.sleep(1)
        #         try:
        #             os.rename(pickle_file_temp, pickle_file)
        #         except Exception as e:
        #             print('myerror', attempt, e)
        #             sys.exit()        
        return True


# def PickleData(pickle_file, data_to_store): 
#     # initializing data to be stored in db
#     p_timestamp = {'file_creation': datetime.datetime.now()} 
#     if os.path.exists(pickle_file) == False:
#         with open(pickle_file, 'wb+') as dbfile:
#             print("init", pickle_file)
#             db = {} 
#             db['jp_timestamp'] = p_timestamp 
#             pickle.dump(db, dbfile)                   

#     if data_to_store:
#         p_timestamp = {'last_modified': datetime.datetime.now()}
#         db = {}
#         with open(pickle_file, 'wb+') as dbfile:
#             for k, v in data_to_store.items(): 
#                 db[k] = v
#             db['last_modified'] = p_timestamp 
#             pickle.dump(db, dbfile)                   
        
#         return True


def ReadPickleData(pickle_file, db_init_dict=False): 
    p_timestamp = {'file_creation': datetime.datetime.now()} 
    if os.path.exists(pickle_file) == False:
        with open(pickle_file, 'wb+') as dbfile:
            print("init", pickle_file)
            db = {} 
            db['jp_timestamp'] = p_timestamp 
            pickle.dump(db, dbfile) 
    # for reading also binary mode is important try 3 times
    try:
        with open(pickle_file, "rb") as f:
            return pickle.load(f)
    except Exception as e:
        try:
            time.sleep(.33)
            with open(pickle_file, "rb") as f:
                return pickle.load(f)
        except Exception as e:
            print("CRITICAL PICKLE READ ERROR logme", e)
            return False


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


def get_ticker_statatistics(symbol):
    try:
        url = f"https://finance.yahoo.com/quote/{symbol}/key-statistics?p={symbol}"
        dataframes = pd.read_html(requests.get(url, headers={'User-agent': 'Mozilla/5.0'}).text)
    except Exception as e:
        print(symbol, e)
    return dataframes



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


def read_csv_db(db_root, tablename, ext='.csv', prod=True, init=False):
    orders = False
    main_orders_cols = ['trigname', 'client_order_id', 'origin_client_order_id', 'exit_order_link', 'date', 'lastmodified', 'selfnote', 'app_requests_id', 'bulkorder_origin__client_order_id', 'portfolio_name', 'system_recon']

    if init:
        def create_csv_table(cols, db_root, tablename, ext):
            table_path = os.path.join(db_root, tablename)
            if os.path.exists(table_path) == False:
                with open(table_path, 'w') as f:
                    df = pd.DataFrame()
                    for i in cols:
                        df[i] = ''
                    df.to_csv(table_path, index=True, encoding='utf8')
                    print(table_path, "created")
                    return True
            else:
                return True

        tables = ['main_orders.csv', 'main_orders_sandbox.csv']
        for t in tables:
            if os.path.exists(os.path.join(db_root, t)):
                pass
            else:
                create_csv_table(cols=main_orders_cols, db_root=db_root, tablename=t, ext='.csv')

    if tablename:
        if prod:
            return pd.read_csv(os.path.join(db_root, f'{tablename}{ext}'), dtype=str, encoding='utf8', engine='python')
        else:
            return pd.read_csv(os.path.join(db_root, f'{tablename}{"_sandbox"}{ext}'), dtype=str, encoding='utf8', engine='python')


def update_csv_db(df_to_add, tablename, append, update=False, replace=False, ext='.csv', prod=True):
    df_to_add['lastmodified'] = datetime.datetime.now().isoformat()
    if prod:
        table_path = os.path.join(db_root, f'{tablename}{ext}')
    else:
        table_path = os.path.join(db_root, f'{tablename}{"_sandbox"}{ext}')

    if tablename:
        if prod:
            main_df = pd.read_csv(os.path.join(db_root, f'{tablename}{ext}'), dtype=str, encoding='utf8', engine='python')
        else:
            main_df = pd.read_csv(os.path.join(db_root, f'{tablename}{"_sandbox"}{ext}'), dtype=str, encoding='utf8', engine='python')

        if append:
            new_df = pd.concat([main_df, df_to_add], axis=0, ignore_index=True)
            new_df.to_csv(table_path, index=False, encoding='utf8')
        
        if update:
            indx = list(df_to_add.index)
            main_df['index'] = main_df.index
            main_df = main_df[~main_df['index'].isin(indx)]
            new_df = pd.concat([main_df, df_to_add], axis=0)
            new_df.to_csv(table_path, index=False, encoding='utf8')
        
        if replace:
            new_df = df_to_add
            new_df.to_csv(table_path, index=False, encoding='utf8')      


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
    digit_trc_time=1656785012.538478
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


###### >>>>>>>>>>>>>>>> CASTLE BISHOP FUNCTIONS <<<<<<<<<<<<<<<#########
#####                                                            #######
"""TICKER Calculation Functions"""

def return_macd(df_main, fast, slow, smooth):
    price = df_main['close']
    exp1 = price.ewm(span = fast, adjust = False).mean()
    exp2 = price.ewm(span = slow, adjust = False).mean()
    macd = pd.DataFrame(exp1 - exp2).rename(columns = {'close':'macd'})
    signal = pd.DataFrame(macd.ewm(span = smooth, adjust = False).mean()).rename(columns = {'macd':'signal'})
    hist = pd.DataFrame(macd['macd'] - signal['signal']).rename(columns = {0:'hist'})
    frames =  [macd, signal, hist]
    df = pd.concat(frames, join='inner', axis=1)
    df_main = pd.concat([df_main, df], join='inner', axis=1)
    return df_main


# def return_VWAP(df):
#     # VWAP
#     df = df.assign(
#         vwap=df.eval(
#             'wgtd = close * volume', inplace=False
#         ).groupby(df['timestamp_est']).cumsum().eval('wgtd / volume')
#     )
#     return df

def return_VWAP(df, window=3):
    # VWAP
    df['vwap'] = bta.volume.VolumeWeightedAveragePrice(df["high"], df["low"], df["close"], df["volume"], window=15, fillna=True).volume_weighted_average_price()
    return df


def vwap(df):
    q = df.volume.values
    p = df.close.values
    df.assign(vwap=(p * q).cumsum() / q.cumsum())
    df = df.groupby(df['timestamp_est'], group_keys=False).apply(vwap).fillna(0)
    return df


def return_RSI(df, length):
    # Define function to calculate the RSI
    # length = 14 # test
    # df = df.reset_index(drop=True)
    close = df['close']
    def calc_rsi(over: pd.Series, fn_roll: Callable) -> pd.Series:
        # Get the difference in price from previous step
        delta = over.diff()
        # Get rid of the first row, which is NaN since it did not have a previous row to calculate the differences
        delta = delta[1:] 

        # Make the positive gains (up) and negative gains (down) Series
        up, down = delta.clip(lower=0), delta.clip(upper=0).abs()

        roll_up, roll_down = fn_roll(up), fn_roll(down)
        rs = roll_up / roll_down
        rsi = 100.0 - (100.0 / (1.0 + rs))

        # Avoid division-by-zero if `roll_down` is zero
        # This prevents inf and/or nan values.
        rsi[:] = np.select([roll_down == 0, roll_up == 0, True], [100, 0, rsi])
        rsi.name = 'rsi'

        # Assert range
        valid_rsi = rsi[length - 1:]
        assert ((0 <= valid_rsi) & (valid_rsi <= 100)).all()
        # Note: rsi[:length - 1] is excluded from above assertion because it is NaN for SMA.
        return rsi

    # Calculate RSI using MA of choice
    # Reminder: Provide ≥ 1 + length extra data points!
    rsi_ema = calc_rsi(close, lambda s: s.ewm(span=length).mean())
    rsi_ema.name = 'rsi_ema'
    df = pd.concat((df, rsi_ema), axis=1).fillna(0)
    
    rsi_sma = calc_rsi(close, lambda s: s.rolling(length).mean())
    rsi_sma.name = 'rsi_sma'
    df = pd.concat((df, rsi_sma), axis=1).fillna(0)

    rsi_rma = calc_rsi(close, lambda s: s.ewm(alpha=1 / length).mean())  # Approximates TradingView.
    rsi_rma.name = 'rsi_rma'
    df = pd.concat((df, rsi_rma), axis=1).fillna(0)

    return df


def return_sma_slope(df, y_list, time_measure_list):
        # df=pollenstory['SPY_1Minute_1Day'].copy()
        # time_measure_list = [3, 23, 33]
        # y_list = ['close', 'macd', 'hist']
        for mtime in time_measure_list:
            for el in y_list:
                sma_name = f'{el}{"_sma-"}{mtime}'
                slope_name = f'{el}{"_slope-"}{mtime}'
                df[sma_name] = df[el].rolling(mtime).mean().fillna(1)
                df[slope_name] = np.degrees(np.arctan(df[sma_name].diff()/mtime))
        return df



""" Main Functions"""
def return_getbars_WithIndicators(bars_data, MACD):
    # time = '1Minute' #TEST
    # symbol = 'SPY' #TEST
    # ndays = 1
    # bars_data = return_bars(symbol, time, ndays, trading_days_df=trading_days_df)

    try:
        s = datetime.datetime.now() #TEST
        bars_data['vwap_original'] = bars_data['vwap']
        # del mk_hrs_data['vwap']
        df_vwap = return_VWAP(bars_data)
        # df_vwap = vwap(bars_data)

        df_vwap_rsi = return_RSI(df=df_vwap, length=14)
        # append_MACD(df_vwap_rsi_macd, fast=MACD['fast'], slow=MACD['slow'])
        df_vwap_rsi_macd = return_macd(df_main=df_vwap_rsi, fast=MACD['fast'], slow=MACD['slow'], smooth=MACD['smooth'])
        df_vwap_rsi_macd_smaslope = return_sma_slope(df=df_vwap_rsi_macd, time_measure_list=[3, 6, 23, 33], y_list=['close', 'macd', 'hist'])
        e = datetime.datetime.now()
        # print(str((e - s)) + ": " + datetime.datetime.now().strftime("%A, %d. %B %Y %I:%M%p"))
        # 0:00:00.198920: Monday, 21. March 2022 03:02PM 2 days 1 Minute
        return [True, df_vwap_rsi_macd_smaslope]
    except Exception as e:
        print("log error", print_line_of_error())
        return [False, e, print_line_of_error()]


def Return_Init_ChartData(ticker_list, chart_times): #Iniaite Ticker Charts with Indicator Data
    # ticker_list = ['SPY', 'QQQ']
    # chart_times = {
    #     "1Minute_1Day": 0, "5Minute_5Day": 5, "30Minute_1Month": 18, 
    #     "1Hour_3Month": 48, "2Hour_6Month": 72, 
    #     "1Day_1Year": 250}
    msg = (ticker_list, chart_times)
    logging.info(msg)
    print(msg)

    error_dict = {}
    s = datetime.datetime.now()
    dfs_index_tickers = {}
    bars = return_bars_list(ticker_list, chart_times)
    if bars[1]: # rebuild and split back to ticker_time with market hours only
        bars_dfs = bars[1]
        for timeframe, df in bars_dfs.items():
            time_frame=timeframe.split("_")[0] # '1day_1year'
            if '1day' in time_frame.lower():
                for ticker in ticker_list:
                    df_return = df[df['symbol']==ticker].copy()
                    dfs_index_tickers[f'{ticker}{"_"}{timeframe}'] = df_return
            else:
                df = df.set_index('timestamp_est')
                market_hours_data = df.between_time('9:30', '16:00')
                market_hours_data = market_hours_data.reset_index()
                for ticker in ticker_list:
                    df_return = market_hours_data[market_hours_data['symbol']==ticker].copy()
                    dfs_index_tickers[f'{ticker}{"_"}{timeframe}'] = df_return
    
    e = datetime.datetime.now()
    msg = {'function':'Return_Init_ChartData',  'func_timeit': str((e - s)), 'datetime': datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S_%p')}
    print(msg)
    # dfs_index_tickers['SPY_5Minute']
    return {'init_charts': dfs_index_tickers, 'errors': error_dict}


def Return_Bars_LatestDayRebuild(ticker_time): #Iniaite Ticker Charts with Indicator Data
    # IMPROVEMENT: use Return_bars_list for Return_Bars_LatestDayRebuild
    # ticker_time = "SPY_1Minute_1Day"

    ticker, timeframe, days = ticker_time.split("_")
    error_dict = {}
    s = datetime.datetime.now()
    dfs_index_tickers = {}
    try:
        # return market hours data from bars
        bars_data = return_bars(symbol=ticker, timeframe=timeframe, ndays=0, trading_days_df=trading_days_df) # return [True, symbol_data, market_hours_data, after_hours_data]
        df_bars_data = bars_data[2] # mkhrs if in minutes
        # df_bars_data = df_bars_data.reset_index()
        if bars_data[0] == False:
            error_dict["NoData"] = bars_data[1] # symbol already included in value
        else:
            dfs_index_tickers[ticker_time] = df_bars_data
    except Exception as e:
        print(ticker_time, e)
    
    e = datetime.datetime.now()
    msg = {'function':'Return_Bars_LatestDayRebuild',  'func_timeit': str((e - s)), 'datetime': datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S_%p')}
    # print(msg)
    # dfs_index_tickers['SPY_5Minute']
    return [dfs_index_tickers, error_dict, msg]


def Return_Snapshots_Rebuild(df_tickers_data, init=False): # from snapshots & consider using day.min.chart to rebuild other timeframes
    ticker_list = list([set(j.split("_")[0] for j in df_tickers_data.keys())][0]) #> get list of tickers

    snapshots = api.get_snapshots(ticker_list)
    # snapshots['SPY'].latest_trade
    # snapshots['SPY'].latest_trade.conditions

    for ticker in snapshots.keys(): # replace snapshot if in exclude_conditions
        c = 0
        while True:
            conditions = snapshots[ticker].latest_trade.conditions
            # print(conditions)
            invalid = [c for c in conditions if c in exclude_conditions]
            if len(invalid) == 0 or c > 10:
                break
            else:
                print("invalid trade-condition pull snapshot")
                snapshot = api.get_snapshot(ticker) # return_last_quote from snapshot
                snapshots[ticker] = snapshot
                c+=1

    float_cols = ['close', 'high', 'open', 'low', 'vwap']
    int_cols = ['volume', 'trade_count']
    main_return_dict = {}
    # min_bars_dict = rebuild_timeframe_bars(ticker_list)
    # if min_bars_dict['resp'] == False:
    #     print("Min Bars Error", min_bars_dict)
    #     min_bars_dict = {k:{} for k in ticker_list}
    # else:
    #     min_bars_dict = min_bars_dict['resp']
    min_bars_dict = {k:{} for k in ticker_list} # REBUILDING MIN BARS NEEDS IMPROVEMENT BEFORE SOME MAY FAIL TO RETURN

    def response_returned(ticker_list):
        return_dict = {}
        for ticker in ticker_list:
            dl = {
            'close': snapshots[ticker].daily_bar.close,
            'high': snapshots[ticker].daily_bar.high,
            'low': snapshots[ticker].daily_bar.low,
            'timestamp_est': snapshots[ticker].daily_bar.timestamp,
            'open': snapshots[ticker].daily_bar.open,
            'volume': snapshots[ticker].daily_bar.volume,
            'trade_count': snapshots[ticker].daily_bar.trade_count,
            'vwap': snapshots[ticker].daily_bar.vwap
            }
            df_daily = pd.Series(dl).to_frame().T  # reshape dataframe
            for i in float_cols:
                df_daily[i] = df_daily[i].apply(lambda x: float(x))
            for i in int_cols:
                df_daily[i] = df_daily[i].apply(lambda x: int(x))
            # df_daily = df_daily.rename(columns={'timestamp': 'timestamp_est'})
            
            return_dict[ticker + "_day"] = df_daily
            
            # if len(min_bars_dict[ticker]) != 0:
            #     # "THIS IS NOT being used"
            #     d = {'close': min_bars_dict[ticker].close.iloc[-1],
            #     'high': min_bars_dict[ticker].high.iloc[-1],
            #     'low': min_bars_dict[ticker].low.iloc[-1],
            #     'timestamp_est': min_bars_dict[ticker].timestamp_est.iloc[-1],
            #     'open': min_bars_dict[ticker].open.iloc[-1],
            #     'volume': min_bars_dict[ticker].volume.iloc[-1],
            #     'trade_count': min_bars_dict[ticker].trade_count.iloc[-1],
            #     'vwap': min_bars_dict[ticker].vwap.iloc[-1]
            #     }
            # else:
            #     d = {
            #     'close': snapshots[ticker].latest_trade.price,
            #     'high': 0, # snapshots[ticker].minute_bar.high,
            #     'low': 0, # snapshots[ticker].minute_bar.low,
            #     'timestamp_est': snapshots[ticker].latest_trade.timestamp,
            #     'open': 0, # snapshots[ticker].minute_bar.open,
            #     'volume': 0, # snapshots[ticker].minute_bar.volume,
            #     'trade_count': 0, # snapshots[ticker].minute_bar.trade_count,
            #     'vwap': snapshots[ticker].minute_bar.vwap
            #     }
            d = {
                'close': snapshots[ticker].latest_trade.price,
                'high': 0, # snapshots[ticker].minute_bar.high,
                'low': 0, # snapshots[ticker].minute_bar.low,
                'timestamp_est': snapshots[ticker].latest_trade.timestamp,
                'open': 0, # snapshots[ticker].minute_bar.open,
                'volume': 0, # snapshots[ticker].minute_bar.volume,
                'trade_count': 0, # snapshots[ticker].minute_bar.trade_count,
                'vwap': snapshots[ticker].minute_bar.vwap
                }
            df_minute = pd.Series(d).to_frame().T
            for i in float_cols:
                df_minute[i] = df_minute[i].apply(lambda x: float(x))
            for i in int_cols:
                df_minute[i] = df_minute[i].apply(lambda x: int(x))
            # df_minute = df_minute.rename(columns={'timestamp': 'timestamp_est'})

            return_dict[ticker + "_minute"] = df_minute
        
        return return_dict
    snapshot_ticker_data = response_returned(ticker_list)
    
    for ticker_time, df in df_tickers_data.items():
        symbol_snapshots = {k:v for (k,v) in snapshot_ticker_data.items() if k.split("_")[0] == ticker_time.split("_")[0]}
        symbol, timeframe, days = ticker_time.split("_")
        if "day" in timeframe.lower():
            df_day_snapshot = symbol_snapshots[f'{symbol}{"_day"}'] # stapshot df
            df_day_snapshot['symbol'] = symbol
            df = df.head(-1) # drop last row which has current day / added minute
            df_rebuild = pd.concat([df, df_day_snapshot], join='outer', axis=0).reset_index(drop=True) # concat minute
            main_return_dict[ticker_time] = df_rebuild
        else:
            df_snapshot = symbol_snapshots[f'{symbol}{"_minute"}'] # stapshot df
            df_snapshot['symbol'] = symbol
            if init:
                df_rebuild = pd.concat([df, df_snapshot], join='outer', axis=0).reset_index(drop=True) # concat minute
                main_return_dict[ticker_time] = df_rebuild
            else:
                df = df.head(-1) # drop last row which has current day
                df_rebuild = pd.concat([df, df_snapshot], join='outer', axis=0).reset_index(drop=True) # concat minute
                main_return_dict[ticker_time] = df_rebuild

    return main_return_dict


def ReInitiate_Charts_Past_Their_Time(df_tickers_data): # re-initiate for i timeframe 
    # IMPROVEMENT: use Return_bars_list for Return_Bars_LatestDayRebuild
    return_dict = {}
    rebuild_confirmation = {}

    def tag_current_day(timestamp):
        if timestamp.day == current_day and timestamp.month == current_month and timestamp.year == current_year:
            return 'tag'
        else:
            return '0'

    for ticker_time, df in df_tickers_data.items():
        ticker, timeframe, days = ticker_time.split("_")
        last = df['timestamp_est'].iloc[-2].replace(tzinfo=None)
        now = datetime.datetime.now()
        timedelta_minutes = (now - last).seconds / 60
        now_day = now.day
        last_day = last.day
        if now_day != last_day:
            return_dict[ticker_time] = df
            continue

        if "1minute" == timeframe.lower():
            if timedelta_minutes > 2:
                dfn = Return_Bars_LatestDayRebuild(ticker_time)
                if len(dfn[1]) == 0:
                    df_latest = dfn[0][ticker_time]
                    df['timetag'] = df['timestamp_est'].apply(lambda x: tag_current_day(x))
                    df_replace = df[df['timetag']!= 'tag'].copy()
                    del df_replace['timetag']
                    df_return = pd.concat([df_replace, df_latest], join='outer', axis=0).reset_index(drop=True)
                    df_return_me = pd.concat([df_return, df_return.tail(1)], join='outer', axis=0).reset_index(drop=True) # add dup last row to act as snapshot
                    return_dict[ticker_time] = df_return_me
                    rebuild_confirmation[ticker_time] = "rebuild"
            else:
                return_dict[ticker_time] = df

        elif "5minute" == timeframe.lower():
            if timedelta_minutes > 6:
                dfn = Return_Bars_LatestDayRebuild(ticker_time)
                if len(dfn[1]) == 0:
                    df_latest = dfn[0][ticker_time]
                    df['timetag'] = df['timestamp_est'].apply(lambda x: tag_current_day(x))
                    df_replace = df[df['timetag']!= 'tag'].copy()
                    del df_replace['timetag']
                    df_return = pd.concat([df_replace, df_latest], join='outer', axis=0).reset_index(drop=True)
                    df_return_me = pd.concat([df_return, df_return.tail(1)], join='outer', axis=0).reset_index(drop=True) # add dup last row to act as snapshot
                    return_dict[ticker_time] = df_return_me
                    rebuild_confirmation[ticker_time] = "rebuild"
            else:
                return_dict[ticker_time] = df
        
        elif "30minute" == timeframe.lower():
            if timedelta_minutes > 31:
                dfn = Return_Bars_LatestDayRebuild(ticker_time)
                if len(dfn[1]) == 0:
                    df_latest = dfn[0][ticker_time]

                    df['timetag'] = df['timestamp_est'].apply(lambda x: tag_current_day(x))
                    df_replace = df[df['timetag']!= 'tag'].copy()
                    del df_replace['timetag']
                    df_return = pd.concat([df_replace, df_latest], join='outer', axis=0).reset_index(drop=True)
                    df_return_me = pd.concat([df_return, df_return.tail(1)], join='outer', axis=0).reset_index(drop=True) # add dup last row to act as snapshot
                    return_dict[ticker_time] = df_return_me
                    rebuild_confirmation[ticker_time] = "rebuild"
            else:
                return_dict[ticker_time] = df

        elif "1hour" == timeframe.lower():
            if timedelta_minutes > 61:
                dfn = Return_Bars_LatestDayRebuild(ticker_time)
                if len(dfn[1]) == 0:
                    df_latest = dfn[0][ticker_time]
                    df['timetag'] = df['timestamp_est'].apply(lambda x: tag_current_day(x))
                    df_replace = df[df['timetag']!= 'tag'].copy()
                    del df_replace['timetag']
                    df_return = pd.concat([df_replace, df_latest], join='outer', axis=0).reset_index(drop=True)
                    df_return_me = pd.concat([df_return, df_return.tail(1)], join='outer', axis=0).reset_index(drop=True) # add dup last row to act as snapshot
                    return_dict[ticker_time] = df_return_me
                    rebuild_confirmation[ticker_time] = "rebuild"
            else:
                return_dict[ticker_time] = df

        elif "2hour" == timeframe.lower():
            if timedelta_minutes > 121:
                dfn = Return_Bars_LatestDayRebuild(ticker_time)
                if len(dfn[1]) == 0:
                    df_latest = dfn[0][ticker_time]
                    df['timetag'] = df['timestamp_est'].apply(lambda x: tag_current_day(x))
                    df_replace = df[df['timetag']!= 'tag'].copy()
                    del df_replace['timetag']
                    df_return = pd.concat([df_replace, df_latest], join='outer', axis=0).reset_index(drop=True)
                    df_return_me = pd.concat([df_return, df_return.tail(1)], join='outer', axis=0).reset_index(drop=True) # add dup last row to act as snapshot
                    return_dict[ticker_time] = df_return_me
                    rebuild_confirmation[ticker_time] = "rebuild"
            else:
                return_dict[ticker_time] = df

        else:
            return_dict[ticker_time] = df
    
    # add back in snapshot init
    return {"ticker_time": return_dict, "rebuild_confirmation": rebuild_confirmation}


def pollen_hunt(df_tickers_data, MACD):
    # Check to see if any charts need to be Recreate as times lapsed
    df_tickers_data_rebuilt = ReInitiate_Charts_Past_Their_Time(df_tickers_data)
    if len(df_tickers_data_rebuilt['rebuild_confirmation'].keys()) > 0:
        print(df_tickers_data_rebuilt['rebuild_confirmation'].keys())
        print(datetime.datetime.now().strftime("%H:%M-%S"))
    
    # re-add snapshot
    df_tickers_data_rebuilt = Return_Snapshots_Rebuild(df_tickers_data=df_tickers_data_rebuilt['ticker_time'])
    
    main_rebuild_dict = {} ##> only override current dict if memory becomes issues!
    chart_rebuild_dict = {}
    for ticker_time, bars_data in df_tickers_data_rebuilt.items():
        chart_rebuild_dict[ticker_time] = bars_data
        df_data_new = return_getbars_WithIndicators(bars_data=bars_data, MACD=MACD)
        if df_data_new[0] == True:
            main_rebuild_dict[ticker_time] = df_data_new[1]
        else:
            print("error", ticker_time)

    return {'pollencharts_nectar': main_rebuild_dict, 'pollencharts': chart_rebuild_dict}



###### >>>>>>>>>>>>>>>> CASTLE BISHOP FUNCTIONS <<<<<<<<<<<<<<<#########


# ###### >>>>>>>>>>>>>>>> QUEEN <<<<<<<<<<<<<<<#########

def return_dfshaped_orders(running_orders, portfolio_name='Jq'):
    running_orders_df = pd.DataFrame(running_orders)
    if len(running_orders_df) > 0:
        running_orders_df['filled_qty'] =  running_orders_df['filled_qty'].apply(lambda x: float(x))
        running_orders_df['req_qty'] =  running_orders_df['req_qty'].apply(lambda x: float(x))
        running_orders_df = running_orders_df[running_orders_df['portfolio_name']==portfolio_name].copy()
        running_portfolio = running_orders_df.groupby('symbol')[['filled_qty', 'req_qty']].sum().reset_index()
    else:
        running_portfolio = [] # empty
    
    return running_portfolio


def createParser():
    parser = argparse.ArgumentParser()
    parser.add_argument ('-qcp', default="queen")
    parser.add_argument ('-prod', default='false')
    return parser


def return_market_hours(api_cal, crypto):
    trading_days = api_cal # api.get_calendar()
    trading_days_df = pd.DataFrame([day._raw for day in trading_days])
    s = datetime.datetime.now()
    s_iso = s.isoformat()[:10]
    mk_open_today = s_iso in trading_days_df["date"].tolist()
    mk_open = datetime.datetime(s.year, s.month, s.day, hour=9, minute=30)
    mk_close = datetime.datetime(s.year, s.month, s.day, hour=16, minute=0)
    
    if str(crypto).lower() == 'true':
        return "open"
    else:
        if mk_open_today:
            if s >= mk_open and s <= mk_close:
                return "open"
            else:
                return "closed"
        else:
            return "closed"



def discard_allprior_days(df):
    df_day = df['timestamp_est'].iloc[-1]
    df = df.copy()
    df = df.set_index('timestamp_est', drop=True) # test
    # df = df[(df.index.day == df_day.day) & (df.index.year == df_day.year) & (df.index.month == df_day.month)].copy() # remove yesterday
    df = df[(df.index.day == df_day.day)].copy()
    df = df.reset_index()
    return df


def slice_by_time(df, between_a, between_b):
    df = df.copy()
    df = df.set_index('timestamp_est', drop=True) # test
    # df = df.between_time('9:30', '12:00') #test
    df = df.between_time(between_a, between_b)
    df = df.reset_index()
    return df


def init_app(pickle_file):
    if os.path.exists(pickle_file) == False:
        if "_App_" in pickle_file:
            print("init app")
            data = init_QUEEN_App()
            PickleData(pickle_file=pickle_file, data_to_store=data)
        if "_Orders_" in pickle_file:
            print("init Orders")
            data = {'orders_completed': [], 'archived': []}
            PickleData(pickle_file=pickle_file, data_to_store=data)            


def stars(chart_times=False, desc="frame_period: period count -- 1Minute_1Day"):
    if chart_times:
        return chart_times
    else:
        chart_times = {
        "1Minute_1Day": 1, "5Minute_5Day": 5, "30Minute_1Month": 18, 
        "1Hour_3Month": 48, "2Hour_6Month": 72, 
        "1Day_1Year": 250}
        return chart_times
    

def pollen_themes(KING, themes=['nuetral', 'strong'], waves_cycles=['waveup', 'wavedown'], wave_periods={'morning_9-11': .01, 'lunch_11-2': .01, 'afternoon_2-4': .01, 'Day': .01, 'afterhours': .01}):
    ## set the course for the day how you want to buy expecting more scalps vs long? this should update and change as new info comes into being
    # themes = ['nuetral', 'strong']
    # waves_cycles = ['waveup', 'wavedown']
    # wave_periods = {'morning_9-11': .01, 'lunch_11-2': .01, 'afternoon_2-4': .01, 'Day': .01, 'afterhours': .01}
    
    star_times = KING['stars']
    pollen_themes = {}
    for theme in themes:
        pollen_themes[theme] = {}
        for star in star_times.keys():
            pollen_themes[theme][star] = {}
            for wave_c in waves_cycles:
                pollen_themes[theme][star][wave_c] = {wave_period: n for (wave_period, n) in wave_periods.items()}
     
    return pollen_themes


def KINGME(chart_times=False):
    return_dict = {}

    if chart_times:
        return_dict['stars'] = stars(chart_times)
    else:
        return_dict['stars'] = stars()

    order_rule_types = ['queen_gen']
    
    kings_order_rules = {'knight_bees': 
                                    {
    'queen_gen': {'max_profit_waveDeviation': 1, 
                'timeduration': 33, 
                'take_profit': .005,
                'sellout': -.0089,
                'sell_trigbee_trigger': 'true',
                'stagger_profits': 'false',
                'scalp_profits': 'true',
                'profit_gradiant': 1,
                },
    'init': {'max_profit_waveDeviation': 1, 
                'timeduration': 33, 
                'take_profit': .005,
                'sellout': -.0089,
                'sell_trigbee_trigger': 'true',
                'stagger_profits': 'false',
                'scalp_profits': 'true',
                'profit_gradiant': 1,
                    },
    'app': {'max_profit_waveDeviation': 1, 
                'timeduration': 33, 
                'take_profit': .005,
                'sellout': -.0089,
                'sell_trigbee_trigger': 'true',
                'stagger_profits': 'false',
                'scalp_profits': 'true',
                'profit_gradiant': 1,
                },
    'buy_cross-0': {'max_profit_waveDeviation': 1, 
                'timeduration': 33, 
                'take_profit': .005,
                'sellout': -.0089,
                'sell_trigbee_trigger': 'true',
                'stagger_profits': 'false',
                'scalp_profits': 'true',
                'profit_gradiant': 1,
                },
    'sell_cross-0': {'max_profit_waveDeviation': 1, 
                'timeduration': 33, 
                'take_profit': .005,
                'sellout': -.0089,
                'sell_trigbee_trigger': 'true',
                'stagger_profits': 'false',
                'scalp_profits': 'true',
                'profit_gradiant': 1,
                },
    'ready_buy_cross': {'max_profit_waveDeviation': 1, 
                'timeduration': 33, 
                'take_profit': .005,
                'sellout': -.0089,
                'sell_trigbee_trigger': 'true',
                'stagger_profits': 'false',
                'scalp_profits': 'true',
                'profit_gradiant': 1,
                },
    'ready_sell_cross': {'max_profit_waveDeviation': 1, 
                'timeduration': 33, 
                'take_profit': .005,
                'sellout': -.0089,
                'sell_trigbee_trigger': 'true',
                'stagger_profits': 'false',
                'scalp_profits': 'true',
                'profit_gradiant': 1,
                },
                                    }
    }
    
    
    def tradingModel_kings_order_rules():
        
        return True
    
    # add order rules
    return_dict['kings_order_rules'] = kings_order_rules
    
    return return_dict


def order_vars__queen_order_items(trading_model, king_order_rules, order_side, wave_amo, maker_middle, origin_wave, power_up_rangers, ticker_time_frame_origin, double_down_trade=False, sell_reason={}, running_close_legs='false', qty_available_running_close_adjustment='false', wave_at_creation={}, sell_qty='false'):
    order_vars = {}
    if order_side == 'sell':
        if maker_middle:
            order_vars['order_type'] = 'limit'
            order_vars['limit_price'] = maker_middle # 10000
            order_vars['order_trig_sell_stop_limit'] = 'true'
        else:
            order_vars['order_type'] = 'market'
            order_vars['limit_price'] = False
            order_vars['order_trig_sell_stop_limit'] = 'false'
        
        order_vars['origin_wave'] = origin_wave
        order_vars['power_up'] = power_up_rangers
        order_vars['wave_amo'] = wave_amo
        order_vars['order_side'] = order_side
        order_vars['ticker_time_frame_origin'] = ticker_time_frame_origin
        order_vars['power_up_rangers'] = power_up_rangers
        order_vars['king_order_rules'] = king_order_rules
        order_vars['trading_model'] = trading_model
        order_vars['double_down_trade'] = double_down_trade
        order_vars['sell_reason'] = sell_reason
        order_vars['running_close_legs'] = running_close_legs
        order_vars['qty_available_running_close_adjustment'] = qty_available_running_close_adjustment
        order_vars['wave_at_creation'] = wave_at_creation
        order_vars['sell_qty'] = sell_qty

        return order_vars
    
    elif order_side == 'buy':
        if maker_middle:
            order_vars['order_type'] = 'limit'
            order_vars['limit_price'] = maker_middle # 10000
            order_vars['order_trig_sell_stop_limit'] = 'true'
        else:
            order_vars['order_type'] = 'market'
            order_vars['limit_price'] = False
            order_vars['order_trig_sell_stop_limit'] = 'false'
        
        order_vars['origin_wave'] = origin_wave
        order_vars['power_up'] = sum(power_up_rangers.values())
        order_vars['wave_amo'] = wave_amo
        order_vars['order_side'] = order_side
        order_vars['ticker_time_frame_origin'] = ticker_time_frame_origin
        order_vars['power_up_rangers'] = power_up_rangers
        order_vars['king_order_rules'] = king_order_rules
        order_vars['trading_model'] = trading_model
        order_vars['double_down_trade'] = double_down_trade
        order_vars['sell_reason'] = sell_reason
        order_vars['running_close_legs'] = running_close_legs
        order_vars['qty_available_running_close_adjustment'] = qty_available_running_close_adjustment
        order_vars['wave_at_creation'] = wave_at_creation
        order_vars['sell_qty'] = sell_qty
        
        return order_vars

    else:
        print("break in program")
        logging_log_message(log_type='error', msg='break in program order vars queen order items')
        return False


def create_QueenOrderBee(trading_model, KING, order_vars, order, ticker_time_frame, portfolio_name, status_q, trig, exit_order_link, priceinfo, queen_init=False): # Create Running Order
    date_mark = datetime.datetime.now().astimezone(est)
    # allowed_col = ["queen_order_state", ]
    if queen_init:
        # print("Queen Template Initalized")
        logging_log_message(msg='QueenHive Queen Template Initalized')
        running_order = {'trading_model': trading_model,
                        'double_down_trade': False,
                        'queen_order_state': 'init',
                        'side': 'init',
                        'order_trig_buy_stop': 'false',
                        'order_trig_sell_stop': 'false',
                        'order_trig_sell_stop_limit': 'false',
                        'limit_price': 'false',
                        'running_close_legs': 'false',
                        'symbol': 'init', 
                        'order_rules': KING["kings_order_rules"]["knight_bees"]['init'], 
                        'trigname': trig, 
                        'datetime': date_mark,
                        'ticker_time_frame': 'init_init_init',
                        'ticker_time_frame_origin': 'init_init_init',
                        'status_q': 'init',
                        'portfolio_name': 'init',
                        'exit_order_link': 'init', 
                        'client_order_id': 'init',
                        'system_recon': True,
                        'req_qty': 0,
                        'filled_qty': 0,
                        'qty_available': 0,
                        'qty_available_running_close_adjustment': 'false',
                        'filled_avg_price': 0,
                        'price_time_of_request': 0,
                        'bid': 0,
                        'ask': 0,
                        'honey_gauge': deque([], 89),
                        'macd_gauge': deque([], 89),
                        '$honey': 0,
                        'origin_wave': {},
                        'assigned_wave': {},
                        'wave_at_creation': {},
                        'sell_reason': {},
                        'power_up': {},
                        'power_up_rangers': 0,
                        'honey_time_in_profit': {},
                        } 
    elif order['side'] == 'buy' or order['side'] == 'sell':
        # print("create buy running order")
        running_order = {'trading_model': trading_model,
                        'double_down_trade': order_vars['double_down_trade'],
                        'queen_order_state': 'submitted',
                        'side': order['side'],
                        'order_trig_buy_stop': True,
                        'order_trig_sell_stop': 'false',
                        'order_trig_sell_stop_limit': order_vars['order_trig_sell_stop_limit'],
                        'limit_price': order_vars['limit_price'],
                        'running_close_legs': 'false',
                        'symbol': order['symbol'], 
                        'order_rules': order_vars['king_order_rules'],
                        'origin_wave': order_vars['origin_wave'],
                        'wave_at_creation': order_vars['wave_at_creation'],
                        'assigned_wave': {},
                        'power_up': order_vars['power_up'],
                        'power_up_rangers': order_vars['power_up_rangers'], 
                        'ticker_time_frame_origin': order_vars['ticker_time_frame_origin'], 

                        'trigname': trig, 'datetime': date_mark,
                        'ticker_time_frame': ticker_time_frame,
                        'status_q': status_q,
                        'portfolio_name': portfolio_name,

                        'exit_order_link': exit_order_link, 
                        'client_order_id': order['client_order_id'],
                        'system_recon': False,
                        'req_qty': order['qty'],
                        'filled_qty': order['filled_qty'],
                        'qty_available': order['filled_qty'],
                        'qty_available_running_close_adjustment': order_vars['qty_available_running_close_adjustment'],

                        'filled_avg_price': order['filled_avg_price'],
                        'price_time_of_request': priceinfo['price'],
                        'bid': priceinfo['bid'],
                        'ask': priceinfo['ask'],
                        'honey_gauge': deque([], 89),
                        'macd_gauge': deque([], 89),
                        '$honey': 0,
                        'sell_reason': order_vars['sell_reason'],
                        'honey_time_in_profit': {},
                        }

    return running_order


def generate_TradingModel(portfolio_name='Jq', ticker='SPY', stars=stars, trading_model_name='tradingmodel1', status='active', portforlio_weight_ask=.01):
    
    def star_trading_model_vars(stars=stars):
        
        def kings_order_rules(status, doubledown_storylength, trade_using_limits, max_profit_waveDeviation, 
        timeduration, take_profit, sellout, sell_trigbee_trigger, stagger_profits, scalp_profits, scalp_profits_timeduration, stagger_profits_tiers):
            return {
            'status': status,
            'trade_using_limits': trade_using_limits,
            'doubledown_storylength': doubledown_storylength,
            'max_profit_waveDeviation': max_profit_waveDeviation,
            'timeduration': timeduration,
            'take_profit': take_profit,
            'sellout': sellout,
            'sell_trigbee_trigger': sell_trigbee_trigger,
            'stagger_profits': stagger_profits,
            'scalp_profits': scalp_profits,
            'scalp_profits_timeduration': scalp_profits_timeduration,
            'stagger_profits_tiers': stagger_profits_tiers,}

        def star_kings_order_rules_mapping(trigbees):
            star_kings_order_rules_dict = {}
            star_kings_order_rules_dict["1Minute_1Day"] = {}
            star_kings_order_rules_dict["5Minute_5Day"] = {}
            star_kings_order_rules_dict["30Minute_1Month"] = {}
            star_kings_order_rules_dict["1Hour_3Month"] = {}
            star_kings_order_rules_dict["2Hour_6Month"] = {}
            star_kings_order_rules_dict["1Day_1Year"] = {}

            for trigbee in trigbees:
                if trigbee == 'buy_cross-0':
                    star_kings_order_rules_dict["1Minute_1Day"][trigbee] =  kings_order_rules(status='active', trade_using_limits=False, doubledown_storylength=60, max_profit_waveDeviation=1, timeduration=33, take_profit=.005 , sellout=-.0089, sell_trigbee_trigger=True, stagger_profits=False, scalp_profits=False, scalp_profits_timeduration=30, stagger_profits_tiers=1)
                    star_kings_order_rules_dict["5Minute_5Day"][trigbee] =  kings_order_rules(status='active', trade_using_limits=False, doubledown_storylength=300, max_profit_waveDeviation=1, timeduration=33, take_profit=.005 , sellout=-.0089, sell_trigbee_trigger=True, stagger_profits=False, scalp_profits=False, scalp_profits_timeduration=30, stagger_profits_tiers=1)
                    star_kings_order_rules_dict["30Minute_1Month"][trigbee] =  kings_order_rules(status='active', trade_using_limits=False, doubledown_storylength=1800, max_profit_waveDeviation=1, timeduration=33, take_profit=.005 , sellout=-.0089, sell_trigbee_trigger=True, stagger_profits=False, scalp_profits=False, scalp_profits_timeduration=30, stagger_profits_tiers=1)
                    star_kings_order_rules_dict["1Hour_3Month"][trigbee] =  kings_order_rules(status='active', trade_using_limits=False, doubledown_storylength=3600, max_profit_waveDeviation=1, timeduration=33, take_profit=.005 , sellout=-.0089, sell_trigbee_trigger=True, stagger_profits=False, scalp_profits=False, scalp_profits_timeduration=30, stagger_profits_tiers=1)
                    star_kings_order_rules_dict["2Hour_6Month"][trigbee] =  kings_order_rules(status='active', trade_using_limits=False, doubledown_storylength=7200, max_profit_waveDeviation=1, timeduration=33, take_profit=.005 , sellout=-.0089, sell_trigbee_trigger=True, stagger_profits=False, scalp_profits=False, scalp_profits_timeduration=30, stagger_profits_tiers=1)
                    star_kings_order_rules_dict["1Day_1Year"][trigbee] =  kings_order_rules(status='active', trade_using_limits=False, doubledown_storylength=86400, max_profit_waveDeviation=1, timeduration=33, take_profit=.005 , sellout=-.0089, sell_trigbee_trigger=True, stagger_profits=False, scalp_profits=False, scalp_profits_timeduration=30, stagger_profits_tiers=1)

                elif trigbee == 'sell_cross-0':
                    star_kings_order_rules_dict["1Minute_1Day"][trigbee] =  kings_order_rules(status='active', trade_using_limits=False, doubledown_storylength=60, max_profit_waveDeviation=1, timeduration=33, take_profit=.005 , sellout=-.0089, sell_trigbee_trigger=True, stagger_profits=False, scalp_profits=False, scalp_profits_timeduration=30, stagger_profits_tiers=1)
                    star_kings_order_rules_dict["5Minute_5Day"][trigbee] =  kings_order_rules(status='active', trade_using_limits=False, doubledown_storylength=300, max_profit_waveDeviation=1, timeduration=33, take_profit=.005 , sellout=-.0089, sell_trigbee_trigger=True, stagger_profits=False, scalp_profits=False, scalp_profits_timeduration=30, stagger_profits_tiers=1)
                    star_kings_order_rules_dict["30Minute_1Month"][trigbee] =  kings_order_rules(status='active', trade_using_limits=False, doubledown_storylength=1800, max_profit_waveDeviation=1, timeduration=33, take_profit=.005 , sellout=-.0089, sell_trigbee_trigger=True, stagger_profits=False, scalp_profits=False, scalp_profits_timeduration=30, stagger_profits_tiers=1)
                    star_kings_order_rules_dict["1Hour_3Month"][trigbee] =  kings_order_rules(status='active', trade_using_limits=False, doubledown_storylength=3600, max_profit_waveDeviation=1, timeduration=33, take_profit=.005 , sellout=-.0089, sell_trigbee_trigger=True, stagger_profits=False, scalp_profits=False, scalp_profits_timeduration=30, stagger_profits_tiers=1)
                    star_kings_order_rules_dict["2Hour_6Month"][trigbee] =  kings_order_rules(status='active', trade_using_limits=False, doubledown_storylength=7200, max_profit_waveDeviation=1, timeduration=33, take_profit=.005 , sellout=-.0089, sell_trigbee_trigger=True, stagger_profits=False, scalp_profits=False, scalp_profits_timeduration=30, stagger_profits_tiers=1)
                    star_kings_order_rules_dict["1Day_1Year"][trigbee] =  kings_order_rules(status='active', trade_using_limits=False, doubledown_storylength=86400, max_profit_waveDeviation=1, timeduration=33, take_profit=.005 , sellout=-.0089, sell_trigbee_trigger=True, stagger_profits=False, scalp_profits=False, scalp_profits_timeduration=30, stagger_profits_tiers=1)

                elif trigbee == 'ready_buy_cross':
                    star_kings_order_rules_dict["1Minute_1Day"][trigbee] =  kings_order_rules(status='active', trade_using_limits=False, doubledown_storylength=60, max_profit_waveDeviation=1, timeduration=33, take_profit=.005 , sellout=-.0089, sell_trigbee_trigger=True, stagger_profits=False, scalp_profits=True, scalp_profits_timeduration=30, stagger_profits_tiers=1)
                    star_kings_order_rules_dict["5Minute_5Day"][trigbee] =  kings_order_rules(status='active', trade_using_limits=False, doubledown_storylength=300, max_profit_waveDeviation=1, timeduration=33, take_profit=.005 , sellout=-.0089, sell_trigbee_trigger=True, stagger_profits=False, scalp_profits=True, scalp_profits_timeduration=30, stagger_profits_tiers=1)
                    star_kings_order_rules_dict["30Minute_1Month"][trigbee] =  kings_order_rules(status='active', trade_using_limits=False, doubledown_storylength=1800, max_profit_waveDeviation=1, timeduration=33, take_profit=.005 , sellout=-.0089, sell_trigbee_trigger=True, stagger_profits=False, scalp_profits=True, scalp_profits_timeduration=30, stagger_profits_tiers=1)
                    star_kings_order_rules_dict["1Hour_3Month"][trigbee] =  kings_order_rules(status='active', trade_using_limits=False, doubledown_storylength=3600, max_profit_waveDeviation=1, timeduration=33, take_profit=.005 , sellout=-.0089, sell_trigbee_trigger=True, stagger_profits=False, scalp_profits=True, scalp_profits_timeduration=30, stagger_profits_tiers=1)
                    star_kings_order_rules_dict["2Hour_6Month"][trigbee] =  kings_order_rules(status='active', trade_using_limits=False, doubledown_storylength=7200, max_profit_waveDeviation=1, timeduration=33, take_profit=.005 , sellout=-.0089, sell_trigbee_trigger=True, stagger_profits=False, scalp_profits=True, scalp_profits_timeduration=30, stagger_profits_tiers=1)
                    star_kings_order_rules_dict["1Day_1Year"][trigbee] =  kings_order_rules(status='active', trade_using_limits=False, doubledown_storylength=86400, max_profit_waveDeviation=1, timeduration=33, take_profit=.005 , sellout=-.0089, sell_trigbee_trigger=True, stagger_profits=False, scalp_profits=True, scalp_profits_timeduration=30, stagger_profits_tiers=1)

            return star_kings_order_rules_dict

        def star_vars_mapping(trigbees, stars=stars):
            return_dict = {}
            trigbees_king_order_rules = star_kings_order_rules_mapping(trigbees=trigbees)

            star = '1Minute_1Day'
            return_dict[star] = {'status': 'active', 'trade_using_limits': False,
                                    'total_budget': 100,
                                    'buyingpower_allocation_LongTerm': .2,
                                    'buyingpower_allocation_ShortTerm': .8,
                                    'power_rangers': {k: 'active' for k in stars().keys() if k in list(stars().keys())},
                                    'trigbees': trigbees_king_order_rules[star], 
            }

            star = '5Minute_5Day'
            return_dict[star] = {'status': 'active', 'trade_using_limits': False,
                                    'total_budget': 100,
                                    'buyingpower_allocation_LongTerm': .2,
                                    'buyingpower_allocation_ShortTerm': .8,
                                    'power_rangers': {k: 'active' for k in stars().keys() if k in list(stars().keys())},
                                    'trigbees': trigbees_king_order_rules[star]}



            star = '30Minute_1Month'
            return_dict[star] = {'status': 'active', 'trade_using_limits': False,
                                    'total_budget': 100,
                                    'buyingpower_allocation_LongTerm': .2,
                                    'buyingpower_allocation_ShortTerm': .8,
                                    'power_rangers': {k: 'active' for k in stars().keys() if k in list(stars().keys())},
                                    'trigbees': trigbees_king_order_rules[star]}

            
            
            star = '1Hour_3Month'
            return_dict[star] = {'status': 'active', 'trade_using_limits': False,
                                    'total_budget': 100,
                                    'buyingpower_allocation_LongTerm': .2,
                                    'buyingpower_allocation_ShortTerm': .8,
                                    'power_rangers': {k: 'active' for k in stars().keys() if k in list(stars().keys())},
                                    'trigbees': trigbees_king_order_rules[star]}



            star = '2Hour_6Month'
            return_dict[star] = {'status': 'active', 'trade_using_limits': False,
                                    'total_budget': 100,
                                    'buyingpower_allocation_LongTerm': .2,
                                    'buyingpower_allocation_ShortTerm': .8,
                                    'power_rangers': {k: 'active' for k in stars().keys() if k in list(stars().keys())},
                                    'trigbees': trigbees_king_order_rules[star]}

            
            star = '1Day_1Year'
            return_dict[star] = {'status': 'active', 'trade_using_limits': False,
                                    'total_budget': 100,
                                    'buyingpower_allocation_LongTerm': .2,
                                    'buyingpower_allocation_ShortTerm': .8,
                                    'power_rangers': {k: 'active' for k in stars().keys() if k in list(stars().keys())},
                                    'trigbees': trigbees_king_order_rules[star]}

            
            
            return return_dict

        def star_vars(star, star_vars_mapping):
            
            return {'star': star,
            'status': star_vars_mapping[star]['status'],
            'trade_using_limits': star_vars_mapping[star]['trade_using_limits'],
            'total_budget': star_vars_mapping[star]['total_budget'],
            'buyingpower_allocation_LongTerm': star_vars_mapping[star]['buyingpower_allocation_LongTerm'],
            'buyingpower_allocation_ShortTerm': star_vars_mapping[star]['buyingpower_allocation_ShortTerm'],
            'power_rangers': star_vars_mapping[star]['power_rangers'],
            'trigbees': star_vars_mapping[star]['trigbees']}
        
        # default_king_order_rules = kings_order_rules(status='active', trade_using_limits=False, doubledown_storylength=60, max_profit_waveDeviation=1, timeduration=33, take_profit=.005 , sellout=-.0089, sell_trigbee_trigger=True, stagger_profits=False, scalp_profits=True)

        all_stars = stars().keys()
        trigbees = ['buy_cross-0', 'sell_cross-0', 'ready_buy_cross']
        star_vars_mapping_dict = star_vars_mapping(trigbees=trigbees, stars=stars)
        
        return_dict = {star: star_vars(star=star, star_vars_mapping=star_vars_mapping_dict) for star in all_stars}
        
        return return_dict


    def model_vars(trading_model_name, star, stars_vars):
        return {'status': stars_vars[star]['status'], 
                'buyingpower_allocation_LongTerm': stars_vars[star]['buyingpower_allocation_LongTerm'], 
                'buyingpower_allocation_ShortTerm': stars_vars[star]['buyingpower_allocation_ShortTerm'], 
                'power_rangers': stars_vars[star]['power_rangers'],
                'trade_using_limits': stars_vars[star]['trade_using_limits'],
                'total_budget': stars_vars[star]['total_budget'],
                'trigbees': stars_vars[star]['trigbees'],
                'index_inverse_X': '1X',
                'index_long_X': '1X',
                'trading_model_name': trading_model_name,
    }
    
    def tradingmodel_vars(stars_vars, ticker=ticker, trading_model_name=trading_model_name, status=status, portforlio_weight_ask=portforlio_weight_ask, stars=stars):
        return {
            ticker: 
                {star: model_vars(trading_model_name=trading_model_name, star=star, stars_vars=stars_vars) for star in stars().keys()},
                'ticker': ticker,
                'status': status,
                'portforlio_weight_ask': portforlio_weight_ask,
                'trading_model_name': trading_model_name,
                'portfolio_name': portfolio_name,
        }

    # Trading Model Version 1
    stars_vars = star_trading_model_vars()
    tradingmodel1 = tradingmodel_vars(stars_vars=stars_vars)

    return {'tradingmodel1': tradingmodel1}


def heartbeat_portfolio_revrec_template(QUEEN, portforlio_name='Jq'):
    # buying_powers
    # buying power item
                
    # adjust ticker weight with current QueenRevRec
    # df = pd.DataFrame(QUEEN['queen_controls']['symbols_stars_TradingModel'])
    # for ticker in df['ticker'].to_list():
    #     if ticker not in QUEEN['queen_controls']['ticker_settings'].keys():
    #         add_ticker_settings = generate_queen_ticker_settings(portforlio_name='Jq', ticker=ticker, portforlio_weight=.1, day_theme_throttle=.75, long_theme_throttle=.55)
    #         reduce_tickers = add_ticker_settings['portforlio_weight'] / sum(np.where(df['status'] == 'active',1 ,0))
    #         df['new_weight'] = df['portforlio_weight'] - reduce_tickers
    # df = pd.DataFrame(QUEEN['queen_controls']['ticker_settings'].items())
    # df = df.T
    # headers = df.iloc[0].values
    # df.columns = headers
    # df.drop(index=0, axis=0, inplace=True)
    # for ticker, tradingmodel in QUEEN['queen_controls']['symbols_stars_TradingModel'].items():
    #     if ticker not in df['ticker'].tolist():
    #         add_ticker_settings = generate_queen_ticker_settings(portforlio_name='Jq', status='active', ticker=ticker, portforlio_weight=.1, day_theme_throttle=.75, long_theme_throttle=.55)
    #         reduce_tickers = add_ticker_settings['portforlio_weight'] / sum(np.where(df['status'] == 'active',1 ,0))
    #         df['portforlio_weight'] = df['portforlio_weight'] - reduce_tickers
    #         QUEEN['queen_controls']['ticker_settings'] = df.T.to_dict()[0]
    #         QUEEN['queen_controls']['ticker_settings'].update(add_ticker_settings)

    # for ticker, tradingmodel in QUEEN['queen_controls']['symbols_stars_TradingModel'].items():
    #     if ticker not in QUEEN['queen_controls']['ticker_settings'].keys():
    #         add_ticker_settings = generate_queen_ticker_settings(portforlio_name='Jq', status='active', ticker=ticker, portforlio_weight=.1, day_theme_throttle=.75, long_theme_throttle=.55)
    #         reduce_tickers = add_ticker_settings['portforlio_weight'] / len([i for k, i in QUEEN['queen_controls']['ticker_settings'].items() if i['status']=='active'])
    #         for ticker2 in QUEEN['queen_controls']['ticker_settings'].keys()
    #             if QUEEN['queen_controls']['ticker_settings'][ticker2]['portforlio_weight'] > reduce_tickers:
    #                 QUEEN['queen_controls']['ticker_settings'][ticker2]['portforlio_weight'] = QUEEN['queen_controls']['ticker_settings'][ticker2]['portforlio_weight'] - reduce_tickers
            
    #         QUEEN['queen_controls']['ticker_settings'] = {df.T.to_dict()[0]}
    #         QUEEN['queen_controls']['ticker_settings'].update(add_ticker_settings)

    # rebalance based on total budget???          
    
    # for ticker in settings check for new models and if they are active, ReAllocate weight and return star powers
    
    return True


def generate_queen_buying_powers_settings(portfolio_name='Jq', total_dayTrade_allocation=.5, total_longTrade_allocation=.5):
    return {portfolio_name: {
    'portfolio_name': portfolio_name,
    'total_dayTrade_allocation': total_dayTrade_allocation,
    'total_longTrade_allocation': total_longTrade_allocation,}
    }


def generate_queen_ticker_settings(ticker='SPY', status='active', portforlio_name='Jq', portforlio_weight=1, day_theme_throttle=.33, long_theme_throttle=.33):
    return {
    portforlio_name: {
    'portforlio_name': portforlio_name,
    'ticker': ticker,
    'status': status,
    'portforlio_weight': portforlio_weight,
    'day_theme_throttle': day_theme_throttle,
    'long_theme_throttle': long_theme_throttle,}
    }


# def theme_throttle():
#     return_dict = {f'{num}{"X"}': num * .01 for num in range(1, 100)}
    
#     return return_dict


def return_queen_controls(stars=stars):
    num_of_stars = len(stars())
    queen_controls_dict = { 
            'theme': 'nuetral',
            'last_read_app': datetime.datetime.now(),
            'stars': stars(),
            'ticker_settings': generate_queen_ticker_settings(),
            'buying_powers': generate_queen_buying_powers_settings(),

            # Trading Model and Child Components Worker Bee Controls
            'symbols_stars_TradingModel': generate_TradingModel()['tradingmodel1'],
            'power_rangers': init_PowerRangers(),
            'max_profit_waveDeviation': {star_time: 2 for star_time in stars().keys()},

            # Worker Bees UPDATE TO PER TICKER on Ticker Settings
            'MACD_fast_slow_smooth': {'fast': 12, 'slow': 26, 'smooth': 9},
            'macd_worlds' : {
                'crypto': 
                    {'macd': {"1Minute": 10, "5Minute": 10, "30Minute": 20, "1Hour": 50, "2Hour": 50, "1Day": 50},
                    'hist': {"1Minute": 1, "5Minute": 1, "30Minute": 5, "1Hour": 5, "2Hour": 10, "1Day": 10}},
                
                'default': 
                    {'macd': {"1Minute": 1, "5Minute": 1, "30Minute": 2, "1Hour": 5, "2Hour": 5, "1Day": 5},
                    'hist': {"1Minute": 1, "5Minute": 1, "30Minute": 2, "1Hour": 5, "2Hour": 5, "1Day": 5}},
                },

    
    }
    return queen_controls_dict


def init_QUEEN(queens_chess_piece):
    KING = KINGME()
    num_of_stars = len(stars())
    QUEEN = { # The Queens Mind
        'prod': "",
        'source': "na",
        'last_modified': datetime.datetime.now(),
        'command_conscience': {},
        'queen_orders': [create_QueenOrderBee(trading_model='false', KING=KING, queen_init=True, order_vars=False, order=False, ticker_time_frame=False, portfolio_name=False, status_q=False, trig=False, exit_order_link=False, priceinfo=False)],
        'portfolios': {'Jq': {'total_investment': 0, 'currnet_value': 0}},
        'heartbeat': {'active_tickerStars': {}, 'available_tickers': [], 'active_tickers': [], 'available_triggerbees': []}, # ticker info ... change name
        'kings_order_rules': {},
        'queen_controls': return_queen_controls(stars),
        'workerbees': {
            'castle': {'MACD_fast_slow_smooth': {'fast': 12, 'slow': 26, 'smooth': 9},
                        'tickers': ['SPY'],
                        'stars': stars(),},
            'bishop': {'MACD_fast_slow_smooth': {'fast': 12, 'slow': 26, 'smooth': 9},
                        'tickers': ['META', 'GOOG', 'HD'],
                        'stars': stars(),},
            'knight': {'MACD_fast_slow_smooth': {'fast': 12, 'slow': 26, 'smooth': 9},
                        'tickers': ['META', 'GOOG', 'HD'],
                        'stars': stars(),},
            'castle_coin': {'MACD_fast_slow_smooth': {'fast': 12, 'slow': 26, 'smooth': 9},
                        'tickers': ['BTCUSD', 'ETHUSD'],
                        'stars': stars(),},
            },
        'errors': {},
        'client_order_ids_qgen': [],
        'app_requests__bucket': [],
        # 'triggerBee_frequency': {}, # hold a star and the running trigger
        'saved_pollenThemes': [], # bucket of saved star settings to choose from
        'saved_powerRangers': [], # bucket of saved star settings to choose from
        'subconscious': {},
        # Worker Bees
        queens_chess_piece: {
        'conscience': {'STORY_bee': {},'KNIGHTSWORD': {}, 'ANGEL_bee': {}}, # 'command_conscience': {}, 'memory': {}, 'orders': []}, # change knightsword
        'pollenstory': {}, # latest story of dataframes castle and bishop
        'pollencharts': {}, # latest chart rebuild
        'pollencharts_nectar': {}, # latest chart rebuild with indicators
        'pollenstory_info': {}, # Misc Info,
        'client': {},
        # 'heartbeat': {},
        'last_modified' : datetime.datetime.now(),
        }
    }
    return QUEEN


def init_QUEEN_App():
    app = {'theme': 'nuetral', 
    'app_order_requests': [], 
    'sell_orders': [], 'buy_orders': [], 
    'last_modified': {'last_modified': datetime.datetime.now().astimezone(est)},
    'queen_processed_orders': [],
    'wave_triggers': [],
    'app_wave_requests': [],
    'trading_models': [],
    'trading_models_requests': [],
    'power_rangers': [],
    'power_rangers_requests': [],
    'power_rangers_lastupdate': datetime.datetime.now().astimezone(est),
    'knight_bees_kings_rules': [],
    'knight_bees_kings_rules_requests': [],
    'queen_controls_reset': 'false', 
    'queen_controls': [],
    'queen_controls_requests': [],
    'queen_contorls_lastupdate': 'false', 
    'del_QUEEN_object': [],
    'del_QUEEN_object_requests': [],
    'last_app_update': datetime.datetime.now(), ## Update Time Zone... Low Priority
    'update_queen_order': [],
    'update_queen_order_requests': [],
    'savedstars': [],
    'misc_bucket': [],
    'source': 'na',
    'stop_queen' : 'false',
    }
    return app


def add_key_to_app(APP_requests): # returns QUEES
    q_keys = APP_requests.keys()
    latest_queen = init_QUEEN_App()
    update=False
    for k, v in latest_queen.items():
        if k not in q_keys:
            APP_requests[k] = v
            update=True
            msg = f'{k}{" : Key Added"}'
            print(msg)
            logging.info(msg)
    return {'APP_requests': APP_requests, 'update': update}


def add_key_to_QUEEN(QUEEN, queens_chess_piece): # returns QUEEN
    update = False
    q_keys = QUEEN.keys()
    latest_queen = init_QUEEN('queen')
    for k, v in latest_queen.items():
        if k not in q_keys:
            QUEEN[k] = v
            update=True
            msg = f'{k}{" : Key Added to "}{queens_chess_piece}'
            print(msg)
            logging.info(msg)
    
    for k, v in latest_queen['queen_controls'].items():
        if k not in QUEEN['queen_controls'].keys():
            QUEEN['queen_controls'][k] = v
            update=True
            msg = f'{k}{" : queen controls Key Added to "}{queens_chess_piece}'
            print(msg)
            logging.info(msg)

    for k, v in latest_queen['heartbeat'].items():
        if k not in QUEEN['heartbeat'].keys():
            QUEEN['heartbeat'][k] = v
            update=True
            msg = f'{k}{" : queen heartbeat Key Added to "}{queens_chess_piece}'
            print(msg)
            logging.info(msg)

    for k, v in latest_queen['workerbees'].items():
        if k not in QUEEN['workerbees'].keys():
            QUEEN['workerbees'][k] = v
            update=True
            msg = f'{k}{" : queen workerbees Key Added to "}{queens_chess_piece}'
            print(msg)
            logging.info(msg)

    return {'QUEEN': QUEEN, 'update': update}


def logging_log_message(log_type='info', msg='default', error='none', origin_func='default', ticker='false'):
    if log_type == 'error':
        return {'msg': msg, 'error': error, 'origin_func': origin_func, 'ticker': ticker}
    if log_type == 'critical':
        return {'msg': msg, 'error': error, 'origin_func': origin_func, 'ticker': ticker}


def return_Best_Waves(df, rankname='maxprofit', top=False):
    if top:
        df = df.sort_values(rankname)
        return df.tail(top)
    else:
        df = df.sort_values(rankname)
        return df

def analyze_waves(STORY_bee, ttframe_wave_trigbee=False):
    # len and profits
    groupby_agg_dict = {'winners_n': 'sum', 'losers_n': 'sum', 'maxprofit': 'sum', 'length': 'mean', 'time_to_max_profit': 'mean'}
    # groupby_agg_dict = {'maxprofit': 'sum', 'length': 'mean', 'time_to_max_profit': 'mean'}


    if ttframe_wave_trigbee:
        # buy_cross-0
        wave_series = STORY_bee[ttframe_wave_trigbee]['waves']['buy_cross-0']
        upwave_dict = [wave_data for (k, wave_data) in wave_series.items() if k != '0']
        df = pd.DataFrame(upwave_dict)
        df['winners'] = np.where(df['maxprofit'] > 0, 'winner', 'loser')
        df['winners_n'] = np.where(df['maxprofit'] > 0, 1, 0)
        df['losers_n'] = np.where(df['maxprofit'] < 0, 1, 0)
        df['winners'] = np.where(df['maxprofit'] > 0, 'winner', 'loser')
        groups = df.groupby(['wave_blocktime']).agg({'maxprofit': 'sum', 'length': 'mean', 'time_to_max_profit': 'mean'}).reset_index()
        df_return = groups.rename(columns={'length': 'avg_length', 'time_to_max_profit': 'avg_time_to_max_profit', 'maxprofit': 'sum_maxprofit'})

        df_bestwaves = return_Best_Waves(df=df, top=3)

        # # show today only
        df_today_return = pd.DataFrame()
        # ipdb.set_trace()
        df_today = split_today_vs_prior(df=df, other_timestamp='wave_start_time')['df_today']
        df_day_bestwaves = return_Best_Waves(df=df_today, top=3)
        groups = df_today.groupby(['wave_blocktime']).agg({'maxprofit': 'sum', 'length': 'mean', 'time_to_max_profit': 'mean'}).reset_index()
        df_today_return = groups.rename(columns={'length': 'avg_length', 'time_to_max_profit': 'avg_time_to_max_profit', 'maxprofit': 'sum_maxprofit'})


        # sell_cross-0
        wave_series = STORY_bee[ttframe_wave_trigbee]['waves']['sell_cross-0']
        upwave_dict = [wave_data for (k, wave_data) in wave_series.items() if k != '0']
        df = pd.DataFrame(upwave_dict)
        df['winners'] = np.where(df['maxprofit'] > 0, 'winner', 'loser')
        df['winners_n'] = np.where(df['maxprofit'] > 0, 1, 0)
        df['losers_n'] = np.where(df['maxprofit'] < 0, 1, 0)
        groups = df.groupby(['wave_blocktime']).agg({'winners_n': 'sum', 'losers_n': 'sum', 'maxprofit': 'sum', 'length': 'mean', 'time_to_max_profit': 'mean'}).reset_index()
        df_return_wavedown = groups.rename(columns={'length': 'avg_length', 'time_to_max_profit': 'avg_time_to_max_profit', 'maxprofit': 'sum_maxprofit'})
        
        df_bestwaves_sell_cross = return_Best_Waves(df=df, top=3)

        df_best_buy__sell__waves = pd.concat([df_bestwaves, df_bestwaves_sell_cross], axis=0)

        return {'df': df_return, 
        'df_wavedown': df_return_wavedown, 
        'df_today': df_today_return,
        'df_bestwaves': df_bestwaves,
        'df_bestwaves_sell_cross': df_bestwaves_sell_cross,
        'df_day_bestwaves': df_day_bestwaves, 
        'df_best_buy__sell__waves': df_best_buy__sell__waves,}
    else:
        df_bestwaves = pd.DataFrame()
        d_return = {} # every star and the data by grouping
        d_agg_view_return = {} # every star and the data by grouping

        for symbol_star, data in STORY_bee.items():
            try:
                d_return[symbol_star] = {}
                d_agg_view_return[symbol_star] = {}
                
                waves = data['waves']
                for trigbee, wave in waves.items():
                    if trigbee == 'story':
                        continue
                    else:
                        d_wave = [wave_data for (k, wave_data) in wave.items() if k != '0']
                        df = pd.DataFrame(d_wave)
                        if len(df) > 0:
                            df['winners'] = np.where(df['maxprofit'] > 0, 'winner', 'loser')
                            df['winners'] = np.where(df['maxprofit'] > 0, 'winner', 'loser')
                            df['winners_n'] = np.where(df['maxprofit'] > 0, 1, 0)
                            df['losers_n'] = np.where(df['maxprofit'] < 0, 1, 0)
                            
                            groups = df.groupby(['wave_blocktime']).agg(groupby_agg_dict).reset_index()
                            groups = groups.rename(columns={'length': 'avg_length', 'time_to_max_profit': 'avg_time_to_max_profit', 'maxprofit': 'sum_maxprofit'})
                            d_return[symbol_star][trigbee] = groups

                            groups = df.groupby(['trigbee', 'wave_blocktime']).agg(groupby_agg_dict).reset_index()
                            groups = groups.rename(columns={'length': 'avg_length', 'time_to_max_profit': 'avg_time_to_max_profit', 'maxprofit': 'sum_maxprofit'})
                            groups['ticker_time_frame'] = symbol_star
                            d_agg_view_return[symbol_star][f'{trigbee}'] = groups


            except Exception as e:
                print(e)
        

        # 
    
        df_return = pd.DataFrame(d_return)
        df_agg_view_return = pd.DataFrame(d_agg_view_return)
        df_agg_view_return = df_agg_view_return.T

    
    # d_return2 = {} # every star and the data by grouping
    # for symbol_star, data in STORY_bee.items():
    #     d_return[symbol_star] = {}
    #     waves = data['waves']['story']
    #     df = pd.DataFrame(waves)
    #     # df = df[~df['macd_wave_length'] == 'NULL'].copy()
    #     if len(df) > 0:
    #         df['winners'] = np.where(df['maxprofit'] > 0, 'winner', 'loser')
    #         groups = df.groupby(['wave_blocktime']).agg({'maxprofit': 'sum', 'length': 'mean', 'time_to_max_profit': 'mean'}).reset_index()
    #         groups = groups.rename(columns={'length': 'avg_length'})
    #         d_return[symbol_star][trigbee] = groups


    return {'df': d_return, 
    'd_agg_view_return': d_agg_view_return,
    'df_agg_view_return': df_agg_view_return,
    'df_bestwaves': df_bestwaves}


def story_view(STORY_bee, ticker): # --> returns dataframe
    storyview = ['ticker_time_frame', 'macd_state', 'current_macd_tier', 'current_hist_tier', 'macd', 'hist', 'mac_ranger', 'hist_ranger']
    wave_view = ['length', 'maxprofit', 'time_to_max_profit', 'wave_n']
    ttframe__items = {k:v for (k,v) in STORY_bee.items() if k.split("_")[0] == ticker}
    return_view = [] # queenmemory objects in conscience {}
    return_agg_view = []
    for ttframe, conscience in ttframe__items.items():
        queen_return = {'star': ttframe}

        trigbees = ['buy_cross-0', 'sell_cross-0']

        buys = conscience['waves']['buy_cross-0']
        # max profit


        story = {k: v for (k,v) in conscience['story'].items() if k in storyview}
        last_buy_wave = [v for (k,v) in conscience['waves']['buy_cross-0'].items() if str((len(conscience['waves']['buy_cross-0'].keys()) - 1)) == str(k)][0]
        last_sell_wave = [v for (k,v) in conscience['waves']['sell_cross-0'].items() if str((len(conscience['waves']['sell_cross-0'].keys()) - 1)) == str(k)][0]
        p_story = {k: v for (k,v) in conscience['story']['current_mind'].items() if k in storyview}

        all_buys = [v for (k,v) in conscience['waves']['buy_cross-0'].items()]
        all_sells = [v for (k,v) in conscience['waves']['sell_cross-0'].items()]

        # ALL waves groups
        trigbee_waves_analzyed = analyze_waves(STORY_bee, ttframe_wave_trigbee=ttframe)
        return_agg_view.append(trigbee_waves_analzyed)

        # Current Wave View
        if 'buy' in story['macd_state']:
            current_wave = last_buy_wave
        else:
            current_wave = last_sell_wave
        
        current_wave_view = {k: v for (k,v) in current_wave.items() if k in wave_view}
        obj_return = {**story, **current_wave_view}
        obj_return_ = {**obj_return, **p_story}
        queen_return = {**queen_return, **obj_return_}
        """append view"""
        return_view.append(queen_return)
    
    
    df =  pd.DataFrame(return_view)
    df_agg = pd.DataFrame(return_agg_view)
    # map in ranger color
    # df['mac_ranger'] = df['current_mac_tier'].apply(lambda x: power_ranger_mapping(x))
    # df['hist_ranger'] = df['current_hist_tier'].apply(lambda x: power_ranger_mapping(x))


    return {'df': df, 'df_agg': df_agg, 'current_wave': current_wave}


def queen_orders_view(QUEEN, queen_order_state, cols_to_view=False, return_all_cols=False):
    if cols_to_view:
        col_view = col_view
    else:
        col_view = ['trigname', 'ticker_time_frame', 'filled_avg_price', 'cost_basis', 'honey', '$honey', 'profit_loss', 'status_q', 'client_order_id', 'queen_order_state']
    if len(QUEEN['queen_orders']) > 0:
        orders = [i for i in QUEEN['queen_orders'] if i['queen_order_state'] == queen_order_state]
        df = pd.DataFrame(orders)
        # df = df.astype(str)
        if len(df) > 0:
            # df["honey"] = df["honey"] * 100
            if 'profit_loss' in df.columns:
                df["profit_loss"] = df['profit_loss'].map("{:.2f}".format)
            if "honey" in df.columns:
                df["honey"] = df['honey'].map("{:.2%}".format)
            if "cost_basis" in df.columns:
                df["cost_basis"] = df['cost_basis'].map("{:.2f}".format)

            col_view = [i for i in col_view if i in df.columns]
            df_return = df[col_view].copy()
        else:
            df_return = df
        
        if return_all_cols and len(df_return) > 0:
            all_cols = col_view + [i for i in df.columns.tolist() if i not in col_view]
            df_return = df[all_cols].copy()

        df_return = df_return.astype(str)
        
        return {'df': df_return}
    else:
        return {'df': pd.DataFrame()}


def power_ranger_mapping(tier_value,  colors=['red', 'blue', 'pink', 'yellow', 'white', 'green', 'orange', 'purple', 'black']):

    # When 1M macd tier in range (-7, -5) + 50% : Red // Sell :: 1%
    # When 1M macd tier in range (-5, -3) + 40% : Blue // Sell :: 1%
    # When 1M macd tier in range (-3, -2) + 25% : Pink // Sell :: 1%
    # When 1M macd tier in range (-2, -1) + 10% : Yellow // Sell :: 1%
    # When 1M macd tier in range (-1, 1) + 1% : White // Sell :: 1%
    # When 1M macd tier in range (1, 2) + 1% : Green // Sell :: 1%
    # When 1M macd tier in range (2, 3) + 1% : orange // Sell :: 25%
    # When 1M macd tier in range (3, 5) + 1% : purple // Sell :: 40%
    # When 1M macd tier in range (5, 7) + 1% : Black // Sell :: 50%

    tier_value = float(tier_value)
    
    if tier_value >= -8 and tier_value <=-7:
        return 'red'
    elif tier_value >=-6 and tier_value <=-5:
        return 'blue'
    elif tier_value >=-4 and tier_value <=-3:
        return 'pink'
    elif tier_value >=-2 and tier_value <=-1:
        return 'yellow'
    elif tier_value >-1 and tier_value <=1:
        return 'white'
    elif tier_value >=2 and tier_value <=3:
        return 'green'
    elif tier_value >=4 and tier_value <=5:
        return 'purple'
    elif tier_value >=6 and tier_value >=7:
        return 'black'
    else:
        return 'black'



def init_PowerRangers(ranger_dimensions=False):
    # ranger = '1Minute_1Day'
    # stars = ['1Minute_1Day', '5Minute_5Day', '30Minute_1Month', '1Hour_3Month', '2Hour_6Month', '1Day_1Year']
    # trigbees = ['buy_wave', 'sell_wave']
    # theme_list = ['nuetral', 'strong']
    # colors = ['red', 'blue', 'pink', 'yellow', 'white', 'green', 'orange', 'purple', 'black']
    # bee_ranger_tiers = 9

    # BUY_Cross
    # When 1M macd tier in range (-7, -5) + 50% : Red // Sell :: 1%
    # When 1M macd tier in range (-5, -3) + 40% : Blue // Sell :: 1%
    # When 1M macd tier in range (-3, -2) + 25% : Pink // Sell :: 1%
    # When 1M macd tier in range (-2, -1) + 10% : Yellow // Sell :: 1%
    # When 1M macd tier in range (-1, 1) + 1% : White // Sell :: 1%
    # When 1M macd tier in range (1, 2) + 1% : Green // Sell :: 1%
    # When 1M macd tier in range (2, 3) + 1% : orange // Sell :: 25%
    # When 1M macd tier in range (3, 5) + 1% : purple // Sell :: 40%
    # When 1M macd tier in range (5, 7) + 1% : Black // Sell :: 50%


    if ranger_dimensions:
        stars = ranger_dimensions['stars'] #  = ['1Minute_1Day', '5Minute_5Day', '30Minute_1Month', '1Hour_3Month', '2Hour_6Month', '1Day_1Year']
        trigbees = ranger_dimensions['trigbees'] # = ['buy_wave', 'sell_wave']
        theme_list = ranger_dimensions['theme_list'] # theme_list = ['nuetral', 'strong']
        colors = ranger_dimensions['colors'] # colors = ['red', 'blue', 'pink', 'yellow', 'white', 'green', 'orange', 'purple', 'black']
        wave_types = ranger_dimensions['wave_types']
        # bee_ranger_tiers = 9
        ranger_init = ranger_dimensions['ranger_init']
    else:
        wave_types = ['mac_ranger', 'hist_ranger']
        stars = ['1Minute_1Day', '5Minute_5Day', '30Minute_1Month', '1Hour_3Month', '2Hour_6Month', '1Day_1Year']
        trigbees = ['buy_wave', 'sell_wave']
        theme_list = ['nuetral', 'strong']
        colors = ['red', 'blue', 'pink', 'yellow', 'white', 'green', 'orange', 'purple', 'black']

        ## FEAT REQUEST: adjust upstream to include universe
        ranger_init = {
        'mac_ranger' : {'buy_wave': {'nuetral': 
                                            {'red': .05, 'blue': .04, 'pink': .025, 'yellow': .01, 'white': .01, 'green': .01, 'orange': .01, 'purple': .01, 'black': .001},
                                        'strong': 
                                            {'red': .05, 'blue': .04, 'pink': .025, 'yellow': .01, 'white': .01, 'green': .01, 'orange': .01, 'purple': .01, 'black': .001},
                                    },
                    'sell_wave': {'nuetral': 
                                        {'red': .001, 'blue': .001, 'pink': .01, 'yellow': .01, 'white': .03, 'green': .01, 'orange': .01, 'purple': .01, 'black': .01},
                                    'strong': 
                                        {'red': .05, 'blue': .04, 'pink': .025, 'yellow': .01, 'white': .01, 'green': .01, 'orange': .01, 'purple': .01, 'black': .01},
                                        }
                },
        'hist_ranger' : {'buy_wave': {'nuetral': 
                                            {'red': .05, 'blue': .04, 'pink': .025, 'yellow': .01, 'white': .01, 'green': .01, 'orange': .01, 'purple': .01, 'black': .001},
                                        'strong': 
                                            {'red': .05, 'blue': .04, 'pink': .025, 'yellow': .01, 'white': .01, 'green': .01, 'orange': .01, 'purple': .01, 'black': .001},
                                    },
                    'sell_wave': {'nuetral': 
                                        {'red': .001, 'blue': .001, 'pink': .01, 'yellow': .01, 'white': .03, 'green': .01, 'orange': .01, 'purple': .01, 'black': .01},
                                    'strong': 
                                        {'red': .05, 'blue': .04, 'pink': .025, 'yellow': .01, 'white': .05, 'green': .01, 'orange': .01, 'purple': .01, 'black': .01},
                                        }
                },
        }

    r_dict = {}
    for star in stars:
        r_dict[star] = {}
        for wave_type in wave_types:
            r_dict[star][wave_type] = {}
            for trigbee in trigbees:
                r_dict[star][wave_type][trigbee] = {}
                for theme in theme_list:
                    r_dict[star][wave_type][trigbee][theme] = {}
                    for color in colors:
                        r_dict[star][wave_type][trigbee][theme][color] = ranger_init[wave_type][trigbee][theme][color]
 
    return r_dict


def init_pollen_dbs(db_root, api, prod, queens_chess_piece):
    
    if prod:
        api = api
        main_orders_file = os.path.join(db_root, 'main_orders.csv')
        PB_QUEEN_Pickle = os.path.join(db_root, f'{queens_chess_piece}{".pkl"}')
        PB_KING_Pickle = os.path.join(db_root, f'{"KING"}{".pkl"}')
        PB_App_Pickle = os.path.join(db_root, f'{queens_chess_piece}{"_App_"}{".pkl"}')
        PB_Orders_Pickle = os.path.join(db_root, f'{queens_chess_piece}{"_Orders_"}{".pkl"}')


        if 'queen' in queens_chess_piece:
            if os.path.exists(PB_QUEEN_Pickle) == False:
                QUEEN = init_QUEEN(queens_chess_piece=queens_chess_piece)
                PickleData(pickle_file=PB_QUEEN_Pickle, data_to_store=QUEEN)
                print("You Need a Queen")
                logging.info(("queen created", timestamp_string()))
            # sys.exit()
            if os.path.exists(PB_App_Pickle) == False:
                init_app(pickle_file=PB_App_Pickle)
            # if os.path.exists(PB_Orders_Pickle) == False:
            #     init_app(pickle_file=PB_Orders_Pickle)
        print("My Queen Production")
    else:
        api = api_paper
        main_orders_file = os.path.join(db_root, 'main_orders_sandbox.csv')
        PB_QUEEN_Pickle = os.path.join(db_root, f'{queens_chess_piece}{"_sandbox"}{".pkl"}')
        PB_App_Pickle = os.path.join(db_root, f'{queens_chess_piece}{"_App_"}{"_sandbox"}{".pkl"}')
        PB_Orders_Pickle = os.path.join(db_root, f'{queens_chess_piece}{"_Orders_"}{"_sandbox"}{".pkl"}')

        if 'queen' in queens_chess_piece:
            if os.path.exists(PB_QUEEN_Pickle) == False:
                QUEEN = init_QUEEN(queens_chess_piece=queens_chess_piece)
                PickleData(pickle_file=PB_QUEEN_Pickle, data_to_store=QUEEN)
                print("You Need a Queen__sandbox")
                logging.info(("queen created", timestamp_string()))
                # sys.exit()
            
            if os.path.exists(PB_App_Pickle) == False:
                init_app(pickle_file=PB_App_Pickle)
            
            # if os.path.exists(PB_Orders_Pickle) == False:
            #     init_app(pickle_file=PB_Orders_Pickle)
        print("My Queen Sandbox")
    
    return {'PB_QUEEN_Pickle': PB_QUEEN_Pickle, 'PB_App_Pickle': PB_App_Pickle}







### NEEDS TO BE WORKED ON TO ADD TO WORKERBEE
def speedybee(QUEEN, queens_chess_piece, ticker_list): # if queens_chess_piece.lower() == 'workerbee': # return tics
    ticker_list = ['AAPL', 'TSLA', 'GOOG', 'META']

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

    print("cum.slope", sum([v for k,v in slope_dict.items()]))
    return {'speedybee': speedybee_dict}




def theme_calculator(POLLENSTORY, chart_times):
    # ticker = 'SPY' # test
    # chart_times = {
    #     "1Minute_1Day": 0, "5Minute_5Day": 5, "30Minute_1Month": 18, 
    #     "1Hour_3Month": 48, "2Hour_6Month": 72, 
    #     "1Day_1Year": 250}
    # return all prior 5 days close and compare to current, return angle of the different periods

    theme = {'castle': {},
            'sub_indexes': {},
            'big_players': {}
                }
    tickers = set([i.split("_")[0] for i in POLLENSTORY.keys()])
    all_tframes = chart_times.keys()
    for ticker in tickers:
        theme[ticker] = {}
        for tframe in all_tframes:
            story={}
            # theme[ticker][] = {}
            theme_df = POLLENSTORY[f'{ticker}{"_"}{tframe}'].copy()

            if tframe == "1Minute_1Day":
                theme_df = split_today_vs_prior(df=theme_df) # remove prior day
                theme_today_df = theme_df['df_today']
                theme_prior_df = theme_df['df_prior']                
                
                # we want...last vs currnet close prices, && Height+length of wave

                # current from open price
                open_price = theme_today_df.iloc[0]['close']
                current_price = theme_today_df.iloc[-1]['close']
                delta_pct = (current_price - open_price) / current_price
                story['current_from_open'] = delta_pct
                # current day slope
                slope, intercept, r_value, p_value, std_err = stats.linregress(theme_today_df.index, theme_today_df['close'])
                story['slope'] = slope
                
                # how did day start
                last_price = theme_prior_df.iloc[-1]['close']
                delta_pct = (open_price - last_price) / open_price
                story['open_start'] = delta_pct
                
                
                
                theme[ticker][tframe] = story
    
    return theme










# def liquidate_position(api, ticker, side, type, client_order_id): # TBD
#     client_order_id = f'{ticker}{"_"}{side}{"_"}{datetime.datetime.now().isoformat()}'
#     p = api.get_position(ticker)
#     p_qty = p.qty
#     p_side = p.side
#     if type ==  'market':
#         order = submit_order(api=api, side=side, symbol=ticker, qty=p_qty, type=type, client_order_id=client_order_id)
#     else:
#         print("make this a limit order")
#     return order


# def reconcile_portfolio(portfolio_name='Jq'):  # IF MISSING FROM RUNNING ADD
#     # If Ticker in portfolio but not in RUNNING !!!!!! Need to consider changing to qty_available from pending close orders
#     # portfolio_holdings = {k : v['qty_available'] for (k,v) in portfolio.items()}
#     # portfolio_holdings = {k : v['qty'] for (k,v) in portfolio.items()} 
#     portfolio = return_alpc_portolio(api)['portfolio']
#     running_orders = [i for i in QUEEN['queen_orders'] if i['queen_order_state'] in ['running', 'submitted', 'running_close']]

#     # return running_orders in df    
#     running_portfolio = return_dfshaped_orders(running_orders=running_orders)
#     clean_errors = []
#     for symbol in portfolio:
#         for sy in QUEEN['errors'].keys():
#             if sy not in portfolio.keys():
#                 clean_errors.append(sy)
#         if len(running_portfolio) > 0:
#             if symbol not in running_portfolio['symbol'].values:
#                 msg = {"reconcile portfolio()": f'{symbol}{": was missing added to RUNNING"}'}
#                 print(msg)
#                 logging.error(msg)
                
#                 # # create a system gen. running order with portfolio info
#                 # filled_qty = float(portfolio[symbol]["qty"])
#                 # filled_avg_price = portfolio[symbol]["avg_entry_price"]
#                 # side = portfolio[symbol]["side"]
#                 # req_qty = portfolio[symbol]["qty"]
#                 # system_recon = {'req_qty': req_qty, 'filled_qty': filled_qty, 'filled_avg_price': filled_avg_price, 'side': side}
#                 # ticker_time_frame = f'{"symbol"}{"_queen_gen"}'
#                 # trig = 'buy_cross-0'
#                 # order = {'symbol': symbol, 'side': False, "id": "pollen_recon", 'client_order_id': generate_client_order_id(QUEEN=QUEEN,ticker=symbol, trig=trig)}
                
#                 # order_process = process_order_submission(prod=prod, order=order, trig=trig, tablename='main_orders', ticker_time_frame=ticker_time_frame, system_recon=system_recon)
#                 # QUEEN['queen_orders'].append(order_process['sending_order'])
#                 # QUEEN['command_conscience']['memory']['trigger_stopped'].append(order_process['trig_stop_info'])
#             else: # symbol is in running check our totals
#                 total_running_ticker_qty = float(running_portfolio[running_portfolio['symbol']==symbol].iloc[0]['filled_qty'])
#                 total_portfolio_ticker_qty = float(portfolio[symbol]["qty"])
#                 # !!! check in running_close to see if you have an open order to match qty !!!
#                 if total_running_ticker_qty != total_portfolio_ticker_qty:
#                     # print(symbol, ": qty does not match, adjust running order to fix")
#                     QUEEN["errors"].update({symbol: {'msg': "recon portfolio qty does not match!", 'root': "reconcile portfolio"}})
#                     # run_order_ = {idx: i for (idx, i) in enumerate(QUEEN["command_conscience"]["orders"]["requests"]) if i['queen_order_state'] == 'running' and i['symbol']==symbol}
#                     # if run_order_:
#                     #     if total_portfolio_ticker_qty < 0 : # short
#                     #         print("NEED TO UPDATE")
#                     #     else:
#                     #         qty_correction = total_running_ticker_qty - abs(total_portfolio_ticker_qty - total_running_ticker_qty)
#                     #         QUEEN["command_conscience"]["orders"]["requests"][list(run_order_.keys())[0]]['filled_qty'] = total_portfolio_ticker_qty
#                     #         QUEEN["command_conscience"]["orders"]["requests"][list(run_order_.keys())[0]]['status_q'] = True
                    
#                     # # update any running order
#                     # if total_running_ticker_qty > total_portfolio_ticker_qty: # if T_run > portfolio 
#                     #     qty_correction = total_portfolio_ticker_qty - (total_running_ticker_qty - total_portfolio_ticker_qty)
#                     #     QUEEN["command_conscience"]["orders"]["running"][0]['filled_qty'] = qty_correction
#                     #     QUEEN["command_conscience"]["orders"]["running"][0]['status_q'] = True
#                     # else:
#                     #     if total_portfolio_ticker_qty < 0: # short
#                     #         qty_correction = (total_running_ticker_qty-total_portfolio_ticker_qty)
#                     #     else:
#                     #         qty_correction = total_running_ticker_qty + (total_portfolio_ticker_qty- total_running_ticker_qty)
                        
#                     #     QUEEN["command_conscience"]["orders"]["running"][0]['filled_qty'] = qty_correction
#                     #     QUEEN["command_conscience"]["orders"]["running"][0]['status_q'] = True
#                 else:
#                     if symbol in QUEEN["errors"].keys():
#                         clean_errors.append(symbol)

#         else:
#             msg = {"reconcile portfolio()": f'{symbol}{": was missing added to RUNNING"}'}
#             print(msg)
#             logging.error(msg)
            
#             # create a system gen. running order with portfolio info
#             filled_qty = float(portfolio[symbol]["qty_available"])
#             filled_avg_price = float(portfolio[symbol]["avg_entry_price"])
#             side = portfolio[symbol]["side"]
#             req_qty = float(portfolio[symbol]["qty_available"])
#             system_recon = {'req_qty': req_qty, 'filled_qty': filled_qty, 'filled_avg_price': filled_avg_price, 'side': 'buy'}
#             ticker_time_frame = f'{"symbol"}{"_1Minute_1Day"}'
#             trig = 'queen_gen'
#             order = {'symbol': symbol, 'side': False, "id": "pollen_recon", 'client_order_id': generate_client_order_id(QUEEN=QUEEN,ticker=symbol, trig=trig)}
            
#             order_process = process_order_submission(prod=prod, order=order, trig=trig, tablename='main_orders', ticker_time_frame=False, system_recon=system_recon)
#             order_process['sending_order']['queen_order_state'] = 'running'
#             QUEEN['queen_orders'].append(order_process['sending_order'])
    
#     if clean_errors:
#         QUEEN['errors'] = {k:v for (k,v) in QUEEN['errors'].items() if k not in clean_errors}
#     return True




        # return {
        #     "1Minute_1Day": {
        #     'status': 'active',
        #     'trade_using_limits': False,
        #     'total_budget': 100,
        #     'buyingpower_allocation_LongTerm': .2,
        #     'buyingpower_allocation_ShortTerm': .8,
        #     'power_rangers': {k: 'active' for k in stars().keys() if k in list(stars().keys())},
        #     'trigbees': {'buy_cross-0': default, 
        #                 'sell_cross-0': default,
        #                 'ready_buy_cross': default,},

        # },
        #     "5Minute_5Day": {
        #     'status': 'active',
        #     'trade_using_limits': False,
        #     'total_budget': 100,
        #     'buyingpower_allocation_LongTerm': .2,
        #     'buyingpower_allocation_ShortTerm': .8,
        #     'power_rangers': {k: 'active' for k in stars().keys() if k in list(stars().keys())},
        #     # 'trigbees': {'buy_cross-0': 'active', 'sell_cross-0': 'active', 'ready_buy_cross': 'active'},
        #     'trigbees': {'buy_cross-0': default, 
        #                 'sell_cross-0': default, 
        #                 'ready_buy_cross': default,
        #         },

        #             },
        #     "30Minute_1Month": {
        #     'status': 'active',
        #     'trade_using_limits': False,
        #     'total_budget': 100,
        #     'buyingpower_allocation_LongTerm': .2,
        #     'buyingpower_allocation_ShortTerm': .8,
        #     'power_rangers': {k: 'active' for k in stars().keys() if k in list(stars().keys())},
        #     # 'trigbees': {'buy_cross-0': 'active', 'sell_cross-0': 'active', 'ready_buy_cross': 'active'},
        #     'trigbees': {'buy_cross-0': default, 
        #                 'sell_cross-0': default, 
        #                 'ready_buy_cross': default,
        #         },

        #             },
        #     "1Hour_3Month": {
        #     'status': 'active',
        #     'trade_using_limits': False,
        #     'total_budget': 100,
        #     'buyingpower_allocation_LongTerm': .2,
        #     'buyingpower_allocation_ShortTerm': .8,
        #     'power_rangers': {k: 'active' for k in stars().keys() if k in list(stars().keys())},
        #     # 'trigbees': {'buy_cross-0': 'active', 'sell_cross-0': 'active', 'ready_buy_cross': 'active'},
        #     'trigbees': {'buy_cross-0': default, 
        #                 'sell_cross-0': default, 
        #                 'ready_buy_cross': default,
        #         },

        #             },
        #     "2Hour_6Month": {
        #     'status': 'active',
        #     'trade_using_limits': False,
        #     'total_budget': 100,
        #     'buyingpower_allocation_LongTerm': .2,
        #     'buyingpower_allocation_ShortTerm': .8,
        #     'power_rangers': {k: 'active' for k in stars().keys() if k in list(stars().keys())},
        #     # 'trigbees': {'buy_cross-0': 'active', 'sell_cross-0': 'active', 'ready_buy_cross': 'active'},
        #     'trigbees': {'buy_cross-0': default, 
        #                 'sell_cross-0': default, 
        #                 'ready_buy_cross': default,
        #         },

        #             },
        #     "1Day_1Year": {
        #     'status': 'active',
        #     'trade_using_limits': False,
        #     'total_budget': 100,
        #     'buyingpower_allocation_LongTerm': .2,
        #     'buyingpower_allocation_ShortTerm': .8,
        #     'power_rangers': {k: 'active' for k in stars().keys() if k in list(stars().keys())},
        #     # 'trigbees': {'buy_cross-0': 'active', 'sell_cross-0': 'active', 'ready_buy_cross': 'active'},
        #     'trigbees': {'buy_cross-0': default, 
        #                 'sell_cross-0': default, 
        #                 'ready_buy_cross': default
        #         },

        #             },
        # }