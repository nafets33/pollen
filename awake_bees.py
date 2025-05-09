import time
from datetime import datetime
import schedule
import sys, importlib, os
import subprocess
from chess_piece.king import hive_master_root, ReadPickleData
from chess_piece.queen_hive import read_swarm_db, return_alpaca_api_keys, return_market_hours, init_swarm_dbs, init_qcp_workerbees, send_email
from chess_piece.workerbees import queen_workerbees
import pytz
import pandas as pd
from dotenv import load_dotenv

load_dotenv()
pg_migration = os.environ.get('pg_migration')

try:
    run = sys.argv[1]
except IndexError:
    run = False

try:
    prod = sys.argv[2]
except IndexError:
    prod = True

est = pytz.timezone("US/Eastern")
db=init_swarm_dbs(prod)


def call_bishop_bees(prod=prod):
    print("HELLO BISHOP", datetime.now().strftime("%A, %d. %B %Y %I:%M%p"))
    send_email(subject="BISHOP RUNNING")
    if pg_migration:
        BISHOP = read_swarm_db(prod, 'BISHOP')
    else:
        BISHOP = ReadPickleData(db.get('BISHOP'))

    qcp_bees_key = 'workerbees'
    QUEENBEE = {qcp_bees_key: {}}
    df = BISHOP.get('2025_Screen')
    sector_tickers = {}
    for sector in set(df['sector']):
        token = df[df['sector']==sector]
        tickers=token['symbol'].tolist()
        QUEENBEE[qcp_bees_key][sector] = init_qcp_workerbees(ticker_list=tickers)
        sector_tickers[sector] = len(tickers)

    pieces = list(QUEENBEE['workerbees'].keys())

    queen_workerbees(
                    qcp_s=pieces,
                    QUEENBEE=QUEENBEE,
                    prod=prod, 
                    reset_only=True, 
                    # backtesting=False, 
                    # run_all_pawns=False, 
                    # macd=None,
                    # streamit=False,
                        )
    print("BISHOP COMPLETE", datetime.now().strftime("%A, %d. %B %Y %I:%M%p"))
    send_email(subject="BISHOP COMPLETE")

def call_job_workerbees(prod=prod):

    print("Bees Awake!: ", datetime.now().strftime("%A, %d. %B %Y %I:%M%p"))

    """ Keys """
    api = return_alpaca_api_keys(prod=prod)["api"]

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


run_time = "09:30"
a = schedule.every().day.at(run_time).do(call_job_workerbees)

# # run_times = ["09:35", "10:15", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00"]
# b = schedule.every().day.at("09:35").do(call_bishop_bees)
# c = schedule.every().day.at("10:15").do(call_bishop_bees)
# d = schedule.every().day.at("11:00").do(call_bishop_bees)
# e = schedule.every().day.at("12:00").do(call_bishop_bees)
# f = schedule.every().day.at("13:00").do(call_bishop_bees)
# g = schedule.every().day.at("14:00").do(call_bishop_bees)
# h = schedule.every().day.at("15:00").do(call_bishop_bees)
# i = schedule.every().day.at("16:00").do(call_bishop_bees)


all_jobs = schedule.get_jobs()
for job in all_jobs:
    print(job)


if run == 'run':
    print("adhoc run")
    call_job_workerbees()

while True:
    schedule.run_pending()
    time.sleep(1)