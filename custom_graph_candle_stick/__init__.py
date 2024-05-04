import os
import streamlit.components.v1 as components
from decouple import config

_RELEASE = True
# _RELEASE = False

if not _RELEASE:
    _component_func = components.declare_component(
        "custom_graph_candle_stick",
        url="http://localhost:3001",
    )
else:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "frontend", "build")
    _component_func = components.declare_component("custom_graph_candle_stick", path=build_dir)


def st_custom_graph_candle_stick(**kwargs):
    component_value = _component_func(kwargs=kwargs)
    return component_value
