import db_manager
import prompt_introduction
from prompt_introduction import summary_rule, random_topic_rule, screenshot_topic_user_content, screenshot_topic_record_user_content
from openai_controller import query_gpt, quary_with_screenshot
from datetime import datetime, timedelta
from message_utils import remove_emoji, split_answer_message
from translate_util import translate_conversation
import screenshot_utils

KEEP_RECENT_MESSAGE_COUNT = 50
COMPARISON_HOURS = 6

__all__ = ['request_summary', 'try_request_summary_from_timestamp']

def chat(user_input: str):
    # 과거 대화 기록에 입력을 더해 전송
    converstations, is_required_summary = get_conversations_prompt()

    current_time = datetime.now()
    timestamp = current_time.strftime(f"%Y-%m-%d %H:%M:%S")
    converstations.append({"role" : "system", "content" : f"現在時刻 : {timestamp}"})
    converstations.append({"role" : "user", "content" : user_input})

    response_content = query_gpt(converstations)
    
    message_jp, face, motion, user_input_ko, message_ko = apply_llm_response_content(response_content, user_input)

    return message_jp, face, motion, user_input_ko, message_ko, is_required_summary

def chat_with_screenshot(user_input: str = ""):
    screenshot_utils.capture_screen()
    converstations, is_required_summary = get_conversations_prompt()

    recorded_user_input = user_input

    if user_input == "":
        user_input = screenshot_topic_user_content
        recorded_user_input = screenshot_topic_record_user_content
    
    response_content = quary_with_screenshot(converstations, user_input)
    message_jp, face, motion, user_input_ko, message_ko = apply_llm_response_content(response_content, recorded_user_input)

    return message_jp, face, motion, user_input_ko, message_ko

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

def generate_random_topic_converstaion() -> str:
    gpt_message = []
    gpt_message.append(random_topic_rule)
    message_random_topics = query_gpt(gpt_message)

    return message_random_topics

def get_conversations_prompt():
    long_term_conversations = db_manager.get_long_term_conversations()
    recent_converstations, is_required_summary = db_manager.get_recent_conversations()
 
    converstations = []
    converstations.append(prompt_introduction.introduction_message_jp)
    converstations.extend(long_term_conversations)
    converstations.extend(recent_converstations)
    converstations.append(prompt_introduction.rule_message_jp)

    return converstations, is_required_summary

def apply_llm_response_content(response_content: str, recorded_user_input: str):
    face, motion, answer = split_answer_message(response_content)
    message_jp = remove_emoji(answer)
    
    print(response_content)
    print(message_jp)

    db_manager.add_recent_converstaion("user", recorded_user_input)
    db_manager.add_recent_converstaion("assistant", message_jp, face, motion)

    user_input_ko, message_ko = translate_conversation(recorded_user_input, message_jp)
    
    return message_jp, face, motion, user_input_ko, message_ko