import streamlit.components.v1 as components
from decouple import config
import os

_RELEASE = True
# _RELEASE = False

if not _RELEASE:
    _component_func = components.declare_component(
        "custom_slider",
        url="http://localhost:3001",
    )
else:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "frontend","build")
    _component_func = components.declare_component("custom_text", path=build_dir)

# Add label, min and max as input arguments of the wrapped function
# Pass them to _component_func which will deliver them to the frontend part


def custom_text(api, text_size = 10, refresh_sec = 1, refresh_cutoff_sec = 0):
    component_value = _component_func(
        api=api,
        text_size= text_size,
        refresh_sec = refresh_sec,
        refresh_cutoff_sec = refresh_cutoff_sec,
    )
    return component_value
