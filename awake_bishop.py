import time
from datetime import datetime
import schedule
import sys, importlib, os
import subprocess
from chess_piece.king import hive_master_root, ReadPickleData
from chess_piece.queen_hive import read_swarm_db, return_symbols_list_from_queenbees_story, return_market_hours, init_swarm_dbs, init_qcp_workerbees, send_email
from chess_piece.workerbees import queen_workerbees
from chess_piece.pollen_db import PollenDatabase, MigratePostgres
import pytz
import pandas as pd
from dotenv import load_dotenv
import argparse


load_dotenv()
pg_migration = os.environ.get('pg_migration')
parser = argparse.ArgumentParser(description="Run the Bishop Bees Scheduler")
parser.add_argument("-bishop_symbols", action="store_true", help="Trigger the call_bishop_bees function immediately")
parser.add_argument('-prod', default='true', help="Run in production mode")
parser.add_argument('-run', default='false', help="Run in production mode")
args = parser.parse_args()

try:
    prod = sys.argv[2]
except IndexError:
    prod = True

est = pytz.timezone("US/Eastern")
db=init_swarm_dbs(prod)


def call_bishop_bees(prod=prod, upsert_to_main_server=False):
    print("HELLO BISHOP", datetime.now().strftime("%A, %d. %B %Y %I:%M%p"))
    # send_email(subject="BISHOP RUNNING")
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

def copy_pollen_store_by_symbol_to_MAIN_server():
    try:
        s = datetime.now()
        symbols = return_symbols_list_from_queenbees_story(all_symbols=True)
        # send_email(subject="Pollen Store Server Sync RUNNING")
        retrieve_all_pollenstory_data = PollenDatabase.retrieve_all_pollenstory_data(symbols).get('pollenstory')

        # Extract the nested dict and add proper key prefixes
        bulk_data = {
            f'POLLEN_STORY_{key}': {"pollen_story": value} 
            for key, value in retrieve_all_pollenstory_data.items()
        }
        # Bulk upsert
        MigratePostgres.upsert_multiple('pollen_store', bulk_data, console=True)

        retrieve_all_story_bee_data = PollenDatabase.retrieve_all_story_bee_data(symbols).get('STORY_bee')
        bulk_data = {
            f'STORY_BEE_{key}': {"STORY_bee": value}
            for key, value in retrieve_all_story_bee_data.items()
        }
        MigratePostgres.upsert_multiple('pollen_store', bulk_data, console=True)

        time_delta = (datetime.now() - s).total_seconds()
        send_email(subject=f"Pollen Store Server Sync COMPLETED {round(time_delta)} seconds", body=f"Migrated {len(symbols)} symbols in {round(time_delta)} seconds.")
    except Exception as e:
        print(e)
        send_email(subject=f"Pollen Store Server Sync FAILED", body=str(e))

def copy_data_between_tables(source_table='snapshot_priceinfo', target_table='snapshot_priceinfo'):

    def get_connection_and_cursor():
        conn = MigratePostgres.get_server_connection()
        cur = conn.cursor()
        return conn, cur

    try:
        # Get connection and cursor
        source_con, source_cur = PollenDatabase.return_db_conn(return_curser=True)
        target_con, target_cur = get_connection_and_cursor()

        # Fetch data from the source table
        source_cur.execute(f"SELECT * FROM {source_table};")
        rows = source_cur.fetchall()

        # Get column names from the source table
        source_cur.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name = '{source_table}';")
        columns = [row[0] for row in source_cur.fetchall()]
        column_list = ", ".join(columns)

        # Prepare the INSERT statement for the target table
        placeholders = ", ".join(["%s"] * len(columns))
        insert_query = f"INSERT INTO {target_table} ({column_list}) VALUES ({placeholders});"

        # Write each row into the target table
        for row in rows:
            target_cur.execute(insert_query, row)

        # Commit changes to the target table
        target_con.commit()
        print(f"Data successfully copied from {source_table} to {target_table}.")

    except Exception as e:
        print(e)
    finally:
        # Ensure both connections are closed
        if source_cur:
            source_cur.close()
        if source_con:
            source_con.close()
        if target_cur:
            target_cur.close()
        if target_con:
            target_con.close()

if __name__ == "__main__":
# Parse command-line arguments

    if args.run:
        print("Ad-hoc run triggered for BISHOP")
        copy_pollen_store_by_symbol_to_MAIN_server()

    # Schedule tasks
    schedule.every().day.at("09:33").do(copy_data_between_tables)
    times = ["09:35", "10:15", "11:00", "12:00", "13:00", "14:00", "15:00", "15:16"]
    for t in times:
        schedule.every().day.at(t).do(copy_pollen_store_by_symbol_to_MAIN_server)
    # schedule.every().day.at("09:35").do(copy_pollen_store_by_symbol_to_MAIN_server)
    # schedule.every().day.at("10:15").do(copy_pollen_store_by_symbol_to_MAIN_server)
    # schedule.every().day.at("11:00").do(copy_pollen_store_by_symbol_to_MAIN_server)
    # schedule.every().day.at("12:00").do(copy_pollen_store_by_symbol_to_MAIN_server)
    # schedule.every().day.at("13:00").do(copy_pollen_store_by_symbol_to_MAIN_server)
    # schedule.every().day.at("14:00").do(copy_pollen_store_by_symbol_to_MAIN_server)
    # schedule.every().day.at("15:00").do(copy_pollen_store_by_symbol_to_MAIN_server)
    # schedule.every().day.at("15:16").do(copy_pollen_store_by_symbol_to_MAIN_server)
    
    # Print all scheduled jobs
    all_jobs = schedule.get_jobs()
    for job in all_jobs:
        print(job)

    # Run the scheduler
    while True:
        schedule.run_pending()
        time.sleep(1)