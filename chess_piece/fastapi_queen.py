#find and read the pkl file in the folder.
import logging
import os
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import pytz
import ipdb
import copy
from chess_piece.king import (return_QUEENs__symbols_data, kingdom__global_vars, main_index_tickers, streamlit_config_colors, hive_master_root, load_local_json, save_json, ReadPickleData, PickleData, read_QUEENs__pollenstory, print_line_of_error, master_swarm_KING)
from chess_piece.queen_hive import (return_symbol_from_ttf, 
                                    update_sell_date, 
                                    init_logging, 
                                    split_today_vs_prior, 
                                    kings_order_rules, 
                                    buy_button_dict_items,
                                    order_vars__queen_order_items,
                                    find_symbol,
                                    power_amo,
                                    init_queenbee,
                                    return_trading_model_trigbee,
                                    bishop_ticker_info,
                                    ttf_grid_names,
                                    sell_button_dict_items,
                                    wave_buy__var_items,
                                    star_names,
                                    init_swarm_dbs,
                                    init_qcp_workerbees
                                    )

from chess_piece.queen_bee import execute_buy_order
from chess_piece.queen_mind import refresh_chess_board__revrec
from chess_utils.conscience_utils import story_return, return_waveview_fillers, generate_shade
from chess_piece.pollen_db import PollenDatabase
from dotenv import load_dotenv


pd.options.mode.chained_assignment = None  # default='warn' Set copy warning


est = pytz.timezone("US/Eastern")

main_root = hive_master_root() # os.getcwd()  # hive root
load_dotenv(os.path.join(main_root, ".env"))
db_root = os.path.join(main_root, "db")

pg_migration = os.environ.get('pg_migration')

# init_logging(queens_chess_piece="fastapi_queen", db_root=db_root, prod=True)

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





# the_type = get_type_by_name('float')
def add_priorday_tic_value(df, story_indexes=1):
  try:
    split_day = split_today_vs_prior(df)
    df_p = split_day.get('df_prior')
    df = split_day.get('df_today')
    
    df_pz = df_p.tail(story_indexes)
    # for idx in len(df_pz):
    prior_tic = df.iloc[0].get('timestamp_est').replace(minute=29)
    
    df_pz.at[df_pz.index[0], 'timestamp_est'] = prior_tic

    df = pd.concat([df_pz, df])

    return df
  except Exception as e:
     print_line_of_error(e)
     return df

def validate_kors_valueType(newvalue, current_value):

  try:
    if type(newvalue) == type(current_value):
        # print("update kor value", kor, newvalue)
        return newvalue
    elif newvalue:
      # print("try to update type", newvalue)
      if type(current_value) == datetime:
        print(newvalue, current_value)
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
      ttf_gridnames = [i.lower() for i in star_names().keys()]
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



def parse_date(date_str):
    date_formats = [
       "%Y-%m-%dT%H:%M:%S",
       "%Y-%m-%dT%H:%M",
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

def app_buy_order_request(client_user, prod, selected_row, kors, ready_buy=False, story=False, trigbee='buy_cross-0'): # index & wave_amount
  try:
    qb = init_queenbee(client_user=client_user, prod=prod, queen_king=True, api=True, revrec=True, queen_heart=True, pg_migration=pg_migration)
    QUEEN_KING = qb.get('QUEEN_KING')
    api = qb.get('api')
    revrec = qb.get('revrec') # qb.get('queen_revrec')
    QUEENsHeart = qb.get('QUEENsHeart')
    portfolio = QUEENsHeart['heartbeat'].get('portfolio')

    buy_package = create_AppRequest_package(request_name='buy_orders')
    buy_package.update({'buy_order': {}})
    blessing={} #{i: '': for i in []}, # order_vars
    
    # Trading Model
    symbol=selected_row.get('symbol')
    if story:
      # star_time=star_names(kors.get('star_list')[0])
      # ticker_time_frame = f'{symbol}_{star_time}'
      
      ticker_time_frame = kors.get('star')
      star_time = return_startime_from_ttf(ticker_time_frame)
      if not revrec:
         wave_blocktime = 'afternoon_2-4'
      elif ticker_time_frame in revrec.get('waveview').index:
        wave_blocktime = revrec.get('waveview').loc[ticker_time_frame].get('wave_blocktime')
      else:
         wave_blocktime = 'afternoon_2-4'
    else:
      star_time = selected_row.get('star')
      ticker_time_frame = selected_row.get('ticker_time_frame')
      trigbee = selected_row.get('macd_state')
      wave_blocktime = selected_row.get('wave_blocktime')

    trading_model = QUEEN_KING['king_controls_queen']['symbols_stars_TradingModel'].get(symbol) # main symbol for Model (SPY)
    if not trading_model:
       trading_model = QUEEN_KING['king_controls_queen']['symbols_stars_TradingModel'].get("SPY")
    
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

    exx = execute_buy_order(
                    api=api, 
                    portfolio=portfolio, 
                    blessing=blessing,
                    trading_model=blessing.get('trading_model'),
                    ticker=blessing.get('symbol'), 
                    ticker_time_frame=blessing.get('ticker_time_frame_origin'), 
                    trig=blessing.get('trigbee'), 
                    wave_amo=blessing.get('wave_amo'),
                    order_type=blessing.get('order_type'),
                    side=blessing.get('order_side'),
                    limit_price=blessing.get('limit_price'),
                    crypto=crypto
                    )

    if exx.get('executed'):
      print("APP EXX Order")

      buy_package.update({'new_queen_order_df': exx.get('new_queen_order_df')})   

      # save
      QUEEN_KING['buy_orders'].append(buy_package)

      if pg_migration:
        table_name = 'client_user_store' if prod else 'client_user_store_sandbox'
        PollenDatabase.upsert_data(table_name, key=QUEEN_KING.get('key'), value=QUEEN_KING)
      else:
        PickleData(QUEEN_KING.get('source'), QUEEN_KING)

      print("SAVED ORDER TO QK")
      return {'status': True, 'msg': f'{symbol} purchased'}
    else:
       print("Ex Failed")
       return {'status': False, 'msg': "Ex Failed"}
    
  except Exception as e:
     y=print_line_of_error(f"fastapi buy button failed {e}")
    #  logging.error(("fastapi", e))
     return {'status': False, 'msg': str(y)}


def app_buy_wave_order_request(username, prod, selected_row, default_value=False, ready_buy=False, x_buy=False, order_rules=False): # index & wave_amount
  try:
    QUEEN_KING = init_queenbee(client_user=username, prod=prod, queen_king=True, pg_migration=pg_migration).get('QUEEN_KING')
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

    if pg_migration:
      table_name = 'client_user_store' if prod else 'client_user_store_sandbox'
      PollenDatabase.upsert_data(table_name, key=QUEEN_KING.get('key'), value=QUEEN_KING)
    else:
      PickleData(QUEEN_KING.get('source'), QUEEN_KING)
    

    return True
  except Exception as e:
     print(e)
    #  logging.error(("fastapi", e))


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

    QUEEN_KING = init_queenbee(client_user=client_user, prod=prod, queen_king=True, pg_migration=pg_migration).get('QUEEN_KING')
    ORDERS = init_queenbee(client_user=client_user, prod=prod, orders=True, pg_migration=pg_migration).get('ORDERS')
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
      if pg_migration:
        table_name = 'client_user_store' if prod else 'client_user_store_sandbox'
        PollenDatabase.upsert_data(table_name, key=QUEEN_KING.get('key'), value=QUEEN_KING)
      else:
        PickleData(QUEEN_KING.get('source'), QUEEN_KING)

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
    QUEEN_KING = init_queenbee(client_user=username, prod=prod, queen_king=True, pg_migration=pg_migration).get('QUEEN_KING')
    order_update_package = create_AppRequest_package(request_name='update_queen_order', client_order_id=client_order_id)
    order_update_package['queen_order_updates'] = {client_order_id: {'queen_order_state': 'archived'}}
    QUEEN_KING['update_queen_order'].append(order_update_package)
    if pg_migration:
      table_name = 'client_user_store' if prod else 'client_user_store_sandbox'
      PollenDatabase.upsert_data(table_name, key=QUEEN_KING.get('key'), value=QUEEN_KING)
    else:
      PickleData(QUEEN_KING.get('source'), QUEEN_KING)
    return True


def app_queen_order_update_order_rules(client_user, username, prod, selected_row, default_value):
    try:
      current_kors = kings_order_rules()
      queen_order = selected_row
      client_order_id = queen_order.get('client_order_id')
      # number_shares = default_value
      QUEEN_KING = init_queenbee(client_user=client_user, prod=prod, queen_king=True, pg_migration=pg_migration).get('QUEEN_KING')
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
        if pg_migration:
          table_name = 'client_user_store' if prod else 'client_user_store_sandbox'
          PollenDatabase.upsert_data(table_name, key=QUEEN_KING.get('key'), value=QUEEN_KING)
        else:
          PickleData(QUEEN_KING.get('source'), QUEEN_KING)
        return {'status': True, 'description': 'kors updates'}
      else:
        msg = ("no updates to kors")
        return {'status': False, 'description': msg}
         
    except Exception as e:
       print_line_of_error(e)
       return {'status': False, 'description': str(e)}

## MAIN GRIDS


def get_queen_orders_json(client_user, username, prod, toggle_view_selection):
  
  try:
      if toggle_view_selection.lower() == 'queen':
          ORDERS = init_queenbee(client_user, prod, queen=True, pg_migration=pg_migration).get('QUEEN')
      elif toggle_view_selection.lower() == 'final':
          ORDERS = init_queenbee(client_user, prod, orders_final=True, pg_migration=pg_migration).get('ORDERS_FINAL')
      else:
          ORDERS = init_queenbee(client_user, prod, orders=True, pg_migration=pg_migration).get('ORDERS')

      df = ORDERS['queen_orders']

      # ORDERS NOT Available
      if type(ORDERS) != dict:
        print("NO ORDERS")
        return pd.DataFrame().to_json()
      if type(df) != pd.core.frame.DataFrame:
        return pd.DataFrame().to_json()
      if len(df) == 1:
        print("init queen")
        return pd.DataFrame().to_json()
      
      king_G = kingdom__global_vars()
      active_queen_order_states = king_G.get('active_queen_order_states')
      # filter for range
      df = df[(df['datetime'] >= datetime.now(est).replace(year=2024, month=10, day=1)) | (df['queen_order_state'].isin(active_queen_order_states))]


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

      def update_order_rules(d):
        try:
          d['sell_date'] = d['sell_date'].strftime('%m/%d/%YT%H:%M')
          return d
        except Exception as e:
           return d

      df['order_rules'] = df['order_rules'].apply(lambda cell: update_order_rules(cell) if isinstance(cell, dict) else cell)

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
    print_line_of_error(f"{e} Orders Failed")


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
    
    try:
      s = datetime.now()
      if toggle_view_selection.lower() == 'king':
        king_G = kingdom__global_vars()
        qb = init_queenbee(client_user=client_user, prod=prod, queen=True, queen_king=True, revrec=True, pg_migration=pg_migration)
        QUEEN = qb.get('QUEEN')
        QUEEN_KING = qb.get('QUEEN_KING')
        STORY_bee = return_QUEENs__symbols_data(QUEEN=QUEEN, QUEEN_KING=QUEEN_KING, swarmQueen=False, read_pollenstory=False).get('STORY_bee')
        revrec = refresh_chess_board__revrec(QUEEN['account_info'], QUEEN, QUEEN_KING, STORY_bee, king_G.get('active_queen_order_states')) ## Setup Board
      elif toggle_view_selection == '400_10M':
        king_G = kingdom__global_vars()
        qb = init_queenbee(client_user=client_user, prod=prod, queen=True, queen_king=True, revrec=True, pg_migration=pg_migration)
        QUEEN = qb.get('QUEEN')
        QUEEN_KING = qb.get('QUEEN_KING')

        QUEENBEE = {'workerbees': {}}
        db=init_swarm_dbs(prod)
        BISHOP = ReadPickleData(db.get('BISHOP'))
        df = BISHOP.get(toggle_view_selection)
        for sector in set(df['sector']):
            token = df[df['sector']==sector]
            tickers=token['symbol'].tolist()
            QUEENBEE['workerbees'][sector] = init_qcp_workerbees(ticker_list=tickers, buying_power=0)
        QUEEN_KING['chess_board'] = QUEENBEE['workerbees']
        symbols = [item for sublist in [v.get('tickers') for v in QUEEN_KING['chess_board'].values()] for item in sublist]
        STORY_bee = return_QUEENs__symbols_data(QUEEN=None, QUEEN_KING=QUEEN_KING, swarmQueen=False, read_pollenstory=False, symbols=symbols).get('STORY_bee')
        revrec = refresh_chess_board__revrec(QUEEN['account_info'], QUEEN, QUEEN_KING, STORY_bee, king_G.get('active_queen_order_states'), wave_blocktime='morning_9-11') ## Setup Board
      else:
        qb = init_queenbee(client_user, prod, revrec=True, queen_king=True, pg_migration=pg_migration)
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
   
      df_waveview = return_waveview_fillers(QUEEN_KING, waveview)

      if return_type == 'waves':
        
        df = df_waveview
          
        df['color_row'] = df['macd_state'].apply(lambda x: generate_shade(x, wave=True))
        df['color_row_text'] = default_text_color

        df = update_col_number_format(df)
        df = filter_gridby_timeFrame_view(df, toggle_view_selection, grid='wave')

        json_data = df.to_json(orient='records')
        print((datetime.now() - s).total_seconds())
        return json_data

      elif return_type == 'story':
        print('prod', prod)
        df = story_return(QUEEN_KING, revrec, prod, toggle_view_selection)
        
        json_data = df.to_json(orient='records')
        print("story runtime: ", (datetime.now() - s).total_seconds())
        return json_data
    
    except Exception as e:
      print_line_of_error(e)


def update_buy_autopilot(client_user, prod, selected_row, default_value, status='-'):
    print(client_user, default_value) 
    buy_autopilot = default_value.get('buy_autopilot')
    QUEEN_KING = init_queenbee(client_user, prod, queen_king=True, pg_migration=pg_migration).get('QUEEN_KING')
    symbol = selected_row.get('symbol')
    if symbol not in QUEEN_KING['king_controls_queen']['ticker_autopilot'].index:
        QUEEN_KING['king_controls_queen']['ticker_autopilot'].loc[symbol] = pd.Series([None, None], index=['buy_autopilot', 'sell_autopilot'])
    
    status = f'{status} BUY AutoPilot Updated to {buy_autopilot}'
    QUEEN_KING['king_controls_queen']['ticker_autopilot'].at[symbol, 'buy_autopilot'] = buy_autopilot

    if pg_migration:
        table_name = 'client_user_store' if prod else 'client_user_store_sandbox'
        PollenDatabase.upsert_data(table_name, QUEEN_KING.get('key'), QUEEN_KING)
    else:
       PickleData(QUEEN_KING.get('source'), QUEEN_KING)
    print(status)
    return grid_row_button_resp(description=status)

def update_sell_autopilot(client_user, prod, selected_row, default_value, status='-'):
    print(client_user, default_value) 
    sell_autopilot = default_value.get('sell_autopilot')
    QUEEN_KING = init_queenbee(client_user, prod, queen_king=True, pg_migration=pg_migration).get('QUEEN_KING')
    symbol = selected_row.get('symbol')
    if symbol not in QUEEN_KING['king_controls_queen']['ticker_autopilot'].index:
        QUEEN_KING['king_controls_queen']['ticker_autopilot'].loc[symbol] = pd.Series([False, False], index=['buy_autopilot', 'sell_autopilot'])
  
    status = f'{status} SELL AutoPilot Updated to {sell_autopilot}'
    QUEEN_KING['king_controls_queen']['ticker_autopilot'].at[symbol, 'sell_autopilot'] = sell_autopilot
    
    if pg_migration:
        table_name = 'client_user_store' if prod else 'client_user_store_sandbox'
        PollenDatabase.upsert_data(table_name, QUEEN_KING.get('key'), QUEEN_KING)
    else:
       PickleData(QUEEN_KING.get('source'), QUEEN_KING)
    print(status)
    return grid_row_button_resp(description=status)


def update_queenking_chessboard(client_user, prod, selected_row, default_value):
   QUEEN_KING = init_queenbee(client_user, prod, queen_king=True, pg_migration=pg_migration).get('QUEEN_KING')
   print("KOR", default_value)
  #  df = pd.DataFrame(new_data).T
   if 'ticker_revrec_allocation_mapping' in QUEEN_KING['king_controls_queen'].keys():
      # update_dict = dict(zip(df['symbol'], df['']))
      updated_dict = {selected_row.get('symbol'): selected_row.get('ticker_buying_power')}
      print(updated_dict)
   status = 'updated'
   return grid_row_button_resp(description=status)

# Account Header account_header
def header_account(client_user, prod):
  QUEENsHeart = init_queenbee(client_user=client_user, prod=prod, queen_heart=True, pg_migration=pg_migration).get('QUEENsHeart')
  broker_info = init_queenbee(client_user=client_user, prod=prod, broker_info=True, pg_migration=pg_migration).get('broker_info') ## WORKERBEE, account_info is in heartbeat already, no need to read this file

  if 'charlie_bee' not in QUEENsHeart.keys():
    df = pd.DataFrame()
  
  # heart
  broker_qty_delta = QUEENsHeart['heartbeat'].get('broker_qty_delta')
  beat = round((datetime.now(est) - QUEENsHeart.get('heartbeat_time')).total_seconds(), 1)
  if beat > 89:
      beat = "zZzzz"
  try:
    charlie_bee = QUEENsHeart.get('charlie_bee')
    avg_beat = round(charlie_bee['queen_cyle_times']['QUEEN_avg_cycletime'])
  except Exception as e:
    print(e)
    avg_beat = 0
  long = QUEENsHeart['heartbeat'].get('long')
  short = QUEENsHeart['heartbeat'].get('short')
  long = '${:,}'.format(long)
  short = '${:,}'.format(short)
  df_heart = pd.DataFrame([{'Broker': 'Alpaca', 'Long': long, 'Short': short, 'Heart Beat': beat, 'Avg Beat': avg_beat}])

  # Account Info
  acct_info = broker_info
  if len(acct_info) == 0:
      df_accountinfo = pd.DataFrame()

  honey_text = '%{:,.2f}'.format(((acct_info['portfolio_value'] - acct_info['last_equity']) / acct_info['portfolio_value']) *100)
  # money_text = round((acct_info['portfolio_value'] - acct_info['last_equity']),0)
  money_text = '${:,.0f}'.format(acct_info['portfolio_value'] - acct_info['last_equity'])
  
  buying_power = '${:,}'.format(round(acct_info.get('buying_power')))
  cash = '${:,}'.format(round(acct_info.get('cash')))
  daytrade_count = round(acct_info.get('daytrade_count'))
  portfolio_value = '${:,}'.format(round(acct_info.get('portfolio_value')))

  df_accountinfo = pd.DataFrame([{'Money': money_text, 'Todays Honey': honey_text, 'Portfolio Value': portfolio_value, 'Cash': cash, 'Buying Power': buying_power, 'daytrade count': daytrade_count}])


  df = pd.concat([df_heart, df_accountinfo], axis=1)

  return df.to_json(orient='records')



### GRAPH
def get_ticker_data(symbols, toggles_selection):
  time_frame = star_names(toggles_selection)
  if pg_migration:
     pollenstory = PollenDatabase.retrieve_all_pollenstory_data(symbols).get('pollenstory')
  else:
    pollenstory = read_QUEENs__pollenstory(symbols=symbols,read_storybee=False, read_pollenstory=True,).get('pollenstory')

  df_main = False
  for symbol in symbols:
    df = pollenstory[f'{symbol}_{time_frame}']
    df = df[['timestamp_est', 'close', 'vwap']]
    if time_frame == '1Minute_1Day':
      df = add_priorday_tic_value(df)
    
    df['timestamp_est'] = pd.to_datetime(df['timestamp_est']).dt.floor('min')
    df['timestamp_est'] = df['timestamp_est'].dt.strftime('%Y-%m-%d %H:%M:%S%z')

    c_start = df.iloc[0]['close']

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
def get_ticker_time_frame(symbols=['SPY'],  toggles_selection=False):
  try:
    df_main=False
    star_time = star_names(toggles_selection)
    if pg_migration:
      pollenstory = PollenDatabase.retrieve_all_pollenstory_data(symbols).get('pollenstory')
    else:
      pollenstory = read_QUEENs__pollenstory(symbols=symbols,read_storybee=False, read_pollenstory=True,).get('pollenstory')
    for symbol in symbols:
         
      df = pollenstory[f'{symbol}_{star_time}']
      if star_time == '1Minute_1Day':
        df = add_priorday_tic_value(df)
      df = df[['timestamp_est', 'trinity_tier']] #'ticker_time_frame',
      df['timestamp_est'] = pd.to_datetime(df['timestamp_est']).dt.floor('min')
      df['timestamp_est'] = df['timestamp_est'].dt.strftime('%Y-%m-%d %H:%M:%S%z')
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





def get_queen_messages_logfile_json(username, log_file):


  k_colors = streamlit_config_colors()
  with open(log_file, 'r') as f:
      content = f.readlines()

  df = pd.DataFrame(content).reset_index()
  df = df.sort_index(ascending=False)
  df = df.rename(columns={'index': 'idx', 0: 'message'})
  # df = df.head(500)
  # print(df)

  df['color_row'] = k_colors.get('default_background_color')
  df['color_row_text'] = k_colors.get('default_text_color')

  json_data = df.to_json(orient='records')
  return json_data
