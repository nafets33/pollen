import time
from datetime import datetime
import schedule
import sys, importlib
from chess_piece.workerbees_manager import workerbees_multiprocess_pool

def call_job_workerbees():
    # importlib.reload(sys.modules['chess_piece'])
    # from chess_piece.workerbees_manager import workerbees_multiprocess_pool
    print("I'm Awake!: ", datetime.now().strftime("%A, %d. %B %Y %I:%M%p"))
    qcp_s = ["castle", "bishop", "knight", "pawn1", "pawn_5"]
    workerbees_multiprocess_pool(prod=True, qcp_s=qcp_s)



qrd_run_time = "09:32"
a = schedule.every().day.at(qrd_run_time).do(call_job_workerbees)

all_jobs = schedule.get_jobs()
print(all_jobs)

while True:
    schedule.run_pending()
    time.sleep(1)