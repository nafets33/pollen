# QueenBee Workers
import argparse
import multiprocessing as mp
import os, sys
import time
from datetime import datetime

import pytz

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from chess_piece.king import master_swarm_QUEENBEE
from chess_piece.queen_hive import ReadPickleData, send_email
from chess_piece.workerbees import queen_workerbees
from chess_piece.pollen_db import PollenDatabase
est = pytz.timezone("US/Eastern")
pg_migration = os.environ.get('pg_migration')

def workerbees_multiprocess_pool(prod, qcp_s, num_workers=5, reset_only=False):  
    ## improvement send in reset_only into pool
    num_workers = len(qcp_s)
    
    # if num_workers > 10:
    #     print("Only Allowed 10 Processes to Run At Once")
    #     num_workers = 10

    send_email(subject=f"WorkerBees Online Production is {prod}_{num_workers}")

    def runpool(qcp_s):
        x = []

        pool = qcp_s

        print("pool: ", pool)
        with mp.Pool(num_workers) as p:
            res = p.map(queen_workerbees, pool)
            x.append(res)
        # print(sum(x[0]))


    runpool(qcp_s)


if __name__ == "__main__":

    def createParser_workerbees():
        parser = argparse.ArgumentParser()
        parser.add_argument("-prod", default=True)
        # parser.add_argument("-qcp_s", default="castle")

        return parser

    # script arguments
    parser = createParser_workerbees()
    namespace = parser.parse_args()
    prod = True if str(namespace.prod).lower() == "true" else False
    
    if pg_migration:
        table_name = 'db' if prod else 'db_sandbox'
        QUEENBEE = PollenDatabase.retrieve_data(table_name, 'QUEEN')
    else:
        QUEENBEE = ReadPickleData(master_swarm_QUEENBEE(prod=prod))
    
    workerbees = QUEENBEE['workerbees']
    qcp_s = []
    for qcp, va in workerbees.items():
        tickers = va.get('tickers')
        if tickers:
            qcp_s.append(qcp)
    print(qcp_s)
    while True:
        seconds_to_market_open = (datetime.now(est).replace(hour=9, minute=32, second=0) - datetime.now(est)).total_seconds()

        if seconds_to_market_open > 0:
            print(seconds_to_market_open, " ZZzzzZZ")
            time.sleep(3)
        else:
            break
    workerbees_multiprocess_pool(prod, qcp_s, num_workers=5, reset_only=False)
