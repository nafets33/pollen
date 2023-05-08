#find and read the pkl file in the folder.
import os
import pandas as pd
import random
from chess_piece.king import hive_master_root, ReadPickleData, PickleData, read_QUEENs__pollenstory
from chess_piece.queen_hive import split_today_vs_prior, story_view
from datetime import datetime
from dotenv import load_dotenv
import pytz
import ipdb
est = pytz.timezone("US/Eastern")

main_root = hive_master_root() # os.getcwd()  # hive root
load_dotenv(os.path.join(main_root, ".env"))

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
  print(queen_pkl_path)
  queen_pkl = ReadPickleData(queen_pkl_path)
  return queen_pkl

def load_queen_pkl(username, prod):
  if prod == False:
    queen_pkl_path = username+'/queen_sandbox.pkl'
  else:
    queen_pkl_path = username+'/queen.pkl'
  print(queen_pkl_path)
  queen_pkl = ReadPickleData(queen_pkl_path)
  return queen_pkl

def load_POLLENSTORY_STORY_pkl(symbols, read_storybee, read_pollenstory, username, prod):
    ticker_db = read_QUEENs__pollenstory(
        symbols=symbols,
        read_storybee=read_storybee, 
        read_pollenstory=read_pollenstory,
    )    
    return ticker_db


# Router Calls

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

def get_queen_orders_json(username, prod, kwargs):
  if kwargs.get('api_key') != os.environ.get("fastAPI_key"): # fastapi_pollenq_key
     print("Auth Failed", kwargs.get('api_key'))
     return "NOTAUTH"
  
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
  
  df['client_order_id'] = df.index
  df["$honey"] = pd.to_numeric(df["$honey"], errors='coerce')
  df["honey"] = pd.to_numeric(df["honey"], errors='coerce')
  df["honey"] = round(df["honey"] * 100,2)
  df["$honey"] = round(df["$honey"],0)
  
  df = df[df['queen_order_state'].isin(['running'])]
  df = df[col_view]
  json_data = df.to_json(orient='records')
  return json_data

def get_ticker_data(symbols, prod, kwargs):

  if kwargs.get('api_key') != os.environ.get("fastAPI_key"):
     print("Auth Failed", kwargs.get('api_key'))
     return "NOTAUTH"

  ticker_db = read_QUEENs__pollenstory(
      symbols=symbols,
      read_storybee=False, 
      read_pollenstory=True,
  )
  
  df = ticker_db.get('pollenstory')[f'{symbols[0]}_{"1Minute_1Day"}']
  df_ = df[['timestamp_est', 'close', 'vwap']]
  df_main = split_today_vs_prior(df_).get('df_today')

  json_data = df_main.to_json(orient='records')

  return json_data

def get_account_info(username, prod, kwargs):
   # read account data
   return True


def queen_wavestories__get_macdwave(username, prod, symbols, read_storybee, read_pollenstory, tickers_avail):
    # cust_Button("misc/waves.png", hoverText='', key='waves_icon', height=f'23px')
    # st.image((os.path.join(hive_master_root(), "/custom_button/frontend/build/misc/waves.png")), width=33)
    QUEEN_KING = load_queen_App_pkl(username, prod)
    QUEEN = load_queen_pkl(username, prod)
    ticker_db = load_POLLENSTORY_STORY_pkl(symbols, read_storybee, read_pollenstory, username, prod)
    POLLENSTORY = ticker_db['pollenstory']
    STORY_bee = ticker_db['STORY_bee']
    
    try:
        # req = ticker_time_frame__option(tickers_avail=tickers_avail, req_key='wavestories')
        # tickers = req.get('tickers')

        # if len(tickers) > 8:
        #     st.warning("Total MACD GUAGE Number reflects all tickers BUT you may only view 8 tickers")
        # cols = st.columns((1, 3))
        df_main = None
        for symbol in symbols:
            # star__view = its_morphin_time_view(QUEEN=QUEEN, STORY_bee=STORY_bee, ticker=symbol, POLLENSTORY=POLLENSTORY) ## RETURN FASTER maybe cache?
            story_views = story_view(STORY_bee=STORY_bee, ticker=symbol)
            # SV = st.selectbox("Story Views", options=list(story_views.get('df_agg').keys()), key=f'{"sview"}{symbol}')
            # st.write(story_views.get('df_agg').get(SV))
            # st.write(story_views.get('df_agg').get(SV).iloc[0])
            # df_hm = story_views.get('df_agg').get(SV)
            df = story_views.get('df')
            df = df.set_index('star')
            df.at[f'{symbol}_{"1Minute_1Day"}', 'sort'] = 1
            df.at[f'{symbol}_{"5Minute_5Day"}', 'sort'] = 2
            df.at[f'{symbol}_{"30Minute_1Month"}', 'sort'] = 3
            df.at[f'{symbol}_{"1Hour_3Month"}', 'sort'] = 4
            df.at[f'{symbol}_{"2Hour_6Month"}', 'sort'] = 5
            df.at[f'{symbol}_{"1Day_1Year"}', 'sort'] = 6
            df = df.sort_values('sort')
            trading_model = QUEEN_KING['king_controls_queen']['symbols_stars_TradingModel'].get(symbol)
            # story_guages = wave_guage(df, trading_model=trading_model)
            # df_style = df.style.background_gradient(cmap="RdYlGn", gmap=df['current_macd_tier'], axis=0, vmin=-8, vmax=8)
            # with cols[0]:
            #     st.plotly_chart(create_guage_chart(title=f'{symbol} Wave Gauge', value=float(story_guages.get(f'{"weight_L"}_macd_tier_guage'))))
            # with cols[1]:
            #     for weight_ in ['weight_L', 'weight_S']:
            #         macd_ = story_guages.get(f'{weight_}_macd_tier_guage')
            #         hist_ = story_guages.get(f'{weight_}_hist_tier_guage')
                    # mark_down_text(fontsize=25, text=f'{symbol} {f"{weight_} MACD Gauge "}{"{:,.2%}".format(macd_)}{" Hist Gauge "}{"{:,.2%}".format(hist_)}')

                # st.dataframe(df_style)
            if df_main is None:
               df_main = df
            df_main = pd.concat([df_main, df])
            json_data = df_main.to_json(orient='records')

            return json_data
    except Exception as e:
       print(e)