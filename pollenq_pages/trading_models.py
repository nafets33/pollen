
import pandas as pd
import os
import sys
import pandas as pd
import numpy as np
import datetime
import pytz
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from itertools import islice
from PIL import Image
from dotenv import load_dotenv

import streamlit as st
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode, JsCode
from streamlit_extras.stoggle import stoggle
from streamlit_extras.switch_page_button import switch_page
import time
import os
import sqlite3
import time
from custom_button import cust_Button

from polleq_app_auth import signin_main
# import requests
# from requests.auth import HTTPBasicAuth
from chess_piece.app_hive import create_AppRequest_package, standard_AGgrid, create_wave_chart_all, create_slope_chart, create_wave_chart_single, create_wave_chart, create_guage_chart, create_main_macd_chart, page_session_state__cleanUp, trigger_airflow_dag, send_email, queen__account_keys, progress_bar, queen_order_flow, mark_down_text, click_button_grid, nested_grid, mark_down_text, page_line_seperator, write_flying_bee, hexagon_gif, local_gif, flying_bee_gif, pollen__story
from chess_piece.king import menu_bar_selection, return_all_client_users__db, kingdom__grace_to_find_a_Queen, return_QUEENs__symbols_data, hive_master_root, streamlit_config_colors, local__filepaths_misc, print_line_of_error
from chess_piece.queen_hive import init_pollen_dbs, init_qcp, return_alpaca_user_apiKeys, return_queen_controls, return_STORYbee_trigbees, add_key_to_app, add_key_to_QUEEN, refresh_account_info, generate_TradingModel, stars, analyze_waves, story_view, return_alpc_portolio, ReadPickleData, pollen_themes, PickleData, return_timestamp_string, init_logging
from ozz.ozz_bee import send_ozz_call
from chat_bot import ozz_bot
# from tqdm import tqdm
# from collections import defaultdict
import ipdb
# import matplotlib.pyplot as plt
# import base64
# from random import randint
load_dotenv()
est = pytz.timezone("US/Eastern")
utc = pytz.timezone('UTC')


pd.options.mode.chained_assignment = None

scriptname = os.path.basename(__file__)
queens_chess_piece = os.path.basename(__file__)


page = 'Trading_Models'

def trading_models():
    # ###### GLOBAL # ######
    ARCHIVE_queenorder = 'archived'
    active_order_state_list = ['running', 'running_close', 'submitted', 'error', 'pending', 'completed', 'completed_alpaca', 'running_open', 'archived_bee']
    active_queen_order_states = ['submitted', 'accetped', 'pending', 'running', 'running_close', 'running_open']
    CLOSED_queenorders = ['running_close', 'completed', 'completed_alpaca']
    RUNNING_Orders = ['running', 'running_open']
    RUNNING_CLOSE_Orders = ['running_close']

    # crypto
    crypto_currency_symbols = ['BTCUSD', 'ETHUSD', 'BTC/USD', 'ETH/USD']
    crypto_symbols__tickers_avail = ['BTCUSD', 'ETHUSD']

    main_root = hive_master_root() # os.getcwd()  # hive root

    # images
    MISC = local__filepaths_misc()
    jpg_root = MISC['jpg_root']
    bee_image = MISC['bee_image']
    castle_png = MISC['castle_png']
    bishop_png = MISC['bishop_png']
    queen_png = MISC['queen_png']
    knight_png = MISC['knight_png']
    mainpage_bee_png = MISC['mainpage_bee_png']
    floating_queen_gif = MISC['floating_queen_gif']
    chess_board__gif = MISC['chess_board__gif']
    bee_power_image = MISC['bee_power_image']
    hex_image = MISC['hex_image']
    hive_image = MISC['hive_image']
    queen_image = MISC['queen_image']
    queen_angel_image = MISC['queen_angel_image']
    flyingbee_gif_path = MISC['flyingbee_gif_path']
    flyingbee_grey_gif_path = MISC['flyingbee_grey_gif_path']
    bitcoin_gif = MISC['bitcoin_gif']
    power_gif = MISC['power_gif']
    uparrow_gif = MISC['uparrow_gif']
    learningwalk_bee = MISC['learningwalk_bee']
    queen_flair_gif = MISC['queen_flair_gif']
    chess_piece_queen = MISC['chess_piece_queen']
    runaway_bee_gif = MISC['runaway_bee_gif']
    queen_crown_url = MISC['queen_crown_url']
    pawn_png_url = MISC['pawn_png_url']

    # hexagon_loop = MISC['hexagon_loop']
    # purple_heartbeat_gif = MISC['purple_heartbeat_gif'] MISC.get('puprple')

    moving_ticker_gif = MISC['moving_ticker_gif']
    # heart_bee_gif = MISC['heart_bee_gif']

    learningwalk_bee = Image.open(learningwalk_bee)
    page_icon = Image.open(bee_image)

    ##### STREAMLIT ###
    k_colors = streamlit_config_colors()
    default_text_color = k_colors['default_text_color'] # = '#59490A'
    default_font = k_colors['default_font'] # = "sans serif"
    default_yellow_color = k_colors['default_yellow_color'] # = '#C5B743'
    
    with st.spinner("News Headlines about Trading Models"):
        # prod_name = "LIVE" if st.session_state['production'] else "Sandbox"    
        # prod_name_oppiste = "Sandbox" if st.session_state['production']  else "LIVE"  
        # menu_id = menu_bar_selection(host='queen', prod_name_oppiste=prod_name_oppiste, prod_name=prod_name, prod=st.session_state['production'], key='queen') 

        # if menu_id == 'pollenq':
        #     st.session_state['menu_id'] = menu_id
        #     st.session_state['menu_id_name'] = menu_id
        #     switch_page('pollenq')

        # signin_main(page='QueensConscience')
        
        # progress_bar(value=89)  ## show user completion of user flow interaction

        # return page last visited 
        sneak_peak = False
        if 'sneak_peak' in st.session_state and st.session_state['sneak_peak'] == True:
            sneak_peak = True
            st.session_state['production'] = True
            st.session_state['username'] = 'stefanstapinski@gmail.com'
            st.session_state['authorized_user'] = False
            st.session_state['db_root'] = os.path.join(main_root, 'db')
            st.info("Welcome and Watch A QueenBot in Action")
                    
            init_pollen_dbs(db_root=st.session_state['db_root'], prod=True, queens_chess_piece='queen', queenKING=True)

        
        elif st.session_state['authentication_status'] != True:
            st.write(st.session_state['authentication_status'])
            st.error("You Need to Log In to pollenq")
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

        db_root = st.session_state['db_root']
        prod, admin, prod_name = st.session_state['production'], st.session_state['admin'], st.session_state['prod_name']

        authorized_user = st.session_state['authorized_user']
        client_user = st.session_state["username"]
        # st.write("*", client_user)
        
        cols = st.columns((4,8,4))
        if prod:
            with cols[1]:
                # st.warning("LIVE ENVIORMENT The RealWorld")
                mark_down_text(text='LIVE', fontsize='23', align='left', color="Green", sidebar=True)
                flying_bee_gif(sidebar=True)

        else:
            with cols[1]:
                # st.info("SandBox")
                mark_down_text(text='SandBox', fontsize='23', align='left', color="Red", sidebar=True)
                local_gif(gif_path=flyingbee_grey_gif_path, sidebar=True)
        
        PB_QUEEN_Pickle = st.session_state['PB_QUEEN_Pickle'] 
        PB_App_Pickle = st.session_state['PB_App_Pickle'] 
        PB_Orders_Pickle = st.session_state['PB_Orders_Pickle'] 
        PB_queen_Archives_Pickle = st.session_state['PB_queen_Archives_Pickle']
        PB_QUEENsHeart_PICKLE = st.session_state['PB_QUEENsHeart_PICKLE']
        PB_KING_Pickle = st.session_state['PB_KING_Pickle']


        QUEEN_KING = ReadPickleData(pickle_file=PB_App_Pickle)    
        KING = ReadPickleData(pickle_file=PB_KING_Pickle)
        pollen_theme = pollen_themes(KING=KING)
        # QUEEN Databases
        QUEEN_KING['source'] = PB_App_Pickle
        QUEEN = ReadPickleData(PB_QUEEN_Pickle)
        # ORDERS = ReadPickleData(PB_Orders_Pickle)
        # QUEENsHeart = ReadPickleData(PB_QUEENsHeart_PICKLE)


        if st.session_state['authorized_user']:
            APP_req = add_key_to_app(QUEEN_KING)
            QUEEN_KING = APP_req['QUEEN_KING']
            if APP_req['update']:
                PickleData(PB_App_Pickle, QUEEN_KING)

            # add new keys
            QUEEN_req = add_key_to_QUEEN(QUEEN=QUEEN, queens_chess_piece=queens_chess_piece)
            if QUEEN_req['update']:
                QUEEN = QUEEN_req['QUEEN']
                PickleData(PB_QUEEN_Pickle, QUEEN)


        if st.session_state['authorized_user'] == False and sneak_peak == False:
            cols = st.columns(2)
            with cols[0]:
                st.info("You Don't have a QueenTraderBot yet! Need authorization, Please contact pollenq.queen@gmail.com or click the button below to send a Request")
            with cols[1]:
                st.info("Below is a Preview")
            client_user_wants_a_queen = st.button("Yes I want a Queen!")
            if client_user_wants_a_queen:
                st.session_state['init_queen_request'] = True
                if 'init_queen_request' in st.session_state:
                    QUEEN_KING['init_queen_request'] = {'timestamp_est': datetime.datetime.now(est)}
                    PickleData(PB_App_Pickle, QUEEN_KING)
                    send_email(recipient=os.environ('pollenq_gmail'), subject="RequestingQueen", body=f'{st.session_state["username"]} Asking for a Queen')
                    st.success("Hive Master Notified and You should receive contact soon")



        def chunk(it, size):
            it = iter(it)
            return iter(lambda: tuple(islice(it, size)), ())



        def return_image_upon_save(title="Saved", width=33, gif=power_gif):
            local_gif(gif_path=gif)
            st.success(title)


        def update_QueenControls(QUEEN_KING, control_option, theme_list, tickers_avail):
            theme_desc = {'nuetral': ' follows basic model wave patterns',
                        'strong_risk': ' defaults to high power trades',
                        'star__storywave': ' follows symbols each day changes and adjusts order rules based on latest data'}
            
            if control_option.lower() == 'theme':
                with st.form("Update Control"):
                    cols = st.columns((1,3))
                    with cols[0]:
                        st.info("Set your Risk Theme")
                    with cols[0]:
                        theme_option = st.selectbox(label='set theme', options=theme_list, index=theme_list.index('nuetral'))
                    with cols[1]:
                        # st.warning(f'Theme: {theme_option}')
                        ep = st.empty()
                    with cols[1]:
                        st.warning(f'Theme: {theme_option}{theme_desc[theme_option]}')

                    save_button = st.form_submit_button("Save")
                    if save_button:
                        QUEEN_KING['theme'] = theme_option
                        QUEEN_KING['last_app_update'] = datetime.datetime.now()
                        PickleData(pickle_file=PB_App_Pickle, data_to_store=QUEEN_KING)
                        return_image_upon_save(title="Theme saved")
                return True

            elif control_option.lower() == 'symbols_stars_tradingmodel':
                # add: ticker_family, short position and macd/hist story 
                # queen__write_active_symbols(QUEEN_KING=QUEEN_KING)
                cols = st.columns((1,4))
                with cols[0]:
                    saved_avail = list(QUEEN_KING['saved_trading_models'].keys()) + ['select']
                    saved_model_ticker = st.selectbox("View Saved Model", options=saved_avail, index=saved_avail.index('select'), help="This will display Saved Model")
                page_line_seperator(height='1')

                # mark_down_text(color='Black', text='Ticker Model')
                if saved_model_ticker != 'select':
                    title = f'{"Viewing a Saved Not active Ticker Model"}'
                else:
                    title = "Current Ticker Model"
                
                st.header(title)
                
                cols = st.columns(4)
                with cols[0]:
                    # tickers_avail = list(QUEEN_KING['king_controls_queen'][control_option].keys())
                    ticker_option_qc = st.selectbox("Symbol", tickers_avail, index=tickers_avail.index(["SPY" if "SPY" in tickers_avail else tickers_avail[0]][0]))

                    # QUEEN_KING = add_trading_model(PB_APP_Pickle=PB_App_Pickle, QUEEN_KING=QUEEN_KING, ticker=ticker_option_qc)
                

                if saved_model_ticker != 'select':
                    st.info("You Are Viewing Saved Model")
                    trading_model = QUEEN_KING['saved_trading_models'][saved_model_ticker]
                else:
                    trading_model = QUEEN_KING['king_controls_queen'][control_option][ticker_option_qc]
                
                star_avail = list(trading_model['stars_kings_order_rules'].keys())
                trigbees_avail = list(trading_model['trigbees'].keys())
                blocktime_avail = list(trading_model['time_blocks'].keys())
                
                with cols[1]:
                    star_option_qc = st.selectbox("Star", star_avail, index=star_avail.index(["1Minute_1Day" if "1Minute_1Day" in star_avail else star_avail[0]][0]))
                with cols[2]:
                    trigbee_sel = st.selectbox("Trigbee", trigbees_avail, index=trigbees_avail.index(["buy_cross-0" if "buy_cross-0" in trigbees_avail else trigbees_avail[0]][0]))
                with cols[3]:
                    # wave_blocks_option = st.selectbox("Block Time", KING['waveBlocktimes'])
                    wave_blocks_option = st.selectbox("BlockTime", blocktime_avail, index=blocktime_avail.index(["morning_9-11" if "morning_9-11" in blocktime_avail else blocktime_avail[0]][0]))
                    
                trading_model__star = trading_model['stars_kings_order_rules'][star_option_qc]



                ticker_model_level_1 = {
                        'portforlio_weight_ask': {'type': 'portforlio_weight_ask'},
                        'QueenBeeTrader': {'type': None}, # not allowed to change
                        'status': {'type': 'status', 'list': ['active', 'not_active']},
                        'buyingpower_allocation_LongTerm': {'type': 'numberslider', 'min': 0, 'max': 1},
                        'buyingpower_allocation_ShortTerm': {'type': None}, # returns opposite of LongTerm
                        'index_long_X': {'type': 'index_long_X', 'list': ['1X', '2X', '3X']},
                        'index_inverse_X': {'type': 'index_inverse_X', 'list': ['1X', '2X', '3X']},
                        'total_budget': {'type': 'total_budget'},
                        'max_single_trade_amount': {'type': 'number'},
                        'allow_for_margin': {'type': 'allow_for_margin'}, 
                        'buy_ONLY_by_accept_from_QueenBeeTrader': {'type': 'buy_ONLY_by_accept_from_QueenBeeTrader'},
                        'trading_model_name': {'type': None}, # not allowed to change
                        'portfolio_name': {'type': None}, # not allowed to change
                        'trigbees': {'type': 'trigbees', 'list': ['active', 'not_active']},
                        'time_blocks': {'type': 'time_blocks', 'list': ['active', 'not_active']},
                        'power_rangers': {'type': 'power_rangers', 'list': ['active', 'not_active']},
                        # 'power_rangers_power': {'type': 'power_rangers_power'},
                        'kings_order_rules': {'type': 'PENDING'},
                        'stars_kings_order_rules': {'type': 'stars_kings_order_rules'},
                }

                star_level_2 = {
                    # 'stars': ["1Minute_1Day", "5Minute_5Day", "30Minute_1Month", "1Hour_3Month", "2Hour_6Month", "1Day_1Year"], 
                    'trade_using_limits': {'name': 'trade_using_limits', 'type':'bool', 'var': None},
                    'stagger_profits': {'name': 'stagger_profits', 'type':'number', 'var': None},
                    'total_budget': {'name': 'total_budget', 'type':'number', 'var': None},
                    'buyingpower_allocation_LongTerm': {'name': 'buyingpower_allocation_LongTerm', 'type':'number', 'var': None},
                    'buyingpower_allocation_ShortTerm': {'name': 'buyingpower_allocation_ShortTerm', 'type':'number', 'var': None},
                    'power_rangers': ["1Minute_1Day", "5Minute_5Day", "30Minute_1Month", "1Hour_3Month", "2Hour_6Month", "1Day_1Year"],
                    'trigbees': None,
        }

                star_trigbee_mapping = {
                    'status': 'checkbox',
                }
                    
                kor_option_mapping = {
                'take_profit': 'number',
                'sellout': 'number',
                # 'status': 'checkbox',
                'trade_using_limits': 'checkbox',
                'doubledown_timeduration': 'number',
                'max_profit_waveDeviation': 'number',
                'max_profit_waveDeviation_timeduration': 'number',
                'timeduration': 'number',
                'sell_trigbee_trigger': 'checkbox',
                'stagger_profits': 'checkbox',
                'scalp_profits': 'checkbox',
                'scalp_profits_timeduration': 'number',
                'stagger_profits_tiers': 'number',
                'limitprice_decay_timeduration': 'number',
                'take_profit_in_vwap_deviation_range': 'take_profit_in_vwap_deviation_range',
                'skip_sell_trigbee_distance_frequency': 'skip_sell_trigbee_distance_frequency', # skip sell signal if frequency of last sell signal was X distance >> timeperiod over value, 1m: if sell was 1 story index ago
                'ignore_trigbee_at_power': 'ignore_trigbee_at_power',
                'ignore_trigbee_in_vwap_range': 'ignore_trigbee_in_vwap_range',
                'ignore_trigbee_in_macdstory_tier': 'ignore_trigbee_in_macdstory_tier',
                'ignore_trigbee_in_histstory_tier': 'ignore_trigbee_in_histstory_tier',
                }
                # take_profit_in_vwap_deviation_range={'low_range': -.05, 'high_range': .05}



                with st.form('trading model form'):

                    # trigbee_update = trading_model__star['trigbees'][trigbee_sel]
                    king_order_rules_update = trading_model__star['trigbees'][trigbee_sel][wave_blocks_option]
                    # # st.write('tic level', QUEEN['queen_controls'][control_option][ticker_option_qc].keys())
                    st.subheader("Settings")
                    with st.expander(f'{ticker_option_qc} Global Settings'):
                        cols = st.columns((1,1,1,1,1))
                        
                        # all ticker settings
                        for kor_option, kor_v in trading_model.items():
                            if kor_option in ticker_model_level_1.keys():
                                item_type = ticker_model_level_1[kor_option]['type']
                                # st.write(kor_option, kor_v, item_type)
                                if item_type == None:
                                    continue # not allowed edit

                                elif kor_option == 'status':
                                    with cols[0]:
                                        item_val = ticker_model_level_1[kor_option]['list']
                                        trading_model[kor_option] = st.selectbox(label=f'{ticker_option_qc}{"_"}{kor_option}', options=item_val, index=item_val.index(kor_v), key=f'{ticker_option_qc}{"_"}{kor_option}')
                            
                                elif kor_option == 'total_budget':
                                    with cols[1]:
                                        trading_model[kor_option] = st.number_input(label=f'{ticker_option_qc}{"_"}{kor_option}', value=kor_v, key=f'{ticker_option_qc}{"_"}{kor_option}')

                                elif kor_option == 'max_single_trade_amount':
                                    with cols[1]:
                                        trading_model[kor_option] = st.number_input(label=f'{ticker_option_qc}{"_"}{kor_option}', value=kor_v, key=f'{ticker_option_qc}{"_"}{kor_option}')

                                elif kor_option == 'allow_for_margin':
                                    with cols[0]:
                                        trading_model[kor_option] = st.checkbox(label=f'{ticker_option_qc}{"_"}{kor_option}', value=kor_v, key=f'{ticker_option_qc}{"_"}{kor_option}')
                                
                                elif kor_option == 'buy_ONLY_by_accept_from_QueenBeeTrader':
                                    with cols[1]:
                                        trading_model[kor_option] = st.checkbox(label=f'{ticker_option_qc}{"_"}{kor_option}', value=kor_v, key=f'{ticker_option_qc}{"_"}{kor_option}')

                                elif kor_option == 'index_long_X':
                                    with cols[0]:
                                        item_val = ticker_model_level_1[kor_option]['list']
                                        trading_model[kor_option] = st.selectbox(label=f'{ticker_option_qc}{"_"}{kor_option}', options=item_val, index=item_val.index(kor_v), key=f'{ticker_option_qc}{"_"}{kor_option}')
                                elif kor_option == 'index_inverse_X':
                                    with cols[0]:
                                        item_val = ticker_model_level_1[kor_option]['list']
                                        trading_model[kor_option] = st.selectbox(label=f'{ticker_option_qc}{"_"}{kor_option}', options=item_val, index=item_val.index(kor_v), key=f'{ticker_option_qc}{"_"}{kor_option}')
                                
                                elif kor_option == 'portforlio_weight_ask':
                                    with cols[0]:
                                        trading_model[kor_option] = st.slider(label=f'{"portforlio_weight_ask"}', key='portforlio_weight_ask', min_value=float(0.0), max_value=float(1.0), value=float(kor_v), help="Allocation to Strategy by portfolio")

                                elif kor_option == 'trigbees':
                                    with cols[4]:
                                        st.write("Activate Trigbees")
                                        item_val = ticker_model_level_1[kor_option]['list']
                                        for trigbee, trigactive in trading_model['trigbees'].items():
                                            trading_model[kor_option][trigbee] = st.checkbox(label=f'{trigbee}', value=trigactive, key=f'{ticker_option_qc}{"_"}{kor_option}{trigbee}')

                                elif kor_option == 'time_blocks':
                                    with cols[2]:
                                        st.write("Trade Following Time Blocks")
                                        for wave_block, waveactive in trading_model['time_blocks'].items():
                                            trading_model[kor_option][wave_block] = st.checkbox(label=f'{wave_block}', value=waveactive, key=f'{ticker_option_qc}{"_"}{kor_option}{wave_block}')
                                
                                elif kor_option == 'power_rangers':
                                    with cols[3]:
                                        st.write('Trade Following Time Frames')
                                        for power_ranger, pr_active in trading_model['power_rangers'].items():
                                            trading_model[kor_option][power_ranger] = st.checkbox(label=f'{power_ranger}', value=pr_active, key=f'{ticker_option_qc}{"_"}{kor_option}{power_ranger}')
                                
                                elif kor_option == 'buyingpower_allocation_LongTerm':
                                    with cols[0]:
                                        long = st.slider(label=f'{"Long Term Allocation"}', key='tic_long', min_value=float(0.0), max_value=float(1.0), value=float(trading_model['buyingpower_allocation_LongTerm']), help="Set the Length of the trades, lower number means short trade times")
                                        short = st.slider(label=f'{"Short Term Allocation"}', key='tic_short', min_value=float(0.0), max_value=float(1.0), value=float(trading_model['buyingpower_allocation_ShortTerm']), help="Set the Length of the trades, lower number means short trade times")

                                        if long > short:
                                            long = long
                                        else:
                                            short = 1 - long
                                        
                                        trading_model['buyingpower_allocation_ShortTerm'] = short
                                        trading_model["buyingpower_allocation_LongTerm"] = long
                                else:
                                    st.write("not accounted ", kor_option)
                            else:
                                # trading_model[kor_option] = kor_v
                                st.write("missing ", kor_option)

                    with st.expander(f'{star_option_qc}'):
                        # st.write([i for i in star_level_2.keys() if i ])
                        st.info("Set the Stars Gravity; allocation of power on the set of stars your Symbol's choice")
                        cols = st.columns(3)
                        
                        for item_control, itc_vars in star_level_2.items():
                            if item_control not in QUEEN_KING['king_controls_queen'][control_option][ticker_option_qc]['stars_kings_order_rules'][star_option_qc].keys():
                                st.write(f'{item_control} not in scope')
                                continue
                        

                        with cols[0]: # total_budget
                            trading_model['stars_kings_order_rules'][star_option_qc]['total_budget'] = st.number_input(label='$Budget', value=float(trading_model['stars_kings_order_rules'][star_option_qc]['total_budget']))

                        with cols[0]: # Allocation
                            long = st.slider(label=f'{"Long Term Allocation"}', key='trigbee_long', min_value=float(0.0), max_value=float(1.0), value=float(trading_model__star['buyingpower_allocation_LongTerm']), help="Set the Length of the trades, lower number means shorter trade times")
                            short = st.slider(label=f'{"Short Term Allocation"}', key='trigbee_short', min_value=float(0.0), max_value=float(1.0), value=float(trading_model__star['buyingpower_allocation_ShortTerm']), help="Set the Length of the trades, lower number means shorter trade times")

                            if long > short:
                                long = long
                            else:
                                short = 1 - long
                            
                            trading_model['stars_kings_order_rules'][star_option_qc]['buyingpower_allocation_ShortTerm'] = short
                            trading_model['stars_kings_order_rules'][star_option_qc]["buyingpower_allocation_LongTerm"] = long
                        
                        with cols[1]: # index_long_X
                            trading_model['stars_kings_order_rules'][star_option_qc]['index_long_X'] = st.selectbox("Long X Weight", options=['1X', '2X', '3X'], index=['1X', '2X', '3X'].index(f'{trading_model["stars_kings_order_rules"][star_option_qc]["index_long_X"]}'))

                        with cols[1]: # index_inverse_X
                            trading_model['stars_kings_order_rules'][star_option_qc]['index_inverse_X'] = st.selectbox("Short X Weight", options=['1X', '2X', '3X'], index=['1X', '2X', '3X'].index(f'{trading_model["stars_kings_order_rules"][star_option_qc]["index_inverse_X"]}'))                    
                        
                        with cols[2]: # trade_using_limits
                            trading_model['stars_kings_order_rules'][star_option_qc]['trade_using_limits'] = st.checkbox("trade_using_limits", value=trading_model['stars_kings_order_rules'][star_option_qc]['trade_using_limits'])
                        
                        page_line_seperator(height='1')
                        cols = st.columns((1,3,1))
                        with cols[1]:
                            st.write('Star Allocation Power')
                        
                        # with cols[2]:
                        #     st.write('Gravity')
                        
                        for power_ranger, pr_active in trading_model['stars_kings_order_rules'][star_option_qc]['power_rangers'].items():
                            # st.write(power_ranger, pr_active)
                            with cols[1]:
                                trading_model['stars_kings_order_rules'][star_option_qc]['power_rangers'][power_ranger] = st.slider(label=f'{power_ranger}', min_value=float(0.0), max_value=float(1.0), value=float(pr_active), key=f'{star_option_qc}{power_ranger}')
                            
                    with st.expander(f'{wave_blocks_option}'):
                        # mark_down_text(text=f'{trigbee_sel}{" >>> "}{wave_blocks_option}')
                        # st.write(f'{wave_blocks_option} >>> WaveBlocktime KingOrderRules 4')
                        cols = st.columns((1, 1, 2, 3))

                        for kor_option, kor_v in king_order_rules_update.items():
                            if kor_option in kor_option_mapping.keys():
                                st_func = kor_option_mapping[kor_option]
                                if kor_option == 'take_profit_in_vwap_deviation_range':
                                    # with cols[0]:
                                    #     st.write("vwap_deviation_range")
                                    with cols[0]:
                                        low = st.number_input(label=f'{"vwap_deviation_low"}', value=kor_v['low_range'], key=f'{trigbee_sel}{"_"}{wave_blocks_option}{"_"}{"low_range"}', help="take_profit_in_vwap_deviation_range")
                                    with cols[1]:
                                        high = st.number_input(label=f'{"vwap_deviation_high"}', value=kor_v['high_range'], key=f'{trigbee_sel}{"_"}{wave_blocks_option}{"_"}{"high_range"}')
                                        
                                    king_order_rules_update[kor_option] = {'high_range': high, "low_range": low}
                                
                                if kor_option == 'ignore_trigbee_in_vwap_range':
                                    # with cols[0]:
                                    #     st.write("ignore_trigbee_in_vwap_range")
                                    with cols[0]:
                                        low = st.number_input(label=f'{"ignore_vwap_low"}', value=kor_v['low_range'], key=f'{trigbee_sel}{"_"}{wave_blocks_option}{"_"}{"vwap_low_range"}')
                                    with cols[1]:
                                        high = st.number_input(label=f'{"ignore_vwap_high"}', value=kor_v['high_range'], key=f'{trigbee_sel}{"_"}{wave_blocks_option}{"_"}{"vwap_high_range"}')
                                    king_order_rules_update[kor_option] = {'high_range': high, "low_range": low}

                                if kor_option == 'skip_sell_trigbee_distance_frequency':
                                    with cols[3]:
                                        king_order_rules_update[kor_option] = st.slider(label=f'{kor_option}', key=f'{trigbee_sel}{"_"}{wave_blocks_option}{"_"}{kor_option}', min_value=float(0.0), max_value=float(3.0), value=float(kor_v), help="Skip a sellcross trigger frequency")
                                
                                if kor_option == 'ignore_trigbee_at_power':
                                    with cols[3]:
                                        king_order_rules_update[kor_option] = st.slider(label=f'{kor_option}', key=f'{trigbee_sel}{"_"}{wave_blocks_option}{"_"}{kor_option}', min_value=float(0.0), max_value=float(3.0), value=float(kor_v), help="Trade Needs to be Powerful Enough as defined by the model allocation story")
                                                        
                                if st_func == 'checckbox':
                                    king_order_rules_update[kor_option] = st.checkbox(label=f'{kor_option}', value=kor_v, key=f'{trigbee_sel}{"_"}{wave_blocks_option}{"_"}{kor_option}')
                                elif st_func == 'number':
                                    king_order_rules_update[kor_option] = st.number_input(label=f'{kor_option}', value=kor_v, key=f'{trigbee_sel}{"_"}{wave_blocks_option}{"_"}{kor_option}')
                                elif st_func == 'text':
                                    king_order_rules_update[kor_option] = st.text_input(label=f'{kor_option}', value=kor_v, key=f'{trigbee_sel}{"_"}{wave_blocks_option}{"_"}{kor_option}')
                            
                            else:
                                # print('missing')
                                st.write("missing ", kor_option)
                                king_order_rules_update[kor_option] = kor_v

                    
                    #### TRADING MODEL ####
                    # Ticker Level 1
                    # Star Level 2
                    # trading_model = trading_model
                    
                    # Trigbees Level 3
                    # trading_model['stars_kings_order_rules'][star_option_qc]['trigbees'][trigbee_sel].update(trigbee_update)
                    # trading_model = trading_model
                    
                    # WaveBlock Time Levle 4 ## using all selections to change KingsOrderRules
                    trading_model['stars_kings_order_rules'][star_option_qc]['trigbees'][trigbee_sel][wave_blocks_option] = king_order_rules_update

                    cols = st.columns((1,1,1,1,3))
                    with cols[0]:
                        save_button_addranger = st.form_submit_button("Save Trading Model Settings")
                    with cols[1]:
                        savecopy_button_addranger = st.form_submit_button("Save Copy of Trading Model Settings")
                    with cols[2]:
                        replace_model_with_saved_selection = st.form_submit_button("replace model with saved selection")
                    with cols[3]:
                        refresh_to_theme = st.form_submit_button("Refresh Model To Current Theme")           

                    if save_button_addranger:
                        app_req = create_AppRequest_package(request_name='trading_models_requests')
                        app_req['trading_model'] = trading_model
                        QUEEN_KING['trading_models_requests'].append(app_req)
                        QUEEN_KING['king_controls_queen'][control_option][ticker_option_qc] = trading_model
                        
                        PickleData(pickle_file=PB_App_Pickle, data_to_store=QUEEN_KING)
                        return_image_upon_save(title="Model Saved")
                    
                    elif savecopy_button_addranger:                        
                        QUEEN_KING['saved_trading_models'].update(trading_model)
                        PickleData(pickle_file=PB_App_Pickle, data_to_store=QUEEN_KING)
                        return_image_upon_save(title="Model Cpoy Saved")

                    elif replace_model_with_saved_selection:                        
                        app_req = create_AppRequest_package(request_name='trading_models_requests')
                        app_req['trading_model'] = trading_model
                        QUEEN_KING['trading_models_requests'].append(app_req)
                        QUEEN_KING['king_controls_queen'][control_option][ticker_option_qc] = trading_model
                        
                        PickleData(pickle_file=PB_App_Pickle, data_to_store=QUEEN_KING)
                        return_image_upon_save(title="Model Replaced With Saved Version")
                    elif refresh_to_theme:
                        QUEEN_KING = refresh_tickers_TradingModels(QUEEN_KING=QUEEN_KING, ticker=ticker_option_qc)
                        PickleData(pickle_file=PB_App_Pickle, data_to_store=QUEEN_KING)
                        return_image_upon_save(title=f'Model Refreshed to Theme: {QUEEN_KING["theme"]}')



                if st.button('show queens trading model'):
                    st.write(QUEEN_KING['king_controls_queen'][control_option][ticker_option_qc])
            else:
                st.write("PENDING WORK")
            

            return True 

        def clean_out_app_requests(QUEEN, QUEEN_KING, request_buckets):
            save = False
            for req_bucket in request_buckets:
                if req_bucket not in QUEEN_KING.keys():
                    st.write("Verison Missing DB: ", req_bucket)
                    continue
                for app_req in QUEEN_KING[req_bucket]:
                    if app_req['app_requests_id'] in QUEEN['app_requests__bucket']:
                        print("Quen Processed app req item")
                        archive_bucket = f'{req_bucket}{"_requests"}'
                        QUEEN_KING[req_bucket].remove(app_req)
                        QUEEN_KING[archive_bucket].append(app_req)
                        save = True
            if save:
                PickleData(pickle_file=PB_App_Pickle, data_to_store=QUEEN_KING)

      
        def add_trading_model(PB_APP_Pickle, QUEEN_KING, ticker, model='MACD', status='not_active', workerbee=False):
            trading_models = QUEEN_KING['king_controls_queen']['symbols_stars_TradingModel']
            confirmed_qcp = ['castle', 'bishop', 'knight', 'castle_coin']
            if ticker not in trading_models.keys():
                if workerbee in confirmed_qcp:
                    print(ticker, " Ticker Missing Trading Model Adding Default ", model)
                    # logging_log_message(msg=f'{ticker}{": added trading model: "}{model}')
                    # logging.info()
                    tradingmodel1 = generate_TradingModel(ticker=ticker, status=status)[model]
                    QUEEN_KING['king_controls_queen']['symbols_stars_TradingModel'].update(tradingmodel1)
                    PickleData(pickle_file=PB_APP_Pickle, data_to_store=QUEEN_KING)
                else:
                    tradingmodel1 = generate_TradingModel(ticker=ticker, status='not_active')[model]
                    QUEEN_KING['king_controls_queen']['symbols_stars_TradingModel'].update(tradingmodel1)
                    PickleData(pickle_file=PB_APP_Pickle, data_to_store=QUEEN_KING)

                return QUEEN_KING
            else:
                return QUEEN_KING

        
        def chunk_write_dictitems_in_row(chunk_list, max_n=10, write_type='checkbox', title="Active Models", groupby_qcp=False, info_type='buy'):
            # qcp_ticker_index = set_chess_pieces_symbols(QUEEN_KING=QUEEN_KING)['qcp_ticker_index']
            # if groupby_qcp:
            #     for qcp in set(qcp_ticker_index.values()):
            #         st.warning()
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
                                        st.warning(f'{ticker} {v}')
                                        local_gif(gif_path=uparrow_gif, height='23', width='23')
                                    else:
                                        st.info(f'{ticker} {v}')
                                    flying_bee_gif(width='43', height='40')
                                if write_type == 'pl_profits':
                                    st.write(ticker, v)
            except Exception as e:
                print(e, print_line_of_error())
            # else:
            #     cols = st.columns(len(chunk_list) + 1)
            #     with cols[0]:
            #         if write_type == 'info':
            #             flying_bee_gif(width='53', height='53')
            #         else:
            #             st.write(title)
            #     for idx, package in enumerate(chunk_list):
            #         for ticker, v in package.items():
            #         # ticker, value = package.items()
            #             with cols[idx + 1]:
            #                 if write_type == 'checkbox':
            #                     st.checkbox(ticker, v, key=f'{ticker}{v}')  ## add as quick save to turn off and on Model
            #                 if write_type == 'info':
            #                     if info_type == 'buy':
            #                         st.warning(f'{ticker} {v}')
            #                         local_gif(gif_path=uparrow_gif, height='23', width='23')
            #                     else:
            #                         st.info(f'{ticker} {v}')
            #                         flying_bee_gif(width='38', height='42')
            return True 
        
        def queen__write_active_symbols(QUEEN_KING):

            active_ticker_models = [{i: v['status']} for i, v in QUEEN_KING['king_controls_queen']['symbols_stars_TradingModel'].items() if v['status'] == 'active']
            chunk_write_dictitems_in_row(active_ticker_models)

            return True

        def refresh_tickers_TradingModels(QUEEN_KING, ticker):
            tradingmodel1 = generate_TradingModel(ticker=ticker, status='active')['MACD']
            QUEEN_KING['king_controls_queen']['symbols_stars_TradingModel'].update(tradingmodel1)
            return QUEEN_KING

        
        def page_tab_permission_denied(admin, st_stop=True):
            if admin == False:
                st.warning("permission denied you need a Queen to access")
                if st_stop:
                    st.info("Page Stopped")
                    st.stop()

        ########################################################
        ########################################################
        #############The Infinite Loop of Time #################
        ########################################################
        ########################################################
        ########################################################


        # """ if "__name__" == "__main__": """
        if st.session_state['admin']:
            with st.expander("ozz"):
                query = st.text_input('ozz call')
                if st.button("ozz"):
                    send_ozz_call(query=query)
            with st.sidebar:    
                OZZ = ozz_bot(api_key=os.environ.get("ozz_api_key"), username=st.session_state['username'])
        
        prod_keys_confirmed = QUEEN_KING['users_secrets']['prod_keys_confirmed']
        sandbox_keys_confirmed = QUEEN_KING['users_secrets']['sandbox_keys_confirmed']

        api = return_alpaca_user_apiKeys(QUEEN_KING=QUEEN_KING, authorized_user=authorized_user, prod=st.session_state['production'])
        
        try:
            api_failed = False
            snapshot = api.get_snapshot("SPY") # return_last_quote from snapshot
        except Exception as e:
            # requests.exceptions.HTTPError: 403 Client Error: Forbidden for url: https://data.alpaca.markets/v2/stocks/SPY/snapshot
            st.write("API Keys failed! You need to update, Please Go to your Alpaca Broker Account to Generate API Keys")
            # time.sleep(5)
            queen__account_keys(PB_App_Pickle=PB_App_Pickle, QUEEN_KING=QUEEN_KING, authorized_user=authorized_user, show_form=True) #EDRXZ Maever65teo
            api_failed = True

        if st.session_state['authorized_user']: ## MOVE THIS INTO pollenq?
            clean_out_app_requests(QUEEN=QUEEN, QUEEN_KING=QUEEN_KING, request_buckets=['subconscious', 'sell_orders'])
        

        # # if authorized_user: log type auth and none
        log_dir = os.path.join(db_root, 'logs')
        init_logging(queens_chess_piece=queens_chess_piece, db_root=db_root, prod=st.session_state['production'])


    try:

        today_day = datetime.datetime.now(est).day
        
        with st.spinner("TModel Ad2"):

            cols = st.columns((1,2,3))

            queen_tabs = ["Trading Models", "Themes", "Raw Model"]
            trading_models_tab, theme_tab, raw_model = st.tabs(queen_tabs)

            tickers_avail = list(QUEEN_KING['king_controls_queen']['symbols_stars_TradingModel'].keys())

            with trading_models_tab:
                queen__write_active_symbols(QUEEN_KING=QUEEN_KING)
                with cols[0]:
                    st.header("Select Control")
                with cols[1]:
                    theme_list = list(pollen_theme.keys())
                    contorls = list(QUEEN['queen_controls'].keys())
                    control_option = st.selectbox('control', contorls, index=contorls.index('theme'))
                with cols[2]:
                    st.image(MISC.get('mainpage_bee_png'), width=100)
                
                update_QueenControls(QUEEN_KING=QUEEN_KING, control_option=control_option, theme_list=theme_list, tickers_avail=tickers_avail)
            
            with raw_model:
                cols = st.columns(2)
                with cols[0]:
                    view_model = st.radio(
                        label="View Raw Model",
                        options=['no', 'yes'],key="raw_model",label_visibility='visible',horizontal=True)
                with cols[1]:
                    see_queen = st.radio(
                        label="See QUEEN",
                        options=['no', 'yes'],key="see_queen",label_visibility='visible',horizontal=True)
                
                if view_model == 'yes':
                    ticker_sel = st.selectbox('Tickers', tickers_avail)
                    if see_queen == 'yes':
                        trading_model = QUEEN['queen_controls']['symbols_stars_TradingModel'][ticker_sel]
                    else:
                        trading_model = QUEEN_KING['king_controls_queen']['symbols_stars_TradingModel'][ticker_sel]
                    
                    st.write(trading_model)


            page_line_seperator(color=default_yellow_color)

            
        page_session_state__cleanUp(page=page)

            
        st.session_state['host'] = 'trading_model'
        PickleData(PB_App_Pickle, QUEEN_KING)

        ##### END ####
    except Exception as e:
        print(e, print_line_of_error())
        # switch_page('pollenq')
if __name__ == '__main__':
    trading_models()