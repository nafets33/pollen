# Whale Wisdom Utils
import os, sys
from dotenv import load_dotenv
load_dotenv()

import json
import time
import hmac
import hashlib
import base64
import requests
import pandas as pd
from tqdm import tqdm
from datetime import datetime

# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from chess_piece.king import hive_master_root_db, PickleData, ReadPickleData
from chess_piece.pollen_db import PollenDatabase

def shape_whalewishdom_holdings(json_data):
    results = json_data['results']
    df_return = pd.DataFrame()
    for fund in results:
        records = fund['records']
        if len(records) != 1:
            print("WTF what Whale are you?")
        
        data = records[0]['holdings']
        df = pd.DataFrame(data)
        df_return = pd.concat([df_return, df])
    
    return df_return


def get_whalewisdom(secret_key, shared_key, args):
    """Simple function to GET WhaleWisdom Data from their API.
    Args:
        secret_key (str) : Your secret API key.
        shared_key (str) : Your shared API key.
        args       (dict): The command to execute.
    Returns:
        dict: Returns a dictionary object containing data retrieved from a successful API call.
    """
    args_str = json.dumps(args)
    curr_time = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    hmac_hash = hmac.new(
        secret_key.encode(), f"{args_str}\n{curr_time}".encode(), hashlib.sha1
    ).digest()
    signature = base64.b64encode(hmac_hash).rstrip()
    response = requests.get(
        url="https://whalewisdom.com/shell/command.json",
        params={
            "args": args_str,
            "api_shared_key": shared_key,
            "api_sig": signature.decode(),
            "timestamp": curr_time,
        },
    )

    return response.json()


def get_whalewisdom_holdings(command='holdings', filer_ids=[34, 89], include_13d=1):

    try:
        args = {
            "command": command,
            "filer_ids": filer_ids,
            "include_13d": include_13d
        }

        json_data = get_whalewisdom(secret_key=os.getenv("whale_wisdom_secret"), 
                        shared_key=os.getenv("whale_wisdom_key"), 
                        args=args)
        df_shaped = shape_whalewishdom_holdings(json_data)

        return df_shaped
    except Exception as e:
        print(f"ERROR in WW Pull {e} {filer_ids}")
        print(json_data)
        return pd.DataFrame()


def get_all_wwisdom_filer_holdings():
    s = datetime.now()
    local_db_root = hive_master_root_db()
    filers = os.path.join(local_db_root, 'whalewisdom_filers.csv')
    df = pd.read_csv(filers)
    df = df.set_index('id', drop=False)
    all_filers = df['id'].tolist()[1245:1246]
    # all_filers = list(range(len(all_filers)))

    chunk_size = 10  # Number of items per batch

    df_return = pd.DataFrame()
    # Iterate through batches
    # for i in tqdm(range(0, len(all_filers), chunk_size)):
        # batch = all_filers[i:i + chunk_size]
        # print(f"Processing batch ({i} to {i + len(batch) - 1}): {batch}")
    for filer in tqdm(all_filers):
        print(df.loc[filer].get('name'))
        df_holdings = get_whalewisdom_holdings(filer_ids=[filer])
        df_return = pd.concat([df_return, df_holdings])
        time.sleep(10)
    
    df_return = df_return.reset_index(drop='index')
    # clean out NA
    df_return = df_return.fillna("DROPME")
    df_return = df_return[~(df_return['filer_name'] == "DROPME")]

    # Save
    data = {'latest_filer_holdings': df_return}
    PollenDatabase.upsert_data(table_name='db_sandbox', key='whalewisdom', value=data)
    PickleData(os.path.join(local_db_root, 'whalewisdom'), data)  

    print("run time mins", (datetime.now() - s).total_seconds() / 60) 

    return True 



