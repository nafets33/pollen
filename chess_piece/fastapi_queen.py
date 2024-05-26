#find and read the pkl file in the folder.
import logging
import os
import json
import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
from dotenv import load_dotenv
import pytz
import ipdb
import time
import sys
from chess_piece.king import (return_QUEENs__symbols_data, kingdom__global_vars, main_index_tickers, streamlit_config_colors, hive_master_root, load_local_json, save_json, ReadPickleData, PickleData, read_QUEENs__pollenstory, print_line_of_error, master_swarm_KING)
from chess_piece.queen_hive import (return_symbol_from_ttf, 
                                    trigger_bees, 
                                    stars, 
                                    init_logging, 
                                    split_today_vs_prior, 
                                    kings_order_rules, 
                                    buy_button_dict_items,
                                    order_vars__queen_order_items,
                                    find_symbol,
                                    power_amo,
                                    init_queenbee,
                                    return_trading_model_trigbee,
                                    init_charlie_bee,
                                    ttf_grid_names,
                                    ttf_grid_names_list,
                                    sell_button_dict_items,
                                    wave_buy__var_items,
                                    star_names,
                                    refresh_chess_board__revrec)
from chess_piece.queen_bee import execute_order, sell_order__var_items
import copy

pd.options.mode.chained_assignment = None  # default='warn' Set copy warning

est = pytz.timezone("US/Eastern")

main_root = hive_master_root() # os.getcwd()  # hive root
load_dotenv(os.path.join(main_root, ".env"))
db_root = os.path.join(main_root, "db")

init_logging(queens_chess_piece="fastapi_queen", db_root=db_root, prod=True)

 ###### Helpers UTILS

# WORKERBEE Update all ROUTERS to use fun resp return vs function
def grid_row_button_resp(status='success', description='success', message_type='fade', close_modal=True, color_text='red', error=False):
    return {'status': status, # success
            'description': description,
            'error': error,
            'data':{
                'close_modal': close_modal, # T/F
                'color_text': color_text, #? test if it works
                'message_type': message_type # click / fade
            },
            }

# KORS
def return_trading_model_kors(QUEEN_KING, star__wave, current_wave_blocktime='morning_9-11'):
  star, wave_state = star__wave.split("__")
  symbol, tframe, tperoid = star.split("_")
  star = f'{tframe}_{tperoid}'
  trigbee = "buy_cross-0" if 'buy' in wave_state else 'sell_cross-0'
  trading_model = QUEEN_KING['king_controls_queen']['symbols_stars_TradingModel'][symbol]['stars_kings_order_rules'][star]['trigbees'][trigbee].get(current_wave_blocktime)
  return trading_model

def return_trading_model_kors_v2(QUEEN_KING, symbol='SPY', trigbee='buy_cross-0', star='1Day_1Year', current_wave_blocktime='morning_9-11'):
  try:
    QK_tradingModels = QUEEN_KING['king_controls_queen']['symbols_stars_TradingModel']
    if symbol in QK_tradingModels.keys():
      trading_model = QUEEN_KING['king_controls_queen']['symbols_stars_TradingModel'][symbol]['stars_kings_order_rules'][star]['trigbees'][trigbee].get(current_wave_blocktime)
    else:
      trading_model = QUEEN_KING['king_controls_queen']['symbols_stars_TradingModel']['SPY']['stars_kings_order_rules'][star]['trigbees'][trigbee].get(current_wave_blocktime)
    return trading_model
  except Exception as e:
     print_line_of_error("wwwwtf")
     return {}

# the_type = get_type_by_name('float')
def add_priorday_tic_value(df, story_indexes=1):
  split_day = split_today_vs_prior(df)
  df_p = split_day.get('df_prior')
  df = split_day.get('df_today')
  
  df_pz = df_p.tail(story_indexes)
  # for idx in len(df_pz):
  prior_tic = df.iloc[0].get('timestamp_est').replace(minute=29)
  
  df_pz.at[df_pz.index[0], 'timestamp_est'] = prior_tic

  df = pd.concat([df_pz, df])

  return df

def validate_kors_valueType(newvalue, current_value):

  try:
    if type(newvalue) == type(current_value):
        # print("update kor value", kor, newvalue)
        return newvalue
    elif newvalue:
      # print("try to update type", newvalue)
      if type(current_value) == datetime:
        newvalue = parse_date(newvalue)
        if newvalue:
            return newvalue
        else:
            return 'error'
      else:
        correct_type = type(current_value)
        return correct_type(newvalue)
    else:
       return current_value
  except Exception as e:
    print(e)
    print("unable to update type")
    return 'error'

def generate_shade(number_variable, base_color=False, wave=False, shade_num_var=300):
    try:
      # Validate the input range
      red = '#FBC0C0'
      green = '#C0FBD3'
      blue = '#64D2EC'
      if wave:
        m_wave, m_num = number_variable.split("_")
        base_color = green if 'buy' in m_wave else red
        number_variable = int(m_num.split("-")[-1])
        # number_variable = 33
      else:
        # print(number_variable)

        base_color = green if (number_variable) > 0 else red
        number_variable = round(abs(number_variable * 100))
        shade_num_var = shade_num_var * 3
      # if number_variable < -100 or number_variable > 100:
      #     raise ValueError("Number variable must be between -100 and 100")

      if base_color:
          pass
      else:
        base_color = green if number_variable > 0 else red

      # Convert base_color to RGB values
      base_color = base_color.lstrip('#')
      base_color_rgb = tuple(int(base_color[i:i+2], 16) for i in (0, 2, 4))

      # Calculate shade amount based on number_variable
      shade_amount = abs(number_variable) / shade_num_var  # Map to range [0, 1]

      # Calculate shaded RGB values
      shaded_rgb = tuple(int(base_color_comp * (1 - shade_amount)) for base_color_comp in base_color_rgb)

      # Convert RGB to hex color code
      shaded_color = "#{:02X}{:02X}{:02X}".format(*shaded_rgb)

      return shaded_color
    except Exception as e:
      print_line_of_error(e)



def generate_shade_story(number_variable, base_color=False, wave=False, shade_num_var=300):
    try:
      # Validate the input range
      red = '#FBC0C0'
      green = '#C0FBD3'
      blue = '#64D2EC'
      if wave:
        m_wave, m_num = number_variable.split("_")
        base_color = green if 'buy' in m_wave else red
        number_variable = int(m_num.split("-")[-1])
        # number_variable = 33
      else:
        # print(number_variable)

        base_color = green if (number_variable) > 0 else red
        number_variable = round(abs(number_variable * 100))
        shade_num_var = shade_num_var * 3
      # if number_variable < -100 or number_variable > 100:
      #     raise ValueError("Number variable must be between -100 and 100")

      if base_color:
          pass
      else:
        base_color = green if number_variable > 0 else red

      # Convert base_color to RGB values
      base_color = base_color.lstrip('#')
      base_color_rgb = tuple(int(base_color[i:i+2], 16) for i in (0, 2, 4))

      # Calculate shade amount based on number_variable
      shade_amount = abs(number_variable) / shade_num_var  # Map to range [0, 1]

      # Calculate shaded RGB values
      shaded_rgb = tuple(int(base_color_comp * (1 - shade_amount)) for base_color_comp in base_color_rgb)

      # Convert RGB to hex color code
      shaded_color = "#{:02X}{:02X}{:02X}".format(*shaded_rgb)

      return shaded_color
    except Exception as e:
      print_line_of_error(e)

def filter_gridby_timeFrame_view(df, toggle_view_selection, grid=False, ttf_namefilter=True, wave_state_filter=True):
    try:
      ttf_gridnames = [i.lower() for i in ttf_grid_names_list()]
      if grid == 'wave':
        if 'ttf_grid_name' not in df.columns:
          df['ttf_grid_name'] = df['ticker_time_frame'].apply(lambda x: ttf_grid_names(x, symbol=True))
      else:
        if 'ttf_grid_name' not in df.columns:
          df['ttf_grid_name'] = df['ticker_time_frame'].apply(lambda x: ttf_grid_names(x, symbol=False))
      
      if ttf_namefilter:
        if toggle_view_selection.lower() in ttf_gridnames:
          df = df[df['ttf_grid_name'].str.contains(toggle_view_selection)]
        if toggle_view_selection.lower() == 'close today':
          df = df[(df['order_rules'].apply(lambda x: x.get('close_order_today') == True))]

      
      if wave_state_filter:
        trigname = 'trigname' if 'trigname' in df.columns else 'macd_state'
        if toggle_view_selection.lower() == 'buys':
            df = df[df[trigname].str.contains('buy')]
        elif toggle_view_selection.lower() == 'sells':
            df = df[~df[trigname].str.contains('buy')]
      
      return df
    except Exception as e:
       print_line_of_error(e)

def return_timestamp_string(format="%Y-%m-%d %H-%M-%S %p {}".format(est), tz=est):
    return datetime.now(tz).strftime(format)

def create_AppRequest_package(request_name, archive_bucket=None, client_order_id=None):
    now = datetime.now(est)
    return {
    'client_order_id': client_order_id,
    'app_requests_id': f'{request_name}_{client_order_id}{"_app-request_id_"}{return_timestamp_string()}{now.microsecond}', 
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
  if prod:
    QUEEN = ReadPickleData(username + '/queen.pkl')
  else:
    QUEEN = ReadPickleData(username + '/queen_sandbox.pkl')
  
  return QUEEN

def load_queen_order_pkl(username, prod):
  if prod:
    ORDERS = ReadPickleData(username + '/queen_Orders_.pkl')
  else:
    ORDERS = ReadPickleData(username + '/queen_Orders__sandbox.pkl')
  
  return ORDERS

def load_revrec_pkl(username, prod):
  if prod == False:
    queen_pkl_path = username+'/queen_revrec_sandbox.pkl'
  else:
    queen_pkl_path = username+'/queen_revrec.pkl'
  queen_pkl = ReadPickleData(queen_pkl_path)
  return queen_pkl

def parse_date(date_str):
    date_formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y/%m/%d %H:%M:%S",
        "%m-%d-%Y %H:%M:%S",
        "%m/%d/%Y %H:%M:%S",
        "%Y-%m-%d",
        "%Y/%m/%d",
        "%m-%d-%Y",
        "%m/%d/%Y",
    ]
    
    for format_str in date_formats:
        try:
            parsed_date = datetime.strptime(date_str, format_str)
            return parsed_date
        except ValueError:
            pass
        
    return None

####### Router Calls

def get_waveview_state_for_ttf(revrec, wave_view_name, ttf):
   df_wave = revrec.get('waveview').loc[ttf].get(wave_view_name)
   return df_wave.loc[ttf].get('macd_state')

def validate_return_kors(king_order_rules, kors):
  for rule, value in kors.items():
    if rule in ['wave_amo', 'close_order_today', 'take_profit', 'sell_out', 'sell_trigbee_trigger', 'sell_trigbee_trigger_timeduration']: # validated items to add orules

      if rule == 'wave_amo':
        if type(value) != float:
          value = float(value)
      elif rule == 'close_order_today':
          if type(value) != bool:
            print("ERRROR BOOL CLOSE ORDER")
            continue
      elif rule == 'take_profit':
          if type(value) != float:
            value = float(value)
      elif rule == 'sell_out':
          if type(value) != float:
            value = float(value)
      elif rule == 'sell_trigbee_trigger':
          if type(value) != bool: ## BOOLS are already handled by frontend
            print("ERRROR BOOL CLOSE ORDER")
            continue
      elif rule == 'sell_trigbee_trigger_timeduration':
          if type(value) != int:
            value = int(value)
      
      king_order_rules.update({rule: value})

  return king_order_rules
    

def return_startime_from_ttf(ticker_time_frame):
   t,tt,f = ticker_time_frame.split("_")
   return f'{tt}_{f}'

def app_buy_order_request(client_user, prod, selected_row, kors, ready_buy=False, story=False): # index & wave_amount
  try:

    qb = init_queenbee(client_user=client_user, prod=prod, queen=True, queen_king=True, api=True, revrec=False)
    QUEEN = qb.get('QUEEN')
    QUEEN_KING = qb.get('QUEEN_KING')
    api = qb.get('api')
    revrec = QUEEN.get('revrec') # qb.get('queen_revrec')

    buy_package = create_AppRequest_package(request_name='buy_orders')
    buy_package.update({'buy_order': {}})
    blessing={} #{i: '': for i in []}, # order_vars
    
    # Trading Model
    symbol=selected_row.get('symbol')
    if story:
      # star_time=star_names(kors.get('star_list')[0])
      # ticker_time_frame = f'{symbol}_{star_time}'
      trigbee = 'buy_cross-0'
      ticker_time_frame = kors.get('star')
      star_time = return_startime_from_ttf(ticker_time_frame)
      wave_blocktime = revrec.get('waveview').loc[ticker_time_frame].get('wave_blocktime')
    else:
      star_time = selected_row.get('star_time')
      ticker_time_frame = selected_row.get('ticker_time_frame')
      trigbee = selected_row.get('macd_state')
      wave_blocktime = selected_row.get('wave_blocktime')

    trading_model = QUEEN_KING['king_controls_queen']['symbols_stars_TradingModel'].get(symbol) # main symbol for Model (SPY)
    
    # Ensure Symbol for Inverse Indexes
    main_indexes = main_index_tickers()
    symbol = find_symbol(main_indexes, symbol, trading_model, trigbee).get('ticker') # FOR BUYING
    
    # Ensure Trading Model TrigName
    tm_trig = return_trading_model_trigbee(tm_trig=trigbee, trig_wave_length=trigbee.split("-")[-1])
    if ready_buy:
      tm_trig = f'sell_cross-0' if 'buy' in tm_trig else f'buy_cross-0'

    # Copy TM
    king_order_rules = copy.deepcopy(trading_model['stars_kings_order_rules'][star_time]['trigbees'][tm_trig][wave_blocktime])
    
    # Other Misc
    crypto=False
    maker_middle = False
    current_wave = {} # revrec['waveview'].get('current_wave')
    current_macd_cross__wave = {}
    power_up_amo = power_amo()
    borrowed_funds = True # USER INITIATE
    borrow_qty = False ## DEPRECIATE

    kors = validate_return_kors(king_order_rules, kors)
    wave_amo = kors.get('wave_amo')

    order_vars = order_vars__queen_order_items(trading_model=trading_model.get('theme'), 
                                                king_order_rules=kors, 
                                                order_side='buy', 
                                                wave_amo=wave_amo, 
                                                maker_middle=maker_middle, 
                                                origin_wave=current_wave, 
                                                power_up_rangers=power_up_amo, 
                                                ticker_time_frame_origin=ticker_time_frame, 
                                                double_down_trade=True, 
                                                wave_at_creation=current_macd_cross__wave,
                                                symbol=symbol,
                                                trigbee=trigbee,
                                                tm_trig=tm_trig,
                                                borrowed_funds=borrowed_funds,
                                                ready_buy=ready_buy,
                                                assigned_wave=current_macd_cross__wave,
                                                borrow_qty=borrow_qty,
                                                )
    blessing = order_vars

    exx = execute_order(api=api, QUEEN=QUEEN, blessing=blessing,
                    side=blessing.get('order_side'),
                    wave_amo=blessing.get('wave_amo'),
                    order_type=blessing.get('order_type'),
                    limit_price=blessing.get('limit_price'),
                    trading_model=blessing.get('trading_model'),
                    king_resp=True, 
                    king_eval_order=False, 
                    ticker=blessing.get('symbol'), 
                    ticker_time_frame=blessing.get('ticker_time_frame_origin'), 
                    trig=blessing.get('trigbee'), 
                    crypto=crypto)
    if exx.get('executed'):
      print("APP EXX Order")

      buy_package.update({'new_queen_order_df': exx.get('new_queen_order_df')})   

      # save
      QUEEN_KING['buy_orders'].append(buy_package)
      PickleData(QUEEN_KING.get('source'), QUEEN_KING)
      print("SAVED ORDER TO QK")
      return {'status': True, 'msg': f'{symbol} purchased'}
    else:
       print("Ex Failed")
       return {'status': False, 'msg': "Ex Failed"}
    
  except Exception as e:
     y=print_line_of_error(f"fastapi buy button failed {e}")
     logging.error(("fastapi", e))
     return {'status': False, 'msg': str(y)}


def app_buy_wave_order_request(username, prod, selected_row, default_value=False, ready_buy=False, x_buy=False, order_rules=False): # index & wave_amount
  try:
    QUEEN_KING = load_queen_App_pkl(username, prod)
    # buy_package = create_AppRequest_package(request_name='buy_orders')
    ticker_time_frame = selected_row.get('ticker_time_frame')
    macd_state = selected_row.get('macd_state')
    # trigbee = f'buy_cross-0' if 'buy' in macd_state else f'sell_cross-0'
    trigbee = macd_state
    if default_value:
       print(default_value)
    
    wave_trigger = {ticker_time_frame: [trigbee]}
    order_dict = wave_buy__var_items(ticker_time_frame, trigbee, macd_state, ready_buy, x_buy, order_rules)

    QUEEN_KING['wave_triggers'].append(order_dict)
    PickleData(QUEEN_KING.get('source'), QUEEN_KING)
    

    return True
  except Exception as e:
     print(e)
     logging.error(("fastapi", e))


def process_clean_on_QK_requests(QUEEN, QUEEN_KING, request_name='sell_orders'): #WORKERBEE add in somewhere?
    try:
      app_requests__bucket = 'app_requests__bucket'
      oglen = len(QUEEN_KING['sell_orders'])
      QUEEN_KING['sell_orders'] = [i for i in QUEEN_KING['sell_orders'] if i.get('app_requests_id') not in QUEEN[app_requests__bucket]]
      newlen = len(QUEEN_KING['sell_orders'])
      if oglen != newlen:
        print(f"{request_name} requests cleaned")

      return True
    except Exception as e:
       print_line_of_error("sell orders clean failed")
       return False


def app_Sellorder_request(client_user, username, prod, selected_row, default_value):
  try:
    # WORKERBEE validate to ensure number of shares available to SELL as user can click twice
    number_shares = int(default_value.get('sell_qty'))
    client_order_id = selected_row.get('client_order_id')
    symbol = selected_row.get('symbol')

    QUEEN_KING = load_queen_App_pkl(username, prod)
    ORDERS = init_queenbee(client_user=client_user, prod=prod, orders=True).get('ORDERS')
    if type(ORDERS) != dict:
      print("NO ORDERS")
      return pd.DataFrame().to_json()
    queen_order = ORDERS['queen_orders']
    
    if client_order_id:
      # VALIDATE check against available_shares and validate amount
      df = queen_order.loc[client_order_id]
      qty_available = float(df.get('qty_available'))
      number_shares = qty_available if number_shares > qty_available else number_shares 
      selected_client_order_ids = {client_order_id: number_shares}
    else:
       print("Find Available Orders")
       selected_client_order_ids = {}
       orders_avial = queen_order[queen_order['symbol']==symbol]
       if len(orders_avial) > 0:
          # sort by borrowed = True
          # sort by time purchased?
          orders_avial = orders_avial.sort_values(by=['borrowed_funds', 'datetime'], ascending=[False, True])
          cumulative_sum = 0

          # Iterate over DataFrame rows
          for client_order_id, row in orders_avial.iterrows():
              # Add qty_available to cumulative sum
              cumulative_sum += row['qty_available']              
              # Check if cumulative sum exceeds or equals numshares
              if cumulative_sum >= number_shares:
                  # Calculate remaining qty_available to satisfy numshares
                  remaining_qty = number_shares - (cumulative_sum - row['qty_available'])
                  selected_client_order_ids[client_order_id] = remaining_qty
                  break
              else:
                  selected_client_order_ids[client_order_id] = row['qty_available']

    status = ''
    save=False
    for client_order_id, number_shares in selected_client_order_ids.items():
      if client_order_id in queen_order.index:
        # Sell Order
        df = queen_order.loc[client_order_id]
        sell_package = create_AppRequest_package(request_name='sell_orders', client_order_id=client_order_id)
        sell_package['sell_qty'] = number_shares
        sell_package['side'] = 'sell'
        sell_package['type'] = 'market'
        QUEEN_KING['sell_orders'].append(sell_package)
        save=True
        if status:
          status = status + f' __ {client_order_id} : Selling {number_shares}'
        else:
           status = f'{client_order_id} : Selling {number_shares}'
    if save:
       PickleData(QUEEN_KING.get('source'), QUEEN_KING)
       print("QK Saved Sell Orders")

    # if len(df) > 0:
    #     current_requests = [i for i in QUEEN_KING['sell_orders'] if client_order_id in i.keys()]
    #     if len(current_requests) > 0:
    #         status = "You Already Requested Queen To Sell order, Refresh Orders to View latest Status"
    #     else:
    #         sell_package = create_AppRequest_package(request_name='sell_orders', client_order_id=client_order_id)
    #         sell_package['sell_qty'] = number_shares
    #         sell_package['side'] = 'sell'
    #         sell_package['type'] = 'market'
    #         QUEEN_KING['sell_orders'].append(sell_package)
    #         PickleData(QUEEN_KING.get('source'), QUEEN_KING)
    #         status = f'{client_order_id} : Selling {number_shares} share, Please wait for QueenBot to process'
    # else:
    #     status = "Nothing to Sell"
    print(status)
    return grid_row_button_resp(description=status)
  except Exception as e:
     print("fapi e", e)
     print_line_of_error()
     return {'status': 'error', 'error': e}


def app_archive_queen_order(username, prod, selected_row, default_value):
    # number_shares = default_value
    # print(default_value)
    queen_order = selected_row
    client_order_id = queen_order.get('client_order_id')
    QUEEN_KING = load_queen_App_pkl(username, prod)
    order_update_package = create_AppRequest_package(request_name='update_queen_order', client_order_id=client_order_id)
    order_update_package['queen_order_updates'] = {client_order_id: {'queen_order_state': 'archived'}}
    QUEEN_KING['update_queen_order'].append(order_update_package)
    PickleData(QUEEN_KING.get('source'), QUEEN_KING)
    return True


def get_type_by_name(type_name):
    return getattr(__builtins__, type_name)




def app_queen_order_update_order_rules(client_user, username, prod, selected_row, default_value):
    try:
      current_kors = kings_order_rules()
      queen_order = selected_row
      client_order_id = queen_order.get('client_order_id')
      # number_shares = default_value
      QUEEN_KING = load_queen_App_pkl(username, prod)
      order_update_package = create_AppRequest_package(request_name='update_order_rules', client_order_id=client_order_id)
      order_update_package['update_order_rules'] = {}
      
      update_dict = {}
      kors = queen_order.get('order_rules')
      for kor, newvalue in default_value.items():
        if kor in kors.keys():
          if newvalue == kors[kor]:
            #  print("no update")
            continue
        current_value = current_kors[kor] # if current_value in current_kors else None
        newvalue = validate_kors_valueType(newvalue, current_value)
        if newvalue == 'error':
          print('validation failed')
          return {'status': False, 'description': f"date time conversion failed try mm/dd/yyyy"}
        else:
            update_dict[kor] = newvalue
        
      if update_dict:
        order_update_package['update_order_rules'].update({client_order_id: update_dict})
        print(order_update_package['update_order_rules'])
      
        QUEEN_KING['update_order_rules'].append(order_update_package)
        PickleData(QUEEN_KING.get('source'), QUEEN_KING)
        return {'status': True, 'description': 'kors updates'}
      else:
        msg = ("no updates to kors")
        return {'status': False, 'description': msg}
         
    except Exception as e:
       print_line_of_error(e)
       return {'status': False, 'description': str(e)}

## MAIN GRIDS

def update_queenking_chessboard(username, prod, selected_row):
   QK = load_queen_App_pkl(username, prod)
  #  df = pd.DataFrame(new_data).T
   if 'ticker_revrec_allocation_mapping' in QK['king_controls_queen'].keys():
      # update_dict = dict(zip(df['symbol'], df['']))
      updated_dict = {selected_row.get('symbol'): selected_row.get('ticker_buying_power')}
      print(updated_dict)
   status = 'updated'
   return grid_row_button_resp(description=status)

def get_queen_orders_json(client_user, username, prod, toggle_view_selection):
  
  try:
      if toggle_view_selection.lower() == 'queen':
          ORDERS = init_queenbee(client_user, prod, queen=True).get('QUEEN')
      else:
          ORDERS = init_queenbee(client_user, prod, orders=True).get('ORDERS')


      if type(ORDERS) != dict:
        print("NO ORDERS")
        return pd.DataFrame().to_json()

      df = ORDERS['queen_orders']

      if type(df) != pd.core.frame.DataFrame:
        return pd.DataFrame().to_json()

      if len(df) == 1:
        print("init queen")
        return pd.DataFrame().to_json()

      # Colors
      k_colors = streamlit_config_colors()
      default_text_color = k_colors['default_text_color'] # = '#59490A'
      default_font = k_colors['default_font'] # = "sans serif"
      default_yellow_color = k_colors['default_yellow_color'] # = '#C5B743'

      sell_options = sell_button_dict_items()
      df['sell_option'] = [sell_options for _ in range(df.shape[0])]

      df = df[df['client_order_id']!='init']
      df = df.fillna('000')
      df = df[df['ticker_time_frame']!='000'] ## who are you?? WORKERBEE
      # print(df_)
      df['ttf_symbol'] = df['ticker_time_frame'].apply(lambda x: return_symbol_from_ttf(x))

      df["money"] = pd.to_numeric(df["money"], errors='coerce')
      df["honey"] = pd.to_numeric(df["honey"], errors='coerce')
      df["honey"] = round(df["honey"] * 100,2)
      df["money"] = round(df["money"],0)
      # df['color_row'] = np.where(df['honey'] > 0, default_yellow_color, "#ACE5FB")
      df['color_row_text'] = np.where(df['honey'] > 0, default_text_color, default_text_color)
      df['color_row'] = df['honey'].apply(lambda x: generate_shade(x, wave=False))
      df['sell_reason'] = df['sell_reason'].astype(str)
      df['time_frame'] = df['ticker_time_frame'].apply(lambda x: ttf_grid_names(x, symbol=True))
  
      df = filter_gridby_timeFrame_view(df, toggle_view_selection)
      
      if toggle_view_selection == 'today':
         df = split_today_vs_prior(df, timestamp='datetime').get('df_today')
      # else:
      #   qos_view=['running', 'running_close', 'running_open']
      #   df = df[df['queen_order_state'].isin(qos_view)]

      for ttf in df.index:
        symbol = df.at[ttf, 'symbol']
        sell_qty = df.at[ttf, 'qty_available']
        sell_option = sell_button_dict_items(symbol, sell_qty)
        df.at[ttf, 'sell_option'] = sell_option

      # sort
      sort_colname = 'cost_basis_current'
      df = df.sort_values(sort_colname, ascending=False)
      
      # # Totals Index
      df.loc['Total', 'money'] = df['money'].sum()
      df.loc['Total', 'honey'] = df['honey'].sum()
      # df.loc['Total', 'datetime'] = ''
      df.loc['Total', 'cost_basis'] = df['cost_basis'].sum()
      df.loc['Total', 'cost_basis_current'] = df['cost_basis_current'].sum()
      newIndex=['Total']+[ind for ind in df.index if ind!='Total']
      df=df.reindex(index=newIndex)

      json_data = df.to_json(orient='records')
      return json_data
  except Exception as e:
    print('hey now')
    print_line_of_error()


def queen_wavestories__get_macdwave(client_user, prod, symbols, toggle_view_selection, return_type='waves', revrec=None):
    def update_col_number_format(df, float_cols=['trinity', 'current_profit', 'maxprofit', 'current_profit_deviation']):
      for col in df.columns:
        # print(type(df_storygauge.iloc[-1].get(col)))
        if type(df.iloc[-1].get(col)) == np.float64:
            if col in float_cols:
              df[col] = round(df[col] * 100,2)
            else:
                df[col] = round(df[col],2)
      return df
    
    # try:
    if toggle_view_selection.lower() == 'king':
      king_G = kingdom__global_vars()
      qb = init_queenbee(client_user=client_user, prod=prod, queen=True, queen_king=True, revrec=True)
      QUEEN = qb.get('QUEEN')
      QUEEN_KING = qb.get('QUEEN_KING')
      STORY_bee = return_QUEENs__symbols_data(QUEEN=QUEEN, QUEEN_KING=QUEEN_KING, swarmQueen=False, read_pollenstory=False).get('STORY_bee')
      revrec = refresh_chess_board__revrec(QUEEN['account_info'], QUEEN, QUEEN_KING, STORY_bee, king_G.get('active_queen_order_states'), chess_board__revrec={}, revrec__ticker={}, revrec__stars={}) ## Setup Board
    else:
      qb = init_queenbee(client_user, prod, revrec=True, queen_king=True)
      revrec = qb.get('revrec')
      QUEEN_KING = qb.get('QUEEN_KING')

    if type(revrec.get('waveview')) != pd.core.frame.DataFrame:
      print(f'rr not df null, {revrec}')
      return pd.DataFrame().to_json()


    if len(symbols) == 0:
      symbols=['SPY']

    k_colors = streamlit_config_colors()
    default_text_color = k_colors['default_text_color'] # = '#59490A'
    default_font = k_colors['default_font'] # = "sans serif"
    default_yellow_color = k_colors['default_yellow_color'] # = '#C5B743'

    waveview = revrec.get('waveview')
    waveview['sell_alloc_deploy'] =  np.where((waveview['macd_state'].str.contains("buy")) & (waveview['allocation_deploy'] < 0), round(waveview['allocation_deploy']), 0)
    waveview['sellbuy_alloc_deploy'] =  np.where((waveview['macd_state'].str.contains("sell")) & (waveview['allocation_deploy'] > 0), round(waveview['allocation_deploy']), 0)
    waveview['sell_alloc_deploy'] = waveview['sell_alloc_deploy'] + waveview['sellbuy_alloc_deploy']
    
    waveview['buy_alloc_deploy'] =  np.where((waveview['macd_state'].str.contains("buy")) & (waveview['allocation_deploy'] > 0), round((waveview['allocation_deploy'])), 0)
    waveview['buysell_alloc_deploy'] =  np.where((waveview['macd_state'].str.contains("sell")) & (waveview['allocation_deploy'] < 0), round(abs(waveview['allocation_deploy'])), 0) 
    waveview['buy_alloc_deploy'] = waveview['buy_alloc_deploy'] + waveview['buysell_alloc_deploy']

    
    def return_waveview_fillers(waveview):
      df = waveview

      # sell_options = sell_button_dict_items()
      # df['sell_option'] = [sell_options for _ in range(df.shape[0])]
      kors_dict = buy_button_dict_items()
      df['kors'] = [kors_dict for _ in range(df.shape[0])]
      df['kors_key'] = df["ticker_time_frame"] +  "__" + df['macd_state']
      df['trading_model_kors'] = df['kors_key'].apply(lambda x: return_trading_model_kors(QUEEN_KING, star__wave=x))
      for ttf in df.index.tolist():
        # try:
        remaining_budget = df.at[ttf, 'remaining_budget'].astype(float)
        remaining_budget_borrow = df.at[ttf, 'remaining_budget_borrow'].astype(float)
        # print(type(remaining_budget))
        if type(remaining_budget) is np.float64:
            pass
        else:
            print(ttf, "OBBBBJ", remaining_budget)
            continue
        remaining_budget = round(df.at[ttf, 'remaining_budget'], 2)
        
        # get kor variables
        take_profit = df.at[ttf, "trading_model_kors"].get('take_profit')
        sell_out = df.at[ttf, "trading_model_kors"].get('sell_out')
        close_order_today = df.at[ttf, "trading_model_kors"].get('close_order_today')
        sell_trigbee_trigger_timeduration = df.at[ttf, "trading_model_kors"].get('sell_trigbee_trigger_timeduration')
        
        margin = ''
        if remaining_budget <0 and (remaining_budget_borrow + remaining_budget) > 0:
          margin = "Margin"
          remaining_budget = round((remaining_budget_borrow + remaining_budget))
          
          if remaining_budget <0:
              remaining_budget == 0
        
        reverse_buy = False
        # if 'sell' in df.at[ttf, 'macd_state'] and df.at[ttf, 'symbol']
        kors = buy_button_dict_items(star=ttf, wave_amo=remaining_budget, take_profit=take_profit, sell_out=sell_out, sell_trigbee_trigger_timeduration=sell_trigbee_trigger_timeduration, close_order_today=close_order_today, reverse_buy=reverse_buy)

        df.at[ttf, 'kors'] = kors
        df.at[ttf, 'ticker_time_frame__budget'] = f"""{margin} {"${:,}".format(remaining_budget)}"""
        # except Exception as e:
        #     print_line_of_error(f"{ttf} grid buttons {remaining_budget}")
        
      return df

        
    df_waveview = return_waveview_fillers(waveview)

    if return_type == 'waves':
      
      df = df_waveview
        
      df['color_row'] = df['macd_state'].apply(lambda x: generate_shade(x, wave=True))
      df['color_row_text'] = default_text_color

      df = update_col_number_format(df)
      df = filter_gridby_timeFrame_view(df, toggle_view_selection, grid='wave')

      json_data = df.to_json(orient='records')
      return json_data

    elif return_type == 'story':
      df = revrec.get('storygauge')

      qcp_ticker = dict(zip(revrec.get('df_ticker')['qcp_ticker'],revrec.get('df_ticker')['qcp']))
      ticker_filter = [ticker for (ticker, qcp) in qcp_ticker.items() if qcp == toggle_view_selection]                
      if ticker_filter:
          df = df[df.index.isin(ticker_filter)]
      storygauge_columns = df.columns.tolist()
      waveview['buy_alloc_deploy'] = waveview['allocation_long_deploy']
      # symbol group by to join on story
      num_cols = ['allocation_long_deploy', 'buy_alloc_deploy', 'long_at_play', 'sell_alloc_deploy', 'short_at_play', 'star_total_budget', 'remaining_budget', 'remaining_budget_borrow']
      for col in num_cols:
          waveview[col] = round(waveview[col])
          if col in storygauge_columns:
            df[col] = round(df[col])

      df_wave_symbol = waveview.groupby("symbol")[num_cols].sum().reset_index().set_index('symbol', drop=False)
      df_wave_symbol['sell_msg'] = df_wave_symbol.apply(lambda row: '${:,.0f}'.format(row['sell_alloc_deploy']), axis=1)
      df_wave_symbol['buy_msg'] = df_wave_symbol.apply(lambda row: '${:,.0f}'.format(row['buy_alloc_deploy']), axis=1)

      remaining_budget = dict(zip(df_wave_symbol['symbol'], df_wave_symbol['remaining_budget']))
      remaining_budget_borrow = dict(zip(df_wave_symbol['symbol'], df_wave_symbol['remaining_budget_borrow']))
      sell_msg = dict(zip(df_wave_symbol['symbol'], df_wave_symbol['sell_msg']))
      buy_msg = dict(zip(df_wave_symbol['symbol'], df_wave_symbol['buy_msg']))
      buy_alloc_deploy = dict(zip(df_wave_symbol['symbol'], df_wave_symbol['buy_alloc_deploy']))
      sell_alloc_deploy = dict(zip(df_wave_symbol['symbol'], df_wave_symbol['sell_alloc_deploy']))
      # queens_note = dict(zip(df_wave_symbol['symbol'], df_wave_symbol['queens_note']))


      kors_dict = buy_button_dict_items()

      # display whole number
      for col in df.columns:
        if 'trinity' in col:
            df[col] = round(pd.to_numeric(df[col]),2) * 100

      df['queens_suggested_sell'] = df['symbol'].map(sell_msg)
      df['queens_suggested_buy'] = df['symbol'].map(buy_msg)
      df['queens_suggested_sell'] = round(df['money'])

      kors_dict = buy_button_dict_items()
      df['kors'] = [kors_dict for _ in range(df.shape[0])]

      sell_options = sell_button_dict_items()
      df['sell_option'] = [sell_options for _ in range(df.shape[0])]

      x_dict = {'allocation': .3}
      df['edit_allocation_option'] = [x_dict for _ in range(df.shape[0])]

      df['current_from_open'] = round(df['current_from_open'] * 100,2)

      for star in star_names().keys():
        # kors per star
        df[f'{star}_kors'] = [kors_dict for _ in range(df.shape[0])]


      for symbol in df.index.tolist():
        if 'ticker_buying_power' not in df.columns:
            alloc = .3
        else:
          alloc = df.at[symbol, 'ticker_buying_power']
        alloc_option = {'allocation': alloc}
        df.at[symbol, 'edit_allocation_option'] = alloc_option

        sell_qty = df.at[symbol, 'qty_available']
        sell_option = sell_button_dict_items(symbol, sell_qty)
        df.at[symbol, 'sell_option'] = sell_option
        remaining_budget__ = remaining_budget.get(symbol)
        df.at[symbol, 'remaining_budget'] = remaining_budget__
        df.at[symbol, 'remaining_budget_borrow'] = remaining_budget_borrow[symbol]
        df.at[symbol, 'buy_alloc_deploy'] = buy_alloc_deploy[symbol]
        df.at[symbol, 'sell_alloc_deploy'] = sell_alloc_deploy[symbol]
        df.at[symbol, 'total_budget'] = round(revrec['df_ticker'].at[symbol, 'ticker_total_budget'])

        df['trading_model_kors'] = df['symbol'].apply(lambda x: return_trading_model_kors_v2(QUEEN_KING, symbol=x))
        take_profit = df.at[symbol, "trading_model_kors"].get('take_profit')
        sell_out = df.at[symbol, "trading_model_kors"].get('sell_out')
        close_order_today = df.at[symbol, "trading_model_kors"].get('close_order_today')
        sell_trigbee_trigger_timeduration = df.at[symbol, "trading_model_kors"].get('sell_trigbee_trigger_timeduration')
        reverse_buy = False
        kors = buy_button_dict_items(star="1Day_1Year", star_list=ttf_grid_names_list(), wave_amo=buy_alloc_deploy[symbol], take_profit=take_profit, sell_out=sell_out, sell_trigbee_trigger_timeduration=sell_trigbee_trigger_timeduration, close_order_today=close_order_today, reverse_buy=reverse_buy)
        df.at[symbol, 'kors'] = kors
      
        try:
          # star kors
          for star in star_names().keys():
            ttf = f'{symbol}_{star_names(star)}'
            # kors per star
            df.at[symbol, f'{star}_kors'] = df_waveview.at[ttf, 'kors']
            # message
            wavestate = f'{df_waveview.at[ttf, "bs_position"]} {df_waveview.at[ttf, "length"]}'
            alloc_deploy_msg = '${:,.0f}'.format(round(df_waveview.at[ttf, "allocation_long_deploy"]))
            df.at[symbol, f'{star}_state'] = f'{wavestate} {alloc_deploy_msg}'
            df.at[symbol, f'{star}_value'] = df_waveview.at[ttf, "allocation_long_deploy"]
        except Exception as e:
          print("mmm error", ttf, print_line_of_error(e))

      story_grid_num_cols = ['long_at_play',
      'short_at_play',
      'remaining_budget',
      'remaining_budget_borrow',
      'trinity_w_L',
      'trinity_w_15',
      'trinity_w_30',
      'trinity_w_54',
      'trinity_w_S',
      'queens_suggested_buy',
      'queens_suggested_sell',
      'total_budget',
      'allocation_long_deploy',
      # 'current_from_yesterday',
      'Month_value',
      # "Month_kors"
      ]
      df['current_from_yesterday'] = round(df['current_from_yesterday'] * 100,2)
      df['color_row'] = df['trinity_w_L'].apply(lambda x: generate_shade(x/100))
      df['color_row_text'] = default_text_color

      # # Totals Index
      colss = df.columns.tolist()
      for totalcols in story_grid_num_cols:
        if totalcols in colss:
          if 'trinity' in totalcols:
            df.loc['Total', totalcols] = f'{round(df[totalcols].sum() / len(df))} %'
          # elif 'current_from_yesterday' == totalcols:
          #   df.loc['Total', totalcols] = f'{round(df[totalcols].sum() / len(df))} %'
          elif totalcols == 'queens_suggested_buy':
            df.loc['Total', totalcols] = '${:,.0f}'.format(round(df["buy_alloc_deploy"].sum()))
          elif totalcols == 'queens_suggested_sell':
            df.loc['Total', totalcols] = '${:,.0f}'.format(round(df["money"].sum()))
          elif totalcols == 'total_budget':
            df.loc['Total', totalcols] = df["total_budget"].sum()
          elif totalcols == 'Month':
            df.loc['Total', 'Month_value'] = df["Month_value"].sum()
            # df.loc['Total', 'Month_kors'] = df["Month_value"].sum()
          else:
            df.loc['Total', totalcols] = df[totalcols].sum()
      
      newIndex=['Total']+[ind for ind in df.index if ind!='Total']
      df=df.reindex(index=newIndex)
      
      
      
      json_data = df.to_json(orient='records')
      return json_data

    

def header_account(client_user, prod):
  QUEENsHeart = ReadPickleData(init_queenbee(client_user=client_user, prod=prod, init_pollen_ONLY=True).get('init_pollen').get('PB_QUEENsHeart_PICKLE'))
  broker_info = init_queenbee(client_user=client_user, prod=prod, broker_info=True).get('broker_info')

  if 'charlie_bee' not in QUEENsHeart.keys():
    df = pd.DataFrame()
  
  # heart
  beat = round((datetime.now(est) - QUEENsHeart.get('heartbeat_time')).total_seconds(), 1)
  if beat > 89:
      beat = "zZzzz"
  charlie_bee = QUEENsHeart.get('charlie_bee')
  avg_beat = round(charlie_bee['queen_cyle_times']['QUEEN_avg_cycletime'])
  long = QUEENsHeart['heartbeat'].get('long')
  short = QUEENsHeart['heartbeat'].get('short')
  long = '${:,}'.format(long)
  short = '${:,}'.format(short)
  df_heart = pd.DataFrame([{'Long': long, 'Short': short, 'Heart Beat': beat, 'Avg Beat': avg_beat}])

  # Account Info
  acct_info = broker_info['account_info']
  if len(acct_info) == 0:
      df_accountinfo = pd.DataFrame()

  honey_text = '%{:,.2f}'.format(((acct_info['portfolio_value'] - acct_info['last_equity']) / acct_info['portfolio_value']) *100)
  money_text = '${:,.0f}'.format(acct_info['portfolio_value'] - acct_info['last_equity'])
  mmoney = f'{honey_text} {money_text}'
  mmoney = "\u0332".join(mmoney)
  
  buying_power = '${:,}'.format(round(acct_info.get('buying_power')))
  cash = '${:,}'.format(round(acct_info.get('cash')))
  daytrade_count = round(acct_info.get('daytrade_count'))
  portfolio_value = '${:,}'.format(round(acct_info.get('portfolio_value')))

  df_accountinfo = pd.DataFrame([{'Money': money_text, 'Todays Honey': honey_text, 'Portfolio Value': portfolio_value, 'Cash': cash, 'Buying Power': buying_power, 'daytrade count': daytrade_count }])

  df = pd.concat([df_heart, df_accountinfo], axis=1)

  return df.to_json(orient='records')

## RETURN TEXT STRING
def get_heart(client_user, username, prod):

  QUEENsHeart = ReadPickleData(init_queenbee(client_user=client_user, prod=prod, init_pollen_ONLY=True).get('init_pollen').get('PB_QUEENsHeart_PICKLE'))
  
  if 'charlie_bee' not in QUEENsHeart.keys():
    return 'Pending QUEEN'
  
  beat = round((datetime.now(est) - QUEENsHeart.get('heartbeat_time')).total_seconds(), 1)
  charlie_bee = QUEENsHeart.get('charlie_bee')
  avg_beat = round(charlie_bee['queen_cyle_times']['QUEEN_avg_cycletime'])
  long = QUEENsHeart['heartbeat'].get('long')
  short = QUEENsHeart['heartbeat'].get('short')
  long = '${:,}'.format(long)
  short = '${:,}'.format(short)
  
  msg_ls = f'Long: {long} Short: {short}'
  
  if beat > 89:
      beat = "ZZzzzZZzzz"
  msg = f"HeartRate {beat} Avg {avg_beat}"
  msg = msg + "\n" + msg_ls
  return msg

def get_account_info(client_user, username, prod):

  try:
    # WORKERBEE
    broker_info = init_queenbee(client_user=client_user, prod=prod, broker_info=True).get('broker_info')
    acct_info = broker_info['account_info']
    if len(acct_info) == 0:
       return 'PENDING QUEEN'

    honey_text = '%{:,.2f}'.format(((acct_info['portfolio_value'] - acct_info['last_equity']) / acct_info['portfolio_value']) *100)
    money_text = '${:,.2f}'.format(acct_info['portfolio_value'] - acct_info['last_equity'])
    mmoney = f'{honey_text} {money_text}'
    mmoney = "\u0332".join(mmoney)
    
    buying_power = '${:,.2f}'.format(round(acct_info.get('buying_power')))
    cash = '${:,.2f}'.format(round(acct_info.get('cash')))
    daytrade_count = round(acct_info.get('daytrade_count'))
    portfolio_value = '${:,.2f}'.format(round(acct_info.get('portfolio_value')))

    df = pd.DataFrame([{'Money': money_text, 'Todays Honey': honey_text, 'Portfolio Value': portfolio_value, 'Buying Power': buying_power, 'daytrade count': daytrade_count }])

    msg = f'{mmoney} BuyPower: {buying_power} $cash: {cash} Portfolio Value: {portfolio_value} daytrade: {daytrade_count}'
    return msg

  except Exception as e:
    print_line_of_error("heart in api")
    return 'Error QUEENs Heart'

### GRAPH
def get_ticker_data(symbols, prod):

  ticker_db = read_QUEENs__pollenstory(
      symbols=symbols,
      read_storybee=False, 
      read_pollenstory=True,
  )
  df_main = False
  for symbol in symbols:
    df = ticker_db.get('pollenstory')[f'{symbol}_{"1Minute_1Day"}']
    df = df[['timestamp_est', 'close', 'vwap']]
    # df = split_today_vs_prior(df).get('df_today')
    df = add_priorday_tic_value(df)
    start_index = 0 if len(df) == 1 else 1
    c_start = df.iloc[0]['close']
    # df['vwap'] = (df['vwap'] / df['close'])

    df[f'{symbol}'] = round((df['close'] - c_start) / c_start * 100,2)
    df[f'{symbol} vwap'] = round((df['vwap'] - df.iloc[0]['vwap']) / df.iloc[0]['vwap'] * 100,2)

    del df['close']
    del df['vwap']

    # df_main = pd.concat([df_main, df])
    if type(df_main) == bool:
        df_main = df
    else:
      df_main = df_main.merge(df, how='inner', on='timestamp_est')
  
  json_data = df_main.to_json(orient='records')

  return json_data

### GRAPH
def get_ticker_data_v2(symbol, prod):

  ticker_db = read_QUEENs__pollenstory(
      symbols=[symbol],
      read_storybee=False, 
      read_pollenstory=True,
  )
  df_main = False
  ttf = "5Minute_5Day"
  df = ticker_db.get('pollenstory')[f'{symbol}_{"5Minute_5Day"}']
  df = df[['timestamp_est', 'close', 'vwap']]
  if ttf == '1Minute_1Day':
    df = add_priorday_tic_value(df)
  df[f'{symbol}'] = df['close'] #round((df['close'] - c_start) / c_start * 100,2)
  df[f'{symbol} vwap'] = df['vwap'] #round((df['vwap'] - df.iloc[0]['vwap']) / df.iloc[0]['vwap'] * 100,2)

  del df['close']
  del df['vwap']
  
  json_data = df_main.to_json(orient='records')

  return json_data


def get_ticker_data_candle_stick(selectedOption):
  print("ssss", selectedOption)
  symbol = selectedOption[0]
  ticker_db = read_QUEENs__pollenstory(
      symbols=[symbol],
      read_storybee=False, 
      read_pollenstory=True,
  )
  df = ticker_db.get('pollenstory')[f'{symbol}_{"1Minute_1Day"}']
  df = df[['timestamp_est', 'close', 'high', 'low', 'open']]
  # df = split_today_vs_prior(df).get('df_today')
  df = add_priorday_tic_value(df)

  
  json_data = df.to_json(orient='records')

  return json_data


def get_ticker_time_frame(symbols=['SPY'], ttf="1Minute_1Day", df_main=False):
  try:

    ticker_db = read_QUEENs__pollenstory(
        symbols=symbols,
        read_storybee=False, 
        read_pollenstory=True,
    )
    ttf="5Minute_5Day"
    for symbol in symbols:
      df = ticker_db.get('pollenstory')[f'{symbol}_{ttf}']
      if ttf == '1Minute_1Day':
        df = add_priorday_tic_value(df)
      # df['trinity_tier'] = round(round(((df['macd_tier'] + df['vwap_tier'] + df['rsi_ema_tier']) / 3), 2) / 8 * 100)
      df = df[['timestamp_est', 'trinity_tier']] #'ticker_time_frame',
      df = df.rename(columns={'trinity_tier': symbol})

      if type(df_main) == bool:
         df_main = df
      else:
        df_main = df_main.merge(df, how='inner', on='timestamp_est')

    json_data = df_main.to_json(orient='records')

    return json_data

  except Exception as e:
     print_line_of_error("trinity revrec fastapi")
     return pd.DataFrame([{'error': 'list'}]).to_json()


def get_charlie_bee():
  main_db_root = os.path.join(hive_master_root(), 'db')
  queens_charlie_bee, charlie_bee = init_charlie_bee(main_db_root)

  return f'{charlie_bee}'


## MESSAGES LOGS
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

  k_colors = streamlit_config_colors()
  with open(log_file, 'r') as f:
      content = f.readlines()

  df = pd.DataFrame(content).reset_index()
  df = df.sort_index(ascending=False)
  df = df.rename(columns={'index': 'idx', 0: 'message'})
  df = df.head(500)

  df['color_row'] = k_colors.get('default_background_color')
  df['color_row_text'] = k_colors.get('default_text_color')

  json_data = df.to_json(orient='records')
  return json_data


def get_queens_mind(username, prod):

  QUEEN = load_queen_pkl(username, prod)
  # QUEEN['messages']

  return QUEEN['queens_messages']