import time
from datetime import datetime
import schedule
import sys, importlib, os
import subprocess
from chess_piece.king import hive_master_root
run = sys.argv[1]
def call_job_workerbees():
    # importlib.reload(sys.modules['chess_piece'])
    # from chess_piece.workerbees_manager import workerbees_multiprocess_pool
    print("I'm Awake!: ", datetime.now().strftime("%A, %d. %B %Y %I:%M%p"))
    # qcp_s = ["castle", "bishop", "knight", "pawn1", "pawn_5"]
    # workerbees_multiprocess_pool(prod=True, qcp_s=qcp_s)
    script_path = os.path.join(hive_master_root(), 'chess_piece/workerbees_manager.py')
    subprocess.call(['python', script_path])



run_time = "09:32"
a = schedule.every().day.at(run_time).do(call_job_workerbees)

all_jobs = schedule.get_jobs()
print(all_jobs)

if run == 'run':
    print("adhoc run")
    call_job_workerbees()

while True:
    schedule.run_pending()
    time.sleep(1)