import streamlit as st
from custom_graph import st_custom_graph


def main():
    st_custom_graph(symbols=["SPY"], 
                    prod=False, 
                    api_key="api_key", 
                    y_axis=[{
                        'field':'close',
                        'name':'CLOSE!!!',
                        'color':'#332d1a'
                        },
                        {
                        'field':'vwap',
                        'name':'VWAP!!!',
                        'color':'#2133dd'
                        }
                        
                        ])


if __name__ == '__main__':
    main()
