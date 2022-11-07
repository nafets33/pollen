#QueenBeeScheduler

# use scheduler to run cron jobs
import time
import datetime
# import subprocess
import schedule
import sys
import argparse
from QueenWorkerCrypto import queen_workerbee_coins
from QueenWorkerBees import queen_workerbees

def createParser():
    parser = argparse.ArgumentParser()
    parser.add_argument ('-qcp', default="scheduler")
    parser.add_argument ('-prod', default='false')
    parser.add_argument ('-adhoc', default='false')
    return parser

parser = createParser()
namespace = parser.parse_args()
adhoc_run = namespace.adhoc

def call_job():
    print("I'm Awake!: ", datetime.datetime.now().strftime("%A, %d. %B %Y %I:%M%p"))
    # subprocess.call("QueenWorkerCrypto.py", shell=True)
    queen_workerbee_coins()



schedule.every().day.at("07:00").do(call_job)
print("HeartBeat Turns on at 7AM")

if adhoc_run == 'true':
    print("running adhoc")
    call_job()

while True:
    schedule.run_pending()
    time.sleep(1)