import streamlit as st
from streamlit_extras.stoggle import stoggle
from PIL import Image
import subprocess
from custom_grid import st_custom_grid
from pq_auth import signin_main
from chess_piece.queen_hive import print_line_of_error, return_Ticker_Universe, init_swarm_dbs
from chess_piece.app_hive import set_streamlit_page_config_once, show_waves, create_AppRequest_package, queens_orders__aggrid_v2, click_button_grid, nested_grid, page_line_seperator, standard_AGgrid, queen_orders_view
from chess_piece.king import master_swarm_KING, hive_master_root, local__filepaths_misc, ReadPickleData, PickleData, return_QUEENs__symbols_data
from custom_button import cust_Button
from streamlit_option_menu import option_menu
from datetime import datetime, timedelta
import hydralit_components as hc
from ozz.ozz_bee import send_ozz_call
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


set_streamlit_page_config_once()



def PlayGround():
    with st.spinner("Verifying Your Scent, Hang Tight"):
        authenticator = signin_main(page="playground")
        if st.session_state["authorized_user"] != True:
            switch_page('pollen')
        prod = st.session_state['production']
    db=init_swarm_dbs(prod)
    BISHOP = ReadPickleData(db.get('BISHOP'))
    try:
        # st.write("Me")

        # pickle_file = os.path.join(hive_master_root(), 'delme2.pkl')
        # if st.button("test write new file"):
        #     PickleData(pickle_file, {})
        # if st.button("test set file permissions"):
        #     os.chmod(pickle_file, 0o400)

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
    
        with st.expander("Ozz"):
            cols = st.columns(2)
            with cols[0]:
                query = st.text_input('ozz learning walks call')
                if st.button("ozz"):
                    send_ozz_call(query=query)
            with cols[1]:
                OZZ = ozz_bot(api_key=os.environ.get("ozz_api_key"), username=st.session_state['username'])
                st.write(OZZ)
        
        with st.sidebar:
            option_data = [
            {'icon': "bi bi-hand-thumbs-up", 'label':"Agree"},
            {'icon':"fa fa-question-circle",'label':"Unsure"},
            {'icon': "bi bi-hand-thumbs-down", 'label':"Disagree"},
            ]
            op = hc.option_bar(option_definition=option_data,title='Feedback Response',key='nul') #,override_theme=over_theme,font_styling=font_fmt,horizontal_orientation=True)


        with st.expander('feedback menu options examples'):
            option_data = [
            {'icon': "bi bi-hand-thumbs-up", 'label':"Agree"},
            {'icon':"fa fa-question-circle",'label':"Unsure"},
            {'icon': "bi bi-hand-thumbs-down", 'label':"Disagree"},
            ]

            # override the theme, else it will use the Streamlit applied theme
            over_theme = {'txc_inactive': 'white','menu_background':'purple','txc_active':'yellow','option_active':'blue'}
            font_fmt = {'font-class':'h2','font-size':'150%'}

            # display a horizontal version of the option bar
            op = hc.option_bar(option_definition=option_data,title='Feedback Response',key='PrimaryOption') #,override_theme=over_theme,font_styling=font_fmt,horizontal_orientation=True)
            st.write(op)

            # display a version version of the option bar
            op2 = hc.option_bar(option_definition=option_data,title='Feedback Response',key='PrimaryOption2', horizontal_orientation=False) #,override_theme=over_theme,font_styling=font_fmt,horizontal_orientation=False)
            st.write(op2)


            selected2 = option_menu(None, ["Home", "Upload", "Tasks", 'Settings'], 
                icons=['house', 'cloud-upload', "list-task", 'gear'], 
                menu_icon="cast", default_index=0, orientation="horizontal")
            st.write(selected2)

        view_ss_state = st.sidebar.button("View Session State")
        if view_ss_state:
            st.write(st.session_state)

        
        QUEEN = ReadPickleData(st.session_state['PB_QUEEN_Pickle'])
        
        PB_App_Pickle = st.session_state['PB_App_Pickle']
        QUEEN_KING = ReadPickleData(pickle_file=PB_App_Pickle)
        ticker_db = return_QUEENs__symbols_data(QUEEN=QUEEN, QUEEN_KING=QUEEN_KING)
        POLLENSTORY = ticker_db['pollenstory']
        STORY_bee = ticker_db['STORY_bee']
        tickers_avail = [set(i.split("_")[0] for i in STORY_bee.keys())][0]
        PB_KING_Pickle = master_swarm_KING(prod=st.session_state['production'])
        KING = ReadPickleData(pickle_file=PB_KING_Pickle)

        # st_custom_grid("stefanstapinski", "http://127.0.0.1:8000/api/data/queen", 2, 20, False)
        ticker_universe = return_Ticker_Universe()
        alpaca_symbols_dict = ticker_universe.get('alpaca_symbols_dict')
        alpaca_symbols = {k: i['_raw'] for k,i in alpaca_symbols_dict.items()}
        df = pd.DataFrame(alpaca_symbols).T
        st.write("all symbols")
        with st.expander("all symbols"):
            st.dataframe(df)


        st.markdown("[![Click me](app/static/cat.png)](https://pollenq.com)",unsafe_allow_html=True)
        cols = st.columns(2)
        with cols[0]:
            with st.expander('nested columns'):
                cols_2 = st.columns(2)
                with cols_2[1]:
                    st.markdown("[![Click me](app/static/cat.png)](https://pollenq.com)",unsafe_allow_html=True)
        
        # with st.expander("button on grid"):
        #     click_button_grid()
        if st.toggle("nested grid"):
            with st.expander("nested grid"):
                nested_grid()

        if st.toggle("pollenstory"):
            with st.expander("pollenstory"):
                ttf = st.selectbox('ttf', list(STORY_bee.keys())) # index=['no'].index('no'))
                data=POLLENSTORY[ttf]
                default_cols = ['timestamp_est', 'open', 'close', 'high', 'low', 'buy_cross-0', 'buy_cross-0__wave_number']
                cols = st.multiselect('qcp', options=data.columns.tolist(), default=default_cols)
                data=data[cols].copy()
                data = data.reset_index()
                grid = standard_AGgrid(data=data, configure_side_bar=True)


        if st.toggle("wave stories"):
            with st.expander("wave stories"):
                ticker_option = st.selectbox("ticker", options=tickers_avail)
                frame_option = st.selectbox("frame", options=KING['star_times'])
                show_waves(STORY_bee=STORY_bee, ticker_option=ticker_option, frame_option=frame_option)


        def get_screen_processes():
            # Run the "screen -ls" command to get a list of screen processes
            output = subprocess.run(["screen", "-ls"], stdout=subprocess.PIPE).stdout.decode(
                "utf-8"
            )

            # Split the output into lines
            lines = output.strip().split("\n")

            # The first line is a header, so skip it
            lines = lines[1:]

            # Initialize an empty dictionary
            screen_processes = {}

            # Iterate over the lines and extract the process name and PID
            for line in lines:
                parts = line.split()
                name = parts[0]
                pid = parts[1]
                screen_processes[name] = pid

            return screen_processes
    
        if st.toggle("yahoo", True):
            db_qb_root = os.path.join(hive_master_root(), "db")
            yahoo_stats_bee = os.path.join(db_qb_root, "yahoo_stats_bee.pkl")
            db = ReadPickleData(yahoo_stats_bee)
            # st.write(db['AAPL'])
            
            def refresh_yfinance_ticker_info(KING):
                all_info = {}
                sectors = {}
                ticker_universe = KING['ticker_universe']
                main_symbols_full_list = ticker_universe['main_symbols_full_list']
                progress_text = "Operation in progress. Please wait."
                my_bar = st.progress(0, text=progress_text)
                max = len(main_symbols_full_list)
                for idx, tic in enumerate(main_symbols_full_list):
                    num = round(idx/max)
                    try:
                        ticker = yf.Ticker(tic)
                        all_info[tic] = ticker.info
                        sectors[tic] = ticker.info.get('sector')
                        my_bar.progress(num, text=progress_text)
                    except Exception as e:
                        print_line_of_error(tic)

                my_bar.empty()
                # df = pd.DataFrame(sectors.items())
                # st.write(df)

                # if all_info:
                df = pd.DataFrame()
                # Initialize progress bar
                progress_text = "Processing tickers..."
                my_bar = st.progress(0, text=progress_text)

                # Calculate total number of tickers
                total_tickers = len(all_info)

                # Iterate through ticker information
                for idx, (tic, data) in enumerate(all_info.items(), start=1):
                    # Calculate progress percentage
                    progress_percent = round(idx / total_tickers * 100)
                    
                    # Update progress bar
                    my_bar.progress(progress_percent, text=progress_text)
                    
                    # Process ticker data
                    token = pd.DataFrame(data.items()).T
                    headers=token.iloc[0]
                    token.columns=headers
                    token = token.drop(0)
                    token['ticker'] = tic
                    df = pd.concat([df, token], ignore_index=True)
                    my_bar = st.empty()

                    return df
            
            if st.button("Refresh ALL yahoo ticker info into BISHOP"):
                df_info = refresh_yfinance_ticker_info(KING)
                if type(df_info) == pd.core.frame.DataFrame:
                    BISHOP['ticker_info'] = df_info
                    PickleData(BISHOP.get('source'), BISHOP, console=True)
        

        if 'ticker_info' in BISHOP.keys():
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
            
            
            # screener
            def stock_screen(df):
                df = df[df['marketCap'] > 50000000]
                df = df[df['volume'] > 1000000]
                df = df[df['shortRatio'] < 2]
                df = df[df['ebitdaMargins'] > .25]
                return df

            df = stock_screen(df)
            screen_name = st.text_input('Screen Name')
            if st.button("Save Screen to Bishop"):
                BISHOP[screen_name] = df
                PickleData(BISHOP.get('source'), BISHOP)

            standard_AGgrid(df, hide_cols=hide_cols)


    except Exception as e:
        print("playground error: ", e,  print_line_of_error())
if __name__ == '__main__':
    PlayGround()