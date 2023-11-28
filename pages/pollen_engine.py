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
    
    with st.expander('queen logs'):
        logs = os.listdir(log_dir)
        logs = [i for i in logs if i.endswith(".log")]
        log_file = st.selectbox('log files', list(logs))
        with open(os.path.join(log_dir, log_file), 'r') as f:
            content = f.readlines()
            st.write(content)
    
    return True