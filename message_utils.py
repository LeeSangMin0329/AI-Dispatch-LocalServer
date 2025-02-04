import re
import emoji

remove_words = ["ご視聴ありがとうござ", "by", "チョ", "トミ", "お疲れさまでした", "字幕視聴", "コメント欄に書いてあげてね", "咳 ごちそうさまでした", "【", "】", "パチパチパチ", "バイバイ"]

def remove_emoji(message: str):
    return emoji.replace_emoji(message, replace='')

def postprocess_stt(transcription: str) -> str:
    if len(transcription) < 4:
        return ""

    for bad_word in remove_words:
        if bad_word in transcription:
            return ""
            
    message = remove_emoji(transcription)
    return message.strip()

def postprocess_llm_answer(plain_text: str):
    message = remove_emoji(plain_text).strip()
    
    # 괄호 안의 문자와 : 특수문자 제거.
    return re.sub(r'（.*?）|[:『』「」]', '', message)

def split_answer_message(message: str):
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
