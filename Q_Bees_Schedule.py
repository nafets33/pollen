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

est = pytz.timezone("US/Eastern")


def createParser_scheduler():
    parser = argparse.ArgumentParser()
    parser.add_argument ('-adhoc', default='false')
    parser.add_argument ('-qcp', default="scheduler")
    parser.add_argument ('-prod', default='false')
    return parser



def call_job_workerbees(prod, bee_scheduler):
    print("I'm Awake!: ", datetime.datetime.now().strftime("%A, %d. %B %Y %I:%M%p"))
    print("I'm Awake! EST: ", datetime.datetime.now(est).strftime("%A, %d. %B %Y %I:%M%p"))
    # subprocess.call("QueenWorkerCrypto.py", shell=True)
    queen_workerbees(prod=prod, bee_scheduler=bee_scheduler)

# est = pytz.timezone("US/Eastern")
# schedule = Scheduler(tzinfo=est)

if __name__ == '__main__':
    parser = createParser_scheduler()
    namespace = parser.parse_args()
    adhoc_workers = namespace.adhoc
    prod = namespace.prod
    bee_scheduler = True

    schedule.every().day.at("14:32").do(call_job_workerbees(prod=prod, bee_scheduler=bee_scheduler)) ## UTC
    print("Workers Turns on at 9:32AM EST")

    if adhoc_workers == 'true':
        print("running adhoc")
        call_job_workerbees(prod=prod, bee_scheduler=bee_scheduler)

    while True:
        schedule.run_pending()
        time.sleep(1)