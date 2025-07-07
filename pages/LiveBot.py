# LiveBot
import pandas as pd
from pages.conscience import queens_conscience
from chess_piece.queen_hive import init_queenbee, hive_dates, return_market_hours, kingdom__grace_to_find_a_Queen, create_QueenOrderBee, kingdom__global_vars
from chess_piece.king import return_app_ip
from chess_piece.app_hive import set_streamlit_page_config_once, sac_menu_buttons
from pages.orders import order_grid, config_orders_cols
import streamlit as st
import pytz
from datetime import datetime

est = pytz.timezone("US/Eastern")

def demo_bot():
    menu_id = sac_menu_buttons("demo")

    client_user = 'stapinskistefan@gmail.com'
    prod = False
    KING = kingdom__grace_to_find_a_Queen()

    st.session_state['sneak_peak'] = True
    st.info("Welcome, feel free to place trades, every trade is handled and management by the AI using TimeSeries Weighted Averages...TimeValueMoney")
    st.session_state['sneak_peak'] = False

    st.session_state["ip_address"] = return_app_ip()
    print(st.session_state["ip_address"])
    st.session_state["username"] = client_user
    st.session_state['db_root'] = 'db__stapinskistefan_99757341'
    st.session_state['prod'] = False

    if menu_id == 'Orders':
        # seconds_to_market_close = st.session_state['seconds_to_market_close'] if 'seconds_to_market_close' in st.session_state else 0
        # client_user = st.session_state['client_user']
        ip_address = st.session_state['ip_address']
        prod = st.session_state['prod']
        queen_orders = pd.DataFrame([create_QueenOrderBee(queen_init=True)])
        king_G = kingdom__global_vars()
        active_order_state_list = king_G.get('active_order_state_list')
        config_cols = config_orders_cols(active_order_state_list)
        missing_cols = [i for i in queen_orders.iloc[-1].index.tolist() if i not in config_cols.keys()]
        order_grid(client_user, config_cols, missing_cols, ip_address)
        st.stop()


    qb = init_queenbee(client_user=client_user, prod=prod, orders_v2=True, 
                       queen_king=True, api=True, init=True, 
                       revrec=True, 
                       demo=True)
    QUEEN_KING = qb.get('QUEEN_KING')
    api = qb.get('api')
    revrec = qb.get('revrec')

    trading_days = hive_dates(api=api)['trading_days']
    # st.write(trading_days) # STORE IN KING and only call once
    mkhrs = return_market_hours(trading_days=trading_days)
    seconds_to_market_close = (datetime.now(est).replace(hour=16, minute=0, second=0) - datetime.now(est)).total_seconds()
    refresh_sec = 8 if seconds_to_market_close > 0 and mkhrs == 'open' else 89
    # account_header_grid(client_user, prod, refresh_sec, st.session_state["ip_address"], seconds_to_market_close)
    queens_conscience(api, revrec, KING, QUEEN_KING, api, sneak_peak=True, show_acct=True)
if __name__ == '__main__':
    set_streamlit_page_config_once()
    demo_bot()