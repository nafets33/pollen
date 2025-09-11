import os
import streamlit.components.v1 as components
from decouple import config
from .grid_options_builder import GridOptionsBuilder  # Relative import
from .JsCode import JsCode, walk_gridOptions  # Relative import

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

    def convert_js_code(obj):
        if isinstance(obj, JsCode):
            return obj.js_code
        elif isinstance(obj, dict):
            return {k: convert_js_code(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_js_code(v) for v in obj]
        else:
            return obj

    # Convert all JsCode objects in kwargs
    kwargs = convert_js_code(kwargs)

    try:
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
    except TypeError as e:
        print(f"Custom grid failed to serialize: {e}")
        component_value = None
    return component_value


__all__ = [
    "st_custom_grid",  # The main function
    "GridOptionsBuilder",  # Utility class
    "JsCode",  # Utility class
    "walk_gridOptions",  # Utility function
]