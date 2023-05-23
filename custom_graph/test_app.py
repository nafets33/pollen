import streamlit as st
from custom_graph import st_custom_graph


def main():
    st_custom_graph(
        api="http://localhost:8000/api/data/symbol_graph",
        prod=False,
        symbols=["SPY"],
        api_key="api_key",
        refresh_sec=10,
        y_axis=[{
            'field': 'close',
            'name': 'CLOSE!!!',
            'color': '#332d1a'
        },
            {
            'field': 'vwap',
            'name': 'VWAP!!!',
            'color': '#2133dd'
        }
        ],
        y_max=430)


if __name__ == '__main__':
    main()
