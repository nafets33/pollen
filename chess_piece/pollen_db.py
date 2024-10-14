import collections
import datetime
import json
import os
import pandas as pd
import numpy as np
import psycopg2


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


class PollenDatabase:
    @staticmethod
    def get_connection():
        # Reading connection details from environment variables
        DATABASE_HOST = os.getenv("POLLEN_DATABASE_host", "localhost")
        DATABASE_PORT = os.getenv("POLLEN_DATABASE_port", "5432")
        DATABASE_NAME = os.getenv("POLLEN_DATABASE_name", "pollen")
        DATABASE_USER = os.getenv("POLLEN_DATABASE_user", "postgres")
        DATABASE_PASS = os.getenv("POLLEN_DATABASE_pass", "12345")

        return psycopg2.connect(
            host=DATABASE_HOST,
            port=DATABASE_PORT,
            dbname=DATABASE_NAME,
            user=DATABASE_USER,
            password=DATABASE_PASS,
        )
    
    @staticmethod
    def create_table_if_not_exists(table_name):
        """
        Create a table if it doesn't exist with the following structure:
        - id: serial, primary key
        - key: varchar(255), unique, not null
        - data: text, not null
        - created_at: timestamp, defaults to CURRENT_TIMESTAMP
        """
        with PollenDatabase.get_connection() as conn, conn.cursor() as cur:
            create_table_query = f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                id SERIAL PRIMARY KEY,
                key VARCHAR(255) UNIQUE NOT NULL,
                data TEXT NOT NULL,
                created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
            """
            cur.execute(create_table_query)
            conn.commit()
            # conn.close()

    @staticmethod
    def key_exists(table_name, key):
        """
        Checks if a key exists in the specified table.

        :param table_name: The name of the table to search.
        :param key: The key to check for.
        :return: True if the key exists, False otherwise.
        """
        conn = None
        try:
            conn = PollenDatabase.get_connection()
            cur = conn.cursor()

            # Query to check if the key exists in the table
            query = f"SELECT EXISTS (SELECT 1 FROM {table_name} WHERE key = %s);"
            cur.execute(query, (key,))
            result = cur.fetchone()

            # Return True if the key exists, False otherwise
            return result[0]

        except Exception as e:
            return False
        finally:
            if conn:
                conn.close()

    @staticmethod
    def get_table_name():
        # Get table name from environment variable
        ### Tables created
        # client_user_dbs
        # db
        # pollen_store
        return os.getenv(
            "POLLEN_TABLE_NAME", "pollen_store"
        )  # default to "pollen_store" if not set


    @staticmethod
    def upsert_data(table_name, key, value):
        """
        Upsert data into a specified table. If the table doesn't exist, it will be created.
        """
        # Ensure the table exists before attempting to upsert data
        PollenDatabase.create_table_if_not_exists(table_name)

        with PollenDatabase.get_connection() as conn, conn.cursor() as cur:
            # Serialize the value to JSON
            value_json = json.dumps(value, cls=PollenJsonEncoder)

            # Upsert data into the table
            upsert_query = f"""
                INSERT INTO {table_name} (key, data) 
                VALUES (%s, %s)
                ON CONFLICT (key) 
                DO UPDATE SET data = EXCLUDED.data;
            """
            cur.execute(upsert_query, (key, value_json))
            conn.commit()

    @staticmethod
    def retrieve_data(table_name, key):
        conn = None
        try:
            conn = PollenDatabase.get_connection()
            cur = conn.cursor()

            # Retrieve using the configured table name
            cur.execute(
                f"SELECT data FROM {table_name} WHERE key = %s;",
                (key,),
            )
            result = cur.fetchone()
            if result:
                # Check the type of the result
                if isinstance(result[0], str):
                    serialized_data = result[0]
                elif isinstance(result[0], dict):
                    serialized_data = json.dumps(result[0])

                # Always deserialize using custom decoder
                return json.loads(serialized_data, cls=PollenJsonDecoder)

        except Exception as e:
            print(f"Error: {e}")
        finally:
            if conn:
                conn.close()

        return None
    
    @staticmethod
    def retrieve_all_story_bee_data(symbols):
        conn = None
        merged_data = {"STORY_bee": {}}

        try:
            conn = PollenDatabase.get_connection()
            cur = conn.cursor()

            # Base query
            query = f"SELECT key, data FROM {PollenDatabase.get_table_name()} WHERE key LIKE 'STORY_BEE%';"
            
            # If symbols are provided, filter by the 3rd underscore value (symbol) in the key
            if symbols:
                symbol_conditions = " OR ".join([f"split_part(key, '_', 3) = '{symbol}'" for symbol in symbols])
                query = f"SELECT key, data FROM {PollenDatabase.get_table_name()} WHERE key LIKE 'STORY_BEE%' AND ({symbol_conditions});"
            
            cur.execute(query)
            results = cur.fetchall()

            for result in results:
                key_name = result[0]
                data_dict = result[1]  # Now data column is the second column
                nested_key = key_name.replace('STORY_BEE_', '')

                # Assuming data_dict is a dict, but if it's a string representation of JSON, use json.loads(data_dict)
                merged_data["STORY_bee"][nested_key] = data_dict["STORY_bee"]

            merged_data = json.dumps(merged_data)
            # Always deserialize using custom decoder
            return json.loads(merged_data, cls=PollenJsonDecoder)

        except Exception as e:
            print(f"Error: {e}")
        finally:
            if conn:
                conn.close()

        return None

class TestPollenDatabase:
    @staticmethod
    def assertEqual(a, b, msg=None):
        if a != b:
            print(f"✖ {msg} - Expected: {a}, Got: {b}")
        else:
            print(f"✔ {msg}")

    @staticmethod
    def assertTrue(cond, msg=None):
        if not cond:
            print(f"✖ {msg}")
        else:
            print(f"✔ {msg}")

    @staticmethod
    def test_upsert_retrieve():
        test_data = {
            "integer": 123,
            "float": 3.14,
            "numpy_int": np.int64(456),
            "dataframe": pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]}),
            "timestamp": pd.Timestamp("2023-09-01"),
            "datetime": datetime.datetime(2023, 9, 1),
            "series": pd.Series([7, 8, 9]),
            "deque": collections.deque([10, 11, 12]),
        }

        # Upserting the test data
        PollenDatabase.upsert_data("test_key", test_data)

        # Retrieving the stored data
        retrieved_data = PollenDatabase.retrieve_data("test_key")

        # Comparisons
        TestPollenDatabase.assertEqual(
            test_data["integer"], retrieved_data["integer"], "Integer Check"
        )
        TestPollenDatabase.assertEqual(
            test_data["float"], retrieved_data["float"], "Float Check"
        )
        TestPollenDatabase.assertEqual(
            test_data["numpy_int"], retrieved_data["numpy_int"], "Numpy Integer Check"
        )

        # For DataFrame: Using numpy's array_equal for value-based comparison
        df_check = np.array_equal(
            test_data["dataframe"].values, retrieved_data["dataframe"].values
        )
        TestPollenDatabase.assertTrue(df_check, "DataFrame Check")

        TestPollenDatabase.assertEqual(
            test_data["timestamp"], retrieved_data["timestamp"], "Timestamp Check"
        )
        TestPollenDatabase.assertEqual(
            test_data["datetime"], retrieved_data["datetime"], "Datetime Check"
        )

        # For Series: Using numpy's array_equal for value-based comparison
        series_check = np.array_equal(
            test_data["series"].values, retrieved_data["series"].values
        )
        TestPollenDatabase.assertTrue(series_check, "Series Check")

        # Convert deque to list for value-based comparison
        TestPollenDatabase.assertEqual(
            list(test_data["deque"]), list(retrieved_data["deque"]), "Deque Check"
        )