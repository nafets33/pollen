#find and read the pkl file in the folder.

import pandas as pd
import random
from helpers.utils import ReadPickleData, find_folder, db_folder_path, PickleData
from datetime import datetime
import pytz
est = pytz.timezone("US/Eastern")

def return_timestamp_string(format="%Y-%m-%d %H-%M-%S %p {}".format(est), tz=est):
    return datetime.now(tz).strftime(format)

def create_AppRequest_package(request_name, archive_bucket=None, client_order_id=None):
    now = datetime.now(est)
    return {
    'client_order_id': client_order_id,
    'app_requests_id': f'{request_name}{"_app-request_id_"}{return_timestamp_string()}{now.microsecond}', 
    'request_name': request_name,
    'archive_bucket': archive_bucket,
    'request_timestamp': now,
    }


def app_Sellorder_request(username, prod, client_order_id, number_shares):
  QUEEN_KING = load_queen_App_pkl(username, prod)
  QUEEN = load_queen_pkl(username, prod)
  queen_order = QUEEN['queen_orders']
  df = queen_order.loc[client_order_id]
  # check against available_shares and validate amount
  # if number_shares > 0: # validate
  # print("Trying Request")
  qty_available = float(df.get('qty_available'))
  number_shares = qty_available if number_shares > qty_available else number_shares 
  status = None
  if len(df) > 0:
      current_requests = [i for i in QUEEN_KING['sell_orders'] if client_order_id in i.keys()]
      if len(current_requests) > 0:
          status = "You Already Requested Queen To Sell order, Refresh Orders to View latest Status"
      else:
          sell_package = create_AppRequest_package(request_name='sell_orders', client_order_id=client_order_id)
          sell_package['sell_qty'] = number_shares
          sell_package['side'] = 'sell'
          sell_package['type'] = 'market'
          QUEEN_KING['sell_orders'].append(sell_package)
          PickleData(QUEEN_KING.get('source'), QUEEN_KING)
          status = f'{client_order_id} : Selling Order Sent to Queen Please wait for Queen to process, Refresh Table'
  else:
      status = None

  return {'status': status}

def load_queen_App_pkl(username, prod):
  print(db_folder_path)
  if prod == False:
    queen_pkl_path = db_folder_path+"/"+find_folder(username)+'/queen_App__sandbox.pkl'
  else:
    queen_pkl_path = db_folder_path+"/"+find_folder(username)+'/queen_App_.pkl'
  print(queen_pkl_path)
  queen_pkl = ReadPickleData(queen_pkl_path)
  return queen_pkl

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

  qo = queen_db['queen_orders']
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
  
  df["$honey"] = pd.to_numeric(df["$honey"], errors='coerce')
  df["honey"] = pd.to_numeric(df["honey"], errors='coerce')
  df["honey"] = round(df["honey"] * 100,2)
  df["$honey"] = round(df["$honey"],0)
  
  df = df[df['queen_order_state'].isin(['running'])]
  df = df[col_view]
  json_data = df.to_json(orient='records')
  return json_data
