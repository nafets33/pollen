# LiveBot
from pages.conscience import queens_conscience
from chess_piece.queen_hive import init_queenbee, hive_dates, return_market_hours, kingdom__grace_to_find_a_Queen
from chess_piece.king import return_app_ip
from chess_piece.app_hive import set_streamlit_page_config_once, account_header_grid
import streamlit as st
import pytz
from datetime import datetime

est = pytz.timezone("US/Eastern")

def demo_bot():
    client_user = 'stefanstapinski@gmail.com'
    prod = False
    KING = kingdom__grace_to_find_a_Queen()

    st.session_state['sneak_peak'] = True
    st.info("Welcome, feel free to place trades, every trade is handled and management by the AI using TimeSeries Weighted Averages...TimeValueMoney")
    st.session_state['sneak_peak'] = False

    st.session_state["ip_address"] = return_app_ip()
    st.session_state["username"] = client_user
    st.session_state['db_root'] = 'db__stefanstapinski_11854791'
    st.session_state['prod'] = False
    

    qb = init_queenbee(client_user=client_user, prod=prod, 
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
    refresh_sec = 8 if seconds_to_market_close > 0 and mkhrs == 'open' else 63000
    account_header_grid(client_user, prod, refresh_sec, st.session_state["ip_address"], seconds_to_market_close)
    queens_conscience(revrec, KING, QUEEN_KING, api, sneak_peak=True)
if __name__ == '__main__':
    set_streamlit_page_config_once()
    demo_bot()