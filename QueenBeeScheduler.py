#QueenBeeScheduler

# use scheduler to run cron jobs
import time
import datetime
import subprocess
from jquest_utils import send_email_attachments
from jquest_utils import print_line_of_error
import schedule
import sys
from QueenHive import KING, logging_log_message, createParser, return_index_tickers, return_alpc_portolio, return_market_hours, return_dfshaped_orders, add_key_to_app, init_QUEEN, pollen_themes, init_app, check_order_status, slice_by_time, split_today_vs_prior, read_csv_db, update_csv_db, read_queensmind, read_pollenstory, pickle_chesspiece, speedybee, submit_order, return_timestamp_string, pollen_story, ReadPickleData, PickleData, return_api_keys, return_bars_list, refresh_account_info, return_bars, init_index_ticker, print_line_of_error, add_key_to_QUEEN

parser = createParser()
namespace = parser.parse_args()
queens_chess_piece = namespace.qcp # 'castle', 'knight' 'queen'

def call_job():
    print("I'm Awake!: ", datetime.datetime.now().strftime("%A, %d. %B %Y %I:%M%p"))
    try:
        subprocess.call("jq_RevRec-QRD_HeartBeat.py", shell=True)
    except Exception as e:
        send_email_attachments(emails=["<sstapinski@roku.com>"], subject="stay awake error", message=str(e))

schedule.every().day.at("06:00").do(call_job)
print("HeartBeat Turns on at 6AM")

if run == 'run':
    print("Adhoc Call Running Now")
    call_job()

while True:
    schedule.run_pending()
    time.sleep(1)