
import streamlit as st
import pandas as pd
import numpy as np
from chess_piece.king import ReadPickleData, print_line_of_error, streamlit_config_colors
from chess_piece.queen_hive import init_swarm_dbs, star_names, bishop_ticker_info, sell_button_dict_items, update_sell_date

import pytz
from datetime import datetime, timedelta
pd.options.mode.chained_assignment = None  # default='warn' Set copy warning

est = pytz.timezone("US/Eastern")


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

def buy_button_dict_items(queen_handles_trade=True, 
                          star='1Minute_1Day',
                          star_list=list(star_names().keys()),
                          wave_amo=1000,
                          trade_using_limits=None,
                          limit_price=False,
                          take_profit=.03,
                          sell_out=-.03,
                          sell_trigbee_trigger=True,
                          sell_trigbee_trigger_timeduration=5,
                          close_order_today=False, 
                          reverse_buy=False, 
                          sell_at_vwap=False,
                          sell_trigbee_date=datetime.now(est).strftime('%m/%d/%YT%H:%M'), 
                          ):
    column = {
                'queen_handles_trade': queen_handles_trade,
                'star':star,
                'wave_amo': wave_amo,
                # 'trade_using_limits': trade_using_limits,
                'limit_price': limit_price,
                'take_profit': take_profit,
                'sell_out': sell_out,
                'sell_trigbee_trigger': sell_trigbee_trigger,
                'sell_trigbee_trigger_timeduration': sell_trigbee_trigger_timeduration,
                'close_order_today': close_order_today,
                'reverse_buy': reverse_buy,
                'sell_at_vwap': sell_at_vwap,
                'star_list': star_list,
                'sell_trigbee_date': sell_trigbee_date,
                }
    return {key: value for key, value in column.items() if value is not None}

def return_waveview_fillers(QUEEN_KING, waveview):
    df = waveview

    df['sell_alloc_deploy'] =  np.where((df['macd_state'].str.contains("buy")) & (df['allocation_deploy'] < 0), round(df['allocation_deploy']), 0)
    df['sellbuy_alloc_deploy'] =  np.where((df['macd_state'].str.contains("sell")) & (df['allocation_deploy'] > 0), round(df['allocation_deploy']), 0)
    df['sell_alloc_deploy'] = df['sell_alloc_deploy'] + df['sellbuy_alloc_deploy']
    df['buysell_alloc_deploy'] =  np.where((df['macd_state'].str.contains("sell")) & (df['allocation_deploy'] < 0), round(abs(waveview['allocation_deploy'])), 0) 

    # sell_options = sell_button_dict_items()
    # df['sell_option'] = [sell_options for _ in range(df.shape[0])]
    kors_dict = buy_button_dict_items()
    df['kors'] = [kors_dict for _ in range(df.shape[0])]
    df['kors_key'] = df["ticker_time_frame"] +  "__" + df['macd_state']
    df['trading_model_kors'] = df['kors_key'].apply(lambda x: return_trading_model_kors(QUEEN_KING, star__wave=x))
    for ttf in df.index.tolist():
        remaining_budget = df.at[ttf, 'remaining_budget'].astype(float)
        remaining_budget_borrow = df.at[ttf, 'remaining_budget_borrow'].astype(float)
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
        
        margin = ''
        if remaining_budget <0 and (remaining_budget_borrow + remaining_budget) > 0:
            margin = "Margin"
            remaining_budget = round((remaining_budget_borrow + remaining_budget))
        
        if remaining_budget <0:
            remaining_budget = 0
        
        ticker, time, frame = ttf.split("_")
        chart_time = f'{time}_{frame}'
        sell_trigbee_date = update_sell_date(chart_time)
        kors = buy_button_dict_items(star=ttf, 
                                    wave_amo=remaining_budget, 
                                    take_profit=take_profit, 
                                    sell_out=sell_out, 
                                    sell_trigbee_date=sell_trigbee_date,
                                    close_order_today=close_order_today, 
                                    sell_trigbee_trigger_timeduration=None,
                                    star_list=None,
                                    reverse_buy=None, 
        )

        df.at[ttf, 'kors'] = kors
        df.at[ttf, 'ticker_time_frame__budget'] = f"""{margin} {"${:,}".format(remaining_budget)}"""
        # except Exception as e:
        #     print_line_of_error(f"{ttf} grid buttons {remaining_budget}")
    
    return df


def story_return(QUEEN_KING, revrec, prod=True, toggle_view_selection='Queen'):
    waveview = revrec.get('waveview')
    df = revrec.get('storygauge')

    df_waveview = return_waveview_fillers(QUEEN_KING, waveview)
    
    qcp_name = {data.get('piece_name'): qcp for qcp, data in QUEEN_KING['chess_board'].items() }
    qcp_name['Queen'] = 'Queen'
    qcp_name['King'] = 'King'
    if toggle_view_selection in qcp_name.keys():
        toggle_view_selection = qcp_name[toggle_view_selection]

    qcp_ticker = dict(zip(revrec.get('df_ticker')['qcp_ticker'],revrec.get('df_ticker')['qcp']))
    ticker_filter = [ticker for (ticker, qcp) in qcp_ticker.items() if qcp == toggle_view_selection]                
    if ticker_filter:
        df = df[df.index.isin(ticker_filter)]
    storygauge_columns = df.columns.tolist()
    waveview['buy_alloc_deploy'] = waveview['allocation_long_deploy']
    # symbol group by to join on story
    num_cols = ['allocation_long_deploy', 'buy_alloc_deploy', 'star_buys_at_play', 'sell_alloc_deploy', 'star_sells_at_play', 'star_total_budget', 'remaining_budget', 'remaining_budget_borrow']
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

    df_ticker = revrec.get('df_ticker')
    try:
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

                # if symbol in df_ticker.index:
                budget = df_ticker.at[symbol, 'ticker_total_budget']
                df.at[symbol, 'total_budget'] = round(budget)
                    # if isinstance(budget, float):
                    # else:
                    #     df.at[symbol, 'total_budget'] = 0

                df['trading_model_kors'] = df['symbol'].apply(lambda x: return_trading_model_kors_v2(QUEEN_KING, symbol=x))
                take_profit = df.at[symbol, "trading_model_kors"].get('take_profit')
                sell_out = df.at[symbol, "trading_model_kors"].get('sell_out')
                close_order_today = df.at[symbol, "trading_model_kors"].get('close_order_today')
                sell_trigbee_trigger_timeduration = df.at[symbol, "trading_model_kors"].get('sell_trigbee_trigger_timeduration')
                reverse_buy = False
                kors = buy_button_dict_items(star="1Day_1Year", star_list=list(star_names().keys()), wave_amo=buy_alloc_deploy[symbol], take_profit=take_profit, sell_out=sell_out, sell_trigbee_trigger_timeduration=sell_trigbee_trigger_timeduration, close_order_today=close_order_today, reverse_buy=reverse_buy)
                df.at[symbol, 'kors'] = kors
        
            # star kors
            for star in star_names().keys():
                ttf = f'{symbol}_{star_names(star)}'
                # kors per star
                star_kors = df_waveview.at[ttf, 'kors']
                star_kors['wave_amo'] = df_waveview.at[ttf, "allocation_long_deploy"]
                df.at[symbol, f'{star}_kors'] = star_kors
                # message
                wavestate = f'{df_waveview.at[ttf, "bs_position"]} {df_waveview.at[ttf, "length"]}'
                alloc_deploy_msg = '${:,.0f}'.format(round(df_waveview.at[ttf, "allocation_long_deploy"]))
                df.at[symbol, f'{star}_state'] = f"{wavestate} {alloc_deploy_msg}"
                df.at[symbol, f'{star}_value'] = df_waveview.at[ttf, "allocation_long_deploy"]
    except Exception as e:
        print("mmm error", ttf, print_line_of_error(e))

    story_grid_num_cols = ['star_buys_at_play',
    'star_sells_at_play',
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
    'broker_qty_delta',
    'Month_value',
    # "Month_kors"
    ]
    df['current_from_yesterday'] = round(df['current_from_yesterday'] * 100,2)
    df['color_row'] = df['trinity_w_L'].apply(lambda x: generate_shade(x/100, shade_num_var=89))

    # # Totals Index
    df_total = pd.DataFrame([{'symbol': 'Total'}]).set_index('symbol')
    colss = df.columns.tolist()
    for totalcols in story_grid_num_cols:
        if totalcols in colss:
            if 'trinity' in totalcols:
                df_total.loc['Total', totalcols] = f'{round(df[totalcols].sum() / len(df))} %'
            elif totalcols == 'queens_suggested_buy':
                df_total.loc['Total', totalcols] = '${:,.0f}'.format(round(df["buy_alloc_deploy"].sum()))
            elif totalcols == 'queens_suggested_sell':
                df_total.loc['Total', totalcols] = '${:,.0f}'.format(round(df["money"].sum()))
            elif totalcols == 'total_budget':
                df_total.loc['Total', totalcols] = df["total_budget"].sum()
            elif totalcols == 'Month':
                print("month")
                df_total.loc['Total', 'Month_value'] = df["Month_value"].sum()
                # df.loc['Total', 'Month_kors'] = df["Month_value"].sum()
            else:
                df_total.loc['Total', totalcols] = df[totalcols].sum()
    
    df = pd.concat([df_total, df])
    df.at['Total', 'symbol'] = 'Total'

    for star in star_names().keys():
        try:
            df[f'{star}_value'] = df[f'{star}_value'].fillna(0)
            df.at['Total', f'{star}_state'] = '${:,.0f}'.format(round(sum(df[f'{star}_value'])))
        except Exception as e:
            print_line_of_error(e)
    
          # Colors
    k_colors = streamlit_config_colors()
    default_text_color = k_colors['default_text_color'] # = '#59490A'
    default_font = k_colors['default_font'] # = "sans serif"
    default_yellow_color = k_colors['default_yellow_color'] # = '#C5B743'
    # handle colors
    df['color_row'] = np.where(df['symbol']=='Total', default_yellow_color, df['color_row'])
    df['color_row_text'] = default_text_color

    # Bishop yahoo data
    # WORKERBEE, only read bishop once a day then cache it
    db=init_swarm_dbs(prod)
    BISHOP = ReadPickleData(db.get('BISHOP'))
    ticker_info = BISHOP.get('ticker_info').set_index('ticker')
    ticker_info_cols = bishop_ticker_info().get('ticker_info_cols')
    df = df.set_index('symbol', drop=False)
    ticker_info = ticker_info[[i for i in ticker_info_cols if i not in df.columns]]
    df = df.merge(ticker_info, left_index=True, right_index=True, how='left')

    return df
