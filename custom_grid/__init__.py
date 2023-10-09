import os
import streamlit.components.v1 as components
from decouple import config
from custom_grid.grid_options_builder import GridOptionsBuilder

_RELEASE = True
# _RELEASE = False

if not _RELEASE:
    _component_func = components.declare_component(
        "custom_grid",
        url="http://localhost:3001",
    )
else:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "frontend", "build")
    _component_func = components.declare_component("custom_grid", path=build_dir)


def st_custom_grid(
    username: str,
    api: str,
    api_update: str,
    refresh_sec: int,
    refresh_cutoff_sec: int,
    prod: bool,
    key: str,
    grid_options,
    **kwargs
):
    component_value = _component_func(
        username=username,
        api=api,
        api_update=api_update,
        refresh_sec=refresh_sec,
        refresh_cutoff_sec=refresh_cutoff_sec,
        prod=prod,
        key=key,
        grid_options=grid_options,
        kwargs=kwargs,
    )
    return component_value
