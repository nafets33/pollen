import streamlit as st
from streamlit_extras.stoggle import stoggle
from PIL import Image
import subprocess
from custom_grid import st_custom_grid
from pq_auth import signin_main
from chess_piece.queen_hive import print_line_of_error, init_swarm_dbs
from chess_piece.app_hive import set_streamlit_page_config_once, show_waves,  standard_AGgrid
from chess_piece.king import kingdom__grace_to_find_a_Queen, hive_master_root, local__filepaths_misc, ReadPickleData, PickleData, return_QUEENs__symbols_data
from custom_button import cust_Button
from streamlit_option_menu import option_menu
from datetime import datetime, timedelta
import hydralit_components as hc
# from ozz.ozz_bee import send_ozz_call
import pytz
import ipdb
import pandas as pd
import numpy as np
from chat_bot import ozz_bot
import os
# from st_on_hover_tabs import on_hover_tabs
from streamlit_extras.switch_page_button import switch_page
import yfinance as yf
import time

from plotly.subplots import make_subplots
import plotly.graph_objects as go

set_streamlit_page_config_once()

def delete_dict_keys(object_dict):
    bishop_screens = st.selectbox("Bishop Screens", options=list(object_dict.keys()))
    if st.button("Delete Screen"):
        object_dict.pop(bishop_screens)
        PickleData(object_dict.get('source'), object_dict)
        st.success(f"{bishop_screens} Deleted")


def refresh_yfinance_ticker_info(main_symbols_full_list):
    s = datetime.now()
    all_info = {}
    sectors = {}

    # Initialize the progress bar outside the loop
    progress_text = "Operation in progress. Please wait. ({percent}%)"
    my_bar = st.progress(0)

    max_tickers = len(main_symbols_full_list)

    for idx, tic in enumerate(main_symbols_full_list):
        try:
            ticker = yf.Ticker(tic)
            all_info[tic] = ticker.info
            sectors[tic] = ticker.info.get('sector')

            # Update the progress bar with the correct progress and percentage
            progress_percent = (idx + 1) / max_tickers * 100
            my_bar.progress((idx + 1) / max_tickers, text=progress_text.format(percent=int(progress_percent)))
        except Exception as e:
            print_line_of_error(tic)

    my_bar.empty()

    df = pd.DataFrame()

    # Reset progress bar for the second loop
    progress_text = "Processing tickers... ({percent}%)"
    my_bar = st.progress(0)

    total_tickers = len(all_info)

    for idx, (tic, data) in enumerate(all_info.items(), start=1):
        progress_percent = idx / total_tickers * 100
        my_bar.progress(idx / total_tickers, text=progress_text.format(percent=int(progress_percent)))

        token = pd.DataFrame(data.items()).T
        headers = token.iloc[0]
        token.columns = headers
        token = token.drop(0)
        token['ticker'] = tic
        df = pd.concat([df, token], ignore_index=True)

    my_bar.empty()  # Clear the progress bar after the loop completes

    print((datetime.now() - s).total_seconds())
    return df


def PlayGround():

    if 'authentication_status' not in st.session_state:
        authenticator = signin_main(page="pollenq")

    if 'authentication_status' not in st.session_state or st.session_state['authentication_status'] != True:
        switch_page('pollen')
    
    prod = st.session_state['prod']
    
    print("PLAYGROUND", st.session_state['client_user'])
    db=init_swarm_dbs(prod)
    BISHOP = ReadPickleData(db.get('BISHOP'))

    delete_dict_keys(BISHOP)

    try:

        # images
        MISC = local__filepaths_misc()
        learningwalk_bee = MISC['learningwalk_bee']
        mainpage_bee_png = MISC['mainpage_bee_png']

        est = pytz.timezone("US/Eastern")
        utc = pytz.timezone('UTC')
        
        
        cols = st.columns(4)
        with cols[0]:
            st.write("# Welcome to Playground! 👋")
        with cols[1]:
            # st.image(MISC.get('mainpage_bee_png'))
            st.write(st.color_picker("colors"))
        with cols[2]:
            cB = cust_Button(file_path_url="misc/learningwalks_bee_jq.png", height='23px', key='b1', hoverText="HelloMate")
            if cB:
                st.write("Thank you Akash")
        with cols[3]:
            st.image(MISC.get('mainpage_bee_png'))
    
        
        QUEEN = ReadPickleData(st.session_state['PB_QUEEN_Pickle'])
        
        PB_App_Pickle = st.session_state['PB_App_Pickle']
        QUEEN_KING = ReadPickleData(pickle_file=PB_App_Pickle)
        ticker_db = return_QUEENs__symbols_data(QUEEN=QUEEN, QUEEN_KING=QUEEN_KING)
        POLLENSTORY = ticker_db['pollenstory']
        STORY_bee = ticker_db['STORY_bee']
        tickers_avail = [set(i.split("_")[0] for i in STORY_bee.keys())][0]
        KING, users_allowed_queen_email, users_allowed_queen_emailname__db = kingdom__grace_to_find_a_Queen()


        # ticker_universe = return_Ticker_Universe()
        # alpaca_symbols_dict = ticker_universe.get('alpaca_symbols_dict')
        # alpaca_symbols = {k: i['_raw'] for k,i in alpaca_symbols_dict.items()}
        # df = pd.DataFrame(alpaca_symbols).T
        alpaca_symbols_dict = KING.get('alpaca_symbols_dict')
        # print(alpaca_symbols_dict['SPY']['_raw'].get('exchange'))
        # st.write(alpaca_symbols_dict)
        df = KING.get('alpaca_symbols_df')
        st.write("all symbols")
        with st.expander("all symbols"):
            standard_AGgrid(df)


        st.markdown("[![Click me](app/static/cat.png)](https://pollenq.com)",unsafe_allow_html=True)
        cols = st.columns(2)
        # with cols[0]:
        #     with st.expander('nested columns'):
        #         cols_2 = st.columns(2)
        #         with cols_2[1]:
        #             st.markdown("[![Click me](app/static/cat.png)](https://pollenq.com)",unsafe_allow_html=True)
        
        # with st.expander("button on grid"):
        #     click_button_grid()
        # if st.toggle("nested grid"):
        #     with st.expander("nested grid"):
        #         nested_grid()

        # if st.toggle("pollenstory"):
        with st.expander("pollenstory"):
            ttf = st.selectbox('ttf', list(STORY_bee.keys())) # index=['no'].index('no'))
            data=POLLENSTORY[ttf]
            data['trinity_avg_tier'] = sum(data['trinity_tier']) / len(data)
            default_cols = ['timestamp_est', 'open', 'close', 'high', 'low', 'buy_cross-0', 'buy_cross-0__wave_number', 'trinity_tier', 'trinity_avg_tier']
            cols = st.multiselect('qcp', options=data.columns.tolist(), default=default_cols)
            view=data[cols].copy()
            view = data.reset_index()
            grid = standard_AGgrid(data=view, configure_side_bar=True)

            def create_wave_chart(df):
                title = f'i know'
                fig = make_subplots(rows=1, cols=1, shared_xaxes=True, vertical_spacing=0.01)
                df = df.copy()
                # df['timestamp_est'] = df['timestamp_est'].apply(lambda x: f'{x.month}{"-"}{x.day}{"_"}{x.hour}{":"}{x.minute}')

                fig.add_bar(x=df['timestamp_est'], y=df['trinity_tier'],  row=1, col=1, name='trinity')
                fig.add_bar(x=df['timestamp_est'], y=df['trinity_avg_tier'],  row=1, col=1, name='sellcross wave')
                fig.update_layout(height=600, width=900, title_text=title)
                return fig
            create_wave_chart(data)

        # if st.toggle("wave stories"):
        with st.expander("wave stories"):
            ticker_option = st.selectbox("ticker", options=tickers_avail)
            frame_option = st.selectbox("frame", options=KING['star_times'])
            show_waves(STORY_bee=STORY_bee, ticker_option=ticker_option, frame_option=frame_option)


        if st.toggle("yahoo", True):
            db_qb_root = os.path.join(hive_master_root(), "db")
            yahoo_stats_bee = os.path.join(db_qb_root, "yahoo_stats_bee.pkl")
            db = ReadPickleData(yahoo_stats_bee)
            # st.write(db['AAPL'])
            

            if st.button("Refresh ALL yahoo ticker info from BISHOP"):
                ticker_universe = KING['alpaca_symbols_df']
                main_symbols_full_list = ticker_universe['symbol'].tolist()

                df_info = refresh_yfinance_ticker_info(main_symbols_full_list)
                if type(df_info) == pd.core.frame.DataFrame:
                    BISHOP['ticker_info'] = df_info
                    PickleData(BISHOP.get('source'), BISHOP, console=True)
        
        if st.button("Sync Queen King Symbol Yahoo Stats"):
            symbols = [item for sublist in [v.get('tickers') for v in QUEEN_KING['chess_board'].values()] for item in sublist]
            df_info = refresh_yfinance_ticker_info(symbols)
            if type(df_info) == pd.core.frame.DataFrame:
                BISHOP['queen_story_symbol_stats'] = df_info
                PickleData(BISHOP.get('source'), BISHOP, console=True)
        
        if 'queen_story_symbol_stats' in BISHOP.keys():
            st.header("QK Yahoo Stats")
            standard_AGgrid(BISHOP['queen_story_symbol_stats'])
        
        if 'ticker_info' in BISHOP.keys():
            cols = st.columns(3)
            with cols[0]:
                market_cap = st.number_input("marker cap >=", value=50000000)
                volume = st.number_input("volume >=", value=1000000)
            with cols[1]:
                shortRatio = st.number_input("shortRatio <=", value=2)
                ebitdaMargins = st.number_input("ebitdaMargins >=", min_value=-1.0, max_value=1.0, value=.25)
            
            show_all = st.toggle("show all tickers")
            df = BISHOP.get('ticker_info')
            hide_cols = df.columns.tolist()
            
            view_cols = ['symbol', 'sector', 'shortName']
            num_cols = ['dividendRate', 'dividendYield', 'volume', 'averageVolume', 'marketCap', 'shortRatio', 'ebitdaMargins']
            hide_cols = [i for i in hide_cols if i not in view_cols + num_cols]
            
            def clean_ticker_info_df(df):
                df = df.fillna('')
                df = df[df['sector']!='']
                for col in num_cols:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                
                return df
            
            df=clean_ticker_info_df(df)

            avail_symbols = KING['alpaca_symbols_df']['symbol'].tolist()
            df = df[df['symbol'].isin(avail_symbols)]
            # screener
            def stock_screen(df, market_cap=50000000, volume=1000000, shortRatio=2, ebitdaMargins=.25, show_all=False):
                if show_all:
                    return df
                df = df[df['marketCap'] >= market_cap]
                df = df[df['volume'] >= volume]
                df = df[df['shortRatio'] < shortRatio]
                df = df[df['ebitdaMargins'] > ebitdaMargins]
                return df

            df = stock_screen(df, market_cap, volume, shortRatio, ebitdaMargins, show_all)
            df['exchange'] = df['symbol'].apply(lambda x: alpaca_symbols_dict[x]['_raw'].get('exchange'))
            # fitler out exchanges
            df_filter = df[df['exchange']!= 'OTC'].copy()
            if len(df) != len(df_filter):
                st.warning("Check for tickers lost in exchange filter")
            default_name = f'MarketCap{market_cap}__Volume{volume}__ShortRatio{shortRatio}__ebitdaMargins{ebitdaMargins}'
            with st.form("Save Screen"):
                screen_name = st.text_input('Screen Name', value=default_name)
                if st.form_submit_button("Save Screen to Bishop"):
                    BISHOP[screen_name] = df_filter
                    PickleData(BISHOP.get('source'), BISHOP)

            st.header(screen_name)
            standard_AGgrid(df_filter, hide_cols=hide_cols)


    except Exception as e:
        print("playground error: ", e,  print_line_of_error())
if __name__ == '__main__':
    PlayGround()