# archived_functions


def produce_pollen_story(pollen_charts):
    # add in indicators
    # produce pollenstory
    main_rebuild_dict = {} ##> only override current dict if memory becomes issues!
    for ticker_time, bars_data in pollen_charts.items():
        df_data_new = return_getbars_WithIndicators(bars_data=bars_data, MACD=MACD)
        if df_data_new[0] == True:
            main_rebuild_dict[ticker_time] = df_data_new[1]
        else:
            print("error", ticker_time)
    # for ticker_time_frame, df_data in main_rebuild_dict.items():
    pollens_honey = pollen_story(pollen_nectar=QUEEN[queens_chess_piece]['pollencharts_nectar'], QUEEN=QUEEN, queens_chess_piece=queens_chess_piece)


    return {'pollencharts_nectar': main_rebuild_dict, 'pollencharts': chart_rebuild_dict}




# def recon_running_trigger_stops(QUEEN):
#     run_dict = {'running': 'trigger_stopped', 'running_close': 'trigger_sell_stopped'}
#     save_queen = False
#     for run, runstop in run_dict.items():
#         # check if item in other bucket, if NOT its MISSING
#         for idx, run_order in enumerate(QUEEN['command_conscience']['orders'][run]):
#             stop = [i for i in QUEEN['command_conscience']['memory'][runstop] if i['client_order_id'] == run_order['client_order_id']]
#             if len(stop) == 0:
#                 save_queen = True
#                 msg = {"recon_running_trigger_stops": {"run_order": run_order['client_order_id']}}
#                 print(msg)
#                 logging.error(msg)

#                 # create trig stop
#                 trig_stop_info = {'symbol': run_order['symbol'], 'trigname': run_order['trigname'], 
#                 'ticker_time_frame': run_order['ticker_time_frame'], 'exit_order_link': run_order['exit_order_link'], 
#                 'client_order_id': run_order['client_order_id'], 'datetime': run_order['datetime']}
#                 QUEEN['command_conscience']['memory'][runstop].append(trig_stop_info)

#         for idx, stop_trig in enumerate(QUEEN['command_conscience']['memory'][runstop]):
#             matching_run = [i for i in QUEEN['command_conscience']['orders'][run] if i['client_order_id'] == stop_trig['client_order_id']]
#             if len(matching_run) == 0:
#                 save_queen = True
#                 msg = {"recon_running_trigger_stops": {"msg": "stop found but no running order exists: REMOVING STOP", "run_order": stop_trig['client_order_id']}}
#                 print(msg)
#                 logging.error(msg)

#                 QUEEN['command_conscience']['memory'][runstop].remove(stop_trig)


    
#     # God save the Queen
#     if save_queen:
#         PickleData(pickle_file=PB_Story_Pickle, data_to_store=QUEEN)
    
#     return True


# pollenstory():
        # # Create Tiers
        # for tier in range(1, macd_tier_range + 1): # Tiers of MinMax
        #     for mac_name in ['macd', 'signal', 'hist']:
        #         divder_max = mac_world['{}_high'.format(mac_name)] / macd_tier_range
        #         minvalue = mac_world['{}_low'.format(mac_name)]
        #         divder_min = minvalue / macd_tier_range
                
        #         if tier == 1:
        #             maxvalue = mac_world['{}_high'.format(mac_name)]
        #             macd_t1 = (maxvalue, (maxvalue - divder_max))
        #             CHARLIE_bee[ticker_time_frame]["tier"+str(tier)+"_"+mac_name+"-GREEN"] = macd_t1

        #             macd_t1_min = (minvalue, (minvalue - divder_min))
        #             CHARLIE_bee[ticker_time_frame]["tier"+str(tier)+"_"+mac_name+"-RED"] = macd_t1_min
        #         else:
        #             prior_tier = tier - 1
        #             prior_second_value = CHARLIE_bee[ticker_time_frame]["tier"+str(prior_tier)+"_"+mac_name+"-GREEN"][1]
                    
        #             macd_t2 = (prior_second_value,  (prior_second_value - divder_max))
        #             CHARLIE_bee[ticker_time_frame]["tier"+str(tier)+"_"+mac_name+"-GREEN"] = macd_t2

        #             prior_second_value_red = CHARLIE_bee[ticker_time_frame]["tier"+str(prior_tier)+"_"+mac_name+"-RED"][1]
        #             macd_t1_min2 = (prior_second_value_red, (prior_second_value_red - divder_min))
        #             CHARLIE_bee[ticker_time_frame]["tier"+str(tier)+"_"+mac_name+"-RED"] = macd_t1_min2
        # df = pd.DataFrame(CHARLIE_bee.items(), columns=['name', 'values'])
        # df[(df["name"].str.contains("macd")) & (df["name"].str.contains("-GREEN"))]

        # BETTY_bee = {}  # 'SPY_1Minute': {'macd': {'tier4_macd-RED': (-3.062420318268792, 0.0), 'current_value': -1.138314020642838}    
        
        # Map in CHARLIE_bee tier
        # def map_tiers(): # map in into main df
        #     def map_values_tier(mac_name, value, ticker_time_tiers, tier_range_set_value=False): # map in tier name or tier range high low
        #         # ticker_time_tiers = CHARLIE_bee[ticker_time_frame]
        #         if value < 0:
        #             chart_range = {k:v for (k,v) in ticker_time_tiers.items() if mac_name in k and "RED" in k}
        #         else:
        #             chart_range = {k:v for (k,v) in ticker_time_tiers.items() if mac_name in k and "GREEN" in k}
                
        #         for tier_macname_sector, tier_range in chart_range.items():
        #             if abs(value) <= abs(tier_range[0]) and abs(value) >= abs(tier_range[1]):
        #                 if tier_range_set_value == 'high':
        #                     return tier_range[0]
        #                 elif tier_range_set_value == 'low':
        #                     return tier_range[1]
        #                 else:
        #                     return tier_macname_sector
            
        #     ticker_time_tiers = CHARLIE_bee[ticker_time_frame]
        #     df['tier_macd'] = df['macd'].apply(lambda x: map_values_tier('macd', x, ticker_time_tiers))
        #     df['tier_macd_range-high'] = df['macd'].apply(lambda x: map_values_tier('macd', x, ticker_time_tiers, tier_range_set_value='high'))
        #     df['tier_macd_range-low'] = df['macd'].apply(lambda x: map_values_tier('macd', x, ticker_time_tiers, tier_range_set_value='low'))

        #     df['tier_signal'] = df['signal'].apply(lambda x: map_values_tier('signal', x, ticker_time_tiers))
        #     df['tier_signal_range-high'] = df['signal'].apply(lambda x: map_values_tier('signal', x, ticker_time_tiers, tier_range_set_value='high'))
        #     df['tier_signal_range-low'] = df['signal'].apply(lambda x: map_values_tier('signal', x, ticker_time_tiers, tier_range_set_value='low'))

        #     df['tier_hist'] = df['hist'].apply(lambda x: map_values_tier('hist', x, ticker_time_tiers))
        #     df['tier_hist_range-high'] = df['hist'].apply(lambda x: map_values_tier('hist', x, ticker_time_tiers, tier_range_set_value='high'))
        #     df['tier_hist_range-low'] = df['hist'].apply(lambda x: map_values_tier('hist', x, ticker_time_tiers, tier_range_set_value='low'))
            
        #     return True
        # map_tiers()

        # # Add Seq columns of tiers, return [0,1,2,0,1,0,0,1,2,3,0] (how Long in Tier)
        #     # how long since prv High/Low?
        #     # when was the last time you were in higest tier
        # #>/ how many times have you reached tiers
        # #>/ how long have you stayed in your tier?
        #     # side of tier, are you closer to exit or enter of next tier?
        #     # how far away from MACD CROSS?
        #     # ARE you a startcase Hist? # linear regression 
        # def count_sequential_n_inList(df, item_list, mac_name): # df['tier_macd'].to_list()
        #     # how long you been in tier AND 
        #     # item_list = df['tier_macd'].to_list()
        #     d = defaultdict(int) # you have totals here to return!!!
        #     d_total_tier_counts = defaultdict(int)
        #     res_list = []
        #     res_dist_list = []
        #     set_index = {'start': 0}
        #     for i, el in enumerate(item_list):
        #         if i == 0:
        #             d[el]+=1
        #             d_total_tier_counts[el] += 1
        #             res_list.append(d[el])
        #             res_dist_list.append(0)
        #         else:
        #             seq_el = item_list[i-1]
        #             if el == seq_el:
        #                 d[el]+=1
        #                 d_total_tier_counts[el] += 1
        #                 res_list.append(d[el])
        #                 # count new total distance
        #                 total = sum(res_list[set_index['start']:i])
        #                 res_dist_list.append(total)
        #             else:
        #                 d[el]=0
        #                 res_list.append(d[el])
        #                 set_index['start'] = i - 1
        #                 res_dist_list.append(0)
            
        #     # Join in Data and send info to the QUEEN
        #     # QUEEN[queens_chess_piece]['pollenstory_info'][ticker_time_frame][''] = d_total_tier_counts
        #     bee_tier_totals = d_total_tier_counts
        #     dfseq = pd.DataFrame(res_list, columns=['seq_'+mac_name])
        #     dfrunning = pd.DataFrame(res_dist_list, columns=['running_'+mac_name])
        #     df_new = pd.concat([df, dfseq, dfrunning], axis=1)
        #     return df_new

        
        
        # def tier_time_patterns(df, names):
        #     # {'macd': {'tier4_macd-RED': (-3.062420318268792, 0.0), 'current_value': -1.138314020642838}
        #     names = ['macd', 'signal', 'hist']
        #     for name in names:
        #         tier_name = f'tier_{name}' # tier_macd
        #         item_list = df[tier_name].to_list()
        #         res = count_sequential_n_inList(item_list)

        #         tier_list = list(set(df[tier_name].to_list()))

                
        #         for tier in tier_list:
        #             if tier.lower().startswith('t'): # ensure tier
        #                 df_tier = df[df[tier_name] == tier].copy()
        #                 x = df_tier["timestamp_est"].to_list()

        # # macd_high = df_i[df_i[mac_name] == mac_world['{}_high'.format(mac_name)]].timestamp_est # last time High
        # # macd_min = df_i[df_i[mac_name] == mac_world['{}_low'.format(mac_name)]].timestamp_est # last time Low
        
        # try:  # count_sequential_n_inList
        #     for mac_name in ['macd', 'signal', 'hist']:
        #         df = count_sequential_n_inList(df=df, item_list=df['tier_'+mac_name].to_list(), mac_name=mac_name)

        #         # distance from prior HIGH LOW
        #         toptier = f'{"tier1"}{"_"}{mac_name}{"-GREEN"}'
        #         bottomtier = f'{"tier1"}{"_"}{mac_name}{"-RED"}'
        #         # Current Distance from top and bottom
        #         for tb in [toptier, bottomtier]:
        #             df_t = df[df['tier_'+mac_name]==tb].copy()
        #             last_time_tier_found = df_t.iloc[-1].story_index
        #             distance_from_last_tier = df.iloc[-1].story_index - df_t.iloc[-1].story_index
        #             betty_bee[f'{ticker_time_frame}{"--"}{"tier_"}{mac_name}{"-"}{tb.split("-")[-1]}'] = distance_from_last_tier
        #         QUEEN[queens_chess_piece]['pollenstory_info']['betty_bee'] = betty_bee

        # except Exception as e:
        #     msg=(e,"--", print_line_of_error(), "--", ticker_time_frame, "--", mac_name)
        #     logging.error(msg)


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

def return_trade_bars(symbol, start_date_iso, end_date_iso, limit=None):
    # symbol = 'SPY'
    # start_date_iso = '2022-03-10 19:00' # 2 PM EST start_date_iso = '2022-03-10 14:30'
    # end_date_iso = '2022-03-10 19:15' # end_date_iso = '2022-03-10 20:00'
    # Function to check if trade has one of inputted conditions
    def has_condition(condition_list, condition_check):
        if type(condition_list) is not list: 
            # Assume none is a regular trade?
            in_list = False
        else:
            # There are one or more conditions in the list
            in_list = any(condition in condition_list for condition in condition_check)

        return in_list

    exclude_conditions = [
    'B',
    'W',
    '4',
    '7',
    '9',
    'C',
    'G',
    'H',
    'I',
    'M',
    'N',
    'P',
    'Q',
    'R',
    'T',
    'U',
    'V',
    'Z'
    ]

    # fetch trades over whatever timeframe you need
    start_time = pd.to_datetime(start_date_iso, utc=True)
    end_time = pd.to_datetime(end_date_iso, utc=True)

    trades_df = api.get_trades(symbol=symbol, start=start_time.isoformat(), end=end_time.isoformat(), limit=limit).df

    # convert to market time for easier reading
    trades_df = trades_df.tz_convert('America/New_York')

    # add a column to easily identify the trades to exclude using our function from above
    trades_df['exclude'] = trades_df.conditions.apply(has_condition, condition_check=exclude_conditions)

    # filter to only look at trades which aren't excluded
    valid_trades = trades_df.query('not exclude')

    # # Resample the valid trades to calculate the OHLCV bars
    # agg_functions = {'price': ['first', 'max', 'min', 'last'], 'size': 'sum'}
    # min_bars = valid_trades.resample('1T').agg(agg_functions)

    # Resample the trades to calculate the OHLCV bars
    agg_functions = {'price': ['first', 'max', 'min', 'last'], 'size': ['sum', 'count']}

    valid_trades = trades_df.query('not exclude')
    min_bars = valid_trades.resample('1T').agg(agg_functions)

    min_bars = min_bars.droplevel(0, 'columns')
    min_bars.columns=['open', 'high', 'low' , 'close', 'volume', 'trade_count']

    return min_bars



def Return_Bars_list_LatestDayRebuild(ticker_time): #Iniaite Ticker Charts with Indicator Data
    # IMPROVEMENT: use Return_bars_list for Return_Bars_LatestDayRebuild
    # ticker_time = "SPY_1Minute_1Day"

    ticker, time_name, days = ticker_time.split("_")
    error_dict = {}
    s = datetime.datetime.now()
    dfs_index_tickers = {}
    try:
        # return market hours data from bars
        bars_data = return_bars(symbol=ticker, time=time_name, ndays=0, trading_days_df=trading_days_df) # return [True, symbol_data, market_hours_data, after_hours_data]
        df_bars_data = bars_data[2] # mkhrs if in minutes
        df_bars_data = df_bars_data.reset_index()
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
# Return_Bars_LatestDayRebuild(ticker_time)


def Return_Init_ChartData(ticker_list, chart_times): #Iniaite Ticker Charts with Indicator Data
    # ticker_list = ['SPY', 'QQQ']
    # chart_times = {"1Minute": 1, "5Minute": 5, "30Minute": 18, "1Hour": 48, "2Hour": 72, "1Day": 233}
    # MACD={'fast': 16, 'slow': 29} 
   
    error_dict = {}
    s = datetime.datetime.now()
    dfs_index_tickers = {}
    for ticker in tqdm(ticker_list):
        for time_frames, ndays in chart_times.items(): # 1day: 250, 1minute: 0
            try:
                bars_data = return_bars(symbol=ticker, time=time_frames, ndays=ndays, trading_days_df=trading_days_df) # return [True, symbol_data, market_hours_data, after_hours_data]
                df_bars_data = bars_data[2] # mkhrs if in minutes
                df_bars_data = df_bars_data.reset_index()
                if bars_data[0] == False:
                    error_dict["NoData"] = bars_data[1] # symbol already included in value
                else:
                    name = ticker + "_" + time_frames
                    dfs_index_tickers[name] = df_bars_data
            except Exception as e:
                print(e)
                print(ticker, time_frames, ndays)
    
    e = datetime.datetime.now()
    msg = {'function':'init_ticker_charts_data',  'func_timeit': str((e - s)), 'datetime': datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S_%p')}
    print(msg)
    # dfs_index_tickers['SPY_5Minute']
    return [dfs_index_tickers, error_dict]
# Return_Init_ChartData = init_ticker_charts_data(ticker_list=ticker_list, chart_times=chart_times)




    def count_sequential_n_inList(df, item_list):
        item_list = df['tier_macd'].to_list()
        df_token = df['tier_macd'].copy()
        # item_dict = dict(zip(df.index, df['tier_macd']))
        # res_dict = {}
        d = defaultdict(int)
        res_list = []
        # for i, el in item_dict.items():
        #     if i == 0:
        #         res_dict[i] = 0
        #         d[el]+=1
        #         res_list.append(d[el])
        #         d[el]+=1
        #     else:
        #         seq_el = item_dict[i-1]
        #         # seq_el = item_list[i-1]
        #         if el == seq_el:
        #             d[el]+=1
        #             res_dict[i] = d[el]
        #             res_list.append(d[el])
        #         else:
        #             d[el]=0
        #             res_dict[i] = d[el]
        #             res_list.append(d[el])
        
        for i, el in enumerate(item_list):
            # ipdb.set_trace()
            if i == 0:
                res_list.append(d[el])
                d[el]+=1
            else:
                seq_el = item_list[i-1]
                if el == seq_el:
                    d[el]+=1
                    res_list.append(d[el])
                else:
                    d[el]=0
                    res_list.append(d[el])
        df2 = pd.DataFrame(res_list, columns=['seq_'+mac_name])
        df_new = pd.concat([df, df2], axis=1)
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



# [0, 0, 0, 1, 2]                    


        # how long since prv High/Low? 
        # when was the last time you were in higest tier
        # how many times have you reached tiers
        # how long have you stayed in your tier?
        # side of tier, are you closer to exit or enter of next tier?
        macd_high = df_i[df_i[mac_name] == mac_world['{}_high'.format(mac_name)]].timestamp_est # last time High
        macd_min = df_i[df_i[mac_name] == mac_world['{}_low'.format(mac_name)]].timestamp_est # last time Low

# this counts seq. Numbers and upates past numbers
from itertools import count
from collections import defaultdict

c = defaultdict(count)
x = df[tier_name].to_list()

x = [2,3,4,2,2,2]

[next(c[n]) for n in x ]


# Day Trading Margin Requirements
# dtbp = 4 x prev_eod_excess_margin
# prev_eod_excess_margin = prev_equity - prev_maintenance_margin
# dtbp = 4 x (prev_equity - prev_maintenance_margin)
        BETTY_bee[ticker_time] = {}
        # 1. whats is tier?  >>> 2. how long since prv High/Low?
        for mac_name in ['macd', 'signal', 'hist']:
            ticker_time_tiers = CHARLIE_bee[ticker_time]
            current_value = df_i[mac_name].iloc[-1] # df_i['macd'].iloc[-1]

            if current_value < 0:
                chart_range = {k:v for (k,v) in ticker_time_tiers.items() if mac_name in k and "RED" in k}
            else:
                chart_range = {k:v for (k,v) in ticker_time_tiers.items() if mac_name in k and "GREEN" in k}
            
            for tier_macname_sector, tier_range in chart_range.items():
                if abs(current_value) <= abs(tier_range[0]) and abs(current_value) >= abs(tier_range[1]):
                    BETTY_bee[ticker_time][mac_name] = {tier_macname_sector: tier_range, 'current_value': current_value}




""" Return Tickers of SP500 & Nasdaq / Other Tickers"""
table=pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
df = table[0]
sp500 = df['Symbol'].tolist()

# TOP 100 ETFs
table=pd.read_html('https://etfdb.com/compare/market-cap/')
df = table[0]
ETF_list = df['Symbol'].tolist()
""" Return Tickers of SP500 & Nasdaq / Other Tickers"""

""" not using

def return_ticker_min(symbol, time, sec_n):
    # how should 1 day 1 min be built? start to now every time? 
    # or store in dict and return increment? WINNER
        # first call returns up until now & then second returns stored main_df

    now = datetime.datetime.now()
    main_time = pd.DataFrame()

    symbol = 'SPY'
    sec_n = 10000 # 1 day: 27000, 5min: 330
    min = sec_n / 60
    time = tradeapi.TimeFrame(1, tradeapi.TimeFrameUnit.Minute) # every second

    start_date_iso = datetime.datetime.now().strftime('%Y-%m-%d') + ' 19:00'
    a = datetime.datetime.strptime(start_date_iso, '%Y-%m-%d %H:%M')
    # a = datetime.datetime.now()
    b = a + datetime.timedelta(0, sec_n) # days, seconds, then other fields.
    end_date_iso = str(b)[:16]
    
    now = datetime.datetime.now()

    # spy_1min = return_bars(api=api, symbol='SPY', timeframe=time, start_date=start_date, end_date=end_date) # return 1 Day Mac
    spy_1min = return_trade_bars(symbol, start_date_iso, end_date_iso, limit=None)
    spy_1min = spy_1min.reset_index()
    df_calc = return_VWAP(spy_1min)
    df_calc = return_MACD(spy_1min, fast=12, slow=16)




# def return_RSI(df):
# 	window_length = 14
# 	df['diff'] = df.diff(1)
# 	df['gain'] = df['diff'].clip(lower=0).round(2)
# 	df['loss'] = df['diff'].clip(upper=0).abs().round(2)
# 	# Get initial Averages
# 	df['avg_gain'] = df['gain'].rolling(window=window_length, min_periods=window_length).mean()[:window_length+1]
# 	df['avg_loss'] = df['loss'].rolling(window=window_length, min_periods=window_length).mean()[:window_length+1]
# 	# Get WMS averages
# 	# Average Gains
# 	for i, row in enumerate(df['avg_gain'].iloc[window_length+1:]):
# 		df['avg_gain'].iloc[i + window_length + 1] =\
# 			(df['avg_gain'].iloc[i + window_length] *
# 			(window_length - 1) +
# 			df['gain'].iloc[i + window_length + 1])\
# 			/ window_length
# 	# Average Losses
# 	for i, row in enumerate(df['avg_loss'].iloc[window_length+1:]):
# 		df['avg_loss'].iloc[i + window_length + 1] =\
# 			(df['avg_loss'].iloc[i + window_length] *
# 			(window_length - 1) +
# 			df['loss'].iloc[i + window_length + 1])\
# 			/ window_length

# 	# Calculate RS Values
# 	df['rs'] = df['avg_gain'] / df['avg_loss']
# 	# Calculate RSI
# 	df['rsi'] = 100 - (100 / (1.0 + df['rs']))

def relative_strength_index(frame):
    delta = frame['close'].diff()
    up = delta.clip(lower=0)
    down = -1 * delta.clip(upper=0)
    ema_up = up.ewm(com=13, adjust=False).mean()
    ema_down = down.ewm(com=3, adjust=False).mean()
    rsi = ema_up/ema_down
    frame['rsi'] = rsi

    return frame
"""

""" XXXXXXXXXXX depricated functions XXXXXXXXXX"""

def old_return_bars(api, symbol, timeframe, start_date, end_date):
    # symbol = 'SPY'
    # time = 1
    # timeframe = tradeapi.TimeFrame(1, tradeapi.TimeFrameUnit.Minute) # every second
    # start_date = '2022-02-15'
    # end_date = '2022-02-15'
    start_date = pd.to_datetime('2022-02-17 19:00', utc=True)
    end_date = pd.to_datetime('2022-02-17 19:15', utc=True)
    ticker = api.get_bars(symbol, timeframe, start_date.isoformat(), end_date.isoformat())
    df = ticker.df.reset_index()
    df['timestamp_est'] = df['timestamp'].apply(lambda x: x.astimezone(est))

    # macd = df.ta.macd(close='close', fast=12, slow=26, append=True)
    # print(df.iloc[-1])

    return df


def old_return_latest_trade(api, symbol):
    resp = api.get_latest_trade(symbol)
    di = {}
    d = vars(resp)
    data = d["_raw"] # raw data
    dataname = d["_reversed_mapping"] # data names
    for k,v in dataname.items():
        if v in data.keys():
            di[str(k)] = data[v]
    data['time_est'] = convert_todatetime_string(data['t']) # add est
    # QuoteV2({   'ap': 448.27,
    #     'as': 3,
    #     'ax': 'X',
    #     'bp': 448.25,
    #     'bs': 4,
    #     'bx': 'T',
    #     'c': ['R'],
    #     't': '2022-02-11T16:19:51.467033352Z',    
    #     'z': 'B'})
    return data


def old_return_latest_quote(api, symbol, tradeconditions=True):
    resp = api.get_latest_quote(symbol)
    di = {}
    d = vars(resp)
    data = d["_raw"] # raw data
    dataname = d["_reversed_mapping"] # data names
    for k,v in dataname.items():
        if v in data.keys():
            di[str(k)] = data[v]
    data['time_est'] = convert_todatetime_string(data['t']) # add est
    # QuoteV2({   'ap': 448.27,
    #     'as': 3,
    #     'ax': 'X',
    #     'bp': 448.25,
    #     'bs': 4,
    #     'bx': 'T',
    #     'c': ['R'],
    #     't': '2022-02-11T16:19:51.467033352Z',    
    #     'z': 'B'})
    return data



# # Return order Status
# def clientId_order_status(api, client_id_order):
#     open_orders_list = api.list_orders(status='open')
#     if client_id_order:
#         order_token = api.get_order_by_client_order_id(client_id_order)
#     else:
#         order_token = False
#     return [True, spdn_order, open_orders_list]


""" entity_v2.py Alpaca symbol matching"""
# trade_mapping_v2 = {
#     "i": "id",
#     "S": "symbol",
#     "c": "conditions",
#     "x": "exchange",
#     "p": "price",
#     "s": "size",
#     "t": "timestamp",
#     "z": "tape",  # stocks only
#     "tks": "takerside"  # crypto only
# }

# quote_mapping_v2 = {
#     "S":  "symbol",
#     "x": "exchange",  # crypto only
#     "ax": "ask_exchange",
#     "ap": "ask_price",
#     "as": "ask_size",
#     "bx": "bid_exchange",
#     "bp": "bid_price",
#     "bs": "bid_size",
#     "c":  "conditions",  # stocks only
#     "t":  "timestamp",
#     "z":  "tape"  # stocks only
# }

# bar_mapping_v2 = {
#     "S":  "symbol",
#     "x": "exchange",  # crypto only
#     "o":  "open",
#     "h":  "high",
#     "l":  "low",
#     "c":  "close",
#     "v":  "volume",
#     "t":  "timestamp",
#     "n":  "trade_count",
#     "vw": "vwap"
# }

# status_mapping_v2 = {
#     "S":  "symbol",
#     "sc": "status_code",
#     "sm": "status_message",
#     "rc": "reason_code",
#     "rm": "reason_message",
#     "t":  "timestamp",
#     "z":  "tape"
# }

# luld_mapping_v2 = {
#     "S": "symbol",
#     "u": "limit_up_price",
#     "d": "limit_down_price",
#     "i": "indicator",
#     "t": "timestamp",
#     "z": "tape"
# }

# cancel_error_mapping_v2 = {
#     "S": "symbol",
#     "i": "id",
#     "x": "exchange",
#     "p": "price",
#     "s": "size",
#     "a": "cancel_error_action",
#     "z": "tape",
#     "t": "timestamp",
# }

# correction_mapping_v2 = {
#     "S": "symbol",
#     "x": "exchange",
#     "oi": "original_id",
#     "op": "original_price",
#     "os": "original_size",
#     "oc": "original_conditions",
#     "ci": "corrected_id",
#     "cp": "corrected_price",
#     "cs": "corrected_size",
#     "cc": "corrected_conditions",
#     "z": "tape",
#     "t": "timestamp",
# }

""" snapshot"""
# snapshots = api.get_snapshots(['AAPL', 'IBM'])
# snapshots['AAPL'].latest_trade.price

# In [34]: vars(api.get_snapshot("SPY"))
# Out[34]: 
# {'latest_trade': TradeV2({   'c': [' ', 'M'],
#      'i': 52983677401155,
#      'p': 420.07,
#      's': 2018694,
#      't': '2022-03-12T01:00:00.00258816Z',
#      'x': 'P',
#      'z': 'B'}),
#  'latest_quote': QuoteV2({   'ap': 419.95,
#      'as': 245,
#      'ax': 'P',
#      'bp': 419.94,
#      'bs': 19,
#      'bx': 'P',
#      'l': 419.91,
#      'n': 56,
#      'o': 419.92,
#      't': '2022-03-12T00:59:00Z',
#      'v': 2397,
#      'vw': 419.929908}),
#  'daily_bar': BarV2({   'c': 420.07,
#      'h': 428.77,
#      'l': 419.53,
#      'n': 809145,
#      'o': 428.18,
#      't': '2022-03-11T05:00:00Z',
#      'v': 90803923,
#      'vw': 424.040193}),
#  'prev_daily_bar': BarV2({   'c': 425.48,
#      'h': 426.43,
#      'l': 420.44,
#      'n': 891241,
#      'o': 422.73,
#      't': '2022-03-10T05:00:00Z',
#      'v': 91933914,
#      'vw': 423.871044})}



"""Order Return ref"""
# Out[14]: 
# Order({   'asset_class': 'us_equity',
#     'asset_id': 'b28f4066-5c6d-479b-a2af-85dc1a8f16fb',
#     'canceled_at': None,
#     'client_order_id': '001',
#     'created_at': '2022-02-08T16:20:07.813040847Z',
#     'expired_at': None,
#     'extended_hours': False,
#     'failed_at': None,
#     'filled_at': None,
#     'filled_avg_price': None,
#     'filled_qty': '0',
#     'hwm': None,
#     'id': '5dbcb543-956b-4eec-b9b8-fc768d517da9',
#     'legs': None,
#     'limit_price': '449.2',
#     'notional': None,
#     'order_class': '',
#     'order_type': 'limit',
#     'qty': '1',
#     'replaced_at': None,
#     'replaced_by': None,
#     'replaces': None,
#     'side': 'buy',
#     'status': 'accepted',
#     'stop_price': None,
#     'submitted_at': '2022-02-08T16:20:07.812422547Z',
#     'symbol': 'SPY',
#     'time_in_force': 'gtc',
#     'trail_percent': None,
#     'trail_price': None,
#     'type': 'limit',
#     'updated_at': '2022-02-08T16:20:07.813040847Z'})


# def old_return_bars(symbol, time, ndays, trading_days_df):
#     try:
#         s = datetime.datetime.now()
#         # ndays = 0 # today 1=yesterday...  # TEST
#         # time = "1Min" #"1Day" # "1Min"  # TEST
#         # symbol = 'SPY'  # TEST
#         # current_day = api.get_clock().timestamp.date().isoformat()  # TEST MOVED TO GLOBAL
#         # trading_days = api.get_calendar()  # TEST MOVED TO GLOBAL
#         # trading_days_df = pd.DataFrame([day._raw for day in trading_days])  # TEST MOVED TO GLOBAL

#         symbol_n_days = trading_days_df.query('date < @current_day').tail(ndays)

#         # Fetch bars for those days
#         symbol_data = api.get_bars(symbol, time,
#                                     start=symbol_n_days.head(1).date,
#                                     end=symbol_n_days.tail(1).date, 
#                                     adjustment='all').df.reset_index()
#         # est = pytz.timezone("US/Eastern") # GlovalVar
#         symbol_data['timestamp_est'] = symbol_data['timestamp'].apply(lambda x: x.astimezone(est))
#         symbol_data['timestamp_est_timestamp'] = symbol_data['timestamp_est'].apply(lambda x: datetime.datetime.fromtimestamp(x.timestamp()))
    
#         symbol_data["day"] = symbol_data['timestamp_est'].apply(lambda x: x.day)
#         symbol_data["month"] = symbol_data['timestamp_est'].apply(lambda x: x.month)
#         symbol_data["year"] = symbol_data['timestamp_est'].apply(lambda x: x.year)
#         symbol_data["date_Id"] = symbol_data["year"].astype(str) + symbol_data["month"].astype(str) + symbol_data["day"].astype(str)
        
#         date_list = list(set(symbol_data["date_Id"].tolist())) # group to then split up market hours
        
#         symbol_data['index'] = symbol_data.index
#         def split_market_open_hrs(df):
#             day = df["timestamp_est"].iloc[0].day
#             month = df["timestamp_est"].iloc[0].month
#             year = df["timestamp_est"].iloc[0].year        
#             formater = "%Y-%m-%d %H:%M:%S"
#             str_timestamp = "{}-{}-{} 09:30:00".format(year, month, day)
#             df['open_time'] = datetime.datetime.strptime(str_timestamp, formater)
#             str_timestamp = "{}-{}-{} 16:00:00".format(year, month, day)
#             df['closed_time'] = datetime.datetime.strptime(str_timestamp, formater)
#             return df
        
#         market_hrs_join = {}
#         for i in date_list:
#             t = symbol_data.copy()
#             t = t[t["date_Id"]==i].copy()
#             t = split_market_open_hrs(df=t)
#             t['after_hours_tag'] = np.where((t['timestamp_est_timestamp']>=t['open_time']) & (t['timestamp_est_timestamp']<=t['closed_time']), "MarketHours", "AfterHours")
#             d = dict(zip(t['index'], t['after_hours_tag']))
#             market_hrs_join.update(d)



#         # symbol_data['after_hours_tag'] = np.where((symbol_data['timestamp_est_timestamp']>=market_reg_open) & (symbol_data['timestamp_est_timestamp']<=market_reg_close), "MarketHours", "AfterHours")
#         symbol_data['after_hours_tag'] = symbol_data['index'].map(market_hrs_join)
#         market_hours_data = symbol_data[symbol_data['after_hours_tag']=='MarketHours'].copy()
#         after_hours_data = symbol_data[symbol_data['after_hours_tag']=='AfterHours'].copy()

#         e = datetime.datetime.now()
#         print(str((e - s)) + ": " + datetime.datetime.now().strftime('%Y-%m-%d %H:%M'))
#         return [symbol_data, market_hours_data, after_hours_data]
#     # handle error
#     except Exception as e:
#         print("sending email of error", e)