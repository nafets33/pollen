import time
from datetime import datetime
import schedule
import os, sys, importlib
from chess_piece.king import hive_master_root
import argparse
import subprocess
run = sys.argv[1]

def call_job_queen():
    # importlib.reload(sys.modules['chess_piece'])
    # from chess_piece.workerbees_manager import workerbees_multiprocess_pool
    print("I'm Awake!: ", datetime.now().strftime("%A, %d. %B %Y %I:%M%p"))
    # queenbee(client_user=client_user, prod=prod)
    script_path = os.path.join(hive_master_root(), 'chess_piece/queen_bee.py')
    subprocess.call(['python', script_path])

run_time = "09:32"
queen_sch = schedule.every().day.at(run_time).do(call_job_queen)

all_jobs = schedule.get_jobs()
print(all_jobs)

if run == 'run':
    print("adhoc call run")
    call_job_queen()

while True:
    schedule.run_pending()
    time.sleep(1)


# if __name__ == '__main__':
#     # read
#     def createParser():
#         parser = argparse.ArgumentParser()
#         parser.add_argument ('-run', default='false')
#         parser.add_argument ('-prod', default='true')
#         parser.add_argument ('-client_user', default='stefanstapinski@gmail.com')
#         return parser
    
#     parser = createParser()
#     namespace = parser.parse_args()
#     client_user = namespace.client_user
#     prod = True if 'true' == namespace.prod.lower() else False
#     run = True if 'true' == namespace.prod.lower() else False
    