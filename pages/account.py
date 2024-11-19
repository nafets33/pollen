from chess_piece.app_hive import sac_menu_buttons, set_streamlit_page_config_once, queen__account_keys
from chess_piece.king import hive_master_root, return_app_ip
from chess_piece.queen_hive import init_queenbee
from pq_auth import signin_main, reset_password, forgot_password

import streamlit as st
from custom_voiceGPT import custom_voiceGPT, VoiceGPT_options_builder
from chess_piece.king import get_ip_address
import os
from dotenv import load_dotenv
from streamlit_extras.switch_page_button import switch_page


main_root = hive_master_root()  # os.getcwd()
load_dotenv(os.path.join(main_root, ".env"))

set_streamlit_page_config_once()

ip_address = return_app_ip()

st.title("Your Account")

menu = sac_menu_buttons("Account")    
if menu.lower() == 'queen':
    switch_page('pollen')

authenticator = signin_main(page="account")
email = st.session_state['auth_email']

cols = st.columns(3)
if 'logout' in st.session_state and st.session_state["logout"] != True:
    with cols[0]:
        authenticator.logout("Logout", location='main')
# with cols[1]:
    with st.expander("Forgot Password", expanded=True):
        forgot_password(authenticator)
# with cols[2]:
    reset_password(authenticator, email, location='main')


if st.button('show_keys'):
    QUEEN_KING = init_queenbee(client_user=st.session_state['client_user'], prod=st.session_state['prod'], queen_king=True).get('QUEEN_KING')
    queen__account_keys(QUEEN_KING=QUEEN_KING, authorized_user=st.session_state['authorized_user'], show_form=True) #EDRXZ Maever65teo

