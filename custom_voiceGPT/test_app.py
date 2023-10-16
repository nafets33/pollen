import streamlit as st
from custom_voiceGPT import custom_voiceGPT, VoiceGPT_options_builder
from chess_piece.king import get_ip_address


def main():
    st.title("Testing Streamlit custom components")

    # Add Streamlit widgets to define the parameters for the CustomSlider
    ip_address = get_ip_address()
    to_builder = VoiceGPT_options_builder.create()
    to_builder.configure_background_color("yellow")
    to_builder.configure_text_color("#0d233a")
    to_builder.configure_font_style("italic")
    to = to_builder.build()
    custom_voiceGPT(
        api=f"http://{ip_address}:8000/api/data/text",
        self_image="",
        face_recon=True,
        text_input=False,
        keywords=["hey hootie", "hey hoots"],
    )


if __name__ == "__main__":
    main()
