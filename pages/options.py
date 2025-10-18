import pandas as pd
import numpy as np
import streamlit as st
import yfinance as yf
from datetime import datetime, timedelta
import pytz
import os
from dotenv import load_dotenv
import alpaca_trade_api as tradeapi
from chess_piece.queen_hive import init_queenbee, refresh_account_info
from chess_piece.pollen_db import PollenDatabase
from chess_piece.king import hive_master_root
from pq_auth import signin_main
import logging

# Set page config FIRST - before any other Streamlit commands
st.set_page_config(
    page_title="Options Trading",
    page_icon="📈",
    layout="wide"
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
main_root = hive_master_root()
load_dotenv(os.path.join(main_root, ".env"))

# Set pandas options
pd.options.mode.chained_assignment = None

# Timezone setup
est = pytz.timezone("US/Eastern")

# -----------------------
# Options utils (Greeks, OCC symbol)
# -----------------------

def _norm_cdf(x: float) -> float:
    return 0.5 * (1.0 + np.math.erf(x / np.sqrt(2)))

def _norm_pdf(x: float) -> float:
    return (1.0 / np.sqrt(2 * np.pi)) * np.exp(-0.5 * x * x)

def compute_black_scholes_greeks(spot_price: float, strike_price: float, time_years: float, risk_free_rate: float, implied_vol: float, option_type: str) -> dict:
    if spot_price <= 0 or strike_price <= 0 or time_years <= 0 or implied_vol <= 0:
        return {"delta": np.nan, "gamma": np.nan, "theta": np.nan, "vega": np.nan}
    sigma = implied_vol
    r = risk_free_rate
    S = spot_price
    K = strike_price
    T = time_years
    d1 = (np.log(S / K) + (r + 0.5 * sigma * sigma) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    if option_type.lower() == "call":
        delta = _norm_cdf(d1)
        theta = (-(S * _norm_pdf(d1) * sigma) / (2 * np.sqrt(T)) - r * K * np.exp(-r * T) * _norm_cdf(d2)) / 365
    else:
        delta = _norm_cdf(d1) - 1
        theta = (-(S * _norm_pdf(d1) * sigma) / (2 * np.sqrt(T)) + r * K * np.exp(-r * T) * _norm_cdf(-d2)) / 365
    gamma = _norm_pdf(d1) / (S * sigma * np.sqrt(T))
    vega = (S * _norm_pdf(d1) * np.sqrt(T)) / 100
    return {"delta": float(delta), "gamma": float(gamma), "theta": float(theta), "vega": float(vega)}

def construct_occ_symbol(underlying: str, expiration_yyyy_mm_dd: str, strike: float, option_type: str) -> str:
    # OCC: Underlying 6 chars (left-justified, space-padded), YYMMDD, C/P, strike (8 digits, 3 decimals implied)
    und = (underlying[:6]).ljust(6)
    y, m, d = expiration_yyyy_mm_dd.split("-")
    yy = y[2:]
    cp = 'C' if option_type.lower().startswith('c') else 'P'
    strike_scaled = int(round(strike * 1000))
    strike_str = f"{strike_scaled:08d}"
    return f"{und}{yy}{m}{d}{cp}{strike_str}"

# Check authentication
if 'authorized_user' not in st.session_state:
    signin_main("options")

if st.session_state["authorized_user"] != True:
    st.error("You do not have permissions to access this page")
    st.stop()

def get_alpaca_api():
    """Initialize and return Alpaca API connection"""
    try:
        api_key = os.getenv('ALPACA_API_KEY')
        api_secret = os.getenv('ALPACA_SECRET_KEY')
        base_url = os.getenv('ALPACA_BASE_URL', 'https://paper-api.alpaca.markets')
        
        if not api_key or not api_secret:
            st.error("Alpaca API credentials not found. Please check your environment variables.")
            return None
            
        api = tradeapi.REST(api_key, api_secret, base_url, api_version='v2')
        return api
    except Exception as e:
        st.error(f"Failed to initialize Alpaca API: {e}")
        return None

def fetch_options_chain(ticker, expiration_date=None):
    """Fetch options chain for a given ticker"""
    try:
        stock = yf.Ticker(ticker)
        
        # Get options expiration dates
        expirations = stock.options
        if not expirations:
            st.warning(f"No options data available for {ticker}")
            return None, None
            
        # Use provided expiration or the first available
        if expiration_date is None:
            expiration_date = expirations[0]
        elif expiration_date not in expirations:
            st.warning(f"Expiration date {expiration_date} not available. Using {expirations[0]}")
            expiration_date = expirations[0]
            
        # Get options chain
        options_chain = stock.option_chain(expiration_date)
        
        return options_chain, expiration_date
    except Exception as e:
        st.error(f"Error fetching options chain for {ticker}: {e}")
        return None, None

def filter_options_by_timeframe(options_chain, timeframe):
    """Filter options by timeframe (1D, 5D, 1M, 3M, 6M, 1Y)"""
    if not options_chain:
        return None, None
        
    calls = options_chain.calls
    puts = options_chain.puts
    
    # Calculate days to expiration
    current_date = datetime.now(est).date()
    expiration_date = pd.to_datetime(options_chain.calls['expiration'].iloc[0]).date()
    days_to_exp = (expiration_date - current_date).days
    
    # Filter based on timeframe
    timeframe_days = {
        '1D': 1,
        '5D': 5,
        '1M': 30,
        '3M': 90,
        '6M': 180,
        '1Y': 365
    }
    
    target_days = timeframe_days.get(timeframe, 30)
    
    # For now, return all options (in a real implementation, you'd filter by expiration)
    return calls, puts

def generate_option_suggestions(calls, puts, current_price, strategy_type="call", expiration_date: str = None, risk_free_rate: float = 0.02):
    """Generate simple option suggestions based on current price and strategy"""
    suggestions = []
    
    if strategy_type == "call":
        # Find calls near the money
        near_money_calls = calls[
            (calls['strike'] >= current_price * 0.95) & 
            (calls['strike'] <= current_price * 1.05)
        ].head(5)
        
        for _, option in near_money_calls.iterrows():
            iv = float(option.get('impliedVolatility', np.nan))
            greeks = compute_black_scholes_greeks(
                spot_price=float(current_price),
                strike_price=float(option['strike']),
                time_years=max(1/365, (pd.to_datetime(expiration_date) - datetime.now(est)).days / 365.0) if expiration_date else 30/365,
                risk_free_rate=risk_free_rate,
                implied_vol=float(iv) if iv < 10 else iv/100.0,
                option_type="call",
            )
            suggestions.append({
                'type': 'Call',
                'strike': option['strike'],
                'bid': option['bid'],
                'ask': option['ask'],
                'volume': option['volume'],
                'open_interest': option['openInterest'],
                'implied_volatility': option['impliedVolatility'],
                **greeks
            })
    
    elif strategy_type == "put":
        # Find puts near the money
        near_money_puts = puts[
            (puts['strike'] >= current_price * 0.95) & 
            (puts['strike'] <= current_price * 1.05)
        ].head(5)
        
        for _, option in near_money_puts.iterrows():
            iv = float(option.get('impliedVolatility', np.nan))
            greeks = compute_black_scholes_greeks(
                spot_price=float(current_price),
                strike_price=float(option['strike']),
                time_years=max(1/365, (pd.to_datetime(expiration_date) - datetime.now(est)).days / 365.0) if expiration_date else 30/365,
                risk_free_rate=risk_free_rate,
                implied_vol=float(iv) if iv < 10 else iv/100.0,
                option_type="put",
            )
            suggestions.append({
                'type': 'Put',
                'strike': option['strike'],
                'bid': option['bid'],
                'ask': option['ask'],
                'volume': option['volume'],
                'open_interest': option['openInterest'],
                'implied_volatility': option['impliedVolatility'],
                **greeks
            })
    
    return suggestions

def place_option_order(api, symbol, option_symbol, quantity, side, order_type="market", limit_price=None):
    """Place an options order through Alpaca API"""
    try:
        if order_type == "market":
            order = api.submit_order(
                symbol=option_symbol,
                qty=quantity,
                side=side,
                type="market",
                time_in_force="gtc"
            )
        elif order_type == "limit":
            if not limit_price:
                st.error("Limit price required for limit orders")
                return None
            order = api.submit_order(
                symbol=option_symbol,
                qty=quantity,
                side=side,
                type="limit",
                time_in_force="gtc",
                limit_price=limit_price
            )
        
        return order
    except Exception as e:
        st.error(f"Error placing order: {e}")
        return None

def save_option_order(order_data, client_user, prod=False):
    """Save option order to database using existing PollenDatabase framework"""
    try:
        # Create a comprehensive order record
        order_record = {
            'order_id': order_data.get('id'),
            'symbol': order_data.get('symbol'),
            'side': order_data.get('side'),
            'quantity': order_data.get('qty'),
            'order_type': order_data.get('order_type'),
            'status': order_data.get('status'),
            'created_at': datetime.now(est).isoformat(),
            'client_order_id': order_data.get('client_order_id'),
            'client_user': client_user,
            'prod': prod,
            'order_class': 'option',
            'asset_class': 'option'
        }
        
        # Use existing PollenDatabase framework
        table_name = 'option_orders' if prod else 'option_orders_sandbox'
        
        # Create table if it doesn't exist
        PollenDatabase.create_table_if_not_exists(table_name)
        
        # Save the order
        PollenDatabase.upsert_data(table_name, order_data.get('id'), order_record)
        
        logger.info(f"Option order saved: {order_record}")
        return True
    except Exception as e:
        logger.error(f"Error saving option order: {e}")
        return False

def get_option_orders(client_user, prod=False):
    """Retrieve option orders from database"""
    try:
        table_name = 'option_orders' if prod else 'option_orders_sandbox'
        
        # This is a simplified retrieval - in practice you'd want more sophisticated querying
        # For now, we'll return the session state orders
        return st.session_state.get('option_orders', [])
    except Exception as e:
        logger.error(f"Error retrieving option orders: {e}")
        return []

def fetch_positions(api):
    """Fetch open option positions from Alpaca"""
    try:
        positions = api.list_positions()
        option_positions = [p for p in positions if p.asset_class == 'option']
        return option_positions
    except Exception as e:
        logger.error(f"Error fetching positions: {e}")
        return []

def cancel_order(api, order_id):
    """Cancel an order by ID"""
    try:
        api.cancel_order(order_id)
        return True
    except Exception as e:
        logger.error(f"Error canceling order {order_id}: {e}")
        return False

def get_order_status(api, order_id):
    """Get order status by ID"""
    try:
        order = api.get_order(order_id)
        return {
            'id': order.id,
            'status': order.status,
            'side': order.side,
            'symbol': order.symbol,
            'qty': order.qty,
            'filled_qty': order.filled_qty,
            'filled_avg_price': order.filled_avg_price,
            'created_at': order.created_at,
            'updated_at': order.updated_at
        }
    except Exception as e:
        logger.error(f"Error getting order status {order_id}: {e}")
        return None

def check_risk_limits(api, order_side, quantity, limit_price=None, current_price=None):
    """Basic risk checks for option orders"""
    try:
        account = refresh_account_info(api=api)
        buying_power = float(account.get('info_converted', {}).get('buying_power', 0))
        cash = float(account.get('info_converted', {}).get('cash', 0))
        
        # Estimate order value
        if limit_price:
            order_value = limit_price * quantity * 100  # Options are 100 shares per contract
        elif current_price:
            order_value = current_price * quantity * 100
        else:
            order_value = 0
        
        # Basic checks
        if order_side == 'buy' and order_value > buying_power:
            return False, f"Order value ${order_value:,.2f} exceeds buying power ${buying_power:,.2f}"
        
        if order_side == 'sell' and order_value > cash:
            return False, f"Order value ${order_value:,.2f} exceeds cash ${cash:,.2f}"
        
        # Max order size check
        max_order_value = min(buying_power * 0.1, 10000)  # 10% of buying power or $10k max
        if order_value > max_order_value:
            return False, f"Order value ${order_value:,.2f} exceeds max allowed ${max_order_value:,.2f}"
        
        return True, "Risk checks passed"
    except Exception as e:
        logger.error(f"Error in risk checks: {e}")
        return False, f"Risk check error: {e}"

def main():
    
    st.title("📈 Options Trading Dashboard")
    st.markdown("---")
    
    # Get user and environment info
    client_user = st.session_state.get('username', 'unknown')
    prod = st.session_state.get('prod', False)
    
    # Display environment info
    env_text = "Live Account" if prod else "Sandbox Account"
    st.info(f"Environment: {env_text} | User: {client_user}")
    
    # Initialize session state
    if 'option_orders' not in st.session_state:
        st.session_state['option_orders'] = []
    
    # Initialize queen bee for API access
    try:
        qb = init_queenbee(client_user=client_user, prod=prod, queen_king=True, api=True, init=True)
        api = qb.get('api')
        QUEEN_KING = qb.get('QUEEN_KING')
        
        if not api:
            st.error("Failed to initialize API connection. Please check your credentials.")
            st.stop()
            
        # Display account info
        with st.expander("Account Information", expanded=False):
            try:
                account_info = refresh_account_info(api=api)
                if account_info:
                    # Debug: show what we received
                    st.write("Debug - Account info keys:", list(account_info.keys()) if isinstance(account_info, dict) else "Not a dict")
                    
                    # Use the converted info which has proper numeric formatting
                    converted_info = account_info.get('info_converted', {})
                    if converted_info:
                        st.json(converted_info)
                    else:
                        # Fallback: display basic account info in a readable format
                        raw_info = account_info.get('info', {})
                        if hasattr(raw_info, '__dict__'):
                            # Extract basic info from the account object
                            basic_info = {
                                'account_number': getattr(raw_info, 'account_number', 'N/A'),
                                'status': getattr(raw_info, 'status', 'N/A'),
                                'currency': getattr(raw_info, 'currency', 'N/A'),
                                'buying_power': getattr(raw_info, 'buying_power', 'N/A'),
                                'cash': getattr(raw_info, 'cash', 'N/A'),
                                'portfolio_value': getattr(raw_info, 'portfolio_value', 'N/A')
                            }
                            st.json(basic_info)
                        else:
                            st.warning("Account info format not recognized")
                else:
                    st.warning("No account information received")
            except Exception as e:
                st.warning(f"Could not fetch account info: {e}")
                st.write("Full error:", str(e))
                
    except Exception as e:
        st.error(f"Failed to initialize trading environment: {e}")
        st.stop()
    
    # Sidebar for input parameters
    with st.sidebar:
        st.header("Options Parameters")
        
        # Ticker input
        ticker = st.text_input("Enter Ticker Symbol", value="AAPL", help="Enter the stock symbol (e.g., AAPL, TSLA)")
        
        # Timeframe selection
        timeframe = st.selectbox(
            "Select Timeframe",
            options=["1D", "5D", "1M", "3M", "6M", "1Y"],
            index=2,  # Default to 1M
            help="Filter options by expiration timeframe"
        )
        
        # Strategy type
        strategy_type = st.selectbox(
            "Strategy Type",
            options=["call", "put"],
            help="Choose between call or put options"
        )
        
        # Fetch options button
        fetch_options = st.button("Fetch Options Chain", type="primary")
    
    # Main content area
    if fetch_options and ticker:
        with st.spinner(f"Fetching options data for {ticker}..."):
            # Get current stock price
            try:
                stock = yf.Ticker(ticker)
                current_price = stock.history(period="1d")['Close'].iloc[-1]
                st.success(f"Current {ticker} price: ${current_price:.2f}")
            except Exception as e:
                st.error(f"Could not fetch current price for {ticker}: {e}")
                current_price = None
            
            # Fetch options chain
            options_chain, expiration_date = fetch_options_chain(ticker)
            
            if options_chain:
                st.success(f"Options chain loaded for expiration: {expiration_date}")
                
                # Filter options by timeframe
                calls, puts = filter_options_by_timeframe(options_chain, timeframe)
                
                if calls is not None and puts is not None:
                    # Display options data
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader("📞 Call Options")
                        if not calls.empty:
                            # Enrich with Greeks (approx)
                            T_years = max(1/365, (pd.to_datetime(expiration_date) - datetime.now(est)).days / 365.0)
                            def _add_call_greeks(row):
                                g = compute_black_scholes_greeks(
                                    spot_price=float(current_price),
                                    strike_price=float(row['strike']),
                                    time_years=T_years,
                                    risk_free_rate=0.02,
                                    implied_vol=float(row['impliedVolatility']) if row['impliedVolatility'] < 10 else row['impliedVolatility']/100.0,
                                    option_type='call'
                                )
                                return pd.Series(g)
                            calls_enriched = calls.copy()
                            try:
                                calls_enriched[['delta','gamma','theta','vega']] = calls_enriched.apply(_add_call_greeks, axis=1)
                            except Exception:
                                pass
                            display_calls = calls_enriched[['strike', 'bid', 'ask', 'volume', 'openInterest', 'impliedVolatility', 'delta','gamma','theta','vega']].head(10)
                            st.dataframe(display_calls, use_container_width=True)
                        else:
                            st.info("No call options available")
                    
                    with col2:
                        st.subheader("📉 Put Options")
                        if not puts.empty:
                            # Enrich with Greeks (approx)
                            T_years = max(1/365, (pd.to_datetime(expiration_date) - datetime.now(est)).days / 365.0)
                            def _add_put_greeks(row):
                                g = compute_black_scholes_greeks(
                                    spot_price=float(current_price),
                                    strike_price=float(row['strike']),
                                    time_years=T_years,
                                    risk_free_rate=0.02,
                                    implied_vol=float(row['impliedVolatility']) if row['impliedVolatility'] < 10 else row['impliedVolatility']/100.0,
                                    option_type='put'
                                )
                                return pd.Series(g)
                            puts_enriched = puts.copy()
                            try:
                                puts_enriched[['delta','gamma','theta','vega']] = puts_enriched.apply(_add_put_greeks, axis=1)
                            except Exception:
                                pass
                            display_puts = puts_enriched[['strike', 'bid', 'ask', 'volume', 'openInterest', 'impliedVolatility', 'delta','gamma','theta','vega']].head(10)
                            st.dataframe(display_puts, use_container_width=True)
                        else:
                            st.info("No put options available")
                    
                    # Generate suggestions
                    if current_price:
                        st.subheader("💡 Option Suggestions")
                        suggestions = generate_option_suggestions(calls, puts, current_price, strategy_type, expiration_date)
                        
                        if suggestions:
                            suggestions_df = pd.DataFrame(suggestions)
                            st.dataframe(suggestions_df, use_container_width=True)
                            
                            # Trading interface
                            st.subheader("🛒 Place Order")
                            
                            with st.form("option_order_form"):
                                col1, col2, col3 = st.columns(3)
                                
                                with col1:
                                    selected_option = st.selectbox(
                                        "Select Option",
                                        options=[f"{opt['type']} ${opt['strike']:.0f}" for opt in suggestions],
                                        help="Choose an option from the suggestions"
                                    )
                                
                                with col2:
                                    quantity = st.number_input("Quantity", min_value=1, value=1, help="Number of contracts")
                                
                                with col3:
                                    order_side = st.selectbox("Side", options=["buy", "sell"], help="Buy or sell the option")
                                
                                order_type = st.selectbox(
                                    "Order Type",
                                    options=["market", "limit"],
                                    help="Market order executes immediately, limit order sets a price"
                                )
                                
                                limit_price = None
                                if order_type == "limit":
                                    limit_price = st.number_input("Limit Price", min_value=0.01, value=0.01, step=0.01)
                                
                                submit_order = st.form_submit_button("Place Order", type="primary")
                                
                                if submit_order:
                                    # Get the selected option details
                                    option_index = [f"{opt['type']} ${opt['strike']:.0f}" for opt in suggestions].index(selected_option)
                                    selected_option_data = suggestions[option_index]
                                    
                                    # Risk checks
                                    current_price = (selected_option_data['bid'] + selected_option_data['ask']) / 2
                                    risk_ok, risk_message = check_risk_limits(
                                        api=api,
                                        order_side=order_side,
                                        quantity=quantity,
                                        limit_price=limit_price,
                                        current_price=current_price
                                    )
                                    
                                    if not risk_ok:
                                        st.error(f"Risk check failed: {risk_message}")
                                    else:
                                        st.info(f"Risk check passed: {risk_message}")
                                        
                                        # Create proper OCC option symbol
                                        option_symbol = construct_occ_symbol(
                                            underlying=ticker,
                                            expiration_yyyy_mm_dd=expiration_date,
                                            strike=float(selected_option_data['strike']),
                                            option_type='Call' if selected_option_data['type'] == 'Call' else 'Put'
                                        )
                                        
                                        # Place the order
                                        with st.spinner("Placing order..."):
                                            order = place_option_order(
                                                api=api,
                                                symbol=ticker,
                                                option_symbol=option_symbol,
                                                quantity=quantity,
                                                side=order_side,
                                                order_type=order_type,
                                                limit_price=limit_price
                                            )
                                        
                                        if order:
                                            st.success("Order placed successfully!")
                                            
                                            # Display order details
                                            order_details = {
                                                'order_id': order.id,
                                                'symbol': order.symbol,
                                                'side': order.side,
                                                'quantity': order.qty,
                                                'status': order.status,
                                                'order_type': order_type,
                                                'created_at': datetime.now(est).strftime("%Y-%m-%d %H:%M:%S")
                                            }
                                            
                                            st.json(order_details)
                                            
                                            # Save order to database
                                            order_data = {
                                                'id': order.id,
                                                'symbol': order.symbol,
                                                'side': order.side,
                                                'qty': order.qty,
                                                'order_type': order_type,
                                                'status': order.status,
                                                'client_order_id': order.client_order_id
                                            }
                                            
                                            if save_option_order(order_data, client_user, prod):
                                                st.success("Order saved to database")
                                            else:
                                                st.warning("Order placed but not saved to database")
                                            
                                            # Add to session state
                                            st.session_state['option_orders'].append(order_details)
                                            
                                            # Log the test order for validation
                                            logger.info(f"TEST ORDER PLACED: {order_details}")
                                            st.info("📝 Test order logged for validation")
                                        else:
                                            st.error("Failed to place order")
                        else:
                            st.info("No suggestions available for the selected parameters")
                    
                    # -----------------------
                    # Basic Vertical Spread (Debit Call)
                    # -----------------------
                    st.subheader("🧩 Vertical Spread (Debit Call)")
                    try:
                        call_strikes = sorted(list(calls['strike'].unique()))
                        col_a, col_b, col_c = st.columns(3)
                        with col_a:
                            lower_strike = st.selectbox("Buy Strike (lower)", options=call_strikes)
                        with col_b:
                            higher_strike = st.selectbox("Sell Strike (higher)", options=[s for s in call_strikes if s > lower_strike])
                        with col_c:
                            spread_qty = st.number_input("Quantity", min_value=1, value=1)

                        # Mid prices
                        buy_row = calls[calls['strike'] == lower_strike].head(1)
                        sell_row = calls[calls['strike'] == higher_strike].head(1)
                        if not buy_row.empty and not sell_row.empty:
                            buy_mid = float(buy_row['bid'].iloc[0] + buy_row['ask'].iloc[0]) / 2.0
                            sell_mid = float(sell_row['bid'].iloc[0] + sell_row['ask'].iloc[0]) / 2.0
                            net_debit = (buy_mid - sell_mid) * 100 * spread_qty
                            st.info(f"Estimated net debit: ${net_debit:,.2f} for {spread_qty} spread(s)")

                            if st.button("Place Debit Call Vertical"):
                                # Basic budget check via account info
                                try:
                                    acct = refresh_account_info(api=api)
                                    buying_power = float(acct.get('info_converted', {}).get('buying_power', 0))
                                except Exception:
                                    buying_power = 0
                                if buying_power and net_debit > buying_power:
                                    st.error("Insufficient buying power for this spread.")
                                else:
                                    with st.spinner("Placing spread legs..."):
                                        buy_symbol = construct_occ_symbol(ticker, expiration_date, float(lower_strike), 'Call')
                                        sell_symbol = construct_occ_symbol(ticker, expiration_date, float(higher_strike), 'Call')
                                        # Leg 1: Buy lower strike call
                                        leg1 = place_option_order(
                                            api=api,
                                            symbol=ticker,
                                            option_symbol=buy_symbol,
                                            quantity=spread_qty,
                                            side="buy",
                                            order_type="market"
                                        )
                                        # Leg 2: Sell higher strike call
                                        leg2 = place_option_order(
                                            api=api,
                                            symbol=ticker,
                                            option_symbol=sell_symbol,
                                            quantity=spread_qty,
                                            side="sell",
                                            order_type="market"
                                        )
                                        if leg1 and leg2:
                                            st.success("Spread placed (two legs submitted)")
                                        else:
                                            st.warning("One or more legs failed to submit")
                    except Exception as _e:
                        st.warning(f"Spread builder unavailable: {_e}")
                else:
                    st.warning("No options data available for the selected timeframe")
            else:
                st.error("Failed to fetch options chain")
    
    # Display recent orders
    if st.session_state['option_orders']:
        st.subheader("📋 Recent Option Orders")
        orders_df = pd.DataFrame(st.session_state['option_orders'])
        st.dataframe(orders_df, use_container_width=True)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Clear Orders"):
                st.session_state['option_orders'] = []
                st.rerun()
        with col2:
            if st.button("Refresh Orders"):
                # In a real implementation, you'd fetch from database
                st.info("Orders refreshed from session state")
    else:
        st.info("No option orders placed yet")

    # -----------------------
    # Positions View
    # -----------------------
    st.subheader("📊 Open Positions")
    try:
        positions = fetch_positions(api)
        if positions:
            positions_data = []
            for pos in positions:
                positions_data.append({
                    'symbol': pos.symbol,
                    'qty': pos.qty,
                    'side': pos.side,
                    'market_value': pos.market_value,
                    'cost_basis': pos.cost_basis,
                    'unrealized_pl': pos.unrealized_pl,
                    'unrealized_plpc': pos.unrealized_plpc,
                    'asset_class': pos.asset_class
                })
            
            if positions_data:
                positions_df = pd.DataFrame(positions_data)
                st.dataframe(positions_df, use_container_width=True)
                
                # PnL Summary
                total_pl = sum(float(p['unrealized_pl']) for p in positions_data)
                total_market_value = sum(float(p['market_value']) for p in positions_data)
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total P&L", f"${total_pl:,.2f}")
                with col2:
                    st.metric("Total Market Value", f"${total_market_value:,.2f}")
                with col3:
                    st.metric("Number of Positions", len(positions_data))
            else:
                st.info("No open positions")
        else:
            st.info("No open positions")
    except Exception as e:
        st.warning(f"Could not fetch positions: {e}")

    # -----------------------
    # Order Management
    # -----------------------
    st.subheader("🔧 Order Management")
    
    # Order status check
    with st.expander("Check Order Status", expanded=False):
        order_id = st.text_input("Enter Order ID")
        if st.button("Get Status") and order_id:
            with st.spinner("Fetching order status..."):
                status = get_order_status(api, order_id)
                if status:
                    st.json(status)
                else:
                    st.error("Order not found or error occurred")
    
    # Cancel order
    with st.expander("Cancel Order", expanded=False):
        cancel_order_id = st.text_input("Enter Order ID to Cancel")
        if st.button("Cancel Order") and cancel_order_id:
            with st.spinner("Canceling order..."):
                if cancel_order(api, cancel_order_id):
                    st.success("Order canceled successfully")
                else:
                    st.error("Failed to cancel order")

    # -----------------------
    # Risk Management
    # -----------------------
    st.subheader("⚠️ Risk Management")
    
    try:
        account = refresh_account_info(api=api)
        buying_power = float(account.get('info_converted', {}).get('buying_power', 0))
        cash = float(account.get('info_converted', {}).get('cash', 0))
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Buying Power", f"${buying_power:,.2f}")
        with col2:
            st.metric("Cash", f"${cash:,.2f}")
        with col3:
            max_order = min(buying_power * 0.1, 10000)
            st.metric("Max Order Size", f"${max_order:,.2f}")
            
        # Risk settings
        st.info("Risk Limits: Max 10% of buying power per order, $10k maximum order size")
        
    except Exception as e:
        st.warning(f"Could not load risk information: {e}")

if __name__ == "__main__":
    main()
