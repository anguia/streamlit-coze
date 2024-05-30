import sqlite3
import json

def create_tables():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY, 
        password TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS api_info (
        username TEXT, 
        user_id TEXT, 
        bot_id TEXT, 
        access_token TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS conversations (
        username TEXT, 
        conversation TEXT)''')
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
    c.execute('INSERT INTO api_info (username, user_id, bot_id, access_token) VALUES (?, ?, ?, ?)', 
              (username, user_id, bot_id, access_token))
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
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    conversation_json = json.dumps(conversation)
    c.execute('DELETE FROM conversations WHERE username = ?', (username,))
    c.execute('INSERT INTO conversations (username, conversation) VALUES (?, ?)', 
              (username, conversation_json))
    conn.commit()
    c.close()
    conn.close()

def load_conversation(username):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT conversation FROM conversations WHERE username = ?', (username,))
    conversation_row = c.fetchone()
    c.close()
    conn.close()
    if conversation_row:
        return json.loads(conversation_row[0])
    else:
        return []