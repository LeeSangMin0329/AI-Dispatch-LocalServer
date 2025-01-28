import sqlite3

DB_FILE_PATH = "sqlite/conversations.db"

def init():
    db_connect = sqlite3.connect(DB_FILE_PATH)
    cursor = db_connect.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS conversations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        role TEXT,
        message TEXT,
        face TEXT,
        motion TEXT,
        timestamp DATETIME DEFAULT (datetime('now', 'localtime')),
        context TEXT
    )
                ''')
    
    db_connect.close()

def add_converstaion(role: str, message: str, face: str = None, motion: str = None, context: str = None):
    db_connect = sqlite3.connect(DB_FILE_PATH)
    cursor = db_connect.cursor()

    cursor.execute('''
    INSERT INTO conversations (role, message, face, motion, context)
    VALUES (?, ?, ?, ?, ?)
                   ''', (role, message, face, motion, context))
    
    db_connect.commit()
    db_connect.close()

def get_conversations():
    db_connect = sqlite3.connect(DB_FILE_PATH)
    cursor = db_connect.cursor()

    cursor.execute('''
    SELECT role, message, face, motion, timestamp FROM conversations
    ORDER BY timestamp
                   ''')
    
    conversations = cursor.fetchall()

    db_connect.close()

    gpt_messages = []

    for row in conversations:
        role, message, face, motion, timestamp = row

        if role == "user":
            gpt_messages.append({"role" : role, "content" : f"user ({timestamp}):" + message})
        else:
            gpt_messages.append({"role" : role, "content" : f"{face}|{motion}|{message}"})

    print(f"converstaion length: {len(gpt_messages)}")
    return gpt_messages

def split_message(message: str):
    parts = message.split("|")

    face = ""
    motion = ""
    answer = ""

    if len(parts) < 3:
        answer = parts[-1]
    else:
        face = parts[0]
        motion = parts[1]
        answer = parts[2]
    
    return face, motion, answer