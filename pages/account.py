from chess_piece.app_hive import sac_menu_buttons, set_streamlit_page_config_once
from chess_piece.king import hive_master_root, return_app_ip
from pq_auth import signin_main, reset_password, forgot_password

import streamlit as st
from custom_voiceGPT import custom_voiceGPT, VoiceGPT_options_builder
from chess_piece.king import get_ip_address
import os
from dotenv import load_dotenv

main_root = hive_master_root()  # os.getcwd()
load_dotenv(os.path.join(main_root, ".env"))

set_streamlit_page_config_once()

ip_address, streamlit_ip = return_app_ip()

st.title("Your Account")
sac_menu_buttons("Account")

authenticator = signin_main(page="account")
email = st.session_state['auth_email']

authenticator.logout("Logout", location='main')

with st.expander("Forgot Password", expanded=True):
    forgot_password(authenticator)


reset_password(authenticator, email, location='main')



