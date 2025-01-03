
import pandas as pd
import os
import numpy as np
from datetime import datetime, timedelta
import pytz
from itertools import islice
from PIL import Image
from dotenv import load_dotenv
import streamlit as st
import os
import time
import hydralit_components as hc

from streamlit_extras.switch_page_button import switch_page

from pq_auth import signin_main
from chess_piece.king import return_QUEEN_KING_symbols, master_swarm_QUEENBEE, local__filepaths_misc, print_line_of_error, ReadPickleData, PickleData, kingdom__grace_to_find_a_Queen, return_QUEENs__symbols_data, kingdom__global_vars
from chess_piece.queen_hive import pollen_themes, init_qcp_workerbees, create_QueenOrderBee, generate_chessboards_trading_models, return_queen_controls, stars, generate_chess_board, refresh_account_info, init_queenbee,setup_chess_board, add_trading_model, set_chess_pieces_symbols, init_qcp, read_swarm_db
from chess_piece.queen_mind import refresh_chess_board__revrec
from custom_button import cust_Button
from custom_grid import st_custom_grid, GridOptionsBuilder
from custom_graph_v1 import st_custom_graph
from chess_piece.pollen_db import PollenDatabase

import ipdb

pg_migration = os.getenv('pg_migration')
print("pg_migration", pg_migration)

def add_new_qcp__to_chessboard(QUEEN_KING, ticker_allowed, themes, qcp_bees_key='chess_board'):
    models = ['MACD', 'story__AI']
    qcp_pieces = QUEEN_KING[qcp_bees_key].keys()
    qcp_name = st.text_input(label='piece name', value=f'pawn_{len(qcp_pieces)}', help="Theme your names to match your strategy")
    if qcp_name in qcp_pieces:
        st.error("Chess Piece Name must be Unique")
        st.stop()

    with st.form('new qcp'):
        qcp_vars = init_qcp()
        cols = st.columns((1,3,2,2,2,2,2,2))
        with cols[0]:
            picture = cust_Button(local__filepaths_misc().get('queen_png'), key=f'{qcp_name}_image')
        with cols[1]:
            qcp_vars['tickers'] = st.multiselect(label=f'symbols', options=ticker_allowed + crypto_symbols__tickers_avail, default=qcp_vars['tickers'], help='Castle Should Hold your Highest Valued Symbols', key=f'{qcp_name}tickers{admin}', label_visibility='hidden')
        with cols[2]:
            qcp_vars['model'] = st.selectbox(label='model', options=models, index=models.index(qcp_vars.get('model')), key=f'{qcp_name}model{admin}')
        with cols[3]:
            qcp_vars['theme'] = st.selectbox(label=f'theme', options=themes, index=themes.index(qcp_vars.get('theme')), help='Trading Star Strategy, You May Customize Trading Models', key=f'{qcp_name}theme{admin}')
        with cols[4]:
            qcp_vars['total_buyng_power_allocation'] = st.slider(label=f'Budget Allocation', min_value=float(0.0), max_value=float(1.0), value=float(qcp_vars['total_buyng_power_allocation']), key=f'{qcp_name}_buying_power_allocation{admin}')
        with cols[5]:
            qcp_vars['total_borrow_power_allocation'] = st.slider(label=f'Margin Allocation', min_value=float(0.0), max_value=float(1.0), value=float(qcp_vars['total_borrow_power_allocation']), key=f'{qcp_name}_borrow_power_allocation{admin}', label_visibility='hidden')
        with cols[6]:
            qcp_vars['margin_power'] = st.slider(label=f'Margin Power', min_value=float(0.0), max_value=float(1.0), value=float(qcp_vars.get('margin_power')), key=f'{qcp_name}_margin_power_{admin}', label_visibility='hidden')
        
        qcp = init_qcp(init_macd_vars={"fast": 12, "slow": 26, "smooth": 9}, 
                        ticker_list=qcp_vars.get('tickers'), 
                        theme=qcp_vars.get('theme'), 
                        model=qcp_vars.get('model'), 
                        piece_name=qcp_name, 
                        buying_power=qcp_vars.get('total_buyng_power_allocation'), 
                        borrow_power=qcp_vars.get('total_borrow_power_allocation'), 
                        picture='queen_png', 
                        margin_power=qcp_vars['margin_power'])
        
        if st.form_submit_button('Add New Piece'):
            QUEEN_KING[qcp_bees_key][qcp.get('piece_name')] = qcp
            QUEEN_KING = handle__new_tickers__AdjustTradingModels(QUEEN_KING=QUEEN_KING)
            PickleData(QUEEN_KING.get('source'), QUEEN_KING)
            st.success("New Piece Added Refresh")
        
        return QUEEN_KING


def reallocate_star_power(QUEEN_KING, trading_model, ticker_option_qc, trading_model_revrec={}, trading_model_revrec_s={}, showguage=False, func_selection=False, formkey='Star__Allocation'):
    try:
        cols = st.columns((1,8))
        if func_selection:
            with cols[0]:
                control_option = 'symbols_stars_TradingModel'
                models_avail = list(QUEEN_KING['king_controls_queen'][control_option].keys())
                ticker_option_qc = st.selectbox("Reallocate Symbol", models_avail, index=models_avail.index(["SPY" if "SPY" in models_avail else models_avail[0]][0]), key=formkey) 
                trading_model = QUEEN_KING['king_controls_queen'][control_option][ticker_option_qc]
        with cols[1]:
            with st.form("Reallocate Star Power"):
                st.header(f"Reallocate {ticker_option_qc}")
                cols = st.columns((1,1,1,1,1,1,1))
                c = 0
                for star, star_vars in trading_model.get('stars_kings_order_rules').items():
                    trading_model_revrec[star] = star_vars.get("buyingpower_allocation_LongTerm")
                    trading_model_revrec_s[star] = star_vars.get("buyingpower_allocation_ShortTerm")
                    with cols[c]:
                        trading_model['stars_kings_order_rules'][star]["buyingpower_allocation_LongTerm"] = st.slider(label=f'L {star}', value=star_vars.get('buyingpower_allocation_LongTerm'), key=f'{star}{"_"}{"buying_power"}')
                        trading_model['stars_kings_order_rules'][star]["buyingpower_allocation_ShortTerm"] = st.slider(label=f'S {star}', value=star_vars.get('buyingpower_allocation_ShortTerm'), key=f'{star}{"_"}{"buying_power_s"}')
                    c+=1
                    # with cols[0]:
                    #     mark_down_text(align='left', text=star)
                
                if st.form_submit_button("Reallocate Star Power"):
                    QUEEN_KING['saved_trading_models'].update(trading_model)
                    PickleData(pickle_file=QUEEN_KING.get('source'), data_to_store=QUEEN_KING)
    except Exception as e:
        print_line_of_error("rev allocation error")


def setup_qcp_on_board(QUEEN_KING, qcp_bees_key, qcp, ticker_allowed, themes, new_piece=False, headers=0):
    def return_active_image(qcp):
        if 'qcp_k' not in st.session_state:
            b_key = 89
            st.session_state['qcp_k'] = 89
        else:
            b_key = st.session_state['qcp_k'] + 1
            st.session_state['qcp_k'] = b_key
        if 'qcp_k' in st.session_state and b_key == st.session_state['qcp_k']:
            b_key+=1
        try:
            with cols[0]:
                if qcp == 'castle':
                    cust_Button(local__filepaths_misc().get('castle_png'), key=f'{b_key} castle')

                else:
                    cust_Button(local__filepaths_misc().get('queen_png'), key=f'{b_key}')
                #     # hc.option_bar(option_definition=pq_buttons.get('castle_option_data'),title='', key='castle_qcp', horizontal_orientation=False)
                # elif qcp == 'bishop':
                #     st.write(qcp)
                #     # hc.option_bar(option_definition=pq_buttons.get('bishop_option_data'),title='', key='bishop_qcp', horizontal_orientation=False)                                
                # elif qcp == 'knight':
                #     st.write(qcp)
                #     # hc.option_bar(option_definition=pq_buttons.get('knight_option_data'),title='', key='knight_qcp', horizontal_orientation=False)                                
                # elif qcp == 'castle_coin':
                #     st.write(qcp)
                #     # hc.option_bar(option_definition=pq_buttons.get('coin_option_data'),title='', key='coin_qcp', horizontal_orientation=False)                                
                # else:
                #     st.write(qcp)
                #     # st.image(MISC.get('knight_png'), width=74)
                # cust_Button(os.path.join(hive_master_root(), 'misc/dollar_symbol.gif'), height='38px')

            return True
        except Exception as e:
            print(e)
            print_line_of_error()

    models = ['MACD', 'story__AI']
                
    try:
        cols = st.columns((1,1,4,1,1,2,2,2))
        if headers == 0:
            # Headers
            c=0
            chess_board_names = list(QUEEN_KING[qcp_bees_key]['castle'].keys())
            chess_board_names = ["pq", "Name", 'symbols', 'Model', 'Theme', 'Budget Allocation', 'Margin Allocation', 'Margin Power']
            for qcpvar in chess_board_names:
                try:
                    with cols[c]:
                        st.write(f'{qcpvar}')
                        c+=1
                except Exception as e:
                    print(qcpvar, e)

        # return_active_image(qcp)
        with st.container():
            cols = st.columns((1,1,4,1,1,2,2,2))
            with cols[0]:
                cust_Button(local__filepaths_misc().get('castle_png'), key=f'{qcp}')
            # chess board vars
            with cols[1]:
                QUEEN_KING[qcp_bees_key][qcp]['piece_name'] = st.text_input("Name", value=QUEEN_KING[qcp_bees_key][qcp]['piece_name'], key=f'{qcp}piece_name{admin}', label_visibility='hidden')
            with cols[2]:
                QUEEN_KING[qcp_bees_key][qcp]['tickers'] = st.multiselect(label=qcp, options=ticker_allowed + crypto_symbols__tickers_avail, default=QUEEN_KING[qcp_bees_key][qcp]['tickers'], help='Castle Should Hold your Highest Valued Symbols', key=f'{qcp}tickers{admin}',  label_visibility='hidden')
            with cols[3]:
                QUEEN_KING[qcp_bees_key][qcp]['model'] = st.selectbox(label='-', options=models, index=models.index(QUEEN_KING[qcp_bees_key][qcp].get('model')), key=f'{qcp}model{admin}')
            with cols[4]:
                QUEEN_KING[qcp_bees_key][qcp]['theme'] = st.selectbox(label=f'-', options=themes, index=themes.index(QUEEN_KING[qcp_bees_key][qcp].get('theme')), help='Trading Star Strategy, You May Customize Trading Models', key=f'{qcp}theme{admin}')
            with cols[5]:
                QUEEN_KING[qcp_bees_key][qcp]['total_buyng_power_allocation'] = st.slider(label=f'Budget Allocation', min_value=float(0.0), max_value=float(1.0), value=float(QUEEN_KING[qcp_bees_key][qcp]['total_buyng_power_allocation']), key=f'{qcp}_buying_power_allocation{admin}', label_visibility='hidden')
            with cols[6]:
                QUEEN_KING[qcp_bees_key][qcp]['total_borrow_power_allocation'] = st.slider(label=f'Margin Allocation', min_value=float(0.0), max_value=float(1.0), value=float(QUEEN_KING[qcp_bees_key][qcp]['total_borrow_power_allocation']), key=f'{qcp}_borrow_power_allocation{admin}', label_visibility='hidden')
            with cols[7]:
                QUEEN_KING[qcp_bees_key][qcp]['margin_power'] = st.slider(label=f'Margin Power', min_value=float(0.0), max_value=float(1.0), value=float(QUEEN_KING[qcp_bees_key][qcp]['margin_power']), key=f'{qcp}margin_power{admin}', label_visibility='hidden')

        return QUEEN_KING
    
    except Exception as e:
        er_line=print_line_of_error("chess board")
        st.write(f'{qcp_bees_key} {qcp} failed {er_line}')


def handle__new_tickers__AdjustTradingModels(QUEEN_KING, qcp_bees_key='chess_board', reset_theme=False):
    # add new trading models if needed
    # Castle 
    trading_models = QUEEN_KING['king_controls_queen']['symbols_stars_TradingModel']
    for qcp, bees_data in QUEEN_KING[qcp_bees_key].items():
        tickers = bees_data.get('tickers')
        if tickers:
            for ticker in tickers:
                try:
                    if reset_theme:
                        QUEEN_KING = add_trading_model(status='active', QUEEN_KING=QUEEN_KING, ticker=ticker, model=bees_data.get('model'), theme=bees_data.get('theme'))
                    else:
                        if ticker not in trading_models.keys():
                            QUEEN_KING = add_trading_model(status='active', QUEEN_KING=QUEEN_KING, ticker=ticker, model=bees_data.get('model'), theme=bees_data.get('theme'))
                except Exception as e:
                    print('wtferr', e)
    return QUEEN_KING


def refresh_chess_board__button(QUEEN_KING):
    refresh = st.button("Reset Chess Board",  use_container_width=True)

    if refresh:
        QUEEN_KING['chess_board'] = generate_chess_board()
        PickleData(pickle_file=st.session_state['PB_App_Pickle'], data_to_store=QUEEN_KING)
        st.success("Generated Default Chess Board")
        time.sleep(1)
        st.rerun()
            
    return True

def refresh_queen_controls_button(QUEEN_KING):
    refresh = st.button("Reset ALL QUEEN controls", use_container_width=True)

    if refresh:
        QUEEN_KING['king_controls_queen'] = return_queen_controls()
        
        PickleData(pickle_file=st.session_state['PB_App_Pickle'], data_to_store=QUEEN_KING)
        st.success("All Queen Controls Reset")
        st.rerun()
            
    return True

def refresh_trading_models_button(QUEEN_KING):
    refresh = st.button("Reset All Trading Models", use_container_width=True)

    if refresh:
        chessboard = QUEEN_KING['chess_board']
        tradingmodels = generate_chessboards_trading_models(chessboard)
        QUEEN_KING['king_controls_queen']['symbols_stars_TradingModel'] = tradingmodels
        
        PickleData(pickle_file=st.session_state['PB_App_Pickle'], data_to_store=QUEEN_KING)
        st.success("All Queen.TradingModels Reset")
        st.experimental_rerun()
            
    return True

def refresh_queen_orders(QUEEN):
    refresh = st.button("Reset All Queen Orders", use_container_width=True)

    if refresh:
        QUEEN['queen_orders'] = pd.DataFrame([create_QueenOrderBee(queen_init=True)]).set_index("client_order_id")
        PickleData(pickle_file=st.session_state['PB_QUEEN_Pickle'], data_to_store=QUEEN)
        st.success("Orders Reset")
        st.experimental_rerun()

def stash_queen(QUEEN):
    refresh = st.button("Stash All Queen Orders", use_container_width=True)

    if refresh:
        queen_logs = os.path.join(st.session_state['db_root'], '/logs/logs/queens')
        queen_log_filename = len(os.listdir(queen_logs))
        queen_log_filename = f'{len(os.listdir(queen_logs)) + 1}_queen.pkl'
        queen_logs = os.path.join(st.session_state['db_root'], queen_log_filename)
        PickleData(pickle_file=st.session_state['PB_App_Pickle'], data_to_store=QUEEN)
        st.success("Queen Stashed")


def chessboard(revrec, QUEEN_KING, ticker_allowed, themes, admin=False, qcp_bees_key = 'chess_board'):
    try:

        if st.toggle("Control Settings"):
            with st.expander("control buttons"):
                refresh_chess_board__button(QUEEN_KING)
                refresh_queen_controls_button(QUEEN_KING)
                refresh_trading_models_button(QUEEN_KING)
                refresh_queen_orders(QUEEN)
                stash_queen(QUEEN)
        all_portfolios = ['Queen', 'King', 'Bishop', "Warren Buffet"]

        optoins = []
        for op in all_portfolios:
            icon = "fas fa-chess-pawn"
            optoins.append({'id': op, 'icon': "fas fa-chess-pawn", 'label':op})
        
        chessboard_selection = hc.option_bar(option_definition=optoins,title='Source', key='chessboard_selections', horizontal_orientation=True) #,override_theme=over_theme,font_styling=font_fmt,horizontal_orientation=True)
        if chessboard_selection == 'Queen':
            pass
        elif chessboard_selection == 'Bishop':
            # WORKERBEE GET
            if pg_migration:
                QUEENBEE = read_swarm_db(prod, 'QUEEN')
                BISHOP = read_swarm_db(prod, 'BISHOP')
                df = BISHOP.get('screen_1')
                for sector in set(df['sector']):
                    token = df[df['sector']==sector]
                    tickers=token['symbol'].tolist()
                    QUEENBEE[qcp_bees_key][sector] = init_qcp_workerbees(ticker_list=tickers)
                
                symbols = return_QUEEN_KING_symbols(QUEEN_KING, QUEENBEE)
                STORY_bee = PollenDatabase.retrieve_all_story_bee_data(symbols=symbols)
            else:
                QUEENBEE = setup_chess_board(QUEEN=QUEENBEE)
                STORY_bee = return_QUEENs__symbols_data(QUEEN=QUEEN, QUEEN_KING=QUEEN_KING, swarmQueen=False, read_pollenstory=False).get('STORY_bee')
            
            QUEEN_KING['chess_board'] = QUEENBEE['workerbees']
            revrec = refresh_chess_board__revrec(acct_info, QUEEN, QUEEN_KING, STORY_bee, active_queen_order_states) ## Setup Board
            QUEEN_KING['revrec'] = revrec

        # current_setup = copy.deepcopy(QUEEN_KING['chess_board'])

        chess_pieces = set_chess_pieces_symbols(QUEEN_KING=QUEEN_KING, qcp_bees_key=qcp_bees_key)
        view = chess_pieces.get('view')
        all_workers = chess_pieces.get('all_workers')
        qcp_ticker_index = chess_pieces.get('ticker_qcp_index')
        current_tickers = qcp_ticker_index.keys()

        
        ### AUTO PILOT CONTRROLS

        # def AutoPilot(revrec, QUEEN_KING):

        def align_autopilot_with_revrec(revrec, QUEEN_KING):
            current_index = QUEEN_KING['king_controls_queen']['ticker_autopilot'].index
            for symbol in revrec.get('storygauge').index:
                if symbol not in current_index:
                    QUEEN_KING['king_controls_queen']['ticker_autopilot'].loc[symbol] = pd.Series([False, False], index=['buy_autopilot', 'sell_autopilot'])

            return QUEEN_KING
        
        if st.button("align auto_pilot"):
            QUEEN_KING =  align_autopilot_with_revrec(revrec, QUEEN_KING)
            if pg_migration:
                PollenDatabase.upsert_data(table_name, QUEEN_KING.get('key'), QUEEN_KING)
            else:
                PickleData(QUEEN_KING.get('source'), QUEEN_KING)
        
        def switch_autopilot_on_off(QUEEN_KING, x_autopilot='buy_autopilot', onoff=True):
            for indx in QUEEN_KING['king_controls_queen']['ticker_autopilot'].index:
                QUEEN_KING['king_controls_queen']['ticker_autopilot'].at[indx, x_autopilot] = onoff
            return QUEEN_KING


        buy_autopilot = st.checkbox("Switch buy auto pilot", False)
        if st.button("Turn Auto Pilot ON for buys"):
            QUEEN_KING = switch_autopilot_on_off(QUEEN_KING, x_autopilot='buy_autopilot', onoff=buy_autopilot)
            st.write(QUEEN_KING['king_controls_queen']['ticker_autopilot'])
            if pg_migration:
                PollenDatabase.upsert_data(table_name, QUEEN_KING.get('key'), QUEEN_KING)
            else:
                PickleData(QUEEN_KING.get('source'), QUEEN_KING)

        sell_autopilot = st.checkbox("Switch sell auto pilot", False)
        if st.button("Turn Auto Pilot OFF for buys"):
            QUEEN_KING = switch_autopilot_on_off(QUEEN_KING, x_autopilot='sell_autopilot', onoff=sell_autopilot)
            st.write(QUEEN_KING['king_controls_queen']['ticker_autopilot'])
            if pg_migration:
                PollenDatabase.upsert_data(table_name, QUEEN_KING.get('key'), QUEEN_KING)
            else:
                PickleData(QUEEN_KING.get('source'), QUEEN_KING)

        ### AUTO PILOT CONTRROLS

        # if st.sidebar.toggle("autopilot funcs"):
        #     AutoPilot(revrec, QUEEN_KING)
        # with st.expander(name, True): # ChessBoard
        cb_tab_list = ['Board', 'Star Allocation']
        tabs = st.tabs(cb_tab_list)
        with tabs[0]:
            with st.form(f'ChessBoard_form{admin}'):
                try:

                    headers = 0
                    for qcp in all_workers:
                        QUEEN_KING=setup_qcp_on_board(QUEEN_KING, qcp_bees_key, qcp, ticker_allowed=ticker_allowed, themes=themes, headers=headers)
                        headers+=1
                    
                    # RevRec
                    # print('RevRec')
                    QUEEN_KING['revrec'] = revrec
                    QUEEN_KING['chess_board__revrec'] = revrec
                        
                    cols = st.columns(2)
                    with cols[0]:
                        if st.form_submit_button('Save Board', use_container_width=True):
                            if authorized_user == False:
                                st.warning("You Need your Queen First! Please contact pollenq.queen@gmail.com")
                                return False
                            
                            QUEEN_KING = handle__new_tickers__AdjustTradingModels(QUEEN_KING=QUEEN_KING)
                            PickleData(pickle_file=QUEEN_KING.get('source'), data_to_store=QUEEN_KING)
                            st.success("New Move Saved")
                    with cols[1]:
                        if st.form_submit_button('Reset ChessBoards Trading Models With Theme', use_container_width=True):
                            if authorized_user == False:
                                st.warning("You Need your Queen First! Please contact pollenq.queen@gmail.com")
                                return False

                            QUEEN_KING = handle__new_tickers__AdjustTradingModels(QUEEN_KING, reset_theme=True)
                            PickleData(pickle_file=QUEEN_KING.get('source'), data_to_store=QUEEN_KING)
                            st.success("All Trading Models Reset to Theme")

                except Exception as e:
                    print_line_of_error()

                
            # st.write("# Reallocation")
            with tabs[1]:
                reallocate_star_power(QUEEN_KING, trading_model=False, ticker_option_qc=False, trading_model_revrec={}, trading_model_revrec_s={}, showguage=False, func_selection=True, formkey="Reallocate_Star")


        with st.expander("New Chess Piece"):
            QUEEN_KING = add_new_qcp__to_chessboard(QUEEN_KING=QUEEN_KING, ticker_allowed=ticker_allowed, themes=themes, qcp_bees_key='chess_board')


    except Exception as e:
        print('chessboard ', e, print_line_of_error())


## WORKERBEE : func to select portfolio and have board allocate
# return current board, if None Setup with SPY
# update board

if __name__ == '__main__':

    signin_main()

    if st.button("Return home"):
        switch_page("pollen")

    client_user = st.session_state['client_user']
    authorized_user = st.session_state['authorized_user']
    if authorized_user != True:
        switch_page('pollen')


    king_G = kingdom__global_vars()
    active_order_state_list = king_G.get('active_order_state_list') # = ['running', 'running_close', 'submitted', 'error', 'pending', 'completed', 'completed_alpaca', 'running_open', 'archived_bee']
    active_queen_order_states = king_G.get('active_queen_order_states')

    crypto_symbols__tickers_avail = ['BTCUSD', 'ETHUSD']
    admin = st.session_state['admin']
    prod = st.session_state['prod']
    table_name = 'client_user_store' if prod else 'client_user_store_sandbox'



    reset_theme = False

    KING, users_allowed_queen_email, users_allowed_queen_emailname__db = kingdom__grace_to_find_a_Queen()
    qb = init_queenbee(client_user=client_user, prod=prod, queen=True, queen_king=True, api=True, init=True, pg_migration=pg_migration)
    QUEEN = qb.get('QUEEN')
    QUEEN_KING = qb.get('QUEEN_KING')
    api = qb.get('api')    
    revrec = QUEEN.get('revrec')

    alpaca_acct_info = refresh_account_info(api=api)
    with st.sidebar:
        if st.button('acct info'):
            st.write(alpaca_acct_info)

    acct_info = alpaca_acct_info.get('info_converted')

    if pg_migration:
        QUEENBEE = read_swarm_db(prod, 'QUEEN')
    else:
        QUEENBEE = ReadPickleData(master_swarm_QUEENBEE(prod))

    swarm_queen_symbols = []
    for qcp, va in QUEENBEE['workerbees'].items():
        tickers = va.get('tickers')
        if tickers:
            for tic in tickers:
                swarm_queen_symbols.append(tic)

    themes = list(pollen_themes(KING).keys())
    chessboard(revrec=revrec, QUEEN_KING=QUEEN_KING, ticker_allowed=swarm_queen_symbols, themes=themes, admin=False)