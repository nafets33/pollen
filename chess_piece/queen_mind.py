import os
from collections import defaultdict, deque
from datetime import datetime, timedelta
import ipdb
import numpy as np
import pandas as pd
import pytz
from dotenv import load_dotenv
import logging
import copy
from chess_piece.king import print_line_of_error, stars, kingdom__global_vars
from chess_piece.pollen_db import PollenDatabase

prod = True
pg_migration = True
est = pytz.timezone("America/New_York")

pd.set_option('display.float_format', '{:.10f}'.format)
pd.set_option('display.max_columns', None)

# main_root = hive_master_root()  # os.getcwd()
# load_dotenv(os.path.join(main_root, ".env"))
# db_root = os.path.join(main_root, "db")
crypto_currency_symbols = ["BTCUSD", "ETHUSD", "BTC/USD", "ETH/USD"]
macd_tiers = 8


def search_for_gamble_trade(revrec):
    # WORKERBEE
    ## find me a good gamble 
    return True

# handle long_short in update WORKERBEE
def return_long_short(active_orders, cost_basis_ref='cost_basis_current'):
    reverse_indexes = ['SH', 'PSQ']
    mask = active_orders['symbol'].isin(reverse_indexes)
    long = active_orders.loc[~mask, cost_basis_ref].fillna(0).sum()
    short = active_orders.loc[mask, cost_basis_ref].fillna(0).sum()
    cost_basis_current = sum(active_orders[cost_basis_ref]) if len(active_orders) > 0 else 0

    return long, short, cost_basis_current

def init_qcp(init_macd_vars={"fast": 12, "slow": 26, "smooth": 9}, 
             ticker_list=['SPY'], 
             theme='nuetral', 
             model='MACD', 
             piece_name='king', 
             buying_power=1, 
             borrow_power=0, 
             picture='knight_png', 
             margin_power=0, 
             trade_only_margin=False, 
             refresh_star='1Minute_1Day',
             max_budget_allowed=None, # if int use in logic
             ):
    return {
        "picture": picture,
        "piece_name": piece_name,
        "model": model,
        "MACD_fast_slow_smooth": init_macd_vars,
        "tickers": ticker_list,
        "stars": stars(),
        "theme": theme,
        "total_buyng_power_allocation": buying_power,
        "total_borrow_power_allocation": borrow_power,
        "margin_power": margin_power,
        "trade_only_margin": trade_only_margin,
        'refresh_star': refresh_star, # anchor to use as reallocation # WORKERBEE..chess_board not Saving correclty or being overwritten?
        'max_budget_allowed': max_budget_allowed,
    }


def kings_order_rules( # rules created for 1Minute
    KOR_version=3,
    queen_handles_trade=True,
    order_side='buy', # 'sell'
    order_type='market',
    wave_amo=100,
    # Global, Buy, Sell
    theme='nuetral',
    status='active',
    trade_using_limits=False,
    limit_price=False,
    # BUYS
    doubledown_timeduration=60,
    ignore_trigbee_at_power=0.01,

    # SELLS
    take_profit=.01,
    take_profit_scale={.05: {'take_pct': .25, 'take_mark': False}}, # deprecate
    sell_out=-.0089,
    sell_out_scale={.05: {'take_pct': .25, 'take_mark': False}}, # deprecate
    max_profit_Deviation=.5, # deprecate # how far from max profit
    max_profit_waveDeviation=1, ## # deprecate Need to figure out expected waveDeivation from a top profit in wave to allow trade to exit (faster from seeking profit?)
    max_profit_waveDeviation_timeduration=5, # deprecate # Minutes # deprecate
    timeduration=120, # deprecate # Minutes ### DEPRECATE WORKERBEE
    sell_date=datetime.now().replace(hour=0, minute=00, second=0) + timedelta(days=366), 
    sell_trigbee_trigger=True,
    sell_trigbee_trigger_timeduration=60, # deprecate # Minutes
    sell_trigbee_date=datetime.now(est).strftime('%m/%d/%YT%H:%M'),
    sell_at_vwap = 1, # Sell pct at vwap
    use_wave_guage=False,
    doubledowns_allowed=2,
    close_order_today=False,
    close_order_today_allowed_timeduration=60, # seconds allowed to be past, sells at 60 seconds left in close
    borrow_qty=0,
    ignore_refresh_star=False,
    # Not Used
    short_position=False,
    revisit_trade_frequency=60,
    take_profit_in_vwap_deviation_range={"low_range": -0.05, "high_range": 0.05},
    stagger_profits=False,
    scalp_profits=False,
    scalp_profits_timeduration=30,
    stagger_profits_tiers=1,
    limitprice_decay_timeduration=1,
    skip_sell_trigbee_distance_frequency=0,
    skip_buy_trigbee_distance_frequency=0,
    use_margin=False,

):

    return {
        "KOR_version": KOR_version,
        "queen_handles_trade": queen_handles_trade,
        "theme": theme,
        "status": status,
        "trade_using_limits": trade_using_limits,
        "limitprice_decay_timeduration": limitprice_decay_timeduration,
        "doubledown_timeduration": doubledown_timeduration,
        "max_profit_Deviation": max_profit_Deviation,
        "max_profit_waveDeviation": max_profit_waveDeviation,
        "max_profit_waveDeviation_timeduration": max_profit_waveDeviation_timeduration, # Deprecate
        "timeduration": timeduration, # Deprecate
        "take_profit": take_profit,
        "sell_out": sell_out,
        "sell_trigbee_trigger": sell_trigbee_trigger,
        "sell_date": sell_date,
        "sell_at_vwap": sell_at_vwap,
        "stagger_profits": stagger_profits, # Deprecate
        "scalp_profits": scalp_profits, # Deprecate
        "scalp_profits_timeduration": scalp_profits_timeduration,# Deprecate
        "stagger_profits_tiers": stagger_profits_tiers,# Deprecate
        "skip_sell_trigbee_distance_frequency": skip_sell_trigbee_distance_frequency,
        "skip_buy_trigbee_distance_frequency": skip_buy_trigbee_distance_frequency,
        # skip sell signal if frequency of last sell signal was X distance >> timeperiod over value, 1m: if sell was 1 story index ago
        "ignore_trigbee_at_power": ignore_trigbee_at_power, # Deprecate ?
        "take_profit_in_vwap_deviation_range": take_profit_in_vwap_deviation_range, # Deprecate ?
        "short_position": short_position,
        'use_wave_guage': use_wave_guage,
        'doubledowns_allowed': doubledowns_allowed,
        'close_order_today': close_order_today,
        "use_margin": use_margin, # Deprecate
        "revisit_trade_frequency": revisit_trade_frequency, # Deprecate ???
        'close_order_today_allowed_timeduration': close_order_today_allowed_timeduration,
        'sell_trigbee_trigger_timeduration': sell_trigbee_trigger_timeduration,
        'borrow_qty': borrow_qty, # Deprecate
        'order_side': order_side,
        'wave_amo': wave_amo,
        'limit_price': limit_price,
        'sell_trigbee_date': sell_trigbee_date,
        'ignore_refresh_star': ignore_refresh_star,

    }


def generate_TradingModel(
    theme="nuetral", portfolio_name="Jq", ticker="SPY",
    stars=stars, trigbees=["buy_cross-0", "sell_cross-0"], 
    trading_model_name="MACD", status="active", portforlio_weight_ask=0.01, init=False,
    ):
    # theme level settings
    themes = [
        "nuetral", # Custom
        "custom", # Custom
        "long_star", # 1yr + 6Mon
        "short_star", # 1min(safe) + 5Min(safe) + 
        "day_shark",
        "safe",
        "star__storywave_AI", # 
    ]

    def theme_king_order_rules(theme, stars=stars):
        # " time duration in minutes" ### DOUBLE CHECK SOME NOT ALIGNED IN SECONDS ###
        # Returns Star KOR for all waveblocktimes
        
        # Default Model Settings return all levels of model
        symbol_theme_vars = {
            "power_rangers": {
                "1Minute_1Day": True,
                "5Minute_5Day" : True,
                "30Minute_1Month": True,
                "1Hour_3Month": True,
                "2Hour_6Month": True,
                "1Day_1Year": True,

            }
        }        
        star_theme_vars = {
                "1Minute_1Day": {
                    'stagger_profits':False, 
                    'buyingpower_allocation_LongTerm': 0,
                    'buyingpower_allocation_ShortTerm': 0,
                    'use_margin': False,
                    },
                "5Minute_5Day" : {
                    'stagger_profits':False, 
                    'buyingpower_allocation_LongTerm': 0,
                    'buyingpower_allocation_ShortTerm': 0,
                    'use_margin': False,
                    },
                "30Minute_1Month": {
                    'stagger_profits':False, 
                    'buyingpower_allocation_LongTerm': .4,
                    'buyingpower_allocation_ShortTerm': .4,
                    'use_margin': False,
                    },
                "1Hour_3Month": {
                    'stagger_profits':False, 
                    'buyingpower_allocation_LongTerm': .6,
                    'buyingpower_allocation_ShortTerm': .5,
                    'use_margin': False,
                    },
                "2Hour_6Month": {
                    'stagger_profits':False, 
                    'buyingpower_allocation_LongTerm': .8,
                    'buyingpower_allocation_ShortTerm': .8,
                    'use_margin': False,
                    },
                "1Day_1Year": {
                    'stagger_profits':False, 
                    'buyingpower_allocation_LongTerm': .8,
                    'buyingpower_allocation_ShortTerm': .8,
                    'use_margin': False,
                    },
        }
        wave_block_theme__kor = {}

        if theme.lower() == 'nuetral':
            symbol_theme_vars = symbol_theme_vars
            star_theme_vars = star_theme_vars
            wave_block_theme__kor = {
                "1Minute_1Day": kings_order_rules(
                                    theme=theme,
                                    status='active',
                                    doubledown_timeduration=60,
                                    trade_using_limits=False,
                                    max_profit_waveDeviation=3,
                                    max_profit_waveDeviation_timeduration=5,
                                    timeduration=360,
                                    take_profit=.01,
                                    sell_out=0,
                                    sell_trigbee_trigger=False,
                                    stagger_profits=False,
                                    scalp_profits=False,
                                    scalp_profits_timeduration=30,
                                    stagger_profits_tiers=1,
                                    limitprice_decay_timeduration=1,
                                    skip_sell_trigbee_distance_frequency=1,
                                    ignore_trigbee_at_power=0.01,
                                    # ignore_trigbee_in_vwap_range={"low_range": -0.05, "high_range": 0.05},
                                    take_profit_in_vwap_deviation_range={"low_range": -0.05, "high_range": 0.05},
                                    short_position=False,
                                    use_wave_guage=False,
                                    close_order_today=False,
                                    revisit_trade_frequency=60,
                ),
                "5Minute_5Day": kings_order_rules(
                                    theme=theme,
                                    status='active',
                                    doubledown_timeduration=60,
                                    trade_using_limits=False,
                                    max_profit_waveDeviation=3,
                                    max_profit_waveDeviation_timeduration=10,
                                    timeduration=320,
                                    take_profit=.05,
                                    sell_out=0,
                                    sell_trigbee_trigger=True,
                                    stagger_profits=False,
                                    scalp_profits=False,
                                    scalp_profits_timeduration=30,
                                    stagger_profits_tiers=3,
                                    limitprice_decay_timeduration=1,
                                    skip_sell_trigbee_distance_frequency=0,
                                    ignore_trigbee_at_power=0.01,
                                    # ignore_trigbee_in_vwap_range={"low_range": -0.05, "high_range": 0.05},
                                    take_profit_in_vwap_deviation_range={"low_range": -0.05, "high_range": 0.05},
                                    short_position=False,
                                    use_wave_guage=False,
                                    close_order_today=False,
                                    revisit_trade_frequency=5 * 3600,
                ),
                "30Minute_1Month": kings_order_rules(
                                    theme=theme,
                                    status='active',
                                    doubledown_timeduration=60,
                                    trade_using_limits=False,
                                    max_profit_waveDeviation=2,
                                    max_profit_waveDeviation_timeduration=30,
                                    timeduration=43800,
                                    take_profit=.08,
                                    sell_out=0,
                                    sell_trigbee_trigger=True,
                                    stagger_profits=False,
                                    scalp_profits=False,
                                    scalp_profits_timeduration=30,
                                    stagger_profits_tiers=1,
                                    limitprice_decay_timeduration=1,
                                    skip_sell_trigbee_distance_frequency=0,
                                    ignore_trigbee_at_power=0.01,
                                    # ignore_trigbee_in_vwap_range={"low_range": -0.05, "high_range": 0.05},
                                    take_profit_in_vwap_deviation_range={"low_range": -0.05, "high_range": 0.05},
                                    short_position=False,
                                    use_wave_guage=False,
                                    close_order_today=False,
                                    revisit_trade_frequency=10 * 3600,
                ),
                "1Hour_3Month": kings_order_rules(
                                    theme=theme,
                                    status='active',
                                    doubledown_timeduration=60,
                                    trade_using_limits=False,
                                    max_profit_waveDeviation=2,
                                    max_profit_waveDeviation_timeduration=60,
                                    timeduration=43800 * 3,
                                    take_profit=.1,
                                    sell_out=0,
                                    sell_trigbee_trigger=True,
                                    stagger_profits=False,
                                    scalp_profits=False,
                                    scalp_profits_timeduration=30,
                                    stagger_profits_tiers=1,
                                    limitprice_decay_timeduration=1,
                                    skip_sell_trigbee_distance_frequency=0,
                                    ignore_trigbee_at_power=0.01,
                                    # ignore_trigbee_in_vwap_range={"low_range": -0.05, "high_range": 0.05},
                                    take_profit_in_vwap_deviation_range={"low_range": -0.05, "high_range": 0.05},
                                    short_position=False,
                                    use_wave_guage=False,
                                    close_order_today=False,
                                    revisit_trade_frequency=10 * 3600,
                ),
                "2Hour_6Month": kings_order_rules(
                                    theme='nuetral',
                                    status='active',
                                    doubledown_timeduration=60,
                                    trade_using_limits=False,
                                    max_profit_waveDeviation=2,
                                    max_profit_waveDeviation_timeduration=120,
                                    timeduration=43800 * 6,
                                    take_profit=.2,
                                    sell_out=0,
                                    sell_trigbee_trigger=True,
                                    stagger_profits=False,
                                    scalp_profits=False,
                                    scalp_profits_timeduration=30,
                                    stagger_profits_tiers=1,
                                    limitprice_decay_timeduration=1,
                                    skip_sell_trigbee_distance_frequency=0,
                                    ignore_trigbee_at_power=0.01,
                                    # ignore_trigbee_in_vwap_range={"low_range": -0.05, "high_range": 0.05},
                                    take_profit_in_vwap_deviation_range={"low_range": -0.05, "high_range": 0.05},
                                    short_position=False,
                                    use_wave_guage=False,
                                    close_order_today=False,
                                    revisit_trade_frequency=10 * 3600,
                ),
                "1Day_1Year": kings_order_rules(
                                    theme=theme,
                                    status='active',
                                    doubledown_timeduration=60,
                                    trade_using_limits=False,
                                    max_profit_waveDeviation=3,
                                    max_profit_waveDeviation_timeduration=60 * 24, 
                                    timeduration=525600,
                                    take_profit=.5,
                                    sell_out=0,
                                    sell_trigbee_trigger=True,
                                    stagger_profits=False,
                                    scalp_profits=False,
                                    scalp_profits_timeduration=30,
                                    stagger_profits_tiers=1,
                                    limitprice_decay_timeduration=1,
                                    skip_sell_trigbee_distance_frequency=0,
                                    ignore_trigbee_at_power=0.01,
                                    # ignore_trigbee_in_vwap_range={"low_range": -0.05, "high_range": 0.05},
                                    take_profit_in_vwap_deviation_range={"low_range": -0.05, "high_range": 0.05},
                                    short_position=False,
                                    use_wave_guage=False,
                                    close_order_today=False,
                                    revisit_trade_frequency=60 * 3600,
                ),
            }
        elif theme.lower() == 'long_star':
            symbol_theme_vars = symbol_theme_vars
            star_theme_vars = {
                "1Minute_1Day": {
                    'stagger_profits':False, 
                    'buyingpower_allocation_LongTerm': 0,
                    'buyingpower_allocation_ShortTerm': 0,
                    'use_margin': False,
                    },
                "5Minute_5Day" : {
                    'stagger_profits':False, 
                    'buyingpower_allocation_LongTerm': .3,
                    'buyingpower_allocation_ShortTerm': 0,
                    'use_margin': False,
                    },
                "30Minute_1Month": {
                    'stagger_profits':False, 
                    'buyingpower_allocation_LongTerm': .4,
                    'buyingpower_allocation_ShortTerm': 0,
                    'use_margin': False,
                    },
                "1Hour_3Month": {
                    'stagger_profits':False, 
                    'buyingpower_allocation_LongTerm': .5,
                    'buyingpower_allocation_ShortTerm': 0,
                    'use_margin': False,
                    },
                "2Hour_6Month": {
                    'stagger_profits':False, 
                    'buyingpower_allocation_LongTerm': .8,
                    'buyingpower_allocation_ShortTerm': 0,
                    'use_margin': False,
                    },
                "1Day_1Year": {
                    'stagger_profits':False, 
                    'buyingpower_allocation_LongTerm': .89,
                    'buyingpower_allocation_ShortTerm': 0,
                    'use_margin': False,
                    },
        }
            wave_block_theme__kor = {
                "1Minute_1Day": kings_order_rules(
                                    theme=theme,
                                    status='active',
                                    doubledown_timeduration=60,
                                    trade_using_limits=False,
                                    max_profit_waveDeviation=1,
                                    max_profit_waveDeviation_timeduration=5,
                                    timeduration=120,
                                    take_profit=.005,
                                    sell_out=-.089,
                                    sell_trigbee_trigger=True,
                                    stagger_profits=False,
                                    scalp_profits=False,
                                    scalp_profits_timeduration=30,
                                    stagger_profits_tiers=1,
                                    limitprice_decay_timeduration=1,
                                    skip_sell_trigbee_distance_frequency=0,
                                    ignore_trigbee_at_power=0.01,
                                    # ignore_trigbee_in_vwap_range={"low_range": -0.05, "high_range": 0.05},
                                    take_profit_in_vwap_deviation_range={"low_range": -0.05, "high_range": 0.05},
                                    short_position=False,
                                    use_wave_guage=False,
                                    close_order_today=True,
                ),
                "5Minute_5Day": kings_order_rules(
                                    theme=theme,
                                    status='active',
                                    doubledown_timeduration=60,
                                    trade_using_limits=False,
                                    max_profit_waveDeviation=1,
                                    max_profit_waveDeviation_timeduration=5,
                                    timeduration=320,
                                    take_profit=.01,
                                    sell_out=-.0089,
                                    sell_trigbee_trigger=True,
                                    stagger_profits=False,
                                    scalp_profits=False,
                                    scalp_profits_timeduration=30,
                                    stagger_profits_tiers=1,
                                    limitprice_decay_timeduration=1,
                                    skip_sell_trigbee_distance_frequency=0,
                                    ignore_trigbee_at_power=0.01,
                                    # ignore_trigbee_in_vwap_range={"low_range": -0.05, "high_range": 0.05},
                                    take_profit_in_vwap_deviation_range={"low_range": -0.05, "high_range": 0.05},
                                    short_position=False,
                                    use_wave_guage=False,
                                    close_order_today=True,
                ),
                "30Minute_1Month": kings_order_rules(
                                    theme=theme,
                                    status='active',
                                    doubledown_timeduration=60,
                                    trade_using_limits=False,
                                    max_profit_waveDeviation=1,
                                    max_profit_waveDeviation_timeduration=30,
                                    timeduration=43800,
                                    take_profit=.01,
                                    sell_out=-.0089,
                                    sell_trigbee_trigger=True,
                                    stagger_profits=False,
                                    scalp_profits=False,
                                    scalp_profits_timeduration=30,
                                    stagger_profits_tiers=1,
                                    limitprice_decay_timeduration=1,
                                    skip_sell_trigbee_distance_frequency=0,
                                    ignore_trigbee_at_power=0.01,
                                    # ignore_trigbee_in_vwap_range={"low_range": -0.05, "high_range": 0.05},
                                    take_profit_in_vwap_deviation_range={"low_range": -0.05, "high_range": 0.05},
                                    short_position=False,
                                    use_wave_guage=False,
                ),
                "1Hour_3Month": kings_order_rules(
                                    theme=theme,
                                    status='active',
                                    doubledown_timeduration=60,
                                    trade_using_limits=False,
                                    max_profit_waveDeviation=1,
                                    max_profit_waveDeviation_timeduration=60,
                                    timeduration=43800 * 3,
                                    take_profit=.01,
                                    sell_out=-.0089,
                                    sell_trigbee_trigger=True,
                                    stagger_profits=False,
                                    scalp_profits=False,
                                    scalp_profits_timeduration=30,
                                    stagger_profits_tiers=1,
                                    limitprice_decay_timeduration=1,
                                    skip_sell_trigbee_distance_frequency=0,
                                    ignore_trigbee_at_power=0.01,
                                    # ignore_trigbee_in_vwap_range={"low_range": -0.05, "high_range": 0.05},
                                    take_profit_in_vwap_deviation_range={"low_range": -0.05, "high_range": 0.05},
                                    short_position=False,
                                    use_wave_guage=False,
                ),
                "2Hour_6Month": kings_order_rules(
                                    theme='nuetral',
                                    status='active',
                                    doubledown_timeduration=60,
                                    trade_using_limits=False,
                                    max_profit_waveDeviation=1,
                                    max_profit_waveDeviation_timeduration=120,
                                    timeduration=43800 * 6,
                                    take_profit=.01,
                                    sell_out=-.0089,
                                    sell_trigbee_trigger=True,
                                    stagger_profits=False,
                                    scalp_profits=False,
                                    scalp_profits_timeduration=30,
                                    stagger_profits_tiers=1,
                                    limitprice_decay_timeduration=1,
                                    skip_sell_trigbee_distance_frequency=0,
                                    ignore_trigbee_at_power=0.01,
                                    # ignore_trigbee_in_vwap_range={"low_range": -0.05, "high_range": 0.05},
                                    take_profit_in_vwap_deviation_range={"low_range": -0.05, "high_range": 0.05},
                                    short_position=False,
                                    use_wave_guage=False,
                ),
                "1Day_1Year": kings_order_rules(
                                    theme=theme,
                                    status='active',
                                    doubledown_timeduration=60,
                                    trade_using_limits=False,
                                    max_profit_waveDeviation=1,
                                    max_profit_waveDeviation_timeduration=60 * 24, 
                                    timeduration=525600,
                                    take_profit=.05,
                                    sell_out=-.015,
                                    sell_trigbee_trigger=True,
                                    stagger_profits=False,
                                    scalp_profits=False,
                                    scalp_profits_timeduration=30,
                                    stagger_profits_tiers=1,
                                    limitprice_decay_timeduration=1,
                                    skip_sell_trigbee_distance_frequency=0,
                                    ignore_trigbee_at_power=0.01,
                                    # ignore_trigbee_in_vwap_range={"low_range": -0.05, "high_range": 0.05},
                                    take_profit_in_vwap_deviation_range={"low_range": -0.05, "high_range": 0.05},
                                    short_position=False,
                                    use_wave_guage=False,
                ),
            }
        else: # custom catch all ? Random AI
            print("there is no else, get it right")

        return symbol_theme_vars, star_theme_vars,  wave_block_theme__kor
    
    def star_trading_model_vars(star_theme_vars, wave_block_theme__kor, trigbees, stars=stars):

        def star_kings_order_rules_mapping(stars, trigbees, waveBlocktimes, wave_block_theme__kor=wave_block_theme__kor,):
            # symbol_theme_vars, star_theme_vars, wave_block_theme__kor =  theme_king_order_rules(theme=theme, stars=stars)
            # star_kings_order_rules_dict["1Minute_1Day"][trigbee]
            # for theme in themes
            # import copy
            star_kings_order_rules_dict = {} # Master Return
            for star in stars().keys():
                star_kings_order_rules_dict[star] = {}
                for trigbee in trigbees:
                    star_kings_order_rules_dict[star][trigbee] = {}
                    for blocktime in waveBlocktimes:
                        star_kings_order_rules_dict[star][trigbee][blocktime] = wave_block_theme__kor.get(star) # theme=theme

            return star_kings_order_rules_dict

        def star_vars_mapping(star_theme_vars, trigbees, waveBlocktimes, stars=stars,theme=theme,):
            return_dict = {}
            
            trigbees_king_order_rules = star_kings_order_rules_mapping(stars=stars, trigbees=trigbees, waveBlocktimes=waveBlocktimes)
            
            star = "1Minute_1Day"
            return_dict[star] = {
                "total_budget": 0,
                "trade_using_limits": False,
                "buyingpower_allocation_LongTerm": star_theme_vars[star].get('buyingpower_allocation_LongTerm'),
                "buyingpower_allocation_ShortTerm": star_theme_vars[star].get('buyingpower_allocation_ShortTerm'),
                "stagger_profits": star_theme_vars[star].get('stagger_profits'),
                "use_margin": star_theme_vars[star].get('use_margin'),
                "power_rangers": {k: 1 for k in stars().keys()},
                "trigbees": trigbees_king_order_rules[star],
                "short_position": False,
                "ticker_family": [ticker],
                "theme": theme,
            }
            star = "5Minute_5Day"
            return_dict[star] = {
                "total_budget": 0,
                "trade_using_limits": False,
                "buyingpower_allocation_LongTerm": star_theme_vars[star].get('buyingpower_allocation_LongTerm'),
                "buyingpower_allocation_ShortTerm": star_theme_vars[star].get('buyingpower_allocation_ShortTerm'),
                "stagger_profits": star_theme_vars[star].get('stagger_profits'),
                "use_margin": star_theme_vars[star].get('use_margin'),
                "power_rangers": {k: 1 for k in stars().keys()},
                "trigbees": trigbees_king_order_rules[star],
                "short_position": False,
                "ticker_family": [ticker],
                "theme": theme,
            }
            star = "30Minute_1Month"
            return_dict[star] = {
                "total_budget": 0,
                "trade_using_limits": False,
                "buyingpower_allocation_LongTerm": star_theme_vars[star].get('buyingpower_allocation_LongTerm'),
                "buyingpower_allocation_ShortTerm": star_theme_vars[star].get('buyingpower_allocation_ShortTerm'),
                "stagger_profits": star_theme_vars[star].get('stagger_profits'),
                "use_margin": star_theme_vars[star].get('use_margin'),
                "power_rangers": {k: 1 for k in stars().keys()},
                "trigbees": trigbees_king_order_rules[star],
                "short_position": False,
                "ticker_family": [ticker],
                "theme": theme,
            }
            star = "1Hour_3Month"
            return_dict[star] = {
                "total_budget": 0,
                "trade_using_limits": False,
                "buyingpower_allocation_LongTerm": star_theme_vars[star].get('buyingpower_allocation_LongTerm'),
                "buyingpower_allocation_ShortTerm": star_theme_vars[star].get('buyingpower_allocation_ShortTerm'),
                "stagger_profits": star_theme_vars[star].get('stagger_profits'),
                "use_margin": star_theme_vars[star].get('use_margin'),
                "power_rangers": {k: 1 for k in stars().keys()},
                "trigbees": trigbees_king_order_rules[star],
                "short_position": False,
                "ticker_family": [ticker],
                "theme": theme,
            }
            star = "2Hour_6Month"
            return_dict[star] = {
                "total_budget": 0,
                "trade_using_limits": False,
                "buyingpower_allocation_LongTerm": star_theme_vars[star].get('buyingpower_allocation_LongTerm'),
                "buyingpower_allocation_ShortTerm": star_theme_vars[star].get('buyingpower_allocation_ShortTerm'),
                "stagger_profits": star_theme_vars[star].get('stagger_profits'),
                "use_margin": star_theme_vars[star].get('use_margin'),
                "power_rangers": {k: 1 for k in stars().keys()},
                "trigbees": trigbees_king_order_rules[star],
                "short_position": False,
                "ticker_family": [ticker],
                "theme": theme,
            }
            star = "1Day_1Year"
            return_dict[star] = {
                "total_budget": 0,
                "trade_using_limits": False,
                "buyingpower_allocation_LongTerm": star_theme_vars[star].get('buyingpower_allocation_LongTerm'),
                "buyingpower_allocation_ShortTerm": star_theme_vars[star].get('buyingpower_allocation_ShortTerm'),
                "stagger_profits": star_theme_vars[star].get('stagger_profits'),
                "use_margin": star_theme_vars[star].get('use_margin'),
                "power_rangers": {k: 1 for k in stars().keys()},
                "trigbees": trigbees_king_order_rules[star],
                "short_position": False,
                "ticker_family": [ticker],
                "theme": theme,
            }

            return return_dict

        def star_vars(star, star_vars_mapping):
            return {
                "star": star,
                # 'status': star_vars_mapping[star]['status'],
                "trade_using_limits": star_vars_mapping[star]["trade_using_limits"],
                "total_budget": star_vars_mapping[star]["total_budget"],
                "buyingpower_allocation_LongTerm": star_vars_mapping[star]["buyingpower_allocation_LongTerm"],
                "buyingpower_allocation_ShortTerm": star_vars_mapping[star]["buyingpower_allocation_ShortTerm"],
                "power_rangers": star_vars_mapping[star]["power_rangers"],
                "trigbees": star_vars_mapping[star]["trigbees"],
                "short_position": star_vars_mapping[star]["short_position"],
                "ticker_family": star_vars_mapping[star]["ticker_family"],
            }

        # Get Stars Trigbees and Blocktimes to create kings order rules
        all_stars = stars().keys()
        waveBlocktimes = [
            "premarket",
            "morning_9-11",
            "lunch_11-2",
            "afternoon_2-4",
            "afterhours",
            "Day",
        ]
        star_vars_mapping_dict = star_vars_mapping(
            trigbees=trigbees, waveBlocktimes=waveBlocktimes, stars=stars, theme=theme, star_theme_vars=star_theme_vars
        )

        return_dict = {
            star: star_vars(star=star, star_vars_mapping=star_vars_mapping_dict)
            for star in all_stars
        }

        return return_dict

    def model_vars(trading_model_name, star, stars_vars, stars=stars):
        return {
            # 'status': stars_vars[star]['status'],
            "buyingpower_allocation_LongTerm": stars_vars[star]["buyingpower_allocation_LongTerm"],
            "buyingpower_allocation_ShortTerm": stars_vars[star]["buyingpower_allocation_ShortTerm"],
            "power_rangers": stars_vars[star]["power_rangers"],
            "trade_using_limits": stars_vars[star]["trade_using_limits"],
            "total_budget": stars_vars[star]["total_budget"],
            "trigbees": stars_vars[star]["trigbees"],
            "index_inverse_X": "1X",
            "index_long_X": "1X",
            "trading_model_name": trading_model_name,
        }

    def tradingmodel_vars(
        symbol_theme_vars,
        stars_vars,
        trigbees=trigbees,
        ticker=ticker,
        trading_model_name=trading_model_name,
        status=status,
        portforlio_weight_ask=portforlio_weight_ask,
        stars=stars,
        portfolio_name=portfolio_name,
        theme=theme,):
        
        afterhours = True if ticker in crypto_currency_symbols else False
        afternoon = True if ticker in crypto_currency_symbols else True
        lunch = True if ticker in crypto_currency_symbols else True
        morning = True if ticker in crypto_currency_symbols else True
        premarket = True if ticker in crypto_currency_symbols else False
        Day = True if ticker in crypto_currency_symbols else False

        time_blocks = {
            "premarket": premarket,
            "afterhours": afterhours,
            "morning_9-11": morning,
            "lunch_11-2": lunch,
            "afternoon_2-4": afternoon,
            "afterhours": afterhours,
            "Day": Day,
        }

        allow_for_margin = [False if ticker in crypto_currency_symbols else True][0]
        # etf_X_direction = ["1X", "2X", "3X"]  # Determined by QUEEN

        def init_stars_allocation():
            return {}

        model1 = {
            "theme": theme,
            "QueenBeeTrader": "Jq",
            "status": status,
            "buyingpower_allocation_LongTerm": 1,
            "buyingpower_allocation_ShortTerm": 0,
            "index_long_X": "1X",
            "index_inverse_X": "1X",
            "portforlio_weight_ask": portforlio_weight_ask,
            "total_budget": 0,
            "max_single_trade_amount": 100000,
            "allow_for_margin": allow_for_margin,
            "buy_ONLY_by_accept_from_QueenBeeTrader": False,
            "trading_model_name": trading_model_name,
            "portfolio_name": portfolio_name,
            "trigbees": {k: True for k in trigbees},
            "time_blocks": time_blocks,
            "power_rangers": {k: True for k in stars().keys()},
            "stars": {k: True for k in stars().keys()},
            "stars_kings_order_rules": {
                star: model_vars(
                    trading_model_name=trading_model_name,
                    star=star,
                    stars_vars=stars_vars,
                )
                for star in stars().keys()
            },
            "short_position": False,  # flip all star allocation to short
            "ticker_family": [ticker],
            "refresh_star" : None, # WORKERBEE needs to update model to add in different stars
        }

        star_model = {ticker: model1}

        return star_model

    try:
        # Trading Model Version 1
        symbol_theme_vars, star_theme_vars, wave_block_theme__kor =  theme_king_order_rules(theme=theme, stars=stars)
        stars_vars = star_trading_model_vars(star_theme_vars, wave_block_theme__kor, trigbees)
        # {ticker: model_vars}
        macd_model = tradingmodel_vars(symbol_theme_vars=symbol_theme_vars, stars_vars=stars_vars)

        # if init==False:
        #     print(f'{trading_model_name} {ticker} {theme} Model Generated')

        return {"MACD": macd_model}
    except Exception as e:
        print_line_of_error("generate trading model error")
        return None


def return_queen_orders__query(QUEEN, queen_order_states, ticker=False, star=False, ticker_time_frame=False, trigbee=False, info='1var able queried at a time'):
    q_orders = QUEEN['queen_orders']
    if len(q_orders) == 1 and q_orders.index[0] == None: # init only
        return ''
    if ticker_time_frame:
        orders = q_orders[q_orders['queen_order_state'].isin(queen_order_states) & (q_orders['ticker_time_frame'].isin([ticker_time_frame]))]
    elif ticker:
        orders = q_orders[q_orders['queen_order_state'].isin(queen_order_states) & (q_orders['ticker'].isin([ticker]))]
    elif star:
        orders = q_orders[q_orders['queen_order_state'].isin(queen_order_states) & (q_orders['star'].isin([star]))] ## needs to be added to orders
    elif trigbee:
        orders = q_orders[q_orders['queen_order_state'].isin(queen_order_states) & (q_orders['trigbee'].isin([trigbee]))] ## needs to be added to orders
    else:
        orders = q_orders[q_orders['queen_order_state'].isin(queen_order_states)] ## needs to be added to orders

    return orders


def return_ttf_remaining_budget(QUEEN, total_budget, borrow_budget, active_queen_order_states, ticker_time_frame, cost_basis_ref='cost_basis_current'):
    try:
        if not QUEEN:
            print("NO QUEEN")
            active_orders = {}
            remaining_budget = 0
            remaining_budget_borrow = 0
            budget_cost_basis = 0
            borrowed_cost_basis = 0
            buys_at_play = 0
            sells_at_play = 0
            return active_orders, remaining_budget, remaining_budget_borrow, budget_cost_basis, borrowed_cost_basis, buys_at_play, sells_at_play
        
        # Total In Running, Remaining
        active_orders = return_queen_orders__query(QUEEN, queen_order_states=active_queen_order_states, ticker_time_frame=ticker_time_frame,)
        if len(active_orders) == 0:
            return '', total_budget, borrow_budget, 0, 0, 0, 0
        

        
        # active_orders['long_short'] = np.where(active_orders['trigname'].str.contains('buy'), 'long', 'long') # WORKERBEE NO SHORTING ALLOWED YET...
        # buy_orders = active_orders[active_orders['long_short'] == 'long']
        # sell_orders = active_orders[active_orders['long_short'] == 'short']
        # # get cost basis
        # cost_basis_current = sum(active_orders[cost_basis_ref]) if len(active_orders) > 0 else 0
        # buys_at_play = sum(buy_orders[cost_basis_ref]) if len(buy_orders) > 0 else 0
        # sells_at_play = sum(sell_orders[cost_basis_ref]) if len(sell_orders) > 0 else 0

        buys_at_play, sells_at_play, cost_basis_current = return_long_short(active_orders, cost_basis_ref)

        # check current cost_basis
        if cost_basis_current == 0:
            budget_cost_basis = 0
            borrowed_cost_basis = 0
            remaining_budget = total_budget
            remaining_budget_borrow = borrow_budget
            return active_orders, remaining_budget, remaining_budget_borrow, budget_cost_basis, borrowed_cost_basis, buys_at_play, sells_at_play
        
        remaining_budget = total_budget - cost_basis_current
        if remaining_budget < 0:
            budget_cost_basis = total_budget
            borrowed_cost_basis = abs(remaining_budget)
            # (ticker_time_frame, "over budget")
            remaining_budget_borrow = borrow_budget - borrowed_cost_basis
            if remaining_budget_borrow < 0:
                # (ticker_time_frame, "WHATT YOU WENT OVER BORROW BUDGET")
                remaining_budget_borrow = 0
        else:
            budget_cost_basis = cost_basis_current
            borrowed_cost_basis = 0
            remaining_budget = remaining_budget
            remaining_budget_borrow = borrow_budget
        
        return active_orders, remaining_budget, remaining_budget_borrow, budget_cost_basis, borrowed_cost_basis, buys_at_play, sells_at_play
    
    except Exception as e:
        print_line_of_error("return_ttf_remaining_budget")


def return_trading_model_trigbee(tm_trig, trig_wave_length):
    on_wave_buy = True if trig_wave_length != '0' else False
    if on_wave_buy:
        tm_trig = 'buy_cross-0' if 'buy' in tm_trig else 'sell_cross-0'
    
    return tm_trig


def return_star_from_ttf(x):
    try:
        ticker, tframe, tperiod = x.split("_")
        return f'{tframe}_{tperiod}'
    except Exception as e:
        print(e)
        return x  


def weight_team_keys():
    return {
        'w_L': 'w_L',
        'w_S': 'w_S',
        '1Minute_1Day': 'w_15',# : ['1Minute_1Day', '5Minute_5Day', '30Minute_1Month', '1Hour_3Month', '2Hour_6Month', '1Day_1Year'],
        '5Minute_5Day': 'w_15',
        '30Minute_1Month': 'w_30',
        '1Hour_3Month': 'w_30',
        '2Hour_6Month': 'w_54',
        '1Day_1Year': 'w_54',
    }


def wave_gauge_revrec_2(symbol, df_waves, weight_team = ['w_L', 'w_S', 'w_15', 'w_30', 'w_54'], 
               model_eight_tier=8, 
               wave_guage_list=['end_tier_macd', 'end_tier_vwap', 'end_tier_rsi_ema'], 
               star_weights = {'1Minute_1Day': .1, '5Minute_5Day': .4, '30Minute_1Month': .6, '1Hour_3Month': .6, '2Hour_6Month': .8, '1Day_1Year': .89},
               long_weight=.89, margin_weight=.33):
    try:
        # WORKERBEE update these objs to be based on weight_team_keys func dict return
        weight__short = ['1Minute_1Day', '5Minute_5Day']
        weight__mid = ['30Minute_1Month', '1Hour_3Month']
        weight__long = ['2Hour_6Month', '1Day_1Year'] # future force
        # weight__3 = ['1Minute_1Day', '5Minute_5Day', '30Minute_1Month']
        # print(df_waves.columns)
        for ticker_time_frame in df_waves.index:
            ticker, tframe, tperiod = ticker_time_frame.split("_")
                
            df_waves.at[ticker_time_frame, 'w_L'] = long_weight
            df_waves.at[ticker_time_frame, 'w_S'] = margin_weight

            if f'{tframe}_{tperiod}' in weight__short:
                df_waves.at[ticker_time_frame, 'w_15'] = .89 # luck
            elif f'{tframe}_{tperiod}' in weight__mid:
                df_waves.at[ticker_time_frame, 'w_30'] = .89 # luck
            elif f'{tframe}_{tperiod}' in weight__long:
                df_waves.at[ticker_time_frame, 'w_54'] = .89 # luck
            else:
                df_waves.at[ticker_time_frame, 'w_15'] = .11 # luck
                df_waves.at[ticker_time_frame, 'w_30'] = .11 # luck
                df_waves.at[ticker_time_frame, 'w_54'] = .11 # luck

        guage_return = {}
        df_waves = df_waves.fillna(0)
        for weight_ in weight_team:

            df_waves[f'{weight_}_weight_base'] = df_waves[weight_] * model_eight_tier
            df_waves[f'{weight_}_macd_weight_sum'] = df_waves[weight_] * df_waves['end_tier_macd']
            # df_waves[f'{weight_}_hist_weight_sum'] = df_waves[weight_] * df_waves['end_tier_hist']
            df_waves[f'{weight_}_vwap_weight_sum'] = df_waves[weight_] * df_waves['end_tier_vwap'] ## skip out on OLD tickers that haven't been refreshed
            df_waves[f'{weight_}_rsi_weight_sum'] = df_waves[weight_] * df_waves['end_tier_rsi_ema']

            # Macd Tier Position 
            guage_return[f'{weight_}_macd_tier_position'] = sum(df_waves[f'{weight_}_macd_weight_sum']) / sum(df_waves[f'{weight_}_weight_base'])
            # guage_return[f'{weight_}_hist_tier_position'] = sum(df_waves[f'{weight_}_hist_weight_sum']) / sum(df_waves[f'{weight_}_weight_base'])

            guage_return[f'{weight_}_vwap_tier_position'] = sum(df_waves[f'{weight_}_vwap_weight_sum']) / sum(df_waves[f'{weight_}_weight_base'])
            guage_return[f'{weight_}_rsi_tier_position'] = sum(df_waves[f'{weight_}_rsi_weight_sum']) / sum(df_waves[f'{weight_}_weight_base'])

        guage_return['symbol'] = symbol
        
        return guage_return
    
    except Exception as e:
        print_line_of_error(e)
        return None


def return_trading_model_mapping(QUEEN_KING, waveview):
    return_main = {}
    for ttf in waveview.index.to_list():
        try:
            ticker = waveview.at[ttf, 'symbol']
            star_time = waveview.at[ttf, 'star']
            tm_trig = waveview.at[ttf, 'macd_state']
            trig_wave_length = waveview.at[ttf, 'length']
            tm_trig = return_trading_model_trigbee(tm_trig, trig_wave_length)
            wave_blocktime = waveview.at[ttf, 'wave_blocktime']
            
            trading_model = QUEEN_KING['king_controls_queen']['symbols_stars_TradingModel'].get(ticker)
            if trading_model:
                king_order_rules = trading_model['stars_kings_order_rules'][star_time]['trigbees'][tm_trig][wave_blocktime]
                return_main[ttf] = king_order_rules
            else:
                trading_model = QUEEN_KING['king_controls_queen']['symbols_stars_TradingModel'].get("SPY")
                king_order_rules = trading_model['stars_kings_order_rules'][star_time]['trigbees'][tm_trig][wave_blocktime]
                return_main[ttf] = king_order_rules
        except Exception as e:
            print_line_of_error(e)
            return_main[ttf] = {}
    
    return return_main


def star_ticker_WaveAnalysis(STORY_bee, ticker_time_frame, trigbee=False): # buy/sell cross
    """ Waves: Current Wave, answer questions about proir waves """
    
    # index                                                                 0
    # wave_n                                                               37
    # length                                                              8.0
    # wave_blocktime                                            afternoon_2-4
    # wave_start_time                               2022-08-31 15:52:00-04:00
    # wave_end_time                          2022-08-31 16:01:00.146718-04:00
    # trigbee                                                    sell_cross-0
    # maxprofit                                                        0.0041
    # time_to_max_profit                                                  8.0
    # macd_wave_n                                                           0
    # macd_wave_length                                        0 days 00:11:00    

    token_df = pd.DataFrame(STORY_bee[ticker_time_frame]['waves']['buy_cross-0']).T
    current_buywave = token_df.iloc[0]

    token_df = pd.DataFrame(STORY_bee[ticker_time_frame]['waves']['sell_cross-0']).T
    current_sellwave = token_df.iloc[0]

    # token_df = pd.DataFrame(STORY_bee[ticker_time_frame]['waves']['ready_buy_cross']).T
    # ready_buy_cross = token_df.iloc[0]


    if current_buywave['wave_start_time'] > current_sellwave['wave_start_time']:
        current_wave = current_buywave
    else:
        current_wave = current_sellwave


    d_return = {'buy_cross-0': current_buywave, 'sell_cross-0':current_sellwave }



    return {'current_wave': current_wave, 'current_active_waves': d_return}


def refresh_chess_board__revrec(acct_info, QUEEN, QUEEN_KING, STORY_bee, active_queen_order_states=None, wave_blocktime=None, check_portfolio=True, chess_board='chess_board', wash_sale_rule=None): # WORKERBEE remove queen order states
    # WORKERBEE move out QUEEN_KING and only bring in chess_board *
    try:
        rr_starttime = datetime.now()
        s = datetime.now()

        rr_run_cycle = {}
        # base line power allocation per qcp
        revrec__stars_borrow = {}
        symbol_qcp_dict = {}
        board_tickers = []
        # ticker_TradingModel = {}
        chess_board__revrec = {}
        revrec__ticker={}
        revrec__ticker_borrow={}
        revrec__stars={}
        chess_board__revrec_borrow={}
        marginPower={}
        df_star_agg = {'allocation_long': 'sum', 'allocation_long_deploy': 'sum', 'star_buys_at_play': 'sum', 'star_sells_at_play': 'sum', 'money': 'sum', 'honey': 'sum', 'queen_wants_to_sell_qty': 'sum' } # 



        if not QUEEN.get('portfolio') or not check_portfolio:
            df_broker_portfolio = pd.DataFrame([{'symbol': 'init_jq'}])
        else:
            df_broker_portfolio = pd.DataFrame([v for i, v in QUEEN['portfolio'].items()])
        df_broker_portfolio = df_broker_portfolio.set_index('symbol', drop=False)

        symbols = [item for sublist in [v.get('tickers') for v in QUEEN_KING[chess_board].values()] for item in sublist]
        if check_portfolio:
            missing_tickers = [i for i in df_broker_portfolio.index if i not in symbols and i not in ['init_jq']]
            if missing_tickers:
                print("RR SYMBOLS NOT IN CHESSBOARD", missing_tickers)
                if 'non_active_stories' not in QUEEN_KING[chess_board].keys():
                    QUEEN_KING[chess_board]['non_active_stories'] = init_qcp(piece_name='non_active_stories', ticker_list=missing_tickers, buying_power=0)
                else:
                    non_tics = QUEEN_KING[chess_board]['non_active_stories'].get('tickers')
                    for tic in missing_tickers:
                        if tic not in non_tics:
                            non_tics.append(tic)
                    QUEEN_KING[chess_board]['non_active_stories']['tickers'] = non_tics
        # Check for First
        # if not active_queen_order_states:
        active_queen_order_states = kingdom__global_vars().get('active_queen_order_states')

        if not QUEEN.get('revrec'):
            print( "QUEENMIND", "Fresh Queen on the Block")
            ticker_trinity = None
            q_revrec = None
            pass
        else:
            # Handle Weight Adjustments based on Story
            q_revrec = QUEEN.get('revrec')
            # q_story = q_revrec.get('storygauge')
            # ticker_trinity = dict(zip(q_story['symbol'], q_story['trinity_w_L']))
            waveview = q_revrec.get('waveview')
            waveview['total_allocation_budget_long'] = np.where((waveview['bs_position']=='buy'), 
                                                    waveview['total_allocation_budget'], 
                                                    (waveview['star_total_budget'] - waveview['total_allocation_budget'])
                                                    )
            alloc_weight = 'total_allocation_budget_long' if 'total_allocation_budget_long' in waveview.columns.tolist() else 'total_allocation_budget'
            symbols_budget_alloc = waveview.groupby(['symbol']).agg({alloc_weight: 'sum', 'star_total_budget': 'sum'}).reset_index()
            symbols_budget_alloc['symbol_allocation_pct'] = symbols_budget_alloc[alloc_weight] / symbols_budget_alloc['star_total_budget']
            ticker_trinity = dict(zip(symbols_budget_alloc['symbol'], symbols_budget_alloc['symbol_allocation_pct']))
            

        # WORKERBEE: Add validation only 1 symbol per qcp --- QUEEN not needed only need ORDERS and QUEEN_KING
        if not acct_info:
            acct_info = {'accrued_fees': 0.0,
                        'buying_power': 100000,
                        'cash': 0,
                        'daytrade_count': 0,
                        'last_equity': 100000,
                        'portfolio_value': 100000,}
        if not wave_blocktime:
            wave_blocktime = 'Day'
            # current_wave = star_ticker_WaveAnalysis(STORY_bee=STORY_bee, ticker_time_frame="SPY_1Minute_1Day").get('current_wave')
            # wave_blocktime = current_wave.get('wave_blocktime')
    except Exception as e:
        print_line_of_error(f"RevRec Setup Error {e}")
        return None

    def shape_revrec_chesspieces(dic_items, acct_info, chess_board__revrec_borrow, marginPower, cash):

        # -- Borrow DF
        df_borrow = pd.DataFrame(chess_board__revrec_borrow.items(), columns=['qcp', 'buying_power_borrow'])
        bpb = df_borrow['buying_power_borrow'].sum()

        if bpb > 0:
            if cash < 0:
            # -- Apply cash cap if negative (e.g., -0.25 means only 25% of borrow budget allowed)
                df_borrow['borrow_budget'] = (df_borrow['buying_power_borrow'] * acct_info.get('buying_power', 0)) / bpb
                borrow_cap = abs(cash)
                df_borrow['borrow_budget'] = df_borrow['borrow_budget'] * borrow_cap
            else:
                df_borrow['borrow_budget'] = 0
        else:
            df_borrow['borrow_budget'] = 0

        # -- Regular DF
        df = pd.DataFrame(dic_items.items(), columns=['qcp', 'buying_power'])
        bp = df['buying_power'].sum()

        if bp > 0:
            base_budget = (df['buying_power'] * acct_info.get('last_equity', 0)) / bp
            if cash > 0:
                df['total_budget'] = base_budget - (base_budget * cash)  # total_budget absorbs cash
            else:
                df['total_budget'] = base_budget
        else:
            df['total_budget'] = 0

        # -- Merge & Final Touches
        df = pd.merge(df, df_borrow, how='left', on='qcp')
        df = df.set_index('qcp', drop=False)
        df['margin_power'] = df['qcp'].map(marginPower)

        return df

    def shape_revrec_tickers(dic_items, symbol_qcp_dict, df_qcp):
        df = pd.DataFrame(dic_items.items())
        df = df.rename(columns={0: 'qcp_ticker', 1: 'ticker_buying_power'})
        df = df.set_index('qcp_ticker', drop=False)
        df['qcp'] = df['qcp_ticker'].map(symbol_qcp_dict)
        df['margin_power'] = df['qcp'].map(dict(zip(df_qcp['qcp'], df_qcp['margin_power'])))
        df['piece_name'] = df['qcp'].map(dict(zip(df_qcp['qcp'], df_qcp['piece_name'])))
        df__ = len(df)

        # drop duplicates
        df = df.drop_duplicates(subset='qcp_ticker')

        if len(df) != df__:
            print("RevRec Duplicate Ticker")
        
        return df

    def shape_revrec_stars(dic_items, revrec__stars_borrow, symbol_qcp_dict, df_qcp): 
        df = pd.DataFrame(dic_items.items())
        df_main = df.rename(columns={0: 'qcp_ticker_star', 1: 'star_buying_power'})

        df = pd.DataFrame(revrec__stars_borrow.items())
        df = df.rename(columns={0: 'qcp_ticker_star', 1: 'star_borrow_buying_power'})

        df_main = df_main.merge(df, how='left', on='qcp_ticker_star')
        df_main = df_main.set_index('qcp_ticker_star', drop=False)
        
        df_main['ticker_time_frame'] = df_main.index
        df_main['ticker'] = df_main['ticker_time_frame'].apply(lambda x: x.split("_")[0])
        df_main['star'] = df_main['ticker_time_frame'].apply(lambda x: return_star_from_ttf(x))
        
        df_main['qcp'] = df_main['ticker'].map(symbol_qcp_dict)

        df_main['margin_power'] = df_main['qcp'].map(dict(zip(df_qcp['qcp'], df_qcp['margin_power'])))

        return df_main

    def return_trading_model(QUEEN_KING, qcp, ticker):
        trading_model = QUEEN_KING['king_controls_queen']['symbols_stars_TradingModel'].get(ticker)
        # Handle missing TM
        if trading_model is None: 
            # print(ticker, ' tradingmodel missing handling in revrec to default')
            QUEEN_KING['king_controls_queen']['symbols_stars_TradingModel'].update(generate_TradingModel(ticker=ticker, theme=QUEEN_KING[chess_board][qcp].get('theme'))["MACD"])
            trading_model = QUEEN_KING['king_controls_queen']['symbols_stars_TradingModel'].get(ticker)

        return trading_model
    
    def calculate_weights(data):
        # Calculate the sum of absolute values for normalization
        total = sum(abs(value) for value in data.values())
        
        # Function to apply the weight rules
        def apply_rules(value):
            if value == 0:
                return .08
            elif value < 0 and value > -.1:
                return 0.05
            elif value < -.1 and value > -.3:
                return .06
            elif value < -.3 and value > -.5:
                return .3
            elif value < -.5 and value >-.6:
                return .4
            elif value < -.6:
                return .3
            else:
                weight = abs(value) / total
                # if 0.75 >= value <= 0.80:
                #     weight *= 0.55
                # elif 0.8 > value <= 0.85:
                #     weight *= 0.65
                # elif value > 0.89:
                #     weight *= 0.20
                return weight
        
        # Apply rules to each value and create a new dictionary with raw weights
        raw_weights = {key: apply_rules(value) for key, value in data.items()}
        
        # Calculate total weight and adjust weights to ensure they sum to 1
        total_weight = sum(raw_weights.values())
        if total_weight > 0:
            # Adjust weights to ensure they sum to 1
            adjusted_weights = {key: weight / total_weight for key, weight in raw_weights.items()}
        else:
            # Handle case where all weights are zero to avoid division by zero
            adjusted_weights = {key: 1 / len(data) for key in raw_weights}
        
        return adjusted_weights

    def validate_qcp_balance(df_qcp):
        # Validate Budget Allocations
        for qcp in df_qcp.index:
            tickers_ = df_ticker[df_ticker['qcp'] == qcp]
            if len(tickers_)>0:
                qcp_bp = float(df_qcp.at[qcp, 'buying_power'])
                qcp_tb = float(df_qcp.at[qcp, 'total_budget'])
                deltaa = sum(tickers_['ticker_buying_power']) - qcp_bp
                if abs(deltaa) > 1:
                    msg=(f'{qcp} out of balance by {deltaa} ${round(deltaa * qcp_tb)} Allocation At Risk')
                    print(msg) 
        
    def revrec_allocation(waveview, wave_blocktime):
        
        """ WORK ON
        # handle star allocation, conflicts your sellhomes are cancel out the flying
        """
        # Global
        tier_max = 8
        sell_smoother = .1
        tier_max_universe = tier_max * 2 # 16
        alloc_powerlen_base_weight = .23 #????

        # Weight Tiers of Time and Profit
        allloc_time_weight = 2
        alloc_powerlen_weight = 1
        alloc_currentprofit_weight = 4
        alloc_maxprofit_shot_weight = 1
        revrec_weight_sum = allloc_time_weight + alloc_powerlen_weight + alloc_currentprofit_weight + alloc_maxprofit_shot_weight

        # Weight Tiers of Tier Gain
        macd_weight = 3
        vwap_weight = 2
        rsi_weight = 3
        wavestat_weight_sum = macd_weight + vwap_weight + rsi_weight

        # Weight Tiers of Start Tier
        macd_start_weight = 3
        vwap_start_weight = 2
        rsi_start_weight = 1
        wavestat_start_weight_sum = macd_start_weight + vwap_start_weight + rsi_start_weight

        alloc_trinity_of__len_and_profit = 1
        wave_tiers_allocation = 1
        wave_tier_start = 1
    
        try:

            """Weights of 3 sets (profit/len, tier_gain, tier_start) to the final allocation table"""
            waveview['wave_blocktime'] = wave_blocktime
            # return all STORY BEE Data
            current_wave_stats = []
            for ttf in waveview.index:

                dict_return = {}
                dict_return['ttf'] = ttf
                # story
                current_macd = STORY_bee[ttf]["story"].get("macd_state")
                bs_position = STORY_bee[ttf]["story"].get("macd_state_side")
                dict_return['bs_position'] = bs_position
                dict_return['macd_state'] = current_macd
                # waves
                trigbee = f'{bs_position}_cross-0'
                token = STORY_bee[ttf]['waves'][trigbee]
                first_key = next(iter(token))
                # print(ttf, len(token), first_key, token[first_key].get('wave_id'))
                dict_return['maxprofit'] = token[first_key].get('maxprofit')
                dict_return['current_profit'] = token[first_key].get('current_profit')
                dict_return['time_to_max_profit'] = token[first_key].get('time_to_max_profit')
                dict_return['length'] = token[first_key].get('length')
                dict_return['start_tier_macd'] = token[first_key].get('start_tier_macd')
                dict_return['end_tier_macd'] = token[first_key].get('end_tier_macd')
                dict_return['start_tier_vwap'] = token[first_key].get('start_tier_vwap')
                dict_return['end_tier_vwap'] = token[first_key].get('end_tier_vwap')
                dict_return['start_tier_rsi_ema'] = token[first_key].get('start_tier_rsi_ema')
                dict_return['end_tier_rsi_ema'] = token[first_key].get('end_tier_rsi_ema')
                dict_return['macd_tier_gain'] = token[first_key].get('macd_tier_gain')
                dict_return['vwap_tier_gain'] = token[first_key].get('vwap_tier_gain')
                dict_return['rsi_tier_gain'] = token[first_key].get('rsi_tier_gain')
                dict_return['wave_id'] = token[first_key].get('wave_id')
                current_wave_stats.append(dict_return)
            
            # df_current_story = pd.DataFrame(current_story).set_index('ttf')
            df_current_waves = pd.DataFrame(current_wave_stats).set_index('ttf')

            waveview = pd.concat([waveview, df_current_waves], axis=1, join='inner')

            # """ STORY VIEW Star STATS """
            # # Story Buy Waves
            # df_storyview['star'] = df_storyview.index
            # wave_up_star_stats = df_storyview[['star', 'star_avg_time_to_max_profit']].drop_duplicates().reset_index(drop=True).set_index('star')
            # wave_analysis_length = df_storyview[['star', 'star_avg_length']].drop_duplicates().reset_index(drop=True).set_index('star')
            wave_up_star_stats = pd.DataFrame()
            wave_analysis_length = pd.DataFrame()

            # # Story Sell Waves
            # wave_analysis_down['star'] = wave_analysis_down.index
            # wave_analysis_sell = wave_analysis_down[['star', 'star_avg_time_to_max_profit']].drop_duplicates().reset_index(drop=True).set_index('star')
            # wave_analysis_length_sell = wave_analysis_down[['star', 'star_avg_length']].drop_duplicates().reset_index(drop=True).set_index('star')
            wave_analysis_sell = pd.DataFrame()
            wave_analysis_length_sell = pd.DataFrame()
            
            wave_stars_default_time_max_profit  = {
                                            "1Minute_1Day": 8,
                                            "5Minute_5Day": 8,
                                            "30Minute_1Month": 8,
                                            "1Hour_3Month": 8,
                                            "2Hour_6Month": 8,
                                            "1Day_1Year": 11,
                                        }
            wave_stars_default_length  = {
                                            "1Minute_1Day": 23,
                                            "5Minute_5Day": 23,
                                            "30Minute_1Month": 23,
                                            "1Hour_3Month": 23,
                                            "2Hour_6Month": 23,
                                            "1Day_1Year": 23,
                                        }
            wave_stars_default_maxprofit_shot  = {
                                            "1Minute_1Day": .02,
                                            "5Minute_5Day": .1,
                                            "30Minute_1Month": .2,
                                            "1Hour_3Month": .33,
                                            "2Hour_6Month": .50,
                                            "1Day_1Year": .89,
                                        }
            for ttf in df_current_waves.index:
                tic, stime, sframe = ttf.split("_")
                star_avg_mx_profit = wave_up_star_stats.loc[ttf].get('star_avg_time_to_max_profit') if ttf in wave_up_star_stats else wave_stars_default_time_max_profit.get(f'{stime}_{sframe}')
                star_avg_length = wave_analysis_length.loc[ttf].get('star_avg_length') if ttf in wave_analysis_length else wave_stars_default_length.get(f'{stime}_{sframe}')
                waveview.at[ttf, 'star_avg_time_to_max_profit'] = star_avg_mx_profit
                waveview.at[ttf, 'star_avg_length'] = star_avg_length
            
            


            waveview_map = return_trading_model_mapping(QUEEN_KING, waveview)
            waveview['king_order_rules'] = waveview['ticker_time_frame'].map(waveview_map)

            """ CALCULATOR """
            ## base calc variables ##
            # power on current deviation
            waveview['tmp_deivation'] = waveview['time_to_max_profit'] - waveview['star_avg_time_to_max_profit']
            waveview['starmark_len_deivation'] = waveview['length'] / waveview['star_avg_time_to_max_profit']
            # where we are you, tmp - len deviation
            waveview['tmp_length_deivation'] = waveview['time_to_max_profit'] - waveview['length']
            # len - star deviation
            waveview['len__starmark_tmp_deviation'] = waveview['length'] - waveview['star_avg_time_to_max_profit']

            waveview['tmp_deivation_multiplier'] = waveview['tmp_deivation'] / waveview['star_avg_time_to_max_profit']
            waveview['current_tmp_len_multiplier'] = waveview['tmp_length_deivation'] / waveview['star_avg_time_to_max_profit']
            waveview['lev_vs_starmark_tmp_multiplier'] = np.where(waveview['len__starmark_tmp_deviation']>=0, 0, waveview['len__starmark_tmp_deviation'] / waveview['star_avg_time_to_max_profit'])

            waveview['tmp_power'] = waveview['star_total_budget'] * waveview['tmp_deivation_multiplier'] # 
            waveview['tmp_power_len'] = waveview['star_total_budget'] * waveview['current_tmp_len_multiplier'] # 

            # waveview['allocation_power_powerlen'] = np.where((abs(waveview['tmp_power']) - abs(waveview['tmp_power_len'])) < 1, alloc_powerlen_base_weight * waveview['star_total_budget'], waveview['tmp_power'] - waveview['tmp_power_len'])

            """ # TIME to Max Profit Delta from Current Length """
            waveview['alloc_powerlen'] = np.where(waveview['time_to_max_profit'] == 0, 
                                                    -1, 
                                                    ((1- (waveview['length'] - waveview['time_to_max_profit']) / waveview['length']) * -1))
            waveview['alloc_powerlen'] = np.where((waveview['alloc_powerlen'] == -1) & (waveview['length']>1), -.5, waveview['alloc_powerlen']) # check if no mxprofit and length past 1, lose budget

            # OJ allocation time # Allow for Reverse budget outcome
            waveview['allocation'] = waveview['star_total_budget'] * waveview['lev_vs_starmark_tmp_multiplier'] # 
            waveview['allocation_borrow'] = waveview['star_borrow_budget'] * waveview['lev_vs_starmark_tmp_multiplier'] # 

            """# Allocation Profit Deviation # current profit deviation"""
            waveview['current_profit_deviation'] = np.where(
                (waveview['current_profit'] == waveview['maxprofit']) | 
                (waveview['current_profit'] == 0) & (waveview['maxprofit'] == 0), 
                -1, -1 - (waveview['current_profit'] - waveview['maxprofit']) / waveview['maxprofit']
                )
            waveview['current_profit_deviation'] = np.where(waveview['current_profit']< 0, 0, waveview['current_profit_deviation'] )
            waveview['current_profit_deviation_pct'] = np.where(waveview['current_profit_deviation']== 0, 0, waveview['current_profit_deviation'] )
            waveview['current_profit_deviation_pct'] = np.where(waveview['current_profit_deviation']== -1, -1, waveview['current_profit_deviation'] )
            wave_stars_maxprofit_shot = {'SPY_1Minute_1Day': .01}
            waveview['maxprofit_shot'] = waveview['ticker_time_frame'].map(wave_stars_maxprofit_shot).fillna(waveview['star'].map(wave_stars_default_maxprofit_shot)) # join from wave analysis
            waveview['maxprofit_shot_weight'] = (waveview['maxprofit'] / waveview['maxprofit_shot'])
            waveview['maxprofit_shot_weight_score'] = np.where(waveview['maxprofit_shot_weight'] == 0, -1, (waveview['maxprofit_shot_weight'] *-1))# np.where(waveview['tmp_mark_deivation'] < 0, waveview['tmp_mark_deivation'] * waveview['remaining_budget'], 0)
            waveview['maxprofit_shot_weight_score'] = np.where(waveview['maxprofit_shot_weight'] >= 1, 0, (waveview['maxprofit_shot_weight_score']))# np.where(waveview['tmp_mark_deivation'] < 0, waveview['tmp_mark_deivation'] * waveview['remaining_budget'], 0)
            # waveview['maxprofit_deviation__shotweight__score'] = ((waveview['current_profit_deviation']) + (waveview['maxprofit_shot_weight_score']) ) / 2

            # Top Level Allocations on Budget - Time, profit deviation, maxprofit shot
            waveview['alloc_time'] = ((waveview['star_total_budget'] * waveview['lev_vs_starmark_tmp_multiplier'])/waveview['star_total_budget']) * allloc_time_weight * (waveview['star_total_budget'] * waveview['lev_vs_starmark_tmp_multiplier'])/revrec_weight_sum
            waveview['alloc_ttmp_length'] = ((waveview['star_total_budget'] * waveview['alloc_powerlen'])/waveview['star_total_budget']) * alloc_powerlen_weight * (waveview['star_total_budget'] * waveview['alloc_powerlen'])/revrec_weight_sum
            waveview['alloc_currentprofit'] = ((waveview['star_total_budget'] * waveview['current_profit_deviation_pct'])/waveview['star_total_budget']) * alloc_currentprofit_weight * (waveview['star_total_budget'] * waveview['current_profit_deviation_pct'])/revrec_weight_sum
            waveview['alloc_maxprofit_shot'] = ((waveview['star_total_budget'] * waveview['maxprofit_shot_weight_score'])/waveview['star_total_budget']) * alloc_maxprofit_shot_weight * (waveview['star_total_budget'] * waveview['maxprofit_shot_weight_score'])/revrec_weight_sum
            waveview['total_allocation_budget'] = waveview['alloc_time'] + waveview['alloc_ttmp_length'] + waveview['alloc_currentprofit'] + waveview['alloc_maxprofit_shot']
            waveview['total_allocation_budget_long'] = np.where((waveview['bs_position']=='buy'), 
                                                    waveview['total_allocation_budget'], 
                                                    (waveview['star_total_budget'] - waveview['total_allocation_budget'])
                                                    ) 
            # -Tiers
            # # tier divergence, how many tiers have been gain'd / lost MACD/RSI/VWAP // current profit deviation
            weight_tier_team = ['macd', 'vwap', 'rsi_ema']
            for wave_tier in weight_tier_team:
                waveview[f'{wave_tier}_tier_gain'] = waveview[f'end_tier_{wave_tier}'] - waveview[f'start_tier_{wave_tier}'] #np.where((waveview[f'end_tier_{wave_tier}'] - waveview[f'start_tier_{wave_tier}'] > 0), waveview[f'end_tier_{wave_tier}'] - waveview[f'start_tier_{wave_tier}'], 0)
                # ###3 tier,
                waveview[f'{wave_tier}_max_growth'] = (tier_max + 1) - waveview[f'start_tier_{wave_tier}'] # max growth need 9 
                waveview[f'{wave_tier}_tier_gain_weight'] = 1 - (waveview[f'{wave_tier}_tier_gain'] / waveview[f'{wave_tier}_max_growth'])
                waveview[f'{wave_tier}_tier_gain_pct'] = np.where(waveview[f'{wave_tier}_tier_gain'] < 0, np.minimum(waveview[f'{wave_tier}_tier_gain_weight'], 1), waveview[f'{wave_tier}_tier_gain_weight'] * -1)
                if wave_tier == 'macd':
                    weight_score = macd_start_weight
                elif wave_tier == 'vwap':
                    weight_score = vwap_start_weight
                else: # RSI
                    weight_score = rsi_start_weight
                
                waveview[f'alloc_{wave_tier}_tier'] = ((waveview['star_total_budget'] * waveview[f'{wave_tier}_tier_gain_pct'])/waveview['star_total_budget']) * weight_score * (waveview['star_total_budget'] * waveview[f'{wave_tier}_tier_gain_pct'])/wavestat_start_weight_sum

            waveview['tier_gain_movement'] = waveview[[f'alloc_{wt}_tier' for wt in weight_tier_team]].sum(axis=1)
            # total_allocation_budget
            waveview['total_allocation_budget_single'] = waveview['total_allocation_budget'].copy()
            waveview['total_allocation_budget'] = (waveview['total_allocation_budget'] + waveview['tier_gain_movement']) / 2

            waveview['pct_budget_allocation'] = waveview['total_allocation_budget'] / waveview['star_total_budget']
            waveview['total_allocation_borrow_budget'] = (waveview['pct_budget_allocation'] * waveview['star_borrow_budget'])

            #Hold the Line Minimum Allocation with Margin
            # Deploy Allocation Number
            waveview['allocation_deploy'] = np.where((waveview['bs_position']=='buy'), 
                                                        waveview['total_allocation_budget'] - waveview['star_buys_at_play_allocation'], 
                                                        waveview['total_allocation_budget'] - waveview['star_sells_at_play']
                                                        )
            waveview['allocation_deploy'] = np.where(waveview['star_total_budget']<=0,0,waveview['allocation_deploy'])
            
            waveview['allocation_long'] = np.where((waveview['bs_position']=='buy'), 
                                                    waveview['total_allocation_budget'], 
                                                    (waveview['star_total_budget'] - waveview['total_allocation_budget'])
                                                    )
            waveview['allocation_borrow_deploy'] = np.where((waveview['bs_position']=='buy'), # WORKERBEE, consider allocation_deploy for full consideration
                                                            (waveview['total_allocation_borrow_budget'] - waveview['star_buys_at_play_allocation']) , 
                                                            (waveview['total_allocation_borrow_budget'] - waveview['star_sells_at_play']) 
                                                            )
            waveview['allocation_borrow_deploy'] = np.where(waveview['star_borrow_budget']<=0,0,waveview['allocation_borrow_deploy'])

            waveview['allocation_borrow_long'] = np.where((waveview['bs_position']=='buy'), 
                                                    waveview['total_allocation_borrow_budget'], 
                                                    (waveview['star_borrow_budget'] - waveview['total_allocation_borrow_budget'])
                                                    )
            waveview['allocation_borrow_long'] = np.where(waveview['star_borrow_budget']<=0,0,waveview['allocation_borrow_long'])
            
            waveview['allocation_long_deploy'] = (waveview['allocation_long'] + waveview['allocation_borrow_long']) - waveview['star_buys_at_play_allocation']

        except Exception as e:
            print_line_of_error(e)

        return waveview

    def calculate_budgets__query_queen_orders(df_ticker, df_stars, STORY_bee):
        try:
            tt_ = df_ticker.copy()
            tt_2 = df_stars.copy()
            df_active_orders = pd.DataFrame()

            # calculate budgets dollar values and join in current buys / sells as play
            for qcp, data in QUEEN_KING[chess_board].items():            
                tickers = data.get('tickers')
                
                for ticker in tickers:
                    # if ticker == 'AER':
                    #     ipdb.set_trace()
                    # if ticker in crypto_currency_symbols:
                    #     print(ticker, "WORKING HANLDING CRYPTO YET")
                    # #     continue
                    # TICKER
                    df_temp = df_ticker[df_ticker.index.isin(tickers)]
                    bp_ticker = sum(df_temp['ticker_buying_power'])
                    if bp_ticker == 0:
                        df_temp['total_budget'] = 0
                        # df_temp['equity_budget'] = 0
                        df_temp['borrow_budget'] = 0
                    else:
                        df_temp['total_budget'] = (df_temp['ticker_buying_power'] * df_qcp.at[qcp, 'total_budget']) / bp_ticker
                        # df_temp['equity_budget'] = (df_temp['ticker_buying_power'] * df_qcp.at[qcp, 'equity_budget']) / bp_ticker
                        df_temp['borrow_budget'] = ((df_temp['ticker_buying_power'] * df_qcp.at[qcp, 'borrow_budget']) / bp_ticker) * df_qcp.at[qcp, 'margin_power']
                        # budget_remaining, borrowed_budget_remaining = return_ticker_remaining_budgets(cost_basis_current, ticker, df_temp)

                    # UPDTAE TICKER
                    df_ticker.at[ticker, 'ticker_total_budget'] = df_temp.at[ticker, 'total_budget']
                    # df_ticker.at[ticker, 'ticker_equity_budget'] = df_temp.at[ticker, 'equity_budget']
                    df_ticker.at[ticker, 'ticker_borrow_budget'] = df_temp.at[ticker, 'borrow_budget']
                    # df_ticker.at[ticker, 'refresh_star'] = df_qcp.at[qcp, 'refresh_star'] # WORKERBEE del this is a dup?
                    # df_ticker.at[ticker, 'ticker_remaining_borrow'] = borrowed_budget_remaining

                    # UPDATE star time 
                    df_temp = df_stars[(df_stars['ticker'].isin([ticker]))].copy()
                    bp = sum(df_temp['star_buying_power'])
                    if bp_ticker == 0:
                        df_temp['total_budget'] = 0
                        # df_temp['equity_budget'] = 0
                        df_temp['borrow_budget'] = 0
                    else:
                        bp_borrow = sum(df_temp['star_borrow_buying_power'])
                        df_temp['total_budget'] = (df_temp['star_buying_power'] * df_ticker.loc[ticker].get('ticker_total_budget')) / bp
                        # df_temp['equity_budget'] = (df_temp['star_buying_power'] * df_ticker.loc[ticker].get('ticker_equity_budget')) / bp
                        df_temp['borrow_budget'] = (df_temp['star_borrow_buying_power'] * df_ticker.loc[ticker].get('ticker_borrow_budget')) / bp_borrow
                    
                    ## Return price and stats & JOIN in ORDERS
                    ticker_remaining_budget = 0
                    ticker_remaining_borrow = 0
                    ttf_storybeekeys=STORY_bee.keys()
                    for star in df_temp['star'].to_list():
                        ticker_time_frame = f'{ticker}_{star}'
                        if '1Minute_1Day' in ticker_time_frame and ticker_time_frame:
                            if ticker_time_frame in ttf_storybeekeys:
                                current_from_open = STORY_bee[ticker_time_frame]["story"].get("current_from_open", 0)
                                current_from_yesterday = STORY_bee[ticker_time_frame]["story"].get("current_from_yesterday", 0)
                            else:
                                current_from_open = 0
                                current_from_yesterday = 0
                            df_ticker.at[ticker, 'current_from_open'] = current_from_open
                            df_ticker.at[ticker, 'current_from_yesterday'] = current_from_yesterday
                        
                        df_stars.at[f'{ticker}_{star}', 'star_total_budget'] = df_temp.loc[f'{ticker}_{star}'].get('total_budget')
                        # df_stars.at[f'{ticker}_{star}', 'star_equity_budget'] = df_temp.loc[f'{ticker}_{star}'].get('equity_budget')
                        df_stars.at[f'{ticker}_{star}', 'star_borrow_budget'] = df_temp.loc[f'{ticker}_{star}'].get('borrow_budget')
                        star_total_budget = df_stars.at[ticker_time_frame, 'star_total_budget']
                        star_borrow_budget = df_stars.at[ticker_time_frame, 'star_borrow_budget']
                        active_orders, ttf_remaining_budget, remaining_budget_borrow, budget_cost_basis, borrowed_cost_basis, buys_at_play, sells_at_play = return_ttf_remaining_budget(QUEEN=QUEEN, 
                                                                            total_budget=star_total_budget,
                                                                            borrow_budget=star_borrow_budget,
                                                                            ticker_time_frame=ticker_time_frame, 
                                                                            active_queen_order_states=active_queen_order_states)

                        df_stars.at[ticker_time_frame, 'remaining_budget'] = ttf_remaining_budget
                        df_stars.at[ticker_time_frame, 'remaining_budget_borrow'] = remaining_budget_borrow
                        df_stars.at[ticker_time_frame, 'star_at_play'] = budget_cost_basis
                        df_stars.at[ticker_time_frame, 'star_at_play_borrow'] = borrowed_cost_basis
                        df_stars.at[ticker_time_frame, 'star_buys_at_play'] = buys_at_play
                        df_stars.at[ticker_time_frame, 'star_sells_at_play'] = sells_at_play
                        if len(active_orders) > 0: 
                            # Active Orders
                            # return Want to Sell
                            if 'queen_wants_to_sell_qty' in active_orders.columns:
                                df_stars.at[ticker_time_frame, 'queen_wants_to_sell_qty'] = sum(active_orders['queen_wants_to_sell_qty'])
                            else:
                                df_stars.at[ticker_time_frame, 'queen_wants_to_sell_qty'] = 0

                            # return buys at play and Money
                            df_stars.at[ticker_time_frame, 'money'] = sum(active_orders['money'])
                            df_stars.at[ticker_time_frame, 'honey'] = sum(active_orders['honey'])
                            df_active_orders = pd.concat([df_active_orders, active_orders])
                            active_orders_close_today = active_orders[active_orders['side'] == 'buy']
                            if len(active_orders_close_today) > 0:
                                active_orders_close_today = active_orders_close_today[(active_orders_close_today['order_rules'].apply(lambda x: x.get('close_order_today') == True))]
                                # active_orders_close_today['long_short'] = np.where(active_orders_close_today['trigname'].str.contains('buy'), 'long', 'short') 
                                # buy_orders = active_orders_close_today[active_orders_close_today['long_short'] == 'long']
                                buys_at_play_close_today, sells_at_play_today, cost_basis_current = return_long_short(active_orders_close_today)
                                # buys_at_play_close_today = buys_at_play #sum(buy_orders["cost_basis_current"]) if len(buy_orders) > 0 else 0
                                df_stars.at[ticker_time_frame, 'star_buys_at_play_allocation'] = buys_at_play - buys_at_play_close_today
                            else:
                                df_stars.at[ticker_time_frame, 'star_buys_at_play_allocation'] = buys_at_play
                        else:
                            df_stars.at[ticker_time_frame, 'money'] = 0
                            df_stars.at[ticker_time_frame, 'honey'] = 0
                            df_stars.at[ticker_time_frame, 'star_buys_at_play_allocation'] = buys_at_play
                            df_stars.at[ticker_time_frame, 'queen_wants_to_sell_qty'] = 0
                        
                        ticker_remaining_budget += ttf_remaining_budget
                        ticker_remaining_borrow += remaining_budget_borrow
                    
                    df_ticker.at[ticker, 'ticker_remaining_budget'] = ticker_remaining_budget
                    df_ticker.at[ticker, 'ticker_remaining_borrow'] = ticker_remaining_borrow
                
            df_ticker = df_ticker.fillna(0)
            df_stars = df_stars.fillna(0)
            return df_ticker, df_stars, df_active_orders
        except Exception as e:
            print_line_of_error(e)


    try:
        rr_run_cycle.update({'load': (datetime.now() - s).total_seconds()})
        s = datetime.now()

        chessboard = QUEEN_KING[chess_board]
    
        # Handle Weight change
        s = datetime.now()
        symbol_qcp_dict_name = {}
        for qcp, data in chessboard.items():
            
            # Refresh ChessBoard and RevRec
            qcp_power = float(QUEEN_KING[chess_board][qcp].get('total_buyng_power_allocation', 0))
            qcp_borrow_power = float(QUEEN_KING[chess_board][qcp].get('total_borrow_power_allocation', 0))
            qcp_marginpower = float(QUEEN_KING[chess_board][qcp].get('margin_power', 0))
            chess_board__revrec[qcp] = qcp_power
            chess_board__revrec_borrow[qcp] = qcp_borrow_power
            marginPower[qcp] = qcp_marginpower

            qcp_tickers = QUEEN_KING[chess_board][qcp].get('tickers')
            board_tickers = board_tickers + qcp_tickers

            num_tickers = len(qcp_tickers)
            if num_tickers == 0:
                print("No Tickers in Chess Piece", qcp)
                continue

            # Group Trinity and Re-Calculate qcp buying power ??? # WORKERBEE
            
            # CONFIRM TRADING MODEL Ticker Budget Allocation #WORKEBEE trigger based on queen controls 
            ticker_mapping = QUEEN_KING['king_controls_queen'].get('ticker_revrec_allocation_mapping')
            ticker_mapping = ticker_mapping if ticker_mapping else {}

            # if ticker_trinity:
            #     # reallocate weights create a dictionary of ticker and triniity then create a weightet pct
            #     ticker__trinity = {k:v for (k,v) in ticker_trinity.items() if k in qcp_tickers}
            #     ticker_mapping = calculate_weights(ticker__trinity)
            ticker_buying_power = {}
            ticker_borrow_power = {}
            for ticker in qcp_tickers:
                trading_model = return_trading_model(QUEEN_KING, qcp, ticker)
                ticker_buying_power[ticker] = trading_model.get('buyingpower_allocation_LongTerm', 0)
                ticker_borrow_power[ticker] = trading_model.get('buyingpower_allocation_ShortTerm', 0)
            total_weight = sum(ticker_buying_power.values())
            total_weight_borrow = sum(ticker_borrow_power.values())
            
            # ticker_mapping_enabled = True if ticker_mapping else False
            # total_weight = sum(ticker_mapping.values()) if ticker_mapping_enabled else num_tickers

            for ticker in qcp_tickers:

                symbol_qcp_dict[ticker] = qcp
                symbol_qcp_dict_name[ticker] = qcp        
                
                trading_model= return_trading_model(QUEEN_KING, qcp, ticker)
                tm_keys = trading_model['stars_kings_order_rules'].keys()

                ## Ticker Allocation Budget

                if total_weight:
                    weight = ticker_buying_power[ticker]
                    revrec__ticker[ticker] = (weight / total_weight) * qcp_power
                else:
                    revrec__ticker[ticker] = 0
                
                if total_weight_borrow:
                    weight = ticker_borrow_power.get(ticker, 0)
                    revrec__ticker_borrow[ticker] = (weight / total_weight_borrow) * qcp_borrow_power
                else:
                    revrec__ticker_borrow[ticker] = 0
                    # if ticker_mapping_enabled:
                    #     print("Ticker Mapping Enabled")
                    # # if ticker in ticker_mapping.keys():
                    #     # Adjust allocation based on ticker_mapping weight
                    #     weight = ticker_mapping[ticker]
                    #     revrec__ticker[ticker] = (weight / total_weight) * qcp_power
                    # else:
                    #     revrec__ticker[ticker] = qcp_power / num_tickers ## equal number disribution

                # Star Allocation Budget
                for star in tm_keys:
                    revrec__stars[f'{ticker}_{star}'] = trading_model['stars_kings_order_rules'][star].get("buyingpower_allocation_LongTerm")
                    revrec__stars_borrow[f'{ticker}_{star}'] = trading_model['stars_kings_order_rules'][star].get("buyingpower_allocation_ShortTerm")

        # Refresh RevRec Total Budgets
        cash = QUEEN_KING['king_controls_queen']['buying_powers']['Jq']['total_longTrade_allocation']
        df_qcp_og = pd.DataFrame(chessboard).T
        df_qcp = shape_revrec_chesspieces(chess_board__revrec, acct_info, chess_board__revrec_borrow, marginPower, cash)
        df_qcp_og = df_qcp_og[[i for i in df_qcp_og.columns if i not in df_qcp.columns]]
        df_qcp = pd.concat([df_qcp, df_qcp_og], axis=1)
        df_ticker = shape_revrec_tickers(revrec__ticker, symbol_qcp_dict, df_qcp)
        df_stars = shape_revrec_stars(revrec__stars, revrec__stars_borrow, symbol_qcp_dict, df_qcp)
        df_stars = df_stars.fillna(0) # tickers without budget move this to upstream in code and fillna only total budget column
        df_ticker['symbol'] = df_ticker.index
        df_stars['symbol'] = df_stars['ticker']

        # # shape tickers
        # df_qcp_og = pd.DataFrame(chessboard).T.explode('tickers')
        # # Set 'tickers' as the index
        # df_qcp_og = df_qcp_og.set_index('tickers')
        # # Ensure that the index is unique if necessary
        # df_qcp_og = df_qcp_og[~df_qcp_og.index.duplicated(keep='first')]
        # df_qcp_og = df_qcp_og[['piece_name']]
        # df_qcp_og = df_qcp_og[[i for i in df_qcp_og.columns if i not in df_ticker.columns]]
        # df_ticker = pd.concat([df_ticker, df_qcp_og], axis=1)


        validate_qcp_balance(df_qcp)
        rr_run_cycle.update({'shape': (datetime.now() - s).total_seconds()})
        s = datetime.now()
        if check_portfolio:
            df_ticker, df_stars, df_active_orders = calculate_budgets__query_queen_orders(df_ticker, df_stars, STORY_bee)
        else:
            t_col = ['ticker_total_budget', 'ticker_borrow_budget', 'current_from_open', 'current_from_yesterday', 'ticker_remaining_budget', 'ticker_remaining_borrow']
            s_col = ['star_total_budget', 'star_borrow_budget', 'remaining_budget', 'remaining_budget_borrow', 'star_at_play', 'star_at_play_borrow', 'star_buys_at_play', 'star_sells_at_play', 'queen_wants_to_sell_qty', 'money', 'honey', 'star_buys_at_play_allocation']
            for col in t_col:
                df_ticker[col] = 0
            for col in s_col:
                df_stars[col] = 0
            df_active_orders = []

        ## print("ORDERS")
        if len(df_active_orders) > 0:
            df_active_orders['qty_available'] = pd.to_numeric(df_active_orders['qty_available'], errors='coerce')
            symbols_qty_avail = df_active_orders.groupby("symbol")[['qty_available']].sum().reset_index().set_index('symbol', drop=False)
        else:
            symbols_qty_avail = pd.DataFrame({'symbol':'SPY', 'qty_available':0}, index=['symbol'])

        if wash_sale_rule:
            df_wash = pd.DataFrame(wash_sale_rule)
            if len(df_wash) > 0:
                df_wash['loss'] = pd.to_numeric(df_wash['loss'], errors='coerce')
                df_wash = df_wash.groupby(['symbol', 'wash_sale_next_buy_date']).agg({'loss': 'sum'}).reset_index().set_index('symbol')
        else:
            df_wash = pd.DataFrame()

        # Story Bee
        # def storybee__data(STORY_bee, df_ticker):
        for symbol in df_ticker.index:
            ttf = f'{symbol}_1Minute_1Day'
            if ttf not in STORY_bee.keys():
                # print(f'{ttf} missing in story')
                df_ticker.at[symbol, 'current_from_open'] = None
            else:
                df_ticker.at[symbol, 'current_from_open'] = STORY_bee[ttf]['story'].get('current_from_open')
            ### Broker DELTA ###
            if symbol in symbols_qty_avail.index:
                df_ticker.at[symbol, 'qty_available'] = float(symbols_qty_avail.at[symbol, 'qty_available'])
            else:
                df_ticker.at[symbol, 'qty_available'] = 0
            
            if symbol in df_broker_portfolio.index:
                df_ticker.at[symbol, 'broker_qty_available'] = float(df_broker_portfolio.at[symbol, 'qty_available'])
                df_ticker.at[symbol, 'unrealized_pl'] = float(df_broker_portfolio.at[symbol, 'unrealized_pl'])
                df_ticker.at[symbol, 'unrealized_plpc'] = float(df_broker_portfolio.at[symbol, 'unrealized_plpc'])
            else:
                df_ticker.at[symbol, 'broker_qty_available'] = 0
                df_ticker.at[symbol, 'unrealized_pl'] = 0
                df_ticker.at[symbol, 'unrealized_plpc'] = 0
            
            # wash sale
            if symbol in df_wash.index:
                df_ticker.at[symbol, 'wash_loss'] = float(df_wash.at[symbol, 'wash_loss'])
                df_ticker.at[symbol, 'wash_sale_next_buy_date'] = df_wash.at[symbol, 'wash_sale_next_buy_date']
            else:
                df_ticker.at[symbol, 'wash_loss'] = 0
                df_ticker.at[symbol, 'wash_sale_next_buy_date'] = None


        df_ticker['broker_qty_delta'] = df_ticker['qty_available'] - df_ticker['broker_qty_available']
        
        QUEEN['heartbeat']['broker_qty_delta'] = df_ticker['broker_qty_delta'].sum()

        waveview = df_stars.copy()
        ## updated, was removed before bc revalocation wasn't able to handle missing from STORY_bee -- fix allows since mapping is still done
        ttf_errors = []
        for ttf in waveview.index:
            if ttf not in STORY_bee.keys():
                # print(f'{ttf} missing in story excluding from revrec')
                ttf_errors.append(ttf)
                continue
        # waveview = waveview[~waveview.index.isin(ttf_errors)]
        for ttf in ttf_errors:
            tic, tstar, tframe = ttf.split("_")
            star_time = f'{tstar}_{tframe}'
            linking_ttf = f'SPY_{star_time}'
            # waveview.loc[ttf] = waveview.loc[linking_ttf]
            # waveview.at[ttf, 'ticker_time_frame'] = ttf

            STORY_bee[ttf] = STORY_bee[linking_ttf]

        s = datetime.now()
        waveview = revrec_allocation(waveview, wave_blocktime)
        rr_run_cycle.update({'revrec allocation': (datetime.now() - s).total_seconds()})
        
        
        ########### gauge ############
        s = datetime.now()

        def revrec_lastmod(QUEEN):
            if not pg_migration:
                return datetime.fromtimestamp(os.stat(QUEEN['dbs'].get('PB_RevRec_PICKLE')).st_mtime).astimezone(est)
            keys = PollenDatabase.get_all_keys_with_timestamps(table_name=QUEEN['table_name'], db_root=QUEEN['db_root'])
            df = pd.DataFrame(keys)
            df['key_name'] = df[0].apply(lambda x: x.split("-")[-1])
            df = df.set_index('key_name', drop=False)
            return df.at['revrec', 1].tz_localize('UTC').astimezone(est)
        
        def calculate_wave_gauge(symbols, waveview, weight_team_keys=weight_team_keys):
            
            # Wave Gauge # WORKERBEE
            # waveview_symbols = waveview['symbol'].tolist()
            story_guages_view = []
            weight_team = list(weight_team_keys().values()) # ['w_L', 'w_S', 'w_15', 'w_30', 'w_54']
            for symbol in set(symbols):
                # if symbol not in waveview_symbols:
                #     print(f'queen_mind: {symbol} MISSING IN waveview')
                #     continue
                df_waves = waveview[waveview['symbol'] == symbol]
                story_guages = wave_gauge_revrec_2(symbol=symbol, df_waves=df_waves, weight_team=weight_team)
                if story_guages:
                    story_guages_view.append(story_guages)
            
            if story_guages_view:
                df_storyguage = pd.DataFrame(story_guages_view)
                df_storyguage = df_storyguage.set_index('symbol')
                
                # Trinity 
                for w_t in weight_team:
                    df_storyguage[f'trinity_{w_t}'] = (df_storyguage[f'{w_t}_macd_tier_position'] + df_storyguage[f'{w_t}_vwap_tier_position'] + df_storyguage[f'{w_t}_rsi_tier_position']) / 3
                
                return df_storyguage
            else:
                return pd.DataFrame()

        ### Return Story Gauge
        wave_symbols = list(set(waveview['symbol'].tolist()))
        cols =['w_L_macd_tier_position', 'w_L_vwap_tier_position',
       'w_L_rsi_tier_position', 'w_S_macd_tier_position',
       'w_S_vwap_tier_position', 'w_S_rsi_tier_position',
       'w_15_macd_tier_position', 'w_15_vwap_tier_position',
       'w_15_rsi_tier_position', 'w_30_macd_tier_position',
       'w_30_vwap_tier_position', 'w_30_rsi_tier_position',
       'w_54_macd_tier_position', 'w_54_vwap_tier_position',
       'w_54_rsi_tier_position', 'trinity_w_L', 'trinity_w_S', 'trinity_w_15',
       'trinity_w_30', 'trinity_w_54',]
        # revrec = QUEEN.get('revrec')
        # story_g = True if revrec else None
        # if story_g:
        #     story_g = revrec.get('storygauge')
        #     last_mod_revrec = revrec_lastmod(QUEEN)
        #     print(last_mod_revrec)
        #     if (datetime.now(est) - last_mod_revrec).total_seconds() > 500:
        #         print("Refresh Story Gauge")
        #         df_storygauge = calculate_wave_gauge(wave_symbols, waveview)
        #     else:
        #         df_storygauge = story_g
        # else:
        #     df_storygauge = calculate_wave_gauge(wave_symbols, waveview)
        if check_portfolio:
            df_storygauge = calculate_wave_gauge(wave_symbols, waveview)
        df_storygauge = pd.DataFrame(index=wave_symbols)
        for col in cols:
            df_storygauge[col] = 0

        df_storygauge = df_storygauge[cols]
        symbols_failed = [i for i in df_ticker.index if i not in df_storygauge.index]
        if symbols_failed:
            print("symbols missing story attempting to add back", symbols_failed)
            story_token = calculate_wave_gauge(symbols_failed, waveview)
            if len(story_token) > 0:
                story_token = story_token[cols]
                df_storygauge = pd.concat([df_storygauge, story_token])

        
        # Join Story to Tickers
        storygauge = df_ticker.merge(df_storygauge, left_index=True, right_index=True, how='left')
        budget_sum = sum(storygauge['ticker_total_budget'])
        storygauge['pct_portfolio'] = storygauge['ticker_total_budget']  / budget_sum
        symbol_orders = {}
        for symbol in storygauge.index:
            if len(df_active_orders) > 0:
                if symbol in df_active_orders['symbol'].tolist():
                    orders = df_active_orders[df_active_orders['symbol'] == symbol]
                    orders = orders[['ticker_time_frame', 'side', 'qty_available', 'qty', 'money', 'honey', 'trigname']]
                    symbol_orders[symbol] = orders.to_dict(orient='records')
        if symbol_orders:
            storygauge['active_orders'] = storygauge.index.to_series().apply(lambda x: symbol_orders.get(x, []))  # Always return a list

        rr_run_cycle.update({'create gauge': (datetime.now() - s).total_seconds()})
        s = datetime.now()
        ########### gauge ############

        # Get refresh Star
        ticker_refresh_star = QUEEN_KING['king_controls_queen'].get('ticker_refresh_star')
        if type(ticker_refresh_star) == pd.DataFrame:
            storygauge = storygauge.merge(ticker_refresh_star, left_index=True, right_index=True, how='left')
            storygauge['ticker_refresh_star'] = storygauge['ticker_refresh_star'].fillna(False)
            
        # Join in AutoPilot
        ticker_autopilot = QUEEN_KING['king_controls_queen'].get('ticker_autopilot')
        if type(ticker_autopilot) == pd.DataFrame:
            storygauge = storygauge.merge(ticker_autopilot, left_index=True, right_index=True, how='left')
            storygauge['buy_autopilot'] = storygauge['buy_autopilot'].fillna(False)
            storygauge['sell_autopilot'] = storygauge['sell_autopilot'].fillna(False)


        # Price Info data
        if 'price_info_symbols' in QUEEN.keys(): # WORKERBEE handle in new table of all
            price_info_symbols = QUEEN['price_info_symbols']
            df_new = pd.json_normalize(price_info_symbols['priceinfo']).set_index('ticker')
            # storygauge = pd.concat([storygauge, df_new], axis=1, join='outer')
            storygauge = storygauge.merge(df_new, left_index=True, right_index=True, how='left')
            for col in df_new.columns:
                storygauge[col] = storygauge[col].fillna(0)

        df_star_token = waveview.groupby('symbol').agg(df_star_agg).reset_index().set_index('symbol')
        storygauge = storygauge.merge(df_star_token, left_index=True, right_index=True, how='left')
        storygauge = storygauge.fillna(0)
        waveview = waveview.fillna(0)

        # % Change per Star
        for symbol in storygauge.index:
            for star in stars().keys():
                pct_change = STORY_bee[f'{symbol}_{star}']['story'].get('last_close_price')
                storygauge.at[symbol, f'{star}_change'] = pct_change


        rr_run_cycle.update({'story gauge': (datetime.now() - s).total_seconds()})
        total = sum(rr_run_cycle.values())

        cycle_time = (datetime.now()-rr_starttime).total_seconds()
        rr_run_cycle.update({'final time': cycle_time})
        if cycle_time > 10:
            msg=("rervec cycle_time > 10 seconds", cycle_time)
            print(msg)
        print(rr_run_cycle)
        
        return {'cycle_time': cycle_time, 'df_qcp': df_qcp, 'df_ticker': df_ticker, 'df_stars':df_stars, 
                'waveview': waveview, 'storygauge': storygauge, 
                'symbols_failed': symbols_failed, 'ttf_failed': ttf_errors, 
                'rr_run_cycle': rr_run_cycle}
    
    except Exception as e:
        print_line_of_error(f'REVREC FAILED {e}')
        print(qcp)
        return None

