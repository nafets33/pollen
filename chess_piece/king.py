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
import ipdb
# from pollenq_pages.queens_conscience import queens_conscience
# from custom_button import cust_Button

# from ozz.ozz_bee import send_ozz_call

# HTTPSConnectionPool(host='api.alpaca.markets', port=443): Read timed out. (read timeout=None)
# <class 'requests.exceptions.ReadTimeout'> 2409
# {'type': 'ProgramCrash', 'errbuz': ReadTimeout(ReadTimeoutError("HTTPSConnectionPool(host='api.alpaca.markets', port=443): Read timed out. (read timeout=None)")), 'er': <class 'requests.exceptions.ReadTimeout'>, 'lineerror': 2409}


est = pytz.timezone("US/Eastern")
utc = pytz.timezone('UTC')

def return_timestamp_string(format="%Y-%m-%d %H-%M-%S %p {}".format(est), tz=est):
    return datetime.now(tz).strftime(format)

def kingdom__global_vars():
    # ###### GLOBAL # ######
    return {
    'ARCHIVE_queenorder': "archived",
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
    ],
    'active_queen_order_states': [
        "submitted",
        "accetped",
        "pending",
        "running",
        "running_close",
        "running_open",
    ],
    'CLOSED_queenorders': ["running_close", "completed", "completed_alpaca"],
    'RUNNING_Orders': ["running", "running_open"],
    'RUNNING_CLOSE_Orders': ["running_close"],
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
# ###### GLOBAL # ######
ARCHIVE_queenorder = "archived"
active_order_state_list = [
    "running",
    "running_close",
    "submitted",
    "error",
    "pending",
    "completed",
    "completed_alpaca",
    "running_open",
    "archived_bee",
]
active_queen_order_states = [
    "submitted",
    "accetped",
    "pending",
    "running",
    "running_close",
    "running_open",
]
CLOSED_queenorders = ["running_close", "completed", "completed_alpaca"]
RUNNING_Orders = ["running", "running_open"]
RUNNING_CLOSE_Orders = ["running_close"]
# crypto
crypto_currency_symbols = ["BTCUSD", "ETHUSD", "BTC/USD", "ETH/USD"]
coin_exchange = "CBSE"

# misc
exclude_conditions = [
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
]  # 'U'
# script_path = os.path.abspath(__file__)
# print(script_path)


def menu_bar_selection(prod_name_oppiste, prod_name, prod, menu,hide_streamlit_markers=True):
    k_colors = streamlit_config_colors()
    default_text_color = k_colors['default_text_color'] # = '#59490A'
    default_font = k_colors['default_font'] # = "sans serif"
    default_yellow_color = k_colors['default_yellow_color'] # = '#C5B743'
    


    if menu == 'main':
        
        menu_data = [
            {'id':'QC','icon':"fa fa-fire",'label':"Queen"},
            {'id':'TradingModels','icon':"fa fa-fire",'label':"Trading Models"},
            {'icon': "fa fa-bug", 'label':"PlayGround"},
            {'icon': "fa fa-fighter-jet",'label':"HiveEngine", 'submenu':[{'id':'pollen_engine', 'label':"QUEEN", 'icon': "fa fa-heart"},{'label':"KING", 'icon': "fa fa-meh"}]},
            # {'id':'sb_liv_switch', 'icon': "fa fa-reply", 'label':f'Switch To {prod_name_oppiste}'},
# 'submenu':[{'id': 'sb_liv_switch', 'label': f'Switch To {prod_name_oppiste}', 'icon': "fa fa-reply"}]
        ]
    elif menu == 'unAuth':
        menu_data = [
            {'id':'unauth','icon':"fa fa-fire",'label':"Welcome to pollenq"},

            # {'id':'Copy','icon':"🐙",'label':"Copy"},
            # {'icon': "fa-solid fa-radar",'label':"Dropdown1", 'submenu':[{'id':' subid11','icon': "fa fa-paperclip", 'label':"Sub-item 1"},{'id':'subid12','icon': "💀", 'label':"Sub-item 2"},{'id':'subid13','icon': "fa fa-database", 'label':"Sub-item 3"}]},
            # {'icon': "far fa-chart-bar", 'label':"Chart"},#no tooltip message
            # {'id':' Crazy return value 💀','icon': "💀", 'label':"Calendar"},
            # {'icon': "fas fa-tachometer-alt", 'label':"Dashboard",'ttip':"I'm the Dashboard tooltip!"}, #can add a tooltip message
            # {'icon': "far fa-copy", 'label':"Right End"},
            # {'icon': "fa-solid fa-radar",'label':"Dropdown2", 'submenu':[{'label':"Sub-item 1", 'icon': "fa fa-meh"},{'label':"Sub-item 2"},{'icon':'🙉','label':"Sub-item 3",}]},
        ]
        prod_name = ""

    if prod:

        menu_id = hc.nav_bar(
            menu_definition=menu_data,
            home_name=f'pollenq {prod_name}',
            login_name='Account',
            hide_streamlit_markers=hide_streamlit_markers, #will show the st hamburger as well as the navbar now!
            sticky_nav=True, #at the top or not
            sticky_mode='pinned', #jumpy or not-jumpy, but sticky or pinned
        )
    else:
        over_theme = {'option_active':'#B7C8D6'} # {'txc_inactive': '#FB070A'} #'txc_active':'#59490A','option_active':'#FB6464'} #'menu_background':'black',
        # over_font = {'font-class':'h2','font-size':'100%'}
        # over_theme = {'txc_inactive': "#0D93FB"}
        menu_id = hc.nav_bar(
            menu_definition=menu_data,
            override_theme=over_theme,
            # font_styling=over_font,
            home_name=f'pollenq {prod_name}',
            login_name='Account',
            hide_streamlit_markers=hide_streamlit_markers, #will show the st hamburger as well as the navbar now!
            sticky_nav=True, #at the top or not
            sticky_mode='pinned', #jumpy or not-jumpy, but sticky or pinned
        )

    st.session_state['menu_id']= menu_id

    return menu_id


def hive_master_root(info='\pollen\pollen'):
    script_path = os.path.abspath(__file__)
    return os.path.dirname(os.path.dirname(script_path)) # \pollen\pollen

# def pollenmain_root():
#     return os.path.dirname(hive_master_root()) # \pollen

def master_swarm_QUEENBEE(prod):
    if prod:
        PB_QUEENBEE_Pickle = os.path.join(os.path.join(hive_master_root(), "db"), "queen.pkl") # pollen/db
    else:
        PB_QUEENBEE_Pickle = os.path.join(os.path.join(hive_master_root(), "db"), "queen_sandbox.pkl")
    
    return PB_QUEENBEE_Pickle

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

def kingdom__grace_to_find_a_Queen():
    # create list for userdb
    PB_KING_Pickle = master_swarm_KING(prod=True)
    KING = ReadPickleData(PB_KING_Pickle)
    users_allowed_queen_email = KING['users'].get('client_user__allowed_queen_list')
    users_allowed_queen_email.append("stefanstapinski@gmail.com")
    users_allowed_queen_email.append("sven0227@gmail.com")

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


def read_QUEENs__pollenstory(symbols, read_swarmQueen=False, read_storybee=True, read_pollenstory=True, info="function uses async"):  # return combined dataframes
    ### updates return ticker db and path to db ###
    def async__read_symbol_data(ttf_file_paths):  # re-initiate for i timeframe
        async def get_changelog(session, ttf_file_name):
            async with session:
                try:
                    db = ReadPickleData(ttf_file_name)
                    ttf = os.path.basename(ttf_file_name).split(".pkl")[0]
                    return {"ttf_file_name": ttf_file_name, "ttf": ttf, "db": db}
                except Exception as e:
                    return {"ttf_file_name": ttf_file_name, "ttf": ttf, "error": e}

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
            ps_all_files_names = ps_all_files_names + [
                os.path.join(main_dir, i)
                for i in os.listdir(main_dir)
                if symbol in i and "temp" not in i
            ]  # SPY SPY_1Minute_1Day
        
        if read_storybee:
            sb_all_files_names = sb_all_files_names + [
                os.path.join(main_story_dir, i)
                for i in os.listdir(main_story_dir)
                if symbol in i and "temp" not in i
            ]  # SPY SPY_1Minute_1Day

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


def return_QUEENs_workerbees_chessboard(QUEEN_KING):
    queens_master_tickers = []
    for qcp, qcp_vars in QUEEN_KING["chess_board"].items():
        for ticker in qcp_vars["tickers"]:
            queens_master_tickers.append(ticker)

    return {"queens_master_tickers": queens_master_tickers}


def return_QUEENs__symbols_data(QUEEN, QUEEN_KING, symbols=False, swarmQueen=False, read_pollenstory=True, read_storybee=True, info="returns all ticker_time_frame data for open orders and chessboard"):
    def return_active_orders(QUEEN):
        df = QUEEN["queen_orders"]
        df["index"] = df.index
        df_active = df[df["queen_order_state"].isin(active_queen_order_states)].copy()

        return df_active

    # symbol ticker data # 1 all current pieces on chess board && all current running orders
    current_active_orders = return_active_orders(QUEEN=QUEEN)
    active_order_symbols = list(set(current_active_orders["symbol"].tolist()))
    chessboard_symbols = return_QUEENs_workerbees_chessboard(
        QUEEN_KING=QUEEN_KING)["queens_master_tickers"]

    if symbols:
        symbols = symbols + active_order_symbols + chessboard_symbols
    else:
        symbols = active_order_symbols + chessboard_symbols
    
    if swarmQueen:
        symbols = [i.split("_")[0] for i in os.listdir(os.path.join(hive_master_root(), 'symbols_STORY_bee_dbs'))]

    ticker_db = read_QUEENs__pollenstory(
        symbols=symbols,
        read_storybee=read_storybee, 
        read_pollenstory=read_pollenstory,
    )

    return ticker_db


def handle__ttf_notactive__datastream(
    info="if ticker stream offline pull latest price by MasterApi",
):
    return True


def PickleData(pickle_file, data_to_store, write_temp=False):
    if write_temp:
        root, name = os.path.split(pickle_file)
        pickle_file_temp = os.path.join(root, ("temp" + name))
        with open(pickle_file_temp, "wb+") as dbfile:
            pickle.dump(data_to_store, dbfile)

    with open(pickle_file, "wb+") as dbfile:
        pickle.dump(data_to_store, dbfile)

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
            pass
            # print(f"{pickle_file} is currently being written to")
            # logging.info(f'{pickle_file} is currently being written to')
        else:
            try:
                with open(pickle_file, "rb") as f:
                    return pickle.load(f)
            except Exception as e:
                # print('pickleerror ', pickle_file, e)
                # logging.error(f'{e} error is pickle load')
                if stop > 3:
                    print("CRITICAL read pickle failed ", e)
                    # logging.critical(f'{e} error is pickle load')
                    # send_email(subject='CRITICAL Read Pickle Break')
                    break
                stop += 1
                time.sleep(0.033)

        # Update the previous size and modification time
        prev_size = curr_size
        prev_mtime = curr_mtime

        # Wait a short amount of time before checking again
        time.sleep(0.033)


def print_line_of_error():
    exc_type, exc_obj, exc_tb = sys.exc_info()
    print(exc_type, exc_tb.tb_lineno)
    return exc_type, exc_tb.tb_lineno

def streamlit_config_colors():
    # read config file and parse from there
    return {
        "default_text_color": "#59490A",
        "default_font": "sans serif",
        "default_yellow_color": "#C5B743",
    }


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



#### #### if __name__ == '__main__'  ###

