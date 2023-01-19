import asyncio
import datetime
import os
import pickle
import sqlite3
import sys
import time

import aiohttp
import ipdb
import pytz

# import logging

est = pytz.timezone("US/Eastern")


def hive_master_root():
    return os.getcwd()


def master_swarm_QUEENBEE(prod):
    if prod:
        return os.path.join(os.path.join(hive_master_root(), "db"), "queen.pkl")
    else:
        return os.path.join(os.path.join(hive_master_root(), "db"), "queen_sandbox.pkl")


def client_dbs_root():
    main_root = hive_master_root()
    client_dbs = os.path.join(os.path.dirname(main_root), "client_user_dbs")
    return client_dbs


def workerbee_dbs_root():
    symbols_pollenstory_dbs = os.path.join(
        os.path.join(os.path.dirname(hive_master_root()), "symbols_pollenstory_dbs")
    )
    return symbols_pollenstory_dbs


def workerbee_dbs_root__STORY_bee():
    symbols_pollenstory_dbs = os.path.join(
        os.path.join(os.path.dirname(hive_master_root()), "symbols_STORY_bee_dbs")
    )
    return symbols_pollenstory_dbs


def init_symbol_dbs__pollenstory():
    main_root = hive_master_root()  # os.getcwd()  # hive root
    symbol_dbs = os.path.join(os.path.dirname(main_root), "symbols_pollenstory_dbs")

    if os.path.exists(symbol_dbs) == False:
        print("Init symbols_dbs")
        os.mkdir(symbol_dbs)

    return symbol_dbs


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


def init_clientUser_dbroot(client_user):
    main_root = hive_master_root()  # os.getcwd()  # hive root
    client_user_db_dir = client_dbs_root()

    if client_user in ["stefanstapinski"]:  ## admin
        db_root = os.path.join(main_root, "db")
    else:
        client_user = client_user.split("@")[0]
        db_root = os.path.join(client_user_db_dir, f"db__{client_user}")
        if os.path.exists(db_root) == False:
            os.mkdir(db_root)
            os.mkdir(os.path.join(db_root, "logs"))

    return db_root


def streamlit_config_colors():
    # read config file and parse from there
    return {
        "default_text_color": "#59490A",
        "default_font": "sans serif",
        "default_yellow_color": "#C5B743",
    }


def local__filepaths_misc():

    jpg_root = os.path.join(hive_master_root(), "misc")
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
    queen_flair_gif = os.path.join(jpg_root, "queen_flair.gif")
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
        "queen_flair_gif": queen_flair_gif,
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
    }


def kingdom__grace_to_find_a_Queen():
    # create list for userdb
    con = sqlite3.connect("db/users.db")
    cur = con.cursor()
    users = cur.execute("SELECT * FROM users").fetchall()

    users_allowed_queen_email = [
        "stevenweaver8@gmail.com",
        "stefanstapinski@gmail.com",
        "adivergentthinker@gmail.com",
        "stapinski89@gmail.com",
        "jehddie@gmail.com",
        "conrad.studzinski@yahoo.com",
        "jamesliess@icloud.com",
    ]

    users_allowed_queen_emailname = [
        client_user.split("@")[0] for client_user in users_allowed_queen_email
    ]
    users_allowed_queen_emailname__db = [
        f"db__{cu}" for cu in users_allowed_queen_emailname
    ]

    return (
        users_allowed_queen_email,
        users_allowed_queen_emailname,
        users_allowed_queen_emailname__db,
    )


def return_QUEENs_workerbees_chessboard(QUEEN):
    queens_master_tickers = []
    for qcp, qcp_vars in QUEEN["workerbees"].items():
        for ticker in qcp_vars["tickers"]:
            queens_master_tickers.append(ticker)

    return {"queens_master_tickers": queens_master_tickers}


def read_QUEEN(queen_db, qcp_s=["castle", "bishop", "knight"]):
    # queen_db = os.path.join(db_root, "queen_sandbox.pkl")
    QUEENBEE = ReadPickleData(queen_db)
    queens_master_tickers = []
    queens_chess_pieces = []
    for qcp, qcp_vars in QUEENBEE["workerbees"].items():
        for ticker in qcp_vars["tickers"]:
            if qcp in qcp_s:
                # if qcp in ['knight']:
                queens_master_tickers.append(ticker)
                queens_chess_pieces.append(qcp)
    queens_chess_pieces = list(set(queens_chess_pieces))

    return {
        "QUEENBEE": QUEENBEE,
        "queens_chess_pieces": queens_chess_pieces,
        "queens_master_tickers": queens_master_tickers,
    }


def return_QUEEN_masterSymbols(
    prod=False,
    master_swarm_QUEENBEE=master_swarm_QUEENBEE,
    qcp_s=["castle", "bishop", "knight"],
):
    # QUEENBEE_db =  # os.path.join(os.path.join(hive_master_root(), 'db'), 'queen.pkl') # MasterSwarmQueen
    QUEENBEE = ReadPickleData(master_swarm_QUEENBEE(prod=prod))
    queens_master_tickers = []
    queens_chess_pieces = []
    for qcp, qcp_vars in QUEENBEE["workerbees"].items():
        for ticker in qcp_vars["tickers"]:
            if qcp in qcp_s:
                # if qcp in ['knight']:
                queens_master_tickers.append(ticker)
                queens_chess_pieces.append(qcp)
    queens_chess_pieces = list(set(queens_chess_pieces))

    return {
        "QUEENBEE": QUEENBEE,
        "queens_chess_pieces": queens_chess_pieces,
        "queens_master_tickers": queens_master_tickers,
    }


def read_QUEENs__pollenstory(
    symbols, read_swarmQueen=False, info="function uses async"
):  # return combined dataframes
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
        symbols = qb["queens_master_tickers"]
    else:
        symbols = symbols

    main_dir = workerbee_dbs_root()
    main_story_dir = workerbee_dbs_root__STORY_bee()

    # Final Return
    pollenstory = {}
    STORY_bee = {}

    # pollen story // # story bee
    ps_all_files_names = []
    sb_all_files_names = []
    for symbol in set(symbols):
        ps_all_files_names = ps_all_files_names + [
            os.path.join(main_dir, i)
            for i in os.listdir(main_dir)
            if symbol in i and "temp" not in i
        ]  # SPY SPY_1Minute_1Day
        sb_all_files_names = sb_all_files_names + [
            os.path.join(main_story_dir, i)
            for i in os.listdir(main_story_dir)
            if symbol in i and "temp" not in i
        ]  # SPY SPY_1Minute_1Day

    # async read data
    pollenstory_data = async__read_symbol_data(ttf_file_paths=ps_all_files_names)
    storybee_data = async__read_symbol_data(ttf_file_paths=sb_all_files_names)

    # put into dictionary
    errors = {}
    for package_ in pollenstory_data:
        if "error" not in package_.keys():
            pollenstory[package_["ttf"]] = package_["db"]["pollen_story"]
        else:
            errors[package_["ttf"]] = package_["error"]
    for package_ in storybee_data:
        if "error" not in package_.keys():
            STORY_bee[package_["ttf"]] = package_["db"]["STORY_bee"]
        else:
            errors[package_["ttf"]] = package_["error"]

    return {"pollenstory": pollenstory, "STORY_bee": STORY_bee, "errors": errors}


def handle__ttf_notactive__datastream(
    info="if ticker stream offline pull latest price by MasterApi",
):

    return True


#### GLOBAL ####
def PickleData(pickle_file, data_to_store, write_temp=True):

    p_timestamp = {"pq_last_modified": datetime.datetime.now(est)}
    root, name = os.path.split(pickle_file)
    pickle_file_temp = os.path.join(root, ("temp" + name))
    if write_temp:
        with open(pickle_file_temp, "wb+") as dbfile:
            db = data_to_store
            db["pq_last_modified"] = p_timestamp
            pickle.dump(db, dbfile)

    with open(pickle_file, "wb+") as dbfile:
        db = data_to_store
        db["pq_last_modified"] = p_timestamp
        pickle.dump(db, dbfile)

    return True


def ReadPickleData(pickle_file):

    # Check the file's size and modification time
    prev_size = os.stat(pickle_file).st_size
    prev_mtime = os.stat(pickle_file).st_mtime
    while True:
        stop = 0
        # Get the current size and modification time of the file
        curr_size = os.stat(pickle_file).st_size
        curr_mtime = os.stat(pickle_file).st_mtime

        # Check if the size or modification time has changed
        if curr_size != prev_size or curr_mtime != prev_mtime:
            print(f"{pickle_file} is currently being written to")
            # logging.info(f'{pickle_file} is currently being written to')
        else:
            if stop > 3:
                print("pickle error")
                # logging.critical(f'{e} error is pickle load')
                # send_email(subject='CRITICAL Read Pickle Break')
                break
            try:
                with open(pickle_file, "rb") as f:
                    return pickle.load(f)
            except Exception as e:
                print(e)
                # logging.error(f'{e} error is pickle load')
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


#### GLOBAL ####


#### #### if __name__ == '__main__'  ###
