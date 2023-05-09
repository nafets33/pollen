import os
import streamlit.components.v1 as components
from decouple import config
from custom_grid.grid_options_builder import GridOptionsBuilder

# _RELEASE = True
_RELEASE = False

if not _RELEASE:
    _component_func = components.declare_component(
        "custom_graph",
        url="http://localhost:3001",
    )
else:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "frontend", "build")
    _component_func = components.declare_component(
        "custom_graph", path=build_dir)


def st_custom_graph():
    component_value = _component_func(
        )
    return component_value
