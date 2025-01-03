import os
import streamlit.components.v1 as components
from custom_voiceGPT.options_builder import OptionsBuilder as VoiceGPT_options_builder

_RELEASE = True
# _RELEASE = False

if not _RELEASE:
    _component_func = components.declare_component(
        "custom_slider",
        url="http://localhost:3001",
    )
else:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "frontend", "build")
    _component_func = components.declare_component(
        "custom_voiceGPT", path=build_dir)

# Add label, min and max as input arguments of the wrapped function
# Pass them to _component_func which will deliver them to the frontend part


def custom_voiceGPT(api, key=None, text_option=None, **kwargs):
    component_value = _component_func(
        api=api,
        key=key,
        kwargs=kwargs,
    )
    return component_value
