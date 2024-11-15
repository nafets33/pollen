import asyncio
import os
import pickle
import sqlite3
import sys
import time
from datetime import datetime
import streamlit as st
import hashlib
import pandas as pd
import aiohttp
import pytz
import socket
import json
from chess_piece.pollen_db import PollenDatabase
from chess_piece.king import stars, print_line_of_error
from chess_piece.queen_hive import init_KING, init_queen



def init_swarm_dbs(prod, init=True):
    ## SSBEE 
    # ✅ if db table does not exist, create table 
    table_name = 'db'
    PollenDatabase.create_table_if_not_exists(table_name)
    envs = '_Sandbox' if prod == False else ''
    dbs = ['KING', 'QUEEN', 'BISHOP', 'KNIGHT']
    keys = {}
    for db_name in dbs:
        key = f'{db_name}{envs}'
        keys[db_name] = key
        # key = Path(pathname).stem
        if init:
            if PollenDatabase.key_exists(table_name, key) == False:
                print("init db ", db_name)
                if db_name == 'KING':
                    data = init_KING()
                elif db_name == 'QUEEN':
                    data = init_queen('queen')
                else:
                    data = {}
                PollenDatabase.upsert_data(table_name, key, data)
        
    return keys


def read_pollenstore(symbols, read_storybee=True, read_pollenstory=True, info="function uses async"):  # return combined dataframes
    ### updates return ticker db and path to db ###
    def async__read_symbol_data(table_name, keys):  # re-initiate for i timeframe
        async def get_changelog(session, table_name, key):
            async with session:
                try:
                    # print("read", ttf_file_name)
                    # db = ReadPickleData(ttf_file_name)
                    db = PollenDatabase.retrieve_data(table_name, key)
                    if db:
                        ttf = key.replace("POLLEN_STORY_", "").replace("STORY_BEE_", "") #os.path.basename(ttf_file_name).split(".pkl")[0]
                        return {"ttf_file_name": key, "ttf": ttf, "db": db}
                    else:
                        return {"ttf_file_name": key, "error": "Data Missing"}
                except Exception as e:
                    return {"ttf_file_name": key, "error": e}

        async def main(keys):
            async with aiohttp.ClientSession() as session:
                return_list = []
                tasks = []
                for key in keys:  # castle: [spy], bishop: [goog], knight: [META] ..... pawn1: [xmy, skx], pawn2: [....]
                    tasks.append(
                        asyncio.ensure_future(get_changelog(session, table_name, key))
                    )
                original_pokemon = await asyncio.gather(*tasks)
                for pokemon in original_pokemon:
                    return_list.append(pokemon)

                return return_list

        list_of_status = asyncio.run(main(keys))
        return list_of_status

    try:

        # main_dir = workerbee_dbs_root()
        # main_story_dir = workerbee_dbs_root__STORY_bee()
        table_name = os.environ.get('POLLEN_TABLE_name')

        # Final Return
        pollenstory = {}
        STORY_bee = {}
        errors = {}

        # pollen story // # story bee
        ps_all_files_names = []
        sb_all_files_names = []
        for symbol in set(symbols):
            if read_pollenstory:
                for star in stars().keys():
                    # file = os.path.join(main_dir, f'{symbol}_{star}.pkl')
                    file = f'POLLEN_STORY_{symbol}_{star}'
                    if PollenDatabase.key_exists(table_name, file) == False:
                        print("DB does not exist", file)
                        pass
                    else:
                        ps_all_files_names.append(file)
            
            if read_storybee:
                for star in stars().keys():
                    # file = os.path.join(main_story_dir, f'{symbol}_{star}.pkl')
                    file = f'STORY_BEE_{symbol}_{star}'
                    if PollenDatabase.key_exists(table_name, file) == False:
                        print("DB does not exist", file)
                        pass
                    else:
                        sb_all_files_names.append(file)

        # async read data
        if read_pollenstory:
            pollenstory_data = async__read_symbol_data(table_name, ps_all_files_names)
            # put into dictionary
            for package_ in pollenstory_data:
                if "error" not in package_.keys():
                    pollenstory[package_["ttf"]] = package_["db"]["pollen_story"]
                else:
                    errors[package_["ttf"]] = package_["error"]
        if read_storybee:
            storybee_data = async__read_symbol_data(table_name, sb_all_files_names)
            for package_ in storybee_data:
                if "error" not in package_.keys():
                    STORY_bee[package_["ttf"]] = package_["db"]["STORY_bee"]
                else:
                    errors[package_["ttf"]] = package_["error"]

        return {"pollenstory": pollenstory, "STORY_bee": STORY_bee, "errors": errors}
    except Exception as e:
        print_line_of_error("king return symbols failed")


def create_pg_table():
    table_name = st.text_input('Table Name', 'db_store')
    if st.button("Create Pollen Store"):
        PollenDatabase.create_table_if_not_exists(table_name)
        st.success(f"{table_name} created")