import base64
import datetime
import json
from typing import Any, Dict, Optional
import uuid
import requests
from nacl.signing import SigningKey

from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.environ.get('pollen_rh')
BASE64_PRIVATE_KEY = os.environ.get('robinhood_crypto_private_key')

class CryptoAPITrading:
    def __init__(self):
        self.api_key = API_KEY
        private_key_seed = base64.b64decode(BASE64_PRIVATE_KEY)
        self.private_key = SigningKey(private_key_seed)
        self.base_url = "https://trading.robinhood.com"

    @staticmethod
    def _get_current_timestamp() -> int:
        return int(datetime.datetime.now(tz=datetime.timezone.utc).timestamp())

    @staticmethod
    def get_query_params(key: str, *args: Optional[str]) -> str:
        if not args:
            return ""

        params = []
        for arg in args:
            params.append(f"{key}={arg}")

        return "?" + "&".join(params)

    def make_api_request(self, method: str, path: str, body: str = "") -> Any:
        timestamp = self._get_current_timestamp()
        headers = self.get_authorization_header(method, path, body, timestamp)
        url = self.base_url + path

        try:
            response = {}
            if method == "GET":
                response = requests.get(url, headers=headers, timeout=10)
            elif method == "POST":
                response = requests.post(url, headers=headers, json=json.loads(body), timeout=10)
            return response.json()
        except requests.RequestException as e:
            print(f"Error making API request: {e}")
            return None

    def get_authorization_header(
            self, method: str, path: str, body: str, timestamp: int
    ) -> Dict[str, str]:
        message_to_sign = f"{self.api_key}{timestamp}{path}{method}{body}"
        signed = self.private_key.sign(message_to_sign.encode("utf-8"))

        return {
            "x-api-key": self.api_key,
            "x-signature": base64.b64encode(signed.signature).decode("utf-8"),
            "x-timestamp": str(timestamp),
        }

    def get_account(self) -> Any:
        path = "/api/v1/crypto/trading/accounts/"
        return self.make_api_request("GET", path)

    # The symbols argument must be formatted in trading pairs, e.g "BTC-USD", "ETH-USD". If no symbols are provided,
    # all supported symbols will be returned
    def get_trading_pairs(self, *symbols: Optional[str]) -> Any:
        query_params = self.get_query_params("symbol", *symbols)
        path = f"/api/v1/crypto/trading/trading_pairs/{query_params}"
        return self.make_api_request("GET", path)

    # The asset_codes argument must be formatted as the short form name for a crypto, e.g "BTC", "ETH". If no asset
    # codes are provided, all crypto holdings will be returned
    def get_holdings(self, *asset_codes: Optional[str]) -> Any:
        query_params = self.get_query_params("asset_code", *asset_codes)
        path = f"/api/v1/crypto/trading/holdings/{query_params}"
        return self.make_api_request("GET", path)

    # The symbols argument must be formatted in trading pairs, e.g "BTC-USD", "ETH-USD". If no symbols are provided,
    # the best bid and ask for all supported symbols will be returned
    def get_best_bid_ask(self, *symbols: Optional[str]) -> Any:
        query_params = self.get_query_params("symbol", *symbols)
        path = f"/api/v1/crypto/marketdata/best_bid_ask/{query_params}"
        return self.make_api_request("GET", path)

    # The symbol argument must be formatted in a trading pair, e.g "BTC-USD", "ETH-USD"
    # The side argument must be "bid", "ask", or "both".
    # Multiple quantities can be specified in the quantity argument, e.g. "0.1,1,1.999".
    def get_estimated_price(self, symbol: str, side: str, quantity: str) -> Any:
        path = f"/api/v1/crypto/marketdata/estimated_price/?symbol={symbol}&side={side}&quantity={quantity}"
        return self.make_api_request("GET", path)

    def place_order(
            self,
            client_order_id: str,
            side: str,
            order_type: str,
            symbol: str,
            order_config: Dict[str, str],
    ) -> Any:
        body = {
            "client_order_id": client_order_id,
            "side": side,
            "type": order_type,
            "symbol": symbol,
            f"{order_type}_order_config": order_config,
        }
        path = "/api/v1/crypto/trading/orders/"
        return self.make_api_request("POST", path, json.dumps(body))

    def place_limit_order(self, client_order_id: str, side: str, symbol: str, limit_price: str, quantity: str) -> Any:
        order_type = "limit"
        order_config = {
            "price": limit_price,
            "quantity": quantity,
            # Add any other necessary parameters for a limit order here
        }
        return self.place_order(client_order_id, side, order_type, symbol, order_config)

    def cancel_order(self, order_id: str) -> Any:
        path = f"/api/v1/crypto/trading/orders/{order_id}/cancel/"
        return self.make_api_request("POST", path)

    def get_order(self, order_id: str) -> Any:
        path = f"/api/v1/crypto/trading/orders/{order_id}/"
        return self.make_api_request("GET", path)

    def get_orders(self) -> Any:
        path = "/api/v1/crypto/trading/orders/"
        return self.make_api_request("GET", path)

    def get_order_fees(self, order_id: str) -> Any:
        path = f"/api/v1/crypto/trading/orders/{order_id}/"
        response = self.make_api_request("GET", path)
        # Assuming the response contains 'executions' with fee details
        executions = response.get('executions', [])
        total_fees = sum(exec.get('fee', 0) for exec in executions)
        return total_fees

    # def get_account_activity(self) -> Any:
    #     path = "/api/v1/crypto/trading/account/activity/"
    #     response = self.make_api_request("GET", path)
    #     # Assuming the response contains a list of activities with fees
    #     return response.get('activities', [])


def main():
    api_rh = CryptoAPITrading()
    print(api_rh.get_account(), api_rh.get_trading_pairs(), api_rh.get_holdings(),)
    symbol_info = api_rh.get_best_bid_ask('BTC-USD')
    wave_amo = 100000 / float(symbol_info.get('results')[0]['ask_inclusive_of_buy_spread'])

    # api_rh.get_order("67b37e02-ac37-434e-a2d4-b14cb89f74cc")

    # api_rh.get_account_activity()

    # In [10]: api_rh.get_holdings()
    # Out[10]: 
    # {'next': None,
    # 'previous': None,
    # 'results': [{'account_number': '311015558547',
    # 'asset_code': 'TRUMP',
    # 'total_quantity': '19.199800000000000000',
    # 'quantity_available_for_trading': '19.199800000000000000'},
    # {'account_number': '311015558547',
    # 'asset_code': 'SOL',
    # 'total_quantity': '19.451540000000000000',
    # 'quantity_available_for_trading': '19.451540000000000000'},
    # {'account_number': '311015558547',
    # 'asset_code': 'ETH',
    # 'total_quantity': '5.965706000000000000',
    # 'quantity_available_for_trading': '5.965706000000000000'},
    # {'account_number': '311015558547',
    # 'asset_code': 'BTC',
    # 'total_quantity': '0.643721170000000000',
    # 'quantity_available_for_trading': '0.643721170000000000'}]}

    # In [11]: api_rh.get_best_bid_ask('BTC-USD')
    # Out[11]: 
    # {'results': [{'symbol': 'BTC-USD',
    # 'timestamp': '2025-02-17T18:11:17.489975071Z',
    # 'price': '95455.49270237',
    # 'bid_inclusive_of_sell_spread': '94886.67342',
    # 'sell_spread': '0.005959',
    # 'ask_inclusive_of_buy_spread': '96024.31198474',
    # 'buy_spread': '0.005959'}]}
    
    
    """
    BUILD YOUR TRADING STRATEGY HERE

    order = api_rh.place_order(
          str(uuid.uuid4()),
          "buy",
          "market",
          "BTC-USD",
          {"asset_quantity": "0.0001"}
    )

    In [27]: order
    Out[27]: 
    {'symbol': 'BTC-USD',
    'client_order_id': '1b54ccdc-6946-45ef-81bf-6c9974951e63',
    'side': 'buy',
    'type': 'market',
    'id': '67b37e02-ac37-434e-a2d4-b14cb89f74cc',
    'account_number': '311015558547',
    'state': 'open',
    'filled_asset_quantity': '0.000000000000000000',
    'executions': [],
    'average_price': None,
    'created_at': '2025-02-17T13:20:50.234331-05:00',
    'updated_at': '2025-02-17T13:20:50.539851-05:00',
    'market_order_config': {'asset_quantity': '0.000100000000000000'}}

    """

    # api_rh.get_order("67b37e02-ac37-434e-a2d4-b14cb89f74cc")

    # api_rh.get_order_fees(order_id="67b37e02-ac37-434e-a2d4-b14cb89f74cc")


    """
    {'symbol': 'BTC-USD',
    'client_order_id': '1b54ccdc-6946-45ef-81bf-6c9974951e63',
    'side': 'buy',
    'type': 'market',
    'id': '67b37e02-ac37-434e-a2d4-b14cb89f74cc',
    'account_number': '311015558547',
    'state': 'filled',
    'filled_asset_quantity': '0.000100000000000000',
    'executions': [{'effective_price': '96328.270000000000000000',
    'quantity': '0.000100000000000000',
    'timestamp': '2025-02-17T13:20:50.565000-05:00'}],
    'average_price': '96328.270000000000000000',
    'created_at': '2025-02-17T13:20:50.234331-05:00',
    'updated_at': '2025-02-17T13:20:51.050895-05:00',
    'market_order_config': {'asset_quantity': '0.000100000000000000'}}
    """

    # In [5]: api_rh.get_order("67b37e02-ac37-434e-a2d4-b14cb8
    #    ...: 9f74cc")
    # Out[5]: 
    # {'symbol': 'BTC-USD',
    #  'client_order_id': '1b54ccdc-6946-45ef-81bf-6c9974951e63',
    #  'side': 'buy',
    #  'type': 'market',
    #  'id': '67b37e02-ac37-434e-a2d4-b14cb89f74cc',
    #  'account_number': '311015558547',
    #  'state': 'filled',
    #  'filled_asset_quantity': '0.000100000000000000',
    #  'executions': [{'effective_price': '96328.270000000000000000',
    #    'quantity': '0.000100000000000000',
    #    'timestamp': '2025-02-17T13:20:50.565000-05:00'}],
    #  'average_price': '96328.270000000000000000',
    #  'created_at': '2025-02-17T13:20:50.234331-05:00',
    #  'updated_at': '2025-02-17T13:20:51.050895-05:00',
    #  'market_order_config': {'asset_quantity': '0.000100000000000000'}}

    def broker_orders_fields() -> list:
        return ['id', 'client_order_id', 'symbol', 'side', 'type', 'qty', 'filled_qty', 'filled_avg_price', 'status', 'created_at', 'updated_at']

    def convert_robinhood_crypto_order_fields(order) -> Dict[str, Any]:
        return {
            'id': order.get('id'),
            'client_order_id': order.get('client_order_id'),
            'symbol': order.get('symbol'),
            'side': order.get('side'),
            'type': order.get('type'),
            'qty': order.get('market_order_config', {}).get('asset_quantity', ''),
            'filled_qty': order.get('filled_asset_quantity', 0),
            'filled_avg_price': order.get('average_price', 0),
            'status': order.get('state'),
            'created_at': order.get('created_at'),
            'updated_at': order.get('updated_at')
        }

if __name__ == "__main__":
    main()