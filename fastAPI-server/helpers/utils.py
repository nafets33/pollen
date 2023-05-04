import os, sys
import pickle
import time
from dotenv import load_dotenv

# script_dir = os.path.dirname(__file__)
# db_folder_path = os.path.abspath(os.path.join(
#     script_dir, '..', '..', '..', '..', 'client_user_dbs'))

# chess_piece_module = os.path.abspath(os.path.join(script_dir, '..', '..', '..', '..', 'chess_piece'))

# sys.path.append(chess_piece_module)

# from .chess_piece.king import hive_master_root

# def find_folder(user_name):
#     # Loop through all folders and files in the db folder
#     for root, dirs, files in os.walk(db_folder_path):
#         for dir_name in dirs:
#             if user_name in dir_name:
#                 return dir_name

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
                    # print("CRITICAL read pickle failed ", e)
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

def PickleData(pickle_file, data_to_store, write_temp=False):
    if write_temp:
        root, name = os.path.split(pickle_file)
        pickle_file_temp = os.path.join(root, ("temp" + name))
        with open(pickle_file_temp, "wb+") as dbfile:
            pickle.dump(data_to_store, dbfile)

    with open(pickle_file, "wb+") as dbfile:
        pickle.dump(data_to_store, dbfile)

    return True