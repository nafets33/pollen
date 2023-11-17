from chess_piece.app_hive import setup_page
from chess_piece.king import hive_master_root
from chess_piece.app_hive import set_streamlit_page_config_once, sac_menu_buttons

import streamlit as st
from custom_voiceGPT import custom_voiceGPT, VoiceGPT_options_builder
from chess_piece.king import get_ip_address, return_app_ip
import os
from dotenv import load_dotenv

main_root = hive_master_root()  # os.getcwd()
load_dotenv(os.path.join(main_root, ".env"))

set_streamlit_page_config_once()
ip_address, streamlit_ip = return_app_ip()

sac_menu_buttons('Account')

st.title("Testing Streamlit custom components")

# Add Streamlit widgets to define the parameters for the CustomSlider

to_builder = VoiceGPT_options_builder.create()
to = to_builder.build()
# if st.session_state['username'] not in users_allowed_queen_email
custom_voiceGPT(
    api=f"{st.session_state['ip_address']}/api/data/voiceGPT",
    self_image="hoots.png",
    width=150,
    height=200,
    hello_audio="test_audio.mp3",
    face_recon=True,
    show_video=True,
    input_text=True,
    show_conversation=True,
    no_response_time=3,
    commands=[{
        "keywords": ["hey Hoots", "hey Foods", "hello"], # keywords are case insensitive
        "api_body": {"keyword": "hey hoots"},
    }, {
        "keywords": ["bye Hoots", "bye Foods", "bye"],
        "api_body": {"keyword": "bye hoots"},
    }
    ]
)

