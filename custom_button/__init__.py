import os
import streamlit.components.v1 as components
import streamlit as st


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


def cust_Button(file_path_url, height, hoverText=None, key=None):
    component_value = _component_func(
        file_path_url=file_path_url,
        height=height,
        hoverText=hoverText,
        key=key,
        default=0,
    )
    return component_value
