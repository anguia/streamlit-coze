import sqlite3

def create_tables():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS api_info (username TEXT, user_id TEXT, bot_id TEXT, access_token TEXT)''')
    c.close()
    conn.close()

def register_user(username, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    try:
        c.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        c.close()
        conn.close()

def authenticate_user(username, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
    user = c.fetchone()
    c.close()
    conn.close()
    return user is not None

def save_api_info(username, user_id, bot_id, access_token):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('DELETE FROM api_info WHERE username = ?', (username,))
    c.execute('INSERT INTO api_info (username, user_id, bot_id, access_token) VALUES (?, ?, ?, ?)', (username, user_id, bot_id, access_token))
    conn.commit()
    c.close()
    conn.close()

def get_api_info(username):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT user_id, bot_id, access_token FROM api_info WHERE username = ?', (username,))
    api_info = c.fetchone()
    c.close()
    conn.close()
    return api_info if api_info else None

def save_conversation(username, conversation):
    # To be implemented: Save conversation into the database
    pass

def load_conversation(username):
    # To be implemented: Load conversation from the database
    return []