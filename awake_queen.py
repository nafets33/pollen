import time
from datetime import datetime
import schedule
import os, sys
from chess_piece.king import hive_master_root
import argparse
import subprocess
import logging
# run = sys.argv[1]



def call_job_queen(prod, client_user, server):
    print("I'm Awake!: ", datetime.now().strftime("%A, %d. %B %Y %I:%M%p"))
    script_path = os.path.join(hive_master_root(), 'chess_piece/queen_bee.py')
    
    # Pass the arguments to queen_bee.py
    subprocess.call([
        'python', script_path,
        '-prod', str(prod).lower(),
        '-client_user', client_user,
        '-server', str(server).lower()
    ])

if __name__ == '__main__':
    # Create argument parser
    def createParser():
        parser = argparse.ArgumentParser(description="Run queen scheduler with arguments")
        parser.add_argument('-run', default='false', help="Run the script immediately")
        parser.add_argument('-prod', default='true', help="Run in production mode")
        parser.add_argument('-client_user', default='stefanstapinski@gmail.com', help="Specify client user")
        parser.add_argument('-server', default='false', help="Specify server for database access")
        return parser

    # Parse command-line arguments
    parser = createParser()
    namespace = parser.parse_args()
    
    # Convert arguments to appropriate types
    client_user = namespace.client_user
    prod = True if namespace.prod.lower() == 'true' else False
    run = True if namespace.run.lower() == 'true' else False
    server = True if namespace.server.lower() == 'true' else False

    if prod and client_user in ['stefanstapinski@gmail.com']:
        print("Running in production mode with client user:", client_user)

    if run:
        print("Ad-hoc run triggered")
        call_job_queen(prod, client_user)

    # Schedule job if not running ad-hoc
    run_time = "09:32"
    schedule.every().day.at(run_time).do(call_job_queen, prod, client_user, server)

    print(schedule.get_jobs())  # Print scheduled jobs

    while True:
        schedule.run_pending()
        time.sleep(1)
    