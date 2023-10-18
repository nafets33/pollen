import streamlit as st
from custom_voiceGPT import custom_voiceGPT, VoiceGPT_options_builder
from chess_piece.king import get_ip_address


def main():
    st.title("Testing Streamlit custom components")

    # Add Streamlit widgets to define the parameters for the CustomSlider
    ip_address = get_ip_address()
    to_builder = VoiceGPT_options_builder.create()
    to = to_builder.build()
    custom_voiceGPT(
        api=f"http://{ip_address}:8000/api/data/voiceGPT",
        self_image="hoots.png",
        face_recon=True,
        text_input=False,
        # keywords=["hey hootie", "hey hoots"],
        commands=[{
            "keywords": ["hey Hoots *", "hey Foods *", "hello *"],
            "api_body": {"keyword": "hey hoots, "},
            # "image_on_listen": "hootsAndHootie.png"
        },{
            "keywords": ["bye Hoots *", "bye Foods *", "bye *"],
            "api_body": {"keyword": "bye hoots, "},
            # "image_on_listen": "hoots.png"
        }
        ]
    )


if __name__ == "__main__":
    main()
