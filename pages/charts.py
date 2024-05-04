

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import pytz

import hydralit_components as hc

import streamlit as st
from streamlit_extras.switch_page_button import switch_page
import os
import time

from chess_piece.app_hive import create_slope_chart, pollenq_button_source, symbols_unique_color, create_main_macd_chart, create_wave_chart, create_wave_chart_all, create_wave_chart_single
from chess_piece.king import return_QUEENs__symbols_data, print_line_of_error, streamlit_config_colors
from chess_piece.queen_hive import init_queenbee
from custom_graph_candle_stick import st_custom_graph_candle_stick

from custom_button import cust_Button
from custom_grid import st_custom_grid, GridOptionsBuilder
from custom_graph_v1 import st_custom_graph

import ipdb

est = pytz.timezone("US/Eastern")
pq_buttons = pollenq_button_source()

pd.options.mode.chained_assignment = None

prod=st.session_state['prod']
client_user=st.session_state['client_user']
qb = init_queenbee(client_user, prod, queen=True, queen_king=True, api=True)
QUEEN = qb.get('QUEEN')
QUEEN_KING = qb.get('QUEEN_KING')
api = qb.get('api')

call_all_ticker_data = st.sidebar.checkbox("swarmQueen Symbols", False)

ticker_db = return_QUEENs__symbols_data(QUEEN=QUEEN, QUEEN_KING=QUEEN_KING, swarmQueen=call_all_ticker_data)
POLLENSTORY = ticker_db['pollenstory']
STORY_bee = ticker_db['STORY_bee']

tickers_avail = [list(set(i.split("_")[0] for i in STORY_bee.keys()))][0]
k_colors = streamlit_config_colors()
default_text_color = k_colors['default_text_color']
def advanced_charts():
    try:
        st_custom_graph_candle_stick(
                api=f'{st.session_state["ip_address"]}/api/data/candle_stick',
                api_key=os.environ.get("fastAPI_key"),
                symbols=['SPY', 'QQQ'],
                prod=prod,
                key="candle_stick"
            )


        # tickers_avail = [list(set(i.split("_")[0] for i in POLLENSTORY.keys()))][0]
        cols = st.columns((1,5,1,1))
        # fullstory_option = st.selectbox('POLLENSTORY', ['no', 'yes'], index=['yes'].index('yes'))
        stars_radio_dict = {'1Min':"1Minute_1Day", '5Min':"5Minute_5Day", '30m':"30Minute_1Month", '1hr':"1Hour_3Month", 
        '2hr':"2Hour_6Month", '1Yr':"1Day_1Year", 'all':"all",}
        with cols[0]:
            ticker_option = st.selectbox("Tickers", tickers_avail, index=tickers_avail.index(["SPY" if "SPY" in tickers_avail else tickers_avail[0]][0]))
            ticker = ticker_option
        with cols[1]:
            option__ = st.radio(
                label="stars_radio",
                options=list(stars_radio_dict.keys()),
                key="signal_radio",
                label_visibility='visible',
                # disabled=st.session_state.disabled,
                horizontal=True,
            )
            print("OPTION+++++",st.session_state["ip_address"])
            # st_custom_graph(
                # api=f'{st.session_state["ip_address"]}/api/data/ticker_time_frame', 
                # x_axis={
                #     'field': 'timestamp_est'
                # },

                # y_axis=symbols_unique_color(symbols),
                # theme_options={
                #         'backgroundColor': k_colors.get('default_background_color'),
                #         'main_title': '',   # '' for none
                #         'x_axis_title': '',
                #         'grid_color': default_text_color,
                #         "showInLegend": True,
                #         "showInLegendPerLine": True,
                #     },
                # refresh_button=True,
                
                #kwrags
                # username=KING['users_allowed_queen_emailname__db'].get(client_user),
                # prod=prod,
                # symbols=symbols,
                # refresh_sec=refresh_sec,
                # api_key=os.environ.get("fastAPI_key"),
                # return_type=None,
                # graph_height=250,
                # key='graph2',
                # ttf=stars_radio_dict.get(option__),
                # y_max=420
                # )
        
        with cols[2]:
            # day_only_option = st.selectbox('Show Today Only', ['no', 'yes'], index=['no'].index('no'))
            hc.option_bar(option_definition=pq_buttons.get('charts_day_option_data'),title='Show Today Only', key='day_only_option', horizontal_orientation=True) #,override_theme=over_theme,font_styling=font_fmt,horizontal_orientation=True)

        if option__ != 'all':
            ticker_time_frame = f'{ticker}_{stars_radio_dict[option__]}'
        else:
            ticker_time_frame = f'{ticker}_{"1Minute_1Day"}'

        df = POLLENSTORY[ticker_time_frame].copy()

        charts__view, waves__view, slopes__view = st.tabs(['charts', 'waves', 'slopes'])
        
        with charts__view:
            try:

                st.markdown('<div style="text-align: center;">{}</div>'.format(ticker_option), unsafe_allow_html=True)

                if option__.lower() == 'all':
                    min_1 = POLLENSTORY[f'{ticker_option}{"_"}{"1Minute_1Day"}'].copy()
                    min_5 = POLLENSTORY[f'{ticker_option}{"_"}{"5Minute_5Day"}'].copy()
                    min_30m = POLLENSTORY[f'{ticker_option}{"_"}{"30Minute_1Month"}'].copy()
                    _1hr = POLLENSTORY[f'{ticker_option}{"_"}{"1Hour_3Month"}'].copy()
                    _2hr = POLLENSTORY[f'{ticker_option}{"_"}{"2Hour_6Month"}'].copy()
                    _1yr = POLLENSTORY[f'{ticker_option}{"_"}{"1Day_1Year"}'].copy()

                    c1, c2 = st.columns(2)
                    with c1:
                        st.plotly_chart(create_main_macd_chart(min_1))
                    with c2:
                        st.plotly_chart(create_main_macd_chart(min_5))
                    with c1:
                        st.plotly_chart(create_main_macd_chart(min_30m))
                    with c2:
                        st.plotly_chart(create_main_macd_chart(_1hr))
                    with c1:
                        st.plotly_chart(create_main_macd_chart(_2hr))
                    with c2:
                        st.plotly_chart(create_main_macd_chart(_1yr))
                else:
                    # if day_only_option == 'yes':
                    if st.session_state['day_only_option'] == 'charts_dayonly_yes':
                        df_day = df['timestamp_est'].iloc[-1]
                        df['date'] = df['timestamp_est'] # test

                        df_today = df[df['timestamp_est'] > (datetime.now().replace(hour=1, minute=1, second=1)).astimezone(est)].copy()
                        df_prior = df[~(df['timestamp_est'].isin(df_today['timestamp_est'].to_list()))].copy()

                        df = df_today
                    print("+++++DF+++++", df)
                    st.plotly_chart(create_main_macd_chart(df=df, width=1500, height=550))
            
            except Exception as e:
                print(e)
                print_line_of_error()

        # if slope_option == 'yes':
        with slopes__view:
            # df = POLLENSTORY[ticker_time_frame].copy()
            slope_cols = [i for i in df.columns if "slope" in i]
            slope_cols.append("close")
            slope_cols.append("timestamp_est")
            slopes_df = df[['timestamp_est', 'hist_slope-3', 'hist_slope-6', 'macd_slope-3']]
            fig = create_slope_chart(df=df)
            st.plotly_chart(fig)
            st.dataframe(slopes_df)
            
        # if wave_option == "yes":
        with waves__view:
            # df = POLLENSTORY[ticker_time_frame].copy()
            fig = create_wave_chart(df=df)
            st.plotly_chart(fig)
            
            # dft = split_today_vs_prior(df=df)
            # dft = dft['df_today']
            fig=create_wave_chart_all(df=df, wave_col='buy_cross-0__wave')
            st.plotly_chart(fig)

            st.write("current wave")
            current_buy_wave = df['buy_cross-0__wave_number'].tolist()
            current_buy_wave = [int(i) for i in current_buy_wave]
            current_buy_wave = max(current_buy_wave)
            st.write("current wave number")
            st.write(current_buy_wave)
            dft = df[df['buy_cross-0__wave_number'] == str(current_buy_wave)].copy()
            st.write({'current wave': [dft.iloc[0][['timestamp_est', 'close', 'macd']].values]})
            fig=create_wave_chart_single(df=dft, wave_col='buy_cross-0__wave')
            st.plotly_chart(fig)
    
    
        st.session_state['last_page'] = 'queen'
    
    
    except Exception as e:
        print(e)
        print_line_of_error()
    
    return True



if __name__ == '__main__':
    advanced_charts()
