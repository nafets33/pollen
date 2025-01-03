import streamlit as st
from custom_voiceGPT import custom_voiceGPT, VoiceGPT_options_builder
from chess_piece.king import get_ip_address


def main():

    # Add Streamlit widgets to define the parameters for the CustomSlider
    ip_address = 'localhost'
    # ip_address = get_ip_address()
    to_builder = VoiceGPT_options_builder.create()
    to = to_builder.build()
    custom_voiceGPT(
        api=f"http://{ip_address}:8000/api/data/voiceGPT",
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


if __name__ == "__main__":
    main()
