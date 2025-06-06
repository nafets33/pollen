import os
import streamlit.components.v1 as components
from decouple import config
from custom_grid.grid_options_builder import GridOptionsBuilder
from custom_grid.JsCode import JsCode, walk_gridOptions

_RELEASE = True
# _RELEASE = False  #When using this, you need to start the server for the frontend using npm start on a terminal session.

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
    enable_JsCode=True,
    **kwargs
):
    if enable_JsCode:
        walk_gridOptions(
            grid_options, lambda v: v.js_code if isinstance(v, JsCode) else v
        )

        # as buttons are sent in a separated kwargs parameter and later merged on the 
        # grid options (AgGrid.tsx line # 198), we'll need to serialize any JsCode 
        # object as as string, the same way we do for normal grid options.
        # aftter we change the buttons dictionary, we add it back to kwargs
        if 'buttons' in kwargs:
            buttons = kwargs.pop('buttons')
            for b in buttons:
                walk_gridOptions(
                    b, lambda v: v.js_code if isinstance(v, JsCode) else v
                )
            kwargs['buttons'] = buttons



    component_value = _component_func(
        username=username,
        api=api,
        api_update=api_update,
        refresh_sec=refresh_sec,
        refresh_cutoff_sec=refresh_cutoff_sec,
        prod=prod,
        key=key,
        grid_options=grid_options,
        enable_JsCode=enable_JsCode,
        kwargs=kwargs,
    )
    return component_value
