import sqlite3
import os

# Get the path to the persistent memory directory outside of git
HOME_DIR = os.path.expanduser("~")
DATA_DIR = os.path.join(HOME_DIR, ".algae_data")
DB_PATH = os.path.join(DATA_DIR, "algae_memory.db")

def init_db():
    """Creates the database and tables if they don't exist."""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Simple schema to store chat logs
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            role TEXT NOT NULL,
            content TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def add_message(role: str, content: str):
    """Adds a message to the conversation history."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO chat_history (role, content) VALUES (?, ?)', (role, content))
    conn.commit()
    conn.close()

def get_history(limit=10):
    """Retrieves the last N messages to send to Gemma as context."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Get the last N messages, ordered by oldest to newest
    cursor.execute('SELECT role, content FROM chat_history ORDER BY timestamp DESC LIMIT ?', (limit,))
    rows = cursor.fetchall()
    conn.close()
    
    # Reverse to feed to LLM in correct chronological order
    history = [{"role": row[0], "content": row[1]} for row in reversed(rows)]
    return history

def clear_history():
    """Deletes all chat history (Can be triggered by voice command)."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM chat_history')
    conn.commit()
    conn.close()

# Initialize when the module loads
init_db()