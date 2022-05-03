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


est = pytz.timezone("America/New_York")

system = 'windows' #mac, windows
load_dotenv()

if system != 'windows':
    db_root = os.environ.get('db_root_mac')
else:
    db_root = os.environ.get('db_root_winodws')

# logging.basicConfig(
#     filename='hive_utils.log',
#     level=logging.INFO,
#     format='%(asctime)s:%(levelname)s:%(message)s',
# )

api_key_id = os.environ.get('APCA_API_KEY_ID')
api_secret = os.environ.get('APCA_API_SECRET_KEY')
base_url = "https://api.alpaca.markets"

exclude_conditions = [
    'B','W','4','7','9','C','G','H','I','M','N',
    'P','Q','R','T','U','V','Z'
]

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

"""# Dates """
current_day = api.get_clock().timestamp.date().isoformat()
trading_days = api.get_calendar()
trading_days_df = pd.DataFrame([day._raw for day in trading_days])

start_date = datetime.datetime.now().strftime('%Y-%m-%d')
end_date = datetime.datetime.now().strftime('%Y-%m-%d')

""" VAR >>>>>>>>>>VAR >>>>>>>>>>VAR >>>>>>>>>>VAR >>>>>>>>>>VAR >>>>>>>>>>VAR >>>>>>>>>>"""

""" STORY: I want a dict of every ticker and the chart_time TRADE buy/signal weights """
def pollen_story(pollen_nectar, QUEEN):
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

    CHARLIE_bee = {}  # holds all ranges for ticker and passes info into df
    betty_bee = {}  
    macd_tier_range = 33

    for ticker_time, df_i in pollen_nectar.items(): # CHARLIE_bee: # create ranges for MACD & RSI 4-3, 70-80, or USE Prior MAX&Low ...
        CHARLIE_bee[ticker_time] = {} 
        df = df_i.fillna(0).copy()
        df = df.reset_index(drop=True)
        df['story_index'] = df.index
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

        # Create Tiers
        for tier in range(1, macd_tier_range + 1): # Tiers of MinMax
            for mac_name in ['macd', 'signal', 'hist']:
                divder_max = mac_world['{}_high'.format(mac_name)] / macd_tier_range
                minvalue = mac_world['{}_low'.format(mac_name)]
                divder_min = minvalue / macd_tier_range
                
                if tier == 1:
                    maxvalue = mac_world['{}_high'.format(mac_name)]
                    macd_t1 = (maxvalue, (maxvalue - divder_max))
                    CHARLIE_bee[ticker_time]["tier"+str(tier)+"_"+mac_name+"-GREEN"] = macd_t1

                    macd_t1_min = (minvalue, (minvalue - divder_min))
                    CHARLIE_bee[ticker_time]["tier"+str(tier)+"_"+mac_name+"-RED"] = macd_t1_min
                else:
                    prior_tier = tier - 1
                    prior_second_value = CHARLIE_bee[ticker_time]["tier"+str(prior_tier)+"_"+mac_name+"-GREEN"][1]
                    
                    macd_t2 = (prior_second_value,  (prior_second_value - divder_max))
                    CHARLIE_bee[ticker_time]["tier"+str(tier)+"_"+mac_name+"-GREEN"] = macd_t2

                    prior_second_value_red = CHARLIE_bee[ticker_time]["tier"+str(prior_tier)+"_"+mac_name+"-RED"][1]
                    macd_t1_min2 = (prior_second_value_red, (prior_second_value_red - divder_min))
                    CHARLIE_bee[ticker_time]["tier"+str(tier)+"_"+mac_name+"-RED"] = macd_t1_min2
        # df = pd.DataFrame(CHARLIE_bee.items(), columns=['name', 'values'])
        # df[(df["name"].str.contains("macd")) & (df["name"].str.contains("-GREEN"))]

        # BETTY_bee = {}  # 'SPY_1Minute': {'macd': {'tier4_macd-RED': (-3.062420318268792, 0.0), 'current_value': -1.138314020642838}    
        
        # Map in CHARLIE_bee tier 
        def map_values_tier(mac_name, value, ticker_time_tiers, tier_range_set_value=False): # map in tier name or tier range high low
            # ticker_time_tiers = CHARLIE_bee[ticker_time]
            if value < 0:
                chart_range = {k:v for (k,v) in ticker_time_tiers.items() if mac_name in k and "RED" in k}
            else:
                chart_range = {k:v for (k,v) in ticker_time_tiers.items() if mac_name in k and "GREEN" in k}
            
            for tier_macname_sector, tier_range in chart_range.items():
                if abs(value) <= abs(tier_range[0]) and abs(value) >= abs(tier_range[1]):
                    if tier_range_set_value == 'high':
                        return tier_range[0]
                    elif tier_range_set_value == 'low':
                        return tier_range[1]
                    else:
                        return tier_macname_sector
        
        ticker_time_tiers = CHARLIE_bee[ticker_time]
        df['tier_macd'] = df['macd'].apply(lambda x: map_values_tier('macd', x, ticker_time_tiers))
        df['tier_macd_range-high'] = df['macd'].apply(lambda x: map_values_tier('macd', x, ticker_time_tiers, tier_range_set_value='high'))
        df['tier_macd_range-low'] = df['macd'].apply(lambda x: map_values_tier('macd', x, ticker_time_tiers, tier_range_set_value='low'))

        df['tier_signal'] = df['signal'].apply(lambda x: map_values_tier('signal', x, ticker_time_tiers))
        df['tier_signal_range-high'] = df['signal'].apply(lambda x: map_values_tier('signal', x, ticker_time_tiers, tier_range_set_value='high'))
        df['tier_signal_range-low'] = df['signal'].apply(lambda x: map_values_tier('signal', x, ticker_time_tiers, tier_range_set_value='low'))

        df['tier_hist'] = df['hist'].apply(lambda x: map_values_tier('hist', x, ticker_time_tiers))
        df['tier_hist_range-high'] = df['hist'].apply(lambda x: map_values_tier('hist', x, ticker_time_tiers, tier_range_set_value='high'))
        df['tier_hist_range-low'] = df['hist'].apply(lambda x: map_values_tier('hist', x, ticker_time_tiers, tier_range_set_value='low'))

        # Add Seq columns of tiers, return [0,1,2,0,1,0,0,1,2,3,0] (how Long in Tier)
            # how long since prv High/Low?
            # when was the last time you were in higest tier
        #>/ how many times have you reached tiers
        #>/ how long have you stayed in your tier?
            # side of tier, are you closer to exit or enter of next tier?
            # how far away from MACD CROSS?
            # ARE you a startcase Hist? # linear regression 
        def count_sequential_n_inList(df, item_list, mac_name): # df['tier_macd'].to_list()
            # how long you been in tier AND 
            # item_list = df['tier_macd'].to_list()
            d = defaultdict(int) # you have totals here to return!!!
            d_total_tier_counts = defaultdict(int)
            res_list = []
            res_dist_list = []
            set_index = {'start': 0}
            for i, el in enumerate(item_list):
                if i == 0:
                    d[el]+=1
                    d_total_tier_counts[el] += 1
                    res_list.append(d[el])
                    res_dist_list.append(0)
                else:
                    seq_el = item_list[i-1]
                    if el == seq_el:
                        d[el]+=1
                        d_total_tier_counts[el] += 1
                        res_list.append(d[el])
                        # count new total distance
                        total = sum(res_list[set_index['start']:i])
                        res_dist_list.append(total)
                    else:
                        d[el]=0
                        res_list.append(d[el])
                        set_index['start'] = i - 1
                        res_dist_list.append(0)
            # Join in Data and send info to the QUEEN
            QUEEN['pollenstory_info'][ticker_time] = d_total_tier_counts
            dfseq = pd.DataFrame(res_list, columns=['seq_'+mac_name])
            dfrunning = pd.DataFrame(res_dist_list, columns=['running_'+mac_name])
            df_new = pd.concat([df, dfseq, dfrunning], axis=1)
            return df_new

            def tier_time_patterns(df, names):
                # {'macd': {'tier4_macd-RED': (-3.062420318268792, 0.0), 'current_value': -1.138314020642838}
                names = ['macd', 'signal', 'hist']
                for name in names:
                    tier_name = f'tier_{name}' # tier_macd
                    item_list = df[tier_name].to_list()
                    res = count_sequential_n_inList(item_list)

                    tier_list = list(set(df[tier_name].to_list()))

                    
                    for tier in tier_list:
                        if tier.lower().startswith('t'): # ensure tier
                            df_tier = df[df[tier_name] == tier].copy()
                            x = df_tier["timestamp_est"].to_list()



            macd_high = df_i[df_i[mac_name] == mac_world['{}_high'.format(mac_name)]].timestamp_est # last time High
            macd_min = df_i[df_i[mac_name] == mac_world['{}_low'.format(mac_name)]].timestamp_est # last time Low
        
        try:
            for mac_name in ['macd', 'signal', 'hist']:
                df = count_sequential_n_inList(df=df, item_list=df['tier_'+mac_name].to_list(), mac_name=mac_name)

                # distance from prior HIGH LOW
                toptier = f'{"tier1"}{"_"}{mac_name}{"-GREEN"}'
                bottomtier = f'{"tier1"}{"_"}{mac_name}{"-RED"}'
                # Current Distance from top and bottom
                for tb in [toptier, bottomtier]:
                    df_t = df[df['tier_'+mac_name]==tb].copy()
                    last_time_tier_found = df_t.iloc[-1].story_index
                    distance_from_last_tier = df.iloc[-1].story_index - df_t.iloc[-1].story_index
                    betty_bee[f'{ticker_time}{"--"}{"tier_"}{mac_name}{"-"}{tb.split("-")[-1]}'] = distance_from_last_tier
                QUEEN['pollenstory_info']['betty_bee'] = betty_bee
        
                # create running sum of past x(3/5) values and determine slope
                l = [0,0,0,0,0,0,1,2,3,4,3,2,1,0,1,2,3,10]
                final = []
                final_avg = []
                count_set = 5
                for i, value in enumerate(l):
                    if i < count_set:
                        final.append(0)
                        final_avg.append(0)
                    else:
                        # ipdb.set_trace()
                        prior_index = i - count_set
                        running_total = sum(l[prior_index:i])
                        final.append(running_total)
                        # print(running_total)
                        
                        prior_value = final[i-1]
                        if prior_value==0 or value==0:
                            final_avg.append(0)
                        else:
                            pct_change_from_prior = (value - prior_value) / value
                            final_avg.append(pct_change_from_prior)
        except Exception as e:
            msg=(e,"--", print_line_of_error(), "--", ticker_time, "--", mac_name)
            logging.error(msg)
        
        df['name'] = ticker_time
        story[ticker_time] = df
        # print(df['name'].iloc[-1], df['close'].iloc[-1], df['tier_macd'].iloc[-1], df['timestamp_est'].iloc[-1])
        
        # add momentem ( when macd < signal & past 3 macds are > X Value or %)
        
        # when did macd and signal share same tier?
        # OR When did macd and signal last cross macd < signal
        # what is momentum of past intervals (3, 5, 8...)
    # QUEEN['pollenstory'] = story
    e = datetime.datetime.now()
    # print(str((e - s)) + ": " + datetime.datetime.now().strftime("%A, %d. %B %Y %I:%M:%S%p"))
    return {'pollen_story': story, 'betty_bee': betty_bee}


def mark_macd_signal_cross(df): # Mark the signal macd crosses 
    m=df['macd'].to_list()
    s=df['signal'].to_list()
    cross_list=[]
    for i, macdvalue in enumerate(m):
        if i != 0:
            prior_mac = m[i-1]
            prior_signal = s[i-1]
            now_mac = macdvalue
            now_signal = s[i]
            if now_mac > now_signal and prior_mac <= prior_signal:
                cross_list.append('buy_cross')
            elif now_mac < now_signal and prior_mac >= prior_signal:
                cross_list.append('sell_cross')
            else:
                cross_list.append('hold')
        else:
            cross_list.append('hold')
    df2 = pd.DataFrame(cross_list, columns=['macd_cross'])
    df_new = pd.concat([df, df2], axis=1)
    return df_new


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

def rebuild_timeframe_bars(ticker_list, timedelta_input=False, min_input=False, sec_input=False):
    # ticker_list = ['IBM', 'AAPL', 'SPY', 'QQQQ']
    try:
        # First get the current time
        current_time = datetime.datetime.now()
        current_sec = current_time.second
        if current_sec < 5:
            time.sleep(1)
            current_time = datetime.datetime.now()
            current_sec = current_time.second

        if timedelta_input:
            current_sec = timedelta_input 

        min_input = 0
        sec_input = current_sec
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
    except Exception as e:
        print("rebuild_timeframe_bars", e)
        return {'resp': False, 'msg': [e, current_time, previous_time]}
# r = rebuild_timeframe_bars(ticker_list)

def submit_best_limit_order(symbol, qty, side, client_order_id=False):
    # side = 'buy'
    # qty = '1'
    # symbol = 'BABA'
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


def submit_order(symbol, qty, side, type, limit_price, client_order_id, time_in_force, order_class=False, stop_loss=False, take_profit=False):
    
    order = api.submit_order(symbol='BABA', 
            qty=1, 
            side='buy', # buy, sell 
            time_in_force='gtc', # 'day'
            type='limit', # 'market'
            limit_price=425.15, 
            client_order_id='test1') # optional make sure it unique though to call later!
    order = api.submit_order(symbol='BABA', 
            qty=1, 
            side='sell', # buy, sell 
            time_in_force='gtc', # 'day'
            type='market', # 'market'
            # limit_price=425.15, 
            client_order_id='test1') # optional make sure it unique though to call later!

    if type == 'market':
        order = api.submit_order(symbol=symbol,
        qty=qty,
        side=side,
        type=type,
        time_in_force=time_in_force)
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



    if 'name' == 'main':
        submit_order()


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


def init_log(root, dirname, name, update_df=False, update_type=False, update_write=False, cols=False):
    # dirname = 'db'
    # root_token=os.path.join(root, dirname)
    # name='hive_utils_log.csv'
    # cols = ['type', 'log_note', 'timestamp']
    # update_df = pd.DataFrame(list(zip(['info'], ['text'])), columns = ['type', 'log_note'])
    # update_write=True
    
    root_token=os.path.join(root, dirname)
    
    if os.path.exists(os.path.join(root_token, name)) == False:
        with open(os.path.join(root_token, name), 'w') as f:
            df = pd.DataFrame()
            for i in cols:
                if i == 'timestamp':
                    df[i] = datetime.datetime.now()
                else:
                    df[i] = ''
            df.to_csv(os.path.join(root_token, name), index=False, encoding='utf8')
            print(name, "created")
            return df
    else:
        df = pd.read_csv(os.path.join(root_token, name), dtype=str, encoding='utf8')
        if update_type == 'append':
            # df = df.append(update_df, ignore_index=True, sort=False)
            df = pd.concat([df, update_df], join='outer', ignore_index=True, axis=0)
            if update_write:
                df.to_csv(os.path.join(root_token, name), index=False, encoding='utf8')
                return df
            else:
                return df
        else:
            return df
# # TESTS
# log_file = init_log(root=os.getcwd(), dirname='db', name='hive_utils_log.csv', cols=['type', 'log_note', 'timestamp'])
# log_file = init_log(root=os.getcwd(), dirname='db', name='hive_utils_log.csv', update_df=update_df, update_type='append', update_write=True, cols=False)

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


def timestamp_string():
    return datetime.datetime.now().strftime("%m-%d-%Y %I.%M%p")


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




# NOT IN USE #
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