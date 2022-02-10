from cgitb import reset
import logging
from enum import Enum
import time
import alpaca_trade_api as tradeapi
import asyncio
import os
import pandas as pd
import pandas_ta as ta
import sys
from alpaca_trade_api.rest import TimeFrame, URL
from alpaca_trade_api.rest_async import gather_with_concurrency, AsyncRest
from dotenv import load_dotenv
import threading
load_dotenv()
logging.basicConfig(
    filename='hive_utils.log',
    level=logging.WARNING,
    format='%(asctime)s:%(levelname)s:%(message)s',
)

def return_api_keys(base_url, api_key_id, api_secret):

    api_key_id = os.environ.get('APCA_API_KEY_ID')
    api_secret = os.environ.get('APCA_API_SECRET_KEY')
    base_url = "https://api.alpaca.markets"
    feed = "iex"  # change to "sip" if you have a paid account

    rest = AsyncRest(key_id=api_key_id,
                        secret_key=api_secret)

    api = tradeapi.REST(key_id=api_key_id,
                        secret_key=api_secret,
                        base_url=URL(base_url), api_version='v2')
    return [{'rest': rest, 'api': api}]

keys = return_api_keys()

rest = keys['rest']
api = keys['api']

def wait_for_market_open():
	clock = api.get_clock()
	if not clock.is_open:
		time_to_open = (clock.next_open - clock.timestamp).total_seconds()
		time.sleep(round(time_to_open))


def time_to_market_close():
	clock = api.get_clock()
	return (clock.next_close - clock.timestamp).total_seconds()


# submit order
def submit_order(symbol, qty, side, type, limit_price, client_order_id, time_in_force, order_class=False, stop_loss=False, take_profit=False):
    
    # sell_x = api.submit_order(symbol='SPDN', 
    #         qty=1, 
    #         side='sell', 
    #         time_in_force='gtc', 
    #         type='limit', # market
    #         limit_price=14.90, 
    #         client_order_id='004') # optional make sure it unique though to call later!

    if type == 'market':
        order = api.submit_order(symbol=symbol,
        qty=qty,
        side=side,
        type=type,
        time_in_force=time_in_force)
    return order

    """stop loss order""" 
    # api.submit_order(symbol='TSLA', 
    #         qty=1, 
    #         side='buy', 
    #         time_in_force='gtc', 
    #         type='limit', 
    #         limit_price=400.00, 
    #         client_order_id=001, 
    #         order_class='bracket', 
    #         stop_loss=dict(stop_price='360.00'), 
	#         take_profit=dict(limit_price='440.00'))
    """Order Return"""
    # Out[14]: 
    # Order({   'asset_class': 'us_equity',
    #     'asset_id': 'b28f4066-5c6d-479b-a2af-85dc1a8f16fb',
    #     'canceled_at': None,
    #     'client_order_id': '001',
    #     'created_at': '2022-02-08T16:20:07.813040847Z',
    #     'expired_at': None,
    #     'extended_hours': False,
    #     'failed_at': None,
    #     'filled_at': None,
    #     'filled_avg_price': None,
    #     'filled_qty': '0',
    #     'hwm': None,
    #     'id': '5dbcb543-956b-4eec-b9b8-fc768d517da9',
    #     'legs': None,
    #     'limit_price': '449.2',
    #     'notional': None,
    #     'order_class': '',
    #     'order_type': 'limit',
    #     'qty': '1',
    #     'replaced_at': None,
    #     'replaced_by': None,
    #     'replaces': None,
    #     'side': 'buy',
    #     'status': 'accepted',
    #     'stop_price': None,
    #     'submitted_at': '2022-02-08T16:20:07.812422547Z',
    #     'symbol': 'SPY',
    #     'time_in_force': 'gtc',
    #     'trail_percent': None,
    #     'trail_price': None,
    #     'type': 'limit',
    #     'updated_at': '2022-02-08T16:20:07.813040847Z'})


    if 'name' == 'main':
        submit_order()


def return_account_info(api):
    info = api.get_account()
            # Account({   'account_blocked': False,
            #     'account_number': '603397580',
            #     'accrued_fees': '0',
            #     'buying_power': '80010',
            #     'cash': '40005',
            #     'created_at': '2022-01-23T22:11:15.978765Z',
            #     'crypto_status': 'PAPER_ONLY',
            #     'currency': 'USD',
            #     'daytrade_count': 0,
            #     'daytrading_buying_power': '0',
            #     'equity': '40005',
            #     'id': '2fae9699-b24f-4d06-80ec-d531b61e9458',
            #     'initial_margin': '0',
            #     'last_equity': '40005',
            #     'last_maintenance_margin': '0',
            #     'long_market_value': '0',
            #     'maintenance_margin': '0',
            #     'multiplier': '2',
            #     'non_marginable_buying_power': '40005',
            #     'pattern_day_trader': False,
            #     'pending_transfer_in': '40000',
            #     'portfolio_value': '40005',
            #     'regt_buying_power': '80010',
            #     'short_market_value': '0',
            #     'shorting_enabled': True,
            #     'sma': '40005',
            #     'status': 'ACTIVE',
            #     'trade_suspended_by_user': False,
            #     'trading_blocked': False,
            #     'transfers_blocked': False})
    return {'account_number': info.account_number,
            'accrued_fees': info.accrued_fees,
            'buying_power': info.buying_power,
            'cash': info.cash,
            'daytrade_count': info.daytrade_count,
            'last_equity': info.last_equity,
            'portfolio_value': info.portfolio_value,
            'sma': info.sma}


# Return order Status
def clientId_order_status(api, client_id_order):
    open_orders_list = api.list_orders(status='open')
    if client_id_order:
        order_token = api.get_order_by_client_order_id(client_id_order)
    else:
        order_token = False
    return [True, spdn_order, open_orders_list]