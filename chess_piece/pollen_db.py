import collections
import datetime
import json
import os
import pandas as pd
import numpy as np
from chess_piece.king import print_line_of_error
import logging
import json
import psycopg2
from psycopg2 import sql
from psycopg2 import extras
import pickle
import streamlit as st
import sys

server = os.getenv("server", False)


class PollenJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        try:
            # Handle NumPy types
            if isinstance(obj, (np.int32, np.int64)):  # Add np.int32 here
                return {"_type": "np.int64", "value": int(obj)}
            if isinstance(obj, (np.float32, np.float64)):  # Handle float types as well
                return {"_type": "float", "value": float(obj)}
            
            # Handle pandas types
            if isinstance(obj, pd.DataFrame):
                return {"_type": "pd.DataFrame", "value": obj.to_dict()}
            if isinstance(obj, pd.Timestamp):
                return {"_type": "pd.Timestamp", "value": obj.isoformat()}
            if isinstance(obj, pd.Series):
                return {"_type": "pd.Series", "value": obj.to_dict()}
            
            # Handle Python datetime
            if isinstance(obj, datetime.datetime):
                return {"_type": "datetime.datetime", "value": obj.isoformat()}
            
            # Handle collections.deque
            if isinstance(obj, collections.deque):
                return {"_type": "collections.deque", "value": list(obj)}
            
            # Default handling
            return super(PollenJsonEncoder, self).default(obj)
        except Exception as e:
            # Handle unexpected errors in the encoding process
            return {"_type": "error", "message": str(e)}

class PollenJsonDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        super(PollenJsonDecoder, self).__init__(
            object_hook=self.object_hook, *args, **kwargs
        )

    def object_hook(self, item):
        if "_type" in item:
            if item["_type"] == "np.int64" or item["_type"] == "<class 'numpy.int64'>":
                return np.int64(item["value"])
            if item["_type"] == "float":
                return float(item["value"])
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
    def get_connection(server=server):
        if server:
            # Reading connection details from environment variables
            DATABASE_HOST = os.getenv("POLLEN_DATABASE_host_server")
            DATABASE_PORT = os.getenv("POLLEN_DATABASE_port_server")
            DATABASE_NAME = os.getenv("POLLEN_DATABASE_name_server")
            DATABASE_USER = os.getenv("POLLEN_DATABASE_user_server")
            DATABASE_PASS = os.getenv("POLLEN_DATABASE_pass_server")
        else:
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
    def return_db_conn(return_curser=False):
        
        con = PollenDatabase.get_connection()
        cur = con.cursor()
        if return_curser:
            return con, cur
        
        # Create table if it doesn't exist
        create_table_query = """
        CREATE TABLE IF NOT EXISTS client_users (
            email VARCHAR(255) PRIMARY KEY,
            password TEXT NOT NULL,
            name VARCHAR(255) NOT NULL,
            phone_no VARCHAR(50),
            signup_date TIMESTAMP,
            last_login_date TIMESTAMP,
            login_count INTEGER
        );
        """
        cur.execute(create_table_query)
        con.commit()
        
        return con, cur

    @staticmethod
    def create_table_if_not_exists(table_name):
        """
        Create a table if it doesn't exist with the following structure:
        - id: serial, primary key
        - key: varchar(255), unique, not null
        - data: text, not null
        - created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        - last_modified: timestamp, defaults to CURRENT_TIMESTAMP
        Returns True if the table was created, False if it already existed.
        """
        with PollenDatabase.get_connection() as conn, conn.cursor() as cur:
            # Check if the table exists already
            cur.execute("""
            SELECT to_regclass(%s);
            """, (table_name,))
            result = cur.fetchone()[0]
            
            if result is None:  # Table does not exist
                create_table_query = f"""
                CREATE TABLE {table_name} (
                    id SERIAL PRIMARY KEY,
                    key VARCHAR(255) UNIQUE NOT NULL,
                    data TEXT NOT NULL,
                    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    last_modified TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
                """
                cur.execute(create_table_query)
                conn.commit()
                return True  # Table was created
            else:
                return False  # Table already exists

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
    def ensure_last_modified_column(table_name):
        """
        Adds 'last_modified' column to the table if it doesn't exist.
        """
        with PollenDatabase.get_connection() as conn, conn.cursor() as cur:
            alter_query = f"""
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1
                    FROM information_schema.columns 
                    WHERE table_name = '{table_name}' 
                    AND column_name = 'last_modified'
                ) THEN
                    ALTER TABLE {table_name} 
                    ADD COLUMN last_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
                END IF;
            END $$;
            """
            cur.execute(alter_query)
            conn.commit()

    @staticmethod
    def upsert_data(table_name, key, value, console=True, console_table_ignore=['logging_store'], main_server=server):
        """
        Upsert data into a specified table. If the table doesn't exist, it will be created.
        Dynamically handles 'last_modified' based on table schema.
        """
        # Ensure the table exists before attempting to upsert data
        PollenDatabase.create_table_if_not_exists(table_name)
        try:
            # print(f"saving {key}  size: {sys.getsizeof(value)}")
            # Check if 'last_modified' column exists
            with PollenDatabase.get_connection(main_server) as conn, conn.cursor() as cur:
                cur.execute(f"""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = %s AND column_name = 'last_modified'
                """, (table_name,))
                has_last_modified = cur.fetchone() is not None
            if not has_last_modified:
                PollenDatabase.update_table_schema(table_name)
            
            with PollenDatabase.get_connection(main_server) as conn, conn.cursor() as cur:
                value_json = json.dumps(value, cls=PollenJsonEncoder)

                upsert_query = f"""
                    INSERT INTO {table_name} (key, data, last_modified)
                    VALUES (%s, %s, CURRENT_TIMESTAMP)
                    ON CONFLICT (key) 
                    DO UPDATE SET data = EXCLUDED.data, last_modified = CURRENT_TIMESTAMP;
                """

                cur.execute(upsert_query, (key, value_json))
                conn.commit()

                if console and table_name not in console_table_ignore:
                    print(f'{key} Upserted to {table_name} server={main_server}')
        except Exception as e:
            print("issue arrived in upsert_data function")
            print_line_of_error(e)
            return False
        
        return True

    @staticmethod
    def upsert_multiple(table_name, data_dict):
        """
        Bulk upsert dictionary of data into the specified table.
        Data values are serialized with a custom JSON encoder if needed.
        """
        with PollenDatabase.get_connection() as conn, conn.cursor() as cur:
            try:
                # Prepare records for batch insert (key, data, last_modified)
                records = [
                    (key, json.dumps(value, cls=PollenJsonEncoder), datetime.datetime.now()) 
                    for key, value in data_dict.items()
                ]

                # Use PostgreSQL's INSERT ON CONFLICT for upsert
                insert_query = f"""
                    INSERT INTO {table_name} (key, data, last_modified)
                    VALUES %s
                    ON CONFLICT (key) 
                    DO UPDATE SET 
                        data = EXCLUDED.data, 
                        last_modified = CURRENT_TIMESTAMP;
                """
                
                
                # Use execute_values for efficient batch inserts
                extras.execute_values(cur, insert_query, records)
                conn.commit()

            except Exception as e:
                print("Error during bulk upsert:", e)
                conn.rollback()

    @staticmethod
    def retrieve_data(table_name, key, main_server=server):
        conn = None
        try:
            conn = PollenDatabase.get_connection(main_server)
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
                data = json.loads(serialized_data, cls=PollenJsonDecoder)
                if len(data) == 0:
                    print('NO DATA AVAIL for ', key)
                    return None
                
                data['key'] = key
                data['table_name'] = table_name
                data['db_root'] = key.split("-")[0]
                return data

        except Exception as e:
            print_line_of_error()
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
            # import ipdb
            # ipdb.set_trace()
            for result in results:
                key_name = result[0]
                data_dict = result[1]  # Now data column is the second column
                nested_key = key_name.replace('STORY_BEE_', '')

                # Assuming data_dict is a dict, but if it's a string representation of JSON, use json.loads(data_dict)
                if type(data_dict) == str:
                    data_dict = json.loads(data_dict)
                    merged_data["STORY_bee"][nested_key] = data_dict["STORY_bee"]
                else:
                    merged_data["STORY_bee"][nested_key] = data_dict["STORY_bee"]

            merged_data = json.dumps(merged_data)
            # Always deserialize using custom decoder
            return json.loads(merged_data, cls=PollenJsonDecoder)

        except Exception as e:
            print_line_of_error(e)
        finally:
            if conn:
                conn.close()

        return None


    @staticmethod
    def retrieve_all_pollenstory_data(symbols):
        conn = None
        merged_data = {"pollenstory": {}}

        try:
            conn = PollenDatabase.get_connection()
            cur = conn.cursor()

            # Base query
            query = f"SELECT key, data FROM {PollenDatabase.get_table_name()} WHERE key LIKE 'POLLEN_STORY%';"
            
            # If symbols are provided, filter by the 3rd underscore value (symbol) in the key
            if symbols:
                symbol_conditions = " OR ".join([f"split_part(key, '_', 3) = '{symbol}'" for symbol in symbols])
                query = f"SELECT key, data FROM {PollenDatabase.get_table_name()} WHERE key LIKE 'POLLEN_STORY%' AND ({symbol_conditions});"
            
            cur.execute(query)
            results = cur.fetchall()
            # ipdb.set_trace()

            for result in results:
                key_name = result[0]
                data_dict = result[1]  # Now data column is the second column
                nested_key = key_name.replace('POLLEN_STORY_', '')

                # Assuming data_dict is a dict, but if it's a string representation of JSON, use json.loads(data_dict)
                
                # Assuming data_dict is a dict, but if it's a string representation of JSON, use json.loads(data_dict)
                if type(data_dict) == str:
                    data_dict = json.loads(data_dict)
                    merged_data["pollenstory"][nested_key] = data_dict["pollen_story"]
                else:
                    merged_data["pollenstory"][nested_key] = data_dict["pollen_story"]

            merged_data = json.dumps(merged_data)
            # Always deserialize using custom decoder
            return json.loads(merged_data, cls=PollenJsonDecoder)

        except Exception as e:
            print_line_of_error(e)
        finally:
            if conn:
                conn.close()

        return None


    @staticmethod
    def get_all_tables():
        with PollenDatabase.get_connection() as conn, conn.cursor() as cur:
            try:
                # Execute query to fetch all table names in the public schema
                cur.execute("""
                    SELECT table_name
                    FROM information_schema.tables
                    WHERE table_schema = 'public'
                    AND table_type = 'BASE TABLE';
                """)
                
                # Fetch all table names
                tables = cur.fetchall()
                
                # Return the list of table names
                return [table[0] for table in tables]
    
            except Exception as e:
                print("Error Fetch in All Tables:", e)


    @staticmethod
    def get_all_tables_with_sizes():
        with PollenDatabase.get_connection() as conn, conn.cursor() as cur:
            try:
                # Execute query to fetch all table names and their sizes in the public schema
                cur.execute("""
                    SELECT 
                        table_name, 
                        pg_size_pretty(pg_total_relation_size('public.' || table_name)) AS table_size
                    FROM information_schema.tables
                    WHERE table_schema = 'public'
                    ORDER BY table_name;
                """)
                
                # Fetch all tables and their sizes
                tables = cur.fetchall()
                
                # Check if tables are fetched
                if not tables:
                    print("No tables found.")
                
                # Return the list of tuples (table_name, table_size)
                return [(table[0], table[1]) for table in tables]

            except Exception as e:
                print(f"Error Fetching Table Sizes: {e}")
                return []

    @staticmethod
    def get_all_keys(table_name='pollen_store'):
        with PollenDatabase.get_connection() as conn, conn.cursor() as cur:
            try:
                # Execute query to fetch all unique keys in the specified table
                query = f"SELECT DISTINCT key FROM {table_name} ORDER BY key;"
                cur.execute(query)
                
                # Fetch all unique keys
                keys = cur.fetchall()
                
                # Return the list of keys
                return [key[0] for key in keys]

            except Exception as e:
                if table_name == 'client_users':
                    pass
                else:
                    print(f"Error Fetch in all Keys table {table_name} {e}")
                return []


    @staticmethod
    def update_table_schema(table_name='pollen_store'):
        """
        Add a 'last_modified' column to the table if it does not exist.
        """
        with PollenDatabase.get_connection() as conn, conn.cursor() as cur:
            try:
                # Check if the 'last_modified' column exists
                cur.execute(
                    f"""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = %s AND column_name = 'last_modified';
                    """,
                    (table_name,)
                )
                
                # If the column doesn't exist, add it
                if not cur.fetchone():
                    print(f"Adding 'last_modified' column to {table_name}")
                    cur.execute(
                        sql.SQL("""
                            ALTER TABLE {table} 
                            ADD COLUMN last_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
                        """).format(table=sql.Identifier(table_name))
                    )
                    conn.commit()
                    print(f"Column 'last_modified' added successfully.")
                else:
                    print(f"'last_modified' column already exists in {table_name}.")

            except Exception as e:
                print("Error updating table schema:", e)

    @staticmethod
    def get_all_keys_with_timestamps(table_name='db', db_root=None):
        """
        Fetch all keys along with their last modified timestamp from the specified table.
        """
        with PollenDatabase.get_connection() as conn, conn.cursor() as cur:
            try:
                if db_root:
                    query = f"""
                        SELECT key, last_modified
                        FROM {table_name}
                        WHERE key LIKE %s
                        ORDER BY last_modified DESC;
                    """
                    cur.execute(query, (f'%{db_root}%',))
                else:
                    query = f"""
                        SELECT key, last_modified
                        FROM {table_name}
                        ORDER BY last_modified DESC;
                    """
                    cur.execute(query)
                
                # Fetch all keys and their last modified timestamps
                results = cur.fetchall()
                
                # Return a list of tuples (key, last_modified)
                return [(key, last_modified) for key, last_modified in results]

            except Exception as e:
                if table_name == 'client_users':
                    pass
                else:
                    print_line_of_error(f"GET KEYS Error: {e}")
                return []

    @staticmethod
    def delete_table(table_name):
        """
        Delete the specified table from the database.
        """
        with PollenDatabase.get_connection() as conn, conn.cursor() as cur:
            try:
                # Drop the table if it exists
                cur.execute(f"DROP TABLE IF EXISTS {table_name};")
                conn.commit()
                print(f"Table '{table_name}' has been deleted successfully.")
                return True
            except Exception as e:
                print(f"Error deleting table '{table_name}':", e)
                return False

    @staticmethod
    def delete_key(table_name, key_column, console='del'):
        """
        Delete a specific row from the specified table based on the key.

        Parameters:
        - table_name (str): The name of the table.
        - key_column (str): The column name that holds the key.
        # - key_value: The value of the key to delete.

        Returns:
        - bool: True if the deletion was successful, False otherwise.
        """
        # Validate table and column names to prevent SQL injection
        # if not table_name.isidentifier() or not key_column.isidentifier():
        #     print("Invalid table name or column name.")
        #     print("The given table name and column name: ", table_name, key_column)
        #     return False

        # Construct the query safely
        delete_query = f"DELETE FROM {table_name} WHERE key = %s"

        try:
            with PollenDatabase.get_connection() as conn:
                with conn.cursor() as cur:
                    # Execute the query
                    cur.execute(delete_query, (key_column,))
                    conn.commit()
                    if console:
                        msg=(f"Row with key = '{key_column}' has been deleted successfully from table '{table_name}'.")
                        st.write(console+msg)
                    return True
        except Exception as e:
            print(f"Error deleting row with key = '{key_column}' from table '{table_name}': {e}")
            return False

    @staticmethod
    def read_client_users(source_table='client_users'):
        with PollenDatabase.get_connection() as conn, conn.cursor() as cur:
            try:
                with PollenDatabase.get_connection() as conn, conn.cursor() as cur:

                    # Fetch data from the source table
                    cur.execute(f"SELECT * FROM {source_table};")
                    users = cur.fetchall()
                    # users = cur.execute("SELECT * FROM client_users").fetchall()
                    df = pd.DataFrame(users)

                return users, df

            except Exception as e:
                print("Error client users", e)


class PostgresHandler(logging.Handler):
    def __init__(self, log_name):
        super().__init__()
        self.log_name = log_name
        self.conn = None

    def emit(self, record):
        # Get a new connection for each emit to ensure thread safety
        try:
            self.conn = PollenDatabase.get_connection()
            log_message = self.format(record)
            log_level = record.levelname
            value = f'{log_message, log_level}'

            PollenDatabase.upsert_data("logging_store", self.log_name, value)

        except Exception as e:
            print(f"Failed to insert log into PostgreSQL: {e}")
        finally:
            if self.conn:
                self.conn.close()

class MigratePostgres:
    @staticmethod
    def get_server_connection():
        # Reading connection details from environment variables
        DATABASE_HOST = os.getenv("POLLEN_DATABASE_host_server")
        DATABASE_PORT = os.getenv("POLLEN_DATABASE_port_server")
        DATABASE_NAME = os.getenv("POLLEN_DATABASE_name_server")
        DATABASE_USER = os.getenv("POLLEN_DATABASE_user_server")
        DATABASE_PASS = os.getenv("POLLEN_DATABASE_pass_server")


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
        - created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        - last_modified: timestamp, defaults to CURRENT_TIMESTAMP
        Returns True if the table was created, False if it already existed.
        """
        with MigratePostgres.get_server_connection() as conn, conn.cursor() as cur:
            # Check if the table exists already
            cur.execute("""
            SELECT to_regclass(%s);
            """, (table_name,))
            result = cur.fetchone()[0]
            
            if result is None:  # Table does not exist
                create_table_query = f"""
                CREATE TABLE {table_name} (
                    id SERIAL PRIMARY KEY,
                    key VARCHAR(255) UNIQUE NOT NULL,
                    data TEXT NOT NULL,
                    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    last_modified TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
                """
                cur.execute(create_table_query)
                conn.commit()
                return True  # Table was created
            else:
                return False  # Table already exists


    @staticmethod
    def upsert_migrate_data(table_name, key, value, console=True, console_table_ignore=['logging_store']):
        """
        Upsert data into a specified table. If the table doesn't exist, it will be created.
        Dynamically handles 'last_modified' based on table schema.
        """
        # Ensure the table exists before attempting to upsert data
        MigratePostgres.create_table_if_not_exists(table_name)
        try:

            with MigratePostgres.get_server_connection() as conn, conn.cursor() as cur:
                value_json = json.dumps(value, cls=PollenJsonEncoder)

                upsert_query = f"""
                    INSERT INTO {table_name} (key, data, last_modified)
                    VALUES (%s, %s, CURRENT_TIMESTAMP)
                    ON CONFLICT (key) 
                    DO UPDATE SET data = EXCLUDED.data, last_modified = CURRENT_TIMESTAMP;
                """

                cur.execute(upsert_query, (key, value_json))
                conn.commit()

                if console and table_name not in console_table_ignore:
                    print(f'{key} Upserted to {table_name}')
            
            return True
        except Exception as e:
            print("issue arrived in upsert_data function")
            print_line_of_error(e)
            return False


    @staticmethod
    def get_server_keys(table_name='db', db_root=None):
        """
        Fetch all keys along with their last modified timestamp from the specified table.
        """
        with MigratePostgres.get_server_connection() as conn, conn.cursor() as cur:
            try:
                if db_root:
                    query = f"""
                        SELECT key, last_modified
                        FROM {table_name}
                        WHERE key LIKE %s
                        ORDER BY last_modified DESC;
                    """
                    cur.execute(query, (f'%{db_root}%',))
                else:
                    query = f"""
                        SELECT key, last_modified
                        FROM {table_name}
                        ORDER BY last_modified DESC;
                    """
                    cur.execute(query)
                
                # Fetch all keys and their last modified timestamps
                results = cur.fetchall()
                
                # Return a list of tuples (key, last_modified)
                return [(key, last_modified) for key, last_modified in results]

            except Exception as e:
                print_line_of_error(f"GET KEYS Error: {e}")
                return []



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
