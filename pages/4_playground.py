import streamlit as st
from streamlit_extras.stoggle import stoggle

# https://extras.streamlit.app/Annotated%20text

# st.set_page_config(
#     page_title="Hello",
#     page_icon="👋",
# )

st.write("# Welcome to Streamlit! 👋")


stoggle(
    "Click me!",
    """🥷 Surprise! Here's some additional content""",
)


html = """
  <style>
    /* Disable overlay (fullscreen mode) buttons */
    .overlayBtn {
      display: none;
    }

    /* Remove horizontal scroll */
    .element-container {
      width: auto !important;
    }

    .fullScreenFrame > div {
      width: auto !important;
    }

    /* 2nd thumbnail */
    .element-container:nth-child(4) {
      top: -266px;
      left: 350px;
    }

    /* 1st button */
    .element-container:nth-child(3) {
      left: 10px;
      top: -60px;
    }

    /* 2nd button */
    .element-container:nth-child(5) {
      left: 360px;
      top: -326px;
    }
  </style>
"""
st.markdown(html, unsafe_allow_html=True)

st.image("https://www.w3schools.com/howto/img_forest.jpg", width=300)
st.button("Show", key=1)

st.image("https://www.w3schools.com/howto/img_forest.jpg", width=300)
st.button("Show", key=2)


st.image("https://cdn.pixabay.com/photo/2012/04/18/00/42/chess-36311_960_720.png", width=33)