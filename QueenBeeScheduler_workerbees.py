#QueenBeeScheduler

# use scheduler to run cron jobs
import time
import datetime
import subprocess
import schedule
# from scheduler import Scheduler
import pytz
import sys
import argparse
# from QueenWorkerCrypto import queen_workerbee_coins
from QueenWorkerBees import queen_workerbees

def createParser_scheduler():
    parser = argparse.ArgumentParser()
    parser.add_argument ('-qcp', default="scheduler")
    parser.add_argument ('-prod', default='false')
    # parser.add_argument ('-adhoc_coins', default='false')
    parser.add_argument ('-adhoc_workers', default='false')
    return parser

parser = createParser_scheduler()
namespace = parser.parse_args()
# adhoc_coins = namespace.adhoc_coins
adhoc_workers = namespace.adhoc_workers

def call_job_workerbees():
    print("I'm Awake!: ", datetime.datetime.now().strftime("%A, %d. %B %Y %I:%M%p"))
    # subprocess.call("QueenWorkerCrypto.py", shell=True)
    queen_workerbees()

# est = pytz.timezone("US/Eastern")
# schedule = Scheduler(tzinfo=est)

schedule.every().day.at("14:32").do(call_job_workerbees) ## UTC
print("Workers Turns on at 9:32AM")

if adhoc_workers == 'true':
    print("running adhoc")
    call_job_workerbees()

while True:
    schedule.run_pending()
    time.sleep(1)