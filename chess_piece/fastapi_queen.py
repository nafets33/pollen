#find and read the pkl file in the folder.
import requests
import os
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import pytz
import random
import copy
from chess_piece.king import (return_QUEEN_KING_symbols, return_QUEENs__symbols_data, 
                              kingdom__global_vars, ReadPickleData, streamlit_config_colors, 
                              hive_master_root, stars, PickleData, hive_master_root_db, 
                              read_QUEENs__pollenstory, print_line_of_error)
from chess_piece.queen_hive import (return_symbol_from_ttf, 
                                    add_trading_model, 
                                    find_symbol_in_chess_board, 
                                    split_today_vs_prior, 
                                    order_vars__queen_order_items,
                                    power_amo,
                                    init_queenbee,
                                    return_trading_model_trigbee,
                                    ttf_grid_names,
                                    sell_button_dict_items,
                                    wave_buy__var_items,
                                    star_names,
                                    init_clientUser_dbroot,
                                    init_qcp_workerbees,
                                    chessboard_button_dict_items,
                                    read_swarm_db,
                                    shape_chess_board,
                                    remove_symbol_from_chess_board,
                                    add_symbol_to_chess_board,
                                    init_swarm_dbs,
                                    assign_block_time,
                                    
                                    )

from chess_piece.queen_bee import execute_buy_order, get_priceinfo_snapshot, symbol_is_crypto, handle_broker
from chess_piece.queen_mind import refresh_chess_board__revrec, init_qcp, kings_order_rules
from chess_utils.conscience_utils import story_return, return_waveview_fillers, generate_shade, get_powers
# from chess_utils.trigrule_utils import trig_rule_ID
from chess_piece.pollen_db import PollenDatabase
from dotenv import load_dotenv


pd.options.mode.chained_assignment = None  # default='warn' Set copy warning


est = pytz.timezone("US/Eastern")

main_root = hive_master_root() # os.getcwd()  # hive root
load_dotenv(os.path.join(main_root, ".env"))
db_root = os.path.join(main_root, "db")

pg_migration = os.environ.get('pg_migration')


 ###### Helpers UTILS


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

def get_revrec_lastmod_time(client_user, prod, api_lastmod_key='REVREC'):
  db_root = init_clientUser_dbroot(client_username=client_user, pg_migration=pg_migration)
  table_name = 'client_user_store' if prod else 'client_user_store_sandbox'
  dbs = dict(PollenDatabase.get_all_keys_with_timestamps(table_name, db_root))
  dbs = {'lastModified': str(v) for k, v in dbs.items() if api_lastmod_key in k}
  return dbs

def get_keyTable_lastmod_time(client_user, prod, table_key='REVREC'):
  db_root = init_clientUser_dbroot(client_username=client_user, pg_migration=pg_migration)
  table_name = 'db' if prod else 'db_sandbox'
  dbs = dict(PollenDatabase.get_all_keys_with_timestamps(table_name, db_root))
  dbs = {'lastModified': str(v) for k, v in dbs.items() if table_key in k}
  return dbs

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

### CACHE
def get_bishop_cache(key=None):
    """
    Simple function to get BISHOP data from cache API.
    
    Args:
        key: Optional specific key (e.g., 'ticker_info', '2025_Screen')
    
    Returns:
        dict or DataFrame
    """
    API_URL = os.getenv('fastAPI_url', 'http://localhost:8000')
    
    try:
        if key:
            # Get specific key
            url = f"{API_URL}/cache/bishop/{key}"
        else:
            # Get summary
            url = f"{API_URL}/cache/bishop"
        
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            # # Convert to DataFrame if it's a list of records
            # if key and 'data' in data and isinstance(data['data'], list):
            #     return pd.DataFrame(data['data'])
            
            return data
        else:
            print(f"❌ API Error: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return None
####### Router Calls

def get_waveview_state_for_ttf(revrec, wave_view_name, ttf):
   df_wave = revrec.get('waveview').loc[ttf].get(wave_view_name)
   return df_wave.loc[ttf].get('macd_state')

def validate_return_kors(king_order_rules, kors):
  kor_keys = king_order_rules.keys()
  for rule, value in kors.items():
    if rule not in kor_keys:#['wave_amo', 'close_order_today', 'take_profit', 'sell_out', 'sell_trigbee_trigger', 'sell_trigbee_date']: # validated items to add orules
      print("WTF RULE", rule)
      continue

    if rule == 'wave_amo':
      if type(value) != float:
        value = float(value)
    elif rule in['close_order_today', 'ignore_allocation_budget']:
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
    elif rule == 'sell_trigbee_date': # KEEP as STRING
       print(rule, value)
       pass # check datetime is greate then if not change to now WORKERBEE
    
        # if type(value) != datetime:
        #   value = pd.datetime(value)
        
    king_order_rules.update({rule: value})

  return king_order_rules
    

def return_startime_from_ttf(ticker_time_frame):
   t,tt,f = ticker_time_frame.split("_")
   return f'{tt}_{f}'


def app_buy_order_request(client_user, prod, selected_row, kors, ready_buy=False, story=False, trigbee='buy_cross-0', long_short='long', wave_buy_orders=[], wave_buys=False, buy_amount_field="allocation_long"): # index & wave_amount
  try:
    #WORKERBEE Handling Crypto, # workerbee add check for buying amount allowed
    
    df_wave_buys = pd.DataFrame(wave_buy_orders)
    if wave_buys:
      if len(df_wave_buys) > 0:
        df_wave_buys['close_order_today'] = df_wave_buys['close_order_today'].astype(bool)
        df_wave_buys[buy_amount_field] = pd.to_numeric(df_wave_buys[buy_amount_field], errors='coerce').fillna(0)
        df_wave_buys = df_wave_buys[(df_wave_buys['confirm_buy'] == True) & (df_wave_buys[buy_amount_field] > 0)]
        if df_wave_buys.empty:
          return grid_row_button_resp(status='error', description='No valid wave buy orders to process.', message_type='fade', close_modal=False, color_text='red', error=True)
      else:
        return grid_row_button_resp(status='error', description='No valid wave buy orders to process.', message_type='fade', close_modal=False, color_text='red', error=True)

    # WORKERBEE handle long short
    qb = init_queenbee(client_user=client_user, prod=prod, queen_king=True, api=True, revrec=False, queen_heart=True, pg_migration=pg_migration)
    QUEEN_KING = qb.get('QUEEN_KING')
    api = qb.get('api')
    # revrec = qb.get('revrec') # qb.get('queen_revrec') # WORKERBEE but shouldn't we just use RevRec anyways?
    QUEENsHeart = qb.get('QUEENsHeart')
    portfolio = QUEENsHeart['heartbeat'].get('portfolio')

    buy_package = create_AppRequest_package(request_name='buy_orders')
    # buy_package.update({'buy_order': {}})
    blessing={} #{i: '': for i in []}, # order_vars
    
    # Broker
    broker = kors['broker']
    broker = handle_broker(broker)
    print("BROKER", broker)
    # Trading Model
    if not wave_buys:
      symbol = selected_row.get('symbol')
      if story:
        ticker_time_frame = kors.get('star')
        tticker, tframe, frame = ticker_time_frame.split("_")
        star_time = return_startime_from_ttf(ticker_time_frame)
        wave_blocktime = assign_block_time(tframe)
      else:
        star_time=star_names(kors.get('star_list')[0])
        ticker_time_frame = f'{symbol}_{star_time}'
        tticker, tframe, frame = ticker_time_frame.split("_")
        wave_blocktime = assign_block_time(tframe)

    wave_buy_cols_float = ['star_total_budget', 'remaining_budget',
          'star_borrow_budget', 'remaining_budget_borrow', 'star_at_play',
          'star_at_play_borrow', 'allocation_long', 'allocation_long_deploy',
          'allocation_deploy', 'limit_price', 'take_profit', 'sell_out',
          buy_amount_field, ] # 'close_order_today', 'sell_trigbee_date', ''confirm_buy'
    
    orders_saved_msg = []
    if wave_buys and len(df_wave_buys) > 0:
      # sell_trigbee_date=datetime.now(est).strftime('%m/%d/%YT%H:%M')
      # df_wave_buys['sell_trigbee_date'] = df_wave_buys['sell_trigbee_date'].fillna(datetime.now(est).strftime('%m/%d/%YT%H:%M'))
      df_wave_buys['close_order_today'] = df_wave_buys['close_order_today'].astype(bool)
      for col in wave_buy_cols_float:
        if col in df_wave_buys.columns:
          df_wave_buys[col] = pd.to_numeric(df_wave_buys[col], errors='coerce').fillna(0)
      for idx, row in df_wave_buys.iterrows():
        # KORS
        kors = {}
        kors['take_profit'] = row.get('take_profit', 0)
        kors['limit_price'] = row.get('limit_price', 0)
        kors['sell_out'] = row.get('sell_out', 0)
        kors['close_order_today'] = row.get('close_order_today', False)
        kors['sell_trigbee_date'] = row.get('sell_trigbee_date', False)
        kors['sell_trigbee_date'] = pd.to_datetime(kors['sell_trigbee_date']).strftime('%m/%d/%YT%H:%M')
        kors['ignore_allocation_budget'] = row.get('ignore_allocation_budget', False)
        kors['wave_amo'] = row.get(buy_amount_field, 0)
        kors['limit_price'] = row.get('limit_price', 0)
        
        # Trading Model
        ticker_time_frame = row['ticker_time_frame']
        trigbee = row.get('macd_state', 'buy_cross-0')
        symbol, tframe, frame = ticker_time_frame.split("_")
        star_time = f'{tframe}_{frame}'
        wave_blocktime = assign_block_time(tframe)
        trading_model = QUEEN_KING['king_controls_queen']['symbols_stars_TradingModel'].get(symbol) # main symbol for Model (SPY)
        if not trading_model:
          trading_model = QUEEN_KING['king_controls_queen']['symbols_stars_TradingModel'].get("SPY")
        tm_trig = return_trading_model_trigbee(tm_trig=trigbee, trig_wave_length=trigbee.split("-")[-1]) # Ensure Trading Model TrigName
        king_order_rules = copy.deepcopy(trading_model['stars_kings_order_rules'][star_time]['trigbees'][tm_trig][wave_blocktime])
        
        # Other Misc
        crypto_currency_symbols = ['BTCUSD', 'ETHUSD', 'BTC/USD', 'ETH/USD']
        crypto = True if symbol in crypto_currency_symbols else False
        maker_middle = False
        current_wave = {} # deprecate revrec['waveview'].get('current_wave')
        current_macd_cross__wave = {} # deprecate
        power_up_amo = power_amo() # deprecate?
        borrowed_funds = True # USER INITIATE
        latest_kors = kings_order_rules()
        latest_kors = {k:v for k,v in latest_kors.items() if k not in king_order_rules} # remove any keys that we don't want to overwrite
        king_order_rules = {**king_order_rules, **latest_kors} # add any new rules to the mix
        kors = validate_return_kors(king_order_rules, kors)
        wave_amo = kors.get('wave_amo')

        blessing = order_vars__queen_order_items(trading_model=trading_model.get('theme'), 
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
                                                    long_short=long_short,
                                                    )
        # print("BLESSING", blessing)

        exx = execute_buy_order(
                        broker=broker,
                        order_key=QUEEN_KING.get('db_root'),
                        prod=prod,
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
          buy_package = create_AppRequest_package(request_name='buy_orders', client_order_id=exx.get('new_queen_order').get('client_order_id'))
          print("APP EXX Order", buy_package)

          buy_package.update({'new_queen_order': exx.get('new_queen_order')})

          # save
          QUEEN_KING['buy_orders'].append(buy_package)

          if pg_migration:
            PollenDatabase.upsert_data(QUEEN_KING.get('table_name'), key=QUEEN_KING.get('key'), value=QUEEN_KING)
          else:
            PickleData(QUEEN_KING.get('source'), QUEEN_KING)
          
          orders_saved_msg.append(f' >{symbol} purchased<')
        else:
          orders_saved_msg.append(f' >{symbol} purchase failed<')

      return {'status': True, 'msg': orders_saved_msg}

    elif story:
      trading_model = QUEEN_KING['king_controls_queen']['symbols_stars_TradingModel'].get(symbol) # main symbol for Model (SPY)
      if not trading_model:
        trading_model = QUEEN_KING['king_controls_queen']['symbols_stars_TradingModel'].get("SPY")
      # Ensure Trading Model TrigName
      tm_trig = return_trading_model_trigbee(tm_trig=trigbee, trig_wave_length=trigbee.split("-")[-1])
      if ready_buy:
        tm_trig = f'sell_cross-0' if 'buy' in tm_trig else f'buy_cross-0'
      # Copy TM
      king_order_rules = copy.deepcopy(trading_model['stars_kings_order_rules'][star_time]['trigbees'][tm_trig][wave_blocktime])
      # Other Misc
      crypto_currency_symbols = ['BTCUSD', 'ETHUSD', 'BTC/USD', 'ETH/USD']
      crypto = True if symbol in crypto_currency_symbols else False
      maker_middle = False
      current_wave = {} # revrec['waveview'].get('current_wave')
      current_macd_cross__wave = {}
      power_up_amo = power_amo()
      borrowed_funds = True # USER INITIATE
      borrow_qty = False ## DEPRECIATE
      latest_kors = kings_order_rules()
      latest_kors = {k:v for k,v in latest_kors.items() if k not in king_order_rules} # remove any keys that we don't want to overwrite
      king_order_rules = {**king_order_rules, **latest_kors} # add any new rules to the mix
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
                                                  long_short=long_short,
                                                  )
      blessing = order_vars

      exx = execute_buy_order(
                      broker=broker,
                      order_key=QUEEN_KING.get('db_root'),
                      prod=prod,
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

        buy_package.update({'new_queen_order': exx.get('new_queen_order')})   

        # save
        QUEEN_KING['buy_orders'].append(buy_package)

        if pg_migration:
          PollenDatabase.upsert_data(QUEEN_KING.get('table_name'), key=QUEEN_KING.get('key'), value=QUEEN_KING)
        else:
          PickleData(QUEEN_KING.get('source'), QUEEN_KING)

        print("SAVED ORDER TO QK")
        return {'status': True, 'msg': f'{symbol} purchased'}
      else:
        print("Ex Failed")
        return {'status': False, 'msg': "Ex Failed"}
    
    else:
       return {'status': False, 'msg': "Not an Options"}
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


def app_Sellorder_request(client_user, prod, process_type, selected_row, default_value, df_sells=[]): # sell_orders
  # WORKERBEE attempt to handle WashSale Rule
  try:
    king_G = kingdom__global_vars()
    RUNNING_Orders = king_G.get('RUNNING_Orders') # = ['running', 'running_open']
    qb = init_queenbee(client_user=client_user, prod=prod, orders_v2=True, queen_king=True, api=True, orders=True, pg_migration=pg_migration)
    QUEEN_KING = qb.get('QUEEN_KING')
    api = qb.get('api')
    ORDERS = qb.get('ORDERS')
    if type(ORDERS) != dict:
      print("NO ORDERS")
      return grid_row_button_resp(description="NO ORDERS AVAILABLE")
    
    queen_order = ORDERS['queen_orders']
    queen_order['qty_available'] = pd.to_numeric(queen_order['qty_available'], errors='coerce')


    selected_client_order_ids = {}
    status = ''
    save=False
    number_shares = 0
    if len(df_sells) > 0 and process_type == 'batch':
      for idx, row in df_sells.iterrows():
        client_order_id = row.get('client_order_id')
        symbol = row.get('ticker_time_frame').split("_")[0]
        crypto = symbol_is_crypto(symbol)
        if client_order_id in queen_order.index:
            number_shares = int(row.get('sell_qty', 0))
            sell_amount = int(row.get('sell_amount', 0))
            if number_shares > 0:
              number_shares = min(queen_order.loc[client_order_id, 'qty_available'], number_shares)
              if number_shares <=0:
                print("NO SHARES TO SELL", client_order_id)
                continue
            elif sell_amount > 0:
              ask_price = get_priceinfo_snapshot(api=api, ticker=symbol, crypto=crypto).get('ask')
              if not crypto:
                if sell_amount < ask_price:
                  print("SELL AMOUNT LESS THAN ASK PRICE")
                  status = "SELL AMOUNT LESS THAN ASK PRICE"
                elif ask_price > 0:
                  number_shares = sell_amount / ask_price
                  number_shares = max(1, int(number_shares)) if not crypto else round(number_shares, 8)
              else: # crypto
                number_shares = sell_amount / ask_price
                number_shares = round(number_shares, 8)
            else:
              print("NO SELL QTY OR AMOUNT")
              status = "NO SELL QTY OR AMOUNT"
              continue

            # limit_price = int(row.get('limit_price', 0))
            # # Sell Order
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


    # WORKERBEE validate to ensure number of shares available to SELL as user can click twice
    if process_type in ['single', 'specific']:
      symbol = selected_row.get('symbol')
      client_order_id = selected_row.get('client_order_id')
      number_shares = int(default_value.get('sell_qty', 0))
      sell_amount = int(default_value.get('sell_amount', 0))
      limit_price = int(default_value.get('limit_price', 0))
      crypto = symbol_is_crypto(symbol)
      if number_shares == 0 and sell_amount == 0:
          print("SELL AMOUNT IS 0")
          return grid_row_button_resp(status='error', description="SELL AMOUNT IS 0")
      if sell_amount > 0:
        ask_price = get_priceinfo_snapshot(api=api, ticker=symbol, crypto=crypto).get('ask')
        if not crypto:
            if sell_amount < ask_price:
              print("SELL AMOUNT LESS THAN ASK PRICE")
              return grid_row_button_resp(status='error', description="SELL AMOUNT LESS THAN ASK PRICE", error=True)
        
        number_shares = sell_amount / ask_price #selected_row.get('current_ask') WORKERBEE until it can be trusted
        print("SELL AMOUNT: ", number_shares, ' sell amount', sell_amount, ' ask price', ask_price)
      
      number_shares = max(1, int(number_shares)) if not crypto else round(number_shares,8)

      if client_order_id and process_type == 'specific':
        # VALIDATE check against available_shares and validate amount
        df = queen_order.loc[client_order_id]
        qty_available = float(df.get('qty_available'))
        number_shares = qty_available if number_shares > qty_available else number_shares 
        selected_client_order_ids = {client_order_id: number_shares}
      elif len(df_sells) == 0 and process_type == 'single':
        print("SELL AMOUNT: Find Available Orders")
        selected_client_order_ids = {}
        # define available orders # WORKERBEE FINISH STORE Func
        orders_avial = queen_order[(queen_order['symbol']==symbol) & (queen_order['qty_available'] > 0) & (queen_order['queen_order_state'].isin(RUNNING_Orders)) & (queen_order['side'] == 'buy')]
        # filter to available orders
        if len(orders_avial) > 0:
            # sort by borrowed = True
            # sort by time purchased
            orders_avial = orders_avial.sort_values(by=['borrowed_funds', 'datetime'], ascending=[False, True])
            cumulative_sum = 0

            # Iterate over DataFrame rows
            for client_order_id, row in orders_avial.iterrows():
                # Add qty_available to cumulative sum
                qty_available = row.get('qty_available', 0)
                if not isinstance(qty_available, (float, int)):
                  print("qty_available NOT AVAILABLE", qty_available)
                  continue
                cumulative_sum += row.get('qty_available', 0)              
                # Check if cumulative sum exceeds or equals numshares
                if cumulative_sum >= number_shares:
                    # Calculate remaining qty_available to satisfy numshares
                    remaining_qty = number_shares - (cumulative_sum - qty_available)
                    selected_client_order_ids[client_order_id] = remaining_qty
                    break
                else:
                    selected_client_order_ids[client_order_id] = qty_available


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


def app_queen_order_update_order_rules(client_user, prod, selected_row, default_value):
    try:
      current_kors = kings_order_rules()
      queen_order = selected_row
      client_order_id = queen_order.get('client_order_id')
      kors = queen_order.get('order_rules', None) # need ruleS
      QUEEN_KING = init_queenbee(client_user=client_user, prod=prod, queen_king=True, pg_migration=pg_migration).get('QUEEN_KING')
      order_update_package = create_AppRequest_package(request_name='update_order_rules', client_order_id=client_order_id)
      order_update_package['update_order_rules'] = {}

      if kors:
        update_dict = {}
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
      else:
         update_dict = default_value
        
      if update_dict:
        order_update_package['update_order_rules'].update({client_order_id: update_dict})
        print(order_update_package['update_order_rules'])
      
        QUEEN_KING['update_order_rules'].append(order_update_package)
        
        if pg_migration:
          table_name = 'client_user_store' if prod else 'client_user_store_sandbox'
          PollenDatabase.upsert_data(table_name, key=QUEEN_KING.get('key'), value=QUEEN_KING)
        else:
          PickleData(QUEEN_KING.get('source'), QUEEN_KING)

        return grid_row_button_resp(status="Success", description=str(order_update_package['update_order_rules']))

      else:
        msg = ("no updates to kors")
        return grid_row_button_resp(status="No Changes", description=msg, error=True)
         
    except Exception as e:
       print_line_of_error(e)
       return grid_row_button_resp(status="Error", description=str(e), error=True)

def load_bishop_data(prod):

  if pg_migration:
      BISHOP = read_swarm_db(prod, 'BISHOP')
  else:
      db = init_swarm_dbs(prod)
      BISHOP = ReadPickleData(db.get('BISHOP'))
  ticker_info = BISHOP.get('ticker_info', {})
  # ticker_info = ticker_info.set_index('symbol')
  return ticker_info.to_json(orient='records')

## MAIN GRIDS


def get_queen_orders_json(client_user, username, prod, toggle_view_selection): # get_orders, return_orders
  
  try:
      toggle_view_selection = toggle_view_selection.split("-")[0].strip()
      if toggle_view_selection.lower() in ['queen', 'portfolio']:
          ORDERS = init_queenbee(client_user, prod, queen=True, orders_v2=True, pg_migration=pg_migration).get('QUEEN')
      # elif toggle_view_selection.lower() == 'final':
      #     ORDERS = init_queenbee(client_user, prod, orders_final=True, orders_v2=True, pg_migration=pg_migration).get('ORDERS_FINAL')
      else:
          ORDERS = init_queenbee(client_user, prod, orders=False, orders_v2=True, pg_migration=pg_migration).get('ORDERS')
      
      if isinstance(ORDERS, pd.DataFrame):
         df = ORDERS
      else:
         df = ORDERS['queen_orders']

      if len(df) == 1:
        print("init queen")
        return df.to_json(orient='records')
      
      # king_G = kingdom__global_vars()
      # active_queen_order_states = king_G.get('active_queen_order_states')

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
      df['color_row_text'] = np.where(df['honey'] > 0, default_text_color, default_text_color)
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

      for ttf in df.index:
        symbol = df.at[ttf, 'symbol']
        sell_qty = df.at[ttf, 'qty_available']
        sell_option = sell_button_dict_items(symbol, sell_qty)
        df.at[ttf, 'sell_option'] = sell_option

      # sort
      sort_colname = 'cost_basis_current'
      df = df.sort_values(sort_colname, ascending=False)
      
      # # # Totals Index
      # df.loc['Total', 'money'] = df['money'].sum()
      # df.loc['Total', 'honey'] = df['honey'].sum()
      # # df.loc['Total', 'datetime'] = ''
      # df.loc['Total', 'cost_basis'] = df['cost_basis'].sum()
      # df.loc['Total', 'cost_basis_current'] = df['cost_basis_current'].sum()
      # newIndex=['Total']+[ind for ind in df.index if ind!='Total']
      # df=df.reindex(index=newIndex)

      json_data = df.to_json(orient='records')
      return json_data
  except Exception as e:
    print_line_of_error(f"{e} Orders Failed")


def get_storygauge_waveview_json(client_user, prod, symbols, toggle_view_selection=['queen'], return_type='waves', revrec=None):
    toggle_view_selection = toggle_view_selection.split("-")[0].strip()
    def update_col_number_format(df, float_cols=['trinity', 'current_profit', 'maxprofit', 'current_profit_deviation']):
      for col in df.columns:
        # print(type(df_storygauge.iloc[-1].get(col)))
        if type(df.iloc[-1].get(col)) == np.float64:
            if col in float_cols:
              df[col] = round(df[col] * 100,2)
            else:
                df[col] = round(df[col],2)
      return df
    qk_chessboard = None
    try:
      s = datetime.now()

      if toggle_view_selection.lower() in ['queen', 'portfolio']:
        qb = init_queenbee(client_user, prod, revrec=True, queen_king=True, pg_migration=pg_migration)
        revrec = qb.get('revrec')
        QUEEN_KING = qb.get('QUEEN_KING')

      elif toggle_view_selection.lower() == 'king': # revrec refresh
        king_G = kingdom__global_vars()
        qb = init_queenbee(client_user=client_user, prod=prod, orders_v2=True, queen=True, queen_king=True, revrec=True, pg_migration=pg_migration)
        QUEEN = qb.get('QUEEN')
        QUEEN_KING = qb.get('QUEEN_KING')
        if pg_migration:
            symbols = return_QUEEN_KING_symbols(QUEEN_KING, symbols=QUEEN['revrec']['storygauge'].index.tolist())
            STORY_bee = PollenDatabase.retrieve_all_story_bee_data(symbols).get('STORY_bee')
        else:
            STORY_bee = return_QUEENs__symbols_data(QUEEN=QUEEN, QUEEN_KING=QUEEN_KING, read_storybee=True, read_pollenstory=False).get('STORY_bee') ## async'd func
        revrec = refresh_chess_board__revrec(QUEEN['account_info'], QUEEN, QUEEN_KING, STORY_bee, king_G.get('active_queen_order_states')) ## Setup Board
      
      # elif toggle_view_selection == "Not On Board":
                   
      elif toggle_view_selection == '2025_Screen':
        screen = toggle_view_selection
        king_G = kingdom__global_vars()
        qb = init_queenbee(client_user=client_user, prod=prod, queen=True, orders_v2=True, queen_king=True, api=True, pg_migration=pg_migration)
        QUEEN = qb.get('QUEEN')
        acct_info = QUEEN.get('account_info')
        QUEEN_KING = qb.get('QUEEN_KING')
        active_queen_order_states = king_G.get('active_queen_order_states')
        
        workerbees = 'workerbees'
        QUEENBEE = {workerbees: {}}
        db = init_swarm_dbs(prod)
                
        if pg_migration:
            BISHOP = read_swarm_db(prod, 'BISHOP')
        else:
            BISHOP = ReadPickleData(db.get('BISHOP'))
        
        df = BISHOP.get(screen)
        for sector in set(df['sector']):
            token = df[df['sector']==sector]
            tickers=token['symbol'].tolist()
            QUEENBEE[workerbees][sector] = init_qcp_workerbees(ticker_list=tickers, buying_power=0)
        
        QUEEN_KING['chess_board'] = QUEENBEE['workerbees']
        symbols = [item for sublist in [v.get('tickers') for v in QUEEN_KING['chess_board'].values()] for item in sublist]
        s = datetime.now()
        if pg_migration:
            symbols = return_QUEEN_KING_symbols(QUEEN_KING, QUEEN)
            STORY_bee = PollenDatabase.retrieve_all_story_bee_data(symbols).get('STORY_bee')
        else:
            symbols = [item for sublist in [v.get('tickers') for v in QUEEN_KING['chess_board'].values()] for item in sublist]
            STORY_bee = return_QUEENs__symbols_data(QUEEN=QUEEN, QUEEN_KING=QUEEN_KING, swarmQueen=False, read_pollenstory=False).get('STORY_bee')

        revrec = refresh_chess_board__revrec(acct_info, QUEEN, QUEEN_KING, STORY_bee, active_queen_order_states, wave_blocktime='morning_9-11') ## Setup Board
        
      else:
        # hedge funds
        qb = init_queenbee(client_user, prod, revrec=True, queen=True, queen_king=True, pg_migration=pg_migration)
        revrec = qb.get('revrec')
        QUEEN_KING = qb.get('QUEEN_KING')
        
        QUEEN = qb.get('QUEEN')

        def read_filer_names_coverpage():
          # df = pd.read_csv(os.path.join(hive_master_root_db(), 'COVERPAGE.tsv'), sep='\t')
          df = PollenDatabase.retrieve_data('hedgefund_13f_data', 'COVERPAGE')
          return df
        # Get the available hedge fund accession numbers
        all_avail_hfunds = set(PollenDatabase.get_all_keys('hedgefund_holdings'))
        # Read the filing names
        df = read_filer_names_coverpage()
        # Filter only rows where ACCESSION_NUMBER is in all_avail_hfunds
        df_filtered = df[df['ACCESSION_NUMBER'].isin(all_avail_hfunds)]
        filer_names_ = dict(zip(df_filtered['FILINGMANAGER_NAME'], df_filtered['ACCESSION_NUMBER']))

        if toggle_view_selection in filer_names_.keys():
            sl = datetime.now()         
            ACCESSION_NUMBER = filer_names_[toggle_view_selection]
            data = PollenDatabase.retrieve_data('hedgefund_holdings', ACCESSION_NUMBER)
            data['VALUE'] = pd.to_numeric(data['VALUE'], errors='coerce')
            data = data.groupby(['symbol']).agg({'VALUE': 'sum'}).reset_index()
            data['buying_power'] = data['VALUE'] / data['VALUE'].sum()
            data['pct_portfolio'] = data['VALUE'] / data['VALUE'].sum()
            data = data.set_index('symbol')
            print("ACCESSION_NUMBER runtime: ", (datetime.now() - sl).total_seconds())
            
            # data = hedge_funds[hedge_funds['filer_name'] == toggle_view_selection]
            # data = data.drop_duplicates(subset='stock_ticker')
            # data = data.set_index('stock_ticker', drop=False)
            # if data.iloc[0].get('current_percent_of_portfolio') == 'DROPME':
            #    data['current_percent_of_portfolio'] = 1 / len(data)
            # data['current_percent_of_portfolio'] = pd.to_numeric(data['current_percent_of_portfolio'], errors='coerce')
            # data = data[data['current_percent_of_portfolio'] > 0]
            # data['buying_power'] = data['current_percent_of_portfolio'] / 100
            sb = datetime.now()
            symbols = []
            board = {}
            for ticker in data.index:
                if ticker in symbols:
                   print("DUP Ticker", ticker)
                   continue # duplicate

                buying_power = data.loc[ticker].get('buying_power')
                symbols.append(ticker)
                board[ticker] = init_qcp(ticker_list=[ticker], buying_power=buying_power, piece_name=ticker)
            
            QUEEN_KING[toggle_view_selection] = board
            if 'SPY' not in symbols:
                print("SPY not in symbols")
                symbols.append('SPY')
            print("INIT runtime: ", (datetime.now() - sb).total_seconds())

            sb = datetime.now()
            STORY_bee = PollenDatabase.retrieve_all_story_bee_data(symbols).get('STORY_bee')
            print("STORY_bee runtime: ", (datetime.now() - sb).total_seconds())

            # % Change per Star failed couldn't get it to work?
            # storybee_pct_change = {}
            # STORY_bee_keys = STORY_bee.keys()
            # for symbol in symbols:
            #     for star in stars().keys():
            #         if f'{symbol}_{star}' in STORY_bee_keys:
            #             pct_change = STORY_bee[f'{symbol}_{star}']['story'].get('last_close_price')
            #             # storybee_pct_change[f'{symbol}{star}_change'] = pct_change
            #             data.at[symbol, f'{symbol}{star}_change'] = pct_change if pct_change else 89
            #         else:
            #             print(symbol, star, "not in STORY_bee_keys")
            #             data.at[symbol, f'{symbol}{star}_change'] = 89
            # df_story = data
            sb = datetime.now()
            revrec = refresh_chess_board__revrec(acct_info=QUEEN.get('account_info'), QUEEN=QUEEN, QUEEN_KING=QUEEN_KING, STORY_bee=STORY_bee, check_portfolio=False, chess_board=toggle_view_selection, exit_early=True) ## Setup Board
            print("RevRec runtime: ", (datetime.now() - sb).total_seconds())
            df_story = revrec['storygauge']
            df_story['pct_portfolio'] = df_story.index.map(dict(zip(data.index, data['pct_portfolio'])))
            # check for new storybee data and call it
            # you could also consider waveview?
            # symbols = revrec['storygauge'].index.tolist()
            sb_symbols = set([i.split("_")[0] for i in STORY_bee.keys()])
            missing = [i for i in symbols if i not in list(sb_symbols)]
            if missing:
              print("NEED SYMBOLS", missing)

              # queen_workerbees(
              #                 qcp_s=['apicall'],
              #                 QUEENBEE=QUEENBEE,
              #                 prod=prod, 
              #                 reset_only=True, 
              #                 pg_migration=pg_migration,
              #                 upsert_to_main_server=True,
              #                     )

              return df_story.to_json(orient='records')

        else:
           revrec = init_queenbee(client_user, prod, revrec=True).get('revrec')

      if type(revrec.get('waveview')) != pd.core.frame.DataFrame:
        print(f'rr not df null, {revrec}')
        return pd.DataFrame().to_json()

      if len(symbols) == 0:
        symbols=['SPY']

      k_colors = streamlit_config_colors()
      default_text_color = k_colors['default_text_color'] # = '#59490A'
      # default_font = k_colors['default_font'] # = "sans serif"
      # default_yellow_color = k_colors['default_yellow_color'] # = '#C5B743'

      if return_type == 'waves':
        waveview = revrec.get('waveview')
        sw = datetime.now()
        df_waveview = return_waveview_fillers(QUEEN_KING, waveview)
        print("wave runtime: ", (datetime.now() - sw).total_seconds())
        
        df = df_waveview
          
        df['color_row'] = df['macd_state'].apply(lambda x: generate_shade(x, wave=True))
        df['color_row_text'] = default_text_color

        df = update_col_number_format(df)
        df = filter_gridby_timeFrame_view(df, toggle_view_selection, grid='wave')

        json_data = df.to_json(orient='records')
        print((datetime.now() - s).total_seconds())
        return json_data

      elif return_type == 'story':
        qk_chessboard = copy.deepcopy(QUEEN_KING['chess_board'])
        
        print('prod', prod)
        df = story_return(QUEEN_KING, revrec, toggle_view_selection, qk_chessboard)

        # BISHOP DATA MERGE
        data = get_bishop_cache()
        if isinstance(data['ticker_info'], str):
            # Parse JSON string to list
            import json
            parsed_data = json.loads(data['ticker_info'])
            ticker_info = pd.DataFrame(parsed_data)
        elif isinstance(data['ticker_info'], list):
            ticker_info = pd.DataFrame(data['ticker_info'])
        else:
            ticker_info = data['ticker_info']
    
        if len(ticker_info) > 0:
           bishop_cols = ['symbol', 'sector', 'shortName', 'industry', 'website', 'city', 'country', 'longBusinessSummary']
           df_info = ticker_info[bishop_cols]
           info_symbols = df_info['symbol'].tolist()
           df_symbols = df.index.tolist()
           missing_symbols = [sym for sym in df_symbols if sym not in info_symbols]
           if missing_symbols:
              print("Missing BISHOP symbols:", missing_symbols)
          #  df_info = df_info.set_index(df_info['symbol'])
          #  print("Merging BISHOP data", df_info.head())
          #  df = df.merge(df_info, how='left', left_index=True, right_index=True)
           for col in bishop_cols:
              if col != 'symbol':
                df[col] = df.index.map(dict(zip(df_info['symbol'], df_info[col]))).fillna('N/A')

        # for idx in df.index:
        #     df.at[idx, 'nestedRows'] = [{
        #         'count_on_me': 89,
        #         'nestedRows': [{
        #             'count_on_her': 89,
        #             'nestedRows': [{
        #                 'count_on_them': 89
        #             }]
        #         }]
        #     }]

        json_data = df.to_json(orient='records')
        print("story runtime: ", (datetime.now() - s).total_seconds())
        return json_data
    
    except Exception as e:
      print_line_of_error(e)


def chessboard_view(client_user, prod, symbols, toggle_view_selection):
  QUEEN_KING = init_queenbee(client_user, prod, queen_king=True, pg_migration=pg_migration).get('QUEEN_KING')
  df = shape_chess_board(QUEEN_KING['chess_board'])
  df['refresh_star'] = 'Day'
  kors_dict = chessboard_button_dict_items()
  # df['kors'] = [kors_dict for _ in range(df.shape[0])]
  # for idx in df.index:
  #    df.at[idx, 'kors'] = kors_dict
  return df.to_json(orient='records')


def update_buy_autopilot(client_user, prod, selected_row, default_value, status='-'):
    print(client_user, default_value) 
    buy_autopilot = default_value.get('buy_autopilot')
    QUEEN_KING = init_queenbee(client_user, prod, queen_king=True, pg_migration=pg_migration).get('QUEEN_KING')
    symbol = selected_row.get('symbol')
    
    # ✅ Handle list of dicts instead of DataFrame
    ticker_autopilot = QUEEN_KING['king_controls_queen'].get('ticker_autopilot', [])
    
    # Ensure it's a list
    if not isinstance(ticker_autopilot, list):
        ticker_autopilot = []
    
    # Find existing entry for symbol
    existing_entry = None
    for idx, entry in enumerate(ticker_autopilot):
        if entry.get('symbol') == symbol:
            existing_entry = idx
            break
    
    # Update or add new entry
    if existing_entry is not None:
        # Update existing
        ticker_autopilot[existing_entry]['buy_autopilot'] = buy_autopilot
        status = f'{status} BUY AutoPilot Updated to {buy_autopilot}'
    else:
        # Add new entry
        ticker_autopilot.append({
            'symbol': symbol,
            'buy_autopilot': buy_autopilot,
            'sell_autopilot': False  # Default value
        })
        status = f'{status} BUY AutoPilot Created with value {buy_autopilot}'
    
    # Save back to QUEEN_KING
    QUEEN_KING['king_controls_queen']['ticker_autopilot'] = ticker_autopilot

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
    
    # ✅ Handle list of dicts instead of DataFrame
    ticker_autopilot = QUEEN_KING['king_controls_queen'].get('ticker_autopilot', [])
    
    # Ensure it's a list
    if not isinstance(ticker_autopilot, list):
        ticker_autopilot = []
    
    # Find existing entry for symbol
    existing_entry = None
    for idx, entry in enumerate(ticker_autopilot):
        if entry.get('symbol') == symbol:
            existing_entry = idx
            break
    
    # Update or add new entry
    if existing_entry is not None:
        # Update existing
        ticker_autopilot[existing_entry]['sell_autopilot'] = sell_autopilot
        status = f'{status} SELL AutoPilot Updated to {sell_autopilot}'
    else:
        # Add new entry
        ticker_autopilot.append({
            'symbol': symbol,
            'buy_autopilot': False,  # Default value
            'sell_autopilot': sell_autopilot
        })
        status = f'{status} SELL AutoPilot Created with value {sell_autopilot}'
    
    # Save back to QUEEN_KING
    QUEEN_KING['king_controls_queen']['ticker_autopilot'] = ticker_autopilot

    if pg_migration:
        table_name = 'client_user_store' if prod else 'client_user_store_sandbox'
        PollenDatabase.upsert_data(table_name, QUEEN_KING.get('key'), QUEEN_KING)
    else:
       PickleData(QUEEN_KING.get('source'), QUEEN_KING)
    
    print(status)
    return grid_row_button_resp(description=status)

def update_queenking_chessboard(client_user, prod, selected_row, default_value): # DEPRECATED NOT USED
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

  demo = True if client_user == 'stapinskistefan@gmail.com' else False

  if 'charlie_bee' not in QUEENsHeart.keys():
    df = pd.DataFrame()
  
  # heart
  if 'heartbeat' in QUEENsHeart.keys():
      # broker_qty_delta = QUEENsHeart['heartbeat'].get('broker_qty_delta')
      beat = round((datetime.now(est) - QUEENsHeart.get('heartbeat_time')).total_seconds(), 1)
      # beat = QUEENsHeart.get('heartbeat_beat', 0)
      avg_beat = QUEENsHeart.get('heartbeat_avg_beat', 0)
      if beat > 1989:
          beat = "zZzzz"

      long = QUEENsHeart['heartbeat'].get('long')
      short = QUEENsHeart['heartbeat'].get('short')
  else:
     beat = 0
     avg_beat = 0
     long = 0
     short = 0

  df = pd.DataFrame()
  brokers = ['Alpaca', 'RobinHood', 'Interactive Brokers', 'Etrade']
  for broker in brokers:
    crypto_value = 0

    # Account Info
    acct_info = broker_info
    if 'buying_power' not in acct_info.keys():
    # if len(acct_info) == 0:
        df_accountinfo = pd.DataFrame()
        acct_info = {'accrued_fees': 0.0,
                  'buying_power': 100000,
                  'cash': 0,
                  'daytrade_count': 0,
                  'last_equity': 100000,
                  'portfolio_value': 100000,}

    if broker != 'Alpaca':
      crypto_value = random.randint(20000, 80000) # fake crypto value for non-alpaca brokers  
      long = random.randint(50000, 100000)
      short = random.randint(0, 26000)
      portfolio_value = long + short + crypto_value
      buying_power = random.randint(50, 10000)
      if not demo:
        print("DEMO MODE - Randomizing values for non-Alpaca brokers")
        crypto_value = 0
        long = 0
        short = 0
        portfolio_value = 1
        buying_power = 0
      
      acct_info = {'accrued_fees': 0.0,
              'buying_power': buying_power,
              'cash': portfolio_value - long,
              'daytrade_count': 0,
              'last_equity': portfolio_value,
              'portfolio_value': portfolio_value,}


    # format
    # 1
    long = '${:,}'.format(long)
    short = '${:,}'.format(short)
    crypto_value = '${:,}'.format(crypto_value)
    # 2
    honey_text = '%{:,.2f}'.format(((acct_info['portfolio_value'] - acct_info['last_equity']) / acct_info['portfolio_value']) *100)
    money_text = '${:,.0f}'.format(acct_info['portfolio_value'] - acct_info['last_equity'])
    # 3
    buying_power = '${:,}'.format(round(acct_info.get('buying_power')))
    cash = '${:,}'.format(round(acct_info.get('cash')))
    daytrade_count = round(acct_info.get('daytrade_count'))
    portfolio_value = '${:,}'.format(round(acct_info.get('portfolio_value')))

    df_heart = pd.DataFrame([{'Broker': broker, 'Long': long, 'Short': short, 'Crypto': crypto_value, 'Heart Beat': beat, 'Avg Beat': avg_beat}])

    df_accountinfo = pd.DataFrame([{'Money': money_text, 'Day % Change': honey_text, 'Portfolio Value': portfolio_value, 'Cash': cash, 'Buying Power': buying_power, 'daytrade count': daytrade_count}])


    df_ = pd.concat([df_heart, df_accountinfo], axis=1)

    df = pd.concat([df, df_]).reset_index(drop=True)

    # for idx in df.index:
    #   df.at[idx, 'nestedRows'] = [{'count_on_me': 89, 'nestedRows': [{'count_on_her': 89}]}]
    # print("acoucnt", df)

  return df.to_json(orient='records')


# Add Symbol to Board
def queenking_symbol(client_user, prod, selected_row=None, default_value=None, triggers=None, triggers_only=False):
    starnames = star_names()
    starnames_margin = {f'{i} Margin': v for i, v in starnames.items()}
    table_name = 'client_user_store' if prod else 'client_user_store_sandbox'

    symbol = selected_row.get('symbol')
    
    QUEEN_KING = init_queenbee(client_user, prod, queen_king=True, pg_migration=pg_migration).get('QUEEN_KING')
    chess_board = QUEEN_KING['chess_board']
    
    # WORKERBEE only update if triggers differ for now just replace
    # Simple trigger update: find by trigger_id and replace, or add if new
    existing_trigrules = QUEEN_KING['king_controls_queen'].get('ticker_trigrules', [])
    if not isinstance(existing_trigrules, list):
        existing_trigrules = []
    
    # Create dict of existing triggers by trigger_id for easy lookup
    existing_by_id = {rule.get('trigger_id'): rule for rule in existing_trigrules if rule.get('trigger_id')}
    
    # Process triggers marked for saving
    triggers_to_save = [t for t in triggers if t.get('save_to_db') == True]
    if triggers_to_save:
      for trig in triggers_to_save:
          # Set Trigger ID
          trigger_id = f"{symbol}_{trig.get('trigrule_type')}_{trig.get('ttf')}"
          trig['trigger_id'] = trigger_id
          trig['save_to_db'] = False  # Flip save back
          
          # Replace or add
          if trigger_id in existing_by_id:
              # Update existing trigger
              existing_by_id[trigger_id].update(trig)
              print(f"✏️  QUEEN_KING Updated trigger: {trigger_id}")
          else:
              # Add new trigger
              existing_by_id[trigger_id] = trig
              print(f"➕ New trigger: {trigger_id}")
      
      # Convert back to list and save
      QUEEN_KING['king_controls_queen']['ticker_trigrules'] = list(existing_by_id.values())
      if triggers_only:
          if pg_migration:
              table_name = 'client_user_store' if prod else 'client_user_store_sandbox'
              PollenDatabase.upsert_data(table_name, QUEEN_KING.get('key'), QUEEN_KING)
          else:
             PickleData(QUEEN_KING.get('source'), QUEEN_KING)
          
          return grid_row_button_resp(description=f" {symbol} Trigger Rules Updated")

    trading_model = QUEEN_KING['king_controls_queen']['symbols_stars_TradingModel'].get(symbol)
    if not trading_model:
        print("MISSING TRADING MODEL adding model", symbol)
        QUEEN_KING = add_trading_model(QUEEN_KING=QUEEN_KING, ticker=symbol)
        trading_model = QUEEN_KING['king_controls_queen']['symbols_stars_TradingModel'][symbol]    
    for key, value in default_value.items():
        if key == 'buying_power':
            if 'buyingpower_allocation_LongTerm' in trading_model:
                trading_model['buyingpower_allocation_LongTerm'] = value
        elif key == 'borrow_power':
            if 'buyingpower_allocation_ShortTerm' in trading_model:
                trading_model['buyingpower_allocation_ShortTerm'] = value
        elif key == 'max_budget_allowed':
            if 'total_budget' in trading_model:
                trading_model['total_budget'] = value
        elif key in starnames.keys():
            if 'stars_kings_order_rules' in trading_model and starnames[key] in trading_model['stars_kings_order_rules']:
                trading_model['stars_kings_order_rules'][starnames[key]]['buyingpower_allocation_LongTerm'] = value
        elif key in starnames_margin.keys():
            margin_key = starnames[key.split(" ")[0]]
            if 'stars_kings_order_rules' in trading_model and margin_key in trading_model['stars_kings_order_rules']:
                trading_model['stars_kings_order_rules'][margin_key]['buyingpower_allocation_ShortTerm'] = value
        elif key == 'symbol_group':  # qcp data
            qcp = find_symbol_in_chess_board(chess_board, symbol)
            if qcp and value in chess_board.keys():
                if qcp != value:
                    if remove_symbol_from_chess_board(chess_board, symbol):
                        add_symbol_to_chess_board(chess_board, value, symbol)
        elif key == 'status': # qcp data ? change / remove
            # QUEEN_KING["chess_board"][ticker] = init_qcp(ticker_list=[ticker], buying_power=buying_power, piece_name=ticker)
            pass
                  

    # update trading model
    QUEEN_KING['king_controls_queen']['symbols_stars_TradingModel'][symbol] = trading_model
    QUEEN_KING['chess_board'] = chess_board

    # default_value
    # {'symbol': 'GOOG', 'buying_power': 0.125, 'borrow_power': 0, 'status': ['active', 'not_active'], 'refresh_star': ['1Minute_1Day', 'Day', 'Week', 'Month', 'Quarter', 'Quarters', 'Year'], 'max_budget_allowed': None, 'symbol group': [], 'Day': 0.03, 'Week': 0.5, 'Month': 0.6, 'Quarter': 0.8, 'Quarters': 0.8, 'Year': 0.8, 'Day Margin': 0.03, 'Week Margin': 0.4, 'Month Margin': 0.4, 'Quarter Margin': 0.5, 'Quarters Margin': 0.8, 'Year Margin': 0.8, 'sell_date': 'Invalid date'}

    if pg_migration:
        PollenDatabase.upsert_data(table_name, QUEEN_KING.get('key'), QUEEN_KING)
    else:
       PickleData(QUEEN_KING.get('source'), QUEEN_KING)
    
    return grid_row_button_resp(description=f" {symbol} Trading Model Updated")


def queen_queenking_trigger_update(client_user, prod, trigger_id, status='trig_running'):
    """Update a single trigger rule by trigger_id."""
    
    QUEEN_KING = init_queenbee(client_user, prod, queen_king=True, pg_migration=pg_migration).get('QUEEN_KING')
    
    # Get existing trigger rules
    existing_trigrules = QUEEN_KING['king_controls_queen'].get('ticker_trigrules', [])
    if not isinstance(existing_trigrules, list):
        existing_trigrules = []
    
    # Create lookup dict by trigger_id
    existing_by_id = {
        rule.get('trigger_id'): rule 
        for rule in existing_trigrules 
        if rule.get('trigger_id')
    }

    # Find and update the trigger
    if trigger_id in existing_by_id:
        # Hardcoded updates
        # existing_by_id[trigger_id]['save_to_db'] = False
        existing_by_id[trigger_id]['trigrule_status'] = status
        
        print(f"✏️  QUEEN Updated trigger: {trigger_id}")
        
        # Convert back to list and save
        QUEEN_KING['king_controls_queen']['ticker_trigrules'] = list(existing_by_id.values())
        
        # Save to database
        if pg_migration:
            table_name = 'client_user_store' if prod else 'client_user_store_sandbox'
            PollenDatabase.upsert_data(table_name, QUEEN_KING.get('key'), QUEEN_KING)
        else:
            PickleData(QUEEN_KING.get('source'), QUEEN_KING)
        
        return grid_row_button_resp(
            description=f"'{trigger_id}' updated"
        )
    else:
        print(f"❌ Trigger not found: {trigger_id}")
        return grid_row_button_resp(
            description=f"Trigger '{trigger_id}' not found",
            error=True
        )
    pass


### GRAPH
def get_ticker_data(symbols, toggles_selection):
  time_frame = star_names(toggles_selection)
  if pg_migration:
     pollenstory = PollenDatabase.retrieve_all_pollenstory_data(symbols, time_frame).get('pollenstory')
  else:
    pollenstory = read_QUEENs__pollenstory(symbols=symbols,read_storybee=False, read_pollenstory=True,).get('pollenstory')

  df_main = False
  for symbol in symbols:
    df = pollenstory[f'{symbol}_{time_frame}']
    df = df[['timestamp_est', 'close', 'vwap']]
    if time_frame == '1Minute_1Day':
      df = add_priorday_tic_value(df)
 
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
    time_frame = star_names(toggles_selection)
    if pg_migration:
      pollenstory = PollenDatabase.retrieve_all_pollenstory_data(symbols, time_frame).get('pollenstory')
    else:
      pollenstory = read_QUEENs__pollenstory(symbols=symbols,read_storybee=False, read_pollenstory=True,).get('pollenstory')
    for symbol in symbols:
      if f'{symbol}_{time_frame}' not in pollenstory.keys():
        #  print("Need Pollenstory Charts: ", symbol)
         continue
         
      df = pollenstory[f'{symbol}_{time_frame}']
      if time_frame == '1Minute_1Day':
        df = add_priorday_tic_value(df)
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
