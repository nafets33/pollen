#QueenBeeScheduler

# use scheduler to run cron jobs
import time
import datetime
import subprocess
import schedule
import sys
import argparse
from QueenWorkerCrypto import queen_workerbee_coins
# from QueenWorkerBees import queen_workerbees

def createParser_scheduler():
    parser = argparse.ArgumentParser()
    parser.add_argument ('-qcp', default="scheduler")
    parser.add_argument ('-prod', default='false')
    parser.add_argument ('-adhoc_coins', default='false')
    # parser.add_argument ('-adhoc_workers', default='false')
    return parser

parser = createParser_scheduler()
namespace = parser.parse_args()
adhoc_coins = namespace.adhoc_coins
# adhoc_workers = namespace.adhoc_workers

def call_job_coins():
    print("I'm Awake!: ", datetime.datetime.now().strftime("%A, %d. %B %Y %I:%M%p"))
    # subprocess.call("QueenWorkerCrypto.py", shell=True)
    queen_workerbee_coins()


schedule.every().day.at("07:00").do(call_job_coins)
print("Coins Turns on at 7AM")


if adhoc_coins == 'true':
    print("running adhoc")
    call_job_coins()

while True:
    schedule.run_pending()
    time.sleep(1)