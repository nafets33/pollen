import asyncio
import os
import pickle
import sqlite3
import sys
import time
from datetime import datetime
import streamlit as st
import hashlib
import shutil
import hydralit_components as hc
import pandas as pd
import aiohttp
import pytz
import socket
import json


# HTTPSConnectionPool(host='api.alpaca.markets', port=443): Read timed out. (read timeout=None)
# <class 'requests.exceptions.ReadTimeout'> 2409
# {'type': 'ProgramCrash', 'errbuz': ReadTimeout(ReadTimeoutError("HTTPSConnectionPool(host='api.alpaca.markets', port=443): Read timed out. (read timeout=None)")), 'er': <class 'requests.exceptions.ReadTimeout'>, 'lineerror': 2409}


est = pytz.timezone("US/Eastern")
utc = pytz.timezone('UTC')


def get_ip_address():
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    return ip_address

def return_app_ip(streamlit_ip="http://localhost:8501", ip_address="http://127.0.0.1:8000", ss_state=True):
    machine_ip = get_ip_address()
    if machine_ip == os.environ.get('gcp_ip'):
        # print("IP", ip_address, os.environ.get('gcp_ip'))
        ip_address = "https://api.quantqueen.com"

    if ss_state:
        st.session_state['ip_address'] = ip_address
        st.session_state['streamlit_ip'] = streamlit_ip

    return ip_address

def return_timestamp_string(format="%Y-%m-%d %H-%M-%S %p {}".format(est), tz=est):
    return datetime.now(tz).strftime(format)

def kingdom__global_vars():
    # ###### GLOBAL # ######
    return {
    'ARCHIVE_queenorder': ["final", "archived"],
    'active_order_state_list': [
        "running",
        "running_close",
        "submitted",
        "error",
        "pending",
        "completed",
        "completed_alpaca",
        "running_open",
        "archived_bee",
        "final",
    ],
    'active_queen_order_states': [
        "submitted",
        "accetped",
        "pending",
        "running",
        "running_close",
        "running_open",
    ],
    'status_q_states': [
        'pending',
        'filled',
    ],
    'CLOSED_queenorders': ["running_close", "completed", "completed_alpaca"],
    'RUNNING_Orders': ["running", "running_open"],
    'RUNNING_CLOSE_Orders': ["running_close"],
    'RUNNING_OPEN': ['running_open'],
    # crypto
    'crypto_currency_symbols': ["BTCUSD", "ETHUSD", "BTC/USD", "ETH/USD"],
    'coin_exchange': "CBSE",

    # misc
    'exclude_conditions': [
        "B",
        "W",
        "4",
        "7",
        "9",
        "C",
        "G",
        "H",
        "I",
        "M",
        "N",
        "P",
        "Q",
        "R",
        "T",
        "V",
        "Z",
    ],  # 'U'

    }



def hive_master_root(info='\pollen\pollen'):
    script_path = os.path.abspath(__file__)
    return os.path.dirname(os.path.dirname(script_path)) # \pollen\pollen

# def pollenmain_root():
#     return os.path.dirname(hive_master_root()) # \pollen

def master_swarm_QUEENBEE(prod=True):
    if prod:
        PB_QUEENBEE_Pickle = os.path.join(os.path.join(hive_master_root(), "db"), "queen.pkl") # pollen/db
    else:
        PB_QUEENBEE_Pickle = os.path.join(os.path.join(hive_master_root(), "db"), "queen_sandbox.pkl")
    
    return PB_QUEENBEE_Pickle

def stefan_home_queen_king(prod=False):
    if prod:
        PB_QUEEN_Pickle = os.path.join(os.path.join(hive_master_root(), "client_user_dbs/db__stefanstapinski_11854791"), "queen.pkl") # pollen/db
    else:
        PB_QUEEN_Pickle = os.path.join(os.path.join(hive_master_root(), "client_user_dbs/db__stefanstapinski_11854791"), "queen_sandbox.pkl")
    QUEEN = ReadPickleData(PB_QUEEN_Pickle)
    QUEEN['source'] = PB_QUEEN_Pickle

    if prod:
        pkl_file = os.path.join(os.path.join(hive_master_root(), "client_user_dbs/db__stefanstapinski_11854791"), "queen_App_.pkl") # pollen/db
    else:
        pkl_file = os.path.join(os.path.join(hive_master_root(), "client_user_dbs/db__stefanstapinski_11854791"), "queen_App__sandbox.pkl")
    QUEEN_KING = ReadPickleData(pkl_file)
    QUEEN_KING['source'] = pkl_file

    return QUEEN, QUEEN_KING

def master_swarm_KING(prod):
    if prod:
        PB_KING_Pickle = os.path.join(hive_master_root(), "db/KING.pkl")
    else:
        PB_KING_Pickle = os.path.join(hive_master_root(), "db/KING_sandbox.pkl")

    return PB_KING_Pickle

def client_dbs_root():
    client_dbs = os.path.join(hive_master_root(), "client_user_dbs")
    return client_dbs


def workerbee_dbs_root():
    symbols_pollenstory_dbs = os.path.join(hive_master_root(), "symbols_pollenstory_dbs")
    return symbols_pollenstory_dbs


def workerbee_dbs_root__STORY_bee():
    symbols_pollenstory_dbs = os.path.join(hive_master_root(), "symbols_STORY_bee_dbs")
    return symbols_pollenstory_dbs


def init_symbol_dbs__pollenstory():
    symbol_dbs = os.path.join(hive_master_root(), "symbols_pollenstory_dbs")

    if os.path.exists(symbol_dbs) == False:
        print("Init symbols_dbs")
        os.mkdir(symbol_dbs)

    return symbol_dbs


def workerbee_dbs_backtesting_root():
    symbols_pollenstory_dbs_backtesting = os.path.join(os.path.dirname(hive_master_root()), "symbols_pollenstory_dbs_backtesting")
    if os.path.exists(symbols_pollenstory_dbs_backtesting) == False:
        os.mkdir(symbols_pollenstory_dbs_backtesting)
    return symbols_pollenstory_dbs_backtesting


def workerbee_dbs_backtesting_root__STORY_bee():
    symbols_pollenstory_dbs_backtesting = os.path.join(os.path.dirname(hive_master_root()), "symbols_STORY_bee_dbs_backtesting")
    if os.path.exists(symbols_pollenstory_dbs_backtesting) == False:
        os.mkdir(symbols_pollenstory_dbs_backtesting)
    return symbols_pollenstory_dbs_backtesting

def return_list_of_all__Queens__pkl():
    queen_files = []
    client_dbs = client_dbs_root()
    for db__client_users in os.listdir(client_dbs_root()):
        for files_ in os.listdir(os.path.join(client_dbs, db__client_users)):
            if files_ == "queen.pkl" or files_ == "queen_sandbox.pkl":
                queen_files.append(
                    os.path.join(client_dbs, os.path.join(db__client_users, files_))
                )

    return queen_files


def return_list_of_all__QueenKing__pkl():
    queen_files = []
    client_dbs = client_dbs_root()
    for db__client_users in os.listdir(client_dbs_root()):
        for files_ in os.listdir(os.path.join(client_dbs, db__client_users)):
            if files_ == "queen_App_.pkl" or files_ == "queen_App__sandbox.pkl":
                queen_files.append(
                    os.path.join(client_dbs, os.path.join(db__client_users, files_))
                )

    return queen_files


def hash_string(string):
    # Hash the string
    hashed_string = hashlib.sha256(string.encode()).hexdigest()
    # Convert the hash to an integer ID
    id = int(hashed_string, 16) % (10 ** 8)
    return id

def return_db_root(client_username):
    client_user_pqid = hash_string(client_username)
    client_user = client_username.split("@")[0]
    db_name = f'db__{client_user}_{client_user_pqid}'
    db_root = os.path.join(client_dbs_root(), db_name)

    return db_root

def return_all_client_users__db(query="SELECT * FROM users"):
    con = sqlite3.connect(os.path.join(hive_master_root(), "db/client_users.db"))
    cur = con.cursor()
    users = cur.execute(query).fetchall()
    df = pd.DataFrame(users)

    df = df.rename(columns={
                    0:'email',
                    1:'password',
                    2:'name',
                    3:'phone_no',
                    4:'signup_date',
                    5:'last_login_date',
                    6:'login_count',
                    }
                )

    return df



def kingdom__grace_to_find_a_Queen(prod=True):
    # create list for userdb
    PB_KING_Pickle = master_swarm_KING(prod)
    KING = ReadPickleData(master_swarm_KING(prod))
    users_allowed_queen_email = KING['users'].get('client_user__allowed_queen_list')
    users_allowed_queen_email.append("stefanstapinski@gmail.com")
    users_allowed_queen_email.append("stefanstapinski@yahoo.com")
    users_allowed_queen_email.append("sven0227@gmail.com")
    users_allowed_queen_email.append("nitinrohan17@gmail.com")
    users_allowed_queen_email.append("m.kobzar19@gmail.com")

    users_allowed_queen_emailname__db = {clientusername: return_db_root(client_username=clientusername) for clientusername in users_allowed_queen_email}
    KING['users_allowed_queen_emailname__db'] = users_allowed_queen_emailname__db
    KING['source'] = PB_KING_Pickle
    
    return (
        KING,
        users_allowed_queen_email,
        users_allowed_queen_emailname__db,
    )


def read_QUEEN(queen_db, qcp_s=["castle", "bishop", "knight"]):
    # queen_db = os.path.join(db_root, "queen_sandbox.pkl")
    QUEENBEE = ReadPickleData(queen_db)
    queens_master_tickers = []
    queens_chess_pieces = []
    for qcp, qcp_vars in QUEENBEE["workerbees"].items():
        if qcp in qcp_s:
            for ticker in qcp_vars["tickers"]:
                queens_master_tickers.append(ticker)
                queens_chess_pieces.append(qcp)
    queens_chess_pieces = list(set(queens_chess_pieces))
    queens_master_tickers = list(set(queens_master_tickers))

    return {
        "QUEENBEE": QUEENBEE,
        "queens_chess_pieces": queens_chess_pieces,
        "queens_master_tickers": queens_master_tickers,
    }


def return_QUEEN_masterSymbols(
    prod=False,
    master_swarm_QUEENBEE=master_swarm_QUEENBEE,
):
    # QUEENBEE_db =  # os.path.join(os.path.join(hive_master_root(), 'db'), 'queen.pkl') # MasterSwarmQueen
    QUEENBEE = ReadPickleData(master_swarm_QUEENBEE(prod=prod))
    queens_master_tickers = []
    queens_chess_pieces = []
    for qcp, qcp_vars in QUEENBEE["workerbees"].items():
        for ticker in qcp_vars["tickers"]:
            # if qcp in qcp_s:
                # if qcp in ['knight']:
            queens_master_tickers.append(ticker)
            queens_chess_pieces.append(qcp)
    queens_chess_pieces = list(set(queens_chess_pieces))

    return {
        "QUEENBEE": QUEENBEE,
        "queens_chess_pieces": queens_chess_pieces,
        "queens_master_tickers": queens_master_tickers,
    }

def stars(chart_times=False, desc="frame_period: period count -- 1Minute_1Day"):
    if chart_times:
        return chart_times
    else:
        chart_times = {
            "1Minute_1Day": 1,
            "5Minute_5Day": 5,
            "30Minute_1Month": 18,
            "1Hour_3Month": 48,
            "2Hour_6Month": 72,
            "1Day_1Year": 250,
        }
        return chart_times

def read_QUEENs__pollenstory(symbols, read_swarmQueen=False, read_storybee=True, read_pollenstory=True, info="function uses async"):  # return combined dataframes
    ### updates return ticker db and path to db ###
    def async__read_symbol_data(ttf_file_paths):  # re-initiate for i timeframe
        async def get_changelog(session, ttf_file_name):
            async with session:
                try:
                    # print("read", ttf_file_name)
                    db = ReadPickleData(ttf_file_name)
                    if db:
                        ttf = os.path.basename(ttf_file_name).split(".pkl")[0]
                        return {"ttf_file_name": ttf_file_name, "ttf": ttf, "db": db}
                    else:
                        return {"ttf_file_name": ttf_file_name, "error": "Data Missing"}
                except Exception as e:
                    return {"ttf_file_name": ttf_file_name, "error": e}

        async def main(ttf_file_paths):
            async with aiohttp.ClientSession() as session:
                return_list = []
                tasks = []
                for (
                    ttf_file_name
                ) in (
                    ttf_file_paths
                ):  # castle: [spy], bishop: [goog], knight: [META] ..... pawn1: [xmy, skx], pawn2: [....]
                    tasks.append(
                        asyncio.ensure_future(get_changelog(session, ttf_file_name))
                    )
                original_pokemon = await asyncio.gather(*tasks)
                for pokemon in original_pokemon:
                    return_list.append(pokemon)

                return return_list

        list_of_status = asyncio.run(main(ttf_file_paths))
        return list_of_status

    try:
        # return beeworkers data

        if read_swarmQueen:
            qb = return_QUEEN_masterSymbols()
            symbols = qb.get("queens_master_tickers")
        else:
            symbols = symbols

        main_dir = workerbee_dbs_root()
        main_story_dir = workerbee_dbs_root__STORY_bee()

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
                    file = os.path.join(main_dir, f'{symbol}_{star}.pkl')
                    if os.path.exists(file) == False:
                        # print("DB does not exist", file)
                        pass
                    else:
                        ps_all_files_names.append(file)
            
            if read_storybee:
                for star in stars().keys():
                    file = os.path.join(main_story_dir, f'{symbol}_{star}.pkl')
                    if os.path.exists(file) == False:
                        # print("DB does not exist", file)
                        pass
                    else:
                        sb_all_files_names.append(file)

        # async read data
        if read_pollenstory:
            pollenstory_data = async__read_symbol_data(ttf_file_paths=ps_all_files_names)
            # put into dictionary
            for package_ in pollenstory_data:
                if "error" not in package_.keys():
                    pollenstory[package_["ttf"]] = package_["db"]["pollen_story"]
                else:
                    errors[package_["ttf"]] = package_["error"]
        if read_storybee:
            storybee_data = async__read_symbol_data(ttf_file_paths=sb_all_files_names)
            for package_ in storybee_data:
                if "error" not in package_.keys():
                    STORY_bee[package_["ttf"]] = package_["db"]["STORY_bee"]
                else:
                    errors[package_["ttf"]] = package_["error"]

        return {"pollenstory": pollenstory, "STORY_bee": STORY_bee, "errors": errors}
    except Exception as e:
        print_line_of_error("king return symbols failed")


def return_QUEENs_workerbees_chessboard(QUEEN_KING):
    queens_master_tickers = []
    for qcp, qcp_vars in QUEEN_KING["chess_board"].items():
        for ticker in qcp_vars["tickers"]:
            queens_master_tickers.append(ticker)

    return {"queens_master_tickers": queens_master_tickers}


def return_QUEENs__symbols_data(QUEEN=False, QUEEN_KING=False, symbols=False, swarmQueen=False, read_pollenstory=True, read_storybee=True, info="returns all ticker_time_frame data for open orders and chessboard"):
    active_queen_order_states = kingdom__global_vars().get('active_queen_order_states')
    def return_active_orders(QUEEN):
        df = QUEEN["queen_orders"]
        df["index"] = df.index
        df_active = df[df["queen_order_state"].isin(active_queen_order_states)].copy()

        return df_active

    try:
        if symbols:
            symbols = symbols
        else:
            # symbol ticker data # 1 all current pieces on chess board && all current running orders
            current_active_orders = return_active_orders(QUEEN=QUEEN)
            active_order_symbols = list(set(current_active_orders["symbol"].tolist())) if len(current_active_orders) > 1 else []
            chessboard_symbols = return_QUEENs_workerbees_chessboard(QUEEN_KING=QUEEN_KING).get("queens_master_tickers")

            if symbols:
                symbols = symbols + active_order_symbols + chessboard_symbols
            else:
                symbols = active_order_symbols + chessboard_symbols

        ticker_db = read_QUEENs__pollenstory(
            symbols=symbols,
            read_storybee=read_storybee, 
            read_pollenstory=read_pollenstory,
        )
        return ticker_db
    except Exception as e:
        print_line_of_error('king symbols data')

def handle__ttf_notactive__datastream(
    info="if ticker stream offline pull latest price by MasterApi",
):
    return True

def load_local_json(file_path):
    with open(file_path, 'r') as filee:
        data = json.load(filee)
        
    return data

def save_json(db_name, data):
    if db_name:
        with open(db_name, 'w') as file:
            json.dump(data, file)


def PickleData(pickle_file, data_to_store, write_temp=False, console=True):
    if pickle_file:
        if write_temp:
            root, name = os.path.split(pickle_file)
            pickle_file_temp = os.path.join(root, ("temp" + name))
            with open(pickle_file_temp, "wb+") as dbfile:
                pickle.dump(data_to_store, dbfile)

        with open(pickle_file, "wb+") as dbfile:
            pickle.dump(data_to_store, dbfile)
            if console:
                print("saved: ", pickle_file)
    else:
        print("saving a file without a file not a good idea")
        return False

    return True


def ReadPickleData(pickle_file):
    # Check the file's size and modification time
    prev_size = os.stat(pickle_file).st_size
    prev_mtime = os.stat(pickle_file).st_mtime
    stop = 0
    e = None
    while True:
        # Get the current size and modification time of the file
        curr_size = os.stat(pickle_file).st_size
        curr_mtime = os.stat(pickle_file).st_mtime

        # Check if the size or modification time has changed
        if curr_size != prev_size or curr_mtime != prev_mtime:
            # print(f"{pickle_file} is currently being written to")
            # logging.info(f'{pickle_file} is currently being written to')
            pass
        else:
            try:
                with open(pickle_file, "rb") as f:
                    pk_load = pickle.load(f)
                    pk_load['source'] = pickle_file
                    return pk_load
            except Exception as e:
                if stop > 0:
                    print('pkl read error: ', pickle_file, e, stop)
                if stop > 3:
                    print("CRITICAL read pickle failed ", e)
                    # logging.critical(f'{e} error is pickle load')
                    # send_email(subject='CRITICAL Read Pickle Break')
                    return ''
                stop += 1
                time.sleep(0.089)

        # Update the previous size and modification time
        prev_size = curr_size
        prev_mtime = curr_mtime

        # Wait a short amount of time before checking again
        time.sleep(0.033)


def print_line_of_error(e='print_error_message'):
    exc_type, exc_obj, exc_tb = sys.exc_info()
    print(e, exc_type, exc_tb.tb_lineno)
    return exc_type, exc_tb.tb_lineno

def streamlit_config_colors():
    # read config file and parse from there
    k_colors = {
        "default_text_color": "#055A6E",
        "default_font": "sans serif",
        "default_yellow_color": "#E6C93B",
        "default_background_color": '#F3FAFD',
    }
    for k,v in k_colors.items():
        st.session_state[k] = v
    return k_colors


def copy_directory(src, dst):
    # Check if the source directory exists
    if not os.path.exists(src):
        print(f"Error: {src} does not exist.")
        return
    # Create the destination directory if it does not exist
    os.makedirs(dst, exist_ok=True)
    # Copy all files from the source to the destination directory
    for file_name in os.listdir(src):
        src_file = os.path.join(src, file_name)
        dst_file = os.path.join(dst, file_name)
        if os.path.isfile(src_file):
            shutil.copy2(src_file, dst_file)

    return True


def local__filepaths_misc(jpg_root=hive_master_root()):
    jpg_root = os.path.join(jpg_root, "misc")
    bee_image = os.path.join(jpg_root, "bee.jpg")
    bee_power_image = os.path.join(jpg_root, "power.jpg")
    hex_image = os.path.join(jpg_root, "hex_design.jpg")
    hive_image = os.path.join(jpg_root, "bee_hive.jpg")
    queen_image = os.path.join(jpg_root, "queen.jpg")
    queen_angel_image = os.path.join(jpg_root, "queen_angel.jpg")
    flyingbee_gif_path = os.path.join(jpg_root, "flyingbee_gif_clean.gif")
    flyingbee_grey_gif_path = os.path.join(jpg_root, "flying_bee_clean_grey.gif")
    bitcoin_gif = os.path.join(jpg_root, "bitcoin_spinning.gif")
    power_gif = os.path.join(jpg_root, "power_gif.gif")
    uparrow_gif = os.path.join(jpg_root, "uparrows.gif")
    learningwalk_bee = os.path.join(jpg_root, "learningwalks_bee_jq.png")
    queen_flair_gif = os.path.join(jpg_root, "queen_flair.gif")
    chess_piece_queen = (
        "https://cdn.pixabay.com/photo/2012/04/18/00/42/chess-36311_960_720.png"
    )
    runaway_bee_gif = os.path.join(jpg_root, "runaway_bee_gif.gif")
    queen_png = "https://cdn.shopify.com/s/files/1/0925/9070/products/160103_queen_chess_piece_wood_shape_600x.png?v=1461105893"
    castle_png = "https://images.vexels.com/media/users/3/255175/isolated/lists/3c6de0f0c883416d9b6bd981a4471092-rook-chess-piece-line-art.png"
    bishop_png = "https://images.vexels.com/media/users/3/255170/isolated/lists/efeb124323c55a60510564779c9e1d38-bishop-chess-piece-line-art.png"
    knight_png = "https://cdn2.iconfinder.com/data/icons/chess-set-pieces/100/Chess_Set_04-White-Classic-Knight-512.png"
    mainpage_bee_png = (
        "https://i.pinimg.com/originals/a8/95/e8/a895e8e96c08357bfeb92d3920cd7da0.png"
    )
    runaway_bee_gif = os.path.join(jpg_root, "runaway_bee_gif.gif")
    floating_queen_gif = os.path.join(jpg_root, "floating-queen-unscreen.gif")
    chess_board__gif = os.path.join(jpg_root, "chess_board.gif")
    bishop_unscreen = os.path.join(jpg_root, "bishop_unscreen.gif")
    alpaca_portfolio_keys_png = os.path.join(jpg_root, "alpaca_portfolio_snap_keys.PNG")
    purple_heartbeat_gif = os.path.join(jpg_root, "purple_heartbeat.gif")
    moving_ticker_gif = os.path.join(jpg_root, "moving_ticker.gif")
    heart_bee_gif = os.path.join(jpg_root, "heart_bee.gif")
    hexagon_loop = os.path.join(jpg_root, "hexagon_loop.gif")
    queen_crown_url = (
        "https://cdn.pixabay.com/photo/2012/04/18/00/42/chess-36311_960_720.png"
    )
    pawn_png_url = "https://cdn0.iconfinder.com/data/icons/project-management-1-1/24/14-512.png"

    return {
        "jpg_root": jpg_root,
        "bee_image": bee_image,
        "bee_power_image": bee_power_image,
        "hex_image": hex_image,
        "hive_image": hive_image,
        "queen_image": queen_image,
        "queen_angel_image": queen_angel_image,
        "flyingbee_gif_path": flyingbee_gif_path,
        "flyingbee_grey_gif_path": flyingbee_grey_gif_path,
        "bitcoin_gif": bitcoin_gif,
        "power_gif": power_gif,
        "uparrow_gif": uparrow_gif,
        "learningwalk_bee": learningwalk_bee,
        "chess_piece_queen": chess_piece_queen,
        "runaway_bee_gif": runaway_bee_gif,
        "castle_png": castle_png,
        "bishop_png": bishop_png,
        "knight_png": knight_png,
        "queen_png": queen_png,
        "queen_flair_gif": queen_flair_gif,
        "mainpage_bee_png": mainpage_bee_png,
        "runaway_bee_gif": runaway_bee_gif,
        "floating_queen_gif": floating_queen_gif,
        "chess_board__gif": chess_board__gif,
        "bishop_unscreen": bishop_unscreen,
        "alpaca_portfolio_keys_png": alpaca_portfolio_keys_png,
        "purple_heartbeat_gif": purple_heartbeat_gif,
        "moving_ticker_gif": moving_ticker_gif,
        "heart_bee_gif": heart_bee_gif,
        "hexagon_loop": hexagon_loop,
        "queen_crown_url": queen_crown_url,
        "pawn_png_url": pawn_png_url,
    }

def main_index_tickers():
    main_indexes = {
        'SPY': {'long1X': "SPY",
                'long3X': 'SPXL', 
                'inverse1X': 'SH', 
                'inverse2X': 'SDS', 
                'inverse3X': 'SPXU'},
        'QQQ': {'long3X': 'TQQQ', 
                'inverse1X': 'PSQ', 
                'inverse2X': 'QID', 
                'inverse3X': 'SQQQ'}
        }
    
    return main_indexes

#### #### if __name__ == '__main__'  ###

