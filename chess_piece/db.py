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
        DATABASE_HOST = os.getenv("POLLEN_DATABASE_HOST")
        DATABASE_PORT = os.getenv("POLLEN_DATABASE_PORT")
        DATABASE_NAME = os.getenv("POLLEN_DATABASE_NAME")
        DATABASE_USER = os.getenv("POLLEN_DATABASE_USER")
        DATABASE_PASS = os.getenv("POLLEN_DATABASE_PASS")

        return psycopg2.connect(
            host=DATABASE_HOST,
            port=DATABASE_PORT,
            dbname=DATABASE_NAME,
            user=DATABASE_USER,
            password=DATABASE_PASS,
        )

    @staticmethod
    def get_table_name():
        # Get table name from environment variable
        return os.getenv(
            "POLLEN_TABLE_NAME", "pollen_store"
        )  # default to "pollen_store" if not set

    @staticmethod
    def upsert_data(key, value):
        with PollenDatabase.get_connection() as conn, conn.cursor() as cur:
            # Serialize data with custom encoder
            value_json = json.dumps(value, cls=PollenJsonEncoder)

            # Upserting using the configured table name
            cur.execute(
                f"""
                INSERT INTO {PollenDatabase.get_table_name()} (key, data) 
                VALUES (%s, %s)
                ON CONFLICT (key) 
                DO UPDATE SET data = EXCLUDED.data;
            """,
                (key, value_json),
            )
            conn.commit()

    @staticmethod
    def retrieve_data(key):
        conn = None
        try:
            conn = PollenDatabase.get_connection()
            cur = conn.cursor()

            # Retrieve using the configured table name
            cur.execute(
                f"SELECT data FROM {PollenDatabase.get_table_name()} WHERE key = %s;",
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