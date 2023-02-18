import os
import streamlit.components.v1 as components


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


def ozz_bot(api_key, username, key=None):
    component_value = _component_func(
        api_key=api_key,
        username=username,
        key=key,
        default=0,
    )
    return component_value
