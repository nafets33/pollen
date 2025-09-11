# LiveBot
import pandas as pd
from pages.conscience import queens_conscience
from chess_piece.queen_hive import init_queenbee, hive_dates, return_market_hours, kingdom__grace_to_find_a_Queen, create_QueenOrderBee, kingdom__global_vars, pollen_themes
from chess_piece.king import return_app_ip
from chess_piece.app_hive import set_streamlit_page_config_once, sac_menu_buttons, mark_down_text
from pages.orders import order_grid, config_orders_cols
from pages.chessboard import chessboard
from pollen import get_portfolio_performance
import streamlit as st
import pytz
from datetime import datetime

est = pytz.timezone("US/Eastern")

def demo_bot():
    pass
    menu_id = sac_menu_buttons("demo")
    cols = st.columns((2, 1, 1, 4))
    with cols[3]:
        with st.expander("Portfolio Performance", expanded=True):
        # Show all portfolio history periods in columns
            periods = ['7D', '1M', '3M', '6M', '1A']
            perf_cols = st.columns(len(periods))
            perf_containers = [col.container() for col in perf_cols]



    client_user = 'stapinskistefan@gmail.com'
    prod = False
    KING = kingdom__grace_to_find_a_Queen()
    st.session_state['sneak_peak'] = True
    st.info("Welcome, This Portoflio is currently being managed by James-CFP, an AI Agentic Trader, FEEL free to utilize the Trading Tool, James will manage all Trades you Place")
    st.session_state['sneak_peak'] = False
    st.session_state["ip_address"] = return_app_ip()
    st.session_state["username"] = client_user
    st.session_state["client_user"] = client_user
    st.session_state['db_root'] = 'db__stapinskistefan_99757341'
    st.session_state['prod'] = False
    st.session_state['authentication_status'] = False
    qb = init_queenbee(client_user=client_user, prod=prod, orders_v2=True, 
                       queen_king=True, api=True, init=True, 
                       revrec=True, 
                       demo=True,
                       main_server=True,)
    QUEEN_KING = qb.get('QUEEN_KING')
    # st.write(QUEEN_KING['chess_board'])
    api = qb.get('api')
    revrec = qb.get('revrec')

    trading_days = hive_dates(api=api)['trading_days']
    # st.write(trading_days) # STORE IN KING and only call once
    mkhrs = return_market_hours(trading_days=trading_days)
    seconds_to_market_close = (datetime.now(est).replace(hour=16, minute=0, second=0) - datetime.now(est)).total_seconds()
    refresh_sec = 8 if seconds_to_market_close > 0 and mkhrs == 'open' else 89
    if menu_id == 'Portfolio Allocations':
        ticker_allowed = KING['alpaca_symbols_df'].index.tolist()
        themes = list(pollen_themes(KING).keys())
        chessboard(revrec=revrec, QUEEN_KING=QUEEN_KING, ticker_allowed=ticker_allowed, themes=themes, admin=False)
        st.stop()
    
    if menu_id == 'Orders':
        # seconds_to_market_close = st.session_state['seconds_to_market_close'] if 'seconds_to_market_close' in st.session_state else 0
        # client_user = st.session_state['client_user']
        ip_address = st.session_state['ip_address']
        queen_orders = pd.DataFrame([create_QueenOrderBee(queen_init=True)])
        king_G = kingdom__global_vars()
        active_order_state_list = king_G.get('active_order_state_list')
        config_cols = config_orders_cols(active_order_state_list)
        missing_cols = [i for i in queen_orders.iloc[-1].index.tolist() if i not in config_cols.keys()]
        order_grid(client_user, config_cols, missing_cols, ip_address)
        st.stop()
    
    portfolio_performance = get_portfolio_performance(api, periods)
    for i, period in enumerate(periods):
        # if i == 0:
        #     with perf_containers[i]:
        #         # mark_down_text('Portfolio', fontsize='23')
        #         cust_Button("misc/dollar-symbol-unscreen.gif", hoverText='Portfolio', key='portfolio_ahe', )
        # else:
        # df = fetch_portfolio_history(api, period=period)
        portfolio_perf = portfolio_performance.get(period)
        if portfolio_perf is not None:
        # if df is not None and not df.empty:
            # portfolio_perf = round((df.iloc[-1]['equity'] - df.iloc[0]['equity']) / df.iloc[0]['equity'] * 100, 2)
            with perf_containers[i]:
                color = "#1d982b" if portfolio_perf > 0 else "#ff4136"
                mark_down_text(f'{period}', fontsize='18', color="#888", align="center")
                mark_down_text(f'{portfolio_perf}%', fontsize='23', color=color, align="center")

    queens_conscience(api, revrec, KING, QUEEN_KING, api, sneak_peak=True, show_acct=True)
if __name__ == '__main__':
    set_streamlit_page_config_once()
    demo_bot()
    # pollenq(sandbox=True, demo=True)