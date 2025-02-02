import db_manager
from prompt_introduction import summary_rule
from openai_controller import query_gpt
from datetime import datetime, timedelta

KEEP_RECENT_MESSAGE_COUNT = 50
COMPARISON_HOURS = 6

__all__ = ['request_summary', 'try_request_summary_from_timestamp']

def request_summary():
    conversation_count = db_manager.get_count_recent_conversations()

    if conversation_count <= KEEP_RECENT_MESSAGE_COUNT:
        print(f"conversations table row cound less than {KEEP_RECENT_MESSAGE_COUNT}. so not work archive.")
        return
    
    _converting_old_conversation_to_long_term_memory(KEEP_RECENT_MESSAGE_COUNT)

def try_request_summary_from_timestamp():
    # 마지막 대화가 지정 시간 이전이면 아카이빙
    recent_timestamp = db_manager.get_timestamp_most_recent_conversations()

    if not recent_timestamp:
        return
    
    current_time = datetime.now()
    comparison_time = current_time - timedelta(hours = COMPARISON_HOURS)
    
    recent_time = datetime.strptime(recent_timestamp, f"%Y-%m-%d %H:%M:%S")

    print(f"{current_time - recent_time} have passed since our last conversation.")
    if recent_time >= comparison_time:
        return

    conversation_count = db_manager.get_count_recent_conversations()

    if conversation_count <= 0:
        return
    
    print(f"{conversation_count} conversations exist.")
    _converting_old_conversation_to_long_term_memory(keep_recent_rows_count = 0)

def _converting_old_conversation_to_long_term_memory(keep_recent_rows_count: int):
    start_id, end_id = db_manager.archive_old_conversations(keep_recent_rows_count)

    if (start_id is None) or (end_id is None):
        return

    conversations, timestamp = db_manager.get_archived_conversations(start_id, end_id)

    if len(conversations) <= 0:
        print(f"{start_id} ~ {end_id} is not exist. from archive")
        return
    
    conversations.insert(0, summary_rule)

    result = query_gpt(conversations).strip()
    
    if not result:
        return
    
    print(f"summary {start_id} ~ {end_id} : {result}")
    db_manager.add_summary_conversation(result, timestamp)
