import time
from datetime import datetime
import schedule
import sys, importlib, os
import subprocess
from chess_piece.king import hive_master_root, ReadPickleData
from chess_piece.queen_hive import read_swarm_db, return_alpaca_api_keys, return_market_hours, init_swarm_dbs, init_qcp_workerbees, send_email
from chess_piece.workerbees import queen_workerbees
from chess_piece.pollen_db import PollenDatabase, MigratePostgres
import pytz
import pandas as pd
from dotenv import load_dotenv


load_dotenv()
pg_migration = os.environ.get('pg_migration')


try:
    prod = sys.argv[2]
except IndexError:
    prod = True

est = pytz.timezone("US/Eastern")
db=init_swarm_dbs(prod)


def call_bishop_bees(prod=prod, upsert_to_main_server=False):
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
                    upsert_to_main_server=upsert_to_main_server
                        )
    print("BISHOP COMPLETE", datetime.now().strftime("%A, %d. %B %Y %I:%M%p"))
    send_email(subject="BISHOP COMPLETE")


def copy_pollen_store_to_MAIN_server(tables_to_migrate=['pollen_store']):
    try:
        send_email(subject="Pollen Store Server Sync RUNNING")
        s = datetime.now()
        for table in tables_to_migrate:
            df=(pd.DataFrame(PollenDatabase.get_all_keys_with_timestamps(table))).rename(columns={0:'key', 1:'timestamp'})
            for key in df['key'].tolist():
                data = PollenDatabase.retrieve_data(table, key)
                if MigratePostgres.upsert_migrate_data(table, key, data):
                    print(f'{key} migrated to Main Server')
        time_delta = (datetime.now() - e).total_seconds()
        send_email(subject=f"Pollen Store Server Sync COMPLETED {round(time_delta)} seconds")
    except Exception as e:
        print(e)
        send_email(subject=f"Pollen Store Server Sync FAILED", body=str(e))

# run_time = "09:30"
# a = schedule.every().day.at(run_time).do(call_job_workerbees)

# run_times = ["09:35", "10:15", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00"]
b = schedule.every().day.at("09:35").do(call_bishop_bees)
# bb = schedule.every().day.at("09:35").do(copy_pollen_store_to_MAIN_server)
c = schedule.every().day.at("10:15").do(call_bishop_bees)
# cc = schedule.every().day.at("10:15").do(copy_pollen_store_to_MAIN_server)
d = schedule.every().day.at("11:00").do(call_bishop_bees)
# dd = schedule.every().day.at("10:45").do(copy_pollen_store_to_MAIN_server)

e = schedule.every().day.at("12:00").do(call_bishop_bees)
# ee = schedule.every().day.at("13:04").do(copy_pollen_store_to_MAIN_server)

f = schedule.every().day.at("13:00").do(call_bishop_bees)
g = schedule.every().day.at("14:00").do(call_bishop_bees)
h = schedule.every().day.at("15:00").do(call_bishop_bees)
i = schedule.every().day.at("21:05").do(call_bishop_bees)

# bb = schedule.every().day.at("21:34").do(lambda: call_bishop_bees(prod=prod, upsert_to_main_server=True))



all_jobs = schedule.get_jobs()
for job in all_jobs:
    print(job)

while True:
    schedule.run_pending()
    time.sleep(1)