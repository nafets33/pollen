
# check last loss order, if the loss order is > X amount, then set ticker on a 31 day Buying Hold, set this in QUEEN_KING['symbols_buying_hold'] = []

def revrec___deprecated__v1(acct_info, QUEEN, QUEEN_KING, STORY_bee, active_queen_order_states, 
                                save_queenking=False, fresh_board=False, wave_blocktime=None):

    # base line power allocation per qcp
    revrec__stars_borrow = {}
    symbol_qcp_dict = {}
    board_tickers = []
    ticker_TradingModel = {}
    chess_board__revrec = {}
    revrec__ticker={}
    revrec__stars={}
    chess_board__revrec_borrow={}
    marginPower={}

    # Check for First
    if 'revrec' not in QUEEN.keys():
        st.info("Fresh Queen on the Block")
        ticker_trinity = None
        pass
    else:
        # Handle Weight Adjustments based on Story
        q_revrec = QUEEN.get('revrec')
        q_story = q_revrec.get('storygauge')
        ticker_trinity = dict(zip(q_story['symbol'], q_story['trinity_w_L']))


    # WORKERBEE: Add validation only 1 symbol per qcp --- QUEEN not needed only need ORDERS and QUEEN_KING
    if not acct_info:
        acct_info = {'accrued_fees': 0.0,
                    'buying_power': 100000,
                    'cash': 0,
                    'daytrade_count': 0,
                    'last_equity': 100000,
                    'portfolio_value': 100000,}
    if not wave_blocktime:
        current_wave = star_ticker_WaveAnalysis(STORY_bee=STORY_bee, ticker_time_frame="SPY_1Minute_1Day").get('current_wave')
        wave_blocktime = current_wave.get('wave_blocktime')

    rr_starttime = datetime.now()
    def shape_revrec_chesspieces(dic_items, acct_info, chess_board__revrec_borrow, marginPower):
        df_borrow = pd.DataFrame(chess_board__revrec_borrow.items())
        df_borrow = df_borrow.rename(columns={0: 'qcp', 1: 'buying_power_borrow'})
        bpb = sum(df_borrow['buying_power_borrow'])
        df_borrow['borrow_budget'] = (df_borrow['buying_power_borrow'] * acct_info.get('buying_power')) / bpb
        
        df = pd.DataFrame(dic_items.items())
        df = df.rename(columns={0: 'qcp', 1: 'buying_power'})
        bp = sum(df['buying_power'])
        
        df['total_budget'] = (df['buying_power'] * acct_info.get('last_equity')) / bp
        df['equity_budget'] = (df['buying_power'] * acct_info.get('last_equity')) / bp
        df['cash_budget'] = (df['buying_power'] * acct_info.get('cash')) / bp
        
        df = pd.merge(df, df_borrow, how='left', on='qcp')

        df = df.set_index('qcp', drop=False)

        df['margin_power'] = df.index.map(marginPower)
        
        return df

    def shape_revrec_tickers(dic_items, symbol_qcp_dict, df_qcp):
        df = pd.DataFrame(dic_items.items())
        df = df.rename(columns={0: 'qcp_ticker', 1: 'ticker_buying_power'})
        df = df.set_index('qcp_ticker', drop=False)
        df['qcp'] = df['qcp_ticker'].map(symbol_qcp_dict)
        df['margin_power'] = df['qcp'].map(dict(zip(df_qcp['qcp'], df_qcp['margin_power'])))
        
        return df

    def shape_revrec_stars(dic_items, revrec__stars_borrow, symbol_qcp_dict, df_qcp):
        df = pd.DataFrame(dic_items.items())
        df_main = df.rename(columns={0: 'qcp_ticker_star', 1: 'star_buying_power'})

        df = pd.DataFrame(revrec__stars_borrow.items())
        df = df.rename(columns={0: 'qcp_ticker_star', 1: 'star_borrow_buying_power'})

        df_main = df_main.merge(df, how='left', on='qcp_ticker_star')
        df_main = df_main.set_index('qcp_ticker_star', drop=False)
        
        df_main['ticker_time_frame'] = df_main.index
        df_main['ticker'] = df_main['ticker_time_frame'].apply(lambda x: x.split("_")[0])
        df_main['star'] = df_main['ticker_time_frame'].apply(lambda x: return_star_from_ttf(x))
        
        df_main['qcp'] = df_main['ticker'].map(symbol_qcp_dict)

        df_main['margin_power'] = df_main['qcp'].map(dict(zip(df_qcp['qcp'], df_qcp['margin_power'])))

        return df_main

    def return_trading_model(QUEEN_KING, qcp, ticker):
        trading_model = QUEEN_KING['king_controls_queen']['symbols_stars_TradingModel'].get(ticker)
        # Handle missing TM
        if trading_model is None: 
            print(ticker, ' tradingmodel missing handling in revrec to default')
            QUEEN_KING['king_controls_queen']['symbols_stars_TradingModel'].update(generate_TradingModel(ticker=ticker, theme=QUEEN_KING['chess_board'][qcp].get('theme'))["MACD"])
            trading_model = QUEEN_KING['king_controls_queen']['symbols_stars_TradingModel'].get(ticker)

        return trading_model
    
    def calculate_weights(data):
        # Calculate the sum of absolute values for normalization
        total = sum(abs(value) for value in data.values())
        
        # Function to apply the weight rules
        def apply_rules(value):
            if value < 0 and value > -.1:
                return 0.05
            elif value < -.1 and value > -.3:
                return .06
            elif value < -.3 and value > -.5:
                return .08
            elif value < -.5 and value >-.6:
                return .1
            elif value < -.6:
                return .01
            else:
                weight = abs(value) / total
                if 0.75 <= value <= 0.89:
                    weight *= 0.75
                elif value > 0.89:
                    weight *= 0.20
                return weight
        
        # Apply rules to each value and create a new dictionary with raw weights
        raw_weights = {key: apply_rules(value) for key, value in data.items()}
        
        # Calculate total weight and adjust weights to ensure they sum to 1
        total_weight = sum(raw_weights.values())
        if total_weight > 0:
            # Adjust weights to ensure they sum to 1
            adjusted_weights = {key: weight / total_weight for key, weight in raw_weights.items()}
        else:
            # Handle case where all weights are zero to avoid division by zero
            adjusted_weights = {key: 1 / len(data) for key in raw_weights}
        
        return adjusted_weights
    
    
    try:
        if fresh_board:
            marginPower={}
            chess_board__revrec_borrow={}
            chess_board__revrec={}
            revrec__ticker={}
            revrec__stars={}
    
        all_workers = list(QUEEN_KING['chess_board'].keys())

        # Handle Weight change
        for qcp in all_workers:
            if QUEEN_KING['chess_board'][qcp].get('buying_power') == 0:
                continue
            
            # Refresh ChessBoard and RevRec
            qcp_power = float(QUEEN_KING['chess_board'][qcp]['total_buyng_power_allocation'])
            qcp_borrow = float(QUEEN_KING['chess_board'][qcp]['total_borrow_power_allocation'])
            qcp_marginpower = float(QUEEN_KING['chess_board'][qcp]['margin_power'])
            chess_board__revrec[qcp] = qcp_power
            chess_board__revrec_borrow[qcp] = qcp_borrow
            marginPower[qcp] = qcp_marginpower
            
            qcp_tickers = QUEEN_KING['chess_board'][qcp].get('tickers')
            board_tickers = board_tickers + qcp_tickers

            num_tickers = len(qcp_tickers)
            if num_tickers == 0:
                print("No Tickers in Chess Piece")
                continue
            
            # CONFIRM TRADING MODEL Ticker Budget Allocation
            ticker_mapping = QUEEN_KING['king_controls_queen'].get('ticker_revrec_allocation_mapping')
            ticker_mapping = ticker_mapping if ticker_mapping else {}
            if ticker_trinity:
                # reallocate weights create a dictionary of ticker and triniity then create a weightet pct
                ticker__trinity = {k:v for (k,v) in ticker_trinity.items() if k in qcp_tickers}
                ticker_mapping = calculate_weights(ticker__trinity)

            for ticker in qcp_tickers:
                symbol_qcp_dict[ticker] = qcp              
                
                trading_model= return_trading_model(QUEEN_KING, qcp, ticker)
                tm_keys = trading_model['stars_kings_order_rules'].keys()
                ticker_TradingModel[ticker] = trading_model

                ## Ticker Allocation Budget
                if num_tickers == 1:
                    revrec__ticker[ticker] = qcp_power
                else:
                    if ticker in ticker_mapping.keys():
                        revrec__ticker[ticker] = ticker_mapping[ticker]
                    else:
                        revrec__ticker[ticker] = qcp_power / num_tickers ## equal number disribution

                # Star Allocation Budget
                for star in tm_keys:
                    revrec__stars[f'{ticker}_{star}'] = trading_model['stars_kings_order_rules'][star].get("buyingpower_allocation_LongTerm")
                    revrec__stars_borrow[f'{ticker}_{star}'] = trading_model['stars_kings_order_rules'][star].get("buyingpower_allocation_ShortTerm")

        # Refresh RevRec Total Budgets
        df_qcp = shape_revrec_chesspieces(chess_board__revrec, acct_info, chess_board__revrec_borrow, marginPower)
        df_ticker = shape_revrec_tickers(revrec__ticker, symbol_qcp_dict, df_qcp)
        df_stars = shape_revrec_stars(revrec__stars, revrec__stars_borrow, symbol_qcp_dict, df_qcp)
        df_stars = df_stars.fillna(0) # tickers without budget move this to upstream in code and fillna only total budget column
        
        # Validate Budget Allocations
        for qcp in df_qcp.index:
            tickers_ = df_ticker[df_ticker['qcp'] == qcp]
            if len(tickers_)>0:
                qcp_bp = float(df_qcp.at[qcp, 'buying_power'])
                qcp_tb = float(df_qcp.at[qcp, 'total_budget'])
                deltaa = sum(tickers_['ticker_buying_power']) - qcp_bp
                if abs(deltaa) > 1:
                    msg=(f'{qcp} out of balance by {deltaa} ${round(deltaa * qcp_tb)} Allocation At Risk')
                    st.write(msg)
                    print(msg)

        df_active_orders = pd.DataFrame()
        # print("WORKERS")
        for qcp in all_workers:
            
            piece = QUEEN_KING['chess_board'].get(qcp)
            tickers = list(set(piece.get('tickers')))
            
            for ticker in tickers:
                # TICKER
                df_temp = df_ticker[df_ticker.index.isin(tickers)].copy()
                bp = sum(df_temp['ticker_buying_power'])
                df_temp['total_budget'] = (df_temp['ticker_buying_power'] * df_qcp.at[qcp, 'total_budget']) / bp
                df_temp['equity_budget'] = (df_temp['ticker_buying_power'] * df_qcp.at[qcp, 'equity_budget']) / bp
                df_temp['borrow_budget'] = ((df_temp['ticker_buying_power'] * df_qcp.at[qcp, 'borrow_budget']) / bp) * df_qcp.at[qcp, 'margin_power']
                # budget_remaining, borrowed_budget_remaining = return_ticker_remaining_budgets(cost_basis_current, ticker, df_temp)

                # UPDTAE TICKER
                df_ticker.at[ticker, 'ticker_total_budget'] = df_temp.at[ticker, 'total_budget']
                df_ticker.at[ticker, 'ticker_equity_budget'] = df_temp.at[ticker, 'equity_budget']
                df_ticker.at[ticker, 'ticker_borrow_budget'] = df_temp.at[ticker, 'borrow_budget']
                # df_ticker.at[ticker, 'ticker_remaining_borrow'] = borrowed_budget_remaining

                # UPDATE star time 
                df_temp = df_stars[(df_stars['ticker'].isin([ticker]))].copy()
                bp = sum(df_temp['star_buying_power'])
                bp_borrow = sum(df_temp['star_borrow_buying_power'])
                df_temp['total_budget'] = (df_temp['star_buying_power'] * df_ticker.loc[ticker].get('ticker_total_budget')) / bp
                df_temp['equity_budget'] = (df_temp['star_buying_power'] * df_ticker.loc[ticker].get('ticker_equity_budget')) / bp
                df_temp['borrow_budget'] = (df_temp['star_borrow_buying_power'] * df_ticker.loc[ticker].get('ticker_borrow_budget')) / bp_borrow
                
                current_from_open = 0
                current_from_yesterday = 0
                ticker_remaining_budget = 0
                ticker_remaining_borrow = 0
                ttf_storybeekeys=STORY_bee.keys()
                for star in df_temp['star'].to_list():
                    ticker_time_frame = f'{ticker}_{star}'
                    if '1Minute_1Day' in ticker_time_frame and ticker_time_frame in ttf_storybeekeys:
                        current_from_open = STORY_bee[ticker_time_frame]["story"].get("current_from_open")
                        current_from_yesterday = STORY_bee[ticker_time_frame]["story"].get("current_from_yesterday")
                        df_ticker.at[ticker, 'current_from_open'] = current_from_open
                        df_ticker.at[ticker, 'current_from_yesterday'] = current_from_yesterday
                    
                    df_stars.at[f'{ticker}_{star}', 'star_total_budget'] = df_temp.loc[f'{ticker}_{star}'].get('total_budget')
                    df_stars.at[f'{ticker}_{star}', 'star_equity_budget'] = df_temp.loc[f'{ticker}_{star}'].get('equity_budget')
                    df_stars.at[f'{ticker}_{star}', 'star_borrow_budget'] = df_temp.loc[f'{ticker}_{star}'].get('borrow_budget')
                    star_total_budget = df_stars.at[ticker_time_frame, 'star_total_budget']
                    star_borrow_budget = df_stars.at[ticker_time_frame, 'star_borrow_budget']
                    active_orders, ttf_remaining_budget, remaining_budget_borrow, budget_cost_basis, borrowed_cost_basis, buys_at_play, sells_at_play = return_ttf_remaining_budget(QUEEN=QUEEN, 
                                                                        total_budget=star_total_budget,
                                                                        borrow_budget=star_borrow_budget,
                                                                        ticker_time_frame=ticker_time_frame, 
                                                                        active_queen_order_states=active_queen_order_states)

                    df_stars.at[ticker_time_frame, 'remaining_budget'] = ttf_remaining_budget
                    df_stars.at[ticker_time_frame, 'remaining_budget_borrow'] = remaining_budget_borrow
                    df_stars.at[ticker_time_frame, 'star_at_play'] = budget_cost_basis
                    df_stars.at[ticker_time_frame, 'star_at_play_borrow'] = borrowed_cost_basis
                    df_stars.at[ticker_time_frame, 'star_buys_at_play'] = buys_at_play
                    df_stars.at[ticker_time_frame, 'star_sells_at_play'] = sells_at_play
                    # df_stars.at[ticker_time_frame, 'sell_reccomendation'] =
                    if len(active_orders) > 0: 
                        df_stars.at[ticker_time_frame, 'money'] = sum(active_orders['money'])
                        df_stars.at[ticker_time_frame, 'honey'] = sum(active_orders['honey'])
                        df_active_orders = pd.concat([df_active_orders, active_orders])
                        active_orders_close_today = active_orders[active_orders['side'] == 'buy']
                        if len(active_orders_close_today) > 0:
                            active_orders_close_today = active_orders_close_today[(active_orders_close_today['order_rules'].apply(lambda x: x.get('close_order_today') == True))]
                            active_orders_close_today['long_short'] = np.where(active_orders_close_today['trigname'].str.contains('buy'), 'long', 'short') 
                            buy_orders = active_orders_close_today[active_orders_close_today['long_short'] == 'long']
                            buys_at_play_close_today = sum(buy_orders["cost_basis_current"]) if len(buy_orders) > 0 else 0
                            df_stars.at[ticker_time_frame, 'star_buys_at_play_allocation'] = buys_at_play - buys_at_play_close_today
                        else:
                            df_stars.at[ticker_time_frame, 'star_buys_at_play_allocation'] = buys_at_play
                    else:
                        df_stars.at[ticker_time_frame, 'money'] = 0
                        df_stars.at[ticker_time_frame, 'honey'] = 0
                        df_stars.at[ticker_time_frame, 'star_buys_at_play_allocation'] = buys_at_play
                    
                    ticker_remaining_budget += ttf_remaining_budget
                    ticker_remaining_borrow += remaining_budget_borrow
                
                df_ticker.at[ticker, 'ticker_remaining_budget'] = ticker_remaining_budget
                df_ticker.at[ticker, 'ticker_remaining_borrow'] = ticker_remaining_borrow

        # print("ORDERS")
        if len(df_active_orders) > 0:
            df_active_orders['qty_available'] = pd.to_numeric(df_active_orders['qty_available'], errors='coerce')
            symbols_qty_avail = df_active_orders.groupby("symbol")[['qty_available']].sum().reset_index().set_index('symbol', drop=False)
        else:
            symbols_qty_avail = pd.DataFrame()
        # cost basis at play
        ticker_buys_at_play_dict = df_stars.groupby("ticker")[['star_buys_at_play']].sum().reset_index().set_index('ticker', drop=False)
        ticker_sells_at_play_dict = df_stars.groupby("ticker")[['star_sells_at_play']].sum().reset_index().set_index('ticker', drop=False)

        # order money/honey
        tickers_money = df_stars.groupby("ticker")[['money']].sum().reset_index().set_index('ticker', drop=False)
        tickers_honey = df_stars.groupby("ticker")[['honey']].sum().reset_index().set_index('ticker', drop=False)

        # Wave Analysis 3 triforce view
        # print("WAVES")
        symbols=board_tickers
        symbols = [i for i in symbols if df_ticker.loc[i].get('ticker_buying_power') > 0]

        WAVE_ANALYSIS = ReadPickleData(QUEEN['dbs'].get('PB_Wave_Analysis_Pickle'))

        if 'STORY_bee_wave_analysis' not in WAVE_ANALYSIS.keys():
            print("INIT Board")
            fresh_board = True
        else:
            missing_symbols = [i for i in symbols if i not in WAVE_ANALYSIS['STORY_bee_wave_analysis']['df_storyguage']['symbol'].tolist()]
            if missing_symbols:
                print("MISSING symbols Refresh Wave Analysis: ", missing_symbols)
                fresh_board = True
            if (datetime.now(est) - WAVE_ANALYSIS['fresh_board_timer']).total_seconds() > 60:
                print("Wave Analysis Refresh Timer")
                fresh_board = True
    
        if fresh_board:
            print("Fresh Board on Wave Analysis")
            resp = wave_analysis__storybee_model(QUEEN_KING, STORY_bee, symbols)
            WAVE_ANALYSIS = {'fresh_board_timer': datetime.now(est), 'STORY_bee_wave_analysis': resp}
            save_queenking = True
        else:
            # print("using Cached Wave Analysis")
            resp = WAVE_ANALYSIS['STORY_bee_wave_analysis']

        storygauge = resp.get('df_storyguage') # wave_gauge
        storygauge = storygauge.set_index('symbol', drop=False)
        waveview = resp.get('df_waveview') # up
        # print(waveview.columns)
        df_storyview = resp.get('df_storyview')
        wave_analysis_down = resp.get('df_storyview_down') # down

        # # filter out story fails
        # waveview['macd_state'] = waveview['macd_state'].fillna('WHO')
        # waveview = waveview[~(waveview['macd_state']=='WHO')]

        # for every star ad the stars column to storygauge i.e. trading grid, ... put the kors
        # CURRENLT UNABLE TO HANDLE TICKER IF NOT IN DB : ) WORKERBEE: handle tickers not returned from wave analysis

        star_longs = dict(zip(df_stars.index, df_stars['star_buys_at_play']))
        star_short = dict(zip(df_stars.index, df_stars['star_sells_at_play']))
        star_money = dict(zip(df_stars.index, df_stars['money']))

        waveview['star_buys_at_play'] = waveview.index.map(star_longs)
        waveview['star_sells_at_play'] = waveview.index.map(star_short)
        waveview['star_money'] = waveview.index.map(star_money)
        
        df_broker_portfolio = pd.DataFrame([v for i, v in QUEEN['portfolio'].items()])
        df_broker_portfolio = df_broker_portfolio.set_index('symbol', drop=False)

        # if len(storygauge) > 0: # should be able to remove this now WORKERBEE
        for symbol in storygauge.index:
            # STORYBEE
            storygauge.at[symbol, 'current_from_open'] = STORY_bee[f'{symbol}_1Minute_1Day']['story'].get('current_from_open')
            
            if symbol in df_ticker.index:
                storygauge.at[symbol, 'ticker_buying_power'] = df_ticker.at[symbol, 'ticker_buying_power']
            else:
                storygauge.at[symbol, 'ticker_buying_power'] = 0
            
            if symbol in ticker_buys_at_play_dict.index:
                storygauge.at[symbol, 'long_at_play'] = ticker_buys_at_play_dict.at[symbol, 'star_buys_at_play']
            else:
                storygauge.at[symbol, 'long_at_play'] = 0
            if symbol in ticker_sells_at_play_dict.index:
                storygauge.at[symbol, 'short_at_play'] = ticker_sells_at_play_dict.at[symbol, 'star_sells_at_play']
            else:
                storygauge.at[symbol, 'short_at_play'] = 0

            ### Broker DELTA ###
            if symbol in symbols_qty_avail.index:
                storygauge.at[symbol, 'qty_available'] = float(symbols_qty_avail.at[symbol, 'qty_available'])
            else:
                storygauge.at[symbol, 'qty_available'] = 0
            if symbol in df_broker_portfolio.index:
                storygauge.at[symbol, 'broker_qty_available'] = float(df_broker_portfolio.at[symbol, 'qty_available'])
            else:
                storygauge.at[symbol, 'broker_qty_available'] = 0

        storygauge['broker_qty_delta'] = storygauge['qty_available'] - storygauge['broker_qty_available']           
        
        QUEEN['heartbeat']['broker_qty_delta'] = sum(storygauge['broker_qty_delta'])
        
        def revrec_allocation(waveview, df_storyview, wave_analysis_down, wave_blocktime):
            """ WORK ON
            # handle star allocation, conflicts your sellhomes are cancel out the flying
            """
            try:

                """Weights of 3 sets (profit/len, tier_gain, tier_start) to the final allocation table"""


                # Global
                tier_max = 8
                tier_max_universe = tier_max * 2 # 16
                alloc_powerlen_base_weight = .23 #????

                # Weight Tiers of Time and Profit
                allloc_time_weight = 2
                alloc_powerlen_weight = 1
                alloc_currentprofit_weight = 4
                alloc_maxprofit_shot_weight = 1
                revrec_weight_sum = allloc_time_weight + alloc_powerlen_weight + alloc_currentprofit_weight + alloc_maxprofit_shot_weight

                # Weight Tiers of Tier Gain
                macd_weight = 3
                vwap_weight = 2
                rsi_weight = 3
                wavestat_weight_sum = macd_weight + vwap_weight + rsi_weight

                # Weight Tiers of Start Tier
                macd_start_weight = 3
                vwap_start_weight = 2
                rsi_start_weight = 3
                wavestat_start_weight_sum = macd_start_weight + vwap_start_weight + rsi_start_weight

                alloc_trinity_of__len_and_profit = 1
                wave_tiers_allocation = 1
                wave_tier_start = 1
            

                waveview['wave_blocktime'] = wave_blocktime
                waveview['wave_state'] = waveview['macd_state'].str.split("-").str[-1]

                # waveview['star'] = waveview.index
                waveview['symbol'] = waveview['ticker_time_frame'].apply(lambda x: return_symbol_from_ttf(x))
                waveview['bs_position'] = waveview['macd_state'].apply(lambda x: x.split("_")[0])

                waveview_buy = waveview[waveview['macd_state'].str.contains('buy')]
                waveview_sell = waveview[waveview['macd_state'].str.contains('sell')]
                
                """ STORY VIEW Star STATS """
                # Story Buy Waves
                df_storyview['star'] = df_storyview.index
                wave_up_star_stats = df_storyview[['star', 'star_avg_time_to_max_profit']].drop_duplicates().reset_index(drop=True).set_index('star')
                wave_analysis_length = df_storyview[['star', 'star_avg_length']].drop_duplicates().reset_index(drop=True).set_index('star')

                # Story Sell Waves
                wave_analysis_down['star'] = wave_analysis_down.index
                wave_analysis_sell = wave_analysis_down[['star', 'star_avg_time_to_max_profit']].drop_duplicates().reset_index(drop=True).set_index('star')
                wave_analysis_length_sell = wave_analysis_down[['star', 'star_avg_length']].drop_duplicates().reset_index(drop=True).set_index('star')

                for ttf in waveview.index.to_list():

                    waveview.at[ttf, 'star_time'] = df_stars.at[ttf, 'star']
                    waveview.at[ttf, 'star_total_budget'] = df_stars.at[ttf, 'star_total_budget']
                    waveview.at[ttf, 'star_borrow_budget'] = df_stars.at[ttf, 'star_borrow_budget']
                    waveview.at[ttf, 'remaining_budget'] = df_stars.at[ttf, 'remaining_budget']
                    waveview.at[ttf, 'remaining_budget_borrow'] = df_stars.at[ttf, 'remaining_budget_borrow']
                    waveview.at[ttf, 'star_at_play'] = df_stars.at[ttf, 'star_at_play']
                    waveview.at[ttf, 'star_at_play_borrow'] = df_stars.at[ttf, 'star_at_play_borrow']
                    waveview.at[ttf, 'star_time'] = df_stars.at[ttf, 'star']
                    waveview.at[ttf, 'long_at_play'] = df_stars.at[ttf, 'star_buys_at_play']
                    waveview.at[ttf, 'short_at_play'] = df_stars.at[ttf, 'star_sells_at_play']
                    waveview.at[ttf, 'star_buys_at_play_allocation'] = df_stars.at[ttf, 'star_buys_at_play_allocation']
                    waveview.at[ttf, 'margin_power'] = df_stars.at[ttf, 'margin_power']
                
                wave_stars_default_time_max_profit  = {
                                                "1Minute_1Day": 1,
                                                "5Minute_5Day": 5,
                                                "30Minute_1Month": 18,
                                                "1Hour_3Month": 48,
                                                "2Hour_6Month": 72,
                                                "1Day_1Year": 250,
                                            }
                wave_stars_default_length  = {
                                                "1Minute_1Day": 1,
                                                "5Minute_5Day": 5,
                                                "30Minute_1Month": 18,
                                                "1Hour_3Month": 48,
                                                "2Hour_6Month": 72,
                                                "1Day_1Year": 250,
                                            }

                for ttf in waveview_buy.index:
                    tic, stime, sframe = ttf.split("_")
                    star_avg_mx_profit = wave_up_star_stats.loc[ttf].get('star_avg_time_to_max_profit') if ttf in wave_up_star_stats else wave_stars_default_time_max_profit.get(f'{stime}_{sframe}')
                    star_avg_length = wave_analysis_length.loc[ttf].get('star_avg_length') if ttf in wave_analysis_length else wave_stars_default_length.get(f'{stime}_{sframe}')

                    waveview.at[ttf, 'star_avg_time_to_max_profit'] = star_avg_mx_profit
                    waveview.at[ttf, 'star_avg_length'] = star_avg_length

                for ttf in waveview_sell.index:
                    tic, stime, sframe = ttf.split("_")
                    star_avg_mx_profit = wave_analysis_sell.loc[ttf].get('star_avg_time_to_max_profit') if ttf in wave_analysis_sell else wave_stars_default_time_max_profit.get(f'{stime}_{sframe}')
                    star_avg_length = wave_analysis_length_sell.loc[ttf].get('star_avg_length') if ttf in wave_analysis_length_sell else wave_stars_default_length.get(f'{stime}_{sframe}')

                    waveview.at[ttf, 'star_avg_time_to_max_profit'] = star_avg_mx_profit
                    waveview.at[ttf, 'star_avg_length'] = star_avg_length

                waveview['star'] = waveview['star_time']
                waveview_map = return_trading_model_mapping(QUEEN_KING, waveview)
                waveview['king_order_rules'] = waveview['ticker_time_frame'].map(waveview_map)

                """ CALCULATOR """


                ## base calc variables ##
                # power on current deviation
                waveview['tmp_deivation'] = waveview['time_to_max_profit'] - waveview['star_avg_time_to_max_profit']
                waveview['starmark_len_deivation'] = waveview['length'] / waveview['star_avg_time_to_max_profit']
                # where we are you, tmp - len deviation
                waveview['tmp_length_deivation'] = waveview['time_to_max_profit'] - waveview['length']
                # len - star deviation
                waveview['len__starmark_tmp_deviation'] = waveview['length'] - waveview['star_avg_time_to_max_profit']

                waveview['tmp_deivation_multiplier'] = waveview['tmp_deivation'] / waveview['star_avg_time_to_max_profit']
                waveview['current_tmp_len_multiplier'] = waveview['tmp_length_deivation'] / waveview['star_avg_time_to_max_profit']
                waveview['lev_vs_starmark_tmp_multiplier'] = np.where(waveview['len__starmark_tmp_deviation']>=0, 0, waveview['len__starmark_tmp_deviation'] / waveview['star_avg_time_to_max_profit'])

                waveview['tmp_power'] = waveview['star_total_budget'] * waveview['tmp_deivation_multiplier'] # 
                waveview['tmp_power_len'] = waveview['star_total_budget'] * waveview['current_tmp_len_multiplier'] # 

                # waveview['allocation_power_powerlen'] = np.where((abs(waveview['tmp_power']) - abs(waveview['tmp_power_len'])) < 1, alloc_powerlen_base_weight * waveview['star_total_budget'], waveview['tmp_power'] - waveview['tmp_power_len'])

                """ # TIME to Max Profit Delta from Current Length """
                waveview['alloc_powerlen'] = np.where(waveview['time_to_max_profit'] == 0, 
                                                      -1, 
                                                      ((1- (waveview['length'] - waveview['time_to_max_profit']) / waveview['length']) * -1))
                waveview['alloc_powerlen'] = np.where((waveview['alloc_powerlen'] == -1) & (waveview['length']>1), -.5, waveview['alloc_powerlen']) # check if no mxprofit and length past 1, lose budget

                # OJ allocation time # Allow for Reverse budget outcome
                waveview['allocation'] = waveview['star_total_budget'] * waveview['lev_vs_starmark_tmp_multiplier'] # 
                waveview['allocation_borrow'] = waveview['star_borrow_budget'] * waveview['lev_vs_starmark_tmp_multiplier'] # 

                """# Allocation Profit Deviation # current profit deviation"""
                waveview['current_profit_deviation'] = np.where(
                    (waveview['current_profit'] == waveview['maxprofit']) | 
                    (waveview['current_profit'] == 0) & (waveview['maxprofit'] == 0), 
                    -1, -1 - (waveview['current_profit'] - waveview['maxprofit']) / waveview['maxprofit']
                    )
                waveview['current_profit_deviation'] = np.where(waveview['current_profit']< 0, 0, waveview['current_profit_deviation'] )
                waveview['current_profit_deviation_pct'] = np.where(waveview['current_profit_deviation']== 0, 0, waveview['current_profit_deviation'] )
                waveview['current_profit_deviation_pct'] = np.where(waveview['current_profit_deviation']== -1, -1, waveview['current_profit_deviation'] )

                waveview['maxprofit_shot'] = waveview.index.map(dict(zip(df_storyview.index, df_storyview['ttf_median_maxprofit_median']))) # join from wave analysis
                waveview['maxprofit_shot_weight'] = (waveview['maxprofit'] / waveview['maxprofit_shot'])
                waveview['maxprofit_shot_weight_score'] = np.where(waveview['maxprofit_shot_weight'] == 0, -1, (waveview['maxprofit_shot_weight'] *-1))# np.where(waveview['tmp_mark_deivation'] < 0, waveview['tmp_mark_deivation'] * waveview['remaining_budget'], 0)
                waveview['maxprofit_shot_weight_score'] = np.where(waveview['maxprofit_shot_weight'] >= 1, 0, (waveview['maxprofit_shot_weight_score']))# np.where(waveview['tmp_mark_deivation'] < 0, waveview['tmp_mark_deivation'] * waveview['remaining_budget'], 0)
                # waveview['maxprofit_deviation__shotweight__score'] = ((waveview['current_profit_deviation']) + (waveview['maxprofit_shot_weight_score']) ) / 2

                # Top Level Allocations on Budget - Time, profit deviation, maxprofit shot
                waveview['alloc_time'] = ((waveview['star_total_budget'] * waveview['lev_vs_starmark_tmp_multiplier'])/waveview['star_total_budget']) * allloc_time_weight * (waveview['star_total_budget'] * waveview['lev_vs_starmark_tmp_multiplier'])/revrec_weight_sum
                waveview['alloc_ttmp_length'] = ((waveview['star_total_budget'] * waveview['alloc_powerlen'])/waveview['star_total_budget']) * alloc_powerlen_weight * (waveview['star_total_budget'] * waveview['alloc_powerlen'])/revrec_weight_sum
                waveview['alloc_currentprofit'] = ((waveview['star_total_budget'] * waveview['current_profit_deviation_pct'])/waveview['star_total_budget']) * alloc_currentprofit_weight * (waveview['star_total_budget'] * waveview['current_profit_deviation_pct'])/revrec_weight_sum
                waveview['alloc_maxprofit_shot'] = ((waveview['star_total_budget'] * waveview['maxprofit_shot_weight_score'])/waveview['star_total_budget']) * alloc_maxprofit_shot_weight * (waveview['star_total_budget'] * waveview['maxprofit_shot_weight_score'])/revrec_weight_sum
                waveview['total_allocation_budget'] = waveview['alloc_time'] + waveview['alloc_ttmp_length'] + waveview['alloc_currentprofit'] + waveview['alloc_maxprofit_shot']

                # -Tiers
                # # tier divergence, how many tiers have been gain'd / lost MACD/RSI/VWAP // current profit deviation
                weight_tier_team = ['macd', 'vwap', 'rsi_ema']
                for wave_tier in weight_tier_team:
                    waveview[f'{wave_tier}_tier_gain'] = waveview[f'end_tier_{wave_tier}'] - waveview[f'start_tier_{wave_tier}'] 
                    # ###3 tier,
                    waveview[f'{wave_tier}_max_growth'] = (tier_max + 1) - waveview[f'start_tier_{wave_tier}'] # max growth need 9 
                    waveview[f'{wave_tier}_tier_gain_weight'] = 1 - (waveview[f'{wave_tier}_tier_gain'] / waveview[f'{wave_tier}_max_growth'])
                    waveview[f'{wave_tier}_tier_gain_pct'] = np.where(waveview[f'{wave_tier}_tier_gain'] < 0, np.minimum(waveview[f'{wave_tier}_tier_gain_weight'], 1), waveview[f'{wave_tier}_tier_gain_weight'] * -1)
                    if wave_tier == 'macd':
                        weight_score = macd_start_weight
                    elif wave_tier == 'vwap':
                        weight_score = vwap_start_weight
                    else: # RSI
                        weight_score = rsi_start_weight
                    
                    waveview[f'alloc_{wave_tier}_tier'] = ((waveview['star_total_budget'] * waveview[f'{wave_tier}_tier_gain_pct'])/waveview['star_total_budget']) * weight_score * (waveview['star_total_budget'] * waveview[f'{wave_tier}_tier_gain_pct'])/wavestat_start_weight_sum

                waveview['tier_gain_movement'] = waveview[[f'alloc_{wt}_tier' for wt in weight_tier_team]].sum(axis=1)
                # total_allocation_budget
                waveview['total_allocation_budget_single'] = waveview['total_allocation_budget'].copy()
                waveview['total_allocation_budget'] = (waveview['total_allocation_budget'] + waveview['tier_gain_movement']) / 2

                waveview['pct_budget_allocation'] = waveview['total_allocation_budget'] / waveview['star_total_budget']
                waveview['total_allocation_borrow_budget'] = (waveview['pct_budget_allocation'] * waveview['star_borrow_budget'])

                #Hold the Line Minimum Allocation with Margin
                # Deploy Allocation Number
                waveview['allocation_deploy'] = np.where((waveview['bs_position']=='buy'), 
                                                         waveview['total_allocation_budget'] - waveview['star_buys_at_play_allocation'], 
                                                         waveview['total_allocation_budget'] - waveview['star_sells_at_play']
                                                         )
                waveview['allocation_deploy'] = np.where(waveview['star_total_budget']<=0,0,waveview['allocation_deploy'])

                waveview['allocation_borrow_deploy'] = np.where((waveview['bs_position']=='buy'), 
                                                                (waveview['total_allocation_borrow_budget'] - waveview['star_buys_at_play_allocation']) , 
                                                                (waveview['total_allocation_borrow_budget'] - waveview['star_sells_at_play']) 
                                                                )
                waveview['allocation_borrow_deploy'] = np.where(waveview['star_borrow_budget']<=0,0,waveview['allocation_borrow_deploy'])
                
                waveview['allocation_long'] = np.where((waveview['bs_position']=='buy'), 
                                                       waveview['total_allocation_budget'] - waveview['star_buys_at_play_allocation'], 
                                                       (waveview['star_total_budget'] - waveview['total_allocation_budget'])
                                                       )
                waveview['allocation_borrow_long'] = np.where((waveview['bs_position']=='buy'), 
                                                       waveview['total_allocation_budget'] - waveview['star_buys_at_play_allocation'], 
                                                       (waveview['star_borrow_budget'] - waveview['total_allocation_borrow_budget'])
                                                       )
                # Minimum Allocation // consider when sell, long shold be allocation_long
                waveview['allocation_long_deploy'] = (waveview['allocation_long'] + waveview['allocation_borrow_long'])

            except Exception as e:
                print_line_of_error(e)

            return waveview

        waveview = revrec_allocation(waveview, df_storyview, wave_analysis_down, wave_blocktime)
        
        # print("STORYGAUGE")
        price_info_symbols = QUEEN['price_info_symbols']
        for symbol in storygauge.index:
            token = waveview[waveview['symbol'] == symbol]
            if len(token) > 0:
                storygauge.at[symbol, 'allocation_long'] = sum(token['allocation_long'])
                storygauge.at[symbol, 'allocation_long_deploy'] = sum(token['allocation_long_deploy'])
            if symbol in tickers_money.index:
                storygauge.at[symbol, 'money'] = tickers_money.at[symbol, 'money']
            if symbol in tickers_honey.index:
                storygauge.at[symbol, 'honey'] = tickers_honey.at[symbol, 'honey']
            
            # storybee OR price_info_symbols
            if symbol in price_info_symbols.index:
                storygauge.at[symbol, 'ask'] = price_info_symbols.loc[symbol]['priceinfo'].get('current_ask')
                storygauge.at[symbol, 'bid'] = price_info_symbols.loc[symbol]['priceinfo'].get('current_bid')
                storygauge.at[symbol, 'ask_bid_variance'] = price_info_symbols.loc[symbol]['priceinfo'].get('ask_bid_variance')
                storygauge.at[symbol, 'maker_middle'] = price_info_symbols.loc[symbol]['priceinfo'].get('maker_middle')

            # STORY BEE
            storygauge.at[symbol, 'current_from_open'] = df_ticker.loc[symbol].get('current_from_open')
            storygauge.at[symbol, 'current_from_yesterday'] = df_ticker.loc[symbol].get('current_from_yesterday')
            

        cycle_time = (datetime.now()-rr_starttime).total_seconds()
        if cycle_time > 10:
            msg=("rervec cycle_time > 10 seconds", cycle_time)
            print(msg)
            logging.warning(msg)
        return {'cycle_time': cycle_time, 'df_qcp': df_qcp, 'df_ticker': df_ticker, 'df_stars':df_stars, 
                'df_storyview': df_storyview, 'storygauge': storygauge, 'waveview': waveview, "save_queenking": save_queenking, 'WAVE_ANALYSIS': WAVE_ANALYSIS}
    
    except Exception as e:
        print_line_of_error(f'revrec failed {e}')

