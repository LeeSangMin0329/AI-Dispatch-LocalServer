from prompt_introduction import summary_rule
from db_manager import archive_old_conversations, add_summary_conversation, get_archived_conversations
from openai_controller import query_gpt

def request_summary():
    start_id, end_id = archive_old_conversations()

    if (start_id is None) or (end_id is None):
        return

    conversations, timestamp = get_archived_conversations(start_id, end_id)

    if len(conversations) <= 0:
        print(f"{start_id} ~ {end_id} is not exist. from archive")
        return
    
    conversations.insert(0, summary_rule)

    result = query_gpt(conversations).strip()
    
    if not result:
        return
    
    print(f"summary {start_id} ~ {end_id} : {result}")
    add_summary_conversation(result, timestamp)
