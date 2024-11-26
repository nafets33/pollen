import pandas as pd
import logging
import os
import pandas as pd
from datetime import datetime, timedelta, date
import pytz
import subprocess
import sys

from PIL import Image
from dotenv import load_dotenv
import os
import requests

import streamlit as st
from pq_auth import signin_main
import time
import argparse
import json

# main chess piece
from chess_piece.workerbees import queen_workerbees
from chess_piece.king import return_db_root, return_all_client_users__db, master_swarm_QUEENBEE, hive_master_root, print_line_of_error, ReadPickleData, read_QUEENs__pollenstory
from chess_piece.queen_hive import init_qcp_workerbees, init_queenbee, init_swarm_dbs
from chess_piece.app_hive import trigger_py_script, standard_AGgrid
# componenets
from streamlit_extras.switch_page_button import switch_page
from streamlit_extras.stoggle import stoggle
import hydralit_components as hc
from custom_button import cust_Button
from custom_text import custom_text, TextOptionsBuilder

from chess_piece.pollen_db import PollenDatabase, PollenJsonEncoder, PollenJsonDecoder
from chess_utils.postgres_utils import create_pg_table


import ipdb


pd.options.mode.chained_assignment = None
est = pytz.timezone("US/Eastern")

if 'authorized_user' not in st.session_state:
    signin_main("workerbees")

if st.session_state["authorized_user"] != True:
    st.error("you do not have permissions young fellow")
    st.stop()

client_user = st.session_state['username']
prod = st.session_state['prod']
st.warning(f'Production{prod}')


db=init_swarm_dbs(prod)

def find_all_circular_references(obj, seen=None, path="root", found_refs=None):
    if seen is None:
        seen = set()
    if found_refs is None:
        found_refs = []

    # Check if the object ID has already been encountered
    if id(obj) in seen:
        circular_ref_path = f"Circular reference detected at: {path}"
        print(circular_ref_path)
        found_refs.append(circular_ref_path)
        return found_refs

    # Add the current object ID to the seen set
    seen.add(id(obj))

    # Recursively check for circular references in dictionaries and lists
    if isinstance(obj, dict):
        for key, value in obj.items():
            find_all_circular_references(value, seen.copy(), path=f"{path} -> {key}", found_refs=found_refs)
    elif isinstance(obj, list):
        for index, item in enumerate(obj):
            find_all_circular_references(item, seen.copy(), path=f"{path} -> [{index}]", found_refs=found_refs)

    # Return the list of all found circular references
    return found_refs

if __name__ == '__main__':
    tables = PollenDatabase.get_all_tables()
    tab_list = ['Tables', 'Create', 'Migrate User', 'Delete'] + tables
    tabs = st.tabs(tab_list)
    if st.session_state['admin']:
        with tabs[3]:
            del_tables = st.selectbox("delete table", options=tables)
            if st.button(f"Delete Table {del_tables}"):
                PollenDatabase.delete_table(del_tables)
            sub_tabs = st.tabs([i for i in tables])
            s_t = 0
            for table in tables:
                with sub_tabs[s_t]:
                    with st.form(f"Del Key Table {table}"):
                        table_keys = PollenDatabase.get_all_keys(table_name=table)
                        del_key = st.selectbox(f"delete key from {table}", options=table_keys, key=table)
                        if st.form_submit_button(f"Delete Key {del_key}"):
                            data = PollenDatabase.retrieve_data(table, key=del_key)
                            PollenDatabase.delete_key(table, key_column=del_key, key_value=data)
                s_t+=1
        s_t = 4
        for table in tables:
            with tabs[s_t]:
                st.write(table)
                # st.write(pd.DataFrame(PollenDatabase.get_all_keys(table)))
                st.write(pd.DataFrame(PollenDatabase.get_all_keys_with_timestamps(table)))
                s_t+=1

        with tabs[1]:
            create_pg_table()
        with tabs[0]: 
            st.write(tables)

            table_name = st.selectbox('table_name', options=tables)
            if st.button(f'add last mod to table: {table_name}'):
                PollenDatabase.update_table_schema(table_name)
            
            if st.button('migrate_db'):
                swarm = init_swarm_dbs(prod)
                for db_name, db_file in swarm.items():
                    data = ReadPickleData(db_file)
                    PollenDatabase.upsert_data(table_name='db', key=db_name, value=data)
                    st.success(f'{db_name} saved')
            
            all_users = return_all_client_users__db()
            st.write(all_users)
            # qb = init_queenbee(client_user, prod, queen_heart=True).get('QUEENsHeart')
            # db_root = return_db_root(client_user, pg_migration=True)
            # key=f'{db_root}QUEENsHeart'
            # value_json = PollenDatabase.retrieve_data(table_name='client_user_store', key=f'{db_root}_QUEENsHeart')
            # st.write(value_json['key'])
            # print("DD", len(value_json))
            # 1073741824
            # 622070226

            
            with tabs[2]:
                c_user = st.selectbox('Client Users', options=all_users['email'].tolist())
                c_user_root = return_db_root(c_user)
                c_user_root_name = os.path.split(c_user_root)[-1]
                st.write(f'{c_user} <> {c_user_root} <> {c_user_root_name}')
                if st.button(f"migrate user {c_user_root_name}"):
                    st.write("hell yea")
                    with st.spinner("Reading Client User DB"):
                        qb = init_queenbee(c_user, prod, queen=True, queen_king=True, orders=True, broker=True, broker_info=True, revrec=True, queen_heart=True) # orders_final=True handle in new table
                    for db_name in qb.keys():
                        data = qb.get(db_name)
                        key_name = f'{c_user_root_name}-{db_name}'
                        st.write(f'Uploading {key_name}')
                        if data:
                            if not find_all_circular_references(data):
                                if PollenDatabase.upsert_data(table_name='client_user_store', key=key_name, value=data):
                                    st.success(f'{key_name} Saved')
                            else:
                                st.error(f"{key_name} C error")

        # qb = init_queenbee(client_user=client_user, prod=prod, queen=True, queen_king=True, pg_migration=True)
        # st.write(qb['QUEEN'].keys())
        # qq = PollenDatabase.retrieve_data(table_name='client_user_store', key='db__stefanstapinski_72704614_QUEEN')
        # st.write(qq.keys())



        # data = init_queenbee(client_user, prod, queen=True,).get('QUEENsHeart')
        # # data.pop('heartbeat')
        # find_all_circular_references(data)