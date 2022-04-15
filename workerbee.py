from ast import Break
from math import floor
from termcolor import colored as cl
import matplotlib.pyplot as plt
def get_macd(df_main, price, slow, fast, smooth):
    exp1 = price.ewm(span = fast, adjust = False).mean()
    exp2 = price.ewm(span = slow, adjust = False).mean()
    macd = pd.DataFrame(exp1 - exp2).rename(columns = {'close':'macd'})
    signal = pd.DataFrame(macd.ewm(span = smooth, adjust = False).mean()).rename(columns = {'macd':'signal'})
    hist = pd.DataFrame(macd['macd'] - signal['signal']).rename(columns = {0:'hist'})
    frames =  [macd, signal, hist]
    df = pd.concat(frames, join = 'inner', axis = 1)
    return pd.concat(df_main, df)
    return df

googl_macd = get_macd(googl['close'], 26, 12, 9)
googl_macd.tail()


def plot_macd(prices, macd, signal, hist):
    ax1 = plt.subplot2grid((8,1), (0,0), rowspan = 5, colspan = 1)
    ax2 = plt.subplot2grid((8,1), (5,0), rowspan = 3, colspan = 1)

    ax1.plot(prices)
    ax2.plot(macd, color = 'grey', linewidth = 1.5, label = 'MACD')
    ax2.plot(signal, color = 'skyblue', linewidth = 1.5, label = 'SIGNAL')

    for i in range(len(prices)):
        if str(hist[i])[0] == '-':
            ax2.bar(prices.index[i], hist[i], color = '#ef5350')
        else:
            ax2.bar(prices.index[i], hist[i], color = '#26a69a')

    plt.legend(loc = 'lower right')
    plt.show()

# plot_macd(googl['close'], googl_macd['macd'], googl_macd['signal'], googl_macd['hist'])

plot_macd(spy['close'], spy['MACD_12_26_9'], spy['MACDs_12_26_9'], spy['MACDh_12_26_9'])

plot_macd(x['close'], x['MACD_12_26_9'], x['MACDs_12_26_9'], x['MACDh_12_26_9'])


ax1 = plt.subplot2grid((8,1), (0,0), rowspan = 5, colspan = 1)
ax2 = plt.subplot2grid((8,1), (5,0), rowspan = 3, colspan = 1)

googl = spy
ax1.plot(googl['close'], color = 'skyblue', linewidth = 2, label = 'GOOGL')
ax1.plot(googl.index, buy_price, marker = '^', color = 'green', markersize = 10, label = 'BUY SIGNAL', linewidth = 0)
ax1.plot(googl.index, sell_price, marker = 'v', color = 'r', markersize = 10, label = 'SELL SIGNAL', linewidth = 0)
ax1.legend()
ax1.set_title('GOOGL MACD SIGNALS')
ax2.plot(googl_macd['macd'], color = 'grey', linewidth = 1.5, label = 'MACD')
ax2.plot(googl_macd['signal'], color = 'skyblue', linewidth = 1.5, label = 'SIGNAL')

for i in range(len(googl_macd)):
    if str(googl_macd['hist'][i])[0] == '-':
        ax2.bar(googl_macd.index[i], googl_macd['hist'][i], color = '#ef5350')
    else:
        ax2.bar(googl_macd.index[i], googl_macd['hist'][i], color = '#26a69a')
        
plt.legend(loc = 'lower right')
plt.show()

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

def submit_best_limit_order(symbol, qty, side, client_order_id=False):
    # side = 'buy'
    # qty = '1'
    # symbol = 'BABA'
    snapshot = api.get_snapshot(symbol) # return_last_quote from snapshot
    conditions = snapshot.latest_quote.conditions
    while True:
        print(conditions)
        valid = [j for j in conditions if j in exclude_conditions]
        if valid:
            break
        else:
            snapshot = api.get_snapshot(symbol) # return_last_quote from snapshot
            conditions = snapshot.latest_quote.conditions    
    
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

def order_filled(client_order_id):
    order_status = api.get_order_by_client_order_id(client_order_id=client_order_id)
    filled_qty = order_status.filled_qty
    order_status.status
    order_status.filled_avg_price
    while True:
        if order_status.status == 'filled':
            print("order fully filled")
            break
    return True

order = submit_best_limit_order(symbol='BABA', qty=1, side='sell', client_order_id=client_order_id)


In [84]: market_hours_data.columns
Out[84]: 
Index(['timestamp', 'open', 'high', 'low', 'close', 'volume', 'trade_count',        
       'vwap', 'index_timestamp', 'timestamp_est_timestamp'],
      dtype='object')
main_symbols_full_list = main_symbols_full_list[:200]
s=datetime.datetime.now()
for i in main_symbols_full_list:
    api.get_snapshot(i)

e=datetime.datetime.now()
print(e-s)

s=datetime.datetime.now()
api.get_snapshots(main_symbols_full_list)
e=datetime.datetime.now()
print(e-s)





def Return_Snapshots_Rebuild(df_tickers_data):
    ticker_list = list([set(j.split("_")[0] for j in df_tickers_data.keys())][0]) #> get list of tickers
    
    snapshots = api.get_snapshots(ticker_list)

    float_cols = ['close', 'high', 'open', 'low', 'vwap']
    int_cols = ['volume', 'trade_count']
    main_return_dict = {}

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
            df_daily = df_daily.rename(columns={'timestamp': 'timestamp_est'})
            
            return_dict[ticker + "_day"] = df_daily

            d = {'close': snapshots[ticker].minute_bar.close,
            'high': snapshots[ticker].minute_bar.high,
            'low': snapshots[ticker].minute_bar.low,
            'timestamp': snapshots[ticker].minute_bar.timestamp,
            'open': snapshots[ticker].minute_bar.open,
            'volume': snapshots[ticker].minute_bar.volume,
            'trade_count': snapshots[ticker].minute_bar.trade_count,
            'vwap': snapshots[ticker].minute_bar.vwap
            }
            df_minute = pd.Series(d).to_frame().T
            for i in float_cols:
                df_minute[i] = df_minute[i].apply(lambda x: float(x))
            for i in int_cols:
                df_minute[i] = df_minute[i].apply(lambda x: int(x))
            df_minute = df_minute.rename(columns={'timestamp': 'timestamp_est'})

            return_dict[ticker + "_minute"] = df_minute
        
        return return_dict
    snapshot_ticker_data = response_returned(ticker_list)

    for ticker in chartdata in df_tickers_data.items():
        symbol_snapshots = {k:v for (k,v) in snapshot_ticker_data.items() if k.split("_")[0] == ticker.split("_")[0]}
        symbol, timeframe = ticker.split("_")
        if "Day" in timeframe:
            pass
            # concat the day snapshot
        if "Minute" in timeframe:
            # chartdata = df_tickers_data["SPY_1Minute"]
            df_minute_snapshot = symbol_snapshots[f'{symbol}{"_minute"}'] # stapshot df
            df_rebuild = pd.concat([chartdata, df_minute_snapshot]) # concat minute
            main_return_dict[ticker] = df_rebuild
            # assert ensure df is solid (dtypes are correct)
            


    
    return [df_daily, df_minute]
#beer = Return_Snapshots(ticker_list=['QQQ', 'SPY', 'MFST', 'MSFT'])







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



bee = return_getbars_WithIndicators(bars_data=df_bars_data, MACD=MACD)
if bee[0] == False:
    error_dict["Indicators"] = {ticker: bee[1]}
else: a
    name = ticker + "_" + time_frames
    dfs_index_tickers[name] = bee[1]




s = return_snapshots(ticker_list)

    snapshots = api.get_snapshots(ticker_list)
    # x=vars(snapshots)

    l = []
    x = snapshots[ticker].daily_bar.close,
    y = snapshots[ticker].daily_bar.high,
    b = snapshots[ticker].daily_bar.low,
    e = snapshots[ticker].daily_bar.timestamp,
    e2 = snapshots[ticker].daily_bar.open,
    s = snapshots[ticker].daily_bar.volume
    l.append([x,y,b,e,e2,s])



    dl = {
    'close': snapshots[ticker].daily_bar.close,
    'high': snapshots[ticker].daily_bar.high,
    'low': snapshots[ticker].daily_bar.low,
    'timestamp_est': snapshots[ticker].daily_bar.timestamp,
    'open': snapshots[ticker].daily_bar.open,
    'volume': snapshots[ticker].daily_bar.volume,
    }
    df = pd.Series(dl).to_frame().T

    d = {'close': snapshots[ticker].minute_bar.close,
    'high': snapshots[ticker].minute_bar.high,
    'low': snapshots[ticker].minute_bar.low,
    'timestamp': snapshots[ticker].minute_bar.timestamp,
    'open': snapshots[ticker].minute_bar.open,
    'volume': snapshots[ticker].minute_bar.volume}
    df = pd.Series(d).to_frame().T
    

    # snapshots[ticker].daily_bar.vwrap
    df = pd.Series(snapshots['WMT']['minute_bar']).to_frame().T
    df['index_timestamp'] = df['timestamp'].apply(lambda x: convert_todatetime_string(x))
    df['timestamp_est'] = df['index_timestamp'].apply(lambda x: x.astimezone(est))
# df = df.set_index('index_timestamp')
# df['index_timestamp'].tz_convert('US/Eastern')
#     df_n = pd.concat([bars_data_df, df], ignore_index=True)
#     df_n['timestamp'] = df_n['timestamp_est_timestamp'].apply(lambda x: convert_todatetime_string(x))

# datetime.datetime.fromisoformat(df_n.iloc[-1].timestamp)
# df_n['index_timestamp'] = df_n['timestamp'].apply(lambda x: convert_todatetime_string(x))
# df_n['timestamp_est'] = df_n['timestamp'].apply(lambda x: x.astimezone(est))


# df_n['index_timestamp'] = df_n.index
# df_n['timestamp_est'] = df_n['timestamp'].apply(lambda x: x.astimezone(est))
# df_n['timestamp_est_timestamp'] = df_n['timestamp_est'].apply(lambda x: datetime.datetime.fromtimestamp(x.timestamp()))



    t = snapshots['WMT']['latest_trade']['price']
    snapshots['WMT']['daily_bar']['price']

def open_orders_beeManager(orders):
    
    def order_pulse(time_in_trade):
        decision = {}
        time_in_trade = 4 # 3 Mins
        return decision

    # order is open manage when trade will be closed
    time_trade_horizion = # guage on when to trade out (i.e. critical mass for profits)
    profit_take_block1 = .03 # % to sell
    profit_take_block2 = .05 # % to sell
    profit_take_ALL = # Full Position
    exit_trade_block1 = .02 # % to sell
    exit_trade_block2 = .02 # % to sell
    exit_trade_ALL = # Full Position
    return True


def QueenBee(): # Order Management
    acc_info = 	refresh_account_info(api)
    open_orders = 
    num_of_trades = 
    day_profitloss = 
    max_num_of_trades = 10
    happy_ending = .02 #2%
    bee_ticks = # current tick momentum
    bee_1min = # current momentum (use combination of RSI, MACD to Determine weight of BUY/SELL)
    bee_5min = # current momentum (use combination of RSI, MACD to Determine weight of BUY/SELL)
    bee_1month = # current momentum (use combination of RSI, MACD to Determine weight of BUY/SELL)
    bee_3month = # current momentum (use combination of RSI, MACD to Determine weight of BUY/SELL)
    bee_6month = # current momentum (use combination of RSI, MACD to Determine weight of BUY/SELL)
    bee_1yr = # current momentum (use combination of RSI, MACD to Determine weight of BUY/SELL)

    if open_orders: # based on indicators decide whether to close position
        open_orders_bee_manager(orders)





a = 0
while True:
    return_last_trade_price
    if last_trade_price_min - ticker_last_trade_price_min > 2:
        refresh(ticker_data)
    
    re_build_charts(last_trade_price) # return all new objects (allowed obj based on how many pr may return wihtin the minute)

    order_managment(ticker_obj_list)
































def init_ticker_charts_data(ticker_list, chart_times, MACD): #Iniaite Ticker Charts with Indicator Data
    # ticker_list = ['SPY', 'QQQ']
    # chart_times = {"1Minute": 1, "5Minute": 5, "30Minute": 18, "1Hour": 48, "2Hour": 72, "1Day": 233}
    # MACD={'fast': 16, 'slow': 29}
        
    df_n = pd.concat([df_bars_data, df], ignore_index=False)
 
   
    error_dict = {}
    s = datetime.datetime.now()
    dfs_index_tickers = {}
    for ticker in tqdm(ticker_list):
        for time_frames, ndays in chart_times.items(): # 1day: 250, 1minute: 0
            try:
                bars_data = return_bars(symbol=ticker, time=time_frames, ndays=ndays, trading_days_df=trading_days_df) # return [True, symbol_data, market_hours_data, after_hours_data]
                df_bars_data = bars_data[2] # mkhrs if in minutes
                df_bars_data = df_bars_data.reset_index()
                # def rebuild_chart_data_with_latest(df=bars_data_df, ticker=ticker):
                #     # >>>> Rebuild Chart Data
                #     snapshots = return_snapshots(ticker)
                #     snapshot_errors = snapshots[1]
                #     snapshots = snapshots[0]

                if bars_data[0] == False:
                    error_dict["NoData"] = bars_data[1] # symbol already included in value
                else:
                    bee = return_getbars_WithIndicators(bars_data=df_bars_data, MACD=MACD)
                    if bee[0] == False:
                        error_dict["Indicators"] = {ticker: bee[1]}
                    else:
                        name = ticker + "_" + time_frames
                        dfs_index_tickers[name] = bee[1]
            except Exception as e:
                print(e)
                print(ticker, time_frames, ndays)
    
    snapshots = Return_Snapshots(ticker_list=ticker_list)
    e = datetime.datetime.now()
    msg = {'function':'init_ticker_charts_data',  'func_timeit': str((e - s)), 'datetime': datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S_%p')}
    print(msg)
    # dfs_index_tickers['SPY_5Minute']
    return [dfs_index_tickers, error_dict]
# df_tickers_data = init_ticker_charts_data(main_index_tickers=main_index_tickers, chart_times=chart_times)
























import FundamentalAnalysis as fa

ticker = "AAPL"
api_key = "64d71a66be2036aa9f3d46da92962af1"

# Show the available companies
companies = fa.available_companies(api_key)

# Collect general company information
profile = fa.profile(ticker, api_key)

# Collect recent company quotes
quotes = fa.quote(ticker, api_key)

# Collect market cap and enterprise value
entreprise_value = fa.enterprise(ticker, api_key)

# Show recommendations of Analysts
ratings = fa.rating(ticker, api_key)

# Obtain DCFs over time
dcf_annually = fa.discounted_cash_flow(ticker, api_key, period="annual")
dcf_quarterly = fa.discounted_cash_flow(ticker, api_key, period="quarter")

# Collect the Balance Sheet statements
balance_sheet_annually = fa.balance_sheet_statement(ticker, api_key, period="annual")
balance_sheet_quarterly = fa.balance_sheet_statement(ticker, api_key, period="quarter")

# Collect the Income Statements
income_statement_annually = fa.income_statement(ticker, api_key, period="annual")
income_statement_quarterly = fa.income_statement(ticker, api_key, period="quarter")

# Collect the Cash Flow Statements
cash_flow_statement_annually = fa.cash_flow_statement(ticker, api_key, period="annual")
cash_flow_statement_quarterly = fa.cash_flow_statement(ticker, api_key, period="quarter")

# Show Key Metrics
key_metrics_annually = fa.key_metrics(ticker, api_key, period="annual")
key_metrics_quarterly = fa.key_metrics(ticker, api_key, period="quarter")

# Show a large set of in-depth ratios
financial_ratios_annually = fa.financial_ratios(ticker, api_key, period="annual")
financial_ratios_quarterly = fa.financial_ratios(ticker, api_key, period="quarter")

# Show the growth of the company
growth_annually = fa.financial_statement_growth(ticker, api_key, period="annual")
growth_quarterly = fa.financial_statement_growth(ticker, api_key, period="quarter")

# Download general stock data
stock_data = fa.stock_data(ticker, period="ytd", interval="1d")

# Download detailed stock data
stock_data_detailed = fa.stock_data_detailed(ticker, api_key, begin="2000-01-01", end="2020-01-01")





class Company:
   def __init__(self, symbol):
      self.symbol = symbol
      self.fundamental_indicators = {}
def to_float(val):
    if val == 0:
        return float(0)

    val = str(val).upper()
    
    if '%' in val:
        return round(float(val[:-1]), 4)

    m = {'K': 3, 'M': 6, 'B': 9, 'T': 12}

    for key in m.keys():
        if key in val:
            multiplier = m.get(val[-1])
            return round(float(val[:-1]) * (10 ** multiplier), 4)
    return round(float(val), 4)
def get_statatistics(symbol):
    url = f"https://finance.yahoo.com/quote/{symbol}/key-statistics?p={symbol}"
    import requests
    dataframes = pandas.read_html(requests.get(url, headers={'User-agent': 'Mozilla/5.0'}).text)
    return pandas.concat(dataframes[1:])
def get_data_item(result, dataframe, columns):
    for column_to_find, column_to_name in columns.items():
        try:
            result[column_to_name] = list((dataframe.loc[dataframe[0] == column_to_find].to_dict()[1]).values())[0]
        except Exception as ex:
            result[column_to_name] = 'NA'

def get_last_data_item(result, dataframe, columns):
    data = dataframe.iloc[:, :2]
    data.columns = ["Column", "Last"]

    for column_to_find, column_to_name in columns.items():
        try:
            val = data[data.Column.str.contains(column_to_find, case=False, regex=True)].iloc[0, 1]
            float_val = to_float(val)
            result[column_to_name] = float_val
        except Exception as ex:
            result[column_to_name] = "NA"


import asyncio
import pandas
import yahoo_fin.stock_info as si
async def get_fundamental_indicators_for_company(config, company):
    company.fundmantal_indicators = {}

    # Statistics Valuation
    keys = {
    'Market Cap (intraday) 5': 'MarketCap',
    'Price/Sales (ttm)': 'PS',
    'Trailing P/E': 'PE',
    'PEG Ratio (5 yr expected) 1': 'PEG',
    'Price/Book (mrq)': 'PB'
    }
    data = si.get_stats_valuation(company.symbol)
    get_data_item(company.fundmantal_indicators, data, keys)

    # Income statement and Balance sheet
    data = get_statatistics(company.symbol)

    get_data_item(company.fundmantal_indicators, data,
                {
                    'Profit Margin': 'ProfitMargin',
                    'Operating Margin (ttm)': 'OperMargin',
                    'Current Ratio (mrq)': 'CurrentRatio',
                    'Payout Ratio 4': 'DivPayoutRatio'
                })

    get_last_data_item(company.fundmantal_indicators, data,
            {
                'Return on assets': 'ROA',
                'Return on equity': 'ROE',
                'Total cash per share': 'Cash/Share',
                'Book value per share': 'Book/Share',
                'Total debt/equity': 'Debt/Equity'
            })


config = {}
company = Company('ROKU')
# Note: 
# You might want to create an event loop and run within the loop:
loop = asyncio.get_event_loop()
loop.run_until_complete(get_fundamental_indicators_for_company(config, company))
print(company.fundmantal_indicators)