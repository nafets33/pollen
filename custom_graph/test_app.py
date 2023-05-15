import streamlit as st
from custom_graph import st_custom_graph


def main():
    st_custom_graph(symbols=["SPY"], prod=False, api_key="api_key")


if __name__ == '__main__':
    main()
