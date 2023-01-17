import pandas as pd
import logging
import os
import pandas as pd
import datetime
import pytz
import ipdb
import matplotlib.pyplot as plt
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from itertools import islice
from PIL import Image
from dotenv import load_dotenv
import os
# from random import randint
import streamlit as st
from app_auth import signin_main
import time
from streamlit_extras.switch_page_button import switch_page
from appHive import live_sandbox__setup_switch, local_gif, mark_down_text, update_queencontrol_theme, progress_bar, page_line_seperator, return_runningbee_gif__save
from King import return_list_of_all__Queens__pkl, hive_master_root, streamlit_config_colors, local__filepaths_misc
import argparse
from streamlit_extras.stoggle import stoggle


### Read All Queens that have enabled public ### display as list of charcaters by category of investment strategy ###
# build time: 3 hours
# steps: loop queens dir dbs and ready queen, read if queen (queen, queen_sandbox) allowed to be public
# steps: reaad all queens and write list using .......

def public():

    est = pytz.timezone("US/Eastern")

    pd.options.mode.chained_assignment = None

    scriptname = os.path.basename(__file__)
    queens_chess_piece = os.path.basename(__file__)

    main_root = hive_master_root() # os.getcwd()  # hive root

    # images
    jpg_root = os.path.join(main_root, 'misc')

    MISC = local__filepaths_misc()
    bee_image = MISC['bee_image']
    castle_png = MISC['castle_png']
    bishop_png = MISC['bishop_png']
    queen_png = MISC['queen_png']
    mainpage_bee_png = MISC['mainpage_bee_png']
    floating_queen_gif = MISC['floating_queen_gif']
    chess_board__gif = MISC['chess_board__gif']
    knight_png = MISC['knight_png']
    bishop_unscreen = MISC['bishop_unscreen']
    flyingbee_grey_gif_path = MISC['flyingbee_grey_gif_path']
    alpaca_portfolio_keys_png = MISC['alpaca_portfolio_keys_png']
    

    
    page_icon = Image.open(bee_image)


    ##### STREAMLIT ###
    k_colors = streamlit_config_colors()
    default_text_color = k_colors['default_text_color'] # = '#59490A'
    default_font = k_colors['default_font'] # = "sans serif"
    default_yellow_color = k_colors['default_yellow_color'] # = '#C5B743'


    if 'sidebar_hide' in st.session_state:
        sidebar_hide = 'collapsed'
    else:
        sidebar_hide = 'expanded'

    st.set_page_config(
        page_title="pollenq",
        page_icon=page_icon,
        layout="wide",
        initial_sidebar_state=sidebar_hide,
        #  menu_items={
        #      'Get Help': 'https://www.extremelycoolapp.com/help',
        #      'Report a bug': "https://www.extremelycoolapp.com/bug",
        #      'About': "# This is a header. This is an *extremely* cool app!"
        #  }
    )
##################################################################################################################################
##################Page#####################################################################################################
####################################Setup######################################################################################
##################################################################################################################################
##################################################################################################################################


# all_queens = return_list_of_all__Queens__pkl()

# use async to read all queens data to show
