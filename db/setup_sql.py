import sqlite3
from sqlite3 import Error
import os

def create_connection(db_file):
    """ create a database connection to a SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print(sqlite3.version)
    except Error as e:
        print(e)
    finally:
        if conn:
            conn.close()


if __name__ == '__main__':
    r = str(os.path.dirname(os.path.realpath(__file__)))
    db = r + "\pythonsqlite.db"
    create_connection(db)