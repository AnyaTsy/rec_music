import pandas as pd
import sqlite3

def load_data_from_db():
    conn = sqlite3.connect('music_data.db')
    query = "SELECT * FROM songs"
    music_data = pd.read_sql_query(query, conn)
    conn.close()
    return music_data
