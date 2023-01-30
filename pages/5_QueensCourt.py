import streamlit as st
from streamlit_extras.stoggle import stoggle
from PIL import Image
import subprocess
from polleq_app_auth import signin_main
from chess_piece.app_hive import local_gif, click_button_grid, nested_grid, page_tab_permission_denied, standard_AGgrid
from chess_piece.king import copy_directory, hive_master_root, local__filepaths_misc, kingdom__grace_to_find_a_Queen, ReadPickleData, return_QUEENs__symbols_data

from custom_button import cust_Button

# https://extras.streamlit.app/Annotated%20text

st.set_page_config(
    page_title="PlayGround",
    # page_icon=page_icon,
    layout="wide",
    # initial_sidebar_state=sidebar_hide,
    #  menu_items={
    #      'Get Help': 'https://www.extremelycoolapp.com/help',
    #      'Report a bug': "https://www.extremelycoolapp.com/bug",
    #      'About': "# This is a header. This is an *extremely* cool app!"
    #  }
)

signin_main(page="QueensCourt")
page_tab_permission_denied(admin=st.session_state['admin']) # stopper

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
# hexagon_loop = MISC['hexagon_loop']
# purple_heartbeat_gif = MISC['purple_heartbeat_gif'] MISC.get('puprple')

moving_ticker_gif = MISC['moving_ticker_gif']
# heart_bee_gif = MISC['heart_bee_gif']



with st.form('Copy Directory'):

    src = st.text_input(label=f'src', value='/home/stapinski89/pollen/pollen/client_user_dbs/1', key='src_copy')
    dst = st.text_input(label=f'dst', value='/home/stapinski89/pollen/pollen/client_user_dbs/2', key='src_dst')
    if st.form_submit_button('replace files from src to dst directory'):
        copy_directory(src=src, dst=dst)
        st.write("Copy Completed")


# if admin:
#     st.write('admin:', admin)
#     d = list(os.listdir(client_dbs_root()))
#     d = [i.split("db__")[1] for i in d]
#     admin_client_user = st.sidebar.selectbox('admin client_users', options=d, index=d.index(client_user))
#     if st.sidebar.button('admin change user'):
#         st.session_state['admin__client_user'] = admin_client_user
#         switch_page("pollenq")