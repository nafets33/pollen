from chess_piece.app_hive import setup_page

import streamlit as st
from custom_voiceGPT import custom_voiceGPT, VoiceGPT_options_builder
from chess_piece.king import get_ip_address



st.title("Testing Streamlit custom components")

# Add Streamlit widgets to define the parameters for the CustomSlider
ip_address = get_ip_address()
if ip_address == '10.202.0.2':
    ip_address = "https://api.pollenq.com"
else:
    print("IP sandbox")
    ip_address = "http://127.0.0.1:8000"
st.session_state['ip_address'] = ip_address
to_builder = VoiceGPT_options_builder.create()
to = to_builder.build()
custom_voiceGPT(
    api=f"{ip_address}/api/data/voiceGPT",
    self_image="hoots.png",
    face_recon=True,
    text_input=False,
    hello_audio="test_audio.mp3",
    commands=[{
        "keywords": ["hey Hoots *", "hey hootie *", "hello *"],
        "api_body": {"keyword": "hey_hoots"},
    },{
        "keywords": ["bye Hoots *", "bye hootie *", "bye *"],
        "api_body": {"keyword": "bye_hoots"},
    }
    ]
)


