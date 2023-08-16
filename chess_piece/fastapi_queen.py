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
                                    story_view, 
                                    refresh_chess_board__revrec, 
                                    buy_button_dict_items,
                                    order_vars__queen_order_items,
                                    find_symbol,
                                    power_amo,
                                    init_queenbee,
                                    return_trading_model_trigbee,
                                    init_charlie_bee)
from chess_piece.queen_bee import execute_order, sell_order__var_items


pd.options.mode.chained_assignment = None  # default='warn' Set copy warning

est = pytz.timezone("US/Eastern")

main_root = hive_master_root() # os.getcwd()  # hive root
load_dotenv(os.path.join(main_root, ".env"))
db_root = os.path.join(main_root, "db")
init_logging(queens_chess_piece="fastapi_queen", db_root=db_root, prod=True)

 ###### Helpers UTILS

def generate_shade(number_variable, base_color=False, wave=False):
    try:
      # Validate the input range
      red = '#FBC0C0'
      green = '#C0FBD3'
      if wave:
        m_wave, m_num = number_variable.split("_")
        base_color = green if 'buy' in m_wave else red
        number_variable = int(m_num.split("-")[-1])
        # number_variable = 33
      else:
        # print(number_variable)

        base_color = green if (number_variable) > 0 else red
        number_variable = round(abs(number_variable * 100))
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
      shade_amount = abs(number_variable) / 100  # Map to range [0, 1]

      # Calculate shaded RGB values
      shaded_rgb = tuple(int(base_color_comp * (1 - shade_amount)) for base_color_comp in base_color_rgb)

      # Convert RGB to hex color code
      shaded_color = "#{:02X}{:02X}{:02X}".format(*shaded_rgb)

      return shaded_color
    except Exception as e:
      print_line_of_error(e)


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
def symbols_wave_guage(username, prod):
   return True


def app_buy_order_request(client_user, username, prod, selected_row, default_value, ready_buy=False, x_buy=False): # index & wave_amount
  try:
    # QUEEN = load_queen_pkl(username, prod)
    # QUEEN_KING = load_queen_App_pkl(username, prod)
    button_buy = default_value
    QUEEN, QUEEN_KING, ORDERS, api = init_queenbee(client_user=client_user, prod=prod, queen=True, queen_king=True, api=True)
    buy_package = create_AppRequest_package(request_name='buy_orders')
    buy_package.update({'buy_order': {}})

    revrec = QUEEN.get('revrec')
    blessing={} #{i: '': for i in []}, # order_vars
    ticker = selected_row.get('symbol') # update symbol on X
    ticker_time_frame = selected_row.get('ticker_time_frame')
    star_time = selected_row.get('star_time')
    trigbee = selected_row.get('macd_state')
    wave_blocktime = selected_row.get('wave_blocktime')
    
    trading_model = QUEEN_KING['king_controls_queen']['symbols_stars_TradingModel'].get(ticker)
    symbol, etf_long_tier, etf_inverse_tier = find_symbol(QUEEN, ticker, trading_model, trigbee)

    tm_trig = return_trading_model_trigbee(tm_trig=trigbee, trig_wave_length=trigbee.split("-")[-1])
    if ready_buy:
      tm_trig = f'sell_cross-0' if 'buy' in tm_trig else f'buy_cross-0'
    
    king_order_rules = trading_model['stars_kings_order_rules'][star_time]['trigbees'][tm_trig][wave_blocktime]
    # king_order_rules = revrec['waveview'].at[ticker_time_frame, 'king_order_rules']
    
    crypto=False
    king_resp=True, 
    king_eval_order=False, 
    
    trading_model_theme = trading_model.get('theme')
    maker_middle = False
    current_wave = revrec['waveview'].get('current_wave')
    current_macd_cross__wave = QUEEN['heartbeat'].get('current_wave')
    power_up_amo = power_amo()
    order_side = 'buy'

    borrowed_funds = False
    borrow_qty = False
    print(button_buy.keys())
    if type(button_buy) is dict:
       for rule, value in button_buy.items():
          if rule in ['wave_amo', 'close_order_today']: # validated items to add orules
            if rule == 'wave_amo':
              #  print(type(value), value)
               if type(value) != float:
                  value = float(value)
               wave_amo = value
            if rule == 'close_order_today':
               if type(value) != bool:
                  print("ERRROR BOOL CLOSE ORDER")
                  continue
            print("updateing", rule, value)
            king_order_rules.update({rule: value})
       
      # #  trig=button_buy.get('trigbee'),
      #  order_side=button_buy.get('order_side'),
      #  order_type = button_buy.get('order_type'),
      #  limit_price=button_buy.get('limit_price'),

    order_vars = order_vars__queen_order_items(trading_model=trading_model_theme, 
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
     print_line_of_error()
     logging.error(("fastapi", e))


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


def app_queen_order_update_order_rules(username, prod, selected_row, default_value):
    # number_shares = default_value
    print(default_value)
    queen_order = selected_row
    client_order_id = queen_order.get('client_order_id')
    QUEEN_KING = load_queen_App_pkl(username, prod)
    order_update_package = create_AppRequest_package(request_name='update_order_rules', client_order_id=client_order_id)
    order_update_package['update_order_rules'] = {client_order_id: {'queen_order_state': 'archived'}}
    # QUEEN_KING['update_order_rules'].append(order_update_package)
    # PickleData(QUEEN_KING.get('source'), QUEEN_KING)
    return True

## MAIN GRIDS
def get_queen_orders_json(client_user, username, prod, toggle_view_selection):
  
  try:
      # ORDERS = load_queen_order_pkl(username, prod)

      # QUEEN_KING = load_queen_App_pkl(username, prod)
      QUEEN, QUEEN_KING, ORDERS, api = init_queenbee(client_user=client_user, prod=prod, orders=True)


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
      # KORS
      # stars = stars.keys()
      # t_kors ={}
      # for symbol in set(df['ttf_symbol'].tolist()):
      #   trading_model = QUEEN_KING['king_controls_queen']['symbols_stars_TradingModel'].get(symbol)
      #   # t_kors[symbol] = {}
      #   for star in stars:
      #     ttf_key = f'{symbol}_{star}'
      #     t_kors[symbol][star] = {}
      #     for trigbee in trigger_bees().keys():
      #        king_order_rules = trading_model['stars_kings_order_rules'][star]['trigbees'][trigbee].get('morning_9-11')
      #        t_kors[symbol][star][trigbee] = king_order_rules
      
      # king_order_rules = trading_model['stars_kings_order_rules'][star_time]['trigbees'][tm_trig][current_wave_blocktime]
      


      # df.reset_index(drop=True, inplace=True)
      df = df[df['client_order_id']!='init']
      df = df.fillna('000')
      df = df[df['ticker_time_frame']!='000'] ## who are you?? WORKERBEE
      # print(df_)
      df['ttf_symbol'] = df['ticker_time_frame'].apply(lambda x: return_symbol_from_ttf(x))
      # df["order_rules"] = df["order_rules"].astype(str)
      # df["take_profit"] = df["order_rules"].apply(lambda x: x.get("take_profit"))
      # df['client_order_id'] = df.index
      df["money"] = pd.to_numeric(df["money"], errors='coerce')
      df["honey"] = pd.to_numeric(df["honey"], errors='coerce')
      df["honey"] = round(df["honey"] * 100,2)
      df["money"] = round(df["money"],0)
      df['color_row'] = np.where(df['honey'] > 0, default_yellow_color, "#ACE5FB")
      df['color_row_text'] = np.where(df['honey'] > 0, default_text_color, default_text_color)
      
      # df.at[len(df)-1, 'color_row'] = '#24A92A'
      print('tview', toggle_view_selection)
      qos_view = ['running', 'running_close', 'running_open']
      # if toggle_view_selection == 'today':
      #    df = split_today_vs_prior(df=df, timestamp='datetime').get('df_today')
      # elif toggle_view_selection == 'sells':
      #    df = df[df['queen_order_state'].isin(['completed'])]
      # else:
      #   df = df[df['queen_order_state'].isin(qos_view)]

      # sort
      df = df[df['queen_order_state'].isin(qos_view)]
      sort_colname = 'cost_basis_current'
      df = df.sort_values(sort_colname, ascending=False)
      
      # # Totals Index
      # df.loc['Total', 'money'] = df['money'].sum()
      # df.loc['Total', 'honey'] = df['honey'].sum()
      # df.loc['Total', 'datetime'] = ''
      # df.loc['Total', 'cost_basis'] = df['cost_basis'].sum()
      # df.loc['Total', 'cost_basis_current'] = df['cost_basis_current'].sum()
      # newIndex=['Total']+[ind for ind in df.index if ind!='Total']
      # df=df.reindex(index=newIndex)

      json_data = df.to_json(orient='records')
      return json_data
  except Exception as e:
    print('hey now')
    print_line_of_error()


def queen_wavestories__get_macdwave(username, prod, symbols, return_type='waves'):
    try:
        if prod:
          revrec = ReadPickleData(username + '/queen_revrec.pkl').get('revrec')
        else:
           revrec = ReadPickleData(username + '/queen_revrec_sandbox.pkl').get('revrec')

        # QUEEN_KING = load_queen_App_pkl(username, prod)
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


        if return_type == 'waves':
           df = revrec.get('waveview')
           kors_dict = buy_button_dict_items()
           df['kors'] = [kors_dict for _ in range(df.shape[0])]
          #  for ttf in df_main.index.tolist():
          #     df_main.at[ttf, 'king_order_rules'] = df_main.at[ttf, 'king_order_rules'].update({'wave_amo':
          #                                                                                       df_main.at[ttf, 'allocation_deploy']})
           df["maxprofit"] = pd.to_numeric(df["maxprofit"], errors='coerce')
           df["maxprofit"] = round(df["maxprofit"] * 100,2).fillna(0)
           df['color_row'] = df['macd_state'].apply(lambda x: generate_shade(x, wave=True))
           df['color_row_text'] = default_text_color
          #  df.at['SPY_1Minute_1Day', 'color_row'] = '#a1b357'
           json_data = df.to_json(orient='records')
           return json_data
        elif return_type == 'story':
            # def update_dictionary_column(df, dict_column_name, update_column_name, key_column_name):
            #     def update_dictionary(dictionary, value, key):
            #         dictionary[key] = value
            #         return dictionary
                
            #     df[dict_column_name] = df.apply(lambda row: update_dictionary(row[dict_column_name], row[update_column_name], row[key_column_name]), axis=1)

            # # Example DataFrame
            # data = {
            #     'id': [1, 2, 3],
            #     'data_dict': [{'a': 10, 'b': 20}, {'c': 30, 'd': 40}, {'e': 50, 'f': 60}],
            #     'update_value': [100, 200, 300],
            #     'update_key': ['a', 'd', 'f']
            # }

            # df = pd.DataFrame(data)

            # # Call the function to update the dictionary column
            # update_dictionary_column(df, 'data_dict', 'update_value', 'update_key')

            # print(df)
           df = revrec.get('storygauge')       
           df = df[[i for i in df.columns.tolist() if i == 'symbol' or 'trinity' in i]]
           kors_dict = buy_button_dict_items()
           df['kors'] = [kors_dict for _ in range(df.shape[0])]
          #  df['kors'] = df['kors'].apply(lambda x: update_kors(x))
          #  df['trinity_w_L'] = pd.to_numeric(df["trinity_w_L"], errors='coerce')
           df['color_row'] = df['trinity_w_L'].apply(lambda x: generate_shade(x))
           df['color_row_text'] = default_text_color
           for col in df.columns:
              # print(type(df_storygauge.iloc[-1].get(col)))
              if type(df.iloc[-1].get(col)) == np.float64:
                  # print(col)
                  df[col] = round(df[col] * 100,2)
           json_data = df.to_json(orient='records')
           return json_data

    
    except Exception as e:
       print("mmm error", print_line_of_error(e))



## RETURN TEXT STRING
def get_account_info(client_user, username, prod):
  # QUEEN = load_queen_pkl(username, prod)
  # print(username, client_user, prod)
  # if prod:
  #   acct = ReadPickleData(username +'/queen_account_info.pkl')
  # else:
  #    acct = ReadPickleData(username +'/queen_account_info_sandbox.pkl')

  QUEEN, QUEEN_KING, ORDERS, api = init_queenbee(client_user=client_user, prod=prod, queen=True)
  QUEENsHeart = ReadPickleData(QUEEN['dbs'].get('PB_QUEENsHeart_PICKLE'))
  beat = round((datetime.now(est) - QUEENsHeart.get('heartbeat_time')).total_seconds(), 1)
  charlie_bee = QUEENsHeart.get('charlie_bee')
  avg_beat = round(charlie_bee['queen_cyle_times']['QUEEN_avg_cycletime'])
  
  acct_info = QUEEN['account_info']
  if len(acct_info) > 0:
    honey_text = "Today" + '%{:,.4f}'.format(((acct_info['portfolio_value'] - acct_info['last_equity']) / acct_info['portfolio_value']) *100)
    money_text = '${:,.2f}'.format(acct_info['portfolio_value'] - acct_info['last_equity'])
    buying_power = '${:,.2f}'.format(round(acct_info.get('buying_power')))
    cash = '${:,.2f}'.format(round(acct_info.get('cash')))
    daytrade_count = round(acct_info.get('daytrade_count'))
    portfolio_value = '${:,.2f}'.format(round(acct_info.get('portfolio_value')))
    long = QUEEN['heartbeat'].get('long')
    short = QUEEN['heartbeat'].get('short')
    long = '${:,}'.format(long)
    short = '${:,}'.format(short)
    # df = QUEEN['queen_orders']
    # buys = df[df['trigname'].str.contains('buy')]
    # sells = df[df['trigname'].str.contains('sell')]
    # long = sum(buys['cost_basis_current'])
    # short = sum(sells['cost_basis_current'])
    mmoney = f'{honey_text} {money_text}'
    mmoney = "\u0332".join(mmoney)
    msg = f'{mmoney} Heart {beat} Avg {avg_beat} $ BP: {buying_power} Cash: {cash} Portfolio Value: {portfolio_value}  daytrade: {daytrade_count} L: {long} S: {short}'
    return msg
  else:
     return 'NO QUEEN'


## GRAPH
def get_ticker_data(symbols, prod):

  ticker_db = read_QUEENs__pollenstory(
      symbols=symbols,
      read_storybee=False, 
      read_pollenstory=True,
  )
  
  df = ticker_db.get('pollenstory')[f'{symbols[0]}_{"1Minute_1Day"}']
  df_main = df[['timestamp_est', 'close', 'vwap']]
  df_main = split_today_vs_prior(df_main).get('df_today')

  json_data = df_main.to_json(orient='records')

  return json_data

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