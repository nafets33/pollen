from datetime import datetime
import pandas as pd
import logging
import requests
import os
from dotenv import load_dotenv
import ipdb

load_dotenv()

### """ TRIGGER RULES"""

def trig_rule_ID(symbol, trigrule_type, ttf):
    return f"{symbol}_{trigrule_type}_{ttf}"

def trigrule_name_ui_backend(trigrule=None):

    keys = {'trinity': "trinity_w_L",
            'trinity_15': "trinity_w_15",
            'trinity_30': "trinity_w_30",
            'trinity_54': "trinity_w_54",
            'vwap': "vwap",
            'rsi': "rsi",
            'macd': "macd"}

    if trigrule:
        return keys[trigrule]
    return keys

def create_TrigRule(
                    symbol='SPY',
                    save_to_db=False,
                    trigrule_type='wave_trinity', # trading_pairs
                    trigrule_status='not_active', # active, not_active
                    ttf='1Minute_1Day', # anchor time frame
                    expire_date=datetime.now().strftime('%m/%d/%YT%H:%M'), 
                    user_accept=True, 
                    max_order_nums=1, # to achieve max budget
                    wave_amo=89, 
                    marker='trinity', # vwap, rsi, macd, trinity..
                    marker_value=None, # -.2
                    marker_direction=['below'], # 'below', 'above'
                    deviation_symbols=[], # list of symbols to compare against
                    deviation_group=[], # compare on group std deviation
                    block_times=[], # trigging active when in block time
                    take_profit=.01,
                    sell_out=0.0,
                    sell_trigbee_date=datetime.now().strftime('%m/%d/%YT%H:%M'),
                    trigger_id=None
                    ):
    # all_vars = {key: value for key, value in globals().items() if not key.startswith("__") and not callable(value)}
    return {
        "symbol": symbol,
        "save_to_db": save_to_db,
        "trigrule_type": trigrule_type,
        "trigrule_status": trigrule_status,
        "expire_date": expire_date,
        "user_accept": user_accept,
        "wave_amo": wave_amo,
        "marker": marker,
        "marker_value": marker_value,
        "marker_direction": marker_direction,
        "ttf": ttf,
        "block_times": block_times,
        "deviation_symbols": deviation_symbols,
        "deviation_group": deviation_group,
        "max_order_nums": max_order_nums,
        "take_profit": take_profit,
        "sell_out": sell_out,
        "sell_trigbee_date": sell_trigbee_date,
        "trigger_id": trigger_id,
    }

def create_trig_rule_metadata(symbols, qcp_s, star_list):
    # Define the keys and their metadata
    trig_rule_keys = {
        "save_to_db": {
            "display_name": "Save Buy Trigger",
            "col_header": "save_to_db",
            "dtype": "checkbox",
            "values": [True, False],
            "pinned": True,  # ✅ Pin this column
            "backgroundColor": "#e8f5e9",  # ✅ Light green background
        },
        "ttf": {
            "display_name": "Ticker Model Time",
            "col_header": "ttf",
            "dtype": "list",
            "values": star_list,
            "pinned": True,  # ✅ Pin this column
        },
        "trigrule_type": {
            "display_name": "Trigger Rule Type",
            "col_header": "trigrule_type",
            "dtype": "list",
            "values": ["wave_trinity", "trading_pairs"]
        },
        "trigrule_status": {
            "display_name": "Trigger Rule Status",
            "col_header": "trigrule_status",
            "dtype": "list",
            "values": ["active", "not_active", "trig_running", "expired"],
            "conditionalColor": {  # ✅ Color based on status
                "type": "threshold",
                "field": "trigrule_status",
                "operator": "==",
                "value": "active",
                "trueColor": "#c8e6c9",  # Green when active
                "falseColor": "#ffcdd2"  # Red when not active
            }
        },
        "expire_date": {
            "display_name": "Trigger Expiration Date",
            "col_header": "expire_date",
            "dtype": "datetime",
            "values": []
        },
        "user_accept": {
            "display_name": "User Acceptance",
            "col_header": "user_accept",
            "dtype": "checkbox",
            "values": [True, False]
        },
        "wave_amo": {
            "display_name": "Buy Amount",
            "col_header": "wave_amo",
            "dtype": "float",
            "values": [50.0, 100.0, 500.0],
            "conditionalColor": {  # ✅ Color based on amount threshold
                "type": "threshold",
                "field": "wave_amo",
                "operator": ">",
                "value": 100,
                "trueColor": "#fff9c4",  # Yellow when > 100
                "falseColor": "white"
            }
        },
        "marker": {
            "display_name": "Marker",
            "col_header": "marker",
            "dtype": "list",
            "values": ["trinity", "trinity_15", "trinity_30", "trinity_54", "vwap", "rsi", "macd"]
        },
        "marker_direction": {
            "display_name": "Marker Direction",
            "col_header": "marker_direction",
            "dtype": "list",
            "values": ["below", "above"]
        },
        "marker_value": {
            "display_name": "Marker Value",
            "col_header": "marker_value",
            "dtype": "float",
            "values": [-0.5, 0.0, 0.5, 1.0]
        },
        "deviation_symbols": {
            "display_name": "Deviation Symbol",
            "col_header": "deviation_symbols",
            "dtype": "list",
            "values": symbols
        },
        "deviation_group": {
            "display_name": "Deviation From Budget Group",
            "col_header": "deviation_group",
            "dtype": "list",
            "values": qcp_s
        },
        "block_times": {
            "display_name": "Block Times",
            "col_header": "block_times",
            "dtype": "list",
            "values": ["morning_9-11", "lunch_11-2", "afternoon_2-4"]
        },
        "take_profit": {
            "display_name": "Take Profit",
            "col_header": "take_profit",
            "dtype": "float",
            "backgroundColor": "#e8f5e9",  # ✅ Light green for profit targets
            "conditionalColor": {  # ✅ Color based on profit level
                "type": "threshold",
                "field": "take_profit",
                "operator": ">",
                "value": 0.02,  # More than 2%
                "trueColor": "#c8e6c9",  # Darker green
                "falseColor": "#fff9c4"  # Yellow for lower targets
            }
        },
        "sell_out": {
            "display_name": "Sell Out",
            "col_header": "sell_out",
            "dtype": "float",
            "backgroundColor": "#ffebee",  # ✅ Light red for stop loss
        },
        "sell_trigbee_date": {
            "display_name": "Auto Pilot Sell on Sell Signal",
            "col_header": "sell_trigbee_date",
            "dtype": "datetime",
        },
        "max_order_nums": {
            "display_name": "Max Num of Active Triggers",
            "col_header": "max_order_nums",
            "dtype": "int",
        },
    }

    return trig_rule_keys


def get_existing_trigrule_orders(symbols, active_orders):
    """
    Get all existing orders that have trigger_ids for symbols in storygauge.
    Returns DataFrame of existing orders with their trigger_ids.
    """
    try:
        if len(active_orders) == 0:
            return pd.DataFrame()
        
        # Filter active orders for symbols in storygauge with active states
        existing_orders = active_orders[
            (active_orders['symbol'].isin(symbols))
        ].copy()
        
        if len(existing_orders) == 0:
            return pd.DataFrame()
        
        # Extract trigger_id from order_rules
        def extract_trigger_id(row):
            order_rules = row.get('order_rules')
            if isinstance(order_rules, dict):
                return order_rules.get('trigger_id')
            return None
        
        existing_orders['trigger_id'] = existing_orders.apply(extract_trigger_id, axis=1)
        
        # Filter out orders without trigger_ids
        existing_orders = existing_orders[existing_orders['trigger_id'].notna()].copy()
        
        # logging.info(f"[TRIGRULE DEBUG] Found {len(existing_orders)} existing orders with trigger_ids")
        
        return existing_orders[['symbol', 'trigger_id', 'queen_order_state', 'order_rules', 'cost_basis_current', 'filled_qty', 'qty_available', 'money', 'honey']]
    
    except Exception as e:
        print(f"❌ Error getting existing trigrule orders: {e}")
        return pd.DataFrame()

def check_trigrule_conditions(symbol, storygauge, QUEEN_KING, existing_orders_df, API_URL=None):
    """
    Check if TrigRule conditions are met for a symbol.
    Returns first passing TrigRule dict with trigger_id, or None if none pass.
    """
    if API_URL is None:
        API_URL = os.getenv('fastAPI_url')
    try:
        ticker_trigrules = QUEEN_KING['king_controls_queen'].get('ticker_trigrules', [])
        # TEST: Create test TrigRule for this symbol (only once)
        # ticker_trigrules.append(create_TrigRule(trigrule_status='active', marker_value=-.02, marker_direction='below')) # TESTING ONLY
        # ticker_trigrules.append(create_TrigRule(trigrule_type='trading_pairs', trigrule_status='active', marker_value=-.02, marker_direction='below', deviation_symbols='SPY', deviation_group=False)) # TESTING ONLY
        df_trigrules = pd.DataFrame(ticker_trigrules) if isinstance(ticker_trigrules, list) else ticker_trigrules
        
        if len(df_trigrules) == 0:
            return None

        # Filter for active rules for this symbol
        symbol_rules = df_trigrules[(df_trigrules['symbol'] == symbol) & (df_trigrules['trigrule_status'] == 'active')].copy()

        if len(symbol_rules) == 0:
            return None

        # Get trinity_w_L for the symbol
        if symbol not in storygauge.index:
            return None

        # Get existing trigger_ids for this symbol (pre-filtered)
        existing_trigger_ids = set()
        if len(existing_orders_df) > 0:
            symbol_existing_orders = existing_orders_df[existing_orders_df['symbol'] == symbol]
            existing_trigger_ids = set(symbol_existing_orders['trigger_id'].tolist())
        

        # Check each rule - return first one that passes
        for idx, rule in symbol_rules.iterrows():
            marker = rule.get('marker', 'trinity').lower()
            marker_backend_name = trigrule_name_ui_backend(marker)
            story_field_value = float(storygauge.loc[symbol].get(marker_backend_name))
            trigrule_type = rule.get('trigrule_type')
            ttf = rule.get('ttf')
            marker_value = float(rule.get('marker_value'))
            if pd.isna(marker_value):
                logging.info(f"[TRIGRULE DEBUG] Rule {symbol} {ttf} skipped: marker_value is NaN")
                continue
            if abs(marker_value) > 1:
                marker_value = marker_value / 100.0  # convert percentage to decimal

            # Check if this trigger_id already has an order (max_order_nums = 1)
            trigger_id = trig_rule_ID(symbol, trigrule_type, ttf) # trigger_id = f"{symbol}_{rule.get('trigrule_type')}_{rule.get('ttf')}"
            if trigger_id in existing_trigger_ids:
                logging.info(f"[TRIGRULE DEBUG] Rule {symbol} {ttf} skipped: existing order found with trigger_id: {trigger_id}")
                continue

            expire_date = rule.get('expire_date', None)
            if expire_date:
                try:
                    expire_datetime = pd.to_datetime(expire_date)
                    # Check if conversion resulted in NaT
                    if pd.isna(expire_datetime):
                        logging.error(f"[TRIGRULE DEBUG] Rule {symbol} {ttf}: expire_date is invalid (NaT): {expire_date}")
                        continue
                    # Make timezone-naive for comparison if needed
                    if expire_datetime.tzinfo is not None:
                        expire_datetime = expire_datetime.replace(tzinfo=None)
                    # Now safe to compare
                    if datetime.now() > expire_datetime:
                        logging.info(f"[TRIGRULE DEBUG] Rule {symbol} {ttf} skipped: expired on {expire_datetime}")
                        flip_queen_trigger_rule_status(API_URL, trigger_id, client_user=QUEEN_KING['client_user'], prod=QUEEN_KING['prod'], status='expired')
                        continue
                except Exception as e:
                    logging.error(f"[TRIGRULE DEBUG] Rule {symbol} {ttf}: Failed to parse expire_date '{expire_date}': {e}")
                    continue

            # Check wave_trinity type
            marker_direction = rule['marker_direction']  # default to 'above' if not specified
            if isinstance(marker_direction, list):
                marker_direction = marker_direction[0]
            
            # Check Trinity Rule
            if trigrule_type == 'wave_trinity':
                # Compare trinity_w_L against marker_value
                if marker_value is not None:
                    if marker_direction == 'below':
                        condition_met = story_field_value <= marker_value
                    else:
                        condition_met = story_field_value >= marker_value

                    if condition_met:
                        logging.info(f"[TRIGRULE DEBUG] TrigRule PASSED for {symbol}! trigger_id: {trigger_id} ::: marker_direction {marker_direction} Marker Value {marker_value} VS Trinity Value {story_field_value} ")
                        rule_dict = rule.to_dict()
                        rule_dict['trigger_id'] = trigger_id
                        return rule_dict
                    else:
                        logging.info(f"[TRIGRULE DEBUG] TrigRule NOT PASSED for {symbol} (condition not met)")

            # Check trading_pairs Rule
            elif trigrule_type == 'trading_pairs':  # WORKERBEE NEED TO REDO THIS LOGIC
                deviation_symbols = rule.get('deviation_symbols', [])
                if not deviation_symbols or len(deviation_symbols) == 0:
                    continue

                # Calculate deviation for each deviation symbol
                for dev_symbol in deviation_symbols:
                    if dev_symbol not in storygauge.index:
                        continue

                    dev_story_field_value = float(storygauge.loc[dev_symbol].get(marker_backend_name))
                    if pd.isna(dev_story_field_value) or dev_story_field_value == 0:
                        continue

                    # Calculate deviation
                    deviation = (story_field_value - dev_story_field_value) / dev_story_field_value

                    # Compare deviation against marker_value
                    if marker_value is not None:
                        if marker_direction == 'below':
                            condition_met = deviation <= marker_value
                            print(f"[TRIGRULE DEBUG] wave_trinity check: {deviation} <= {marker_value} = {condition_met}")
                        else:
                            condition_met = deviation >= marker_value
                            print(f"[TRIGRULE DEBUG] wave_trinity check: {deviation} >= {marker_value} = {condition_met}")

                        if condition_met:
                            rule_dict = rule.to_dict()
                            rule_dict['trigger_id'] = trigger_id
                            return rule_dict

        return None

    except Exception as e:
        print(f"Error checking TrigRule conditions for {symbol}: {e}")
        return None

def flip_queen_trigger_rule_status(API_URL, trigger_id, client_user, prod, status):
    # call to update QUEEN_KING
    payload = {
                'api_key': os.getenv('fastAPI_key'),
                'client_user': client_user,
                'trigger_id': trigger_id,
                'prod':prod,
                'status': status
                }
    try:
        # Determine API URL
        endpoint = f"{API_URL}/api/data/queen_queenking_trigrule_event"
        
        # Send POST request to update trigger
        response = requests.post(
            endpoint,
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            logging.info(f"Trigger {trigger_id} status updated successfully")
            print(f"Trigger {trigger_id} updated: {result.get('description')}")
            return result
        else:
            logging.error(f"❌ Failed to update trigger {trigger_id}: {response.status_code}")
            print(f"❌ Failed to update trigger: {response.text}")
            return {'error': response.text}
            
    except requests.exceptions.Timeout:
        logging.error(f"⏱️ Timeout updating trigger {trigger_id}")
        return {'error': 'Timeout occurred'}
    except requests.exceptions.ConnectionError:
        logging.error(f"❌ Connection error updating trigger {trigger_id}")
        return {'error': 'Connection error occurred'}
    except Exception as e:
        logging.error(f"❌ Error updating trigger {trigger_id}: {e}")
        return {'error': str(e)}

### """ TRIGGER RULES""" ###