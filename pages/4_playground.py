import streamlit as st
from streamlit_extras.stoggle import stoggle
from chess_piece.app_hive import click_button_grid, nested_grid, page_tab_permission_denied, standard_AGgrid
from chess_piece.king import hive_master_root, local__filepaths_misc, ReadPickleData, return_QUEENs__symbols_data
from PIL import Image
from app_auth import signin_main

# https://extras.streamlit.app/Annotated%20text

st.set_page_config(
    page_title="pollenq",
    # page_icon=page_icon,
    layout="wide",
    # initial_sidebar_state=sidebar_hide,
    #  menu_items={
    #      'Get Help': 'https://www.extremelycoolapp.com/help',
    #      'Report a bug': "https://www.extremelycoolapp.com/bug",
    #      'About': "# This is a header. This is an *extremely* cool app!"
    #  }
)

st.write("# Welcome to Playground! 👋")

if 'username' not in st.session_state:
    signin_main()

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

learningwalk_bee = Image.open(learningwalk_bee)


view_ss_state = st.sidebar.button("View Session State")
if view_ss_state:
    st.write(st.session_state)


page_tab_permission_denied(st.session_state['admin'])
with st.expander("button on grid"):
    click_button_grid()

with st.expander("nested grid"):
    nested_grid()

QUEEN = ReadPickleData(st.session_state['PB_QUEEN_Pickle'])
ticker_db = return_QUEENs__symbols_data(QUEEN=QUEEN)
POLLENSTORY = ticker_db['pollenstory']
STORY_bee = ticker_db['STORY_bee']

with st.expander("pollenstory"):
  ttf = st.selectbox('ttf', list(STORY_bee.keys())) # index=['no'].index('no'))

  grid = standard_AGgrid(data=POLLENSTORY[ttf], configure_side_bar=True)


# admin_user_swap = st.number_input("fast", min_value=1, max_value=10000, value=0)
# if st.button("swap"): 
#     if admin_user_swap == 89:
#         d = list(os.listdir(client_dbs_root()))
#         d = [i.split("db__")[1] for i in d]
#         admin_client_user = st.sidebar.selectbox('admin client_users', options=d, index=d.index(db_client_user_name))
#         if st.sidebar.button('admin change user'):
#             st.session_state['admin__client_user'] = admin_client_user
#             switch_page("pollenq")

# stoggle(
#     "Click me!",
#     """🥷 Surprise! Here's some additional content""",
# )


# html = """
#   <style>
#     /* Disable overlay (fullscreen mode) buttons */
#     .overlayBtn {
#       display: none;
#     }

#     /* Remove horizontal scroll */
#     .element-container {
#       width: auto !important;
#     }

#     .fullScreenFrame > div {
#       width: auto !important;
#     }

#     /* 2nd thumbnail */
#     .element-container:nth-child(4) {
#       top: -266px;
#       left: 350px;
#     }

#     /* 1st button */
#     .element-container:nth-child(3) {
#       left: 10px;
#       top: -60px;
#     }

#     /* 2nd button */
#     .element-container:nth-child(5) {
#       left: 360px;
#       top: -326px;
#     }
#   </style>
# """
# st.markdown(html, unsafe_allow_html=True)

# st.image("https://www.w3schools.com/howto/img_forest.jpg", width=300)
# st.button("Show", key=1)

# # img=st.image("https://www.w3schools.com/howto/img_forest.jpg", width=300)
# st.button("Show:key:", key=2)

# st.button('name', st.image(learningwalk_bee, width=33))


# st.image("https://cdn.pixabay.com/photo/2012/04/18/00/42/chess-36311_960_720.png", width=33)

