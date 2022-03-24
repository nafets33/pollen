# archived_functions


# Day Trading Margin Requirements
# dtbp = 4 x prev_eod_excess_margin
# prev_eod_excess_margin = prev_equity - prev_maintenance_margin
# dtbp = 4 x (prev_equity - prev_maintenance_margin)


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