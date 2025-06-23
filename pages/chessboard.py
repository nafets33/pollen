
import pandas as pd
import os
import numpy as np
from datetime import datetime, timedelta
import pytz
from itertools import islice
from PIL import Image
from dotenv import load_dotenv
import streamlit as st
import os
import time
import hydralit_components as hc

from streamlit_extras.switch_page_button import switch_page

from pq_auth import signin_main
from chess_piece.king import return_QUEEN_KING_symbols, master_swarm_QUEENBEE, local__filepaths_misc, print_line_of_error, ReadPickleData, PickleData, return_QUEENs__symbols_data, kingdom__global_vars
from chess_piece.queen_hive import star_names, kingdom__grace_to_find_a_Queen, pollen_themes, init_qcp_workerbees, generate_chessboards_trading_models, return_queen_controls, shape_chess_board, generate_chess_board, refresh_account_info, init_queenbee, unshape_chess_board, setup_chess_board, add_trading_model, set_chess_pieces_symbols, read_swarm_db, refresh_broker_account_portolfio
from chess_piece.queen_mind import refresh_chess_board__revrec, init_qcp
from custom_button import cust_Button
from custom_grid import st_custom_grid, GridOptionsBuilder
# from custom_graph_v1 import st_custom_graph
from chess_piece.pollen_db import PollenDatabase
import copy
import ipdb
crypto_symbols__tickers_avail = ['BTC/USD', 'ETH/USD']
pg_migration = os.getenv('pg_migration')

hedge_funds = {
    "Bridgewater Associates": {
        "theme": "weight_time_waves",
        "portfolio": {
            "SPY": 0.15,
            "TLT": 0.10,
            "GLD": 0.08,
            "LQD": 0.12,
            "IEF": 0.10,
            "AGG": 0.05,
            "DBC": 0.05,
            "VTI": 0.15,
            "VEA": 0.10,
            "VNQ": 0.10,
        }
    },
    "Renaissance Technologies": {
        "theme": "weight_time_waves",
        "portfolio": {
            "AAPL": 0.10,
            "MSFT": 0.12,
            "NVDA": 0.08,
            "AMZN": 0.12,
            "GOOG": 0.10,
            "META": 0.10,
            "TSLA": 0.08,
            "AMD": 0.10,
            "ADBE": 0.10,
            "NFLX": 0.10,
        }
    },
    "Two Sigma": {
        "theme": "weight_time_waves",
        "portfolio": {
            "SPY": 0.20,
            "QQQ": 0.15,
            "EFA": 0.10,
            "TLT": 0.15,
            "XLE": 0.10,
            "XLF": 0.10,
            "XLK": 0.10,
            "XLV": 0.10,
        }
    },
    "Citadel": {
        "theme": "weight_time_waves",
        "portfolio": {
            "AAPL": 0.10,
            "GOOG": 0.10,
            "TSLA": 0.15,
            "AMZN": 0.10,
            "NVDA": 0.15,
            "META": 0.10,
            "MSFT": 0.10,
            "BRK.B": 0.10,
            "JPM": 0.10,
        }
    },
    "DE Shaw": {
        "theme": "weight_time_waves",
        "portfolio": {
            "SPY": 0.12,
            "EFA": 0.10,
            "GLD": 0.08,
            "TLT": 0.12,
            "LQD": 0.10,
            "AGG": 0.10,
            "DBC": 0.08,
            "IEF": 0.10,
            "VEA": 0.10,
            "VTI": 0.10,
        }
    },
    "Millennium Management": {
        "theme": "weight_time_waves",
        "portfolio": {
            "XLK": 0.20,
            "XLE": 0.15,
            "XLV": 0.10,
            "XLF": 0.10,
            "SPY": 0.10,
            "TLT": 0.10,
            "GLD": 0.05,
            "EFA": 0.10,
            "VTI": 0.10,
        }
    },
    "Point72 Asset Management": {
        "theme": "weight_time_waves",
        "portfolio": {
            "AAPL": 0.10,
            "MSFT": 0.10,
            "TSLA": 0.10,
            "META": 0.10,
            "AMZN": 0.10,
            "GOOG": 0.10,
            "NFLX": 0.10,
            "NVDA": 0.10,
            "BRK.B": 0.10,
            "JPM": 0.10,
        }
    },
    "Elliott Management": {
        "theme": "weight_time_waves",
        "portfolio": {
            "XLE": 0.20,
            "XLF": 0.20,
            "XLV": 0.10,
            "XLK": 0.10,
            "SPY": 0.10,
            "TLT": 0.10,
            "IEF": 0.10,
            "AGG": 0.10,
        }
    },
    "AQR Capital Management": {
        "theme": "weight_time_waves",
        "portfolio": {
            "SPY": 0.15,
            "TLT": 0.10,
            "AGG": 0.10,
            "DBC": 0.05,
            "LQD": 0.10,
            "IEF": 0.10,
            "GLD": 0.10,
            "EFA": 0.10,
            "VEA": 0.10,
            "VTI": 0.10,
        }
    },
    "Man Group": {
        "theme": "weight_time_waves",
        "portfolio": {
            "SPY": 0.12,
            "QQQ": 0.10,
            "TLT": 0.12,
            "XLE": 0.08,
            "XLK": 0.10,
            "GLD": 0.10,
            "IEF": 0.10,
            "AGG": 0.08,
            "DBC": 0.10,
            "VEA": 0.10,
        }
    }
}

def save_queen_king(QUEEN_KING):
    PollenDatabase.upsert_data(QUEEN_KING.get('table_name'), QUEEN_KING.get('key'), QUEEN_KING)

def chessboard_grid(chess_board, client_user, ip_address, symbols=[], refresh_sec=0, paginationOn=False, key='chessboard', seconds_to_market_close=0, prod=None):

    if not prod:
        prod = prod
    try:
        gb = GridOptionsBuilder.create()
        gb.configure_default_column(column_width=100, 
                                    resizable=True,wrapText=False, wrapHeaderText=True, sortable=True, autoHeaderHeight=True, autoHeight=True, 
                                    suppress_menu=False, filterable=True,)            
        gb.configure_index('ticker')
        gb.configure_theme('ag-theme-material')
        if paginationOn:
            gb.configure_pagination(paginationAutoPageSize=True) #Add pagination

        def story_grid_buttons():
            buttons=[
                        # {'button_name': None,
                        # 'button_api': f'{ip_address}/api/data/chessboard',
                        # 'prompt_message': 'Edit Board',
                        # 'prompt_field': 'kors',
                        # 'col_headername': 'Update',
                        # "col_header": "chessboard_update_button",
                        # # "border_color": "green",
                        # 'col_width':100,
                        # 'sortable': True,
                        # 'pinned': 'left',
                        # 'prompt_order_rules': [] # [i for i in buy_button_dict_items().keys() if i not in exclude_buy_kors],
                        # # 'cellStyle': button_suggestedallocation_style,
                        # },
                    ]
            return buttons

        def config_cols(cols):
            values_list = list(star_names().keys())
            model_list = ['Pollen AI', 'MACD', 'Williams', 'Simple Weighted']
            return  {
            # for col in cols:
            'ticker': {'headerName':'Symbol', 'initialWidth':89, 'pinned': 'left', 'sortable':'true',},
            'picture': {}, # image selection,
            'piece_name': {"cellEditorParams": {"editable":True, "cellEditor":"agSelectCellEditor",}, #editable,
            'model': {'headerName':'Model',
                      "cellEditorParams": {"values": model_list},
                                                                "editable":True,
                                                                "cellEditor":"agSelectCellEditor",
                                                                },
            },
            # 'theme': {'headerName':'Theme', },
            'total_buyng_power_allocation': {'headerName':'Buying Power Allocation', 'sortable':'true', },
            'total_borrow_power_allocation': {'headerName': 'Margin Power Allocation', 'sortable':'true', "type": ["customNumberFormat", "numericColumn", "numberColumnFilter", ]},
            'margin_power': {'headerName': 'Margin Power % Use', 'sortable':'true', "type": ["customNumberFormat", "numericColumn", "numberColumnFilter", ]},
            'refresh_star': {'headerName': 'Re Allocate Every', 
                             "cellEditorParams": {"values": values_list},
                                                                "editable":True,
                                                                "cellEditor":"agSelectCellEditor",
                                                                },

            }

        df = shape_chess_board(chess_board)
        chess_pieces = [v.get('piece_name') for i, v in chess_board.items()]
        story_col = df.columns.tolist()
        config_cols_ = config_cols(story_col)
        for col, config_values in config_cols_.items():
            config = config_values
            gb.configure_column(col, config)

        mmissing = [i for i in story_col if i not in config_cols_.keys()]
        if len(mmissing) > 0:
            print('chessboard page: cols missing', mmissing)
            for col in mmissing:
                gb.configure_column(col) #{'hide': True})

        g_buttons = story_grid_buttons()

        go = gb.build()
        # with st.expander("default build check"):
        #     st.write(go)
        st_custom_grid(
            client_user=client_user,
            username=client_user, 
            api=f"{ip_address}/api/data/chessboard",
            api_update=f"{ip_address}/api/data/update_queenking_chessboard",
            refresh_sec=refresh_sec, 
            refresh_cutoff_sec=seconds_to_market_close, 
            prod=prod,
            grid_options=go,
            key=key,
            api_key=os.environ.get("fastAPI_key"),
            symbols=symbols,
            buttons=g_buttons,
            grid_height='450px',
            toggle_views = chess_pieces,
            allow_unsafe_jscode=True,

        ) 

    except Exception as e:
        print_line_of_error(e)


def first_revrec_setup(QUEEN_KING):

    QUEEN = init_queenbee(client_user=client_user, prod=prod, queen=True).get('QUEEN')
    
    if pg_migration:
        symbols = return_QUEEN_KING_symbols(QUEEN_KING, QUEEN)
        STORY_bee = PollenDatabase.retrieve_all_story_bee_data(symbols).get('STORY_bee')
    else:
        STORY_bee = return_QUEENs__symbols_data(QUEEN=QUEEN, QUEEN_KING=QUEEN_KING, read_storybee=True, read_pollenstory=False).get('STORY_bee') ## async'd func
    
    from chess_piece.queen_bee import god_save_the_queen
    pq = init_queenbee(client_user=client_user, prod=prod, queen=True, queen_heart=True)
    QUEEN = pq.get('QUEEN')
    QUEENsHeart = pq.get('QUEENsHeart')

    if pg_migration:
        symbols = return_QUEEN_KING_symbols(QUEEN_KING, QUEEN)
        STORY_bee = PollenDatabase.retrieve_all_story_bee_data(symbols).get('STORY_bee')
    else:
        STORY_bee = return_QUEENs__symbols_data(QUEEN=QUEEN, QUEEN_KING=QUEEN_KING, read_storybee=True, read_pollenstory=False).get('STORY_bee') ## async'd func
    
    QUEEN = refresh_broker_account_portolfio(api, QUEEN)
    revrec = refresh_chess_board__revrec(QUEEN['account_info'], QUEEN, QUEEN_KING, STORY_bee) ## Setup Board
    if not revrec:
        st.error("RevRec Failed")
        return False
    
    QUEEN['revrec'] = revrec
    god_save_the_queen(QUEENsHeart=QUEENsHeart, 
                        QUEEN=QUEEN, 
                    save_q=True,
                    save_rr=True,
                    console=True)
    QUEEN_KING['revrec'] = True
    if pg_migration:
        PollenDatabase.upsert_data(QUEEN_KING.get('table_name'), QUEEN_KING.get('key'), QUEEN_KING)
    else:
        PickleData(QUEEN_KING.get('source'), QUEEN_KING, console=True)
    
    st.success("Trading RevRec Board Initialized")



def add_new_qcp__to_chessboard(QUEEN_KING, ticker_allowed, themes, qcp_bees_key='chess_board'):
    models = ['MACD', 'story__AI']
    qcp_pieces = QUEEN_KING[qcp_bees_key].keys()
    qcp_name = st.text_input(label='piece name', value=f'pawn_{len(qcp_pieces)}', help="Theme your names to match your strategy")
    if qcp_name in qcp_pieces:
        st.error("Chess Piece Name must be Unique")
        st.stop()

    with st.form('new qcp'):
        qcp_vars = init_qcp()
        cols = st.columns((1,3,2,2,2,2,2,2))
        with cols[0]:
            picture = cust_Button(local__filepaths_misc().get('queen_png'), key=f'{qcp_name}_image')
        with cols[1]:
            qcp_vars['tickers'] = st.multiselect(label=f'symbols', options=ticker_allowed + crypto_symbols__tickers_avail, default=qcp_vars['tickers'], help='Castle Should Hold your Highest Valued Symbols', key=f'{qcp_name}tickers{admin}', label_visibility='hidden')
        with cols[2]:
            qcp_vars['model'] = st.selectbox(label='model', options=models, index=models.index(qcp_vars.get('model')), key=f'{qcp_name}model{admin}')
        with cols[3]:
            qcp_vars['theme'] = st.selectbox(label=f'theme', options=themes, index=themes.index(qcp_vars.get('theme')), help='Trading Star Strategy, You May Customize Trading Models', key=f'{qcp_name}theme{admin}')
        with cols[4]:
            qcp_vars['total_buyng_power_allocation'] = st.slider(label=f'Budget Allocation', min_value=float(0.0), max_value=float(1.0), value=float(qcp_vars['total_buyng_power_allocation']), key=f'{qcp_name}_buying_power_allocation{admin}')
        with cols[5]:
            qcp_vars['total_borrow_power_allocation'] = st.slider(label=f'Margin Allocation', min_value=float(0.0), max_value=float(1.0), value=float(qcp_vars['total_borrow_power_allocation']), key=f'{qcp_name}_borrow_power_allocation{admin}', label_visibility='hidden')
        with cols[6]:
            qcp_vars['margin_power'] = st.slider(label=f'Margin Power', min_value=float(0.0), max_value=float(1.0), value=float(qcp_vars.get('margin_power')), key=f'{qcp_name}_margin_power_{admin}', label_visibility='hidden')
        
        qcp = init_qcp(init_macd_vars={"fast": 12, "slow": 26, "smooth": 9}, 
                        ticker_list=qcp_vars.get('tickers'), 
                        theme=qcp_vars.get('theme'), 
                        model=qcp_vars.get('model'), 
                        piece_name=qcp_name, 
                        buying_power=qcp_vars.get('total_buyng_power_allocation'), 
                        borrow_power=qcp_vars.get('total_borrow_power_allocation'), 
                        picture='queen_png', 
                        margin_power=qcp_vars.get('margin_power'))
        
        if st.form_submit_button('Add New Piece'):
            QUEEN_KING[qcp_bees_key][qcp.get('piece_name')] = qcp
            QUEEN_KING = handle__new_tickers__AdjustTradingModels(QUEEN_KING=QUEEN_KING)
            if pg_migration:
                save_queen_king(QUEEN_KING)
            else:
                PickleData(QUEEN_KING.get('source'), QUEEN_KING)
            st.success("New Piece Added Refresh")
        
        return QUEEN_KING


# def return_star_power_allocation(trading_model):

#     for star, star_vars in trading_model.get('stars_kings_order_rules').items():
#         trading_model_revrec[star] = star_vars.get("buyingpower_allocation_LongTerm")
#         trading_model_revrec_s[star] = star_vars.get("buyingpower_allocation_ShortTerm")


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
                
                if st.form_submit_button("Reallocate Star Power"):
                    QUEEN_KING['saved_trading_models'].update(trading_model)
                    if pg_migration:
                        save_queen_king(QUEEN_KING)
                    else:
                        PickleData(pickle_file=QUEEN_KING.get('source'), data_to_store=QUEEN_KING)
    except Exception as e:
        print_line_of_error("rev allocation error")


def setup_qcp_on_board(QUEEN_KING, qcp_bees_key, qcp, ticker_allowed, themes, new_piece=False, headers=0):
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
            print_line_of_error(e)

    models = ['MACD', 'story__AI']

    ticker_allowed = ticker_allowed + crypto_symbols__tickers_avail

    try:
        cols = st.columns((1,1,4,1,1,2,2,2))
        if headers == 0:
            # Headers
            c=0
            chess_board_names = list(QUEEN_KING[qcp_bees_key][list(QUEEN_KING[qcp_bees_key].keys())[0]].keys())
            chess_board_names = ["pq", "Name", 'symbols', 'Model', 'Theme', 'Budget Allocation', 'Margin Allocation', 'Margin Power']
            for qcpvar in chess_board_names:
                try:
                    with cols[c]:
                        st.write(f'{qcpvar}')
                        c+=1
                except Exception as e:
                    print("AHH", qcpvar, e)

        with st.container():
            cols = st.columns((1,1,4,1,1,2,2,2))
            with cols[0]:
                cust_Button(local__filepaths_misc().get('castle_png'), key=f'{qcp}')
            # chess board vars
            with cols[1]:
                QUEEN_KING[qcp_bees_key][qcp]['piece_name'] = st.text_input("Name", value=QUEEN_KING[qcp_bees_key][qcp]['piece_name'], key=f'{qcp}piece_name{admin}', label_visibility='hidden')
            with cols[2]:
                QUEEN_KING[qcp_bees_key][qcp]['tickers'] = st.multiselect(label=qcp, options=ticker_allowed, default=QUEEN_KING[qcp_bees_key][qcp].get('tickers', []), help='Castle Should Hold your Highest Valued Symbols', key=f'{qcp}tickers{admin}',  label_visibility='hidden')
            with cols[3]:
                QUEEN_KING[qcp_bees_key][qcp]['model'] = st.selectbox(label='-', options=models, index=models.index(QUEEN_KING[qcp_bees_key][qcp].get('model')), key=f'{qcp}model{admin}')
            with cols[4]:
                QUEEN_KING[qcp_bees_key][qcp]['theme'] = st.selectbox(label=f'-', options=themes, index=themes.index(QUEEN_KING[qcp_bees_key][qcp].get('theme')), help='Trading Star Strategy, You May Customize Trading Models', key=f'{qcp}theme{admin}')
            with cols[5]:
                QUEEN_KING[qcp_bees_key][qcp]['total_buyng_power_allocation'] = st.slider(label=f'Budget Allocation', min_value=float(0.0), max_value=float(1.0), value=float(QUEEN_KING[qcp_bees_key][qcp]['total_buyng_power_allocation']), key=f'{qcp}_buying_power_allocation{admin}', label_visibility='hidden')
            with cols[6]:
                QUEEN_KING[qcp_bees_key][qcp]['total_borrow_power_allocation'] = st.slider(label=f'Margin Allocation', min_value=float(0.0), max_value=float(1.0), value=float(QUEEN_KING[qcp_bees_key][qcp]['total_borrow_power_allocation']), key=f'{qcp}_borrow_power_allocation{admin}', label_visibility='hidden')
            with cols[7]:
                QUEEN_KING[qcp_bees_key][qcp]['margin_power'] = st.slider(label=f'Margin Power', min_value=float(0.0), max_value=float(1.0), value=float(QUEEN_KING[qcp_bees_key][qcp]['margin_power']), key=f'{qcp}margin_power{admin}', label_visibility='hidden')

        return QUEEN_KING
    
    except Exception as e:
        st.write(print_line_of_error("chess board"))


def handle__new_tickers__AdjustTradingModels(QUEEN_KING, qcp_bees_key='chess_board', reset_theme=False):
    # add new trading models if needed
    # Castle 
    trading_models = QUEEN_KING['king_controls_queen']['symbols_stars_TradingModel']
    for qcp, bees_data in QUEEN_KING[qcp_bees_key].items():
        tickers = bees_data.get('tickers')
        if tickers:
            for ticker in tickers:
                try:
                    if reset_theme:
                        QUEEN_KING = add_trading_model(QUEEN_KING=QUEEN_KING, ticker=ticker, model=bees_data.get('model'), theme=bees_data.get('theme'))
                    else:
                        if ticker not in trading_models.keys():
                            QUEEN_KING = add_trading_model(QUEEN_KING=QUEEN_KING, ticker=ticker, model=bees_data.get('model'), theme=bees_data.get('theme'))
                except Exception as e:
                    print('wtferr', e)
    return QUEEN_KING


def refresh_chess_board__button(QUEEN_KING):
    refresh = st.button("Reset Chess Board",  use_container_width=True)

    if refresh:
        QUEEN_KING['chess_board'] = generate_chess_board()
        if pg_migration:
            save_queen_king(QUEEN_KING)
        else:
            PickleData(pickle_file=st.session_state['PB_App_Pickle'], data_to_store=QUEEN_KING)
        st.success("Generated Default Chess Board")
        time.sleep(1)
        st.rerun()
            
    return True

def refresh_queen_controls_button(QUEEN_KING):
    refresh = st.button("Reset ALL QUEEN controls", use_container_width=True)

    if refresh:
        QUEEN_KING['king_controls_queen'] = return_queen_controls()
        if pg_migration:
            save_queen_king(QUEEN_KING)
        else:
            PickleData(pickle_file=st.session_state['PB_App_Pickle'], data_to_store=QUEEN_KING)
        st.success("All Queen Controls Reset")
        st.rerun()
            
    return True

def refresh_trading_models_button(QUEEN_KING):
    refresh = st.button("Reset All Trading Models", use_container_width=True)

    if refresh:
        chessboard = QUEEN_KING['chess_board']
        tradingmodels = generate_chessboards_trading_models(chessboard)
        QUEEN_KING['king_controls_queen']['symbols_stars_TradingModel'] = tradingmodels
        
        if pg_migration:
            save_queen_king(QUEEN_KING)
        else:
            PickleData(pickle_file=st.session_state['PB_App_Pickle'], data_to_store=QUEEN_KING)
        st.success("All Queen.TradingModels Reset")
            
    return True

def align_autopilot_with_revrec(revrec, QUEEN_KING):
    current_index = QUEEN_KING['king_controls_queen']['ticker_autopilot'].index
    for symbol in revrec.get('storygauge').index:
        if symbol not in current_index:
            QUEEN_KING['king_controls_queen']['ticker_autopilot'].loc[symbol] = pd.Series([False, False], index=['buy_autopilot', 'sell_autopilot'])

    return QUEEN_KING


def switch_autopilot_on_off(QUEEN_KING, x_autopilot='buy_autopilot', onoff=True, save=False):
    for qcp, qcp_data in QUEEN_KING["chess_board"].items():
        for symbol in qcp_data.get('tickers'):
            # Ensure symbol exists in the DataFrame's index
            if symbol not in QUEEN_KING['king_controls_queen']['ticker_autopilot'].index:
                # Add a new row for the missing symbol, initializing columns
                QUEEN_KING['king_controls_queen']['ticker_autopilot'].loc[symbol] = {x_autopilot: False}
            
            # Assign the boolean value
            QUEEN_KING['king_controls_queen']['ticker_autopilot'].at[symbol, x_autopilot] = onoff
    if save:
        if pg_migration:
            PollenDatabase.upsert_data(table_name, QUEEN_KING.get('key'), QUEEN_KING)
        else:
            PickleData(QUEEN_KING.get('source'), QUEEN_KING)
    
    return QUEEN_KING


def chessboard(revrec, QUEEN_KING, ticker_allowed, themes, admin=False, qcp_bees_key = 'chess_board'):
    try:
        ip_address = st.session_state['ip_address']
        client_user = st.session_state["username"]
        print(client_user, "CHESSBOARD")
        chessboard_setup = st.session_state.get('chessboard_setup')
        if chessboard_setup:
            st.write("# Setup Your Portfolio, Try Selecting a Hedge Fund and Edit from there ! :star2:")
            st.write(":warning: Symbols in the same Group will share a Budget - You can edit Exact Amounts Later :gear:")

        hedge_funds = PollenDatabase.retrieve_data('db_sandbox', 'whalewisdom').get('latest_filer_holdings')
        # print(len(hedge_funds))
        # for fund in hedge_funds:
            # print(len(fund))

        hedge_fund_names = list(set(hedge_funds['filer_name'].tolist()))
        all_portfolios = ['Queen']
        save_as_main_chessboard = st.sidebar.checkbox("Save as Main Chessboard", True)

        with st.sidebar:
            if st.toggle("Control Settings"):
                with st.expander("control buttons"):
                    refresh_chess_board__button(QUEEN_KING)
                    refresh_queen_controls_button(QUEEN_KING)
                    refresh_trading_models_button(QUEEN_KING)
                    # refresh_queen_orders(QUEEN)
                    # stash_queen(QUEEN)


        optoins = []
        for op in all_portfolios:
            icon = "fas fa-chess-pawn"
            optoins.append({'id': op, 'icon': "fas fa-chess-pawn", 'label':op})

        # chessboard_selection = hc.option_bar(option_definition=optoins, title='Queen is Your Portfolio', key='chessboard_selections', horizontal_orientation=True) #,override_theme=over_theme,font_styling=font_fmt,horizontal_orientation=True)
        chessboard_selection = st.selectbox("Select Portfolio", [None] + hedge_fund_names)
        if not chessboard_selection:
            chessboard_selection = 'Queen'
        if chessboard_selection == 'Queen':
            pass
        if chessboard_selection in hedge_fund_names:
            if save_as_main_chessboard == False:
                qcp_bees_key = chessboard_selection
            if qcp_bees_key not in QUEEN_KING.keys():
                QUEEN_KING[qcp_bees_key] = {}
            # data = hedge_funds.get(chessboard_selection)
            data = hedge_funds[hedge_funds['filer_name'] == chessboard_selection]
            data = data.set_index('stock_ticker', drop=False)
            data = data.replace('DROPME', .001)
            data['current_percent_of_portfolio'] = pd.to_numeric(data['current_percent_of_portfolio'], errors='coerce')
            data = data[data['current_percent_of_portfolio'] > 0]
            data['buying_power'] = data['current_percent_of_portfolio'] / 100
            st.write(data)
            for ticker in data.index:
                if len(ticker) > 2 and ticker not in QUEEN_KING[qcp_bees_key].keys():
                    buying_power = data.loc[ticker].get('buying_power')
                    QUEEN_KING[qcp_bees_key][ticker] = init_qcp(ticker_list=[ticker], buying_power=buying_power, piece_name=ticker)
            symbols = return_QUEEN_KING_symbols(QUEEN_KING, QUEEN=None)
            if 'SPY' not in symbols:
                print("SPY not in symbols")
                symbols.append('SPY')
            STORY_bee = PollenDatabase.retrieve_all_story_bee_data(symbols=symbols).get('STORY_bee')
            # print("REVREC CALC")
            revrec = refresh_chess_board__revrec(acct_info, QUEEN, QUEEN_KING, STORY_bee, active_queen_order_states, check_portfolio=False) ## Setup Board
            QUEEN_KING['revrec'] = revrec
        elif chessboard_selection == 'Bishop':
            # WORKERBEE GET
            if pg_migration:
                QUEENBEE = read_swarm_db(prod, 'QUEEN')
                BISHOP = read_swarm_db(prod, 'BISHOP')
                df = BISHOP.get('screen_1')
                for sector in set(df['sector']):
                    token = df[df['sector']==sector]
                    tickers=token['symbol'].tolist()
                    QUEENBEE[qcp_bees_key][sector] = init_qcp_workerbees(ticker_list=tickers)
                
                symbols = return_QUEEN_KING_symbols(QUEEN_KING, QUEENBEE)
                STORY_bee = PollenDatabase.retrieve_all_story_bee_data(symbols=symbols).get('STORY_bee')
            else:
                QUEENBEE = setup_chess_board(QUEEN=QUEENBEE)
                STORY_bee = return_QUEENs__symbols_data(QUEEN=QUEEN, QUEEN_KING=QUEEN_KING, swarmQueen=False, read_pollenstory=False).get('STORY_bee')
            
            QUEEN_KING['chess_board'] = QUEENBEE['workerbees']
            revrec = refresh_chess_board__revrec(acct_info, QUEEN, QUEEN_KING, STORY_bee, active_queen_order_states) ## Setup Board
            QUEEN_KING['revrec'] = revrec
        
        chess_board = copy.deepcopy(QUEEN_KING[qcp_bees_key])
        # st.write(chess_board)
        

        chess_pieces = set_chess_pieces_symbols(QUEEN_KING=QUEEN_KING, qcp_bees_key=qcp_bees_key)
        view = chess_pieces.get('view')
        all_workers = chess_pieces.get('all_workers')
        qcp_ticker_index = chess_pieces.get('ticker_qcp_index')
        current_tickers = qcp_ticker_index.keys()

        
        ### AUTO PILOT CONTRROLS

        # def AutoPilot(revrec, QUEEN_KING):



        with st.sidebar:
            if st.button("align auto_pilot"):
                QUEEN_KING =  align_autopilot_with_revrec(revrec, QUEEN_KING)
                if pg_migration:
                    PollenDatabase.upsert_data(table_name, QUEEN_KING.get('key'), QUEEN_KING)
                else:
                    PickleData(QUEEN_KING.get('source'), QUEEN_KING)
            
            buy_autopilot = st.checkbox("Switch buy auto pilot", False)
            if st.button("Switch Buys Auto Pilot"):
                QUEEN_KING = switch_autopilot_on_off(QUEEN_KING, x_autopilot='buy_autopilot', onoff=buy_autopilot)
                st.write(QUEEN_KING['king_controls_queen']['ticker_autopilot'])
                if pg_migration:
                    PollenDatabase.upsert_data(table_name, QUEEN_KING.get('key'), QUEEN_KING)
                else:
                    PickleData(QUEEN_KING.get('source'), QUEEN_KING)

            sell_autopilot = st.checkbox("Switch sell auto pilot", False)
            if st.button("Switch Sells Auto Pilot"):
                QUEEN_KING = switch_autopilot_on_off(QUEEN_KING, x_autopilot='sell_autopilot', onoff=sell_autopilot)
                st.write(QUEEN_KING['king_controls_queen']['ticker_autopilot'])
                if pg_migration:
                    PollenDatabase.upsert_data(table_name, QUEEN_KING.get('key'), QUEEN_KING)
                else:
                    PickleData(QUEEN_KING.get('source'), QUEEN_KING)

        ### AUTO PILOT CONTRROLS

        # if st.sidebar.toggle("autopilot funcs"):
        #     AutoPilot(revrec, QUEEN_KING)
        # with st.expander(name, True): # ChessBoard
        cb_tab_list = ['Board', 'Star Allocation', 'Board Group', 'Board By Symbol', 'Portfolio Story']
        tabs = st.tabs(cb_tab_list)
        with tabs[4]:
            st.write(revrec.get('storygauge'))
        with tabs[0]:
            with st.form(f'ChessBoard_form{admin}'):
                try:
                    # st.write(QUEEN_KING['king_controls_queen']['buying_powers']['Jq']['total_dayTrade_allocation'])
                    cash = QUEEN_KING['king_controls_queen']['buying_powers']['Jq']['total_longTrade_allocation']
                    cash = max(min(cash, 1), -1)
                    QUEEN_KING['king_controls_queen']['buying_powers']['Jq']['total_longTrade_allocation'] = st.slider("Cash", min_value=-1.0, max_value=1.0, value=cash)
                    
                    headers = 0
                    for qcp in all_workers:
                        for tic in QUEEN_KING[qcp_bees_key][qcp].get('tickers', []):
                            if tic not in ticker_allowed:
                                print("TICKER NOT ALLOWED", tic)
                                QUEEN_KING[qcp_bees_key][qcp]['tickers'].remove(tic)
                        
                        if len(QUEEN_KING[qcp_bees_key][qcp]['tickers']) == 0:
                            continue

                        QUEEN_KING=setup_qcp_on_board(QUEEN_KING, qcp_bees_key, qcp, ticker_allowed=ticker_allowed, themes=themes, headers=headers)
                        headers+=1
                    
                    # RevRec
                    # print('RevRec')
                    QUEEN_KING['revrec'] = revrec
                    QUEEN_KING['chess_board__revrec'] = revrec
                    if save_as_main_chessboard:
                        st.warning("This Will Save as your Main Portfolio")
                    cols = st.columns(2)
                    with cols[0]:
                        if st.form_submit_button('Save Board', use_container_width=True):
                            if authorized_user == False:
                                st.warning("You Need your Queen First! Please contact pollenq.queen@gmail.com")
                                return False
                            
                            QUEEN_KING = handle__new_tickers__AdjustTradingModels(QUEEN_KING=QUEEN_KING)
                            if pg_migration:
                                save_queen_king(QUEEN_KING)
                            else:
                                PickleData(pickle_file=st.session_state['PB_App_Pickle'], data_to_store=QUEEN_KING)
                            if chessboard_setup:
                                first_revrec_setup(QUEEN_KING)

                            st.success("Trading Board Saved")
                    with cols[1]:
                        if st.form_submit_button('Reset ChessBoards Trading Models With Theme', use_container_width=True):
                            if authorized_user == False:
                                st.warning("You Need your Queen First! Please contact pollenq.queen@gmail.com")
                                return False

                            QUEEN_KING = handle__new_tickers__AdjustTradingModels(QUEEN_KING, reset_theme=True)
                            if pg_migration:
                                save_queen_king(QUEEN_KING)
                            else:
                                PickleData(pickle_file=st.session_state['PB_App_Pickle'], data_to_store=QUEEN_KING)
                            st.success("All Trading Models Reset to Theme")

                except Exception as e:
                    print_line_of_error()

                
            # st.write("# Reallocation")
            with tabs[1]:
                reallocate_star_power(QUEEN_KING, trading_model=False, ticker_option_qc=False, trading_model_revrec={}, trading_model_revrec_s={}, showguage=False, func_selection=True, formkey="Reallocate_Star")


        with st.expander("New Chess Piece", True):
            QUEEN_KING = add_new_qcp__to_chessboard(QUEEN_KING=QUEEN_KING, ticker_allowed=ticker_allowed, themes=themes, qcp_bees_key='chess_board')

        with tabs[3]:
            # WORKERBEE View a Board, compare Boards, Edit Current Board
            chess_board = QUEEN_KING['chess_board']
            chessboard_grid(chess_board, client_user, ip_address) #chess_board_id=qcp_bees_key)
            st.data_editor(chess_board)    
            df = shape_chess_board(chess_board)
        with tabs[2]:
            st.data_editor(df)    
            # boardagain = upshape_chess_board(df)

    except Exception as e:
        print('chessboard ', e, print_line_of_error())


## WORKERBEE : func to select portfolio and have board allocate
# return current board, if None Setup with SPY
# update board

if __name__ == '__main__':

    signin_main()

    client_user = st.session_state['client_user']
    authorized_user = st.session_state['authorized_user']
    if authorized_user != True:
        switch_page('pollen')


    king_G = kingdom__global_vars()
    active_order_state_list = king_G.get('active_order_state_list') # = ['running', 'running_close', 'submitted', 'error', 'pending', 'completed', 'completed_alpaca', 'running_open', 'archived_bee']
    active_queen_order_states = king_G.get('active_queen_order_states')

    admin = st.session_state['admin']
    prod = st.session_state['prod']
    table_name = 'client_user_store' if prod else 'client_user_store_sandbox'



    reset_theme = False

    KING = kingdom__grace_to_find_a_Queen()
    # st.write(KING['alpaca_symbols_df'])
    qb = init_queenbee(client_user=client_user, prod=prod, queen=True, queen_king=True, api=True, init=True, pg_migration=pg_migration)
    QUEEN = qb.get('QUEEN')
    QUEEN_KING = qb.get('QUEEN_KING')
    api = qb.get('api')    
    revrec = QUEEN.get('revrec')
    # st.write(QUEEN_KING['chess_board'])


    ticker_allowed = KING['alpaca_symbols_df'].index.tolist()

    alpaca_acct_info = refresh_account_info(api=api)
    with st.sidebar:
        if st.button('acct info'):
            st.write(alpaca_acct_info)

    acct_info = alpaca_acct_info.get('info_converted')

    themes = list(pollen_themes(KING).keys())
    chessboard(revrec=revrec, QUEEN_KING=QUEEN_KING, ticker_allowed=ticker_allowed, themes=themes, admin=False)

    if not st.session_state.get('chessboard_setup'):
        if st.button("Return To Trading Engine", use_container_width=True):
            st.switch_page("pollen.py")
    
    
    st.write(len(QUEEN_KING['sell_orders']), "sell orders")
    st.write(len(QUEEN_KING['buy_orders']), "buy_orders orders")
    st.write(len(QUEEN['queen_orders']), "queen_orders orders")

    if st.button("clear sell orders"):
        QUEEN_KING['sell_orders'] = []
        PollenDatabase.upsert_data(table_name, QUEEN_KING.get('key'), QUEEN_KING)
        
    if st.button("clear buy orders"):
        QUEEN_KING['buy_orders'] = []
        PollenDatabase.upsert_data(table_name, QUEEN_KING.get('key'), QUEEN_KING)
    
    # if admin:
    if st.button("Reset RevRec"):

        first_revrec_setup(QUEEN_KING)
