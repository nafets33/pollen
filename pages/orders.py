#orders

import pandas as pd
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


from chess_piece.app_hive import set_streamlit_page_config_once, create_ag_grid_column, standard_AGgrid
from chess_piece.king import kingdom__grace_to_find_a_Queen, kingdom__global_vars
from chess_piece.queen_hive import create_QueenOrderBee, star_names, init_queenbee
from pq_auth import signin_main
from custom_button import cust_Button
from custom_grid import st_custom_grid, GridOptionsBuilder
from custom_graph_v1 import st_custom_graph

from streamlit_extras.switch_page_button import switch_page

def symbol_requesting_to_sell(queen_orders, symbol):

    return True


def config_orders_cols(active_order_state_list):
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
            'symbol': {},
            'ttf_grid_name': {'hide':True},
            'sell_reason': create_ag_grid_column(headerName="Reason To Sell", initialWidth=135, editable=True),
            'cost_basis_current': {'headerName': 'Cost Basis Current', "type": ["customNumberFormat", "numericColumn", "numberColumnFilter", ], # "customCurrencyFormat"
                                                        #    'custom_currency_symbol':"$",
                                                        "sortable":True,
                                                        'sort':'desc',
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
            'exit_order_link': {},
                    }


def order_grid(client_user, config_cols, KING, missing_cols, ip_address, seconds_to_market_close):
    gb = GridOptionsBuilder.create()
    gb.configure_grid_options(pagination=True, enableRangeSelection=True, copyHeadersToClipboard=False, sideBar=False)
    gb.configure_default_column(column_width=100, resizable=True, wrapText=False, wrapHeaderText=True, autoHeaderHeight=True, autoHeight=True, suppress_menu=False, filterable=True, sortable=True, ) # cellStyle= {"color": "white", "background-color": "gray"}   

    #Configure index field
    gb.configure_index('client_order_id')
    gb.configure_theme('ag-theme-material')


    for col, config_values in config_cols.items():
        config = config_values
        config['sortable'] = True
        gb.configure_column(col, config)
    if len(missing_cols) > 0:
        for col in missing_cols:
            gb.configure_column(col, {'hide': True})

    go = gb.build()
    

    refresh_sec = 0 #5 if seconds_to_market_close > 0 and mkhrs == 'open' else None
    st_custom_grid(
        client_user=client_user,
        username=KING['users_allowed_queen_emailname__db'].get(client_user), 
        api=f'{ip_address}/api/data/queen',
        api_update=f'{ip_address}/api/data/update_orders',
        refresh_sec=refresh_sec, 
        refresh_cutoff_sec=seconds_to_market_close, 
        prod=st.session_state['prod'],
        key='maingrid',
        grid_options=go,
        # kwargs from here
        api_key=os.environ.get("fastAPI_key"),
        buttons=[{'button_name': 'sell',
                'button_api': f'{ip_address}/api/data/queen_sell_orders',
                'prompt_message': 'Select Qty to Sell',
                'prompt_field': "sell_option",
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
                'col_width':133,
                'pinned': 'left',
                'prompt_order_rules': ['take_profit', 'sell_out', 'close_order_today', 'close_order_today_allowed_timeduration', 'stagger_profits_tiers', 'trade_using_limits', 'sell_trigbee_trigger', 'sell_trigbee_trigger_timeduration', 'sell_date', 'sell_trigbee_date', 'use_wave_guage'],
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
        grid_height='650px',
        toggle_views = ['ORDERS', 'QUEEN'] + ['buys', 'sells', 'today', 'close today'] + list(star_names().keys()) + ['FINAL'],
    )
    st.write("prod", st.session_state['prod'])
    # ORDERS = init_queenbee(client_user, prod, orders_final=True).get('ORDERS_FINAL')
    # standard_AGgrid(ORDERS['queen_orders'])


    if st.toggle("Broker Orders"):
        ORDERS = init_queenbee(client_user, prod, broker=True).get('BROKER')
        df = ORDERS['broker_orders']
        standard_AGgrid(df)

if __name__ == '__main__':

    
    signin_main(page="pollenq")
    # if 'authentication_status' not in st.session_state:
    #     print("SIGN IN")
    #     authenticator = 

    # if 'authentication_status' not in st.session_state or st.session_state['authentication_status'] != True:
    #     print("SWITCHING PAGES")
    #     switch_page('pollen')

    seconds_to_market_close = st.session_state['seconds_to_market_close'] if 'seconds_to_market_close' in st.session_state else 0
    # mkhrs = st.session_state['mkhrs']
    client_user = st.session_state['client_user']
    ip_address = st.session_state['ip_address']
    prod = st.session_state['prod']

    KING, users_allowed_queen_email, users_allowed_queen_emailname__db = kingdom__grace_to_find_a_Queen()

    queen_orders = pd.DataFrame([create_QueenOrderBee(queen_init=True)])

    king_G = kingdom__global_vars()
    active_order_state_list = king_G.get('active_order_state_list')
    config_cols = config_orders_cols(active_order_state_list)
    missing_cols = [i for i in queen_orders.iloc[-1].index.tolist() if i not in config_cols.keys()]
    
    order_grid(client_user, config_cols, KING, missing_cols, ip_address, seconds_to_market_close)