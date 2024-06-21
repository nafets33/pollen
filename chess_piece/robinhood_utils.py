import robin_stocks as rs
from dotenv import load_dotenv
import os

load_dotenv()


def login_robinhood():
    # Login to Robinhood
    username = os.environ.get('username_robinhood')
    password = os.environ.get('password_robinhood')
    login = rs.robinhood.login(username=username,password=password, mfa_code="otp")

    return login

def sell_order_robinhood(rs, symbol='AAPL', quantity=1, price=None):

    # Place the sell order
    order_response = rs.robinhood.orders.order_sell_market(symbol, quantity)

    print(order_response)

    return order_response

def submit_order_robinhood(rs, symbol='AAPL', quantity=1, price=None):
    # Place the buy order
    order_response = rs.robinhood.orders.order_buy_market(symbol, quantity)

    return order_response

def get_lib_keys_robinhood():
    g=vars(rs.robinhood).keys()

def get_portfolio_robinhood():
    # Get your portfolio data
    portfolio = rs.robinhood.account.build_holdings() # dictionary
    crypto_positions = rs.robinhood.crypto.get_crypto_positions() # list
    # quantity, quantity_available
    for crypt in crypto_positions:
        for k,v in crypt.items():
            print(k,v)

    # Print portfolio data
    for symbol, data in portfolio.items():
        print(f"Symbol: {symbol}")
        print(f"Quantity: {data['quantity']}")
        print(f"Avg Cost: {data['average_buy_price']}")
        print(f"Current Price: {data['price']}")
        print(f"Equity: {data['equity']}")
        print(f"--------------------------")


if '__name__' is '__main__':
    login_robinhood()
    get_portfolio_robinhood()
