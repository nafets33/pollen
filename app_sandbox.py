
import pandas as pd
import streamlit as st
import logging
import os
import pandas as pd
import numpy as np
import datetime
import pytz
from typing import Callable
import random
from tqdm import tqdm
from collections import defaultdict
import ipdb
import matplotlib.pyplot as plt
from plotly.subplots import make_subplots
from PIL import Image
from dotenv import load_dotenv
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode, JsCode
import _locale
import os
from random import randint
import sqlite3
import streamlit as st
# from appHIVE import signin_main
from app_auth import signin_main
import base64

_locale._getdefaultlocale = (lambda *args: ['en_US', 'UTF-8'])
est = pytz.timezone("US/Eastern")

# import streamlit_authenticator as stauth
# import smtplib
# import ssl
# from email.message import EmailMessage
# from streamlit.web.server.websocket_headers import _get_websocket_headers

# headers = _get_websocket_headers()


# https://discuss.streamlit.io/t/how-to-animate-a-line-chart/164/6 ## animiate the Bees Images : )
# https://blog.streamlit.io/introducing-theming/  # change theme colors
pd.options.mode.chained_assignment = None

scriptname = os.path.basename(__file__)
queens_chess_piece = os.path.basename(__file__)

main_root = os.getcwd()

# images
jpg_root = os.path.join(main_root, 'misc')
bee_image = os.path.join(jpg_root, 'bee.jpg')
bee_power_image = os.path.join(jpg_root, 'power.jpg')
hex_image = os.path.join(jpg_root, 'hex_design.jpg')
hive_image = os.path.join(jpg_root, 'bee_hive.jpg')
queen_image = os.path.join(jpg_root, 'queen.jpg')
queen_angel_image = os.path.join(jpg_root, 'queen_angel.jpg')
page_icon = Image.open(bee_image)
flyingbee_gif_path = os.path.join(jpg_root, 'flyingbee_gif_clean.gif')
flyingbee_grey_gif_path = os.path.join(jpg_root, 'flying_bee_clean_grey.gif')
bitcoin_gif = os.path.join(jpg_root, 'bitcoin_spinning.gif')
power_gif = os.path.join(jpg_root, 'power_gif.gif')


##### STREAMLIT ###
default_text_color = '#59490A'
default_font = "sans serif"
default_yellow_color = '#C5B743'
st.set_page_config(
     page_title="pollenq",
     page_icon=page_icon,
     layout="wide",
     initial_sidebar_state="expanded",
    #  Theme='Light'
    #  menu_items={
    #      'Get Help': 'https://www.extremelycoolapp.com/help',
    #      'Report a bug': "https://www.extremelycoolapp.com/bug",
    #      'About': "# This is a header. This is an *extremely* cool app!"
    #  }
 )
with st.spinner("Buzz Buzz Where is my Honey"):
    signin_auth = signin_main()
    # st.write(st.session_state)
    if signin_auth:
        client_user = st.session_state['username']
        gatekeeper = True
        prod = False if 'sandbox' in scriptname else True
    else:
        st.write("Sign in to get your Queen")
        # st.stop()
        client_user = st.session_state['username']
        gatekeeper = True
        prod = False

    if prod:
        from QueenHive import return_STORYbee_trigbees, return_alpaca_api_keys, add_key_to_app, read_pollenstory, init_clientUser_dbroot, init_pollen_dbs, createParser_App, refresh_account_info, generate_TradingModel, stars, analyze_waves, KINGME, queen_orders_view, story_view, return_alpc_portolio, return_dfshaped_orders, ReadPickleData, pollen_themes, PickleData, return_timestamp_string, return_api_keys, read_queensmind, split_today_vs_prior, init_logging
        load_dotenv(os.path.join(os.getcwd(), '.env_jq'))
    else:
        from QueenHive_sandbox import return_STORYbee_trigbees, return_alpaca_api_keys, add_key_to_app, read_pollenstory, init_clientUser_dbroot, init_pollen_dbs, createParser_App, refresh_account_info, generate_TradingModel, stars, analyze_waves, KINGME, queen_orders_view, story_view, return_alpc_portolio, return_dfshaped_orders, ReadPickleData, pollen_themes, PickleData, return_timestamp_string, return_api_keys, read_queensmind, split_today_vs_prior, init_logging
        load_dotenv(os.path.join(os.getcwd(), '.env'))


    # ###### GLOBAL # ######
    ARCHIVE_queenorder = 'archived'
    active_order_state_list = ['running', 'running_close', 'submitted', 'error', 'pending', 'completed', 'completed_alpaca', 'running_open', 'archived_bee']
    active_queen_order_states = ['submitted', 'accetped', 'pending', 'running', 'running_close', 'running_open']
    CLOSED_queenorders = ['running_close', 'completed', 'completed_alpaca']
    RUNNING_Orders = ['running', 'running_open']
    RUNNING_CLOSE_Orders = ['running_close']

    # crypto
    crypto_currency_symbols = ['BTCUSD', 'ETHUSD', 'BTC/USD', 'ETH/USD']
    crypto_symbols__tickers_avail = ['BTCUSD', 'ETHUSD']


    parser = createParser_App()
    namespace = parser.parse_args()
    admin = True if namespace.admin == 'true' or client_user == 'stefanstapinski@gmail.com' else False
    authorized_user = True if namespace.admin == 'true' or client_user == 'stefanstapinski@gmail.com' else False

    if admin:
        st.session_state['admin'] = True
    else:
        st.session_state['admin'] = False



    def queen_triggerbees():
        cq1, cq2, cq3, cq4 = st.columns((4,1,1,4))
        
        now_time = datetime.datetime.now(est)
        req = return_STORYbee_trigbees(QUEEN=QUEEN, STORY_bee=STORY_bee, tickers_filter=False)
        active_trigs = req['active_trigs']
        all_current_trigs = req['all_current_trigs']
        
        with cq1:
            if len(active_trigs) > 0:
                mark_down_text(align='left', fontsize=15, color=default_text_color, text="Active TriggerBees")
                # write_flying_bee()
                df = pd.DataFrame(active_trigs.items())
                df = df.rename(columns={0: 'ttf', 1: 'trig'})
                df = df.sort_values('ttf')
                st.write(df)
                # g = {write_flying_bee() for i in range(len(df))}
            else:
                mark_down_text(fontsize=12, color=default_text_color, text="No Active TriggerBees")     
        with cq2:
            flying_bee_gif()
        with cq3:
            flying_bee_gif()

        with cq4:
            if len(all_current_trigs) > 0:
                with st.expander('All Available TriggerBees'):
                    mark_down_text(fontsize=15, color=default_text_color, text="All Available TriggerBees")
                    df = pd.DataFrame(all_current_trigs.items())
                    df = df.rename(columns={0: 'ttf', 1: 'trig'})
                    df = df.sort_values('ttf')
                    st.write(df)
            else:
                mark_down_text(fontsize=12, color=default_text_color, text="No Available TriggerBees")


    def queen_order_flow():
        # if st.session_state['admin'] == False:
        #     return False
        page_line_seperator()

        orders_table = st.checkbox("show completed orders")

        if orders_table:
            refresh_b = st.button("Refresh Orders", key='r1')
            with st.expander('Completed/ALL Orders', expanded=True):
                now_time = datetime.datetime.now(est)
                cols = st.columns((1,1,5))
                with cols[0]:
                    all_orders = st.checkbox("Show All Orders", False)
                with cols[1]:
                    today_orders = st.checkbox("Today Orders", True)
                
                order_states = set(QUEEN['queen_orders']['queen_order_state'].tolist())
                
                if all_orders:
                    order_states = all_orders
                else:
                    order_states = ['completed', 'completed_alpaca']
                
                queen_order_states = st.multiselect('queen order states', options=list(active_order_state_list), default=order_states)

                df = queen_orders_view(QUEEN=QUEEN, queen_order_state=queen_order_states, return_str=False)['df']
                if len(df) == 0:
                    st.info("No Orders to View")
                else:
                    if today_orders:
                        df = df[df['datetime'] > now_time.replace(hour=1, minute=1, second=1)].copy()
                    
                    if len(df) > 0:
                        ordertables__agrid = build_AGgrid_df__queenorders(data=df.astype(str), reload_data=False, height=200)
                    else:
                        st.info("No Orders To View")
        
        with st.expander('Flying Orders', expanded=True):
            refresh_b = st.button("Refresh Orders", key='r2')
            error_orders = queen_orders_view(QUEEN=QUEEN, queen_order_state=['error'], return_all_cols=True)['df']
            error_orders = error_orders.astype(str)
            if len(error_orders)> 0:
                new_title = '<p style="font-family:sans-serif; color:Black; font-size: 25px;">ERRORS</p>'
                st.markdown(new_title, unsafe_allow_html=True)
                st.dataframe(error_orders)

            for order_state in active_queen_order_states:
                df = queen_orders_view(QUEEN=QUEEN, queen_order_state=[order_state])['df']
                if len(df) > 89:
                    grid_height = 654
                elif len(df) < 10:
                    grid_height = 200
                else:
                    grid_height = 333
                
                if len(df) > 0:
                    if order_state == 'error':
                        continue
                    elif order_state == 'submitted':
                        mark_down_text(align='center', color=default_text_color, fontsize='23', text=order_state)
                        run_orders__agrid_submit = build_AGgrid_df__queenorders(data=df, reload_data=False, height=grid_height)
                    elif order_state == 'running_open':
                        mark_down_text(align='center', color=default_text_color, fontsize='23', text=order_state)
                        run_orders__agrid_open = build_AGgrid_df__queenorders(data=df, reload_data=False, height=grid_height)
                    elif order_state == 'running':
                        mark_down_text(align='center', color=default_text_color, fontsize='23', text=order_state)
                        run_orders__agrid = build_AGgrid_df__queenorders(data=df, reload_data=False, height=grid_height, paginationOn=False)
                    elif order_state == 'running_close':
                        mark_down_text(align='center', color=default_text_color, fontsize='23', text=order_state)
                        run_orders__agrid_open = build_AGgrid_df__queenorders(data=df, reload_data=False, height=grid_height)


                
        return True


    def queen_QueenOrders():
        if admin == False:
            st.write("You Do Not Have Access")
            return False
        # Update run order
        all_orders = QUEEN['queen_orders']
        active_orders = all_orders[all_orders['queen_order_state'].isin(active_order_state_list)].copy()
        show_errors_option = st.selectbox('show last error', ['no', 'yes'], index=['no'].index('no'))
        c_order_input_list = st.multiselect("active client_order_id", active_orders['client_order_id'].to_list(), default=active_orders.iloc[-1]['client_order_id'])
        
        c_order_input = [c_order_input_list[0] if len(c_order_input_list) > 0 else all_orders.iloc[-1]['client_order_id'] ][0]

        # if show_errors_option == 'yes':
        if show_errors_option == 'yes':
            latest_queen_order = all_orders[all_orders['queen_order_state'] == 'error'].copy()
        else:                
            latest_queen_order = all_orders[all_orders['client_order_id'] == c_order_input].copy()

        
        df = latest_queen_order
        df = df.T.reset_index()
        df = df.astype(str)
        df = df.rename(columns={df.columns[1]: 'main'})
        
        grid_response = build_AGgrid_df(data=df, reload_data=False, update_cols=['update_column'], height=933)
        data = grid_response['data']
        # st.write(data)
        ttframe = data[data['index'] == 'ticker_time_frame'].copy()
        ttframe = ttframe.iloc[0]['main']
        # st.write(ttframe.iloc[0]['main'])
        selected = grid_response['selected_rows'] 
        df_sel = pd.DataFrame(selected)

        if len(df_sel) > 0:
            df_sel = df_sel.astype(str)
            st.write(df_sel)
            up_values = dict(zip(df_sel['index'], df_sel['update_column_update']))
            up_values = {k: v for (k,v) in up_values.items() if len(v) > 0}
            update_dict = {latest_queen_order.iloc[0]["client_order_id"]: up_values}
            st.session_state['update'] = update_dict
            st.session_state['ttframe_update'] = ttframe

        save_button_runorder = st.button("Save RunOrderUpdate")
        if save_button_runorder:
            # st.write(st.session_state['update'])
            update_sstate = st.session_state['update']
            update_ttframe = st.session_state['ttframe_update']
            order_dict = {'system': 'app',
            'queen_order_update_package': update_sstate,
            'app_requests_id' : f'{save_signals}{"_app-request_id_"}{return_timestamp_string()}{datetime.datetime.now().microsecond}',
            'ticker_time_frame': update_ttframe,
            }
            # st.write(order_dict)
            data = ReadPickleData(pickle_file=PB_App_Pickle)
            data['update_queen_order'].append(order_dict)
            PickleData(pickle_file=PB_App_Pickle, data_to_store=data)
            data = ReadPickleData(pickle_file=PB_App_Pickle)
            st.write(data['update_queen_order'])
            

    def queen_beeAction():
        if st.session_state['admin'] == False:
            st.write('admin', admin)
            st.write("Permission Denied")
            return False
        
        wave_button_sel = st.selectbox("Waves", ["buy_cross-0", "sell_cross-0"])
        initiate_waveup = st.button("Send Wave")
        # pollen = return_pollen()
        # ticker_time_frame = [set(i for i in STORY_bee.keys())][0]
        ticker_time_frame = QUEEN['heartbeat']['available_tickers']

        if len(ticker_time_frame) == 0:
            ticker_time_frame = list(set(i for i in STORY_bee.keys()))

        # ticker_time_frame = [i for i in ticker_time_frame]
        # ticker_time_frame.sort()
        ticker_wave_option = st.sidebar.selectbox("Tickers", ticker_time_frame, index=ticker_time_frame.index(["SPY_1Minute_1Day" if "SPY_1Minute_1Day" in ticker_time_frame else ticker_time_frame[0]][0]))

        wave_trigger = {ticker_wave_option: [wave_button_sel]}

        if initiate_waveup:
            order_dict = {'ticker': ticker_wave_option.split("_")[0],
            'ticker_time_frame': ticker_wave_option,
            'system': 'app',
            'wave_trigger': wave_trigger,
            'request_time': datetime.datetime.now(),
            'app_requests_id' : f'{save_signals}{"_"}{"waveup"}{"_app-request_id_"}{return_timestamp_string()}{datetime.datetime.now().microsecond}'
            }

            # data = ReadPickleData(pickle_file=PB_App_Pickle)
            # st.write(data.keys())
            APP_requests['wave_triggers'].append(order_dict)
            PickleData(pickle_file=PB_App_Pickle, data_to_store=APP_requests)
            return_image_upon_save(bee_power_image=bee_power_image)          


        new_title = '<p style="font-family:sans-serif; color:Black; font-size: 33px;">Flash Buttons</p>'
        st.markdown(new_title, unsafe_allow_html=True)
        
        c1, c2, = st.columns(2)
        with c1:
            quick_buy_short = st.button("FLASH BUY SQQQ")
        with c2:
            quick_buy_long = st.button("FLASH BUY TQQQ")
        
        quick_buy_BTC = st.button("FLASH BUY BTC")
        
        quick_buy_amt = st.selectbox("FLASH BUY $", [5000, 10000, 20000, 30000], index=[10000].index(10000))
        
        type_option = st.selectbox('type', ['market'], index=['market'].index('market'))                

        if quick_buy_short or quick_buy_long or quick_buy_BTC:
            
            if quick_buy_short:
                ticker = "SQQQ"
            elif quick_buy_long:
                ticker = "TQQQ"
            elif quick_buy_BTC:
                ticker = "BTCUSD"
            
            print("buy buy meee, sending app request")
            # get price convert to amount
            if ticker in crypto_currency_symbols:
                crypto = True
                snap = api.get_crypto_snapshot(ticker, exchange=coin_exchange)
                current_price = snap.latest_trade.price
            else:
                crypto = False
                snap = api.get_snapshot(ticker)
                current_price = snap.latest_trade.price
            
            info = api.get_account()
            total_buying_power = info.buying_power # what is the % amount you want to buy?


            validation = True # not > 50% of buying power COIN later
            
            if validation:
                print("qty validated")
                # process order signal                
                order_dict = {'ticker': ticker,
                'system': 'app',
                'trig': 'app',
                'request_time': datetime.datetime.now(est),
                'wave_amo': quick_buy_amt,
                'app_seen_price': current_price,
                'side': 'buy',
                'type': type_option,
                'app_requests_id' : f'{save_signals}{"_app-request_id_"}{return_timestamp_string()}{datetime.datetime.now().microsecond}'
                }

                data = ReadPickleData(pickle_file=PB_App_Pickle)
                data['buy_orders'].append(order_dict)
                PickleData(pickle_file=PB_App_Pickle, data_to_store=data)
                data = ReadPickleData(pickle_file=PB_App_Pickle)
                st.write(data['buy_orders'])


    def create_main_macd_chart(df):
        title = df.iloc[-1]['name']
        # st.markdown('<div style="text-align: center;">{}</div>'.format(title), unsafe_allow_html=True)
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.1999, row_heights=[0.7, 0.3])
        # df.set_index('timestamp_est')
        # df['chartdate'] = f'{df["chartdate"].day}{df["chartdate"].hour}{df["chartdate"].minute}'
        df=df.copy()
        df['chartdate'] = df['chartdate'].apply(lambda x: f'{x.month}{"-"}{x.day}{"_"}{x.hour}{":"}{x.minute}')
        fig.add_ohlc(x=df['chartdate'], close=df['close'], open=df['open'], low=df['low'], high=df['high'], name='price')
        # fig.add_scatter(x=df['chartdate'], y=df['close'], mode="lines", row=1, col=1)
        # if '1Minute_1Day' in df.iloc[0]['name']:
        fig.add_scatter(x=df['chartdate'], y=df['vwap'], mode="lines", row=1, col=1, name='vwap')

        fig.add_scatter(x=df['chartdate'], y=df['macd'], mode="lines", row=2, col=1, name='mac')
        fig.add_scatter(x=df['chartdate'], y=df['signal'], mode="lines", row=2, col=1, name='signal')
        fig.add_bar(x=df['chartdate'], y=df['hist'], row=2, col=1, name='hist')
        fig.update_layout(title_text=title)
        df['cross'] = np.where(df['macd_cross'].str.contains('cross'), df['macd'], 0)
        fig.add_scatter(x=df['chartdate'], y=df['cross'], mode='lines', row=2, col=1, name='cross',) # line_color='#00CC96')
        # fig.add_scatter(x=df['chartdate'], y=df['cross'], mode='markers', row=1, col=1, name='cross',) # line_color='#00CC96')
        fig.update_xaxes(showgrid=False)
        fig.update_yaxes(showgrid=False)
        return fig


    def create_slope_chart(df):
        title = df.iloc[-1]['name']
        # st.markdown('<div style="text-align: center;">{}</div>'.format(title), unsafe_allow_html=True)
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.01)
        # df.set_index('timestamp_est')
        # df['chartdate'] = f'{df["chartdate"].day}{df["chartdate"].hour}{df["chartdate"].minute}'
        df = df.copy()
        df['chartdate'] = df['chartdate'].apply(lambda x: f'{x.month}{"-"}{x.day}{"_"}{x.hour}{":"}{x.minute}')
        slope_cols = [i for i in df.columns if 'slope' in i]
        for col in slope_cols:
            df[col] = pd.to_numeric(df[col])
            df[col] = np.where(abs(df[col])>5, 0, df[col])
        fig.add_scatter(x=df['chartdate'], y=df['hist_slope-3'], mode="lines", row=1, col=1, name='hist_slope-3')
        fig.add_scatter(x=df['chartdate'], y=df['hist_slope-6'], mode="lines", row=1, col=1, name='hist_slope-6')
        # fig.add_scatter(x=df['chartdate'], y=df['hist_slope-23'], mode="lines", row=1, col=1, name='hist_slope-23')
        fig.add_scatter(x=df['chartdate'], y=df['macd_slope-3'], mode="lines", row=2, col=1, name='macd_slope-3')
        fig.add_scatter(x=df['chartdate'], y=df['macd_slope-6'], mode="lines", row=2, col=1, name='macd_slope-6')
        # fig.add_scatter(x=df['chartdate'], y=df['macd_slope-23'], mode="lines", row=2, col=1, name='macd_slope-23')
        fig.update_layout(height=600, width=900, title_text=title)
        return fig


    def create_wave_chart(df):
        title = f'buy+sell cross __waves {df.iloc[-1]["name"]}'
        # st.markdown('<div style="text-align: center;">{}</div>'.format(title), unsafe_allow_html=True)
        fig = make_subplots(rows=1, cols=1, shared_xaxes=True, vertical_spacing=0.01)
        # df.set_index('timestamp_est')
        # df['chartdate'] = f'{df["chartdate"].day}{df["chartdate"].hour}{df["chartdate"].minute}'
        df = df.copy()
        df['chartdate'] = df['chartdate'].apply(lambda x: f'{x.month}{"-"}{x.day}{"_"}{x.hour}{":"}{x.minute}')

        fig.add_bar(x=df['chartdate'], y=df['buy_cross-0__wave'],  row=1, col=1, name='buycross wave')
        fig.add_bar(x=df['chartdate'], y=df['sell_cross-0__wave'],  row=1, col=1, name='sellcross wave')
        fig.update_layout(height=600, width=900, title_text=title)
        return fig


    def create_wave_chart_single(df, wave_col):
        title = df.iloc[-1]['name']
        # st.markdown('<div style="text-align: center;">{}</div>'.format(title), unsafe_allow_html=True)
        fig = make_subplots(rows=1, cols=1, shared_xaxes=True, vertical_spacing=0.01)
        # df.set_index('timestamp_est')
        # df['chartdate'] = f'{df["chartdate"].day}{df["chartdate"].hour}{df["chartdate"].minute}'
        df = df.copy()
        df['chartdate'] = df['chartdate'].apply(lambda x: f'{x.month}{"-"}{x.day}{"_"}{x.hour}{":"}{x.minute}')

        fig.add_bar(x=df['chartdate'], y=df[wave_col],  row=1, col=1, name=wave_col)
        fig.update_layout(height=600, width=900, title_text=title)
        return fig


    def create_wave_chart_all(df, wave_col):
        title = df.iloc[-1]['name']
        # st.markdown('<div style="text-align: center;">{}</div>'.format(title), unsafe_allow_html=True)
        fig = make_subplots(rows=1, cols=1, shared_xaxes=True, vertical_spacing=0.01)
        # df.set_index('timestamp_est')
        # df['chartdate'] = f'{df["chartdate"].day}{df["chartdate"].hour}{df["chartdate"].minute}'
        df = df.copy()
        # df['chartdate'] = df['chartdate'].apply(lambda x: f'{x.month}{"-"}{x.day}{"_"}{x.hour}{":"}{x.minute}')
        # df[f'{wave_col}{"_number"}'] = df[f'{wave_col}{"_number"}'].astype(str)
        # dft = df[df[f'{wave_col}{"_number"}'] == '1'].copy()
        fig.add_bar(x=df[f'{wave_col}{"_number"}'], y=df[wave_col].values,  row=1, col=1, name=wave_col)
        fig.update_layout(height=600, width=900, title_text=title)
        return fig


    def return_total_profits(QUEEN):
        
        df = QUEEN['queen_orders']
        ORDERS = df[(df['queen_order_state']== 'completed') & (df['side'] == 'sell')].copy()
        return_dict = {}
        if len(ORDERS) > 0:
            with st.expander("P/L Summary"):
                by_ticker = st.checkbox('Group by Ticker')
                group_by_value = ['symbol'] if by_ticker == True else ['symbol', 'ticker_time_frame']

                tic_group_df = df.groupby(group_by_value)[['profit_loss']].sum().reset_index()
                return_dict['TotalProfitLoss'] = tic_group_df

                now_ = datetime.datetime.now(est)
                orders_today = df[df['datetime'] > now_.replace(hour=1, minute=1, second=1)].copy()
                
                if len(orders_today) > 0:
                    df = orders_today
                    today_pl_df = df.groupby(group_by_value)[['profit_loss']].sum().reset_index()
                    mark_down_text(fontsize='25', text="Today Profit Loss")
                    st.write(today_pl_df)
                    mark_down_text(fontsize='25', text="Total Profit Loss")
                    st.write(tic_group_df)
                else:
                    mark_down_text(fontsize='25', text="Total Profit Loss")

                    st.write(tic_group_df)
                # submitted = st.form_submit_button("Save")
        
        return return_dict


    def return_buying_power(api):
        with st.expander("Portfolio"):
            ac_info = refresh_account_info(api=api)['info_converted']
            num_text = "Total Buying Power: " + '${:,.2f}'.format(ac_info['buying_power'])
            mark_down_text(fontsize='18', text=num_text)
            # st.write(":heavy_minus_sign:" * 34)

            num_text = "last_equity: " + '${:,.2f}'.format(ac_info['last_equity'])
            mark_down_text(fontsize='15', text=num_text)

            num_text = "portfolio_value: " + '${:,.2f}'.format(ac_info['portfolio_value'])
            mark_down_text(fontsize='15', text=num_text)

            num_text = "Cash: " + '${:,.2f}'.format(ac_info['cash'])
            mark_down_text(fontsize='15', text=num_text)
            
            num_text = "Total Fees: " + '${:,.2f}'.format(ac_info['accrued_fees'])
            mark_down_text(fontsize='12', text=num_text)


    def stop_queenbee(APP_requests):
        with st.form("stop_queen"):
            checkbox_val = st.checkbox("Stop Queen")

            # Every form must have a submit button.
            submitted = st.form_submit_button("Submit")
            if submitted:
                APP_requests['stop_queen'] = str(checkbox_val).lower()
                PickleData(pickle_file=PB_App_Pickle, data_to_store=APP_requests)
                st.success("Queen Sleeps")
        return True


    def refresh_queenbee_controls(APP_requests):
        with st.form("refresh QUEEN controls"):
            checkbox_val = st.checkbox("refresh QUEEN controls")

            # Every form must have a submit button.
            submitted = st.form_submit_button("Submit")
            if submitted:
                ("checkbox", checkbox_val)
                
                APP_requests['queen_controls_reset'] = str(checkbox_val).lower()
                
                # app_request_package = create_AppRequest_package(request_name='queen_controls_reset', archive_bucket='misc_bucket')
                # app_request_package['control_name'] = control_option
                # control_upate = {'control_update' : dict(zip(df_sel['star'], df_sel['Update_Value_update']))}
                # app_request_package.update(control_upate)
                # Save
                # st.write(app_request_package)
                # APP_requests['queen_controls_reset'].append(app_request_package)
                # APP_requests['queen_controls_lastupdate'] = datetime.datetime.now().astimezone(est)
                # PickleData(pickle_file=PB_App_Pickle, data_to_store=APP_requests)
                
                PickleData(pickle_file=PB_App_Pickle, data_to_store=APP_requests)
                
        return True


    def return_image_upon_save(bee_power_image, width=33):
        # st.write("Controls Saved", return_timestamp_string())
        # st.image(Image.open(bee_power_image), width=width)
        local_gif(gif_path=power_gif)
        st.success("Saved")


    def update_Workerbees(APP_requests):
        #### SPEED THIS UP AND CHANGE TO DB CALL FOR ALLOWED ACTIVE TICKERS ###
        all_alpaca_tickers = api.list_assets()
        alpaca_symbols_dict = {}
        for n, v in enumerate(all_alpaca_tickers):
            if all_alpaca_tickers[n].status == 'active':
                alpaca_symbols_dict[all_alpaca_tickers[n].symbol] = vars(all_alpaca_tickers[n])
        
        # st.subheader("Current Chess Board")
        all_workers = list(QUEEN['workerbees'].keys())
        view = []
        for qcp in all_workers:
            if qcp in ['castle', 'bishop', 'knight', 'castle_coin']:
                view.append(f'{qcp} ({QUEEN["workerbees"][qcp]["tickers"]} )')
        name = str(view).replace("[", "").replace("]", "").replace('"', "")
        with st.expander(f'WorkingBees Sybmols Chess Board: {name}'):
            st.subheader("Current Chess Board")
            cols = st.columns((1,1,1,1))
            # all_workers = list(QUEEN['workerbees'].keys())
            for qcp in all_workers:
                if qcp == 'castle_coin':
                    # with cols[0]:
                    #     local_gif(gif_path=bitcoin_gif)
                    with cols[0]:
                        st.write(f'{qcp} {QUEEN["workerbees"][qcp]["tickers"]}')
                if qcp == 'castle':
                    with cols[1]:
                        st.write(f'{qcp} {QUEEN["workerbees"][qcp]["tickers"]}')
                elif qcp == 'knight':
                    with cols[2]:
                        st.write(f'{qcp} {QUEEN["workerbees"][qcp]["tickers"]}')
                elif qcp == 'bishop':
                    with cols[3]:
                        st.write(f'{qcp} {QUEEN["workerbees"][qcp]["tickers"]}')
                elif qcp == 'pawns':
                    if len(QUEEN["workerbees"][qcp]["tickers"]) > 20:
                        show = QUEEN["workerbees"][qcp]["tickers"][:20]
                        show = f'{show} ....'
                    else:
                        show = QUEEN["workerbees"][qcp]["tickers"]
                    st.write(f'{qcp} {show}')

            wrkerbees_list = list(QUEEN['workerbees'].keys())
            c1, c2, c3 = st.columns((1,5,1))
            with c1:
                workerbee = st.selectbox('select worker', wrkerbees_list, index=wrkerbees_list.index('castle'))
            with c2:
                worker_tickers = st.multiselect(label='workers', options=list(alpaca_symbols_dict.keys()) + crypto_symbols__tickers_avail, default=QUEEN['workerbees'][workerbee]['tickers'])
            with c3:
                flying_bee_gif()

            with st.form("Update WorkerBees"):
                st.write("MACD Model Settings")
                c1, c2, c3 = st.columns(3)
                with c1:
                    fast = st.slider("fast", min_value=1, max_value=33, value=int(QUEEN['workerbees'][workerbee]['MACD_fast_slow_smooth']['fast']))
                with c2:
                    slow = st.slider("slow", min_value=1, max_value=33, value=int(QUEEN['workerbees'][workerbee]['MACD_fast_slow_smooth']['slow']))
                with c3:
                    smooth = st.slider("smooth", min_value=1, max_value=33, value=int(QUEEN['workerbees'][workerbee]['MACD_fast_slow_smooth']['smooth']))



                if st.form_submit_button('Save Workers'):
                    app_req = create_AppRequest_package(request_name='workerbees')
                    app_req['queens_chess_piece'] = workerbee
                    app_req['tickers'] = worker_tickers
                    app_req['MACD_fast_slow_smooth'] = {'fast': fast, 'slow': slow, 'smooth': smooth}
                    APP_requests['workerbees'].append(app_req)
                    PickleData(pickle_file=PB_App_Pickle, data_to_store=APP_requests)
                    return_image_upon_save(bee_power_image=bee_power_image)
        return True
        

    def update_QueenControls(APP_requests, control_option, theme_list):
        if control_option.lower() == 'theme':
            with st.form("Update Control"):

                if control_option.lower() == 'theme':
                    theme_option = st.selectbox('Select theme', theme_list, index=theme_list.index('nuetral'))
                
                save_button = st.form_submit_button("Submit")
                if save_button:
                    APP_requests['theme'] = theme_option
                    APP_requests['last_app_update'] = datetime.datetime.now()
                    PickleData(pickle_file=PB_App_Pickle, data_to_store=APP_requests)
                    return_image_upon_save(bee_power_image=bee_power_image)
            return True

        elif control_option.lower() == 'max_profit_wavedeviation':
            st.write("active")
            df = pd.DataFrame(QUEEN['queen_controls']['max_profit_waveDeviation'].items()).astype(str)
            df = df.rename(columns={0: 'star', 1: 'Sell At Devation'})
            grid_response = build_AGgrid_df(data=df, reload_data=False, height=250, update_cols=['Update_Value'], paginationOn=False)
            data = grid_response['data']
            selected = grid_response['selected_rows'] 
            df_sel = pd.DataFrame(selected)
            st.write(df_sel)
            save_waveD = st.button('Save')
            if save_waveD:
                # Create
                app_request_package = create_AppRequest_package(request_name=control_option, archive_bucket='queen_contorls_requests')
                app_request_package['control_name'] = control_option
                control_upate = {'control_update' : dict(zip(df_sel['star'], df_sel['Update_Value_update']))}
                app_request_package.update(control_upate)
                # Save
                st.write(app_request_package)
                APP_requests['queen_controls'].append(app_request_package)
                APP_requests['queen_controls_lastupdate'] = datetime.datetime.now().astimezone(est)
                PickleData(pickle_file=PB_App_Pickle, data_to_store=APP_requests)
                return_image_upon_save(bee_power_image=bee_power_image)

        elif control_option.lower() == 'power_rangers':
            st.write("active")
            # power rangers
            theme_token = st.selectbox('Power Rangers Theme', theme_list, index=theme_list.index('nuetral'))
            queens_power_rangers = QUEEN['queen_controls']['power_rangers']
            powerRangers = list(queens_power_rangers.keys())
            star = st.selectbox('Power Rangers', powerRangers, index=powerRangers.index(["1Minute_1Day" if "1Minute_1Day" in powerRangers else powerRangers[0]][0]))
            ranger_waves_types = list(queens_power_rangers[star].keys())
            ranger_waves = list(queens_power_rangers[star]['mac'].keys())

            wave_type = st.selectbox('Wave_Type', ranger_waves_types, index=ranger_waves_types.index(["mac" if "mac" in ranger_waves_types else ranger_waves_types[0]][0]))
            wave_ = st.selectbox('Wave', ranger_waves, index=ranger_waves.index(["buy_wave" if "buy_wave" in ranger_waves else ranger_waves[0]][0]))


            st.write(wave_)
            ranger_settings = queens_power_rangers[star][wave_type][wave_][theme_token]
            df_i = pd.DataFrame(ranger_settings.items())
            df = df_i.rename(columns={0: 'PowerRanger', 1: theme_token}) 

            
            grid_response = build_AGgrid_df(data=df, reload_data=False, height=333, update_cols=['UpdateRangerTheme'])
            data = grid_response['data']
            selected = grid_response['selected_rows'] 
            df_sel = pd.DataFrame(selected)
            st.write(df_sel)
            
            save_wavePRanger = st.button('Save')
            if save_wavePRanger:
                # Create
                app_request_package = create_AppRequest_package(request_name=control_option, archive_bucket='queen_contorls_requests')
                app_request_package['star'] = star
                app_request_package['wave_type'] = wave_type
                app_request_package['wave_'] = wave_
                app_request_package['theme_token'] = theme_token
                app_request_package['rangers_values'] = dict(zip(df_sel['PowerRanger'], df_sel['UpdateRangerTheme_update']))

                # ranger_wave_update = {star: {wave_: { theme_token: update_values } }}  ### UPDATER HERE

                # control_upate = {'control_update' : ranger_wave_update}
                # app_request_package.update(control_upate)
        
                # Save
                st.write(app_request_package)
                APP_requests['power_rangers'].append(app_request_package)
                APP_requests['power_rangers_lastupdate'] = datetime.datetime.now().astimezone(est)
                PickleData(pickle_file=PB_App_Pickle, data_to_store=APP_requests)
                return_image_upon_save(bee_power_image=bee_power_image)

                return True


            return True

        elif control_option.lower() == 'symbols_stars_tradingmodel':
            mark_down_text(color='Black', text='Ticker Model')

            c1, c2, = st.columns(2)
            with c1:
                tickers_avail = list(QUEEN['queen_controls'][control_option].keys())
                ticker_option_qc = st.selectbox("Select Tickers", tickers_avail, index=tickers_avail.index(["SPY" if "SPY" in tickers_avail else tickers_avail[0]][0]))
                # Trading Model
                trading_model = QUEEN['queen_controls'][control_option][ticker_option_qc]
                trigbee_sel = st.selectbox("trigbees", list(trading_model['trigbees'].keys()))
            with c2:
                star_avail = list(QUEEN['queen_controls'][control_option][ticker_option_qc]['stars_kings_order_rules'].keys())
                star_option_qc = st.selectbox("Select Star", star_avail, index=star_avail.index(["1Minute_1Day" if "1Minute_1Day" in star_avail else star_avail[0]][0]))
                wave_blocks_option = st.selectbox("block time", KING['waveBlocktimes'])
                # wave_blocks_option = st.selectbox("block time", trading_model['stars_kings_order_rules'][star_option_qc]['trigbees'][trigbee_sel]['waveBlocktimes']['premarket'])
                trading_model__star = trading_model['stars_kings_order_rules'][star_option_qc]

            with st.expander("trading model"):
                st.write(trading_model)
            
            tic_options_mapping = {
            # 'QueenBeeTrader', 'trigbees': 'checkbox',
            'status': 'checkbox',
            'total_budget': 'number',
            'buyingpower_allocation_LongTerm':  'number', 'buyingpower_allocation_ShortTerm': 'number',
            'index_long_X': 'text', 'index_inverse_X': 'text', 
            'portforlio_weight_ask':  'number', 
            'max_single_trade_amount':  'number', 'allow_for_margin': 'checkbox', 
            'buy_ONLY_by_accept_from_QueenBeeTrader': 'checkbox', 
            'trading_model_name': 'text', 'portfolio_name': 'text', 
            'premarket': 'checkbox', 'afterhours': 'checkbox', 'morning_9-11': 'checkbox', 'lunch_11-2':'checkbox', 'afternoon_2-4': 'checkbox', 'Day': 'checkbox'}

            star_trigbee_mapping = {
                'status': 'checkbox',
            }
                
            kor_option_mapping = {
            'status': 'checkbox',
            'trade_using_limits': 'checkbox',
            'doubledown_timeduration': 'number',
            'max_profit_waveDeviation': 'number',
            'max_profit_waveDeviation_timeduration': 'number',
            'timeduration': 'number',
            'take_profit': 'number',
            'sellout': 'number',
            'sell_trigbee_trigger': 'checkbox',
            'stagger_profits': 'checkbox',
            'scalp_profits': 'checkbox',
            'scalp_profits_timeduration': 'number',
            'stagger_profits_tiers': 'number',
            'limitprice_decay_timeduration': 'number'}


            with st.form('trading model form'):
                star_settings_upadte = {}
                star__items = {}

                trigbee_update = trading_model__star['trigbees'][trigbee_sel]
                king_order_rules_update = trading_model__star['trigbees'][trigbee_sel][wave_blocks_option]

                with st.expander('Ticker Settings'):
                    st.write('tic level', QUEEN['queen_controls'][control_option][ticker_option_qc].keys())

                    mark_down_text(text='Ticker Settings')
                    # power rangers
                    for k,v in trading_model['power_rangers'].items():
                        star__items[k] = st.checkbox(label=k, value=v, key=f'{"tic_level1"}{k}{v}')
                    # all ticker settings
                    for kor_option, kor_v in trading_model.items():
                        if kor_option in tic_options_mapping.keys():
                            st_func = tic_options_mapping[kor_option]
                            if st_func == 'checkbox':
                                trading_model[kor_option] = st.checkbox(label=f'{ticker_option_qc}{"_"}{kor_option}', value=kor_v, key=f'{ticker_option_qc}{"_"}{kor_option}')
                            elif st_func == 'number':
                                trading_model[kor_option] = st.number_input(label=f'{ticker_option_qc}{"_"}{kor_option}', value=kor_v, key=f'{ticker_option_qc}{"_"}{kor_option}')
                            elif st_func == 'text':
                                trading_model[kor_option] = st.text_input(label=f'{ticker_option_qc}{"_"}{kor_option}', value=kor_v, key=f'{ticker_option_qc}{"_"}{kor_option}')
                        else:
                            # trading_model[kor_option] = kor_v
                            st.write("missing ", kor_option)
                    
                with st.expander('Star Settings'):
                    st.write(QUEEN['queen_controls'][control_option][ticker_option_qc]['stars_kings_order_rules'][star_option_qc].keys())

                    mark_down_text(text=f'{star_option_qc}{" Star Settings"}') 
                    control_status = st.selectbox("Ticker Active", ['active', 'not_active'], index=['active', 'not_active'].index(trading_model__star['status']))
                    total_budget = st.number_input(label='total_budget', value=float(trading_model__star['total_budget']))
                    trade_using_limits = st.checkbox("trade_using_limits", value=trading_model__star['trade_using_limits'])
                    buyingpower_allocation_LongTerm = st.number_input(label='buyingpower_allocation_LongTerm', value=trading_model__star['buyingpower_allocation_LongTerm'])
                    buyingpower_allocation_ShortTerm = st.number_input(label='buyingpower_allocation_ShortTerm', value=trading_model__star['buyingpower_allocation_ShortTerm'])

                    st.write("active stars")
                    active_stars = {}
                    for k,v in trading_model__star['power_rangers'].items():
                        active_stars[k] = st.checkbox(label=f'{k}', value=v, key=f'{"star_level2"}{k}{v}')

                with st.expander(f'{"Star Trigbee Settings: "}{trigbee_sel}'):
                    
                    mark_down_text(text=f'{trigbee_sel}')
                    for kor_option, kor_v in trigbee_update.items():
                        if kor_option in star_trigbee_mapping.keys():
                            st_func = star_trigbee_mapping[kor_option]
                            if st_func == 'checckbox':
                                trigbee_update[kor_option] = st.checkbox(label=f'{trigbee_sel}{"_"}{kor_option}', value=kor_v, key=f'{trigbee_sel}{"_"}{kor_option}')
                            elif st_func == 'number':
                                trigbee_update[kor_option] = st.number_input(label=f'{trigbee_sel}{"_"}{kor_option}', value=kor_v, key=f'{trigbee_sel}{"_"}{kor_option}')
                            elif st_func == 'text':
                                trigbee_update[kor_option] = st.text_input(label=f'{trigbee_sel}{"_"}{kor_option}', value=kor_v, key=f'{trigbee_sel}{"_"}{kor_option}')
                        else:
                            print('missing', kor_option)
                            st.write("missing ", kor_option)

                with st.expander(f'{"StarTrigbee WaveBlocktime KingOrderRules "}{trigbee_sel}{" >>> "}{wave_blocks_option}'):
                    mark_down_text(text=f'{trigbee_sel}{" >>> "}{wave_blocks_option}')
                    for kor_option, kor_v in king_order_rules_update.items():
                        if kor_option in kor_option_mapping.keys():
                            st_func = kor_option_mapping[kor_option]
                            if st_func == 'checckbox':
                                king_order_rules_update[kor_option] = st.checkbox(label=f'{trigbee_sel}{"_"}{wave_blocks_option}{"_"}{kor_option}', value=kor_v, key=f'{trigbee_sel}{"_"}{wave_blocks_option}{"_"}{kor_option}')
                            elif st_func == 'number':
                                king_order_rules_update[kor_option] = st.number_input(label=f'{trigbee_sel}{"_"}{wave_blocks_option}{"_"}{kor_option}', value=kor_v, key=f'{trigbee_sel}{"_"}{wave_blocks_option}{"_"}{kor_option}')
                            elif st_func == 'text':
                                king_order_rules_update[kor_option] = st.text_input(label=f'{trigbee_sel}{"_"}{wave_blocks_option}{"_"}{kor_option}', value=kor_v, key=f'{trigbee_sel}{"_"}{wave_blocks_option}{"_"}{kor_option}')
                        else:
                            print('missing')
                            st.write("missing ", kor_option)
                            king_order_rules_update[kor_option] = kor_v


                # Create App Package
                save_button_addranger = st.form_submit_button("Save Trading Model Settings")
                if save_button_addranger:
                    app_req = create_AppRequest_package(request_name='trading_models')
                    # Ticker Level 1
                    # trading_model.update(ticker_update)

                    trading_model['status'] = control_status
                    trading_model['trade_using_limits'] = trade_using_limits
                    trading_model['buyingpower_allocation_LongTerm'] = buyingpower_allocation_LongTerm
                    trading_model['buyingpower_allocation_ShortTerm'] = buyingpower_allocation_ShortTerm
                    trading_model['total_budget'] = total_budget
                    trading_model['power_rangers'] = {k: v for (k,v) in active_stars.items()}

                    # Star Level 2
                    trading_model['stars_kings_order_rules'][star_option_qc].update(ticker_update)
                    
                    # Trigbees Level 3
                    trading_model['stars_kings_order_rules'][star_option_qc]['trigbees'][trigbee_sel].update(trigbee_update)
                    
                    # WaveBlock Time Levle 4
                    trading_model['stars_kings_order_rules'][star_option_qc]['trigbees'][trigbee_sel][wave_blocks_option].update(king_order_rules_update)


                    st.write(trading_model)
                    app_req['trading_model'] = trading_model
                    APP_requests['trading_models'].append(app_req)
                    PickleData(pickle_file=PB_App_Pickle, data_to_store=APP_requests)
                    return_image_upon_save(bee_power_image=bee_power_image)
            
        else:
            st.write("PENDING WORK")


    def queen_order_update(latest_queen_order, c_order_input):
        with st.form("my_form"):
            df = pd.DataFrame(latest_queen_order)
            df = df.T.reset_index()
            df = df.astype(str)
            # for col in df.columns:
            #     df[col] = df[col].astype(str)
            df = df.rename(columns={0: 'main'})
            grid_response = build_AGgrid_df(data=df, reload_data=False, update_cols=['update_column'])
            data = grid_response['data']
            # st.write(data)
            ttframe = data[data['index'] == 'ticker_time_frame'].copy()
            ttframe = ttframe.iloc[0]['main']
            # st.write(ttframe.iloc[0]['main'])
            selected = grid_response['selected_rows'] 
            df_sel = pd.DataFrame(selected)
            st.write(df_sel)
            if len(df_sel) > 0:
                up_values = dict(zip(df_sel['index'], df_sel['update_column_update']))
                up_values = {k: v for (k,v) in up_values.items() if len(v) > 0}
                update_dict = {c_order_input: up_values}
                st.session_state['update'] = update_dict
                st.session_state['ttframe_update'] = ttframe

            save_button_runorder = st.button("Save RunOrderUpdate")
            if save_button_runorder:
                # st.write(st.session_state['update'])
                update_sstate = st.session_state['update']
                update_ttframe = st.session_state['ttframe_update']
                order_dict = {'system': 'app',
                'queen_order_update_package': update_sstate,
                'app_requests_id' : f'{save_signals}{"_app-request_id_"}{return_timestamp_string()}{datetime.datetime.now().microsecond}',
                'ticker_time_frame': update_ttframe,
                }
                # st.write(order_dict)
                data = ReadPickleData(pickle_file=PB_App_Pickle)
                data['update_queen_order'].append(order_dict)
                PickleData(pickle_file=PB_App_Pickle, data_to_store=data)
                data = ReadPickleData(pickle_file=PB_App_Pickle)
                st.write(data['update_queen_order'])


    def create_AppRequest_package(request_name, archive_bucket=None):
        return {
        'app_requests_id': f'{request_name}{"_app-request_id_"}{return_timestamp_string()}{datetime.datetime.now().microsecond}', 
        'request_name': request_name,
        'archive_bucket': archive_bucket,
        'request_timestamp': datetime.datetime.now().astimezone(est),
        }


    def build_AGgrid_df(data, reload_data=False, fit_columns_on_grid_load=True, height=750, update_cols=['Update'], update_mode_value='MANUAL', paginationOn=True, dropdownlst=False, allow_unsafe_jscode=True):
        gb = GridOptionsBuilder.from_dataframe(data, min_column_width=30)
        if paginationOn:
            gb.configure_pagination(paginationAutoPageSize=True) #Add pagination
        gb.configure_side_bar() #Add a sidebar
        gb.configure_selection('multiple', use_checkbox=True, groupSelectsChildren="Group checkbox select children") #Enable multi-row selection
        if update_cols:
            for colName in update_cols:        
                if dropdownlst:
                    gb.configure_column(f'{colName}{"_update"}', editable=True, cellEditor='agSelectCellEditor', cellEditorParams={'values': dropdownlst })
                else:
                    gb.configure_column(f'{colName}{"_update"}', header_name=colName, editable=True, groupable=True)

        
        gridOptions = gb.build()

        gridOptions['wrapHeaderText'] = 'true'
        gridOptions['autoHeaderHeight'] = 'true'
        gridOptions['rememberGroupStateWhenNewData'] = 'true'
        gridOptions['enableCellTextSelection'] = 'true'

        grid_response = AgGrid(
            data,
            gridOptions=gridOptions,
            data_return_mode='AS_INPUT', 
            update_mode=update_mode_value, 
            fit_columns_on_grid_load=fit_columns_on_grid_load,
            # theme='blue', #Add theme color to the table
            enable_enterprise_modules=True,
            height=height, 
            # width='100%',
            reload_data=reload_data,
            allow_unsafe_jscode=allow_unsafe_jscode
        )
        return grid_response


    def build_AGgrid_df__queenorders(data, reload_data=False, fit_columns_on_grid_load=False, height=200, update_mode_value='VALUE_CHANGED', paginationOn=False,  allow_unsafe_jscode=True):
        # Color Code Honey

        gb = GridOptionsBuilder.from_dataframe(data, min_column_width=30)
        
        if paginationOn:
            gb.configure_pagination(paginationAutoPageSize=True) #Add pagination
        
        gb.configure_side_bar() #Add a sidebar

        gb.configure_selection('multiple', use_checkbox=True, groupSelectsChildren="Group checkbox select children") #Enable multi-row selection


        honey_colors = JsCode("""
        function(params) {
            if (params.value > 0) {
                return {
                    'color': '#027500',
                    'backgroundColor': '#FFFDE8'
                }
            }
            else if (params.value < 0) {
                return {
                    'color': '#F5AA7F',
                    'backgroundColor': '#5C2C0D'
                }
            }
        };
        """)

        # Config Columns
        gb.configure_column('queen_order_state', header_name='State', editable=True, cellEditor='agSelectCellEditor', cellEditorParams={'values': active_order_state_list })
        gb.configure_column("datetime", header_name='Date', type=["dateColumnFilter","customDateTimeFormat"], custom_format_string='MM/dd/yy', pivot=True, initialWidth=100, maxWidth=110, autoSize=True)
        gb.configure_column("symbol", pivot=True, resizable=True, initialWidth=89, autoSize=True)
        gb.configure_column("trigname", header_name='TrigBee', pivot=True, wrapText=True, resizable=True, initialWidth=100, maxWidth=120, autoSize=True)
        gb.configure_column("ticker_time_frame", header_name='Star', pivot=True, wrapText=True, resizable=True, initialWidth=120, maxWidth=140, autoSize=True)
        gb.configure_column("honey", header_name='Honey', cellStyle=honey_colors, type=["numericColumn"], wrapText=True, resizable=True, initialWidth=89, autoSize=True)
        gb.configure_column("$honey", header_name='Money', cellStyle=honey_colors, type=["numericColumn", "numberColumnFilter", "customCurrencyFormat"], custom_currency_symbol="$", wrapText=True, resizable=True, initialWidth=89, maxWidth=100, autoSize=True)
        gb.configure_column("honey_time_in_profit", header_name='Time.In.Honey', resizable=True, maxWidth=120, autoSize=True, autoHeight=True)
        gb.configure_column("filled_qty", wrapText=True, resizable=True, initialWidth=95, maxWidth=100, autoSize=True)
        gb.configure_column("qty_available", header_name='available_qty', autoHeight=True, wrapText=True, resizable=True, initialWidth=105, maxWidth=130, autoSize=True)
        gb.configure_column("filled_avg_price", type=["numericColumn", "numberColumnFilter", "customCurrencyFormat"], custom_currency_symbol="$", header_name='filled_avg_price', autoHeight=True, wrapText=True, resizable=True, initialWidth=120, maxWidth=130, autoSize=True)
        gb.configure_column("limit_price", type=["numericColumn", "numberColumnFilter", "customCurrencyFormat"], custom_currency_symbol="$", resizable=True, initialWidth=95, maxWidth=100, autoSize=True)
        gb.configure_column("cost_basis",   type=["numericColumn", "numberColumnFilter", "customCurrencyFormat"], custom_currency_symbol="$", autoHeight=True, wrapText=True, resizable=True, initialWidth=110, maxWidth=120, autoSize=True)
        gb.configure_column("wave_amo",   type=["numericColumn", "numberColumnFilter", "customCurrencyFormat"], custom_currency_symbol="$", autoHeight=True, wrapText=True, resizable=True, initialWidth=110, maxWidth=120, autoSize=True)
        gb.configure_column("order_rules", header_name='OrderRules', wrapText=True, resizable=True, autoSize=True)

        ## WHY IS IT NO WORKING??? 
        # k_sep_formatter = JsCode("""
        # function(params) {
        #     return (params.value == null) ? params.value : params.value.toLocaleString('en-US',{style: "currency", currency: "USD"}); 
        # }
        # """)

        # int_cols = ['$honey', 'filled_avg_price', 'cost_basis', 'wave_amo']
        # gb.configure_columns(int_cols, valueFormatter=k_sep_formatter)
        # for int_col in int_cols:
        #     gb.configure_column(int_col, type=["numericColumn", "numberColumnFilter", "customCurrencyFormat"], custom_currency_symbol="$")
        

        gridOptions = gb.build()
        
        gridOptions['wrapHeaderText'] = 'true'
        gridOptions['autoHeaderHeight'] = 'true'
        gridOptions['rememberGroupStateWhenNewData'] = 'true'
        gridOptions['enableCellTextSelection'] = 'true'
        gridOptions['resizable'] = 'true'

        grid_response = AgGrid(
            data,
            gridOptions=gridOptions,
            data_return_mode='AS_INPUT', 
            update_mode=update_mode_value, 
            fit_columns_on_grid_load=fit_columns_on_grid_load,
            # theme='blue', #Add theme color to the table
            enable_enterprise_modules=True,
            height=height, 
            reload_data=reload_data,
            allow_unsafe_jscode=allow_unsafe_jscode
        )

        return grid_response


    def add_trading_model(QUEEN, ticker, trading_model_universe):
        trading_models = QUEEN['queen_controls']['symbols_stars_TradingModel']
        if ticker not in trading_models.keys():
            print("Ticker Missing Trading Model Adding Default Model1")
            tradingmodel1 = generate_TradingModel(ticker=ticker)['tradingmodel1']
            st.write(tradingmodel1)
            app_req = create_AppRequest_package(request_name='add_trading_model', archive_bucket='add_trading_model_requests')


    def its_morphin_time_view(QUEEN, STORY_bee, ticker, POLLENSTORY):

        now_time = datetime.datetime.now().astimezone(est)
        active_ttf = QUEEN['heartbeat']['available_tickers'] = [i for (i, v) in STORY_bee.items() if (now_time - v['story']['time_state']).seconds < 86400]
        
        all_df = []
        total_current_macd_tier = 0
        total_current_hist_tier = 0
        for ttf in active_ttf :
            if ttf in POLLENSTORY.keys() and ticker in ttf.split("_")[0]:
                df = POLLENSTORY[ttf]
                df = df[['timestamp_est', 'chartdate', 'name', 'macd_tier', 'hist_tier', 'profits']].copy()
                total_current_macd_tier += df.iloc[-1]['macd_tier']
                total_current_hist_tier += df.iloc[-1]['hist_tier']
                
                all_df.append(df)
        
        # st.write('macd', total_current_macd_tier, ': ', '{:,.2%}'.format(total_current_macd_tier/ 64))
        # st.write('hist', total_current_hist_tier, ': ', '{:,.2%}'.format(total_current_hist_tier / 64))
        
        # t = 'macd', total_current_macd_tier, " ", '{:,.2%}'.format(total_current_macd_tier/ 64)
        # h = 'hist', total_current_hist_tier, " ", '{:,.2%}'.format(total_current_hist_tier / 64)

        t = '{:,.2%}'.format(total_current_macd_tier/ 64)
        h = '{:,.2%}'.format(total_current_hist_tier / 64)


        return {'macd_tier_guage': t, 'hist_tier_guage': h}


    def mark_down_text(align='center', color=default_text_color, fontsize='33', text='Hello There', font=default_font):
        st.markdown('<p style="text-align: {}; font-family:{}; color:{}; font-size: {}px;">{}</p>'.format(align, font, color, fontsize, text), unsafe_allow_html=True)
        return True


    def page_line_seperator(height='3', border='none', color='#C5B743'):
        return st.markdown("""<hr style="height:{}px;border:{};color:#333;background-color:{};" /> """.format(height, border, color), unsafe_allow_html=True)


    def write_flying_bee(width="45", height="45", frameBorder="0"):
        return st.markdown('<iframe src="https://giphy.com/embed/ksE4eFvxZM3oyaFEVo" width={} height={} frameBorder={} class="giphy-embed" allowFullScreen></iframe><p><a href="https://giphy.com/gifs/bee-traveling-flying-into-next-week-like-ksE4eFvxZM3oyaFEVo"></a></p>'.format(width, height, frameBorder), unsafe_allow_html=True)


    def hexagon_gif(width="45", height="45", frameBorder="0"):
        return st.markdown('<iframe src="https://giphy.com/embed/Wv35RAfkREOSSjIZDS" width={} height={} frameBorder={} class="giphy-embed" allowFullScreen></iframe><p><a href="https://giphy.com/gifs/star-12-hexagon-Wv35RAfkREOSSjIZDS"></a></p>'.format(width, height, frameBorder), unsafe_allow_html=True)


    def local_gif(gif_path, width='33', height='33'):
        with open(gif_path, "rb") as file_:
            contents = file_.read()
            data_url = base64.b64encode(contents).decode("utf-8")
            st.markdown(f'<img src="data:image/gif;base64,{data_url}" width={width} height={height} alt="bee">', unsafe_allow_html=True)


    def flying_bee_gif(width='33', height='33'):
        with open(os.path.join(jpg_root, 'flyingbee_gif_clean.gif'), "rb") as file_:
            contents = file_.read()
            data_url = base64.b64encode(contents).decode("utf-8")
            st.markdown(f'<img src="data:image/gif;base64,{data_url}" width={width} height={height} alt="bee">', unsafe_allow_html=True)


    def pollen__story(df):
        with st.expander('pollen story', expanded=False):
            df_write = df.astype(str)
            st.dataframe(df_write)
            pass
            

    def queen_main_view():
        if st.session_state['admin'] == False:
            return False

        queens_subconscious_Thoughts(QUEEN=QUEEN)

        update_Workerbees(APP_requests=APP_requests)

        cq1, cq2 = st.columns(2)

        with cq1:
            return_buying_power(api=api)
            # return_total_profits(QUEEN=QUEEN)
            # page_line_seperator()
        with cq2:
            return_total_profits(QUEEN=QUEEN)
        
        page_line_seperator()

        return True
        

    def model_wave_results(STORY_bee):
        with st.expander('model results of queens court'):
            return_results = {}
            dict_list_ttf = analyze_waves(STORY_bee, ttframe_wave_trigbee=False)['d_agg_view_return']        

            ticker_list = set([i.split("_")[0] for i in dict_list_ttf.keys()])
            for ticker_option in ticker_list:
            
                for trigbee in dict_list_ttf[list(dict_list_ttf.keys())[0]]:
                    
                    ticker_selection = {k: v for k, v in dict_list_ttf.items() if ticker_option in k}
                    buys = [data[trigbee] for k, data in ticker_selection.items()]
                    df_trigbee_waves = pd.concat(buys, axis=0)
                    col_view = ['ticker_time_frame'] + [i for i in df_trigbee_waves.columns if i not in 'ticker_time_frame']
                    df_trigbee_waves = df_trigbee_waves[col_view]
                    color = 'Green' if 'buy' in trigbee else 'Red'

                    t_winners = sum(df_trigbee_waves['winners_n'])
                    t_losers = sum(df_trigbee_waves['losers_n'])
                    total_waves = t_winners + t_losers
                    win_pct = 100 * round(t_winners / total_waves, 2)

                    t_maxprofits = sum(df_trigbee_waves['sum_maxprofit'])

                    return_results[f'{ticker_option}{"_bee_"}{trigbee}'] = f'{"~Total Max Profits "}{round(t_maxprofits * 100, 2)}{"%"}{"  ~Win Pct "}{win_pct}{"%"}{": Winners "}{t_winners}{" :: Losers "}{t_losers}'
                # df_bestwaves = analyze_waves(STORY_bee, ttframe_wave_trigbee=df_trigbee_waves['ticker_time_frame'].iloc[-1])['df_bestwaves']

            df = pd.DataFrame(return_results.items())
            mark_down_text(color='#C5B743', text=f'{"Trigger Bee Model Results "}')
            st.write(df) 

            return True


    def clean_out_app_requests(QUEEN, APP_requests, request_buckets):
        save = False
        for req_bucket in request_buckets:
            if req_bucket not in APP_requests.keys():
                st.write("Verison Missing DB", req_bucket)
                continue
            for app_req in APP_requests[req_bucket]:
                if app_req['app_requests_id'] in QUEEN['app_requests__bucket']:
                    print("Quen Processed app req item")
                    archive_bucket = f'{req_bucket}{"_requests"}'
                    APP_requests[req_bucket].remove(app_req)
                    APP_requests[archive_bucket].append(app_req)
                    save = True
        if save:
            PickleData(pickle_file=PB_App_Pickle, data_to_store=APP_requests)


    def queens_subconscious_Thoughts(QUEEN):
        write_sub = []
        for key, bucket in QUEEN['subconscious'].items():
            if len(bucket) > 0:
                write_sub.append(bucket)
        expand_ = True if len(write_sub) > 0 else False
        if expand_:
            with st.expander('subconscious alert thoughts', expand_):
                st.write(write_sub)


    def clear_subconscious_Thought(QUEEN, APP_requests):
        with st.form('clear subconscious'):
            thoughts = QUEEN['subconscious'].keys()
            clear_thought = st.selectbox('clear subconscious thought', list(thoughts))
            
            if st.form_submit_button("Save"):
                app_req = create_AppRequest_package(request_name='subconscious', archive_bucket='subconscious_requests')
                app_req['subconscious_thought_to_clear'] = clear_thought
                app_req['subconscious_thought_new_value'] = []
                APP_requests['subconscious'].append(app_req)
                st.success("subconscious thought cleared")
                return_image_upon_save(bee_power_image=bee_power_image)
                PickleData(pickle_file=PB_App_Pickle, data_to_store=APP_requests)

                return True


    def queen_online(QUEEN):
        now = datetime.datetime.now(est)
        if (now - QUEEN['pq_last_modified']['pq_last_modified']).total_seconds() > 60:
            # st.write("YOUR QUEEN if OFFLINE")
            # mark_down_text(align='left', fontsize='15', color='Red', text="YOUR QUEEN is Asleep")
            cols = st.columns((1,1,5))
            with cols[0]:
                st.error("Your Queen Is Asleep")
                # st.snow()
            with cols[1]:
                local_gif(gif_path=flyingbee_grey_gif_path)
            return False
        else:
            return True

    def queen_chart(ticker_option, POLLENSTORY):
        # Main CHART Creation
        with st.expander('chart', expanded=False):
            df = POLLENSTORY[ticker_time_frame].copy()

            st.markdown('<div style="text-align: center;">{}</div>'.format(ticker_option), unsafe_allow_html=True)

            # star__view = its_morphin_time_view(QUEEN=QUEEN, STORY_bee=STORY_bee, ticker=ticker_option, POLLENSTORY=POLLENSTORY)
            
            day_only_option = st.checkbox("Only Today")
            
            if day_only_option:
                df_day = df['timestamp_est'].iloc[-1]
                df['date'] = df['timestamp_est'] # test

                df_today = df[df['timestamp_est'] > (datetime.datetime.now().replace(hour=1, minute=1, second=1)).astimezone(est)].copy()
                df_prior = df[~(df['timestamp_est'].isin(df_today['timestamp_est'].to_list()))].copy()

                df = df_today
            fig = create_main_macd_chart(df)
            st.write(fig)

            return True

    ########################################################
    ########################################################
    #############The Infinite Loop of Time #################
    ########################################################
    ########################################################
    ########################################################



    # """ if "__name__" == "__main__": """

    if gatekeeper:
        if 'admin' in st.session_state.keys() and st.session_state['admin']:
            admin = True
            st.sidebar.write('admin', admin)

        else:
            st.write("queenbee not yet authorized READ ONLY")
            st.sidebar.write('Read Only')
            admin = False
    else:
        st.write("Are you My Queen?")
        # sys.exit()
        st.stop()

    ## answer the question what to show to a User when they first Sign On OR whats a Preview to Show? I.E. if User Not allowed then show Sandbox Data?
    if authorized_user:
        READONLY = False
        # SETUP USER #
        # Client User DB
        db_root = init_clientUser_dbroot(client_user=client_user) # main_root = os.getcwd() // # db_root = os.path.join(main_root, 'db')
        init_pollen = init_pollen_dbs(db_root=db_root, prod=prod, queens_chess_piece='queen')
        PB_QUEEN_Pickle = init_pollen['PB_QUEEN_Pickle']
        PB_App_Pickle = init_pollen['PB_App_Pickle']
        PB_Orders_Pickle = init_pollen['PB_Orders_Pickle']

    else:
        # Read Only View
        READONLY = True
        db_root = os.path.join(main_root, 'db')  ## Force to Main db and Sandbox API
        prod = False
        load_dotenv(os.path.join(os.getcwd(), '.env'))
        init_pollen = init_pollen_dbs(db_root=db_root, prod=False, queens_chess_piece='queen')
        PB_QUEEN_Pickle = init_pollen['PB_QUEEN_Pickle']
        PB_App_Pickle = init_pollen['PB_App_Pickle']
        PB_Orders_Pickle = init_pollen['PB_Orders_Pickle']


    # """ Keys """ ### NEEDS TO BE FIXED TO PULL USERS API CREDS UNLESS USER IS PART OF MAIN.FUND.Account
    api = return_alpaca_api_keys(prod=prod)['api']

    # if authorized_user:
    portfolio = return_alpc_portolio(api)['portfolio']
    acct_info = refresh_account_info(api=api)

    # # if authorized_user: log type auth and none
    log_dir = os.path.join(db_root, 'logs')
    init_logging(queens_chess_piece=queens_chess_piece, db_root=db_root, prod=prod)

    # db global
    coin_exchange = "CBSE"

    # def run_main_page():
    KING = KINGME()
    pollen_theme = pollen_themes(KING=KING)
    # QUEEN Databases
    APP_requests = ReadPickleData(pickle_file=PB_App_Pickle)
    QUEEN = ReadPickleData(PB_QUEEN_Pickle)
    ORDERS = ReadPickleData(PB_Orders_Pickle)
    # Ticker DataBase
    ticker_db = read_pollenstory(db_root=os.path.join(os.getcwd(), 'db'), dbs=['castle.pkl', 'bishop.pkl', 'castle_coin.pkl', 'knight.pkl'])
    POLLENSTORY = ticker_db['pollenstory']
    STORY_bee = ticker_db['STORY_bee']

    queen_is_online = queen_online(QUEEN=QUEEN)


    ####### START ######
    if authorized_user:
        APP_requests['source'] = PB_App_Pickle
        APP_req = add_key_to_app(APP_requests)
        APP_requests = APP_req['APP_requests']
        if APP_req['update']:
            PickleData(PB_App_Pickle, APP_requests)

        clean_out_app_requests(QUEEN=QUEEN, APP_requests=APP_requests, request_buckets=['workerbees', 'queen_controls', 'subconscious'])

st.sidebar.button("Refresh ::: always Bee better")
# st.sidebar.write("always Bee better")

c1,c2,c3 = st.columns((1,3,1))
# with c1:
#     local_gif(gif_path=flyingbee_gif_path, width='33', height='33')
with c2:
    option = st.radio(
                "",
        ["queen", "controls",  "signal", "charts", "model_results", "pollen_engine"],
        key="main_radio",
        label_visibility='visible',
        # disabled=st.session_state.disabled,
        horizontal=True,
    )
# with c3:
#     # st.image(page_icon, caption='pollenq', width=54)
#     flying_bee_gif()

cols = st.columns((1,1,1,1,1,1,1,1,1,1,1,2))
if option == 'queen':
    with cols[2]:
        flying_bee_gif()
elif option == "controls":
    with cols[3]:
        flying_bee_gif()
elif option == "signal":
    with cols[4]:
        flying_bee_gif()
elif option == "charts":
    with cols[5]:
        flying_bee_gif()
elif option == "model_results":
    with cols[6]:
        flying_bee_gif()
elif option == "pollen_engine":
    with cols[7]:
        flying_bee_gif()

page_line_seperator('3', color=default_yellow_color)


def rename_trigbee_name(tribee_name):
    return tribee_name


def ticker_time_frame_UI_rename(ticker_time_frame):
    new_ttf = ticker_time_frame
    # group tickers . i.e. if apart of index = index is a character
    stars = stars() # 1Minute_1Day
    rename = {'ticker': {}, 'time': {}, 'stars': {}}
    return new_ttf


if str(option).lower() == 'queen':
    
    # Global Vars
    tickers_avail = [set(i.split("_")[0] for i in STORY_bee.keys())][0]
    tickers_avail.update({"all"})
    tickers_avail_op = list(tickers_avail)
    ticker_option = st.sidebar.selectbox("Tickers", tickers_avail_op, index=tickers_avail_op.index('SPY'))
    ticker = ticker_option
    ticker_storys = {k:v for (k,v) in STORY_bee.items() if k.split("_")[0] == ticker_option}
    ttframe_list = list(set([i.split("_")[1] + "_" + i.split("_")[2] for i in POLLENSTORY.keys()]))
    frame_option = st.sidebar.selectbox("Ticker_Stars", ttframe_list, index=ttframe_list.index(["1Minute_1Day" if "1Minute_1Day" in ttframe_list else ttframe_list[0]][0]))
    option_showaves = st.sidebar.selectbox("Show Waves", ('no', 'yes'), index=["no"].index("no"))

    today_day = datetime.datetime.now().day

    ticker_time_frame = f'{ticker_option}{"_"}{frame_option}'

    star__view = its_morphin_time_view(QUEEN=QUEEN, STORY_bee=STORY_bee, ticker=ticker_option, POLLENSTORY=POLLENSTORY)

    with st.expander(f'{ticker_option} Stars {"MACD Guage "}{star__view["macd_tier_guage"]} {"Hist Guage "}{star__view["hist_tier_guage"]}'):
        mark_down_text(fontsize=25, text=f'{"MACD Guage "}{star__view["macd_tier_guage"]}')
        mark_down_text(fontsize=22, text=f'{"Hist Guage "}{star__view["hist_tier_guage"]}')
        df = story_view(STORY_bee=STORY_bee, ticker=ticker_option)['df']
        df_style = df.style.background_gradient(cmap="RdYlGn", gmap=df['current_macd_tier'], axis=0, vmin=-8, vmax=8)

        st.dataframe(df_style)


    queen_main_view()
    queen_triggerbees()
    queen_order_flow()
    queen_chart(ticker_option=ticker_option, POLLENSTORY=POLLENSTORY)

    
    if ticker_option != 'all': ### Trigbee Waves
      
        page_line_seperator(color=default_yellow_color)

        dict_list_ttf = analyze_waves(STORY_bee, ttframe_wave_trigbee=False)['d_agg_view_return']        

        for trigbee in dict_list_ttf[list(dict_list_ttf.keys())[0]]:
            
            ticker_selection = {k: v for k, v in dict_list_ttf.items() if ticker_option in k}
            buys = [data[trigbee] for k, data in ticker_selection.items()]
            df_trigbee_waves = pd.concat(buys, axis=0)
            col_view = ['ticker_time_frame'] + [i for i in df_trigbee_waves.columns if i not in 'ticker_time_frame']
            df_trigbee_waves = df_trigbee_waves[col_view]
            color = 'Green' if 'buy' in trigbee else 'Red'
            df_bestwaves = analyze_waves(STORY_bee, ttframe_wave_trigbee=df_trigbee_waves['ticker_time_frame'].iloc[-1])['df_bestwaves']

            t_winners = sum(df_trigbee_waves['winners_n'])
            t_losers = sum(df_trigbee_waves['losers_n'])
            total_waves = t_winners + t_losers
            win_pct = 100 * round(t_winners / total_waves, 2)

            t_maxprofits = sum(df_trigbee_waves['sum_maxprofit'])
            
            # Top Winners Header
            df_bestwaves = df_bestwaves[[col for col in df_bestwaves.columns if col not in ['wave_id', 'winners_n', 'loser_n']]]
            df_bestwaves = df_bestwaves[['maxprofit'] + [col for col in df_bestwaves.columns if col not in ['maxprofit']]]
            
            c1, c2, c3, c4 = st.columns((1,3,3,3))
            with c1:
                flying_bee_gif()
            with c2:
                mark_down_text(align='left', color=color, fontsize='15', text=f'{"Trigger Bee "}{trigbee}')
            with c3:
                # write_flying_bee(25,25)
                mark_down_text(align='left', color='Green', fontsize='15', text=f'{"~Total Max Profits "}{round(t_maxprofits * 100, 2)}{"%"}')
            with c4:
                # write_flying_bee(28,28)
                mark_down_text(align='left', color='Green', fontsize='15', text=f'{"~Win Pct "}{win_pct}{"%"}{": Winners "}{t_winners}{" :: Losers "}{t_losers}')

            # with st.expander(f'{"Todays Best Waves: "}{len(df_bestwaves)}', expanded=False):
            #     st.dataframe(df_bestwaves)
            # c1, c2, c3 = st.columns(3)
            # with c1:
                # mark_down_text(color='Purple', align='center', text=f'{"All Ticker Bee Waves"}')
            with st.expander(f'{"Top "}{len(df_bestwaves)}{" Waves"}', expanded=False):
                st.dataframe(df_bestwaves)
            # with c2:
            #     with st.expander(f'{"Top "}{len(df_bestwaves)}{" Waves"}', expanded=False):
            #         st.dataframe(df_bestwaves)

            with st.expander(f'{"All Ticker Bee Waves"}', expanded=False):
                st.dataframe(df_trigbee_waves)
        page_line_seperator(color=default_yellow_color, height='3')


        if option_showaves.lower() == 'yes':

            ttframe = f'{ticker_option}{"_"}{frame_option}'
            knowledge = ticker_storys[ttframe]
            
            mark_down_text(text=ttframe)
            st.write("waves story -- investigate BACKEND functions")
            df = knowledge['waves']['story']
            df = df.astype(str)
            st.dataframe(df)

            st.write("buy cross waves")
            m_sort = knowledge['waves']['buy_cross-0']
            df_m_sort = pd.DataFrame(m_sort).T
            df_m_sort = df_m_sort.astype(str)
            st.dataframe(data=df_m_sort)

            st.write("sell cross waves")
            m_sort = knowledge['waves']['sell_cross-0']
            df_m_sort = pd.DataFrame(m_sort).T
            df_m_sort = df_m_sort.astype(str)
            st.dataframe(data=df_m_sort)
    else:
        # st.write(STORY_bee)
        print("groups not allowed yet")
    
    see_pollenstory = st.button("Show Me Pollenstory")
    if see_pollenstory:
        with st.expander('STORY_bee'):
            st.write(STORY_bee[ticker_time_frame]['story'])
        
        pollen__story(df=POLLENSTORY[ticker_time_frame].copy())

if str(option).lower() == 'controls':
    col1, col2 = st.columns(2)
    if admin == False:
        st.write("permission denied")
        st.stop()
    else:
        with st.expander('Heartbeat'):
            st.write(QUEEN['heartbeat'])
        
        with col1:
            stop_queenbee(APP_requests=APP_requests)
        with col2:
            refresh_queenbee_controls(APP_requests=APP_requests)

        theme_list = list(pollen_theme.keys())

        page_line_seperator()

        contorls = list(QUEEN['queen_controls'].keys())
        control_option = st.selectbox('select control', contorls, index=contorls.index('theme'))
        update_QueenControls(APP_requests=APP_requests, control_option=control_option, theme_list=theme_list)

        clear_subconscious_Thought(QUEEN=QUEEN, APP_requests=APP_requests)


if str(option).lower() == 'charts':
    tickers_avail = list([set(i.split("_")[0] for i in POLLENSTORY.keys())][0])
    ticker_option = st.sidebar.selectbox("Tickers", tickers_avail, index=tickers_avail.index(["SPY" if "SPY" in tickers_avail else tickers_avail[0]][0]))
    ticker = ticker_option
    ttframe_list = list(set([i.split("_")[1] + "_" + i.split("_")[2] for i in POLLENSTORY.keys()]))
    ttframe_list.append(["short_star", "mid_star", "long_star", "retire_star"])
    frame_option = st.sidebar.selectbox("ttframes", ttframe_list, index=ttframe_list.index(["1Minute_1Day" if "1Minute_1Day" in ttframe_list else ttframe_list[0]][0]))
    day_only_option = st.sidebar.selectbox('Show Today Only', ['no', 'yes'], index=['no'].index('no'))
    slope_option = st.sidebar.selectbox('Show Slopes', ['no', 'yes'], index=['no'].index('no'))
    wave_option = st.sidebar.selectbox('Show Waves', ['no', 'yes'], index=['no'].index('no'))
    fullstory_option = st.sidebar.selectbox('POLLENSTORY', ['no', 'yes'], index=['yes'].index('yes'))
    selections = [i for i in POLLENSTORY.keys() if i.split("_")[0] in ticker_option and i.split("_")[1] in frame_option]

    ticker_time_frame = selections[0]
    df = POLLENSTORY[ticker_time_frame].copy()
    st.markdown('<div style="text-align: center;">{}</div>'.format(ticker_option), unsafe_allow_html=True)

    # star__view = its_morphin_time_view(QUEEN=QUEEN, STORY_bee=STORY_bee, ticker=ticker_option, POLLENSTORY=POLLENSTORY)

    if day_only_option == 'yes':
        df_day = df['timestamp_est'].iloc[-1]
        df['date'] = df['timestamp_est'] # test

        df_today = df[df['timestamp_est'] > (datetime.datetime.now().replace(hour=1, minute=1, second=1)).astimezone(est)].copy()
        df_prior = df[~(df['timestamp_est'].isin(df_today['timestamp_est'].to_list()))].copy()

        df = df_today

    min_1 = POLLENSTORY[f'{ticker_option}{"_"}{"1Minute_1Day"}'].copy()
    min_5 = POLLENSTORY[f'{ticker_option}{"_"}{"5Minute_5Day"}'].copy()
    min_30m = POLLENSTORY[f'{ticker_option}{"_"}{"30Minute_1Month"}'].copy()
    min_1hr = POLLENSTORY[f'{ticker_option}{"_"}{"1Hour_3Month"}'].copy()
    min_2hr = POLLENSTORY[f'{ticker_option}{"_"}{"2Hour_6Month"}'].copy()
    min_1yr = POLLENSTORY[f'{ticker_option}{"_"}{"1Day_1Year"}'].copy()

    option__ = st.radio(
                            "",
        ['1Min', '5Min', '30m', '1hr', '2hr', '1Yr', 'all'],
        key="signal_radio",
        label_visibility='visible',
        # disabled=st.session_state.disabled,
        horizontal=True,
    )

    if option__.lower() == 'all':
        c1, c2 = st.columns(2)
        with c1:
            st.write(create_main_macd_chart(min_1))
        with c2:
            st.write(create_main_macd_chart(min_5))
        c1, c2 = st.columns(2)
        with c1:
            st.write(create_main_macd_chart(min_30m))
        with c2:
            st.write(create_main_macd_chart(min_1hr))
        c1, c2 = st.columns(2)
        with c1:
            st.write(create_main_macd_chart(min_2hr))
        with c2:
            st.write(create_main_macd_chart(min_1yr))
    else:
        # Main CHART Creation
        radio_b_dict = {'1Min': '1Minute_1Day', 
        '5Min': '5Minute_5Day', '30m': '30Minute_1Month', 
        '1hr': '1Hour_3Month' , '2hr': '2Hour_6Month', '1Yr': '1Day_1Year'}
        ticker_time_frame = f'{ticker}_{radio_b_dict[option__]}'
        st.write(create_main_macd_chart(POLLENSTORY[ticker_time_frame].copy()))

    if slope_option == 'yes':
        slope_cols = [i for i in df.columns if "slope" in i]
        slope_cols.append("close")
        slope_cols.append("timestamp_est")
        slopes_df = df[['timestamp_est', 'hist_slope-3', 'hist_slope-6', 'macd_slope-3']]
        fig = create_slope_chart(df=df)
        st.write(fig)
        st.dataframe(slopes_df)
        
    if wave_option == "yes":
        fig = create_wave_chart(df=df)
        st.write(fig)
        
        dft = split_today_vs_prior(df=df)
        dft = dft['df_today']

        fig=create_wave_chart_all(df=dft, wave_col='buy_cross-0__wave')
        st.write(fig)

        st.write("current wave")
        current_buy_wave = df['buy_cross-0__wave_number'].tolist()
        current_buy_wave = [int(i) for i in current_buy_wave]
        current_buy_wave = max(current_buy_wave)
        st.write("current wave number")
        st.write(current_buy_wave)
        dft = df[df['buy_cross-0__wave_number'] == str(current_buy_wave)].copy()
        st.write({'current wave': [dft.iloc[0][['timestamp_est', 'close', 'macd']].values]})
        fig=create_wave_chart_single(df=dft, wave_col='buy_cross-0__wave')
        st.write(fig)


if str(option).lower() == 'signal':

    c1,c2,c3 = st.columns(3)
    
    with c2:
        option__ = st.radio(
                                "",
            ['beeaction', 'orders', 'QueenOrders', 'WorkerBees'],
            key="signal_radio",
            label_visibility='visible',
            # disabled=st.session_state.disabled,
            horizontal=True,
        )
    save_signals = option__
    c1,c2,c3,c4,c5 = st.columns(5)

    col1, col2 = st.columns(2)

    ## SHOW CURRENT THEME
    with st.sidebar:
        # with st.echo():
            # st.write("theme>>>", QUEEN['collective_conscience']['theme']['current_state'])
        st.write("theme>>>", QUEEN['queen_controls']['theme'])


    if save_signals == 'QueenOrders':
        queen_QueenOrders()
    
    
    # if save_signals == 'orders':
    #     show_app_req = st.selectbox('show app requests', ['yes', 'no'], index=['yes'].index('yes'))
    #     if show_app_req == 'yes':
    #         data = ReadPickleData(pickle_file=PB_App_Pickle)
    #         st.write("sell orders", data['sell_orders'])
    #         st.write("buy orders", data['buy_orders'])
    #     df = QUEEN['queen_orders']
        
    #     running_orders = df[df['queen_order_state'] == 'running'].copy()
        
    #     # running_portfolio = return_dfshaped_orders(running_orders)
        
    #     # portfolio = return_alpc_portolio(api)['portfolio']
    #     # p_view = {k: [v['qty'], v['qty_available']] for (k,v) in portfolio.items()}
    #     # st.write(p_view)
    #     # st.write(running_portfolio)

    #     position_orders = [i for i in running_orders if not i['client_order_id'].startswith("close__") ]
    #     closing_orders = [i for i in running_orders if i['client_order_id'].startswith("close__") ]
    #     c_order_ids = [i['client_order_id'] for i in position_orders]
    #     c_order_iddict = {i['client_order_id']: idx for idx, i in enumerate(position_orders)}
    #     c_order_ids.append("Select")
    #     c_order_id_option = st.selectbox('client_order_id', c_order_ids, index=c_order_ids.index('Select'))
    #     if c_order_id_option != 'Select':
    #         run_order = position_orders[c_order_iddict[c_order_id_option]]
    #         run_order_alpaca = check_order_status(api=api, client_order_id=c_order_id_option, queen_order=run_order, prod=prod)
    #         st.write(("pollen matches alpaca", float(run_order_alpaca['filled_qty']) == float(run_order['filled_qty']))) ## VALIDATION FOR RUN ORDERS
    #         st.write(run_order_alpaca)
    #         st.write(run_order['filled_qty'])
    #         sell_qty_option = st.number_input(label="Sell Qty", max_value=float(run_order['filled_qty']), value=float(run_order['filled_qty']), step=1e-4, format="%.4f")
    #         # sell_qty_option = st.selectbox('sell_qty', [run_order['filled_qty']])
    #         type_option = st.selectbox('type', ['market'], index=['market'].index('market'))                

    #         sell_command = st.button("Sell Order")
    #         if sell_command:
    #             st.write("yes")
    #             # val qty
    #             if sell_qty_option > 0 and sell_qty_option <= float(run_order['filled_qty']):
    #                 print("qty validated")
    #                 # process order signal
    #                 client_order_id = c_order_id_option
    #                 sellable_qty = sell_qty_option
                    
    #                 order_dict = {'system': 'app',
    #                 'request_time': datetime.datetime.now(),
    #                 'client_order_id': client_order_id, 'sellable_qty': sellable_qty,
    #                 'side': 'sell',
    #                 'type': type_option,
    #                 'app_requests_id' : f'{save_signals}{"_app-request_id_"}{return_timestamp_string()}{datetime.datetime.now().microsecond}'

    #                 }
    #                 data = ReadPickleData(pickle_file=PB_App_Pickle)
    #                 data['sell_orders'].append(order_dict)
    #                 PickleData(pickle_file=PB_App_Pickle, data_to_store=data)
    #                 data = ReadPickleData(pickle_file=PB_App_Pickle)
    #                 st.write(data['sell_orders'])
                
    #             if sell_qty_option < 0 and sell_qty_option >= float(run_order['filled_qty']):
    #                 print("qty validated")
    #                 # process order signal
    #                 client_order_id = c_order_id_option
    #                 sellable_qty = sell_qty_option
                    
    #                 order_dict = {'system': 'app',
    #                 'request_time': datetime.datetime.now(),
    #                 'client_order_id': client_order_id, 'sellable_qty': sellable_qty,
    #                 'side': 'sell',
    #                 'type': type_option,
    #                 'app_requests_id' : f'{save_signals}{"_app-request_id_"}{return_timestamp_string()}{datetime.datetime.now().microsecond}'

    #                 }
    #                 data = ReadPickleData(pickle_file=PB_App_Pickle)
    #                 data['sell_orders'].append(order_dict)
    #                 PickleData(pickle_file=PB_App_Pickle, data_to_store=data)
    #                 data = ReadPickleData(pickle_file=PB_App_Pickle)
    #                 st.write(data['sell_orders'])

    
    if save_signals == 'beeaction':

        queen_beeAction()


if str(option).lower() == 'model_results':
    model_wave_results(STORY_bee)
    

if str(option).lower() == 'pollen_engine':

    with st.expander('betty_bee'):
        betty_bee = ReadPickleData(os.path.join(db_root, 'betty_bee.pkl'))
        df_betty = pd.DataFrame(betty_bee)
        df_betty = df_betty.astype(str)
        st.write(df_betty)

    with st.expander('charlie_bee'):

        queens_charlie_bee = ReadPickleData(os.path.join(db_root, 'charlie_bee.pkl'))
        df_charlie = pd.DataFrame(queens_charlie_bee)
        df_charlie = df_charlie.astype(str)
        st.write(df_charlie)
    
    if admin == False:
        st.warning("End of the Line")
        st.stop()
    with st.expander('queen logs'):
        logs = os.listdir(log_dir)
        logs = [i for i in logs if i.endswith(".log")]
        log_file = st.selectbox('log files', list(logs))
        with open(os.path.join(log_dir, log_file), 'r') as f:
            content = f.readlines()
            st.write(content)
    with st.expander('users db'):
        con = sqlite3.connect("db/users.db")
        cur = con.cursor()

        users = cur.execute("SELECT * FROM users").fetchall()
        st.dataframe(pd.DataFrame(users))
    

##### END ####