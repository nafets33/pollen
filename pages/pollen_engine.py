from chess_piece.king import ReadPickleData, hive_master_root
import sqlite3
import os
import streamlit as st
import pandas as pd

def pollen_engine(acct_info, log_dir):
    
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

        queens_charlie_bee = ReadPickleData(os.path.join(st.session_state['db_root'], 'charlie_bee.pkl'))
        df_charlie = pd.DataFrame(queens_charlie_bee)
        df_charlie = df_charlie.astype(str)
        st.write(df_charlie)
    

    
    return True