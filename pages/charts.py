

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

# import streamlit as st
# from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode, JsCode
# from streamlit_extras.stoggle import stoggle
# from streamlit_extras.switch_page_button import switch_page
import time
import os
import sqlite3
import time
import aiohttp
import asyncio
# import requests
# from requests.auth import HTTPBasicAuth
from chess_piece.app_hive import queen_messages_grid__apphive, custom_fastapi_text, symbols_unique_color, cust_graph, custom_graph_ttf_qcp, create_ag_grid_column, download_df_as_CSV, show_waves, send_email, pollenq_button_source, standard_AGgrid, create_AppRequest_package, create_wave_chart_all, create_slope_chart, create_wave_chart_single, create_wave_chart, create_guage_chart, create_main_macd_chart,  queen_order_flow, mark_down_text, mark_down_text, page_line_seperator, local_gif, flying_bee_gif, pollen__story
from chess_piece.king import get_ip_address, workerbee_dbs_backtesting_root__STORY_bee, return_all_client_users__db, kingdom__global_vars, return_QUEENs__symbols_data, hive_master_root, streamlit_config_colors, local__filepaths_misc, print_line_of_error, ReadPickleData, PickleData
from chess_piece.queen_hive import sell_button_dict_items, ttf_grid_names_list, buy_button_dict_items, wave_analysis__storybee_model, hive_dates, return_market_hours, init_ticker_stats__from_yahoo, refresh_chess_board__revrec, add_trading_model, set_chess_pieces_symbols, init_pollen_dbs, init_qcp, wave_gauge, return_STORYbee_trigbees, generate_TradingModel, stars, analyze_waves, pollen_themes, return_timestamp_string, init_logging

from custom_button import cust_Button
from custom_grid import st_custom_grid, GridOptionsBuilder
from custom_graph_v1 import st_custom_graph

from ozz.ozz_bee import send_ozz_call
# from chat_bot import ozz_bot


# from tqdm import tqdm

import ipdb


pd.options.mode.chained_assignment = None


# with charts_tab:
trading_days = hive_dates(api=api)['trading_days']
mkhrs = return_market_hours(trading_days=trading_days)
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
