import pandas as pd
import logging
import os
import pandas as pd
import datetime
import pytz
import ipdb
# import matplotlib.pyplot as plt
# from plotly.subplots import make_subplots
# import plotly.graph_objects as go
# from itertools import islice
from PIL import Image
from dotenv import load_dotenv
import os
# from random import randint
import streamlit as st
from polleq_app_auth import signin_main
import time
# from streamlit_extras.switch_page_button import switch_page
import argparse
from streamlit_extras.stoggle import stoggle
from chess_piece.app_hive import display_for_unAuth_client_user, queen__account_keys, local_gif, mark_down_text, update_queencontrol_theme, progress_bar, page_line_seperator, return_runningbee_gif__save
from chess_piece.king import menu_bar_selection, kingdom__grace_to_find_a_Queen, streamlit_config_colors, local__filepaths_misc, ReadPickleData, PickleData, client_dbs_root
from chess_piece.queen_hive import add_key_to_app, init_pollen_dbs, KINGME, pollen_themes
from custom_button import cust_Button
# import hydralit_components as hc
from pollenq_pages.playground import PlayGround
from pollenq_pages.queens_conscience import queens_conscience
from ozz.ozz_bee import send_ozz_call

# import sys, importlib
# importlib.reload(sys.modules['pollenq_pages.queens_conscience'])

pd.options.mode.chained_assignment = None
# https://blog.streamlit.io/a-new-streamlit-theme-for-altair-and-plotly/
# https://discuss.streamlit.io/t/how-to-animate-a-line-chart/164/6 ## animiate the Bees Images : )
# https://blog.streamlit.io/introducing-theming/  # change theme colors
# https://extras.streamlit.app
# https://www.freeformatter.com/cron-expression-generator-quartz.html
# http://34.162.236.105:8080/home # dags
# https://docs.google.com/spreadsheets/d/1ddqj-EkO1MluAjDg-U-DyCzJvtFjRN-9SfEYXkB8eNo/edit#gid=0 # track hours
# https://unicode.org/emoji/charts/full-emoji-list.html#1fae0

# scriptname = os.path.basename(__file__)
# queens_chess_piece = os.path.basename(__file__)


def account(admin_pq):

    ##### STREAMLIT ###
    k_colors = streamlit_config_colors()
    default_text_color = k_colors['default_text_color'] # = '#59490A'
    default_font = k_colors['default_font'] # = "sans serif"
    default_yellow_color = k_colors['default_yellow_color'] # = '#C5B743'


    with st.spinner("Hello Welcome To pollenq a Kings Queen"):
        # signin_main(page="Account")
        st.write("# WORKER BEES WORKING")
    

    return True
if __name__ == '__main__':
    account()