# QueenBee Workers
import argparse
import multiprocessing as mp
import os
import time
from datetime import datetime

import pytz

from chess_piece.king import hive_master_root, read_QUEEN
from chess_piece.queen_hive import return_market_hours, send_email
from chess_piece.workerbees import queen_workerbees

est = pytz.timezone("US/Eastern")


def workerbees_multiprocess_pool(
    prod, qcp_s, num_workers=3, reset_only=False
):  ## improvement send in reset_only into pool

    if num_workers > 10:
        print("Only Allowed 10 Processes to Run At Once")
        num_workers = 10

    send_email(subject=f"WorkerBees Online Production is {prod}_{num_workers}")

    def runpool(qcp_s):
        x = []

        pool = qcp_s

        print(pool)
        with mp.Pool(num_workers) as p:
            res = p.map(queen_workerbees, pool)
            x.append(res)
        # print(sum(x[0]))

    db_root = os.path.join(hive_master_root(), "db")
    queen_db = (
        os.path.join(db_root, "queen.pkl")
        if prod
        else os.path.join(db_root, "queen_sandbox.pkl")
    )
    # queen_db = master_swarm_QUEENBEE()

    pq = read_QUEEN(queen_db=queen_db, qcp_s=qcp_s)  # castle, bishop
    QUEENBEE = pq.get("QUEENBEE")
    queens_chess_pieces = pq.get("queens_chess_pieces")
    queens_master_tickers = pq.get("queens_master_tickers")

    runpool(qcp_s=queens_chess_pieces)


if __name__ == "__main__":

    def createParser_workerbees():
        parser = argparse.ArgumentParser()
        parser.add_argument("-prod", default=True)
        # parser.add_argument("-qcp_s", default="castle")

        return parser

    # script arguments
    parser = createParser_workerbees()
    namespace = parser.parse_args()
    # qcp_s = namespace.qcp_s  # 'castle', 'knight' 'queen'
    qcp_s = ["castle", "bishop", "knight", "pawn1", "pawn_5"]

    prod = True if str(namespace.prod).lower() == "true" else False
    while True:
        seconds_to_market_open = (
            datetime.now(est).replace(hour=9, minute=32, second=0) - datetime.now(est)
        ).total_seconds()
        # if datetime.now(est) > datetime.now(est).replace(hour=9, minute=32, second=0):
        #     print('zzz market closed')
        #     time.sleep(3)
        #     continue
        if seconds_to_market_open > 0:
            print(seconds_to_market_open, " ZZzzzZZ")
            time.sleep(3)
        else:
            break
    workerbees_multiprocess_pool(prod, qcp_s, num_workers=5, reset_only=False)
