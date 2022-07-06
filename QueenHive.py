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
import ipdb
import json

queens_chess_piece = os.path.basename(__file__)

prod=True

main_root = os.getcwd()
db_root = os.path.join(main_root, 'db')
db_app_root = os.path.join(db_root, 'app')

current_day = datetime.datetime.now().day
current_month = datetime.datetime.now().month
current_year = datetime.datetime.now().year

# init_logging(queens_chess_piece, db_root)
loglog_newfile = False
log_dir = dst = os.path.join(db_root, 'logs')
log_dir_logs = dst = os.path.join(log_dir, 'logs')
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

    if os.path.exists(os.path.join(db_root, 'castle_coin.pkl')):
        castle_coin = ReadPickleData(pickle_file=os.path.join(db_root, 'castle_coin.pkl'))
    else:
        castle_coin = False
    
    pollenstory = {**pollenstory, **castle_coin['castle_coin']['pollenstory']} # combine daytrade and longterm info
    return pollenstory


def read_queensmind(prod): # return active story workers
    
    if prod:
        queen = ReadPickleData(pickle_file=os.path.join(db_root, 'queen.pkl'))
    else:
        queen = ReadPickleData(pickle_file=os.path.join(db_root, 'queen_sandbox.pkl'))

    # return beeworkers data
    castle = ReadPickleData(pickle_file=os.path.join(db_root, 'castle.pkl'))['castle']
    bishop = ReadPickleData(pickle_file=os.path.join(db_root, 'bishop.pkl'))['bishop']
    # knight = ReadPickleData(pickle_file=os.path.join(db_root, 'knight.pkl'))
    STORY_bee = {**bishop['conscience']['STORY_bee'], **castle['conscience']['STORY_bee']}
    KNIGHTSWORD = {**bishop['conscience']['KNIGHTSWORD'], **castle['conscience']['KNIGHTSWORD']}
    ANGEL_bee = {**bishop['conscience']['ANGEL_bee'], **castle['conscience']['ANGEL_bee']}
    
    if os.path.exists(os.path.join(db_root, 'castle_coin.pkl')):
        castle_coin = ReadPickleData(pickle_file=os.path.join(db_root, 'castle_coin.pkl'))['castle_coin']
        STORY_bee = {**STORY_bee, **castle['conscience']['STORY_bee']}
        KNIGHTSWORD = {**KNIGHTSWORD, **castle['conscience']['KNIGHTSWORD']}
        ANGEL_bee = {**ANGEL_bee, **castle['conscience']['ANGEL_bee']}
    else:
        castle_coin = False

    return {'queen': queen, 
    'bishop': bishop, 'castle': castle, 
    'STORY_bee': STORY_bee, 'KNIGHTSWORD': KNIGHTSWORD, 'ANGEL_bee': ANGEL_bee, 'castle_coin': castle_coin}

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
    try:
        s = datetime.datetime.now()
        story = {}
        ANGEL_bee = {} # add to QUEENS mind
        STORY_bee = {} 
        # CHARLIE_bee = {}  # holds all ranges for ticker and passes info into df
        betty_bee = {}  
        macd_tier_range = 33
        knights_sight_word = {}
        # knight_sight_df = {}

        for ticker_time_frame, df_i in pollen_nectar.items(): # CHARLIE_bee: # create ranges for MACD & RSI 4-3, 70-80, or USE Prior MAX&Low ...
            ticker, tframe, frame = ticker_time_frame.split("_")
            # CHARLIE_bee[ticker_time_frame] = {}
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

            # mac cross
            df = mark_macd_signal_cross(df=df)

            resp = knight_sight(df=df)
            df = resp['df']
            knights_word = resp['bee_triggers']
            # how long does trigger stay profitable?
            """for every index(timeframe) calculate profit length, bell curve
                conclude with how well trigger is doing to then determine when next trigger will do well
            """
            def return_knightbee_waves(df, knights_word):  # adds profit wave based on trigger
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
                    df[f'{trig_name}{"__wave"}'] = df['story_index'].map(index_wave_series).fillna(0)
                    df[f'{trig_name}{"__wave_number"}'] = df['story_index'].map(index_perwave).fillna("0")
                    # bees_wave_df = df[df['story_index'].isin(bees_wave_list)].copy()
                    # tag greatest profit
                return wave
            
            wave = return_knightbee_waves(df=df, knights_word=knights_word)
            # wave_trigger_list = wave[ticker_time_frame].keys()
            wave_trigger_list = ['buy_cross-0', 'sell_cross-0']

            # Queen to make understanding of trigger-profit waves
            #Q? split up time blocks and describe wave-buy time segments, morning, beforenoon, afternoon
            #Q? measure pressure of a wave? if small waves, expect bigger wave>> up the buy


            def return_macd_wave_story(df, wave_trigger_list):
                # POLLENSTORY = read_pollenstory()
                # df = POLLENSTORY["SPY_1Minute_1Day"]
                # wave_trigger_list = ["buy_cross-0", "sell_cross-0"]
                
                t = split_today_vs_prior(df=df)
                dft = t['df_today']

                # length and height of wave
                MACDWAVE_story = {'story': {}}
                MACDWAVE_story.update({trig_name: {} for trig_name in wave_trigger_list})

                for trigger in wave_trigger_list:
                    wave_col_name = f'{trigger}{"__wave"}'
                    wave_col_wavenumber = f'{trigger}{"__wave_number"}'
                
                    num_waves = dft[wave_col_wavenumber].tolist()
                    num_waves_list = list(set(num_waves))
                    num_waves_list = [str(i) for i in sorted([int(i) for i in num_waves_list])]

                    for wave_n in num_waves_list:
                        MACDWAVE_story[trigger][wave_n] = {}
                        if wave_n == '0':
                            continue
                        t = dft[['timestamp_est', wave_col_wavenumber, 'story_index', wave_col_name]].copy()
                        t = dft[dft[wave_col_wavenumber] == wave_n] # slice by trigger event wave start / end 
                        
                        row_1 = t.iloc[0]['story_index']
                        row_2 = t.iloc[-1]['story_index']

                        # we want to know the how long it took to get to low? 

                        # Assign each waves timeblock
                        if "Day" in tframe:
                            wave_blocktime = "Day"
                            wave_starttime = t.iloc[0]['timestamp_est']
                            wave_endtime = t.iloc[-1]['timestamp_est']
                        else:
                            wave_starttime = t.iloc[0]['timestamp_est']
                            wave_endtime = t.iloc[-1]['timestamp_est']
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
                        'wave_times': ( wave_starttime, wave_endtime ),
                        })
                        
                        wave_height_value = max(t[wave_col_name].values)
                        # how long was it profitable?
                        profit_df = t[t[wave_col_name] > 0].copy()
                        profit_length  = len(profit_df)
                        if profit_length > 0:
                            max_profit_index = profit_df[profit_df[wave_col_name] == wave_height_value].iloc[0]['story_index']
                            time_to_max_profit = max_profit_index - row_1
                            MACDWAVE_story[trigger][wave_n].update({'maxprofit': wave_height_value, 'time_to_max_profit': time_to_max_profit})

                        else:
                            MACDWAVE_story[trigger][wave_n].update({'maxprofit': wave_height_value, 'time_to_max_profit': 0})
                
                # make conculsions: morning had X# of waves, Y# was profitable, big_waves_occured
                # bee_89 = MACDWAVE_story["buy_cross-0"]
                # for wave in bee_89:
                # gather current avg waves

                return MACDWAVE_story
            MACDWAVE_story = return_macd_wave_story(df=df, wave_trigger_list=wave_trigger_list)
            STORY_bee[ticker_time_frame]['waves'] = MACDWAVE_story

            knights_sight_word[ticker_time_frame] = knights_word
            STORY_bee[ticker_time_frame]['KNIGHTSWORD'] = knights_word
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
                            ANGEL_bee[ticker_time_frame][name] = return_degree_angle(x, y)
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
            
            time_state = df['timestamp_est'].iloc[-1] # current time
            STORY_bee[ticker_time_frame]['story']['time_state'] = time_state

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
            today_df = df[df['timestamp_est'] > (datetime.datetime.now().replace(hour=1, minute=1, second=1)).isoformat()].copy()
            STORY_bee[ticker_time_frame]['story']['macd_cross_count'] = {
                'buy_cross_total_running_count': sum(np.where(df['macd_cross'] == 'buy_cross-0',1,0)),
                'sell_cross_totalrunning_count' : sum(np.where(df['macd_cross'] == 'sell_cross-0',1,0)),
                'buy_cross_todays_running_count': sum(np.where(today_df['macd_cross'] == 'buy_cross-0',1,0)),
                'sell_cross_todays_running_count' : sum(np.where(today_df['macd_cross'] == 'sell_cross-0',1,0))
            }
            
            # latest_close_price
            STORY_bee[ticker_time_frame]['story']['last_close_price'] = df.iloc[-1]['close']

            # macd signal divergence
            df['macd_singal_deviation'] = df['macd'] - df['signal']
            STORY_bee[ticker_time_frame]['story']['macd_singal_deviation'] = df.iloc[-1]['macd_singal_deviation']


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

                slope, intercept, r_value, p_value, std_err = stats.linregress(theme_today_df.index, theme_today_df['close'])
                STORY_bee[ticker_time_frame]['story']['current_slope'] = slope




            # how long have you been stuck at vwap ?
            
            # Measure MACD WAVES
            # change % shifts for each, close, macd, signal, hist....

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

        e = datetime.datetime.now()
        print("pollen_story", str((e - s)))
        return {'pollen_story': story, 'conscience': {'ANGEL_bee': ANGEL_bee, 'KNIGHTSWORD': knights_sight_word, 'STORY_bee': STORY_bee  } }
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
            (df['hist_slope-3'] > -.3)
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
        last_buycross_index = 0
        last_sellcross_index = 0
        wave_mark_list = []
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
                    last_buycross_index = i
                    wave_mark_list.append(last_buycross_index)
                elif now_mac < now_signal and prior_mac >= prior_signal:
                    cross_list.append(f'{"sell_cross"}{"-"}{0}')
                    c = 0
                    prior_cross = 'sell'
                    sell_c += 1
                    last_sellcross_index = i
                    wave_mark_list.append(last_sellcross_index)

                else:
                    if prior_cross:
                        if prior_cross == 'buy':
                            c+=1
                            cross_list.append(f'{"buy_hold"}{"-"}{c}')
                            wave_mark_list.append(0)
                        else:
                            c+=1
                            cross_list.append(f'{"sell_hold"}{"-"}{c}')
                            wave_mark_list.append(0)
                    else:
                        cross_list.append(f'{"hold"}{"-"}{0}')
                        wave_mark_list.apend(0)
            else:
                cross_list.append(f'{"hold"}{"-"}{0}')
                wave_mark_list.append(0)
        df2 = pd.DataFrame(cross_list, columns=['macd_cross'])
        df3 = pd.DataFrame(wave_mark_list, columns=['macd_cross_wavedistance'])
        df_new = pd.concat([df, df2, df3], axis=1)
        return df_new
    except Exception as e:
        msg=(e,"--", print_line_of_error(), "--", 'macd_cross')
        logging.critical(msg)     


def split_today_vs_prior(df):
    df_day = df['timestamp_est'].iloc[-1]
    df = df.copy()
    df = df.set_index('timestamp_est', drop=True) # test
    df_prior = df[~(df.index.day == df_day.day)].copy()
    
    df_today = df[(df.index.day == df_day.day)].copy()
    df_today = df_today.reset_index()
    df_prior = df_prior.reset_index()
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

def check_order_status(api, client_order_id, prod=True): # return raw dict form
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
        with open(pickle_file, 'wb+') as dbfile:
            for k, v in data_to_store.items(): 
                db[k] = v
            db['last_modified'] = p_timestamp 
            pickle.dump(db, dbfile)                   
        
        return True


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
            print("CRITICAL ERROR logme", e)
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
    main_orders_cols = ['trigname', 'client_order_id', 'origin_client_order_id', 'exit_order_link', 'date', 'lastmodified', 'selfnote', 'app_requests_id', 'bulkorder_origin__client_order_id']

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


def return_VWAP(df):
    # VWAP
    df = df.assign(
        vwap=df.eval(
            'wgtd = close * volume', inplace=False
        ).groupby(df['timestamp_est']).cumsum().eval('wgtd / volume')
    )
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

# class return_pollen():
#     workerbees = ['queen', 'castle', 'bishop', 'castle_coin']
#     POLLENSTORY = {}
#     STORY_bee = {}
#     KNIGHTSWORD = {}
#     ANGEL_bee = {}
#     QUEENSMIND = {}
#     for bee in workerbees:
#         chess_piece = ReadPickleData(pickle_file=os.path.join(db_root, f'{bee}{".pkl"}'))
#         POLLENSTORY = {**POLLENSTORY, **chess_piece[bee]['pollenstory']}
#         STORY_bee = {**STORY_bee, **chess_piece[bee]['conscience']['STORY_bee']}
#         KNIGHTSWORD = {**KNIGHTSWORD, **chess_piece[bee]['conscience']['KNIGHTSWORD']}
#         ANGEL_bee = {**ANGEL_bee, **chess_piece[bee]['conscience']['ANGEL_bee']}

#         if bee == "queen":
#             QUEENSMIND = chess_piece['command_conscience']
# if '__name__' == '__main__':
#     return_pollen()


# df = POLLENSTORY['SPY_1Minute_1Day']
# buy_cross = df['buy_cross-0'].tolist()
# close = df['close'].tolist()
# track_bees = {}
# track_bees_profits = {}
# trig_bee_count = 0
# trig_name = 'buy_cross-0'
# for idx, trig_bee in enumerate(buy_cross):
#     if idx == 0:
#         continue
#     if trig_bee == 'bee':
#         trig_bee_count+=1
#         beename = f'{trig_name}{trig_bee_count}'
#         close_price = close[idx]
#         track_bees[beename] = close_price
#         continue
#     if trig_bee_count > 0:
#         beename = f'{trig_name}{trig_bee_count}'
#         origin_trig_price = track_bees[beename]
#         latest_price = close[idx]
#         profit_loss = (latest_price - origin_trig_price) / latest_price
#         if beename in track_bees_profits.keys():
#             track_bees_profits[beename].update({idx: profit_loss})
#         else:
#             track_bees_profits[beename] = {idx: profit_loss}

def return_main_chart_times(queens_chess_piece):
    if queens_chess_piece in ['queen', 'castle', 'bishop']:
        chart_times = {
            "1Minute_1Day": 0, "5Minute_5Day": 5, "30Minute_1Month": 18, 
            "1Hour_3Month": 48, "2Hour_6Month": 72, 
            "1Day_1Year": 250}
        return chart_times


def update_queen_controls(pickle_file, dict_update, queen=False):

    data = ReadPickleData(pickle_file=pickle_file)
    for k, v in dict_update.items():
        data[k] = v
    
    if queen:
        data['queens_last_update'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    else:
        data['app_last_update'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    
    PickleData(pickle_file=pickle_file, data_to_store=data)        
    
    return data

def init_app(pickle_file):
    if os.path.exists(pickle_file) == False:
        print("init app")
        data = {'orders': [], 'theme': [], 'queen_processed': []}
        PickleData(pickle_file=pickle_file, data_to_store=data)

def pollen_themes():

    pollen_themes = {'strong_open': {'name': 'strong_open',
                                'desc': """SPY/overall up > 1% 
                                            & prior X(5) days decline is Z(-5%)
                                            
                                            """,
                                # 'formula': theme_calculator(POLLENSTORY, chart_times),
                                'triggerbees_tofind': ['VWAP_GRAVITY'],
                                'waveup' : {'morning_9-11': .3,
                                'lunch_11-2': .1,
                                'afternoon_2-4': .1
                                    },
                                'wavedown' : {'morning_9-11': .1,
                                'lunch_11-2': .3,
                                'afternoon_2-4': .3
                                    }
                                }
                    } # set the course for the day how you want to buy expecting more scalps vs long? this should update and change as new info comes into being
    return pollen_themes





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