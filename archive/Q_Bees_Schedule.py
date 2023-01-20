#QueenBeeScheduler

# use scheduler to run cron jobs
import time
import datetime
import subprocess
import schedule
from scheduler import Scheduler
import pytz
import sys
import argparse
# from QueenWorkerCrypto import queen_workerbee_coins
from QueenWorkerBees import queen_workerbees
import pandas as pd

est = pytz.timezone("US/Eastern")

# scheduler = schedule.Scheduler(tzinfo=est)
schedule = Scheduler(tzinfo=est)

def createParser_scheduler():
    parser = argparse.ArgumentParser()
    parser.add_argument ('-adhoc', default='false')
    parser.add_argument ('-qcp', default="scheduler")
    parser.add_argument ('-prod', default='true')
    return parser



def call_job_workerbees(prod, bee_scheduler):
    print("I'm Awake!: ", datetime.datetime.now().strftime("%A, %d. %B %Y %I:%M%p"))
    print("I'm Awake! EST: ", datetime.datetime.now(est).strftime("%A, %d. %B %Y %I:%M%p"))
    # subprocess.call("QueenWorkerCrypto.py", shell=True)
    queen_workerbees(prod=prod, bee_scheduler=bee_scheduler)



if __name__ == '__main__':
    parser = createParser_scheduler()
    namespace = parser.parse_args()
    prod = True if namespace.prod.lower() == 'true' else False
    bee_scheduler = True

    # schedule.every().day.at("14:32").do(call_job_workerbees(prod=prod, bee_scheduler=bee_scheduler)) ## UTC
    # schedule.daily(datetime.time(hour=9, minute=32), call_job_workerbees(prod=prod, bee_scheduler=bee_scheduler))

    print("Workers Turns on at 9:32AM EST")

    if namespace.adhoc == 'true':
        print("running adhoc")
        call_job_workerbees(prod=prod, bee_scheduler=bee_scheduler)

    while True:
        s = datetime.datetime.now(est)
        mk_open = s.replace(hour=9, minute=31, second=1)
        if s > mk_open:
            call_job_workerbees(prod=prod, bee_scheduler=bee_scheduler)

        time.sleep(1)
