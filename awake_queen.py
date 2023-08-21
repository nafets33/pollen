import time
from datetime import datetime
import schedule
import sys, importlib
from chess_piece.queen_bee import queenbee

def call_job_queen():
    # importlib.reload(sys.modules['chess_piece'])
    # from chess_piece.workerbees_manager import workerbees_multiprocess_pool
    print("I'm Awake!: ", datetime.now().strftime("%A, %d. %B %Y %I:%M%p"))
    queenbee(client_user='stefanstapinski@gmail.com', prod=True)


run_time = "09:32"
a = schedule.every().day.at(run_time).do(call_job_queen)

all_jobs = schedule.get_jobs()
print(all_jobs)

while True:
    schedule.run_pending()
    time.sleep(1)