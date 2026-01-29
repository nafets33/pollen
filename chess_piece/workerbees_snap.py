import argparse
import logging
import time
import os
import pandas as pd
import sys
from dotenv import load_dotenv
from datetime import datetime, timedelta, date
import pytz
import asyncio
import aiohttp
import asyncio
from asyncio import Semaphore

# Load environment variables
load_dotenv()

pg_migration = os.getenv('pg_migration') 

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from chess_piece.king import ReadPickleData, print_line_of_error, return_crypto_snapshots, master_swarm_QUEENBEE
from chess_piece.queen_hive import init_logging, get_best_limit_price, return_alpaca_api_keys, return_Ticker_Universe, return_market_hours, return_symbols_list_from_queenbees_story
from chess_piece.pollen_db import PollenDatabase, PollenJsonEncoder

# Global variables
est = pytz.timezone("US/Eastern")
crypto_currency_symbols = ['BTC/USD', 'ETH/USD']
server = os.getenv('server', False)




class PriceInfoDatabase:
    """Extended PollenDatabase for price info specific operations"""
    
    @staticmethod
    def create_priceinfo_table(table_name='snapshot_priceinfo'):
        """
        Create a simple latest-price-only table
        """
        with PollenDatabase.get_connection() as conn, conn.cursor() as cur:
            cur.execute("""
            SELECT to_regclass(%s);
            """, (table_name,))
            result = cur.fetchone()[0]
            
            if result is None:  # Table does not exist
                create_table_query = f"""
                CREATE TABLE {table_name} (
                    ticker VARCHAR(10) PRIMARY KEY,
                    current_price DOUBLE PRECISION,
                    current_bid DOUBLE PRECISION,
                    current_ask DOUBLE PRECISION,
                    maker_middle DOUBLE PRECISION,
                    ask_bid_variance DOUBLE PRECISION,
                    bid_ask_var DOUBLE PRECISION,
                    is_crypto BOOLEAN DEFAULT FALSE,
                    last_updated TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
                
                -- Only needed index for crypto filtering
                CREATE INDEX idx_{table_name}_crypto ON {table_name}(is_crypto);
                """
                cur.execute(create_table_query)
                conn.commit()
                print(f"Created table: {table_name}")
                return True
            else:
                print(f"Table already exists: {table_name}")
                return False
        

    @staticmethod
    def insert_priceinfo(price_data, table_name='snapshot_priceinfo'):
        """
        Insert price info data into the database
        """
        try:
            with PollenDatabase.get_connection() as conn, conn.cursor() as cur:
                now_est = datetime.now(est)
                
                insert_query = f"""
                INSERT INTO {table_name} 
                (ticker, current_price, current_bid, current_ask, maker_middle, 
                ask_bid_variance, bid_ask_var, is_crypto, last_updated)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (ticker) DO UPDATE SET
                    current_price = EXCLUDED.current_price,
                    current_bid = EXCLUDED.current_bid,
                    current_ask = EXCLUDED.current_ask,
                    maker_middle = EXCLUDED.maker_middle,
                    ask_bid_variance = EXCLUDED.ask_bid_variance,
                    bid_ask_var = EXCLUDED.bid_ask_var,
                    is_crypto = EXCLUDED.is_crypto,
                    last_updated = EXCLUDED.last_updated
                """
                
                cur.execute(insert_query, (
                    price_data['ticker'],
                    price_data.get('current_price'),
                    price_data.get('current_bid'),
                    price_data.get('current_ask'),
                    price_data.get('maker_middle'),
                    price_data.get('ask_bid_variance'),
                    price_data.get('bid_ask_var'),
                    price_data.get('is_crypto', False),
                    now_est
                ))
                
                conn.commit()
                return True
                
        except Exception as e:
            print(f"Error inserting price data for {price_data.get('ticker', 'unknown')}: {e}")
            return False

    @staticmethod
    def bulk_insert_priceinfo(price_data_list, table_name='snapshot_priceinfo'):
        """
        Bulk insert multiple price info records
        """
        try:
            with PollenDatabase.get_connection() as conn, conn.cursor() as cur:
                now_est = datetime.now(est)
                
                insert_query = f"""
                INSERT INTO {table_name} 
                (ticker, current_price, current_bid, current_ask, maker_middle, 
                ask_bid_variance, bid_ask_var, is_crypto, last_updated)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (ticker) DO UPDATE SET
                    current_price = EXCLUDED.current_price,
                    current_bid = EXCLUDED.current_bid,
                    current_ask = EXCLUDED.current_ask,
                    maker_middle = EXCLUDED.maker_middle,
                    ask_bid_variance = EXCLUDED.ask_bid_variance,
                    bid_ask_var = EXCLUDED.bid_ask_var,
                    is_crypto = EXCLUDED.is_crypto,
                    last_updated = EXCLUDED.last_updated
                """
                
                records = []
                for price_data in price_data_list:
                    records.append((
                        price_data['ticker'],
                        price_data.get('current_price'),
                        price_data.get('current_bid'),
                        price_data.get('current_ask'),
                        price_data.get('maker_middle'),
                        price_data.get('ask_bid_variance'),
                        price_data.get('bid_ask_var'),
                        price_data.get('is_crypto', False),
                        now_est
                    ))
                
                cur.executemany(insert_query, records)
                conn.commit()
                # print(f"Successfully inserted {len(records)} price records", datetime.now(est).strftime('%Y-%m-%d %H:%M:%S'))
                return True
                
        except Exception as e:
            print(f"Error bulk inserting price data: {e}")
            return False



def get_bulk_snapshots_priceinfo(api, symbols, max_symbols_per_api_call=89):
    """
    Get bulk snapshots for multiple symbols at once using Alpaca's batch endpoint
    Now handles smaller batches more efficiently with proper type conversion
    """
    try:
        # Separate crypto and regular symbols
        regular_symbols = [s for s in symbols if s not in crypto_currency_symbols]
        crypto_symbols = [s for s in symbols if s in crypto_currency_symbols]
        
        all_priceinfo = []
        
        # Fetch regular stocks in bulk
        if regular_symbols:
            # Split into API call chunks (Alpaca limit per call)
            for i in range(0, len(regular_symbols), max_symbols_per_api_call):
                symbol_chunk = regular_symbols[i:i + max_symbols_per_api_call]
                # print(len(symbol_chunk), "symbols in this chunk")
                try:
                    # print(f"Fetching bulk snapshots for {len(symbol_chunk)} symbols...")
                    # Use Alpaca's multi-snapshot endpoint
                    snapshots = api.get_snapshots(symbol_chunk)
                    
                    for ticker, snap in snapshots.items():
                        if snap and snap.latest_quote and snap.latest_trade:
                            # Convert to float to avoid Decimal/float conflicts
                            ask = float(snap.latest_quote.ask_price)
                            price = float(snap.latest_trade.price)
                            bid = float(snap.latest_quote.bid_price)
                            
                            if ask > 0 and price > 0 and bid > 0:
                                # Calculate metrics - all operations now use floats
                                best_limit_price = get_best_limit_price(ask=ask, bid=bid)
                                maker_middle = float(best_limit_price['maker_middle'])
                                ask_bid_variance = bid / ask  # Now safe - both floats
                                bid_ask_var = bid / ask       # Now safe - both floats
                                
                                priceinfo = {
                                    'ticker': ticker,
                                    'current_price': price,
                                    'current_bid': bid,
                                    'current_ask': ask,
                                    'maker_middle': maker_middle,
                                    'ask_bid_variance': ask_bid_variance,
                                    'bid_ask_var': bid_ask_var,
                                    'is_crypto': False
                                }
                                all_priceinfo.append(priceinfo)
                    
                    chunk_results = len(snapshots) if snapshots else 0
                    print(f"Successfully processed, symbols in this chunk {chunk_results} ")
                                
                except Exception as e:
                    print(f"Error fetching bulk snapshots for chunk: {e}")
                    
                # Small delay between API calls to be respectful
                time.sleep(0.1)
        
        # Handle crypto separately (with type conversion too)
        if crypto_symbols:
            for ticker in crypto_symbols:
                try:
                    crypto_data = return_crypto_snapshots(ticker)
                    if ticker in crypto_data:
                        snap = crypto_data[ticker]
                        # Convert crypto values to float as well
                        ask_price = float(snap['latestQuote']['ap'])
                        bid_price = float(snap['latestQuote']['bp'])
                        
                        priceinfo = {
                            'ticker': ticker,
                            'current_price': ask_price,  # Use ask as price for crypto
                            'current_bid': bid_price,
                            'current_ask': ask_price,
                            'maker_middle': ask_price,  # Simplified for crypto
                            'ask_bid_variance': bid_price / ask_price if ask_price > 0 else 0,
                            'bid_ask_var': bid_price / ask_price if ask_price > 0 else 0,
                            'is_crypto': True
                        }
                        all_priceinfo.append(priceinfo)
                except Exception as e:
                    print(f"Error fetching crypto snapshot for {ticker}: {e}")
        
        return all_priceinfo
        
    except Exception as e:
        print(f"Error in bulk snapshot fetch: {e}")
        return []


def get_priceinfo_snapshot(api, ticker, crypto=False):
    """
    Get price snapshot for a single ticker
    """
    try:
        snap = api.get_snapshot(ticker) if not crypto else return_crypto_snapshots(ticker)
        
        if crypto:
            snap = snap[ticker]
            priceinfo_order = {
                'price': snap['latestQuote']['ap'], 
                'bid': snap['latestQuote']['bp'], 
                'ask': snap['latestQuote']['ap'], 
                'bid_ask_var': snap['latestQuote']['bp']/snap['latestQuote']['ap']
            }
        else:
            ask = snap.latest_quote.ask_price
            price = snap.latest_trade.price
            if ask == 0 or price == 0:
                print(f"ERROR: Price OR Ask is 0 for {ticker}: {snap}")
                return {}
            
            priceinfo_order = {
                'price': snap.latest_trade.price, 
                'bid': snap.latest_quote.bid_price, 
                'ask': snap.latest_quote.ask_price, 
                'bid_ask_var': snap.latest_quote.bid_price/snap.latest_quote.ask_price
            }
        
        priceinfo_order['ticker'] = ticker
        return priceinfo_order
        
    except Exception as e:
        print(f"SNAP CALL ERROR for {ticker}: {e}")
        return {}


def process_priceinfo_snapshot(api, ticker, crypto=False):
    """
    Process a single ticker and return formatted price info
    """
    try:
        # Get raw price snapshot
        temp = get_priceinfo_snapshot(api, ticker, crypto)
        if not temp:
            print(f"Failed to get price info for {ticker}")
            return None

        # Extract price data
        current_price = temp.get('price')
        current_ask = temp.get('ask')
        current_bid = temp.get('bid')
        bid_ask_var = temp.get('bid_ask_var')

        # Calculate best limit price and other metrics
        best_limit_price = get_best_limit_price(ask=current_ask, bid=current_bid)
        maker_middle = best_limit_price['maker_middle']
        ask_bid_variance = current_bid / current_ask if current_ask and current_ask != 0 else 0

        # Format final price info
        priceinfo = {
            'ticker': ticker,
            'current_price': current_price,
            'current_bid': current_bid,
            'current_ask': current_ask,
            'maker_middle': maker_middle,
            'ask_bid_variance': ask_bid_variance,
            'bid_ask_var': bid_ask_var,
            'is_crypto': crypto
        }
        
        return priceinfo
        
    except Exception as e:
        print(f"Error processing price info for {ticker}: {e}")
        return None


async def get_priceinfo_async(session, api, ticker, crypto=False):
    """
    Async function to get price info for a single ticker
    """
    try:
        # Run the synchronous API call in executor to avoid blocking
        loop = asyncio.get_event_loop()
        priceinfo = await loop.run_in_executor(
            None, 
            process_priceinfo_snapshot, 
            api, 
            ticker, 
            crypto
        )
        return priceinfo
    except Exception as e:
        print(f"Async price info error for {ticker}: {e}")
        return None


async def fetch_and_store_priceinfo_async(symbols, api, table_name='snapshot_priceinfo', save_to_db=False, batch_size=100, max_concurrent_batches=3, init=False):
    """
    Main async function to fetch and store price info using batched bulk API calls
    """
    try:
        s = datetime.now()
        logging.info(f"Fetching price info for {len(symbols)} symbols using batched bulk API...")
        
        # Create table if it doesn't exist
        if save_to_db and init:
            PriceInfoDatabase.create_priceinfo_table(table_name)
        
        # Split symbols into batches
        symbol_batches = [symbols[i:i + batch_size] for i in range(0, len(symbols), batch_size)]
        # print(f"Processing {len(symbol_batches)} batches of {batch_size} symbols each")
        
        # Semaphore to limit concurrent API calls
        semaphore = asyncio.Semaphore(max_concurrent_batches)
        
        async def process_batch(batch):
            async with semaphore:
                # Run bulk snapshot call in executor to avoid blocking
                loop = asyncio.get_event_loop()
                return await loop.run_in_executor(
                    None, 
                    get_bulk_snapshots_priceinfo, 
                    api, 
                    batch
                )
        
        # Process all batches concurrently
        batch_tasks = [process_batch(batch) for batch in symbol_batches]
        batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
        
        # Flatten results
        price_data_list = []
        for result in batch_results:
            if isinstance(result, list):
                price_data_list.extend(result)
            elif isinstance(result, Exception):
                print(f"Batch error: {result}")
        
        # print(f"Time taken to FETCH snapshots: {datetime.now() - s}")
        
        if not price_data_list:
            logging.error("No valid price data retrieved")
            return []
        
        logging.info(f"Retrieved price data for {len(price_data_list)} symbols {symbol_batches}")
        
        # Save to database if requested
        s = datetime.now()
        if save_to_db:
            success = PriceInfoDatabase.bulk_insert_priceinfo(price_data_list, table_name)
            if success:
                logging.info(f"Successfully saved {len(price_data_list)} records to {table_name}")
            else:
                logging.error("Failed to save records to database")
        # print(f"Time taken to SAVE snapshots: {datetime.now() - s}")
        
        return price_data_list
        
    except Exception as e:
        logging.error(f"Error in fetch_and_store_priceinfo_async: {e}")
        print_line_of_error()
        return []


def fetch_and_store_priceinfo(symbols, api, table_name='snapshot_priceinfo', save_to_db=False, batch_size=100, max_concurrent_batches=3, init=False):
    """
    Wrapper function to run the async version
    """
    return asyncio.run(fetch_and_store_priceinfo_async(
        symbols, api, table_name, save_to_db, batch_size, max_concurrent_batches, init
    ))



def confirm_tickers_available(alpaca_symbols_dict, symbols):
    queens_master_tickers = []
    errors = []
    alpaca_symbols_dict['BTC/USD'] = {}
    alpaca_symbols_dict['ETH/USD'] = {}
    for i in symbols:
        if i in alpaca_symbols_dict.keys():
            queens_master_tickers.append(i)
        else:
            msg=(i, "Ticker NOT in Alpaca Ticker DB")
            errors.append(msg)
    if errors:
        msg = str(errors)
        # send_email(subject="Tickers Not Longer Active", body=msg)
        print("MISSING TICKER NOT IN ALPACA", msg)
    
    return queens_master_tickers


def close_crypto_worker(crypto):
    s = datetime.now(est)
    date = datetime.now(est)
    if crypto:
        turn_off_time = date.replace(hour=22, minute=0, second=0)
        if s > turn_off_time:
            print("CRYPTO: Great Job! See you Tomorrow")
            return True
    # else:
    #     date = date.replace(hour=16, minute=0, second=1)
    #     if s >= date:
    #         # logging.info("Happy Bee Day End")
    #         print("Great Job! See you Tomorrow")
    #         print("save all workers and their results")
    #         return True
    
    return False


def main_workerbees_snap(prod=True, awake=False, save_to_db=True, loglevel='WARNING'):
    """
    Main function for standalone execution
    """
    # Initialize logging
    init_logging(queens_chess_piece="SnapShots", loglevel=loglevel, console_only=True)
    
    # Example symbols to fetch
    # symbols = ['HD', 'AAPL', 'GOOGL', 'MSFT', 'TSLA', 'SPY', 'QQQ', 'BTC/USD', 'ETH/USD']

    alpaca_symbols_dict = return_Ticker_Universe().get('alpaca_symbols_dict')
    print("READING MASTER QUEEN")
    if pg_migration:
        table_name = 'db' if prod else 'db_sandbox'
        QUEENBEE = PollenDatabase.retrieve_data(table_name, key='QUEEN')
    else:
        QUEENBEE = ReadPickleData(master_swarm_QUEENBEE(prod=prod))
    queens_chess_pieces = [k for k,v in QUEENBEE['workerbees'].items()]
    list_of_lists = [i.get('tickers') for qcp, i in QUEENBEE['workerbees'].items() if qcp in queens_chess_pieces]
    symbols = [item for sublist in list_of_lists for item in sublist]
    symbols = confirm_tickers_available(alpaca_symbols_dict, symbols)
    symbols = return_symbols_list_from_queenbees_story(symbols=symbols, all_symbols=True)
    print(len(symbols), "Total Symbols to Process")

    
    # You'll need to initialize your API client here
    api = return_alpaca_api_keys(prod=prod)["api"]
    
    if api is None:
        print("ERROR: API client not initialized")
        return
    
    # Fetch and store price info
    print(f"Number of Symbolds to Process: {len(symbols)}")
    table_name = 'snapshot_priceinfo'  # or 'snapshot_priceinfo' for production
    price_data = fetch_and_store_priceinfo(symbols, api, table_name, save_to_db=save_to_db, init=True)
    
    # Display results
    if price_data:
        df = pd.DataFrame(price_data)
        print("\nPrice Info Summary:")
        print(df[['ticker', 'current_price', 'current_ask', 'current_bid', 'is_crypto']])
    
    print("Price info snapshot complete!")

    trading_days = api.get_calendar()
    trading_days_df = pd.DataFrame([day._raw for day in trading_days])
    trading_days_df["date"] = pd.to_datetime(trading_days_df["date"])
    
    if awake:
        last_print_time = datetime.now()  # Add this
        while True:
            mkhrs = return_market_hours(trading_days=trading_days)
            if mkhrs != 'open':
                # print("Market is closed.")
                symbols = [i for i in symbols if i in crypto_currency_symbols]
                if close_crypto_worker(crypto=True):
                    break
            if symbols:
                current_time = datetime.now()
                if (current_time - last_print_time).total_seconds() >= 60:
                    print("Fetching price info snapshot at", symbols, datetime.now(est).strftime("%Y-%m-%d %I:%M%p"))
                    last_print_time = current_time

                price_data = fetch_and_store_priceinfo(symbols, api, table_name, save_to_db=save_to_db)

            else:
                print("No symbols to process.")

if __name__ == "__main__":

    def script_parser():
        parser = argparse.ArgumentParser()
        parser.add_argument("-prod", default=True)
        parser.add_argument("-awake", default=False)
        parser.add_argument("-save_to_db", default=True)
        parser.add_argument("-loglevel", default='WARNING')


        return parser

    # script arguments
    parser = script_parser()
    namespace = parser.parse_args()
    awake = namespace.awake
    prod = namespace.prod
    save_to_db = namespace.save_to_db
    loglevel = namespace.loglevel

    main_workerbees_snap(prod=prod, awake=awake, save_to_db=save_to_db, loglevel=loglevel)