import streamlit as st
from streamlit_extras.switch_page_button import switch_page
from chess_piece.app_hive import set_streamlit_page_config_once, standard_AGgrid
from dotenv import load_dotenv
import os

set_streamlit_page_config_once()

if 'authentication_status' not in st.session_state or st.session_state['authentication_status'] != True:
    switch_page('pollen')

from chess_piece.king import print_line_of_error, master_swarm_KING
from chess_piece.queen_hive import init_queenbee, hive_master_root, pollen_themes, ReadPickleData, PickleData, refresh_tickers_TradingModels
from chess_piece.app_hive import page_line_seperator, create_AppRequest_package, return_image_upon_save


main_root = hive_master_root()
load_dotenv(os.path.join(main_root, ".env"))

client_user=st.session_state['client_user']
prod=st.session_state['prod']

KING = ReadPickleData(master_swarm_KING(prod=prod))

qb = init_queenbee(client_user, prod, queen=True, queen_king=True, api=True)
QUEEN = qb.get('QUEEN')
QUEEN_KING = qb.get('QUEEN_KING')
api = qb.get('api')

st.info(QUEEN_KING.keys())

st.header("order update requests")
st.write(QUEEN_KING['update_order_rules'])
if st.button('clear update order requests'):
    QUEEN_KING['update_order_rules'] = []
    PickleData(QUEEN_KING.get('source'), QUEEN_KING)
    st.success('app requests cleared')