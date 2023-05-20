#find and read the pkl file in the folder.
import logging
import os
import json
import pandas as pd
import numpy as np
import random
from chess_piece.king import hive_master_root, ReadPickleData, PickleData, read_QUEENs__pollenstory, print_line_of_error
from chess_piece.queen_hive import init_logging, split_today_vs_prior, story_view, refresh_chess_board__revrec
from datetime import datetime, timedelta
from dotenv import load_dotenv
import pytz
import ipdb
est = pytz.timezone("US/Eastern")

main_root = hive_master_root() # os.getcwd()  # hive root
load_dotenv(os.path.join(main_root, ".env"))
db_root = os.path.join(main_root, "db")
init_logging(queens_chess_piece="fastapi_queen", db_root=db_root, prod=True)
# Helpers

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

def load_queen_App_pkl(username, prod):
  if prod == False:
    queen_pkl_path = username+'/queen_App__sandbox.pkl'
  else:
    queen_pkl_path = username+'/queen_App_.pkl'
  queen_pkl = ReadPickleData(queen_pkl_path)
  return queen_pkl

def load_queen_pkl(username, prod):
  if prod == False:
    queen_pkl_path = username+'/queen_sandbox.pkl'
  else:
    queen_pkl_path = username+'/queen.pkl'
  queen_pkl = ReadPickleData(queen_pkl_path)
  return queen_pkl

def load_POLLENSTORY_STORY_pkl(symbols, read_storybee, read_pollenstory, username, prod):
    try:
      ticker_db = read_QUEENs__pollenstory(
          symbols=symbols,
          read_storybee=read_storybee, 
          read_pollenstory=read_pollenstory,
      )    
      return ticker_db
    except Exception as e:
       print("pp", e)


# Router Calls
def app_buy_order_request(username, prod, selected_row, default_value): # index & wave_amount
  try:
    QUEEN_KING = load_queen_App_pkl(username, prod)
    # buy_package = create_AppRequest_package(request_name='buy_orders')
    ticker_time_frame = selected_row.get('star')
    macd_state = selected_row.get('macd_state')
    trigbee = f'buy_cross-0' if 'buy' in macd_state else f'sell_cross-0'

    wave_trigger = {ticker_time_frame: [trigbee]}
    order_dict = {'ticker': ticker_time_frame.split("_")[0],
    'ticker_time_frame': ticker_time_frame,
    'system': 'app',
    'wave_trigger': wave_trigger,
    'request_time': datetime.now(est),
    'app_requests_id' : f'{"theflash"}{"_"}{"waveup"}{"_app-request_id_"}{return_timestamp_string()}{datetime.now().microsecond}'
    'macd_state': trigbee,
    }

    QUEEN_KING['wave_triggers'].append(order_dict)
    PickleData(QUEEN_KING.get('source'), QUEEN_KING)
    
    # validate
    # execute_order(QUEEN=QUEEN, blessing=blessing, # order_vars
    #               side=blessing.get('order_side'),
    #               wave_amo=blessing.get('wave_amo'),
    #               order_type=blessing.get('order_type'),
    #               limit_price=blessing.get('limit_price'),
    #               trading_model=blessing.get('trading_model'),
    #               king_resp=True, 
    #               king_eval_order=False, 
    #               ticker=blessing.get('symbol'), 
    #               ticker_time_frame=blessing.get('ticker_time_frame_origin'), 
    #               trig=blessing.get('trigbee'), 
    #               portfolio=portfolio, 
    #               crypto=crypto)



    return True
  except Exception as e:
     print(e)
     logging.error(("fastapi", e))


def app_Sellorder_request(username, prod, selected_row, default_value):
  try:

    number_shares = default_value
    print(default_value)
    client_order_id = selected_row.get('client_order_id')
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
  except Exception as e:
     print("fapi e", e)
     print_line_of_error()

def get_queen_orders_json(username, prod):
  
  QUEEN = load_queen_pkl(username, prod)

  qo = QUEEN['queen_orders']
  if len(qo) == 1:
    print("init queen")
    return pd.DataFrame().to_json()

  df = pd.DataFrame(qo)
  df.reset_index(drop=True, inplace=True)
  df = df[df['client_order_id']!='init']
  # df["take_profit"] = df["order_rules"].apply(lambda x: x.get("take_profit"))
  # df['client_order_id'] = df.index
  df["money"] = pd.to_numeric(df["money"], errors='coerce')
  df["honey"] = pd.to_numeric(df["honey"], errors='coerce')
  df["honey"] = round(df["honey"] * 100,2)
  df["money"] = round(df["money"],0)
  # df['wave_state'] = df['assigned_wave'].apply(lambda x: x.get('macd_state'))
  # df["take_profit"] = df["order_rules"].get('take_profit')
  # df["close_order_today"] = df["order_rules"].get('close_order_today')
  
  df = df[df['queen_order_state'].isin(['running'])]
  # df = df[col_view]
  json_data = df.to_json(orient='records')
  return json_data

def get_ticker_data(symbols, prod):

  ticker_db = read_QUEENs__pollenstory(
      symbols=symbols,
      read_storybee=False, 
      read_pollenstory=True,
  )
  
  df = ticker_db.get('pollenstory')[f'{symbols[0]}_{"1Minute_1Day"}']
  df_ = df[['timestamp_est', 'close', 'vwap']]
  df_main = split_today_vs_prior(df_).get('df_today')
  # df_token = df_.tail(1)
  # df_token['timestamp_est'] = df_token['timestamp_est'] + timedelta(seconds=1)
  # df_token['close'] = df_token['close'] + random.randint(1,10)
  # df_main = pd.concat([df_main, df_token])


  json_data = df_main.to_json(orient='records')

  return json_data

def get_queen_messages_json(username, prod,):

  QUEEN = load_queen_pkl(username, prod)
  qo = QUEEN['queens_messages']

  df = pd.DataFrame(qo.items())
  df.reset_index(inplace=True)
  df = df.rename(columns={0: 'idx', 1: 'message'})
  df['message'] = df['message'].astype(str)
  # df = df.set_index('idx', drop=False)


  json_data = df.to_json(orient='records')
  return json_data


def get_queen_messages_logfile_json(username, log_file):

  # QUEEN = load_queen_pkl(username, prod)
  # log_dir = os.path.join(username, 'logs')
  # logs = os.listdir(log_dir)
  # logs = [i for i in logs if i.endswith(".log")]
  with open(log_file, 'r') as f:
      content = f.readlines()

  df = pd.DataFrame(content).reset_index()
  df = df.sort_index(ascending=False)
  df = df.rename(columns={'index': 'idx', 0: 'message'})
  df = df.tail(500)



  json_data = df.to_json(orient='records')
  return json_data


def queen_wavestories__get_macdwave(username, prod, symbols, api_key):
    if len(symbols) == 0:
       symbols=['SPY']
    # cust_Button("misc/waves.png", hoverText='', key='waves_icon', height=f'23px')
    # ipdb.set_trace()
    read_storybee=True, #kwargs.get('read_storybee')
    read_pollenstory=False, #kwargs.get('read_pollenstory')
    # st.image((os.path.join(hive_master_root(), "/custom_button/frontend/build/misc/waves.png")), width=33)
    # QUEEN_KING = load_queen_App_pkl(username, prod)
    QUEEN = load_queen_pkl(username, prod)
    # revrec = refresh_chess_board__revrec(acct_info, QUEEN, QUEEN_KING, active_queen_order_states=RUNNING_Orders, chess_board__revrec={}, revrec__ticker={}, revrec__stars={}) ## Setup Board
    revrec = QUEEN.get("revrec")
    ticker_db = load_POLLENSTORY_STORY_pkl(symbols, read_storybee, read_pollenstory, username, prod)
    # POLLENSTORY = ticker_db['pollenstory']
    STORY_bee = ticker_db['STORY_bee']
    try:
        df_main = pd.DataFrame()
        for symbol in symbols:
            story_views = story_view(STORY_bee=STORY_bee, ticker=symbol)

            df = story_views.get('df')
            df = df.set_index('star', drop=False)
            df.at[f'{symbol}_{"1Minute_1Day"}', 'sort'] = 1
            df.at[f'{symbol}_{"5Minute_5Day"}', 'sort'] = 2
            df.at[f'{symbol}_{"30Minute_1Month"}', 'sort'] = 3
            df.at[f'{symbol}_{"1Hour_3Month"}', 'sort'] = 4
            df.at[f'{symbol}_{"2Hour_6Month"}', 'sort'] = 5
            df.at[f'{symbol}_{"1Day_1Year"}', 'sort'] = 6
            df = df.sort_values('sort')

            if len(df_main) == 0:
               df_main = df
            else:
            #   ipdb.set_trace()
              df_main = pd.concat([df_main, df])

        df_main["maxprofit"] = pd.to_numeric(df_main["maxprofit"], errors='coerce')
        df_main["maxprofit"] = round(df_main["maxprofit"] * 100,2).fillna(0)
        
        if revrec is not None:
          for indx in df_main.index.tolist():
            df_main.at[indx, 'remaining_budget'] = revrec.get('df_stars').loc[indx]['remaining_budget']
            df_main.at[indx, 'remaining_budget_borrow'] = revrec.get('df_stars').loc[indx]['remaining_budget_borrow']

        json_data = df_main.to_json(orient='records')

        return json_data
    except Exception as e:
       print("mmm error", e)


def get_account_info(username, prod):
  QUEEN = load_queen_pkl(username, prod)
  acct_info = QUEEN['account_info']

  honey_text = "Honey: " + '%{:,.4f}'.format(((acct_info['portfolio_value'] - acct_info['last_equity']) / acct_info['portfolio_value']) *100)
  money_text = "Money: " + '${:,.2f}'.format(acct_info['portfolio_value'] - acct_info['last_equity'])

  return f'{honey_text} {money_text}'


def get_queens_mind(username, prod):

  QUEEN = load_queen_pkl(username, prod)
  # QUEEN['messages']

  return QUEEN['queens_messages']