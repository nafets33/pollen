import streamlit as st
from custom_graph_v1 import st_custom_graph


def main():
    st_custom_graph(
        api="http://127.0.0.1:8000/api/data/symbol_graph",
        prod=False,
        symbols=["SPY"],
        api_key="fastapi_pollenq_key",
        refresh_sec=0,
        x_axis={"field": "timestamp_est"},
        y_axis=[
            {"field": "close", "name": "CLOSE!!!", "color": "#332d1a"},
            {"field": "vwap", "name": "VWAP!!!", "color": "#2133dd"},
        ],
        y_max=430,
        theme_options={
            "backgroundColor": "#F5DEB3",
            "main_title": "Main title",  # '' for none
            "x_axis_title": "X-Axis title",
            "grid_color": "black",
            "showInLegend": False,
            "showInLegendPerLine": False,
        },
        refresh_button=True,
        graph_height=500,
    )


if __name__ == "__main__":
    main()
