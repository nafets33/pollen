
import pandas as pd
import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import pytz
from itertools import islice
from PIL import Image
from dotenv import load_dotenv
import random

import os
import sqlite3
import time
import aiohttp
import asyncio
# import requests
# from requests.auth import HTTPBasicAuth
from chess_piece.app_hive import return_image_upon_save, symbols_unique_color, cust_graph, custom_graph_ttf_qcp, create_ag_grid_column, download_df_as_CSV, show_waves, send_email, pollenq_button_source, standard_AGgrid, create_AppRequest_package, create_wave_chart_all, create_slope_chart, create_wave_chart_single, create_wave_chart, create_guage_chart, create_main_macd_chart,  queen_order_flow, mark_down_text, mark_down_text, page_line_seperator, local_gif, flying_bee_gif
from chess_piece.king import kingdom__global_vars, return_QUEENs__symbols_data, hive_master_root, streamlit_config_colors, local__filepaths_misc, print_line_of_error, ReadPickleData, PickleData
from chess_piece.queen_hive import return_queenking_board_symbols, sell_button_dict_items, ttf_grid_names_list, buy_button_dict_items, wave_analysis__storybee_model, hive_dates, return_market_hours, init_ticker_stats__from_yahoo, refresh_chess_board__revrec, return_queen_orders__query, add_trading_model, set_chess_pieces_symbols, init_pollen_dbs, init_qcp, wave_gauge, return_STORYbee_trigbees, generate_TradingModel, stars, analyze_waves, story_view, pollen_themes, return_timestamp_string, init_logging

from custom_button import cust_Button
from custom_grid import st_custom_grid, GridOptionsBuilder
from custom_graph_v1 import st_custom_graph

from ozz.ozz_bee import send_ozz_call
# from chat_bot import ozz_bot


# from tqdm import tqdm

import ipdb


pd.options.mode.chained_assignment = None

scriptname = os.path.basename(__file__)
queens_chess_piece = os.path.basename(__file__)

page = 'QueensConscience'


def return_user_symbol_colors(QUEEN_KING, idx_field="symbol", qcp='bishop'):
    qcp_tickers = QUEEN_KING['chess_board'][qcp].get('tickers')
    df = QUEEN_KING['revrec'].get('waveview')
    df = df[df[idx_field].isin(qcp_tickers)]
    df = df[df.index.str.contains("1Minute")]
    
    symbol_dicts = []

    for ttf in df.index:
        symbol = ttf.split("_")[0]
        if 'buy' in df.at[ttf, 'macd_state']:
            color = '#13B107' 
        else:
            color = '#DE0C0C' # 'green'
        
        symbol_dict = {
            "field": symbol,
            "name": f'{symbol}',
            "color": color # unique_colors[i]
        }
        symbol_dicts.append(symbol_dict)
    
    
    
    # # Get unique names from the 'name' column
    # unique_names = df[idx_field].tolist()
    
    # # Generate a list of unique colors for each unique name
    # unique_colors = ['#' + ''.join([random.choice('0123456789ABCDEF') for j in range(6)]) for _ in range(len(unique_names))]
    
    # for i, name in enumerate(unique_names):
    #     # Customize the 'name' and 'color' values as needed
    #     symbol_dict = {
    #         "field": name,
    #         "name": name,
    #         "color": unique_colors[i]
    #     }
    #     symbol_dicts.append(symbol_dict)
    
    return symbol_dicts

def queens_conscience(st, hc, QUEENBEE, KING, QUEEN, QUEEN_KING, api, api_vars):

    # print("here")
    # from random import randint
    main_root = hive_master_root() # os.getcwd()  # hive root
    load_dotenv(os.path.join(main_root, ".env"))
    est = pytz.timezone("US/Eastern")
    utc = pytz.timezone('UTC')
    # ###### GLOBAL # ######
    king_G = kingdom__global_vars()
    active_order_state_list = king_G.get('active_order_state_list') # = ['running', 'running_close', 'submitted', 'error', 'pending', 'completed', 'completed_alpaca', 'running_open', 'archived_bee']
    active_queen_order_states = king_G.get('active_queen_order_states') # = ['submitted', 'accetped', 'pending', 'running', 'running_close', 'running_open']
    # CLOSED_queenorders = king_G.get('CLOSED_queenorders') # = ['running_close', 'completed', 'completed_alpaca']
    RUNNING_Orders = king_G.get('RUNNING_Orders') # = ['running', 'running_open']
    # RUNNING_CLOSE_Orders = king_G.get('RUNNING_CLOSE_Orders') # = ['running_close']
    
    # crypto
    crypto_currency_symbols = ['BTCUSD', 'ETHUSD', 'BTC/USD', 'ETH/USD']
    crypto_symbols__tickers_avail = ['BTCUSD', 'ETHUSD']


    # images
    MISC = local__filepaths_misc()
    flyingbee_grey_gif_path = MISC['flyingbee_grey_gif_path']
    power_gif = MISC['power_gif']
    uparrow_gif = MISC['uparrow_gif']
    learningwalk_bee = MISC['learningwalk_bee']
    runaway_bee_gif = MISC['runaway_bee_gif']

    ##### STREAMLIT ###
    k_colors = streamlit_config_colors()
    default_text_color = k_colors['default_text_color'] # = '#59490A'
    default_font = k_colors['default_font'] # = "sans serif"
    default_yellow_color = k_colors['default_yellow_color'] # = '#C5B743'
    
    with st.spinner("Welcome to the QueensMind"):

        def advanced_charts():
            try:
                # tickers_avail = [list(set(i.split("_")[0] for i in POLLENSTORY.keys()))][0]
                cols = st.columns((1,5,1,1))
                # fullstory_option = st.selectbox('POLLENSTORY', ['no', 'yes'], index=['yes'].index('yes'))
                stars_radio_dict = {'1Min':"1Minute_1Day", '5Min':"5Minute_5Day", '30m':"30Minute_1Month", '1hr':"1Hour_3Month", 
                '2hr':"2Hour_6Month", '1Yr':"1Day_1Year", 'all':"all",}
                with cols[0]:
                    ticker_option = st.selectbox("Tickers", tickers_avail, index=tickers_avail.index(["SPY" if "SPY" in tickers_avail else tickers_avail[0]][0]))
                    ticker = ticker_option
                with cols[1]:
                    option__ = st.radio(
                        label="stars_radio",
                        options=list(stars_radio_dict.keys()),
                        key="signal_radio",
                        label_visibility='visible',
                        # disabled=st.session_state.disabled,
                        horizontal=True,
                    )
                
                with cols[2]:
                    # day_only_option = st.selectbox('Show Today Only', ['no', 'yes'], index=['no'].index('no'))
                    hc.option_bar(option_definition=pq_buttons.get('charts_day_option_data'),title='Show Today Only', key='day_only_option', horizontal_orientation=True) #,override_theme=over_theme,font_styling=font_fmt,horizontal_orientation=True)

                
                if option__ != 'all':
                    ticker_time_frame = f'{ticker}_{stars_radio_dict[option__]}'
                else:
                    ticker_time_frame = f'{ticker}_{"1Minute_1Day"}'

                df = POLLENSTORY[ticker_time_frame].copy()

                charts__view, waves__view, slopes__view = st.tabs(['charts', 'waves', 'slopes'])
                
                with charts__view:
                    try:
    
                        st.markdown('<div style="text-align: center;">{}</div>'.format(ticker_option), unsafe_allow_html=True)

                        if option__.lower() == 'all':
                            min_1 = POLLENSTORY[f'{ticker_option}{"_"}{"1Minute_1Day"}'].copy()
                            min_5 = POLLENSTORY[f'{ticker_option}{"_"}{"5Minute_5Day"}'].copy()
                            min_30m = POLLENSTORY[f'{ticker_option}{"_"}{"30Minute_1Month"}'].copy()
                            _1hr = POLLENSTORY[f'{ticker_option}{"_"}{"1Hour_3Month"}'].copy()
                            _2hr = POLLENSTORY[f'{ticker_option}{"_"}{"2Hour_6Month"}'].copy()
                            _1yr = POLLENSTORY[f'{ticker_option}{"_"}{"1Day_1Year"}'].copy()

                            c1, c2 = st.columns(2)
                            with c1:
                                st.plotly_chart(create_main_macd_chart(min_1))
                            with c2:
                                st.plotly_chart(create_main_macd_chart(min_5))
                            with c1:
                                st.plotly_chart(create_main_macd_chart(min_30m))
                            with c2:
                                st.plotly_chart(create_main_macd_chart(_1hr))
                            with c1:
                                st.plotly_chart(create_main_macd_chart(_2hr))
                            with c2:
                                st.plotly_chart(create_main_macd_chart(_1yr))
                        else:
                            # if day_only_option == 'yes':
                            if st.session_state['day_only_option'] == 'charts_dayonly_yes':
                                df_day = df['timestamp_est'].iloc[-1]
                                df['date'] = df['timestamp_est'] # test

                                df_today = df[df['timestamp_est'] > (datetime.now().replace(hour=1, minute=1, second=1)).astimezone(est)].copy()
                                df_prior = df[~(df['timestamp_est'].isin(df_today['timestamp_est'].to_list()))].copy()

                                df = df_today
                            
                            st.plotly_chart(create_main_macd_chart(df=df, width=1500, height=550))
                    
                    except Exception as e:
                        print(e)
                        print_line_of_error()

                # if slope_option == 'yes':
                with slopes__view:
                    # df = POLLENSTORY[ticker_time_frame].copy()
                    slope_cols = [i for i in df.columns if "slope" in i]
                    slope_cols.append("close")
                    slope_cols.append("timestamp_est")
                    slopes_df = df[['timestamp_est', 'hist_slope-3', 'hist_slope-6', 'macd_slope-3']]
                    fig = create_slope_chart(df=df)
                    st.plotly_chart(fig)
                    st.dataframe(slopes_df)
                    
                # if wave_option == "yes":
                with waves__view:
                    # df = POLLENSTORY[ticker_time_frame].copy()
                    fig = create_wave_chart(df=df)
                    st.plotly_chart(fig)
                    
                    # dft = split_today_vs_prior(df=df)
                    # dft = dft['df_today']
                    fig=create_wave_chart_all(df=df, wave_col='buy_cross-0__wave')
                    st.plotly_chart(fig)

                    st.write("current wave")
                    current_buy_wave = df['buy_cross-0__wave_number'].tolist()
                    current_buy_wave = [int(i) for i in current_buy_wave]
                    current_buy_wave = max(current_buy_wave)
                    st.write("current wave number")
                    st.write(current_buy_wave)
                    dft = df[df['buy_cross-0__wave_number'] == str(current_buy_wave)].copy()
                    st.write({'current wave': [dft.iloc[0][['timestamp_est', 'close', 'macd']].values]})
                    fig=create_wave_chart_single(df=dft, wave_col='buy_cross-0__wave')
                    st.plotly_chart(fig)
            
            
                st.session_state['last_page'] = 'queen'
            
            
            except Exception as e:
                print(e)
                print_line_of_error()
            
            return True


        def chunk(it, size):
            it = iter(it)
            return iter(lambda: tuple(islice(it, size)), ())


        def on_click_ss_value_bool(name):
            st.session_state[name] = True


        def clean_out_app_requests(QUEEN, QUEEN_KING, request_buckets):
            save = False
            for req_bucket in request_buckets:
                if req_bucket not in QUEEN_KING.keys():
                    st.write("Verison Missing DB: ", req_bucket)
                    continue
                for app_req in QUEEN_KING[req_bucket]:
                    if app_req['app_requests_id'] in QUEEN['app_requests__bucket']:
                        # print(f'{app_req["client_order_id"]}__{req_bucket}__QUEEN Processed app Request__{app_req["app_requests_id"]}')
                        # st.info(f'{app_req["client_order_id"]}__{req_bucket}__QUEEN Processed app Request__{app_req["app_requests_id"]}')
                        archive_bucket = f'{req_bucket}{"_requests"}'
                        QUEEN_KING[req_bucket].remove(app_req)
                        QUEEN_KING[archive_bucket].append(app_req)
                        save = True
            if save:
                PickleData(pickle_file=PB_App_Pickle, data_to_store=QUEEN_KING)
            
            return True


        def clear_subconscious_Thought(QUEEN, QUEEN_KING):
            with st.sidebar.expander("clear subconscious thought"):
                with st.form('clear subconscious'):
                    thoughts = QUEEN['subconscious'].keys()
                    clear_thought = st.selectbox('clear subconscious thought', list(thoughts))
                    
                    if st.form_submit_button("Save"):
                        app_req = create_AppRequest_package(request_name='subconscious', archive_bucket='subconscious_requests')
                        app_req['subconscious_thought_to_clear'] = clear_thought
                        app_req['subconscious_thought_new_value'] = []
                        QUEEN_KING['subconscious'].append(app_req)
                        return_image_upon_save(title="subconscious thought cleared")
                        PickleData(pickle_file=PB_App_Pickle, data_to_store=QUEEN_KING)

                        return True


        def trigger_queen_vars(dag, client_username, last_trig_date=datetime.now(est)):
            return {'dag': dag, 'last_trig_date': last_trig_date, 'client_user': client_username}
        
        def chunk_write_dictitems_in_row(chunk_list, max_n=10, write_type='checkbox', title="Active Models", groupby_qcp=False, info_type='buy'):

            try:
                # chunk_list = chunk_list
                num_rr = len(chunk_list) + 1 # + 1 is for chunking so slice ends at last 
                chunk_num = max_n if num_rr > max_n else num_rr
                
                # if num_rr > chunk_num:
                chunks = list(chunk(range(num_rr), chunk_num))
                for i in chunks:
                    if i[0] == 0:
                        slice1 = i[0]
                        slice2 = i[-1] # [0 : 49]
                    else:
                        slice1 = i[0] - 1
                        slice2 = i[-1] # [49 : 87]
                    # print("chunk slice", (slice1, slice2))
                    chunk_n = chunk_list[slice1:slice2]
                    cols = st.columns(len(chunk_n) + 1)
                    with cols[0]:
                        if write_type == 'info':
                            flying_bee_gif(width='53', height='53')
                        else:
                            st.write(title)
                        # bees = [write_flying_bee(width='3') for i in chunk_n]
                    for idx, package in enumerate(chunk_n):
                        for ticker, v in package.items():
                        # ticker, value = package.items()
                            with cols[idx + 1]:
                                if write_type == 'checkbox':
                                    st.checkbox(ticker, v, key=f'{ticker}')  ## add as quick save to turn off and on Model
                                if write_type == 'info':
                                    if info_type == 'buy':
                                        st.info(f'{ticker} {v}')
                                        # local_gif(gif_path=uparrow_gif, height='23', width='23')
                                    else:
                                        st.error(f'{ticker} {v}')
                                    # flying_bee_gif(width='43', height='40')
                                if write_type == 'pl_profits':
                                    st.write(ticker, v)
            except Exception as e:
                print(e, print_line_of_error())

            return True 
        
        
        def add_new_qcp__to_chessboard(cols, QUEEN_KING, qcp_bees_key, ticker_allowed, themes):
            cols = st.columns((1,5,2,2,2,2,2,3,2,2))
            qcp_pieces = QUEEN_KING[qcp_bees_key].keys()
            qcp = st.text_input(label='piece name', value=f'pawn_{len(qcp_pieces)}', help="Theme your names to match your strategy")
            if qcp in qcp_pieces:
                st.error("Chess Piece Name must be Unique")
                st.stop()
            with st.form('new qcp'):
                if st.form_submit_button('Add New Piece'):
                    qcp = setup_qcp_on_board(cols, QUEEN_KING, qcp_bees_key, qcp=None, new_piece=qcp, ticker_allowed=ticker_allowed, themes=themes, headers=0)
                    QUEEN_KING[qcp_bees_key][qcp.get('piece_name')] = qcp
                    PickleData(st.session_state['PB_App_Pickle'], QUEEN_KING)
                    st.success("New Piece Added Refresh")
  
        def setup_qcp_on_board(cols, QUEEN_KING, qcp_bees_key, qcp, ticker_allowed, themes, new_piece=False, headers=0):
            def return_active_image(qcp):
                if 'qcp_k' not in st.session_state:
                    b_key = 89
                    st.session_state['qcp_k'] = 89
                else:
                    b_key = st.session_state['qcp_k'] + 1
                    st.session_state['qcp_k'] = b_key
                if 'qcp_k' in st.session_state and b_key == st.session_state['qcp_k']:
                    b_key+=1
                try:
                    with cols[0]:
                        if qcp == 'castle':
                            cust_Button(local__filepaths_misc().get('castle_png'), key=f'{b_key} castle')

                        else:
                            cust_Button(local__filepaths_misc().get('queen_png'), key=f'{b_key}')
                        #     # hc.option_bar(option_definition=pq_buttons.get('castle_option_data'),title='', key='castle_qcp', horizontal_orientation=False)
                        # elif qcp == 'bishop':
                        #     st.write(qcp)
                        #     # hc.option_bar(option_definition=pq_buttons.get('bishop_option_data'),title='', key='bishop_qcp', horizontal_orientation=False)                                
                        # elif qcp == 'knight':
                        #     st.write(qcp)
                        #     # hc.option_bar(option_definition=pq_buttons.get('knight_option_data'),title='', key='knight_qcp', horizontal_orientation=False)                                
                        # elif qcp == 'castle_coin':
                        #     st.write(qcp)
                        #     # hc.option_bar(option_definition=pq_buttons.get('coin_option_data'),title='', key='coin_qcp', horizontal_orientation=False)                                
                        # else:
                        #     st.write(qcp)
                        #     # st.image(MISC.get('knight_png'), width=74)
                        # cust_Button(os.path.join(hive_master_root(), 'misc/dollar_symbol.gif'), height='38px')

                    return True
                except Exception as e:
                    print(e)
                    print_line_of_error()

            models = ['MACD', 'story__AI']
                       
            try:
                if headers == 0:
                    # Headers
                    c=0
                    chess_board_names = list(QUEEN_KING[qcp_bees_key]['castle'].keys())
                    chess_board_names = ["pq", 'symbols', 'Model', 'Theme', 'BuyP.Alloc', 'BorrowP.Alloc']
                    for qcpvar in chess_board_names:
                        try:
                            with cols[c]:
                                st.write(qcpvar)
                                c+=1
                        except Exception as e:
                            print(qcpvar, e)

                if new_piece:
                    return_active_image(new_piece)
                else:
                    return_active_image(qcp)

                if new_piece:
                    qcp = new_piece
                    if qcp not in QUEEN_KING[qcp_bees_key].keys():
                        qcp_vars = init_qcp(buying_power=0, piece_name=qcp)
                        # QUEEN_KING[qcp_bees_key][qcp] = qcp_vars
                        models = ['MACD']
                        # chess board vars
                        with cols[1]:
                            qcp_vars['tickers'] = st.multiselect(label=qcp, options=ticker_allowed + crypto_symbols__tickers_avail, default=qcp_vars['tickers'], help='Castle Should Hold your Highest Valued Symbols', key=f'{qcp}tickers{admin}')
                        with cols[2]:
                            st.selectbox(label='-', options=models, index=models.index(qcp_vars.get('model')), key=f'{qcp}model{admin}')
                        with cols[3]:
                            qcp_vars['theme'] = st.selectbox(label=f'-', options=themes, index=themes.index(qcp_vars.get('theme')), help='Trading Star Strategy, You May Customize Trading Models', key=f'{qcp}theme{admin}')
                        with cols[4]:
                            qcp_vars['total_buyng_power_allocation'] = st.slider(label=f'-', min_value=float(0.0), max_value=float(1.0), value=float(qcp_vars['total_buyng_power_allocation']), key=f'{qcp}_buying_power_allocation{admin}', label_visibility='hidden')
                        with cols[5]:
                            qcp_vars['total_borrow_power_allocation'] = st.slider(label=f'-', min_value=float(0.0), max_value=float(1.0), value=float(qcp_vars['total_borrow_power_allocation']), key=f'{qcp}_borrow_power_allocation{admin}', label_visibility='hidden')
                            # QUEEN_KING[qcp_bees_key][qcp]['total_borrow_power_allocation'] = 
                    return qcp_vars
                
                else:   
                    # chess board vars
                    with cols[1]:
                        QUEEN_KING[qcp_bees_key][qcp]['tickers'] = st.multiselect(label=qcp, options=ticker_allowed + crypto_symbols__tickers_avail, default=QUEEN_KING[qcp_bees_key][qcp]['tickers'], help='Castle Should Hold your Highest Valued Symbols', key=f'{qcp}tickers{admin}')
                    with cols[2]:
                        QUEEN_KING[qcp_bees_key][qcp]['model'] = st.selectbox(label='-', options=models, index=models.index(QUEEN_KING[qcp_bees_key][qcp].get('model')), key=f'{qcp}model{admin}')
                    with cols[3]:
                        QUEEN_KING[qcp_bees_key][qcp]['theme'] = st.selectbox(label=f'-', options=themes, index=themes.index(QUEEN_KING[qcp_bees_key][qcp].get('theme')), help='Trading Star Strategy, You May Customize Trading Models', key=f'{qcp}theme{admin}')
                    with cols[4]:
                        QUEEN_KING[qcp_bees_key][qcp]['total_buyng_power_allocation'] = st.slider(label=f'-', min_value=float(0.0), max_value=float(1.0), value=float(QUEEN_KING[qcp_bees_key][qcp]['total_buyng_power_allocation']), key=f'{qcp}_buying_power_allocation{admin}', label_visibility='hidden')
                    with cols[5]:
                        QUEEN_KING[qcp_bees_key][qcp]['total_borrow_power_allocation'] = st.slider(label=f'-', min_value=float(0.0), max_value=float(1.0), value=float(QUEEN_KING[qcp_bees_key][qcp]['total_borrow_power_allocation']), key=f'{qcp}_borrow_power_allocation{admin}', label_visibility='hidden')
                
                return True
            
            except Exception as e:
                er, er_line = print_line_of_error()
                st.write(f'{qcp_bees_key} {qcp} failed {er_line}')


        def chessboard(revrec, QUEEN_KING, ticker_allowed, themes, admin=False):
            try:
                def reset_qcps_model_theme(QUEEN_KING, qcp, model='MACD', theme='neutral'): # WORKERBEE update THEME 1 at a time
                    for ticker in QUEEN_KING['chess_board'][qcp].get('tickers'):
                        QUEEN_KING = add_trading_model(status='active', QUEEN_KING=QUEEN_KING, ticker=ticker, model=model, theme=theme)
                    
                    PickleData(QUEEN_KING.get('source'), QUEEN_KING)

                    return True
                
                def handle__new_tickers__AdjustTradingModels(QUEEN_KING, reset_theme=False):
                    # add new trading models if needed
                    # Castle 
                    trading_models = QUEEN_KING['king_controls_queen']['symbols_stars_TradingModel']
                    for qcp, bees_data in QUEEN_KING[qcp_bees_key].items():
                        for ticker in bees_data.get('tickers'):
                            try:
                                if reset_theme:
                                    QUEEN_KING = add_trading_model(status='active', QUEEN_KING=QUEEN_KING, ticker=ticker, model=bees_data.get('model'), theme=bees_data.get('theme'))
                                else:
                                    if ticker not in trading_models.keys():
                                        QUEEN_KING = add_trading_model(status='active', QUEEN_KING=QUEEN_KING, ticker=ticker, model=bees_data.get('model'), theme=bees_data.get('theme'))
                            except Exception as e:
                                print('wtferr', e)
                    return QUEEN_KING

                name = 'Chess Board'
                qcp_bees_key = 'chess_board'

                current_setup = QUEEN_KING['chess_board']
                chess_pieces = set_chess_pieces_symbols(QUEEN_KING=QUEEN_KING, qcp_bees_key=qcp_bees_key)
                view = chess_pieces.get('view')
                all_workers = chess_pieces.get('all_workers')
                qcp_ticker_index = chess_pieces.get('ticker_qcp_index')
                current_tickers = qcp_ticker_index.keys()
                
                # with st.expander(name, True): # ChessBoard
                allow_queen_to_update_chessboard = st.checkbox("Allow QUEEN to update Board as best she see's fit", True)
                cb_tab_list = ['Board', 'Star Allocation']
                tabs = st.tabs(cb_tab_list)
                with tabs[0]:
                    with st.form(f'ChessBoard_form{admin}'):
                        try:
                            # cols = st.columns((1,3,2))
                            # with cols[0]:
                            #     hc.option_bar(option_definition=pq_buttons.get('chess_option_data'),title='', key='chess_search', horizontal_orientation=True)                                
                            # with cols[1]:
                            #     ticker_search = st.text_input("Find Symbol") ####### WORKERBEE
                            # with cols[1]:
                            #     st.subheader(name)
                            
                            cols = st.columns((1,3,1,1,2,2))
                            headers = 0
                            for qcp in all_workers:
                                setup_qcp_on_board(cols, QUEEN_KING, qcp_bees_key, qcp, ticker_allowed=ticker_allowed, themes=themes, headers=headers)
                                headers+=1
                            
                            # RevRec
                            # print('RevRec')
                            QUEEN_KING['revrec'] = revrec
                            QUEEN_KING['chess_board__revrec'] = revrec
                            df_qcp = revrec.get('df_qcp')
                            df_ticker = revrec.get('df_ticker')
                            df_stars = revrec.get('df_stars')
                            waveview = revrec.get('waveview')

                            QUEEN_KING['chess_board__revrec'] = {'df_qcp': df_qcp, 'df_ticker': df_ticker, 'df_stars':df_stars,}

                            # symbol_total_budget_remaining = revrec['df_ticker'].loc["SPY"].get("ticker_remaining_budget")
                            # symbol_total_borrow_remaining = revrec['df_ticker'].loc["SPY"].get("ticker_remaining_borrow")
                            # st.write(symbol_total_budget_remaining, symbol_total_borrow_remaining)
                            # for ticker_time_frame in df_stars.index.to_list():
                            #     star_total_budget = df_stars.loc[ticker_time_frame].get('star_total_budget')
                            #     ttf_remaining_budget = return_ttf_remaining_budget(QUEEN, star_total_budget, ticker_time_frame, active_queen_order_states)
                            #     df_stars.at[ticker_time_frame, 'remaining_budget'] = ttf_remaining_budget

                            for qcp in all_workers:
                                # if qcp not in ['castle', 'castle_coin', 'bishop', 'knight']:
                                #     continue
                                
                                total_ticker_budget = 0
                                tickers_cost_basis = 0
                                qcp_tickers = [i for i in qcp_ticker_index.keys() if qcp_ticker_index[i] == qcp]
                                for ticker in qcp_tickers:

                                    total_budget = df_ticker.loc[ticker].get('ticker_total_budget')
                                    total_ticker_budget+=total_budget
                                    q_orders = return_queen_orders__query(QUEEN=QUEEN, queen_order_states=RUNNING_Orders , ticker=ticker)
                                    if len(q_orders) > 0:
                                        current_running_cost_b = sum(q_orders['cost_basis'])
                                        tickers_cost_basis+=current_running_cost_b
                                
                                remaing_qcp_budget = total_ticker_budget - tickers_cost_basis
                            cols = st.columns(2)
                            with cols[0]:
                                if st.form_submit_button('Save Board', use_container_width=True):
                                    if authorized_user == False:
                                        st.warning("You Need your Queen First! Please contact pollenq.queen@gmail.com")
                                        return False
                                    
                                    QUEEN_KING = handle__new_tickers__AdjustTradingModels(QUEEN_KING=QUEEN_KING)
                                    PickleData(pickle_file=PB_App_Pickle, data_to_store=QUEEN_KING)
                                    st.success("New Move Saved")
                            with cols[1]:
                                if st.form_submit_button('Reset ChessBoards Trading Models With Theme', on_click=on_click_ss_value_bool('reset_chessboard_theme'), use_container_width=True):
                                    if authorized_user == False:
                                        st.warning("You Need your Queen First! Please contact pollenq.queen@gmail.com")
                                        return False

                                    reset_theme = True if 'reset_chessboard_theme' in st.session_state and st.session_state['reset_chessboard_theme'] else False
                                    print(reset_theme)
                                    QUEEN_KING = handle__new_tickers__AdjustTradingModels(QUEEN_KING, reset_theme)
                                    PickleData(pickle_file=PB_App_Pickle, data_to_store=QUEEN_KING)
                                    st.success("All Trading Models Reset to Theme")

                        except Exception as e:
                            print_line_of_error()

                        
                    # st.write("# Reallocation")
                    with tabs[1]:
                        reallocate_star_power(QUEEN_KING, trading_model=False, ticker_option_qc=False, trading_model_revrec={}, trading_model_revrec_s={}, showguage=False, func_selection=True, formkey="Reallocate_Star")


                with st.expander("New Chess Piece"):
                    add_new_qcp__to_chessboard(cols=False, QUEEN_KING=QUEEN_KING, qcp_bees_key='chess_board', ticker_allowed=ticker_allowed, themes=themes)

                # with st.form("download files"):
                if st.button("download csv"):
                    try:
                        download_df_as_CSV(waveview, 'waveview.csv')
                    except Exception as e:
                        print(e)
            except Exception as e:
                print('chessboard ', e, print_line_of_error())

        
        def add_new_qcp__to_Queens_workerbees(QUEENBEE, qcp_bees_key, ticker_allowed):
            models = ['MACD', 'story__AI']
            qcp_pieces = QUEENBEE[qcp_bees_key].keys()
            qcp = st.text_input(label='piece name', value=f'pawn_{len(qcp_pieces)}', help="Theme your names to match your strategy")
            if qcp in qcp_pieces:
                st.error("Chess Piece Name must be Unique")
                st.stop()
            cols = st.columns(2)
            QUEENBEE[qcp_bees_key][qcp] = init_qcp(init_macd_vars={'fast': 12, 'slow': 26, 'smooth': 9}, ticker_list=[], model='story__AI')
            with cols[0]:
                QUEENBEE[qcp_bees_key][qcp]['tickers'] = st.multiselect(label=f'{qcp} symbols', options=ticker_allowed, default=None, help='Try not to Max out number of piecesm, only ~10 allowed')
            with cols[1]:
                QUEENBEE[qcp_bees_key][qcp]['model'] = st.selectbox(label='-', options=models, index=models.index(QUEENBEE[qcp_bees_key][qcp].get('model')), key=f'{qcp}model{admin}')


            with st.form('add new qcp'):
                cols = st.columns((1,6,2,2,2,2))

                with cols[0]:
                    st.image(MISC.get('queen_crown_url'), width=64)
                
                if QUEENBEE[qcp_bees_key][qcp]['model'] == 'story__AI':
                    # first_symbol = QUEENBEE[qcp_bees_key][qcp]['tickers'][0]
                    # ttf_macd_wave_ratios = ReadPickleData(os.path.join(hive_master_root(), 'backtesting/macd_backtest_analysis.csv'))
                    st.write("Lets Let AI Wave Analysis Handle Wave")
                else:
                    m_fast=int(QUEENBEE[qcp_bees_key][qcp]['MACD_fast_slow_smooth']['fast'])
                    m_slow=int(QUEENBEE[qcp_bees_key][qcp]['MACD_fast_slow_smooth']['slow'])
                    m_smooth=int(QUEENBEE[qcp_bees_key][qcp]['MACD_fast_slow_smooth']['smooth'])
                # with cols[1]:
                #     QUEENBEE[qcp_bees_key][qcp]['tickers'] = st.multiselect(label=f'{qcp} symbols', options=ticker_allowed, default=None, help='Try not to Max out number of piecesm, only ~10 allowed')
                # with cols[2]:
                #     QUEENBEE[qcp_bees_key][qcp]['model'] = st.selectbox(label='', options=models, index=models.index(QUEENBEE[qcp_bees_key][qcp].get('model')), key=f'{qcp}model{admin}')
                    with cols[3]:
                        QUEENBEE[qcp_bees_key][qcp]['MACD_fast_slow_smooth']['fast'] = st.number_input("fast", min_value=1, max_value=33, value=m_fast, key=f'{qcp}fast')
                    with cols[4]:
                        QUEENBEE[qcp_bees_key][qcp]['MACD_fast_slow_smooth']['slow'] = st.number_input("slow", min_value=1, max_value=33, value=m_slow, key=f'{qcp}slow')
                    with cols[5]:
                        QUEENBEE[qcp_bees_key][qcp]['MACD_fast_slow_smooth']['smooth'] = st.number_input("smooth", min_value=1, max_value=33, value=m_smooth, key=f'{qcp}smooth')            
                
                if st.form_submit_button('Save New qcp'):
                    PickleData(QUEENBEE.get('source'), QUEENBEE)

        def QB_workerbees(QUEENBEE, admin=True):
            try:
                # QUEENBEE read queen bee and update based on QUEENBEE
                name = 'Workerbees_Admin'
                qcp_bees_key = 'workerbees'
                ticker_allowed = list(KING['ticker_universe'].get('alpaca_symbols_dict').keys()) + crypto_symbols__tickers_avail
                
                chess_pieces = set_chess_pieces_symbols(QUEEN_KING=QUEENBEE, qcp_bees_key=qcp_bees_key)
                view = chess_pieces.get('view')
                all_workers = chess_pieces.get('all_workers')
                qcp_ticker_index = chess_pieces.get('ticker_qcp_index')
                current_tickers = qcp_ticker_index.keys()
 
                with st.expander("New Workerbee"):
                    add_new_qcp__to_Queens_workerbees(QUEENBEE=QUEENBEE, qcp_bees_key=qcp_bees_key, ticker_allowed=ticker_allowed)
                
                with st.expander(name, True):
                    with st.form(f'Update WorkerBees{admin}'):
                        ticker_search = st.text_input("Find Symbol") ####### WORKERBEE
                        
                        cols = st.columns((1,1,1))
                        with cols[1]:
                            st.subheader(name)
                        
                        cols = st.columns((1,3,2,2,2,2))
                        for qcp in all_workers:
                            try:
                                if qcp == 'castle_coin':
                                    with cols[0]:
                                        st.image(MISC.get('castle_png'), width=74)
                                elif qcp == 'castle':
                                    with cols[0]:
                                        st.image(MISC.get('castle_png'), width=74)
                                elif qcp == 'bishop':
                                    with cols[0]:
                                        st.image(MISC.get('bishop_png'), width=74)
                                elif qcp == 'knight':
                                    with cols[0]:
                                        st.image(MISC.get('knight_png'), width=74)
                                else:
                                    with cols[0]:
                                        st.image(MISC.get('knight_png'), width=74)
                                
                                ticker_list = QUEENBEE[qcp_bees_key][qcp]['tickers']
                                all_tickers = ticker_allowed + crypto_symbols__tickers_avail
                                # st.write([i for i in ticker_list if i not in all_tickers])
                                QUEENBEE[qcp_bees_key][qcp]['tickers'] = [i for i in ticker_list if i in all_tickers]

                                with cols[1]:
                                    QUEENBEE[qcp_bees_key][qcp]['tickers'] = st.multiselect(label=f'{qcp}', options=ticker_allowed + crypto_symbols__tickers_avail, default=QUEENBEE[qcp_bees_key][qcp]['tickers'], help='Castle Should Hold your Highest Valued Symbols', key=f'{qcp}tickers{admin}')
                                with cols[2]:
                                    st.selectbox(label='Model', options=['MACD'], key=f'{qcp}model{admin}')
                                with cols[3]:
                                    QUEENBEE[qcp_bees_key][qcp]['MACD_fast_slow_smooth']['fast'] = st.number_input(f'fast', min_value=1, max_value=88, value=int(QUEENBEE[qcp_bees_key][qcp]['MACD_fast_slow_smooth']['fast']), key=f'{qcp}fast{admin}')
                                with cols[4]:
                                    QUEENBEE[qcp_bees_key][qcp]['MACD_fast_slow_smooth']['slow'] = st.number_input(f'slow', min_value=1, max_value=88, value=int(QUEENBEE[qcp_bees_key][qcp]['MACD_fast_slow_smooth']['slow']), key=f'{qcp}slow{admin}')
                                with cols[5]:
                                    QUEENBEE[qcp_bees_key][qcp]['MACD_fast_slow_smooth']['smooth'] = st.number_input(f'slow', min_value=1, max_value=88, value=int(QUEENBEE[qcp_bees_key][qcp]['MACD_fast_slow_smooth']['smooth']), key=f'{qcp}smooth{admin}')
                            except Exception as e:
                                print(e, qcp)
                                st.write(qcp, " ", e)
                                st.write(QUEENBEE[qcp_bees_key][qcp])

                        if st.form_submit_button('Save ChessBoard'):
                            PickleData(pickle_file=QUEENBEE.get('source'), data_to_store=QUEENBEE)
                            st.success("Swarm QueenBee Saved")
                            
                            return True


                return True
            except Exception as e:
                print(e, print_line_of_error())

       
        def show_heartbeat():
            cols = st.columns(4)
            with cols[0]:
                if st.button("clear all sell orders", key=f'button_a'):
                    QUEEN_KING['sell_orders'] = []
                    PickleData(PB_App_Pickle, QUEEN_KING)
                st.write("sell_orders")
                st.write(QUEEN_KING['sell_orders'])
                
                st.write("Heart")
                st.write(QUEEN['heartbeat'])

                if st.button("clear all buy orders", key=f'button_buy'):
                    QUEEN_KING['buy_orders'] = []
                    PickleData(PB_App_Pickle, QUEEN_KING)
                st.write("buy_orders")
                st.write(QUEEN_KING['buy_orders'])

            
            with cols[1]:
                if st.button("clear all queen_sleep", key=f'button_b'):
                    QUEEN_KING['queen_sleep'] = []
                    PickleData(PB_App_Pickle, QUEEN_KING)
                st.write("queen_sleep")
                st.write(QUEEN_KING['queen_sleep'])
                st.write("queen_messages")
                st.write(QUEEN['queens_messages'])
            with cols[2]:
                if st.button("clear all update_queen_order", key=f'button_c'):
                    QUEEN_KING['update_queen_order'] = []
                    PickleData(PB_App_Pickle, QUEEN_KING)
                st.write("update_queen_order")
                st.write(QUEEN_KING['update_queen_order'])
            with cols[3]:
                if st.button("clear all wave_triggers", key=f'button_d'):
                    QUEEN_KING['wave_triggers'] = []
                    PickleData(PB_App_Pickle, QUEEN_KING)
                st.write(QUEEN_KING.get('wave_triggers'))
            
                if st.button("update KORS", key=f'update_kors'):
                    QUEEN_KING['update_order_rules'] = []
                    # PickleData(PB_App_Pickle, QUEEN_KING)
                    PickleData(QUEEN_KING.get('source'), QUEEN_KING)
                st.write(QUEEN_KING.get('update_order_rules'))

        
        def backtesting():
            with st.expander("backtesting"):
                cols = st.columns((1,1,3))
                with cols[0]:
                    # back_test_blocktime = pd.read_csv(os.path.join(hive_master_root(), 'backtesting/macd_backtest_analysis.csv'))
                    back_test_blocktime = pd.read_csv(os.path.join(hive_master_root(), 'backtesting/macd_backtest_analysis.txt'))
                    st.write("current MACDS", back_test_blocktime)

                with cols[0]:
                    len_divider = st.slider(label=f'back test len to avg', key=f'len_divider', min_value=int(1), max_value=int(10), value=3)
                back_test_blocktime = os.path.join(hive_master_root(), 'backtesting/macd_grid_search_blocktime.txt')
                df_backtest = pd.read_csv(back_test_blocktime, dtype=str)
                df_backtest['key'] = df_backtest["macd_fast"] + "_" + df_backtest["macd_slow"] + "_" + df_backtest["macd_smooth"]
                for col in ['macd_fast', 'macd_slow', 'macd_smooth', 'winratio', 'maxprofit']:
                    df_backtest[col] = pd.to_numeric(df_backtest[col], errors='coerce')
                df_backtest_ttf = df_backtest.groupby(['ttf', 'key', 'macd_fast', 'macd_slow', 'macd_smooth'])[['winratio', 'maxprofit']].sum().reset_index()
                # st.dataframe(df_backtest)
                # standard_AGgrid(df_backtest_ttf)
                # standard_AGgrid(df_backtest)
                stars_times = stars().keys()
                tickers = set([i.split("_")[0] for i in df_backtest_ttf['ttf'].tolist()])
                results = []
                results_top = []
                for ticker in tickers:
                    for tframes in stars_times:
                        spy = df_backtest_ttf[df_backtest_ttf['ttf'] == f'{ticker}_{tframes}']
                        top_num = round(int(len(spy) / len_divider),0)
                        # print(len(spy), top_num)
                        spy_ = spy[spy.index.isin(spy['maxprofit'].nlargest(n=top_num).index.tolist())]
                        mf = int(round(sum(spy_['macd_fast']) / len(spy_),0))
                        ms = int(round(sum(spy_['macd_slow']) / len(spy_),0))
                        mss = int(round(sum(spy_['macd_smooth']) / len(spy_),0))
                        spy_['avg_ratio'] = f'{mf}_{ms}_{mss}'
                        spy_result = spy_[['ttf', 'avg_ratio']].drop_duplicates()
                        results_top.append(spy_result)
                        results.append(spy_)

                df_top5 = pd.concat(results)
                df_top5_results = pd.concat(results_top)

                with cols[1]:
                    st.write("top ", len_divider)
                    standard_AGgrid(df_top5_results)
                with cols[2]:
                    if st.button("write analysis results"):
                        df_top5_results.to_csv(os.path.join(hive_master_root(), 'backtesting/macd_backtest_analysis.txt'))
                        st.success("Saved")
                standard_AGgrid(df_top5)


        def orders_agrid():
            with st.expander("Portfolio Orders", False):
                ordertables__agrid = queen_order_flow(QUEEN=QUEEN, active_order_state_list=active_order_state_list, order_buttons=st.session_state.get('order_buttons'))
                if authorized_user:
                    if ordertables__agrid == False:
                        return True
                    if ordertables__agrid.selected_rows:
                        # st.write(queen_order[0]['client_order_id'])
                        queen_order = ordertables__agrid.selected_rows[0]
                        client_order_id = queen_order.get('client_order_id')

                        try: # OrderState
                            df = ordertables__agrid["data"][ordertables__agrid["data"].orderstate == "clicked"]
                            if len(df) > 0:
                                current_requests = [i for i in QUEEN_KING['update_queen_order'] if client_order_id in i.keys()]
                                if len(current_requests) > 0:
                                    st.write("You Already Requested Queen To Change Order State, Refresh Orders to View latest Status")
                                else:
                                    order_update_package = create_AppRequest_package(request_name='update_queen_order', client_order_id=client_order_id)
                                    order_update_package['queen_order_updates'] = {client_order_id: {'queen_order_state': queen_order.get('queen_order_state')}}
                                    QUEEN_KING['update_queen_order'].append(order_update_package)
                                    PickleData(PB_App_Pickle, QUEEN_KING)
                                    st.success(f'{client_order_id} Changing QueenOrderState Please wait for Queen to process, Refresh Table')
                        except:
                            st.write("OrderState nothing was clicked")
                        
                        # validate to continue with selection
                        try: ## SELL
                            df = ordertables__agrid["data"][ordertables__agrid["data"].sell == "clicked"]
                            if len(df) > 0:
                                current_requests = [i for i in QUEEN_KING['sell_orders'] if client_order_id in i.keys()]
                                if len(current_requests) > 0:
                                    st.write("You Already Requested Queen To Sell order, Refresh Orders to View latest Status")
                                else:
                                    sell_package = create_AppRequest_package(request_name='sell_orders', client_order_id=client_order_id)
                                    sell_package['sell_qty'] = float(queen_order.get('qty_available'))
                                    sell_package['side'] = 'sell'
                                    sell_package['type'] = 'market'
                                    QUEEN_KING['sell_orders'].append(sell_package)
                                    PickleData(PB_App_Pickle, QUEEN_KING)
                                    st.success(f'{client_order_id} : Selling Order Sent to Queen Please wait for Queen to process, Refresh Table')
                            else:
                                st.write("Nothing Sell clicked")

                        except:
                            er_line = print_line_of_error()
                            st.write("Error in Sell ", er_line)
                        try: ## KOR
                            df = ordertables__agrid["data"][ordertables__agrid["data"].orderrules == "clicked"]
                            if len(df) > 0:
                                st.write("KOR: ", client_order_id)
                            else:
                                st.write("Nothing KOR clicked")
                        except:
                            st.write("KOR PENDING WORK")


        def order_grid(KING, queen_orders, ip_address):
            gb = GridOptionsBuilder.create()
            gb.configure_grid_options(pagination=False, enableRangeSelection=True, copyHeadersToClipboard=True, sideBar=False)
            gb.configure_default_column(column_width=100, resizable=True, textWrap=True, wrapHeaderText=True, autoHeaderHeight=True, autoHeight=True, suppress_menu=False, filterable=True, sortable=True, ) # cellStyle= {"color": "white", "background-color": "gray"}   

            #Configure index field
            gb.configure_index('client_order_id')
            gb.configure_theme('ag-theme-material')


            def config_cols():
                money_def = {
                    'cellRenderer': 'agAnimateShowChangeCellRenderer',
                    'enableCellChangeFlash': True,
                    'pinned':'left',
                    }
                honey_options = {'headerName': '%Honey',
                                # 'pinned': 'left',
                                 'cellRenderer': 'agAnimateShowChangeCellRenderer','enableCellChangeFlash': True,
                                 'type': ["customNumberFormat", "numericColumn", "numberColumnFilter", ],
                                 'custom_currency_symbol':"%",
                                            }
                return {
                        'honey': honey_options,
                        'symbol': create_ag_grid_column(headerName="Symbol", initialWidth=95),
                        'ttf_grid_name': create_ag_grid_column(headerName='Star'),
                        'sell_reason': create_ag_grid_column(headerName="Reason To Sell", initialWidth=135, editable=True),
                        'cost_basis_current': {'headerName': 'Cost Basis Current', "type": ["customNumberFormat", "numericColumn", "numberColumnFilter", ], # "customCurrencyFormat"
                                                                    #    'custom_currency_symbol':"$",
                                                                    "sortable":True,
                                                                    # "pinned": 'right',
                                                                    'initialWidth': 115,
                                                                    },
                        'filled_qty': {},
                        'qty_available': {},
                        'borrowed_funds': create_ag_grid_column(headerName="Borrowed Money", initialWidth=135),
                        'trigname': {'headerName': 'TrigWave', 'initialWidth': 135,},
                        'current_macd': {'headerName': 'Current MACD', 'initialWidth': 135,},
                        'queen_order_state': {"cellEditorParams": {"values": active_order_state_list},
                                                                            "editable":True,
                                                                            "cellEditor":"agSelectCellEditor",
                                                                            },
                        'client_order_id': {},
                        'cost_basis': {'headerName': 'Starting Cost Basis', "type": ["customNumberFormat", "numericColumn", "numberColumnFilter", ], # "customCurrencyFormat"
                                                                    #    'custom_currency_symbol':"$",
                                                                    "sortable":True,
                                                                    # "pinned": 'right',
                                                                    'initialWidth': 115,
                                                                    },
                        'datetime': {'type': ["dateColumnFilter", "customDateTimeFormat"], "custom_format_string": "MM/dd/yy HH:mm", 'initialWidth': 133,},

                                }

            config_cols = config_cols()
            for col, config_values in config_cols.items():
                config = config_values
                config['sortable'] = True
                gb.configure_column(col, config)
            mmissing = [i for i in queen_orders.iloc[-1].index.tolist() if i not in config_cols.keys()]
            if len(mmissing) > 0:
                for col in mmissing:
                    gb.configure_column(col, {'hide': True})

            go = gb.build()
            

            refresh_sec = 5 if seconds_to_market_close > 0 and mkhrs == 'open' else None
            st_custom_grid(
                client_user=client_user,
                username=KING['users_allowed_queen_emailname__db'].get(client_user), 
                api=f'{ip_address}/api/data/queen',
                api_update=f'{ip_address}/api/data/update_orders',
                refresh_sec=refresh_sec, 
                refresh_cutoff_sec=seconds_to_market_close, 
                prod=st.session_state['production'],
                key='maingrid',
                grid_options=go,
                # kwargs from here
                api_key=os.environ.get("fastAPI_key"),
                buttons=[{'button_name': 'sell',
                        'button_api': f'{ip_address}/api/data/queen_sell_orders',
                        'prompt_message': 'Select Qty to Sell',
                        'prompt_field': "qty_available",
                        'col_headername': 'Take Money',
                        'col_width':135,
                        'pinned': 'right',
                        "col_header": "money",
                        "border_color": "green",
                        },
                        {'button_name': 'Order Rules',
                        'button_api': f'{ip_address}/api/data/update_queen_order_kors',
                        'prompt_message': 'Edit Rules',
                        'prompt_field': 'order_rules',
                        'col_headername': 'Order Rules',
                        'col_width':135,
                        # 'pinned': 'right',
                        'prompt_order_rules': ['take_profit', 'sell_out', 'close_order_today', 'close_order_today_allowed_timeduration', 'stagger_profits_tiers', 'trade_using_limits', 'sell_trigbee_trigger', 'sell_trigbee_trigger_timeduration', 'sell_date', 'use_wave_guage'],
                        "col_header": "time_frame",
                        "border_color": "green",
                        },
                        {'button_name': 'Archive',
                        'button_api': f'{ip_address}/api/data/queen_archive_queen_order',
                        'prompt_message': 'Archive Order',
                        'prompt_field': 'client_order_id',
                        'col_headername': 'Archive Order',
                        'col_width':89,
                        # "col_header": "symbol",
                        "border_color": "green",
                        },
                        ],
                grid_height='300px',
                toggle_views = ['buys', 'sells', 'today', 'close today'] + ttf_grid_names_list(),
            )

        
        def wave_grid(revrec, symbols, ip_address, refresh_sec=8, key='default'):
            gb = GridOptionsBuilder.create()
            gb.configure_default_column(column_width=100, resizable=True,textWrap=True, wrapHeaderText=True, autoHeaderHeight=True, autoHeight=True, suppress_menu=False,filterable=True,sortable=True)            
            gb.configure_index('ticker_time_frame')
            gb.configure_theme('ag-theme-material')

            def config_cols():

                return {
                    # 'ticker_time_frame': {'initialWidth': 168,},
                        # 'symbol': create_ag_grid_column(headerName='symbol'),
                        'ttf_grid_name': create_ag_grid_column(headerName='Star', width=148),
                        # 'ttf_grid_name': {'headerName':'Star','initialWidth':123, 'textWrap':True},
                        'current_profit': create_ag_grid_column(headerName='Curent Profit', initialWidth=89, type=["customNumberFormat", "numericColumn", "numberColumnFilter"], cellRenderer='agAnimateShowChangeCellRenderer', enableCellChangeFlash=True,),
                        'maxprofit': {'cellRenderer': 'agAnimateShowChangeCellRenderer','enableCellChangeFlash': True,
                                    "type": ["customNumberFormat", "numericColumn", "numberColumnFilter", ],},
                        
                        'long_at_play': {'headerName':'Long At Play', "type": ["customNumberFormat", "numericColumn", "numberColumnFilter", ], # "customCurrencyFormat"
                                                        #    'custom_currency_symbol':"$",
                                                        'initialWidth':123,
                                                        },
                        'short_at_play': {'headerName':'Short At Play', "type": ["customNumberFormat", "numericColumn", "numberColumnFilter", ], # "customCurrencyFormat"
                                                        #    'custom_currency_symbol':"$",
                                                        'initialWidth':123,
                                                        },
                        'allocation_deploy': {'headerName':'Allocation Deploy', 'cellRenderer': 'agAnimateShowChangeCellRenderer','enableCellChangeFlash': True,
                                    "type": ["customNumberFormat", "numericColumn", "numberColumnFilter", ],
                                    'initialWidth':123,
                                    },
                        'allocation_borrow_deploy': {'headerName':'Allocation Borrow Deploy',
                                    "type": ["customNumberFormat", "numericColumn", "numberColumnFilter", ],
                                    'initialWidth':123,
                                    },
                        'total_allocation_budget': {'headerName':'Budget Allocation',
                                    "type": ["customNumberFormat", "numericColumn", "numberColumnFilter", ],
                                    'initialWidth':123,
                                    },
                        
                        'total_allocation_borrow_budget': {'headerName':'Margin Budget Allocation',
                                    "type": ["customNumberFormat", "numericColumn", "numberColumnFilter", ],
                                    'initialWidth':123,
                                    },

                        'remaining_budget': {'header_name':'Remaining Budget', "type": ["customNumberFormat", "numericColumn", "numberColumnFilter", ], # "customCurrencyFormat"
                                                        #    'custom_currency_symbol':"$",
                                                        'initialWidth':123,
                                                        },
                        'remaining_budget_borrow': {'header_name':'Remaining Budget', "type": ["customNumberFormat", "numericColumn", "numberColumnFilter", ], # "customCurrencyFormat"
                                                        #    'custom_currency_symbol':"$",
                                                        'initialWidth':123,
                                                        },
                        'ticker_time_frame__budget': {'hide': True},
                        
                                }

            config_cols = config_cols()
            for col, config_values in config_cols.items():
                config = config_values
                config['sortable'] = True
                gb.configure_column(col, config)
                # gb.configure_column(col, {'pinned': 'left'})
            mmissing = [i for i in revrec.get('waveview').columns.tolist() if i not in config_cols.keys()]
            # print(revrec.get('waveview').at['SPY_1Minute_1Day', 'king_order_rules'])
            if len(mmissing) > 0:
                for col in mmissing:
                    gb.configure_column(col, {'hide': True})

            go = gb.build()

            st_custom_grid(
                client_user=client_user,
                username=KING['users_allowed_queen_emailname__db'].get(client_user), 
                api=f'{ip_address}/api/data/wave_stories',
                api_update= f'{ip_address}/api/data/update_orders',
                refresh_sec=refresh_sec, 
                refresh_cutoff_sec=seconds_to_market_close, 
                prod=st.session_state['production'],
                grid_options=go,
                key=f'{"workerbees"}{key}',
                # kwargs from here
                api_key=os.environ.get("fastAPI_key"),
                return_type='waves',
                prompt_message ="Buy Amount",
                prompt_field = "star", # "current_macd_tier",
                read_pollenstory = False,
                read_storybee = True,
                symbols=symbols,
                buttons=[
                        {'button_name': None,
                        'button_api': f'{ip_address}/api/data/queen_buy_wave_orders',
                        'prompt_message': 'Buy Wave',
                        'prompt_field': 'macd_state',
                        'col_headername': 'macd_state',
                        "col_header": "macd_state",
                        "col_width": 133,
                        "border_color": "green",
                        # 'pinned': 'left',
                        },

                        {'button_name': None, # this used to name the button
                        'button_api': f'{ip_address}/api/data/queen_buy_orders',
                        'prompt_message': 'Edit Buy',
                        'prompt_field': 'kors',
                        'col_headername': 'Buy Wave',
                        "col_header": "ticker_time_frame__budget", # button display
                        'col_width':125,
                        'pinned': 'right',
                        'prompt_order_rules': [i for i in buy_button_dict_items().keys()],
                        },
                        ],
                grid_height='350px',
                toggle_views = ["Queen",] + ttf_grid_names_list() + ['Buys', 'Sells', 'King'],
            ) 

      
        def story_grid(client_user, ip_address, revrec, symbols, refresh_sec=8, key='default'):
            try:
                gb = GridOptionsBuilder.create()
                gb.configure_default_column(column_width=100, resizable=True,textWrap=True, wrapHeaderText=True, autoHeaderHeight=True, autoHeight=True, suppress_menu=False,filterable=True,sortable=True)            
                gb.configure_index('symbol')
                gb.configure_theme('ag-theme-material')

                def config_cols(cols):

                    return  {
                    # for col in cols:
                    'symbol': create_ag_grid_column(headerName='Symbol', initialWidth=89),
                    'queens_note': create_ag_grid_column(headerName='Queens Note', initialWidth=89, textWrap=True),
                    'long_at_play': create_ag_grid_column(headerName='$Long',sortable=True, initialWidth=100, enableCellChangeFlash=True, cellRenderer='agAnimateShowChangeCellRenderer', type=["customNumberFormat", "numericColumn", "numberColumnFilter", ]),
                    'short_at_play': create_ag_grid_column(headerName='$Short',sortable=True, initialWidth=100, enableCellChangeFlash=True, cellRenderer='agAnimateShowChangeCellRenderer',  type=["customNumberFormat", "numericColumn", "numberColumnFilter", ]),
                    'remaining_budget': create_ag_grid_column(headerName='Remaining Budget', initialWidth=100,  type=["customNumberFormat", "numericColumn", "numberColumnFilter", ]),
                    'remaining_budget_borrow': create_ag_grid_column(headerName='Remaining Budget Margin', initialWidth=100, type=["customNumberFormat", "numericColumn", "numberColumnFilter", ]),
                    'trinity_w_L': create_ag_grid_column(headerName='Trinity Force',sortable=True, initialWidth=89, enableCellChangeFlash=True, cellRenderer='agAnimateShowChangeCellRenderer'),
                    'trinity_w_15': create_ag_grid_column(headerName='Flash Force',sortable=True, initialWidth=89, ),
                    'trinity_w_30': create_ag_grid_column(headerName='Middle Force',sortable=True, initialWidth=89, ),
                    'trinity_w_54': create_ag_grid_column(headerName='Future Force',sortable=True, initialWidth=89, ),
                    'qty_available': create_ag_grid_column(headerName='Qty Avail', initialWidth=89),
                    'broker_qty_available': create_ag_grid_column(headerName='Broker Qty Avail', initialWidth=89),
                    # 'trinity_w_S': create_ag_grid_column(headerName='Margin Force',sortable=True, initialWidth=89, enableCellChangeFlash=True, cellRenderer='agAnimateShowChangeCellRenderer'),

                    }


                story_col = revrec.get('storygauge').columns.tolist()
                config_cols_ = config_cols(story_col)
                for col, config_values in config_cols_.items():
                    config = config_values
                    gb.configure_column(col, config)
                mmissing = [i for i in story_col if i not in config_cols_.keys()]
                if len(mmissing) > 0:
                    for col in mmissing:
                        gb.configure_column(col, {'hide': True})



                go = gb.build()

                st_custom_grid(
                    client_user=client_user,
                    username=KING['users_allowed_queen_emailname__db'].get(client_user), 
                    api=f"{ip_address}/api/data/story",
                    api_update=f"{ip_address}/api/data/story",
                    refresh_sec=refresh_sec, 
                    refresh_cutoff_sec=seconds_to_market_close, 
                    prod=st.session_state['production'],
                    grid_options=go,
                    key=f'{"story"}{key}',
                    # kwargs from here
                    prompt_message = "symbol",
                    prompt_field = "symbol", # "current_macd_tier",
                    api_key=os.environ.get("fastAPI_key"),
                    return_type='story',
                    symbols=symbols,
                    buttons=[
                                {'button_name': None,
                                'button_api': f'{ip_address}/api/data/queen_buy_orders',
                                'prompt_message': 'Edit Buy',
                                'prompt_field': 'kors',
                                'col_headername': 'Buy',
                                "col_header": "queens_suggested_buy",
                                "border_color": "green",
                                'col_width':135,
                                # 'pinned': 'right',
                                'prompt_order_rules': [i for i in buy_button_dict_items().keys()],
                                },
                                {'button_name': None,
                                'button_api': f'{ip_address}/api/data/queen_sell_orders',
                                'prompt_message': 'Edit Sell',
                                'prompt_field': 'kors',
                                'col_headername': 'Sell',
                                "col_header": "queens_suggested_sell",
                                "border_color": "red",
                                'col_width':135,
                                # 'pinned': 'right',
                                'prompt_order_rules': [i for i in sell_button_dict_items().keys()],
                                },

                            ],
                grid_height='500px',
                toggle_views = ['Queen Picks'],
                ) 

            except Exception as e:
                print_line_of_error(e)

        
        def reallocate_star_power(QUEEN_KING, trading_model, ticker_option_qc, trading_model_revrec={}, trading_model_revrec_s={}, showguage=False, func_selection=False, formkey='Star__Allocation'):
            try:
                cols = st.columns((1,8))
                if func_selection:
                    with cols[0]:
                        control_option = 'symbols_stars_TradingModel'
                        models_avail = list(QUEEN_KING['king_controls_queen'][control_option].keys())
                        ticker_option_qc = st.selectbox("Reallocate Symbol", models_avail, index=models_avail.index(["SPY" if "SPY" in models_avail else models_avail[0]][0]), key=formkey) 
                        trading_model = QUEEN_KING['king_controls_queen'][control_option][ticker_option_qc]
                with cols[1]:
                    with st.form("Reallocate Star Power"):
                        st.header(f"Reallocate {ticker_option_qc}")
                        cols = st.columns((1,1,1,1,1,1,1))
                        c = 0
                        for star, star_vars in trading_model.get('stars_kings_order_rules').items():
                            trading_model_revrec[star] = star_vars.get("buyingpower_allocation_LongTerm")
                            trading_model_revrec_s[star] = star_vars.get("buyingpower_allocation_ShortTerm")
                            with cols[c]:
                                trading_model['stars_kings_order_rules'][star]["buyingpower_allocation_LongTerm"] = st.slider(label=f'L {star}', value=star_vars.get('buyingpower_allocation_LongTerm'), key=f'{star}{"_"}{"buying_power"}')
                                trading_model['stars_kings_order_rules'][star]["buyingpower_allocation_ShortTerm"] = st.slider(label=f'S {star}', value=star_vars.get('buyingpower_allocation_ShortTerm'), key=f'{star}{"_"}{"buying_power_s"}')
                            c+=1
                            # with cols[0]:
                            #     mark_down_text(align='left', text=star)

                        if showguage:
                            df_revrec = pd.DataFrame(trading_model_revrec.items())
                            df_revrec_s = pd.DataFrame(trading_model_revrec_s.items())
                            df = story_view(STORY_bee=STORY_bee, ticker=ticker_option_qc)['df']
                            # df_write = pd.concat([df], axis=1) ## Need to fix
                            df_style = df.style.background_gradient(cmap="RdYlGn", gmap=df['current_macd_tier'], axis=0, vmin=-8, vmax=8)
                            # with cols[1]:
                            st.write(df_style)
                            # edited_df = st.experimental_data_editor(df_write)
                        
                        if st.form_submit_button("Reallocate Star Power"):
                            QUEEN_KING['saved_trading_models'].update(trading_model)
                            PickleData(pickle_file=PB_App_Pickle, data_to_store=QUEEN_KING)
                            return_image_upon_save(title="Saved")
            except Exception as e:
                print_line_of_error("rev allocation error")
        
        
        def queen_messages_grid(KING, f_api="http://127.0.0.1:8000/api/data/queen_messages", varss={'seconds_to_market_close': None, 'refresh_sec': None}):
            gb = GridOptionsBuilder.create()
            gb.configure_default_column(pagination=False, column_width=100, resizable=True,textWrap=True, wrapHeaderText=True, autoHeaderHeight=True, autoHeight=True, suppress_menu=False,filterable=True,sortable=True)            
            
            #Configure index field
            gb.configure_index('idx')
            gb.configure_column('idx')
            gb.configure_column('message', {'initialWidth':800, "wrapText": True, "autoHeight": True, 'filter': True})
            go = gb.build()


            st_custom_grid(
                username=KING['users_allowed_queen_emailname__db'].get(st.session_state["username"]), 
                api=f_api,
                api_update=None,
                refresh_sec=varss.get('refresh_sec'), 
                refresh_cutoff_sec=varss.get('seconds_to_market_close'), 
                prod=st.session_state['production'],
                grid_options=go,
                key=f'{"queen_messages"}',
                button_name='insight',
                api_url=None,
                # kwargs from here
                api_key=os.environ.get("fastAPI_key"),
                prompt_message ="message",
                prompt_field = "idx", # "current_macd_tier",

            ) 

            return True


        def queen_messages_logfile_grid(KING, log_file, grid_key, f_api, varss={'seconds_to_market_close': None, 'refresh_sec': None}):
            gb = GridOptionsBuilder.create()
            gb.configure_grid_options(pagination=False, enableRangeSelection=True, copyHeadersToClipboard=True, sideBar=False)
            gb.configure_default_column(column_width=100, resizable=True,
                                textWrap=True, wrapHeaderText=True, autoHeaderHeight=True, autoHeight=True, suppress_menu=False, filterable=True, sortable=True)             
            #Configure index field
            gb.configure_index('idx')
            gb.configure_column('idx', {"sortable":True, 'initialWidth':23})
            gb.configure_column('message', {'initialWidth':800, "wrapText": True, "autoHeight": True, "sortable":True})
            go = gb.build()

            st_custom_grid(
                username=KING['users_allowed_queen_emailname__db'].get(st.session_state["username"]), 
                api=f_api,
                api_update=None,
                refresh_sec=varss.get('refresh_sec'), 
                refresh_cutoff_sec=varss.get('seconds_to_market_close'), 
                prod=st.session_state['production'],
                grid_options=go,
                key=f'{grid_key}',

                # kwargs from here
                api_key=os.environ.get("fastAPI_key"),
                buttons = [],

                grid_height='300px',
                log_file=log_file

            ) 

            return True



            def charts():
                refresh_sec = 8 if seconds_to_market_close > 0 and mkhrs == 'open' else 0
                refresh_sec = 23 if 'sneak_peak' in st.session_state and st.session_state['sneak_peak'] else refresh_sec

                cust_graph(username=KING['users_allowed_queen_emailname__db'].get(client_user),
                            prod=prod,
                            api=f'{ip_address}/api/data/symbol_graph',
                            x_axis='timestamp_est',
                            y_axis=symbols_unique_color(['SPY', 'SPY vwap', 'QQQ', 'QQQ vwap']),
                            theme_options={
                                'backgroundColor': k_colors.get('default_background_color'),
                                'main_title': '',   # '' for none
                                'x_axis_title': '',
                                'grid_color': default_text_color,
                                "showInLegend": True,
                                "showInLegendPerLine": True,
                            },
                            refresh_sec=refresh_sec,
                            refresh_button=True,
                            graph_height=300,
                            symbols=['SPY', 'QQQ'],
                            )
                # with cols[1]:
                    # with st.expander("Wave Race :ocean:", True):
                refresh_sec = 8 if seconds_to_market_close > 0 and mkhrs == 'open' else 0
                refresh_sec = 23 if 'sneak_peak' in st.session_state and st.session_state['sneak_peak'] else refresh_sec
                custom_graph_ttf_qcp(prod, KING, client_user, QUEEN_KING, refresh_sec, ip_address)

        ########################################################
        ########################################################
        #############The Infinite Loop of Time #################
        ########################################################
        ########################################################
        ########################################################

    try:

        pq_buttons = pollenq_button_source()

        db_root = st.session_state['db_root']
        prod, admin, prod_name = st.session_state['production'], st.session_state['admin'], st.session_state['prod_name']

        authorized_user = st.session_state['authorized_user']
        client_user = st.session_state["username"]

        # return page last visited 
        sneak_peak = False
        if 'sneak_peak' in st.session_state and st.session_state['sneak_peak'] == True:
            st.info("Welcome You must be Family -- This QueenBot is LIVE")

        elif st.session_state['authentication_status'] != True:
            st.write(st.session_state['authentication_status'])
            st.error("You Need to Log In")
            # switch_page("pollenq")
            sneak_peak = False
            st.session_state['sneak_peak'] == False
            st.stop()
        
        elif st.session_state['authentication_status']:
            sneak_peak = False
            pass
        else:
            st.error("Stopping page")
            st.stop()

        if 'chess_board__revrec' not in QUEEN_KING.keys():
            st.error("QUEENBOT Not Enabled >>> Save Your Portfolio Board before your Queen Bot can start Trading")
            chessboard(revrec=revrec, QUEEN_KING=QUEEN_KING, ticker_allowed=ticker_allowed, themes=themes, admin=False)
            st.stop()


        PB_QUEEN_Pickle = st.session_state['PB_QUEEN_Pickle'] 
        PB_App_Pickle = st.session_state['PB_App_Pickle'] 
        PB_Orders_Pickle = st.session_state['PB_Orders_Pickle'] 
        PB_queen_Archives_Pickle = st.session_state['PB_queen_Archives_Pickle']
        PB_QUEENsHeart_PICKLE = st.session_state['PB_QUEENsHeart_PICKLE']

    
        QUEENsHeart = ReadPickleData(PB_QUEENsHeart_PICKLE)

        acct_info = api_vars.get('acct_info')
        if st.session_state['authorized_user']: ## MOVE THIS INTO pollenq?
            clean_out_app_requests(QUEEN=QUEEN, QUEEN_KING=QUEEN_KING, request_buckets=['subconscious', 'sell_orders', 'queen_sleep', 'update_queen_order'])
        

        # # if authorized_user: log type auth and none
        log_dir = os.path.join(db_root, 'logs')
        init_logging(queens_chess_piece=queens_chess_piece, db_root=db_root, prod=st.session_state['production'])

        # db global
        # Ticker DataBase
        call_all_ticker_data = st.sidebar.checkbox("swarmQueen Symbols", False)

        coin_exchange = "CBSE"
        ticker_db = return_QUEENs__symbols_data(QUEEN=QUEEN, QUEEN_KING=QUEEN_KING, swarmQueen=call_all_ticker_data)
        POLLENSTORY = ticker_db['pollenstory']
        STORY_bee = ticker_db['STORY_bee']
        ticker_allowed = list(KING['ticker_universe'].get('alpaca_symbols_dict').keys()) + crypto_symbols__tickers_avail

        # tic_need_TM = [i.split("_")[0] for i in STORY_bee.keys()]
        tickers_avail = [list(set(i.split("_")[0] for i in STORY_bee.keys()))][0]
        # def cache_tradingModelsNotGenerated() IMPROVEMENT TO SPEED UP CACHE cache function
        tic_need_TM = [i for i in tickers_avail if i not in QUEEN_KING['king_controls_queen'].get('symbols_stars_TradingModel')]
        if len(tic_need_TM) > 0:
            print("Adding Trading Model")
            for ticker in tic_need_TM:
                tradingmodel1 = generate_TradingModel(ticker=ticker, status='active', theme="long_star")['MACD'][ticker]
                QUEEN_KING['king_controls_queen']['symbols_stars_TradingModel'][ticker] = tradingmodel1
        
        ticker_db_errors = ticker_db.get('errors')
        if len(ticker_db_errors) > 0:
            st.error("symbol errors")
            st.write(ticker_db_errors)
        trading_days = hive_dates(api=api)['trading_days']
        mkhrs = return_market_hours(trading_days=trading_days)
        seconds_to_market_close = (datetime.now(est).replace(hour=16, minute=0)- datetime.now(est)).total_seconds() 
        seconds_to_market_close = seconds_to_market_close if seconds_to_market_close > 0 else 0

        symbols = return_queenking_board_symbols(QUEEN_KING)

        # ip_address = get_ip_address()
        ip_address = st.session_state['ip_address']
        story_tab, trading_tab, order_tab, charts_tab, board_tab, model_tab = st.tabs(['Story', 'Waves', 'Orders', 'Wave Charts', 'Trading Board', 'Trading Models',]) # 'waves', 'workerbees', 'charts'
        # func_list = [i for i in func_list if st.session_state[i]]
        with st.spinner("Refreshing"): # ozzbot

            if authorized_user:
                revrec = refresh_chess_board__revrec(acct_info, QUEEN, QUEEN_KING, STORY_bee, active_queen_order_states, chess_board__revrec={}, revrec__ticker={}, revrec__stars={}) ## Setup Board
                if QUEEN_KING.get('revrec') == 'init':
                     QUEEN_KING['revrec'] = revrec
                clear_subconscious_Thought(QUEEN, QUEEN_KING)

                if 'show_queenheart' in st.session_state and st.session_state['show_queenheart']:
                    with st.expander('heartbeat', True):
                        show_heartbeat()
            
                if 'workerbees' in st.session_state and st.session_state['workerbees'] == True:
                    # hc.option_bar(option_definition=pq_buttons.get('workerbees_option_data'),title='WorkerBees', key='workerbees_option_data', horizontal_orientation=True) #,override_theme=over_theme,font_styling=font_fmt,horizontal_orientation=True)   
                    # if st.button("backtesting"):
                    backtesting()
                    # queen_triggerbees()
                    if st.session_state['admin']:
                        if st.button("Yahoo Return Fin.Data Job"):
                            with st.spinner("running yahoo.Fin.Data job"):
                                init_ticker_stats__from_yahoo()
                    with st.expander("yahoo stats", False):
                        db = ReadPickleData(os.path.join(hive_master_root(), 'db/yahoo_stats_bee.pkl'))
                        # st.write(db.keys())
                        avail_ticker_list = list(db.keys())
                        ticker_option = st.selectbox("ticker", options=avail_ticker_list)
                        if ticker_option is not None:
                            df_i = len(db.get(ticker_option))
                            for n in  range(df_i):
                                st.write(db.get(ticker_option)[n])
                    st.stop()

                with story_tab:

                    # with st.expander("Story Grid :fire:", True):
                    # ipdb.set_trace()
                    refresh_sec = 8 if seconds_to_market_close > 0 and mkhrs == 'open' else 0
                    refresh_sec = 23 if 'sneak_peak' in st.session_state and st.session_state['sneak_peak'] else refresh_sec
                    refresh_sec = None if st.sidebar.toggle("Edit Story Grid") else refresh_sec
                    story_grid(client_user=client_user, ip_address=ip_address, revrec=revrec, symbols=symbols, refresh_sec=refresh_sec)
               
                with trading_tab:
                    symbols = QUEEN['heartbeat'].get('active_tickers')
                    symbols = ['SPY'] if len(symbols) == 0 else symbols
                    queen_orders = QUEEN['queen_orders']
                    if 'orders' in st.session_state and st.session_state['orders']:
                        if type(revrec.get('waveview')) != pd.core.frame.DataFrame:
                            st.error("PENDING QUEEN")
                        else:
                            # with st.expander("Star Grid :sparkles:", True):
                            refresh_sec = 8 if seconds_to_market_close > 0 and mkhrs == 'open' else 0
                            refresh_sec = 23 if 'sneak_peak' in st.session_state and st.session_state['sneak_peak'] else refresh_sec
                            wave_grid(revrec=revrec, symbols=symbols, ip_address=ip_address, key=f'{"wb"}{symbols}{"orders"}', refresh_sec=refresh_sec)

                with order_tab:
                    refresh_sec = 8 if seconds_to_market_close > 0 and mkhrs == 'open' else None
                    refresh_sec = 23 if 'sneak_peak' in st.session_state and st.session_state['sneak_peak'] else refresh_sec
                    order_grid(KING, queen_orders, ip_address)

                # with charts_tab:
                #     refresh_sec = 8 if seconds_to_market_close > 0 and mkhrs == 'open' else 0
                #     refresh_sec = 23 if 'sneak_peak' in st.session_state and st.session_state['sneak_peak'] else refresh_sec

                #     cust_graph(username=KING['users_allowed_queen_emailname__db'].get(client_user),
                #                 prod=prod,
                #                 api=f'{ip_address}/api/data/symbol_graph',
                #                 x_axis='timestamp_est',
                #                 y_axis=symbols_unique_color(['SPY', 'SPY vwap', 'QQQ', 'QQQ vwap']),
                #                 theme_options={
                #                     'backgroundColor': k_colors.get('default_background_color'),
                #                     'main_title': '',   # '' for none
                #                     'x_axis_title': '',
                #                     'grid_color': default_text_color,
                #                     "showInLegend": True,
                #                     "showInLegendPerLine": True,
                #                 },
                #                 refresh_sec=refresh_sec,
                #                 refresh_button=True,
                #                 graph_height=300,
                #                 symbols=['SPY', 'QQQ'],
                #                 )
                #     # with cols[1]:
                #         # with st.expander("Wave Race :ocean:", True):
                #     refresh_sec = 8 if seconds_to_market_close > 0 and mkhrs == 'open' else 0
                #     refresh_sec = 23 if 'sneak_peak' in st.session_state and st.session_state['sneak_peak'] else refresh_sec
                #     custom_graph_ttf_qcp(prod, KING, client_user, QUEEN_KING, refresh_sec, ip_address)

                with board_tab:
                    
                    chess_board_admin = st.toggle("Swarm Board", False, key='chess_board_m') if admin else False
                    
                    chess_board = st.toggle("Trading Board", False, key='chess_board')
                    
                    if 'chess_board' in st.session_state and st.session_state['chess_board'] == True:
                        themes = list(pollen_themes(KING).keys())

                        if chess_board_admin:
                            QB_workerbees(QUEENBEE=QUEENBEE, admin=admin)
                        else:
                            if chess_board:
                                chessboard(revrec=revrec, QUEEN_KING=QUEEN_KING, ticker_allowed=ticker_allowed, themes=themes, admin=False)


                        # if tab_name == 'waves':
                        #     if 'waves' in st.session_state and st.session_state['waves'] == True:
                        #         with st.expander("wave stories"):
                        #             ticker_option = st.selectbox("ticker", options=tickers_avail)
                        #             frame_option = st.selectbox("frame", options=KING['star_times'])
                        #             show_waves(STORY_bee=STORY_bee, ticker_option=ticker_option, frame_option=frame_option)
                        #         with st.expander('waves', True):
                        #             # hc.option_bar(option_definition=pq_buttons.get('charts_option_data'),title='Waves', key='waves_toggle', horizontal_orientation=True) #,override_theme=over_theme,font_styling=font_fmt,horizontal_orientation=True)
                        #             queen_wavestories(QUEEN, STORY_bee, POLLENSTORY, tickers_avail)
                        #         with st.expander('STORY_bee'):
                        #             st.write(STORY_bee['SPY_1Minute_1Day']['story'])

                        # if tab_name == 'workerbees':
                        #     if 'workerbees' in st.session_state and st.session_state['workerbees'] == True:
                        #         st.write("waves")

                        # if tab_name == 'charts':
                        #     if 'charts' in st.session_state and st.session_state['charts'] == True:
                        #         with st.expander("charts", True):
                        #             advanced_charts()






                
                
                
                """ Bottom Page """
                cols = st.columns(2)
                with cols[0]:
                    cust_graph(username=KING['users_allowed_queen_emailname__db'].get(client_user),
                                prod=prod,
                                api=f'{ip_address}/api/data/symbol_graph',
                                x_axis='timestamp_est',
                                y_axis=symbols_unique_color(['SPY', 'SPY vwap', 'QQQ', 'QQQ vwap']),
                                theme_options={
                                    'backgroundColor': k_colors.get('default_background_color'),
                                    'main_title': '',   # '' for none
                                    'x_axis_title': '',
                                    'grid_color': default_text_color,
                                    "showInLegend": True,
                                    "showInLegendPerLine": True,
                                },
                                refresh_sec=refresh_sec,
                                refresh_button=True,
                                graph_height=250,
                                symbols=['SPY', 'QQQ'],
                                )
                with cols[1]:
                    # with st.expander("Wave Race :ocean:", True):
                    refresh_sec = 8 if seconds_to_market_close > 0 and mkhrs == 'open' else 0
                    refresh_sec = 23 if 'sneak_peak' in st.session_state and st.session_state['sneak_peak'] else refresh_sec
                    custom_graph_ttf_qcp(prod, KING, client_user, QUEEN_KING, refresh_sec, ip_address, graph_height=250)

        ##### END ####
    except Exception as e:
        print('queensconscience', print_line_of_error(e))

if __name__ == '__main__':
    queens_conscience(None, None, None, None, None, None, None)