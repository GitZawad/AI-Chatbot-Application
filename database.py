import sqlite3
import uuid
import hashlib

def initialize_database():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    # Create users table if it doesn't exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        salt TEXT NOT NULL
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS chat_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        sender TEXT NOT NULL,
        message TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
    ''')

    conn.commit()
    conn.close()

def hash_password(password, salt=None):
    if salt is None:
        salt = uuid.uuid4().hex
    hashed_password = hashlib.sha512((password + salt).encode('utf-8')).hexdigest()
    return hashed_password, salt

def verify_password(stored_hash, stored_salt, provided_password):
    new_hash, _ = hash_password(provided_password, stored_salt)
    return new_hash == stored_hash

def save_message_to_history(user_id, sender, message):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO chat_history (user_id, sender, message) VALUES (?, ?, ?)",
        (user_id, sender, message)
    )
    conn.commit()
    conn.close()

def load_chat_history(user_id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT sender, message FROM chat_history WHERE user_id = ? ORDER BY timestamp ASC",
            (user_id,)
        )
        return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Error loading chat history: {e}")
        return []
    finally:
        conn.close()

def clear_chat_history(user_id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    try:
        cursor.execute(
            "DELETE FROM chat_history WHERE user_id = ?",
            (user_id,)
        )
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Error clearing chat history: {e}")
        return False
    finally:
        conn.close()

def create_user(username, password):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    try:
        password_hash, salt = hash_password(password)
        user_id = uuid.uuid4().hex
        cursor.execute(
            "INSERT INTO users (id, username, password_hash, salt) VALUES (?, ?, ?, ?)",
            (user_id, username, password_hash, salt)
        )
        conn.commit()
        return user_id
    except sqlite3.Error as e:
        print(f"Error creating user: {e}")
        return None
    finally:
        conn.close()

def get_user(username):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, password_hash, salt FROM users WHERE username=?", (username,))
        return cursor.fetchone()
    except sqlite3.Error as e:
        print(f"Error getting user: {e}")
        return None
    finally:
        conn.close()