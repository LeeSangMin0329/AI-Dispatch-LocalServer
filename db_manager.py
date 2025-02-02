import sqlite3

DB_FILE_PATH = "sqlite/conversations.db"
SUMMARY_LENGTH = 100
RECENT_ARCHIVED_MESSAGE_COUNT = 50

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
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS archived_conversations (
        id INTEGER PRIMARY KEY,
        role TEXT,
        message TEXT,
        face TEXT,
        motion TEXT,
        timestamp DATETIME,
        context TEXT
    )
                ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS summarized_conversation (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        summary TEXT,
        timestamp DATETIME
    )
                ''')
    
    db_connect.close()

# region recent conversations
def add_recent_converstaion(role: str, message: str, face: str = None, motion: str = None, context: str = None):
    db_connect = sqlite3.connect(DB_FILE_PATH)
    cursor = db_connect.cursor()

    cursor.execute('''
        INSERT INTO conversations (role, message, face, motion, context)
        VALUES (?, ?, ?, ?, ?)
                   ''', (role, message, face, motion, context))
    
    db_connect.commit()
    db_connect.close()

def get_recent_conversations() -> tuple[list, bool]:
    db_connect = sqlite3.connect(DB_FILE_PATH)
    cursor = db_connect.cursor()

    cursor.execute('''
        SELECT role, message, face, motion, timestamp FROM conversations
        ORDER BY timestamp ASC
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

    print(f"recent conversations length: {len(conversations)}")
    return gpt_messages, (len(conversations) > SUMMARY_LENGTH)

def get_count_recent_conversations() -> int:
    db_connect = sqlite3.connect(DB_FILE_PATH)
    cursor = db_connect.cursor()

    cursor.execute("SELECT COUNT(*) FROM conversations")
    query_result = cursor.fetchone()
    conversation_count = query_result[0] if query_result else 0
    db_connect.close()

    return conversation_count

def get_timestamp_most_recent_conversations():
    db_connect = sqlite3.connect(DB_FILE_PATH)
    cursor = db_connect.cursor()

    cursor.execute('''
        SELECT timestamp
        FROM conversations
        ORDER BY timestamp DESC
        LIMIT 1
                   ''')
    query_result = cursor.fetchone()
    recent_timestamp = query_result[0] if query_result else ""
    db_connect.close()

    return recent_timestamp
# endregion

# region summary converstaions
def get_long_term_conversations() -> list:
    db_connect = sqlite3.connect(DB_FILE_PATH)
    cursor = db_connect.cursor()
    cursor.execute(f'''
        SELECT summary, timestamp
        FROM summarized_conversation
        ORDER BY timestamp ASC
        LIMIT {RECENT_ARCHIVED_MESSAGE_COUNT}
                   ''')
    
    conversations = cursor.fetchall()
    db_connect.close()

    gpt_messages = []

    for row in conversations:
        summary, timestamp = row
        gpt_messages.append({"role" : "assistant", "content" : f"({timestamp}の過去記憶):" + summary})
    return gpt_messages
 
def add_summary_conversation(summary_message: str, timestamp: str):
    db_connect = sqlite3.connect(DB_FILE_PATH)
    cursor = db_connect.cursor()
    cursor.execute('''
        INSERT INTO summarized_conversation (summary, timestamp) VALUES (?, ?)
        ''', (summary_message, timestamp))
    db_connect.commit()
    db_connect.close()
# endregion

# region archived conversations
def archive_old_conversations(keep_recent_rows_limit: int):
    # conversations 테이블의 최신 문장만 남기고 아카이빙
    db_connect = sqlite3.connect(DB_FILE_PATH)
    cursor = db_connect.cursor()

    cursor.execute("SELECT MAX(id) FROM archived_conversations")
    query_result = cursor.fetchone()
    previous_max_id = query_result[0] if query_result else 0

    cursor.execute(f'''
        INSERT INTO archived_conversations SELECT * 
        FROM conversations 
        WHERE id NOT IN (
            SELECT id FROM conversations ORDER BY timestamp DESC LIMIT {keep_recent_rows_limit}
        )''')

    db_connect.commit()
    
    cursor.execute("SELECT MAX(id) FROM archived_conversations")
    query_result = cursor.fetchone()
    end_id = query_result[0] if query_result else 0

    if previous_max_id == end_id:
        print(f"id {previous_max_id}: No new conversations to archive.")
        db_connect.close()
        return None, None
    
    cursor.execute(f'''
        DELETE FROM conversations  
        WHERE id NOT IN (
            SELECT id FROM conversations ORDER BY timestamp DESC LIMIT {keep_recent_rows_limit}
        )''')
    
    db_connect.commit()
    db_connect.close()
    
    # archived_conversations 테이블 id
    return (previous_max_id + 1), end_id

def get_archived_conversations(start_id, end_id):
    db_connect = sqlite3.connect(DB_FILE_PATH)
    cursor = db_connect.cursor()

    cursor.execute('''
        SELECT role, message, timestamp FROM archived_conversations
        WHERE id BETWEEN ? AND ?
        ORDER BY timestamp ASC
        ''', (start_id, end_id))

    conversations = cursor.fetchall()
    db_connect.close()

    gpt_messages = []
    timestamp = ""

    if len(conversations) > 0:
        timestamp = conversations[-1][2]

    message_list = []
    for row in conversations:
        role, message, timestamp = row
        message_list.append(f"{role}: {message}\n")

    content = ''.join(message_list)
    gpt_messages.append({"role" : "user", "content" : content})
    return gpt_messages, timestamp
# endregion   
