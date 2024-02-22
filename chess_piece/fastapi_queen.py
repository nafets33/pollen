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
from chess_piece.king import (streamlit_config_colors, hive_master_root, ReadPickleData, PickleData, read_QUEENs__pollenstory, print_line_of_error, master_swarm_KING)
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
                                    sell_button_dict_items,)
from chess_piece.queen_bee import execute_order, sell_order__var_items
# import streamlit as st

pd.options.mode.chained_assignment = None  # default='warn' Set copy warning

est = pytz.timezone("US/Eastern")

main_root = hive_master_root() # os.getcwd()  # hive root
load_dotenv(os.path.join(main_root, ".env"))
db_root = os.path.join(main_root, "db")

init_logging(queens_chess_piece="fastapi_queen", db_root=db_root, prod=True)

 ###### Helpers UTILS



# KORS
def return_trading_model_kors(QUEEN_KING, star__wave, current_wave_blocktime='morning_9-11'):
  star, wave_state = star__wave.split("__")
  symbol, tframe, tperoid = star.split("_")
  star = f'{tframe}_{tperoid}'
  trigbee = "buy_cross-0" if 'buy' in wave_state else 'sell_cross-0'
  trading_model = QUEEN_KING['king_controls_queen']['symbols_stars_TradingModel'][symbol]['stars_kings_order_rules'][star]['trigbees'][trigbee].get(current_wave_blocktime)
  return trading_model


def return_kors(df, QUEEN_KING):
  stars = stars.keys()
  t_kors ={}
  for symbol in set(df['ttf_symbol'].tolist()):
    trading_model = QUEEN_KING['king_controls_queen']['symbols_stars_TradingModel'].get(symbol)
    # t_kors[symbol] = {}
    for star in stars:
      ttf_key = f'{symbol}_{star}'
      t_kors[symbol][star] = {}
      for trigbee in trigger_bees().keys():
        king_order_rules = trading_model['stars_kings_order_rules'][star]['trigbees'][trigbee].get('morning_9-11')
        t_kors[symbol][star][trigbee] = king_order_rules
    # king_order_rules = trading_model['stars_kings_order_rules'][star_time]['trigbees'][tm_trig][current_wave_blocktime]
  
  return t_kors

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

def generate_shade(number_variable, base_color=False, wave=False, shade_num_var=100):
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

        base_color = green if (number_variable) > 0 else blue
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
    #
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
    
    if wave_state_filter:
      trigname = 'trigname' if 'trigname' in df.columns else 'macd_state'
      if toggle_view_selection.lower() == 'buys':
          df = df[df[trigname].str.contains('buy')]
      elif toggle_view_selection.lower() == 'sells':
          df = df[~df[trigname].str.contains('buy')]
    
    return df


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

def wave_buy__var_items(ticker_time_frame, trigbee, macd_state, ready_buy, x_buy, order_rules):
   trigbee = macd_state
   return {'ticker': ticker_time_frame.split("_")[0],
    'ticker_time_frame': ticker_time_frame,
    'system': 'app',
    # 'wave_trigger': wave_trigger,
    'request_time': datetime.now(est),
    'app_requests_id' : f'wave_buy__app_requests_id__{return_timestamp_string()}{datetime.now().microsecond}',
    'macd_state': trigbee,
    'ready_buy': ready_buy,
    'x_buy': x_buy,
    'order_rules': order_rules,
    }

####### Router Calls

def app_buy_order_request(client_user, username, prod, selected_row, default_value, ready_buy=False, x_buy=False): # index & wave_amount
  try:
    # QUEENsHeart = ReadPickleData(init_queenbee(client_user=client_user, prod=prod, init_pollen_ONLY=True).get('init_pollen').get('PB_QUEENsHeart_PICKLE'))
    # heartbeat = QUEENsHeart.get('heartbeat')
    # revrec = load_revrec_pkl(username, prod).get('revrec')

    button_buy = default_value # dictionary k,v return

    qb = init_queenbee(client_user=client_user, prod=prod, queen=True, queen_king=True, api=True)
    QUEEN = qb.get('QUEEN')
    QUEEN_KING = qb.get('QUEEN_KING')
    api = qb.get('api')

    buy_package = create_AppRequest_package(request_name='buy_orders')
    buy_package.update({'buy_order': {}})
    blessing={} #{i: '': for i in []}, # order_vars
    revrec = QUEEN.get('revrec')
    heartbeat = QUEEN.get('heartbeat')
    # return trading model

    
    ticker = selected_row.get('symbol') # update symbol on X
    ticker_time_frame = selected_row.get('ticker_time_frame')
    star_time = selected_row.get('star_time')
    trigbee = selected_row.get('macd_state')
    wave_blocktime = selected_row.get('wave_blocktime')
    trading_model = QUEEN_KING['king_controls_queen']['symbols_stars_TradingModel'].get(ticker)
    symbol = find_symbol(QUEEN, ticker, trading_model, trigbee).get('ticker')
    
    tm_trig = return_trading_model_trigbee(tm_trig=trigbee, trig_wave_length=trigbee.split("-")[-1])
    if ready_buy:
      tm_trig = f'sell_cross-0' if 'buy' in tm_trig else f'buy_cross-0'

    # king_order_rules = revrec['waveview'].at[ticker_time_frame, 'king_order_rules']
    king_order_rules = trading_model['stars_kings_order_rules'][star_time]['trigbees'][tm_trig][wave_blocktime]
    # END
    
    crypto=False
    king_resp=True,
    king_eval_order=False,
    maker_middle = False
    current_wave = revrec['waveview'].get('current_wave')
    current_macd_cross__wave = heartbeat.get('current_wave')
    power_up_amo = power_amo()
    order_side = 'buy'
    borrowed_funds = True # USER INITIATE
    borrow_qty = False ## DEPRECIATE
    # print(button_buy.keys())

    for rule, value in button_buy.items():
      if rule in ['wave_amo', 'close_order_today', 'take_profit', 'sell_out', 'sell_trigbee_trigger', 'sell_trigbee_trigger_timeduration']: # validated items to add orules

        if rule == 'wave_amo':
          #  print(type(value), value)
            if type(value) != float:
              value = float(value)
            wave_amo = value
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
        
        print("updating", rule, value)
        king_order_rules.update({rule: value})

    order_vars = order_vars__queen_order_items(trading_model=trading_model.get('theme'), 
                                                king_order_rules=king_order_rules, 
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
      return {'status': True}
    else:
       print("Ex Failed")
       return {'status': False}
    
  except Exception as e:
     print_line_of_error(f"fastapi buy button failed {e}")
     logging.error(("fastapi", e))
     return {'status': False}


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


def app_Sellorder_request(client_user, username, prod, selected_row, default_value):
  try:
    # WORKERBEE validate to ensure number of shares available to SELL as user can click twice
    number_shares = default_value

    ORDERS = init_queenbee(client_user=client_user, prod=prod, orders=True).get('ORDERS')
    if type(ORDERS) != dict:
      print("NO ORDERS")
      return pd.DataFrame().to_json()
    queen_order = ORDERS['queen_orders']
    # QUEEN = load_queen_pkl(username, prod)
    # queen_order = QUEEN['queen_orders']
    
    QUEEN_KING = load_queen_App_pkl(username, prod)
    
    # if client id not on grid return then find client id that has the number of shares
    client_order_id = selected_row.get('client_order_id')
    df = queen_order.loc[client_order_id]
    
    # VALIDATE check against available_shares and validate amount
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

    return {'status': 'success'}
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
def get_queen_orders_json(client_user, username, prod, toggle_view_selection):
  
  try:
      # qb = init_queenbee(client_user=client_user, prod=prod, orders=True)
      ORDERS = init_queenbee(client_user=client_user, prod=prod, orders=True).get('ORDERS')


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
         df = split_today_vs_prior(df).get('df_today')
      else:
        qos_view=['running', 'running_close', 'running_open']
        df = df[df['queen_order_state'].isin(qos_view)]

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


def queen_wavestories__get_macdwave(username, prod, symbols, toggle_view_selection, return_type='waves'):
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
        if toggle_view_selection.lower() == 'king':
          revrec = load_queen_App_pkl(username, prod).get('revrec')
        elif prod:
          revrec = ReadPickleData(username + '/queen_revrec.pkl').get('revrec')
        else:
          revrec = ReadPickleData(username + '/queen_revrec_sandbox.pkl').get('revrec')


        # star_powers = QUEEN_KING['king_controls_queen'].get('star_power')
        # print(QUEEN_KING['king_controls_queen'].keys())

        if type(revrec.get('waveview')) != pd.core.frame.DataFrame:
          print(f'rr not df null, {revrec}')
          return pd.DataFrame().to_json()
        
        if len(symbols) == 0:
          symbols=['SPY']

        k_colors = streamlit_config_colors()
        default_text_color = k_colors['default_text_color'] # = '#59490A'
        default_font = k_colors['default_font'] # = "sans serif"
        default_yellow_color = k_colors['default_yellow_color'] # = '#C5B743'


        df_wave = revrec.get('waveview')
        df_wave['sell_alloc_deploy'] =  np.where((df_wave['macd_state'].str.contains("buy")) & (df_wave['allocation_deploy'] > 0), df_wave['star_at_play'] - df_wave['allocation_deploy'], 0)
        df_wave['sellbuy_alloc_deploy'] =  np.where((df_wave['macd_state'].str.contains("sell")) & (df_wave['allocation_deploy'] > 0), df_wave['star_at_play'] - df_wave['allocation_deploy'], 0)
        df_wave['sell_alloc_deploy'] = df_wave['sell_alloc_deploy'] + df_wave['sellbuy_alloc_deploy']
        df_wave['buy_alloc_deploy'] =  np.where((df_wave['macd_state'].str.contains("buy")) & (df_wave['allocation_deploy'] < 0), round(abs(df_wave['allocation_deploy'])), 0)
        # df_wave['queens_note'] = 
        
        if return_type == 'waves':
          QUEEN_KING = load_queen_App_pkl(username, prod)
          df = df_wave
          kors_dict = buy_button_dict_items()
          df['kors'] = [kors_dict for _ in range(df.shape[0])]
          df['kors_key'] = df["ticker_time_frame"] +  "__" + df['macd_state']
          df['trading_model_kors'] = df['kors_key'].apply(lambda x: return_trading_model_kors(QUEEN_KING, star__wave=x))
          for ttf in df.index.tolist():
            try:
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
              
              kors = buy_button_dict_items(star=ttf, wave_amo=remaining_budget, take_profit=take_profit, sell_out=sell_out, sell_trigbee_trigger_timeduration=sell_trigbee_trigger_timeduration, close_order_today=close_order_today)
              # ttf_name = ttf_grid_names(ttf, symbol=False)
              # df.at[ttf, 'time_frame'] = ttf_name
              df.at[ttf, 'kors'] = kors
              df.at[ttf, 'ticker_time_frame__budget'] = f"""{margin} {"${:,}".format(remaining_budget)}"""
            
            
            except Exception as e:
                print_line_of_error(f"{ttf} grid buttons {remaining_budget}")
           
          df['color_row'] = df['macd_state'].apply(lambda x: generate_shade(x, wave=True))
          df['color_row_text'] = default_text_color

          df = update_col_number_format(df)
          df = filter_gridby_timeFrame_view(df, toggle_view_selection, grid='wave')

          # wave_grid_num_cols = ['current_profit',
          # 'maxprofit',
          # 'star_at_play',
          # 'star_at_play_borrow',
          # 'allocation_deploy',
          # 'allocation_borrow_deploy',
          # 'remaining_budget',
          # 'remaining_budget_borrow',
          # 'current_profit_deviation',
          # ]
          # # # Totals Index
          # for totalcols in wave_grid_num_cols:
          #   df.loc['Total', totalcols] = df[totalcols].sum()
          # newIndex=['Total']+[ind for ind in df.index if ind!='Total']
          # df=df.reindex(index=newIndex)


          json_data = df.to_json(orient='records')
          return json_data
        

        elif return_type == 'story':

          df = revrec.get('storygauge')
          storygauge_columns = df.columns.tolist()

          # symbol group by to join on story
          num_cols = ['buy_alloc_deploy', 'long_at_play', 'sell_alloc_deploy', 'short_at_play', 'star_total_budget', 'remaining_budget', 'remaining_budget_borrow']
          for col in num_cols:
              df_wave[col] = round(df_wave[col])
              if col in storygauge_columns:
                df[col] = round(df[col])

          df_wave_symbol = df_wave.groupby("symbol")[num_cols].sum().reset_index().set_index('symbol', drop=False)
          df_wave_symbol['sell_pct'] = (df_wave_symbol['sell_alloc_deploy'] / df_wave_symbol['long_at_play'] * 100).fillna(0)
          df_wave_symbol['sell_pct'] = round(df_wave_symbol['sell_pct'],1)
          df_wave_symbol['buy_pct'] = (df_wave_symbol['buy_alloc_deploy'] / df_wave_symbol['star_total_budget'] * 100).fillna(0)
          df_wave_symbol['buy_pct'] = round(df_wave_symbol['buy_pct'],1)
          df_wave_symbol['sell_msg'] = df_wave_symbol.apply(lambda row: '%{} ${:,.0f}'.format(row['sell_pct'], row['sell_alloc_deploy']), axis=1)
          df_wave_symbol['buy_msg'] = df_wave_symbol.apply(lambda row: '%{} ${:,.0f}'.format(row['buy_pct'], row['buy_alloc_deploy']), axis=1)

          remaining_budget = dict(zip(df_wave_symbol['symbol'], df_wave_symbol['remaining_budget']))
          remaining_budget_borrow = dict(zip(df_wave_symbol['symbol'], df_wave_symbol['remaining_budget_borrow']))
          sell_msg = dict(zip(df_wave_symbol['symbol'], df_wave_symbol['sell_msg']))
          buy_msg = dict(zip(df_wave_symbol['symbol'], df_wave_symbol['buy_msg']))
          buy_alloc_deploy = dict(zip(df_wave_symbol['symbol'], df_wave_symbol['buy_alloc_deploy']))
          sell_alloc_deploy = dict(zip(df_wave_symbol['symbol'], df_wave_symbol['sell_alloc_deploy']))
          # queens_note = dict(zip(df_wave_symbol['symbol'], df_wave_symbol['queens_note']))

          df['color_row'] = df['trinity_w_L'].apply(lambda x: generate_shade(x))

          # display whole number
          for col in df.columns:
            if 'trinity' in col:
                df[col] = round(pd.to_numeric(df[col]),2) * 100

          df['color_row_text'] = default_text_color
          df['queens_suggested_sell'] =  df['symbol'].map(sell_msg)
          df['queens_suggested_buy'] =  df['symbol'].map(buy_msg)
          # df['buy_alloc_deploy'] =  df['symbol'].map(buy_alloc_deploy)
          # df['sell_alloc_deploy'] =  df['symbol'].map(sell_alloc_deploy)

          kors_dict = sell_button_dict_items()
          df['kors'] = [kors_dict for _ in range(df.shape[0])]
          
          for symbol in df.index.tolist():
            # sell_amt = df_wave_symbol.at[symbol, 'sell_alloc_deploy']
            # symbol_rate = df_wave_symbol
            
            sell_qty = df_wave_symbol.at[symbol, 'sell_alloc_deploy']
            kors = sell_button_dict_items(symbol, sell_qty)
            df.at[symbol, 'kors'] = kors
            df.at[symbol, 'remaining_budget'] = remaining_budget[symbol]
            df.at[symbol, 'remaining_budget_borrow'] = remaining_budget_borrow[symbol]
            df.at[symbol, 'buy_alloc_deploy'] = buy_alloc_deploy[symbol]
            df.at[symbol, 'sell_alloc_deploy'] = sell_alloc_deploy[symbol]


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
          ]
          # # Totals Index
          for totalcols in story_grid_num_cols:
            if 'trinity' in totalcols:
              df.loc['Total', totalcols] = f'{round(df[totalcols].sum() / len(df))} %'
            elif totalcols == 'queens_suggested_buy':
               df.loc['Total', totalcols] = '${:,.0f}'.format(round(df["buy_alloc_deploy"].sum()))
            elif totalcols == 'queens_suggested_sell':
               df.loc['Total', totalcols] = '${:,.0f}'.format(round(df["sell_alloc_deploy"].sum()))
            else:
               df.loc['Total', totalcols] = df[totalcols].sum()
          newIndex=['Total']+[ind for ind in df.index if ind!='Total']
          df=df.reindex(index=newIndex)
          
          
          
          json_data = df.to_json(orient='records')
          return json_data

    
    except Exception as e:
       print("mmm error", print_line_of_error(e))



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
    qb = init_queenbee(client_user=client_user, prod=prod, broker_info=True)
    broker_info = qb.get('broker_info')
    acct_info = broker_info['account_info']
    if len(acct_info) == 0:
       return 'PENDING QUEEN'

    honey_text = "Today" + '%{:,.2f}'.format(((acct_info['portfolio_value'] - acct_info['last_equity']) / acct_info['portfolio_value']) *100)
    money_text = '${:,.2f}'.format(acct_info['portfolio_value'] - acct_info['last_equity'])
    mmoney = f'{honey_text} {money_text}'
    mmoney = "\u0332".join(mmoney)
    
    buying_power = '${:,.2f}'.format(round(acct_info.get('buying_power')))
    cash = '${:,.2f}'.format(round(acct_info.get('cash')))
    daytrade_count = round(acct_info.get('daytrade_count'))
    portfolio_value = '${:,.2f}'.format(round(acct_info.get('portfolio_value')))


    msg = f'{mmoney} BuyPower: {buying_power} $cash: {cash} Portfolio Value: {portfolio_value} daytrade: {daytrade_count}'
    return msg

  except Exception as e:
    print_line_of_error("heart in api")
    return 'Error QUEENs Heart'

## GRAPH
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


def get_revrec_trinity(username, prod, trinity_weight='w_15', symbols=['SPY']):
  try:
    revrec = load_revrec_pkl(username, prod).get('revrec')
    df  = revrec.get('storygauge')
    # df['symbol'] = df.index
    df["trinity_w_15"] = pd.to_numeric(df["trinity_w_15"], errors='coerce')
    df = df[['symbol', "trinity_w_15"]]
    df = df.T.reset_index()
    df['timestamp_est'] = datetime.now(est)
    # df = df.set_index('timestamp_est', drop=True)
    df = df[[i for i in df.columns if i != 'index']]
    df = df.tail(1)
    # df2 = df.copy()
    # df2['timestamp_est'] = datetime.now(est).replace(minute=59)
    df_n = df.copy()
    for i in range(60):
       df_n['timestamp_est'] = datetime.now(est).replace(minute=i)
       df = pd.concat([df, df_n])

    json_data = df.to_json(orient='records')
    return json_data


  except Exception as e:
     print_line_of_error("trinity revrec fastapi")

def get_ticker_time_frame(symbols=['SPY']):
  try:


    ticker_db = read_QUEENs__pollenstory(
        symbols=symbols,
        read_storybee=False, 
        read_pollenstory=True,
    )
    df_main = False
    # for star in stars().keys():
    for symbol in symbols:
      df = ticker_db.get('pollenstory')[f'{symbol}_{"1Minute_1Day"}']
      df = df[['timestamp_est', 'macd_tier']] #'ticker_time_frame',
      df = df.rename(columns={'macd_tier': symbol})
      df = add_priorday_tic_value(df)

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