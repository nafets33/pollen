import os
import streamlit.components.v1 as components
import streamlit as st

st.markdown(
    """
        <style>
            .css-18e3th9 {
                    padding-top: 0rem;
                    padding-bottom: 0rem;
                    padding-left: 0rem;
                    padding-right: 0rem;
                }
            .css-1d391kg {
                    padding-top: 0rem;
                    padding-right: 0rem;
                    padding-bottom: 0rem;
                    padding-left: 0rem;
                }
                
                #MainMenu {visibility: hidden;}
                header {visibility: hidden;}
                footer {visibility : hidden;}
                body{ background : "black";}

        </style>
        """,
    unsafe_allow_html=True,
)

_RELEASE = True
if not _RELEASE:
    _component_func = components.declare_component(
        "my_component", url="http://localhost:3001/"
    )
else:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "frontend/build")
    _component_func = components.declare_component(
        "my_component",
        path=build_dir,
    )


def cust_Button(file_path_url, height, key=None):
    # This is a custom button
    # Parameter 1 = Enter the File Path or the URL
    # Parameter 2 = Set the Height in PX
    component_value = _component_func(
        file_path_url=file_path_url, height=height, key=key, default=0
    )
    return component_value
