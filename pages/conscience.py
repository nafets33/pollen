import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import pytz
from itertools import islice
from PIL import Image
from dotenv import load_dotenv
import streamlit as st
import os
import copy
import hydralit_components as hc

from chess_piece.app_hive import return_image_upon_save, symbols_unique_color, custom_graph_ttf_qcp, create_ag_grid_column, download_df_as_CSV, show_waves, send_email, pollenq_button_source, standard_AGgrid, create_AppRequest_package, create_wave_chart_all, create_slope_chart, create_wave_chart_single, create_wave_chart, create_guage_chart, create_main_macd_chart,  queen_order_flow, mark_down_text, mark_down_text, page_line_seperator, local_gif, flying_bee_gif
from chess_piece.king import master_swarm_QUEENBEE, kingdom__global_vars, return_QUEENs__symbols_data, hive_master_root, streamlit_config_colors, local__filepaths_misc, print_line_of_error, ReadPickleData, PickleData
from chess_piece.queen_hive import star_names, return_queenking_board_symbols, sell_button_dict_items, buy_button_dict_items, hive_dates, return_market_hours, refresh_chess_board__revrec, generate_TradingModel, init_logging
# from pages.orders import order_grid

from custom_grid import st_custom_grid, GridOptionsBuilder
# from st_aggrid import AgGrid, GridUpdateMode, JsCode

from custom_graph_v1 import st_custom_graph

import ipdb


pd.options.mode.chained_assignment = None

scriptname = os.path.basename(__file__)
queens_chess_piece = os.path.basename(__file__)

page = 'QueensConscience'


main_root = hive_master_root() # os.getcwd()  # hive root
load_dotenv(os.path.join(main_root, ".env"))
est = pytz.timezone("US/Eastern")
utc = pytz.timezone('UTC')


def chunk(it, size):
    it = iter(it)
    return iter(lambda: tuple(islice(it, size)), ())

def clean_out_app_requests(QUEEN, QUEEN_KING, request_buckets):
    save = False
    for req_bucket in request_buckets:
        if req_bucket not in QUEEN_KING.keys():
            st.write("Verison Missing DB: ", req_bucket)
            continue
        for app_req in QUEEN_KING[req_bucket]:
            if app_req['app_requests_id'] in QUEEN['app_requests__bucket']:
                archive_bucket = f'{req_bucket}{"_requests"}'
                QUEEN_KING[req_bucket].remove(app_req)
                QUEEN_KING[archive_bucket].append(app_req)
                save = True
    if save:
        PickleData(pickle_file=QUEEN_KING.get('source'), data_to_store=QUEEN_KING, console="Cleared APP Requests")
    
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
                PickleData(pickle_file=QUEEN_KING.get('source'), data_to_store=QUEEN_KING)

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
        print_line_of_error()

    return True 


def queens_conscience(QUEENBEE, KING, QUEEN, QUEEN_KING, api, api_vars):

    # print("Conscience Page")

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

    ##### STREAMLIT ###
    k_colors = streamlit_config_colors()
    default_text_color = k_colors['default_text_color'] # = '#59490A'
    
    with st.spinner("Welcome to the QueensMind"):

        def wave_grid(revrec, symbols, ip_address, refresh_sec=8, key='default'):
            gb = GridOptionsBuilder.create()
            gb.configure_default_column(column_width=100, resizable=True, wrapText=False, wrapHeaderText=True, autoHeaderHeight=True, autoHeight=True, suppress_menu=False,filterable=True,sortable=True)            
            gb.configure_index('ticker_time_frame')
            gb.configure_theme('ag-theme-material')

            def config_cols():

                return {
                    # 'ticker_time_frame': {'initialWidth': 168,},
                        # 'symbol': {'headerName': 'Symbol', 'enableRowGroup':True, 'rowGroup': 'True'},
                        'ttf_grid_name': create_ag_grid_column(headerName='Star', width=148),
                        'current_profit': create_ag_grid_column(headerName='Curent Profit', initialWidth=89, type=["customNumberFormat", "numericColumn", "numberColumnFilter"], cellRenderer='agAnimateShowChangeCellRenderer', enableCellChangeFlash=True,),
                        'maxprofit': {'cellRenderer': 'agAnimateShowChangeCellRenderer','enableCellChangeFlash': True,
                                    "type": ["customNumberFormat", "numericColumn", "numberColumnFilter", ],},
                        
                        'long_at_play': {'headerName':'Long At Play', "type": ["customNumberFormat", "numericColumn", "numberColumnFilter", ],'initialWidth':123,},
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
                key=f'waves',
                return_type='waves',
                # kwargs from here
                api_key=os.environ.get("fastAPI_key"),
                prompt_message ="Buy Amount",
                prompt_field = "star", # "current_macd_tier",
                read_pollenstory = False,
                read_storybee = True,
                symbols=symbols,
                buttons=[
                        # {'button_name': None,
                        # 'button_api': f'{ip_address}/api/data/queen_buy_wave_orders',
                        # 'prompt_message': 'Buy Wave',
                        # 'prompt_field': 'macd_state',
                        # 'col_headername': 'macd_state',
                        # "col_header": "macd_state",
                        # "col_width": 133,
                        # "border_color": "green",
                        # # 'pinned': 'left',
                        # },

                        {'button_name': None, # this used to name the button
                        'button_api': f'{ip_address}/api/data/queen_buy_orders',
                        'prompt_message': 'Edit Buy',
                        'prompt_field': 'kors',
                        'col_headername': 'Buy Wave',
                        "col_header": "ticker_time_frame__budget", # button display
                        'col_width':125,
                        'pinned': 'left',
                        'prompt_order_rules': [i for i in buy_button_dict_items().keys()],
                        },
                        ],
                grid_height='350px',
                toggle_views = ["Queen", 'Buys', 'Sells', ] + star_names().keys() + ['King'],
            ) 

      
        def story_grid(client_user, ip_address, revrec, symbols, refresh_sec=8, key='default'):
            try:
                gb = GridOptionsBuilder.create()
                gb.configure_default_column(column_width=100, resizable=True,wrapText=False, wrapHeaderText=True, sortable=True, autoHeaderHeight=True, autoHeight=True, suppress_menu=False,filterable=True,)            
                gb.configure_index('symbol')
                gb.configure_theme('ag-theme-material')
                def story_grid_buttons():
                    buttons=[
                                {'button_name': None,
                                'button_api': f'{ip_address}/api/data/queen_buy_orders',
                                'prompt_message': 'Edit Buy',
                                'prompt_field': 'kors',
                                'col_headername': 'Re Allocate',
                                "col_header": "queens_suggested_buy",
                                "border_color": "green",
                                'col_width':135,
                                'sortable': True,
                                'pinned': 'left',
                                'prompt_order_rules': [i for i in buy_button_dict_items().keys()],
                                },
                                {'button_name': None,
                                'button_api': f'{ip_address}/api/data/queen_sell_orders',
                                'prompt_message': 'Edit Sell',
                                'prompt_field': 'sell_option',
                                'col_headername': 'Take Money',
                                "col_header": "queens_suggested_sell",
                                "border_color": "red",
                                'col_width':135,
                                'sortable': True,
                                'pinned': 'left',
                                'prompt_order_rules': [i for i in sell_button_dict_items().keys()],
                                },
                                {'button_name': None,
                                'button_api': f'{ip_address}/api/data/update_queenking_chessboard',
                                'prompt_message': 'Edit Allocation',
                                'prompt_field': 'edit_allocation_option',
                                'col_headername': 'Buying Power Weight',
                                "col_header": "ticker_buying_power",
                                "border_color": "black",
                                'col_width':90,
                                # 'pinned': 'left',
                                'prompt_order_rules': ['allocation'],
                                },
                            ]
                    
                    for star in star_names().keys():
                        # if star != '1Minute_1Day':
                        #     continue
                        column_header = f"{star}_state"
                        temp = {'button_name': None,
                                'button_api': f'{ip_address}/api/data/queen_buy_orders',
                                'prompt_message': 'Edit Buy',
                                'prompt_field': f'{star}_kors',
                                'col_headername': f'{star}',
                                "col_header": column_header,
                                "border_color": "#BEE3FE",
                                'col_width':135,
                                # 'pinned': 'right',
                                'prompt_order_rules': [i for i in buy_button_dict_items().keys()],
# 'cellStyle': f"""
#     function(params) {{
#         if (params.data['{column_header}'] && params.data['{column_header}'].includes('sell')) {{
#             return {{
#                 'backgroundColor': 'red',
#                 'color': 'white'
#             }};
#         }} else {{
#             return {{
#                 'backgroundColor': 'green',
#                 'color': 'black'
#             }};
#         }}
#     }}
# """
                                }
                        buttons.append(temp)
                    
                    return buttons

                def config_cols(cols):

                    return  {
                    # for col in cols:
                    'symbol': {'headerName':'Symbol', 'initialWidth':89, 'pinned': 'left'},
                    'current_from_yesterday': {'headerName':'% Change', 'sortable':'true',}, #  "type": ["customNumberFormat", "numericColumn", "numberColumnFilter", ]},                    
                    # 'ticker_buying_power': {'headerName':'BuyingPower Allocation', 'editable':True, }, #  'cellEditorPopup': True "type": ["customNumberFormat", "numericColumn", "numberColumnFilter", ]},                    
                    'current_from_open': {'headerName':"% From Open", 'sortable':'true',}, #  "type": ["customNumberFormat", "numericColumn", "numberColumnFilter", ]},                    


                    # 'queens_note': create_ag_grid_column(headerName='Queens Note', initialWidth=89, wrapText=True),
                    'total_budget': {'headerName':'Total Budget', 'sortable':'true', "type": ["customNumberFormat", "numericColumn", "numberColumnFilter", ]},                    
                    'long_at_play': create_ag_grid_column(headerName='$Long',sortable=True, initialWidth=100, enableCellChangeFlash=True, cellRenderer='agAnimateShowChangeCellRenderer', type=["customNumberFormat", "numericColumn", "numberColumnFilter", ]),
                    'short_at_play': create_ag_grid_column(headerName='$Short',sortable=True, initialWidth=100, enableCellChangeFlash=True, cellRenderer='agAnimateShowChangeCellRenderer',  type=["customNumberFormat", "numericColumn", "numberColumnFilter", ]),
                    # 'allocation_long_deploy': {'headerName':'Queen Allocation Deploy', 'sortable':'true', "type": ["customNumberFormat", "numericColumn", "numberColumnFilter", ],
                    #                            'cellRenderer': 'agAnimateShowChangeCellRenderer','enableCellChangeFlash': True,
                    #                            },                    
                    'trinity_w_L': create_ag_grid_column(headerName='Trinity Force',sortable=True, initialWidth=89, enableCellChangeFlash=True, cellRenderer='agAnimateShowChangeCellRenderer'),
                    'trinity_w_15': create_ag_grid_column(headerName='Flash Force',sortable=True, initialWidth=89, ),
                    'trinity_w_30': create_ag_grid_column(headerName='Middle Force',sortable=True, initialWidth=89, ),
                    'trinity_w_54': create_ag_grid_column(headerName='Future Force',sortable=True, initialWidth=89, ),
                    'remaining_budget': create_ag_grid_column(headerName='Remaining Budget', initialWidth=100,  type=["customNumberFormat", "numericColumn", "numberColumnFilter", ]),
                    'remaining_budget_borrow': create_ag_grid_column(headerName='Remaining Budget Margin', initialWidth=100, type=["customNumberFormat", "numericColumn", "numberColumnFilter", ]),
                    # 'qty_available': create_ag_grid_column(headerName='Qty Avail', initialWidth=89),
                    # 'broker_qty_delta': create_ag_grid_column(headerName='Broker Qty Delta', initialWidth=89, cellStyle={'backgroundColor': 'grey', 'color': 'white', 'font': '18px'}),
                    # 'trinity_w_S': create_ag_grid_column(headerName='Margin Force',sortable=True, initialWidth=89, enableCellChangeFlash=True, cellRenderer='agAnimateShowChangeCellRenderer'),
                    }

                # chess_pieces = list(revrec['df_qcp'].index)
                chess_pieces = [v.get('piece_name') for i, v in QUEEN_KING['chess_board'].items()]
                story_col = revrec.get('storygauge').columns.tolist()
                config_cols_ = config_cols(story_col)
                for col, config_values in config_cols_.items():
                    config = config_values
                    gb.configure_column(col, config)
                mmissing = [i for i in story_col if i not in config_cols_.keys()]
                if len(mmissing) > 0:
                    for col in mmissing:
                        gb.configure_column(col, {'hide': True})

                g_buttons = story_grid_buttons()

                go = gb.build()
                # with st.expander("default build check"):
                #     st.write(go)
                st_custom_grid(
                    client_user=client_user,
                    username=KING['users_allowed_queen_emailname__db'].get(client_user), 
                    api=f"{ip_address}/api/data/story",
                    api_update=f"{ip_address}/api/data/update_queenking_chessboard",
                    refresh_sec=refresh_sec, 
                    refresh_cutoff_sec=seconds_to_market_close, 
                    prod=st.session_state['production'],
                    grid_options=go,
                    key=f'story_grid',
                    return_type='story',
                    # kwargs from here
                    prompt_message = "symbol",
                    prompt_field = "symbol", # "current_macd_tier", # for signle value
                    api_key=os.environ.get("fastAPI_key"),
                    symbols=symbols,
                    buttons=g_buttons,
                    grid_height='450px',
                    toggle_views = ["Queen", "King"] + chess_pieces,
                    allow_unsafe_jscode=True,

                ) 

            except Exception as e:
                print_line_of_error(e)

        ########################################################
        ########################################################
        #############The Infinite Loop of Time #################
        ########################################################nnj
        ########################################################jnk
        ########################################################kjm,mmmm

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
            sneak_peak = False
            st.session_state['sneak_peak'] == False
            st.stop()
        
        elif st.session_state['authentication_status']:
            sneak_peak = False
            pass
        else:
            st.error("Stopping page")
            st.stop()


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

        swarm_queen_symbols = []
        for qcp, va in QUEENBEE['workerbees'].items():
            tickers = va.get('tickers')
            if tickers:
                for tic in tickers:
                    swarm_queen_symbols.append(tic)

        tickers_avail = [list(set(i.split("_")[0] for i in STORY_bee.keys()))][0]
        # def cache_tradingModelsNotGenerated() IMPROVEMENT TO SPEED UP CACHE cache function
        tic_need_TM = [i for i in tickers_avail if i not in QUEEN_KING['king_controls_queen'].get('symbols_stars_TradingModel')]
        if len(tic_need_TM) > 0:
            print("Adding Trading Model for: ", tic_need_TM)
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
        # func_list = [i for i in func_list if st.session_state[i]]
        with st.spinner("Refreshing"): # ozzbot

            if authorized_user:
                revrec = QUEEN.get('revrec')
                if QUEEN_KING.get('revrec') == 'init' or st.sidebar.button("refresh revrec"):
                    revrec = refresh_chess_board__revrec(acct_info, QUEEN, QUEEN_KING, STORY_bee, active_queen_order_states, chess_board__revrec={}, revrec__ticker={}, revrec__stars={}, fresh_board=True) ## Setup Board
                    QUEEN_KING['revrec'] = revrec
                
                if st.sidebar.button("Clear Thoughts"):
                    clear_subconscious_Thought(QUEEN, QUEEN_KING)

                # story_tab, trading_tab, order_tab, charts_tab = st.tabs(['Story', 'Waves', 'Orders', 'Wave Charts',]) # 'waves', 'workerbees', 'charts'

                # with story_tab:
                refresh_sec = 8 if seconds_to_market_close > 0 and mkhrs == 'open' else 0
                refresh_sec = 23 if 'sneak_peak' in st.session_state and st.session_state['sneak_peak'] else refresh_sec
                # refresh_sec = None if st.sidebar.toggle("Edit Story Grid") else refresh_sec
                # print("STORY GRID")
                story_grid(client_user=client_user, ip_address=ip_address, revrec=revrec, symbols=symbols, refresh_sec=refresh_sec)
               
                # with trading_tab:
                symbols = QUEEN['heartbeat'].get('active_tickers')
                symbols = ['SPY'] if len(symbols) == 0 else symbols
                if 'orders' in st.session_state and st.session_state['orders']:
                    if type(revrec.get('waveview')) != pd.core.frame.DataFrame:
                        st.error("PENDING QUEEN")
                    else:
                        # with st.expander("Star Grid :sparkles:", True):
                        refresh_sec = 8 if seconds_to_market_close > 120 and mkhrs == 'open' else 0
                        refresh_sec = 54 if 'sneak_peak' in st.session_state and st.session_state['sneak_peak'] else refresh_sec
                        if st.toggle("show wave grid"):
                            wave_grid(revrec=revrec, symbols=symbols, ip_address=ip_address, key=f'{"wb"}{symbols}{"orders"}', refresh_sec=False)

                # with order_tab:
                # refresh_sec = 8 if seconds_to_market_close > 0 and mkhrs == 'open' else None
                # refresh_sec = 23 if 'sneak_peak' in st.session_state and st.session_state['sneak_peak'] else refresh_sec
                # if st.toggle("show Orders"):
                #     order_grid(KING, queen_orders, ip_address)

                cols = st.columns(2)
                with cols[0]:
                    refresh_sec = 12 if seconds_to_market_close > 120 and mkhrs == 'open' else 0
                    refresh_sec = 60 if 'sneak_peak' in st.session_state and st.session_state['sneak_peak'] else refresh_sec
                    # print("GRAPHS")
                    st_custom_graph(
                        api=f'{ip_address}/api/data/symbol_graph',
                        x_axis={
                            'field': "timestamp_est"
                        },

                        y_axis=symbols_unique_color(['SPY', 'SPY vwap', 'QQQ', 'QQQ vwap']),
                        theme_options={
                                    'backgroundColor': k_colors.get('default_background_color'),
                                    'main_title': '',   # '' for none
                                    'x_axis_title': '',
                                    'grid_color': default_text_color,
                                    "showInLegend": True,
                                    "showInLegendPerLine": True,
                                },
                        refresh_button=True,
                        
                        #kwrags
                        username=KING['users_allowed_queen_emailname__db'].get(client_user),
                        prod=prod,
                        symbols=['SPY', 'QQQ'],
                        refresh_sec=refresh_sec,
                        api_key=os.environ.get("fastAPI_key"),
                        return_type=None,
                        graph_height=300,
                        key="Index_Graph",
                        toggles=list(star_names().keys()),
                        # y_max=420
                        )




                with cols[1]:
                    with st.sidebar:
                        graph_qcps = st.multiselect('graph qcps', options=QUEEN_KING.get('chess_board'), default=['bishop', 'castle', 'knight'])
                    refresh_sec = 8 if seconds_to_market_close > 0 and mkhrs == 'open' else 0
                    refresh_sec = 23 if 'sneak_peak' in st.session_state and st.session_state['sneak_peak'] else refresh_sec
                    symbols = []
                    for qcp in graph_qcps:
                        symbols+= QUEEN_KING['chess_board'][qcp].get('tickers')
                    
                    if len(symbols) > 10:
                        print('symbols > 10 lines')
                        c=1
                        symbols_copy = symbols.copy()
                        symbols =  []
                        for s in symbols_copy:
                            if c > 9:
                                continue
                            symbols.append(s)
                            c+=1

                    refresh_sec = 12 if seconds_to_market_close > 120 and mkhrs == 'open' else 0
                    refresh_sec = 60 if 'sneak_peak' in st.session_state and st.session_state['sneak_peak'] else refresh_sec
                    st_custom_graph(
                        api=f'{ip_address}/api/data/ticker_time_frame',
                        x_axis={
                            'field': 'timestamp_est'
                        },

                        y_axis=symbols_unique_color(symbols),
                        theme_options={
                                'backgroundColor': k_colors.get('default_background_color'),
                                'main_title': '',   # '' for none
                                'x_axis_title': '',
                                'grid_color': default_text_color,
                                "showInLegend": True,
                                "showInLegendPerLine": True,
                            },
                        refresh_button=True,
                        
                        #kwrags
                        username=KING['users_allowed_queen_emailname__db'].get(client_user),
                        prod=prod,
                        symbols=symbols,
                        refresh_sec=refresh_sec,
                        api_key=os.environ.get("fastAPI_key"),
                        return_type=None,
                        graph_height=300,
                        key='graph2',
                        ttf='1Minute_1Day',
                        toggles=list(star_names().keys()),
                        # y_max=420
                        )
        # print("END CONSCIENCE")
        ##### END ####
    except Exception as e:
        print('queensconscience', print_line_of_error(e))

if __name__ == '__main__':
    # client_user =
    # prod =
    # KING, users_allowed_queen_email, users_allowed_queen_emailname__db = kingdom__grace_to_find_a_Queen()

    # QUEENBEE=None

    # qb = init_queenbee(client_user=client_user, prod=prod, queen=True, queen_king=True, api=True, broker=True, init=True)
    # QUEEN = qb.get('QUEEN')
    # QUEEN_KING = qb.get('QUEEN_KING')
    # api = qb.get('api')

    # # QUEEN=
    # # QUEEN_KING=
    # # api=
    # # api_var=

    # queens_conscience(QUEENBEE, KING, QUEEN, QUEEN_KING, api, api_vars)

    queens_conscience(None, None, None, None, None)


                # hh = JSCode("""
                #         function(params) {
                #             // Add your logic here to determine the style based on cell value
                #             if (params.value > 0) {
                #                 return {
                #                     'background-color': 'green',
                #                     'color': 'white'
                #                 };
                #             } else {
                #                 return {
                #                     'background-color': 'red',
                #                     'color': 'white'
                #                 };
                #             }
                #         }
                #     """)