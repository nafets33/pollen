
import streamlit as st
from streamlit_extras.switch_page_button import switch_page
from chess_piece.app_hive import set_streamlit_page_config_once
set_streamlit_page_config_once()
if 'authentication_status' not in st.session_state or st.session_state['authentication_status'] != True:
    switch_page('pollen')


import pandas as pd
import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import pytz
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from itertools import islice
from PIL import Image
from dotenv import load_dotenv
import random

import os
import time

from chess_piece.king import master_swarm_KING, ReadPickleData, kingdom__global_vars, return_QUEENs__symbols_data
from chess_piece.queen_hive import model_wave_results, init_queenbee, hive_master_root, refresh_chess_board__revrec, refresh_account_info
from chess_piece.app_hive import show_waves, pollenq_button_source
from custom_button import cust_Button
from custom_grid import st_custom_grid, GridOptionsBuilder
from custom_graph_v1 import st_custom_graph
import hydralit_components as hc



# from ...pollen.pq_auth import signin_main
# auth = signin_main("waves")
# ImportError: attempted relative import with no known parent package


main_root = hive_master_root()  # os.getcwd()
load_dotenv(os.path.join(main_root, ".env"))


import ipdb


pd.options.mode.chained_assignment = None

scriptname = os.path.basename(__file__)
queens_chess_piece = os.path.basename(__file__)

page = 'waves'
pq_buttons = pollenq_button_source()

# with st.sidebar:
# q_or_qk_toggle = st.toggle("QUEEN King RevRec", False)
# with st.sidebar:
# q_or_qk_toggle = st.toggle("QUEEN RevRec", False)
hc_source_option = hc.option_bar(option_definition=pq_buttons.get('waves_queen_qk_source_toggle'),title='Source', key='waves_revrec_source', horizontal_orientation=True) #,override_theme=over_theme,font_styling=font_fmt,horizontal_orientation=True)

KING = ReadPickleData(master_swarm_KING(st.session_state['prod']))
king_G = kingdom__global_vars()
active_order_state_list = king_G.get('active_order_state_list') # = ['running', 'running_close', 'submitted', 'error', 'pending', 'completed', 'completed_alpaca', 'running_open', 'archived_bee']
active_queen_order_states = king_G.get('active_queen_order_states')

client_user=st.session_state['client_user']
prod=st.session_state['prod']

qb = init_queenbee(client_user, prod, queen=True, queen_king=True, api=True)
QUEEN = qb.get('QUEEN')
QUEEN_KING = qb.get('QUEEN_KING')
api = qb.get('api')

coin_exchange = "CBSE"
ticker_db = return_QUEENs__symbols_data(QUEEN=QUEEN, QUEEN_KING=QUEEN_KING, swarmQueen=False, read_pollenstory=False)
# POLLENSTORY = ticker_db['pollenstory']
STORY_bee = ticker_db['STORY_bee']
# ticker_allowed = list(KING['ticker_universe'].get('alpaca_symbols_dict').keys()) # + crypto_symbols__tickers_avail
# st.write(STORY_bee.keys())
if hc_source_option == 'waves_revrec_queen':
    revrec = QUEEN.get('revrec')
elif hc_source_option == 'waves_revrec_king':
    revrec = QUEEN_KING.get('revrec')
else:
    acct_info = QUEEN.get('account_info')
    # acct_info = refresh_account_info(api=api)['info_converted']
    revrec = refresh_chess_board__revrec(acct_info, QUEEN, QUEEN_KING, STORY_bee, active_queen_order_states, chess_board__revrec={}, revrec__ticker={}, revrec__stars={}) ## Setup Board

# ipdb.set_trace()
# wave_analysis = revrec.get('df_storyview')
# wave_analysis['wave_count'] = wave_analysis['winners'] + wave_analysis['losers']

# wave_analysis['sum_maxprofit'] = wave_analysis['sum_maxprofit'] / wave_analysis['wave_count']
# st.write(wave_analysis)
tabs = st.tabs([key for key in revrec.keys()])
tab = 0
for revrec_key in revrec.keys():
    with tabs[tab]:
        st.write(revrec_key)
        st.write(revrec.get(revrec_key))
    
    tab+=1

if st.toggle("wave stories", True):
    with st.expander("wave stories"):
        ticker_option = st.selectbox("ticker", options=STORY_bee.get('tickers_avail'))
        frame_option = st.selectbox("frame", options=KING['star_times'])
        show_waves(STORY_bee=STORY_bee, ticker_option=ticker_option, frame_option=frame_option)

        ticker_time_frame = f'{ticker_option}_{frame_option}'

        wave_series = STORY_bee[ticker_time_frame]["waves"]["buy_cross-0"]

        st.dataframe(wave_series)

# for key, value in revrec.items():
#     st.write(key)
#     st.write(revrec.get(key))


# ticker_option = st.selectbox("ticker", options=tickers_avail)
# frame_option = st.selectbox("frame", options=KING['star_times'])
# show_waves(STORY_bee=STORY_bee, ticker_option=ticker_option, frame_option=frame_option)


# waves, analyzed_waves = model_wave_results(STORY_bee)
# st.write(waves)
# st.write(analyzed_waves)

# import streamlit as st
# import streamlit_antd_components as sac
# def display_tree_from_dict(data_dict):
#     items = []
    
#     def convert_to_tree_dict(data, parent_key=''):
#         tree_dict = []

#         for key, value in data.items():
#             item = {'title': key}

#             if isinstance(value, dict):
#                 item['children'] = convert_to_tree_dict(value, parent_key=f"{parent_key}/{key}" if parent_key else key)
#             elif isinstance(value, list):
#                 item['children'] = [{'title': f"[{i}]" } for i in range(len(value))]
#             elif isinstance(value, pd.DataFrame):
#                 item['title'] = f"{key} (DataFrame)"
#             else:
#                 item['title'] = f"{key}: {value}"

#             tree_dict.append(item)
        
#         return tree_dict

#     items = convert_to_tree_dict(data_dict)
    
#     selected_items = st.checkbox("Select items:", True)
#     selected_data = {}

#     # Set default checked status based on selected_items
#     default_checked = {item['title']: item['title'] in selected_items for item in items}

#     tree_data = sac.checkbox_tree(
#         items=items,
#         label='label',
#         index=0,
#         format_func='title',
#         icon='table',
#         open_all=True,
#         default=default_checked  # Use default to set checked status
#     )

#     # Process selected items
#     def process_selected_items(tree_data, parent_key=''):
#         nonlocal selected_data
#         for item in tree_data:
#             key = f"{parent_key}/{item['title']}" if parent_key else item['title']
#             if item.get('checked', False):
#                 selected_data[key] = data_dict.get(item['title'], None)
#             if 'children' in item:
#                 process_selected_items(item['children'], parent_key=key)

#     process_selected_items(tree_data)
    
#     # Display selected data
#     st.write("Selected Data:")
#     st.write(selected_data)

# # Example usage:
# my_dict = {
#     'name': 'John',
#     'age': 30,
#     'address': {
#         'city': 'New York',
#         'state': 'NY'
#     },
#     'grades': [90, 85, 92],
#     'dataframe': pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
# }

# st.title("Streamlit App with Checkbox Tree")
# display_tree_from_dict(my_dict)