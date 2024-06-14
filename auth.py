import pandas as pd
import sqlite3

def register_user(username, password):
    conn = sqlite3.connect('users_data.db')
    users = pd.read_sql_query("SELECT * FROM users", conn)
    if username in users['username'].values:
        return "Username already exists."
    new_user = pd.DataFrame([[username, password]], columns=["username", "password"])
    new_user.to_sql('users', conn, if_exists='append', index=False)
    conn.close()
    return "Registered successfully"

def authenticate_user(username, password):
    conn = sqlite3.connect('users_data.db')
    users = pd.read_sql_query("SELECT * FROM users", conn)
    user = users[(users['username'] == username) & (users['password'] == password)]
    conn.close()
    return not user.empty

def get_user_data(username):
    conn = sqlite3.connect('users_data.db')
    users = pd.read_sql_query("SELECT * FROM users", conn)
    user_data = users[users['username'] == username]
    conn.close()
    return user_data

def update_user_data(username, field, value):
    conn = sqlite3.connect('users_data.db')
    users = pd.read_sql_query("SELECT * FROM users", conn)
    users.loc[users['username'] == username, field] = value
    users.to_sql('users', conn, if_exists='replace', index=False)
    conn.close()
