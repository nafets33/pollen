from chess_piece.king import ReadPickleData, hive_master_root
from chess_piece.queen_hive import init_queenbee, refresh_account_info
import sqlite3
import os
import streamlit as st
import pandas as pd

def pollen_engine(acct_info):
    
    with st.expander("alpaca account info"):
        st.write(acct_info)

    with st.expander('betty_bee'):
        betty_bee = ReadPickleData(os.path.join(os.path.join(hive_master_root(), 'db'), 'betty_bee.pkl'))
        df_betty = pd.DataFrame(betty_bee)
        df_betty = df_betty.astype(str)
        st.write(df_betty)
    
    if st.session_state['admin']:
        with st.expander('users db'):
            con = sqlite3.connect("db/client_users.db")
            cur = con.cursor()
            users = cur.execute("SELECT * FROM users").fetchall()
            st.dataframe(pd.DataFrame(users))

    with st.expander('charlie_bee'):

        charlie_bee = ReadPickleData(os.path.join(st.session_state['db_root'], 'charlie_bee.pkl'))
        df_charlie = pd.DataFrame(charlie_bee)
        df_charlie = df_charlie.astype(str)
        st.write(df_charlie)
    
    df = pd.DataFrame(charlie_bee['queen_cyle_times']['beat_times'])
    st.line_chart(df)

    
    return True

if __name__ == '__main__':
    qb = init_queenbee(client_user='stefanstapinski@gmail.com', prod=True, api=True)
    # QUEEN = qb.get('QUEEN')
    QUEEN_KING = qb.get('QUEEN_KING')
    api = qb.get('api')
    alpaca_acct_info = refresh_account_info(api=api)
    acct_info = alpaca_acct_info.get('info_converted')
    acct_info_raw = alpaca_acct_info.get('info')
    pollen_engine(acct_info_raw)