import re
import emoji

remove_words = ["ご視聴ありがとうござ", "by", "チョ", "トミ", "お疲れさまでした", "字幕視聴", "コメント欄に書いてあげてね", "咳 ごちそうさまでした", "【", "】", "パチパチパチ"]

def remove_emoji(message: str):
    return emoji.replace_emoji(message, replace='')

def postprocess_stt(transcription: str) -> str:
    if len(transcription) < 4:
        return ""

    for bad_word in remove_words:
        if bad_word in transcription:
            return ""
        
    transcription = remove_emoji(transcription).strip()
    
    # 괄호 안의 문자와 : 특수문자 제거.
    return re.sub(r'\(.*?\)|:', '', transcription)
