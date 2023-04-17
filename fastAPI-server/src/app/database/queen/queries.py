#find and read the pkl file in the folder.

import pandas as pd
import random
from helpers.utils import ReadPickleData, find_folder, db_folder_path


def load_queen_pkl(username, prod):
  print(db_folder_path)
  if prod == False:
    queen_pkl_path = db_folder_path+"/"+find_folder(username)+'/queen_sandbox.pkl'
  else:
    queen_pkl_path = db_folder_path+"/"+find_folder(username)+'/queen.pkl'
  print(queen_pkl_path)
  queen_pkl = ReadPickleData(queen_pkl_path)
  return queen_pkl

def get_queen_orders_json(username, prod):
  queen_db = load_queen_pkl(username, prod)

  qo =queen_db['queen_orders']
  col_view = [
              "honey",
              "$honey",
              "symbol",
              "ticker_time_frame",
              "trigname",
              "datetime",
              "honey_time_in_profit",
              "filled_qty",
              "qty_available",
              "filled_avg_price",
              "limit_price",
              "cost_basis",
              "wave_amo",
              "status_q",
              "client_order_id",
              "origin_wave",
              "wave_at_creation",
              "power_up",
              "sell_reason",
              "exit_order_link",
              "queen_order_state",
              "order_rules",
              "order_trig_sell_stop",
              "side",
          ]

  df = pd.DataFrame(qo)

  json_data = df.to_json(orient='records')
  return json_data
