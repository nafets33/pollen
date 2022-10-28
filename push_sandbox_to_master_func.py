# Push all sandbox to Master File

import shutil
import os

main_root = os.getcwd()
db_root = os.path.join(main_root, 'db')

def push_sandbox_to_master(db_root=db_root, sb_file_paths=['QueenBee_sandbox.py', 'QueenHive_sandbox.py', 'app_sandbox.py']):
    
    for file_ in sb_file_paths:
        db_file = os.path.join(db_root, file_)
        dst_path = os.path.join(db_root, file_.replace("_sandbox", ''))
        print(dst_path)
        shutil.copy(db_file, dst_path) 
    
    return True