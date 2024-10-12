import time
from datetime import datetime
import schedule
import sys, importlib, os
import subprocess
from chess_piece.king import hive_master_root
from chess_piece.queen_hive import return_alpaca_api_keys, return_market_hours
import pytz
import pandas as pd

run = sys.argv[1]

est = pytz.timezone("US/Eastern")


def call_job_workerbees():

    print("Bees Awake!: ", datetime.now().strftime("%A, %d. %B %Y %I:%M%p"))

    """ Keys """
    api = return_alpaca_api_keys(prod=False)["api"]

    """# Dates """
    current_date = datetime.now(est).strftime("%Y-%m-%d")
    trading_days = api.get_calendar()
    trading_days_df = pd.DataFrame([day._raw for day in trading_days])

    trading_days_df["date"] = pd.to_datetime(trading_days_df["date"])


    mkhrs = return_market_hours(trading_days=trading_days)
    if mkhrs != 'open':
        print("Markets Closed")
        return False

    script_path = os.path.join(hive_master_root(), 'chess_piece/workerbees_manager.py')
    subprocess.call(['python', script_path])

    return True


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