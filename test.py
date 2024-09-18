import os
import json
import pandas as pd
import numpy as np
import psycopg2
import pickle
import datetime
import collections

# Custom JSON Encoder and Decoder from your provided code
class PollenJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.int64):
            return {"_type": "np.int64", "value": int(obj)}
        if isinstance(obj, pd.DataFrame):
            return {"_type": "pd.DataFrame", "value": obj.to_dict()}
        if isinstance(obj, pd.Timestamp):
            return {"_type": "pd.Timestamp", "value": obj.isoformat()}
        if isinstance(obj, datetime.datetime):
            return {"_type": "datetime.datetime", "value": obj.isoformat()}
        if isinstance(obj, pd.Series):
            return {"_type": "pd.Series", "value": obj.to_dict()}
        if isinstance(obj, collections.deque):
            return {"_type": "collections.deque", "value": list(obj)}
        return super(PollenJsonEncoder, self).default(obj)

class PollenJsonDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        super(PollenJsonDecoder, self).__init__(
            object_hook=self.object_hook, *args, **kwargs
        )

    def object_hook(self, item):
        if "_type" in item:
            if item["_type"] == "np.int64":
                return np.int64(item["value"])
            if item["_type"] == "pd.DataFrame":
                return pd.DataFrame.from_dict(item["value"])
            if item["_type"] == "pd.Timestamp":
                return pd.Timestamp(item["value"])
            if item["_type"] == "datetime.datetime":
                return datetime.datetime.fromisoformat(item["value"])
            if item["_type"] == "pd.Series":
                return pd.Series(item["value"])
            if item["_type"] == "collections.deque":
                return collections.deque(item["value"])
        return item

# Function to read pickle file using PollenJsonDecoder
def read_pickle_file(file_path):
    with open(file_path, 'rb') as f:
        data = pickle.load(f)
    
    # If data is serialized using PollenJsonEncoder, deserialize it
    if isinstance(data, str):
        data = json.loads(data, cls=PollenJsonDecoder)
    elif isinstance(data, dict):
        # Handle the case where data is already a dict but may contain serialized components
        data = json.loads(json.dumps(data, cls=PollenJsonEncoder), cls=PollenJsonDecoder)
    else:
        print("Unsupported data type in pickle file:", type(data))
        return None
    
    # Extract DataFrame if present
    if isinstance(data, pd.DataFrame):
        return data
    elif isinstance(data, dict):
        for value in data.values():
            if isinstance(value, pd.DataFrame):
                return value
    return data

# Function to fetch data from PostgreSQL by key using PollenJsonDecoder
def fetch_postgres_data_by_key(key, conn_params):
    conn = psycopg2.connect(**conn_params)
    cursor = conn.cursor()
    
    query = "SELECT data FROM pollen_store WHERE key = %s LIMIT 1;"
    cursor.execute(query, (key,))
    
    result = cursor.fetchone()
    conn.close()
    
    if result:
        data_json = result[0]
        data = json.loads(data_json, cls=PollenJsonDecoder)
        
        # Extract DataFrame if present
        if isinstance(data, pd.DataFrame):
            return data
        elif isinstance(data, dict):
            for value in data.values():
                if isinstance(value, pd.DataFrame):
                    return value
        return data
    else:
        raise ValueError(f"No data found for key: {key}")

# Function to compare keys and data types
def compare_data(pickle_df, postgres_df):
    # Ensure both are DataFrames
    if not isinstance(pickle_df, pd.DataFrame):
        print("Pickle data is not a DataFrame.")
        return
    if not isinstance(postgres_df, pd.DataFrame):
        print("Postgres data is not a DataFrame.")
        return

    pickle_keys = set(pickle_df.columns)
    postgres_keys = set(postgres_df.columns)

    print("Pickle Keys:", pickle_keys)
    print("Postgres Keys:", postgres_keys)

    # Check if keys match
    if pickle_keys != postgres_keys:
        print("Keys mismatch!")
    else:
        print("Keys match!")

    # Check data types
    pickle_dtypes = pickle_df.dtypes
    postgres_dtypes = postgres_df.dtypes

    print("\nPickle dtypes:")
    print(pickle_dtypes)
    print("\nPostgres dtypes:")
    print(postgres_dtypes)

    if not pickle_dtypes.equals(postgres_dtypes):
        print("\nData types mismatch!")
    else:
        print("\nData types match!")

    # Compare the actual data content
    if pickle_df.equals(postgres_df):
        print("\nData content matches!")
    else:
        print("\nData content does not match!")

if __name__ == "__main__":
    # Paths and connection details
    pickle_file_path = 'symbols_pollenstory_dbs/SPY_1Minute_1Day.pkl'
    postgres_key = 'POLLEN_STORY_SPY_1Minute_1Day'  # Replace with your key value

    # PostgreSQL connection parameters
    conn_params = {
        'dbname': 'pollen',      # Replace with your database name
        'user': 'postgres',        # Replace with your username
        'password': '12345',    # Replace with your password
        'host': 'localhost',            # Replace with your host
        'port': 5432                    # Replace with your port
    }

    # Load pickle data
    pickle_data = read_pickle_file(pickle_file_path)

    # Fetch PostgreSQL data by key
    postgres_data = fetch_postgres_data_by_key(postgres_key, conn_params)

    # Compare data
    compare_data(pickle_data, postgres_data)
